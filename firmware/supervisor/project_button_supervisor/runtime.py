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
    def set_heartbeat_allowed(self, allowed: bool) -> None: ...
    def close(self) -> None: ...


class CommandSource(Protocol):
    """Selected authenticated command-source contract."""

    def poll(self, now_ms: int) -> TrajectoryCommand | None: ...
    def close(self) -> None: ...


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
    ) -> None:
        lateness = supervisor.config.maximum_sample_lateness_ms
        if lateness is None or lateness < 0:
            raise RuntimeExecutionError("maximum sample lateness remains SELECTION REQUIRED")
        self.supervisor = supervisor
        self.bus = bus
        self.hardware = hardware
        self.commands = commands
        self.maximum_sample_lateness_ms = lateness
        self.started = False
        self._accepted_at_ms: int | None = None
        self._next_sample_index = 0

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

    def start(self) -> None:
        """Connect torque-off and configure the bus; never enable heartbeat here."""

        if self.started:
            raise RuntimeExecutionError("runtime is already started")
        self.hardware.set_heartbeat_allowed(False)
        try:
            self.bus.connect_and_configure()
        except Exception as exc:
            heartbeat_error: Exception | None = None
            try:
                self.hardware.set_heartbeat_allowed(False)
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
        self.started = True

    def cycle(self, now_ms: int) -> RuntimeStatus:
        """Execute one bounded observation/authority/trajectory cycle."""

        if not self.started:
            raise RuntimeExecutionError("runtime is not started")
        try:
            self.supervisor.tick(now_ms)
            self._synchronize_outputs()
            if self.supervisor.state is OperatingState.FAULT_LATCHED:
                return self.status

            positions = self.bus.read_positions_engineering(
                require_torque=bool(self.bus.torque_enabled)
            )
            snapshot = self.hardware.snapshot(positions)
            self.supervisor.observe_hardware(snapshot, now_ms)
            self._synchronize_outputs()
            if self.supervisor.state is OperatingState.FAULT_LATCHED:
                return self.status

            if (
                self.supervisor.active_command is None
                and self.supervisor.state is OperatingState.ARMED
            ):
                command = self.commands.poll(now_ms)
                if command is not None and self.supervisor.accept_trajectory(command, now_ms):
                    self.bus.start_trajectory(
                        self.supervisor.outputs,
                        command.trajectory_id,
                        command.starting_positions,
                    )
                    self._accepted_at_ms = now_ms
                    self._next_sample_index = 0

            if self.supervisor.active_command is not None:
                self._execute_active(now_ms)
            self._synchronize_outputs()
            return self.status
        except RuntimeExecutionError:
            self._fail_active(now_ms)
            raise
        except Exception as exc:
            self._fail_active(now_ms)
            raise RuntimeExecutionError(f"runtime cycle failed closed: {exc}") from exc

    def shutdown(self) -> None:
        """Remove the ordinary heartbeat request before torque and resources."""

        errors: list[str] = []
        try:
            self.hardware.set_heartbeat_allowed(False)
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
        else:
            # Re-send the terminal target so the actuator bus watchdog remains
            # serviced while terminal-position evidence is collected.
            received = self.bus.write_sample_engineering(
                self.supervisor.outputs,
                command.trajectory_id,
                command.expected_terminal_positions,
            )

        if self._next_sample_index == len(command.samples) and self._terminal_matches(
            received, command.expected_terminal_positions
        ):
            if not self.supervisor.complete_trajectory(
                now_ms, True, received
            ):
                raise RuntimeExecutionError("terminal completion was not accepted")
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

    def _synchronize_outputs(self) -> None:
        outputs = self.supervisor.outputs
        try:
            self.hardware.set_heartbeat_allowed(outputs.heartbeat_allowed)
        finally:
            if not outputs.torque_enable_request and self.bus.torque_enabled:
                self.bus.stop()

    def _fail_active(self, now_ms: int) -> None:
        heartbeat_error: Exception | None = None
        try:
            self.hardware.set_heartbeat_allowed(False)
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
        if heartbeat_error is not None:
            raise RuntimeExecutionError(
                f"heartbeat removal failed while bus stop was still attempted: {heartbeat_error}"
            ) from heartbeat_error


__all__ = [
    "CommandSource",
    "HardwareIO",
    "RuntimeBus",
    "RuntimeExecutionError",
    "RuntimeExecutive",
    "RuntimeStatus",
]
