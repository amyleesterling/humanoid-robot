"""Generate individual HR-30 P0.1 fabrication-candidate part files.

All 98 physical frame, cover, and gripper-mechanism parts receive native STEP and SVG drawing-view
exports.  Planar 2.5D candidates also receive face-profile DXF; printable cover
candidates receive STL.  These are refinement/RFQ candidates, not released
drawings or authority to make parts.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_fabrication_architecture_p01 as fabrication


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "manufacturing-files"
IDENTIFIER = "HR30-MANUFACTURING-FILES-P0.1"
WARNING = body.WARNING
MODULE_ORDER = ["H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"]
PHYSICAL_PART_COUNT = 98


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export_step(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(shape, str(path))
    body.canonicalize_step(path)


def largest_planar_face(shape: cq.Shape) -> cq.Face:
    faces = [face for face in shape.Faces() if face.geomType() == "PLANE"]
    if not faces:
        raise RuntimeError("shape has no planar face for DXF profile")
    return max(faces, key=lambda face: face.Area())


def export_profile_dxf(shape: cq.Shape, path: Path) -> tuple[float, int]:
    face = largest_planar_face(shape)
    center = face.Center()
    normal = face.normalAt()
    plane = body.local_plane((center.x, center.y, center.z), (normal.x, normal.y, normal.z))
    workplane = cq.Workplane(plane).add(face)
    cq.exporters.exportDXF(workplane, str(path))
    return face.Area(), len(face.Wires())


def export_svg(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(
        shape,
        str(path),
        opt={
            "width": 1000,
            "height": 760,
            "marginLeft": 90,
            "marginTop": 70,
            "showAxes": True,
            "showHidden": False,
            "projectionDir": (1.0, -1.0, 0.75),
            "strokeWidth": 0.65,
            "strokeColor": (8, 43, 85),
            "hiddenColor": (140, 170, 195),
        },
    )
    # CadQuery's SVG writer leaves indentation on otherwise blank lines.
    # Canonicalize those generated views so repository whitespace checks stay clean.
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8", newline="\n")


def stock_form(part: fabrication.Part, bbox: cq.BoundBox) -> str:
    if part.role == "removable cover":
        return f"additive blank within {bbox.xlen:.1f} x {bbox.ylen:.1f} x {bbox.zlen:.1f} mm envelope"
    if "EXTRUSION" in part.material_candidate or "TUBE" in part.material_candidate:
        return f"hollow section / machined tube within {bbox.xlen:.1f} x {bbox.ylen:.1f} x {bbox.zlen:.1f} mm envelope"
    thickness = min(bbox.xlen, bbox.ylen, bbox.zlen)
    return f"plate or sheet candidate, nominal minimum envelope dimension {thickness:.3f} mm"


def drawing_datum_scheme(part: fabrication.Part, bbox: cq.BoundBox) -> str:
    if part.role == "removable cover":
        return "A mounting/seam surface; B longest edge/centerplane; C orthogonal edge/centerplane"
    if "2.5D" in part.process_candidate or "waterjet" in part.process_candidate:
        return "A largest planar face; B longest profile edge/centerline; C orthogonal profile edge/centerline"
    return "A primary mounting face/section; B longitudinal centerplane; C orthogonal centerplane"


def render_index(rows: list[dict], module_counts: Counter) -> str:
    groups = []
    for module in MODULE_ORDER:
        cards = []
        for row in (item for item in rows if item["module"] == module):
            derivative = []
            if row["dxf_path"]:
                derivative.append(f'<a href="{html.escape(row["dxf_path"])}">DXF</a>')
            if row["stl_path"]:
                derivative.append(f'<a href="{html.escape(row["stl_path"])}">STL</a>')
            derivative_text = " · ".join(derivative)
            if derivative_text:
                derivative_text = " · " + derivative_text
            cards.append(f'''<article class="part"><h3>{html.escape(row["part_id"])}</h3><p>{html.escape(row["role"])}</p><p>{html.escape(row["bbox_mm"])} · {html.escape(row["material_candidate"])}</p><p><a href="{html.escape(row["step_path"])}">STEP</a> · <a href="{html.escape(row["svg_path"])}">drawing view</a>{derivative_text}</p></article>''')
        groups.append(f'''<details open><summary>{module} · {module_counts[module]} parts</summary><div class="parts">{''.join(cards)}</div></details>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 individual manufacturing files P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#071d36;--navy:#0b3765;--sky:#7dd3fc;--pale:#eef8fe;--gold:#f2b91d;--line:#acd4e8;--ink:#142a40}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{background:var(--deep);color:white;padding:36px max(20px,calc((100vw - 1280px)/2))}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.04;margin:.2em 0}}h2{{font-size:clamp(27px,4vw,42px);color:var(--navy)}}h3{{font-size:19px;color:var(--navy);margin:.1em 0}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}main{{width:100%;max-width:1280px;margin:auto;padding:28px 20px 80px}}.viewer,.part,.panel,details{{background:white;border:2px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 3px 0 #c4e2f1}}model-viewer{{display:block;width:100%;height:clamp(520px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p,.panel{{padding:16px 20px}}details{{margin:16px 0}}summary{{cursor:pointer;padding:16px 20px;background:var(--navy);color:white;font-size:20px;font-weight:900}}.parts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;padding:14px}}.part{{padding:16px;box-shadow:none}}.part p{{margin:.35em 0}}a{{color:#075b9b;font-weight:800}}footer{{background:var(--deep);color:white;padding:30px max(20px,calc((100vw - 1280px)/2))}}@media(max-width:560px){{.parts{{grid-template-columns:1fr;padding:10px}}main{{padding-inline:12px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><h1>Individual fabrication candidates for the whole robot.</h1><p>Every physical frame, cover, and gripper-mechanism part has a native STEP and human-readable SVG drawing view. Planar 2.5D candidates also expose DXF profiles; removable printed covers expose STL meshes.</p></header><main><section><h2>Keep the whole robot in view</h2><div class="viewer"><model-viewer src="../module-cad/HR-30_module_exploded_candidate.glb" poster="../front-elevation.svg" alt="Interactive exploded view of the twelve HR-30 modules whose individual fabrication candidates are listed below" camera-controls camera-orbit="35deg 76deg 115%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>Use the <a href="part-file-register.csv">part-file register</a>, <a href="material-cut-list.csv">material/cut list</a>, <a href="process-route-register.csv">process routes</a>, and <a href="inspection-characteristic-register.csv">inspection characteristics</a> with the native files below.</p></div></section><section><h2>{PHYSICAL_PART_COUNT} physical part candidates</h2>{''.join(groups)}</section><section><h2>Manufacturing boundary</h2><div class="panel"><p>These files expose the current geometry for refinement and supplier discussion. They are not released drawings: exact material/product, allowables, stock condition, tolerances, GD&amp;T, threads/inserts, fasteners, surface finish, print orientation/settings, support removal, post-processing, DFM, FAI, structural proof and physical validation remain unresolved. Routing-reference volumes are intentionally excluded.</p></div></section></main><footer>Project Button · HR-30 individual manufacturing files P0.1 · no procurement, fabrication, assembly, powered-test, motion or energization authority</footer></body></html>'''


def update_package() -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "individual_manufacturing_file_package_present": True,
        "individual_physical_part_step_count": PHYSICAL_PART_COUNT,
        "individual_part_svg_drawing_view_count": PHYSICAL_PART_COUNT,
        "individual_part_files_fabrication_released": False,
        "individual_part_drawings_released": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H06":
            row["unresolved_item"] = f"All {PHYSICAL_PART_COUNT} physical frame/cover/gripper-mechanism candidates now have individual native STEP and SVG drawing-view files; planar 2.5D candidates also have DXF profiles and removable printed covers have STL meshes. Material candidates, stock condition, allowables, print material/process, ribs/stiffness, retention, vents, access, tolerance/GD&T, threads/inserts, edge treatment, DFM, FAI, structural/impact proof and qualified review remain open."
        if row["hold_id"] == "HR30-P01-H10":
            row["unresolved_item"] = f"Twelve module STEP pairs, an exploded whole-body assembly, a web interface atlas, and individual candidate files for all {PHYSICAL_PART_COUNT} physical fabrication parts now exist. The per-part package adds material/cut, process-route and inspection-characteristic registers. Released drawings, tolerances/GD&T, exact material/process selections, threads/inserts/fasteners, DFM, FAI, proof, physical test and qualified review remain open."
    write_csv(holds_path, holds)

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Serviceable joint-family CAD\n"
    addition = f"\n## Individual manufacturing-candidate files\n\nEvery one of the {PHYSICAL_PART_COUNT} physical frame, removable-cover, and gripper-mechanism candidates now has its own native STEP and SVG drawing-view export in `manufacturing-files/`. Planar 2.5D candidates also expose largest-face DXF profiles; removable printed covers expose STL meshes. Material/cut, process-route, inspection-characteristic and file-provenance registers keep the parts connected to the authoritative fabrication source. These are design-refinement and supplier-discussion files, not released drawings or fabrication authority; exact materials, tolerances/GD&T, threads/inserts, print settings, DFM, FAI, structural proof and physical validation remain open.\n"
    if addition.strip() not in readme:
        if marker in readme:
            readme = readme.replace(marker, addition + marker)
        else:
            # Earlier whole-body generators intentionally rebuild their own
            # sections from source.  A missing optional downstream marker is
            # therefore not a reason to discard the generated manufacturing
            # package; append the controlled section and let later generators
            # restore their own blocks.
            readme = readme.rstrip() + "\n" + addition
        readme_path.write_text(readme, encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-MANUFACTURING-FILES-P01-START -->", "<!-- HR30-MANUFACTURING-FILES-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<!-- HR30-JOINT-FAMILY-CAD-P01-START -->"
    section = f'''{start}<section id="manufacturing-files"><h2>Every physical frame, cover, and gripper-mechanism part now has its own file</h2><div class="grid"><article class="card pass"><div class="metric">{PHYSICAL_PART_COUNT}</div><p>Individual native STEP and SVG drawing-view exports.</p></article><article class="card pass"><h3>Process-specific derivatives</h3><p>Planar 2.5D candidates have DXF profiles; removable printed covers have STL meshes.</p></article><article class="card pass"><h3>Controlled routes</h3><p>Material/cut, process and inspection registers bind every part to its source geometry.</p></article><article class="card hold"><h3>Still preliminary</h3><p>Released drawings, tolerances, exact materials, DFM, FAI and physical proof remain open.</p></article></div><p><a href="manufacturing-files/index.html">Open the individual manufacturing-file guide</a> · <a href="manufacturing-files/part-file-register.csv">Part-file register</a> · <a href="manufacturing-files/material-cut-list.csv">Material/cut list</a>.</p></section>{end}'''
    if marker not in page:
        raise RuntimeError("main page manufacturing-file marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    part_root = OUT / "parts"
    physical = [part for part in fabrication.build()[0] if part.density_kg_m3 > 1.0]
    if len(physical) != PHYSICAL_PART_COUNT:
        raise RuntimeError(f"expected {PHYSICAL_PART_COUNT} physical fabrication parts, found {len(physical)}")

    file_rows: list[dict] = []
    material_rows: list[dict] = []
    process_rows: list[dict] = []
    inspection_rows: list[dict] = []
    dxf_count = 0
    stl_count = 0
    for part in physical:
        part_dir = part_root / part.module / part.name
        part_dir.mkdir(parents=True)
        step_path = part_dir / f"{part.name}.step"
        svg_path = part_dir / f"{part.name}.svg"
        export_step(part.shape, step_path)
        export_svg(part.shape, svg_path)
        dxf_rel = ""
        dxf_sha = ""
        dxf_bytes = ""
        profile_area = ""
        profile_wires = ""
        if "2.5D" in part.process_candidate or "waterjet" in part.process_candidate:
            dxf_path = part_dir / f"{part.name}_largest-face-profile.dxf"
            area, wires = export_profile_dxf(part.shape, dxf_path)
            dxf_rel = dxf_path.relative_to(OUT).as_posix()
            dxf_sha = sha256(dxf_path)
            dxf_bytes = str(dxf_path.stat().st_size)
            profile_area = f"{area:.6f}"
            profile_wires = str(wires)
            dxf_count += 1
        stl_rel = ""
        stl_sha = ""
        stl_bytes = ""
        if part.role == "removable cover":
            stl_path = part_dir / f"{part.name}.stl"
            cq.exporters.export(part.shape, str(stl_path), tolerance=0.15, angularTolerance=0.15)
            stl_rel = stl_path.relative_to(OUT).as_posix()
            stl_sha = sha256(stl_path)
            stl_bytes = str(stl_path.stat().st_size)
            stl_count += 1
        bbox = part.shape.BoundingBox()
        bbox_text = f"{bbox.xlen:.3f} x {bbox.ylen:.3f} x {bbox.zlen:.3f} mm"
        file_rows.append({
            "part_id": part.name,
            "module": part.module,
            "role": part.role,
            "bbox_mm": bbox_text,
            "volume_mm3": f"{part.shape.Volume():.6f}",
            "candidate_mass_kg": f"{fabrication.volume_mass_kg(part.shape, part.density_kg_m3):.9f}",
            "material_candidate": part.material_candidate,
            "process_candidate": part.process_candidate,
            "service_state": part.service_state,
            "step_path": step_path.relative_to(OUT).as_posix(),
            "step_bytes": step_path.stat().st_size,
            "step_sha256": sha256(step_path),
            "svg_path": svg_path.relative_to(OUT).as_posix(),
            "svg_bytes": svg_path.stat().st_size,
            "svg_sha256": sha256(svg_path),
            "dxf_path": dxf_rel,
            "dxf_bytes": dxf_bytes,
            "dxf_sha256": dxf_sha,
            "largest_planar_profile_area_mm2": profile_area,
            "largest_planar_profile_wire_count": profile_wires,
            "stl_path": stl_rel,
            "stl_bytes": stl_bytes,
            "stl_sha256": stl_sha,
            "release_state": "INDIVIDUAL P0.1 CANDIDATE FILE - DRAWING/GD&T/MATERIAL/PROCESS/DFM/FAI/PHYSICAL VALIDATION OPEN",
            "warning": WARNING,
        })
        material_rows.append({
            "part_id": part.name,
            "module": part.module,
            "quantity_candidate": 1,
            "stock_form_candidate": stock_form(part, bbox),
            "material_candidate": part.material_candidate,
            "gross_envelope_mm": bbox_text,
            "net_volume_mm3": f"{part.shape.Volume():.6f}",
            "net_mass_screen_kg": f"{fabrication.volume_mass_kg(part.shape, part.density_kg_m3):.9f}",
            "exact_stock_size_and_allowance": "SELECTION REQUIRED",
            "material_certification": "MTR/CoC REQUIREMENT SELECTION REQUIRED",
            "warning": WARNING,
        })
        process_rows.append({
            "part_id": part.name,
            "module": part.module,
            "primary_process_candidate": part.process_candidate,
            "secondary_operations": "holes/threads/inserts/edge finishing/support removal/post-process SELECTION REQUIRED",
            "finish_candidate": "deburr and safe edge baseline; coating/surface treatment SELECTION REQUIRED",
            "fixture_or_print_orientation": "SELECTION REQUIRED",
            "dfm_status": "NOT REVIEWED",
            "fai_status": "NOT EXECUTED",
            "release_state": "PROCESS ROUTE CANDIDATE ONLY - NOT RELEASED",
            "warning": WARNING,
        })
        datum = drawing_datum_scheme(part, bbox)
        characteristics = (
            ("DATUM_SCHEME", datum, "datum simulators and precedence SELECTION REQUIRED"),
            ("OVERALL_X", f"{bbox.xlen:.3f} mm nominal CAD envelope", "size tolerance SELECTION REQUIRED"),
            ("OVERALL_Y", f"{bbox.ylen:.3f} mm nominal CAD envelope", "size tolerance SELECTION REQUIRED"),
            ("OVERALL_Z", f"{bbox.zlen:.3f} mm nominal CAD envelope", "size tolerance SELECTION REQUIRED"),
            ("PROFILE_OR_SURFACE", "nominal native STEP geometry", "profile tolerance, inspection method and sampling SELECTION REQUIRED"),
        )
        for characteristic_id, nominal, requirement in characteristics:
            inspection_rows.append({
                "part_id": part.name,
                "module": part.module,
                "characteristic_id": characteristic_id,
                "nominal_or_basis": nominal,
                "acceptance_requirement": requirement,
                "inspection_method": "SELECTION REQUIRED",
                "result": "NOT EXECUTED",
                "authority": "NO FABRICATION OR ACCEPTANCE AUTHORITY",
                "warning": WARNING,
            })

    write_csv(OUT / "part-file-register.csv", file_rows)
    write_csv(OUT / "material-cut-list.csv", material_rows)
    write_csv(OUT / "process-route-register.csv", process_rows)
    write_csv(OUT / "inspection-characteristic-register.csv", inspection_rows)
    module_counts = Counter(row["module"] for row in file_rows)
    (OUT / "index.html").write_text(render_index(file_rows, module_counts), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 individual manufacturing files P0.1\n\n**{WARNING}**\n\nAll {PHYSICAL_PART_COUNT} physical fabrication candidates have individual native STEP and SVG drawing-view exports. The {dxf_count} planar 2.5D candidates also have largest-face DXF profiles; the {stl_count} removable covers have 0.15 mm / 0.15 rad STL meshes. Twelve nonmaterial harness corridors are intentionally excluded.\n\nThese files support design refinement and supplier discussion only. They are not released drawings or fabrication authority. Exact materials, stock, tolerances/GD&T, threads/inserts, print settings, DFM, FAI, capacity and physical validation remain open.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "manufacturing-files-source.py")
    source_binding = {
        "identifier": IDENTIFIER,
        "source_generator": "tools/generate_hr30_fabrication_architecture_p01.py",
        "source_generator_sha256": sha256(ROOT / "tools" / "generate_hr30_fabrication_architecture_p01.py"),
        "manufacturing_file_generator": "tools/generate_hr30_manufacturing_files_p01.py",
        "manufacturing_file_generator_sha256": sha256(Path(__file__)),
        "physical_source_part_count": PHYSICAL_PART_COUNT,
        "excluded_reference_volume_count": 12,
        "warning": WARNING,
    }
    (OUT / "source-binding.json").write_text(json.dumps(source_binding, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER,
        "physical_part_count": PHYSICAL_PART_COUNT,
        "individual_step_count": PHYSICAL_PART_COUNT,
        "individual_svg_drawing_view_count": PHYSICAL_PART_COUNT,
        "planar_profile_dxf_count": dxf_count,
        "printed_cover_stl_count": stl_count,
        "inspection_characteristic_count": len(inspection_rows),
        "module_count": len(module_counts),
        "reference_route_volumes_excluded": 12,
        "editable_source_present": True,
        "drawings_released": False,
        "materials_selected": False,
        "tolerances_gdt_released": False,
        "dfm_complete": False,
        "fai_complete": False,
        "structural_capacity_validated": False,
        "physical_validation_complete": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "manufacturing-files-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    update_package()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
