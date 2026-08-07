"""Fail-closed DYNAMIXEL configuration-readback contract.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

This module validates received register readback.  It does not communicate
with an actuator, turn torque on, establish a connector current rating, or
claim functional-safety integrity.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ActuatorReadback:
    actuator_id: int
    model: str
    model_number: int
    firmware_version: int
    operating_mode: int
    drive_mode: int
    startup_configuration: int
    torque_enable: int
    current_limit_raw: int
    goal_current_raw: int
    hardware_error_status: int


@dataclass(frozen=True)
class ActuatorRule:
    actuator_id: int
    model: str
    model_number: int | None
    firmware_version: int | None
    current_limit_raw: int
    goal_current_max_raw: int


class ActuatorConfiguration:
    """Load candidate rules and reject any torque-enable precondition mismatch."""

    def __init__(self, raw: Mapping[str, object]) -> None:
        self.configuration_id = str(raw["configuration_id"])
        self.operating_mode = int(raw["operating_mode"])
        self.startup_torque_on = bool(raw["startup_torque_on"])
        self.torque_on_by_goal_update = bool(raw["torque_on_by_goal_update"])
        self.external_branch_current_limit_a = raw["external_branch_current_limit_a"]
        self.rules: dict[str, ActuatorRule] = {}
        for joint, item in dict(raw["actuators"]).items():
            entry = dict(item)
            model_number = entry["model_number"]
            firmware_version = entry["firmware_version"]
            self.rules[str(joint)] = ActuatorRule(
                actuator_id=int(entry["id"]),
                model=str(entry["model"]),
                model_number=int(model_number) if isinstance(model_number, int) else None,
                firmware_version=int(firmware_version) if isinstance(firmware_version, int) else None,
                current_limit_raw=int(entry["current_limit_raw_candidate"]),
                goal_current_max_raw=int(entry["goal_current_max_raw_candidate"]),
            )

    @classmethod
    def from_json(cls, path: Path) -> "ActuatorConfiguration":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    @property
    def release_selections_closed(self) -> bool:
        external_limit = self.external_branch_current_limit_a
        identities = all(
            rule.model_number is not None and rule.firmware_version is not None
            for rule in self.rules.values()
        )
        return isinstance(external_limit, (int, float)) and identities

    def torque_enable_inhibits(self, joint: str, readback: ActuatorReadback) -> tuple[str, ...]:
        """Return every reason torque enable must remain false."""

        rule = self.rules[joint]
        reasons: list[str] = []
        if not self.release_selections_closed:
            reasons.append("RELEASE_SELECTIONS_OPEN")
        if readback.actuator_id != rule.actuator_id:
            reasons.append("ACTUATOR_ID_MISMATCH")
        if readback.model != rule.model:
            reasons.append("MODEL_MISMATCH")
        if rule.model_number is None or readback.model_number != rule.model_number:
            reasons.append("MODEL_NUMBER_UNVERIFIED")
        if rule.firmware_version is None or readback.firmware_version != rule.firmware_version:
            reasons.append("FIRMWARE_VERSION_UNVERIFIED")
        if readback.operating_mode != self.operating_mode:
            reasons.append("OPERATING_MODE_MISMATCH")
        if bool(readback.drive_mode & 0x08) is not self.torque_on_by_goal_update:
            reasons.append("TORQUE_ON_GOAL_UPDATE_MISMATCH")
        if bool(readback.startup_configuration & 0x01) is not self.startup_torque_on:
            reasons.append("STARTUP_TORQUE_MISMATCH")
        if readback.torque_enable != 0:
            reasons.append("TORQUE_ALREADY_ENABLED")
        if readback.current_limit_raw != rule.current_limit_raw:
            reasons.append("CURRENT_LIMIT_MISMATCH")
        if abs(readback.goal_current_raw) > rule.goal_current_max_raw:
            reasons.append("GOAL_CURRENT_EXCEEDS_CANDIDATE")
        if readback.hardware_error_status != 0:
            reasons.append("HARDWARE_ERROR_PRESENT")
        return tuple(reasons)

