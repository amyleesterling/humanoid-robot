"""Generate the HR-30 P0.1 1:1 nonstructural whole-body fit-check kit.

Every physical fabrication candidate is converted from its authoritative
individual STEP file into a full-scale STL.  The prints are dimensional and
packaging fit articles only; they are never structural robot parts and confer
no powered-work, standing, walking, or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import itertools
import json
import math
import shutil
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
MANUFACTURING = WHOLE / "manufacturing-files"
OUT = WHOLE / "full-scale-fit-check-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-FULL-SCALE-FIT-CHECK-P0.1"
WARNING = "PRELIMINARY - 1:1 NONSTRUCTURAL FIT ARTICLES ONLY - NOT APPROVED FOR LOAD BEARING, STANDING, WALKING, POWERED TESTING, MOTION, OR ENERGIZATION"
MODULES = ["H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"]
PART_COUNT = 98
MESH_LINEAR_TOLERANCE_MM = 0.15
MESH_ANGULAR_TOLERANCE_RAD = 0.15
BED_X_MM = 220.0
BED_Y_MM = 220.0
BED_Z_MM = 250.0
BED_MARGIN_MM = 5.0
PLATE_GAP_MM = 5.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_binary_stl(path: Path) -> tuple[int, tuple[float, float, float], tuple[float, float, float]]:
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"short STL: {path}")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    if triangle_count <= 0 or len(data) != 84 + 50 * triangle_count:
        raise RuntimeError(f"invalid binary STL framing: {path}")
    lower = [math.inf, math.inf, math.inf]
    upper = [-math.inf, -math.inf, -math.inf]
    for index in range(triangle_count):
        values = struct.unpack_from("<12f", data, 84 + 50 * index)
        for vertex in (values[3:6], values[6:9], values[9:12]):
            if not all(math.isfinite(value) for value in vertex):
                raise RuntimeError(f"non-finite STL vertex: {path}")
            for axis, value in enumerate(vertex):
                lower[axis] = min(lower[axis], value)
                upper[axis] = max(upper[axis], value)
    return triangle_count, tuple(lower), tuple(upper)


def read_binary_stl(path: Path) -> list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], int]]:
    data = path.read_bytes()
    if len(data) < 84:
        raise RuntimeError(f"short STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    if count <= 0 or len(data) != 84 + 50 * count:
        raise RuntimeError(f"invalid binary STL framing: {path}")
    triangles = []
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + 50 * index)
        triangles.append((values[0:3], values[3:6], values[6:9], values[9:12], values[12]))
    return triangles


def determinant(matrix: tuple[tuple[int, int, int], ...]) -> int:
    a, b, c = matrix
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def orientation_matrices() -> list[tuple[tuple[int, int, int], ...]]:
    matrices = []
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            rows = []
            for row, source_axis in enumerate(permutation):
                values = [0, 0, 0]
                values[source_axis] = signs[row]
                rows.append(tuple(values))
            matrix = tuple(rows)
            if determinant(matrix) == 1:
                matrices.append(matrix)
    if len(matrices) != 24:
        raise RuntimeError("expected 24 right-handed orthogonal print orientations")
    return matrices


ORIENTATIONS = orientation_matrices()


def apply_matrix(vector: tuple[float, float, float], matrix: tuple[tuple[int, int, int], ...]) -> tuple[float, float, float]:
    return tuple(sum(matrix[row][axis] * vector[axis] for axis in range(3)) for row in range(3))


def orient_for_bed(raw_path: Path, output_path: Path) -> dict:
    triangles = read_binary_stl(raw_path)
    vertices = [vertex for _normal, a, b, c, _attribute in triangles for vertex in (a, b, c)]
    candidates = []
    for matrix in ORIENTATIONS:
        transformed = [apply_matrix(vertex, matrix) for vertex in vertices]
        lower = tuple(min(vertex[axis] for vertex in transformed) for axis in range(3))
        upper = tuple(max(vertex[axis] for vertex in transformed) for axis in range(3))
        size = tuple(upper[axis] - lower[axis] for axis in range(3))
        if size[0] <= BED_X_MM - 2 * BED_MARGIN_MM + 1e-5 and size[1] <= BED_Y_MM - 2 * BED_MARGIN_MM + 1e-5 and size[2] <= BED_Z_MM + 1e-5:
            negative_count = sum(value < 0 for row in matrix for value in row)
            candidates.append(((size[2], max(size[0], size[1]), size[0] * size[1], negative_count, matrix), matrix, lower, size))
    if not candidates:
        raise RuntimeError(f"no orientation fits generic {BED_X_MM:g} x {BED_Y_MM:g} x {BED_Z_MM:g} mm envelope: {raw_path}")
    _rank, matrix, lower, size = min(candidates, key=lambda candidate: candidate[0])
    translation = (BED_MARGIN_MM - lower[0], BED_MARGIN_MM - lower[1], -lower[2])
    header = b"HR-30 1:1 BED-NORMALIZED NONSTRUCTURAL FIT ARTICLE"[:80].ljust(80, b"\0")
    with output_path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(triangles)))
        for normal, a, b, c, attribute in triangles:
            new_normal = apply_matrix(normal, matrix)
            new_vertices = []
            for vertex in (a, b, c):
                rotated = apply_matrix(vertex, matrix)
                new_vertices.append(tuple(rotated[axis] + translation[axis] for axis in range(3)))
            handle.write(struct.pack("<12fH", *new_normal, *new_vertices[0], *new_vertices[1], *new_vertices[2], attribute))
    count, output_lower, output_upper = parse_binary_stl(output_path)
    output_size = tuple(output_upper[axis] - output_lower[axis] for axis in range(3))
    if count != len(triangles) or any(abs(output_size[axis] - size[axis]) > 1e-4 for axis in range(3)):
        raise RuntimeError(f"bed-orientation writeback drift: {raw_path}")
    return {"matrix": matrix, "translation": translation, "lower": output_lower, "upper": output_upper, "size": output_size}


def mesh_volume_mm3(path: Path) -> float:
    volume6 = 0.0
    for _normal, a, b, c, _attribute in read_binary_stl(path):
        cross = (b[1] * c[2] - b[2] * c[1], b[2] * c[0] - b[0] * c[2], b[0] * c[1] - b[1] * c[0])
        volume6 += a[0] * cross[0] + a[1] * cross[1] + a[2] * cross[2]
    return abs(volume6) / 6.0


def pack_module_plates(part_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    plate_rows: list[dict] = []
    placement_rows: list[dict] = []
    for module in MODULES:
        parts = sorted((row for row in part_rows if row["module"] == module), key=lambda row: (-max(float(row["oriented_bbox_x_mm"]), float(row["oriented_bbox_y_mm"])), -float(row["oriented_bbox_x_mm"]) * float(row["oriented_bbox_y_mm"]), row["part_id"]))
        plates: list[dict] = []
        for part in parts:
            choices = []
            for plate_index, plate in enumerate(plates):
                for rotated in (False, True):
                    width = float(part["oriented_bbox_y_mm"] if rotated else part["oriented_bbox_x_mm"])
                    depth = float(part["oriented_bbox_x_mm"] if rotated else part["oriented_bbox_y_mm"])
                    for shelf_index, shelf in enumerate(plate["shelves"]):
                        if depth <= shelf["height"] + 1e-6 and shelf["x"] + width <= BED_X_MM - BED_MARGIN_MM + 1e-6:
                            choices.append((plate_index, shelf["y"], shelf["x"], shelf_index, rotated, width, depth, False))
                    y = BED_MARGIN_MM if not plate["shelves"] else plate["shelves"][-1]["y"] + plate["shelves"][-1]["height"] + PLATE_GAP_MM
                    if y + depth <= BED_Y_MM - BED_MARGIN_MM + 1e-6:
                        choices.append((plate_index, y, BED_MARGIN_MM, len(plate["shelves"]), rotated, width, depth, True))
            if not choices:
                plates.append({"shelves": []})
                plate_index = len(plates) - 1
                width = float(part["oriented_bbox_x_mm"])
                depth = float(part["oriented_bbox_y_mm"])
                rotated = False
                if width > BED_X_MM - 2 * BED_MARGIN_MM or depth > BED_Y_MM - 2 * BED_MARGIN_MM:
                    width, depth, rotated = depth, width, True
                if width > BED_X_MM - 2 * BED_MARGIN_MM or depth > BED_Y_MM - 2 * BED_MARGIN_MM:
                    raise RuntimeError(f"part cannot fit packing envelope: {part['part_id']}")
                choice = (plate_index, BED_MARGIN_MM, BED_MARGIN_MM, 0, rotated, width, depth, True)
            else:
                choice = min(choices, key=lambda item: (item[0], item[1], item[2], item[4]))
            plate_index, y, x, shelf_index, rotated, width, depth, new_shelf = choice
            plate = plates[plate_index]
            if new_shelf:
                plate["shelves"].append({"y": y, "height": depth, "x": x + width + PLATE_GAP_MM})
            else:
                plate["shelves"][shelf_index]["x"] = x + width + PLATE_GAP_MM
            placement_rows.append({
                "plate_id": f"FC-{module}-P{plate_index+1:02d}", "module": module, "part_id": part["part_id"],
                "stl_path": part["stl_path"], "x_mm": f"{x:.3f}", "y_mm": f"{y:.3f}", "rotation_z_deg": 90 if rotated else 0,
                "placed_width_mm": f"{width:.3f}", "placed_depth_mm": f"{depth:.3f}", "part_height_mm": part["oriented_bbox_z_mm"],
                "physical_layout_executed": "NO", "warning": WARNING,
            })
        for index, _plate in enumerate(plates, 1):
            assigned = [row for row in placement_rows if row["plate_id"] == f"FC-{module}-P{index:02d}"]
            plate_rows.append({
                "plate_id": f"FC-{module}-P{index:02d}", "module": module, "printer_envelope_mm": f"{BED_X_MM:g} x {BED_Y_MM:g} x {BED_Z_MM:g}",
                "part_count": len(assigned), "parts": ";".join(row["part_id"] for row in assigned),
                "layout_svg": f"plate-layouts/FC-{module}-P{index:02d}.svg", "gcode_released": "NO", "slicer_profile_selected": "NO", "printed": "NO", "warning": WARNING,
            })
    return plate_rows, placement_rows


def plate_svg(plate: dict, placements: list[dict]) -> str:
    scale = 3.0
    shapes = []
    for row in placements:
        x, y = float(row["x_mm"]), float(row["y_mm"])
        width, depth = float(row["placed_width_mm"]), float(row["placed_depth_mm"])
        label = html.escape(row["part_id"].replace(f"{row['module']}_", ""))
        shapes.append(f'<g><rect x="{x*scale:.2f}" y="{y*scale:.2f}" width="{width*scale:.2f}" height="{depth*scale:.2f}" rx="6" fill="#d9f2ff" stroke="#0b4f91" stroke-width="2"/><text x="{(x+width/2)*scale:.2f}" y="{(y+depth/2)*scale:.2f}" text-anchor="middle" dominant-baseline="middle" font-size="12" font-weight="700" fill="#071d36">{label}</text></g>')
    size = int(BED_X_MM * scale)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size+54}" viewBox="0 0 {size} {size+54}" role="img"><title>{plate['plate_id']} candidate 220 mm print layout</title><rect width="{size}" height="{size}" fill="#f7fbff" stroke="#071d36" stroke-width="4"/>{''.join(shapes)}<text x="{size/2}" y="{size+30}" text-anchor="middle" font-size="16" font-weight="700" fill="#982520">Candidate layout only · slicer profile and collision preview required</text></svg>'''


def module_name(module: str) -> str:
    return {
        "H01": "Head", "N01": "Neck", "T01": "Torso", "P01": "Pelvis",
        "A01": "Left arm", "G01": "Left hand", "A02": "Right arm", "G02": "Right hand",
        "L01": "Left leg", "F01": "Left foot", "L02": "Right leg", "F02": "Right foot",
    }[module]


def assembly_rows(counts: Counter) -> list[dict]:
    rows = []
    step = 1
    stages = [
        ("PREP", "Freeze source hashes; inspect printer, material lot, tools and unpowered workspace", "all modules", "No damaged or unidentified material; configuration recorded"),
        ("PREP", "Print one calibration coupon before robot parts and record dimensional offsets", "all modules", "Coupon results recorded; offsets remain development-only"),
    ]
    for stage, action, module, acceptance in stages:
        rows.append({"step_id": f"FC-T{step:03d}", "stage": stage, "module": module, "action": action, "objective_record": acceptance, "performed_by": "UNASSIGNED", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING})
        step += 1
    for module in MODULES:
        name = module_name(module)
        actions = [
            ("PRINT", f"Print all {counts[module]} {name} fit articles at 1:1 scale", "All files complete; material/print log attached"),
            ("INSPECT", f"Measure X/Y/Z envelopes and critical interfaces for {name}", "Measurements entered; deviations and rework recorded"),
            ("ASSEMBLE", f"Dry-assemble {name} with inert dummy or unpowered candidate hardware", "No force-fit damage; interfaces accessible; no electrical source present"),
            ("ROUTE", f"Pull string or sacrificial sleeving through {name} harness corridors and service loops", "Route, clamp access, bend and service clearance observations recorded"),
        ]
        for stage, action, acceptance in actions:
            rows.append({"step_id": f"FC-T{step:03d}", "stage": stage, "module": module, "action": action, "objective_record": acceptance, "performed_by": "UNASSIGNED", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING})
            step += 1
    final = [
        ("INTEGRATE", "Join all twelve modules as one complete recognizable humanoid while supported by an independent fixture", "All modules visible; fixture carries every gravity/fall load"),
        ("SWEEP", "Manually sweep every one of the 25 unpowered joint axes through the proposed fit-check range", "Binding, collision, cover, cable and access observations recorded per axis"),
        ("PACKAGE", "Trial-fit all installed-equipment envelopes, service panels and hand mechanisms", "Every interface has a recorded result or open issue"),
        ("CLOSE", "Photograph the complete supported fit-check and freeze the as-built issue register", "Configuration and unresolved issues recorded; no production release inferred"),
    ]
    for stage, action, acceptance in final:
        rows.append({"step_id": f"FC-T{step:03d}", "stage": stage, "module": "whole robot", "action": action, "objective_record": acceptance, "performed_by": "UNASSIGNED", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING})
        step += 1
    return rows


def inspection_rows(part_rows: list[dict]) -> list[dict]:
    rows = []
    for part in part_rows:
        for characteristic, method in [
            ("X/Y/Z printed envelope", "caliper/tape method and uncertainty SELECTION REQUIRED"),
            ("mating/interface fit", "controlled mating hardware or gauge SELECTION REQUIRED"),
            ("holes/slots/inserts", "go/no-go pins or received hardware SELECTION REQUIRED"),
            ("surface/warp/support damage", "visual plus flatness method SELECTION REQUIRED"),
        ]:
            rows.append({
                "inspection_id": f"FC-I{len(rows)+1:04d}", "part_id": part["part_id"], "module": part["module"],
                "characteristic": characteristic, "source_nominal": part["source_bbox_mm"] if characteristic.startswith("X/Y/Z") else "native STEP geometry",
                "method": method, "acceptance_limit": "SELECTION REQUIRED - fit-check development result, not production tolerance",
                "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE", "warning": WARNING,
            })
    return rows


def render_svg(counts: Counter) -> str:
    labels = [("H01", 400, 60), ("N01", 400, 130), ("T01", 400, 210), ("P01", 400, 340),
              ("A01", 245, 225), ("G01", 105, 330), ("A02", 555, 225), ("G02", 695, 330),
              ("L01", 325, 455), ("F01", 305, 680), ("L02", 475, 455), ("F02", 455, 680)]
    boxes = []
    for module, x, y in labels:
        width, height = (120, 55) if module in {"H01", "N01"} else (145, 90)
        if module in {"G01", "G02", "F01", "F02"}:
            width, height = 125, 70
        boxes.append(f'<g><rect x="{x-width/2}" y="{y}" width="{width}" height="{height}" rx="14" fill="#d9f2ff" stroke="#0b4f91" stroke-width="3"/><text x="{x}" y="{y+26}" text-anchor="middle" font-size="18" font-weight="700" fill="#071d36">{module} · {module_name(module)}</text><text x="{x}" y="{y+49}" text-anchor="middle" font-size="16" fill="#0b3765">{counts[module]} STL parts</text></g>')
    lines = '<path d="M400 115V130M400 185V210M400 300V340M327 260H245M473 260H555M173 300L105 330M627 300L695 330M365 430L325 455M435 430L475 455M325 545L305 680M475 545L455 680" fill="none" stroke="#f2b91d" stroke-width="10" stroke-linecap="round"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="780" viewBox="0 0 800 780" role="img" aria-labelledby="title desc"><title id="title">HR-30 full-scale fit-check architecture</title><desc id="desc">Twelve modules and the count of full-scale nonstructural STL parts in each.</desc><rect width="800" height="780" rx="24" fill="#f7fbff"/>{lines}{''.join(boxes)}<text x="400" y="760" text-anchor="middle" font-size="16" font-weight="700" fill="#982520">Unpowered fit only · independent support required · no load-bearing use</text></svg>'''


def render_index(part_rows: list[dict], counts: Counter, plate_rows: list[dict], bundle_rows: list[dict]) -> str:
    sections = []
    for module in MODULES:
        bundle = next(row for row in bundle_rows if row["module"] == module)
        table_rows = "".join(
            f'<tr><td>{html.escape(r["part_id"])}</td><td>{html.escape(r["role"])}</td><td>{html.escape(r["source_bbox_mm"])}</td><td>{html.escape(r["oriented_bbox_x_mm"])} × {html.escape(r["oriented_bbox_y_mm"])} × {html.escape(r["oriented_bbox_z_mm"])} mm</td><td>{int(r["triangle_count"]):,}</td><td><a href="{html.escape(r["stl_path"])}">bed-ready STL</a></td></tr>'
            for r in part_rows if r["module"] == module
        )
        sections.append(f'<details><summary>{module} · {module_name(module)} · {counts[module]} parts</summary><p><a href="{html.escape(bundle["zip_path"])}">Download the complete {module} module STL bundle</a></p><div class="tablewrap"><table><thead><tr><th>Part</th><th>Role</th><th>Source envelope</th><th>Bed-oriented envelope</th><th>Triangles</th><th>File</th></tr></thead><tbody>{table_rows}</tbody></table></div></details>')
    layouts = "".join(f'<article class="card"><h3>{html.escape(row["plate_id"])}</h3><p>{row["part_count"]} parts · generic {html.escape(row["printer_envelope_mm"])} envelope</p><a href="{html.escape(row["layout_svg"])}"><img src="{html.escape(row["layout_svg"])}" alt="Candidate bed layout for {html.escape(row["plate_id"])}"></a></article>' for row in plate_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 full-scale fit-check P0.1</title><style>
:root{{--deep:#071d36;--navy:#0b4f91;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:20px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}.card,details,.diagram{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:16px 0;min-width:0}}.card img{{display:block;width:100%;height:auto}}.metric{{font-size:clamp(38px,5vw,58px);font-weight:900;color:var(--navy)}}.diagram img{{display:block;max-width:800px;width:100%;margin:auto}}summary{{cursor:pointer;font-size:20px;font-weight:900;color:var(--navy)}}.tablewrap{{overflow-x:auto;margin-top:14px}}table{{border-collapse:collapse;width:100%;min-width:980px;font-size:16px}}th,td{{padding:12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9b;font-weight:800}}.boundary{{border-left:8px solid var(--red)}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}main{{padding-inline:12px}}}}
</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>Project Button · HR-30 whole-body P0.1</p><h1>Print the whole robot before machining the whole robot.</h1><p>These 98 one-to-one meshes are now rigidly bed-normalized from the authoritative CAD: minimum Z is 0 mm, minimum X/Y is 5 mm, and no mesh is left floating in whole-robot coordinates.</p></header><main><section class="grid"><article class="card"><div class="metric">98</div><p>source-bound bed-ready STL parts</p></article><article class="card"><div class="metric">12</div><p>complete body-module bundles</p></article><article class="card"><div class="metric">{len(plate_rows)}</div><p>generic 220 × 220 × 250 mm candidate plates</p></article><article class="card boundary"><div class="metric">0</div><p>parts printed or physically accepted</p></article></section><section><h2>One complete supported humanoid</h2><div class="diagram"><img src="fit-check-architecture.svg" alt="Diagram of all twelve HR-30 modules and their fit-check STL counts"><p>The complete print is for dimension, service, equipment and harness-route discovery. An independent fixture must support it. Printed parts receive no structural, fall-restraint, standing, walking, impact or powered-test credit.</p></div></section><section><h2>Execution records</h2><div class="grid"><article class="card"><a href="fit-check-assembly-traveler.csv">Assembly traveler</a><p>Prepare, print, inspect, dry-assemble, route and manually sweep.</p></article><article class="card"><a href="fit-check-inspection-register.csv">Inspection register</a><p>Four controlled checks for every part; all currently not executed.</p></article><article class="card"><a href="plate-layout-register.csv">Plate placements</a><p>Recorded candidate X/Y position and 0°/90° bed rotation for every part.</p></article><article class="card"><a href="printer-envelope-compatibility.csv">Printer envelopes</a><p>Geometry-only compatibility against four generic build volumes; machine/profile suitability remains open.</p></article></div></section><section><h2>Candidate module plate layouts</h2><p>These layouts use bounding-box separation with a 5 mm margin and gap. They are a starting point for a real slicer collision/support preview, not released G-code.</p><div class="grid">{layouts}</div></section><section><h2>Download by module</h2>{''.join(sections)}</section><section><h2>Hard boundary</h2><div class="card boundary"><p>Do not stand, hang, power, walk or load this printed assembly. Do not install live batteries or energized electronics. Do not treat print fit as proof of metal strength, tolerance, fatigue, fall behavior, electrical protection or functional safety. Production CAD, material, drawings, DFM, FAI, testing and qualified approvals remain separate.</p><small>{html.escape(WARNING)}</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "full_scale_fit_check_package_present": True,
        "full_scale_fit_check_part_count": PART_COUNT,
        "full_scale_fit_check_stl_count": PART_COUNT,
        "full_scale_fit_check_module_count": len(MODULES),
        "full_scale_fit_check_bed_normalized_part_count": PART_COUNT,
        "full_scale_fit_check_built_part_count": 0,
        "full_scale_fit_check_inspected_part_count": 0,
        "full_scale_fit_check_physically_validated": False,
        "full_scale_fit_check_structural_use_permitted": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme_path = WHOLE / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-FULL-SCALE-FIT-CHECK-P01-README-START -->", "<!-- HR30-FULL-SCALE-FIT-CHECK-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Full-scale unpowered fit-check kit\n\nThe [full-scale fit-check guide](full-scale-fit-check-p0.1/index.html) provides one source-bound, bed-normalized STL for every one of the **{PART_COUNT} physical CAD parts** across all twelve body modules, plus twelve module ZIP bundles and candidate generic 220 x 220 x 250 mm plate layouts. Every file is 1:1, placed at Z=0 with a 5 mm X/Y margin, and retains a recorded rigid transform back to its native STEP source. Zero parts have been printed or accepted; no G-code or slicer profile is released. Printed articles may not carry robot, standing, walking, fall, powered-test or impact loads.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    if marker in text:
        text = text.replace(marker, block + marker)
    else:
        text = text.rstrip() + "\n\n" + block
    readme_path.write_text(text, encoding="utf-8", newline="\n")

    page_path = WHOLE / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-FULL-SCALE-FIT-CHECK-P01-START -->", "<!-- HR30-FULL-SCALE-FIT-CHECK-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="full-scale-fit-check"><h2>The entire robot now has a bed-normalized unpowered fit-check kit</h2><div class="grid"><article class="card pass"><div class="metric">{PART_COUNT}</div><p>Source-bound 1:1 STLs at Z=0.</p></article><article class="card pass"><div class="metric">12</div><p>Head-to-feet module ZIP bundles.</p></article><article class="card hold"><div class="metric">0</div><p>Parts printed or physically accepted.</p></article><article class="card hold"><h3>No released G-code</h3><p>Printer, material, supports and slicer profile still require physical selection.</p></article></div><p><a href="full-scale-fit-check-p0.1/index.html">Open the full-scale fit-check guide</a> · <a href="full-scale-fit-check-p0.1/fit-check-part-register.csv">Part and transform register</a> · <a href="full-scale-fit-check-p0.1/print-build-plate-register.csv">Candidate plate register</a>.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    if marker in text:
        text = text.replace(marker, section + marker)
    elif "</main>" in text:
        text = text.replace("</main>", section + "</main>", 1)
    else:
        raise RuntimeError("root page main boundary missing")
    page_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_register = MANUFACTURING / "part-file-register.csv"
    source_rows = read_csv(source_register)
    if len(source_rows) != PART_COUNT or set(r["module"] for r in source_rows) != set(MODULES):
        raise RuntimeError("authoritative 98-part manufacturing source drift")

    part_rows: list[dict] = []
    for source in source_rows:
        source_step = MANUFACTURING / source["step_path"]
        if not source_step.is_file() or sha(source_step) != source["step_sha256"]:
            raise RuntimeError(f"source STEP/hash drift: {source['part_id']}")
        shape = cq.importers.importStep(str(source_step))
        if shape is None or shape.val() is None or shape.val().Volume() <= 0:
            raise RuntimeError(f"invalid source STEP solid: {source['part_id']}")
        # Capture exact B-Rep bounds before STL tessellation. Open Cascade may
        # retain a triangulation deflection on the in-memory shape after export,
        # which can expand a later BoundingBox() query by that deflection.
        cad_bbox = shape.val().BoundingBox()
        stl = OUT / "stl" / source["module"] / f"{source['part_id']}.stl"
        raw_stl = OUT / ".mesh-work" / source["module"] / f"{source['part_id']}.stl"
        stl.parent.mkdir(parents=True, exist_ok=True)
        raw_stl.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(shape, str(raw_stl), tolerance=MESH_LINEAR_TOLERANCE_MM, angularTolerance=MESH_ANGULAR_TOLERANCE_RAD)
        raw_sha = sha(raw_stl)
        orientation = orient_for_bed(raw_stl, stl)
        triangles, lower, upper = parse_binary_stl(stl)
        mesh_bbox = tuple(upper[i] - lower[i] for i in range(3))
        matrix = orientation["matrix"]
        translation = orientation["translation"]
        mesh_volume = mesh_volume_mm3(stl)
        part_rows.append({
            "part_id": source["part_id"], "module": source["module"], "role": source["role"],
            "source_step_path": source_step.relative_to(ROOT).as_posix(), "source_step_sha256": sha(source_step),
            "source_bbox_mm": source["bbox_mm"], "source_volume_mm3": source["volume_mm3"],
            "stl_path": stl.relative_to(OUT).as_posix(), "stl_sha256": sha(stl), "stl_bytes": stl.stat().st_size,
            "source_tessellation_sha256": raw_sha, "triangle_count": triangles, "mesh_volume_mm3": f"{mesh_volume:.6f}",
            "orientation_matrix_row_major": " ".join(str(value) for row in matrix for value in row),
            "translation_xyz_mm": " ".join(f"{value:.9f}" for value in translation),
            "bed_min_xyz_mm": " ".join(f"{value:.6f}" for value in lower), "bed_max_xyz_mm": " ".join(f"{value:.6f}" for value in upper),
            "oriented_bbox_x_mm": f"{mesh_bbox[0]:.6f}", "oriented_bbox_y_mm": f"{mesh_bbox[1]:.6f}", "oriented_bbox_z_mm": f"{mesh_bbox[2]:.6f}",
            "step_bbox_x_mm": f"{cad_bbox.xlen:.6f}", "step_bbox_y_mm": f"{cad_bbox.ylen:.6f}", "step_bbox_z_mm": f"{cad_bbox.zlen:.6f}",
            "scale": "1:1 millimetres", "bed_normalized": "YES - X/Y MIN 5 MM; Z MIN 0 MM", "intended_use": "UNPOWERED DIMENSIONAL/PACKAGING FIT ARTICLE ONLY",
            "built_quantity": 0, "inspection_result": "NOT EXECUTED", "structural_credit": "NONE", "warning": WARNING,
        })

    shutil.rmtree(OUT / ".mesh-work")
    counts = Counter(r["module"] for r in part_rows)
    write_csv(OUT / "fit-check-part-register.csv", part_rows)
    write_csv(OUT / "source-binding.csv", [{"source_id": "FC-S01", "path": source_register.relative_to(ROOT).as_posix(), "sha256": sha(source_register), "role": "authoritative 98-part native STEP/file register", "warning": WARNING}, {"source_id": "FC-S02", "path": "hr30/whole-body-p0.1/HR-30_integrated_whole_robot_candidate.step", "sha256": sha(WHOLE / "HR-30_integrated_whole_robot_candidate.step"), "role": "recognizable complete whole-robot assembly reference", "warning": WARNING}])
    plate_rows, placement_rows = pack_module_plates(part_rows)
    write_csv(OUT / "print-build-plate-register.csv", plate_rows)
    write_csv(OUT / "plate-layout-register.csv", placement_rows)
    layout_root = OUT / "plate-layouts"
    layout_root.mkdir()
    for plate in plate_rows:
        placements = [row for row in placement_rows if row["plate_id"] == plate["plate_id"]]
        (OUT / plate["layout_svg"]).write_text(plate_svg(plate, placements), encoding="utf-8", newline="\n")

    def fits_envelope(row: dict, x: float, y: float, z: float) -> bool:
        dimensions = (float(row["step_bbox_x_mm"]), float(row["step_bbox_y_mm"]), float(row["step_bbox_z_mm"]))
        return any(dimensions[p[0]] <= x + 1e-6 and dimensions[p[1]] <= y + 1e-6 and dimensions[p[2]] <= z + 1e-6 for p in itertools.permutations(range(3)))

    envelope_rows = []
    for envelope_id, x, y, z in [("FC-ENV-180", 180.0, 180.0, 180.0), ("FC-ENV-220", 220.0, 220.0, 250.0), ("FC-ENV-250X210", 250.0, 210.0, 220.0), ("FC-ENV-256", 256.0, 256.0, 256.0)]:
        fitting = [row for row in part_rows if fits_envelope(row, x, y, z)]
        excluded = sorted(row["part_id"] for row in part_rows if row not in fitting)
        envelope_rows.append({"envelope_id": envelope_id, "build_volume_mm": f"{x:g} x {y:g} x {z:g}", "fit_part_count": len(fitting), "excluded_part_count": len(excluded), "excluded_parts": ";".join(excluded) if excluded else "NONE", "basis": "axis-aligned rigid 90-degree orientation; geometry envelope only", "printer_or_slicer_selected": "NO", "warning": WARNING})
    write_csv(OUT / "printer-envelope-compatibility.csv", envelope_rows)

    bundle_root = OUT / "module-bundles"
    bundle_root.mkdir()
    bundle_rows = []
    for module in MODULES:
        archive = bundle_root / f"HR30-{module}-fit-check-stl-p0.1.zip"
        module_parts = [row for row in part_rows if row["module"] == module]
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for row in module_parts:
                bundle.write(OUT / row["stl_path"], arcname=f"{module}/{Path(row['stl_path']).name}")
            bundle.writestr(f"{module}/README.txt", f"HR-30 {module} 1:1 bed-normalized nonstructural fit articles.\n{WARNING}\n")
        bundle_rows.append({"bundle_id": f"FC-ZIP-{module}", "module": module, "part_count": len(module_parts), "zip_path": archive.relative_to(OUT).as_posix(), "zip_bytes": archive.stat().st_size, "zip_sha256": sha(archive), "built": "NO", "warning": WARNING})
    write_csv(OUT / "module-bundle-register.csv", bundle_rows)
    write_csv(OUT / "fit-check-print-settings.csv", [
        {"setting_id": "FC-PS01", "parameter": "scale", "development_candidate": "100% / 1:1 millimetres", "release_state": "FIXED FOR FIT-CHECK", "basis": "source STEP dimensional comparison", "warning": WARNING},
        {"setting_id": "FC-PS02", "parameter": "material", "development_candidate": "PETG or PLA", "release_state": "SELECTION REQUIRED PER PART/PRINTER", "basis": "nonstructural fit article; temperature/warp/availability must be recorded", "warning": WARNING},
        {"setting_id": "FC-PS03", "parameter": "layer height", "development_candidate": "0.20 mm", "release_state": "DEVELOPMENT CANDIDATE", "basis": "fit-check resolution/time trade", "warning": WARNING},
        {"setting_id": "FC-PS04", "parameter": "perimeters", "development_candidate": "3 to 4", "release_state": "DEVELOPMENT CANDIDATE", "basis": "handling durability only; no structural credit", "warning": WARNING},
        {"setting_id": "FC-PS05", "parameter": "infill", "development_candidate": "15% to 25%", "release_state": "DEVELOPMENT CANDIDATE", "basis": "handling/warp trial; no structural credit", "warning": WARNING},
        {"setting_id": "FC-PS06", "parameter": "orientation/support", "development_candidate": "rigid lowest-Z bed orientation encoded; support and interface-critical reorientation remain open", "release_state": "BED FRAME FIXED; SLICER REVIEW REQUIRED", "basis": "recorded right-handed 90-degree transform; interface accuracy, support scars and warp require preview", "warning": WARNING},
        {"setting_id": "FC-PS07", "parameter": "hole/insert compensation", "development_candidate": "NONE RELEASED", "release_state": "CALIBRATION COUPON REQUIRED", "basis": "printer/material/process specific", "warning": WARNING},
    ])
    traveler = assembly_rows(counts)
    inspections = inspection_rows(part_rows)
    write_csv(OUT / "fit-check-assembly-traveler.csv", traveler)
    write_csv(OUT / "fit-check-inspection-register.csv", inspections)
    write_csv(OUT / "fit-check-issue-register.csv", [{"issue_id": f"FC-ISS-{module}", "module": module, "issue": "NO PHYSICAL FIT-CHECK EXECUTED; record dimensional, interface, access, collision and routing issues here", "severity": "OPEN EXECUTION HOLD", "disposition": "NOT EXECUTED", "owner": "UNASSIGNED", "evidence": "NONE", "warning": WARNING} for module in MODULES])
    holds = [
        ("FC-H01", "No fit-check parts printed", "received printed-part records, material lot, slicer profile and photographs"),
        ("FC-H02", "No dimensional inspections executed", "calibrated measurements and acceptance criteria for every part/interface"),
        ("FC-H03", "Print material, orientation, supports and compensation unresolved", "printer/material calibration and part-specific process disposition"),
        ("FC-H04", "No whole-body dry assembly or supported manual sweep executed", "independently supported twelve-module assembly and 25-axis inspection records"),
        ("FC-H05", "Installed-equipment, service-access and harness-pull fits unverified", "received hardware/dummies, pull-string routes, clamp access and issue dispositions"),
        ("FC-H06", "Fit articles have no structural or production equivalence", "released metal/production CAD, drawings, materials, DFM, FAI, capacity and physical validation remain separate"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN - NOT EXECUTED", "warning": WARNING} for i, item, evidence in holds])
    (OUT / "fit-check-architecture.svg").write_text(render_svg(counts), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_index(part_rows, counts, plate_rows, bundle_rows), encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "physical_part_count": len(part_rows), "stl_count": len(part_rows),
        "module_count": len(counts), "triangle_count": sum(int(r["triangle_count"]) for r in part_rows),
        "mesh_linear_tolerance_mm": MESH_LINEAR_TOLERANCE_MM, "mesh_angular_tolerance_rad": MESH_ANGULAR_TOLERANCE_RAD,
        "bed_normalized_stl_count": len(part_rows), "generic_printer_envelope_mm": [BED_X_MM, BED_Y_MM, BED_Z_MM],
        "candidate_plate_count": len(plate_rows), "module_bundle_count": len(bundle_rows), "gcode_released": False, "slicer_profile_selected": False,
        "assembly_traveler_step_count": len(traveler), "inspection_record_count": len(inspections), "open_hold_count": len(holds),
        "built_part_count": 0, "inspected_part_count": 0, "assembled_module_count": 0, "whole_body_fit_check_executed": False,
        "source_step_geometry_verified": True, "stl_binary_structure_verified": True, "fit_physically_validated": False,
        "structural_credit": False, "production_equivalence": False, "procurement_authority": False, "production_fabrication_authority": False,
        "assembly_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "fit-check-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 full-scale fit-check P0.1\n\n**{WARNING}**\n\nThis package contains {PART_COUNT} source-bound, 1:1, bed-normalized STL fit articles covering all twelve physical HR-30 modules, plus {len(plate_rows)} generic 220 x 220 x 250 mm candidate plate layouts and twelve module ZIP bundles. Every transform is recorded in `fit-check-part-register.csv`; every mesh has minimum Z=0 mm and X/Y=5 mm. Use [index.html](index.html) for the interactive guide. Zero parts have been printed or accepted. No G-code or printer/slicer profile is released.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "full-scale-fit-check-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root()
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
