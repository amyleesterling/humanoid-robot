#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 governance-control snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "governance-p0.3"
WEB = ROOT / "release" / "hr-v0" / "governance-p0.3"
IDENTIFIER = "HR-V0-GOV-P0.3"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"

SOURCES = {
    "requirements": ROOT / "requirements" / "requirements.csv",
    "risks": ROOT / "safety" / "risk-register.csv",
    "gates": ROOT / "requirements" / "hr-v0-energization-gates.csv",
    "procedures": ROOT / "tests" / "procedures" / "procedure-registry.csv",
    "atomic_requirements": ROOT / "requirements" / "atomic-p0.2" / "atomic-requirements.csv",
    "atomic_requirements_summary": ROOT / "requirements" / "atomic-p0.2" / "atomic-requirements-summary.json",
}

LEVEL_ROLES = {
    "system": ("systems_engineer", "qualified_systems_reviewer"),
    "safety": ("functional_safety_engineer", "qualified_functional_safety_reviewer"),
    "electrical": ("electrical_engineer", "qualified_electrical_reviewer"),
    "control": ("controls_engineer", "qualified_controls_reviewer"),
    "thermal": ("thermal_engineer", "qualified_mechanical_electrical_reviewer"),
    "gripper": ("mechanical_engineer", "qualified_mechanical_reviewer"),
    "mechanical": ("mechanical_engineer", "qualified_mechanical_reviewer"),
    "verification": ("test_engineer", "qualified_independent_test_reviewer"),
    "configuration": ("configuration_manager", "program_owner"),
    "product": ("systems_engineer", "program_owner"),
    "legs": ("mechanical_controls_engineer", "qualified_mechanical_controls_reviewer"),
    "walking": ("walking_controls_engineer", "qualified_mechanical_controls_reviewer"),
    "stance": ("walking_test_engineer", "qualified_mechanical_controls_reviewer"),
    "commissioning": ("test_director", "qualified_electrical_functional_safety_reviewers"),
}

GATE_APPROVERS = {
    "program": "program_owner_and_qualified_applicability_reviewer",
    "configuration": "configuration_manager_and_program_owner",
    "bill_of_materials": "responsible_domain_reviewers_and_program_owner",
    "mechanical": "qualified_mechanical_reviewer",
    "safety": "qualified_functional_safety_reviewer",
    "electrical": "qualified_electrical_reviewer",
    "controls": "qualified_controls_reviewer",
    "commissioning": "test_director_and_qualified_electrical_functional_safety_reviewers",
    "system_test": "test_director_and_qualified_systems_safety_reviewers",
    "inspection": "responsible_domain_reviewer_and_independent_witness",
    "electrical_test": "qualified_electrical_reviewer_and_test_director",
    "safety_test": "qualified_functional_safety_reviewer_and_test_director",
    "review": "program_owner_and_all_required_qualified_reviewers",
    "controls_test": "qualified_controls_reviewer_and_test_director",
    "thermal_test": "qualified_thermal_reviewer_and_test_director",
    "mechanical_test": "qualified_mechanical_reviewer_and_test_director",
    "release": "program_owner_and_all_required_qualified_reviewers",
}

