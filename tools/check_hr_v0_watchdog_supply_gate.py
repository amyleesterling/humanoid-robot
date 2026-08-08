"""Fail-closed validation for the HR-V0 watchdog supply-gate correction."""

from __future__ import annotations

import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "safety" / "hr-v0-watchdog-supply-gate-p0.1"
V3 = ROOT / "electrical" / "kicad" / "project-button-v3"
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.5"
CANONICAL = ROOT / "safety" / "hr-v0-watchdog-boundary-fmea.csv"
WARNING = "PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    expected = {
        "exact-path-register.csv": (14, "path_id"),
        "topology-option-register.csv": (4, "option_id"),
        "contact-load-screen.csv": (7, "screen_id"),
        "separation-control-register.csv": (12, "control_id"),
        "open-decision-register.csv": (10, "hold_id"),
        "source-register.csv": (8, "source_id"),
        "failure-mode-register.csv": (32, "fmea_id"),
        "fault-injection-matrix.csv": (28, "case_id"),
    }
    loaded: dict[str, list[dict[str, str]]] = {}
    for name, (count, key) in expected.items():
        path = OUT / name
        if not path.is_file():
            errors.append(f"missing {name}")
            continue
        data = rows(path)
        loaded[name] = data
        if len(data) != count or len({row.get(key) for row in data}) != count:
            errors.append(f"{name} expected {count} unique rows")
        for row in data:
            if row.get("warning") != WARNING:
                errors.append(f"{name} {row.get(key)} warning mismatch")

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else {}
    for key, expected_value in {
        "revision": "HR-V0-WD-SUPPLY-P0.1",
        "configuration": "Electrical V3-P1.13 / PCB-P0.5 / HR-V0-CP-P0.5",
        "path_count": 14,
        "fmea_count": 32,
        "fault_case_count": 28,
        "separation_control_count": 12,
        "open_decision_count": 10,
        "df01_safety_credit": "ZERO",
        "encoded_internal_kwd_to_estop_return_path_removed": True,
        "physical_noninterference_proved": False,
        "physical_test_executed": False,
        "qualified_review_executed": False,
        "energization_authorized": False,
    }.items():
        if status.get(key) != expected_value:
            errors.append(f"status {key} expected {expected_value!r}, got {status.get(key)!r}")

    wire_text = (V3 / "wire-number-table.csv").read_text(encoding="utf-8-sig")
    net_text = (V3 / "net-schedule.csv").read_text(encoding="utf-8-sig")
    panel_text = (PANEL / "stationary-wire-schedule.csv").read_text(encoding="utf-8-sig")
    route_text = (PANEL / "supply-gate-routing-register.csv").read_text(encoding="utf-8-sig")
    combined = wire_text + net_text + panel_text + route_text
    for prohibited in ("WD1_SAFETY_IN", "WD2_SAFETY_IN"):
        if prohibited in combined:
            errors.append(f"obsolete injection-prone net remains: {prohibited}")
    for required in (
        "S0,R-2,CH1 RIGHT NC MARK 2,SR1_S12",
        "S0,L-2,CH2 LEFT NC MARK 2,SR1_S22",
        "SR1,A1,24V SUPPLY,SR1_A1_WD_GATED",
        "KWD1,14,SR1 SUPPLY GATE STAGE 1,WD_SUPPLY_INTERMEDIATE",
        "KWD2,11,SR1 SUPPLY GATE STAGE 1,WD_SUPPLY_INTERMEDIATE",
        "KWD2,14,SR1 A1 GATED SUPPLY,SR1_A1_WD_GATED",
        "KWD1:14 -> KWD2:11",
        "KWD2:14 -> SR1:A1",
    ):
        if required not in combined:
            errors.append(f"current ECAD/panel topology omits: {required}")

    options = {row.get("option_id"): row for row in loaded.get("topology-option-register.csv", [])}
    if options.get("OPT-001", {}).get("decision") != "REJECTED":
        errors.append("old KWD-in-input topology is not explicitly rejected")
    if options.get("OPT-004", {}).get("decision") != "SELECTED CANDIDATE":
        errors.append("SR1:A1 supply gate is not selected only as a candidate")

    fmea = loaded.get("failure-mode-register.csv", [])
    canonical = rows(CANONICAL) if CANONICAL.is_file() else []
    if fmea and canonical:
        package_core = [{key: value for key, value in row.items() if key != "warning"} for row in fmea]
        if package_core != canonical:
            errors.append("package FMEA and canonical FMEA differ")
    fmea_by_id = {row.get("fmea_id"): row for row in fmea}
    for fid in ("WDF-012", "WDF-013", "WDF-014", "WDF-015", "WDF-016"):
        row = fmea_by_id.get(fid, {})
        if row.get("safe_by_design") != "conditional" or "P1.13" not in row.get("sf01_effect", "") and fid != "WDF-016":
            errors.append(f"{fid} lacks current conditional topology disposition")
        if row.get("status") != "open":
            errors.append(f"{fid} is not controlled open")
    if fmea_by_id.get("WDF-008", {}).get("safe_by_design") != "no" or "can be impaired" not in fmea_by_id.get("WDF-008", {}).get("sf01_effect", ""):
        errors.append("external S0-return harness bypass case WDF-008 must remain open")
    if any(row.get("status") != "open" for row in fmea):
        errors.append("all 32 FMEA cases must remain open")

    for row in loaded.get("fault-injection-matrix.csv", []):
        if row.get("execution_state") != "NOT EXECUTED" or row.get("authorization") != "NOT AUTHORIZED":
            errors.append(f"{row.get('case_id')} appears executed or authorized")
    for row in loaded.get("separation-control-register.csv", []):
        if row.get("release_state") != "NOT RELEASED" or row.get("execution_state") != "NOT EXECUTED":
            errors.append(f"{row.get('control_id')} appears released or executed")
    for row in loaded.get("open-decision-register.csv", []):
        if row.get("state") != "SELECTION REQUIRED":
            errors.append(f"{row.get('hold_id')} appears closed")

    svg_path = OUT / "watchdog-supply-gate.svg"
    if svg_path.is_file():
        try:
            ET.parse(svg_path)
        except ET.ParseError as exc:
            errors.append(f"SVG parse error: {exc}")
        svg = svg_path.read_text(encoding="utf-8")
        fonts = [int(value) for value in re.findall(r"font-size:(\d+)px", svg)]
        if not fonts or min(fonts) < 16:
            errors.append(f"SVG functional text below 16px: {fonts}")
        for phrase in ("ZERO SAFETY CREDIT", "Physical noninterference: NOT PROVED", "NOT APPROVED FOR FABRICATION, ENERGIZATION OR MOTION"):
            if phrase not in svg:
                errors.append(f"SVG omits {phrase}")
    page = (OUT / "index.html").read_text(encoding="utf-8") if (OUT / "index.html").is_file() else ""
    for phrase in ("32", "28", "10", "Filter all tables", "encoded internal KWD-to-E-stop-return injection path"):
        if phrase not in page:
            errors.append(f"interactive guide omits {phrase}")
    css_sizes = [int(value) for value in re.findall(r"font-size:(\d+)px", page)]
    if any(size < 16 for size in css_sizes):
        errors.append(f"interactive guide contains text below 16px: {css_sizes}")

    if errors:
        print("HR-V0 watchdog supply-gate check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 watchdog supply-gate check passed: 14 paths; 32 open FMEA cases; 28 unexecuted fault cases")
    print("Encoded KWD-to-E-stop-return injection removed; physical noninterference and qualified review remain open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
