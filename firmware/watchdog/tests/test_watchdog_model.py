from __future__ import annotations

import sys
import unittest
from pathlib import Path


WATCHDOG_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WATCHDOG_ROOT))

from reference_model import WatchdogConfig, WatchdogModel  # noqa: E402


def model() -> WatchdogModel:
    return WatchdogModel(WatchdogConfig.from_json(WATCHDOG_ROOT / "watchdog-config.json"))


def reach_permit(watchdog: WatchdogModel) -> None:
    watchdog.step(0, False, True, True)
    watchdog.step(100, True, True, True)
    watchdog.step(200, False, True, True)
    output = watchdog.step(300, True, True, True)
    if not (output.relay1_drive and output.relay2_drive):
        raise AssertionError("test helper failed to reach permit")


class WatchdogModelTests(unittest.TestCase):
    def test_power_up_and_stuck_level_are_default_off(self) -> None:
        watchdog = model()
        self.assertFalse(watchdog.step(0, False, True, True).relay1_drive)
        self.assertFalse(watchdog.step(500, False, True, True).relay2_drive)

    def test_three_valid_edges_are_required(self) -> None:
        watchdog = model()
        self.assertFalse(watchdog.step(0, False, True, True).relay1_drive)
        self.assertFalse(watchdog.step(100, True, True, True).relay1_drive)
        self.assertFalse(watchdog.step(200, False, True, True).relay1_drive)
        output = watchdog.step(300, True, True, True)
        self.assertTrue(output.relay1_drive)
        self.assertTrue(output.relay2_drive)
        self.assertEqual(output.valid_edges, 3)

    def test_timeout_drops_both_and_recovery_requires_three_new_edges(self) -> None:
        watchdog = model()
        reach_permit(watchdog)
        output = watchdog.step(600, True, False, False)
        self.assertFalse(output.relay1_drive)
        self.assertFalse(output.relay2_drive)
        self.assertFalse(output.heartbeat_fresh)
        self.assertFalse(output.fault_latched)

        watchdog.step(625, True, True, True)
        self.assertFalse(watchdog.step(700, False, True, True).relay1_drive)
        self.assertFalse(watchdog.step(800, True, True, True).relay1_drive)
        self.assertTrue(watchdog.step(900, False, True, True).relay1_drive)

    def test_too_fast_edge_latches_and_drops_both(self) -> None:
        watchdog = model()
        reach_permit(watchdog)
        output = watchdog.step(310, False, True, True)
        self.assertTrue(output.fault_latched)
        self.assertFalse(output.relay1_drive)
        self.assertFalse(output.relay2_drive)
        self.assertIn("minimum", output.fault_reason or "")

    def test_relay_feedback_disagreement_latches_and_drops_both(self) -> None:
        watchdog = model()
        reach_permit(watchdog)
        output = watchdog.step(326, True, True, False)
        self.assertTrue(output.fault_latched)
        self.assertFalse(output.relay1_drive)
        self.assertFalse(output.relay2_drive)
        self.assertIn("relay 1", output.fault_reason or "")

    def test_feedback_is_allowed_to_settle(self) -> None:
        watchdog = model()
        reach_permit(watchdog)
        self.assertTrue(watchdog.step(320, True, True, True).relay1_drive)
        output = watchdog.step(325, True, False, False)
        self.assertFalse(output.fault_latched)
        self.assertTrue(output.relay1_drive)

    def test_monotonic_clock_regression_fails_off(self) -> None:
        watchdog = model()
        reach_permit(watchdog)
        output = watchdog.step(250, True, False, False)
        self.assertTrue(output.fault_latched)
        self.assertFalse(output.relay1_drive)
        self.assertFalse(output.relay2_drive)


if __name__ == "__main__":
    unittest.main()
