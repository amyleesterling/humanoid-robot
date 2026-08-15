#!/usr/bin/env python3
"""Fail-closed checks for the R208 observation compute-power boundary."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/interfaces/hr-v0-observation-compute-power-boundary-p0.1"
WEB = ROOT / "release/hr-v0/observation-compute-power-boundary-p0.1"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R203 = ROOT / "electrical/interfaces/hr-v0-runtime-observation-pi-pinmap-p0.1"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
R207 = ROOT / "electrical/harness/hr-v0-observation-compute-harness-p0.1"
P116 = ROOT / "electrical/kicad/project-button-v3-p1.16-observation-candidate"
IDENTIFIER = "HR-V0-OBSERVATION-COMPUTE-POWER-BOUNDARY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {
        "README.md", "SOURCE-MANIFEST.csv", "acceptance-matrix.csv", "fault-matrix.csv", "index.html",
        "load-budget.csv", "manufacturer-question-register.csv", "package-status.json", "power-boundary.svg",
        "power-state-matrix.csv", "selection-holds.csv", "signal-margin-screen.csv", "source-register.csv",
        "topology-register.csv",
    }
    for directory in (ENG, WEB):
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
        need(actual == expected, f"package membership changed: {directory}")
        manifest = rows(directory / "SOURCE-MANIFEST.csv")
        need({row["file"] for row in manifest} == expected - {"SOURCE-MANIFEST.csv"}, f"manifest membership changed: {directory.name}")
        for row in manifest:
            path = directory / row["file"]
            need(row["sha256"] == digest(path).upper(), f"manifest digest mismatch: {directory.name}/{row['file']}")
    for name in expected - {"SOURCE-MANIFEST.csv"}:
        need((ENG / name).read_bytes() == (WEB / name).read_bytes(), f"engineering/web mirror differs: {name}")

    status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R208", "package identity changed")
    for key, value in {"topology_rows": 5, "source_rows": 4, "power_state_rows": 7, "fault_rows": 8, "manufacturer_questions": 6, "selection_holds": 12, "acceptance_rows": 14}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(abs(status.get("steady_load_screen_ma", 0) - 5.0) < 0.001, "steady-load screen changed")
    need(abs(status.get("source_high_floor_screen_v", 0) - round(2.6 * 10 / 11, 3)) < 0.001, "source-high floor changed")
    need(abs(status.get("short_current_nominal_ma", 0) - 3.3) < 0.001, "nominal short-current screen changed")
    need(abs(status.get("short_current_rso_minus_1pct_ma", 0) - round(3.3 / 0.99, 3)) < 0.001, "tolerance short-current screen changed")
    need(status.get("ti_recommended_output_current_ma") == 3.0 and status.get("rso_fault_current_blocker") is True, "RSO blocker was weakened")
    for key, value in status.items():
        if key.endswith("_authorized") or key in {"pi_header_3v3_load_accepted", "pi_gpio_dc_limits_accepted", "signal_margin_accepted", "back_power_accepted", "partial_power_behavior_accepted", "rso_selection_released", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "safety_credit"}:
            need(value is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")

    r202_bom = rows(R202 / "bom.csv")
    bom_values = {row["reference"]: row["value"] for row in r202_bom}
    for ref in ("UOBS1", "UOBS2"):
        need("ISO1212DBQ" in bom_values.get(ref, ""), f"{ref} identity changed")
    for ref in ("RSO1", "RSO2", "RSO3", "RSO4"):
        need("1.00 kohm" in bom_values.get(ref, "") and "ERJ6ENF1001V" in bom_values.get(ref, ""), f"{ref} candidate changed")
    for ref in ("RPD1", "RPD2", "RPD3", "RPD4"):
        need("10.0 kohm" in bom_values.get(ref, "") and "ERJ6ENF1002V" in bom_values.get(ref, ""), f"{ref} candidate changed")

    topology = rows(ENG / "topology-register.csv")
    need(len(topology) == 5 and {row["path_id"] for row in topology} == {"PWR-01", "RET-01", "SIG-01", "ISO-01", "ABSENT-01"}, "topology register changed")
    native = (R202 / "validation/hr-v0-runtime-observation-carrier-p0.2.net").read_text(encoding="utf-8")
    for token in ("PI_3V3_CANDIDATE", "COMPUTE_0V", "OBS_SR1_PI", "OBS_SRA1_PI", "OBS_K1_PI", "OBS_K2_PI"):
        need(token in native, f"R202 native net missing: {token}")
    need('(name "5V")' not in native and '(name "+5V")' not in native and "PI_5V" not in native, "unexpected 5 V net entered R202 observation source")

    pinmap = json.loads((R203 / "pinmap-summary.json").read_text(encoding="utf-8"))
    need(pinmap.get("carrier_supply_physical_header_pin") == 17 and pinmap.get("carrier_return_physical_header_pin") == 20, "Pi supply/return allocation changed")
    expected_gpio = {"sr1_status": (22, 15), "sra1_status": (23, 16), "k1_status": (24, 18), "k2_status": (25, 22)}
    for name, (gpio, pin) in expected_gpio.items():
        entry = pinmap.get("observation_inputs", {}).get(name, {})
        need(entry.get("gpio") == gpio and entry.get("physical_header_pin") == pin and entry.get("active_high") is True, f"Pi mapping changed: {name}")
    r207 = rows(R207 / "conductor-schedule.csv")
    need({(row["wire_number"], row["net"], row["from"], row["to"]) for row in r207} == {
        ("W14001", "PI_3V3_CANDIDATE", "JLOGIC1:1", "JOBS1:1"),
        ("W14002", "COMPUTE_0V", "JLOGIC1:2", "JOBS1:2"),
        ("W14003", "OBS_SR1_PI", "JLOGIC1:3", "JOBS1:3"),
        ("W14004", "OBS_SRA1_PI", "JLOGIC1:4", "JOBS1:4"),
        ("W14005", "OBS_K1_PI", "JLOGIC1:5", "JOBS1:5"),
        ("W14006", "OBS_K2_PI", "JLOGIC1:6", "JOBS1:6"),
    }, "R207 harness mapping changed")

    budget = rows(ENG / "load-budget.csv")
    need(len(budget) == 6 and budget[-1]["result"] == "SELECTION REQUIRED" and budget[-1]["status"] == "BLOCKER", "Pi 5 header-load gap not held")
    margins = rows(ENG / "signal-margin-screen.csv")
    need(len(margins) == 5 and sum(row["disposition"].startswith("BLOCKER") for row in margins) == 2, "signal blocker rows changed")
    need(any(row["result"] == "3.300 mA" and "EXCEEDS" in row["disposition"] for row in margins), "nominal RSO hard-short blocker absent")
    need(any(row["result"] == "3.333 mA" and "MUST CHANGE" in row["disposition"] for row in margins), "tolerance RSO hard-short blocker absent")

    states = rows(ENG / "power-state-matrix.csv")
    need({row["state_id"] for row in states} == {"OFF", "FIELD_ONLY", "STANDBY", "RAMP", "ACTIVE_FIELD_OFF", "ACTIVE_FIELD_ON", "WARM_STANDBY"}, "power-state membership changed")
    need(all(row["authority"] in {"NONE", "DIAGNOSTIC ONLY"} and row["warning"] == WARNING for row in states), "power-state authority or warning weakened")
    need(any(row["state_id"] == "FIELD_ONLY" and "undetermined" in row["ti_output_basis"] and "NO-BACKFEED" in row["evidence_state"] for row in states), "field-only uncertainty lost")
    faults = rows(ENG / "fault-matrix.csv")
    need(len(faults) == 8 and any(row["fault_id"] == "FLT-04" and row["closure"].startswith("BLOCKER") for row in faults), "fault blocker absent")
    need(all(row["closure"].startswith(("OPEN", "BLOCKER")) and row["warning"] == WARNING for row in faults), "fault closure was overstated")

    sources = rows(ENG / "source-register.csv")
    for token in ("05 December 2024", "release 1.1; 07 November 2023", "SLLSEY7G; revised February 2025"):
        need(any(token in " ".join(row.values()) for row in sources), f"source revision missing: {token}")
    need(all(row["official_url"].startswith(("https://datasheets.raspberrypi.com/", "https://www.raspberrypi.com/", "https://www.ti.com/")) for row in sources), "non-primary source entered register")
    for name, expected_hash in status.get("source_hashes", {}).items():
        path_map = {
            "R202 BOM": R202 / "bom.csv", "R202 connector schedule": R202 / "connector-schedule.csv", "R202 load budget": R202 / "load-budget.csv",
            "R202 native netlist": R202 / "validation/hr-v0-runtime-observation-carrier-p0.2.net", "R203 pinmap summary": R203 / "pinmap-summary.json",
            "R204 connector schedule": R204 / "connector-schedule.csv", "R207 conductor schedule": R207 / "conductor-schedule.csv",
            "P1.16 connector schedule": P116 / "connector-schedule.csv",
        }
        need(name in path_map and expected_hash == digest(path_map[name]), f"controlled source hash mismatch: {name}")

    questions = rows(ENG / "manufacturer-question-register.csv")
    need(len(questions) == 6 and all(row["sent"] == "NO" and row["answer"] == "OPEN" and row["warning"] == WARNING for row in questions), "manufacturer questions must remain unsent/open")
    holds = rows(ENG / "selection-holds.csv")
    acceptance = rows(ENG / "acceptance-matrix.csv")
    need(len(holds) == 12 and all(row["state"].startswith("OPEN") and not row["evidence_uri"] and row["warning"] == WARNING for row in holds), "all 12 holds must remain open")
    need(len(acceptance) == 14 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["evidence_uri"] and not row["approver"] for row in acceptance), "all 14 acceptance rows must remain unexecuted/open")

    page = (WEB / "index.html").read_text(encoding="utf-8")
    svg = (WEB / "power-boundary.svg").read_text(encoding="utf-8")
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        failures.append(f"power-boundary.svg is not valid XML: {exc}")
    for token in ("font:clamp(16px", "font-size:14px", WARNING, "RSO candidate does not bound", "state-select", "addEventListener('change',render)", "0</b>physical acceptance results"):
        need(token in page or token in svg, f"web guide token missing: {token}")
    need("font-size:13px" not in page and "font-size:12px" not in page, "web interface text was reduced below 14 px")

    if failures:
        print(f"{IDENTIFIER} FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS")
    print("  exact R202/R203/R204/R207/P1.16 topology and source-bounded screens")
    print("  RSO hard-short current remains a BLOCKER; Pi 5 limits and all physical evidence remain open")
    print("  no procurement, fabrication, connection, powered-test, motion, safety or energization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
