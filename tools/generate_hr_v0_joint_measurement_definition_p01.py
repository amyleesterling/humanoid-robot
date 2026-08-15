#!/usr/bin/env python3
"""Generate R256 source-bound HR-V0 joint measurement definitions."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_joint_stack_fixture_p01 as fixture  # noqa: E402

ID = "HR-V0-JOINT-MEAS-DEF-P0.1"
CID = "HR-V0-CONFIG-REC-P0.20"
ROUND = "R256"
WARNING = fixture.WARNING
OUT = ROOT / "test-fixtures/hr-v0/joint-measurement-definition-p0.1"
REL = ROOT / "release/hr-v0/joint-measurement-definition-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.19"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.20"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.20"
SOURCES = fixture.SOURCE_STEP


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def warned(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(row, warning=WARNING) for row in rows]


def manifest(directory: Path) -> None:
    rows = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file() and item.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)})
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], rows)


def transform_point(article: str, xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = xyz
    if article == "XM540":
        return (1.75 - z, y, x)
    if article == "S102":
        return (x, -z, y)
    return xyz


def transform_direction(article: str, xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = xyz
    if article == "XM540":
        return (-z, y, x)
    if article == "S102":
        return (x, -z, y)
    return xyz


def canonical_direction(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    values = list(xyz)
    for value in values:
        if abs(value) > 1e-8:
            if value < 0:
                values = [-entry for entry in values]
            break
    return tuple(0.0 if abs(entry) < 5e-10 else entry for entry in values)


def fmt_vec(xyz: tuple[float, float, float]) -> str:
    return ",".join(f"{value:.6f}" for value in xyz)


def plane_feature(article: str, shape: cq.Shape, face_index: int, feature_id: str, role: str, hsi: str, method: str) -> dict[str, object]:
    face = shape.Faces()[face_index - 1]
    if face.geomType() != "PLANE":
        raise ValueError(f"{article} face {face_index} is not planar")
    adaptor = BRepAdaptor_Surface(face.wrapped)
    plane = adaptor.Plane()
    direction = plane.Axis().Direction()
    point = transform_point(article, face.Center().toTuple())
    axis = canonical_direction(transform_direction(article, (direction.X(), direction.Y(), direction.Z())))
    signature = f"PLANE|A={face.Area():.9f}|P={fmt_vec(point)}|N={fmt_vec(axis)}"
    return {
        "feature_id": feature_id,
        "article": article,
        "source_face_index_1_based": face_index,
        "geometry_type": "PLANE",
        "nominal_point_joint_xyz_mm": fmt_vec(point),
        "nominal_axis_or_normal_joint_xyz": fmt_vec(axis),
        "nominal_radius_mm": "",
        "nominal_area_mm2": f"{face.Area():.9f}",
        "geometric_signature": signature,
        "measurement_role": role,
        "hsi_route": hsi,
        "method_route": method,
        "status": "CONTROLLED CAD NOMINAL ONLY - RECEIVED FEATURE MATCH REQUIRED",
    }


def cylinder_feature(article: str, shape: cq.Shape, face_index: int, feature_id: str, role: str, hsi: str, method: str) -> dict[str, object]:
    face = shape.Faces()[face_index - 1]
    if face.geomType() != "CYLINDER":
        raise ValueError(f"{article} face {face_index} is not cylindrical")
    cylinder = BRepAdaptor_Surface(face.wrapped).Cylinder()
    location = cylinder.Axis().Location()
    direction = cylinder.Axis().Direction()
    point = transform_point(article, (location.X(), location.Y(), location.Z()))
    axis = canonical_direction(transform_direction(article, (direction.X(), direction.Y(), direction.Z())))
    radius = cylinder.Radius()
    signature = f"CYLINDER|A={face.Area():.9f}|P={fmt_vec(point)}|D={fmt_vec(axis)}|R={radius:.9f}"
    return {
        "feature_id": feature_id,
        "article": article,
        "source_face_index_1_based": face_index,
        "geometry_type": "CYLINDER",
        "nominal_point_joint_xyz_mm": fmt_vec(point),
        "nominal_axis_or_normal_joint_xyz": fmt_vec(axis),
        "nominal_radius_mm": f"{radius:.9f}",
        "nominal_area_mm2": f"{face.Area():.9f}",
        "geometric_signature": signature,
        "measurement_role": role,
        "hsi_route": hsi,
        "method_route": method,
        "status": "CONTROLLED CAD NOMINAL ONLY - RECEIVED FEATURE MATCH REQUIRED",
    }


def unique_axis_features(article: str, shape: cq.Shape, *, axis_index: int, radius: float, prefix: str, role: str, hsi: str) -> list[dict[str, object]]:
    candidates: list[tuple[tuple[float, ...], int]] = []
    for face_index, face in enumerate(shape.Faces(), 1):
        if face.geomType() != "CYLINDER":
            continue
        cylinder = BRepAdaptor_Surface(face.wrapped).Cylinder()
        if not math.isclose(cylinder.Radius(), radius, abs_tol=1e-7):
            continue
        direction = cylinder.Axis().Direction()
        axis = canonical_direction(transform_direction(article, (direction.X(), direction.Y(), direction.Z())))
        if not math.isclose(abs(axis[axis_index]), 1.0, abs_tol=1e-7):
            continue
        location = cylinder.Axis().Location()
        point = transform_point(article, (location.X(), location.Y(), location.Z()))
        transverse = tuple(round(point[index], 6) for index in range(3) if index != axis_index)
        key = (*transverse, round(radius, 6))
        candidates.append((key, face_index))
    chosen: dict[tuple[float, ...], int] = {}
    for key, face_index in candidates:
        chosen[key] = min(face_index, chosen.get(key, face_index))
    rows = []
    for count, (key, face_index) in enumerate(sorted(chosen.items()), 1):
        rows.append(cylinder_feature(article, shape, face_index, f"{prefix}-{count:02d}", role, hsi, "JSM2-M01"))
    return rows


def derive_features() -> tuple[dict[str, cq.Shape], list[dict[str, object]]]:
    native = {article: cq.importers.importStep(str(path)).val() for article, path in SOURCES.items()}
    rows = [
        plane_feature("XM540", native["XM540"], 58, "XM540-PL-OUTER-OUTPUT", "external output-side axial plane candidate", "HSI-004/006", "JSM2-M01/M02"),
        plane_feature("XM540", native["XM540"], 317, "XM540-PL-OUTER-IDLER", "external idler-side axial plane candidate", "HSI-004/006", "JSM2-M01/M02"),
        plane_feature("H101", native["H101"], 11, "H101-PL-MOVING-PLUS", "moving-frame positive-X outer axial plane", "HSI-003/005", "JSM2-M01/M02"),
        plane_feature("H101", native["H101"], 76, "H101-PL-MOVING-MINUS", "moving-frame negative-X outer axial plane", "HSI-003/005", "JSM2-M01/M02"),
        plane_feature("H101", native["H101"], 1, "H101-PL-ANGLE-REF", "moving external angle-reference candidate", "HSI-013/014", "JSM2-M03"),
        plane_feature("S102", native["S102"], 32, "S102-PL-FIXED-PLUS", "fixed-frame positive-X outer axial plane", "HSI-004/006", "JSM2-M01/M02"),
        plane_feature("S102", native["S102"], 4, "S102-PL-FIXED-MINUS", "fixed-frame negative-X outer axial plane", "HSI-004/006", "JSM2-M01/M02"),
        plane_feature("S102", native["S102"], 20, "S102-PL-ANGLE-REF", "fixed external angle-reference candidate", "HSI-013/014", "JSM2-M03"),
        cylinder_feature("XM540", native["XM540"], 100, "XM540-AXIS-OUTPUT", "output-side joint-axis realization candidate", "HSI-003/004/005/006", "JSM2-M01/M02"),
        cylinder_feature("XM540", native["XM540"], 315, "XM540-AXIS-IDLER", "idler-side joint-axis realization candidate", "HSI-003/004/005/006", "JSM2-M01/M02"),
        cylinder_feature("H101", native["H101"], 15, "H101-AXIS-PLUS", "moving-frame positive-X coaxial bore candidate", "HSI-003/005", "JSM2-M01/M02"),
        cylinder_feature("H101", native["H101"], 81, "H101-AXIS-MINUS", "moving-frame negative-X coaxial bore candidate", "HSI-003/005", "JSM2-M01/M02"),
        cylinder_feature("S102", native["S102"], 19, "S102-AXIS-SIDE-MINUS", "fixed-frame negative-X side-hole axis candidate", "HSI-004/006/009/011", "JSM2-M01/M02"),
        cylinder_feature("S102", native["S102"], 25, "S102-AXIS-SIDE-PLUS", "fixed-frame positive-X side-hole axis candidate", "HSI-004/006/009/011", "JSM2-M01/M02"),
    ]
    rows += unique_axis_features("XM540", native["XM540"], axis_index=0, radius=1.0, prefix="XM540-IDLER-PATTERN", role="actuator idler-side cylindrical pattern candidate; manufacturer function allocation required", hsi="HSI-009/010/011/012")
    rows += unique_axis_features("H101", native["H101"], axis_index=0, radius=1.25, prefix="H101-SIDE-PATTERN", role="moving-frame side cylindrical pattern candidate; manufacturer function allocation required", hsi="HSI-010/012")
    rows += unique_axis_features("H101", native["H101"], axis_index=1, radius=1.25, prefix="H101-FLANGE-PATTERN", role="moving-frame flange cylindrical pattern candidate; manufacturer function allocation required", hsi="HSI-010/012")
    rows += unique_axis_features("S102", native["S102"], axis_index=1, radius=1.25, prefix="S102-FLANGE-PATTERN", role="fixed-frame flange cylindrical pattern candidate; manufacturer function allocation required", hsi="HSI-009/011")
    return native, rows


def axial_svg(features: list[dict[str, object]]) -> str:
    ids = ["XM540-PL-OUTER-IDLER", "S102-PL-FIXED-MINUS", "H101-PL-MOVING-MINUS", "H101-PL-MOVING-PLUS", "S102-PL-FIXED-PLUS", "XM540-PL-OUTER-OUTPUT"]
    indexed = {row["feature_id"]: row for row in features}
    colors = {"XM540": "#50a9df", "H101": "#f3bd28", "S102": "#164f86"}
    lines = []
    for offset, feature_id in enumerate(ids):
        row = indexed[feature_id]
        x = float(str(row["nominal_point_joint_xyz_mm"]).split(",")[0])
        px = 520 + x * 13
        y2 = 140 + (offset % 3) * 58
        lines.append(f"<line x1='{px:.1f}' y1='300' x2='{px:.1f}' y2='{y2}' stroke='{colors[str(row['article'])]}' stroke-width='5'/><circle cx='{px:.1f}' cy='300' r='7' fill='{colors[str(row['article'])]}'/><text x='{px + 8:.1f}' y='{y2 - 8}' font-size='13'>{html.escape(feature_id)}</text><text x='{px + 8:.1f}' y='{y2 + 10}' font-size='13'>x={x:.3f} mm</text>")
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1120' height='440' viewBox='0 0 1120 440'><rect width='1120' height='440' fill='#f8fbfe'/><text x='36' y='34' font-family='system-ui' font-size='14' font-weight='800' fill='#8d1721'>{WARNING}</text><text x='36' y='70' font-family='system-ui' font-size='26' font-weight='700' fill='#092f57'>Nominal axial feature index — not an inspection drawing</text><text x='36' y='101' font-family='system-ui' font-size='16' fill='#102338'>Joint-frame X positions derived from exact controlled STEP. Received surfaces and acceptance limits remain unverified.</text><line x1='110' y1='320' x2='930' y2='320' stroke='#102338' stroke-width='3'/><text x='940' y='326' font-family='system-ui' font-size='15'>+X</text><g transform='translate(0,20)' font-family='system-ui' fill='#102338'>{''.join(lines)}</g><g transform='translate(0,20)' font-family='system-ui' font-size='14'><rect x='36' y='350' width='18' height='18' fill='#50a9df'/><text x='64' y='365'>XM540</text><rect x='160' y='350' width='18' height='18' fill='#f3bd28'/><text x='188' y='365'>H101 moving frame</text><rect x='370' y='350' width='18' height='18' fill='#164f86'/><text x='398' y='365'>S102 fixed frame</text></g></svg>"""


