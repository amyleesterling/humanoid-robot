#!/usr/bin/env python3
"""Generate the HR-30 three-rail auxiliary-power module candidate.

The package replaces the former imaginary pelvis converter envelope with a
physical, editable three-channel architecture.  It deliberately does not
select fuse values, reverse-polarity/inrush devices, the secondary-return/PE
bond, harness conductors, or grant any work authority.
"""

from __future__ import annotations

import csv
import argparse
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

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "electrical" / "auxiliary-power-module-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "auxiliary-power-module-p0.1"
PROJECT = "hr30-auxiliary-power-module-p0.1"
IDENTIFIER = "HR30-AUXILIARY-POWER-MODULE-P0.1"
DATE = "2026-08-19"
WARNING = "PRELIMINARY - UNBUILT AUXILIARY-POWER MODULE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
RECOM_PAGE = "https://recom-power.com/en/rec-s-REC30E-Z.html"
RECOM_DS = "https://recom-power.com/pdf/Econoline/REC30E-Z.pdf"
JST_VH = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
BOARD_W, BOARD_H, BOARD_T = 120.0, 58.0, 1.6


@dataclass(frozen=True)
class Part:
    rail: str
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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def load_model():
    source = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_aux_power_schematic_model", source)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load KiCad schematic model")
    model = importlib.util.module_from_spec(spec); sys.modules[spec.name] = model; spec.loader.exec_module(model)
    model.OUT = OUT; model.PROJECT = PROJECT; model.REV = "P0.1"; model.DATE = DATE; model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 AUXILIARY POWER MODULE"
    model.PROJECT_SUBTITLE = "Three isolated 30 W rails; protection, thermal and physical validation open."
    return model


def load_carrier_utils():
    source = ROOT / "tools" / "generate_hr30_actuator_interface_carriers_p01.py"
    spec = importlib.util.spec_from_file_location("hr30_aux_power_board_utils", source)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load KiCad board utilities")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module


def circuit_parts() -> list[Part]:
    rails = (
        ("COMPUTE", 22.0, "COMPUTE_5V1", "Raspberry Pi 5 compute", 27.0),
        ("HMI", 60.0, "HMI_5V0", "face display, cameras, audio and networking", 30.0),
        ("CONTROL", 98.0, "AUX_5V_SAFE", "deterministic controller, carriers, IMU and feet", 15.0),
    )
    parts: list[Part] = []
    for index, (rail, x, output, load, peak) in enumerate(rails, 1):
        raw, fused, protected = f"{rail}_12V_RAW", f"{rail}_12V_FUSED", f"{rail}_12V_PROTECTED"
        disable = f"{rail}_DISABLE_N"
        parts.extend([
            Part(rail, f"JI{index}", f"{rail} 12 V input and active-low disable", "B3P-VH-B", "JST", "Connector_JST:JST_VH_B3P-VH-B_1x03_P3.96mm_Vertical", {"1": raw, "2": "ACT_0V_CONTROLLED", "3": disable}, x, 5.0, 0, True, JST_VH, "contact map is project-owned; conductor, mating housing, contact and derating validation remain open"),
            Part(rail, f"F{index}", f"{rail} input fuse - SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "HR30_AUX:AUX_SELECTION_BLOCK", {"1": raw, "2": fused}, x - 8.0, 14.0, 0, True, "", "fault current, inrush, ambient, conductor and clearing coordination required"),
            Part(rail, f"RP{index}", f"{rail} reverse-polarity and inrush block - SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "HR30_AUX:AUX_SELECTION_BLOCK", {"1": fused, "2": protected}, x + 8.0, 14.0, 0, True, RECOM_PAGE, "RECOM states reverse polarity is not internal and high-power battery inputs require external protection/inrush control"),
            Part(rail, f"U{index}", f"REC30E-2405SZ {rail} isolated converter", "REC30E-2405SZ", "RECOM", "HR30_AUX:REC30E-Z", {"1": protected, "2": "ACT_0V_CONTROLLED", "3": disable, "4": "AUX_0V_STAR", "6": output}, x, 30.0, 0, True, RECOM_DS, "REV 1/2024; 9-36 V input, 5 V 6 A output, 89% typical efficiency, 2 kVDC/1 min isolation; pin 5 trim deliberately unconnected"),
            Part(rail, f"JO{index}", f"{rail} protected output", "B2P-VH-B", "JST", "Connector_JST:JST_VH_B2P-VH-B_1x02_P3.96mm_Vertical", {"1": output, "2": "AUX_0V_STAR"}, x, 53.0, 180, True, JST_VH, f"candidate output to {load}; harness and derating open"),
        ])
    return parts


def write_schematic(parts: list[Part]) -> None:
    model = load_model(); by_rail: dict[str, list] = {}
    for part in parts:
        pins = [model.pn(part.ref, number, number, net, "left" if idx % 2 == 0 else "right") for idx, (number, net) in enumerate(part.pins.items()) if net]
        component = model.Component(part.ref, part.value, pins, "CANDIDATE / SELECTION REQUIRED", part.evidence, part.source, part.evidence, position=(50, 50), width=96, footprint=part.footprint)
        by_rail.setdefault(part.rail, []).append(component)
    sheets = []
    for number, rail in enumerate(("COMPUTE", "HMI", "CONTROL"), 1):
        sheet = model.Sheet(number, f"0{number}_{rail.lower()}_rail.kicad_sch", f"{rail} isolated 5 V rail", "Physical module and connector candidates; input protection and validation open.")
        sheet.components = by_rail[rail]
        for idx, item in enumerate(sheet.components):
            item.position = (54 + (idx % 3) * 140, 60 + (idx // 3) * 92); item.width = 94
        sheet.notes = [WARNING, "Pin 3 CTRL is ON when open and OFF when shorted to -Vin; it is diagnostic/control only and has zero safety credit.", "All three -Vout pins meet only at AUX_0V_STAR; the single PE bond remains SELECTION REQUIRED."]
        sheets.append(sheet)
    counts: dict[str, int] = {}
    for sheet in sheets:
        for item in sheet.components:
            for pin in item.pins:
                counts[pin.net] = counts.get(pin.net, 0) + 1
    wires = model.build_wire_numbers(sheets, counts); root_uuid = model.uid("root-hr30-auxiliary-power-module-p0.1")
    project = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.25, "track_width": 0.5, "via_diameter": 0.8, "via_drill": 0.4}], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for sheet in sheets for item in sheet.components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 auxiliary power symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wires), encoding="utf-8")


