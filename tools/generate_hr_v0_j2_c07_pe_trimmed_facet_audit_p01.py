#!/usr/bin/env python3
"""Corrected exact trimmed-face ownership audit for the R307 boundary."""
from __future__ import annotations
import csv,hashlib,json,shutil
from collections import Counter,defaultdict
from pathlib import Path
import gmsh,numpy as np
import generate_hr_v0_j2_c07_brep_facet_load_p01 as base
from hr_v0_mesh_raw_shards import load_shards
ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";R309=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";R310=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-surface-imprint-disposition-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-prereg-p0.1";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-trimmed-facet-audit-p0.1";IDENT="HR-V0-J2-C07-PE-TRIMMED-FACET-AUDIT-P0.1";WARNING="PRELIMINARY - CORRECTED EXACT TRIMMED-FACE OWNERSHIP AUDIT ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=1e-7
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    protocol_path=PREREG/"frozen-protocol.json";protocol=json.loads(protocol_path.read_text())
    if protocol["audit_executed"] or protocol["generator_sha256"]!=sha(Path(__file__).resolve()):raise RuntimeError("R311 protocol state")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);raw=load_shards(R307);tet=np.asarray(raw["tet10_connectivity"],dtype=np.int64);ntags=np.asarray(raw["node_tags"],dtype=np.int64);xyz=np.asarray(raw["node_xyz"],dtype=float);lookup={int(tag):i for i,tag in enumerate(ntags)};facets,elements,local=base.boundary_facets(tet);coords=np.asarray([[xyz[lookup[int(tag)]] for tag in facet] for facet in facets]);btags=np.asarray(sorted(set(int(v) for v in facets.ravel())),dtype=np.int64);bxyz=np.asarray([xyz[lookup[int(tag)]] for tag in btags]);membership={int(tag):set() for tag in btags};underlying_hits=trim_rejects=0
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R311_TRIMMED_FACE_AUDIT");gmsh.model.occ.importShapes(str(base.STEP));gmsh.model.occ.synchronize();faces=[tag for _d,tag in gmsh.model.getEntities(2)];face_info={}
        for face in faces:
            signature,detail=base.feature.face_signature(face);face_info[face]={"signature":signature,"type":detail["geometry_type"],"bbox":detail["bbox_mm"]};bbox=np.asarray(detail["bbox_mm"],dtype=float);mask=np.all(bxyz>=bbox[:3]-base.SURFACE_DEVIATION_LIMIT_MM,axis=1)&np.all(bxyz<=bbox[3:]+base.SURFACE_DEVIATION_LIMIT_MM,axis=1);indices=np.nonzero(mask)[0]
            if not indices.size:continue
            closest,_=gmsh.model.getClosestPoint(2,face,bxyz[indices].ravel().tolist());closest=np.asarray(closest,dtype=float).reshape((-1,3));distance=np.linalg.norm(closest-bxyz[indices],axis=1)
            for index,point,deviation in zip(indices,closest,distance):
                if float(deviation)>TOL:continue
                underlying_hits+=1
                if gmsh.model.isInside(2,face,point.tolist(),parametric=False)==1:membership[int(btags[index])].add(face)
                else:trim_rejects+=1
        mapped=[];unmapped=[];multiple=[];candidate_sets=[]
        for index,nodes in enumerate(facets):
            common=set(membership[int(nodes[0])])
            for node in nodes[1:]:common.intersection_update(membership[int(node)])
            if len(common)>1:
                interior=base.map_tri6(coords[index],np.asarray(((1/3,1/3),)))[0];trimmed=set()
                for face in common:
                    closest,_=gmsh.model.getClosestPoint(2,face,interior.tolist())
                    if gmsh.model.isInside(2,face,list(closest),parametric=False)==1:trimmed.add(face)
                common=trimmed
            candidate_sets.append(tuple(sorted(common)))
            if len(common)==1:mapped.append(index)
            elif len(common)==0:unmapped.append(index)
            else:multiple.append(index)
        fail_rows=[]
        for index in [*unmapped,*multiple]:
            per_node=[sorted(membership[int(tag)]) for tag in facets[index]];union=sorted({face for values in per_node for face in values});fail_rows.append({"facet_id":index+1,"source_tet10_element_tag":int(raw["tet10_element_tags"][elements[index]]),"source_local_face":int(local[index]),"classification":"UNMAPPED" if index in unmapped else "MULTIPLY_MAPPED","node_tags_json":json.dumps([int(v) for v in facets[index]],separators=(",",":")),"node_xyz_json":json.dumps(coords[index].tolist(),separators=(",",":")),"per_node_exact_trimmed_face_tags_json":json.dumps(per_node,separators=(",",":")),"union_exact_trimmed_face_tags_json":json.dumps(union,separators=(",",":")),"common_exact_trimmed_face_tags_json":json.dumps(list(candidate_sets[index]),separators=(",",":")),"warning":WARNING})
        write_csv(OUT/"failed-trimmed-facet-register.csv",fail_rows if fail_rows else [{"facet_id":"NONE","classification":"NONE","warning":WARNING}])
        cluster=Counter(tuple(json.loads(row["union_exact_trimmed_face_tags_json"])) for row in fail_rows);cluster_rows=[]
        for ordinal,(face_set,count) in enumerate(sorted(cluster.items(),key=lambda item:(-item[1],item[0])),1):cluster_rows.append({"cluster_id":f"R311-C{ordinal:03d}","union_exact_trimmed_face_tags_json":json.dumps(list(face_set),separators=(",",":")),"face_signatures_sha256_json":json.dumps([face_info[face]["signature"] for face in face_set],separators=(",",":")),"face_types_json":json.dumps([face_info[face]["type"] for face in face_set],separators=(",",":")),"failed_facets":count,"warning":WARNING})
        write_csv(OUT/"failure-cluster-summary.csv",cluster_rows if cluster_rows else [{"cluster_id":"NONE","failed_facets":0,"warning":WARNING}])
        correction={"supersedes_r308_mapping_result_as_complete_exact_trimmed_face_evidence":True,"supersedes_r309_zero_distance_as_trimmed_containment_evidence":True,"rejects_r310_seven_face_imprint_as_underconstrained":True,"reason":"underlying-surface distance is insufficient; every candidate node must also lie inside the exact trimmed OCC face","warning":WARNING};(OUT/"method-correction.json").write_text(json.dumps(correction,indent=2)+"\n")
        status={"identifier":IDENT,"round":"R311","date":"2026-08-13","candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r308_status_sha256":sha(R308/"analysis-status.json"),"r309_status_sha256":sha(R309/"analysis-status.json"),"r310_status_sha256":sha(R310/"analysis-status.json"),"exterior_facets":len(facets),"boundary_nodes":len(btags),"underlying_surface_hits_within_tolerance":underlying_hits,"underlying_hits_rejected_by_exact_trim":trim_rejects,"uniquely_mapped_facets":len(mapped),"unmapped_facets":len(unmapped),"multiply_mapped_facets":len(multiple),"failure_clusters":len(cluster),"corrected_exact_trimmed_face_map_complete":len(unmapped)==0 and len(multiple)==0,"audit_executed":True,"r308_exact_facet_claim_superseded":True,"r309_trimmed_cluster_inference_superseded":True,"r310_imprint_candidate_rejected":True,"mesh_or_tolerance_change":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"energization_authorized":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"preregistration_sha256":sha(protocol_path),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"step_sha256":sha(base.STEP),"underlying_surface_tolerance_mm":TOL,"trim_containment":"gmsh.model.isInside on closest physical point for every candidate node","warning":WARNING},indent=2)+"\n");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR311 corrects the earlier exact-face method by requiring both <=1e-7 mm underlying-surface distance and exact OCC trimmed-face containment for every quadratic-facet node. R308-R310 are superseded where they treated distance as sufficient containment evidence. No mesh or tolerance changed.\n",encoding="utf-8");write_csv(OUT/"open-holds.csv",[{"hold_id":"R311-H01","hold":"Disposition the corrected complete-boundary ownership result before any topology operation.","state":"OPEN","warning":WARNING},{"hold_id":"R311-H02","hold":"Any successor must preserve material, analysis zones and seam-free PE topology and then rerun the corrected trimmed-face audit.","state":"OPEN","warning":WARNING},{"hold_id":"R311-H03","hold":"R279-C02, structural execution, H02, capacity and every work authority remain open.","state":"OPEN","warning":WARNING}]);manifest=[]
        for path in sorted(OUT.iterdir()):
            if path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",manifest)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
