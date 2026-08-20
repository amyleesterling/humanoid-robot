#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 first-energization-cell hardware P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import cadquery as cq


ROOT=Path(__file__).resolve().parents[1]
WHOLE=ROOT/"hr30"/"whole-body-p0.1"
OUT=WHOLE/"first-energization-cell-hardware-p0.1"
RELEASE=ROOT/"release"/"hr30"/"whole-body-p0.1"/"first-energization-cell-hardware-p0.1"
GEN=ROOT/"tools"/"generate_hr30_first_energization_cell_hardware_p01.py"
ROBOT=WHOLE/"HR-30_p00_neutral_stand_candidate.step"
IDENTIFIER="HR30-FIRST-ENERGIZATION-CELL-HARDWARE-P0.1"
WARNING=("PRELIMINARY - UNBUILT FASTENED CELL HARDWARE CANDIDATE - PURCHASED-PART ENVELOPES ARE NOT MANUFACTURING MODELS - NOT A WALKING GANTRY OR RATED FALL-ARREST SYSTEM - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION")


def need(value: bool,message: str)->None:
    if not value: raise SystemExit(f"FAIL: {message}")


def sha(path: Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str)->list[dict[str,str]]:
    with (OUT/name).open(encoding="utf-8-sig",newline="") as handle: return list(csv.DictReader(handle))


