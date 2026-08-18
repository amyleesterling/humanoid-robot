"""Generate the HR-30 G01 manual first-fit article P0.1.

This is a derived, unpowered physical-learning rig for the authoritative
whole-body left gripper.  It corrects the earlier loose-part print by creating
one manually operable rack-and-pinion mechanism with a retained frame, open
and closed CAD states, bed-ready meshes, a calibration coupon, an inspection
traveler, and an interactive guide.  It grants no production, structural,
powered-test, motion, or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import math
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "first-fit-article-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-G01-FIRST-FIT-ARTICLE-P0.1"
WARNING = (
    "PRELIMINARY - UNPOWERED NONSTRUCTURAL MANUAL FIT ARTICLE ONLY - "
    "NOT APPROVED FOR PRODUCTION FABRICATION, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)

FRAME_WIDTH_MM = 80.0
FRAME_HEIGHT_MM = 42.0
FRAME_OUTER_DEPTH_MM = 58.0
PLATE_THICKNESS_MM = 3.0
PLATE_Y_MM = 27.5
BRIDGE_WIDTH_MM = 76.0
BRIDGE_DEPTH_MM = 50.0
BRIDGE_THICKNESS_MM = 4.0
BRIDGE_Z_MM = 19.0
END_BLOCK_X_MM = 35.5
END_BLOCK_WIDTH_MM = 5.0
END_BLOCK_DEPTH_MM = 50.0
END_BLOCK_HEIGHT_MM = 24.0
GUIDE_Y_MM = 9.0
GUIDE_Z_MM = -8.0
GUIDE_DIAMETER_MM = 4.0
GUIDE_HOLE_DIAMETER_MM = 4.35
GUIDE_LENGTH_MM = 84.0
TIE_HOLE_DIAMETER_MM = 3.4
PINION_SHAFT_DIAMETER_MM = 8.0
PINION_BEARING_HOLE_MM = 8.4
PINION_RETAINER_HOLE_MM = 3.4
FINGER_TRAVEL_EACH_MM = 13.0
BED_X_MM = 220.0
BED_Y_MM = 220.0
BED_MARGIN_MM = 5.0
BED_GAP_MM = 5.0
_GRIPPER_MODULE = None


@dataclass(frozen=True)
class ArticlePart:
    part_id: str
    role: str
    shape: cq.Shape
    color: tuple[float, float, float, float]
    note: str
    bed_rotation_x_deg: float = 0.0
    bed_rotation_y_deg: float = 0.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def rounded_box(x: float, y: float, z: float, center: tuple[float, float, float], radius: float) -> cq.Shape:
    work = cq.Workplane("XY").box(x, y, z)
    try:
        work = work.edges().fillet(min(radius, x / 2 - 0.05, y / 2 - 0.05, z / 2 - 0.05))
    except Exception:
        pass
    return work.translate(center).val()


def cylinder_between(center: tuple[float, float, float], axis: tuple[float, float, float], length: float, diameter: float) -> cq.Shape:
    vector = cq.Vector(*axis).normalized()
    start = cq.Vector(*center) - vector.multiply(length / 2.0)
    return cq.Solid.makeCylinder(diameter / 2.0, length, start, vector)


def valid(shape: cq.Shape, name: str) -> cq.Shape:
    if shape.isNull() or not shape.isValid() or len(shape.Solids()) < 1 or shape.Volume() <= 1e-6:
        raise RuntimeError(f"invalid fit-article part: {name}")
    return shape.clean()


def frame_plate(y: float) -> cq.Shape:
    plate = rounded_box(FRAME_WIDTH_MM, PLATE_THICKNESS_MM, FRAME_HEIGHT_MM, (0, y, 0), 2.0)
    for x in (-17.0, 17.0):
        plate = plate.cut(rounded_box(25.0, 5.0, 26.0, (x, y, 0), 3.0))
    for x in (-28.0, 28.0):
        for z in (-BRIDGE_Z_MM, BRIDGE_Z_MM):
            plate = plate.cut(cylinder_between((x, y, z), (0, 1, 0), 7.0, TIE_HOLE_DIAMETER_MM))
    for x in (-END_BLOCK_X_MM, END_BLOCK_X_MM):
        plate = plate.cut(cylinder_between((x, y, 0.0), (0, 1, 0), 7.0, TIE_HOLE_DIAMETER_MM))
    plate = plate.cut(cylinder_between((0, y, 0), (0, 1, 0), 7.0, PINION_BEARING_HOLE_MM))
    return valid(plate, f"frame plate y={y}")


def bridge(z: float) -> cq.Shape:
    part = rounded_box(BRIDGE_WIDTH_MM, BRIDGE_DEPTH_MM, BRIDGE_THICKNESS_MM, (0, 0, z), 1.6)
    for x in (-28.0, 28.0):
        part = part.cut(cylinder_between((x, 0, z), (0, 1, 0), BRIDGE_DEPTH_MM + 4.0, TIE_HOLE_DIAMETER_MM))
    return valid(part, f"bridge z={z}")


def end_block(x: float) -> cq.Shape:
    part = rounded_box(END_BLOCK_WIDTH_MM, END_BLOCK_DEPTH_MM, END_BLOCK_HEIGHT_MM, (x, 0, GUIDE_Z_MM), 1.4)
    for y in (-GUIDE_Y_MM, GUIDE_Y_MM):
        part = part.cut(cylinder_between((x, y, GUIDE_Z_MM), (1, 0, 0), END_BLOCK_WIDTH_MM + 4.0, GUIDE_HOLE_DIAMETER_MM))
    part = part.cut(cylinder_between((x, 0, 0), (0, 1, 0), END_BLOCK_DEPTH_MM + 4.0, TIE_HOLE_DIAMETER_MM))
    return valid(part, f"end block x={x}")


def guide_rod(y: float) -> cq.Shape:
    return valid(cylinder_between((0, y, GUIDE_Z_MM), (1, 0, 0), GUIDE_LENGTH_MM, GUIDE_DIAMETER_MM), f"guide rod y={y}")


def load_gripper_module():
    global _GRIPPER_MODULE
    if _GRIPPER_MODULE is not None:
        return _GRIPPER_MODULE
    source = WB / "grippers-p0.1" / "gripper-source.py"
    spec = importlib.util.spec_from_file_location("hr30_gripper_source_for_fit_article", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load authoritative gripper source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _GRIPPER_MODULE = module
    return module


def pad_gap_mm(travel_each_mm: float) -> float:
    module = load_gripper_module()
    source_parts = {part.name: part.shape for part in module.build_hand_parts(travel_each_mm)}
    return source_parts["PAD_POSITIVE"].BoundingBox().xmin - source_parts["PAD_NEGATIVE"].BoundingBox().xmax


def moving_parts(travel_each_mm: float) -> tuple[cq.Shape, cq.Shape]:
    module = load_gripper_module()
    source_parts = {part.name: part.shape for part in module.build_hand_parts(travel_each_mm)}
    positive_center = 13.0 + travel_each_mm
    negative_center = -positive_center
    positive_web = rounded_box(7.0, 6.0, 5.0, (positive_center - 3.5, 0.0, 3.6), 0.7)
    negative_web = rounded_box(7.0, 6.0, 5.0, (negative_center + 3.5, 0.0, -3.6), 0.7)
    positive = source_parts["FINGER_POSITIVE"].fuse(source_parts["RACK_POSITIVE"]).fuse(source_parts["PAD_POSITIVE"]).fuse(positive_web)
    negative = source_parts["FINGER_NEGATIVE"].fuse(source_parts["RACK_NEGATIVE"]).fuse(source_parts["PAD_NEGATIVE"]).fuse(negative_web)

    # The authoritative packaging candidate cuts guide bores only through its
    # slider primitive and then fuses the full finger, which re-fills the bores.
    # It also lets the lower opposing rack cross the closed positive finger.
    # This physical-learning derivative corrects both issues explicitly while
    # recording that the resulting moving parts are not production-equivalent.
    for y in (-GUIDE_Y_MM, GUIDE_Y_MM):
        positive = positive.cut(cylinder_between((positive_center, y, GUIDE_Z_MM), (1, 0, 0), 20.0, GUIDE_HOLE_DIAMETER_MM))
        negative = negative.cut(cylinder_between((negative_center, y, GUIDE_Z_MM), (1, 0, 0), 20.0, GUIDE_HOLE_DIAMETER_MM))
    lower_box = source_parts["RACK_NEGATIVE"].BoundingBox()
    upper_box = source_parts["RACK_POSITIVE"].BoundingBox()
    positive = positive.cut(rounded_box(lower_box.xlen + 0.8, lower_box.ylen + 0.8, lower_box.zlen + 0.8, (lower_box.center.x, lower_box.center.y, lower_box.center.z), 0.25))
    negative = negative.cut(rounded_box(upper_box.xlen + 0.8, upper_box.ylen + 0.8, upper_box.zlen + 0.8, (upper_box.center.x, upper_box.center.y, upper_box.center.z), 0.25))
    return valid(positive, "positive moving finger"), valid(negative, "negative moving finger")


def manual_pinion(travel_each_mm: float) -> cq.Shape:
    module = load_gripper_module()
    pinion = next(part.shape for part in module.build_hand_parts(travel_each_mm) if part.name == "PINION")
    shaft = cylinder_between((0, 0, 0), (0, 1, 0), 66.0, PINION_SHAFT_DIAMETER_MM)
    shaft = shaft.cut(cylinder_between((0, 0, 0), (0, 1, 0), 72.0, PINION_RETAINER_HOLE_MM))
    knob = cylinder_between((0, -35.0, 0), (0, 1, 0), 4.0, 16.0)
    knob = knob.cut(cylinder_between((0, -35.0, 0), (0, 1, 0), 8.0, PINION_RETAINER_HOLE_MM))
    return valid(pinion.fuse(shaft).fuse(knob), "manual pinion and shaft")


def calibration_coupon() -> cq.Shape:
    coupon = rounded_box(94.0, 24.0, 5.0, (0, 0, 0), 1.6)
    for index, diameter in enumerate((4.00, 4.20, 4.35, 4.50, 4.70)):
        x = -36.0 + index * 18.0
        coupon = coupon.cut(cylinder_between((x, -5.5, 0), (0, 0, 1), 9.0, diameter))
    for index, diameter in enumerate((3.00, 3.20, 3.40, 3.60)):
        x = -27.0 + index * 18.0
        coupon = coupon.cut(cylinder_between((x, 6.0, 0), (0, 0, 1), 9.0, diameter))
    notch = cq.Workplane("XY").polyline([(-47, -12), (-39, -12), (-47, -4)]).close().extrude(7, both=True).val()
    return valid(coupon.cut(notch), "clearance calibration coupon")


def fixed_parts() -> list[ArticlePart]:
    return [
        ArticlePart("FFA_FRAME_FRONT", "windowed palm frame and front pinion bearing", frame_plate(-PLATE_Y_MM), (0.15, 0.45, 0.75, 1), "M3 tie and 8.4 mm manual-shaft holes", 90.0, 0.0),
        ArticlePart("FFA_FRAME_REAR", "windowed palm frame and rear pinion bearing", frame_plate(PLATE_Y_MM), (0.12, 0.36, 0.64, 1), "M3 tie and 8.4 mm manual-shaft holes", 90.0, 0.0),
        ArticlePart("FFA_TOP_BRIDGE", "upper palm tie bridge", bridge(BRIDGE_Z_MM), (0.18, 0.52, 0.82, 1), "two M3 through ties"),
        ArticlePart("FFA_BOTTOM_BRIDGE", "lower palm tie bridge", bridge(-BRIDGE_Z_MM), (0.18, 0.52, 0.82, 1), "two M3 through ties"),
        ArticlePart("FFA_END_POSITIVE", "positive guide support and open stop", end_block(END_BLOCK_X_MM), (0.12, 0.60, 0.72, 1), "two 4.35 mm guide holes and one M3 tie"),
        ArticlePart("FFA_END_NEGATIVE", "negative guide support and open stop", end_block(-END_BLOCK_X_MM), (0.12, 0.60, 0.72, 1), "two 4.35 mm guide holes and one M3 tie"),
        ArticlePart("FFA_GUIDE_FRONT", "84 mm printed guide proxy", guide_rod(-GUIDE_Y_MM), (0.72, 0.78, 0.84, 1), "replace with measured 4 mm rod after coupon fit"),
        ArticlePart("FFA_GUIDE_REAR", "84 mm printed guide proxy", guide_rod(GUIDE_Y_MM), (0.72, 0.78, 0.84, 1), "replace with measured 4 mm rod after coupon fit"),
    ]


def all_parts(travel_each_mm: float) -> list[ArticlePart]:
    positive, negative = moving_parts(travel_each_mm)
    return fixed_parts() + [
        ArticlePart("FFA_FINGER_RACK_POSITIVE", "fused positive finger, rack and rigid pad proxy", positive, (0.30, 0.72, 0.93, 1), "fit-article-only web; not production gripper geometry", 90.0, 0.0),
        ArticlePart("FFA_FINGER_RACK_NEGATIVE", "fused negative finger, rack and rigid pad proxy", negative, (0.30, 0.72, 0.93, 1), "fit-article-only web; not production gripper geometry", 90.0, 0.0),
        ArticlePart("FFA_MANUAL_PINION", "manual pinion, hollow shaft and knob", manual_pinion(travel_each_mm), (0.96, 0.68, 0.08, 1), "M3 retainer through 8 mm rotating printed shaft", 90.0, 0.0),
    ]


def compound(parts: list[ArticlePart]) -> cq.Shape:
    return cq.Compound.makeCompound([part.shape for part in parts])


def export_step(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(shape, str(path))
    import generate_hr30_body_architecture_p01 as body
    body.canonicalize_step(path)


def export_state(parts: list[ArticlePart], state: str) -> None:
    export_step(compound(parts), OUT / f"HR30_G01_manual_fit_article_{state.lower()}_candidate.step")
    assembly = cq.Assembly(name=f"HR30_G01_MANUAL_FIT_ARTICLE_{state}_P01_NOT_RELEASED")
    for part in parts:
        assembly.add(part.shape, name=part.part_id, color=cq.Color(*part.color))
    assembly.save(str(OUT / f"HR30_G01_manual_fit_article_{state.lower()}_candidate.glb"), tolerance=0.18, angularTolerance=0.14)


def bed_normalize(part: ArticlePart) -> cq.Shape:
    shape = part.shape
    if part.bed_rotation_x_deg:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), part.bed_rotation_x_deg)
    if part.bed_rotation_y_deg:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), part.bed_rotation_y_deg)
    box = shape.BoundingBox()
    return shape.translate((-box.xmin, -box.ymin, -box.zmin))


def pack(parts: list[tuple[ArticlePart, cq.Shape]]) -> tuple[list[dict], list[cq.Shape]]:
    ordered = sorted(parts, key=lambda item: max(item[1].BoundingBox().xlen, item[1].BoundingBox().ylen), reverse=True)
    rows: list[dict] = []
    placed: list[cq.Shape] = []
    x = BED_MARGIN_MM
    y = BED_MARGIN_MM
    shelf_height = 0.0
    for sequence, (part, shape) in enumerate(ordered, 1):
        box = shape.BoundingBox()
        width, depth = box.xlen, box.ylen
        rotation = 0
        if x + width > BED_X_MM - BED_MARGIN_MM and x + depth <= BED_X_MM - BED_MARGIN_MM:
            shape = shape.rotate((0, 0, 0), (0, 0, 1), 90)
            box = shape.BoundingBox()
            shape = shape.translate((-box.xmin, -box.ymin, -box.zmin))
            box = shape.BoundingBox()
            width, depth = box.xlen, box.ylen
            rotation = 90
        if x + width > BED_X_MM - BED_MARGIN_MM:
            x = BED_MARGIN_MM
            y += shelf_height + BED_GAP_MM
            shelf_height = 0.0
        if y + depth > BED_Y_MM - BED_MARGIN_MM:
            raise RuntimeError(f"fit-article plate overflow at {part.part_id}: {x}, {y}, {width}, {depth}")
        translated = shape.translate((x, y, 0))
        placed.append(translated)
        rows.append({
            "sequence": sequence,
            "part_id": part.part_id,
            "placed_x_mm": f"{x:.3f}",
            "placed_y_mm": f"{y:.3f}",
            "plate_rotation_z_deg": rotation,
            "placed_width_mm": f"{width:.3f}",
            "placed_depth_mm": f"{depth:.3f}",
            "placed_height_mm": f"{box.zlen:.3f}",
            "scale": "1:1 MILLIMETRES - DO NOT SCALE",
            "printed": "NO",
            "warning": WARNING,
        })
        x += width + BED_GAP_MM
        shelf_height = max(shelf_height, depth)
    return rows, placed


def layout_svg(rows: list[dict]) -> str:
    scale = 3.0
    shapes = []
    colors = ["#75c9ef", "#f2b91d", "#9ddcf6", "#ffd56a"]
    for index, row in enumerate(rows):
        x = float(row["placed_x_mm"]) * scale
        y = float(row["placed_y_mm"]) * scale
        width = float(row["placed_width_mm"]) * scale
        depth = float(row["placed_depth_mm"]) * scale
        label = html.escape(row["part_id"].replace("FFA_", ""))
        shapes.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{depth:.2f}" rx="5" fill="{colors[index % len(colors)]}" stroke="#071d36" stroke-width="2"/>'
            f'<text x="{x + 6:.2f}" y="{y + 18:.2f}" font-size="12" font-weight="800" fill="#071d36">{index + 1}</text>'
            f'<title>{label}</title>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="760" viewBox="0 0 900 760" role="img">
<title>HR-30 G01 first fit article 220 millimetre candidate plate</title>
<rect width="100%" height="100%" fill="#f6fbff"/><text x="28" y="35" font-family="system-ui,sans-serif" font-size="24" font-weight="900" fill="#071d36">G01 manual fit article · candidate 220 mm plate</text>
<g transform="translate(25 60)"><rect width="660" height="660" fill="#fff" stroke="#0b4f91" stroke-width="3"/>{''.join(shapes)}</g>
<g font-family="system-ui,sans-serif" font-size="16" fill="#142a40"><text x="710" y="90" font-weight="900">11 mechanism parts</text><text x="710" y="122">plus one separate</text><text x="710" y="146">clearance coupon.</text><text x="710" y="198">Slicer collision, support,</text><text x="710" y="222">adhesion and time review</text><text x="710" y="246">remain mandatory.</text><text x="710" y="305" font-weight="900" fill="#8a5b00">UNPOWERED ONLY</text></g></svg>'''


def assembly_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="760" viewBox="0 0 1100 760" role="img">
<title>Dimensioned HR-30 G01 manual fit article</title><rect width="100%" height="100%" fill="#f6fbff"/>
<g font-family="system-ui,sans-serif" fill="#142a40"><text x="45" y="48" font-size="28" font-weight="900" fill="#071d36">G01 first fit article · controlling development dimensions</text>
<rect x="105" y="120" width="560" height="294" rx="18" fill="#fff" stroke="#0b4f91" stroke-width="5"/><rect x="135" y="265" width="35" height="168" rx="8" fill="#77c9f2" stroke="#071d36" stroke-width="3"/><rect x="600" y="265" width="35" height="168" rx="8" fill="#77c9f2" stroke="#071d36" stroke-width="3"/>
<line x1="152" y1="325" x2="618" y2="325" stroke="#657786" stroke-width="9"/><line x1="152" y1="380" x2="618" y2="380" stroke="#657786" stroke-width="9"/>
<rect x="275" y="282" width="80" height="170" rx="18" fill="#8ed8f7" stroke="#071d36" stroke-width="3"/><rect x="415" y="282" width="80" height="170" rx="18" fill="#8ed8f7" stroke="#071d36" stroke-width="3"/><circle cx="385" cy="352" r="38" fill="#f2b91d" stroke="#071d36" stroke-width="4"/><circle cx="385" cy="352" r="12" fill="#fff" stroke="#071d36" stroke-width="3"/>
<line x1="105" y1="472" x2="665" y2="472" stroke="#0b4f91" stroke-width="2"/><path d="M105 462v20M665 462v20" stroke="#0b4f91" stroke-width="2"/><text x="335" y="505" font-size="18" font-weight="900">80 mm frame width</text>
<line x1="720" y1="120" x2="720" y2="414" stroke="#0b4f91" stroke-width="2"/><path d="M710 120h20M710 414h20" stroke="#0b4f91" stroke-width="2"/><text x="744" y="275" font-size="18" font-weight="900">42 mm frame height</text>
<text x="770" y="135" font-size="20" font-weight="900" fill="#0b4f91">Interfaces</text><text x="770" y="175" font-size="17">Rod centres: Y ±9, Z −8 mm</text><text x="770" y="208" font-size="17">Rod: Ø4 × 84 mm proxy</text><text x="770" y="241" font-size="17">Slider bores: Ø4.35 mm</text><text x="770" y="274" font-size="17">Manual shaft: Ø8 / M3 retainer</text><text x="770" y="307" font-size="17">Closed pad gap: 8 mm</text><text x="770" y="340" font-size="17">Open pad gap: 34 mm</text><text x="770" y="373" font-size="17">Travel: 13 mm per jaw</text>
<rect x="70" y="570" width="960" height="118" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="95" y="608" font-size="19" font-weight="900">FIT-ARTICLE DERIVATIVE — NOT THE PRODUCTION HAND</text><text x="95" y="642" font-size="17">Widened frame, longer guide proxies, fused finger/rack/pad parts and manual pinion exist only to obtain physical fit, backlash and cycle evidence.</text><text x="95" y="673" font-size="17">No motor, load, grasp, safety, structural, powered-test, motion or energization credit.</text></g></svg>'''


def source_bindings() -> list[dict]:
    paths = [
        WB / "grippers-p0.1" / "gripper-source.py",
        WB / "grippers-p0.1" / "gripper-status.json",
        WB / "grippers-p0.1" / "gripper-kinematic-state-register.csv",
        WB / "grippers-p0.1" / "gripper-interface-register.csv",
        WB / "full-scale-fit-check-p0.1" / "fit-check-part-register.csv",
        WB / "full-scale-fit-check-p0.1" / "plate-layout-register.csv",
        WB / "grippers-p0.1" / "gripper-part-register.csv",
    ]
    return [{
        "source_id": f"FFA-S{index:02d}",
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "use": "AUTHORITATIVE WHOLE-BODY/GRIPPER INPUT; FIT-ARTICLE DERIVATIVE ONLY",
        "warning": WARNING,
    } for index, path in enumerate(paths, 1)]


def records(closed: list[ArticlePart], opened: list[ArticlePart], plate_rows: list[dict]) -> dict[str, list[dict]]:
    opened_map = {part.part_id: part for part in opened}
    part_rows = []
    for sequence, part in enumerate(closed, 1):
        box = part.shape.BoundingBox()
        part_rows.append({
            "sequence": sequence, "part_id": part.part_id, "role": part.role,
            "quantity": 1, "design_bbox_xyz_mm": f"{box.xlen:.3f} x {box.ylen:.3f} x {box.zlen:.3f}",
            "closed_to_open_relation": "TRANSLATES +13 MM X" if "POSITIVE" in part.part_id and "FINGER" in part.part_id else "TRANSLATES -13 MM X" if "NEGATIVE" in part.part_id and "FINGER" in part.part_id else "ROTATES 148.969 DEG ABOUT +Y" if part.part_id == "FFA_MANUAL_PINION" else "FIXED",
            "fit_article_note": part.note, "production_interchangeable": "NO", "built_quantity": 0, "warning": WARNING,
        })
    hardware = [
        {"item_id": "FFA-HW01", "item": "M3 x 70 mm socket-head screw candidate", "quantity": 7, "purpose": "six frame ties plus one hollow-shaft retainer", "exact_product_state": "SELECTION REQUIRED BEFORE PHYSICAL ASSEMBLY", "substitution_rule": "record actual standard, material, head, length and supplier; unpowered fit only", "warning": WARNING},
        {"item_id": "FFA-HW02", "item": "M3 flat washer candidate", "quantity": 14, "purpose": "protect printed frame faces", "exact_product_state": "SELECTION REQUIRED BEFORE PHYSICAL ASSEMBLY", "substitution_rule": "record actual OD/thickness/material", "warning": WARNING},
        {"item_id": "FFA-HW03", "item": "M3 prevailing-torque nut candidate", "quantity": 7, "purpose": "retain frame ties and pinion axle", "exact_product_state": "SELECTION REQUIRED BEFORE PHYSICAL ASSEMBLY", "substitution_rule": "record actual nut and verify no binding; no torque release", "warning": WARNING},
        {"item_id": "FFA-HW04", "item": "4 mm x 84 mm smooth guide rod", "quantity": 2, "purpose": "preferred physical guide after coupon check; printed proxies included", "exact_product_state": "SELECTION REQUIRED / RECEIVED DIAMETER AND STRAIGHTNESS REQUIRED", "substitution_rule": "do not force oversize rod through printed parts", "warning": WARNING},
        {"item_id": "FFA-HW05", "item": "4 mm removable shaft collar", "quantity": 4, "purpose": "temporary rod retention outside end blocks", "exact_product_state": "SELECTION REQUIRED BEFORE PHYSICAL ASSEMBLY", "substitution_rule": "record collar OD/set-screw clearance; tape is not accepted retention evidence", "warning": WARNING},
    ]
    traveler_actions = [
        ("FFA-T01", "CONFIGURATION", "Record commit, ZIP/STL hashes, printer, slicer, material lot and operator before slicing", "all identities recorded; 100% scale; no G-code accepted from this package"),
        ("FFA-T02", "CALIBRATION", "Print the clearance coupon before mechanism parts", "actual 4 mm rod and M3 candidate pass/fail recorded for every coupon hole"),
        ("FFA-T03", "SLICE", "Slice the eleven-part plate at 100% and inspect support, adhesion, collision and estimated time", "slicer screenshot/profile/time attached; no part collision or automatic scaling"),
        ("FFA-T04", "PRINT", "Print, separate and label all eleven parts", "eleven identified parts plus coupon; no missing or merged solid"),
        ("FFA-T05", "INSPECT", "Measure frame, rod, hole and moving-part characteristics in the inspection register", "all required measurements recorded with tool and uncertainty"),
        ("FFA-T06", "FRAME", "Dry-assemble the two plates, bridges and end blocks with recorded M3 candidates", "frame closes without cracking, forced drilling or unrecorded rework"),
        ("FFA-T07", "GUIDES", "Install measured smooth rods or printed proxies and temporary collars", "both rods retained; no sharp protrusion; no power source present"),
        ("FFA-T08", "MOVERS", "Install both fused finger/rack/pad proxies on both rods", "both parts translate by hand across the full candidate stroke without cracking"),
        ("FFA-T09", "PINION", "Insert the manual pinion shaft through the frame and engage both racks", "pinion retained by M3 axle; both racks engage; knob remains accessible"),
        ("FFA-T10", "KINEMATICS", "Move from closed to open and measure both jaw travels and pad gaps", "closed 8 ±1 mm; open 34 ±1 mm; jaw-travel mismatch ≤0.5 mm"),
        ("FFA-T11", "CYCLING", "Perform 50 slow hand-driven open/close cycles with no object", "no jam, crack, tooth skip, loose rod or retained pinch; observations recorded"),
        ("FFA-T12", "DISPOSITION", "Photograph four views and quarantine or accept only as a development fit article", "issue register complete; no inference to production, load, actuator or safety release"),
    ]
    traveler = [{"step": index, "traveler_id": tid, "stage": stage, "action": action, "completion_criterion": criterion, "performed_by": "UNASSIGNED", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING} for index, (tid, stage, action, criterion) in enumerate(traveler_actions, 1)]
    inspections = [
        ("FFA-I01", "coupon 4.35 mm guide hole", "4.35 mm nominal", "pin/gauge and caliper", "record fit with received 4 mm rod; no forcing or cracking"),
        ("FFA-I02", "printed or received guide diameter", "4.00 mm nominal", "micrometer at 6 locations", "record min/max; use only after coupon disposition"),
        ("FFA-I03", "assembled frame width", "80.0 mm", "caliper", "80.0 ±0.7 mm development screen"),
        ("FFA-I04", "assembled outer depth", "58.0 mm", "caliper", "58.0 ±0.7 mm development screen"),
        ("FFA-I05", "guide centre spacing", "18.0 mm", "caliper/gauge", "18.0 ±0.5 mm development screen"),
        ("FFA-I06", "closed pad gap", "8.0 mm", "caliper", "8.0 ±1.0 mm"),
        ("FFA-I07", "open pad gap", "34.0 mm", "caliper", "34.0 ±1.0 mm"),
        ("FFA-I08", "positive jaw travel", "13.0 mm", "caliper/scale", "13.0 ±0.7 mm"),
        ("FFA-I09", "negative jaw travel", "13.0 mm", "caliper/scale", "13.0 ±0.7 mm"),
        ("FFA-I10", "jaw travel mismatch", "0.0 mm", "derived from I08/I09", "≤0.5 mm"),
        ("FFA-I11", "manual backlash at pad", "CAD candidate only", "dial indicator or caliper method recorded", "record only; no production limit released"),
        ("FFA-I12", "50-cycle condition", "no visible damage or jam", "visual/manual", "no crack, jam, tooth skip, rod release or increasing drag"),
    ]
    inspection_rows = [{"inspection_id": iid, "characteristic": char, "source_nominal": nominal, "method": method, "development_acceptance": acceptance, "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING} for iid, char, nominal, method, acceptance in inspections]
    issues = [{"issue_id": f"FFA-ISS-{index:02d}", "area": area, "observation": "NONE", "severity": "UNASSIGNED", "disposition": "OPEN - NOT EXECUTED", "evidence": "NONE", "warning": WARNING} for index, area in enumerate(("print/surface", "frame fit", "guide fit", "finger sliding", "rack/pinion mesh", "travel symmetry", "manual cycling", "other"), 1)]
    holds = [
        {"hold_id": "FFA-H01", "unresolved": "printer, material, slicer profile, support and print time not selected", "evidence_required": "receiving-printer preflight and calibration coupon", "state": "OPEN", "warning": WARNING},
        {"hold_id": "FFA-H02", "unresolved": "exact M3, guide-rod and collar products not selected or received", "evidence_required": "received identity, dimensions and fit results", "state": "OPEN", "warning": WARNING},
        {"hold_id": "FFA-H03", "unresolved": "zero article parts or coupons built", "evidence_required": "completed traveler, photos and measurements", "state": "OPEN", "warning": WARNING},
        {"hold_id": "FFA-H04", "unresolved": "fit-article frame and fused moving parts intentionally differ from production G01", "evidence_required": "feed measured corrections into authoritative gripper CAD before any production release", "state": "OPEN", "warning": WARNING},
        {"hold_id": "FFA-H05", "unresolved": "actuator, horn, force, pinch, retention, load, endurance and failure behavior not tested", "evidence_required": "separate guarded design and physical validation after qualified review", "state": "OPEN", "warning": WARNING},
    ]
    return {"parts": part_rows, "hardware": hardware, "traveler": traveler, "inspections": inspection_rows, "issues": issues, "holds": holds, "plate": plate_rows}


def fit_screen_rows(closed: list[ArticlePart], opened: list[ArticlePart]) -> list[dict]:
    rows: list[dict] = []
    for state, parts in (("CLOSED", closed), ("OPEN", opened)):
        by_id = {part.part_id: part.shape for part in parts}
        pairs = [
            ("MOVING-PART-SEPARATION", "FFA_FINGER_RACK_POSITIVE", "FFA_FINGER_RACK_NEGATIVE", "ZERO INTERFERENCE; CLOSED CLEARANCE >=0.30 MM"),
            ("POSITIVE-GUIDE-FRONT", "FFA_FINGER_RACK_POSITIVE", "FFA_GUIDE_FRONT", "ZERO INTERFERENCE; RADIAL CLEARANCE 0.175 MM"),
            ("POSITIVE-GUIDE-REAR", "FFA_FINGER_RACK_POSITIVE", "FFA_GUIDE_REAR", "ZERO INTERFERENCE; RADIAL CLEARANCE 0.175 MM"),
            ("NEGATIVE-GUIDE-FRONT", "FFA_FINGER_RACK_NEGATIVE", "FFA_GUIDE_FRONT", "ZERO INTERFERENCE; RADIAL CLEARANCE 0.175 MM"),
            ("NEGATIVE-GUIDE-REAR", "FFA_FINGER_RACK_NEGATIVE", "FFA_GUIDE_REAR", "ZERO INTERFERENCE; RADIAL CLEARANCE 0.175 MM"),
            ("POSITIVE-PINION-MESH", "FFA_FINGER_RACK_POSITIVE", "FFA_MANUAL_PINION", "ZERO INTERFERENCE; SOLID DISTANCE <=0.10 MM"),
            ("NEGATIVE-PINION-MESH", "FFA_FINGER_RACK_NEGATIVE", "FFA_MANUAL_PINION", "ZERO INTERFERENCE; SOLID DISTANCE <=0.10 MM"),
            ("POSITIVE-OPEN-STOP", "FFA_FINGER_RACK_POSITIVE", "FFA_END_POSITIVE", "OPEN DISTANCE <=0.01 MM; CLOSED DISTANCE >=12 MM"),
            ("NEGATIVE-OPEN-STOP", "FFA_FINGER_RACK_NEGATIVE", "FFA_END_NEGATIVE", "OPEN DISTANCE <=0.01 MM; CLOSED DISTANCE >=12 MM"),
        ]
        for index, (name, left, right, criterion) in enumerate(pairs, 1):
            interference = by_id[left].intersect(by_id[right]).Volume()
            distance = by_id[left].distance(by_id[right])
            passed = interference <= 1e-6
            if "GUIDE" in name:
                passed = passed and distance >= 0.174
            elif "PINION" in name:
                passed = passed and distance <= 0.10
            elif "STOP" in name:
                passed = passed and (distance <= 0.01 if state == "OPEN" else distance >= 12.0)
            elif state == "CLOSED":
                passed = passed and distance >= 0.30
            rows.append({
                "screen_id": f"FFA-{state[0]}-{index:02d}", "state": state, "screen": name,
                "left_part": left, "right_part": right,
                "solid_interference_volume_mm3": f"{interference:.9f}", "minimum_solid_distance_mm": f"{distance:.9f}",
                "criterion": criterion, "result": "PASS - CAD GEOMETRY ONLY" if passed else "FAIL",
                "physical_credit": "NONE", "warning": WARNING,
            })
    if any(row["result"] == "FAIL" for row in rows):
        raise RuntimeError("fit-article CAD screen failed")
    return rows


def write_zip(files: list[Path]) -> Path:
    output = OUT / "HR30-G01-first-fit-article-p0.1.zip"
    with zipfile.ZipFile(output, "w") as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(path.relative_to(OUT).as_posix(), date_time=(2026, 8, 17, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return output


def render_page(status: dict, record_sets: dict[str, list[dict]]) -> str:
    steps = "".join(f'''<li><label><input type="checkbox" data-id="{row['traveler_id']}"><span><strong>{html.escape(row['stage'])}</strong> — {html.escape(row['action'])}</span></label></li>''' for row in record_sets["traveler"])
    hold_rows = "".join(f"<tr><td>{html.escape(row['hold_id'])}</td><td>{html.escape(row['unresolved'])}</td><td>{html.escape(row['evidence_required'])}</td></tr>" for row in record_sets["holds"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 G01 first fit article</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#071d36;--navy:#0b4f91;--sky:#77c9f2;--pale:#f1faff;--gold:#f2b91d;--ink:#142a40;--line:#94cce8;--red:#982520}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1240px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,43px);color:var(--navy)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card,.panel,.viewer{{background:#fff;border:2px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 3px 0 #c8e6f3}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--navy)}}.hold{{border-left:8px solid var(--red)}}model-viewer{{display:block;width:100%;height:520px;background:#dff3fd;border-radius:12px}}img{{display:block;max-width:100%;height:auto;margin:auto}}a{{color:#075b9b;font-weight:800}}ul.steps{{list-style:none;padding:0;display:grid;gap:10px}}.steps label{{display:flex;gap:12px;padding:14px;background:#fff;border:2px solid var(--line);border-radius:12px}}input{{width:22px;height:22px;flex:0 0 auto}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{font-size:16px;padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}th{{background:var(--deep);color:#fff}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{height:420px}}}}
</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Project Button · HR-30 whole-body derivative</p><h1>The first hand now assembles and moves by hand.</h1><p>This eleven-part, one-to-one development fixture converts the authoritative G01 rack-and-pinion geometry into a physically retainable manual article. It exists to replace guesses with measurements before actuator or production hardware is released.</p></header><main>
<section class="grid"><article class="card"><div class="metric">11</div><p>printable mechanism parts on one candidate 220 mm plate.</p></article><article class="card"><div class="metric">8–34 mm</div><p>closed-to-open pad-gap screen.</p></article><article class="card"><div class="metric">50</div><p>slow manual cycles required for the first disposition.</p></article><article class="card hold"><div class="metric">0 built</div><p>all physical and acceptance fields remain unexecuted.</p></article></section>
<section><h2>Inspect the mechanism before printing</h2><div class="grid"><article class="viewer"><h3>Closed state</h3><model-viewer src="HR30_G01_manual_fit_article_closed_candidate.glb" alt="Interactive closed HR-30 G01 manual fit article" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer></article><article class="viewer"><h3>Open state</h3><model-viewer src="HR30_G01_manual_fit_article_open_candidate.glb" alt="Interactive open HR-30 G01 manual fit article" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer></article></div></section>
<section><h2>Controlling dimensions and print plate</h2><div class="grid"><article class="panel"><img src="assembly-drawing.svg" alt="Dimensioned manual gripper fit article"></article><article class="panel"><img src="plate-layout.svg" alt="Candidate 220 millimetre print plate layout"></article></div></section>
<section><h2>Download the physical handoff</h2><div class="panel"><p><a href="HR30-G01-first-fit-article-p0.1.zip">Complete ZIP</a> · <a href="HR30_G01_manual_fit_article_plate_candidate.stl">combined eleven-part STL</a> · <a href="FFA_clearance_coupon.stl">clearance coupon</a> · <a href="fit-article-hardware-register.csv">hardware candidates</a> · <a href="fit-article-inspection-register.csv">inspection record</a> · <a href="fit-article-issue-register.csv">issue record</a>.</p><p>No G-code is included. The receiving printer must perform scale, support, adhesion, collision and time preflight.</p></div></section>
<section><h2>Manual build traveler</h2><p>Checkboxes are a browser convenience only; they are not engineering evidence. The CSV traveler must be completed and signed separately.</p><ul class="steps">{steps}</ul></section>
<section><h2>What remains open</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Unresolved</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div></section>
<section><div class="warning">This fixture deliberately widens the palm frame, lengthens the guide proxies, fuses rack/finger/pad proxies and uses a manual pinion. Measurements must feed back into the authoritative whole-body G01 design. Do not install a motor or infer structural, load, grasp, pinch-safety, motion, or energization approval.</div></section>
</main><footer>{html.escape(WARNING)}</footer><script>const key='hr30-g01-first-fit-article-p01';document.querySelectorAll('input[data-id]').forEach(box=>{{box.checked=localStorage.getItem(key+box.dataset.id)==='1';box.addEventListener('change',()=>localStorage.setItem(key+box.dataset.id,box.checked?'1':'0'))}});</script></body></html>'''


def replace_marked(text: str, start: str, end: str, block: str) -> str:
    if start in text:
        left = text.index(start)
        right = text.index(end, left) + len(end)
        return text[:left] + block + text[right:]
    return text.rstrip() + "\n\n" + block + "\n"


def integrate(status: dict) -> None:
    start = "<!-- HR30-FIRST-FIT-ARTICLE-P01-START -->"
    end = "<!-- HR30-FIRST-FIT-ARTICLE-P01-END -->"
    readme_path = WB / "README.md"
    block = f'''{start}
## First manual G01 fit article P0.1

The [interactive first-fit-article guide](first-fit-article-p0.1/index.html) packages one manually operable, unpowered G01 development fixture: eleven printable parts, open/closed STEP and GLB states, one 220 mm combined plate candidate, a clearance coupon, assembly hardware candidates, and a twelve-step physical traveler. Zero parts are built. The fixture is intentionally derived and may not receive production, actuator, structural, grasp, powered-test, motion, or energization credit.
{end}'''
    readme_path.write_text(replace_marked(readme_path.read_text(encoding="utf-8"), start, end, block), encoding="utf-8", newline="\n")

    page_path = WB / "index.html"
    section = f'''{start}<section id="first-fit-article"><h2>The first hand now has an actually assemblable manual fit article</h2><div class="grid"><article class="card pass"><div class="metric">11 parts</div><p>one retained frame, two guide proxies, two fused moving fingers and one manual pinion.</p></article><article class="card pass"><div class="metric">8–34 mm</div><p>measurable closed/open pad-gap screen.</p></article><article class="card hold"><div class="metric">0 built</div><p>printer preflight, hardware, measurements and physical cycling remain open.</p></article><article class="card hold"><h3>Derived fixture only</h3><p>measurements must return to the authoritative whole-body G01 design.</p></article></div><p><a href="first-fit-article-p0.1/index.html">Open the G01 first-fit-article guide</a>.</p></section>{end}'''
    page = page_path.read_text(encoding="utf-8")
    if start in page:
        page = replace_marked(page, start, end, section)
    else:
        anchor = "<!-- HR30-FIRST-BUILD-CART-P01-END -->"
        if anchor not in page:
            raise RuntimeError("first-build-cart anchor missing")
        page = page.replace(anchor, anchor + section, 1)
    page_path.write_text(page, encoding="utf-8", newline="\n")

    root_path = ROOT / "index.html"
    root_page = root_path.read_text(encoding="utf-8")
    link = '<li><a href="hr30/whole-body-p0.1/first-fit-article-p0.1/index.html">G01 first manual fit article</a></li>'
    if link not in root_page:
        anchor = '<li><a href="hr30/whole-body-p0.1/first-build-cart-p0.1/index.html">Interactive first physical-build cart</a></li>'
        if anchor not in root_page:
            raise RuntimeError("first-build-cart root link missing")
        root_page = root_page.replace(anchor, anchor + link, 1)
    root_path.write_text(root_page, encoding="utf-8", newline="\n")

    status_path = WB / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "first_fit_article_present": True,
        "first_fit_article_part_count": status["printable_part_count"],
        "first_fit_article_open_closed_states_present": True,
        "first_fit_article_physical_parts_built": 0,
        "first_fit_article_physical_tests_executed": 0,
        "first_fit_article_production_interchangeable": False,
        "first_fit_article_powered_test_authority": False,
        "first_fit_article_motion_authority": False,
        "first_fit_article_energization_authority": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8", newline="\n")


def manifest_release() -> None:
    manifest = OUT / "file-manifest.csv"
    if manifest.exists():
        manifest.unlink()
    write_csv(manifest, [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in sorted(OUT.rglob("*")) if path.is_file()])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def build() -> dict:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "stl").mkdir()

    closed = all_parts(0.0)
    opened = all_parts(FINGER_TRAVEL_EACH_MM)
    if len(closed) != 11 or {part.part_id for part in closed} != {part.part_id for part in opened}:
        raise RuntimeError("expected eleven stable fit-article parts")
    export_state(closed, "CLOSED")
    export_state(opened, "OPEN")

    bed_parts = []
    for part in closed:
        shape = bed_normalize(part)
        path = OUT / "stl" / f"{part.part_id}.stl"
        cq.exporters.export(shape, str(path), tolerance=0.10, angularTolerance=0.12)
        bed_parts.append((part, shape))
    coupon = bed_normalize(ArticlePart("FFA_CLEARANCE_COUPON", "guide and M3 clearance coupon", calibration_coupon(), (0.95, 0.72, 0.12, 1), "print before mechanism"))
    cq.exporters.export(coupon, str(OUT / "FFA_clearance_coupon.stl"), tolerance=0.08, angularTolerance=0.10)

    plate_rows, placed = pack(bed_parts)
    plate_shape = cq.Compound.makeCompound(placed)
    plate_path = OUT / "HR30_G01_manual_fit_article_plate_candidate.stl"
    cq.exporters.export(plate_shape, str(plate_path), tolerance=0.10, angularTolerance=0.12)
    plate_box = plate_shape.BoundingBox()
    if plate_box.xlen > BED_X_MM or plate_box.ylen > BED_Y_MM:
        raise RuntimeError("combined fit article exceeds 220 mm plate")

    record_sets = records(closed, opened, plate_rows)
    screens = fit_screen_rows(closed, opened)
    write_csv(OUT / "fit-article-part-register.csv", record_sets["parts"])
    write_csv(OUT / "fit-article-hardware-register.csv", record_sets["hardware"])
    write_csv(OUT / "fit-article-build-traveler.csv", record_sets["traveler"])
    write_csv(OUT / "fit-article-inspection-register.csv", record_sets["inspections"])
    write_csv(OUT / "fit-article-issue-register.csv", record_sets["issues"])
    write_csv(OUT / "open-holds.csv", record_sets["holds"])
    write_csv(OUT / "plate-placement-register.csv", record_sets["plate"])
    write_csv(OUT / "fit-screen-register.csv", screens)
    write_csv(OUT / "source-binding.csv", source_bindings())

    (OUT / "plate-layout.svg").write_text(layout_svg(plate_rows) + "\n", encoding="utf-8", newline="\n")
    (OUT / "assembly-drawing.svg").write_text(assembly_svg() + "\n", encoding="utf-8", newline="\n")

    closed_gap = pad_gap_mm(0.0)
    opened_gap = pad_gap_mm(FINGER_TRAVEL_EACH_MM)
    state_rows = [
        {"state": "CLOSED", "travel_each_jaw_mm": "0.000", "measured_cad_gap_mm": f"{closed_gap:.6f}", "target_gap_mm": "8.000", "physical_result": "NOT EXECUTED", "warning": WARNING},
        {"state": "OPEN", "travel_each_jaw_mm": "13.000", "measured_cad_gap_mm": f"{opened_gap:.6f}", "target_gap_mm": "34.000", "physical_result": "NOT EXECUTED", "warning": WARNING},
    ]
    write_csv(OUT / "kinematic-state-register.csv", state_rows)

    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "derived_from_authoritative_g01": True,
        "printable_part_count": len(closed),
        "combined_plate_present": True,
        "combined_plate_bbox_mm": [round(plate_box.xlen, 6), round(plate_box.ylen, 6), round(plate_box.zlen, 6)],
        "combined_plate_sha256": sha256(plate_path),
        "clearance_coupon_present": True,
        "open_closed_step_present": True,
        "open_closed_glb_present": True,
        "closed_cad_gap_mm": round(closed_gap, 6),
        "open_cad_gap_mm": round(opened_gap, 6),
        "manual_cycle_target": 50,
        "hardware_selection_count": len(record_sets["hardware"]),
        "traveler_step_count": len(record_sets["traveler"]),
        "inspection_count": len(record_sets["inspections"]),
        "cad_fit_screen_count": len(screens),
        "cad_fit_screen_pass_count": sum(row["result"].startswith("PASS") for row in screens),
        "open_hold_count": len(record_sets["holds"]),
        "built_part_count": 0,
        "physical_measurement_count": 0,
        "manual_cycle_count": 0,
        "production_interchangeable": False,
        "actuator_installation_permitted": False,
        "structural_credit": False,
        "grasp_credit": False,
        "fabrication_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "fit-article-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 G01 first manual fit article P0.1\n\n**{WARNING}**\n\n"
        "This package contains an eleven-part, one-to-one manual rack-and-pinion fit fixture derived from the authoritative whole-body G01 gripper. It includes open/closed editable CAD, individual and combined bed-ready STLs, a clearance coupon, candidate hardware, an inspection register, a twelve-step traveler and an interactive guide. The widened frame, longer rods, fused moving parts and manual shaft are fit-article features and are not production-interchangeable. Zero parts are built.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "first-fit-article-source.py")
    (OUT / "index.html").write_text(render_page(status, record_sets) + "\n", encoding="utf-8", newline="\n")

    zip_members = [path for path in OUT.rglob("*") if path.is_file() and path.name not in {"file-manifest.csv", "HR30-G01-first-fit-article-p0.1.zip"}]
    bundle = write_zip(zip_members)
    status["bundle_sha256"] = sha256(bundle)
    status["bundle_bytes"] = bundle.stat().st_size
    (OUT / "fit-article-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    integrate(status)
    manifest_release()
    return status


def main() -> int:
    print(json.dumps(build(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
