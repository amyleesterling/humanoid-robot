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
        reasons = self.config.torque_enable_inhibits("J1", self.readback(operating_mode=3, current_limit_raw=801))
        self.assertIn("OPERATING_MODE_MISMATCH", reasons)
        self.assertIn("CURRENT_LIMIT_MISMATCH", reasons)

    def test_goal_current_over_candidate_is_rejected(self):
        self.assertIn("GOAL_CURRENT_EXCEEDS_CANDIDATE", self.config.torque_enable_inhibits("J1", self.readback(goal_current_raw=801)))

    def test_hardware_error_is_rejected(self):
        self.assertIn("HARDWARE_ERROR_PRESENT", self.config.torque_enable_inhibits("J1", self.readback(hardware_error_status=4)))

    def test_fully_frozen_copy_can_pass_nominal_readback(self):
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        raw["external_branch_current_limit_a"] = 2.4
        for item in raw["actuators"].values():
            item["model_number"] = 1130 if item["model"].startswith("XM540") else 1020
            item["firmware_version"] = 46
        frozen = ActuatorConfiguration(raw)
        self.assertEqual((), frozen.torque_enable_inhibits("J1", self.readback()))


if __name__ == "__main__":
    unittest.main()
