"""Project Button HR-V0 preliminary mechanical baseline.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.

This source generates quote geometry and an assembly-space model.  Vendor
components are represented by controlled envelopes in the assembly; their
manufacturer STEP files remain unmodified under cad/vendor/robotis.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
PARTS = OUT / "parts"
DRAWINGS = OUT / "drawings"

REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
MATERIAL = "6061-T6 aluminum"
DENSITY_KG_MM3 = 2.70e-6

LINK_CENTERS_MM = 160.0
LINK_WIDTH_MM = 44.0
LINK_THICKNESS_MM = 4.75  # nominal 3/16 in sheet; supplier tolerance applies
FRAME_PCD_MM = 22.0
FRAME_HOLE_MM = 2.70  # candidate M2.5 normal clearance; verify supplier/process

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


def pcd_points(cx: float, cz: float, count: int = 8):
    r = FRAME_PCD_MM / 2.0
    return [
        (cx + r * math.cos(2.0 * math.pi * i / count),
         cz + r * math.sin(2.0 * math.pi * i / count))
        for i in range(count)
    ]


def link_plate() -> cq.Workplane:
    """Flat capsule link with manufacturer-frame PCD at each joint."""
    radius = LINK_WIDTH_MM / 2.0
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, -radius)
        .lineTo(LINK_CENTERS_MM, -radius)
        .threePointArc((LINK_CENTERS_MM + radius, 0.0),
                       (LINK_CENTERS_MM, radius))
        .lineTo(0.0, radius)
        .threePointArc((-radius, 0.0), (0.0, -radius))
        .close()
    )
    holes = pcd_points(0.0, 0.0) + pcd_points(LINK_CENTERS_MM, 0.0)
    return profile.extrude(LINK_THICKNESS_MM).faces(">Y").workplane().pushPoints(holes).hole(FRAME_HOLE_MM)


def shoulder_adapter() -> cq.Workplane:
    """Plate between the 40-series column and FR13-S102K shoulder frame."""
    plate = cq.Workplane("XZ").rect(ADAPTER_X_MM, ADAPTER_Z_MM).extrude(ADAPTER_T_MM)
    # Workplane origin is the plate centre. Convert controlled drawing coordinates.
    sx = SHOULDER_AXIS[0] - ADAPTER_X_MM / 2.0
    sz = SHOULDER_AXIS[1] - ADAPTER_Z_MM / 2.0
    frame_pts = pcd_points(sx, sz)
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


def export_part(part_number: str, name: str, solid: cq.Workplane, material: str):
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
        "quantity": 1,
        "release_status": "QUOTE GEOMETRY ONLY—DRAWING REVIEW REQUIRED",
    }


def write_svg_drawing(part_number: str, title: str, kind: str):
    """Human-readable quote drawing; dimensions remain controlled in source."""
    if kind == "link":
        width, height = 920, 380
        geometry = f'''
          <path d="M 150 250 L 710 250 A 77 77 0 0 0 710 96 L 150 96 A 77 77 0 0 0 150 250 Z" class="part"/>
          <g class="hole">{''.join(f'<circle cx="{150 + (560 if end else 0) + 38.5*math.cos(2*math.pi*i/8):.1f}" cy="{173 + 38.5*math.sin(2*math.pi*i/8):.1f}" r="4.7"/>' for end in (0,1) for i in range(8))}</g>
          <line x1="150" y1="300" x2="710" y2="300" class="dim"/><text x="430" y="330">160.0 ±0.5 AXIS TO AXIS</text>
          <line x1="95" y1="96" x2="95" y2="250" class="dim"/><text x="55" y="180" transform="rotate(-90 55 180)">44.0</text>
          <text x="150" y="70">2 × 8 HOLES ⌀2.70 ON ⌀22.0 PCD, 45° EQUAL SPACING</text>
          <text x="150" y="357">THICKNESS 4.75 mm NOMINAL · DEBURR ALL EDGES · BREAK SHARP EDGES 0.5 MAX</text>'''
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
    upper = link_plate()
    forearm = link_plate()
    adapter = shoulder_adapter()
    anchor_left = anchor_plate()
    anchor_right = anchor_plate()
    rows = [
        export_part("MV0-001", "upper_link_plate", upper, MATERIAL),
        export_part("MV0-002", "forearm_link_plate", forearm, MATERIAL),
        export_part("MV0-003", "shoulder_adapter", adapter, MATERIAL),
        export_part("MV0-004", "bench_anchor_plate", anchor_left, MATERIAL),
    ]
    write_svg_drawing("MV0-001", "UPPER LINK PLATE", "link")
    write_svg_drawing("MV0-002", "FOREARM LINK PLATE", "link")
    write_svg_drawing("MV0-003", "SHOULDER ADAPTER", "adapter")
    write_svg_drawing("MV0-004", "BENCH ANCHOR PLATE", "anchor")
    with (OUT / "custom-parts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "revision": REVISION,
        "units": "mm",
        "warning": "PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION",
        "controlled_parameters": {
            "link_centers_mm": LINK_CENTERS_MM,
            "link_width_mm": LINK_WIDTH_MM,
            "link_thickness_mm": LINK_THICKNESS_MM,
            "robotis_frame_pcd_mm": FRAME_PCD_MM,
            "candidate_frame_hole_mm": FRAME_HOLE_MM,
            "adapter_mm": [ADAPTER_X_MM, ADAPTER_Z_MM, ADAPTER_T_MM],
            "anchor_mm": [ANCHOR_X_MM, ANCHOR_Z_MM, ANCHOR_T_MM],
        },
        "release_gates": [
            "Overlay DXF against physical FR13-H101K and FR13-S102K fit-check coupons",
            "Resolve M2.5 fastener grade, engagement, torque and retention",
            "Resolve T-slot fasteners, torque, anti-rotation and bracket arrangement",
            "Survey actual bench and select anchor fasteners from substrate evidence",
            "Complete structural, hard-stop, cable, guard and proof-test release",
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    build_assembly({"upper": upper, "forearm": forearm, "adapter": adapter,
                    "anchor_left": anchor_left, "anchor_right": anchor_right})


if __name__ == "__main__":
    main()

