from __future__ import annotations

import sys
import unittest
from pathlib import Path


SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor import (  # noqa: E402
    HardwareSnapshot,
    OperatingState,
    RuntimeExecutionError,
    RuntimeExecutive,
    Supervisor,
    SupervisorConfig,
)
from test_supervisor import START, command, config  # noqa: E402


class FakeBus:
    def __init__(self) -> None:
        self.torque_enabled = False
        self.positions = dict(START)
        self.log: list[tuple[object, ...]] = []

    def connect_and_configure(self) -> None:
        self.log.append(("connect",))

    def read_positions_engineering(self, *, require_torque: bool):
        self.log.append(("read", require_torque))
        return dict(self.positions)

    def start_trajectory(self, authority, trajectory_id, starting_positions) -> None:
        if not authority.torque_enable_request or authority.active_trajectory_id != trajectory_id:
            raise RuntimeError("authority absent")
        self.torque_enabled = True
        self.log.append(("start", trajectory_id, dict(starting_positions)))

    def write_sample_engineering(self, authority, trajectory_id, positions):
        if not self.torque_enabled or not authority.torque_enable_request:
            raise RuntimeError("torque authority absent")
        self.positions = dict(positions)
        self.log.append(("write", trajectory_id, dict(positions)))
        return dict(self.positions)

    def stop(self) -> None:
        self.torque_enabled = False
        self.log.append(("stop",))

    def close(self) -> None:
        self.torque_enabled = False
        self.log.append(("close",))


class FakeHardware:
    def __init__(self) -> None:
        self.estop_healthy = True
        self.sr1_ready = False
        self.sra1_armed = False
        self.k1_feedback = False
        self.k2_feedback = False
        self.heartbeat: list[bool] = []
        self.heartbeat_service: list[tuple[int, bool]] = []
        self.closed = False
        self.fail_heartbeat = False

    def snapshot(self, positions):
        return HardwareSnapshot(
            control_power=True,
            estop_healthy=self.estop_healthy,
            watchdog_healthy=True,
            edm_healthy=True,
            bus_healthy=True,
            compute_undervoltage=False,
            sr1_ready=self.sr1_ready,
            sra1_armed=self.sra1_armed,
            k1_feedback=self.k1_feedback,
            k2_feedback=self.k2_feedback,
            positions=dict(positions),
        )

    def service_heartbeat(self, now_ms: int, allowed: bool) -> None:
        self.heartbeat_service.append((now_ms, bool(allowed)))
        self.heartbeat.append(bool(allowed))
        if self.fail_heartbeat:
            raise RuntimeError("injected heartbeat driver failure")

    def disable_heartbeat(self) -> None:
        self.heartbeat.append(False)
        if self.fail_heartbeat:
            raise RuntimeError("injected heartbeat driver failure")

    def close(self) -> None:
        self.closed = True


class FakeCommands:
    def __init__(self) -> None:
        self.queue = []
        self.closed = False

    def poll(self, now_ms: int):
        return self.queue.pop(0) if self.queue else None

    def close(self) -> None:
        self.closed = True


class FakeEvidence:
    def __init__(self) -> None:
        self.records: list[tuple[int, str, dict[str, object]]] = []
        self.closed = False
        self.fail = False

    def record(self, monotonic_ms: int, event: str, payload) -> None:
        if self.fail:
            raise RuntimeError("injected evidence failure")
        self.records.append((monotonic_ms, event, dict(payload)))

    def close(self, monotonic_ms: int) -> None:
        if self.fail:
            raise RuntimeError("injected evidence failure")
        self.closed = True


def runtime() -> tuple[RuntimeExecutive, FakeBus, FakeHardware, FakeCommands, FakeEvidence]:
    bus = FakeBus()
    hardware = FakeHardware()
    commands = FakeCommands()
    evidence = FakeEvidence()
    supervisor = Supervisor(config(), lambda samples: [0.0 for _ in samples], "SESSION-TEST")
    return RuntimeExecutive(supervisor, bus, hardware, commands, evidence), bus, hardware, commands, evidence


def arm(executive: RuntimeExecutive, hardware: FakeHardware) -> None:
    executive.cycle(0)
    hardware.sr1_ready = True
    executive.cycle(10)
    hardware.sra1_armed = True
    hardware.k1_feedback = True
    hardware.k2_feedback = True
    executive.cycle(20)