def fp_line(fp: pcbnew.FOOTPRINT, a: tuple[float, float], b: tuple[float, float], layer: int, width: float = 0.15) -> None:
    item = pcbnew.PCB_SHAPE(fp); item.SetShape(pcbnew.SHAPE_T_SEGMENT); item.SetStart(pcbnew.VECTOR2I_MM(*a)); item.SetEnd(pcbnew.VECTOR2I_MM(*b)); item.SetLayer(layer); item.SetWidth(pcbnew.FromMM(width)); fp.Add(item)


def custom_pad(fp: pcbnew.FOOTPRINT, number: str, x: float, y: float, drill: float = 1.3, diameter: float = 2.5) -> pcbnew.PAD:
    pad = pcbnew.PAD(fp); pad.SetNumber(number); pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH); pad.SetShape(pcbnew.PAD_SHAPE_RECT if number == "1" else pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I_MM(diameter, diameter)); pad.SetDrillSize(pcbnew.VECTOR2I_MM(drill, drill)); pad.SetFPRelativePosition(pcbnew.VECTOR2I_MM(x, y))
    layers = pcbnew.LSET.AllCuMask(); layers.AddLayer(pcbnew.F_Mask); layers.AddLayer(pcbnew.B_Mask); pad.SetLayerSet(layers); fp.Add(pad); return pad


def rec30_footprint() -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None); fp.SetFPID(pcbnew.LIB_ID("HR30_AUX", "REC30E-Z")); fp.SetValue("REC30E-Z"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    # Bottom-view candidate transcribed from RECOM REV 1/2024.  Received-part
    # pin-position FAI remains an explicit hold before fabrication release.
    for number, x, y in (("1", -10.16, -10.16), ("2", -10.16, 10.16), ("3", -10.16, 0.0), ("4", 10.16, -10.16), ("5", 10.16, 0.0), ("6", 10.16, 10.16)):
        custom_pad(fp, number, x, y)
    for a, b in (((-12.7, -12.7), (12.7, -12.7)), ((12.7, -12.7), (12.7, 12.7)), ((12.7, 12.7), (-12.7, 12.7)), ((-12.7, 12.7), (-12.7, -12.7))):
        fp_line(fp, a, b, pcbnew.F_Fab); fp_line(fp, a, b, pcbnew.F_CrtYd, 0.05)
    return fp


def selection_footprint() -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None); fp.SetFPID(pcbnew.LIB_ID("HR30_AUX", "AUX_SELECTION_BLOCK")); fp.SetValue("SELECTION REQUIRED"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    custom_pad(fp, "1", -4.0, 0.0, 1.2, 2.4); custom_pad(fp, "2", 4.0, 0.0, 1.2, 2.4)
    for a, b in (((-5.5, -3.0), (5.5, -3.0)), ((5.5, -3.0), (5.5, 3.0)), ((5.5, 3.0), (-5.5, 3.0)), ((-5.5, 3.0), (-5.5, -3.0))): fp_line(fp, a, b, pcbnew.F_Fab)
    return fp


def write_footprint_library() -> None:
    lib = OUT / "HR30_AUX.pretty"; lib.mkdir(parents=True, exist_ok=True)
    io = pcbnew.PCB_IO_KICAD_SEXPR(); io.FootprintSave(str(lib), rec30_footprint()); io.FootprintSave(str(lib), selection_footprint())
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "HR30_AUX")(type "KiCad")(uri "${KIPRJMOD}/HR30_AUX.pretty")(options "")(descr "HR-30 REC30E and unresolved protection footprints"))\n)\n', encoding="utf-8")


