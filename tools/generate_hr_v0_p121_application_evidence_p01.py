#!/usr/bin/env python3
"""Generate the R235 P1.21 manufacturer-RFI and no-load evidence package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
REVIEW = ROOT / "electrical/reviews/hr-v0-p121-application-evidence-p0.1"
SAFETY = ROOT / "safety/hr-v0-p121-application-evidence-p0.1"
RELEASE = ROOT / "release/hr-v0/p121-application-evidence-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
IDENTIFIER = "HR-V0-P121-APP-EVID-P0.1"


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def write_text_lf(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def warned(rows: list[tuple[str, ...]], fields: tuple[str, ...]) -> list[dict[str, object]]:
    return [dict(zip(fields, row)) | {"warning": WARNING} for row in rows]


SOURCES = [
    ("SRC-001", "Pilz", "PNOZ s4 750104 product record", "live US product page rechecked 2026-08-11", "https://www.pilz.com/en-US/eshop/product/750104", "Exact order code, 24 V DC supply, 2.5 W consumption, manual list", "Product record does not accept the Project Button application"),
    ("SRC-002", "Pilz", "PNOZ s4 operating manual", "21396-EN-23; portal file dated 2026-06-22; rechecked 2026-08-11", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "A1/A2 supply, 0.5 A for 5 ms startup pulse, falling-edge monitored start, terminal functions", "Manual does not explicitly answer the proposed repeated A1-gating application"),
    ("SRC-003", "Pilz USA", "Technical support route", "live support page rechecked 2026-08-11", "https://www.pilz.com/en-US/support", "Official US route for a written application question", "No request has been submitted and no response exists"),
    ("SRC-004", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060 product PDF", "data management 2026-04-01; generated and rechecked 2026-08-11", "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf", "Two changeover contacts, 5 V/10 mA minimum load, 6 A limiting current, 15 A for 300 ms inrush, DC load data", "Catalog limits do not establish application endurance or safety credit"),
    ("SRC-005", "Phoenix Contact USA", "Technical Service contact", "live contact page rechecked 2026-08-11", "https://www.phoenixcontact.com/en-us/service-and-support/contact", "Official US route for relay application questions", "No request has been submitted and no response exists"),
    ("SRC-006", "Project Button", "P1.21 SRA1-supply watchdog candidate", "R234 clean commit 3ca10d24035f7736486a9d1de6b7c0de5d911c1e", "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate/", "Exact proposed terminals, nets, schedules, ERC and fault boundary", "P1.15 remains current; P1.21 is unaccepted"),
]


ROUTES = [
    ("ROUTE-001", "Pilz USA Technical Support", "email", "techsupport@pilzusa.com", "official support page", "NOT SENT", "Use a configuration-controlled email or support ticket and retain headers/ticket ID"),
    ("ROUTE-002", "Pilz USA Technical Support", "telephone", "+1 877 745-9872", "official support page", "NOT USED", "A call may clarify routing but cannot close evidence without a written follow-up"),
    ("ROUTE-003", "Pilz USA", "web form", "https://www.pilz.com/en-US/support", "official support page", "NOT SENT", "Record submission timestamp and generated ticket/reference"),
    ("ROUTE-004", "Phoenix Contact USA Technical Service", "email", "us-technicalservice@phoenixcontact.com", "official contact page", "NOT SENT", "Use a configuration-controlled email or support ticket and retain headers/ticket ID"),
    ("ROUTE-005", "Phoenix Contact USA Technical Service", "telephone", "+1 800 322-3225", "official contact page", "NOT USED", "A call may clarify routing but cannot close evidence without a written follow-up"),
    ("ROUTE-006", "Phoenix Contact USA", "web question route", "https://www.phoenixcontact.com/en-us/service-and-support/contact", "official contact page", "NOT SENT", "Record submission timestamp and generated ticket/reference"),
]


QUESTIONS = [
    ("PILZ-Q01", "Pilz", "PNOZ s4 750104", "Is deliberate removal and restoration of A1 supply by external ordinary relay contacts permitted as a non-safety diagnostic inhibit when the two safety input channels remain direct and independent? State every constraint and identify any intended-use limitation.", "This is the exact P1.21 architecture and cannot be inferred from the manual", "NOT SENT", "OPEN"),
    ("PILZ-Q02", "Pilz", "PNOZ s4 750104", "After A1 supply is removed, what voltage threshold and minimum off-time guarantee a complete internal reset for every supported temperature and tolerance condition?", "The brownout/off-time test grid needs manufacturer limits", "NOT SENT", "OPEN"),
    ("PILZ-Q03", "Pilz", "PNOZ s4 750104", "With falling-edge monitored start selected, can restoring A1 while both input channels and the feedback loop are healthy ever close a safety output without a new valid falling edge at S34? Include power interruption, brownout and chatter cases.", "Heartbeat restoration must not restore eligibility", "NOT SENT", "OPEN"),
    ("PILZ-Q04", "Pilz", "PNOZ s4 750104", "What A1 ramp-rate, residual-ripple, interruption, chatter, repetition-rate or minimum on-time limits apply to repeated supply gating?", "The catalog pulse data do not define dynamic supply cycling", "NOT SENT", "OPEN"),
    ("PILZ-Q05", "Pilz", "PNOZ s4 750104", "Does this A1-gating use change any permissible safety category, PL/SIL calculation, diagnostic-coverage assumption, proof-test requirement or certificate condition for the PNOZ s4? If it is outside intended use, identify a supported architecture or product.", "A qualified allocation cannot assume certification scope", "NOT SENT", "OPEN"),
    ("PILZ-Q06", "Pilz", "PNOZ s4 750104", "Specify required upstream branch protection, source characteristics, suppression and wiring constraints for an A1 circuit switched by dry contacts at 24 V DC.", "Protection and coordination remain unresolved", "NOT SENT", "OPEN"),
    ("PILZ-Q07", "Pilz", "PNOZ s4 750104", "Provide or identify an authoritative power-up/power-down state diagram and timing limits for A1, S12, S22, S34 and safety outputs 13-14/23-24/33-34.", "The physical procedure must record the correct state sequence", "NOT SENT", "OPEN"),
    ("PHX-Q01", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "Is one 11-14 NO contact suitable for repeatedly switching the A1 supply of Pilz PNOZ s4 750104 at 24 V DC, 2.5 W nominal and a published maximum 0.5 A/5 ms startup pulse? State the applicable load classification.", "Paper margins do not establish application suitability", "NOT SENT", "OPEN"),
    ("PHX-Q02", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "For that exact electronic load, what electrical endurance or B10/B10d information applies as a function of switching rate, total cycles, ambient temperature and mounting orientation?", "Mechanical life cannot substitute for electrical endurance", "NOT SENT", "OPEN"),
    ("PHX-Q03", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "Does the 5 V/10 mA minimum-load specification provide a contact-reliability basis for approximately 104 mA steady load after repeated 0.5 A inrush events, or is additional wetting/load conditioning required?", "Contact reliability over life remains open", "NOT SENT", "OPEN"),
    ("PHX-Q04", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "Specify required branch protection, suppression and coordination for this switching duty, including any constraint created by the module's integrated input suppression.", "Protection cannot be selected from current arithmetic alone", "NOT SENT", "OPEN"),
    ("PHX-Q05", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "Does using contacts from two separate modules in series to gate one PNOZ A1 circuit require any additional derating, minimum-current provision, spacing, common-supply or diagnostic consideration?", "P1.21 uses two series contacts", "NOT SENT", "OPEN"),
    ("PHX-Q06", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060", "Identify failure-mode, contact-weld/stick, proof-test or reliability data that may be used in a non-safety diagnostic FMEA, while explicitly assigning no safety credit to the relay modules.", "DF-01 common-cause and diagnostic evidence remain open", "NOT SENT", "OPEN"),
]


RESPONSE_ACCEPTANCE = [
    ("RA-001", "Traceable response", "Official manufacturer-domain email, signed letter or support ticket with immutable identifier", "SELECTION REQUIRED"),
    ("RA-002", "Responder authority", "Responder name, role and application-engineering authority recorded", "SELECTION REQUIRED"),
    ("RA-003", "Exact product identity", "Pilz 750104 and/or Phoenix 2967060 explicitly named", "SELECTION REQUIRED"),
    ("RA-004", "Exact topology", "Attached P1.21 terminal/net excerpt acknowledged as the reviewed circuit", "SELECTION REQUIRED"),
    ("RA-005", "Exact load envelope", "24 V DC, 2.5 W nominal, 0.5 A for 5 ms maximum startup pulse and proposed cycle profile addressed", "SELECTION REQUIRED"),
    ("RA-006", "Question coverage", "Every submitted question answered or explicitly declined; silence is not acceptance", "SELECTION REQUIRED"),
    ("RA-007", "Conditions and exclusions", "Temperature, supply, ramp, off-time, cycle, protection, wiring and lifecycle limits stated", "SELECTION REQUIRED"),
    ("RA-008", "Document control", "Referenced document number, revision and date captured", "SELECTION REQUIRED"),
    ("RA-009", "Permitted/prohibited disposition", "Written permitted, permitted-with-conditions or prohibited disposition recorded without inference", "SELECTION REQUIRED"),
    ("RA-010", "Conflict resolution", "Any conflict between Pilz and Phoenix responses is resolved in writing", "SELECTION REQUIRED"),
    ("RA-011", "Qualified review", "Qualified electrical and functional-safety reviewers accept the response for the exact configuration", "SELECTION REQUIRED"),
    ("RA-012", "Configuration archive", "Response, attachments, hashes, ticket metadata and disposition are included in a later accepted baseline", "SELECTION REQUIRED"),
]


PREREQUISITES = [
    ("AUTH-001", "P1.21 has independent terminal review and qualified electrical disposition", "OPEN", "No test authority"),
    ("AUTH-002", "Pilz and Phoenix written responses satisfy RA-001 through RA-012", "OPEN", "No test authority"),
    ("AUTH-003", "Exact received 750104 and two 2967060 articles pass identity and terminal inspection", "OPEN", "No test authority"),
    ("AUTH-004", "A no-load fixture drawing and point-to-point schedule are released and independently checked", "OPEN", "No test authority"),
    ("AUTH-005", "Actuator source, actuators and K1/K2 power poles are physically absent; low-energy contact-state sensing only", "OPEN", "No test authority"),
    ("AUTH-006", "Current-limited isolated 24 V source, protection and emergency isolation are selected and reviewed", "OPEN", "No test authority"),
    ("AUTH-007", "All instruments have in-date calibration and adequate bandwidth, isolation and ratings", "OPEN", "No test authority"),
    ("AUTH-008", "Manufacturer-derived numeric limits and test-point grid are entered; no field is left SELECTION REQUIRED", "OPEN", "No test authority"),
    ("AUTH-009", "Configuration-specific procedure is signed by test owner and qualified reviewers; stop-work conditions briefed", "OPEN", "No test authority"),
    ("AUTH-010", "Separate written E2 control-only work authorization identifies people, place, date, boundary and revision", "OPEN", "No test authority"),
]


SIGNALS = [
    ("SIG-001", "SAFETY_24V at source", "voltage and current", "SELECTION REQUIRED", "calibrated isolated voltage probe and current measurement"),
    ("SIG-002", "SRA1_A1_WD_GATED at SRA1:A1", "voltage", "SELECTION REQUIRED", "calibrated isolated voltage probe"),
    ("SIG-003", "SRA1:A2 / SAFETY_0V", "voltage and continuity", "SELECTION REQUIRED", "calibrated isolated voltage probe"),
    ("SIG-004", "SRA1:S12", "voltage/state", "SELECTION REQUIRED", "calibrated isolated voltage probe"),
    ("SIG-005", "SRA1:S22", "voltage/state", "SELECTION REQUIRED", "calibrated isolated voltage probe"),
    ("SIG-006", "SRA1:S34 monitored-start return", "voltage/state", "SELECTION REQUIRED", "calibrated isolated voltage probe"),
    ("SIG-007", "SRA1:13-14", "contact state", "MUST REMAIN OPEN unless a valid fresh ARM is applied", "approved low-energy isolated continuity channel"),
    ("SIG-008", "SRA1:23-24", "contact state", "MUST REMAIN OPEN unless a valid fresh ARM is applied", "approved low-energy isolated continuity channel"),
    ("SIG-009", "SRA1:33-34", "contact state", "MUST REMAIN OPEN unless a valid fresh ARM is applied", "approved low-energy isolated continuity channel"),
    ("SIG-010", "KWD1:11-14", "contact state and voltage", "SELECTION REQUIRED", "approved isolated state channel"),
    ("SIG-011", "KWD2:11-14", "contact state and voltage", "SELECTION REQUIRED", "approved isolated state channel"),
    ("SIG-012", "PI_HEARTBEAT stimulus", "edge timestamps and logic level", "SELECTION REQUIRED", "isolated pattern source/logger"),
    ("SIG-013", "S2 ARM stimulus", "make/break timestamps", "falling edge must be separately identifiable", "approved dry-contact fixture and logger"),
    ("SIG-014", "S0 E-stop channels", "both channel states and timestamps", "both channels recorded independently", "approved dual dry-contact fixture and logger"),
    ("SIG-015", "EDM simulator", "K1/K2 mirror-state simulation", "must be configuration controlled", "approved dry-contact fixture and logger"),
]


TESTS = [
    ("TEST-001", "Unpowered received identity, terminal map, fixture continuity and isolation inspection", "UNPOWERED", "No discrepancy; signed inspection evidence", "NOT EXECUTED"),
    ("TEST-002", "Initial current-limited 24 V application with SRA1 inputs open and no ARM", "CONTROL ONLY", "All SRA1 safety outputs remain open; no chatter; measured startup trace retained", "NOT EXECUTED"),
    ("TEST-003", "Both direct SRA1 inputs healthy and EDM healthy, but no ARM edge", "CONTROL ONLY", "All SRA1 safety outputs remain open", "NOT EXECUTED"),
    ("TEST-004", "Apply one valid manufacturer-compliant falling-edge ARM", "CONTROL ONLY", "Outputs may close only after the valid edge; measured timing checked against selected limit", "NOT EXECUTED"),
    ("TEST-005", "Interrupt heartbeat so both KWD contacts open", "CONTROL ONLY", "SRA1 A1 loses supply and every SRA1 safety output opens; dropout timing checked against selected limit", "NOT EXECUTED"),
    ("TEST-006", "Restore valid heartbeat after TEST-005 without a new ARM", "CONTROL ONLY", "SRA1 may repower but every safety output remains open indefinitely; any closure is FAIL", "NOT EXECUTED"),
    ("TEST-007", "After TEST-006, apply one new valid falling-edge ARM with EDM healthy", "CONTROL ONLY", "Outputs may close only after the new ARM; no earlier closure", "NOT EXECUTED"),
    ("TEST-008", "Demand E-stop with heartbeat valid and both KWD contacts closed", "CONTROL ONLY", "Direct SR1/SRA1 input path opens every safety output; timing checked against selected limit", "NOT EXECUTED"),
    ("TEST-009", "Simulate KWD1 11-14 welded closed; interrupt heartbeat so KWD2 opens", "FAULT INJECTION", "SRA1 A1 loses supply through KWD2; outputs open; no unsafe restart", "NOT EXECUTED"),
    ("TEST-010", "Simulate KWD2 11-14 welded closed; interrupt heartbeat so KWD1 opens", "FAULT INJECTION", "SRA1 A1 loses supply through KWD1; outputs open; no unsafe restart", "NOT EXECUTED"),
    ("TEST-011", "Bypass both KWD supply contacts to model DF-01 failed, then demand E-stop", "FAULT INJECTION", "SRA1 remains powered but direct input channels open every safety output; any interference is FAIL", "NOT EXECUTED"),
    ("TEST-012", "Hold KWD1 open with valid heartbeat", "FAULT INJECTION", "SRA1 remains unpowered and outputs open", "NOT EXECUTED"),
    ("TEST-013", "Hold KWD2 open with valid heartbeat", "FAULT INJECTION", "SRA1 remains unpowered and outputs open", "NOT EXECUTED"),
    ("TEST-014", "Abruptly remove and restore SAFETY_24V", "CONTROL ONLY", "Removal opens outputs; restoration alone never closes an output", "NOT EXECUTED"),
    ("TEST-015", "Open and restore SAFETY_0V with approved fixture", "FAULT INJECTION", "No output remains or becomes closed; restoration alone never closes an output", "NOT EXECUTED"),
    ("TEST-016", "Ramp SRA1 A1 downward through manufacturer-approved voltage/time points", "BROWNOUT", "No output chatter; transition and recovery comply with selected manufacturer limits", "NOT EXECUTED"),
    ("TEST-017", "Ramp SRA1 A1 upward through manufacturer-approved voltage/time points without ARM", "BROWNOUT", "No safety output closes; no chatter; selected limits met", "NOT EXECUTED"),
    ("TEST-018", "Apply manufacturer-approved off-time, contact-bounce and asynchronous KWD-opening matrix", "BROWNOUT/FAULT", "No chatter or closure without fresh ARM; every measured limit passes", "NOT EXECUTED"),
]


HOLDS = [
    ("APP-H01", "Pilz written response accepted under RA-001 through RA-012"),
    ("APP-H02", "Phoenix Contact written response accepted under RA-001 through RA-012"),
    ("APP-H03", "Mission cycle profile and electrical endurance target selected"),
    ("APP-H04", "A1 off-time, ramp, brownout, ripple and repetition limits selected from manufacturer evidence"),
    ("APP-H05", "Gate-branch conductor, protection and fault-current coordination released"),
    ("APP-H06", "Received component identities and terminal maps verified"),
    ("APP-H07", "Low-energy no-load fixture ECAD, BOM, wiring and protection released"),
    ("APP-H08", "Instrumentation range, bandwidth, isolation and calibration accepted"),
    ("APP-H09", "Protected routing/common-cause drawing released"),
    ("APP-H10", "All eighteen configuration-bound tests executed and reviewed"),
    ("APP-H11", "P1.21 independent electrical review accepted"),
    ("APP-H12", "PLr/SIL/category/CCF/DC/reliability allocation and validation accepted"),
    ("APP-H13", "P1.21 formally promoted through configuration control"),
    ("APP-H14", "Separate signed work authorization issued for each later powered stage"),
]


def page() -> str:
    qrows = "".join(
        f"<tr data-maker='{html.escape(maker)}'><td><strong>{qid}</strong></td><td>{html.escape(maker)}</td><td>{html.escape(question)}</td><td>{state}</td></tr>"
        for qid, maker, _part, question, _reason, _sent, state in QUESTIONS
    )
    trows = "".join(
        f"<tr data-mode='{html.escape(mode)}'><td><strong>{tid}</strong></td><td>{html.escape(mode)}</td><td>{html.escape(stimulus)}</td><td>{html.escape(acceptance)}</td><td>{state}</td></tr>"
        for tid, stimulus, mode, acceptance, state in TESTS
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 application evidence</title><style>
:root{{--sky:#78cef2;--navy:#082b4c;--blue:#155d91;--gold:#f3b61f;--paper:#f5fbff;--line:#94b8ce}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.3rem);line-height:1.05;max-width:18ch;margin:.35rem 0 1rem}}h2{{font-size:clamp(1.45rem,2.3vw,2.15rem)}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #a87500;background:#fff3c4;border-radius:.8rem;font-weight:700}}.lead{{font-size:clamp(1.15rem,1.8vw,1.5rem);max-width:74rem}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}.card{{border:3px solid var(--blue);border-radius:.8rem;padding:1rem;background:var(--paper)}}.card strong{{display:block;font-size:clamp(1.6rem,3vw,2.5rem)}}button{{font:inherit;font-weight:700;color:var(--navy);background:#fff;border:3px solid var(--blue);border-radius:.55rem;padding:.65rem .9rem;margin:.2rem}}button[aria-pressed=true]{{background:var(--gold)}}.table{{overflow:auto;border:2px solid var(--line);border-radius:.7rem;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:980px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b7ccd8}}th{{background:var(--navy);color:#fff;position:sticky;top:0}}[hidden]{{display:none!important}}
</style></head><body><header><strong>{IDENTIFIER} / R235</strong><h1>Ask first. Test later. Never infer acceptance.</h1><div class="warning">{WARNING}</div></header><main><p class="lead">This package turns the P1.21 manufacturer and physical-test holds into exact, unsent questions and an unexecuted no-load procedure. It does not send a message, select a limit, authorize a connection, or close a safety finding.</p><div class="cards"><div class="card"><strong>{len(QUESTIONS)}</strong>unsent manufacturer questions</div><div class="card"><strong>{len(RESPONSE_ACCEPTANCE)}</strong>response-acceptance controls</div><div class="card"><strong>{len(TESTS)}</strong>unexecuted test cases</div><div class="card"><strong>{len(HOLDS)}</strong>open holds</div></div><h2>Manufacturer questions</h2><div><button data-group="maker" data-filter="ALL" aria-pressed="true">All {len(QUESTIONS)}</button><button data-group="maker" data-filter="Pilz">Pilz</button><button data-group="maker" data-filter="Phoenix Contact">Phoenix Contact</button></div><div class="table"><table><thead><tr><th>ID</th><th>Addressee</th><th>Exact question</th><th>Response</th></tr></thead><tbody id="questions">{qrows}</tbody></table></div><h2>No-load test matrix</h2><div><button data-group="mode" data-filter="ALL" aria-pressed="true">All {len(TESTS)}</button><button data-group="mode" data-filter="CONTROL ONLY">Control only</button><button data-group="mode" data-filter="FAULT INJECTION">Fault injection</button><button data-group="mode" data-filter="BROWNOUT">Brownout</button></div><div class="table"><table><thead><tr><th>ID</th><th>Mode</th><th>Stimulus</th><th>Acceptance boundary</th><th>State</th></tr></thead><tbody id="tests">{trows}</tbody></table></div><h2>Release boundary</h2><p>P1.15 remains current. P1.21 is unaccepted. Every manufacturer route is unsent, every test is unexecuted, every numeric dynamic limit remains selection-controlled, and DF-01 receives zero safety credit. A later response or test result must still pass qualified review and formal configuration control.</p></main><script>
const groups={{maker:[...document.querySelectorAll('#questions tr')],mode:[...document.querySelectorAll('#tests tr')]}};document.querySelectorAll('button[data-group]').forEach(b=>b.addEventListener('click',()=>{{const g=b.dataset.group;document.querySelectorAll(`button[data-group="${{g}}"]`).forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');const f=b.dataset.filter;groups[g].forEach(r=>r.hidden=f!=='ALL'&&r.dataset[g]!==f)}}));
</script></body></html>'''


def procedure() -> str:
    return f"""# HR-V0 P1.21 no-load A1-gating test procedure P0.1

