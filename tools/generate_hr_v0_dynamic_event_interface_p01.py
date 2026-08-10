#!/usr/bin/env python3
"""Generate the R176 HR-V0 isolated dynamic-event acquisition candidate."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/dynamic-event-interface-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-dynamic-event-interface-p0.1"
WEB = ROOT / "release/hr-v0/dynamic-event-interface-p0.1"
FORM = ROOT / "tests/forms/hr-v0-dynamic-event-interface-receiving-template-p0.1.csv"
DOC = ROOT / "docs/hr-v0-dynamic-event-interface-p0.1.md"
PROJECT = "hr-v0-dynamic-event-interface-p0.1"
IDENTIFIER = "HR-V0-DYN-EVENT-IF-P0.1"
REV = "R176 / P0.1"
WARNING = "PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")


CHANNELS = [
    ("DEI-001", "FIO0", "DB37-6", "COMMON_TRIGGER_LOGIC", "output and streamed witness", "DCH-001", "Trigger receiver/driver and camera compatibility SELECTION REQUIRED"),
    ("DEI-002", "FIO1", "DB37-24", "EVMA_OUT1", "S0 channel-1 return / SR1_S12 candidate", "DCH-014", "Direct tap prohibited pending Pilz pulse/loading/common-cause review"),
    ("DEI-003", "FIO2", "DB37-5", "EVMA_OUT2", "RESET return / SR1_START_RETURN candidate", "DCH-X01", "Direct tap prohibited pending monitored-reset loading/fault review"),
    ("DEI-004", "FIO3", "DB37-23", "EVMA_OUT3", "ARM after S2 / ARM_AFTER_S2 candidate", "DCH-X02", "Direct tap prohibited pending monitored-start loading/fault review"),
    ("DEI-005", "FIO4", "DB37-4", "EVMA_OUT4", "K1 coil command / K1_A1 candidate", "DCH-008", "Direct tap prohibited pending coil-command loading/dropout review"),
    ("DEI-006", "FIO5", "DB37-22", "EVMB_OUT1", "K2 coil command / K2_A1 candidate", "DCH-009", "Direct tap prohibited pending coil-command loading/dropout review"),
    ("DEI-007", "FIO6", "DB37-3", "EVMB_OUT2", "K1 mirror chain / EDM_K1_OUT candidate", "DCH-010", "Direct tap prohibited pending EDM loading/fault review"),
    ("DEI-008", "FIO7", "DB37-21", "EVMB_OUT3", "K2 mirror chain / SRA1_START_RETURN candidate", "DCH-011", "Direct tap prohibited pending EDM loading/fault review"),
]

EVM_MAP = [
    ("A", "1", "J4-9", "J2-2", "EVMA_IN1", "EVMA_OUT1", "fast / no 0.33 uF filter"),
    ("A", "2", "J4-8", "J2-4", "EVMA_IN2", "EVMA_OUT2", "fast / no 0.33 uF filter"),
    ("A", "3", "J4-7", "J2-6", "EVMA_IN3", "EVMA_OUT3", "fast / no 0.33 uF filter"),
    ("A", "4", "J4-6", "J2-8", "EVMA_IN4", "EVMA_OUT4", "fast / no 0.33 uF filter"),
    ("B", "1", "J4-9", "J2-2", "EVMB_IN1", "EVMB_OUT1", "fast / no 0.33 uF filter"),
    ("B", "2", "J4-8", "J2-4", "EVMB_IN2", "EVMB_OUT2", "fast / no 0.33 uF filter"),
    ("B", "3", "J4-7", "J2-6", "EVMB_IN3", "EVMB_OUT3", "fast / no 0.33 uF filter"),
    ("B", "4", "J4-6", "J2-8", "EVMB_IN4_DNP", "EVMB_OUT4_DNP", "unused fast channel / DNP"),
]

FIELD = [
    ("EVMA_IN1", "SR1_S12", "S0 channel-1 return", "Pilz diagnostic/test circuit; waveform and allowed added load not accepted"),
    ("EVMA_IN2", "SR1_START_RETURN", "manual RESET return", "monitored reset; added load and stuck/high fault effect not accepted"),
    ("EVMA_IN3", "ARM_AFTER_S2", "manual ARM/start return", "monitored start; added load and stuck/high fault effect not accepted"),
    ("EVMA_IN4", "K1_A1", "K1 coil command", "parallel input load/dropout and surge behavior not accepted"),
    ("EVMB_IN1", "K2_A1", "K2 coil command", "parallel input load/dropout and surge behavior not accepted"),
    ("EVMB_IN2", "EDM_K1_OUT", "K1 mirror-contact chain", "EDM diagnostic behavior with added input not accepted"),
    ("EVMB_IN3", "SRA1_START_RETURN", "K2 mirror-contact chain", "EDM diagnostic behavior with added input not accepted"),
]

HOLDS = [
    ("DEH-001", "PROCUREMENT", "Two received ISO1212EVM units with exact identities/revisions and an accepted current source; TI currently shows no TI stock"),
    ("DEH-002", "INTENDED USE", "Bench R&D-only disposition accepted; EVMs prohibited from robot installation or finished-product assembly"),
    ("DEH-003", "FIELD LOAD", "Per-tap source capability and allowed added 2.25 mA typical input load established from exact Pilz/Schneider application evidence"),
    ("DEH-004", "DIAGNOSTIC PULSES", "Oscilloscope comparison proves no masking, false state, pulse distortion or cross-fault diagnostic degradation on SR1_S12 and start/reset paths"),
    ("DEH-005", "EDM", "K1/K2 mirror-contact chain loading and welded/contact-open fault behavior accepted with the measurement taps present and absent"),
    ("DEH-006", "COIL COMMANDS", "K1_A1/K2_A1 loading, surge, dropout, leakage and de-energization timing accepted"),
    ("DEH-007", "FIELD REFERENCE", "Single EVM field-side FGND-to-SAFETY_0V connection point, fault effect, routing and no-ground-loop proof accepted"),
    ("DEH-008", "LOGIC POWER", "T7 VS budget or a separately selected 5 V SELV bench source accepted for two received EVMs over temperature and fault"),
    ("DEH-009", "JUMPERS", "Both received EVM J3 jumpers photographed and continuity-verified in 1-2 ENABLE position; no board modification"),
    ("DEH-010", "HARNESS", "Exact mating terminals, wire, insulation, labels, strain relief, segregation and guarded test-point adapters selected"),
    ("DEH-011", "DAQ CONFIG", "T7 FIO0 output, FIO1-FIO7 input, FIO_STATE scan, rate, host transport, buffer and dropped-scan settings frozen and checked"),
    ("DEH-012", "TRIGGER", "Exact isolated/buffered camera or witness receiver interface selected; no direct camera connection inferred"),
    ("DEH-013", "TIMING", "Installed channel propagation, pulse width, sample period, skew, trigger latency and combined uncertainty measured over accepted conditions"),
    ("DEH-014", "FAULT INJECTION", "Open, short, stuck-high, stuck-low, field-ground loss, logic-power loss and DAQ/host failure cases executed without safety-function credit"),
    ("DEH-015", "QUALIFIED REVIEW", "Qualified electrical and functional-safety reviewers accept noninterference and a separate controlled work authorization is issued"),
]

SOURCES = [
    ("DES-001", "Texas Instruments", "ISO1212EVM user guide", "SLLU254A", "May 2017; revised January 2018", "https://www.ti.com/lit/pdf/SLLU254", "Eight channels; first four fast; exact J1/J2/J3/J4 mapping; 2.25 mA typical field current; EVM/R&D limitations"),
    ("DES-002", "Texas Instruments", "ISO1212 datasheet", "SLLSEY7G", "February 2025", "https://www.ti.com/lit/pdf/SLLSEY7", "Receiver electrical characteristics and basic-isolation device scope; no Project Button safety credit"),
    ("DES-003", "Texas Instruments", "ISO1212EVM product page", "live page / no revision published", "accessed 2026-08-10", "https://www.ti.com/tool/ISO1212EVM", "Exact evaluation-module identity, four dual-channel devices, current TI stock state"),
    ("DES-004", "LabJack", "T-Series stream mode", "live web datasheet / no revision published", "accessed 2026-08-10", "https://support.labjack.com/docs/3-2-stream-mode-t-series-datasheet", "FIO_STATE is streamable; one scan samples every address after a hardware-timed clock pulse; T7 one-address maximum is not an accepted installed rate"),
    ("DES-005", "LabJack", "T7 DB37 pinout", "live web datasheet / no revision published", "accessed 2026-08-10", "https://support.labjack.com/docs/16-0-db37-t7-only-t-series-datasheet", "Exact FIO0-FIO7, VS and GND DB37 pin mapping and duplicate-terminal warning"),
    ("DES-006", "LabJack", "T-Series digital I/O", "live web datasheet / no revision published", "accessed 2026-08-10", "https://support.labjack.com/docs/13-0-digital-i-o-t-series-datasheet", "3.3 V logic, 5 V-tolerant input statement and input-state configuration requirements"),
    ("DES-007", "LabJack", "T-Series digital I/O specifications", "live web datasheet / no revision published", "accessed 2026-08-10", "https://support.labjack.com/docs/a-2-digital-i-o-t-series-datasheet", "Guaranteed high/low and maximum input-voltage limits; received compatibility still requires test"),
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
    spec = importlib.util.spec_from_file_location("event_interface_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = "2026-08-10"
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 ISOLATED DYNAMIC EVENT INTERFACE"
    model.PROJECT_SUBTITLE = "BENCH R&D EQUIPMENT ONLY; DIRECT FIELD TAPS PROHIBITED UNTIL NONINTERFERENCE REVIEW; ZERO SAFETY CREDIT"
    return model


def evm(model, ref: str, prefix: str, position: tuple[float, float]):
    pn, Component = model.pn, model.Component
    inputs = [f"{prefix}_IN1", f"{prefix}_IN2", f"{prefix}_IN3", f"{prefix}_IN4" if prefix == "EVMA" else f"{prefix}_IN4_DNP"]
    outputs = [f"{prefix}_OUT1", f"{prefix}_OUT2", f"{prefix}_OUT3", f"{prefix}_OUT4" if prefix == "EVMA" else f"{prefix}_OUT4_DNP"]
    pins = [
        pn(ref, "J4-9", "FAST INPUT 1", inputs[0], "left"), pn(ref, "J4-8", "FAST INPUT 2", inputs[1], "left"),
        pn(ref, "J4-7", "FAST INPUT 3", inputs[2], "left"), pn(ref, "J4-6", "FAST INPUT 4", inputs[3], "left"),
        pn(ref, "J4-1", "FIELD GND", "SAFETY_0V_TAP_CANDIDATE", "left"), pn(ref, "J1-2", "VCC1 MAX 5 V", "DAQ_VS_5V_CANDIDATE", "left"),
        pn(ref, "J1-1", "GND1", "DAQ_GND", "left"),
        pn(ref, "J2-2", "OUTPUT 1", outputs[0], "right"), pn(ref, "J2-4", "OUTPUT 2", outputs[1], "right"),
        pn(ref, "J2-6", "OUTPUT 3", outputs[2], "right"), pn(ref, "J2-8", "OUTPUT 4", outputs[3], "right"),
        pn(ref, "J2-1", "GND1", "DAQ_GND", "right"), pn(ref, "J2-3", "GND1", "DAQ_GND", "right"),
        pn(ref, "J2-5", "GND1", "DAQ_GND", "right"), pn(ref, "J2-7", "GND1", "DAQ_GND", "right"),
    ]
    return Component(ref, "TI ISO1212EVM - EXACT EVALUATION CANDIDATE", pins, "NOT SELECTED / BENCH R&D ONLY", "Use only unmodified fast channels 1-4. J3 jumper must be at 1-2 ENABLE. No channel-to-channel isolation; common field FGND. Direct field connection prohibited pending application review.", "TI SLLU254A Rev A", "EVM is not finished-product hardware and receives zero safety credit.", position=position, width=58)


def build_ecad() -> None:
    model = load_model()
    pn, Component = model.pn, model.Component

    def make_field_sheet(number: int, suffix: str, rows: list[tuple[str, str, str, str]]):
        field_ref, evm_ref = f"JFIELD{suffix}", f"EVM{suffix}J4"
        field_pins = [pn(field_ref, net, label, net, "right") for net, _, label, _ in rows]
        field_pins.append(pn(field_ref, "SAFETY_0V", "FIELD REFERENCE", "SAFETY_0V_TAP_CANDIDATE", "right"))
        field = Component(field_ref, "LOGICAL FIELD TEST POINTS - NO CONNECTOR RELEASED", field_pins, "DIRECT CONNECTION PROHIBITED", "Exact probes/adapters, noninterference, routing and guarding are SELECTION REQUIRED.", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "Logical names only; not physical terminals or authority.", position=(50, 105), width=62)
        nets = [row[0] for row in rows]
        while len(nets) < 4:
            nets.append("EVMB_IN4_DNP")
        j4 = Component(evm_ref, f"TI ISO1212EVM {suffix} FIELD CONNECTOR J4", [
            pn(evm_ref, "J4-9", "FAST INPUT 1", nets[0], "left"), pn(evm_ref, "J4-8", "FAST INPUT 2", nets[1], "left"),
            pn(evm_ref, "J4-7", "FAST INPUT 3", nets[2], "left"), pn(evm_ref, "J4-6", "FAST INPUT 4", nets[3], "left"),
            pn(evm_ref, "J4-1", "FIELD GND", "SAFETY_0V_TAP_CANDIDATE", "left"),
        ], "NOT SELECTED / BENCH R&D ONLY", "Unmodified fast channels only. J4 pin 1 is common FGND. No channel-to-channel isolation. Direct field connection prohibited.", "TI SLLU254A Rev A Figure 7", "Connector representation only.", position=(230, 105), width=72)
        sheet = model.Sheet(number, f"0{number}_field_{suffix.lower()}.kicad_sch", f"EVM {suffix} field taps - connection prohibited", "Exact J4 fast-channel allocation; noninterference and fault review open.", compact=True)
        sheet.components = [field, j4]
        sheet.notes = ["Each used input draws about 2.25 mA typical; J4 pin 1 is shared FGND.", "NO WIRE until diagnostic-pulse, start/reset, EDM and coil-loading effects are accepted."]
        return sheet

    sheet_a = make_field_sheet(1, "A", FIELD[:4])
    sheet_b = make_field_sheet(2, "B", FIELD[4:])

    def make_logic(ref: str, prefix: str, y: float):
        outputs = [f"{prefix}_OUT1", f"{prefix}_OUT2", f"{prefix}_OUT3", f"{prefix}_OUT4" if prefix == "EVMA" else f"{prefix}_OUT4_DNP"]
        return Component(ref, f"TI ISO1212EVM {prefix[-1]} LOGIC J1/J2", [
            pn(ref, "J1-2", "VCC1 MAX 5 V", "DAQ_VS_5V_CANDIDATE", "left"), pn(ref, "J1-1", "GND1", "DAQ_GND", "left"),
            pn(ref, "J2-2", "OUTPUT 1", outputs[0], "right"), pn(ref, "J2-4", "OUTPUT 2", outputs[1], "right"),
            pn(ref, "J2-6", "OUTPUT 3", outputs[2], "right"), pn(ref, "J2-8", "OUTPUT 4", outputs[3], "right"),
            pn(ref, "J2-1", "GND1", "DAQ_GND", "right"), pn(ref, "J2-3", "GND1", "DAQ_GND", "right"),
            pn(ref, "J2-5", "GND1", "DAQ_GND", "right"), pn(ref, "J2-7", "GND1", "DAQ_GND", "right"),
        ], "NOT SELECTED / BENCH R&D ONLY", "J3 must be received and verified in 1-2 ENABLE position. VCC budget and logic-level proof remain open.", "TI SLLU254A Rev A Figure 7", "J1/J2 representation; no board modification.", position=(60, y), width=66)

    evma = make_logic("EVMAJ2", "EVMA", 70)
    evma.position = (150, 70)
    evmb = make_logic("EVMBJ2", "EVMB", 138)
    evmb.position = (150, 138)
    daq = Component("DAQ1", "LabJack T7 + CB37 - EXACT EVALUATION CANDIDATES", [
        pn("DAQ1", "DB37-27", "VS ABOUT 5 V", "DAQ_VS_5V_CANDIDATE", "left"), pn("DAQ1", "DB37-1", "GND", "DAQ_GND", "left"),
        pn("DAQ1", "DB37-6", "FIO0 TRIGGER/WITNESS", "COMMON_TRIGGER_LOGIC", "right"),
        pn("DAQ1", "DB37-24", "FIO1 EVENT", "EVMA_OUT1", "left"), pn("DAQ1", "DB37-5", "FIO2 EVENT", "EVMA_OUT2", "left"),
        pn("DAQ1", "DB37-23", "FIO3 EVENT", "EVMA_OUT3", "left"), pn("DAQ1", "DB37-4", "FIO4 EVENT", "EVMA_OUT4", "left"),
        pn("DAQ1", "DB37-22", "FIO5 EVENT", "EVMB_OUT1", "left"), pn("DAQ1", "DB37-3", "FIO6 EVENT", "EVMB_OUT2", "left"),
        pn("DAQ1", "DB37-21", "FIO7 EVENT", "EVMB_OUT3", "left"),
    ], "NOT SELECTED / ZERO SAFETY CREDIT", "FIO_STATE candidate scan: FIO0 witness plus FIO1-FIO7 inputs. Configuration, VS budget, host and timing proof remain open.", "LabJack live T-Series datasheet accessed 2026-08-10", "Exact DB37 pins; CB37 continuity required.", position=(120, 105), width=68)
    trig = Component("JTRIG1", "TRIGGER RECEIVER - SELECTION REQUIRED", [pn("JTRIG1", "IN", "LOGIC TRIGGER", "COMMON_TRIGGER_LOGIC", "left"), pn("JTRIG1", "RTN", "LOGIC RETURN", "DAQ_GND", "left")], "NO DIRECT CAMERA CONNECTION", "Driver, polarity, cable, delay and camera compatibility required.", "No manufacturer selected", "FIO0 external connection prohibited.", position=(248, 105), width=48)
    sheet_logic = model.Sheet(3, "03_evm_logic.kicad_sch", "EVM logic-side connector allocation", "Exact J1/J2 mapping; received jumpers, power budget and levels open.", compact=True)
    sheet_logic.components = [evma, evmb]
    sheet_logic.notes = ["Verify both received J3 jumpers at 1-2 ENABLE.", "J2 pins 2/4/6/8 are outputs; odd pins shown are logic GND."]
    sheet_daq = model.Sheet(4, "04_common_clock_capture.kicad_sch", "Common-clock T7 capture and trigger witness", "Exact DB37 mapping; trigger receiver and run configuration open.", compact=True)
    sheet_daq.components = [daq, trig]
    sheet_daq.notes = ["FIO_STATE candidate: FIO0 witness plus FIO1-FIO7 event bits.", "DAQ, host and trigger receive ZERO SAFETY CREDIT; timing and work authority remain open."]
    sheets = [sheet_a, sheet_b, sheet_logic, sheet_daq]
    items = [component for sheet in sheets for component in sheet.components]
    counts = Counter(pin.net for component in items for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    root_uuid = model.uid("root-hr-v0-dynamic-event-interface-p01")
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 isolated event acquisition candidate"))\n)\n', encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["reference", "terminal", "function", "net", "state"], [(component.ref, pin.number, pin.name, pin.net, component.status) for component in items for pin in component.pins])
    write_csv(ECAD / "bom.csv", ["reference", "manufacturer", "part_number", "quantity", "state"], [
        ("EVMAJ4/EVMAJ2,EVMBJ4/EVMBJ2", "Texas Instruments", "ISO1212EVM", "2", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("DAQ1", "LabJack", "T7", "1", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("DAQ1 breakout", "LabJack", "CB37 Terminal Board", "1", "EXACT EVALUATION CANDIDATE / NOT SELECTED"),
        ("JFIELDA/JFIELDB,JTRIG1", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "NO PHYSICAL CONNECTOR RELEASED"),
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
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
            raise SystemExit(result.returncode)
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    children = [path for path in output.glob("*.svg") if path.name != f"{PROJECT}.svg"]
    for index, source in enumerate(sorted(children), start=1):
        source.replace(output / f"event-interface-{index}.svg")
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (ECAD / "SOURCE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(rows)


def write_package() -> None:
    PKG.mkdir(parents=True, exist_ok=True)
    write_csv(PKG / "candidate-bom.csv", ["item_id", "reference", "manufacturer", "part_number", "quantity", "selection_state", "procurement_state", "use_limit"], [
        ("TE-009A", "EVMAJ4/EVMAJ2,EVMBJ4/EVMBJ2", "Texas Instruments", "ISO1212EVM", "2", "EXACT EVALUATION CANDIDATE / NOT SELECTED", "NOT AUTHORIZED", "Bench R&D only; first four fast channels only; never robot-installed"),
        ("TE-009B", "DAQ1", "LabJack", "T7", "1", "INHERITED EXACT EVALUATION CANDIDATE / NOT SELECTED", "NOT AUTHORIZED", "Measurement only; zero safety credit"),
        ("TE-009C", "DAQ1 breakout", "LabJack", "CB37 Terminal Board", "1", "INHERITED EXACT EVALUATION CANDIDATE / NOT SELECTED", "NOT AUTHORIZED", "Continuity and duplicate-terminal controls required"),
        ("TE-009D", "JFIELD1 field harness", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "NOT AUTHORIZED", "No field connection until noninterference evidence and qualified review"),
        ("TE-009E", "JTRIG1 trigger interface", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "NOT AUTHORIZED", "No direct camera connection inferred"),
    ])
    write_csv(PKG / "channel-map.csv", ["channel_id", "t7_terminal", "db37_pin", "net", "function", "requirement", "hold"], CHANNELS)
    write_csv(PKG / "evm-connector-map.csv", ["evm", "channel", "field_terminal", "logic_terminal", "field_net", "logic_net", "configuration"], EVM_MAP)
    write_csv(PKG / "field-tap-risk-register.csv", ["event_input_net", "project_net_candidate", "meaning", "unaccepted_risk"], FIELD)
    write_csv(PKG / "selection-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "document", "revision", "document_date", "official_locator", "use_and_limit"], SOURCES)
    write_csv(PKG / "timing-budget-inputs.csv", ["input_id", "quantity", "candidate_or_requirement", "state", "evidence_required"], [
        ("DTI-001", "FIO_STATE scan rate", "10 kscan/s preliminary verification target", "SELECTION REQUIRED", "Frozen T7 configuration plus no-overflow execution evidence"),
        ("DTI-002", "nominal sample period", "100 us at 10 kscan/s", "DERIVED SCREEN ONLY", "Accepted installed scan rate"),
        ("DTI-003", "ISO1212/EVM propagation", "SELECTION REQUIRED", "OPEN", "Per-channel rising/falling delay over voltage and temperature on received EVMs"),
        ("DTI-004", "field diagnostic pulse width", "SELECTION REQUIRED", "OPEN", "Measured minimum high/low pulse width at every tapped circuit"),
        ("DTI-005", "T7 digital threshold margin", "SELECTION REQUIRED", "OPEN", "Received EVM high/low voltage under load against T7 guaranteed thresholds"),
        ("DTI-006", "trigger-to-camera latency", "SELECTION REQUIRED", "OPEN", "Selected driver/camera/cable measurement"),
        ("DTI-007", "combined uncertainty", "SELECTION REQUIRED", "OPEN", "Accepted propagation + sampling + clock + trigger + analysis budget"),
    ])
    (PKG / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": "2026-08-10", "status": WARNING,
        "exact_new_evaluation_candidate_count": 1, "exact_new_evaluation_unit_count": 2,
        "field_event_count": 7, "common_clock_word_count": 1, "open_hold_count": len(HOLDS),
        "authorized_procurement_count": 0, "authorized_connection_count": 0,
        "authorized_powered_run_count": 0, "executed_physical_run_count": 0,
        "safety_function_credit": "ZERO", "release_effect": "NONE"
    }, indent=2) + "\n", encoding="utf-8")
    FORM.parent.mkdir(parents=True, exist_ok=True)
    write_csv(FORM, ["record_id", "article", "serial_or_lot", "received_identity", "hardware_revision", "j3_position", "power_off_continuity", "field_to_logic_isolation_screen", "result", "reviewer", "evidence_hash"], [
        ("DER-001", "EVMA1 ISO1212EVM", "", "", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("DER-002", "EVMB1 ISO1212EVM", "", "", "", "", "", "", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("DER-003", "DAQ1 LabJack T7", "", "", "", "N/A", "", "N/A", "NOT EXECUTED", "SELECTION REQUIRED", ""),
        ("DER-004", "DAQ1 CB37", "", "", "", "N/A", "", "N/A", "NOT EXECUTED", "SELECTION REQUIRED", ""),
    ])
    source_pdf = ROOT / "references/ti/iso1212evm-r176/sllu254a.pdf"
    (ROOT / "references/ti/iso1212evm-r176/source-record.json").write_text(json.dumps({
        "manufacturer": "Texas Instruments", "document": "ISO1212EVM user guide", "revision": "SLLU254A",
        "document_date": "May 2017; revised January 2018", "retrieved_on": "2026-08-10",
        "official_url": "https://www.ti.com/lit/ug/sllu254a/sllu254a.pdf", "bytes": source_pdf.stat().st_size,
        "sha256": hashlib.sha256(source_pdf.read_bytes()).hexdigest().upper()
    }, indent=2) + "\n", encoding="utf-8")


def write_docs() -> None:
    DOC.write_text(f'''# HR-V0 isolated dynamic-event interface P0.1

> **{WARNING}.**

Identifier: `{IDENTIFIER}`

Date: 2026-08-10

Electrical basis: `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`

## Decision

Two unmodified Texas Instruments `ISO1212EVM` boards are exact **evaluation candidates** for seven 24 V-class event witnesses. Only each board's first four fast channels are used. A LabJack T7 reads FIO1-FIO7 and records the FIO0 trigger/witness bit in one hardware-timed `FIO_STATE` scan word. This creates a coherent candidate timebase without giving the DAQ, host, EVMs or trigger path any safety-function credit.

The EVMs are TI evaluation equipment intended for engineering development. They are not finished-product hardware and may never be installed in Project Button. They provide a field-to-logic isolation barrier as encoded by the manufacturer, but not channel-to-channel isolation. Every field channel shares the EVM field ground.

## Exact connector mapping

On each EVM, fast field inputs 1-4 are J4 pins 9, 8, 7 and 6; J4 pin 1 is FGND. Their logic outputs are J2 pins 2, 4, 6 and 8. J2 odd pins 1, 3, 5 and 7 are logic ground. J1 pin 2 is VCC1 and J1 pin 1 is GND1. J3 must be received and verified in the 1-2 ENABLE position. Channels 5-8 remain unused so the installed 0.33 uF slow-channel filters are not modified.

T7/CB37 mapping is exact at the manufacturer DB37: FIO0 pin 6, FIO1 pin 24, FIO2 pin 5, FIO3 pin 23, FIO4 pin 4, FIO5 pin 22, FIO6 pin 3 and FIO7 pin 21. VS is pin 27 and the candidate logic reference uses DB37 pin 1 GND. Duplicate T7 terminals may not be connected elsewhere.

## Critical hold: direct taps remain prohibited

The ISO1212EVM presents approximately 2.25 mA typical field input current. That load is not yet accepted on `SR1_S12`, `SR1_START_RETURN`, `ARM_AFTER_S2`, `K1_A1`, `K2_A1`, `EDM_K1_OUT` or `SRA1_START_RETURN`. Several are Pilz diagnostic, monitored-start/reset or EDM paths. A parallel measurement input could distort a pulse, mask a fault, change a threshold or alter dropout timing. The native KiCad sheet is therefore a connected **candidate**, not a wiring instruction.

Closure requires exact circuit-source capability, measured waveforms with taps present and absent, every applicable stuck/open/short/ground-loss fault, accepted propagation and uncertainty, and qualified electrical/functional-safety review. No test computer or DAQ may command motion, maintain power, bypass a protective circuit, or receive safety credit.

## Timing state

`FIO_STATE` is a single stream address, so all eight represented bits share the T7 scan clock. A 10 kscan/s (100 us nominal period) configuration is only a preliminary verification target. Actual scan rate, host transport, buffering, overflow handling, ISO1212 propagation, diagnostic-pulse width, trigger latency and combined uncertainty remain `SELECTION REQUIRED` and must be measured on received hardware.

## Release effect

This correction replaces TE-009's unnamed isolated-input gap with an exact evaluation candidate and a native connected integration schematic. It does not authorize procurement or connection, does not close `EG-025` or `EG-026`, and supplies no executed stopping/reset evidence.
''', encoding="utf-8")

    WEB.mkdir(parents=True, exist_ok=True)
    rows = "".join(f"<tr><td>{c[0]}</td><td>{c[1]} / {c[2]}</td><td>{c[4]}</td><td>{c[5]}</td><td>{c[6]}</td></tr>" for c in CHANNELS)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 dynamic event interface</title><style>
:root{{--ink:#082b55;--blue:#0b5c9b;--sky:#d9f2ff;--gold:#f5bd24;--paper:#f7fbff;--red:#8b1d2c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,4vw,42px)}}header{{background:var(--ink);color:white;border-bottom:8px solid var(--gold)}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(24px,3vw,36px)}}.warning{{background:#fff1b8;color:#2a1a00;border:3px solid var(--gold);padding:16px;font-weight:850}}.flow{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:12px;align-items:center;overflow-x:auto;background:white;border:2px solid #9bcbea;padding:18px;border-radius:12px}}.box{{min-width:190px;border:2px solid var(--blue);padding:16px;border-radius:10px}}.danger{{border-color:var(--red);background:#fff3f4}}.table{{overflow-x:auto;border:2px solid #9bcbea;background:white;border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:980px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid #b7d9ed;font-size:16px}}th{{background:var(--sky)}}code{{font-size:14px}}a{{color:var(--blue);font-weight:750}}@media(max-width:700px){{.flow{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);text-align:center}}}}
</style></head><body><header><div><p>PROJECT BUTTON / R176</p><h1>Seven events. One clock.</h1><p>An exact isolated-input evaluation candidate with every unsafe field connection still held.</p></div></header><main><p class="warning">{WARNING}</p><h2>Candidate signal path</h2><div class="flow"><div class="box danger">7 logical field taps<br><small>connection prohibited</small></div><div class="arrow">→</div><div class="box">2 × TI ISO1212EVM<br><small>fast channels only</small></div><div class="arrow">→</div><div class="box">LabJack FIO_STATE<br><small>FIO0 witness + FIO1-FIO7 events</small></div></div><h2>Why it is still held</h2><p>Each field input draws about 2.25 mA typical. That seemingly small load can matter on Pilz diagnostic pulses, monitored reset/start paths and EDM mirror-contact circuits. The taps remain prohibited until waveform comparison, fault injection and qualified noninterference review are complete.</p><h2>Exact capture map</h2><div class="table"><table><thead><tr><th>ID</th><th>T7 point</th><th>Observed event</th><th>Requirement</th><th>Blocking evidence</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Boundaries</h2><p>The EVMs are bench R&D equipment only, share one field ground per board, and are not channel-to-channel isolated. They may not be installed in the robot. The DAQ and host receive ZERO SAFETY CREDIT and may not command motion or defeat power removal.</p><p><a href="../../../docs/hr-v0-dynamic-event-interface-p0.1.md">Read the controlled engineering record</a> · <a href="../../../electrical/kicad/hr-v0-dynamic-event-interface-p0.1/output/event-interface-1.svg">Open the first native schematic sheet</a></p></main></body></html>''', encoding="utf-8")


def main() -> int:
    write_package(); build_ecad(); write_docs()
    print(f"Generated {IDENTIFIER}: 7 field events, one common FIO_STATE word, {len(HOLDS)} open holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
