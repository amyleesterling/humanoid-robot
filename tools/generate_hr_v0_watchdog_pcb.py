"""Generate the native HR-V0 watchdog PCB placement/interface candidate.

This board freezes board membership, footprints, terminal-block identities and
project pin allocation.  It deliberately contains no routed copper and is not
a fabrication release.  KiCad DRC must therefore report unrouted items until a
reviewed routing pass closes the layout requirements.

PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
BOARD_PATH = OUT / "project-button-v3.kicad_pcb"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")
FOOTPRINT_ROOT = KICAD_ROOT / "share" / "kicad" / "footprints"
CUSTOM_ROOT = OUT / "PBV3_Footprints.pretty"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


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
    "DC1": (55, 34, 0),
    "CDRV1": (76, 26, 0),
    "UDRV1": (88, 34, 0),
    "CDRV2": (112, 26, 0),
    "UDRV2": (124, 34, 0),
    "JWF1": (30, 58, 0),
    "RTH1": (48, 57, 0),
    "RSN1": (59, 57, 0),
    "CFI1": (69, 61, 90),
    "RW1": (49, 68, 0),
    "RTH2": (48, 80, 0),
    "RSN2": (59, 80, 0),
    "CFI2": (69, 84, 90),
    "RW2": (49, 91, 0),
    "UFB1": (84, 76, 0),
    "CDEC1": (84, 68, 0),
    "RSO1": (99, 68, 0),
    "RPD1": (112, 68, 0),
    "RSO2": (99, 82, 0),
    "RPD2": (112, 82, 0),
    "JWH1": (30, 108, 0),
    "RHB1": (48, 108, 0),
    "ISO1": (62, 108, 0),
    "RHP1": (77, 100, 0),
    "WDCTRL1": (146, 75, 90),
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
    title.SetTitle("Project Button HR-V0 ordinary watchdog PCB placement/interface candidate")
    title.SetDate("2026-08-06")
    title.SetRevision("PCB-P0.1 / Electrical V3-P1.0")
    title.SetCompany("Project Button")
    title.SetComment(0, WARNING)
    title.SetComment(1, "UNROUTED PLACEMENT CANDIDATE - NO GERBER RELEASE")
    default_class = pcbnew.NETCLASS("Default")
    default_class.SetClearance(pcbnew.FromMM(0.15))
    default_class.SetTrackWidth(pcbnew.FromMM(0.25))
    default_class.SetViaDiameter(pcbnew.FromMM(0.8))
    default_class.SetViaDrill(pcbnew.FromMM(0.4))
    board.GetNetClasses()["Default"] = default_class

    nets = {}
    for name in sorted({pin.net for comp in components.values() for pin in comp.pins}):
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    for ref, comp in components.items():
        lib, name = footprint_location(comp.footprint)
        footprint = pcbnew.FootprintLoad(str(lib), name)
        if footprint is None:
            raise RuntimeError(f"cannot load {comp.footprint} for {ref}")
        footprint.SetReference(ref)
        footprint.SetValue(comp.value)
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
        board.Add(footprint)

    add_outline(pcbnew, board)
    add_mounting_holes(pcbnew, board)
    add_text(pcbnew, board, WARNING, 35, 116.5, 1.35, pcbnew.F_SilkS)
    add_text(pcbnew, board, "PCB-P0.1 - UNROUTED - NO SAFETY CREDIT", 95, 112, 1.2, pcbnew.F_SilkS)
    add_text(pcbnew, board, "+24  0V  C1-  C2-", 25, 42, 1.1, pcbnew.F_SilkS)
    add_text(pcbnew, board, "FB1  FB2", 25, 51.5, 1.1, pcbnew.F_SilkS)
    add_text(pcbnew, board, "HB   COMPUTE-0V", 25, 101.5, 1.1, pcbnew.F_SilkS)

    pcbnew.SaveBoard(str(BOARD_PATH), board)

    project_path = OUT / "project-button-v3.kicad_pro"
    project = json.loads(project_path.read_text(encoding="utf-8-sig"))
    classes = project.setdefault("net_settings", {}).setdefault("classes", [])
    default = next((item for item in classes if item.get("name") == "Default"), None)
    if default is None:
        default = {"name": "Default", "priority": 2147483647}
        classes.append(default)
    default.update({"clearance": 0.15, "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4})
    project_path.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")

    validation = OUT / "validation"
    output = OUT / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    cli = KICAD_ROOT / "bin" / "kicad-cli.exe"
    commands = [
        [str(cli), "pcb", "drc", "--output", str(validation / "project-button-v3-pcb-placement-drc.rpt"), str(BOARD_PATH)],
        [str(cli), "pcb", "render", "--output", str(output / "project-button-v3-pcb-placement-top.png"), "--width", "1800", "--height", "1100", "--side", "top", "--background", "opaque", str(BOARD_PATH)],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
    (validation / "project-button-v3-pcb-placement-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (OUT / "project-button-v3.kicad_prl").unlink(missing_ok=True)
    model.manifest()
    print(f"Generated {BOARD_PATH}")
    print(f"Board-mounted schematic references: {len(components)}")
    print(WARNING)
    print("This placement candidate is intentionally unrouted; DRC closure is not claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
