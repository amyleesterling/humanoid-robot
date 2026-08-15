#!/usr/bin/env python3
"""Localize the preregistered R308 set of 77 unmapped R307 facets."""
from __future__ import annotations
import csv,hashlib,json,shutil
from collections import defaultdict
from pathlib import Path
import gmsh,numpy as np
import generate_hr_v0_j2_c07_brep_facet_load_p01 as base
from hr_v0_mesh_raw_shards import load_shards
ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-prereg-p0.1";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-localization-p0.1";IDENT="HR-V0-J2-C07-PE-CAD-CURVING-FACET-LOCALIZATION-P0.1";WARNING="PRELIMINARY - R308 UNMAPPED-FACET LOCALIZATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION";TOL=1e-7;SEARCH=0.05
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    protocol_path=PREREG/"frozen-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol["localization_executed"] or protocol["generator_sha256"]!=sha(Path(__file__).resolve()):raise RuntimeError("R309 protocol state")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);raw=load_shards(R307);tet=np.asarray(raw["tet10_connectivity"],dtype=np.int64);ntags=np.asarray(raw["node_tags"],dtype=np.int64);xyz=np.asarray(raw["node_xyz"],dtype=float);lookup={int(tag):i for i,tag in enumerate(ntags)}
    facets,elements,local=base.boundary_facets(tet);coords=np.asarray([[xyz[lookup[int(tag)]] for tag in facet] for facet in facets]);btags=np.asarray(sorted(set(int(value) for value in facets.ravel())),dtype=np.int64);bxyz=np.asarray([xyz[lookup[int(tag)]] for tag in btags]);membership={int(tag):set() for tag in btags}
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R309_C07_FACET_LOCALIZATION");gmsh.model.occ.importShapes(str(base.STEP));gmsh.model.occ.synchronize();faces=[tag for _d,tag in gmsh.model.getEntities(2)];face_info={}
        for face in faces:
            signature,detail=base.feature.face_signature(face);bbox=np.asarray(detail["bbox_mm"],dtype=float);face_info[face]={"signature":signature,"type":detail["geometry_type"],"bbox":detail["bbox_mm"]};mask=np.all(bxyz>=bbox[:3]-base.SURFACE_DEVIATION_LIMIT_MM,axis=1)&np.all(bxyz<=bbox[3:]+base.SURFACE_DEVIATION_LIMIT_MM,axis=1);indices=np.nonzero(mask)[0]
            if indices.size:
                closest,_=gmsh.model.getClosestPoint(2,face,bxyz[indices].ravel().tolist());dist=np.linalg.norm(np.asarray(closest).reshape((-1,3))-bxyz[indices],axis=1)
                for i,d in zip(indices,dist):
                    if float(d)<=TOL:membership[int(btags[i])].add(face)
        mapped=[];unmapped=[]
        for index,nodes in enumerate(facets):
            common=set(membership[int(nodes[0])])
            for node in nodes[1:]:common.intersection_update(membership[int(node)])
            if len(common)>1:
                interior=base.map_tri6(coords[index],np.asarray(((1/3,1/3),)))[0];trimmed=set()
                for face in common:
                    closest,_=gmsh.model.getClosestPoint(2,face,interior.tolist())
                    if gmsh.model.isInside(2,face,list(closest),parametric=False)==1:trimmed.add(face)
                common=trimmed
            if len(common)==1:mapped.append(index)
            elif len(common)==0:unmapped.append(index)
            else:raise RuntimeError(f"unexpected multiply mapped facet {index}: {common}")
        if len(unmapped)!=protocol["expected_unmapped_facets"] or len(mapped)!=protocol["expected_uniquely_mapped_facets"]:raise RuntimeError(f"R308 count did not reproduce mapped={len(mapped)} unmapped={len(unmapped)}")
        detail_rows=[];clusters=defaultdict(list)
        for index in unmapped:
            node_xyz=coords[index];facet_bbox=np.r_[node_xyz.min(axis=0),node_xyz.max(axis=0)];candidates=[]
            for face,info in face_info.items():
                bbox=np.asarray(info["bbox"],dtype=float)
                if np.any(facet_bbox[:3]>bbox[3:]+SEARCH) or np.any(facet_bbox[3:]<bbox[:3]-SEARCH):continue
                closest,_=gmsh.model.getClosestPoint(2,face,node_xyz.ravel().tolist());dist=np.linalg.norm(np.asarray(closest).reshape((-1,3))-node_xyz,axis=1);candidates.append((float(np.max(dist)),float(np.mean(dist)),face,dist))
            if not candidates:raise RuntimeError(f"no nearby face for unmapped facet {index}")
            maxd,meand,face,dist=min(candidates,key=lambda value:(value[0],value[1],value[2]));clusters[face].append((index,maxd,meand))
            detail_rows.append({"facet_id":index+1,"source_tet10_element_tag":int(raw["tet10_element_tags"][elements[index]]),"source_local_face":int(local[index]),"node_tags_json":json.dumps([int(v) for v in facets[index]],separators=(",",":")),"node_xyz_json":json.dumps(node_xyz.tolist(),separators=(",",":")),"nearest_occ_face_tag_diagnostic_only":face,"nearest_face_signature_sha256":face_info[face]["signature"],"nearest_face_type":face_info[face]["type"],"nearest_face_bbox_mm_json":json.dumps(face_info[face]["bbox"],separators=(",",":")),"six_node_deviation_mm_json":json.dumps(dist.tolist(),separators=(",",":")),"maximum_six_node_deviation_mm":maxd,"mean_six_node_deviation_mm":meand,"node_face_membership_tolerance_mm":TOL,"within_0p005_surface_screen":maxd<=base.SURFACE_DEVIATION_LIMIT_MM,"exact_membership_gate":"FAIL","warning":WARNING})
        cluster_rows=[]
        for face,values in sorted(clusters.items()):cluster_rows.append({"nearest_occ_face_tag_diagnostic_only":face,"nearest_face_signature_sha256":face_info[face]["signature"],"nearest_face_type":face_info[face]["type"],"nearest_face_bbox_mm_json":json.dumps(face_info[face]["bbox"],separators=(",",":")),"unmapped_facets":len(values),"maximum_six_node_deviation_mm":max(v[1] for v in values),"minimum_six_node_deviation_mm":min(v[1] for v in values),"mean_of_facet_mean_deviation_mm":float(np.mean([v[2] for v in values])),"warning":WARNING})
        write_csv(OUT/"unmapped-facet-localization.csv",detail_rows);write_csv(OUT/"nearest-face-cluster-summary.csv",cluster_rows)
        status={"identifier":IDENT,"round":"R309","date":"2026-08-13","candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r308_status_sha256":sha(R308/"analysis-status.json"),"exterior_facets":len(facets),"uniquely_mapped_facets":len(mapped),"unmapped_facets":len(unmapped),"nearest_face_clusters":len(clusters),"maximum_nearest_face_six_node_deviation_mm":max(float(row["maximum_six_node_deviation_mm"]) for row in detail_rows),"all_unmapped_within_0p005_surface_screen":all(bool(row["within_0p005_surface_screen"]) for row in detail_rows),"localization_executed":True,"mesh_or_tolerance_change":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"energization_authorized":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        (OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"r308_status_sha256":sha(R308/"analysis-status.json"),"step_sha256":sha(base.STEP),"membership_tolerance_mm":TOL,"search_envelope_mm":SEARCH,"warning":WARNING},indent=2)+"\n",encoding="utf-8")
        (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR309 reproduces the R308 77-facet failure without changing mesh or tolerance and assigns each unmapped facet its nearest exact OCC face with six-node deviations. This is localization only; it does not retroactively pass the exact-face map or authorize a replacement mesh.\n",encoding="utf-8")
        write_csv(OUT/"open-holds.csv",[{"hold_id":"R309-H01","hold":"Review the localized exact-face clusters and preregister one corrective method without relaxing the 1e-7 mm membership tolerance.","state":"OPEN","warning":WARNING},{"hold_id":"R309-H02","hold":"Repeat complete exact facet/B-Rep/area/load validation under the accepted successor.","state":"OPEN","warning":WARNING},{"hold_id":"R309-H03","hold":"R279-C02, structural execution, H02, capacity and all work authority remain open.","state":"OPEN","warning":WARNING}])
        manifest=[]
        for path in sorted(OUT.iterdir()):
            if path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",manifest)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
