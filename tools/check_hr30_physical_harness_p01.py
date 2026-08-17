"""Fail-closed checks for HR-30 whole-body physical-harness P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "harness" / "physical-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / "physical-p0.1"
WARNING = "PRELIMINARY - PHYSICAL HARNESS ARCHITECTURE ONLY"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def main() -> int:
    status = json.loads((OUT / "physical-harness-status.json").read_text(encoding="utf-8"))
    axes = rows("axis-harness-binding.csv")
    routes = rows("route-segment-register.csv")
    points = rows("route-point-register.csv")
    route_cad = rows("route-cad-register.csv")
    loops = rows("service-loop-register.csv")
    power = rows("actuator-power-drop-register.csv")
    transitions = rows("actuator-power-transition-register.csv")
    links = rows("bus-physical-link-register.csv")
    connectors = rows("connector-instance-register.csv")
    contacts = rows("connector-contact-map.csv")
    cores = rows("cable-core-register.csv")
    chains = rows("actuator-chain-contact-map.csv")
    power_pairs = rows("individual-power-pair-register.csv")
    data_links = rows("serial-data-link-register.csv")
    equipment = rows("equipment-interface-register.csv")
    logical = rows("logical-terminal-binding.csv")
    assemblies = rows("harness-assembly-register.csv")
    terminations = rows("bus-termination-register.csv")
    shields = rows("shield-bond-register.csv")
    retain = rows("retention-strain-relief-register.csv")
    derating = rows("current-derating-register.csv")
    inspections = rows("inspection-test-register.csv")
    unresolved = rows("unresolved-harness-selections.csv")
    interfaces = rows("actuator-interface-verification-register.csv")
    commercial_cables = rows("robotis-cable-family-register.csv")
    discrepancies = rows("manufacturer-interface-discrepancy-register.csv")
    source = rows("source-register.csv")

    require(len(axes) == len(loops) == len(power) == len(transitions) == len(links) == len(chains) == len(power_pairs) == len(data_links) == len(retain) == len(derating) == 25, "25-axis register spine incomplete")
    require(len(connectors) == 196, "42 actuator/data plus 104 walking-power and 50 inline-transition connector boundaries required")
    require(len(routes) == 62 and len(points) == 124, "route geometry count drift")
    require(len(route_cad) == 62 and {r["segment_id"] for r in route_cad} == {r["segment_id"] for r in routes}, "whole-body route CAD register does not cover all 62 segments")
    require(len({r["solid_name"] for r in route_cad}) == 62, "route CAD solid names are not unique")
    require(all(r["geometry_interpretation"].startswith("REFERENCE CENTERLINE ROD ONLY") and r["authority"].startswith("NO PROCUREMENT") for r in route_cad), "route CAD overclaims cable sizing or authority")
    require(Counter(r["segment_kind"] for r in routes) == {"MOVING JOINT LOOP": 50, "FIXED BODY CORRIDOR": 12}, "fixed/moving route split drift")
    require(len(assemblies) == 14 and len(terminations) == len(shields) == 8, "assembly/bus completeness drift")
    with (WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv").open(encoding="utf-8-sig", newline="") as handle:
        ecad_terminals = list(csv.DictReader(handle))
    require(len(equipment) == 64 and len(logical) == len(ecad_terminals), "equipment or logical-terminal binding incomplete")
    require(len(contacts) == 515 and len(cores) == 144, "actuator/WPS/transition contact and split-core mapping drift")
    require(len(inspections) >= 10 and len(unresolved) >= 10, "inspection/open-selection registers incomplete")
    require(len(interfaces) == 4 and {r["actuator_family"] for r in interfaces} == {"XH540", "XM540", "XM430", "XC330"}, "four actuator interface verification records required")
    require(sum(int(r["axis_count"]) for r in interfaces) == 25 and all(r["verified_boundary"].startswith("DEVICE PINOUT") for r in interfaces), "actuator interface coverage/claim drift")
    require(len(commercial_cables) == 5 and len({r["official_order_code"] for r in commercial_cables}) == 5, "five exact ROBOTIS commercial cable families required")
    require(all("VDD" in r["published_populated_contacts"] and r["hr30_whole_body_role"].startswith("REJECT") for r in commercial_cables), "commercial cable VDD/rejection boundary missing")
    require({r["finding_id"] for r in discrepancies} == {f"DXL-IF-00{i}" for i in range(1, 6)}, "manufacturer discrepancy set incomplete")
    require(all("OPEN" in r["disposition"] or "REJECT" in r["disposition"] or "CANDIDATE ONLY" in r["disposition"] for r in discrepancies), "manufacturer discrepancy incorrectly closed")

    axis_ids = {r["axis_id"] for r in axes}
    require(len(axis_ids) == 25, "axis IDs not unique")
    route_ids = {r["segment_id"] for r in routes}
    point_ids = {r["point_id"] for r in points}
    require(len(route_ids) == len(routes) and len(point_ids) == len(points), "route/point IDs not unique")
    for r in routes:
        require(r["from_point"] in point_ids and r["to_point"] in point_ids, f"route point missing for {r['segment_id']}")
        require(float(r["planning_length_mm"]) > 0, f"nonpositive route length {r['segment_id']}")
    for a in axes:
        require(a["power_loop"] in route_ids and a["data_loop"] in route_ids, f"axis loops missing {a['axis_id']}")
        require(a["power_trunk"] in route_ids and a["data_trunk"] in route_ids, f"axis trunk missing {a['axis_id']}")

    bus_axis: dict[str, list[str]] = defaultdict(list)
    for a in axes: bus_axis[a["bus_id"]].append(a["axis_id"])
    require(sorted(len(v) for v in bus_axis.values()) == [1, 2, 2, 2, 3, 3, 6, 6], "eight-bus axis allocation drift")
    require(abs(sum(float(r["candidate_12v_stall_endpoint_a"]) for r in power) - 71.88) < 1e-8, "stall endpoint arithmetic drift")
    require(all("PAIRED OPPOSING TPS259482LYWPR" in r["protection_topology"] and "CHANNEL" in r["protection_topology"] for r in power), "25 paired board/channel protection bindings missing")
    require(all("CF130.03.02.UL" in r["conductor_size"] and "Alpha Wire 3051" in r["conductor_size"] for r in power), "moving/pigtail conductor architecture missing")
    require(all(r["moving_housing_terminal"] == "430250200 + 2 x 430300001" and r["panel_housing_terminal"] == "430200200 + 2 x 430310001" and "PANEL-MOUNT BRACKET" in r["load_path"] for r in transitions), "25 fixed-side transition bindings drift")
    require({r["branch_net"] for r in power} == {axis + "_VDD" for axis in axis_ids}, "individual actuator VDD net binding drift")
    require(all("STANDARD DYNAMIXEL CABLE VDD" in r["vdd_isolation_rule"] for r in links), "VDD backfeed boundary missing")
    require(all("SERIAL DATA TRUNK" in r["topology_state"] for r in chains), "serial chain topology missing")
    require(sum(r["successor_axis"] != "FAR END" for r in chains) == 17, "expected 17 inter-actuator outgoing data connectors")
    require(sum(r["successor_axis"] == "FAR END" for r in chains) == 8, "expected one far end per data bus")
    by_bus_chain: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in chains:
        by_bus_chain[row["bus_id"]].append(row)
    for bus, values in by_bus_chain.items():
        values.sort(key=lambda row: int(row["ordinal"]))
        for index, row in enumerate(values):
            expected_upstream = f"CB-{bus}" if index == 0 else f"J-OUT-{values[index - 1]['axis_id']}"
            expected_successor = values[index + 1]["axis_id"] if index + 1 < len(values) else "FAR END"
            require(row["upstream_data_endpoint"] == expected_upstream, f"chain predecessor mismatch {row['axis_id']}")
            require(row["successor_axis"] == expected_successor, f"chain successor mismatch {row['axis_id']}")
            require("1=INDIVIDUAL RETURN; 2=INDIVIDUAL VDD" in row["input_pin_map"], f"input power pair mapping missing {row['axis_id']}")
            if expected_successor != "FAR END":
                require("1=EMPTY; 2=EMPTY" in row["outgoing_pin_map"], f"outgoing GND/VDD cavities not empty {row['axis_id']}")
    require(all(float(row["one_way_planning_length_mm"]) > 0 and abs(float(row["round_trip_planning_length_mm"]) - 2 * float(row["one_way_planning_length_mm"])) < 0.0011 for row in power_pairs), "power-pair planning lengths missing")
    require(all(float(row["planning_length_mm"]) > 0 for row in data_links), "serial data-link planning lengths missing")

    by_connector = Counter(r["connector_id"] for r in contacts)
    for c in connectors:
        require(by_connector[c["connector_id"]] == int(c["contact_count"]), f"contact count mismatch {c['connector_id']}")
    used_contact_cores = {r["wire_core"] for r in contacts if not r["wire_core"].startswith("NONE") and r["wire_core"] != "SELECTION REQUIRED"}
    require({r["core_id"] for r in cores} == used_contact_cores, "contact/core references mismatch")
    outgoing_contacts = [r for r in contacts if r["connector_id"].startswith("J-OUT-")]
    require(sum(r["signal"].startswith("EMPTY") for r in outgoing_contacts) == 34, "outgoing GND/VDD empty-cavity count drift")
    require(all(r["wire_core"] == "NONE - CAVITY EMPTY" for r in outgoing_contacts if r["signal"].startswith("EMPTY")), "empty outgoing cavity has a conductor")
    for core in cores:
        if core["service"] in {"ACTUATOR POWER", "POWER RETURN"}:
            if core["core_id"].endswith("-DYNAMIC"):
                require(core["from_connector_contact"].startswith("J-WPS-") and core["from_connector_contact"].endswith(("/1", "/2")) and core["to_connector_contact"].startswith("J-TR-DYN-"), f"dynamic power-core boundary missing {core['core_id']}")
            elif core["core_id"].endswith("-PIGTAIL"):
                require(core["from_connector_contact"].startswith("J-TR-PIG-") and core["to_connector_contact"].startswith("J-ACT-"), f"pigtail power-core boundary missing {core['core_id']}")
            else:
                require(False, f"unsplit power core remains {core['core_id']}")
    require(all(float(r["length_mm"]) > 0 and r["calculation_state"].startswith("PARTIAL - LENGTH PRESENT") for r in derating), "geometry-derived derating lengths missing or overclaimed")
    pdu_equipment = [r for r in equipment if r["item_id"].startswith("EQ-WPS-")]
    require(len(pdu_equipment) == 8 and all(r["physical_connector"].startswith("WPS LOGICAL CONNECTOR FUNCTIONS") for r in pdu_equipment), "eight WPS equipment connector boundaries missing")
    require(all(r["physical_connector"] == "SELECTION REQUIRED" for r in equipment if not r["item_id"].startswith("EQ-WPS-")), "non-WPS equipment connector closure overclaimed")
    require(all(r["physical_binding_state"].startswith("LOGICAL TERMINAL RETAINED") for r in logical), "logical terminal lost or overclaimed")

    false_gates = ["standard_dynamixel_cable_direct_use_approved", "assembled_cables_selected", "u2d2_final_whole_body_controller_approved", "u2d2_power_hub_whole_body_or_leg_power_approved", "robotis_jst_wire_gauge_conflict_closed", "robotis_jst_housing_order_code_conflict_closed", "conductor_sizing_released", "protection_released", "connector_set_released", "harness_validated", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]
    require(all(status[k] is False for k in false_gates), "authority/selection gate overclaimed")
    require(status["total_route_segments"] == 62 and status["logical_terminals"] == len(ecad_terminals), "status count drift")
    require(status["route_cad_solid_count"] == 62 and status["whole_body_route_step_present"] is True and status["whole_body_route_glb_present"] is True, "whole-body route CAD status missing")
    require(status["route_cad_is_cable_size_release"] is False, "route centerline CAD incorrectly releases cable sizing")
    require(status["split_harness_candidate_defined"] is True and status["data_star_topology_rejected"] is True and status["serial_data_predecessor_successor_chain_complete"] is True, "split-harness status missing")
    require(status["actuator_connector_instances"] == 196 and status["actuator_connector_contacts"] == 515 and status["cable_cores"] == 144 and status["serial_data_links"] == status["individual_power_pairs"] == status["fixed_side_power_transitions"] == 25, "split-harness/WPS/transition status counts drift")
    require(status["fixed_side_microfit_transition_candidate_defined"] and status["direct_cf130_to_jst_eh_crimp_rejected"] and status["transition_order_code_candidates_bound"], "fixed-transition status missing")
    require(not status["transition_brackets_dimensioned"] and not status["cf130_individual_core_od_verified"], "physical transition evidence overclaimed")
    require(status["actuator_interface_verification_records"] == 4 and status["robotis_commercial_cable_families_reviewed"] == 5 and status["manufacturer_interface_discrepancies_open"] == 5, "manufacturer interface status counts drift")

    for s in source:
        p = ROOT / s["source"]
        require(p.is_file() and sha(p) == s["sha256"], f"source hash mismatch {s['source']}")

    manifest = rows("file-manifest.csv")
    listed = {r["path"] for r in manifest}
    actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
    require(listed == actual, "package manifest file set mismatch")
    for row in manifest:
        p = OUT / row["path"]
        require(p.stat().st_size == int(row["bytes"]) and sha(p) == row["sha256"], f"manifest mismatch {row['path']}")

    src_files = {p.relative_to(OUT).as_posix(): p for p in OUT.rglob("*") if p.is_file()}
    rel_files = {p.relative_to(RELEASE).as_posix(): p for p in RELEASE.rglob("*") if p.is_file()}
    require(src_files.keys() == rel_files.keys(), "release mirror file set mismatch")
    require(all(sha(p) == sha(rel_files[n]) for n, p in src_files.items()), "release mirror byte mismatch")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "whole-body-physical-harness.svg").read_text(encoding="utf-8")
    require("font-size:14px" in page and "font:16px/1.5" in page, "web guide legibility floor missing")
    require(not re.search(r"font-size\s*:\s*(?:[0-9]|1[01])px", page), "web guide contains text below 12 px")
    require(svg.count('class="joint"') == 25 and svg.count('class="route ') == 62, "SVG route/joint completeness drift")
    diagrams = sorted((OUT / "bus-diagrams").glob("*.svg"))
    require(len(diagrams) == 8 and all("Outgoing pins 1/2 EMPTY" in path.read_text(encoding="utf-8") for path in diagrams), "eight serial bus assembly drawings missing")
    require("Eight serial data-chain assembly drawings" in page and "actuator-chain-contact-map.csv" in page, "interactive split-harness guide missing")
    require("Manufacturer interface reality check" in page and "robotis-cable-family-register.csv" in page and "manufacturer-interface-discrepancy-register.csv" in page, "manufacturer interface web guidance missing")
    require("Fixed transition at every actuator branch" in page and "actuator-power-transition-register.csv" in page and "Moving CF130 no longer terminates directly into JST EH" in page, "fixed-transition web guidance missing")
    require("71.88 A figure" in page and "76.08 A figure" not in page, "whole-body endpoint current text is stale")
    require("HR30_whole_body_harness_centerlines_candidate.glb" in page and "route-cad-register.csv" in page and "model-viewer.min.js" in page, "interactive 3D route model missing from web guide")
    step_path = OUT / "HR30_whole_body_harness_centerlines_candidate.step"
    glb_path = OUT / "HR30_whole_body_harness_centerlines_candidate.glb"
    require(step_path.stat().st_size > 100_000 and glb_path.stat().st_size > 25_000, "whole-body route STEP/GLB exports are missing or empty")
    step_shape = cq.importers.importStep(str(step_path))
    box = step_shape.val().BoundingBox()
    require(len(step_shape.solids().vals()) >= 73, "route STEP does not contain 62 routes plus recognizable body context")
    require(abs(box.zmin) < 1e-6 and abs(box.zmax - 762.0) < 1e-6, "route STEP does not preserve the complete 762 mm body datum")
    require(not list(OUT.rglob("*.pdf")), "physical harness package must remain web/register native")

    whole_readme = (WB / "README.md").read_text(encoding="utf-8")
    whole_page = (WB / "index.html").read_text(encoding="utf-8")
    whole_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    require("## Physical whole-body harness P0.1" in whole_readme, "whole-body README integration missing")
    require('href="harness/physical-p0.1/index.html"' in whole_page, "whole-body web guide link missing")
    require(whole_status.get("physical_harness_package_present") is True, "whole-body status integration missing")
    require(whole_status.get("physical_harness_selected") is False and whole_status.get("physical_harness_validated") is False, "whole-body harness status overclaimed")

    readme = (OUT / "README.md").read_text(encoding="utf-8")
    require("71.88 A figure" in readme and "76.08 A figure" not in readme, "README endpoint current text is stale")
    require("21 AWG cable statement conflicts" in readme and "U2D2 is retained only" in readme, "README manufacturer-interface boundary missing")

    print(f"PASS: HR-30 physical harness: 25 fixed-side Micro-Fit transitions split moving CF130 from restrained Alpha 3051 pigtails; 196 connectors / 515 contacts / 144 cores; {len(logical)} logical terminals; all release/authority gates false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
