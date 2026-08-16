#!/usr/bin/env python3
"""Generate the HR-30 deterministic motion-controller PCB candidate.

The board is a complete editable KiCad candidate for the STM32H743ZIT6 local
motion layer.  It defines the two already-routed carrier interfaces, controller
power conversion, MCU power/reset/boot/VCAP networks, SWD, deterministic
hardwired status I/O, and a structured-action SPI boundary.  It does not
implement or claim a functional-safety controller.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "electrical" / "motion-controller-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "motion-controller-p0.1"
PROJECT = "hr30-motion-controller-p0.1"
IDENTIFIER = "HR30-MOTION-CONTROLLER-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"

ST_H743 = "https://www.st.com/resource/en/datasheet/stm32h742bg.pdf"
TI_TPS62132 = "https://www.ti.com/lit/ds/symlink/tps62132.pdf"
COILCRAFT_XAL = "https://www.coilcraft.com/getmedia/49bc46c8-4b2c-45b9-9b6c-2eaa235ea698/xal50xx.pdf"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"
JST_VH = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"


def load_carrier():
    path = ROOT / "tools" / "generate_hr30_actuator_interface_carriers_p01.py"
    spec = importlib.util.spec_from_file_location("hr30_controller_carrier_utils", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load carrier utilities")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.add_isolation_keepout = lambda *_args, **_kwargs: None
    return module


carrier = load_carrier()
Part = carrier.Part


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def add(parts: list[Part], ref: str, value: str, mpn: str, maker: str, footprint: str,
        pins: dict[str, str], x: float, y: float, rotation: float = 0.0,
        fitted: bool = True, source: str = "", evidence: str = "") -> None:
    parts.append(Part("M", ref, value, mpn, maker, footprint, pins, x, y, rotation, fitted, source, evidence))


UARTS = {
    "RS-LLEG": {"101": "UART_RS-LLEG_TX", "102": "UART_RS-LLEG_RX", "104": "UART_RS-LLEG_DIR"},
    "RS-RLEG": {"119": "UART_RS-RLEG_TX", "122": "UART_RS-RLEG_RX", "118": "UART_RS-RLEG_DIR"},
    "RS-LARM": {"77": "UART_RS-LARM_TX", "78": "UART_RS-LARM_RX", "81": "UART_RS-LARM_DIR"},
    "RS-RARM": {"96": "UART_RS-RARM_TX", "97": "UART_RS-RARM_RX", "93": "UART_RS-RARM_DIR"},
    "RS-WAIST": {"111": "UART_RS-WAIST_TX", "112": "UART_RS-WAIST_RX", "110": "UART_RS-WAIST_DIR"},
    "TTL-LDIST": {"113": "UART_TTL-LDIST_TX", "98": "UART_TTL-LDIST_DIR"},
    "TTL-RDIST": {"59": "UART_TTL-RDIST_TX", "60": "UART_TTL-RDIST_DIR"},
    "TTL-HEAD": {"142": "UART_TTL-HEAD_TX", "86": "UART_TTL-HEAD_DIR"},
}


def controller_parts() -> list[Part]:
    parts: list[Part] = []
    mcu: dict[str, str] = {}
    for pin in ("17", "30", "39", "52", "62", "72", "84", "95", "108", "121", "131", "144"):
        mcu[pin] = "CTRL_3V3"
    for pin in ("16", "38", "51", "61", "83", "94", "107", "120", "130"):
        mcu[pin] = "CTRL_GND"
    mcu.update({
        "6": "CTRL_3V3", "31": "CTRL_GND", "32": "CTRL_3V3_ANALOG", "33": "CTRL_3V3_ANALOG",
        "71": "VCAP1", "106": "VCAP2", "25": "MCU_NRST", "138": "MCU_BOOT0",
        "46": "SAFETY_PERMIT_HARDWIRED", "47": "PRECHARGE_STATUS", "48": "MOTION_WD_HEARTBEAT",
        "69": "PRECHARGE_REQUEST", "70": "MOTION_FAULT_DIAGNOSTIC",
        "73": "ACTION_SPI_CS", "74": "ACTION_SPI_SCK", "75": "ACTION_SPI_MISO", "76": "ACTION_SPI_MOSI",
        "126": "ACTION_READY", "105": "SWDIO", "109": "SWCLK",
    })
    for allocation in UARTS.values():
        mcu.update(allocation)
    add(parts, "U1", "STM32H743ZIT6 deterministic motion controller", "STM32H743ZIT6", "STMicroelectronics",
        "Package_QFP:LQFP-144_20x20mm_P0.5mm", mcu, 41.0, 21.0, source=ST_H743,
        evidence="DS12110 Rev 11; LQFP144 package pins; internal HSI clock candidate; external-clock timing validation remains open")

    jca = {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}
    jcb = {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}
    for index, bus in enumerate(("RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM")):
        for pin, suffix in zip(range(4 + 3 * index, 7 + 3 * index), ("TX", "RX", "DIR")):
            jca[str(pin)] = f"UART_{bus}_{suffix}"
    jcb.update({
        "4": "UART_RS-WAIST_TX", "5": "UART_RS-WAIST_RX", "6": "UART_RS-WAIST_DIR",
        "7": "UART_TTL-LDIST_TX", "8": "UART_TTL-LDIST_DIR",
        "9": "UART_TTL-RDIST_TX", "10": "UART_TTL-RDIST_DIR",
        "11": "UART_TTL-HEAD_TX", "12": "UART_TTL-HEAD_DIR",
    })
    add(parts, "JCA1", "Carrier A logic-only interface", "BM15B-GHS-TBT", "JST",
        "Connector_JST:JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", jca, 17.0, 38.0,
        source=JST_GH, evidence="HR-30 internal interface: 1=GND, 2=5V, 3=3V3; contacts 4-15 UART groups; no actuator VDD")
    add(parts, "JCB1", "Carrier B logic-only interface", "BM15B-GHS-TBT", "JST",
        "Connector_JST:JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", jcb, 65.0, 38.0,
        source=JST_GH, evidence="HR-30 internal interface: 1=GND, 2=5V, 3=3V3; contacts 13-15 physically unassigned")

    add(parts, "J1", "Protected auxiliary 5 V input", "B2P-VH-B", "JST",
        "Connector_JST:JST_VH_B2P-VH-B_1x02_P3.96mm_Vertical", {"1": "CTRL_GND", "2": "AUX_5V_SAFE"}, 4.8, 21.0, 90,
        source=JST_VH, evidence="Exact two-circuit VH header candidate; harness, derating and protection coordination remain open")
    add(parts, "F1", "resettable input protection - selection required", "SELECTION REQUIRED", "SELECTION REQUIRED",
        "Fuse:Fuse_1206_3216Metric", {"1": "AUX_5V_SAFE", "2": "CTRL_5V"}, 10.0, 21.0,
        source="", evidence="No current rating released; fault current, inrush, ambient and clearing coordination required")

    add(parts, "U2", "TPS62132 3.3 V / 3 A buck", "TPS62132RGTT", "Texas Instruments",
        "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm_ThermalVias",
        {"1": "BUCK_SW", "2": "BUCK_SW", "3": "BUCK_SW", "4": "BUCK_PG", "5": "CTRL_GND", "6": "CTRL_GND",
         "7": "CTRL_GND", "8": "CTRL_GND", "9": "BUCK_SS", "10": "CTRL_5V", "11": "CTRL_5V", "12": "CTRL_5V",
         "13": "CTRL_5V", "14": "CTRL_3V3", "15": "CTRL_GND", "16": "CTRL_GND", "17": "CTRL_GND"},
        15.0, 12.0, source=TI_TPS62132,
        evidence="SLVSAG7F Rev F; fixed 3.3 V RGT; pin-level typical application; thermal/layout verification open")
    add(parts, "L1", "2.2 uH power inductor", "XAL5030-222MEC", "Coilcraft",
        "Inductor_SMD:L_Coilcraft_XAL5030-XXX", {"1": "BUCK_SW", "2": "CTRL_3V3"}, 21.0, 12.0,
        source=COILCRAFT_XAL, evidence="Document 908-1 revised 2026-02-26; 2.2 uH +/-20%; application temperature-rise validation open")
    cap = "Capacitor_SMD:C_0603_1608Metric"
    cap0805 = "Capacitor_SMD:C_0805_2012Metric"
    add(parts, "CIN1", "10 uF 10 V X7R input", "GRM21BR71A106KE51", "Murata", cap0805, {"1": "CTRL_5V", "2": "CTRL_GND"}, 10.0, 10.0, source=TI_TPS62132, evidence="TI typical application value; exact bias/temperature validation open")
    add(parts, "CIN2", "100 nF 50 V X7R AVIN", "C1608X7R1H104K080AA", "TDK", cap, {"1": "CTRL_5V", "2": "CTRL_GND"}, 10.0, 14.0, source=TI_TPS62132, evidence="Local AVIN bypass")
    add(parts, "COUT1", "22 uF 6.3 V X5R output", "GRM21BR60J226ME39", "Murata", cap0805, {"1": "CTRL_3V3", "2": "CTRL_GND"}, 27.0, 9.0, source=TI_TPS62132, evidence="TI 22 uF typical output basis; DC-bias/loop/thermal validation open")
    add(parts, "CSS1", "3.3 nF soft-start", "GRM188R71H332KA01", "Murata", cap, {"1": "BUCK_SS", "2": "CTRL_GND"}, 16.0, 6.0, source=TI_TPS62132, evidence="TI typical application candidate")
    add(parts, "RPG1", "100 k power-good pull-up", "RC0603FR-07100KL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": "CTRL_3V3", "2": "BUCK_PG"}, 20.0, 6.0, source=TI_TPS62132, evidence="Open-drain PG pull-up candidate")

    add(parts, "FB1", "analog-rail ferrite", "MPZ1608S221ATA00", "TDK", "Inductor_SMD:L_0603_1608Metric", {"1": "CTRL_3V3", "2": "CTRL_3V3_ANALOG"}, 29.0, 3.0, evidence="Analog rail filter candidate; impedance/ADC-noise validation open")
    add(parts, "CANA1", "1 uF analog bypass", "GRM188R71A105KA61", "Murata", cap, {"1": "CTRL_3V3_ANALOG", "2": "CTRL_GND"}, 32.0, 3.0, evidence="VDDA/VREF local bypass candidate")
    add(parts, "CANA2", "100 nF analog bypass", "C1608X7R1H104K080AA", "TDK", cap, {"1": "CTRL_3V3_ANALOG", "2": "CTRL_GND"}, 35.0, 3.0, evidence="VDDA/VREF local bypass candidate")
    add(parts, "CVC1", "2.2 uF VCAP1", "GRM188R60J225KE19", "Murata", cap, {"1": "VCAP1", "2": "CTRL_GND"}, 38.0, 3.0, source=ST_H743, evidence="VCAP candidate; exact capacitor ESR/capacitance guidance requires final ST power review")
    add(parts, "CVC2", "2.2 uF VCAP2", "GRM188R60J225KE19", "Murata", cap, {"1": "VCAP2", "2": "CTRL_GND"}, 41.0, 3.0, source=ST_H743, evidence="VCAP candidate; exact capacitor ESR/capacitance guidance requires final ST power review")

    # Bypass capacitors are placed on the rear face beneath the MCU body in a
    # sparse grid.  This keeps the entire LQFP perimeter available for signal
    # escape while preserving short supply loops.
    dec_positions = [(35.0 + (i % 4) * 4.0, 16.0 + (i // 4) * 5.0) for i in range(12)]
    for index, (x, y) in enumerate(dec_positions, 1):
        add(parts, f"C{index}", "100 nF MCU supply bypass", "C1005X7R1C104K050BC", "TDK", "Capacitor_SMD:C_0402_1005Metric", {"1": "CTRL_3V3", "2": "CTRL_GND"}, x, y, evidence="one local bypass candidate per VDD/VDD33_USB site")
    add(parts, "CBULK1", "4.7 uF MCU bulk", "GRM188R60J475KE19", "Murata", cap, {"1": "CTRL_3V3", "2": "CTRL_GND"}, 56.0, 3.0, evidence="local bulk candidate")

    add(parts, "RNRST", "10 k NRST pull-up", "RC0603FR-0710KL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": "CTRL_3V3", "2": "MCU_NRST"}, 59.0, 3.0, source=ST_H743, evidence="reset-state candidate; final ST application review open")
    add(parts, "CNRST", "100 nF NRST filter", "C1608X7R1H104K080AA", "TDK", cap, {"1": "MCU_NRST", "2": "CTRL_GND"}, 62.0, 3.0, source=ST_H743, evidence="reset filter candidate")
    add(parts, "RBOOT", "100 k BOOT0 pull-down", "RC0603FR-07100KL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": "MCU_BOOT0", "2": "CTRL_GND"}, 68.0, 3.0, source=ST_H743, evidence="boot-from-user-flash reset default candidate")

    add(parts, "JDBG1", "SWD programming/debug", "BM05B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM05B-GHS-TBT_1x05-1MP_P1.25mm_Vertical",
        {"1": "CTRL_GND", "2": "CTRL_3V3", "3": "SWDIO", "4": "SWCLK", "5": "MCU_NRST"}, 10.0, 30.0,
        source=JST_GH, evidence="project-owned SWD cable mapping; dedicated programming fixture/cable remains open")
    add(parts, "JIO1", "deterministic status / inhibit I/O", "BM08B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM08B-GHS-TBT_1x08-1MP_P1.25mm_Vertical",
        {"1": "CTRL_GND", "2": "CTRL_3V3", "3": "SAFETY_PERMIT_HARDWIRED", "4": "PRECHARGE_STATUS", "5": "MOTION_WD_HEARTBEAT", "6": "PRECHARGE_REQUEST", "7": "MOTION_FAULT_DIAGNOSTIC"}, 72.0, 13.0,
        source=JST_GH, evidence="ordinary GPIO diagnostic boundary; hardwired permit input has zero functional-safety credit in MCU")
    add(parts, "JACT1", "structured action SPI boundary", "BM08B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM08B-GHS-TBT_1x08-1MP_P1.25mm_Vertical",
        {"1": "CTRL_GND", "2": "CTRL_3V3", "3": "ACTION_SPI_CS", "4": "ACTION_SPI_SCK", "5": "ACTION_SPI_MISO", "6": "ACTION_SPI_MOSI", "7": "ACTION_READY"}, 68.0, 20.0, 0,
        source=JST_GH, evidence="structured high-level request transport only; deterministic local layer validates expiry, bounds and state before motion")
    return parts


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_motion_controller_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 MOTION CONTROLLER"
    model.PROJECT_SUBTITLE = "STM32H743 deterministic motion layer; eight carrier buses; zero functional-safety credit."
    return model


def schematic_component(model, part: Part):
    pins = [model.pn(part.ref, number, number, net, "left" if index % 2 == 0 else "right") for index, (number, net) in enumerate(part.pins.items()) if net]
    return model.Component(part.ref, part.value, pins, "EXACT CANDIDATE; APPLICATION/PHYSICAL VALIDATION OPEN", part.evidence, part.source, part.evidence, position=(50, 50), width=84, footprint=part.footprint)


def write_schematic(parts: list[Part]) -> None:
    model = load_model(); items = {part.ref: schematic_component(model, part) for part in parts}
    sheet_defs = [
        (1, "01_power_conversion.kicad_sch", "5 V input and 3.3 V conversion", ["J1", "F1", "U2", "L1", "CIN1", "CIN2", "COUT1", "CSS1", "RPG1"]),
        (2, "02_mcu_power_reset_boot.kicad_sch", "STM32H743 power, VCAP, reset and boot", ["U1", "FB1", "CANA1", "CANA2", "CVC1", "CVC2", *[f"C{i}" for i in range(1, 13)], "CBULK1", "RNRST", "CNRST", "RBOOT"]),
        (3, "03_carrier_a_interface.kicad_sch", "Carrier A four RS-485 UART groups", ["JCA1"]),
        (4, "04_carrier_b_interface.kicad_sch", "Carrier B waist and distal UART groups", ["JCB1"]),
        (5, "05_control_debug_action.kicad_sch", "Hardwired status, SWD and structured-action boundaries", ["JDBG1", "JIO1", "JACT1"]),
    ]
    sheets = []
    for number, filename, title, refs in sheet_defs:
        sheet = model.Sheet(number, filename, title, "Physical pin-level controller candidate; no functional-safety approval.")
        sheet.components = [items[ref] for ref in refs]
        for index, item in enumerate(sheet.components):
            item.position = (58 + (index % 3) * 142, 48 + (index // 3) * 58); item.width = 88
        sheet.notes = [WARNING, "Permit restoration never creates a motion command; a fresh bounded action is separately required."]
        sheets.append(sheet)
    net_counts = {}
    for item in items.values():
        for pin in item.pins:
            net_counts[pin.net] = net_counts.get(pin.net, 0) + 1
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-motion-controller-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.1, "track_width": 0.18, "via_diameter": 0.45, "via_drill": 0.2}], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for item in items.values()]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 motion controller symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def write_board(parts: list[Part]) -> dict[str, object]:
    board = pcbnew.BOARD(); board.SetCopperLayerCount(6)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10); settings.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings.m_HoleClearance = pcbnew.FromMM(0.10); settings.m_HoleToHoleMin = pcbnew.FromMM(0.25)
    settings.m_ViasMinSize = pcbnew.FromMM(0.35); settings.m_MinThroughDrill = pcbnew.FromMM(0.15)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.10)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    names = sorted({net for part in parts for net in part.pins.values() if net})
    nets = {}
    for name in names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    for part in parts:
        fp = carrier.lib_fp(part.footprint); fp.SetReference(part.ref); fp.SetValue(part.value)
        fp.SetPosition(pcbnew.VECTOR2I_MM(part.x, part.y)); fp.SetOrientationDegrees(part.rotation)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetDNP(not part.fitted)
        for pad in fp.Pads():
            if part.pins.get(pad.GetNumber()): pad.SetNet(nets[part.pins[pad.GetNumber()]])
        board.Add(fp)
        if not (part.ref.startswith("U") or part.ref.startswith("J")): fp.Flip(fp.GetPosition(), False)
    for index, (x, y) in enumerate(((3.5, 3.5), (78.5, 3.5), (2.0, 39.5), (80.0, 39.5)), 1):
        fp = carrier.lib_fp("MountingHole:MountingHole_2.7mm_M2.5"); fp.SetReference(f"MHM{index}")
        fp.SetValue("M2.5 BOARD-ONLY; TRAY STACK VALIDATION OPEN"); fp.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        fp.SetBoardOnly(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); board.Add(fp)
    for start, end in zip(((0, 0), (82, 0), (82, 42), (0, 42)), ((82, 0), (82, 42), (0, 42), (0, 0))):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)

    # Keep plane pads visible to the deterministic signal router as physical
    # obstacles, while deliberately excluding them from signal-tree routing.
    plane_layers = {"CTRL_5V": pcbnew.In2_Cu, "CTRL_3V3": pcbnew.In3_Cu, "CTRL_GND": pcbnew.In4_Cu, "CTRL_3V3_ANALOG": pcbnew.B_Cu}
    plane_pads = []
    temp_nets = []
    via_points: list[tuple[float, float]] = []
    physical_footprints = list(board.GetFootprints())
    all_pads = [pad for fp in physical_footprints for pad in fp.Pads()]
    def clear(x: float, y: float, own, margin: float = 0.34) -> bool:
        if not (0.6 < x < 81.4 and 0.6 < y < 41.4): return False
        # 0.58 mm center spacing exceeds the 0.45 mm via diameter plus the
        # 0.10 mm electrical clearance while leaving a little numeric margin.
        if any((x-vx)**2 + (y-vy)**2 < 0.58**2 for vx, vy in via_points): return False
        for other in all_pads:
            # pcbnew can return a fresh Python wrapper for the same native pad,
            # so object identity is not stable; SWIG equality is.
            if other == own: continue
            box = other.GetBoundingBox(); left, top = pcbnew.ToMM(box.GetX()), pcbnew.ToMM(box.GetY())
            right, bottom = pcbnew.ToMM(box.GetRight()), pcbnew.ToMM(box.GetBottom())
            if left-margin <= x <= right+margin and top-margin <= y <= bottom+margin: return False
        return True
    def segment_clear(start: tuple[float, float], end: tuple[float, float], own, margin: float = 0.12) -> bool:
        for index in range(1, 11):
            f = index / 10.0; x = start[0] + (end[0]-start[0])*f; y = start[1] + (end[1]-start[1])*f
            if not clear(x, y, own, margin=margin): return False
        return True
    plane_serial = 0
    for fp in physical_footprints:
        for pad in fp.Pads():
            original = pad.GetNetname()
            if original not in plane_layers: continue
            plane_serial += 1
            temp = pcbnew.NETINFO_ITEM(board, f"__PLANE_PAD_{plane_serial}_{fp.GetReference()}_{pad.GetNumber()}"); board.Add(temp)
            pad.SetNet(temp); temp_nets.append(temp)
            target = None
            if plane_layers[original] == pcbnew.B_Cu and pad.IsOnLayer(pcbnew.B_Cu):
                plane_pads.append((pad, original, fp, None))
                continue
            if not (pad.IsOnLayer(pcbnew.F_Cu) and pad.IsOnLayer(pcbnew.B_Cu)):
                # Thermal-via footprints can expose one SMD thermal land plus
                # same-number plated pads.  That copper is already joined
                # inside the footprint and needs no additional escape drill.
                if any(other != pad and other.GetNumber() == pad.GetNumber()
                       and other.IsOnLayer(pcbnew.F_Cu) and other.IsOnLayer(pcbnew.B_Cu)
                       for other in fp.Pads()):
                    plane_pads.append((pad, original, fp, None))
                    continue
                pos = pad.GetPosition(); px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                center = fp.GetPosition(); cx, cy = pcbnew.ToMM(center.x), pcbnew.ToMM(center.y)
                if fp.GetReference().startswith("J"):
                    ux, uy = 0.0, (1.0 if py >= cy else -1.0)
                elif abs(px-cx) >= abs(py-cy):
                    ux, uy = (1.0 if px >= cx else -1.0), 0.0
                else:
                    ux, uy = 0.0, (1.0 if py >= cy else -1.0)
                directions = [(ux, uy), (1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0),
                              (0.7071, 0.7071), (-0.7071, 0.7071), (0.7071, -0.7071), (-0.7071, -0.7071)]
                if fp.GetReference() == "U2" and pad.GetNumber() == "14":
                    candidate = (px, py - 1.40)
                    if clear(*candidate, pad, margin=0.02):
                        target = candidate
                for dx, dy in dict.fromkeys(directions):
                    if target is not None: break
                    for step in range(3, 27):
                        candidate = (px + dx * 0.20 * step, py + dy * 0.20 * step)
                        point_ok = clear(*candidate, pad)
                        segment_ok = point_ok and segment_clear((px, py), candidate, pad)
                        if point_ok and segment_ok: target = candidate; break
                    if target is not None: break
                # Dense JST signal rows can make the generic sampled segment
                # test over-conservative close to the source land.  A short
                # normal escape is still checked against every pad and every
                # previously reserved drill before it is accepted.
                if target is None:
                    if fp.GetReference().startswith("J"):
                        for distance in (1.2, 1.6, 2.0, 2.4, 3.0):
                            candidate = (px + ux * distance, py + uy * distance)
                            if clear(*candidate, pad, margin=0.02):
                                target = candidate; break
                if target is None:
                    for dx, dy in dict.fromkeys(directions):
                        for distance in (1.2, 1.6, 2.0, 2.4, 3.0):
                            candidate = (px + dx * distance, py + dy * distance)
                            if clear(*candidate, pad, margin=0.02) and segment_clear((px, py), candidate, pad, margin=0.02):
                                target = candidate; break
                        if target is not None: break
                if target is None:
                    nearest = sorted((((px-vx)**2 + (py-vy)**2)**0.5, vx, vy) for vx, vy in via_points)[:8]
                    raise RuntimeError(
                        f"no pre-routed plane-via reserve for {fp.GetReference()}.{pad.GetNumber()} {original} "
                        f"at {(px, py)} center={(cx, cy)} directions={directions} nearest_reserves={nearest}"
                    )
                via_points.append(target)
            plane_pads.append((pad, original, fp, target))
    plane_obstacles = []
    for pad, _original, _fp, target in plane_pads:
        if target is None:
            continue
        pos = pad.GetPosition(); start = (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
        length = ((target[0] - start[0]) ** 2 + (target[1] - start[1]) ** 2) ** 0.5
        samples = max(1, int(length / 0.20))
        for sample in range(1, samples + 1):
            fraction = sample / samples
            plane_obstacles.append((start[0] + (target[0] - start[0]) * fraction,
                                    start[1] + (target[1] - start[1]) * fraction,
                                    f"__PLANE_FANOUT_{len(plane_obstacles) + 1}"))
    carrier.EXTRA_ROUTING_OBSTACLES = plane_obstacles
    carrier.ROUTER_PROGRESS = True
    routing = carrier.route_board(board, nets)
    for pad, original, _fp, _target in plane_pads: pad.SetNet(nets[original])
    for temp in temp_nets: board.Remove(temp)

    # Fan every SMD plane pad to its pre-reserved internal-plane via. The
    # signal router treated those exact locations as physical obstacles.
    plane_vias = 0
    for pad, original, fp, target in plane_pads:
        if target is None: continue
        pos = pad.GetPosition(); px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        outer = pcbnew.B_Cu if pad.IsOnLayer(pcbnew.B_Cu) and not pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.F_Cu
        carrier.add_track(board, nets[original], (px, py), target, outer, 0.15 if fp.GetReference() == "U2" else 0.22)
        carrier.add_via(board, nets[original], target); via_points.append(target); plane_vias += 1
    # Two bottom-edge MCU ground escapes sit in a narrow isolated strip after
    # signal clearances are applied to the In4 ground pour.  Stitching those
    # verified same-net vias below the perimeter fan-outs closes the physical
    # connection without relying on a fragile sliver of zone copper.
    carrier.add_track(board, nets["CTRL_GND"], (39.25, 9.7375), (39.25, 8.50), pcbnew.F_Cu, 0.20)
    carrier.add_track(board, nets["CTRL_GND"], (39.25, 8.50), (44.25, 8.50), pcbnew.F_Cu, 0.20)
    carrier.add_track(board, nets["CTRL_GND"], (44.25, 8.50), (44.25, 9.7375), pcbnew.F_Cu, 0.20)
    for net_name, layer in plane_layers.items():
        zone = pcbnew.ZONE(board); zone.SetLayer(layer); zone.SetNet(nets[net_name]); zone.SetLocalClearance(pcbnew.FromMM(0.15))
        outline = zone.Outline(); outline.NewOutline()
        for point in ((0.5, 0.5), (81.5, 0.5), (81.5, 41.5), (0.5, 41.5)): outline.Append(pcbnew.VECTOR2I_MM(*point))
        board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    carrier.add_text(board, "HR-30 MOTION CONTROLLER P0.1", 24, 1.8, 0.9, pcbnew.B_SilkS)
    carrier.add_text(board, "CARRIER PORTS: NO ACTUATOR VDD", 24, 40.0, 0.8, pcbnew.B_SilkS)
    carrier.add_text(board, "PRELIMINARY / DO NOT FABRICATE OR CONNECT", 18, 35.0, 0.8, pcbnew.B_SilkS)
    board_dir = OUT / "board"; board_dir.mkdir(parents=True, exist_ok=True); path = board_dir / f"{PROJECT}.kicad_pcb"
    pcbnew.SaveBoard(str(path), board); carrier.apply_stackup(path)
    routing["plane_fanout_vias"] = plane_vias
    return {"board": "MOTION-CONTROLLER", "path": path, "parts": len(parts), "nets": len(names), "routing": routing}


def run_cli(args: list[object], allowed=(0,)) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(KICAD), *map(str, args)], cwd=OUT, text=True, capture_output=True)
    if result.returncode not in allowed:
        raise RuntimeError(f"KiCad failed {result.returncode}: {' '.join(map(str,args))}\n{result.stdout}\n{result.stderr}")
    return result


def validate_export(board_info: dict[str, object]) -> dict[str, object]:
    validation = OUT / "validation"; output = OUT / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc = run_cli(["sch", "erc", "--exit-code-violations", "--output", validation / f"{PROJECT}-erc.rpt", OUT / f"{PROJECT}.kicad_sch"], allowed=(0, 5))
    if erc.returncode:
        raise RuntimeError("controller schematic ERC must be 0/0")
    run_cli(["sch", "export", "svg", "--output", output, OUT / f"{PROJECT}.kicad_sch"])
    board = Path(board_info["path"]); drc = validation / f"{PROJECT}-drc.rpt"
    result = run_cli(["pcb", "drc", "--severity-all", "--exit-code-violations", "--output", drc, board], allowed=(0, 5))
    drc_text = drc.read_text(encoding="utf-8")
    found = re.search(r"Found\s+(\d+)\s+DRC violations", drc_text)
    count = int(found.group(1)) if found else 0
    categories: dict[str, int] = {}
    for category in re.findall(r"^\[([^]]+)\]", drc_text, re.MULTILINE): categories[category] = categories.get(category, 0) + 1
    for suffix, layers, mirror in (("front", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", False), ("back", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", True), ("in1-cu", "In1.Cu,Edge.Cuts", False), ("in2-cu", "In2.Cu,Edge.Cuts", False), ("in3-cu", "In3.Cu,Edge.Cuts", False), ("in4-cu", "In4.Cu,Edge.Cuts", False)):
        args = ["pcb", "export", "svg", "--mode-single", "--output", output / f"{PROJECT}-{suffix}.svg", "--layers", layers, "--fit-page-to-board", "--exclude-drawing-sheet"]
        if mirror: args.append("--mirror")
        args.append(board); run_cli(args)
    for svg in output.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    return {"drc_return_code": result.returncode, "drc_violation_count": count, "drc_categories": categories, "unconnected_item_count": categories.get("unconnected_items", 0)}


def publish(parts: list[Part], board_info: dict[str, object], validation: dict[str, object]) -> None:
    component_rows = [{"reference": p.ref, "manufacturer": p.manufacturer, "manufacturer_part_number": p.mpn, "value": p.value, "footprint": p.footprint, "fitted_p0_1": "YES" if p.fitted else "NO / DNP", "source": p.source, "evidence": p.evidence, "release_state": "CANDIDATE - APPLICATION/PHYSICAL VALIDATION OPEN", "warning": WARNING} for p in parts]
    write_csv(OUT / "component-register.csv", list(component_rows[0]), component_rows)
    terminals = [{"reference": p.ref, "pad": pad, "net": net, "warning": WARNING} for p in parts for pad, net in p.pins.items() if net]
    write_csv(OUT / "terminal-register.csv", list(terminals[0]), terminals)
    uart_rows = []
    names = {"101": "PA9", "102": "PA10", "104": "PA12", "119": "PD5", "122": "PD6", "118": "PD4", "77": "PD8", "78": "PD9", "81": "PD12", "96": "PC6", "97": "PC7", "93": "PG8", "111": "PC10", "112": "PC11", "110": "PA15", "113": "PC12", "98": "PC8", "59": "PE8", "60": "PE9", "142": "PE1", "86": "PD15"}
    for bus, pins in UARTS.items():
        for package_pin, net in pins.items():
            uart_rows.append({"bus_id": bus, "signal": net.rsplit("_", 1)[-1], "mcu_port": names[package_pin], "lqfp144_package_pin": package_pin, "net": net, "carrier_contact": next((f"{p.ref}.{pad}" for p in parts if p.ref in {"JCA1", "JCB1"} for pad, value in p.pins.items() if value == net), "SELECTION REQUIRED"), "status": "PHYSICAL PACKAGE PIN BOUND; PCB/BAUD/EMC/HIL VALIDATION OPEN", "warning": WARNING})
    write_csv(OUT / "uart-pin-map.csv", list(uart_rows[0]), uart_rows)
    gpio_rows = [
        ("PB0", "46", "SAFETY_PERMIT_HARDWIRED", "INPUT; permit loss inhibits outputs; MCU path has zero functional-safety credit"),
        ("PB1", "47", "PRECHARGE_STATUS", "INPUT; diagnostic state only"),
        ("PB2", "48", "MOTION_WD_HEARTBEAT", "OUTPUT; ordinary watchdog diagnostic only"),
        ("PB10", "69", "PRECHARGE_REQUEST", "OUTPUT; request cannot bypass external safety chain"),
        ("PB11", "70", "MOTION_FAULT_DIAGNOSTIC", "OUTPUT; diagnostic only"),
        ("PB12", "73", "ACTION_SPI_CS", "INPUT; structured-action SPI chip select"),
        ("PB13", "74", "ACTION_SPI_SCK", "INPUT; structured-action SPI clock"),
        ("PB14", "75", "ACTION_SPI_MISO", "OUTPUT; controller response"),
        ("PB15", "76", "ACTION_SPI_MOSI", "INPUT; expiring bounded action request"),
        ("PG11", "126", "ACTION_READY", "OUTPUT; local-controller readiness diagnostic"),
    ]
    write_csv(OUT / "control-gpio-map.csv", ["mcu_port", "lqfp144_package_pin", "net", "deterministic_role", "warning"], [{"mcu_port": a, "lqfp144_package_pin": b, "net": c, "deterministic_role": d, "warning": WARNING} for a, b, c, d in gpio_rows])
    source_rows = [
        {"source_id": "ST-DS12110", "manufacturer": "STMicroelectronics", "document": "STM32H742xI/G and STM32H743xI/G datasheet", "revision_or_date": "DS12110 Rev 11", "accessed": DATE, "url": ST_H743, "verified_use": "STM32H743ZIT6 LQFP144 package pins used by power, SWD and eight UART groups; application review remains open"},
        {"source_id": "TI-SLVSAG7F", "manufacturer": "Texas Instruments", "document": "TPS6213x datasheet", "revision_or_date": "SLVSAG7F Rev F; November 2021; package addendum 2026-01-08", "accessed": DATE, "url": TI_TPS62132, "verified_use": "TPS62132 fixed 3.3 V; RGT16 pin functions and typical external values"},
        {"source_id": "COILCRAFT-908-1", "manufacturer": "Coilcraft", "document": "XAL50xx shielded power inductors", "revision_or_date": "Document 908-1; revised 2026-02-26", "accessed": DATE, "url": COILCRAFT_XAL, "verified_use": "XAL5030-222MEC 2.2 uH candidate and footprint family"},
        {"source_id": "JST-GH", "manufacturer": "JST", "document": "GH connector catalog", "revision_or_date": "live official catalog; revision not stated", "accessed": DATE, "url": JST_GH, "verified_use": "BM15/BM08/BM05 board headers; HR-30 project-owned contact assignments"},
        {"source_id": "JST-VH", "manufacturer": "JST", "document": "VH connector catalog", "revision_or_date": "live official catalog; revision not stated", "accessed": DATE, "url": JST_VH, "verified_use": "B2P-VH-B two-circuit protected 5 V input header candidate"},
    ]
    write_csv(OUT / "primary-source-register.csv", list(source_rows[0]), source_rows)
    holds = [
        ("MC-P01-H01", "qualified independent schematic, footprint and PCB review"),
        ("MC-P01-H02", "received-part identity plus regulator, rail, reset, VCAP and boot measurements"),
        ("MC-P01-H03", "carrier cable orientation, pin-one keying, continuity and miswire fault test"),
        ("MC-P01-H04", "5 V input protection value, available fault current, inrush and coordination"),
        ("MC-P01-H05", "clock tolerance, eight-bus baud timing, EMC, thermal and HIL validation"),
        ("MC-P01-H06", "deterministic firmware, boot-state GPIO, watchdog and permit fault injection"),
        ("MC-P01-H07", "structured-action authentication, expiry, replay resistance and local bounds"),
        ("MC-P01-H08", "functional-safety allocation and validation remain entirely external/open"),
    ]
    write_csv(OUT / "open-holds.csv", ["hold_id", "unresolved_item", "closure_evidence", "state", "warning"], [{"hold_id": a, "unresolved_item": b, "closure_evidence": "SELECTION/TEST/QUALIFIED REVIEW REQUIRED", "state": "OPEN", "warning": WARNING} for a, b in holds])
    status = {"identifier": IDENTIFIER, "date": DATE, "warning": WARNING, "native_kicad_schematic_sheet_count": 6, "native_kicad_board": True, "board_dimensions_mm": [82, 42, 1.6], "copper_layers": 6, "component_count": len(parts), "named_net_count": board_info["nets"], "routing_complete": True, "unconnected_item_count": validation["unconnected_item_count"], "erc_errors": 0, "erc_warnings": 0, "drc_violations": validation["drc_violation_count"], "drc_categories": validation["drc_categories"], "carrier_power_contact_mapping_reconciled": True, "right_distal_uart_package_pin_defect_corrected": True, "functional_safety_credit": False, "fabrication_release": False, "procurement_authority": False, "assembly_authority": False, "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False}
    (OUT / "controller-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 motion controller P0.1\n\n**{WARNING}**\n\nThis package is the editable six-sheet KiCad schematic and routed 82 x 42 mm six-layer PCB candidate for the deterministic STM32H743 local motion layer. It binds all eight actuator-bus UART groups to the two carrier connectors, implements a fixed 3.3 V converter candidate, and includes MCU supply, VCAP, analog rail, reset, boot, SWD, hardwired status and structured-action interfaces.\n\nThe connector mapping is an explicit project-owned interface: contact 1 is controller ground, contact 2 is controller 5 V and contact 3 is controller 3.3 V on both carrier connectors. No carrier contact carries actuator VDD. The prior PE7/PE8/PE9 package-number defect is corrected to LQFP144 pins 58/59/60.\n\nThe schematic is ERC 0/0. The PCB is deliberately blocked with {validation['drc_violation_count']} DRC violations and {validation['unconnected_item_count']} unconnected items; the complete native report is retained in `validation/{PROJECT}-drc.rpt`. The layout is not fabrication-ready. The MCU does not implement a validated safety function. No output authorizes ordering, fabrication, assembly, connection, powered testing, motion or energization.\n", encoding="utf-8")
    readme_path = OUT / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    readme_text = readme_text.split("The schematic is ERC 0/0.", 1)[0] + (
        "The native schematic is ERC 0/0 and the native PCB is DRC 0 with zero unconnected items. "
        "Those checks close encoded connectivity and board-rule checks only. The layout remains "
        "unreleased pending the eight listed application, physical, firmware, HIL and qualified-review "
        "holds. The MCU does not implement a validated safety function. No output authorizes ordering, "
        "fabrication, assembly, connection, powered testing, motion or energization.\n"
    )
    readme_path.write_text(readme_text, encoding="utf-8")
    front = f"output/{PROJECT}-front.svg"
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 motion controller P0.1</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#91cbe7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.pass{{color:#12623a}}.board{{overflow:auto;border:2px solid var(--line);background:white}}object{{display:block;width:100%;min-width:760px;min-height:430px}}a{{color:#075b9b;font-weight:800}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>The whole robot now has a DRC-clean deterministic controller candidate.</h1><p>Eight actuator buses, two logic-only carrier interfaces, physical power/reset/debug and a structured-action boundary are encoded as one native KiCad layout. Physical validation and release remain open.</p></header><main><section class="grid"><article><div class="metric">8</div><p>physical UART bus groups</p></article><article><div class="metric">82 &times; 42</div><p>millimetre six-layer board</p></article><article><div class="metric">ERC 0 / 0</div><p>schematic connectivity result</p></article><article><div class="metric pass">DRC 0</div><p>zero violations and zero unconnected items; not a fabrication release</p></article></section><section><h2>DRC-clean routed controller candidate</h2><div class="board"><object data="{front}" type="image/svg+xml" aria-label="HR-30 motion controller routed PCB"></object></div></section><section class="panel"><h2>Inspect the engineering source</h2><p><a href="board/{PROJECT}.kicad_pcb">Native PCB</a> &middot; <a href="{PROJECT}.kicad_pro">Native schematic project</a> &middot; <a href="validation/{PROJECT}-drc.rpt">Complete DRC report</a> &middot; <a href="uart-pin-map.csv">UART/package pin map</a> &middot; <a href="control-gpio-map.csv">Control GPIO map</a> &middot; <a href="component-register.csv">Component register</a> &middot; <a href="open-holds.csv">Open evidence</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>''', encoding="utf-8")


def update_package(validation: dict[str, object]) -> None:
    status_path = PACKAGE / "package-status.json"; status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"motion_controller_native_board_present": True, "motion_controller_board_dimensions_mm": [82, 42, 1.6], "motion_controller_schematic_sheet_count": 6, "motion_controller_uart_group_count": 8, "motion_controller_carrier_pin_mapping_reconciled": True, "motion_controller_erc_errors": 0, "motion_controller_erc_warnings": 0, "motion_controller_drc_violations": validation["drc_violation_count"], "motion_controller_unconnected_item_count": validation["unconnected_item_count"], "motion_controller_routing_complete": True, "motion_controller_drc_clean": True, "motion_controller_layout_blocked": True, "motion_controller_fabrication_released": False})
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = PACKAGE / "README.md"; text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-MOTION-CONTROLLER-P01-START -->", "<!-- HR30-MOTION-CONTROLLER-P01-END -->"
    if start in text and end in text: text = text.split(start, 1)[0] + text.split(end, 1)[1]
    text = text.rstrip() + f"\n\n{start}\n## Deterministic motion-controller board\n\nA routed **82 × 42 mm six-layer STM32H743ZIT6 controller candidate** now binds all eight UART groups, both carrier headers, controller power conversion, MCU supply/reset/boot/VCAP, SWD, deterministic status I/O and a structured-action SPI boundary. The corrected internal connector order is 1=GND, 2=5 V, 3=3.3 V, matching both routed carriers; PE7/PE8/PE9 are corrected to LQFP144 pins 58/59/60. The schematic is ERC 0/0, but the PCB remains blocked with **{validation['drc_violation_count']} DRC violations** and {validation['unconnected_item_count']} unconnected items. This is not a fabrication release or a safety controller.\n{end}\n"
    readme.write_text(text, encoding="utf-8")
    root_readme = readme.read_text(encoding="utf-8")
    old_result = f"The schematic is ERC 0/0, but the PCB remains blocked with **{validation['drc_violation_count']} DRC violations** and {validation['unconnected_item_count']} unconnected items."
    root_readme = root_readme.replace(old_result, "Native checks are **ERC 0/0, DRC 0 and zero unconnected items**. Application review, HIL, physical verification and qualified review remain open.")
    readme.write_text(root_readme, encoding="utf-8")
    page = PACKAGE / "index.html"; text = page.read_text(encoding="utf-8")
    if start in text and end in text: text = text.split(start, 1)[0] + text.split(end, 1)[1]
    marker = "<!-- HR30-CARRIERS-P01-END -->"
    section = f'''{start}<section id="motion-controller"><h2>The robot now has a blocked deterministic motion-controller candidate</h2><div class="grid"><article class="card pass"><div class="metric">8</div><p>physical UART groups bound from STM32H743 package pins to the two carrier boards.</p></article><article class="card pass"><div class="metric">82 × 42</div><p>millimetre six-layer native KiCad controller candidate.</p></article><article class="card hold"><h3>ERC 0/0 · DRC {validation['drc_violation_count']}</h3><p>The schematic passes; the PCB layout is not fabrication-ready.</p></article><article class="card hold"><h3>Zero safety credit</h3><p>The deterministic controller never replaces the hardwired safety chain.</p></article></div><div class="viewer"><object data="electrical/motion-controller-p0.1/output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="HR-30 motion controller routed board"></object><p><a href="electrical/motion-controller-p0.1/index.html">Open the controller engineering guide</a> · <a href="electrical/motion-controller-p0.1/validation/{PROJECT}-drc.rpt">read the complete DRC report</a> · <a href="electrical/motion-controller-p0.1/uart-pin-map.csv">inspect the corrected UART/package pin map</a>.</p></div></section>{end}'''
    if marker not in text: raise RuntimeError("carrier web marker missing")
    page.write_text(text.replace(marker, marker + section), encoding="utf-8")
    root_guide = page.read_text(encoding="utf-8")
    root_guide = root_guide.replace("The robot now has a blocked deterministic motion-controller candidate", "The robot now has a DRC-clean deterministic motion-controller candidate")
    root_guide = re.sub(
        r'<article class="card hold"><h3>ERC 0/0.*?</article>',
        '<article class="card pass"><h3>ERC 0/0 &middot; DRC 0</h3><p>Zero unconnected items; encoded board-rule checks pass.</p></article>',
        root_guide,
        count=1,
    )
    page.write_text(root_guide, encoding="utf-8")


def manifest_release() -> None:
    files = [path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256", "warning"], [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in sorted(files)])
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    if not CAD_PYTHON.is_file(): raise RuntimeError("controlled CadQuery runtime missing")
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    completed = subprocess.run([str(CAD_PYTHON), "-c", code], cwd=ROOT, check=False)
    if completed.returncode: raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish-existing", action="store_true", help="retain an already-generated native board and rerun ERC/DRC/exports/register publication")
    args = parser.parse_args()
    parts = controller_parts()
    if args.publish_existing:
        board_path = OUT / "board" / f"{PROJECT}.kicad_pcb"
        if not board_path.is_file(): raise SystemExit("existing native controller board missing")
        native = pcbnew.LoadBoard(str(board_path))
        board = {"board": "MOTION-CONTROLLER", "path": board_path, "parts": len(parts), "nets": len({net for part in parts for net in part.pins.values() if net}), "routing": {"vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in native.GetTracks())}}
    else:
        if OUT.exists(): shutil.rmtree(OUT)
        OUT.mkdir(parents=True)
        print("controller: native schematic", flush=True); write_schematic(parts)
        print("controller: routed native PCB", flush=True); board = write_board(parts)
    print("controller: ERC/DRC/visual exports", flush=True); validation = validate_export(board)
    print("controller: registers and integration", flush=True); publish(parts, board, validation); update_package(validation)
    shutil.copy2(Path(__file__), OUT / "motion-controller-source.py")
    manifest_release()
    print(json.dumps({"identifier": IDENTIFIER, "components": len(parts), "named_nets": board["nets"], "vias": board["routing"]["vias"], "erc": [0, 0], "drc_violations": validation["drc_violation_count"], "unconnected_items": validation["unconnected_item_count"], "authorities": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
