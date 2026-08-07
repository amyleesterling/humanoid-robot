"""Validate the HR-V0 watchdog PCB placement/interface candidate.

Run this checker with KiCad's bundled Python.  It proves source consistency,
placement membership and the explicitly unrouted state only.  It does not
release routing, fabrication, assembly, energization or safety credit.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("pbv3_check_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load electrical model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []
    model = load_model()
    expected = {
        comp.ref: comp
        for sheet in model.sheets()
        for comp in sheet.components
        if comp.watchdog_pcb
    }
    board_path = OUT / "project-button-v3.kicad_pcb"
    require(board_path.is_file(), "native PCB source missing", failures)
    if not board_path.is_file():
        return 1
    board = pcbnew.LoadBoard(str(board_path))
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}
    board_only = {f"MH{index}" for index in range(1, 5)}
    require(set(footprints) == set(expected) | board_only,
            "PCB footprint membership differs from controlled board subset plus four board-only holes", failures)
    for ref, comp in expected.items():
        footprint = footprints.get(ref)
        if footprint is None:
            continue
        actual = {pad.GetNumber(): pad.GetNetname() for pad in footprint.Pads() if pad.GetNetname()}
        wanted = {pin.number: pin.net for pin in comp.pins}
        require(actual == wanted, f"PCB pad/net mapping differs at {ref}", failures)
    require(len(list(board.Tracks())) == 0, "placement candidate unexpectedly contains tracks or vias", failures)
    require(len(list(board.Zones())) == 0, "placement candidate unexpectedly contains copper zones", failures)

    title = board.GetTitleBlock()
    require(title.GetRevision() == "PCB-P0.1 / Electrical V3-P1.0", "PCB title-block revision mismatch", failures)
    require(WARNING in board_path.read_text(encoding="utf-8-sig"), "PCB warning missing", failures)
    require("UNROUTED" in board_path.read_text(encoding="utf-8-sig"), "unrouted status missing from PCB", failures)

    project = json.loads((OUT / "project-button-v3.kicad_pro").read_text(encoding="utf-8-sig"))
    default = next((item for item in project["net_settings"]["classes"] if item.get("name") == "Default"), {})
    require(default.get("clearance") == 0.15, "controlled 0.15 mm candidate copper clearance missing", failures)
    require(default.get("track_width") == 0.25, "controlled 0.25 mm candidate track width missing", failures)

    drc = (OUT / "validation" / "project-button-v3-pcb-placement-drc.rpt").read_text(encoding="utf-8-sig")
    require("Found 0 DRC violations" in drc, "placement DRC has non-unrouted violations", failures)
    unconnected = re.search(r"Found (\d+) unconnected pads", drc)
    require(unconnected is not None and int(unconnected.group(1)) == 68,
            "controlled unrouted-pad count differs from 68", failures)
    log = (OUT / "validation" / "project-button-v3-pcb-placement-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 2, "PCB DRC/render command did not both exit 0", failures)
    render = OUT / "output" / "project-button-v3-pcb-placement-top.png"
    require(render.is_file() and render.stat().st_size > 30_000, "PCB top render missing or unexpectedly small", failures)
    for name in ("MKDS_1_2_3P5.kicad_mod", "MKDS_1_4_3P5.kicad_mod", "VO618A_Option7_SMD.kicad_mod"):
        require((OUT / "PBV3_Footprints.pretty" / name).is_file(), f"custom candidate footprint missing: {name}", failures)

    if failures:
        print("HR-V0 watchdog PCB placement validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCB placement validation: PASS")
    print("26 board-mounted references; 4 board-only M3 holes; 0 routed tracks; 0 zones")
    print("KiCad DRC: 0 non-unrouted violations; 68 unconnected pads are the controlled open routing gate")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
