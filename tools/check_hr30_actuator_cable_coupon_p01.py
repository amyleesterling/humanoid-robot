#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 actuator-cable coupon package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-coupon-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_actuator_cable_coupon_p01.py"
WARNING = "PRELIMINARY - UNBUILT CABLE COUPON PLAN - NOT APPROVED FOR PROCUREMENT, PRODUCTION CUTTING, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    sources = rows(OUT / "primary-source-register.csv")
    tools = rows(OUT / "tooling-candidate-register.csv")
    bom = rows(OUT / "coupon-bom.csv")
    specimens = rows(OUT / "coupon-specimen-register.csv")
    traveler = rows(OUT / "coupon-build-traveler.csv")
    measurements = rows(OUT / "coupon-measurement-record.csv")
    routes = rows(OUT / "precut-route-register.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "coupon-status.json").read_text(encoding="utf-8"))

    need((len(sources), len(tools), len(bom), len(specimens), len(traveler), len(measurements), len(routes), len(holds)) == (20, 4, 11, 11, 16, 12, 25, 14), "package coverage drift")
    need(len({r["axis_id"] for r in routes}) == 25, "25 unique axis routes required")
    all_controlled = sources + tools + bom + specimens + traveler + measurements + routes + holds
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for r in all_controlled), "execution/warning overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["result"] == "NOT EXECUTED" and r["recorded_value"] == "NONE" for r in traveler), "traveler execution overclaim")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" and "SELECTION REQUIRED" in r["acceptance_limit"] for r in measurements), "measurement invented or executed")
    need(all(r["is_production_cut_length"] == "NO" and r["built_quantity"] == r["tested_quantity"] == "0" for r in specimens), "specimen/production boundary drift")
    need(all(r["final_cut_length_mm"].startswith("SELECTION REQUIRED") and r["mockup_pull_string_length_mm"] == "MEASURE ON ASSEMBLED ROBOT" and r["precut_action"] == "DO NOT CUT PRODUCTION CABLE" for r in routes), "production cut length falsely released")
    need(all(r["route_measurement_state"] == "NOT EXECUTED" for r in routes), "route measurement overclaim")

    local = [r for r in sources if r["publisher"] == "Project Button"]
    need(len(local) == 7, "local source coverage drift")
    need(all(r["sha256"] == sha(ROOT / r["official_url_or_path"]) for r in local), "local input hash drift")
    need(any(r["candidate_tool"] == "JST YC-260R" and r["terminal_or_interface"] == "JST BEH-001T-P0.6" for r in tools), "loose-piece tool path missing")
    need(any(r["candidate_tool"] == "JST YRS-260" and r["terminal_or_interface"] == "JST SEH-001T-P0.6" for r in tools), "strip-terminal tool path missing")
    need(any(r["candidate_tool"] == "JST EJ-PH" for r in tools), "extraction tool missing")
    need(any(r["order_code"] == "CF9.UL.02.02" and "not an actuator-power candidate" in r["description"] for r in bom), "24 AWG predecessor rejection missing")
    need(any(r["order_code"] == "3051" and r["manufacturer"] == "Alpha Wire" for r in bom), "static 22 AWG coupon candidate missing")
    need(any(r["order_code"] == "CF130.03.02.UL" and r["manufacturer"] == "igus" for r in bom), "dynamic 22 AWG coupon candidate missing")
    need(any(r["order_code"] == "430250200 + 430300001" for r in bom), "moving-side Micro-Fit coupon parts missing")
    need(any(r["order_code"] == "430200200 + 430310001" for r in bom), "panel-side Micro-Fit coupon parts missing")
    need(any(r["specimen_id"] == "ACC-C10" and "complete fixed-transition" in r["purpose"] for r in specimens), "complete transition coupon missing")
    need(any(r["specimen_id"] == "ACC-C11" and "flex-isolation" in r["purpose"] for r in specimens), "JST pigtail isolation coupon missing")
    need(any(r["order_code"] == "YC-260R" for r in bom), "prototype crimp tool missing")
    need(any(r["order_code"] == "BEH-001T-P0.6" for r in bom), "loose contact missing")
    need(any("pull-force acceptance" in r["unresolved_item"] for r in holds), "crimp acceptance hold missing")
    need(any("production cut lengths" in r["unresolved_item"] for r in holds), "route-length hold missing")
    need(any(r["hold_id"] == "ACC-H12" and "dimensioned bracket parts" in r["unresolved_item"] and "tolerance-aware integration" in r["unresolved_item"] for r in holds), "transition-bracket successor hold missing")

    need(status["loose_piece_tooling_path_bound"] and status["strip_terminal_tooling_path_bound"], "tooling advancement missing")
    need(status["built_coupon_count"] == status["executed_test_count"] == status["measured_robot_route_count"] == status["released_final_cut_length_count"] == 0, "physical evidence overclaim")
    need(status["cf9_power_candidate_rejected"] and status["static_22awg_candidate_defined"] and status["dynamic_22awg_candidate_defined"], "power-wire candidate disposition missing")
    need(status["complete_fixed_transition_coupon_defined"] and status["direct_cf130_to_jst_eh_crimp_rejected"], "complete transition disposition missing")
    need(status["transition_brackets_dimensioned"] and status["transition_bracket_placement_count"] == 25, "transition-bracket binding missing")
    for key in ["alpha_3051_crimp_process_selected", "cf130_crimp_process_selected", "cf9_specific_crimp_process_selected", "procurement_authority", "production_cutting_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")

    need((OUT / "actuator-cable-coupon-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "coupon-architecture.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1100px" in page, "web legibility/overflow drift")
    need("font-size=\"18\"" in svg and "font-size=\"34\"" in svg, "drawing legibility drift")
    need("Build and break coupons before cutting robot cables" in page and "DO NOT CUT PRODUCTION CABLE" in page, "guide purpose/warning drift")
    need("Test the complete transition" in page and "430250200 / 430300001" in page and "430200200 / 430310001" in page and "CF9.UL.02.02 is 24 AWG" in page, "complete transition guide missing")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_page.count("HR30-ACTUATOR-CABLE-COUPON-P01-START") == root_page.count("HR30-ACTUATOR-CABLE-COUPON-P01-END") == 1, "root web integration missing")
    need(root_readme.count("HR30-ACTUATOR-CABLE-COUPON-P01-README-START") == root_readme.count("HR30-ACTUATOR-CABLE-COUPON-P01-README-END") == 1, "root README integration missing")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["actuator_cable_coupon_route_measurement_count"] == 25 and root_status["actuator_cable_coupon_built_count"] == 0, "root status integration missing")
    need(root_status["actuator_cable_coupon_transition_brackets_dimensioned"] and root_status["actuator_cable_coupon_transition_bracket_placement_count"] == 25, "root bracket reconciliation missing")
    need(root_status["actuator_cable_final_cut_lengths_selected"] is False and root_status["energization_authority"] is False, "root authority/release drift")
    print("PASS: HR-30 cable coupon package binds the complete CF130/Micro-Fit/Alpha-3051/JST transition, 11 specimen families and 25 route measurements; zero coupons/tests/cut lengths are released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
