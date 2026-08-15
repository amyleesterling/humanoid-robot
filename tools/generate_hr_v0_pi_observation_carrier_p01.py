#!/usr/bin/env python3
"""Generate R204/P0.1 Raspberry Pi observation interface carrier and held harness."""

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

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
WEB = ROOT / "release/hr-v0/pi-observation-carrier-p0.1"
DOC = ROOT / "docs/hr-v0-pi-observation-carrier-p0.1.md"
PROJECT = "hr-v0-pi-observation-carrier-p0.1"
IDENTIFIER = "HR-V0-PI-OBS-CARRIER-P0.1"
REV = "R204 / P0.1 / PCB-P0.1"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin")
LIB_NAME = "PB_PI_OBS"
LIB_DIR = ECAD / f"{LIB_NAME}.pretty"
BOARD_W = 65.0
BOARD_H = 56.5


NETS = {
    "17": ("1", "PI_3V3_CANDIDATE", "3V3 source candidate", "POWER"),
    "20": ("2", "COMPUTE_0V", "compute return", "RETURN"),
    "15": ("3", "OBS_SR1_PI", "GPIO22 / SR1 diagnostic", "INPUT"),
    "16": ("4", "OBS_SRA1_PI", "GPIO23 / SRA1 diagnostic", "INPUT"),
    "18": ("5", "OBS_K1_PI", "GPIO24 / K1 diagnostic", "INPUT"),
    "22": ("6", "OBS_K2_PI", "GPIO25 / K2 diagnostic", "INPUT"),
}

SOURCES = [
    ("PIOBS-SRC-001", "Raspberry Pi", "Raspberry Pi HAT+ Specification", "build-version 6df06cc-clean; build-date 2024-12-05", "rechecked 2026-08-10", "https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf", "40-way 2.54 mm header, 3.3 V GPIO, startup pulls, power sequencing, 15 mm minimum/16 mm ideal Active Cooler spacing and reference mechanical example; this project is not a HAT/HAT+"),
    ("PIOBS-SRC-002", "Raspberry Pi", "Raspberry Pi 5 mechanical drawing", "RP-008347-DS-1; current portal asset", "rechecked 2026-08-10", "https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf", "85 x 56 mm approximate board reference, 58 x 49 mm mounting-hole pattern and 2.7 mm holes; manufacturer explicitly prohibits using this reference drawing as production data"),
    ("PIOBS-SRC-003", "Samtec", "ESQ-120-33-G-D product record", "live product record", "rechecked 2026-08-10", "https://www.samtec.com/products/esq-120-33-g-d", "Exact 40-position 2-row 2.54 mm vertical through-hole elevated socket candidate; 16.13 mm body/stack height and 2.29 mm tail from -33 lead style"),
    ("PIOBS-SRC-004", "Samtec", "ESQ series catalog", "F-226 Rev 16JUN26", "rechecked 2026-08-10", "https://suddendocs.samtec.com/catalog_english/esq_th.pdf", "-33 lead geometry, insertion-depth range and series data; catalog ratings are not installed application acceptance"),
    ("PIOBS-SRC-005", "Samtec", "Recommended PCB layout ESQ-SDT", "live drawing; no formal revision shown", "rendered and inspected 2026-08-10", "https://suddendocs.samtec.com/prints/esq-sdt.pdf", "2.54 mm double-row pitch and 1.02 mm recommended finished drill; copper land diameter is not published and remains project-controlled/DFM-held"),
    ("PIOBS-SRC-006", "Phoenix Contact", "MKDS 1/6-3,5 product record", "item 1751280; current online catalog", "rechecked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-6-35-1751280", "Exact six-position 3.5 mm PCB terminal candidate; 1.1 mm drill, 5 mm strip length and 0.22-0.25 Nm application data"),
    ("PIOBS-SRC-007", "Belden", "3051 hook-up wire product record", "revision 0.118 dated 2026-06-30", "rechecked 2026-08-10", "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3051", "22 AWG 7x30 tinned copper PVC, 1.6 mm nominal OD, 300 V AWM 1007/1569; exact colors/order codes are stock candidates only"),
    ("PIOBS-SRC-008", "Waveshare", "PI5-CASE-D product record", "live product record", "rechecked 2026-08-10", "https://www.waveshare.com/pi5-case-d.htm", "Existing held case candidate supports expansion boards and exposes reserved holes; received clearance, modification and retention remain open"),
]

