#!/usr/bin/env python3
"""Publish the fail-closed R285 C07 targeted-remesh disposition."""
from __future__ import annotations
import csv,hashlib,html,json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FEATURE=ROOT/"mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1"
REMESH=ROOT/"mechanical/analysis/hr-v0-j2-c07-targeted-remesh-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-targeted-remesh-disposition-p0.1"
REL=ROOT/"release/hr-v0/j2-targeted-remesh-disposition-p0.1"
CFG0=ROOT/"configuration/hr-v0-config-reconciliation-p0.48";CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.49";CFGREL=ROOT/"release/hr-v0/configuration-reconciliation-p0.49"
IDENT="HR-V0-J2-TARGETED-REMESH-DISPOSITION-P0.1";CFGIDENT="HR-V0-CONFIG-REC-P0.49"
WARNING="PRELIMINARY - TARGETED CURVED-MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p:Path)->list[dict[str,str]]:
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def write(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for k in r:
            if k not in fields:fields.append(k)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def manifest(d:Path)->None:
    data=[]
    for p in sorted(x for x in d.rglob("*") if x.is_file() and x.name!="file-manifest.csv"):data.append({"relative_path":p.relative_to(d).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write(d/"file-manifest.csv",data)
def mirror(a:Path,b:Path)->None:
    if b.exists():shutil.rmtree(b)
    shutil.copytree(a,b)
def table(data:list[dict[str,object]])->str:
    fields=list(data[0]);head="".join(f"<th>{html.escape(x.replace('_',' '))}</th>" for x in fields);body="".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(x,'')))}</td>" for x in fields)+"</tr>" for r in data);return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"