# Explicit review screen only. These IDs retain their original parent requirement and
# require controlled atomic children before approval; R141 does not invent those children.
COMPOUND_REQUIREMENTS = {
    "SYS-001", "SYS-002", "SYS-004", "SYS-005", "SYS-006",
    "SAFE-003", "SAFE-004", "SAFE-007", "SAFE-008", "SAFE-010", "SAFE-011",
    "ELEC-001", "ELEC-003", "ELEC-004",
    "CTRL-003", "CTRL-004", "CTRL-005", "CTRL-006", "CTRL-007", "CTRL-008",
    "THERM-001", "GRIP-002", "MECH-001", "MECH-002", "MECH-003", "MECH-004", "MECH-005", "MECH-006",
    "VER-001", "CFG-001", "CFG-002", "CFG-003", "GOV-001",
    "PROD-001", "PROD-002", "PROD-005", "PROD-006", "PROD-008", "PROD-009", "PROD-010", "PROD-011",
    "LEG-001", "LEG-002",
    "WALK-002", "WALK-003", "WALK-004", "WALK-005", "WALK-006", "WALK-007", "WALK-008", "WALK-009", "WALK-011", "WALK-013", "WALK-014",
    "STANCE-001", "STANCE-002", "STANCE-003", "STANCE-004",
    "MASS-001", "MASS-002", "SAFE-009",
    "COMM-001", "COMM-002", "COMM-003", "COMM-004", "COMM-005",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    requirements = read_csv(SOURCES["requirements"])
    risks = read_csv(SOURCES["risks"])
    gates = read_csv(SOURCES["gates"])
    procedures = {row["verification_id"]: row for row in read_csv(SOURCES["procedures"])}
    levels = {row["id"]: row["level"] for row in requirements}

    requirement_rows: list[dict[str, str]] = []
    for row in requirements:
        owner_role, approver_role = LEVEL_ROLES[row["level"]]
        procedure = procedures[row["verification_id"]]
        requirement_rows.append({
            "record_type": "requirement",
            "record_id": row["id"],
            "domain": row["level"],
            "source_status": row["status"],
            "accountable_role_candidate": owner_role,
            "accountable_person": "SELECTION REQUIRED",
            "verification_id": row["verification_id"],
            "acceptance_evidence": procedure["evidence_required"],
            "evidence_uri": "NOT EXECUTED",
            "approver_role_candidate": approver_role,
            "approver_person": "SELECTION REQUIRED",
            "decision": "NOT APPROVED",
            "change_history": "R141 snapshot; prior record-level history NOT BACKFILLED",
            "governance_state": "PARTIAL - ROLES CANDIDATE; PEOPLE/EVIDENCE/APPROVAL/HISTORY OPEN",
            "warning": WARNING,
        })
    write_csv(OUT / "requirement-control-register.csv", requirement_rows)

    risk_rows: list[dict[str, str]] = []
    for row in risks:
        linked = [item.strip() for item in row["linked_requirements"].split(";") if item.strip()]
        linked_levels = [levels[item] for item in linked]
        lead_level = linked_levels[0]
        owner_role, approver_role = LEVEL_ROLES[lead_level]
        risk_rows.append({
            "record_type": "risk",
            "record_id": row["risk_id"],
            "domain_basis": ";".join(dict.fromkeys(linked_levels)),
            "source_status": row["status"],
            "accountable_role_candidate": owner_role,
            "accountable_person": "SELECTION REQUIRED",
            "linked_requirements": ";".join(linked),
            "acceptance_evidence": "approved linked-requirement evidence; configuration-specific residual-risk evaluation; control-effectiveness evidence",
            "evidence_uri": "NOT EXECUTED",
            "approver_role_candidate": approver_role,
            "approver_person": "SELECTION REQUIRED",
            "decision": "RESIDUAL RISK NOT ACCEPTED",
            "change_history": "R141 snapshot; prior record-level history NOT BACKFILLED",
            "governance_state": "PARTIAL - LEAD ROLE DERIVED FOR REVIEW; PEOPLE/EVIDENCE/APPROVAL/HISTORY OPEN",
            "warning": WARNING,
        })
    write_csv(OUT / "risk-control-register.csv", risk_rows)

    gate_rows: list[dict[str, str]] = []
    for row in gates:
        gate_rows.append({
            "record_type": "gate",
            "record_id": row["gate_id"],
            "domain": row["domain"],
            "required_before_stage": row["required_before_stage"],
            "source_status": row["status"],
            "accountable_role_candidate": row["owner"],
            "accountable_person": "SELECTION REQUIRED",
            "acceptance_evidence": row["required_evidence"],
            "evidence_uri": row["evidence_location"] or "NOT EXECUTED",
            "approver_role_candidate": GATE_APPROVERS[row["domain"]],
            "approver_person": "SELECTION REQUIRED",
            "decision": "NOT APPROVED",
            "change_history": "R141 snapshot; prior record-level history NOT BACKFILLED",
            "governance_state": "PARTIAL - ROLES CANDIDATE; PEOPLE/SIGNATURE/HISTORY OPEN",
            "warning": WARNING,
        })
    write_csv(OUT / "gate-control-register.csv", gate_rows)

    atomicity_rows = []
    for row in requirements:
        compound = row["id"] in COMPOUND_REQUIREMENTS
        atomicity_rows.append({
            "requirement_id": row["id"],
            "review_state": "DECOMPOSED CANDIDATE - INDEPENDENT REVIEW REQUIRED" if compound else "ATOMIC CANDIDATE - INDEPENDENT REVIEW REQUIRED",
            "parent_statement": row["statement"],
            "child_requirement_register": "requirements/atomic-p0.2/atomic-requirements.csv" if compound else "NOT APPLICABLE CANDIDATE",
            "closure_evidence": "independent review confirms complete/nonoverlapping parent coverage, one testable obligation per child, stable parent trace and child-specific verification results" if compound else "independent requirements review confirms one measurable obligation",
            "approval_effect": "NONE - source requirement remains draft",
            "warning": WARNING,
        })
    write_csv(OUT / "requirement-atomicity-review.csv", atomicity_rows)

    source_rows = [
        {"source_id": key, "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "state": "CONTROLLED INPUT SNAPSHOT"}
        for key, path in SOURCES.items()
    ]
    write_csv(OUT / "source-register.csv", source_rows)

    holds = [
        ("GOV-HOLD-001", "select named accountable people for every requirement, risk and gate"),
        ("GOV-HOLD-002", "select independent qualified approvers and record scope/competence/independence"),
        ("GOV-HOLD-003", "decompose every compound requirement into stable atomic child requirements"),
        ("GOV-HOLD-004", "backfill controlled row-level change history without rewriting historical evidence"),
        ("GOV-HOLD-005", "bind executed evidence URIs and immutable configuration hashes"),
        ("GOV-HOLD-006", "record approval/rejection decisions and signatures only after evidence review"),
        ("GOV-HOLD-007", "obtain configuration-specific residual-risk decisions from accountable roles"),
        ("GOV-HOLD-008", "independently review role allocation and separation of author/reviewer/approver"),
        ("GOV-HOLD-009", "merge and formally accept the immutable candidate before any baseline claim"),
    ]
    hold_rows = [
        {"hold_id": hold_id, "required_evidence": evidence, "state": "OPEN", "warning": WARNING}
        for hold_id, evidence in holds
    ]
    write_csv(OUT / "governance-holds.csv", hold_rows)

    summary = {
        "identifier": IDENTIFIER,
        "date": DATE,
        "warning": WARNING,
        "requirement_count": len(requirement_rows),
        "risk_count": len(risk_rows),
        "gate_count": len(gate_rows),
        "compound_requirement_count": len(COMPOUND_REQUIREMENTS),
        "decomposed_candidate_parent_count": len(COMPOUND_REQUIREMENTS),
        "atomic_child_candidate_count": 458,
        "internally_separated_r142_duty_count": 62,
        "atomic_candidate_count": len(requirement_rows) - len(COMPOUND_REQUIREMENTS),
        "open_hold_count": len(hold_rows),
        "named_accountable_person_count": 0,
        "named_approver_person_count": 0,
        "approved_record_count": 0,
        "executed_evidence_record_count": 0,
        "governance_requirement_closed": False,
        "energization_authorized": False,
    }
    (OUT / "governance-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    combined = requirement_rows + risk_rows + gate_rows
    payload = json.dumps(combined).replace("</", "<\\/")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 governance control P0.3</title><style>
:root{{--sky:#8ed5ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--paper:#f4f9ff;--ink:#10253d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{padding:15px 5vw;background:var(--gold);font-weight:850;line-height:1.35;overflow-wrap:anywhere;white-space:normal}}header,main,footer{{padding:28px 5vw}}header{{background:var(--sky)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.08;color:var(--dark);max-width:1100px}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px}}.number{{font-size:32px;font-weight:850;color:var(--dark)}}label,input,select,button{{font-size:16px}}.filters{{display:grid;grid-template-columns:2fr 1fr;gap:14px;margin:18px 0}}input,select{{width:100%;padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1600px;table-layout:fixed}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #b8d3e7;vertical-align:top;overflow-wrap:anywhere}}th{{position:sticky;top:0;background:var(--dark);color:white}}th:nth-child(1){{width:120px}}th:nth-child(2){{width:150px}}th:nth-child(3){{width:260px}}th:nth-child(4){{width:430px}}th:nth-child(5){{width:300px}}th:nth-child(6){{width:340px}}.state{{font-weight:750;color:#8b1e1e}}footer{{background:var(--dark);color:white;margin-top:28px}}@media(max-width:640px){{header,main,footer{{padding:20px}}.filters{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R143 · {DATE}</p><h1>Accountability coverage with audited child trace.</h1><p>This review surface covers every current requirement, risk and release gate and links the 66 compound parents to 458 draft child candidates. Internal review separated 62 R142 multi-duty records; independent acceptance remains open. Roles are candidates; named people, signatures, executed evidence and row-level history remain open.</p></header><main><section class="cards"><div class="card"><div class="number">{len(requirement_rows)}</div>requirements</div><div class="card"><div class="number">{len(risk_rows)}</div>risks</div><div class="card"><div class="number">{len(gate_rows)}</div>gates</div><div class="card"><div class="number">458</div>draft atomic children</div><div class="card"><div class="number">0</div>approved records</div></section><section><h2>Controlled register</h2><div class="filters"><label>Search<input id="search" type="search" placeholder="ID, role, evidence or state"></label><label>Record type<select id="kind"><option value="">All</option><option>requirement</option><option>risk</option><option>gate</option></select></label></div><p id="count" aria-live="polite"></p><div class="table-wrap"><table><thead><tr><th>Record</th><th>Domain/stage</th><th>Accountability</th><th>Evidence</th><th>Approval</th><th>State</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Fail-closed interpretation</h2><p>A role label is not a person, a file path is not executed evidence, and a clean checker is not approval. The 458 child IDs are draft candidates, not passed obligations. Every record remains preliminary until named accountable people and qualified approvers review configuration-bound evidence and sign a controlled decision.</p><p><a href="../../../requirements/governance-p0.3/requirement-control-register.csv">Requirements</a> · <a href="../../../requirements/governance-p0.3/risk-control-register.csv">Risks</a> · <a href="../../../requirements/governance-p0.3/gate-control-register.csv">Gates</a> · <a href="../../../requirements/governance-p0.3/requirement-atomicity-review.csv">Atomicity review</a> · <a href="../atomic-requirements-p0.2/index.html">Atomic children</a> · <a href="../../../requirements/governance-p0.3/governance-summary.json">Summary</a></p></section></main><footer>{WARNING}. GOV-001 and Sol B-018/N-004 remain open.</footer><script>
const data={payload};const search=document.querySelector('#search'),kind=document.querySelector('#kind'),body=document.querySelector('#rows'),count=document.querySelector('#count');function esc(v){{return String(v??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function render(){{const q=search.value.toLowerCase(),k=kind.value;const rows=data.filter(r=>(!k||r.record_type===k)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));count.textContent=`${{rows.length}} of ${{data.length}} records shown`;body.innerHTML=rows.map(r=>`<tr><td><strong>${{esc(r.record_id)}}</strong><br>${{esc(r.record_type)}}</td><td>${{esc(r.domain||r.domain_basis||'')}}<br>${{esc(r.required_before_stage||'')}}</td><td>${{esc(r.accountable_role_candidate)}}<br><span class="state">person: ${{esc(r.accountable_person)}}</span></td><td>${{esc(r.verification_id||'')}}<br>${{esc(r.acceptance_evidence)}}</td><td>${{esc(r.approver_role_candidate)}}<br><span class="state">${{esc(r.decision)}}</span></td><td class="state">${{esc(r.governance_state)}}</td></tr>`).join('')}}search.addEventListener('input',render);kind.addEventListener('change',render);render();
</script></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: {len(requirement_rows)} requirements / {len(risk_rows)} risks / {len(gate_rows)} gates")
    print(f"{len(COMPOUND_REQUIREMENTS)} compound screens / {len(hold_rows)} open holds / 0 approvals")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
