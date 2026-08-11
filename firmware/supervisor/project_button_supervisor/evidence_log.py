"""Configuration-bound, hash-chained HR-V0 runtime evidence log.

PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TESTING,
MOTION, OR ENERGIZATION.

This module provides integrity and configuration-binding controls for future
test evidence.  It does not establish clock accuracy, calibration validity,
storage durability, functional-safety integrity, or permission to run a test.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


SCHEMA_ID = "HR-V0-EVID-LOG-P0.1"
ZERO_HASH = "0" * 64
UNRESOLVED = {"", "SELECTION REQUIRED", "NOT_AUTHORIZED", "NOT EXECUTED", "NOT_EXECUTED"}
EVENT_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
REQUIRED_IDENTITIES = frozenset(
    {
        "release_candidate_id",
        "electrical_revision",
        "mechanical_revision",
        "bom_revision",
        "calibration_set_id",
        "test_procedure_id",
    }
)
REQUIRED_HASHES = frozenset(
    {
        "system_configuration_sha256",
        "supervisor_file_sha256",
        "actuator_file_sha256",
        "compute_interface_file_sha256",
        "firmware_source_manifest_sha256",
        "release_manifest_sha256",
        "calibration_set_sha256",
        "test_procedure_sha256",
    }
)


class EvidenceLogError(RuntimeError):
    """Evidence logging or verification failed closed."""


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
    )


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EvidenceLogError(f"record is not canonical JSON: {exc}") from exc


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise EvidenceLogError("UTC clock provider returned a naive timestamp")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class EvidenceContext:
    """Exact identities and hashes that every record inherits."""

    session_id: str
    identities: Mapping[str, str]
    hashes: Mapping[str, str]

    def as_dict(self) -> dict[str, object]:
        identities = dict(self.identities)
        hashes = {key: value.lower() for key, value in self.hashes.items()}
        if not self.session_id or len(self.session_id) > 128 or not re.fullmatch(r"[A-Za-z0-9._-]+", self.session_id):
            raise EvidenceLogError("session identifier is absent or malformed")
        if set(identities) != REQUIRED_IDENTITIES:
            raise EvidenceLogError("evidence identity set is incomplete or contains unknown fields")
        if set(hashes) != REQUIRED_HASHES:
            raise EvidenceLogError("evidence hash set is incomplete or contains unknown fields")
        for key, value in identities.items():
            if not isinstance(value, str) or value.strip().upper() in UNRESOLVED:
                raise EvidenceLogError(f"evidence identity {key} is unresolved")
        for key, value in hashes.items():
            if not _is_sha256(value):
                raise EvidenceLogError(f"evidence hash {key} is not an exact SHA-256")
        return {
            "session_id": self.session_id,
            "identities": identities,
            "hashes": hashes,
        }


@dataclass(frozen=True)
class LogVerification:
    record_count: int
    first_monotonic_ms: int
    last_monotonic_ms: int
    final_sha256: str
    closed_cleanly: bool
    context_sha256: str


class HashChainedJsonlSink:
    """Write one exclusive, append-only-by-process JSONL session file."""

    def __init__(
        self,
        path: Path,
        context: EvidenceContext,
        start_monotonic_ms: int,
        utc_now: Callable[[], datetime] | None = None,
    ) -> None:
        if isinstance(start_monotonic_ms, bool) or not isinstance(start_monotonic_ms, int) or start_monotonic_ms < 0:
            raise EvidenceLogError("start monotonic timestamp must be a nonnegative integer")
        self.path = path
        self.context = context.as_dict()
        self.context_sha256 = hashlib.sha256(_canonical(self.context)).hexdigest()
        self._utc_now = utc_now or (lambda: datetime.now(timezone.utc))
        self._sequence = 0
        self._previous_sha256 = ZERO_HASH
        self._last_monotonic_ms = start_monotonic_ms
        self._closed = False
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            self._handle = path.open("x", encoding="utf-8", newline="\n")
        except OSError as exc:
            raise EvidenceLogError(f"cannot create exclusive evidence log: {exc}") from exc
        try:
            self.record(start_monotonic_ms, "SESSION_START", {"context": self.context})
        except Exception:
            self._handle.close()
            raise

    def record(self, monotonic_ms: int, event: str, payload: Mapping[str, object]) -> None:
        if self._closed:
            raise EvidenceLogError("evidence log is closed")
        if isinstance(monotonic_ms, bool) or not isinstance(monotonic_ms, int):
            raise EvidenceLogError("monotonic timestamp must be an integer")
        if monotonic_ms < self._last_monotonic_ms:
            raise EvidenceLogError("monotonic timestamp regressed")
        if not isinstance(event, str) or not EVENT_PATTERN.fullmatch(event):
            raise EvidenceLogError("event identifier is malformed")
        if not isinstance(payload, Mapping):
            raise EvidenceLogError("event payload is not a mapping")
        record: dict[str, Any] = {
            "schema_id": SCHEMA_ID,
            "sequence": self._sequence,
            "monotonic_ms": monotonic_ms,
            "wall_time_utc": _utc_text(self._utc_now()),
            "event": event,
            "context_sha256": self.context_sha256,
            "previous_sha256": self._previous_sha256,
            "payload": dict(payload),
        }
        record_sha256 = hashlib.sha256(_canonical(record)).hexdigest()
        record["record_sha256"] = record_sha256
        try:
            self._handle.write(_canonical(record).decode("utf-8") + "\n")
            self._handle.flush()
            os.fsync(self._handle.fileno())
        except OSError as exc:
            raise EvidenceLogError(f"evidence log write failed: {exc}") from exc
        self._previous_sha256 = record_sha256
        self._last_monotonic_ms = monotonic_ms
        self._sequence += 1

    def close(self, monotonic_ms: int) -> None:
        if self._closed:
            return
        try:
            self.record(monotonic_ms, "SESSION_END", {"closed_cleanly": True})
        finally:
            self._closed = True
            self._handle.close()


def verify_log(path: Path) -> LogVerification:
    """Verify exact schema, sequence, monotonicity, context, and hash chain."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvidenceLogError(f"cannot read evidence log: {exc}") from exc
    if not lines:
        raise EvidenceLogError("evidence log is empty")

    expected_previous = ZERO_HASH
    last_monotonic = -1
    context_sha256: str | None = None
    first_monotonic = -1
    last_event = ""
    for sequence, line in enumerate(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceLogError(f"record {sequence} is not valid JSON") from exc
        if not isinstance(record, dict):
            raise EvidenceLogError(f"record {sequence} is not an object")
        record_hash = record.pop("record_sha256", None)
        if not _is_sha256(record_hash) or hashlib.sha256(_canonical(record)).hexdigest() != record_hash.lower():
            raise EvidenceLogError(f"record {sequence} hash mismatch")
        if record.get("schema_id") != SCHEMA_ID or record.get("sequence") != sequence:
            raise EvidenceLogError(f"record {sequence} schema or sequence mismatch")
        if record.get("previous_sha256") != expected_previous:
            raise EvidenceLogError(f"record {sequence} chain mismatch")
        monotonic_ms = record.get("monotonic_ms")
        if isinstance(monotonic_ms, bool) or not isinstance(monotonic_ms, int) or monotonic_ms < last_monotonic:
            raise EvidenceLogError(f"record {sequence} monotonic timestamp invalid")
        try:
            wall = datetime.fromisoformat(str(record.get("wall_time_utc", "")).replace("Z", "+00:00"))
        except ValueError as exc:
            raise EvidenceLogError(f"record {sequence} UTC timestamp invalid") from exc
        if wall.utcoffset() != timezone.utc.utcoffset(wall):
            raise EvidenceLogError(f"record {sequence} UTC timestamp is not UTC")
        current_context = record.get("context_sha256")
        if not _is_sha256(current_context):
            raise EvidenceLogError(f"record {sequence} context hash invalid")
        if context_sha256 is None:
            context_sha256 = current_context.lower()
            payload = record.get("payload")
            context = payload.get("context") if isinstance(payload, dict) else None
            if record.get("event") != "SESSION_START" or not isinstance(context, dict):
                raise EvidenceLogError("first record is not a context-bearing SESSION_START")
            if hashlib.sha256(_canonical(context)).hexdigest() != context_sha256:
                raise EvidenceLogError("SESSION_START context hash mismatch")
            first_monotonic = monotonic_ms
        elif current_context.lower() != context_sha256:
            raise EvidenceLogError(f"record {sequence} context changed")
        expected_previous = record_hash.lower()
        last_monotonic = monotonic_ms
        last_event = str(record.get("event", ""))

    assert context_sha256 is not None
    return LogVerification(
        record_count=len(lines),
        first_monotonic_ms=first_monotonic,
        last_monotonic_ms=last_monotonic,
        final_sha256=expected_previous,
        closed_cleanly=last_event == "SESSION_END",
        context_sha256=context_sha256,
    )


__all__ = [
    "EvidenceContext",
    "EvidenceLogError",
    "HashChainedJsonlSink",
    "LogVerification",
    "REQUIRED_HASHES",
    "REQUIRED_IDENTITIES",
    "SCHEMA_ID",
    "verify_log",
]
