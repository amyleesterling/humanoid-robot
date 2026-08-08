"""Controlled HR-V0 mechanical-to-control configuration boundary.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

These values identify the current candidate geometry and engineering-unit
motion envelope.  They are not released physical limits.  Runtime motion
remains inhibited until a separate accepted evidence hash is configured.
"""

from __future__ import annotations

import re
from typing import Mapping


EXPECTED_MECHANICAL_BINDING = {
    "limit_set_id": "HR-V0-LIMITS-P0.2",
    "mechanical_revision": "HR-V0-MECH-P0.6",
    "arm_architecture_revision": "HR-V0-ARM-ARCH-P0.7",
    "hard_stop_revision": "HR-V0-HS-P0.3",
}

EXPECTED_ENGINEERING_LIMITS = {
    "J1": (-20.0, 70.0, "deg"),
    "J2": (15.0, 115.0, "deg"),
    "GRIPPER": (20.0, 75.0, "mm"),
}

ACCEPTED_LIMIT_STATE = "ACCEPTED-FOR-GUARDED-HIL"
EXPECTED_SUPERVISOR_CONFIGURATION_ID = "HR-V0-SUP-P0.3"
EXPECTED_ACTUATOR_CONFIGURATION_ID = "HR-V0-ACT-P0.3"


def selection_is_closed(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    upper = value.upper()
    return "SELECTION" not in upper and "REQUIRED" not in upper


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9A-Fa-f]{64}", value) is not None


def binding_is_current(binding: Mapping[str, object]) -> bool:
    return all(binding.get(key) == value for key, value in EXPECTED_MECHANICAL_BINDING.items())


def evidence_is_accepted(binding: Mapping[str, object]) -> bool:
    return (
        binding_is_current(binding)
        and binding.get("release_state") == ACCEPTED_LIMIT_STATE
        and is_sha256(binding.get("acceptance_evidence_hash"))
    )
