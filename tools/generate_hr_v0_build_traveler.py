#!/usr/bin/env python3
"""Generate the R144 integrated, unpowered HR-V0 build-traveler candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assembly/hr-v0-build-traveler-p0.1"
WEB = ROOT / "release/hr-v0/build-traveler-p0.1"
IDENTIFIER = "HR-V0-BUILD-TRAVELER-P0.1"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"

SOURCES = {
    "release_candidate": ROOT / "release/hr-v0/release-candidate.json",
    "release_manifest": ROOT / "release/hr-v0/HR-V0-RC-P0.1-file-manifest.csv",
    "energization_gates": ROOT / "requirements/hr-v0-energization-gates.csv",
    "bom_closure": ROOT / "bom/hr-v0-bom-closure.csv",
    "mechanical_release": ROOT / "docs/hr-v0-mechanical-release-p0.6.md",
    "mechanical_dfm": ROOT / "docs/hr-v0-mechanical-dfm-data-p0.1.md",
    "control_panel": ROOT / "docs/hr-v0-control-panel-p0.6.md",
    "joint_metrology": ROOT / "docs/hr-v0-joint-stack-metrology-p0.1.md",
    "guard": ROOT / "docs/hr-v0-fixed-guard-receiver-p0.3.md",
    "receiver": ROOT / "docs/hr-v0-passive-arm-receiver-detail-p0.2.md",
    "electrical": ROOT / "docs/hr-v0-electrical-v3-candidate.md",
    "e2_sequence": ROOT / "docs/hr-v0-e2-control-only-energization-p0.1.md",
    "procedure_registry": ROOT / "tests/procedures/procedure-registry.csv",
}

PHASES = [
    ("BT-P00", "Configuration and work boundary", "", "No physical work", "Exact accepted configuration and written phase authority", "OPEN"),
    ("BT-P01", "Receiving and quarantine", "BT-P00", "Unpowered; unopened or isolated articles", "Accepted purchase/receiving records and calibrated inspection tools", "OPEN"),
    ("BT-P02", "Site and bench survey", "BT-P00", "Unpowered; no machine article", "Named Boston-area site, permission, branch/service and bench evidence", "OPEN"),
    ("BT-P03", "Control-panel mechanical assembly", "BT-P01,BT-P02", "Unpowered; no conductors installed", "Released panel drilling/cut/rail/duct package", "OPEN"),
    ("BT-P04", "Frame dry assembly", "BT-P01,BT-P02", "Unpowered; actuators absent", "Released frame/joint hardware and bench interface", "OPEN"),
    ("BT-P05", "Joint-stack metrology", "BT-P01", "Unpowered; encoder reading prohibited", "Separately authorized temporary-assembly traveler and exact received articles", "OPEN"),
    ("BT-P06", "Custom-part first articles", "BT-P01,BT-P05", "Unpowered; one segregated first article per geometry", "Qualified drawing release, supplier DFM and separate first-article authority", "OPEN"),
    ("BT-P07", "Final arm mechanical assembly", "BT-P04,BT-P05,BT-P06", "Unpowered; actuator cables disconnected", "Accepted first articles, fastener stack, torque/locking and stop settings", "OPEN"),
    ("BT-P08", "Guard and passive receiver", "BT-P02,BT-P07", "Unpowered; no access credit until inspection passes", "Released guard/receiver application, anchors and proof basis", "OPEN"),
    ("BT-P09", "Harness fabrication", "BT-P01,BT-P03,BT-P07,BT-P08", "Unpowered; source ends physically absent", "Released harness drawings, pins, contacts, gauges, lengths and tooling", "OPEN"),
    ("BT-P10", "Unpowered electrical assembly", "BT-P03,BT-P08,BT-P09", "All sources absent; actuator branches disconnected and covered", "Accepted ECAD, protection, grounding and harness package", "OPEN"),
    ("BT-P11", "Compute and firmware staging", "BT-P01,BT-P10", "Unpowered installation only; no device port opened", "Accepted compute image, firmware hashes and configuration binding", "OPEN"),
    ("BT-P12", "Integrated unpowered inspection", "BT-P07,BT-P08,BT-P10,BT-P11", "All sources absent; guards installed", "Completed as-built, continuity-precheck and configuration records", "OPEN"),
    ("BT-P13", "Connection and powered-work boundary", "BT-P12", "PROHIBITED", "EG-001 through EG-022 closure and separate written authorization", "PROHIBITED"),
]

STEP_GROUPS = {
    "BT-P00": [
        ("Verify the exact candidate Git commit and deterministic file manifest.", "release_candidate|release_manifest", "configuration snapshot"),
        ("Record every current domain-product identifier from the release candidate.", "release_candidate", "product identifier checklist"),
        ("Confirm the worktree or clean clone reproduces every applicable checker.", "release_manifest", "clean-clone validation record"),
        ("Record the exact planned phase and prohibit all later phases.", "energization_gates", "phase authorization boundary"),
        ("Assign a named accountable person and qualified reviewer for the planned phase.", "procedure_registry", "signed role/competence record"),
        ("Record calibrated-tool identities and expiry dates for the planned phase.", "procedure_registry", "calibration register"),
        ("Confirm no build step starts from a document marked historical, superseded or withdrawn.", "release_candidate", "supersession audit"),
    ],
    "BT-P01": [
        ("Receive each article against an authorized order and exact manufacturer order code.", "bom_closure", "receiving line record"),
        ("Photograph manufacturer labels, lot/date codes and package condition before opening.", "bom_closure", "receiving photographs"),
        ("Quarantine any identity, quantity or condition mismatch.", "bom_closure", "nonconformance record"),
        ("Keep evaluation candidates segregated from released production material.", "bom_closure", "segregation log"),
        ("Measure controlled received interfaces without powering any article.", "joint_metrology", "raw metrology record"),
        ("Inventory exact ROBOTIS included hardware rather than trusting commerce mass fields.", "joint_metrology", "kit-content inventory"),
        ("Record certificates and heat/lot trace for controlled structural material.", "mechanical_dfm", "material certificate register"),
        ("Prevent any received article from silently closing a selection or application hold.", "bom_closure", "hold disposition record"),
    ],
    "BT-P02": [
        ("Freeze the exact Boston-area build and use location.", "energization_gates", "signed site-input record"),
        ("Record site permission, intended adult users and child-exclusion boundary.", "energization_gates", "site-use authorization"),
        ("Record mains service, branch protection, receptacle, grounding and available disconnect evidence.", "energization_gates", "qualified site electrical review"),
        ("Survey bench material, thickness, edge distances, support geometry and underside access.", "mechanical_release", "bench survey"),
        ("Select no anchor until pull-out, shear, bearing and support-load calculations are accepted.", "mechanical_release", "anchor selection hold"),
        ("Record ambient temperature, humidity/condensation controls, lighting, access and emergency response.", "energization_gates", "site environmental record"),
    ],
    "BT-P03": [
        ("Inspect the enclosure/backplate/rail/duct articles before any cutting or drilling.", "control_panel", "panel receiving inspection"),
        ("Use only a released drilling and cut schedule tied to the exact enclosure revision.", "control_panel", "panel machining traveler"),
        ("Deburr, clean and inspect every panel feature before component installation.", "control_panel", "panel feature inspection"),
        ("Install rail and duct using released fasteners, torque and corrosion controls.", "control_panel", "rail/duct installation record"),
        ("Dry-fit all bounded component envelopes and verify service/tool clearance.", "control_panel", "panel dry-fit record"),
        ("Stop before installing any wire, fuse link, mains part or unresolved cable entry.", "control_panel", "mechanical-only phase signoff"),
    ],
    "BT-P04": [
        ("Inspect profile cut lengths, end condition and bracket kit contents.", "mechanical_release", "frame receiving record"),
        ("Dry-assemble the base rectangle on a verified flat reference.", "mechanical_release", "base squareness record"),
        ("Install uprights with released bracket orientation and exact hardware.", "mechanical_release", "upright installation record"),
        ("Verify base width, depth, diagonal equality and upright perpendicularity.", "mechanical_release", "frame geometry inspection"),
        ("Install no bench anchor before BT-P02 anchor acceptance.", "mechanical_release", "anchor hold confirmation"),
        ("Apply only released torque/locking rules and witness marks.", "mechanical_release", "frame fastener log"),
        ("Quarantine the frame if any interface prevents later guard or receiver installation.", "guard|receiver", "frame nonconformance record"),
    ],
    "BT-P05": [
        ("Execute the controlled joint-stack traveler with all power absent.", "joint_metrology", "signed traveler"),
        ("Register exact actuator/frame/output faces and external mechanical datums.", "joint_metrology", "datum measurement record"),
        ("Measure fastener depth, engagement, spacer and washer requirements before installation.", "joint_metrology", "fastener stack record"),
        ("Measure backlash and mechanical angle using the released external method.", "joint_metrology", "angle/backlash raw data"),
        ("Measure received masses and conservative envelopes with uncertainty.", "joint_metrology", "mass/envelope record"),
        ("Disassemble and quarantine temporary stacks pending qualified disposition.", "joint_metrology", "teardown/quarantine signoff"),
    ],
    "BT-P06": [
        ("Obtain qualified acceptance of each exact drawing/STEP/DXF/hash set before supplier contact.", "mechanical_dfm", "drawing acceptance"),
        ("Obtain written supplier DFM and process/material/inspection agreement.", "mechanical_dfm", "supplier DFM response"),
        ("Authorize at most one segregated first article per distinct geometry.", "mechanical_dfm", "first-article authorization"),
        ("Inspect every first article against the controlled FAI and material certificate.", "mechanical_dfm", "completed FAI/MTR"),
        ("Reject or formally disposition every nonconformance before assembly use.", "mechanical_dfm", "qualified first-article disposition"),
    ],
    "BT-P07": [
        ("Install only accepted custom parts and exact received ROBOTIS interfaces.", "mechanical_release|joint_metrology|mechanical_dfm", "part identity signoff"),
        ("Assemble J1 and J2 using released fastener stacks, torque, locking and reuse rules.", "mechanical_release", "joint assembly log"),
        ("Install independent mechanical hard-stop hardware and released bumper stack.", "mechanical_release", "hard-stop installation record"),
        ("Measure stop contact angles and verify the released collision-margin allocation without power.", "mechanical_release", "stop metrology record"),
        ("Install the selected gripper and verify its exact H104 registration.", "mechanical_release", "gripper registration record"),
        ("Record as-built moving mass, center of mass and conservative inertia inputs.", "mechanical_release", "mass-property record"),
        ("Keep every actuator lead disconnected, individually covered and labeled.", "electrical", "disconnected-actuator inspection"),
    ],
    "BT-P08": [
        ("Assemble the fixed guard frame from released profiles, joints and anchors.", "guard", "guard frame traveler"),
        ("Install accepted panels, retention and tool-removable access provisions.", "guard", "panel/retention record"),
        ("Install the passive arm receiver with accepted guides, contact layer, joints and supports.", "receiver", "receiver assembly record"),
        ("Verify continuous nominal clearance using as-built survey data and released uncertainty.", "guard|receiver", "guard/receiver clearance record"),
        ("Execute authorized unpowered proof, access-probe, retention and containment inspections.", "guard|receiver", "physical inspection/proof record"),
        ("Assign no guarding or containment credit until qualified results are accepted.", "guard|receiver", "qualified guard/receiver disposition"),
    ],
    "BT-P09": [
        ("Release every harness drawing with exact connectors, contacts, seals, tools and pin views.", "electrical", "released harness drawing set"),
        ("Release every conductor manufacturer order code, gauge, color, length and termination.", "electrical", "conductor schedule"),
        ("Cut, strip and terminate only under released tooling and inspection instructions.", "electrical", "harness fabrication traveler"),
        ("Apply released labels, strain relief, shielding and bend/twist controls.", "electrical", "harness workmanship record"),
        ("Perform unpowered point-to-point, polarity, isolation and no-backfeed checks on each harness.", "electrical", "harness electrical inspection"),
        ("Quarantine every harness until pull-test and qualified acceptance pass.", "electrical", "harness acceptance/quarantine record"),
    ],
    "BT-P10": [
        ("Verify every power source and fuse link remains physically absent.", "electrical", "source-absence inspection"),
        ("Install only accepted panel components at released locations.", "control_panel|electrical", "component installation record"),
        ("Install protective-earth and bonding conductors before ordinary circuit conductors.", "electrical", "bonding installation record"),
        ("Route and terminate conductors under the released wire-number schedule.", "electrical", "panel wiring traveler"),
        ("Install actuator harnesses with source ends absent and branch ends disconnected/covered.", "electrical", "actuator harness state record"),
        ("Inspect terminal torque, ferrules, separation, shielding, labels and service loops.", "electrical", "unpowered workmanship inspection"),
        ("Stop before continuity, insulation or no-backfeed execution unless its separate procedure is authorized.", "e2_sequence", "electrical assembly phase signoff"),
    ],
    "BT-P11": [
        ("Receive and inspect exact compute, cooling, storage and power-adapter articles.", "bom_closure", "compute receiving record"),
        ("Write only an accepted image hash under the released rollback and recovery procedure.", "release_candidate", "image-write record"),
        ("Install compute hardware using released tray, retention and cable controls.", "control_panel", "compute installation record"),
        ("Build firmware reproducibly and record exact source/toolchain/binary hashes.", "release_candidate", "firmware build record"),
        ("Do not connect a source, open a device path, flash a connected actuator or request torque.", "e2_sequence", "unpowered firmware-boundary signoff"),
    ],
    "BT-P12": [
        ("Reconcile the complete as-built article to the exact BOM and file manifest.", "release_candidate|bom_closure", "as-built configuration audit"),
        ("Verify all required guards and receiver components are installed.", "guard|receiver", "integrated guard inspection"),
        ("Verify all torque witness marks and mechanical inspection records are complete.", "mechanical_release", "integrated mechanical audit"),
        ("Verify all actuator branches remain disconnected, covered and at an absent-source boundary.", "electrical", "actuator-source absence audit"),
        ("Verify every open selection, deviation and nonconformance remains visible and blocking.", "energization_gates", "open-item audit"),
        ("Verify no test record claims execution from a template or checker.", "procedure_registry", "evidence-maturity audit"),
        ("Photograph and hash the integrated unpowered article from controlled views.", "release_candidate", "as-built photograph manifest"),
        ("Quarantine the complete article pending independent review and separate E2 authorization.", "e2_sequence", "integrated quarantine record"),
    ],
    "BT-P13": [
        ("Do not connect or energize any source under this traveler.", "energization_gates|e2_sequence", "separate signed E2 authorization required"),
    ],
}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    phase_rows = [{
        "phase_id": phase_id, "phase_name": name, "depends_on": depends_on or "NONE",
        "energy_boundary": boundary, "entry_evidence": evidence, "status": status,
        "named_authorizer": "SELECTION REQUIRED", "decision": "NOT APPROVED", "warning": WARNING,
    } for phase_id, name, depends_on, boundary, evidence, status in PHASES]
    write_csv(OUT / "build-phases.csv", phase_rows)

    step_rows: list[dict[str, str]] = []
    for phase_id, name, *_ in PHASES:
        for index, (action, inputs, evidence) in enumerate(STEP_GROUPS[phase_id], 1):
            step_rows.append({
                "step_id": f"{phase_id}-S{index:02d}", "phase_id": phase_id, "phase_name": name,
                "sequence": str(index), "action": action, "required_input_keys": inputs,
                "required_evidence": evidence, "owner_role_candidate": "manufacturing_or_test_lead",
                "named_executor": "SELECTION REQUIRED", "named_reviewer": "SELECTION REQUIRED",
                "authorization_state": "NOT AUTHORIZED", "result": "NOT EXECUTED",
                "evidence_uri": "NOT EXECUTED", "stop_work_on_failure": "YES",
                "energization_effect": "NONE", "warning": WARNING,
            })
    write_csv(OUT / "build-steps.csv", step_rows)

    gate_rows = []
    with SOURCES["energization_gates"].open(newline="", encoding="utf-8") as handle:
        for gate in csv.DictReader(handle):
            if gate["required_before_stage"] not in {"E0", "E1", "E2"}:
                continue
            mapped_phase = {
                "E0": "BT-P00", "E1": "BT-P03 through BT-P12", "E2": "BT-P13",
            }[gate["required_before_stage"]]
            gate_rows.append({
                "gate_id": gate["gate_id"], "required_before_stage": gate["required_before_stage"],
                "traveler_boundary": mapped_phase, "current_status": gate["status"],
                "required_evidence": gate["required_evidence"], "evidence_location": gate["evidence_location"],
                "traveler_effect": "BLOCKS ENTRY OR RELEASE - DOES NOT CLOSE GATE",
                "warning": WARNING,
            })
    write_csv(OUT / "gate-phase-matrix.csv", gate_rows)

    hold_rows = []
    for phase_id, name, depends_on, boundary, evidence, status in PHASES:
        hold_rows.append({
            "hold_id": f"BUILD-HOLD-{int(phase_id[-2:]) + 1:03d}", "phase_id": phase_id,
            "hold_point": f"Release {name}", "required_evidence": evidence,
            "release_role_candidate": "qualified_reviewer_and_program_owner",
            "named_releaser": "SELECTION REQUIRED", "state": "OPEN" if status != "PROHIBITED" else "PROHIBITED",
            "warning": WARNING,
        })
    write_csv(OUT / "hold-points.csv", hold_rows)

    source_rows = [{
        "source_id": key, "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "state": "CONTROLLED INPUT SNAPSHOT",
    } for key, path in SOURCES.items()]
    write_csv(OUT / "source-register.csv", source_rows)

    summary = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "phase_count": len(phase_rows), "step_count": len(step_rows), "through_e2_gate_count": len(gate_rows),
        "open_phase_count": sum(row["status"] == "OPEN" for row in phase_rows),
        "prohibited_phase_count": sum(row["status"] == "PROHIBITED" for row in phase_rows),
        "authorized_step_count": 0, "executed_step_count": 0, "closed_hold_count": 0,
        "fabrication_authorized": False, "connection_authorized": False, "energization_authorized": False,
    }
    (OUT / "build-traveler-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    payload = json.dumps(step_rows).replace("</", "<\\/")
    phase_options = "".join(f'<option value="{row["phase_id"]}">{row["phase_id"]} · {row["phase_name"]}</option>' for row in phase_rows)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 unpowered build traveler P0.1</title><style>
:root{{--sky:#8ed5ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--paper:#f4f9ff;--ink:#10253d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{padding:15px 5vw;background:var(--gold);font-weight:850;line-height:1.35;overflow-wrap:anywhere}}header,main,footer{{padding:28px 5vw}}header{{background:var(--sky)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.08;color:var(--dark);max-width:1100px}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}}.card{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px}}.number{{font-size:32px;font-weight:850}}label,input,select{{font-size:16px}}.filters{{display:grid;grid-template-columns:2fr 1fr;gap:14px;margin:18px 0}}input,select{{width:100%;padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1450px;table-layout:fixed}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #b8d3e7;vertical-align:top;overflow-wrap:anywhere}}th{{position:sticky;top:0;background:var(--dark);color:white}}th:nth-child(1){{width:150px}}th:nth-child(2){{width:190px}}th:nth-child(3){{width:520px}}th:nth-child(4){{width:360px}}th:nth-child(5){{width:230px}}.state{{font-weight:750;color:#8b1e1e}}a{{color:#005ca8}}footer{{background:var(--dark);color:white;margin-top:28px}}@media(max-width:640px){{header,main,footer{{padding:20px}}.filters{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R144 · {DATE}</p><h1>Build in a controlled order. Stop before power.</h1><p>This integrated traveler sequences the current HR-V0 candidate from configuration control through unpowered final inspection. Every step is unexecuted and unauthorized. BT-P13 prohibits source connection and energization.</p></header><main><section class="cards"><div class="card"><div class="number">{len(phase_rows)}</div>controlled phases</div><div class="card"><div class="number">{len(step_rows)}</div>build steps</div><div class="card"><div class="number">{len(gate_rows)}</div>through-E2 gates mapped</div><div class="card"><div class="number">0</div>authorized steps</div><div class="card"><div class="number">0</div>executed steps</div></section><section><h2>Integrated build sequence</h2><div class="filters"><label>Search<input id="search" type="search" placeholder="Step, phase, action, input or evidence"></label><label>Phase<select id="phase"><option value="">All phases</option>{phase_options}</select></label></div><p id="count" aria-live="polite"></p><div class="table-wrap"><table><thead><tr><th>Step</th><th>Phase</th><th>Required action</th><th>Inputs and evidence</th><th>State</th></tr></thead><tbody id="rows"></tbody></table></div></section><section><h2>Traveler boundary</h2><p>This is an assembly-order and evidence-control candidate, not a work permit. A generated row is not executed evidence. A named qualified person, exact accepted inputs, phase-specific written authority and signed result are required at each hold point.</p><p><a href="../../../assembly/hr-v0-build-traveler-p0.1/build-phases.csv">Phases</a> · <a href="../../../assembly/hr-v0-build-traveler-p0.1/build-steps.csv">Steps</a> · <a href="../../../assembly/hr-v0-build-traveler-p0.1/gate-phase-matrix.csv">Gate matrix</a> · <a href="../../../assembly/hr-v0-build-traveler-p0.1/hold-points.csv">Hold points</a> · <a href="../../../assembly/hr-v0-build-traveler-p0.1/build-traveler-summary.json">Status</a></p></section></main><footer>{WARNING}. BT-P13 is PROHIBITED under this traveler.</footer><script>
const data={payload};const search=document.querySelector('#search'),phase=document.querySelector('#phase'),body=document.querySelector('#rows'),count=document.querySelector('#count');function esc(v){{return String(v??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function render(){{const q=search.value.toLowerCase(),p=phase.value;const rows=data.filter(r=>(!p||r.phase_id===p)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));count.textContent=`${{rows.length}} of ${{data.length}} build steps shown`;body.innerHTML=rows.map(r=>`<tr><td><strong>${{esc(r.step_id)}}</strong></td><td>${{esc(r.phase_id)}}<br>${{esc(r.phase_name)}}</td><td>${{esc(r.action)}}</td><td>Inputs: ${{esc(r.required_input_keys)}}<br>Evidence: ${{esc(r.required_evidence)}}</td><td class="state">${{esc(r.authorization_state)}}<br>${{esc(r.result)}}<br>${{esc(r.evidence_uri)}}</td></tr>`).join('')}}search.addEventListener('input',render);phase.addEventListener('change',render);render();
</script></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: {len(phase_rows)} phases / {len(step_rows)} steps / {len(gate_rows)} gates")
    print("0 authorized / 0 executed / BT-P13 prohibited")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
