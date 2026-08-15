#!/usr/bin/env python3
"""Localize R284 C07 curved-Jacobian failures from retained raw meshes.

This is a bounded diagnostic.  It reconstructs exactly the MeshTet2 mapping
used by the screen, identifies failed element/quadrature pairs, and measures
their physical points against exact imported OCC entities.  It performs no
remeshing, structural solve, convergence, H02 closure, or authority grant.
"""
from __future__ import annotations
import csv, hashlib, json, math, platform, shutil, sys
from pathlib import Path
import gmsh
import numpy as np
from skfem import MeshTet, MeshTet2
from skfem.quadrature import get_quadrature_tet

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1"
RELEASE_OUT=ROOT/"release/hr-v0/j2-c07-failure-localization-p0.1"
STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
IDENT="HR-V0-J2-C07-FAILURE-LOCALIZATION-P0.1"
WARNING="PRELIMINARY - CURVED-MESH FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
VARIANTS={
 "R284-V03-REFINED":SOURCE/"r284-v03-refined/raw-r284_v03_refined_fixed.npz",
 "R284-V06-FINE":SOURCE/"r284-v06-fine/raw-r284_v06_fine_fixed.npz",
 "R284-V08-ULTRAFINE":SOURCE/"r284-v08-ultrafine/raw-r284_v08_ultrafine_fixed.npz",
}
EDGE_ORDER=((0,1,4),(1,2,5),(0,2,6),(0,3,7),(2,3,8),(1,3,9))

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path, records:list[dict[str,object]])->None:
    if not records: raise RuntimeError(f"empty output: {path}")
    fields=[]
    for row in records:
        for key in row:
            if key not in fields: fields.append(key)
    with path.open("w",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)

def reconstruct(z:np.lib.npyio.NpzFile)->tuple[MeshTet,MeshTet2,dict[int,np.ndarray]]:
    tags=z["node_tags"]; xyz=z["node_xyz"]; tag_xyz={int(tag):xyz[i] for i,tag in enumerate(tags)}
    raw=z["tet10_connectivity"]; corners=sorted(set(map(int,raw[:,:4].ravel()))); corner_i={tag:i for i,tag in enumerate(corners)}
    linear=MeshTet(np.vstack([tag_xyz[tag] for tag in corners]).T,np.asarray([[corner_i[int(tag)] for tag in tet[:4]] for tet in raw],dtype=np.int64).T)
    curved=MeshTet2.from_mesh(linear); edge_map={}
    for tet in raw:
        for a,b,m in EDGE_ORDER: edge_map[tuple(sorted((int(tet[a]),int(tet[b]))))]=tag_xyz[int(tet[m])]
    doflocs=curved.doflocs.copy()
    for edge_index,(a,b) in enumerate(curved.edges.T):
        doflocs[:,int(curved.dofs.edge_dofs[0,edge_index])]=edge_map[tuple(sorted((corners[int(a)],corners[int(b)])))]
    return linear,MeshTet2(doflocs,curved.t),tag_xyz

def closest(dim:int,tags:list[int],point:np.ndarray,required:bool=True)->tuple[float,int,np.ndarray]:
    best=(float("inf"),-1,np.full(3,np.nan))
    for tag in tags:
        try:q,_=gmsh.model.getClosestPoint(dim,tag,point.tolist())
        except Exception:continue
        q=np.asarray(q,dtype=float).reshape((-1,3))[0]
        b=np.asarray(gmsh.model.getBoundingBox(dim,tag),dtype=float)
        # Gmsh/OCC may return a projection on the underlying untrimmed curve
        # or surface.  It receives no nearest-entity credit unless the returned
        # point is inside the exact entity's own bounding box.
        if np.any(q < b[:3]-1e-6) or np.any(q > b[3:]+1e-6):continue
        candidate=(float(np.linalg.norm(point-q)),tag,q)
        if candidate[0]<best[0]: best=candidate
    if best[1]<0 and required:raise RuntimeError(f"no projectable OCC entity for dimension {dim}")
    return best

def entity_detail(dim:int,tag:int)->dict[str,object]:
    return {"dimension":dim,"tag":tag,"type":gmsh.model.getType(dim,tag),"bbox_mm":[round(float(x),9) for x in gmsh.model.getBoundingBox(dim,tag)]}

def feature_zone(point:np.ndarray, group_dist:dict[str,float])->str:
    if point[0] < -34.0 and point[1] > 7.0:return "NEGATIVE_X_RAIL_TOP_TRANSITION"
    if point[0] > 34.0 and point[1] > 7.0:return "POSITIVE_X_CATCH_TOP_TRANSITION"
    nearest=min(group_dist,key=group_dist.get)
    if group_dist[nearest]<=0.35:return nearest.upper()
    return "BODY_OTHER"

def refine_feature_zone(zone:str, point:np.ndarray, face_detail:dict[str,object])->str:
    if zone=="BODY_OTHER" and face_detail["type"]=="Cylinder":
        if 13.0<=abs(float(point[0]))<=19.0 and 5.0<=abs(float(point[2]))<=11.0 and float(point[1])<=0.1:
            return "BACKSIDE_MOUNTING_BOSS_CYLINDER"
    return zone

