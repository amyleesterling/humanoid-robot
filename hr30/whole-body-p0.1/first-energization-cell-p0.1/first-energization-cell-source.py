#!/usr/bin/env python3
"""Generate the HR-30 whole-body first-energization cell P0.1.

The cell is a static, no-motion development enclosure.  It places the real
neutral-pose HR-30 CAD on a supported platform, locates a rigid pelvis cradle,
clear guards, secondary position-only tethers, an exclusion zone, and external
operator/instrument stations.  It is not a walking gantry or rated fall-arrest
system and grants no work authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-cell-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "first-energization-cell-p0.1"
ROBOT_STEP = WHOLE / "HR-30_p00_neutral_stand_candidate.step"
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
IDENTIFIER = "HR30-FIRST-ENERGIZATION-CELL-P0.1"
DATE = "2026-08-18"
WARNING = (
    "PRELIMINARY - UNBUILT STATIC FIRST-ENERGIZATION CELL CANDIDATE - "
    "NOT A WALKING GANTRY OR RATED FALL-ARREST SYSTEM - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, "
    "WALKING OR ENERGIZATION"
)
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_step(path: Path) -> None:
    path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", path.read_bytes()))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty table: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def box(x: float, y: float, z: float, sx: float, sy: float, sz: float) -> cq.Shape:
    return cq.Workplane("XY").box(sx, sy, sz).translate((x, y, z)).val()


def rod(a: tuple[float, float, float], b: tuple[float, float, float], radius: float) -> cq.Shape:
    start = cq.Vector(*a)
    vector = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
    return cq.Solid.makeCylinder(radius, vector.Length, start, vector.normalized())


def frame_geometry() -> tuple[list[dict], dict[str, cq.Shape]]:
    rows: list[dict] = []
    shapes: dict[str, cq.Shape] = {}

    def add(member_id: str, role: str, center: tuple[float, float, float], size: tuple[float, float, float], cut_length: float) -> None:
        rows.append({
            "member_id": member_id, "role": role, "candidate_profile": "80/20 40-4040-Lite 40 x 40 mm",
            "center_x_mm": center[0], "center_y_mm": center[1], "center_z_mm": center[2],
            "size_x_mm": size[0], "size_y_mm": size[1], "size_z_mm": size[2],
            "candidate_cut_length_mm": cut_length, "end_preparation": "SQUARE CUT CANDIDATE; DFM REQUIRED",
            "structural_release": "NO", "warning": WARNING,
        })
        shapes[member_id] = box(*center, *size)

    # 1200 x 1000 x 1400 mm outside envelope.
    add("FR-BX-01", "BASE FRONT", (0, -480, 20), (1200, 40, 40), 1200)
    add("FR-BX-02", "BASE REAR", (0, 480, 20), (1200, 40, 40), 1200)
    add("FR-BY-01", "BASE LEFT", (-580, 0, 20), (40, 920, 40), 920)
    add("FR-BY-02", "BASE RIGHT", (580, 0, 20), (40, 920, 40), 920)
    for index, (x, y) in enumerate(((-580, -480), (580, -480), (-580, 480), (580, 480)), 1):
        add(f"FR-U-{index:02d}", "VERTICAL UPRIGHT", (x, y, 700), (40, 40, 1360), 1360)
    add("FR-TX-01", "TOP FRONT", (0, -480, 1380), (1200, 40, 40), 1200)
    add("FR-TX-02", "TOP REAR", (0, 480, 1380), (1200, 40, 40), 1200)
    add("FR-TY-01", "TOP LEFT", (-580, 0, 1380), (40, 920, 40), 920)
    add("FR-TY-02", "TOP RIGHT", (580, 0, 1380), (40, 920, 40), 920)
    add("FR-TC-01", "POSITION-ONLY TETHER CROSSBAR", (0, 0, 1360), (1120, 40, 40), 1120)
    return rows, shapes


def guard_geometry() -> tuple[list[dict], dict[str, cq.Shape]]:
    panels = [
        ("GP-LEFT", "FIXED LEFT", (-557, 0, 720), (6, 880, 1280), "FIXED"),
        ("GP-RIGHT", "FIXED RIGHT", (557, 0, 720), (6, 880, 1280), "FIXED"),
        ("GP-REAR", "FIXED REAR", (0, 457, 720), (1090, 6, 1280), "FIXED"),
        ("GP-FRONT-L", "FRONT LEFT DOOR", (-287, -457, 720), (540, 6, 1280), "HINGED OUTWARD"),
        ("GP-FRONT-R", "FRONT RIGHT DOOR", (287, -457, 720), (540, 6, 1280), "HINGED OUTWARD"),
        ("GP-ROOF", "TOP INFILL", (0, 0, 1357), (1090, 880, 6), "FIXED"),
    ]
    rows = [{
        "panel_id": pid, "role": role, "center_x_mm": c[0], "center_y_mm": c[1], "center_z_mm": c[2],
        "width_x_mm": s[0], "depth_y_mm": s[1], "height_z_mm": s[2],
        "candidate_material": "6 mm SABIC LEXAN 9030 OR 9034 POLYCARBONATE - EXACT GRADE SELECTION REQUIRED",
        "mounting": mounting, "impact_containment_credit": "NONE", "door_interlock_credit": "NONE",
        "state": "DIMENSIONED CAD CANDIDATE; GUARD ANALYSIS/TEST OPEN", "warning": WARNING,
    } for pid, role, c, s, mounting in panels]
    return rows, {pid: box(*c, *s) for pid, _, c, s, _ in panels}


def support_geometry() -> tuple[list[dict], dict[str, cq.Shape]]:
    items: list[tuple[str, str, tuple[float, float, float], tuple[float, float, float], str]] = [
        ("SP-PLATFORM", "ROBOT FOOT PLATFORM", (0, 0, 81), (700, 700, 18), "BOTH FEET FULLY SUPPORTED; NO WALKING"),
        ("SP-POST-L", "LEFT CRADLE POST", (-95, 185, 290), (60, 60, 400), "CUSTOM STRUCTURE; CAPACITY OPEN"),
        ("SP-POST-R", "RIGHT CRADLE POST", (95, 185, 290), (60, 60, 400), "CUSTOM STRUCTURE; CAPACITY OPEN"),
        ("SP-BEAM-L", "LEFT CRADLE ARM", (-70, 112, 497), (50, 190, 28), "TERMINATES AT P01 RESTRAINT RESERVATION"),
        ("SP-BEAM-R", "RIGHT CRADLE ARM", (70, 112, 497), (50, 190, 28), "TERMINATES AT P01 RESTRAINT RESERVATION"),
        ("SP-PAD-L", "LEFT PELVIS PAD", (-43, 32, 506), (34, 26, 40), "COMPLIANT PAD MATERIAL SELECTION REQUIRED"),
        ("SP-PAD-R", "RIGHT PELVIS PAD", (43, 32, 506), (34, 26, 40), "COMPLIANT PAD MATERIAL SELECTION REQUIRED"),
        ("SP-REAR-BRACE", "POST CROSS-BRACE", (0, 185, 450), (250, 36, 40), "CUSTOM STRUCTURE; CAPACITY OPEN"),
    ]
    rows = [{
        "support_id": pid, "role": role, "center_x_mm": c[0], "center_y_mm": c[1], "center_z_mm": c[2],
        "size_x_mm": s[0], "size_y_mm": s[1], "size_z_mm": s[2], "interface_basis": basis,
        "rated_load_n": "SELECTION REQUIRED", "proof_load_n": "NOT EXECUTED", "walking_credit": "NONE",
        "state": "DIMENSIONED CANDIDATE; STRUCTURAL REVIEW/PROOF OPEN", "warning": WARNING,
    } for pid, role, c, s, basis in items]
    return rows, {pid: box(*c, *s) for pid, _, c, s, _ in items}


def build_cad() -> dict:
    frame_rows, frame = frame_geometry()
    guard_rows, guards = guard_geometry()
    support_rows, supports = support_geometry()
    robot_raw = cq.importers.importStep(str(ROBOT_STEP)).val()
    robot_shift_z = 92.5
    robot = robot_raw.translate((0, 0, robot_shift_z))

    tether_points = [
        ("TR-01", (-210, 0, 1335), (-45, 42, 535)),
        ("TR-02", (210, 0, 1335), (45, 42, 535)),
    ]
    tethers = {pid: rod(a, b, 4.0) for pid, a, b in tether_points}
    tether_rows = [{
        "support_id": pid, "tether_id": pid, "top_anchor_xyz_mm": json.dumps(a), "robot_anchor_xyz_mm": json.dumps(b),
        "candidate_diameter_mm": 8, "role": "SECONDARY POSITION/RETENTION CANDIDATE ONLY",
        "rated_load_n": "SELECTION REQUIRED", "proof_load_n": "NOT EXECUTED", "fall_arrest_credit": "NONE",
        "walking_credit": "NONE", "state": "VISUAL ROUTE ONLY; HARDWARE/ANCHORS/CAPACITY OPEN", "warning": WARNING,
    } for pid, a, b in tether_points]

    exclusion = {
        "EZ-FRONT": box(0, -900, 2, 2000, 24, 4), "EZ-REAR": box(0, 900, 2, 2000, 24, 4),
        "EZ-LEFT": box(-988, 0, 2, 24, 1776, 4), "EZ-RIGHT": box(988, 0, 2, 24, 1776, 4),
    }
    stations = {
        "ST-ESTOP": cq.Compound.makeCompound([box(-880, -700, 420, 110, 110, 800), box(-880, -700, 845, 160, 160, 50)]),
        "ST-INSTRUMENT": box(860, -650, 500, 500, 360, 1000),
        "ST-FIRE": cq.Compound.makeCompound([box(865, 680, 140, 220, 220, 280), rod((865, 680, 280), (865, 680, 620), 45)]),
    }
    station_rows = [
        {"station_id":"ST-ESTOP","role":"REMOTE E-STOP PEDESTAL","center_xyz_mm":"[-880,-700,845]","minimum_clearance_mm":300,"installed":"NO","calibrated_or_verified":"NO","state":"LOCATION CANDIDATE; DEVICE/REACH/RESPONSE VALIDATION OPEN","warning":WARNING},
        {"station_id":"ST-INSTRUMENT","role":"ISOLATED INSTRUMENT CART ENVELOPE","center_xyz_mm":"[860,-650,500]","minimum_clearance_mm":300,"installed":"NO","calibrated_or_verified":"NO","state":"LOCATION CANDIDATE; INSTRUMENT SELECTION/CALIBRATION OPEN","warning":WARNING},
        {"station_id":"ST-FIRE","role":"FIRE-RESPONSE EQUIPMENT STAGING","center_xyz_mm":"[865,680,280]","minimum_clearance_mm":300,"installed":"NO","calibrated_or_verified":"NO","state":"LOCATION CANDIDATE; DEVICE/TRAINING/SITE APPROVAL OPEN","warning":WARNING},
    ]

    structure_assembly = cq.Assembly(name="HR30_FIRST_ENERGIZATION_CELL_STRUCTURE_P01_NOT_RELEASED")
    for key, shape in frame.items():
        structure_assembly.add(shape, name=key, color=cq.Color(0.08, 0.25, 0.48, 1))
    for key, shape in guards.items():
        structure_assembly.add(shape, name=key, color=cq.Color(0.42, 0.82, 1.0, 0.25))
    for key, shape in supports.items():
        structure_assembly.add(shape, name=key, color=cq.Color(0.92, 0.68, 0.08, 1))
    for key, shape in tethers.items():
        structure_assembly.add(shape, name=key, color=cq.Color(0.93, 0.55, 0.07, 1))
    for key, shape in exclusion.items():
        structure_assembly.add(shape, name=key, color=cq.Color(1.0, 0.68, 0.0, 1))
    for key, shape in stations.items():
        color = cq.Color(0.78, 0.10, 0.08, 1) if key == "ST-ESTOP" else cq.Color(0.10, 0.45, 0.72, 0.22)
        structure_assembly.add(shape, name=key, color=color)

    structure_parts = [*frame.values(), *guards.values(), *supports.values(), *tethers.values(), *exclusion.values(), *stations.values()]
    structure = cq.Compound.makeCompound(structure_parts)
    structure_step = OUT / "HR30_first_energization_cell_structure_candidate.step"
    cq.exporters.export(structure, str(structure_step)); clean_step(structure_step)
    structure_assembly.save(str(OUT / "HR30_first_energization_cell_structure_candidate.glb"), tolerance=0.75, angularTolerance=0.20)

    whole = cq.Compound.makeCompound([structure, robot])
    whole_step = OUT / "HR30_first_energization_cell_with_robot_candidate.step"
    cq.exporters.export(whole, str(whole_step)); clean_step(whole_step)
    structure_assembly.add(robot, name="HR30_P00_NEUTRAL_ROBOT_SHA_BOUND", color=cq.Color(0.78, 0.80, 0.83, 1))
    structure_assembly.save(str(OUT / "HR30_first_energization_cell_with_robot_candidate.glb"), tolerance=0.75, angularTolerance=0.20)

    write_csv(OUT / "frame-member-register.csv", frame_rows)
    write_csv(OUT / "guard-panel-register.csv", guard_rows)
    write_csv(OUT / "restraint-interface-register.csv", support_rows + tether_rows)
    write_csv(OUT / "operator-and-instrument-location-register.csv", station_rows)
    bounds = whole.BoundingBox()
    return {
        "frame_member_count": len(frame_rows), "guard_panel_count": len(guard_rows),
        "support_component_count": len(support_rows), "secondary_tether_count": len(tether_rows),
        "external_station_count": len(station_rows), "robot_translation_z_mm": robot_shift_z,
        "assembly_extent_mm": [round(bounds.xlen, 3), round(bounds.ylen, 3), round(bounds.zlen, 3)],
        "robot_step_sha256": sha(ROBOT_STEP),
    }


def publish(geometry: dict) -> None:
    dimensions = [
        ("CELL-OUTER", "GUARD FRAME OUTSIDE", 1200, 1000, 1400, "robot-centered world frame; floor Z=0"),
        ("CELL-INNER", "CLEAR GUARDED VOLUME APPROXIMATE", 1114, 914, 1314, "between panels and base/top members"),
        ("EXCLUSION", "FLOOR EXCLUSION ZONE", 2000, 1800, 0, "gold perimeter; access control procedure open"),
        ("PLATFORM", "FOOT SUPPORT PLATFORM", 700, 700, 18, "top Z=90 mm"),
        ("ROBOT", "SHA-BOUND P00 ROBOT IN CELL", 330, 152.5, 764.5, "translated +92.5 mm so foot bottom rests at Z=90 mm"),
        ("PELVIS-RESERVATION", "P01 RESTRAINT INTERFACE AFTER CELL TRANSLATION", 80, 52, 20, "X +/-40; Y 6..58; Z 496.5..516.5 mm"),
    ]
    write_csv(OUT / "cell-dimension-register.csv", [{
        "dimension_id": a, "description": b, "x_mm": c, "y_mm": d, "z_mm": e,
        "datum_or_basis": f, "validation_state": "CAD DEFINED; PHYSICAL VALIDATION OPEN", "warning": WARNING,
    } for a,b,c,d,e,f in dimensions])

    stages = [
        ("FER-E0", "UNPOWERED INSPECTION", "CELL OPTIONAL; ROBOT MAY BE IN CELL ONLY IF MECHANICALLY STABLE", "NO MOTION"),
        ("FER-E1", "UNPOWERED ELECTRICAL MEASUREMENTS", "USE SEPARATE E1 FIXTURE; WHOLE ROBOT REMAINS DISCONNECTED", "NO MOTION"),
        ("FER-E2", "COMPUTE/CONTROLLER BOOT", "USE CONTROLS-ONLY FIXTURE; NO ACTUATOR INTERFACES", "NO MOTION"),
        ("FER-E3", "SAFETY-LOGIC OBSERVATION", "USE CONTROLS-ONLY FIXTURE; CONTACTOR LOAD SIDE DE-ENERGIZED", "NO MOTION"),
        ("FER-E4", "ONE-ACTUATOR IDENTITY", "SEPARATE GUARDED BENCH FIXTURE; NOT THIS WHOLE-BODY CELL", "NO MOTION"),
        ("FER-E5", "ONE-BRANCH LOAD", "SEPARATE ISOLATED LOAD FIXTURE; NO ACTUATORS", "NO MOTION"),
        ("FER-E6", "WHOLE HARNESS POLARITY", "ROBOT IN CELL MAY BE USED ONLY AFTER G02/G10/G11 AND ALL REQUIRED GATES", "NO ACTUATORS CONNECTED"),
        ("FER-E7", "FIRST WHOLE-BODY STATIC RAIL OBSERVATION", "ROBOT RIGIDLY SUPPORTED AT PELVIS AND FEET; DOORS CLOSED; EXCLUSION ZONE ACTIVE", "TORQUE DISABLED; ZERO MOTION REQUEST"),
    ]
    write_csv(OUT / "stage-use-register.csv", [{
        "stage_id": a, "stage": b, "cell_use": c, "motion_boundary": d,
        "execution_state": "OPEN - NOT EXECUTED", "cell_authorizes_stage": "NO",
        "required_release": "ALL APPLICABLE FER GATES PLUS QUALIFIED SIGNOFF", "warning": WARNING,
    } for a,b,c,d in stages])

    bom = [
        ("CELL-B01", "40 x 40 mm T-slot frame members", "80/20", "40-4040-Lite", 13, "CUT LENGTHS IN FRAME REGISTER; WRITTEN QUOTE/DFM REQUIRED"),
        ("CELL-B02", "8-hole gusseted inside corner brackets", "80/20", "40-4338", 16, "CANDIDATE QUANTITY; JOINT CALCULATION/FASTENERS REQUIRED"),
        ("CELL-B03", "40-series leveling-caster base plates", "80/20", "40-2407", 4, "CANDIDATE ONLY; FOOTING/ANCHORAGE DESIGN OPEN"),
        ("CELL-B04", "leveling casters", "80/20", "2715", 4, "CANDIDATE ONLY; CATALOG LOAD IS NOT CELL/FALL RATING"),
        ("CELL-B05", "panel hinges for 6 mm panels", "80/20", "40-2080", 6, "CANDIDATE ONLY; DOOR DESIGN/RETENTION OPEN"),
        ("CELL-B06", "6 mm clear polycarbonate panels", "SABIC", "LEXAN 9030 OR 9034 - SELECTION REQUIRED", 6, "DIMENSIONS IN GUARD REGISTER; IMPACT CONTAINMENT UNVALIDATED"),
        ("CELL-B07", "panel retainers and door latches", "SELECTION REQUIRED", "SELECTION REQUIRED", 1, "COMPLETE SET; EXACT HARDWARE/RETENTION OPEN"),
        ("CELL-B08", "robot platform and pelvis cradle parts", "CUSTOM", "SELECTION REQUIRED", 8, "MATERIAL/WELD OR FASTENER DESIGN/CAPACITY/PROOF OPEN"),
        ("CELL-B09", "secondary tether assemblies", "SELECTION REQUIRED", "SELECTION REQUIRED", 2, "POSITION ONLY; ZERO FALL-ARREST CREDIT"),
        ("CELL-B10", "remote E-stop pedestal/device", "SELECTION REQUIRED", "SELECTION REQUIRED", 1, "LOCATION ENVELOPE ONLY; SAFETY CIRCUIT SELECTION/VALIDATION OPEN"),
    ]
    write_csv(OUT / "candidate-bom.csv", [{
        "item_id": a, "item": b, "manufacturer": c, "candidate_part_or_family": d, "quantity": e,
        "selection_state": f, "procurement_released": "NO", "warning": WARNING,
    } for a,b,c,d,e,f in bom])

    sources = [
        ("CELL-S01", "80/20", "40-4040-Lite product page", "live official page; accessed 2026-08-18", "https://8020.net/40-4040-lite.html", "40 x 40 mm 6063-T6 four-slot profile; machine guards/enclosures/work benches"),
        ("CELL-S02", "80/20", "40-4338 product page", "live official page; accessed 2026-08-18", "https://8020.net/fasteningmethods/externalfasteners/bracketsgussetscorners/standardgussetedbrackets/8holegussetedinsidecornerbracket/40-series.html", "40-series 8-hole gusseted inside corner bracket candidate"),
        ("CELL-S03", "80/20", "40-2407 product page", "live official page; accessed 2026-08-18", "https://8020.net/40-2407.html", "40-series leveling-caster base plate candidate"),
        ("CELL-S04", "80/20", "2715 product page", "live official page; accessed 2026-08-18", "https://8020.net/2715.html", "leveling-caster candidate; published product load is not credited as system rating"),
        ("CELL-S05", "80/20", "40-2080 product page", "live official page; accessed 2026-08-18", "https://8020.net/40-2080.html", "panel hinge candidate for plastic panels up to 6 mm"),
        ("CELL-S06", "SABIC", "LEXAN sheet portfolio brochure", "official Americas portfolio; accessed 2026-08-18", "https://www.sabic.com/en/images/sabic-lexan-sheet-portfolio-brochure-english-americas_tcm1010-5016.pdf", "9030/9034 general-purpose polycarbonate sheet; available gauge includes 6 mm"),
    ]
    write_csv(OUT / "primary-source-register.csv", [{
        "source_id": a, "manufacturer": b, "document": c, "revision_date": d, "url": e,
        "verified_scope": f, "not_verified": "WHOLE-CELL CAPACITY, GUARD IMPACT, RESTRAINT, FALL ARREST, SITE ACCEPTANCE", "warning": WARNING,
    } for a,b,c,d,e,f in sources])

    instruments = [
        ("IN-01", "ISOLATED CURRENT-LIMITED SOURCE", "ST-INSTRUMENT", "OUTPUT LIMIT/POLARITY/ISOLATION", "SELECTION/CALIBRATION REQUIRED"),
        ("IN-02", "VOLTAGE PROBES / DMM", "ST-INSTRUMENT", "ALL OBSERVED RAILS AND DC REFERENCE", "SELECTION/CALIBRATION REQUIRED"),
        ("IN-03", "CURRENT SHUNT / CLAMP", "ST-INSTRUMENT", "SOURCE AND SELECTED BRANCH", "SELECTION/CALIBRATION REQUIRED"),
        ("IN-04", "THERMAL CAMERA", "OUTSIDE RIGHT GUARD", "CONNECTORS, PDU, CONTROLLERS, ACTUATORS", "SELECTION/CALIBRATION REQUIRED"),
        ("IN-05", "E-STOP RESPONSE LOGGER", "ST-INSTRUMENT", "PERMIT/CONTACTOR/RAIL STATE", "SELECTION/CALIBRATION REQUIRED"),
        ("IN-06", "VIDEO RECORD", "OUTSIDE REAR/RIGHT GUARD", "ROBOT, OPERATORS, INDICATORS", "SELECTION/TIMESTAMP CORRELATION REQUIRED"),
    ]
    write_csv(OUT / "instrument-location-register.csv", [{
        "instrument_id": a, "instrument": b, "location": c, "measurement_scope": d,
        "selection_and_calibration": e, "installed": "NO", "abort_limits_frozen": "NO", "warning": WARNING,
    } for a,b,c,d,e in instruments])

    checks = [
        ("CELL-T01", "frame identity/dimensions", "every member and joint matches the frozen as-built register"),
        ("CELL-T02", "base anchorage and leveling", "cell cannot roll, rack, lift or tip under reviewed static/proof cases"),
        ("CELL-T03", "guard panel retention", "all panels/doors/retainers pass the approved inspection and proof procedure"),
        ("CELL-T04", "door state", "doors latch closed; any selected interlock is separately validated"),
        ("CELL-T05", "platform support", "both complete soles contact the level platform with no rocking"),
        ("CELL-T06", "pelvis cradle fit", "pads engage the P01 reservation without harness, cover or mechanism interference"),
        ("CELL-T07", "restraint proof", "reviewed cradle and anchors pass defined proof load with recorded deflection"),
        ("CELL-T08", "secondary tether fit", "tethers are slack/position-only and cannot create hidden primary restraint credit"),
        ("CELL-T09", "whole-body clearance", "robot and support remain inside guards in the approved static envelope"),
        ("CELL-T10", "exclusion zone", "floor boundary, access control and observer positions are physically established"),
        ("CELL-T11", "E-stop access", "operator can reach remote E-stop from the assigned station without entering zone"),
        ("CELL-T12", "instrumentation", "all selected instruments have valid calibration and frozen limits"),
        ("CELL-T13", "fire response", "site-specific equipment, evacuation and trained roles are approved"),
        ("CELL-T14", "dry rehearsal", "test lead, observer and stop operator complete an unpowered abort rehearsal"),
        ("CELL-T15", "configuration signoff", "G02, G10, G11 and all other applicable FER gates close on one frozen configuration"),
    ]
    write_csv(OUT / "inspection-traveler.csv", [{
        "check_id": a, "inspection": b, "acceptance": c, "result": "NOT EXECUTED",
        "evidence": "REQUIRED", "responsible_role": "QUALIFIED ROLE SELECTION REQUIRED", "warning": WARNING,
    } for a,b,c in checks])

    holds = [
        ("CELL-H01", "frame joints/base anchorage", "structural calculation, exact fasteners, floor/base condition, proof plan and qualified acceptance"),
        ("CELL-H02", "pelvis cradle capacity", "load cases, material/joints, pad forces, proof load and received as-built inspection"),
        ("CELL-H03", "guard containment", "hazard analysis, panel grade/thickness, retention, impact/deflection test and qualified acceptance"),
        ("CELL-H04", "secondary tethers", "exact anchors/hardware and load evidence; no fall-arrest credit until separately released"),
        ("CELL-H05", "door/access control", "latch/interlock selection, defeat prevention, safety allocation and validation"),
        ("CELL-H06", "test-site commissioning", "floor, clearance, egress, fire response, observer and stop-role signoff"),
        ("CELL-H07", "instrumentation/limits", "selected calibrated instruments and frozen voltage/current/temperature/time abort limits"),
        ("CELL-H08", "whole-body fit", "physical robot/platform/cradle/guard/envelope inspection with measured clearances"),
        ("CELL-H09", "FER gate closure", "FER-G01 through G12 closed with traceable evidence on the same configuration"),
        ("CELL-H10", "future walking restraint", "separate rated dynamic gantry and walking test architecture; explicitly outside this cell"),
    ]
    write_csv(OUT / "open-holds.csv", [{
        "hold_id": a, "unresolved_item": b, "closure_evidence": c, "state": "OPEN",
        "authority": AUTHORITY, "warning": WARNING,
    } for a,b,c in holds])

    source_binding = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "robot_source": ROBOT_STEP.relative_to(ROOT).as_posix(), "robot_source_sha256": sha(ROBOT_STEP),
        "robot_source_extent_mm": [330.0000002, 152.5000002, 764.5000002],
        "robot_translation_z_mm": geometry["robot_translation_z_mm"],
        "pelvis_reservation_source": "component-envelope-schedule.csv PELVIS_RESTRAINT_INTERFACE_ENVELOPE",
        "pelvis_reservation_cell_xyz_mm": {"x": [-40, 40], "y": [6, 58], "z": [496.5, 516.5]},
    }
    (OUT / "source-binding.json").write_text(json.dumps(source_binding, indent=2) + "\n", encoding="utf-8")

    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING, **geometry,
        "whole_robot_cad_bound": True, "complete_humanoid_visible": True,
        "static_first_energization_use_only": True, "walking_gantry": False,
        "structure_calculated": False, "restraint_rated": False, "guard_impact_validated": False,
        "fabricated": False, "site_commissioned": False, "instrumentation_calibrated": False,
        "fire_response_approved": False, "fer_g02_state": "OPEN - NOT EXECUTED",
        "fer_g10_state": "OPEN - NOT EXECUTED", "fer_g11_state": "OPEN - NOT EXECUTED",
        "fall_arrest_credit": False, "walking_credit": False, "functional_safety_credit": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False,
        "walking_authority": False, "energization_authority": False,
    }
    (OUT / "cell-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# HR-30 first-energization cell P0.1\n\n**{WARNING}**\n\n"
        "This package places the SHA-bound complete neutral-pose HR-30 assembly inside a dimensioned "
        "1200 x 1000 x 1400 mm guarded cell. Both feet rest on a fixed platform and the pelvis is held by "
        "a rigid cradle located at the reserved P01 interface. Two overhead lines are position-only secondary "
        "tether candidates with zero fall-arrest credit. The static cell does not authorize or support walking.\n\n"
        "Editable source, STEP, GLB, dimensions, frame members, guards, restraint interfaces, stage use, "
        "instrument locations, BOM, sources, inspection traveler and open holds are included. The cell is unbuilt; "
        "FER-G02, G10 and G11 remain open, as do all other readiness gates and every work authority.\n",
        encoding="utf-8",
    )

    stage_cards = "".join(
        f'<button class="stage" data-stage="{a}"><strong>{a}</strong><span>{html.escape(b)}</span><small>{html.escape(c)}</small></button>'
        for a,b,c,_ in stages
    )
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 first-energization cell</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#91cce9;--red:#8f1d1d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1200px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,42px);color:var(--blue)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:17px}}.card,.panel,.viewer{{background:white;border:2px solid var(--line);border-radius:18px;padding:19px;margin:18px 0;overflow:hidden}}.metric{{font-size:clamp(32px,5vw,52px);font-weight:900;color:var(--blue)}}model-viewer{{display:block;width:100%;height:clamp(560px,72vh,820px);background:radial-gradient(circle,#fff,var(--sky))}}.stages{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}.stage{{font:inherit;text-align:left;padding:15px;border:2px solid var(--line);border-radius:12px;background:white;color:var(--ink);cursor:pointer}}.stage strong,.stage span,.stage small{{display:block}}.stage strong{{font-size:18px;color:var(--blue)}}.stage span{{font-weight:800}}.stage small{{font-size:14px;margin-top:7px}}.stage.active{{border-color:#805600;background:#fff4c7}}.notice{{border-left:8px solid var(--red);padding:16px;background:#fff0f0}}a{{color:#075b9b;font-weight:800}}li{{margin:.55rem 0}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{height:520px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>The complete robot now has a physical static test cell.</h1><p>A dimensioned enclosure, clear guards, supported feet, rigid pelvis cradle, exclusion zone and external test stations surround the actual HR-30 CAD.</p></header><main><section class="viewer"><model-viewer src="HR30_first_energization_cell_with_robot_candidate.glb" alt="Interactive complete 762 millimetre HR-30 humanoid inside a guarded first-energization cell" camera-controls camera-orbit="25deg 72deg 105%" field-of-view="34deg" shadow-intensity="0.9" exposure="1.0"></model-viewer><p><a href="HR30_first_energization_cell_with_robot_candidate.step">Whole cell + robot STEP</a> · <a href="HR30_first_energization_cell_structure_candidate.step">cell-only STEP</a> · <a href="cell-dimension-register.csv">dimensions</a> · <a href="inspection-traveler.csv">inspection traveler</a>.</p></section><section class="grid"><article class="card"><div class="metric">1200 × 1000 × 1400</div><p>mm guarded frame envelope.</p></article><article class="card"><div class="metric">6</div><p>dimensioned clear polycarbonate panels.</p></article><article class="card"><div class="metric">2 + 2</div><p>supported feet and pelvis contact pads.</p></article><article class="card"><div class="metric">0</div><p>motion, walking, fall-arrest or energization authority.</p></article></section><section><h2>What physically restrains the robot</h2><div class="grid"><article class="card"><h3>Feet stay planted</h3><p>Both full soles rest on a 700 × 700 mm rigid platform. The cell is not a suspended walking rig.</p></article><article class="card"><h3>Pelvis carries the restraint</h3><p>Twin posts and arms terminate in two pads at the P01 pelvis reservation. Exact load capacity and proof remain open.</p></article><article class="card"><h3>Tethers are secondary only</h3><p>Two visible overhead routes locate future hardware but carry zero rated-load or fall-arrest credit.</p></article></div></section><section><h2>Stage-by-stage boundary</h2><p>Select a stage to highlight its planned use. Every stage remains open and unexecuted.</p><div class="stages">{stage_cards}</div><div id="stage-detail" class="panel">Choose a stage. No selection authorizes work.</div></section><section class="panel"><h2>Three external readiness stations</h2><ul><li><strong>Remote E-stop pedestal:</strong> outside the front-left exclusion boundary.</li><li><strong>Instrument cart:</strong> outside the front-right guard for isolated probes and calibrated logging.</li><li><strong>Fire-response staging:</strong> outside the rear-right guard; exact equipment and site procedure remain open.</li></ul></section><section class="notice"><h2>What this does not solve</h2><p>The frame and cradle are not structurally released; guards have no impact-containment credit; tethers are not fall arrest; the site is not commissioned; instruments and abort limits are not selected; FER-G02, G10 and G11 remain open. E7 and all powered work remain prohibited.</p></section><section class="panel"><h2>Engineering package</h2><p><a href="first-energization-cell-source.py">editable source</a> · <a href="frame-member-register.csv">frame</a> · <a href="guard-panel-register.csv">guards</a> · <a href="restraint-interface-register.csv">restraint</a> · <a href="operator-and-instrument-location-register.csv">stations</a> · <a href="instrument-location-register.csv">instrumentation</a> · <a href="candidate-bom.csv">BOM</a> · <a href="primary-source-register.csv">manufacturer sources</a> · <a href="open-holds.csv">open holds</a>.</p></section></main><footer>{html.escape(WARNING)}</footer><script>const details={json.dumps({a: f'{b}: {c}. Motion boundary: {d}. State: OPEN - NOT EXECUTED.' for a,b,c,d in stages})};document.querySelectorAll('.stage').forEach(button=>button.addEventListener('click',()=>{{document.querySelectorAll('.stage').forEach(x=>x.classList.remove('active'));button.classList.add('active');document.getElementById('stage-detail').textContent=details[button.dataset.stage]+' No authority is granted.';}}));</script></body></html>''', encoding="utf-8")


def integrate() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "first_energization_cell_present": True, "first_energization_cell_whole_robot_bound": True,
        "first_energization_cell_static_use_only": True, "first_energization_cell_walking_gantry": False,
        "first_energization_cell_structure_calculated": False, "first_energization_cell_restraint_rated": False,
        "first_energization_cell_guard_impact_validated": False, "first_energization_cell_fabricated": False,
        "first_energization_cell_site_commissioned": False, "first_energization_cell_instrumentation_calibrated": False,
        "fer_g02_closed": False, "fer_g10_closed": False, "fer_g11_closed": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    start, end = "<!-- HR30-FIRST-ENERGIZATION-CELL-P01-START -->", "<!-- HR30-FIRST-ENERGIZATION-CELL-P01-END -->"
    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Whole-body first-energization cell\n\nThe [interactive first-energization-cell guide](first-energization-cell-p0.1/index.html) places the SHA-bound complete neutral-pose robot inside a dimensioned **1200 x 1000 x 1400 mm** guarded frame. Both feet are supported and a rigid cradle locates the reserved pelvis interface. The two overhead routes are secondary position-only tether candidates, not fall arrest. The cell is unbuilt, FER-G02/G10/G11 remain open, and it grants no powered-test, motion, walking or energization authority.\n{end}\n'''
    readme.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="first-energization-cell"><h2>The complete robot now has a physical static first-energization cell</h2><div class="grid"><article class="card pass"><div class="metric">1200 × 1000 × 1400</div><p>mm dimensioned guarded frame around the SHA-bound whole robot.</p></article><article class="card pass"><h3>Supported, not suspended</h3><p>Both feet rest on a platform and a rigid pelvis cradle carries the primary restraint intent.</p></article><article class="card hold"><h3>Not a walking gantry</h3><p>Structure, guards, restraint, site, instruments and all FER gates remain unvalidated and open.</p></article></div><p><a href="first-energization-cell-p0.1/index.html">Open the interactive cell guide</a>.</p></section>{end}'''
    text = text.replace("</main>", section + "</main>", 1)
    page.write_text(text, encoding="utf-8")


def manifest_release() -> None:
    shutil.copy2(Path(__file__), OUT / "first-energization-cell-source.py")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{
        "path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size,
        "sha256": sha(p), "warning": WARNING,
    } for p in sorted(files)])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    result = subprocess.run([str(CAD_PYTHON), "-c", code], cwd=ROOT)
    if result.returncode:
        raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    print("first-energization cell: CAD", flush=True)
    geometry = build_cad()
    print("first-energization cell: registers and guide", flush=True)
    publish(geometry)
    integrate()
    manifest_release()
    print(json.dumps({"identifier": IDENTIFIER, **geometry, "authorities": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
