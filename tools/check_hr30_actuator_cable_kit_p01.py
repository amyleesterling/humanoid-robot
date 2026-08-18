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
    transitions = rows(OUT / "actuator-power-transition-register.csv")
    data = rows(OUT / "data-cable-candidate.csv")
    cavities = rows(OUT / "connector-cavity-population.csv")
    references = rows(OUT / "bus-reference-register.csv")
    reference_tests = rows(OUT / "bus-reference-test-plan.csv")
    tests = rows(OUT / "inspection-test-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "actuator-cable-kit-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 29 and len(connectors) == 6, "source/connector coverage drift")
    need(len(axes) == 25 and len({r["axis_id"] for r in axes}) == 25, "25 unique axis candidates required")
    need(len(transitions) == 25 and {r["axis_id"] for r in transitions} == {r["axis_id"] for r in axes}, "25 transition candidates required")
    need(len(data) == 7 and len(tests) == 14 and len(holds) == 14, "candidate/test/hold coverage drift")
    need(len(cavities) == 159 and len({r["cavity_id"] for r in cavities}) == 159, "159 unique cavity records required")
    need(len(references) == 8 and len(reference_tests) == 8, "eight-bus reference architecture/test coverage required")
    all_rows = sources + connectors + axes + transitions + data + cavities + references + reference_tests + tests + holds
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for r in all_rows), "execution/warning overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in tests), "test execution overclaim")

    local_sources = [r for r in sources if r["publisher"] == "Project Button"]
    need(len(local_sources) == 10, "local source coverage drift")
    need(all(r["sha256"] == sha(ROOT / r["official_url_or_path"]) for r in local_sources), "local source hash drift")
    need(any(r["candidate_housing"] == "JST EHR-4" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "RS-485 connector family missing")
    need(any(r["candidate_housing"] == "JST EHR-3" and r["candidate_contact"] == "JST SEH-001T-P0.6" for r in connectors), "TTL connector family missing")
    need(any(r["candidate_housing"] == "Molex 430250200" and r["candidate_contact"] == "Molex 430300001" for r in connectors), "dynamic-side Micro-Fit candidate missing")
    need(any(r["candidate_housing"] == "Molex 430200200" and r["candidate_contact"] == "Molex 430310001" for r in connectors), "fixed-side Micro-Fit candidate missing")
    need(any("LOW-INSERTION-FORCE" in r["disposition"] and "REJECTED" in r["disposition"] for r in connectors), "vibration contact disposition missing")

    cap_sum = sum(float(r["candidate_internal_limit_a"]) for r in axes)
    stall_sum = sum(float(r["published_stall_endpoint_a"]) for r in axes)
    need(abs(cap_sum - 46.67779) < 1e-6 and abs(stall_sum - 71.88) < 1e-9, "current boundaries drift")
    need(all(float(r["candidate_internal_limit_a"]) <= 2.499010 + 1e-9 for r in axes), "per-axis cap exceeds frozen candidate")
    need(all(r["stall_is_normal_demand"] == "NO" for r in axes), "stall endpoint promoted to demand")
    need(all("Alpha Wire 3051" in r["power_pair_test_coupon_candidate"] and "CF130.03.02.UL" in r["power_pair_test_coupon_candidate"] and "430250200/430300001" in r["power_pair_test_coupon_candidate"] and "CF9.UL.02.02 REJECTED" in r["power_pair_test_coupon_candidate"] for r in axes), "moving/transition/pigtail candidate split drift")
    need(all("0.33 mm2" in r["jst_eh_published_conductor_range"] and "ALPHA 3051 TO JST/MICRO-FIT" in r["wire_contact_geometric_compatibility"] and "CORE-OD LIMIT REMAINS UNVERIFIED" in r["wire_contact_geometric_compatibility"] for r in axes), "wire/contact candidate boundary missing")
    need(all(r["dynamic_housing"] == "Molex 430250200" and r["fixed_panel_housing"] == "Molex 430200200" and "PANEL-MOUNT TRANSITION" in r["load_isolation"] and r["pigtail_length_mm"].startswith("SELECTION REQUIRED") for r in transitions), "fixed-side transition architecture drift")
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
    need(abs(max(float(r["voltage_drop_20c_at_candidate_cap_v"]) for r in axes) - 0.208594) < 1e-6, "maximum planning drop drift")
    need(abs(max(float(r["conductor_loss_20c_at_candidate_cap_w"]) for r in axes) - 0.423840) < 1e-6, "maximum planning loss drift")

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
    need(any(r["hold_id"] == "ACK-H11" and "single-point reference architecture" in r["unresolved_item"] and "PDU_COMMON_RET" in r["unresolved_item"] for r in holds), "signal-reference validation hold missing")
    need(any(r["hold_id"] == "ACK-H13" and "dimensioned bracket CAD" in r["unresolved_item"] and "production-body tolerance sweep" in r["unresolved_item"] for r in holds), "transition-bracket successor hold missing")

    need({r["bus_id"] for r in references} == {"RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM", "RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD"}, "reference bus set drift")
    rs = [r for r in references if r["protocol"].startswith("RS-485")]
    ttl = [r for r in references if r["protocol"].startswith("TTL")]
    need(len(rs) == 5 and len(ttl) == 3, "5 RS-485 / 3 TTL reference split required")
    need(all(r["interface_candidate"] == "ISOW1432DFMR" and "ISOLATED" in r["controller_isolation_state"] and "NOT GALVANICALLY" not in r["controller_isolation_state"] for r in rs), "RS-485 isolation candidate drift")
    need(all(r["interface_candidate"] == "SN74LVC1T45DCKR" and r["controller_isolation_state"] == "NOT GALVANICALLY ISOLATED" for r in ttl), "TTL non-isolated boundary drift")
    need(all(r["parallel_motor_return_path"] == "PROHIBITED" and r["inter_actuator_pin_1_rule"].startswith("EMPTY") and r["inter_actuator_pin_2_rule"].startswith("EMPTY") for r in references), "parallel-return prohibition drift")
    need(all("PDU_COMMON_RET" in r["single_reference_path"] and "DEDICATED POWER-PAIR" in r["actuator_reference_path"] for r in references), "single-point reference path missing")
    axis_by_bus = {bus: [a for a in axes if a["bus_id"] == bus] for bus in {r["bus_id"] for r in references}}
    for ref in references:
        drops = sorted((float(a["voltage_drop_20c_at_candidate_cap_v"]) / 2.0 for a in axis_by_bus[ref["bus_id"]]), reverse=True)
        pair = drops[0] + drops[1] if len(drops) > 1 else drops[0]
        need(abs(float(ref["max_star_to_axis_offset_screen_v"]) - drops[0]) < 5.1e-7, f"star offset screen drift: {ref['bus_id']}")
        need(abs(float(ref["max_pairwise_opposite_sign_offset_screen_v"]) - pair) < 5.1e-7, f"pair offset screen drift: {ref['bus_id']}")
        need("REJECTED-CF9 PREDECESSOR" in ref["screen_basis"] and ref["validation_state"].startswith("NOT EXECUTED"), f"reference screen promoted: {ref['bus_id']}")
    need({r["test_id"] for r in reference_tests} == {f"ACK-BRT{i:02d}" for i in range(1, 9)}, "reference test IDs drift")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in reference_tests), "reference test execution overclaim")

    need(status["cf9_jst_cross_section_geometry_compatible"] is True, "legacy geometric evidence not recorded")
    need(status["cf9_power_candidate_rejected"] and status["static_alpha_3051_coupon_candidate_defined"] and status["dynamic_cf130_coupon_candidate_defined"], "power-wire disposition missing")
    need(status["direct_cf130_to_jst_eh_crimp_rejected"] and status["microfit_fixed_transition_candidate_defined"] and status["microfit_fixed_transition_exact_order_codes_bound"], "transition disposition missing")
    need(status["transition_count"] == 25 and not status["microfit_cf130_core_od_verified"] and status["transition_brackets_dimensioned"] and status["transition_bracket_placement_count"] == 25, "transition evidence boundary drift")
    need(status["bus_reference_architecture_defined"] and status["bus_reference_count"] == 8 and status["bus_reference_star_node"] == "PDU_COMMON_RET", "bus-reference status missing")
    need(status["parallel_motor_return_path_prohibited"] and status["rs485_isolated_channel_count"] == 5 and status["ttl_nonisolated_channel_count"] == 3 and not status["bus_reference_validated"], "bus-reference validation boundary drift")
    need(abs(status["maximum_planning_voltage_drop_20c_at_candidate_cap_v"] - 0.208594) < 1e-6, "status max drop drift")
    need(abs(status["maximum_planning_conductor_loss_20c_at_candidate_cap_w"] - 0.423840) < 1e-6, "status max loss drift")
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
    need("All 25 actuator feeds now use a fixed-side transition candidate" in page and "Do not crimp or connect either candidate" in page, "guide purpose/warning drift")
    need("430250200" in page and "430200200" in page and "Alpha Wire 3051" in page and "CF130.03.02.UL" in page and "Direct CF130-to-JST crimping is rejected" in (OUT / "README.md").read_text(encoding="utf-8"), "power-transition guide drift")
    need("Reference current returns to one controlled star" in page and "bus-reference-register.csv" in page and "bus-reference-test-plan.csv" in page, "reference guide missing")
    reference_svg = (OUT / "bus-reference-architecture.svg").read_text(encoding="utf-8")
    need("font-size:16px" in reference_svg and "font-size:34px" in reference_svg and "PDU_COMMON_RET" in reference_svg, "reference diagram legibility/content drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    need("HR30-ACTUATOR-CABLE-KIT-P01-START" in root_page and "8 / 8" in root_page and "five isolated RS-485" in root_page, "root guide integration missing")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-START") == 1 and root_readme.count("HR30-ACTUATOR-CABLE-KIT-P01-README-END") == 1, "cable-kit README marker drift")
    need(root_readme.count("HR30-AXIS-COMMISSION-START") == 1 and root_readme.count("HR30-AXIS-COMMISSION-END") == 1, "axis-commissioning README marker drift")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["actuator_cable_kit_axis_count"] == 25 and root_status["actuator_cable_kit_cavity_record_count"] == 159, "root status integration missing")
    need(root_status["actuator_power_transition_brackets_dimensioned"] and root_status["actuator_power_transition_bracket_placement_count"] == 25, "root transition-bracket reconciliation missing")
    need(root_status["actuator_bus_reference_architecture_defined"] and root_status["actuator_bus_reference_count"] == 8 and root_status["actuator_bus_reference_star_node"] == "PDU_COMMON_RET", "root reference architecture missing")
    need(root_status["actuator_bus_rs485_isolated_channel_count"] == 5 and root_status["actuator_bus_ttl_nonisolated_channel_count"] == 3 and not root_status["actuator_bus_reference_validated"], "root reference validation boundary drift")
    need(root_status["actuator_cable_kit_current_caps_propagated"] and root_status["actuator_power_cable_20c_planning_calculated"] and not root_status["actuator_power_cable_hot_ampacity_verified"], "root advancement/thermal boundary drift")
    need(not root_status["energization_authority"], "root authority drift")
    print("PASS: HR-30 actuator cable kit binds all 8 buses to a single-point return/reference candidate without daisy GND/VDD conductors; all physical release gates remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
