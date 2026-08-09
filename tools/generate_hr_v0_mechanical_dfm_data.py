#!/usr/bin/env python3
"""Generate the review-only HR-V0 P0.7 mechanical DFM/FAI dataset."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1"
ARM = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7"
ROUTE = ROOT / "release" / "hr-v0" / "boston-fabrication-route-p0.2"
DOC = ROOT / "docs" / "hr-v0-mechanical-dfm-data-p0.1.md"
IDENTIFIER = "HR-V0-MECH-DFM-DATA-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


PARTS = [
    {"part_id": "MV0-C01", "name": "Joint-to-20-2040 adapter", "envelope_mm": "48.000 x 40.000 x 9.525", "critical_features": "M2.5 joint pattern; M5 end-tap pattern; 11.30 +0.10/-0.00 mm countersinks; residual thickness", "process_candidate": "One-stop 3-axis CNC mill; no portal-default substitutions"},
    {"part_id": "MV0-C04", "name": "H104-to-20-2040 adapter", "envelope_mm": "48.000 x 40.000 x 9.525", "critical_features": "Asymmetric H104 pattern; M5 end-tap pattern; countersinks; received H104 dry fit", "process_candidate": "One-stop 3-axis CNC mill; no slotting or best-fit pattern shift"},
    {"part_id": "MV0-C05", "name": "S102-to-40-4040 support", "envelope_mm": "48.000 x 80.000 x 9.525", "critical_features": "S102 pattern relative to column holes; single-setup or documented datum transfer; received stack fit", "process_candidate": "One-stop 3-axis CNC mill; retained datum-transfer inspection"},
    {"part_id": "MV0-C06", "name": "J2 positive moving striker", "envelope_mm": "82.000 x 57.380699 x 9.525", "critical_features": "Twin rail datums +/-0.025 mm from joint-hole datum; shared joint/end-tap interfaces", "process_candidate": "One-stop 3-axis CNC mill; retained CMM results for both rails"},
    {"part_id": "MV0-C07", "name": "J2 positive fixed catch", "envelope_mm": "84.000 x 42.000 x 9.525", "critical_features": "1.000 +/-0.05 mm face step; two rails coplanar <=0.03 mm; shared interfaces", "process_candidate": "One-stop 3-axis CNC mill; retained surface map"},
]


QUESTIONS = [
    "Bind every response to exact STEP, DXF, drawing, revision, units and SHA-256 values without silent geometry or datum changes.",
    "Confirm 6061-T651, nominal 9.525 mm stock, 9.00..10.00 mm finished thickness, one heat lot and an MTR; list any substitute separately.",
    "State whether every drawing control can be held instead of portal defaults, including feature locations, flatness, parallelism and edge break.",
    "Define the first-article report, instruments, calibration identity, pin-gauge results, five-point thickness map and coordinate results.",
    "For C01/C04/C06/C07, accept 11.30 +0.10/-0.00 mm 90-degree countersinks, >=5.80 mm residual and the received-head functional gauge.",
    "For C04, control all four asymmetric H104 coordinates independently with no slotting or best-fit shift.",
    "For C05, state the setup or datum-transfer method preserving the S102-to-column relative location.",
    "For C06, state the workholding, datum-transfer and CMM method for both +/-0.025 mm rail datums.",
    "For C07, demonstrate the 1.000 +/-0.05 mm step and <=0.03 mm rail coplanarity with a retained surface map.",
    "List every DFM exception, automatic radius/edge addition, substitution, tolerance relaxation, finish change and subcontracted operation.",
    "Keep each distinct first article segregated from further work pending written acceptance with material and inspection traceability.",
    "Acknowledge that capability or DFM feedback is not authorization to quote, order or fabricate.",
]


HOLDS = [
    ("MDFM-H01", "Qualified mechanical review", "Exact P0.7 parts, datums, tolerance scheme, load paths and inspection methods need signed disposition."),
    ("MDFM-H02", "Architecture freeze", "P0.7 remains controlled; P1.1/X430 exists but is nonselected and incomplete mass/duty evidence remains open."),
    ("MDFM-H03", "Material and MTR", "6061-T651 identity, heat lot, stock condition and substitution policy need supplier acceptance and receiving evidence."),
    ("MDFM-H04", "Received interface hardware", "H104, S102, 20-2040 and 40-4040 identities and metrology are not closed."),
    ("MDFM-H05", "T-slot joint capacity", "C05 column slip, pullout, prying, preload and proof basis remain open."),
    ("MDFM-H06", "Countersink and fastener stack", "Received head fit, residual thickness, engagement, torque, locking, access and proof remain open."),
    ("MDFM-H07", "J2 stop bumper", "Material, geometry, retention, force-stroke, temperature and life remain selection required."),
    ("MDFM-H08", "J2 stop load and contact", "Single-rail load, tolerance, deformation, rebound, overtravel and physical proof remain open."),
    ("MDFM-H09", "Cable, connector and guard envelope", "Complete swept geometry, strain relief, local guard and pinch controls remain open."),
    ("MDFM-H10", "Mass, COM and inertia", "Complete received assembly values remain unmeasured; P1.1 comparison is not a closed upper bound."),
    ("MDFM-H11", "Continuous actuator duty", "Configuration-specific torque, current and thermal limits are not demonstrated."),
    ("MDFM-H12", "All physical acceptance", "FAI, dry fit, contact, stopping, proof, fatigue and impact evidence are unexecuted."),
    ("MDFM-H13", "Provider acceptance", "No provider has reviewed or accepted the files, tolerances, material, inspection or workholding."),
    ("MDFM-H14", "Commercial authority", "No contact, upload, quotation, purchase, first article or fabrication authority exists."),
    ("MDFM-H15", "Safety and energization", "No functional-safety validation or energization authority exists."),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    geometry = read_csv(ROUTE / "geometry-file-register.csv")
    geometry_out: list[dict[str, object]] = []
    for row in geometry:
        source = ROOT / row["repository_path"]
        geometry_out.append({
            "part_id": row["part_id"], "artifact_role": row["artifact_role"], "repository_path": row["repository_path"],
            "bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "review_state": "INTERNAL QUALIFIED-REVIEW INPUT ONLY", "upload_authorized": "FALSE", "warning": WARNING,
        })
    write_csv(OUT / "geometry-file-register.csv", list(geometry_out[0]), geometry_out)

    part_rows = []
    for part in PARTS:
        part_rows.append({**part, "material_candidate": "6061-T651 aluminum; 9.525 mm nominal; 9.00..10.00 mm finished", "quantity_first_article": 1,
                          "release_state": "CANDIDATE; QUALIFIED REVIEW REQUIRED", "fabrication_authorized": "FALSE", "warning": WARNING})
    write_csv(OUT / "part-register.csv", list(part_rows[0]), part_rows)

    controls: list[dict[str, object]] = []
    for source_name in ("adapter-drawing-controls.csv", "new-interface-drawing-controls.csv", "j2-positive-stop-controls.csv"):
        for row_number, row in enumerate(read_csv(ARM / source_name), 2):
            controls.append({"source_table": source_name, "source_row": row_number, **row, "evidence_state": "UNEXECUTED", "release_state": "REVIEW INPUT ONLY", "warning": WARNING})
    control_fields: list[str] = []
    for row in controls:
        for key in row:
            if key not in control_fields:
                control_fields.append(key)
    write_csv(OUT / "inspection-control-register.csv", control_fields, controls)

    fai_rows: list[dict[str, object]] = []
    operations = [
        ("material", "Verify alloy/temper/heat-lot identity against MTR", "MTR plus receiving identity"),
        ("visual", "Verify bare finish, edge break and burr-free condition", "Calibrated visual/edge inspection"),
        ("envelope", "Record width, height and five-point thickness map", "Caliper/micrometer or CMM raw data"),
        ("features", "Inspect all holes, countersinks, profiles and part-specific critical datums", "Pin gauges plus CMM/optical raw report"),
        ("dry_fit", "Dry-fit only against received mating articles without forced alignment", "Photos, fastener-loose record and deviations"),
        ("disposition", "Qualified reviewer dispositions every result and deviation before further work", "Signed disposition; segregation state"),
    ]
    for part in PARTS:
        for index, (operation, method, evidence) in enumerate(operations, 1):
            fai_rows.append({"fai_id": f"FAI-{part['part_id'][-3:]}-{index:02d}", "part_id": part["part_id"], "sequence": index,
                             "operation": operation, "method": method, "required_evidence": evidence, "execution_state": "UNEXECUTED",
                             "acceptance_state": "NOT REVIEWED", "next_work_authorized": "FALSE", "warning": WARNING})
    write_csv(OUT / "first-article-plan.csv", list(fai_rows[0]), fai_rows)

    question_rows = [{"question_id": f"DFM-Q{index:02d}", "question": question, "sent_state": "NOT SENT",
                      "response_state": "NO RESPONSE", "commercial_action_authorized": "FALSE", "warning": WARNING}
                     for index, question in enumerate(QUESTIONS, 1)]
    write_csv(OUT / "dfm-question-register.csv", list(question_rows[0]), question_rows)
    hold_rows = [{"hold_id": hold_id, "hold": hold, "closure_evidence": evidence, "status": "OPEN", "warning": WARNING}
                 for hold_id, hold, evidence in HOLDS]
    write_csv(OUT / "hold-register.csv", list(hold_rows[0]), hold_rows)

    status = {
        "identifier": IDENTIFIER, "date": "2026-08-09", "round": "R134", "controlled_architecture": "HR-V0-ARM-ARCH-P0.7",
        "comparison_available": "HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE", "comparison_selected": False,
        "part_count": len(PARTS), "geometry_file_count": len(geometry_out), "inspection_control_count": len(controls),
        "first_article_operation_count": len(fai_rows), "dfm_question_count": len(question_rows), "open_hold_count": len(hold_rows),
        "provider_contacted": False, "supplier_selected": False, "upload_authorized": False, "quotation_authorized": False,
        "purchase_authorized": False, "first_article_authorized": False, "fabrication_authorized": False,
        "assembly_authorized": False, "motion_authorized": False, "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = "".join(
        f'<article class="card" data-search="{html.escape((p["part_id"] + " " + p["name"] + " " + p["critical_features"]).lower())}">'
        f'<p class="badge">{p["part_id"]}</p><h3>{html.escape(p["name"])}</h3><p><strong>Envelope:</strong> {p["envelope_mm"]} mm</p>'
        f'<p><strong>Critical:</strong> {html.escape(p["critical_features"])}</p><p><strong>Candidate process:</strong> {html.escape(p["process_candidate"])}</p>'
        f'<p><a href="../../../{next(row["repository_path"] for row in geometry_out if row["part_id"] == p["part_id"] and row["artifact_role"] == "readable control drawing")}">Open readable drawing</a></p></article>'
        for p in PARTS
    )
    holds_html = "".join(f'<li><strong>{hold_id}: {html.escape(hold)}</strong><span>{html.escape(evidence)}</span></li>' for hold_id, hold, evidence in HOLDS)
    questions_html = "".join(f'<li><span class="badge">DFM-Q{i:02d}</span>{html.escape(q)}</li>' for i, q in enumerate(QUESTIONS, 1))
    guide = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 mechanical DFM data P0.1</title><style>
:root{{--ink:#082f5b;--blue:#0d6fb8;--sky:#dff3ff;--gold:#f4bd28;--paper:#f8fcff;--danger:#8b1e2d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header{{background:linear-gradient(135deg,var(--sky),#fff);border-bottom:6px solid var(--gold);padding:32px max(24px,calc((100% - 1180px)/2))}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:.3rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.3rem)}}h3{{font-size:1.25rem}}main{{max-width:1180px;margin:auto;padding:24px}}.warning{{background:var(--danger);color:#fff;padding:12px 16px;font-weight:800;font-size:16px}}.meta,.helper{{font-size:14px}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}}.metric,.card,.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px;box-shadow:5px 5px 0 var(--sky)}}.metric strong{{display:block;font-size:2rem;color:var(--blue)}}.badge{{display:inline-block;background:var(--gold);padding:4px 9px;border-radius:999px;font-size:13px;font-weight:800}}input{{width:100%;font:16px system-ui;padding:13px;border:2px solid var(--blue);border-radius:10px;margin:0 0 16px}}a{{color:#07579f;font-weight:700}}ul{{padding-left:1.4rem}}li{{margin:.8rem 0}}li span:not(.badge){{display:block;font-size:14px}}.boundary{{border-left:8px solid var(--gold)}}footer{{margin-top:36px;padding:24px;background:var(--ink);color:#fff;font-size:14px}}@media(max-width:600px){{header{{padding:24px 18px}}main{{padding:18px}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p class="meta">{IDENTIFIER} · R134 · controlled P0.7 architecture</p><h1>Five parts, one inspectable review dataset.</h1><p>This internal guide binds the current STEP, DXF and readable drawings to material, feature-control, first-article and DFM questions. It is not a supplier payload and cannot authorize a quote or machining.</p></header><main>
<section><h2>What is controlled</h2><div class="metrics"><div class="metric"><strong>5</strong>custom parts</div><div class="metric"><strong>15</strong>hashed geometry files</div><div class="metric"><strong>{len(controls)}</strong>source controls</div><div class="metric"><strong>0</strong>authorized external actions</div></div></section>
<section><h2>Find a part</h2><p class="helper">Search by part ID, name or critical feature.</p><input id="search" aria-label="Find a mechanical part" placeholder="Try C06, countersink, H104 or rail"><div class="grid" id="cards">{cards}</div></section>
<section class="panel"><h2>Unsent DFM questions</h2><ol>{questions_html}</ol></section>
<section class="panel"><h2>Open holds</h2><ul>{holds_html}</ul></section>
<section class="panel boundary"><h2>Release boundary</h2><p>P1.1/X430 comparison evidence now exists, but it is nonselected and incomplete. P0.7 remains controlled. No provider contact, upload, quotation, purchase, first article, fabrication, assembly, motion or energization is authorized.</p><p><a href="part-register.csv">Part register</a> · <a href="geometry-file-register.csv">Geometry identities</a> · <a href="inspection-control-register.csv">Inspection controls</a> · <a href="first-article-plan.csv">FAI plan</a> · <a href="dfm-question-register.csv">DFM questions</a> · <a href="hold-register.csv">Holds</a></p></section></main><footer>{WARNING}</footer>
<script>const input=document.querySelector('#search');const cards=[...document.querySelectorAll('.card')];input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();cards.forEach(card=>card.hidden=!card.dataset.search.includes(q))}});</script></body></html>'''
    (OUT / "index.html").write_text(guide, encoding="utf-8")

    DOC.write_text(f'''# HR-V0 mechanical DFM data P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Round: R134

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Outcome

The current five custom aluminum candidates now have one deterministic internal qualified-review dataset: five exact part records, fifteen SHA-256-bound STEP/DXF/SVG identities, {len(controls)} source inspection controls, thirty unexecuted first-article operations, twelve unsent DFM questions and fifteen open holds.

This corrects the stale R91 statement that an exact-coordinate X430 comparison still had to be produced. P0.8 through P1.1 comparison evidence now exists. P1.1/X430 remains nonselected because moving mass/COM/inertia, continuous duty, tolerances, stops, interfaces and physical evidence are incomplete. P0.7 remains the controlled architecture.

## Manufacturing boundary

- Candidate material is 6061-T651 aluminum, 9.525 mm nominal and 9.00..10.00 mm finished.
- One high-requirement 3-axis CNC route remains the screened process for C01/C04/C05/C06/C07.
- The earlier 4.75 mm SendCutSend route remains rejected. SendCutSend may only be reconsidered as a separately controlled blank source; it is not a finished-part route.
- No provider has accepted a tolerance, material, inspection plan, workholding method or file.
- Every FAI operation is `UNEXECUTED`; every hold is `OPEN`; every external-action flag is false.

## Controlled artifacts

- [Interactive review guide](../release/hr-v0/mechanical-dfm-data-p0.1/index.html)
- `release/hr-v0/mechanical-dfm-data-p0.1/part-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/geometry-file-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/inspection-control-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/first-article-plan.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/dfm-question-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/hold-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/package-status.json`

## Permitted next action

Qualified mechanical reviewers may inspect and redline the exact controlled files and registers. Provider contact, file upload, quotation, purchase, first-article machining, fabrication, assembly, motion and energization remain prohibited until separately authorized after the applicable holds close.

Automated consistency proves file identity and internal completeness only. It does not prove machinability, strength, fit, stopping behavior, safety or readiness for fabrication or energization.
''', encoding="utf-8")


if __name__ == "__main__":
    main()