> **{WARNING}**

Identifier: `{IDENTIFIER}`

Execution state: **NOT EXECUTED - NOT AUTHORIZED**

This procedure is a controlled future-test definition. It shall not be executed until every `AUTH-001` through `AUTH-010` prerequisite is independently verified and a separate written E2 control-only work authorization is issued for the exact configuration.

## Hard boundary

- The actuator source, actuators and main power path shall be physically absent.
- SRA1 output contacts shall be observed only with an approved isolated low-energy continuity fixture.
- K1/K2 power poles shall not switch a load. EDM may be represented only by an approved dry-contact simulator.
- No mains source, installed robot actuator rail, motion, payload or person may be introduced.
- Any unexpected output closure, relay chatter, odor, heat, smoke, unstable trace, instrument overrange, fixture discrepancy or loss of isolation requires immediate source removal, quarantine and nonconformance entry.

## Required order

1. Freeze the exact Git commit, P1.21 native KiCad hash, fixture ECAD/BOM/wiring hashes, firmware hash and received serial/lot identities.
2. Complete and sign all authorization-prerequisite rows.
3. Enter manufacturer-derived numeric limits and approved test points. `SELECTION REQUIRED` is not an executable value.
4. Complete TEST-001 unpowered. Stop on any discrepancy.
5. Apply only the separately authorized current-limited 24 V control source.
6. Execute TEST-002 through TEST-018 in order unless the signed test owner issues a controlled deviation.
7. Capture every required signal on a common time base and preserve raw files before analysis.
8. Mark a test PASS only when every qualitative condition and every selected numerical limit passes. Ambiguous, missing or clipped data are FAIL, not PASS.
9. Remove power, verify zero energy, archive evidence and obtain independent review.