def add_track(board: pcbnew.BOARD, net, points: list[tuple[float, float]], layer=None, width: float = 1.0) -> None:
    if layer is None:
        layer = pcbnew.F_Cu
    for a, b in zip(points, points[1:]):
        item = pcbnew.PCB_TRACK(board); item.SetStart(pcbnew.VECTOR2I_MM(*a)); item.SetEnd(pcbnew.VECTOR2I_MM(*b)); item.SetLayer(layer); item.SetWidth(pcbnew.FromMM(width)); item.SetNet(net); board.Add(item)


def write_board(parts: list[Part]) -> dict[str, object]:
    utils = load_carrier_utils(); write_footprint_library(); board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
    settings = board.GetDesignSettings(); settings.SetBoardThickness(pcbnew.FromMM(BOARD_T)); settings.m_MinClearance = pcbnew.FromMM(0.30); settings.m_TrackMinWidth = pcbnew.FromMM(0.40); settings.m_HoleClearance = pcbnew.FromMM(0.25); settings.m_HoleToHoleMin = pcbnew.FromMM(0.30); settings.m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.30))
    net_names = sorted({net for p in parts for net in p.pins.values() if net}); nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    fps: dict[str, pcbnew.FOOTPRINT] = {}
    for part in parts:
        if part.footprint == "HR30_AUX:REC30E-Z": fp = rec30_footprint()
        elif part.footprint == "HR30_AUX:AUX_SELECTION_BLOCK": fp = selection_footprint()
        else: fp = utils.lib_fp(part.footprint)
        fp.SetReference(part.ref); fp.SetValue(part.value); fp.SetPosition(pcbnew.VECTOR2I_MM(part.x, part.y)); fp.SetOrientationDegrees(part.rotation); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        for pad in fp.Pads():
            if part.pins.get(pad.GetNumber()): pad.SetNet(nets[part.pins[pad.GetNumber()]])
        board.Add(fp); fps[part.ref] = fp
    for index, (x, y) in enumerate(((4, 4), (116, 4), (4, 54), (116, 54)), 1):
        hole = utils.lib_fp("MountingHole:MountingHole_3.2mm_M3"); hole.SetReference(f"H{index}"); hole.SetValue("M3 BOARD MOUNT - STACK/FASTENER SELECTION REQUIRED"); hole.SetPosition(pcbnew.VECTOR2I_MM(x, y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); hole.Value().SetVisible(False); board.Add(hole)
    corners = ((0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H))
    for a, b in zip(corners, (*corners[1:], corners[0])):
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetStart(pcbnew.VECTOR2I_MM(*a)); edge.SetEnd(pcbnew.VECTOR2I_MM(*b)); edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(pcbnew.FromMM(0.20)); board.Add(edge)
    def pad_xy(ref: str, pin: str) -> tuple[float, float]:
        pad = next(p for p in fps[ref].Pads() if p.GetNumber() == pin); pos = pad.GetPosition(); return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
    for index, (rail, x, output) in enumerate((("COMPUTE", 22.0, "COMPUTE_5V1"), ("HMI", 60.0, "HMI_5V0"), ("CONTROL", 98.0, "AUX_5V_SAFE")), 1):
        raw, fused, protected, disable = f"{rail}_12V_RAW", f"{rail}_12V_FUSED", f"{rail}_12V_PROTECTED", f"{rail}_DISABLE_N"
        add_track(board, nets[raw], [pad_xy(f"JI{index}", "1"), pad_xy(f"F{index}", "1")], width=1.5)
        add_track(board, nets[fused], [pad_xy(f"F{index}", "2"), pad_xy(f"RP{index}", "1")], width=1.5)
        add_track(board, nets[protected], [pad_xy(f"RP{index}", "2"), (x + 12.0, 17.4), (x - 10.16, 17.4), pad_xy(f"U{index}", "1")], width=1.5)
        # Primary return stays on the back and approaches each converter from
        # the left clearance corridor.  All three branches then join the same
        # controlled-return bus immediately behind the input connectors.
        return_x = x - 15.0
        add_track(board, nets["ACT_0V_CONTROLLED"], [(return_x, 2.4), (return_x, 40.16), pad_xy(f"U{index}", "2")], layer=pcbnew.B_Cu, width=1.5)
        add_track(board, nets[disable], [pad_xy(f"JI{index}", "3"), (pad_xy(f"JI{index}", "3")[0], 30.0), pad_xy(f"U{index}", "3")], layer=pcbnew.B_Cu, width=0.5)
        add_track(board, nets[output], [pad_xy(f"U{index}", "6"), (x + 10.16, 48.0), (x, 48.0), pad_xy(f"JO{index}", "1")], width=2.0)
        add_track(board, nets["AUX_0V_STAR"], [pad_xy(f"U{index}", "4"), (x + 14.0, 19.84), (x + 14.0, 46.0), (x - 3.96, 46.0), pad_xy(f"JO{index}", "2")], layer=pcbnew.B_Cu, width=2.0)
    add_track(board, nets["ACT_0V_CONTROLLED"], [(7.0, 2.4), (101.96, 2.4)], layer=pcbnew.B_Cu, width=1.5)
    for x in (25.96, 63.96, 101.96): add_track(board, nets["ACT_0V_CONTROLLED"], [(x, 2.4), (x, 5.0)], layer=pcbnew.B_Cu, width=1.5)
    add_track(board, nets["AUX_0V_STAR"], [(18.04, 46.0), (112.0, 46.0)], layer=pcbnew.B_Cu, width=2.0)
    board_dir = OUT / "board"; board_dir.mkdir(exist_ok=True)
    (board_dir / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "HR30_AUX")(type "KiCad")(uri "${KIPRJMOD}/../HR30_AUX.pretty")(options "")(descr "HR-30 REC30E and unresolved protection footprints"))\n)\n', encoding="utf-8")
    path = board_dir / f"{PROJECT}.kicad_pcb"; pcbnew.SaveBoard(str(path), board)
    return {"path": path, "parts": len(parts), "nets": len(nets)}


