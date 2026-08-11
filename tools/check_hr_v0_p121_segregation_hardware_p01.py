#!/usr/bin/env python3
"""Validate R241 segregation hardware and configuration P0.5."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT/"electrical/routing/hr-v0-p121-segregation-hardware-p0.1"
OUT=ROOT/"release/hr-v0/p121-segregation-hardware-p0.1"
CFG_ENG=ROOT/"configuration/hr-v0-config-reconciliation-p0.5"
CFG_OUT=ROOT/"release/hr-v0/configuration-reconciliation-p0.5"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check_dir(directory,expected,fail):
    fail(not directory.is_dir() or {p.name for p in directory.iterdir() if p.is_file()}!=expected,f"membership: {directory}")
    m=rows(directory/"file-manifest.csv")
    actual={p.name for p in directory.iterdir() if p.is_file() and p.name!="file-manifest.csv"}
    fail({r['path'] for r in m}!=actual,f"manifest membership: {directory}")
    for r in m:
        p=directory/r['path'];fail(not p.is_file() or p.stat().st_size!=int(r['bytes']) or digest(p)!=r['sha256'],f"manifest mismatch: {p}")

def main():
    errors=[]; fail=lambda condition,message:errors.append(message) if condition else None
    common={"README.md","catalog-candidate-register.csv","wd5-geometry-register.csv","stock-screen.csv","conductor-allocation-screen.csv","junction-control-register.csv","domain-occupancy-register.csv","open-holds.csv","inspection-register.csv","source-register.csv","segregation-overlay.svg","package-status.json","file-manifest.csv"}
    check_dir(ENG,common,fail);check_dir(OUT,common|{"index.html"},fail)
    for name in common-{"file-manifest.csv"}:fail((ENG/name).read_bytes()!=(OUT/name).read_bytes(),f"engineering/release mismatch: {name}")
    status=json.loads((OUT/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-P121-SEGREGATION-HW-P0.1","round":"R241","selected_planning_candidate":"Phoenix Contact 3240187","wd5_length_mm":369.8,"logical_conductors":7,"open_holds":9,"blank_inspections":8,"warning":WARNING}.items():fail(status.get(key)!=value,f"status: {key}")
    for key in ("numeric_safety_separation_released","fill_calculation_complete","junction_released","physical_evidence_exists","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):fail(status.get(key)is not False,f"{key} must be false")
    cat={r['item_number']:r for r in rows(OUT/"catalog-candidate-register.csv")}
    fail(set(cat)!={"3240187","3240189"},"catalog membership")
    fail((cat["3240187"]["width_mm"],cat["3240187"]["height_mm"],cat["3240187"]["stock_length_mm"],cat["3240187"]["usage_cross_section_mm2"])!=("25","25","2000","327"),"3240187 facts")
    g=rows(OUT/"wd5-geometry-register.csv")[0]
    fail(tuple(float(g[k]) for k in ("x_mm","y_mm","width_mm","height_mm"))!=(54.0,10.0,369.8,25.0),"WD5 geometry")
    fail(float(g["x_mm"])+float(g["width_mm"])>533.4 or float(g["y_mm"])+float(g["height_mm"])>685.8,"WD5 outside backplate")
    stock={r['stock_id']:r for r in rows(OUT/"stock-screen.csv")}
    fail(stock["DUCT-A"]["residual_before_kerf_mm"]!="20.8" or "FAIL" not in stock["DUCT-A"]["result"],"existing stock must fail")
    fail(stock["DUCT-B"]["residual_before_kerf_mm"]!="1630.2" or "PLANNING" not in stock["DUCT-B"]["result"],"new stock screen")
    cond=rows(OUT/"conductor-allocation-screen.csv")
    fail(len(cond)!=7 or any(r["outside_diameter_mm"]!="SELECTION REQUIRED" or not r["fill_disposition"].startswith("NOT CALCULATED") for r in cond),"conductor/fill fail-closed")
    fail(any(r["state"]!="SELECTION REQUIRED" for r in rows(OUT/"junction-control-register.csv")),"junction falsely released")
    fail(len(rows(OUT/"open-holds.csv"))!=9 or any(r["state"]!="OPEN" for r in rows(OUT/"open-holds.csv")),"holds")
    fail(len(rows(OUT/"inspection-register.csv"))!=8 or any(r["result"]!="NOT EXECUTED" or r["evidence"]!="BLANK" for r in rows(OUT/"inspection-register.csv")),"inspections")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","3240187","SELECTION REQUIRED","zero safety credit"):fail(token not in page,f"guide token: {token}")
    cfg_common={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    check_dir(CFG_ENG,cfg_common,fail);check_dir(CFG_OUT,cfg_common|{"index.html"},fail)
    cfg=json.loads((CFG_OUT/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.5","round":"R241","system_bom_groups":96,"current_records":24,"supersession_records":12,"bom_integration_records":16,"open_holds":29,"acceptance_rows":29}.items():fail(cfg.get(key)!=value,f"config: {key}")
    fail(cfg.get("current_core_electrical_identifier")!="Project Button Electrical V3-P1.15-CARRIER-CANDIDATE","P1.15 current identity")
    fail(cfg.get("unaccepted_panel_topology_candidate")!="V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE","P1.21 unaccepted identity")
    bom={r['item_id']:r for r in rows(ROOT/"bom/bom.csv")}; closure={r['item_id']:r for r in rows(ROOT/"bom/hr-v0-bom-closure.csv")}
    fail(len(bom)!=98 or len(closure)!=98 or set(bom)!=set(closure),"current 98-group BOM coverage")
    fail(bom.get("BOM-096",{}).get("manufacturer_part_number")!="CD 25X25 item 3240187","BOM-096 identity")
    fail(closure.get("BOM-096",{}).get("closure_class")!="exact_candidate_hold" or closure["BOM-096"]["allowed_action"]!="HOLD","BOM-096 hold")
    fail(closure.get("BOM-097",{}).get("closure_class")!="exact_candidate_hold" or closure["BOM-097"]["allowed_action"]!="HOLD","R242 BOM-097 hold")
    fail(closure.get("BOM-098",{}).get("closure_class")!="exact_candidate_hold" or closure["BOM-098"]["allowed_action"]!="HOLD","R243 BOM-098 hold")
    integration={r['item_id']:r for r in rows(CFG_OUT/"bom-integration-map.csv")}
    fail(len(integration)!=16 or "BOM-096" not in integration or integration["BOM-096"]["procurement_released"]!="NO","config BOM integration")
    cfg_sources=rows(CFG_OUT/"source-hash-register.csv")
    fail(len(cfg_sources)!=24,"config source count")
    historical_live_sources={"bom/bom.csv","release/hr-v0/release-candidate.json"}
    for source_row in cfg_sources:
        source=ROOT/source_row["source_path"]
        fail(not source.is_file(),f"config source missing: {source_row['source_path']}")
        if source_row["source_path"] not in historical_live_sources:
            fail(digest(source)!=source_row["sha256"],f"config source hash: {source_row['source_path']}")
    if errors:
        print("HR-V0 R241 segregation hardware: FAIL");[print("-",e) for e in errors];return 1
    print("HR-V0 R241 segregation hardware: PASS")
    print("Exact 3240187 planning candidate; 96 BOM groups; 9 route holds; P1.15 current; P1.21 unaccepted")
    print("No procurement, fabrication, assembly, connection, powered test, motion, safety credit or energization authority")
    return 0
if __name__=="__main__":raise SystemExit(main())
