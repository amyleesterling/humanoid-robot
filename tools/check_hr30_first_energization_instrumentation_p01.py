#!/usr/bin/env python3
"""Fail-closed checker for HR-30 first-energization instrumentation P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import cadquery as cq


ROOT=Path(__file__).resolve().parents[1]
WHOLE=ROOT/"hr30"/"whole-body-p0.1"
OUT=WHOLE/"first-energization-instrumentation-p0.1"
RELEASE=ROOT/"release"/"hr30"/"whole-body-p0.1"/"first-energization-instrumentation-p0.1"
GEN=ROOT/"tools"/"generate_hr30_first_energization_instrumentation_p01.py"
IDENTIFIER="HR30-FIRST-ENERGIZATION-INSTRUMENTATION-P0.1"
WARNING="PRELIMINARY - UNBUILT FIRST-ENERGIZATION INSTRUMENTATION CANDIDATE - ABORT LIMITS ARE NOT QUALIFIED OR RELEASED - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


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
    step=OUT/"HR30_first_energization_instrument_bench_candidate.step"; glb=OUT/"HR30_first_energization_instrument_bench_candidate.glb"
    need(step.stat().st_size>5000 and glb.stat().st_size>5000,"bench STEP/GLB missing or substantiveless")
    bb=cq.importers.importStep(str(step)).val().BoundingBox()
    need(bb.xlen>=895 and bb.ylen>=595 and bb.zlen>=515,"instrument bench extent drift")
    layout=rows("bench-layout-register.csv")
    need(len(layout)==13 and sum(r["representation"]=="INSTRUMENT INTERFACE ENVELOPE ONLY" for r in layout)==8,"bench/instrument layout count drift")
    need(all(r["manufacturing_source"]=="NO" for r in layout),"instrument envelope manufacturing overclaim")


def check_registers()->None:
    instruments=rows("instrument-register.csv")
    need(len(instruments)==11 and len({r["instrument_id"] for r in instruments})==11,"11 unique candidate instruments required")
    need(next(r for r in instruments if r["instrument_id"]=="INS-08")["order_code"]=="5206068","calibrated DMM part drift")
    need("WHOLE-RAIL CURRENT JACK USE PROHIBITED" in next(r for r in instruments if r["instrument_id"]=="INS-08")["connection_state"],"DMM current misuse not prohibited")
    dio_state=next(r for r in instruments if r["instrument_id"]=="INS-05")["connection_state"]
    need("BATTERY-ONLY" in dio_state and "24 V CONNECTION PROHIBITED" in dio_state,"battery-only/direct-24-V TTL boundary missing")
    channels=rows("measurement-channel-register.csv")
    need(len(channels)==18 and len({r["channel_id"] for r in channels})==18,"18 unique channels required")
    need(sum(r["channel_id"].startswith("CH-AI-") for r in channels)==8,"eight isolated analog channels required")
    need(sum(r["channel_id"].startswith("CH-TC-") for r in channels)==4,"four contact-temperature channels required")
    need(all(r["physical_point_released"]=="NO" and r["calibration_evidence_present"]=="NO" for r in channels),"channel physical/calibration overclaim")
    stages=rows("stage-instrument-binding.csv")
    need([r["stage"] for r in stages]==[f"E{i}" for i in range(8)],"E0-E7 stage binding required")
    need(all(r["execution_state"]=="NOT EXECUTED" and r["test_lead_signoff"]=="REQUIRED" for r in stages),"stage execution/signoff overclaim")
    limits=rows("provisional-abort-limit-register.csv")
    need(len(limits)==9,"nine limit/abort records required")
    need(all(r["automatic_trip"] in {"NONE DEFINED","NONE","SOURCE CURRENT LIMIT IS NOT A VALIDATED BRANCH PROTECTION FUNCTION","local deterministic torque-disable/E-stop path must be separately validated"} for r in limits),"uncontrolled automatic trip claim")
    need(next(r for r in limits if r["limit_id"]=="AL-05")["provisional_observation"]=="NO NUMERIC ABORT CURRENT RELEASED","current limit invented")
    need("no universal Celsius limit invented" in next(r for r in limits if r["limit_id"]=="AL-06")["provisional_observation"],"temperature limit invented")
    calibrations=rows("calibration-and-verification-register.csv")
    need(len(calibrations)==8 and all(r["state"]=="NOT EXECUTED" for r in calibrations),"calibration execution overclaim")
    triggers=rows("trigger-and-timebase-register.csv")
    need(len(triggers)==4 and all(r["released"].startswith("NO") for r in triggers),"trigger/timebase release overclaim")
    connections=rows("probe-connection-register.csv")
    need(len(connections)==12 and all(r["installed"]=="NO" for r in connections),"probe installation overclaim")
    for row in connections:
        if row["channel"].startswith("CH-AI-"):
            need(row["connector_pinout_released"]=="PANEL CONTACTS RELEASED; FIELD/DAQ ENDS OPEN" and row["probe_protection_released"]=="CURRENT-LIMITING DESIGN PRESENT; NOT PHYSICALLY VALIDATED","analog panel disposition mismatch")
        elif row["channel"]=="CH-DIO-01":
            need(row["connector_pinout_released"]=="PANEL CONTACTS RELEASED; NI CONTACTS OPEN" and row["probe_protection_released"]=="BATTERY-ONLY 1K SERIES DESIGN PRESENT; NOT PHYSICALLY VALIDATED","sync panel disposition mismatch")
        else:
            need(row["connector_pinout_released"]=="NO" and row["probe_protection_released"]=="NO","unrelated probe connection overclaim")
    need("direct robot 24 V" in next(r for r in connections if r["connection_id"]=="PC-11")["method"],"digital input prohibition missing")
    schema=rows("data-file-schema.csv")
    need(len(schema)==16 and all(r["required"]=="YES" for r in schema),"raw data schema completeness drift")
    traveler=rows("dry-rehearsal-traveler.csv")
    need(len(traveler)==12 and all(r["state"]=="NOT EXECUTED" and r["abort_on_failure"]=="YES" for r in traveler),"dry rehearsal overclaim")
    sources=rows("primary-source-register.csv")
    need(len(sources)==11 and all(r["url"].startswith("https://") and "2026-08-18" in r["revision_or_access_date"] and r["system_suitability_verified"]=="NO" for r in sources),"source verification/date/suitability drift")
    holds=rows("open-holds.csv")
    need(len(holds)==12 and all(r["state"].startswith("OPEN") and r["authority"]=="NONE" for r in holds),"open hold closure overclaim")
    bom=rows("candidate-bom.csv")
    need(len(bom)==15 and all(r["procurement_released"]=="NO" for r in bom),"candidate BOM release overclaim")


def check_status_guides()->None:
    status=json.loads((OUT/"instrumentation-status.json").read_text(encoding="utf-8"))
    need(status["identifier"]==IDENTIFIER and status["warning"]==WARNING,"status identity drift")
    need(status["instrument_candidate_count"]==11 and status["controlled_channel_count"]==18 and status["stage_count"]==8,"status counts drift")
    for key in ("numeric_current_abort_released","numeric_temperature_abort_released","stopping_time_limit_released","physical_test_points_released","calibration_evidence_present","dry_rehearsal_executed","fer_g11_closed","procurement_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority"):
        need(status[key] is False,f"status must remain false: {key}")
    binding=json.loads((OUT/"source-binding.json").read_text(encoding="utf-8"))
    fer=WHOLE/"first-energization-readiness-p0.1"/"energization-gate-register.csv"; budget=WHOLE/"energy-safety-spine-p0.1"/"current-power-budget.csv"
    need(binding["authoritative_fer_register_sha256"]==sha(fer) and binding["power_budget_sha256"]==sha(budget),"source binding drift")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    need("model-viewer" in page and "Measure first. Energize later." in page,"interactive guide/outcome missing")
    need("font:17px" in page and "font-size:14px" in page and "font-size:16px" in page,"legibility floors missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px",page),"user-facing text below 12 px")
    readme=(OUT/"README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "Eighteen channels" in readme and "FER-G11 remains open" in readme,"README outcome/authority drift")
    whole_status=json.loads((WHOLE/"package-status.json").read_text(encoding="utf-8"))
    need(whole_status["first_energization_instrumentation_present"] is True and whole_status["fer_g11_closed"] is False,"whole-body status integration drift")
    need("first-energization-instrumentation-p0.1/index.html" in (WHOLE/"README.md").read_text(encoding="utf-8"),"whole-body README link missing")
    need("id='fer-instruments'" in (WHOLE/"index.html").read_text(encoding="utf-8"),"whole-body guide section missing")


def main()->int:
    need(OUT.is_dir() and RELEASE.is_dir(),"source/release package missing")
    need((OUT/"first-energization-instrumentation-source.py").read_bytes()==GEN.read_bytes(),"editable source snapshot drift")
    check_manifest(); check_geometry(); check_registers(); check_status_guides()
    print("PASS: HR-30 E0-E7 instrumentation has exact candidate hardware, 18 controlled channels, timing/calibration/data/traveler artifacts; FER-G11 and all work authority remain open")
    return 0


if __name__=="__main__": raise SystemExit(main())