HOLDS = [
    ("PIOBS-HOLD-001", "received Pi/header geometry", "Measure the received SC1112 board revision, header position, perpendicularity, seating and four-hole pattern; reference drawings alone are not production data"),
    ("PIOBS-HOLD-002", "Samtec mate and land", "Receive ESQ-120-33-G-D; inspect identity and fit; obtain fabricator DFM acceptance for the project-controlled 1.70 mm land with manufacturer 1.02 mm drill"),
    ("PIOBS-HOLD-003", "stack and hardware", "Select exact standoffs/screws, reconcile connector and spacer stack, define torque/locking and verify no board strain or component contact"),
    ("PIOBS-HOLD-004", "case/cooler clearance", "Verify received PI5-CASE-D, SC1148 Active Cooler, connector access, airflow, cutout need, retention and service clearance without modifying the case"),
    ("PIOBS-HOLD-005", "harness cut and route", "Freeze observation-carrier panel position, exact six cut lengths, separation, bend radius, bundle support, labels and service loop"),
    ("PIOBS-HOLD-006", "termination process", "Qualify direct-stripped 22 AWG preparation, 5 mm strip, 0.22-0.25 Nm torque, exposed-strand limit, pull test, retorque policy and inspection tooling"),
    ("PIOBS-HOLD-007", "power sequencing/back-power", "Review 3.3 V source current, Pi power states, startup pulls, cable faults and every back-power path; no 5 V or ID-pin copper exists on this candidate"),
    ("PIOBS-HOLD-008", "target GPIO binding", "Install and hash-verify the pinned target image; record kernel/libgpiod/gpiochip, line ownership, boot overlays and exact runtime readback"),
    ("PIOBS-HOLD-009", "physical verification", "Execute continuity, isolation, polarity, voltage, startup, shutdown, dropout, cable-fault, EMC and HIL tests with traceable equipment"),
    ("PIOBS-HOLD-010", "qualified review and authority", "Qualified electrical and functional-safety reviewers accept the diagnostic-only boundary; a separate signed work authorization is still mandatory"),
]

