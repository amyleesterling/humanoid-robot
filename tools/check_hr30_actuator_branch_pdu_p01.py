#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 actuator branch PDU P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"hr30/whole-body-p0.1/electrical/actuator-branch-pdu-p0.1"
REL=ROOT/"release/hr30/whole-body-p0.1/electrical/actuator-branch-pdu-p0.1"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(f"FAIL: {message}")
def rows(name: str) -> list[dict]: return list(csv.DictReader((SRC/name).open(encoding="utf-8")))


def main() -> int:
    required={"hr30-actuator-branch-pdu-p0.1.kicad_pro","hr30-actuator-branch-pdu-p0.1.kicad_sch","hr30-actuator-branch-pdu-p0.1.kicad_pcb","01_pdu_boundaries.kicad_sch",*[f"{i+1:02d}_channel_{i}.kicad_sch" for i in range(1,7)],*[f"output/hr30-actuator-branch-pdu-p0.1-in{i}-cu.svg" for i in range(1,9)],"board-instance-channel-allocation.csv","current-limit-torque-consequence-register.csv","component-register.csv","terminal-register.csv","primary-source-register.csv","open-holds.csv","pdu-status.json","index.html","README.md","validation/hr30-actuator-branch-pdu-p0.1-erc.rpt","validation/hr30-actuator-branch-pdu-p0.1-drc.rpt","file-manifest.csv"}
    src_files={p.relative_to(SRC).as_posix() for p in SRC.rglob("*") if p.is_file()}; rel_files={p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file()}
    need(required<=src_files,"required PDU artifacts missing"); need(src_files==rel_files,"PDU source/release file-set mismatch")
    for name in src_files: need(sha(SRC/name)==sha(REL/name),f"PDU source/release mismatch {name}")
    manifest=rows("file-manifest.csv"); need({r["path"] for r in manifest}==src_files-{"file-manifest.csv"},"PDU manifest file set mismatch")
    for row in manifest:
        path=SRC/row["path"]; need(row["sha256"]==sha(path) and int(row["bytes"])==path.stat().st_size,f"PDU manifest mismatch {row['path']}"); need(row["warning"]==WARNING,"PDU manifest warning drift")
    alloc=rows("board-instance-channel-allocation.csv"); need(len(alloc)==30,"allocation must contain five six-channel boards"); need(len({r["board_instance"] for r in alloc})==5,"five board instances missing"); need(sum(r["axis_id"]!="DNP SPARE" for r in alloc)==25,"25 axis allocations missing"); need(sum(r["axis_id"]=="DNP SPARE" for r in alloc)==5,"five DNP spares missing"); need(len({r["axis_id"] for r in alloc if r["axis_id"]!="DNP SPARE"})==25,"axis allocation duplicated")
    need(all(r["walking_state"].startswith("DISABLED") for r in alloc),"walking boundary missing from allocation")
    status=json.loads((SRC/"pdu-status.json").read_text(encoding="utf-8")); need(status["native_schematic_sheet_count"]==8 and status["allocated_axis_channels"]==25 and status["dnp_spare_channels"]==5,"PDU status count drift"); need(status["placement_complete"] and status["routing_complete"] and status["drc_accepted"],"routed candidate status drift"); need(status["copper_layer_count"]==10 and status["board_width_mm"]==150.0 and not status["production_stackup_selected"],"board geometry/stackup boundary drift"); need(not any(status[k] for k in ("walking_power_architecture_complete","reverse_energy_architecture_complete","connector_current_compatibility_validated","thermal_validated","functional_safety_credit","procurement_authority","fabrication_authority","connection_authority","powered_test_authority","motion_authority","energization_authority")),"PDU authority overclaim")
    erc=(SRC/"validation/hr30-actuator-branch-pdu-p0.1-erc.rpt").read_text(encoding="utf-8"); need("ERC messages: 0  Errors 0  Warnings 0" in erc,"PDU ERC is not 0/0")
    drc=(SRC/"validation/hr30-actuator-branch-pdu-p0.1-drc.rpt").read_text(encoding="utf-8"); need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc,"PDU DRC is not 0/0 with zero unconnected pads")
    pcb=(SRC/"hr30-actuator-branch-pdu-p0.1.kicad_pcb").read_text(encoding="utf-8"); need(all(f'"In{i}.Cu"' in pcb for i in range(1,9)),"ten-layer board definition missing")
    holds=rows("open-holds.csv"); need(len(holds)>=8 and all(r["state"].startswith("OPEN") for r in holds),"PDU holds not fail-closed")
    page=(SRC/"index.html").read_text(encoding="utf-8"); need("not the walking power stage" in page.lower() and "drc 0/0" in page.lower() and "production stackup" in page.lower(),"interactive guide hides routed/preliminary boundary")
    print("PASS: HR-30 PDU has 25 allocated routed branch slots; ERC/DRC 0/0; zero unconnected pads; stackup/physical validation and every work authority remain open")
    return 0


if __name__=="__main__": raise SystemExit(main())
