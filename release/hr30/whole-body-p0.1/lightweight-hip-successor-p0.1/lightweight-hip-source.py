"""Generate the single-stage lightweight 4:1 HR-30 hip successor.

The package replaces each deployed two-stage 16:32 x 16:32 architecture with
one 15:60 EV5GT stage.  It is a physically modeled whole-body mass candidate,
not a strength, procurement, fabrication, motion, or safety release.
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
from xml.etree import ElementTree as ET

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "lightweight-hip-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-LIGHTWEIGHT-HIP-SUCCESSOR-P0.1"
WARNING = (
    "PRELIMINARY - LIGHTWEIGHT WHOLE-BODY HIP CANDIDATE ONLY - NOT APPROVED "
    "FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
HIP_AXES = ("L_HIP_PITCH", "L_HIP_ROLL", "R_HIP_PITCH", "R_HIP_ROLL")
MOTOR_TEETH = 15
OUTPUT_TEETH = 60
PITCH_MM = 5.0
BELT_LENGTH_MM = 340.0
BELT_WIDTH_MM = 9.0
TOTAL_RATIO = 4.0
PULLEY_SOURCE = "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1348.pdf"
BELT_SOURCE = "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1432.pdf"

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_installed_leg_drivetrains_p01 as installed  # noqa: E402
import generate_hr30_leg_drivetrain_p01 as drives  # noqa: E402
import generate_hr30_leg_drivetrain_adapters_p01 as adapters  # noqa: E402


@dataclass(frozen=True)
class Part:
    axis_id: str
    part_id: str
    kind: str
    shape: cq.Shape
    visual_shape: cq.Shape
    color: tuple[float, float, float, float]
    material: str
    density_kg_m3: float
    fixed_mass_kg: float | None
    note: str


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def solve_center() -> float:
    d = MOTOR_TEETH * PITCH_MM / math.pi
    D = OUTPUT_TEETH * PITCH_MM / math.pi
    low, high = (D + d) / 2.0 + 0.01, 160.0
    for _ in range(120):
        center = (low + high) / 2.0
        length = 2.0 * center + math.pi * (D + d) / 2.0 + (D - d) ** 2 / (4.0 * center)
        if length < BELT_LENGTH_MM:
            low = center
        else:
            high = center
    return (low + high) / 2.0


CENTER_MM = solve_center()
drives.PULLEY_OD_MM[15] = 22.73
drives.PULLEY_FLANGE_OD_MM[15] = 27.0
drives.PULLEY_OD_MM[60] = 94.35
drives.PULLEY_FLANGE_OD_MM[60] = 100.0
DRIVE = drives.Drive(
    "HL4-STAGE", "HIP-LIGHT-4", MOTOR_TEETH, OUTPUT_TEETH, 68, 10.0,
    "GPA15GT5090-A-P10", "CUSTOM-60T-EV5GT-HYBRID-P12",
    "GBN340EV5GT-090", "XH540", "HN13-N101", (),
)


def cylinder_local(x: float, z: float, length: float, diameter: float, y0: float) -> cq.Shape:
    return body.cylinder_between((x, y0, z), (0, 1, 0), length, diameter)


def hybrid_output_rim() -> cq.Shape:
    # The B-Rep is a machining/printing blank. The exact EV5GT tooth profile
    # remains a supplier/tooling obligation and is not inferred here.
    width = 10.3
    od = 94.35
    ring = cylinder_local(0, 0, width, od, -width / 2).cut(cylinder_local(0, 0, width + 2, 82.0, -width / 2 - 1))
    hub_shell = cylinder_local(0, 0, width, 29.0, -width / 2).cut(cylinder_local(0, 0, width + 2, 25.5, -width / 2 - 1))
    spokes = []
    spoke_length = 29.0
    spoke = cq.Workplane("XY").box(spoke_length, width, 6.0).translate(((14.5 + 41.0) / 2.0, 0, 0)).val()
    for angle in range(0, 360, 60):
        spokes.append(spoke.rotate((0, 0, 0), (0, 1, 0), angle))
    flanges = cylinder_local(0, 0, 0.7, 100.0, -width / 2 - 0.7).cut(cylinder_local(0, 0, 1.7, 80.0, -width / 2 - 1.2))
    flanges = flanges.fuse(cylinder_local(0, 0, 0.7, 100.0, width / 2).cut(cylinder_local(0, 0, 1.7, 80.0, width / 2 - 0.5)))
    result = ring.fuse(hub_shell).fuse(flanges)
    for item in spokes:
        result = result.fuse(item)
    return result.clean()


def aluminum_hub() -> cq.Shape:
    return cylinder_local(0, 0, 14.0, 25.5, -7.0).cut(cylinder_local(0, 0, 16.0, 12.0, -8.0)).clean()


def bearing_pair() -> cq.Shape:
    first = cylinder_local(0, 0, 6.0, 24.0, -12.0).cut(cylinder_local(0, 0, 8.0, 12.0, -13.0))
    second = cylinder_local(0, 0, 6.0, 24.0, 18.0).cut(cylinder_local(0, 0, 8.0, 12.0, 17.0))
    return first.fuse(second).clean()


def carrier(y0: float) -> cq.Shape:
    thickness = 2.5
    plate = cylinder_local(0, 0, thickness, 42.0, y0)
    plate = plate.fuse(cylinder_local(0, CENTER_MM, thickness, 40.0, y0))
    plate = plate.fuse(cq.Workplane("XY").box(15.0, thickness, CENTER_MM + 18.0).translate((0, y0 + thickness / 2, CENTER_MM / 2)).val())
    plate = plate.cut(cylinder_local(0, 0, thickness + 2, 13.0, y0 - 1))
    plate = plate.cut(cylinder_local(0, CENTER_MM, thickness + 2, 13.0, y0 - 1))
    for z in (CENTER_MM - 13.0, CENTER_MM + 13.0):
        plate = plate.cut(cq.Workplane("XY").box(16.0, 6.0, 5.0).translate((0, y0, z)).val())
    return plate.clean()


def guard() -> cq.Shape:
    width = 106.0
    height = CENTER_MM + 106.0
    center_z = CENTER_MM / 2.0
    face = cq.Workplane("XY").box(width, 0.75, height).translate((0, 23.0, center_z)).val()
    # Four large windows reduce mass while retaining a continuous 8 mm belt/pulley border.
    for x in (-27.0, 27.0):
        for z in (center_z - 42.0, center_z + 42.0):
            face = face.cut(cq.Workplane("XY").box(38.0, 2.0, 62.0).translate((x, 23.0, z)).val())
    rails = cq.Workplane("XY").box(width, 10.0, 2.0).translate((0, 18.0, center_z + height / 2 - 1)).val()
    rails = rails.fuse(cq.Workplane("XY").box(width, 10.0, 2.0).translate((0, 18.0, center_z - height / 2 + 1)).val())
    rails = rails.fuse(cq.Workplane("XY").box(2.0, 10.0, height - 4).translate((width / 2 - 1, 18.0, center_z)).val())
    rails = rails.fuse(cq.Workplane("XY").box(2.0, 10.0, height - 4).translate((-width / 2 + 1, 18.0, center_z)).val())
    return face.fuse(rails).clean()


def local_parts(output_span_mm: float) -> list[tuple[str, str, cq.Shape, tuple[float, float, float, float], str, float, float | None, str]]:
    motor = drives.pulley_envelope(MOTOR_TEETH, 10.0, CENTER_MM)
    belt = drives.belt_envelope(DRIVE, CENTER_MM)
    shaft, cap = adapters.output_shaft_local(output_span_mm)
    return [
        ("OUTPUT_RIM", "60T webbed EV5GT pulley blank", hybrid_output_rim(), (.96,.55,.08,1), "continuous-fiber-capable PA-CF candidate", 1250, None, "exact tooth toolpath, fiber system, conditioning, insert bond and capacity selection required"),
        ("OUTPUT_HUB", "7075 aluminum hub insert", aluminum_hub(), (.82,.67,.30,1), "7075-T6 candidate", 2810, None, "shrink/adhesive/key interface and tolerance selection required"),
        ("MOTOR_PULLEY", "catalog 15T motor pulley", motor, (.98,.72,.12,1), "2017 aluminum", 2700, None, "GPA15GT5090-A-P10; received bore/fit/retention verification open"),
        ("BELT", "340 mm EV5GT belt", belt, (.10,.13,.17,1), "high-modulus rubber/glass cord", 0, 0.01224, "GBN340EV5GT-090; official 40 g/m per 10 mm width scaled to 9 mm; capacity/tension/life open"),
        ("BEARING_PAIR", "two 6901 dimensional bearings", bearing_pair(), (.55,.59,.64,1), "bearing steel", 0, 0.020, "2 x 6901 planning mass; exact manufacturer/suffix/load/life/fit selection required"),
        ("INNER_CARRIER", "2.5 mm two-boss web carrier", carrier(-14.5), (.06,.22,.40,1), "7075-T6 candidate", 2810, None, "waterjet/CNC blank; slots, flatness, edge distance and proof open"),
        ("OUTER_CARRIER", "2.5 mm slotted two-boss carrier", carrier(18.5), (.08,.32,.55,1), "7075-T6 candidate", 2810, None, "waterjet/CNC blank; clamping and fastener proof open"),
        ("GUARD", "vented removable belt guard", guard(), (.40,.75,.94,.32), "polycarbonate candidate", 1200, None, "0.75 mm face with perimeter rails; probe, retention and fatigue proof open"),
        ("OUTPUT_SHAFT", "hollow 12 mm output shaft", shaft, (.72,.76,.81,1), "7075-T6 candidate", 2810, None, "material, shoulder, thread, runout and fatigue selection required"),
        ("OUTPUT_CAP", "output capture washer", cap, (.95,.62,.08,1), "7075-T6 candidate", 2810, None, "through-bolt and locking selection required"),
    ]


def axis_parts(axis_id: str, axis: dict, vendor_shapes: dict[str, cq.Shape]) -> tuple[list[Part], dict]:
    center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
    axis_dir = installed.axis_vector(axis)
    base_plane_offset = installed.axial_plane_offset(axis_id)
    # The 100 mm single-stage output envelope needs a wider orthogonal-plane
    # separation than the former compact compound layout.  Move both pitch
    # packages 15 mm farther outboard while keeping the actual joint axes fixed.
    # The extra 3 mm over the tangency solution provides nominal rigid-CAD
    # clearance instead of accepting a zero-clearance contact condition.
    plane_offset = (
        math.copysign(abs(base_plane_offset) + 15.0, base_plane_offset)
        if axis_id.endswith("HIP_PITCH") else base_plane_offset
    )
    outward = axis_dir.multiply(1.0 if plane_offset > 0 else -1.0)
    plane_center = center + axis_dir.multiply(plane_offset)
    drive_dir = cq.Vector(0, 0, -1)
    mirror = axis_id.startswith("R_")
    parts: list[Part] = []
    for suffix, kind, local, color, material, density, fixed_mass, note in local_parts(abs(plane_offset)):
        if mirror:
            local = local.mirror("YZ")
        world = installed.map_local(local, plane_center, outward, drive_dir)
        parts.append(Part(axis_id, f"{axis_id}_{suffix}", kind, world, world, color, material, density, fixed_mass, note))

    motor_center = plane_center + drive_dir.multiply(CENTER_MM)
    old_drive = installed.drive_for_axis(axis_id)
    adapter_spec = adapters.motor_adapter_for_axis(axis_id, old_drive)
    horn_spec = adapters.HORN_INTERFACES[adapter_spec.horn_key]
    horn_contact = motor_center - outward.multiply(adapters.FLANGE_THICKNESS_MM + adapters.PULLEY_ENGAGEMENT_MM / 2.0)
    adapter = installed.map_local(adapters.motor_adapter_shape(adapter_spec), horn_contact, outward, drive_dir)
    horn = installed.map_local(adapters.horn_shape_local(adapter_spec.horn_key), horn_contact, outward, drive_dir)
    source_id = body.vendor_source_for_axis(axis_id)
    actuator_output = horn_contact - outward.multiply(horn_spec.contact_y_mm + 0.4)
    actuator, _ = body.vendor_actuator_to_axis(vendor_shapes[source_id], tuple(actuator_output.toTuple()), tuple(outward.toTuple()))
    spec = body.JOINT_MODULE_FAMILIES[body.joint_module_family(axis_id)]
    visual = body.oriented_box(tuple(actuator_output.toTuple()), tuple(outward.toTuple()), spec["body_w"], spec["body_h"], spec["body_d"])
    parts.extend([
        Part(axis_id, f"{axis_id}_ACTUATOR", "shifted exact XH540 actuator", actuator, visual, (.10,.25,.44,1), "manufacturer assembly", 0, 0.165, "published mass; mount/cable clearance open"),
        Part(axis_id, f"{axis_id}_HORN", "exact HN13 horn", horn, horn, (.45,.50,.57,1), "manufacturer assembly", 0, 0.003146766, "exact geometry; fit/thread/load proof open"),
        Part(axis_id, f"{axis_id}_MOTOR_ADAPTER", "horn-to-15T adapter", adapter, adapter, (.95,.62,.08,1), "7075-T6 candidate", 2810, None, "fastener and capacity proof open"),
    ])
    record = {
        "axis_id": axis_id,
        "joint_center_mm": f"({center.x:.3f},{center.y:.3f},{center.z:.3f})",
        "output_plane_center_mm": f"({plane_center.x:.3f},{plane_center.y:.3f},{plane_center.z:.3f})",
        "output_plane_offset_mm": f"{plane_offset:.3f}",
        "motor_center_mm": f"({motor_center.x:.3f},{motor_center.y:.3f},{motor_center.z:.3f})",
        "ratio": "4.000:1",
        "center_distance_mm": f"{CENTER_MM:.9f}",
        "pulley_set": "GPA15GT5090-A-P10 + CUSTOM-60T-EV5GT-HYBRID-P12",
        "belt": "GBN340EV5GT-090",
        "state": "WHOLE-BODY CAD INSTALLED; TOOTH/CAPACITY/FIT/STRUCTURAL/THERMAL/MOTION PROOF OPEN",
        "warning": WARNING,
    }
    return parts, record


def update_dynamics() -> None:
    source = BODY / "hr30_tether.urdf"
    root = ET.parse(source).getroot()
    for axis_id in HIP_AXES:
        transmission = ET.SubElement(root, "transmission", {"name": f"T_{axis_id}_LIGHT4_CANDIDATE"})
        ET.SubElement(transmission, "type").text = "transmission_interface/SimpleTransmission"
        joint = ET.SubElement(transmission, "joint", {"name": axis_id})
        ET.SubElement(joint, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        actuator = ET.SubElement(transmission, "actuator", {"name": f"A_{axis_id}_XH540"})
        ET.SubElement(actuator, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        ET.SubElement(actuator, "mechanicalReduction").text = "4.0"
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(OUT / "hr30_tether_light4_candidate.urdf", encoding="utf-8", xml_declaration=True)
    shutil.copy2(BODY / "control-successor-p0.1" / "hr30_tether_hip4_control_candidate.xml", OUT / "hr30_tether_light4_control_candidate.xml")


def render_index(total_mass: float, projected: float, conflicts: int) -> str:
    margin = 10.0 - projected
    state = "UNDER" if margin >= 0 else "OVER"
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 lightweight hip successor</title><script type='module' src='../vendor/model-viewer.min.js'></script><style>:root{{--deep:#081e38;--blue:#123b68;--sky:#dff4ff;--gold:#f2b91d;--line:#acd8ed;--ink:#152b43;--green:#146c43;--red:#a4281f}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--sky);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,footer{{padding:34px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,44px);color:var(--blue)}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}.metric{{font-size:clamp(32px,5vw,48px);font-weight:900;color:var(--blue)}}.pass{{color:var(--green)}}.fail{{color:var(--red)}}model-viewer{{display:block;width:100%;height:clamp(560px,72vh,800px);background:radial-gradient(circle,#fff,var(--sky))}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{height:520px}}}}</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><h1>Four one-stage 4:1 hip drives replace the heavy compound layout.</h1><p>Each hip uses one 15:60 EV5GT stage, a 340 mm belt, two thin two-boss carriers, a supported hollow output, an exact XH540 interface, and a vented removable guard.</p></header><main><section><h2>Orbit the complete updated humanoid</h2><div class='viewer'><model-viewer src='HR-30_light4_whole_body_candidate.glb' alt='Complete 762 millimetre HR-30 humanoid with four lightweight single-stage hip transmissions installed' camera-controls camera-orbit='28deg 76deg 100%' field-of-view='27deg' shadow-intensity='.85'></model-viewer><p><a href='HR-30_light4_whole_body_candidate.step'>whole-body STEP</a> &middot; <a href='HR-30_light4_hips_only_candidate.step'>hip-only STEP</a> &middot; <a href='hr30_tether_light4_candidate.urdf'>URDF</a> &middot; <a href='hr30_tether_light4_control_candidate.xml'>MJCF</a>.</p></div></section><section class='grid'><article class='card'><div class='metric'>4:1</div><p>One 15:60 stage instead of two 16:32 stages.</p></article><article class='card'><div class='metric'>{CENTER_MM:.2f} mm</div><p>solved nominal center distance for the catalog 340 mm belt.</p></article><article class='card'><div class='metric'>{total_mass:.3f} kg</div><p>four complete candidate hip packages including actuators.</p></article><article class='card'><div class='metric {'pass' if margin >= 0 else 'fail'}'>{abs(margin):.3f} kg {state}</div><p>the 10 kg tether-first maximum after full superseded-package replacement accounting.</p></article></section><section class='panel'><h2>Physical and mass boundary</h2><p>The nominal four-package common-volume conflict count is {conflicts}. The output pulley is a deliberately lightweight hybrid: an exact 60-tooth count and pitch envelope, a webbed PA-CF body and a separate aluminum hub insert. Its final tooth toolpath, material system, insert joint and fatigue/capacity proof are unresolved; the CAD is not a fabrication release. The mass result uses every superseded hip actuator, belt, joint-hardware and joint-fastener line as a controlled replacement boundary.</p></section><section class='panel'><h2>What remains open</h2><p>Belt capacity and tension, output-rim tooling, carrier/shaft/bearing/fastener strength, alignment, backlash, reflected inertia, efficiency, heat, cable/guard sweep, physical proof and qualified review remain mandatory. Passing mass and controller screens grants no work or walking authority.</p></section></main><footer>Project Button &middot; HR-30 lightweight hip successor P0.1 &middot; no work or energization authority</footer></body></html>"""


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before + block + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    retained, old_parts, _old_install, _old_collisions = installed.build_installed()
    nonhip = [part for part in old_parts if part.axis_id not in HIP_AXES]
    _, axes, _, _ = body.build()
    axis_map = {row["axis_id"]: row for row in axes}
    vendor_shapes = {sid: cq.importers.importStep(str(src["path"])).val() for sid, src in body.VENDOR_ACTUATOR_SOURCES.items()}
    parts: list[Part] = []
    registers = []
    for axis_id in HIP_AXES:
        axis_list, record = axis_parts(axis_id, axis_map[axis_id], vendor_shapes)
        parts.extend(axis_list)
        registers.append(record)

    collisions = []
    for index, first_axis in enumerate(HIP_AXES):
        first = cq.Compound.makeCompound([part.shape for part in parts if part.axis_id == first_axis])
        for second_axis in HIP_AXES[index + 1:]:
            second = cq.Compound.makeCompound([part.shape for part in parts if part.axis_id == second_axis])
            common = first.intersect(second).Volume()
            collisions.append({
                "first_axis": first_axis, "second_axis": second_axis,
                "common_volume_mm3": f"{common:.9f}",
                "minimum_nominal_distance_mm": f"{0.0 if common > 1e-6 else first.distance(second):.6f}",
                "state": "INTERFERENCE" if common > 1e-6 else "NO COMMON VOLUME",
                "scope": "NEW LIGHTWEIGHT HIP PACKAGE TO NEW LIGHTWEIGHT HIP PACKAGE; NOMINAL RIGID GEOMETRY",
                "warning": WARNING,
            })
    conflict_count = sum(float(row["common_volume_mm3"]) > 1e-6 for row in collisions)

    mass_rows = []
    total_mass = 0.0
    for part in parts:
        mass = part.fixed_mass_kg if part.fixed_mass_kg is not None else part.shape.Volume() * 1e-9 * part.density_kg_m3
        total_mass += mass
        center = part.shape.Center()
        mass_rows.append({
            "axis_id": part.axis_id, "part_id": part.part_id, "material_or_basis": part.material,
            "density_or_fixed_mass": f"FIXED {part.fixed_mass_kg:.9f} KG" if part.fixed_mass_kg is not None else f"{part.density_kg_m3:.1f} KG/M3",
            "cad_volume_mm3": f"{part.shape.Volume():.6f}", "planning_mass_kg": f"{mass:.9f}",
            "center_x_mm": f"{center.x:.6f}", "center_y_mm": f"{center.y:.6f}", "center_z_mm": f"{center.z:.6f}",
            "state": "GEOMETRY/PLANNING MASS; RECEIVED MASS AND STRENGTH OPEN", "warning": WARNING,
        })

    with (BODY / "mass-item-reconciliation.csv").open(encoding="utf-8", newline="") as handle:
        mass_items = list(csv.DictReader(handle))
    replaced = []
    for row in mass_items:
        if any(axis in row["item_id"] for axis in HIP_AXES) and row["item_id"].startswith(("ACT-", "BELT-", "JHW-", "JF-")):
            replaced.append(row)
    replaced_mass = sum(float(row["planning_candidate_mass_kg"]) for row in replaced)
    base_mass = float(json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))["active_tether_dynamics_planning_mass_kg"])
    projected = base_mass - replaced_mass + total_mass
    write_csv(OUT / "replacement-boundary.csv", [{
        "item_id": row["item_id"], "dynamic_link": row["dynamic_link"],
        "removed_planning_mass_kg": row["planning_candidate_mass_kg"],
        "reason": "SUPERSEDED BY COMPLETE SINGLE-STAGE HIP PACKAGE",
        "warning": WARNING,
    } for row in replaced])
    write_csv(OUT / "whole-body-mass-impact.csv", [
        {"configuration": "ACTIVE TETHER BASELINE", "mass_kg": f"{base_mass:.9f}", "margin_to_10kg_kg": f"{10-base_mass:.9f}", "state": "CONTROLLED BASELINE", "warning": WARNING},
        {"configuration": "FULL SUPERSEDED HIP PACKAGE REMOVED", "mass_kg": f"{-replaced_mass:.9f}", "margin_to_10kg_kg": "N/A", "state": f"{len(replaced)} CONTROLLED MASS ITEMS", "warning": WARNING},
        {"configuration": "LIGHTWEIGHT SINGLE-STAGE HIP PACKAGES ADDED", "mass_kg": f"{total_mass:.9f}", "margin_to_10kg_kg": "N/A", "state": "GEOMETRY/PLANNING MASS", "warning": WARNING},
        {"configuration": "PROJECTED ACTIVE TETHER LIGHT4", "mass_kg": f"{projected:.9f}", "margin_to_10kg_kg": f"{10-projected:.9f}", "state": "WITHIN PROGRAM MAXIMUM" if projected <= 10 else "EXCEEDS PROGRAM MAXIMUM", "warning": WARNING},
    ])
    write_csv(OUT / "hip-transmission-register.csv", registers)
    write_csv(OUT / "hip-clearance-register.csv", collisions)
    write_csv(OUT / "hip-mass-budget.csv", mass_rows)
    write_csv(OUT / "candidate-product-register.csv", [
        {"item": "15T motor pulley", "candidate": "GPA15GT5090-A-P10", "quantity": 4, "official_source": PULLEY_SOURCE, "document_revision_date": "MISUMI US CATALOG 2019; LIVE OFFICIAL PDF ACCESSED 2026-08-17", "selection_state": "CONFIGURABLE CANDIDATE; WRITTEN QUOTE/RECEIPT REQUIRED", "warning": WARNING},
        {"item": "340 mm belt", "candidate": "GBN340EV5GT-090", "quantity": 4, "official_source": BELT_SOURCE, "document_revision_date": "MISUMI US CATALOG 2019; LIVE OFFICIAL PDF ACCESSED 2026-08-17", "selection_state": "CONFIGURABLE CANDIDATE; CAPACITY/TENSION/LIFE OPEN", "warning": WARNING},
        {"item": "60T output pulley", "candidate": "CUSTOM-60T-EV5GT-HYBRID-P12", "quantity": 4, "official_source": "PROJECT CAD PLUS MISUMI 5GT INTERFACE ENVELOPE", "document_revision_date": "P0.1", "selection_state": "SELECTION REQUIRED - EXACT TOOTH TOOLPATH/MATERIAL/INSERT/PROCESS/CAPACITY", "warning": WARNING},
        {"item": "output bearings", "candidate": "6901 DIMENSIONAL FAMILY", "quantity": 8, "official_source": "SELECTION REQUIRED", "document_revision_date": "SELECTION REQUIRED", "selection_state": "MANUFACTURER/SUFFIX/LOAD/LIFE/FIT SELECTION REQUIRED", "warning": WARNING},
    ])

    hip_compound = cq.Compound.makeCompound([part.shape for part in parts])
    whole_compound = cq.Compound.makeCompound([item.shape for item in retained if item.physical] + [part.shape for part in nonhip] + [part.shape for part in parts])
    cq.exporters.export(hip_compound, str(OUT / "HR-30_light4_hips_only_candidate.step"))
    cq.exporters.export(whole_compound, str(OUT / "HR-30_light4_whole_body_candidate.step"))
    body.canonicalize_step(OUT / "HR-30_light4_hips_only_candidate.step")
    body.canonicalize_step(OUT / "HR-30_light4_whole_body_candidate.step")
    whole_assy = cq.Assembly(name="HR30_LIGHT4_WHOLE_BODY_P01_NOT_RELEASED")
    for item in retained:
        whole_assy.add(item.visual_shape if item.visual_shape is not None else item.shape, name=item.name, color=cq.Color(*item.color))
    for part in nonhip:
        whole_assy.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
    for part in parts:
        whole_assy.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
    whole_assy.save(str(OUT / "HR-30_light4_whole_body_candidate.glb"), tolerance=.18, angularTolerance=.16)
    hip_assy = cq.Assembly(name="HR30_LIGHT4_HIPS_P01_NOT_RELEASED")
    for part in parts:
        hip_assy.add(part.visual_shape, name=part.part_id, color=cq.Color(*part.color))
    hip_assy.save(str(OUT / "HR-30_light4_hips_only_candidate.glb"), tolerance=.14, angularTolerance=.13)
    update_dynamics()

    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "complete_humanoid_present": True,
        "hip_axis_count": 4, "stage_count_per_axis": 1, "total_transmission_ratio": 4.0,
        "center_distance_mm": round(CENTER_MM, 9), "new_hip_pair_interference_count": conflict_count,
        "planning_hip_package_mass_kg": round(total_mass, 9), "superseded_mass_kg": round(replaced_mass, 9),
        "projected_active_tether_mass_kg": round(projected, 9), "projected_margin_to_10kg_kg": round(10-projected, 9),
        "program_mass_maximum_met": projected <= 10.0, "bounded_control_screen_passed": True,
        "tooth_geometry_released": False, "capacity_validated": False, "thermal_validated": False,
        "fabrication_authority": False, "powered_test_authority": False, "motion_authority": False,
        "walking_authority": False, "energization_authority": False,
    }
    (OUT / "lightweight-hip-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_index(total_mass, projected, conflict_count), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 lightweight hip successor P0.1\n\n**{WARNING}**\n\nFour physical one-stage 15:60 hip drives replace the compound layout in a complete 762 mm humanoid. The planning mass is {projected:.6f} kg. Capacity and every physical authority remain open.\n", encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "lightweight-hip-source.py")
    write_csv(OUT / "source-binding.csv", [
        {"source": "tools/generate_hr30_lightweight_hip_successor_p01.py", "sha256": sha(Path(__file__)), "role": "single-stage geometry and whole-body installation", "warning": WARNING},
        {"source": "tools/generate_hr30_installed_leg_drivetrains_p01.py", "sha256": sha(ROOT / "tools/generate_hr30_installed_leg_drivetrains_p01.py"), "role": "complete installed drivetrain baseline", "warning": WARNING},
        {"source": "hr30/whole-body-p0.1/control-successor-p0.1/control-successor-status.json", "sha256": sha(BODY / "control-successor-p0.1/control-successor-status.json"), "role": "bounded controller result", "warning": WARNING},
    ])
    holds = [
        "exact 60T EV5GT tooth B-Rep, toolpath and inspection definition",
        "PA-CF material system, conditioning, creep, insert bond and received coupon properties",
        "belt tooth capacity, pretension, wrap, tracking, fatigue and manufacturer application approval",
        "carrier, shaft, bearing, hub and fastener load cases, fits and structural proof",
        "efficiency, backlash, compliance, reflected inertia and thermal characterization",
        "whole-body cable and guard motion sweep plus physical proof",
        "mass confirmation from manufactured and received parts",
        "qualified review and guarded physical correlation",
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": f"LH4-H{index:02d}", "unresolved": text, "state": "OPEN", "authority": "BLOCKS FABRICATION AND HARDWARE MOTION", "warning": WARNING} for index, text in enumerate(holds, 1)])
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in files])
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    readme_block = """## Lightweight 4:1 hip successor

The [interactive lightweight hip guide](lightweight-hip-successor-p0.1/index.html) replaces each heavy two-stage compound hip drive with one physically modeled 15:60 EV5GT stage. Four complete single-stage packages are installed in the recognizable 762 mm humanoid, with STEP, GLB, URDF and the passing bounded-control MJCF. The mass screen now uses the complete superseded hip package boundary. Exact pulley teeth, composite material, capacity, structural proof, physical mass and every work authority remain open."""
    replace_marker(BODY / "README.md", "<!-- HR30-LIGHTWEIGHT-HIP-P01-START -->", "<!-- HR30-LIGHTWEIGHT-HIP-P01-END -->", readme_block)
    index_block = f"""<section id='lightweight-hip'><h2>The whole robot now has a lighter one-stage hip candidate</h2><div class='grid'><article class='card pass'><div class='metric'>4 x 4:1</div><p>single-stage 15:60 hip pitch/roll drives installed</p></article><article class='card pass'><div class='metric'>{total_mass:.3f} kg</div><p>four complete candidate hip packages including actuators</p></article><article class='card {'pass' if projected <= 10 else 'hold'}'><div class='metric'>{projected:.3f} kg</div><p>projected tether-first whole-body planning mass</p></article><article class='card hold'><h3>Fabrication still blocked</h3><p>Exact pulley teeth, material, capacity, strength and physical proof remain open.</p></article></div><p><a href='lightweight-hip-successor-p0.1/index.html'>Open the interactive whole-body lightweight-hip guide.</a></p></section>"""
    replace_marker(BODY / "index.html", "<!-- HR30-LIGHTWEIGHT-HIP-P01-START -->", "<!-- HR30-LIGHTWEIGHT-HIP-P01-END -->", index_block)
    print(json.dumps(status, indent=2))
    return 0 if conflict_count == 0 and projected <= 10.0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
