#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 Boston fabrication route P0.4 package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/boston-fabrication-route-p0.4"
IDENTIFIER = "HR-V0-BOSTON-FAB-ROUTE-P0.4"
ROUND = "R217"
DATE = "2026-08-11"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty register: {name}")
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    row["warning"] = WARNING
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    bindings = [
        ("CFG-FAB-01", "integrated arm", "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/architecture-summary.json"),
        ("CFG-FAB-02", "custom-part manufacturing identity", "HR-V0-MECH-BOM-BIND-P0.2", "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv"),
        ("CFG-FAB-03", "manufacturing-review front door", "HR-V0-MECH-MFG-REVIEW-P0.1", "release/hr-v0/mechanical-manufacturing-review-p0.1/part-release-matrix.csv"),
        ("CFG-FAB-04", "provider DFM questions", "HR-V0-MECH-MFG-REVIEW-P0.1", "release/hr-v0/mechanical-manufacturing-review-p0.1/provider-dfm-response-template.csv"),
        ("CFG-FAB-05", "fabrication inputs", "HR-V0-FAB-INPUT-P0.1", "release/hr-v0/fabrication-input-basis-p0.1/input-reconciliation.csv"),
    ]
    binding_rows = []
    for record_id, role, identifier, relative in bindings:
        path = ROOT / relative
        binding_rows.append(warned({
            "record_id": record_id,
            "role": role,
            "identifier": identifier,
            "path": relative,
            "sha256": digest(path),
            "state": "CURRENT CONTROLLED INPUT",
        }))
    write_csv("configuration-binding.csv", binding_rows)

    routes = [
        warned({
            "route_id": "BOS-K4D",
            "provider": "Kontrast4D",
            "route_class": "local commercial CNC candidate",
            "location": "Salem, Massachusetts",
            "published_capability": "3/4/5-axis CNC; 6061 listed; called-out CMM-verified features to +/-0.0005 in; FAI reports on request; STEP/IGES/SolidWorks/PDF",
            "project_fit": "Strongest published local commercial screen; all five part envelopes fit published machine envelopes",
            "blocking_unknowns": "Exact 6061-T651/9.525 mm heat lot; MTR; all 26 controls; 30-operation FAI; countersinks; C07 surface map; no-substitution acceptance",
            "disposition": "PRIMARY LOCAL CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED",
            "next_evidence": "Written response to the exact R215 DFM packet after separate contact authority",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
        warned({
            "route_id": "ONLINE-PROTOLABS",
            "provider": "Protolabs",
            "route_class": "online commercial CNC candidate",
            "location": "United States factory/network",
            "published_capability": "3-axis and indexed 5-axis CNC; 6061-T651 listed; technical drawings; FAI, dimensional/CMM reports and material certifications available",
            "project_fit": "Strongest published exact-material online screen; all five envelopes fit published aluminum capacity",
            "blocking_unknowns": "Factory/network allocation; 9.525 mm stock; all tight rail/coplanarity controls; custom retained surface map; full DFM exception handling",
            "disposition": "PRIMARY ONLINE CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED",
            "next_evidence": "Manual technical-drawing and quality-plan review after separate contact/upload authority",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
        warned({
            "route_id": "ONLINE-XOMETRY",
            "provider": "Xometry",
            "route_class": "online manufacturing-network candidate",
            "location": "United States network",
            "published_capability": "6061-T6x best-available default; custom material review; formal/CMM/FAI/build-and-hold inspection; material traceability selectable at quote",
            "project_fit": "Quality-plan mechanisms could support the five-part first-article route if exact material and controls are accepted",
            "blocking_unknowns": "6061-T651 is not the published default; exact supplier/stock; all 26 controls; custom one-part hold; surface-map format; exception and nonconformance controls",
            "disposition": "SECONDARY ONLINE CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED",
            "next_evidence": "Custom engineering review with exact T651, traceability and build-and-hold requirements after separate authority",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
        warned({
            "route_id": "BOS-ARTISANS",
            "provider": "Artisans Asylum",
            "route_class": "local self-fabrication/training candidate",
            "location": "96 Holton Street, Allston, Massachusetts",
            "published_capability": "Manual and CNC machining of aluminum; Bridgeport CNC mill; M3X CNC mill; tool testing/classes required",
            "project_fit": "Useful for training, process trials, fixtures and non-credit prototypes under qualified supervision",
            "blocking_unknowns": "Operator competence; machine condition; fixturing; exact achievable controls; calibration/CMM/FAI/MTR chain; liability and independent inspection route",
            "disposition": "TRAINING/PROTOTYPE ROUTE ONLY - NOT A QUALIFIED FIRST-ARTICLE PROVIDER",
            "next_evidence": "Facility/tool survey and named competent machinist plus independent metrology plan; no structural part credit before qualified acceptance",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
        warned({
            "route_id": "BOS-DIGITALFAB",
            "provider": "Boston Digital Fabrication",
            "route_class": "local commercial capability-screen candidate",
            "location": "96 Holton Street, Boston, Massachusetts",
            "published_capability": "3-axis CNC knee mill and lathe for small-to-medium quantity custom milled parts",
            "project_fit": "Local commercial route worth a capability-only screen",
            "blocking_unknowns": "6061-T651; machine envelope; numerical tolerances; CMM/FAI/calibration; MTR/traceability; all five drawing and operation acceptances",
            "disposition": "HOLD - PUBLISHED QUALITY EVIDENCE INCOMPLETE",
            "next_evidence": "Capability-only response to R215 questions after separate contact authority; do not upload geometry initially",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
        warned({
            "route_id": "BOS-BPL-EXCLUDED",
            "provider": "Boston Public Library",
            "route_class": "excluded structural-metal route",
            "location": "Boston, Massachusetts",
            "published_capability": "Official current pages list design software and MakerBot 3D printing; no suitable metal CNC mill is documented",
            "project_fit": "May support CAD learning or plastic mockups only",
            "blocking_unknowns": "No published structural-metal machining, material traceability, calibrated inspection or FAI capability",
            "disposition": "EXCLUDED FOR THE FIVE STRUCTURAL METAL PARTS",
            "next_evidence": "None unless direct current facility evidence establishes a controlled metal-machining route",
            "selected": "FALSE",
            "contacted": "FALSE",
            "files_uploaded": "FALSE",
            "quote_requested": "FALSE",
            "fabrication_authorized": "FALSE",
        }),
    ]
    write_csv("route-comparison.csv", routes)

    sources = [
        ("FAB-SRC-01", "Kontrast4D", "Official capability specification", "https://kontrast4d.com/", "K4D-CAP-001 Rev 1; updated 2026-05", "6061; 3/4/5-axis CNC; numerical tolerance bands; Mitutoyo Mistar 555 CMM; FAI reports on request"),
        ("FAB-SRC-02", "Protolabs", "CNC machining capability", "https://www.protolabs.com/services/cnc-machining/", "live official page; formal revision unstated", "6061-T651; 3-axis/indexed 5-axis; aluminum envelope and technical-drawing tolerance route"),
        ("FAB-SRC-03", "Protolabs", "CNC quality and inspection", "https://www.protolabs.com/services/cnc-machining/quality/", "live official page; formal revision unstated", "FAI, dimensional reports, CMM options, CoC and material certifications are available subject to site capability"),
        ("FAB-SRC-04", "Xometry", "CNC material categories", "https://community.xometry.com/kb/articles/637-materials-by-category", "live official knowledge-base page", "6061-T6x best available is default; custom material can be submitted for expert review"),
        ("FAB-SRC-05", "Xometry", "CNC inspection options", "https://community.xometry.com/kb/articles/673-cnc-machining-sheet-fabrication-inspection-options", "live official knowledge-base page", "Formal, CMM, FAIR, source, build-and-hold and custom inspections are described"),
        ("FAB-SRC-06", "Xometry", "Material traceability", "https://community.xometry.com/kb/articles/856-what-is-material-traceability", "live official knowledge-base page", "Traceability must be selected during quoting and includes heat-lot and ownership-chain records"),
        ("FAB-SRC-07", "Artisans Asylum", "Machine Shop", "https://www.artisansasylum.com/shops/machine", "live official page; formal revision unstated", "Aluminum manual/CNC machining, Bridgeport CNC mill, membership/day-pass access and tool testing"),
        ("FAB-SRC-08", "Artisans Asylum", "M3X CNC mill", "https://wiki.artisansasylum.com/wiki/M3X_CNC_Milling_Machine", "official wiki page last updated 2025-01-21", "Three-axis CNC mill; access through CNC class; project-specific capability not established"),
        ("FAB-SRC-09", "Boston Digital Fabrication", "CNC machining and turning", "https://bostondigitalfab.com/", "live official page; formal revision unstated", "Three-axis CNC knee mill and lathe for small-to-medium quantity custom milled parts"),
        ("FAB-SRC-10", "Boston Public Library", "Current technology resources", "https://www.bpl.org/faq/technology/", "live official page accessed 2026-08-11", "MakerBot 3D printing is listed; no suitable metal CNC route is documented"),
    ]
    source_rows = [warned({
        "source_id": source_id,
        "provider": provider,
        "title": title,
        "url": url,
        "document_revision_or_date": revision,
        "access_date": DATE,
        "verified_claim_boundary": claim,
        "project_acceptance_effect": "CAPABILITY SCREEN ONLY - NO PROVIDER OR APPLICATION ACCEPTANCE",
    }) for source_id, provider, title, url, revision, claim in sources]
    write_csv("source-register.csv", source_rows)

    inputs = [
        ("FAB-IN-001", "payload", "soft foam object; measured mass including uncertainty <=100 g; each principal dimension 40..70 mm", "CONTROLLED DRAFT - INDEPENDENT ACCEPTANCE REQUIRED", "Exact object/material/lot and retained calibrated measurement"),
        ("FAB-IN-002", "duty cycle", "one object per accepted cycle; exactly 100 guarded verification cycles", "PARTIAL", "Cycle time, moves/hour, dwell/rest, lifetime and representative thermal/fatigue spectrum"),
        ("FAB-IN-003", "speed and acceleration", "TCP <=0.15 m/s; automatic joints <=30 deg/s; setup joints <=10 deg/s hold-to-run", "PARTIAL", "Pose-dependent rates, acceleration/deceleration, jerk, emergency trajectory, measured stopping and uncertainty"),
        ("FAB-IN-004", "restraint and fall", "fixed bench-mounted architecture only", "OPEN", "Base/restraint geometry, anchors, push/pull/tip, dropped-arm and proof cases"),
        ("FAB-IN-005", "safety factors", "no accepted configuration-specific factors", "SELECTION REQUIRED", "Qualified yield/slip/pullout/prying/fatigue/fastener/proof/impact allocation"),
        ("FAB-IN-006", "C05 T-slot joint", "catalog compatibility only", "OPEN", "Reviewed calculation and physical slip/pullout/prying proof"),
        ("FAB-IN-007", "C06/C07 stop", "P0.8 geometry controlled; bumper/load/life and physical validation open", "OPEN", "Accepted bumper, force-stroke/energy, load/contact analysis and retained proof"),
        ("FAB-IN-008", "material traceability", "6061-T651 required; provider not selected", "OPEN", "Written stock/MTR/heat-lot/substitution acceptance and receiving evidence"),
        ("FAB-IN-009", "inspection data", "26 controls and 30 blank FAI operations controlled by R215", "OPEN", "Provider acceptance, calibrated methods, CMM/surface map, executed results and qualified disposition"),
        ("FAB-IN-010", "work authorization", "no provider contact, upload, quote or fabrication authority", "NOT AUTHORIZED", "Separate signed capability-only inquiry and later first-article authorization"),
    ]
    input_rows = [warned({
        "input_id": input_id,
        "topic": topic,
        "current_controlled_statement": statement,
        "state": state,
        "remaining_evidence": remaining,
        "release_effect": "BLOCKS FABRICATION RELEASE UNTIL ACCEPTED OR FORMALLY DISPOSITIONED",
    }) for input_id, topic, statement, state, remaining in inputs]
    write_csv("input-reconciliation.csv", input_rows)

    inquiry_rows = [
        ("CI-01", "configuration", "Bind any response to the exact five R215 drawing/DXF/STEP identities and SHA-256 values."),
        ("CI-02", "material", "Confirm 6061-T651, nominal 9.525 mm stock, one heat lot, applicable specification and MTR; list no silent substitutions."),
        ("CI-03", "process", "Confirm a one-stop CNC route and list every setup, datum transfer, deburr and subcontracted operation."),
        ("CI-04", "drawing", "Accept or explicitly reject each of the 26 controlled drawing requirements without portal-default override."),
        ("CI-05", "countersink", "Confirm the four-part 11.30 +0.10/-0.00 mm, 90-degree countersink and received-head gauge route."),
        ("CI-06", "interfaces", "Confirm C04 asymmetric H104, C05 datum chain, C06 +/-0.025 mm rails and C07 step/coplanarity controls."),
        ("CI-07", "inspection", "Confirm all 30 FAI operations, instruments, calibration identities, CMM results and C07 surface map."),
        ("CI-08", "segregation", "Hold one first article of each geometry segregated before any additional work; define nonconformance control."),
        ("CI-09", "authority", "Acknowledge that capability feedback is not permission to quote, order, fabricate or continue after first article."),
    ]
    inquiry_register = [warned({
        "question_id": qid,
        "domain": domain,
        "question": question,
        "response": "NOT SENT / NO RESPONSE",
        "provider": "SELECTION REQUIRED",
        "bound_hashes": "SELECTION REQUIRED",
        "internal_disposition": "NOT REVIEWED",
        "external_action_authorized": "FALSE",
    }) for qid, domain, question in inquiry_rows]
    write_csv("capability-inquiry-register.csv", inquiry_register)

    authority_rows = [
        ("internal route research and qualified review", "TRUE", "Read-only review and controlled redlines", "AVAILABLE"),
        ("provider contact", "FALSE", "Separate named and signed capability-inquiry authority", "PROHIBITED"),
        ("file upload", "FALSE", "Separate scope-limited authority after qualified configuration review", "PROHIBITED"),
        ("quote request or commercial commitment", "FALSE", "Separate commercial authority", "PROHIBITED"),
        ("first-article or production fabrication", "FALSE", "Accepted qualified review, provider response and separate written fabrication authority", "PROHIBITED"),
        ("assembly, connection, powered testing, motion or energization", "FALSE", "Outside this package and blocked by applicable gates", "PROHIBITED"),
    ]
    write_csv("authority-boundary.csv", [warned({
        "activity": activity,
        "permitted_by_this_package": permitted,
        "condition": condition,
        "state": state,
    }) for activity, permitted, condition, state in authority_rows])

    authorization = [warned({
        "authorization_id": "FAB-CI-AUTH-001",
        "scope": "capability-only inquiry; initial contact contains no geometry unless separately authorized",
        "provider": "SELECTION REQUIRED",
        "permitted_files": "NONE",
        "named_requestor": "SELECTION REQUIRED",
        "named_configuration_reviewer": "SELECTION REQUIRED",
        "named_program_authority": "SELECTION REQUIRED",
        "commit": "SELECTION REQUIRED",
        "start_time": "SELECTION REQUIRED",
        "expiry_time": "SELECTION REQUIRED",
        "revocation_method": "SELECTION REQUIRED",
        "signature_evidence": "SELECTION REQUIRED",
        "state": "NOT AUTHORIZED",
    })]
    write_csv("capability-inquiry-authorization-template.csv", authorization)

    status = {
        "schema": "project-button-boston-fabrication-route-v2",
        "identifier": IDENTIFIER,
        "round": ROUND,
        "date": DATE,
        "current_configuration": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "manufacturing_identity": "HR-V0-MECH-BOM-BIND-P0.2",
        "manufacturing_review": "HR-V0-MECH-MFG-REVIEW-P0.1",
        "fabrication_input_basis": "HR-V0-FAB-INPUT-P0.1",
        "part_count": 5,
        "configuration_bindings": len(binding_rows),
        "route_records": len(routes),
        "source_records": len(source_rows),
        "input_records": len(input_rows),
        "inquiry_questions": len(inquiry_register),
        "qualified_provider_selected": False,
        "supplier_contacted": False,
        "files_uploaded": False,
        "quote_requested": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "powered_test_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    cards = "".join(
        f'''<article class="card" data-class="{html.escape(str(row['route_class']))}">
        <span class="tag">{html.escape(str(row['route_class']))}</span>
        <h3>{html.escape(str(row['provider']))}</h3><p>{html.escape(str(row['location']))}</p>
        <p><strong>Published:</strong> {html.escape(str(row['published_capability']))}</p>
        <p><strong>Project boundary:</strong> {html.escape(str(row['blocking_unknowns']))}</p>
        <p class="state">{html.escape(str(row['disposition']))}</p></article>'''
        for row in routes
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 Boston fabrication route P0.4</title><style>
:root{{--ink:#08264a;--blue:#0b609e;--sky:#dff3ff;--gold:#f5bd18;--paper:#f7fbff;--line:#83bde3;--hold:#fff1b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;padding:30px max(20px,5vw);border-bottom:7px solid var(--gold)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(34px,5vw,60px);line-height:1.05;max-width:20ch}}h2{{font-size:clamp(26px,3vw,38px)}}h3{{font-size:22px}}.warn{{background:var(--hold);color:#3b2a00;border:3px solid var(--gold);padding:16px;font-weight:850}}.controls{{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}}button{{font:inherit;font-size:16px;padding:10px 14px;border:2px solid var(--blue);border-radius:999px;background:white;color:var(--ink);font-weight:750;cursor:pointer}}button[aria-pressed="true"]{{background:var(--gold);border-color:#7b5800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;overflow-wrap:anywhere}}.tag{{display:inline-block;background:var(--sky);padding:5px 9px;border-radius:999px;font-size:14px;font-weight:800}}.state{{font-weight:850;color:#7a4300}}.metric{{font-size:32px;font-weight:900}}a{{color:#07599b;font-weight:750}}.small{{font-size:14px}}@media(max-width:520px){{.grid{{grid-template-columns:1fr}}button{{width:100%}}}}</style></head><body><header><div class="warn">{WARNING}</div><p>{IDENTIFIER} - {ROUND}</p><h1>A real route to five custom metal parts.</h1><p>The current P0.8/R215 files are bound. Providers are screened, not selected, contacted, or authorized.</p></header><main><section class="grid"><article class="card"><div class="metric">5</div><p>Exact controlled part identities</p></article><article class="card"><div class="metric">6</div><p>Fabrication routes screened</p></article><article class="card"><div class="metric">26 / 30</div><p>Drawing controls / blank FAI operations</p></article><article class="card"><div class="metric">0</div><p>Provider actions authorized</p></article></section><section><h2>Route comparison</h2><div class="controls"><button data-filter="all" aria-pressed="true">All</button><button data-filter="local" aria-pressed="false">Boston-area</button><button data-filter="online" aria-pressed="false">Online</button><button data-filter="excluded" aria-pressed="false">Excluded</button></div><div id="cards" class="grid">{cards}</div></section><section><h2>What the library can do</h2><div class="card"><p>Boston Public Library's current official pages document CAD/design support and MakerBot printing, not controlled structural-metal CNC machining. Use it for learning or plastic mockups, not these five aluminum parts.</p></div></section><section><h2>Controlled next step</h2><ol><li>Qualified mechanical review dispositions the current drawings, loads, interfaces and R215 questions.</li><li>A separately signed capability-only inquiry selects one local and one online candidate.</li><li>No geometry is uploaded until the exact file scope and hashes are authorized.</li><li>One first article per geometry remains segregated until material, FAI, fit and qualified acceptance close.</li></ol><p class="small"><a href="route-comparison.csv">Routes</a> - <a href="source-register.csv">Sources</a> - <a href="configuration-binding.csv">Configuration binding</a> - <a href="input-reconciliation.csv">Inputs</a> - <a href="capability-inquiry-register.csv">Inquiry questions</a> - <a href="capability-inquiry-authorization-template.csv">Authorization template</a></p></section><div class="warn">Capability screening does not authorize contact, upload, quotation, procurement, fabrication, assembly, connection, powered testing, motion, or energization.</div></main><script>
const buttons=[...document.querySelectorAll('button[data-filter]')],cards=[...document.querySelectorAll('.card[data-class]')];function show(filter){{cards.forEach(card=>{{const c=card.dataset.class.toLowerCase();card.hidden=filter!=='all'&&!c.includes(filter)}});buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===filter)))}}buttons.forEach(button=>button.addEventListener('click',()=>show(button.dataset.filter)));</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    print(f"{IDENTIFIER}: {len(routes)} routes / {len(source_rows)} official sources / {len(input_rows)} controlled inputs")
    print("0 providers selected, contacted, quoted, uploaded, or authorized for fabrication")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
