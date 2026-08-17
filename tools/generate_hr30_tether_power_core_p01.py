#!/usr/bin/env python3
"""Generate the HR-30 tether power-core P0.1 candidate.

This package resolves the physical-location contradiction in the earlier
architecture: the two series contactors and mains equipment are located in an
external enclosure.  The robot carries only a touch-safe inlet, main
protection boundary, and five protected feeds to the five installed actuator
PDU boards.  Protection values and final conductors remain selections.
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

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "electrical" / "tether-power-core-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "tether-power-core-p0.1"
PROJECT = "hr30-tether-power-core-p0.1"
IDENTIFIER = "HR30-TETHER-POWER-CORE-P0.1"
DATE = "2026-08-15"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
OPEN = "SELECTION REQUIRED"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")

SOURCES = {
    "RSP": ("Mean Well", "RSP-500-12", "RSP-500-SPEC 2025-09-26", "https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF"),
    "SD": ("Mean Well", "SD-15A-24", "SD-15-SPEC 2024-11-22", "https://www.meanwell.com/Upload/PDF/SD-15/SD-15-SPEC.PDF"),
    "PNOZ": ("Pilz", "PNOZ s4 750104", "21396-EN-23, 2026-06-22", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf"),
    "TESYS": ("Schneider Electric", "TeSys Deca LC1D40ABD", "MKTED210011EN v17.1, 2026-07-10, A5/120-A5/123; product page accessed 2026-08-16", "https://shop.se.com/pro/us/en/product/iec-contactor-tesys-deca-nonreversing-40a-30hp-at-480vac-up-to-100ka-sccr-3-phase-3-no-24vdc-coil-open-style/"),
    "SBS": ("Anderson Power", "SBS75GBLK / 1339G2 / 1340G1", "1S6417, accessed 2026-08-15", "https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/SBS75G/1s6417-SBS-Assembly-Instructions.pdf"),
    "MIDI": ("Littelfuse", "04980923ZXT", "MIDI 498 datasheet 012826-A", "https://www.littelfuse.com/assetdocs/midi-498-datasheet?assetguid=5a3ddf39-419e-44c6-91bf-270e6a6d560b"),
    "HAMMOND": ("Hammond Manufacturing", "1418N4C6", "1418 N4 series, accessed 2026-08-15", "https://www.hammfg.com/electrical/products/industrial/1418n4.pdf"),
    "PHOENIX": ("Phoenix Contact", "MKDS 5/2-9.5 1714971", "live official page, accessed 2026-08-15", "https://www.phoenixcontact.com/en-us/products/pcb-terminal-block-mkds-5-2-95-1714971"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collapse_duplicate_hr30_blocks(text: str) -> str:
    """Keep the first complete copy of every generated HR30 integration block.

    Some older generators relocate their own block relative to another marker.
    When a historical file already contains a duplicate anchor, that can
    multiply downstream sections on repeated release-pipeline runs.  The power
    stage is the first new downstream stage and therefore acts as a harmless
    canonicalization checkpoint without changing the contents of any block.
    """
    starts = list(dict.fromkeys(re.findall(r"<!-- (HR30-[A-Z0-9-]+-START) -->", text)))
    for token in starts:
        start = f"<!-- {token} -->"
        end = f"<!-- {token[:-5]}END -->"
        pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
        seen = False
        def keep_first(match):
            nonlocal seen
            if seen:
                return ""
            seen = True
            return match.group(0)
        text = pattern.sub(keep_first, text)
    return text


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def load_model():
    source = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_power_model", source)
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
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 TETHER POWER CORE P0.1"
    model.PROJECT_SUBTITLE = "External redundant interruption; touch-safe tether; five protected robot PDU feeds."
    return model


def comp(model, ref, value, pins, description, position, width=90.0, source="", evidence="", status=OPEN):
    return model.Component(
        ref=ref, value=value,
        pins=[model.pn(ref, number, name, net, side) for number, name, net, side in pins],
        status=status, description=description, datasheet=source, evidence=evidence,
        position=position, width=width,
    )


def build_sheets(model):
    sheets = []
    s1 = model.Sheet(1, "01_external_source_panel.kicad_sch", "External mains boundary and DC sources", "Qualified mains enclosure boundary and exact DC source candidates.")
    s1.components = [
        comp(model, "XAC1", "FACILITY AC / PE / DISCONNECT / BRANCH PROTECTION", [("L", "LINE", "FACILITY_L", "right"), ("N", "NEUTRAL", "FACILITY_N", "right"), ("PE", "PROTECTIVE EARTH", "PANEL_PE", "right")], "Mains inlet, disconnect, branch protection, conductors, terminals and Boston jurisdictional installation remain qualified selections.", (75, 90), 92),
        comp(model, "PS1", "MEAN WELL RSP-500-12", [("AC/L", "AC LINE FUNCTION", "FACILITY_L", "left"), ("AC/N", "AC NEUTRAL FUNCTION", "FACILITY_N", "left"), ("FG", "FRAME GROUND FUNCTION", "PANEL_PE", "left"), ("+V", "12 V RAW OUTPUT", "RAW_12V_POS", "right"), ("-V", "DC RETURN", "RAW_0V", "right")], "230 x 127 x 40.5 mm, 1.3 kg, 12 V/41.7 A evaluation candidate. Final terminal-number mapping, source adjustment lock, inrush, protection, thermal rise and regeneration response remain open.", (220, 90), 100, SOURCES["RSP"][3], SOURCES["RSP"][2], "EXACT PRODUCT CANDIDATE - APPLICATION OPEN"),
        comp(model, "PS2", "MEAN WELL SD-15A-24", [("1", "DC INPUT +", "RAW_12V_POS", "left"), ("2", "DC INPUT -", "RAW_0V", "left"), ("3", "FG", "PANEL_PE", "left"), ("4", "DC OUTPUT -", "SAFE_0V", "right"), ("5", "DC OUTPUT +24 V", "SAFE_24V", "right")], "78 x 51 x 28 mm, 0.18 kg, 24 V/0.625 A candidate. Pin assignment is from SD-15-SPEC 2024-11-22; loading, protection, grounding and application validation remain open.", (350, 90), 94, SOURCES["SD"][3], SOURCES["SD"][2], "PHYSICAL TERMINALS VERIFIED - APPLICATION OPEN"),
    ]
    s1.notes = ["All mains wiring and enclosure work requires qualified electrical design/review. This drawing grants no installation or energization authority.", "RSP-500-12 is limited to 41.7 A while the provisional whole-body short peak is 60.58 A; deterministic current and torque limits are mandatory."]
    sheets.append(s1)

    s2 = model.Sheet(2, "02_estop_reset_safety_relay.kicad_sch", "Dual-channel E-stop, monitored manual reset and PNOZ s4", "Manufacturer terminal identifiers; application validation remains open.")
    s2.components = [
        comp(model, "S0", "IDEC XW DUAL-NC E-STOP FAMILY - ORDER CODE REQUIRED", [("NC1-A", "CHANNEL 1 FEED", "SAFE_24V", "left"), ("NC1-B", "CHANNEL 1 RETURN", "S12_CH1", "right"), ("NC2-A", "CHANNEL 2 FEED", "S21_TEST", "left"), ("NC2-B", "CHANNEL 2 RETURN", "S22_CH2", "right")], "Dual direct-opening contact family candidate. Exact complete order code, terminal numbering, enclosure and application remain selection work.", (80, 92), 96),
        comp(model, "S1", "IDEC HW1B-M1F11-G RESET CANDIDATE", [("NO-A", "RESET FEED", "S12_CH1", "left"), ("NO-B", "RESET / EDM LOOP", "RESET_EDM", "right")], "Momentary reset is eligibility only. It cannot command motion. Exact terminal IDs and monitored falling-edge behavior require physical verification.", (210, 92), 92),
        comp(model, "SR1", "PILZ PNOZ s4 750104", [("A1", "+24 V SUPPLY", "SAFE_24V", "left"), ("A2", "0 V SUPPLY", "SAFE_0V", "left"), ("S11", "TEST PULSE CH1", "SAFE_24V", "left"), ("S12", "INPUT CH1", "S12_CH1", "left"), ("S21", "TEST PULSE CH2", "S21_TEST", "left"), ("S22", "INPUT CH2", "S22_CH2", "left"), ("S34", "MONITORED START / FEEDBACK", "RESET_EDM", "left"), ("13", "SAFETY CONTACT 1 IN", "SAFE_24V", "left"), ("14", "SAFETY CONTACT 1 OUT", "K1_COIL_POS", "right"), ("23", "SAFETY CONTACT 2 IN", "SAFE_24V", "left"), ("24", "SAFETY CONTACT 2 OUT", "K2_COIL_POS", "right"), ("33", "SAFETY CONTACT 3 IN", "SAFE_24V", "left"), ("34", "SAFETY PERMIT STATUS", "HARDWIRED_PERMIT", "right"), ("41", "AUXILIARY NC IN", "SAFE_24V", "left"), ("42", "AUXILIARY NC OUT", "PNOZ_AUX_STATUS", "right"), ("Y32", "SEMICONDUCTOR STATUS", "PNOZ_Y32_STATUS", "right")], "Manual 21396-EN-23 identifies these terminals and supports dual-channel E-stop, monitored start and feedback-loop application examples. Exact circuit mode, PLr/SIL allocation, contact protection, reset proof and validation remain open.", (340, 160), 116, SOURCES["PNOZ"][3], SOURCES["PNOZ"][2], "TERMINALS VERIFIED - NO WHOLE-MACHINE SAFETY APPROVAL"),
    ]
    s2.notes = ["The PNOZ manual says 41-42 and Y32 must not be used for safety circuits. They are status-only here.", "E-stop release and reset restore eligibility only. The motion controller still requires a fresh bounded action request before motion."]
    sheets.append(s2)

    s3 = model.Sheet(3, "03_redundant_dc_interruption.kicad_sch", "Two series LC1D40ABD contactors and mirror-feedback loop", "External-panel three-pole-series DC interruption candidate; no achieved safety-performance claim.")
    s3.components = [
        comp(model, "K1", "SCHNEIDER TESYS DECA LC1D40ABD", [("1/L1", "MAIN POLE 1 INPUT", "RAW_12V_POS", "left"), ("2/T1", "MAIN POLE 1 OUTPUT", "K1_POLE2_IN", "right"), ("3/L2", "MAIN POLE 2 INPUT", "K1_POLE2_IN", "left"), ("4/T2", "MAIN POLE 2 OUTPUT", "K1_POLE3_IN", "right"), ("5/L3", "MAIN POLE 3 INPUT", "K1_POLE3_IN", "left"), ("6/T3", "MAIN POLE 3 OUTPUT", "K1_OUT", "right"), ("A1", "24 VDC COIL POSITIVE", "K1_COIL_POS", "left"), ("A2", "COIL RETURN", "SAFE_0V", "left"), ("21", "MIRROR NC COMMON", "RESET_EDM", "left"), ("22", "MIRROR NC RETURN", "EDM_K1_OUT", "right"), ("13", "BUILT-IN NO AUX SPARE", "K1_NO_AUX_13_UNCONNECTED", "left"), ("14", "BUILT-IN NO AUX SPARE", "K1_NO_AUX_14_UNCONNECTED", "right")], "Three main poles are connected in series. Schneider catalog MKTED210011EN v17.1 A5/120-A5/123 lists LC1D40A at 50 A for 24 VDC with one, two or three series poles under its DC-1 and DC-2...DC-5 table conditions. The built-in 21-22 NC auxiliary is mirror certified. HR-30 fault current, actual L/R, durability, regeneration, protection, conductor termination, received-device identity and opening-time validation remain open.", (130, 120), 112, SOURCES["TESYS"][3], SOURCES["TESYS"][2], "EXACT ORDER-CODE / MIRROR CONTACT VERIFIED - APPLICATION VALIDATION OPEN"),
        comp(model, "K2", "SCHNEIDER TESYS DECA LC1D40ABD", [("1/L1", "MAIN POLE 1 INPUT", "K1_OUT", "left"), ("2/T1", "MAIN POLE 1 OUTPUT", "K2_POLE2_IN", "right"), ("3/L2", "MAIN POLE 2 INPUT", "K2_POLE2_IN", "left"), ("4/T2", "MAIN POLE 2 OUTPUT", "K2_POLE3_IN", "right"), ("5/L3", "MAIN POLE 3 INPUT", "K2_POLE3_IN", "left"), ("6/T3", "MAIN POLE 3 OUTPUT", "TETHER_POS_SWITCHED", "right"), ("A1", "24 VDC COIL POSITIVE", "K2_COIL_POS", "left"), ("A2", "COIL RETURN", "SAFE_0V", "left"), ("21", "MIRROR NC COMMON", "EDM_K1_OUT", "left"), ("22", "MIRROR NC RETURN", "RESET_EDM", "right"), ("13", "BUILT-IN NO AUX SPARE", "K2_NO_AUX_13_UNCONNECTED", "left"), ("14", "BUILT-IN NO AUX SPARE", "K2_NO_AUX_14_UNCONNECTED", "right")], "Second independent contactor in series, also using all three main poles in series. K1/K2 21-22 mirror contacts form the monitored reset feedback chain. Common-cause analysis, fault-current coordination, coil suppression effects, durability, stopping time and qualified whole-machine validation remain open.", (325, 120), 112, SOURCES["TESYS"][3], SOURCES["TESYS"][2], "EXACT ORDER-CODE / MIRROR CONTACT VERIFIED - APPLICATION VALIDATION OPEN"),
        comp(model, "XPERMIT", "HARDWIRED PERMIT STATUS TO MOTION CONTROLLER", [("IN", "PNOZ SAFETY CONTACT", "HARDWIRED_PERMIT", "left"), ("OUT", "PERMIT INPUT", "MOTION_PERMIT_INPUT", "right")], "Permit restoration never issues motion. Interface voltage, isolation, test pulses and fault response remain selection and validation work.", (225, 220), 105),
    ]
    s3.notes = ["Both high-current contactors are in the external panel, not on the robot. Each contactor's three main poles are wired in series; K1 and K2 remain independent series interruption elements.", "Schneider identifies built-in 21-22 as an IEC 60947-4-1 mirror contact. This supports the proposed EDM architecture only; no achieved Category, PL, SIL or whole-machine safety claim is made."]
    sheets.append(s3)

    s4 = model.Sheet(4, "04_touch_safe_tether.kicad_sch", "SBS75G touch-safe three-contact tether", "Project-assigned cavities, pre-mate frame reference and flexible tether boundary.")
    s4.components = [
        comp(model, "XT1A", "PANEL SBS75G - SBS75GBLK", [("P1", "PROJECT-ASSIGNED SWITCHED +12 V", "TETHER_POS_SWITCHED", "left"), ("G", "PRE-MATE FRAME / SHIELD REFERENCE", "PANEL_PE", "left"), ("P2", "PROJECT-ASSIGNED DC RETURN", "RAW_0V", "left")], "Black genderless three-position housing. P1/P2 project polarity assignment must be permanently keyed, labeled and continuity-tested; ground contact uses 1340G1. Cable, breakaway/retention and shielding remain open.", (120, 120), 104, SOURCES["SBS"][3], SOURCES["SBS"][2], "HOUSING/6 AWG CONTACT FAMILY VERIFIED - HARNESS OPEN"),
        comp(model, "XT1B", "ROBOT SBS75G - SBS75GBLK", [("P1", "PROJECT-ASSIGNED CONTROLLED +12 V", "ROBOT_MAIN_POS", "right"), ("G", "PRE-MATE ROBOT FRAME REFERENCE", "ROBOT_FRAME_BOUNDARY", "right"), ("P2", "PROJECT-ASSIGNED CONTROLLED RETURN", "ROBOT_MAIN_RET", "right")], "Mating robot-side housing with the same controlled project polarity. Finger-safe state, strain relief, frame bond, flex life and tether trip/breakaway behavior require physical validation.", (320, 120), 104, SOURCES["SBS"][3], SOURCES["SBS"][2], "PROJECT CONTACT ASSIGNMENT - PHYSICAL VERIFICATION REQUIRED"),
    ]
    s4.notes = ["Anderson rates the family with specified contacts and conductor sizes; this does not establish HR-30 ampacity under walking flex, bundling or ambient conditions.", "No connector is treated as a routine load-break E-stop. The contactors must open before planned disconnection."]
    sheets.append(s4)

    s5 = model.Sheet(5, "05_robot_five_branch_distribution.kicad_sch", "Robot inlet, main boundary and five protected PDU feeds", "One physical branch holder per installed PDU board; all fuse values open.")
    s5.components = [
        comp(model, "FM0", "LITTELFUSE 04980923ZXT MAIN HOLDER - FUSE VALUE REQUIRED", [("IN", "ROBOT INLET POSITIVE", "ROBOT_MAIN_POS", "left"), ("OUT", "MAIN DISTRIBUTION BUS", "ROBOT_FUSED_POS", "right")], "58 V MIDI holder with cover and M6 mounting tabs. Fuse value, fuse order code, interrupt rating, coordination, terminal hardware, conductor and torque are not released.", (85, 70), 115, SOURCES["MIDI"][3], SOURCES["MIDI"][2], "HOLDER SELECTED - FUSE VALUE SELECTION REQUIRED"),
        comp(model, "RB0", "ROBOT RETURN / FRAME BOUNDARY", [("RET-IN", "TETHER RETURN", "ROBOT_MAIN_RET", "left"), ("RET-BUS", "CONTROLLED RETURN BUS", "PDU_COMMON_RET", "right"), ("FRAME-IN", "TETHER PRE-MATE FRAME", "ROBOT_FRAME_BOUNDARY", "left"), ("FRAME-STAR", "PROPOSED SINGLE 0 V / FRAME STAR POINT", "STAR_POINT_0V_FRAME", "right")], "Return bus, frame bond and proposed single star point are not finalized. Bond conductor, terminal, location, fault current and jurisdictional treatment require qualified selection.", (85, 190), 115),
    ]
    boards = [("LLEG", 60), ("RLEG", 100), ("ARMS", 140), ("DISTAL", 180), ("CORE", 220)]
    for index, (name, y) in enumerate(boards, 1):
        s5.components.extend([
            comp(model, f"FB{index}", f"04980923ZXT {name} BRANCH HOLDER - FUSE VALUE REQUIRED", [("IN", "COMMON DISTRIBUTION INPUT", "ROBOT_FUSED_POS", "left"), ("OUT", f"{name} PROTECTED FEED", f"PDU_{name}_POS", "right")], "Fuse holder is physically selected; exact MIDI fuse, value, interrupt rating, discrimination, conductor, lug, terminal hardware and torque remain selection work.", (230, y), 108, SOURCES["MIDI"][3], SOURCES["MIDI"][2], "HOLDER SELECTED - NO FUSE VALUE RELEASED"),
            comp(model, f"J{name}", f"PDU-{name} INPUT - PHOENIX 1714971", [("1", "PDU 0 V", "PDU_COMMON_RET", "left"), ("2", "PDU +12 V INPUT", f"PDU_{name}_POS", "left")], "Board terminal is nominally 32 A / 4 mm2 per the manufacturer page. Field mating wire, ferrule, retention, derating and measured temperature remain open.", (370, y), 98, SOURCES["PHOENIX"][3], SOURCES["PHOENIX"][2], "BOARD TERMINAL IDENTIFIED - FIELD ASSEMBLY OPEN"),
        ])
    s5.notes = ["Five holders correspond exactly to PDU-LLEG, PDU-RLEG, PDU-ARMS, PDU-DISTAL and PDU-CORE.", "No fuse value is shown because available fault current, cable lengths, temperatures, bundling, inrush, regeneration and coordination are not closed."]
    sheets.append(s5)

    s6 = model.Sheet(6, "06_telemetry_interlocks_commissioning.kicad_sch", "Status, telemetry and fail-closed commissioning boundary", "No reset-to-motion path and no diagnostic safety credit.")
    s6.components = [
        comp(model, "MCU1", "DETERMINISTIC MOTION CONTROLLER BOUNDARY", [("PERMIT", "HARDWIRED PERMIT INPUT", "MOTION_PERMIT_INPUT", "left"), ("CMD", "FRESH BOUNDED MOTION REQUEST", "FRESH_MOTION_REQUEST", "left"), ("ENABLE", "PDU DISABLE COMMANDS", "PDU_ENABLE_BOUNDARY", "right")], "Motion requires both hardwired permit and a fresh bounded local command. A permit/reset transition alone must leave all branch enables disabled.", (115, 120), 105),
        comp(model, "MON1", "NON-SAFETY DIAGNOSTIC MONITOR", [("SR", "PNOZ AUX STATUS", "PNOZ_AUX_STATUS", "left"), ("Y32", "PNOZ SEMICONDUCTOR STATUS", "PNOZ_Y32_STATUS", "left"), ("BR", "PDU POWER-GOOD AGGREGATE", "PDU_STATUS_BOUNDARY", "left"), ("LOG", "FAULT LOG / TELEMETRY", "DIAGNOSTIC_LOG", "right")], "Auxiliary diagnostics are not part of the safety function and cannot enable motion or bypass E-stop, feedback loop or fresh-command logic.", (315, 120), 110),
    ]
    s6.notes = ["Required commissioning sequence: unpowered continuity/PE inspection, isolated 24 V controls, contactor feedback fault injection, then separately authorized current-limited DC testing.", "This package does not authorize any of those steps; signed procedures and qualified review remain required."]
    sheets.append(s6)
    return sheets


def write_ecad(sheets, model):
    OUT.mkdir(parents=True, exist_ok=True)
    root_uuid = model.uid("hr30-tether-root")
    counts = Counter(pin.net for sheet in sheets for component in sheet.components for pin in component.pins)
    wires = model.build_wire_numbers(sheets, counts)
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wires), encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps({"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}, indent=2) + "\n", encoding="utf-8")
    components = [c for s in sheets for c in s.components]
    symbols = [model.lib_symbol(c).replace(f'(symbol "PBV3:{c.ref}"', f'(symbol "{c.ref}"', 1) for c in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 tether power symbols"))\n)\n', encoding="utf-8")
    model.write_tables(sheets, counts, wires)
    validation, output = OUT / "validation", OUT / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    commands = [
        [str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
            raise SystemExit(result.returncode)
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def rounded_box(x, y, z, p=(0, 0, 0), r=2):
    return cq.Workplane("XY").box(x, y, z).edges("|Z").fillet(min(r, x / 4, y / 4)).translate(p).val()


def write_cad():
    # External panel: 508 x 406 x 152 mm Hammond envelope, 432 x 330 mm back panel.
    shell_outer = cq.Workplane("XY").box(508, 152, 406).translate((0, 0, 203))
    shell_inner = cq.Workplane("XY").box(500, 144, 398).translate((0, -2, 203))
    shell = shell_outer.cut(shell_inner).val()
    backplate = rounded_box(432, 4, 330, (0, -68, 203), 1)
    rsp = rounded_box(230, 42, 127, (-90, -42, 235), 3)
    din = rounded_box(250, 10, 35, (105, -60, 320), 1)
    pnoz = rounded_box(22.5, 120, 98, (48, -2, 280), 2)
    sd15 = rounded_box(78, 52, 28, (125, -42, 290), 2)
    # Current LC1D40ABD product envelope: 55 mm wide, about 122 mm high and
    # 120 mm deep.  These are clearance solids, not manufacturer CAD.
    k1 = rounded_box(55, 120, 122, (75, -2, 150), 3)
    k2 = rounded_box(55, 120, 122, (155, -2, 150), 3)
    estop = cq.Workplane("XY").cylinder(45, 22).translate((-185, 80, 300)).val()
    reset = cq.Workplane("XY").cylinder(30, 15).translate((-185, 80, 220)).val()
    tether = rounded_box(70, 28, 48, (190, 68, 72), 5)
    panel_parts = [(shell, "ENCLOSURE_1418N4C6", (0.65, 0.72, 0.78, 0.35)), (backplate, "BACK_PANEL_432x330", (0.75, 0.78, 0.80, 1)), (rsp, "PS1_RSP-500-12", (0.18, 0.45, 0.78, 1)), (din, "DIN_RAIL", (0.72, 0.72, 0.72, 1)), (pnoz, "SR1_PNOZ_s4_750104", (0.95, 0.75, 0.12, 1)), (sd15, "PS2_SD-15A-24", (0.22, 0.65, 0.85, 1)), (k1, "K1_LC1D40ABD", (0.74, 0.15, 0.13, 1)), (k2, "K2_LC1D40ABD", (0.74, 0.15, 0.13, 1)), (estop, "S0_ESTOP_FAMILY", (0.86, 0.05, 0.05, 1)), (reset, "S1_RESET", (0.95, 0.76, 0.12, 1)), (tether, "XT1A_SBS75G", (0.12, 0.18, 0.24, 1))]
    assy = cq.Assembly(name="HR30_EXTERNAL_TETHER_PANEL_P01_NOT_RELEASED")
    for shape, name, color in panel_parts:
        assy.add(shape, name=name, color=cq.Color(*color))
    cq.exporters.export(cq.Compound.makeCompound([p[0] for p in panel_parts]), str(OUT / "HR30_external_tether_panel_candidate.step"))
    assy.save(str(OUT / "HR30_external_tether_panel_candidate.glb"))

    # Robot passive distribution assembly: inlet at rear, six covered holders in two rows.
    base = rounded_box(146, 28, 38, (0, 0, 0), 3)
    inlet = rounded_box(52, 38, 30, (-46, 2, 0), 4)
    holders = []
    for index in range(6):
        x = -40 + (index % 3) * 40
        z = -11 + (index // 3) * 22
        holders.append(rounded_box(34, 30, 15, (x, 0, z), 3))
    splitter_parts = [(base, "INSULATED_DISTRIBUTION_ENCLOSURE", (0.10, 0.22, 0.34, 1)), (inlet, "XT1B_SBS75G", (0.08, 0.10, 0.14, 1))] + [(shape, "FM0_MAIN" if i == 0 else f"FB{i}_{['LLEG','RLEG','ARMS','DISTAL','CORE'][i-1]}", (0.88, 0.56, 0.08, 1)) for i, shape in enumerate(holders)]
    assy2 = cq.Assembly(name="HR30_ROBOT_FIVE_BRANCH_DISTRIBUTOR_P01_NOT_RELEASED")
    for shape, name, color in splitter_parts:
        assy2.add(shape, name=name, color=cq.Color(*color))
    cq.exporters.export(cq.Compound.makeCompound([p[0] for p in splitter_parts]), str(OUT / "HR30_robot_five_branch_distributor_candidate.step"))
    assy2.save(str(OUT / "HR30_robot_five_branch_distributor_candidate.glb"))


def write_docs(sheets):
    source_rows = []
    for key, (maker, part, rev, url) in SOURCES.items():
        source_rows.append({"source_id": key, "manufacturer": maker, "candidate": part, "document_revision_or_date": rev, "accessed": DATE, "official_url": url, "verified_scope": {
            "RSP": "12 V, 41.7 A, 500.4 W; 230 x 127 x 40.5 mm; 1.3 kg",
            "SD": "SD-15A-24; input terminals 1/2, FG 3, output -V/+V 4/5; 78 x 51 x 28 mm; 0.18 kg",
            "PNOZ": "Product 750104; A1/A2, S11/S12/S21/S22/S34, 13-14/23-24/33-34, 41-42, Y32; 22.5 x 98 x 120 mm",
            "TESYS": "LC1D40ABD; 24 VDC coil; 3 NO main poles; built-in 13-14 NO and mirror-certified 21-22 NC; A1 positive/A2 negative; 50 A at 24 VDC for 1-3 series poles under catalog DC table conditions",
            "SBS": "SBS75GBLK three-position touch-safe housing; 1339G2 and 1340G1 6 AWG contact families",
            "MIDI": "04980923ZXT holder, 58 V, covered, M6 mounting tabs; fuse sold separately",
            "HAMMOND": "1418N4C6 Type 4 enclosure candidate, 508 x 406 x 152 mm; 432 x 330 mm panel envelope",
            "PHOENIX": "1714971 two-position 9.52 mm PCB terminal; nominal 32 A, 4 mm2",
        }[key], "selection_boundary": "APPLICATION / INSTALLATION / VALIDATION OPEN", "warning": WARNING})
    write_csv(OUT / "primary-source-register.csv", source_rows)
    branch_currents = {"PDU-LLEG": 24.20, "PDU-RLEG": 24.20, "PDU-ARMS": 18.00, "PDU-DISTAL": 5.28, "PDU-CORE": 4.40}
    write_csv(OUT / "five-pdu-feed-register.csv", [{"branch_id": f"FB{i}", "board_instance": board, "positive_net": f"PDU_{board[4:]}_POS", "return_net": "PDU_COMMON_RET", "holder_order_code": "04980923ZXT", "fuse_order_code": OPEN, "fuse_value_a": OPEN, "published_actuator_stall_endpoint_sum_a": f"{amps:.2f}", "board_input_terminal": "Phoenix Contact 1714971 pin 2 positive / pin 1 return", "terminal_nominal_current_a": "32", "final_conductor": OPEN, "required_closure": "fault current; cable length; ambient; bundling; inrush; duty; regeneration; connector/lug limits; coordination; jurisdiction", "authority": AUTHORITY} for i, (board, amps) in enumerate(branch_currents.items(), 1)])
    write_csv(OUT / "connector-contact-map.csv", [
        {"connector": "XT1A/XT1B", "housing": "SBS75GBLK", "project_cavity": "P1", "function": "controlled +12 V", "contact_candidate": "1339G2 for 6 AWG", "manufacturer_assignment": "power position", "project_polarity_marking": "REQUIRED", "physical_validation": "NOT EXECUTED"},
        {"connector": "XT1A/XT1B", "housing": "SBS75GBLK", "project_cavity": "G center", "function": "pre-mate frame/shield reference", "contact_candidate": "1340G1 for 6 AWG", "manufacturer_assignment": "pre-mate ground position", "project_polarity_marking": "REQUIRED", "physical_validation": "NOT EXECUTED"},
        {"connector": "XT1A/XT1B", "housing": "SBS75GBLK", "project_cavity": "P2", "function": "controlled DC return", "contact_candidate": "1339G2 for 6 AWG", "manufacturer_assignment": "power position", "project_polarity_marking": "REQUIRED", "physical_validation": "NOT EXECUTED"},
    ])
    holds = [
        ("H01", "facility mains disconnect, branch protection, cable and Boston jurisdictional installation"),
        ("H02", "RSP-500-12 adjustment lock, inrush, thermal rise, source current limiting and regeneration response"),
        ("H03", "complete E-stop order code, reset terminals, PNOZ mode setting, contact protection and whole-machine safety validation"),
        ("H04", "LC1D40ABD received-device/terminal inspection, HR-30 fault current and L/R, DC electrical durability, series-pole jumpers, protection, opening time, regeneration, life and common-cause analysis"),
        ("H05", "all six MIDI fuse order codes and values, interrupt ratings and coordination"),
        ("H06", "all tether/branch conductors, lugs, ferrules, torque, temperature, bundling, flex and strain relief"),
        ("H07", "single proposed 0 V/frame star point, PE/frame bonding, shield terminations and enclosure bond"),
        ("H08", "power-loss, regeneration, stopping time, contactor opening time and branch-disable sequencing"),
        ("H09", "external-panel thermal analysis, spacing, wireways, touch protection, labels and qualified drawing review"),
        ("H10", "robot distributor fit, access, cover retention, crash/fall loads, ingress and thermal proof"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": i, "unresolved_selection_or_evidence": text, "state": "OPEN", "authority": AUTHORITY} for i, text in holds])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 760" role="img" aria-labelledby="t d"><title id="t">HR-30 physical tether power core</title><desc id="d">External enclosure with power supply, safety relay and two series contactors feeds a touch-safe tether and six fuse holders on the robot: one main and five PDU branches.</desc><style>text{{font-family:system-ui,sans-serif;fill:#082f58}}.box{{fill:white;stroke:#0b5790;stroke-width:3}}.ext{{fill:#d8f1ff}}.robot{{fill:#fff4bf}}.line{{stroke:#0b5790;stroke-width:6;fill:none;marker-end:url(#a)}}.h{{font-size:25px;font-weight:800}}.b{{font-size:18px}}.s{{font-size:14px}}</style><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L9 3L0 6z" fill="#0b5790"/></marker></defs><rect width="1500" height="760" fill="#f7fcff"/><text x="45" y="48" class="h">{WARNING}</text><rect class="box ext" x="45" y="90" width="610" height="590" rx="24"/><text x="75" y="130" class="h">External 1418N4C6 panel candidate</text><rect class="box" x="80" y="175" width="220" height="105" rx="14"/><text x="100" y="212" class="h">RSP-500-12</text><text x="100" y="245" class="b">12 V · 41.7 A candidate</text><rect class="box" x="355" y="175" width="250" height="105" rx="14"/><text x="375" y="212" class="h">PNOZ s4 750104</text><text x="375" y="245" class="b">Dual channel + reset + EDM</text><rect class="box" x="95" y="360" width="190" height="100" rx="14"/><text x="120" y="400" class="h">K1 GV121CAC</text><rect class="box" x="365" y="360" width="190" height="100" rx="14"/><text x="390" y="400" class="h">K2 GV121CAC</text><path class="line" d="M190 280V350"/><path class="line" d="M285 410H355"/><rect class="box" x="170" y="530" width="350" height="90" rx="14"/><text x="200" y="568" class="h">SBS75G tether</text><text x="200" y="598" class="b">+12 V · return · pre-mate frame</text><path class="line" d="M460 460V520"/><rect class="box robot" x="780" y="90" width="675" height="590" rx="24"/><text x="810" y="130" class="h">Robot passive distribution assembly</text><rect class="box" x="825" y="180" width="210" height="95" rx="14"/><text x="850" y="218" class="h">FM0 main holder</text><text x="850" y="248" class="b">Fuse value: required</text><path class="line" d="M520 575H745V225H815"/><path class="line" d="M1035 225H1100"/><rect class="box" x="1110" y="170" width="285" height="400" rx="14"/><text x="1140" y="210" class="h">Five branch holders</text>{''.join(f'<text x="1140" y="{255+i*55}" class="b">FB{i+1} → PDU-{name}</text>' for i,name in enumerate(['LLEG','RLEG','ARMS','DISTAL','CORE']))}<text x="835" y="625" class="b">No fuse value or conductor is released. No contactor is on the robot.</text></svg>'''
    svg = (svg
        .replace("K1 GV121CAC", "K1 LC1D40ABD")
        .replace("K2 GV121CAC", "K2 LC1D40ABD")
        .replace("+12 V · return · pre-mate frame", "+12 V / return / pre-mate frame"))
    (OUT / "system-architecture.svg").write_text(svg, encoding="utf-8")
    panels = []
    for sheet in sheets:
        exported = sorted((OUT / "output").glob(f"{PROJECT}-{sheet.number:02d} *.svg"))
        if len(exported) != 1:
            raise RuntimeError(f"expected one exported SVG for sheet {sheet.number:02d}, found {len(exported)}")
        panels.append(f'<details><summary>{sheet.number:02d} · {html.escape(sheet.title)}</summary><div class="drawing"><object data="output/{html.escape(exported[0].name)}" type="image/svg+xml" aria-label="{html.escape(sheet.title)}"></object></div></details>')
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 tether power core P0.1</title><script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script><style>:root{{--navy:#082f58;--blue:#0b5790;--sky:#cfeeff;--gold:#f2b928;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif;background:var(--paper)}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(2.4rem,6vw,5rem);line-height:1.02;max-width:17ch}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #a66f00;background:#fff2bd;border-radius:14px;padding:1rem;font-weight:850}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1rem;margin:2rem 0}}article,details{{background:white;border:2px solid var(--blue);border-radius:16px;overflow:hidden}}article{{padding:1rem}}article b{{display:block;font-size:clamp(2rem,4vw,3.6rem)}}model-viewer{{width:100%;height:520px;background:white;border:2px solid #83bddb}}summary{{padding:1rem;font-size:18px;font-weight:850;cursor:pointer;background:#e2f5ff}}.system-map{{display:block;width:100%;max-width:100%;height:570px}}.drawing{{width:100%;max-width:100%;height:650px;overflow:auto;contain:inline-size}}.drawing object{{display:block;width:900px;max-width:none;height:100%}}a{{color:#075d98;font-weight:800}}small{{font-size:14px}}@media(max-width:650px){{main{{padding:1.2rem .8rem 4rem}}model-viewer{{height:420px}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>The contactors are outside the robot.</h1><p>A physical external panel candidate now feeds one touch-safe tether and exactly five protected onboard PDU inputs.</p></div></header><main><section class="grid"><article><b>7</b>native KiCad files: root plus six sheets</article><article><b>ERC 0 / 0</b>connectivity and annotation only</article><article><b>2</b>LC1D40ABD candidates</article><article><b>5</b>axis-bound PDU feeds</article></section><div class="hold"><h2>The EDM hardware mismatch is corrected</h2><p>K1 and K2 each use explicit 21-22 mirror-certified NC auxiliary contacts. Their three main poles are wired in series. This is still an unvalidated candidate circuit: no achieved Category, PL, SIL or permission to energize is claimed.</p></div><div class="hold"><h2>Fuse values are intentionally absent</h2><p>Fault current, cable length, ambient temperature, bundling, inrush, duty cycle, regeneration, connector limits, coordination and jurisdiction are not yet closed. No fuse value or conductor is released.</p></div><h2>Physical system map</h2><object class="system-map" data="system-architecture.svg" type="image/svg+xml" aria-label="Physical tether power architecture"></object><h2>External enclosure candidate</h2><model-viewer src="HR30_external_tether_panel_candidate.glb" camera-controls shadow-intensity="0.9" alt="Interactive external HR-30 tether power panel candidate"></model-viewer><p><a href="HR30_external_tether_panel_candidate.step">External panel STEP</a> · <a href="HR30_robot_five_branch_distributor_candidate.step">Robot distributor STEP</a> · <a href="{PROJECT}.kicad_pro">KiCad project</a> · <a href="five-pdu-feed-register.csv">five-feed register</a> · <a href="open-holds.csv">open holds</a></p><h2>Native schematic sheets</h2>{''.join(panels)}</main></body></html>''', encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 tether power core P0.1\n\n**{WARNING}**\n\nThis package implements the tether-first arrangement with RSP-500-12, PNOZ s4 750104 and two independent series Schneider LC1D40ABD contactors in the external Hammond 1418N4C6 panel candidate. Each contactor uses all three main poles in series, and its built-in mirror-certified 21-22 NC auxiliary is wired into the monitored reset/EDM chain. The robot receives controlled DC through an SBS75G boundary and carries one main plus five branch fuse holders feeding the five installed actuator PDU boards. The contactor candidate and terminal functions are now explicit; fuse values, final conductors, fault current, L/R, durability, grounding, thermal behavior, regeneration, stopping behavior, physical validation and every work authority remain open.\n", encoding="utf-8")


def integrate_status():
    status_path = WB / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "tether_power_core_package_present": True,
        "tether_power_core_native_sheet_count": 7,
        "tether_power_core_erc_errors": 0,
        "tether_power_core_erc_warnings": 0,
        "external_contactor_count": 2,
        "external_contactor_candidate": "Schneider LC1D40ABD",
        "contactor_mirror_nc_terminals": "21-22",
        "contactor_main_poles_in_series_per_device": 3,
        "contactor_application_validated": False,
        "on_robot_contactor_count": 0,
        "robot_pdu_feed_count": 5,
        "robot_main_fuse_value_selected": False,
        "robot_branch_fuse_values_selected": False,
        "tether_power_core_energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    page = WB / "index.html"
    text = collapse_duplicate_hr30_blocks(page.read_text(encoding="utf-8"))
    start, end = "<!-- HR30-TETHER-POWER-START -->", "<!-- HR30-TETHER-POWER-END -->"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", text)
    section = f'''{start}<section id="tether-power-core"><h2>The tether power path now has physical hardware and locations</h2><div class="grid"><article class="card pass"><h3>External interruption</h3><p>RSP-500-12, PNOZ s4 and two GV121CAC contactors are located in a 1418N4C6 external-panel candidate—not inside the robot.</p></article><article class="card pass"><h3>Five PDU feeds</h3><p>One covered branch holder is allocated to each installed PDU board through a touch-safe SBS75G tether boundary.</p></article><article class="card hold"><h3>No fuse values released</h3><p>Fault current, wire, connector temperature, coordination and regeneration evidence remain open.</p></article></div><div class="viewer"><object data="electrical/tether-power-core-p0.1/system-architecture.svg" type="image/svg+xml" aria-label="HR-30 tether power core architecture"></object><p><a href="electrical/tether-power-core-p0.1/index.html">Open the interactive power-core guide</a> · <a href="electrical/tether-power-core-p0.1/{PROJECT}.kicad_pro">native KiCad</a> · <a href="electrical/tether-power-core-p0.1/HR30_external_tether_panel_candidate.step">panel STEP</a>.</p></div></section>{end}'''
    section = section.replace("two GV121CAC contactors", "two LC1D40ABD contactors")
    section = section.replace('<article class="card pass"><h3>Five PDU feeds</h3>', '<article class="card pass"><h3>Mirror-contact EDM</h3><p>Each contactor\'s 21-22 mirror-certified NC auxiliary is in the monitored reset chain. This corrects the former candidate mismatch but does not establish an achieved safety level.</p></article><article class="card pass"><h3>Five PDU feeds</h3>')
    page.write_text(text.replace("</main>", section + "</main>"), encoding="utf-8")
    readme = WB / "README.md"
    readme_text = collapse_duplicate_hr30_blocks(readme.read_text(encoding="utf-8"))
    md_start, md_end = "<!-- HR30-TETHER-POWER-START -->", "<!-- HR30-TETHER-POWER-END -->"
    readme_text = re.sub(re.escape(md_start) + r"[\s\S]*?" + re.escape(md_end), "", readme_text).rstrip()
    readme_text += f"\n\n{md_start}\n## Physical tether power core\n\nThe P0.1 robot no longer contains an abstract high-current interruption module. RSP-500-12, PNOZ s4 750104 and both GV121CAC series contactors are located in an external 1418N4C6 panel candidate. The robot carries an SBS75G inlet and one main plus five covered MIDI-holder positions mapped exactly to PDU-LLEG, PDU-RLEG, PDU-ARMS, PDU-DISTAL and PDU-CORE. The seven-sheet native KiCad package validates at ERC 0/0 for connectivity and annotation only. All six fuse values, final conductors, grounding, thermal behavior, stopping behavior and every work authority remain open. See `electrical/tether-power-core-p0.1/index.html`.\n{md_end}\n"
    readme_text = readme_text.replace("both GV121CAC series contactors", "two independent LC1D40ABD series contactors")
    readme_text = readme_text.replace("The robot carries an SBS75G inlet", "Each contactor's three main poles are wired in series and the built-in 21-22 mirror-certified NC auxiliary participates in EDM. This corrects a candidate/interface mismatch but does not establish a Category, PL or SIL. The robot carries an SBS75G inlet")
    readme.write_text(readme_text, encoding="utf-8")


def main() -> int:
    if not KICAD.exists():
        raise RuntimeError("KiCad 10 CLI missing")
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    model = load_model(); sheets = build_sheets(model)
    write_ecad(sheets, model); write_cad(); write_docs(sheets); integrate_status()
    shutil.copy2(Path(__file__), OUT / "tether-power-core-source.py")
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "native_sheet_count": 7,
        "child_sheet_count": 6, "erc_errors": 0, "erc_warnings": 0,
        "external_contactor_count": 2, "on_robot_contactor_count": 0,
        "external_contactor_candidate": "Schneider LC1D40ABD",
        "contactor_mirror_nc_terminals": "21-22",
        "contactor_main_poles_in_series_per_device": 3,
        "contactor_application_validated": False,
        "robot_pdu_feed_count": 5, "fuse_holder_count": 6,
        "fuse_values_selected": False, "final_conductors_selected": False,
        "functional_safety_approved": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "power-core-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in files])
    if REL.exists(): shutil.rmtree(REL)
    shutil.copytree(OUT, REL)
    release_root = ROOT / "release" / "hr30" / "whole-body-p0.1"
    release_root.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "index.html", "package-status.json"):
        shutil.copy2(WB / name, release_root / name)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
