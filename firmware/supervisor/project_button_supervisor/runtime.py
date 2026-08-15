"""Fail-closed HR-V0 supervisor, heartbeat and actuator execution core.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

The runtime is dependency-injected: this module imports no GPIO, serial,
DYNAMIXEL SDK, network or command-transport backend.  It owns the sequencing
between received hardware observations, non-safety heartbeat permission,
supervisor authority and the torque-capable bus controller.  The committed
configuration cannot construct it because physical selections remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from .dynamixel_bus import BusError, DynamixelBusController
from .model import (
    HardwareSnapshot,
    OperatingState,
    Supervisor,
    TrajectoryCommand,
)


class RuntimeExecutionError(RuntimeError):
    """A process-boundary, scheduling, hardware or bus execution failure."""


class HardwareIO(Protocol):
    """Selected backend contract; implementations remain selection-required."""

    def snapshot(self, positions: Mapping[str, float]) -> HardwareSnapshot: ...
    def service_heartbeat(self, now_ms: int, allowed: bool) -> None: ...
    def disable_heartbeat(self) -> None: ...
    def close(self) -> None: ...


class CommandSource(Protocol):
    """Selected authenticated command-source contract."""

    def poll(self, now_ms: int) -> TrajectoryCommand | None: ...
    def close(self) -> None: ...


class EvidenceSink(Protocol):
    """Configuration-bound evidence channel; no safety integrity is claimed."""

    def record(self, monotonic_ms: int, event: str, payload: Mapping[str, object]) -> None: ...
    def close(self, monotonic_ms: int) -> None: ...


class RuntimeBus(Protocol):
    torque_enabled: bool

    def connect_and_configure(self) -> None: ...
    def read_positions_engineering(self, *, require_torque: bool) -> Mapping[str, float]: ...
    def start_trajectory(
        self, authority: object, trajectory_id: str, starting_positions: Mapping[str, float]
    ) -> None: ...
    def write_sample_engineering(
        self, authority: object, trajectory_id: str, positions: Mapping[str, float]
    ) -> Mapping[str, float]: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class RuntimeStatus:
    started: bool
    state: OperatingState
    heartbeat_allowed: bool
    torque_enable_request: bool
    bus_torque_enabled: bool
    active_trajectory_id: str | None
    next_sample_index: int


class RuntimeExecutive:
    """One-thread deterministic execution boundary with explicit shutdown."""

    def __init__(
        self,
        supervisor: Supervisor,
        bus: RuntimeBus,
        hardware: HardwareIO,
        commands: CommandSource,
        evidence: EvidenceSink,
    ) -> None:
        lateness = supervisor.config.maximum_sample_lateness_ms
        if lateness is None or lateness < 0:
            raise RuntimeExecutionError("maximum sample lateness remains SELECTION REQUIRED")
        self.supervisor = supervisor
        self.bus = bus
        self.hardware = hardware
        self.commands = commands
        self.evidence = evidence
        self.maximum_sample_lateness_ms = lateness
        self.started = False
        self._accepted_at_ms: int | None = None
        self._next_sample_index = 0
        self._next_supervisor_event_index = 0

    @property
    def status(self) -> RuntimeStatus:
        outputs = self.supervisor.outputs
        return RuntimeStatus(
            started=self.started,
            state=outputs.state,
            heartbeat_allowed=outputs.heartbeat_allowed,
            torque_enable_request=outputs.torque_enable_request,
            bus_torque_enabled=bool(self.bus.torque_enabled),
            active_trajectory_id=outputs.active_trajectory_id,
            next_sample_index=self._next_sample_index,
        )

    def start(self, now_ms: int) -> None:
        """Connect torque-off and configure the bus; never enable heartbeat here."""

        if self.started:
            raise RuntimeExecutionError("runtime is already started")
        self.evidence.record(now_ms, "RUNTIME_START_REQUEST", self._status_payload())
        self.hardware.disable_heartbeat()
        try:
            self.bus.connect_and_configure()
            self.started = True
            self.evidence.record(now_ms, "RUNTIME_STARTED", self._status_payload())
        except Exception as exc:
            self.started = False
            heartbeat_error: Exception | None = None
            try:
                self.hardware.disable_heartbeat()
            except Exception as heartbeat_exc:
                heartbeat_error = heartbeat_exc
            finally:
                try:
                    self.bus.close()
                finally:
                    detail = f"torque-off bus startup failed: {exc}"
                    if heartbeat_error is not None:
                        detail += f"; heartbeat removal also failed: {heartbeat_error}"
                    raise RuntimeExecutionError(detail) from exc

    def cycle(self, now_ms: int) -> RuntimeStatus:
        """Execute one bounded observation/authority/trajectory cycle."""

        if not self.started:
            raise RuntimeExecutionError("runtime is not started")
        try:
            self.evidence.record(now_ms, "CYCLE_BEGIN", self._status_payload())
            self.supervisor.tick(now_ms)
            self._flush_supervisor_events()
            self._synchronize_outputs(now_ms)
            if self.supervisor.state is OperatingState.FAULT_LATCHED:
                self.evidence.record(now_ms, "CYCLE_OUTPUT", self._status_payload())
                return self.status

            positions = self.bus.read_positions_engineering(
                require_torque=bool(self.bus.torque_enabled)
            )
            snapshot = self.hardware.snapshot(positions)
            self.evidence.record(
                now_ms,
                "FEEDBACK_SAMPLE",
                {
                    "positions": dict(snapshot.positions),
                    "control_power": snapshot.control_power,
                    "estop_healthy": snapshot.estop_healthy,
                    "watchdog_healthy": snapshot.watchdog_healthy,
                    "edm_healthy": snapshot.edm_healthy,
                    "bus_healthy": snapshot.bus_healthy,
                    "compute_undervoltage": snapshot.compute_undervoltage,
                    "sr1_ready": snapshot.sr1_ready,
                    "sra1_armed": snapshot.sra1_armed,
                    "k1_feedback": snapshot.k1_feedback,
                    "k2_feedback": snapshot.k2_feedback,
                },
            )
            self.supervisor.observe_hardware(snapshot, now_ms)
            self._flush_supervisor_events()
            self._synchronize_outputs(now_ms)
            if self.supervisor.state is OperatingState.FAULT_LATCHED:
                self.evidence.record(now_ms, "CYCLE_OUTPUT", self._status_payload())
                return self.status

            if (
                self.supervisor.active_command is None
                and self.supervisor.state is OperatingState.ARMED
            ):
                command = self.commands.poll(now_ms)
                if command is not None:
                    self.evidence.record(
                        now_ms,
                        "COMMAND_RECEIVED",
                        {
                            "trajectory_id": command.trajectory_id,
                            "session_id": command.session_id,
                            "sequence": command.sequence,
                            "source_time_ms": command.source_time_ms,
                            "validity_deadline_ms": command.validity_deadline_ms,
                            "execution_deadline_ms": command.execution_deadline_ms,
                            "configuration_hash": command.configuration_hash,
                            "kinematic_model_hash": command.kinematic_model_hash,
                            "sender_state": command.sender_state,
                            "mode": command.mode.value,
                            "sample_count": len(command.samples),
                            "starting_positions": dict(command.starting_positions),
                            "expected_terminal_positions": dict(command.expected_terminal_positions),
                        },
                    )
                    accepted = self.supervisor.accept_trajectory(command, now_ms)
                    self._flush_supervisor_events()
                    self.evidence.record(
                        now_ms,
                        "COMMAND_DECISION",
                        {
                            "trajectory_id": command.trajectory_id,
                            "sequence": command.sequence,
                            "accepted": accepted,
                            "state": self.supervisor.state.value,
                            "fault": self.supervisor.fault.value if self.supervisor.fault else None,
                        },
                    )
                else:
                    accepted = False
                if command is not None and accepted:
                    self.bus.start_trajectory(
                        self.supervisor.outputs,
                        command.trajectory_id,
                        command.starting_positions,
                    )
                    self._accepted_at_ms = now_ms
                    self._next_sample_index = 0

            if self.supervisor.active_command is not None:
                self._execute_active(now_ms)
            self._synchronize_outputs(now_ms)
            self.evidence.record(now_ms, "CYCLE_OUTPUT", self._status_payload())
            return self.status
        except RuntimeExecutionError:
            self._fail_active(now_ms)
            raise
        except Exception as exc:
            self._fail_active(now_ms)
            raise RuntimeExecutionError(f"runtime cycle failed closed: {exc}") from exc

    def shutdown(self, now_ms: int) -> None:
        """Remove the ordinary heartbeat request before torque and resources."""

        errors: list[str] = []
        try:
            self.evidence.record(now_ms, "RUNTIME_SHUTDOWN_REQUEST", self._status_payload())
        except Exception as exc:
            errors.append(f"evidence-start: {exc}")
        try:
            self.hardware.disable_heartbeat()
        except Exception as exc:
            errors.append(f"heartbeat: {exc}")
        finally:
            try:
                self.bus.close()
            except Exception as exc:
                errors.append(f"bus: {exc}")
            finally:
                try:
                    self.commands.close()
                except Exception as exc:
                    errors.append(f"commands: {exc}")
                finally:
                    try:
                        self.hardware.close()
                    except Exception as exc:
                        errors.append(f"hardware: {exc}")
                    finally:
                        self.started = False
                        self._accepted_at_ms = None
                        self._next_sample_index = 0
        try:
            self.evidence.record(now_ms, "RUNTIME_STOPPED", self._status_payload())
        except Exception as exc:
            errors.append(f"evidence-stop: {exc}")
        try:
            self.evidence.close(now_ms)
        except Exception as exc:
            errors.append(f"evidence-close: {exc}")
        if errors:
            raise RuntimeExecutionError("shutdown attempted every output; failures: " + "; ".join(errors))

    def _execute_active(self, now_ms: int) -> None:
        command = self.supervisor.active_command
        accepted_at = self._accepted_at_ms
        if command is None or accepted_at is None:
            raise RuntimeExecutionError("active command has no runtime schedule")
        if not self.bus.torque_enabled or not self.supervisor.outputs.torque_enable_request:
            raise RuntimeExecutionError("active trajectory lost torque authority")

        if self._next_sample_index < len(command.samples):
            sample = command.samples[self._next_sample_index]
            sample_index = self._next_sample_index
            due_ms = accepted_at + sample.offset_ms
            if now_ms > due_ms + self.maximum_sample_lateness_ms:
                raise RuntimeExecutionError(
                    f"sample {self._next_sample_index} missed its released lateness bound"
                )
            if now_ms < due_ms:
                return
            received = self.bus.write_sample_engineering(
                self.supervisor.outputs, command.trajectory_id, sample.positions
            )
            self._next_sample_index += 1
            terminal_reassert = False
        else:
            # Re-send the terminal target so the actuator bus watchdog remains
            # serviced while terminal-position evidence is collected.
            received = self.bus.write_sample_engineering(
                self.supervisor.outputs,
                command.trajectory_id,
                command.expected_terminal_positions,
            )
            sample_index = len(command.samples)
            due_ms = accepted_at + command.samples[-1].offset_ms
            sample = command.samples[-1]
            terminal_reassert = True

        self.evidence.record(
            now_ms,
            "COMMAND_SAMPLE",
            {
                "trajectory_id": command.trajectory_id,
                "sample_index": sample_index,
                "due_ms": due_ms,
                "terminal_reassert": terminal_reassert,
                "commanded_positions": dict(
                    command.expected_terminal_positions if terminal_reassert else sample.positions
                ),
                "measured_positions": dict(received),
            },
        )

        if self._next_sample_index == len(command.samples) and self._terminal_matches(
            received, command.expected_terminal_positions
        ):
            if not self.supervisor.complete_trajectory(
                now_ms, True, received
            ):
                raise RuntimeExecutionError("terminal completion was not accepted")
            self._flush_supervisor_events()
            self.bus.stop()
            self._accepted_at_ms = None
            self._next_sample_index = 0

    def _terminal_matches(
        self, measured: Mapping[str, float], expected: Mapping[str, float]
    ) -> bool:
        if set(measured) != set(expected) or set(measured) != set(self.supervisor.config.joints):
            return False
        return all(
            rule.terminal_tolerance is not None
            and abs(float(measured[axis]) - float(expected[axis])) <= rule.terminal_tolerance
            for axis, rule in self.supervisor.config.joints.items()
        )

    def _synchronize_outputs(self, now_ms: int) -> None:
        outputs = self.supervisor.outputs
        try:
            self.hardware.service_heartbeat(now_ms, outputs.heartbeat_allowed)
        finally:
            if not outputs.torque_enable_request and self.bus.torque_enabled:
                self.bus.stop()

    def _status_payload(self) -> dict[str, object]:
        status = self.status
        return {
            "started": status.started,
            "state": status.state.value,
            "heartbeat_allowed": status.heartbeat_allowed,
            "torque_enable_request": status.torque_enable_request,
            "bus_torque_enabled": status.bus_torque_enabled,
            "active_trajectory_id": status.active_trajectory_id,
            "next_sample_index": status.next_sample_index,
            "fault": self.supervisor.fault.value if self.supervisor.fault is not None else None,
        }

    def _flush_supervisor_events(self) -> None:
        while self._next_supervisor_event_index < len(self.supervisor.events):
            event = self.supervisor.events[self._next_supervisor_event_index]
            self.evidence.record(
                event.monotonic_ms,
                "SUPERVISOR_EVENT",
                {
                    "supervisor_event": event.event,
                    "state": event.state.value,
                    "detail": event.detail,
                },
            )
            self._next_supervisor_event_index += 1

    def _fail_active(self, now_ms: int) -> None:
        heartbeat_error: Exception | None = None
        try:
            self.hardware.disable_heartbeat()
        except Exception as exc:
            heartbeat_error = exc
        finally:
            try:
                self.bus.stop()
            finally:
                if self.supervisor.active_command is not None:
                    self.supervisor.complete_trajectory(now_ms, False, {})
                self._accepted_at_ms = None
                self._next_sample_index = 0
        try:
            self.evidence.record(now_ms, "RUNTIME_FAIL_CLOSED", self._status_payload())
        except Exception:
            # The original evidence failure remains the reported cause; torque
            # and heartbeat removal above are attempted independently of it.
            pass
        if heartbeat_error is not None:
            raise RuntimeExecutionError(
                f"heartbeat removal failed while bus stop was still attempted: {heartbeat_error}"
            ) from heartbeat_error


__all__ = [
    "CommandSource",
    "EvidenceSink",
    "HardwareIO",
    "RuntimeBus",
    "RuntimeExecutionError",
    "RuntimeExecutive",
    "RuntimeStatus",
]