Passing this procedure would provide configuration-specific evidence only. It would not establish functional-safety approval, loaded interruption, stopping distance, guard containment, actuator motion authority or general energization permission.
"""


def cover_note() -> str:
    return f"""# Unsent manufacturer application inquiry

> **{WARNING}**

Subject: Project Button HR-V0 - application questions for PNOZ s4 750104 and PLC-RSC-24DC/21-21 2967060

This draft is **NOT SENT**. It is intended for separate submissions to Pilz and Phoenix Contact through the official routes in `submission-route-register.csv`.

Project Button is evaluating an unaccepted 24 V DC control-only topology. Two ordinary Phoenix Contact relay NO contacts, one from each of two separate 2967060 modules, would be placed in series between a protected 24 V control source and terminal A1 of one Pilz PNOZ s4 750104. The PNOZ A2 terminal returns directly to control 0 V. The PNOZ input and monitored-start circuits are separate from these ordinary relay contacts. The ordinary relays receive zero safety credit.

Pilz publishes 2.5 W nominal consumption and a maximum 0.5 A for 5 ms A1 startup pulse for 750104. Phoenix Contact publishes a 5 V/10 mA minimum load and 15 A for 300 ms maximum inrush for 2967060. We are not treating those figures as application acceptance.

Please answer the applicable rows in `manufacturer-question-register.csv`, identify the exact document revision/date supporting each answer, and state whether the proposed use is permitted, permitted with conditions, or prohibited. Please do not infer or certify the safety of the complete robot; we are seeking component-application limits only.

