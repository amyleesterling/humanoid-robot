#!/usr/bin/env python3
"""Generate the R233 P1.20 PNOZ/KWD source-application dossier."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P120 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"
SAFETY = ROOT / "safety" / "hr-v0-pnoz-kwd-application-p0.2"
RELEASE = ROOT / "release" / "hr-v0" / "pnoz-kwd-application-p0.2"
IDENTIFIER = "HR-V0-PNOZ-KWD-APP-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sources() -> list[dict[str, object]]:
    manual = ROOT / "electrical" / "vendor" / "pilz" / "pnoz-s4-750104-r116" / "PNOZ_s4_21396-EN-23.pdf"
    return [
        {
            "source_id": "APP-SRC-001", "manufacturer": "Pilz", "product": "PNOZ s4, order 750104",
            "document": "Operating Manual 21396-EN-23", "revision_date": "21396-EN-23; portal dated 2026-06-22; rechecked 2026-08-11",
            "official_url": "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf",
            "controlled_file": str(manual.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(manual.read_bytes()).hexdigest().upper(),
            "verified_use": "750104 terminal behavior; dual-channel short detection; monitored falling-edge start; 24 VDC/50 mA input, start and feedback circuits; 0.2 A for 100 ms maximum input inrush; timing and installation constraints",
            "boundary": "Manufacturer data is not Project Button application approval and does not establish achieved PL, SIL, Category or stopping performance.", "warning": WARNING,
        },
        {
            "source_id": "APP-SRC-002", "manufacturer": "Phoenix Contact", "product": "PLC-RSC-24DC/21-21, item 2967060",
            "document": "Official product record and manufacturer-generated product PDF", "revision_date": "data maintenance 2026-04-01; rechecked 2026-08-11",
            "official_url": "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060",
            "controlled_file": "NOT ARCHIVED - CURRENT OFFICIAL WEB RECORD",
            "sha256": "SELECTION REQUIRED",
            "verified_use": "24 VDC coil; two AgNi changeover contacts; 5 V/10 mA minimum switching load; 6 A continuous; 15 A for 300 ms inrush; 2 A at 24 V DC13; typical 8 ms pickup and 10 ms release",
            "boundary": "No force-guided-contact or safety-relay claim was found. KWD1/KWD2 receive zero safety credit; typical timing is not an acceptance limit.", "warning": WARNING,
        },
    ]


PATH_KEYS = [
    ("02_estop_eligibility.kicad_sch", "SR1", terminal) for terminal in ("A1", "A2", "13", "14", "23", "24")
] + [
    ("03_arm_watchdog_eligibility.kicad_sch", "SRA1", terminal) for terminal in ("A1", "A2", "S11", "S12", "S21", "S22", "S34", "13", "14", "23", "24")
] + [
    ("03_arm_watchdog_eligibility.kicad_sch", ref, terminal)
    for ref, terminals in (("KWD1", ("A1", "A2", "11", "14")), ("KWD2", ("A1", "A2", "11", "14")), ("S2", ("TBD-A1", "TBD-A2")))
    for terminal in terminals
] + [
    ("04_contactor_edm.kicad_sch", ref, terminal)
    for ref, terminals in (("K1", ("21", "22")), ("K2", ("21", "22")))
    for terminal in terminals
]


def terminal_paths() -> list[dict[str, object]]:
    schedule = {(r["sheet"], r["reference"], r["terminal"]): r for r in read_csv(P120 / "connector-schedule.csv")}
    missing = [key for key in PATH_KEYS if key not in schedule]
    if missing:
        raise RuntimeError(f"P1.20 terminal path missing: {missing}")
    rows = []
    for sequence, key in enumerate(PATH_KEYS, 1):
        source = schedule[key]
        rows.append({
            "sequence": sequence, "sheet": key[0], "reference": key[1], "terminal": key[2],
            "pin_name": source["pin_name"], "net": source["net"], "source_status": source["status"],
            "application_state": "SOURCE PARITY CONFIRMED / PHYSICAL PATH UNVERIFIED",
            "safety_credit": "NONE", "warning": WARNING,
        })
    return rows


def compatibility() -> list[dict[str, object]]:
    rows = [
        ("APP-001", "PNOZ input/start/feedback nominal voltage", "24", "VDC", "Pilz 21396-EN-23", "SOURCE VERIFIED", "Measure on received installed hardware."),
        ("APP-002", "PNOZ input/start/feedback current", "50", "mA", "Pilz 21396-EN-23", "SOURCE VERIFIED", "Measure S11/S21 path current and voltage with exact route and contacts."),
        ("APP-003", "PNOZ maximum input-circuit inrush", "0.2 for 100", "A / ms", "Pilz 21396-EN-23", "SOURCE VERIFIED", "Published maximum input inrush is an application screen, not an installed trace."),
        ("APP-004", "Phoenix minimum switching load", "5 V at 10", "V / mA", "Phoenix 2967060 record", "SOURCE VERIFIED", "Environmental contamination and life at actual load remain unverified."),
        ("APP-005", "Voltage wetting screen", "4.8", "ratio", "24 V / 5 V", "PAPER SCREEN PASS", "Does not prove contact reliability or safety performance."),
        ("APP-006", "Steady-current wetting screen", "5.0", "ratio", "50 mA / 10 mA", "PAPER SCREEN PASS", "Does not prove contact reliability or safety performance."),
        ("APP-007", "Phoenix maximum inrush switching envelope", "15 for 300", "A / ms", "Phoenix 2967060 record", "SOURCE VERIFIED", "Contact voltage and category must match the received application."),
        ("APP-008", "Input-inrush current margin screen", "75", "ratio", "15 A / 0.2 A", "PAPER SCREEN PASS", "Duration screen is 100 ms within 300 ms; not a life or safety validation."),
        ("APP-009", "Phoenix 24 VDC DC13 current envelope", "2", "A", "Phoenix 2967060 record", "SOURCE VERIFIED", "PNOZ input load is not proven to be a DC13 utilization case."),
        ("APP-010", "DC13-to-input-inrush current screen", "10", "ratio", "2 A / 0.2 A", "PAPER SCREEN PASS", "Secondary conservative comparison only; exact utilization category remains to be reviewed."),
        ("APP-011", "Mixed timing screen", "30", "ms", "Phoenix release typical 10 ms + Pilz E-stop dropout maximum 20 ms", "NOT AN ACCEPTANCE BOUND", "Typical plus maximum data cannot define worst-case response; rail and torque decay remain unknown."),
        ("APP-012", "P1.20 short-detection cable-resistance ceiling", "30", "ohm", "Pilz dual-channel short-detection table", "SOURCE VERIFIED / UNALLOCATED", "Route length, conductor, terminal/contact resistance and measurement method remain selection required."),
    ]
    return [{"screen_id": i, "parameter": p, "value": v, "unit": u, "basis": b, "disposition": d, "remaining_evidence": e, "safety_credit": "NONE", "warning": WARNING} for i, p, v, u, b, d, e in rows]


def faults() -> list[dict[str, object]]:
    data = [
        ("AF-001", "KWD1 11-14 welded; heartbeat removed", "KWD2 opens SRA1 channel 2; SRA1 expected OFF", "SOURCE TOPOLOGY ADDRESSES SINGLE FAULT", "physical injection and asynchronous-input behavior"),
        ("AF-002", "KWD2 11-14 welded; heartbeat removed", "KWD1 opens SRA1 channel 1; SRA1 expected OFF", "SOURCE TOPOLOGY ADDRESSES SINGLE FAULT", "physical injection and asynchronous-input behavior"),
        ("AF-003", "Both KWD contacts welded/bypassed", "Both SRA1 returns can remain complete", "HAZARDOUS / OPEN", "dependent-failure and common-cause control"),
        ("AF-004", "Shared controller or driver keeps both KWD coils energized", "Both SRA1 returns can remain complete", "HAZARDOUS / OPEN", "independent architecture or justified safety allocation"),
        ("AF-005", "One channel conductor shorted around KWD", "Other channel opening is expected to remove eligibility", "SOURCE TOPOLOGY ADDRESSES SINGLE FAULT", "protected routing and cross-short test"),
        ("AF-006", "Both channel conductors bypassed by common route damage", "Both SRA1 returns can remain complete", "HAZARDOUS / OPEN", "separation, protection and credible-fault disposition"),
        ("AF-007", "One KWD contact bounces or opens earlier", "SRA1 should drop or enter a fault/non-start state", "APPLICATION TEST REQUIRED", "received-hardware timing trace and Pilz fault-recovery proof"),
        ("AF-008", "Heartbeat returns without a fresh monitored ARM event", "SRA1, K1 and K2 must remain OFF", "APPLICATION TEST REQUIRED", "executed restart-prevention trace"),
        ("AF-009", "Start or feedback-loop cross-short", "Pilz manual says these cross-shorts are not detected", "HAZARDOUS / OPEN", "protected/separate installation and inspection"),
        ("AF-010", "KWD coil suppression or driver fails short/open", "Effect depends on exact driver, suppression, PCB and relay failure", "APPLICATION/FMEA OPEN", "complete circuit, component failure modes and physical injection"),
    ]
    return [{"case_id": i, "fault": f, "modeled_response": r, "disposition": d, "closure_evidence": e, "safety_credit": "NONE", "warning": WARNING} for i, f, r, d, e in data]


def questions() -> list[dict[str, object]]:
    data = [
        ("Q-001", "PNOZ selector", "Confirm lower-row third selector position: short-detection plus monitored falling-edge; set unpowered, seal and inspect."),
        ("Q-002", "PNOZ input behavior", "Confirm external ordinary series contacts are acceptable on S12/S22 with the proposed two-stage architecture."),
        ("Q-003", "PNOZ fault recovery", "Define response/recovery for short, cross-short, bounce and asynchronous S12/S22 interruption."),
        ("Q-004", "KWD contact reliability", "Establish received minimum-load behavior, contamination class, endurance and inspection/replacement interval at actual input load."),
        ("Q-005", "KWD timing", "Obtain guaranteed or measured pickup/release/bounce distributions; typical catalog values are insufficient."),
        ("Q-006", "Common cause", "Analyze shared MCU, clock, supply, PCB, driver, connector, harness and environmental dependencies."),
        ("Q-007", "Physical routing", "Release separated/protected channel routes and terminal allocations; document short/cross-short assumptions."),
        ("Q-008", "Functional-safety allocation", "Qualified reviewer to assign PLr/SIL/Category and validate MTTFd/DC/CCF or IEC 62061 evidence."),
        ("Q-009", "Physical response", "Measure SRA1, K1/K2, actuator rail, torque and stopping response under authorized fault injection."),
        ("Q-010", "Configuration", "Independently review and formally promote or reject P1.20; P1.15 remains current."),
    ]
    return [{"question_id": i, "topic": t, "required_evidence": e, "state": "SELECTION REQUIRED", "owner": "QUALIFIED REVIEWER / PROJECT AUTHORITY", "warning": WARNING} for i, t, e in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("APP-H01", "Independent topology/application review", "Independent terminal-by-terminal and application disposition of P1.20."),
        ("APP-H02", "Received identity and configuration", "Received 750104 and 2967060 identity, terminal mapping, selector setting and inspection evidence."),
        ("APP-H03", "Measured electrical application", "Measured S11/S21 voltage, steady/inrush current, contact drop and cable-loop resistance."),
        ("APP-H04", "Common cause/dependent failure", "Accepted controller/driver/supply/PCB/harness/environment analysis with no unsupported exclusion."),
        ("APP-H05", "Protected routing", "Released separated routes and inspection records for input, start and feedback paths."),
        ("APP-H06", "Manual re-arm and fault recovery", "Executed trace showing restoration alone cannot re-energize and defining all PNOZ recovery states."),
        ("APP-H07", "Fault/stopping validation", "Authorized calibrated single/dual fault injection plus rail, torque and stop traces."),
        ("APP-H08", "Functional-safety validation", "Qualified PLr/SIL allocation, calculation, validation report and signatures."),
        ("APP-H09", "Configuration promotion/work authority", "Formal P1.20 disposition and separate signed work authorization; neither exists."),
    ]
    return [{"hold_id": i, "subject": s, "state": "OPEN", "closure_evidence": e, "warning": WARNING} for i, s, e in data]


def b005() -> list[dict[str, object]]:
    return [{
        "finding": "Sol R12 B-005", "reviewed_baseline_state": "OPEN_BLOCKER",
        "r232_source_change": "Two ordinary contacts now interrupt separate SRA1 input returns; either single contact weld is defeated in the modeled topology.",
        "r233_application_screen": "24 V/50 mA PNOZ load is above Phoenix 5 V/10 mA minimum and below published inrush/DC envelopes.",
        "current_disposition": "PARTIALLY_ADDRESSED_OPEN",
        "still_open": "dual/common-cause and route bypass; non-force-guided contacts; exact configuration; physical fault response; PLr/SIL allocation; qualified review",
        "qualified_closure": "NO", "safety_credit": "NONE", "work_authority": "NO", "warning": WARNING,
    }]


def page(compat: list[dict[str, object]], fault_rows: list[dict[str, object]]) -> str:
    comp = "".join(f"<tr><td>{html.escape(str(r['screen_id']))}</td><td>{html.escape(str(r['parameter']))}</td><td><strong>{html.escape(str(r['value']))} {html.escape(str(r['unit']))}</strong></td><td>{html.escape(str(r['disposition']))}</td><td>{html.escape(str(r['remaining_evidence']))}</td></tr>" for r in compat)
    faults_html = "".join(f"<tr data-state='{html.escape(str(r['disposition']))}'><td>{html.escape(str(r['case_id']))}</td><td>{html.escape(str(r['fault']))}</td><td>{html.escape(str(r['modeled_response']))}</td><td><strong>{html.escape(str(r['disposition']))}</strong></td><td>{html.escape(str(r['closure_evidence']))}</td></tr>" for r in fault_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNOZ/KWD application screen</title><style>
:root{{--sky:#8bd7f7;--navy:#082f55;--blue:#145f98;--gold:#f1b827;--paper:#f6fbff;--warn:#fff2bd}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(1.5rem,5vw,4.5rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:8px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5.5vw,5rem);line-height:1.03;max-width:18ch;margin:.35rem 0 1rem}}h2{{font-size:clamp(1.5rem,2.5vw,2.25rem)}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{font-weight:800;padding:1rem;border:3px solid #9a6900;background:var(--warn);border-radius:.8rem}}.lead{{font-size:clamp(1.15rem,1.8vw,1.55rem);max-width:75rem}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem}}.metric{{border:3px solid var(--blue);border-radius:.8rem;padding:1rem;background:var(--paper)}}.metric strong{{display:block;font-size:clamp(1.7rem,3vw,2.8rem)}}.table{{overflow:auto;border:2px solid #9cbacb;border-radius:.8rem;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:1050px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bed0da}}th{{background:var(--navy);color:white;position:sticky;top:0}}code{{font-size:14px}}@media(max-width:650px){{main{{padding:1.2rem .8rem}}}}
</style></head><body><header><strong>{IDENTIFIER} / R233</strong><h1>Contact compatibility is plausible. Safety closure is not.</h1><div class="warning">{WARNING}</div></header><main><p class="lead">The selected Pilz input load clears the Phoenix relay contact's published minimum-load and inrush envelopes on paper. This is a source screen only. The Phoenix relays are ordinary, non-force-guided contacts with zero safety credit; common-cause, routing, physical response and qualified functional-safety validation remain open.</p><section class="metrics"><div class="metric"><strong>4.8×</strong>voltage above published minimum</div><div class="metric"><strong>5.0×</strong>steady current above published minimum</div><div class="metric"><strong>75×</strong>published inrush-current screen</div><div class="metric"><strong>0</strong>safety credit or work authority</div></section><h2>Electrical application screens</h2><div class="table"><table><thead><tr><th>ID</th><th>Parameter</th><th>Value</th><th>Disposition</th><th>What is still missing</th></tr></thead><tbody>{comp}</tbody></table></div><h2>Fault boundary</h2><div class="table"><table><thead><tr><th>Case</th><th>Fault</th><th>Modeled response</th><th>Disposition</th><th>Closure evidence</th></tr></thead><tbody>{faults_html}</tbody></table></div><h2>Configuration verdict</h2><p><strong>Sol B-005: PARTIALLY ADDRESSED / OPEN.</strong> P1.20 remains unaccepted. P1.15 remains current. No source calculation, ERC result or interactive guide authorizes procurement, fabrication, connection, powered testing, motion or energization.</p></main></body></html>'''


def main() -> None:
    for directory in (SAFETY, RELEASE):
        directory.mkdir(parents=True, exist_ok=True)
    datasets = {
        "source-register.csv": (("source_id", "manufacturer", "product", "document", "revision_date", "official_url", "controlled_file", "sha256", "verified_use", "boundary", "warning"), sources()),
        "terminal-path-conformance.csv": (("sequence", "sheet", "reference", "terminal", "pin_name", "net", "source_status", "application_state", "safety_credit", "warning"), terminal_paths()),
        "electrical-compatibility.csv": (("screen_id", "parameter", "value", "unit", "basis", "disposition", "remaining_evidence", "safety_credit", "warning"), compatibility()),
        "fault-behavior.csv": (("case_id", "fault", "modeled_response", "disposition", "closure_evidence", "safety_credit", "warning"), faults()),
        "qualification-questions.csv": (("question_id", "topic", "required_evidence", "state", "owner", "warning"), questions()),
        "open-holds.csv": (("hold_id", "subject", "state", "closure_evidence", "warning"), holds()),
        "b005-disposition.csv": (("finding", "reviewed_baseline_state", "r232_source_change", "r233_application_screen", "current_disposition", "still_open", "qualified_closure", "safety_credit", "work_authority", "warning"), b005()),
    }
    status = {
        "identifier": IDENTIFIER, "round": "R233", "candidate": "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE",
        "current_electrical_product": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "application_disposition": "SOURCE_APPLICATION_SCREEN_PASS_QUALIFIED_AND_PHYSICAL_CLOSURE_OPEN",
        "b005_disposition": "PARTIALLY_ADDRESSED_OPEN", "terminal_path_rows": len(PATH_KEYS),
        "compatibility_screens": 12, "fault_cases": 10, "open_holds": 9,
        "p120_accepted": False, "safety_credit": "NONE", "work_authority": False, "warning": WARNING,
    }
    for directory in (SAFETY, RELEASE):
        for name, (fields, records) in datasets.items():
            write_csv(directory / name, fields, records)
        (directory / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR233 screens the P1.20 PNOZ s4 750104 input path against Phoenix Contact 2967060 source data. The electrical contact screen passes on paper; B-005 remains partially addressed/open, P1.20 remains unaccepted, and safety credit/work authority remain zero.\n", encoding="utf-8", newline="\n")
    (RELEASE / "index.html").write_text(page(compatibility(), faults()), encoding="utf-8", newline="\n")
    manifest = []
    for path in sorted(p for p in RELEASE.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        raw = path.read_bytes()
        manifest.append({"file": path.name, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "warning": WARNING})
    write_csv(RELEASE / "file-manifest.csv", ("file", "size_bytes", "sha256", "warning"), manifest)
    print(f"Wrote {IDENTIFIER}: {len(PATH_KEYS)} path rows, 12 screens, 10 faults, 9 holds")
    print(WARNING)


if __name__ == "__main__":
    main()