def pattern_svg(features: list[dict[str, object]]) -> str:
    panels = [
        ("H101-SIDE-PATTERN", "H101 side pattern", 50, 105, 1, 2),
        ("H101-FLANGE-PATTERN", "H101 flange pattern", 390, 105, 0, 2),
        ("S102-FLANGE-PATTERN", "S102 flange pattern", 730, 105, 0, 2),
    ]
    contents = []
    for prefix, title, ox, oy, ai, bi in panels:
        rows = [row for row in features if str(row["feature_id"]).startswith(prefix)]
        dots = []
        for row in rows:
            xyz = [float(value) for value in str(row["nominal_point_joint_xyz_mm"]).split(",")]
            x = ox + 145 + xyz[ai] * 7
            y = oy + 150 - xyz[bi] * 7
            label = str(row["feature_id"]).split("-")[-1]
            dots.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='7'/><text x='{x + 9:.1f}' y='{y + 5:.1f}' font-size='12'>{label}</text>")
        contents.append(f"<g><rect x='{ox}' y='{oy}' width='310' height='315' rx='14' fill='#fff' stroke='#8eb9d8' stroke-width='2'/><text x='{ox + 18}' y='{oy + 32}' font-size='19' font-weight='700'>{title}</text><line x1='{ox + 35}' y1='{oy + 150}' x2='{ox + 275}' y2='{oy + 150}' stroke='#9bb4c7'/><line x1='{ox + 145}' y1='{oy + 55}' x2='{ox + 145}' y2='{oy + 275}' stroke='#9bb4c7'/><g fill='#f3bd28' stroke='#092f57' stroke-width='2'>{''.join(dots)}</g><text x='{ox + 18}' y='{oy + 295}' font-size='13'>Labels are feature suffixes; exact coordinates are in CSV.</text></g>")
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1100' height='510' viewBox='0 0 1100 510'><rect width='1100' height='510' fill='#f8fbfe'/><g transform='translate(0,30)' font-family='system-ui' fill='#102338'><text x='50' y='-4' font-size='14' font-weight='800' fill='#8d1721'>{WARNING}</text><text x='50' y='45' font-size='26' font-weight='700' fill='#092f57'>Source-derived cylindrical pattern index</text><text x='50' y='74' font-size='16'>Candidate surfaces only. Hole function, thread identity, tolerance and received conformity are not inferred from STEP.</text>{''.join(contents)}</g></svg>"""


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(features: list[dict[str, object]], measurands: list[dict[str, object]], hsi: list[dict[str, object]], selections: list[dict[str, object]]) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><script type='module' src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js'></script><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(24px,2.5vw,36px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2rem;font-weight:800;color:var(--blue)}}model-viewer{{width:100%;height:620px;background:var(--sky);border-radius:12px}}img{{display:block;width:100%;height:auto;border:1px solid var(--line)}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:1050px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:white;position:sticky;top:0}}@media(max-width:700px){{main{{padding:12px}}model-viewer{{height:430px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Joint measurement definition P0.1</h1><p>Exact source-feature indices for repeatable metrology bids. CAD nominals are references, not received-part measurements or acceptance limits.</p></header><main><div class='cards'><div class='card'><div class='big'>{len(features)}</div>source-bound features</div><div class='card'><div class='big'>{len(measurands)}</div>measurement characteristics</div><div class='card'><div class='big'>20</div>HSI routes retained</div><div class='card'><div class='big'>0</div>executed results or approvals</div></div><section><h2>Inspect exact controlled geometry</h2><model-viewer src='HR-V0_joint-measurement-definition_P0.1_review.glb' alt='Exact ROBOTIS joint stack geometry with source-feature markers' camera-controls shadow-intensity='0.8'></model-viewer><p>Blue, gray and gold bodies are exact controlled vendor geometry in the project joint frame. Marker spheres identify indexed feature points; they do not define probe paths, tolerances, or acceptance.</p></section><section><h2>Axial references</h2><img src='axial-feature-index.svg' alt='Nominal axial feature positions'></section><section><h2>Attachment-pattern references</h2><img src='attachment-pattern-index.svg' alt='Nominal cylindrical pattern feature positions'></section>{table('Feature register',features,['feature_id','article','source_face_index_1_based','geometry_type','nominal_point_joint_xyz_mm','nominal_axis_or_normal_joint_xyz','nominal_radius_mm','measurement_role','hsi_route','status'])}{table('Measurand definitions',measurands,['characteristic_id','hsi_id','method_id','received_article_scope','feature_ids','definition','cad_nominal','reported_result','acceptance_limit','state'])}{table('HSI closure map',hsi,['hsi_id','definition_coverage','feature_or_characteristic_ids','closure_boundary','state'])}{table('Selections and evidence',selections,['selection_id','selection','evidence_required','state'])}<section><h2>Boundary</h2><p>Face indices are one-based indices in the exact source STEP under the recorded CadQuery/OpenCascade environment. Geometric signatures and source hashes provide the machine-checkable identity. A provider must match each received feature, disclose any mismatch, and return raw evidence. Qualified reviewers must still select datums, methods, uncertainty and acceptance limits. No physical work is authorized.</p></section></main></body></html>"""


