#!/usr/bin/env python3
"""Generate R249 accepted-property propagation and stale-analysis control package."""
from __future__ import annotations

import csv, hashlib, html, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IDENT="HR-V0-PROP-PROPAGATION-P0.1"; CFG_IDENT="HR-V0-CONFIG-REC-P0.13"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
SRC=ROOT/"mechanical/analysis/hr-v0-property-propagation-p0.1"; REL=ROOT/"release/hr-v0/property-propagation-p0.1"
CFG_OLD=ROOT/"configuration/hr-v0-config-reconciliation-p0.12"; CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.13"; CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.13"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as h:r=csv.DictReader(h);return list(r),list(r.fieldnames or [])
def write(path,fields,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows({f:r.get(f,"") for f in fields} for r in rows)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest(directory):
    rs=[]
    for p in sorted(x for x in directory.rglob("*") if x.is_file() and x.name!="file-manifest.csv"):rs.append({"path":p.relative_to(directory).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)})
    write(directory/"file-manifest.csv",["path","bytes","sha256"],rs)
def common(rows):return [dict(r,warning=WARNING) for r in rows]
def page(title,intro,directory,names):
    sections=[]
    for name in names:
        rs,fs=read(directory/name); head="".join(f"<th>{html.escape(f.replace('_',' '))}</th>" for f in fs); body="".join("<tr>"+"".join(f"<td>{html.escape(str(r[f]))}</td>" for f in fs)+"</tr>" for r in rs)
        sections.append(f"<section><h2>{html.escape(name[:-4].replace('-',' ').title())}</h2><p><a href='{name}'>Download {name}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>")
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>:root{{--ink:#082a4a;--blue:#075ea8;--sky:#dff3ff;--gold:#f3bd28;--paper:#f8fbfd;--line:#9bc6e4;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--ink),var(--blue));color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}.warning{{font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd;border:3px solid var(--gold);padding:14px;border-radius:12px}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.5em 0 .2em}}h2{{font-size:clamp(24px,2.6vw,36px);margin-top:1.7em}}.status{{font-size:18px;font-weight:800;color:var(--danger)}}a{{font-size:16px;font-weight:700;color:var(--blue)}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{position:sticky;top:0;background:var(--sky)}}code{{font-size:14px}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:34px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><h1>{html.escape(title)}</h1><p>{html.escape(intro)}</p></div></header><main><p class='status'>NO ACCEPTED PROPERTY BUNDLE · HISTORICAL SCREENS ARE NOT RELEASE INPUTS · DOWNSTREAM REBUILD NOT EXECUTED</p><p>The compiler exits 78 until all six required physical-property records are executed, accepted, uncertainty-bearing and hash-bound.</p>{''.join(sections)}</main></body></html>"""

def generate_package():
    for d in (SRC,REL):
        if d.exists():shutil.rmtree(d)
        d.mkdir(parents=True)
    axes=[("CFG-MP-01","J2"),("CFG-MP-02","J1"),("CFG-MP-03","J1"),("CFG-MP-03","J2"),("CFG-MP-04","J1"),("CFG-MP-04","J2")]
    datasets={}
    datasets["accepted-property-input-template.csv"]=(['configuration_id','axis','configuration_hash','accepted_mass_kg','expanded_uncertainty_mass_kg','accepted_com_radius_m','expanded_uncertainty_com_radius_m','accepted_inertia_kg_m2','expanded_uncertainty_inertia_kg_m2','measurement_manifest_sha256','accepted_by','acceptance_record_uri','execution_state','acceptance','warning'],common([{"configuration_id":c,"axis":a,"configuration_hash":"","accepted_mass_kg":"","expanded_uncertainty_mass_kg":"","accepted_com_radius_m":"","expanded_uncertainty_com_radius_m":"","accepted_inertia_kg_m2":"","expanded_uncertainty_inertia_kg_m2":"","measurement_manifest_sha256":"","accepted_by":"","acceptance_record_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN"} for c,a in axes]))
    consumers=[
        ("CON-01","J1 gravity/static torque","mechanical load","mass; J1 COM radius; uncertainties","acceleration; pose transform; load factor; safety factors","cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/joint-load-screen.csv"),
        ("CON-02","J2 gravity/static torque","mechanical load","mass; J2 COM radius; uncertainties","pose transform; payload; load factor; safety factors","cad/hr-v0/generated/arm-load-basis-p1.1-x430/gravity-envelope.csv"),
        ("CON-03","J1 acceleration torque","mechanical load","J1 inertia; uncertainty","released acceleration/jerk/duty and drivetrain reflection","test-fixtures/hr-v0/dynamic-characterization-p0.1/"),
        ("CON-04","J2 acceleration torque","mechanical load","J2 inertia; uncertainty","released acceleration/jerk/duty and drivetrain reflection","release/hr-v0/x430-duty-characterization-p0.1/"),
        ("CON-05","rotational stopping energy","stopping","J1/J2 inertia; uncertainties","measured velocity; drive persistence; braking/coast; compliance","controls/hr-v0-stopping-budget-p0.1.csv"),
        ("CON-06","hard-stop load/energy","mechanical stop","mass; COM; inertia; uncertainties","bumper force-stroke; tolerance; speed; drive persistence; impact factor","cad/hr-v0/generated/arm-load-basis-p1.1-x430/stop-load-sensitivity.csv"),
        ("CON-07","guard/catch impact","containment","mass; COM; inertia; uncertainties","detached-part set; direction; drive energy; material/retention proof","cad/hr-v0/guard-impact-basis-p0.1/impact-energy-cases.csv"),
        ("CON-08","power-loss collapse/receiver","containment","mass; COM; inertia; uncertainties","friction; backdrive; start pose; contact sequence; receiver proof","safety/hr-v0-power-loss-containment-p0.1/power-loss-energy-bound.csv"),
        ("CON-09","joint/fastener/plate structure","structure","mass; COM; inertia; uncertainties","joint stiffness; shock/fatigue spectrum; safety factors; material allowables","release/hr-v0/mechanical-shop-rfq-assembly-p0.1/joint-verification-matrix.csv"),
        ("CON-10","actuator continuous/cyclic duty","thermal/control","mass; COM; inertia; uncertainties","efficiency; current/torque curve; thermal network; duty trajectory","release/hr-v0/x430-duty-characterization-p0.1/duty-test-sequence.csv"),
        ("CON-11","firmware pose/rate/acceleration limits","control","accepted downstream load/stop/duty envelopes","HIL; calibration; quantization; watchdog/fault behavior","firmware/supervisor/actuator-config.json"),
        ("CON-12","qualified motion-test matrix","verification","all accepted downstream analyses","test fixtures; uncertainty; witness; work authorization","tests/forms/hr-v0-dynamic-characterization-template.csv"),
    ]
    datasets["consumer-input-register.csv"]=(['consumer_id','consumer','domain','accepted_property_inputs','additional_required_inputs','current_artifact','current_release_state','rebuild_state','warning'],common([{"consumer_id":a,"consumer":b,"domain":c,"accepted_property_inputs":d,"additional_required_inputs":e,"current_artifact":f,"current_release_state":"INCOMPLETE HISTORICAL/PLANNING SCREEN - NOT A RELEASE INPUT","rebuild_state":"NOT EXECUTED"} for a,b,c,d,e,f in consumers]))
    stale=[
        ("STALE-01","cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/joint-load-screen.csv","Uses planning load case and incomplete physical properties","REBUILD AFTER ACCEPTED BUNDLE"),
        ("STALE-02","cad/hr-v0/generated/arm-load-basis-p1.1-x430/gravity-envelope.csv","Explicitly excludes FR12/hardware/harness/gripper distributions","NONSELECTED P1.1; DO NOT PROMOTE"),
        ("STALE-03","cad/hr-v0/generated/arm-load-basis-p1.1-x430/stop-load-sensitivity.csv","Uses incomplete reference support inertia and sensitivity moments","REBUILD AFTER ACCEPTED BUNDLE"),
        ("STALE-04","cad/hr-v0/guard-impact-basis-p0.1/impact-energy-cases.csv","Omits reflected inertia and continued drive","REBUILD AFTER ACCEPTED BUNDLE AND DRIVE DATA"),
        ("STALE-05","safety/hr-v0-power-loss-containment-p0.1/power-loss-energy-bound.csv","Planning mass/height bound; as-built behavior absent","REBUILD AND PHYSICALLY VALIDATE"),
        ("STALE-06","controls/hr-v0-stopping-budget-p0.1.csv","Geometric/time screen; physical total stop absent","REBUILD AND EXECUTE SYNCHRONIZED TEST"),
        ("STALE-07","release/hr-v0/x430-duty-characterization-p0.1/","Nonselected actuator route; no continuous physical data","DO NOT APPLY TO CURRENT XM540 WITHOUT NEW ROUTE"),
        ("STALE-08","firmware/supervisor/actuator-config.json","Candidate limits precede accepted load/stop/duty envelopes","NO MOTION RELEASE CREDIT"),
    ]
    datasets["stale-input-register.csv"]=(['stale_id','artifact','reason','required_disposition','release_use','warning'],common([{"stale_id":a,"artifact":b,"reason":c,"required_disposition":d,"release_use":"PROHIBITED"} for a,b,c,d in stale]))
    order=[
        ("RB-01","Compile accepted physical-property bundle","R248 accepted results plus hashes/signatures","canonical accepted bundle"),
        ("RB-02","Reconcile coordinate frames and pose transforms","accepted as-built datums and calibration","axis-specific COM/radius envelope"),
        ("RB-03","Rebuild gravity/static torque envelopes","RB-01/RB-02 plus payload","J1/J2 gravity envelope with uncertainty"),
        ("RB-04","Rebuild acceleration/jerk torque","accepted acceleration/jerk/duty","dynamic torque envelope with uncertainty"),
        ("RB-05","Characterize continuous/cyclic actuator duty","received current/torque/thermal tests","accepted actuator operating envelope"),
        ("RB-06","Rebuild stopping energy/travel","accepted inertia, velocity and measured stop chain","statistical stopping envelope"),
        ("RB-07","Rebuild hard-stop/guard/receiver loads","RB-03/RB-04/RB-06 plus contact data","peak/contact/containment cases"),
        ("RB-08","Rebuild structure/joint/anchor proof","accepted loads/material/joint factors","signed calculation/proof package"),
        ("RB-09","Derive firmware motion limits","accepted envelopes and calibration","configuration-bound limits and HIL cases"),
        ("RB-10","Qualified integrated acceptance","all prior rows and physical results","signed release decision; separate work authority still required"),
    ]
    datasets["analysis-rebuild-order.csv"]=(['step_id','step','required_inputs','output','execution_state','acceptance','warning'],common([{"step_id":a,"step":b,"required_inputs":c,"output":d,"execution_state":"NOT EXECUTED","acceptance":"OPEN"} for a,b,c,d in order]))
    datasets["downstream-analysis-record-template.csv"]=(['consumer_id','input_bundle_sha256','analysis_source_sha256','configuration_hash','method_revision','result_uri','uncertainty_uri','independent_check_uri','execution_state','acceptance','approver','warning'],common([{"consumer_id":a,"input_bundle_sha256":"","analysis_source_sha256":"","configuration_hash":"","method_revision":"","result_uri":"","uncertainty_uri":"","independent_check_uri":"","execution_state":"NOT EXECUTED","acceptance":"OPEN","approver":""} for a,_,_,_,_,_ in consumers]))
    sources=[("SRC-01","R248 physical-properties contract","release/hr-v0/moving-properties-closure-p0.1/package-status.json","current blank physical evidence contract"),("SRC-02","current integrated arm identity","cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated/architecture-summary.json","current nominal mechanical candidate"),("SRC-03","current firmware actuator config","firmware/supervisor/actuator-config.json","candidate command limits; no motion credit"),("SRC-04","current stopping budget","controls/hr-v0-stopping-budget-p0.1.csv","historical screen; physical total stop absent"),("SRC-05","Sol R12 B-010/B-011/B-013","release/hr-v0/sol-r12-current-disposition-r231/blocker-disposition.csv","blocker basis; zero qualified closures")]
    datasets["source-register.csv"]=(['source_id','source','path','use','sha256','warning'],common([{"source_id":a,"source":b,"path":c,"use":d,"sha256":sha(ROOT/c)} for a,b,c,d in sources]))
    holds=["R248 physical measurements and qualified acceptance","Canonical six-row accepted-property bundle","As-built coordinate-frame/pose transform reconciliation","Released payload and retained-object configuration","Acceleration/jerk/duty/fault spectrum","Actuator current/torque/thermal and drivetrain reflection","Measured total stopping and drive-persistence envelope","Bumper/guard/receiver contact and material evidence","Structural/joint/anchor safety factors and proof","Regenerated analysis source plus independent calculation checks","Firmware limits/HIL bound to accepted analyses","Qualified integrated review and separate work authorization"]
    datasets["open-holds.csv"]=(['hold_id','hold','state','closure_evidence','release_effect','warning'],common([{"hold_id":f"R249-H{i:02d}","hold":v,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS DOWNSTREAM ANALYSIS ACCEPTANCE AND MOTION CREDIT"} for i,v in enumerate(holds,1)]))
    accepts=["Six exact physical-property rows compile with accepted evidence and uncertainty.","As-built coordinate frames and pose transforms are accepted.","J1/J2 gravity and dynamic torque envelopes are regenerated and independently checked.","Continuous/cyclic actuator operating envelope is physically accepted.","Stopping time, residual travel and energy are physically accepted.","Hard-stop, guard, receiver, joint, frame and anchor cases are accepted.","Every downstream record binds exact bundle, source, configuration and result hashes.","Firmware limits and HIL cases consume only accepted regenerated analyses.","Qualified mechanical, controls and functional-safety reviewers sign the integrated package.","A separate configuration-bound work authorization is issued for any later powered step."]
    datasets["acceptance-matrix.csv"]=(['acceptance_id','criterion','execution_state','result','evidence_uri','approver','warning'],common([{"acceptance_id":f"R249-ACC-{i:02d}","criterion":v,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,v in enumerate(accepts,1)]))
    for name,(fields,rs) in datasets.items():write(SRC/name,fields,rs)
    status={"identifier":IDENT,"round":"R249","date":"2026-08-11","state":"FAIL-CLOSED PROPAGATION CONTRACT","required_property_rows":6,"accepted_property_rows":0,"consumers":12,"stale_inputs":8,"rebuild_steps":10,"open_holds":12,"acceptance_rows":10,"compiler_blank_exit_code":78,"downstream_rebuild_executed":False,"b010_closed":False,"b011_closed":False,"b013_closed":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (SRC/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (SRC/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR249 prevents incomplete historical mass, torque, stop and impact screens from becoming release inputs. The six-row accepted-property compiler currently exits 78 because R248 is unexecuted. No downstream analysis is rebuilt or accepted.\n",encoding="utf-8",newline="\n")
    for p in SRC.iterdir():
        if p.is_file() and p.name!="file-manifest.csv":shutil.copy2(p,REL/p.name)
    (REL/"index.html").write_text(page("HR-V0 accepted-property propagation","A fail-closed bridge from physical mass/COM/inertia evidence to every downstream load, stop, structure and control analysis.",REL,list(datasets)),encoding="utf-8",newline="\n")
    manifest(SRC);manifest(REL)

def generate_config():
    for d in (CFG,CFG_REL):
        if d.exists():shutil.rmtree(d)
        shutil.copytree(CFG_OLD,d)
    current,fields=read(CFG/"current-configuration-map.csv");current.append({"record_id":"CFG-33","role":"accepted moving-property propagation and stale-analysis control","identifier":IDENT,"source_path":"release/hr-v0/property-propagation-p0.1/package-status.json","configuration_state":"CURRENT FAIL-CLOSED CONTRACT - NO ACCEPTED BUNDLE","release_boundary":"six required property rows blank; twelve consumers unrebuilt; historical screens prohibited from release use","warning":WARNING});write(CFG/"current-configuration-map.csv",fields,current)
    sup,fields=read(CFG/"supersession-map.csv");sup.append({"record_id":"SUP-20","prior_identifier":"HR-V0-CONFIG-REC-P0.12","current_or_required_successor":CFG_IDENT,"disposition":"SUPERSEDED BY R249 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING});write(CFG/"supersession-map.csv",fields,sup)
    holds,fields=read(CFG/"open-holds.csv")
    for i,v in enumerate(["Accepted six-row physical-property bundle","Coordinate-frame and pose-transform reconciliation","Regenerated load/stop/containment/structure analyses","Regenerated firmware limits and HIL","Qualified integrated acceptance and separate work authority"],51):holds.append({"hold_id":f"HOLD-{i}","hold":v,"state":"NOT EXECUTED","closure_evidence":"Configuration-bound accepted evidence and signed review","warning":WARNING})
    write(CFG/"open-holds.csv",fields,holds)
    acc,fields=read(CFG/"acceptance-matrix.csv")
    for i,v in enumerate(["R249 accepted-property compiler input accepted","R249 coordinate-frame handoff accepted","R249 gravity/dynamic torque rebuild accepted","R249 stopping/impact rebuild accepted","R249 structure/containment rebuild accepted","R249 firmware limit/HIL rebuild accepted","R249 hash-bound downstream records accepted","R249 qualified integrated release signed"],74):acc.append({"acceptance_id":f"ACC-{i:02d}","criterion":v,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write(CFG/"acceptance-matrix.csv",fields,acc)
    impacts,fields=read(CFG/"gate-impact.csv")
    for r in impacts:
        if r["gate_id"] in {"EG-005","EG-006"}:r["evidence_added"]+=f"; {IDENT} fail-closed property propagation/stale-screen control";r["remaining_evidence"]+="; accepted property bundle and regenerated load/stop/structure/control analyses with physical/qualified acceptance";r["gate_closed"]="NO"
    write(CFG/"gate-impact.csv",fields,impacts)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"));status.update({"identifier":CFG_IDENT,"round":"R249","current_records":33,"supersession_records":20,"open_holds":55,"acceptance_rows":81,"property_propagation":IDENT});(CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8",newline="\n")
    (CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR249 carries P0.12 forward and adds fail-closed accepted-property propagation. No accepted physical bundle or downstream rebuild exists. Fifty-five holds and eighty-one unexecuted acceptance rows remain.\n",encoding="utf-8",newline="\n")
    hashes=[]
    for r in current:
        p=ROOT/r["source_path"]
        if not p.is_file():raise SystemExit(f"missing config source: {p}")
        hashes.append({"source_path":r["source_path"],"sha256":sha(p),"role":r["role"],"warning":WARNING})
    write(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes);manifest(CFG)
    for p in CFG.iterdir():
        if p.is_file() and p.name!="file-manifest.csv":shutil.copy2(p,CFG_REL/p.name)
    (CFG_REL/"index.html").write_text(page("HR-V0 configuration reconciliation P0.13","Current identifiers and open evidence after the R249 property-propagation contract.",CFG_REL,["current-configuration-map.csv","supersession-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv"]),encoding="utf-8",newline="\n");manifest(CFG_REL)

def main():generate_package();generate_config();print(f"Generated {IDENT} and {CFG_IDENT}: 0 accepted properties, 12 consumers unrebuilt, no authority")
if __name__=="__main__":main()
