"""Generate the native HR-V0 watchdog PCB routed-copper candidate.

This board freezes board membership, footprints, terminal-block identities,
project pin allocation, placement constraints and a first controlled two-layer
routing candidate. It is not a fabrication release: supplier acceptance,
protection, physical test access, physical verification and independent layout
review remain open.

PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from hr_v0_watchdog_footprint_metadata import apply_metadata


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
BOARD_PATH = OUT / "project-button-v3.kicad_pcb"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")
FOOTPRINT_ROOT = KICAD_ROOT / "share" / "kicad" / "footprints"
CUSTOM_ROOT = OUT / "PBV3_Footprints.pretty"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
FAB_TRACE_MIN_MM = 0.1524
FAB_CLEARANCE_MIN_MM = 0.1524


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("pbv3_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load electrical model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PLACEMENTS = {
    "JWP1": (30, 34, 0),
    "DC1": (50, 34, 0),
    "CDRV1": (92, 39, 180),
    "UDRV1": (92, 34, 0),
    "CDRV2": (124, 39, 180),
    "UDRV2": (124, 34, 0),
    "JWF1": (150, 76, 0),
    "RTH1": (125, 70, 180),
    "RSN1": (109, 73.50, 270),
    "CFI1": (104, 70, 90),
    "RW1": (136, 70, 0),
    "RTH2": (125, 82, 180),
    "RSN2": (109, 78.50, 270),
    "CFI2": (104, 80.8, 270),
    "RW2": (136, 82, 0),
    "UFB1": (100, 76, 0),
    "CDEC1": (94.2, 73.5, 90),
    "RSO1": (91, 64, 0),
    "RPD1": (91, 68, 0),
    "RSO2": (91, 84, 0),
    "RPD2": (91, 88, 0),
    "JWH1": (30, 108, 0),
    "RHB1": (48, 108, 0),
    "ISO1": (62, 108, 0),
    "RHP1": (50, 98, 0),
    "WDCTRL1": (60, 72, 90),
    "TP1": (72, 40, 0),
    "TP2": (76, 36, 0),
    "TP3": (62, 32, 0),
    "TP4": (70, 46, 0),
    "TP5": (38, 105, 0),
    "TP6": (50, 92, 0),
    "TP7": (78, 52, 0),
    "TP8": (108, 54, 0),
    "TP9": (74, 24, 0),
    "TP10": (108, 21.5, 0),
    "TP11": (154, 66, 0),
    "TP12": (166, 88, 0),
    "TP13": (90, 58, 0),
    "TP14": (86, 90, 0),
    "TP15": (96, 58, 0),
    "TP16": (90, 78, 0),
}

TESTPOINT_LABELS = {
    "TP1": "24V", "TP2": "0V", "TP3": "5V", "TP4": "3V3",
    "TP5": "PI-HB", "TP6": "WD-HB", "TP7": "DRV1", "TP8": "DRV2",
    "TP9": "COIL1", "TP10": "COIL2", "TP11": "NC1", "TP12": "NC2",
    "TP13": "FB1", "TP14": "FB2", "TP15": "SWDIO", "TP16": "SWCLK",
}

TESTPOINT_LABEL_POSITIONS = {
    "TP10": (110.0, 23.5),
    "TP13": (86.0, 56.0),
    "TP14": (86.0, 93.0),
    "TP15": (98.0, 60.0),
}


def footprint_location(identifier: str) -> tuple[Path, str]:
    library, name = identifier.split(":", 1)
    if library == "PBV3_Footprints":
        return CUSTOM_ROOT, name
    return FOOTPRINT_ROOT / f"{library}.pretty", name


def add_text(pcbnew, board, value: str, x: float, y: float, size: float, layer):
    text = pcbnew.PCB_TEXT(board)
    text.SetText(value)
    text.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    text.SetLayer(layer)
    text.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    text.SetTextThickness(pcbnew.FromMM(max(0.18, size * 0.12)))
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(text)


def add_outline(pcbnew, board):
    points = [(20, 20), (180, 20), (180, 120), (20, 120), (20, 20)]
    for start, end in zip(points, points[1:]):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(pcbnew.VECTOR2I_MM(*start))
        line.SetEnd(pcbnew.VECTOR2I_MM(*end))
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetWidth(pcbnew.FromMM(0.25))
        board.Add(line)


def add_mounting_holes(pcbnew, board):
    lib = FOOTPRINT_ROOT / "MountingHole.pretty"
    for index, (x, y) in enumerate(((25, 25), (175, 25), (25, 115), (175, 115)), 1):
        footprint = pcbnew.FootprintLoad(str(lib), "MountingHole_3.2mm_M3")
        if footprint is None:
            raise RuntimeError("cannot load M3 mounting-hole footprint")
        footprint.SetReference(f"MH{index}")
        footprint.SetValue("M3 BOARD-ONLY - MOUNTING/ENCLOSURE SELECTION OPEN")
        footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        footprint.SetBoardOnly(True)
        footprint.SetExcludedFromBOM(True)
        footprint.SetExcludedFromPosFiles(True)
        board.Add(footprint)


def add_track(pcbnew, board, net, points, width: float, layer):
    """Add a routed polyline on one copper layer."""
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I_MM(*start))
        track.SetEnd(pcbnew.VECTOR2I_MM(*end))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_via(pcbnew, board, net, point, diameter: float = 0.8, drill: float = 0.4):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(*point))
    via.SetWidth(pcbnew.FromMM(diameter))
    via.SetDrill(pcbnew.FromMM(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def add_ground_zone(pcbnew, board, net):
    """Add the provisional B.Cu safety-return plane above the ISO1 corridor."""
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(net)
    zone.SetLocalClearance(pcbnew.FromMM(0.25))
    outline = zone.Outline()
    outline.NewOutline()
    for point in ((22, 22), (178, 22), (178, 103), (22, 103)):
        outline.Append(pcbnew.VECTOR2I_MM(*point))
    board.Add(zone)


def add_floating_plane(pcbnew, board, net, center):
    """Add the ISO1212-recommended isolated 2 mm x 2 mm B.Cu SUB plane."""
    x, y = center
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(net)
    zone.SetAssignedPriority(2)
    zone.SetLocalClearance(pcbnew.FromMM(FAB_CLEARANCE_MIN_MM))
    outline = zone.Outline()
    outline.NewOutline()
    for point in ((x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 1), (x - 1, y + 1)):
        outline.Append(pcbnew.VECTOR2I_MM(*point))
    board.Add(zone)


def route_board(pcbnew, board, nets):
    """Create the first reviewable two-layer route candidate."""
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}

    def pad_point(reference: str, number: str) -> tuple[float, float]:
        matches = [pad for pad in footprints[reference].Pads() if pad.GetNumber() == number]
        if len(matches) != 1:
            raise RuntimeError(f"expected one pad {reference}.{number}")
        position = matches[0].GetPosition()
        return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)

    def f(net_name: str, points, width: float = 0.25):
        add_track(pcbnew, board, nets[net_name], points, width, pcbnew.F_Cu)

    def b(net_name: str, points, width: float = 0.25):
        add_track(pcbnew, board, nets[net_name], points, width, pcbnew.B_Cu)

    def via(net_name: str, point, diameter: float = 0.8, drill: float = 0.4):
        add_via(pcbnew, board, nets[net_name], point, diameter, drill)

    # Bottom compute/heartbeat boundary. No B.Cu safety-return zone is placed
    # below y=103 mm, leaving a visible copper corridor around ISO1.
    f("PI_HEARTBEAT", [pad_point("JWH1", "1"), (30.0, 105.0), pad_point("TP5", "1"), (47.0, 105.0), pad_point("RHB1", "1")])
    f("HB_LED_A", [pad_point("RHB1", "2"), (53.0, 108.0), (55.0, 106.73), pad_point("ISO1", "1")])
    f("COMPUTE_0V", [pad_point("JWH1", "2"), (33.5, 113.0), (57.6, 113.0), pad_point("ISO1", "2")])

    # Watchdog heartbeat: local optical/pull-up connection plus a B.Cu hop to
    # the Pico edge. Vias are outside component pads rather than via-in-pad.
    f("WD_HEARTBEAT", [pad_point("ISO1", "4"), (60.0, 106.73), (55.0, 101.0), pad_point("RHP1", "2")])
    f("WD_HEARTBEAT", [pad_point("RHP1", "2"), (53.0, 96.0)])
    f("WD_HEARTBEAT", [(53.0, 96.0), pad_point("TP6", "1")])
    via("WD_HEARTBEAT", (53.0, 96.0))
    via("WD_HEARTBEAT", (42.0, 84.0))
    b("WD_HEARTBEAT", [(53.0, 96.0), (42.0, 96.0), (42.0, 84.0)])
    f("WD_HEARTBEAT", [(42.0, 84.0), pad_point("WDCTRL1", "4")])

    # Both controller supplies use B.Cu trunks with short front-copper Pico
    # fan-outs, avoiding the 24 V front-copper corridor.
    b("WD_5V", [pad_point("DC1", "3"), (60.0, 34.0), (60.0, 44.0), (32.0, 44.0), (32.0, 65.5), (38.41, 65.5)])
    f("WD_5V", [pad_point("DC1", "3"), (54.0, 34.0), (58.0, 32.0), pad_point("TP3", "1")], 0.5)
    via("WD_5V", (38.41, 65.5))
    f("WD_5V", [(38.41, 65.5), pad_point("WDCTRL1", "39")], 0.5)
    f("WD_3V3", [pad_point("WDCTRL1", "36"), (46.03, 58.0), (44.0, 58.0)])
    via("WD_3V3", (44.0, 58.0))
    f("WD_3V3", [pad_point("RHP1", "1"), (49.0, 104.0), (54.0, 104.0)])
    via("WD_3V3", (54.0, 104.0))
    f("WD_3V3", [pad_point("UFB1", "2"), (95.0, 74.412), pad_point("CDEC1", "1")], FAB_TRACE_MIN_MM)
    f("WD_3V3", [pad_point("UFB1", "3"), (94.5, 75.047), pad_point("CDEC1", "1")], FAB_TRACE_MIN_MM)
    f("WD_3V3", [pad_point("CDEC1", "1"), (92.0, 74.45)], FAB_TRACE_MIN_MM)
    via("WD_3V3", (92.0, 74.45))
    b("WD_3V3", [(44.0, 58.0), (44.0, 46.0)])
    via("WD_3V3", (44.0, 46.0))
    via("WD_3V3", (118.0, 46.0))
    f("WD_3V3", [(44.0, 46.0), pad_point("TP4", "1"), (118.0, 46.0)])
    b("WD_3V3", [(118.0, 46.0), (118.0, 100.0), (54.0, 100.0), (54.0, 104.0)])
    b("WD_3V3", [(118.0, 100.0), (118.0, 72.5), (93.5, 72.5), (93.5, 74.45), (92.0, 74.45)])

    # 24 V distribution and coil sinks use provisional 0.75 mm copper. Final
    # widths remain a protection/fault-current release input.
    f("SAFETY_24V", [pad_point("JWP1", "1"), (30.0, 43.0), (72.0, 43.0), (93.0375, 43.0), pad_point("CDRV1", "1")], 0.75)
    f("SAFETY_24V", [pad_point("TP1", "1"), (72.0, 43.0)], 0.75)
    f("SAFETY_24V", [pad_point("DC1", "1"), (50.0, 43.0)], 0.75)
    f("SAFETY_24V", [pad_point("CDRV1", "1"), (96.5, 39.0), (96.5, 36.275), pad_point("UDRV1", "9")], 0.25)
    f("SAFETY_24V", [(93.0375, 43.0), (125.0375, 43.0), pad_point("CDRV2", "1")], 0.75)
    f("SAFETY_24V", [pad_point("CDRV2", "1"), (128.5, 39.0), (128.5, 36.275), pad_point("UDRV2", "9")], 0.25)
    f("WD1_COIL_N", [pad_point("JWP1", "3"), (37.0, 27.0), (74.0, 27.0), (96.5, 27.0), (96.5, 31.725)], 0.75)
    f("WD1_COIL_N", [pad_point("TP9", "1"), (74.0, 27.0)], 0.75)
    f("WD1_COIL_N", [(96.5, 31.725), pad_point("UDRV1", "16")], FAB_TRACE_MIN_MM)
    b("WD2_COIL_N", [pad_point("JWP1", "4"), (40.5, 24.0), (128.5, 24.0), (128.5, 29.5)], 0.75)
    f("WD2_COIL_N", [pad_point("TP10", "1"), (108.0, 24.0)], 0.75)
    via("WD2_COIL_N", (108.0, 24.0), 1.0, 0.5)
    via("WD2_COIL_N", (128.5, 29.5), 1.0, 0.5)
    f("WD2_COIL_N", [(128.5, 29.5), (128.5, 31.725)], 0.25)
    f("WD2_COIL_N", [(128.5, 31.725), pad_point("UDRV2", "16")], FAB_TRACE_MIN_MM)

    # Two independent logic-drive routes. Channel 2 changes layer briefly to
    # cross channel 1 without a same-layer junction.
    f("WD1_DRIVE", [pad_point("WDCTRL1", "5"), (46.03, 85.0)])
    via("WD1_DRIVE", (46.03, 85.0))
    via("WD1_DRIVE", (84.0, 29.5))
    b("WD1_DRIVE", [(46.03, 85.0), (46.03, 48.0), (78.0, 48.0), (84.0, 48.0), (84.0, 29.5)])
    f("WD1_DRIVE", [pad_point("TP7", "1"), (78.0, 48.0)])
    via("WD1_DRIVE", (78.0, 48.0))
    f("WD1_DRIVE", [(84.0, 29.5), (87.0, 29.5), pad_point("UDRV1", "1")])
    f("WD2_DRIVE", [pad_point("WDCTRL1", "6"), (48.57, 86.5)])
    via("WD2_DRIVE", (48.57, 86.5))
    via("WD2_DRIVE", (116.0, 29.5))
    b("WD2_DRIVE", [(48.57, 86.5), (48.57, 50.0), (108.0, 50.0), (116.0, 50.0), (116.0, 29.5)])
    f("WD2_DRIVE", [pad_point("TP8", "1"), (108.0, 50.0)])
    via("WD2_DRIVE", (108.0, 50.0))
    f("WD2_DRIVE", [(116.0, 29.5), (119.0, 29.5), pad_point("UDRV2", "1")])

    # ISO1212 field-input clusters. These front-copper trees preserve the
    # machine-checked high-voltage and decoupling placement constraints.
    f("FB_IN1", [pad_point("UFB1", "15"), (104.5, 74.412), (106.0, 74.5), pad_point("RSN1", "2")])
    f("FB_IN2", [pad_point("UFB1", "10"), (104.5, 77.588), (106.0, 79.5), pad_point("RSN2", "2")])
    f("FB_SENSE1", [pad_point("UFB1", "16"), (104.5, 73.778), (104.5, 70.862), pad_point("CFI1", "1")])
    f("FB_SENSE1", [pad_point("CFI1", "1"), (106.0, 72.5), pad_point("RSN1", "1"), (115.0, 72.5), pad_point("RTH1", "2")])
    f("FB_SENSE2", [pad_point("UFB1", "11"), (105.5, 76.953)], FAB_TRACE_MIN_MM)
    via("FB_SENSE2", (105.5, 76.953), 0.6, 0.3)
    via("FB_SENSE2", (105.5, 80.138), 0.6, 0.3)
    b("FB_SENSE2", [(105.5, 76.953), (105.5, 80.138)], FAB_TRACE_MIN_MM)
    f("FB_SENSE2", [(105.5, 80.138), pad_point("CFI2", "1")], FAB_TRACE_MIN_MM)
    f("FB_SENSE2", [pad_point("CFI2", "1"), (107.0, 80.138), (107.0, 83.0), (115.0, 83.0), (115.0, 77.5), pad_point("RSN2", "1")], FAB_TRACE_MIN_MM)
    f("FB_SENSE2", [(115.0, 77.5), (115.0, 82.0), pad_point("RTH2", "2")])
    f("WD1_NC_24V", [pad_point("RTH1", "1"), pad_point("RW1", "1"), (132.0, 68.0)], 0.5)
    via("WD1_NC_24V", (132.0, 68.0), 1.0, 0.5)
    via("WD1_NC_24V", (147.0, 74.0), 1.0, 0.5)
    b("WD1_NC_24V", [(132.0, 68.0), (142.0, 68.0), (147.0, 68.0), (147.0, 74.0)], 0.5)
    f("WD1_NC_24V", [pad_point("TP11", "1"), (150.0, 68.0), (147.0, 68.0)], 0.5)
    via("WD1_NC_24V", (147.0, 68.0), 1.0, 0.5)
    f("WD1_NC_24V", [(147.0, 74.0), pad_point("JWF1", "1")], 0.5)
    f("WD2_NC_24V", [pad_point("RTH2", "1"), pad_point("RW2", "1"), (132.0, 84.0)], 0.5)
    via("WD2_NC_24V", (132.0, 84.0), 1.0, 0.5)
    via("WD2_NC_24V", (160.0, 82.0), 1.0, 0.5)
    b("WD2_NC_24V", [(132.0, 84.0), (142.0, 84.0), (160.0, 84.0), (160.0, 82.0)], 0.5)
    f("WD2_NC_24V", [pad_point("TP12", "1"), (162.0, 84.0), (160.0, 84.0)], 0.5)
    via("WD2_NC_24V", (160.0, 84.0), 1.0, 0.5)
    f("WD2_NC_24V", [(160.0, 82.0), (160.0, 76.0), pad_point("JWF1", "2")], 0.5)

    # Receiver outputs use B.Cu hops around the package, then local front
    # networks and separate B.Cu returns to the Pico feedback inputs.
    for net_name, ufb_pin, rso_ref, near_via, far_via, corridor_y in (
        ("UFB_OUT1", "4", "RSO1", (93.0, 75.683), (86.0, 64.0), 75.683),
        ("UFB_OUT2", "5", "RSO2", (94.0, 76.3175), (86.0, 84.0), 77.0),
    ):
        f(net_name, [pad_point("UFB1", ufb_pin), near_via], FAB_TRACE_MIN_MM)
        via(net_name, near_via)
        via(net_name, far_via)
        b(net_name, [near_via, (near_via[0], corridor_y), (86.0, corridor_y), far_via])
        f(net_name, [far_via, pad_point(rso_ref, "1")])
    f("UFB_OUT1", [(86.0, 64.0), (86.0, 58.0), pad_point("TP13", "1")])
    via("UFB_OUT2", (86.0, 92.0))
    b("UFB_OUT2", [(86.0, 84.0), (86.0, 92.0)])
    f("UFB_OUT2", [(86.0, 92.0), pad_point("TP14", "1")])
    f("WD_SWDIO", [pad_point("WDCTRL1", "D3"), (88.0, 69.46)])
    via("WD_SWDIO", (88.0, 69.46))
    via("WD_SWDIO", (96.0, 60.0))
    b("WD_SWDIO", [(88.0, 69.46), (96.0, 60.0)])
    f("WD_SWDIO", [(96.0, 60.0), pad_point("TP15", "1")])
    f("WD_SWCLK", [pad_point("WDCTRL1", "D1"), (86.0, 74.54), (86.0, 78.0), pad_point("TP16", "1")])
    f("WD1_NC_DIAG", [pad_point("RSO1", "2"), pad_point("RPD1", "1"), (82.0, 68.0)])
    via("WD1_NC_DIAG", (82.0, 68.0))
    f("WD1_NC_DIAG", [pad_point("WDCTRL1", "9"), (56.0, 79.0)])
    via("WD1_NC_DIAG", (56.0, 79.0))
    b("WD1_NC_DIAG", [(82.0, 68.0), (82.0, 92.0), (56.0, 92.0), (56.0, 79.0)])
    f("WD2_NC_DIAG", [pad_point("RSO2", "2"), pad_point("RPD2", "1"), (84.0, 88.0)])
    via("WD2_NC_DIAG", (84.0, 88.0))
    f("WD2_NC_DIAG", [pad_point("WDCTRL1", "10"), (60.0, 79.0)])
    via("WD2_NC_DIAG", (84.0, 96.0))
    via("WD2_NC_DIAG", (60.0, 96.0))
    b("WD2_NC_DIAG", [(84.0, 88.0), (84.0, 96.0)])
    f("WD2_NC_DIAG", [(84.0, 96.0), (60.0, 96.0)])
    b("WD2_NC_DIAG", [(60.0, 96.0), (60.0, 93.5)])
    via("WD2_NC_DIAG", (60.0, 93.5))
    f("WD2_NC_DIAG", [(60.0, 93.5), (60.0, 79.0)])

    # Local safety-return fan-outs into a provisional B.Cu plane. No via is
    # placed in an SMD pad. Adjacent TPL7407L ground pins are first stitched on
    # front copper.
    for driver_ref, cap_ref, via_point in (("UDRV1", "CDRV1", (87.0, 38.0)), ("UDRV2", "CDRV2", (119.0, 38.0))):
        driver_points = [pad_point(driver_ref, str(number)) for number in range(2, 9)]
        f("SAFETY_0V", driver_points, 0.25)
        f("SAFETY_0V", [driver_points[-1], via_point], 0.25)
        f("SAFETY_0V", [pad_point(cap_ref, "2"), via_point], 0.25)
        via("SAFETY_0V", via_point, 1.0, 0.5)
    for reference, number, via_point in (
        ("WDCTRL1", "38", (40.95, 65.5)), ("WDCTRL1", "D2", (83.5, 72.0)),
        ("RPD1", "2", (93.5, 68.0)), ("RPD2", "2", (93.5, 88.0)),
        ("CFI1", "2", (106.0, 68.5)), ("CFI2", "2", (106.0, 82.5)),
        ("RW1", "2", (141.5, 65.5)), ("RW2", "2", (141.5, 86.5)),
    ):
        f("SAFETY_0V", [pad_point(reference, number), via_point], 0.5)
        via("SAFETY_0V", via_point, 1.0, 0.5)
    f("SAFETY_0V", [pad_point("CDEC1", "2"), (92.0, 72.55)], FAB_TRACE_MIN_MM)
    via("SAFETY_0V", (92.0, 72.55), 0.8, 0.4)
    for ufb_pin, via_point in (("1", (100.0, 70.5)), ("8", (95.0, 79.5)), ("14", (104.0, 75.0475)), ("9", (103.2, 83.5))):
        if ufb_pin == "9":
            f("SAFETY_0V", [pad_point("UFB1", ufb_pin), (103.2, 78.222), via_point], FAB_TRACE_MIN_MM)
        else:
            f("SAFETY_0V", [pad_point("UFB1", ufb_pin), via_point], FAB_TRACE_MIN_MM)
        if ufb_pin == "14":
            via("SAFETY_0V", via_point, 0.6, 0.3)
        else:
            via("SAFETY_0V", via_point, 0.8, 0.4)
    f("SAFETY_0V", [pad_point("ISO1", "3"), (70.0, 109.27), (70.0, 102.5)], 0.5)
    via("SAFETY_0V", (70.0, 102.5), 1.0, 0.5)
    f("SAFETY_0V", [pad_point("TP2", "1"), (76.0, 38.5)], 0.5)
    via("SAFETY_0V", (76.0, 38.5), 1.0, 0.5)

    # TI ISO1212 Rev G recommends a separate, floating 2 mm x 2 mm plane for
    # each exposed SUB pin. These two nets remain isolated from each other and
    # from both field and logic grounds; the copper is thermal-only.
    f("INTENTIONALLY_UNUSED_UFB1_13", [pad_point("UFB1", "13"), (104.0, 75.6825), (105.0, 75.2)], FAB_TRACE_MIN_MM)
    via("INTENTIONALLY_UNUSED_UFB1_13", (105.0, 75.2), 0.6, 0.3)
    b("INTENTIONALLY_UNUSED_UFB1_13", [(105.0, 75.2), (112.0, 75.2)], 0.2)
    add_floating_plane(pcbnew, board, nets["INTENTIONALLY_UNUSED_UFB1_13"], (112.0, 75.2))
    f("INTENTIONALLY_UNUSED_UFB1_12", [pad_point("UFB1", "12"), (104.5, 76.3175)], FAB_TRACE_MIN_MM)
    via("INTENTIONALLY_UNUSED_UFB1_12", (104.5, 76.3175), 0.6, 0.3)
    b("INTENTIONALLY_UNUSED_UFB1_12", [(104.5, 76.3175), (104.0, 80.5), (108.0, 82.0), (108.0, 88.0), (112.0, 88.0)], 0.2)
    add_floating_plane(pcbnew, board, nets["INTENTIONALLY_UNUSED_UFB1_12"], (112.0, 88.0))
    add_ground_zone(pcbnew, board, nets["SAFETY_0V"])


def main() -> int:
    try:
        import pcbnew
    except ImportError:
        print("Run with KiCad's bundled Python so pcbnew is available.", file=sys.stderr)
        return 3

    model = load_model()
    components = {
        comp.ref: comp
        for sheet in model.sheets()
        for comp in sheet.components
        if comp.watchdog_pcb
    }
    if set(components) != set(PLACEMENTS):
        missing = sorted(set(components) - set(PLACEMENTS))
        extra = sorted(set(PLACEMENTS) - set(components))
        raise RuntimeError(f"placement/model mismatch; missing={missing}, extra={extra}")

    board = pcbnew.BOARD()
    board.SetFileName(str(BOARD_PATH))
    title = board.GetTitleBlock()
    title.SetTitle("Project Button HR-V0 ordinary watchdog PCB routed/test-access candidate")
    title.SetDate("2026-08-09")
    title.SetRevision("PCB-P0.9 / Electrical V3-P1.14")
    title.SetCompany("Project Button")
    title.SetComment(0, WARNING)
    title.SetComment(1, "ROUTED/TEST-ACCESS CANDIDATE - NO GERBER RELEASE")
    default_class = pcbnew.NETCLASS("Default")
    default_class.SetClearance(pcbnew.FromMM(FAB_CLEARANCE_MIN_MM))
    default_class.SetTrackWidth(pcbnew.FromMM(0.25))
    default_class.SetViaDiameter(pcbnew.FromMM(0.8))
    default_class.SetViaDrill(pcbnew.FromMM(0.4))
    board.GetNetClasses()["Default"] = default_class
    board.GetDesignSettings().m_TrackMinWidth = pcbnew.FromMM(FAB_TRACE_MIN_MM)
    power_class = pcbnew.NETCLASS("POWER24")
    power_class.SetClearance(pcbnew.FromMM(FAB_CLEARANCE_MIN_MM))
    power_class.SetTrackWidth(pcbnew.FromMM(0.75))
    power_class.SetViaDiameter(pcbnew.FromMM(1.0))
    power_class.SetViaDrill(pcbnew.FromMM(0.5))
    board.GetNetClasses()["POWER24"] = power_class

    nets = {}
    for name in sorted({pin.net for comp in components.values() for pin in comp.pins}):
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    for name in ("SAFETY_24V", "WD1_COIL_N", "WD2_COIL_N"):
        nets[name].SetNetClass(power_class)

    for ref, comp in components.items():
        lib, name = footprint_location(comp.footprint)
        footprint = pcbnew.FootprintLoad(str(lib), name)
        if footprint is None:
            raise RuntimeError(f"cannot load {comp.footprint} for {ref}")
        footprint.SetReference(ref)
        footprint.SetValue(comp.value)
        apply_metadata(footprint)
        x, y, rotation = PLACEMENTS[ref]
        footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        footprint.SetOrientationDegrees(rotation)
        pad_by_number = {pad.GetNumber(): pad for pad in footprint.Pads() if pad.GetNumber()}
        expected = {pin.number: pin.net for pin in comp.pins}
        absent = sorted(set(expected) - set(pad_by_number))
        if absent:
            raise RuntimeError(f"{ref} footprint lacks modeled pads {absent}")
        for number, net_name in expected.items():
            pad_by_number[number].SetNet(nets[net_name])
        if ref.startswith("TP"):
            footprint.Reference().SetVisible(False)
        board.Add(footprint)

    add_outline(pcbnew, board)
    add_mounting_holes(pcbnew, board)
    route_board(pcbnew, board, nets)
    add_text(pcbnew, board, WARNING, 35, 116.5, 1.35, pcbnew.F_SilkS)
    add_text(pcbnew, board, "PCB-P0.7 - HARWIN LAND SHAPE CORRECTION - NO SAFETY CREDIT", 80, 112, 1.2, pcbnew.F_SilkS)
    add_text(pcbnew, board, "+24  0V  C1-  C2-", 25, 42, 1.1, pcbnew.F_SilkS)
    add_text(pcbnew, board, "FB1  FB2", 143, 69, 1.1, pcbnew.F_SilkS)
    add_text(pcbnew, board, "HB   COMPUTE-0V", 25, 101.5, 1.1, pcbnew.F_SilkS)
    for ref, label in TESTPOINT_LABELS.items():
        x, y, _ = PLACEMENTS[ref]
        label_x, label_y = TESTPOINT_LABEL_POSITIONS.get(ref, (x + 2.0, y - 1.0))
        add_text(pcbnew, board, label, label_x, label_y, 0.8, pcbnew.F_SilkS)

    pcbnew.SaveBoard(str(BOARD_PATH), board)

    project_path = OUT / "project-button-v3.kicad_pro"
    project = json.loads(project_path.read_text(encoding="utf-8-sig"))
    classes = project.setdefault("net_settings", {}).setdefault("classes", [])
    default = next((item for item in classes if item.get("name") == "Default"), None)
    if default is None:
        default = {"name": "Default", "priority": 2147483647}
        classes.append(default)
    default.update({"clearance": FAB_CLEARANCE_MIN_MM, "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4})
    power = next((item for item in classes if item.get("name") == "POWER24"), None)
    if power is None:
        power = {"name": "POWER24", "priority": 1}
        classes.append(power)
    power.update({"clearance": FAB_CLEARANCE_MIN_MM, "track_width": 0.75, "via_diameter": 1.0, "via_drill": 0.5})
    project["net_settings"]["netclass_assignments"] = {
        name: "POWER24" for name in ("SAFETY_24V", "WD1_COIL_N", "WD2_COIL_N")
    }
    project_path.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")

    validation = OUT / "validation"
    output = OUT / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    cli = KICAD_ROOT / "bin" / "kicad-cli.exe"
    commands = [
        [str(cli), "pcb", "drc", "--refill-zones", "--save-board", "--output", str(validation / "project-button-v3-pcb-test-access-drc.rpt"), str(BOARD_PATH)],
        [str(cli), "pcb", "render", "--output", str(output / "project-button-v3-pcb-test-access-top.png"), "--width", "1800", "--height", "1100", "--side", "top", "--background", "opaque", str(BOARD_PATH)],
        [str(cli), "pcb", "render", "--output", str(output / "project-button-v3-pcb-test-access-bottom.png"), "--width", "1800", "--height", "1100", "--side", "bottom", "--background", "opaque", str(BOARD_PATH)],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        combined = "\n".join(line.rstrip() for line in (result.stdout + result.stderr).splitlines())
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + combined + f"\nexit={result.returncode}\n")
    (validation / "project-button-v3-pcb-test-access-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (OUT / "project-button-v3.kicad_prl").unlink(missing_ok=True)
    model.manifest()
    print(f"Generated {BOARD_PATH}")
    print(f"Board-mounted schematic references: {len(components)}")
    print(WARNING)
    print("This routed/test-access candidate has no fabrication release; DRC and connectivity evidence are review inputs only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
