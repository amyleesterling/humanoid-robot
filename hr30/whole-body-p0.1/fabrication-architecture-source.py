"""Generate HR-30 P0.1 modular frame, cover, service, and harness architecture.

The output is dimensioned candidate geometry.  It is deliberately not a drawing
release: material allowables, tolerances, fasteners, tooling, loads, fit, and
physical validation remain open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_detailed_grippers_p01 as grippers


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-FABRICATION-ARCH-P0.1"
WARNING = body.WARNING


@dataclass(frozen=True)
class Part:
    name: str
    module: str
    role: str
    shape: cq.Shape
    material_candidate: str
    density_kg_m3: float
    process_candidate: str
    color: tuple[float, float, float, float]
    service_state: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def beam_between(a: tuple[float, float, float], b: tuple[float, float, float], width: float, depth: float) -> cq.Shape:
    av, bv = cq.Vector(*a), cq.Vector(*b)
    delta = bv - av
    center = av + delta.multiply(0.5)
    return cq.Workplane(body.local_plane((center.x, center.y, center.z), (delta.x, delta.y, delta.z))).box(width, depth, delta.Length).val()


def hollow_tapered(z0: float, z1: float, lower_w: float, lower_d: float, upper_w: float, upper_d: float, wall: float) -> cq.Shape:
    outer = body.tapered_body(z0, z1, lower_w, lower_d, upper_w, upper_d)
    inner = body.tapered_body(z0 - 1.0, z1 + 1.0, lower_w - 2 * wall, lower_d - 2 * wall, upper_w - 2 * wall, upper_d - 2 * wall)
    return outer.cut(inner)


def hollow_rail(width: float, depth: float, height: float, center, wall: float, radius: float = 2.0) -> cq.Shape:
    outer = body.rounded_box(width, depth, height, center, radius)
    inner = body.rounded_box(width - 2 * wall, depth - 2 * wall, height + 2.0, center, max(0.5, radius - wall * 0.5))
    return outer.cut(inner)


def windowed_xz_plate(width: float, depth: float, height: float, center, rail: float, end: float, radius: float = 1.5) -> cq.Shape:
    outer = body.rounded_box(width, depth, height, center, radius)
    window = body.rounded_box(width - 2 * rail, depth + 2.0, height - 2 * end, center, max(1.0, radius))
    return outer.cut(window)


def windowed_xy_plate(width: float, depth: float, height: float, center, rail: float, radius: float = 2.0) -> cq.Shape:
    edge_radius = min(radius, max(0.5, height / 2.0 - 0.2))
    outer = body.rounded_box(width, depth, height, center, edge_radius)
    window = body.rounded_box(width - 2 * rail, depth - 2 * rail, height + 2.0, center, max(0.5, edge_radius))
    return outer.cut(window)


def slotted_beam(a, b, width: float, depth: float, rail: float, end: float) -> cq.Shape:
    outer = beam_between(a, b, width, depth)
    av, bv = cq.Vector(*a), cq.Vector(*b)
    direction = (bv - av).normalized()
    inner_a = av + direction.multiply(end)
    inner_b = bv - direction.multiply(end)
    inner = beam_between(tuple(inner_a.toTuple()), tuple(inner_b.toTuple()), width - 2 * rail, depth + 2.0)
    return outer.cut(inner)


def half(shape: cq.Shape, front: bool) -> cq.Shape:
    clip = body.rounded_box(500, 250, 900, (0, -125 if front else 125, 400), 0)
    return shape.intersect(clip)


def volume_mass_kg(shape: cq.Shape, density: float) -> float:
    return shape.Volume() * 1e-9 * density


def build() -> tuple[list[Part], list[dict], list[dict]]:
    aluminum = (0.08, 0.20, 0.38, 1.0)
    cover_blue = (0.25, 0.68, 0.92, 0.78)
    cover_dark = (0.10, 0.34, 0.62, 0.82)
    sole_gold = (0.96, 0.70, 0.08, 1.0)
    route_power = (0.96, 0.55, 0.08, 0.52)
    route_data = (0.15, 0.85, 0.95, 0.52)
    parts: list[Part] = []
    routes: list[dict] = []
    panels: list[dict] = []
    closed_gripper_parts = grippers.build_hand_parts(0.0)

    def add(name: str, module: str, role: str, shape: cq.Shape, material: str, density: float, process: str, color, service: str) -> None:
        if shape.isNull() or not shape.isValid() or shape.Volume() <= 1e-6:
            raise RuntimeError(f"invalid fabrication part {name}")
        parts.append(Part(name, module, role, shape, material, density, process, color, service))

    def add_panel(name: str, module: str, shape: cq.Shape, access: str, seam: str, retention: str, color=cover_blue, wall: float = 1.5) -> None:
        add(name, module, "removable cover", shape, "PETG/PA-CF PRINT COUPON SELECTION REQUIRED", 1200.0, "FDM/SLS candidate; orientation and process qualification required", color, "TOOL-REMOVABLE CANDIDATE")
        panels.append({
            "panel_id": name, "module": module, "nominal_wall_mm": f"{wall:.1f}", "access_role": access,
            "seam_datum": seam, "retention_candidate": retention,
            "edge_rule": ">=3 mm external radius where geometry permits; pinch/access review required",
            "release_state": "GEOMETRIC CANDIDATE - FASTENER, INSERT, GAP, TOLERANCE AND PROCESS SELECTION REQUIRED",
        })

    # Central load path: two torso rails, shoulder tube, pelvis front/rear
    # plates, waist bridge, hollow neck tube, and a visible restraint bridge.
    for x in (-66.0, 66.0):
        add(f"T01_TORSO_RAIL_{'L' if x > 0 else 'R'}", "T01", "primary frame rail", hollow_rail(18, 18, 146, (x, 6, 507), 2.0), "6061-T6/T651 HOLLOW EXTRUSION CANDIDATE", 2700, "cut/drill fixture; exact section and temper selection required", aluminum, "FIXED FRAME")
    shoulder_outer = body.rounded_box(174, 28, 24, (0, 0, 578), 3)
    shoulder_inner = body.rounded_box(164, 20, 16, (0, 0, 578), 2)
    add("T01_SHOULDER_CROSS_TUBE", "T01", "shoulder load bridge", shoulder_outer.cut(shoulder_inner), "6061-T6/T651 MACHINED OR EXTRUDED CANDIDATE", 2700, "3-axis machining/extrusion finish; joint load proof required", aluminum, "FIXED FRAME")
    for y, suffix in ((-31.0, "FRONT"), (31.0, "REAR")):
        add(f"P01_PELVIS_PLATE_{suffix}", "P01", "pelvis frame plate", windowed_xz_plate(136, 5, 62, (0, y, 386), 14, 14, 2), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate; MTR/tolerance/fixture review required", aluminum, "FIXED FRAME")
    add("P01_WAIST_BRIDGE", "P01", "waist load bridge", windowed_xy_plate(112, 62, 8, (0, 0, 414), 16, 3), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")
    neck_outer = body.rounded_box(38, 38, 58, (0, 0, 625), 4)
    neck_inner = body.rounded_box(31, 31, 60, (0, 0, 625), 3)
    add("N01_NECK_TUBE", "N01", "neck frame tube", neck_outer.cut(neck_inner), "6061-T6/T651 TUBE OR MACHINED CANDIDATE", 2700, "tube/machined candidate; buckling and joint proof required", aluminum, "FIXED FRAME")
    add("P01_RESTRAINT_BRIDGE", "P01", "fall-restraint load-path candidate", body.rounded_box(84, 14, 12, (0, 31, 410), 2), "6061-T651 PLATE CANDIDATE", 2700, "CNC candidate; no restraint rating or load credit", sole_gold, "FIXED FRAME - NO FALL LOAD CREDIT")

    # Paired limb plates and cross ties define actual modular load paths.  They
    # are not credited until joined-hardware and gait/impact proof exists.
    for side, sign in (("L", 1.0), ("R", -1.0)):
        x = sign * body.HIP_HALF_WIDTH
        for y, suffix in ((-20.0, "FRONT"), (20.0, "REAR")):
            add(f"L0{1 if side == 'L' else 2}_SHIN_SIDE_{suffix}", f"L0{1 if side == 'L' else 2}", "shin side plate", windowed_xz_plate(50, 4, 136, (x, y, 127.5), 11, 18), "6061-T651 4 MM WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC/waterjet candidate; edge finish and flatness open", aluminum, "FIXED FRAME")
            add(f"L0{1 if side == 'L' else 2}_THIGH_SIDE_{suffix}", f"L0{1 if side == 'L' else 2}", "thigh side plate", windowed_xz_plate(56, 4, 142, (x, y, 295), 12, 18), "6061-T651 4 MM WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC/waterjet candidate; edge finish and flatness open", aluminum, "FIXED FRAME")
        for z in (72.0, 135.0, 183.0):
            add(f"L0{1 if side == 'L' else 2}_SHIN_TIE_Z{int(z)}", f"L0{1 if side == 'L' else 2}", "shin cross tie", windowed_xy_plate(42, 40, 4, (x, 0, z), 8), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")
        for z in (235.0, 300.0, 355.0):
            add(f"L0{1 if side == 'L' else 2}_THIGH_TIE_Z{int(z)}", f"L0{1 if side == 'L' else 2}", "thigh cross tie", windowed_xy_plate(46, 40, 4, (x, 0, z), 8), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")
        foot_module = f"F0{1 if side == 'L' else 2}"
        add(f"{foot_module}_SOLE_CARRIER", foot_module, "foot sole carrier", windowed_xy_plate(86, 138, 5, (x, 25, 4.5), 14), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate; sole interface open", aluminum, "FIXED FRAME")
        add(f"{foot_module}_TOP_BRIDGE", foot_module, "foot top bridge", windowed_xy_plate(68, 86, 4, (x, 6, 31), 12), "6061-T651 WINDOWED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")

        shoulder = (sign * body.SHOULDER_AXIS_X, 0.0, body.SHOULDER_Z)
        elbow = (sign * body.ELBOW_X, 0.0, body.ELBOW_Z)
        wrist = (sign * body.WRIST_X, 0.0, body.WRIST_Z)
        arm_module = f"A0{1 if side == 'L' else 2}"
        for y, suffix in ((-14.0, "FRONT"), (14.0, "REAR")):
            add(f"{arm_module}_UPPER_ARM_LINK_{suffix}", arm_module, "upper-arm link plate", slotted_beam((shoulder[0], y, shoulder[2]), (elbow[0], y, elbow[2]), 28, 4, 7, 18), "6061-T651 4 MM SLOTTED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")
            add(f"{arm_module}_FOREARM_LINK_{suffix}", arm_module, "forearm link plate", slotted_beam((elbow[0], y, elbow[2]), (wrist[0], y, wrist[2]), 26, 4, 7, 18), "6061-T651 4 MM SLOTTED PLATE CANDIDATE", 2700, "2.5D CNC candidate", aluminum, "FIXED FRAME")

        # Flat tool-removable limb panels around the paired frames.
        leg_module = f"L0{1 if side == 'L' else 2}"
        add_panel(f"{leg_module}_SHIN_FRONT_COVER", leg_module, body.rounded_box(60, 1.5, 132, (x, -34, 127.5), 0.7), "shin harness and cross-tie access", "Y=-33.25 mm", "M3-class captive insert pattern candidate; exact system selection required")
        add_panel(f"{leg_module}_SHIN_REAR_COVER", leg_module, body.rounded_box(60, 1.5, 132, (x, 34, 127.5), 0.7), "shin harness and cross-tie access", "Y=+33.25 mm", "M3-class captive insert pattern candidate; exact system selection required", cover_dark)
        add_panel(f"{leg_module}_THIGH_FRONT_COVER", leg_module, body.rounded_box(66, 1.5, 138, (x, -37, 295), 0.7), "thigh transmission and harness access", "Y=-36.25 mm", "M3-class captive insert pattern candidate; exact system selection required")
        add_panel(f"{leg_module}_THIGH_REAR_COVER", leg_module, body.rounded_box(66, 1.5, 138, (x, 37, 295), 0.7), "thigh transmission and harness access", "Y=+36.25 mm", "M3-class captive insert pattern candidate; exact system selection required", cover_dark)
        add_panel(f"{foot_module}_TOP_COVER", foot_module, body.rounded_box(82, 118, 1.5, (x, 25, 34.0), 0.7), "ankle and foot-sensor access", "Z=33.25 mm", "four tool-fastened corners candidate; exact inserts open", cover_blue)
        for segment, p0, p1, width in (("UPPER_ARM", shoulder, elbow, 46), ("FOREARM", elbow, wrist, 44)):
            for y, suffix, color in ((-24.0, "FRONT", cover_blue), (24.0, "REAR", cover_dark)):
                add_panel(f"{arm_module}_{segment}_{suffix}_COVER", arm_module, beam_between((p0[0], y, p0[2]), (p1[0], y, p1[2]), width, 1.5), f"{segment.lower().replace('_', ' ')} harness/link access", f"local Y={'-' if y < 0 else '+'} cover plane", "M3-class captive insert pattern candidate; exact system selection required", color)
        # Make the detailed gripper part of the authoritative fabrication
        # spine.  It replaces the former one-piece palm rear-cover envelope.
        # The product actuator is carried separately by the official-product
        # mass/equipment records, so only the seventeen custom parts are added.
        hand_module = f"G0{1 if side == 'L' else 2}"
        for hand_part in closed_gripper_parts:
            if not hand_part.fabrication_candidate:
                continue
            if hand_part.name.startswith("PALM_") or hand_part.name == "WRIST_MOUNT_PLATE":
                process = "2.5D CNC or qualified polymer process candidate; exact route and inserts open"
            elif hand_part.name.startswith("GUIDE_ROD"):
                process = "precision cut/finish from 4 mm rod; straightness and end retention open"
            elif hand_part.name.startswith("RACK_") or hand_part.name == "PINION":
                process = "precision gear machining or qualified molded candidate; tooth inspection and wear proof open"
            elif hand_part.name.startswith("FINGER_") or hand_part.name.startswith("STOP_"):
                process = "SLS/FDM or 3-axis machining candidate; orientation, clearance and proof open"
            elif hand_part.name.startswith("PAD_"):
                process = "die-cut or molded compliant insert candidate; force-stroke and retention open"
            else:
                process = "3-axis machining candidate; fit, access and retention open"
            add(
                f"{hand_module}_{hand_part.name}", hand_module, hand_part.kind,
                grippers.translate(hand_part.shape, side), hand_part.material,
                hand_part.density_kg_m3, process, hand_part.color,
                "SERVICEABLE GRIPPER MECHANISM CANDIDATE",
            )

    # Hollow central shells split into separately removable front and rear parts.
    torso_shell = hollow_tapered(430, 585, 152, 94, 190, 110, 1.6)
    pelvis_shell = hollow_tapered(352, 417, 142, 96, 155, 105, 1.6)
    add_panel("T01_TORSO_FRONT_COVER", "T01", half(torso_shell, True), "compute, cooling, bus and shoulder-frame access", "Y=0 split plane", "eight M3-class captive points candidate; exact count/load/insert selection required", wall=1.6)
    add_panel("T01_TORSO_REAR_COVER", "T01", half(torso_shell, False), "compute cooling and harness-spine access", "Y=0 split plane", "eight M3-class captive points candidate; exact count/load/insert selection required", cover_dark, wall=1.6)
    add_panel("P01_PELVIS_FRONT_COVER", "P01", half(pelvis_shell, True), "power-bay service access", "Y=0 split plane", "six M3-class captive points candidate; exact selection required", wall=1.6)
    add_panel("P01_PELVIS_REAR_COVER", "P01", half(pelvis_shell, False), "restraint, power-disconnect and harness access", "Y=0 split plane", "six M3-class captive points candidate; exact selection required", cover_dark, wall=1.6)
    head_outer = body.rounded_box(150, 110, 112, (0, 0, 706), 12)
    head_inner = body.rounded_box(146.8, 106.8, 116, (0, 0, 706), 10.4)
    head_shell = head_outer.cut(head_inner)
    face_opening = body.rounded_box(120, 28, 62, (0, -54, 704), 4)
    add_panel("H01_HEAD_FRONT_BEZEL", "H01", half(head_shell, True).cut(face_opening), "screen, camera, privacy indicator and microphone access", "Y=0 split plane; controlled screen opening", "six small captive fasteners candidate; exact selection required", wall=1.6)
    add_panel("H01_HEAD_REAR_COVER", "H01", half(head_shell, False), "speaker, camera and cooling access", "Y=0 split plane", "six small captive fasteners candidate; exact selection required", cover_dark, wall=1.6)

    # Segregated power/data routing references.  Corridors are not physical
    # cable geometry and receive no fill, bend, EMC, fire, or current credit.
    def add_route(route_id: str, module: str, service: str, a, b, diameter: float, bend_radius: float, separation: str, color) -> None:
        av, bv = cq.Vector(*a), cq.Vector(*b)
        delta = bv - av
        midpoint = av + delta.multiply(0.5)
        shape = body.cylinder_between((midpoint.x, midpoint.y, midpoint.z), tuple(delta.toTuple()), delta.Length, diameter)
        add(route_id, module, "harness corridor reference", shape, "REFERENCE VOLUME - NOT MATERIAL", 0.001, "route reservation only", color, "REFERENCE ONLY")
        routes.append({
            "route_id": route_id, "module": module, "service_class": service,
            "start_xyz_mm": f"({a[0]:.1f},{a[1]:.1f},{a[2]:.1f})", "end_xyz_mm": f"({b[0]:.1f},{b[1]:.1f},{b[2]:.1f})",
            "corridor_diameter_mm": f"{diameter:.1f}", "minimum_dynamic_bend_radius_mm": f"{bend_radius:.1f}",
            "separation_rule": separation, "connector_boundary": "SELECTION REQUIRED",
            "validation_state": "ROUTE RESERVED - CABLE OD/FILL/FLEX/STRAIN-RELIEF/EMC/CURRENT/THERMAL TEST OPEN",
        })

    add_route("HN01_TORSO_POWER_SPINE", "HN01", "ACTUATOR POWER", (18, 18, 405), (18, 18, 575), 14, 70, "opposite torso rail from data; crossing only at 90 degrees", route_power)
    add_route("HN01_TORSO_DATA_SPINE", "HN01", "DATA/LOW VOLTAGE", (-18, -18, 405), (-18, -18, 575), 10, 50, "opposite torso rail from actuator power", route_data)
    add_route("HN01_HEAD_BRANCH", "HN01", "DATA/LOW VOLTAGE", (-18, -18, 575), (0, -12, 700), 10, 50, "no shared conduit with actuator power", route_data)
    add_route("HN01_HEAD_POWER_BRANCH", "HN01", "ACTUATOR POWER", (18, 18, 575), (0, 12, 700), 8, 40, "opposite side of neck from head data branch; moving pan/tilt service loops required", route_power)
    for side, sign in (("L", 1.0), ("R", -1.0)):
        leg = f"L0{1 if side == 'L' else 2}"
        arm = f"A0{1 if side == 'L' else 2}"
        x = sign * body.HIP_HALF_WIDTH
        add_route(f"HN01_{side}_LEG_POWER", leg, "ACTUATOR POWER", (x + sign * 12, 15, 397), (x + sign * 12, 15, 45), 12, 60, "front/rear offset from data corridor; joint service loops required", route_power)
        add_route(f"HN01_{side}_LEG_DATA", leg, "DATA/ENCODER", (x - sign * 12, -15, 397), (x - sign * 12, -15, 45), 9, 45, "front/rear offset from power corridor; shield/return topology open", route_data)
        add_route(f"HN01_{side}_ARM_POWER", arm, "ACTUATOR POWER", (sign * 92, 15, 575), (sign * body.WRIST_X, 15, body.WRIST_Z), 10, 50, "rearward offset from data; shoulder/elbow loops required", route_power)
        add_route(f"HN01_{side}_ARM_DATA", arm, "DATA/ENCODER", (sign * 100, -15, 575), (sign * body.WRIST_X, -15, body.WRIST_Z), 8, 40, "forward offset from power; shield/return topology open", route_data)

    return parts, panels, routes


def update_bom_and_docs(frame_mass: float, cover_mass: float) -> None:
    bom_path = OUT / "whole-robot-candidate-bom.csv"
    rows = list(csv.DictReader(bom_path.open(encoding="utf-8")))
    for row in rows:
        if row["item_id"] == "HR30-BOM-021":
            row["candidate"] = f"P0.1 windowed 4 mm limb plates, hollow torso rails/cross-tube, windowed pelvis plates and foot carriers; CAD density screen {frame_mass:.3f} kg; drawings/material release open"
        elif row["item_id"] == "HR30-BOM-022":
            row["candidate"] = f"P0.1 1.5 mm limb/palm/foot panels and 1.6 mm torso/pelvis/head shells; CAD density screen {cover_mass:.3f} kg; material/process/rib/retention open"
        elif row["item_id"] == "HR30-BOM-030":
            row["candidate"] = "12 segregated power/data route corridors with controlled diameters and bend-radius requirements; cables/connectors/fill/EMC/current selection open"
    write_csv(bom_path, rows)

    readme_path = OUT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    heading = "## Modular fabrication architecture"
    section = f"""{heading}

