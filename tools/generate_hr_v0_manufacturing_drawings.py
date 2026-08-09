#!/usr/bin/env python3
"""Generate the R137 conventional drawing and finished-profile DXF candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import textwrap
from pathlib import Path

import cadquery as cq
import ezdxf
from ezdxf import bbox as dxf_bbox


ROOT = Path(__file__).resolve().parents[1]
GENERATED_ROOT = ROOT / "cad" / "hr-v0" / "generated"
P07 = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7" / "parts"
P08 = ROOT / "cad" / "hr-v0" / "generated" / "countersink-mbd-p0.1"
DFM = ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1"
CAD_OUT = ROOT / "cad" / "hr-v0" / "generated" / "mechanical-drawing-p0.1"
DXF_OUT = CAD_OUT / "dxf"
DRAWING_OUT = CAD_OUT / "drawings"
OUT = ROOT / "release" / "hr-v0" / "mechanical-drawing-p0.1"
DOC = ROOT / "docs" / "hr-v0-manufacturing-drawing-p0.1.md"
IDENTIFIER = "HR-V0-MECH-DWG-P0.1"
CANDIDATE = "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}


PARTS = {
    "MV0-C01": {
        "name": "Joint-to-20-2040 adapter",
        "step": P08 / "MV0-C01_rect32x16_to_20-2040_countersunk_adapter_P0.8_nominal-countersink-candidate.step",
        "profile_tolerance": "+/-0.10 mm rectangular envelope",
        "holes": [
            *(dict(fid=f"J{i+1}", x=x, z=z, diameter=2.70, layer="M2_5_CLEARANCE") for i, (x, z) in enumerate(((-16, -8), (-16, 8), (16, -8), (16, 8)))),
            dict(fid="E1", x=0, z=-10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
            dict(fid="E2", x=0, z=10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
        ],
        "pattern_note": "J1-J4: Ø2.70 +0.10/-0.00 at X=±16.00, Z=±8.00; coordinates ±0.05",
        "special_note": "E1-E2: Ø5.50 +0.10/-0.00 at X=0, Z=±10.00; CSK Ø11.30 +0.10/-0.00 x 90°",
    },
    "MV0-C04": {
        "name": "H104-to-20-2040 adapter",
        "step": P08 / "MV0-C04_H104_to_20-2040_countersunk_adapter_P0.8_nominal-countersink-candidate.step",
        "profile_tolerance": "+/-0.10 mm rectangular envelope",
        "holes": [
            *(dict(fid=f"H{i+1}", x=x, z=z, diameter=2.70, layer="M2_5_CLEARANCE") for i, (x, z) in enumerate(((-11, 8), (11, 8), (-12, -6), (12, -6)))),
            dict(fid="E1", x=0, z=-10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
            dict(fid="E2", x=0, z=10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
        ],
        "pattern_note": "H1-H4: Ø2.70 +0.10/-0.00 at (-11,+8),(+11,+8),(-12,-6),(+12,-6); coordinates ±0.05",
        "special_note": "E1-E2: Ø5.50 +0.10/-0.00 at X=0, Z=±10.00; CSK Ø11.30 +0.10/-0.00 x 90°",
    },
    "MV0-C05": {
        "name": "S102-to-40-4040 support",
        "step": P07 / "MV0-C05_S102_to_40-4040_side_slot_support.step",
        "profile_tolerance": "+/-0.10 mm rectangular envelope",
        "holes": [
            *(dict(fid=f"S{i+1}", x=x, z=z, diameter=2.70, layer="M2_5_CLEARANCE") for i, (x, z) in enumerate(((-16, -8), (-16, 8), (16, -8), (16, 8)))),
            dict(fid="K1", x=0, z=-30, diameter=8.50, layer="M8_CLEARANCE"),
            dict(fid="K2", x=0, z=30, diameter=8.50, layer="M8_CLEARANCE"),
        ],
        "pattern_note": "S1-S4: Ø2.70 +0.10/-0.00 at X=±16.00, Z=±8.00; coordinates ±0.05",
        "special_note": "K1-K2: Ø8.50 +0.10/-0.00 at X=0, Z=±30.00; coordinates ±0.05",
    },
    "MV0-C06": {
        "name": "J2 positive moving striker",
        "step": P08 / "MV0-C06_J2_positive_moving_striker_adapter_P0.8_nominal-countersink-candidate.step",
        "profile_tolerance": "profile +/-0.05 mm; R2.00 all finished profile corners",
        "holes": [
            *(dict(fid=f"J{i+1}", x=x, z=z, diameter=2.70, layer="M2_5_CLEARANCE") for i, (x, z) in enumerate(((-16, -8), (-16, 8), (16, -8), (16, 8)))),
            dict(fid="E1", x=0, z=-10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
            dict(fid="E2", x=0, z=10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
        ],
        "pattern_note": "J1-J4: Ø2.70 +0.10/-0.00 at X=±16.00, Z=±8.00; coordinates ±0.05",
        "special_note": "Twin striker top datum Z=37.380699 at X=±38.0; ±0.025 relative to registered J1-J4 pattern",
    },
    "MV0-C07": {
        "name": "J2 positive fixed catch",
        "step": P08 / "MV0-C07_J2_positive_fixed_catch_adapter_P0.8_nominal-countersink-candidate.step",
        "profile_tolerance": "profile +/-0.05 mm; R2.00 all finished profile corners",
        "holes": [
            *(dict(fid=f"J{i+1}", x=x, z=z, diameter=2.70, layer="M2_5_CLEARANCE") for i, (x, z) in enumerate(((-16, -8), (-16, 8), (16, -8), (16, 8)))),
            dict(fid="E1", x=0, z=-10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
            dict(fid="E2", x=0, z=10, diameter=5.50, csk=11.30, layer="M5_CLEARANCE"),
        ],
        "pattern_note": "J1-J4: Ø2.70 +0.10/-0.00 at X=±16.00, Z=±8.00; coordinates ±0.05",
        "special_note": "Two moving-side rail faces recessed 1.000 ±0.05; rails coplanar <=0.03; rail centerlines X=±38",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def outer_wire(shape: cq.Shape) -> cq.Wire:
    y0 = shape.BoundingBox().ymin
    faces = [face for face in shape.Faces() if face.geomType() == "PLANE" and abs(face.Center().y - y0) < 1e-6]
    face = max(faces, key=lambda item: item.Area())
    return max(face.Wires(), key=lambda item: item.Length())


def make_finished_dxf(part_id: str, spec: dict[str, object], shape: cq.Shape, path: Path) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".profile-temp.dxf")
    cq.exporters.exportDXF(cq.Workplane("XZ").newObject([outer_wire(shape)]), str(temp))
    source = ezdxf.readfile(temp)
    doc = ezdxf.new("R2013", setup=True)
    for layer, color in (("FINISHED_PROFILE_STEP_DERIVED", 7), ("M2_5_CLEARANCE", 5), ("M5_CLEARANCE", 3), ("M5_COUNTERSINK_NOMINAL", 2), ("M8_CLEARANCE", 6), ("FACE_MILL_RECESS_BOUNDARY", 1)):
        if layer not in doc.layers:
            doc.layers.add(layer, color=color)
    model = doc.modelspace()
    profile_count = 0
    line_count = 0
    arc_count = 0
    for entity in source.modelspace():
        if entity.dxftype() == "LINE":
            model.add_line((entity.dxf.start.x, entity.dxf.start.y), (entity.dxf.end.x, entity.dxf.end.y), dxfattribs={"layer": "FINISHED_PROFILE_STEP_DERIVED"})
            profile_count += 1
            line_count += 1
        elif entity.dxftype() == "ARC":
            model.add_arc((entity.dxf.center.x, entity.dxf.center.y), entity.dxf.radius, entity.dxf.start_angle, entity.dxf.end_angle, dxfattribs={"layer": "FINISHED_PROFILE_STEP_DERIVED"})
            profile_count += 1
            arc_count += 1
    for hole in spec["holes"]:
        model.add_circle((hole["x"], hole["z"]), hole["diameter"] / 2.0, dxfattribs={"layer": hole["layer"]})
        if "csk" in hole:
            model.add_circle((hole["x"], hole["z"]), hole["csk"] / 2.0, dxfattribs={"layer": "M5_COUNTERSINK_NOMINAL"})
    if part_id == "MV0-C07":
        for x0, x1 in ((-42.0, -23.5), (23.5, 42.0)):
            points = [(x0, -20.0), (x1, -20.0), (x1, 22.0), (x0, 22.0)]
            for start, end in zip(points, points[1:] + points[:1]):
                model.add_line(start, end, dxfattribs={"layer": "FACE_MILL_RECESS_BOUNDARY"})
    doc.header.custom_vars.append("PBSTATUS", "PRELIMINARY_NOT_APPROVED")
    doc.header.custom_vars.append("PBID", IDENTIFIER)
    doc.saveas(path)
    temp.unlink()
    # DXF group 999 is a standard ignored comment and does not create geometry.
    serialized = "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n"
    path.write_text(f"999\n{WARNING}\n" + serialized, encoding="utf-8", newline="\n")
    loaded = ezdxf.readfile(path)
    profile = list(loaded.modelspace().query('LINE ARC[layer=="FINISHED_PROFILE_STEP_DERIVED"]'))
    extents = dxf_bbox.extents(profile)
    box = shape.BoundingBox()
    return {
        "part_id": part_id,
        "step_profile_edge_count": len(outer_wire(shape).Edges()),
        "dxf_profile_entity_count": profile_count,
        "dxf_profile_line_count": line_count,
        "dxf_profile_arc_count": arc_count,
        "step_xmin_mm": round(box.xmin, 6), "step_xmax_mm": round(box.xmax, 6),
        "step_zmin_mm": round(box.zmin, 6), "step_zmax_mm": round(box.zmax, 6),
        "dxf_xmin_mm": round(extents.extmin.x, 6), "dxf_xmax_mm": round(extents.extmax.x, 6),
        "dxf_zmin_mm": round(extents.extmin.y, 6), "dxf_zmax_mm": round(extents.extmax.y, 6),
        "maximum_extent_delta_mm": round(max(abs(box.xmin-extents.extmin.x), abs(box.xmax-extents.extmax.x), abs(box.zmin-extents.extmin.y), abs(box.zmax-extents.extmax.y)), 9),
        "through_hole_count": len(spec["holes"]),
        "nominal_countersink_count": sum("csk" in hole for hole in spec["holes"]),
        "profile_semantics": "FINISHED PROFILE DERIVED FROM CANDIDATE STEP OUTER WIRE",
        "warning": WARNING,
    }


def wrap_svg(value: str, width: int) -> list[str]:
    return textwrap.wrap(str(value), width=width, break_long_words=True, break_on_hyphens=False) or [""]


def svg_text(x: float, y: float, value: str, css: str = "txt", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{css}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def drawing_svg(part_id: str, spec: dict[str, object], shape: cq.Shape, dxf_path: Path, controls: list[dict[str, str]], path: Path) -> None:
    doc = ezdxf.readfile(dxf_path)
    profile = list(doc.modelspace().query('LINE ARC[layer=="FINISHED_PROFILE_STEP_DERIVED"]'))
    box = shape.BoundingBox()
    scale = min(5.5, 430.0 / max(box.xlen, box.zlen))
    cx, cy = 350.0, 380.0

    def px(x: float) -> float: return cx + x * scale
    def py(z: float) -> float: return cy - z * scale

    geometry: list[str] = []
    for entity in profile:
        if entity.dxftype() == "LINE":
            geometry.append(f'<line class="profile" x1="{px(entity.dxf.start.x):.3f}" y1="{py(entity.dxf.start.y):.3f}" x2="{px(entity.dxf.end.x):.3f}" y2="{py(entity.dxf.end.y):.3f}"/>')
        else:
            start = math.radians(entity.dxf.start_angle)
            end = math.radians(entity.dxf.end_angle)
            sweep = (entity.dxf.end_angle - entity.dxf.start_angle) % 360.0
            points = []
            for index in range(13):
                angle = start + math.radians(sweep) * index / 12.0
                points.append(f"{px(entity.dxf.center.x + entity.dxf.radius*math.cos(angle)):.3f},{py(entity.dxf.center.y + entity.dxf.radius*math.sin(angle)):.3f}")
            geometry.append(f'<polyline class="profile" points="{" ".join(points)}"/>')
    for hole in spec["holes"]:
        geometry.append(f'<circle class="hole" cx="{px(hole["x"]):.3f}" cy="{py(hole["z"]):.3f}" r="{hole["diameter"]*scale/2.0:.3f}"/>')
        if "csk" in hole:
            geometry.append(f'<circle class="csk" cx="{px(hole["x"]):.3f}" cy="{py(hole["z"]):.3f}" r="{hole["csk"]*scale/2.0:.3f}"/>')
        geometry.append(svg_text(px(hole["x"])+8, py(hole["z"])-8, hole["fid"], "label"))
    geometry.extend([
        f'<line class="center" x1="{px(box.xmin)-25:.1f}" y1="{py(0):.1f}" x2="{px(box.xmax)+25:.1f}" y2="{py(0):.1f}"/>',
        f'<line class="center" x1="{px(0):.1f}" y1="{py(box.zmin)+25:.1f}" x2="{px(0):.1f}" y2="{py(box.zmax)-25:.1f}"/>',
    ])
    # Conventional overall dimensions with extension lines.
    dim_y = py(box.zmin) + 55
    geometry.extend([
        f'<line class="dim" x1="{px(box.xmin):.1f}" y1="{dim_y:.1f}" x2="{px(box.xmax):.1f}" y2="{dim_y:.1f}" marker-start="url(#arr)" marker-end="url(#arr)"/>',
        f'<line class="ext" x1="{px(box.xmin):.1f}" y1="{py(box.zmin):.1f}" x2="{px(box.xmin):.1f}" y2="{dim_y+12:.1f}"/>',
        f'<line class="ext" x1="{px(box.xmax):.1f}" y1="{py(box.zmin):.1f}" x2="{px(box.xmax):.1f}" y2="{dim_y+12:.1f}"/>',
        svg_text((px(box.xmin)+px(box.xmax))/2, dim_y-8, f"{box.xlen:.6f} OVERALL", "dimtxt", "middle"),
    ])
    dim_x = px(box.xmin) - 65
    geometry.extend([
        f'<line class="dim" x1="{dim_x:.1f}" y1="{py(box.zmin):.1f}" x2="{dim_x:.1f}" y2="{py(box.zmax):.1f}" marker-start="url(#arr)" marker-end="url(#arr)"/>',
        f'<line class="ext" x1="{dim_x-12:.1f}" y1="{py(box.zmin):.1f}" x2="{px(box.xmin):.1f}" y2="{py(box.zmin):.1f}"/>',
        f'<line class="ext" x1="{dim_x-12:.1f}" y1="{py(box.zmax):.1f}" x2="{px(box.xmin):.1f}" y2="{py(box.zmax):.1f}"/>',
        f'<text x="{dim_x-10:.1f}" y="{(py(box.zmin)+py(box.zmax))/2:.1f}" class="dimtxt" text-anchor="middle" transform="rotate(-90 {dim_x-10:.1f} {(py(box.zmin)+py(box.zmax))/2:.1f})">{box.zlen:.6f} OVERALL</text>',
    ])

    coordinate_rows = []
    for hole in spec["holes"]:
        feature = f'Ø{hole["diameter"]:.2f}' + (f' / CSK Ø{hole["csk"]:.2f} x 90°' if "csk" in hole else "")
        coordinate_rows.append((hole["fid"], f'{hole["x"]:+.2f}', f'{hole["z"]:+.2f}', feature))
    coord_svg = [svg_text(820, 170, "FEATURE COORDINATES (mm)", "section")]
    headers = ("ID", "X", "Z", "FEATURE")
    for col, value in zip((820, 900, 980, 1060), headers): coord_svg.append(svg_text(col, 202, value, "tablehead"))
    y = 234
    for row in coordinate_rows:
        for col, value in zip((820, 900, 980, 1060), row): coord_svg.append(svg_text(col, y, value, "tabletxt"))
        y += 30

    side_x, side_y = 860, 450
    side_w = max(90, box.ylen * 12)
    side_svg = [svg_text(820, 410, "SIDE / THICKNESS CONTROL", "section"), f'<rect class="profile" x="{side_x}" y="{side_y}" width="{side_w:.1f}" height="150"/>', svg_text(side_x+side_w/2, side_y+180, "9.525 NOMINAL; 9.00 MIN / 10.00 MAX", "dimtxt", "middle")]
    if part_id == "MV0-C07":
        side_svg.extend([f'<rect class="recess" x="{side_x}" y="{side_y}" width="12" height="150"/>', svg_text(side_x+side_w+35, side_y+75, "RAIL FACE RECESS 1.000 ±0.05", "tabletxt")])
    elif any("csk" in hole for hole in spec["holes"]):
        side_svg.append(svg_text(side_x+side_w+35, side_y+75, "COUNTERSINK SIDE: -Y FACE", "tabletxt"))

    note_lines = [
        "UNITS mm. DO NOT SCALE. PROFILE IS CONTROLLED BY THIS DRAWING, HASH-BOUND FINISHED DXF AND STEP TOGETHER.",
        f"PROFILE: {spec['profile_tolerance']}.",
        "MATERIAL CANDIDATE: ASTM B209 6061-T651, certified heat/lot; project minimum yield screen 240 MPa.",
        "FINISH: BARE AS-MACHINED; EDGE BREAK 0.20..0.50; BURR-FREE; NO COATING.",
        "BROAD-FACE FLATNESS <=0.15; OPPOSITE-FACE PARALLELISM <=0.10.",
        f"{spec['pattern_note']}.",
        f"{spec['special_note']}.",
        "INSPECTION FRAME ICF-01: PRIMARY A = +Y BROAD FACE (NON-COUNTERSINK FACE WHERE PRESENT); REGISTER X/Z BY 2D RIGID LEAST-SQUARES FIT OF THE FOUR SMALL INTERFACE-HOLE CENTERS TO THEIR NOMINAL PATTERN; NO SCALE; REPORT EACH RESIDUAL.",
        "ICF-01 IS A CANDIDATE CMM METHOD, NOT A RELEASED ASME Y14.5 DATUM REFERENCE FRAME. QUALIFIED DISPOSITION REQUIRED.",
        "RECEIVED MATING-PART DRY FIT, FASTENER SEATING, MTR, FAI AND QUALIFIED REVIEW REQUIRED. NO FILING, SLOTTING, BENDING OR FORCED ALIGNMENT.",
    ]
    if any("csk" in hole for hole in spec["holes"]):
        note_lines.insert(7, "COUNTERSINK RESIDUAL >=5.80; RECEIVED M5 HEAD PROUD <=0.05 / RECESS <=0.25; FUNCTIONAL-GAUGE RESULT REQUIRED.")
    notes_svg = [svg_text(40, 690, "GENERAL AND PART-SPECIFIC CONTROLS", "section")]
    note_y = 722
    for note_number, note in enumerate(note_lines, 1):
        numbered_note = f"{note_number}. {note}"
        for index, line in enumerate(wrap_svg(numbered_note, 145)):
            notes_svg.append(svg_text(55 if index else 40, note_y, line, "note"))
            note_y += 23
        note_y += 4

    table_y = max(1010, note_y + 15)
    table_svg = [svg_text(40, table_y, "SOURCE CONTROL BINDING", "section")]
    table_y += 32
    for col, value in zip((40, 155, 475, 925, 1250), ("CONTROL", "FEATURE", "NOMINAL", "TOLERANCE / LIMIT", "INSPECTION")):
        table_svg.append(svg_text(col, table_y, value, "tablehead"))
    table_y += 28
    for control in controls:
        nominal = control.get("nominal_mm") or control.get("nominal") or ""
        cells = (control["control_id"], control["feature"], nominal, control["tolerance_or_limit"], control["inspection"])
        lines = [wrap_svg(value.replace("/", "/ ") if index == 4 else value, width) for index, (value, width) in enumerate(zip(cells, (12, 34, 46, 36, 34)))]
        row_height = max(map(len, lines)) * 21 + 12
        table_svg.append(f'<rect class="row" x="30" y="{table_y-20}" width="1535" height="{row_height}"/>')
        for col, cell_lines in zip((40, 155, 475, 925, 1250), lines):
            for offset, line in enumerate(cell_lines): table_svg.append(svg_text(col, table_y + offset*21, line, "tabletxt"))
        table_y += row_height

    height = max(1400, table_y + 150)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-labelledby="title desc"><title id="title">{part_id} conventional drawing candidate</title><desc id="desc">Dimensioned front and side views, coordinate table, controls and release warning.</desc><defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#082f5b"/></marker></defs><style>
text{{font-family:Arial,sans-serif;fill:#082f5b}}.title{{font-size:30px;font-weight:700}}.subtitle{{font-size:18px}}.warning{{font-size:19px;font-weight:700;fill:white}}.section{{font-size:19px;font-weight:700}}.txt,.tabletxt,.note{{font-size:16px}}.label{{font-size:14px;font-weight:700}}.tablehead{{font-size:14px;font-weight:700}}.dimtxt{{font-size:16px;font-weight:700}}.profile{{fill:none;stroke:#082f5b;stroke-width:2}}.hole{{fill:white;stroke:#0d6fb8;stroke-width:2}}.csk{{fill:none;stroke:#d59600;stroke-width:2;stroke-dasharray:7 5}}.center{{stroke:#7d9bb5;stroke-width:1;stroke-dasharray:10 6}}.dim{{stroke:#082f5b;stroke-width:1.4}}.ext{{stroke:#486b86;stroke-width:1}}.recess{{fill:#ffd76a;stroke:#8b5f00;stroke-width:2}}.row{{fill:none;stroke:#9bb4c9;stroke-width:1}}
</style><rect width="1600" height="{height}" fill="#fff"/><rect width="1600" height="52" fill="#8b1e2d"/>{svg_text(800, 34, WARNING, 'warning', 'middle')}<rect x="20" y="70" width="1560" height="{height-90}" fill="none" stroke="#082f5b" stroke-width="3"/>{svg_text(40, 115, f'{part_id} — {spec["name"]}', 'title')}{svg_text(40, 148, f'{IDENTIFIER} · {CANDIDATE} · SCALE NTS · PROJECT X/Z FRONT VIEW', 'subtitle')}{''.join(geometry)}{''.join(coord_svg)}{''.join(side_svg)}{''.join(notes_svg)}{''.join(table_svg)}<rect x="1010" y="{height-115}" width="550" height="70" fill="#dff3ff" stroke="#082f5b"/>{svg_text(1030, height-85, 'STATUS: NONSELECTED CANDIDATE / FAI UNEXECUTED', 'tablehead')}{svg_text(1030, height-58, 'DRAWING, STEP AND DXF MUST REMAIN HASH-BOUND', 'tabletxt')}</svg>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    DXF_OUT.mkdir(parents=True, exist_ok=True)
    DRAWING_OUT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    controls = read_csv(DFM / "inspection-control-register.csv")
    control_by_id = {row["control_id"]: row for row in controls}
    assignments = {
        "MV0-C01": [f"ADP-{index:03d}" for index in range(1, 11)],
        "MV0-C04": [f"C04-{index:03d}" for index in range(1, 6)],
        "MV0-C05": [f"C05-{index:03d}" for index in range(1, 6)],
        "MV0-C06": ["STOP-001", "STOP-002", "STOP-005", "STOP-006"],
        "MV0-C07": ["STOP-003", "STOP-004", "STOP-005", "STOP-006"],
    }
    # Canonical one-row coverage retains the original 26 controls without duplicating STOP-005/006.
    canonical_control_drawing = {**{f"ADP-{index:03d}": "MV0-C01" for index in range(1, 11)}, **{f"C04-{index:03d}": "MV0-C04" for index in range(1, 6)}, **{f"C05-{index:03d}": "MV0-C05" for index in range(1, 6)}, "STOP-001": "MV0-C06", "STOP-002": "MV0-C06", "STOP-003": "MV0-C07", "STOP-004": "MV0-C07", "STOP-005": "MV0-C06;MV0-C07", "STOP-006": "MV0-C06;MV0-C07"}

    profile_rows = []
    binding_rows = []
    registration_rows = []
    drawing_paths: dict[str, Path] = {}
    dxf_paths: dict[str, Path] = {}
    for part_id, spec in PARTS.items():
        shape = cq.importers.importStep(str(spec["step"])).val()
        dxf_path = DXF_OUT / f"{part_id}_finished-profile-and-features_P0.1.dxf"
        drawing_path = DRAWING_OUT / f"{part_id}_conventional-drawing_P0.1.svg"
        profile_rows.append(make_finished_dxf(part_id, spec, shape, dxf_path))
        drawing_svg(part_id, spec, shape, dxf_path, [control_by_id[cid] for cid in assignments[part_id]], drawing_path)
        drawing_paths[part_id] = drawing_path
        dxf_paths[part_id] = dxf_path
        binding_rows.append({
            "part_id": part_id,
            "step_path": spec["step"].relative_to(ROOT).as_posix(), "step_sha256": sha256(spec["step"]),
            "finished_dxf_path": dxf_path.relative_to(ROOT).as_posix(), "finished_dxf_sha256": sha256(dxf_path),
            "drawing_path": drawing_path.relative_to(ROOT).as_posix(), "drawing_sha256": sha256(drawing_path),
            "configuration_state": "NONSELECTED P0.8 DRAWING CANDIDATE" if part_id != "MV0-C05" else "UNCHANGED P0.7 C05 IN P0.8 DRAWING CANDIDATE",
            "quotation_authorized": "FALSE", "fabrication_authorized": "FALSE", "warning": WARNING,
        })
        registration_rows.append({
            "part_id": part_id, "registration_id": "ICF-01", "primary_constraint": "+Y broad face establishes measurement Y plane; this is the non-countersink face where countersinks are present",
            "in_plane_registration": "2D rigid least-squares fit of four small interface-hole centers to nominal X/Z pattern; translation and rotation only; no scale",
            "required_output": "registered transform, each center residual, raw measured centers and calibration identity",
            "formal_gdt_state": "QUALIFIED REVIEW REQUIRED - NOT A RELEASED ASME Y14.5 DATUM REFERENCE FRAME",
            "physical_execution_state": "UNEXECUTED", "warning": WARNING,
        })
    write_csv(OUT / "profile-entity-certificate.csv", profile_rows)
    write_csv(OUT / "source-binding.csv", binding_rows)
    write_csv(OUT / "inspection-coordinate-register.csv", registration_rows)

    coverage_rows = []
    for row in controls:
        part_refs = canonical_control_drawing[row["control_id"]]
        paths = ";".join(drawing_paths[item].relative_to(ROOT).as_posix() for item in part_refs.split(";"))
        coverage_rows.append({
            "control_id": row["control_id"], "part_id_or_interface": part_refs, "source_table": row["source_table"], "source_row": row["source_row"],
            "drawing_path_or_paths": paths, "coverage_class": "DRAWING_EXPLICIT_NONPART_HOLD" if row["control_id"] == "STOP-006" else "DRAWING_EXPLICIT",
            "evidence": "numeric/qualitative control printed on the conventional candidate drawing; exact geometry remains hash-bound to drawing + DXF + STEP",
            "physical_execution_state": "UNEXECUTED", "fabrication_authorized": "FALSE", "warning": WARNING,
        })
    write_csv(OUT / "drawing-control-coverage.csv", coverage_rows)

    fai_rows = []
    for row in read_csv(DFM / "first-article-plan.csv"):
        part_id = row["part_id"]
        fai_rows.append({**row,
            "candidate_drawing_path": drawing_paths[part_id].relative_to(ROOT).as_posix(), "candidate_drawing_sha256": sha256(drawing_paths[part_id]),
            "finished_dxf_path": dxf_paths[part_id].relative_to(ROOT).as_posix(), "finished_dxf_sha256": sha256(dxf_paths[part_id]),
            "candidate_step_path": PARTS[part_id]["step"].relative_to(ROOT).as_posix(), "candidate_step_sha256": sha256(PARTS[part_id]["step"]),
        })
    write_csv(OUT / "first-article-drawing-map.csv", fai_rows)

    findings = [
        {"finding_id": "MDWG-F01", "priority": "MAJOR", "finding": "R135 C06/C07 pre-fillet DXFs did not encode finished R2 profiles.", "disposition": "Candidate DXFs now derive their complete LINE/ARC outer wires from the exact STEP solids; independent review remains open.", "status": "CANDIDATE CORRECTION - REVIEW OPEN"},
        {"finding_id": "MDWG-F02", "priority": "MAJOR", "finding": "R135 identified six schedule-bound controls rather than drawing-explicit controls.", "disposition": "All 26 source controls now map to explicit text/graphics on one or two conventional candidate drawings; independent drafting review remains open.", "status": "CANDIDATE CORRECTION - REVIEW OPEN"},
        {"finding_id": "MDWG-F03", "priority": "MAJOR", "finding": "The source set lacked an explicit repeatable part-coordinate registration method.", "disposition": "ICF-01 defines broad-face constraint plus rigid four-hole CMM registration, but formal ASME Y14.5 datum acceptance remains a qualified-review hold.", "status": "CANDIDATE CORRECTION - REVIEW OPEN"},
        {"finding_id": "MDWG-F04", "priority": "BLOCKER", "finding": "Drawing completeness cannot prove supplier capability, material, tolerance, fastener seating, received fit, strength, stop load, fatigue, stopping or safety.", "disposition": "Retain provider DFM, MTR, FAI, fit, proof, physical test and qualified release gates.", "status": "OPEN"},
    ]
    for row in findings: row["warning"] = WARNING
    write_csv(OUT / "finding-register.csv", findings)

    status = {
        "identifier": IDENTIFIER, "round": "R137", "date": "2026-08-09", "candidate_revision": CANDIDATE,
        "controlled_revision_remains": "HR-V0-ARM-ARCH-P0.7", "part_count": 5, "drawing_count": 5, "finished_dxf_count": 5,
        "step_binding_count": 5, "source_control_count": len(coverage_rows), "schedule_bound_control_count": 0,
        "first_article_operation_count": len(fai_rows), "inspection_registration_count": len(registration_rows), "finding_count": len(findings),
        "candidate_selected": False, "provider_contacted": False, "upload_authorized": False, "quotation_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    cards = []
    for row in binding_rows:
        part_id = row["part_id"]
        spec = PARTS[part_id]
        profile = next(item for item in profile_rows if item["part_id"] == part_id)
        cards.append(f'''<article class="card" data-search="{html.escape((part_id+' '+spec['name']).lower())}"><span class="badge">{part_id}</span><h3>{html.escape(spec['name'])}</h3><img src="../../../{row['drawing_path']}" alt="{part_id} conventional drawing candidate"><dl><dt>Finished profile</dt><dd>{profile['dxf_profile_line_count']} lines + {profile['dxf_profile_arc_count']} arcs</dd><dt>STEP/DXF extent delta</dt><dd>{profile['maximum_extent_delta_mm']} mm</dd><dt>Feature circles</dt><dd>{profile['through_hole_count']} through + {profile['nominal_countersink_count']} countersink</dd><dt>Configuration</dt><dd>{row['configuration_state']}</dd></dl><p><a href="../../../{row['drawing_path']}">Open drawing</a> · <a href="../../../{row['finished_dxf_path']}">Finished DXF</a> · <a href="../../../{row['step_path']}">Bound STEP</a></p></article>''')
    guide = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 manufacturing drawing candidate</title><style>
:root{{--ink:#082f5b;--blue:#0d6fb8;--sky:#dff3ff;--gold:#f4bd28;--paper:#f8fcff;--danger:#8b1e2d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.5 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{background:var(--danger);color:#fff;padding:12px 18px;font-size:16px;font-weight:800}}header{{padding:32px max(20px,calc((100% - 1220px)/2));background:linear-gradient(135deg,var(--sky),#fff);border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4.2rem);line-height:1.04;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.3rem)}}h3{{font-size:1.25rem}}main{{max-width:1220px;margin:auto;padding:24px}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}.metric,.card,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px;box-shadow:5px 5px 0 var(--sky)}}.metric strong{{display:block;font-size:2rem;color:var(--blue)}}.badge{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:13px;font-weight:800;background:var(--gold)}}.helper,small{{font-size:14px}}input{{width:100%;font:16px system-ui;padding:13px;border:2px solid var(--blue);border-radius:10px;margin-bottom:18px}}.card img{{display:block;width:100%;height:330px;object-fit:contain;background:#fff;border:1px solid #8ed5ff;border-radius:8px;margin:12px 0}}dl{{display:grid;grid-template-columns:minmax(120px,1fr) 1.5fr;gap:7px 12px}}dt{{font-weight:750}}dd{{margin:0}}a{{color:#07579f;font-weight:700}}footer{{padding:24px;background:var(--ink);color:#fff;font-size:14px;margin-top:35px}}@media(max-width:600px){{main{{padding:18px}}header{{padding:24px 18px}}.grid{{grid-template-columns:1fr}}.card img{{height:260px}}dl{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R137 · nonselected P0.8 drawing candidate</p><h1>The five custom parts now have one readable definition chain.</h1><p>Each card binds one conventional drawing, one finished-feature DXF and one STEP identity. The stop-part DXFs now contain the finished R2 arcs. This is a qualified-review package, not a supplier payload.</p></header><main><section><h2>Bounded result</h2><div class="metrics"><div class="metric"><strong>5</strong>conventional candidate drawings</div><div class="metric"><strong>5</strong>finished-feature DXFs</div><div class="metric"><strong>26/26</strong>source controls drawing-explicit</div><div class="metric"><strong>0</strong>fabrication releases</div></div></section><section><h2>Inspect each definition</h2><p class="helper">Search by part ID or name. Do not separate the drawing, DXF and STEP or upload them to a provider until configuration control and qualified review authorize it.</p><input id="search" aria-label="Find a drawing" placeholder="Find C07 or H104"><div class="grid">{''.join(cards)}</div></section><section class="panel"><h2>Machine-readable evidence</h2><p><a href="source-binding.csv">Source binding</a> · <a href="profile-entity-certificate.csv">Profile certificate</a> · <a href="drawing-control-coverage.csv">Control coverage</a> · <a href="inspection-coordinate-register.csv">Inspection registration</a> · <a href="first-article-drawing-map.csv">FAI map</a> · <a href="finding-register.csv">Findings</a> · <a href="package-status.json">Status</a></p></section></main><footer>{WARNING}</footer><script>const input=document.querySelector('#search');const cards=[...document.querySelectorAll('.card')];input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();cards.forEach(card=>card.hidden=!card.dataset.search.includes(q))}});</script></body></html>'''
    (OUT / "index.html").write_text(guide, encoding="utf-8", newline="\n")

    DOC.write_text(f'''# HR-V0 conventional manufacturing drawing candidate P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Candidate configuration: `{CANDIDATE}`

Controlled architecture remains: `HR-V0-ARM-ARCH-P0.7`

## Result

This package converts the R135/R136 file-definition findings into a five-part drawing candidate:

- five conventional SVG drawings with front/side views, overall dimensions, coordinate feature tables, exact source-control tables, thickness/finish/inspection notes and release warnings;
- five finished-profile/feature DXFs derived from the bound STEP outer wires;
- C06/C07 finished DXFs containing twelve LINE plus twelve ARC entities each, including the exact R2 finished corners absent from the earlier pre-fillet references;
- five hash-bound STEP/DXF/drawing triplets, using the R136 nominal-countersink candidates for C01/C04/C06/C07 and unchanged P0.7 C05;
- all 26 existing source controls mapped to explicit drawing content with zero schedule-bound rows;
- ICF-01 repeatable CMM registration for each part; and
- all 30 R134 FAI operations mapped to the candidate drawing, DXF and STEP identities while remaining unexecuted.

## Inspection registration

ICF-01 constrains the +Y broad face as the measurement Y plane; it is the non-countersink face where countersinks are present. It establishes X/Z using a rigid two-dimensional least-squares fit of the four small interface-hole centers to their nominal pattern. Translation and rotation are allowed; scale is prohibited; the transform, raw centers and each residual must be retained. This is a candidate CMM method, not a released ASME Y14.5 datum reference frame. Qualified drafting/metrology review must accept or replace it.

## Configuration boundary

The P0.8 drawing candidate is not selected. P0.7 remains controlled. No provider may receive or quote the files until independent review accepts the drawing/DXF/STEP semantics, formal datum treatment, material controls, inspection plan and supplier inquiry boundary.

## What remains open

Drawing completeness does not prove supplier capability, certified material, achieved tolerance, fastener seating, received fit, structural or stop strength, fatigue, impact, stopping, guarding or safety. Provider DFM, MTR, FAI, CMM records, received-article dry fit, proof testing and qualified release remain mandatory.
''', encoding="utf-8", newline="\n")

    manifest_rows = []
    for generated_path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if generated_path.is_file() and generated_path != GENERATED_SOURCE_MANIFEST:
            manifest_rows.append({
                "file": generated_path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_sha256(generated_path),
                "revision": "HR-V0-MECH-R0.1-PRELIMINARY",
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, manifest_rows)

    print(f"Generated {IDENTIFIER}: 5 drawings, 5 finished DXFs, {len(coverage_rows)} explicit controls, {len(fai_rows)} mapped FAI rows")
    print(WARNING)


if __name__ == "__main__":
    main()
