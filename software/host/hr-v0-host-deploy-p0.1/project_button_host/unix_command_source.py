"""Credential-checked local trajectory source for HR-V0.

PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, MOTION OR ENERGIZATION.

The source accepts one bounded JSON datagram from an exact local UID/GID over
an AF_UNIX socket.  It does not listen on TCP/IP, spawn a process, reuse a
stale file, or bypass the supervisor's session, sequence, state, kinematic,
position, velocity, duration and deadline checks.
"""

from __future__ import annotations

import json
import math
import os
import socket
import stat
import struct
from pathlib import Path
from typing import Any, Mapping

from project_button_supervisor import MotionMode, TrajectoryCommand, TrajectorySample


COMMAND_FIELDS = {
    "trajectory_id",
    "session_id",
    "sequence",
    "source_time_ms",
    "validity_deadline_ms",
    "execution_deadline_ms",
    "configuration_hash",
    "kinematic_model_hash",
    "sender_state",
    "mode",
    "starting_positions",
    "samples",
    "expected_terminal_positions",
}
SAMPLE_FIELDS = {"offset_ms", "positions", "velocities"}


class CommandSourceError(RuntimeError):
    """A framing, credential, schema or local-socket failure."""


def _finite_mapping(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, dict) or not value:
        raise CommandSourceError(f"{label} must be a nonempty object")
    result: dict[str, float] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or not key or isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise CommandSourceError(f"{label} contains an invalid axis or number")
        number = float(raw)
        if not math.isfinite(number):
            raise CommandSourceError(f"{label} contains a non-finite number")
        result[key] = number
    return result


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise CommandSourceError(f"{label} must be an integer at least {minimum}")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise CommandSourceError(f"{label} must be nonempty text no longer than 128 characters")
    return value


