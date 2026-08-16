#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 SWD adapter P0.1 package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "swd-adapter-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "swd-adapter-p0.1"
GEN = ROOT / "tools" / "generate_hr30_swd_adapter_p01.py"
PROJECT = "hr30-swd-adapter-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(actual, expected, abs_tol=tolerance)


def check_manifest() -> None:
    manifest = rows(OUT / "file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    need(listed == actual, f"manifest file set mismatch missing={sorted(actual-listed)} extra={sorted(listed-actual)}")
    for row in manifest:
        path = OUT / row["path"]
        need(path.stat().st_size == int(row["bytes"]), f"manifest byte mismatch {row['path']}")
        need(sha(path) == row["sha256"], f"manifest hash mismatch {row['path']}")
        need(row["warning"] == WARNING, f"manifest warning drift {row['path']}")
    source = {path.relative_to(OUT).as_posix(): sha(path) for path in OUT.rglob("*") if path.is_file()}
    release = {path.relative_to(RELEASE).as_posix(): sha(path) for path in RELEASE.rglob("*") if path.is_file()}
    need(source == release, "source/release file or hash parity failed")


def check_footprint() -> None:
    path = OUT / "HR30_SWD.pretty" / "FTSH-107-01-L-DV-K-A.kicad_mod"
    text = path.read_text(encoding="utf-8")
    need("Rev H recommended PCB layout" in text and "molded alignment pins" in text, "footprint source identity missing")
    footprint = pcbnew.FootprintLoad(str(path.parent), path.stem)
    need(footprint is not None, "custom footprint does not parse")
    numbered = {pad.GetNumber(): pad for pad in footprint.Pads() if pad.GetNumber()}
    need(set(numbered) == {str(number) for number in range(1, 15)}, "custom footprint contact set is not 1..14")
    for number, pad in numbered.items():
        size = pad.GetSize()
        need(close(pcbnew.ToMM(size.x), 0.74) and close(pcbnew.ToMM(size.y), 2.79), f"land size drift at contact {number}")
    for number in range(1, 15, 2):
        odd = numbered[str(number)].GetPosition(); even = numbered[str(number + 1)].GetPosition()
        need(close(pcbnew.ToMM(odd.x), pcbnew.ToMM(even.x)), f"pair x mismatch {number}/{number+1}")
        need(close(pcbnew.ToMM(odd.y), 2.035) and close(pcbnew.ToMM(even.y), -2.035), f"row geometry drift {number}/{number+1}")
    odd_x = [pcbnew.ToMM(numbered[str(number)].GetPosition().x) for number in range(1, 15, 2)]
    need(all(close(b-a, 1.27) for a, b in zip(odd_x, odd_x[1:])), "1.27 mm pitch drift")
    holes = [pad for pad in footprint.Pads() if not pad.GetNumber()]
    need(len(holes) == 2, "alignment-hole count drift")
    hole_x = sorted(pcbnew.ToMM(pad.GetPosition().x) for pad in holes)
    need(all(close(pcbnew.ToMM(pad.GetDrillSize().x), 1.02) for pad in holes), "alignment-hole drill drift")
    need(close(hole_x[0], -3.175) and close(hole_x[1], 3.175), "alignment-hole spacing drift")


def check_board() -> None:
    board_path = OUT / "board" / f"{PROJECT}.kicad_pcb"
    board = pcbnew.LoadBoard(str(board_path))
    need(board.GetCopperLayerCount() == 2, "board is not two copper layers")
    need(close(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()), 1.6), "board thickness drift")
    footprints = {footprint.GetReference(): footprint for footprint in board.GetFootprints()}
    need(set(footprints) == {"J1", "J2", "H1", "H2"}, f"board footprint set drift {sorted(footprints)}")
    need(footprints["J1"].GetValue() == "FTSH-107-01-L-DV-K-A", "J1 exact part drift")
    need(footprints["J2"].GetValue() == "BM05B-GHS-TBT", "J2 exact part drift")
    expected = {
        "J1": {"3": "CTRL_3V3", "4": "SWDIO", "5": "CTRL_GND", "6": "SWCLK", "7": "CTRL_GND", "11": "CTRL_GND", "12": "MCU_NRST"},
        "J2": {"1": "CTRL_GND", "2": "CTRL_3V3", "3": "SWDIO", "4": "SWCLK", "5": "MCU_NRST"},
    }
    for reference, pad_map in expected.items():
        actual = {pad.GetNumber(): pad.GetNetname() for pad in footprints[reference].Pads() if pad.GetNumber()}
        for number, net in pad_map.items():
            need(actual.get(number) == net, f"{reference}.{number} net drift")
    j1_nets = {pad.GetNumber(): pad.GetNetname() for pad in footprints["J1"].Pads() if pad.GetNumber()}
    for number in ("1", "2", "8", "9", "10", "13", "14"):
        need(j1_nets.get(number, "") == "", f"J1.{number} must remain physically no-connect")
    via_count = sum(isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks())
    need(via_count == 6, f"via count drift {via_count}")
    need(any(zone.GetNetname() == "CTRL_GND" and zone.GetLayer() == pcbnew.F_Cu for zone in board.Zones()), "front ground zone missing")
    # Board edges must define exactly the 32 x 20 mm candidate rectangle.
    edge_points = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts and isinstance(drawing, pcbnew.PCB_SHAPE):
            for point in (drawing.GetStart(), drawing.GetEnd()):
                edge_points.append((pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)))
    need(edge_points and min(x for x, _ in edge_points) == 0 and max(x for x, _ in edge_points) == 32, "board x envelope drift")
    need(min(y for _, y in edge_points) == 0 and max(y for _, y in edge_points) == 20, "board y envelope drift")


