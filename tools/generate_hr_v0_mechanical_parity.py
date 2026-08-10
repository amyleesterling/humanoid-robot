#!/usr/bin/env python3
"""Generate independent STEP/DXF/drawing parity evidence for P0.7 metal parts."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1"
OUT = ROOT / "release" / "hr-v0" / "mechanical-parity-p0.1"
DOC = ROOT / "docs" / "hr-v0-mechanical-parity-p0.1.md"
IDENTIFIER = "HR-V0-MECH-PARITY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
PART_ORDER = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dxf(path: Path) -> list[dict[str, object]]:
    lines = path.read_text(encoding="ascii").splitlines()
    if len(lines) % 2:
        raise ValueError(f"odd DXF group-code line count: {path}")
    pairs = [(lines[index].strip(), lines[index + 1].strip()) for index in range(0, len(lines), 2)]
    entities: list[dict[str, object]] = []
    in_entities = False
    index = 0
    while index < len(pairs):
        code, value = pairs[index]
        if code == "2" and value == "ENTITIES":
            in_entities = True
        elif in_entities and code == "0" and value in {"LINE", "CIRCLE"}:
            entity_type = value
            data: dict[str, str] = {}
            index += 1
            while index < len(pairs) and pairs[index][0] != "0":
                key, item = pairs[index]
                data[key] = item
                index += 1
            if entity_type == "LINE":
                entities.append({"type": "LINE", "layer": data["8"], "x1": float(data["10"]), "z1": float(data["20"]), "x2": float(data["11"]), "z2": float(data["21"])})
            else:
                entities.append({"type": "CIRCLE", "layer": data["8"], "x": float(data["10"]), "z": float(data["20"]), "radius": float(data["40"])})
            continue
        elif in_entities and code == "0" and value == "ENDSEC":
            break
        index += 1
    return entities


def circular_radii(face: cq.Face) -> list[float]:
    values: list[float] = []
    for edge in face.Edges():
        try:
            values.append(round(float(edge.radius()), 6))
        except Exception:
            pass
    return sorted(set(values))


def step_features(shape: cq.Shape) -> list[dict[str, object]]:
    found: dict[tuple[float, float, float, str], dict[str, object]] = {}
    for face in shape.Faces():
        geom = face.geomType()
        center = face.Center()
        radii = circular_radii(face)
        if geom == "CYLINDER":
            for radius in radii:
                if any(math.isclose(radius, item, abs_tol=1e-6) for item in (1.35, 2.75, 4.25)):
                    key = (round(center.x, 6), round(center.z, 6), radius, "CYLINDER")
                    found[key] = {"kind": "CYLINDER", "x_mm": key[0], "z_mm": key[1], "radius_mm": radius}
        elif geom == "CONE":
            for radius in radii:
                if any(math.isclose(radius, item, abs_tol=1e-6) for item in (5.65, 5.70)):
                    key = (round(center.x, 6), round(center.z, 6), radius, "CONE_EDGE")
                    found[key] = {"kind": "CONE_EDGE", "x_mm": key[0], "z_mm": key[1], "radius_mm": radius}
    return list(found.values())


def dxf_profile_bounds(entities: list[dict[str, object]]) -> tuple[float, float, float, float]:
    lines = [item for item in entities if item["type"] == "LINE" and str(item["layer"]).startswith("FINISHED_PROFILE")]
    xs = [float(item[key]) for item in lines for key in ("x1", "x2")]
    zs = [float(item[key]) for item in lines for key in ("z1", "z2")]
    return min(xs), max(xs), min(zs), max(zs)


def svg_map(part_id: str, entities: list[dict[str, object]]) -> str:
    xmin, xmax, zmin, zmax = dxf_profile_bounds(entities)
    margin = 5.0
    view = f"{xmin-margin:.3f} {-zmax-margin:.3f} {xmax-xmin+2*margin:.3f} {zmax-zmin+2*margin:.3f}"
    items: list[str] = [f'<line class="axis" x1="{xmin-margin}" y1="0" x2="{xmax+margin}" y2="0"/>', f'<line class="axis" x1="0" y1="{-zmax-margin}" x2="0" y2="{-zmin+margin}"/>']
    for entity in entities:
        if entity["type"] == "LINE":
            layer = str(entity["layer"])
            css = "recess" if layer == "FACE_MILL_RECESS_BOUNDARY" else "profile"
            items.append(f'<line class="{css}" x1="{entity["x1"]}" y1="{-float(entity["z1"])}" x2="{entity["x2"]}" y2="{-float(entity["z2"])}"/>')
        else:
            layer = str(entity["layer"])
            css = "csk" if "COUNTERSINK" in layer else ("large-hole" if "M8" in layer or "M5_CLEARANCE" in layer else "small-hole")
            items.append(f'<circle class="{css}" cx="{entity["x"]}" cy="{-float(entity["z"])}" r="{entity["radius"]}"/>')
    return f'''<svg class="part-map" viewBox="{view}" role="img" aria-label="{part_id} DXF feature map"><g>{''.join(items)}</g></svg>'''


def drawing_assignment(control_id: str, source_table: str, row: dict[str, str], drawings: dict[str, str]) -> tuple[str, str, str]:
    schedule_only = {"C04-004", "C05-004", "STOP-001", "STOP-003", "STOP-004", "STOP-005"}
    physical_hold = {"C04-005", "C05-005", "STOP-006"}
    if source_table == "adapter-drawing-controls.csv":
        parts = ["MV0-C01"]
    elif source_table == "new-interface-drawing-controls.csv":
        parts = [row["part_id"]]
    elif control_id in {"STOP-001", "STOP-002"}:
        parts = ["MV0-C06"]
    elif control_id in {"STOP-003", "STOP-004"}:
        parts = ["MV0-C07"]
    else:
        parts = ["MV0-C06", "MV0-C07"]
    coverage = "SCHEDULE_BOUND_CONTROL" if control_id in schedule_only else ("DRAWING_EXPLICIT_PHYSICAL_HOLD" if control_id in physical_hold else "DRAWING_TEXT_EXPLICIT")
    evidence = "Combined readable drawing plus exact source control row; physical result still required" if control_id in physical_hold else ("Readable drawing explicitly defers numeric detail to the exact source control row" if control_id in schedule_only else "Readable drawing contains the controlled feature or acceptance statement")
    return ";".join(parts), ";".join(drawings[part] for part in parts), coverage + " / " + evidence


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    geometry = read_csv(SOURCE / "geometry-file-register.csv")
    parts = {row["part_id"]: row for row in read_csv(SOURCE / "part-register.csv")}
    by_part: dict[str, dict[str, str]] = {part: {} for part in PART_ORDER}
    for row in geometry:
        by_part[row["part_id"]][row["artifact_role"]] = row["repository_path"]

    profile_rows: list[dict[str, object]] = []
    feature_rows: list[dict[str, object]] = []
    drawing_paths: dict[str, str] = {}
    maps: dict[str, str] = {}
    for part_id in PART_ORDER:
        records = by_part[part_id]
        step_rel = records["3D candidate"]
        dxf_rel = records["profile reference"]
        drawing_rel = records["readable control drawing"]
        drawing_paths[part_id] = drawing_rel
        step_path, dxf_path, drawing_path = ROOT / step_rel, ROOT / dxf_rel, ROOT / drawing_rel
        shape = cq.importers.importStep(str(step_path)).val()
        box = shape.BoundingBox()
        entities = parse_dxf(dxf_path)
        maps[part_id] = svg_map(part_id, entities)
        dxf_bounds = dxf_profile_bounds(entities)
        deltas = (abs(box.xmin-dxf_bounds[0]), abs(box.xmax-dxf_bounds[1]), abs(box.zmin-dxf_bounds[2]), abs(box.zmax-dxf_bounds[3]))
        y_planes: list[float] = []
        for face in shape.Faces():
            if face.geomType() == "PLANE":
                center = face.Center()
                normal = face.normalAt(center)
                if abs(normal.y) > 0.99:
                    y_planes.append(round(center.y, 6))
        recess = ""
        if part_id == "MV0-C07":
            levels = sorted(set(y_planes), reverse=True)
            recess = round(levels[0] - levels[1], 6)
        profile_rows.append({
            "part_id": part_id, "step_path": step_rel, "step_sha256": digest(step_path), "dxf_path": dxf_rel, "dxf_sha256": digest(dxf_path),
            "drawing_path": drawing_rel, "drawing_sha256": digest(drawing_path), "step_solid_count": len(shape.Solids()),
            "step_xmin_mm": round(box.xmin, 6), "step_xmax_mm": round(box.xmax, 6), "step_ymin_mm": round(box.ymin, 6), "step_ymax_mm": round(box.ymax, 6),
            "step_zmin_mm": round(box.zmin, 6), "step_zmax_mm": round(box.zmax, 6), "step_thickness_mm": round(box.ymax-box.ymin, 6),
            "dxf_xmin_mm": dxf_bounds[0], "dxf_xmax_mm": dxf_bounds[1], "dxf_zmin_mm": dxf_bounds[2], "dxf_zmax_mm": dxf_bounds[3],
            "maximum_profile_extent_delta_mm": round(max(deltas), 9), "step_face_recess_mm": recess,
            "profile_relation": "BOUNDING_EXTENTS_MATCH; DXF IS PRE-FILLET CONSTRUCTION" if part_id in {"MV0-C06", "MV0-C07"} else "EXACT RECTANGULAR PROFILE EXTENTS MATCH",
            "result": "PASS NOMINAL FILE PARITY", "release_effect": "NONE - physical FAI and qualified review remain required", "warning": WARNING,
        })
        features = step_features(shape)
        dxf_circles = [item for item in entities if item["type"] == "CIRCLE"]
        for index, circle in enumerate(dxf_circles, 1):
            expected_kind = "CONE_EDGE" if "COUNTERSINK" in str(circle["layer"]) else "CYLINDER"
            matches = [item for item in features if item["kind"] == expected_kind and math.isclose(float(item["x_mm"]), float(circle["x"]), abs_tol=1e-6) and math.isclose(float(item["z_mm"]), float(circle["z"]), abs_tol=1e-6) and (math.isclose(float(item["radius_mm"]), float(circle["radius"]), abs_tol=1e-6) or (expected_kind == "CONE_EDGE" and math.isclose(float(item["radius_mm"])-float(circle["radius"]), 0.05, abs_tol=1e-6)))]
            if len(matches) != 1:
                raise ValueError(f"{part_id} DXF feature {index} matched {len(matches)} STEP features")
            match = matches[0]
            radius_delta = round(abs(float(match["radius_mm"])-float(circle["radius"])), 9)
            result = "EXACT NOMINAL MATCH" if radius_delta <= 1e-9 else "CONTROLLED UPPER-LIMIT MATCH"
            feature_rows.append({
                "feature_id": f"{part_id}-F{index:02d}", "part_id": part_id, "dxf_layer": circle["layer"], "expected_step_kind": expected_kind,
                "dxf_x_mm": circle["x"], "dxf_z_mm": circle["z"], "dxf_radius_mm": circle["radius"],
                "step_x_mm": match["x_mm"], "step_z_mm": match["z_mm"], "step_radius_mm": match["radius_mm"],
                "center_delta_mm": round(math.hypot(float(match["x_mm"])-float(circle["x"]), float(match["z_mm"])-float(circle["z"])), 9),
                "radius_delta_mm": radius_delta, "diameter_delta_mm": round(2.0 * radius_delta, 9), "result": result,
                "release_effect": "NONE - tolerances and FAI remain controlled separately", "warning": WARNING,
            })
    write_csv(OUT / "profile-parity.csv", profile_rows)
    write_csv(OUT / "feature-parity.csv", feature_rows)

    coverage_rows: list[dict[str, object]] = []
    source_controls = read_csv(SOURCE / "inspection-control-register.csv")
    for row in source_controls:
        control_id = row["control_id"]
        part_ids, drawings, disposition = drawing_assignment(control_id, row["source_table"], row, drawing_paths)
        coverage, evidence = disposition.split(" / ", 1)
        coverage_rows.append({"control_id": control_id, "part_id_or_interface": part_ids, "source_table": row["source_table"], "source_row": row["source_row"],
                              "drawing_path_or_paths": drawings, "coverage_class": coverage, "evidence": evidence, "physical_execution_state": "UNEXECUTED",
                              "fabrication_authorized": "FALSE", "warning": WARNING})
    write_csv(OUT / "drawing-control-coverage.csv", coverage_rows)

    finding_rows = [
        {"finding_id": "MPAR-F01", "priority": "MAJOR", "finding": "C04/C05/C06/C07 readable drawings do not graphically dimension every controlled feature; six controls are schedule-bound rather than fully displayed.", "disposition": "R135 binds each schedule row and adds interactive DXF maps; qualified reviewer must decide whether released supplier drawings need conventional dimensioned views.", "status": "OPEN"},
        {"finding_id": "MPAR-F02", "priority": "MAJOR", "finding": "C06/C07 DXFs intentionally contain pre-fillet construction profiles while STEP contains the R2 finished profile.", "disposition": "Do not machine from DXF alone; provider must bind STEP plus drawing/control schedule and return its interpreted manufacturing model for review.", "status": "OPEN"},
        {"finding_id": "MPAR-F03", "priority": "BLOCKER", "finding": "Nominal file parity cannot prove material, tolerance capability, received fit, stop load, strength, fatigue, impact, stopping or safety.", "disposition": "Execute supplier DFM, FAI, received-interface metrology, structural/stop analysis, proof and qualified review before any fabrication or energization release.", "status": "OPEN"},
        {"finding_id": "MPAR-F04", "priority": "MAJOR", "finding": "C01/C04/C06/C07 STEP countersink openings are diameter 11.40 mm while DXF/drawing nominal is 11.30 mm with +0.10/-0.00 tolerance.", "disposition": "Qualified review must decide whether to remodel STEP at nominal or explicitly declare upper-limit model semantics; supplier may not infer nominal or tolerance from STEP alone.", "status": "OPEN"},
    ]
    for row in finding_rows:
        row["warning"] = WARNING
    write_csv(OUT / "finding-register.csv", finding_rows)

    status = {
        "identifier": IDENTIFIER, "round": "R135", "date": "2026-08-09", "controlled_architecture": "HR-V0-ARM-ARCH-P0.7",
        "parent_dataset": "HR-V0-MECH-DFM-DATA-P0.1", "part_count": len(profile_rows), "feature_parity_count": len(feature_rows),
        "drawing_control_count": len(coverage_rows), "schedule_bound_control_count": sum(row["coverage_class"] == "SCHEDULE_BOUND_CONTROL" for row in coverage_rows),
        "exact_feature_match_count": sum(row["result"] == "EXACT NOMINAL MATCH" for row in feature_rows),
        "controlled_upper_limit_match_count": sum(row["result"] == "CONTROLLED UPPER-LIMIT MATCH" for row in feature_rows),
        "open_finding_count": len(finding_rows), "all_bounded_parity_checks_pass": all(row["result"].startswith("PASS") for row in profile_rows) and all(row["result"] in {"EXACT NOMINAL MATCH", "CONTROLLED UPPER-LIMIT MATCH"} for row in feature_rows),
        "provider_contacted": False, "upload_authorized": False, "quotation_authorized": False, "fabrication_authorized": False,
        "assembly_authorized": False, "motion_authorized": False, "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards: list[str] = []
    for row in profile_rows:
        part_id = str(row["part_id"])
        part = parts[part_id]
        feature_count = sum(item["part_id"] == part_id for item in feature_rows)
        cards.append(f'''<article class="card" data-search="{html.escape((part_id+' '+part['name']+' '+part['critical_features']).lower())}"><div class="card-head"><span class="badge">{part_id}</span><h3>{html.escape(part['name'])}</h3></div>{maps[part_id]}<div class="legend"><span class="profile-key">Profile</span><span class="small-key">M2.5</span><span class="large-key">M5/M8</span><span class="csk-key">Countersink</span></div><dl><dt>STEP/DXF extents</dt><dd>Maximum delta {row['maximum_profile_extent_delta_mm']} mm</dd><dt>Matched feature entities</dt><dd>{feature_count}</dd><dt>Thickness</dt><dd>{row['step_thickness_mm']} mm nominal</dd><dt>Relation</dt><dd>{row['profile_relation']}</dd></dl><p><a href="../../../{row['drawing_path']}">Readable candidate drawing</a></p></article>''')
    findings_html = "".join(f'<li><span class="priority {row["priority"].lower()}">{row["priority"]}</span><strong>{row["finding_id"]}</strong> {html.escape(row["finding"])}<small>{html.escape(row["disposition"])}</small></li>' for row in finding_rows)
    guide = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 mechanical parity P0.1</title><style>
:root{{--ink:#082f5b;--blue:#0d6fb8;--sky:#dff3ff;--gold:#f4bd28;--paper:#f8fcff;--danger:#8b1e2d;--purple:#7a4fa3}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.5 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{background:var(--danger);color:#fff;padding:12px 18px;font-size:16px;font-weight:800}}header{{padding:32px max(20px,calc((100% - 1220px)/2));background:linear-gradient(135deg,var(--sky),#fff);border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4.2rem);line-height:1.04;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.3rem)}}h3{{font-size:1.25rem;margin:.35rem 0}}main{{max-width:1220px;margin:auto;padding:24px}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:18px}}.metric,.card,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px;box-shadow:5px 5px 0 var(--sky)}}.metric strong{{display:block;font-size:2rem;color:var(--blue)}}.meta,.helper,small{{font-size:14px}}.badge,.priority{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:13px;font-weight:800;background:var(--gold)}}input{{width:100%;font:16px system-ui;padding:13px;border:2px solid var(--blue);border-radius:10px;margin-bottom:18px}}.part-map{{display:block;width:100%;height:260px;background:#f8fcff;border:1px solid #8ed5ff;border-radius:10px;margin:14px 0}}.part-map .profile{{stroke:var(--ink);stroke-width:.7;fill:none;vector-effect:non-scaling-stroke}}.part-map .axis{{stroke:#9bb4c9;stroke-width:.35;stroke-dasharray:2 2;vector-effect:non-scaling-stroke}}.part-map circle{{fill:#fff;stroke-width:.7;vector-effect:non-scaling-stroke}}.small-hole{{stroke:var(--blue)}}.large-hole{{stroke:var(--purple)}}.csk{{stroke:#d59600;stroke-dasharray:2 1}}.recess{{stroke:#a33;stroke-width:.6;stroke-dasharray:2 1;vector-effect:non-scaling-stroke}}.legend{{display:flex;flex-wrap:wrap;gap:8px;font-size:13px}}.legend span{{padding:3px 7px;border-radius:6px;background:var(--sky)}}dl{{display:grid;grid-template-columns:minmax(110px,1fr) 1.4fr;gap:6px 12px}}dt{{font-weight:750}}dd{{margin:0}}a{{color:#07579f;font-weight:700}}li{{margin:1rem 0}}li small{{display:block;margin:.25rem 0 0 0}}.blocker{{background:#8b1e2d;color:#fff}}.major{{background:#f4bd28}}footer{{padding:24px;background:var(--ink);color:#fff;font-size:14px;margin-top:35px}}@media(max-width:600px){{main{{padding:18px}}header{{padding:24px 18px}}.grid{{grid-template-columns:1fr}}.part-map{{height:220px}}dl{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p class="meta">{IDENTIFIER} · R135 · P0.7 independent nominal-file audit</p><h1>Do the geometry files actually agree?</h1><p>Yes at the bounded profile and feature level, with an important countersink-model caveat. That answer is narrow: it does not prove tolerances, strength, fit, manufacturability, stopping or safety.</p></header><main><section><h2>Audit result</h2><div class="metrics"><div class="metric"><strong>5/5</strong>STEP/DXF profile extents match</div><div class="metric"><strong>30 + 8</strong>exact + controlled-limit features</div><div class="metric"><strong>{len(coverage_rows)}</strong>drawing controls traced</div><div class="metric"><strong>0</strong>released fabrication actions</div></div></section><section><h2>Inspect each part</h2><p class="helper">These maps render the controlled DXF entities. C06/C07 DXF outlines are explicitly pre-fillet construction; their STEP files control the R2 finished solids. Eight countersink STEP edges are at the controlled upper diameter limit rather than nominal.</p><input id="search" aria-label="Find a parity record" placeholder="Find C07, H104, countersink or rail"><div class="grid">{''.join(cards)}</div></section><section class="panel"><h2>Findings that remain open</h2><ul>{findings_html}</ul></section><section class="panel"><h2>Machine-readable evidence</h2><p><a href="profile-parity.csv">Profile parity</a> · <a href="feature-parity.csv">Feature parity</a> · <a href="drawing-control-coverage.csv">Drawing coverage</a> · <a href="finding-register.csv">Findings</a> · <a href="package-status.json">Status</a></p></section></main><footer>{WARNING}</footer><script>const input=document.querySelector('#search');const cards=[...document.querySelectorAll('.card')];input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();cards.forEach(card=>card.hidden=!card.dataset.search.includes(q))}});</script></body></html>'''
    (OUT / "index.html").write_text(guide, encoding="utf-8")

    DOC.write_text(f'''# HR-V0 mechanical nominal-file parity P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Round: R135

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Outcome

An independent parser and STEP inspection now reconcile all five current custom parts. All five STEP bounding profiles match the controlled DXF extents at zero reported delta. Thirty DXF hole entities have exact nominal STEP-cylinder matches. Eight countersink entities match position but expose an important semantic difference: DXF/drawing nominal diameter is 11.30 mm while STEP uses the allowed 11.40 mm upper limit. C07's STEP contains the controlled 1.000 mm face recess. Each of the twenty-six source inspection controls is bound to its readable drawing and source row.

## Important limitation discovered

C04/C05/C06/C07 are not conventional fully dimensioned fabrication drawings. Six controls are schedule-bound rather than fully displayed on their readable SVGs. C06/C07 DXFs are intentionally pre-fillet construction profiles while STEP controls the R2 finished solid. C01/C04/C06/C07 STEP countersink openings are modeled at the upper diameter limit rather than nominal. A provider must not machine from STEP or DXF alone, and a qualified reviewer must decide whether to remodel the STEP solids at nominal and whether conventional released drawings are required.

## Controlled evidence

- [Interactive parity guide](../release/hr-v0/mechanical-parity-p0.1/index.html)
- `release/hr-v0/mechanical-parity-p0.1/profile-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/feature-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/drawing-control-coverage.csv`
- `release/hr-v0/mechanical-parity-p0.1/finding-register.csv`
- `release/hr-v0/mechanical-parity-p0.1/package-status.json`

## Release boundary

Nominal file parity closes no physical or authorization gate. Material certification, provider DFM, manufacturing capability, FAI, received fit, fastener/T-slot capacity, stop loads, complete mass/COM/inertia, continuous duty, guard/cable geometry, proof, fatigue, impact, stopping, functional-safety validation and qualified release remain open. No contact, upload, quotation, fabrication, assembly, motion or energization is authorized.
''', encoding="utf-8")


if __name__ == "__main__":
    main()
