import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUPERVISOR_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUPERVISOR_ROOT))

from project_button_supervisor.actuator_config import ActuatorConfiguration, ActuatorReadback  # noqa: E402


CONFIG_PATH = ROOT / "firmware" / "supervisor" / "actuator-config.json"


class ActuatorConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.config = ActuatorConfiguration.from_json(CONFIG_PATH)

    def readback(self, **changes):
        values = dict(
            actuator_id=1,
            model="XM540-W270-T",
            model_number=1130,
            firmware_version=46,
            operating_mode=5,
            drive_mode=0,
            startup_configuration=0,
            torque_enable=0,
            current_limit_raw=800,
            goal_current_raw=800,
            hardware_error_status=0,
        )
        values.update(changes)
        return ActuatorReadback(**values)

    def test_candidate_remains_fail_closed_while_received_identity_and_external_limit_open(self):
        reasons = self.config.torque_enable_inhibits("J1", self.readback())
        self.assertIn("RELEASE_SELECTIONS_OPEN", reasons)
        self.assertIn("MODEL_NUMBER_UNVERIFIED", reasons)
        self.assertIn("FIRMWARE_VERSION_UNVERIFIED", reasons)

    def test_torque_already_enabled_is_rejected(self):
        self.assertIn("TORQUE_ALREADY_ENABLED", self.config.torque_enable_inhibits("J1", self.readback(torque_enable=1)))

    def test_startup_torque_bit_is_rejected(self):
        self.assertIn("STARTUP_TORQUE_MISMATCH", self.config.torque_enable_inhibits("J1", self.readback(startup_configuration=1)))

    def test_goal_update_torque_bit_is_rejected(self):
        self.assertIn("TORQUE_ON_GOAL_UPDATE_MISMATCH", self.config.torque_enable_inhibits("J1", self.readback(drive_mode=8)))

    def test_mode_and_current_mismatch_are_rejected(self):
        reasons = self.config.torque_enable_inhibits("J1", self.readback(operating_mode=3, drive_mode=1, current_limit_raw=801))
        self.assertIn("OPERATING_MODE_MISMATCH", reasons)
        self.assertIn("DRIVE_MODE_MISMATCH", reasons)
        self.assertIn("CURRENT_LIMIT_MISMATCH", reasons)

    def test_goal_current_over_candidate_is_rejected(self):
        self.assertIn("GOAL_CURRENT_EXCEEDS_CANDIDATE", self.config.torque_enable_inhibits("J1", self.readback(goal_current_raw=801)))

    def test_hardware_error_is_rejected(self):
        self.assertIn("HARDWARE_ERROR_PRESENT", self.config.torque_enable_inhibits("J1", self.readback(hardware_error_status=4)))

    def test_fully_frozen_copy_can_pass_nominal_readback(self):
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["external_branch_current_limit_a"] = 2.4
        raw["transport"]["device"] = "TEST-ONLY"
        raw["mechanical_limit_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
        raw["mechanical_limit_binding"]["acceptance_evidence_hash"] = "C" * 64
        raw["current_envelope_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
        raw["current_envelope_binding"]["acceptance_evidence_hash"] = "D" * 64
        for item in raw["actuators"].values():
            item["model_number"] = 1130 if item["model"].startswith("XM540") else 1020
            item["firmware_version"] = 46
            item["profile_velocity_raw_candidate"] = 20
            item["profile_acceleration_raw_candidate"] = 5
            item["position_zero_raw"] = 2048
            item["position_zero_engineering"] = 0.0
            item["raw_per_unit"] = 10.0
            item["direction"] = 1
            item["minimum_raw"] = 0
            item["maximum_raw"] = 4095
            item["start_tolerance_raw"] = 10
            item["minimum_input_voltage_raw"] = 100
            item["maximum_input_voltage_raw"] = 140
            item["maximum_temperature_c"] = 60
        frozen = ActuatorConfiguration(raw)
        self.assertEqual((), frozen.torque_enable_inhibits("J1", self.readback()))
        self.assertEqual(frozen.engineering_to_raw("J2", 115.0), frozen.engineering_to_raw("J2", 115.0))
        with self.assertRaisesRegex(ValueError, "controlled motion envelope"):
            frozen.engineering_to_raw("J2", 115.001)

    def test_repository_calibration_refuses_raw_conversion(self):
        with self.assertRaisesRegex(ValueError, "selections remain open"):
            self.config.engineering_to_raw("J1", 0.0)

    def test_duplicate_actuator_id_keeps_release_fail_closed(self):
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["external_branch_current_limit_a"] = 2.4
        raw["transport"]["device"] = "TEST-ONLY"
        raw["mechanical_limit_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
        raw["mechanical_limit_binding"]["acceptance_evidence_hash"] = "C" * 64
        raw["current_envelope_binding"]["release_state"] = "ACCEPTED-FOR-GUARDED-HIL"
        raw["current_envelope_binding"]["acceptance_evidence_hash"] = "D" * 64
        for item in raw["actuators"].values():
            item.update(
                model_number=1130,
                firmware_version=46,
                profile_velocity_raw_candidate=20,
                profile_acceleration_raw_candidate=5,
                position_zero_raw=2048,
                position_zero_engineering=0.0,
                raw_per_unit=10.0,
                direction=1,
                minimum_raw=0,
                maximum_raw=4095,
                start_tolerance_raw=10,
                minimum_input_voltage_raw=100,
                maximum_input_voltage_raw=140,
                maximum_temperature_c=60,
            )
        raw["actuators"]["J2"]["id"] = raw["actuators"]["J1"]["id"]
        self.assertFalse(ActuatorConfiguration(raw).release_selections_closed)

    def test_stale_limit_or_mechanical_revision_keeps_release_fail_closed(self):
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["actuators"]["J2"]["maximum_engineering"] = 120.0
        self.assertFalse(ActuatorConfiguration(raw).release_selections_closed)
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["mechanical_limit_binding"]["arm_architecture_revision"] = "HR-V0-ARM-ARCH-P0.5"
        self.assertFalse(ActuatorConfiguration(raw).release_selections_closed)
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["configuration_id"] = "HR-V0-ACT-P0.1"
        self.assertFalse(ActuatorConfiguration(raw).release_selections_closed)


if __name__ == "__main__":
    unittest.main()
