"""Project Button HR-V0 preliminary mechanical baseline.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

This source generates quote geometry and an assembly-space model.  Vendor
components are represented by controlled envelopes in the assembly; their
manufacturer STEP files remain unmodified under cad/vendor/robotis.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
PARTS = OUT / "parts"
DRAWINGS = OUT / "drawings"
FIT_COUPONS = OUT / "fit-coupons"
HARD_STOPS = OUT / "hard-stops"
SAFETY_ENCLOSURE = OUT / "safety-enclosure"

REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
MATERIAL = "6061-T6 aluminum"
DENSITY_KG_MM3 = 2.70e-6

LINK_CENTERS_MM = 160.0
LINK_WIDTH_MM = 44.0
LINK_THICKNESS_MM = 4.75  # nominal 3/16 in sheet; supplier tolerance applies
FRAME_PCD_MM = 22.0
FRAME_HOLE_MM = 2.70  # candidate M2.5 normal clearance; verify supplier/process
S102_TAPPED_RECT_X_MM = 32.0
S102_TAPPED_RECT_Z_MM = 16.0

FIT_COUPON_PART = "MV0-FC01"
FIT_COUPON_OUTER_D_MM = 38.0
FIT_COUPON_CENTER_CLEARANCE_MM = 14.0
FIT_COUPON_THICKNESS_MM = 2.0
S102_FIT_COUPON_PART = "MV0-FC02"
S102_FIT_COUPON_X_MM = 44.0
S102_FIT_COUPON_Z_MM = 30.0
GRIPPER_FIT_COUPON_PART = "MV0-FC03"
GRIPPER_FRAME_PATTERN_X_MM = 24.0
GRIPPER_FRAME_PATTERN_Z_MM = 12.0
GRIPPER_FIT_COUPON_X_MM = 36.0
GRIPPER_FIT_COUPON_Z_MM = 24.0
HARD_STOP_CONTACT_RADIUS_MM = 50.0
HARD_STOP_MARGIN_DEG = 5.0
J1_SOFTWARE_LIMIT_DEG = (-20.0, 70.0)
J1_MECHANICAL_DATUM_DEG = (-25.0, 75.0)
J2_INTERNAL_SOFTWARE_LIMIT_DEG = (15.0, 125.0)
J2_INTERNAL_MECHANICAL_DATUM_DEG = (10.0, 130.0)
SOURCE_MANIFEST = OUT / "SOURCE-MANIFEST.csv"

ADAPTER_X_MM = 90.0
ADAPTER_Z_MM = 110.0
ADAPTER_T_MM = 6.35  # nominal 1/4 in plate
SHOULDER_AXIS = (58.0, 70.0)
T_SLOT_HOLE_X_MM = 14.0
T_SLOT_HOLE_Z_MM = (35.0, 75.0)
T_SLOT_CLEARANCE_MM = 9.0  # candidate M8 clearance

ANCHOR_X_MM = 100.0
ANCHOR_Z_MM = 80.0
ANCHOR_T_MM = 6.35
ANCHOR_SLOT_LENGTH_MM = 28.0
ANCHOR_SLOT_WIDTH_MM = 9.0

SHOULDER_AXIS_HEIGHT_MM = 500.0
MAX_OBJECT_CENTER_REACH_MM = 360.0
MAX_OBJECT_HALF_EXTENT_MM = 35.0
PROVISIONAL_STOPPING_TRAVEL_MM = 25.0
PROVISIONAL_GUARD_CLEARANCE_MM = 25.0
PROVISIONAL_ENVELOPE_TOLERANCE_MM = 5.0
GUARD_RADIAL_ENVELOPE_MM = (
    MAX_OBJECT_CENTER_REACH_MM
    + MAX_OBJECT_HALF_EXTENT_MM
    + PROVISIONAL_STOPPING_TRAVEL_MM
    + PROVISIONAL_GUARD_CLEARANCE_MM
    + PROVISIONAL_ENVELOPE_TOLERANCE_MM
)
GUARD_INTERNAL_DEPTH_MM = 400.0
GUARD_PANEL_THICKNESS_MM = 6.0
CATCH_TRAY_X_MM = 820.0
CATCH_TRAY_Y_MM = 320.0
CATCH_TRAY_WALL_HEIGHT_MM = 50.0
CATCH_TRAY_BOTTOM_THICKNESS_MM = 3.0


def pcd_points(cx: float, cz: float, count: int = 8):
    r = FRAME_PCD_MM / 2.0
    return [
        (cx + r * math.cos(2.0 * math.pi * i / count),
         cz + r * math.sin(2.0 * math.pi * i / count))
        for i in range(count)
    ]


def link_profile() -> cq.Workplane:
    """Common flat capsule profile before configuration-specific interfaces."""
    radius = LINK_WIDTH_MM / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, -radius)
        .lineTo(LINK_CENTERS_MM, -radius)
        .threePointArc((LINK_CENTERS_MM + radius, 0.0),
                       (LINK_CENTERS_MM, radius))
        .lineTo(0.0, radius)
        .threePointArc((-radius, 0.0), (0.0, -radius))
        .close()
    )


def s102_tapped_rectangle_points(cx: float, cz: float) -> list[tuple[float, float]]:
    """Selected four-hole pattern from the S102 32 x 16 tapped rectangle."""
    return [
        (cx + dx, cz + dz)
        for dx in (-S102_TAPPED_RECT_X_MM / 2.0, S102_TAPPED_RECT_X_MM / 2.0)
        for dz in (-S102_TAPPED_RECT_Z_MM / 2.0, S102_TAPPED_RECT_Z_MM / 2.0)
    ]


def gripper_frame_rectangle_points(cx: float, cz: float) -> list[tuple[float, float]]:
    """Selected four-hole subset on the FR12-H104K broad face."""
    return [
        (cx + dx, cz + dz)
        for dx in (-GRIPPER_FRAME_PATTERN_X_MM / 2.0, GRIPPER_FRAME_PATTERN_X_MM / 2.0)
        for dz in (-GRIPPER_FRAME_PATTERN_Z_MM / 2.0, GRIPPER_FRAME_PATTERN_Z_MM / 2.0)
    ]


def upper_link_plate() -> cq.Workplane:
    """H101 output interface at J1; S102 body-frame interface at J2."""
    solid = link_profile().extrude(LINK_THICKNESS_MM)
    solid = solid.faces(">Y").workplane().pushPoints(pcd_points(0.0, 0.0)).hole(FRAME_HOLE_MM)
    return solid.faces(">Y").workplane().pushPoints(
        s102_tapped_rectangle_points(LINK_CENTERS_MM, 0.0)
    ).hole(FRAME_HOLE_MM)


def forearm_link_plate() -> cq.Workplane:
    """H101 output at J2 and selected FR12-H104K candidate interface distally."""
    solid = link_profile().extrude(LINK_THICKNESS_MM)
    solid = solid.faces(">Y").workplane().pushPoints(pcd_points(0.0, 0.0)).hole(FRAME_HOLE_MM)
    # Rotate the frame's 24 x 12 broad-face rectangle so 24 mm lies across the link.
    distal_points = [
        (LINK_CENTERS_MM + dz, dx)
        for dx, dz in gripper_frame_rectangle_points(0.0, 0.0)
    ]
    return solid.faces(">Y").workplane().pushPoints(distal_points).hole(FRAME_HOLE_MM)


def robotis_pcd22_fit_coupon() -> cq.Workplane:
    """Non-structural coupon for checking the received FR13 PCD22 interface."""
    coupon = (
        cq.Workplane("XZ")
        .circle(FIT_COUPON_OUTER_D_MM / 2.0)
        .circle(FIT_COUPON_CENTER_CLEARANCE_MM / 2.0)
        .extrude(FIT_COUPON_THICKNESS_MM)
    )
    return coupon.faces(">Y").workplane().pushPoints(pcd_points(0.0, 0.0)).hole(FRAME_HOLE_MM)


def robotis_s102_32x16_fit_coupon() -> cq.Workplane:
    """Non-structural coupon for the selected S102 four-tapped-hole rectangle."""
    coupon = (
        cq.Workplane("XZ")
        .rect(S102_FIT_COUPON_X_MM, S102_FIT_COUPON_Z_MM)
        .extrude(FIT_COUPON_THICKNESS_MM)
    )
    return coupon.faces(">Y").workplane().pushPoints(s102_tapped_rectangle_points(0.0, 0.0)).hole(FRAME_HOLE_MM)


def robotis_h104_24x12_fit_coupon() -> cq.Workplane:
    """Non-structural coupon for the selected FR12-H104K four-hole subset."""
    coupon = (
        cq.Workplane("XZ")
        .rect(GRIPPER_FIT_COUPON_X_MM, GRIPPER_FIT_COUPON_Z_MM)
        .extrude(FIT_COUPON_THICKNESS_MM)
    )
    return coupon.faces(">Y").workplane().pushPoints(
        gripper_frame_rectangle_points(0.0, 0.0)
    ).hole(FRAME_HOLE_MM)


def shoulder_adapter() -> cq.Workplane:
    """Plate between the 40-series column and FR13-S102K shoulder frame."""
    plate = cq.Workplane("XZ").rect(ADAPTER_X_MM, ADAPTER_Z_MM).extrude(ADAPTER_T_MM)
    # Workplane origin is the plate centre. Convert controlled drawing coordinates.
    sx = SHOULDER_AXIS[0] - ADAPTER_X_MM / 2.0
    sz = SHOULDER_AXIS[1] - ADAPTER_Z_MM / 2.0
    frame_pts = s102_tapped_rectangle_points(sx, sz)
    mount_pts = [
        (T_SLOT_HOLE_X_MM - ADAPTER_X_MM / 2.0,
         z - ADAPTER_Z_MM / 2.0)
        for z in T_SLOT_HOLE_Z_MM
    ]
    plate = plate.faces(">Y").workplane().pushPoints(frame_pts).hole(FRAME_HOLE_MM)
    plate = plate.faces(">Y").workplane().pushPoints(mount_pts).hole(T_SLOT_CLEARANCE_MM)
    return plate


def anchor_plate() -> cq.Workplane:
    """Candidate T-slot-to-bench anchor plate; bench fastener remains selected on site."""
    plate = cq.Workplane("XZ").rect(ANCHOR_X_MM, ANCHOR_Z_MM).extrude(ANCHOR_T_MM)
    # Two M8 frame holes and two open-selection bench slots.
    plate = plate.faces(">Y").workplane().pushPoints([(-20.0, 20.0), (20.0, 20.0)]).hole(T_SLOT_CLEARANCE_MM)
    plate = (
        plate.faces(">Y").workplane()
        .pushPoints([(-28.0, -20.0), (28.0, -20.0)])
        .slot2D(ANCHOR_SLOT_LENGTH_MM, ANCHOR_SLOT_WIDTH_MM, 0.0)
        .cutThruAll()
    )
    return plate


def servo_envelope() -> cq.Workplane:
    # Official XM540-W270-T published body envelope: 33.5 x 58.5 x 44 mm.
    return cq.Workplane("XY").box(58.5, 44.0, 33.5)


def tslot_envelope(length_mm: float, axis: str) -> cq.Workplane:
    if axis == "x":
        return cq.Workplane("XY").box(length_mm, 40.0, 40.0)
    if axis == "y":
        return cq.Workplane("XY").box(40.0, length_mm, 40.0)
    return cq.Workplane("XY").box(40.0, 40.0, length_mm)


def export_part(
    part_number: str,
    name: str,
    solid: cq.Workplane,
    material: str,
    quantity: int = 1,
):
    stem = f"{part_number}_{name}"
    exporters.export(solid, str(PARTS / f"{stem}.step"))
    exporters.export(solid, str(PARTS / f"{stem}.stl"), tolerance=0.02, angularTolerance=0.1)
    # DXF is the source for 2D cutting quotations. Export the XZ profile face.
    exporters.export(solid.faces("<Y"), str(PARTS / f"{stem}.dxf"))
    volume = solid.val().Volume()
    return {
        "part_number": part_number,
        "name": name,
        "revision": REVISION,
        "material": material,
        "volume_mm3": round(volume, 2),
        "calculated_mass_g": round(volume * DENSITY_KG_MM3 * 1000.0, 1),
        "quantity": quantity,
        "release_status": "QUOTE GEOMETRY ONLY—DRAWING REVIEW REQUIRED",
    }


def write_svg_drawing(part_number: str, title: str, kind: str):
    """Human-readable quote drawing; dimensions remain controlled in source."""
    if kind == "upper_link":
        width, height = 920, 420
        h101_holes = ''.join(
            f'<circle cx="{150 + 38.5*math.cos(2*math.pi*i/8):.1f}" '
            f'cy="{173 + 38.5*math.sin(2*math.pi*i/8):.1f}" r="4.7"/>'
            for i in range(8)
        )
        geometry = f'''
          <path d="M 150 250 L 710 250 A 77 77 0 0 0 710 96 L 150 96 A 77 77 0 0 0 150 250 Z" class="part"/>
          <g class="hole">{h101_holes}</g>
          <g class="hole"><circle cx="654" cy="145" r="4.7"/><circle cx="654" cy="201" r="4.7"/><circle cx="766" cy="145" r="4.7"/><circle cx="766" cy="201" r="4.7"/></g>
          <line x1="150" y1="300" x2="710" y2="300" class="dim"/><text x="430" y="330">160.0 +/-0.5 AXIS TO AXIS</text>
          <line x1="95" y1="96" x2="95" y2="250" class="dim"/><text x="55" y="180" transform="rotate(-90 55 180)">44.0</text>
          <text x="110" y="70">J1/H101: 8 x dia 2.70 ON dia 22 PCD</text>
          <text x="490" y="70">J2/S102: 4 x dia 2.70 ON 32 x 16 RECTANGLE</text>
          <text x="150" y="357">THICKNESS 4.75 mm NOMINAL - FASTENER STACK AND TOLERANCES NOT RELEASED</text>'''
    elif kind == "forearm_link":
        width, height = 920, 420
        h101_holes = ''.join(
            f'<circle cx="{150 + 38.5*math.cos(2*math.pi*i/8):.1f}" '
            f'cy="{173 + 38.5*math.sin(2*math.pi*i/8):.1f}" r="4.7"/>'
            for i in range(8)
        )
        gripper_holes = ''.join(
            f'<circle cx="{710 + dx*3.5:.1f}" cy="{173 + dz*3.5:.1f}" r="4.7"/>'
            for dx in (-6.0, 6.0)
            for dz in (-12.0, 12.0)
        )
        geometry = f'''
          <path d="M 150 250 L 710 250 A 77 77 0 0 0 710 96 L 150 96 A 77 77 0 0 0 150 250 Z" class="part"/>
          <g class="hole">{h101_holes}</g>
          <g class="hole">{gripper_holes}</g>
          <line x1="150" y1="300" x2="710" y2="300" class="dim"/><text x="430" y="330">160.0 +/-0.5 AXIS TO GRIPPER DATUM</text>
          <line x1="95" y1="96" x2="95" y2="250" class="dim"/><text x="55" y="180" transform="rotate(-90 55 180)">44.0</text>
          <text x="110" y="70">J2/H101: 8 x dia 2.70 ON dia 22 PCD</text>
          <text x="470" y="50">GRIPPER/H104: 4 x dia 2.70</text>
          <text x="470" y="74">12 LONGITUDINAL x 24 TRANSVERSE</text>
          <text x="150" y="357">THICKNESS 4.75 mm NOMINAL - DO NOT CUT UNTIL MV0-FC03 PHYSICAL FIT PASSES</text>'''
    elif kind == "link":
        width, height = 920, 380
        geometry = f'''
          <path d="M 150 250 L 710 250 A 77 77 0 0 0 710 96 L 150 96 A 77 77 0 0 0 150 250 Z" class="part"/>
          <g class="hole">{''.join(f'<circle cx="{150 + (560 if end else 0) + 38.5*math.cos(2*math.pi*i/8):.1f}" cy="{173 + 38.5*math.sin(2*math.pi*i/8):.1f}" r="4.7"/>' for end in (0,1) for i in range(8))}</g>
          <line x1="150" y1="300" x2="710" y2="300" class="dim"/><text x="430" y="330">160.0 ±0.5 AXIS TO AXIS</text>
          <line x1="95" y1="96" x2="95" y2="250" class="dim"/><text x="55" y="180" transform="rotate(-90 55 180)">44.0</text>
          <text x="150" y="70">2 × 8 HOLES ⌀2.70 ON ⌀22.0 PCD, 45° EQUAL SPACING</text>
          <text x="150" y="357">THICKNESS 4.75 mm NOMINAL · DEBURR ALL EDGES · BREAK SHARP EDGES 0.5 MAX</text>'''
    elif kind == "adapter_s102":
        width, height = 920, 500
        geometry = '''
          <rect x="180" y="80" width="450" height="300" class="part"/>
          <g class="hole"><circle cx="390" cy="187" r="7"/><circle cx="390" cy="267" r="7"/><circle cx="550" cy="187" r="7"/><circle cx="550" cy="267" r="7"/><circle cx="250" cy="285" r="22"/><circle cx="250" cy="176" r="22"/></g>
          <text x="180" y="55">90.0 x 110.0 x 6.35 mm NOMINAL</text>
          <text x="650" y="190">S102: 4 x dia 2.70</text><text x="650" y="218">ON 32 x 16 RECTANGLE</text>
          <text x="650" y="285">2 x dia 9.0 CANDIDATE</text><text x="650" y="313">M8 COLUMN FASTENERS</text>
          <text x="180" y="430">SHOULDER AXIS: X=58.0, Z=70.0 FROM LOWER-LEFT DATUM</text>
          <text x="180" y="460">FASTENER LENGTH, ENGAGEMENT, TORQUE AND TOLERANCES: SELECTION REQUIRED</text>'''
    elif kind == "adapter":
        width, height = 920, 500
        geometry = '''
          <rect x="180" y="80" width="450" height="300" class="part"/>
          <g class="hole"><circle cx="470" cy="189" r="7"/><circle cx="497" cy="200" r="7"/><circle cx="508" cy="227" r="7"/><circle cx="497" cy="254" r="7"/><circle cx="470" cy="265" r="7"/><circle cx="443" cy="254" r="7"/><circle cx="432" cy="227" r="7"/><circle cx="443" cy="200" r="7"/><circle cx="250" cy="285" r="22"/><circle cx="250" cy="176" r="22"/></g>
          <text x="180" y="55">90.0 × 110.0 × 6.35 mm NOMINAL</text>
          <text x="655" y="190">8 × ⌀2.70</text><text x="655" y="218">ON ⌀22.0 PCD</text>
          <text x="655" y="285">2 × ⌀9.0 CANDIDATE</text><text x="655" y="313">M8 COLUMN FASTENERS</text>
          <text x="180" y="430">SHOULDER AXIS: X=58.0, Z=70.0 FROM LOWER-LEFT DATUM</text>
          <text x="180" y="460">COLUMN HOLES: X=14.0; Z=35.0 AND 75.0 · VERIFY AGAINST ACTUAL FRAME BEFORE CUT</text>'''
    else:
        width, height = 920, 450
        geometry = '''
          <rect x="170" y="80" width="500" height="260" class="part"/>
          <g class="hole"><circle cx="320" cy="145" r="22"/><circle cx="520" cy="145" r="22"/><rect x="265" y="235" width="110" height="32" rx="16"/><rect x="465" y="235" width="110" height="32" rx="16"/></g>
          <text x="170" y="55">100.0 × 80.0 × 6.35 mm NOMINAL</text>
          <text x="690" y="145">2 × ⌀9.0 FRAME</text><text x="690" y="252">2 × 28 × 9 SLOT</text>
          <text x="170" y="395">BENCH FASTENER, EDGE DISTANCE, SUBSTRATE AND PULL-OUT: SELECTION REQUIRED AFTER SITE SURVEY</text>'''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <style>
        text {{ font: 16px system-ui, sans-serif; fill: #082554; }}
        .title {{ font-size: 24px; font-weight: 700; }}
        .warning {{ font-size: 18px; font-weight: 700; fill: #8a4b00; }}
        .part {{ fill: #d9efff; stroke: #082554; stroke-width: 3; }}
        .hole {{ fill: white; stroke: #082554; stroke-width: 2; }}
        .dim {{ stroke: #b17700; stroke-width: 2; marker-start: url(#arrow); marker-end: url(#arrow); }}
      </style>
      <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#b17700"/></marker></defs>
      <text x="30" y="32" class="title">{part_number} · {title}</text>
      {geometry}
      <text x="30" y="{height-14}" class="warning">{REVISION} · PRELIMINARY—NOT RELEASED FOR FABRICATION</text>
    </svg>'''
    (DRAWINGS / f"{part_number}_{kind}.svg").write_text(svg, encoding="utf-8")


def export_fit_coupon(coupon: cq.Workplane) -> dict[str, object]:
    """Export a non-structural PCD22 coupon and a calibrated 1:1 A4 overlay."""
    stem = f"{FIT_COUPON_PART}_robotis_pcd22_fit_coupon"
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.step"))
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.stl"), tolerance=0.02, angularTolerance=0.1)
    exporters.export(coupon.faces("<Y"), str(FIT_COUPONS / f"{stem}.dxf"))

    cx, cy = 105.0, 82.0
    hole_circles = "".join(
        f'<circle cx="{cx + FRAME_PCD_MM/2*math.cos(2*math.pi*i/8):.3f}" '
        f'cy="{cy + FRAME_PCD_MM/2*math.sin(2*math.pi*i/8):.3f}" r="{FRAME_HOLE_MM/2:.3f}" class="hole"/>'
        for i in range(8)
    )
    overlay = f'''<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
      <style>
        text {{ font-family: Arial, sans-serif; font-size: 5px; fill: #082554; }}
        .title {{ font-size: 7px; font-weight: 700; }}
        .warning {{ font-size: 5px; font-weight: 700; fill: #8a4b00; }}
        .coupon {{ fill: none; stroke: #082554; stroke-width: 0.35; }}
        .hole {{ fill: none; stroke: #b17700; stroke-width: 0.35; }}
        .center {{ stroke: #0b72b9; stroke-width: 0.25; stroke-dasharray: 2 1; }}
        .scale {{ stroke: #082554; stroke-width: 0.6; }}
      </style>
      <text x="15" y="15" class="title">{FIT_COUPON_PART} - ROBOTIS PCD22 FIT COUPON</text>
      <text x="15" y="23" class="title">1:1 A4 OVERLAY</text>
      <text x="15" y="32" class="warning">FIT CHECK ONLY - NOT A STRUCTURAL OR FABRICATION-RELEASED PART</text>
      <text x="15" y="40">Print at ACTUAL SIZE / 100%. Disable Fit, Shrink, and Scale-to-page.</text>
      <circle cx="{cx}" cy="{cy}" r="{FIT_COUPON_OUTER_D_MM/2:.3f}" class="coupon"/>
      <circle cx="{cx}" cy="{cy}" r="{FIT_COUPON_CENTER_CLEARANCE_MM/2:.3f}" class="coupon"/>
      {hole_circles}
      <line x1="{cx-24}" y1="{cy}" x2="{cx+24}" y2="{cy}" class="center"/>
      <line x1="{cx}" y1="{cy-24}" x2="{cx}" y2="{cy+24}" class="center"/>
      <text x="15" y="116">8 x dia 2.70 candidate clearance holes on dia 22.00 PCD; 45 deg equal spacing.</text>
      <text x="15" y="124">Manufacturer drawings call out 8 x dia 2.5 THRU on dia 22 PCD.</text>
      <text x="15" y="132">Coupon OD 38.0; center clearance 14.0; coupon thickness 2.0 nominal.</text>
      <text x="15" y="144">Verify against received FR13-H101K and FR13-S102K broad faces.</text>
      <text x="15" y="152">Do not release metal holes from paper/CAD agreement alone. Record physical fit.</text>
      <line x1="15" y1="174" x2="115" y2="174" class="scale"/>
      <line x1="15" y1="170" x2="15" y2="178" class="scale"/>
      <line x1="115" y1="170" x2="115" y2="178" class="scale"/>
      <text x="15" y="186">X PRINT SCALE CHECK: 100.00 mm</text>
      <text x="15" y="194">Record measured X before using the overlay.</text>
      <line x1="155" y1="174" x2="155" y2="274" class="scale"/>
      <line x1="151" y1="174" x2="159" y2="174" class="scale"/>
      <line x1="151" y1="274" x2="159" y2="274" class="scale"/>
      <text x="163" y="186">Y SCALE</text><text x="163" y="194">100.00 mm</text><text x="163" y="202">Record Y</text>
      <text x="15" y="222">Source: ROBOTIS FR13-H101K and FR13-S102K drawings</text>
      <text x="15" y="230">dated 2026/01/07. NONSCALE / FOR REFERENCE ONLY.</text>
      <text x="15" y="240">Hashes and URLs: cad/vendor/robotis/vendor-manifest.csv</text>
      <text x="15" y="286" class="warning">PRELIMINARY - PHYSICAL FIT AND TOLERANCE REVIEW REQUIRED</text>
      <text x="15" y="294" class="warning">NOT RELEASED FOR FABRICATION OR ENERGIZATION</text>
    </svg>'''
    (FIT_COUPONS / f"{stem}_1to1_A4.svg").write_text(overlay, encoding="utf-8")
    return {
        "part_number": FIT_COUPON_PART,
        "description": "ROBOTIS PCD22 non-structural fit coupon",
        "revision": REVISION,
        "outer_diameter_mm": FIT_COUPON_OUTER_D_MM,
        "outer_x_mm": "",
        "outer_z_mm": "",
        "center_clearance_mm": FIT_COUPON_CENTER_CLEARANCE_MM,
        "hole_count": 8,
        "hole_diameter_mm": FRAME_HOLE_MM,
        "pcd_mm": FRAME_PCD_MM,
        "pattern_x_mm": "",
        "pattern_z_mm": "",
        "thickness_mm": FIT_COUPON_THICKNESS_MM,
        "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
    }


def export_s102_fit_coupon(coupon: cq.Workplane) -> dict[str, object]:
    """Export the selected S102 32 x 16 tapped-pattern coupon and 1:1 overlay."""
    stem = f"{S102_FIT_COUPON_PART}_s102_32x16_tapped_pattern_coupon"
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.step"))
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.stl"), tolerance=0.02, angularTolerance=0.1)
    exporters.export(coupon.faces("<Y"), str(FIT_COUPONS / f"{stem}.dxf"))

    cx, cy = 105.0, 82.0
    holes = "".join(
        f'<circle cx="{cx + dx:.3f}" cy="{cy + dz:.3f}" r="{FRAME_HOLE_MM/2:.3f}" class="hole"/>'
        for dx in (-S102_TAPPED_RECT_X_MM / 2.0, S102_TAPPED_RECT_X_MM / 2.0)
        for dz in (-S102_TAPPED_RECT_Z_MM / 2.0, S102_TAPPED_RECT_Z_MM / 2.0)
    )
    overlay = f'''<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
      <style>
        text {{ font-family: Arial, sans-serif; font-size: 5px; fill: #082554; }}
        .title {{ font-size: 7px; font-weight: 700; }}
        .warning {{ font-size: 5px; font-weight: 700; fill: #8a4b00; }}
        .coupon {{ fill: none; stroke: #082554; stroke-width: 0.35; }}
        .hole {{ fill: none; stroke: #b17700; stroke-width: 0.35; }}
        .center {{ stroke: #0b72b9; stroke-width: 0.25; stroke-dasharray: 2 1; }}
        .scale {{ stroke: #082554; stroke-width: 0.6; }}
      </style>
      <text x="15" y="15" class="title">{S102_FIT_COUPON_PART} - S102 32 x 16 TAP PATTERN</text>
      <text x="15" y="23" class="title">1:1 A4 OVERLAY</text>
      <text x="15" y="32" class="warning">FIT CHECK ONLY - NOT A STRUCTURAL OR FABRICATION-RELEASED PART</text>
      <text x="15" y="40">Print at ACTUAL SIZE / 100%. Disable Fit, Shrink, and Scale-to-page.</text>
      <rect x="{cx-S102_FIT_COUPON_X_MM/2:.3f}" y="{cy-S102_FIT_COUPON_Z_MM/2:.3f}" width="{S102_FIT_COUPON_X_MM:.3f}" height="{S102_FIT_COUPON_Z_MM:.3f}" class="coupon"/>
      {holes}
      <line x1="{cx-24}" y1="{cy}" x2="{cx+24}" y2="{cy}" class="center"/>
      <line x1="{cx}" y1="{cy-20}" x2="{cx}" y2="{cy+20}" class="center"/>
      <text x="15" y="116">4 x dia 2.70 candidate clearance holes on a 32.00 x 16.00 rectangle.</text>
      <text x="15" y="124">Selected manufacturer feature: 4-M2.5 x 0.45 TAP THRU on S102 broad face.</text>
      <text x="15" y="132">Coupon 44.0 x 30.0 x 2.0 nominal. It does not test thread strength.</text>
      <text x="15" y="144">Verify against the received FR13-S102K broad face without forcing.</text>
      <text x="15" y="152">Bolt length, engagement, grade, torque and retention remain SELECTION REQUIRED.</text>
      <line x1="15" y1="174" x2="115" y2="174" class="scale"/>
      <line x1="15" y1="170" x2="15" y2="178" class="scale"/>
      <line x1="115" y1="170" x2="115" y2="178" class="scale"/>
      <text x="15" y="186">X PRINT SCALE CHECK: 100.00 mm</text>
      <text x="15" y="194">Record measured X before using the overlay.</text>
      <line x1="155" y1="174" x2="155" y2="274" class="scale"/>
      <line x1="151" y1="174" x2="159" y2="174" class="scale"/>
      <line x1="151" y1="274" x2="159" y2="274" class="scale"/>
      <text x="163" y="186">Y SCALE</text><text x="163" y="194">100.00 mm</text><text x="163" y="202">Record Y</text>
      <text x="15" y="222">Source: ROBOTIS FR13-S102K reference drawing</text>
      <text x="15" y="230">dated 2026/01/07. NONSCALE / FOR REFERENCE ONLY.</text>
      <text x="15" y="240">Received part governs. Hashes and URLs:</text>
      <text x="15" y="248">cad/vendor/robotis/vendor-manifest.csv</text>
      <text x="15" y="286" class="warning">PRELIMINARY - PHYSICAL FIT AND THREAD INSPECTION REQUIRED</text>
      <text x="15" y="294" class="warning">NOT RELEASED FOR FABRICATION OR ENERGIZATION</text>
    </svg>'''
    (FIT_COUPONS / f"{stem}_1to1_A4.svg").write_text(overlay, encoding="utf-8")
    return {
        "part_number": S102_FIT_COUPON_PART,
        "description": "FR13-S102K 32 x 16 tapped-pattern non-structural fit coupon",
        "revision": REVISION,
        "outer_diameter_mm": "",
        "outer_x_mm": S102_FIT_COUPON_X_MM,
        "outer_z_mm": S102_FIT_COUPON_Z_MM,
        "center_clearance_mm": "",
        "hole_count": 4,
        "hole_diameter_mm": FRAME_HOLE_MM,
        "pcd_mm": "",
        "pattern_x_mm": S102_TAPPED_RECT_X_MM,
        "pattern_z_mm": S102_TAPPED_RECT_Z_MM,
        "thickness_mm": FIT_COUPON_THICKNESS_MM,
        "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
    }


def export_gripper_fit_coupon(coupon: cq.Workplane) -> dict[str, object]:
    """Export the selected FR12-H104K 24 x 12 four-hole coupon and overlay."""
    stem = f"{GRIPPER_FIT_COUPON_PART}_h104_24x12_mount_pattern_coupon"
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.step"))
    exporters.export(coupon, str(FIT_COUPONS / f"{stem}.stl"), tolerance=0.02, angularTolerance=0.1)
    exporters.export(coupon.faces("<Y"), str(FIT_COUPONS / f"{stem}.dxf"))

    cx, cy = 105.0, 82.0
    holes = "".join(
        f'<circle cx="{cx + dx:.3f}" cy="{cy + dz:.3f}" r="{FRAME_HOLE_MM/2:.3f}" class="hole"/>'
        for dx, dz in gripper_frame_rectangle_points(0.0, 0.0)
    )
    overlay = f'''<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">
      <style>
        text {{ font-family: Arial, sans-serif; font-size: 5px; fill: #082554; }}
        .title {{ font-size: 7px; font-weight: 700; }}
        .warning {{ font-size: 5px; font-weight: 700; fill: #8a4b00; }}
        .coupon {{ fill: none; stroke: #082554; stroke-width: 0.35; }}
        .hole {{ fill: none; stroke: #b17700; stroke-width: 0.35; }}
        .center {{ stroke: #0b72b9; stroke-width: 0.25; stroke-dasharray: 2 1; }}
        .scale {{ stroke: #082554; stroke-width: 0.6; }}
      </style>
      <text x="15" y="15" class="title">{GRIPPER_FIT_COUPON_PART} - FR12-H104K SELECTED 24 x 12 PATTERN</text>
      <text x="15" y="23" class="title">1:1 A4 OVERLAY</text>
      <text x="15" y="32" class="warning">FIT CHECK ONLY - NOT A STRUCTURAL OR FABRICATION-RELEASED PART</text>
      <text x="15" y="40">Print at ACTUAL SIZE / 100%. Disable Fit, Shrink, and Scale-to-page.</text>
      <rect x="{cx-GRIPPER_FIT_COUPON_X_MM/2:.3f}" y="{cy-GRIPPER_FIT_COUPON_Z_MM/2:.3f}" width="{GRIPPER_FIT_COUPON_X_MM:.3f}" height="{GRIPPER_FIT_COUPON_Z_MM:.3f}" class="coupon"/>
      {holes}
      <line x1="{cx-24}" y1="{cy}" x2="{cx+24}" y2="{cy}" class="center"/>
      <line x1="{cx}" y1="{cy-20}" x2="{cx}" y2="{cy+20}" class="center"/>
      <text x="15" y="116">4 x dia 2.70 candidate clearance holes on a 24.00 x 12.00 rectangle.</text>
      <text x="15" y="124">Selected four received-STEP features on the FR12-H104K broad face.</text>
      <text x="15" y="132">Coupon 36.0 x 24.0 x 2.0 nominal. It does not validate the final load path.</text>
      <text x="15" y="144">Verify seating against the received FR12-H104K without forcing.</text>
      <text x="15" y="152">Record proposed fastener and nut/tool access at every selected hole.</text>
      <text x="15" y="160">Fastener length, grade, torque, retention and guard clearance remain SELECTION REQUIRED.</text>
      <line x1="15" y1="174" x2="115" y2="174" class="scale"/>
      <line x1="15" y1="170" x2="15" y2="178" class="scale"/>
      <line x1="115" y1="170" x2="115" y2="178" class="scale"/>
      <text x="15" y="186">X PRINT SCALE CHECK: 100.00 mm</text>
      <text x="15" y="194">Record measured X before using the overlay.</text>
      <line x1="155" y1="174" x2="155" y2="274" class="scale"/>
      <line x1="151" y1="174" x2="159" y2="174" class="scale"/>
      <line x1="151" y1="274" x2="159" y2="274" class="scale"/>
      <text x="163" y="186">Y SCALE</text><text x="163" y="194">100.00 mm</text><text x="163" y="202">Record Y</text>
      <text x="15" y="222">Source: ROBOTIS FR12-H104K reference drawing dated Aug-31-17</text>
      <text x="15" y="230">and received manufacturer STEP. Drawing states FOR REFERENCE ONLY.</text>
      <text x="15" y="240">Received part governs. Hashes and URLs:</text>
      <text x="15" y="248">cad/vendor/robotis/vendor-manifest.csv</text>
      <text x="15" y="286" class="warning">PRELIMINARY - PHYSICAL FIT AND FASTENER ACCESS INSPECTION REQUIRED</text>
      <text x="15" y="294" class="warning">NOT RELEASED FOR FABRICATION OR ENERGIZATION</text>
    </svg>'''
    (FIT_COUPONS / f"{stem}_1to1_A4.svg").write_text(overlay, encoding="utf-8")
    return {
        "part_number": GRIPPER_FIT_COUPON_PART,
        "description": "FR12-H104K selected 24 x 12 pattern non-structural fit coupon",
        "revision": REVISION,
        "outer_diameter_mm": "",
        "outer_x_mm": GRIPPER_FIT_COUPON_X_MM,
        "outer_z_mm": GRIPPER_FIT_COUPON_Z_MM,
        "center_clearance_mm": "",
        "hole_count": 4,
        "hole_diameter_mm": FRAME_HOLE_MM,
        "pcd_mm": "",
        "pattern_x_mm": GRIPPER_FRAME_PATTERN_X_MM,
        "pattern_z_mm": GRIPPER_FRAME_PATTERN_Z_MM,
        "thickness_mm": FIT_COUPON_THICKNESS_MM,
        "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
    }


def write_hard_stop_layout() -> None:
    """Write kinematic stop datums without inventing a bracket or bumper selection."""
    def point(ray_deg: float) -> tuple[float, float]:
        radians = math.radians(ray_deg)
        return (
            HARD_STOP_CONTACT_RADIUS_MM * math.cos(radians),
            HARD_STOP_CONTACT_RADIUS_MM * math.sin(radians),
        )

    rows = []
    definitions = (
        ("HS-J1-MIN", "J1", "shoulder angle from +X; CCW positive", -20.0, -25.0, -25.0),
        ("HS-J1-MAX", "J1", "shoulder angle from +X; CCW positive", 70.0, 75.0, 75.0),
        ("HS-J2-MIN", "J2", "internal elbow angle; layout ray = 180 - internal", 15.0, 10.0, 170.0),
        ("HS-J2-MAX", "J2", "internal elbow angle; layout ray = 180 - internal", 125.0, 130.0, 50.0),
    )
    for stop_id, joint, definition, software_value, mechanical_value, layout_ray in definitions:
        x_mm, z_mm = point(layout_ray)
        rows.append({
            "stop_id": stop_id,
            "joint": joint,
            "coordinate_definition": definition,
            "software_joint_value_deg": software_value,
            "mechanical_datum_joint_value_deg": mechanical_value,
            "layout_ray_deg": layout_ray,
            "moving_contact_radius_mm": HARD_STOP_CONTACT_RADIUS_MM,
            "contact_x_mm": round(x_mm, 3),
            "contact_z_mm": round(z_mm, 3),
            "required_nominal_margin_deg": HARD_STOP_MARGIN_DEG,
            "status": "DATUM STUDY ONLY - BRACKET BUMPER AND TOLERANCE DESIGN REQUIRED",
        })
    HARD_STOPS.mkdir(parents=True, exist_ok=True)
    with (HARD_STOPS / "hard-stop-datums.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    def ray(cx: float, cy: float, ray_deg: float, css: str) -> str:
        radians = math.radians(ray_deg)
        radius_px = 175.0
        x2 = cx + radius_px * math.cos(radians)
        y2 = cy - radius_px * math.sin(radians)
        return (
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{css}"/>'
            f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="6" class="{css}-point"/>'
        )

    j1_rays = "".join((
        ray(250, 360, -20, "software"),
        ray(250, 360, 70, "software"),
        ray(250, 360, -25, "mechanical"),
        ray(250, 360, 75, "mechanical"),
    ))
    j2_rays = "".join((
        ray(750, 360, 165, "software"),
        ray(750, 360, 55, "software"),
        ray(750, 360, 170, "mechanical"),
        ray(750, 360, 50, "mechanical"),
    ))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="720" viewBox="0 0 1000 720">
      <style>
        text {{ font: 16px system-ui, sans-serif; fill: #082554; }}
        .title {{ font-size: 28px; font-weight: 700; }}
        .subtitle {{ font-size: 20px; font-weight: 700; }}
        .warning {{ font-size: 18px; font-weight: 700; fill: #8a4b00; }}
        .joint {{ fill: #d9efff; stroke: #082554; stroke-width: 3; }}
        .sweep {{ fill: none; stroke: #9cb9d8; stroke-width: 2; stroke-dasharray: 8 6; }}
        .software {{ stroke: #0b72b9; stroke-width: 3; }}
        .mechanical {{ stroke: #b17700; stroke-width: 4; }}
        .software-point {{ fill: #0b72b9; stroke: white; stroke-width: 2; }}
        .mechanical-point {{ fill: #ffbf2f; stroke: #8a4b00; stroke-width: 2; }}
        .label {{ font-size: 15px; font-weight: 600; }}
      </style>
      <text x="40" y="45" class="title">HR-V0 HARD-STOP KINEMATIC DATUM STUDY</text>
      <text x="40" y="78" class="warning">NO BRACKET OR BUMPER IS RELEASED - NOT A FABRICATION DRAWING</text>
      <text x="40" y="108">Candidate moving-contact radius: 50.0 mm. Orange rays are 5 deg beyond provisional software limits.</text>
      <text x="250" y="155" text-anchor="middle" class="subtitle">J1 SHOULDER</text>
      <text x="750" y="155" text-anchor="middle" class="subtitle">J2 ELBOW</text>
      <circle cx="250" cy="360" r="175" class="sweep"/><circle cx="250" cy="360" r="25" class="joint"/>
      <circle cx="750" cy="360" r="175" class="sweep"/><circle cx="750" cy="360" r="25" class="joint"/>
      {j1_rays}{j2_rays}
      <text x="330" y="177" class="label">BLUE: SW +70 deg</text>
      <text x="330" y="202" class="label">ORANGE: STOP +75 deg</text>
      <text x="425" y="425" class="label">BLUE: SW -20 deg</text>
      <text x="425" y="450" class="label">ORANGE: STOP -25 deg</text>
      <text x="560" y="285" class="label">BLUE: SW internal 15 deg</text>
      <text x="560" y="310" class="label">ORANGE: STOP internal 10 deg</text>
      <text x="775" y="177" class="label">BLUE: SW internal 125 deg</text>
      <text x="775" y="202" class="label">ORANGE: STOP internal 130 deg</text>
      <text x="40" y="590">J1 convention: angle from horizontal +X; counter-clockwise positive.</text>
      <text x="40" y="620">J2 convention: internal elbow angle; layout ray = 180 deg - internal angle.</text>
      <text x="40" y="650">Final stop position must include measured backlash, calibration error, tolerance, bumper compression and stopping travel.</text>
      <text x="40" y="690" class="warning">PRELIMINARY - HARD-STOP LOAD PATH, MATERIAL, FASTENERS AND IMPACT TEST REMAIN DESIGN REQUIRED</text>
    </svg>'''
    (HARD_STOPS / "HR-V0_hard-stop-kinematic-layout.svg").write_text(svg, encoding="utf-8")


def write_guard_receiver_cable_study() -> None:
    """Generate a non-released guard, catch and harness space-reservation study."""
    SAFETY_ENCLOSURE.mkdir(parents=True, exist_ok=True)
    guard_width = 2.0 * GUARD_RADIAL_ENVELOPE_MM
    guard_height = SHOULDER_AXIS_HEIGHT_MM + GUARD_RADIAL_ENVELOPE_MM

    assumption_rows = [
        ("shoulder_axis_height", SHOULDER_AXIS_HEIGHT_MM, "mm", "CONTROLLED CURRENT CAD DATUM", "Correlate to surveyed bench and assembled article"),
        ("maximum_object_center_reach", MAX_OBJECT_CENTER_REACH_MM, "mm", "CONTROLLED REQUIREMENT", "Verify under INSPECT-MECH-001"),
        ("maximum_object_half_extent", MAX_OBJECT_HALF_EXTENT_MM, "mm", "DERIVED FROM 70 MM MAXIMUM OBJECT", "Freeze reference foam dimensions and tolerance"),
        ("stopping_travel_space_reservation", PROVISIONAL_STOPPING_TRAVEL_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Measure worst pose and fault stopping travel; enlarge guard if exceeded"),
        ("guard_clearance_space_reservation", PROVISIONAL_GUARD_CLEARANCE_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Select access probe and released minimum clearance"),
        ("envelope_tolerance_space_reservation", PROVISIONAL_ENVELOPE_TOLERANCE_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Close CAD build calibration and measurement tolerance stack"),
        ("guard_radial_envelope", GUARD_RADIAL_ENVELOPE_MM, "mm", "DERIVED PRELIMINARY SPACE CLAIM", "Must be at least the released swept stopping payload and tolerance union"),
        ("guard_internal_width", guard_width, "mm", "PRELIMINARY SPACE CLAIM", "Site footprint and guard-frame design required"),
        ("guard_internal_depth", GUARD_INTERNAL_DEPTH_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Complete 3D sweep cable and service-volume study"),
        ("guard_internal_height", guard_height, "mm", "PRELIMINARY SPACE CLAIM", "Site footprint and guard-frame design required"),
        ("candidate_panel_thickness", GUARD_PANEL_THICKNESS_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Exact material grade impact retention fasteners and support spacing required"),
        ("catch_tray_plan", f"{CATCH_TRAY_X_MM:.0f} x {CATCH_TRAY_Y_MM:.0f}", "mm", "PRELIMINARY SPACE CLAIM", "Execute payload drop and rebound containment tests"),
        ("catch_tray_wall_height", CATCH_TRAY_WALL_HEIGHT_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Validate maximum bounce slide and receiver-fixture interference"),
        ("catch_tray_bottom_thickness", CATCH_TRAY_BOTTOM_THICKNESS_MM, "mm", "PROVISIONAL - SELECTION REQUIRED", "Exact material support span and impact/retention proof required"),
    ]
    with (SAFETY_ENCLOSURE / "guard-receiver-assumptions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("parameter", "value", "unit", "status", "evidence_required"))
        writer.writerows(assumption_rows)

    cable_rows = [
        ("CR-001", "base_to_J1", "BASE/J1", "fixed entry to J1 service loop", "All joint poses and service isolation", "DESIGN REQUIRED", "Select cable connector gland clamp and bend radius"),
        ("CR-002", "upper_link_neutral_zone", "J1 link local", "x 35 to 125; z +28; y SELECTION REQUIRED", "J1 -25 to +75 deg mechanical range", "PRELIMINARY SPACE CLAIM", "Verify against H101/S102 frames stop hardware guard and full cable bundle"),
        ("CR-003", "J2_service_loop", "J2 local", "loop geometry SELECTION REQUIRED", "J2 internal 10 to 130 deg mechanical range", "DESIGN REQUIRED", "Measure required slack bend twist and connector load on unpowered article"),
        ("CR-004", "forearm_neutral_zone", "J2 link local", "x 35 to 125; z +28; y SELECTION REQUIRED", "J1/J2 combined mechanical ranges", "PRELIMINARY SPACE CLAIM", "Verify against H101 gripper frame stops guard and object"),
        ("CR-005", "gripper_pigtail", "FR12-H104K/XM430 local", "connector to first retained clamp SELECTION REQUIRED", "Full gripper and arm range", "DESIGN REQUIRED", "Select strain relief flex length and guarded route"),
    ]
    with (SAFETY_ENCLOSURE / "cable-route-datums.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("zone_id", "segment", "coordinate_frame", "candidate_route", "required_motion", "status", "evidence_required"))
        writer.writerows(cable_rows)

    guard = cq.Assembly(name="HR_V0_GUARD_ENVELOPE_NOT_RELEASED")
    panel = GUARD_PANEL_THICKNESS_MM
    half_depth = GUARD_INTERNAL_DEPTH_MM / 2.0
    half_width = guard_width / 2.0
    guard.add(cq.Workplane("XY").box(guard_width, panel, guard_height),
              loc=cq.Location(cq.Vector(0, -half_depth - panel / 2.0, guard_height / 2.0)), name="rear_panel_envelope")
    guard.add(cq.Workplane("XY").box(guard_width, panel, guard_height),
              loc=cq.Location(cq.Vector(0, half_depth + panel / 2.0, guard_height / 2.0)), name="tool_removable_front_panel_envelope")
    guard.add(cq.Workplane("XY").box(panel, GUARD_INTERNAL_DEPTH_MM, guard_height),
              loc=cq.Location(cq.Vector(-half_width - panel / 2.0, 0, guard_height / 2.0)), name="left_panel_envelope")
    guard.add(cq.Workplane("XY").box(panel, GUARD_INTERNAL_DEPTH_MM, guard_height),
              loc=cq.Location(cq.Vector(half_width + panel / 2.0, 0, guard_height / 2.0)), name="right_panel_envelope")
    guard.add(cq.Workplane("XY").box(guard_width, GUARD_INTERNAL_DEPTH_MM, panel),
              loc=cq.Location(cq.Vector(0, 0, guard_height + panel / 2.0)), name="top_panel_envelope")
    guard.add(cq.Workplane("XY").box(CATCH_TRAY_X_MM, CATCH_TRAY_Y_MM, CATCH_TRAY_BOTTOM_THICKNESS_MM),
              loc=cq.Location(cq.Vector(0, 0, CATCH_TRAY_BOTTOM_THICKNESS_MM / 2.0)), name="catch_bottom_envelope")
    guard.add(cq.Workplane("XY").box(CATCH_TRAY_X_MM, panel, CATCH_TRAY_WALL_HEIGHT_MM),
              loc=cq.Location(cq.Vector(0, -CATCH_TRAY_Y_MM / 2.0, CATCH_TRAY_WALL_HEIGHT_MM / 2.0)), name="catch_rear_wall_envelope")
    guard.add(cq.Workplane("XY").box(CATCH_TRAY_X_MM, panel, CATCH_TRAY_WALL_HEIGHT_MM),
              loc=cq.Location(cq.Vector(0, CATCH_TRAY_Y_MM / 2.0, CATCH_TRAY_WALL_HEIGHT_MM / 2.0)), name="catch_front_wall_envelope")
    guard.add(cq.Workplane("XY").box(panel, CATCH_TRAY_Y_MM, CATCH_TRAY_WALL_HEIGHT_MM),
              loc=cq.Location(cq.Vector(-CATCH_TRAY_X_MM / 2.0, 0, CATCH_TRAY_WALL_HEIGHT_MM / 2.0)), name="catch_left_wall_envelope")
    guard.add(cq.Workplane("XY").box(panel, CATCH_TRAY_Y_MM, CATCH_TRAY_WALL_HEIGHT_MM),
              loc=cq.Location(cq.Vector(CATCH_TRAY_X_MM / 2.0, 0, CATCH_TRAY_WALL_HEIGHT_MM / 2.0)), name="catch_right_wall_envelope")
    guard.save(str(SAFETY_ENCLOSURE / "HR-V0_guard_receiver_envelope_NOT_RELEASED.step"))

    scale = 2.0 / 3.0
    front_x = 100.0
    front_bottom = 790.0
    front_width = guard_width * scale
    front_height = guard_height * scale
    shoulder_x = front_x + front_width / 2.0
    shoulder_y = front_bottom - SHOULDER_AXIS_HEIGHT_MM * scale
    reach_r = MAX_OBJECT_CENTER_REACH_MM * scale
    envelope_r = GUARD_RADIAL_ENVELOPE_MM * scale
    plan_y = 1010.0
    plan_depth = GUARD_INTERNAL_DEPTH_MM * scale
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1320" viewBox="0 0 1100 1320">
      <style>
        text {{ font: 16px system-ui, sans-serif; fill: #082554; }}
        .title {{ font-size: 28px; font-weight: 700; }}
        .subtitle {{ font-size: 21px; font-weight: 700; }}
        .warning {{ font-size: 18px; font-weight: 700; fill: #8a4b00; }}
        .guard {{ fill: #d9efff; fill-opacity: 0.20; stroke: #082554; stroke-width: 4; }}
        .reach {{ fill: none; stroke: #0b72b9; stroke-width: 3; stroke-dasharray: 10 7; }}
        .envelope {{ fill: #ffbf2f; fill-opacity: 0.10; stroke: #b17700; stroke-width: 4; }}
        .tray {{ fill: #ffdf83; stroke: #8a4b00; stroke-width: 3; }}
        .datum {{ stroke: #082554; stroke-width: 3; }}
      </style>
      <text x="50" y="45" class="title">HR-V0 GUARD / RECEIVER PRELIMINARY SPACE STUDY</text>
      <text x="50" y="78" class="warning">NO PANEL, FRAME, FASTENER, RECEIVER OR CLEARANCE IS RELEASED</text>
      <text x="50" y="108">The orange envelope includes provisional 25 mm stopping, 25 mm clearance and 5 mm tolerance reservations.</text>
      <text x="50" y="134">Measured stopping/drop/sweep evidence governs. Increase the enclosure if any released case exceeds this space claim.</text>
      <text x="100" y="180" class="subtitle">FRONT VIEW - SHOULDER-CENTERED</text>
      <rect x="{front_x:.1f}" y="{front_bottom-front_height:.1f}" width="{front_width:.1f}" height="{front_height:.1f}" class="guard"/>
      <circle cx="{shoulder_x:.1f}" cy="{shoulder_y:.1f}" r="{envelope_r:.1f}" class="envelope"/>
      <circle cx="{shoulder_x:.1f}" cy="{shoulder_y:.1f}" r="{reach_r:.1f}" class="reach"/>
      <line x1="{shoulder_x-18:.1f}" y1="{shoulder_y:.1f}" x2="{shoulder_x+18:.1f}" y2="{shoulder_y:.1f}" class="datum"/>
      <line x1="{shoulder_x:.1f}" y1="{shoulder_y-18:.1f}" x2="{shoulder_x:.1f}" y2="{shoulder_y+18:.1f}" class="datum"/>
      <rect x="{front_x+(guard_width-CATCH_TRAY_X_MM)*scale/2:.1f}" y="{front_bottom-CATCH_TRAY_WALL_HEIGHT_MM*scale:.1f}" width="{CATCH_TRAY_X_MM*scale:.1f}" height="{CATCH_TRAY_WALL_HEIGHT_MM*scale:.1f}" class="tray"/>
      <text x="730" y="260">BLUE DASH: 360 mm object-center reach ceiling</text>
      <text x="730" y="292">ORANGE: 450 mm preliminary radial envelope</text>
      <text x="730" y="324">GUARD INSIDE: 900 W x 950 H mm</text>
      <text x="730" y="356">SHOULDER DATUM: 500 mm above bench</text>
      <text x="730" y="388">CATCH SPACE: 820 x 320 x 50 mm</text>
      <text x="730" y="438" class="warning">25 mm stopping travel is NOT measured.</text>
      <text x="730" y="470" class="warning">It is not an acceptance limit.</text>
      <text x="730" y="520">Final guard requires complete 3D sweep,</text>
      <text x="730" y="548">access probe, impact and retention proof,</text>
      <text x="730" y="576">panel support, service isolation and drop tests.</text>
      <text x="100" y="900" class="subtitle">PLAN VIEW - PRELIMINARY INTERNAL DEPTH</text>
      <rect x="{front_x:.1f}" y="{plan_y:.1f}" width="{front_width:.1f}" height="{plan_depth:.1f}" class="guard"/>
      <rect x="{front_x+(guard_width-CATCH_TRAY_X_MM)*scale/2:.1f}" y="{plan_y+(GUARD_INTERNAL_DEPTH_MM-CATCH_TRAY_Y_MM)*scale/2:.1f}" width="{CATCH_TRAY_X_MM*scale:.1f}" height="{CATCH_TRAY_Y_MM*scale:.1f}" class="tray"/>
      <line x1="{shoulder_x-18:.1f}" y1="{plan_y+plan_depth/2:.1f}" x2="{shoulder_x+18:.1f}" y2="{plan_y+plan_depth/2:.1f}" class="datum"/>
      <line x1="{shoulder_x:.1f}" y1="{plan_y+plan_depth/2-18:.1f}" x2="{shoulder_x:.1f}" y2="{plan_y+plan_depth/2+18:.1f}" class="datum"/>
      <text x="730" y="1035">GUARD INSIDE DEPTH: 400 mm provisional</text>
      <text x="730" y="1067">CATCH INSIDE PLAN: 820 x 320 mm</text>
      <text x="730" y="1117">Front panel shown as tool-removable only.</text>
      <text x="730" y="1145">No door interlock is selected or credited.</text>
      <text x="50" y="1285" class="warning">PRELIMINARY - NOT A FABRICATION DRAWING OR PERMISSION TO ENERGIZE</text>
    </svg>'''
    (SAFETY_ENCLOSURE / "HR-V0_guard_receiver_layout.svg").write_text(svg, encoding="utf-8")

    cable_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="760" viewBox="0 0 1100 760">
      <style>
        text { font: 16px system-ui, sans-serif; fill: #082554; }
        .title { font-size: 28px; font-weight: 700; }
        .warning { font-size: 18px; font-weight: 700; fill: #8a4b00; }
        .link { stroke: #082554; stroke-width: 42; stroke-linecap: round; }
        .joint { fill: #d9efff; stroke: #082554; stroke-width: 4; }
        .route { fill: none; stroke: #b17700; stroke-width: 8; stroke-linecap: round; stroke-dasharray: 12 8; }
        .zone { fill: none; stroke: #0b72b9; stroke-width: 3; stroke-dasharray: 8 6; }
      </style>
      <text x="45" y="45" class="title">HR-V0 CABLE-ROUTE DATUM STUDY</text>
      <text x="45" y="78" class="warning">CENTERLINE SPACE ONLY - NO CABLE, CLAMP, LOOP OR BEND RADIUS IS RELEASED</text>
      <line x1="170" y1="330" x2="500" y2="330" class="link"/><line x1="500" y1="330" x2="830" y2="330" class="link"/>
      <circle cx="170" cy="330" r="34" class="joint"/><circle cx="500" cy="330" r="34" class="joint"/><circle cx="830" cy="330" r="34" class="joint"/>
      <circle cx="170" cy="330" r="100" class="zone"/><circle cx="500" cy="330" r="100" class="zone"/>
      <path d="M70,460 C95,390 100,255 170,245 C240,235 275,260 335,270 L430,270 C470,270 480,245 500,245 C570,235 605,260 665,270 L780,270 C820,270 840,250 900,250" class="route"/>
      <text x="55" y="510">CR-001 fixed entry / J1 loop: DESIGN REQUIRED</text>
      <text x="235" y="220">CR-002 upper-link neutral zone</text>
      <text x="420" y="510">CR-003 J2 service loop: DESIGN REQUIRED</text>
      <text x="610" y="220">CR-004 forearm neutral zone</text>
      <text x="790" y="510">CR-005 gripper pigtail: DESIGN REQUIRED</text>
      <text x="45" y="560">Blue circles reserve the 50 mm hard-stop contact-radius study.</text>
      <text x="45" y="590">Cable must not enter any final stop, pinch, connector or guard-contact path.</text>
      <text x="45" y="620">Exact bundle, conductor/connector, bend radius, torsion and tension remain SELECTION REQUIRED.</text>
      <text x="45" y="650">Clamp spacing, flex life, abrasion protection and moving mass also remain SELECTION REQUIRED.</text>
      <text x="45" y="700" class="warning">VERIFY ALL COMBINED JOINT POSES ON THE UNPOWERED ARTICLE BEFORE ANY ACTUATOR CONNECTION</text>
      <text x="45" y="736" class="warning">PRELIMINARY - NOT A HARNESS DRAWING OR PERMISSION TO ENERGIZE</text>
    </svg>'''
    (SAFETY_ENCLOSURE / "HR-V0_cable_route_datums.svg").write_text(cable_svg, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_source_manifest() -> None:
    """Hash every generated artifact except the self-referential manifest."""
    rows = []
    for path in sorted(OUT.rglob("*"), key=lambda candidate: candidate.as_posix().lower()):
        if path.is_file() and path != SOURCE_MANIFEST:
            rows.append({
                "file": path.relative_to(OUT).as_posix(),
                "sha256": sha256(path),
                "revision": REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    with SOURCE_MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("file", "sha256", "revision", "status"))
        writer.writeheader()
        writer.writerows(rows)


def build_assembly(parts: dict[str, cq.Workplane]):
    assy = cq.Assembly(name="HR-V0_PRELIMINARY")
    # Base/column vendor envelopes. Origin: base centre, bench plane z=0.
    assy.add(tslot_envelope(500, "x"), loc=cq.Location(cq.Vector(0, -160, 20)), name="base_rear", color=cq.Color(0.25, 0.35, 0.55))
    assy.add(tslot_envelope(500, "x"), loc=cq.Location(cq.Vector(0, 160, 20)), name="base_front", color=cq.Color(0.25, 0.35, 0.55))
    assy.add(tslot_envelope(320, "y"), loc=cq.Location(cq.Vector(-210, 0, 20)), name="base_left", color=cq.Color(0.25, 0.35, 0.55))
    assy.add(tslot_envelope(320, "y"), loc=cq.Location(cq.Vector(210, 0, 20)), name="base_right", color=cq.Color(0.25, 0.35, 0.55))
    assy.add(tslot_envelope(500, "z"), loc=cq.Location(cq.Vector(-210, 0, 270)), name="column", color=cq.Color(0.25, 0.35, 0.55))

    # Controlled custom geometry shown in a neutral working pose. These locations
    # are for fit/space review, not final manufacturing datums.
    assy.add(parts["adapter"], loc=cq.Location(cq.Vector(-190, -ADAPTER_T_MM / 2, 430)), name="MV0_003_adapter", color=cq.Color(0.95, 0.68, 0.10))
    assy.add(servo_envelope(), loc=cq.Location(cq.Vector(-125, 0, 500)), name="J1_XM540_envelope", color=cq.Color(0.12, 0.35, 0.72))
    assy.add(parts["upper"], loc=cq.Location(cq.Vector(-110, -LINK_THICKNESS_MM / 2, 500)), name="MV0_001_upper", color=cq.Color(0.85, 0.88, 0.92))
    assy.add(servo_envelope(), loc=cq.Location(cq.Vector(50, 0, 500)), name="J2_XM540_envelope", color=cq.Color(0.12, 0.35, 0.72))
    assy.add(parts["forearm"], loc=cq.Location(cq.Vector(50, -LINK_THICKNESS_MM / 2, 500)), name="MV0_002_forearm", color=cq.Color(0.85, 0.88, 0.92))
    assy.add(parts["anchor_left"], loc=cq.Location(cq.Vector(-210, -ANCHOR_T_MM/2, 43)), name="MV0_004_anchor_left", color=cq.Color(0.95, 0.68, 0.10))
    assy.add(parts["anchor_right"], loc=cq.Location(cq.Vector(210, -ANCHOR_T_MM/2, 43)), name="MV0_004_anchor_right", color=cq.Color(0.95, 0.68, 0.10))
    assy.save(str(OUT / "HR-V0_preliminary_assembly.step"))
    try:
        assy.save(str(OUT / "HR-V0_preliminary_assembly.glb"))
    except Exception as exc:  # GLB depends on optional runtime support.
        (OUT / "GLB_EXPORT_FAILED.txt").write_text(str(exc), encoding="utf-8")


def main():
    PARTS.mkdir(parents=True, exist_ok=True)
    DRAWINGS.mkdir(parents=True, exist_ok=True)
    FIT_COUPONS.mkdir(parents=True, exist_ok=True)
    HARD_STOPS.mkdir(parents=True, exist_ok=True)
    SAFETY_ENCLOSURE.mkdir(parents=True, exist_ok=True)
    for obsolete_name in ("MV0-001_link.svg", "MV0-002_link.svg", "MV0-003_adapter.svg"):
        (DRAWINGS / obsolete_name).unlink(missing_ok=True)
    upper = upper_link_plate()
    forearm = forearm_link_plate()
    adapter = shoulder_adapter()
    anchor_left = anchor_plate()
    anchor_right = anchor_plate()
    fit_coupon = robotis_pcd22_fit_coupon()
    s102_fit_coupon = robotis_s102_32x16_fit_coupon()
    gripper_fit_coupon = robotis_h104_24x12_fit_coupon()
    rows = [
        export_part("MV0-001", "upper_link_plate", upper, MATERIAL),
        export_part("MV0-002", "forearm_link_plate", forearm, MATERIAL),
        export_part("MV0-003", "shoulder_adapter", adapter, MATERIAL),
        export_part("MV0-004", "bench_anchor_plate", anchor_left, MATERIAL, quantity=2),
    ]
    write_svg_drawing("MV0-001", "UPPER LINK PLATE", "upper_link")
    write_svg_drawing("MV0-002", "FOREARM LINK PLATE", "forearm_link")
    write_svg_drawing("MV0-003", "SHOULDER ADAPTER", "adapter_s102")
    write_svg_drawing("MV0-004", "BENCH ANCHOR PLATE", "anchor")
    with (OUT / "custom-parts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    coupon_rows = [
        export_fit_coupon(fit_coupon),
        export_s102_fit_coupon(s102_fit_coupon),
        export_gripper_fit_coupon(gripper_fit_coupon),
    ]
    with (FIT_COUPONS / "fit-coupons.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=coupon_rows[0].keys())
        writer.writeheader()
        writer.writerows(coupon_rows)
    write_hard_stop_layout()
    write_guard_receiver_cable_study()
    manifest = {
        "revision": REVISION,
        "units": "mm",
        "warning": "PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION",
        "controlled_parameters": {
            "link_centers_mm": LINK_CENTERS_MM,
            "link_width_mm": LINK_WIDTH_MM,
            "link_thickness_mm": LINK_THICKNESS_MM,
            "robotis_frame_pcd_mm": FRAME_PCD_MM,
            "s102_selected_tapped_rectangle_mm": [S102_TAPPED_RECT_X_MM, S102_TAPPED_RECT_Z_MM],
            "candidate_frame_hole_mm": FRAME_HOLE_MM,
            "fit_coupon_mm": [FIT_COUPON_OUTER_D_MM, FIT_COUPON_CENTER_CLEARANCE_MM, FIT_COUPON_THICKNESS_MM],
            "s102_fit_coupon_mm": [S102_FIT_COUPON_X_MM, S102_FIT_COUPON_Z_MM, FIT_COUPON_THICKNESS_MM],
            "gripper_h104_selected_rectangle_mm": [GRIPPER_FRAME_PATTERN_X_MM, GRIPPER_FRAME_PATTERN_Z_MM],
            "gripper_fit_coupon_mm": [GRIPPER_FIT_COUPON_X_MM, GRIPPER_FIT_COUPON_Z_MM, FIT_COUPON_THICKNESS_MM],
            "hard_stop_contact_radius_mm": HARD_STOP_CONTACT_RADIUS_MM,
            "hard_stop_nominal_margin_deg": HARD_STOP_MARGIN_DEG,
            "j1_software_limit_deg": list(J1_SOFTWARE_LIMIT_DEG),
            "j1_mechanical_datum_deg": list(J1_MECHANICAL_DATUM_DEG),
            "j2_internal_software_limit_deg": list(J2_INTERNAL_SOFTWARE_LIMIT_DEG),
            "j2_internal_mechanical_datum_deg": list(J2_INTERNAL_MECHANICAL_DATUM_DEG),
            "adapter_mm": [ADAPTER_X_MM, ADAPTER_Z_MM, ADAPTER_T_MM],
            "anchor_mm": [ANCHOR_X_MM, ANCHOR_Z_MM, ANCHOR_T_MM],
            "guard_space_reservation_mm": {
                "radial_envelope": GUARD_RADIAL_ENVELOPE_MM,
                "internal_width": 2.0 * GUARD_RADIAL_ENVELOPE_MM,
                "internal_depth": GUARD_INTERNAL_DEPTH_MM,
                "internal_height": SHOULDER_AXIS_HEIGHT_MM + GUARD_RADIAL_ENVELOPE_MM,
                "candidate_panel_thickness": GUARD_PANEL_THICKNESS_MM,
            },
            "guard_provisional_allowances_mm": {
                "stopping_travel": PROVISIONAL_STOPPING_TRAVEL_MM,
                "guard_clearance": PROVISIONAL_GUARD_CLEARANCE_MM,
                "envelope_tolerance": PROVISIONAL_ENVELOPE_TOLERANCE_MM,
            },
            "catch_tray_space_reservation_mm": [
                CATCH_TRAY_X_MM,
                CATCH_TRAY_Y_MM,
                CATCH_TRAY_WALL_HEIGHT_MM,
                CATCH_TRAY_BOTTOM_THICKNESS_MM,
            ],
        },
        "release_gates": [
            "Execute INSPECT-MECH-003 with MV0-FC01 against received FR13-H101K and FR13-S102K parts",
            "Execute INSPECT-MECH-004 with MV0-FC02 against the received FR13-S102K selected tapped pattern",
            "Resolve M2.5 fastener grade, engagement, torque and retention",
            "Execute INSPECT-MECH-008 with MV0-FC03 against the received FR12-H104K and verify seating and fastener access",
            "Release hard-stop bracket, bumper, load path, tolerance stack and impact validation before actuator motion",
            "Resolve T-slot fasteners, torque, anti-rotation and bracket arrangement",
            "Survey actual bench and select anchor fasteners from substrate evidence",
            "Complete structural, hard-stop, cable, guard and proof-test release",
            "Execute INSPECT-GUARD-001 INSPECT-CABLE-001 and TEST-DROP-001 on the frozen unpowered article before actuator connection",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    build_assembly({"upper": upper, "forearm": forearm, "adapter": adapter,
                    "anchor_left": anchor_left, "anchor_right": anchor_right})
    write_source_manifest()


if __name__ == "__main__":
    main()
