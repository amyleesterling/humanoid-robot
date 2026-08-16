#!/usr/bin/env python3
"""Generate the HR-30 STDC14-to-JDBG1 SWD adapter candidate.

The output is a native two-sheet KiCad project, routed two-layer PCB, exact
project-owned Samtec footprint, manufacturing-candidate exports, contact map,
cable drawing, inspection traveller and human-readable web guide.  It is a
debug fixture only and grants no connection, powered-test, motion or
energization authority.
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
from dataclasses import dataclass
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "swd-adapter-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "swd-adapter-p0.1"
PROJECT = "hr30-swd-adapter-p0.1"
IDENTIFIER = "HR30-SWD-ADAPTER-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
FP_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

ST_UM2910 = "https://www.st.com/resource/en/user_manual/um2910-stlinkv3minie-debuggerprogrammer-tiny-probe-for-stm32-microcontrollers-stmicroelectronics.pdf"
ARM_IHI0029 = "https://documentation-service.arm.com/static/63a03a981d698c4dc521ca77"
SAMTEC_PRINT = "https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-xxx-x-xx-mkt.pdf"
SAMTEC_FOOTPRINT = "https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf"
JST_GH = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"


@dataclass(frozen=True)
class Part:
    ref: str
    value: str
    manufacturer: str
    mpn: str
    footprint: str
    pins: dict[str, str]
    x: float
    y: float
    rotation: float = 0.0
    source: str = ""
    evidence: str = ""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_swd_adapter_model", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.OUT = OUT
    model.PROJECT = PROJECT
    model.REV = "P0.1"
    model.DATE = DATE
    model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 SWD ADAPTER"
    model.PROJECT_SUBTITLE = "STDC14 to JDBG1 passive debug fixture; target-powered reference only."
    return model


def parts() -> list[Part]:
    j1 = {
        "1": "INTENTIONALLY_NOT_CONNECTED_J1_1",
        "2": "INTENTIONALLY_NOT_CONNECTED_J1_2",
        "3": "CTRL_3V3",
        "4": "SWDIO",
        "5": "CTRL_GND",
        "6": "SWCLK",
        "7": "CTRL_GND",
        "8": "INTENTIONALLY_NOT_CONNECTED_J1_8",
        "9": "INTENTIONALLY_NOT_CONNECTED_J1_9",
        "10": "INTENTIONALLY_NOT_CONNECTED_J1_10",
        "11": "CTRL_GND",
        "12": "MCU_NRST",
        "13": "INTENTIONALLY_NOT_CONNECTED_J1_13",
        "14": "INTENTIONALLY_NOT_CONNECTED_J1_14",
    }
    j2 = {"1": "CTRL_GND", "2": "CTRL_3V3", "3": "SWDIO", "4": "SWCLK", "5": "MCU_NRST"}
    return [
        Part(
            "J1", "STDC14 target header", "Samtec", "FTSH-107-01-L-DV-K-A",
            "HR30_SWD:FTSH-107-01-L-DV-K-A", j1, 8.0, 10.0, 0.0,
            ST_UM2910,
            "UM2910 Rev 5 Table 4 names the exact keyed/alignment-pin header; Samtec Rev H land pattern and Rev FX product print control the local footprint.",
        ),
        Part(
            "J2", "HR-30 JDBG1 cable header", "JST", "BM05B-GHS-TBT",
            "Connector_JST:JST_GH_BM05B-GHS-TBT_1x05-1MP_P1.25mm_Vertical", j2, 24.0, 10.0, 90.0,
            JST_GH,
            "Exact five-contact JST GH board header already bound at motion-controller JDBG1; contact order is project-controlled.",
        ),
    ]


def write_custom_footprint() -> None:
    library = OUT / "HR30_SWD.pretty"
    library.mkdir(parents=True, exist_ok=True)
    pads = []
    for position in range(7):
        x = -3.81 + position * 1.27
        odd = 1 + position * 2
        even = odd + 1
        pads.append(f'  (pad "{odd}" smd roundrect (at {x:.2f} 2.035) (size 0.74 2.79) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.12))')
        pads.append(f'  (pad "{even}" smd roundrect (at {x:.2f} -2.035) (size 0.74 2.79) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.12))')
    footprint = f'''(footprint "FTSH-107-01-L-DV-K-A"
  (version 20240108)
  (generator "project-button")
  (layer "F.Cu")
  (descr "Samtec FTSH-107-01-L-DV-K-A; Rev H recommended PCB layout; 14 contacts; keyed; molded alignment pins")
  (tags "STDC14 Samtec FTSH 1.27mm keyed alignment")
  (property "Reference" "REF**" (at 0 -4.9 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "FTSH-107-01-L-DV-K-A" (at 0 4.9 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
  (attr smd)
  (fp_rect (start -4.445 -1.715) (end 4.445 1.715) (stroke (width 0.10) (type solid)) (fill no) (layer "F.Fab"))
  (fp_line (start -4.55 -1.82) (end -4.55 1.82) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))
  (fp_line (start 4.55 -1.82) (end 4.55 1.82) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))
  (fp_rect (start -4.95 -3.75) (end 4.95 3.75) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
{chr(10).join(pads)}
  (pad "" np_thru_hole circle (at -3.175 0) (size 1.02 1.02) (drill 1.02) (layers "*.Cu" "*.Mask"))
  (pad "" np_thru_hole circle (at 3.175 0) (size 1.02 1.02) (drill 1.02) (layers "*.Cu" "*.Mask"))
  (embedded_fonts no)
)
'''
    (library / "FTSH-107-01-L-DV-K-A.kicad_mod").write_text(footprint, encoding="utf-8")


def schematic_component(model, part: Part):
    pins = []
    for index, (number, net) in enumerate(part.pins.items()):
        side = "left" if index % 2 == 0 else "right"
        name = {
            "1": "RESERVED / NC" if part.ref == "J1" else "CTRL_GND",
            "2": "RESERVED / NC" if part.ref == "J1" else "CTRL_3V3 / VTREF",
            "3": "T_VCC" if part.ref == "J1" else "SWDIO",
            "4": "SWDIO" if part.ref == "J1" else "SWCLK",
            "5": "GND" if part.ref == "J1" else "MCU_NRST",
            "6": "SWCLK", "7": "GND", "8": "SWO / NC", "9": "RESERVED / NC",
            "10": "JTDI / NC", "11": "GNDDETECT", "12": "NRST", "13": "VCP_RX / NC", "14": "VCP_TX / NC",
        }.get(number, number)
        pins.append(model.pn(part.ref, number, name, net, side))
    return model.Component(
        part.ref, part.value, pins,
        "EXACT CONNECTOR CANDIDATE - PHYSICAL/DFM/RECEIVING VALIDATION OPEN",
        part.evidence, part.source, part.evidence,
        position=(82 if part.ref == "J1" else 250, 92), width=102 if part.ref == "J1" else 86,
        footprint=part.footprint,
    )


def write_schematic(items: list[Part]) -> None:
    model = load_model()
    components = [schematic_component(model, part) for part in items]
    sheet = model.Sheet(1, "01_swd_adapter.kicad_sch", "STDC14 to HR-30 JDBG1 passive adapter", "Exact contact map; no target power source; unused STDC14 functions remain explicit no-connects.")
    sheet.components = components
    sheet.notes = [
        "STDC14 pin 3 senses the already-powered target CTRL_3V3 rail; STLINK-V3MINIE does not supply target power.",
        "STDC14 pin 11 GNDDETECT is tied to target signal ground following the Arm CoreSight 10 target convention.",
        "Pins 1, 2, 8, 9, 10, 13 and 14 remain no-connect; SWO, JTAG and VCP are outside P0.1.",
        WARNING,
    ]
    net_counts: dict[str, int] = {}
    for component in components:
        for pin in component.pins:
            net_counts[pin.net] = net_counts.get(pin.net, 0) + 1
    wires = model.build_wire_numbers([sheet], net_counts)
    root_uuid = model.uid("root-hr30-swd-adapter-p0.1")
    project = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.15, "track_width": 0.20, "via_diameter": 0.60, "via_drill": 0.30}], "meta": {"version": 3}},
        "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING},
    }
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 SWD adapter symbols"))\n)\n', encoding="utf-8")
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "HR30_SWD")(type "KiCad")(uri "${KIPRJMOD}/HR30_SWD.pretty")(options "")(descr "Project-owned Samtec STDC14 footprint"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, [sheet]), encoding="utf-8")
    (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wires), encoding="utf-8")


def library_footprint(identifier: str):
    library, name = identifier.split(":", 1)
    base = OUT if library == "HR30_SWD" else FP_ROOT
    folder = base / f"{library}.pretty"
    footprint = pcbnew.FootprintLoad(str(folder), name)
    if footprint is None:
        raise RuntimeError(f"cannot load footprint {identifier}")
    return footprint


def add_track(board: pcbnew.BOARD, net, points: list[tuple[float, float]], layer: int, width: float = 0.22) -> None:
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I_MM(*start)); track.SetEnd(pcbnew.VECTOR2I_MM(*end))
        track.SetLayer(layer); track.SetWidth(pcbnew.FromMM(width)); track.SetNet(net); board.Add(track)


def add_via(board: pcbnew.BOARD, net, point: tuple[float, float]) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(0.60)); via.SetDrill(pcbnew.FromMM(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def add_text(board: pcbnew.BOARD, value: str, x: float, y: float, size: float, layer: int = pcbnew.F_SilkS) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value); item.SetPosition(pcbnew.VECTOR2I_MM(x, y)); item.SetLayer(layer)
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); item.SetTextThickness(pcbnew.FromMM(max(0.15, size * 0.14)))
    if layer == pcbnew.B_SilkS:
        item.SetMirrored(True)
    board.Add(item)


def pad_xy(footprint, number: str) -> tuple[float, float]:
    pads = [pad for pad in footprint.Pads() if pad.GetNumber() == number]
    if len(pads) != 1:
        raise RuntimeError(f"expected one pad {footprint.GetReference()}.{number}, found {len(pads)}")
    point = pads[0].GetPosition()
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def write_board(items: list[Part]) -> dict[str, object]:
    board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(1.6))
    settings.m_MinClearance = pcbnew.FromMM(0.15); settings.m_TrackMinWidth = pcbnew.FromMM(0.18)
    settings.m_HoleClearance = pcbnew.FromMM(0.20); settings.m_HoleToHoleMin = pcbnew.FromMM(0.25)
    settings.m_ViasMinSize = pcbnew.FromMM(0.55); settings.m_MinThroughDrill = pcbnew.FromMM(0.25)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.12)
    settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.15))
    names = ("CTRL_GND", "CTRL_3V3", "SWDIO", "SWCLK", "MCU_NRST")
    nets = {}
    for name in names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    footprints = {}
    for part in items:
        footprint = library_footprint(part.footprint)
        footprint.SetReference(part.ref); footprint.SetValue(part.mpn)
        footprint.SetPosition(pcbnew.VECTOR2I_MM(part.x, part.y)); footprint.SetOrientationDegrees(part.rotation)
        footprint.Reference().SetVisible(False); footprint.Value().SetVisible(False)
        for pad in footprint.Pads():
            net_name = part.pins.get(pad.GetNumber(), "")
            if net_name in nets:
                pad.SetNet(nets[net_name])
        board.Add(footprint); footprints[part.ref] = footprint
    for index, point in enumerate(((2.5, 2.5), (29.5, 17.5)), 1):
        hole = library_footprint("MountingHole:MountingHole_2.7mm_M2.5")
        hole.SetReference(f"H{index}"); hole.SetValue("M2.5 FIXTURE HOLE - MECHANICAL VALIDATION OPEN")
        hole.SetPosition(pcbnew.VECTOR2I_MM(*point)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True)
        hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    corners = ((0, 0), (32, 0), (32, 20), (0, 20))
    for start, end in zip(corners, (*corners[1:], corners[0])):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(pcbnew.VECTOR2I_MM(*start)); edge.SetEnd(pcbnew.VECTOR2I_MM(*end)); edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)

    j1, j2 = footprints["J1"], footprints["J2"]
    p = {f"J1.{n}": pad_xy(j1, n) for n in ("3", "4", "6", "12")}
    p.update({f"J2.{n}": pad_xy(j2, n) for n in ("2", "3", "4", "5")})
    # SWDIO stays on the component side and deliberately runs around the left
    # and lower connector perimeter.  This leaves three short, non-crossing
    # component-side fan-outs to rear-layer vias for the other signals.
    add_track(board, nets["SWDIO"], [p["J1.4"], (5.46, 5.20), (3.40, 5.20), (3.40, 15.50), (20.00, 15.50), (20.00, p["J2.3"][1]), p["J2.3"]], pcbnew.F_Cu)
    # The reference, clock and reset each use a separate rear-layer corridor.
    # T_VCC remains a sense signal, never an adapter power output.
    tvcc_a, tvcc_b = (p["J1.3"][0], 14.20), (24.50, p["J2.2"][1])
    add_track(board, nets["CTRL_3V3"], [p["J1.3"], tvcc_a], pcbnew.F_Cu)
    add_via(board, nets["CTRL_3V3"], tvcc_a)
    add_track(board, nets["CTRL_3V3"], [tvcc_a, (tvcc_a[0], 16.50), (24.50, 16.50), tvcc_b], pcbnew.B_Cu)
    add_via(board, nets["CTRL_3V3"], tvcc_b)
    add_track(board, nets["CTRL_3V3"], [tvcc_b, p["J2.2"]], pcbnew.F_Cu)
    swclk_a, swclk_b = (p["J1.6"][0], 5.80), (22.50, p["J2.4"][1])
    add_track(board, nets["SWCLK"], [p["J1.6"], swclk_a], pcbnew.F_Cu)
    add_via(board, nets["SWCLK"], swclk_a)
    add_track(board, nets["SWCLK"], [swclk_a, (22.50, swclk_a[1]), swclk_b], pcbnew.B_Cu)
    add_via(board, nets["SWCLK"], swclk_b)
    add_track(board, nets["SWCLK"], [swclk_b, p["J2.4"]], pcbnew.F_Cu)
    nrst_a, nrst_b = (p["J1.12"][0], 4.20), (23.50, p["J2.5"][1])
    add_track(board, nets["MCU_NRST"], [p["J1.12"], nrst_a], pcbnew.F_Cu)
    add_via(board, nets["MCU_NRST"], nrst_a)
    add_track(board, nets["MCU_NRST"], [nrst_a, (23.50, nrst_a[1]), nrst_b], pcbnew.B_Cu)
    add_via(board, nets["MCU_NRST"], nrst_b)
    add_track(board, nets["MCU_NRST"], [nrst_b, p["J2.5"]], pcbnew.F_Cu)
    ground = pcbnew.ZONE(board); ground.SetLayer(pcbnew.F_Cu); ground.SetNet(nets["CTRL_GND"]); ground.SetLocalClearance(pcbnew.FromMM(0.18)); ground.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    outline = ground.Outline(); outline.NewOutline()
    for point in ((0.5, 0.5), (31.5, 0.5), (31.5, 19.5), (0.5, 19.5)):
        outline.Append(pcbnew.VECTOR2I_MM(*point))
    board.Add(ground); pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    add_text(board, "SWD P0.1", 16.0, 18.0, 0.80)
    add_text(board, "1", 2.0, 14.6, 0.80)
    board_dir = OUT / "board"; board_dir.mkdir(parents=True, exist_ok=True)
    path = board_dir / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(path), board)
    return {"path": path, "named_nets": len(names), "component_count": len(items), "vias": 6}


def run_cli(args: list[object], allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run([str(KICAD), *map(str, args)], cwd=OUT, text=True, capture_output=True)
    if completed.returncode not in allowed:
        raise RuntimeError(f"KiCad failed {completed.returncode}: {' '.join(map(str, args))}\n{completed.stdout}\n{completed.stderr}")
    return completed


def validate_export(board_info: dict[str, object]) -> dict[str, object]:
    validation = OUT / "validation"; output = OUT / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc_report = validation / f"{PROJECT}-erc.rpt"
    erc = run_cli(["sch", "erc", "--exit-code-violations", "--output", erc_report, OUT / f"{PROJECT}.kicad_sch"], allowed=(0, 5))
    if erc.returncode:
        raise RuntimeError("SWD adapter schematic ERC must be 0/0")
    run_cli(["sch", "export", "svg", "--output", output, OUT / f"{PROJECT}.kicad_sch"])
    board = Path(board_info["path"]); drc_report = validation / f"{PROJECT}-drc.rpt"
    drc = run_cli(["pcb", "drc", "--severity-all", "--exit-code-violations", "--output", drc_report, board], allowed=(0, 5))
    if drc.returncode:
        raise RuntimeError(drc_report.read_text(encoding="utf-8"))
    run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{PROJECT}-front.svg", "--layers", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", "--fit-page-to-board", "--exclude-drawing-sheet", board])
    run_cli(["pcb", "export", "svg", "--mode-single", "--output", output / f"{PROJECT}-back.svg", "--layers", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", "--mirror", "--fit-page-to-board", "--exclude-drawing-sheet", board])
    fabrication = OUT / "fabrication-candidate-not-released"; gerber = fabrication / "gerber"; drill = fabrication / "drill"
    gerber.mkdir(parents=True, exist_ok=True); drill.mkdir(parents=True, exist_ok=True)
    run_cli(["pcb", "export", "gerbers", "--output", gerber, "--layers", "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts", "--precision", "6", "--check-zones", board])
    run_cli(["pcb", "export", "drill", "--output", drill, "--format", "excellon", "--drill-origin", "absolute", "--excellon-zeros-format", "decimal", "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "svg", "--generate-report", "--report-path", drill / f"{PROJECT}-drill-report.rpt", board])
    run_cli(["pcb", "export", "ipcd356", "--output", fabrication / f"{PROJECT}.d356", board])
    run_cli(["pcb", "export", "pos", "--output", fabrication / f"{PROJECT}-positions.csv", "--side", "both", "--format", "csv", "--units", "mm", board])
    run_cli(["pcb", "export", "stats", "--output", fabrication / f"{PROJECT}-board-stats.json", "--format", "json", "--units", "mm", board])
    for svg in OUT.rglob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    (fabrication / "README.txt").write_text(WARNING + "\n\nMachine-readable outputs are for DFM quotation and inspection only. They are not an order or fabrication release.\n", encoding="utf-8")
    return {"erc_errors": 0, "erc_warnings": 0, "drc_violations": 0, "unconnected_items": 0}


def cable_svg() -> str:
    rows = [
        ("1", "BLACK", "CTRL_GND", "J2.1", "JDBG1.1"),
        ("2", "RED", "CTRL_3V3 / VTREF", "J2.2", "JDBG1.2"),
        ("3", "BLUE", "SWDIO", "J2.3", "JDBG1.3"),
        ("4", "YELLOW", "SWCLK", "J2.4", "JDBG1.4"),
        ("5", "WHITE", "MCU_NRST", "J2.5", "JDBG1.5"),
    ]
    lines = []
    colors = {"BLACK": "#1f2937", "RED": "#c62828", "BLUE": "#0b63b6", "YELLOW": "#d69a00", "WHITE": "#f8fafc"}
    for index, (contact, color, signal, left, right) in enumerate(rows):
        y = 170 + index * 72
        lines.append(f'<line x1="300" y1="{y}" x2="980" y2="{y}" stroke="{colors[color]}" stroke-width="16"/><text x="325" y="{y-14}">{contact} {color} - {html.escape(signal)}</text><text x="90" y="{y+7}">{left}</text><text x="1010" y="{y+7}">{right}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="590" viewBox="0 0 1280 590" role="img" aria-labelledby="t d"><title id="t">HR-30 SWD service cable</title><desc id="d">Five straight-through conductors between adapter J2 and motion-controller JDBG1. Candidate finished length 200 millimetres. Exact wire order code remains selection required.</desc><style>text{{font:600 18px system-ui;fill:#12263a}}.h{{font-size:30px;font-weight:900}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}</style><rect width="1280" height="590" fill="#e7f7ff"/><text class="h" x="45" y="48">Five-contact SWD service cable - candidate 200 +/- 10 mm</text><text x="45" y="82">Two JST GHR-05V-S housings; SSHL-002T-P0.2 contacts; exact conductor order code and crimp process remain open.</text><rect class="box" x="60" y="120" width="210" height="400" rx="18"/><text x="95" y="150">Adapter J2</text><rect class="box" x="1000" y="120" width="220" height="400" rx="18"/><text x="1030" y="150">Controller JDBG1</text>{''.join(lines)}<text x="45" y="565">{html.escape(WARNING)}</text></svg>'''


def publish(items: list[Part], board_info: dict[str, object], validation: dict[str, object]) -> None:
    contact_rows = []
    role = {
        "1": "RESERVED - DO NOT CONNECT", "2": "RESERVED - DO NOT CONNECT", "3": "T_VCC / target reference sense",
        "4": "T_SWDIO", "5": "GND", "6": "T_SWCLK", "7": "GND", "8": "T_SWO - not used P0.1",
        "9": "RESERVED - DO NOT CONNECT", "10": "T_JTDI / NC for SWD", "11": "GNDDETECT - target ground",
        "12": "T_NRST", "13": "T_VCP_RX - not used P0.1", "14": "T_VCP_TX - not used P0.1",
    }
    for contact, net in items[0].pins.items():
        contact_rows.append({"adapter_connector": "J1", "contact": contact, "official_function": role[contact], "adapter_net": "NO CONNECT" if net.startswith("INTENTIONALLY_") else net, "destination": {"3": "J2.2", "4": "J2.3", "5": "J2.1", "6": "J2.4", "7": "J2.1", "11": "J2.1", "12": "J2.5"}.get(contact, "NONE"), "disposition": "CONNECTED" if not net.startswith("INTENTIONALLY_") else "EXPLICIT NO CONNECT", "warning": WARNING})
    write_csv(OUT / "contact-map.csv", list(contact_rows[0]), contact_rows)
    component_rows = [
        {"reference": part.ref, "item": part.value, "manufacturer": part.manufacturer, "manufacturer_part_number": part.mpn, "quantity": 1, "footprint": part.footprint, "selection_state": "EXACT CANDIDATE - PROCUREMENT/RECEIVING OPEN", "source": part.source, "warning": WARNING}
        for part in items
    ]
    component_rows += [
        {"reference": "PCB1", "item": "32 x 20 x 1.6 mm two-layer FR-4 adapter PCB", "manufacturer": "SELECTION REQUIRED", "manufacturer_part_number": "SELECTION REQUIRED", "quantity": 1, "footprint": "N/A", "selection_state": "NATIVE DESIGN PRESENT; FABRICATOR/FINISH/DFM OPEN", "source": "PROJECT NATIVE KICAD", "warning": WARNING},
        {"reference": "CBL1-H1/2", "item": "five-contact cable housings", "manufacturer": "JST", "manufacturer_part_number": "GHR-05V-S", "quantity": 2, "footprint": "N/A", "selection_state": "EXACT CANDIDATE - RECEIVING/CRIMP VALIDATION OPEN", "source": JST_GH, "warning": WARNING},
        {"reference": "CBL1-C1/10", "item": "GH crimp contacts", "manufacturer": "JST", "manufacturer_part_number": "SSHL-002T-P0.2", "quantity": 10, "footprint": "N/A", "selection_state": "EXACT CANDIDATE - WIRE/TOOL/PULL TEST OPEN", "source": JST_GH, "warning": WARNING},
        {"reference": "CBL1-W1/5", "item": "stranded flex conductors, candidate finished cable 200 +/- 10 mm", "manufacturer": "SELECTION REQUIRED", "manufacturer_part_number": "SELECTION REQUIRED", "quantity": 5, "footprint": "N/A", "selection_state": "WIRE ORDER CODE/GAUGE/INSULATION SELECTION REQUIRED", "source": JST_GH, "warning": WARNING},
    ]
    write_csv(OUT / "adapter-bom.csv", list(component_rows[0]), component_rows)
    source_rows = [
        {"source_id": "SWD-S01", "manufacturer": "STMicroelectronics", "document": "UM2910 STLINK-V3MINIE user manual", "revision_or_date": "Rev 5; document history through 2025-03-25", "accessed": DATE, "url": ST_UM2910, "verified_use": "CN4 Table 4 pinout; exact FTSH-107-01-L-DV-K-A; target voltage is input; reserved pins 1/2 target no-connect"},
        {"source_id": "SWD-S02", "manufacturer": "Arm", "document": "CoreSight Architecture Specification", "revision_or_date": "ARM IHI 0029F; ID022122; 2022", "accessed": DATE, "url": ARM_IHI0029, "verified_use": "CoreSight 10 target connector pinout; VTref sense; signal ground and GNDDetect target convention"},
        {"source_id": "SWD-S03", "manufacturer": "Samtec", "document": "FTSH double-vertical surface-mount recommended PCB layout", "revision_or_date": "Revision H; 2019-08-27", "accessed": DATE, "url": SAMTEC_FOOTPRINT, "verified_use": "0.74 x 2.79 mm lands; 1.27 mm pitch; 6.86 mm row envelope; 1.02 mm -A alignment holes"},
        {"source_id": "SWD-S04", "manufacturer": "Samtec", "document": "FTSH double-vertical SMT terminal strip product print", "revision_or_date": "Revision FX; current official print", "accessed": DATE, "url": SAMTEC_PRINT, "verified_use": "-01 lead style; -K keying; -A molded alignment pins; 0.89 mm alignment-pin diameter"},
        {"source_id": "SWD-S05", "manufacturer": "JST", "document": "GH connector catalog", "revision_or_date": "live official catalog; revision not stated", "accessed": DATE, "url": JST_GH, "verified_use": "BM05B-GHS-TBT, GHR-05V-S and SSHL-002T-P0.2 candidate connector family"},
    ]
    write_csv(OUT / "primary-source-register.csv", list(source_rows[0]), source_rows)
    inspection = [
        ("SWD-I01", "Received identity", "J1 marking/order code, J2 marking, cable housings and contacts agree with BOM", "NOT EXECUTED"),
        ("SWD-I02", "Bare-board geometry", "32 x 20 mm outline, 1.6 mm nominal thickness, two 1.02 mm alignment holes and two 2.7 mm fixture holes measured", "NOT EXECUTED"),
        ("SWD-I03", "Pin-one orientation", "J1 key/notch and pin-one marker agree with ST CN4 top view and cable orientation", "NOT EXECUTED"),
        ("SWD-I04", "No-connect isolation", "J1.1/.2/.8/.9/.10/.13/.14 each >10 Mohm to every used net at inspection voltage", "NOT EXECUTED"),
        ("SWD-I05", "Continuity", "J1.3-J2.2; J1.4-J2.3; J1.6-J2.4; J1.12-J2.5 each <=0.5 ohm", "NOT EXECUTED"),
        ("SWD-I06", "Ground continuity", "J1.5/.7/.11 and J2.1 each <=0.5 ohm to one another", "NOT EXECUTED"),
        ("SWD-I07", "Cable continuity", "five straight-through contacts match cable drawing; zero adjacent-contact swaps", "NOT EXECUTED"),
        ("SWD-I08", "Cable pull/retention", "crimp height, visual acceptance and pull requirement accepted for selected wire/tool/process", "NOT EXECUTED"),
        ("SWD-I09", "Unpowered system check", "adapter+cable mapping reaches controller JDBG1 with actuator carriers physically absent", "NOT EXECUTED"),
    ]
    write_csv(OUT / "inspection-traveller.csv", ["step_id", "inspection", "acceptance", "result", "evidence", "warning"], [{"step_id": a, "inspection": b, "acceptance": c, "result": d, "evidence": "REQUIRED", "warning": WARNING} for a, b, c, d in inspection])
    holds = [
        ("SWD-H01", "qualified schematic/PCB/footprint review", "signed review against the five primary sources and native KiCad"),
        ("SWD-H02", "PCB fabrication/assembly", "received board, assembly workmanship and full inspection traveller"),
        ("SWD-H03", "cable wire and tooling", "exact wire order code, gauge, insulation, crimp tool/die, crimp-height and pull-test acceptance"),
        ("SWD-H04", "mechanical fit", "STDC14 cable key/alignment, JST latch access, strain relief and bench-fixture clearance"),
        ("SWD-H05", "target logic supply", "separately protected current-limited CTRL_5V/CTRL_3V3 source selection and approved no-actuator procedure"),
        ("SWD-H06", "physical bring-up", "all no-motion bring-up measurements, fault injections and HIL evidence"),
    ]
    write_csv(OUT / "open-holds.csv", ["hold_id", "unresolved_item", "closure_evidence", "state", "authority", "warning"], [{"hold_id": a, "unresolved_item": b, "closure_evidence": c, "state": "OPEN", "authority": "NO CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY", "warning": WARNING} for a, b, c in holds])
    (OUT / "cable-drawing.svg").write_text(cable_svg(), encoding="utf-8")
    status = {
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "native_kicad_schematic_sheet_count": 2, "native_kicad_board": True,
        "board_dimensions_mm": [32, 20, 1.6], "copper_layers": 2,
        "component_count": board_info["component_count"], "named_net_count": board_info["named_nets"], "via_count": board_info["vias"],
        **validation,
        "exact_stdc14_part_bound": True, "project_owned_stdc14_footprint": True,
        "gnddetect_tied_to_target_ground": True, "reserved_and_unused_contacts_explicit_no_connect": True,
        "cable_design_present": True, "cable_wire_selection_complete": False,
        "adapter_pcb_designed": True, "adapter_pcb_fabricated": False, "adapter_cable_built": False,
        "independent_review_complete": False, "physical_validation_complete": False,
        "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "adapter-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    fab_files = [path for path in (OUT / "fabrication-candidate-not-released").rglob("*") if path.is_file()]
    write_csv(OUT / "fabrication-candidate-register.csv", ["path", "bytes", "sha256", "release_state", "warning"], [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "release_state": "CANDIDATE ONLY - NOT RELEASED FOR ORDER", "warning": WARNING} for path in sorted(fab_files)])
    (OUT / "README.md").write_text(f"# HR-30 SWD adapter P0.1\n\n**{WARNING}**\n\nThis package contains the native two-sheet KiCad schematic and routed 32 x 20 mm two-layer adapter between STLINK-V3MINIE STDC14 and the HR-30 motion controller's JST GH JDBG1 service boundary. The exact Samtec alignment-pin footprint, complete contact dispositions, candidate fabrication files, five-contact cable drawing and nine-step inspection traveller are included.\n\nNative checks are ERC 0/0 and DRC 0 with zero unconnected board items. That verifies encoded connectivity and board rules only. The PCB is unbuilt, the cable wire/order code and crimp process remain unresolved, the target logic supply remains unresolved, and no physical inspection or bring-up has run.\n", encoding="utf-8")
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 SWD adapter P0.1</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f6fbff;--ink:#142a40;--line:#91cbe7}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:#fff}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}article,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}.pass{{color:#12623a}}.hold{{border-color:#c99200;background:#fff8db}}.viewer{{overflow:auto;border:2px solid var(--line);background:#fff}}object{{display:block;width:100%;min-width:760px;min-height:390px}}a{{color:#075b9b;font-weight:800}}li{{margin:.55rem 0}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><h1>The controller now has a real programming adapter design.</h1><p>The complete 14-contact STDC14 boundary is converted to the controller's five-contact JDBG1 interface on a routed native KiCad board. Reserved functions stay visibly disconnected.</p></header><main><section class="grid"><article><div class="metric">32 x 20</div><p>millimetre two-layer adapter</p></article><article><div class="metric pass">ERC 0/0</div><p>native schematic connectivity</p></article><article><div class="metric pass">DRC 0</div><p>zero encoded board-rule violations</p></article><article class="hold"><div class="metric">0</div><p>fabricated boards or physical tests</p></article></section><section><h2>Routed adapter</h2><div class="viewer"><object data="output/{PROJECT}-front.svg" type="image/svg+xml" aria-label="Front copper and silkscreen of the HR-30 SWD adapter"></object></div></section><section><h2>Five-contact service cable</h2><div class="viewer"><object data="cable-drawing.svg" type="image/svg+xml" aria-label="Five-contact SWD service cable drawing"></object></div></section><section class="panel"><h2>Contact rules that prevent an accidental power path</h2><ul><li>STDC14 pin 3 senses CTRL_3V3. It does not power the target.</li><li>STDC14 pins 5, 7 and 11 are target signal ground, including GNDDETECT.</li><li>Pins 1, 2, 8, 9, 10, 13 and 14 are explicit no-connects.</li><li>The adapter is used only with actuator carriers physically disconnected.</li></ul></section><section class="panel"><h2>Inspect the engineering source</h2><p><a href="{PROJECT}.kicad_pro">Native KiCad project</a> &middot; <a href="board/{PROJECT}.kicad_pcb">Native PCB</a> &middot; <a href="contact-map.csv">Contact map</a> &middot; <a href="adapter-bom.csv">BOM</a> &middot; <a href="inspection-traveller.csv">Inspection traveller</a> &middot; <a href="validation/{PROJECT}-erc.rpt">ERC</a> &middot; <a href="validation/{PROJECT}-drc.rpt">DRC</a> &middot; <a href="open-holds.csv">Open holds</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>''', encoding="utf-8")


def integrate_whole_body() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "swd_adapter_native_board_present": True, "swd_adapter_board_dimensions_mm": [32, 20, 1.6],
        "swd_adapter_erc_errors": 0, "swd_adapter_erc_warnings": 0, "swd_adapter_drc_violations": 0,
        "swd_adapter_exact_stdc14_contact_map": True, "swd_adapter_fabricated": False,
        "swd_adapter_cable_built": False, "swd_adapter_physical_validation_complete": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = WHOLE / "README.md"; text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-SWD-ADAPTER-P01-START -->", "<!-- HR30-SWD-ADAPTER-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Native SWD programming adapter\n\nThe [interactive SWD adapter guide](electrical/swd-adapter-p0.1/index.html) contains a routed **32 x 20 mm two-layer native KiCad adapter** from STLINK-V3MINIE STDC14 to controller JDBG1, plus the exact Samtec alignment-pin footprint, candidate manufacturing files, complete 14-contact disposition, five-contact service-cable drawing and inspection traveller. Native checks are ERC 0/0 and DRC 0. The board and cable remain unbuilt and all physical validation and work authority remain open.\n{end}\n'''
    readme.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
    page = WHOLE / "index.html"; text = page.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="swd-adapter"><h2>The programming path now has a native adapter board</h2><div class="grid"><article class="card pass"><div class="metric">32 x 20</div><p>millimetre native two-layer KiCad adapter.</p></article><article class="card pass"><h3>ERC 0/0 &middot; DRC 0</h3><p>Exact STDC14-to-JDBG1 connectivity and routed board rules pass.</p></article><article class="card hold"><h3>Physical closure open</h3><p>The board and cable are unbuilt; wire selection, crimping, inspection and target supply remain open.</p></article></div><p><a href="electrical/swd-adapter-p0.1/index.html">Open the interactive SWD adapter guide</a>.</p></section>{end}'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-END -->"
    if marker not in text:
        raise RuntimeError("STM32 bring-up web marker missing")
    page.write_text(text.replace(marker, marker + section), encoding="utf-8")


def manifest_release() -> None:
    shutil.copy2(Path(__file__), OUT / "swd-adapter-source.py")
    files = [path for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", ["path", "bytes", "sha256", "warning"], [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING} for path in sorted(files)])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    if not CAD_PYTHON.is_file():
        raise RuntimeError("controlled CadQuery runtime missing")
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    if subprocess.run([str(CAD_PYTHON), "-c", code], cwd=ROOT, check=False).returncode:
        raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    items = parts()
    write_custom_footprint()
    print("SWD adapter: native schematic", flush=True); write_schematic(items)
    print("SWD adapter: routed native PCB", flush=True); board_info = write_board(items)
    print("SWD adapter: ERC/DRC and manufacturing candidate", flush=True); validation = validate_export(board_info)
    print("SWD adapter: guides and integration", flush=True); publish(items, board_info, validation); integrate_whole_body(); manifest_release()
    print(json.dumps({"identifier": IDENTIFIER, "board_mm": [32, 20, 1.6], "erc": [0, 0], "drc": 0, "fabricated": False, "authorities": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