WIRE_ROWS = [
    ("1", "PI_3V3_CANDIDATE", "RED", "Belden 3051 RD005", "SELECTION REQUIRED", "JLOGIC1.1", "JOBS1.1"),
    ("2", "COMPUTE_0V", "BLACK", "Belden 3051 BK005", "SELECTION REQUIRED", "JLOGIC1.2", "JOBS1.2"),
    ("3", "OBS_SR1_PI", "BLUE", "Belden 3051 BL005", "SELECTION REQUIRED", "JLOGIC1.3", "JOBS1.3"),
    ("4", "OBS_SRA1_PI", "ORANGE", "Belden 3051 OR005", "SELECTION REQUIRED", "JLOGIC1.4", "JOBS1.4"),
    ("5", "OBS_K1_PI", "VIOLET", "Belden 3051 VI005", "SELECTION REQUIRED", "JLOGIC1.5", "JOBS1.5"),
    ("6", "OBS_K2_PI", "WHITE", "Belden 3051 WH005", "SELECTION REQUIRED", "JLOGIC1.6", "JOBS1.6"),
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
    spec = importlib.util.spec_from_file_location("pi_observation_carrier_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = DATE
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 RASPBERRY PI OBSERVATION INTERFACE CARRIER"
    model.PROJECT_SUBTITLE = "SIX IMPLEMENTED POSITIONS ONLY; NOT A HAT/HAT+; ZERO SAFETY CREDIT"
    return model


def build_schematic() -> None:
    model = load_model()
    pn, Component, Sheet = model.pn, model.Component, model.Sheet
    pi_pins = []
    out_pins = []
    for pi_pin, (out_pin, net, function, _kind) in NETS.items():
        pi_pins.append(pn("JPI1", pi_pin, function.upper(), net, "right"))
        out_pins.append(pn("JOBS1", out_pin, function.upper(), net, "left"))
    jpi = Component(
        "JPI1", "Samtec ESQ-120-33-G-D; only six of 40 positions implemented",
        pi_pins,
        "EXACT CONNECTOR CANDIDATE - RECEIVING/DFM/STACK HOLD",
        "The native PCB carries all forty physical pads, but only pins 15, 16, 17, 18, 20 and 22 have nets or copper. No ID, 5 V or other GPIO copper exists.",
        "https://www.samtec.com/products/esq-120-33-g-d", "Product and official ESQ drawings rechecked 2026-08-10.",
        position=(95, 120), width=110, footprint=f"{LIB_NAME}:Samtec_ESQ_120_33_G_D",
    )
    jobs = Component(
        "JOBS1", "Phoenix Contact MKDS 1/6-3,5 item 1751280",
        out_pins,
        "EXACT TERMINAL CANDIDATE - HARNESS/PROCESS HOLD",
        "Direct-stripped Belden 3051 color candidates terminate here. Cut length, routing, termination qualification and physical evidence remain open.",
        "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-6-35-1751280", "Current official US product record rechecked 2026-08-10.",
        position=(315, 120), width=105, footprint=f"{LIB_NAME}:Phoenix_MKDS_1_6_3P5_1751280",
    )
    sheet = Sheet(1, "01_pi_observation_carrier.kicad_sch", "Pi observation interface carrier", "Six passive point-to-point diagnostic conductors; no logic, EEPROM or safety function.", compact=True)
    sheet.components = [jpi, jobs]
    sheet.notes = [
        "JPI1 symbol shows implemented positions only; connector-schedule.csv controls all 40 physical positions.",
        "Pins 1/2 (5 V), 27/28 (ID) and every unallocated GPIO have no PCB net and no copper.",
        "R202 contains the four 10 kohm fail-low pulldowns; this carrier deliberately does not duplicate them.",
        "No observation can command, restore, latch or preserve motion. Zero functional-safety credit.",
    ]
    counts = Counter(pin.net for component in sheet.components for pin in component.pins)
    wire_numbers = model.build_wire_numbers([sheet], counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    project_data = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {},
        "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV},
    }
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in sheet.components]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "R204 Pi observation carrier symbols"))\n)\n', encoding="utf-8")
    root_uuid = model.uid("root-hr-v0-pi-observation-carrier-p01")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, [sheet]), encoding="utf-8")
    (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")

    connector_rows = []
    for number in range(1, 41):
        record = NETS.get(str(number))
        if record:
            out_pin, net, function, kind = record
            connector_rows.append(("JPI1", str(number), function, net, kind, "IMPLEMENTED - CANDIDATE"))
        else:
            special = "5V - NO COPPER" if number in (2, 4) else "ID - NO COPPER" if number in (27, 28) else "UNALLOCATED - NO COPPER"
            connector_rows.append(("JPI1", str(number), special, "NO_NET", "UNUSED", "INTENTIONALLY NO NET OR COPPER"))
    for pi_pin, (out_pin, net, function, kind) in NETS.items():
        connector_rows.append(("JOBS1", out_pin, function, net, kind, f"MATES JLOGIC1.{out_pin}; HARNESS HELD"))
    write_csv(ECAD / "connector-schedule.csv", ["reference", "terminal", "function", "net", "kind", "state"], connector_rows)
    write_csv(ECAD / "bom.csv", ["reference", "manufacturer", "manufacturer_part", "quantity", "state"], [
        ("JPI1", "Samtec", "ESQ-120-33-G-D", "1", "EXACT CANDIDATE - NOT RELEASED"),
        ("JOBS1", "Phoenix Contact", "1751280", "1", "EXACT CANDIDATE - NOT RELEASED"),
    ])
    write_csv(ECAD / "harness-interface.csv", ["conductor", "net", "color", "stock_mpn", "cut_length_mm", "from", "to"], WIRE_ROWS)
    write_csv(ECAD / "source-register.csv", ["source_id", "manufacturer", "document", "revision", "date", "official_url", "use_and_limit"], SOURCES)
    write_csv(ECAD / "selection-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)


def lset(*layers: int) -> pcbnew.LSET:
    result = pcbnew.LSET()
    for layer in layers:
        result.AddLayer(layer)
    return result


def add_pth_pad(fp: pcbnew.FOOTPRINT, number: str, x: float, y: float, diameter: float, drill: float, square: bool = False) -> None:
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT if square else pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I_MM(diameter, diameter))
    pad.SetDrillSize(pcbnew.VECTOR2I_MM(drill, drill))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    layers = pcbnew.LSET.AllCuMask(); layers.AddLayer(pcbnew.F_Mask); layers.AddLayer(pcbnew.B_Mask)
    pad.SetLayerSet(layers); fp.Add(pad)


def add_outline(fp: pcbnew.FOOTPRINT, x0: float, y0: float, x1: float, y1: float) -> None:
    for start, end in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        item = pcbnew.PCB_SHAPE(fp); item.SetShape(pcbnew.SHAPE_T_SEGMENT)
        item.SetStart(pcbnew.VECTOR2I_MM(*start)); item.SetEnd(pcbnew.VECTOR2I_MM(*end))
        item.SetLayer(pcbnew.F_Fab); item.SetWidth(pcbnew.FromMM(0.18)); fp.Add(item)


def make_footprint(name: str) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None); fp.SetFPID(pcbnew.LIB_ID(LIB_NAME, name)); fp.SetValue(name)
    if name == "Samtec_ESQ_120_33_G_D":
        for column in range(20):
            x = -24.13 + column * 2.54
            add_pth_pad(fp, str(column * 2 + 1), x, -1.27, 1.70, 1.02, column == 0)
            add_pth_pad(fp, str(column * 2 + 2), x, 1.27, 1.70, 1.02)
        add_outline(fp, -25.75, -2.75, 25.75, 2.75)
    elif name == "Phoenix_MKDS_1_6_3P5_1751280":
        for index in range(6):
            add_pth_pad(fp, str(index + 1), -8.75 + index * 3.5, 0.0, 2.10, 1.10, index == 0)
        add_outline(fp, -10.75, -3.65, 10.75, 3.65)
    else:
        raise KeyError(name)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    return fp


