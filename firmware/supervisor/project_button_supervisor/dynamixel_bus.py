"""Fail-closed DYNAMIXEL Protocol 2.0 bus and execution boundary.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

This module deliberately separates packet transport from authority.  It can
only configure or enable a received bus after every identity, current,
calibration, profile and device-path selection in actuator-config.json is
closed.  The committed repository configuration is intentionally incomplete,
so it refuses to open a serial port or write any actuator register.

The register addresses are the common XM430/XM540 X-series addresses checked
against the ROBOTIS e-Manual on 2026-08-07.  A successful source test is not a
substitute for received-hardware inspection, current/thermal characterization,
HIL fault injection, or qualified review.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable
from typing import Mapping, Protocol

from .actuator_config import ActuatorConfiguration, ActuatorReadback


class BusError(RuntimeError):
    """A communication, configuration, authority, or telemetry failure."""


class RegisterTransport(Protocol):
    """Small testable subset of the ROBOTIS SDK used by the supervisor."""

    def open(self) -> None: ...
    def close(self) -> None: ...
    def discover(self) -> Mapping[int, int]: ...
    def read(self, actuator_id: int, address: int, size: int, *, signed: bool = False) -> int: ...
    def write(self, actuator_id: int, address: int, size: int, value: int, *, signed: bool = False) -> None: ...
    def sync_write(self, address: int, size: int, values: Mapping[int, int], *, signed: bool = False) -> None: ...


class MotionAuthority(Protocol):
    torque_enable_request: bool
    active_trajectory_id: str | None


@dataclass(frozen=True)
class Register:
    address: int
    size: int
    signed: bool = False


MODEL_NUMBER = Register(0, 2)
FIRMWARE_VERSION = Register(6, 1)
ACTUATOR_ID = Register(7, 1)
DRIVE_MODE = Register(10, 1)
OPERATING_MODE = Register(11, 1)
CURRENT_LIMIT = Register(38, 2)
STARTUP_CONFIGURATION = Register(60, 1)
TORQUE_ENABLE = Register(64, 1)
HARDWARE_ERROR_STATUS = Register(70, 1)
BUS_WATCHDOG = Register(98, 1, True)
GOAL_CURRENT = Register(102, 2, True)
PROFILE_ACCELERATION = Register(108, 4)
PROFILE_VELOCITY = Register(112, 4)
GOAL_POSITION = Register(116, 4, True)
PRESENT_CURRENT = Register(126, 2, True)
PRESENT_VELOCITY = Register(128, 4, True)
PRESENT_POSITION = Register(132, 4, True)
PRESENT_INPUT_VOLTAGE = Register(144, 2)
PRESENT_TEMPERATURE = Register(146, 1)


@dataclass(frozen=True)
class ActuatorTelemetry:
    actuator_id: int
    torque_enable: int
    bus_watchdog: int
    hardware_error_status: int
    configured_current_limit_raw: int
    active_goal_current_raw: int
    present_current_raw: int
    present_velocity_raw: int
    present_position_raw: int
    present_input_voltage_raw: int
    present_temperature_c: int


class DynamixelBusController:
    """Own ordered configuration, torque enable, command writes and shutdown."""

    def __init__(self, transport: RegisterTransport, config: ActuatorConfiguration) -> None:
        self.transport = transport
        self.config = config
        self.is_open = False
        self.is_configured = False
        self.torque_enabled = False
        self.active_trajectory_id: str | None = None

    @property
    def joint_by_id(self) -> dict[int, str]:
        return {rule.actuator_id: joint for joint, rule in self.config.rules.items()}

    def connect_and_configure(self) -> None:
        """Open only a fully frozen candidate, force torque off, then configure."""

        if not self.config.release_selections_closed:
            raise BusError("release selections remain open; serial port will not be opened")
        expected_ids = set(self.joint_by_id)
        touched_ids = set(expected_ids)
        try:
            self.transport.open()
            self.is_open = True
            self._torque_off_ids(expected_ids, verify=True)
            discovered = dict(self.transport.discover())
            touched_ids.update(discovered)
            self._torque_off_ids(discovered, verify=True)
            if set(discovered) != expected_ids:
                raise BusError(
                    f"discovered IDs {sorted(discovered)} do not exactly match released IDs {sorted(expected_ids)}"
                )
            for actuator_id, model_number in discovered.items():
                joint = self.joint_by_id[actuator_id]
                expected = self.config.rules[joint].model_number
                if expected is None or model_number != expected:
                    raise BusError(f"{joint} broadcast identity mismatch")
            for joint, rule in self.config.rules.items():
                self._configure_one(joint, rule.actuator_id)
            self.is_configured = True
        except Exception as exc:
            self._best_effort_torque_off(touched_ids)
            self._close_transport()
            if isinstance(exc, BusError):
                raise
            raise BusError(f"bus configuration failed: {exc}") from exc

    def start_trajectory(
        self,
        authority: MotionAuthority,
        trajectory_id: str,
        starting_positions: Mapping[str, float],
    ) -> None:
        """Enable torque last, only for the exact fresh supervisor trajectory."""

        if not self.is_configured or not self.is_open:
            raise BusError("bus is not configured")
        if (
            not authority.torque_enable_request
            or authority.active_trajectory_id != trajectory_id
            or not trajectory_id
        ):
            raise BusError("fresh matching supervisor motion authority is absent")
        if set(starting_positions) != set(self.config.rules):
            raise BusError("starting-position joint set mismatch")

        try:
            raw_targets = {
                self.config.rules[joint].actuator_id: self.config.engineering_to_raw(joint, position)
                for joint, position in starting_positions.items()
            }
            for actuator_id, raw_target in raw_targets.items():
                rule = self.config.rules[self.joint_by_id[actuator_id]]
                assert rule.start_tolerance_raw is not None
                present = self._read(actuator_id, PRESENT_POSITION)
                if abs(present - raw_target) > rule.start_tolerance_raw:
                    raise BusError(f"ID {actuator_id} is outside released raw start tolerance")

            # Establish zero-motion targets and current/profile bounds before
            # the bus watchdog and torque are enabled.
            self._sync_write(GOAL_POSITION, raw_targets)
            for joint, rule in self.config.rules.items():
                assert rule.profile_acceleration_raw is not None
                assert rule.profile_velocity_raw is not None
                self._write(rule.actuator_id, GOAL_CURRENT, rule.goal_current_max_raw)
                self._write(rule.actuator_id, PROFILE_ACCELERATION, rule.profile_acceleration_raw)
                self._write(rule.actuator_id, PROFILE_VELOCITY, rule.profile_velocity_raw)
                self._write(rule.actuator_id, BUS_WATCHDOG, self.config.bus_watchdog_raw_candidate)
            self._sync_write(TORQUE_ENABLE, {actuator_id: 1 for actuator_id in raw_targets})
            for actuator_id in raw_targets:
                if self._read(actuator_id, TORQUE_ENABLE) != 1:
                    raise BusError(f"ID {actuator_id} torque-enable readback mismatch")
            self.torque_enabled = True
            self.active_trajectory_id = trajectory_id
        except Exception as exc:
            self._best_effort_torque_off(set(self.joint_by_id))
            self.torque_enabled = False
            self.active_trajectory_id = None
            if isinstance(exc, BusError):
                raise
            raise BusError(f"torque-enable sequence failed: {exc}") from exc

    def write_sample(
        self,
        authority: MotionAuthority,
        trajectory_id: str,
        positions: Mapping[str, float],
    ) -> Mapping[str, ActuatorTelemetry]:
        """Write one bounded synchronous position sample and verify telemetry."""

        if (
            not self.torque_enabled
            or not authority.torque_enable_request
            or authority.active_trajectory_id != trajectory_id
            or self.active_trajectory_id != trajectory_id
        ):
            self.stop()
            raise BusError("motion authority missing or trajectory identity changed")
        if set(positions) != set(self.config.rules):
            self.stop()
            raise BusError("sample joint set mismatch")
        try:
            values = {
                self.config.rules[joint].actuator_id: self.config.engineering_to_raw(joint, position)
                for joint, position in positions.items()
            }
            self._sync_write(GOAL_POSITION, values)
            telemetry = self.poll_telemetry(require_torque=True)
            return telemetry
        except Exception as exc:
            self._best_effort_torque_off(set(self.joint_by_id))
            self.torque_enabled = False
            self.active_trajectory_id = None
            if isinstance(exc, BusError):
                raise
            raise BusError(f"sample execution failed: {exc}") from exc

    def read_positions_engineering(self, *, require_torque: bool) -> Mapping[str, float]:
        """Return received positions through the released calibration only."""

        telemetry = self.poll_telemetry(require_torque=require_torque)
        return self.positions_from_telemetry(telemetry)

    def write_sample_engineering(
        self,
        authority: MotionAuthority,
        trajectory_id: str,
        positions: Mapping[str, float],
    ) -> Mapping[str, float]:
        """Write one sample and return the checked received engineering pose."""

        telemetry = self.write_sample(authority, trajectory_id, positions)
        return self.positions_from_telemetry(telemetry)

    def positions_from_telemetry(
        self, telemetry: Mapping[str, ActuatorTelemetry]
    ) -> Mapping[str, float]:
        if set(telemetry) != set(self.config.rules):
            raise BusError("telemetry joint set mismatch")
        try:
            return {
                joint: self.config.raw_to_engineering(
                    joint, telemetry[joint].present_position_raw
                )
                for joint in self.config.rules
            }
        except (KeyError, TypeError, ValueError) as exc:
            raise BusError(f"received position conversion failed: {exc}") from exc

    def poll_telemetry(self, *, require_torque: bool) -> Mapping[str, ActuatorTelemetry]:
        """Read all execution invariants and force torque-off on any failure."""

        try:
            return self._poll_telemetry(require_torque=require_torque)
        except Exception:
            self._best_effort_torque_off(set(self.joint_by_id))
            self.torque_enabled = False
            self.active_trajectory_id = None
            raise

    def _poll_telemetry(self, *, require_torque: bool) -> Mapping[str, ActuatorTelemetry]:
        result: dict[str, ActuatorTelemetry] = {}
        for joint, rule in self.config.rules.items():
            actuator_id = rule.actuator_id
            item = ActuatorTelemetry(
                actuator_id=actuator_id,
                torque_enable=self._read(actuator_id, TORQUE_ENABLE),
                bus_watchdog=self._read(actuator_id, BUS_WATCHDOG),
                hardware_error_status=self._read(actuator_id, HARDWARE_ERROR_STATUS),
                configured_current_limit_raw=self._read(actuator_id, CURRENT_LIMIT),
                active_goal_current_raw=self._read(actuator_id, GOAL_CURRENT),
                present_current_raw=self._read(actuator_id, PRESENT_CURRENT),
                present_velocity_raw=self._read(actuator_id, PRESENT_VELOCITY),
                present_position_raw=self._read(actuator_id, PRESENT_POSITION),
                present_input_voltage_raw=self._read(actuator_id, PRESENT_INPUT_VOLTAGE),
                present_temperature_c=self._read(actuator_id, PRESENT_TEMPERATURE),
            )
            if item.hardware_error_status != 0:
                raise BusError(f"{joint} hardware error status is nonzero")
            if item.bus_watchdog == -1:
                raise BusError(f"{joint} bus watchdog expired")
            if item.configured_current_limit_raw != rule.current_limit_raw:
                raise BusError(f"{joint} configured-current-limit readback changed during execution")
            expected_goal_current = rule.goal_current_max_raw if require_torque else 0
            if item.active_goal_current_raw != expected_goal_current:
                raise BusError(f"{joint} goal-current readback disagrees with torque state")
            if require_torque and item.torque_enable != 1:
                raise BusError(f"{joint} torque dropped during execution")
            if not require_torque and item.torque_enable != 0:
                raise BusError(f"{joint} torque is enabled outside motion authority")
            if abs(item.present_current_raw) > rule.current_limit_raw:
                raise BusError(f"{joint} present-current readback exceeds configured raw limit")
            assert rule.minimum_input_voltage_raw is not None
            assert rule.maximum_input_voltage_raw is not None
            assert rule.maximum_temperature_c is not None
            if not rule.minimum_input_voltage_raw <= item.present_input_voltage_raw <= rule.maximum_input_voltage_raw:
                raise BusError(f"{joint} input-voltage readback is outside the released envelope")
            if item.present_temperature_c > rule.maximum_temperature_c:
                raise BusError(f"{joint} temperature readback exceeds the released limit")
            result[joint] = item
        return result

    def stop(self) -> None:
        self._best_effort_torque_off(set(self.joint_by_id))
        self._best_effort_goal_current_zero(set(self.joint_by_id))
        self.torque_enabled = False
        self.active_trajectory_id = None

    def close(self) -> None:
        self.stop()
        self._close_transport()
        self.is_configured = False

    def _configure_one(self, joint: str, actuator_id: int) -> None:
        rule = self.config.rules[joint]
        if self._read(actuator_id, MODEL_NUMBER) != rule.model_number:
            raise BusError(f"{joint} model-number readback mismatch")
        if self._read(actuator_id, FIRMWARE_VERSION) != rule.firmware_version:
            raise BusError(f"{joint} firmware-version readback mismatch")
        if self._read(actuator_id, ACTUATOR_ID) != actuator_id:
            raise BusError(f"{joint} ID register mismatch")
        if self._read(actuator_id, TORQUE_ENABLE) != 0:
            raise BusError(f"{joint} torque was not removed before configuration")
        if self._read(actuator_id, BUS_WATCHDOG) == -1:
            self._write(actuator_id, BUS_WATCHDOG, 0)

        desired = (
            (DRIVE_MODE, self.config.expected_drive_mode),
            (OPERATING_MODE, self.config.operating_mode),
            (STARTUP_CONFIGURATION, 0),
            (CURRENT_LIMIT, rule.current_limit_raw),
            (GOAL_CURRENT, 0),
            (BUS_WATCHDOG, 0),
        )
        for register, value in desired:
            if self._read(actuator_id, register) != value:
                self._write(actuator_id, register, value)
            if self._read(actuator_id, register) != value:
                raise BusError(f"{joint} register {register.address} failed readback")

        readback = ActuatorReadback(
            actuator_id=self._read(actuator_id, ACTUATOR_ID),
            model=rule.model,
            model_number=self._read(actuator_id, MODEL_NUMBER),
            firmware_version=self._read(actuator_id, FIRMWARE_VERSION),
            operating_mode=self._read(actuator_id, OPERATING_MODE),
            drive_mode=self._read(actuator_id, DRIVE_MODE),
            startup_configuration=self._read(actuator_id, STARTUP_CONFIGURATION),
            torque_enable=self._read(actuator_id, TORQUE_ENABLE),
            current_limit_raw=self._read(actuator_id, CURRENT_LIMIT),
            goal_current_raw=self._read(actuator_id, GOAL_CURRENT),
            hardware_error_status=self._read(actuator_id, HARDWARE_ERROR_STATUS),
        )
        inhibits = self.config.torque_enable_inhibits(joint, readback)
        if inhibits:
            raise BusError(f"{joint} configuration inhibits: {','.join(inhibits)}")

    def _torque_off_ids(self, ids: Iterable[int], *, verify: bool) -> None:
        actuator_ids = sorted(int(value) for value in ids)
        for actuator_id in actuator_ids:
            self._write(actuator_id, TORQUE_ENABLE, 0)
        if verify:
            for actuator_id in actuator_ids:
                if self._read(actuator_id, TORQUE_ENABLE) != 0:
                    raise BusError(f"ID {actuator_id} torque-off readback mismatch")

    def _best_effort_torque_off(self, ids: set[int]) -> None:
        if not self.is_open:
            return
        for actuator_id in sorted(ids):
            try:
                self._write(actuator_id, TORQUE_ENABLE, 0)
            except Exception:
                pass

    def _best_effort_goal_current_zero(self, ids: set[int]) -> None:
        if not self.is_open:
            return
        for actuator_id in sorted(ids):
            try:
                self._write(actuator_id, GOAL_CURRENT, 0)
            except Exception:
                pass

    def _read(self, actuator_id: int, register: Register) -> int:
        return self.transport.read(
            actuator_id, register.address, register.size, signed=register.signed
        )

    def _write(self, actuator_id: int, register: Register, value: int) -> None:
        self.transport.write(
            actuator_id, register.address, register.size, value, signed=register.signed
        )

    def _sync_write(self, register: Register, values: Mapping[int, int]) -> None:
        self.transport.sync_write(
            register.address, register.size, values, signed=register.signed
        )

    def _close_transport(self) -> None:
        if self.is_open:
            try:
                self.transport.close()
            finally:
                self.is_open = False
