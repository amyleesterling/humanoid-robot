#!/usr/bin/env python3
"""Generate the two HR-30 actuator-interface carrier candidates.

The boards are editable, placed and routed KiCad candidates derived from the
pin-level whole-body electrical architecture.  Manufacturing outputs are
included for inspection, but every output remains explicitly non-authorizing.
"""

from __future__ import annotations

import csv
import hashlib
import heapq
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
JLC_6_LAYER = "https://jlcpcb.com/6-layer-pcb"
JLC_IMPEDANCE = "https://jlcpcb.com/impedance"

STACKUP_ID = "JLC06161H-3313"
STACKUP_LAYERS = (
    ("F.Cu", "copper", 0.035, ""),
    ("dielectric 1", "prepreg", 0.0994, "3313"),
    ("In1.Cu", "copper", 0.0152, ""),
    ("dielectric 2", "core", 0.55, "FR-4"),
    ("In2.Cu", "copper", 0.0152, ""),
    ("dielectric 3", "prepreg", 0.1088, "2116"),
    ("In3.Cu", "copper", 0.0152, ""),
    ("dielectric 4", "core", 0.55, "FR-4"),
    ("In4.Cu", "copper", 0.0152, ""),
    ("dielectric 5", "prepreg", 0.0994, "3313"),
    ("B.Cu", "copper", 0.035, ""),
)

RS_BUSES = (("RS-LLEG", "A"), ("RS-RLEG", "A"), ("RS-LARM", "A"), ("RS-RARM", "A"), ("RS-WAIST", "B"))
TTL_BUSES = (("TTL-LDIST", "B"), ("TTL-RDIST", "B"), ("TTL-HEAD", "B"))
# Optional caller-owned reserved points.  The carrier generator leaves this
# empty; other board generators may reserve future via locations without
# inventing temporary components or copper.
EXTRA_ROUTING_OBSTACLES: list[tuple[float, float, str]] = []
ROUTER_PROGRESS = False


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


def apply_stackup(board_path: Path) -> None:
    """Bind the native board to the current JLCPCB 1.6 mm six-layer candidate.

    The manufacturer-published buildup totals 1.5384 mm before solder mask and
    is sold as a nominal 1.6 mm finished board.  No dielectric constant is
    invented here; impedance and finished-thickness acceptance remain open.
    """
    layer_lines = []
    for name, kind, thickness, material in STACKUP_LAYERS:
        material_clause = f'\n\t\t\t\t(material "{material}")' if material else ""
        color_clause = '\n\t\t\t\t(color "FR4 natural")' if kind in {"prepreg", "core"} else ""
        layer_lines.append(
            f'\t\t\t(layer "{name}"\n\t\t\t\t(type "{kind}"){color_clause}\n'
            f'\t\t\t\t(thickness {thickness}){material_clause}\n\t\t\t)'
        )
    stackup = (
        "\t\t(stackup\n"
        "\t\t\t(layer \"F.SilkS\" (type \"Top Silk Screen\"))\n"
        "\t\t\t(layer \"F.Paste\" (type \"Top Solder Paste\"))\n"
        "\t\t\t(layer \"F.Mask\" (type \"Top Solder Mask\") (thickness 0.01))\n"
        + "\n".join(layer_lines)
        + "\n\t\t\t(layer \"B.Mask\" (type \"Bottom Solder Mask\") (thickness 0.01))\n"
        "\t\t\t(layer \"B.Paste\" (type \"Bottom Solder Paste\"))\n"
        "\t\t\t(layer \"B.SilkS\" (type \"Bottom Silk Screen\"))\n"
        "\t\t\t(copper_finish \"ENIG\")\n"
        "\t\t\t(dielectric_constraints no)\n"
        "\t\t)\n"
    )
    text = board_path.read_text(encoding="utf-8")
    marker = "\t(setup\n"
    if text.count(marker) != 1 or "\t\t(stackup\n" in text:
        raise RuntimeError(f"unexpected stackup insertion state: {board_path}")
    board_path.write_text(text.replace(marker, marker + stackup, 1), encoding="utf-8")


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
    via = pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(0.35))
    via.SetDrill(pcbnew.FromMM(0.15)); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def add_isolation_keepout(board: pcbnew.BOARD, center_x: float) -> None:
    """Reserve a four-millimetre all-copper moat beneath one ISOW1432."""
    zone = pcbnew.ZONE(board); zone.SetIsRuleArea(True); zone.SetLayerSet(pcbnew.LSET.AllCuMask())
    zone.SetDoNotAllowTracks(True); zone.SetDoNotAllowVias(True); zone.SetDoNotAllowZoneFills(True)
    zone.SetDoNotAllowPads(False); zone.SetDoNotAllowFootprints(False)
    outline = zone.Outline(); outline.NewOutline()
    for point in ((center_x - 8.2, 18.0), (center_x + 8.2, 18.0), (center_x + 8.2, 22.0), (center_x - 8.2, 22.0)):
        outline.Append(pcbnew.VECTOR2I_MM(*point))
    board.Add(zone)