def check_records() -> None:
    contact = rows(OUT / "contact-map.csv")
    need(len(contact) == 14 and {row["contact"] for row in contact} == {str(n) for n in range(1, 15)}, "contact map must cover all STDC14 contacts")
    mapping = {row["contact"]: row for row in contact}
    need(mapping["3"]["destination"] == "J2.2" and mapping["3"]["adapter_net"] == "CTRL_3V3", "VTREF mapping drift")
    need(mapping["4"]["destination"] == "J2.3" and mapping["6"]["destination"] == "J2.4" and mapping["12"]["destination"] == "J2.5", "SWD signal mapping drift")
    need(mapping["11"]["adapter_net"] == "CTRL_GND" and "GNDDETECT" in mapping["11"]["official_function"], "GNDDETECT not bound to target ground")
    need(all(mapping[number]["disposition"] == "EXPLICIT NO CONNECT" for number in ("1", "2", "8", "9", "10", "13", "14")), "unused-contact disposition drift")
    sources = rows(OUT / "primary-source-register.csv")
    need(len(sources) == 5 and {row["source_id"] for row in sources} == {f"SWD-S0{n}" for n in range(1, 6)}, "primary-source register drift")
    need(any("UM2910" in row["document"] and "Rev 5" in row["revision_or_date"] for row in sources), "ST Rev 5 source missing")
    need(any("IHI 0029F" in row["revision_or_date"] for row in sources), "Arm source revision missing")
    need(any("Revision H" in row["revision_or_date"] for row in sources), "Samtec footprint revision missing")
    inspection = rows(OUT / "inspection-traveller.csv")
    need(len(inspection) == 9 and all(row["result"] == "NOT EXECUTED" for row in inspection), "inspection traveller cannot claim execution")
    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 6 and all(row["state"] == "OPEN" for row in holds), "adapter holds are not fail-closed")
    bom = rows(OUT / "adapter-bom.csv")
    need(any(row["manufacturer_part_number"] == "FTSH-107-01-L-DV-K-A" for row in bom), "exact Samtec order code absent")
    need(any(row["manufacturer_part_number"] == "BM05B-GHS-TBT" for row in bom), "exact JST board header absent")
    need(any(row["manufacturer_part_number"] == "SELECTION REQUIRED" and "conductor" in row["item"] for row in bom), "wire selection must remain unresolved")


def check_status_and_guides() -> None:
    status = json.loads((OUT / "adapter-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR30-SWD-ADAPTER-P0.1" and status["warning"] == WARNING, "adapter status identity drift")
    need(status["native_kicad_schematic_sheet_count"] == 2 and status["board_dimensions_mm"] == [32, 20, 1.6], "native artifact status drift")
    need(status["erc_errors"] == status["erc_warnings"] == status["drc_violations"] == status["unconnected_items"] == 0, "native validation status not zero")
    need(status["adapter_pcb_designed"] is True and status["adapter_pcb_fabricated"] is False and status["adapter_cable_built"] is False, "design/build status boundary drift")
    for key in ("procurement_authority", "fabrication_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        need(status[key] is False, f"authority must remain false: {key}")
    erc = (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    drc = (OUT / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "native ERC report is not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "native DRC report is not clean")
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in guide and "font-size:16px" in guide, "guide legibility floor missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", guide), "guide contains user-facing text below 12 px")
    need("The controller now has a real programming adapter design" in guide and "fabricated boards or physical tests" in guide, "guide outcome/boundary missing")
    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(whole_status["swd_adapter_native_board_present"] is True and whole_status["swd_adapter_fabricated"] is False, "whole-body status integration drift")
    need("electrical/swd-adapter-p0.1/index.html" in (WHOLE / "README.md").read_text(encoding="utf-8"), "whole-body README integration missing")
    need("id=\"swd-adapter\"" in (WHOLE / "index.html").read_text(encoding="utf-8"), "whole-body web integration missing")


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source or release package missing")
    need((OUT / "swd-adapter-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    check_manifest(); check_footprint(); check_board(); check_records(); check_status_and_guides()
    print("PASS: HR-30 SWD adapter native KiCad, exact contact map, manufacturing candidate, guides and fail-closed authority verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
