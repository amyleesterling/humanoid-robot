#!/usr/bin/env python3
"""Pure-file, fail-closed preflight for the HR-V0 host candidate.

This module deliberately imports no GPIO, serial, DYNAMIXEL, network or process
control backend. It cannot command motion or emit a heartbeat.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_RELEASE_STATE = "RELEASED_FOR_ISOLATED_HOST_HIL"
REQUIRED_STAGE = "ISOLATED_HOST_HIL_AUTHORIZED"
UNRESOLVED_MARKERS = {"", "SELECTION REQUIRED", "NOT_AUTHORIZED", "NOT EXECUTED", "NOT_EXECUTED"}


@dataclass(frozen=True)
class PreflightResult:
    ready: bool
    holds: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "holds": list(self.holds), "motion_authority": "NONE"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().lower()


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)


def _load_object(path: Path, label: str, holds: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        holds.append(f"{label}: unreadable JSON ({type(error).__name__})")
        return {}
    if not isinstance(value, dict):
        holds.append(f"{label}: top-level JSON is not an object")
        return {}
    return value


def evaluate(config_path: Path, root: Path = Path("/")) -> PreflightResult:
    """Evaluate readiness without opening devices, changing GPIO or spawning processes."""

    holds: list[str] = []
    config = _load_object(config_path, "host config", holds)
    if not config:
        return PreflightResult(False, tuple(holds))

    exact_values = (
        "service_identity",
        "service_group",
        "python_interpreter",
        "runtime_entrypoint",
        "runtime_backend",
        "serial_device",
        "gpio_backend",
    )
    hash_values = (
        "python_interpreter_sha256",
        "package_lock_sha256",
        "supervisor_config_sha256",
        "actuator_config_sha256",
        "compute_interface_config_sha256",
        "physical_hil_evidence_sha256",
        "power_loss_recovery_evidence_sha256",
        "rollback_evidence_sha256",
        "controls_approval_sha256",
        "electrical_approval_sha256",
        "test_authorization_sha256",
    )

    if config.get("identifier") != "HR-V0-HOST-DEPLOY-P0.1":
        holds.append("host config: identifier mismatch")
    if config.get("release_state") != REQUIRED_RELEASE_STATE:
        holds.append("host config: release state is not isolated-HIL released")
    if config.get("authorized_stage") != REQUIRED_STAGE:
        holds.append("host config: isolated-HIL authorization is absent")
    if config.get("motion_authority") != "NONE" or config.get("functional_safety_credit") != "NONE":
        holds.append("host config: prohibited authority or safety-credit claim")
    for key in exact_values:
        value = config.get(key)
        if not isinstance(value, str) or value.strip().upper() in UNRESOLVED_MARKERS:
            holds.append(f"host config: {key} unresolved")
    for key in hash_values:
        if not _is_sha256(config.get(key)):
            holds.append(f"host config: {key} is not an exact SHA-256")

    startup = config.get("startup_policy", {})
    required_policy = {
        "service_default": "DISABLED",
        "restart": "NO",
        "heartbeat_initial_state": "INPUT_OR_HIGH_IMPEDANCE",
        "serial_open_before_preflight": False,
        "gpio_access_before_preflight": False,
        "stale_motion_resume": False,
    }
    if not isinstance(startup, dict) or any(startup.get(key) != value for key, value in required_policy.items()):
        holds.append("host config: fail-closed startup policy changed")

    file_bindings = (
        ("supervisor_config_path", "supervisor_config_sha256"),
        ("actuator_config_path", "actuator_config_sha256"),
        ("compute_interface_config_path", "compute_interface_config_sha256"),
    )
    for path_key, hash_key in file_bindings:
        target = config.get(path_key)
        expected = config.get(hash_key)
        if not isinstance(target, str) or not target.startswith("/"):
            holds.append(f"host config: {path_key} is not an absolute target path")
            continue
        candidate = root / target.lstrip("/")
        if not candidate.is_file():
            holds.append(f"host config: {path_key} target absent")
        elif _is_sha256(expected) and _sha256(candidate) != expected.lower():
            holds.append(f"host config: {path_key} hash mismatch")

    return PreflightResult(not holds, tuple(holds))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("/"))
    args = parser.parse_args()
    result = evaluate(args.config, args.root)
    print(json.dumps(result.as_dict(), sort_keys=True))
    return 0 if result.ready else 78


if __name__ == "__main__":
    raise SystemExit(main())
