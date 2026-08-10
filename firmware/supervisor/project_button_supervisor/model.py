"""Fail-closed HR-V0 supervisor authority model.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

This module has no API for closing the hardware contactors.  Its only motion
output is a non-safety torque-enable request which is false unless the hardware
chain is already armed and a fresh trajectory has passed every configured
check.  Hardware observations are diagnostic evidence, not safety inputs with
claimed integrity.
"""

from __future__ import annotations

import json
import copy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .mechanical_binding import (
    EXPECTED_ENGINEERING_LIMITS,
    EXPECTED_SUPERVISOR_CONFIGURATION_ID,
    binding_is_current,
    evidence_is_accepted,
    is_sha256,
)
from .kinematics import PlanarKinematicModel


WARNING = "PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION"


class OperatingState(str, Enum):
    POWER_OFF = "POWER_OFF"
    SAFE_DISABLED = "SAFE_DISABLED"
    RESET_REQUIRED = "RESET_REQUIRED"
    SAFE_READY = "SAFE_READY"
    ARMED = "ARMED"
    DRIVE_ENABLED = "DRIVE_ENABLED"
    CONTROLLED_STOP = "CONTROLLED_STOP"
    FAULT_LATCHED = "FAULT_LATCHED"
    ENERGY_REMOVED = "ENERGY_REMOVED"


