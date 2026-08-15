#!/usr/bin/env python3
"""Generate R269 P0.9 widened J2-stop candidate without touching P0.8."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"cad/hr-v0/generated/arm-architecture-p0.9-stop-strength"
P08=ROOT/"cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated"
REV="HR-V0-ARM-ARCH-P0.9-STOP-STRENGTH-CANDIDATE"
STOP_REV="HR-V0-J2-STOP-P0.2"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
STRIKER_INNER=35.0
STRIKER_OUTER=47.0
CATCH_INNER=34.0
CATCH_OUTER=48.0
PROJECT_MIN_YIELD_MPA=240.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, fields: list[str], records: list[dict[str,object]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n"); writer.writeheader(); writer.writerows(records)


def load_exact(part_id: str, filename: str) -> cq.Shape:
    path=P08/"parts"/filename
    if not path.is_file(): raise RuntimeError(f"missing P0.8 source {path}")
    return cq.importers.importStep(str(path)).val()


def translated(shape: cq.Shape, y0: float) -> cq.Shape:
    return shape if math.isclose(y0,0.0) else shape.translate((0.0,y0,0.0))


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    exact={
        "MV0-C01":load_exact("MV0-C01","MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step"),
        "MV0-C04":load_exact("MV0-C04","MV0-C04_H104_to_20-2040_countersunk_adapter.step"),
        "MV0-C05":load_exact("MV0-C05","MV0-C05_S102_to_40-4040_side_slot_support.step"),
    }
    arm.OUT=OUT; arm.REVISION=REV
    arm.END_CSK_D=11.30; arm.END_CSK_DEPTH=2.90
    arm.STOP_STRIKER_INNER_X_MM=STRIKER_INNER; arm.STOP_STRIKER_OUTER_X_MM=STRIKER_OUTER
    arm.STOP_CATCH_INNER_X_MM=CATCH_INNER; arm.STOP_CATCH_OUTER_X_MM=CATCH_OUTER
    arm.adapter=lambda y0:translated(exact["MV0-C01"],y0)
    arm.gripper_adapter=lambda y0:translated(exact["MV0-C04"],y0)
    arm.shoulder_support_plate=lambda:exact["MV0-C05"]
    result=arm.main()
    if result: return result

    # Preserve the three unchanged controlled STEP byte identities in the
    # successor part directory. The combined assembly was built from these
    # imported solids before the base generator re-exported its part files.
    for filename in (
        "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step",
        "MV0-C04_H104_to_20-2040_countersunk_adapter.step",
        "MV0-C05_S102_to_40-4040_side_slot_support.step",
    ):
        shutil.copy2(P08/"parts"/filename,OUT/"parts"/filename)

    analysis=json.loads((OUT/"j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    radius=float(analysis["contact_radius_mm"])
    lever=arm.STOP_STRIKER_TOP_Z_MM+15.0
    width=STRIKER_OUTER-STRIKER_INNER
    z=width*arm.PLATE_MIN_T**2/6.0
    torque_cases=[("R69_PROOF_SCREEN",3.475348,"inherited static proof-screen input; qualified acceptance open"),("RAW800_IDEAL_STALL_LINE",5.18,"ideal current-to-torque line only; not a safety-rated limit"),("PUBLISHED_12V_MOMENTARY_STALL_ENDPOINT",10.6,"published momentary endpoint; continuous output is lower and unverified")]
    loads=[]
    for case,torque,basis in torque_cases:
        force=torque*1000.0/radius
        equal=force/2.0*lever/z
        single=force*lever/z
        loads.append({"case":case,"torque_input_nm":f"{torque:.6f}","contact_radius_mm":f"{radius:.6f}","total_tangential_force_n":f"{force:.3f}","equal_share_force_per_rail_n":f"{force/2.0:.3f}","equal_share_nominal_stress_mpa":f"{equal:.3f}","single_rail_force_n":f"{force:.3f}","single_rail_nominal_stress_mpa":f"{single:.3f}","static_yield_ratio_at_240_mpa":f"{PROJECT_MIN_YIELD_MPA/single:.3f}","basis":basis,"status":"SCREEN ONLY - NOT AN ALLOWABLE OR RELEASE","warning":WARNING})
    write_csv(OUT/"j2-positive-stop-load-screen.csv",list(loads[0]),loads)

    stall=float(loads[-1]["single_rail_nominal_stress_mpa"])
    factors=[]
    for factor in (1.0,1.5,2.0,2.5,3.0,3.5,4.0):
        stress=stall*factor
        factors.append({"case_id":f"CF-{int(factor*10):02d}","load_case":"published 12 V momentary stall endpoint; one rail carries 100 percent","combined_notch_dynamic_factor":f"{factor:.2f}","nominal_stress_mpa":f"{stall:.3f}","factored_stress_mpa":f"{stress:.3f}","project_mtr_yield_threshold_mpa":f"{PROJECT_MIN_YIELD_MPA:.1f}","ratio":f"{PROJECT_MIN_YIELD_MPA/stress:.3f}","screen_result":"PASS SCREEN" if stress<=PROJECT_MIN_YIELD_MPA else "FAIL SCREEN","release_boundary":"factor allocation, fatigue, contact, deformation and proof remain SELECTION REQUIRED","warning":WARNING})
    write_csv(OUT/"combined-factor-envelope.csv",list(factors[0]),factors)

    old_c06=cq.importers.importStep(str(P08/"parts/MV0-C06_J2_positive_moving_striker_adapter.step")).val()
    old_c07=cq.importers.importStep(str(P08/"parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    new_c06=cq.importers.importStep(str(OUT/"parts/MV0-C06_J2_positive_moving_striker_adapter.step")).val()
    new_c07=cq.importers.importStep(str(OUT/"parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    changes=[
        {"change_id":"R269-CH-01","part_id":"MV0-C06","feature":"two striker rails","p08":"6.0 mm each; X=35..41 and -41..-35","p09":"12.0 mm each; X=35..47 and -47..-35","reason":"double section modulus without moving the actuator-side edge","geometry_effect":"outer envelope grows 82 to 94 mm","mass_delta_g":f"{(new_c06.Volume()-old_c06.Volume())/1000*2.70:.6f}","status":"UNACCEPTED DESIGN CANDIDATE","warning":WARNING},
        {"change_id":"R269-CH-02","part_id":"MV0-C07","feature":"two catch rails","p08":"8.0 mm each; X=34..42 and -42..-34","p09":"14.0 mm each; X=34..48 and -48..-34","reason":"retain 1 mm lateral catch border around each 12 mm striker","geometry_effect":"outer envelope grows 84 to 96 mm","mass_delta_g":f"{(new_c07.Volume()-old_c07.Volume())/1000*2.70:.6f}","status":"UNACCEPTED DESIGN CANDIDATE","warning":WARNING},
        {"change_id":"R269-CH-03","part_id":"MV0-C01/C04/C05","feature":"all geometry","p08":"exact controlled STEP identity","p09":"byte-identical imported STEP geometry","reason":"no change needed","geometry_effect":"none","mass_delta_g":"0.000000","status":"UNCHANGED SOURCE GEOMETRY","warning":WARNING},
    ]
    write_csv(OUT/"design-change-register.csv",list(changes[0]),changes)

    controls=list(csv.DictReader((OUT/"j2-positive-stop-controls.csv").open(newline="",encoding="utf-8")))
    for row in controls:
        if row["control_id"]=="STOP-001": row["nominal"]=row["nominal"].replace("82.000", "94.000")
        if row["control_id"]=="STOP-003": row["nominal"]=row["nominal"].replace("84.000", "96.000")
        if row["control_id"]=="STOP-006": row["nominal"]=row["nominal"].replace("two 6 x 42 mm", "two 12 x 42 mm")
        row["warning"]=WARNING
    write_csv(OUT/"j2-positive-stop-controls.csv",list(controls[0]),controls)

    holds_text=[
        "Qualified reviewer accepts the widened outward envelope and load-case allocation",
        "Guard, receiver, cable and operator-clearance envelopes are regenerated and accepted",
        "Exact dynamic amplification and stress-concentration factors are established",
        "Nonlinear contact/prying/local deformation analysis is accepted",
        "Material certificate proves the configuration-bound yield threshold and other required properties",
        "C06/C07 successor drawings, datum controls and FAI plan are accepted",
        "Bumper material, retention, force-stroke, temperature and life are selected and validated",
        "Single-rail and two-rail proof fixtures and acceptance limits are qualified",
        "Five-part provider DFM and first articles are accepted",
        "Received arm stack passes unpowered fit, contact-mark and deformation inspection",
        "Physical stopping tests establish overtravel, rebound, peak load and no-damage behavior",
        "Configuration-bound qualified release and separate work authority are signed",
    ]
    holds=[{"hold_id":f"R269-H{i:02d}","hold":h,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS P0.9 SELECTION/FABRICATION/MOTION","warning":WARNING} for i,h in enumerate(holds_text,1)]
    write_csv(OUT/"open-holds.csv",list(holds[0]),holds)
    acceptance=[{"acceptance_id":f"R269-ACC-{i:02d}","criterion":h,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,h in enumerate(holds_text,1)]
    write_csv(OUT/"acceptance-matrix.csv",list(acceptance[0]),acceptance)

    summary=json.loads((OUT/"architecture-summary.json").read_text(encoding="utf-8"))
    summary["revision"]=REV
    summary["disposition"]="unaccepted widened J2 stop candidate; three P0.8 custom parts unchanged, C06/C07 widened outward; full collision/clearance evidence regenerated; all physical, guard, cable, load-factor, material, DFM, FAI, stopping and qualified-release holds open"
    summary["stop_strength_correction"]={"identifier":STOP_REV,"p08_striker_width_mm":6.0,"p09_striker_width_mm":12.0,"p08_catch_width_mm":8.0,"p09_catch_width_mm":14.0,"single_rail_stall_nominal_stress_mpa":round(stall,3),"project_mtr_yield_threshold_mpa":PROJECT_MIN_YIELD_MPA,"static_ratio":round(PROJECT_MIN_YIELD_MPA/stall,3),"load_factor_acceptance":"SELECTION REQUIRED"}
    (OUT/"architecture-summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    analysis["revision"]=STOP_REV; analysis["parent_arm_revision"]=REV; analysis["architecture"]="twin widened outward 12 mm moving striker rails against 14 mm recessed catch rails; actuator-side edges unchanged"; analysis["status"]="UNACCEPTED WIDENED STOP CAD CANDIDATE; LOAD FACTORS, GUARD/CABLE ENVELOPES, MATERIAL, PHYSICAL TEST AND QUALIFIED RELEASE OPEN"
    (OUT/"j2-positive-stop-analysis.json").write_text(json.dumps(analysis,indent=2)+"\n",encoding="utf-8")
    status={"identifier":REV,"stop_identifier":STOP_REV,"round":"R269","date":"2026-08-12","parent":"HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE","unchanged_parts":["MV0-C01","MV0-C04","MV0-C05"],"changed_parts":["MV0-C06","MV0-C07"],"striker_width_mm":width,"catch_width_mm":CATCH_OUTER-CATCH_INNER,"single_rail_stall_nominal_stress_mpa":round(stall,3),"static_yield_ratio":round(PROJECT_MIN_YIELD_MPA/stall,3),"collision_sweep_executed":True,"continuous_clearance_executed":True,"selected":False,"physical_evidence_complete":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"p09-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__": raise SystemExit(main())