def pcb_mode() -> int:
    global pcbnew
    import pcbnew as pcbnew_module
    pcbnew = pcbnew_module
    OUT.mkdir(parents=True, exist_ok=True)
    board = write_board(circuit_parts())
    (OUT / "board-info.json").write_text(json.dumps({**board, "path": str(board["path"])}, indent=2) + "\n", encoding="utf-8")
    return 0


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run([str(KICAD), *map(str, args)], cwd=OUT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.stdout: print(result.stdout.strip())
    if result.stderr: print(result.stderr.strip())
    return result


def validate_export(board: dict[str, object]) -> dict[str, int]:
    validation = OUT / "validation"; output = OUT / "output"; validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    erc = run_cli(["sch", "erc", "--output", validation / f"{PROJECT}-erc.rpt", "--severity-all", OUT / f"{PROJECT}.kicad_sch"])
    erc_text = (validation / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"ERC messages:\s*(\d+)\s+Errors\s+(\d+)\s+Warnings", erc_text); errors, warnings = (int(match.group(1)), int(match.group(2))) if match else (-1, -1)
    drc = run_cli(["pcb", "drc", "--output", validation / f"{PROJECT}-drc.rpt", "--severity-all", board["path"]])
    drc_text = (validation / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8", errors="replace")
    found = re.search(r"Found\s+(\d+)\s+DRC violations", drc_text); drc_count = int(found.group(1)) if found else 0
    unconnected = len(re.findall(r"^\[unconnected_items\]", drc_text, re.MULTILINE))
    for suffix, layers, mirror in (("front", "F.Cu,F.Silkscreen,F.Mask,Edge.Cuts", False), ("back", "B.Cu,B.Silkscreen,B.Mask,Edge.Cuts", True)):
        args = ["pcb", "export", "svg", "--mode-single", "--output", output / f"{PROJECT}-{suffix}.svg", "--layers", layers, "--fit-page-to-board", "--exclude-drawing-sheet"]
        if mirror: args.append("--mirror")
        args.append(board["path"]); result = run_cli(args)
        if result.returncode: raise RuntimeError(f"SVG export failed for {suffix}")
    run_cli(["sch", "export", "pdf", "--output", output / f"{PROJECT}-schematic.pdf", OUT / f"{PROJECT}.kicad_sch"])
    return {"erc_code": erc.returncode, "erc_errors": errors, "erc_warnings": warnings, "drc_code": drc.returncode, "drc_violations": drc_count, "unconnected": unconnected}


def export_cad() -> dict[str, float]:
    import cadquery as cq
    from cadquery.occ_impl.exporters.assembly import exportAssembly, exportGLTF
    board = cq.Workplane("XY").box(BOARD_W, BOARD_H, BOARD_T).edges("|Z").fillet(2.0)
    for x, y in ((-BOARD_W/2+4, -BOARD_H/2+4), (BOARD_W/2-4, -BOARD_H/2+4), (-BOARD_W/2+4, BOARD_H/2-4), (BOARD_W/2-4, BOARD_H/2-4)):
        board = board.faces(">Z").workplane().pushPoints([(x, y)]).hole(3.2)
    asm = cq.Assembly(name="HR30_AUXILIARY_POWER_MODULE_P0_1"); asm.add(board, name="CARRIER_PCB", color=cq.Color(0.05, 0.38, 0.20))
    colors = ((0.12, 0.52, 0.86), (0.95, 0.67, 0.10), (0.14, 0.72, 0.68))
    for index, (x, color) in enumerate(zip((-38.0, 0.0, 38.0), colors), 1):
        module = cq.Workplane("XY").box(25.4, 25.4, 10.0).edges("|Z").fillet(1.2).translate((x, 1.0, 5.8))
        asm.add(module, name=f"U{index}_REC30E_2405SZ", color=cq.Color(*color))
        for y, circuits, name in ((-24.0, 3, f"JI{index}"), (26.0, 2, f"JO{index}")):
            conn = cq.Workplane("XY").box(14.0 if circuits == 3 else 10.0, 8.0, 12.0).edges("|Z").fillet(1.0).translate((x, y, 6.8))
            asm.add(conn, name=name, color=cq.Color(0.92, 0.92, 0.90))
        for dx, name in ((-8.0, f"F{index}_SELECTION_REQUIRED"), (8.0, f"RP{index}_SELECTION_REQUIRED")):
            block = cq.Workplane("XY").box(11.0, 6.0, 5.0).translate((x + dx, -14.0, 3.3))
            asm.add(block, name=name, color=cq.Color(0.80, 0.16, 0.13))
    step = OUT / "HR30_auxiliary_power_module_candidate.step"; glb = OUT / "HR30_auxiliary_power_module_candidate.glb"
    if not exportAssembly(asm, str(step), mode="default"): raise RuntimeError("STEP export failed")
    if not exportGLTF(asm, str(glb), binary=True): raise RuntimeError("GLB export failed")
    return {"board_width_mm": BOARD_W, "board_height_mm": BOARD_H, "board_thickness_mm": BOARD_T, "module_height_above_board_mm": 10.0}


def table(rows: list[dict[str, object]]) -> str:
    fields = list(rows[0]); head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[field]))}</td>" for field in fields) + "</tr>" for row in rows)
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def publish(parts: list[Part], geometry: dict[str, float], validation: dict[str, int]) -> None:
    rail_rows = [
        {"rail_id": "AUX-COMPUTE", "converter": "REC30E-2405SZ", "input_vdc": "9-36", "output_vdc": "5.0 nominal; 5.1 target validation required", "published_capacity_w": "30", "p0_1_peak_budget_w": "27", "capacity_margin_w": "3", "loads": "Raspberry Pi 5 and compute-only accessories", "secondary_return": "AUX_0V_STAR", "state": "CANDIDATE - LOAD/TRANSIENT/THERMAL VALIDATION OPEN", "warning": WARNING},
        {"rail_id": "AUX-HMI", "converter": "REC30E-2405SZ", "input_vdc": "9-36", "output_vdc": "5.0 nominal", "published_capacity_w": "30", "p0_1_peak_budget_w": "30", "capacity_margin_w": "0", "loads": "display, cameras, microphones, audio and network", "secondary_return": "AUX_0V_STAR", "state": "BLOCKED - ZERO PEAK HEADROOM; MEASURED LOAD/REDESIGN REQUIRED", "warning": WARNING},
        {"rail_id": "AUX-CONTROL", "converter": "REC30E-2405SZ", "input_vdc": "9-36", "output_vdc": "5.0 nominal", "published_capacity_w": "30", "p0_1_peak_budget_w": "15", "capacity_margin_w": "15", "loads": "motion controller, two interface carriers, pelvis IMU and foot sensing", "secondary_return": "AUX_0V_STAR", "state": "CANDIDATE - LOAD/TRANSIENT/THERMAL VALIDATION OPEN", "warning": WARNING},
    ]
    write_csv(OUT / "rail-allocation-register.csv", list(rail_rows[0]), rail_rows)
    components = [{"reference": p.ref, "rail": p.rail, "manufacturer": p.manufacturer, "manufacturer_part_number": p.mpn, "description": p.value, "footprint": p.footprint, "fitted_p0_1": "YES" if p.fitted else "NO / DNP", "selection_state": "EXACT CANDIDATE" if p.mpn not in {"SELECTION REQUIRED", ""} else "SELECTION REQUIRED", "primary_source": p.source or "SELECTION REQUIRED", "evidence": p.evidence, "procurement_released": "NO", "warning": WARNING} for p in parts]
    write_csv(OUT / "component-register.csv", list(components[0]), components)
    contacts = [{"connector": p.ref, "rail": p.rail, "contact": pad, "net": net, "physical_family": p.mpn, "mapping_state": "PROJECT-OWNED CANDIDATE - HARNESS/DERATING/KEYING OPEN", "warning": WARNING} for p in parts if p.ref.startswith("J") for pad, net in p.pins.items()]
    write_csv(OUT / "connector-contact-map.csv", list(contacts[0]), contacts)
    sources = [
        {"source_id": "AUX-S01", "manufacturer": "RECOM", "document": "REC30E-Z datasheet", "revision_or_date": "REV 1/2024", "accessed": DATE, "url": RECOM_DS, "verified_use": "REC30E-2405SZ pinout, 9-36 V input, 5 V/6 A output, 89% typical efficiency, 2 kVDC/1 min isolation, protections, dimensions and mass"},
        {"source_id": "AUX-S02", "manufacturer": "RECOM", "document": "REC30E-Z current product page", "revision_or_date": "live page; revision not stated", "accessed": DATE, "url": RECOM_PAGE, "verified_use": "REC30E-2405SZ listed as current Focus product; manufacturer application cautions for reverse polarity, battery inrush and customer suitability"},
        {"source_id": "AUX-S03", "manufacturer": "JST", "document": "VH connector catalog", "revision_or_date": "live official catalog; revision not stated", "accessed": DATE, "url": JST_VH, "verified_use": "B2P-VH-B and B3P-VH-B board-header family; final wire/contact/derating application remains open"},
    ]
    write_csv(OUT / "primary-source-register.csv", list(sources[0]), sources)
    holds = [
        ("AUX-H01", "input fuse values and holders", "available fault current, inrush, cable length/gauge, connector limits, ambient/bundling and clearing coordination"),
        ("AUX-H02", "reverse-polarity and inrush front ends", "exact circuits/order codes, SOA, fault cases, startup and physical validation"),
        ("AUX-H03", "HMI rail has zero peak headroom", "measured worst-case device loads and startup; either accepted derated envelope or higher-capacity redesign"),
        ("AUX-H04", "compute 5.1 V target and all trim networks", "cable-drop/load-step measurements and exact trim components; no remote voltage trim drive"),
        ("AUX-H05", "secondary return star and sole PE bond", "signed grounding disposition, exact bond hardware/location, fault and EMC evidence"),
        ("AUX-H06", "JST VH mating parts, contacts, wire and derating", "exact order codes, contact crimp qualification, current/temperature rise and retention"),
        ("AUX-H07", "PCB footprint, copper, thermal and EMC", "independent layout review, received-part FAI, current-density/temperature, RECOM filter disposition and compliance tests"),
        ("AUX-H08", "pelvis fit, airflow, guard and service access", "integrated CAD interference review, thermal test, DFM/FAI and safe touch/access assessment"),
        ("AUX-H09", "unpowered assembly inspection and test", "signed traveler, continuity/isolation/polarity records and calibrated instruments"),
        ("AUX-H10", "qualified electrical review and work authority", "separate signed review and staged work authorization; this package cannot grant energization"),
    ]
    hold_rows = [{"hold_id": a, "open_item": b, "closure_evidence": c, "state": "OPEN", "authority": AUTHORITY, "warning": WARNING} for a, b, c in holds]
    write_csv(OUT / "open-holds.csv", list(hold_rows[0]), hold_rows)
    tests = [
        ("AUX-T01", "received identity and pin FAI", "all three exact order codes, lot markings, body/pin coordinates and isolation spacing match controlled drawings"),
        ("AUX-T02", "unpowered continuity and isolation", "all contact-to-pad paths match map; no rail-positive cross connection; qualified isolation voltage still required"),
        ("AUX-T03", "polarity and disable behavior", "each CTRL input independently disables only its rail; open=ON behavior documented; no safety credit"),
        ("AUX-T04", "current-limited startup", "input/output waveforms, inrush, delay, overshoot and source-current limit recorded for each unloaded rail"),
        ("AUX-T05", "load step and cable drop", "0-100%/75-100% rail tests at min/nom/max input and final harness; voltage stays within accepted load limits"),
        ("AUX-T06", "thermal soak", "case, connector, protection and PCB temperatures at accepted worst load/ambient/airflow"),
        ("AUX-T07", "single-fault behavior", "fuse/protection/short/reverse/dropout cases performed under released low-energy procedure"),
        ("AUX-T08", "grounding and EMC", "star/bond continuity, common-mode current and conducted/radiated disposition accepted"),
    ]
    test_rows = [{"test_id": a, "test": b, "acceptance_or_evidence": c, "result": "NOT EXECUTED", "review": "REQUIRED", "authority": AUTHORITY, "warning": WARNING} for a, b, c in tests]
    write_csv(OUT / "inspection-test-register.csv", list(test_rows[0]), test_rows)
    status = {"identifier": IDENTIFIER, "date": DATE, "warning": WARNING, "whole_body_scope": True, "candidate_converter_order_code": "REC30E-2405SZ", "converter_count": 3, "rail_count": 3, "published_total_capacity_w": 90, "p0_1_peak_budget_total_w": 72, "hmi_peak_headroom_w": 0, "board_dimensions_mm": [BOARD_W, BOARD_H, BOARD_T], "editable_step_present": True, "interactive_glb_present": True, "native_kicad_sheet_count": 4, "erc_errors": validation["erc_errors"], "erc_warnings": validation["erc_warnings"], "drc_violations": validation["drc_violations"], "unconnected_items": validation["unconnected"], "protection_values_selected": False, "secondary_pe_bond_selected": False, "harness_selected": False, "thermal_validated": False, "physical_fit_validated": False, "procurement_authority": False, "fabrication_authority": False, "assembly_authority": False, "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "walking_authority": False, "energization_authority": False}
    (OUT / "auxiliary-power-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 auxiliary-power module P0.1\n\n**{WARNING}**\n\nThis package replaces the former undefined pelvis converter with a dimensioned **120 x 58 mm three-rail carrier candidate**. Three current RECOM `REC30E-2405SZ` modules separately supply compute, face/HMI and deterministic-control positive rails. Their isolated output returns meet only at the explicit `AUX_0V_STAR`; the single possible PE bond remains unselected.\n\nThe HMI rail has **zero margin** against the current coarse 30 W peak budget, so the architecture is not released. Every fuse, reverse-polarity/inrush block, trim network, harness, PE bond, thermal result and physical test remains open. Native KiCad, STEP, GLB, contact maps and test registers are included.\n", encoding="utf-8")
    lane_data = (("Compute", "COMPUTE_5V1", 27, 3), ("Face / HMI", "HMI_5V0", 30, 0), ("Control", "AUX_5V_SAFE", 15, 15))
    lanes = "".join(f'''<g transform="translate(0,{190 + i * 155})"><rect class="box" x="70" y="0" width="190" height="105" rx="16"/><text class="sub" x="95" y="39">{name} input</text><text class="small" x="95" y="73">9-36 V module range</text><path class="line" d="M260 53H330"/><rect class="hold" x="330" y="0" width="230" height="105" rx="16"/><text x="355" y="39">Fuse + reverse/inrush</text><text class="small" x="355" y="73">SELECTION REQUIRED</text><path class="line" d="M560 53H630"/><rect class="box" x="630" y="0" width="230" height="105" rx="16"/><text class="sub" x="655" y="39">REC30E-2405SZ</text><text class="small" x="655" y="73">30 W · 5 V · 6 A · isolated</text><path class="line" d="M860 53H930"/><rect class="box" x="930" y="0" width="430" height="105" rx="16"/><text class="sub" x="955" y="39">{rail}</text><text class="small" x="955" y="73">coarse peak {peak} W · margin {margin} W</text><path class="ret" d="M745 105V{500 - i * 155}H1180"/></g>''' for i, (name, rail, peak, margin) in enumerate(lane_data))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" role="img" aria-labelledby="title desc"><title id="title">HR-30 three-rail auxiliary power architecture</title><desc id="desc">Three protected twelve volt inputs feed three isolated thirty watt converters and separate compute, HMI and control five volt rails. All secondary returns meet at one star.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.title{{font-size:36px;font-weight:900}}.sub{{font-size:23px;font-weight:800}}.small{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.hold{{fill:#fff0b5;stroke:#8d241f;stroke-width:4}}.line{{stroke:#0b4f91;stroke-width:6;fill:none}}.ret{{stroke:#17243a;stroke-width:7;fill:none}}</style><rect width="1500" height="820" fill="#eef8fe"/><text class="title" x="55" y="58">HR-30 auxiliary power: three explicit fault domains</text><rect class="hold" x="55" y="84" width="1390" height="66" rx="14"/><text x="80" y="124">UNBUILT — fuse, reverse/inrush, PE bond, harness, thermal and load validation remain OPEN</text>{lanes}<path class="ret" d="M745 760H1180"/><rect class="box" x="1180" y="690" width="250" height="110" rx="18"/><text class="sub" x="1205" y="732">AUX_0V_STAR</text><text class="small" x="1205" y="766">PE bond: SELECTION REQUIRED</text></svg>'''
    (OUT / "auxiliary-power-architecture.svg").write_text(svg, encoding="utf-8")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 auxiliary power module</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1450px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:#fff}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel{{background:#fff;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:#fff2cd;border-color:#9a6500}}.metric{{font-size:clamp(34px,5vw,56px);font-weight:900;color:var(--blue)}}section{{margin:44px 0}}.scroll,.viewer{{overflow:auto;background:#fff;border:2px solid var(--blue);border-radius:14px}}object{{display:block;width:100%;min-width:1000px;min-height:550px}}model-viewer{{width:100%;height:560px;background:radial-gradient(circle,#fff,#d9f2ff)}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:520px}}th{{position:sticky;top:0;background:var(--deep);color:#fff;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#075b9b;font-weight:800}}@media(max-width:600px){{body{{font-size:16px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / pelvis / physical auxiliary power</p><h1>The imaginary converter is gone.</h1><p>Three real, current 30 W modules now separate compute, face/HMI and deterministic-control loads on one dimensioned carrier.</p></header><main><section class="grid"><article><div class="metric">3</div><h2>isolated rails</h2><p>No positive outputs are paralleled.</p></article><article><div class="metric">90 W</div><h2>published total</h2><p>Against a 72 W coarse short-peak budget.</p></article><article><div class="metric">120 x 58</div><h2>millimetres</h2><p>Editable carrier envelope with four M3 mounting holes.</p></article><article class="hold"><div class="metric">0 W</div><h2>HMI headroom</h2><p>Measured load or redesign is mandatory.</p></article></section><section><h2>Power path</h2><div class="scroll"><object data="auxiliary-power-architecture.svg" type="image/svg+xml" aria-label="Three-rail auxiliary power architecture"></object></div></section><section><h2>Editable module layout</h2><div class="viewer"><model-viewer src="HR30_auxiliary_power_module_candidate.glb" camera-controls auto-rotate shadow-intensity="1" alt="HR-30 three-rail auxiliary power carrier"></model-viewer></div></section><section><h2>Rail allocation</h2>{table(rail_rows)}</section><section><h2>Connector contacts</h2>{table(contacts)}</section><section><h2>Open gates</h2>{table(hold_rows)}</section><section><h2>Inspection and test</h2>{table(test_rows)}</section><section class="panel"><h2>Engineering files</h2><p><a href="{PROJECT}.kicad_pro">native KiCad project</a> · <a href="board/{PROJECT}.kicad_pcb">native PCB</a> · <a href="output/{PROJECT}-front.svg">front copper view</a> · <a href="output/{PROJECT}-schematic.pdf">schematic export</a> · <a href="HR30_auxiliary_power_module_candidate.step">STEP assembly</a> · <a href="component-register.csv">component register</a> · <a href="primary-source-register.csv">manufacturer sources</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")


def integrate_root(status: dict[str, object]) -> None:
    status_path = PACKAGE / "package-status.json"; root_status = json.loads(status_path.read_text(encoding="utf-8"))
    root_status.update({"auxiliary_power_physical_candidate_present": True, "auxiliary_power_converter_order_code": "REC30E-2405SZ", "auxiliary_power_converter_count": 3, "auxiliary_power_rail_count": 3, "auxiliary_power_board_dimensions_mm": [BOARD_W, BOARD_H, BOARD_T], "auxiliary_power_hmi_zero_peak_headroom_blocker": True, "auxiliary_power_protection_selected": False, "auxiliary_power_thermal_validated": False})
    status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    start, end = "<!-- HR30-AUXILIARY-POWER-P01-START -->", "<!-- HR30-AUXILIARY-POWER-P01-END -->"
    readme = PACKAGE / "README.md"; text = readme.read_text(encoding="utf-8")
    if start in text and end in text: text = text.split(start, 1)[0] + text.split(end, 1)[1]
    text = text.rstrip() + f"\n\n{start}\n## Three-rail auxiliary-power module\n\nThe former undefined pelvis converter has been replaced by a dimensioned **120 x 58 mm three-channel candidate** using three current RECOM `REC30E-2405SZ` isolated 30 W modules. Compute, face/HMI and deterministic control now have separate positive rails and independent enable/protection boundaries; secondary returns meet only at `AUX_0V_STAR`. The HMI rail has zero margin against the current coarse 30 W peak budget, and all fuses, reverse/inrush devices, trim parts, harnesses, PE bonding, thermal tests and physical reviews remain open. [Open the interactive engineering guide](electrical/auxiliary-power-module-p0.1/index.html).\n{end}\n"
    readme.write_text(text, encoding="utf-8")
    page = PACKAGE / "index.html"; text = page.read_text(encoding="utf-8")
    if start in text and end in text: text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="auxiliary-power"><h2>The pelvis now has a physical three-rail auxiliary-power candidate</h2><div class="grid"><article class="card pass"><div class="metric">3 × 30 W</div><p>current RECOM isolated modules for compute, HMI and deterministic control.</p></article><article class="card pass"><div class="metric">120 × 58</div><p>millimetre carrier with native KiCad and editable STEP/GLB.</p></article><article class="card hold"><h3>HMI margin: 0 W</h3><p>The current coarse 30 W peak equals module capacity; measured load or redesign is mandatory.</p></article><article class="card hold"><h3>Protection open</h3><p>Fuse, reverse/inrush, PE bond, harness, thermal and physical validation remain unreleased.</p></article></div><div class="viewer"><object data="electrical/auxiliary-power-module-p0.1/auxiliary-power-architecture.svg" type="image/svg+xml" aria-label="HR-30 auxiliary power architecture"></object><p><a href="electrical/auxiliary-power-module-p0.1/index.html">Open the auxiliary-power engineering guide</a>.</p></div></section>{end}'''
    marker = "</main>"
    if marker not in text: raise RuntimeError("root guide main marker missing")
    page.write_text(text.replace(marker, section + marker, 1), encoding="utf-8")


def manifest_release() -> None:
    files = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    rows = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(files)]
    write_csv(OUT / "file-manifest.csv", list(rows[0]), rows)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    if not CAD_PYTHON.is_file(): raise RuntimeError("controlled CadQuery runtime missing")
    code = "import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"
    result = subprocess.run([str(CAD_PYTHON), "-c", code], cwd=ROOT, check=False)
    if result.returncode: raise RuntimeError("whole-body manifest/release refresh failed")


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--pcb", action="store_true"); args = parser.parse_args()
    if args.pcb:
        return pcb_mode()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    parts = circuit_parts(); write_schematic(parts)
    pcb_result = subprocess.run([r"C:\Program Files\KiCad\10.0\bin\python.exe", str(Path(__file__)), "--pcb"], cwd=ROOT, check=False)
    if pcb_result.returncode:
        raise RuntimeError("native PCB generation failed")
    board = json.loads((OUT / "board-info.json").read_text(encoding="utf-8")); board["path"] = Path(board["path"])
    validation = validate_export(board); geometry = export_cad(); publish(parts, geometry, validation)
    shutil.copy2(Path(__file__), OUT / "auxiliary-power-module-source.py")
    shutil.copy2(ROOT / "tools" / "check_hr30_auxiliary_power_module_p01.py", OUT / "auxiliary-power-module-checker.py")
    status = json.loads((OUT / "auxiliary-power-status.json").read_text(encoding="utf-8")); integrate_root(status); manifest_release()
    print(json.dumps({"identifier": IDENTIFIER, "parts": len(parts), "rails": 3, "erc": [validation["erc_errors"], validation["erc_warnings"]], "drc": validation["drc_violations"], "unconnected": validation["unconnected"], "authorities": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
