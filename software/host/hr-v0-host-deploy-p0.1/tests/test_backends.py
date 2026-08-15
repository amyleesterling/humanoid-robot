from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[2]
SUPERVISOR = ROOT / "firmware/supervisor"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(SUPERVISOR))

from project_button_host.gpiod_hardware import (  # noqa: E402
    GpiodHardware,
    HardwareBackendError,
    HeartbeatScheduler,
    INPUT_NAMES,
)
from project_button_host.unix_command_source import CommandSourceError, parse_command  # noqa: E402


class FakeAccess:
    def __init__(self) -> None:
        self.outputs: list[bool] = []
        self.inputs = {name: False for name in INPUT_NAMES}
        self.closed = False

    def set_heartbeat(self, active: bool) -> None:
        self.outputs.append(bool(active))

    def read_inputs(self):
        return dict(self.inputs)

    def close(self) -> None:
        self.closed = True


def command_payload() -> bytes:
    return json.dumps(
        {
            "trajectory_id": "T-1",
            "session_id": "BOOT-1",
            "sequence": 1,
            "source_time_ms": 1000,
            "validity_deadline_ms": 1050,
            "execution_deadline_ms": 1300,
            "configuration_hash": "A" * 64,
            "kinematic_model_hash": "B" * 64,
            "sender_state": "ARMED",
            "mode": "AUTOMATIC",
            "starting_positions": {"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0},
            "samples": [
                {
                    "offset_ms": 0,
                    "positions": {"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0},
                    "velocities": {"J1": 0.0, "J2": 0.0, "GRIPPER": 0.0},
                },
                {
                    "offset_ms": 200,
                    "positions": {"J1": 5.0, "J2": 35.0, "GRIPPER": 42.0},
                    "velocities": {"J1": 25.0, "J2": 25.0, "GRIPPER": 10.0},
                },
            ],
            "expected_terminal_positions": {"J1": 5.0, "J2": 35.0, "GRIPPER": 42.0},
        },
        separators=(",", ":"),
    ).encode()


class BackendTests(unittest.TestCase):
    def test_heartbeat_toggles_only_at_released_edges(self) -> None:
        access = FakeAccess()
        scheduler = HeartbeatScheduler(access, half_period_ms=50, maximum_lateness_ms=5)
        scheduler.service(100, True)
        scheduler.service(149, True)
        scheduler.service(150, True)
        scheduler.service(200, True)
        self.assertEqual(access.outputs, [True, False, True])

    def test_heartbeat_lateness_forces_inactive(self) -> None:
        access = FakeAccess()
        scheduler = HeartbeatScheduler(access, half_period_ms=50, maximum_lateness_ms=5)
        scheduler.service(100, True)
        with self.assertRaisesRegex(HardwareBackendError, "lateness"):
            scheduler.service(156, True)
        self.assertFalse(access.outputs[-1])
        self.assertFalse(scheduler.enabled)

    def test_heartbeat_time_reversal_forces_inactive(self) -> None:
        access = FakeAccess()
        scheduler = HeartbeatScheduler(access, half_period_ms=50, maximum_lateness_ms=5)
        scheduler.service(100, True)
        with self.assertRaisesRegex(HardwareBackendError, "backwards"):
            scheduler.service(99, True)
        self.assertFalse(access.outputs[-1])

    def test_snapshot_applies_explicit_input_polarity(self) -> None:
        access = FakeAccess()
        access.inputs["sr1_status"] = False
        access.inputs["sra1_status"] = True
        access.inputs["k1_status"] = True
        active_high = {name: True for name in INPUT_NAMES}
        hardware = GpiodHardware(access, active_high, 50, 5)
        snapshot = hardware.snapshot({"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0})
        self.assertIsNone(snapshot.control_power)
        self.assertIsNone(snapshot.estop_healthy)
        self.assertIsNone(snapshot.watchdog_healthy)
        self.assertIsNone(snapshot.edm_healthy)
        self.assertIsNone(snapshot.compute_undervoltage)
        self.assertTrue(snapshot.bus_healthy)
        self.assertFalse(snapshot.sr1_ready)
        self.assertTrue(snapshot.sra1_armed)
        self.assertTrue(snapshot.k1_feedback)
        self.assertFalse(snapshot.k2_feedback)

    def test_snapshot_rejects_missing_input(self) -> None:
        access = FakeAccess()
        del access.inputs["k2_status"]
        hardware = GpiodHardware(access, {name: True for name in INPUT_NAMES}, 50, 5)
        with self.assertRaisesRegex(HardwareBackendError, "incomplete"):
            hardware.snapshot({"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0})

    def test_valid_command_parses_to_typed_model(self) -> None:
        command = parse_command(command_payload())
        self.assertEqual(command.trajectory_id, "T-1")
        self.assertEqual(len(command.samples), 2)
        self.assertEqual(command.mode.value, "AUTOMATIC")

    def test_command_rejects_extra_field(self) -> None:
        raw = json.loads(command_payload())
        raw["unexpected"] = True
        with self.assertRaisesRegex(CommandSourceError, "fields"):
            parse_command(json.dumps(raw).encode())

    def test_command_rejects_nonfinite_value(self) -> None:
        raw = json.loads(command_payload())
        raw["samples"][0]["positions"]["J1"] = float("nan")
        with self.assertRaises(CommandSourceError):
            parse_command(json.dumps(raw).encode())


if __name__ == "__main__":
    unittest.main()