class MotionMode(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    SETUP = "SETUP"


class FaultCode(str, Enum):
    ESTOP_OPEN = "ESTOP_OPEN"
    WATCHDOG_UNHEALTHY = "WATCHDOG_UNHEALTHY"
    EDM_UNHEALTHY = "EDM_UNHEALTHY"
    BUS_UNHEALTHY = "BUS_UNHEALTHY"
    COMPUTE_UNDERVOLTAGE = "COMPUTE_UNDERVOLTAGE"
    CONTACTOR_DISAGREEMENT = "CONTACTOR_DISAGREEMENT"
    UNEXPECTED_ARM_ORDER = "UNEXPECTED_ARM_ORDER"
    COMMAND_REJECTED = "COMMAND_REJECTED"
    COMMAND_EXPIRED = "COMMAND_EXPIRED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    HARDWARE_PERMIT_DROPPED = "HARDWARE_PERMIT_DROPPED"


@dataclass(frozen=True)
class JointRule:
    minimum: float
    maximum: float
    unit: str
    start_tolerance: float | None
    terminal_tolerance: float | None


@dataclass(frozen=True)
class SupervisorConfig:
    configuration_id: str
    configuration_hash: str
    maximum_command_age_ms: int
    maximum_tcp_speed_m_s: float
    automatic_joint_speed_deg_s: float
    setup_joint_speed_deg_s: float
    automatic_gripper_speed_mm_s: float
    setup_gripper_speed_mm_s: float
    maximum_sample_lateness_ms: int | None
    maximum_trajectory_samples: int | None
    maximum_trajectory_duration_ms: int | None
    maximum_execution_slack_ms: int | None
    joints: Mapping[str, JointRule]
    kinematic_model_hash: str
    kinematic_model: PlanarKinematicModel
    mechanical_limit_binding: Mapping[str, object]

    @classmethod
    def from_json(cls, path: Path) -> "SupervisorConfig":
        raw = json.loads(path.read_text(encoding="utf-8"))
        kinematic_model = PlanarKinematicModel.from_mapping(raw)
        return cls(
            configuration_id=raw["configuration_id"],
            configuration_hash=raw["configuration_hash"],
            maximum_command_age_ms=int(raw["maximum_command_age_ms"]),
            maximum_tcp_speed_m_s=float(raw["maximum_tcp_speed_m_s"]),
            automatic_joint_speed_deg_s=float(raw["automatic_joint_speed_deg_s"]),
            setup_joint_speed_deg_s=float(raw["setup_joint_speed_deg_s"]),
            automatic_gripper_speed_mm_s=float(raw["automatic_gripper_speed_mm_s"]),
            setup_gripper_speed_mm_s=float(raw["setup_gripper_speed_mm_s"]),
            maximum_sample_lateness_ms=(
                int(raw["maximum_sample_lateness_ms"])
                if isinstance(raw.get("maximum_sample_lateness_ms"), int)
                and not isinstance(raw.get("maximum_sample_lateness_ms"), bool)
                else None
            ),
            maximum_trajectory_samples=(
                int(raw["maximum_trajectory_samples"])
                if isinstance(raw.get("maximum_trajectory_samples"), int)
                and not isinstance(raw.get("maximum_trajectory_samples"), bool)
                else None
            ),
            maximum_trajectory_duration_ms=(
                int(raw["maximum_trajectory_duration_ms"])
                if isinstance(raw.get("maximum_trajectory_duration_ms"), int)
                and not isinstance(raw.get("maximum_trajectory_duration_ms"), bool)
                else None
            ),
            maximum_execution_slack_ms=(
                int(raw["maximum_execution_slack_ms"])
                if isinstance(raw.get("maximum_execution_slack_ms"), int)
                and not isinstance(raw.get("maximum_execution_slack_ms"), bool)
                else None
            ),
            joints={name: JointRule(**rule) for name, rule in raw["joints"].items()},
            kinematic_model_hash=raw["kinematic_model_hash"],
            kinematic_model=kinematic_model,
            mechanical_limit_binding=dict(raw["mechanical_limit_binding"]),
        )

    @property
    def selections_closed(self) -> bool:
        values = (self.configuration_hash, self.kinematic_model_hash)
        hashes_closed = all(is_sha256(value) for value in values)
        tolerances_closed = all(
            rule.start_tolerance is not None and rule.terminal_tolerance is not None
            for rule in self.joints.values()
        )
        exact_axes = set(self.joints) == set(EXPECTED_ENGINEERING_LIMITS)
        limits_current = exact_axes and all(
            (
                self.joints[axis].minimum,
                self.joints[axis].maximum,
                self.joints[axis].unit,
            )
            == expected
            for axis, expected in EXPECTED_ENGINEERING_LIMITS.items()
        )
        return (
            self.configuration_id == EXPECTED_SUPERVISOR_CONFIGURATION_ID
            and hashes_closed
            and tolerances_closed
            and self.maximum_sample_lateness_ms is not None
            and self.maximum_sample_lateness_ms >= 0
            and self.maximum_trajectory_samples is not None
            and self.maximum_trajectory_samples > 0
            and self.maximum_trajectory_duration_ms is not None
            and self.maximum_trajectory_duration_ms > 0
            and self.maximum_execution_slack_ms is not None
            and self.maximum_execution_slack_ms >= 0
            and limits_current
            and self.kinematic_model.selections_closed
            and self.kinematic_model.configured_model_hash == self.kinematic_model_hash
            and binding_is_current(self.mechanical_limit_binding)
            and evidence_is_accepted(self.mechanical_limit_binding)
        )


@dataclass(frozen=True)
class HardwareSnapshot:
    control_power: bool
    estop_healthy: bool
    watchdog_healthy: bool
    edm_healthy: bool
    bus_healthy: bool
    compute_undervoltage: bool
    sr1_ready: bool
    sra1_armed: bool
    k1_feedback: bool
    k2_feedback: bool
    positions: Mapping[str, float]


@dataclass(frozen=True)
class TrajectorySample:
    offset_ms: int
    positions: Mapping[str, float]
    velocities: Mapping[str, float]


@dataclass(frozen=True)
class TrajectoryCommand:
    trajectory_id: str
    session_id: str
    sequence: int
    source_time_ms: int
    validity_deadline_ms: int
    execution_deadline_ms: int
    configuration_hash: str
    kinematic_model_hash: str
    sender_state: str
    mode: MotionMode
    starting_positions: Mapping[str, float]
    samples: Sequence[TrajectorySample]
    expected_terminal_positions: Mapping[str, float]


@dataclass(frozen=True)
class SupervisorOutputs:
    heartbeat_allowed: bool
    torque_enable_request: bool
    state: OperatingState
    active_trajectory_id: str | None


@dataclass(frozen=True)
class EventRecord:
    monotonic_ms: int
    event: str
    state: OperatingState
    detail: str


KinematicValidator = Callable[[Sequence[TrajectorySample]], Sequence[float]]


class Supervisor:
    """Non-safety authority state machine with explicit stale-target invalidation."""

    def __init__(self, config: SupervisorConfig, kinematic_validator: KinematicValidator, session_id: str):
        if not session_id:
            raise ValueError("a nonempty boot/session ID is required")
        self.config = config
        self._kinematic_validator = kinematic_validator
        self.session_id = session_id
        self.state = OperatingState.POWER_OFF
        self.fault: FaultCode | None = None
        self.last_sequence = -1
        self.active_command: TrajectoryCommand | None = None
        self._last_snapshot: HardwareSnapshot | None = None
        self._safe_ready_seen = False
        self._reset_required_seen = False
        self._watchdog_ever_healthy = False
        self.events: list[EventRecord] = []

    @classmethod
    def from_json(cls, path: Path, session_id: str) -> "Supervisor":
        """Build only with the validator bound to the same configuration file."""

        config = SupervisorConfig.from_json(path)
        return cls(config, config.kinematic_model.validator(), session_id)

    @property
    def outputs(self) -> SupervisorOutputs:
        control_power = bool(self._last_snapshot and self._last_snapshot.control_power)
        return SupervisorOutputs(
            heartbeat_allowed=control_power and self.state is not OperatingState.FAULT_LATCHED,
            torque_enable_request=self.state is OperatingState.DRIVE_ENABLED and self.active_command is not None,
            state=self.state,
            active_trajectory_id=self.active_command.trajectory_id if self.active_command else None,
        )

    def observe_hardware(self, snapshot: HardwareSnapshot, now_ms: int) -> None:
        self._last_snapshot = snapshot
        if not snapshot.control_power:
            self._invalidate_target()
            self._safe_ready_seen = False
            self._reset_required_seen = False
            self._watchdog_ever_healthy = False
            self.fault = None
            self._transition(OperatingState.POWER_OFF, now_ms, "control power absent")
            return

        if self.state is OperatingState.POWER_OFF:
            self._transition(OperatingState.SAFE_DISABLED, now_ms, "control power applied")

        if self.state is OperatingState.FAULT_LATCHED:
            return

        for condition, code, detail in (
            (not snapshot.estop_healthy, FaultCode.ESTOP_OPEN, "E-stop channel not healthy"),
            (not snapshot.edm_healthy, FaultCode.EDM_UNHEALTHY, "EDM not healthy"),
            (not snapshot.bus_healthy, FaultCode.BUS_UNHEALTHY, "actuator bus not healthy"),
            (snapshot.compute_undervoltage, FaultCode.COMPUTE_UNDERVOLTAGE, "compute undervoltage"),
        ):
            if condition:
                self._latch_fault(code, now_ms, detail)
                return

        if snapshot.watchdog_healthy:
            self._watchdog_ever_healthy = True
        elif self._watchdog_ever_healthy:
            self._latch_fault(FaultCode.WATCHDOG_UNHEALTHY, now_ms, "watchdog permit dropped after becoming healthy")
            return
        else:
            self._invalidate_target()
            self._transition(OperatingState.SAFE_DISABLED, now_ms, "waiting for three valid watchdog heartbeat edges")
            return

        if snapshot.k1_feedback != snapshot.k2_feedback or snapshot.sra1_armed != (snapshot.k1_feedback and snapshot.k2_feedback):
            self._latch_fault(FaultCode.CONTACTOR_DISAGREEMENT, now_ms, "SRA1/K1/K2 feedback disagreement")
            return

        if not snapshot.sr1_ready:
            if self.state in (OperatingState.ARMED, OperatingState.DRIVE_ENABLED):
                self._latch_fault(FaultCode.HARDWARE_PERMIT_DROPPED, now_ms, "SR1 dropped after hardware ARM")
                return
            if snapshot.sra1_armed or snapshot.k1_feedback or snapshot.k2_feedback:
                self._latch_fault(FaultCode.CONTACTOR_DISAGREEMENT, now_ms, "contactor energized without SR1 readiness")
                return
            self._invalidate_target()
            self._safe_ready_seen = False
            self._reset_required_seen = True
            self._transition(OperatingState.RESET_REQUIRED, now_ms, "physical reset required")
            return

        if not snapshot.sra1_armed:
            if self.state in (OperatingState.ARMED, OperatingState.DRIVE_ENABLED):
                self._latch_fault(FaultCode.HARDWARE_PERMIT_DROPPED, now_ms, "SRA1 or contactors dropped after ARM")
                return
            if snapshot.k1_feedback or snapshot.k2_feedback:
                self._latch_fault(FaultCode.CONTACTOR_DISAGREEMENT, now_ms, "feedback on while SRA1 is off")
                return
            if not self._reset_required_seen:
                self._latch_fault(FaultCode.UNEXPECTED_ARM_ORDER, now_ms, "SAFE_READY observed without prior RESET_REQUIRED")
                return
            self._invalidate_target()
            self._safe_ready_seen = True
            self._transition(OperatingState.SAFE_READY, now_ms, "SR1 ready; physical ARM still required")
            return

        if not self._safe_ready_seen:
            self._latch_fault(FaultCode.UNEXPECTED_ARM_ORDER, now_ms, "ARM observed without prior SAFE_READY")
            return

        if self.state is not OperatingState.DRIVE_ENABLED:
            self._transition(OperatingState.ARMED, now_ms, "hardware ARM and both contactors observed; torque remains off")

    def acknowledge_fault(self, now_ms: int, operator_acknowledged: bool) -> bool:
        snapshot = self._last_snapshot
        if self.state is not OperatingState.FAULT_LATCHED or not operator_acknowledged or snapshot is None:
            return False
        cause_absent = (
            snapshot.control_power
            and snapshot.estop_healthy
            and snapshot.edm_healthy
            and snapshot.bus_healthy
            and not snapshot.compute_undervoltage
            and not snapshot.sra1_armed
            and not snapshot.k1_feedback
            and not snapshot.k2_feedback
            and not snapshot.sr1_ready
        )
        if not cause_absent:
            self._record(now_ms, "FAULT_ACK_REJECTED", "cause absent/energy removed preconditions not met")
            return False
        self.fault = None
        self._safe_ready_seen = False
        self._reset_required_seen = True
        self._watchdog_ever_healthy = False
        self._invalidate_target()
        self._transition(OperatingState.RESET_REQUIRED, now_ms, "operator acknowledged local fault; hardware sequence still required")
        return True

    def accept_trajectory(self, command: TrajectoryCommand, now_ms: int) -> bool:
        rejection = self._trajectory_rejection(command, now_ms)
        if rejection is not None:
            self._record(now_ms, "COMMAND_REJECTED", rejection)
            return False
        self.last_sequence = command.sequence
        self.active_command = copy.deepcopy(command)
        self._transition(OperatingState.DRIVE_ENABLED, now_ms, f"accepted fresh trajectory {command.trajectory_id}")
        return True

    def tick(self, now_ms: int) -> None:
        if self.state is OperatingState.DRIVE_ENABLED and self.active_command is not None:
            command = self.active_command
            if now_ms > command.execution_deadline_ms:
                self._latch_fault(FaultCode.COMMAND_EXPIRED, now_ms, "trajectory execution deadline expired")

    def complete_trajectory(self, now_ms: int, success: bool, terminal_positions: Mapping[str, float]) -> bool:
        command = self.active_command
        if self.state is not OperatingState.DRIVE_ENABLED or command is None:
            return False
        if not success or not self._positions_match(
            terminal_positions, command.expected_terminal_positions, terminal=True
        ):
            self._latch_fault(FaultCode.EXECUTION_FAILED, now_ms, "trajectory failed or terminal state mismatched")
            return False
        self._invalidate_target()
        self._transition(OperatingState.ARMED, now_ms, "trajectory completed; torque request removed")
        return True

    def _trajectory_rejection(self, command: TrajectoryCommand, now_ms: int) -> str | None:
        snapshot = self._last_snapshot
        if self.state is not OperatingState.ARMED or snapshot is None:
            return "supervisor is not ARMED"
        if not self.config.selections_closed:
            return "configuration or kinematic model remains SELECTION REQUIRED"
        if not (snapshot.sra1_armed and snapshot.k1_feedback and snapshot.k2_feedback):
            return "hardware ARM/contactor observations are not all true"
        if command.configuration_hash != self.config.configuration_hash:
            return "configuration hash mismatch"
        if command.session_id != self.session_id:
            return "boot/session ID mismatch"
        if command.kinematic_model_hash != self.config.kinematic_model_hash:
            return "kinematic model hash mismatch"
        if command.sender_state != OperatingState.ARMED.value:
            return "sender state is not ARMED"
        if command.sequence <= self.last_sequence:
            return "duplicate or out-of-order sequence"
        if not command.trajectory_id:
            return "trajectory ID is empty"
        if command.source_time_ms > now_ms or now_ms > command.validity_deadline_ms:
            return "command timestamp is future or stale"
        if command.validity_deadline_ms - command.source_time_ms > self.config.maximum_command_age_ms:
            return "command validity window exceeds configured maximum"
        if set(command.starting_positions) != set(self.config.joints):
            return "starting-position axis set mismatch"
        if not self._positions_match(snapshot.positions, command.starting_positions):
            return "measured starting pose outside tolerance"
        if not command.samples:
            return "trajectory has no samples"
        if self.config.maximum_trajectory_samples is None or len(command.samples) > self.config.maximum_trajectory_samples:
            return "trajectory sample count exceeds the released bound"

        last_offset = -1
        expected_axes = set(self.config.joints)
        for sample in command.samples:
            if sample.offset_ms <= last_offset:
                return "sample times are not strictly increasing"
            last_offset = sample.offset_ms
            if set(sample.positions) != expected_axes or set(sample.velocities) != expected_axes:
                return "sample axis set mismatch"
            for axis, rule in self.config.joints.items():
                position = float(sample.positions[axis])
                velocity = abs(float(sample.velocities[axis]))
                if not rule.minimum <= position <= rule.maximum:
                    return f"{axis} position outside configured limit"
                if axis == "GRIPPER":
                    limit = self.config.setup_gripper_speed_mm_s if command.mode is MotionMode.SETUP else self.config.automatic_gripper_speed_mm_s
                else:
                    limit = self.config.setup_joint_speed_deg_s if command.mode is MotionMode.SETUP else self.config.automatic_joint_speed_deg_s
                if velocity > limit:
                    return f"{axis} velocity outside configured {command.mode.value} limit"

        if (
            self.config.maximum_trajectory_duration_ms is None
            or command.samples[-1].offset_ms > self.config.maximum_trajectory_duration_ms
        ):
            return "trajectory duration exceeds the released bound"

        tcp_speeds = list(self._kinematic_validator(command.samples))
        if len(tcp_speeds) != len(command.samples):
            return "kinematic validator returned wrong sample count"
        if any(speed < 0 or speed > self.config.maximum_tcp_speed_m_s for speed in tcp_speeds):
            return "computed TCP speed outside configured limit"
        if command.execution_deadline_ms < command.source_time_ms + command.samples[-1].offset_ms:
            return "execution deadline precedes the final trajectory sample"
        if (
            self.config.maximum_execution_slack_ms is None
            or command.execution_deadline_ms
            > command.source_time_ms
            + command.samples[-1].offset_ms
            + self.config.maximum_execution_slack_ms
        ):
            return "execution deadline slack exceeds the released bound"
        if set(command.expected_terminal_positions) != expected_axes:
            return "terminal-position axis set mismatch"
        if not self._positions_match(command.samples[-1].positions, command.expected_terminal_positions):
            return "last sample does not match expected terminal state"
        return None

    def _positions_match(
        self,
        measured: Mapping[str, float],
        expected: Mapping[str, float],
        *,
        terminal: bool = False,
    ) -> bool:
        if set(measured) != set(self.config.joints) or set(expected) != set(self.config.joints):
            return False
        return all(
            (rule.terminal_tolerance if terminal else rule.start_tolerance) is not None
            and abs(float(measured[axis]) - float(expected[axis]))
            <= float(rule.terminal_tolerance if terminal else rule.start_tolerance)
            for axis, rule in self.config.joints.items()
        )

    def _latch_fault(self, code: FaultCode, now_ms: int, detail: str) -> None:
        self.fault = code
        self._safe_ready_seen = False
        self._invalidate_target()
        self._transition(OperatingState.FAULT_LATCHED, now_ms, f"{code.value}: {detail}")

    def _invalidate_target(self) -> None:
        self.active_command = None

    def _transition(self, state: OperatingState, now_ms: int, detail: str) -> None:
        if self.state is state:
            return
        self.state = state
        self._record(now_ms, "STATE_TRANSITION", detail)

    def _record(self, now_ms: int, event: str, detail: str) -> None:
        self.events.append(EventRecord(now_ms, event, self.state, detail))
