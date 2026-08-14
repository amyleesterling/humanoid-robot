"""Generate separable HR-30 P0.1 module CAD and an exploded assembly.

The exports are derived from the existing whole-body fabrication, body/joint,
hand, shell and installed-equipment generators.  They make the candidate
inspectable module-by-module without pretending that drawings, fits,
tolerances, fasteners, materials or physical validation are released.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_fabrication_architecture_p01 as fabrication
import generate_hr30_installed_equipment_p01 as equipment


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "module-cad"
IDENTIFIER = "HR30-MODULE-CAD-EXPORTS-P0.1"
WARNING = body.WARNING
MODULE_IDS = ["H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"]
AXIS_MODULE = {
    "HEAD_PAN": "N01", "HEAD_TILT": "N01", "WAIST_YAW": "P01",
    "L_SHOULDER_PITCH": "A01", "L_SHOULDER_ROLL": "A01", "L_ELBOW_PITCH": "A01", "L_WRIST_ROTATION": "A01", "L_GRIPPER": "G01",
    "R_SHOULDER_PITCH": "A02", "R_SHOULDER_ROLL": "A02", "R_ELBOW_PITCH": "A02", "R_WRIST_ROTATION": "A02", "R_GRIPPER": "G02",
    "L_HIP_YAW": "L01", "L_HIP_ROLL": "L01", "L_HIP_PITCH": "L01", "L_KNEE_PITCH": "L01", "L_ANKLE_PITCH": "L01", "L_ANKLE_ROLL": "L01",
    "R_HIP_YAW": "L02", "R_HIP_ROLL": "L02", "R_HIP_PITCH": "L02", "R_KNEE_PITCH": "L02", "R_ANKLE_PITCH": "L02", "R_ANKLE_ROLL": "L02",
}
EXPLODE = {
    "H01": (0, 0, 105), "N01": (0, 0, 48), "T01": (0, 0, 0), "P01": (0, 0, -42),
    "A01": (180, 0, 0), "G01": (275, 0, -28), "A02": (-180, 0, 0), "G02": (-275, 0, -28),
    "L01": (95, 0, -95), "F01": (95, 0, -170), "L02": (-95, 0, -95), "F02": (-95, 0, -170),
}
MODULE_COLORS = {
    "H01": (0.47, 0.79, 0.95, 1), "N01": (0.10, 0.24, 0.40, 1), "T01": (0.08, 0.22, 0.40, 1), "P01": (0.18, 0.43, 0.64, 1),
    "A01": (0.30, 0.68, 0.88, 1), "G01": (0.95, 0.70, 0.08, 1), "A02": (0.30, 0.68, 0.88, 1), "G02": (0.95, 0.70, 0.08, 1),
    "L01": (0.43, 0.76, 0.92, 1), "F01": (0.18, 0.43, 0.64, 1), "L02": (0.43, 0.76, 0.92, 1), "F02": (0.18, 0.43, 0.64, 1),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def body_component_module(name: str) -> str | None:
    for axis in sorted(AXIS_MODULE, key=len, reverse=True):
        if name == f"AXIS_{axis}" or name.startswith(f"JMOD_{axis}_"):
            return AXIS_MODULE[axis]
    direct = [
        (("FACE_", "HEAD_SHELL", "HEAD_SENSOR"), "H01"), (("NECK_",), "N01"),
        (("TORSO_",), "T01"), (("PELVIS_", "WAIST_"), "P01"),
        (("L_SHOULDER", "L_UPPER_ARM", "L_ELBOW", "L_FOREARM", "L_WRIST"), "A01"),
        (("L_HAND", "L_INBOARD", "L_OUTBOARD"), "G01"),
        (("R_SHOULDER", "R_UPPER_ARM", "R_ELBOW", "R_FOREARM", "R_WRIST"), "A02"),
        (("R_HAND", "R_INBOARD", "R_OUTBOARD"), "G02"),
        (("L_HIP", "L_THIGH", "L_KNEE", "L_SHIN", "L_ANKLE"), "L01"), (("L_FOOT",), "F01"),
        (("R_HIP", "R_THIGH", "R_KNEE", "R_SHIN", "R_ANKLE"), "L02"), (("R_FOOT",), "F02"),
    ]
    for prefixes, module in direct:
        if name.startswith(prefixes):
            return module
    return None


def equipment_module(item: equipment.Equipment) -> str | None:
    if item.module in MODULE_IDS:
        return item.module
    if item.module in {"C01", "S01", "T01/P01/H01"}:
        return "T01"
    combined = {"A01/G01": "A01", "A02/G02": "A02", "L01/F01": "L01", "L02/F02": "L02"}
    if item.module in combined:
        return combined[item.module]
    if item.module == "HN01":
        tokens = [
            ("HEAD", "H01"), ("L_ARM", "A01"), ("R_ARM", "A02"),
            ("L_LEG", "L01"), ("R_LEG", "L02"), ("TORSO", "T01"),
        ]
        for token, module in tokens:
            if token in item.item_id:
                return module
    return None


def reference_route_module(part: fabrication.Part) -> str | None:
    if part.module in MODULE_IDS:
        return part.module
    if part.module != "HN01":
        return None
    for token, module in (("HEAD", "H01"), ("L_ARM", "A01"), ("R_ARM", "A02"), ("L_LEG", "L01"), ("R_LEG", "L02"), ("TORSO", "T01")):
        if token in part.name:
            return module
    return None


def compound(shapes: list[cq.Shape], label: str) -> cq.Shape:
    if not shapes:
        raise RuntimeError(f"empty module geometry {label}")
    result = cq.Compound.makeCompound(shapes)
    if result.isNull() or not result.isValid() or result.Volume() <= 1e-6:
        raise RuntimeError(f"invalid module compound {label}")
    return result


def export_step(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(shape, str(path))
    body.canonicalize_step(path)


def render_index(rows: list[dict]) -> str:
    cards = []
    for row in rows:
        cards.append(f'''<article class="module"><span>{row['module_id']}</span><div><h3>{html.escape(row['body_segment'])}</h3><p>{row['fabrication_part_count']} fabrication parts · {row['body_component_count']} body/joint components · {row['equipment_item_count']} installed-equipment envelopes</p><p><a href="{row['fabrication_step']}">Fabrication STEP</a> · <a href="{row['integration_reference_step']}">Integration-reference STEP</a></p></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 exploded module CAD P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>
:root{{--deep:#0b203a;--navy:#132f55;--sky:#77c9f2;--pale:#eef8fd;--gold:#f2b91d;--line:#b8d7e8;--ink:#17243a}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header{{background:var(--deep);color:white;padding:36px max(20px,calc((100vw - 1240px)/2))}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.04;margin:.2em 0}}h2{{font-size:clamp(27px,4vw,42px);color:var(--navy)}}h3{{font-size:22px;color:var(--navy);margin:0}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}main{{width:100%;max-width:1240px;margin:auto;padding:28px 20px 80px}}.viewer,.module,.panel{{background:white;border:2px solid var(--line);border-radius:17px;overflow:hidden;box-shadow:0 3px 0 #c4e2f1}}model-viewer{{display:block;width:100%;height:clamp(520px,72vh,780px);background:radial-gradient(circle,#fff,var(--pale))}}.viewer p,.panel{{padding:16px 20px}}.modules{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}.module{{display:flex;gap:14px;padding:18px}}.module>span{{display:grid;place-items:center;min-width:58px;height:43px;border-radius:11px;background:var(--gold);border:2px solid #8a5b00;font-weight:900}}.module p{{margin:.25em 0}}a{{color:#075b9b;font-weight:800}}footer{{background:var(--deep);color:white;padding:30px max(20px,calc((100vw - 1240px)/2))}}@media(max-width:560px){{.modules{{grid-template-columns:1fr}}}}
</style></head><body><header><div class="warning">{WARNING}</div><h1>The complete robot, separated into real build modules.</h1><p>The exploded model retains the actual P0.1 fabrication parts, joint/hand/body geometry, and located equipment envelopes. Separation offsets are presentation transforms only.</p></header><main><section><h2>Exploded whole-body assembly</h2><div class="viewer"><model-viewer src="HR-30_module_exploded_candidate.glb" poster="../front-elevation.svg" alt="Interactive exploded view of all 12 HR-30 body modules" camera-controls camera-orbit="35deg 76deg 115%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Download the <a href="HR-30_module_exploded_candidate.step">exploded STEP</a> or the <a href="module-export-register.csv">export register</a>.</p></div></section><section><h2>12 separable module exports</h2><div class="modules">{''.join(cards)}</div></section><section><h2>What these exports mean</h2><div class="panel"><p>The fabrication STEP for each module contains its current frame and removable-cover candidates. The integration-reference STEP adds the module-owned joint, hand, shell and installed-equipment geometry. Neither is a released part drawing: fasteners, bearing fits, tolerances, materials, harnesses, DFM, FAI, structural proof and physical validation remain open.</p></div></section></main><footer>Project Button · HR-30 module CAD P0.1 · no procurement, fabrication, assembly, powered-test, motion or energization authority</footer></body></html>'''


def update_package(rows: list[dict]) -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "module_cad_exports_present": True, "module_cad_export_count": 12,
        "module_fabrication_step_count": 12, "module_integration_reference_step_count": 12,
        "exploded_module_step_present": True, "exploded_module_glb_present": True,
        "module_cad_manufacturing_released": False, "fabrication_drawings_released": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H10":
            row["unresolved_item"] = "Twelve module-specific fabrication and integration-reference STEP exports plus an exploded whole-body STEP/GLB now exist. A web interface atlas binds their dimensions, axes, masses and dependencies. Released part drawings, tolerances/GD&T, material/process selections, fasteners, DFM, FAI, proof, physical test and qualified review remain open."
    write_csv(holds_path, holds)

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Whole-body interface atlas\n"
    addition = "\n## Separable module CAD\n\nThe fabrication and integration-reference geometry is now exported as 12 real body modules plus an exploded whole-body STEP and interactive GLB. Each module export is derived from the same fabrication, body/joint/hand and installed-equipment sources as the integrated robot rather than from placeholder blocks. Explosion offsets are presentation transforms only. These are P0.1 separation and refinement artifacts, not released manufacturing drawings or assembly authority.\n"
    if addition.strip() not in readme:
        if marker not in readme:
            raise RuntimeError("README module-CAD marker missing")
        readme = readme.replace(marker, addition + marker)
        readme_path.write_text(readme, encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-MODULE-CAD-P01-START -->", "<!-- HR30-MODULE-CAD-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<section><h2>System artifacts</h2>"
    section = f'''{start}<section id="module-cad"><h2>Explode the robot into 12 real modules</h2><div class="grid"><article class="card pass"><div class="metric">12 + 12</div><p>Fabrication STEP and integration-reference STEP exports cover every body module.</p></article><article class="card pass"><div class="metric">66</div><p>Existing fabrication parts are deterministically owned by the module exports.</p></article><article class="card pass"><h3>Actual whole-body sources</h3><p>Joint, hand, shell and equipment geometry comes from the same generators as the integrated robot.</p></article><article class="card hold"><h3>Still preliminary</h3><p>Explosion is a service/refinement view; drawings, fasteners, fits, tolerances and physical proof remain open.</p></article></div><div class="viewer"><model-viewer src="module-cad/HR-30_module_exploded_candidate.glb" poster="front-elevation.svg" alt="Interactive exploded view of all 12 HR-30 whole-body modules" camera-controls camera-orbit="35deg 76deg 115%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="module-cad/index.html">Open the exploded module guide</a> · <a href="module-cad/HR-30_module_exploded_candidate.step">Exploded STEP</a> · <a href="module-cad/module-export-register.csv">Module export register</a>.</p></div></section>{end}'''
    if marker not in page:
        raise RuntimeError("main page module-CAD marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    fab_parts, _panels, _routes = fabrication.build()
    body_components, _axes, _bindings, _transforms = body.build()
    equipment_items = equipment.build()

    fab_by_module: dict[str, list[fabrication.Part]] = defaultdict(list)
    ref_routes_by_module: dict[str, list[fabrication.Part]] = defaultdict(list)
    for part in fab_parts:
        module = reference_route_module(part)
        if module is None:
            continue
        if part.density_kg_m3 > 1.0:
            fab_by_module[module].append(part)
        else:
            ref_routes_by_module[module].append(part)
    body_by_module: dict[str, list[body.Component]] = defaultdict(list)
    unmapped_body = []
    for component in body_components:
        module = body_component_module(component.name)
        if module:
            body_by_module[module].append(component)
        elif component.physical:
            unmapped_body.append(component.name)
    if unmapped_body:
        raise RuntimeError(f"unmapped physical body components: {unmapped_body}")
    equipment_by_module: dict[str, list[equipment.Equipment]] = defaultdict(list)
    unmapped_equipment = []
    for item in equipment_items:
        module = equipment_module(item)
        if module:
            equipment_by_module[module].append(item)
        else:
            unmapped_equipment.append(item.item_id)
    if unmapped_equipment:
        raise RuntimeError(f"unmapped equipment items: {unmapped_equipment}")

    interface_rows = {row["module_id"]: row for row in csv.DictReader((PACKAGE / "module-interface-control-register.csv").open(encoding="utf-8"))}
    exploded_shapes = []
    exploded = cq.Assembly(name="HR30_EXPLODED_12_MODULES_P01_NOT_RELEASED")
    rows = []
    for module in MODULE_IDS:
        module_dir = OUT / module
        module_dir.mkdir()
        fab = fab_by_module[module]
        bcomponents = body_by_module[module]
        eq = equipment_by_module[module]
        fab_shape = compound([part.shape for part in fab], f"{module} fabrication")
        fab_path = module_dir / f"{module}_fabrication_candidate.step"
        export_step(fab_shape, fab_path)
        integration_shapes = [part.shape for part in fab]
        integration_shapes.extend(component.shape for component in bcomponents if component.physical)
        integration_shapes.extend(item.shape for item in eq)
        integration = compound(integration_shapes, f"{module} integration")
        integration_path = module_dir / f"{module}_integration_reference.step"
        export_step(integration, integration_path)

        offset = cq.Location(cq.Vector(*EXPLODE[module]))
        for index, shape in enumerate(integration_shapes):
            moved = shape.moved(offset)
            exploded_shapes.append(moved)
            exploded.add(moved, name=f"{module}_SOLID_{index+1:03d}", color=cq.Color(*MODULE_COLORS[module]))
        for index, part in enumerate(ref_routes_by_module[module]):
            exploded.add(part.shape.moved(offset), name=f"{module}_ROUTE_{index+1:02d}", color=cq.Color(*part.color))

        box = integration.BoundingBox()
        mass = sum(fabrication.volume_mass_kg(part.shape, part.density_kg_m3) for part in fab)
        rows.append({
            "module_id": module, "body_segment": interface_rows[module]["body_segment"],
            "fabrication_part_count": len(fab), "body_component_count": len(bcomponents), "equipment_item_count": len(eq),
            "integration_physical_solid_count": len(integration_shapes), "reference_route_count": len(ref_routes_by_module[module]),
            "fabrication_cad_mass_screen_kg": f"{mass:.9f}",
            "integration_bbox_x_mm": f"{box.xlen:.3f}", "integration_bbox_y_mm": f"{box.ylen:.3f}", "integration_bbox_z_mm": f"{box.zlen:.3f}",
            "explode_offset_xyz_mm": f"({EXPLODE[module][0]}, {EXPLODE[module][1]}, {EXPLODE[module][2]})",
            "fabrication_step": f"{module}/{fab_path.name}", "fabrication_step_bytes": fab_path.stat().st_size, "fabrication_step_sha256": sha256(fab_path),
            "integration_reference_step": f"{module}/{integration_path.name}", "integration_reference_step_bytes": integration_path.stat().st_size, "integration_reference_step_sha256": sha256(integration_path),
            "release_state": "SEPARABLE P0.1 MODULE CAD - DRAWING/GD&T/MATERIAL/FASTENER/DFM/FAI/PHYSICAL VALIDATION OPEN", "warning": WARNING,
        })

    if sum(len(v) for v in fab_by_module.values()) != 66:
        raise RuntimeError("66 fabrication parts are not owned exactly once")
    exploded_step = OUT / "HR-30_module_exploded_candidate.step"
    export_step(compound(exploded_shapes, "exploded whole body"), exploded_step)
    exploded_glb = OUT / "HR-30_module_exploded_candidate.glb"
    # This GLB is a web/presentation mesh, not the dimensional authority.  A
    # 0.50 mm / 0.25 rad tessellation keeps the complete exploded robot below
    # GitHub's 100,000,000-byte single-file limit while the native STEP above
    # retains the exact B-Rep geometry used for engineering refinement.
    exploded.save(str(exploded_glb), tolerance=0.50, angularTolerance=0.25)
    write_csv(OUT / "module-export-register.csv", rows)
    (OUT / "index.html").write_text(render_index(rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(
        f"# HR-30 separable module CAD P0.1\n\n**{WARNING}**\n\nTwelve fabrication STEP exports contain the current module-owned frame and removable-cover candidates. Twelve integration-reference STEP exports add exact module-owned joint, hand, shell and located equipment geometry. The exploded STEP/GLB applies only the offsets in `module-export-register.csv`; it does not change interface datums. The STEP is the dimensional B-Rep candidate; the GLB is a 0.50 mm / 0.25 rad display tessellation.\n\nThese files are design/refinement artifacts, not manufacturing drawings. Exact fasteners, fits, tolerances, materials, harnesses, DFM, FAI, structural proof and physical validation remain open.\n",
        encoding="utf-8", newline="\n",
    )
    shutil.copy2(Path(__file__), OUT / "module-cad-source.py")
    status = {
        "identifier": IDENTIFIER, "module_count": 12, "fabrication_step_count": 12,
        "integration_reference_step_count": 12, "fabrication_part_ownership_count": 66,
        "exploded_step_present": True, "exploded_glb_present": True,
        "exploded_glb_display_linear_tolerance_mm": 0.50,
        "exploded_glb_display_angular_tolerance_rad": 0.25,
        "drawings_released": False, "materials_selected": False, "fasteners_selected": False,
        "structural_capacity_validated": False, "fabrication_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "module-cad-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    update_package(rows)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
