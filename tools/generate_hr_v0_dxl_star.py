"""Generate the HR-V0 DYNAMIXEL star-injection schematic and routed PCB.

The board keeps J1/J2/J3 positive rails electrically separate, shares only the
TTL DATA and actuator return, and leaves U2D2 TTL pin 2 without copper.  It is a
review candidate, not a fabrication or energization release.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star"
PROJECT = "hr-v0-dxl-star"
REV = "DXL-STAR-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")
FOOTPRINT_ROOT = KICAD_ROOT / "share" / "kicad" / "footprints"
TRACE_MIN_MM = 0.1524
CLEARANCE_MIN_MM = 0.1524


def load_schematic_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("dxl_star_schematic_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.PROJECT = PROJECT
    module.REV = REV
    module.PROJECT_TITLE = "PROJECT BUTTON HR-V0 DYNAMIXEL STAR INJECTION BOARD"
    module.PROJECT_SUBTITLE = "U2D2 pin 2 omitted; three protected positive rails remain isolated; common TTL DATA and return only."
    return module


def components(model):
    pn = model.pn
    Component = model.Component
    eh_source = "https://www.jst-mfg.com/product/index.php?lang=2&series=58"
    vh_source = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
    eh_footprint = "Connector_JST:JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical"
    vh_footprint = "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical"
    result = [
        Component(
            "JC1", "JST B3B-EH-A U2D2 data/reference input",
            [pn("JC1", "1", "GND", "ACT_0V_PE_BONDED", "right"),
             pn("JC1", "2", "VDD OMITTED", "INTENTIONALLY_UNUSED_U2D2_VDD", "right"),
             pn("JC1", "3", "DATA", "DXL_TTL_DATA", "right")],
            "PROPOSED - TWO-WIRE CABLE TEST REQUIRED",
            "Use EHR-3 housing with pin-2 cavity empty at both ends; exact wire, contacts, crimp tooling, length, strain relief and received continuity remain open. Pin 2 has no assigned PCB net or route.",
            eh_source, "ROBOTIS U2D2 and JST EH live pages rechecked 2026-08-07; exact header family/pins supported, harness application not released.",
            position=(65, 95), width=95, footprint=eh_footprint,
        ),
    ]
    for index in (1, 2, 3):
        result.append(Component(
            f"JP{index}", f"JST B2P-VH protected branch {index} power input",
            [pn(f"JP{index}", "1", f"J{index} FUSED VDD", f"J{index}_VDD", "right"),
             pn(f"JP{index}", "2", "COMMON RETURN", "ACT_0V_PE_BONDED", "right")],
            "PROPOSED - WIRE/THERMAL TEST REQUIRED",
            "Mates VHR-2N with SVH-21T-P1.1 candidate contacts. Project pin 1 is positive and pin 2 return; exact 18/16 AWG choice, crimp tooling, pull force, branch protection and thermal evidence remain open.",
            vh_source, "JST VH English catalog current asset rechecked 2026-08-07; B2P-VH/VHR-2N/SVH-21T-P1.1 family evidence only.",
            position=(170 + 80 * (index - 1), 70), width=72, footprint=vh_footprint,
        ))
        result.append(Component(
            f"JA{index}", f"JST B3B-EH-A actuator J{index} output",
            [pn(f"JA{index}", "1", "GND", "ACT_0V_PE_BONDED", "left"),
             pn(f"JA{index}", "2", f"J{index} VDD", f"J{index}_VDD", "left"),
             pn(f"JA{index}", "3", "DATA", "DXL_TTL_DATA", "left")],
            "PROPOSED - CABLE/LIMIT TEST REQUIRED",
            "Mates the exact X-series TTL connector family. Cable length and received identity remain open; XM540 4.4 A stall versus JST EH 3 A series basis remains a protection/thermal blocker.",
            eh_source, "ROBOTIS X-series connector table and JST EH page rechecked 2026-08-07; no permission to exceed published connector limits.",
            position=(170 + 80 * (index - 1), 180), width=82, footprint=eh_footprint,
        ))
    return result


def write_schematic(model, items):
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = model.Sheet(
        1, "01_star_injection.kicad_sch", "Three-branch DYNAMIXEL TTL star injection",
        "One fixed board shares DATA/return and keeps all three protected positive rails separate.",
    )
    sheet.components = items
    sheet.notes = [
        "JC1 pin 2 has no PCB net or route; the controller cable shall leave cavity 2 empty.",
        "J1/J2/J3 VDD never join; common return and PE/fault paths require qualified review.",
        "Validate star-DATA waveforms at released cable lengths, loads and baud rate.",
    ]
    net_counts = Counter(pin.net for comp in items for pin in comp.pins)
    wire_numbers = model.build_wire_numbers([sheet], net_counts)
    root_uuid = model.uid("root-hr-v0-dxl-star")
    project_data = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {"name": "Default", "priority": 2147483647, "clearance": CLEARANCE_MIN_MM,
                 "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4},
                {"name": "ACTUATOR_POWER", "priority": 1, "clearance": 0.25,
                 "track_width": 2.0, "via_diameter": 1.2, "via_drill": 0.6},
            ],
            "meta": {"version": 3},
            "netclass_assignments": {f"J{index}_VDD": "ACTUATOR_POWER" for index in (1, 2, 3)},
        },
        "pcbnew": {}, "schematic": {},
        "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV},
    }
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(comp).replace(f'(symbol "PBV3:{comp.ref}"', f'(symbol "{comp.ref}"', 1) for comp in items]
    (OUT / f"{PROJECT}.kicad_sym").write_text(
        '(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '
        + "\n".join(symbols) + "\n)\n", encoding="utf-8",
    )
    (OUT / "sym-lib-table").write_text(
        f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 DXL star symbols"))\n)\n',
        encoding="utf-8",
    )
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, [sheet]), encoding="utf-8")
    (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wire_numbers), encoding="utf-8")

    with (OUT / "connector-schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reference", "terminal", "pin_name", "net", "status"])
        for comp in items:
            for pin in comp.pins:
                writer.writerow([comp.ref, pin.number, pin.name, pin.net, comp.status])
    with (OUT / "bom.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reference", "value", "quantity", "status", "evidence"])
        for comp in items:
            writer.writerow([comp.ref, comp.value, 1, comp.status, comp.evidence])


def footprint_location(identifier: str) -> tuple[Path, str]:
    library, name = identifier.split(":", 1)
    return FOOTPRINT_ROOT / f"{library}.pretty", name


def add_text(board, value: str, x: float, y: float, size: float, layer):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    item.SetLayer(layer)
    item.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
    item.SetTextThickness(pcbnew.FromMM(max(0.18, size * 0.12)))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(item)


def add_track(board, net, points, width: float, layer=pcbnew.F_Cu):
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


def pad_xy(footprints, ref: str, number: str) -> tuple[float, float]:
    matches = [pad for pad in footprints[ref].Pads() if pad.GetNumber() == number]
    if len(matches) != 1:
        raise RuntimeError(f"expected one pad {ref}.{number}")
    pos = matches[0].GetPosition()
    return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)


def write_board(items):
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    nets = {}
    for name in ("ACT_0V_PE_BONDED", "DXL_TTL_DATA", "J1_VDD", "J2_VDD", "J3_VDD"):
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    placements = {
        "JC1": (30, 50, 270),
        "JP1": (50, 30, 0), "JP2": (75, 30, 0), "JP3": (100, 30, 0),
        "JA1": (50, 70, 180), "JA2": (75, 70, 180), "JA3": (100, 70, 180),
    }
    by_ref = {}
    for comp in items:
        library, name = footprint_location(comp.footprint)
        footprint = pcbnew.FootprintLoad(str(library), name)
        if footprint is None:
            raise RuntimeError(f"cannot load {comp.footprint}")
        footprint.SetReference(comp.ref)
        footprint.SetValue(comp.value)
        x, y, rotation = placements[comp.ref]
        footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        footprint.SetOrientationDegrees(rotation)
        footprint.Reference().SetVisible(False)
        pin_nets = {pin.number: pin.net for pin in comp.pins}
        for pad in footprint.Pads():
            name = pin_nets.get(pad.GetNumber(), "")
            if name in nets:
                pad.SetNet(nets[name])
        board.Add(footprint)
        by_ref[comp.ref] = footprint

    outline = [(20, 20), (120, 20), (120, 80), (20, 80), (20, 20)]
    for start, end in zip(outline, outline[1:]):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(pcbnew.VECTOR2I_MM(*start))
        line.SetEnd(pcbnew.VECTOR2I_MM(*end))
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetWidth(pcbnew.FromMM(0.25))
        board.Add(line)
    hole_lib = FOOTPRINT_ROOT / "MountingHole.pretty"
    for index, (x, y) in enumerate(((25, 25), (115, 25), (25, 75), (115, 75)), 1):
        hole = pcbnew.FootprintLoad(str(hole_lib), "MountingHole_3.2mm_M3")
        if hole is None:
            raise RuntimeError("cannot load M3 mounting hole")
        hole.SetReference(f"MH{index}")
        hole.SetValue("M3 BOARD-ONLY - ENCLOSURE/MOUNTING SELECTION OPEN")
        hole.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        hole.SetBoardOnly(True)
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)
        board.Add(hole)

    for index in (1, 2, 3):
        start = pad_xy(by_ref, f"JP{index}", "1")
        end = pad_xy(by_ref, f"JA{index}", "2")
        mid_y = 45 + 4 * (index - 2)
        add_track(board, nets[f"J{index}_VDD"], [start, (start[0], mid_y), (end[0], mid_y), end], 2.0)
    data_start = pad_xy(by_ref, "JC1", "3")
    trunk_y = 62.0
    data_targets = [pad_xy(by_ref, f"JA{index}", "3") for index in (1, 2, 3)]
    add_track(
        board, nets["DXL_TTL_DATA"],
        [data_start, (38, data_start[1]), (38, trunk_y), (data_targets[0][0], trunk_y)],
        0.25, pcbnew.B_Cu,
    )
    add_track(board, nets["DXL_TTL_DATA"], [(target[0], trunk_y) for target in data_targets], 0.25, pcbnew.B_Cu)
    for target in data_targets:
        add_track(board, nets["DXL_TTL_DATA"], [(target[0], trunk_y), target], 0.25, pcbnew.B_Cu)

    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(nets["ACT_0V_PE_BONDED"])
    zone.SetLocalClearance(pcbnew.FromMM(0.25))
    polygon = zone.Outline()
    polygon.NewOutline()
    for point in ((21, 21), (119, 21), (119, 79), (21, 79)):
        polygon.Append(pcbnew.VECTOR2I_MM(*point))
    zone.SetMinThickness(pcbnew.FromMM(0.254))
    board.Add(zone)

    add_text(board, WARNING, 31, 77, 1.0, pcbnew.F_SilkS)
    add_text(board, "DXL-STAR-P0.1 - U2D2 VDD OMITTED", 39, 24, 1.1, pcbnew.F_SilkS)
    add_text(board, "CTRL", 24, 42, 1.0, pcbnew.F_SilkS)
    for label, x in (("PWR1", 46), ("PWR2", 71), ("PWR3", 96)):
        add_text(board, label, x, 36, 0.9, pcbnew.F_SilkS)
    for label, x in (("ACT1", 46), ("ACT2", 71), ("ACT3", 96)):
        add_text(board, label, x, 66, 0.9, pcbnew.F_SilkS)
    pcbnew.SaveBoard(str(OUT / f"{PROJECT}.kicad_pcb"), board)


def run_cli():
    validation = OUT / "validation"
    output = OUT / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    for path in (*output.glob("*.svg"), *output.glob("*.png"), *output.glob("*.pdf")):
        path.unlink()
    cli = KICAD_ROOT / "bin" / "kicad-cli.exe"
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "pdf", "--output", str(output / f"{PROJECT}-preliminary.pdf"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli), "pcb", "drc", "--exit-code-violations", "--refill-zones", "--save-board", "--output", str(validation / f"{PROJECT}-drc.rpt"), str(OUT / f"{PROJECT}.kicad_pcb")],
        [str(cli), "pcb", "render", "--output", str(output / f"{PROJECT}-top.png"), "--width", "1600", "--height", "1000", "--side", "top", "--background", "opaque", str(OUT / f"{PROJECT}.kicad_pcb")],
        [str(cli), "pcb", "render", "--output", str(output / f"{PROJECT}-bottom.png"), "--width", "1600", "--height", "1000", "--side", "bottom", "--background", "opaque", str(OUT / f"{PROJECT}.kicad_pcb")],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            log_text = re.sub(r"[ \t]+(?=\r?$)", "", "\n".join(logs), flags=re.MULTILINE)
            (validation / "kicad-cli.log").write_text(log_text, encoding="utf-8")
            raise SystemExit(result.returncode)
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    log_text = re.sub(r"[ \t]+(?=\r?$)", "", "\n".join(logs), flags=re.MULTILINE)
    (validation / "kicad-cli.log").write_text(log_text, encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_readme():
    (OUT / "README.md").write_text(f"""# HR-V0 DYNAMIXEL star injection {REV}

