#!/usr/bin/env python3
"""Generate the R272 P0.11 full-height side-web J2-stop candidate.

This candidate preserves the P0.10 contact planes and all six C06/C07 hole
axes.  It changes the rear material envelope and is not selected or released.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_arm_architecture_p010 as p010


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.11-side-web-stop"
REV = "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE"
STOP_REV = "HR-V0-J2-STOP-P0.4"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
STOCK_T = 25.4
MIN_STRUCTURAL_T = 23.0
BACK_EXTENSION = STOCK_T - arm.PLATE_T
STRIKER_INNER = 35.0
STRIKER_OUTER = 53.0
CATCH_INNER = 34.0
CATCH_OUTER = 54.0
C06_WEB_INNER = 20.0
C07_WEB_INNER = 14.0
WEB_TOP = 20.0
STEP_BLEND_R = 2.0
STRIKER_TOP_Z = 36.026374


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def side_web_boss(y0: float, *, outer: float, inner: float, top: float) -> cq.Shape:
    """C06 contact-side and C07 rear-side webs preserving contact planes."""
    shapes: list[cq.Shape] = []
    web_top = min(WEB_TOP, top - 5.0)
    web_inner = C06_WEB_INNER if top > 30.0 else C07_WEB_INNER
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
        if top > 30.0:
            web = arm._profile_plate(points, y0 + arm.PLATE_T, BACK_EXTENSION)
            web = cq.Workplane(obj=web).faces("<Y").edges().fillet(STEP_BLEND_R).val()
        else:
            web = arm._profile_plate(points, y0 - BACK_EXTENSION, BACK_EXTENSION)
            web = cq.Workplane(obj=web).faces(">Y").edges().fillet(STEP_BLEND_R).val()
            for x in (-16.0, 16.0):
                for z in (-8.0, 8.0):
                    web = web.cut(cq.Solid.makeCylinder(1.35, BACK_EXTENSION, cq.Vector(x, y0 - BACK_EXTENSION, z), cq.Vector(0, 1, 0)))
        shapes.append(web)
    return cq.Compound.makeCompound(shapes)


def rewrite_generated_text() -> None:
    replacements = {
        "P0.10": "P0.11",
        "p010-status.json": "p011-status.json",
        "R270": "R272",
        "integral-boss": "mixed-side side-web",
        "integral rear bosses": "mixed-side side webs",
        "integral rear boss": "mixed-side side web",
    }
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    p010.OUT = OUT
    p010.REV = REV
    p010.STOP_REV = STOP_REV
    p010.STRIKER_INNER = STRIKER_INNER
    p010.STRIKER_OUTER = STRIKER_OUTER
    p010.CATCH_INNER = CATCH_INNER
    p010.CATCH_OUTER = CATCH_OUTER
    arm.STOP_STRIKER_TOP_Z_MM = STRIKER_TOP_Z
    p010.STOCK_T = STOCK_T
    p010.MIN_STRUCTURAL_T = MIN_STRUCTURAL_T
    p010.BACK_EXTENSION = BACK_EXTENSION
    p010.boss_profile = side_web_boss
    result = p010.main()
    if result:
        return result

    old_status = OUT / "p010-status.json"
    if old_status.exists():
        old_status.rename(OUT / "p011-status.json")
    rewrite_generated_text()

    interfaces = list(csv.DictReader((OUT / "interface-schedule.csv").open(newline="", encoding="utf-8")))
    for row in interfaces:
        if row["interface"] == "A04":
            row["pattern"] = "4 x diameter 2.70 through the full 25.4 mm C07 side-web section at X=+/-16 Z=+/-8; same axes as S102"
            row["fasteners"] = "M2.5 fastener length, grip, washers/nut, torque, locking and reuse SELECTION REQUIRED"
            row["status"] = "axis_registered_only; extended stack, access, preload, bearing and proof open"
    write_csv(OUT / "interface-schedule.csv", interfaces)

    changes = [
        {
            "change_id": "R272-CH-01",
            "part_id": "MV0-C06",
            "change": "18 mm striker rails with contact-side webs beginning at |X|=20 mm from 25.4 mm nominal stock; actuator-side envelope retained",
            "preserved_interfaces": "four M2.5 axes, two M5 axes and central 9.525 mm mounting stack; striker top is retuned to preserve 118 degree contact",
            "state": "UNSELECTED CAD CANDIDATE",
            "warning": WARNING,
        },
        {
            "change_id": "R272-CH-02",
            "part_id": "MV0-C07",
            "change": "20 mm catch rails with rear-side webs beginning at |X|=14 mm; four M2.5 axes extend through the full 25.4 mm section; existing 1 mm contact recess retained",
            "preserved_interfaces": "four M2.5 axes, two M5 axes, central 9.525 mm mounting stack and recessed +Y contact face",
            "state": "UNSELECTED CAD CANDIDATE",
            "warning": WARNING,
        },
        {
            "change_id": "R272-CH-03",
            "part_id": "C06/C07 rear envelope",
            "change": "C06 added depth is entirely +Y/contact-side; C07 added depth is entirely -Y/rear-side and carries through the four-bolt pattern; modeled R2 step blends",
            "preserved_interfaces": "nominal joint/link coordinate chain and stop-contact planes",
            "state": "CLEARANCE, DFM AND PHYSICAL FIT REVIEW REQUIRED",
            "warning": WARNING,
        },
    ]
    write_csv(OUT / "design-change-register.csv", changes)

    status_path = OUT / "p011-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update(
        {
            "identifier": REV,
            "stop_identifier": STOP_REV,
            "round": "R272",
            "parent": "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE",
            "nominal_stock_thickness_mm": STOCK_T,
            "minimum_structural_thickness_screen_mm": MIN_STRUCTURAL_T,
            "c06_side_web_inner_x_mm": C06_WEB_INNER,
            "c07_side_web_inner_x_mm": C07_WEB_INNER,
            "c06_added_depth_direction": "+Y contact/forearm side",
            "c07_added_depth_direction": "-Y rear side",
            "c06_rear_side_web_z_range_mm": [-20.0, WEB_TOP],
            "c07_rear_side_web_z_range_mm": [-20.0, arm.STOP_CATCH_TOP_Z_MM - 5.0],
            "modeled_front_step_blend_radius_mm": STEP_BLEND_R,
            "contact_face_area_changed": True,
            "c07_m2p5_hole_depth_changed": True,
            "c07_m2p5_fastener_stack": "SELECTION REQUIRED",
            "striker_top_z_mm": STRIKER_TOP_Z,
            "striker_top_z_changed_from_p010": True,
            "striker_rail_width_mm": STRIKER_OUTER - STRIKER_INNER,
            "catch_rail_width_mm": CATCH_OUTER - CATCH_INNER,
            "contact_face_and_hole_axes_changed": False,
            "contact_plane_and_hole_axis_coordinates_changed": False,
            "interface_change_note": "Contact planes and hole-axis coordinates are retained; contact-face area and C07 M2.5 hole depth/fastener stack are changed.",
            "selected": False,
            "physical_evidence_complete": False,
            "qualified_review_complete": False,
            "fabrication_authorized": False,
            "powered_testing_authorized": False,
            "motion_authorized": False,
            "energization_authorized": False,
            "safety_credit": False,
            "warning": WARNING,
        }
    )
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    analysis_path = OUT / "j2-positive-stop-analysis.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    analysis["architecture"] = (
        "Twin 18 mm C06 moving rails against 20 mm C07 catches; C06 uses a +Y contact-side web, "
        "C07 uses a -Y rear web carried through the four M2.5 axes, and the C06 striker top is "
        "retuned to 36.026374 mm for nominal 118 degree contact."
    )
    analysis["configuration_state"] = "UNSELECTED P0.11 CAD CANDIDATE"
    analysis["selection_note"] = "No selection, fabrication, safety, motion, or energization credit."
    analysis_path.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")

    summary_path = OUT / "architecture-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["revision"] = REV
    summary["disposition"] = "unselected mixed-side side-web stop candidate; exact C06/C07 structural, collision, DFM, physical and qualified closure remain open"
    summary["side_web_stop_candidate"] = status
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    holds = list(csv.DictReader((OUT / "open-holds.csv").open(newline="", encoding="utf-8")))
    for row in holds:
        row["release_effect"] = "BLOCKS P0.11 SELECTION/FABRICATION/MOTION"
        row["warning"] = WARNING
    write_csv(OUT / "open-holds.csv", holds)
    print(f"Generated {REV}; mixed-side side-web candidate remains unselected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
