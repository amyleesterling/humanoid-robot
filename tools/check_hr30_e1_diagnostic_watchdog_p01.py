#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 E1 diagnostic watchdog P0.1."""

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
OUT = WHOLE / "electrical" / "e1-diagnostic-watchdog-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "e1-diagnostic-watchdog-p0.1"
GEN = ROOT / "tools" / "generate_hr30_e1_diagnostic_watchdog_p01.py"
PROJECT = "hr30-e1-diagnostic-watchdog-p0.1"
IDENTIFIER = "HR30-E1-DIAGNOSTIC-WATCHDOG-P0.1"
WARNING = "PRELIMINARY - DIAGNOSTIC ONLY - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(a, b, abs_tol=tolerance)


def check_manifest() -> None:
    manifest = rows(OUT / "file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    need(listed == actual, f"manifest set mismatch missing={sorted(actual-listed)} extra={sorted(listed-actual)}")
    for row in manifest:
        path = OUT / row["path"]
        need(path.stat().st_size == int(row["bytes"]), f"manifest byte mismatch {row['path']}")
        need(sha(path) == row["sha256"], f"manifest hash mismatch {row['path']}")
        need(row["warning"] == WARNING, f"manifest warning drift {row['path']}")
    source = {path.relative_to(OUT).as_posix(): sha(path) for path in OUT.rglob("*") if path.is_file()}
    release = {path.relative_to(RELEASE).as_posix(): sha(path) for path in RELEASE.rglob("*") if path.is_file()}
    need(source == release, "source/release parity failed")


def board_pad_map(board, reference: str) -> dict[str, str]:
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    return {pad.GetNumber(): pad.GetNetname() for pad in footprints[reference].Pads() if pad.GetNumber()}


def check_board() -> None:
    board = pcbnew.LoadBoard(str(OUT / "board" / f"{PROJECT}.kicad_pcb"))
    need(board.GetCopperLayerCount() == 2, "board must have two copper layers")
    need(close(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()), 1.6), "board thickness drift")
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    expected = {"J1", "U1", "R1", "R2", "R5", "R6", "C1", "TP1", "TP2", "TP3", "TP4", "TP5", "H1", "H2"}
    need(set(footprints) == expected, f"footprint set drift {sorted(footprints)}")
    need(footprints["U1"].GetValue() == "TPS3431SDRBR", "exact TPS3431 orderable drift")
    need(footprints["J1"].GetValue() == "BM08B-GHS-TBT", "exact JST board header drift")
    j1 = board_pad_map(board, "J1")
    need(j1["1"] == "CTRL_GND" and j1["2"] == "CTRL_3V3" and j1["3"] == "CTRL_GND" and j1["5"] == "MOTION_WD_HEARTBEAT", "J1 populated net mapping drift")
    need(all(j1.get(number, "") == "" for number in ("4", "6", "7", "8")), "J1 contacts 4/6/7/8 must be board no-connects")
    u1 = board_pad_map(board, "U1")
    required = {"1":"CTRL_3V3","2":"","3":"CTRL_3V3","4":"CTRL_GND","5":"CTRL_3V3","6":"WD_INPUT","7":"WD_OUTPUT_N","8":"WD_ENOUT","9":"CTRL_GND"}
    need(all(u1.get(pin, "") == net for pin, net in required.items()), "TPS3431 pin/net mapping drift")
    # WDO_N and ENOUT must remain local: U1 + pullup + one test point only.
    net_endpoints: dict[str, set[str]] = {}
    for ref, fp in footprints.items():
        for pad in fp.Pads():
            if pad.GetNetname():
                net_endpoints.setdefault(pad.GetNetname(), set()).add(f"{ref}.{pad.GetNumber()}")
    need(net_endpoints["WD_OUTPUT_N"] == {"U1.7", "R5.2", "TP2.1"}, f"WDO_N escaped local boundary {net_endpoints['WD_OUTPUT_N']}")
    need(net_endpoints["WD_ENOUT"] == {"U1.8", "R6.2", "TP3.1"}, f"ENOUT escaped local boundary {net_endpoints['WD_ENOUT']}")
    need(not any("ACT" in net.upper() or "PDU" in net.upper() for net in net_endpoints), "actuator/PDU net exists on diagnostic board")
    need(any(zone.GetNetname() == "CTRL_GND" and zone.GetLayer() == pcbnew.F_Cu for zone in board.Zones()), "front ground zone missing")
    need(any(zone.GetNetname() == "CTRL_3V3" and zone.GetLayer() == pcbnew.B_Cu for zone in board.Zones()), "back 3V3 zone missing")
    points = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts and isinstance(drawing, pcbnew.PCB_SHAPE):
            points += [(pcbnew.ToMM(drawing.GetStart().x), pcbnew.ToMM(drawing.GetStart().y)), (pcbnew.ToMM(drawing.GetEnd().x), pcbnew.ToMM(drawing.GetEnd().y))]
    need(points and min(x for x, _ in points) == 0 and max(x for x, _ in points) == 40, "board x envelope drift")
    need(min(y for _, y in points) == 0 and max(y for _, y in points) == 25, "board y envelope drift")