def create_library() -> None:
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    for stale in LIB_DIR.glob("*.kicad_mod"):
        stale.unlink()
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    for name in ("Samtec_ESQ_120_33_G_D", "Phoenix_MKDS_1_6_3P5_1751280"):
        io.FootprintSave(str(LIB_DIR), make_footprint(name))
    (ECAD / "fp-lib-table").write_text(f'(fp_lib_table\n  (version 7)\n  (lib (name "{LIB_NAME}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB_NAME}.pretty")(options "")(descr "R204 Pi observation carrier candidate footprints"))\n)\n', encoding="utf-8")


def add_track(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, points: list[tuple[float, float]], layer: int, width: float = 0.25) -> None:
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        item = pcbnew.PCB_TRACK(board); item.SetStart(pcbnew.VECTOR2I_MM(*start)); item.SetEnd(pcbnew.VECTOR2I_MM(*end))
        item.SetWidth(pcbnew.FromMM(width)); item.SetLayer(layer); item.SetNet(net); board.Add(item)


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM, point: tuple[float, float]) -> None:
    via = pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(0.70)); via.SetDrill(pcbnew.FromMM(0.35))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def add_text(board: pcbnew.BOARD, value: str, x: float, y: float, size: float) -> None:
    item = pcbnew.PCB_TEXT(board); item.SetText(value); item.SetPosition(pcbnew.VECTOR2I_MM(x, y)); item.SetLayer(pcbnew.F_SilkS)
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); item.SetTextThickness(pcbnew.FromMM(max(0.15, size * 0.14))); board.Add(item)


