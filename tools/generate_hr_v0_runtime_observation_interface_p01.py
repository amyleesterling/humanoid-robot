#!/usr/bin/env python3
"""Generate the R201 HR-V0 four-channel runtime observation candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-interface-p0.1"
WEB = ROOT / "release/hr-v0/runtime-observation-interface-p0.1"
DOC = ROOT / "docs/hr-v0-runtime-observation-interface-p0.1.md"
PROJECT = "hr-v0-runtime-observation-interface-p0.1"
IDENTIFIER = "HR-V0-RUNTIME-OBS-IF-P0.1"
REV = "R201 / P0.1"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")


SOURCES = [
    ("OBS-SRC-001", "Pilz", "PNOZ s4 operating manual", "21396-EN-23", "2026-06-22", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "Y32 high semantics; 24 V, 20 mA maximum, 0.1 mA residual and 5 V maximum internal drop; diagnostic only"),
    ("OBS-SRC-002", "Texas Instruments", "ISO1211/ISO1212 datasheet", "SLLSEY7G", "revised 2025-02; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/iso1212.pdf", "DBQ pins; 562 ohm / 1 kohm Type-3 network; thresholds, current, thermal, EMC and layout limits"),
    ("OBS-SRC-003", "Schneider Electric", "LC1D25BD product data sheet", "current generated sheet", "rechecked 2026-08-10", "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", "Built-in linked NO/NC; NC mirror; signalling minimum 5 mA and 17 V"),
    ("OBS-SRC-004", "IDEC", "HW1P-1FQD-A-24V product page and HW Series Catalog_Screw", "catalog dated 2026-07-23", "rechecked 2026-08-10", "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1p-1fqd-a-24v", "Exact amber 24 VAC/DC pilot-light identity; catalog family screen is 7 mA DC, while received current/terminals/brightness remain open"),
    ("OBS-SRC-005", "Raspberry Pi", "RP1 Peripherals", "current PDF", "rechecked 2026-08-10", "https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf", "Pi 5 RP1 GPIO bank is 3.3 V; numerical input threshold and exact header allocation are not released by this package"),
    ("OBS-SRC-006", "Phoenix Contact", "MKDS 1/4-3,5 product record", "item 1751264; current online catalog", "rechecked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-4-35-1751264", "Four-position 3.5 mm-pitch PCB screw terminal candidate; 17.5 A nominal, 200 V III/2 and 1.5 mm2 nominal cross-section are catalog ratings, not installed-system acceptance"),
    ("OBS-SRC-007", "Phoenix Contact", "MKDS 1/2-3,5 product record", "item 1751248; current online catalog", "rechecked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248", "Two-position 3.5 mm-pitch PCB screw terminal candidate; 17.5 A nominal, 200 V III/2 and 1.5 mm2 nominal cross-section are catalog ratings, not installed-system acceptance"),
]

LOADS = [
    ("OBS-LOAD-001", "SR1_STATUS", "Pilz Y32 plus existing H1 plus ISO1212 channel", "22.8 to 25.2 V rail; Y32 may drop 5 V", "ISO input 2.05 to 2.75 mA; IDEC catalog-family screen 7 mA DC", "9.75 mA catalog-family screen; not a received-part maximum", "10.25 mA to Pilz 20 mA", "OPEN - received H1 maximum current and brightness at 17.8 V required"),
    ("OBS-LOAD-002", "SRA1_STATUS", "Pilz Y32 plus 2.70 kohm shunt plus ISO1212 channel", "22.8 V / 2727 ohm to 25.2 V / 2673 ohm", "8.36 to 9.43 mA shunt plus 2.05 to 2.75 mA ISO", "10.41 to 12.18 mA", "7.82 mA minimum to Pilz 20 mA", "DERIVED SCREEN - thermal, fault, EMC and physical evidence open"),
    ("OBS-LOAD-003", "K1_STATUS", "LC1D25BD NO auxiliary plus 2.70 kohm shunt plus ISO1212 channel", "same tolerance screen as SRA1", "10.41 to 12.18 mA; at 17 V minimum: 8.28 mA", "exceeds Schneider 5 mA minimum", "contact voltage must remain at least 17 V", "DERIVED SCREEN - installed voltage, wetting, thermal and fault evidence open"),
    ("OBS-LOAD-004", "K2_STATUS", "LC1D25BD NO auxiliary plus 2.70 kohm shunt plus ISO1212 channel", "same tolerance screen as SRA1", "10.41 to 12.18 mA; at 17 V minimum: 8.28 mA", "exceeds Schneider 5 mA minimum", "contact voltage must remain at least 17 V", "DERIVED SCREEN - installed voltage, wetting, thermal and fault evidence open"),
    ("OBS-LOAD-005", "PI_3V3", "two ISO1212 logic sides plus four output pulldowns", "2 x 1.9 mA maximum ICC1 plus no more than 4 x 3.3 V / 11 kohm", "less than or equal to 5.0 mA calculation screen", "not a Raspberry Pi external-load approval", "PI 3V3 source, cable and back-power limits open", "SELECTION REQUIRED"),
]

HOLDS = [
    ("OBS-HOLD-001", "SR1 Y32/H1", "Measure exact received H1 current over accepted voltage/temperature, identify terminals/internal circuit, and prove useful indication with Y32 at the 17.8 V low screen"),
    ("OBS-HOLD-002", "Y32 application", "Qualified review of aggregate current, short/open faults, leakage, startup and no interference with SR1/SRA1 diagnostics"),
    ("OBS-HOLD-003", "K1/K2 wetting", "Received contact voltage/current, bounce, contamination, life and fault testing with the exact 2.70 kohm shunts"),
    ("OBS-HOLD-004", "EMC/protection", "Accept the exact Type-3 network, 10 nF DC-bias, 500 V line-to-FGND catalog test level, cable environment and any additional protection"),
    ("OBS-HOLD-005", "PCB/layout", "Native PCB, field/logic separation, 4 mm placement rule, floating SUB copper, creepage/clearance, thermal and DFM review"),
    ("OBS-HOLD-006", "Grounding", "Accept FGND-to-SAFETY_0V and GND1-to-COMPUTE_0V boundaries without creating an unintended bond, loop or back-power path"),
    ("OBS-HOLD-007", "Raspberry Pi", "Select four conflict-free GPIOs and exact physical pins from current official documentation; verify RP1 thresholds, pull state, cable, boot and power-loss behavior"),
    ("OBS-HOLD-008", "Connectors/harness", "Accept the exact PCB terminal application, conductor range, ferrules, strip length, torque, wire, labels, shield/return routing, retention, separation and service access"),
    ("OBS-HOLD-009", "Fault injection", "Execute open, short, cross-short, stuck-high, stuck-low, field-return loss, compute-return loss, logic brownout and source-loss cases"),
    ("OBS-HOLD-010", "Safety boundary", "Qualified reviewer confirms every observation remains diagnostic-only and cannot command, restore or preserve motion"),
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
    spec = importlib.util.spec_from_file_location("runtime_observation_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = DATE
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 FOUR-CHANNEL RUNTIME OBSERVATION INTERFACE"
    model.PROJECT_SUBTITLE = "DIAGNOSTIC-ONLY ISOLATED RECEIVER CANDIDATE; NO GPIO ALLOCATION; ZERO SAFETY CREDIT"
    return model


def resistor(model, ref: str, value: str, mpn: str, net1: str, net2: str, position: tuple[float, float], purpose: str):
    return model.Component(ref, f"{value}; {mpn}", [model.pn(ref, "1", purpose + " A", net1, "left"), model.pn(ref, "2", purpose + " B", net2, "right")], "EXACT COMPONENT CANDIDATE - APPLICATION/PCB/PHYSICAL HOLD", purpose + "; exact component identity inherited from the controlled watchdog receiver network. No fabrication or connection release.", position=position, width=52)


def capacitor(model, ref: str, net1: str, net2: str, position: tuple[float, float], purpose: str):
    return model.Component(ref, "10 nF 50 V X7R; TDK CGA3E2X7R1H103K080AA", [model.pn(ref, "1", "SENSE", net1, "left"), model.pn(ref, "2", "FIELD RETURN", net2, "right")], "EXACT COMPONENT CANDIDATE - DC-BIAS/PCB/EMC HOLD", purpose + "; 10 nF nominal is not credited until bias/tolerance/temperature and installed EMC evidence exist.", position=position, width=52)


def iso1212(model, ref: str, ch1: str, ch2: str, out1: str, out2: str, position: tuple[float, float]):
    pn = model.pn
    return model.Component(ref, "Texas Instruments ISO1212DBQ dual isolated digital-input receiver", [
        pn(ref, "1", "GND1", "COMPUTE_0V", "left"), pn(ref, "2", "VCC1", "PI_3V3_CANDIDATE", "left"),
        pn(ref, "3", "EN TIED HIGH", "PI_3V3_CANDIDATE", "left"), pn(ref, "4", "OUT1", out1, "right"),
        pn(ref, "5", "OUT2", out2, "right"), pn(ref, "6", "NC", f"INTENTIONALLY_UNUSED_{ref}_6", "right"),
        pn(ref, "7", "NC", f"INTENTIONALLY_UNUSED_{ref}_7", "right"), pn(ref, "8", "GND1", "COMPUTE_0V", "left"),
        pn(ref, "9", "SUB2 FLOAT", f"INTENTIONALLY_UNUSED_{ref}_9", "right"), pn(ref, "10", "SENSE2", f"{ch2}_SENSE", "left"),
        pn(ref, "11", "IN2", f"{ch2}_IN", "left"), pn(ref, "12", "FGND2", "SAFETY_0V", "left"),
        pn(ref, "13", "SUB1 FLOAT", f"INTENTIONALLY_UNUSED_{ref}_13", "right"), pn(ref, "14", "FGND1", "SAFETY_0V", "left"),
        pn(ref, "15", "IN1", f"{ch1}_IN", "left"), pn(ref, "16", "SENSE1", f"{ch1}_SENSE", "left"),
    ], "EXACT IC CANDIDATE - PCB/EMC/FAULT/PHYSICAL HOLD", "Logic GND1 is COMPUTE_0V; field FGND is SAFETY_0V. SUB pins require separate floating copper and no connection. Device isolation is not system safety approval.", "https://www.ti.com/lit/ds/symlink/iso1212.pdf", "SLLSEY7G revised February 2025; rechecked 2026-08-10.", position=position, width=76)


def channel_parts(model, index: int, source: str, prefix: str, x: float, shunt: bool):
    parts = [
        resistor(model, f"RTH{index}", "1.00 kohm 1% 0.4 W MELF", "Vishay MMA02040C1001FB300", source, f"{prefix}_SENSE", (x, 58), "TYPE-3 THRESHOLD/SURGE"),
        resistor(model, f"RSN{index}", "562 ohm 1% 0.125 W 0805", "Panasonic ERJ6ENF5620V", f"{prefix}_SENSE", f"{prefix}_IN", (x, 112), "CURRENT LIMIT"),
        capacitor(model, f"CFI{index}", f"{prefix}_SENSE", "SAFETY_0V", (x, 166), "TYPE-3 INPUT FILTER"),
    ]
    if shunt:
        parts.append(resistor(model, f"RW{index}", "2.70 kohm 1% 0.5 W 1210", "Vishay CRCW12102K70FKEA", source, "SAFETY_0V", (x, 220), "WETTING/BLEED SHUNT"))
    return parts


def build_ecad() -> None:
    model = load_model()
    pn, Component, Sheet = model.pn, model.Component, model.Sheet

    jfield = Component("JFIELD1", "Phoenix MKDS field terminal candidates: 1751264 plus 1751248", [
        pn("JFIELD1", "1", "SR1 STATUS", "SR1_STATUS", "right"), pn("JFIELD1", "2", "SRA1 STATUS", "SRA1_STATUS", "right"),
        pn("JFIELD1", "3", "K1 STATUS", "K1_STATUS", "right"), pn("JFIELD1", "4", "K2 STATUS", "K2_STATUS", "right"),
        pn("JFIELD1", "5", "FIELD RETURN", "SAFETY_0V", "right"), pn("JFIELD1", "6", "N/C", "INTENTIONALLY_UNUSED_JFIELD1_6", "right"),
    ], "EXACT PCB TERMINAL CANDIDATES - MATING/HARNESS/PCB HOLD", "Four positive status nets plus one field return and one deliberate no-connect. Position numbering is project-defined and not a harness release.", position=(76, 92), width=74)
    jlogic = Component("JLOGIC1", "Phoenix MKDS compute terminal candidates: 1751264 plus 1751248", [
        pn("JLOGIC1", "1", "PI 3V3 CANDIDATE", "PI_3V3_CANDIDATE", "left"), pn("JLOGIC1", "2", "COMPUTE RETURN", "COMPUTE_0V", "left"),
        pn("JLOGIC1", "3", "OBS SR1", "OBS_SR1_PI", "left"), pn("JLOGIC1", "4", "OBS SRA1", "OBS_SRA1_PI", "left"),
        pn("JLOGIC1", "5", "OBS K1", "OBS_K1_PI", "left"), pn("JLOGIC1", "6", "OBS K2", "OBS_K2_PI", "left"),
    ], "EXACT PCB TERMINAL CANDIDATES - PI PINS/HARNESS/PCB HOLD", "No Raspberry Pi GPIO or header pin is selected. Exact mating cable/contact system and external 3V3-load acceptance remain open.", position=(300, 92), width=74)
    boundary = Component("BOUNDARY1", "GALVANIC DOMAIN BOUNDARY - ZERO SAFETY CREDIT", [pn("BOUNDARY1", "FIELD", "FIELD FGND", "SAFETY_0V", "left"), pn("BOUNDARY1", "LOGIC", "LOGIC GND1", "COMPUTE_0V", "right")], "SYSTEM GROUNDING/INSULATION REVIEW REQUIRED", "The ISO1212 barriers separate these schematic domains. Cable, PCB, enclosure, PE, parasitic capacitance and fault paths determine the real system boundary.", position=(190, 202), width=98)
    s1 = Sheet(1, "01_boundaries.kicad_sch", "Field and compute boundaries", "Six-position field and logic terminal candidates; no Pi GPIO allocation.", compact=True)
    s1.components = [jfield, jlogic, boundary]
    s1.notes = ["Four positive diagnostic states only. No receiver output commands motion.", "SAFETY_0V and COMPUTE_0V remain distinct; no new bond is authorized."]

    u1 = iso1212(model, "UOBS1", "SR1", "SRA1", "OBS_SR1_RAW", "OBS_SRA1_RAW", (210, 136))
    h1 = Component("H1EXT", "Existing IDEC HW1P-1FQD-A-24V load outside this board", [pn("H1EXT", "TBD-HA", "UNVERIFIED INPUT", "SR1_STATUS", "left"), pn("H1EXT", "TBD-HB", "UNVERIFIED RETURN", "SAFETY_0V", "right")], "EXTERNAL LOAD - RECEIVED CURRENT/TERMINALS/BRIGHTNESS HOLD", "Catalog screen is 7 mA DC, but exact received current and Y32 low-voltage brightness are not accepted.", position=(210, 246), width=76)
    s2 = Sheet(2, "02_sr1_sra1_inputs.kicad_sch", "SR1 and SRA1 Type-3 inputs", "Y32 load budget and existing H1 application remain held.", compact=True)
    s2.components = channel_parts(model, 1, "SR1_STATUS", "SR1", 62, False) + [u1] + channel_parts(model, 2, "SRA1_STATUS", "SRA1", 360, True) + [h1]
    s2.notes = ["SR1 has no added shunt because H1 is already in parallel; received H1 evidence is mandatory.", "SRA1 uses the exact 2.70 kohm candidate: 10.41 to 12.18 mA total derived screen."]

    u2 = iso1212(model, "UOBS2", "K1", "K2", "OBS_K1_RAW", "OBS_K2_RAW", (210, 136))
    k1src = Component("K1AUX", "Existing Schneider LC1D25BD NO auxiliary 13-14", [pn("K1AUX", "13", "AUX NO IN", "SAFETY_24V", "left"), pn("K1AUX", "14", "AUX NO OUT", "K1_STATUS", "right")], "EXTERNAL CONTACT - ZERO SAFETY CREDIT", "Minimum signalling application: 5 mA and 17 V. This NO contact is diagnostic only.", position=(86, 246), width=72, quantity=0)
    k2src = Component("K2AUX", "Existing Schneider LC1D25BD NO auxiliary 13-14", [pn("K2AUX", "13", "AUX NO IN", "SAFETY_24V", "left"), pn("K2AUX", "14", "AUX NO OUT", "K2_STATUS", "right")], "EXTERNAL CONTACT - ZERO SAFETY CREDIT", "Same application boundary as K1AUX.", position=(334, 246), width=72, quantity=0)
    s3 = Sheet(3, "03_k1_k2_inputs.kicad_sch", "K1 and K2 diagnostic auxiliary inputs", "2.70 kohm shunts raise current above Schneider signalling minima in the derived screen.", compact=True)
    s3.components = channel_parts(model, 3, "K1_STATUS", "K1", 62, True) + [u2] + channel_parts(model, 4, "K2_STATUS", "K2", 360, True) + [k1src, k2src]
    s3.notes = ["At 17 V and worst high shunt resistance, the screen is 8.28 mA, above the 5 mA minimum.", "Received voltage/current, bounce, contamination, life and fault evidence remain open."]

    outputs = []
    for i, name in enumerate(("SR1", "SRA1", "K1", "K2"), start=1):
        x = 52 + (i - 1) * 104
        outputs.extend([
            resistor(model, f"RSO{i}", "1.00 kohm 1% 0.125 W 0805", "Panasonic ERJ6ENF1001V", f"OBS_{name}_RAW", f"OBS_{name}_PI", (x, 88), "OUTPUT SERIES"),
            resistor(model, f"RPD{i}", "10.0 kohm 1% 0.125 W 0805", "Panasonic ERJ6ENF1002V", f"OBS_{name}_PI", "COMPUTE_0V", (x, 158), "FAIL-LOW PULLDOWN"),
        ])
    cdec1 = Component("CDEC1", "100 nF 50 V X7R; Murata GRM21BR71H104KA01L", [pn("CDEC1", "1", "VCC1", "PI_3V3_CANDIDATE", "left"), pn("CDEC1", "2", "GND1", "COMPUTE_0V", "right")], "EXACT COMPONENT CANDIDATE - PLACEMENT/PCB HOLD", "Place at UOBS1 within TI guidance; received capacitance and layout remain open.", position=(145, 230), width=68)
    cdec2 = Component("CDEC2", "100 nF 50 V X7R; Murata GRM21BR71H104KA01L", [pn("CDEC2", "1", "VCC1", "PI_3V3_CANDIDATE", "left"), pn("CDEC2", "2", "GND1", "COMPUTE_0V", "right")], "EXACT COMPONENT CANDIDATE - PLACEMENT/PCB HOLD", "Place at UOBS2 within TI guidance; received capacitance and layout remain open.", position=(285, 230), width=68)
    s4 = Sheet(4, "04_compute_outputs.kicad_sch", "Fail-low compute outputs", "Four 1 kohm series outputs and 10 kohm pulldowns; Pi pins remain selection required.", compact=True)
    s4.components = outputs + [cdec1, cdec2]
    s4.notes = ["Two ISO1212 devices plus four pulldowns screen at no more than 5.0 mA from 3.3 V; this is not a Pi external-load approval.", "Exact Pi GPIOs, header contacts, thresholds, pulls, boot state and cable remain SELECTION REQUIRED."]

    sheets = [s1, s2, s3, s4]
    items = [component for sheet in sheets for component in sheet.components]
    counts = Counter(pin.net for component in items for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 runtime observation candidate"))\n)\n', encoding="utf-8")
    root_uuid = model.uid("root-hr-v0-runtime-observation-interface-p01")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["sheet", "reference", "terminal", "function", "net", "state"], [(sheet.filename, component.ref, pin.number, pin.name, pin.net, component.status) for sheet in sheets for component in sheet.components for pin in component.pins])
    write_csv(ECAD / "bom.csv", ["reference", "value", "quantity", "state"], [(component.ref, component.value, str(component.quantity), component.status) for component in items if component.quantity])
    write_csv(ECAD / "net-schedule.csv", ["net", "node_count", "nodes"], [(net, str(count), " | ".join(f"{sheet.filename}:{component.ref}:{pin.number}" for sheet in sheets for component in sheet.components for pin in component.pins if pin.net == net)) for net, count in sorted(counts.items())])
    write_csv(ECAD / "load-budget.csv", ["load_id", "net", "architecture", "input_screen", "current_basis", "derived_result", "margin_or_condition", "state"], LOADS)
    write_csv(ECAD / "selection-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)
    write_csv(ECAD / "source-register.csv", ["source_id", "manufacturer", "document", "revision", "date", "official_url", "use_and_limit"], SOURCES)

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
    children = sorted(path for path in output.glob("*.svg") if path.name != f"{PROJECT}.svg")
    for index, source in enumerate(children, start=1):
        source.replace(output / f"runtime-observation-{index}.svg")
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs_and_web() -> None:
    DOC.write_text(f'''# HR-V0 runtime observation interface {REV}\n\n**{WARNING}**\n\nThis correction turns the four positive diagnostic states identified in R200 into a connected native KiCad evaluation candidate. It does not select Raspberry Pi GPIO pins, release a PCB or harness, add any safety function, or authorize a connection.\n\n## Architecture\n\nTwo exact TI `ISO1212DBQ` candidates receive `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS`, and `K2_STATUS`. Every channel uses the exact controlled Type-3 network: Vishay `MMA02040C1001FB300` 1.00 kohm RTHR, Panasonic `ERJ6ENF5620V` 562 ohm RSENSE, and TDK `CGA3E2X7R1H103K080AA` 10 nF CIN. SRA1, K1, and K2 also use Vishay `CRCW12102K70FKEA` 2.70 kohm shunts. SR1 does not, because its Y32 output already drives H1.\n\nField FGND connects only to `SAFETY_0V`; logic GND1 connects only to `COMPUTE_0V`. This preserves a proposed isolated boundary in the schematic, but gives no system insulation or functional-safety credit. SUB pins remain intentionally unconnected and require their own floating copper under TI layout guidance.\n\n## Calculation results\n\n- ISO1212 Type-3 current is screened at 2.05 to 2.75 mA per active channel.\n- SRA1/K1/K2 total status current is 10.41 to 12.18 mA with resistor and rail tolerance. Each 2.70 kohm shunt dissipates at most 0.238 W, 47.6% of its 0.5 W 70 C rating before enclosure derating.\n- At Schneider's 17 V signalling minimum, the K1/K2 screen is 8.28 mA, above the 5 mA minimum. Installed voltage and physical contact performance remain open.\n- Pilz Y32 residual current of 0.1 mA produces no more than 0.27 V across the nominal 2.70 kohm shunt, below the 8.7 V maximum-low threshold screen.\n- SR1's catalog current screen is 7 mA H1 plus 2.75 mA receiver = 9.75 mA, leaving 10.25 mA to Pilz's 20 mA limit. This is not closure: the exact received H1 maximum current is unknown, and a 5 V Y32 drop on the 22.8 V rail can leave only 17.8 V for a 24 V light whose published voltage range begins at 21.6 V.\n- Two ISO1212 logic sides plus four 10 kohm pulldowns screen at no more than 5.0 mA from 3.3 V. Raspberry Pi source capacity, GPIO thresholds, exact pins, boot pulls, cable and back-power behavior remain selection and HIL items.\n\n## EMC and fault boundary\n\nTI SLLSEY7G Table 8-1 reports the 562 ohm / 1 kohm / 10 nF Type-3 network at +/-1 kV line-to-PE and line-to-line, +/-500 V line-to-FGND surge, +/-6 kV IEC ESD and +/-4 kV EFT under TI's test arrangement. Those component-level application results are not a Project Button enclosure or cable qualification. TI also requires the high-voltage side of RTHR at least 4 mm from device/CIN/RSENSE pins and local 100 nF VCC1 bypassing.\n\nAll ten holds in `selection-holds.csv` remain open. The interface is diagnostic only; no output may command, restore, latch or preserve motion. ERC 0/0 proves only the encoded graph and annotations.\n''', encoding="utf-8")
    WEB.mkdir(parents=True, exist_ok=True)
    load_rows = "".join(f"<tr><td>{html.escape(r[1])}</td><td>{html.escape(r[4])}</td><td>{html.escape(r[5])}</td><td>{html.escape(r[7])}</td></tr>" for r in LOADS)
    hold_rows = "".join(f"<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td></tr>" for r in HOLDS)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#7b1e1e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,4vw,3rem);background:var(--ink);color:white}}main{{max-width:1180px;margin:auto;padding:1rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.25rem)}}.warning{{background:var(--gold);color:#211700;border:3px solid #211700;padding:.8rem;font-weight:800}}.flow{{display:grid;grid-template-columns:repeat(7,max-content);gap:.7rem;align-items:center;overflow:auto;background:white;border:2px solid var(--blue);padding:1rem}}.box{{min-width:155px;padding:.9rem;border:2px solid var(--blue);border-radius:10px}}.arrow{{font-size:1.5rem}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}}.metric{{background:white;border:2px solid var(--blue);border-radius:10px;padding:1rem}}.metric strong{{display:block;font-size:1.5rem}}.table,.diagram{{overflow:auto;background:white;border:2px solid var(--blue);margin:1rem 0}}table{{border-collapse:collapse;min-width:900px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #adc9df}}th{{background:var(--sky)}}.diagram object{{display:block;min-width:960px;width:100%;height:620px}}small{{font-size:14px}}footer{{background:var(--ink);color:white;padding:1rem;margin-top:2rem}}@media(max-width:600px){{main{{padding:.75rem}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - {DATE}</p><h1>Four status lines, isolated from compute.</h1><p>A connected evaluation schematic for diagnostics only. Raspberry Pi pins, PCB, harness and powered evidence are deliberately not released.</p></header><main><h2>Signal path</h2><div class="flow"><div class="box">24 V status<br><small>SR1 / SRA1 / K1 / K2</small></div><span class="arrow">-&gt;</span><div class="box">Type-3 input<br><small>1 kohm + 562 ohm + 10 nF</small></div><span class="arrow">-&gt;</span><div class="box">ISO1212 barrier<br><small>field FGND / logic GND1</small></div><span class="arrow">-&gt;</span><div class="box">fail-low output<br><small>1 kohm series + 10 kohm pull</small></div></div><h2>What the arithmetic says</h2><div class="metrics"><div class="metric"><strong>10.41-12.18 mA</strong>SRA1/K1/K2 channel load screen</div><div class="metric"><strong>0.238 W</strong>maximum 2.70 kohm shunt screen</div><div class="metric"><strong>9.75 mA</strong>SR1 catalog-only H1 + receiver screen</div><div class="metric"><strong>&le;5.0 mA</strong>3.3 V logic-load calculation screen</div></div><div class="table"><table><thead><tr><th>Net</th><th>Current basis</th><th>Derived result</th><th>State</th></tr></thead><tbody>{load_rows}</tbody></table></div><h2>Native KiCad sheets</h2><p>These are browser-readable exports of the same native source used for ERC and netlisting.</p><div class="diagram"><object data="../../../electrical/kicad/hr-v0-runtime-observation-interface-p0.1/output/runtime-observation-1.svg" type="image/svg+xml">Open boundaries schematic SVG.</object></div><div class="diagram"><object data="../../../electrical/kicad/hr-v0-runtime-observation-interface-p0.1/output/runtime-observation-2.svg" type="image/svg+xml">Open SR1/SRA1 schematic SVG.</object></div><div class="diagram"><object data="../../../electrical/kicad/hr-v0-runtime-observation-interface-p0.1/output/runtime-observation-3.svg" type="image/svg+xml">Open K1/K2 schematic SVG.</object></div><div class="diagram"><object data="../../../electrical/kicad/hr-v0-runtime-observation-interface-p0.1/output/runtime-observation-4.svg" type="image/svg+xml">Open compute-output schematic SVG.</object></div><h2>Ten gates still open</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence needed</th></tr></thead><tbody>{hold_rows}</tbody></table></div><footer>Diagnostic-only architecture. No procurement, fabrication, connection, powered testing, motion or energization authority.</footer></main></body></html>''', encoding="utf-8")


def manifest() -> None:
    rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (ECAD / "SOURCE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(rows)


def main() -> int:
    build_ecad(); write_docs_and_web(); manifest()
    print(f"Generated {IDENTIFIER}: 5 native sheets, 4 diagnostic channels, 10 open holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