def check_records() -> None:
    contacts = rows(OUT / "connector-contact-map.csv")
    need(len(contacts) == 8 and {row["contact"] for row in contacts} == {str(n) for n in range(1, 9)}, "contact map must cover 1..8")
    by_contact = {row["contact"]: row for row in contacts}
    need({n for n,row in by_contact.items() if row["cable_contact_state"] == "POPULATED"} == {"1","2","3","5"}, "populated cable contact set drift")
    need(all(by_contact[n]["cable_contact_state"] == "PHYSICALLY EMPTY" for n in ("4","6","7","8")), "empty cable contact set drift")
    need("CTRL_GND" in by_contact["3"]["signal_or_disposition"] and "HARD-LOW" in by_contact["3"]["motion_enable_capability"], "permit hard-low mapping absent")
    sources = rows(OUT / "primary-source-register.csv")
    need(len(sources) == 4 and {row["source_id"] for row in sources} == {"WD-S01","WD-S02","WD-S03","WD-S04"}, "primary source register drift")
    need(any("SNVSB66A" in row["document"] and "October 2021" in row["revision_date"] for row in sources), "TI datasheet revision missing")
    need(any("1360/1600/1840" in row["verified"] for row in sources), "TI timeout limits missing")
    bom = rows(OUT / "candidate-bom.csv")
    need(any(row["manufacturer_part_number"] == "TPS3431SDRBR" for row in bom), "exact TI orderable absent")
    need(any(row["manufacturer_part_number"] == "GHR-08V-S" for row in bom), "exact cable housing absent")
    need(any(row["manufacturer_part_number"] == "SSHL-002T-P0.2" for row in bom), "exact contact absent")
    need(sum(row["manufacturer_part_number"] == "SELECTION REQUIRED" for row in bom) >= 4, "passive/fabrication selections overclaimed")
    tests = rows(OUT / "inspection-and-hil-register.csv")
    need(len(tests) == 8 and all(row["result"] == "NOT EXECUTED" for row in tests), "HIL register cannot claim execution")
    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 7 and all(row["state"] == "OPEN" for row in holds), "open holds must remain open")


def check_status_guides_and_native_reports() -> None:
    status = json.loads((OUT / "watchdog-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == IDENTIFIER and status["warning"] == WARNING, "status identity drift")
    need(status["watchdog_timeout_ms"] == {"minimum":1360,"typical":1600,"maximum":1840}, "timeout status drift")
    need(status["jio1_populated_contacts"] == [1,2,3,5] and status["jio1_physically_empty_contacts"] == [4,6,7,8], "status contact set drift")
    need(status["permit_hard_tied_low"] is True and status["watchdog_outputs_local_only"] is True, "fail-closed signal boundary drift")
    need(status["actuator_interfaces_present"] is False and status["actuator_power_path_present"] is False, "actuator boundary drift")
    need(status["functional_safety_credit"] is False and status["pcb_fabricated"] is False and status["fixture_cable_built"] is False and status["hil_executed"] is False, "evidence/credit boundary drift")
    for key in ("procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","energization_authority"):
        need(status[key] is False, f"authority must remain false: {key}")
    need(status["erc_errors"] == status["erc_warnings"] == status["drc_violations"] == status["unconnected_items"] == 0, "native validation status not zero")
    erc = (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    drc = (OUT / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "native ERC is not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "native DRC is not clean")
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in guide and "font-size:16px" in guide, "web legibility floor missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", guide), "web guide contains text below 12 px")
    need("A real watchdog board, with no route to motion" in guide and "zero safety credit" in guide.lower(), "guide outcome/boundary missing")
    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(whole_status["e1_diagnostic_watchdog_native_board_present"] is True and whole_status["e1_diagnostic_watchdog_safety_credit"] is False, "whole-body status integration drift")
    need("electrical/e1-diagnostic-watchdog-p0.1/index.html" in (WHOLE / "README.md").read_text(encoding="utf-8"), "whole-body README integration missing")
    need('id="e1-watchdog"' in (WHOLE / "index.html").read_text(encoding="utf-8"), "whole-body web integration missing")


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source or release package missing")
    need((OUT / "watchdog-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    check_manifest(); check_board(); check_records(); check_status_guides_and_native_reports()
    print("PASS: E1 diagnostic watchdog native KiCad, hard-low permit, local-only outputs, four-contact cable and fail-closed authority verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
