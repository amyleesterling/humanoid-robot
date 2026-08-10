#!/usr/bin/env python3
"""Fail-closed validation for the R207 observation compute-harness candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/harness/hr-v0-observation-compute-harness-p0.1"
WEB = ROOT / "release/hr-v0/observation-compute-harness-p0.1"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
P116 = ROOT / "electrical/kicad/project-button-v3-p1.16-observation-candidate"
IDENTIFIER = "HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1"
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

    expected = {"README.md", "SOURCE-MANIFEST.csv", "acceptance-matrix.csv", "bundle-area-screen.csv", "compute-harness.svg", "conductor-schedule.csv", "electrical-budget-screen.csv", "harness-bom.csv", "index.html", "interface-control.csv", "package-status.json", "route-length-calculation.csv", "selection-holds.csv", "source-register.csv", "termination-process.csv"}
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
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R207", "package identity changed")
    for key, value in {"conductor_rows": 6, "interface_rows": 6, "source_rows": 9, "selection_holds": 13, "acceptance_rows": 13}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(status.get("digital_mapping_complete") is True, "digital mapping is not recorded complete")
    need(abs(status.get("rounded_centerline_screen_mm", 0) - round(335.4 + 2 * (math.pi / 2 - 2) * 15, 1)) < 0.01, "rounded route calculation changed")
    need(abs(status.get("bare_bundle_area_screen_mm2", 0) - round(6 * math.pi * (1.6 / 2) ** 2, 2)) < 0.01, "bundle-area calculation changed")
    for key, value in status.items():
        if key.endswith("_authorized") or key in {"cut_lengths_selected", "physical_route_accepted", "duct_fill_accepted", "pi_external_load_accepted", "back_power_accepted", "harness_released", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "safety_credit"}:
            need(value is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")

    schedule = rows(ENG / "conductor-schedule.csv")
    expected_map = {
        "W14001": ("PI_3V3_CANDIDATE", "JLOGIC1:1", "JOBS1:1", "3051 RD005", "red"),
        "W14002": ("COMPUTE_0V", "JLOGIC1:2", "JOBS1:2", "3051 BK005", "black"),
        "W14003": ("OBS_SR1_PI", "JLOGIC1:3", "JOBS1:3", "3051 BL005", "blue"),
        "W14004": ("OBS_SRA1_PI", "JLOGIC1:4", "JOBS1:4", "3051 OR005", "orange"),
        "W14005": ("OBS_K1_PI", "JLOGIC1:5", "JOBS1:5", "3051 VI005", "violet"),
        "W14006": ("OBS_K2_PI", "JLOGIC1:6", "JOBS1:6", "3051 WH005", "white"),
    }
    need(len(schedule) == 6 and {row["wire_number"] for row in schedule} == set(expected_map), "six-wire membership changed")
    for row in schedule:
        expected_row = expected_map.get(row["wire_number"])
        if expected_row:
            net, start, end, part, color = expected_row
            need((row["net"], row["from"], row["to"]) == (net, start, end), f"interface mapping changed: {row['wire_number']}")
            need(part in row["wire_candidate"] and row["color"] == color, f"wire/color candidate changed: {row['wire_number']}")
        need(row["cut_length_mm"] == "SELECTION REQUIRED", f"cut length prematurely selected: {row['wire_number']}")
        need(row["termination"] == "direct-stripped flexible conductor; no ferrule candidate", f"termination candidate changed: {row['wire_number']}")
        need(row["warning"] == WARNING, f"warning changed: {row['wire_number']}")

    original = rows(R204 / "harness-interface.csv")
    need(len(original) == 6, "R204 harness source no longer has six rows")
    original_map = {(row["net"], row["from"].replace(".", ":"), row["to"].replace(".", ":"), row["stock_mpn"].removeprefix("Belden "), row["color"].lower()) for row in original}
    package_map = {(row["net"], row["from"], row["to"], row["wire_candidate"].removeprefix("Belden "), row["color"]) for row in schedule}
    need(package_map == original_map, "R207 schedule differs from R204 source interface")
    p116 = rows(P116 / "connector-schedule.csv")
    p116_map = {(row["reference"], row["terminal"], row["net"]) for row in p116 if row["reference"] in {"OBS1", "PIOBS1"}}
    for _, net, start, end, _, _, _ in [(row["wire_number"], row["net"], row["from"], row["to"], "", "", "") for row in schedule]:
        need(("OBS1", start, net) in p116_map and ("PIOBS1", end, net) in p116_map, f"P1.16 native interface parity missing: {net}")

    process = rows(ENG / "termination-process.csv")
    need(len(process) == 2 and {row["end"] for row in process} == {"R202 JLOGIC1", "R204 JOBS1"}, "both-end process rows changed")
    for row in process:
        need("5 mm" in row["candidate_preparation"] and row["torque"] == "0.22-0.25 N m" and row["candidate_conductors_per_clamp"] == "one", f"termination envelope changed: {row['end']}")
        need("support PCB terminal" in row["candidate_preparation"], f"terminal support instruction missing: {row['end']}")
    load = rows(ENG / "electrical-budget-screen.csv")
    need(len(load) == 1 and load[0]["r202_load_screen"] == "<=5.0 mA calculation screen", "R202 load screen changed")
    need(load[0]["pi_external_load_approval"] == "NOT ESTABLISHED" and load[0]["back_power_behavior"] == "NOT ESTABLISHED" and load[0]["cable_drop"].startswith("SELECTION REQUIRED"), "load/drop/back-power boundary weakened")
    bundle = rows(ENG / "bundle-area-screen.csv")
    need(len(bundle) == 1 and bundle[0]["duct_fill_percent"] == "SELECTION REQUIRED" and "NOT A DUCT-FILL RESULT" in bundle[0]["state"], "bare-area screen was misrepresented as duct fill")

    source = rows(ENG / "source-register.csv")
    for token in ("1751280", "revision 0.118 dated 2026-06-30", "RD005/BK005/BL005/OR005/VI005/WH005"):
        need(any(token in " ".join(row.values()) for row in source), f"primary-source evidence missing: {token}")
    for row in source:
        if row["manufacturer"] == "Project Button":
            path = ROOT / row["uri"]
            need(path.is_file(), f"controlled source missing: {row['uri']}")
            need(status["source_hashes"].get(row["document"]) == digest(path), f"controlled source hash mismatch: {row['document']}")

    holds = rows(ENG / "selection-holds.csv")
    acceptance = rows(ENG / "acceptance-matrix.csv")
    need(len(holds) == 13 and all(row["state"].startswith("OPEN") and row["warning"] == WARNING for row in holds), "all 13 holds must remain open")
    need(len(acceptance) == 13 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "all 13 acceptance rows must remain unexecuted/open")

    page = (WEB / "index.html").read_text(encoding="utf-8")
    svg = (WEB / "compute-harness.svg").read_text(encoding="utf-8")
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        failures.append(f"compute-harness.svg is not valid XML: {exc}")
    for token in ("font:clamp(16px", "font-size:14px", WARNING, "Six exact conductors", "source load screen—not Pi approval", "../../../electrical/"):
        need(token in page or token in svg, f"web guide token missing: {token}")
    need("font-size:13px" not in page and "font-size:12px" not in page, "web interface text was reduced below 14 px")

    if failures:
        print(f"{IDENTIFIER} FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS")
    print("  exact six-wire R202/R204/P1.16 mapping and both-end terminal process envelope")
    print("  cut length, duct fill, Pi load/back-power and 13 acceptance results remain open")
    print("  no procurement, fabrication, connection, powered-test, motion, safety or energization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
