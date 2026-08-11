#!/usr/bin/env python3
"""Validate R242 P1.21 conductor/fill evidence and configuration P0.6."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT/"electrical/routing/hr-v0-p121-conductor-fill-p0.1"
OUT=ROOT/"release/hr-v0/p121-conductor-fill-p0.1"
CFG_ENG=ROOT/"configuration/hr-v0-config-reconciliation-p0.6"
CFG_OUT=ROOT/"release/hr-v0/configuration-reconciliation-p0.6"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check_dir(directory,expected,fail):
    fail(not directory.is_dir() or {p.name for p in directory.iterdir() if p.is_file()}!=expected,f"membership: {directory}")
    m=rows(directory/"file-manifest.csv"); actual={p.name for p in directory.iterdir() if p.is_file() and p.name!="file-manifest.csv"}
    fail({r['path'] for r in m}!=actual,f"manifest membership: {directory}")
    for r in m:
        p=directory/r['path']; fail(not p.is_file() or p.stat().st_size!=int(r['bytes']) or digest(p)!=r['sha256'],f"manifest mismatch: {p}")

def main():
    errors=[]; fail=lambda condition,message:errors.append(message) if condition else None
    common={"README.md","source-register.csv","exact-conductor-candidate.csv","p121-conductor-schedule.csv","terminal-compatibility.csv","route-length-screen.csv","duct-occupancy-screen.csv","wd2-known-occupancy.csv","voltage-drop-screen.csv","thermal-screen.csv","color-identification-hold.csv","open-holds.csv","inspection-register.csv","conductor-fill-overlay.svg","package-status.json","file-manifest.csv"}
    check_dir(ENG,common,fail); check_dir(OUT,common|{"index.html"},fail)
    for name in common-{"file-manifest.csv"}:fail((ENG/name).read_bytes()!=(OUT/name).read_bytes(),f"engineering/release mismatch: {name}")
    status=json.loads((OUT/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-P121-CONDUCTOR-FILL-P0.1","round":"R242","exact_conductor_candidate":"Belden 3057 BL005","candidate_color":"blue","candidate_put_up_m":30.48,"logical_conductors":7,"planning_centerline_total_m":6.72325,"wd5_known_circular_area_mm2":29.08,"wd5_known_percent_of_published_usable_area":8.89,"wd2_max_enumerated_cross_section_area_mm2":32.84,"wd2_max_enumerated_percent_of_published_usable_area":2.66,"open_holds":12,"blank_inspections":10,"warning":WARNING}.items():fail(status.get(key)!=value,f"status: {key}")
    for key in ("color_convention_accepted","dcr_controlled","cut_lengths_released","total_duct_fill_complete","thermal_calculation_complete","protection_coordinated","physical_evidence_exists","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):fail(status.get(key)is not False,f"{key} must be false")
    exact=rows(OUT/"exact-conductor-candidate.csv")
    fail(len(exact)!=1 or exact[0]["exact_order_code"]!="3057 BL005" or exact[0]["procurement_released"]!="NO","exact held candidate")
    conductors=rows(OUT/"p121-conductor-schedule.csv")
    fail(len(conductors)!=7 or {r['allocation_id'] for r in conductors}!={f"C-{i:02d}" for i in range(1,8)},"seven conductor membership")
    fail(any(r['exact_order_code']!="Belden 3057 BL005 - HELD" or r['nominal_od_mm']!="2.3" or r['cut_length_mm']!="SELECTION REQUIRED" for r in conductors),"conductor fail-closed fields")
    fail(sum(float(r['planning_centerline_mm']) for r in conductors)!=6723.25,"centerline sum")
    fail(sum(r['traverses_WD2']=="YES" for r in conductors)!=5,"WD2 transition count")
    expected={"C-01":("XD24:02","SR1:A1","SAFETY_24V"),"C-02":("XD24:06","KWD1:A1","SAFETY_24V"),"C-03":("XD24:07","KWD1:11","SAFETY_24V"),"C-04":("XD24:09","KWD2:A1","SAFETY_24V"),"C-05":("XD24:10","KWD2:21","SAFETY_24V"),"C-06":("KWD1:14","KWD2:11","WD_SRA1_SUPPLY_INTERMEDIATE"),"C-07":("KWD2:14","SRA1:A1","SRA1_A1_WD_GATED")}
    for r in conductors:fail((r['from'],r['to'],r['net'])!=expected[r['allocation_id']],f"P1.21 mapping {r['allocation_id']}")
    term=rows(OUT/"terminal-compatibility.csv")
    fail(len(term)!=3 or any(r['3057_1p31mm2_fit']!="GAUGE FIT" or "unresolved" in r['3057_1p31mm2_fit'].lower() for r in term),"terminal gauge screens")
    fill={r['screen_id']:r for r in rows(OUT/"duct-occupancy-screen.csv")}
    fail(set(fill)!={"FILL-WD5","FILL-WD2-A","FILL-WD2-B","FILL-WD2-C"},"fill screen membership")
    area3057=math.pi*(2.3/2)**2; area3051=math.pi*(1.6/2)**2
    fail(abs(float(fill['FILL-WD5']['known_circular_envelope_mm2'])-7*area3057)>0.01,"WD5 area")
    fail(abs(float(fill['FILL-WD2-B']['known_circular_envelope_mm2'])-(5*area3057+6*area3051))>0.01,"WD2 max area")
    fail(any("NOT" not in r['result'] and "KNOWN" not in r['result'] for r in fill.values()),"fill must remain non-release")
    fail(len(rows(OUT/"wd2-known-occupancy.csv"))!=4,"WD2 occupancy rows")
    fail(any(r['numeric_result']!="NOT CALCULATED" for r in rows(OUT/"voltage-drop-screen.csv")),"voltage drop must remain uncalculated")
    fail(any(r['result'] not in {"OPEN","BLOCKING"} for r in rows(OUT/"thermal-screen.csv")),"thermal must remain open")
    color=rows(OUT/"color-identification-hold.csv")
    fail(len(color)!=3 or "CONFIGURATION CONFLICT OPEN" not in {r['disposition'] for r in color},"color conflict")
    fail(len(rows(OUT/"open-holds.csv"))!=12 or any(r['state']!="OPEN" for r in rows(OUT/"open-holds.csv")),"holds")
    fail(len(rows(OUT/"inspection-register.csv"))!=10 or any(r['result']!="NOT EXECUTED" or r['evidence_uri'] for r in rows(OUT/"inspection-register.csv")),"blank inspections")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","3057 BL005","8.90%","2.66%","Voltage drop remains open","XD24","XD0"):fail(token not in page,f"guide token: {token}")
    cfg_common={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    check_dir(CFG_ENG,cfg_common,fail); check_dir(CFG_OUT,cfg_common|{"index.html"},fail)
    cfg=json.loads((CFG_OUT/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.6","round":"R242","system_bom_groups":97,"current_records":25,"supersession_records":13,"bom_integration_records":17,"gate_records":11,"open_holds":32,"acceptance_rows":35}.items():fail(cfg.get(key)!=value,f"config: {key}")
    fail(cfg.get("current_core_electrical_identifier")!="Project Button Electrical V3-P1.15-CARRIER-CANDIDATE","P1.15 current")
    fail(cfg.get("unaccepted_panel_topology_candidate")!="V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE","P1.21 unaccepted")
    bom={r['item_id']:r for r in rows(ROOT/"bom/bom.csv")}; closure={r['item_id']:r for r in rows(ROOT/"bom/hr-v0-bom-closure.csv")}
    fail(len(bom)!=98 or len(closure)!=98 or set(bom)!=set(closure),"current 98-group BOM coverage")
    fail(bom.get("BOM-097",{}).get("manufacturer_part_number")!="3057 BL005","BOM-097 identity")
    fail(closure.get("BOM-097",{}).get("closure_class")!="exact_candidate_hold" or closure["BOM-097"]["allowed_action"]!="HOLD","BOM-097 hold")
    fail(closure.get("BOM-098",{}).get("closure_class")!="exact_candidate_hold" or closure["BOM-098"]["allowed_action"]!="HOLD","R243 BOM-098 hold")
    integration={r['item_id']:r for r in rows(CFG_OUT/"bom-integration-map.csv")}
    fail(len(integration)!=17 or integration.get("BOM-097",{}).get("procurement_released")!="NO","config BOM integration")
    sources=rows(CFG_OUT/"source-hash-register.csv"); fail(len(sources)!=25,"config source count")
    historical_live_sources={"bom/bom.csv","release/hr-v0/release-candidate.json"}
    for r in sources:
        source=ROOT/r['source_path']
        fail(not source.is_file(),f"config source missing: {r['source_path']}")
        if r['source_path'] not in historical_live_sources:
            fail(digest(source)!=r['sha256'],f"config source hash: {r['source_path']}")
    if errors:
        print("HR-V0 R242 P1.21 conductor/fill: FAIL"); [print("-",e) for e in errors]; return 1
    print("HR-V0 R242 P1.21 conductor/fill: PASS")
    print("3057 BL005 held; WD5 8.89%; WD2 enumerated max 2.66%; 12 holds; P1.21 unaccepted")
    print("No procurement, fabrication, assembly, connection, powered test, motion, safety credit or energization authority")
    return 0
if __name__=="__main__":raise SystemExit(main())
