#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-EVID-LOG-P0.1 / R236."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "HR-V0-EVID-LOG-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
DIRECTORIES = (
    ROOT / "controls/hr-v0-runtime-evidence-log-p0.1",
    ROOT / "release/hr-v0/runtime-evidence-log-p0.1",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected_files = {
        "README.md", "index.html", "package-status.json", "log-schema.json",
        "channel-register.csv", "clock-budget.csv", "calibration-register.csv",
        "test-case-register.csv", "open-holds.csv", "session-acceptance-template.csv",
        "file-manifest.csv",
    }
    for directory in DIRECTORIES:
        actual = {path.name for path in directory.iterdir() if path.is_file()}
        need(actual == expected_files, f"package membership changed: {directory}")
        manifest = rows(directory / "file-manifest.csv")
        need({row["file"] for row in manifest} == expected_files - {"file-manifest.csv"}, f"manifest membership changed: {directory}")
        for row in manifest:
            path = directory / row["file"]
            need(path.stat().st_size == int(row["bytes"]), f"manifest byte count mismatch: {path}")
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], f"manifest hash mismatch: {path}")

        channels = rows(directory / "channel-register.csv")
        clocks = rows(directory / "clock-budget.csv")
        calibrations = rows(directory / "calibration-register.csv")
        tests = rows(directory / "test-case-register.csv")
        holds = rows(directory / "open-holds.csv")
        acceptance = rows(directory / "session-acceptance-template.csv")
        status = json.loads((directory / "package-status.json").read_text(encoding="utf-8"))
        schema = json.loads((directory / "log-schema.json").read_text(encoding="utf-8"))
        guide = (directory / "index.html").read_text(encoding="utf-8")

        need(len(channels) == 14 and [row["channel_id"] for row in channels] == [f"LOG-CH-{number:03d}" for number in range(1, 15)], "event-channel register changed")
        need({row["event"] for row in channels} == {"SESSION_START", "RUNTIME_START_REQUEST", "RUNTIME_STARTED", "CYCLE_BEGIN", "FEEDBACK_SAMPLE", "COMMAND_RECEIVED", "COMMAND_DECISION", "COMMAND_SAMPLE", "SUPERVISOR_EVENT", "CYCLE_OUTPUT", "RUNTIME_SHUTDOWN_REQUEST", "RUNTIME_STOPPED", "RUNTIME_FAIL_CLOSED", "SESSION_END"}, "event set changed")
        need(len(clocks) == 10 and all(row["status"] == "OPEN" for row in clocks), "clock budget must retain ten open rows")
        need(next(row for row in clocks if row["clock_id"] == "CLK-001")["candidate_or_required_limit"] == "<= 10 ms", "100 Hz period bound changed")
        need(len(calibrations) == 12 and all(row["status"] == "SELECTION REQUIRED" and not row["serial"] and not row["calibration_certificate"] and not row["uncertainty"] for row in calibrations), "calibration template contains unsupported evidence")
        need(len(tests) == 15 and all(row["state"] == "NOT_EXECUTED" and row["authorization"] == "NOT_AUTHORIZED" and not row["actual_result"] and not row["evidence_hash"] for row in tests), "future test register contains result or authority")
        need(len(holds) == 15 and all(row["state"] == "OPEN" for row in holds), "open-hold register changed")
        need(len(acceptance) == 1 and acceptance[0]["disposition"] == "NOT_REVIEWED" and not acceptance[0]["session_id"] and not acceptance[0]["log_sha256"], "session template contains evidence")
        for register in (channels, clocks, calibrations, tests, holds, acceptance):
            need(all(row["warning"] == WARNING for row in register), f"warning changed in {directory}")
        need(status.get("identifier") == IDENTIFIER and status.get("runtime_sink_required") is True, "package status identity/runtime binding changed")
        need(status.get("physical_tests_executed") == 0 and status.get("open_holds") == 15, "package status claims unsupported closure")
        need(status.get("sol_m022_disposition") == "PARTIALLY_ADDRESSED_OPEN" and status.get("functional_safety_credit") == "NONE" and status.get("work_authority") is False, "M-022 or authority boundary changed")
        need(schema.get("$id") == "urn:project-button:hr-v0:evidence-log:p0.1" and schema.get("additionalProperties") is False, "JSON schema identity/strictness changed")
        need(set(schema.get("required", [])) == {"schema_id", "sequence", "monotonic_ms", "wall_time_utc", "event", "context_sha256", "previous_sha256", "payload", "record_sha256"}, "JSON schema required set changed")
        need("font:16px" in guide and "font-size:16px" in guide, "guide does not preserve 16 px text floor")
        need(not re.search(r"(?:font-size|font):\s*(?:1[0-5]|[0-9])px", guide), "guide contains undersized text")
        need(guide.count("data-show=") == 4 and guide.count("<section") == 4, "interactive guide section controls changed")

    source = (ROOT / "firmware/supervisor/project_button_supervisor/evidence_log.py").read_text(encoding="utf-8")
    runtime = (ROOT / "firmware/supervisor/project_button_supervisor/runtime.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "firmware/supervisor/tests/test_runtime.py").read_text(encoding="utf-8")
    log_tests = (ROOT / "firmware/supervisor/tests/test_evidence_log.py").read_text(encoding="utf-8")
    preflight_path = ROOT / "software/host/hr-v0-host-deploy-p0.1/project_button_host/preflight.py"
    preflight_source = preflight_path.read_text(encoding="utf-8")
    host_config = json.loads((ROOT / "software/host/hr-v0-host-deploy-p0.1/host-deploy-config.json").read_text(encoding="utf-8"))

    for token in ("path.open(\"x\"", "allow_nan=False", "os.fsync", "monotonic timestamp regressed", "SESSION_START", "SESSION_END", "record_sha256", "verify_log"):
        need(token in source, f"evidence source invariant missing: {token}")
    for token in ("evidence: EvidenceSink", "CYCLE_BEGIN", "FEEDBACK_SAMPLE", "COMMAND_RECEIVED", "COMMAND_DECISION", "COMMAND_SAMPLE", "SUPERVISOR_EVENT", "CYCLE_OUTPUT", "RUNTIME_FAIL_CLOSED"):
        need(token in runtime, f"runtime evidence invariant missing: {token}")
    need(runtime.find("self.evidence.record(now_ms, \"RUNTIME_START_REQUEST\"") < runtime.find("self.hardware.disable_heartbeat()"), "runtime can access hardware before initial evidence record")
    need("test_evidence_failure_during_motion_fails_closed" in runtime_tests, "runtime evidence-failure regression missing")
    for token in ("test_round_trip_verifies_closed_hash_chain", "test_tamper_is_detected", "test_monotonic_regression_is_rejected_before_write", "test_existing_session_file_is_never_appended", "test_unresolved_context_is_rejected"):
        need(token in log_tests, f"evidence-log regression missing: {token}")
    need("not 1 <= period <= 10" in preflight_source, "preflight does not enforce 100 Hz-capable period")
    evidence_config = host_config.get("evidence_log", {})
    need(evidence_config.get("schema_id") == IDENTIFIER and evidence_config.get("directory") == "/var/lib/project-button/logs", "host evidence-log binding changed")
    need(evidence_config.get("identities", {}).get("calibration_set_id") == "SELECTION REQUIRED", "calibration set was inferred")
    need(all(value == "SELECTION REQUIRED" for value in evidence_config.get("hashes", {}).values()), "host evidence hashes were populated without acceptance")

    preflight = subprocess.run([sys.executable, str(preflight_path), "--config", str(ROOT / "software/host/hr-v0-host-deploy-p0.1/host-deploy-config.json")], cwd=ROOT, text=True, capture_output=True)
    need(preflight.returncode == 78, "committed host preflight did not fail closed")
    try:
        preflight_result = json.loads(preflight.stdout)
    except json.JSONDecodeError:
        preflight_result = {}
    need(preflight_result.get("ready") is False and len(preflight_result.get("holds", [])) == 49, "committed preflight must expose exactly 49 holds")

    firmware_tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "firmware/supervisor/tests", "-v"], cwd=ROOT, text=True, capture_output=True)
    need(firmware_tests.returncode == 0 and "Ran 75 tests" in firmware_tests.stderr, "75 supervisor/logging tests did not pass")

    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    firmware_product = next((item for item in metadata.get("current_products", []) if item.get("domain") == "firmware"), {})
    need(IDENTIFIER in firmware_product.get("supporting_identifiers", []), "release metadata lacks evidence-log identifier")
    need(firmware_product.get("runtime_evidence_log") == IDENTIFIER, "release metadata lacks current evidence-log field")
    need((ROOT / "docs/hr-v0-runtime-evidence-log-p0.1.md").is_file(), "R236 summary document missing")
    need((ROOT / "requirements/hr-v0-gate-evidence-supplement-r236.csv").is_file(), "R236 gate supplement missing")

    if failures:
        raise SystemExit("HR-V0 runtime evidence-log check failed:\n- " + "\n- ".join(failures))
    print("HR-V0-EVID-LOG-P0.1 PASS: 14 events, 10 clock rows, 12 blank calibrations, 15 unexecuted tests, 15 open holds")
    print("75 supervisor/logging tests pass; target timing, calibration, storage, HIL and qualified acceptance remain open")
    print("Sol M-022 remains PARTIALLY_ADDRESSED_OPEN; EG-002/017/020/021/022 remain PARTIAL")
    print(WARNING)


if __name__ == "__main__":
    main()
