#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 safety-requirements P0.2 package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/safety-requirements-p0.2"
IDENTIFIER = "HR-V0-SRS-P0.2"
ROUND = "R218"
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
        ("SRS-CFG-01", "system requirements", "HR-30-SYS-R0.2", "requirements/requirements.csv"),
        ("SRS-CFG-02", "atomic requirements", "HR-V0-REQ-ATOMIC-P0.2", "requirements/atomic-p0.2/atomic-requirements.csv"),
        ("SRS-CFG-03", "safety allocation boundary", "HR-V0-FSA-P0.1", "safety/hr-v0-safety-function-allocation.csv"),
        ("SRS-CFG-04", "stopping arithmetic", "HR-V0-STOP-BUDGET-P0.1", "controls/hr-v0-stopping-budget-p0.1.csv"),
        ("SRS-CFG-05", "PNOZ path conformance", "HR-V0-PNOZ-CONF-P0.1", "safety/hr-v0-pnoz-path-conformance-p0.1.csv"),
        ("SRS-CFG-06", "PNOZ component manual", "PNOZ-S4-750104-21396-EN-23", "electrical/vendor/pilz/pnoz-s4-750104-r116/PNOZ_s4_21396-EN-23.pdf"),
        ("SRS-CFG-07", "contactor application boundary", "HR-V0-K1K2-APP-P0.2", "docs/hr-v0-contactor-application-p0.1.md"),
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

    requirements = [
        ("SRS-001", "scope", "HR-V0", "All powered HR-V0 work shall remain adult-only, fixed-guarded and bench-restrained; children and bystanders shall have no access to the hazard zone.", "audit", "NOT EXECUTED", "QUALIFIED REVIEW REQUIRED"),
        ("SRS-002", "SF-01", "E2/E3/E4", "A dual-channel E-stop demand shall remove actuator-rail energy through two series interruption paths without relying on Linux, Raspberry Pi, watchdog firmware or motion software.", "analysis_and_test", "NOT EXECUTED", "QUALIFIED ALLOCATION AND PHYSICAL TEST REQUIRED"),
        ("SRS-003", "SF-01", "E4 J2 positive setup only", "From first E-stop input contact separation to the accepted stopped-motion threshold, total response shall be no more than 200 ms and residual J2 travel shall be no more than 2.000 degrees at a verified command rate no greater than 10.000 degrees per second.", "timing_test", "CANDIDATE LIMIT", "QUALIFIED ACCEPTANCE AND PHYSICAL STATISTICAL BOUND REQUIRED"),
        ("SRS-004", "SF-01", "E4 J2 positive setup only", "The 2.000-degree residual-travel limit shall retain a nominal 1.000-degree geometric reserve between the 115.000-degree software boundary and the 118.000-degree nominal positive metal stop before tolerance, backlash, compliance and uncertainty deductions.", "analysis_and_inspection", "CANDIDATE LIMIT", "TOLERANCE AND PHYSICAL STOP ACCEPTANCE REQUIRED"),
        ("SRS-005", "SF-01", "future automatic motion", "Automatic motion at 30.000 degrees per second is prohibited until the same 2.000-degree residual-travel envelope is supported by an accepted total-response bound no greater than 66.667 ms and by the released guard, stop and uncertainty evidence.", "timing_test", "PROHIBITED", "SEPARATE QUALIFIED RELEASE REQUIRED"),
        ("SRS-006", "SF-01", "all powered phases", "With either K1 or K2 deliberately prevented from opening by an accepted fault-injection fixture, the remaining interruption path shall reach the same phase-specific rail and motion safe-state limits.", "fault_injection", "NOT EXECUTED", "EXACT DC CONTACT APPLICATION AND PHYSICAL TEST REQUIRED"),
        ("SRS-007", "SF-01", "all powered phases", "The accepted safe state shall include actuator-rail voltage below the received actuator's verified torque-capable threshold; that voltage threshold and dwell remain SELECTION REQUIRED.", "measurement", "SELECTION REQUIRED", "RECEIVED ACTUATOR AND RAIL-DECAY EVIDENCE REQUIRED"),
        ("SRS-008", "SF-03", "all phases", "E-stop release, safety-device recovery, controller reboot, heartbeat restoration and clearing a diagnostic fault shall not energize either contactor coil, enable actuator torque or command motion.", "fault_injection", "NOT EXECUTED", "PHYSICAL/HIL TRACE SET REQUIRED"),
        ("SRS-009", "SF-03", "all phases", "A restart sequence shall require cause removal, accepted K1/K2 feedback, one valid monitored falling-edge physical RESET, a later distinct physical ARM action and a fresh validated trajectory in that order.", "sequence_test", "NOT EXECUTED", "QUALIFIED SEQUENCE VALIDATION REQUIRED"),
        ("SRS-010", "SF-03", "all phases", "RESET and ARM shall be non-motion-producing actions; each shall leave torque authority false until all later sequence conditions are satisfied.", "sequence_test", "NOT EXECUTED", "HARDWARE AND SOFTWARE AUTHORITY TRACES REQUIRED"),
        ("SRS-011", "SF-03", "all phases", "A K1 or K2 mirror-contact discrepancy, invalid RESET waveform, early or held ARM input, stale trajectory or sequence-order error shall latch restart inhibition until the released recovery procedure is completed.", "fault_injection", "NOT EXECUTED", "FAULT MATRIX AND SIGNED DISPOSITION REQUIRED"),
        ("SRS-012", "DF-01", "HR-V0", "The ordinary heartbeat watchdog shall receive zero safety credit, and PG-01 containment shall be assessed with DF-01 stuck valid and otherwise failed to demand a stop.", "analysis_and_test", "CONTROLLED", "GUARD CONTAINMENT AND NONINTERFERENCE EVIDENCE REQUIRED"),
        ("SRS-013", "PG-01", "before actuator connection", "The fixed guard, passive receiver and bench restraint shall contain every permitted arm, object, stop, rebound and power-loss outcome with the phase-specific residual-travel envelope plus build, calibration and measurement uncertainty.", "inspection_and_test", "NOT EXECUTED", "RELEASED GUARD CAD, FAI, IMPACT/DROP AND QUALIFIED REVIEW REQUIRED"),
        ("SRS-014", "SF-01/SF-03", "qualified allocation", "Required PLr or SIL, architecture/category, MTTFd or B10d use, diagnostic coverage, common-cause measures, systematic measures, fault exclusions, demand assumptions and validation method shall be selected and signed by a qualified functional-safety reviewer.", "qualified_analysis", "SELECTION REQUIRED", "ANALYSIS-SAFE-001 REQUIRED"),
        ("SRS-015", "program boundary", "all phases", "No candidate numeric limit, manufacturer component time, ERC/DRC result, unit test or source review shall be treated as achieved stopping performance, functional-safety validation or permission to energize.", "audit", "CONTROLLED", "NO AUTHORITY GRANTED"),
    ]
    requirement_rows = [warned({
        "requirement_id": rid,
        "function_id": function_id,
        "phase_or_scope": phase,
        "requirement": statement,
        "verification_method": method,
        "current_state": state,
        "closure_evidence": evidence,
        "approval_state": "NOT APPROVED",
    }) for rid, function_id, phase, statement, method, state, evidence in requirements]
    write_csv("safety-function-requirements.csv", requirement_rows)

    timing = [
        ("SRS-TIM-001", "E4 J2 positive setup", "10.000", "2.000", "200.000", "CANDIDATE FIRST-MOTION LIMIT", "Physical statistical bound and qualified acceptance"),
        ("SRS-TIM-002", "future J2 positive automatic", "30.000", "2.000", "66.667", "PROHIBITED UNTIL SEPARATELY RELEASED", "Physical statistical bound, guard/stop closure and qualified acceptance"),
        ("SRS-TIM-003", "PNOZ s4 750104 E-stop de-energisation", "NOT APPLICABLE", "NOT APPLICABLE", "20.000", "PUBLISHED COMPONENT MAXIMUM ONLY", "Received-device timing and complete-function validation"),
        ("SRS-TIM-004", "LC1D25BD opening", "NOT APPLICABLE", "NOT APPLICABLE", "24.000", "PUBLISHED COMPONENT MAXIMUM ONLY", "Written DC application acceptance and received loaded timing"),
        ("SRS-TIM-005", "sequential component arithmetic screen", "10.000", "0.440", "44.000", "ARITHMETIC SCREEN ONLY", "Actual topology timing, rail decay, coast and uncertainty"),
        ("SRS-TIM-006", "setup residual allocation after component screen", "10.000", "1.560", "156.000", "UNPROVEN ALLOCATION", "Measured rail decay and mechanical coast within accepted uncertainty"),
        ("SRS-TIM-007", "automatic residual allocation after component screen", "30.000", "0.680", "22.667", "NOT RELEASED", "Separate architecture/timing decision; no automatic motion on this evidence"),
    ]
    timing_rows = [warned({
        "record_id": rid,
        "case": case,
        "speed_deg_s": speed,
        "travel_deg": travel,
        "time_ms": time_ms,
        "evidence_class": evidence_class,
        "remaining_evidence": remaining,
        "safety_credit": "NONE UNTIL QUALIFIED VALIDATION",
    }) for rid, case, speed, travel, time_ms, evidence_class, remaining in timing]
    write_csv("timing-budget.csv", timing_rows)

    scenarios = [
        ("SRS-VAL-001", "E-stop both channels during E4 setup motion", "SF-01", "K1 and K2 commanded open; rail and motion reach accepted limits; restart inhibited"),
        ("SRS-VAL-002", "E-stop channel 1 opens first", "SF-01", "Stop demand accepted; no channel-order dependence or restart"),
        ("SRS-VAL-003", "E-stop channel 2 opens first", "SF-01", "Stop demand accepted; no channel-order dependence or restart"),
        ("SRS-VAL-004", "K1 deliberately prevented from opening", "SF-01", "K2 alone reaches accepted safe state; discrepancy blocks restart"),
        ("SRS-VAL-005", "K2 deliberately prevented from opening", "SF-01", "K1 alone reaches accepted safe state; discrepancy blocks restart"),
        ("SRS-VAL-006", "E-stop released with RESET idle", "SF-03", "No coil, torque-enable or motion authority"),
        ("SRS-VAL-007", "RESET held while E-stop is released", "SF-03", "Monitored-start condition not accepted; no authority"),
        ("SRS-VAL-008", "Valid RESET falling edge without later ARM", "SF-03", "SAFE_READY may be indicated; contactor coils and torque remain inhibited"),
        ("SRS-VAL-009", "ARM held before valid RESET", "SF-03", "ARM rejected; sequence remains inhibited"),
        ("SRS-VAL-010", "Valid ARM after RESET but no fresh trajectory", "SF-03", "No stale torque or motion command resumes"),
        ("SRS-VAL-011", "Heartbeat restoration after diagnostic dropout", "DF-01/SF-03", "No bypass of RESET, ARM or fresh-trajectory requirements"),
        ("SRS-VAL-012", "Raspberry Pi or watchdog reboot", "DF-01/SF-03", "No coil, torque-enable or motion authority on recovery"),
        ("SRS-VAL-013", "K1 mirror-contact discrepancy", "SF-03", "Reset/ARM rejected and discrepancy latched"),
        ("SRS-VAL-014", "K2 mirror-contact discrepancy", "SF-03", "Reset/ARM rejected and discrepancy latched"),
        ("SRS-VAL-015", "24 V control brownout and recovery", "SF-01/SF-03", "Fail-closed dropout; recovery cannot command motion"),
        ("SRS-VAL-016", "DF-01 stuck valid", "DF-01/PG-01", "No safety credit; fixed guard and hard-stop containment remain effective"),
    ]
    scenario_rows = [warned({
        "test_id": test_id,
        "scenario": scenario,
        "function_id": function_id,
        "required_result": result,
        "repetitions": "SELECTION REQUIRED BY QUALIFIED VALIDATION PLAN",
        "measurement_thresholds": "SELECTION REQUIRED EXCEPT CONTROLLED SRS-TIM LIMITS",
        "execution_state": "NOT EXECUTED",
        "approval_state": "NOT APPROVED",
    }) for test_id, scenario, function_id, result in scenarios]
    write_csv("validation-matrix.csv", scenario_rows)

    ccf_items = [
        ("SRS-CCF-001", "shared 24 V control supply", "Loss, undervoltage, surge or common recovery affects both channels/final elements", "Power-fault analysis, brownout test, separation and protection evidence"),
        ("SRS-CCF-002", "common enclosure and contamination", "Conductive debris, moisture or damage bridges separated circuits", "Enclosure rating, spacing/routing inspection and contamination fault analysis"),
        ("SRS-CCF-003", "E-stop channel cable", "Cross-short or common mechanical damage defeats both channels", "Cable/routing selection, protected separation and injected-fault validation"),
        ("SRS-CCF-004", "RESET/ARM wiring", "Short or held input creates unintended start sequence", "Protected routing, monitored waveform and fault injection"),
        ("SRS-CCF-005", "K1/K2 coil control", "Shared driver, trace, supply or bridge commands both coils", "Physical PCB/harness review, driver-fault analysis and tests"),
        ("SRS-CCF-006", "K1/K2 power path", "Miswiring or conductor bridge bypasses series interruption", "Point-to-point inspection, isolation test and controlled fault injection"),
        ("SRS-CCF-007", "feedback/EDM path", "Welded or bridged mirror feedback masks final-element failure", "Exact contact classification, routing analysis and discrepancy tests"),
        ("SRS-CCF-008", "coil suppression", "Suppression or stored energy delays both contactors", "Exact suppression topology and loaded release-time measurement"),
        ("SRS-CCF-009", "actuator regeneration and rail storage", "Rail remains torque-capable after contacts open", "Loaded rail-decay/regeneration traces and discharge disposition"),
        ("SRS-CCF-010", "software and stale commands", "Common software recovers into a prior target", "Fresh-trajectory authority protocol and HIL/physical traces"),
        ("SRS-CCF-011", "mechanical hard-stop/guard dependence", "Tolerance, rebound or guard deformation defeats containment", "FAI, impact/drop, uncertainty and retained inspection evidence"),
        ("SRS-CCF-012", "maintenance/debug bypass", "Temporary jumper, service mode or test lead defeats a protective path", "Key control, inspection checklist, configuration audit and removal verification"),
    ]
    ccf_rows = [warned({
        "record_id": record_id,
        "common_cause": cause,
        "credible_effect": effect,
        "required_evidence": evidence,
        "current_disposition": "OPEN - NO EXCLUSION OR SAFETY CREDIT",
        "qualified_review_state": "NOT EXECUTED",
    }) for record_id, cause, effect, evidence in ccf_items]
    write_csv("common-cause-review-register.csv", ccf_rows)

    allocation_rows = []
    for function_id, hazard, initiator, logic, final_element, safe_state in [
        ("SF-01", "Emergency stop during hazardous arm motion", "IDEC XW dual-NC E-stop candidate", "SR1/SRA1 PNOZ s4 750104 candidates", "K1 and K2 series contactors", "Actuator rail below verified torque-capable threshold and motion stopped within phase limit"),
        ("SF-03", "Unexpected restart after safety or diagnostic dropout", "RESET, ARM, K1/K2 feedback and safety-relay state", "SR1/SRA1 PNOZ s4 candidates plus fail-closed authority protocol", "SRA1 outputs and K1/K2 coils", "Coils and torque authority remain inhibited until ordered restart conditions and fresh trajectory"),
    ]:
        allocation_rows.append(warned({
            "function_id": function_id,
            "hazard": hazard,
            "initiator": initiator,
            "logic": logic,
            "final_element": final_element,
            "safe_state": safe_state,
            "severity_input": "SELECTION REQUIRED",
            "frequency_exposure_input": "SELECTION REQUIRED",
            "avoidance_input": "SELECTION REQUIRED",
            "required_plr_or_sil": "SELECTION REQUIRED",
            "architecture_or_category": "SELECTION REQUIRED",
            "mttfd_or_b10d": "SELECTION REQUIRED",
            "diagnostic_coverage": "SELECTION REQUIRED",
            "ccf_score_and_measures": "SELECTION REQUIRED",
            "fault_exclusions": "NONE ACCEPTED",
            "reviewer": "SELECTION REQUIRED",
            "qualification_basis": "SELECTION REQUIRED",
            "independence_disposition": "SELECTION REQUIRED",
            "signature": "NOT EXECUTED",
            "approval_status": "NOT APPROVED",
        }))
    write_csv("qualified-allocation-inputs.csv", allocation_rows)

    sources = [
        ("SRS-SRC-01", "ISO", "ISO 12100:2010", "https://www.iso.org/standard/51528.html", "Edition 1; published 2010-11; current page rechecked 2026-08-11", "Risk-assessment and risk-reduction methodology scope only"),
        ("SRS-SRC-02", "ISO", "ISO 13849-1:2023", "https://www.iso.org/standard/73481.html", "Edition 4; published 2023-04; current page rechecked 2026-08-11", "SRP/CS design methodology; does not prescribe this project's PLr"),
        ("SRS-SRC-03", "ISO", "ISO 13849-2:2012", "https://www.iso.org/standard/53640.html", "Edition 2; published 2012-10; current page rechecked 2026-08-11", "Validation by analysis and testing; replacement draft remains under development"),
        ("SRS-SRC-04", "ISO", "ISO 13850:2015", "https://www.iso.org/standard/59970.html", "Edition 3; published 2015-11; current page rechecked 2026-08-11", "Emergency-stop functional requirements and design-principles scope"),
        ("SRS-SRC-05", "Pilz", "PNOZ s4 operating manual", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "21396-EN-23; PDF created 2026-06-17; product file dated 2026-06-22", "750104 maximum E-stop de-energisation delay 20 ms; falling-edge monitored-start maximum switch-on delay 70 ms"),
        ("SRS-SRC-06", "Schneider Electric", "LC1D25BD product data sheet", "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", "Product sheet dated 2017-09-13; live source rechecked 2026-08-11", "24 VDC coil candidate and 16-24 ms published opening-time component datum; application suitability remains open"),
    ]
    source_rows = [warned({
        "source_id": source_id,
        "organization": organization,
        "title": title,
        "url": url,
        "document_revision_or_date": revision,
        "access_date": DATE,
        "verified_claim_boundary": boundary,
        "project_acceptance_effect": "REFERENCE INPUT ONLY - NO PLR, APPLICATION OR SAFETY APPROVAL",
    }) for source_id, organization, title, url, revision, boundary in sources]
    write_csv("source-register.csv", source_rows)

    authority_rows = [
        ("internal SRS review and redline", "TRUE", "Read-only review; no physical action", "AVAILABLE"),
        ("qualified PLr/SIL allocation", "FALSE", "Named competent independent reviewer with controlled standards and signed analysis", "NOT EXECUTED"),
        ("component/application acceptance", "FALSE", "Exact hardware evidence and qualified electrical/safety disposition", "PROHIBITED"),
        ("fabrication, assembly or connection", "FALSE", "Separate released work package and accepted upstream gates", "PROHIBITED"),
        ("powered testing, motion or energization", "FALSE", "Separate signed phase authorization and executed prerequisites", "PROHIBITED"),
    ]
    authority = [warned({
        "activity": activity,
        "permitted_by_this_package": permitted,
        "condition": condition,
        "state": state,
    }) for activity, permitted, condition, state in authority_rows]
    write_csv("authority-boundary.csv", authority)

    setup_limit = Decimal("2.000") / Decimal("10.000") * Decimal("1000")
    auto_limit = Decimal("2.000") / Decimal("30.000") * Decimal("1000")
    component_screen = Decimal("20.000") + Decimal("24.000")
    status = {
        "schema": "project-button-hr-v0-safety-requirements-v1",
        "identifier": IDENTIFIER,
        "round": ROUND,
        "date": DATE,
        "program_scope": "HR-V0 adult-only fixed-guarded bench demonstrator",
        "requirement_records": len(requirement_rows),
        "timing_records": len(timing_rows),
        "validation_scenarios": len(scenario_rows),
        "common_cause_records": len(ccf_rows),
        "qualified_allocation_records": len(allocation_rows),
        "source_records": len(source_rows),
        "configuration_bindings": len(binding_rows),
        "setup_candidate_speed_deg_s": 10.0,
        "setup_candidate_residual_travel_deg": 2.0,
        "setup_candidate_total_response_ms": float(setup_limit),
        "automatic_candidate_total_response_ms": round(float(auto_limit), 3),
        "component_maximum_arithmetic_screen_ms": float(component_screen),
        "plr_or_sil_assigned": False,
        "architecture_or_category_approved": False,
        "physical_validation_executed": False,
        "functional_safety_approved": False,
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

    req_cards = "".join(
        f'''<article class="card" data-function="{html.escape(str(row['function_id']))}" data-state="{html.escape(str(row['current_state']))}">
          <div class="tag">{html.escape(str(row['requirement_id']))} - {html.escape(str(row['function_id']))}</div>
          <h3>{html.escape(str(row['phase_or_scope']))}</h3>
          <p>{html.escape(str(row['requirement']))}</p>
          <dl><dt>State</dt><dd>{html.escape(str(row['current_state']))}</dd><dt>Closure</dt><dd>{html.escape(str(row['closure_evidence']))}</dd></dl>
        </article>'''
        for row in requirement_rows
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 safety requirements P0.2</title><style>
:root{{--sky:#d9f2ff;--blue:#0b2f5b;--deep:#071d38;--gold:#f5bd24;--paper:#f7fbff;--line:#8fb8d6;--danger:#7b1f1f}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--deep);font:clamp(16px,1.05vw,18px)/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{background:linear-gradient(135deg,var(--sky),#fff 58%);border-bottom:5px solid var(--gold);padding:clamp(24px,5vw,68px)}}
.wrap{{max-width:1220px;margin:auto}}h1{{font-size:clamp(34px,6vw,72px);line-height:1.03;margin:.2em 0;color:var(--blue)}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}h3{{font-size:clamp(19px,2vw,24px);margin:.35rem 0}}
.warning{{background:#fff1f1;border:3px solid var(--danger);color:var(--danger);font-weight:800;padding:16px;border-radius:12px}}
main{{padding:clamp(22px,4vw,52px)}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:16px}}
.metric,.card{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #d5e7f2}}.metric strong{{display:block;font-size:clamp(25px,4vw,42px);color:var(--blue)}}
.filters{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}}button{{font:inherit;font-size:16px;font-weight:750;border:2px solid var(--blue);background:#fff;color:var(--blue);padding:10px 14px;border-radius:999px;cursor:pointer}}button.active{{background:var(--blue);color:#fff}}
.tag{{font-size:14px;font-weight:800;color:var(--blue);letter-spacing:.02em}}dl{{margin:.75rem 0 0}}dt{{font-size:14px;font-weight:800;color:var(--blue)}}dd{{margin:0 0 .7rem}}.small{{font-size:14px}}a{{color:var(--blue);font-weight:700}}footer{{padding:24px;border-top:2px solid var(--line)}}
@media(max-width:540px){{header,main{{padding:20px}}.card{{padding:16px}}button{{width:100%}}}}
</style></head><body><header><div class="wrap"><div class="tag">{IDENTIFIER} - {ROUND}</div><h1>Measurable limits, no invented approval.</h1><p>Candidate requirements for adult-only, fixed-guarded HR-V0 commissioning. The qualified allocation and every physical result remain open.</p><div class="warning">{WARNING}</div></div></header>
<main class="wrap"><section><h2>Controlled candidate boundary</h2><div class="metrics"><div class="metric"><strong>200 ms</strong>E4 J2-positive setup total-response candidate</div><div class="metric"><strong>2.000 deg</strong>candidate residual-travel ceiling</div><div class="metric"><strong>0</strong>PLr/SIL assignments or approvals</div><div class="metric"><strong>{len(scenario_rows)}</strong>unexecuted validation scenarios</div></div>
<p class="small">The 200 ms / 2.000 degree pair is a project design candidate for J2-positive setup motion at no more than 10 degrees per second. It is not achieved performance. Automatic motion remains prohibited on this evidence.</p></section>
<section><h2>Requirements</h2><div class="filters"><button class="active" data-filter="all">All</button><button data-filter="SF-01">SF-01 stop</button><button data-filter="SF-03">SF-03 restart</button><button data-filter="DF-01">DF-01 diagnostic</button><button data-filter="PG-01">PG-01 guard</button><button data-filter="open">Open/selection</button></div><div class="grid">{req_cards}</div></section>
<section><h2>What the package contains</h2><p>Machine-readable timing arithmetic, restart/fault scenarios, common-cause inputs, qualified-allocation blanks, primary-source provenance and a fail-closed authority boundary. See <a href="timing-budget.csv">timing budget</a>, <a href="validation-matrix.csv">validation matrix</a>, <a href="common-cause-review-register.csv">common-cause register</a>, <a href="qualified-allocation-inputs.csv">allocation inputs</a> and <a href="source-register.csv">sources</a>.</p></section></main>
<footer><div class="wrap small">Candidate engineering input only. A qualified functional-safety reviewer must determine PLr/SIL and validate the complete safety-related control system.</div></footer>
<script>const buttons=[...document.querySelectorAll('button[data-filter]')],cards=[...document.querySelectorAll('.card')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.classList.toggle('active',x===b));const f=b.dataset.filter;cards.forEach(c=>{{const open=/NOT EXECUTED|SELECTION REQUIRED|CANDIDATE LIMIT|PROHIBITED/.test(c.dataset.state);c.hidden=!(f==='all'||c.dataset.function.includes(f)||(f==='open'&&open));}});}}));</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    print(f"Wrote {IDENTIFIER}: {len(requirement_rows)} requirements, {len(scenario_rows)} unexecuted validation scenarios")
    print("No PLr/SIL assigned; no physical validation, motion, or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
