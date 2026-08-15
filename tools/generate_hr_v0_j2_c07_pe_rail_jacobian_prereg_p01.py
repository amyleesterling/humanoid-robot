#!/usr/bin/env python3
"""Freeze the R302 X/Z-closed rail-transition Jacobian successor."""
from __future__ import annotations
import csv,hashlib,html,json,shutil
from pathlib import Path
import gmsh
ROOT=Path(__file__).resolve().parents[1];R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R301=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-failure-localization-p0.1";BREP=R297/"c07-pe-seam-free-analysis-partition.brep"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-rail-jacobian-prereg-p0.1";IDENT="HR-V0-J2-C07-PE-RAIL-JACOBIAN-PREREG-P0.1";WARNING="PRELIMINARY - RAIL-TRANSITION JACOBIAN SUCCESSOR PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=2e-6
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def close(a:list[float],b:list[float])->bool:return all(abs(x-y)<=TOL for x,y in zip(a,b))
def mx(b:list[float])->list[float]:return [-b[3],b[1],b[2],-b[0],b[4],b[5]]
def record(tag:int)->dict[str,object]:
    r={"geometry_type":gmsh.model.getType(2,tag),"bbox_mm":[round(float(v),9) for v in gmsh.model.getBoundingBox(2,tag)],"area_mm2":round(float(gmsh.model.occ.getMass(2,tag)),9),"center_mm":[round(float(v),9) for v in gmsh.model.occ.getCenterOfMass(2,tag)]};r["signature_sha256"]=stable(r);return r
def table(data:list[dict[str,object]])->str:
    fields=list(data[0]);head="".join(f"<th>{html.escape(f.replace('_',' '))}</th>" for f in fields);body="".join("<tr>"+"".join(f"<td>{html.escape(str(r[f]))}</td>" for f in fields)+"</tr>" for r in data);return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
