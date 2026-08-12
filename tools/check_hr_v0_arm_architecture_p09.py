#!/usr/bin/env python3
"""Fail-closed checks for R269 P0.9 widened-stop arm candidate."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_arm_architecture_p09 as gen

ROOT=Path(__file__).resolve().parents[1]


def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(message)


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def close(a: float,b: float,tol: float=1e-6) -> bool: return math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol)


def bbox(shape: cq.Shape) -> tuple[float,...]:
    b=shape.BoundingBox(); return tuple(float(x) for x in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))


def main() -> None:
    out=gen.OUT; p08=gen.P08
    need(out.is_dir(),"P0.9 output missing")
    status=json.loads((out/"p09-status.json").read_text(encoding="utf-8"))
    expected={"identifier":gen.REV,"stop_identifier":gen.STOP_REV,"round":"R269","parent":"HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE","unchanged_parts":["MV0-C01","MV0-C04","MV0-C05"],"changed_parts":["MV0-C06","MV0-C07"],"striker_width_mm":12.0,"catch_width_mm":14.0,"single_rail_stall_nominal_stress_mpa":61.344,"static_yield_ratio":3.912,"collision_sweep_executed":True,"continuous_clearance_executed":True,"selected":False}
    for key,value in expected.items(): need(status.get(key)==value,f"status {key}")
    for key in ("physical_evidence_complete","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(status.get(key) is False,f"authority {key}")
    need(status["warning"]==gen.WARNING,"warning")

    names=("MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step","MV0-C04_H104_to_20-2040_countersunk_adapter.step","MV0-C05_S102_to_40-4040_side_slot_support.step")
    for name in names: need(sha(out/"parts"/name)==sha(p08/"parts"/name),f"unchanged part byte identity {name}")
    new06=cq.importers.importStep(str(out/"parts/MV0-C06_J2_positive_moving_striker_adapter.step")).val()
    new07=cq.importers.importStep(str(out/"parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    old06=cq.importers.importStep(str(p08/"parts/MV0-C06_J2_positive_moving_striker_adapter.step")).val()
    old07=cq.importers.importStep(str(p08/"parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    need(close(new06.BoundingBox().xlen,94.0) and close(new07.BoundingBox().xlen,96.0),"new stop widths")
    need(close(old06.BoundingBox().xlen,82.0) and close(old07.BoundingBox().xlen,84.0),"P0.8 stop widths")
    expected_small={(-16.0,-8.0),(-16.0,8.0),(16.0,-8.0),(16.0,8.0)}
    for part,shape in (("C06",new06),("C07",new07)):
        need(arm.cylindrical_axes(shape,radius=1.35,axis="Y")==expected_small,f"{part} M2.5 axes")
        need(arm.cylindrical_axes(shape,radius=2.75,axis="Y")=={(0.0,-10.0),(0.0,10.0)},f"{part} M5 axes")
    need(new06.Volume()>old06.Volume() and new07.Volume()>old07.Volume(),"stop mass increase")

    transforms08=rows(p08/"transform-schedule.csv"); transforms09=rows(out/"transform-schedule.csv")
    need(transforms08==transforms09,"transform schedule changed")
    collision=rows(out/"collision-sweep.csv")
    need(len(collision)==40001,"collision sweep count")
    need(sum(r["result"]=="COLLISION" for r in collision)==1267,"collision classification changed")
    need(not any(r["result"]=="COLLISION" and float(r["j2_internal_deg"])<=115.0 for r in collision),"collision inside soft limit")
    continuous=json.loads((out/"continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    need(continuous["pair_count"]==69 and continuous["certified_leaf_cell_count"]>=135,"continuous coverage")
    need(float(continuous["minimum_guaranteed_clearance_mm"])>=0.75,"continuous clearance below 0.75 mm")
    stop=json.loads((out/"j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    need(stop["revision"]==gen.STOP_REV and stop["parent_arm_revision"]==gen.REV,"stop identity")
    need(close(stop["nominal_metal_contact_deg"],118.0,.002) and float(stop["nominal_body_clearance_at_metal_contact_mm"])>=2.0,"stop contact/clearance")

    loads=rows(out/"j2-positive-stop-load-screen.csv")
    need(len(loads)==3,"load cases")
    stall=next(r for r in loads if r["case"]=="PUBLISHED_12V_MOMENTARY_STALL_ENDPOINT")
    need(close(stall["single_rail_nominal_stress_mpa"],61.344,.001),"single-rail stress")
    need(close(stall["static_yield_ratio_at_240_mpa"],3.912,.001),"static ratio")
    need(all(r["status"]=="SCREEN ONLY - NOT AN ALLOWABLE OR RELEASE" and r["warning"]==gen.WARNING for r in loads),"load boundary")
    factors=rows(out/"combined-factor-envelope.csv")
    need(len(factors)==7,"factor rows")
    need(next(r for r in factors if r["combined_notch_dynamic_factor"]=="3.50")["screen_result"]=="PASS SCREEN","3.5 screen")
    need(next(r for r in factors if r["combined_notch_dynamic_factor"]=="4.00")["screen_result"]=="FAIL SCREEN","4.0 fail exposure")
    changes=rows(out/"design-change-register.csv")
    need(len(changes)==3 and changes[0]["mass_delta_g"]!="0.000000" and changes[1]["mass_delta_g"]!="0.000000","change register")
    controls=rows(out/"j2-positive-stop-controls.csv")
    need("94.000" in controls[0]["nominal"] and "96.000" in controls[2]["nominal"] and "two 12 x 42 mm" in controls[5]["nominal"],"control widths")
    holds=rows(out/"open-holds.csv"); acceptance=rows(out/"acceptance-matrix.csv")
    need(len(holds)==12 and all(r["state"]=="OPEN" for r in holds),"holds")
    need(len(acceptance)==12 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in acceptance),"acceptance")
    summary=json.loads((out/"architecture-summary.json").read_text(encoding="utf-8"))
    need(summary["revision"]==gen.REV and summary["stop_strength_correction"]["identifier"]==gen.STOP_REV,"summary")
    need((out/"HR-V0_arm_architecture_candidate.step").stat().st_size>1_000_000 and (out/"HR-V0_arm_architecture_candidate.glb").stat().st_size>100_000,"assembly artifacts")
    print("R269 P0.9 widened-stop arm checks: PASS")
    print("40,001 poses / 69 continuous pairs / 12 mm single-rail stall screen 61.344 MPa / 0 authority")
    print(gen.WARNING)


if __name__=="__main__": main()