def main()->int:
    feature=json.loads((FEATURE/"analysis-status.json").read_text());remesh=json.loads((REMESH/"analysis-status.json").read_text())
    if feature["surface_entities"]!=12 or feature["boundary_curve_entities"]!=46 or not feature["feature_topology_gate"]:raise RuntimeError("feature freeze drift")
    if remesh["runs_executed"]!=3 or not remesh["all_runs_pass"] or not remesh["raw_arrays_exactly_repeatable"]:raise RuntimeError("remesh evidence drift")
    forbidden=("r278_h02_closed","capacity_credit","work_authority")
    if any(feature.get(k,False) or remesh.get(k,False) for k in forbidden):raise RuntimeError("upstream authority violation")
    for d in (OUT,REL,CFG,CFGREL):
        if d.exists():shutil.rmtree(d)
    OUT.mkdir(parents=True)
    findings=[
      {"finding_id":"R285-F01","subject":"exact feature preregistration","result":"PASS METHOD CONTROL","evidence":"12 cylindrical surfaces and 46 owner-boundary curves frozen with STEP/geometric/adjacency signatures","credit":"TARGETED-MESH INPUT IDENTITY ONLY"},
      {"finding_id":"R285-F02","subject":"targeted V06-based mesh","result":"PASS BOUNDED SAMPLED SCREEN","evidence":"three fresh runs; 22,078 vertices; 92,455 Tet10; exact repeatability; zero Q4/Q6/Q8 sampled determinant failures","credit":"CANDIDATE MESH METHOD ONLY"},
      {"finding_id":"R285-F03","subject":"linear mesh screens","result":"PASS BOUNDED SCREEN","evidence":"minimum linear SICN 0.17901949697693917; below-0.20 fraction 4.326429073603374e-05","credit":"GLOBAL LINEAR QUALITY ONLY"},
      {"finding_id":"R285-F04","subject":"exact B-Rep surface fidelity and facet map","result":"NOT EXECUTED","evidence":"corner membership is not independent full surface-deviation/facet proof","credit":"NONE"},
      {"finding_id":"R285-F05","subject":"full-domain curved positivity","result":"NOT PROVEN","evidence":"Q4/Q6/Q8 finite samples do not prove positivity over every curved element domain","credit":"NONE"},
      {"finding_id":"R285-F06","subject":"exact zones and histograms","result":"NOT EXECUTED","evidence":"no exact cell/facet clipping or every-zone fixed-bin SICN/Jacobian evidence","credit":"NONE"},
      {"finding_id":"R285-F07","subject":"load-boundary preservation","result":"NOT EXECUTED","evidence":"loaded area, resultant, centroid and moment not checked against exact B-Rep","credit":"NONE"},
      {"finding_id":"R285-F08","subject":"R279-C02/R278-H02","result":"OPEN","evidence":"no production structural quadrature, exact-zone outputs, multilevel convergence, GCI, singularity trends or independent acceptance","credit":"NONE"},
    ]
    for r in findings:r["warning"]=WARNING
    write(OUT/"finding-register.csv",findings)
    hold_text=["Independently verify target-feature signatures, topology and symmetry","Prove exact boundary-facet/OCC mapping and quantify B-Rep surface deviation","Prove full-domain curved-Jacobian positivity or provide an accepted conservative substitute","Execute exact cell/facet clipping and every monitored-zone fixed-bin quality histograms","Verify exact loaded boundary area, resultant, centroid, line of action and moment","Execute structural quadrature fields, exact-zone statistics, frozen probes and section resultants","Execute accepted C06/C07 L0-L3/L4 convergence, GCI and singularity trends with raw manifests","Obtain independent numerical-method acceptance; keep contact/joint/dynamic/material/physical/work gates separate"]
    holds=[{"hold_id":f"R285-H{i:02d}","hold":x,"state":"OPEN","execution":"NOT EXECUTED","effect":"R279-C02, R278-H02, capacity, selection, safety credit and all work authority remain open","warning":WARNING} for i,x in enumerate(hold_text,1)];write(OUT/"open-holds.csv",holds)
    acceptance=[
      {"acceptance_id":"R285-ACC-01","criterion":"exact stable symmetric target-feature groups","execution_state":"EXECUTED","result":"PASS PROJECT-OWNED FEATURE FREEZE","evidence_uri":"j2-c07-target-feature-identity-p0.1/","approver":""},
      {"acceptance_id":"R285-ACC-02","criterion":"three fresh targeted-remesh runs and raw repeatability","execution_state":"EXECUTED","result":"PASS BOUNDED METHOD SCREEN","evidence_uri":"j2-c07-targeted-remesh-p0.1/","approver":""},
      {"acceptance_id":"R285-ACC-03","criterion":"exact B-Rep/facet fidelity","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""},
      {"acceptance_id":"R285-ACC-04","criterion":"full-domain curved-Jacobian positivity","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""},
      {"acceptance_id":"R285-ACC-05","criterion":"exact-zone clipped quality and structural outputs","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""},
      {"acceptance_id":"R285-ACC-06","criterion":"exact load-boundary preservation","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""},
      {"acceptance_id":"R285-ACC-07","criterion":"full R279-C02 and accepted multilevel convergence","execution_state":"NOT EXECUTED","result":"OPEN; H02 OPEN","evidence_uri":"","approver":""},
      {"acceptance_id":"R285-ACC-08","criterion":"independent/qualified acceptance and separate physical gates","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""},
    ]
    for r in acceptance:r["warning"]=WARNING
    write(OUT/"acceptance-matrix.csv",acceptance)
    inputs=[]
    for p,role in ((FEATURE/"analysis-status.json","feature status"),(FEATURE/"factor-model-feature-preregistration.json","feature preregistration"),(FEATURE/"file-manifest.csv","feature manifest"),(REMESH/"analysis-status.json","targeted-remesh status"),(REMESH/"variant-summary.csv","three-run summary"),(REMESH/"repeatability-register.csv","repeatability"),(REMESH/"file-manifest.csv","targeted-remesh manifest"),(ROOT/"tools/publish_hr_v0_j2_targeted_remesh_disposition_p01.py","R285 publisher")):inputs.append({"source_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"role":role,"warning":WARNING})
    write(OUT/"exact-input-register.csv",inputs)
    status={"identifier":IDENT,"round":"R285","date":"2026-08-13","exact_target_feature_identity_complete":True,"targeted_remesh_three_run_repeatability_complete":True,"bounded_sampled_jacobian_method_candidate_found":True,"surface_deviation_from_brep_complete":False,"exact_facet_map_complete":False,"exact_zone_clipped_histograms_complete":False,"full_domain_curved_jacobian_positivity_proven":False,"load_boundary_preservation_complete":False,"r279_c02_complete":False,"structural_solution_executed":False,"mesh_convergence_complete":False,"independent_numerical_acceptance_complete":False,"r278_h02_closed":False,"capacity_established":False,"selected":False,"safety_credit":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n")
    page=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R285 targeted remesh</title><style>:root{{--sky:#dff3ff;--blue:#0a3f73;--deep:#041c38;--gold:#f6c33b;--paper:#f7fbff;--ink:#11263d;--line:#8db9d8;--bad:#8b1e2d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,56px)}}header{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}header>div,main{{max-width:1440px;margin:auto}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.08}}h2{{font-size:clamp(27px,3vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:17px;font-size:16px;font-weight:900}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin:28px 0}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:20px}}.card strong{{display:block;font-size:clamp(26px,3vw,40px);color:var(--blue)}}.stop{{border-color:var(--bad)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white;margin-bottom:30px}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--blue);color:white;position:sticky;top:0}}@media(max-width:620px){{header,main{{padding:18px 14px}}}}</style></head><body><header><div><p class='warning'>{html.escape(WARNING)}</p><p>R285 - {IDENT}</p><h1>The targeted mesh repeats. Engineering closure does not.</h1><p>Three fresh runs reproduce the same bounded Q4/Q6/Q8 screen. Exact B-Rep fidelity, facet/load preservation, full-domain positivity, exact zones and convergence remain open.</p></div></header><main><section class='cards'><div class='card'><strong>3 of 3</strong>fresh runs passed the bounded sampled screen</div><div class='card'><strong>12 + 46</strong>surfaces and owner-boundary curves frozen</div><div class='card stop'><strong>OPEN</strong>R279-C02 and R278-H02</div></section><h2>Evidence disposition</h2>{table(findings)}<h2>Acceptance state</h2>{table(acceptance)}<h2>Open work</h2>{table(holds)}</main></body></html>""";(OUT/"index.html").write_text(page,encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR285 freezes exact target features and demonstrates a three-run repeatable bounded sampled-Jacobian targeted mesh. Exact B-Rep/facet/load/full-domain/exact-zone/convergence evidence, R279-C02 and H02 remain open.\n",encoding="utf-8");manifest(OUT);mirror(OUT,REL);mirror(FEATURE,ROOT/"release/hr-v0/j2-c07-target-feature-identity-p0.1");mirror(REMESH,ROOT/"release/hr-v0/j2-c07-targeted-remesh-p0.1")
    shutil.copytree(CFG0,CFG);current=rows(CFG/"current-configuration-map.csv");add=[
      {"record_id":"CFG-73","role":"R285 exact target-feature identity","identifier":feature["identifier"],"source_path":"release/hr-v0/j2-c07-target-feature-identity-p0.1/analysis-status.json","configuration_state":"CURRENT TARGETED-MESH INPUT IDENTITY","release_boundary":"no mesh/structural/capacity/work authority","warning":WARNING},
      {"record_id":"CFG-74","role":"R285 targeted C07 remesh","identifier":remesh["identifier"],"source_path":"release/hr-v0/j2-c07-targeted-remesh-p0.1/analysis-status.json","configuration_state":"CURRENT BOUNDED REPEATABLE MESH CANDIDATE","release_boundary":"finite samples only; exact B-Rep/facet/load/full-domain/R279-C02/H02 open","warning":WARNING},
      {"record_id":"CFG-75","role":"R285 targeted-remesh disposition","identifier":IDENT,"source_path":"release/hr-v0/j2-targeted-remesh-disposition-p0.1/analysis-status.json","configuration_state":"CURRENT R285 DISPOSITION - H02 OPEN","release_boundary":"no structural/convergence/capacity/work authority","warning":WARNING}];current.extend(add);write(CFG/"current-configuration-map.csv",current)
    ch=rows(CFG/"open-holds.csv");
    for h in holds:ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {h['hold']}","state":"OPEN","closure_evidence":"controlled numerical/physical evidence and independent/qualified acceptance","warning":WARNING})
    write(CFG/"open-holds.csv",ch);ca=rows(CFG/"acceptance-matrix.csv")
    for a in acceptance:ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {a['criterion']}","execution_state":a["execution_state"],"result":a["result"],"evidence_uri":a["evidence_uri"],"approver":"","warning":WARNING})
    write(CFG/"acceptance-matrix.csv",ca);cs=json.loads((CFG/"package-status.json").read_text());cs.update({"identifier":CFGIDENT,"round":"R285","current_records":len(current),"open_holds":len(ch),"acceptance_rows":len(ca),"j2_targeted_remesh_disposition":IDENT,"bounded_sampled_jacobian_method_candidate_found":True,"surface_deviation_from_brep_complete":False,"exact_facet_map_complete":False,"exact_zone_clipped_histograms_complete":False,"full_domain_curved_jacobian_positivity_proven":False,"load_boundary_preservation_complete":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_established":False,"selected":False,"safety_credit":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False});(CFG/"package-status.json").write_text(json.dumps(cs,indent=2)+"\n")
    write(CFG/"source-hash-register.csv",[{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current]);(CFG/"README.md").write_text(f"# {CFGIDENT}\n\n> **{WARNING}**\n\nR285 indexes exact target-feature identities and a repeatable bounded targeted-remesh candidate. Exact B-Rep/facet/load/full-domain/exact-zone/R279-C02/H02 and every authority remain open.\n");shutil.copy2(OUT/"index.html",CFG/"index.html");manifest(CFG);mirror(CFG,CFGREL)
    (ROOT/"docs/hr-v0-j2-targeted-remesh-disposition-p0.1.md").write_text(f"# HR-V0 J2 targeted-remesh disposition P0.1\n\n> **{WARNING}**\n\nR285 freezes stable target-feature identities and reproduces one bounded targeted mesh in three fresh processes. This is not R279-C02, convergence, capacity or work authority. Exact B-Rep surface fidelity, facet and load preservation, full-domain positivity, exact-zone clipping and production structural outputs remain open.\n\n[Interactive R285 guide](../release/hr-v0/j2-targeted-remesh-disposition-p0.1/index.html)\n")
    (ROOT/"docs/reviews/2026-08-13-r285-independent-review-request.md").write_text(f"# R285 independent review request\n\n> **{WARNING}**\n\nIndependently verify stable full symmetric OCC feature identities; every raw three-run targeted mesh artifact; repeatability; SICN and Q4/Q6/Q8 reconstruction; and the explicit absence of exact B-Rep deviation, facet/load preservation, full-domain positivity, exact-zone clipping, R279-C02, H02, capacity and work authority.\n")
    (ROOT/"docs/reviews/2026-08-13-r285-validation-record.md").write_text(f"# R285 validation record - draft\n\n> **{WARNING}**\n\nProject-owned checks pass feature topology/signature controls, three fresh process runs, raw repeatability, finite sampled determinant screens, manifests and release parity. Independent and qualified acceptance remain open.\n")
    hand=ROOT/"docs/handoff-current.md";old=hand.read_text();prefix=f"R285 targeted C07 remesh: **`{IDENT}` is a repeatable bounded sampled-Jacobian candidate only. Exact B-Rep/facet/load/full-domain/exact-zone/R279-C02/H02/capacity and all physical work remain blocked.**\n\n";
    if not old.startswith(prefix):hand.write_text(prefix+old)
    ledger=ROOT/"docs/review-ledger.md";lt=ledger.read_text().replace("Two hundred eighty-four rounds are complete (R01-R284).","Two hundred eighty-five rounds are complete (R01-R285).")
    if "| R285 |" not in lt:lt=lt.rstrip()+"\n| R285 | 2026-08-13 | Exact target-feature freeze and repeatable targeted C07 remesh | Codex project-owned numerical-method evidence; independent review requested | R284 left targeted remeshing open after non-monotonic screens. | Stable symmetric features frozen; three fresh targeted runs repeat and pass bounded samples. Exact B-Rep/facet/load/full-domain/exact-zone/R279-C02/H02 and all authority remain open. | `docs/hr-v0-j2-targeted-remesh-disposition-p0.1.md`; `release/hr-v0/j2-targeted-remesh-disposition-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.49/` |\n"
    ledger.write_text(lt);readme=ROOT/"README.md";rt=readme.read_text();links="- [R285 J2 targeted-remesh disposition](docs/hr-v0-j2-targeted-remesh-disposition-p0.1.md)\n- [R285 independent review request](docs/reviews/2026-08-13-r285-independent-review-request.md)\n- [R285 validation draft](docs/reviews/2026-08-13-r285-validation-record.md)\n- [Interactive R285 targeted-remesh guide](release/hr-v0/j2-targeted-remesh-disposition-p0.1/index.html)\n- [Interactive configuration reconciliation P0.49](release/hr-v0/configuration-reconciliation-p0.49/index.html)\n";
    if links not in rt:rt=rt.replace("## Start here\n\n","## Start here\n\n"+links)
    rt=rt.replace("Two hundred eighty-four rounds are complete: R01-R284.","Two hundred eighty-five rounds are complete: R01-R285.");readme.write_text(rt)
    cm=ROOT/"docs/configuration-management.md";ct=cm.read_text().rstrip();line=f"R285 adds `{IDENT}` and `{CFGIDENT}` as fail-closed targeted-remesh evidence. Repeatable finite samples do not close exact B-Rep/facet/load/full-domain/exact-zone/R279-C02/H02 or any work authority."
    if line not in ct:cm.write_text(ct+"\n\n"+line+"\n")
    print(f"Published R285 {IDENT}; R279-C02/H02 and all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
