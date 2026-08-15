"""Generate serviceable HR-30 P0.1 joint-family CAD candidates.

Ten reusable assemblies cover all 25 whole-body axes.  The files expose real
shaft, bearing, carrier, retainer, coupling, transmission, encoder-carrier,
actuator and fastener geometry without claiming selected fits, capacity,
manufacturing release, or permission for powered work.
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

import generate_hr30_body_architecture_p01 as body


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "joint-family-cad"
IDENTIFIER = "HR30-JOINT-FAMILY-CAD-P0.1"
WARNING = body.WARNING
FAMILY_AXIS = {
    "JMF-01-COMPACT": "HEAD_PAN",
    "JMF-02-GRIPPER": "L_GRIPPER",
    "JMF-03-SHOULDER-GIMBAL": "L_SHOULDER_PITCH",
    "JMF-04-MEDIUM": "L_ELBOW_PITCH",
    "JMF-05-WAIST": "WAIST_YAW",
    "JMF-06-LEG-DIRECT": "L_HIP_YAW",
    "JMF-07-LEG-REDUCED-15": "L_HIP_PITCH",
    "JMF-08-LEG-REDUCED-20": "L_HIP_ROLL",
    "JMF-09-KNEE-REDUCED-20": "L_KNEE_PITCH",
    "JMF-10-ANKLE-PITCH-REDUCED-25": "L_ANKLE_PITCH",
}
FAMILY_AXIS_COUNT = {
    "JMF-01-COMPACT": 4,
    "JMF-02-GRIPPER": 2,
    "JMF-03-SHOULDER-GIMBAL": 4,
    "JMF-04-MEDIUM": 2,
    "JMF-05-WAIST": 1,
    "JMF-06-LEG-DIRECT": 2,
    "JMF-07-LEG-REDUCED-15": 2,
    "JMF-08-LEG-REDUCED-20": 4,
    "JMF-09-KNEE-REDUCED-20": 2,
    "JMF-10-ANKLE-PITCH-REDUCED-25": 2,
}
COLORS = {
    "carrier": (0.04, 0.18, 0.34, 1.0),
    "shaft": (0.75, 0.80, 0.84, 1.0),
    "bearing": (0.20, 0.28, 0.36, 1.0),
    "retainer": (0.95, 0.70, 0.08, 1.0),
    "transmission": (0.95, 0.54, 0.08, 1.0),
    "actuator": (0.27, 0.66, 0.88, 1.0),
    "encoder": (0.18, 0.72, 0.62, 1.0),
    "fastener": (0.58, 0.63, 0.68, 1.0),
    "guard": (0.55, 0.82, 0.96, 0.42),
}


@dataclass(frozen=True)
class DetailPart:
    name: str
    kind: str
    shape: cq.Shape
    color: tuple[float, float, float, float]
    material_candidate: str
    density_kg_m3: float
    note: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def annulus(center: tuple[float, float, float], direction: tuple[float, float, float], width: float, od: float, id_: float) -> cq.Shape:
    return body.cylinder_between(center, direction, width, od).cut(body.cylinder_between(center, direction, width + 1.0, id_))


def socket_screw(center: tuple[float, float, float], direction: tuple[float, float, float], shank_length: float, shank_d: float) -> cq.Shape:
    normal = cq.Vector(*direction).normalized()
    shank_center = cq.Vector(*center) + normal.multiply(shank_length / 2.0)
    shank = body.cylinder_between((shank_center.x, shank_center.y, shank_center.z), direction, shank_length, shank_d)
    head_h = max(2.0, shank_d * 0.65)
    head_center = cq.Vector(*center) - normal.multiply(head_h / 2.0)
    head = body.cylinder_between((head_center.x, head_center.y, head_center.z), direction, head_h, shank_d * 1.65)
    return shank.fuse(head).clean()


def belt_candidate(output_d: float, motor_d: float, offset: float, width: float = 10.0) -> cq.Shape:
    """Create a physical smooth-belt candidate around two parallel pulleys."""
    belt_t = 1.4
    output_r = output_d / 2.0 + belt_t / 2.0
    motor_r = motor_d / 2.0 + belt_t / 2.0
    output_ring = annulus((0, 0, 0), (0, 1, 0), width, output_d + belt_t * 2.0, output_d)
    motor_ring = annulus((0, 0, offset), (0, 1, 0), width, motor_d + belt_t * 2.0, motor_d)
    tangent_x = min(output_r, motor_r) - belt_t / 2.0
    run_length = max(1.0, offset - output_r - motor_r + belt_t * 2.0)
    run_center_z = (output_r + (offset - motor_r)) / 2.0
    runs = []
    for sign in (-1.0, 1.0):
        runs.append(cq.Workplane("XY").box(belt_t, width, run_length).translate((sign * tangent_x, 0, run_center_z)).val())
    return output_ring.fuse(motor_ring).fuse(runs[0]).fuse(runs[1]).clean()


def toothed_rack(length: float, side: float) -> cq.Shape:
    base = cq.Workplane("XY").box(length, 5.0, 5.0).translate((0, 0, side * 7.0)).val()
    rack = base
    for x in range(-4, 5):
        tooth = cq.Workplane("XY").box(3.0, 5.0, 2.0).translate((x * 5.0, 0, side * 3.5)).val()
        rack = rack.fuse(tooth)
    return rack.clean()


def component_mass_kg(part: DetailPart) -> float:
    if part.density_kg_m3 <= 0.0:
        return 0.0
    return part.shape.Volume() * 1e-9 * part.density_kg_m3


def build_family(family_id: str, vendor_shapes: dict[str, cq.Shape]) -> tuple[list[DetailPart], dict]:
    spec = body.JOINT_MODULE_FAMILIES[family_id]
    representative_axis = FAMILY_AXIS[family_id]
    normal = (0.0, 1.0, 0.0)
    center = (0.0, 0.0, 0.0)
    span = float(spec["span"])
    plate_t = float(spec["plate_t"])
    bearing_w = float(spec["bearing_w"])
    shaft_d = float(spec["shaft_d"])
    shaft_length = span + 2.0 * plate_t + 4.0
    shaft_bore = max(2.0, shaft_d * 0.62)
    parts: list[DetailPart] = []

    def add(name: str, kind: str, shape: cq.Shape, color: str, material: str, density: float, note: str) -> None:
        if shape.isNull() or not shape.isValid() or shape.Volume() <= 1e-6:
            raise RuntimeError(f"invalid {family_id} part {name}")
        parts.append(DetailPart(name, kind, shape, COLORS[color], material, density, note))

    add("OUTPUT_SHAFT", "hollow output shaft", body.hollow_cylinder_between(center, normal, shaft_length, shaft_d, shaft_bore), "shaft", "17-4PH or alloy-steel candidate - SELECTION REQUIRED", 7800.0, "shoulders, surface finish, hardness and received runout open")
    end_specs = (("A", -1.0), ("B", 1.0)) if int(spec["external_bearings"]) == 2 else (("B", 1.0),)
    plane = body.local_plane(center, normal)
    for end_name, sign in end_specs:
        bearing_y = sign * (span / 2.0 - bearing_w / 2.0)
        plate_y = sign * (span / 2.0 + plate_t / 2.0)
        add(f"BEARING_{end_name}", "catalogue bearing candidate", body.bearing_ring((0, bearing_y, 0), normal, bearing_w, float(spec["bearing_od"]), shaft_d), "bearing", body.BEARING_CANDIDATES[spec["bearing_id"]]["designation"], 7850.0, "application, suffix, fit, lubrication, life and preload open")
        plate = body.interface_plate((0, plate_y, 0), normal, float(spec["plate_w"]), float(spec["plate_h"]), plate_t, float(spec["pattern_x"]), float(spec["pattern_y"]), float(spec["hole_d"]), shaft_d)
        add(f"CARRIER_{end_name}", "removable joint carrier", plate, "carrier", "6061-T6 plate candidate", 2700.0, "machining process, tolerances, inserts and capacity open")
        retainer_y = sign * (span / 2.0 - bearing_w - 0.65)
        add(f"RETAINER_{end_name}", "axial bearing retainer", annulus((0, retainer_y, 0), normal, 1.2, shaft_d + 4.0, shaft_d + 0.25), "retainer", "spring-steel ring or threaded collar candidate", 7850.0, "groove/thread geometry and axial capacity open")
        plate_center = cq.Vector(0, plate_y, 0)
        for ix, x in enumerate((-float(spec["pattern_x"]) / 2.0, float(spec["pattern_x"]) / 2.0)):
            for iz, z in enumerate((-float(spec["pattern_y"]) / 2.0, float(spec["pattern_y"]) / 2.0)):
                hole = plate_center + plane.xDir.multiply(x) + plane.yDir.multiply(z)
                screw_direction = tuple(-sign * v for v in normal)
                add(f"CARRIER_{end_name}_SCREW_{ix+1}{iz+1}", "socket-head carrier screw", socket_screw((hole.x, hole.y, hole.z), screw_direction, plate_t + 7.0, float(spec["hole_d"]) - 0.35), "fastener", "metric alloy-steel screw candidate", 7850.0, "property class, length, tapped side, torque, locking and access open")

    encoder_y = span / 2.0 + plate_t + 1.6
    add("OUTPUT_ENCODER_CARRIER", "output encoder carrier", annulus((0, encoder_y, 0), normal, 2.4, max(shaft_d + 13.0, 22.0), shaft_d + 0.5), "encoder", "magnetic absolute encoder carrier candidate", 1800.0, "sensor, magnet, PCB, accuracy, redundancy and safety role SELECTION REQUIRED")
    add("OUTPUT_MAGNET_HUB", "encoder magnet hub", annulus((0, encoder_y + 1.8, 0), normal, 2.0, shaft_d + 5.0, shaft_d + 0.2), "retainer", "nonmagnetic hub plus magnet candidate", 2700.0, "magnet grade, adhesive, retention and air gap open")

    source_id = body.vendor_source_for_axis(representative_axis)
    motor_offset = float(spec["motor_offset"])
    if family_id == "JMF-02-GRIPPER":
        motor_center = (0.0, -(span / 2.0 + plate_t + float(spec["body_d"]) / 2.0), 0.0)
        actuator, _basis = body.vendor_actuator_to_axis(vendor_shapes[source_id], motor_center, normal)
        add("ACTUATOR", "SHA-bound manufacturer actuator", actuator, "actuator", source_id, 0.0, "exact manufacturer B-Rep; model/suffix and project mount remain provisional")
        add("PINION", "symmetric gripper pinion", body.spoked_pulley(center, normal, 6.0, 20.0, 5.0), "transmission", "POM or aluminum pinion candidate", 1400.0, "tooth form, backlash, strength and retention open")
        add("RACK_UPPER", "gripper rack", toothed_rack(50.0, 1.0), "transmission", "POM rack candidate", 1400.0, "guide, stop, pad and pinch-force validation open")
        add("RACK_LOWER", "gripper rack", toothed_rack(50.0, -1.0), "transmission", "POM rack candidate", 1400.0, "guide, stop, pad and pinch-force validation open")
    elif motor_offset > 0.0:
        motor_center = (0.0, 0.0, motor_offset)
        actuator, _basis = body.vendor_actuator_to_axis(vendor_shapes[source_id], motor_center, normal)
        add("ACTUATOR", "SHA-bound manufacturer actuator", actuator, "actuator", source_id, 0.0, "exact manufacturer B-Rep; exact model/suffix and mount remain provisional")
        output_d = float(spec.get("output_pulley_d", 32.0))
        motor_d = float(spec.get("motor_pulley_d", 24.0))
        add("OUTPUT_PULLEY", "spoked timing-pulley candidate", body.spoked_pulley(center, normal, 12.0, output_d, shaft_d), "transmission", "7075-T6 or reinforced-polymer pulley candidate", 2810.0, "pitch, tooth form, flange, bore and retention open")
        add("MOTOR_PULLEY", "spoked timing-pulley candidate", body.spoked_pulley(motor_center, normal, 12.0, motor_d, 6.0), "transmission", "7075-T6 or reinforced-polymer pulley candidate", 2810.0, "pitch, tooth form, flange, bore and retention open")
        add("TIMING_BELT", "closed-loop belt candidate", belt_candidate(output_d, motor_d, motor_offset), "transmission", "5M elastomer/fiber belt candidate", 1200.0, "exact tooth count, width, preload, rating, guard clearance and life open")
        guard = cq.Workplane("XY").box(max(output_d, motor_d) + 12.0, 16.0, motor_offset + max(output_d, motor_d) + 12.0).translate((0, 0, motor_offset / 2.0)).val()
        inner = cq.Workplane("XY").box(max(output_d, motor_d) + 6.0, 18.0, motor_offset + max(output_d, motor_d) + 6.0).translate((0, 0, motor_offset / 2.0)).val()
        add("TRANSMISSION_GUARD", "removable belt guard", guard.cut(inner), "guard", "printed polymer or thin aluminum guard candidate", 1180.0, "split, retention, vent, pinch access and impact proof open")
    else:
        motor_center = (0.0, -(span / 2.0 + plate_t + float(spec["body_d"]) / 2.0), 0.0)
        actuator, _basis = body.vendor_actuator_to_axis(vendor_shapes[source_id], motor_center, normal)
        add("ACTUATOR", "SHA-bound manufacturer actuator", actuator, "actuator", source_id, 0.0, "exact manufacturer B-Rep; exact model/suffix and project mounting stack remain provisional")
        coupler_mid = (0.0, motor_center[1] / 2.0, 0.0)
        add("OUTPUT_COUPLER", "coaxial clamping coupler", body.hollow_cylinder_between(coupler_mid, normal, abs(motor_center[1]), max(shaft_d + 5.0, 12.0), max(2.0, shaft_d * 0.55)), "transmission", "split-clamp aluminum/steel coupler candidate", 2700.0, "spline/horn interface, clamp preload, fretting and retention open")

    if family_id == "JMF-03-SHOULDER-GIMBAL":
        secondary_center = (42.5, 0.0, 0.0)
        secondary, _basis = body.vendor_actuator_to_axis(vendor_shapes["ROBOTIS-X430"], secondary_center, (1.0, 0.0, 0.0))
        add("ROLL_ACTUATOR", "second SHA-bound gimbal actuator", secondary, "actuator", "ROBOTIS-X430", 0.0, "intersecting-axis shoulder roll candidate; mount and load path open")
        add("ROLL_SHAFT", "intersecting gimbal shaft", body.hollow_cylinder_between(center, (1.0, 0.0, 0.0), span, shaft_d, shaft_bore), "shaft", "17-4PH or alloy-steel candidate", 7800.0, "gimbal cross-shaft shoulders, fits and strength open")
        add("GIMBAL_RING", "intersecting-axis gimbal ring", annulus(center, normal, 8.0, 62.0, 52.0), "carrier", "7075-T6 gimbal ring candidate", 2810.0, "section, split, access and cross-axis capacity open")

    solid = cq.Compound.makeCompound([part.shape for part in parts])
    if solid.isNull() or not solid.isValid() or solid.Volume() <= 1e-6:
        raise RuntimeError(f"invalid family assembly {family_id}")
    box = solid.BoundingBox()
    summary = {
        "family_id": family_id,
        "role": spec["role"],
        "representative_axis": representative_axis,
        "whole_body_axis_count": FAMILY_AXIS_COUNT[family_id],
        "part_count": len(parts),
        "shaft_od_mm": f"{shaft_d:.3f}",
        "shaft_bore_mm": f"{shaft_bore:.3f}",
        "support_span_mm": f"{span:.3f}",
        "bearing_candidate": body.BEARING_CANDIDATES[spec["bearing_id"]]["designation"],
        "external_bearing_count": int(spec["external_bearings"]),
        "carrier_plate_mm": f"{spec['plate_w']:.1f} x {spec['plate_h']:.1f} x {plate_t:.1f}",
        "transmission": spec["transmission"],
        "ratio": spec["ratio"],
        "bbox_x_mm": f"{box.xlen:.3f}",
        "bbox_y_mm": f"{box.ylen:.3f}",
        "bbox_z_mm": f"{box.zlen:.3f}",
        "candidate_non_actuator_mass_kg": f"{sum(component_mass_kg(part) for part in parts):.9f}",
        "release_state": "SERVICEABLE GEOMETRIC CANDIDATE - FITS, CAPACITY, MATERIALS, EXACT HARDWARE AND PHYSICAL VALIDATION OPEN",
        "warning": WARNING,
    }
    return parts, summary


def render_index(rows: list[dict]) -> str:
    cards = []
    for row in rows:
        family = row["family_id"]
        axis_label = "axis" if int(row["whole_body_axis_count"]) == 1 else "axes"
        cards.append(f'''<article class="family"><span>{html.escape(family.replace("JMF-", ""))}</span><div><h3>{html.escape(row["role"])}</h3><p>{row["whole_body_axis_count"]} whole-body {axis_label} · {row["part_count"]} visible candidate parts · {html.escape(row["ratio"])}</p><p><a href="{family}/{family}_assembly.step">STEP</a> · <a href="{family}/{family}_assembly.glb">GLB</a></p></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 joint-family CAD P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#071d36;--navy:#0b3765;--sky:#78cdf4;--pale:#edf8fe;--gold:#f2b91d;--line:#a9d2e8;--ink:#142a40}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{background:var(--deep);color:white;padding:36px max(20px,calc((100vw - 1240px)/2))}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.04;margin:.2em 0}}h2{{font-size:clamp(27px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy);margin:0}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}main{{width:100%;max-width:1240px;margin:auto;padding:28px 20px 80px}}.viewer,.family,.panel{{background:white;border:2px solid var(--line);border-radius:17px;overflow:hidden;box-shadow:0 3px 0 #c4e2f1}}model-viewer{{display:block;width:100%;height:clamp(520px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p,.panel{{padding:16px 20px}}.families{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}}.family{{display:flex;gap:14px;padding:18px}}.family>span{{display:grid;place-items:center;min-width:82px;height:43px;border-radius:11px;background:var(--gold);border:2px solid #8a5b00;font-size:14px;font-weight:900}}.family p{{margin:.25em 0}}a{{color:#075b9b;font-weight:800}}footer{{background:var(--deep);color:white;padding:30px max(20px,calc((100vw - 1240px)/2))}}@media(max-width:560px){{.families{{grid-template-columns:1fr}}.family{{display:block}}.family>span{{margin-bottom:12px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><h1>Ten serviceable joint families for the complete robot.</h1><p>Every HR-30 axis maps to one of these reusable physical stacks. The native geometry includes shafts, catalogue-bearing candidates, truss carriers, retainers, fasteners, actuator B-Reps, transmission members, encoder carriers and guards where applicable.</p></header><main><section><h2>Orbit all ten candidates</h2><div class="viewer"><model-viewer src="HR-30_joint_family_lineup_candidate.glb" poster="../front-elevation.svg" alt="Interactive lineup of ten preliminary HR-30 joint-family assemblies" camera-controls camera-orbit="35deg 70deg 120%" field-of-view="30deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Download the <a href="HR-30_joint_family_lineup_candidate.step">native lineup STEP</a>, <a href="joint-family-stack-register.csv">stack register</a>, <a href="joint-family-part-register.csv">part register</a>, or <a href="fit-retention-register.csv">fit/retention register</a>.</p></div></section><section><h2>Reusable family exports</h2><div class="families">{''.join(cards)}</div></section><section><h2>Buildability boundary</h2><div class="panel"><p>These assemblies make the current mechanical concept explicit and serviceable, but they are not released manufacturing models. Exact shaft material and heat treatment, bearing suffix and life, fits, shoulders/grooves, pulley/belt products, encoder products, fastener property classes, preload/locking, guards, tolerance stacks, capacity, DFM, FAI and physical proof remain unresolved. No work authority follows.</p></div></section></main><footer>Project Button · HR-30 joint-family CAD P0.1 · no procurement, fabrication, assembly, powered-test, motion or energization authority</footer></body></html>'''


def update_package() -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "joint_family_cad_package_present": True,
        "joint_family_cad_export_count": 10,
        "joint_family_cad_axis_coverage_count": 25,
        "joint_family_serviceable_stack_geometry_present": True,
        "joint_family_manufacturing_released": False,
        "joint_family_structural_capacity_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H01":
            row["unresolved_item"] = "Ten reusable serviceable joint-family CAD assemblies now cover all 25 axes with visible shafts, catalogue-bearing candidates, truss carriers, retainers, 156 located whole-body carrier screws, couplers or belt/rack members, output-encoder carriers and guards where applicable. Exact shaft material/heat treatment, bearing suffix/life, fits, shoulders/grooves, pulley/belt/encoder products, fastener property classes, tapped-side material/inserts, torque/preload/locking/access, capacity, DFM, FAI, physical proof and qualified review remain open."
    write_csv(holds_path, holds)

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Separable module CAD\n"
    addition = "\n## Serviceable joint-family CAD\n\nTen native reusable joint-family assemblies cover every one of the 25 axes. Each family exposes a hollow output shaft, aligned catalogue-bearing candidates, removable truss carriers, axial retainers, carrier screws, an output-encoder carrier, exact SHA-bound actuator packaging geometry, and the appropriate direct coupler, belt reduction, shoulder gimbal, or symmetric hand rack/pinion candidate. Native STEP and interactive GLB exports plus stack, part, fit/retention, and assembly registers live in `joint-family-cad/`. They are whole-body refinement artifacts, not manufacturing or work releases; exact fits, materials, products, capacity and physical proof remain open.\n"
    if addition.strip() not in readme:
        if marker not in readme:
            raise RuntimeError("README joint-family marker missing")
        readme_path.write_text(readme.replace(marker, addition + marker), encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-JOINT-FAMILY-CAD-P01-START -->", "<!-- HR30-JOINT-FAMILY-CAD-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<!-- HR30-MODULE-CAD-P01-START -->"
    section = f'''{start}<section id="joint-family-cad"><h2>Ten physical joint families cover all 25 axes</h2><div class="grid"><article class="card pass"><div class="metric">10</div><p>Reusable native joint-family assemblies.</p></article><article class="card pass"><div class="metric">25 / 25</div><p>Every whole-body axis maps to one family.</p></article><article class="card pass"><h3>Serviceable stacks</h3><p>Shafts, bearings, truss carriers, retainers, fasteners, actuator B-Reps, transmissions and encoder carriers are visible and registered.</p></article><article class="card hold"><h3>Still preliminary</h3><p>Exact fits, products, capacity, DFM, FAI and physical proof remain open.</p></article></div><div class="viewer"><model-viewer src="joint-family-cad/HR-30_joint_family_lineup_candidate.glb" poster="front-elevation.svg" alt="Interactive lineup of ten preliminary HR-30 joint-family assemblies" camera-controls camera-orbit="35deg 70deg 120%" field-of-view="30deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="joint-family-cad/index.html">Open the joint-family guide</a> · <a href="joint-family-cad/HR-30_joint_family_lineup_candidate.step">Lineup STEP</a> · <a href="joint-family-cad/joint-family-stack-register.csv">Stack register</a>.</p></div></section>{end}'''
    if marker not in page:
        raise RuntimeError("main page joint-family marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    vendor_shapes: dict[str, cq.Shape] = {}
    for source_id, source in body.VENDOR_ACTUATOR_SOURCES.items():
        path = Path(source["path"])
        if sha256(path).upper() != source["expected_sha256"].upper():
            raise RuntimeError(f"vendor source hash drift: {source_id}")
        vendor_shapes[source_id] = cq.importers.importStep(str(path)).val()

    summary_rows: list[dict] = []
    part_rows: list[dict] = []
    fit_rows: list[dict] = []
    assembly_rows: list[dict] = []
    lineup = cq.Assembly(name="HR30_TEN_JOINT_FAMILIES_P01_NOT_RELEASED")
    lineup_shapes: list[cq.Shape] = []
    for index, family_id in enumerate(body.JOINT_MODULE_FAMILIES):
        family_dir = OUT / family_id
        family_dir.mkdir()
        parts, summary = build_family(family_id, vendor_shapes)
        compound = cq.Compound.makeCompound([part.shape for part in parts])
        step_path = family_dir / f"{family_id}_assembly.step"
        cq.exporters.export(compound, str(step_path))
        body.canonicalize_step(step_path)
        assembly = cq.Assembly(name=f"{family_id}_P01_NOT_RELEASED")
        for part in parts:
            assembly.add(part.shape, name=part.name, color=cq.Color(*part.color))
        glb_path = family_dir / f"{family_id}_assembly.glb"
        assembly.save(str(glb_path), tolerance=0.35, angularTolerance=0.20)
        summary.update({
            "step_path": f"{family_id}/{step_path.name}",
            "step_bytes": step_path.stat().st_size,
            "step_sha256": sha256(step_path),
            "glb_path": f"{family_id}/{glb_path.name}",
            "glb_bytes": glb_path.stat().st_size,
            "glb_sha256": sha256(glb_path),
        })
        summary_rows.append(summary)
        for part in parts:
            part_rows.append({
                "family_id": family_id,
                "part_name": part.name,
                "part_kind": part.kind,
                "solid_count": len(part.shape.Solids()),
                "volume_mm3": f"{part.shape.Volume():.6f}",
                "candidate_non_actuator_mass_kg": f"{component_mass_kg(part):.9f}",
                "material_or_product_candidate": part.material_candidate,
                "note": part.note,
                "authority": "NO PROCUREMENT, FABRICATION, ASSEMBLY, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY",
                "warning": WARNING,
            })
        spec = body.JOINT_MODULE_FAMILIES[family_id]
        interfaces = [
            ("shaft-to-bearing", f"shaft OD {spec['shaft_d']:.3f} / bearing bore {spec['shaft_d']:.3f}", "rotating or fixed-ring fit allocation, tolerance and surface finish SELECTION REQUIRED"),
            ("bearing-to-carrier", f"bearing OD {spec['bearing_od']:.3f} / carrier seat envelope {spec['bearing_od']:.3f}", "housing fit, shoulder, axial clamp and thermal allowance SELECTION REQUIRED"),
            ("carrier-to-link", f"4 x DIA {spec['hole_d']:.1f} on {spec['pattern_x']:.1f} x {spec['pattern_y']:.1f}", "tapped side, insert, screw length, preload, locking and access SELECTION REQUIRED"),
            ("shaft axial retention", "visible retainer/collar candidate both supported ends", "groove or thread, edge distance, fatigue and axial capacity SELECTION REQUIRED"),
            ("output encoder", f"annular carrier outside B support; shaft OD {spec['shaft_d']:.1f}", "sensor, magnet, air gap, accuracy, wiring, redundancy and safety role SELECTION REQUIRED"),
            ("actuator/transmission", spec["transmission"], "exact model, horn/spline or pulley/belt/rack interfaces and proof SELECTION REQUIRED"),
        ]
        for interface_id, geometry, unresolved in interfaces:
            fit_rows.append({"family_id": family_id, "interface_id": interface_id, "nominal_geometry": geometry, "candidate_design_state": "VISIBLE P0.1 GEOMETRIC STACK", "unresolved_selection_or_evidence": unresolved, "warning": WARNING})
        for step, action in enumerate((
            "Inspect carrier seats, shaft, bearing and actuator identities against received parts",
            "Install supported-end bearing candidate(s) into removable truss carrier(s)",
            "Install hollow output shaft, spacer/retainer candidates and verify free rotation",
            "Install direct coupler, gimbal, rack/pinion or belt transmission as assigned",
            "Install exact actuator candidate and establish the project mounting interface",
            "Install output-encoder carrier/magnet candidate and route the service loop",
            "Install carrier screws and guard using released torque/locking instructions only after those exist",
            "Perform unpowered metrology, free-motion, retention and interference checks before any separate powered-work authorization",
        ), 1):
            assembly_rows.append({"family_id": family_id, "step": step, "action": action, "required_release_evidence": "DRAWING/FIT/MATERIAL/HARDWARE/DFM/FAI/PHYSICAL PROCEDURE NOT YET RELEASED", "authority": "UNPOWERED DESIGN SEQUENCE ONLY - NO ASSEMBLY OR POWERED-WORK AUTHORITY", "warning": WARNING})

        x = (index % 5 - 2) * 150.0
        z = (1 - index // 5) * 180.0
        location = cq.Location(cq.Vector(x, 0, z))
        for part in parts:
            moved = part.shape.moved(location)
            lineup_shapes.append(moved)
            lineup.add(moved, name=f"{family_id}_{part.name}", color=cq.Color(*part.color))

    if sum(FAMILY_AXIS_COUNT.values()) != 25:
        raise RuntimeError("joint-family axis coverage drift")
    lineup_step = OUT / "HR-30_joint_family_lineup_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(lineup_shapes), str(lineup_step))
    body.canonicalize_step(lineup_step)
    lineup_glb = OUT / "HR-30_joint_family_lineup_candidate.glb"
    lineup.save(str(lineup_glb), tolerance=0.50, angularTolerance=0.25)
    write_csv(OUT / "joint-family-stack-register.csv", summary_rows)
    write_csv(OUT / "joint-family-part-register.csv", part_rows)
    write_csv(OUT / "fit-retention-register.csv", fit_rows)
    write_csv(OUT / "assembly-sequence.csv", assembly_rows)
    (OUT / "index.html").write_text(render_index(summary_rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 joint-family CAD P0.1\n\n**{WARNING}**\n\nTen reusable native assemblies cover all 25 HR-30 axes. They expose physical shaft, bearing, carrier, retainer, fastener, actuator, transmission, encoder-carrier and guard candidates plus controlled stack, part, fit/retention and assembly registers. Exact vendor actuator B-Reps remain SHA-bound; the rest are editable project-native candidates.\n\nThese files are not released manufacturing CAD. Fits, materials, heat treatment, exact bearing/pulley/belt/encoder/fastener products, capacity, tolerance, DFM, FAI and physical proof remain open.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "joint-family-cad-source.py")
    status = {
        "identifier": IDENTIFIER,
        "joint_family_count": len(summary_rows),
        "whole_body_axis_coverage_count": sum(int(row["whole_body_axis_count"]) for row in summary_rows),
        "visible_candidate_part_count": len(part_rows),
        "fit_retention_record_count": len(fit_rows),
        "assembly_sequence_record_count": len(assembly_rows),
        "lineup_step_present": True,
        "lineup_glb_present": True,
        "exact_vendor_actuator_geometry_present": True,
        "editable_project_source_present": True,
        "fits_selected": False,
        "materials_selected": False,
        "exact_transmission_products_selected": False,
        "structural_capacity_validated": False,
        "physical_validation_complete": False,
        "manufacturing_released": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "joint-family-cad-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    update_package()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
