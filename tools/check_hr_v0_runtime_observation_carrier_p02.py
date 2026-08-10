#!/usr/bin/env python3
"""Independently check the R202 routed runtime-observation carrier candidate.

Run with KiCad's bundled Python. Passing proves encoded schematic/PCB parity,
native ERC/DRC status and presentation invariants only. It grants no authority
to procure, fabricate, assemble, connect, power, move or energize anything.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
PROJECT = "hr-v0-runtime-observation-carrier-p0.2"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.2.md"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.2/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (ECAD / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def close(actual: float, expected: float, tolerance: float = 0.001) -> bool:
    return math.isclose(actual, expected, abs_tol=tolerance)


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(len(sheets) == 5, "expected root plus four native KiCad sheets")
    need((ECAD / f"{PROJECT}.kicad_pro").is_file(), "KiCad project missing")
    need((ECAD / f"{PROJECT}.kicad_sym").is_file(), "project symbol library missing")
    need((ECAD / f"{PROJECT}.kicad_pcb").is_file(), "native PCB source missing")
    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    drc = (ECAD / f"validation/{PROJECT}-drc.rpt").read_text(encoding="utf-8-sig")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "native ERC is not 0/0")
    need("Found 0 DRC violations" in drc, "native DRC is not zero violations")
    need("Found 0 unconnected pads" in drc, "native DRC reports an unconnected pad")
    need("Found 0 Footprint errors" in drc, "native DRC reports a footprint error")

    connector = rows("connector-schedule.csv")
    holds = rows("selection-holds.csv")
    sources = rows("source-register.csv")
    placements = rows("pcb-placement.csv")
    need(len(connector) == 102, "connector schedule row count changed")
    need(len(holds) == 14, "all fourteen physical-evidence holds must remain open")
    need(len(sources) == 15, "primary-source register must contain fifteen records")
    need(len(placements) == 33, "placement schedule must contain 29 mounted parts plus four holes")
    need(all(row.get("warning") == WARNING for row in connector + holds + sources + placements), "warning changed or is missing from a schedule")
    phoenix = [row for row in sources if row["manufacturer"] == "Phoenix Contact"]
    need(len(phoenix) == 1 and "1751280" in phoenix[0]["revision"] and "MKDS 1/6-3,5" in phoenix[0]["document"], "exact six-position Phoenix source binding changed")

    board = pcbnew.LoadBoard(str(ECAD / f"{PROJECT}.kicad_pcb"))
    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    board_only = {f"MH{i}" for i in range(1, 5)}
    schedule_refs = {row["reference"] for row in placements} - board_only
    need(set(footprints) == schedule_refs | board_only, "board footprint membership differs from the placement schedule")
    node_net = {(row["reference"], row["terminal"]): row["net"] for row in connector}
    for ref in sorted(schedule_refs):
        actual = {pad.GetNumber(): pad.GetNetname() for pad in footprints[ref].Pads()}
        expected = {row["terminal"]: row["net"] for row in connector if row["reference"] == ref}
        need(actual == expected, f"pad/net parity changed at {ref}")

    need(board.GetCopperLayerCount() == 4, "candidate must remain a four-layer board")
    edges = [item for item in board.GetDrawings() if item.GetLayer() == pcbnew.Edge_Cuts]
    xs = [mm(point) for item in edges for point in (item.GetStart().x, item.GetEnd().x)]
    ys = [mm(point) for item in edges for point in (item.GetStart().y, item.GetEnd().y)]
    need(close(max(xs) - min(xs), 120.0) and close(max(ys) - min(ys), 90.0), "board outline differs from 120 x 90 mm")
    expected_holes = {"MH1": (4.5, 4.5), "MH2": (115.5, 4.5), "MH3": (4.5, 85.5), "MH4": (115.5, 85.5)}
    for ref, expected in expected_holes.items():
        position = footprints[ref].GetPosition()
        need(close(mm(position.x), expected[0]) and close(mm(position.y), expected[1]), f"{ref} datum changed")

    for ref in ("JFIELD1", "JLOGIC1"):
        fp = footprints[ref]
        need(fp.GetFPID().GetLibItemName() == "Phoenix_MKDS_1_6_3P5_1751280", f"{ref} exact footprint identity changed")
        pads = sorted(fp.Pads(), key=lambda item: int(item.GetNumber()))
        need(len(pads) == 6, f"{ref} must have six positions")
        for pad in pads:
            need(close(mm(pad.GetDrillSize().x), 1.10), f"{ref}.{pad.GetNumber()} drill differs from 1.10 mm")
            need(close(mm(pad.GetSize().x), 2.10) and close(mm(pad.GetSize().y), 2.10), f"{ref}.{pad.GetNumber()} controlled land differs from 2.10 mm")
        pitch = [math.hypot(mm(pads[i + 1].GetPosition().x - pads[i].GetPosition().x), mm(pads[i + 1].GetPosition().y - pads[i].GetPosition().y)) for i in range(5)]
        need(all(close(item, 3.50) for item in pitch), f"{ref} pitch differs from 3.50 mm")

    tracks = list(board.GetTracks())
    segments = [item for item in tracks if type(item).__name__ == "PCB_TRACK"]
    vias = [item for item in tracks if type(item).__name__ == "PCB_VIA"]
    zones = list(board.Zones())
    need(len(segments) == 143, "controlled routed-segment count changed")
    need(len(vias) == 56, "controlled via count changed")
    need(len(zones) == 3, "controlled zone count changed")
    zone_signature = {(zone.GetNetname(), zone.GetLayer()) for zone in zones}
    need(zone_signature == {("SAFETY_0V", pcbnew.In1_Cu), ("COMPUTE_0V", pcbnew.In1_Cu), ("PI_3V3_CANDIDATE", pcbnew.In2_Cu)}, "internal-plane allocation changed")
    for zone in zones:
        need(zone.IsFilled() and zone.HasFilledPolysForLayer(zone.GetLayer()), f"{zone.GetNetname()} has no saved fill")

    # No routed signal copper may cross the 57.2..62.8 mm field/compute corridor.
    # Only UOBS1/UOBS2 package pads bridge the functional domain boundary.
    for item in tracks:
        if isinstance(item, pcbnew.PCB_VIA):
            x_values = [mm(item.GetPosition().x)]
        else:
            x_values = [mm(item.GetStart().x), mm(item.GetEnd().x)]
        if min(x_values) < 57.2 and max(x_values) > 62.8:
            need(False, f"routed copper crosses the field/compute corridor on {item.GetNetname()}")
    for fp in footprints.values():
        box = fp.GetBoundingBox()
        crosses = mm(box.GetLeft()) < 57.2 and mm(box.GetRight()) > 62.8
        if crosses:
            need(fp.GetReference() in {"UOBS1", "UOBS2"}, f"unexpected footprint spans isolation corridor: {fp.GetReference()}")

    summary = json.loads((ECAD / "validation/pcb-summary.json").read_text(encoding="utf-8"))
    need(summary == {
        "footprints": 33, "mounted_components": 29, "mounting_holes": 4,
        "board_width_mm": 120.0, "board_height_mm": 90.0, "copper_layers": 4,
        "field_compute_corridor_mm": 5.6, "fabrication_authorized": False,
        "connection_authorized": False, "energization_authorized": False,
        "track_segments": 143, "vias": 56, "zones": 3,
    }, "PCB summary changed or claims authority")

    forbidden = {".gbr", ".ger", ".drl", ".xln", ".pos", ".ipc", ".odb", ".zip", ".pdf"}
    production_like = [path for path in ECAD.rglob("*") if path.is_file() and path.suffix.lower() in forbidden]
    need(not production_like, "fabrication/CAM/PDF output exists in the candidate")
    browser_svg = ECAD / "output/runtime-observation-carrier-top.svg"
    need(browser_svg.is_file(), "interactive-guide SVG export missing")
    svg_text = browser_svg.read_text(encoding="utf-8")
    need("#0B4F8A" in svg_text and "#9A6500" in svg_text and "#082B55" in svg_text, "browser SVG lost the high-contrast blue/gold palette")
    need("#C83434" not in svg_text and "#F2EDA1" not in svg_text, "browser SVG retained low-contrast KiCad presentation colors")

    doc = DOC.read_text(encoding="utf-8")
    html = WEB.read_text(encoding="utf-8")
    for token in (WARNING, "all fourteen holds remain open", "zero functional-safety credit"):
        need(token.lower() in (doc + html).lower(), f"documentation boundary missing: {token}")
    need("font:16px/1.55" in html and "font-size:14px" in html, "web guide legibility floor changed")
    need("font-size:13px" not in html and "font-size:12px" not in html, "web guide contains undersized user-facing text")
    need("GPIO17" not in doc and "physical pin" not in doc.lower().replace("exact physical pins", ""), "documentation inferred an unselected Pi pin")

    if failures:
        print("HR-V0 runtime observation carrier P0.2 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 runtime observation carrier P0.2 check PASS")
    print("  5 sheets; 33 footprints; 143 segments; 56 vias; ERC/DRC 0; 14 holds open")
    print("  zero procurement, fabrication, connection, motion, safety or energization authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
