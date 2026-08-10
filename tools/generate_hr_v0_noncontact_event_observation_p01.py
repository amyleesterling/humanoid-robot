#!/usr/bin/env python3
"""Generate the R179 non-contact event-observation correction package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical/analysis/hr-v0-noncontact-event-observation-p0.1"
WEB = ROOT / "release/hr-v0/noncontact-event-observation-p0.1"
FORM = ROOT / "tests/forms/hr-v0-noncontact-event-observation-template.csv"
IDENTIFIER = "HR-V0-NONCONTACT-EVENT-OBS-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


CONDUCTORS = [
    ("NCO-001", "SR1_S12", "W2008", "SR1:S12", "02_estop_eligibility.kicad_sch", "Pilz input/start feed", "50 mA steady; 0.2 A / 100 ms published input pulse", "TCP0030A jaw around this conductor only; polarity mark SELECTION REQUIRED"),
    ("NCO-002", "SR1_START_RETURN", "W2011", "SR1:S34", "02_estop_eligibility.kicad_sch", "Pilz monitored RESET return", "50 mA steady; 0.2 A / 15 ms published start pulse", "TCP0030A jaw around this conductor only; threshold SELECTION REQUIRED"),
    ("NCO-003", "ARM_AFTER_S2", "W3021", "S2:TBD-A2", "03_arm_watchdog_eligibility.kicad_sch", "Pilz ARM/EDM path", "50 mA steady; 0.2 A / 15 ms published start/feedback pulse", "S2 terminal remains TBD; received terminal and physical conductor identity required"),
    ("NCO-004", "K1_A1", "W4001", "K1:A1", "04_contactor_edm.kicad_sch", "Schneider K1 coil feed", "5.4 W at 24 V nominal; pickup/transient unmeasured", "TCP0030A jaw around this conductor only; K1:A2 returns to SAFETY_0V"),
    ("NCO-005", "K2_A1", "W4007", "K2:A1", "04_contactor_edm.kicad_sch", "Schneider K2 coil feed", "5.4 W at 24 V nominal; pickup/transient unmeasured", "TCP0030A jaw around this conductor only; K2:A2 returns to SAFETY_0V"),
    ("NCO-006", "EDM_K1_OUT", "W4005", "K1:22", "04_contactor_edm.kicad_sch", "Pilz EDM chain between mirror contacts", "50 mA steady; 0.2 A / 15 ms published feedback pulse", "TCP0030A jaw around this conductor only; physical direction toward K2:21 must be recorded"),
    ("NCO-007", "SRA1_START_RETURN", "W3007", "SRA1:S34", "03_arm_watchdog_eligibility.kicad_sch", "Pilz monitored ARM/EDM return", "50 mA steady; 0.2 A / 15 ms published start/feedback pulse", "TCP0030A jaw around this conductor only; threshold SELECTION REQUIRED"),
]

INSTRUMENTS = [
    ("NCI-001", "Tektronix", "TCP0030A", "AC/DC current probe", "EXACT EVALUATION CANDIDATE", "DC to at least 120 MHz; 1 mA sensitivity; 5 A/30 A ranges; 14.5 ns signal delay; 5 mm maximum conductor; direct TekVPI interface", "No galvanic field connection, but jaw placement, calibration, conductor routing, magnetic/mechanical influence and measurement uncertainty remain unproved"),
    ("NCI-002", "SELECTION REQUIRED", "TekVPI-compatible oscilloscope", "shared-timebase acquisition host", "SELECTION REQUIRED", "Must support the exact probe, channel count, sample rate, record length, trigger/export and traceable calibration needed by each test", "Do not infer a scope model or option code; no general-purpose host receives safety credit"),
    ("NCI-003", "SELECTION REQUIRED", "independent motion witness", "angle/displacement channel", "SELECTION REQUIRED", "Must close the R174 range, bandwidth, latency, synchronization, calibration and uncertainty requirements", "Current observation alone cannot prove motion stop or reset-without-motion"),
    ("NCI-004", "SELECTION REQUIRED", "source-voltage monitor", "24 V rail witness", "SELECTION REQUIRED", "Must observe the control-source rail without adding an unaccepted return path", "Exact isolation, probe loading and transient range remain open"),
]

SOURCES = [
    ("NCS-001", "Tektronix", "TCP0030A datasheet", "51W-19042-12", "2025-04-10; accessed 2026-08-10", "https://www.tek.com/en/support/datasheets-manuals-software-downloads?model=TCP0030A", "Current availability, 1 mA sensitivity, current ranges, bandwidth, signal delay, conductor size, accuracy and compatible-host boundary"),
    ("NCS-002", "Tektronix", "TCP0030A instruction manual", "071300601", "2020-12-04; accessed 2026-08-10", "https://www.tek.com/en/manual/current-probe/tcp0030a-current-probe", "Operating, degauss, functional-check, calibration and handling requirements"),
    ("NCS-003", "Pilz", "PNOZ s4 operating manual", "21396-EN-23", "2026-02 document; portal/PDF rechecked 2026-08-10", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "Input/start/feedback currents and pulses; monitored-start and protected/separate wiring limits"),
    ("NCS-004", "Project Button", "Electrical V3-P1.15 wire-number table", "P1.15", "controlled commit R178; rechecked 2026-08-10", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/wire-number-table.csv", "Exact logical conductor labels and terminal locations; not an as-built conductor release"),
    ("NCS-005", "GlobTek", "WR9QI1660YL4NKITR6B live record", "exact order code; Rev B specification controlled by R81", "live record accessed 2026-08-10", "https://www.globtek.com/_0/WR9QI1660YL4NKITR6B/o", "24 V / 1.66 A / 40 W source and YL4/C40337 pin assignment; application remains held"),
]

HOLDS = [
    ("NCH-001", "AS-BUILT CONDUCTOR IDENTITY", "Received terminal identities, from/to schedule, wire part, gauge, insulation OD, length and photographs must bind each W-number to one physical conductor"),
    ("NCH-002", "JAW FIT AND ROUTING", "A 5 mm-jaw clearance study must prove one-conductor capture without pinching, moving, opening or magnetically coupling adjacent conductors"),
    ("NCH-003", "HOST SELECTION", "Exact compatible TekVPI oscilloscope model/options, channel count, sample rate, record length, trigger and export path are required"),
    ("NCH-004", "CALIBRATION", "Current probe and host require in-date traceable calibration, degauss/zero records and an end-to-end injected-current check"),
    ("NCH-005", "POLARITY AND THRESHOLDS", "Every conductor direction, current sign, pulse/steady threshold, hysteresis, dwell and invalid-data rule remains SELECTION REQUIRED"),
    ("NCH-006", "NONINTERFERENCE", "Repeated jaw-open versus jaw-closed disconnected-load E2 sequences must show no state, timing, reset, EDM or dropout change within accepted limits"),
    ("NCH-007", "SIMULTANEITY", "Probe quantity and shared-timebase allocation must cover each claimed causal timing measurement; sequential runs cannot prove simultaneity"),
    ("NCH-008", "MOTION WITNESS", "An independent calibrated angle/displacement channel must prove stopping and no reset/ARM-commanded motion"),
    ("NCH-009", "SOURCE WITNESS", "An accepted isolated control-rail voltage channel must separate command-state changes from source collapse or brownout"),
    ("NCH-010", "E2 BOUNDARY", "Actuator source absent; K1/K2 load poles unsourced and unwired; guarded access, qualified authorization and abort conditions required"),
    ("NCH-011", "UNCERTAINTY", "Probe accuracy/delay, host timing, thresholds, motion witness, source witness, alignment and repeatability must close the R174 budget"),
    ("NCH-012", "QUALIFIED REVIEW", "Qualified electrical and functional-safety reviewers must accept the exact setup, failure analysis, results and limitations"),
]

STEPS = [
    ("NCT-001", "Authority and configuration", "Verify controlled commit, E2 boundary, named personnel and written work authorization", "No source or probe application before every prerequisite is signed", "NOT EXECUTED"),
    ("NCT-002", "Unpowered conductor survey", "With every source physically absent, reconcile all seven W-numbers and photograph terminal-to-conductor routes", "All seven identities exact; any TBD/ambiguity stops the procedure", "NOT EXECUTED"),
    ("NCT-003", "Jaw-clearance coupon", "Check one-conductor jaw closure, insulation condition and adjacent-conductor clearance without powered hardware", "No pinch, displacement, exposed copper, terminal load or adjacent capture", "NOT EXECUTED"),
    ("NCT-004", "Instrument validity", "Record probe/host identity, calibration, zero, degauss, range and injected-current check", "Accepted calibration and end-to-end result; numeric limit SELECTION REQUIRED", "NOT EXECUTED"),
    ("NCT-005", "Jaw-open baseline", "Run the separately authorized disconnected-load E2 RESET/ARM/E-stop/watchdog sequence with no probe jaw around the target conductor", "Complete synchronized traces; no load-pole source and no motion authority", "NOT EXECUTED"),
    ("NCT-006", "Jaw-closed comparison", "Repeat the identical sequence with the probe around one exact conductor and all other setup held constant", "No accepted state/timing difference; numeric equivalence limit SELECTION REQUIRED", "NOT EXECUTED"),
    ("NCT-007", "Seven-conductor matrix", "Repeat NCT-005/006 for all seven conductors and required fault/recovery cases", "Every planned case has raw trace, setup photo, result and deviation disposition", "NOT EXECUTED"),
    ("NCT-008", "Synchronized stop/no-motion run", "Use accepted simultaneous event, coil, source and independent-motion channels", "Stopping and no-reset/no-ARM-motion requirements evaluated with full uncertainty; limits SELECTION REQUIRED", "NOT EXECUTED"),
    ("NCT-009", "Teardown and review", "Remove instrumentation, inspect conductors/terminals and obtain independent plus qualified dispositions", "No damage; hashes complete; deviations closed; reviewers sign or reject", "NOT EXECUTED"),
]


def write_csv(path: Path, header: list[str], rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


def build_package() -> None:
    write_csv(PKG / "conductor-observation-map.csv", ["record_id", "net", "wire_number", "terminal", "sheet", "role", "published_current_basis", "candidate_observation"], CONDUCTORS)
    write_csv(PKG / "instrument-register.csv", ["instrument_id", "manufacturer", "identity", "role", "selection_state", "controlled_capability", "use_limit"], INSTRUMENTS)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "title", "document", "revision_or_date", "official_locator", "engineering_use"], SOURCES)
    write_csv(PKG / "closure-holds.csv", ["hold_id", "topic", "closure_evidence"], HOLDS)
    write_csv(PKG / "e2-comparison-sequence.csv", ["step_id", "operation", "method", "acceptance_boundary", "state"], STEPS)
    write_csv(FORM, ["run_id", "configuration_commit", "wire_number", "terminal", "jaw_state", "probe_serial", "host_serial", "calibration_evidence_uri", "range", "sample_rate", "threshold", "current_trace_uri", "source_trace_uri", "motion_trace_uri", "video_uri", "result", "deviation_id", "executor", "utc_timestamp", "reviewer", "decision"], [])
    (PKG / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "date": "2026-08-10",
        "status": WARNING,
        "exact_logical_conductor_count": 7,
        "electrical_field_tap_count": 0,
        "permanent_adapter_released_count": 0,
        "exact_probe_candidate_count": 1,
        "selected_host_count": 0,
        "open_hold_count": len(HOLDS),
        "executed_physical_test_count": 0,
        "safety_function_credit": "ZERO",
        "decision": "REJECT PERMANENT PASSIVE DIVIDER FOR CURRENT BASELINE; RETAIN NON-CONTACT CURRENT OBSERVATION AS EVALUATION-ONLY ROUTE",
        "eg_025": "OPEN",
        "eg_026": "PARTIAL",
        "release_effect": "NONE",
    }, indent=2) + "\n", encoding="utf-8")


def build_web() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    cards = []
    for row in CONDUCTORS:
        rid, net, wire, terminal, sheet, role, basis, route = row
        group = "coil" if net in {"K1_A1", "K2_A1"} else "pilz"
        cards.append(f'''<article class="card" data-kind="{group}"><div class="eyebrow">{escape(rid)} &middot; {escape(wire)}</div><h2>{escape(net)}</h2><p><strong>{escape(role)}</strong></p><dl><dt>Clamp location</dt><dd>{escape(terminal)} on {escape(sheet)}</dd><dt>Published current basis</dt><dd>{escape(basis)}</dd><dt>Candidate route</dt><dd>{escape(route)}</dd></dl><p class="held">No electrical tap. No released test.</p></article>''')
    hold_items = "".join(f"<li><strong>{escape(row[1])}:</strong> {escape(row[2])}</li>" for row in HOLDS)
    source_items = "".join(f'<li><a href="{escape(row[5])}">{escape(row[1])}: {escape(row[2])} ({escape(row[3])})</a> &mdash; {escape(row[4])}</li>' for row in SOURCES if row[5].startswith("http"))
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 non-contact event observation</title><style>
:root{{--sky:#dff3ff;--blue:#092e66;--mid:#1267a5;--gold:#f5bd2e;--ink:#10213a;--paper:#fff;--hold:#8a2d0b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main,footer{{max-width:1180px;margin:auto;padding:24px}}.warning{{background:var(--blue);color:#fff;border-bottom:6px solid var(--gold);font-weight:800;padding:16px 24px}}h1{{font-size:clamp(34px,6vw,68px);line-height:1.04;margin:.25em 0}}h2{{font-size:25px;margin:.25em 0}}.lead{{font-size:20px;max-width:880px}}.decision{{background:#fff4c7;border-left:8px solid var(--gold);padding:18px;margin:24px 0;font-size:18px}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}}button{{font:700 16px/1.2 system-ui,sans-serif;border:2px solid var(--blue);border-radius:999px;padding:12px 18px;background:#fff;color:var(--blue);cursor:pointer}}button[aria-pressed="true"]{{background:var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}}.card{{background:var(--paper);border:2px solid var(--blue);border-radius:18px;padding:20px;box-shadow:6px 6px 0 var(--blue)}}.eyebrow,dt{{font-size:14px;font-weight:800;color:var(--mid);text-transform:uppercase;letter-spacing:.04em}}dd{{margin:0 0 12px}}.held{{color:var(--hold);font-weight:900}}section{{margin:38px 0}}li{{margin:10px 0}}footer{{font-size:14px}}[hidden]{{display:none!important}}@media(max-width:520px){{header,main,footer{{padding:18px}}.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{escape(WARNING)}</div><header><div class="eyebrow">R179 &middot; {IDENTIFIER}</div><h1>Observe current. Do not tap the safety path.</h1><p class="lead">R178 proved that a catalog-only divider cannot be released on these seven nodes. R179 retains a non-contact AC/DC current-probe route for disconnected-load E2 evaluation, with no conductive field connection and zero safety credit.</p></header><main><div class="decision"><strong>Engineering decision:</strong> the permanent AMC3330 passive-divider route is rejected for the current baseline. Tektronix TCP0030A is an exact evaluation candidate; the host, physical routing, thresholds, calibration, uncertainty and every powered run remain held.</div><div class="controls" aria-label="Filter conductor locations"><button data-filter="all" aria-pressed="true">All 7</button><button data-filter="pilz" aria-pressed="false">Pilz paths</button><button data-filter="coil" aria-pressed="false">Coil feeds</button></div><div class="grid">{''.join(cards)}</div><section><h2>Why this is safer to evaluate</h2><p>The probe jaw surrounds one insulated conductor. It does not add a resistor, capacitance or galvanic return to the monitored node. That removes the specific divider-loading mechanism, but it does not prove noninterference: jaw fit, conductor movement, magnetic influence, calibration, polarity, thresholds and synchronized timing still require physical evidence.</p></section><section><h2>Twelve closure holds</h2><ol>{hold_items}</ol></section><section><h2>Current primary sources</h2><ul>{source_items}</ul></section></main><footer>{escape(WARNING)} &middot; No probe, scope, DAQ, EVM or test host receives functional-safety credit.</footer><script>
const buttons=[...document.querySelectorAll('button[data-filter]')],cards=[...document.querySelectorAll('.card')];buttons.forEach(button=>button.addEventListener('click',()=>{{buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));cards.forEach(card=>card.hidden=button.dataset.filter!=='all'&&card.dataset.kind!==button.dataset.filter)}}));
</script></body></html>'''
    (WEB / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    build_package()
    build_web()
    print(f"generated {IDENTIFIER}: 7 exact logical conductor locations, 0 electrical taps, 12 open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
