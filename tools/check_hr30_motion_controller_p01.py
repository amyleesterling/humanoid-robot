#!/usr/bin/env python3
"""Fail-closed validation for the HR-30 motion-controller P0.1 package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "hr30" / "whole-body-p0.1" / "electrical" / "motion-controller-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "motion-controller-p0.1"
PROJECT = "hr30-motion-controller-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition: raise SystemExit("FAIL: " + message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    require(PKG.is_dir() and REL.is_dir(), "source/release controller package missing")
    schematics = sorted(PKG.glob("*.kicad_sch"))
    require(len(schematics) == 6, "root plus five native schematic sheets required")
    require((PKG / "board" / f"{PROJECT}.kicad_pcb").stat().st_size > 1_000_000, "native routed PCB missing")
    erc = (PKG / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    require(re.search(r"ERC messages:\s+0\s+Errors\s+0\s+Warnings", erc) is not None, "schematic ERC is not 0/0")
    drc = (PKG / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    found = re.search(r"Found\s+(\d+)\s+DRC violations", drc)
    require(found is not None and int(found.group(1)) == 0, "native PCB DRC is not zero")
    categories: dict[str, int] = {}
    for value in re.findall(r"^\[([^]]+)\]", drc, re.MULTILINE): categories[value] = categories.get(value, 0) + 1
    require(categories.get("unconnected_items", 0) == 0 and "Found 0 unconnected pads" in drc, "native PCB still has unconnected items")
    status = json.loads((PKG / "controller-status.json").read_text(encoding="utf-8"))
    require(status["drc_violations"] == int(found.group(1)) and status["unconnected_item_count"] == categories.get("unconnected_items", 0), "status/report DRC mismatch")
    require(status["erc_errors"] == status["erc_warnings"] == 0 and status["carrier_power_contact_mapping_reconciled"] and status["right_distal_uart_package_pin_defect_corrected"], "controller status does not expose verified schematic/interface advancement")
    require(status["routing_complete"] and not status["fabrication_release"] and not status["functional_safety_credit"], "routing advancement or safety boundary is wrong")
    require(not any(status[key] for key in ("procurement_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority")), "work authority overclaimed")

    terminals = rows(PKG / "terminal-register.csv")
    for ref in ("JCA1", "JCB1"):
        mapping = {row["pad"]: row["net"] for row in terminals if row["reference"] == ref and row["pad"] in {"1", "2", "3"}}
        require(mapping == {"1": "CTRL_GND", "2": "CTRL_5V", "3": "CTRL_3V3"}, f"{ref} power mapping drift")
        require(not any("VDD" in row["net"] for row in terminals if row["reference"] == ref), f"actuator VDD entered {ref}")
    uart = rows(PKG / "uart-pin-map.csv")
    require(len(uart) == 21 and {row["bus_id"] for row in uart} == {"RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM", "RS-WAIST", "TTL-LDIST", "TTL-RDIST", "TTL-HEAD"}, "eight-bus MCU map incomplete")
    rdist = {row["mcu_port"]: row["lqfp144_package_pin"] for row in uart if row["bus_id"] == "TTL-RDIST"}
    require(rdist == {"PE8": "59", "PE9": "60"}, "right-distal package-pin defect returned")
    require(not ({"61", "62"} & {row["lqfp144_package_pin"] for row in uart}), "UART signal assigned to STM32 VSS/VDD package pin")
    gpio = rows(PKG / "control-gpio-map.csv")
    require(len(gpio) == 10 and {"SAFETY_PERMIT_HARDWIRED", "MOTION_WD_HEARTBEAT", "ACTION_SPI_MOSI", "ACTION_READY"} <= {row["net"] for row in gpio}, "deterministic control/action GPIO boundary incomplete")
    require("zero functional-safety credit" in " ".join(row["deterministic_role"] for row in gpio).lower(), "ordinary MCU permit boundary lacks zero-safety disclosure")
    components = rows(PKG / "component-register.csv")
    by_ref = {row["reference"]: row for row in components}
    require(by_ref["U1"]["manufacturer_part_number"] == "STM32H743ZIT6" and by_ref["U2"]["manufacturer_part_number"] == "TPS62132RGTT" and by_ref["L1"]["manufacturer_part_number"] == "XAL5030-222MEC", "controller power/compute order-code candidate drift")
    require(len(rows(PKG / "primary-source-register.csv")) == 5 and len(rows(PKG / "open-holds.csv")) == 8, "source or hold register incomplete")
    guide = (PKG / "index.html").read_text(encoding="utf-8")
    require(WARNING in guide and "DRC 0" in guide and "font:17px/1.55" in guide and "not a fabrication release" in guide, "web guide hides result/boundary or violates legibility")
    require((PKG / "output" / f"{PROJECT}-front.svg").stat().st_size > 100_000, "interactive PCB visual missing")
    require(sha(PKG / "motion-controller-source.py") == sha(ROOT / "tools" / "generate_hr30_motion_controller_p01.py"), "controller source snapshot drift")
    manifest = rows(PKG / "file-manifest.csv")
    files = {path.relative_to(PKG).as_posix() for path in PKG.rglob("*") if path.is_file()}
    require({row["path"] for row in manifest} == files - {"file-manifest.csv"}, "controller manifest file set mismatch")
    require(all(int(row["bytes"]) == (PKG / row["path"]).stat().st_size and row["sha256"] == sha(PKG / row["path"]) for row in manifest), "controller manifest bytes/hash mismatch")
    source_files = {path.relative_to(PKG).as_posix() for path in PKG.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file()}
    require(source_files == release_files and all(sha(path) == sha(REL / path.relative_to(PKG)) for path in PKG.rglob("*") if path.is_file()), "controller source/release parity failed")
    root_status = json.loads((ROOT / "hr30" / "whole-body-p0.1" / "package-status.json").read_text(encoding="utf-8"))
    require(root_status["motion_controller_drc_violations"] == 0 and root_status["motion_controller_unconnected_item_count"] == 0 and root_status["motion_controller_routing_complete"] and root_status["motion_controller_drc_clean"] and root_status["motion_controller_layout_blocked"], "root package hides DRC result or unreleased boundary")
    root_page = (ROOT / "hr30" / "whole-body-p0.1" / "index.html").read_text(encoding="utf-8")
    require(root_page.count("HR30-MOTION-CONTROLLER-P01-START") == 1 and f"DRC {status['drc_violations']}" in root_page, "whole-body page lacks blocked controller artifact")
    print("PASS: HR-30 controller has six native sheets, ERC 0/0, DRC 0, zero unconnected items, corrected carrier/UART pins and a visible routed PCB candidate; physical/application validation remains open with no fabrication, safety or work authority")
    return 0


if __name__ == "__main__": raise SystemExit(main())
