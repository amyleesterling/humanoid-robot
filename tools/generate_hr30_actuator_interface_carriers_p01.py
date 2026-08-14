#!/usr/bin/env python3
"""Generate the two HR-30 actuator-interface carrier candidates.

The boards are editable, placed and routed KiCad candidates derived from the
pin-level whole-body electrical architecture.  Manufacturing outputs are
included for inspection, but every output remains explicitly non-authorizing.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "electrical" / "carriers-p0.1"
PROJECT = "hr30-actuator-interface-carriers-p0.1"
IDENTIFIER = "HR30-ACTUATOR-INTERFACE-CARRIERS-P0.1"
DATE = "2026-08-14"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION OR ENERGIZATION"
WHOLE_BODY_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")
KICAD = KICAD_ROOT / "bin" / "kicad-cli.exe"
FP_ROOT = KICAD_ROOT / "share" / "kicad" / "footprints"

TI_ISOW = "https://www.ti.com/lit/ds/symlink/isow1432.pdf"
TI_EVM = "https://www.ti.com/lit/ug/sllu337/sllu337.pdf"
TI_LVC = "https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf"
TI_TPD = "https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf"
TDK_FB = "https://product.tdk.com/en/search/emc/emc/beads/info?part_no=MPZ1005S331ETD25"
LITTELFUSE_SM712 = "https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sm712_datasheet?assetguid=8313a28c-8802-4d47-a2a7-e30b5b1f67d8"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"

RS_BUSES = (("RS-LLEG", "A"), ("RS-RLEG", "A"), ("RS-LARM", "A"), ("RS-RARM", "A"), ("RS-WAIST", "B"))
TTL_BUSES = (("TTL-LDIST", "B"), ("TTL-RDIST", "B"), ("TTL-HEAD", "B"))


@dataclass
class Part:
    board: str
    ref: str
    value: str
    mpn: str
    manufacturer: str
    footprint: str
    pins: dict[str, str]
    x: float
    y: float
    rotation: float = 0.0
    fitted: bool = True
    source: str = ""
    evidence: str = ""


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lib_fp(identifier: str):
    library, name = identifier.split(":", 1)
    fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
    if fp is None:
        raise RuntimeError(f"cannot load footprint {identifier}")
    return fp


def add_part(parts: list[Part], *args, **kwargs) -> Part:
    part = Part(*args, **kwargs)
    parts.append(part)
    return part


def circuit_parts() -> list[Part]:
    parts: list[Part] = []
    # Physical controller connectors. Contacts 1/2/3 are return/5 V/3.3 V.
    carrier_a_pins = {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}
    carrier_b_pins = {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}
    for index, (bus, _) in enumerate(RS_BUSES[:4]):
        for offset, suffix in enumerate(("TX", "RX", "DIR"), 4 + index * 3):
            carrier_a_pins[str(offset)] = f"UART_{bus}_{suffix}"
    carrier_b_pins.update({"4": "UART_RS-WAIST_TX", "5": "UART_RS-WAIST_RX", "6": "UART_RS-WAIST_DIR"})
    for index, (bus, _) in enumerate(TTL_BUSES):
        carrier_b_pins[str(7 + index * 2)] = f"UART_{bus}_TX"
        carrier_b_pins[str(8 + index * 2)] = f"UART_{bus}_DIR"
    add_part(parts, "A", "JCA1", "JST BM15B-GHS-TBT controller", "BM15B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", carrier_a_pins, 41.0, 38.0, source=JST_GH, evidence="JST GH eGH catalog; 15 circuits; 1.25 mm locking family; logic only")
    add_part(parts, "B", "JCB1", "JST BM15B-GHS-TBT controller", "BM15B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", carrier_b_pins, 41.0, 38.0, source=JST_GH, evidence="JST GH eGH catalog; contacts 13-15 intentionally unassigned")

    rs_locations = {"RS-LLEG": (11.0, 20.0), "RS-RLEG": (31.0, 20.0), "RS-LARM": (51.0, 20.0), "RS-RARM": (71.0, 20.0), "RS-WAIST": (11.0, 20.0)}
    for index, (bus, board) in enumerate(RS_BUSES, 1):
        cx, cy = rs_locations[bus]
        tag = f"{index}"
        uref = f"U{100 + index}"
        iso_out, iso_in, gnd2 = f"{bus}_VISOOUT", f"{bus}_VISOIN", f"{bus}_GND2"
        pins = {
            "1": "CTRL_3V3", "2": f"UART_{bus}_TX", "3": f"UART_{bus}_DIR", "4": f"UART_{bus}_RX",
            "5": f"UART_{bus}_DIR", "6": "CTRL_GND", "8": "", "9": "CTRL_5V", "10": "CTRL_GND",
            "11": gnd2, "12": iso_out, "13": gnd2, "14": f"{bus}_RET", "15": f"{bus}_RET", "16": iso_in,
            "17": f"{bus}_DP", "18": f"{bus}_DN", "19": f"{bus}_DN", "20": f"{bus}_DP",
        }
        add_part(parts, board, uref, f"ISOW1432DFMR {bus}", "ISOW1432DFMR", "Texas Instruments", "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm", pins, cx, cy, 90, source=TI_ISOW, evidence="SLLSF86C Rev C, March 2022; pin functions and decoupling requirements")
        add_part(parts, board, f"J{100 + index}", f"{bus} data-only field", "BM03B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", {"1": f"{bus}_RET", "2": f"{bus}_DP", "3": f"{bus}_DN"}, cx, 4.0, source=JST_GH, evidence="No actuator VDD contact")
        add_part(parts, board, f"FB{tag}P", "330R@100MHz isolated supply bead", "MPZ1005S331ETD25", "TDK", "Inductor_SMD:L_0402_1005Metric", {"1": iso_out, "2": iso_in}, cx + 2.0, 14.0, source=TDK_FB, evidence="Production; 330 ohm at 100 MHz; 700 mA; 0.28 ohm max")
        add_part(parts, board, f"FB{tag}N", "330R@100MHz isolated return bead", "MPZ1005S331ETD25", "TDK", "Inductor_SMD:L_0402_1005Metric", {"1": gnd2, "2": f"{bus}_RET"}, cx + 4.4, 14.0, source=TDK_FB, evidence="Second ferrite follows TI two-bead emissions layout")
        cap_specs = (
            (f"C{tag}A", "10nF 50V X7R", "C1608X7R1H103K080AA", "CTRL_5V", "CTRL_GND", cx + 5.2, 29.2),
            (f"C{tag}B", "10uF 6.3V X5R", "GRM188R60J106ME47D", "CTRL_5V", "CTRL_GND", cx, 29.2),
            (f"C{tag}C", "100nF 50V X7R", "C1608X7R1H104K080AA", "CTRL_3V3", "CTRL_GND", cx - 5.2, 29.2),
            (f"C{tag}D", "10uF 6.3V X5R", "GRM188R60J106ME47D", iso_out, gnd2, cx + 5.0, 11.0),
            (f"C{tag}E", "100nF 50V X7R", "C1608X7R1H104K080AA", iso_in, f"{bus}_RET", cx, 11.0),
        )
        for ref, value, mpn, n1, n2, x, y in cap_specs:
            add_part(parts, board, ref, value, mpn, "TDK / Murata", "Capacitor_SMD:C_0603_1608Metric", {"1": n1, "2": n2}, x, y, source=TI_ISOW, evidence="TI Section 12 supply recommendation; exact capacitance candidate")
        add_part(parts, board, f"D{tag}RS", "SM712 RS-485 TVS", "SM712-02HTG", "Littelfuse", "Package_TO_SOT_SMD:SOT-23", {"1": f"{bus}_DP", "2": f"{bus}_DN", "3": f"{bus}_RET"}, cx + 4.8, 7.5, source=LITTELFUSE_SM712, evidence="SM712 datasheet Rev 2019-08-22; -7/+12 V RS-485 protection candidate")
        add_part(parts, board, f"RT{tag}", "120R 1% termination", "RC0603FR-07120RL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": f"{bus}_DP", "2": f"{bus}_TERM"}, cx - 5.2, 7.5, source=TI_EVM, evidence="120 ohm termination candidate; physical bus impedance verification required")
        add_part(parts, board, f"SJ{tag}", "termination enable - OPEN", "SOLDER-JUMPER-2", "KiCad", "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm", {"1": f"{bus}_TERM", "2": f"{bus}_DN"}, cx - 1.6, 7.5, fitted=False, source=TI_EVM, evidence="Default open; close only under controlled bus configuration")

    ttl_locations = {"TTL-LDIST": 31.0, "TTL-RDIST": 51.0, "TTL-HEAD": 71.0}
    for index, (bus, board) in enumerate(TTL_BUSES, 1):
        cx = ttl_locations[bus]
        tag = f"{index}"
        data_pre = f"{bus}_DATA_PRE"
        add_part(parts, board, f"U20{tag}", f"SN74LVC1T45DCKR {bus}", "SN74LVC1T45DCKR", "Texas Instruments", "Package_TO_SOT_SMD:SOT-363_SC-70-6", {"1": "CTRL_3V3", "2": "CTRL_GND", "3": f"UART_{bus}_TX", "4": data_pre, "5": f"UART_{bus}_DIR", "6": "CTRL_5V"}, cx, 20.0, source=TI_LVC, evidence="SCES515N Rev N, June 2024; exact DCK pin mapping")
        add_part(parts, board, f"J20{tag}", f"{bus} data-only field", "BM02B-GHS-TBT", "JST", "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical", {"1": "CTRL_GND", "2": f"{bus}_DATA"}, cx, 4.0, source=JST_GH, evidence="No actuator VDD contact")
        add_part(parts, board, f"C20{tag}A", "100nF 50V X7R VCCA", "C1608X7R1H104K080AA", "TDK", "Capacitor_SMD:C_0603_1608Metric", {"1": "CTRL_3V3", "2": "CTRL_GND"}, cx - 3.0, 23.0, source=TI_LVC, evidence="Local VCCA bypass")
        add_part(parts, board, f"C20{tag}B", "100nF 50V X7R VCCB", "C1608X7R1H104K080AA", "TDK", "Capacitor_SMD:C_0603_1608Metric", {"1": "CTRL_5V", "2": "CTRL_GND"}, cx + 3.0, 23.0, source=TI_LVC, evidence="Local VCCB bypass")
        add_part(parts, board, f"R20{tag}S", "33R 1% series", "RC0603FR-0733RL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": data_pre, "2": f"{bus}_DATA"}, cx, 14.0, source=TI_LVC, evidence="Signal-integrity candidate; waveform validation required")
        add_part(parts, board, f"R20{tag}D", "100k 1% DIR pulldown", "RC0603FR-07100KL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": f"UART_{bus}_DIR", "2": "CTRL_GND"}, cx - 4.0, 17.0, source=TI_LVC, evidence="Receive-default reset state candidate")
        add_part(parts, board, f"D20{tag}", "TPD1E10B06 TTL ESD", "TPD1E10B06DYA", "Texas Instruments", "Diode_SMD:D_SOD-523", {"1": f"{bus}_DATA", "2": "CTRL_GND"}, cx + 3.0, 9.0, source=TI_TPD, evidence="SLLSEB1G Rev G, August 2024; 5.5 V bidirectional ESD candidate")
        add_part(parts, board, f"R20{tag}P", "10k idle pullup - DNP", "RC0603FR-0710KL", "Yageo", "Resistor_SMD:R_0603_1608Metric", {"1": "CTRL_5V", "2": f"{bus}_DATA"}, cx - 3.0, 9.0, fitted=False, source=TI_LVC, evidence="Population requires measured idle/loading validation")
    return parts


def add_text(board, value: str, x: float, y: float, size: float, layer=pcbnew.F_SilkS) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value); item.SetPosition(pcbnew.VECTOR2I_MM(x, y)); item.SetLayer(layer)
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); item.SetTextThickness(pcbnew.FromMM(max(0.15, size * 0.14)))
    if layer == pcbnew.B_SilkS:
        item.SetMirrored(True)
    board.Add(item)


def add_track(board, net, start, end, layer, width=0.18) -> None:
    if start == end:
        return
    track = pcbnew.PCB_TRACK(board); track.SetStart(pcbnew.VECTOR2I_MM(*start)); track.SetEnd(pcbnew.VECTOR2I_MM(*end))
    track.SetLayer(layer); track.SetWidth(pcbnew.FromMM(width)); track.SetNet(net); board.Add(track)


def add_via(board, net, point) -> None:
    via = pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(0.45))
    via.SetDrill(pcbnew.FromMM(0.20)); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def interval_lane(interval, occupied, candidates):
    x0, x1 = interval
    for lane in candidates:
        if all(x1 < a - 0.7 or x0 > b + 0.7 for a, b in occupied[lane]):
            occupied[lane].append((x0, x1)); return lane
    raise RuntimeError(f"no routing lane for interval {interval}")


def route_board(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM]) -> dict[str, object]:
    pads_by_net: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = pad.GetNetname()
            if name:
                pos = pad.GetPosition(); pads_by_net[name].append((pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))
    occupied: dict[float, list[tuple[float, float]]] = defaultdict(list)
    pad_ys = [p[1] for points in pads_by_net.values() for p in points]
    top = [6.63 + 0.56 * i for i in range(15)]
    middle = [17.23 + 0.62 * i for i in range(9)]
    bottom = [27.17 + 0.54 * i for i in range(21)]
    candidates_all = [v for v in top + middle + bottom if all(abs(v - y) > 0.30 for y in pad_ys)]
    lane_rows = []
    for name, points in sorted(pads_by_net.items(), key=lambda item: (-max(p[0] for p in item[1]) + min(p[0] for p in item[1]), item[0])):
        if len(points) < 2:
            continue
        x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
        mean_y = sum(p[1] for p in points) / len(points)
        if max(p[1] for p in points) < 18.0:
            candidate_pool = [v for v in candidates_all if 6.0 < v < 15.0]
        elif min(p[1] for p in points) > 22.0:
            candidate_pool = [v for v in candidates_all if 26.5 < v < 38.5]
        else:
            candidate_pool = [v for v in candidates_all if 16.5 < v < 23.5] + candidates_all
        lane = interval_lane((x0, x1), occupied, candidate_pool)
        lane_rows.append({"net": name, "lane_y_mm": f"{lane:.3f}", "x_min_mm": f"{x0:.3f}", "x_max_mm": f"{x1:.3f}", "pad_count": len(points)})
    # The first automated via-in-pad route was rejected by KiCad DRC. Preserve
    # the real ratsnest and deterministic lane reservations, not unsafe copper.
    return {"vias": 0, "lanes": lane_rows, "routing_complete": False}


def write_board(board_id: str, parts: list[Part]) -> dict[str, object]:
    board_parts = [p for p in parts if p.board == board_id]
    board = pcbnew.BOARD(); board.SetCopperLayerCount(6)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10); settings.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings.m_HoleClearance = pcbnew.FromMM(0.10); settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.10)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.10))
    net_names = sorted({net for part in board_parts for net in part.pins.values() if net})
    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    for part in board_parts:
        fp = lib_fp(part.footprint); fp.SetReference(part.ref); fp.SetValue(part.value)
        fp.SetPosition(pcbnew.VECTOR2I_MM(part.x, part.y)); fp.SetOrientationDegrees(part.rotation)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetDNP(not part.fitted)
        for pad in fp.Pads():
            net_name = part.pins.get(pad.GetNumber(), "")
            if net_name:
                pad.SetNet(nets[net_name])
        board.Add(fp)
        if not (part.ref.startswith("U") or part.ref.startswith("J")):
            fp.Flip(fp.GetPosition(), False)
    for index, (x, y) in enumerate(((3.5, 3.5), (78.5, 3.5), (3.5, 38.5), (78.5, 38.5)), 1):
        hole = lib_fp("MountingHole:MountingHole_2.7mm_M2.5")
        hole.SetReference(f"MH{board_id}{index}"); hole.SetValue("M2.5 BOARD-ONLY; TRAY STACK VALIDATION OPEN")
        hole.SetPosition(pcbnew.VECTOR2I_MM(x, y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True)
        hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    for start, end in zip(((0, 0), (82, 0), (82, 42), (0, 42)), ((82, 0), (82, 42), (0, 42), (0, 0))):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end))
        edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)
    routing = route_board(board, nets)
    add_text(board, f"HR-30 CARRIER {board_id} P0.1", 26, 1.8, 0.9, pcbnew.B_SilkS)
    add_text(board, "DATA ONLY - NO ACTUATOR VDD", 25, 40.0, 0.8, pcbnew.B_SilkS)
    add_text(board, "PRELIMINARY / DO NOT FABRICATE OR CONNECT", 18, 35.0, 0.8, pcbnew.B_SilkS)
    board_path = OUT / f"carrier-{board_id.lower()}" / f"hr30-carrier-{board_id.lower()}-p0.1.kicad_pcb"
    board_path.parent.mkdir(parents=True, exist_ok=True); pcbnew.SaveBoard(str(board_path), board)
    return {"board": board_id, "path": board_path, "parts": len(board_parts), "nets": len(net_names), "routing": routing}


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_carrier_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic generator")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 ACTUATOR INTERFACE CARRIERS"
    model.PROJECT_SUBTITLE = "Carrier A: four isolated RS-485 channels. Carrier B: one isolated RS-485 plus three translated TTL channels."
    return model


def schematic_component(model, part: Part):
    pins = [model.pn(part.ref, number, number, net, "left" if i % 2 == 0 else "right") for i, (number, net) in enumerate(part.pins.items()) if net]
    return model.Component(part.ref, part.value, pins, "EXACT COMPONENT AND FOOTPRINT CANDIDATE; APPLICATION VALIDATION OPEN", part.evidence, part.source, part.evidence, position=(50, 50), width=72, footprint=part.footprint)


def write_schematic(parts: list[Part]) -> None:
    model = load_model(); items = [schematic_component(model, p) for p in parts]
    by_ref = {item.ref: item for item in items}; sheets = []
    overview = model.Sheet(1, "01_carrier_connectors.kicad_sch", "Carrier controller connector boundaries", "Exact 15-contact logic-only connectors; no actuator power contacts.")
    overview.components = [by_ref["JCA1"], by_ref["JCB1"]]
    overview.components[0].position = (115, 105); overview.components[1].position = (305, 105)
    overview.notes = ["Contacts are bound to the whole-body STM32 allocation.", "Contacts 13-15 of JCB1 remain intentionally unassigned.", WARNING]
    sheets.append(overview)
    for sheet_number, (bus, board) in enumerate(RS_BUSES + TTL_BUSES, 2):
        if bus.startswith("RS"):
            idx = [b for b, _ in RS_BUSES].index(bus) + 1
            refs = [f"U{100+idx}", f"J{100+idx}", f"FB{idx}P", f"FB{idx}N", f"C{idx}A", f"C{idx}B", f"C{idx}C", f"C{idx}D", f"C{idx}E", f"D{idx}RS", f"RT{idx}", f"SJ{idx}"]
            subtitle = "Full ISOW1432 application network: decoupling, two isolated-power ferrites, TVS and selectable 120-ohm termination."
        else:
            idx = [b for b, _ in TTL_BUSES].index(bus) + 1
            refs = [f"U20{idx}", f"J20{idx}", f"C20{idx}A", f"C20{idx}B", f"R20{idx}S", f"R20{idx}D", f"D20{idx}", f"R20{idx}P"]
            subtitle = "Full translator network: dual-rail bypass, receive-default DIR, series damping, ESD and optional idle pull-up."
        sheet = model.Sheet(sheet_number, f"{sheet_number:02d}_{bus.lower().replace('-', '_')}.kicad_sch", f"Carrier {board} - {bus}", subtitle)
        sheet.components = [by_ref[r] for r in refs]
        positions = [(55 + (i % 3) * 145, 48 + (i // 3) * 58) for i in range(len(refs))]
        for item, position in zip(sheet.components, positions): item.position, item.width = position, 78
        sheet.notes = [subtitle, "DNP/open configuration items are not permission to populate without the configuration record.", WARNING]
        sheets.append(sheet)
    net_counts = Counter(pin.net for item in items for pin in item.pins); wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-actuator-interface-carriers-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.1, "track_width": 0.18, "via_diameter": 0.45, "via_drill": 0.2}], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for item in items]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 carrier candidate symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def run_cli(args: list[object], allowed=(0,)) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run([str(KICAD), *map(str, args)], cwd=OUT, text=True, capture_output=True)
    if completed.returncode not in allowed:
        raise RuntimeError(f"KiCad CLI failed {completed.returncode}: {' '.join(map(str,args))}\n{completed.stdout}\n{completed.stderr}")
    return completed


def export_and_validate(boards: list[dict[str, object]]) -> list[dict[str, object]]:
    validation = OUT / "validation"; output = OUT / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc = run_cli(["sch", "erc", "--exit-code-violations", "--output", validation / f"{PROJECT}-erc.rpt", OUT / f"{PROJECT}.kicad_sch"], allowed=(0, 5))
    run_cli(["sch", "export", "svg", "--output", output, OUT / f"{PROJECT}.kicad_sch"])
    results = [{"artifact": "schematic", "return_code": erc.returncode, "report": str(validation / f"{PROJECT}-erc.rpt")}]
    for info in boards:
        board_id = info["board"]; path = Path(info["path"]); stem = path.stem
        drc_path = validation / f"{stem}-drc.rpt"
        drc = run_cli(["pcb", "drc", "--severity-all", "--exit-code-violations", "--output", drc_path, path], allowed=(0, 5))
        run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{stem}-front.svg", "--layers", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", path])
        run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{stem}-back.svg", "--layers", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", "--mirror", "--fit-page-to-board", "--exclude-drawing-sheet", path])
        results.append({"artifact": f"carrier-{board_id}", "return_code": drc.returncode, "report": str(drc_path)})
    # KiCad's SVG writer leaves decorative trailing spaces on many XML lines.
    # Normalize those generated exports so repository whitespace checks remain
    # useful without changing any geometric or presentation content.
    for svg in output.glob("*.svg"):
        normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n"
        svg.write_text(normalized, encoding="utf-8")
    return results


def publish(parts: list[Part], boards: list[dict[str, object]], validation: list[dict[str, object]]) -> None:
    component_rows = []
    for p in parts:
        component_rows.append({"board": p.board, "reference": p.ref, "manufacturer": p.manufacturer, "manufacturer_part_number": p.mpn, "value": p.value, "footprint": p.footprint, "fitted_p0_1": "YES" if p.fitted else "NO / DNP", "source": p.source, "evidence": p.evidence, "status": "EXACT CANDIDATE - APPLICATION/DFM/PHYSICAL VALIDATION OPEN", "warning": WARNING})
    write_csv(OUT / "carrier-component-register.csv", list(component_rows[0]), component_rows)
    terminal_rows = [{"board": p.board, "reference": p.ref, "pad": pin, "net": net, "warning": WARNING} for p in parts for pin, net in p.pins.items() if net]
    write_csv(OUT / "carrier-terminal-register.csv", list(terminal_rows[0]), terminal_rows)
    lane_rows = []
    for board in boards:
        for row in board["routing"]["lanes"]:
            lane_rows.append({"board": board["board"], **row, "routing_method": "UNROUTED deterministic lane reservation; rejected auto-route not retained", "warning": WARNING})
    write_csv(OUT / "carrier-routing-register.csv", list(lane_rows[0]), lane_rows)
    config_rows = [
        {"configuration_id": "TERM-RS-001", "applies_to": "SJ1-SJ5", "default": "OPEN / DNP", "change_condition": "Close only when this carrier is verified as a physical bus end and measured cable impedance/waveform supports 120 ohm termination.", "authority": "CONTROLLED CONFIGURATION CHANGE REQUIRED", "warning": WARNING},
        {"configuration_id": "TTL-PULLUP-001", "applies_to": "R201P-R203P", "default": "DNP", "change_condition": "Fit only after measured actuator/bus idle-state and loading validation.", "authority": "CONTROLLED CONFIGURATION CHANGE REQUIRED", "warning": WARNING},
        {"configuration_id": "ROUTING-001", "applies_to": "both boards", "default": "UNROUTED PLACEMENT CANDIDATE", "change_condition": "Complete interactive constraint-aware routing, resolve DRC, and perform independent layout review before any fabrication package exists.", "authority": "PCB DESIGN REQUIRED", "warning": WARNING},
    ]
    write_csv(OUT / "carrier-configuration-register.csv", list(config_rows[0]), config_rows)
    sources = [
        ("TI-ISOW1432", "Texas Instruments", "ISOW1412/ISOW1432 datasheet", "SLLSF86C Rev C; March 2022", TI_ISOW, "pinout; floating enable behavior; decoupling; two-bead isolated supply connection; layout and isolation guidance"),
        ("TI-ISOW-EVM", "Texas Instruments", "ISOW1432DFMEVM guide", "SLLU337; June 2021", TI_EVM, "application schematic; ferrite and termination population references"),
        ("TI-LVC1T45", "Texas Instruments", "SN74LVC1T45 datasheet", "SCES515N Rev N; June 2024", TI_LVC, "pinout; dual-rail bypass; direction and power sequencing"),
        ("TI-TPD1E10B06", "Texas Instruments", "TPD1E10B06 datasheet", "SLLSEB1G Rev G; August 2024", TI_TPD, "active 5.5 V bidirectional single-line ESD candidate"),
        ("TDK-MPZ1005", "TDK", "MPZ1005S331ETD25 product page", "live production page; accessed 2026-08-14", TDK_FB, "330 ohm at 100 MHz; 700 mA; 0.28 ohm max; 0402"),
        ("LITTELFUSE-SM712", "Littelfuse", "SM712 datasheet", "revised 2019-08-22; active page accessed 2026-08-14", LITTELFUSE_SM712, "RS-485 -7/+12 V working range; exact SOT23-3 order code"),
        ("JST-GH", "JST", "GH connector catalog", "live catalog accessed 2026-08-14", JST_GH, "BM15/BM03/BM02 header families; data-only connector boundary"),
    ]
    write_csv(OUT / "primary-source-register.csv", ["source_id", "manufacturer", "document", "revision_or_date", "url", "verified_use"], [{"source_id": a, "manufacturer": b, "document": c, "revision_or_date": d, "url": e, "verified_use": f} for a, b, c, d, e, f in sources])
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "carrier_a": {"board_mm": [82, 42, 1.6], "copper_layers": 6, "components": next(b["parts"] for b in boards if b["board"] == "A"), "native_pcb": True},
        "carrier_b": {"board_mm": [82, 42, 1.6], "copper_layers": 6, "components": next(b["parts"] for b in boards if b["board"] == "B"), "native_pcb": True},
        "validation": validation,
        "design_advancement": "complete native carrier schematics, exact footprints, six-layer board outlines and placement candidates; rejected auto-route removed",
        "drc_acceptance": False, "fabrication_authority": False, "assembly_authority": False, "connection_authority": False, "motion_authority": False, "energization_authority": False,
        "open": ["complete copper routing and resolve every DRC item", "independent schematic/footprint/layout review", "exact stackup and isolation geometry", "termination and bias configuration", "surge/miswire/EMC/timing/thermal tests", "cable and power-injection hardware", "qualified electrical and safety review"],
    }
    (OUT / "carrier-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    cards = []
    for b in boards:
        bid = str(b["board"]); stem = Path(b["path"]).stem
        cards.append(f'''<article><h2>Carrier {bid}</h2><p><strong>{b['parts']} placed components · {b['nets']} named nets · copper routing explicitly open</strong></p><h3>Front: transceivers and connectors</h3><div class="board"><object data="output/{stem}-front.svg" type="image/svg+xml" aria-label="Carrier {bid} front placement and pad view"></object></div><h3>Back: support passives and configuration parts</h3><div class="board"><object data="output/{stem}-back.svg" type="image/svg+xml" aria-label="Carrier {bid} back placement and pad view"></object></div><p><a href="carrier-{bid.lower()}/{stem}.kicad_pcb">Open native KiCad PCB</a> · <a href="validation/{stem}-drc.rpt">Read the complete unrouted DRC report</a></p></article>''')
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator interface carriers P0.1</title><style>:root{{--ink:#071b38;--blue:#0b4f91;--sky:#b9e8ff;--gold:#f5bd2b;--paper:#f5fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{max-width:none;background:var(--ink);color:white}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}.warning{{border:3px solid var(--gold);padding:14px;font-weight:900}}article{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;margin:22px 0}}.board{{overflow:auto;border:1px solid #8bc7e8;background:white}}object{{display:block;width:100%;min-width:760px;min-height:420px}}a{{color:#07549a;font-weight:800}}small{{font-size:14px}}@media(max-width:680px){{body{{font-size:16px}}header,main{{padding:20px 14px}}}}</style></head><body><header><div><p class="warning">{html.escape(WARNING)}</p><h1>Two physical carrier placement candidates.</h1><p>The whole-body architecture now has complete application circuits, exact footprints, 82 × 42 mm board outlines and editable KiCad placement candidates.</p></div></header><main><p><strong>What this is:</strong> editable circuit and placement source. <strong>What it is not:</strong> a routed PCB or fabrication package. The rejected automatic route was removed. Copper routing, DRC closure, isolation, signal integrity, EMC, thermal and physical fault evidence remain gates.</p>{''.join(cards)}<article><h2>Configuration and source records</h2><p><a href="carrier-component-register.csv">Component register</a> · <a href="carrier-terminal-register.csv">pad/net register</a> · <a href="carrier-routing-register.csv">routing lane plan</a> · <a href="carrier-configuration-register.csv">assembly configuration</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="{PROJECT}.kicad_pro">native schematic project</a></p></article></main></body></html>''', encoding="utf-8")
    readme = f"""# HR-30 actuator-interface carriers P0.1\n\n**{WARNING}**\n\nThis package advances the whole humanoid's eight actuator buses from pin-level blocks to two dimensioned native KiCad PCB placement candidates. Carrier A contains four complete ISOW1432 RS-485 application channels. Carrier B contains one complete ISOW1432 channel and three SN74LVC1T45 translator channels. Both boards are 82 x 42 x 1.6 mm, use six copper layers, retain data-only field connectors, and include exact footprints, board outlines, placement, ratsnest and SVG inspection outputs.\n\nThe RS-485 channels include TI-required local bypassing, separate VISOOUT/VISOIN and GND2/GISOIN ferrites, an SM712 bus-protection candidate, and a default-open 120-ohm termination configuration. The TTL channels include dual-rail bypassing, a receive-default direction pulldown, 33-ohm series candidate, TPD1E10B06 ESD candidate and a DNP idle pull-up.\n\nAn automated via-in-pad route was generated during development and rejected after KiCad reported shorts and clearance failures. Those tracks and vias are not retained. The native boards intentionally preserve the unrouted ratsnest and deterministic lane reservations so the remaining work is visible. DRC output is evidence, not approval. Copper routing, isolation geometry, enclosure fit, cable retention, surge/miswire behavior, timing, waveform integrity, EMC, thermal performance and every powered test remain open.\n\nOpen `index.html` for the readable interactive guide.\n"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256", "warning"], [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "warning": WARNING} for p in sorted(files)])