P0.1 now includes an editable CAD assembly that converts the visual body envelopes into a candidate central frame, paired windowed limb plates, foot carriers, hollow split torso/pelvis/head shells, removable body panels, both seventeen-part custom gripper mechanisms, and twelve segregated harness corridors. Separate neck data and actuator-power branches prevent the head actuators from borrowing the data-only corridor. The current mass candidate uses 1.5 mm limb/foot panels and 1.6 mm torso/pelvis/head shells; ribs, print/process qualification and impact stiffness remain open. The CAD density screen is {frame_mass:.3f} kg for fixed/mechanism parts and {cover_mass:.3f} kg for removable covers. These numbers feed the downstream mass reconciliation but remain geometry/material-assumption screens; neither they nor the historical 9.63 kg allocation establish whole-robot mass closure. No drawing, tolerance, material, fastener, harness, structural, DFM, or work release follows.
"""
    if heading in text:
        prefix, remainder = text.split(heading, 1)
        next_heading = remainder.find("\n## ")
        suffix = remainder[next_heading:] if next_heading >= 0 else ""
        text = prefix.rstrip() + "\n\n" + section.rstrip() + suffix
    else:
        text = text.rstrip() + "\n\n" + section.rstrip() + "\n"
    readme_path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")

    plan_path = OUT / "modular-fabrication-assembly-electrification-plan.md"
    plan = plan_path.read_text(encoding="utf-8")
    plan = plan.replace(
        "Each has a released interface-control drawing, mass ceiling, connector boundary, datum set and revision before fabrication.",
        "P0.1 now gives each a geometric module boundary and datum path. Released interface-control drawings, mass ceilings, connector boundaries, tolerances and revisions remain required before fabrication.",
    )
    plan_path.write_text(plan, encoding="utf-8", newline="\n")

    holds_path = OUT / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H06":
            row["unresolved_item"] = "The fabrication assembly now defines lightweight hollow 1.5 mm limb/palm/foot panels and 1.6 mm torso/pelvis/head shells, but material/process, rib/stiffness, retention, vents, access clearance, tolerance and pinch-edge proof remain open."
        elif row["hold_id"] == "HR30-P01-H07":
            row["unresolved_item"] = "Eleven segregated power/data corridors now have diameters and bend-radius requirements, but exact cables, fill, flex life, service loops, connectors, strain relief, shielding, current, EMC and thermal evidence remain open."
    write_csv(holds_path, holds)

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "modular_fabrication_architecture_present": True,
        "frame_part_geometry_present": True,
        "hollow_split_service_cover_geometry_present": True,
        "segregated_harness_route_geometry_present": True,
        "fabrication_part_count": None,
        "service_panel_count": None,
        "harness_route_count": None,
        "fabrication_drawings_released": False,
        "harness_selected_or_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def generate_into_package() -> dict:
    if not (OUT / "whole-robot-candidate-bom.csv").exists():
        raise RuntimeError("run whole-body system generator before fabrication generator")
    parts, panels, routes = build()
    physical_parts = [part for part in parts if part.density_kg_m3 > 1.0]
    reference_parts = [part for part in parts if part.density_kg_m3 <= 1.0]
    physical_compound = cq.Compound.makeCompound([part.shape for part in physical_parts])
    reference_compound = cq.Compound.makeCompound([part.shape for part in parts])
    step_path = OUT / "HR-30_modular_fabrication_candidate.step"
    cq.exporters.export(physical_compound, str(step_path))
    body.canonicalize_step(step_path)
    reference_step = OUT / "HR-30_modular_fabrication_reference.step"
    cq.exporters.export(reference_compound, str(reference_step))
    body.canonicalize_step(reference_step)
    assembly = cq.Assembly(name="HR30_MODULAR_FABRICATION_P01_NOT_RELEASED")
    for part in parts:
        assembly.add(part.shape, name=part.name, color=cq.Color(*part.color))
    # Keep the fabrication view recognizable as the same complete humanoid by
    # adding the controlled joint-module, face-screen, and functional-hand
    # geometry as visual context.  These reference solids are not duplicated
    # into the fabrication STEP or mass calculation.
    body_components, _axes, _bindings, _transforms = body.build()
    for item in body_components:
        if not (
            item.name.startswith("JMOD_")
            or item.group == "joint housing"
            or item.name.startswith("FACE_")
            or "HAND_PALM" in item.name
            or "GRIPPER_FINGER" in item.name
            or "SOFT_PAD_LAND" in item.name
        ):
            continue
        visual = item.visual_shape if item.visual_shape is not None else item.shape
        assembly.add(visual, name=f"CONTEXT_{item.name}", color=cq.Color(*item.color))
    assembly.save(str(OUT / "HR-30_modular_fabrication_reference.glb"))

    part_rows = []
    for part in parts:
        box = part.shape.BoundingBox()
        part_rows.append({
            "part_id": part.name, "module": part.module, "role": part.role,
            "material_candidate": part.material_candidate, "process_candidate": part.process_candidate,
            "cad_volume_mm3": f"{part.shape.Volume():.3f}", "density_screen_kg_m3": f"{part.density_kg_m3:.1f}",
            "cad_mass_screen_kg": f"{volume_mass_kg(part.shape, part.density_kg_m3):.6f}",
            "bbox_mm": f"{box.xlen:.3f} x {box.ylen:.3f} x {box.zlen:.3f}",
            "service_state": part.service_state,
            "release_state": "DIMENSIONED CANDIDATE - DRAWING/GD&T/MATERIAL/FASTENER/LOAD/DFM/FAI RELEASE OPEN",
        })
    write_csv(OUT / "fabrication-part-register.csv", part_rows)
    write_csv(OUT / "service-panel-interface-register.csv", panels)
    write_csv(OUT / "harness-route-register.csv", routes)
    frame_mass = sum(volume_mass_kg(part.shape, part.density_kg_m3) for part in physical_parts if part.role != "removable cover")
    cover_mass = sum(volume_mass_kg(part.shape, part.density_kg_m3) for part in physical_parts if part.role == "removable cover")
    update_bom_and_docs(frame_mass, cover_mass)

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"fabrication_part_count": len(physical_parts), "service_panel_count": len(panels), "harness_route_count": len(routes)})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "physical_fabrication_part_count": len(physical_parts), "reference_route_solid_count": len(reference_parts),
        "service_panel_count": len(panels), "harness_route_count": len(routes),
        "frame_mass_screen_kg": round(frame_mass, 6), "cover_mass_screen_kg": round(cover_mass, 6),
        "all_geometry_valid": all(part.shape.isValid() for part in parts),
        "frame_geometry_present": True, "hollow_split_shell_geometry_present": True,
        "service_access_geometry_present": True, "segregated_harness_corridors_present": True,
        "drawings_released": False, "materials_selected": False, "fasteners_selected": False,
        "harness_selected": False, "structural_capacity_validated": False, "fabrication_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "fabrication-architecture-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "fabrication-architecture-source.py")
    return status


def main() -> int:
    status = generate_into_package()
    manifest_path = OUT / "file-manifest.csv"
    if manifest_path.exists():
        manifest_path.unlink()
    files = [path for path in OUT.rglob("*") if path.is_file()]
    write_csv(manifest_path, [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in sorted(files)])
    release = ROOT / "release" / "hr30" / "whole-body-p0.1"
    if release.exists():
        shutil.rmtree(release)
    shutil.copytree(OUT, release)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