def main() -> None:
    for directory in (OUT, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    OUT.mkdir(parents=True)
    native, features = derive_features()

    source_rows = []
    labels = {"XM540": "XMHD-540.N101.I101.STP", "H101": "FR13-H101K.stp", "S102": "FR13-S102K.stp"}
    for count, article in enumerate(("XM540", "H101", "S102"), 1):
        path = SOURCES[article]
        shape = native[article]
        box = shape.BoundingBox()
        source_rows.append({"source_id": f"R256-SRC-{count:02d}", "article": article, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "source_filename": labels[article], "shape_faces": len(shape.Faces()), "shape_solids": len(shape.Solids()), "native_bbox_mm": f"{box.xmin:.6f},{box.xmax:.6f},{box.ymin:.6f},{box.ymax:.6f},{box.zmin:.6f},{box.zmax:.6f}", "use": "CONTROLLED NOMINAL REFERENCE ONLY"})
    source_rows.extend([
        {"source_id": "R256-SRC-04", "article": "METHOD", "path": "release/hr-v0/joint-stack-metrology-p0.2/package-status.json", "sha256": sha(ROOT / "release/hr-v0/joint-stack-metrology-p0.2/package-status.json"), "source_filename": "R254 method contract", "shape_faces": "", "shape_solids": "", "native_bbox_mm": "", "use": "CURRENT UNEXECUTED METHOD ROUTE"},
        {"source_id": "R256-SRC-05", "article": "INQUIRY", "path": "release/hr-v0/lot-a-inquiry-p0.2/package-status.json", "sha256": sha(ROOT / "release/hr-v0/lot-a-inquiry-p0.2/package-status.json"), "source_filename": "R255 inquiry contract", "shape_faces": "", "shape_solids": "", "native_bbox_mm": "", "use": "CURRENT UNSENT INQUIRY ROUTE"},
    ])
    transforms = [
        {"article": "XM540", "source_to_joint_transform": "[0,0,-1,1.75; 0,1,0,0; 1,0,0,0; 0,0,0,1]", "derivation": "actuator_to_joint_frame followed by Rx(+90 deg)", "status": "CONTROLLED NOMINAL REGISTRATION - RECEIVED REGISTRATION OPEN"},
        {"article": "H101", "source_to_joint_transform": "identity", "derivation": "native H101 STEP is the project joint frame", "status": "CONTROLLED NOMINAL REGISTRATION - RECEIVED REGISTRATION OPEN"},
        {"article": "S102", "source_to_joint_transform": "[1,0,0,0; 0,0,-1,0; 0,1,0,0; 0,0,0,1]", "derivation": "Rx(+90 deg)", "status": "CONTROLLED NOMINAL REGISTRATION - RECEIVED REGISTRATION OPEN"},
    ]
    measurand_specs = [
        ("R256-MZ-001", "HSI-003", "JSM2-M01/M02", "J1 received H101 and assembled stack", "H101-PL-MOVING-PLUS; H101-PL-MOVING-MINUS", "fit both received outer planes; report signed X locations and absolute separation", "53.000000 mm outer-plane separation"),
        ("R256-MZ-002", "HSI-003", "JSM2-M02", "J1 received assembled stack", "H101-AXIS-PLUS; H101-AXIS-MINUS; XM540-AXIS-OUTPUT; XM540-AXIS-IDLER", "fit each accessible cylinder; report axes, residuals, coaxiality screen and accepted constructed joint axis", "all source axes nominally parallel to +X and transverse origin y=z=0"),
        ("R256-MZ-003", "HSI-004", "JSM2-M01/M02", "J1 received S102, XM540 and assembled stack", "S102-PL-FIXED-PLUS; S102-PL-FIXED-MINUS", "fit both received S102 outer side planes; report signed X locations and separation", "48.000000 mm outer-plane separation"),
        ("R256-MZ-004", "HSI-004", "JSM2-M02", "J1 received assembled stack", "H101-PL-MOVING-PLUS; H101-PL-MOVING-MINUS; S102-PL-FIXED-PLUS; S102-PL-FIXED-MINUS", "report signed plus-side and minus-side assembled axial clearances using accepted plane fits", "2.500000 mm nominal clearance each side; not an acceptance limit"),
        ("R256-MZ-005", "HSI-005", "JSM2-M01/M02", "J2 received H101 and assembled stack", "H101-PL-MOVING-PLUS; H101-PL-MOVING-MINUS", "repeat R256-MZ-001 on separately identified J2 articles", "53.000000 mm outer-plane separation"),
        ("R256-MZ-006", "HSI-005", "JSM2-M02", "J2 received assembled stack", "H101-AXIS-PLUS; H101-AXIS-MINUS; XM540-AXIS-OUTPUT; XM540-AXIS-IDLER", "repeat R256-MZ-002 on separately identified J2 articles", "all source axes nominally parallel to +X and transverse origin y=z=0"),
        ("R256-MZ-007", "HSI-006", "JSM2-M01/M02", "J2 received S102, XM540 and assembled stack", "S102-PL-FIXED-PLUS; S102-PL-FIXED-MINUS", "repeat R256-MZ-003 on separately identified J2 articles", "48.000000 mm outer-plane separation"),
        ("R256-MZ-008", "HSI-006", "JSM2-M02", "J2 received assembled stack", "H101-PL-MOVING-PLUS; H101-PL-MOVING-MINUS; S102-PL-FIXED-PLUS; S102-PL-FIXED-MINUS", "repeat R256-MZ-004 on separately identified J2 articles", "2.500000 mm nominal clearance each side; not an acceptance limit"),
        ("R256-MZ-009", "HSI-007", "JSM2-M04", "J1 received complete temporary stack", "all exterior source surfaces plus registered raw scan", "report full two-or-more-orientation point clouds, transforms, residuals and bounding envelope; configured cable/guard remain absent", "source-only bbox is a comparison aid, not a received envelope"),
        ("R256-MZ-010", "HSI-008", "JSM2-M04", "J2 received complete temporary stack", "all exterior source surfaces plus registered raw scan", "repeat R256-MZ-009 on separately identified J2 articles", "source-only bbox is a comparison aid, not a received envelope"),
        ("R256-MZ-011", "HSI-009", "JSM2-M01", "J1 received S102 and XM540", "S102-FLANGE-PATTERN-*; S102-AXIS-SIDE-*; XM540-IDLER-PATTERN-*", "report every matched cylindrical axis, radius screen, pattern fit, residual and any unmatched source/received feature", "source coordinates in feature-register.csv; intended use not inferred"),
        ("R256-MZ-012", "HSI-010", "JSM2-M01", "J1 received H101", "H101-SIDE-PATTERN-*; H101-FLANGE-PATTERN-*", "report every matched cylindrical axis, radius screen, pattern fit, residual and any unmatched source/received feature", "source coordinates in feature-register.csv; intended use not inferred"),
        ("R256-MZ-013", "HSI-011", "JSM2-M01", "J2 received S102 and XM540", "S102-FLANGE-PATTERN-*; S102-AXIS-SIDE-*; XM540-IDLER-PATTERN-*", "repeat R256-MZ-011 on separately identified J2 articles", "source coordinates in feature-register.csv; intended use not inferred"),
        ("R256-MZ-014", "HSI-012", "JSM2-M01", "J2 received H101", "H101-SIDE-PATTERN-*; H101-FLANGE-PATTERN-*", "repeat R256-MZ-012 on separately identified J2 articles", "source coordinates in feature-register.csv; intended use not inferred"),
        ("R256-MZ-015", "HSI-013", "JSM2-M03", "J1 temporary stack", "S102-PL-ANGLE-REF; H101-PL-ANGLE-REF; accepted constructed joint axis", "report externally measured signed angle about accepted axis, both approach directions, applied hand force and backlash estimator", "source reference normals are collinear/opposed at nominal zero; zero convention requires qualified acceptance"),
        ("R256-MZ-016", "HSI-014", "JSM2-M03", "J2 temporary stack", "S102-PL-ANGLE-REF; H101-PL-ANGLE-REF; accepted constructed joint axis", "repeat R256-MZ-015 on separately identified J2 articles", "source reference normals are collinear/opposed at nominal zero; zero convention requires qualified acceptance"),
        ("R256-MZ-017", "HSI-017", "JSM2-M05", "J1 loose and frozen assembled identities", "no CAD volume conversion permitted", "report direct balance readings, tare, repetitions, corrections and uncertainty", "BLANK - STEP volume is not accepted mass"),
        ("R256-MZ-018", "HSI-018", "JSM2-M05", "J2 loose and frozen assembled identities", "no CAD volume conversion permitted", "report direct balance readings, tare, repetitions, corrections and uncertainty; effective/reflected inertia remains external", "BLANK - STEP volume is not accepted mass or inertia"),
    ]
    measurands = [{"characteristic_id": cid, "hsi_id": hsi, "method_id": method, "received_article_scope": scope, "feature_ids": ids, "definition": definition, "cad_nominal": nominal, "reported_result": "", "expanded_uncertainty": "", "acceptance_limit": "SELECTION REQUIRED", "state": "NOT EXECUTED"} for cid, hsi, method, scope, ids, definition, nominal in measurand_specs]
    hsi_rows = []
    for number in range(1, 21):
        hsi_id = f"HSI-{number:03d}"
        mapped = [row["characteristic_id"] for row in measurands if row["hsi_id"] == hsi_id]
        if number in (1, 2):
            coverage, ids = "IDENTITY ONLY - NO GEOMETRIC CLOSURE", "R255 supplier/receiving records"
        elif mapped:
            coverage, ids = "EXACT CAD REFERENCE FEATURES DEFINED; RECEIVED RESULT OPEN", "; ".join(mapped)
        else:
            coverage, ids = "EXTERNAL TO THIS SOURCE-GEOMETRY PACKAGE", ""
        hsi_rows.append({"hsi_id": hsi_id, "definition_coverage": coverage, "feature_or_characteristic_ids": ids, "closure_boundary": "received execution, raw data, uncertainty, qualified acceptance and downstream configuration binding", "state": "OPEN"})
    selections_specs = [
        ("R256-SEL-01", "received-to-source feature-match rule", "provider proposal, mismatch disclosure and qualified acceptance"),
        ("R256-SEL-02", "accepted joint-axis construction", "feature accessibility, fit algorithm, residual limits and uncertainty"),
        ("R256-SEL-03", "accepted plane-fit and outlier rule", "sampling plan, filtering disclosure, residuals and uncertainty"),
        ("R256-SEL-04", "manufacturer function allocation for cylindrical patterns", "current written ROBOTIS evidence; geometry alone is insufficient"),
        ("R256-SEL-05", "received article instance allocation to J1 and J2", "serial/lot/configuration record"),
        ("R256-SEL-06", "measurement support and probe/scan accessibility", "provider method proposal and no-bias evidence"),
        ("R256-SEL-07", "M01/M02/M03/M04/M05 uncertainty budgets", "numeric component budgets, traceability and validation"),
        ("R256-SEL-08", "acceptance limits for every characteristic", "downstream fit/load/tolerance analysis and qualified approval"),
        ("R256-SEL-09", "external zero-angle convention", "signed physical datum and method definition"),
        ("R256-SEL-10", "temporary assembly hardware/torque/reuse", "manufacturer or qualified mechanical instruction"),
        ("R256-SEL-11", "provider and performing facility", "accepted R255 bid, calibration, scope and commercial decision"),
        ("R256-SEL-12", "physical work authorization", "configuration-specific signed authority after all entry gates"),
    ]
    selections = [{"selection_id": sid, "selection": selection, "evidence_required": evidence, "state": "SELECTION REQUIRED"} for sid, selection, evidence in selections_specs]
    results = [{"result_id": f"{row['characteristic_id']}-RESULT", "characteristic_id": row["characteristic_id"], "article_serial_or_lot": "", "method_revision": "", "raw_evidence_uri": "", "raw_evidence_sha256": "", "reported_result": "", "expanded_uncertainty": "", "coverage_factor": "", "reviewer_disposition": "NOT EXECUTED", "approver": ""} for row in measurands]
    acceptance = [{"acceptance_id": f"R256-ACC-{index:02d}", "criterion": row["selection"], "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""} for index, row in enumerate(selections, 1)]

    write_csv(OUT / "source-binding.csv", list(source_rows[0]) + ["warning"], warned(source_rows))
    write_csv(OUT / "transform-register.csv", list(transforms[0]) + ["warning"], warned(transforms))
    write_csv(OUT / "feature-register.csv", list(features[0]) + ["warning"], warned(features))
    write_csv(OUT / "measurand-definition.csv", list(measurands[0]) + ["warning"], warned(measurands))
    write_csv(OUT / "hsi-closure-map.csv", list(hsi_rows[0]) + ["warning"], warned(hsi_rows))
    write_csv(OUT / "execution-result-template.csv", list(results[0]) + ["warning"], warned(results))
    write_csv(OUT / "selection-register.csv", list(selections[0]) + ["warning"], warned(selections))
    write_csv(OUT / "acceptance-matrix.csv", list(acceptance[0]) + ["warning"], warned(acceptance))
    (OUT / "axial-feature-index.svg").write_text(axial_svg(features), encoding="utf-8")
    (OUT / "attachment-pattern-index.svg").write_text(pattern_svg(features), encoding="utf-8")

    joint = fixture.joint_geometry()
    assembly = cq.Assembly(name="HR_V0_JOINT_MEAS_DEF_P01_NOT_RELEASED")
    colors = {"XM540": cq.Color(0.15, 0.55, 0.82), "H101": cq.Color(0.75, 0.78, 0.80), "S102": cq.Color(0.09, 0.31, 0.53)}
    for article, shape in joint.items():
        assembly.add(shape, name=f"EXACT_{article}_CONTROLLED_VENDOR_GEOMETRY", color=colors[article])
    for index, row in enumerate(features, 1):
        point = tuple(float(value) for value in str(row["nominal_point_joint_xyz_mm"]).split(","))
        marker = cq.Solid.makeSphere(0.70, cq.Vector(*point))
        assembly.add(marker, name=f"FEATURE_MARKER_{index:03d}_{row['feature_id']}", color=cq.Color(0.95, 0.70, 0.10))
    assembly.save(str(OUT / "HR-V0_joint-measurement-definition_P0.1_review.glb"))

    status = {"identifier": ID, "round": ROUND, "date": "2026-08-11", "source_step_files": 3, "source_bound_features": len(features), "measurement_characteristics": len(measurands), "hsi_routes": 20, "result_rows": len(results), "executed_results": 0, "selections": len(selections), "open_selections": len(selections), "acceptance_rows": len(acceptance), "accepted_rows": 0, "cad_nominal_is_received_evidence": False, "provider_selected": False, "physical_work_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "qualified_review_complete": False, "safety_credit": False, "warning": WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(guide(features, measurands, hsi_rows, selections), encoding="utf-8")
    manifest(OUT)
    shutil.copytree(OUT, REL)
    manifest(REL)

    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-39", "role": "Source-bound joint feature and measurand definition", "identifier": ID, "source_path": "release/hr-v0/joint-measurement-definition-p0.1/package-status.json", "configuration_state": "CURRENT CONTROLLED DRAFT - CAD NOMINALS ONLY", "release_boundary": f"{len(features)} exact source features, {len(measurands)} characteristics, all physical results and limits open", "warning": WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id": "SUP-31", "prior_identifier": "HR-V0-CONFIG-REC-P0.19", "current_or_required_successor": CID, "disposition": "SUPERSEDED BY R256 CONFIGURATION RECORD ONLY", "use_authorized": "NO", "warning": WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    holds, fields = read_csv(CFG / "open-holds.csv")
    for index, selection in enumerate(selections, 98):
        holds.append({"hold_id": f"HOLD-{index:02d}", "hold": f"{ID}: {selection['selection']}", "state": "OPEN", "closure_evidence": selection["evidence_required"], "warning": WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    config_acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for index, row in enumerate(acceptance, 131):
        config_acceptance.append({"acceptance_id": f"ACC-{index:03d}", "criterion": f"{ID}: {row['criterion']}", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, config_acceptance)
    impacts, fields = read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-002", "EG-003", "EG-005", "EG-007"}:
            row["evidence_added"] += f"; {ID} exact CAD feature/measurand definition"
            row["remaining_evidence"] += "; received feature match; executed measurements; numeric uncertainty; accepted limits; qualified disposition"
    write_csv(CFG / "gate-impact.csv", fields, impacts)
    hashes, fields = read_csv(CFG / "source-hash-register.csv")
    hashes.append({"source_path": "release/hr-v0/joint-measurement-definition-p0.1/package-status.json", "sha256": sha(REL / "package-status.json"), "role": "Joint feature/measurand definition", "warning": WARNING})
    write_csv(CFG / "source-hash-register.csv", fields, hashes)
    config_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    config_status.update({"identifier": CID, "round": ROUND, "current_records": 39, "supersession_records": 31, "open_holds": 109, "acceptance_rows": 142})
    (CFG / "package-status.json").write_text(json.dumps(config_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR256 adds {ID}. It defines exact source references but releases no physical result, tolerance, selection or work authority. 109 holds and 142 unexecuted acceptances remain.\n", encoding="utf-8")
    (CFG / "index.html").write_text(guide(features, measurands, hsi_rows, selections), encoding="utf-8")
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)
    print(f"Generated {ID}: {len(features)} features; {len(measurands)} characteristics; zero results/acceptances/authorizations")


if __name__ == "__main__":
    main()