def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    variants={row["screen_id"]:row for row in csv.DictReader((SOURCE/"variant-summary.csv").open(newline="",encoding="utf-8-sig"))}
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R284_LOCALIZE");gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize()
        # Preserve source-screen tag semantics, but independently obtain exact
        # entity groups from the same SHA-bound STEP in this fresh OCC model.
        sys.path.insert(0,str(ROOT/"tools"));import generate_hr_v0_j2_stop_refinement_execution_p01 as base
        _,groups=base.entity_register("C07")
        group_defs={"holes":(2,groups["holes"]),"pocket_floor":(2,groups["pocket_floor"]),"pocket_edge":(1,groups["pocket_edge"]),"metal_face":(2,groups["metal_face"])}
        all_edges=[tag for _,tag in gmsh.model.getEntities(1)];all_faces=[tag for _,tag in gmsh.model.getEntities(2)]
        rows=[];summaries=[]
        for screen,path in VARIANTS.items():
            z=np.load(path);linear,curved,tag_xyz=reconstruct(z);raw=z["tet10_connectivity"];element_tags=z["tet10_element_tags"]
            failures={};screen_points=0
            for order in (4,6,8):
                X,_=get_quadrature_tet(order);lm=linear.mapping();cm=curved.mapping();ld=np.asarray(lm.detDF(X));cd=np.asarray(cm.detDF(X));oriented=cd*np.where(ld>=0,1,-1)
                bad=np.argwhere(oriented<=0);screen_points+=oriented.size
                for element_index,qp_index in bad:
                    point=cm.F(X,tind=np.asarray([element_index]))[:,0,qp_index]
                    key=int(element_index);record=failures.setdefault(key,{"orders":set(),"pairs":0,"worst":(float("inf"),None,None,None)})
                    record["orders"].add(order);record["pairs"]+=1
                    frob=float(np.linalg.norm(cm.DF(X,tind=np.asarray([element_index]))[:,:,0,qp_index]))
                    normalized=float(oriented[element_index,qp_index]/max(frob**3,np.finfo(float).tiny))
                    if normalized<record["worst"][0]:record["worst"]=(normalized,order,int(qp_index),point)
            for element_index,record in sorted(failures.items()):
                nodes=raw[element_index];corner_xyz=np.vstack([tag_xyz[int(tag)] for tag in nodes[:4]])
                lengths=[float(np.linalg.norm(corner_xyz[a]-corner_xyz[b])) for a,b,_ in EDGE_ORDER]
                centroid=np.mean(corner_xyz,axis=0);worst_n,worst_order,worst_qp,point=record["worst"]
                group_nearest={name:closest(dim,tags,point,required=False) for name,(dim,tags) in group_defs.items()}
                edge=closest(1,all_edges,point);face=closest(2,all_faces,point);group_dist={name:value[0] for name,value in group_nearest.items()}
                source_sets={name:set(map(int,z[f"post_entity_nodes_{name}"])) for name in group_defs}
                face_detail=entity_detail(2,face[1]);zone=refine_feature_zone(feature_zone(point,group_dist),point,face_detail)
                rows.append({
                    "screen_id":screen,"element_index_zero_based":element_index,"element_tag":int(element_tags[element_index]),
                    "failed_quadrature_orders":";".join(map(str,sorted(record["orders"]))),"failed_order_point_pairs":record["pairs"],
                    "worst_order":worst_order,"worst_quadrature_index_zero_based":worst_qp,"worst_normalized_determinant":worst_n,
                    "worst_x_mm":point[0],"worst_y_mm":point[1],"worst_z_mm":point[2],
                    "corner_centroid_x_mm":centroid[0],"corner_centroid_y_mm":centroid[1],"corner_centroid_z_mm":centroid[2],
                    "corner_edge_min_mm":min(lengths),"corner_edge_mean_mm":sum(lengths)/6.0,"corner_edge_max_mm":max(lengths),
                    "nominal_global_h_mm":variants[screen]["global_h_mm"],"nominal_pocket_h_mm":variants[screen]["pocket_h_mm"],"nominal_hole_h_mm":variants[screen]["hole_h_mm"],
                    "nearest_source_feature_group":min(group_dist,key=group_dist.get),"nearest_source_group_distance_mm":min(group_dist.values()),
                    "coordinate_diagnostic_zone":zone,
                    "nearest_occ_edge_distance_mm":edge[0],"nearest_occ_edge_tag":edge[1],"nearest_occ_edge_detail_json":json.dumps(entity_detail(1,edge[1]),sort_keys=True,separators=(",",":")),
                    "nearest_occ_face_distance_mm":face[0],"nearest_occ_face_tag":face[1],"nearest_occ_face_detail_json":json.dumps(face_detail,sort_keys=True,separators=(",",":")),
                    "element_nodes_on_hole_group":sum(int(tag) in source_sets["holes"] for tag in nodes),
                    "element_nodes_on_pocket_edge_group":sum(int(tag) in source_sets["pocket_edge"] for tag in nodes),
                    "element_nodes_on_pocket_floor_group":sum(int(tag) in source_sets["pocket_floor"] for tag in nodes),
                    "element_nodes_on_metal_face_group":sum(int(tag) in source_sets["metal_face"] for tag in nodes),
                    "scope":"reconstructed retained raw NPZ; exact OCC nearest-entity localization; no remesh/solve/convergence credit","warning":WARNING,
                })
            summaries.append({"screen_id":screen,"raw_npz":path.relative_to(ROOT).as_posix(),"raw_npz_sha256":sha(path),"tet10_elements":len(element_tags),"quadrature_points_screened":screen_points,"unique_failed_elements":len(failures),"failed_order_point_pairs":sum(x["pairs"] for x in failures.values()),"result":"PASS - NO FAILURES" if not failures else "FAILURES LOCALIZED","h02_closed":False,"warning":WARNING})
        # Preserve a nonempty fail-closed table even though V06 has no failure rows.
        write_csv(OUT/"failed-element-localization.csv",rows)
        write_csv(OUT/"variant-localization-summary.csv",summaries)
        zones={}
        for row in rows:zones[row["coordinate_diagnostic_zone"]]=zones.get(row["coordinate_diagnostic_zone"],0)+1
        recommendation={
            "finding":"V03/V08 failures are localized by exact retained element tag and OCC proximity; V06 is the only passing sampled size level.",
            "failed_element_zone_counts":zones,
            "action":"Use the V06 size triplet (global 3.0 mm, pocket 0.50 mm, hole 0.75 mm) as the bounded starting mesh. First expand the SHA-bound hole refinement group beyond the six bore cylinders to the coaxial backside mounting-boss cylinders and their rim curves; V03 places 8 failed elements on those ungrouped boss cylinders and 2 on a grouped bore. Apply target <=0.75 mm with the existing 3.0 mm distance transition. Second add exact edge/face groups for both top rail transitions (the current C07 rail_root group is empty); apply target <=0.50 mm with a transition >=2.5 mm, or <=0.35 mm when retrying the V08 nominal level. Retain no high-order optimizer and rerun orders 4/6/8. Do not infer monotonic safety from global refinement: V08 created a new inversion at the unrefined negative-X rail transition.",
            "acceptance":"zero oriented determinant <=0 and zero normalized determinant <=1e-10 at every order 4/6/8, with the existing identity and linear-SICN gates also passing; retain raw NPZ plus this localization rerun.",
            "boundary":"The 0.50 mm local target is a diagnostic next attempt based on the passing V06 pocket scale, not an accepted production mesh prescription.",
            "h02_closed":False,"capacity_credit":False,"work_authority":False,"warning":WARNING,
        }
        (OUT/"actionable-meshing-correction.json").write_text(json.dumps(recommendation,indent=2)+"\n",encoding="utf-8")
        status={"identifier":IDENT,"round":"R284-LOCALIZATION","step_sha256":sha(STEP),"source_variants":[x for x in VARIANTS],"failed_elements_localized":len(rows),"passing_comparator":"R284-V06-FINE","remeshing_executed":False,"structural_solution_executed":False,"mesh_convergence_complete":False,"r278_h02_closed":False,"capacity_credit":False,"work_authority":False,"warning":WARNING}
        (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        source_evidence={
            "variant-summary.csv":SOURCE/"variant-summary.csv",
            "r284-v03-refined/analysis-status.json":SOURCE/"r284-v03-refined/analysis-status.json",
            "r284-v03-refined/file-manifest.csv":SOURCE/"r284-v03-refined/file-manifest.csv",
            "r284-v06-fine/analysis-status.json":SOURCE/"r284-v06-fine/analysis-status.json",
            "r284-v06-fine/file-manifest.csv":SOURCE/"r284-v06-fine/file-manifest.csv",
            "r284-v08-ultrafine/analysis-status.json":SOURCE/"r284-v08-ultrafine/analysis-status.json",
            "r284-v08-ultrafine/file-manifest.csv":SOURCE/"r284-v08-ultrafine/file-manifest.csv",
        }
        provenance={"generator_sha256":sha(Path(__file__).resolve()),"step_sha256":sha(STEP),"source_package":SOURCE.relative_to(ROOT).as_posix(),"source_evidence_sha256":{name:sha(path) for name,path in source_evidence.items()},"source_npz_path":{screen:path.relative_to(ROOT).as_posix() for screen,path in VARIANTS.items()},"source_npz_sha256":{screen:sha(path) for screen,path in VARIANTS.items()},"python":platform.python_version(),"numpy":np.__version__,"gmsh":gmsh.option.getString("General.BuildInfo"),"warning":WARNING}
        (OUT/"execution-provenance.json").write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
        files=[]
        for path in sorted(OUT.iterdir()):
            if path.is_file() and path.name!="file-manifest.csv":files.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",files)
        if RELEASE_OUT.exists():shutil.rmtree(RELEASE_OUT)
        RELEASE_OUT.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE_OUT)
        print(json.dumps(status,indent=2));return 0
    finally:gmsh.finalize()

if __name__=="__main__":raise SystemExit(main())
