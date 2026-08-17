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
    require(status["allocated_axis_count"] == 25 and status["populated_efuse_count"] == 50 and status["dnp_spare_count"] == 5, "population count wrong")
    require(status["branch_topology_selected_as_p01_candidate"] and status["bidirectional_overcurrent_architecture_defined"], "candidate architecture absent")
    require(status["reverse_energy_path_to_downstream_feed_defined"] and not status["feed_brake_dump_selected"], "energy boundary wrong")
    for key in ("tps25948_pair_manufacturer_application_accepted", "exact_ywp_footprint_released", "pcb_layout_present", "thermal_validated", "walking_power_architecture_complete", "functional_safety_credit", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        require(status[key] is False, f"must remain false: {key}")
    alloc = rows("axis-branch-allocation.csv")
    require(len(alloc) == 30 and sum(r["axis_id"] != "DNP SPARE" for r in alloc) == 25, "allocation register wrong")
    require(sum(r["axis_id"] == "DNP SPARE" for r in alloc) == 5, "DNP count wrong")
    require(all("TPS259482LYWPR" in r["forward_device"] and "TPS259482LYWPR" in r["reverse_device"] for r in alloc if r["axis_id"] != "DNP SPARE"), "paired devices missing")
    pins = rows("component-pin-register.csv")
    for channel in range(1, 7):
        fwd = {r["pin"]: r["net"] for r in pins if r["reference"] == f"U{channel}F"}
        rev = {r["pin"]: r["net"] for r in pins if r["reference"] == f"U{channel}R"}
        require(fwd == {"1": f"CH{channel}_EN", "2": f"CH{channel}_OV_F", "3": f"CH{channel}_PG_F", "4": f"CH{channel}_RCBCTRL", "5": "PDU_12V_IN", "6": f"CH{channel}_MID", "7": f"CH{channel}_DVDT_F", "8": "PDU_0V", "9": f"CH{channel}_ILM_F", "10": f"CH{channel}_ITIMER_F", "11": f"CH{channel}_MID", "12": "PDU_12V_IN"}, f"forward pin map wrong: channel {channel}")
        require(rev == {"1": f"CH{channel}_EN", "2": f"CH{channel}_OV_R", "3": f"CH{channel}_PG_R", "4": f"CH{channel}_RCBCTRL", "5": f"BRANCH_{channel}_12V", "6": f"CH{channel}_MID", "7": f"CH{channel}_DVDT_R", "8": "PDU_0V", "9": f"CH{channel}_ILM_R", "10": f"CH{channel}_ITIMER_R", "11": f"CH{channel}_MID", "12": f"BRANCH_{channel}_12V"}, f"reverse pin map wrong: channel {channel}")
        require(all(r["footprint"] == "" for r in pins if r["reference"] in {f"U{channel}F", f"U{channel}R"}), "unreleased or dimension-near footprint assigned")
    for channel in range(1, 7):
        sheet = (OUT / f"{channel + 1:02d}_paired_channel_{channel}.kicad_sch").read_text(encoding="utf-8")
        for required_net in (f"CH{channel}_PG_F", f"CH{channel}_PG_R", f"CH{channel}_RCBCTRL", f"CH{channel}_DVDT_F", f"CH{channel}_DVDT_R", f"CH{channel}_MID"):
            require(required_net in sheet, f"native channel {channel} missing {required_net}")
    losses = rows("axis-pair-loss-screen.csv")
    require(len(losses) == 25 and sum(r["device_1_to_9a_range_screen"].startswith("FAIL") for r in losses) == 6, "1 A boundary wrong")
    require(len(rows("board-pair-loss-screen.csv")) == 5 and len(rows("feed-brake-dump-boundary.csv")) == 5, "board/feed records wrong")
    options = rows("architecture-option-register.csv")
    require(any(r["option_id"] == "WPS-O03" and r["disposition"].startswith("SELECTED") for r in options), "paired topology not selected")
    require(any(r["option_id"] == "WPS-O02" and r["disposition"].startswith("REJECT") for r in options), "single-device trap not rejected")
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
    require(len(list((OUT / "output").glob("*.svg"))) == 8, "native export count wrong")
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
    print("PASS: paired bidirectional HR-30 walking-power candidate; brake/dump, PCB, validation and all authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
