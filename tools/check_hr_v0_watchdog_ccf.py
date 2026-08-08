"""Validate the HR-V0 watchdog dependent-failure package against V3 source."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "safety" / "hr-v0-watchdog-ccf-p0.1"
NETS = ROOT / "electrical" / "kicad" / "project-button-v3" / "net-schedule.csv"
CONNECTORS = ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv"
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.4" / "backplate-layout.csv"
WARNING = "PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    expected = {
        "exact-path-register.csv": (18, "path_id"),
        "failure-mode-register.csv": (32, "fmea_id"),
        "common-cause-group-register.csv": (12, "ccf_id"),
        "fault-injection-matrix.csv": (28, "case_id"),
        "separation-control-register.csv": (16, "control_id"),
        "open-decision-register.csv": (8, "decision_id"),
        "source-register.csv": (8, "source_id"),
    }
    loaded: dict[str, list[dict[str, str]]] = {}
    for name, (count, key) in expected.items():
        path = OUT / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        data = rows(path)
        loaded[name] = data
        if len(data) != count or len({r.get(key) for r in data}) != count:
            errors.append(f"{name} expected {count} unique rows")
        for row in data:
            if row.get("warning") != WARNING:
                errors.append(f"{name} {row.get(key)} warning mismatch")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {
        "exact_path_count": 18,
        "failure_mode_count": 32,
        "common_cause_group_count": 12,
        "fault_case_count": 28,
        "separation_control_count": 16,
        "open_decision_count": 8,
        "df01_safety_credit": "ZERO",
        "sf01_sf03_allocation": "SELECTION REQUIRED",
        "current_topology_noninterference_proved": False,
        "physical_test_executed": False,
        "qualified_review_executed": False,
        "energization_authorized": False,
    }.items():
        if status.get(key) != value:
            errors.append(f"status {key} expected {value!r}")
    net_text = NETS.read_text(encoding="utf-8-sig")
    connector_text = CONNECTORS.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    historical_path_text = (OUT / "exact-path-register.csv").read_text(encoding="utf-8-sig")
    for token in ("WD1_SAFETY_IN", "WD2_SAFETY_IN"):
        if token not in historical_path_text:
            errors.append(f"historical R86 path register missing {token}")
        if token in net_text:
            errors.append(f"current V3 source still contains superseded R86 net {token}")
    for token in ("SR1_S12", "SR1_S22", "SR1_A1_WD_GATED", "WD_SUPPLY_INTERMEDIATE", "ARM_AFTER_S2", "WD1_COIL_N", "WD2_COIL_N", "WD1_NC_24V", "WD2_NC_24V"):
        if token not in net_text:
            errors.append(f"V3 net schedule missing {token}")
    for token in ("KWD1,A1", "KWD1,21", "KWD1,14", "KWD2,A1", "KWD2,21", "KWD2,14"):
        if token not in connector_text:
            errors.append(f"V3 connector schedule missing {token}")
    for token in ("BP-005", "BP-006", "BP-007", "BP-008", "BP-012"):
        if token not in panel_text:
            errors.append(f"panel allocation missing {token}")
    failures = loaded.get("failure-mode-register.csv", [])
    by_id = {r.get("fmea_id"): r for r in failures}
    for fid in ("WDF-012", "WDF-013", "WDF-014", "WDF-015", "WDF-016"):
        if "potential" not in by_id.get(fid, {}).get("sf01_sf03_effect", "").lower():
            errors.append(f"{fid} must preserve potential SF-01 impairment")
    for row in failures:
        if row.get("status") != "OPEN" or not row.get("required_verification"):
            errors.append(f"{row.get('fmea_id')} is not controlled open")
    for row in loaded.get("common-cause-group-register.csv", []):
        if row.get("accepted_fault_exclusion") != "NONE" or row.get("status") != "OPEN":
            errors.append(f"{row.get('ccf_id')} falsely accepts a fault exclusion")
    for row in loaded.get("fault-injection-matrix.csv", []):
        if row.get("execution_state") != "NOT EXECUTED" or row.get("authorization") != "NOT AUTHORIZED":
            errors.append(f"{row.get('case_id')} falsely appears executed/authorized")
    result_rows = rows(ROOT / "tests" / "forms" / "hr-v0-watchdog-fault-injection-template.csv")
    inspection_rows = rows(ROOT / "tests" / "forms" / "hr-v0-watchdog-separation-inspection-template.csv")
    if len(result_rows) != 28 or any(r.get("result") != "NOT EXECUTED" for r in result_rows):
        errors.append("fault-injection template must retain 28 unexecuted cases")
    if len(inspection_rows) != 16 or any(r.get("inspection_state") != "NOT EXECUTED" for r in inspection_rows):
        errors.append("separation template must retain 16 unexecuted controls")
    html = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "watchdog-boundary.svg").read_text(encoding="utf-8")
    for phrase in ("A short to 14 could inject voltage", "DF-01 SAFETY CREDIT: ZERO", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        if phrase not in html:
            errors.append(f"interactive guide missing {phrase}")
    if "font-size:18px" not in svg or "A1/21-to-14 injection path: OPEN BLOCKER" not in svg:
        errors.append("SVG readability/blocker label missing")
    if errors:
        print("HR-V0 watchdog CCF check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 watchdog CCF check passed: 18 paths; 32 failure modes; 12 CCF groups; 28 unexecuted cases; 16 separation controls")
    print("DF-01 safety credit ZERO; topology non-interference NOT PROVED; 8 decisions remain open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
