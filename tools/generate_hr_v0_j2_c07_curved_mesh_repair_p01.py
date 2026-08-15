#!/usr/bin/env python3
"""Bounded geometry-preserving C07 curved Tet10 mesh-repair screen.

Every variant imports the same SHA-bound STEP B-Rep and uses exact OCC entity
tags.  A variant passes only when the linear SICN gates and signed curved
Jacobian gates pass without moving geometry off the exact Gmsh Tet10 nodes.
No structural, convergence, capacity, or work-authority credit is provided.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,shutil,time
from dataclasses import dataclass
from pathlib import Path
import gmsh
import numpy as np
from scipy.spatial import cKDTree
from skfem import MeshTet,MeshTet2
from skfem.quadrature import get_quadrature_tet
import generate_hr_v0_j2_stop_refinement_execution_p01 as base

ROOT=Path(__file__).resolve().parents[1]
STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-curved-mesh-repair-p0.1"
IDENT="HR-V0-J2-C07-CURVED-MESH-REPAIR-P0.1"
WARNING="PRELIMINARY - CURVED MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
NORMALIZED_DETERMINANT_GATE=1e-10
LINEAR_DETERMINANT_ABS_FLOOR=1e-14
CORNER_BIJECTION_TOL_MM=1e-9

@dataclass(frozen=True)
class Variant:
    name:str;global_h:float;pocket_h:float;hole_h:float;algorithm:int;linear_opt:str;high_order_opt:str

VARIANTS={
 "V01_BASELINE_R282":Variant("V01_BASELINE_R282",6.0,1.0,1.4,1,"Netgen",""),
 "V02_BASELINE_HIGH_ORDER":Variant("V02_BASELINE_HIGH_ORDER",6.0,1.0,1.4,1,"Netgen","HighOrder"),
 "V03_REFINED_NETGEN":Variant("V03_REFINED_NETGEN",4.0,0.70,1.0,1,"Netgen",""),
 "V04_REFINED_HIGH_ORDER":Variant("V04_REFINED_HIGH_ORDER",4.0,0.70,1.0,1,"Netgen","HighOrder"),
 "V05_REFINED_ELASTIC":Variant("V05_REFINED_ELASTIC",4.0,0.70,1.0,1,"Netgen","HighOrderElastic"),
 "V06_FINE_NETGEN":Variant("V06_FINE_NETGEN",3.0,0.50,0.75,1,"Netgen",""),
 "V07_FINE_HIGH_ORDER":Variant("V07_FINE_HIGH_ORDER",3.0,0.50,0.75,1,"Netgen","HighOrder"),
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def read_rows(path:Path)->list[dict[str,str]]:
    if not path.exists():return []
    with path.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def write_csv(path:Path,records:list[dict[str,object]])->None:
    if not records:return
    fields=[]
    for r in records:
        for k in r:
            if k not in fields:fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)

def execute(v:Variant)->tuple[dict[str,object],list[dict[str,object]]]:
    t0=time.perf_counter();gmsh.initialize(["-nopopup"])
    try:
        gmsh.option.setNumber("General.Terminal",0);gmsh.option.setNumber("General.NumThreads",1)
        gmsh.option.setNumber("Mesh.MeshSizeMin",min(v.pocket_h,v.hole_h));gmsh.option.setNumber("Mesh.MeshSizeMax",v.global_h)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints",0);gmsh.option.setNumber("Mesh.MeshSizeFromCurvature",0);gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary",1);gmsh.option.setNumber("Mesh.Algorithm3D",v.algorithm)
        gmsh.model.add(f"R283_{v.name}");imported=gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize()
        if len(imported)!=1 or imported[0][0]!=3:raise RuntimeError(f"expected one STEP volume, got {imported}")
        entities,groups=base.entity_register("C07")
        fields=[base.add_threshold(groups["holes"],2,v.hole_h,v.global_h,3.0),base.add_threshold(groups["pocket_edge"],1,v.pocket_h,v.global_h,2.5),base.add_threshold(groups["pocket_floor"],2,v.pocket_h,v.global_h,1.5)]
        minimum=gmsh.model.mesh.field.add("Min");gmsh.model.mesh.field.setNumbers(minimum,"FieldsList",fields);gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.model.mesh.generate(3)
        if v.linear_opt:gmsh.model.mesh.optimize(v.linear_opt)
        tet4=gmsh.model.mesh.getElementType("tetrahedron",1);linear_tags,linear_nodes=gmsh.model.mesh.getElementsByType(tet4);linear_raw=np.asarray(linear_nodes,dtype=np.int64).reshape((-1,4))
        linear_node_tags,linear_coords,_=gmsh.model.mesh.getNodes();linear_points=np.asarray(linear_coords,dtype=float).reshape((-1,3));linear_xyz={int(tag):linear_points[i] for i,tag in enumerate(linear_node_tags)}
        pre_entity_nodes={}
        for group in ("holes","pocket_edge","pocket_floor","metal_face"):
            dimension=1 if group=="pocket_edge" else 2;tags=set()
            for entity in groups[group]:
                nt,_,_=gmsh.model.mesh.getNodes(dimension,entity,includeBoundary=True);tags.update(int(x) for x in nt)
            pre_entity_nodes[group]=tags
        sicn=np.asarray(gmsh.model.mesh.getElementQualities(linear_tags.tolist(),"minSICN"),dtype=float)
        linear_quality=bool(np.min(sicn)>=0.10 and np.mean(sicn<0.20)<=0.001)
        gmsh.model.mesh.setOrder(2)
        if v.high_order_opt:gmsh.model.mesh.optimize(v.high_order_opt)
        tet10=gmsh.model.mesh.getElementType("tetrahedron",2);element_tags,element_nodes=gmsh.model.mesh.getElementsByType(tet10)
        raw=np.asarray(element_nodes,dtype=np.int64).reshape((-1,10));node_tags,coords,_=gmsh.model.mesh.getNodes();xyz=np.asarray(coords).reshape((-1,3));tag_xyz={int(tag):xyz[i] for i,tag in enumerate(node_tags)}
        corners=sorted(set(int(x) for x in raw[:,:4].ravel()));corner_i={tag:i for i,tag in enumerate(corners)}
        p=np.vstack([tag_xyz[tag] for tag in corners]).T;t=np.asarray([[corner_i[int(tag)] for tag in tet[:4]] for tet in raw],dtype=np.int64).T
        old_corners=sorted(set(int(x) for x in linear_raw.ravel()));old_points=np.vstack([linear_xyz[tag] for tag in old_corners]);new_points=np.vstack([tag_xyz[tag] for tag in corners]);distances,new_indices=cKDTree(new_points).query(old_points,k=1,workers=1)
        unique_targets=len(set(int(x) for x in new_indices));bijection=bool(len(old_corners)==len(corners) and unique_targets==len(corners) and float(np.max(distances))<=CORNER_BIJECTION_TOL_MM)
        old_to_new={old_corners[i]:corners[int(new_indices[i])] for i in range(len(old_corners))};corner_immobility=float(np.max(distances));corner_missing_tags=len(corners)-unique_targets;corner_tag_preserved_fraction=unique_targets/len(corners)
        corner_rows=[{"variant":v.name,"old_linear_corner_tag":old,"new_tet10_corner_tag":old_to_new[old],"old_x_mm":float(linear_xyz[old][0]),"old_y_mm":float(linear_xyz[old][1]),"old_z_mm":float(linear_xyz[old][2]),"new_x_mm":float(tag_xyz[old_to_new[old]][0]),"new_y_mm":float(tag_xyz[old_to_new[old]][1]),"new_z_mm":float(tag_xyz[old_to_new[old]][2]),"distance_mm":float(distances[i]),"within_tolerance":bool(distances[i]<=CORNER_BIJECTION_TOL_MM),"warning":WARNING} for i,old in enumerate(old_corners)]
        write_csv(OUT/f"corner-bijection-{v.name.lower()}.csv",corner_rows)
        old_elements={int(tag):linear_raw[i] for i,tag in enumerate(linear_tags)};new_elements={int(tag):raw[i,:4] for i,tag in enumerate(element_tags)};element_identity=True;orientation_identity=True;element_rows=[]
        for element_tag,old_nodes in old_elements.items():
            new_nodes=new_elements.get(element_tag);mapped=np.asarray([old_to_new[int(x)] for x in old_nodes],dtype=np.int64)
            connectivity_ok=bool(new_nodes is not None and np.array_equal(mapped,new_nodes));element_identity=element_identity and connectivity_ok
            old_xyz=np.vstack([linear_xyz[int(x)] for x in old_nodes]);new_xyz=np.vstack([tag_xyz[int(x)] for x in new_nodes]) if new_nodes is not None else np.full((4,3),np.nan)
            old_det=float(np.linalg.det(np.stack((old_xyz[1]-old_xyz[0],old_xyz[2]-old_xyz[0],old_xyz[3]-old_xyz[0]),axis=1)));new_det=float(np.linalg.det(np.stack((new_xyz[1]-new_xyz[0],new_xyz[2]-new_xyz[0],new_xyz[3]-new_xyz[0]),axis=1))) if new_nodes is not None else float("nan")
            orientation_ok=bool(old_det*new_det>0);orientation_identity=orientation_identity and orientation_ok
            element_rows.append({"variant":v.name,"element_tag":element_tag,"corner_connectivity_preserved":connectivity_ok,"orientation_preserved":orientation_ok,"linear_corner_det":old_det,"tet10_corner_det":new_det,"warning":WARNING})
        write_csv(OUT/f"element-corner-identity-{v.name.lower()}.csv",element_rows)
        linear=MeshTet(p,t);curved=MeshTet2.from_mesh(linear)
        edge_blocks=np.asarray(gmsh.model.mesh.getElementEdgeNodes(tet10,primary=False),dtype=np.int64).reshape((-1,6,3));edge_map={};consistency=0.0
        for block in edge_blocks:
            for edge in block:
                key=tuple(sorted((int(edge[0]),int(edge[1]))));candidate=tag_xyz[int(edge[2])]
                if key in edge_map:consistency=max(consistency,float(np.linalg.norm(edge_map[key][1]-candidate)))
                else:edge_map[key]=(int(edge[2]),candidate)
        doflocs=curved.doflocs.copy();missing=0;mapping=[]
        for ei,(a,b) in enumerate(curved.edges.T):
            key=tuple(sorted((corners[int(a)],corners[int(b)])))
            if key not in edge_map:missing+=1;continue
            dof=int(curved.dofs.edge_dofs[0,ei]);midtag,loc=edge_map[key];shift=float(np.linalg.norm(loc-(doflocs[:,int(a)]+doflocs[:,int(b)])/2));doflocs[:,dof]=loc
            mapping.append({"variant":v.name,"edge_corner_tag_a":key[0],"edge_corner_tag_b":key[1],"gmsh_mid_node_tag":midtag,"scikit_geometry_dof":dof,"transferred_x_mm":float(loc[0]),"transferred_y_mm":float(loc[1]),"transferred_z_mm":float(loc[2]),"midpoint_shift_mm":shift,"warning":WARNING})
        curved=MeshTet2(doflocs,curved.t)
        qrows=[];all_pass=True;minimum_oriented=float("inf");minimum_normalized=float("inf");wrong_total=0;conditioning_fail_total=0;points_total=0
        for qorder in (4,6,8):
            X,_=get_quadrature_tet(qorder);lm=linear.mapping();cm=curved.mapping();ld=np.asarray(lm.detDF(X));cd=np.asarray(cm.detDF(X));expected=np.where(ld>=0.0,1.0,-1.0)
            linear_small=int(np.count_nonzero(np.abs(ld)<=LINEAR_DETERMINANT_ABS_FLOOR));oriented=cd*expected;wrong=int(np.count_nonzero(oriented<=0));minimum=float(np.min(oriented));minimum_oriented=min(minimum_oriented,minimum)
            cdf=np.asarray(cm.DF(X));frobenius=np.sqrt(np.sum(cdf*cdf,axis=(0,1)));normalized=oriented/np.maximum(frobenius**3,np.finfo(float).tiny);conditioning_fail=int(np.count_nonzero(normalized<=NORMALIZED_DETERMINANT_GATE));minimum_n=float(np.min(normalized));minimum_normalized=min(minimum_normalized,minimum_n)
            wrong_total+=wrong;conditioning_fail_total+=conditioning_fail;points_total+=cd.size;passed=linear_small==0 and wrong==0 and conditioning_fail==0;all_pass=all_pass and passed
            qrows.append({"variant":v.name,"quadrature_order":qorder,"quadrature_points":int(cd.size),"orientation_reference":"sign of corresponding linear element Jacobian at same quadrature point","linear_abs_det_below_floor":linear_small,"linear_abs_det_floor":LINEAR_DETERMINANT_ABS_FLOOR,"curved_wrong_or_zero":wrong,"curved_wrong_or_zero_fraction":float(wrong/cd.size),"minimum_oriented_curved_jacobian":minimum,"maximum_oriented_curved_jacobian":float(np.max(oriented)),"normalized_determinant_definition":"oriented det(J)/||J||_F^3","normalized_determinant_gate":NORMALIZED_DETERMINANT_GATE,"normalized_gate_scope":"pre-registered bounded nonzero/conditioning floor; not R279-C02 or capacity","minimum_normalized_determinant":minimum_n,"normalized_determinant_fail_count":conditioning_fail,"gate":"PASS" if passed else "FAIL","warning":WARNING})
        surface_sets={}
        entity_membership_rows=[];entity_membership_pass=True
        for group in ("holes","pocket_edge","pocket_floor","metal_face"):
            dimension=1 if group=="pocket_edge" else 2;tags=set()
            for entity in groups[group]:
                nt,_,_=gmsh.model.mesh.getNodes(dimension,entity,includeBoundary=True);tags.update(int(x) for x in nt)
            surface_sets[group]=np.asarray(sorted(tags),dtype=np.int64)
            old_group_corners=sorted(pre_entity_nodes[group].intersection(old_corners));mapped_group={old_to_new[tag] for tag in old_group_corners};membership_ok=mapped_group.issubset(tags);entity_membership_pass=entity_membership_pass and membership_ok
            entity_membership_rows.append({"variant":v.name,"entity_group":group,"old_corner_nodes":len(old_group_corners),"mapped_new_corner_nodes":len(mapped_group),"post_entity_nodes_total":len(tags),"mapped_corner_membership_preserved":membership_ok,"scope":"corner-node membership on exact OCC entities; not an independent surface-deviation proof","warning":WARNING})
        write_csv(OUT/f"occ-corner-membership-{v.name.lower()}.csv",entity_membership_rows)
        raw_path=OUT/f"raw-{v.name.lower()}.npz";np.savez_compressed(raw_path,linear_node_tags=np.asarray(linear_node_tags,dtype=np.int64),linear_node_xyz=linear_points,linear_element_tags=np.asarray(linear_tags,dtype=np.int64),linear_tet4_connectivity=linear_raw,node_tags=np.asarray(node_tags,dtype=np.int64),node_xyz=np.asarray(coords,dtype=float).reshape((-1,3)),tet10_element_tags=np.asarray(element_tags,dtype=np.int64),tet10_connectivity=raw,linear_sicn=sicn,**{f"pre_entity_nodes_{k}":np.asarray(sorted(val),dtype=np.int64) for k,val in pre_entity_nodes.items()},**{f"post_entity_nodes_{k}":val for k,val in surface_sets.items()})
        edge_path=OUT/f"edge-map-{v.name.lower()}.csv";write_csv(edge_path,mapping)
        identity_pass=bool(bijection and element_identity and orientation_identity and entity_membership_pass and missing==0 and consistency<=CORNER_BIJECTION_TOL_MM)
        result={"identifier":IDENT,"variant":v.name,"step_sha256":sha(STEP),"exact_entity_groups":json.dumps(groups,sort_keys=True),"global_h_mm":v.global_h,"pocket_h_mm":v.pocket_h,"hole_h_mm":v.hole_h,"algorithm3d":v.algorithm,"linear_optimizer":v.linear_opt or "NONE","high_order_optimizer":v.high_order_opt or "NONE","vertices":len(corners),"tet10_elements":len(element_tags),"global_edges":int(curved.edges.shape[1]),"mapped_edges":len(mapping),"missing_edges":missing,"adjacent_midnode_consistency_max_mm":consistency,"corner_bijection_tolerance_mm":CORNER_BIJECTION_TOL_MM,"corner_bijection_max_distance_mm":corner_immobility,"corner_bijection_unique_targets":unique_targets,"corner_bijection_gate":"PASS" if bijection else "FAIL","element_corner_connectivity_gate":"PASS" if element_identity else "FAIL","element_corner_orientation_gate":"PASS" if orientation_identity else "FAIL","occ_corner_membership_gate":"PASS" if entity_membership_pass else "FAIL","corner_identity_gate":"PASS" if identity_pass else "FAIL","minimum_linear_sicn":float(np.min(sicn)),"fraction_linear_sicn_below_0p20":float(np.mean(sicn<0.20)),"linear_sicn_gate":"PASS" if linear_quality else "FAIL","quadrature_orders":"4;6;8","curved_wrong_or_zero_across_screens":wrong_total,"normalized_determinant_fail_across_screens":conditioning_fail_total,"curved_quadrature_points_across_screens":points_total,"minimum_oriented_curved_jacobian_across_screens":minimum_oriented,"minimum_normalized_determinant_across_screens":minimum_normalized,"curved_jacobian_gate":"PASS" if all_pass else "FAIL","geometry_identity_evidence":"STEP SHA, unique spatial corner bijection, element connectivity/orientation, OCC corner membership, and transferred Tet10 edge nodes all pass" if identity_pass else "INCOMPLETE - one or more frozen identity gates failed","entity_node_sets_scope":"corner-node membership on exact OCC entities; not an independent B-Rep surface-deviation proof","surface_deviation_from_brep":"NOT INDEPENDENTLY EVALUATED","raw_npz":raw_path.relative_to(ROOT).as_posix(),"raw_npz_sha256":sha(raw_path),"edge_map":edge_path.relative_to(ROOT).as_posix(),"edge_map_sha256":sha(edge_path),"mesh_repair_pass":bool(linear_quality and all_pass and identity_pass),"seconds":time.perf_counter()-t0,"h02_closed":False,"capacity_credit":False,"work_authority":False,"warning":WARNING}
        return result,qrows
    finally:gmsh.finalize()

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--variant",choices=tuple(VARIANTS),required=True);p.add_argument("--reset",action="store_true");args=p.parse_args()
    if args.reset and OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True);results=read_rows(OUT/"variant-register.csv");qrows=read_rows(OUT/"jacobian-screen-register.csv");attempts=read_rows(OUT/"failed-attempt-register.csv")
    result,screen=execute(VARIANTS[args.variant]);results=[r for r in results if r["variant"]!=args.variant]+[result];qrows=[r for r in qrows if r["variant"]!=args.variant]+screen
    attempts=[r for r in attempts if r.get("variant")!=args.variant]
    if not result["mesh_repair_pass"]:attempts.append({"attempt_id":f"R283-{args.variant}","variant":args.variant,"result":"FAIL CURVED MESH REPAIR","linear_sicn_gate":result["linear_sicn_gate"],"curved_jacobian_gate":result["curved_jacobian_gate"],"wrong_or_zero":result["curved_wrong_or_zero_across_screens"],"minimum_oriented_jacobian":result["minimum_oriented_curved_jacobian_across_screens"],"credit":"NONE","warning":WARNING})
    write_csv(OUT/"variant-register.csv",results);write_csv(OUT/"jacobian-screen-register.csv",qrows);write_csv(OUT/"failed-attempt-register.csv",attempts)
    selected=[r for r in results if str(r["mesh_repair_pass"]).lower()=="true"]
    status={"identifier":IDENT,"round":"R283-BOUNDED","baseline_commit":"d36bb8d5979364c9fcf5a46101fcf79500c61f99","step_sha256":sha(STEP),"variants_executed":len(results),"passing_variants":[r["variant"] for r in selected],"geometry_preserving_curved_mesh_route_found":bool(selected),"multi_level_convergence_complete":False,"r278_h02_closed":False,"capacity_credit":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2));return 0 if result["mesh_repair_pass"] else 2
if __name__=="__main__":raise SystemExit(main())