def main()->int:
    s300=json.loads((R300/"analysis-status.json").read_text(encoding="utf-8"));s301=json.loads((R301/"analysis-status.json").read_text(encoding="utf-8"))
    if not s300["global_sicn_gate"] or not s300["monitored_zone_minimum_gate"] or s300["actual_quadrature_signed_jacobian_gate"] or s301["remesh_executed"] or s301["nearest_exact_face_clusters"]!=1:raise RuntimeError("R300/R301 boundary drift")
    with (R301/"curved-jacobian-failure-localization.csv").open(newline="",encoding="utf-8") as s:failures=list(csv.DictReader(s))
    observed=[]
    for r in failures:
        b=json.loads(r["nearest_exact_face_bbox_mm_json"])
        if not any(close(b,x) for x in observed):observed.append(b)
    if len(observed)!=1:raise RuntimeError("observed face count")
    b=observed[0];targets=[]
    for candidate in (b,mx(b)):
        if not any(close(candidate,x) for x in targets):targets.append(candidate)
    if len(targets)!=2:raise RuntimeError("X-mirror closure count")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0);target_rows=[]
    try:
        gmsh.model.add("R302_PREREG");gmsh.model.occ.importShapes(str(BREP));gmsh.model.occ.synchronize()
        for target in targets:
            matches=[]
            for d,t in gmsh.model.getEntities(2):
                if gmsh.model.getType(2,t)=="Cylinder" and close([float(v) for v in gmsh.model.getBoundingBox(2,t)],target):matches.append(t)
            if len(matches)!=1:raise RuntimeError(f"rail target resolved {len(matches)}")
            r=record(matches[0]);target_rows.append({"role":"RAIL-TRANSITION CURVED-JACOBIAN REFINEMENT","selection_basis":"R301 observed face plus exact X-mirror closure; Z mirrors do not exist in the R297 topology","occ_tag_diagnostic_only":matches[0],"geometric_signature_sha256":r["signature_sha256"],"geometry_type":r["geometry_type"],"bbox_mm_json":json.dumps(r["bbox_mm"],separators=(",",":")),"area_mm2":r["area_mm2"],"center_mm_json":json.dumps(r["center_mm"],separators=(",",":")),"size_min_mm":.25,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":1.5,"warning":WARNING})
    finally:gmsh.finalize()
    target_rows=sorted(target_rows,key=lambda r:r["bbox_mm_json"]);write_csv(OUT/"exact-rail-transition-target-register.csv",target_rows)
    protocol={"identifier":IDENT,"round":"R302-PREREG","date":"2026-08-13","candidate_id":"R302-C07-PE-RAIL-JACOBIAN-V01","r297_analysis_brep_sha256":sha(BREP),"r300_pre_shard_status_sha256":json.loads((R300/"execution-provenance.json").read_text(encoding="utf-8"))["pre_raw_shard_migration_status_sha256"],"r300_current_status_sha256":sha(R300/"analysis-status.json"),"r301_status_sha256":sha(R301/"analysis-status.json"),"target_register_sha256":sha(OUT/"exact-rail-transition-target-register.csv"),"observed_face_count":1,"symmetry_closed_face_count":2,"symmetry_rule":"X mirror only; candidate Z mirrors were enumerated and do not exist in the exact R297 topology","additional_face_field":{"size_min_mm":.25,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":1.5},"base_mesh":"R300 seam-free partition, Frontal+Netgen, all prior fields unchanged","acceptance_thresholds":{"global_min_sicn":.10,"global_fraction_below_0p20_max":.001,"each_monitored_zone_min_sicn":.20,"actual_gauss4_6_8_wrong_or_zero":0,"actual_gauss4_6_8_normalized_floor_fail":0},"thresholds_unchanged":True,"stop_rule":"one execution only; retain/disposition without tuning; structural work only after every R279-C02 gate passes","mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"frozen-rail-jacobian-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n",encoding="utf-8");status={"identifier":IDENT,"round":"R302-PREREG","candidate_id":protocol["candidate_id"],"exact_face_targets":2,"x_symmetry_closed":True,"z_symmetry_not_present_in_exact_topology":True,"single_candidate_frozen":True,"thresholds_unchanged":True,"mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"r297_brep_sha256":sha(BREP),"r300_current_status_sha256":sha(R300/"analysis-status.json"),"r301_status_sha256":sha(R301/"analysis-status.json"),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    comparison=[{"round":"R293","result":"quality failed; Jacobian passed"},{"round":"R295","result":"Frontal quality failed; Jacobian passed"},{"round":"R298","result":"seam-free quality passed; six curved QPs failed"},{"round":"R300","result":"all linear cells >=0.20; three Q8 points failed"},{"round":"R302","result":"two exact X-mirrored rail-transition faces frozen; mesh unexecuted"}]
    guide=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R302 mesh progression</title><style>:root{{--navy:#082b55;--deep:#041a35;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#92c9e8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{padding:clamp(30px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:white}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05}}h2{{font-size:clamp(26px,3vw,40px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805800;padding:15px 18px;font-size:16px;font-weight:900}}.decision{{background:white;border:2px solid var(--line);border-left:10px solid #245aa6;border-radius:14px;padding:20px;margin:24px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R293 → R302</p><h1>The seam defect is gone. Three curved Q8 points remain.</h1><p>R302 freezes the next exact X-mirrored correction without executing it.</p></div></header><main><section class='decision'><h2>Linear quality now clears every gate</h2><p>R300 has a global minimum SICN of {s300['global_sicn_minimum']:.6f}, zero cells below 0.20, all monitored zones passing, and a fused PE minimum of {s300['fused_pe_minimum_sicn']:.6f}. R301 localizes the only remaining failure to one exact rail-transition cylinder. Only its X mirror exists in the exact topology; no Z-mirror face is invented.</p></section><h2>Progression</h2>{table(comparison)}<h2>Frozen exact targets</h2>{table(target_rows)}<p>No mesh, structural solve, H02 closure, capacity credit, fabrication authority, motion authority, or energization authority follows from this guide.</p></main></body></html>""";(OUT/"index.html").write_text(guide,encoding="utf-8");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR302 freezes two exact X-mirrored rail-transition cylinders at 0.25 mm after R301 localized three residual Q8 failures to one face. Candidate Z mirrors were explicitly enumerated and do not exist in the R297 topology. R300's passing linear quality evidence and all thresholds remain unchanged. The mesh is not executed by this package.\n\n[Interactive guide](index.html)\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
