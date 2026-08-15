#!/usr/bin/env python3
"""Execute the single preregistered R298 seam-free PE mesh."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,shutil
from pathlib import Path
import gmsh

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-prereg-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-mesh-p0.1"
IDENT="HR-V0-J2-C07-PE-SEAM-FREE-MESH-P0.1";ROUND="R298";WARNING="PRELIMINARY - PREREGISTERED SEAM-FREE PE MESH EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=2e-6
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def load_base():
    spec=importlib.util.spec_from_file_location("r289_base_for_r298",BASE_PATH)
    if spec is None or spec.loader is None:raise RuntimeError("cannot load R289 base")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def close(a:list[float],b:list[float])->bool:return all(abs(x-y)<=TOL for x,y in zip(a,b))
def main()->int:
    protocol_path=PREREG/"frozen-seam-free-mesh-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"));pstatus=json.loads((PREREG/"analysis-status.json").read_text(encoding="utf-8"))
    if pstatus["mesh_executed"] or protocol["candidate_id"]!="R298-C07-PE-SEAM-FREE-V01":raise RuntimeError("R298 prereg state")
    with (PREREG/"exact-face-target-register.csv").open(newline="",encoding="utf-8") as s:faces=list(csv.DictReader(s))
    if len(faces)!=6:raise RuntimeError("face target count")
    face_bboxes=[json.loads(r["bbox_mm_json"]) for r in faces]
    base=load_base();original_add=base.add_threshold;original_set=base.gmsh.option.setNumber;call_count=0;algorithm_calls=[];resolution=[]
    def add_threshold(surfaces:list[int],size_min:float,dist_max:float)->int:
        nonlocal call_count
        field=original_add(surfaces,size_min,dist_max);call_count+=1
        if call_count!=1:return field
        pe_extra=original_add(surfaces,.18,.75)
        resolved=[]
        for i,b in enumerate(face_bboxes,1):
            matches=[]
            for _d,t in gmsh.model.getEntities(2):
                if gmsh.model.getType(2,t)!="Cylinder":continue
                if close([float(v) for v in gmsh.model.getBoundingBox(2,t)],b):matches.append(t)
            if len(matches)!=1:raise RuntimeError(f"exact face {i} resolved {len(matches)}")
            resolved.append(matches[0]);resolution.append({"target_kind":"EXACT_CYLINDER_FACE","ordinal":i,"resolved_occ_tag_diagnostic_only":matches[0],"bbox_mm_json":json.dumps(b,separators=(",",":")),"size_min_mm":.35,"dist_max_mm":2.0,"gate":"PASS","warning":WARNING})
        if len(set(resolved))!=6:raise RuntimeError("face targets not unique")
        face_extra=original_add(sorted(resolved),.35,2.0)
        resolution.append({"target_kind":"EXACT_FUSED_PE_VOLUME","ordinal":"C07-PE-FUSED","resolved_occ_tag_diagnostic_only":"PHYSICAL_VOLUME_BOUNDARY","bbox_mm_json":"N/A","size_min_mm":.18,"dist_max_mm":.75,"gate":"PASS","warning":WARNING})
        minimum=gmsh.model.mesh.field.add("Min");gmsh.model.mesh.field.setNumbers(minimum,"FieldsList",[field,pe_extra,face_extra]);return minimum
    def set_number(name:str,value:float)->None:
        if name=="Mesh.Algorithm3D":
            if int(value)!=1:raise RuntimeError("inherited algorithm drift")
            value=4;algorithm_calls.append(4)
        original_set(name,value)
    base.R288=R297;base.BREP=R297/"c07-pe-seam-free-analysis-partition.brep";base.FRAGMENTS=R297/"analysis-fragment-register.csv";base.ZONES=R297/"analysis-zone-register.csv";base.OUT=OUT;base.RELEASE=RELEASE;base.IDENT=IDENT;base.ROUND=ROUND;base.WARNING=WARNING;base.add_threshold=add_threshold;base.gmsh.option.setNumber=set_number
    code=base.main()
    if call_count!=4 or algorithm_calls!=[4] or len(resolution)!=7:raise RuntimeError(f"execution drift calls={call_count} alg={algorithm_calls} resolution={len(resolution)}")
    status_path=OUT/"analysis-status.json";status=json.loads(status_path.read_text(encoding="utf-8"))
    with (OUT/"zone-quality-summary.csv").open(newline="",encoding="utf-8") as s:summaries=list(csv.DictReader(s))
    fused=[r for r in summaries if r["zone_id"]=="C07-PE-FUSED"]
    if len(fused)!=1:raise RuntimeError("fused PE summary")
    fused_pass=fused[0]["monitored_min_0p20_gate"]=="PASS"
    status.update({"identifier":IDENT,"round":ROUND,"candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"r297_classification_brep_sha256":sha(R297/"c07-pe-eight-subzone-classification.brep"),"analysis_zone_count":21,"retained_exact_pe_subzone_count":8,"fused_pe_minimum_sicn":float(fused[0]["minimum_sicn"]),"fused_pe_quality_gate":fused_pass,"retained_pe_subzone_quality_floor_proven":fused_pass,"algorithm3d":4,"algorithm_name":"Frontal","linear_optimizer_sequence":["Netgen"],"relocate3d":False,"high_order_optimizer":"NONE","thresholds_unchanged":True,"single_preregistered_execution_complete":True,"warning":WARNING})
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    prov_path=OUT/"execution-provenance.json";prov=json.loads(prov_path.read_text(encoding="utf-8"));prov.update({"identifier":IDENT,"generator_path":Path(__file__).resolve().relative_to(ROOT).as_posix(),"generator_sha256":sha(Path(__file__).resolve()),"transitive_r289_generator_sha256":sha(BASE_PATH),"preregistration_path":protocol_path.relative_to(ROOT).as_posix(),"preregistration_sha256":sha(protocol_path),"r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"r297_classification_brep_sha256":sha(R297/"c07-pe-eight-subzone-classification.brep"),"algorithm3d":4,"algorithm_name":"Frontal","linear_optimizer_sequence":["Netgen"],"relocate3d":False,"high_order_optimizer":"NONE","warning":WARNING});prov_path.write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    shutil.copy2(protocol_path,OUT/"frozen-seam-free-mesh-protocol.json");write_csv(OUT/"seam-free-field-resolution.csv",resolution)
    write_csv(OUT/"retained-pe-subzone-quality-inference.csv",[{"exact_subzone_id":r["zone_id"],"classification_brep_sha256":sha(R297/"c07-pe-eight-subzone-classification.brep"),"subset_of":"C07-PE-FUSED","fused_pe_minimum_sicn":status["fused_pe_minimum_sicn"],"conservative_inference_gate":"PASS" if fused_pass else "FAIL","rule":"every exact-subzone-intersecting cell is a fused-PE cell; fused-volume global minimum bounds every subset","warning":WARNING} for r in csv.DictReader((R297/"retained-pe-subzone-classification-register.csv").open(newline="",encoding="utf-8"))])
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR298 executes one preregistered Frontal+Netgen mesh of the R297 seam-free analysis partition. The authoritative physical geometry is unchanged. All cells in the exact fused PE volume are screened at SICN 0.20; because each retained straight/corner solid is an exact subset, the fused-volume minimum conservatively bounds all eight subzones without centroid classification.\n\nThis is mesh evidence only. Structural fields, convergence, H02, capacity, safety credit, and every work authority remain open even if R279-C02 passes.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return code
if __name__=="__main__":raise SystemExit(main())
