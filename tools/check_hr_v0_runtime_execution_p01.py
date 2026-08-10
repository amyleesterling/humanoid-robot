#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-RUNTIME-P0.1 / R198 plus R199 backends."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "software/host/hr-v0-host-deploy-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    controls = rows(ROOT / "controls/hr-v0-runtime-execution-boundary-p0.1.csv")
    overlay = rows(HOST / "overlay-manifest.csv")
    holds = rows(HOST / "hold-register.csv")
    host_config = json.loads((HOST / "host-deploy-config.json").read_text(encoding="utf-8"))
    supervisor_config = json.loads((ROOT / "firmware/supervisor/supervisor-config.json").read_text(encoding="utf-8"))
    runtime = (ROOT / "firmware/supervisor/project_button_supervisor/runtime.py").read_text(encoding="utf-8")
    bus = (ROOT / "firmware/supervisor/project_button_supervisor/dynamixel_bus.py").read_text(encoding="utf-8")
    entry_path = HOST / "project_button_host/runtime_entrypoint.py"
    entry = entry_path.read_text(encoding="utf-8")
    runtime_tests = (ROOT / "firmware/supervisor/tests/test_runtime.py").read_text(encoding="utf-8")
    host_tests = (HOST / "tests/test_host_deploy.py").read_text(encoding="utf-8")
    backend_tests = (HOST / "tests/test_backends.py").read_text(encoding="utf-8")
    gpio_path = HOST / "project_button_host/gpiod_hardware.py"
    command_path = HOST / "project_button_host/unix_command_source.py"
    gpio = gpio_path.read_text(encoding="utf-8")
    command_source = command_path.read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-runtime-execution-boundary-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/host-deployment-p0.1/index.html").read_text(encoding="utf-8")

    need(len(controls) == 14, "runtime control register must contain fourteen rows")
    need([row["control_id"] for row in controls] == [f"RTE-{index:03d}" for index in range(1, 15)], "runtime control IDs changed")
    need(all(row["warning"] == WARNING for row in controls), "runtime control warning changed")
    need(next(row for row in controls if row["control_id"] == "RTE-008")["current_state"] == "SELECTION REQUIRED", "cycle-period hold was released")
    need(next(row for row in controls if row["control_id"] == "RTE-012")["current_state"] == "NOT EXECUTED", "target HIL was falsely executed")
    need(next(row for row in controls if row["control_id"] == "RTE-013")["current_state"] == "NOT AUTHORIZED", "motion was falsely authorized")

    need(len(overlay) == 21 and len({row["target"] for row in overlay}) == 21, "twenty-one exact overlay rows are required")
    need(all((ROOT / row["source"]).is_file() for row in overlay), "overlay source is absent")
    need(len(holds) == 18 and sum(row["current_state"] == "PARTIAL" for row in holds) == 2, "host hold state count changed")
    need(next(row for row in holds if row["hold_id"] == "HOST-004")["current_state"] == "PARTIAL", "HOST-004 GPIO allocation progress changed")
    need(next(row for row in holds if row["hold_id"] == "HOST-006")["current_state"] == "PARTIAL", "HOST-006 source progress changed")

    expected_entry_hash = hashlib.sha256(entry_path.read_bytes()).hexdigest()
    need(host_config.get("runtime_entrypoint") == "/opt/project-button/lib/project_button_host/runtime_entrypoint.py", "entrypoint target changed")
    need(host_config.get("runtime_entrypoint_sha256") == expected_entry_hash, "entrypoint hash mismatch")
    for key in ("runtime_cycle_period_ms", "serial_device"):
        need(host_config.get(key) == "SELECTION REQUIRED", f"unreleased host selection populated: {key}")
    need(host_config.get("runtime_backend") == "project_button_host.unix_command_source:factory", "command backend identity changed")
    need(host_config.get("gpio_backend") == "project_button_host.gpiod_hardware:factory", "GPIO backend identity changed")
    need(host_config.get("runtime_backend_sha256") == hashlib.sha256(command_path.read_bytes()).hexdigest(), "command backend hash mismatch")
    need(host_config.get("gpio_backend_sha256") == hashlib.sha256(gpio_path.read_bytes()).hexdigest(), "GPIO backend hash mismatch")
    need(supervisor_config.get("maximum_sample_lateness_ms") is None, "unreleased sample-lateness value populated")
    for key in ("maximum_trajectory_samples", "maximum_trajectory_duration_ms", "maximum_execution_slack_ms"):
        need(supervisor_config.get(key) is None, f"unreleased supervisor bound populated: {key}")

    for token in (
        "self.hardware.disable_heartbeat()",
        "self.hardware.service_heartbeat(now_ms, outputs.heartbeat_allowed)",
        "self.bus.connect_and_configure()",
        "self.supervisor.observe_hardware(snapshot, now_ms)",
        "self.bus.start_trajectory",
        "missed its released lateness bound",
        "self.bus.stop()",
    ):
        need(token in runtime, f"runtime invariant missing: {token}")
    for token in (
        "expected_goal_current = rule.goal_current_max_raw if require_torque else 0",
        "torque is enabled outside motion authority",
        "_best_effort_goal_current_zero",
        "raw_to_engineering",
    ):
        need(token in bus, f"bus/runtime integration invariant missing: {token}")
    for token in (
        "result = evaluate(config_path, root)",
        "if not supervisor.config.selections_closed",
        "if not actuators.release_selections_closed",
        "signal.SIGTERM",
        "RuntimeExecutive",
    ):
        need(token in entry, f"entrypoint invariant missing: {token}")
    need(entry.find("result = evaluate(config_path, root)") < entry.find("_factory(str(host[\"gpio_backend\"]))"), "backend import is not visibly after preflight")

    for token in (
        "test_reset_and_arm_without_command_never_enable_torque",
        "test_fresh_command_executes_ordered_samples_then_removes_torque",
        "test_hardware_dropout_removes_heartbeat_and_bus_torque",
        "test_missed_sample_lateness_fails_active_trajectory_closed",
        "test_shutdown_removes_heartbeat_before_closing_resources",
    ):
        need(token in runtime_tests, f"runtime regression missing: {token}")
    need("test_runtime_entrypoint_does_not_import_selected_backends_on_hold" in host_tests, "host backend-import refusal regression missing")
    for token in (
        "test_heartbeat_lateness_forces_inactive",
        "test_heartbeat_time_reversal_forces_inactive",
        "test_valid_command_parses_to_typed_model",
        "test_command_rejects_nonfinite_value",
    ):
        need(token in backend_tests, f"backend regression missing: {token}")
    for token in ("metadata.version(distribution)", "gpiod.request_lines", "bias=gpiod.line.Bias.DISABLED", "heartbeat edge missed its released lateness bound"):
        need(token in gpio, f"GPIO backend invariant missing: {token}")
    for token in ("socket.AF_UNIX", "socket.SO_PASSCRED", "socket.SCM_CREDENTIALS", "set(raw) != COMMAND_FIELDS", "math.isfinite"):
        need(token in command_source, f"command backend invariant missing: {token}")

    preflight = subprocess.run(
        [sys.executable, str(HOST / "project_button_host/preflight.py"), "--config", str(HOST / "host-deploy-config.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    need(preflight.returncode == 78, "committed preflight did not return exit 78")
    try:
        preflight_result = json.loads(preflight.stdout)
    except json.JSONDecodeError:
        preflight_result = {}
    need(preflight_result.get("ready") is False and len(preflight_result.get("holds", [])) == 36, "committed preflight must expose exactly 36 holds")

    combined = doc + guide
    for token in ("HR-V0-RUNTIME-P0.1", "R199", "R203", "21", "36", "16", "two partial", "exit 78", "zero functional-safety credit", WARNING):
        need(token.lower() in combined.lower(), f"controlled R198 token missing: {token}")
    need("font:16px" in guide and "font-size:16px" in guide and "font-size:14px" in guide, "guide text floors missing")
    need(not re.search(r"(?:font-size|font):\s*(?:1[0-3]|[0-9])px", guide), "undersized guide CSS declaration found")

    if failures:
        raise SystemExit("HR-V0 runtime execution check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 runtime execution check passed: 21 overlay rows, 36 preflight holds, HOST-004/HOST-006 partial, 14 controls")
    print("78 firmware tests and 16 host tests are source evidence only; target execution and HIL remain NOT EXECUTED")
    print("EG-017 remains PARTIAL; backend source exists but physical observations, installation, connection, motion and energization authority do not")
    print(WARNING)


if __name__ == "__main__":
    main()