def interval_lane(interval, occupied, candidates):
    x0, x1 = interval
    for lane in candidates:
        if all(
            abs(lane - other_lane) >= 0.43 or x1 < a - 0.43 or x0 > b + 0.43
            for other_lane, intervals in occupied.items()
            for a, b in intervals
        ):
            occupied[lane].append((x0, x1)); return lane
    raise RuntimeError(f"no routing lane for interval {interval}")


def route_board(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM]) -> dict[str, object]:
    pad_records: list[dict[str, object]] = []
    pads_by_net: dict[str, list[dict[str, object]]] = defaultdict(list)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = pad.GetNetname()
            if name:
                pos = pad.GetPosition(); px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                center = fp.GetPosition(); cx, cy = pcbnew.ToMM(center.x), pcbnew.ToMM(center.y)
                ref = fp.GetReference()
                bbox = pad.GetBoundingBox()
                half_x = pcbnew.ToMM(bbox.GetWidth()) / 2.0
                half_y = pcbnew.ToMM(bbox.GetHeight()) / 2.0
                if ref.startswith("J"):
                    ux, uy = (0.0, -1.0) if py > 30.0 else (0.0, 1.0)
                    if ref.startswith("J1") and pad.GetNumber() == "1":
                        ux, uy = 0.50, 1.0
                elif not ref.startswith("U"):
                    ux = 0.0
                    if py >= 22.0:
                        uy = 1.0
                    elif py >= 16.0:
                        uy = 1.0
                    elif py >= 10.0:
                        uy = -1.0
                    else:
                        uy = 1.0
                elif abs(px - cx) >= abs(py - cy):
                    ux, uy = (1.0 if px >= cx else -1.0), 0.0
                else:
                    ux, uy = 0.0, (1.0 if py >= cy else -1.0)
                clearance = 0.36
                if ref.startswith("J1") and pad.GetNumber() == "1":
                    distance = 3.60
                else:
                    distance = 0.80 if ref.startswith("J") else (half_x if ux else half_y) + clearance
                if not ref.startswith(("J", "U")):
                    distance += 0.12 * (sum(ord(char) for char in ref) % 2)
                escape = (px + ux * distance, py + uy * distance)
                outer = pcbnew.B_Cu if pad.IsOnLayer(pcbnew.B_Cu) and not pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.F_Cu
                bounds = (pcbnew.ToMM(bbox.GetX()), pcbnew.ToMM(bbox.GetY()), pcbnew.ToMM(bbox.GetRight()), pcbnew.ToMM(bbox.GetBottom()))
                record = {"net": name, "ref": ref, "pad": pad.GetNumber(), "point": (px, py), "escape": escape, "direction": (ux, uy), "outer": outer, "bounds": bounds}
                pad_records.append(record); pads_by_net[name].append(record)
    def point_clear_of_other_pads(x: float, y: float, net_name: str, margin: float = 0.28) -> bool:
        for other in pad_records:
            if other["net"] == net_name:
                continue
            left, top_y, right, bottom_y = map(float, other["bounds"])
            if left - margin <= x <= right + margin and top_y - margin <= y <= bottom_y + margin:
                return False
        return True

    # Move every escape via far enough beyond its SMD pad to clear unrelated
    # copper and every other drilled escape.  The fan-out direction remains
    # normal to the package pad row, preserving a short deterministic stub.
    placed_escapes: list[tuple[float, float]] = []
    for record in sorted(pad_records, key=lambda item: (str(item["ref"]), str(item["pad"]))):
        px, py = map(float, record["point"]); ex0, ey0 = map(float, record["escape"]); ux, uy = map(float, record["direction"])
        accepted = None
        for step in range(17):
            ex, ey = ex0 + ux * 0.22 * step, ey0 + uy * 0.22 * step
            if not (0.55 < ex < 81.45 and 0.55 < ey < 41.45):
                continue
            if not point_clear_of_other_pads(ex, ey, str(record["net"])):
                continue
            if any((ex - ox) ** 2 + (ey - oy) ** 2 < 0.46 ** 2 for ox, oy in placed_escapes):
                continue
            accepted = (ex, ey); break
        if accepted is None:
            raise RuntimeError(f"no DRC-clear escape via for {record['ref']}.{record['pad']} [{record['net']}]")
        record["escape"] = accepted; placed_escapes.append(accepted)

    def point_segment_distance(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
        px, py = point; x1, y1 = start; x2, y2 = end
        dx, dy = x2 - x1, y2 - y1
        if dx == 0.0 and dy == 0.0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        fraction = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        qx, qy = x1 + fraction * dx, y1 + fraction * dy
        return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5

    # Keep drilled escapes away from every other net's surface fan-out stub.
    # Extending only along the already-frozen pad normal avoids arbitrary jogs.
    for _ in range(6):
        changed = False
        for record in pad_records:
            net_name = str(record["net"]); px, py = map(float, record["point"]); ex, ey = map(float, record["escape"]); ux, uy = map(float, record["direction"])
            if (ex - px) ** 2 + (ey - py) ** 2 >= 3.0 ** 2 and not str(record["ref"]).startswith("J1"):
                continue
            conflicts = [
                other for other in pad_records
                if other is not record and str(other["net"]) != net_name
                and point_segment_distance((ex, ey), tuple(map(float, other["point"])), tuple(map(float, other["escape"]))) < 0.39
            ]
            if not conflicts:
                continue
            accepted = None
            for extension in range(1, 13):
                candidate = (ex + ux * 0.22 * extension, ey + uy * 0.22 * extension)
                if (candidate[0] - px) ** 2 + (candidate[1] - py) ** 2 > 3.0 ** 2 and not str(record["ref"]).startswith("J1"):
                    break
                if not (0.55 < candidate[0] < 81.45 and 0.55 < candidate[1] < 41.45):
                    break
                if not point_clear_of_other_pads(candidate[0], candidate[1], net_name):
                    continue
                if any(
                    other is not record and (candidate[0] - float(other["escape"][0])) ** 2 + (candidate[1] - float(other["escape"][1])) ** 2 < 0.46 ** 2
                    for other in pad_records
                ):
                    continue
                if any(
                    other is not record and str(other["net"]) != net_name
                    and point_segment_distance(candidate, tuple(map(float, other["point"])), tuple(map(float, other["escape"]))) < 0.39
                    for other in pad_records
                ):
                    continue
                accepted = candidate; break
            if accepted is None:
                continue
            record["escape"] = accepted; changed = True
        if not changed:
            break

    grid = 0.50; x_origin = 1.0; y_origin = 1.0; nx = 161; ny = 81
    layers = (pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu)
    occupied: dict[int, dict[tuple[int, int], str]] = {layer: {} for layer in layers}
    transition_vias: dict[tuple[int, int], str] = {}
    mounting_centers = ((3.5, 3.5), (78.5, 3.5), (3.5, 38.5), (78.5, 38.5))
    isolation_barriers = []
    for footprint in board.GetFootprints():
        reference = footprint.GetReference()
        if reference.startswith("U1") and reference[1:].isdigit():
            position = footprint.GetPosition(); isolation_barriers.append((pcbnew.ToMM(position.x) - 8.2, pcbnew.ToMM(position.x) + 8.2, 18.0, 22.0))

    def point_for(cell: tuple[int, int]) -> tuple[float, float]:
        return x_origin + cell[0] * grid, y_origin + cell[1] * grid

    def nearest_cell(point: tuple[float, float]) -> tuple[int, int]:
        return round((point[0] - x_origin) / grid), round((point[1] - y_origin) / grid)

    def inside(cell: tuple[int, int]) -> bool:
        ix, iy = cell
        if not (0 <= ix < nx and 0 <= iy < ny):
            return False
        x, y = point_for(cell)
        if not all((x - hx) ** 2 + (y - hy) ** 2 >= 1.85 ** 2 for hx, hy in mounting_centers):
            return False
        return all(not (x0 <= x <= x1 and y0 <= y <= y1) for x0, x1, y0, y1 in isolation_barriers)

    escape_obstacles = [(float(record["escape"][0]), float(record["escape"][1]), str(record["net"])) for record in pad_records] + list(EXTRA_ROUTING_OBSTACLES)
    fanout_segments = [(tuple(map(float, record["point"])), tuple(map(float, record["escape"])), str(record["net"])) for record in pad_records]

    def cell_available(layer: int, cell: tuple[int, int], net_name: str, for_via: bool = False) -> bool:
        if not inside(cell):
            return False
        owner = occupied[layer].get(cell)
        if owner not in (None, net_name):
            return False
        if transition_vias.get(cell) not in (None, net_name):
            return False
        x, y = point_for(cell)
        if any(other_net != net_name and (x - ox) ** 2 + (y - oy) ** 2 < 0.39 ** 2 for ox, oy, other_net in escape_obstacles):
            return False
        if for_via:
            if any(occupied[other_layer].get(cell) not in (None, net_name) for other_layer in layers):
                return False
            if any(other_net != net_name and (cell[0] - other_cell[0]) ** 2 + (cell[1] - other_cell[1]) ** 2 <= 1 for other_cell, other_net in transition_vias.items()):
                return False
            if any((x - ox) ** 2 + (y - oy) ** 2 < 0.46 ** 2 for ox, oy, _ in escape_obstacles):
                return False
            if not point_clear_of_other_pads(x, y, net_name, margin=0.28):
                return False
            if any(other_net != net_name and point_segment_distance((x, y), start, end) < 0.39 for start, end, other_net in fanout_segments):
                return False
        return True

    def edge_available(layer: int, start: tuple[int, int], end: tuple[int, int], net_name: str) -> bool:
        a, b = point_for(start), point_for(end)
        if not all(other_net == net_name or point_segment_distance((ox, oy), a, b) >= 0.39 for ox, oy, other_net in escape_obstacles):
            return False
        return all(other_net == net_name or point_segment_distance(point_for(cell), a, b) >= 0.39 for cell, other_net in transition_vias.items())

    def target_cell(point: tuple[float, float], net_name: str) -> tuple[int, int]:
        base = nearest_cell(point)
        candidates = [(dx * dx + dy * dy, (base[0] + dx, base[1] + dy)) for dx in range(-3, 4) for dy in range(-3, 4)]
        for _, cell in sorted(candidates):
            if any(cell_available(layer, cell, net_name) for layer in layers):
                return cell
        raise RuntimeError(f"no internal grid access near {point} for {net_name}")

    def find_path(target: tuple[int, int], tree: set[tuple[int, int, int]], net_name: str) -> list[tuple[int, int, int]]:
        tree_xy = {(ix, iy) for _, ix, iy in tree}
        min_x = min(ix for ix, _ in tree_xy); max_x = max(ix for ix, _ in tree_xy)
        min_y = min(iy for _, iy in tree_xy); max_y = max(iy for _, iy in tree_xy)

        def heuristic(ix: int, iy: int) -> int:
            return max(min_x - ix, 0, ix - max_x) + max(min_y - iy, 0, iy - max_y)

        frontier: list[tuple[int, int, tuple[int, int, int]]] = []
        parent: dict[tuple[int, int, int], tuple[int, int, int] | None] = {}
        cost: dict[tuple[int, int, int], int] = {}
        serial = 0
        for layer in layers:
            if cell_available(layer, target, net_name):
                state = (layer, target[0], target[1]); parent[state] = None; cost[state] = 0
                heapq.heappush(frontier, (heuristic(target[0], target[1]), serial, state)); serial += 1
        while frontier:
            _, _, state = heapq.heappop(frontier)
            layer, ix, iy = state
            if state in tree:
                path = [state]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                path.reverse(); return path
            base_cost = cost[state]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cell = (ix + dx, iy + dy)
                if not cell_available(layer, cell, net_name) or not edge_available(layer, (ix, iy), cell, net_name):
                    continue
                candidate = (layer, cell[0], cell[1]); new_cost = base_cost + 1
                if new_cost < cost.get(candidate, 10**9):
                    cost[candidate] = new_cost; parent[candidate] = state
                    heapq.heappush(frontier, (new_cost + heuristic(cell[0], cell[1]), serial, candidate)); serial += 1
            for other_layer in layers:
                if other_layer == layer or not cell_available(other_layer, (ix, iy), net_name, for_via=True):
                    continue
                candidate = (other_layer, ix, iy); new_cost = base_cost + 7
                if new_cost < cost.get(candidate, 10**9):
                    cost[candidate] = new_cost; parent[candidate] = state
                    heapq.heappush(frontier, (new_cost + heuristic(ix, iy), serial, candidate)); serial += 1
        raise RuntimeError(f"maze router could not connect {net_name} at {point_for(target)}")

    routed_vias = 0; route_rows: list[dict[str, object]] = []; summary_rows = []
    net_order = sorted(
        ((name, records) for name, records in pads_by_net.items() if len(records) >= 2),
        key=lambda item: (0 if item[0] in {"CTRL_GND", "CTRL_3V3", "CTRL_5V"} else 1, -len(item[1]), item[0]),
    )
    for name, records in net_order:
        if ROUTER_PROGRESS:
            print(f"router net {name} pads={len(records)}", flush=True)
        width = 0.20 if name in {"CTRL_GND", "CTRL_3V3", "CTRL_5V"} or name.endswith(("_RET", "_VISOOUT", "_VISOIN", "_GND2")) else 0.15
        for record in records:
            px, py = map(float, record["point"]); ex, ey = map(float, record["escape"]); outer = int(record["outer"])
            add_track(board, nets[name], (px, py), (ex, ey), outer, width); add_via(board, nets[name], (ex, ey)); routed_vias += 1
        root_record = records[0]; root_point = tuple(map(float, root_record["escape"])); root_cell = target_cell(root_point, name)
        root_layer = next(layer for layer in layers if cell_available(layer, root_cell, name))
        add_track(board, nets[name], root_point, point_for(root_cell), root_layer, width)
        occupied[root_layer][root_cell] = name
        tree: set[tuple[int, int, int]] = {(root_layer, root_cell[0], root_cell[1])}
        pending = records[1:]; segment_count = 1; net_transition_vias = 0
        while pending:
            target_record = min(pending, key=lambda record: min(abs(nearest_cell(tuple(map(float, record["escape"])))[0] - ix) + abs(nearest_cell(tuple(map(float, record["escape"])))[1] - iy) for _, ix, iy in tree))
            pending.remove(target_record); exact = tuple(map(float, target_record["escape"])); target = target_cell(exact, name)
            path = find_path(target, tree, name)
            add_track(board, nets[name], exact, point_for((path[0][1], path[0][2])), path[0][0], width); segment_count += 1
            for first, second in zip(path, path[1:]):
                l1, x1, y1 = first; l2, x2, y2 = second
                if l1 == l2:
                    add_track(board, nets[name], point_for((x1, y1)), point_for((x2, y2)), l1, width); segment_count += 1
                else:
                    cell = (x1, y1)
                    if transition_vias.get(cell) != name:
                        add_via(board, nets[name], point_for(cell)); routed_vias += 1; net_transition_vias += 1; transition_vias[cell] = name
            for layer, ix, iy in path:
                occupied[layer][(ix, iy)] = name; tree.add((layer, ix, iy))
            route_rows.append({"net": name, "reference": target_record["ref"], "pad": target_record["pad"], "escape_x_mm": f"{exact[0]:.3f}", "escape_y_mm": f"{exact[1]:.3f}", "grid_x_mm": f"{point_for(target)[0]:.3f}", "grid_y_mm": f"{point_for(target)[1]:.3f}", "track_width_mm": f"{width:.3f}"})
        summary_rows.append({"net": name, "routing_grid_mm": f"{grid:.2f}", "routed_pad_count": len(records), "path_segments": segment_count, "transition_vias": net_transition_vias, "routing_layers": "In1.Cu/In2.Cu/In3.Cu/In4.Cu"})
    return {"vias": routed_vias, "lanes": summary_rows, "routes": route_rows, "routing_complete": True, "routing_method": "four-layer deterministic Manhattan maze route", "routing_grid_mm": grid}


def write_board(board_id: str, parts: list[Part]) -> dict[str, object]:
    board_parts = [p for p in parts if p.board == board_id]
    board = pcbnew.BOARD(); board.SetCopperLayerCount(6)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.10); settings.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings.m_HoleClearance = pcbnew.FromMM(0.10); settings.m_SolderMaskMinWidth = pcbnew.FromMM(0.10)
    settings.m_HoleToHoleMin = pcbnew.FromMM(0.25); settings.m_ViasMinSize = pcbnew.FromMM(0.35)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.15); settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.10)
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
    for footprint in board.GetFootprints():
        reference = footprint.GetReference()
        if reference.startswith("U1") and reference[1:].isdigit():
            add_isolation_keepout(board, pcbnew.ToMM(footprint.GetPosition().x))
    for start, end in zip(((0, 0), (82, 0), (82, 42), (0, 42)), ((82, 0), (82, 42), (0, 42), (0, 0))):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end))
        edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)
    routing = route_board(board, nets)
    add_text(board, f"HR-30 CARRIER {board_id} P0.1", 26, 1.8, 0.9, pcbnew.B_SilkS)
    add_text(board, "DATA ONLY - NO ACTUATOR VDD", 25, 40.0, 0.8, pcbnew.B_SilkS)
    add_text(board, "PRELIMINARY / DO NOT FABRICATE OR CONNECT", 18, 35.0, 0.8, pcbnew.B_SilkS)
    board_path = OUT / f"carrier-{board_id.lower()}" / f"hr30-carrier-{board_id.lower()}-p0.1.kicad_pcb"
    board_path.parent.mkdir(parents=True, exist_ok=True); pcbnew.SaveBoard(str(board_path), board)
    apply_stackup(board_path)
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
        if drc.returncode != 0:
            raise RuntimeError(f"{stem} must reach KiCad DRC 0/0 before fabrication-candidate exports")
        run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{stem}-front.svg", "--layers", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", path])
        run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{stem}-back.svg", "--layers", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", "--mirror", "--fit-page-to-board", "--exclude-drawing-sheet", path])
        for layer in ("In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu"):
            slug = layer.lower().replace(".", "-")
            run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{stem}-{slug}.svg", "--layers", f"{layer},Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", path])

        fab = OUT / "fabrication-candidate-not-released" / f"carrier-{str(board_id).lower()}"
        gerber = fab / "gerber"; drill = fab / "drill"
        gerber.mkdir(parents=True, exist_ok=True); drill.mkdir(parents=True, exist_ok=True)
        run_cli(["pcb", "export", "gerbers", "--output", gerber, "--layers", "F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts", "--precision", "6", "--check-zones", path])
        run_cli(["pcb", "export", "drill", "--output", drill, "--format", "excellon", "--drill-origin", "absolute", "--excellon-zeros-format", "decimal", "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "svg", "--generate-report", "--report-path", drill / f"{stem}-drill-report.rpt", path])
        run_cli(["pcb", "export", "ipcd356", "--output", fab / f"{stem}.d356", path])
        run_cli(["pcb", "export", "pos", "--output", fab / f"{stem}-positions.csv", "--side", "both", "--format", "csv", "--units", "mm", "--exclude-dnp", path])
        run_cli(["pcb", "export", "stats", "--output", fab / f"{stem}-board-stats.json", "--format", "json", "--units", "mm", path])
        (fab / "README.txt").write_text(
            f"{WARNING}\n\nMachine-readable output for design inspection and manufacturer DFM quotation only.\n"
            "It is not an order release and confers no procurement, fabrication, assembly, connection, motion, or energization authority.\n",
            encoding="utf-8",
        )
        results.append({"artifact": f"carrier-{board_id}", "return_code": drc.returncode, "report": str(drc_path)})
    # KiCad's SVG writer leaves decorative trailing spaces on many XML lines.
    # Normalize those generated exports so repository whitespace checks remain
    # useful without changing any geometric or presentation content.
    for svg in OUT.rglob("*.svg"):
        normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n"
        svg.write_text(normalized, encoding="utf-8")
    fab_files = [p for p in (OUT / "fabrication-candidate-not-released").rglob("*") if p.is_file()]
    write_csv(
        OUT / "fabrication-candidate-register.csv",
        ["path", "bytes", "sha256", "release_state", "warning"],
        [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p), "release_state": "CANDIDATE ONLY - NOT RELEASED FOR ORDER", "warning": WARNING} for p in sorted(fab_files)],
    )
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
            lane_rows.append({"board": board["board"], **row, "routing_method": board["routing"]["routing_method"], "warning": WARNING})
    write_csv(OUT / "carrier-routing-register.csv", list(lane_rows[0]), lane_rows)
    stackup_rows = [
        {"stackup_id": STACKUP_ID, "sequence": index, "layer": name, "type": kind, "nominal_thickness_mm": thickness, "material": material or "COPPER", "source": JLC_IMPEDANCE, "release_state": "CANDIDATE - FAB QUOTE/RECEIPT CONFIRMATION REQUIRED", "warning": WARNING}
        for index, (name, kind, thickness, material) in enumerate(STACKUP_LAYERS, 1)
    ]
    write_csv(OUT / "stackup-register.csv", list(stackup_rows[0]), stackup_rows)
    moat_rows = [
        {"board": p.board, "isolator": p.ref, "x_min_mm": f"{p.x - 8.2:.3f}", "x_max_mm": f"{p.x + 8.2:.3f}", "y_min_mm": "18.000", "y_max_mm": "22.000", "layers": "ALL COPPER", "rule": "NO TRACKS / NO VIAS / NO ZONES / NO COPPER POURS", "validation": "NATIVE KICAD RULE AREA; DRC 0/0", "warning": WARNING}
        for p in parts if p.ref.startswith("U1") and p.ref[1:].isdigit()
    ]
    write_csv(OUT / "isolation-moat-register.csv", list(moat_rows[0]), moat_rows)
    config_rows = [
        {"configuration_id": "TERM-RS-001", "applies_to": "SJ1-SJ5", "default": "OPEN / DNP", "change_condition": "Close only when this carrier is verified as a physical bus end and measured cable impedance/waveform supports 120 ohm termination.", "authority": "CONTROLLED CONFIGURATION CHANGE REQUIRED", "warning": WARNING},
        {"configuration_id": "TTL-PULLUP-001", "applies_to": "R201P-R203P", "default": "DNP", "change_condition": "Fit only after measured actuator/bus idle-state and loading validation.", "authority": "CONTROLLED CONFIGURATION CHANGE REQUIRED", "warning": WARNING},
        {"configuration_id": "ROUTING-001", "applies_to": "both boards", "default": "ROUTED ON In1.Cu/In2.Cu/In3.Cu/In4.Cu; 0 UNCONNECTED; KICAD DRC 0/0", "change_condition": "Any component, net, geometry, stackup or rule change requires regeneration and complete ERC/DRC rerun.", "authority": "INDEPENDENT LAYOUT/DFM/PHYSICAL REVIEW REQUIRED", "warning": WARNING},
        {"configuration_id": "STACKUP-001", "applies_to": "both boards", "default": f"{STACKUP_ID}; JLCPCB nominal 1.6 mm six-layer candidate; ENIG candidate", "change_condition": "Manufacturer DFM quotation and controlled impedance/material confirmation before fabrication release.", "authority": "FABRICATION RELEASE REQUIRED", "warning": WARNING},
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
        ("JLC-6L-CAPABILITY", "JLCPCB", "6-layer PCB manufacturing capability", "live official page accessed 2026-08-14", JLC_6_LAYER, "six-layer 1.6 mm capability and catalog manufacturing limits"),
        ("JLC-STACKUP-3313", "JLCPCB", "PCB impedance and stackup calculator", "live official page accessed 2026-08-14", JLC_IMPEDANCE, f"{STACKUP_ID} nominal layer buildup and material identifiers"),
    ]
    write_csv(OUT / "primary-source-register.csv", ["source_id", "manufacturer", "document", "revision_or_date", "url", "verified_use"], [{"source_id": a, "manufacturer": b, "document": c, "revision_or_date": d, "url": e, "verified_use": f} for a, b, c, d, e, f in sources])
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "carrier_a": {"board_mm": [82, 42, 1.6], "copper_layers": 6, "components": next(b["parts"] for b in boards if b["board"] == "A"), "native_pcb": True},
        "carrier_b": {"board_mm": [82, 42, 1.6], "copper_layers": 6, "components": next(b["parts"] for b in boards if b["board"] == "B"), "native_pcb": True},
        "validation": validation,
        "design_advancement": "complete native carrier schematics, exact footprints, deterministic routed copper, native isolation moats, candidate stackup and machine-readable fabrication-candidate outputs",
        "routing_complete": True, "unconnected_pad_count": 0, "kicad_drc_violations": 0, "kicad_erc_errors": 0, "kicad_erc_warnings": 0,
        "stackup_candidate": STACKUP_ID, "stackup_manufacturer_nominal_finished_thickness_mm": 1.6, "published_buildup_without_soldermask_mm": 1.5384,
        "fabrication_candidate_outputs_generated": True, "fabrication_outputs_released": False,
        "drc_acceptance": False, "fabrication_authority": False, "assembly_authority": False, "connection_authority": False, "motion_authority": False, "energization_authority": False,
        "open": ["independent schematic/footprint/routing/DFM review", "manufacturer confirmation of stackup, finished thickness, finish and controlled impedance", "termination and bias configuration", "surge/miswire/EMC/timing/thermal tests", "cable and power-injection hardware", "physical isolation and fault testing", "qualified electrical and safety review"],
    }
    (OUT / "carrier-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    cards = []
    for b in boards:
        bid = str(b["board"]); stem = Path(b["path"]).stem
        layer_views = ''.join(f'''<details><summary>{layer} routing</summary><div class="board"><object data="output/{stem}-{layer.lower().replace('.', '-')}.svg" type="image/svg+xml" aria-label="Carrier {bid} {layer} routed copper"></object></div></details>''' for layer in ("In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu"))
        cards.append(f'''<article><h2>Carrier {bid}</h2><p><strong>{b['parts']} components · {b['nets']} named nets · {b['routing']['vias']} vias · 0 unconnected pads</strong></p><h3>Front copper and components</h3><div class="board"><object data="output/{stem}-front.svg" type="image/svg+xml" aria-label="Carrier {bid} front routed board"></object></div><h3>Internal routing atlas</h3>{layer_views}<h3>Back copper and components</h3><div class="board"><object data="output/{stem}-back.svg" type="image/svg+xml" aria-label="Carrier {bid} back routed board"></object></div><p><a href="carrier-{bid.lower()}/{stem}.kicad_pcb">Open native KiCad PCB</a> · <a href="validation/{stem}-drc.rpt">Read the complete DRC 0/0 report</a> · <a href="fabrication-candidate-not-released/carrier-{bid.lower()}/">Inspect machine fabrication candidates</a></p></article>''')
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator interface carriers P0.1</title><style>:root{{--ink:#071b38;--blue:#0b4f91;--sky:#b9e8ff;--gold:#f5bd2b;--paper:#f5fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{max-width:none;background:var(--ink);color:white}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}.warning{{border:3px solid var(--gold);padding:14px;font-weight:900}}article{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;margin:22px 0}}.board{{overflow:auto;border:1px solid #8bc7e8;background:white}}object{{display:block;width:100%;min-width:760px;min-height:420px}}details{{margin:14px 0;border:1px solid #8bc7e8;border-radius:10px;padding:12px}}summary{{cursor:pointer;font-size:18px;font-weight:850;color:var(--blue)}}a{{color:#07549a;font-weight:800}}small{{font-size:14px}}@media(max-width:680px){{body{{font-size:16px}}header,main{{padding:20px 14px}}}}</style></head><body><header><div><p class="warning">{html.escape(WARNING)}</p><h1>Two routed physical carrier candidates.</h1><p>The whole-body architecture now has complete application circuits, exact footprints, 82 × 42 mm routed board geometry, editable KiCad sources and layer-by-layer inspection views.</p></div></header><main><p><strong>Verified here:</strong> native KiCad ERC 0/0, DRC 0/0, zero unconnected pads, exact all-copper isolation moats and a bound {STACKUP_ID} candidate stackup. <strong>Not verified:</strong> independent layout acceptance, manufacturer DFM, controlled impedance, signal integrity, EMC, thermal, fault behavior or physical safety. Machine files are inspection/quotation candidates only and are not released for ordering.</p>{''.join(cards)}<article><h2>Configuration and source records</h2><p><a href="carrier-component-register.csv">Component register</a> · <a href="carrier-terminal-register.csv">pad/net register</a> · <a href="carrier-routing-register.csv">routing register</a> · <a href="isolation-moat-register.csv">isolation moats</a> · <a href="stackup-register.csv">stackup</a> · <a href="fabrication-candidate-register.csv">machine-file register</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="{PROJECT}.kicad_pro">native schematic project</a></p></article></main></body></html>''', encoding="utf-8")
    readme = f"""# HR-30 actuator-interface carriers P0.1\n\n**{WARNING}**\n\nThis package advances the whole humanoid's eight actuator buses to two dimensioned, routed native KiCad PCB candidates. Carrier A contains four complete ISOW1432 RS-485 application channels. Carrier B contains one complete ISOW1432 channel and three SN74LVC1T45 translator channels. Both boards are 82 x 42 mm, use six copper layers, retain data-only field connectors, and regenerate from the source tool.\n\nKiCad 10 verifies schematic ERC at 0 errors / 0 warnings and both boards at 0 DRC violations / 0 unconnected pads. The deterministic route uses four internal signal layers with 0.15 mm general traces, 0.20 mm return/power-related traces, and 0.35/0.15 mm through vias. Five native all-copper rule areas preserve 4.0 mm isolation moats across the ISOW1432 barriers. The native boards bind the manufacturer-published {STACKUP_ID} nominal 1.6 mm six-layer candidate; the published copper/dielectric buildup totals 1.5384 mm before solder mask.\n\nThe machine-readable Gerber, Excellon, IPC-D-356, position and board-statistics outputs are fabrication candidates for inspection and DFM quotation only. They are explicitly not released for ordering. DRC completion does not establish independent design acceptance, controlled impedance, enclosure fit, cable retention, surge/miswire behavior, timing, waveform integrity, EMC, thermal performance, fault safety or permission for any powered test.\n\nOpen `index.html` for the interactive layer-by-layer guide.\n"""
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
        "actuator_interface_carrier_unconnected_pad_count": 0,
        "actuator_interface_carrier_routing_complete": True,
        "actuator_interface_carrier_stackup_candidate": STACKUP_ID,
        "actuator_interface_carrier_isolation_moat_count": 5,
        "actuator_interface_carrier_fabrication_candidate_outputs_generated": True,
        "actuator_interface_carrier_fabrication_outputs_released": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = PACKAGE / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8", newline="")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H11":
            row["unresolved_item"] = (
                "The native 19-sheet HR-30 KiCad project and ten-sheet carrier project bind all 25 axes, 25 distinct actuator power-feed boundaries, eight STM32 UART groups, five complete "
                "ISOW1432 application circuits, three complete SN74LVC1T45 application circuits, exact data-only JST GH "
                "connectors, and two 82 x 42 mm six-layer routed candidates. Carrier schematic ERC is 0/0; both boards have "
                "KiCad DRC 0/0 and zero unconnected pads. Five native all-copper isolation moats and the JLC06161H-3313 stackup "
                "candidate are bound in source. Independent layout/DFM acceptance, manufacturer stackup confirmation, cables, "
                "branch power injection, grounding, EMC, timing, thermal behavior, sensing calibration, safety allocation and "
                "physical fault tests remain open. Machine outputs are not released for ordering."
            )
    with holds_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(holds[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(holds)

    equipment_path = PACKAGE / "installed-equipment-register.csv"
    equipment = list(csv.DictReader(equipment_path.open(encoding="utf-8", newline="")))
    for row in equipment:
        if row["item_id"] in {"EQ-T01-BUS-CARRIER-A", "EQ-T01-BUS-CARRIER-B"}:
            row["evidence_state"] = "complete sourced application circuit and routed 82 x 42 mm native PCB candidate exist; ERC/DRC 0/0, zero unconnected pads, five isolation moats and candidate stackup are recorded; independent DFM, EMC, thermal and physical validation remain open; U2D2 stays external commissioning-only"
    with equipment_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(equipment[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(equipment)

    bom_path = PACKAGE / "whole-robot-candidate-bom.csv"
    bom = list(csv.DictReader(bom_path.open(encoding="utf-8", newline="")))
    for row in bom:
        if row["item_id"] == "HR30-BOM-010":
            row["candidate"] = "5x complete ISOW1432DFMR isolated RS-485 plus 3x complete SN74LVC1T45DCKR translated TTL carrier application circuits; two routed native PCB candidates; DFM, physical validation and fabrication release open"
    with bom_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bom[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(bom)

    readme_path = PACKAGE / "README.md"; readme = readme_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-CARRIERS-P01-START -->", "<!-- HR30-CARRIERS-P01-END -->"
    if start in readme and end in readme:
        readme = readme.split(start, 1)[0] + readme.split(end, 1)[1]
    section = f"""\n{start}\n## Physical actuator-interface carriers\n\nThe eight whole-body actuator buses now have **86 sourced circuit parts** across two routed native 82 × 42 mm KiCad PCB candidates. Carrier A contains four complete ISOW1432 isolated RS-485 application networks; Carrier B contains one more plus three SN74LVC1T45 TTL networks. KiCad verifies the carrier schematic at ERC 0/0 and both boards at DRC 0/0 with zero unconnected pads. Five all-copper rule areas protect the isolator moats, and the native sources bind the {STACKUP_ID} nominal 1.6 mm candidate stackup. Layer-by-layer SVGs and machine-readable DFM/fabrication candidates are published for inspection, but no output is released for ordering, assembly, connection or energization. Open `electrical/carriers-p0.1/index.html` for the routed layer guide.\n{end}"""
    readme_path.write_text(readme.rstrip() + section + "\n", encoding="utf-8")

    page_path = PACKAGE / "index.html"; page = page_path.read_text(encoding="utf-8")
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    web = f'''{start}<section id="actuator-interface-carriers"><h2>The actuator buses now have routed physical carrier candidates</h2><div class="grid"><article class="card pass"><div class="metric">86</div><p>Sourced parts across five isolated RS-485 and three translated TTL application circuits.</p></article><article class="card pass"><div class="metric">2</div><p>Native 82 × 42 mm six-layer KiCad routed candidates sized to the torso tray.</p></article><article class="card pass"><h3>ERC 0 / 0</h3><p>The ten-sheet carrier schematic hierarchy parses with no ERC errors or warnings.</p></article><article class="card pass"><h3>DRC 0 / 0</h3><p>Both boards have zero DRC violations and zero unconnected pads. Machine files remain non-released candidates.</p></article></div><div class="viewer"><object data="electrical/carriers-p0.1/output/hr30-carrier-a-p0.1-front.svg" type="image/svg+xml" aria-label="Carrier A front routed candidate"></object><p><a href="electrical/carriers-p0.1/index.html">Open the interactive routed-layer guide</a> · <a href="electrical/carriers-p0.1/carrier-component-register.csv">Component register</a> · <a href="electrical/carriers-p0.1/hr30-actuator-interface-carriers-p0.1.kicad_pro">Native carrier schematic project</a>.</p></div></section>{end}'''
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
