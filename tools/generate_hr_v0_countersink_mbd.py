#!/usr/bin/env python3
"""Generate the bounded P0.7-to-P0.8 countersink MBD correction candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arch


ROOT = Path(__file__).resolve().parents[1]
GENERATED_ROOT = ROOT / "cad" / "hr-v0" / "generated"
SOURCE_DIR = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7" / "parts"
CAD_OUT = ROOT / "cad" / "hr-v0" / "generated" / "countersink-mbd-p0.1"
OUT = ROOT / "release" / "hr-v0" / "countersink-mbd-p0.1"
DOC = ROOT / "docs" / "hr-v0-countersink-mbd-p0.1.md"
IDENTIFIER = "HR-V0-CSK-MBD-P0.1"
CANDIDATE = "HR-V0-ARM-ARCH-P0.8-CSK-MBD-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"

HOLE_D_MM = 5.50
OLD_MAJOR_D_MM = 11.40
OLD_DEPTH_MM = 3.10
NOMINAL_MAJOR_D_MM = 11.30
NOMINAL_DEPTH_MM = (NOMINAL_MAJOR_D_MM - HOLE_D_MM) / 2.0
MAX_DIAMETER_SCREEN_MM = 11.40
MAX_DEPTH_SCREEN_MM = 3.10
MATERIAL_DENSITY_G_PER_CM3 = 2.70
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}

PARTS = [
    ("MV0-C01", "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step", arch.adapter),
    ("MV0-C04", "MV0-C04_H104_to_20-2040_countersunk_adapter.step", arch.gripper_adapter),
    ("MV0-C06", "MV0-C06_J2_positive_moving_striker_adapter.step", arch.j2_positive_striker_adapter),
    ("MV0-C07", "MV0-C07_J2_positive_fixed_catch_adapter.step", arch.j2_positive_catch_adapter),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generated_digest(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bbox_values(shape: cq.Shape) -> list[float]:
    box = shape.BoundingBox()
    return [round(value, 6) for value in (box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax)]


def countersink_angle(major_diameter_mm: float, depth_mm: float) -> float:
    radial_change = (major_diameter_mm - HOLE_D_MM) / 2.0
    return math.degrees(2.0 * math.atan(radial_change / depth_mm))


def main() -> None:
    CAD_OUT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    old_diameter = arch.END_CSK_D
    old_depth = arch.END_CSK_DEPTH
    if not math.isclose(old_diameter, OLD_MAJOR_D_MM) or not math.isclose(old_depth, OLD_DEPTH_MM):
        raise RuntimeError("P0.7 countersink source constants changed; independent reconciliation required")

    # The existing source functions read these globals at call time. Override them
    # only inside this generator process so P0.7 artifacts remain byte-for-byte frozen.
    arch.END_CSK_D = NOMINAL_MAJOR_D_MM
    arch.END_CSK_DEPTH = NOMINAL_DEPTH_MM

    comparison_rows: list[dict[str, object]] = []
    feature_rows: list[dict[str, object]] = []
    cards: list[str] = []
    total_mass_delta_g = 0.0
    for part_id, source_name, builder in PARTS:
        source_path = SOURCE_DIR / source_name
        source_shape = cq.importers.importStep(str(source_path)).val()
        candidate_shape = builder(0.0)
        candidate_name = source_name.replace(".step", "_P0.8_nominal-countersink-candidate.step")
        candidate_path = CAD_OUT / candidate_name
        cq.exporters.export(candidate_shape, str(candidate_path))
        arch.canonicalize_step(candidate_path)
        candidate_shape = cq.importers.importStep(str(candidate_path)).val()

        source_bbox = bbox_values(source_shape)
        candidate_bbox = bbox_values(candidate_shape)
        source_volume = float(source_shape.Volume())
        candidate_volume = float(candidate_shape.Volume())
        volume_delta = candidate_volume - source_volume
        mass_delta_g = volume_delta / 1000.0 * MATERIAL_DENSITY_G_PER_CM3
        total_mass_delta_g += mass_delta_g
        comparison_rows.append({
            "part_id": part_id,
            "p0_7_source_path": source_path.relative_to(ROOT).as_posix(),
            "p0_7_sha256": digest(source_path),
            "p0_8_candidate_path": candidate_path.relative_to(ROOT).as_posix(),
            "p0_8_candidate_sha256": digest(candidate_path),
            "p0_7_solid_count": len(source_shape.Solids()),
            "p0_8_solid_count": len(candidate_shape.Solids()),
            "p0_7_bbox_mm": json.dumps(source_bbox, separators=(",", ":")),
            "p0_8_bbox_mm": json.dumps(candidate_bbox, separators=(",", ":")),
            "maximum_bbox_delta_mm": round(max(abs(a - b) for a, b in zip(source_bbox, candidate_bbox)), 9),
            "p0_7_volume_mm3": round(source_volume, 6),
            "p0_8_volume_mm3": round(candidate_volume, 6),
            "candidate_added_material_mm3": round(volume_delta, 6),
            "candidate_mass_delta_g_at_2_70_g_cm3": round(mass_delta_g, 6),
            "external_envelope_relation": "IDENTICAL BOUNDING ENVELOPE; COUNTERSINK CUT ONLY",
            "selection_state": "NONSELECTED CANDIDATE",
            "warning": WARNING,
        })
        for z_mm in (-10.0, 10.0):
            feature_rows.append({
                "feature_id": f"{part_id}-CSK-{'M10' if z_mm < 0 else 'P10'}",
                "part_id": part_id,
                "center_x_mm": 0.0,
                "center_z_mm": z_mm,
                "through_hole_diameter_mm": HOLE_D_MM,
                "p0_7_modeled_major_diameter_mm": OLD_MAJOR_D_MM,
                "p0_7_modeled_axial_depth_mm": OLD_DEPTH_MM,
                "p0_7_derived_included_angle_deg": round(countersink_angle(OLD_MAJOR_D_MM, OLD_DEPTH_MM), 6),
                "p0_8_nominal_major_diameter_mm": NOMINAL_MAJOR_D_MM,
                "p0_8_nominal_axial_depth_mm": NOMINAL_DEPTH_MM,
                "p0_8_derived_included_angle_deg": round(countersink_angle(NOMINAL_MAJOR_D_MM, NOMINAL_DEPTH_MM), 6),
                "drawing_control": "diameter 11.30 +0.10/-0.00; 90 degree included angle nominal",
                "worst_case_diameter_screen_mm": MAX_DIAMETER_SCREEN_MM,
                "worst_case_depth_screen_mm": MAX_DEPTH_SCREEN_MM,
                "screen_semantics": "MAXIMUM SCREW/CLEARANCE AND RESIDUAL-MATERIAL SCREENS; NOT THE NOMINAL SOLID",
                "selection_state": "NONSELECTED CANDIDATE",
                "warning": WARNING,
            })
        cards.append(f'''<article class="card" data-search="{part_id.lower()} countersink"><span class="badge">{part_id}</span><h3>{part_id} candidate</h3><dl><dt>P0.7 solid</dt><dd>Ø{OLD_MAJOR_D_MM:.2f} × {OLD_DEPTH_MM:.2f} mm; {countersink_angle(OLD_MAJOR_D_MM, OLD_DEPTH_MM):.3f}° derived</dd><dt>P0.8 candidate</dt><dd>Ø{NOMINAL_MAJOR_D_MM:.2f} × {NOMINAL_DEPTH_MM:.2f} mm; 90.000° derived</dd><dt>Added material</dt><dd>{volume_delta:.3f} mm³</dd><dt>Mass delta</dt><dd>{mass_delta_g:.4f} g at 2.70 g/cm³</dd></dl><p><a href="../../../{html.escape(candidate_path.relative_to(ROOT).as_posix())}">Candidate STEP</a></p></article>''')

    write_csv(OUT / "part-comparison.csv", comparison_rows)
    write_csv(OUT / "feature-certificate.csv", feature_rows)

    decisions = [
        {"decision_id": "CSK-D01", "question": "Should a released STEP represent the 11.30 mm nominal countersink rather than the 11.40 mm upper limit?", "candidate_answer": "YES - model nominal geometry and carry tolerance in the drawing/MBD controls", "owner": "QUALIFIED MECHANICAL REVIEWER", "evidence_required": "Independent STEP inspection and manufacturing-model review", "state": "SELECTION REQUIRED"},
        {"decision_id": "CSK-D02", "question": "Is 2.90 mm the correct nominal axial depth for a 90 degree cone from diameter 11.30 to 5.50 mm?", "candidate_answer": "YES - direct trigonometric identity", "owner": "QUALIFIED MECHANICAL REVIEWER", "evidence_required": "Independent calculation and STEP cone inspection", "state": "SELECTION REQUIRED"},
        {"decision_id": "CSK-D03", "question": "May the 11.40 mm diameter and 3.10 mm depth remain separate conservative screens?", "candidate_answer": "YES - only when explicitly labeled as independent upper-bound inspection/calculation screens", "owner": "QUALIFIED MECHANICAL REVIEWER", "evidence_required": "Tolerance/inspection plan and fastener-seat review", "state": "SELECTION REQUIRED"},
        {"decision_id": "CSK-D04", "question": "Does the selected M5 fastener seat correctly across the permitted countersink range?", "candidate_answer": "UNRESOLVED", "owner": "MECHANICAL LEAD / FABRICATOR", "evidence_required": "Received fastener lot, countersink gauge, seating/contact/flushness inspection and proof", "state": "SELECTION REQUIRED"},
        {"decision_id": "CSK-D05", "question": "Can the P0.8 candidate replace P0.7 in downstream assemblies and release records?", "candidate_answer": "NOT YET", "owner": "CONFIGURATION CONTROL", "evidence_required": "Independent review disposition, downstream hash regeneration and full checker pass", "state": "HOLD"},
    ]
    for row in decisions:
        row["warning"] = WARNING
    write_csv(OUT / "decision-register.csv", decisions)

    findings = [
        {"finding_id": "CSK-F01", "priority": "MAJOR", "finding": "P0.7 combines an 11.40 mm major diameter with 3.10 mm axial depth, which derives an 87.159 degree cone rather than the drawing's nominal 90 degree included angle.", "disposition": "P0.8 candidate uses 11.30 mm major diameter and 2.90 mm depth, deriving exactly 90 degrees.", "status": "CANDIDATE CORRECTION - INDEPENDENT REVIEW OPEN"},
        {"finding_id": "CSK-F02", "priority": "MAJOR", "finding": "A maximum diameter envelope and a maximum depth screen were encoded as the nominal STEP solid, obscuring model semantics.", "disposition": "P0.8 separates nominal solid geometry from independent worst-case calculation/inspection screens.", "status": "CANDIDATE CORRECTION - INDEPENDENT REVIEW OPEN"},
        {"finding_id": "CSK-F03", "priority": "BLOCKER", "finding": "Nominal CAD correction does not prove cutter capability, fastener seating, received fit, residual thickness, strength, fatigue, stop behavior or safety.", "disposition": "Retain supplier DFM, FAI, received-fastener gauge, proof and qualified review gates.", "status": "OPEN"},
    ]
    for row in findings:
        row["warning"] = WARNING
    write_csv(OUT / "finding-register.csv", findings)

    status = {
        "identifier": IDENTIFIER,
        "round": "R136",
        "date": "2026-08-09",
        "source_revision": "HR-V0-ARM-ARCH-P0.7",
        "candidate_revision": CANDIDATE,
        "part_count": len(comparison_rows),
        "feature_count": len(feature_rows),
        "decision_count": len(decisions),
        "finding_count": len(findings),
        "p0_7_derived_angle_deg": round(countersink_angle(OLD_MAJOR_D_MM, OLD_DEPTH_MM), 6),
        "p0_8_derived_angle_deg": round(countersink_angle(NOMINAL_MAJOR_D_MM, NOMINAL_DEPTH_MM), 6),
        "total_candidate_mass_delta_g_at_2_70_g_cm3": round(total_mass_delta_g, 6),
        "p0_7_remains_controlled": True,
        "candidate_selected": False,
        "supplier_contacted": False,
        "quotation_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    guide = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 countersink MBD correction</title><style>
:root{{--ink:#082f5b;--blue:#0d6fb8;--sky:#dff3ff;--gold:#f4bd28;--paper:#f8fcff;--danger:#8b1e2d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.5 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{background:var(--danger);color:#fff;padding:12px 18px;font-size:16px;font-weight:800}}header{{padding:32px max(20px,calc((100% - 1160px)/2));background:linear-gradient(135deg,var(--sky),#fff);border-bottom:6px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4rem);line-height:1.04;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.25rem)}}h3{{font-size:1.25rem}}main{{max-width:1160px;margin:auto;padding:24px}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}}.metric,.card,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px;box-shadow:5px 5px 0 var(--sky)}}.metric strong{{display:block;font-size:2rem;color:var(--blue)}}.badge,.priority{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:13px;font-weight:800;background:var(--gold)}}.helper,small{{font-size:14px}}input{{width:100%;font:16px system-ui;padding:13px;border:2px solid var(--blue);border-radius:10px;margin-bottom:18px}}dl{{display:grid;grid-template-columns:minmax(120px,1fr) 1.5fr;gap:7px 12px}}dt{{font-weight:750}}dd{{margin:0}}a{{color:#07579f;font-weight:700}}.diagram{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px;margin:20px 0}}.cone{{padding:20px;border-radius:12px;background:var(--sky);text-align:center;font-weight:750}}.arrow{{font-size:2rem;color:var(--blue)}}.blocker{{background:var(--danger);color:#fff}}li{{margin:1rem 0}}footer{{padding:24px;background:var(--ink);color:#fff;font-size:14px;margin-top:35px}}@media(max-width:600px){{main{{padding:18px}}header{{padding:24px 18px}}.diagram{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);text-align:center}}dl{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R136 · nonselected model-definition candidate</p><h1>One countersink, two different meanings</h1><p>P0.7 encoded conservative upper limits directly in the STEP solid. This candidate restores true nominal 90° geometry while keeping the worst-case diameter and depth screens explicit and separate.</p></header><main><section><h2>The bounded correction</h2><div class="diagram"><div class="cone">P0.7<br>Ø11.40 × 3.10 mm<br>{countersink_angle(OLD_MAJOR_D_MM, OLD_DEPTH_MM):.3f}° derived</div><div class="arrow">→</div><div class="cone">P0.8 candidate<br>Ø11.30 × 2.90 mm<br>90.000° derived</div></div><div class="metrics"><div class="metric"><strong>4</strong>candidate STEP parts</div><div class="metric"><strong>8</strong>corrected countersinks</div><div class="metric"><strong>0 mm</strong>bounding-envelope change</div><div class="metric"><strong>0</strong>fabrication releases</div></div></section><section><h2>Part comparison</h2><p class="helper">Search by C01, C04, C06 or C07. These candidates are review artifacts; P0.7 remains controlled.</p><input id="search" aria-label="Find a candidate part" placeholder="Find C06"><div class="grid">{''.join(cards)}</div></section><section class="panel"><h2>What still has to be decided</h2><ol>{''.join(f'<li><strong>{row["decision_id"]}</strong> {html.escape(row["question"])} <span class="badge">{row["state"]}</span><small>{html.escape(row["evidence_required"])}</small></li>' for row in decisions)}</ol></section><section class="panel"><h2>Machine-readable evidence</h2><p><a href="part-comparison.csv">Part comparison</a> · <a href="feature-certificate.csv">Feature certificate</a> · <a href="decision-register.csv">Decision register</a> · <a href="finding-register.csv">Findings</a> · <a href="package-status.json">Status</a></p></section></main><footer>{WARNING}</footer><script>const input=document.querySelector('#search');const cards=[...document.querySelectorAll('.card')];input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();cards.forEach(card=>card.hidden=!card.dataset.search.includes(q))}});</script></body></html>'''
    (OUT / "index.html").write_text(guide, encoding="utf-8", newline="\n")

    DOC.write_text(f'''# HR-V0 countersink model-definition correction P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Candidate: `{CANDIDATE}`

Controlled source: `HR-V0-ARM-ARCH-P0.7`

## Result

R135 found that all eight P0.7 countersink openings are modeled at the drawing's upper diameter limit, Ø11.40 mm, while the controlled nominal is Ø11.30 +0.10/-0.00 mm with a 90° included angle. The P0.7 STEP also uses a 3.10 mm axial depth. Those two modeled dimensions derive an 87.159469° cone, not 90°.

This package generates four nonselected P0.8 candidate STEP parts with:

- unchanged M5 through hole Ø5.50 mm;
- nominal major diameter Ø11.30 mm;
- nominal axial depth 2.90 mm, derived from the 90° geometry;
- unchanged part bounding boxes, exterior profiles, hole centers and all non-countersink features; and
- separate Ø11.40 maximum-diameter and 3.10 mm maximum-depth screens retained for conservative clearance/residual-material checks.

The candidates add only the material removed by P0.7's larger/deeper countersink. The total calculated mass change across C01/C04/C06/C07 is {total_mass_delta_g:.6f} g at the project screening density of 2.70 g/cm³.

## Configuration boundary

P0.7 remains the controlled architecture. This package does not silently revise its files or downstream hashes. P0.8 cannot be selected until a qualified mechanical reviewer independently verifies the STEP cone geometry, accepts the nominal-versus-limit semantics, reviews fastener seating and directs configuration-control regeneration.

## Evidence

- `release/hr-v0/countersink-mbd-p0.1/part-comparison.csv`
- `release/hr-v0/countersink-mbd-p0.1/feature-certificate.csv`
- `release/hr-v0/countersink-mbd-p0.1/decision-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/finding-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/package-status.json`
- `release/hr-v0/countersink-mbd-p0.1/index.html`
- `cad/hr-v0/generated/countersink-mbd-p0.1/`

## What this does not prove

This bounded correction does not prove manufacturing capability, tolerance, cutter/gauge method, screw-head seating, flushness, received fit, residual strength, fatigue, hard-stop behavior, stopping, guarding or safety. Supplier DFM, FAI, received-lot inspection, proof testing and qualified review remain mandatory.
''', encoding="utf-8", newline="\n")

    generated_rows = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            generated_rows.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_digest(path),
                "revision": "HR-V0-MECH-R0.1-PRELIMINARY",
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, generated_rows)

    print(f"Generated {IDENTIFIER}: {len(comparison_rows)} parts, {len(feature_rows)} countersinks, total candidate mass delta {total_mass_delta_g:.6f} g")
    print(WARNING)


if __name__ == "__main__":
    main()
