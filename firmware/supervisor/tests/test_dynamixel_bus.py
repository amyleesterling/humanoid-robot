from __future__ import annotations

import json
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor import ActuatorConfiguration, BusError, DynamixelBusController  # noqa: E402
from project_button_supervisor.dynamixel_bus import (  # noqa: E402
    BUS_WATCHDOG,
    CURRENT_LIMIT,
    DRIVE_MODE,
    FIRMWARE_VERSION,
    GOAL_CURRENT,
    GOAL_POSITION,
    HARDWARE_ERROR_STATUS,
    MODEL_NUMBER,
    OPERATING_MODE,
    PRESENT_CURRENT,
    PRESENT_INPUT_VOLTAGE,
    PRESENT_POSITION,
    PRESENT_TEMPERATURE,
    PRESENT_VELOCITY,
    PROFILE_ACCELERATION,
    PROFILE_VELOCITY,
    STARTUP_CONFIGURATION,
    TORQUE_ENABLE,
)
from project_button_supervisor.sdk_transport import _decoded, _encoded  # noqa: E402


CONFIG_PATH = ROOT / "firmware" / "supervisor" / "actuator-config.json"


def frozen_config() -> ActuatorConfiguration:
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["external_branch_current_limit_a"] = 2.4
    raw["transport"]["device"] = "TEST-ONLY"
    raw["mechanical_limit_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
    raw["mechanical_limit_binding"]["acceptance_evidence_hash"] = "C" * 64
    raw["current_envelope_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
    raw["current_envelope_binding"]["acceptance_evidence_hash"] = "D" * 64
    for joint, item in raw["actuators"].items():
        item["model_number"] = 1130 if item["model"].startswith("XM540") else 1020
        item["firmware_version"] = 46
        item["profile_velocity_raw_candidate"] = 20
        item["profile_acceleration_raw_candidate"] = 5
        if joint == "GRIPPER":
            item.update(
                position_zero_raw=1000,
                position_zero_engineering=20.0,
                raw_per_unit=10.0,
                direction=1,
                minimum_raw=1000,
                maximum_raw=1550,
                start_tolerance_raw=10,
                minimum_input_voltage_raw=100,
                maximum_input_voltage_raw=140,
                maximum_temperature_c=60,
            )
        else:
            item.update(
                position_zero_raw=2048,
                position_zero_engineering=0.0,
                raw_per_unit=4096.0 / 360.0,
                direction=1,
                minimum_raw=0,
                maximum_raw=4095,
                start_tolerance_raw=12,
                minimum_input_voltage_raw=100,
                maximum_input_voltage_raw=140,
                maximum_temperature_c=65,
            )
    return ActuatorConfiguration(raw)


@dataclass(frozen=True)
class Authority:
    torque_enable_request: bool
    active_trajectory_id: str | None


class FakeTransport:
    def __init__(self, config: ActuatorConfiguration) -> None:
        self.config = config
        self.opened = False
        self.closed = False
        self.log: list[tuple[object, ...]] = []
        self.fail_sync_address: int | None = None
        self.discovered = {
            rule.actuator_id: int(rule.model_number) for rule in config.rules.values()
        }
        self.registers: dict[tuple[int, int], int] = {}
        for rule in config.rules.values():
            actuator_id = rule.actuator_id
            values = {
                MODEL_NUMBER.address: int(rule.model_number),
                FIRMWARE_VERSION.address: int(rule.firmware_version),
                7: actuator_id,
                DRIVE_MODE.address: 1,
                OPERATING_MODE.address: 3,
                CURRENT_LIMIT.address: 2047,
                STARTUP_CONFIGURATION.address: 1,
                TORQUE_ENABLE.address: 1,
                HARDWARE_ERROR_STATUS.address: 0,
                BUS_WATCHDOG.address: -1,
                GOAL_CURRENT.address: 0,
                PROFILE_ACCELERATION.address: 0,
                PROFILE_VELOCITY.address: 0,
                PRESENT_CURRENT.address: 0,
                PRESENT_VELOCITY.address: 0,
                PRESENT_POSITION.address: 0,
                PRESENT_INPUT_VOLTAGE.address: 120,
                PRESENT_TEMPERATURE.address: 25,
            }
            for address, value in values.items():
                self.registers[(actuator_id, address)] = value

    def open(self) -> None:
        self.opened = True
        self.log.append(("open",))

    def close(self) -> None:
        self.closed = True
        self.opened = False
        self.log.append(("close",))

    def discover(self):
        self.log.append(("discover",))
        return dict(self.discovered)

    def read(self, actuator_id, address, size, *, signed=False):
        self.log.append(("read", actuator_id, address, size, signed))
        return self.registers[(actuator_id, address)]

    def write(self, actuator_id, address, size, value, *, signed=False):
        self.log.append(("write", actuator_id, address, size, value, signed))
        self.registers[(actuator_id, address)] = value

    def sync_write(self, address, size, values, *, signed=False):
        self.log.append(("sync", address, size, dict(values), signed))
        if self.fail_sync_address == address:
            raise BusError("injected synchronous-write failure")
        for actuator_id, value in values.items():
            self.registers[(actuator_id, address)] = value


START = {"J1": 0.0, "J2": 30.0, "GRIPPER": 40.0}


def connected() -> tuple[ActuatorConfiguration, FakeTransport, DynamixelBusController]:
    config = frozen_config()
    transport = FakeTransport(config)
    controller = DynamixelBusController(transport, config)
    controller.connect_and_configure()
    for joint, position in START.items():
        rule = config.rules[joint]
        transport.registers[(rule.actuator_id, PRESENT_POSITION.address)] = config.engineering_to_raw(joint, position)
    return config, transport, controller


class DynamixelBusTests(unittest.TestCase):
    def test_repository_config_refuses_to_open_transport(self):
        config = ActuatorConfiguration.from_json(CONFIG_PATH)
        transport = FakeTransport(frozen_config())
        controller = DynamixelBusController(transport, config)
        with self.assertRaisesRegex(BusError, "serial port will not be opened"):
            controller.connect_and_configure()
        self.assertFalse(transport.opened)
        self.assertEqual([], transport.log)

    def test_configuration_forces_torque_off_before_discovery_and_reads_back(self):
        config, transport, controller = connected()
        discover_index = transport.log.index(("discover",))
        prior = transport.log[:discover_index]
        torque_off_ids = {
            entry[1] for entry in prior if entry[:3:2] == ("write", TORQUE_ENABLE.address) and entry[4] == 0
        }
        self.assertEqual(set(controller.joint_by_id), torque_off_ids)
        self.assertTrue(controller.is_configured)
        for rule in config.rules.values():
            actuator_id = rule.actuator_id
            self.assertEqual(0, transport.registers[(actuator_id, TORQUE_ENABLE.address)])
            self.assertEqual(0, transport.registers[(actuator_id, DRIVE_MODE.address)])
            self.assertEqual(5, transport.registers[(actuator_id, OPERATING_MODE.address)])
            self.assertEqual(rule.current_limit_raw, transport.registers[(actuator_id, CURRENT_LIMIT.address)])
            self.assertEqual(0, transport.registers[(actuator_id, BUS_WATCHDOG.address)])

    def test_unexpected_discovered_id_is_torqued_off_then_session_closes(self):
        config = frozen_config()
        transport = FakeTransport(config)
        transport.discovered[9] = 9999
        transport.registers[(9, TORQUE_ENABLE.address)] = 1
        controller = DynamixelBusController(transport, config)
        with self.assertRaisesRegex(BusError, "do not exactly match"):
            controller.connect_and_configure()
        self.assertEqual(0, transport.registers[(9, TORQUE_ENABLE.address)])
        self.assertTrue(transport.closed)

    def test_model_substitution_is_rejected_and_session_closes(self):
        config = frozen_config()
        transport = FakeTransport(config)
        actuator_id = config.rules["J1"].actuator_id
        transport.discovered[actuator_id] = 9999
        controller = DynamixelBusController(transport, config)
        with self.assertRaisesRegex(BusError, "broadcast identity mismatch"):
            controller.connect_and_configure()
        self.assertTrue(transport.closed)
        for rule in config.rules.values():
            self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_motion_authority_is_required_before_any_torque_enable(self):
        _, transport, controller = connected()
        with self.assertRaisesRegex(BusError, "motion authority"):
            controller.start_trajectory(Authority(False, None), "T1", START)
        self.assertFalse(controller.torque_enabled)
        self.assertFalse(any(entry[0] == "sync" and entry[1] == TORQUE_ENABLE.address and 1 in entry[3].values() for entry in transport.log))

    def test_start_sequence_sets_targets_and_watchdog_before_torque_enable(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        self.assertTrue(controller.torque_enabled)
        torque_on_index = next(
            index for index, entry in enumerate(transport.log)
            if entry[0] == "sync" and entry[1] == TORQUE_ENABLE.address and set(entry[3].values()) == {1}
        )
        goal_index = next(index for index, entry in enumerate(transport.log) if entry[0] == "sync" and entry[1] == GOAL_POSITION.address)
        watchdog_indices = [
            index for index, entry in enumerate(transport.log)
            if entry[0] == "write" and entry[2] == BUS_WATCHDOG.address and entry[4] == config.bus_watchdog_raw_candidate
        ]
        self.assertLess(goal_index, torque_on_index)
        self.assertTrue(watchdog_indices)
        self.assertTrue(all(index < torque_on_index for index in watchdog_indices))

    def test_authority_loss_before_sample_forces_torque_off(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        with self.assertRaisesRegex(BusError, "authority missing"):
            controller.write_sample(Authority(False, None), "T1", START)
        self.assertFalse(controller.torque_enabled)
        for rule in config.rules.values():
            self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_watchdog_expiry_during_sample_forces_torque_off(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        transport.registers[(config.rules["J1"].actuator_id, BUS_WATCHDOG.address)] = -1
        with self.assertRaisesRegex(BusError, "watchdog expired"):
            controller.write_sample(Authority(True, "T1"), "T1", START)
        self.assertFalse(controller.torque_enabled)

    def test_each_telemetry_envelope_fault_forces_torque_off(self):
        cases = (
            (HARDWARE_ERROR_STATUS.address, 1, "hardware error status"),
            (CURRENT_LIMIT.address, 801, "configured-current-limit"),
            (GOAL_CURRENT.address, 799, "goal-current"),
            (PRESENT_CURRENT.address, 801, "present-current"),
            (PRESENT_INPUT_VOLTAGE.address, 99, "input-voltage"),
            (PRESENT_TEMPERATURE.address, 66, "temperature"),
        )
        for address, value, message in cases:
            with self.subTest(address=address):
                config, transport, controller = connected()
                controller.start_trajectory(Authority(True, "T1"), "T1", START)
                actuator_id = config.rules["J1"].actuator_id
                transport.registers[(actuator_id, address)] = value
                with self.assertRaisesRegex(BusError, message):
                    controller.write_sample(Authority(True, "T1"), "T1", START)
                self.assertFalse(controller.torque_enabled)
                for rule in config.rules.values():
                    self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_direct_poll_current_bound_drift_forces_torque_off(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        actuator_id = config.rules["J1"].actuator_id
        transport.registers[(actuator_id, GOAL_CURRENT.address)] = 799
        with self.assertRaisesRegex(BusError, "goal-current"):
            controller.poll_telemetry(require_torque=True)
        self.assertFalse(controller.torque_enabled)
        self.assertIsNone(controller.active_trajectory_id)
        for rule in config.rules.values():
            self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_synchronous_write_failure_forces_torque_off(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        transport.fail_sync_address = GOAL_POSITION.address
        with self.assertRaisesRegex(BusError, "synchronous-write failure"):
            controller.write_sample(Authority(True, "T1"), "T1", START)
        for rule in config.rules.values():
            self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_close_forces_torque_off_and_closes_port(self):
        config, transport, controller = connected()
        controller.start_trajectory(Authority(True, "T1"), "T1", START)
        controller.close()
        self.assertFalse(controller.torque_enabled)
        self.assertFalse(controller.is_open)
        self.assertFalse(controller.is_configured)
        self.assertTrue(transport.closed)
        for rule in config.rules.values():
            self.assertEqual(0, transport.registers[(rule.actuator_id, TORQUE_ENABLE.address)])

    def test_raw_conversion_and_signed_sdk_encoding_are_bounded(self):
        config = frozen_config()
        self.assertEqual(2048, config.engineering_to_raw("J1", 0.0))
        config.engineering_to_raw("J2", 115.0)
        with self.assertRaisesRegex(ValueError, "controlled motion envelope"):
            config.engineering_to_raw("J2", 115.001)
        self.assertEqual(-1, _decoded(_encoded(-1, 2, True), 2, True))
        self.assertEqual(-32768, _decoded(_encoded(-32768, 2, True), 2, True))
        self.assertEqual(32767, _decoded(_encoded(32767, 2, True), 2, True))
        with self.assertRaisesRegex(ValueError, "controlled motion envelope"):
            config.engineering_to_raw("J1", 400.0)
        with self.assertRaisesRegex(BusError, "does not fit"):
            _encoded(256, 1, False)
        with self.assertRaisesRegex(BusError, "does not fit"):
            _encoded(-32769, 2, True)


if __name__ == "__main__":
    unittest.main()
