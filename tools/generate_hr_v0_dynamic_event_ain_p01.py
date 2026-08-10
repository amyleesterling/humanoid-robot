#!/usr/bin/env python3
"""Generate the R177 low-loading isolated event-voltage acquisition candidate."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/dynamic-event-ain-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-dynamic-event-ain-p0.1"
WEB = ROOT / "release/hr-v0/dynamic-event-ain-p0.1"
FORM = ROOT / "tests/forms/hr-v0-dynamic-event-ain-receiving-template-p0.1.csv"
PROJECT = "hr-v0-dynamic-event-ain-p0.1"
IDENTIFIER = "HR-V0-DYN-EVENT-AIN-P0.1"
REV = "R177 / P0.1"
WARNING = "PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")


CHANNELS = [
    ("DEA-001", "SR1_S12", "S0 channel-1 return", "DCH-014", "EVM1", "AIN0-AIN1", "DB37-37/18"),
    ("DEA-002", "SR1_START_RETURN", "manual RESET return", "DCH-X01", "EVM2", "AIN2-AIN3", "DB37-36/17"),
    ("DEA-003", "ARM_AFTER_S2", "manual ARM/start return", "DCH-X02", "EVM3", "AIN4-AIN5", "DB37-35/16"),
    ("DEA-004", "K1_A1", "K1 coil command", "DCH-008", "EVM4", "AIN6-AIN7", "DB37-34/15"),
    ("DEA-005", "K2_A1", "K2 coil command", "DCH-009", "EVM5", "AIN8-AIN9", "DB37-33/14"),
    ("DEA-006", "EDM_K1_OUT", "K1 mirror-contact chain", "DCH-010", "EVM6", "AIN10-AIN11", "DB37-32/13"),
    ("DEA-007", "SRA1_START_RETURN", "K2 mirror-contact chain", "DCH-011", "EVM7", "AIN12-AIN13", "DB37-31/12"),
]

HOLDS = [
    ("DAH-001", "FIELD ENVELOPE", "Per-node minimum, nominal, maximum, reverse and transient voltage at the intended tap under normal and single-fault conditions"),
    ("DAH-002", "DIVIDER", "Exact resistor-divider ratio, values, tolerance, voltage rating, pulse rating, creepage, clearance and dissipation; no value released"),
    ("DAH-003", "PROTECTION", "Exact input current limiting, surge, reverse, open-component and short-component behavior; no protection part released"),
    ("DAH-004", "NONINTERFERENCE", "Accepted maximum parallel load for every Pilz, reset/start, EDM and coil node plus tap-present/tap-absent waveform evidence"),
    ("DAH-005", "EVM INTENDED USE", "Seven received AMC3330EVM units restricted to guarded bench R&D; TI says the board is not certified for high-voltage operation"),
    ("DAH-006", "INPUT WIRING", "Exact field adapter and tie of EVM J2.2 INN to J2.3 HGND; direct 24 V-class connection to J2 is prohibited"),
    ("DAH-007", "LOGIC POWER", "Exact 3.0 V to 5.5 V bench source, current budget, fusing, connector and seven-channel common-return arrangement"),
    ("DAH-008", "DAQ CONFIG", "T7 ±10 V range, resolution index, settling, scan order, connection type, buffer and overflow policy frozen on received hardware"),
    ("DAH-009", "SEQUENTIAL SKEW", "Measured channel order and first-to-last skew; T7 is sequential, not simultaneous"),
    ("DAH-010", "THRESHOLDS", "Per-channel analog-to-event thresholds, hysteresis, pulse-width rejection and fail-safe treatment validated from physical traces"),
    ("DAH-011", "TRIGGER", "Exact isolated/buffered FIO0 trigger witness interface; no camera pinout inferred"),
    ("DAH-012", "HARNESS", "Exact mating parts, wire, shielding, segregation, strain relief, guarding and labels"),
    ("DAH-013", "CALIBRATION", "Received EVM/T7 identities, offset/gain characterization, timebase verification and traceable calibration evidence"),
    ("DAH-014", "FAULT INJECTION", "Open, short, stuck, divider-component, field-return, logic-power, DAQ and host failures executed with zero safety credit"),
    ("DAH-015", "QUALIFIED REVIEW", "Qualified electrical and functional-safety reviewers accept the connection plan and a separate controlled work authorization is issued"),
]

SOURCES = [
    ("DAS-001", "Texas Instruments", "AMC3330 datasheet", "SBASA34B", "June 2020; revised August 2024", "https://www.ti.com/lit/ds/symlink/amc3330.pdf", "±1 V linear differential input; 0.1 GΩ minimum single-ended/differential input resistance; gain 2; 1.39 V to 1.49 V output common mode; 300 kHz minimum bandwidth"),
    ("DAS-002", "Texas Instruments", "AMC3301/AMC3302/AMC3330 EVM user guide", "SBAU330C", "June 2019; revised January 2022", "https://www.ti.com/lit/pdf/SBAU330", "J2.1 INP, J2.2 INN, J2.3 HGND; J3.1 OUTN, J3.2 OUTP, J3.3 GND; J1.1 VDD, J1.2 GND; EVM not certified for high-voltage operation"),
    ("DAS-003", "Texas Instruments", "AMC3330 product page", "live page", "accessed 2026-08-10", "https://www.ti.com/product/AMC3330", "ACTIVE product status and AMC3330EVM identity"),
    ("DAS-004", "LabJack", "T7 analog inputs", "live web datasheet", "accessed 2026-08-10", "https://support.labjack.com/docs/14-3-0-analog-inputs-t7-t-series-datasheet", "Fourteen AINs form seven adjacent even-positive/odd-negative differential pairs; AIN0-AIN3 duplicate-terminal warning; multiplexed acquisition"),
    ("DAS-005", "LabJack", "T-Series stream mode", "live web datasheet", "accessed 2026-08-10", "https://support.labjack.com/docs/3-2-stream-mode-t-series-datasheet", "Scan framing, FIO_STATE streamability, and T7 sequential rather than simultaneous sampling"),
    ("DAS-006", "LabJack", "T7 stream data rates", "live web datasheet", "accessed 2026-08-10", "https://support.labjack.com/docs/a-1-1-stream-data-rates-t-series-datasheet", "100 ksamples/s typical maximum only under stated range/resolution conditions; scan rate equals sample rate divided by address count"),
    ("DAS-007", "LabJack", "T7 DB37 pinout", "live web datasheet", "accessed 2026-08-10", "https://support.labjack.com/docs/16-0-db37-t7-only-t-series-datasheet", "Exact AIN0-AIN13, FIO0, VS and GND DB37 pins"),
]


def write_csv(path: Path, header: list[str], rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("event_ain_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = "2026-08-10"
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 LOW-LOADING ISOLATED EVENT ACQUISITION"
    model.PROJECT_SUBTITLE = "BENCH R&D ONLY; FIELD DIVIDER/PROTECTION SELECTION REQUIRED; ZERO SAFETY CREDIT"
    return model


def build_ecad() -> None:
    model = load_model()
    pn, Component = model.pn, model.Component

    def adapter_and_evm(index: int, y: float):
        _, field_net, label, _, evm_ref, pair, _ = CHANNELS[index - 1]
        adapter = Component(f"ADP{index}", "FIELD DIVIDER + PROTECTION - SELECTION REQUIRED", [
            pn(f"ADP{index}", "FIELD", label.upper(), f"{field_net}_TAP_HELD", "left"),
            pn(f"ADP{index}", "INP", "SCALED OUTPUT", f"CH{index}_INP_HELD", "right"),
            pn(f"ADP{index}", "RETURN", "FIELD RETURN", f"CH{index}_RETURN_HELD", "right"),
        ], "NO PARTS / NO VALUES / CONNECTION PROHIBITED", "Field envelope, divider, protection and fault behavior remain SELECTION REQUIRED.", "No manufacturer selected", "Logical boundary only; not buildable hardware.", position=(70, y), width=66)
        evm = Component(evm_ref, "TI AMC3330EVM - EXACT EVALUATION CANDIDATE", [
            pn(evm_ref, "J2.1", "INP", f"CH{index}_INP_HELD", "left"),
            pn(evm_ref, "J2.2", "INN", f"CH{index}_RETURN_HELD", "left"),
            pn(evm_ref, "J2.3", "HGND", f"CH{index}_RETURN_HELD", "left"),
            pn(evm_ref, "J3.2", "OUTP", f"CH{index}_OUTP", "right"),
            pn(evm_ref, "J3.1", "OUTN", f"CH{index}_OUTN", "right"),
            pn(evm_ref, "J3.3", "GND", "DAQ_GND", "right"),
            pn(evm_ref, "J1.1", "VDD", "EVM_VDD_SELECTION_REQUIRED", "right"),
            pn(evm_ref, "J1.2", "GND", "DAQ_GND", "right"),
        ], "NOT SELECTED / BENCH R&D ONLY", f"Output candidate for T7 {pair}. Direct 24 V-class input is prohibited.", "TI SBAU330C", "Board is not certified for high-voltage operation.", position=(230, y), width=70)
        return adapter, evm

    sheets = []
    for sheet_no, group in ((1, range(1, 4)), (2, range(4, 6)), (3, range(6, 8))):
        comps = []
        y_positions = [50, 100, 150] if len(group) == 3 else [75, 145]
        for index, y in zip(group, y_positions):
            comps.extend(adapter_and_evm(index, y))
        sheet = model.Sheet(sheet_no, f"0{sheet_no}_field_and_evm_{sheet_no}.kicad_sch", f"Held field adapters and AMC3330EVM channels {min(group)}-{max(group)}", "Exact EVM terminals; no divider/protection values or field connection released.", compact=True)
        sheet.components = comps
        sheet.notes = []
        sheets.append(sheet)

    def evm_logic(index: int, y: float):
        _, _, _, _, evm_ref, pair, pins = CHANNELS[index - 1]
        return Component(f"{evm_ref}L", f"{evm_ref} LOGIC OUTPUT", [
            pn(f"{evm_ref}L", "J3.2", "OUTP", f"CH{index}_OUTP", "right"),
            pn(f"{evm_ref}L", "J3.1", "OUTN", f"CH{index}_OUTN", "right"),
            pn(f"{evm_ref}L", "J3.3/J1.2", "GND", "DAQ_GND", "right"),
            pn(f"{evm_ref}L", "J1.1", "VDD", "EVM_VDD_SELECTION_REQUIRED", "right"),
        ], "NOT SELECTED / ZERO SAFETY CREDIT", f"Candidate drives {pair} at {pins}.", "TI SBAU330C / LabJack T7 DB37", "Exact output pins; power source still held.", position=(60, y), width=58)

    pair_pins = [("AIN0", "37", "AIN1", "18"), ("AIN2", "36", "AIN3", "17"), ("AIN4", "35", "AIN5", "16"), ("AIN6", "34", "AIN7", "15"), ("AIN8", "33", "AIN9", "14"), ("AIN10", "32", "AIN11", "13"), ("AIN12", "31", "AIN13", "12")]
    t7_pins = [pn("DAQ1", f"DB37-{p_pin}", p, f"CH{i}_OUTP", "left") for i, (p, p_pin, _, _) in enumerate(pair_pins, 1)]
    t7_pins += [pn("DAQ1", f"DB37-{n_pin}", n, f"CH{i}_OUTN", "left") for i, (_, _, n, n_pin) in enumerate(pair_pins, 1)]
    t7_pins += [pn("DAQ1", "DB37-6", "FIO0 TRIGGER WITNESS", "COMMON_TRIGGER_LOGIC_HELD", "right"), pn("DAQ1", "DB37-1", "GND", "DAQ_GND", "left")]
    t7 = Component("DAQ1", "LABJACK T7 + CB37 - EXACT EVALUATION CANDIDATES", t7_pins, "NOT SELECTED / ZERO SAFETY CREDIT", "Seven adjacent differential pairs; eight-address scan includes FIO_STATE. Sequential, not simultaneous.", "LabJack live T-Series datasheet accessed 2026-08-10", "AIN0-AIN3 duplicate terminals may not be used simultaneously.", position=(235, 110), width=74)
    left = [evm_logic(i, 50 + (i - 1) * 38) for i in range(1, 5)]
    sheet4 = model.Sheet(4, "04_logic_outputs_1_4.kicad_sch", "AMC3330EVM outputs to T7 pairs 0-7", "Exact output/DB37 pins; common logic power and calibration open.", compact=True)
    sheet4.components = [*left, t7]
    sheet4.notes = []
    right = [evm_logic(i, 50 + (i - 5) * 50) for i in range(5, 8)]
    capture = Component("DAQCFG1", "T7 STREAM CONFIGURATION - SELECTION REQUIRED", [
        pn("DAQCFG1", "A0", "AIN8-9", "CH5_OUTP", "left"), pn("DAQCFG1", "A1", "AIN10-11", "CH6_OUTP", "left"),
        pn("DAQCFG1", "A2", "AIN12-13", "CH7_OUTP", "left"), pn("DAQCFG1", "D0", "FIO_STATE", "COMMON_TRIGGER_LOGIC_HELD", "left"),
    ], "NO RUN CONFIGURATION RELEASED", "Eight addresses per scan: seven AIN readings plus FIO_STATE. Scan order, rate, thresholds and overflow policy remain open.", "LabJack live stream docs accessed 2026-08-10", "12.5 kscan/s is an upper screen only under stated 100 ksamples/s conditions.", position=(230, 115), width=72)
    sheet5 = model.Sheet(5, "05_logic_outputs_5_7_and_capture.kicad_sch", "AMC3330EVM outputs 5-7 and sequential capture boundary", "Exact output allocation; scan configuration and timing evidence open.", compact=True)
    sheet5.components = [*right, capture]
    sheet5.notes = []
    sheets.extend([sheet4, sheet5])

    items = [component for sheet in sheets for component in sheet.components]
    counts = Counter(pin.net for component in items for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    root_uuid = model.uid("root-hr-v0-dynamic-event-ain-p01")
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 isolated analog event candidate"))\n)\n', encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["reference", "terminal", "function", "net", "state"], [(component.ref, pin.number, pin.name, pin.net, component.status) for component in items for pin in component.pins])
    write_csv(ECAD / "bom.csv", ["reference", "manufacturer", "part_number", "quantity", "state"], [
        ("EVM1-EVM7", "Texas Instruments", "AMC3330EVM", "7", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("DAQ1", "LabJack", "T7", "1", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("DAQ1 breakout", "LabJack", "CB37 Terminal Board", "1", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("ADP1-ADP7", "SELECTION REQUIRED", "SELECTION REQUIRED", "7", "NO DIVIDER OR PROTECTION RELEASED"),
    ])
    validation, output = ECAD / "validation", ECAD / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    for stale in list(output.glob("*.svg")) + list(output.glob("*.pdf")):
        stale.unlink()
    cli = KICAD_ROOT / "bin/kicad-cli.exe"
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "pdf", "--output", str(output / f"{PROJECT}-preliminary.pdf"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "svg", "--output", str(output), str(ECAD / f"{PROJECT}.kicad_sch")],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("COMMAND: " + subprocess.list2cmdline(command) + f"\nEXIT: {result.returncode}\n{result.stdout}{result.stderr}")
        if result.returncode:
            raise RuntimeError(logs[-1])
    (validation / "kicad-cli.log").write_text("\n\n".join(logs), encoding="utf-8")
    for svg in output.glob("*.svg"):
        normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n"
        svg.write_text(normalized, encoding="utf-8")
    for index, source in enumerate(sorted(output.glob("*.svg"))):
        if source.name == f"{PROJECT}.svg":
            continue
        source.rename(output / f"event-ain-{index}.svg")
    for local_settings in ECAD.glob("*.kicad_prl"):
        local_settings.unlink()
    manifest_rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            manifest_rows.append((path.relative_to(ECAD).as_posix(), str(path.stat().st_size), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    write_csv(ECAD / "SOURCE-MANIFEST.csv", ["path", "bytes", "sha256"], manifest_rows)


def write_package() -> None:
    write_csv(PKG / "candidate-bom.csv", ["item_id", "manufacturer", "part_number", "quantity", "role", "procurement_state"], [
        ("TE-009B", "Texas Instruments", "AMC3330EVM", "7", "channel-isolated voltage acquisition evaluation candidate", "NOT AUTHORIZED"),
        ("TE-001", "LabJack", "T7", "1", "sequential differential acquisition and FIO0 witness", "NOT AUTHORIZED"),
        ("TE-002", "LabJack", "CB37 Terminal Board", "1", "DB37 breakout", "NOT AUTHORIZED"),
        ("TE-009C", "SELECTION REQUIRED", "SELECTION REQUIRED", "7", "field divider/protection adapters", "NOT AUTHORIZED"),
        ("TE-009D", "SELECTION REQUIRED", "SELECTION REQUIRED", "1", "3.0 V to 5.5 V seven-EVM bench supply", "NOT AUTHORIZED"),
    ])
    write_csv(PKG / "channel-map.csv", ["channel_id", "project_net_candidate", "event", "requirement", "evm", "t7_pair", "db37_pins", "connection_state"], [(*row, "PROHIBITED - ADAPTER SELECTION REQUIRED") for row in CHANNELS])
    write_csv(PKG / "connector-map.csv", ["reference", "terminal", "signal", "destination", "state"], [
        *[(f"EVM{i}", "J2.1", "INP", f"ADP{i} scaled output", "HELD") for i in range(1, 8)],
        *[(f"EVM{i}", "J2.2/J2.3", "INN/HGND", f"ADP{i} field return", "HELD / EXTERNAL TIE REQUIRED") for i in range(1, 8)],
        *[(f"EVM{i}", "J3.2/J3.1", "OUTP/OUTN", CHANNELS[i-1][5], "EXACT OUTPUT-SIDE CANDIDATE") for i in range(1, 8)],
        *[(f"EVM{i}", "J1.1/J1.2", "VDD/GND", "bench supply / DAQ GND", "SUPPLY SELECTION REQUIRED") for i in range(1, 8)],
    ])
    write_csv(PKG / "loading-design-inputs.csv", ["input_id", "parameter", "value", "state", "closure"], [
        ("LDI-001", "AMC3330 single-ended input resistance", "0.1 Gohm minimum; 0.8 Gohm typical", "VERIFIED DEVICE PARAMETER", "TI SBASA34B Table 5-9"),
        ("LDI-002", "AMC3330 differential input resistance", "0.1 Gohm minimum; 1.2 Gohm typical", "VERIFIED DEVICE PARAMETER", "TI SBASA34B Table 5-9"),
        ("LDI-003", "AMC3330 linear input range", "-1 V to +1 V differential", "VERIFIED DEVICE PARAMETER", "TI SBASA34B"),
        ("LDI-004", "field maximum/transient envelope", "SELECTION REQUIRED", "OPEN", "measure/derive each exact node under normal and fault conditions"),
        ("LDI-005", "allowed parallel measurement current", "SELECTION REQUIRED", "OPEN", "exact Pilz/Schneider application evidence plus waveform comparison"),
        ("LDI-006", "divider/protection values", "SELECTION REQUIRED", "OPEN", "solve only after LDI-004 and LDI-005 close"),
    ])
    write_csv(PKG / "timing-budget-inputs.csv", ["input_id", "parameter", "value", "state", "closure"], [
        ("ATI-001", "T7 scan address count", "8: seven differential AIN results plus FIO_STATE", "DERIVED CANDIDATE", "freeze exact scan list and order"),
        ("ATI-002", "aggregate maximum", "100 ksamples/s typical only at ±10 V and resolution index 0 or 1", "MANUFACTURER CONDITION", "verify received hardware and transport"),
        ("ATI-003", "upper scan-rate screen", "12.5 kscan/s from 100 ksamples/s divided by 8 addresses", "DERIVED SCREEN ONLY", "not an accepted run rate"),
        ("ATI-004", "simultaneity", "T7 samples sequentially; T8 only is simultaneous in T-Series", "VERIFIED ARCHITECTURE LIMIT", "measure installed channel order/skew"),
        ("ATI-005", "AMC3330 bandwidth", "300 kHz minimum; 375 kHz typical", "VERIFIED DEVICE PARAMETER", "measure installed propagation/threshold behavior"),
        ("ATI-006", "combined uncertainty", "SELECTION REQUIRED", "OPEN", "include divider, amplifier, DAQ, threshold, clock, transport and trace analysis"),
    ])
    write_csv(PKG / "selection-holds.csv", ["hold_id", "topic", "evidence_required"], HOLDS)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "title", "document", "revision_date", "official_locator", "use"], SOURCES)
    PKG.joinpath("package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": "2026-08-10", "status": WARNING,
        "exact_new_evaluation_candidate_count": 1, "exact_new_evaluation_unit_count": 7,
        "field_event_count": 7, "differential_pair_count": 7, "scan_address_count": 8,
        "open_hold_count": len(HOLDS), "authorized_procurement_count": 0,
        "authorized_connection_count": 0, "authorized_powered_run_count": 0,
        "executed_physical_run_count": 0, "safety_function_credit": "ZERO",
        "r176_disposition": "ISO1212EVM direct-tap route retained as historical candidate but not preferred because approximately 2.25 mA typical load is unresolved",
        "release_effect": "NONE"
    }, indent=2) + "\n", encoding="utf-8")
    write_csv(FORM, ["record_id", "item", "serial_or_lot", "received_identity", "hardware_revision", "power_off_continuity", "result", "reviewer", "evidence_hash"], [
        ("RCV-AIN-001", "AMC3330EVM units 1-7", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("RCV-AIN-002", "T7 and CB37", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("RCV-AIN-003", "field adapters 1-7", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("RCV-AIN-004", "bench supply", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
    ])


def write_docs() -> None:
    ROOT.joinpath("docs/hr-v0-dynamic-event-ain-p0.1.md").write_text(f'''# HR-V0 low-loading isolated event acquisition P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Date: 2026-08-10

## Decision

Seven TI `AMC3330EVM` boards are the preferred evaluation route for observing seven separate 24 V-class safety/control events without the approximately 2.25 mA typical input load of the R176 `ISO1212EVM` candidate. Each channel has its own isolation barrier and drives one adjacent LabJack T7 differential AIN pair. The R176 direct digital-input candidate is retained as historical evidence but is not preferred for field connection.

This change does **not** make any field tap connectable. TI specifies only a ±1 V differential input for AMC3330 and warns that the EVM is not certified for high-voltage operation. Every channel therefore needs a separately engineered divider/protection adapter. Exact field envelopes, allowed parallel current, resistor values, ratings, protection, creepage, clearance and fault behavior remain `SELECTION REQUIRED`.

## Exact output-side allocation

| EVM | Project event candidate | EVM output | T7 differential pair | DB37 pins |
|---|---|---|---|---|
''' + "\n".join(f"| {row[4]} | `{row[1]}` | J3.2 OUTP / J3.1 OUTN | {row[5]} | {row[6]} |" for row in CHANNELS) + f'''

All EVM J3.3 and J1.2 logic grounds share the DAQ-side reference. EVM J1.1 requires a selected 3.0 V to 5.5 V bench supply. No T7 `VS` power-budget claim is made. AIN0-AIN3 may be connected at only one T7 terminal location because LabJack duplicates those channels internally.

## Field-side boundary

EVM J2.1 is INP. J2.2 INN must be tied externally to J2.3 HGND through the accepted input network. Direct application of a 24 V-class node to J2 is prohibited. The candidate does not assign a divider ratio, resistor value, voltage rating, surge protector or connector because the seven field envelopes and permissible node loading have not been established.

## Timing boundary

The candidate scan has eight addresses: seven differential AIN results and one `FIO_STATE` trigger-witness word. LabJack states that T7 acquisition is sequential, not simultaneous. At the manufacturer's typical 100 ksamples/s maximum under ±10 V and resolution-index 0 or 1 conditions, 12.5 kscan/s is only an arithmetic upper screen. Actual scan order, interchannel skew, settling, thresholds, overflow behavior and combined uncertainty must be frozen and measured on received hardware.

## Safety boundary

The EVMs, T7, host, thresholds and stored traces receive **ZERO SAFETY CREDIT**. They may observe only. They may not command motion, maintain actuator power, defeat a protective circuit or justify energization. `EG-025` remains open and `EG-026` remains partial.
''', encoding="utf-8")

    WEB.mkdir(parents=True, exist_ok=True)
    rows = "".join(f"<tr><td>{r[4]}</td><td><code>{r[1]}</code><br>{r[2]}</td><td>J3.2 / J3.1</td><td>{r[5]}</td><td>{r[6]}</td></tr>" for r in CHANNELS)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 low-loading event acquisition</title><style>
:root{{--ink:#082b55;--blue:#0b5c9b;--sky:#d9f2ff;--gold:#f5bd24;--paper:#f7fbff;--red:#8b1d2c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,4vw,42px)}}header{{background:var(--ink);color:white;border-bottom:8px solid var(--gold)}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(24px,3vw,36px)}}.warning{{background:#fff1b8;color:#2a1a00;border:3px solid var(--gold);padding:16px;font-weight:850}}.flow{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:12px;align-items:center;overflow-x:auto;background:white;border:2px solid #9bcbea;padding:18px;border-radius:12px}}.box{{min-width:210px;border:2px solid var(--blue);padding:16px;border-radius:10px}}.danger{{border-color:var(--red);background:#fff3f4}}.table{{overflow-x:auto;border:2px solid #9bcbea;background:white;border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #b7d9ed;font-size:16px}}th{{background:var(--sky)}}code,small{{font-size:14px}}a{{color:var(--blue);font-weight:750}}@media(max-width:700px){{.flow{{grid-template-columns:1fr;overflow:visible}}.arrow{{transform:rotate(90deg);text-align:center}}}}
</style></head><body><header><div><p>PROJECT BUTTON / R177</p><h1>Lower loading. Same hard stop.</h1><p>A channel-isolated voltage-acquisition route with every field adapter still deliberately unselected.</p></div></header><main><p class="warning">{WARNING}</p><h2>Preferred evaluation path</h2><div class="flow"><div class="box danger">7 field adapters<br><small>SELECTION REQUIRED / no connection</small></div><div class="arrow">→</div><div class="box">7 × TI AMC3330EVM<br><small>one isolation barrier per event</small></div><div class="arrow">→</div><div class="box">7 T7 differential pairs<br><small>sequential + FIO_STATE witness</small></div></div><h2>What changed</h2><p>The AMC3330 input itself is high impedance, so this route can support a far lighter tap than the R176 2.25 mA industrial-input candidate. It still needs an engineered divider and protection network because AMC3330 accepts only ±1 V and TI says its EVM is not certified for high-voltage operation.</p><h2>Exact output map</h2><div class="table"><table><thead><tr><th>EVM</th><th>Event</th><th>Output</th><th>T7 pair</th><th>DB37 pins</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Timing truth</h2><p>The T7 does not sample these seven channels simultaneously. The eight-address scan ceiling is 12.5 kscan/s only under LabJack's stated 100 ksamples/s conditions. Installed order, skew, thresholds and uncertainty remain open and must be measured.</p><p><a href="../../../docs/hr-v0-dynamic-event-ain-p0.1.md">Controlled engineering record</a> · <a href="../../../electrical/kicad/hr-v0-dynamic-event-ain-p0.1/output/event-ain-1.svg">Native schematic sheet</a></p></main></body></html>''', encoding="utf-8")


def main() -> int:
    write_package(); build_ecad(); write_docs()
    print(f"Generated {IDENTIFIER}: 7 isolated analog channels, 15 open holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
