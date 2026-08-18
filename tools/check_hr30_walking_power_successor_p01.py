#!/usr/bin/env python3
"""Validate the HR-30 bidirectional walking-power successor package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "walking-power-successor-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
WARNING = "PRELIMINARY - WALKING-POWER ARCHITECTURE CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def main() -> int:
    required = {
        "README.md", "index.html", "bidirectional-branch-schematic.svg", "source-binding.csv",
        "primary-source-register.csv", "architecture-option-register.csv", "energy-flow-state-register.csv",
        "axis-branch-allocation.csv", "component-pin-register.csv", "axis-pair-loss-screen.csv", "board-pair-loss-screen.csv",
        "feed-brake-dump-boundary.csv", "open-holds.csv", "walking-power-status.json", "file-manifest.csv",
        "hr30-walking-power-successor-p0.1.kicad_pro", "hr30-walking-power-successor-p0.1.kicad_sch",
        "hr30-walking-power-successor-p0.1.kicad_pcb", "ProjectButton_WPS.pretty",
        "hr30-walking-power-successor-p0.1.kicad_sym", "sym-lib-table", "fp-lib-table",
        "01_system_boundaries.kicad_sch", "02_paired_channel_1.kicad_sch", "03_paired_channel_2.kicad_sch",
        "04_paired_channel_3.kicad_sch", "05_paired_channel_4.kicad_sch", "06_paired_channel_5.kicad_sch",
        "07_paired_channel_6.kicad_sch", "validation", "output",
    }
    require(OUT.is_dir() and RELEASE.is_dir(), "walking-power source/release missing")
    require({p.name for p in OUT.iterdir()} == required, "unexpected source file set")
    require({p.name for p in RELEASE.iterdir()} == required, "unexpected release file set")
    for path in OUT.rglob("*"):
        if path.is_file():
            mirror = RELEASE / path.relative_to(OUT)
            require(mirror.is_file() and sha(path) == sha(mirror), f"source/release mismatch: {path.relative_to(OUT)}")
    status = json.loads((OUT / "walking-power-status.json").read_text(encoding="utf-8"))
    require(status["native_schematic_sheet_count"] == 8 and status["kicad_erc_errors"] == 0 and status["kicad_erc_warnings"] == 0, "KiCad status wrong")
    require(status["allocated_axis_count"] == 25 and status["populated_efuse_count"] == 50 and status["dnp_spare_count"] == 23, "population count wrong")
    require(status["authoritative_bus_count"] == 8 and status["board_instance_count"] == 8, "eight-bus board count wrong")
    require(status["one_bus_per_board_instance"] and not status["multi_bus_input_short_present"], "bus isolation disposition wrong")
    require(status["branch_topology_selected_as_p01_candidate"] and status["bidirectional_overcurrent_architecture_defined"], "candidate architecture absent")
    require(status["reverse_energy_path_to_downstream_feed_defined"] and not status["feed_brake_dump_selected"], "energy boundary wrong")
    require(status["exact_ywp_land_pattern_present"] and status["pcb_layout_present"] and status["pcb_routing_complete"] and status["pcb_drc_accepted"], "routed exact-land-pattern PCB evidence absent")
    require(status["pcb_unconnected_pads"] == 0 and status["board_width_mm"] == 150.0 and status["board_height_mm"] == 68.0 and status["copper_layer_count"] == 10, "PCB geometry/connectivity status wrong")
    require(status["validation"]["drc_errors"] == 0 and status["validation"]["drc_warnings"] == 0 and status["validation"]["unconnected_pads"] == 0, "DRC status wrong")
    for key in ("tps25948_pair_manufacturer_application_accepted", "exact_ywp_footprint_released", "production_stackup_selected", "thermal_validated", "walking_power_architecture_complete", "functional_safety_credit", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        require(status[key] is False, f"must remain false: {key}")
    alloc = rows("axis-branch-allocation.csv")
    require(len(alloc) == 48 and sum(r["axis_id"] != "DNP SPARE" for r in alloc) == 25, "allocation register wrong")
    require(sum(r["axis_id"] == "DNP SPARE" for r in alloc) == 23, "DNP count wrong")
    expected_feeds = {
        "RS-LLEG": ("WPS-RS-LLEG", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-RLEG": ("WPS-RS-RLEG", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-LARM": ("WPS-RS-LARM", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-RARM": ("WPS-RS-RARM", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "RS-WAIST": ("WPS-RS-WAIST", "ACT_MAIN_SAFE_12V", "ACT_0V_CONTROLLED", "12 V nominal candidate"),
        "TTL-LDIST": ("WPS-TTL-LDIST", "TTL_LDIST_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
        "TTL-RDIST": ("WPS-TTL-RDIST", "TTL_RDIST_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
        "TTL-HEAD": ("WPS-TTL-HEAD", "TTL_HEAD_SAFE_9V", "ACT_0V_CONTROLLED", "9 V regulated candidate"),
    }
    require(set(r["bus_id"] for r in alloc) == set(expected_feeds), "allocation bus set wrong")
    for bus_id, (board, pos, ret, voltage) in expected_feeds.items():
        members = [r for r in alloc if r["bus_id"] == bus_id]
        require(len(members) == 6 and {r["board_instance"] for r in members} == {board}, f"board isolation wrong: {bus_id}")
        require({r["feed_positive_net"] for r in members} == {pos} and {r["feed_return_net"] for r in members} == {ret}, f"feed nets wrong: {bus_id}")
        require({r["nominal_feed_voltage"] for r in members} == {voltage}, f"feed voltage wrong: {bus_id}")
    require(all("TPS259482LYWPR" in r["forward_device"] and "TPS259482LYWPR" in r["reverse_device"] for r in alloc if r["axis_id"] != "DNP SPARE"), "paired devices missing")
    pins = rows("component-pin-register.csv")
    for channel in range(1, 7):
        fwd = {r["pin"]: r["net"] for r in pins if r["reference"] == f"U{channel}F"}
        rev = {r["pin"]: r["net"] for r in pins if r["reference"] == f"U{channel}R"}
        require(fwd == {"1": f"CH{channel}_EN", "2": f"CH{channel}_OV_F", "3": f"CH{channel}_PG_F", "4": f"CH{channel}_RCBCTRL", "5": "FEED_VPOS", "6": f"CH{channel}_MID", "7": f"CH{channel}_DVDT_F", "8": "FEED_0V", "9": f"CH{channel}_ILM_F", "10": f"CH{channel}_ITIMER_F", "11": f"CH{channel}_MID", "12": "FEED_VPOS"}, f"forward pin map wrong: channel {channel}")
        require(rev == {"1": f"CH{channel}_EN", "2": f"CH{channel}_OV_R", "3": f"CH{channel}_PG_R", "4": f"CH{channel}_RCBCTRL", "5": f"BRANCH_{channel}_VPOS", "6": f"CH{channel}_MID", "7": f"CH{channel}_DVDT_R", "8": "FEED_0V", "9": f"CH{channel}_ILM_R", "10": f"CH{channel}_ITIMER_R", "11": f"CH{channel}_MID", "12": f"BRANCH_{channel}_VPOS"}, f"reverse pin map wrong: channel {channel}")
        require(all(r["footprint"] == "ProjectButton_WPS:TI_YWP0012A_PowerWCSP_2.441x1.728mm" for r in pins if r["reference"] in {f"U{channel}F", f"U{channel}R"}), "exact YWP footprint binding absent")
        ov_f = {r["pin"]: r["net"] for r in pins if r["reference"] == f"R{channel}OF"}
        ov_r = {r["pin"]: r["net"] for r in pins if r["reference"] == f"R{channel}OR"}
        require(ov_f == {"1": f"CH{channel}_OV_F", "2": "FEED_0V"} and ov_r == {"1": f"CH{channel}_OV_R", "2": "FEED_0V"}, f"OVLO anti-float candidate missing: channel {channel}")
    for channel in range(1, 7):
        sheet = (OUT / f"{channel + 1:02d}_paired_channel_{channel}.kicad_sch").read_text(encoding="utf-8")
        for required_net in (f"CH{channel}_PG_F", f"CH{channel}_PG_R", f"CH{channel}_RCBCTRL", f"CH{channel}_DVDT_F", f"CH{channel}_DVDT_R", f"CH{channel}_MID"):
            require(required_net in sheet, f"native channel {channel} missing {required_net}")
    losses = rows("axis-pair-loss-screen.csv")
    require(len(losses) == 25 and sum(r["device_1_to_9a_range_screen"].startswith("FAIL") for r in losses) == 6, "1 A boundary wrong")
    require(len(rows("board-pair-loss-screen.csv")) == 8 and len(rows("feed-brake-dump-boundary.csv")) == 8, "board/feed records wrong")
    options = rows("architecture-option-register.csv")
    require(any(r["option_id"] == "WPS-O03" and r["disposition"].startswith("SELECTED") for r in options), "paired topology not selected")
    require(any(r["option_id"] == "WPS-O02" and r["disposition"].startswith("REJECT") for r in options), "single-device trap not rejected")
    require(any(r["option_id"] == "WPS-O06" and r["disposition"].startswith("REJECT") for r in options), "five-board cross-connection trap not rejected")
    require(any(r["option_id"] == "WPS-O07" and r["disposition"].startswith("SELECTED") for r in options), "eight isolated bus feeds not selected")
    states = rows("energy-flow-state-register.csv")
    require(len(states) == 8 and any(r["state_id"] == "WPS-E3" and "AXIS" in r["energy_path"] for r in states), "regenerative state missing")
    holds = rows("open-holds.csv")
    require(len(holds) == 12 and all(r["state"] == "OPEN" for r in holds), "holds wrong")
    for name in ("source-binding.csv", "primary-source-register.csv", "architecture-option-register.csv", "energy-flow-state-register.csv", "axis-branch-allocation.csv", "component-pin-register.csv", "axis-pair-loss-screen.csv", "board-pair-loss-screen.csv", "feed-brake-dump-boundary.csv", "open-holds.csv"):
        require(all(r["warning"] == WARNING for r in rows(name)), f"warning drift: {name}")
    bindings = rows("source-binding.csv")
    require(len(bindings) == 6, "source binding count wrong")
    for row in bindings:
        path = ROOT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"source binding mismatch: {row['binding_id']}")
    report = (OUT / "validation/hr30-walking-power-successor-p0.1-erc.rpt").read_text(encoding="utf-8", errors="replace")
    require("0  Errors 0  Warnings" in report, "complete ERC report is not 0/0")
    drc = (OUT / "validation/hr30-walking-power-successor-p0.1-drc.rpt").read_text(encoding="utf-8", errors="replace")
    require("found 0 drc violations" in drc.lower() and "found 0 unconnected pads" in drc.lower(), "complete DRC report is not 0/0")
    require(len(list((OUT / "output").glob("*.svg"))) == 18, "native schematic/PCB export count wrong")
    footprint = (OUT / "ProjectButton_WPS.pretty/TI_YWP0012A_PowerWCSP_2.441x1.728mm.kicad_mod").read_text(encoding="utf-8")
    require(footprint.count('(pad "') == 12, "YWP footprint must contain exactly 12 lands")
    for snippet in ('(pad "1" smd roundrect (at -1.060 0.675)', '(pad "4" smd roundrect (at -1.060 -0.675)', '(pad "5" smd roundrect (at -0.476 -0.450)', '(pad "6" smd roundrect (at 0.476 -0.450)', '(pad "7" smd roundrect (at 1.060 -0.675)', '(pad "10" smd roundrect (at 1.060 0.675)', '(pad "11" smd roundrect (at 0.476 0.450)', '(pad "12" smd roundrect (at -0.476 0.450)'):
        require(snippet in footprint, f"YWP coordinate drift: {snippet}")
    manifest = rows("file-manifest.csv")
    for row in manifest:
        path = OUT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {row['path']}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    require("font-size:16px" in page and "font-size:11" not in page and "font-size:10" not in page, "web legibility floor wrong")
    root = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    require(root["walking_power_successor_package_present"] and not root["walking_power_architecture_complete"] and not root["walking_power_energization_authority"], "root integration wrong")
    require((WHOLE / "README.md").read_text(encoding="utf-8").count("HR30-WALKING-POWER-P01-README-START") == 1, "README integration wrong")
    require((WHOLE / "index.html").read_text(encoding="utf-8").count("HR30-WALKING-POWER-P01-START") == 1, "web integration wrong")
    print("PASS: exact YWP land pattern and routed ten-layer HR-30 walking-power PCB; eight bus domains retained; stackup/DFM/brake-dump/thermal and all authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
