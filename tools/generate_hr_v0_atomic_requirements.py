#!/usr/bin/env python3
"""Generate the R142 atomic child-requirement candidate baseline."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from hr_v0_atomic_requirement_data import DECOMPOSITIONS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "atomic-p0.1"
WEB = ROOT / "release" / "hr-v0" / "atomic-requirements-p0.1"
IDENTIFIER = "HR-V0-REQ-ATOMIC-P0.1"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"
SOURCES = {
    "parent_requirements": ROOT / "requirements" / "requirements.csv",
    "procedures": ROOT / "tests" / "procedures" / "procedure-registry.csv",
    "r141_atomicity_screen": ROOT / "requirements" / "governance-p0.1" / "requirement-atomicity-review.csv",
    "controlled_decomposition_data": ROOT / "tools" / "hr_v0_atomic_requirement_data.py",
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
    parents = {row["id"]: row for row in read_csv(SOURCES["parent_requirements"])}
    procedures = {row["verification_id"]: row for row in read_csv(SOURCES["procedures"])}
    screen = {row["requirement_id"]: row for row in read_csv(SOURCES["r141_atomicity_screen"])}

    child_rows: list[dict[str, str]] = []
    parent_rows: list[dict[str, str]] = []
    for parent_id in sorted(DECOMPOSITIONS):
        parent = parents[parent_id]
        procedure = procedures[parent["verification_id"]]
        children = DECOMPOSITIONS[parent_id]
        first_child = f"{parent_id}-A01"
        last_child = f"{parent_id}-A{len(children):02d}"
        parent_rows.append({
            "parent_id": parent_id,
            "parent_level": parent["level"],
            "parent_status": parent["status"],
            "verification_id": parent["verification_id"],
            "child_count": str(len(children)),
            "first_child_id": first_child,
            "last_child_id": last_child,
            "decomposition_state": "CANDIDATE COMPLETE - INDEPENDENT REQUIREMENTS REVIEW REQUIRED",
            "approval_effect": "NONE - PARENT AND CHILDREN REMAIN DRAFT",
            "warning": WARNING,
        })
        for sequence, statement in enumerate(children, 1):
            child_rows.append({
                "child_id": f"{parent_id}-A{sequence:02d}",
                "parent_id": parent_id,
                "sequence": str(sequence),
                "level": parent["level"],
                "child_statement": statement,
                "priority": parent["priority"],
                "verification_id": parent["verification_id"],
                "parent_procedure_evidence": procedure["evidence_required"],
                "child_acceptance_binding": "CHILD-SPECIFIC RESULT REQUIRED IN PARENT PROCEDURE RECORD",
                "status": "draft",
                "evidence_uri": "NOT EXECUTED",
                "accountable_person": "SELECTION REQUIRED",
                "approver_person": "SELECTION REQUIRED",
                "decision": "NOT APPROVED",
                "warning": WARNING,
            })
    write_csv(OUT / "atomic-requirements.csv", child_rows)
    write_csv(OUT / "parent-decomposition-summary.csv", parent_rows)

    source_rows = [
        {"source_id": key, "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "state": "CONTROLLED INPUT SNAPSHOT"}
        for key, path in SOURCES.items()
    ]
    write_csv(OUT / "source-register.csv", source_rows)

    holds = [
        ("ATOMIC-HOLD-001", "independent requirements review of every child statement and parent coverage"),
        ("ATOMIC-HOLD-002", "confirm that no child contains multiple independently passable obligations"),
        ("ATOMIC-HOLD-003", "confirm that no parent duty was lost, weakened, strengthened or moved without change control"),
        ("ATOMIC-HOLD-004", "define child-specific acceptance fields in each parent verification record"),
        ("ATOMIC-HOLD-005", "select named accountable people and qualified independent approvers"),
        ("ATOMIC-HOLD-006", "execute configuration-bound evidence and record child-level pass/fail decisions"),
        ("ATOMIC-HOLD-007", "update risk and gate trace only after independent acceptance of child IDs"),
        ("ATOMIC-HOLD-008", "merge and formally baseline the accepted parent-child hierarchy"),
    ]
    hold_rows = [{"hold_id": key, "required_evidence": evidence, "state": "OPEN", "warning": WARNING} for key, evidence in holds]
    write_csv(OUT / "atomic-requirement-holds.csv", hold_rows)

    summary = {
        "identifier": IDENTIFIER,
        "date": DATE,
        "warning": WARNING,
        "parent_count": len(parent_rows),
        "child_count": len(child_rows),
        "covered_r141_compound_parent_count": sum(screen[key]["review_state"].startswith("COMPOUND") for key in DECOMPOSITIONS),
        "minimum_children_per_parent": min(len(value) for value in DECOMPOSITIONS.values()),
        "maximum_children_per_parent": max(len(value) for value in DECOMPOSITIONS.values()),
        "open_hold_count": len(hold_rows),
        "executed_evidence_count": 0,
        "approved_child_count": 0,
        "approved_parent_count": 0,
        "governance_requirement_closed": False,
        "energization_authorized": False,
    }
    (OUT / "atomic-requirements-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    payload = json.dumps(child_rows).replace("</", "<\\/")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 atomic requirements P0.1</title><style>
:root{{--sky:#8ed5ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--paper:#f4f9ff;--ink:#10253d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{padding:15px 5vw;background:var(--gold);font-weight:850;line-height:1.35;overflow-wrap:anywhere}}header,main,footer{{padding:28px 5vw}}header{{background:var(--sky)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.08;color:var(--dark);max-width:1100px}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px}}.number{{font-size:32px;font-weight:850}}label,input,select{{font-size:16px}}.filters{{display:grid;grid-template-columns:2fr 1fr;gap:14px;margin:18px 0}}input,select{{width:100%;padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1350px;table-layout:fixed}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #b8d3e7;vertical-align:top;overflow-wrap:anywhere}}th{{position:sticky;top:0;background:var(--dark);color:white}}th:nth-child(1){{width:150px}}th:nth-child(2){{width:120px}}th:nth-child(3){{width:520px}}th:nth-child(4){{width:180px}}th:nth-child(5){{width:380px}}.state{{font-weight:750;color:#8b1e1e}}footer{{background:var(--dark);color:white;margin-top:28px}}@media(max-width:640px){{header,main,footer{{padding:20px}}.filters{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R142 · {DATE}</p><h1>One testable obligation per child record.</h1><p>The 66 compound parents now have stable candidate child IDs. All 396 children remain draft, unexecuted and unapproved pending independent requirements review.</p></header><main><section class="cards"><div class="card"><div class="number">{len(parent_rows)}</div>compound parents</div><div class="card"><div class="number">{len(child_rows)}</div>atomic child candidates</div><div class="card"><div class="number">0</div>approved children</div><div class="card"><div class="number">{len(hold_rows)}</div>open holds</div></section><section><h2>Atomic child register</h2><div class="filters"><label>Search<input id="search" type="search" placeholder="Child ID, parent, statement or procedure"></label><label>Parent<select id="parent"><option value="">All 66 parents</option>{''.join(f'<option>{key}</option>' for key in sorted(DECOMPOSITIONS))}</select></label></div><p id="count" aria-live="polite"></p><div class="table-wrap"><table><thead><tr><th>Child / parent</th><th>Domain</th><th>Atomic obligation</th><th>Verification</th><th>State</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Fail-closed interpretation</h2><p>Stable IDs improve traceability; they do not prove that the decomposition is complete or correct. A parent procedure must produce a separate result for every accepted child. No child inherits a pass merely because its parent has a document or checker.</p><p><a href="../../../requirements/atomic-p0.1/atomic-requirements.csv">Child register</a> · <a href="../../../requirements/atomic-p0.1/parent-decomposition-summary.csv">Parent summary</a> · <a href="../../../requirements/atomic-p0.1/atomic-requirement-holds.csv">Open holds</a> · <a href="../../../requirements/atomic-p0.1/atomic-requirements-summary.json">Status</a></p></section></main><footer>{WARNING}. GOV-001 and Sol N-004 remain open pending independent review and acceptance.</footer><script>
const data={payload};const search=document.querySelector('#search'),parent=document.querySelector('#parent'),body=document.querySelector('#rows'),count=document.querySelector('#count');function esc(v){{return String(v??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function render(){{const q=search.value.toLowerCase(),p=parent.value;const rows=data.filter(r=>(!p||r.parent_id===p)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));count.textContent=`${{rows.length}} of ${{data.length}} child records shown`;body.innerHTML=rows.map(r=>`<tr><td><strong>${{esc(r.child_id)}}</strong><br>parent ${{esc(r.parent_id)}}</td><td>${{esc(r.level)}}</td><td>${{esc(r.child_statement)}}</td><td>${{esc(r.verification_id)}}<br>${{esc(r.child_acceptance_binding)}}</td><td class="state">${{esc(r.status)}}<br>${{esc(r.evidence_uri)}}<br>${{esc(r.decision)}}</td></tr>`).join('')}}search.addEventListener('input',render);parent.addEventListener('change',render);render();
</script></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: {len(parent_rows)} parents / {len(child_rows)} child candidates / {len(hold_rows)} open holds")
    print("0 evidence / 0 approvals / all source parents remain draft")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
