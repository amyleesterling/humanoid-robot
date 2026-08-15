#!/usr/bin/env python3
"""Generate the R208 observation compute-power and partial-power boundary package."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from generate_hr_v0_observation_field_harness_p01 import digest, manifest, table, write, write_csv


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/interfaces/hr-v0-observation-compute-power-boundary-p0.1"
WEB = ROOT / "release/hr-v0/observation-compute-power-boundary-p0.1"
DOC = ROOT / "docs/hr-v0-observation-compute-power-boundary-p0.1.md"
IDENTIFIER = "HR-V0-OBSERVATION-COMPUTE-POWER-BOUNDARY-P0.1"
ROUND = "R208"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R203 = ROOT / "electrical/interfaces/hr-v0-runtime-observation-pi-pinmap-p0.1"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
R207 = ROOT / "electrical/harness/hr-v0-observation-compute-harness-p0.1"
P116 = ROOT / "electrical/kicad/project-button-v3-p1.16-observation-candidate"


def main() -> int:
    source_paths = {
        "R202 BOM": R202 / "bom.csv",
        "R202 connector schedule": R202 / "connector-schedule.csv",
        "R202 load budget": R202 / "load-budget.csv",
        "R202 native netlist": R202 / "validation/hr-v0-runtime-observation-carrier-p0.2.net",
        "R203 pinmap summary": R203 / "pinmap-summary.json",
        "R204 connector schedule": R204 / "connector-schedule.csv",
        "R207 conductor schedule": R207 / "conductor-schedule.csv",
        "P1.16 connector schedule": P116 / "connector-schedule.csv",
    }
    for path in source_paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    ENG.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    source_register = [
        {
            "source_id": "OCP-SRC-001", "manufacturer": "Raspberry Pi", "document": "Raspberry Pi HAT+ Specification",
            "revision_date": "05 December 2024", "official_url": "https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf",
            "use_and_limit": "Defines OFF, WARM_STANDBY, STANDBY, SLEEP and ACTIVE; requires add-on circuitry to tolerate STANDBY with 5 V present and 3.3 V absent, unspecified rail sequencing and weak GPIO pulls. R204 is not claimed to be a HAT+.", "warning": WARNING,
        },
        {
            "source_id": "OCP-SRC-002", "manufacturer": "Raspberry Pi", "document": "Raspberry Pi computer hardware documentation - GPIO and power",
            "revision_date": "current web documentation; accessed 2026-08-10", "official_url": "https://www.raspberrypi.com/documentation/computers/raspberry-pi.html",
            "use_and_limit": "Confirms 3.3 V GPIO semantics, input/output configuration, weak pulls, Pi 5 27 W supply recommendation and approximate aggregate GPIO-output guidance. It does not publish a Pi 5 header-3V3 external-load limit or RP1 VIH/VIL/injection-current table.", "warning": WARNING,
        },
        {
            "source_id": "OCP-SRC-003", "manufacturer": "Raspberry Pi", "document": "RP1 Peripherals",
            "revision_date": "release 1.1; 07 November 2023", "official_url": "https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf",
            "use_and_limit": "Confirms Raspberry Pi 5 RP1 GPIO bank, 3.3 V interface timing basis and reset output-disable state. The current document contains no quantitative GPIO DC electrical-characteristics table.", "warning": WARNING,
        },
        {
            "source_id": "OCP-SRC-004", "manufacturer": "Texas Instruments", "document": "ISO1211/ISO1212 datasheet",
            "revision_date": "SLLSEY7G; revised February 2025", "official_url": "https://www.ti.com/lit/ds/symlink/iso1211.pdf",
            "use_and_limit": "ISO1212 VCC1 2.25-5.5 V; ICC1 max 1.9 mA; +/-3 mA recommended OUT current at 3.3 V; VOH at least VCC1-0.4 V and VOL at most 0.4 V at stated loads; output is undetermined while VCC1 is powered down/transitioning. Application suitability still requires validation.", "warning": WARNING,
        },
    ]
    write_csv(ENG / "source-register.csv", source_register)

    topology = [
        {"path_id": "PWR-01", "from": "PI1 physical pin 17 / 3V3", "through": "R204 JPI1:17 -> JOBS1:1 -> W14001 -> R202 JLOGIC1:1", "to": "UOBS1/UOBS2 VCC1 and EN; CDEC1/CDEC2", "domain": "COMPUTE", "source_count": "ONE INTENDED SOURCE", "state": "DIGITAL TOPOLOGY PROVED; PHYSICAL/LOAD APPROVAL OPEN", "warning": WARNING},
        {"path_id": "RET-01", "from": "PI1 physical pin 20 / GND", "through": "R204 JPI1:20 -> JOBS1:2 -> W14002 -> R202 JLOGIC1:2", "to": "UOBS1/UOBS2 GND1; pulldowns; decoupling return", "domain": "COMPUTE", "source_count": "RETURN ONLY", "state": "DIGITAL TOPOLOGY PROVED; PHYSICAL/RETURN-SHIFT APPROVAL OPEN", "warning": WARNING},
        {"path_id": "SIG-01", "from": "UOBS1/UOBS2 OUT1/OUT2", "through": "one 1.00 kohm RSO candidate then one 10.0 kohm RPD to COMPUTE_0V", "to": "GPIO22/GPIO23/GPIO24/GPIO25", "domain": "COMPUTE", "source_count": "NO INDEPENDENT SIGNAL-SIDE SUPPLY SHOWN", "state": "TOPOLOGY PROVED; MARGIN/FAULT APPROVAL OPEN", "warning": WARNING},
        {"path_id": "ISO-01", "from": "four 24 V field-status inputs", "through": "ISO1212 isolation barriers", "to": "four compute-side output buffers", "domain": "FIELD TO COMPUTE", "source_count": "NO CONDUCTIVE DC PATH CLAIMED BY SCHEMATIC", "state": "COMPONENT TOPOLOGY PROVED; PHYSICAL ISOLATION/LEAKAGE TEST OPEN", "warning": WARNING},
        {"path_id": "ABSENT-01", "from": "5 V / USB-C", "through": "none", "to": "R202/R204 observation interface", "domain": "COMPUTE", "source_count": "NO 5 V NET IN R202/R204 OBSERVATION PATH", "state": "NATIVE-NETLIST ABSENCE PROVED", "warning": WARNING},
    ]
    write_csv(ENG / "topology-register.csv", topology)

    ic_quiescent_ma = 2 * 1.9
    high_load_each_ma = 3.3 / (1000 + 10000) * 1000
    high_load_total_ma = 4 * high_load_each_ma
    total_ma = ic_quiescent_ma + high_load_total_ma
    cap_energy_uj = 0.5 * 200e-9 * 3.3**2 * 1e6
    load_budget = [
        {"item": "two ISO1212 VCC1 quiescent maxima", "formula": "2 x 1.9 mA", "result": f"{ic_quiescent_ma:.2f} mA", "evidence": "TI SLLSEY7G ICC1 max", "status": "SOURCE SCREEN", "warning": WARNING},
        {"item": "four simultaneous high-state pulldown loads", "formula": "4 x 3.3 V / (1.00 kohm + 10.0 kohm)", "result": f"{high_load_total_ma:.2f} mA", "evidence": "R202 exact resistor candidates", "status": "WORST-STATE SCREEN", "warning": WARNING},
        {"item": "screened steady external 3V3 load", "formula": "3.80 mA + 1.20 mA", "result": f"{total_ma:.2f} mA", "evidence": "excludes Pi GPIO leakage and tolerance effects", "status": "NOT PI 5 HEADER-LOAD APPROVAL", "warning": WARNING},
        {"item": "installed decoupling", "formula": "2 x 100 nF", "result": "200 nF", "evidence": "R202 CDEC1/CDEC2", "status": "SOURCE SCREEN", "warning": WARNING},
        {"item": "stored energy at 3.3 V", "formula": "0.5 x 200 nF x 3.3^2", "result": f"{cap_energy_uj:.3f} uJ", "evidence": "ideal capacitor screen", "status": "NOT INRUSH OR RAIL-STABILITY APPROVAL", "warning": WARNING},
        {"item": "Pi 5 header 3V3 continuous/inrush allowance", "formula": "manufacturer value required", "result": "SELECTION REQUIRED", "evidence": "not located in current official Pi 5 records", "status": "BLOCKER", "warning": WARNING},
    ]
    write_csv(ENG / "load-budget.csv", load_budget)

    high_floor_v = 2.6 * 10000 / 11000
    short_nom_ma = 3.3 / 1000 * 1000
    short_tol_ma = 3.3 / 990 * 1000
    margins = [
        {"case": "logic high source-side floor", "formula": "(3.0 V - 0.4 V) x 10.0k/(1.0k+10.0k)", "result": f"{high_floor_v:.3f} V", "limit": "Pi 5/RP1 VIH not published in controlled source", "disposition": "MARGIN NOT CLOSED", "warning": WARNING},
        {"case": "logic low source-side ceiling", "formula": "TI VOL maximum at specified load; external pulldown assists low", "result": "<=0.400 V before unknown Pi leakage", "limit": "Pi 5/RP1 VIL and leakage not published in controlled source", "disposition": "MARGIN NOT CLOSED", "warning": WARNING},
        {"case": "signal hard-short to COMPUTE_0V; nominal RSO", "formula": "3.3 V / 1.00 kohm", "result": f"{short_nom_ma:.3f} mA", "limit": "TI recommended IOH magnitude 3 mA at 3.3 V", "disposition": "BLOCKER - EXCEEDS RECOMMENDED OPERATING CURRENT", "warning": WARNING},
        {"case": "signal hard-short to COMPUTE_0V; RSO at -1%", "formula": "3.3 V / 0.990 kohm", "result": f"{short_tol_ma:.3f} mA", "limit": "TI recommended IOH magnitude 3 mA at 3.3 V", "disposition": "BLOCKER - RSO VALUE/FAULT STRATEGY MUST CHANGE", "warning": WARNING},
        {"case": "signal hard-short to PI_3V3 while ISO output low", "formula": "source tolerance and output clamp data required", "result": "SELECTION REQUIRED", "limit": "TI +/-3 mA recommended output current; Pi rail tolerance absent", "disposition": "FAULT CURRENT NOT CLOSED", "warning": WARNING},
    ]
    write_csv(ENG / "signal-margin-screen.csv", margins)

    states = [
        {"state_id": "OFF", "pi_5v": "absent", "pi_3v3": "absent", "field_24v": "absent", "ti_output_basis": "VCC1 powered down; output not usable", "expected_observation": "none", "authority": "NONE", "evidence_state": "SOURCE DESCRIPTION ONLY", "warning": WARNING},
        {"state_id": "FIELD_ONLY", "pi_5v": "absent", "pi_3v3": "absent", "field_24v": "present", "ti_output_basis": "VCC1 powered down; TI says output undetermined", "expected_observation": "Pi off; no diagnostic value; no DC-source inference across isolation", "authority": "NONE", "evidence_state": "NO-BACKFEED MEASUREMENT REQUIRED", "warning": WARNING},
        {"state_id": "STANDBY", "pi_5v": "present", "pi_3v3": "absent", "field_24v": "either", "ti_output_basis": "VCC1 powered down; output undetermined", "expected_observation": "Pi/RP1 not active; external circuit must tolerate state", "authority": "NONE", "evidence_state": "HAT+ DESIGN CRITERION; PHYSICAL TEST OPEN", "warning": WARNING},
        {"state_id": "RAMP", "pi_5v": "present", "pi_3v3": "0 through active", "field_24v": "either", "ti_output_basis": "undetermined below/through UVLO; assumes input state after power-up", "expected_observation": "ignore until host preflight and stable input evidence", "authority": "NONE", "evidence_state": "OSCILLOSCOPE/BOOT TRACE REQUIRED", "warning": WARNING},
        {"state_id": "ACTIVE_FIELD_OFF", "pi_5v": "present", "pi_3v3": "present", "field_24v": "absent", "ti_output_basis": "VCC1 powered; open field input maps low", "expected_observation": "four low diagnostic inputs", "authority": "DIAGNOSTIC ONLY", "evidence_state": "SOURCE EXPECTATION; HIL OPEN", "warning": WARNING},
        {"state_id": "ACTIVE_FIELD_ON", "pi_5v": "present", "pi_3v3": "present", "field_24v": "present", "ti_output_basis": "outputs follow four isolated field input states", "expected_observation": "active-high diagnostics after timing/filter qualification", "authority": "DIAGNOSTIC ONLY", "evidence_state": "SOURCE EXPECTATION; HIL OPEN", "warning": WARNING},
        {"state_id": "WARM_STANDBY", "pi_5v": "present", "pi_3v3": "present", "field_24v": "either", "ti_output_basis": "R202 remains electrically powered while software is halted", "expected_observation": "no software consumer; signals may retain field state", "authority": "NONE", "evidence_state": "SHUTDOWN/RESTART TRACE REQUIRED", "warning": WARNING},
    ]
    write_csv(ENG / "power-state-matrix.csv", states)

    faults = [
        {"fault_id": "FLT-01", "fault": "W14001 3V3 open", "source_prediction": "R202 VCC1 removed; outputs not trustworthy", "required_safe_response": "host observation invalid; heartbeat/motion authority absent", "closure": "OPEN - CABLE FAULT HIL", "warning": WARNING},
        {"fault_id": "FLT-02", "fault": "W14002 return open", "source_prediction": "logic reference lost; all observations invalid", "required_safe_response": "host observation invalid; no automatic recovery", "closure": "OPEN - CABLE FAULT HIL", "warning": WARNING},
        {"fault_id": "FLT-03", "fault": "one signal open", "source_prediction": "R202 10k pulldown is before harness; Pi-side open may float/pull by RP1", "required_safe_response": "diagnostic discrepancy detected; no safety credit", "closure": "OPEN - TARGET PULL/FAULT HIL", "warning": WARNING},
        {"fault_id": "FLT-04", "fault": "one signal short to return", "source_prediction": "low; present 1k candidate permits 3.30-3.33 mA source current", "required_safe_response": "remain within component recommended operation and flag discrepancy", "closure": "BLOCKER - RSO/FAULT STRATEGY REVISION", "warning": WARNING},
        {"fault_id": "FLT-05", "fault": "one signal short to 3V3", "source_prediction": "forced high; low-driving ISO output current unresolved", "required_safe_response": "remain within component limits and flag discrepancy", "closure": "OPEN - SOURCE TOLERANCE/FAULT HIL", "warning": WARNING},
        {"fault_id": "FLT-06", "fault": "signal-to-signal cross-short", "source_prediction": "two diagnostics coupled; opposing-output current path through two RSO", "required_safe_response": "bounded current plus discrepancy", "closure": "OPEN - WORST-CASE CALCULATION/HIL", "warning": WARNING},
        {"fault_id": "FLT-07", "fault": "field on while Pi in STANDBY/off", "source_prediction": "no conductive intended source across barrier; VCC1/output state still undetermined", "required_safe_response": "no Pi back-power and no false work authority", "closure": "OPEN - LEAKAGE/BACK-POWER TEST", "warning": WARNING},
        {"fault_id": "FLT-08", "fault": "Pi brownout or 3V3 ramp dwell", "source_prediction": "ISO outputs undetermined through UVLO region", "required_safe_response": "observation invalid; heartbeat removed; fresh restart sequence", "closure": "OPEN - BROWNOUT TRACE/HIL", "warning": WARNING},
    ]
    write_csv(ENG / "fault-matrix.csv", faults)

    questions = [
        {"question_id": "RFI-001", "addressee": "Raspberry Pi", "question": "For Raspberry Pi 5 SC1112, what continuous, transient/inrush and ambient-derated external load is permitted from physical pin 17/3V3, including board-revision conditions?", "reason": "5.00 mA steady screen and 200 nF load cannot be approved without a Pi 5 header-rail limit", "sent": "NO", "answer": "OPEN", "warning": WARNING},
        {"question_id": "RFI-002", "addressee": "Raspberry Pi", "question": "Publish or identify Pi 5/RP1 GPIO VIH, VIL, leakage, capacitance, clamp/injection-current and unpowered-pin limits for GPIO22-25.", "reason": "direct-input high/low and fault margins cannot close from current RP1 register documentation", "sent": "NO", "answer": "OPEN", "warning": WARNING},
        {"question_id": "RFI-003", "addressee": "Raspberry Pi", "question": "What leakage or applied-voltage limits ensure no back-power through 3V3 or GPIO pins in OFF, STANDBY and rail-ramp states?", "reason": "HAT+ defines compatibility obligation but not quantitative limits for this non-HAT+ topology", "sent": "NO", "answer": "OPEN", "warning": WARNING},
        {"question_id": "RFI-004", "addressee": "Raspberry Pi", "question": "Does the exact passive carrier plus separately mounted, Pi-3V3-powered ISO1212 receiver require additional sequencing, buffering or protection for Pi 5?", "reason": "application review is absent", "sent": "NO", "answer": "OPEN", "warning": WARNING},
        {"question_id": "RFI-005", "addressee": "Texas Instruments", "question": "Provide ISO1212 OUT leakage/clamp behavior with VCC1 unpowered or between 1.7 V and 2.25 V while field inputs are energized and external 10k pulldowns are present.", "reason": "datasheet marks output undetermined; back-power/false-state calculation cannot infer more", "sent": "NO", "answer": "OPEN", "warning": WARNING},
        {"question_id": "RFI-006", "addressee": "Texas Instruments", "question": "Confirm an output-series resistance/current envelope that keeps hard shorts within recommended operation at the actual Pi 3V3 tolerance while preserving Pi 5 input margin.", "reason": "present 1.00k candidate screens above the 3mA recommended output-current magnitude", "sent": "NO", "answer": "OPEN", "warning": WARNING},
    ]
    write_csv(ENG / "manufacturer-question-register.csv", questions)

    hold_topics = [
        "Pi 5 SC1112 physical pin 17 continuous/inrush/ambient load approval",
        "Pi 5/RP1 GPIO22-25 VIH/VIL/leakage/clamp/injection limits",
        "RSO1-RSO4 value/fault strategy revision keeping shorts within recommended operation",
        "recalculated high/low margins after RSO revision and exact cable DCR/length",
        "OFF/STANDBY/WARM_STANDBY/ramp power-state leakage and no-backfeed evidence",
        "received Pi and R202/R204 identities plus exact board revisions",
        "3V3 rail droop, ripple, inrush and brownout traces at temperature",
        "GPIO startup pull, ownership and stable-readback timing on the released image",
        "open/short/cross-short/source-loss/return-loss current and response evidence",
        "isolation, EMC, ESD and cable transient evidence on assembled hardware",
        "qualified electrical/compute application review",
        "separate written authorization for any connection or powered test",
    ]
    holds = [{"hold_id": f"OCP-HOLD-{index:03d}", "topic": topic, "state": "OPEN - SELECTION/EVIDENCE REQUIRED", "evidence_uri": "", "warning": WARNING} for index, topic in enumerate(hold_topics, 1)]
    write_csv(ENG / "selection-holds.csv", holds)

    acceptance_topics = [
        "received PI1/R202/R204 identity and revision record", "unpowered topology continuity and isolation", "Pi OFF plus field OFF leakage",
        "Pi OFF/STANDBY plus field ON back-power voltage/current", "Pi ACTIVE plus field OFF four-low readback", "Pi ACTIVE plus field ON four-channel truth table",
        "3V3 steady load/droop/ripple", "3V3 startup inrush and ramp", "Pi brownout/shutdown/restart trace", "each signal open fault",
        "each signal short-to-return fault", "each signal short-to-3V3 fault", "signal cross-short fault", "qualified review and separate test authorization",
    ]
    acceptance = [{"test_id": f"OCP-ACC-{index:03d}", "test": topic, "procedure": "SELECTION REQUIRED", "instrument": "SELECTION REQUIRED", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING} for index, topic in enumerate(acceptance_topics, 1)]
    write_csv(ENG / "acceptance-matrix.csv", acceptance)

    status = {
        "schema": "project-button-observation-compute-power-boundary-v1", "identifier": IDENTIFIER, "round": ROUND, "date": DATE,
        "topology_rows": len(topology), "source_rows": len(source_register), "power_state_rows": len(states), "fault_rows": len(faults),
        "manufacturer_questions": len(questions), "selection_holds": len(holds), "acceptance_rows": len(acceptance),
        "steady_load_screen_ma": round(total_ma, 2), "source_high_floor_screen_v": round(high_floor_v, 3),
        "short_current_nominal_ma": round(short_nom_ma, 3), "short_current_rso_minus_1pct_ma": round(short_tol_ma, 3),
        "ti_recommended_output_current_ma": 3.0, "rso_fault_current_blocker": True,
        "pi_header_3v3_load_accepted": False, "pi_gpio_dc_limits_accepted": False, "signal_margin_accepted": False,
        "back_power_accepted": False, "partial_power_behavior_accepted": False, "rso_selection_released": False,
        "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False,
        "source_hashes": {name: digest(path) for name, path in source_paths.items()}, "warning": WARNING,
    }
    write(ENG / "package-status.json", json.dumps(status, indent=2) + "\n")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 620" role="img" aria-labelledby="title desc"><title id="title">Observation compute power boundary</title><desc id="desc">Pi 3V3 powers two ISO1212 devices; four diagnostic outputs pass through series resistors to Pi GPIO. Physical and fault evidence remains open.</desc><style>text{{font-family:system-ui,sans-serif;fill:#082b55}}.h{{font-size:28px;font-weight:800}}.m{{font-size:18px;font-weight:700}}.s{{font-size:15px}}.b{{fill:#eef8ff;stroke:#0b4f8a;stroke-width:3}}.p{{fill:#fff4c2;stroke:#a06a00;stroke-width:3}}.x{{fill:#ffe5e5;stroke:#a82323;stroke-width:3}}.line{{fill:none;stroke:#0b4f8a;stroke-width:7}}</style><text x="40" y="45" class="h">Pi 5 observation power and partial-power boundary</text><rect x="40" y="90" width="240" height="180" rx="16" class="b"/><text x="70" y="135" class="m">PI1 / SC1112</text><text x="70" y="175" class="s">pin 17: 3V3 source</text><text x="70" y="205" class="s">pin 20: return</text><text x="70" y="235" class="s">GPIO22-25 inputs</text><rect x="470" y="90" width="260" height="180" rx="16" class="b"/><text x="500" y="135" class="m">R202 receiver</text><text x="500" y="175" class="s">2 x ISO1212</text><text x="500" y="205" class="s">4 x 1k series</text><text x="500" y="235" class="s">4 x 10k fail-low</text><rect x="900" y="90" width="240" height="180" rx="16" class="b"/><text x="930" y="135" class="m">24 V field</text><text x="930" y="175" class="s">4 diagnostic inputs</text><text x="930" y="205" class="s">isolated; zero safety credit</text><path d="M280 140 H470" class="line"/><text x="315" y="125" class="s">3V3 / return</text><path d="M470 220 H280" class="line"/><text x="310" y="250" class="s">4 GPIO inputs</text><path d="M900 180 H730" class="line"/><text x="765" y="165" class="s">isolation barrier</text><rect x="40" y="320" width="520" height="110" rx="14" class="p"/><text x="70" y="360" class="m">Source-bounded screens</text><text x="70" y="392" class="s">steady 3V3 load: {total_ma:.2f} mA; high floor: {high_floor_v:.3f} V</text><text x="70" y="416" class="s">Neither is Pi 5 application approval.</text><rect x="590" y="320" width="550" height="110" rx="14" class="x"/><text x="620" y="360" class="m">BLOCKER: present 1.00k series candidate</text><text x="620" y="392" class="s">hard-short screen: {short_nom_ma:.2f} to {short_tol_ma:.2f} mA</text><text x="620" y="416" class="s">TI recommended operation: 3.00 mA at 3.3 V</text><rect x="40" y="475" width="1100" height="100" rx="14" class="p"/><text x="65" y="515" class="m">Pi 5 header-load, GPIO DC limits, back-power, ramp behavior and physical evidence remain OPEN.</text><text x="65" y="550" class="s">{WARNING}</text></svg>'''
    write(ENG / "power-boundary.svg", svg)

    state_json = json.dumps([{key: row[key] for key in ("state_id", "pi_5v", "pi_3v3", "field_24v", "ti_output_basis", "expected_observation", "authority", "evidence_state")} for row in states])
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R208 observation compute-power boundary</title><style>:root{{--sky:#dff3ff;--blue:#082b55;--gold:#f5bd21;--paper:#f8fbfd;--red:#a82323}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--blue);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:5px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning,.blocker{{padding:18px;border:3px solid;font-weight:800}}.warning{{background:#fff4c2;border-color:#9c6800}}.blocker{{background:#ffe5e5;border-color:var(--red)}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card,.state{{padding:20px;background:white;border:2px solid #8db8d9;border-radius:14px}}.card b{{font-size:30px;display:block}}img{{width:100%;height:auto;background:white;border:2px solid #8db8d9;border-radius:14px}}label{{display:block;font-weight:800;margin-bottom:8px}}select{{width:100%;font:inherit;padding:12px;border:2px solid #0b4f8a;border-radius:8px;background:white;color:var(--blue)}}.state-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:16px}}.state-grid div{{padding:12px;background:#eef8ff;border-radius:8px}}.state-grid b{{display:block}}.scroll{{overflow:auto;border:2px solid #8db8d9;border-radius:12px;background:white}}table{{width:100%;border-collapse:collapse;min-width:880px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid #b8d2e5;font-size:14px}}th{{background:var(--blue);color:white}}a{{color:#075ea8}}@media(max-width:520px){{header,main{{padding:18px}}th,td{{font-size:14px}}}}</style></head><body><header><p>Project Button - R208 controlled engineering guide</p><h1>The topology is bounded. The Pi 5 guarantee is not.</h1><p class="warning">{WARNING}</p></header><main><div class="cards"><div class="card"><b>{total_ma:.2f} mA</b>steady 3V3 source-load screen</div><div class="card"><b>{high_floor_v:.3f} V</b>source-side high floor, not Pi margin</div><div class="card"><b>{short_tol_ma:.3f} mA</b>hard-short screen at RSO -1%</div><div class="card"><b>0</b>physical acceptance results</div></div><p class="blocker">BLOCKER: the existing 1.00 kohm RSO candidate does not bound a 3.3 V hard short within TI's +/-3 mA recommended output-current envelope. RSO and the resulting Pi input margin require correction and review.</p><h2>Connected topology</h2><img src="power-boundary.svg" alt="Pi 5 observation power, isolation and GPIO signal topology"><h2>Explore partial-power states</h2><section class="state"><label for="state-select">Power state</label><select id="state-select"></select><div class="state-grid"><div><b>Pi 5 V</b><span id="pi5"></span></div><div><b>Pi 3V3</b><span id="pi33"></span></div><div><b>Field 24 V</b><span id="field"></span></div><div><b>Authority</b><span id="authority"></span></div></div><p><b>TI output basis:</b> <span id="ti"></span></p><p><b>Expected observation:</b> <span id="obs"></span></p><p><b>Evidence:</b> <span id="evidence"></span></p></section><h2>Signal and fault screens</h2>{table(margins,["case","formula","result","limit","disposition"])}<h2>Open manufacturer questions</h2>{table(questions,["question_id","addressee","question","reason","sent","answer"])}<h2>Acceptance remains blank</h2>{table(acceptance,["test_id","test","execution_state","result","evidence_uri","approver"])}<p><a href="source-register.csv">Primary-source register</a> - <a href="power-state-matrix.csv">Power-state matrix</a> - <a href="fault-matrix.csv">Fault matrix</a> - <a href="selection-holds.csv">Open holds</a></p></main><script>const states={state_json};const select=document.getElementById('state-select');for(const s of states){{const o=document.createElement('option');o.value=s.state_id;o.textContent=s.state_id;select.appendChild(o)}}function render(){{const s=states.find(x=>x.state_id===select.value);document.getElementById('pi5').textContent=s.pi_5v;document.getElementById('pi33').textContent=s.pi_3v3;document.getElementById('field').textContent=s.field_24v;document.getElementById('authority').textContent=s.authority;document.getElementById('ti').textContent=s.ti_output_basis;document.getElementById('obs').textContent=s.expected_observation;document.getElementById('evidence').textContent=s.evidence_state}}select.addEventListener('change',render);render();</script></body></html>'''
    write(ENG / "index.html", page)
    write(ENG / "README.md", f"# {IDENTIFIER}\n\n**{WARNING}**\n\nR208 source-bounds the R202/R204/P1.16 observation compute-power topology, steady-load and signal screens, partial-power states, faults, manufacturer questions and blank acceptance evidence. It identifies a present RSO short-current blocker and does not release a circuit, harness, connection or powered test.\n")

    for path in ENG.iterdir():
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            shutil.copy2(path, WEB / path.name)
    manifest(ENG)
    manifest(WEB)
    write(DOC, f"# R208 observation compute-power boundary\n\n**{WARNING}**\n\n`{IDENTIFIER}` proves the intended one-source 3V3 topology and records source-bounded load, signal and partial-power screens. It also identifies that the current 1.00 kohm RSO candidate permits a 3.30-3.33 mA hard-short screen against TI's 3 mA recommended output-current envelope. Pi 5 header-load limits, RP1 GPIO DC limits, RSO correction, back-power, ramp, physical tests and qualified review remain open.\n")
    print(f"Generated {IDENTIFIER}: {len(states)} power states / {len(faults)} faults / {len(holds)} holds / {len(acceptance)} open acceptance rows")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
