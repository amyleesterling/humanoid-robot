#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 E1 controls-only fixture P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "electrical/e1-controls-only-fixture-p0.1"
REL = ROOT / "release/hr30/whole-body-p0.1/electrical/e1-controls-only-fixture-p0.1"
WARNING = (
    "PRELIMINARY - UNBUILT CONTROLS-ONLY FIXTURE CANDIDATE - NOT APPROVED "
    "FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
EXPECTED_BUSES = {
    "RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM",
    "RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "README.md", "index.html", "e1-fixture-status.json",
        "HR30_E1_controls_only_fixture_candidate.step",
        "HR30_E1_controls_only_fixture_candidate.glb",
        "HR30_E1_base_panel_candidate.step", "HR30_E1_base_panel_candidate.dxf",
        "HR30_E1_carrier_field_port_cover_candidate.step",
        "HR30_E1_carrier_field_port_cover_candidate.stl",
        "mcu-native-pcb.step", "carrier_a-native-pcb.step",
        "carrier_b-native-pcb.step", "swd-native-pcb.step",
        "kicad-board-export.log", "pcb-placement-register.csv",
        "mount-hole-register.csv", "field-port-exclusion-register.csv",
        "e1-configuration-register.csv", "connector-boundary-register.csv",
        "candidate-bom.csv", "assembly-sequence.csv", "source-binding.csv",
        "open-holds.csv", "e1-controls-fixture-source.py", "file-manifest.csv",
        "HR30_E1_logic_harness_candidate.step",
        "HR30_E1_logic_harness_candidate.glb",
        "HR30_E1_controls_fixture_with_logic_harness_candidate.step",
        "HR30_E1_controls_fixture_with_logic_harness_candidate.glb",
        "logic-harness-assembly-register.csv",
        "logic-harness-connector-instance-register.csv",
        "logic-harness-contact-map.csv", "logic-harness-bom.csv",
        "logic-harness-process-traveler.csv",
        "logic-harness-primary-source-register.csv",
        "logic-harness-open-holds.csv", "logic-harness-source-binding.csv",
        "logic-harness-status.json", "logic-harness-assembly-map.svg",
        "e1-logic-harness-source.py",
        "HR30_E1_J1_logic_power_cable_candidate.step",
        "HR30_E1_J1_logic_power_cable_candidate.glb",
        "HR30_E1_J1_logic_power_cable_placed_candidate.step",
        "HR30_E1_J1_logic_power_cable_placed_candidate.glb",
        "HR30_E1_controls_fixture_complete_logic_wiring_candidate.step",
        "HR30_E1_controls_fixture_complete_logic_wiring_candidate.glb",
        "j1-power-cable-assembly-register.csv",
        "j1-power-cable-contact-map.csv", "j1-power-cable-route-register.csv",
        "j1-power-cable-bom.csv", "j1-power-cable-process-traveler.csv",
        "j1-power-cable-primary-source-register.csv",
        "j1-power-cable-source-binding.csv", "j1-power-cable-open-holds.csv",
        "j1-power-cable-status.json", "j1-power-cable-assembly-map.svg",
        "e1-j1-power-cable-source.py",
        "HR30_E1_fixture_hardware_candidate.step",
        "HR30_E1_fixture_hardware_candidate.glb",
        "fixture-hardware-selection-register.csv",
        "fixture-fastener-stack-register.csv",
        "fixture-material-register.csv",
        "fixture-fabrication-drawing-register.csv",
        "fixture-dimensional-inspection-register.csv",
        "fixture-hardware-primary-source-register.csv",
        "fixture-hardware-source-binding.csv",
        "fixture-hardware-open-holds.csv", "fixture-hardware-status.json",
        "base-panel-fabrication-drawing.svg",
        "carrier-cover-fabrication-drawing.svg",
        "under-panel-raceway-fabrication-drawing.svg",
        "fixture-hardware-assembly-map.svg", "e1-fixture-hardware-source.py",
    }
    source_files = {path.name for path in OUT.iterdir() if path.is_file()}
    release_files = {path.name for path in REL.iterdir() if path.is_file()}
    need(source_files == required, f"source file set drift: {sorted(source_files ^ required)}")
    need(release_files == required, f"release file set drift: {sorted(release_files ^ required)}")
    for name in required:
        need(sha(OUT / name) == sha(REL / name), f"source/release mismatch {name}")
    need(
        sha(OUT / "e1-controls-fixture-source.py")
        == sha(ROOT / "tools/generate_hr30_e1_controls_fixture_p01.py"),
        "generator snapshot drift",
    )
    need(
        sha(OUT / "e1-logic-harness-source.py")
        == sha(ROOT / "tools/generate_hr30_e1_logic_harness_p01.py"),
        "logic harness generator snapshot drift",
    )
    need(
        sha(OUT / "e1-j1-power-cable-source.py")
        == sha(ROOT / "tools/generate_hr30_e1_logic_power_cable_p01.py"),
        "J1 power-cable generator snapshot drift",
    )
    need(
        sha(OUT / "e1-fixture-hardware-source.py")
        == sha(ROOT / "tools/generate_hr30_e1_fixture_hardware_p01.py"),
        "fixture hardware generator snapshot drift",
    )

    bindings = rows(OUT / "source-binding.csv")
    need(len(bindings) == 9 and len({row["role"] for row in bindings}) == 9, "source binding count drift")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"] and row["state"] == "BOUND", f"source binding mismatch {row['role']}")

    boards = rows(OUT / "pcb-placement-register.csv")
    need(len(boards) == 4 and {row["board_id"] for row in boards} == {"MCU", "CARRIER_A", "CARRIER_B", "SWD"}, "board population drift")
    need(sum(int(row["mount_hole_count"]) for row in boards) == 14, "board mount-hole aggregate drift")
    for row in boards:
        source = ROOT / row["native_pcb"]
        need(source.is_file() and sha(source) == row["native_pcb_sha256"], f"native PCB hash drift {row['board_id']}")
        need((OUT / row["exported_step"]).is_file(), f"missing board STEP {row['board_id']}")

    holes = rows(OUT / "mount-hole-register.csv")
    need(len(holes) == 14 and len({row["hole_id"] for row in holes}) == 14, "mount-hole register drift")
    need(len({(row["panel_x_mm"], row["panel_y_mm"]) for row in holes}) == 14, "duplicate panel hole axes")
    need(all(float(row["native_hole_diameter_mm"]) == 2.7 and float(row["panel_clearance_diameter_mm"]) == 3.0 for row in holes), "mount-hole diameter drift")

    ports = rows(OUT / "field-port-exclusion-register.csv")
    need(len(ports) == 8 and {row["whole_body_bus"] for row in ports} == EXPECTED_BUSES, "field-port coverage drift")
    need(len({row["port_id"] for row in ports}) == 8, "duplicate field-port identity")
    need(all(row["power_contact_present"] == "NO - DATA-ONLY INTERFACE" for row in ports), "power contact introduced at field port")
    need(all("NO EXTERNAL OPENING" in row["e1_physical_state"] for row in ports), "field port not physically enclosed")

    stages = rows(OUT / "e1-configuration-register.csv")
    need([row["stage"] for row in stages] == ["E1-A", "E1-B", "E1-C"], "E1 stage sequence drift")
    need(all(row["execution"] == "NOT EXECUTED" for row in stages), "unexecuted fixture presented as executed")
    boundaries = rows(OUT / "connector-boundary-register.csv")
    need({row["boundary"] for row in boundaries} == {"J1", "JDBG1", "JMCU_A", "JMCU_B", "FIELD_PORTS", "ACTUATOR_POWER"}, "connector boundary drift")
    actuator_power = next(row for row in boundaries if row["boundary"] == "ACTUATOR_POWER")
    need(actuator_power["allowed_on_fixture"] == "NONE" and "NO CONNECTOR" in actuator_power["e1_state"], "actuator-power exclusion weakened")
    need("15 OF 15 POPULATED" in next(row for row in boundaries if row["boundary"] == "JMCU_A")["selection"], "carrier A harness boundary incomplete")
    need("13-15 EMPTY" in next(row for row in boundaries if row["boundary"] == "JMCU_B")["selection"], "carrier B empty-cavity boundary missing")
    j1_boundary = next(row for row in boundaries if row["boundary"] == "J1")
    need("VHR-2N" in j1_boundary["selection"] and "ALPHA 3051" in j1_boundary["selection"], "J1 physical cable boundary missing")
    need("UNBUILT / UNCONNECTED / UNPOWERED" in j1_boundary["e1_state"], "J1 boundary authority weakened")

    harnesses = rows(OUT / "logic-harness-assembly-register.csv")
    need(len(harnesses) == 2 and {row["harness_id"] for row in harnesses} == {"E1-HA-A", "E1-HA-B"}, "logic harness assembly drift")
    by_harness = {row["harness_id"]: row for row in harnesses}
    need(int(by_harness["E1-HA-A"]["populated_conductors"]) == 15 and by_harness["E1-HA-A"]["empty_positions"] == "NONE", "carrier A harness population drift")
    need(int(by_harness["E1-HA-B"]["populated_conductors"]) == 12 and by_harness["E1-HA-B"]["empty_positions"] == "13;14;15", "carrier B harness population drift")
    need(float(by_harness["E1-HA-A"]["candidate_cut_length_mm"]) == 320.0 and float(by_harness["E1-HA-B"]["candidate_cut_length_mm"]) == 310.0, "logic harness cut-length drift")
    need(all(float(row["candidate_service_allowance_mm"]) > 40.0 for row in harnesses), "logic harness service allowance lost")
    need("320/310 mm cut-length candidates" in (OUT / "README.md").read_text(encoding="utf-8"), "logic harness README cut-length drift")
    guide_text = (OUT / "index.html").read_text(encoding="utf-8")
    need(guide_text.index('id="e1-logic-harness"') < guide_text.index("</main>") < guide_text.index("<footer>"), "logic harness guide section escaped main")
    need("Â" not in guide_text and "\ufffd" not in guide_text, "logic harness guide contains mojibake")

    contacts = rows(OUT / "logic-harness-contact-map.csv")
    need(len(contacts) == 30 and len({row["map_id"] for row in contacts}) == 30, "logic harness contact-map drift")
    populated = [row for row in contacts if row["population"] == "POPULATED BOTH ENDS"]
    empty = [row for row in contacts if row["population"] == "EMPTY BOTH ENDS - NO CONTACT/WIRE"]
    need(len(populated) == 27 and len(empty) == 3, "logic harness populated/empty map count drift")
    need({int(row["position"]) for row in empty} == {13, 14, 15} and {row["harness_id"] for row in empty} == {"E1-HA-B"}, "empty cavities are not carrier B positions 13-15")
    need(all(row["mcu_contact"].split(".")[1] == row["carrier_contact"].split(".")[1] for row in populated), "logic harness is not straight-through")
    need(all(row["continuity"] == row["short_to_adjacent"] == row["retention"] == "NOT EXECUTED" for row in contacts), "unexecuted harness inspection overclaim")
    allowed_wire = {
        "Belden 1852 BK005", "Belden 1852 RD005", "Belden 1852 YL005",
        "Belden 1852 BL005", "Belden 1852 WH005", "Belden 1852 OR005",
    }
    need({row["wire_candidate"] for row in populated} <= allowed_wire, "uncontrolled wire introduced")

    connectors = rows(OUT / "logic-harness-connector-instance-register.csv")
    need(len(connectors) == 4 and sum(int(row["contact_quantity"]) for row in connectors) == 54, "logic harness connector/contact count drift")
    need(all(row["housing_candidate"] == "JST GHR-15V-S" and row["contact_candidate"] == "JST SSHL-002T-P0.2" for row in connectors), "logic harness connector selection drift")
    logic_bom = rows(OUT / "logic-harness-bom.csv")
    need(len(logic_bom) == 10 and sum(int(row["quantity"]) for row in logic_bom if row["order_code"] == "SSHL-002T-P0.2") == 60, "logic harness BOM drift")
    need(any(row["order_code"] == "AP-K2N + MKS-L-10-3 + APLMK SSHL002-02" and "NO HAND TOOL" in row["selection"] for row in logic_bom), "manufacturer machine tooling boundary missing")

    process = rows(OUT / "logic-harness-process-traveler.csv")
    need(len(process) == 10 and all(row["record"] == "NOT EXECUTED" for row in process), "logic harness process execution overclaim")
    logic_holds = rows(OUT / "logic-harness-open-holds.csv")
    need(len(logic_holds) == 6 and all(row["state"] == "OPEN" for row in logic_holds), "logic harness hold drift")
    sources = rows(OUT / "logic-harness-primary-source-register.csv")
    need(len(sources) == 3 and {row["manufacturer"] for row in sources} == {"JST", "Belden"}, "logic harness primary-source drift")
    logic_bindings = rows(OUT / "logic-harness-source-binding.csv")
    need(len(logic_bindings) == 4 and len({row["role"] for row in logic_bindings}) == 4, "logic harness source-binding drift")
    for row in logic_bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"], f"logic harness binding mismatch {row['role']}")

    status = json.loads((OUT / "e1-fixture-status.json").read_text(encoding="utf-8"))
    need(status["native_board_count"] == 4 and status["native_board_step_export_count"] == 4, "status board count drift")
    need(status["native_mount_hole_count"] == 14 and status["sealed_carrier_cover_count"] == 2, "status geometry count drift")
    need(status["actuator_field_port_count"] == 8 and status["actuator_field_ports_physically_covered_in_cad"], "status port coverage drift")
    need(not any(status[key] for key in (
        "actuator_power_connectors_present", "actuator_power_conductors_present",
        "actuator_pdu_present", "actuator_present", "fixture_built", "native_pcbs_built",
        "received_fit_validated", "wiring_built_or_inspected", "firmware_flashed",
        "hil_executed", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    )), "fixture status overclaim or actuator-power path introduced")
    need(status["logic_harness_candidate_present"] and status["logic_harness_assembly_count"] == 2, "fixture logic harness status absent")
    need(status["logic_harness_populated_conductor_count"] == 27 and status["logic_harness_installed_contact_count"] == 54 and status["logic_harness_empty_cavity_count"] == 6, "fixture logic harness counts drift")

    logic_status = json.loads((OUT / "logic-harness-status.json").read_text(encoding="utf-8"))
    need(logic_status["harness_assembly_count"] == 2 and logic_status["physical_wire_cad_count"] == 27, "logic harness CAD/status count drift")
    need(logic_status["native_pin_maps_match"] and logic_status["manufacturer_wire_contact_dimensional_candidate_match"], "logic harness source/dimensional screen failed")
    need(not any(logic_status[key] for key in (
        "harness_built", "crimp_process_qualified", "received_fit_validated",
        "continuity_isolation_executed", "current_derating_validated",
        "connection_authority", "powered_test_authority", "motion_authority",
        "walking_authority", "energization_authority",
    )), "logic harness status overclaim")

    j1_assemblies = rows(OUT / "j1-power-cable-assembly-register.csv")
    need(len(j1_assemblies) == 1 and int(j1_assemblies[0]["conductor_count"]) == 2, "J1 cable assembly drift")
    need(float(j1_assemblies[0]["wire_cut_length_mm_each"]) == 1000.0, "J1 wire cut length drift")
    need("NOT MANUFACTURER CAD" in j1_assemblies[0]["cad_basis"], "J1 dimensional-envelope disclosure missing")
    j1_contacts = rows(OUT / "j1-power-cable-contact-map.csv")
    need(len(j1_contacts) == 2 and len({row["map_id"] for row in j1_contacts}) == 2, "J1 contact-map count drift")
    j1_by_destination = {row["destination"]: row for row in j1_contacts}
    need(j1_by_destination["J1.2"]["net"] == "AUX_5V_SAFE" and j1_by_destination["J1.2"]["color"] == "RED", "J1 positive map drift")
    need(j1_by_destination["J1.1"]["net"] == "CTRL_GND" and j1_by_destination["J1.1"]["color"] == "BLACK", "J1 return map drift")
    need(all(float(row["cut_length_mm"]) == 1000.0 and row["continuity"] == row["isolation"] == "NOT EXECUTED" for row in j1_contacts), "J1 cable execution/cut-length drift")
    j1_routes = rows(OUT / "j1-power-cable-route-register.csv")
    need(len(j1_routes) == 2 and all(abs(float(row["cad_centerline_mm"]) - 1000.0) < 0.001 for row in j1_routes), "J1 placed route length drift")
    need(all("-128.200" in row["native_j1_panel_xyz_mm"] for row in j1_routes), "native J1 placement not bound")
    j1_bom = rows(OUT / "j1-power-cable-bom.csv")
    expected_j1_parts = {"VHR-2N", "SVH-21T-P1.1", "3051 RD005", "3051 BK005", "5934-2", "5934-0", "FIT-KIT-221BK", "M21-11-427"}
    need(expected_j1_parts <= {row["order_code"] for row in j1_bom}, "J1 exact material candidates missing")
    need(any("NO HAND TOOL" in row["selection"] for row in j1_bom), "J1 hand-crimp prohibition missing")
    j1_process = rows(OUT / "j1-power-cable-process-traveler.csv")
    need(len(j1_process) == 9 and all(row["record"] == "NOT EXECUTED" for row in j1_process), "J1 process traveler overclaim")
    j1_sources = rows(OUT / "j1-power-cable-primary-source-register.csv")
    need(len(j1_sources) == 5 and {row["manufacturer"] for row in j1_sources} == {"JST", "Alpha Wire", "Pomona Electronics", "Brady"}, "J1 primary-source set drift")
    j1_holds = rows(OUT / "j1-power-cable-open-holds.csv")
    need(len(j1_holds) == 8 and all(row["state"] == "OPEN" for row in j1_holds), "J1 open-hold drift")
    j1_bindings = rows(OUT / "j1-power-cable-source-binding.csv")
    need(len(j1_bindings) == 4 and len({row["role"] for row in j1_bindings}) == 4, "J1 source-binding drift")
    for row in j1_bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"], f"J1 source binding mismatch {row['role']}")
    j1_status = json.loads((OUT / "j1-power-cable-status.json").read_text(encoding="utf-8"))
    need(j1_status["cable_assembly_count"] == 1 and j1_status["conductor_count"] == 2, "J1 status count drift")
    need(j1_status["project_owned_dimensional_envelopes_only"] and not j1_status["manufacturer_cad_redistributed"], "J1 CAD provenance boundary drift")
    need(not any(j1_status[key] for key in (
        "cable_built", "crimp_process_qualified", "set_screw_process_released",
        "received_fit_validated", "continuity_isolation_polarity_executed",
        "current_thermal_derating_validated", "supply_limits_released",
        "dc_reference_approved", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    )), "J1 status overclaim")

    hardware = rows(OUT / "fixture-hardware-selection-register.csv")
    need(len(hardware) == 13 and len({row["selection_id"] for row in hardware}) == 13, "fixture hardware selection drift")
    expected_orders = {
        "970080155", "50M025045P006 / ITEM 10295533",
        "50M025045D012 / ITEM 10325643", "50M030050P012 / ITEM 10397367",
        "496241 / ITEM 10279151", "SJ5309 / 3M ID 7000029678",
        "ITEM 10374603", "0030030000VR / ITEM 10041420",
    }
    need(expected_orders <= {row["order_code"] for row in hardware}, "exact fixture hardware candidates missing")
    need(all(row["built"] == "NO" for row in hardware), "fixture hardware build overclaim")
    stacks = rows(OUT / "fixture-fastener-stack-register.csv")
    need(len(stacks) == 3 and sum(int(row["location_count"]) for row in stacks) == 26, "fixture fastener stack count drift")
    need({row["stack_id"] for row in stacks} == {"FH-ST01", "FH-ST02", "FH-ST03"}, "fixture stack identity drift")
    materials = rows(OUT / "fixture-material-register.csv")
    need(len(materials) == 4 and all("OPEN" in row["state"] for row in materials), "fixture material register drift")
    drawings = rows(OUT / "fixture-fabrication-drawing-register.csv")
    need(len(drawings) == 4 and all((OUT / row["file"]).is_file() for row in drawings), "fixture drawing register drift")
    inspections = rows(OUT / "fixture-dimensional-inspection-register.csv")
    need(len(inspections) == 10 and all(row["result"] == "NOT EXECUTED" for row in inspections), "fixture inspection overclaim")
    hardware_sources = rows(OUT / "fixture-hardware-primary-source-register.csv")
    need(len(hardware_sources) == 10 and {row["manufacturer"] for row in hardware_sources} == {"SABIC", "Wuerth Elektronik", "Essentra", "3M"}, "fixture primary-source drift")
    hardware_bindings = rows(OUT / "fixture-hardware-source-binding.csv")
    need(len(hardware_bindings) == 6 and len({row["role"] for row in hardware_bindings}) == 6, "fixture hardware binding drift")
    for row in hardware_bindings:
        path = ROOT / row["path"]
        need(path.is_file() and sha(path) == row["sha256"], f"fixture hardware binding mismatch {row['role']}")
    hardware_holds = rows(OUT / "fixture-hardware-open-holds.csv")
    need(len(hardware_holds) == 7 and all(row["state"] == "OPEN" for row in hardware_holds), "fixture hardware hold drift")
    hardware_status = json.loads((OUT / "fixture-hardware-status.json").read_text(encoding="utf-8"))
    need(hardware_status["hardware_selection_count"] == 13 and hardware_status["pcb_support_stack_count"] == 14, "fixture hardware status count drift")
    need(hardware_status["cover_fastener_stack_count"] == 8 and hardware_status["bench_foot_stack_count"] == 4, "fixture cover/foot status drift")
    need(not any(hardware_status[key] for key in (
        "fixture_built", "supplier_coc_received", "machining_process_released",
        "received_fit_validated", "torque_creep_validated", "foot_adhesion_load_validated",
        "fai_executed", "qualified_review_accepted", "fabrication_authority",
        "connection_authority", "powered_test_authority", "motion_authority",
        "walking_authority", "energization_authority",
    )), "fixture hardware authority overclaim")

    assembly = cq.importers.importStep(str(OUT / "HR30_E1_controls_only_fixture_candidate.step")).val()
    bounds = assembly.BoundingBox()
    need(abs(bounds.xlen - 360.009328) < 0.02 and abs(bounds.ylen - 240.009328) < 0.02, "assembly footprint drift")
    need(54.9 < bounds.zlen < 55.2, "assembly height drift")
    base = cq.importers.importStep(str(OUT / "HR30_E1_base_panel_candidate.step")).val()
    base_bounds = base.BoundingBox()
    need(abs(base_bounds.xlen - 360.0) < 0.02 and abs(base_bounds.ylen - 240.0) < 0.02 and abs(base_bounds.zlen - 6.0) < 0.02, "base panel dimensions drift")
    need((OUT / "HR30_E1_controls_only_fixture_candidate.glb").stat().st_size > 500_000, "GLB is implausibly small")
    hardware_cad = cq.importers.importStep(str(OUT / "HR30_E1_fixture_hardware_candidate.step")).val()
    hardware_bounds = hardware_cad.BoundingBox()
    need(hardware_bounds.xlen > 340.0 and hardware_bounds.ylen > 210.0 and hardware_bounds.zlen > 35.0, "fixture hardware CAD is implausibly incomplete")
    need((OUT / "HR30_E1_fixture_hardware_candidate.glb").stat().st_size > 40_000, "fixture hardware GLB is implausibly small")
    logic_cad = cq.importers.importStep(str(OUT / "HR30_E1_logic_harness_candidate.step")).val()
    logic_bounds = logic_cad.BoundingBox()
    need(logic_bounds.xlen > 210.0 and logic_bounds.ylen > 100.0 and logic_bounds.zlen > 30.0, "logic harness CAD is implausibly incomplete")
    integrated = cq.importers.importStep(str(OUT / "HR30_E1_controls_fixture_with_logic_harness_candidate.step")).val()
    integrated_bounds = integrated.BoundingBox()
    need(abs(integrated_bounds.xlen - bounds.xlen) < 0.02 and abs(integrated_bounds.ylen - bounds.ylen) < 0.02, "integrated harness changes fixture footprint")
    need((OUT / "HR30_E1_controls_fixture_with_logic_harness_candidate.glb").stat().st_size > 500_000, "integrated fixture GLB is implausibly small")
    j1_cad = cq.importers.importStep(str(OUT / "HR30_E1_J1_logic_power_cable_candidate.step")).val()
    j1_bounds = j1_cad.BoundingBox()
    need(j1_bounds.xlen > 1035.0 and 6.0 < j1_bounds.ylen < 20.0, "J1 manufacturing cable CAD is implausible")
    complete = cq.importers.importStep(str(OUT / "HR30_E1_controls_fixture_complete_logic_wiring_candidate.step")).val()
    complete_bounds = complete.BoundingBox()
    need(complete_bounds.xlen > 650.0 and complete_bounds.ylen >= bounds.ylen, "complete logic-wiring CAD is implausibly incomplete")
    need((OUT / "HR30_E1_controls_fixture_complete_logic_wiring_candidate.glb").stat().st_size > 500_000, "complete logic-wiring GLB is implausibly small")

    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 8 and all(row["state"] == "OPEN" for row in holds), "E1 open-hold drift")
    log = (OUT / "kicad-board-export.log").read_text(encoding="utf-8")
    need(log.count("exit=0") == 4, "KiCad board export count/result drift")
    need("Could not add 3D model" in log, "missing-model disclosure unexpectedly absent")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "font-size:14px" in page, "E1 guide violates legibility floor")
    need("<model-viewer" in page and "HR30_E1_controls_only_fixture_candidate.glb" in page, "interactive model missing")
    need("HR30_E1_controls_fixture_with_logic_harness_candidate.glb" in page and "27" in page and "54" in page, "interactive logic harness section missing")
    need("HR30_E1_controls_fixture_complete_logic_wiring_candidate.glb" in page and 'id="e1-j1-power-cable"' in page, "interactive J1 cable section missing")
    need(page.index('id="e1-j1-power-cable"') < page.index("</main>") < page.index("<footer>"), "J1 cable guide section escaped main")
    need("HR30_E1_fixture_hardware_candidate.glb" in page and 'id="e1-fixture-hardware"' in page, "interactive fixture hardware section missing")
    need(page.index('id="e1-fixture-hardware"') < page.index("</main>") < page.index("<footer>"), "fixture hardware guide section escaped main")
    need("\ufffd" not in page and "Ã" not in page and "Â" not in page, "E1 guide contains mojibake")
    need("This guide cannot authorize connection or power" in page, "authority boundary missing from guide")
    root_readme = (BODY / "README.md").read_text(encoding="utf-8")
    root_page = (BODY / "index.html").read_text(encoding="utf-8")
    need(root_readme.count("HR30-E1-CONTROLS-FIXTURE-P01-START") == 1, "root README marker drift")
    need(root_page.count("HR30-E1-CONTROLS-FIXTURE-P01-START") == 1, "root page marker drift")
    package_status = json.loads((BODY / "package-status.json").read_text(encoding="utf-8"))
    need(package_status["e1_controls_only_fixture_present"] and package_status["e1_native_pcb_count"] == 4, "root E1 status absent")
    need(package_status["e1_actuator_power_component_count"] == 0, "root status introduces actuator power")
    need(package_status["e1_logic_harness_candidate_present"] and package_status["e1_logic_harness_populated_conductor_count"] == 27, "root logic harness status absent")
    need(not package_status["e1_logic_harness_built"] and not package_status["e1_logic_harness_validated"], "root logic harness overclaim")
    need(package_status["e1_j1_logic_power_cable_candidate_present"] and package_status["e1_j1_logic_power_conductor_count"] == 2, "root J1 cable status absent")
    need(not package_status["e1_j1_logic_power_cable_built"] and not package_status["e1_j1_logic_power_cable_validated"], "root J1 cable overclaim")
    need(package_status["e1_fixture_hardware_candidate_present"] and package_status["e1_fixture_hardware_selection_count"] == 13, "root fixture hardware status absent")
    need(not package_status["e1_fixture_hardware_built"] and not package_status["e1_fixture_hardware_validated"], "root fixture hardware overclaim")
    need(not package_status["e1_fixture_built"] and not package_status["e1_connection_authority"] and not package_status["e1_powered_test_authority"], "root E1 authority overclaim")

    manifest = rows(OUT / "file-manifest.csv")
    need(len(manifest) == len(required) - 1 and len({row["file"] for row in manifest}) == len(manifest), "package manifest population drift")
    for row in manifest:
        path = OUT / row["file"]
        need(path.is_file() and int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"manifest mismatch {row['file']}")
        need(row["warning"] == WARNING, f"manifest warning drift {row['file']}")

    print("PASS: HR-30 E1 fixture uses 4 native PCBs / 14 defined support stacks, 8 physical cover fasteners and 4 full-height foot stacks, encloses all 8 data field ports, includes both logic harnesses plus J1, contains zero actuator-power hardware, and keeps every physical/authority gate false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