def check_manifest()->None:
    manifest=rows("file-manifest.csv")
    listed={r["path"] for r in manifest}; actual={p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"}
    need(listed==actual,f"manifest set mismatch missing={sorted(actual-listed)} extra={sorted(listed-actual)}")
    for row in manifest:
        path=OUT/row["path"]
        need(path.stat().st_size==int(row["bytes"]) and sha(path)==row["sha256"],f"manifest mismatch {row['path']}")
        need(row["warning"]==WARNING,f"manifest warning drift {row['path']}")
    source={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob("*") if p.is_file()}
    release={p.relative_to(RELEASE).as_posix():sha(p) for p in RELEASE.rglob("*") if p.is_file()}
    need(source==release,"source/release parity failed")


def check_geometry()->None:
    for name in ("HR30_first_energization_cell_hardware_candidate.step","HR30_first_energization_cell_hardware_candidate.glb","HR30_first_energization_cell_hardware_with_robot_candidate.step","HR30_first_energization_cell_hardware_with_robot_candidate.glb"):
        need((OUT/name).is_file() and (OUT/name).stat().st_size>2000,f"missing/substantiveless CAD {name}")
    hardware=cq.importers.importStep(str(OUT/"HR30_first_energization_cell_hardware_candidate.step")).val().BoundingBox()
    whole=cq.importers.importStep(str(OUT/"HR30_first_energization_cell_hardware_with_robot_candidate.step")).val().BoundingBox()
    need(hardware.xlen>=1970 and hardware.ylen>=1770 and hardware.zlen>=1390,"cell/exclusion extent drift")
    need(whole.xlen>=hardware.xlen-.5 and whole.zmax>=1395,"whole robot assembly extent drift")
    binding=json.loads((OUT/"source-binding.json").read_text(encoding="utf-8"))
    need(binding["identifier"]==IDENTIFIER and binding["warning"]==WARNING,"binding identity drift")
    need(binding["robot_step_sha256"]==sha(ROBOT),"robot SHA binding drift")


def check_registers()->None:
    profiles=rows("profile-cut-list.csv")
    need(len(profiles)==31 and len({r["member_id"] for r in profiles})==31,"31 unique profile members required")
    need(sum(r["subsystem"]=="MAIN FRAME" for r in profiles)==13,"13 main-frame profiles required")
    need(sum(r["subsystem"].startswith("DOOR") for r in profiles)==8,"8 door-frame profiles required")
    need(sum(r["subsystem"]=="SUPPORT/CRADLE" for r in profiles)==10,"10 platform/cradle profiles required")
    need(all(r["candidate_profile"].startswith("80/20 40-4040-Lite") and r["cut_released"].startswith("NO") for r in profiles),"profile family/release drift")
    joints=rows("frame-joint-register.csv")
    need(len(joints)==39 and len({r["joint_id"] for r in joints})==39,"39 unique frame/door/platform/cradle joints required")
    need(sum("40-4338" in r["candidate_joint_hardware"] for r in joints)==22,"22 gusset bracket joints required")
    need(sum("40-3897" in r["candidate_joint_hardware"] for r in joints)==14,"14 internal-anchor joints required")
    need(all(r["joint_capacity_released"]=="NO" for r in joints),"joint capacity overclaim")
    fasteners=rows("bracket-fastener-register.csv")
    need(len(fasteners)==206,"206 controlled fastener assemblies required")
    need(sum("75-3422" in r["candidate"] for r in fasteners)==192,"192 bracket/custom-interface fasteners required")
    panels=rows("guard-panel-machining-register.csv")
    need(len(panels)==6 and sum("DOOR" in r["role"] for r in panels)==2,"six panels/two door infills required")
    need(all(r["impact_containment_credit"]=="NONE" and r["fabrication_release"]=="NO" for r in panels),"panel credit/release overclaim")
    gaskets=rows("panel-retention-register.csv")
    need(len(gaskets)==6 and math.isclose(sum(float(r["calculated_cut_length_mm"]) for r in gaskets),23984,abs_tol=.1),"gasket paths/net length drift")
    door=rows("door-hardware-register.csv")
    need(len(door)==11,"six hinges, two handles, two catches and interlock record required")
    need(sum(r["role"]=="PROFILE-TO-PROFILE HINGE" for r in door)==6,"six profile hinges required")
    need(sum(r["role"]=="PROTECTIVE DOOR INTERLOCK" for r in door)==1,"controlled interlock selection record missing")
    need(all(r["safety_interlock_credit"]=="NONE" or r["safety_interlock_credit"].startswith("NONE") for r in door),"door hardware safety overclaim")
    bases=rows("base-anchor-register.csv")
    need(len(bases)==4 and sum(int(r["floor_anchor_quantity"]) for r in bases)==8,"four base plates/eight anchor locations required")
    need(all(r["floor_anchor"].startswith("SELECTION REQUIRED") and r["caster_permitted_for_E7"]=="NO" for r in bases),"base fail-closed boundary drift")
    supports=rows("cradle-hardware-register.csv")
    need(len(supports)==4 and all(r["joint_capacity_credit"]=="NONE" and r["proof_state"]=="NOT EXECUTED" for r in supports),"cradle evidence overclaim")
    cases=rows("structural-load-case-register.csv")
    need(len(cases)==6 and sum(r["status"].startswith("NOT CALCULATED") for r in cases)==4,"load-case calculated/open split drift")
    screens=rows("structural-screen.csv")
    need(len(screens)==1 and screens[0]["screen_id"]=="SC-01","exactly one narrow structural screen required")
    need(math.isclose(float(screens[0]["bending_stress_mpa"]),3.386,rel_tol=.02),"cradle arm stress arithmetic drift")
    need("PROFILE ELASTIC SCREEN ONLY" in screens[0]["credit"],"profile-screen scope overclaim")
    proof=rows("proof-plan.csv")
    need(len(proof)==5 and all(r["proof_load"]=="SELECTION REQUIRED" or r["proof_load"].startswith("SELECTION REQUIRED") for r in proof),"proof load invented")
    need(all(r["state"]=="NOT EXECUTED" and r["authority"]=="NONE" for r in proof),"proof evidence overclaim")
    unresolved=rows("unresolved-inputs.csv")
    need(len(unresolved)==10 and all(r["state"]=="SELECTION REQUIRED" and r["work_authority"]=="NONE" for r in unresolved),"unresolved selection drift")
    bom=rows("candidate-bom.csv")
    need(len(bom)==15 and all(r["procurement_released"]=="NO" for r in bom),"BOM release overclaim")
    need(next(r for r in bom if r["item_id"]=="B-10")["quantity"]=="14","gasket stock quantity drift")
    sources=rows("primary-source-register.csv")
    need(len(sources)==9 and all(r["url"].startswith("https://") and "ACCESSED 2026-08-18" in r["revision_or_access_date"] for r in sources),"primary source register drift")


def check_status_guides()->None:
    status=json.loads((OUT/"hardware-status.json").read_text(encoding="utf-8"))
    need(status["identifier"]==IDENTIFIER and status["warning"]==WARNING,"status identity drift")
    need(status["profile_member_count"]==31 and status["joint_count"]==39 and status["fastener_assembly_count"]==206,"status counts drift")
    for key in ("purchased_part_geometry_is_manufacturing_source","whole_cell_structure_released","guard_impact_validated","restraint_rated","door_interlock_selected","floor_anchor_selected","proof_tests_executed","fer_g02_closed","fer_g10_closed","fer_g11_closed","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority"):
        need(status[key] is False,f"status must remain false: {key}")
    html_text=(OUT/"index.html").read_text(encoding="utf-8")
    need("model-viewer" in html_text and "hardware_with_robot_candidate.glb" in html_text,"interactive whole-cell model missing")
    need("The static cell now has buildable hardware" in html_text,"human outcome missing")
    need("font:17px" in html_text and "font-size:14px" in html_text and "font-size:16px" in html_text,"legibility floors missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px",html_text),"user-facing text below 12 px")
    readme=(OUT/"README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "31 profile members" in readme,"README binding/outcome missing")
    whole_status=json.loads((WHOLE/"package-status.json").read_text(encoding="utf-8"))
    need(whole_status["first_energization_cell_hardware_present"] is True and whole_status["first_energization_cell_hardware_released"] is False,"whole-body status integration drift")
    need("first-energization-cell-hardware-p0.1/index.html" in (WHOLE/"README.md").read_text(encoding="utf-8"),"whole-body README link missing")
    need("id='cell-hardware'" in (WHOLE/"index.html").read_text(encoding="utf-8"),"whole-body guide section missing")


def main()->int:
    need(OUT.is_dir() and RELEASE.is_dir(),"source/release package missing")
    need((OUT/"first-energization-cell-hardware-source.py").read_bytes()==GEN.read_bytes(),"editable source snapshot drift")
    check_manifest(); check_geometry(); check_registers(); check_status_guides()
    print("PASS: complete HR-30 cell hardware successor has framed doors, captured panels, physical joints, anchor interfaces, cut/BOM/proof registers; all validation and work gates fail closed")
    return 0


if __name__=="__main__": raise SystemExit(main())
