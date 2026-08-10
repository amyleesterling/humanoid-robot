#!/usr/bin/env python3
"""Generate the source-controlled HR-V0 XC330 gripper feasibility branch.

This package is a design study, not fabrication authority.  It uses exact
manufacturer XC330 STEP geometry, independently generated parametric mechanism
solids, transparent calculations, and fail-closed interface holds.
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
SOURCE_STEP = VENDOR / "XL-XC-330-official-source.stp"
OUT = ROOT / "cad/hr-v0/generated/xc330-gripper-feasibility-p0.1"
GENERATED_ROOT = ROOT / "cad/hr-v0/generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
GUIDE = ROOT / "release/hr-v0/xc330-gripper-feasibility-p0.1"
IDENTIFIER = "HR-V0-GRIP-XC330-P0.1"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
WARNING = (
    "PRELIMINARY FEASIBILITY BRANCH - NOT SELECTED - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)

# All dimensions are millimetres unless stated otherwise.
MODULE = 0.5
TEETH = 32
PITCH_RADIUS = MODULE * TEETH / 2.0
PINION_OUTER_RADIUS = PITCH_RADIUS + MODULE
PINION_ROOT_RADIUS = PITCH_RADIUS - 1.25 * MODULE
RACK_LENGTH = 70.0
RACK_BODY_WIDTH = 5.0
RACK_THICKNESS = 3.0
RACK_PITCH = math.pi * MODULE
BASE_LENGTH = 130.0
BASE_WIDTH = 36.0
BASE_THICKNESS = 3.0
PAD_THICKNESS = 1.0
HARD_OPENING_MIN = 40.0
HARD_OPENING_MAX = 76.0
XC330_MASS_G = 23.0
OLD_XM430_MASS_G = 82.0
CURRENT_LEDGER_SUBTOTAL_G = 692.758
MOVING_MASS_SCREEN_G = 750.0
PETG_DENSITY_G_CM3 = 1.27  # explicit calculation assumption; filament selection remains open
PAD_DENSITY_G_CM3 = 1.15   # explicit calculation assumption; pad selection remains open
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


def normalize_step(path: Path) -> None:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    data = re.sub(rb"[ \t]+(?=\n)", b"", data)
    path.write_bytes(data.rstrip(b"\n") + b"\n")


def cut_holes(part: cq.Workplane, points: list[tuple[float, float]], diameter: float) -> cq.Workplane:
    return part.faces(">Z").workplane().pushPoints(points).hole(diameter)


def base() -> cq.Workplane:
    part = cq.Workplane("XY").box(BASE_LENGTH, BASE_WIDTH, BASE_THICKNESS).translate((0, 0, 8.0))
    part = part.cut(cq.Workplane("XY").circle(10.2).extrude(8.0).translate((0, 0, 4.5)))
    points = [(x, y) for x in (-56.0, 56.0) for y in (-13.0, 13.0)]
    return cut_holes(part, points, 3.4)


def cover() -> cq.Workplane:
    part = cq.Workplane("XY").box(BASE_LENGTH, BASE_WIDTH, 2.0).translate((0, 0, 14.4))
    # Two narrow jaw-carrier travel slots.  These are intentionally recorded as
    # exposed pinch-line holds until a validated bellows or secondary shield exists.
    for y in (-8.0, 8.0):
        slot = cq.Workplane("XY").box(88.0, 6.2, 5.0).translate((0, y, 12.0))
        part = part.cut(slot)
    points = [(x, y) for x in (-56.0, 56.0) for y in (-13.0, 13.0)]
    return cut_holes(part, points, 3.4)


def pinion() -> cq.Workplane:
    gear = cq.Workplane("XY").circle(PINION_ROOT_RADIUS).extrude(RACK_THICKNESS).translate((0, 0, 10.0))
    half_pitch_angle = math.pi / TEETH
    for index in range(TEETH):
        center = 2.0 * math.pi * index / TEETH
        points = []
        for radius, offset in (
            (PINION_ROOT_RADIUS, -0.72 * half_pitch_angle),
            (PINION_OUTER_RADIUS, -0.32 * half_pitch_angle),
            (PINION_OUTER_RADIUS, 0.32 * half_pitch_angle),
            (PINION_ROOT_RADIUS, 0.72 * half_pitch_angle),
        ):
            angle = center + offset
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        tooth = cq.Workplane("XY").polyline(points).close().extrude(RACK_THICKNESS).translate((0, 0, 10.0))
        gear = gear.union(tooth)

    # Four radial slots are derived from the exact official STEP output-wheel
    # geometry.  They remain a fit-study interface, not a released tolerance.
    for angle in (0.0, 90.0, 180.0, 270.0):
        x = 6.0 * math.cos(math.radians(angle))
        y = 6.0 * math.sin(math.radians(angle))
        cutter = (
            cq.Workplane("XY")
            .center(x, y)
            .slot2D(2.62, 1.60, angle)
            .extrude(6.0)
            .translate((0, 0, 8.5))
        )
        gear = gear.cut(cutter)
    hub = cq.Workplane("XY").circle(5.0).extrude(3.5).translate((0, 0, 6.5))
    return gear.union(hub)


def rack(teeth_face: int) -> cq.Workplane:
    """Return one rack at the origin; teeth_face is +1 or -1 along Y."""
    body = cq.Workplane("XY").box(RACK_LENGTH, RACK_BODY_WIDTH, RACK_THICKNESS).translate((0, 0, 10.0))
    count = int(RACK_LENGTH / RACK_PITCH) - 1
    edge = teeth_face * RACK_BODY_WIDTH / 2.0
    for index in range(count):
        x = -RACK_LENGTH / 2.0 + RACK_PITCH * (index + 1)
        near = edge
        far = edge + teeth_face * 1.25 * MODULE
        points = [
            (x - 0.38 * RACK_PITCH, near),
            (x - 0.18 * RACK_PITCH, far),
            (x + 0.18 * RACK_PITCH, far),
            (x + 0.38 * RACK_PITCH, near),
        ]
        body = body.union(cq.Workplane("XY").polyline(points).close().extrude(RACK_THICKNESS).translate((0, 0, 10.0)))
    return body


def jaw(side: int, opening: float) -> tuple[cq.Workplane, cq.Workplane]:
    """Return jaw body and compliant-pad envelope for side -1 or +1."""
    inner = side * opening / 2.0
    body_center_x = inner + side * 3.0
    body = cq.Workplane("XY").box(6.0, 20.0, 25.0).translate((body_center_x, 0, 20.5))
    foot = cq.Workplane("XY").box(10.0, 18.0, 3.0).translate((body_center_x, side * 8.0, 11.5))
    body = body.union(foot)
    pad_center_x = inner - side * PAD_THICKNESS / 2.0
    pad = cq.Workplane("XY").box(PAD_THICKNESS, 18.0, 22.0).translate((pad_center_x, 0, 20.5))
    return body, pad


def pose(opening: float) -> dict[str, cq.Workplane]:
    travel = (opening - HARD_OPENING_MIN) / 2.0
    left_center = 9.0 - travel
    right_center = -9.0 + travel
    left_rack = rack(-1).translate((left_center, 8.0, 0))
    right_rack = rack(+1).translate((right_center, -8.0, 0))
    left_jaw, left_pad = jaw(-1, opening)
    right_jaw, right_pad = jaw(+1, opening)
    return {
        "left_rack": left_rack,
        "right_rack": right_rack,
        "left_jaw": left_jaw,
        "right_jaw": right_jaw,
        "left_pad": left_pad,
        "right_pad": right_pad,
    }


def volume(parts: list[cq.Workplane]) -> float:
    return sum(sum(s.Volume() for s in part.solids().vals()) for part in parts)


def save_part(name: str, part: cq.Workplane) -> None:
    step = OUT / f"{name}.step"
    cq.exporters.export(part, str(step))
    normalize_step(step)
    cq.exporters.export(part, str(OUT / f"{name}.stl"), tolerance=0.02, angularTolerance=0.1)


def guide_html(metrics: dict[str, float]) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--navy:#082f58;--blue:#11689f;--sky:#d8f2ff;--gold:#f2b928;--paper:#f7fcff;--danger:#7b2020}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),white);border-bottom:8px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4.5rem);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(1.55rem,3vw,2.4rem)}}main{{max-width:1250px;margin:auto;padding:clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid var(--danger);background:#fff1d1;color:var(--danger);font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:1rem;margin:1.5rem 0}}article{{background:white;border:3px solid var(--blue);border-radius:1rem;padding:1rem}}.metric{{display:block;font-size:clamp(2rem,4vw,3.3rem);font-weight:850}}model-viewer{{display:block;width:100%;min-height:480px;height:min(68vh,680px);background:var(--sky);border:3px solid var(--blue);border-radius:1rem}}.table-wrap{{overflow:auto;border:2px solid #8bb7d0;border-radius:.8rem}}table{{border-collapse:collapse;width:100%;min-width:820px}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #b9d2df}}th{{background:var(--navy);color:white}}code,.meta{{font-size:14px}}a{{color:#075d98}}footer{{background:var(--navy);color:white;padding:1.2rem}}@media(max-width:650px){{model-viewer{{min-height:360px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p class="meta">{IDENTIFIER} · R190 · 2026-08-10</p><h1>A lighter gripper branch that fits the object envelope on paper.</h1><p>Exact ROBOTIS actuator geometry plus independently generated rack-and-pinion parts. This closes a feasibility question, not the physical evidence chain.</p></header><main><model-viewer src="../../../cad/hr-v0/generated/xc330-gripper-feasibility-p0.1/hr-v0-xc330-gripper-mid-pose-p0.1.glb" camera-controls shadow-intensity="1" exposure="1" alt="Interactive three-dimensional view of the XC330 rack-and-pinion gripper feasibility assembly"></model-viewer><section class="grid"><article><span class="metric">23 g</span><p>manufacturer-published actuator mass</p></article><article><span class="metric">38–74 mm</span><p>nominal padded opening from a 40–76 mm hard-jaw range</p></article><article><span class="metric">{metrics['rotation_deg']:.1f}°</span><p>single-turn actuator travel for the full hard-jaw range</p></article><article><span class="metric">{metrics['custom_mass_g']:.1f} g</span><p>full-density printed-part calculation assumption, excluding frame, screws and cable</p></article></section><h2>Mass-screen effect</h2><p>Replacing the 82 g XM430 line with the 23 g XC330 reduces the incomplete known/CAD subtotal from 692.758 g to 633.758 g. Adding this branch's full-density custom parts gives {metrics['screen_subtotal_g']:.3f} g and leaves {metrics['headroom_g']:.3f} g for every still-unmeasured frame, screw, cable, strain relief, bumper and integration item. That is progress, but not closure.</p><h2>What is exact, and what is not</h2><div class="table-wrap"><table><thead><tr><th>Claim</th><th>Evidence</th><th>Release boundary</th></tr></thead><tbody><tr><td>XC330 geometry, mass, voltage and TTL interface</td><td>Official ROBOTIS STEP, product record and e-Manual</td><td>Received identity, frame fit, cable, current/thermal and protection evidence remain open.</td></tr><tr><td>32-tooth module-0.5 feasibility mechanism</td><td>Parametric source, STEP/STL, two pose assemblies and kinematic table</td><td>Tooth form, backlash, wear, tolerance, print material/process and proof remain open.</td></tr><tr><td>40–70 mm object envelope</td><td>Nominal 38–74 mm padded range contains the requirement</td><td>No compliance credit until received padded opening and uncertainty are measured.</td></tr><tr><td>Force screening</td><td>Ideal statics only: torque divided across two racks at an 8 mm pitch radius</td><td>Stall torque is not continuous torque. Grip force/current must be load-cell tested.</td></tr><tr><td>Guarding</td><td>Central cover and exposed-slot register</td><td>Travel slots and jaw sweep remain reachable pinch lines. A released guard is mandatory.</td></tr></tbody></table></div><h2>Decision</h2><p>This is the preferred lightweight <strong>feasibility branch</strong>, not the selected production gripper. It may replace the RM-X52/XM430 path only after an approved change, complete frame/interface CAD, exact hardware, tolerance and print records, received metrology, guarded force/drop/wear testing, mass closure, and qualified review.</p></main><footer>No ordering, printing, machining, assembly, connection, powered test, motion or energization is authorized by this page.</footer></body></html>'''


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    GUIDE.mkdir(parents=True, exist_ok=True)
    if not SOURCE_STEP.is_file() or not SOURCE_STEP.read_bytes().startswith(b"ISO-10303-21"):
        raise SystemExit("official XC330 STEP missing or invalid")

    fixed = [base(), cover(), pinion()]
    mid = pose((HARD_OPENING_MIN + HARD_OPENING_MAX) / 2.0)
    printable = fixed + [mid["left_rack"], mid["right_rack"], mid["left_jaw"], mid["right_jaw"]]
    pads = [mid["left_pad"], mid["right_pad"]]
    custom_volume_mm3 = volume(printable)
    pad_volume_mm3 = volume(pads)
    custom_mass_g = custom_volume_mm3 / 1000.0 * PETG_DENSITY_G_CM3 + pad_volume_mm3 / 1000.0 * PAD_DENSITY_G_CM3
    replaced_subtotal = CURRENT_LEDGER_SUBTOTAL_G - OLD_XM430_MASS_G + XC330_MASS_G
    screen_subtotal = replaced_subtotal + custom_mass_g
    headroom = MOVING_MASS_SCREEN_G - screen_subtotal
    rotation_rad = (HARD_OPENING_MAX - HARD_OPENING_MIN) / (2.0 * PITCH_RADIUS)
    rotation_deg = math.degrees(rotation_rad)
    padded_min = HARD_OPENING_MIN - 2.0 * PAD_THICKNESS
    padded_max = HARD_OPENING_MAX - 2.0 * PAD_THICKNESS
    metrics = {
        "custom_volume_mm3": custom_volume_mm3,
        "pad_volume_mm3": pad_volume_mm3,
        "custom_mass_g": custom_mass_g,
        "replaced_subtotal_g": replaced_subtotal,
        "screen_subtotal_g": screen_subtotal,
        "headroom_g": headroom,
        "rotation_rad": rotation_rad,
        "rotation_deg": rotation_deg,
        "padded_min_mm": padded_min,
        "padded_max_mm": padded_max,
    }

    named_parts = {
        "hr-v0-xc330-gripper-base-p0.1": fixed[0],
        "hr-v0-xc330-gripper-cover-p0.1": fixed[1],
        "hr-v0-xc330-gripper-pinion-p0.1": fixed[2],
        "hr-v0-xc330-gripper-rack-a-p0.1": rack(-1),
        "hr-v0-xc330-gripper-rack-b-p0.1": rack(+1),
        "hr-v0-xc330-gripper-left-jaw-p0.1": mid["left_jaw"],
        "hr-v0-xc330-gripper-right-jaw-p0.1": mid["right_jaw"],
        "hr-v0-xc330-gripper-left-pad-envelope-p0.1": mid["left_pad"],
        "hr-v0-xc330-gripper-right-pad-envelope-p0.1": mid["right_pad"],
    }
    for name, part in named_parts.items():
        save_part(name, part)

    servo = cq.importers.importStep(str(SOURCE_STEP))
    for label, opening in (("closed", HARD_OPENING_MIN), ("mid", 58.0), ("open", HARD_OPENING_MAX)):
        state = pose(opening)
        assembly = cq.Assembly(name=f"{IDENTIFIER}-{label}")
        assembly.add(servo, name="XC330_OFFICIAL_STEP", color=cq.Color(0.11, 0.28, 0.55))
        assembly.add(fixed[0], name="BASE", color=cq.Color(0.39, 0.73, 0.91))
        assembly.add(fixed[1], name="COVER", color=cq.Color(0.78, 0.92, 0.98))
        assembly.add(fixed[2], name="PINION", color=cq.Color(0.95, 0.66, 0.10))
        assembly.add(state["left_rack"], name="LEFT_RACK", color=cq.Color(0.18, 0.47, 0.72))
        assembly.add(state["right_rack"], name="RIGHT_RACK", color=cq.Color(0.18, 0.47, 0.72))
        assembly.add(state["left_jaw"], name="LEFT_JAW", color=cq.Color(0.95, 0.66, 0.10))
        assembly.add(state["right_jaw"], name="RIGHT_JAW", color=cq.Color(0.95, 0.66, 0.10))
        assembly.add(state["left_pad"], name="LEFT_PAD_ENVELOPE", color=cq.Color(0.16, 0.58, 0.45))
        assembly.add(state["right_pad"], name="RIGHT_PAD_ENVELOPE", color=cq.Color(0.16, 0.58, 0.45))
        step = OUT / f"hr-v0-xc330-gripper-{label}-pose-p0.1.step"
        glb = OUT / f"hr-v0-xc330-gripper-{label}-pose-p0.1.glb"
        assembly.save(str(step)); normalize_step(step)
        assembly.save(str(glb))

    samples = []
    for opening in (40.0, 46.0, 52.0, 58.0, 64.0, 70.0, 76.0):
        theta = (opening - HARD_OPENING_MIN) / (2.0 * PITCH_RADIUS)
        samples.append({
            "hard_jaw_opening_mm": f"{opening:.3f}",
            "nominal_padded_opening_mm": f"{opening - 2.0 * PAD_THICKNESS:.3f}",
            "each_rack_translation_mm": f"{(opening - HARD_OPENING_MIN) / 2.0:.3f}",
            "pinion_rotation_deg": f"{math.degrees(theta):.6f}",
            "claim_boundary": "KINEMATIC NOMINAL ONLY - BACKLASH/TOLERANCE/DEFLECTION/RECEIVED CALIBRATION OPEN",
        })
    write_csv(OUT / "kinematic-samples.csv", samples)

    estimated_rated_torque = 0.184
    stall_torque_11v1 = 0.92
    write_csv(OUT / "force-screen.csv", [
        {
            "case": "ROBOTIS product-page estimated rated torque disclosure",
            "torque_nm": f"{estimated_rated_torque:.3f}",
            "ideal_each_jaw_force_n": f"{estimated_rated_torque / (2.0 * PITCH_RADIUS / 1000.0):.3f}",
            "equation": "F=T/(2*r), r=0.008 m",
            "credit": "SCREEN ONLY - NOT A PROJECT RATING OR ACCEPTANCE VALUE",
        },
        {
            "case": "manufacturer momentary stall torque at 11.1 V",
            "torque_nm": f"{stall_torque_11v1:.3f}",
            "ideal_each_jaw_force_n": f"{stall_torque_11v1 / (2.0 * PITCH_RADIUS / 1000.0):.3f}",
            "equation": "F=T/(2*r), r=0.008 m",
            "credit": "NO CONTINUOUS OR REAL-WORLD FORCE CREDIT; DO NOT COMMAND STALL",
        },
    ])

    write_csv(OUT / "mass-screen.csv", [
        {"item":"Current incomplete known/CAD subtotal with XM430 line","mass_g":f"{CURRENT_LEDGER_SUBTOTAL_G:.3f}","basis":"active moving-mass ledger","boundary":"unresolved frames/hardware/cables absent"},
        {"item":"Remove XM430-W350-T manufacturer mass","mass_g":f"{-OLD_XM430_MASS_G:.3f}","basis":"manufacturer published","boundary":"received mass required"},
        {"item":"Add XC330-T288-T manufacturer mass","mass_g":f"{XC330_MASS_G:.3f}","basis":"manufacturer published","boundary":"received mass required"},
        {"item":"Add generated custom solids full-density assumption","mass_g":f"{custom_mass_g:.6f}","basis":f"PETG {PETG_DENSITY_G_CM3} g/cm3 and pad {PAD_DENSITY_G_CM3} g/cm3 calculation assumptions","boundary":"not a slicer result or measured mass; frame/screws/cable excluded"},
        {"item":"Feasibility screen subtotal","mass_g":f"{screen_subtotal:.6f}","basis":"arithmetic","boundary":"not mass closure"},
        {"item":"Remaining 750 g screen headroom","mass_g":f"{headroom:.6f}","basis":"750 minus feasibility subtotal","boundary":"shared by every unresolved moving item"},
    ])

    write_csv(OUT / "source-register.csv", [
        {"source_id":"XGS-001","record":"ROBOTIS XC330-T288-T e-Manual","revision_date":"live official page accessed 2026-08-10; page carries 2026 copyright, no document revision field","locator":"https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/","sha256":"WEB PAGE - NOT ARCHIVED","use":"23 g; dimensions; 6.5-12 V; recommended 11.1 V; TTL; torque/current; control-table and stall warning"},
        {"source_id":"XGS-002","record":"ROBOTIS US DYNAMIXEL XC330-T288-T product","revision_date":"live official page accessed 2026-08-10; no document revision field","locator":"https://www.robotis.us/dynamixel-xc330-t288-t/","sha256":"WEB PAGE - NOT ARCHIVED","use":"exact product/SKU 902-0171-000; package contents; 0.184 Nm estimated-rated disclosure; lead-time notice"},
        {"source_id":"XGS-003","record":"ROBOTIS official XL/XC330 STEP","revision_date":"official e-Manual download no. 1987; retrieved 2026-08-10; STEP header has no usable manufacturer revision","locator":"cad/vendor/robotis/xc330/XL-XC-330-official-source.stp","sha256":sha256(SOURCE_STEP),"use":"exact actuator geometry and four-slot output-wheel fit study"},
        {"source_id":"XGS-004","record":"ROBOTIS FPX330-S101 4pcs Set","revision_date":"live official product page accessed 2026-08-10; no document revision field","locator":"https://www.robotis.us/fpx330-s101-4pcs-set/","sha256":"WEB PAGE - NOT ARCHIVED","use":"exact compatible side-frame kit SKU 903-0301-000 and included hardware; frame geometry/mass not credited"},
        {"source_id":"XGS-005","record":"Project Button active moving-mass ledger","revision_date":"repository state checked 2026-08-10","locator":"bom/hr-v0-moving-mass-ledger.csv","sha256":sha256(ROOT / "bom/hr-v0-moving-mass-ledger.csv"),"use":"692.758 g incomplete subtotal and 82 g replaced actuator line"},
    ])

    holds = [
        ("XGH-001","CONFIGURATION","Approve or reject replacement of the current RM-X52/XM430 proposal and update GRIP-002/electrical/firmware/CAD together."),
        ("XGH-002","ACTUATOR/FRAME","Acquire and metrologically register received XC330-T288-T and FPX330-S101; control frame STEP/drawing, mass and exact fastener stack."),
        ("XGH-003","OUTPUT INTERFACE","Verify the four radial slots, screw head clearance, thread engagement, torque, locking, reuse and pinion seating on received parts."),
        ("XGH-004","TOOTH FORM","Complete involute/rack tooth engineering, backlash/tolerance stack, print orientation, process capability, lubrication policy and wear life."),
        ("XGH-005","GUIDANCE","Release rack guide geometry, running clearance, debris tolerance, end stops and retained behavior under external jaw loads."),
        ("XGH-006","MATERIAL/PRINT","Select exact filament/resin and supplier; release drying, machine, nozzle, layer, wall/infill, anneal/finish, coupon and lot evidence."),
        ("XGH-007","WRIST ADAPTER","Create and prove exact FR12-H104K-to-FPX330/base transform, fasteners, tolerance stack, cable clearance and structural load path."),
        ("XGH-008","GUARD","Eliminate access to both travel slots, pinion/rack mesh, jaw sweep and fixed/moving pinch lines with probe-tested retained guarding."),
        ("XGH-009","PADS/OBJECT","Select exact pad, adhesive/retention and reference foam; measure installed usable opening, parallelism, compression, damage and wear."),
        ("XGH-010","FORCE/CURRENT","Use a calibrated load cell to establish current, force, repeatability and thermal limits; stall figures receive zero acceptance credit."),
        ("XGH-011","POWER/CABLE","Recalculate branch protection/conductors/connectors/inrush/thermal and prove cable route, bend radius, strain relief and flex life."),
        ("XGH-012","POWER LOSS/DROP","Prove commanded-open, sudden power loss and object-drop containment into a fixed receiver with accepted abort criteria."),
        ("XGH-013","MASS/INERTIA","Measure every received moving item and assembled mass/COM/inertia; reconcile without omission or double counting."),
        ("XGH-014","PHYSICAL PROOF","Execute fit, no-load, guarded low-energy, force, wear, fastener-retention and fault tests under approved work instructions."),
        ("XGH-015","QUALIFIED REVIEW","Obtain signed mechanical, electrical and safety review of one frozen configuration before any release state changes."),
    ]
    write_csv(OUT / "hold-register.csv", [
        {"hold_id":hid,"scope":scope,"evidence_required":evidence,"status":"OPEN","release_effect":"NO PROCUREMENT/FABRICATION/CONNECTION/MOTION/ENERGIZATION"}
        for hid, scope, evidence in holds
    ])

    write_csv(OUT / "candidate-bom.csv", [
        {"item":"XGB-001","quantity":1,"manufacturer":"ROBOTIS","order_code":"902-0171-000","description":"DYNAMIXEL XC330-T288-T; package includes one 180 mm X3P cable and stated M2 fasteners","state":"EXACT FEASIBILITY CANDIDATE - NOT SELECTED","evidence":"official product page; current availability/received identity required"},
        {"item":"XGB-002","quantity":1,"manufacturer":"ROBOTIS","order_code":"903-0301-000","description":"FPX330-S101 4pcs Set","state":"EXACT INTERFACE CANDIDATE - NOT SELECTED","evidence":"official product page; exact allocated quantity, geometry and received mass required"},
        {"item":"XGB-003","quantity":1,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"printed base, cover, pinion, two racks and two jaws from controlled source","state":"PROCESS/MATERIAL/DFM/PROOF REQUIRED","evidence":"native STEP/STL exists; exact material/process and FAI absent"},
        {"item":"XGB-004","quantity":2,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"1.0 mm broad compliant pad plus positive retention","state":"SELECTION REQUIRED","evidence":"durometer, tear/compression, adhesive/retention and object tests absent"},
        {"item":"XGB-005","quantity":1,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"base/cover/wrist fasteners and locking features","state":"SELECTION REQUIRED","evidence":"exact lengths, materials, strengths, torque, locking and reuse absent"},
        {"item":"XGB-006","quantity":1,"manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"fixed guard/bellows and strain-relieved cable route","state":"DESIGN AND SELECTION REQUIRED","evidence":"access-probe, retention, flex and drop evidence absent"},
    ])

    (OUT / "package-summary.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "date": "2026-08-10",
        "status": "PREFERRED LIGHTWEIGHT FEASIBILITY BRANCH - NOT SELECTED",
        "source_step_sha256": sha256(SOURCE_STEP),
        "actuator_model": "XC330-T288-T",
        "actuator_sku": "902-0171-000",
        "actuator_mass_g": XC330_MASS_G,
        "hard_opening_mm": [HARD_OPENING_MIN, HARD_OPENING_MAX],
        "nominal_padded_opening_mm": [padded_min, padded_max],
        "required_object_dimension_mm": [40.0, 70.0],
        "pitch_radius_mm": PITCH_RADIUS,
        "full_travel_rotation_deg": round(rotation_deg, 6),
        "custom_full_density_calculation_mass_g": round(custom_mass_g, 6),
        "screen_subtotal_g": round(screen_subtotal, 6),
        "remaining_incomplete_headroom_g": round(headroom, 6),
        "open_holds": len(holds),
        "requirements_closed": 0,
        "sol_blockers_closed": 0,
        "procurement_release": False,
        "fabrication_release": False,
        "connection_release": False,
        "motion_release": False,
        "energization_release": False,
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    (GUIDE / "index.html").write_text(guide_html(metrics), encoding="utf-8", newline="\n")
    write_generated_source_manifest()
    print(f"Generated {IDENTIFIER}: custom full-density calculation {custom_mass_g:.3f} g; incomplete headroom {headroom:.3f} g")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
