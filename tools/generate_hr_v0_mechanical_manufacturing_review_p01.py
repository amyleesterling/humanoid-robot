#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 mechanical manufacturing-review package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/mechanical-manufacturing-review-p0.1"
IDENTIFIER = "HR-V0-MECH-MFG-REVIEW-P0.1"
ROUND = "R215"
DATE = "2026-08-11"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_record(path_text: str, role: str) -> dict[str, str]:
    path = ROOT / path_text
    return {
        "source_path": path_text,
        "sha256": digest(path),
        "role": role,
        "exists": "TRUE",
        "warning": WARNING,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    source_binding_path = ROOT / "release/hr-v0/mechanical-drawing-p0.1/source-binding.csv"
    binding_path = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv"
    interface_path = ROOT / "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/interface-schedule.csv"
    fastener_path = ROOT / "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/fastener-candidate-schedule.csv"
    controls_path = ROOT / "release/hr-v0/mechanical-drawing-p0.1/drawing-control-coverage.csv"
    fai_path = ROOT / "release/hr-v0/mechanical-drawing-p0.1/first-article-drawing-map.csv"
    dfm_path = ROOT / "release/hr-v0/mechanical-dfm-data-p0.1/dfm-question-register.csv"
    holds_path = ROOT / "release/hr-v0/mechanical-bom-binding-p0.2/open-holds.csv"

    source_binding = read_csv(source_binding_path)
    binding = {row["part_id"]: row for row in read_csv(binding_path)}
    controls = read_csv(controls_path)
    fai = read_csv(fai_path)
    interfaces = read_csv(interface_path)
    fasteners = read_csv(fastener_path)
    dfm = read_csv(dfm_path)
    holds = read_csv(holds_path)

    authority_rows = [
        {"activity": "internal qualified mechanical review", "permitted_by_this_package": "TRUE", "condition": "read-only review and controlled redlines only", "state": "AVAILABLE"},
        {"activity": "provider contact or file upload", "permitted_by_this_package": "FALSE", "condition": "separate written program authority required", "state": "PROHIBITED"},
        {"activity": "quotation or commercial commitment", "permitted_by_this_package": "FALSE", "condition": "MCP-H01 and explicit commercial authorization required", "state": "PROHIBITED"},
        {"activity": "procurement", "permitted_by_this_package": "FALSE", "condition": "released BOM and separate written procurement authority required", "state": "PROHIBITED"},
        {"activity": "fabrication", "permitted_by_this_package": "FALSE", "condition": "all applicable mechanical release holds and separate written authority required", "state": "PROHIBITED"},
        {"activity": "assembly or connection", "permitted_by_this_package": "FALSE", "condition": "received-part acceptance and released traveler required", "state": "PROHIBITED"},
        {"activity": "powered testing, motion, or energization", "permitted_by_this_package": "FALSE", "condition": "not within this package; applicable energization gates and separate authorization required", "state": "PROHIBITED"},
    ]
    for row in authority_rows:
        row["warning"] = WARNING
    write_csv("authority-boundary.csv", ["activity", "permitted_by_this_package", "condition", "state", "warning"], authority_rows)

    precedence_rows = [
        {"rank": 1, "artifact_or_rule": "separate configuration-specific written work authority", "controls": "whether any external or physical action may occur", "conflict_rule": "absence means stop; this package supplies no such authority"},
        {"rank": 2, "artifact_or_rule": "accepted qualified-review disposition tied to exact commit and hashes", "controls": "review acceptance, exceptions, and required revisions", "conflict_rule": "open or conditional disposition blocks downstream work"},
        {"rank": 3, "artifact_or_rule": "conventional drawing plus drawing-control register", "controls": "dimensions, tolerances, material candidate, finish, inspection, and notes", "conflict_rule": "must agree with STEP and DXF; any disagreement is a blocking nonconformance"},
        {"rank": 3, "artifact_or_rule": "exact hash-bound STEP", "controls": "nominal three-dimensional material boundary", "conflict_rule": "does not override drawing tolerances or notes; disagreement stops work"},
        {"rank": 3, "artifact_or_rule": "exact hash-bound finished DXF", "controls": "nominal two-dimensional finished profile and feature geometry", "conflict_rule": "does not override drawing tolerances or notes; disagreement stops work"},
        {"rank": 4, "artifact_or_rule": "interface and fastener schedules", "controls": "assembly use, candidate hardware, stack screens, and unresolved evidence", "conflict_rule": "no best-fit shift, substitution, slotting, filing, or forced alignment"},
        {"rank": 5, "artifact_or_rule": "provider defaults, portal previews, or automatically healed geometry", "controls": "nothing unless explicitly accepted into a new controlled revision", "conflict_rule": "never authoritative; report discrepancy and stop"},
    ]
    for row in precedence_rows:
        row["warning"] = WARNING
    write_csv("document-precedence.csv", ["rank", "artifact_or_rule", "controls", "conflict_rule", "warning"], precedence_rows)

    part_rows: list[dict[str, object]] = []
    for src in source_binding:
        part_id = src["part_id"]
        b = binding[part_id]
        control_count = sum(part_id in row["part_id_or_interface"].split(";") for row in controls)
        fai_count = sum(row["part_id"] == part_id for row in fai)
        part_rows.append({
            "part_id": part_id,
            "quantity": b["quantity_candidate"],
            "material_candidate": b["material_candidate"],
            "process_candidate": b["process_candidate"],
            "drawing_path": src["drawing_path"],
            "drawing_sha256": src["drawing_sha256"],
            "dxf_path": src["finished_dxf_path"],
            "dxf_sha256": src["finished_dxf_sha256"],
            "step_path": b["step_path"],
            "step_sha256": b["step_sha256"],
            "explicit_control_count": control_count,
            "fai_operation_count": fai_count,
            "qualified_review": "OPEN",
            "provider_dfm": "NOT SENT / NO RESPONSE",
            "material_mtr": "NOT RECEIVED",
            "fai": "UNEXECUTED",
            "fabrication_authorized": "FALSE",
            "warning": WARNING,
        })
    write_csv(
        "part-release-matrix.csv",
        ["part_id", "quantity", "material_candidate", "process_candidate", "drawing_path", "drawing_sha256", "dxf_path", "dxf_sha256", "step_path", "step_sha256", "explicit_control_count", "fai_operation_count", "qualified_review", "provider_dfm", "material_mtr", "fai", "fabrication_authorized", "warning"],
        part_rows,
    )

    interface_rows: list[dict[str, object]] = []
    for row in interfaces:
        interface_rows.append({
            "interface": row["interface"],
            "from": row["from"],
            "to": row["to"],
            "pattern": row["pattern"],
            "candidate_fasteners": row["fasteners"],
            "model_state": row["status"],
            "received_stack": "NOT RECEIVED",
            "torque_locking_reuse": "SELECTION REQUIRED",
            "fit_tool_access": "UNEXECUTED",
            "proof": "UNEXECUTED",
            "assembly_authorized": "FALSE",
            "warning": WARNING,
        })
    write_csv(
        "interface-fastener-stack.csv",
        ["interface", "from", "to", "pattern", "candidate_fasteners", "model_state", "received_stack", "torque_locking_reuse", "fit_tool_access", "proof", "assembly_authorized", "warning"],
        interface_rows,
    )

    fastener_rows: list[dict[str, object]] = []
    for row in fasteners:
        fastener_rows.append({
            **row,
            "commercial_availability": "SELECTION REQUIRED - confirm at authorized acquisition",
            "received_identity": "NOT RECEIVED",
            "application_release": "OPEN",
            "procurement_authorized": "FALSE",
            "warning": WARNING,
        })
    write_csv(
        "fastener-candidate-register.csv",
        list(fasteners[0].keys()) + ["commercial_availability", "received_identity", "application_release", "procurement_authorized", "warning"],
        fastener_rows,
    )

    source_freshness = [
        {"source_id": "MFG-SRC-001", "manufacturer": "80/20 Inc.", "item": "20-2040 with 20-7047 end-tap option", "primary_url": "https://8020.net/20-2040.html", "document_revision_or_page_state": "live product/configurator page; no formal revision exposed", "checked_date": DATE, "verification": "VERIFIED: page identifies 20 x 40 profile, 20-7047 two-hole M5 x 0.8 end tap, and 22.23 mm depth", "closure_effect": "source freshness only; receiving and service confirmation remain required"},
        {"source_id": "MFG-SRC-002", "manufacturer": "80/20 Inc.", "item": "13035", "primary_url": "https://8020.net/13035.html", "document_revision_or_page_state": "live product page; no formal revision exposed", "checked_date": DATE, "verification": "VERIFIED: page identifies M8 self-aligning roll-in T-nut with ball spring", "closure_effect": "source freshness only; fit, engagement, torque, pullout, slip and prying proof remain required"},
        {"source_id": "MFG-SRC-003", "manufacturer": "80/20 Inc.", "item": "17-8520", "primary_url": "https://8020.net/17-8520.html", "document_revision_or_page_state": "live product page; no formal revision exposed", "checked_date": DATE, "verification": "VERIFIED: page identifies M8 x 20 full-thread stainless SHCS and published dimensions", "closure_effect": "source freshness only; received identity and application proof remain required"},
        {"source_id": "MFG-SRC-004", "manufacturer": "80/20 Inc.", "item": "40-4040", "primary_url": "https://8020.net/40-4040.html", "document_revision_or_page_state": "live product page; no formal revision exposed", "checked_date": DATE, "verification": "VERIFIED: current official result identifies 40 x 40 four-open-slot profile", "closure_effect": "source freshness only; received section and joint proof remain required"},
        {"source_id": "MFG-SRC-005", "manufacturer": "MISUMI", "item": "SCB2.5-20", "primary_url": "https://us.misumi-ec.com/vona2/detail/110300239250/?HissuCode=SCB2.5-20", "document_revision_or_page_state": "live configurator not fetched; official 2019 U.S. catalog page 2378 found", "checked_date": DATE, "verification": "PARTIAL: official catalog family supports SCB M2.5 and A2-70; exact live order availability must be confirmed", "closure_effect": "SELECTION REQUIRED; no procurement authority"},
        {"source_id": "MFG-SRC-006", "manufacturer": "Accu", "item": "SHKL-M5-20-A2-R360", "primary_url": "https://accu-components.com/us/torx-countersunk-screws/643760-SHKL-M5-20-A2-R360", "document_revision_or_page_state": "official page was not fetchable in R215 verification", "checked_date": DATE, "verification": "UNVERIFIED CURRENT AVAILABILITY: retain previous exact-candidate evidence only", "closure_effect": "SELECTION REQUIRED; authorized acquisition must reverify identity, dimensions, finish and stock"},
        {"source_id": "MFG-SRC-007", "manufacturer": "Accu", "item": "HNN-M2.5-A2", "primary_url": "https://accu-components.com/", "document_revision_or_page_state": "exact current product page not reverified in R215", "checked_date": DATE, "verification": "UNVERIFIED CURRENT AVAILABILITY: retain previous exact-candidate evidence only", "closure_effect": "SELECTION REQUIRED; authorized acquisition must reverify identity, dimensions, temperature and prevailing-torque behavior"},
        {"source_id": "MFG-SRC-008", "manufacturer": "material provider", "item": "6061-T651 plate", "primary_url": "SELECTION REQUIRED", "document_revision_or_page_state": "purchase-order ASTM B209/B209M edition and stock source not released", "checked_date": DATE, "verification": "OPEN: exact source, edition, heat/lot certificate and finished thickness evidence absent", "closure_effect": "MCP-H03 remains open"},
    ]
    for row in source_freshness:
        row["warning"] = WARNING
    write_csv(
        "source-freshness-register.csv",
        ["source_id", "manufacturer", "item", "primary_url", "document_revision_or_page_state", "checked_date", "verification", "closure_effect", "warning"],
        source_freshness,
    )

    checklist_items = [
        ("MR-01", "configuration", "Confirm commit and package identifier; independently recompute every listed SHA-256."),
        ("MR-02", "authority", "Confirm the package grants review only and contains no provider, quote, purchase, fabrication, assembly, connection, motion, or energization authority."),
        ("MR-03", "drawing", "Review all five drawings for complete, legible dimensions, units, finish, material, tolerances, inspection methods, and non-scaling instruction."),
        ("MR-04", "GD&T", "Accept, revise, or reject ICF-01; define a released datum reference frame if required."),
        ("MR-05", "geometry", "Compare each STEP, DXF, and drawing as a co-controlled set; report every mismatch."),
        ("MR-06", "interfaces", "Review A00 through A07 and HS-J2-POS against the full P0.8 arm assembly and vendor interfaces."),
        ("MR-07", "fasteners", "Review candidate order codes, stack lengths, protrusion/engagement, tool access, head seating, locking, reuse, and anti-galling controls."),
        ("MR-08", "material", "Disposition alloy/temper, applicable material specification edition, certificate/MTR, stock thickness, grain/flatness, and substitution prohibition."),
        ("MR-09", "process", "Disposition one-stop 3-axis CNC route, workholding, datum transfer, countersinks, rail/step features, deburr, and no-coating requirement."),
        ("MR-10", "inspection", "Review all 26 controls, 30 FAI operations, instrument capability, calibration, uncertainty, raw-data retention, and segregation."),
        ("MR-11", "fit", "Define received mating-article dry-fit evidence without filing, slotting, bending, best-fit shift, or forced alignment."),
        ("MR-12", "loads", "Review static, stop, joint-slip, preload, prying, fatigue, and proof-load cases; identify missing allowables or calculations."),
        ("MR-13", "mass", "Define measured mass, center-of-mass, and inertia closure for every received moving item."),
        ("MR-14", "stop", "Review J2 striker/catch/bumper, contact patch, local stress, impact, life, backlash, compliance, and overtravel evidence plan."),
        ("MR-15", "integration", "Review complete-arm tool, cable, guard, service, deformation, and collision clearances."),
        ("MR-16", "manufacturing", "Review every DFM question and require provider response against exact hashes with all exceptions listed."),
        ("MR-17", "nonconformance", "Define deviation/NCR control, segregation, rework prohibition, concession authority, and supersession behavior."),
        ("MR-18", "disposition", "Record PASS, PASS WITH REQUIRED REVISION, or FAIL for each item; name reviewer, competence basis, date, exact commit, and signature evidence."),
    ]
    checklist_rows = [{
        "check_id": cid,
        "domain": domain,
        "review_question": question,
        "state": "NOT REVIEWED",
        "finding_reference": "SELECTION REQUIRED",
        "reviewer": "SELECTION REQUIRED",
        "evidence": "NOT EXECUTED",
        "release_effect": "BLOCKS FABRICATION RELEASE UNTIL ACCEPTED OR FORMALLY DISPOSITIONED",
        "warning": WARNING,
    } for cid, domain, question in checklist_items]
    write_csv("qualified-review-checklist.csv", list(checklist_rows[0].keys()), checklist_rows)

    decision_rows = [{
        "decision_id": f"DEC-{index:02d}",
        "scope": scope,
        "decision": "NOT REVIEWED",
        "required_revision_or_condition": "SELECTION REQUIRED",
        "reviewer_name": "SELECTION REQUIRED",
        "competence_basis": "SELECTION REQUIRED",
        "review_date": "SELECTION REQUIRED",
        "git_commit": "SELECTION REQUIRED",
        "signature_evidence": "SELECTION REQUIRED",
        "downstream_authority": "NONE",
        "warning": WARNING,
    } for index, scope in enumerate(["drawing/GD&T", "material/process", "interfaces/fasteners", "loads/proof", "FAI/inspection", "configuration"], start=1)]
    write_csv("qualified-review-decision-template.csv", list(decision_rows[0].keys()), decision_rows)

    provider_rows = []
    for row in dfm:
        provider_rows.append({
            "question_id": row["question_id"],
            "question": row["question"],
            "response": "NOT SENT / NO RESPONSE",
            "exception_or_substitution": "NONE RECORDED",
            "provider_name": "SELECTION REQUIRED",
            "responder": "SELECTION REQUIRED",
            "response_date": "SELECTION REQUIRED",
            "bound_file_hashes": "SELECTION REQUIRED",
            "internal_disposition": "NOT REVIEWED",
            "commercial_action_authorized": "FALSE",
            "warning": WARNING,
        })
    write_csv("provider-dfm-response-template.csv", list(provider_rows[0].keys()), provider_rows)

    hold_rows = []
    for row in holds:
        hold_rows.append({
            "hold_id": row["hold_id"],
            "subject": row["subject"],
            "evidence_required": row["evidence_required"],
            "repository_input_complete": "TRUE" if row["hold_id"] in {"MCP-H01", "MCP-H02", "MCP-H08", "MCP-H12"} else "PARTIAL",
            "external_or_physical_evidence": "ABSENT",
            "state": "OPEN",
            "work_authority_effect": row["work_authority_effect"],
            "warning": WARNING,
        })
    write_csv("open-holds.csv", list(hold_rows[0].keys()), hold_rows)

    inputs = [
        ("bom/hr-v0-mechanical-custom-part-binding-p0.2.csv", "current custom-part manufacturing identity"),
        ("release/hr-v0/mechanical-drawing-p0.1/source-binding.csv", "drawing/DXF/STEP binding"),
        ("release/hr-v0/mechanical-drawing-p0.1/drawing-control-coverage.csv", "26 drawing-explicit controls"),
        ("release/hr-v0/mechanical-drawing-p0.1/first-article-drawing-map.csv", "30 FAI operations"),
        ("release/hr-v0/mechanical-drawing-p0.1/inspection-coordinate-register.csv", "ICF-01 inspection registration"),
        ("release/hr-v0/mechanical-dfm-data-p0.1/dfm-question-register.csv", "provider DFM questions"),
        ("release/hr-v0/mechanical-bom-binding-p0.2/open-holds.csv", "current mechanical hold set"),
        ("cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/interface-schedule.csv", "current integrated arm interfaces"),
        ("cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/fastener-candidate-schedule.csv", "current fastener candidates"),
        ("cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/controlled-custom-part-integration.csv", "exact P0.8 assembly consumption"),
    ]
    source_rows = [source_record(path, role) for path, role in inputs]
    write_csv("source-hash-register.csv", ["source_path", "sha256", "role", "exists", "warning"], source_rows)

    status = {
        "schema": "project-button-mechanical-manufacturing-review-package-v1",
        "identifier": IDENTIFIER,
        "round": ROUND,
        "date": DATE,
        "configuration": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "manufacturing_identity": "HR-V0-MECH-BOM-BIND-P0.2",
        "purpose": "qualified mechanical and provider-DFM review input; no downstream work authority",
        "part_count": len(part_rows),
        "drawing_count": len(part_rows),
        "dxf_count": len(part_rows),
        "step_count": len(part_rows),
        "drawing_explicit_control_count": len(controls),
        "fai_operation_count": len(fai),
        "interface_count": len(interface_rows),
        "fastener_candidate_count": len(fastener_rows),
        "qualified_review_item_count": len(checklist_rows),
        "provider_dfm_question_count": len(provider_rows),
        "open_hold_count": len(hold_rows),
        "qualified_review_complete": False,
        "provider_contacted": False,
        "quotation_authorized": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "powered_test_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = "".join(
        f'<article class="card"><span>{html.escape(part["part_id"])}</span><h3>{part["explicit_control_count"]} controls · {part["fai_operation_count"]} FAI steps</h3><p>Drawing, DXF, and STEP are hash-bound. Review: open. FAI: unexecuted.</p><a href="../../../{html.escape(str(part["drawing_path"]))}">Open drawing</a></article>'
        for part in part_rows
    )
    hold_cards = "".join(
        f'<article class="hold"><strong>{html.escape(row["hold_id"])}</strong><h3>{html.escape(row["subject"])}</h3><p>{html.escape(row["evidence_required"])}</p></article>'
        for row in hold_rows
    )
    html_text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 Mechanical Manufacturing Review P0.1</title>
<style>
:root{{--sky:#dff3ff;--blue:#082f5b;--gold:#f4b942;--ink:#12243a;--paper:#f7fbff;--danger:#8b1e2d}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
.warning{{background:var(--danger);color:white;padding:14px 20px;text-align:center;font-weight:800;font-size:16px}}
header,main{{max-width:1180px;margin:auto;padding:28px}} h1{{font-size:clamp(32px,5vw,60px);line-height:1.05;margin:.2em 0}} h2{{font-size:clamp(25px,3vw,36px);color:var(--blue);margin-top:42px}} h3{{font-size:19px;line-height:1.3}}
.eyebrow,.badge{{font-size:14px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}} .badge{{display:inline-block;background:var(--gold);color:var(--blue);padding:7px 11px;border-radius:999px}}
.summary{{font-size:20px;max-width:850px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}} .card,.hold,.panel{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}
.card span,.hold strong{{font-size:14px;font-weight:900;color:var(--blue)}} a{{color:#075b9b;font-weight:750}} .hold{{border-color:var(--danger);box-shadow:6px 6px 0 #f5d9dd}} .hold h3{{margin:.4em 0}}
.downloads a{{display:inline-block;margin:8px 12px 8px 0;padding:10px 14px;border:2px solid var(--blue);border-radius:10px;background:white}} ul{{padding-left:24px}} li{{margin:.55em 0}}
@media(max-width:600px){{header,main{{padding:20px}}.warning{{font-size:14px;text-align:left}}.summary{{font-size:18px}}}}
</style></head><body>
<div class="warning">{WARNING}</div>
<header><div class="eyebrow">Project Button · R215 · qualified-review input</div><h1>Mechanical manufacturing review package</h1><p class="summary">One controlled front door for the five custom HR-V0 aluminum candidates. It binds the exact drawings, DXFs, STEP files, interfaces, fastener candidates, inspection plan, DFM questions, and open holds. It does not authorize a quote, purchase, cut, assembly, connection, motion, or energization.</p><span class="badge">5 parts · 26 controls · 30 FAI steps · 12 open holds</span></header>
<main><section class="panel"><h2>What a reviewer may do</h2><p>Independently recompute hashes, inspect the exact files, redline them, answer the checklist, and return a signed disposition tied to the exact Git commit. Every physical and commercial action remains prohibited.</p><div class="downloads"><a href="authority-boundary.csv">Authority boundary</a><a href="document-precedence.csv">Document precedence</a><a href="qualified-review-checklist.csv">Reviewer checklist</a><a href="qualified-review-decision-template.csv">Decision template</a></div></section>
<h2>Controlled part sets</h2><div class="grid">{cards}</div>
<h2>Manufacturing and interface evidence</h2><div class="downloads"><a href="part-release-matrix.csv">Part release matrix</a><a href="interface-fastener-stack.csv">Interface/fastener stack</a><a href="fastener-candidate-register.csv">Fastener candidates</a><a href="provider-dfm-response-template.csv">Provider DFM response</a><a href="source-freshness-register.csv">Source freshness</a><a href="source-hash-register.csv">Source hashes</a><a href="package-status.json">Machine status</a></div>
<h2>Open holds</h2><p>Repository-owned review inputs are now collected; external decisions, received articles, measurements, tests, and signatures remain absent.</p><div class="grid">{hold_cards}</div>
<h2>Conflict rule</h2><div class="panel"><p>The drawing/control register, exact STEP, and exact DXF are a co-controlled set. None silently overrides another. Any mismatch, portal healing, substituted material, default tolerance, best-fit shift, or automatic geometry change is a blocking nonconformance: stop and issue a new controlled revision.</p></div>
</main></body></html>"""
    (OUT / "index.html").write_text(html_text, encoding="utf-8")

    # Preserve the hand-authored CSV formatting while appending this package to
    # the three affected gate-evidence cells. The replacement is deliberately
    # idempotent and refuses to infer any status change.
    gate_path = ROOT / "requirements/hr-v0-energization-gates.csv"
    gate_text = gate_path.read_text(encoding="utf-8")
    gate_evidence = (
        "; docs/hr-v0-mechanical-manufacturing-review-p0.1.md"
        "; release/hr-v0/mechanical-manufacturing-review-p0.1/"
        "; requirements/hr-v0-gate-evidence-supplement-r215.csv"
        "; tools/check_hr_v0_mechanical_manufacturing_review_p01.py"
    )
    for gate_id, stage in (("EG-003", "E0"), ("EG-005", "E1"), ("EG-006", "E1")):
        updated: list[str] = []
        matched = False
        for line in gate_text.splitlines():
            if line.startswith(gate_id + ","):
                matched = True
                if "requirements/hr-v0-gate-evidence-supplement-r215.csv" not in line:
                    suffix = f",partial,{stage},"
                    if suffix not in line:
                        raise RuntimeError(f"{gate_id} no longer has the expected partial/{stage} state")
                    line = line.replace(suffix, gate_evidence + suffix, 1)
            updated.append(line)
        if not matched:
            raise RuntimeError(f"{gate_id} missing from energization-gate register")
        gate_text = "\n".join(updated) + "\n"
    gate_path.write_text(gate_text, encoding="utf-8", newline="")

    governance_source_path = ROOT / "requirements/governance-p0.3/source-register.csv"
    governance_sources = read_csv(governance_source_path)
    for row in governance_sources:
        if row["source_id"] == "gates":
            row["sha256"] = digest(gate_path)
    write_fields = list(governance_sources[0])
    with governance_source_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=write_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(governance_sources)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