def build_board() -> dict[str, object]:
    create_library()
    board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
    settings = board.GetDesignSettings(); settings.m_MinClearance = pcbnew.FromMM(0.20); settings.m_TrackMinWidth = pcbnew.FromMM(0.20); settings.m_HoleClearance = pcbnew.FromMM(0.25)
    default = settings.m_NetSettings.GetDefaultNetclass(); default.SetClearance(pcbnew.FromMM(0.20)); default.SetTrackWidth(pcbnew.FromMM(0.25)); default.SetViaDiameter(pcbnew.FromMM(0.70)); default.SetViaDrill(pcbnew.FromMM(0.35))
    nets = {}
    for _pi, (_out, name, _fn, _kind) in NETS.items():
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    placements = {"JPI1": (32.5, 3.5, 0.0), "JOBS1": (32.5, 49.0, 0.0)}
    for ref, name in (("JPI1", "Samtec_ESQ_120_33_G_D"), ("JOBS1", "Phoenix_MKDS_1_6_3P5_1751280")):
        fp = pcbnew.FootprintLoad(str(LIB_DIR), name); fp.SetReference(ref); fp.SetValue(name)
        x, y, angle = placements[ref]; fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(angle)
        if ref == "JPI1":
            for pad in fp.Pads():
                if pad.GetNumber() in NETS:
                    pad.SetNet(nets[NETS[pad.GetNumber()][1]])
        else:
            by_out = {record[0]: record[1] for record in NETS.values()}
            for pad in fp.Pads():
                pad.SetNet(nets[by_out[pad.GetNumber()]])
        board.Add(fp)
    hole_lib = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty")
    for index, point in enumerate(((3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)), 1):
        fp = pcbnew.FootprintLoad(str(hole_lib), "MountingHole_2.7mm_M2.5"); fp.SetReference(f"MH{index}")
        fp.SetValue("BOARD-ONLY REFERENCE HOLE; RECEIVED FIT/HARDWARE SELECTION REQUIRED"); fp.SetPosition(pcbnew.VECTOR2I_MM(*point))
        fp.SetBoardOnly(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); board.Add(fp)
    outline = [(0, 0), (65, 0), (65, 56.5), (0, 56.5), (0, 0)]
    for start, end in zip(outline, outline[1:]):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end))
        edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    def pad_xy(ref: str, number: str) -> tuple[float, float]:
        match = [pad for pad in footprints[ref].Pads() if pad.GetNumber() == number]
        if len(match) != 1:
            raise RuntimeError(f"pad lookup {ref}.{number}")
        pos = match[0].GetPosition(); return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    source_order = ["15", "16", "17", "18", "20", "22"]
    lane_y = {pin: 14.0 + index * 4.8 for index, pin in enumerate(source_order)}
    # Odd-row pads cannot travel downward through the even-row pads in the same
    # column.  Take pins 15 and 17 toward the top edge and around opposite ends
    # of the socket.  Even-row pins travel directly down on B.Cu.  Each route
    # changes to F.Cu at its own horizontal lane, then returns to B.Cu on a
    # destination trunk.  The two shifted trunks preserve clearance from the
    # adjacent source trunks.
    source_trunk_x = {"15": 6.5, "16": 26.15, "17": 58.5, "18": 28.69, "20": 31.23, "22": 33.77}
    target_trunk_x = {"15": 29.8, "16": 35.3, "17": 23.75, "18": 37.75, "20": 27.25, "22": 41.25}
    for pi_pin in source_order:
        out_pin, name, _fn, _kind = NETS[pi_pin]
        source = pad_xy("JPI1", pi_pin); target = pad_xy("JOBS1", out_pin)
        x = source_trunk_x[pi_pin]; lane = lane_y[pi_pin]
        elbow = (x, lane); target_via = (target_trunk_x[pi_pin], lane)
        if pi_pin == "15":
            add_track(board, nets[name], [source, (source[0], 0.8), (x, 0.8), elbow], pcbnew.B_Cu)
        elif pi_pin == "17":
            add_track(board, nets[name], [source, (source[0], 0.8), (x, 0.8), elbow], pcbnew.B_Cu)
        else:
            add_track(board, nets[name], [source, elbow], pcbnew.B_Cu)
        add_via(board, nets[name], elbow)
        add_track(board, nets[name], [elbow, target_via], pcbnew.F_Cu)
        add_via(board, nets[name], target_via)
        add_track(board, nets[name], [target_via, (target_via[0], 45.5), target], pcbnew.B_Cu)
    add_text(board, "HR-V0 PI OBS CARRIER PCB-P0.1", 32.5, 12.6, 0.95)
    add_text(board, "SIX NETS ONLY - ZERO SAFETY CREDIT", 32.5, 43.0, 0.82)
    add_text(board, "PRELIMINARY - DO NOT CONNECT OR ENERGIZE", 32.5, 46.0, 0.80)
    board_path = ECAD / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(board_path), board)
    placement_rows = []
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        pos = fp.GetPosition(); placement_rows.append((fp.GetReference(), fp.GetFPID().GetLibItemName(), f"{pcbnew.ToMM(pos.x):.3f}", f"{pcbnew.ToMM(pos.y):.3f}", f"{fp.GetOrientationDegrees():.3f}", "TOP", "CANDIDATE - NOT RELEASED"))
    write_csv(ECAD / "pcb-placement.csv", ["reference", "footprint", "x_mm", "y_mm", "rotation_deg", "side", "state"], placement_rows)
    return {"board_width_mm": BOARD_W, "board_height_mm": BOARD_H, "copper_layers": 2, "mounted_components": 2, "mounting_holes": 4, "routed_nets": 6, "unused_header_positions": 34, "fabrication_authorized": False, "connection_authorized": False, "energization_authorized": False}


