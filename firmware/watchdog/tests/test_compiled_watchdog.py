from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


WATCHDOG_ROOT = Path(__file__).resolve().parents[1]
ROOT = WATCHDOG_ROOT.parents[1]
RUNNER = WATCHDOG_ROOT / "output" / "host-vector" / "P0.1" / "pb_watchdog_vector_runner.exe"
sys.path.insert(0, str(WATCHDOG_ROOT))

from reference_model import WatchdogConfig, WatchdogModel  # noqa: E402


Vector = tuple[int, bool, bool, bool]


SCENARIOS: dict[str, list[Vector]] = {
    "three_edges_and_timeout_boundaries": [
        (0, False, True, True),
        (100, True, True, True),
        (200, False, True, True),
        (300, True, True, True),
        (599, True, False, False),
        (600, True, False, False),
    ],
    "minimum_edge_19_ms_fault": [
        (0, False, True, True),
        (100, True, True, True),
        (119, False, True, True),
    ],
    "minimum_edge_20_ms_valid": [
        (0, False, True, True),
        (100, True, True, True),
        (120, False, True, True),
        (140, True, True, True),
    ],
    "feedback_settle_24_then_25_ms": [
        (0, False, True, True),
        (100, True, True, True),
        (200, False, True, True),
        (300, True, True, True),
        (324, True, True, True),
        (325, True, True, False),
    ],
    "relay2_feedback_fault": [
        (0, False, True, True),
        (100, True, True, True),
        (200, False, True, True),
        (300, True, True, True),
        (325, True, False, True),
    ],
    "three_edge_recovery_after_timeout": [
        (0, False, True, True),
        (100, True, True, True),
        (200, False, True, True),
        (300, True, True, True),
        (600, True, False, False),
        (625, True, True, True),
        (700, False, True, True),
        (800, True, True, True),
        (900, False, True, True),
    ],
    "uint32_wrap": [
        (0xFFFFFF00, False, True, True),
        ((0xFFFFFF00 + 100) & 0xFFFFFFFF, True, True, True),
        ((0xFFFFFF00 + 200) & 0xFFFFFFFF, False, True, True),
        ((0xFFFFFF00 + 300) & 0xFFFFFFFF, True, True, True),
    ],
    "clock_regression": [
        (0, False, True, True),
        (100, True, True, True),
        (200, False, True, True),
        (300, True, True, True),
        (250, True, False, False),
    ],
    "half_range_fail_closed": [
        (0, False, True, True),
        (0x80000000, False, True, True),
    ],
}


FAULT_BY_REASON = {
    None: 0,
    "heartbeat edge interval below configured minimum": 1,
    "relay 1 NC feedback disagrees with command": 2,
    "relay 2 NC feedback disagrees with command": 3,
    "monotonic clock moved backward or exceeded supported half-range": 4,
}


def model_outputs(vectors: list[Vector]) -> list[tuple[int, int, int, int, int, int]]:
    model = WatchdogModel(WatchdogConfig.from_json(WATCHDOG_ROOT / "watchdog-config.json"))
    outputs: list[tuple[int, int, int, int, int, int]] = []
    for now_ms, heartbeat, relay1_nc, relay2_nc in vectors:
        output = model.step(now_ms, heartbeat, relay1_nc, relay2_nc)
        outputs.append(
            (
                int(output.relay1_drive),
                int(output.relay2_drive),
                int(output.heartbeat_fresh),
                int(output.fault_latched),
                FAULT_BY_REASON[output.fault_reason],
                output.valid_edges,
            )
        )
    return outputs


def compiled_outputs(vectors: list[Vector]) -> list[tuple[int, int, int, int, int, int]]:
    payload = "".join(
        f"{now_ms},{int(heartbeat)},{int(relay1_nc)},{int(relay2_nc)}\n"
        for now_ms, heartbeat, relay1_nc, relay2_nc in vectors
    )
    result = subprocess.run(
        [str(RUNNER)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"compiled runner failed ({result.returncode}): {result.stderr}")
    return [tuple(int(field) for field in line.split(",")) for line in result.stdout.splitlines()]


class CompiledWatchdogDifferentialTests(unittest.TestCase):
    def test_controlled_runner_exists(self) -> None:
        self.assertTrue(RUNNER.is_file(), f"controlled compiled runner missing: {RUNNER}")

    def test_compiled_c_matches_reference_model(self) -> None:
        for name, vectors in SCENARIOS.items():
            with self.subTest(scenario=name):
                self.assertEqual(model_outputs(vectors), compiled_outputs(vectors))


if __name__ == "__main__":
    unittest.main()
