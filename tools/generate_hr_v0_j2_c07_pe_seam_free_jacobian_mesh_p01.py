#!/usr/bin/env python3
"""Execute the single preregistered R300 bore-wall Jacobian successor."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,shutil
from pathlib import Path
import gmsh
ROOT=Path(__file__).resolve().parents[1];PRIOR=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py";BASE=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-prereg-p0.1";R298=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-jacobian-mesh-p0.1";IDENT="HR-V0-J2-C07-PE-SEAM-FREE-JACOBIAN-MESH-P0.1";ROUND="R300";WARNING="PRELIMINARY - PREREGISTERED SEAM-FREE JACOBIAN SUCCESSOR EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=2e-6
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def load_prior():
    spec=importlib.util.spec_from_file_location("r298_for_r300",PRIOR)
    if spec is None or spec.loader is None:raise RuntimeError("cannot load R298 generator")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def close(a:list[float],b:list[float])->bool:return all(abs(x-y)<=TOL for x,y in zip(a,b))
def main()->int:
    protocol_path=PREREG/"frozen-jacobian-successor-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"));pstatus=json.loads((PREREG/"analysis-status.json").read_text(encoding="utf-8"))
    if pstatus["mesh_executed"] or protocol["candidate_id"]!="R300-C07-PE-SEAM-FREE-JACOBIAN-V01":raise RuntimeError("R300 prereg state")
    with (PREREG/"exact-bore-wall-target-register.csv").open(newline="",encoding="utf-8") as s:targets=list(csv.DictReader(s))
    bboxes=[json.loads(r["bbox_mm_json"]) for r in targets]
    if len(bboxes)!=4:raise RuntimeError("R300 target count")
    prior=load_prior();original_load=prior.load_base;resolution=[];lower_calls=0
    def load_base_with_bore_walls():
        base=original_load();original_add=base.add_threshold
        def add_threshold(surfaces:list[int],size_min:float,dist_max:float)->int:
            nonlocal lower_calls
            field=original_add(surfaces,size_min,dist_max);lower_calls+=1
            if lower_calls!=1:return field
            resolved=[]
            for i,b in enumerate(bboxes,1):
                matches=[]
                for d,t in gmsh.model.getEntities(2):
                    if gmsh.model.getType(2,t)=="Cylinder" and close([float(v) for v in gmsh.model.getBoundingBox(2,t)],b):matches.append(t)
                if len(matches)!=1:raise RuntimeError(f"bore wall {i} resolved {len(matches)}")
                resolved.append(matches[0]);resolution.append({"ordinal":i,"resolved_occ_tag_diagnostic_only":matches[0],"bbox_mm_json":json.dumps(b,separators=(",",":")),"size_min_mm":.25,"dist_max_mm":1.5,"gate":"PASS","warning":WARNING})
            if len(set(resolved))!=4:raise RuntimeError("bore wall targets not unique")
            extra=original_add(sorted(resolved),.25,1.5);minimum=gmsh.model.mesh.field.add("Min");gmsh.model.mesh.field.setNumbers(minimum,"FieldsList",[field,extra]);return minimum
        base.add_threshold=add_threshold;return base
    prior.load_base=load_base_with_bore_walls;prior.OUT=OUT;prior.RELEASE=RELEASE;prior.IDENT=IDENT;prior.ROUND=ROUND;prior.WARNING=WARNING
    code=prior.main()
    if lower_calls!=6 or len(resolution)!=4:raise RuntimeError(f"R300 field execution drift calls={lower_calls} resolved={len(resolution)}")
    old=OUT/"frozen-seam-free-mesh-protocol.json"
    if old.exists():old.unlink()
    shutil.copy2(protocol_path,OUT/"frozen-jacobian-successor-protocol.json")
    st_path=OUT/"analysis-status.json";st=json.loads(st_path.read_text(encoding="utf-8"));st.update({"identifier":IDENT,"round":ROUND,"candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r298_baseline_status_sha256":sha(R298/"analysis-status.json"),"additional_bore_wall_face_targets":4,"additional_bore_wall_size_min_mm":.25,"additional_bore_wall_dist_max_mm":1.5,"thresholds_unchanged":True,"single_preregistered_execution_complete":True,"warning":WARNING});st_path.write_text(json.dumps(st,indent=2)+"\n",encoding="utf-8")
    prov_path=OUT/"execution-provenance.json";prov=json.loads(prov_path.read_text(encoding="utf-8"));prov.update({"identifier":IDENT,"generator_path":Path(__file__).resolve().relative_to(ROOT).as_posix(),"generator_sha256":sha(Path(__file__).resolve()),"transitive_r298_generator_sha256":sha(PRIOR),"transitive_r289_generator_sha256":sha(BASE),"preregistration_path":protocol_path.relative_to(ROOT).as_posix(),"preregistration_sha256":sha(protocol_path),"additional_bore_wall_field":protocol["additional_face_field"],"warning":WARNING});prov_path.write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    write_csv(OUT/"bore-wall-field-resolution.csv",resolution);(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR300 executes one preregistered successor to R298. The only change is a symmetry-closed 0.25 mm field on the four H1-H4 bore-wall faces localized by R299. The seam-free partition, Frontal+Netgen method, all existing fields, and every threshold remain unchanged.\n\nA mesh gate pass only unlocks separately preregistered structural-field and convergence work. It does not close H02, establish capacity, or grant work authority.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(st,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
