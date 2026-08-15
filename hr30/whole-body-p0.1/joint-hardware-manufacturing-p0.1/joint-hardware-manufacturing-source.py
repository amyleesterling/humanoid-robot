"""Export and classify every actual-axis HR-30 joint-hardware candidate.

The body architecture contains 142 non-actuator physical joint-module items:
25 output shafts, 39 catalogue-bearing envelopes, 39 interface plates, 28
smooth pulley envelopes and 11 coupling placeholders.  This package makes
that full universe explicit.  It exports individual local-coordinate STEP/SVG
files only for the 64 custom parts whose current geometry is a real solid
definition (shafts and interface plates), and refuses to present catalogue
bearings, toothless pulley envelopes, or coupling placeholders as fabricable
parts.
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


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "joint-hardware-manufacturing-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-JOINT-HARDWARE-MANUFACTURING-P0.1"
WARNING = (
    "PRELIMINARY - JOINT-HARDWARE REFINEMENT FILES ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
AXIS_HARDWARE_COUNT = 142
REAL_SOLID_EXPORT_COUNT = 64
BEARING_REFERENCE_COUNT = 39
REDESIGN_REQUIRED_COUNT = 39


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export_svg(shape: cq.Shape, path: Path) -> None:
    cq.exporters.export(
        shape,
        str(path),
        opt={
            "width": 900,
            "height": 680,
            "marginLeft": 80,
            "marginTop": 65,
            "showAxes": True,
            "showHidden": False,
            "projectionDir": (1.0, -1.0, 0.75),
            "strokeWidth": 0.70,
            "strokeColor": (8, 43, 85),
            "hiddenColor": (140, 170, 195),
        },
    )
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def largest_planar_face(shape: cq.Shape) -> cq.Face:
    planes = [face for face in shape.Faces() if face.geomType() == "PLANE"]
    if not planes:
        raise RuntimeError("interface plate has no planar face")
    return max(planes, key=lambda face: face.Area())


def export_plate_dxf(shape: cq.Shape, path: Path) -> None:
    face = largest_planar_face(shape)
    center = face.Center()
    normal = face.normalAt()
    plane = body.local_plane((center.x, center.y, center.z), (normal.x, normal.y, normal.z))
    cq.exporters.exportDXF(cq.Workplane(plane).add(face), str(path))


def axis_for_name(name: str, axis_ids: list[str]) -> str:
    for axis_id in sorted(axis_ids, key=len, reverse=True):
        if name.startswith(f"JMOD_{axis_id}_"):
            return axis_id
    raise RuntimeError(f"cannot bind joint hardware to an axis: {name}")


def type_for_name(name: str) -> str:
    if "_BEARING_" in name:
        return "CATALOGUE_BEARING_ENVELOPE"
    if name.endswith("_OUTPUT_SHAFT"):
        return "OUTPUT_SHAFT"
    if "_INTERFACE_PLATE_" in name:
        return "INTERFACE_PLATE"
    if name.endswith("_OUTPUT_PULLEY"):
        return "OUTPUT_PULLEY_ENVELOPE"
    if name.endswith("_MOTOR_PULLEY"):
        return "MOTOR_PULLEY_ENVELOPE"
    if name.endswith("_ACTUATOR_OUTPUT_COUPLER"):
        return "ACTUATOR_OUTPUT_COUPLER_PLACEHOLDER"
    if name.endswith("_SYMMETRIC_DRIVE_COUPLER"):
        return "SYMMETRIC_DRIVE_COUPLER_PLACEHOLDER"
    raise RuntimeError(f"unknown joint hardware type: {name}")


def disposition_for(part_type: str) -> tuple[str, str, str, bool]:
    if part_type == "CATALOGUE_BEARING_ENVELOPE":
        return (
            "CATALOGUE REFERENCE - DO NOT FABRICATE",
            "manufacturer bearing selection / receipt inspection",
            "NO SUPPLIER UPLOAD FILE; PURCHASE SELECTION REQUIRED",
            False,
        )
    if part_type in {"OUTPUT_PULLEY_ENVELOPE", "MOTOR_PULLEY_ENVELOPE"}:
        return (
            "REDESIGN REQUIRED - SMOOTH ENVELOPE HAS NO TIMING TEETH OR FLANGES",
            "exact catalogue pulley or released toothed custom pulley",
            "NO FABRICATION FILE; CURRENT SOLID IS PACKAGING EVIDENCE ONLY",
            False,
        )
    if "COUPLER_PLACEHOLDER" in part_type:
        return (
            "REDESIGN REQUIRED - ACTUATOR/HORN/CLAMP INTERFACE ABSENT",
            "product-specific horn or spline adapter with secondary retention",
            "NO FABRICATION FILE; CURRENT SOLID IS PACKAGING EVIDENCE ONLY",
            False,
        )
    if part_type == "OUTPUT_SHAFT":
        return (
            "LOCAL-COORDINATE REFINEMENT STEP - SHOULDERS/GROOVES/FITS ABSENT",
            "turn/mill refinement after bearing-fit and retention design",
            "NOT AN RFQ OR FABRICATION RELEASE",
            True,
        )
    return (
        "LOCAL-COORDINATE REFINEMENT STEP - THREAD/INSERT/TOLERANCE STACK OPEN",
        "2.5D or 3-axis refinement after joint/load/fastener disposition",
        "NOT AN RFQ OR FABRICATION RELEASE",
        True,
    )


def material_for(part_type: str) -> str:
    if part_type == "OUTPUT_SHAFT":
        return "7075-T6/T651 ALUMINUM DENSITY-SCREEN CANDIDATE; 17-4PH/STEEL FAMILY CONFLICT OPEN"
    if part_type == "INTERFACE_PLATE":
        return "6061-T6/T651 PLATE CANDIDATE"
    if part_type == "CATALOGUE_BEARING_ENVELOPE":
        return "MANUFACTURER CATALOGUE PRODUCT - EXACT SUFFIX/APPLICATION SELECTION REQUIRED"
    if "PULLEY" in part_type:
        return "CATALOGUE ALUMINUM/STEEL OR RELEASED CUSTOM PULLEY SELECTION REQUIRED"
    return "PRODUCT-SPECIFIC ALUMINUM/STEEL ADAPTER SELECTION REQUIRED"


def feature_rows_for(axis_id: str, family_id: str, part_id: str, part_type: str, spec: dict) -> list[dict]:
    common = {
        "axis_id": axis_id,
        "family_id": family_id,
        "part_id": part_id,
        "source_basis": "SHA-BOUND BODY-ARCHITECTURE GENERATOR / JOINT_MODULE_FAMILIES",
        "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY",
    }
    rows: list[dict] = []

    def add(feature_id: str, feature_type: str, nominal: str, requirement: str, state: str) -> None:
        rows.append({
            **common,
            "feature_id": feature_id,
            "feature_type": feature_type,
            "nominal_geometry": nominal,
            "candidate_requirement": requirement,
            "state": state,
        })

    if part_type == "OUTPUT_SHAFT":
        add("SHAFT_OD", "diameter", f"{spec['shaft_d']:.3f} mm", "bearing fit, finish and runout SELECTION REQUIRED", "OPEN")
        add("THROUGH_BORE", "diameter", f"{max(2.0, spec['shaft_d'] * 0.62):.3f} mm", "wall/strength and cable use SELECTION REQUIRED", "OPEN")
        add("AXIAL_RETENTION", "shoulder/groove/thread", "ABSENT FROM CURRENT SOLID", "add two-sided bearing shoulders and released retention", "BLOCKING REDESIGN")
    elif part_type == "INTERFACE_PLATE":
        add("PLATE_ENVELOPE", "size", f"{spec['plate_w']:.3f} x {spec['plate_h']:.3f} x {spec['plate_t']:.3f} mm", "general tolerance and flatness SELECTION REQUIRED", "OPEN")
        add("MOUNT_PATTERN", "hole pattern", f"4 x DIA {spec['hole_d']:.3f} on {spec['pattern_x']:.3f} x {spec['pattern_y']:.3f} mm", "tapped side, insert, clearance and true position SELECTION REQUIRED", "OPEN")
        add("CENTRAL_CLEARANCE", "diameter", f"{spec['shaft_d']:.3f} mm nominal", "bearing seat/shaft clearance function SELECTION REQUIRED", "OPEN")
    elif part_type == "CATALOGUE_BEARING_ENVELOPE":
        bearing = body.BEARING_CANDIDATES[spec["bearing_id"]]
        add("CATALOGUE_ENVELOPE", "bearing", f"ID {bearing['bore_d']:.3f} / OD {bearing['outer_d']:.3f} / W {bearing['width']:.3f} mm", "exact suffix, life, fit, lubrication and received identity SELECTION REQUIRED", "CATALOGUE SELECTION OPEN")
    elif "PULLEY" in part_type:
        diameter = spec.get("output_pulley_d", 32.0) if part_type.startswith("OUTPUT") else spec.get("motor_pulley_d", 24.0)
        add("SMOOTH_ENVELOPE", "diameter", f"{diameter:.3f} mm x 12.000 mm wide", "replace with exact pitch/tooth/flange/bore/retention definition", "BLOCKING REDESIGN")
        add("TIMING_TEETH", "tooth geometry", "ABSENT FROM CURRENT SOLID", "catalogue order code or released tooth geometry required", "BLOCKING REDESIGN")
    else:
        add("ACTUATOR_INTERFACE", "spline/horn/clamp", "ABSENT FROM CURRENT SOLID", "exact actuator product interface and secondary retention required", "BLOCKING REDESIGN")
        add("OUTPUT_INTERFACE", "shaft/rack/tendon interface", "ABSENT OR PACKAGING-ONLY", "released torque/load path required", "BLOCKING REDESIGN")
    return rows


def render_index(rows: list[dict], counts: Counter) -> str:
    groups = []
    for axis_id in sorted({row["axis_id"] for row in rows}):
        axis_rows = [row for row in rows if row["axis_id"] == axis_id]
        table_rows = []
        for row in axis_rows:
            files = "—"
            if row["step_path"]:
                files = f'<a href="{html.escape(row["step_path"])}">STEP</a> · <a href="{html.escape(row["svg_path"])}">SVG</a>'
                if row["dxf_path"]:
                    files += f' · <a href="{html.escape(row["dxf_path"])}">DXF</a>'
            table_rows.append(
                f'<tr><td>{html.escape(row["part_id"])}</td><td>{html.escape(row["part_type"])}</td>'
                f'<td>{html.escape(row["disposition"])}</td><td>{files}</td></tr>'
            )
        groups.append(
            f'<details><summary>{html.escape(axis_id)} · {len(axis_rows)} hardware items</summary>'
            f'<div class="tablewrap"><table><thead><tr><th>Part</th><th>Type</th><th>Disposition</th><th>Files</th></tr></thead>'
            f'<tbody>{"".join(table_rows)}</tbody></table></div></details>'
        )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 joint hardware manufacturing P0.1</title><style>
:root{{--navy:#0d2d57;--blue:#158fd0;--sky:#dff4ff;--gold:#f4b400;--paper:#f8fcff}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--paper);color:var(--navy);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,#0d2d57,#1769aa);color:white;padding:32px max(18px,calc((100% - 1180px)/2))}}.warning{{background:var(--gold);color:#142746;padding:15px 18px;border-radius:14px;font-weight:850}}h1{{font-size:clamp(34px,5vw,61px);line-height:1.06}}h2{{font-size:clamp(26px,3vw,39px);margin-top:46px}}main{{max-width:1180px;margin:auto;padding:28px 18px 72px}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.card,.panel,details{{background:white;border:2px solid #9ed9f6;border-radius:16px;overflow:hidden}}.card,.panel{{padding:18px}}.metric{{font-size:31px;font-weight:850}}.hold{{border-left:9px solid var(--gold)}}details{{margin:14px 0}}summary{{cursor:pointer;background:var(--navy);color:white;padding:15px 17px;font-size:18px;font-weight:850}}.tablewrap{{overflow:auto}}table{{border-collapse:collapse;min-width:920px;width:100%}}th,td{{padding:12px 13px;border-bottom:1px solid #cdeafb;text-align:left;vertical-align:top;font-size:16px}}th{{background:#e6f6fe;font-size:14px}}a{{color:#075f9f;font-weight:760}}.meta{{font-size:14px}}@media(max-width:680px){{header{{padding:24px 16px}}main{{padding:20px 13px 60px}}}}
</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 · Whole-body P0.1</p><h1>Actual joint hardware—without calling placeholders parts.</h1><p>Every non-actuator joint item on all 25 axes is classified. Real current solids receive local-coordinate refinement files; catalogue and incomplete geometry is stopped before supplier upload.</p></header><main><section class="stats"><article class="card"><div class="metric">142 / 142</div><p>actual-axis hardware candidates classified</p></article><article class="card"><div class="metric">64</div><p>shaft and carrier refinement STEP/SVG files</p></article><article class="card"><div class="metric">39</div><p>catalogue bearing references—never custom fabricated</p></article><article class="card hold"><div class="metric">39</div><p>pulley and coupler definitions blocked for redesign</p></article></section><h2>What changed</h2><div class="panel hold"><p>The existing 98-part body/frame/hand package was never the whole robot manufacturing universe. This package adds the 142 actual-axis joint-hardware candidates. It deliberately withholds supplier files for 28 toothless pulley envelopes, 11 coupling placeholders and 39 catalogue bearing envelopes.</p><p><a href="joint-hardware-part-register.csv">Full 142-item register</a> · <a href="joint-hardware-feature-register.csv">geometry and missing-feature register</a> · <a href="source-binding.json">source binding</a></p></div><h2>All 25 axes</h2>{''.join(groups)}<h2>Authority boundary</h2><div class="panel hold"><p>These files advance editable geometry and configuration control only. Shafts still need shoulders, grooves, fits and material closure; carriers need thread/insert, tolerance and load closure. No file in this package authorizes procurement, fabrication, assembly, powered testing, motion or energization.</p><p class="meta">Counts: {dict(counts)}</p></div></main></body></html>'''


def replace_section(text: str, start: str, end: str, replacement: str, anchor: str) -> str:
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        return before + replacement + after
    if anchor not in text:
        raise RuntimeError(f"integration anchor missing: {anchor}")
    return text.replace(anchor, anchor + replacement, 1)


def integrate(status: dict) -> None:
    readme_path = WB / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "## Actual-axis joint-hardware manufacturing P0.1"
    block = f'''{marker}

The [joint-hardware manufacturing guide](joint-hardware-manufacturing-p0.1/index.html) classifies all {status['axis_hardware_count']} non-actuator hardware items on the 25 actual axes. It adds {status['local_refinement_step_count']} local-coordinate shaft/carrier STEP and SVG files plus {status['interface_plate_dxf_count']} carrier DXFs, while correctly withholding supplier files for {status['catalogue_bearing_reference_count']} catalogue bearing envelopes and {status['redesign_required_count']} toothless pulley/coupler placeholders.

This corrects the manufacturing-universe boundary: the 98 body/frame/hand parts were never the complete robot. Joint fits, shoulders, retention, toothed pulley products, actuator adapters, materials, tolerances, DFM, FAI and structural proof remain open.'''
    if marker in readme:
        begin = readme.index(marker)
        finish = readme.find("\n## ", begin + len(marker))
        readme = readme[:begin].rstrip() + "\n\n" + block + ("\n\n" + readme[finish + 1:] if finish >= 0 else "\n")
    else:
        readme = readme.rstrip() + "\n\n" + block + "\n"
    readme_path.write_text(readme, encoding="utf-8", newline="\n")

    start = "<!-- HR30-JOINT-HARDWARE-MFG-P01-START -->"
    end = "<!-- HR30-JOINT-HARDWARE-MFG-P01-END -->"
    section = f'''{start}<section id="joint-hardware-manufacturing"><h2>The 98 body parts were not the complete manufacturing universe</h2><div class="grid"><article class="card pass"><div class="metric">142 / 142</div><p>actual-axis joint-hardware items now classified.</p></article><article class="card pass"><div class="metric">64</div><p>shaft and interface-carrier refinement STEP/SVG files.</p></article><article class="card hold"><div class="metric">39</div><p>catalogue bearing envelopes blocked from custom fabrication.</p></article><article class="card pass"><div class="metric">39 / 39</div><p>pulley and coupling predecessor placeholders now mapped to named successors in the transmission-closure package.</p></article></div><p><a href="joint-hardware-manufacturing-p0.1/index.html">Open the actual-axis joint-hardware guide</a> · <a href="joint-hardware-manufacturing-p0.1/joint-hardware-part-register.csv">142-item register</a> · <a href="transmission-closure-p0.1/index.html">Inspect the successor transmissions</a>.</p></section>{end}'''
    page_path = WB / "index.html"
    page = replace_section(
        page_path.read_text(encoding="utf-8"), start, end, section,
        "<!-- HR30-FABRICATION-SOURCING-P01-END -->",
    )
    page_path.write_text(page, encoding="utf-8", newline="\n")

    root_path = ROOT / "index.html"
    root = root_path.read_text(encoding="utf-8")
    link = '<li><a href="hr30/whole-body-p0.1/joint-hardware-manufacturing-p0.1/index.html">Actual-axis joint-hardware manufacturing guide</a></li>'
    anchor = '<li><a href="hr30/whole-body-p0.1/fabrication-sourcing-p0.1/index.html">Fabrication sourcing and RFQ guide</a></li>'
    if link not in root:
        if anchor not in root:
            raise RuntimeError("root sourcing link missing")
        root = root.replace(anchor, anchor + link, 1)
        root_path.write_text(root, encoding="utf-8", newline="\n")

    status_path = WB / "package-status.json"
    package_status = json.loads(status_path.read_text(encoding="utf-8"))
    package_status.update({
        "actual_axis_joint_hardware_package_present": True,
        "actual_axis_joint_hardware_count": status["axis_hardware_count"],
        "joint_hardware_local_refinement_step_count": status["local_refinement_step_count"],
        "joint_hardware_catalogue_reference_count": status["catalogue_bearing_reference_count"],
        "joint_hardware_redesign_required_count": status["redesign_required_count"],
        "joint_hardware_complete_manufacturing_definition": False,
        "joint_hardware_procurement_authority": False,
        "joint_hardware_fabrication_authority": False,
    })
    status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")

    holds_path = WB / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H01":
            row["unresolved_item"] = (
                "All 25 axes and all 142 non-actuator actual-axis hardware items are now classified. Sixty-four shaft/carrier solids have local-coordinate refinement STEP/SVG files and 39 carriers have DXFs; 39 catalogue bearing envelopes are correctly excluded from custom manufacture. Twenty-eight pulley solids have no timing teeth/flanges and eleven couplers have no product-specific horn/spline/clamp interface, so those 39 items remain explicit redesign blockers. The 156 located whole-body carrier screws remain candidate hardware with torque, preload, locking and capacity open. Shaft shoulders/grooves/fits/materials, carrier inserts/tolerances/load proof, exact bearings, pulley/coupler products, DFM, FAI and physical proof remain open."
            )
        if row["hold_id"] == "HR30-P01-H06":
            row["unresolved_item"] = (
                "The custom-part universe now separates 98 body/frame/hand candidates from 142 actual-axis joint-hardware items. The body set has controlled STEP/SVG files, 45 DXFs, 24 cover STLs and five nonempty pre-RFQ batches. The joint set adds 64 shaft/carrier refinement STEP/SVG files and 39 carrier DXFs while withholding supplier files for 39 catalogue bearings and 39 incomplete pulley/coupler definitions. Exact materials/stock, tolerances/GD&T, threads/inserts, edge treatment, pulley/coupler redesign, DFM, FAI, structural proof and qualified review remain open."
            )
        if row["hold_id"] == "HR30-P01-H10":
            row["unresolved_item"] = (
                "Whole-body, module and actual-axis geometry now includes individual files for 98 body/frame/hand parts and 64 real current joint shaft/carrier solids, with all remaining joint hardware explicitly classified. Released manufacturing drawings, 39 pulley/coupler redesigns, fits, materials/processes, exact hardware, DFM, FAI, proof, physical test and qualified review remain open."
            )
    write_csv(holds_path, holds)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    components, axes, _, _ = body.build()
    axis_ids = [row["axis_id"] for row in axes]
    axis_rows = {row["axis_id"]: row for row in axes}
    hardware = [
        part for part in components
        if part.physical and part.name.startswith("JMOD_")
        and not part.name.endswith("_ACTUATOR_VENDOR_CANDIDATE")
    ]
    if len(hardware) != AXIS_HARDWARE_COUNT:
        raise RuntimeError(f"expected {AXIS_HARDWARE_COUNT} axis-hardware parts, found {len(hardware)}")

    part_rows: list[dict] = []
    feature_rows: list[dict] = []
    counts: Counter[str] = Counter()
    for part in sorted(hardware, key=lambda item: item.name):
        axis_id = axis_for_name(part.name, axis_ids)
        family_id = body.joint_module_family(axis_id)
        spec = body.JOINT_MODULE_FAMILIES[family_id]
        part_type = type_for_name(part.name)
        disposition, route, release_state, exportable = disposition_for(part_type)
        counts[part_type] += 1
        center = part.shape.Center()
        local = part.shape.translate((-center.x, -center.y, -center.z))
        box = local.BoundingBox()
        step_rel = svg_rel = dxf_rel = step_hash = svg_hash = dxf_hash = ""
        if exportable:
            part_dir = OUT / "parts" / axis_id / part.name
            part_dir.mkdir(parents=True)
            step_path = part_dir / f"{part.name}.step"
            cq.exporters.export(local, str(step_path))
            body.canonicalize_step(step_path)
            svg_path = part_dir / f"{part.name}.svg"
            export_svg(local, svg_path)
            step_rel = step_path.relative_to(OUT).as_posix()
            svg_rel = svg_path.relative_to(OUT).as_posix()
            step_hash = sha256(step_path)
            svg_hash = sha256(svg_path)
            if part_type == "INTERFACE_PLATE":
                dxf_path = part_dir / f"{part.name}_profile.dxf"
                export_plate_dxf(local, dxf_path)
                dxf_rel = dxf_path.relative_to(OUT).as_posix()
                dxf_hash = sha256(dxf_path)
        bearing = body.BEARING_CANDIDATES[spec["bearing_id"]]
        part_rows.append({
            "part_id": part.name,
            "axis_id": axis_id,
            "region": axis_rows[axis_id]["region"],
            "side": axis_rows[axis_id]["side"],
            "family_id": family_id,
            "part_type": part_type,
            "quantity_candidate": 1,
            "material_or_product_candidate": material_for(part_type),
            "catalogue_candidate": bearing["designation"] if part_type == "CATALOGUE_BEARING_ENVELOPE" else "",
            "catalogue_url": bearing["url"] if part_type == "CATALOGUE_BEARING_ENVELOPE" else "",
            "route": route,
            "disposition": disposition,
            "bbox_local_mm": f"{box.xlen:.3f} x {box.ylen:.3f} x {box.zlen:.3f}",
            "volume_mm3": f"{local.Volume():.6f}",
            "assembly_source_center_mm": f"({center.x:.6f}, {center.y:.6f}, {center.z:.6f})",
            "localization_transform": f"TRANSLATE ({-center.x:.6f}, {-center.y:.6f}, {-center.z:.6f}) mm; ORIENTATION UNCHANGED",
            "step_path": step_rel,
            "step_sha256": step_hash,
            "svg_path": svg_rel,
            "svg_sha256": svg_hash,
            "dxf_path": dxf_rel,
            "dxf_sha256": dxf_hash,
            "release_state": release_state,
            "authority": "NO PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        })
        feature_rows.extend(feature_rows_for(axis_id, family_id, part.name, part_type, spec))

    type_counts = Counter(row["part_type"] for row in part_rows)
    export_count = sum(bool(row["step_path"]) for row in part_rows)
    dxf_count = sum(bool(row["dxf_path"]) for row in part_rows)
    bearing_count = type_counts["CATALOGUE_BEARING_ENVELOPE"]
    redesign_count = sum(
        type_counts[key] for key in type_counts
        if "PULLEY_ENVELOPE" in key or "COUPLER_PLACEHOLDER" in key
    )
    if (export_count, dxf_count, bearing_count, redesign_count) != (
        REAL_SOLID_EXPORT_COUNT, 39, BEARING_REFERENCE_COUNT, REDESIGN_REQUIRED_COUNT
    ):
        raise RuntimeError(
            f"joint-hardware classification drift: exports={export_count}, dxf={dxf_count}, "
            f"bearings={bearing_count}, redesign={redesign_count}"
        )
    write_csv(OUT / "joint-hardware-part-register.csv", part_rows)
    write_csv(OUT / "joint-hardware-feature-register.csv", feature_rows)
    source_binding = {
        "identifier": IDENTIFIER,
        "body_architecture_generator": "tools/generate_hr30_body_architecture_p01.py",
        "body_architecture_generator_sha256": sha256(ROOT / "tools" / "generate_hr30_body_architecture_p01.py"),
        "mass_reconciliation_generator": "tools/generate_hr30_mass_reconciliation_p01.py",
        "mass_reconciliation_generator_sha256": sha256(ROOT / "tools" / "generate_hr30_mass_reconciliation_p01.py"),
        "joint_family_generator": "tools/generate_hr30_joint_family_cad_p01.py",
        "joint_family_generator_sha256": sha256(ROOT / "tools" / "generate_hr30_joint_family_cad_p01.py"),
        "axis_count": len(axis_ids),
        "warning": WARNING,
    }
    (OUT / "source-binding.json").write_text(json.dumps(source_binding, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER,
        "axis_count": len(axis_ids),
        "family_count": len({row["family_id"] for row in part_rows}),
        "axis_hardware_count": len(part_rows),
        "local_refinement_step_count": export_count,
        "local_refinement_svg_count": export_count,
        "interface_plate_dxf_count": dxf_count,
        "catalogue_bearing_reference_count": bearing_count,
        "redesign_required_count": redesign_count,
        "part_type_counts": dict(sorted(type_counts.items())),
        "complete_joint_hardware_manufacturing_definition": False,
        "materials_selected": False,
        "fits_tolerances_released": False,
        "dfm_complete": False,
        "fai_complete": False,
        "structural_capacity_validated": False,
        "procurement_authority": False,
        "fabrication_authority": False,
        "assembly_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }
    (OUT / "joint-hardware-manufacturing-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# HR-30 actual-axis joint-hardware manufacturing P0.1\n\n**{WARNING}**\n\n"
        f"All {len(part_rows)} non-actuator joint-hardware candidates on the 25 actual axes are classified. "
        f"The package exports {export_count} local-coordinate shaft/carrier refinement STEP/SVG files and {dxf_count} carrier DXFs. "
        f"It intentionally withholds supplier files for {bearing_count} catalogue bearing envelopes and {redesign_count} incomplete pulley/coupler definitions.\n\n"
        "This is editable refinement geometry, not a drawing release or work authority.\n",
        encoding="utf-8",
        newline="\n",
    )
    (OUT / "index.html").write_text(render_index(part_rows, type_counts), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "joint-hardware-manufacturing-source.py")
    files = [path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", [{
        "path": path.relative_to(OUT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "warning": WARNING,
    } for path in sorted(files)])
    integrate(status)
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
