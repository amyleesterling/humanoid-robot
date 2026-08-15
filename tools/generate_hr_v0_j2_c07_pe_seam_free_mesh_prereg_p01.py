#!/usr/bin/env python3
"""Freeze the single R298 mesh of the validated R297 seam-free partition."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R296=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-disposition-p0.1/next-partition-boundary.json";R291=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-mesh-prereg-p0.1"
IDENT="HR-V0-J2-C07-PE-SEAM-FREE-MESH-PREREG-P0.1";WARNING="PRELIMINARY - SEAM-FREE PE MESH PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    pst=json.loads((R297/"analysis-status.json").read_text(encoding="utf-8"));boundary=json.loads(R296.read_text(encoding="utf-8"))
    if pst["mesh_generated"] or not pst["internal_tangent_pe_seams_removed"] or pst["authoritative_physical_geometry_changed"]:raise RuntimeError("R297 state drift")
    if boundary["next_partition_executed"]:raise RuntimeError("R296 historical boundary unexpectedly executed")
    faces=R291/"exact-face-target-register.csv"
    with faces.open(newline="",encoding="utf-8") as s:face_rows=list(csv.DictReader(s))
    if len(face_rows)!=6:raise RuntimeError("R291 face target drift")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    protocol={"identifier":IDENT,"round":"R298-PREREG","date":"2026-08-13","candidate_id":"R298-C07-PE-SEAM-FREE-V01","r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"r297_classification_brep_sha256":sha(R297/"c07-pe-eight-subzone-classification.brep"),"r297_status_sha256":sha(R297/"analysis-status.json"),"r296_boundary_sha256":sha(R296),"exact_face_target_register_sha256":sha(faces),"exact_face_target_count":6,"analysis_zone_count":21,"retained_pe_subzone_count":8,"mesh_size_fields":{"base":"global 3.0 mm; fused PE/PF/rims 0.25 mm; ligaments 0.40 mm","fused_pe_additional":{"size_min_mm":0.18,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":0.75},"symmetry_closed_exact_face":{"size_min_mm":0.35,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":2.0}},"linear_mesh_method":{"algorithm3d":4,"algorithm_name":"Frontal","optimizer_sequence":["Netgen"],"general_num_threads":1,"relocate3d":False,"high_order_optimizer":"NONE"},"acceptance_thresholds":{"global_min_sicn":0.10,"global_fraction_below_0p20_max":0.001,"each_monitored_zone_min_sicn":0.20,"fused_pe_min_sicn":0.20,"actual_gauss4_6_8_wrong_or_zero":0,"actual_gauss4_6_8_normalized_floor_fail":0},"conservative_subzone_rule":"all cells in exact C07-PE-FUSED volume must meet SICN >=0.20; therefore every cell intersecting any of the eight retained exact PE subset solids meets the same floor","thresholds_unchanged":True,"stop_rule":"one execution only; retain and disposition without tuning; structural solve permitted only after all R279-C02 constituent gates pass","mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"frozen-seam-free-mesh-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n",encoding="utf-8")
    write_csv(OUT/"exact-face-target-register.csv",[{**r,"warning":WARNING} for r in face_rows])
    status={"identifier":IDENT,"round":"R298-PREREG","candidate_id":protocol["candidate_id"],"single_candidate_frozen":True,"thresholds_unchanged":True,"mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"r297_status_sha256":sha(R297/"analysis-status.json"),"r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"r296_boundary_sha256":sha(R296),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR298 freezes one Frontal+Netgen mesh of the validated R297 seam-free analysis partition. The fused PE volume receives the retained 0.18 mm field; six exact curved faces retain 0.35 mm refinement. All thresholds and the one-run stop rule are frozen before meshing.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
