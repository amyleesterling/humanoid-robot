"""Validate the preliminary HR-V0 watchdog and supervisor source package.

This proves source/configuration consistency and executable reference-model
tests only. It does not compile an RP2040 binary, perform HIL testing, establish
functional-safety integrity, or authorize energization.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "firmware"
MANIFEST = FIRMWARE / "SOURCE-MANIFEST.csv"
WARNING = "PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def controlled_files() -> list[Path]:
    return [
        path for path in sorted(FIRMWARE.rglob("*"))
        if path.is_file()
        and path != MANIFEST
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]


def current_hashes() -> dict[str, str]:
    return {
        path.relative_to(FIRMWARE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in controlled_files()
    }


def write_manifest() -> None:
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256"])
        writer.writerows(current_hashes().items())


def load_manifest() -> dict[str, str]:
    if not MANIFEST.is_file():
        return {}
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        return {row["file"]: row["sha256"] for row in csv.DictReader(handle)}


def run_tests(path: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", path, "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def main() -> int:
    if "--write-manifest" in sys.argv:
        write_manifest()

    failures: list[str] = []
    watchdog_ok, watchdog_log = run_tests("firmware/watchdog/tests")
    supervisor_ok, supervisor_log = run_tests("firmware/supervisor/tests")
    if not watchdog_ok:
        failures.append("watchdog reference-model tests failed\n" + watchdog_log)
    if not supervisor_ok:
        failures.append("supervisor tests failed\n" + supervisor_log)

    watchdog_config = json.loads((FIRMWARE / "watchdog" / "watchdog-config.json").read_text(encoding="utf-8"))
    expected_gpio = {
        "heartbeat_input": {"gpio": 2, "physical_pin": 4},
        "relay1_drive": {"gpio": 3, "physical_pin": 5},
        "relay2_drive": {"gpio": 4, "physical_pin": 6},
        "relay1_nc_feedback": {"gpio": 6, "physical_pin": 9},
        "relay2_nc_feedback": {"gpio": 7, "physical_pin": 10},
    }
    if watchdog_config.get("configuration_id") != "HR-V0-WD-P0.3":
        failures.append("watchdog configuration ID is not HR-V0-WD-P0.3")
    if watchdog_config.get("gpio_assignments") != expected_gpio:
        failures.append("watchdog GPIO assignment differs from the Electrical V3-P0.4 candidate")
    if watchdog_config.get("feedback_front_end") != "TI_ISO1212DBQ_P0.1":
        failures.append("watchdog feedback front end differs from the Electrical V3-P0.4 candidate")
    if watchdog_config.get("feedback_gpio_active_high") is not True:
        failures.append("watchdog feedback GPIO polarity is not active-high for KWD NC closed")
    header = (FIRMWARE / "watchdog" / "include" / "pb_watchdog.h").read_text(encoding="utf-8")
    source = (FIRMWARE / "watchdog" / "src" / "pb_watchdog.c").read_text(encoding="utf-8")
    define_names = {
        "heartbeat_nominal_edge_ms": "PB_WD_HEARTBEAT_NOMINAL_EDGE_MS",
        "heartbeat_timeout_ms": "PB_WD_HEARTBEAT_TIMEOUT_MS",
        "heartbeat_minimum_edge_ms": "PB_WD_HEARTBEAT_MINIMUM_EDGE_MS",
        "startup_valid_edges": "PB_WD_STARTUP_VALID_EDGES",
        "relay_feedback_settle_ms": "PB_WD_RELAY_FEEDBACK_SETTLE_MS",
    }
    for json_name, define_name in define_names.items():
        match = re.search(rf"#define\s+{define_name}\s+(\d+)u", header)
        if match is None or int(match.group(1)) != int(watchdog_config[json_name]):
            failures.append(f"watchdog C constant {define_name} differs from watchdog-config.json")
    for required in (
        "_Static_assert(PB_WD_HEARTBEAT_TIMEOUT_MS == 3u * PB_WD_HEARTBEAT_NOMINAL_EDGE_MS",
        "state->relay1_drive = false;",
        "state->relay2_drive = false;",
        "state->valid_edges >= PB_WD_STARTUP_VALID_EDGES",
        "inputs.relay1_nc != !state->relay1_drive",
        "inputs.relay2_nc != !state->relay2_drive",
    ):
        if required not in source:
            failures.append(f"portable watchdog source invariant missing: {required}")

    supervisor_config = json.loads((FIRMWARE / "supervisor" / "supervisor-config.json").read_text(encoding="utf-8"))
    for field in ("configuration_hash", "kinematic_model_hash"):
        value = supervisor_config[field].upper()
        if "SELECTION" not in value or "REQUIRED" not in value:
            failures.append(f"unreleased supervisor {field} is no longer fail-closed SELECTION REQUIRED")
    model = (FIRMWARE / "supervisor" / "project_button_supervisor" / "model.py").read_text(encoding="utf-8")
    for required in (
        "torque_enable_request=self.state is OperatingState.DRIVE_ENABLED",
        "if not self.config.selections_closed:",
        "self._invalidate_target()",
        "UNEXPECTED_ARM_ORDER",
        "HARDWARE_PERMIT_DROPPED",
        "command.session_id != self.session_id",
        "waiting for three valid watchdog heartbeat edges",
        "computed TCP speed outside configured limit",
    ):
        if required not in model:
            failures.append(f"supervisor fail-closed invariant missing: {required}")

    if load_manifest() != current_hashes():
        failures.append("firmware SOURCE-MANIFEST.csv does not match the controlled source tree")

    requirements = (ROOT / "requirements" / "requirements.csv").read_text(encoding="utf-8-sig")
    if "distinct software ARM action" in requirements:
        failures.append("SAFE-003 still conflicts with the physical V3 ARM architecture")

    if failures:
        print("HR-V0 firmware validation: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1

    test_count = watchdog_log.count(" ... ok") + supervisor_log.count(" ... ok")
    print(f"HR-V0 firmware source validation: PASS ({test_count} executable unit tests)")
    print("Portable watchdog C compile/binary/HIL: NOT PERFORMED - TOOLCHAIN AND HARDWARE SELECTION REQUIRED")
    print(WARNING)
    print("Source tests and hashes are not functional-safety approval or permission to energize.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
