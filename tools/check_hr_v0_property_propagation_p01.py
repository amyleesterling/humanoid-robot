#!/usr/bin/env python3
"""Validate R249 property propagation, stale-analysis control, and P0.13 config."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/"mechanical/analysis/hr-v0-property-propagation-p0.1";REL=ROOT/"release/hr-v0/property-propagation-p0.1";CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.13";CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.13"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest(directory,fail):
    rs=rows(directory/"file-manifest.csv");actual={p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv"};fail({r["path"] for r in rs}!=actual,f"manifest membership {directory}")
    for r in rs:
        p=directory/r["path"];fail(not p.is_file() or p.stat().st_size!=int(r["bytes"]) or sha(p)!=r["sha256"],f"manifest hash {p}")
def main():
    errors=[];fail=lambda c,m:errors.append(m) if c else None
    csvs={"accepted-property-input-template.csv","consumer-input-register.csv","stale-input-register.csv","analysis-rebuild-order.csv","downstream-analysis-record-template.csv","source-register.csv","open-holds.csv","acceptance-matrix.csv"};common=csvs|{"README.md","package-status.json","file-manifest.csv"}
    fail(not SRC.is_dir() or {p.name for p in SRC.iterdir() if p.is_file()}!=common,"source membership");fail(not REL.is_dir() or {p.name for p in REL.iterdir() if p.is_file()}!=common|{"index.html"},"release membership");manifest(SRC,fail);manifest(REL,fail)
    for n in common-{"file-manifest.csv"}:fail((SRC/n).read_bytes()!=(REL/n).read_bytes(),f"source/release parity {n}")
    status=json.loads((REL/"package-status.json").read_text(encoding="utf-8"));expected={"identifier":"HR-V0-PROP-PROPAGATION-P0.1","round":"R249","state":"FAIL-CLOSED PROPAGATION CONTRACT","required_property_rows":6,"accepted_property_rows":0,"consumers":12,"stale_inputs":8,"rebuild_steps":10,"open_holds":12,"acceptance_rows":10,"compiler_blank_exit_code":78,"warning":WARNING}
    for k,v in expected.items():fail(status.get(k)!=v,f"status {k}")
    for k in ("downstream_rebuild_executed","b010_closed","b011_closed","b013_closed","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):fail(status.get(k) is not False,f"{k} false")
    inputs=rows(REL/"accepted-property-input-template.csv");expected_keys={("CFG-MP-01","J2"),("CFG-MP-02","J1"),("CFG-MP-03","J1"),("CFG-MP-03","J2"),("CFG-MP-04","J1"),("CFG-MP-04","J2")};fail(len(inputs)!=6 or {(r["configuration_id"],r["axis"]) for r in inputs}!=expected_keys,"six exact compiler inputs")
    numeric=["accepted_mass_kg","expanded_uncertainty_mass_kg","accepted_com_radius_m","expanded_uncertainty_com_radius_m","accepted_inertia_kg_m2","expanded_uncertainty_inertia_kg_m2"]
    fail(any(r["execution_state"]!="NOT EXECUTED" or r["acceptance"]!="OPEN" or any(r[f] for f in numeric) or r["configuration_hash"] or r["measurement_manifest_sha256"] or r["accepted_by"] or r["acceptance_record_uri"] for r in inputs),"blank fail-closed inputs")
    consumers=rows(REL/"consumer-input-register.csv");fail(len(consumers)!=12 or any(r["current_release_state"]!="INCOMPLETE HISTORICAL/PLANNING SCREEN - NOT A RELEASE INPUT" or r["rebuild_state"]!="NOT EXECUTED" for r in consumers),"twelve unrebuilt consumers")
    for r in consumers:
        p=ROOT/r["current_artifact"];fail(not p.exists(),f"consumer artifact missing {p}")
    stale=rows(REL/"stale-input-register.csv");fail(len(stale)!=8 or any(r["release_use"]!="PROHIBITED" for r in stale),"eight prohibited stale inputs")
    for r in stale:fail(not (ROOT/r["artifact"]).exists(),f"stale artifact missing {r['artifact']}")
    fail(len(rows(REL/"analysis-rebuild-order.csv"))!=10 or any(r["execution_state"]!="NOT EXECUTED" or r["acceptance"]!="OPEN" for r in rows(REL/"analysis-rebuild-order.csv")),"ten rebuild steps")
    fail(len(rows(REL/"downstream-analysis-record-template.csv"))!=12 or any(r["execution_state"]!="NOT EXECUTED" or r["acceptance"]!="OPEN" for r in rows(REL/"downstream-analysis-record-template.csv")),"twelve blank downstream records")
    sources=rows(REL/"source-register.csv");fail(len(sources)!=5,"five source records")
    for r in sources:
        p=ROOT/r["path"];fail(not p.is_file() or sha(p)!=r["sha256"],f"source hash {r['path']}")
    fail(len(rows(REL/"open-holds.csv"))!=12 or any(r["state"]!="OPEN" for r in rows(REL/"open-holds.csv")),"12 open holds");fail(len(rows(REL/"acceptance-matrix.csv"))!=10 or any(r["execution_state"]!="NOT EXECUTED" or r["result"]!="OPEN" for r in rows(REL/"acceptance-matrix.csv")),"10 open acceptances")
    for n in csvs:fail(any(r.get("warning")!=WARNING for r in rows(REL/n)),f"warning {n}")
    page=(REL/"index.html").read_text(encoding="utf-8");
    for token in (WARNING,"font:clamp(16px","font-size:14px","NO ACCEPTED PROPERTY BUNDLE","HISTORICAL SCREENS ARE NOT RELEASE INPUTS","consumer-input-register.csv"):fail(token not in page,f"web token {token}")
    spec=importlib.util.spec_from_file_location("compiler",ROOT/"tools/compile_hr_v0_accepted_properties_p01.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    try:mod.compile_rows(inputs,"0"*64);fail(True,"compiler accepted blank template")
    except ValueError:pass
    synth=[]
    for i,(c,a) in enumerate(sorted(expected_keys),1):synth.append({"configuration_id":c,"axis":a,"configuration_hash":hashlib.sha256(c.encode()).hexdigest(),"accepted_mass_kg":str(.4+i*.01),"expanded_uncertainty_mass_kg":"0.001","accepted_com_radius_m":str(.1+i*.001),"expanded_uncertainty_com_radius_m":"0.0005","accepted_inertia_kg_m2":str(.01+i*.001),"expanded_uncertainty_inertia_kg_m2":"0.0001","measurement_manifest_sha256":hashlib.sha256(f"e{i}".encode()).hexdigest(),"accepted_by":"synthetic checker only","acceptance_record_uri":"synthetic://not-evidence","execution_state":"EXECUTED","acceptance":"ACCEPTED"})
    try:bundle=mod.compile_rows(synth,"1"*64)
    except ValueError as exc:fail(True,f"synthetic compile {exc}");bundle={}
    fail(len(bundle.get("properties",[]))!=6 or bundle.get("motion_authorized") is not False or bundle.get("safety_credit") is not False,"synthetic canonical bundle")
    cfg_common={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"};fail({p.name for p in CFG.iterdir() if p.is_file()}!=cfg_common,"config membership");fail({p.name for p in CFG_REL.iterdir() if p.is_file()}!=cfg_common|{"index.html"},"config release membership");manifest(CFG,fail);manifest(CFG_REL,fail)
    cfg=json.loads((CFG_REL/"package-status.json").read_text(encoding="utf-8"));
    for k,v in {"identifier":"HR-V0-CONFIG-REC-P0.13","round":"R249","current_records":33,"supersession_records":20,"open_holds":55,"acceptance_rows":81,"property_propagation":"HR-V0-PROP-PROPAGATION-P0.1"}.items():fail(cfg.get(k)!=v,f"config {k}")
    current=rows(CFG_REL/"current-configuration-map.csv");fail(len(current)!=33 or current[-1]["identifier"]!="HR-V0-PROP-PROPAGATION-P0.1","33 current records");hashes=rows(CFG_REL/"source-hash-register.csv");fail(len(hashes)!=33,"33 hashes")
    for r in hashes:
        p=ROOT/r["source_path"];fail(not p.is_file() or sha(p)!=r["sha256"],f"config hash {r['source_path']}")
    if errors:
        print("HR-V0 R249 property propagation: FAIL");[print("-",e) for e in errors];return 1
    print("HR-V0 R249 property propagation: PASS");print("6 blank accepted-property rows; 12 consumers unrebuilt; 8 stale inputs prohibited; compiler fail-closed");print("Zero Sol blockers, motion credit, safety credit, or energization authority added");return 0
if __name__=="__main__":raise SystemExit(main())