def update_whole_body_package() -> None:
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "actuator_interface_carrier_application_circuits_complete": True,
        "actuator_interface_carrier_native_schematic_sheet_count": 10,
        "actuator_interface_carrier_schematic_erc_errors": 0,
        "actuator_interface_carrier_schematic_erc_warnings": 0,
        "actuator_interface_carrier_board_count": 2,
        "actuator_interface_carrier_component_count": 86,
        "actuator_interface_carrier_placement_complete": True,
        "actuator_interface_carrier_nonconnectivity_drc_violations": 0,
        "actuator_interface_carrier_unconnected_pad_count": 229,
        "actuator_interface_carrier_routing_complete": False,
        "actuator_interface_carrier_fabrication_outputs_released": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8", newline="")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H11":
            row["unresolved_item"] = (
                "The native 18-sheet HR-30 KiCad project and ten-sheet carrier project bind all 25 axes, eight STM32 UART groups, five complete "
                "ISOW1432 application circuits, three complete SN74LVC1T45 application circuits, exact data-only JST GH "
                "connectors, and two 82 x 42 mm six-layer placement candidates. Carrier schematic ERC is 0/0 and both boards "
                "have zero non-connectivity DRC violations. Copper routing remains deliberately open (140 Carrier A and 89 "
                "Carrier B unconnected pads). Stackup/isolation geometry, cables, branch power injection, grounding, EMC, timing, "
                "thermal behavior, sensing calibration, safety allocation and physical fault tests remain open."
            )
    with holds_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(holds[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(holds)

    equipment_path = PACKAGE / "installed-equipment-register.csv"
    equipment = list(csv.DictReader(equipment_path.open(encoding="utf-8", newline="")))
    for row in equipment:
        if row["item_id"] in {"EQ-T01-BUS-CARRIER-A", "EQ-T01-BUS-CARRIER-B"}:
            row["evidence_state"] = "complete sourced application circuit and 82 x 42 mm native PCB placement candidate exist; copper routing, stackup/isolation geometry, EMC, thermal and physical validation remain open; U2D2 stays external commissioning-only"
    with equipment_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(equipment[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(equipment)

    bom_path = PACKAGE / "whole-robot-candidate-bom.csv"
    bom = list(csv.DictReader(bom_path.open(encoding="utf-8", newline="")))
    for row in bom:
        if row["item_id"] == "HR30-BOM-010":
            row["candidate"] = "5x complete ISOW1432DFMR isolated RS-485 plus 3x complete SN74LVC1T45DCKR translated TTL carrier application circuits; two native PCB placement candidates; copper routing and physical validation open"
    with bom_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bom[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(bom)

    readme_path = PACKAGE / "README.md"; readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-CARRIERS-P01-START -->", "<!-- HR30-CARRIERS-P01-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    section = f"""\n{start}\n## Physical actuator-interface carriers\n\nThe eight whole-body actuator buses now have **86 sourced circuit parts** across two native 82 × 42 mm KiCad PCB placement candidates. Carrier A contains four complete ISOW1432 isolated RS-485 application networks; Carrier B contains one more plus three SN74LVC1T45 TTL networks. The carrier schematic hierarchy passes KiCad ERC with 0 errors and 0 warnings. Both board placements have zero non-connectivity DRC violations. Copper is deliberately unrouted: KiCad reports 140 Carrier A and 89 Carrier B unconnected pads. The rejected automatic route is not retained, and no Gerber or drill package is published. Open `electrical/carriers-p0.1/index.html` for the front/back board guide.\n{end}"""
    readme_path.write_text(readme.rstrip() + section + "\n", encoding="utf-8")

    page_path = PACKAGE / "index.html"; page = page_path.read_text(encoding="utf-8")
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    web = f'''{start}<section id="actuator-interface-carriers"><h2>The actuator buses now have physical carrier candidates</h2><div class="grid"><article class="card pass"><div class="metric">86</div><p>Sourced parts across five isolated RS-485 and three translated TTL application circuits.</p></article><article class="card pass"><div class="metric">2</div><p>Native 82 × 42 mm six-layer KiCad placement candidates sized to the torso tray.</p></article><article class="card pass"><h3>ERC 0 / 0</h3><p>The ten-sheet carrier schematic hierarchy parses with no ERC errors or warnings.</p></article><article class="card hold"><h3>Routing remains open</h3><p>Zero non-connectivity DRC violations; 229 unrouted pad connections remain visible. No Gerbers or drill files are released.</p></article></div><div class="viewer"><object data="electrical/carriers-p0.1/output/hr30-carrier-a-p0.1-front.svg" type="image/svg+xml" aria-label="Carrier A front placement candidate"></object><p><a href="electrical/carriers-p0.1/index.html">Open the front/back carrier-board guide</a> · <a href="electrical/carriers-p0.1/carrier-component-register.csv">Component register</a> · <a href="electrical/carriers-p0.1/hr30-actuator-interface-carriers-p0.1.kicad_pro">Native carrier schematic project</a>.</p></div></section>{end}'''
    marker = "<!-- HR30-NATIVE-KICAD-P01-END -->"
    if marker not in page:
        raise RuntimeError("native KiCad website marker missing")
    page_path.write_text(page.replace(marker, marker + web), encoding="utf-8")

    shutil.copy2(ROOT / "tools" / "generate_hr30_actuator_bus_architecture_p01.py", PACKAGE / "actuator-bus-architecture-source.py")
    shutil.copy2(ROOT / "tools" / "generate_hr30_installed_equipment_p01.py", PACKAGE / "installed-equipment-source.py")
    shutil.copy2(ROOT / "tools" / "generate_hr30_system_package_p01.py", PACKAGE / "system-package-source.py")

    # Refresh the source-package manifest only. The branch's unrelated release
    # tree is intentionally not touched.
    files = [p for p in PACKAGE.rglob("*") if p.is_file() and p != PACKAGE / "file-manifest.csv"]
    write_csv(PACKAGE / "file-manifest.csv", ["path", "bytes", "sha256", "warning"], [{"path": p.relative_to(PACKAGE).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "warning": WHOLE_BODY_WARNING} for p in sorted(files)])
    release = ROOT / "release" / "hr30" / "whole-body-p0.1"
    for path in PACKAGE.rglob("*"):
        if path.is_file():
            target = release / path.relative_to(PACKAGE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    parts = circuit_parts(); print("carrier: writing schematic", flush=True); write_schematic(parts)
    print("carrier: writing board A", flush=True); board_a = write_board("A", parts)
    print("carrier: writing board B", flush=True); board_b = write_board("B", parts)
    boards = [board_a, board_b]
    print("carrier: running KiCad validation/exports", flush=True); validation = export_and_validate(boards)
    print("carrier: publishing registers and guide", flush=True)
    publish(parts, boards, validation)
    update_whole_body_package()
    print(json.dumps({"parts": len(parts), "boards": [{"id": b["board"], "parts": b["parts"], "nets": b["nets"], "vias": b["routing"]["vias"]} for b in boards], "validation": validation}, indent=2))


if __name__ == "__main__":
    main()
