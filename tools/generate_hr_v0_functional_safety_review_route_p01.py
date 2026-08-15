#!/usr/bin/env python3
"""Generate the provider-neutral HR-V0 functional-safety review route."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/functional-safety-review-route-p0.1"
IDENTIFIER = "HR-V0-FS-REVIEW-ROUTE-P0.1"
ROUND = "R219"
DATE = "2026-08-11"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    row["warning"] = WARNING
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    bound = [
        ("FSR-CFG-01", "system requirements", "HR-30-SYS-R0.2", "requirements/requirements.csv"),
        ("FSR-CFG-02", "safety requirements candidate", "HR-V0-SRS-P0.2", "docs/hr-v0-safety-requirements-p0.2.md"),
        ("FSR-CFG-03", "qualified allocation inputs", "HR-V0-SRS-P0.2", "release/hr-v0/safety-requirements-p0.2/qualified-allocation-inputs.csv"),
        ("FSR-CFG-04", "common-cause inputs", "HR-V0-SRS-P0.2", "release/hr-v0/safety-requirements-p0.2/common-cause-review-register.csv"),
        ("FSR-CFG-05", "validation inputs", "HR-V0-SRS-P0.2", "release/hr-v0/safety-requirements-p0.2/validation-matrix.csv"),
        ("FSR-CFG-06", "current electrical core", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/project-button-v3-p1.15-carrier-candidate.kicad_pro"),
        ("FSR-CFG-07", "observation presentation view", "V3-P1.17-OBSERVATION-P0.5-CANDIDATE", "electrical/kicad/project-button-v3-p1.17-observation-p05-candidate/project-button-v3-p1.17-observation-p05-candidate.kicad_pro"),
        ("FSR-CFG-08", "controlled gate state", "HR-V0-GOV-P0.3", "requirements/hr-v0-energization-gates.csv"),
    ]
    write_csv("configuration-binding.csv", [warned({
        "record_id": rid, "role": role, "identifier": ident, "path": rel,
        "sha256": sha(ROOT / rel), "state": "CURRENT REVIEW INPUT",
    }) for rid, role, ident, rel in bound])

    providers = [
        ("FSR-TUVSUD", "TÜV SÜD America", "Wakefield, Massachusetts", "ISO 12100 risk assessment; SRS; PLr/SIL determination; achieved PL/SIL evaluation; complete safety-function validation", "LOCAL MA OFFICE; PROJECT TEAM AVAILABILITY UNVERIFIED", "Design assistance and validation roles must be identified and separated in writing", "PRIMARY LOCAL CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED"),
        ("FSR-TUVR", "TÜV Rheinland of North America", "United States; exact project location unverified", "Machine risk assessment; PL/SIL calculation; individual-function and system validation; software assessment", "NATIONAL ROUTE; BOSTON SITE COVERAGE UNVERIFIED", "Named assessor and applicable accreditation/independence scope required", "PRIMARY INDEPENDENT NATIONAL CAPABILITY-INQUIRY CANDIDATE - NOT SELECTED"),
        ("FSR-PILZ", "Pilz Automation Safety L.P.", "Canton, Michigan / US service route", "Machinery risk assessment, design, implementation and three validation levels including fault simulation", "US ROUTE; BOSTON SITE COVERAGE UNVERIFIED", "Project uses a Pilz relay candidate; component-supplier/design/validation conflicts require written disposition", "SECONDARY FULL-LIFECYCLE CANDIDATE - NOT SELECTED"),
        ("FSR-TECNICUM", "Schmersal tec.nicum", "United States", "ISO 12100 / ISO 13849 machine risk analysis, inspections, documentation and recommendations", "NAMED US CONTACT; FULL VALIDATION SCOPE UNVERIFIED", "Published consulting scope does not by itself prove independent ISO 13849-2 validation", "RISK-ASSESSMENT/CONSULTING CANDIDATE - NOT SELECTED"),
    ]
    write_csv("provider-route-comparison.csv", [warned({
        "route_id": rid, "provider": provider, "published_location": location,
        "official_published_scope": scope, "local_status": local, "independence_issue": conflict,
        "project_fit_disposition": disposition, "selected": "FALSE", "contacted": "FALSE",
        "files_uploaded": "FALSE", "quote_requested": "FALSE", "contract_authorized": "FALSE",
    }) for rid, provider, location, scope, local, conflict, disposition in providers])

    sources = [
        ("FSR-SRC-01", "TÜV SÜD", "ISO 13849 and IEC 62061 - Manufacturing and Machinery", "https://www.tuvsud.com/en-us/services/functional-safety/iso-13849-iec-62061", "Live US service page; rechecked 2026-08-11", "SRS, PLr/SIL selection, achieved performance evaluation, validation and ISO 12100 risk-assessment services"),
        ("FSR-SRC-02", "TÜV SÜD", "US imprint", "https://www.tuvsud.com/en-us/imprint", "Live imprint; rechecked 2026-08-11", "TÜV SÜD America Inc., 401 Edgewater Place Suite 500, Wakefield MA 01880, +1 978 573-2500"),
        ("FSR-SRC-03", "TÜV Rheinland", "Functional safety of machinery", "https://www.tuv.com/usa/en/functional-safety-of-machinery.html", "Live US service page; rechecked 2026-08-11", "Machinery assessment, PL/SIL calculation, function/system validation and software assessment route"),
        ("FSR-SRC-04", "Pilz", "Safety validation for machinery safety", "https://www.pilz.com/en-US/services/machinery-safety/validation", "Live US service page; rechecked 2026-08-11", "Three validation levels; published Level 2 neutral-body language; highest level includes fault simulation"),
        ("FSR-SRC-05", "Pilz", "US headquarters", "https://www.pilz.com/en-US/company/locations?q=pilz+distributors", "Live location page; rechecked 2026-08-11", "7150 Commerce Boulevard, Canton MI 48187; +1 734 354-0272; info@pilzusa.com"),
        ("FSR-SRC-06", "Schmersal", "tec.nicum consulting", "https://www.schmersalusa.com/services/safety-services/tecnicum-consulting", "Live US service page; rechecked 2026-08-11", "ISO 12100/ISO 13849 machine risk analysis and named US functional-safety contact; complete validation scope not established"),
        ("FSR-SRC-07", "ISO", "ISO 12100:2010", "https://www.iso.org/standard/51528.html", "Edition 1; published 2010-11; rechecked 2026-08-11", "Risk-assessment and risk-reduction methodology"),
        ("FSR-SRC-08", "ISO", "ISO 13849-1:2023", "https://www.iso.org/standard/73481.html", "Edition 4; published 2023-04; rechecked 2026-08-11", "SRP/CS design and integration; does not select this project's PLr"),
        ("FSR-SRC-09", "ISO", "ISO 13849-2:2012", "https://www.iso.org/standard/53640.html", "Edition 2; published 2012-10; rechecked 2026-08-11", "Validation by analysis and test"),
    ]
    write_csv("source-register.csv", [warned({
        "source_id": rid, "organization": org, "title": title, "url": url,
        "document_revision_or_date": rev, "access_date": DATE,
        "verified_claim_boundary": claim,
        "project_acceptance_effect": "CAPABILITY LEAD ONLY - PROVIDER, PERSONNEL, SCOPE AND PROJECT ACCEPTANCE UNVERIFIED",
    }) for rid, org, title, url, rev, claim in sources])

    criteria = [
        ("FSR-COMP-01", "Named people", "Identify every assessor/validator and accountable signatory; company reputation alone is insufficient", "CV, role, signature authority and named deliverables"),
        ("FSR-COMP-02", "Controlled standards", "Document access to and competence in ISO 12100:2010, ISO 13849-1:2023 and ISO 13849-2:2012 or justified IEC 62061 route", "Competence record plus exact controlled revisions"),
        ("FSR-COMP-03", "Machinery experience", "Demonstrate relevant low-voltage electromechanical machinery/robotics experience", "Comparable project record with confidential details redacted"),
        ("FSR-COMP-04", "Allocation", "Demonstrate PLr/SIL selection and safety-function decomposition competence", "Method statement and named calculation owner"),
        ("FSR-COMP-05", "Quantitative design", "Demonstrate category/architecture, MTTFd/B10d, DCavg, CCF, systematic-measure and fault-exclusion competence", "SISTEMA or equivalent tool/version and review method"),
        ("FSR-COMP-06", "Validation", "Demonstrate ISO 13849-2 analysis, test, fault injection and measurement-uncertainty competence", "Validation plan example and instrument/trace expectations"),
        ("FSR-COMP-07", "Independence", "Disclose design, sales, component, integration and financial conflicts; no person approves their own work", "Signed conflict declaration and role-separation map"),
        ("FSR-COMP-08", "Provider overlap", "If one provider advises design and validates it, use different named people and written organizational independence accepted before work", "Signed independence disposition"),
        ("FSR-COMP-09", "Site capability", "State Boston site-visit ability and what cannot be validated remotely", "Written delivery/site plan"),
        ("FSR-COMP-10", "Evidence custody", "Return signed reports, editable calculations, raw test data, issue log and exact configuration binding", "Contract deliverables schedule"),
        ("FSR-COMP-11", "Authority boundary", "Reviewer recommendations do not authorize Project Button work; phase authority remains with controlled gate process", "Signed acknowledgement"),
        ("FSR-COMP-12", "Expiry/change", "Define when design, component, firmware, standard or test changes invalidate the review", "Validity and change-impact clause"),
    ]
    write_csv("competence-independence-criteria.csv", [warned({
        "criterion_id": rid, "topic": topic, "requirement": requirement,
        "evidence_required": evidence, "evidence_received": "FALSE", "accepted": "FALSE",
    }) for rid, topic, requirement, evidence in criteria])

    phases = [
        ("FSR-SOW-A01", "A pre-design", "ISO 12100 lifecycle/mode hazard review and PLr/SIL selection for each credited function", "Signed risk assessment and allocation"),
        ("FSR-SOW-A02", "A pre-design", "Review SF-01, SF-03, DF-01 zero-credit and PG-01 physical-protection boundaries", "Redlined and signed SRS"),
        ("FSR-SOW-A03", "A pre-design", "Review P1.15 core electrical source; treat P1.17 as a non-authoritative observation view", "Configuration-bound electrical review"),
        ("FSR-SOW-A04", "A pre-design", "Assess category/architecture, MTTFd/B10d, DCavg, CCF, systematic measures and fault exclusions", "Editable calculation plus signed result"),
        ("FSR-SOW-A05", "A pre-design", "Review the 200 ms / 2.000 degree setup candidate and the prohibition on 30 degree/s automatic motion", "Accepted limit or explicit replacement with rationale"),
        ("FSR-SOW-B01", "B before E2", "Approve the disconnected-load E2 validation plan, measurement method, fault fixtures and reset/restart tests", "Signed pre-test review; no actuator source connected"),
        ("FSR-SOW-B02", "B before E2", "Review exact received control hardware, wiring inspection and evidence-parity forms", "Phase-specific disposition; work authority remains separate"),
        ("FSR-SOW-C01", "C before E4", "Review received final elements, written DC application, guard/stops, loaded rail decay and physical traces", "Signed readiness or blocker report"),
        ("FSR-SOW-C02", "C before E4", "Validate each achieved safety function against the selected target using analysis and physical fault injection", "Signed ISO 13849-2 validation report"),
        ("FSR-SOW-C03", "C before E4", "Document residual risk, deviations, change impact and exact released configuration", "Signed final disposition; no general product certification implied"),
    ]
    write_csv("scope-of-work.csv", [warned({
        "scope_id": rid, "phase": phase, "task": task, "required_deliverable": deliverable,
        "provider_accepted": "FALSE", "executed": "FALSE", "accepted_by_project": "FALSE",
    }) for rid, phase, task, deliverable in phases])

    questions = [
        "Will you accept a small, noncommercial, adult-only guarded robot prototype located in Boston, Massachusetts?",
        "Which named people would perform ISO 12100 risk assessment, PLr/SIL allocation and ISO 13849-2 validation?",
        "Do you support ISO 13849-1:2023 and ISO 13849-2:2012 for this machinery scope?",
        "Can you provide written competence records and disclose assessor/signatory roles?",
        "Can you provide a signed independence/conflict disposition, including component sales or prior design assistance?",
        "Which work requires an on-site Boston visit, and which work can be reviewed remotely?",
        "Will you return editable PL calculations, signed reports, raw test evidence and an issue-closure register?",
        "Can the work be contracted in pre-design, pre-E2 and pre-E4 phases without implying authorization between phases?",
        "What additional configuration, hazard, hardware or test evidence is required before you can quote or accept scope?",
        "What commercial, confidentiality and file-transfer process applies before any project files are transmitted?",
    ]
    write_csv("capability-inquiry-register.csv", [warned({
        "question_id": f"FSR-Q-{i:02d}", "question": q, "response": "NOT SENT",
        "response_evidence": "NOT RECEIVED", "accepted": "FALSE",
    }) for i, q in enumerate(questions, 1)])

    write_csv("capability-inquiry-authorization-template.csv", [warned({
        "field": field, "value": value, "required_before_send": required,
    }) for field, value, required in [
        ("selected route", "SELECTION REQUIRED", "TRUE"),
        ("approved recipient", "SELECTION REQUIRED", "TRUE"),
        ("authorized sender", "SELECTION REQUIRED", "TRUE"),
        ("commercial authority", "NOT AUTHORIZED", "TRUE"),
        ("files approved for transmission", "NONE", "TRUE"),
        ("confidentiality disposition", "SELECTION REQUIRED", "TRUE"),
        ("quote request", "NOT AUTHORIZED", "TRUE"),
        ("send state", "NOT SENT", "TRUE"),
    ]])

    declarations = [
        "reviewer legal name", "employer and role", "relevant competence evidence", "standards and revisions controlled",
        "prior design or sales involvement", "component/vendor conflicts", "financial conflicts", "organizational independence measures",
        "scope accepted", "limitations and exclusions", "signature", "signature date", "valid-until/change trigger",
    ]
    write_csv("reviewer-declaration-template.csv", [warned({
        "field_id": f"FSR-DEC-{i:02d}", "field": field, "value": "SELECTION REQUIRED",
        "review_state": "NOT EXECUTED", "project_acceptance": "NOT ACCEPTED",
    }) for i, field in enumerate(declarations, 1)])

    deliverables = [
        "signed safety requirements specification", "signed ISO 12100 risk assessment", "safety-function PLr/SIL allocation",
        "editable SISTEMA or equivalent calculation", "category/architecture and subsystem decomposition",
        "MTTFd/B10d and mission-profile evidence", "DCavg and diagnostic test evidence", "CCF analysis and measures",
        "systematic-measures and fault-exclusion disposition", "signed validation plan", "raw physical/fault-injection evidence",
        "signed ISO 13849-2 validation report", "residual-risk register", "review issue/closure register",
        "competence and independence declarations", "exact commit/configuration/manifest binding",
    ]
    write_csv("deliverable-acceptance-matrix.csv", [warned({
        "deliverable_id": f"FSR-DEL-{i:02d}", "deliverable": item, "received": "FALSE",
        "configuration_bound": "FALSE", "technically_accepted": "FALSE", "signed": "FALSE",
    }) for i, item in enumerate(deliverables, 1)])

    authority = [
        ("internal provider comparison", "TRUE", "Research only; no endorsement"),
        ("send capability inquiry", "FALSE", "Requires completed authorization template"),
        ("upload project files", "FALSE", "Requires explicit file list and confidentiality authorization"),
        ("request or accept quote", "FALSE", "Requires commercial authority"),
        ("select or contract provider", "FALSE", "Requires competence/independence and scope disposition"),
        ("perform powered test or motion", "FALSE", "Requires separate phase-specific gate authorization"),
        ("energize or approve design", "FALSE", "This package grants no work or technical approval"),
    ]
    write_csv("authority-boundary.csv", [warned({
        "activity": activity, "permitted_by_this_package": allowed, "boundary": boundary,
    }) for activity, allowed, boundary in authority])

    status = {
        "identifier": IDENTIFIER, "round": ROUND, "date": DATE,
        "configuration_bindings": len(bound), "provider_routes": len(providers),
        "source_records": len(sources), "competence_criteria": len(criteria),
        "scope_records": len(phases), "capability_questions": len(questions),
        "deliverable_records": len(deliverables), "provider_selected": False,
        "provider_contacted": False, "files_uploaded": False, "quote_requested": False,
        "contract_authorized": False, "named_reviewer_accepted": False,
        "plr_or_sil_assigned": False, "physical_validation_executed": False,
        "functional_safety_approved": False, "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = "".join(
        f'<article class="card" data-kind="{("local " if "Massachusetts" in loc else "")}{("full " if "validation" in scope.lower() else "consulting ")}candidate">'
        f'<p class="tag">{html.escape(rid)}</p><h2>{html.escape(provider)}</h2><p><strong>Published location:</strong> {html.escape(loc)}</p>'
        f'<p>{html.escape(scope)}</p><p class="hold">{html.escape(disposition)}</p></article>'
        for rid, provider, loc, scope, _local, _conflict, disposition in providers
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 functional-safety review route</title><style>
:root{{--sky:#bfe8ff;--blue:#072a5e;--gold:#f6c445;--paper:#f7fbff;--ink:#10243d;--line:#8fbedd}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.25vw,19px)/1.55 system-ui,sans-serif}}
header{{background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold);padding:clamp(24px,5vw,68px)}}
main{{max-width:1180px;margin:auto;padding:28px}}h1{{color:var(--blue);font-size:clamp(34px,6vw,66px);line-height:1.05;margin:.2em 0}}
.warning{{background:var(--blue);color:white;padding:16px;border-left:12px solid var(--gold);font-weight:750}}
.filters{{display:flex;flex-wrap:wrap;gap:10px;margin:28px 0}}button{{font:inherit;min-height:48px;padding:10px 16px;border:2px solid var(--blue);border-radius:12px;background:white;color:var(--blue);font-weight:700}}
button[aria-pressed="true"]{{background:var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:20px}}
.card{{background:white;border:2px solid var(--line);border-radius:18px;padding:22px;box-shadow:7px 7px 0 var(--sky)}}.tag{{font-size:14px;font-weight:800;color:var(--blue)}}
.hold{{border-left:6px solid var(--gold);padding-left:12px;font-weight:700}}.hidden{{display:none}}footer{{margin-top:30px;font-size:14px}}
</style></head><body><header><p class="tag">R219 · {IDENTIFIER}</p><h1>Find the reviewer. Keep the gates closed.</h1><p>Four official capability routes are screened. None is selected, contacted, quoted or authorized.</p></header>
<main><p class="warning">{WARNING}</p><div class="filters" aria-label="Filter provider routes"><button data-filter="all" aria-pressed="true">All routes</button><button data-filter="local" aria-pressed="false">Local MA office</button><button data-filter="full" aria-pressed="false">Published validation scope</button><button data-filter="consulting" aria-pressed="false">Consulting scope only</button></div><section class="grid">{cards}</section>
<section><h2>What this closes</h2><p>A controlled way to assess competence, independence, scope and deliverables before contacting a provider.</p><h2>What remains open</h2><p>Named people, project acceptance, quote, contract, PLr/SIL, calculations, physical fault injection, stopping evidence and signed validation.</p></section><footer>{WARNING}</footer></main>
<script>const buttons=[...document.querySelectorAll('button')],cards=[...document.querySelectorAll('.card')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');const f=b.dataset.filter;cards.forEach(c=>c.classList.toggle('hidden',f!=='all'&&!c.dataset.kind.includes(f)))}}));</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    print(f"generated {IDENTIFIER}: 4 routes; no provider selected/contacted; no safety or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
