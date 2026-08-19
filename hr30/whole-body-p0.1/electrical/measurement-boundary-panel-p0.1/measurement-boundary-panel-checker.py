#!/usr/bin/env python3
"""Deep checker for HR-30 measurement boundary panel P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

try:
    import pcbnew
except ModuleNotFoundError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "measurement-boundary-panel-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "measurement-boundary-panel-p0.1"
PROJECT = "hr30-measurement-boundary-panel-p0.1"
WARNING = "PRELIMINARY - UNBUILT MEASUREMENT FIXTURE - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_manifest_and_release() -> None:
    manifest = rows("file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    require(sorted(r["path"] for r in manifest) == expected, "manifest file set mismatch")
    require(len({r["path"] for r in manifest}) == len(manifest), "duplicate manifest path")
    for row in manifest:
        path = OUT / row["path"]
        require(int(row["bytes"]) == path.stat().st_size, f"manifest byte mismatch {path}")
        require(row["sha256"] == sha(path), f"manifest hash mismatch {path}")
        require(row["warning"] == WARNING, f"manifest warning mismatch {path}")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    require(source_files == release_files, "source/release file-set mismatch")
    for rel in source_files:
        require(sha(OUT / rel) == sha(RELEASE / rel), f"source/release hash mismatch {rel}")


def check_native_board() -> None:
    board_path = OUT / "board" / f"{PROJECT}.kicad_pcb"
    board = pcbnew.LoadBoard(str(board_path))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    require(len(refs) == 59, f"expected 55 circuit components + 4 holes, got {len(refs)}")
    require(sum(1 for ref in refs if re.fullmatch(r"R[1-8][ABCD]", ref)) == 32, "expected 32 analog series resistors")
    require(all(ref in refs for ref in ("J1I","J8I","J1O","J8O","JBT1","JTTL","SW1","D1","RSL1","RSL2","RSL3")), "required footprints missing")
    net_names = {net.GetNetname() for net in board.GetNetInfo().NetsByNetcode().values() if net.GetNetname()}
    analog_nets = {name for name in net_names if re.fullmatch(r"CH[1-8]_(HI|LO)_(IN|MID|OUT)", name)}
    require(len(analog_nets) == 48, f"expected 48 analog nets, got {len(analog_nets)}")
    slate_nets = {name for name in net_names if name.startswith("SLATE_")}
    require(slate_nets == {"SLATE_BAT_POS","SLATE_BAT_RET","SLATE_ACTIVE","SLATE_LED_RET","SLATE_OUT"}, "slate net set mismatch")
    for fp in board.GetFootprints():
        domains=set()
        for pad in fp.Pads():
            name=pad.GetNetname()
            if name.startswith("CH"): domains.add(name.split("_")[0])
            elif name.startswith("SLATE_"): domains.add("SLATE")
        require(len(domains) <= 1, f"footprint bridges channel domains: {fp.GetReference()} {domains}")
    for item in board.Tracks():
        require(item.GetNetname() in analog_nets | slate_nets, f"unexpected routed net {item.GetNetname()}")
    require(board.GetConnectivity().GetUnconnectedCount(False) == 0, "board has unconnected items")
    drc=(OUT/"validation"/f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    erc=(OUT/"validation"/f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    require("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "DRC not clean")
    require("0  Errors 0  Warnings" in erc, "ERC not clean")
    require(sum(1 for _ in OUT.glob("*.kicad_sch")) == 4, "expected root plus three child schematics")


def check_registers() -> None:
    channel = rows("channel-register.csv")
    require(len(channel) == 8 and {r["channel"] for r in channel} == {f"CH-AI-{i:02d}" for i in range(1,9)}, "channel register mismatch")
    require(all(r["shared_reference"] == "NONE" for r in channel), "shared analog reference claimed")
    require(all(math.isclose(float(r["nominal_scale_correction"]),1.0204,rel_tol=0,abs_tol=1e-12) for r in channel), "scale correction mismatch")
    contacts=rows("connector-contact-map.csv")
    require(len(contacts)==36, f"expected 32 analog + 4 slate contacts, got {len(contacts)}")
    require(sum(1 for r in contacts if r["channel"].startswith("CH-AI-"))==32, "analog contact count mismatch")
    calc=rows("current-limit-calculation.csv")
    require(len(calc)==6, "calculation case count mismatch")
    for r in calc:
        voltage=float(r["applied_differential_v"]); count=int(r["remaining_series_resistors"]); loop=count*5100.0
        require(math.isclose(float(r["loop_resistance_ohm"]),loop,abs_tol=1e-9), "loop resistance arithmetic")
        require(math.isclose(float(r["short_current_ma"]),voltage/loop*1000,rel_tol=0,abs_tol=1e-6), "short current arithmetic")
        require(math.isclose(float(r["power_per_remaining_resistor_mw"]),(voltage/loop)**2*5100*1000,rel_tol=0,abs_tol=1e-6), "resistor power arithmetic")
    nets=rows("net-register.csv")
    require(len(nets)==53, f"expected 48 analog + 5 slate nets, got {len(nets)}")
    require(all(r["cross_channel_connection"]=="NO" for r in nets), "cross-channel connection recorded")
    bom=rows("candidate-bom.csv")
    require(sum(1 for r in bom if re.fullmatch(r"R[1-8][ABCD]",r["reference"]))==32, "BOM series resistor count")
    require(any(r["candidate_order_code"]=="RZ0218C" for r in bom), "RZ0218C candidate missing")
    require(any(r["candidate_order_code"]=="781922-01" for r in bom), "NI-9924 candidate missing")
    require(any(r["candidate_order_code"]=="2464" for r in bom), "Keystone holder missing")
    sources=rows("primary-source-register.csv")
    require(len(sources)==9 and all(r["url"].startswith("https://") for r in sources), "primary sources incomplete")
    require(len(rows("inspection-and-calibration-register.csv"))==10, "test register mismatch")
    require(all(r["result"]=="NOT EXECUTED" for r in rows("inspection-and-calibration-register.csv")), "test result overclaim")
    require(len(rows("open-holds.csv"))==10 and all(r["state"]=="OPEN" for r in rows("open-holds.csv")), "holds mismatch")
    require(len(rows("instrumentation-connection-disposition.csv"))==12, "instrumentation disposition mismatch")


def check_status_and_presentation() -> None:
    status=json.loads((OUT/"panel-status.json").read_text(encoding="utf-8"))
    expected_true=("sync_slate_independent_battery","exact_panel_contact_map_present")
    expected_false=("sync_slate_robot_connection_present","field_harness_released","daq_harness_released","fabricated","assembled","calibrated","installed","fer_g11_closed","functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority")
    require(all(status[k] is True for k in expected_true), "required status truth missing")
    require(all(status[k] is False for k in expected_false), "authority or validation overclaim")
    require(status["erc_errors"]==0 and status["erc_warnings"]==0 and status["drc_violations"]==0 and status["unconnected_items"]==0, "validation status mismatch")
    require(status["board_mm"]==[210,134,1.6] and status["component_count"]==55, "board metadata mismatch")
    cad=json.loads((OUT/"cad-status.json").read_text(encoding="utf-8"))
    require(cad["enclosure_candidate"]=="Hammond RZ0218C" and cad["project_pcb_mm"]==[210,134,1.6], "CAD envelope mismatch")
    for name in ("HR30_measurement_boundary_panel_candidate.step","HR30_measurement_boundary_panel_candidate.glb","cad-item-register.csv"):
        require((OUT/name).stat().st_size>100, f"missing/empty CAD artifact {name}")
    html=(OUT/"index.html").read_text(encoding="utf-8")
    require(WARNING in html and "RZ0218C" in html and "FER-G11 remains open" in html, "panel HTML framing mismatch")
    require(not re.search(r"font-size:\s*(?:[0-9]|1[01])px",html), "user-facing text below 12px")
    whole_readme=(WHOLE/"README.md").read_text(encoding="utf-8")
    whole_page=(WHOLE/"index.html").read_text(encoding="utf-8")
    require("HR30-MEASUREMENT-BOUNDARY-P01-START" in whole_readme and "HR30-MEASUREMENT-BOUNDARY-P01-START" in whole_page, "whole-body integration marker missing")
    whole_status=json.loads((WHOLE/"package-status.json").read_text(encoding="utf-8"))
    require(whole_status["measurement_boundary_panel_present"] is True and whole_status["fer_g11_closed"] is False, "whole-body status mismatch")


def main() -> int:
    if pcbnew is None:
        kicad_python = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
        return subprocess.run([str(kicad_python), str(Path(__file__).resolve())], check=False).returncode
    check_manifest_and_release(); check_native_board(); check_registers(); check_status_and_presentation()
    print("PASS: HR-30 measurement boundary native ECAD/CAD, floating-channel topology, calculations, mirrors and fail-closed authority")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
