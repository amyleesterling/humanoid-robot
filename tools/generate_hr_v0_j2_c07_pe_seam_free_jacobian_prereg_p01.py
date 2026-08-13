#!/usr/bin/env python3
"""Freeze the R300 symmetry-closed bore-wall Jacobian successor."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
import gmsh
ROOT=Path(__file__).resolve().parents[1];R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R298=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1";R299=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-failure-localization-p0.1";BREP=R297/"c07-pe-seam-free-analysis-partition.brep"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-jacobian-prereg-p0.1";IDENT="HR-V0-J2-C07-PE-SEAM-FREE-JACOBIAN-PREREG-P0.1";WARNING="PRELIMINARY - SEAM-FREE JACOBIAN SUCCESSOR PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=2e-6
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def close(a:list[float],b:list[float])->bool:return all(abs(x-y)<=TOL for x,y in zip(a,b))
def record(tag:int)->dict[str,object]:
    r={"geometry_type":gmsh.model.getType(2,tag),"bbox_mm":[round(float(v),9) for v in gmsh.model.getBoundingBox(2,tag)],"area_mm2":round(float(gmsh.model.occ.getMass(2,tag)),9),"center_mm":[round(float(v),9) for v in gmsh.model.occ.getCenterOfMass(2,tag)]};r["signature_sha256"]=stable(r);return r
def mirror_x(b:list[float])->list[float]:return [-b[3],b[1],b[2],-b[0],b[4],b[5]]
def mirror_z(b:list[float])->list[float]:return [b[0],b[1],-b[5],b[3],b[4],-b[2]]
def main()->int:
    st298=json.loads((R298/"analysis-status.json").read_text(encoding="utf-8"));st299=json.loads((R299/"analysis-status.json").read_text(encoding="utf-8"))
    if not st298["global_sicn_gate"] or not st298["monitored_zone_minimum_gate"] or st298["actual_quadrature_signed_jacobian_gate"] or st299["remesh_executed"]:raise RuntimeError("R298/R299 boundary drift")
    with (R299/"curved-jacobian-failure-localization.csv").open(newline="",encoding="utf-8") as s:failures=list(csv.DictReader(s))
    observed=[]
    for r in failures:
        b=json.loads(r["nearest_exact_face_bbox_mm_json"])
        if not any(close(b,x) for x in observed):observed.append(b)
    if len(observed)!=1:raise RuntimeError("observed face count")
    b=observed[0];targets=[]
    for candidate in (b,mirror_x(b),mirror_z(b),mirror_x(mirror_z(b))):
        if not any(close(candidate,x) for x in targets):targets.append(candidate)
    if len(targets)!=4:raise RuntimeError("symmetry closure")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R300_PREREG");gmsh.model.occ.importShapes(str(BREP));gmsh.model.occ.synchronize();rows=[]
        for target in targets:
            matches=[]
            for d,t in gmsh.model.getEntities(2):
                if gmsh.model.getType(2,t)=="Cylinder" and close([float(v) for v in gmsh.model.getBoundingBox(2,t)],target):matches.append(t)
            if len(matches)!=1:raise RuntimeError(f"target resolved {len(matches)}")
            r=record(matches[0]);rows.append({"role":"H1-H4 BORE-WALL CURVED-JACOBIAN REFINEMENT","selection_basis":"R299 observed face plus X/Z mirror closure","occ_tag_diagnostic_only":matches[0],"geometric_signature_sha256":r["signature_sha256"],"geometry_type":r["geometry_type"],"bbox_mm_json":json.dumps(r["bbox_mm"],separators=(",",":")),"area_mm2":r["area_mm2"],"center_mm_json":json.dumps(r["center_mm"],separators=(",",":")),"size_min_mm":.25,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":1.5,"warning":WARNING})
    finally:gmsh.finalize()
    write_csv(OUT/"exact-bore-wall-target-register.csv",sorted(rows,key=lambda r:r["bbox_mm_json"]))
    protocol={"identifier":IDENT,"round":"R300-PREREG","date":"2026-08-13","candidate_id":"R300-C07-PE-SEAM-FREE-JACOBIAN-V01","r297_analysis_brep_sha256":sha(BREP),"r298_status_sha256":sha(R298/"analysis-status.json"),"r298_raw_sha256":sha(R298/"raw-conformal-zone-mesh.npz"),"r299_status_sha256":sha(R299/"analysis-status.json"),"target_register_sha256":sha(OUT/"exact-bore-wall-target-register.csv"),"observed_face_count":1,"symmetry_closed_face_count":4,"additional_face_field":{"size_min_mm":.25,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":1.5},"base_mesh":"R298 exact B-Rep, Frontal+Netgen, fused-PE and six prior face fields unchanged","acceptance_thresholds":{"global_min_sicn":.10,"global_fraction_below_0p20_max":.001,"each_monitored_zone_min_sicn":.20,"actual_gauss4_6_8_wrong_or_zero":0,"actual_gauss4_6_8_normalized_floor_fail":0},"thresholds_unchanged":True,"stop_rule":"one execution only; retain/disposition without tuning; structural work only after every R279-C02 gate passes","mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"frozen-jacobian-successor-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n",encoding="utf-8");status={"identifier":IDENT,"round":"R300-PREREG","candidate_id":protocol["candidate_id"],"exact_face_targets":4,"xz_symmetry_closed":True,"single_candidate_frozen":True,"thresholds_unchanged":True,"mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"r297_brep_sha256":sha(BREP),"r298_status_sha256":sha(R298/"analysis-status.json"),"r299_status_sha256":sha(R299/"analysis-status.json"),"warning":WARNING},indent=2)+"\n",encoding="utf-8");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR300 freezes one successor to R298 before meshing. The only addition is a 0.25 mm field around the one R299 bore-wall failure face, closed by X/Z symmetry to all four H1-H4 bore walls. Exact CAD, seam-free topology, existing fields, Frontal+Netgen method, and thresholds are unchanged.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
