"""Generate and install the HR-30 bilateral 4:1 compound hip drives.

This is a whole-body packaging candidate, not a capacity or motion release.
Two catalog-backed 16:32 EV5GT stages are arranged at right angles on each
hip pitch/roll axis.  The generator replaces the four prior one-stage hip
drive packages in the complete installed-drivetrain assembly and emits a
recognizable whole humanoid STEP/GLB plus dynamics metadata.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "hip-transmission-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "hip-transmission-p0.1"
IDENTIFIER = "HR30-HIP-TRANSMISSION-P0.1"
WARNING = "PRELIMINARY - WHOLE-BODY HIP TRANSMISSION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
HIP_AXES = ("L_HIP_PITCH", "L_HIP_ROLL", "R_HIP_PITCH", "R_HIP_ROLL")
PITCH_MM = 5.0
BELT_LENGTH_MM = 225.0
BELT_WIDTH_MM = 9.0
STAGE_RATIO = 2.0
TOTAL_RATIO = 4.0
STAGE_PLANE_SPACING_MM = 14.0
CATALOG_SOURCE = "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1348.pdf"
BELT_SOURCE = "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1432.pdf"

sys.path.insert(0, str(ROOT / "tools"))
import generate_hr30_body_architecture_p01 as body  # noqa: E402
import generate_hr30_installed_leg_drivetrains_p01 as installed  # noqa: E402
import generate_hr30_leg_drivetrain_p01 as drives  # noqa: E402
import generate_hr30_leg_drivetrain_adapters_p01 as adapters  # noqa: E402
import generate_hr30_system_package_p01 as system  # noqa: E402


@dataclass(frozen=True)
class HipPart:
    axis_id: str
    part_id: str
    kind: str
    shape: cq.Shape
    visual_shape: cq.Shape
    color: tuple[float, float, float, float]
    material: str
    density_kg_m3: float
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
    d = 16.0 * PITCH_MM / math.pi
    D = 32.0 * PITCH_MM / math.pi
    low, high = (D - d) / 2.0 + 0.01, 120.0
    for _ in range(100):
        c = (low + high) / 2.0
        length = 2.0 * c + math.pi * (D + d) / 2.0 + (D - d) ** 2 / (4.0 * c)
        if length < BELT_LENGTH_MM:
            low = c
        else:
            high = c
    return (low + high) / 2.0


CENTER_MM = solve_center()
STAGE = drives.Drive("HD4-STAGE", "HIP-4-STAGE", 16, 32, 45, 10.0,
                     "GPA16GT5090-A-P10", "GPA32GT5090-A-P12",
                     "GBN225EV5GT-090", "XH540", "HN13-N101", ())
drives.PULLEY_OD_MM[32] = 49.79
drives.PULLEY_FLANGE_OD_MM[32] = 55.0


def cylinder_local(x: float, z: float, length: float, diameter: float, y0: float) -> cq.Shape:
    return body.cylinder_between((x, y0, z), (0, 1, 0), length, diameter)


def bearing_ring_local(x: float, z: float, y0: float) -> cq.Shape:
    return cylinder_local(x, z, 8.0, 28.0, y0).cut(cylinder_local(x, z, 10.0, 12.0, y0)).clean()


def pulley_local(teeth: int, bore: float, x: float, y: float, z: float) -> cq.Shape:
    return drives.pulley_envelope(teeth, bore, 0.0).translate((x, y, z))


def stage2_belt() -> cq.Shape:
    return drives.belt_envelope(STAGE, CENTER_MM)


def stage1_belt() -> cq.Shape:
    return drives.belt_envelope(STAGE, CENTER_MM).rotate((0, 0, 0), (0, 1, 0), 90).translate((0, STAGE_PLANE_SPACING_MM, CENTER_MM))


def carrier_plate(y: float) -> cq.Shape:
    # A three-boss web plate follows the actual L-shaped load path instead of
    # using a dense rectangular slab.  It is directly millable from plate.
    thickness = 4.0
    plate = cylinder_local(0, 0, thickness, 42.0, y)
    plate = plate.fuse(cylinder_local(0, CENTER_MM, thickness, 42.0, y))
    plate = plate.fuse(cylinder_local(CENTER_MM, CENTER_MM, thickness, 48.0, y))
    vertical_web = cq.Workplane("XY").box(18.0, thickness, CENTER_MM + 20.0).translate((0, y, CENTER_MM / 2.0)).val()
    horizontal_web = cq.Workplane("XY").box(CENTER_MM + 20.0, thickness, 18.0).translate((CENTER_MM / 2.0, y, CENTER_MM)).val()
    diagonal_web = body.link_between((0, y, 0), (CENTER_MM, y, CENTER_MM), 9.0)
    # Thin the round-section diagonal to the plate thickness by intersection.
    diagonal_web = diagonal_web.intersect(cq.Workplane("XY").box(CENTER_MM + 50.0, thickness, CENTER_MM + 50.0).translate((CENTER_MM / 2.0, y, CENTER_MM / 2.0)).val())
    plate = plate.fuse(vertical_web).fuse(horizontal_web).fuse(diagonal_web)
    for x, z, diameter in ((0.0, 0.0, 13.0), (0.0, CENTER_MM, 13.0), (CENTER_MM, CENTER_MM, 18.0)):
        plate = plate.cut(cylinder_local(x, z, thickness + 3.0, diameter, y))
    # Two 18 x 6 mm motor-tension slots are explicit machining candidates.
    for z in (CENTER_MM - 14.0, CENTER_MM + 14.0):
        slot = cq.Workplane("XY").box(18.0, 8.0, 6.0).translate((CENTER_MM, y, z)).val()
        plate = plate.cut(slot)
    return plate.clean()


def guard_local() -> cq.Shape:
    width = CENTER_MM + 84.0
    height = CENTER_MM + 84.0
    # The inner carrier is the back barrier.  A 1.5 mm removable outer face
    # and four 3 mm perimeter rails enclose the reachable belt edge without a
    # needlessly heavy six-sided box.
    face = cq.Workplane("XY").box(width, 1.5, height).translate((CENTER_MM / 2.0, 34.0, CENTER_MM / 2.0)).val()
    top = cq.Workplane("XY").box(width, 18.0, 3.0).translate((CENTER_MM / 2.0, 25.0, CENTER_MM / 2.0 + height / 2.0 - 1.5)).val()
    bottom = cq.Workplane("XY").box(width, 18.0, 3.0).translate((CENTER_MM / 2.0, 25.0, CENTER_MM / 2.0 - height / 2.0 + 1.5)).val()
    left = cq.Workplane("XY").box(3.0, 18.0, height - 6.0).translate((CENTER_MM / 2.0 - width / 2.0 + 1.5, 25.0, CENTER_MM / 2.0)).val()
    right = cq.Workplane("XY").box(3.0, 18.0, height - 6.0).translate((CENTER_MM / 2.0 + width / 2.0 - 1.5, 25.0, CENTER_MM / 2.0)).val()
    return face.fuse(top).fuse(bottom).fuse(left).fuse(right).clean()


def local_module() -> list[tuple[str, str, cq.Shape, tuple[float, float, float, float], str, float, str]]:
    output = pulley_local(32, 12.0, 0, 0, 0)
    intermediate_driver = pulley_local(16, 12.0, 0, 0, CENTER_MM)
    intermediate_driven = pulley_local(32, 12.0, 0, STAGE_PLANE_SPACING_MM, CENTER_MM)
    motor = pulley_local(16, 10.0, CENTER_MM, STAGE_PLANE_SPACING_MM, CENTER_MM)
    intermediate_shaft = cylinder_local(0, CENTER_MM, 38.0, 12.0, -12.0)
    bearings = bearing_ring_local(0, CENTER_MM, -12.0).fuse(bearing_ring_local(0, CENTER_MM, 22.0))
    return [
        ("OUTPUT_PULLEY", "catalog 32T output pulley", output, (0.96, .55, .08, 1), "2017 aluminum", 2700, "GPA32GT5090-A-P12; received bore/fit/retention verification open"),
        ("INTERMEDIATE_DRIVER", "catalog 16T intermediate driver", intermediate_driver, (.98, .72, .12, 1), "2017 aluminum", 2700, "GPA16GT5090-A-P12 candidate; compound hub retention open"),
        ("INTERMEDIATE_DRIVEN", "catalog 32T intermediate driven pulley", intermediate_driven, (.96, .55, .08, 1), "2017 aluminum", 2700, "GPA32GT5090-A-P12; compound hub retention open"),
        ("MOTOR_PULLEY", "catalog 16T motor pulley", motor, (.98, .72, .12, 1), "2017 aluminum", 2700, "GPA16GT5090-A-P10; received bore/fit/retention verification open"),
        ("OUTPUT_STAGE_BELT", "225 mm EV5GT output-stage belt", stage2_belt(), (.10, .13, .17, 1), "high-modulus rubber/glass cord", 1150, "GBN225EV5GT-090; tension/capacity/life open"),
        ("MOTOR_STAGE_BELT", "225 mm EV5GT motor-stage belt", stage1_belt(), (.10, .13, .17, 1), "high-modulus rubber/glass cord", 1150, "GBN225EV5GT-090; tension/capacity/life open"),
        ("INTERMEDIATE_SHAFT", "12 mm shouldered intermediate shaft", intermediate_shaft, (.72, .76, .81, 1), "steel candidate", 7850, "material, shoulder, thread, runout and fatigue selection required"),
        ("INTERMEDIATE_BEARINGS", "two 6001 envelope bearings", bearings, (.55, .59, .64, 1), "bearing steel screen", 7850, "2 x 6001-2RS dimensional family; manufacturer/suffix/load/life/fit selection required"),
        ("INNER_CARRIER", "machined three-boss web carrier plate", carrier_plate(-15.0), (.06, .22, .40, 1), "6061-T651 candidate", 2700, "4 mm three-boss web plate; DFM, tolerance and structural proof open"),
        ("OUTER_CARRIER", "slotted three-boss motor/tension carrier", carrier_plate(27.0), (.08, .32, .55, 1), "6061-T651 candidate", 2700, "4 mm web plate with two explicit slots; clamping/fastener proof open"),
        ("REMOVABLE_GUARD", "two-stage removable guard envelope", guard_local(), (.40, .75, .94, .28), "polycarbonate candidate", 1200, "split/access/retention/ventilation and probe validation open"),
    ]


def axis_geometry(axis_id: str, axis: dict, vendor_shapes: dict[str, cq.Shape]) -> tuple[list[HipPart], dict]:
    center = cq.Vector(float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"]))
    axis_dir = installed.axis_vector(axis)
    plane_offset = installed.axial_plane_offset(axis_id)
    outward_axis = axis_dir.multiply(1.0 if plane_offset > 0 else -1.0)
    plane_center = center + axis_dir.multiply(plane_offset)
    drive_dir = cq.Vector(0, 0, -1)  # both hip families package downward into the leg-side service volume
    # Mirror the complete right-side local L path.  Without this transform the
    # right pitch motor projects aft into the right roll service volume instead
    # of matching the left hip's forward/aft separation.
    mirror_lateral = axis_id.startswith("R_")
    parts: list[HipPart] = []
    for suffix, kind, local, color, material, density, note in local_module():
        if mirror_lateral:
            local = local.mirror("YZ")
        world = installed.map_local(local, plane_center, outward_axis, drive_dir)
        parts.append(HipPart(axis_id, f"{axis_id}_{suffix}", kind, world, world, color, material, density, note))

    lateral = outward_axis.cross(drive_dir).multiply(-1.0 if mirror_lateral else 1.0)
    motor_center = plane_center + drive_dir.multiply(CENTER_MM) + lateral.multiply(CENTER_MM) + outward_axis.multiply(STAGE_PLANE_SPACING_MM)
    old_drive = installed.drive_for_axis(axis_id)
    adapter_spec = adapters.motor_adapter_for_axis(axis_id, old_drive)
    horn_spec = adapters.HORN_INTERFACES[adapter_spec.horn_key]
    horn_contact = motor_center - outward_axis.multiply(adapters.FLANGE_THICKNESS_MM + adapters.PULLEY_ENGAGEMENT_MM / 2.0)
    adapter = installed.map_local(adapters.motor_adapter_shape(adapter_spec), horn_contact, outward_axis, drive_dir)
    horn = installed.map_local(adapters.horn_shape_local(adapter_spec.horn_key), horn_contact, outward_axis, drive_dir)
    source_id = body.vendor_source_for_axis(axis_id)
    actuator_output = horn_contact - outward_axis.multiply(horn_spec.contact_y_mm + 0.4)
    actuator, _ = body.vendor_actuator_to_axis(vendor_shapes[source_id], tuple(actuator_output.toTuple()), tuple(outward_axis.toTuple()))
    spec = body.JOINT_MODULE_FAMILIES[body.joint_module_family(axis_id)]
    visual = body.oriented_box(tuple(actuator_output.toTuple()), tuple(outward_axis.toTuple()), spec["body_w"], spec["body_h"], spec["body_d"])
    output_shaft_local, output_cap_local = adapters.output_shaft_local(abs(plane_offset))
    output_shaft = installed.map_local(output_shaft_local, plane_center, outward_axis, drive_dir)
    output_cap = installed.map_local(output_cap_local, plane_center, outward_axis, drive_dir)
    parts.extend([
        HipPart(axis_id, f"{axis_id}_ACTUATOR", "shifted exact XH540 actuator", actuator, visual, (.10,.25,.44,1), "manufacturer assembly", 0, "published 0.165 kg mass used separately; mount/cable clearance open"),
        HipPart(axis_id, f"{axis_id}_HORN", "exact HN13 horn", horn, horn, (.45,.50,.57,1), "manufacturer assembly", 2700, "exact received-reference geometry; fit/thread/load proof open"),
        HipPart(axis_id, f"{axis_id}_MOTOR_ADAPTER", "horn-to-16T pulley adapter", adapter, adapter, (.95,.62,.08,1), "6061-T651 candidate", 2700, "existing nominal adapter family; fastener/capacity proof open"),
        HipPart(axis_id, f"{axis_id}_OUTPUT_SHAFT", "existing shouldered hollow output shaft", output_shaft, output_shaft, (.72,.76,.81,1), "steel candidate", 7850, "material/fit/retention/capacity open"),
        HipPart(axis_id, f"{axis_id}_OUTPUT_CAP", "existing removable output capture", output_cap, output_cap, (.95,.62,.08,1), "6061-T651 candidate", 2700, "through-bolt/locking/proof open"),
    ])
    record = {
        "axis_id": axis_id, "joint_center_mm": f"({center.x:.3f},{center.y:.3f},{center.z:.3f})",
        "output_plane_center_mm": f"({plane_center.x:.3f},{plane_center.y:.3f},{plane_center.z:.3f})",
        "intermediate_center_mm": f"local (0,{STAGE_PLANE_SPACING_MM:.3f},{CENTER_MM:.6f})",
        "motor_center_mm": f"({motor_center.x:.3f},{motor_center.y:.3f},{motor_center.z:.3f})",
        "stage_ratio": "2.000:1", "total_ratio": "4.000:1", "stage_center_distance_mm": f"{CENTER_MM:.9f}",
        "stage_plane_spacing_mm": f"{STAGE_PLANE_SPACING_MM:.3f}", "pulley_set": "2 x GPA16GT5090 + 2 x GPA32GT5090",
        "belt_set": "2 x GBN225EV5GT-090", "intermediate_support": "12 mm shaft + 2 x 6001-2RS dimensional envelope",
        "state": "WHOLE-BODY CAD INSTALLED; CAPACITY, TENSION, FIT, FASTENER, THERMAL AND MOTION PROOF OPEN", "warning": WARNING,
    }
    return parts, record


def update_dynamics() -> None:
    source = WHOLE / "hr30_tether.urdf"
    root = ET.parse(source).getroot()
    for axis_id in HIP_AXES:
        transmission = ET.SubElement(root, "transmission", {"name": f"T_{axis_id}_HIP4_CANDIDATE"})
        ET.SubElement(transmission, "type").text = "transmission_interface/SimpleTransmission"
        joint = ET.SubElement(transmission, "joint", {"name": axis_id})
        ET.SubElement(joint, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        actuator = ET.SubElement(transmission, "actuator", {"name": f"A_{axis_id}_XH540"})
        ET.SubElement(actuator, "hardwareInterface").text = "hardware_interface/EffortJointInterface"
        ET.SubElement(actuator, "mechanicalReduction").text = "4.0"
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(OUT / "hr30_tether_hip4_candidate.urdf", encoding="utf-8", xml_declaration=True)
    successor = WHOLE / "dynamics-successor-p0.1" / "hr30_tether_hip4_inverse_feedforward.xml"
    shutil.copy2(successor, OUT / "hr30_tether_hip4_candidate.xml")


def render_index(total_mass: float, projected_tether_mass: float, interferences: int) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 hip transmission P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#081e38;--blue:#123b68;--sky:#dff4ff;--gold:#f2b91d;--line:#acd8ed;--ink:#152b43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--sky);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,footer{{padding:34px max(20px,calc((100vw - 1200px)/2));background:var(--deep);color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(28px,4vw,44px);color:var(--blue)}}main{{max-width:1200px;margin:auto;padding:28px 20px 80px}}.warning{{padding:16px;background:var(--gold);color:#17243a;border:3px solid #8a5b00;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}.card,.viewer,.panel{{background:white;border:2px solid var(--line);border-radius:18px;padding:18px;overflow:hidden}}.metric{{font-size:36px;font-weight:900;color:var(--blue)}}model-viewer{{display:block;width:100%;height:clamp(560px,72vh,800px);background:radial-gradient(circle,#fff,var(--sky))}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}.grid{{grid-template-columns:1fr}}model-viewer{{height:520px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>Four real compound hip drives are installed on the complete robot.</h1><p>Each hip pitch and roll axis now has two 16:32 timing stages, a supported intermediate shaft, two carrier plates, explicit tension slots, the XH540/horn interface, output retention, and a removable guard.</p></header><main><section><h2>Orbit the integrated humanoid</h2><div class="viewer"><model-viewer src="HR-30_hip4_whole_body_candidate.glb" alt="Complete 762 millimetre HR-30 humanoid with four compound hip transmissions installed" camera-controls camera-orbit="28deg 76deg 100%" field-of-view="27deg" shadow-intensity="0.85"></model-viewer><p><a href="HR-30_hip4_whole_body_candidate.step">whole-body STEP</a> &middot; <a href="HR-30_hip4_transmissions_only_candidate.step">hip-drive STEP</a> &middot; <a href="hr30_tether_hip4_candidate.urdf">URDF</a> &middot; <a href="hr30_tether_hip4_candidate.xml">MJCF</a>.</p></div></section><section><h2>What is physically defined</h2><div class="grid"><article class="card"><div class="metric">4:1</div><p>Two 2:1 stages per hip, using 16- and 32-tooth 5GT pulleys.</p></article><article class="card"><div class="metric">{CENTER_MM:.2f} mm</div><p>Both 225 mm belts close at the same solved pitch-center distance.</p></article><article class="card"><div class="metric">4 axes</div><p>Left/right hip pitch and roll share one mirrored serviceable architecture.</p></article><article class="card"><div class="metric">{interferences}</div><p>nominal common-volume conflicts among the four new rigid drive packages.</p></article></div></section><section><h2>Mass and model boundary</h2><div class="panel"><p>The four candidate drive packages screen at {total_mass:.3f} kg including four published 0.165 kg actuator masses. Replacing the prior hip actuator/pulley/belt allocation projects the active tether configuration to {projected_tether_mass:.3f} kg—{projected_tether_mass - 10.0:.3f} kg above the program maximum. That is a design blocker, not hidden contingency. This is a geometry-density estimate, not received mass. The derived URDF records 4.0 mechanical reduction and the MJCF carries the already executed inverse-feedforward successor scenario. Bearings, shaft material, belt tension/capacity, fasteners, stiffness, efficiency, reflected inertia, heat, guards, cables, motion sweep and physical proof remain open.</p><p><a href="whole-body-mass-impact.csv">Open the replacement mass calculation</a>.</p></div></section></main><footer>Project Button &middot; HR-30 hip transmission P0.1 &middot; no work or energization authority</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"hip4_compound_transmission_cad_present": True, "hip4_axis_count": 4,
                   "hip4_ratio": 4.0, "hip4_whole_body_step_glb_present": True,
                   "hip4_urdf_mjcf_present": True, "hip4_capacity_validated": False,
                   "hip4_motion_sweep_validated": False, "fabrication_authority": False,
                   "motion_authority": False, "energization_authority": False})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    page_path = WHOLE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-HIP4-P01-START -->", "<!-- HR30-HIP4-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    block = f'''{start}<section id="hip4"><h2>The complete humanoid now carries four physical 4:1 compound hip drives</h2><div class="grid"><article class="card pass"><div class="metric">4 axes</div><p>Both hip pitch and roll axes use installed two-stage drive geometry.</p></article><article class="card pass"><div class="metric">2 x 2:1</div><p>Catalog-backed 16:32 stages avoid a single oversized 64-tooth pulley.</p></article><article class="card pass"><h3>Editable whole-body CAD</h3><p>Carrier plates, intermediate shafts, bearings, belts, guards, actuators and output interfaces are visible in STEP and GLB.</p></article><article class="card hold"><h3>Engineering holds remain</h3><p>Capacity, efficiency, reflected inertia, thermal, tension, fasteners, motion sweep and physical proof are open.</p></article></div><p><a href="hip-transmission-p0.1/index.html">Open the interactive hip-drive guide</a> &middot; <a href="hip-transmission-p0.1/HR-30_hip4_whole_body_candidate.step">whole-body STEP</a> &middot; <a href="hip-transmission-p0.1/hip-transmission-register.csv">axis register</a>.</p></section>{end}'''
    marker = "<!-- HR30-INSTALLED-LEG-DRIVES-P01-START -->"
    page = page.replace(marker, block + marker) if marker in page else page.replace("</main>", block + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")

    readme_path = WHOLE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    rs, re = "<!-- HR30-HIP4-P01-README-START -->", "<!-- HR30-HIP4-P01-README-END -->"
    if rs in readme and re in readme:
        readme = readme.split(rs, 1)[0] + readme.split(re, 1)[1]
    text = f'''{rs}\n## Bilateral 4:1 compound hip transmissions\n\nThe [hip-transmission package](hip-transmission-p0.1/index.html) installs physical two-stage 16:32 EV5GT drives on all four hip pitch/roll axes in a derived complete-body STEP/GLB. Each module includes two belts, four pulleys, a supported intermediate shaft, two carrier plates with explicit motor-tension slots, the exact actuator/horn boundary, output retention and a removable guard. Capacity and motion validation remain open.\n{re}\n'''
    marker = "<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-START -->"
    readme = readme.replace(marker, text + marker) if marker in readme else readme.rstrip() + "\n\n" + text
    readme = re.sub(r"\n{3,}", "\n\n", readme)
    readme_path.write_text(readme, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    retained, old_parts, _old_install, _old_collisions = installed.build_installed()
    nonhip = [p for p in old_parts if p.axis_id not in HIP_AXES]
    _, axes, _, _ = body.build()
    axis_map = {r["axis_id"]: r for r in axes}
    vendor_shapes = {sid: cq.importers.importStep(str(src["path"])).val() for sid, src in body.VENDOR_ACTUATOR_SOURCES.items()}
    hip_parts: list[HipPart] = []
    registers: list[dict] = []
    for axis_id in HIP_AXES:
        parts, record = axis_geometry(axis_id, axis_map[axis_id], vendor_shapes)
        hip_parts.extend(parts)
        registers.append(record)

    collisions = []
    for i, axis_a in enumerate(HIP_AXES):
        a = cq.Compound.makeCompound([p.shape for p in hip_parts if p.axis_id == axis_a])
        for axis_b in HIP_AXES[i + 1:]:
            b = cq.Compound.makeCompound([p.shape for p in hip_parts if p.axis_id == axis_b])
            common = a.intersect(b).Volume()
            collisions.append({"first_axis": axis_a, "second_axis": axis_b,
                               "common_volume_mm3": f"{common:.9f}",
                               "minimum_nominal_distance_mm": f"{0.0 if common > 1e-6 else a.distance(b):.6f}",
                               "state": "INTERFERENCE" if common > 1e-6 else "NO COMMON VOLUME",
                               "scope": "NEW HIP PACKAGE TO NEW HIP PACKAGE; NOMINAL RIGID GEOMETRY ONLY", "warning": WARNING})
    interference_count = sum(float(r["common_volume_mm3"]) > 1e-6 for r in collisions)

    mass_rows = []
    total_mass = 0.0
    for part in hip_parts:
        mass = 0.165 if part.kind == "shifted exact XH540 actuator" else part.shape.Volume() * 1e-9 * part.density_kg_m3
        total_mass += mass
        c = part.shape.Center()
        mass_rows.append({"axis_id": part.axis_id, "part_id": part.part_id, "material_or_basis": part.material,
                          "density_kg_m3": f"{part.density_kg_m3:.1f}" if part.density_kg_m3 else "PUBLISHED ACTUATOR MASS",
                          "cad_volume_mm3": f"{part.shape.Volume():.6f}", "planning_mass_kg": f"{mass:.9f}",
                          "center_x_mm": f"{c.x:.6f}", "center_y_mm": f"{c.y:.6f}", "center_z_mm": f"{c.z:.6f}",
                          "state": "GEOMETRY/DENSITY SCREEN; RECEIVED MASS AND SYSTEM RECONCILIATION OPEN", "warning": WARNING})

    with (WHOLE / "mass-item-reconciliation.csv").open(encoding="utf-8", newline="") as handle:
        reconciled = list(csv.DictReader(handle))
    replaced_ids = {
        *(f"ACT-{axis_id}" for axis_id in HIP_AXES),
        *(f"BELT-{axis_id}" for axis_id in HIP_AXES),
        *(f"JHW-JMOD_{axis_id}_OUTPUT_PULLEY" for axis_id in HIP_AXES),
        *(f"JHW-JMOD_{axis_id}_MOTOR_PULLEY" for axis_id in HIP_AXES),
    }
    prior_hip_mass = sum(float(r["planning_candidate_mass_kg"]) for r in reconciled if r["item_id"] in replaced_ids)
    active_tether_mass = float(json.loads((WHOLE / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))["active_tether_dynamics_planning_mass_kg"])
    projected_tether_mass = active_tether_mass - prior_hip_mass + total_mass
    write_csv(OUT / "whole-body-mass-impact.csv", [
        {"configuration": "ACTIVE TETHER BASELINE", "mass_kg": f"{active_tether_mass:.9f}", "calculation": "controlled mass-reconciliation summary", "margin_to_10kg_kg": f"{10.0-active_tether_mass:.9f}", "state": "CURRENT PLANNING MODEL", "warning": WARNING},
        {"configuration": "PRIOR HIP ACTUATOR/PULLEY/BELT ALLOCATION REMOVED", "mass_kg": f"{-prior_hip_mass:.9f}", "calculation": f"{len(replaced_ids)} controlled mass-item IDs", "margin_to_10kg_kg": "N/A", "state": "REPLACEMENT ACCOUNTING", "warning": WARNING},
        {"configuration": "HIP4 COMPOUND PACKAGES ADDED", "mass_kg": f"{total_mass:.9f}", "calculation": "CAD volume x provisional density plus published actuator masses", "margin_to_10kg_kg": "N/A", "state": "GEOMETRY/DENSITY SCREEN", "warning": WARNING},
        {"configuration": "PROJECTED ACTIVE TETHER WITH HIP4", "mass_kg": f"{projected_tether_mass:.9f}", "calculation": "baseline - prior hip allocation + HIP4 package", "margin_to_10kg_kg": f"{10.0-projected_tether_mass:.9f}", "state": "EXCEEDS PROGRAM MAXIMUM; MASS REDESIGN REQUIRED", "warning": WARNING},
    ])

    write_csv(OUT / "hip-transmission-register.csv", registers)
    write_csv(OUT / "hip-package-clearance-register.csv", collisions)
    write_csv(OUT / "hip-transmission-mass-budget.csv", mass_rows)
    write_csv(OUT / "candidate-product-register.csv", [
        {"item": "16T pulley", "candidate": "GPA16GT5090-A-P10/P12", "quantity": 8, "official_source": CATALOG_SOURCE, "revision_date": "MISUMI US catalog 2019; live official PDF accessed 2026-08-17", "selection_state": "CONFIGURABLE CANDIDATE; WRITTEN QUOTE/RECEIPT REQUIRED", "warning": WARNING},
        {"item": "32T pulley", "candidate": "GPA32GT5090-A-P12", "quantity": 8, "official_source": CATALOG_SOURCE, "revision_date": "MISUMI US catalog 2019; live official PDF accessed 2026-08-17", "selection_state": "CONFIGURABLE CANDIDATE; WRITTEN QUOTE/RECEIPT REQUIRED", "warning": WARNING},
        {"item": "225 mm belt", "candidate": "GBN225EV5GT-090", "quantity": 8, "official_source": BELT_SOURCE, "revision_date": "MISUMI US catalog 2019; live official PDF accessed 2026-08-17", "selection_state": "CONFIGURABLE CANDIDATE; CAPACITY/TENSION/LIFE OPEN", "warning": WARNING},
        {"item": "intermediate bearing", "candidate": "6001-2RS DIMENSIONAL FAMILY", "quantity": 8, "official_source": "SELECTION REQUIRED", "revision_date": "SELECTION REQUIRED", "selection_state": "MANUFACTURER/SUFFIX/LOAD/LIFE/FIT SELECTION REQUIRED", "warning": WARNING},
    ])

    transmission_compound = cq.Compound.makeCompound([p.shape for p in hip_parts])
    whole_shapes = [c.shape for c in retained if c.physical] + [p.shape for p in nonhip] + [p.shape for p in hip_parts]
    whole_compound = cq.Compound.makeCompound(whole_shapes)
    cq.exporters.export(transmission_compound, str(OUT / "HR-30_hip4_transmissions_only_candidate.step"))
    cq.exporters.export(whole_compound, str(OUT / "HR-30_hip4_whole_body_candidate.step"))
    body.canonicalize_step(OUT / "HR-30_hip4_transmissions_only_candidate.step")
    body.canonicalize_step(OUT / "HR-30_hip4_whole_body_candidate.step")
    assembly = cq.Assembly(name="HR30_WHOLE_BODY_HIP4_P01_NOT_RELEASED")
    for c in retained:
        assembly.add(c.visual_shape if c.visual_shape is not None else c.shape, name=c.name, color=cq.Color(*c.color))
    for p in nonhip:
        assembly.add(p.visual_shape, name=p.part_id, color=cq.Color(*p.color))
    for p in hip_parts:
        assembly.add(p.visual_shape, name=p.part_id, color=cq.Color(*p.color))
    assembly.save(str(OUT / "HR-30_hip4_whole_body_candidate.glb"), tolerance=.18, angularTolerance=.16)
    hip_assy = cq.Assembly(name="HR30_HIP4_TRANSMISSIONS_P01_NOT_RELEASED")
    for p in hip_parts:
        hip_assy.add(p.visual_shape, name=p.part_id, color=cq.Color(*p.color))
    hip_assy.save(str(OUT / "HR-30_hip4_transmissions_only_candidate.glb"), tolerance=.14, angularTolerance=.13)
    update_dynamics()

    status = {"identifier": IDENTIFIER, "complete_humanoid_present": True, "hip_axis_count": 4,
              "stage_count_per_axis": 2, "total_transmission_ratio": 4.0,
              "editable_step_present": True, "interactive_glb_present": True,
              "urdf_mjcf_present": True, "new_hip_pair_interference_count": interference_count,
              "planning_hip_package_mass_kg": round(total_mass, 9),
              "projected_active_tether_mass_kg": round(projected_tether_mass, 9),
              "projected_margin_to_10kg_kg": round(10.0 - projected_tether_mass, 9),
              "program_mass_maximum_met": projected_tether_mass <= 10.0, "capacity_validated": False,
              "motion_sweep_validated": False, "thermal_validated": False,
              "fabrication_authority": False, "powered_test_authority": False,
              "motion_authority": False, "walking_authority": False, "energization_authority": False,
              "warning": WARNING}
    (OUT / "hip-transmission-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(render_index(total_mass, projected_tether_mass, interference_count), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 hip transmission P0.1\n\n**{WARNING}**\n\nFour physical two-stage 4:1 hip drives are installed in a complete humanoid assembly. Capacity and motion validation remain open.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "hip-transmission-source.py")
    write_csv(OUT / "source-binding.csv", [
        {"source": "tools/generate_hr30_hip_transmission_p01.py", "sha256": sha(Path(__file__)), "role": "compound-drive geometry and whole-body installation", "warning": WARNING},
        {"source": "tools/generate_hr30_installed_leg_drivetrains_p01.py", "sha256": sha(ROOT / "tools/generate_hr30_installed_leg_drivetrains_p01.py"), "role": "current complete installed leg-drive baseline", "warning": WARNING},
        {"source": "hr30/whole-body-p0.1/dynamics-successor-p0.1/hr30_tether_hip4_inverse_feedforward.xml", "sha256": sha(WHOLE / "dynamics-successor-p0.1/hr30_tether_hip4_inverse_feedforward.xml"), "role": "executed 4:1 inverse-feedforward successor model", "warning": WARNING},
    ])
    write_csv(OUT / "open-holds.csv", [
        {"hold_id": f"HIP4-H{i:02d}", "unresolved_item": item, "required_evidence": evidence, "state": "OPEN", "warning": WARNING}
        for i, (item, evidence) in enumerate([
            ("belt/pulley capacity and tension", "manufacturer application calculation plus received-part proof"),
            ("intermediate shaft/bearing life and fits", "selected manufacturer data, load cases, tolerance stack and physical test"),
            ("carrier/fastener stiffness and fatigue", "drawings, FEA/hand checks, received material and proof"),
            ("efficiency, backlash and reflected inertia", "instrumented transmission characterization"),
            ("thermal duty and regeneration", "measured gait duty and power-loss tests"),
            ("whole-body motion/cable/guard sweep", "exact routed harness, collision sweep and guarded physical test"),
            ("remaining knee/ankle torque saturation", "new whole-body drivetrain allocation and rerun dynamics"),
        ], 1)
    ])
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in files])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root()
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0 if interference_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
