#!/usr/bin/env python3
"""Generate R277 P0.13 J2 bonded-pad-pocket review geometry.

P0.13 retains every P0.12 metal-stop interface and adds two shallow pockets
to C07.  The nominal pocket depth is a visualization/DFM screen only: the
finished depth is a dependent feature set after measuring the received
pad/adhesive stack.  The surrounding metal face remains the structural stop.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_arm_architecture_p012 as p012


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
REV = "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE"
STOP_REV = "HR-V0-J2-STOP-P0.6-PAD-POCKET"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

PAD_W = 12.0
PAD_H = 40.0
PAD_R = 1.5
PAD_NOMINAL_T = 0.61
PAD_MIN_T = 0.53
PAD_MAX_T = 0.69
POCKET_W = 12.4
POCKET_H = 40.4
POCKET_R = 2.0
POCKET_SCREEN_DEPTH = 0.52
POCKET_DEPTH_TOL = 0.02
TARGET_PROTRUSION = 0.15
ACCEPT_PROTRUSION_MIN = 0.10
ACCEPT_PROTRUSION_MAX = 0.20
RAIL_CENTERS_X = (-44.0, 44.0)
POCKET_CENTER_Z = 1.0
FACE_Y = arm.PLATE_T - arm.STOP_CATCH_FACE_RECESS_MM


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def rounded_prism_y(cx: float, cz: float, width: float, height: float, radius: float,
                    y0: float, depth: float) -> cq.Shape:
    """Rounded rectangle in X/Z extruded in +Y."""
    shape = cq.Solid.makeBox(width - 2 * radius, depth, height,
                             cq.Vector(cx - width / 2 + radius, y0, cz - height / 2))
    shape = shape.fuse(cq.Solid.makeBox(width, depth, height - 2 * radius,
                                        cq.Vector(cx - width / 2, y0, cz - height / 2 + radius)))
    for x in (cx - width / 2 + radius, cx + width / 2 - radius):
        for z in (cz - height / 2 + radius, cz + height / 2 - radius):
            shape = shape.fuse(cq.Solid.makeCylinder(radius, depth, cq.Vector(x, y0, z), cq.Vector(0, 1, 0)))
    return shape


def pocketed_catch(base_function):
    def build(y0: float, face_recess_mm: float = arm.STOP_CATCH_FACE_RECESS_MM) -> cq.Shape:
        solid = base_function(y0, face_recess_mm)
        face_y = y0 + arm.PLATE_T - face_recess_mm
        for cx in RAIL_CENTERS_X:
            cutter = rounded_prism_y(cx, POCKET_CENTER_Z, POCKET_W, POCKET_H,
                                     POCKET_R, face_y - POCKET_SCREEN_DEPTH, POCKET_SCREEN_DEPTH + 0.01)
            solid = solid.cut(cutter)
        return solid
    return build


def pad_solids(y0: float = 0.0) -> list[cq.Shape]:
    face_y = y0 + FACE_Y
    back_y = face_y - POCKET_SCREEN_DEPTH
    return [rounded_prism_y(cx, POCKET_CENTER_Z, PAD_W, PAD_H, PAD_R,
                            back_y, PAD_NOMINAL_T) for cx in RAIL_CENTERS_X]


def rewrite_current_identity() -> None:
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("P0.12", "P0.13").replace("p012-status.json", "p013-status.json")
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    original = arm.j2_positive_catch_adapter
    arm.j2_positive_catch_adapter = pocketed_catch(original)
    p012.OUT = OUT
    p012.REV = REV
    p012.STOP_REV = STOP_REV
    result = p012.main()
    if result:
        return result

    old = OUT / "p012-status.json"
    if old.exists():
        old.rename(OUT / "p013-status.json")
    rewrite_current_identity()

    pads = pad_solids()
    catch = arm.j2_positive_catch_adapter(0.0)
    pad_assembly = cq.Assembly(name="HR_V0_J2_PAD_POCKET_CANDIDATE_NOT_RELEASED")
    pad_assembly.add(catch, name="MV0-C07_POCKETED_METAL_BACKUP", color=cq.Color(0.80, 0.18, 0.12))
    for index, pad in enumerate(pads, 1):
        pad_assembly.add(pad, name=f"PAD_SR1_{index}_NOMINAL_SCREEN", color=cq.Color(0.95, 0.75, 0.10))
    installed_step = OUT / "HR-V0_J2_C07_pad-pocket-installed-screen.step"
    cq.exporters.export(cq.Compound.makeCompound([catch, *pads]), str(installed_step))
    arm.canonicalize_step(installed_step)
    pad_assembly.save(str(OUT / "HR-V0_J2_C07_pad-pocket-installed-screen.glb"))
    for index, pad in enumerate(pads, 1):
        pad_path = OUT / "parts" / f"PAD-SR1-{index}_40x12x0.61_nominal-screen.step"
        cq.exporters.export(pad, str(pad_path))
        arm.canonicalize_step(pad_path)

    nominal_protrusion = PAD_NOMINAL_T - POCKET_SCREEN_DEPTH
    pad_only_min = PAD_MIN_T - (POCKET_SCREEN_DEPTH + POCKET_DEPTH_TOL)
    pad_only_max = PAD_MAX_T - (POCKET_SCREEN_DEPTH - POCKET_DEPTH_TOL)
    angle_nominal = math.degrees(nominal_protrusion / 44.07204121151434)
    write_csv(OUT / "j2-pad-pocket-definition.csv", [{
        "feature_id":"C07-PAD-POCKET-01","quantity":"2","rail_centers_x_mm":"-44.000;+44.000",
        "center_z_mm":f"{POCKET_CENTER_Z:.3f}","coupon_width_mm":f"{PAD_W:.3f}",
        "coupon_height_mm":f"{PAD_H:.3f}","coupon_corner_radius_mm":f"{PAD_R:.3f}",
        "pocket_width_mm":f"{POCKET_W:.3f}","pocket_height_mm":f"{POCKET_H:.3f}",
        "pocket_corner_radius_mm":f"{POCKET_R:.3f}","cad_screen_depth_mm":f"{POCKET_SCREEN_DEPTH:.3f}",
        "depth_rule":"DEPENDENT FEATURE: machine after measuring the complete received pad plus adhesive stack; d_pocket=t_stack-0.150 mm",
        "installed_protrusion_acceptance_mm":"0.100..0.200; project candidate requiring qualified acceptance",
        "metal_backup":"unchanged surrounding C07 recessed face at Y=8.525 mm local; no pad strength credit",
        "state":"UNSELECTED DIMENSIONED REVIEW CANDIDATE","warning":WARNING,
    }])
    write_csv(OUT / "j2-pad-pocket-tolerance-screen.csv", [
        {"case_id":"POCKET-TOL-01","basis":"CAD screen, pad only; adhesive excluded","pad_thickness_mm":f"{PAD_NOMINAL_T:.3f}","pocket_depth_mm":f"{POCKET_SCREEN_DEPTH:.3f}","protrusion_mm":f"{nominal_protrusion:.3f}","first_contact_advance_deg":f"{angle_nominal:.6f}","interpretation":"visualization only; not a production depth","warning":WARNING},
        {"case_id":"POCKET-TOL-02","basis":"published pad thickness minimum and screen depth maximum; adhesive excluded","pad_thickness_mm":f"{PAD_MIN_T:.3f}","pocket_depth_mm":f"{POCKET_SCREEN_DEPTH + POCKET_DEPTH_TOL:.3f}","protrusion_mm":f"{pad_only_min:.3f}","first_contact_advance_deg":f"{math.degrees(pad_only_min/44.07204121151434):.6f}","interpretation":"lower-bound geometry sensitivity only","warning":WARNING},
        {"case_id":"POCKET-TOL-03","basis":"published pad thickness maximum and screen depth minimum; adhesive excluded","pad_thickness_mm":f"{PAD_MAX_T:.3f}","pocket_depth_mm":f"{POCKET_SCREEN_DEPTH - POCKET_DEPTH_TOL:.3f}","protrusion_mm":f"{pad_only_max:.3f}","first_contact_advance_deg":f"{math.degrees(pad_only_max/44.07204121151434):.6f}","interpretation":"upper-bound pad-only geometry sensitivity; adhesive requires new stack calculation","warning":WARNING},
    ])
    write_csv(OUT / "j2-pad-pocket-inspection.csv", [
        {"inspection_id":"PAD-FAI-01","feature":"pocket plan location and size","method":"CMM or optical comparator; exact method/uncertainty SELECTION REQUIRED","acceptance":"centers X +/-44.000, Z 1.000; 12.400 x 40.400; drawing tolerances require qualified release","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"inspection_id":"PAD-FAI-02","feature":"received laminated stack thickness","method":"low-force thickness gauge at five points per coupon; force/anvil/repeats SELECTION REQUIRED","acceptance":"record each result; calculate dependent pocket depth; no nominal-only acceptance","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"inspection_id":"PAD-FAI-03","feature":"installed protrusion above metal backup","method":"calibrated depth/height metrology at four corners per coupon","acceptance":"all readings 0.100..0.200 mm after qualified approval of this candidate band","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
        {"inspection_id":"PAD-FAI-04","feature":"retention and metal-backup continuity","method":"visual/peel/cycle/contact-transfer methods SELECTION REQUIRED","acceptance":"no lift/migration; continuous surrounding metal witness after bottom-out proof; limits require qualified release","execution":"NOT EXECUTED","result":"OPEN","warning":WARNING},
    ])

    status_path = OUT / "p013-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "identifier":REV,"stop_identifier":STOP_REV,"round":"R277",
        "parent":"HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE",
        "pad_pocket_quantity":2,"pad_coupon_nominal_mm":[PAD_W, PAD_H, PAD_NOMINAL_T],
        "pocket_plan_mm":[POCKET_W, POCKET_H, POCKET_R],"cad_screen_pocket_depth_mm":POCKET_SCREEN_DEPTH,
        "production_pocket_depth":"DEPENDENT FEATURE - RECEIVED STACK MINUS 0.150 MM",
        "installed_protrusion_candidate_band_mm":[ACCEPT_PROTRUSION_MIN, ACCEPT_PROTRUSION_MAX],
        "pad_retention":"3M 467MP converter-laminated candidate; exact order/configuration and application qualification open",
        "metal_backup_unchanged":True,"pad_structural_credit":False,"selected":False,
        "physical_evidence_complete":False,"qualified_review_complete":False,"fabrication_authorized":False,
        "powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,
        "safety_credit":False,"warning":WARNING,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    changes = list(csv.DictReader((OUT / "design-change-register.csv").open(newline="", encoding="utf-8-sig")))
    changes.append({"change_id":"R277-CH-05","part_id":"MV0-C07","change":"add two rounded 12.400 x 40.400 mm pad pockets centered at X +/-44.000, Z 1.000; CAD depth 0.520 mm is screen-only and production depth is received-stack dependent","preserved_interfaces":"all P0.12 hole axes, central mounting lands, rear access wells, outer envelope and surrounding Y=8.525 mm metal backup face","state":"UNSELECTED DIMENSIONED CAD CANDIDATE; RECEIVED STACK/DFM/FAI/PROOF OPEN","warning":WARNING})
    write_csv(OUT / "design-change-register.csv", changes)

    holds = list(csv.DictReader((OUT / "open-holds.csv").open(newline="", encoding="utf-8-sig")))
    additions = [
        "Obtain converter quote for Rogers 2300327 laminated on its PET-supported face with exact 3M 467MP configuration, lot traceability and finished 40 x 12 mm coupon tolerances",
        "Measure complete received pad/adhesive stack and release the dependent pocket depth before any machining",
        "Qualified reviewer accepts the 0.100..0.200 mm installed-protrusion candidate band and its guard/stopping implications",
        "Inspect pocket plan, dependent depth, installed protrusion, retention and continuous metal-backup witness on the first article",
        "Validate pad loss, migration, bottom-out, single-rail/twin-rail contact, rebound, wear, contamination and replacement interval physically",
    ]
    for index, text in enumerate(additions, 16):
        holds.append({"hold_id":f"R277-H{index:02d}","hold":text,"state":"OPEN","closure_evidence":"controlled supplier/FAI/test evidence plus qualified acceptance","release_effect":"BLOCKS P0.13 SELECTION/FABRICATION/MOTION","warning":WARNING})
    write_csv(OUT / "open-holds.csv", holds)
    acceptance = list(csv.DictReader((OUT / "acceptance-matrix.csv").open(newline="", encoding="utf-8-sig")))
    for index, text in enumerate(additions, 16):
        acceptance.append({"acceptance_id":f"R277-ACC-{index:02d}","criterion":text,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(OUT / "acceptance-matrix.csv", acceptance)

    summary_path = OUT / "architecture-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["revision"] = REV
    summary["disposition"] = "unselected P0.13 pad-pocket stop candidate; production depth is received-stack dependent and all DFM, FAI, dynamic, joined-load, physical and qualified closure remains open"
    summary["pad_pocket_stop_candidate"] = status
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {REV}; pad pockets dimensioned, production depth/retention/physical proof remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
