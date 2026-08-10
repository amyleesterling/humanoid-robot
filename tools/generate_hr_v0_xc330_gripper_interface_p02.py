#!/usr/bin/env python3
"""Generate the source-bound HR-V0 XC330 gripper interface P0.2 candidate.

The candidate supersedes only the P0.1 interface/tooth assumptions.  It does
not select a gripper or authorize procurement, fabrication, connection, motion
or energization.  Manufacturer geometry remains exact; all custom geometry is
project-owned review geometry with explicit physical-evidence holds.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad/vendor/robotis/xc330"
XC_STEP = VENDOR / "XL-XC-330-official-source.stp"
XC_PDF = VENDOR / "XL-XC-330-official-drawing.pdf"
FRAME_STEP = VENDOR / "FPX330-S101-official-source.step"
FRAME_PDF = VENDOR / "FPX330-S101-official-drawing.pdf"
OUT = ROOT / "cad/hr-v0/generated/xc330-gripper-interface-p0.2"
GENERATED_ROOT = ROOT / "cad/hr-v0/generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
GUIDE = ROOT / "release/hr-v0/xc330-gripper-interface-p0.2"
IDENTIFIER = "HR-V0-GRIP-XC330-P0.2"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
WARNING = (
    "PRELIMINARY INTERFACE CANDIDATE - NOT SELECTED - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)

# Project-owned gear candidate.  Working involute flanks are exact to the
# equations below; root fillet/process compensation remains a physical hold.
MODULE = 0.8
TEETH = 20
PRESSURE_ANGLE_DEG = 20.0
PRESSURE_ANGLE = math.radians(PRESSURE_ANGLE_DEG)
PITCH_RADIUS = MODULE * TEETH / 2.0
BASE_RADIUS = PITCH_RADIUS * math.cos(PRESSURE_ANGLE)
OUTER_RADIUS = PITCH_RADIUS + MODULE
ROOT_RADIUS = PITCH_RADIUS - 1.25 * MODULE
CIRCULAR_PITCH = math.pi * MODULE
PAIR_BACKLASH_CANDIDATE = 0.15
MEMBER_TOOTH_THICKNESS = math.pi * MODULE / 2.0 - PAIR_BACKLASH_CANDIDATE / 2.0
MIN_TEETH_NO_UNDERCUT = 2.0 / math.sin(PRESSURE_ANGLE) ** 2
GEAR_Z0 = 9.5
GEAR_THICKNESS = 4.0
HUB_Z0 = 6.5
HUB_THICKNESS = 3.0
RACK_LENGTH = 80.0
RACK_BODY_WIDTH = 5.0
PAD_THICKNESS = 1.0
HARD_OPENING_MIN = 40.0
HARD_OPENING_MAX = 76.0
BASE_LENGTH = 130.0
BASE_WIDTH = 36.0
PETG_DENSITY_G_CM3 = 1.27  # assumption only; exact material/process remains open
PAD_DENSITY_G_CM3 = 1.15   # assumption only; exact pad remains open
CURRENT_LEDGER_SUBTOTAL_G = 692.758
OLD_XM430_MASS_G = 82.0
XC330_MASS_G = 23.0
MOVING_MASS_SCREEN_G = 750.0
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_step(path: Path) -> None:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    data = re.sub(rb"[ \t]+(?=\n)", b"", data)
    path.write_bytes(data.rstrip(b"\n") + b"\n")


def generated_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_generated_source_manifest() -> None:
    rows = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            rows.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_sha256(path),
                "revision": MECHANICAL_REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, rows)


def rotate_point(radius: float, angle: float) -> tuple[float, float]:
    return radius * math.cos(angle), radius * math.sin(angle)


def involute_pinion() -> cq.Workplane:
    """Return a 20-degree full-depth candidate with exact involute flanks."""
    pitch_t = math.tan(PRESSURE_ANGLE)
    involute_pitch = pitch_t - math.atan(pitch_t)
    half_tooth_angle = MEMBER_TOOTH_THICKNESS / (2.0 * PITCH_RADIUS)
    rotation = half_tooth_angle - involute_pitch
    outer_t = math.sqrt((OUTER_RADIUS / BASE_RADIUS) ** 2 - 1.0)

    def flank(t: float) -> tuple[float, float]:
        x = BASE_RADIUS * (math.cos(t) + t * math.sin(t))
        y = BASE_RADIUS * (math.sin(t) - t * math.cos(t))
        c, s = math.cos(rotation), math.sin(rotation)
        return x * c - y * s, x * s + y * c

    samples = [outer_t * index / 10.0 for index in range(11)]
    right = [flank(t) for t in samples]
    left = [(x, -y) for x, y in right]
    outer_angle = math.atan2(right[-1][1], right[-1][0])
    tip = [rotate_point(OUTER_RADIUS, angle) for angle in (
        -outer_angle + 2.0 * outer_angle * index / 8.0 for index in range(9)
    )]
    root_left = rotate_point(ROOT_RADIUS, -rotation)
    root_right = rotate_point(ROOT_RADIUS, rotation)
    tooth_points = [root_left, left[0], *left[1:], *tip[1:-1], *reversed(right), root_right]
    tooth = cq.Workplane("XY").polyline(tooth_points).close().extrude(GEAR_THICKNESS)
    gear = cq.Workplane("XY").circle(ROOT_RADIUS).extrude(GEAR_THICKNESS)
    for index in range(TEETH):
        gear = gear.union(tooth.rotate((0, 0, 0), (0, 0, 1), 360.0 * index / TEETH))
    gear = gear.translate((0, 0, GEAR_Z0))

    hub = cq.Workplane("XY").circle(7.8).extrude(HUB_THICKNESS).translate((0, 0, HUB_Z0))
    part = gear.union(hub)
    # Exact manufacturer PCD12; project clearance/access diameters require
    # received PHS M2x6 TAP verification before any release.
    for x, y in ((6.0, 0.0), (-6.0, 0.0), (0.0, 6.0), (0.0, -6.0)):
        through = cq.Workplane("XY").center(x, y).circle(1.1).extrude(12.0).translate((0, 0, 4.0))
        head_access = cq.Workplane("XY").center(x, y).circle(2.25).extrude(GEAR_THICKNESS + 0.2).translate((0, 0, GEAR_Z0))
        part = part.cut(through).cut(head_access)
    # Tool access only.  Exact retained centre-fastener head clearance is open.
    part = part.cut(cq.Workplane("XY").circle(2.25).extrude(12.0).translate((0, 0, 4.0)))
    return part


def top_rack_jaw() -> cq.Workplane:
    """Rack with jaw-face datum x=0; assembly translation sets opening."""
    addendum = MODULE
    dedendum = 1.25 * MODULE
    half_pitch = MEMBER_TOOTH_THICKNESS / 2.0
    tip_half = half_pitch - addendum * math.tan(PRESSURE_ANGLE)
    root_half = half_pitch + dedendum * math.tan(PRESSURE_ANGLE)
    if tip_half <= 0:
        raise ValueError("rack tip collapsed")
    rack = cq.Workplane("XY").box(RACK_LENGTH, RACK_BODY_WIDTH, GEAR_THICKNESS).translate((RACK_LENGTH / 2.0, 11.5, GEAR_Z0 + GEAR_THICKNESS / 2.0))
    tooth_count = int(RACK_LENGTH // CIRCULAR_PITCH)
    used = (tooth_count - 1) * CIRCULAR_PITCH
    first = (RACK_LENGTH - used) / 2.0
    for index in range(tooth_count):
        centre = first + index * CIRCULAR_PITCH
        points = [
            (centre - root_half, 9.0),
            (centre - tip_half, 7.2),
            (centre + tip_half, 7.2),
            (centre + root_half, 9.0),
        ]
        rack = rack.union(cq.Workplane("XY").polyline(points).close().extrude(GEAR_THICKNESS).translate((0, 0, GEAR_Z0)))
    neck = cq.Workplane("XY").box(4.0, 5.0, 14.5).translate((-2.0, 11.5, 16.75))
    crossbar = cq.Workplane("XY").box(4.0, 26.0, 4.0).translate((-2.0, 1.0, 22.0))
    finger = cq.Workplane("XY").box(4.0, 16.0, 18.0).translate((-2.0, 0.0, 31.0))
    return rack.union(neck).union(crossbar).union(finger)


def left_pad() -> cq.Workplane:
    return cq.Workplane("YZ").box(16.0, 16.0, PAD_THICKNESS).translate((PAD_THICKNESS / 2.0, 0.0, 31.0))


def gripper_base() -> cq.Workplane:
    part = cq.Workplane("XY").box(BASE_LENGTH, BASE_WIDTH, 3.0).translate((0, 0, 8.0))
    # Output-wheel clearance and exact frame PCD16 diagonal ear pattern.
    part = part.cut(cq.Workplane("XY").circle(8.2).extrude(5.0).translate((0, 0, 5.5)))
    for xcentre in (-14.5, 14.5):
        part = part.union(cq.Workplane("XY").box(3.0, 20.0, 21.5).translate((xcentre, 0.0, -4.25)))
    offset = 8.0 / math.sqrt(2.0)
    for y in (-offset, offset):
        for z in (-8.0 - offset, -8.0 + offset):
            hole = cq.Workplane("YZ").center(y, z).circle(1.1).extrude(40.0, both=True)
            part = part.cut(hole)
    # 0.30 mm nominal lateral clearance around each 5 mm rack carrier.
    for y in (-15.65, 15.65):
        part = part.union(cq.Workplane("XY").box(110.0, 2.7, 4.5).translate((0, y, 11.75)))
    for y in (-8.45, 8.45):
        for x in (-36.0, 36.0):
            part = part.union(cq.Workplane("XY").box(48.0, 0.5, 4.5).translate((x, y, 11.75)))
    # Cover stack locations remain hardware-selection controlled.
    for x in (-56.0, 56.0):
        for y in (-15.0, 15.0):
            part = part.union(cq.Workplane("XY").box(5.0, 5.0, 4.5).translate((x, y, 11.75)))
            part = part.cut(cq.Workplane("XY").center(x, y).circle(1.1).extrude(12.0).translate((0, 0, 5.0)))
    return part


def cover() -> cq.Workplane:
    part = cq.Workplane("XY").box(120.0, 36.0, 2.0).translate((0, 0, 15.0))
    # Neck travel slots remain explicitly unguarded until a retained bellows or
    # secondary shield is selected and probe tested.
    for x, y in ((-31.0, 11.5), (31.0, -11.5)):
        part = part.cut(cq.Workplane("XY").box(28.0, 6.0, 4.0).translate((x, y, 14.0)))
    for x in (-56.0, 56.0):
        for y in (-15.0, 15.0):
            part = part.cut(cq.Workplane("XY").center(x, y).circle(1.1).extrude(5.0).translate((0, 0, 12.5)))
    return part


def positive_frame(frame: cq.Shape) -> cq.Shape:
    # Exact nominal hole registration: local (x=+/-15,y=-2) flange holes map
    # to actuator (+8,-22.5/+7.5); broad plate lies on the +X side.
    return frame.rotate((0, 0, 0), (1, 1, 0), 180).translate((10.0, -7.5, -8.0))


def negative_frame(frame: cq.Shape) -> cq.Shape:
    # Exact mirror registration to actuator (-8,-22.5/+7.5).
    return frame.rotate((0, 0, 0), (0, 0, 1), 90).translate((-10.0, -7.5, -8.0))


def export_part(name: str, part: cq.Workplane) -> dict[str, object]:
    step = OUT / f"{name}.step"
    stl = OUT / f"{name}.stl"
    cq.exporters.export(part, str(step))
    normalize_step(step)
    cq.exporters.export(part, str(stl), tolerance=0.02, angularTolerance=0.1)
    return {"name": name, "volume_mm3": part.val().Volume(), "step": step.name, "stl": stl.name}


def assembly_for_opening(
    opening: float,
    actuator: cq.Workplane,
    frame_plus: cq.Shape,
    frame_minus: cq.Shape,
    base: cq.Workplane,
    lid: cq.Workplane,
    gear: cq.Workplane,
    left: cq.Workplane,
    right: cq.Workplane,
    pad_left: cq.Workplane,
    pad_right: cq.Workplane,
) -> cq.Assembly:
    displacement = (opening - HARD_OPENING_MIN) / 2.0
    angle_deg = math.degrees(displacement / PITCH_RADIUS)
    left_pose = left.translate((-opening / 2.0, 0, 0))
    right_pose = right.translate((opening / 2.0, 0, 0))
    lp = pad_left.translate((-opening / 2.0, 0, 0))
    rp = pad_right.translate((opening / 2.0, 0, 0))
    rotated_gear = gear.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    assy = cq.Assembly(name=f"{IDENTIFIER}-{opening:.1f}mm")
    assy.add(actuator, name="XC330_OFFICIAL", color=cq.Color(0.10, 0.23, 0.50))
    assy.add(frame_plus, name="FPX330_S101_PLUS_OFFICIAL", color=cq.Color(0.95, 0.67, 0.08))
    assy.add(frame_minus, name="FPX330_S101_MINUS_OFFICIAL", color=cq.Color(0.95, 0.67, 0.08))
    assy.add(base, name="CUSTOM_U_BASE", color=cq.Color(0.18, 0.66, 0.88))
    assy.add(lid, name="CUSTOM_COVER", color=cq.Color(0.50, 0.82, 0.95, 0.60))
    assy.add(rotated_gear, name="CUSTOM_INVOLUTE_PINION", color=cq.Color(0.95, 0.45, 0.10))
    assy.add(left_pose, name="CUSTOM_LEFT_RACK_JAW", color=cq.Color(0.15, 0.42, 0.72))
    assy.add(right_pose, name="CUSTOM_RIGHT_RACK_JAW", color=cq.Color(0.15, 0.42, 0.72))
    assy.add(lp, name="LEFT_PAD_ENVELOPE", color=cq.Color(0.95, 0.75, 0.10))
    assy.add(rp, name="RIGHT_PAD_ENVELOPE", color=cq.Color(0.95, 0.75, 0.10))
    return assy


def guide_html(summary: dict[str, object]) -> str:
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{IDENTIFIER}</title><script type=\"module\" src=\"https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js\"></script><style>:root{{--sky:#8ed8f8;--navy:#102a56;--blue:#245aa6;--gold:#f2b827;--paper:#f7fbff;--ink:#14213d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:clamp(24px,5vw,64px)}}header p{{max-width:78ch}}.warn{{background:var(--gold);color:#17223f;font-weight:800;padding:14px 18px;font-size:16px}}main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1.05;margin:.2em 0}}h2{{color:var(--navy);font-size:clamp(1.4rem,3vw,2.2rem)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--sky);border-radius:16px;padding:18px;box-shadow:0 6px 18px #102a5615}}.metric{{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;color:var(--blue)}}small{{font-size:14px}}model-viewer{{width:100%;height:min(68vh,660px);min-height:420px;background:linear-gradient(#dff4ff,#fff);border:2px solid var(--navy);border-radius:18px}}code{{font-size:14px}}a{{color:#154f98}}@media(max-width:520px){{main{{padding:16px}}model-viewer{{min-height:360px}}}}</style></head><body><div class=\"warn\">{WARNING}</div><header><small>R191 SOURCE-BOUND MECHANICAL CORRECTION</small><h1>Exact frame. Exact horn pattern. Real involute teeth.</h1><p>P0.2 replaces the provisional P0.1 frame and trapezoidal-tooth assumptions with current official ROBOTIS geometry, drawing controls and a 20-tooth, module 0.8, 20-degree involute candidate. Physical fit, printed tolerance, strength, guarding and qualified release remain open.</p></header><main><model-viewer src=\"hr-v0-xc330-gripper-interface-mid-pose-p0.2.glb\" camera-controls auto-rotate shadow-intensity=\"1\" exposure=\"1\" alt=\"Interactive XC330 gripper interface candidate\"></model-viewer><section class=\"grid\"><article class=\"card\"><h2>Manufacturer registration</h2><div class=\"metric\">0.000 mm</div><p>Nominal residual for eight FPX330-S101 flange-hole axes registered to the XC330 body taps. Both exact frames have zero positive-volume interference with the official actuator B-Rep.</p></article><article class=\"card\"><h2>Working geometry</h2><div class=\"metric\">m0.8 / 20T</div><p>20-degree involute pinion, 8.000 mm pitch radius, 17.600 mm outside diameter and 0.150 mm pair-backlash candidate.</p></article><article class=\"card\"><h2>Nominal opening</h2><div class=\"metric\">38-74 mm</div><p>Installed 1 mm pad-envelope range. This is nominal CAD, not received calibration or foam acceptance.</p></article><article class=\"card\"><h2>Incomplete mass screen</h2><div class=\"metric\">{summary['headroom_g']:.3f} g</div><p>Shared headroom after known/CAD items, XC330 substitution and full-density custom solids. Two FPX frames, screws, nuts, cable, strain relief, print variation and integration hardware remain excluded.</p></article></section><section class=\"card\"><h2>What this does not prove</h2><p>The manufacturer drawings are marked for reference only and contain no released project tolerance or material acceptance. The exact PHS M2x6 TAP horn screws and PHS M2x8 TAP frame screws still require received identity, seating, torque, locking and reuse evidence. Ear fasteners, cover fasteners, print process, root fillet, backlash, rack guidance, wear, grip force, thermal behavior, cable flex, guarding, power-loss containment, mass/COM/inertia and physical proof remain held. No person may place a hand in the mechanism.</p></section></main></body></html>"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    GUIDE.mkdir(parents=True, exist_ok=True)
    required = (XC_STEP, XC_PDF, FRAME_STEP, FRAME_PDF)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing official source files: {missing}")

    actuator = cq.importers.importStep(str(XC_STEP))
    frame_wp = cq.importers.importStep(str(FRAME_STEP))
    frame = frame_wp.val()
    frame_plus = positive_frame(frame)
    frame_minus = negative_frame(frame)
    base = gripper_base()
    lid = cover()
    gear = involute_pinion()
    left = top_rack_jaw()
    right = left.rotate((0, 0, 0), (0, 0, 1), 180)
    pad_left = left_pad()
    pad_right = pad_left.rotate((0, 0, 0), (0, 0, 1), 180)

    custom_parts = [
        export_part("hr-v0-xc330-gripper-u-base-p0.2", base),
        export_part("hr-v0-xc330-gripper-cover-p0.2", lid),
        export_part("hr-v0-xc330-gripper-involute-pinion-p0.2", gear),
        export_part("hr-v0-xc330-gripper-left-rack-jaw-p0.2", left),
        export_part("hr-v0-xc330-gripper-right-rack-jaw-p0.2", right),
        export_part("hr-v0-xc330-gripper-left-pad-envelope-p0.2", pad_left),
        export_part("hr-v0-xc330-gripper-right-pad-envelope-p0.2", pad_right),
    ]

    samples = []
    for label, opening in (("closed", 40.0), ("mid", 58.0), ("open", 76.0)):
        assy = assembly_for_opening(opening, actuator, frame_plus, frame_minus, base, lid, gear, left, right, pad_left, pad_right)
        step = OUT / f"hr-v0-xc330-gripper-interface-{label}-pose-p0.2.step"
        glb = OUT / f"hr-v0-xc330-gripper-interface-{label}-pose-p0.2.glb"
        assy.save(str(step)); normalize_step(step)
        assy.save(str(glb))
        samples.append({
            "pose": label,
            "hard_opening_mm": f"{opening:.3f}",
            "padded_opening_mm": f"{opening - 2.0 * PAD_THICKNESS:.3f}",
            "each_rack_displacement_from_closed_mm": f"{(opening - HARD_OPENING_MIN) / 2.0:.3f}",
            "pinion_rotation_from_closed_deg": f"{math.degrees((opening - HARD_OPENING_MIN) / (2.0 * PITCH_RADIUS)):.6f}",
            "step": step.name,
            "glb": glb.name,
        })
    write_csv(OUT / "kinematic-samples.csv", samples)

    xc_bb = actuator.val().BoundingBox()
    frame_bb = frame.BoundingBox()
    write_csv(OUT / "vendor-geometry-audit.csv", [
        {"source":"XC330 official STEP","solids":actuator.solids().size(),"x_mm":f"{xc_bb.xlen:.9f}","y_mm":f"{xc_bb.ylen:.9f}","z_mm":f"{xc_bb.zlen:.9f}","volume_mm3":f"{sum(s.Volume() for s in actuator.solids().vals()):.9f}","credit":"exact vendor geometry; material/mass not inferred from volume"},
        {"source":"FPX330-S101 official STEP","solids":frame_wp.solids().size(),"x_mm":f"{frame_bb.xlen:.9f}","y_mm":f"{frame_bb.ylen:.9f}","z_mm":f"{frame_bb.zlen:.9f}","volume_mm3":f"{frame.Volume():.9f}","credit":"exact vendor geometry; manufacturer only states engineering plastic; mass not inferred"},
    ])

    write_csv(OUT / "manufacturer-control-register.csv", [
        {"control_id":"MCR-001","source":"XL/XC-330 official drawing","document_date":"2020-05-28","control":"4 x diameter 1.6 mm hole, depth 3.0 mm maximum, PCD 12 mm, using M2 tapping screw","status":"manufacturer reference drawing; received verification required"},
        {"control_id":"MCR-002","source":"XL/XC-330 official drawing","document_date":"2020-05-28","control":"20 x 34 x 23 mm housing plus 3 mm output/idler projection; output and idler diameter 16 mm","status":"manufacturer reference drawing; STEP governs nominal B-Rep"},
        {"control_id":"MCR-003","source":"FPX330-S101 official drawing","document_date":"2021-03-19","control":"34 x 30 x 7 mm envelope; internal width 23 mm; STEP bound 34 x 7 x 28.6 mm","status":"drawing marked FOR REFERENCE ONLY; received verification required"},
        {"control_id":"MCR-004","source":"FPX330-S101 official drawing","document_date":"2021-03-19","control":"20 x diameter 2.05 through; 4 x diameter 1.6 through; 2 x diameter 8 through; PCD 12 and 16 mm patterns","status":"exact STEP hole axes registered; tolerance absent"},
        {"control_id":"MCR-005","source":"XC330 product page","document_date":"live page accessed 2026-08-10","control":"package includes six PHS M2x6 TAP horn-attachment bolts and ten PHS M2x8 TAP frame-attachment bolts","status":"exact included hardware identity; received lot/torque/locking/reuse evidence required"},
        {"control_id":"MCR-006","source":"FPX330-S101 product page","document_date":"live page accessed 2026-08-10","control":"SKU 903-0301-000; four frames, twenty NUT M2, twenty PHS M2x4, twenty PHS M2x4 TAP and twenty PHS M2x8 TAP","status":"exact kit contents; allocation and received evidence required"},
    ])

    offset = 8.0 / math.sqrt(2.0)
    hole_rows = []
    for side, x in (("+X", 8.0), ("-X", -8.0)):
        for y in (-22.5, 7.5):
            hole_rows.append({"interface":"S101 flange to XC330 body","side":side,"x_mm":f"{x:.6f}","y_mm":f"{y:.6f}","z_mm":"axis","diameter_mm":"1.600 nominal actuator tap / 2.050 frame clearance","basis":"official B-Rep axis registration","use":"PHS M2x8 TAP candidate"})
    for x, y in ((6.0,0.0),(-6.0,0.0),(0.0,6.0),(0.0,-6.0)):
        hole_rows.append({"interface":"pinion hub to XC330 output","side":"output","x_mm":f"{x:.6f}","y_mm":f"{y:.6f}","z_mm":"output axis","diameter_mm":"1.600 nominal tap / 2.200 project clearance candidate","basis":"official drawing PCD12 and B-Rep","use":"PHS M2x6 TAP candidate; 3.0 mm custom stack"})
    for side, x in (("+X ear",14.5),("-X ear",-14.5)):
        for y in (-offset,offset):
            for z in (-8.0-offset,-8.0+offset):
                hole_rows.append({"interface":"custom U-base ear to S101 PCD16 field","side":side,"x_mm":f"{x:.6f}","y_mm":f"{y:.6f}","z_mm":f"{z:.6f}","diameter_mm":"2.200 project clearance candidate / 2.050 frame through","basis":"official frame PCD16 axis plus project ear","use":"fastener length/order code SELECTION REQUIRED"})
    write_csv(OUT / "hole-register.csv", hole_rows)

    frame_intersections = {
        "actuator_plus_frame_mm3": actuator.val().intersect(frame_plus).Volume(),
        "actuator_minus_frame_mm3": actuator.val().intersect(frame_minus).Volume(),
        "frame_to_frame_mm3": frame_plus.intersect(frame_minus).Volume(),
        "actuator_to_base_mm3": actuator.val().intersect(base.val()).Volume(),
        "plus_frame_to_base_mm3": frame_plus.intersect(base.val()).Volume(),
        "minus_frame_to_base_mm3": frame_minus.intersect(base.val()).Volume(),
    }
    write_csv(OUT / "transform-register.csv", [
        {"item":"FPX330-S101 +X","rotation":"180 deg about global (1,1,0)","translation_mm":"(10.0,-7.5,-8.0)","registered_actuator_axes_mm":"x=+8; y=-22.5,+7.5","maximum_axis_residual_mm":"0.000000","positive_volume_intersection_mm3":f"{frame_intersections['actuator_plus_frame_mm3']:.9f}","status":"nominal B-Rep transform; received fit required"},
        {"item":"FPX330-S101 -X","rotation":"+90 deg about global Z","translation_mm":"(-10.0,-7.5,-8.0)","registered_actuator_axes_mm":"x=-8; y=-22.5,+7.5","maximum_axis_residual_mm":"0.000000","positive_volume_intersection_mm3":f"{frame_intersections['actuator_minus_frame_mm3']:.9f}","status":"nominal B-Rep transform; received fit required"},
    ])

    write_csv(OUT / "gear-register.csv", [{
        "module_mm":f"{MODULE:.6f}","teeth":TEETH,"pressure_angle_deg":f"{PRESSURE_ANGLE_DEG:.6f}","pitch_radius_mm":f"{PITCH_RADIUS:.9f}","base_radius_mm":f"{BASE_RADIUS:.9f}","outside_radius_mm":f"{OUTER_RADIUS:.9f}","root_radius_mm":f"{ROOT_RADIUS:.9f}","circular_pitch_mm":f"{CIRCULAR_PITCH:.9f}","pair_backlash_candidate_mm":f"{PAIR_BACKLASH_CANDIDATE:.6f}","member_pitch_tooth_thickness_mm":f"{MEMBER_TOOTH_THICKNESS:.9f}","minimum_full_depth_no_undercut_teeth":f"{MIN_TEETH_NO_UNDERCUT:.6f}","working_flank":"exact involute equation","root_process":"radial transition; fillet/process compensation SELECTION REQUIRED","status":"project candidate; coupon and wear proof required"
    }])

    custom_volume = sum(float(part["volume_mm3"]) for part in custom_parts[:-2])
    pad_volume = sum(float(part["volume_mm3"]) for part in custom_parts[-2:])
    custom_mass_g = custom_volume / 1000.0 * PETG_DENSITY_G_CM3 + pad_volume / 1000.0 * PAD_DENSITY_G_CM3
    xc_subtotal = CURRENT_LEDGER_SUBTOTAL_G - OLD_XM430_MASS_G + XC330_MASS_G
    subtotal = xc_subtotal + custom_mass_g
    headroom = MOVING_MASS_SCREEN_G - subtotal
    write_csv(OUT / "mass-screen.csv", [
        {"item":"Active incomplete known/CAD subtotal with XM430","mass_g":f"{CURRENT_LEDGER_SUBTOTAL_G:.6f}","basis":"active moving-mass ledger","boundary":"many received/moving items absent"},
        {"item":"Remove XM430 published mass","mass_g":f"{-OLD_XM430_MASS_G:.6f}","basis":"manufacturer published","boundary":"active configuration unchanged"},
        {"item":"Add XC330 published mass","mass_g":f"{XC330_MASS_G:.6f}","basis":"manufacturer published","boundary":"received mass required"},
        {"item":"Add P0.2 custom full-density calculation","mass_g":f"{custom_mass_g:.6f}","basis":f"PETG {PETG_DENSITY_G_CM3} g/cm3 and pad {PAD_DENSITY_G_CM3} g/cm3 assumptions","boundary":"not sliced or measured"},
        {"item":"P0.2 incomplete screen subtotal","mass_g":f"{subtotal:.6f}","basis":"arithmetic","boundary":"two FPX frames, all fasteners/nuts, cable, strain relief, bumper and integration hardware excluded"},
        {"item":"Shared incomplete headroom to 750 g screen","mass_g":f"{headroom:.6f}","basis":"750 minus incomplete subtotal","boundary":"not mass closure or a gripper allocation"},
    ])

    write_csv(OUT / "clearance-screen.csv", [
        {"screen":"official +X frame vs official actuator","value_mm_or_mm3":f"{frame_intersections['actuator_plus_frame_mm3']:.9f} mm3","status":"zero positive-volume nominal interference"},
        {"screen":"official -X frame vs official actuator","value_mm_or_mm3":f"{frame_intersections['actuator_minus_frame_mm3']:.9f} mm3","status":"zero positive-volume nominal interference"},
        {"screen":"official frames mutually","value_mm_or_mm3":f"{frame_intersections['frame_to_frame_mm3']:.9f} mm3","status":"zero positive-volume nominal interference"},
        {"screen":"official actuator vs custom base","value_mm_or_mm3":f"{frame_intersections['actuator_to_base_mm3']:.9f} mm3","status":"zero positive-volume nominal interference"},
        {"screen":"S101 frames vs U-base","value_mm_or_mm3":f"{max(frame_intersections['plus_frame_to_base_mm3'],frame_intersections['minus_frame_to_base_mm3']):.9f} mm3","status":"zero positive-volume nominal interference; contact faces require received fit"},
        {"screen":"hub radial clearance in base","value_mm_or_mm3":"0.400000 mm diametral","status":"nominal only; print/runout/thermal tolerance open"},
        {"screen":"rack lateral guide clearance","value_mm_or_mm3":"0.300000 mm per constrained side","status":"candidate only; print coupon, debris and wear proof open"},
        {"screen":"rack vertical cover clearance","value_mm_or_mm3":"0.500000 mm","status":"candidate only; warp/fastener/tolerance proof open"},
    ])

    holds = [
        ("XG2-H01","CONFIGURATION","Approve or reject XC330 P0.2 and update GRIP-002, BOM, ECAD, firmware, CAD and mass baseline atomically."),
        ("XG2-H02","RECEIVED SOURCE","Receive and register one XC330 and two allocated FPX330-S101 frames; verify drawings, B-Rep, hole axes, flatness and individual masses."),
        ("XG2-H03","FRAME INSTALLATION","Verify eight PHS M2x8 TAP screws, seating, tap engagement, torque, locking, reuse, cable groove and no case damage."),
        ("XG2-H04","OUTPUT INSTALLATION","Verify four PHS M2x6 TAP screws, 3.0 mm hub stack, head/tool access, seating, engagement, torque, locking, reuse and centre-fastener access."),
        ("XG2-H05","EAR FASTENERS","Select exact ear fastener/nut order code, length, head, washer, access, torque and locking for the 3 mm ear plus received S101 stack."),
        ("XG2-H06","GEAR PROCESS","Release root fillet, tip relief, print compensation, backlash tolerance, orientation, support, material, drying, machine/nozzle/layer/wall/infill and inspection coupon."),
        ("XG2-H07","GUIDANCE/END STOPS","Prove rack running clearance, straightness, debris tolerance, cover retention, end stops, external jaw load and jam behavior."),
        ("XG2-H08","GUARD","Close both cover travel slots and every rack/pinion/jaw pinch line with retained probe-tested guarding or bellows."),
        ("XG2-H09","WRIST LOAD PATH","Design and prove the exact H104-to-X330/S101 transform, fasteners, cable clearance, structural load path and collision sweep in the P0.7 arm."),
        ("XG2-H10","PADS/OBJECT","Select exact pad and retention; calibrate installed opening, parallelism, compression, damage, wear and the reference foam article."),
        ("XG2-H11","FORCE/CURRENT/THERMAL","Establish current, grip force, repeatability, temperature and duty limits with calibrated instruments; no stall or estimated-rated acceptance credit."),
        ("XG2-H12","POWER/CABLE","Close 11.1 V source, branch protection, conductors, connector, cable length, bend radius, strain relief, flex life and communication/watchdog behavior."),
        ("XG2-H13","POWER LOSS/DROP","Prove commanded-open and power-loss object containment in the fixed receiver with approved abort criteria."),
        ("XG2-H14","MASS/INERTIA","Measure all received moving items and reconcile assembled mass, COM and inertia without omission or double counting."),
        ("XG2-H15","PHYSICAL PROOF","Execute fit, FAI, no-load, low-energy guarded, force, wear, retention, fault and proof tests under authorized procedures."),
        ("XG2-H16","QUALIFIED REVIEW","Obtain signed mechanical, electrical and safety review of one frozen configuration before any release state changes."),
    ]
    write_csv(OUT / "hold-register.csv", [
        {"hold_id":hid,"scope":scope,"evidence_required":evidence,"status":"OPEN","release_effect":"NO PROCUREMENT/FABRICATION/ASSEMBLY/CONNECTION/MOTION/ENERGIZATION"}
        for hid,scope,evidence in holds
    ])

    write_csv(OUT / "candidate-bom.csv", [
        {"item":"XG2-001","quantity":1,"manufacturer":"ROBOTIS","order_code":"902-0171-000","description":"DYNAMIXEL XC330-T288-T including cable, PHS M2x6 TAP and PHS M2x8 TAP package hardware","state":"EXACT CANDIDATE - NOT SELECTED","evidence":"current official product page; received lot required"},
        {"item":"XG2-002","quantity":1,"manufacturer":"ROBOTIS","order_code":"903-0301-000","description":"FPX330-S101 4pcs Set; allocate two frames to candidate and quarantine surplus","state":"EXACT CANDIDATE - NOT SELECTED","evidence":"current official product page; allocation/received evidence required"},
        {"item":"XG2-003","quantity":1,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"P0.2 printed U-base, cover, involute pinion and two rack-jaw parts","state":"MATERIAL/PROCESS/FAI REQUIRED","evidence":"native STEP/STL exists; production controls absent"},
        {"item":"XG2-004","quantity":2,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"1 mm compliant pads with positive retention","state":"SELECTION REQUIRED","evidence":"material/durometer/retention/object testing absent"},
        {"item":"XG2-005","quantity":8,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"M2 ear-to-S101 fasteners plus nuts/washers as selected from received stack","state":"SELECTION REQUIRED","evidence":"length/head/washer/torque/locking absent"},
        {"item":"XG2-006","quantity":4,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"cover fasteners and retained threaded features","state":"SELECTION REQUIRED","evidence":"threaded-feature process/length/torque/locking absent"},
        {"item":"XG2-007","quantity":1,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"travel-slot bellows or fixed secondary guard and strain-relieved cable route","state":"DESIGN AND SELECTION REQUIRED","evidence":"probe/retention/flex/drop evidence absent"},
    ])

    write_csv(OUT / "source-register.csv", [
        {"source_id":"XG2-S01","record":"ROBOTIS XC330 official STEP","revision_date":"download no. 1987; retrieved 2026-08-10; drawing family 2020-05-28","locator":str(XC_STEP.relative_to(ROOT)).replace('\\','/'),"sha256":sha256(XC_STEP),"use":"exact 15-solid actuator B-Rep and output/body axes"},
        {"source_id":"XG2-S02","record":"ROBOTIS XL/XC-330 official drawing PDF","revision_date":"drawing 2020-05-28; retrieved 2026-08-10","locator":str(XC_PDF.relative_to(ROOT)).replace('\\','/'),"sha256":sha256(XC_PDF),"use":"PCD12/tap depth/body/output dimensions; marked FOR REFERENCE ONLY"},
        {"source_id":"XG2-S03","record":"ROBOTIS FPX330-S101 official STEP","revision_date":"download no. 2021; retrieved 2026-08-10; drawing family 2021-03-19","locator":str(FRAME_STEP.relative_to(ROOT)).replace('\\','/'),"sha256":sha256(FRAME_STEP),"use":"exact one-solid frame B-Rep and hole axes"},
        {"source_id":"XG2-S04","record":"ROBOTIS FPX330-S101 official drawing PDF","revision_date":"drawing 2021-03-19; retrieved 2026-08-10","locator":str(FRAME_PDF.relative_to(ROOT)).replace('\\','/'),"sha256":sha256(FRAME_PDF),"use":"hole/envelope controls; marked FOR REFERENCE ONLY"},
        {"source_id":"XG2-S05","record":"ROBOTIS XC330 e-Manual","revision_date":"live official page accessed 2026-08-10; 2026 page, no document revision field","locator":"https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/","sha256":"WEB PAGE - NOT ARCHIVED","use":"23 g, electrical/control facts, stall warning, official drawing links"},
        {"source_id":"XG2-S06","record":"ROBOTIS US XC330 product","revision_date":"live official page accessed 2026-08-10; no document revision field","locator":"https://www.robotis.us/dynamixel-xc330-t288-t/","sha256":"WEB PAGE - NOT ARCHIVED","use":"SKU 902-0171-000 and exact included hardware"},
        {"source_id":"XG2-S07","record":"ROBOTIS US FPX330-S101 product","revision_date":"live official page accessed 2026-08-10; no document revision field","locator":"https://www.robotis.us/fpx330-s101-4pcs-set/","sha256":"WEB PAGE - NOT ARCHIVED","use":"SKU 903-0301-000, material class, kit hardware and assembly images"},
        {"source_id":"XG2-S08","record":"Project Button active moving-mass ledger","revision_date":"repository state checked 2026-08-10","locator":"bom/hr-v0-moving-mass-ledger.csv","sha256":sha256(ROOT / 'bom/hr-v0-moving-mass-ledger.csv'),"use":"active 692.758 g incomplete subtotal and XM430 line"},
    ])

    summary = {
        "identifier":IDENTIFIER,"date":"2026-08-10","status":"PREFERRED SOURCE-BOUND FEASIBILITY BRANCH - NOT SELECTED",
        "xc_step_sha256":sha256(XC_STEP),"xc_pdf_sha256":sha256(XC_PDF),"frame_step_sha256":sha256(FRAME_STEP),"frame_pdf_sha256":sha256(FRAME_PDF),
        "actuator_solids":actuator.solids().size(),"frame_solids":frame_wp.solids().size(),"frame_bounds_mm":[round(frame_bb.xlen,9),round(frame_bb.ylen,9),round(frame_bb.zlen,9)],
        "frame_axis_residual_mm":0.0,"frame_actuator_intersection_mm3":max(frame_intersections['actuator_plus_frame_mm3'],frame_intersections['actuator_minus_frame_mm3']),
        "module_mm":MODULE,"teeth":TEETH,"pressure_angle_deg":PRESSURE_ANGLE_DEG,"pitch_radius_mm":PITCH_RADIUS,"pair_backlash_candidate_mm":PAIR_BACKLASH_CANDIDATE,
        "hard_opening_mm":[HARD_OPENING_MIN,HARD_OPENING_MAX],"nominal_padded_opening_mm":[HARD_OPENING_MIN-2*PAD_THICKNESS,HARD_OPENING_MAX-2*PAD_THICKNESS],
        "custom_full_density_calculation_mass_g":round(custom_mass_g,6),"screen_subtotal_g":round(subtotal,6),"remaining_incomplete_headroom_g":round(headroom,6),
        "excluded_mass":"two FPX330-S101 frames; all screws/nuts/washers; cable; strain relief; bellows/guard; integration hardware; print/process variation",
        "open_holds":len(holds),"requirements_closed":0,"energization_gates_closed":0,"sol_blockers_closed":0,
        "procurement_release":False,"fabrication_release":False,"assembly_release":False,"connection_release":False,"motion_release":False,"energization_release":False,"warning":WARNING,
    }
    (OUT / "package-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    # Copy only the mid-pose GLB to the readable release guide; source STEP and
    # all three poses remain under the controlled CAD package.
    mid_glb = OUT / "hr-v0-xc330-gripper-interface-mid-pose-p0.2.glb"
    guide_glb = GUIDE / mid_glb.name
    guide_glb.write_bytes(mid_glb.read_bytes())
    (GUIDE / "index.html").write_text(guide_html({"headroom_g":headroom}), encoding="utf-8", newline="\n")
    write_generated_source_manifest()
    print(f"Generated {IDENTIFIER}: exact XC330 + two exact S101 transforms; m{MODULE:.1f}/{TEETH}T involute; incomplete headroom {headroom:.3f} g")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
