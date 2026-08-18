#!/usr/bin/env python3
"""Generate the HR-V0 P1.21 control-only no-load fixture candidate.

The fixture is intentionally incapable of carrying actuator power or commanding
motion.  It binds its DUT terminals to the P1.21 connector schedule while
keeping fixture-only substitutions (isolated contact sensing and dry-contact
EDM simulation) explicit.  It grants no authority to connect or energize.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
APP = ROOT / "safety/hr-v0-p121-application-evidence-p0.1"
OUT = ROOT / "test-fixtures/hr-v0-p121-no-load-fixture-p0.1"
REL = ROOT / "release/hr-v0/p121-no-load-fixture-p0.1"
PROJECT = "hr-v0-p121-no-load-fixture-p0.1"
IDENTIFIER = "HR-V0-P121-NO-LOAD-FIXTURE-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_model():
    source = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hrv0_fixture_model", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("native KiCad model unavailable")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.OUT = OUT
    model.PROJECT = PROJECT
    model.REV = "P0.1"
    model.DATE = DATE
    model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 P1.21 NO-LOAD FIXTURE P0.1"
    model.PROJECT_SUBTITLE = "Control-only A1-gating evidence fixture; actuator power physically excluded."
    return model


def component(model, ref, value, pins, description, position, width=108, status="FIXTURE CANDIDATE / VALIDATION OPEN"):
    return model.Component(
        ref=ref,
        value=value,
        pins=[model.pn(ref, number, name, net, side) for number, name, net, side in pins],
        status=status,
        description=description,
        datasheet="CONTROLLED SOURCE BINDING IN source-register.csv",
        evidence="P1.21 terminal identity or fixture-only boundary as stated",
        position=position,
        width=width,
    )


def build_sheets(model):
    sheets = []

    s1 = model.Sheet(1, "01_power_and_absence_boundary.kicad_sch", "Isolated 24 V control source and hard exclusion boundary", "No mains inside fixture; no actuator source, actuator rail, contactor coils, contactor power poles or actuators.")
    s1.components = [
        component(model, "PSFIX", "ISOLATED CURRENT-LIMITED 24 V SOURCE - SELECTION REQUIRED", [("+", "SOURCE POSITIVE", "FIX_24V_RAW", "right"), ("-", "SOURCE RETURN", "SAFETY_0V", "right")], "Exact source, limits, protection, isolation and calibration remain AUTH-006/AUTH-007 holds.", (70, 90), 105),
        component(model, "EDISC", "MANUAL EMERGENCY ISOLATION - SELECTION REQUIRED", [("1", "SOURCE IN", "FIX_24V_RAW", "left"), ("2", "ISOLATED OUT", "SAFETY_24V_RAW", "right")], "Visible, reachable fixture isolation device; exact device and DC rating remain unselected.", (205, 90), 95),
        component(model, "F24", "P1.21 F24 - SELECTION REQUIRED", [("IN", "SOURCE +24 V", "SAFETY_24V_RAW", "left"), ("OUT", "PROTECTED +24 V", "SAFETY_24V", "right")], "DUT protection position from P1.21. No fuse value is released.", (335, 90), 85),
        component(model, "XD24", "P1.21 CONTROL +24 V DISTRIBUTION", [("LINE", "PROTECTED FEED", "SAFETY_24V", "left"), ("01", "SR1/SRA1 FEED", "SAFETY_24V", "right"), ("02", "WATCHDOG FEED", "SAFETY_24V", "right"), ("03", "PCB FEED", "SAFETY_24V", "right")], "Fixture uses only enumerated control loads; terminal hardware remains received/physical review work.", (75, 220), 105),
        component(model, "XD0", "P1.21 CONTROL 0 V DISTRIBUTION", [("LINE", "SOURCE RETURN", "SAFETY_0V", "left"), ("01", "SR1/SRA1 RETURN", "SAFETY_0V", "right"), ("02", "WATCHDOG RETURN", "SAFETY_0V", "right"), ("03", "PCB RETURN", "SAFETY_0V", "right")], "No proposed DC 0 V/PE bond is made by this isolated bench fixture.", (215, 220), 105),
        component(model, "ABSENT", "PHYSICAL ABSENCE INTERLOCK", [("A", "ACTUATOR SOURCE", "PROHIBITED_ACTUATOR_SOURCE", "left"), ("B", "K1/K2 COILS AND POWER POLES", "PROHIBITED_CONTACTORS", "left"), ("C", "ALL ACTUATORS", "PROHIBITED_ACTUATORS", "left"), ("D", "MOTION COMPUTER", "PROHIBITED_MOTION", "left")], "These items are absence inspections, not electrical connections. Any presence is a stop-work failure.", (350, 220), 110, "MANDATORY ABSENCE / NOT EXECUTED"),
    ]
    s1.notes = ["The source output remains OFF until every authorization prerequisite is signed.", "J24/PSU2 may not be used unless the exact source/cord/protection application is separately selected and reviewed."]
    sheets.append(s1)

    s2 = model.Sheet(2, "02_estop_and_eligibility_chain.kicad_sch", "Native SR1/S0 and SRA1 input/start chains", "Actual P1.21 terminals; contactor mirror feedback is replaced only by the explicit dry-contact EDM simulator.")
    s2.components = [
        component(model, "SR1", "P1.21 SR1 SAFETY RELAY", [("A1", "24 V SUPPLY", "SAFETY_24V", "left"), ("A2", "0 V SUPPLY", "SAFETY_0V", "left"), ("S11", "CH1 FEED", "SR1_S11", "right"), ("S12", "CH1 RETURN / START FEED", "SR1_S12", "right"), ("S21", "CH2 FEED", "SR1_S21", "right"), ("S22", "CH2 RETURN", "SR1_S22", "right"), ("S34", "START RETURN", "SR1_START_RETURN", "right"), ("13", "OUT1 IN", "SRA1_S11", "right"), ("14", "OUT1 OUT", "SRA1_S12", "right"), ("23", "OUT2 IN", "SRA1_S21", "right"), ("24", "OUT2 OUT", "SRA1_S22", "right")], "Terminal/net identity copied from P1.21; exact article and qualified application remain outside fixture release.", (75, 95), 90),
        component(model, "S0", "P1.21 DUAL-CHANNEL E-STOP", [("R-1", "CH1 NC IN", "SR1_S11", "left"), ("R-2", "CH1 NC OUT", "SR1_S12", "left"), ("L-1", "CH2 NC IN", "SR1_S21", "left"), ("L-2", "CH2 NC OUT", "SR1_S22", "left")], "Both channels require independent state capture; received terminal positions remain verification work.", (205, 65), 86),
        component(model, "S1", "P1.21 SR1 RESET", [("TBD-R1", "RESET IN", "SR1_S12", "left"), ("TBD-R2", "RESET OUT", "SR1_START_RETURN", "right")], "Terminal mapping remains received-lot verification work.", (205, 150), 80),
        component(model, "SRA1", "P1.21 PNOZ S4 750104 CANDIDATE", [("A1", "WATCHDOG-GATED 24 V", "SRA1_A1_WD_GATED", "left"), ("A2", "0 V", "SAFETY_0V", "left"), ("S11", "CH1 FEED", "SRA1_S11", "left"), ("S12", "CH1 RETURN / ARM FEED", "SRA1_S12", "left"), ("S21", "CH2 FEED", "SRA1_S21", "left"), ("S22", "CH2 RETURN", "SRA1_S22", "left"), ("S34", "START / EDM RETURN", "SRA1_START_RETURN", "left"), ("13", "OUT1 CONTACT A", "ISO_SRA1_13", "right"), ("14", "OUT1 CONTACT B", "ISO_SRA1_14", "right"), ("23", "OUT2 CONTACT A", "ISO_SRA1_23", "right"), ("24", "OUT2 CONTACT B", "ISO_SRA1_24", "right"), ("33", "OUT3 CONTACT A", "ISO_SRA1_33", "right"), ("34", "OUT3 CONTACT B", "ISO_SRA1_34", "right"), ("41", "AUX NC A", "ISO_SRA1_41", "right"), ("42", "AUX NC B", "ISO_SRA1_42", "right"), ("Y32", "STATUS", "SRA1_STATUS", "right")], "Output contact terminals are deliberately removed from the P1.21 load path and connected only to isolated low-energy state channels.", (75, 220), 98),
        component(model, "S2", "P1.21 ARM PUSHBUTTON", [("TBD-A1", "ARM IN", "SRA1_S12", "left"), ("TBD-A2", "ARM OUT", "ARM_AFTER_S2", "right")], "Falling edge must be independently timestamped; terminal mapping remains received-lot work.", (320, 65), 80),
        component(model, "EDMSIM", "CONFIGURATION-CONTROLLED DRY-CONTACT EDM SIMULATOR", [("K1-21", "SIMULATED K1 MIRROR IN", "ARM_AFTER_S2", "left"), ("K1-22", "SIMULATED K1 MIRROR OUT", "EDM_K1_OUT", "right"), ("K2-21", "SIMULATED K2 MIRROR IN", "EDM_K1_OUT", "left"), ("K2-22", "SIMULATED K2 MIRROR OUT", "SRA1_START_RETURN", "right")], "K1/K2 contactors are absent. Exact simulator switch hardware, anti-tamper state indication and contact rating are SELECTION REQUIRED.", (320, 165), 90),
    ]
    s2.notes = ["SRA1 13-14, 23-24, 33-34 and 41-42 are not tied to 24 V in this fixture.", "A valid ARM falling edge may change only isolated instrument indications; no coil or actuator load exists."]
    sheets.append(s2)

    s3 = model.Sheet(3, "03_watchdog_gate_and_stimulus.kicad_sch", "Dual ordinary-relay A1 gate and heartbeat boundary", "Two Phoenix 2967060 candidates in series; zero safety credit; watchdog PCB and firmware remain unaccepted.")
    s3.components = [
        component(model, "KWD1", "P1.21 PHOENIX 2967060 CANDIDATE", [("11", "GATE IN", "SAFETY_24V", "left"), ("14", "GATE STAGE 1", "WD_SRA1_SUPPLY_INTERMEDIATE", "right"), ("21", "NC FEEDBACK COM", "SAFETY_24V", "left"), ("22", "NC FEEDBACK", "WD1_NC_24V", "right"), ("A1", "COIL +", "SAFETY_24V", "left"), ("A2", "COIL SINK", "WD1_COIL_N", "right")], "Exact P1.21 terminals. Ordinary relay; no safety credit.", (75, 95), 100),
        component(model, "KWD2", "P1.21 PHOENIX 2967060 CANDIDATE", [("11", "GATE STAGE 1", "WD_SRA1_SUPPLY_INTERMEDIATE", "left"), ("14", "SRA1 A1 GATED", "SRA1_A1_WD_GATED", "right"), ("21", "NC FEEDBACK COM", "SAFETY_24V", "left"), ("22", "NC FEEDBACK", "WD2_NC_24V", "right"), ("A1", "COIL +", "SAFETY_24V", "left"), ("A2", "COIL SINK", "WD2_COIL_N", "right")], "Exact P1.21 terminals. Ordinary relay; no safety credit.", (210, 95), 100),
        component(model, "JWP1", "P1.21 WATCHDOG PCB POWER/COIL INTERFACE", [("1", "SAFETY +24 V", "SAFETY_24V", "left"), ("2", "SAFETY 0 V", "SAFETY_0V", "left"), ("3", "KWD1 COIL SINK", "WD1_COIL_N", "right"), ("4", "KWD2 COIL SINK", "WD2_COIL_N", "right")], "Connector pin identity from P1.21; physical connector and PCB validation remain open.", (345, 70), 100),
        component(model, "JWF1", "P1.21 WATCHDOG FEEDBACK INTERFACE", [("1", "KWD1 NC +24 V", "WD1_NC_24V", "left"), ("2", "KWD2 NC +24 V", "WD2_NC_24V", "left")], "Connector pin identity from P1.21.", (345, 180), 95),
        component(model, "JWH1", "P1.21 HEARTBEAT INTERFACE", [("1", "COMPUTE HEARTBEAT", "PI_HEARTBEAT", "left"), ("2", "COMPUTE 0 V", "COMPUTE_0V", "left")], "Heartbeat source must be isolated, configuration controlled and timestamped.", (75, 220), 95),
        component(model, "HBSRC", "ISOLATED PATTERN SOURCE / LOGGER - SELECTION REQUIRED", [("HB", "HEARTBEAT OUT", "PI_HEARTBEAT", "right"), ("RET", "ISOLATED RETURN", "COMPUTE_0V", "right"), ("LOG", "COMMON TIME BASE", "FIX_TIMEBASE", "right")], "No Raspberry Pi or motion supervisor is required in the no-load fixture; exact pattern source remains unselected.", (230, 220), 105),
    ]
    s3.notes = ["Bypassing both KWD gate contacts is permitted only as the controlled TEST-011 fault stimulus.", "Any PCB discrepancy, coil chatter or unexpected SRA1 output indication is a stop-work failure."]
    sheets.append(s3)

    s4 = model.Sheet(4, "04_isolated_measurement_fanout.kicad_sch", "Fifteen required signals on one time base", "Every measurement channel remains SELECTION REQUIRED until isolation, rating, bandwidth and calibration are approved.")
    s4.components = [
        component(model, "DAQV", "ISOLATED VOLTAGE/CURRENT ACQUISITION", [("V1", "SAFETY_24V", "SAFETY_24V", "left"), ("V2", "SRA1 A1", "SRA1_A1_WD_GATED", "left"), ("V3", "SAFETY 0V", "SAFETY_0V", "left"), ("V4", "SRA1 S12", "SRA1_S12", "left"), ("V5", "SRA1 S22", "SRA1_S22", "left"), ("V6", "SRA1 S34", "SRA1_START_RETURN", "left"), ("T", "COMMON TIMEBASE", "FIX_TIMEBASE", "right")], "SIG-001 through SIG-006. Exact probes and current measurement topology remain unselected.", (70, 105), 100),
        component(model, "DAQC", "ISOLATED LOW-ENERGY CONTACT ACQUISITION", [("7A", "SRA1 13", "ISO_SRA1_13", "left"), ("7B", "SRA1 14", "ISO_SRA1_14", "left"), ("8A", "SRA1 23", "ISO_SRA1_23", "left"), ("8B", "SRA1 24", "ISO_SRA1_24", "left"), ("9A", "SRA1 33", "ISO_SRA1_33", "left"), ("9B", "SRA1 34", "ISO_SRA1_34", "left"), ("10A", "KWD1 11", "SAFETY_24V", "left"), ("10B", "KWD1 14", "WD_SRA1_SUPPLY_INTERMEDIATE", "left"), ("11A", "KWD2 11", "WD_SRA1_SUPPLY_INTERMEDIATE", "left"), ("11B", "KWD2 14", "SRA1_A1_WD_GATED", "left"), ("T", "COMMON TIMEBASE", "FIX_TIMEBASE", "right")], "SIG-007 through SIG-011. Instrument excitation must be isolated and low energy.", (200, 115), 105),
        component(model, "DAQS", "ISOLATED STIMULUS/STATE LOGGER", [("12", "HEARTBEAT", "PI_HEARTBEAT", "left"), ("13", "ARM SWITCH", "ARM_AFTER_S2", "left"), ("14A", "E-STOP CH1", "SR1_S12", "left"), ("14B", "E-STOP CH2", "SR1_S22", "left"), ("15A", "EDM K1", "EDM_K1_OUT", "left"), ("15B", "EDM RETURN", "SRA1_START_RETURN", "left"), ("T", "COMMON TIMEBASE", "FIX_TIMEBASE", "right")], "SIG-012 through SIG-015. Exact dry-contact fixtures and logger remain unselected.", (345, 105), 100),
        component(model, "STOPLOG", "FAIL-CLOSED EVENT RECORD", [("T", "COMMON TIMEBASE", "FIX_TIMEBASE", "left"), ("OFF", "SOURCE-OFF EVENT", "FIX_SOURCE_OFF_EVENT", "left")], "Raw data must be preserved before analysis. Missing, clipped, asynchronous or ambiguous data are FAIL.", (345, 230), 100),
    ]
    s4.notes = ["No oscilloscope or DAQ channel is assumed safe merely because it is isolated in marketing language.", "Every channel requires an exact model, connection diagram, rating, calibration and common-timebase acceptance before use."]
    sheets.append(s4)
    return sheets


def write_ecad(model, sheets):
    root_uuid = model.uid("hr-v0-p121-no-load-fixture-root")
    counts = Counter(pin.net for sheet in sheets for item in sheet.components for pin in item.pins)
    wires = model.build_wire_numbers(sheets, counts)
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wires), encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps({"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}, indent=2) + "\n", encoding="utf-8")
    components = [item for sheet in sheets for item in sheet.components]
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for item in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 P1.21 no-load fixture symbols"))\n)\n', encoding="utf-8")
    model.write_tables(sheets, counts, wires)
    validation, output = OUT / "validation", OUT / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    commands = [
        [str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")],
    ]
    log = []
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        log.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
            raise SystemExit(result.returncode)
    (validation / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def p2p_rows():
    # DUT endpoints use exact P1.21 terminal spellings. Fixture-only endpoints
    # are prefixed FIX and are never represented as robot terminals.
    entries = [
        ("P2P-001", "FIX:PSFIX:+", "FIX:EDISC:1", "FIX_24V_RAW", "fixture source lead"),
        ("P2P-002", "FIX:EDISC:2", "F24:IN", "SAFETY_24V_RAW", "source isolation to P1.21 protection position"),
        ("P2P-003", "F24:OUT", "XD24:LINE", "SAFETY_24V", "protected control feed"),
        ("P2P-004", "FIX:PSFIX:-", "XD0:LINE", "SAFETY_0V", "isolated source return"),
        ("P2P-005", "XD24:01", "SR1:A1", "SAFETY_24V", "SR1 control supply"),
        ("P2P-006", "XD0:01", "SR1:A2", "SAFETY_0V", "SR1 control return"),
        ("P2P-007", "SR1:S11", "S0:R-1", "SR1_S11", "E-stop channel 1 feed"),
        ("P2P-008", "S0:R-2", "SR1:S12", "SR1_S12", "E-stop channel 1 return"),
        ("P2P-009", "SR1:S21", "S0:L-1", "SR1_S21", "E-stop channel 2 feed"),
        ("P2P-010", "S0:L-2", "SR1:S22", "SR1_S22", "E-stop channel 2 return"),
        ("P2P-011", "SR1:S12", "S1:TBD-R1", "SR1_S12", "SR1 reset feed"),
        ("P2P-012", "S1:TBD-R2", "SR1:S34", "SR1_START_RETURN", "SR1 reset return"),
        ("P2P-013", "SR1:13", "SRA1:S11", "SRA1_S11", "SRA1 channel 1 feed through SR1 output"),
        ("P2P-014", "SR1:14", "SRA1:S12", "SRA1_S12", "SRA1 channel 1 return through SR1 output"),
        ("P2P-015", "SR1:23", "SRA1:S21", "SRA1_S21", "SRA1 channel 2 feed through SR1 output"),
        ("P2P-016", "SR1:24", "SRA1:S22", "SRA1_S22", "SRA1 channel 2 return through SR1 output"),
        ("P2P-017", "XD24:02", "KWD1:11", "SAFETY_24V", "watchdog gate input"),
        ("P2P-018", "KWD1:14", "KWD2:11", "WD_SRA1_SUPPLY_INTERMEDIATE", "watchdog gate series link"),
        ("P2P-019", "KWD2:14", "SRA1:A1", "SRA1_A1_WD_GATED", "watchdog-gated SRA1 supply"),
        ("P2P-020", "XD0:02", "SRA1:A2", "SAFETY_0V", "SRA1 supply return"),
        ("P2P-021", "XD24:03", "JWP1:1", "SAFETY_24V", "watchdog PCB supply"),
        ("P2P-022", "XD0:03", "JWP1:2", "SAFETY_0V", "watchdog PCB return"),
        ("P2P-023", "KWD1:A1", "JWP1:1", "SAFETY_24V", "KWD1 coil positive"),
        ("P2P-024", "KWD1:A2", "JWP1:3", "WD1_COIL_N", "KWD1 coil sink"),
        ("P2P-025", "KWD2:A1", "JWP1:1", "SAFETY_24V", "KWD2 coil positive"),
        ("P2P-026", "KWD2:A2", "JWP1:4", "WD2_COIL_N", "KWD2 coil sink"),
        ("P2P-027", "XD24:02", "KWD1:21", "SAFETY_24V", "KWD1 feedback common"),
        ("P2P-028", "KWD1:22", "JWF1:1", "WD1_NC_24V", "KWD1 NC feedback sense"),
        ("P2P-029", "XD24:02", "KWD2:21", "SAFETY_24V", "KWD2 feedback common"),
        ("P2P-030", "KWD2:22", "JWF1:2", "WD2_NC_24V", "KWD2 NC feedback sense"),
        ("P2P-031", "SRA1:S12", "S2:TBD-A1", "SRA1_S12", "ARM falling-edge feed"),
        ("P2P-032", "S2:TBD-A2", "FIX:EDMSIM:K1-21", "ARM_AFTER_S2", "ARM to EDM simulator"),
        ("P2P-033", "FIX:EDMSIM:K1-22", "FIX:EDMSIM:K2-21", "EDM_K1_OUT", "simulated K1-to-K2 mirror series link"),
        ("P2P-034", "FIX:EDMSIM:K2-22", "SRA1:S34", "SRA1_START_RETURN", "EDM return to SRA1"),
        ("P2P-035", "FIX:HBSRC:HB", "JWH1:1", "PI_HEARTBEAT", "isolated heartbeat stimulus"),
        ("P2P-036", "FIX:HBSRC:RET", "JWH1:2", "COMPUTE_0V", "isolated heartbeat return"),
        ("P2P-037", "SRA1:13", "FIX:DAQC:7A", "ISO_SRA1_13", "isolated low-energy continuity only"),
        ("P2P-038", "SRA1:14", "FIX:DAQC:7B", "ISO_SRA1_14", "isolated low-energy continuity only"),
        ("P2P-039", "SRA1:23", "FIX:DAQC:8A", "ISO_SRA1_23", "isolated low-energy continuity only"),
        ("P2P-040", "SRA1:24", "FIX:DAQC:8B", "ISO_SRA1_24", "isolated low-energy continuity only"),
        ("P2P-041", "SRA1:33", "FIX:DAQC:9A", "ISO_SRA1_33", "isolated low-energy continuity only"),
        ("P2P-042", "SRA1:34", "FIX:DAQC:9B", "ISO_SRA1_34", "isolated low-energy continuity only"),
    ]
    return [{"wire_id": a, "from_terminal": b, "to_terminal": c, "fixture_net": d, "function": e, "installation_state": "NOT ASSEMBLED", "inspection_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING} for a, b, c, d, e in entries]


def signal_rows():
    source = read_csv(APP / "signal-capture-register.csv")
    bindings = {
        "SIG-001": "DAQV:V1 / source current channel", "SIG-002": "DAQV:V2", "SIG-003": "DAQV:V3", "SIG-004": "DAQV:V4", "SIG-005": "DAQV:V5", "SIG-006": "DAQV:V6",
        "SIG-007": "DAQC:7A-7B", "SIG-008": "DAQC:8A-8B", "SIG-009": "DAQC:9A-9B", "SIG-010": "DAQC:10A-10B", "SIG-011": "DAQC:11A-11B",
        "SIG-012": "DAQS:12", "SIG-013": "DAQS:13", "SIG-014": "DAQS:14A and 14B independently", "SIG-015": "DAQS:15A and 15B",
    }
    return [row | {"fixture_binding": bindings[row["signal_id"]], "channel_selection": "SELECTION REQUIRED", "execution_state": "NOT EXECUTED"} for row in source]


def write_registers():
    write_csv(OUT / "point-to-point-schedule.csv", p2p_rows())
    write_csv(OUT / "signal-binding-register.csv", signal_rows())
    write_csv(OUT / "test-binding-register.csv", [row | {"fixture_revision": IDENTIFIER, "authorization": "PROHIBITED UNTIL AUTH-001 THROUGH AUTH-010 CLOSE"} for row in read_csv(APP / "test-case-register.csv")])
    write_csv(OUT / "authorization-gate-register.csv", [row | {"fixture_disposition": "ARTIFACT ISSUED; GATE REMAINS OPEN" if row["prerequisite_id"] == "AUTH-004" else "UNCHANGED OPEN EXTERNAL/PHYSICAL GATE", "warning": WARNING} for row in read_csv(APP / "authorization-prerequisites.csv")])
    write_csv(OUT / "physical-absence-register.csv", [
        {"absence_id": "ABS-001", "prohibited_item": "PSA1 / JA1 actuator source and all ACT_12V conductors", "verification": "visual inspection plus continuity to fixture terminals", "required_result": "PHYSICALLY ABSENT / OPEN CIRCUIT", "state": "NOT EXECUTED", "authority": AUTHORITY},
        {"absence_id": "ABS-002", "prohibited_item": "K1 and K2 contactor coils, main poles and power conductors", "verification": "visual inspection; only labeled EDMSIM dry contacts present", "required_result": "PHYSICALLY ABSENT", "state": "NOT EXECUTED", "authority": AUTHORITY},
        {"absence_id": "ABS-003", "prohibited_item": "all actuators, U2D2, actuator buses and mechanical joints", "verification": "fixture boundary inspection", "required_result": "PHYSICALLY ABSENT", "state": "NOT EXECUTED", "authority": AUTHORITY},
        {"absence_id": "ABS-004", "prohibited_item": "mains wiring inside fixture", "verification": "enclosure inspection", "required_result": "PHYSICALLY ABSENT; external isolated SELV/PELV source only after selection", "state": "NOT EXECUTED", "authority": AUTHORITY},
        {"absence_id": "ABS-005", "prohibited_item": "AI, conversation agent or motion supervisor command path", "verification": "software/connection inventory", "required_result": "PHYSICALLY AND LOGICALLY ABSENT", "state": "NOT EXECUTED", "authority": AUTHORITY},
    ])
    write_csv(OUT / "fixture-layout-register.csv", [
        {"item": "LAY-001", "zone": "A / source isolation", "x_mm": 20, "y_mm": 30, "width_mm": 110, "height_mm": 80, "mounting": "DIN rail or insulated stand-off selection required", "clearance": "40 mm service margin", "state": "PLANNING LAYOUT / RECEIVED FIT OPEN"},
        {"item": "LAY-002", "zone": "B / SR1 + SRA1", "x_mm": 155, "y_mm": 30, "width_mm": 150, "height_mm": 120, "mounting": "35 mm DIN rail candidate", "clearance": "manufacturer spacing and terminal access verification open", "state": "PLANNING LAYOUT / RECEIVED FIT OPEN"},
        {"item": "LAY-003", "zone": "C / KWD1 + KWD2", "x_mm": 330, "y_mm": 30, "width_mm": 145, "height_mm": 120, "mounting": "35 mm DIN rail candidate", "clearance": "manufacturer spacing and terminal access verification open", "state": "PLANNING LAYOUT / RECEIVED FIT OPEN"},
        {"item": "LAY-004", "zone": "D / stimuli", "x_mm": 20, "y_mm": 180, "width_mm": 210, "height_mm": 105, "mounting": "panel controls / exact hardware selection required", "clearance": "finger access with cover closed", "state": "PLANNING LAYOUT / RECEIVED FIT OPEN"},
        {"item": "LAY-005", "zone": "E / isolated measurement", "x_mm": 255, "y_mm": 180, "width_mm": 220, "height_mm": 105, "mounting": "external instrument bulkhead / exact connectors required", "clearance": "probe leads segregated from control conductors", "state": "PLANNING LAYOUT / RECEIVED FIT OPEN"},
    ])
    write_csv(OUT / "candidate-bom.csv", [
        {"item": "FX-01", "qty": 1, "description": "PNOZ s4 750104 candidate for SRA1", "order_code": "Pilz 750104", "disposition": "RECEIVED IDENTITY/APPLICATION/QUALIFIED REVIEW OPEN", "authority": AUTHORITY},
        {"item": "FX-02", "qty": 2, "description": "ordinary relay modules for KWD1/KWD2", "order_code": "Phoenix Contact 2967060", "disposition": "RECEIVED IDENTITY/APPLICATION/QUALIFIED REVIEW OPEN; ZERO SAFETY CREDIT", "authority": AUTHORITY},
        {"item": "FX-03", "qty": 1, "description": "isolated current-limited 24 V source", "order_code": "SELECTION REQUIRED", "disposition": "AUTH-006 OPEN", "authority": AUTHORITY},
        {"item": "FX-04", "qty": 1, "description": "manual emergency DC isolation", "order_code": "SELECTION REQUIRED", "disposition": "AUTH-006 OPEN", "authority": AUTHORITY},
        {"item": "FX-05", "qty": 1, "description": "F24 branch protection", "order_code": "SELECTION REQUIRED", "disposition": "NO FUSE VALUE RELEASED", "authority": AUTHORITY},
        {"item": "FX-06", "qty": 1, "description": "isolated common-timebase voltage/current/contact acquisition", "order_code": "SELECTION REQUIRED", "disposition": "AUTH-007/AUTH-008 OPEN", "authority": AUTHORITY},
        {"item": "FX-07", "qty": 1, "description": "isolated heartbeat pattern source/logger", "order_code": "SELECTION REQUIRED", "disposition": "FIRMWARE/HARDWARE/HASH APPROVAL OPEN", "authority": AUTHORITY},
        {"item": "FX-08", "qty": 1, "description": "configuration-controlled dry-contact EDM simulator", "order_code": "SELECTION REQUIRED", "disposition": "ANTI-TAMPER/STATE INDICATION/CONTACT VERIFICATION OPEN", "authority": AUTHORITY},
        {"item": "FX-09", "qty": 1, "description": "560 x 320 mm candidate insulated backplate/enclosure", "order_code": "SELECTION REQUIRED", "disposition": "MATERIAL/ENCLOSURE/GUARD/DFM OPEN", "authority": AUTHORITY},
        {"item": "FX-10", "qty": 1, "description": "received SR1/S0/S1 control-chain articles", "order_code": "EXACT CURRENT CONFIGURATION RECORD REQUIRED", "disposition": "IDENTITY/TERMINAL/QUALIFIED REVIEW OPEN", "authority": AUTHORITY},
    ])
    write_csv(OUT / "source-register.csv", [
        {"source_id": "SRC-001", "artifact": "P1.21 connector schedule", "path": P121.relative_to(ROOT).as_posix() + "/connector-schedule.csv", "sha256": sha(P121 / "connector-schedule.csv"), "use": "authoritative DUT terminal/net identity", "boundary": "P1.21 remains unaccepted"},
        {"source_id": "SRC-002", "artifact": "P1.21 wire-number table", "path": P121.relative_to(ROOT).as_posix() + "/wire-number-table.csv", "sha256": sha(P121 / "wire-number-table.csv"), "use": "authoritative proposed conductor identity", "boundary": "physical installation remains open"},
        {"source_id": "SRC-003", "artifact": "P1.21 application evidence signal register", "path": APP.relative_to(ROOT).as_posix() + "/signal-capture-register.csv", "sha256": sha(APP / "signal-capture-register.csv"), "use": "15 required signals", "boundary": "instruments and limits remain unselected"},
        {"source_id": "SRC-004", "artifact": "P1.21 application evidence test register", "path": APP.relative_to(ROOT).as_posix() + "/test-case-register.csv", "sha256": sha(APP / "test-case-register.csv"), "use": "18 controlled future tests", "boundary": "all tests unexecuted"},
        {"source_id": "SRC-005", "artifact": "P1.21 authorization prerequisites", "path": APP.relative_to(ROOT).as_posix() + "/authorization-prerequisites.csv", "sha256": sha(APP / "authorization-prerequisites.csv"), "use": "AUTH-001 through AUTH-010 gate spine", "boundary": "all authorization gates remain open"},
        {"source_id": "SRC-006", "artifact": "fixture generator", "path": "tools/generate_hr_v0_p121_no_load_fixture_p01.py", "sha256": sha(ROOT / "tools/generate_hr_v0_p121_no_load_fixture_p01.py"), "use": "reproducible package generation", "boundary": "generated candidate only"},
        {"source_id": "SRC-007", "artifact": "fixture checker", "path": "tools/check_hr_v0_p121_no_load_fixture_p01.py", "sha256": sha(ROOT / "tools/check_hr_v0_p121_no_load_fixture_p01.py"), "use": "independent repository consistency checks", "boundary": "does not replace physical or qualified review"},
    ])
    write_csv(OUT / "open-holds.csv", [
        {"hold_id": "FX-H01", "evidence_required": "independent check of native fixture ECAD, point-to-point schedule and physical layout", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H02", "evidence_required": "Pilz/Phoenix written application responses and qualified disposition", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H03", "evidence_required": "received identity and terminal mapping for every DUT article", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H04", "evidence_required": "exact isolated source, protection and emergency isolation selection", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H05", "evidence_required": "exact isolated probes/DAQ/pattern source, calibration, ratings, bandwidth and connection diagrams", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H06", "evidence_required": "manufacturer-derived numeric limits and approved test-point grid", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H07", "evidence_required": "received-fit physical layout, enclosure, guards, DIN hardware, strain relief and labeling", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H08", "evidence_required": "executed unpowered continuity/isolation/absence inspection", "state": "OPEN", "authority": AUTHORITY},
        {"hold_id": "FX-H09", "evidence_required": "signed configuration-specific procedure and E2 control-only work authorization", "state": "OPEN", "authority": AUTHORITY},
    ])


def write_layout_svg():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" role="img" aria-labelledby="t d"><title id="t">HR-V0 P1.21 no-load fixture planning layout</title><desc id="d">A 560 by 320 millimetre candidate control-only fixture with source isolation, safety relays, watchdog relays, stimuli and isolated measurement zones. Actuator power is physically absent.</desc><style>text{{font-family:system-ui,sans-serif;fill:#072b52}}.h{{font-size:32px;font-weight:850}}.w{{font-size:20px;font-weight:850}}.b{{font-size:21px}}.s{{font-size:16px}}.z{{fill:#e6f6ff;stroke:#12699b;stroke-width:4}}.hold{{fill:#fff1b8;stroke:#946200;stroke-width:4}}.ban{{fill:#ffe3e3;stroke:#a11;stroke-width:4}}.rail{{stroke:#687888;stroke-width:10}}</style><rect width="1200" height="760" fill="#f8fcff"/><text x="40" y="29" class="w">PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION</text><text x="40" y="58" class="w">NOT APPROVED FOR POWERED TESTING, MOTION, OR ENERGIZATION</text><rect x="50" y="90" width="1100" height="610" rx="24" fill="white" stroke="#072b52" stroke-width="6"/><text x="80" y="135" class="h">560 x 320 mm planning envelope - received-fit check required</text><line x1="90" y1="280" x2="1110" y2="280" class="rail"/><rect x="90" y="165" width="210" height="90" rx="12" class="hold"/><text x="108" y="200" class="b">A - source isolation</text><text x="108" y="232" class="s">PSFIX / EDISC / F24</text><rect x="330" y="165" width="285" height="90" rx="12" class="z"/><text x="350" y="200" class="b">B - eligibility relays</text><text x="350" y="232" class="s">SR1 / SRA1</text><rect x="650" y="165" width="260" height="90" rx="12" class="z"/><text x="670" y="200" class="b">C - watchdog gate</text><text x="670" y="232" class="s">KWD1 / KWD2</text><rect x="90" y="345" width="430" height="180" rx="16" class="hold"/><text x="115" y="390" class="b">D - controlled stimuli</text><text x="115" y="430" class="s">S0 / S1 / S2 / EDMSIM / heartbeat</text><text x="115" y="470" class="s">All switch states independently timestamped</text><rect x="555" y="345" width="555" height="180" rx="16" class="z"/><text x="580" y="390" class="b">E - isolated measurement boundary</text><text x="580" y="430" class="s">15 required signals / one common time base</text><text x="580" y="470" class="s">Contact outputs use low-energy continuity only</text><rect x="90" y="565" width="1020" height="95" rx="16" class="ban"/><text x="115" y="603" class="b">PHYSICALLY ABSENT</text><text x="115" y="637" class="s">Actuator source / actuator rail / K1/K2 contactors / actuators / motion or AI path / mains</text></svg>'''
    (OUT / "fixture-layout.svg").write_text(svg, encoding="utf-8")


def write_docs(sheets):
    write_layout_svg()
    drawings = "".join(
        f'<details><summary>{sheet.number:02d} - {html.escape(sheet.title)}</summary><div class="drawing"><object data="output/{html.escape(f"{PROJECT}-{sheet.number:02d} {sheet.title}.svg".replace("/", "_"), quote=True)}" type="image/svg+xml" aria-label="{html.escape(sheet.title, quote=True)}"></object></div></details>'
        for sheet in sheets
    )
    p2p = p2p_rows()
    rows = "".join(f'<tr><td>{r["wire_id"]}</td><td>{html.escape(r["from_terminal"])}</td><td>{html.escape(r["to_terminal"])}</td><td>{html.escape(r["fixture_net"])}</td><td>{html.escape(r["function"])}</td></tr>' for r in p2p)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 P1.21 no-load fixture</title><style>:root{{--navy:#062b53;--blue:#12699b;--sky:#dff5ff;--gold:#f4b942;--paper:#f8fcff;--red:#8b1b1b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.12vw,19px)/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(2rem,6vw,5rem) 1rem;background:linear-gradient(135deg,var(--navy),#0c5889);color:white;border-bottom:8px solid var(--gold)}}header>div,main{{max-width:1280px;margin:auto}}h1{{font-size:clamp(2.5rem,6.5vw,5.5rem);line-height:1.02;max-width:16ch}}h2{{font-size:clamp(1.8rem,3.2vw,3rem)}}h3{{font-size:clamp(1.25rem,2vw,1.7rem)}}main{{padding:2rem clamp(.9rem,4vw,3rem) 5rem}}a{{color:#075d98;font-weight:800}}.warning,.stop{{padding:1rem 1.2rem;border:3px solid #815500;border-radius:14px;background:#fff0b5;color:#17243a;font-weight:900}}.stop{{border-color:var(--red);background:#ffe6e6}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:1rem;margin:2rem 0}}article,details,.panel{{padding:1rem;border:2px solid #94cce7;border-radius:16px;background:white}}article b{{display:block;font-size:clamp(2rem,4vw,3.6rem)}}object.layout{{display:block;width:100%;min-height:580px;background:white;border:2px solid var(--blue);border-radius:16px}}summary{{cursor:pointer;font-size:18px;font-weight:850}}.drawing{{height:680px;overflow:auto}}.drawing object{{width:100%;height:100%;min-width:960px}}.tablewrap{{overflow:auto;border:2px solid var(--blue);border-radius:16px}}table{{width:100%;min-width:1050px;border-collapse:collapse;background:white}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #c3deed;font-size:14px}}th{{background:var(--navy);color:white}}code{{font-size:16px}}@media(max-width:680px){{main{{padding-inline:.7rem}}object.layout{{min-height:430px}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>A real no-load fixture, with motion hardware removed.</h1><p>This native KiCad package binds 42 point-to-point fixture connections to the P1.21 DUT terminal schedule, exposes all 15 required signals, and carries the existing 18-test matrix without pretending the tests are authorized.</p></div></header><main><section class="grid"><article><b>5</b>native KiCad sheets</article><article><b>42</b>point-to-point rows</article><article><b>15</b>required signals</article><article><b>18</b>tests, all unexecuted</article></section><section class="stop"><h2>Still not permission to connect or energize</h2><p>AUTH-001 through AUTH-010 remain open. The fixture source, protection, instruments, received articles, numerical limits, physical fit, independent review and written E2 authorization are unresolved.</p></section><h2>Physical layout candidate</h2><object class="layout" data="fixture-layout.svg" type="image/svg+xml" aria-label="Control-only no-load fixture planning layout"></object><p><a href="{PROJECT}.kicad_pro">Open native KiCad project</a> / <a href="point-to-point-schedule.csv">point-to-point schedule</a> / <a href="signal-binding-register.csv">signal bindings</a> / <a href="test-binding-register.csv">test bindings</a> / <a href="open-holds.csv">open holds</a>.</p><h2>Editable schematic sheets</h2>{drawings}<h2>Point-to-point schedule</h2><div class="tablewrap"><table><thead><tr><th>Wire</th><th>From</th><th>To</th><th>Fixture net</th><th>Function</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-V0 P1.21 no-load fixture P0.1\n\n**{WARNING}**\n\nThis package provides the missing control-only fixture artifact for the P1.21 A1-gating evidence plan: a five-sheet native KiCad project, 42-row point-to-point schedule, physical planning layout, all 15 required signal bindings, all 18 unexecuted test bindings, explicit physical-absence checks and candidate BOM. It does not close AUTH-004 because independent checking and release acceptance remain open. AUTH-001 through AUTH-010 still prohibit connection and powered work.\n", encoding="utf-8")


def integrate_site():
    marker_a, marker_b = "<!-- HRV0-P121-FIXTURE-START -->", "<!-- HRV0-P121-FIXTURE-END -->"
    page = ROOT / "index.html"
    text = re.sub(re.escape(marker_a) + r"[\s\S]*?" + re.escape(marker_b), "", page.read_text(encoding="utf-8"))
    block = f'''{marker_a}<section id="hrv0-p121-no-load-fixture"><h2>HR-V0 control-only no-load fixture</h2><div class="grid"><article class="card pass"><h3>Native connected ECAD</h3><p>Five KiCad sheets define the isolated 24 V boundary, P1.21 eligibility chain, watchdog gate and fifteen-channel measurement fanout.</p></article><article class="card pass"><h3>42 point-to-point rows</h3><p>Every DUT endpoint is checked against the authoritative P1.21 connector schedule; deliberate test substitutions stay fixture-only.</p></article><article class="card hold"><h3>Not authorized</h3><p>All ten authorization prerequisites remain open. No connection, powered testing, motion or energization authority follows.</p></article></div><p><a href="test-fixtures/hr-v0-p121-no-load-fixture-p0.1/index.html">Open the interactive fixture guide</a> / <a href="test-fixtures/hr-v0-p121-no-load-fixture-p0.1/{PROJECT}.kicad_pro">native KiCad project</a> / <a href="test-fixtures/hr-v0-p121-no-load-fixture-p0.1/point-to-point-schedule.csv">point-to-point schedule</a>.</p></section>{marker_b}'''
    page.write_text(text.replace("</main>", block + "</main>"), encoding="utf-8")
    readme = ROOT / "README.md"
    text = re.sub(re.escape(marker_a) + r"[\s\S]*?" + re.escape(marker_b), "", readme.read_text(encoding="utf-8")).rstrip()
    text += f"\n\n{marker_a}\n## HR-V0 P1.21 control-only no-load fixture\n\nA connected five-sheet native KiCad fixture candidate now binds 42 point-to-point rows to the P1.21 terminal schedule, exposes all 15 required signals and carries the 18-test matrix with explicit actuator-power/contactors/motion-hardware absence. It is an engineering artifact, not authorization: independent review, received hardware, source/protection/instrument selections, numerical limits, physical inspection and written E2 authority remain open. See `test-fixtures/hr-v0-p121-no-load-fixture-p0.1/index.html`.\n{marker_b}\n"
    readme.write_text(text, encoding="utf-8")


def sync_and_manifest():
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "native_kicad_sheet_count": 5, "point_to_point_rows": len(p2p_rows()), "required_signal_count": 15,
        "test_count": 18, "authorization_gate_count": 10, "physical_absence_checks": 5,
        "erc_errors": 0, "erc_warnings": 0, "p121_accepted": False,
        "fixture_independently_checked": False, "fixture_physically_built": False, "fixture_unpowered_inspection_complete": False,
        "functional_safety_credit": False, "procurement_authority": False, "fabrication_authority": False,
        "assembly_authority": False, "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "fixture-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "fixture-source.py")
    shutil.copy2(ROOT / "tools/check_hr_v0_p121_no_load_fixture_p01.py", OUT / "fixture-checker.py")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in files])
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)


def main() -> int:
    if not KICAD.exists():
        raise RuntimeError("KiCad 10 CLI is required")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    model = load_model()
    sheets = build_sheets(model)
    write_ecad(model, sheets)
    write_registers()
    write_docs(sheets)
    integrate_site()
    sync_and_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
