#!/usr/bin/env python3
"""Fail-closed checker for HR-30 calibration cable/fault-adapter kit P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
WHOLE=ROOT/"hr30"/"whole-body-p0.1"
OUT=WHOLE/"electrical"/"measurement-chain-calibration-cable-kit-p0.1"
REL=ROOT/"release"/"hr30"/"whole-body-p0.1"/"electrical"/OUT.name
FIXTURE=WHOLE/"electrical"/"measurement-chain-calibration-fixture-p0.1"
WARNING="PRELIMINARY - UNBUILT OFF-ROBOT CALIBRATION CABLE AND FAULT-ADAPTER KIT - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, ROBOT CONNECTION, POWERED ROBOT TESTING, MOTION, WALKING OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value: raise RuntimeError(message)


def rows(name: str) -> list[dict[str,str]]:
    with (OUT/name).open(encoding="utf-8",newline="") as handle: return list(csv.DictReader(handle))


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    assemblies=rows("cable-assembly-register.csv"); contacts=rows("connector-contact-map.csv"); cuts=rows("wire-cut-list.csv"); traveler=rows("assembly-traveler.csv"); tests=rows("inspection-test-register.csv"); bom=rows("candidate-bom.csv"); sources=rows("primary-source-register.csv"); holds=rows("open-holds.csv"); labels=rows("label-register.csv")
    ids={f"CK-{i:02d}" for i in range(1,8)}
    need(len(assemblies)==7 and {r["assembly_id"] for r in assemblies}==ids,"seven-assembly set drift")
    need(all(r["state"].startswith("UNBUILT") for r in assemblies),"built assembly claimed")
    need(len(contacts)==13 and {r["assembly_id"] for r in contacts}==ids,"contact-map count/coverage drift")
    need(sum(1 for r in contacts if "EMPTY" in r["from_contact"] or "NO CONDUCTOR" in r["conductor"])==2,"exactly two controlled empty-contact circuits required")
    reverse=[r for r in contacts if r["assembly_id"]=="CK-03"]
    need({(r["from_contact"],r["to_contact"]) for r in reverse}=={("1","2"),("2","1")},"reverse cable not crossed")
    normal=[r for r in contacts if r["assembly_id"]=="CK-02"]
    need({(r["from_contact"],r["to_contact"]) for r in normal}=={("1","1"),("2","2")},"normal cable not straight")
    need(len(cuts)==8 and {r["assembly_id"] for r in cuts}==ids,"cut-list coverage drift")
    need(len(traveler)==12 and all(r["result"]=="NOT EXECUTED" for r in traveler),"traveler execution drift")
    need(len(tests)==10 and all(r["result"]=="NOT EXECUTED" for r in tests),"inspection execution drift")
    need(len(bom)==12 and all(r["procurement_released"]=="NO" for r in bom),"BOM/procurement boundary drift")
    need({r["order_code"] for r in bom} >= {"BU-0061-M-39-2","BU-0061-M-39-0","5610B2201","1757019","3200742","3203066","1213154","TL930 / part 1616671"},"exact candidate set incomplete")
    need(len(sources)==9 and all(r["url"].startswith("https://") for r in sources),"primary sources incomplete")
    need(len(holds)==10 and all(r["state"]=="OPEN" for r in holds),"open-hold state drift")
    need(len(labels)==7 and {r["assembly_id"] for r in labels}==ids,"label coverage drift")
    need(all(float(r["minimum_text_height_mm"])>=3 for r in labels),"physical label text too small")
    binding=json.loads((OUT/"source-binding.json").read_text(encoding="utf-8"))
    for path,key in ((FIXTURE/"fixture-port-register.csv","fixture_port_register_sha256"),(FIXTURE/"fault-injection-register.csv","fixture_fault_register_sha256"),(FIXTURE/"procedure-register.csv","fixture_procedure_register_sha256")):
        need(binding[key]==digest(path),f"source binding drift: {key}")
    status=json.loads((OUT/"cable-kit-status.json").read_text(encoding="utf-8"))
    need(status["assembly_count"]==7 and status["phoenix_plug_count"]==10 and status["contact_map_rows"]==13,"status count drift")
    for key in ("robot_connection_permitted","parts_received","crimp_coupons_accepted","insulation_test_limit_released","kit_built","inspection_executed","qualified_review_accepted","fer_g11_closed","functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_robot_test_authority","motion_authority","walking_authority","energization_authority"):
        need(status[key] is False,f"unsafe or unsupported true status: {key}")
    manifest=rows("file-manifest.csv")
    expected=sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(sorted(r["path"] for r in manifest)==expected,"manifest file set drift")
    for row in manifest:
        path=OUT/row["path"]; need(path.stat().st_size==int(row["bytes"]) and digest(path)==row["sha256"],f"manifest mismatch: {path}"); need(row["warning"]==WARNING,f"manifest warning drift: {path}")
    source_files=sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()); release_files=sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    need(source_files==release_files,"source/release file set drift")
    for rel in source_files: need((OUT/rel).read_bytes()==(REL/rel).read_bytes(),f"source/release byte drift: {rel}")
    page=(OUT/"index.html").read_text(encoding="utf-8"); root_page=(WHOLE/"index.html").read_text(encoding="utf-8")
    need("font:17px" in page and OUT.name+"/index.html" in root_page,"interactive guide/legibility integration missing")
    need((OUT/"HR30_measurement_calibration_cable_kit_candidate.step").stat().st_size>100000,"STEP appears incomplete")
    need((OUT/"HR30_measurement_calibration_cable_kit_candidate.glb").stat().st_size>10000,"GLB appears incomplete")
    print("PASS: seven off-robot calibration cable/fault assemblies, exact contact maps/cut/ferrule/torque records; unbuilt, FER-G11 and all robot authority open")
    return 0


if __name__=="__main__": raise SystemExit(main())