Attachments before any submission must include a configuration-controlled P1.21 circuit excerpt, terminal schedule, proposed cycle profile, supply/protection envelope and this package identifier. The cycle profile, protection and several dynamic limits are currently unresolved, so the inquiry shall not be represented as complete until those fields are filled.
"""


def main() -> None:
    for directory in (REVIEW, SAFETY, RELEASE):
        directory.mkdir(parents=True, exist_ok=True)

    datasets: dict[str, tuple[tuple[str, ...], list[dict[str, object]]]] = {
        "source-register.csv": (("source_id", "owner", "document", "revision_or_date", "url_or_path", "use", "limitation", "warning"), warned(SOURCES, ("source_id", "owner", "document", "revision_or_date", "url_or_path", "use", "limitation"))),
        "submission-route-register.csv": (("route_id", "addressee", "channel", "destination", "source", "state", "record_control", "warning"), warned(ROUTES, ("route_id", "addressee", "channel", "destination", "source", "state", "record_control"))),
        "manufacturer-question-register.csv": (("question_id", "addressee", "part", "question", "reason", "sent", "response_state", "warning"), warned(QUESTIONS, ("question_id", "addressee", "part", "question", "reason", "sent", "response_state"))),
        "response-acceptance-register.csv": (("control_id", "subject", "minimum_evidence", "state", "warning"), warned(RESPONSE_ACCEPTANCE, ("control_id", "subject", "minimum_evidence", "state"))),
        "authorization-prerequisites.csv": (("prerequisite_id", "required_evidence", "state", "effect", "warning"), warned(PREREQUISITES, ("prerequisite_id", "required_evidence", "state", "effect"))),
        "signal-capture-register.csv": (("signal_id", "node_or_event", "measurement", "acceptance_boundary", "method", "warning"), warned(SIGNALS, ("signal_id", "node_or_event", "measurement", "acceptance_boundary", "method"))),
        "test-case-register.csv": (("test_id", "stimulus", "mode", "minimum_acceptance", "execution_state", "warning"), warned(TESTS, ("test_id", "stimulus", "mode", "minimum_acceptance", "execution_state"))),
        "open-holds.csv": (("hold_id", "closure_evidence", "state", "warning"), [dict(hold_id=i, closure_evidence=e, state="OPEN", warning=WARNING) for i, e in HOLDS]),
    }

    response_rows = [
        {"question_id": qid, "ticket_or_message_id": "", "response_date": "", "responder": "", "response_document": "", "response_sha256": "", "disposition": "OPEN", "qualified_review": "NOT REVIEWED", "warning": WARNING}
        for qid, *_ in QUESTIONS
    ]
    result_rows = [
        {"test_id": tid, "configuration_commit": "", "fixture_id": "", "raw_evidence_uri": "", "measured_result": "", "selected_limit": "SELECTION REQUIRED", "result": "NOT EXECUTED", "executor": "", "reviewer": "", "timestamp": "", "warning": WARNING}
        for tid, *_ in TESTS
    ]
    datasets["manufacturer-response-template.csv"] = (("question_id", "ticket_or_message_id", "response_date", "responder", "response_document", "response_sha256", "disposition", "qualified_review", "warning"), response_rows)
    datasets["test-result-template.csv"] = (("test_id", "configuration_commit", "fixture_id", "raw_evidence_uri", "measured_result", "selected_limit", "result", "executor", "reviewer", "timestamp", "warning"), result_rows)

    status = {
        "identifier": IDENTIFIER,
        "round": "R235",
        "configuration": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
        "current_electrical": "V3-P1.15-CARRIER-CANDIDATE",
        "manufacturer_questions": len(QUESTIONS),
        "submission_routes": len(ROUTES),
        "response_acceptance_controls": len(RESPONSE_ACCEPTANCE),
        "authorization_prerequisites": len(PREREQUISITES),
        "signals": len(SIGNALS),
        "test_cases": len(TESTS),
        "open_holds": len(HOLDS),
        "messages_sent": 0,
        "manufacturer_responses": 0,
        "tests_executed": 0,
        "tests_passed": 0,
        "p121_accepted": False,
        "watchdog_safety_credit": "NONE",
        "powered_test_authority": False,
        "energization_authority": False,
        "warning": WARNING,
    }

    readme = f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR235 converts P1.21 application holds into {len(QUESTIONS)} exact unsent manufacturer questions, {len(RESPONSE_ACCEPTANCE)} response controls, {len(TESTS)} unexecuted no-load tests and {len(HOLDS)} open holds. It sends nothing, selects no unresolved dynamic limit, executes no test and grants no authority. P1.15 remains current; P1.21 remains unaccepted.\n"
    for directory in (REVIEW, SAFETY, RELEASE):
        for name, (fields, rows) in datasets.items():
            write_csv(directory / name, fields, rows)
        write_text_lf(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
        write_text_lf(directory / "README.md", readme)
        write_text_lf(directory / "test-procedure.md", procedure())
        write_text_lf(directory / "submission-cover-note.md", cover_note())
    write_text_lf(RELEASE / "index.html", page())

    manifest = []
    for path in sorted(p for p in RELEASE.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        data = path.read_bytes()
        manifest.append({"file": path.name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "warning": WARNING})
    write_csv(RELEASE / "file-manifest.csv", ("file", "size_bytes", "sha256", "warning"), manifest)
    print(f"Wrote {IDENTIFIER}: {len(QUESTIONS)} questions, {len(TESTS)} tests, {len(HOLDS)} holds")
    print(WARNING)


if __name__ == "__main__":
    main()
