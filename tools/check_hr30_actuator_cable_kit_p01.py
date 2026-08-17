#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 actuator cable-kit candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_actuator_cable_kit_p01.py"
WARNING = "PRELIMINARY - UNBUILT ACTUATOR CABLE-KIT CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


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
    connectors = rows(OUT / "connector-family-disposition.csv")
    axes = rows(OUT / "axis-power-cable-candidate.csv")
    data = rows(OUT / "data-cable-candidate.csv")
    cavities = rows(OUT / "connector-cavity-population.csv")
    tests = rows(OUT / "inspection-test-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "actuator-cable-kit-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 17 and len(connectors) == 4, "source/connector coverage drift")
    need(len(axes) == 25 and len({r["axis_id"] for r in axes}) == 25, "25 unique axis candidates required")
    need(len(data) == 7 and len(tests) == 12 and len(holds) == 11, "candidate/test/hold coverage drift")
    need(len(cavities) == 159 and len({r["cavity_id"] for r in cavities}) == 159, "159 unique cavity records required")
    all_rows = sources + connectors + axes + data + cavities + tests + holds
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for r in all_rows), "execution/warning overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in tests), "test execution overclaim")

    local_sources = sources[:4]
    need(all(r["sha256"] == sha(ROOT / r["official_url_or_path"]) for r in local_sources), "local source hash drift")
    need(any(r["candidate_housing"] == "JST EHR-4" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "RS-485 connector family missing")
    need(any(r["candidate_housing"] == "JST EHR-3" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "TTL connector family missing")
    need(any("LOW-INSERTION-FORCE" in r["disposition"] and "REJECTED" in r["disposition"] for r in connectors), "vibration contact disposition missing")

    cap_sum = sum(float(r["candidate_internal_limit_a"]) for r in axes)
    stall_sum = sum(float(r["published_stall_endpoint_a"]) for r in axes)
    need(abs(cap_sum - 46.67779) < 1e-6 and abs(stall_sum - 71.88) < 1e-9, "current boundaries drift")
    need(all(float(r["candidate_internal_limit_a"]) <= 2.499010 + 1e-9 for r in axes), "per-axis cap exceeds frozen candidate")
    need(all(r["stall_is_normal_demand"] == "NO" for r in axes), "stall endpoint promoted to demand")
    need(all("Alpha Wire 3051" in r["power_pair_test_coupon_candidate"] and "CF130.03.02.UL" in r["power_pair_test_coupon_candidate"] and "CF9.UL.02.02 REJECTED" in r["power_pair_test_coupon_candidate"] for r in axes), "static/dynamic wire candidate split drift")
    need(all("0.33 mm2" in r["jst_eh_published_conductor_range"] and "STATIC CANDIDATE PASS" in r["wire_contact_geometric_compatibility"] and "WRITTEN-DISPOSITION HOLD" in r["wire_contact_geometric_compatibility"] for r in axes), "wire/contact candidate boundary missing")
    need(all("AWG22" in r["connector_current_evidence"] and r["current_capacity_disposition"].startswith("OPEN") for r in axes), "ampacity limitation overclaimed")
    need(all(r["branch_protection"] == "SELECTION REQUIRED" and r["selection_state"].endswith("NOT RELEASED") for r in axes), "physical selection overclaimed")
    for r in axes:
        cap = float(r["candidate_internal_limit_a"])
        length_m = float(r["round_trip_planning_length_mm"]) / 1000.0
        resistance = 0.079 * length_m
        need(abs(float(r["loop_resistance_20c_planning_ohm"]) - resistance) < 5.1e-7, f"loop resistance drift: {r['axis_id']}")
        need(abs(float(r["voltage_drop_20c_at_candidate_cap_v"]) - cap * resistance) < 5.1e-7, f"voltage-drop drift: {r['axis_id']}")
        need(abs(float(r["conductor_loss_20c_at_candidate_cap_w"]) - cap * cap * resistance) < 5.1e-7, f"conductor-loss drift: {r['axis_id']}")
        need("REJECTED CF9 PREDECESSOR" in r["calculation_boundary"] and "REJECTED CF9.UL.02.02 PREDECESSOR" in r["calculation_material"], f"planning comparison boundary missing: {r['axis_id']}")
    need(abs(max(float(r["voltage_drop_20c_at_candidate_cap_v"]) for r in axes) - 0.090851) < 1e-6, "maximum planning drop drift")
    need(abs(max(float(r["conductor_loss_20c_at_candidate_cap_w"]) for r in axes) - 0.181582) < 1e-6, "maximum planning loss drift")

    counts = Counter(r["connector_role"] for r in cavities)
    need(counts == Counter({"ACTUATOR INPUT": 94, "DATA-ONLY OUTGOING": 65}), "input/outgoing cavity coverage drift")
    empty = [r for r in cavities if r["required_population"] == "EMPTY"]
    need(len(empty) == 34 and all(r["pin"] in {"1", "2"} and r["connector_role"] == "DATA-ONLY OUTGOING" for r in empty), "outgoing GND/VDD empty rule drift")
    need(all(r["actual_population"] == "NOT INSPECTED" for r in cavities), "physical inspection overclaim")
    incoming = [r for r in cavities if r["connector_role"] == "ACTUATOR INPUT"]
    need(sum(r["signal"] == "VDD" for r in incoming) == 25 and sum(r["signal"] == "GND" for r in incoming) == 25, "individual input power coverage drift")
    need(all(r["disposition"] == "REJECT" for r in data if "ROBOTIS" in r["candidate"]), "standard ROBOTIS powered daisy cable not rejected")
    need(any(r["candidate"] == "igus CFBUS.PVC.001" and r["disposition"] == "TEST-COUPON CANDIDATE" and "150 ohm" in r["published_construction"] for r in data), "RS-485 test-coupon candidate missing")
    need(any(r["candidate"] == "Alpha Wire 86202" and r["disposition"] == "REJECT FOR RS-485 CANDIDATE" for r in data), "87-ohm RS-485 rejection missing")
    need(any(r["hold_id"] == "ACK-H11" and "omit GND" in r["unresolved_item"] for r in holds), "signal-reference architecture hold missing")

    need(status["cf9_jst_cross_section_geometry_compatible"] is True, "legacy geometric evidence not recorded")
    need(status["cf9_power_candidate_rejected"] and status["static_alpha_3051_coupon_candidate_defined"] and status["dynamic_cf130_coupon_candidate_defined"], "power-wire disposition missing")
    need(abs(status["maximum_planning_voltage_drop_20c_at_candidate_cap_v"] - 0.090851) < 1e-6, "status max drop drift")
    for key in ["cf9_current_capacity_released", "cf9_route_life_verified", "power_cable_selected", "data_cable_selected", "crimp_process_selected", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["current_caps_propagated"] and status["canonical_jst_order_code_family_bound"], "material advancement missing")
    need(status["built_cable_count"] == status["executed_test_count"] == 0, "physical evidence overclaim")

    need((OUT / "actuator-cable-kit-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "actuator-cable-kit.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1480px" in page, "web legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:34px" in svg, "drawing legibility drift")
    need("The 25 actuator feeds now separate static and dynamic 22 AWG candidates" in page and "Do not crimp or connect either candidate" in page, "guide purpose/warning drift")
    need("Alpha Wire 3051" in page and "CF130.03.02.UL" in page and "CF9.UL.02.02 is rejected for actuator power" in (OUT / "README.md").read_text(encoding="utf-8"), "power-wire candidate guide drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("HR30-ACTUATOR-CABLE-KIT-P01-START" in root_page and "0.091 V" in root_page, "root guide integration missing")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-START") == 1 and root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-END") == 1, "cable-kit README marker drift")
    need(root_readme.count("HR30-AXIS-COMMISSION-START") == 1 and root_readme.count("HR30-AXIS-COMMISSION-END") == 1, "axis-commissioning README marker drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["actuator_cable_kit_axis_count"] == 25 and root_status["actuator_cable_kit_cavity_record_count"] == 159, "root status integration missing")
    need(root_status["actuator_cable_kit_current_caps_propagated"] and root_status["actuator_power_cable_20c_planning_calculated"] and not root_status["actuator_power_cable_hot_ampacity_verified"], "root advancement/thermal boundary drift")
    need(not root_status["energization_authority"], "root authority drift")
    print("PASS: HR-30 actuator cable kit rejects CF9 power credit, binds separate static/dynamic 22 AWG coupon candidates to all 25 feeds, and retains predecessor calculations only as bounded comparison evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
