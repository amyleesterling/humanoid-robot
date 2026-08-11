from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

from hr_v0_r213_compat import r213_allows_historical_source_hash


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-current-envelope-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    expected = {
        "README.md", "acceptance-matrix.csv", "branch-protection-decision.csv",
        "control-invariant-register.csv", "derived-current-envelope.csv", "file-manifest.csv",
        "index.html", "measurement-plan.csv", "package-status.json", "primary-source-register.csv",
        "residual-holds.csv", "test-data-template.csv",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    need(actual == expected, f"package membership changed: {sorted(actual ^ expected)}")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-CURRENT-ENV-P0.1", "identifier changed")
    need(status.get("round") == "R154", "round changed")
    for key, value in {"axes": 3, "control_invariants": 8, "branch_protection_options": 4, "measurement_steps": 11, "acceptance_rows": 14, "residual_holds": 14}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(status.get("xm540_raw_candidate") == 800, "XM540 raw candidate changed")
    need(abs(float(status.get("xm540_nominal_internal_current_screen_a", 0)) - 2.152) < 1e-9, "XM540 internal current screen changed")
    need(status.get("external_branch_current_limit_a") == "SELECTION REQUIRED", "external current limit was released")
    false_flags = ["fuse_values_released", "connector_current_conflict_closed", "physical_testing_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"]
    for key in false_flags:
        need(status.get(key) is False, f"fail-closed status changed: {key}")
    need(status.get("warning") == WARNING, "status warning changed")

    for relative, expected_hash in status.get("source_hashes", {}).items():
        path = ROOT / relative
        need(path.is_file(), f"source missing: {relative}")
        if path.is_file():
            need(digest(path) == expected_hash or r213_allows_historical_source_hash(ROOT, relative), f"source hash changed: {relative}")
    need(len(status.get("source_hashes", {})) == 7, "source-hash count changed")

    envelope = rows(OUT / "derived-current-envelope.csv")
    need({row["axis"] for row in envelope} == {"J1", "J2", "GRIPPER"}, "axis envelope changed")
    for row in envelope:
        raw = int(row["current_limit_raw_candidate"])
        nominal = float(row["nominal_internal_current_screen_a"])
        need(abs(nominal - raw * 0.00269) < 0.0006, f"raw/current arithmetic changed at {row['axis']}")
        need(row["released_external_branch_limit_a"] == "SELECTION REQUIRED", f"external limit released at {row['axis']}")
        need("PHYSICAL QUALIFICATION REQUIRED" in row["disposition"], f"physical hold missing at {row['axis']}")

    controls = rows(OUT / "control-invariant-register.csv")
    need(len(controls) == 8, "control invariant count changed")
    control_text = "\n".join(row["invariant"] + row["implementation"] for row in controls)
    for token in ("Current Limit is re-read", "Goal Current is re-read", "forces torque-off"):
        need(token in control_text, f"current control invariant missing: {token}")

    decisions = rows(OUT / "branch-protection-decision.csv")
    dispositions = {row["option_id"]: row["disposition"] for row in decisions}
    need(dispositions == {"BP-001": "REJECT AS SOLE CONTROL", "BP-002": "RETAIN FOR GUARDED QUALIFICATION", "BP-003": "ALTERNATIVE - NOT SELECTED", "BP-004": "ALTERNATIVE - NOT SELECTED"}, "architecture decision changed")

    plan = rows(OUT / "measurement-plan.csv")
    need(len(plan) == 11, "measurement-plan count changed")
    need(all(row["state"] in {"INSPECTION ONLY", "NOT EXECUTED", "SOURCE TEST PASS; PHYSICAL HIL NOT EXECUTED"} for row in plan), "measurement execution state changed")
    need(any(row["test_id"] == "CUR-Q-010" and "non-robot fixture" in row["fixture_boundary"] for row in plan), "controlled fuse-fault fixture boundary missing")

    acceptance = rows(OUT / "acceptance-matrix.csv")
    holds = rows(OUT / "residual-holds.csv")
    need(len(acceptance) == len(holds) == 14, "acceptance/hold count changed")
    need(all(row["result"] == "NOT EXECUTED" and not row["evidence_uri"] and not row["approver"] for row in acceptance), "acceptance evidence was inferred")
    need(all(row["state"] == "OPEN" for row in holds), "a current hold closed without evidence")

    evidence = rows(OUT / "test-data-template.csv")
    need(len(evidence) == 11, "test-template row count changed")
    need(all(row["result"] == "NOT EXECUTED" and row["acceptance_basis"] == "SELECTION REQUIRED" and not row["raw_data_uri"] for row in evidence), "test evidence was inferred")

    sources = rows(OUT / "primary-source-register.csv")
    need(len(sources) == 5, "primary-source count changed")
    need(all("2026-08-09" in row["revision_date"] for row in sources), "source access/revision date missing")
    need({row["manufacturer"] for row in sources} == {"ROBOTIS", "JST", "Littelfuse", "Project Button"}, "source manufacturers changed")

    config = json.loads((ROOT / "firmware" / "supervisor" / "actuator-config.json").read_text(encoding="utf-8"))
    need(config.get("external_branch_current_limit_a") == "SELECTION REQUIRED", "firmware external current limit was released")
    need(config.get("current_envelope_binding") == {"identifier": "HR-V0-DXL-CURRENT-ENV-P0.1", "release_state": "CANDIDATE-NOT-RELEASED", "acceptance_evidence_hash": "SELECTION REQUIRED"}, "firmware current-envelope binding changed")
    bus = (ROOT / "firmware" / "supervisor" / "project_button_supervisor" / "dynamixel_bus.py").read_text(encoding="utf-8")
    tests = (ROOT / "firmware" / "supervisor" / "tests" / "test_dynamixel_bus.py").read_text(encoding="utf-8")
    for token in ("configured-current-limit readback changed during execution", "goal-current readback disagrees with torque state", "torque is enabled outside motion authority", "_best_effort_goal_current_zero"):
        need(token in bus, f"runtime current invariant missing: {token}")
    for token in ("CURRENT_LIMIT.address, 801", "GOAL_CURRENT.address, 799"):
        need(token in tests, f"current fault-injection source test missing: {token}")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("Current has a software ceiling. The wire still needs proof.", "Zero safety credit", "Fourteen evidence groups remain open", "font:clamp(16px", "font-size:14px", "overflow:auto"):
        need(token in page, f"interactive guide content/style missing: {token}")
    need(not re.search(r"font-size\s*:\s*(?:[0-9]|1[01])px", page), "interactive guide contains user-facing text below 12 px")

    manifest = rows(OUT / "file-manifest.csv")
    expected_manifest = {path.name: digest(path) for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
    actual_manifest = {row["path"]: row["sha256"] for row in manifest}
    need(actual_manifest == expected_manifest, "package manifest is stale or incomplete")
    need(all(row.get("warning") == WARNING for name in expected if name.endswith((".csv", ".json")) for row in ([] if name == "file-manifest.csv" else ([status] if name == "package-status.json" else rows(OUT / name)))), "machine-readable warning missing")

    if errors:
        print("HR-V0 DXL current-envelope P0.1 check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0-DXL-CURRENT-ENV-P0.1 PASS: 3 axes / 8 invariants / 11 measurement steps / 14 holds OPEN")
    print("Raw 800 = 2.152 A nominal internal screen; external current limit and fuse values remain SELECTION REQUIRED")
    print("PRELIMINARY - no procurement, fabrication, connection, motion, energization, or safety credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
