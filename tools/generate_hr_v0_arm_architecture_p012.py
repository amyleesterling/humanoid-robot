#!/usr/bin/env python3
"""Generate the R273 P0.12 access-well J2-stop development candidate.

P0.12 retains P0.11's mixed-side reinforcement, but restores the original
9.525 mm A04 clamped grip by machining four rear tool wells through C07's
added web.  Hardware identity, tightening, locking, preload and proof remain
unselected and unreleased.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_arm_architecture_p011 as p011


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
REV = "HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE"
STOP_REV = "HR-V0-J2-STOP-P0.5"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
STOCK_T = 25.4
BACK_EXTENSION = STOCK_T - arm.PLATE_T
C06_WEB_INNER = 20.0
C07_WEB_INNER = 12.0
ACCESS_WELL_DIAMETER = 5.2
ACCESS_WELL_DEPTH = BACK_EXTENSION
HEAD_MAX_DIAMETER = 4.5
HEAD_MAX_HEIGHT = 2.5
S102_BROAD_SHEET_T = 1.4
SCREEN_SCREW_LENGTH = 18.0
SCREEN_WASHER_T = 0.55
SCREEN_NUT_OVERALL = 4.5
THREAD_PITCH = 0.45


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def side_web_with_access(y0: float, *, outer: float, inner: float, top: float) -> cq.Shape:
    """P0.11 webs with C07 rear access wells terminating at the base plane."""
    shapes: list[cq.Shape] = []
    web_top = min(p011.WEB_TOP, top - 5.0)
    is_c06 = top > 30.0
    web_inner = C06_WEB_INNER if is_c06 else C07_WEB_INNER
    for sign in (-1.0, 1.0):
        points = [
            (sign * web_inner, -20.0),
            (sign * outer, -20.0),
            (sign * outer, top),
            (sign * inner, top),
            (sign * inner, web_top),
            (sign * web_inner, web_top),
        ]
        if sign < 0:
            points.reverse()
        if is_c06:
            web = arm._profile_plate(points, y0 + arm.PLATE_T, BACK_EXTENSION)
            web = cq.Workplane(obj=web).faces("<Y").edges().fillet(p011.STEP_BLEND_R).val()
        else:
            web = arm._profile_plate(points, y0 - BACK_EXTENSION, BACK_EXTENSION)
            web = cq.Workplane(obj=web).faces(">Y").edges().fillet(p011.STEP_BLEND_R).val()
            for x in (-16.0, 16.0):
                for z in (-8.0, 8.0):
                    well = cq.Solid.makeCylinder(
                        ACCESS_WELL_DIAMETER / 2.0,
                        ACCESS_WELL_DEPTH,
                        cq.Vector(x, y0 - BACK_EXTENSION, z),
                        cq.Vector(0, 1, 0),
                    )
                    web = web.cut(well)
        shapes.append(web)
    return cq.Compound.makeCompound(shapes)


def rewrite_identity() -> None:
    replacements = {
        "P0.11": "P0.12",
        "p011-status.json": "p012-status.json",
        "R272": "R273",
        "mixed-side side-web": "access-well side-web",
        "mixed-side side webs": "access-well side webs",
    }
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")


def fastener_envelope_distance() -> tuple[float, float]:
    """Exact-kernel nominal distance from simple hardware envelopes to XM540."""
    body = arm.rotate_x(arm.import_step("XMHD-540.N101.I101.STP"), 90.0).translate((0.0, arm.J2_Y, 0.0))
    shanks: list[cq.Shape] = []
    inner: list[cq.Shape] = []
    seat_y = 32.0 + arm.PLATE_T + arm.UPPER_BEAM_L
    s102_inner_y = seat_y + arm.PLATE_T + S102_BROAD_SHEET_T
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            shanks.append(cq.Solid.makeCylinder(1.25, SCREEN_SCREW_LENGTH, cq.Vector(x, seat_y, z), cq.Vector(0, 1, 0)))
            inner.append(cq.Solid.makeCylinder(3.0, SCREEN_WASHER_T + SCREEN_NUT_OVERALL, cq.Vector(x, s102_inner_y, z), cq.Vector(0, 1, 0)))
    return body.distance(cq.Compound.makeCompound(shanks)), body.distance(cq.Compound.makeCompound(inner))


def joint_demand_rows() -> list[dict[str, object]]:
    contact = json.loads((OUT / "cad-contact-normal-evidence.json").read_text(encoding="utf-8"))["selected_conservative_solution"]
    static = list(csv.DictReader((OUT / "corrected-static-stop-screen.csv").open(newline="", encoding="utf-8-sig")))
    force = float(static[-1]["single_rail_normal_force_n"])
    nx, ny, nz = (float(value) for value in contact["normal_fixed_to_moving"])
    px, py, pz = (float(value) for value in contact["fixed_point_mm"])
    interface_y = arm.J2_Y - 51.5
    rx, ry, rz = px, py - interface_y, pz
    fx, fy, fz = force * nx, force * ny, force * nz
    mx = ry * fz - rz * fy
    my = rz * fx - rx * fz
    mz = rx * fy - ry * fx
    sum_x2 = 4.0 * 16.0**2
    sum_z2 = 4.0 * 8.0**2
    polar = sum_x2 + sum_z2
    reactions = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            axial = abs(fy / 4.0 + mz * x / sum_x2 - mx * z / sum_z2)
            shear_x = fx / 4.0 + my * z / polar
            shear_z = fz / 4.0 - my * x / polar
            shear = math.hypot(shear_x, shear_z)
            reactions.append((x, z, axial, shear, math.hypot(axial, shear)))
    maximum = max(reactions, key=lambda item: item[-1])
    tensile_area = math.pi / 4.0 * (2.5 - 0.9382 * THREAD_PITCH) ** 2
    shank_area = math.pi * 2.5**2 / 4.0
    axial_stress = maximum[2] / tensile_area
    shear_stress = maximum[3] / shank_area
    return [{
        "case_id": "A04-ENDPOINT-GRAVITY-SINGLE-RAIL-DEMAND",
        "contact_side": "+X rail; mirrored -X gives the same maximum magnitude",
        "normal_resultant_n": f"{force:.3f}",
        "force_components_xyz_n": f"{fx:.3f};{fy:.3f};{fz:.3f}",
        "interface_moments_xyz_nmm": f"{mx:.3f};{my:.3f};{mz:.3f}",
        "elastic_group_max_axis_x_mm": f"{maximum[0]:.3f}",
        "elastic_group_max_axis_z_mm": f"{maximum[1]:.3f}",
        "maximum_absolute_axial_reaction_n": f"{maximum[2]:.3f}",
        "maximum_in_plane_shear_reaction_n": f"{maximum[3]:.3f}",
        "maximum_combined_reaction_n": f"{maximum[4]:.3f}",
        "nominal_m2p5_tensile_area_mm2_formula_only": f"{tensile_area:.4f}",
        "nominal_demand_axial_stress_mpa": f"{axial_stress:.3f}",
        "nominal_demand_shear_stress_mpa": f"{shear_stress:.3f}",
        "model_boundary": "absolute elastic bolt-group demand only; sign, preload, slip, prying, frame flexibility, contact, tolerance, fatigue, shock and allowables unresolved",
        "result": "DEMAND CALCULATED - NO CAPACITY OR PASS CLAIM",
        "warning": WARNING,
    }]


def main() -> int:
    p011.OUT = OUT
    p011.REV = REV
    p011.STOP_REV = STOP_REV
    p011.C07_WEB_INNER = C07_WEB_INNER
    p011.side_web_boss = side_web_with_access
    result = p011.main()
    if result:
        return result

    old = OUT / "p011-status.json"
    if old.exists():
        old.rename(OUT / "p012-status.json")
    rewrite_identity()

    interfaces = list(csv.DictReader((OUT / "interface-schedule.csv").open(newline="", encoding="utf-8")))
    for row in interfaces:
        if row["interface"] == "A04":
            row["pattern"] = "4 x diameter 2.70 through the original 9.525 mm C07 land at X=+/-16 Z=+/-8; 4 x diameter 5.20 rear access wells through the 15.875 mm added web terminate at the screw-head seat plane"
            row["fasteners"] = "M2.5 x 18 ISO 4762 screw + M2.5 washer + prevailing-torque nut dimensional stack SCREEN CANDIDATE; exact available order codes, strength, torque, locking and reuse SELECTION REQUIRED"
            row["status"] = "axis_and_nominal_envelope_screened; exact procurement, tolerance, installation and proof open"
    write_csv(OUT / "interface-schedule.csv", interfaces)

    screw_tip_beyond_nut = SCREEN_SCREW_LENGTH - (arm.PLATE_T + S102_BROAD_SHEET_T + SCREEN_WASHER_T + SCREEN_NUT_OVERALL)
    body_to_shank, body_to_inner = fastener_envelope_distance()
    write_csv(OUT / "a04-fastener-envelope-screen.csv", [{
        "screen_id": "A04-ENV-01",
        "c07_original_grip_mm": f"{arm.PLATE_T:.3f}",
        "c07_added_web_mm": f"{BACK_EXTENSION:.3f}",
        "access_well_diameter_mm": f"{ACCESS_WELL_DIAMETER:.3f}",
        "access_well_depth_mm": f"{ACCESS_WELL_DEPTH:.3f}",
        "socket_head_max_diameter_mm": f"{HEAD_MAX_DIAMETER:.3f}",
        "radial_head_clearance_mm": f"{(ACCESS_WELL_DIAMETER - HEAD_MAX_DIAMETER) / 2.0:.3f}",
        "minimum_inner_web_ligament_mm_nominal": f"{16.0 - ACCESS_WELL_DIAMETER / 2.0 - C07_WEB_INNER:.3f}",
        "screen_screw_length_mm": f"{SCREEN_SCREW_LENGTH:.3f}",
        "screen_grip_plus_frame_washer_nut_mm": f"{arm.PLATE_T + S102_BROAD_SHEET_T + SCREEN_WASHER_T + SCREEN_NUT_OVERALL:.3f}",
        "screen_thread_beyond_nut_mm": f"{screw_tip_beyond_nut:.3f}",
        "screen_thread_beyond_nut_pitches": f"{screw_tip_beyond_nut / THREAD_PITCH:.3f}",
        "nominal_shank_envelope_to_exact_xm540_mm": f"{body_to_shank:.6f}",
        "nominal_washer_nut_envelope_to_exact_xm540_mm": f"{body_to_inner:.6f}",
        "result": "NOMINAL GEOMETRY SCREEN PASS - PROCUREMENT/TOLERANCE/TOOL/PHYSICAL PROOF OPEN",
        "warning": WARNING,
    }])
    write_csv(OUT / "a04-hardware-source-register.csv", [
        {"item":"screw dimensional screen","manufacturer_or_supplier":"Accu","catalog_identity":"SSCF-M2.5-16-A2 and SSC-M2.5-18-A4 reference dimensions","official_source":"https://www.accu.co.uk/metric-cap-head-screws/3809-SSCF-M2-5-16-A2 ; https://www.accu.co.uk/metric-cap-head-screws/15872-SSC-M2-5-18-A4","document_revision_or_access_date":"live catalog checked 2026-08-12","verified_fields":"M2.5x0.45; ISO 4762/DIN 912; 4.5 mm max head diameter; 2.5 mm max head height; 2 mm socket; 16/18 mm lengths","availability":"pages report discontinued/out of stock/available offline","selection_state":"SELECTION REQUIRED - REFERENCE DIMENSIONS ONLY","warning":WARNING},
        {"item":"washer dimensional screen","manufacturer_or_supplier":"Accu","catalog_identity":"HPW-M2.5-A4","official_source":"https://www.accu.co.uk/metric-flat-washers/72503-HPW-M2-5-A4","document_revision_or_access_date":"catalog specification updated 2026-08-11; checked 2026-08-12","verified_fields":"DIN 125; ID 2.7 +0.14/-0; OD 6 +0/-0.3; thickness 0.55 +0/-0.1 mm","availability":"page reports discontinued/out of stock/available offline","selection_state":"SELECTION REQUIRED - REFERENCE DIMENSIONS ONLY","warning":WARNING},
        {"item":"prevailing-torque nut dimensional screen","manufacturer_or_supplier":"Accu / Lanfranco","catalog_identity":"HLFLN-M2.5-A4-80","official_source":"https://www.accu.co.uk/prevailing-torque-locking-nuts/986845-HLFLN-M2-5-A4-80","document_revision_or_access_date":"catalog specification/stock record 2026-07-24; checked 2026-08-12","verified_fields":"M2.5x0.45; A4-80; NFE 25-411; 5 mm AF; 4.5 mm overall; 2.3 mm nut body","availability":"current purchasability not accepted; supplier quote required","selection_state":"SELECTION REQUIRED - REFERENCE DIMENSIONS ONLY","warning":WARNING},
        {"item":"S102 interface","manufacturer_or_supplier":"ROBOTIS","catalog_identity":"FR13-S102K drawing / STEP","official_source":"cad/vendor/robotis/FR13-S102K.pdf ; cad/vendor/robotis/FR13-S102K.stp","document_revision_or_access_date":"drawing date 2026-01-07; controlled STEP SHA in interface-feature-evidence.csv","verified_fields":"four selected tapped-through axes at X +/-16 Z +/-8; broad sheet C1.4 callout","availability":"controlled reference files; received-part inspection still required","selection_state":"REFERENCE VERIFIED - APPLICATION/RECEIPT OPEN","warning":WARNING},
    ])
    write_csv(OUT / "a04-joint-demand-screen.csv", joint_demand_rows())

    status_path = OUT / "p012-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "identifier": REV,
        "stop_identifier": STOP_REV,
        "round": "R273",
        "parent": "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE",
        "c07_rear_access_well_diameter_mm": ACCESS_WELL_DIAMETER,
        "c07_rear_access_well_depth_mm": ACCESS_WELL_DEPTH,
        "c07_original_a04_clamped_grip_restored_mm": arm.PLATE_T,
        "c07_side_web_inner_x_mm": C07_WEB_INNER,
        "c07_m2p5_hole_depth_changed": False,
        "c07_m2p5_access_wells_added": True,
        "c07_m2p5_fastener_stack": "DIMENSIONAL SCREEN CANDIDATE - EXACT AVAILABLE HARDWARE/INSTALLATION SELECTION REQUIRED",
        "interface_change_note": "Contact planes and all six C07 hole axes are retained; four rear access wells restore the original 9.525 mm A04 clamped grip while changing the surrounding web envelope.",
        "selected": False,
        "physical_evidence_complete": False,
        "qualified_review_complete": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    changes = list(csv.DictReader((OUT / "design-change-register.csv").open(newline="", encoding="utf-8")))
    for change in changes:
        if change["change_id"] == "R273-CH-02":
            change["change"] = "20 mm catch rails with rear-side webs beginning at |X|=12 mm; four 5.20 mm rear access wells terminate at the original A04 screw-head seat plane; existing 1 mm contact recess retained"
        elif change["change_id"] == "R273-CH-03":
            change["change"] = "C06 added depth is entirely +Y/contact-side; C07 added depth is entirely -Y/rear-side around four access wells; modeled R2 step blends"
    changes.append({"change_id":"R273-CH-04","part_id":"MV0-C07 A04","change":"replace full-depth 2.70 mm web bores with four 5.20 mm rear access wells terminating at the original screw-head seat plane; retain 2.70 mm clearance through the original 9.525 mm land","preserved_interfaces":"four A04 axes, S102 contact plane, C07 stop contact face and central M5 axes","state":"UNSELECTED NOMINAL GEOMETRY CANDIDATE; HARDWARE/TOOL/TOLERANCE/PROOF OPEN","warning":WARNING})
    write_csv(OUT / "design-change-register.csv", changes)

    analysis_path = OUT / "j2-positive-stop-analysis.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    analysis["architecture"] = "Twin 18 mm C06 moving rails against 20 mm C07 catches; C06 uses a +Y contact-side web, while C07 uses a -Y rear web with four access wells that restore the original A04 screw-head seat plane; the C06 striker top is retuned to 36.026374 mm for nominal 118 degree contact."
    analysis["configuration_state"] = "UNSELECTED P0.12 CAD CANDIDATE"
    analysis_path.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")

    holds = list(csv.DictReader((OUT / "open-holds.csv").open(newline="", encoding="utf-8")))
    holds.extend([
        {"hold_id":"R273-H13","hold":"Select currently purchasable exact A04 screw, washer, prevailing-torque nut and straight 2 mm installation tool with certificates and complete tolerances","state":"OPEN","closure_evidence":"accepted supplier quote/datasheets, received identities, certificates and dimensional inspection","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
        {"hold_id":"R273-H14","hold":"Develop A04 tightening, anti-galling, locking, witness-mark, reuse and proof procedure against the exact received stack","state":"OPEN","closure_evidence":"qualified bolted-joint calculation, calibrated installation trials, prevailing-torque/preload evidence and physical proof","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
        {"hold_id":"R273-H15","hold":"Validate access-well tool reach, head seating, chip/deburr control, inner-web ligament and no-contact hardware envelope on received C07/S102/XM540","state":"OPEN","closure_evidence":"FAI, borescope/photos, gauges, dry-fit record and accepted tolerance analysis","release_effect":"BLOCKS P0.12 SELECTION/FABRICATION/MOTION","warning":WARNING},
    ])
    write_csv(OUT / "open-holds.csv", holds)
    acceptance = list(csv.DictReader((OUT / "acceptance-matrix.csv").open(newline="", encoding="utf-8")))
    for index, hold in enumerate(holds[-3:], 13):
        acceptance.append({"acceptance_id":f"R273-ACC-{index:02d}","criterion":hold["hold"],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(OUT / "acceptance-matrix.csv", acceptance)

    summary_path = OUT / "architecture-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["revision"] = REV
    summary["disposition"] = "unselected P0.12 access-well side-web stop candidate; exact available hardware, installation, joined-load, nonlinear, physical and qualified closure remain open"
    summary.pop("side_web_stop_candidate", None)
    summary["access_well_stop_candidate"] = status
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {REV}; nominal A04 envelope closes, selection and physical proof remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