**{WARNING}**

This native KiCad candidate implements one fixed central branch-isolating board:

- `JC1` is JST `B3B-EH-A`; pins 1/3 carry GND/DATA and pin 2 has no PCB net or route.
- `JP1`-`JP3` are JST `B2P-VH` protected branch inputs; project pin 1 is VDD and pin 2 return.
- `JA1`-`JA3` are JST `B3B-EH-A` actuator outputs using standard ROBOTIS TTL pin order.
- `J1_VDD`, `J2_VDD`, and `J3_VDD` are routed separately and never join.
- `DXL_TTL_DATA` and `ACT_0V_PE_BONDED` are common by design.

The source contains no released cable lengths, branch conductors, fuse ratings, assembly outputs, Gerber/drill package or permission to fabricate. U2D2 pin-2 omission, VDD isolation, grounding, star-bus signal integrity, connector temperature, no-backfeed and fault behavior require physical evidence and qualified review.

Generate with KiCad 10 bundled Python:

`\"C:\\Program Files\\KiCad\\10.0\\bin\\python.exe\" tools/generate_hr_v0_dxl_star.py`

Then run `tools/check_hr_v0_dxl_star.py` with the same interpreter. ERC/DRC prove encoded connectivity only.
""", encoding="utf-8")


def write_manifest():
    rows = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(OUT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (OUT / "SOURCE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256"])
        writer.writerows(rows)


def main() -> int:
    model = load_schematic_model()
    items = components(model)
    write_schematic(model, items)
    write_board(items)
    write_readme()
    run_cli()
    write_manifest()
    print(f"Generated {PROJECT}: {len(items)} connector blocks, 18 terminals, one routed two-layer PCB")
    print(WARNING)
    print("No fabrication outputs were generated; connector, harness and signal-integrity evidence remains open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
