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

from .mechanical_binding import (
    EXPECTED_ENGINEERING_LIMITS,
    EXPECTED_ACTUATOR_CONFIGURATION_ID,
    binding_is_current,
    evidence_is_accepted,
)


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
    profile_velocity_raw: int | None
    profile_acceleration_raw: int | None
    position_zero_raw: int | None
    position_zero_engineering: float | None
    raw_per_unit: float | None
    direction: int | None
    minimum_raw: int | None
    maximum_raw: int | None
    start_tolerance_raw: int | None
    minimum_input_voltage_raw: int | None
    maximum_input_voltage_raw: int | None
    maximum_temperature_c: int | None
    minimum_engineering: float
    maximum_engineering: float
    engineering_unit: str


class ActuatorConfiguration:
    """Load candidate rules and reject any torque-enable precondition mismatch."""

    def __init__(self, raw: Mapping[str, object]) -> None:
        self.configuration_id = str(raw["configuration_id"])
        self.operating_mode = int(raw["operating_mode"])
        self.expected_drive_mode = int(raw["expected_drive_mode"])
        self.startup_torque_on = bool(raw["startup_torque_on"])
        self.torque_on_by_goal_update = bool(raw["torque_on_by_goal_update"])
        self.bus_watchdog_raw_candidate = int(raw["bus_watchdog_raw_candidate"])
        self.transport = dict(raw["transport"])
        self.mechanical_limit_binding = dict(raw["mechanical_limit_binding"])
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
                profile_velocity_raw=_optional_int(entry["profile_velocity_raw_candidate"]),
                profile_acceleration_raw=_optional_int(entry["profile_acceleration_raw_candidate"]),
                position_zero_raw=_optional_int(entry["position_zero_raw"]),
                position_zero_engineering=_optional_float(entry["position_zero_engineering"]),
                raw_per_unit=_optional_float(entry["raw_per_unit"]),
                direction=_optional_int(entry["direction"]),
                minimum_raw=_optional_int(entry["minimum_raw"]),
                maximum_raw=_optional_int(entry["maximum_raw"]),
                start_tolerance_raw=_optional_int(entry["start_tolerance_raw"]),
                minimum_input_voltage_raw=_optional_int(entry["minimum_input_voltage_raw"]),
                maximum_input_voltage_raw=_optional_int(entry["maximum_input_voltage_raw"]),
                maximum_temperature_c=_optional_int(entry["maximum_temperature_c"]),
                minimum_engineering=float(entry["minimum_engineering"]),
                maximum_engineering=float(entry["maximum_engineering"]),
                engineering_unit=str(entry["engineering_unit"]),
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
        actuator_ids = [rule.actuator_id for rule in self.rules.values()]
        identity_set_valid = (
            len(actuator_ids) == len(set(actuator_ids))
            and all(0 <= actuator_id <= 252 for actuator_id in actuator_ids)
        )
        motion_scales = all(
            None not in (
                rule.profile_velocity_raw,
                rule.profile_acceleration_raw,
                rule.position_zero_raw,
                rule.position_zero_engineering,
                rule.raw_per_unit,
                rule.direction,
                rule.minimum_raw,
                rule.maximum_raw,
                rule.start_tolerance_raw,
                rule.minimum_input_voltage_raw,
                rule.maximum_input_voltage_raw,
                rule.maximum_temperature_c,
            )
            and rule.direction in (-1, 1)
            and bool(rule.raw_per_unit and rule.raw_per_unit > 0)
            and bool(rule.profile_velocity_raw is not None and rule.profile_velocity_raw > 0)
            and bool(rule.profile_acceleration_raw is not None and rule.profile_acceleration_raw > 0)
            and bool(rule.minimum_raw is not None and rule.maximum_raw is not None and rule.minimum_raw < rule.maximum_raw)
            and bool(
                rule.position_zero_raw is not None
                and rule.minimum_raw is not None
                and rule.maximum_raw is not None
                and rule.minimum_raw <= rule.position_zero_raw <= rule.maximum_raw
            )
            and bool(rule.start_tolerance_raw is not None and rule.start_tolerance_raw >= 0)
            and bool(
                rule.minimum_input_voltage_raw is not None
                and rule.maximum_input_voltage_raw is not None
                and 0 < rule.minimum_input_voltage_raw < rule.maximum_input_voltage_raw
            )
            and bool(rule.maximum_temperature_c is not None and rule.maximum_temperature_c > 0)
            and 0 < rule.goal_current_max_raw <= rule.current_limit_raw
            for rule in self.rules.values()
        )
        port = self.transport.get("device")
        transport_closed = (
            self.transport.get("sdk_version") == "4.0.5"
            and self.transport.get("protocol") == 2.0
            and self.transport.get("baud_rate") == 1_000_000
            and isinstance(port, str)
            and "SELECTION" not in port.upper()
            and "REQUIRED" not in port.upper()
        )
        external_limit_valid = (
            isinstance(external_limit, (int, float))
            and not isinstance(external_limit, bool)
            and external_limit > 0
        )
        bus_watchdog_valid = 1 <= self.bus_watchdog_raw_candidate <= 127
        exact_axes = set(self.rules) == set(EXPECTED_ENGINEERING_LIMITS)
        engineering_limits_current = exact_axes and all(
            (
                self.rules[joint].minimum_engineering,
                self.rules[joint].maximum_engineering,
                self.rules[joint].engineering_unit,
            )
            == expected
            for joint, expected in EXPECTED_ENGINEERING_LIMITS.items()
        )
        return (
            self.configuration_id == EXPECTED_ACTUATOR_CONFIGURATION_ID
            and external_limit_valid
            and identities
            and identity_set_valid
            and motion_scales
            and transport_closed
            and bus_watchdog_valid
            and engineering_limits_current
            and binding_is_current(self.mechanical_limit_binding)
            and evidence_is_accepted(self.mechanical_limit_binding)
        )

    def engineering_to_raw(self, joint: str, position: float) -> int:
        """Convert a released engineering position to a checked raw target.

        The repository candidate deliberately lacks the received zero/direction/
        scale values, so this method fails closed until those fields are frozen.
        """

        rule = self.rules[joint]
        if not self.release_selections_closed:
            raise ValueError("actuator transport/calibration selections remain open")
        if not rule.minimum_engineering <= float(position) <= rule.maximum_engineering:
            raise ValueError(f"{joint} engineering target outside controlled motion envelope")
        assert rule.position_zero_raw is not None
        assert rule.position_zero_engineering is not None
        assert rule.raw_per_unit is not None
        assert rule.direction is not None
        assert rule.minimum_raw is not None
        assert rule.maximum_raw is not None
        raw = round(
            rule.position_zero_raw
            + rule.direction * (float(position) - rule.position_zero_engineering) * rule.raw_per_unit
        )
        if not rule.minimum_raw <= raw <= rule.maximum_raw:
            raise ValueError(f"{joint} raw target outside released calibration envelope")
        return raw

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
        if readback.drive_mode != self.expected_drive_mode:
            reasons.append("DRIVE_MODE_MISMATCH")
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


def _optional_int(value: object) -> int | None:
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else None


def _optional_float(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