def parse_command(payload: bytes) -> TrajectoryCommand:
    """Parse an exact finite JSON command without accepting NaN or extra keys."""

    try:
        raw = json.loads(
            payload.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise CommandSourceError("trajectory datagram is not strict UTF-8 JSON") from exc
    if not isinstance(raw, dict) or set(raw) != COMMAND_FIELDS:
        raise CommandSourceError("trajectory command fields do not exactly match the controlled schema")
    samples_raw = raw["samples"]
    if not isinstance(samples_raw, list) or not samples_raw:
        raise CommandSourceError("trajectory samples must be a nonempty array")
    samples: list[TrajectorySample] = []
    for index, item in enumerate(samples_raw):
        if not isinstance(item, dict) or set(item) != SAMPLE_FIELDS:
            raise CommandSourceError(f"trajectory sample {index} fields are invalid")
        samples.append(
            TrajectorySample(
                offset_ms=_integer(item["offset_ms"], f"sample {index} offset"),
                positions=_finite_mapping(item["positions"], f"sample {index} positions"),
                velocities=_finite_mapping(item["velocities"], f"sample {index} velocities"),
            )
        )
    try:
        mode = MotionMode(raw["mode"])
    except (TypeError, ValueError) as exc:
        raise CommandSourceError("trajectory mode is invalid") from exc
    return TrajectoryCommand(
        trajectory_id=_text(raw["trajectory_id"], "trajectory ID"),
        session_id=_text(raw["session_id"], "session ID"),
        sequence=_integer(raw["sequence"], "sequence"),
        source_time_ms=_integer(raw["source_time_ms"], "source time"),
        validity_deadline_ms=_integer(raw["validity_deadline_ms"], "validity deadline"),
        execution_deadline_ms=_integer(raw["execution_deadline_ms"], "execution deadline"),
        configuration_hash=_text(raw["configuration_hash"], "configuration hash"),
        kinematic_model_hash=_text(raw["kinematic_model_hash"], "kinematic model hash"),
        sender_state=_text(raw["sender_state"], "sender state"),
        mode=mode,
        starting_positions=_finite_mapping(raw["starting_positions"], "starting positions"),
        samples=tuple(samples),
        expected_terminal_positions=_finite_mapping(
            raw["expected_terminal_positions"], "expected terminal positions"
        ),
    )


class UnixDatagramCommandSource:
    """Nonblocking AF_UNIX datagram receiver with kernel sender credentials."""

    def __init__(
        self,
        path: Path,
        allowed_uid: int,
        allowed_gid: int,
        maximum_datagram_bytes: int,
        mode: int,
    ) -> None:
        if os.name != "posix" or not hasattr(socket, "SO_PASSCRED"):
            raise CommandSourceError("credential-checked AF_UNIX transport requires Linux")
        if path.exists() or path.is_symlink():
            raise CommandSourceError("command socket path already exists; stale-path reuse is prohibited")
        if not path.parent.is_dir():
            raise CommandSourceError("command socket parent directory is absent")
        if allowed_uid < 0 or allowed_gid < 0:
            raise CommandSourceError("command sender UID/GID is invalid")
        if not 256 <= maximum_datagram_bytes <= 1_048_576:
            raise CommandSourceError("maximum command datagram is outside the controlled bound")
        if mode & 0o007 or mode & ~0o777:
            raise CommandSourceError("command socket mode must deny all access to other users")
        self.path = path
        self.allowed_uid = allowed_uid
        self.allowed_gid = allowed_gid
        self.maximum_datagram_bytes = maximum_datagram_bytes
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM | socket.SOCK_NONBLOCK)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            self.socket.bind(str(path))
            os.chmod(path, mode)
        except Exception:
            self.socket.close()
            if path.exists() and stat.S_ISSOCK(path.lstat().st_mode):
                path.unlink()
            raise
        self.closed = False

    def poll(self, now_ms: int) -> TrajectoryCommand | None:  # noqa: ARG002
        if self.closed:
            raise CommandSourceError("command source is closed")
        credential_size = struct.calcsize("3i")
        try:
            payload, ancillary, flags, _ = self.socket.recvmsg(
                self.maximum_datagram_bytes + 1, socket.CMSG_SPACE(credential_size)
            )
        except BlockingIOError:
            return None
        if flags & getattr(socket, "MSG_TRUNC", 0) or len(payload) > self.maximum_datagram_bytes:
            raise CommandSourceError("trajectory datagram exceeds the released size bound")
        credentials: tuple[int, int, int] | None = None
        for level, kind, data in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS and len(data) >= credential_size:
                credentials = struct.unpack("3i", data[:credential_size])
                break
        if credentials is None:
            raise CommandSourceError("trajectory sender credentials are absent")
        _pid, uid, gid = credentials
        if uid != self.allowed_uid or gid != self.allowed_gid:
            raise CommandSourceError("trajectory sender UID/GID is not authorized")
        return parse_command(payload)

    def close(self) -> None:
        if self.closed:
            return
        try:
            self.socket.close()
        finally:
            if self.path.exists() and stat.S_ISSOCK(self.path.lstat().st_mode):
                self.path.unlink()
            self.closed = True


def _selected_int(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise CommandSourceError(f"{label} remains SELECTION REQUIRED")
    return value


def factory(host: Mapping[str, Any], root: Path) -> UnixDatagramCommandSource:
    command = host.get("command_source")
    if not isinstance(command, dict):
        raise CommandSourceError("command-source configuration remains SELECTION REQUIRED")
    path_raw = command.get("socket_path")
    if not isinstance(path_raw, str) or not path_raw.startswith("/") or "SELECTION" in path_raw.upper():
        raise CommandSourceError("command socket path remains SELECTION REQUIRED")
    mode_raw = command.get("socket_mode")
    if not isinstance(mode_raw, str) or not mode_raw.startswith("0o"):
        raise CommandSourceError("command socket mode remains SELECTION REQUIRED")
    try:
        mode = int(mode_raw, 8)
    except ValueError as exc:
        raise CommandSourceError("command socket mode is invalid") from exc
    return UnixDatagramCommandSource(
        root / path_raw.lstrip("/"),
        _selected_int(command.get("allowed_uid"), "command sender UID"),
        _selected_int(command.get("allowed_gid"), "command sender GID"),
        _selected_int(command.get("maximum_datagram_bytes"), "maximum command datagram", 256),
        mode,
    )


__all__ = [
    "COMMAND_FIELDS",
    "CommandSourceError",
    "UnixDatagramCommandSource",
    "factory",
    "parse_command",
]
