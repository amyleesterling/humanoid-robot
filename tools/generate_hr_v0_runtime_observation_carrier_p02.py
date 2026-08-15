#!/usr/bin/env python3
"""Generate R202/P0.2 native schematic and routed receiver-carrier candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.2"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.2.md"
PROJECT = "hr-v0-runtime-observation-carrier-p0.2"
IDENTIFIER = "HR-V0-RUNTIME-OBS-CARRIER-P0.2"
REV = "R202 / P0.2 / PCB-P0.1"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin")
LIB_NAME = "PB_RUNTIME_OBS"
LIB_DIR = ECAD / f"{LIB_NAME}.pretty"
BOARD_W = 120.0
BOARD_H = 90.0


SOURCES = [
    ("OBS2-SRC-001", "Pilz", "PNOZ s4 operating manual", "21396-EN-23", "2026-06-22", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "Y32 24 V/20 mA maximum, 0.1 mA residual and 5 V maximum drop; diagnostic only"),
    ("OBS2-SRC-002", "Texas Instruments", "ISO1211/ISO1212 datasheet", "SLLSEY7G", "revised 2025-02; rechecked 2026-08-10", "https://www.ti.com/lit/ds/symlink/iso1212.pdf", "DBQ pins, Type-3 network, EMC screens, local bypass, 4 mm placement and floating SUB guidance"),
    ("OBS2-SRC-003", "Schneider Electric", "LC1D25BD product data sheet", "current generated sheet", "rechecked 2026-08-10", "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", "Built-in NO diagnostic contacts; 5 mA and 17 V minimum signalling application"),
    ("OBS2-SRC-004", "IDEC", "HW1P-1FQD-A-24V product page and HW Series Catalog_Screw", "catalog 2026-07-23", "rechecked 2026-08-10", "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1p-1fqd-a-24v", "Exact H1 identity and 7 mA family screen; received current/terminals/brightness remain open"),
    ("OBS2-SRC-005", "Raspberry Pi", "RP1 Peripherals", "current PDF", "rechecked 2026-08-10", "https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf", "Pi 5 RP1 GPIO bank is 3.3 V; exact thresholds/header allocation remain open"),
    ("OBS2-SRC-006", "Phoenix Contact", "MKDS 1/6-3,5 product record", "item 1751280; current online catalog", "rechecked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-6-35-1751280", "Exact six-position 3.5 mm-pitch PCB screw terminal; 1.1 mm drill, 21.5 mm width, 5 mm strip and 0.22-0.25 Nm catalog application data"),
    ("OBS2-SRC-007", "Murata", "GRM21BR71H104KA01 exact sheet", "product data 2016-03-03; asset 2025-07-07", "rechecked 2026-08-10", "https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810", "Exact 100 nF part identity/body; current same-series reflow land basis remains assembler-conditional"),
    ("OBS2-SRC-008", "Murata", "GRM21 land dimensions", "GRM21BC81H475KE11-01A", "2025-01-09", "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BC81H475KE11-01A.pdf", "Same-size GRM21 reflow envelope; not an assembly-process release"),
    ("OBS2-SRC-009", "TDK", "CGA3E2X7R1H103K080AA product record", "live product database", "rechecked 2026-08-10", "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E2X7R1H103K080AA", "Exact 10 nF 50 V X7R identity/body"),
    ("OBS2-SRC-010", "TDK", "Automotive MLCC delivery specification", "AC11010023", "2026-06", "https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_general_en.pdf", "CGA3 reflow land envelope; stencil/process remain open"),
    ("OBS2-SRC-011", "Panasonic Industry", "Precision thick-film chip resistors", "AOA0000C304", "2025-05-29", "https://industrial.panasonic.com/cdbs/www-data/pdf/RDA0000/AOA0000C304.pdf", "ERJ6 0805 body and reflow/flow suitability"),
    ("OBS2-SRC-012", "Panasonic Industry", "Surface-mount resistor land pattern", "DMM0000COL17", "2025-12-24", "https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/DMM0000COL17.pdf", "General ERJ6 land envelope used for 562 ohm, 1 kohm and 10 kohm candidates"),
    ("OBS2-SRC-013", "Vishay Beyschlag", "MMA0204 thin-film MELF resistors", "document 28963", "2026-06-02", "https://www.vishay.com/docs/28963/mmu0102_mma0204_mmb0207.pdf", "Exact MMA02040C1001FB300 family/body and date-code condition"),
    ("OBS2-SRC-014", "Vishay", "Recommended solder pad dimensions", "document 28950", "2022-07-12", "https://www.vishay.com/doc/?28950=", "IPC-7351 reflow land used conditionally for MMA0204"),
    ("OBS2-SRC-015", "Vishay", "D/CRCW e3 thick-film chip resistors", "document 20035", "2026-04-14", "https://www.vishay.com/docs/20035/dcrcwe3.pdf", "Exact CRCW12102K70FKEA family, 0.5 W rating and reflow land"),
]


HOLDS = [
    ("OBS2-HOLD-001", "SR1 Y32/H1", "Measure exact received H1 current over accepted voltage/temperature, identify terminals/internal circuit and prove useful indication at the 17.8 V low screen"),
    ("OBS2-HOLD-002", "Y32 application", "Qualified review of aggregate current, short/open faults, leakage, startup and noninterference with SR1/SRA1 diagnostics"),
    ("OBS2-HOLD-003", "K1/K2 contacts", "Received voltage/current, bounce, contamination, life and fault testing with the exact 2.70 kohm shunts"),
    ("OBS2-HOLD-004", "EMC/protection", "Accept the Type-3 network, 10 nF DC-bias envelope, cable environment, surge/ESD/EFT plan and any additional protection"),
    ("OBS2-HOLD-005", "PCB DFM", "Selected fabricator accepts four-layer stackup, material, copper, hole, mask, legend, annular ring, impedance-not-required statement and board drawing"),
    ("OBS2-HOLD-006", "Assembly process", "Selected assembler accepts all land patterns, paste apertures, stencil, solder alloy/profile, MELF handling, cleaning, AOI and rework controls"),
    ("OBS2-HOLD-007", "Grounding/insulation", "Accept field/compute zones, isolation corridor, floating SUB copper, creepage/clearance, enclosure, PE/parasitic and back-power behavior"),
    ("OBS2-HOLD-008", "Raspberry Pi", "Select four conflict-free GPIOs and exact physical pins; verify thresholds, pulls, cable, boot, brownout and power-loss behavior"),
    ("OBS2-HOLD-009", "Harness", "Release exact wire, ferrules, labels, strip length, torque, routing, retention, strain relief, separation and service access"),
    ("OBS2-HOLD-010", "Mounting/enclosure", "Select hole hardware, standoffs, enclosure, panel datums, keepouts, access, airflow and inspection method"),
    ("OBS2-HOLD-011", "First article", "Inspect board dimensions, holes, lands, isolation corridor, continuity, shorts, residue and component identity/orientation before any connection"),
    ("OBS2-HOLD-012", "Fault injection", "Execute open, short, cross-short, stuck-high/low, return loss, logic brownout, back-power and source-loss cases on an authorized isolated fixture"),
    ("OBS2-HOLD-013", "Thermal", "Measure worst-case resistor/device/connector temperature in the selected enclosure and accepted duty/environment"),
    ("OBS2-HOLD-014", "Safety boundary", "Qualified reviewer confirms observations remain diagnostic-only and cannot command, restore or preserve motion"),
]


FOOTPRINTS = {
    "JFIELD1": "Phoenix_MKDS_1_6_3P5_1751280",
    "JLOGIC1": "Phoenix_MKDS_1_6_3P5_1751280",
    "UOBS1": "TI_DBQ0016A_Example_Land",
    "UOBS2": "TI_DBQ0016A_Example_Land",
    **{f"RTH{i}": "Vishay_MMA0204_IPC_Reflow" for i in range(1, 5)},
    **{f"RSN{i}": "Panasonic_ERJ6_Reflow_Nominal" for i in range(1, 5)},
    **{f"RSO{i}": "Panasonic_ERJ6_Reflow_Nominal" for i in range(1, 5)},
    **{f"RPD{i}": "Panasonic_ERJ6_Reflow_Nominal" for i in range(1, 5)},
    **{f"CFI{i}": "TDK_CGA3_Reflow_Nominal" for i in range(1, 5)},
    "RW2": "Vishay_CRCW1210_Reflow",
    "RW3": "Vishay_CRCW1210_Reflow",
    "RW4": "Vishay_CRCW1210_Reflow",
    "CDEC1": "Murata_GRM21_Reflow_Nominal",
    "CDEC2": "Murata_GRM21_Reflow_Nominal",
}


PLACEMENTS = {
    "JFIELD1": (6.0, 45.0, 90.0), "JLOGIC1": (114.0, 45.0, 90.0),
    "UOBS1": (60.0, 55.0, 180.0), "UOBS2": (60.0, 40.0, 180.0),
    "RTH1": (22.0, 57.0, 0.0), "RSN1": (42.0, 57.0, 0.0), "CFI1": (49.0, 61.0, 90.0),
    "RTH2": (22.0, 53.0, 0.0), "RSN2": (42.0, 53.5, 0.0), "CFI2": (49.0, 50.0, 90.0), "RW2": (31.0, 49.0, 0.0),
    "RTH3": (22.0, 42.0, 0.0), "RSN3": (42.0, 42.0, 0.0), "CFI3": (49.0, 45.0, 90.0), "RW3": (31.0, 45.0, 0.0),
    "RTH4": (22.0, 38.5, 0.0), "RSN4": (42.0, 38.5, 0.0), "CFI4": (49.0, 35.0, 90.0), "RW4": (31.0, 35.0, 0.0),
    "RSO1": (76.0, 57.0, 0.0), "RPD1": (86.0, 60.0, 90.0),
    "RSO2": (76.0, 52.0, 0.0), "RPD2": (86.0, 49.0, 90.0), "CDEC1": (68.0, 49.0, 90.0),
    "RSO3": (76.0, 42.0, 0.0), "RPD3": (86.0, 45.0, 90.0),
    "RSO4": (76.0, 37.0, 0.0), "RPD4": (86.0, 34.0, 90.0), "CDEC2": (68.0, 34.0, 90.0),
}


def load_base():
    source = ROOT / "tools/generate_hr_v0_runtime_observation_interface_p01.py"
    spec = importlib.util.spec_from_file_location("runtime_obs_p01_for_p02", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P0.1 schematic generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.ECAD = ECAD
    module.WEB = WEB
    module.DOC = DOC
    module.PROJECT = PROJECT
    module.IDENTIFIER = IDENTIFIER
    module.REV = REV
    module.DATE = DATE
    module.SOURCES = SOURCES
    module.HOLDS = HOLDS
    module.CONNECTOR_VALUE = "Phoenix Contact MKDS 1/6-3,5 item 1751280"
    module.CONNECTOR_FOOTPRINT = f"{LIB_NAME}:{FOOTPRINTS['JFIELD1']}"
    module.FOOTPRINTS = {
        "ISO1212DBQ": f"{LIB_NAME}:TI_DBQ0016A_Example_Land",
        "Vishay MMA02040C1001FB300": f"{LIB_NAME}:Vishay_MMA0204_IPC_Reflow",
        "Panasonic ERJ6ENF5620V": f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        "Panasonic ERJ6ENF1001V": f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        "Panasonic ERJ6ENF1002V": f"{LIB_NAME}:Panasonic_ERJ6_Reflow_Nominal",
        "Vishay CRCW12102K70FKEA": f"{LIB_NAME}:Vishay_CRCW1210_Reflow",
        "TDK CGA3E2X7R1H103K080AA": f"{LIB_NAME}:TDK_CGA3_Reflow_Nominal",
        "Murata GRM21BR71H104KA01L": f"{LIB_NAME}:Murata_GRM21_Reflow_Nominal",
    }
    module.BOUNDARY_QUANTITY = 0
    module.H1EXT_QUANTITY = 0
    return module


def lset(*layers: int) -> pcbnew.LSET:
    result = pcbnew.LSET()
    for layer in layers:
        result.AddLayer(layer)
    return result


def add_smd_pad(fp: pcbnew.FOOTPRINT, number: str, x: float, y: float, sx: float, sy: float, radius: float = 0.2) -> None:
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    pad.SetRoundRectRadiusRatio(radius)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Paste, pcbnew.F_Mask))
    fp.Add(pad)


def add_pth_pad(fp: pcbnew.FOOTPRINT, number: str, x: float, y: float, diameter: float, drill: float) -> None:
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I_MM(diameter, diameter))
    pad.SetDrillSize(pcbnew.VECTOR2I_MM(drill, drill))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    layers = pcbnew.LSET.AllCuMask()
    layers.AddLayer(pcbnew.F_Mask); layers.AddLayer(pcbnew.B_Mask)
    pad.SetLayerSet(layers)
    fp.Add(pad)


def add_outline(fp: pcbnew.FOOTPRINT, x0: float, y0: float, x1: float, y1: float) -> None:
    for start, end in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        item = pcbnew.PCB_SHAPE(fp)
        item.SetShape(pcbnew.SHAPE_T_SEGMENT)
        item.SetStart(pcbnew.VECTOR2I_MM(*start)); item.SetEnd(pcbnew.VECTOR2I_MM(*end))
        item.SetLayer(pcbnew.F_Fab); item.SetWidth(pcbnew.FromMM(0.18)); fp.Add(item)


def footprint(name: str) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID(LIB_NAME, name))
    fp.SetValue(name)
    if name == "Phoenix_MKDS_1_6_3P5_1751280":
        for index in range(6): add_pth_pad(fp, str(index + 1), -8.75 + index * 3.5, 0.0, 2.10, 1.10)
        add_outline(fp, -10.75, -3.65, 10.75, 3.65)
    elif name == "TI_DBQ0016A_Example_Land":
        for index in range(8):
            y = -2.2225 + index * 0.635
            add_smd_pad(fp, str(index + 1), -2.70, y, 1.60, 0.41, 0.12)
            add_smd_pad(fp, str(16 - index), 2.70, y, 1.60, 0.41, 0.12)
        add_outline(fp, -2.15, -2.75, 2.15, 2.75)
    elif name == "Vishay_MMA0204_IPC_Reflow":
        add_smd_pad(fp, "1", -1.50, 0, 1.40, 1.55); add_smd_pad(fp, "2", 1.50, 0, 1.40, 1.55)
        add_outline(fp, -1.95, -0.85, 1.95, 0.85)
    elif name == "Panasonic_ERJ6_Reflow_Nominal":
        add_smd_pad(fp, "1", -1.175, 0, 1.15, 1.15); add_smd_pad(fp, "2", 1.175, 0, 1.15, 1.15)
        add_outline(fp, -1.80, -0.72, 1.80, 0.72)
    elif name == "TDK_CGA3_Reflow_Nominal":
        add_smd_pad(fp, "1", -0.70, 0, 0.70, 0.70); add_smd_pad(fp, "2", 0.70, 0, 0.70, 0.70)
        add_outline(fp, -1.12, -0.46, 1.12, 0.46)
    elif name == "Vishay_CRCW1210_Reflow":
        add_smd_pad(fp, "1", -1.40, 0, 1.10, 2.80, 0.15); add_smd_pad(fp, "2", 1.40, 0, 1.10, 2.80, 0.15)
        add_outline(fp, -2.00, -1.55, 2.00, 1.55)
    elif name == "Murata_GRM21_Reflow_Nominal":
        add_smd_pad(fp, "1", -1.025, 0, 0.95, 0.95); add_smd_pad(fp, "2", 1.025, 0, 0.95, 0.95)
        add_outline(fp, -1.55, -0.58, 1.55, 0.58)
    else:
        raise KeyError(name)
    fp.Reference().SetVisible(False); fp.Reference().SetLayer(pcbnew.F_SilkS)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I_MM(0.9, 0.9)); fp.Reference().SetTextThickness(pcbnew.FromMM(0.15))
    fp.Value().SetVisible(False)
    return fp


def create_library() -> None:
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    for stale in LIB_DIR.glob("*.kicad_mod"): stale.unlink()
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    for name in sorted(set(FOOTPRINTS.values())):
        io.FootprintSave(str(LIB_DIR), footprint(name))
    (ECAD / "fp-lib-table").write_text(f'(fp_lib_table\n  (version 7)\n  (lib (name "{LIB_NAME}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB_NAME}.pretty")(options "")(descr "R202 runtime observation carrier candidate footprints"))\n)\n', encoding="utf-8")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle: return list(csv.DictReader(handle))


def add_track(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, points: list[tuple[float, float]], layer: int, width: float = 0.25) -> None:
    for start, end in zip(points, points[1:]):
        if start == end: continue
        item = pcbnew.PCB_TRACK(board)
        item.SetStart(pcbnew.VECTOR2I_MM(*start)); item.SetEnd(pcbnew.VECTOR2I_MM(*end))
        item.SetWidth(pcbnew.FromMM(width)); item.SetLayer(layer); item.SetNet(net); board.Add(item)


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, point: tuple[float, float], diameter: float = 0.70, drill: float = 0.35) -> None:
    via = pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point))
    via.SetWidth(pcbnew.FromMM(diameter)); via.SetDrill(pcbnew.FromMM(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def add_zone(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, layer: int, outline: list[tuple[float, float]], priority: int = 0, clearance: float = 0.25) -> None:
    zone = pcbnew.ZONE(board); zone.SetLayer(layer); zone.SetNet(net); zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(pcbnew.FromMM(clearance)); polygon = zone.Outline(); polygon.NewOutline()
    for point in outline: polygon.Append(pcbnew.VECTOR2I_MM(*point))
    board.Add(zone)


def add_board_text(board: pcbnew.BOARD, value: str, x: float, y: float, size: float, layer: int = pcbnew.F_SilkS) -> None:
    item = pcbnew.PCB_TEXT(board); item.SetText(value); item.SetPosition(pcbnew.VECTOR2I_MM(x, y)); item.SetLayer(layer)
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); item.SetTextThickness(pcbnew.FromMM(max(0.15, size * 0.14))); board.Add(item)


def build_board() -> dict[str, object]:
    create_library()
    connector = rows(ECAD / "connector-schedule.csv")
    node_net = {(row["reference"], row["terminal"]): row["net"] for row in connector}
    board = pcbnew.BOARD(); board.SetCopperLayerCount(4)
    settings = board.GetDesignSettings(); settings.m_MinClearance = pcbnew.FromMM(0.20); settings.m_TrackMinWidth = pcbnew.FromMM(0.20)
    settings.m_HoleClearance = pcbnew.FromMM(0.25); settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.10)
    default = settings.m_NetSettings.GetDefaultNetclass(); default.SetClearance(pcbnew.FromMM(0.20)); default.SetTrackWidth(pcbnew.FromMM(0.25)); default.SetViaDiameter(pcbnew.FromMM(0.70)); default.SetViaDrill(pcbnew.FromMM(0.35))
    net_names = sorted({node_net[(ref, pin)] for ref in FOOTPRINTS for pin in {row["terminal"] for row in connector if row["reference"] == ref}})
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    for ref, name in FOOTPRINTS.items():
        fp = pcbnew.FootprintLoad(str(LIB_DIR), name); fp.SetReference(ref); fp.SetValue(name)
        x, y, rotation = PLACEMENTS[ref]; fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(rotation)
        for pad in fp.Pads(): pad.SetNet(nets[node_net[(ref, pad.GetNumber())]])
        board.Add(fp)
    hole_lib = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty")
    for index, point in enumerate(((4.5, 4.5), (115.5, 4.5), (4.5, 85.5), (115.5, 85.5)), start=1):
        fp = pcbnew.FootprintLoad(str(hole_lib), "MountingHole_3.2mm_M3"); fp.SetReference(f"MH{index}"); fp.SetValue("BOARD-ONLY M3; HARDWARE/ENCLOSURE SELECTION REQUIRED"); fp.SetPosition(pcbnew.VECTOR2I_MM(*point)); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); board.Add(fp)
    for start, end in ((((0, 0), (BOARD_W, 0))), (((BOARD_W, 0), (BOARD_W, BOARD_H))), (((BOARD_W, BOARD_H), (0, BOARD_H))), (((0, BOARD_H), (0, 0)))):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.25)); board.Add(edge)
    add_board_text(board, "HR-V0 OBS CARRIER PCB-P0.1 - ZERO SAFETY CREDIT", 28, 7.5, 1.1)
    add_board_text(board, "PRELIMINARY - DO NOT CONNECT OR ENERGIZE", 31, 84.5, 1.0)
    add_board_text(board, "FIELD 24 V", 9, 18, 1.0); add_board_text(board, "COMPUTE 3V3", 96, 18, 1.0)
    add_board_text(board, "ISOLATION CORRIDOR", 57.9, 74, 0.8)
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    def pad(ref: str, number: str) -> tuple[float, float]:
        found = [p for p in footprints[ref].Pads() if p.GetNumber() == number]
        if len(found) != 1: raise RuntimeError(f"pad lookup {ref}.{number}")
        position = found[0].GetPosition(); return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)
    def manhattan(net: str, a: tuple[float, float], b: tuple[float, float], xmid: float | None = None, layer: int = pcbnew.F_Cu, width: float = 0.25) -> None:
        middle = (xmid if xmid is not None else (a[0] + b[0]) / 2, a[1])
        add_track(board, nets[net], [a, middle, (middle[0], b[1]), b], layer, width)
    channels = [
        (1, "SR1", "JFIELD1", "1", "UOBS1", "15", "16", None, "4", "3"),
        (2, "SRA1", "JFIELD1", "2", "UOBS1", "11", "10", "RW2", "5", "4"),
        (3, "K1", "JFIELD1", "3", "UOBS2", "15", "16", "RW3", "4", "5"),
        (4, "K2", "JFIELD1", "4", "UOBS2", "11", "10", "RW4", "5", "6"),
    ]
    for index, name, jref, jpin, uref, inpin, sensepin, rwref, outpin, logicpin in channels:
        status, sense, input_net = f"{name}_STATUS", f"{name}_SENSE", f"{name}_IN"
        jpoint, rth1, rth2 = pad(jref, jpin), pad(f"RTH{index}", "1"), pad(f"RTH{index}", "2")
        # Preserve connector/channel ordering and approach both resistor lands on-axis.
        # The ordered status bundle is carried on B.Cu from the through-hole boundary
        # to a via centred in each RTH pad. This avoids necking past the adjacent pad.
        add_via(board, nets[status], rth1)
        add_track(board, nets[status], [jpoint, rth1], pcbnew.B_Cu)
        if rwref:
            rw1 = pad(rwref, "1")
            add_track(board, nets[status], [rth1, (18.5, rth1[1]), (18.5, rw1[1]), rw1], pcbnew.B_Cu)
            add_via(board, nets[status], rw1)
        rsn1, rsn2 = pad(f"RSN{index}", "1"), pad(f"RSN{index}", "2")
        sense_u, input_u = pad(uref, sensepin), pad(uref, inpin)
        add_track(board, nets[sense], [rth2, (31.0, rth2[1]), (31.0, rsn1[1]), rsn1], pcbnew.F_Cu)
        sense_y = rsn1[1] + (1.35 if index in (1, 3) else -1.35)
        add_track(board, nets[sense], [rsn1, (38.5, rsn1[1]), (38.5, sense_y), (54.6, sense_y), (54.6, sense_u[1]), sense_u], pcbnew.F_Cu)
        cfi1 = pad(f"CFI{index}", "1")
        add_track(board, nets[sense], [cfi1, (36.8, cfi1[1]), (36.8, sense_y), (38.5, sense_y)], pcbnew.F_Cu)
        # Carry each input on the bottom signal layer so adjacent sense/input lands cannot cross.
        input_via_a = (46.0, rsn2[1]); input_via_b = (52.0, input_u[1])
        add_track(board, nets[input_net], [rsn2, input_via_a], pcbnew.F_Cu); add_via(board, nets[input_net], input_via_a)
        add_track(board, nets[input_net], [input_via_a, input_via_b], pcbnew.B_Cu); add_via(board, nets[input_net], input_via_b)
        add_track(board, nets[input_net], [input_via_b, input_u], pcbnew.F_Cu)
        raw = f"OBS_{name}_RAW"; output = f"OBS_{name}_PI"
        raw_u, rso1 = pad(uref, outpin), pad(f"RSO{index}", "1")
        raw_via_a = (65.0 if index in (1, 3) else 64.5, raw_u[1])
        raw_via_b = (72.0, rso1[1])
        add_track(board, nets[raw], [raw_u, raw_via_a], pcbnew.F_Cu); add_via(board, nets[raw], raw_via_a, 0.60, 0.30)
        add_track(board, nets[raw], [raw_via_a, raw_via_b], pcbnew.B_Cu); add_via(board, nets[raw], raw_via_b)
        add_track(board, nets[raw], [raw_via_b, rso1], pcbnew.F_Cu)
        rso2, rpd1 = pad(f"RSO{index}", "2"), pad(f"RPD{index}", "1")
        branch = (80.5, rso2[1]); via_a = (90.0, rso2[1]); via_b = (106.0, pad("JLOGIC1", logicpin)[1])
        add_track(board, nets[output], [rso2, branch, via_a], pcbnew.F_Cu); add_via(board, nets[output], via_a)
        add_track(board, nets[output], [branch, (80.5, rpd1[1]), rpd1], pcbnew.F_Cu)
        add_track(board, nets[output], [via_a, via_b], pcbnew.B_Cu); add_via(board, nets[output], via_b)
        add_track(board, nets[output], [via_b, pad("JLOGIC1", logicpin)], pcbnew.F_Cu)
    add_zone(board, nets["SAFETY_0V"], pcbnew.In1_Cu, [(2, 2), (57.2, 2), (57.2, 88), (2, 88)])
    add_zone(board, nets["COMPUTE_0V"], pcbnew.In1_Cu, [(62.8, 2), (118, 2), (118, 88), (62.8, 88)])
    add_zone(board, nets["PI_3V3_CANDIDATE"], pcbnew.In2_Cu, [(62.8, 2), (118, 2), (118, 88), (62.8, 88)])
    plane_nodes = {
        "SAFETY_0V": [("JFIELD1", "5")] + [(f"CFI{i}", "2") for i in range(1, 5)] + [(rw, "2") for rw in ("RW2", "RW3", "RW4")] + [(u, p) for u in ("UOBS1", "UOBS2") for p in ("12", "14")],
        "COMPUTE_0V": [("JLOGIC1", "2")] + [(f"RPD{i}", "2") for i in range(1, 5)] + [(c, "2") for c in ("CDEC1", "CDEC2")] + [(u, p) for u in ("UOBS1", "UOBS2") for p in ("1", "8")],
        "PI_3V3_CANDIDATE": [("JLOGIC1", "1")] + [(c, "1") for c in ("CDEC1", "CDEC2")] + [(u, p) for u in ("UOBS1", "UOBS2") for p in ("2", "3")],
    }
    for net_name, nodes in plane_nodes.items():
        for ref, number in nodes:
            p = pad(ref, number)
            if ref.startswith("J") or ref.startswith("UOBS"): continue
            direction = -1.2 if net_name == "SAFETY_0V" else 1.2
            v = (p[0] + direction, p[1]); add_track(board, nets[net_name], [p, v], pcbnew.F_Cu, 0.30); add_via(board, nets[net_name], v)
    for uref in ("UOBS1", "UOBS2"):
        safety = [pad(uref, "12"), pad(uref, "14")]
        for point in safety:
            safety_via = (53.2, point[1])
            add_track(board, nets["SAFETY_0V"], [point, safety_via], pcbnew.F_Cu, 0.25)
            add_via(board, nets["SAFETY_0V"], safety_via, 0.60, 0.30)
        ground1, ground8 = pad(uref, "1"), pad(uref, "8")
        ground_via1, ground_via8 = (64.0, ground1[1] + 2.3), (64.0, ground8[1] - 2.3)
        add_track(board, nets["COMPUTE_0V"], [ground1, (63.5, ground1[1]), (63.5, ground_via1[1]), ground_via1], pcbnew.F_Cu, 0.25); add_via(board, nets["COMPUTE_0V"], ground_via1)
        add_track(board, nets["COMPUTE_0V"], [ground8, (63.5, ground8[1]), (63.5, ground_via8[1]), ground_via8], pcbnew.F_Cu, 0.25); add_via(board, nets["COMPUTE_0V"], ground_via8)
        supply2, supply3 = pad(uref, "2"), pad(uref, "3"); supply_via = (69.0, ground1[1] + 2.3)
        add_track(board, nets["PI_3V3_CANDIDATE"], [supply3, (67.2, supply3[1])], pcbnew.F_Cu, 0.25)
        add_track(board, nets["PI_3V3_CANDIDATE"], [supply2, (67.2, supply2[1]), (67.2, supply_via[1]), supply_via], pcbnew.F_Cu, 0.25)
        add_track(board, nets["PI_3V3_CANDIDATE"], [(67.2, supply3[1]), (67.2, supply2[1])], pcbnew.F_Cu, 0.25)
        add_via(board, nets["PI_3V3_CANDIDATE"], supply_via)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board_path = ECAD / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(board_path), board)
    placements = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        pos = fp.GetPosition(); placements.append({"reference": fp.GetReference(), "footprint": fp.GetFPID().GetLibItemName(), "x_mm": f"{pcbnew.ToMM(pos.x):.3f}", "y_mm": f"{pcbnew.ToMM(pos.y):.3f}", "rotation_deg": f"{fp.GetOrientationDegrees():.3f}", "side": "TOP", "state": "CANDIDATE - NOT RELEASED"})
    with (ECAD / "pcb-placement.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*placements[0], "warning"]); writer.writeheader(); writer.writerows([{**row, "warning": WARNING} for row in placements])
    return {"footprints": len(placements), "mounted_components": len(FOOTPRINTS), "mounting_holes": 4, "board_width_mm": BOARD_W, "board_height_mm": BOARD_H, "copper_layers": 4, "field_compute_corridor_mm": 5.6, "fabrication_authorized": False, "connection_authorized": False, "energization_authorized": False}


def run_native(summary: dict[str, object]) -> None:
    validation, output = ECAD / "validation", ECAD / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    (output / f"{PROJECT}-preliminary.pdf").unlink(missing_ok=True)
    board = ECAD / f"{PROJECT}.kicad_pcb"; cli = KICAD / "kicad-cli.exe"
    commands = [
        [str(cli), "pcb", "drc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(board)],
        [str(cli), "pcb", "export", "stats", "--output", str(validation / f"{PROJECT}-stats.txt"), str(board)],
        [str(cli), "pcb", "export", "svg", "--mode-single", "--layers", "F.Cu,F.Silkscreen,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", "--output", str(output / "runtime-observation-carrier-top.svg"), str(board)],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True); logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "pcb-kicad-cli.log").write_text("\n".join(logs), encoding="utf-8"); raise SystemExit(result.returncode)
    (validation / "pcb-kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    # KiCad's default pale silkscreen color is not legible on the white SVG
    # board field. Recolor the browser-only export to the controlled site
    # palette; this does not alter native board layers or fabrication data.
    browser_svg = output / "runtime-observation-carrier-top.svg"
    browser_svg_text = (
        browser_svg.read_text(encoding="utf-8")
        .replace("#C83434", "#0B4F8A")
        .replace("#F2EDA1", "#9A6500")
        .replace("#D0D2CD", "#082B55")
    )
    browser_svg.write_text("\n".join(line.rstrip() for line in browser_svg_text.splitlines()) + "\n", encoding="utf-8")
    board_obj = pcbnew.LoadBoard(str(board)); tracks = list(board_obj.GetTracks()); zones = list(board_obj.Zones())
    summary.update({"track_segments": sum(isinstance(item, pcbnew.PCB_TRACK) and not isinstance(item, pcbnew.PCB_VIA) for item in tracks), "vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in tracks), "zones": len(zones)})
    (validation / "pcb-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs_web(summary: dict[str, object]) -> None:
    DOC.write_text(f'''# HR-V0 runtime observation carrier {REV}

**{WARNING}**

R202 supersedes R201's compound 4+2 terminal candidate with exact six-position Phoenix Contact `MKDS 1/6-3,5`, item `1751280`, for both field and compute boundaries. It adds a native routed four-layer 120 x 90 mm PCB candidate while retaining the R201 receiver calculations and diagnostic-only boundary.

The PCB has {summary['mounted_components']} mounted component footprints plus four board-only M3 holes, separate `SAFETY_0V` and `COMPUTE_0V` zones on In1.Cu, a compute-side `PI_3V3_CANDIDATE` zone on In2.Cu, a 5.6 mm field/compute zone corridor and four isolated floating SUB lands. No signal trace crosses the field/compute corridor; only the two ISO1212 packages span the functional domain boundary.

Native ERC and DRC both report zero violations in the encoded candidate. That proves neither application safety nor manufacturability. Phoenix's 1.1 mm drill is manufacturer data; the 2.10 mm copper land is inherited project-controlled geometry and requires fabricator acceptance. Four layers, stackup, laminate, copper, solder mask, stencil, assembly process, mounting, enclosure and first article remain open.

The schematic still does not select Raspberry Pi GPIOs. The two six-position screw terminals terminate project-defined board positions only; exact wire, ferrules, labels, 5 mm strip length, 0.22-0.25 Nm torque application, strain relief and service routing require a released harness. No output may command, restore or preserve motion. All fourteen holds remain open and zero functional-safety credit is claimed.
''', encoding="utf-8")
    placement_rows = rows(ECAD / "pcb-placement.csv")
    placement_html = "".join(f"<tr><td>{html.escape(r['reference'])}</td><td>{html.escape(r['footprint'])}</td><td>{r['x_mm']}, {r['y_mm']}</td><td>{r['rotation_deg']}</td></tr>" for r in placement_rows)
    hold_html = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td></tr>" for a,b,c in HOLDS)
    WEB.mkdir(parents=True, exist_ok=True)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,4vw,3rem);background:var(--ink);color:white}}main{{max-width:1180px;margin:auto;padding:1rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.25rem)}}.warning{{background:var(--gold);color:#211700;border:3px solid #211700;padding:.8rem;font-weight:850}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}.metric{{background:white;border:2px solid var(--blue);border-radius:12px;padding:1rem}}.metric strong{{display:block;font-size:1.6rem}}.figure,.table{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:10px;margin:1rem 0}}.figure img{{display:block;min-width:900px;width:100%;height:auto}}table{{border-collapse:collapse;min-width:900px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #adc9df}}th{{background:var(--sky)}}small{{font-size:14px}}footer{{background:var(--ink);color:white;padding:1rem;margin-top:2rem}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - {DATE}</p><h1>The diagnostic receiver now has copper.</h1><p>A routed native PCB candidate with exact six-position screw terminals. It is still not a fabrication or connection release.</p></header><main><section class="metrics"><div class="metric"><strong>{summary['mounted_components']} + 4</strong>mounted parts plus board holes</div><div class="metric"><strong>{summary['track_segments']}</strong>routed track segments</div><div class="metric"><strong>{summary['vias']}</strong>through vias</div><div class="metric"><strong>ERC/DRC 0</strong>encoded source violations</div><div class="metric"><strong>14</strong>open evidence holds</div></section><h2>Top copper and legend</h2><p>The blue/gold presentation does not replace native KiCad. Field copper stays left, compute copper stays right, and only UOBS1/UOBS2 span the isolation corridor.</p><div class="figure"><img src="../../../electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/output/runtime-observation-carrier-top.svg" alt="Top copper, footprints and board outline for the preliminary runtime observation carrier"></div><h2>Physical placement</h2><div class="table"><table><thead><tr><th>Reference</th><th>Footprint</th><th>X, Y mm</th><th>Rotation</th></tr></thead><tbody>{placement_html}</tbody></table></div><h2>Fourteen holds remain open</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_html}</tbody></table></div></main><footer>{WARNING}. Diagnostic-only candidate; zero functional-safety credit.</footer></body></html>''', encoding="utf-8")


def manifest() -> None:
    target = ECAD / "SOURCE-MANIFEST.csv"; result = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path != target: result.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with target.open("w", newline="", encoding="utf-8") as handle: writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(result)


def main() -> int:
    create_library()
    base = load_base(); base.build_ecad()
    summary = build_board(); run_native(summary); write_docs_web(summary); manifest()
    print(f"{IDENTIFIER}: 5 native sheets / {summary['footprints']} footprints / {summary['track_segments']} tracks / {summary['vias']} vias")
    print("Native ERC 0/0 and DRC 0; 14 holds open; zero safety or work authority")
    print(WARNING)
    return 0


if __name__ == "__main__": raise SystemExit(main())
