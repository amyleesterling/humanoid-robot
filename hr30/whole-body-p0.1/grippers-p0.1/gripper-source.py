"""Generate detailed bilateral HR-30 hand-shaped parallel grippers.

This package replaces the former hand-envelope-only refinement path with an
editable mechanical candidate: palm frame, wrist interface, twin guide rods,
two sliding fingers, paired racks, a common pinion, hard stops, replaceable
compliant pads, a manual-release hub, and the SHA-bound XC330 packaging body.
It remains preliminary and grants no procurement, fabrication, powered-work,
motion, or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "grippers-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "grippers-p0.1"
IDENTIFIER = "HR30-DETAILED-BILATERAL-GRIPPERS-P0.1"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)

PALM_CENTER_Z = 270.0
HAND_CENTER_X = 140.0
FINGER_CENTER_CLOSED_MM = 13.0
FINGER_TRAVEL_EACH_MM = 13.0
FINGER_WIDTH_MM = 12.0
PAD_THICKNESS_MM = 3.0
PINION_PITCH_RADIUS_MM = 5.0
PINION_MODULE_MM = 0.5
PINION_TEETH = 20
GEAR_PRESSURE_ANGLE_DEG = 20.0
GEAR_FACE_WIDTH_MM = 6.0
GEAR_ADDENDUM_MM = PINION_MODULE_MM
GEAR_DEDENDUM_MM = 1.25 * PINION_MODULE_MM
GEAR_TOTAL_TANGENTIAL_BACKLASH_MM = 0.08
GEAR_PROFILE_SAMPLES_PER_FLANK = 12
GUIDE_ROD_DIAMETER_MM = 4.0
GUIDE_ROD_LENGTH_MM = 64.0

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


@dataclass(frozen=True)
class Part:
    name: str
    kind: str
    shape: cq.Shape
    color: tuple[float, float, float, float]
    material: str
    density_kg_m3: float
    fabrication_candidate: bool
    note: str


COLORS = {
    "frame": (0.05, 0.20, 0.38, 1.0),
    "guide": (0.70, 0.76, 0.82, 1.0),
    "finger": (0.25, 0.68, 0.90, 1.0),
    "pad": (0.96, 0.71, 0.10, 1.0),
    "rack": (0.96, 0.48, 0.08, 1.0),
    "stop": (0.12, 0.50, 0.67, 1.0),
    "actuator": (0.47, 0.82, 0.97, 0.75),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def rounded_box(x: float, y: float, z: float, center: tuple[float, float, float], radius: float) -> cq.Shape:
    result = cq.Workplane("XY").box(x, y, z)
    if radius:
        safe_radius = min(radius, x / 2.0 - 0.05, y / 2.0 - 0.05, z / 2.0 - 0.05)
        try:
            result = result.edges().fillet(safe_radius)
        except Exception:
            # Very thin rack teeth can reject all-edge fillets in OCC.  Their
            # controlling geometry remains the explicit bounding prism.
            pass
    return result.translate(center).val()


def frame_plate(y: float) -> cq.Shape:
    plate = rounded_box(50.0, 3.0, 36.0, (0.0, y, 0.0), 2.2)
    window = rounded_box(30.0, 5.0, 17.0, (0.0, y, 1.0), 3.0)
    return plate.cut(window).clean()


def wrist_mount_plate() -> cq.Shape:
    plate = rounded_box(38.0, 36.0, 3.0, (0.0, 0.0, 19.5), 3.0)
    plate = plate.cut(body.cylinder_between((0.0, 0.0, 19.5), (0, 0, 1), 5.0, 6.5))
    for x in (-13.0, 13.0):
        for y in (-14.0, 14.0):
            plate = plate.cut(body.cylinder_between((x, y, 19.5), (0, 0, 1), 5.0, 3.4))
    return plate.clean()


def guide_rod(y: float) -> cq.Shape:
    return body.cylinder_between((0.0, y, -8.0), (1, 0, 0), GUIDE_ROD_LENGTH_MM, GUIDE_ROD_DIAMETER_MM)


def involute_function(angle_rad: float) -> float:
    return math.tan(angle_rad) - angle_rad


def involute_tooth() -> cq.Shape:
    """One project-owned 20-degree involute tooth, centred on local +Z."""
    pressure_angle = math.radians(GEAR_PRESSURE_ANGLE_DEG)
    pitch_radius = PINION_PITCH_RADIUS_MM
    base_radius = pitch_radius * math.cos(pressure_angle)
    root_radius = pitch_radius - GEAR_DEDENDUM_MM
    tip_radius = pitch_radius + GEAR_ADDENDUM_MM
    pinion_pitch_thickness = math.pi * PINION_MODULE_MM / 2.0 - GEAR_TOTAL_TANGENTIAL_BACKLASH_MM / 2.0
    half_pitch_angle = pinion_pitch_thickness / (2.0 * pitch_radius)
    pitch_involute = involute_function(pressure_angle)

    flank: list[tuple[float, float]] = []
    for index in range(GEAR_PROFILE_SAMPLES_PER_FLANK):
        ratio = index / (GEAR_PROFILE_SAMPLES_PER_FLANK - 1)
        radius = base_radius + ratio * (tip_radius - base_radius)
        alpha = math.acos(base_radius / radius)
        theta = half_pitch_angle + pitch_involute - involute_function(alpha)
        flank.append((radius * math.sin(theta), radius * math.cos(theta)))

    root_theta = math.atan2(flank[0][0], flank[0][1])
    left = [(-x, z) for x, z in flank]
    right = list(reversed(flank))
    polygon = [
        (-root_radius * math.sin(root_theta), root_radius * math.cos(root_theta)),
        *left,
        *right,
        (root_radius * math.sin(root_theta), root_radius * math.cos(root_theta)),
    ]
    return cq.Workplane("XZ").polyline(polygon).close().extrude(GEAR_FACE_WIDTH_MM / 2.0, both=True).val()


def spur_pinion(travel_each_mm: float = 0.0) -> cq.Shape:
    root_radius = PINION_PITCH_RADIUS_MM - GEAR_DEDENDUM_MM
    gear = body.cylinder_between((0.0, 0.0, 0.0), (0, 1, 0), GEAR_FACE_WIDTH_MM, root_radius * 2.0)
    tooth = involute_tooth()
    for index in range(PINION_TEETH):
        gear = gear.fuse(tooth.rotate((0, 0, 0), (0, 1, 0), index * 360.0 / PINION_TEETH))
    bore = body.cylinder_between((0.0, 0.0, 0.0), (0, 1, 0), GEAR_FACE_WIDTH_MM + 2.0, 3.2)
    rotation_deg = math.degrees(travel_each_mm / PINION_PITCH_RADIUS_MM)
    return gear.cut(bore).clean().rotate((0, 0, 0), (0, 1, 0), rotation_deg)


def rack_shape(rack_center_x: float, upper: bool) -> cq.Shape:
    direction = 1.0 if upper else -1.0
    pitch = math.pi * PINION_MODULE_MM
    pitch_line_z = direction * PINION_PITCH_RADIUS_MM
    root_z = pitch_line_z + direction * GEAR_DEDENDUM_MM
    body_center_z = direction * 6.6875
    rack = rounded_box(32.0, GEAR_FACE_WIDTH_MM, 2.125, (rack_center_x, 0.0, body_center_z), 0.35)

    rack_pitch_thickness = math.pi * PINION_MODULE_MM / 2.0 - GEAR_TOTAL_TANGENTIAL_BACKLASH_MM / 2.0
    slope = math.tan(math.radians(GEAR_PRESSURE_ANGLE_DEG))
    tip_width = rack_pitch_thickness - 2.0 * GEAR_ADDENDUM_MM * slope
    root_width = rack_pitch_thickness + 2.0 * GEAR_DEDENDUM_MM * slope
    if tip_width <= 0.0:
        raise RuntimeError("rack tip width collapsed")
    tip_z = pitch_line_z - direction * GEAR_ADDENDUM_MM
    closed_center = -3.0 if upper else 3.0
    travel_offset = rack_center_x - closed_center
    phase = pitch / 2.0 + travel_offset
    lower_x, upper_x = rack_center_x - 16.0, rack_center_x + 16.0
    first_index = math.floor((lower_x - phase) / pitch) - 1
    last_index = math.ceil((upper_x - phase) / pitch) + 1
    for index in range(first_index, last_index + 1):
        center_x = phase + index * pitch
        if center_x + root_width / 2.0 < lower_x or center_x - root_width / 2.0 > upper_x:
            continue
        points = [
            (center_x - root_width / 2.0, root_z),
            (center_x - tip_width / 2.0, tip_z),
            (center_x + tip_width / 2.0, tip_z),
            (center_x + root_width / 2.0, root_z),
        ]
        tooth = cq.Workplane("XZ").polyline(points).close().extrude(GEAR_FACE_WIDTH_MM / 2.0, both=True).val()
        rack = rack.fuse(tooth)
    return rack.clean()


def finger_carrier(center_x: float) -> cq.Shape:
    slider = rounded_box(14.0, 34.0, 20.0, (center_x, 0.0, -8.0), 2.2)
    for y in (-9.0, 9.0):
        slider = slider.cut(body.cylinder_between((center_x, y, -8.0), (1, 0, 0), 18.0, 4.35))
    finger = rounded_box(12.0, 36.0, 48.0, (center_x, 0.0, -36.0), 3.0)
    relief = rounded_box(6.0, 24.0, 19.0, (center_x, 0.0, -43.0), 2.0)
    return slider.fuse(finger.cut(relief)).clean()


def pad_shape(center_x: float) -> cq.Shape:
    sign = 1.0 if center_x > 0 else -1.0
    finger_inner_face = center_x - sign * FINGER_WIDTH_MM / 2.0
    pad_center = finger_inner_face - sign * PAD_THICKNESS_MM / 2.0
    return rounded_box(PAD_THICKNESS_MM, 30.0, 30.0, (pad_center, 0.0, -36.0), 1.2)


def stop_block(x: float) -> cq.Shape:
    return rounded_box(4.0, 24.0, 9.0, (x, 0.0, -8.0), 1.2)


def build_hand_parts(travel_each_mm: float) -> list[Part]:
    if not 0.0 <= travel_each_mm <= FINGER_TRAVEL_EACH_MM:
        raise ValueError("gripper travel outside candidate hard-stop range")
    positive_center = FINGER_CENTER_CLOSED_MM + travel_each_mm
    negative_center = -positive_center
    positive_rack_center = positive_center - 16.0
    negative_rack_center = negative_center + 16.0

    actuator_path = Path(body.VENDOR_ACTUATOR_SOURCES["ROBOTIS-XC330"]["path"])
    if sha256(actuator_path).upper() != body.VENDOR_ACTUATOR_SOURCES["ROBOTIS-XC330"]["expected_sha256"].upper():
        raise RuntimeError("XC330 source geometry hash drift")
    actuator_native = cq.importers.importStep(str(actuator_path)).val()
    actuator, _basis = body.vendor_actuator_to_axis(actuator_native, (0.0, 10.0, 0.0), (0, 1, 0))

    raw = [
        ("PALM_FRONT_PLATE", "windowed palm frame plate", frame_plate(-27.5), "frame", "PA-CF or 6061-T6 candidate", 1200.0, True, "front service plate; exact process and inserts open"),
        ("PALM_REAR_PLATE", "windowed palm frame plate", frame_plate(27.5), "frame", "PA-CF or 6061-T6 candidate", 1200.0, True, "rear service plate; exact process and inserts open"),
        ("PALM_TOP_BRIDGE", "palm frame bridge", rounded_box(46.0, 50.0, 4.0, (0, 0, 16.0), 2.0), "frame", "PA-CF or 6061-T6 candidate", 1200.0, True, "top load bridge"),
        ("PALM_BOTTOM_BRIDGE", "palm frame bridge", rounded_box(46.0, 50.0, 4.0, (0, 0, -16.0), 2.0), "frame", "PA-CF or 6061-T6 candidate", 1200.0, True, "bottom guide bridge"),
        ("WRIST_MOUNT_PLATE", "wrist interface plate", wrist_mount_plate(), "frame", "6061-T6 candidate", 2700.0, True, "four-hole JMF-01 wrist candidate; fit and fasteners open"),
        ("GUIDE_ROD_FRONT", "linear guide rod", guide_rod(-9.0), "guide", "hardened stainless 4 mm rod candidate", 7850.0, True, "straightness, finish, end retention and wear open"),
        ("GUIDE_ROD_REAR", "linear guide rod", guide_rod(9.0), "guide", "hardened stainless 4 mm rod candidate", 7850.0, True, "straightness, finish, end retention and wear open"),
        ("PINION", "twenty-tooth symmetric-drive pinion", spur_pinion(travel_each_mm), "rack", "POM or aluminum module-0.5 candidate", 1400.0, True, "20-degree involute candidate; manufactured profile, strength and retention open"),
        ("RACK_POSITIVE", "positive-jaw rack", rack_shape(positive_rack_center, True), "rack", "POM module-0.5 candidate", 1400.0, True, "matching 20-degree rack candidate; manufactured profile and wear proof open"),
        ("RACK_NEGATIVE", "negative-jaw rack", rack_shape(negative_rack_center, False), "rack", "POM module-0.5 candidate", 1400.0, True, "matching 20-degree rack candidate; manufactured profile and wear proof open"),
        ("FINGER_POSITIVE", "broad sliding finger and carrier", finger_carrier(positive_center), "finger", "PA-CF or acetal candidate", 1200.0, True, "broad jaw; guide clearance and proof open"),
        ("FINGER_NEGATIVE", "broad sliding finger and carrier", finger_carrier(negative_center), "finger", "PA-CF or acetal candidate", 1200.0, True, "broad jaw; guide clearance and proof open"),
        ("PAD_POSITIVE", "replaceable compliant contact pad", pad_shape(positive_center), "pad", "silicone or PORON coupon selection required", 500.0, True, "force-stroke, wear, contamination and retention open"),
        ("PAD_NEGATIVE", "replaceable compliant contact pad", pad_shape(negative_center), "pad", "silicone or PORON coupon selection required", 500.0, True, "force-stroke, wear, contamination and retention open"),
        ("STOP_POSITIVE", "positive open-travel hard stop", stop_block(31.0), "stop", "PA-CF/POM candidate", 1200.0, True, "hard-stop energy and life proof open"),
        ("STOP_NEGATIVE", "negative open-travel hard stop", stop_block(-31.0), "stop", "PA-CF/POM candidate", 1200.0, True, "hard-stop energy and life proof open"),
        ("MANUAL_RELEASE_HUB", "manual-release pinion hub", body.hollow_cylinder_between((0.0, -5.0, 0.0), (0, 1, 0), 4.0, 8.0, 3.2), "stop", "aluminum or acetal hub candidate", 1400.0, True, "tool-accessible release; received backdrive/breakaway test open"),
        ("ACTUATOR_VENDOR_CANDIDATE", "XC330 packaging body", actuator, "actuator", "ROBOTIS XC330-T288-T evaluation candidate", 0.0, False, "exact SHA-bound B-Rep; mount, spline/horn and received fit open"),
    ]
    parts: list[Part] = []
    for name, kind, shape, color, material, density, fabrication_candidate, note in raw:
        if shape.isNull() or not shape.isValid() or len(shape.Solids()) < 1 or shape.Volume() <= 1e-6:
            raise RuntimeError(f"invalid gripper part {name}")
        parts.append(Part(name, kind, shape, COLORS[color], material, density, fabrication_candidate, note))
    return parts


def translate(shape: cq.Shape, side: str) -> cq.Shape:
    x = HAND_CENTER_X if side == "L" else -HAND_CENTER_X
    return shape.translate((x, 0.0, PALM_CENTER_Z))


def display_shape(part: Part) -> cq.Shape:
    if part.name == "ACTUATOR_VENDOR_CANDIDATE":
        return rounded_box(28.0, 30.0, 34.0, (0.0, 10.0, 0.0), 3.0)
    return part.shape


def assembly_for(parts: list[Part], side: str, name: str) -> cq.Assembly:
    assembly = cq.Assembly(name=name)
    for part in parts:
        assembly.add(translate(display_shape(part), side), name=f"{side}_{part.name}", color=cq.Color(*part.color))
    return assembly


def compound_for(parts: list[Part], side: str, lightweight_actuator: bool = False) -> cq.Shape:
    return cq.Compound.makeCompound([translate(display_shape(part) if lightweight_actuator else part.shape, side) for part in parts])


def export_step(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(shape, str(path))
    body.canonicalize_step(path)


def export_state(parts: list[Part], state: str) -> None:
    for side, module in (("L", "G01"), ("R", "G02")):
        side_dir = OUT / module
        side_dir.mkdir(exist_ok=True)
        step = side_dir / f"{module}_detailed_gripper_{state.lower()}_candidate.step"
        glb = side_dir / f"{module}_detailed_gripper_{state.lower()}_candidate.glb"
        export_step(compound_for(parts, side), step)
        assembly_for(parts, side, f"{module}_{state}_P01_NOT_RELEASED").save(str(glb), tolerance=0.20, angularTolerance=0.15)


def export_installed_state(parts: list[Part], state: str) -> None:
    # Rebuild the installed view from every non-hand fabrication part.  The
    # authoritative fabrication spine now contains the CLOSED hand parts, so
    # importing that STEP and adding this state would duplicate the mechanism.
    # Keeping the base handless here lets CLOSED and OPEN remain honest,
    # mutually exclusive whole-robot configurations.
    import generate_hr30_fabrication_architecture_p01 as fabrication
    robot = cq.Compound.makeCompound([
        candidate.shape for candidate in fabrication.build()[0]
        if candidate.density_kg_m3 > 1.0 and candidate.module not in {"G01", "G02"}
    ])
    solids = [robot, compound_for(parts, "L", True), compound_for(parts, "R", True)]
    step = OUT / f"HR-30_detailed_hands_installed_{state.lower()}_candidate.step"
    export_step(cq.Compound.makeCompound(solids), step)
    assembly = cq.Assembly(name=f"HR30_DETAILED_HANDS_INSTALLED_{state}_P01_NOT_RELEASED")
    assembly.add(robot, name="HR30_MODULAR_BODY", color=cq.Color(0.20, 0.43, 0.66, 0.44))
    for side in ("L", "R"):
        for part in parts:
            assembly.add(translate(display_shape(part), side), name=f"{side}_{part.name}", color=cq.Color(*part.color))
    glb = OUT / f"HR-30_detailed_hands_installed_{state.lower()}_candidate.glb"
    assembly.save(str(glb), tolerance=0.38, angularTolerance=0.20)


def export_unique_parts(parts: list[Part]) -> list[dict]:
    parts_dir = OUT / "parts"
    parts_dir.mkdir()
    rows: list[dict] = []
    for part in parts:
        if part.name in {"RACK_POSITIVE", "RACK_NEGATIVE", "FINGER_POSITIVE", "FINGER_NEGATIVE", "PAD_POSITIVE", "PAD_NEGATIVE"}:
            state_note = "CLOSED-state geometry; translates 13 mm outward per jaw to OPEN state"
        else:
            state_note = "fixed geometry in CLOSED and OPEN states"
        if part.fabrication_candidate:
            step = parts_dir / f"{part.name}.step"
            export_step(part.shape, step)
            part_path = step.relative_to(OUT).as_posix()
            part_sha = sha256(step)
        else:
            source = Path(body.VENDOR_ACTUATOR_SOURCES["ROBOTIS-XC330"]["path"])
            part_path = source.relative_to(ROOT).as_posix()
            part_sha = sha256(source)
        mass = part.shape.Volume() * 1e-9 * part.density_kg_m3 if part.density_kg_m3 > 0 else 0.023
        box = part.shape.BoundingBox()
        rows.append({
            "part_id": part.name,
            "part_kind": part.kind,
            "quantity_per_hand": 1,
            "whole_robot_quantity": 2,
            "fabrication_candidate": str(part.fabrication_candidate).upper(),
            "candidate_material_or_product": part.material,
            "cad_volume_mm3": f"{part.shape.Volume():.6f}",
            "planning_mass_each_kg": f"{mass:.9f}",
            "bbox_xyz_mm": f"{box.xlen:.3f} x {box.ylen:.3f} x {box.zlen:.3f}",
            "source_path": part_path,
            "source_sha256": part_sha,
            "state_relation": state_note,
            "note": part.note,
            "release_state": "DETAILED P0.1 CANDIDATE - FIT/MATERIAL/TOLERANCE/DFM/FAI/PHYSICAL PROOF OPEN",
            "warning": WARNING,
        })
    return rows


def render_index() -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 detailed hands P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#0b203a;--navy:#12345d;--sky:#77c9f2;--pale:#eff9fe;--gold:#f2b91d;--line:#b8d7e8;--ink:#15243b}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{background:var(--deep);color:white;padding:34px max(20px,calc((100vw - 1220px)/2))}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.04;margin:.25em 0}}h2{{font-size:clamp(28px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}main{{max-width:1220px;margin:auto;padding:28px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 3px 0 #c8e5f3}}.card,.panel{{padding:18px}}.metric{{font-size:34px;font-weight:900;color:var(--navy)}}model-viewer{{display:block;width:100%;height:clamp(540px,74vh,820px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p{{padding:0 20px 18px}}button{{font:800 16px/1 system-ui;padding:13px 18px;border:2px solid #075b9b;border-radius:999px;background:white;color:#075b9b;cursor:pointer}}button[aria-pressed="true"]{{background:var(--gold);color:#17243a;border-color:#8a5b00}}.controls{{display:flex;gap:10px;flex-wrap:wrap;padding:16px 20px}}a{{color:#075b9b;font-weight:800}}code{{font-size:15px}}footer{{background:var(--deep);color:white;padding:28px max(20px,calc((100vw - 1220px)/2))}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}model-viewer{{height:560px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><h1>The robot now has mechanisms at the ends of both wrists.</h1><p>Each hand is an actual symmetric rack-and-pinion parallel gripper candidate with a supported palm frame, twin guide rods, broad sliding fingers, replaceable pads, hard stops, manual release access, and the exact XC330 packaging body.</p></header><main><section><h2>Open and close the complete-robot candidate</h2><div class="viewer"><div class="controls"><button id="closed" aria-pressed="true">Closed: 8 mm pad gap</button><button id="open" aria-pressed="false">Open: 34 mm pad gap</button></div><model-viewer id="hand-viewer" src="HR-30_detailed_hands_installed_closed_candidate.glb" poster="../front-elevation.svg" alt="Interactive complete HR-30 candidate with two detailed parallel grippers" camera-controls camera-orbit="30deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>The OPEN state moves both racks and rotates the pinion by the matching pitch displacement. These are geometry states, not commands or proof of movement.</p></div></section><section><h2>Mechanical definition</h2><div class="grid"><article class="card"><div class="metric">20°</div><p>Project-owned involute pinion and matching rack pressure-angle candidate.</p></article><article class="card"><div class="metric">26 mm</div><p>Total coupled jaw stroke: 13 mm per finger.</p></article><article class="card"><div class="metric">8–34 mm</div><p>Candidate pad-to-pad opening range.</p></article><article class="card"><div class="metric">0.08 mm</div><p>Nominal total tangential backlash candidate; physical correlation remains open.</p></article></div></section><section><h2>Files and remaining work</h2><div class="panel"><p><a href="G01/G01_detailed_gripper_closed_candidate.step">Left closed STEP</a> · <a href="G02/G02_detailed_gripper_closed_candidate.step">Right closed STEP</a> · <a href="gripper-part-register.csv">part register</a> · <a href="gripper-kinematic-state-register.csv">kinematic states</a> · <a href="gripper-gear-geometry-register.csv">gear geometry</a> · <a href="gripper-mesh-state-register.csv">mesh states</a> · <a href="gripper-force-screen.csv">force screen</a> · <a href="gripper-interface-register.csv">interfaces</a> · <a href="gripper-candidate-bom.csv">candidate BOM</a> · <a href="gripper-source.py">editable source</a>.</p><p>Manufactured profile/tolerance, materials/processes, guide fit, exact horn adapter, calibration, compliant-pad behavior, object detection, endurance, breakaway release, pinch probing, DFM, FAI and physical proof remain open.</p></div></section></main><footer>Project Button · HR-30 detailed bilateral grippers P0.1 · no procurement, fabrication, assembly, powered-test, motion or energization authority</footer><script>
const viewer=document.getElementById('hand-viewer');const closed=document.getElementById('closed');const open=document.getElementById('open');function setState(state){{const isOpen=state==='open';viewer.setAttribute('src',`HR-30_detailed_hands_installed_${{state}}_candidate.glb`);closed.setAttribute('aria-pressed',String(!isOpen));open.setAttribute('aria-pressed',String(isOpen));}}closed.addEventListener('click',()=>setState('closed'));open.addEventListener('click',()=>setState('open'));
</script></body></html>'''


def update_root(part_rows: list[dict], closed_parts: list[Part]) -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "detailed_bilateral_gripper_package_present": True,
        "detailed_gripper_visible_part_count_per_hand": len(closed_parts),
        "detailed_gripper_unique_part_count": len(part_rows),
        "detailed_gripper_total_coupled_stroke_mm": 26.0,
        "detailed_gripper_closed_pad_gap_mm": 8.0,
        "detailed_gripper_open_pad_gap_mm": 34.0,
        "detailed_gripper_involute_transmission_candidate_defined": True,
        "detailed_gripper_nominal_tangential_backlash_mm": GEAR_TOTAL_TANGENTIAL_BACKLASH_MM,
        "detailed_gripper_mechanism_selected": False,
        "detailed_gripper_force_calibrated": False,
        "detailed_gripper_physical_validation_complete": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-GRIPPERS-P01-README-START -->", "<!-- HR30-GRIPPERS-P01-README-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    addition = f'''{start}
## Detailed bilateral hand mechanisms

The [detailed gripper package](grippers-p0.1/index.html) contains two editable 18-part symmetric rack-and-pinion assemblies. Each now uses a project-owned 20-degree, module-0.5 involute pinion and matching racks with a 0.08 mm nominal total tangential-backlash candidate. The OPEN assembly rotates its pinion 148.969 degrees for the 13 mm rack displacement. CAD-derived states provide an 8–34 mm pad gap over 26 mm total coupled stroke. Manufactured profile tolerance, fits, materials, exact actuator-horn adapter, calibration, sensing, pinch proof, endurance, DFM/FAI and physical validation remain open.
{end}
'''
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    if marker not in readme:
        readme = readme.rstrip() + "\n\n" + addition
    else:
        readme = readme.replace(marker, addition + "\n" + marker)
    readme_path.write_text(readme, encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-GRIPPERS-P01-START -->", "<!-- HR30-GRIPPERS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<!-- HR30-ASSEMBLY-GUIDE-P01-START -->"
    section = f'''{start}<section id="detailed-grippers"><h2>Both wrists now terminate in actual gripper mechanisms</h2><div class="grid"><article class="card pass"><div class="metric">20° involute</div><p>Module-0.5 pinion and matching rack geometry replace rectangular placeholder teeth.</p></article><article class="card pass"><div class="metric">8–34 mm</div><p>CAD-derived pad opening over 26 mm coupled travel.</p></article><article class="card pass"><h3>Coupled installed states</h3><p>The OPEN assembly moves both racks and rotates the pinion 148.969 degrees on the recognizable whole robot.</p></article><article class="card hold"><h3>Physical proof remains open</h3><p>Manufactured profile, fits, materials, horn adapter, calibration, pinch tests, endurance, DFM and FAI are unresolved.</p></article></div><div class="viewer"><model-viewer src="grippers-p0.1/HR-30_detailed_hands_installed_open_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 candidate with both detailed grippers open" camera-controls camera-orbit="30deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="grippers-p0.1/index.html">Open the detailed hand guide</a> · <a href="grippers-p0.1/gripper-gear-geometry-register.csv">gear geometry</a> · <a href="grippers-p0.1/gripper-mesh-state-register.csv">mesh states</a>.</p></div></section>{end}'''
    if marker not in page:
        raise RuntimeError("main page assembly-guide marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    spec = f'''# HR-30 two-hand gripper functional specification P0.1

**{WARNING}**

Each wrist now terminates in a visible and mechanically defined one-DOF symmetric two-finger gripper. The editable candidate uses a 50 x 58 x 40 mm serviceable palm frame, two 4 mm guide rods, two broad sliding finger/carriers, paired module-0.5 20-degree racks, a 20-tooth 10 mm pitch-diameter involute pinion, 0.08 mm nominal total tangential backlash, two replaceable 3 x 30 x 30 mm compliant pads, hard open stops, manual-release access, and one transversely mounted SHA-bound XC330 packaging body.

The CAD-derived coupled stroke is 26 mm: each jaw moves 13 mm from CLOSED to OPEN. The resulting pad gap is 8 mm closed and 34 mm open. The required behaviors remain **grasp**, **hold**, **present**, and **release** a lightweight foam block. P0.1 retains a 20 N total normal-force ceiling, 0.5 kg object-mass ceiling, 0.25 speed scale, guarded closing, and mandatory current/force/position disagreement shutdown.

For the 5 mm pinion pitch radius, equal opposing rack forces give `total normal force = pinion torque / pitch radius`. A 20 N development ceiling therefore corresponds to 0.10 N·m at the pinion. The published 1.0 N·m XC330 12 V stall endpoint would imply 200 N in this ideal geometry and is not a permissible command, continuous rating, or capacity claim. A local deterministic controller must enforce a separately calibrated current/torque limit; the cloud conversational agent never commands raw position, current, or force.

The tooth surfaces are explicit project-owned involute/trapezoidal-rack candidate geometry based on published ISO terminology and basic-rack concepts; this is not a conformity claim. The OPEN CAD state rotates the pinion by `13 / 5 = 2.6 rad = 148.969 degrees`, matching the 13 mm pitch-line rack travel. Closure still requires manufactured profile inspection, rack/guide clearances, an exact actuator-horn adapter, material/process selection, compliant-pad force-stroke and wear evidence, force/current calibration, object-presence sensing, breakaway/manual-release test, pinch probes, holding-power-loss behavior, endurance, DFM, FAI, and supervised grasp/present/release trials.
'''
    (PACKAGE / "gripper-functional-specification.md").write_text(spec, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    closed = build_hand_parts(0.0)
    opened = build_hand_parts(FINGER_TRAVEL_EACH_MM)

    export_state(closed, "CLOSED")
    export_state(opened, "OPEN")
    export_installed_state(closed, "CLOSED")
    export_installed_state(opened, "OPEN")
    part_rows = export_unique_parts(closed)
    write_csv(OUT / "gripper-part-register.csv", part_rows)

    state_rows = []
    for state, travel, parts in (("CLOSED", 0.0, closed), ("OPEN", FINGER_TRAVEL_EACH_MM, opened)):
        positive = next(p for p in parts if p.name == "FINGER_POSITIVE").shape.BoundingBox().center.x
        negative = next(p for p in parts if p.name == "FINGER_NEGATIVE").shape.BoundingBox().center.x
        pad_positive = next(p for p in parts if p.name == "PAD_POSITIVE").shape.BoundingBox()
        pad_negative = next(p for p in parts if p.name == "PAD_NEGATIVE").shape.BoundingBox()
        gap = pad_positive.xmin - pad_negative.xmax
        for side, module in (("L", "G01"), ("R", "G02")):
            state_rows.append({
                "module_id": module, "side": side, "state": state,
                "travel_each_jaw_mm": f"{travel:.3f}", "total_coupled_travel_mm": f"{2*travel:.3f}",
                "positive_finger_center_x_local_mm": f"{positive:.3f}", "negative_finger_center_x_local_mm": f"{negative:.3f}",
                "pad_gap_mm": f"{gap:.3f}", "mechanical_stop_state": "CLOSED POSITION CONTROL / OBJECT CONTACT" if state == "CLOSED" else "BOTH OPEN STOPS",
                "validation_state": "CAD KINEMATIC GEOMETRY ONLY - PHYSICAL CLEARANCE/BACKLASH/FORCE/ENDURANCE OPEN", "warning": WARNING,
            })
    write_csv(OUT / "gripper-kinematic-state-register.csv", state_rows)

    pressure_angle = math.radians(GEAR_PRESSURE_ANGLE_DEG)
    pitch_diameter = 2.0 * PINION_PITCH_RADIUS_MM
    base_diameter = pitch_diameter * math.cos(pressure_angle)
    outside_diameter = pitch_diameter + 2.0 * GEAR_ADDENDUM_MM
    root_diameter = pitch_diameter - 2.0 * GEAR_DEDENDUM_MM
    circular_pitch = math.pi * PINION_MODULE_MM
    standard_pitch_thickness = circular_pitch / 2.0
    member_pitch_thickness = standard_pitch_thickness - GEAR_TOTAL_TANGENTIAL_BACKLASH_MM / 2.0
    gear_rows = [{
        "geometry_id": "GG-01", "geometry_system": "PROJECT-OWNED EXTERNAL SPUR PINION AND TWO STRAIGHT RACKS",
        "module_mm": f"{PINION_MODULE_MM:.6f}", "pressure_angle_deg": f"{GEAR_PRESSURE_ANGLE_DEG:.6f}",
        "pinion_teeth": PINION_TEETH, "pitch_diameter_mm": f"{pitch_diameter:.6f}",
        "base_diameter_mm": f"{base_diameter:.6f}", "outside_diameter_mm": f"{outside_diameter:.6f}",
        "root_diameter_mm": f"{root_diameter:.6f}", "circular_pitch_mm": f"{circular_pitch:.6f}",
        "standard_pitch_tooth_thickness_mm": f"{standard_pitch_thickness:.6f}",
        "pinion_pitch_tooth_thickness_mm": f"{member_pitch_thickness:.6f}",
        "rack_pitch_tooth_thickness_mm": f"{member_pitch_thickness:.6f}",
        "nominal_total_tangential_backlash_mm": f"{GEAR_TOTAL_TANGENTIAL_BACKLASH_MM:.6f}",
        "addendum_mm": f"{GEAR_ADDENDUM_MM:.6f}", "dedendum_mm": f"{GEAR_DEDENDUM_MM:.6f}",
        "face_width_mm": f"{GEAR_FACE_WIDTH_MM:.6f}", "involute_samples_per_flank": GEAR_PROFILE_SAMPLES_PER_FLANK,
        "geometry_basis": "explicit involute equations and trapezoidal basic-rack candidate; ISO terminology reference only; no conformity claim",
        "validation_state": "CAD GEOMETRY DEFINED - MANUFACTURED PROFILE/TOLERANCE/MESH/LIFE PHYSICAL VALIDATION OPEN",
        "warning": WARNING,
    }]
    write_csv(OUT / "gripper-gear-geometry-register.csv", gear_rows)

    mesh_rows = []
    for state, travel, parts in (("CLOSED", 0.0, closed), ("OPEN", FINGER_TRAVEL_EACH_MM, opened)):
        pinion = next(part.shape for part in parts if part.name == "PINION")
        upper_rack = next(part.shape for part in parts if part.name == "RACK_POSITIVE")
        lower_rack = next(part.shape for part in parts if part.name == "RACK_NEGATIVE")
        rotation_rad = travel / PINION_PITCH_RADIUS_MM
        mesh_rows.append({
            "state": state, "rack_travel_each_mm": f"{travel:.6f}",
            "pinion_rotation_rad": f"{rotation_rad:.9f}", "pinion_rotation_deg": f"{math.degrees(rotation_rad):.9f}",
            "pitch_radius_mm": f"{PINION_PITCH_RADIUS_MM:.6f}",
            "expected_pitch_displacement_mm": f"{rotation_rad * PINION_PITCH_RADIUS_MM:.9f}",
            "kinematic_error_mm": f"{abs(rotation_rad * PINION_PITCH_RADIUS_MM - travel):.12f}",
            "upper_solid_interference_volume_mm3": f"{pinion.intersect(upper_rack).Volume():.12f}",
            "lower_solid_interference_volume_mm3": f"{pinion.intersect(lower_rack).Volume():.12f}",
            "upper_minimum_solid_distance_mm": f"{pinion.distance(upper_rack):.9f}",
            "lower_minimum_solid_distance_mm": f"{pinion.distance(lower_rack):.9f}",
            "credit": "NOMINAL CAD MESH STATE ONLY - NO TOLERANCE/LOAD/WEAR/ENDURANCE OR CAPACITY CREDIT",
            "warning": WARNING,
        })
    write_csv(OUT / "gripper-mesh-state-register.csv", mesh_rows)

    force_rows = []
    for case_id, torque, purpose in (("GF-01", 0.05, "10 N low-force development screen"), ("GF-02", 0.10, "20 N project ceiling geometry"), ("GF-03", 1.00, "published stall endpoint comparison only")):
        total_force = torque / (PINION_PITCH_RADIUS_MM / 1000.0)
        force_rows.append({
            "case_id": case_id, "pinion_torque_nm": f"{torque:.3f}", "pinion_pitch_radius_mm": f"{PINION_PITCH_RADIUS_MM:.3f}",
            "ideal_total_normal_force_n": f"{total_force:.3f}", "equal_force_per_finger_n": f"{total_force/2:.3f}",
            "purpose": purpose, "credit": "GEOMETRIC CONVERSION ONLY - NO EFFICIENCY/FRICTION/COMPLIANCE/CURRENT CALIBRATION OR CAPACITY CREDIT", "warning": WARNING,
        })
    write_csv(OUT / "gripper-force-screen.csv", force_rows)

    interface_rows = [
        ("GI-01", "wrist-to-palm", "4 x DIA 3.4 on 26 x 28 mm rectangle; DIA 6.5 center clearance", "JMF-01 wrist output", "shaft/hub, screw product, tapped side, fit, preload and locking"),
        ("GI-02", "finger linear guidance", "2 x DIA 4 mm rods; 64 mm span; 4.35 mm candidate slider bores", "two broad finger carriers", "rod product, straightness, clearance, wear, lubrication and retention"),
        ("GI-03", "symmetric transmission", "module 0.5; 20-degree involute 20-tooth pinion; paired 32 mm matching racks; 0.08 mm nominal total tangential backlash", "13 mm travel each jaw", "manufactured profile/tolerance, physical backlash correlation, exact horn adapter, strength, wear and life"),
        ("GI-04", "object contact", "2 x 3 x 30 x 30 mm replaceable pad lands", "8-34 mm pad gap", "pad material, adhesive/mechanical retention, force-stroke, wear and contamination"),
        ("GI-05", "travel stops", "fixed blocks at local X +/-31 mm", "open hard-stop contact", "impact energy, rebound, noise, tolerance and endurance"),
        ("GI-06", "manual release", "DIA 8 hub with DIA 3.2 tool access", "pinion backdrive path", "tool, access, backdrive torque, breakaway and trapped-object procedure"),
        ("GI-07", "actuator", "SHA-bound XC330 body; output axis +Y at palm datum", "TTL actuator bus and pinion", "exact horn/spline/mount, fasteners, cable exit, current calibration and received identity"),
    ]
    write_csv(OUT / "gripper-interface-register.csv", [{"interface_id": i, "interface": n, "candidate_geometry": g, "connects_to": c, "unresolved_selection_or_evidence": u, "release_state": "P0.1 MECHANICAL CANDIDATE - OPEN", "warning": WARNING} for i, n, g, c, u in interface_rows])

    bom_rows = [
        ("GB-01", "XC330-T288-T evaluation actuator", 2, "ROBOTIS 902-0171-000 candidate; received identity required"),
        ("GB-02", "palm frame custom parts", 10, "five custom frame parts per hand"),
        ("GB-03", "4 mm guide rods", 4, "64 mm hardened stainless candidates"),
        ("GB-04", "module-0.5 rack candidates", 4, "32 mm paired racks"),
        ("GB-05", "module-0.5 pinion candidates", 2, "20 tooth / 10 mm pitch diameter"),
        ("GB-06", "broad finger-carrier candidates", 4, "two per hand"),
        ("GB-07", "replaceable compliant pads", 4, "3 x 30 x 30 mm pad candidates"),
        ("GB-08", "hard stop blocks", 4, "two per hand"),
        ("GB-09", "manual release hubs", 2, "tool and procedure selection required"),
        ("GB-10", "HNX330-N101 metal horn set", 2, "ROBOTIS 903-0314-000 candidate; exact pinion adapter geometry and received fit required"),
        ("GB-11", "frame/motor fasteners and inserts", 2, "complete set per hand; exact products/quantities/torque selection required"),
    ]
    write_csv(OUT / "gripper-candidate-bom.csv", [{"item_id": i, "item": n, "whole_robot_quantity": q, "candidate_or_boundary": c, "selection_state": "SELECTION REQUIRED", "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY", "warning": WARNING} for i, n, q, c in bom_rows])

    source_rows = [
        {"source_id": "GS-01", "source": "ROBOTIS XC330-T288-T official documentation", "url_or_path": "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/", "revision_or_date": "ROBOTIS-GIT source commit 91f72d1ddd3f86d94d74b35ab037f7ec8c8c4dbe / 2026-01-27", "accessed_date": "2026-08-14", "use": "12 V stall endpoint, mass, protocol and candidate identity; no continuous-duty credit", "warning": WARNING},
        {"source_id": "GS-02", "source": "ROBOTIS XC330 official STEP", "url_or_path": body.VENDOR_ACTUATOR_SOURCES["ROBOTIS-XC330"]["path"].relative_to(ROOT).as_posix(), "revision_or_date": body.VENDOR_ACTUATOR_SOURCES["ROBOTIS-XC330"]["expected_sha256"], "accessed_date": "2026-08-10", "use": "SHA-bound packaging geometry", "warning": WARNING},
        {"source_id": "GS-03", "source": "Project HR-30 P0.1 axis and module datums", "url_or_path": "../joint-axis-schedule.csv; ../module-interface-control-register.csv", "revision_or_date": "repository-bound at generation", "accessed_date": "2026-08-14", "use": "wrist centers, gripper axis ownership and module placement", "warning": WARNING},
        {"source_id": "GS-04", "source": "ISO 53:1998 Cylindrical gears for general and heavy engineering - Standard basic rack tooth profile", "url_or_path": "https://www.iso.org/standard/22643.html", "revision_or_date": "Edition 2 / 1998-08 / confirmed current 2021", "accessed_date": "2026-08-14", "use": "basic-rack terminology and geometry basis only; no conformity claim", "warning": WARNING},
        {"source_id": "GS-05", "source": "ISO 54:1996 Cylindrical gears for general engineering and for heavy engineering - Modules", "url_or_path": "https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/02/26/22644.html?browse=tc", "revision_or_date": "Edition 2 / 1996-08 / confirmed current 2022", "accessed_date": "2026-08-14", "use": "module terminology; project selects provisional module 0.5", "warning": WARNING},
        {"source_id": "GS-06", "source": "ISO 21771-1:2024 Cylindrical involute gears and gear pairs - Concepts and geometry", "url_or_path": "https://www.iso.org/standard/84949.html", "revision_or_date": "Edition 1 / 2024-10", "accessed_date": "2026-08-14", "use": "involute-geometry terminology and equation cross-reference only; no conformity claim", "warning": WARNING},
        {"source_id": "GS-07", "source": "ISO 21771-2:2025 Cylindrical involute gears and gear pairs - Calculation of tooth thickness and backlash", "url_or_path": "https://www.iso.org/standard/78378.html", "revision_or_date": "Edition 1 / 2025-12", "accessed_date": "2026-08-14", "use": "tooth-thickness/backlash terminology only; P0.1 backlash remains a project candidate", "warning": WARNING},
        {"source_id": "GS-08", "source": "ROBOTIS HNX330-N101 metal horn set", "url_or_path": "https://robotis.us/hnx330-n101-set/", "revision_or_date": "live official product page; revision/date not stated", "accessed_date": "2026-08-14", "use": "candidate actuator output horn; SKU 903-0314-000; exact adapter dimensions remain selection required", "warning": WARNING},
    ]
    write_csv(OUT / "source-register.csv", source_rows)

    status = {
        "identifier": IDENTIFIER, "bilateral_hand_count": 2, "visible_part_count_per_hand": len(closed),
        "unique_part_record_count": len(part_rows), "custom_fabrication_candidate_count": sum(row["fabrication_candidate"] == "TRUE" for row in part_rows),
        "total_coupled_stroke_mm": 26.0, "closed_pad_gap_mm": 8.0, "open_pad_gap_mm": 34.0,
        "closed_and_open_step_present": True, "closed_and_open_glb_present": True, "installed_whole_robot_states_present": True,
        "web_and_installed_views_use_dimension_matched_simplified_actuator_body": True,
        "editable_source_present": True, "sha_bound_actuator_geometry_present": True,
        "standard_involute_gear_geometry_present": True, "matching_standard_rack_geometry_present": True,
        "transmission_geometry_candidate_defined": True, "gear_mesh_state_count": len(mesh_rows),
        "nominal_total_tangential_backlash_mm": GEAR_TOTAL_TANGENTIAL_BACKLASH_MM,
        "nominal_mesh_interference_volume_mm3_max": max(
            max(float(row["upper_solid_interference_volume_mm3"]), float(row["lower_solid_interference_volume_mm3"]))
            for row in mesh_rows
        ),
        "mechanism_selected": False, "materials_selected": False, "force_calibrated": False,
        "physical_validation_complete": False, "procurement_authority": False, "fabrication_authority": False,
        "assembly_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "gripper-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 detailed bilateral grippers P0.1\n\n**{WARNING}**\n\nTwo editable rack-and-pinion parallel-gripper assemblies replace the prior envelope-only hand refinement path. Their project-owned module-0.5, 20-degree involute pinions and matching racks include an explicit 0.08 mm nominal total tangential-backlash candidate; CLOSED and OPEN native STEP/GLB states now couple rack displacement to pinion rotation. Exact SHA-bound actuator geometry is retained in the native hand STEP assemblies and source register; the GLB and installed whole-robot views use a dimension-matched lightweight actuator body for practical web delivery. Manufactured profile/tolerance, fits, materials, exact horn adapter, calibration, sensing, pinch safety, endurance, DFM, FAI and physical proof remain open.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "gripper-source.py")

    files = [path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in sorted(files)])
    update_root(part_rows, closed)
    system.refresh_manifest_and_release()

    print(json.dumps({"identifier": IDENTIFIER, "hands": 2, "parts_per_hand": len(closed), "unique_part_records": len(part_rows), "closed_gap_mm": 8.0, "open_gap_mm": 34.0, "authority": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