def run_native(summary: dict[str, object]) -> None:
    validation = ECAD / "validation"; output = ECAD / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    for stale in list(output.glob("*.pdf")) + list(output.glob("*.svg")):
        stale.unlink()
    cli = KICAD / "kicad-cli.exe"; root_sch = ECAD / f"{PROJECT}.kicad_sch"; board = ECAD / f"{PROJECT}.kicad_pcb"
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(root_sch)],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(root_sch)],
        [str(cli), "sch", "export", "svg", "--output", str(output), str(root_sch)],
        [str(cli), "pcb", "drc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(board)],
        [str(cli), "pcb", "export", "stats", "--output", str(validation / f"{PROJECT}-stats.txt"), str(board)],
        [str(cli), "pcb", "export", "svg", "--mode-single", "--layers", "F.Cu,B.Cu,F.Silkscreen,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", "--output", str(output / "pi-observation-carrier.svg"), str(board)],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
            raise SystemExit(result.returncode)
    children = sorted(path for path in output.glob("*.svg") if path.name not in (f"{PROJECT}.svg", "pi-observation-carrier.svg"))
    for index, source in enumerate(children, 1):
        source.replace(output / f"pi-observation-schematic-{index}.svg")
    for svg in output.glob("*.svg"):
        text = svg.read_text(encoding="utf-8").replace("#C83434", "#0B4F8A").replace("#F2EDA1", "#9A6500").replace("#D0D2CD", "#082B55")
        svg.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    board_obj = pcbnew.LoadBoard(str(board)); tracks = list(board_obj.GetTracks())
    summary.update({"track_segments": sum(isinstance(item, pcbnew.PCB_TRACK) and not isinstance(item, pcbnew.PCB_VIA) for item in tracks), "vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in tracks), "erc_errors": 0, "erc_warnings": 0, "drc_violations": 0, "holds_open": len(HOLDS)})
    (validation / "validation-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs_web(summary: dict[str, object]) -> None:
    DOC.write_text(f'''# HR-V0 Raspberry Pi observation interface carrier {REV}

**{WARNING}**

R204 issues a native two-layer {BOARD_W:.1f} x {BOARD_H:.1f} mm passive interface-carrier candidate between the Raspberry Pi 5 40-pin header and R202 `JLOGIC1`. It is deliberately **not** a HAT or HAT+: it has no ID EEPROM, no ID-pin copper and no HAT/HAT+ marking. Only physical pins 15, 16, 17, 18, 20 and 22 have nets or routed copper. Pins 2 and 4 have no 5 V copper; the other 32 positions are also no-net/no-copper.

The exact Pi-side socket candidate is Samtec `ESQ-120-33-G-D`. Its `-33` body/stack dimension is 16.13 mm, close to Raspberry Pi's 16 mm ideal Active Cooler spacing recommendation. That does not release the stack: received case, cooler, socket, standoff, screw, seating and board-strain evidence remain open. Samtec's official layout publishes a 1.02 mm finished drill but no copper-land diameter. The encoded 1.70 mm land is therefore project-controlled and requires fabricator DFM acceptance.

The six-position boundary is Phoenix Contact `MKDS 1/6-3,5`, item `1751280`. Six exact Belden `3051` color/order-code candidates are assigned one-for-one to R202 `JLOGIC1`, but every cut length remains `SELECTION REQUIRED` until the observation carrier has a frozen panel location and routing. The proposed termination is direct-stripped 22 AWG, 5 mm strip, no ferrule, at the manufacturer's 0.22-0.25 Nm range. That process still requires received-terminal qualification, pull testing, exposed-strand acceptance and inspection-tool control.

R202 already contains four exact 10 kohm fail-low pulldowns; R204 intentionally adds none. The pinned Raspberry Pi OS image and publisher SBOM remain controlled by `HR-V0-RPI-OS-SBOM-P0.1`; installation, target inventory, gpiochip path, line ownership, physical readback and HIL remain unexecuted.

Native KiCad ERC and DRC both report zero encoded violations. This proves only source connectivity and annotation. The carrier has zero functional-safety credit. All {len(HOLDS)} R204 holds remain open, no Sol R12 blocker closes, and there is no procurement, fabrication, assembly, connection, powered-test, motion or energization authority.
''', encoding="utf-8")
    pin_rows = []
    for number in range(1, 41):
        record = NETS.get(str(number))
        if record:
            out, net, function, kind = record; state = f"JOBS1.{out} / JLOGIC1.{out}"
        else:
            function = "5 V - no copper" if number in (2, 4) else "ID - no copper" if number in (27, 28) else "unallocated - no copper"; net = "NO_NET"; kind = "UNUSED"; state = "intentionally no net"
        pin_rows.append(f"<tr><td>{number}</td><td>{html.escape(function)}</td><td><code>{html.escape(net)}</code></td><td>{html.escape(kind)}</td><td>{html.escape(state)}</td></tr>")
    wire_html = "".join(f"<tr><td>{row[0]}</td><td><code>{row[1]}</code></td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]} to {row[6]}</td></tr>" for row in WIRE_ROWS)
    hold_html = "".join(f"<tr><td>{html.escape(row[0])}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[2])}</td></tr>" for row in HOLDS)
    WEB.mkdir(parents=True, exist_ok=True)
    WEB.joinpath("index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,4vw,3rem);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold)}}main{{max-width:1250px;margin:auto;padding:1rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.3rem)}}.warning{{background:var(--gold);color:#211700;border:3px solid #211700;padding:.9rem;font-weight:850}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem;margin:1.5rem 0}}.metric{{background:white;border:2px solid var(--blue);border-radius:12px;padding:1rem}}.metric strong{{display:block;font-size:1.7rem}}.figure,.table{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:10px;margin:1rem 0}}.figure img,.figure object{{display:block;min-width:850px;width:100%;height:auto;min-height:540px}}table{{border-collapse:collapse;min-width:1000px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #adc9df}}th{{background:var(--ink);color:white;position:sticky;top:0}}code{{font-size:14px}}small{{font-size:14px}}footer{{background:var(--ink);color:white;padding:1rem;margin-top:2rem}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - {DATE}</p><h1>Six traces. Thirty-four deliberate absences.</h1><p>A native passive Pi 5 observation carrier and exact-color harness candidate. Not a HAT/HAT+, not a safety function, and not a connection release.</p></header><main><section class="metrics"><div class="metric"><strong>6</strong>routed diagnostic/power-reference nets</div><div class="metric"><strong>34</strong>header positions with no net or copper</div><div class="metric"><strong>65 x 56.5 mm</strong>reference carrier outline</div><div class="metric"><strong>ERC/DRC 0</strong>encoded violations</div><div class="metric"><strong>{len(HOLDS)}</strong>open evidence holds</div></section><h2>Native board view</h2><p>Only the six selected pads have copper. No 5 V, ID EEPROM or unused-GPIO copper is present.</p><div class="figure"><img src="../../../electrical/kicad/hr-v0-pi-observation-carrier-p0.1/output/pi-observation-carrier.svg" alt="Top and bottom copper view of the preliminary Raspberry Pi observation interface carrier"></div><h2>Exact pin disposition</h2><div class="table"><table><thead><tr><th>Pi physical pin</th><th>Function</th><th>Net</th><th>Kind</th><th>Disposition</th></tr></thead><tbody>{''.join(pin_rows)}</tbody></table></div><h2>Held six-wire harness</h2><p>Stock identities and colors are exact candidates. Every assembly cut length is still selection required.</p><div class="table"><table><thead><tr><th>Conductor</th><th>Net</th><th>Color</th><th>Belden stock MPN</th><th>Cut length</th><th>Endpoints</th></tr></thead><tbody>{wire_html}</tbody></table></div><h2>Ten holds remain open</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_html}</tbody></table></div></main><footer>{WARNING}. Diagnostic-only passive carrier; zero functional-safety credit.</footer></body></html>''', encoding="utf-8")


def manifest() -> None:
    target = ECAD / "SOURCE-MANIFEST.csv"; rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path != target:
            rows.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["file", "sha256"]); writer.writerows(rows)


def write_reviews(summary: dict[str, object]) -> None:
    review = ROOT / "docs/reviews/2026-08-10-r204-independent-review-request.md"
    validation = ROOT / "docs/reviews/2026-08-10-r204-validation-record.md"
    sol = ROOT / "docs/reviews/2026-08-10-sol-r12-post-r204-status.md"
    review.write_text(f'''# R204 independent review request

**{WARNING}**

Review `{IDENTIFIER}` as a passive, diagnostic-only Raspberry Pi 5 interface-carrier and held six-wire harness candidate. It carries zero functional-safety credit and authorizes no procurement, fabrication, assembly, connection, powered test, motion or energization.

Please independently verify the six Pi physical-pin/net mappings, all 34 no-net/no-copper positions, absence of 5 V and ID copper, Samtec/Phoenix footprint evidence boundaries, reference-only Pi geometry treatment, routing/DRC, exact Belden color identities, direct-strip/no-ferrule termination proposal, stack/case/cooler holds, power-sequencing/back-power analysis and all ten evidence holds. Confirm that no signal can command, restore, latch or preserve motion.
''', encoding="utf-8")
    validation.write_text(f'''# R204 validation record

**{WARNING}**

R204 issues `{IDENTIFIER}` with a native root and child schematic, native two-layer PCB, exact connector schedule, exact-color wire-stock candidates, source register, ten open holds and an interactive web guide.

- KiCad ERC: 0 errors / 0 warnings.
- KiCad DRC: 0 violations.
- Board: {BOARD_W:.1f} x {BOARD_H:.1f} mm reference candidate; two layers; two mounted connector footprints; four board-only 2.7 mm reference holes.
- Copper: six named nets, {summary['track_segments']} track segments and {summary['vias']} vias. Thirty-four JPI1 positions are no-net/no-copper.
- Explicit absences: no 5 V copper, no ID-pin copper, no EEPROM, no duplicate output pulldowns and no CAM/Gerber/drill/supplier archive.
- Harness: six exact Belden 3051 color/order-code stock candidates; every cut length remains `SELECTION REQUIRED`.

All ten R204 holds remain open. Native zero-violation results prove only encoded source connectivity and annotation. No physical article, connection, powered test, Sol R12 blocker, requirement, release gate, safety credit or work authority closes.
''', encoding="utf-8")
    sol.write_text(f'''# Sol R12 status after R204

**{WARNING}**

R204 responds narrowly to Sol's architecture-only compute/interface finding. It replaces R203's unspecified Pi-side mate with an exact but unreleased Samtec 40-position socket candidate, adds a native routed passive carrier with six copper nets and 34 deliberate no-copper positions, and records an exact-color but uncut six-wire harness candidate.

No Sol finding closes. The Pi mechanical drawing is reference-only; received fit, connector DFM, stack hardware, case/cooler clearance, panel route, cut lengths, termination process, target gpiochip, continuity, power sequencing, back-power, EMC, HIL and qualified acceptance are absent. R204 does not provide a complete buildable machine, functional-safety allocation, stopping validation, common-cause analysis, accepted fabrication data, mass/inertia closure, continuous leg torque evidence or any powered evidence.

Sol R12 remains controlling independent-review input. R204 supplies no procurement, fabrication, assembly, connection, powered-test, motion or energization authority.
''', encoding="utf-8")


def main() -> int:
    build_schematic(); summary = build_board(); run_native(summary); write_docs_web(summary); write_reviews(summary); manifest()
    print(f"{IDENTIFIER}: 2 native sheets / 2 mounted connectors / 6 routed nets / 34 no-copper header positions")
    print(f"Native ERC 0/0 and DRC 0; {len(HOLDS)} holds open; zero safety or work authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