class RuntimeTests(unittest.TestCase):
    def test_repository_lateness_selection_refuses_runtime_construction(self) -> None:
        candidate = SupervisorConfig.from_json(SUPERVISOR_ROOT / "supervisor-config.json")
        supervisor = Supervisor(candidate, lambda samples: [0.0 for _ in samples], "test")
        with self.assertRaisesRegex(RuntimeExecutionError, "SELECTION REQUIRED"):
            RuntimeExecutive(supervisor, FakeBus(), FakeHardware(), FakeCommands(), FakeEvidence())

    def test_start_connects_torque_off_with_heartbeat_disallowed(self) -> None:
        executive, bus, hardware, _, evidence = runtime()
        executive.start(0)
        self.assertEqual(bus.log[0], ("connect",))
        self.assertEqual(hardware.heartbeat[0], False)
        self.assertFalse(bus.torque_enabled)
        self.assertEqual(evidence.records[-1][1], "RUNTIME_STARTED")

    def test_reset_and_arm_without_command_never_enable_torque(self) -> None:
        executive, bus, hardware, _, _ = runtime()
        executive.start(0)
        arm(executive, hardware)
        self.assertEqual(executive.status.state, OperatingState.ARMED)
        self.assertFalse(executive.status.torque_enable_request)
        self.assertFalse(bus.torque_enabled)
        self.assertFalse(any(entry[0] == "start" for entry in bus.log))

    def test_fresh_command_executes_ordered_samples_then_removes_torque(self) -> None:
        executive, bus, hardware, commands, evidence = runtime()
        executive.start(0)
        executive.cycle(0)
        hardware.sr1_ready = True
        executive.cycle(10)
        hardware.sra1_armed = hardware.k1_feedback = hardware.k2_feedback = True
        commands.queue.append(command(sequence=1, now_ms=20))
        status = executive.cycle(20)
        self.assertEqual(status.state, OperatingState.DRIVE_ENABLED)
        self.assertTrue(bus.torque_enabled)
        status = executive.cycle(220)
        self.assertEqual(status.state, OperatingState.ARMED)
        self.assertFalse(bus.torque_enabled)
        writes = [entry for entry in bus.log if entry[0] == "write"]
        self.assertEqual([entry[2] for entry in writes], [dict(command(now_ms=20).samples[0].positions), dict(command(now_ms=20).samples[1].positions)])
        self.assertIn("FEEDBACK_SAMPLE", [record[1] for record in evidence.records])
        self.assertEqual(evidence.records[-1][1], "CYCLE_OUTPUT")

    def test_hardware_dropout_removes_heartbeat_and_bus_torque(self) -> None:
        executive, bus, hardware, commands, _ = runtime()
        executive.start(0)
        executive.cycle(0)
        hardware.sr1_ready = True
        executive.cycle(10)
        hardware.sra1_armed = hardware.k1_feedback = hardware.k2_feedback = True
        commands.queue.append(command(sequence=1, now_ms=20))
        executive.cycle(20)
        hardware.estop_healthy = False
        status = executive.cycle(30)
        self.assertEqual(status.state, OperatingState.FAULT_LATCHED)
        self.assertFalse(status.heartbeat_allowed)
        self.assertFalse(bus.torque_enabled)
        self.assertEqual(hardware.heartbeat[-1], False)

    def test_missed_sample_lateness_fails_active_trajectory_closed(self) -> None:
        executive, bus, hardware, commands, _ = runtime()
        executive.start(0)
        executive.cycle(0)
        hardware.sr1_ready = True
        executive.cycle(10)
        hardware.sra1_armed = hardware.k1_feedback = hardware.k2_feedback = True
        commands.queue.append(command(sequence=1, now_ms=20))
        executive.cycle(20)
        with self.assertRaisesRegex(RuntimeExecutionError, "lateness bound"):
            executive.cycle(231)
        self.assertEqual(executive.status.state, OperatingState.FAULT_LATCHED)
        self.assertFalse(bus.torque_enabled)
        self.assertEqual(hardware.heartbeat[-1], False)

    def test_shutdown_removes_heartbeat_before_closing_resources(self) -> None:
        executive, bus, hardware, commands, evidence = runtime()
        executive.start(0)
        executive.shutdown(10)
        self.assertEqual(hardware.heartbeat[-1], False)
        self.assertIn(("close",), bus.log)
        self.assertTrue(hardware.closed)
        self.assertTrue(commands.closed)
        self.assertFalse(executive.started)
        self.assertTrue(evidence.closed)

    def test_shutdown_attempts_every_cleanup_after_heartbeat_failure(self) -> None:
        executive, bus, hardware, commands, _ = runtime()
        executive.start(0)
        hardware.fail_heartbeat = True
        with self.assertRaisesRegex(RuntimeExecutionError, "attempted every output"):
            executive.shutdown(10)
        self.assertIn(("close",), bus.log)
        self.assertTrue(hardware.closed)
        self.assertTrue(commands.closed)
        self.assertFalse(executive.started)

    def test_heartbeat_failure_cannot_skip_bus_stop(self) -> None:
        executive, bus, hardware, commands, _ = runtime()
        executive.start(0)
        executive.cycle(0)
        hardware.sr1_ready = True
        executive.cycle(10)
        hardware.sra1_armed = hardware.k1_feedback = hardware.k2_feedback = True
        commands.queue.append(command(sequence=1, now_ms=20))
        executive.cycle(20)
        hardware.fail_heartbeat = True
        hardware.estop_healthy = False
        with self.assertRaises(RuntimeExecutionError):
            executive.cycle(30)
        self.assertFalse(bus.torque_enabled)
        self.assertIn(("stop",), bus.log)

    def test_evidence_failure_during_motion_fails_closed(self) -> None:
        executive, bus, hardware, commands, evidence = runtime()
        executive.start(0)
        executive.cycle(0)
        hardware.sr1_ready = True
        executive.cycle(10)
        hardware.sra1_armed = hardware.k1_feedback = hardware.k2_feedback = True
        commands.queue.append(command(sequence=1, now_ms=20))
        executive.cycle(20)
        self.assertTrue(bus.torque_enabled)
        evidence.fail = True
        with self.assertRaisesRegex(RuntimeExecutionError, "evidence failure"):
            executive.cycle(30)
        self.assertFalse(bus.torque_enabled)
        self.assertEqual(hardware.heartbeat[-1], False)


if __name__ == "__main__":
    unittest.main()
