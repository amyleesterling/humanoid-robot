#!/usr/bin/env python3
"""Generate the R180 event-observation independence correction package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/event-observation-correction-p0.1"
WEB = ROOT / "release/hr-v0/event-observation-correction-p0.1"
FORM = ROOT / "tests/forms/hr-v0-event-observation-correction-template.csv"
IDENTIFIER = "HR-V0-EVENT-OBS-CORR-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


SUPERSESSIONS = [
    ("EOS-001", "R174 DTA-003", "Both mirror channels were treated as independent contactor-state evidence", "A single series EDM current exists through K1:21-22 and K2:21-22; use one common EDM-chain current witness plus independent diagnostic K1_STATUS and K2_STATUS channels", "CORRECTED BY R180; historical artifact retained"),
    ("EOS-002", "R175 DCH-010 and DCH-011", "EDM_K1_OUT and SRA1_START_RETURN were allocated as two mirror-contact states", "They are two locations in the same series chain and cannot identify which NC contact changed", "CORRECTED BY R180; historical artifact retained"),
    ("EOS-003", "R176/R177 field-event maps", "Two series EDM nodes were presented as separate mirror feedback channels", "No connected adapter is released; R178 no-connect disposition remains controlling", "SEMANTICS SUPERSEDED; no physical connection authorized"),
    ("EOS-004", "R179 seven-conductor map", "Both series-chain conductors remained candidates without an explicit non-independence rule", "Either conductor may witness common chain current, but never as two independent K1/K2 state observations", "CLARIFIED BY R180"),
]

INSTRUMENTS = [
    ("EOI-001", "Tektronix", "MSO58B", "eight-input common-timebase oscilloscope host", "EXACT EVALUATION CANDIDATE", "8 analog/FlexChannel inputs; up to 6.25 GS/s; 8 TekVPI interfaces", "Bandwidth option, record length, OS/storage, calibration option and exact order configuration remain SELECTION REQUIRED; no safety credit"),
    ("EOI-002", "Tektronix", "TCP0030A", "non-contact AC/DC current probe", "EXACT EVALUATION CANDIDATE; QUANTITY 4 PER RUN", "DC to at least 120 MHz; 1 mA sensitivity; 5 A/30 A ranges; direct TekVPI", "Jaw fit, probe power, range, degauss, delay, uncertainty and simultaneous-host compatibility remain open"),
    ("EOI-003", "Tektronix", "TIVP02 with included TIVPMX10X tip", "isolated voltage probe", "EXACT EVALUATION CANDIDATE; QUANTITY 3 PER RUN", "200 MHz; 2 m cable; included 10X tip has +/-50 V differential range and 10 Mohm || 2.8 pF input", "Exact connection, common-mode/transient envelope, delay compensation, probe power, calibration and uncertainty remain open"),
    ("EOI-004", "SELECTION REQUIRED", "independent motion witness", "angle or displacement channel", "SELECTION REQUIRED; QUANTITY 1 PER RUN", "Must share or be proven aligned to the accepted timebase", "No current or voltage channel proves motion or stopping distance"),
    ("EOI-005", "SELECTION REQUIRED", "K1_STATUS/K2_STATUS diagnostic load and protection", "minimum-current diagnostic application", "SELECTION REQUIRED; TWO CHANNELS", "Must meet the LC1D25BD auxiliary-contact application envelope across rail, tolerance, temperature and faults", "No resistor value, part, protection device, conductor or connection is released"),
]

CHANNELS = [
    ("EOC-01", "STOP", "CH1", "SR1_S12", "W2008", "SR1:S12", "TCP0030A", "stop-event current", "Primary event witness only after thresholds and uncertainty close"),
    ("EOC-02", "STOP", "CH2", "K1_A1", "W4001", "K1:A1", "TCP0030A", "K1 coil current", "Command-current witness; does not prove contact position"),
    ("EOC-03", "STOP", "CH3", "K2_A1", "W4007", "K2:A1", "TCP0030A", "K2 coil current", "Command-current witness; does not prove contact position"),
    ("EOC-04", "STOP", "CH4", "SRA1_START_RETURN", "W3007", "SRA1:S34", "TCP0030A", "common series EDM-chain current", "EDM_K1_OUT is an allowed alternative location, never a second independent mirror channel"),
    ("EOC-05", "STOP", "CH5", "K1_STATUS", "W9010", "XT1:XT1-05", "TIVP02/TIVPMX10X", "individual K1 NO auxiliary diagnostic voltage", "Blocked until exact diagnostic load/protection closes; zero safety credit"),
    ("EOC-06", "STOP", "CH6", "K2_STATUS", "W9011", "XT1:XT1-06", "TIVP02/TIVPMX10X", "individual K2 NO auxiliary diagnostic voltage", "Blocked until exact diagnostic load/protection closes; zero safety credit"),
    ("EOC-07", "STOP", "CH7", "SAFETY_24V-to-SAFETY_0V", "SELECTION REQUIRED", "accepted isolated test points", "TIVP02/TIVPMX10X", "control-source voltage witness", "Exact test points, protection and connection remain SELECTION REQUIRED"),
    ("EOC-08", "STOP", "CH8", "MOTION", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "independent angle/displacement witness", "Exact transducer and host interface remain SELECTION REQUIRED"),
    ("EOC-09", "RESET_ARM", "CH1", "SR1_START_RETURN", "W2011", "SR1:S34", "TCP0030A", "RESET event current", "RESET actuation shall not command coil current or motion"),
    ("EOC-10", "RESET_ARM", "CH2", "ARM_AFTER_S2", "W3021", "S2:TBD-A2", "TCP0030A", "ARM/EDM path current", "S2 received terminal remains SELECTION REQUIRED"),
    ("EOC-11", "RESET_ARM", "CH3", "K1_A1", "W4001", "K1:A1", "TCP0030A", "K1 coil current", "Command-current witness; does not prove contact position"),
    ("EOC-12", "RESET_ARM", "CH4", "K2_A1", "W4007", "K2:A1", "TCP0030A", "K2 coil current", "Command-current witness; does not prove contact position"),
    ("EOC-13", "RESET_ARM", "CH5", "K1_STATUS", "W9010", "XT1:XT1-05", "TIVP02/TIVPMX10X", "individual K1 NO auxiliary diagnostic voltage", "Blocked until exact diagnostic load/protection closes; zero safety credit"),
    ("EOC-14", "RESET_ARM", "CH6", "K2_STATUS", "W9011", "XT1:XT1-06", "TIVP02/TIVPMX10X", "individual K2 NO auxiliary diagnostic voltage", "Blocked until exact diagnostic load/protection closes; zero safety credit"),
    ("EOC-15", "RESET_ARM", "CH7", "SAFETY_24V-to-SAFETY_0V", "SELECTION REQUIRED", "accepted isolated test points", "TIVP02/TIVPMX10X", "control-source voltage witness", "Exact test points, protection and connection remain SELECTION REQUIRED"),
    ("EOC-16", "RESET_ARM", "CH8", "MOTION", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "independent angle/displacement witness", "Exact transducer and host interface remain SELECTION REQUIRED"),
]

TEST_CASES = [
    ("EOT-001", "E-stop stop", "STOP", "E-stop demand opens both safety channels", "All eight channels simultaneous; classify event, both coil currents, common EDM chain, two diagnostic auxiliaries, source rail and motion", "Stopping limit, threshold, repetition and uncertainty remain SELECTION REQUIRED", "NOT EXECUTED"),
    ("EOT-002", "watchdog stop", "STOP", "accepted watchdog-fault injection removes permit", "Same eight STOP channels and common clock", "Fault injection, stopping limit, threshold, repetition and uncertainty remain SELECTION REQUIRED", "NOT EXECUTED"),
    ("EOT-003", "E-stop RESET without ARM", "RESET_ARM", "release E-stop then operate monitored RESET only", "RESET current may occur; K1/K2 coil-current and motion channels shall show no commanded motion", "Exact no-motion threshold and uncertainty remain SELECTION REQUIRED", "NOT EXECUTED"),
    ("EOT-004", "ARM sequence", "RESET_ARM", "after valid RESET, deliberate separate ARM action", "ARM path, coils, diagnostics, source and motion observed simultaneously", "Motion authorization remains prohibited in disconnected-load E2; interpretation limit SELECTION REQUIRED", "NOT EXECUTED"),
]

LOAD_HOLDS = [
    ("EOL-001", "K1_STATUS load/return", "P1.15 feeds K1:13 from SAFETY_24V; define the exact protected diagnostic load, conductor and return from K1:14/XT1-05 to SAFETY_0V"),
    ("EOL-002", "K2_STATUS load/return", "P1.15 feeds K2:13 from SAFETY_24V; define the exact protected diagnostic load, conductor and return from K2:14/XT1-06 to SAFETY_0V"),
    ("EOL-003", "minimum switching current", "Prove at least the manufacturer-published 5 mA at 17 V across rail minimum, resistor tolerance, temperature and wiring resistance"),
    ("EOL-004", "maximum application", "Prove contact current, voltage, resistor power, surface temperature and terminal/connector limits at rail maximum and transients"),
    ("EOL-005", "single faults", "Analyze open, short, wrong-value, short-to-0V, short-to-24V, cross-channel and loss-of-source faults without safety credit"),
    ("EOL-006", "exact parts", "Select exact resistor/protection/test-terminal order codes and approved mounting; no calculated example is a released design"),
    ("EOL-007", "diagnostic semantics", "Define valid OPEN/CLOSED/INVALID thresholds and disagreement handling; K1/K2 NO auxiliaries may only corroborate the NC mirror EDM chain"),
    ("EOL-008", "qualified review", "Qualified electrical and functional-safety reviewers must accept the diagnostic circuit and confirm it cannot create automatic restart or mask EDM faults"),
]

HOLDS = [
    ("EOH-001", "MSO58B configuration", "Exact bandwidth, record length, OS/storage, export, calibration and order configuration"),
    ("EOH-002", "simultaneous probe power", "Prove four TCP0030A plus three TIVP02 loads fit the MSO58B total and channel-group power limits"),
    ("EOH-003", "probe calibration", "In-date traceable calibration, zero/degauss, deskew and end-to-end checks for every probe and host channel"),
    ("EOH-004", "motion witness", "Exact transducer, range, mount, interface, calibration, latency, bandwidth and uncertainty"),
    ("EOH-005", "diagnostic loads", "Close all eight EOL records before any K1_STATUS/K2_STATUS connection or interpretation"),
    ("EOH-006", "source witness", "Exact isolated test points, connection, range, transient envelope, loading, protection and uncertainty"),
    ("EOH-007", "as-built conductors", "Bind every wire number and terminal to the received physical conductor; S2 terminal remains unresolved"),
    ("EOH-008", "jaw fit/noninterference", "Prove one-conductor capture, clearance and repeated jaw-open/jaw-closed equivalence in disconnected-load E2"),
    ("EOH-009", "thresholds and timing", "Freeze sign, thresholds, hysteresis, dwell, sample rate, record length, trigger, deskew and invalid-data rules"),
    ("EOH-010", "uncertainty budget", "Combine probe, host, threshold, delay, alignment, motion, source and repeatability uncertainty"),
    ("EOH-011", "E2 boundary", "Actuator source absent; K1/K2 load poles unsourced and unwired; guarded access and separate work authorization"),
    ("EOH-012", "qualified disposition", "Qualified electrical and functional-safety review of setup, physical results, fault injection, limitations and no-safety-credit boundary"),
]

SOURCES = [
    ("EOSRC-001", "Tektronix", "MSO58B product page", "current product record", "accessed 2026-08-10", "https://www.tek.com/en/products/oscilloscopes/5-series-mso/mso58b-oscilloscope-2-ghz-8-analog-64-digital-channels", "Eight analog/FlexChannel inputs, 6.25 GS/s maximum and current product status"),
    ("EOSRC-002", "Tektronix", "5 Series B MSO specifications and performance verification", "077-1725-01 Rev C", "current document accessed 2026-08-10", "https://www.tek.com/en/manual/oscilloscope/5-series-mso-5b-mso54b-mso56b-mso58b-mso58lp-mso58blp-specifications-and-performance", "MSO58B TekVPI count, sample/timebase limits and probe-power allocation boundary"),
    ("EOSRC-003", "Tektronix", "TCP0030A datasheet", "51W-19042-12", "2025-04-10; accessed 2026-08-10", "https://www.tek.com/en/support/datasheets-manuals-software-downloads?model=TCP0030A", "Current probe ranges, sensitivity, bandwidth, delay, conductor size and TekVPI compatibility"),
    ("EOSRC-004", "Tektronix", "TIVP series IsoVu datasheet", "51W-61655-7", "2026-06-14; accessed 2026-08-10", "https://www.tek.com/en/datasheet/isolated-measurement-systems-tivp1-tivp05-tivp02-datasheet", "TIVP02 bandwidth/cable and TIVPMX10X differential range/input loading"),
    ("EOSRC-005", "Tektronix", "TIVP series IsoVu user manual", "071-3692-09", "2026-06-14; accessed 2026-08-10", "https://www.tek.com/en/manual/low-voltage-differential-probe/tivp-series-isovu-measurement-system-user-manual-isovu-isolated-voltage-probes", "Connection, delay, offset, safety and operating boundaries"),
    ("EOSRC-006", "Schneider Electric", "TeSys D LC1D25BD product sheet and auxiliary-contact application record", "current product record; FAQ FA126437", "rechecked 2026-08-10", "https://www.se.com/us/en/product/LC1D25BD/tesys-d-contactor-3p3-no-ac3-ac3e-440v-25a-24v-dc-coil/", "Built-in 1NO+1NC auxiliary arrangement; minimum signaling-current application remains controlled by R117 primary-source evidence"),
    ("EOSRC-007", "Project Button", "Electrical V3-P1.15 net and wire schedules", "P1.15", "controlled commit R179; rechecked 2026-08-10", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/net-schedule.csv", "EDM series topology and exact logical wire/terminal locations; not an as-built release"),
]


def write_csv(path: Path, header: list[str], rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


def build_package() -> None:
    write_csv(PKG / "supersession-register.csv", ["record_id", "affected_record", "incorrect_assumption", "corrected_model", "disposition"], SUPERSESSIONS)
    write_csv(PKG / "instrument-register.csv", ["instrument_id", "manufacturer", "identity", "role", "selection_state", "controlled_capability", "use_limit"], INSTRUMENTS)
    write_csv(PKG / "channel-allocation.csv", ["channel_id", "run_type", "host_channel", "signal", "wire_number", "terminal", "candidate_instrument", "purpose", "interpretation_limit"], CHANNELS)
    write_csv(PKG / "test-case-allocation.csv", ["test_id", "case", "run_type", "stimulus", "simultaneous_evidence", "acceptance_boundary", "state"], TEST_CASES)
    write_csv(PKG / "diagnostic-load-holds.csv", ["hold_id", "topic", "closure_evidence"], LOAD_HOLDS)
    write_csv(PKG / "closure-holds.csv", ["hold_id", "topic", "closure_evidence"], HOLDS)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "title", "document", "revision_or_date", "official_locator", "engineering_use"], SOURCES)
    write_csv(FORM, ["run_id", "test_id", "configuration_commit", "host_model", "host_serial", "host_configuration", "channel_id", "signal", "wire_number", "terminal", "instrument_model", "instrument_serial", "calibration_evidence_uri", "sample_rate", "record_length", "range", "threshold", "deskew", "trace_uri", "motion_trace_uri", "source_trace_uri", "setup_photo_uri", "result", "deviation_id", "executor", "utc_timestamp", "reviewer", "decision"], [])
    (PKG / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "round": "R180",
        "date": "2026-08-10",
        "status": WARNING,
        "corrected_false_independence_count": 1,
        "simultaneous_host_channel_count": 8,
        "run_type_count": 2,
        "selected_host_base_model_count": 1,
        "selected_host_order_configuration_count": 0,
        "released_diagnostic_load_count": 0,
        "released_connection_count": 0,
        "executed_physical_test_count": 0,
        "safety_function_credit": "ZERO",
        "eg_025": "OPEN",
        "eg_026": "PARTIAL",
        "release_effect": "NONE",
    }, indent=2) + "\n", encoding="utf-8")


def build_web() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    cards = []
    for row in CHANNELS[:8]:
        cid, _, ch, signal, wire, terminal, instrument, purpose, limit = row
        cards.append(f'''<article class="card"><div class="eyebrow">{escape(ch)} &middot; {escape(cid)}</div><h2>{escape(signal)}</h2><p><strong>{escape(purpose)}</strong></p><dl><dt>Location</dt><dd>{escape(wire)} &middot; {escape(terminal)}</dd><dt>Candidate</dt><dd>{escape(instrument)}</dd><dt>Boundary</dt><dd>{escape(limit)}</dd></dl></article>''')
    holds = "".join(f"<li><strong>{escape(row[1])}:</strong> {escape(row[2])}</li>" for row in HOLDS)
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 event-observation correction</title><style>
:root{{--sky:#dff3ff;--blue:#092e66;--mid:#1267a5;--gold:#f5bd2e;--ink:#10213a;--paper:#fff;--hold:#8a2d0b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main,footer{{max-width:1180px;margin:auto;padding:24px}}.warning{{background:var(--blue);color:#fff;border-bottom:6px solid var(--gold);font-weight:800;padding:16px 24px}}h1{{font-size:clamp(34px,6vw,68px);line-height:1.04;margin:.25em 0}}h2{{font-size:24px;line-height:1.15;margin:.3em 0}}.lead{{font-size:20px;max-width:900px}}.correction{{background:#fff4c7;border-left:8px solid var(--gold);padding:20px;margin:24px 0;font-size:18px}}.chain{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:12px;align-items:center;background:#fff;padding:20px;border:2px solid var(--blue);border-radius:16px;margin:24px 0}}.node{{padding:14px;background:var(--sky);border-radius:10px;font-weight:800;text-align:center}}.arrow{{font-size:28px;color:var(--mid)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.card{{background:var(--paper);border:2px solid var(--blue);border-radius:18px;padding:20px;box-shadow:6px 6px 0 var(--blue)}}.eyebrow,dt{{font-size:14px;font-weight:800;color:var(--mid);text-transform:uppercase;letter-spacing:.04em}}dd{{margin:0 0 12px}}.held{{color:var(--hold);font-weight:900}}section{{margin:38px 0}}li{{margin:10px 0}}footer{{font-size:14px}}@media(max-width:620px){{header,main,footer{{padding:18px}}.grid{{grid-template-columns:1fr}}.chain{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);text-align:center}}}}
</style></head><body><div class="warning">{escape(WARNING)}</div><header><div class="eyebrow">R180 &middot; {IDENTIFIER}</div><h1>One EDM chain is not two contact states.</h1><p class="lead">R180 corrects the observation model before any instrument is bought or connected. The two former EDM points carry the same series-chain current. Individual contactor corroboration must come from separate diagnostic auxiliaries, with zero safety credit.</p></header><main><div class="correction"><strong>Controlled correction:</strong> use one common EDM-chain current witness. K1_STATUS and K2_STATUS may become individual diagnostic voltage witnesses only after an exact protected minimum-current application is selected, analyzed and independently accepted.</div><div class="chain" aria-label="series EDM chain"><div class="node">K1 NC mirror<br>21&ndash;22</div><div class="arrow">&rarr;</div><div class="node">Same series current<br>one common witness</div><div class="arrow">&rarr;</div><div class="node">K2 NC mirror<br>21&ndash;22</div></div><section><h2>Eight simultaneous STOP channels</h2><div class="grid">{''.join(cards)}</div></section><section><h2>What the eight channels can and cannot show</h2><p>Coil current shows command-current behavior. The common EDM current shows the state of the series feedback chain. Separate NO auxiliary voltages can corroborate individual contactor state, but cannot replace the NC mirror-contact EDM safety function. The isolated source witness distinguishes command changes from rail collapse. Only the independent motion channel can support a stopping or no-motion claim.</p><p class="held">No diagnostic load, probe connection, physical run or safety claim is released.</p></section><section><h2>Twelve remaining closure holds</h2><ol>{holds}</ol></section></main><footer>{escape(WARNING)} &middot; MSO58B, TCP0030A and TIVP02 are evaluation candidates only. No test host receives functional-safety credit.</footer></body></html>'''
    (WEB / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    build_package()
    build_web()
    print(f"generated {IDENTIFIER}: corrected one false-independence model; 8 simultaneous channels; 0 released connections")
    print(WARNING)


if __name__ == "__main__":
    main()
