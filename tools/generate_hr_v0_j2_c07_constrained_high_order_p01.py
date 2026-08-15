#!/usr/bin/env python3
"""R284 constrained-high-order C07 curved-mesh method screen.

After Gmsh HighOrder optimization, pre-order linear corners are uniquely mapped
by position and restored exactly with setNode. Optimized midsides are retained.
This is bounded meshing-method evidence only, never R279-C02/H02/capacity.
"""
from __future__ import annotations
import csv,hashlib,json,shutil,time
from pathlib import Path
import gmsh,numpy as np
from scipy.spatial import cKDTree
from skfem import MeshTet,MeshTet2
from skfem.quadrature import get_quadrature_tet
import generate_hr_v0_j2_stop_refinement_execution_p01 as base
ROOT=Path(__file__).resolve().parents[1];STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-constrained-high-order-p0.1"
IDENT="HR-V0-J2-C07-CONSTRAINED-HIGH-ORDER-P0.1";WARNING="PRELIMINARY - CONSTRAINED HIGH-ORDER MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
BIJECTION_TOL=0.10;RESTORE_TOL=1e-12;NORM_GATE=1e-10;LINEAR_DET_FLOOR=1e-14
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p,rec):
    fields=[]
    for r in rec:
        for k in r:
            if k not in fields:fields.append(k)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rec)
def main():
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);start=time.perf_counter();gmsh.initialize(["-nopopup"])
    try:
        for k,v in (("General.Terminal",0),("General.NumThreads",1),("Mesh.MeshSizeMin",0.7),("Mesh.MeshSizeMax",4.0),("Mesh.MeshSizeFromPoints",0),("Mesh.MeshSizeFromCurvature",0),("Mesh.MeshSizeExtendFromBoundary",1),("Mesh.Algorithm3D",1)):gmsh.option.setNumber(k,v)
        gmsh.model.add("R284_C07_CONSTRAINED_HIGH_ORDER");imported=gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize()
        if len(imported)!=1 or imported[0][0]!=3:raise RuntimeError(f"expected one volume: {imported}")
        _entities,groups=base.entity_register("C07");fields=[base.add_threshold(groups["holes"],2,1.0,4.0,3.0),base.add_threshold(groups["pocket_edge"],1,0.7,4.0,2.5),base.add_threshold(groups["pocket_floor"],2,0.7,4.0,1.5)];minimum=gmsh.model.mesh.field.add("Min");gmsh.model.mesh.field.setNumbers(minimum,"FieldsList",fields);gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize("Netgen")
        tet4=gmsh.model.mesh.getElementType("tetrahedron",1);linear_etags,linear_enodes=gmsh.model.mesh.getElementsByType(tet4);linear_raw=np.asarray(linear_enodes,dtype=np.int64).reshape((-1,4));linear_ntags,linear_coords,_=gmsh.model.mesh.getNodes();linear_points=np.asarray(linear_coords).reshape((-1,3));linear_xyz={int(t):linear_points[i] for i,t in enumerate(linear_ntags)};old_corners=sorted(set(int(x) for x in linear_raw.ravel()));old_points=np.vstack([linear_xyz[t] for t in old_corners]);sicn=np.asarray(gmsh.model.mesh.getElementQualities(linear_etags.tolist(),"minSICN"))
        pre_membership={}
        for group in ("holes","pocket_edge","pocket_floor","metal_face"):
            dim=1 if group=="pocket_edge" else 2;tags=set()
            for entity in groups[group]:nt,_,_=gmsh.model.mesh.getNodes(dim,entity,includeBoundary=True);tags.update(int(x) for x in nt)
            pre_membership[group]=tags
        gmsh.model.mesh.setOrder(2);gmsh.model.mesh.optimize("HighOrder")
        tet10=gmsh.model.mesh.getElementType("tetrahedron",2);etags,enodes=gmsh.model.mesh.getElementsByType(tet10);raw=np.asarray(enodes,dtype=np.int64).reshape((-1,10));ntags,coords,params=gmsh.model.mesh.getNodes();points=np.asarray(coords).reshape((-1,3));xyz={int(t):points[i] for i,t in enumerate(ntags)};new_corners=sorted(set(int(x) for x in raw[:,:4].ravel()));new_points=np.vstack([xyz[t] for t in new_corners])
        dist,index=cKDTree(new_points).query(old_points,k=1,workers=1);unique=len(set(int(i) for i in index));pre_bijection=bool(len(old_corners)==len(new_corners)==unique and float(np.max(dist))<=BIJECTION_TOL);old_to_new={old_corners[i]:new_corners[int(index[i])] for i in range(len(old_corners))}
        if not pre_bijection:raise RuntimeError(f"pre-restore spatial bijection failed: count={len(old_corners)}/{len(new_corners)}/{unique}, max={np.max(dist)}")
        correspondence=[]
        for i,old in enumerate(old_corners):
            new=old_to_new[old];before=xyz[new].copy();gmsh.model.mesh.setNode(new,linear_xyz[old].tolist(),[]);correspondence.append({"old_tag":old,"new_tag":new,"pre_restore_distance_mm":float(dist[i]),"pre_x_mm":float(before[0]),"pre_y_mm":float(before[1]),"pre_z_mm":float(before[2]),"restored_x_mm":float(linear_xyz[old][0]),"restored_y_mm":float(linear_xyz[old][1]),"restored_z_mm":float(linear_xyz[old][2]),"warning":WARNING})
        ntags,coords,_=gmsh.model.mesh.getNodes();points=np.asarray(coords).reshape((-1,3));xyz={int(t):points[i] for i,t in enumerate(ntags)};restore_max=max(float(np.linalg.norm(xyz[old_to_new[o]]-linear_xyz[o])) for o in old_corners);restore_gate=restore_max<=RESTORE_TOL
        old_elements={int(tag):linear_raw[i] for i,tag in enumerate(linear_etags)};new_elements={int(tag):raw[i,:4] for i,tag in enumerate(etags)};connectivity=True;orientation=True;element_rows=[]
        for tag,oldnodes in old_elements.items():
            mapped=np.asarray([old_to_new[int(x)] for x in oldnodes]);newnodes=new_elements.get(tag);c=bool(newnodes is not None and np.array_equal(mapped,newnodes));connectivity&=c;a=np.vstack([linear_xyz[int(x)] for x in oldnodes]);b=np.vstack([xyz[int(x)] for x in newnodes]);da=float(np.linalg.det(np.stack((a[1]-a[0],a[2]-a[0],a[3]-a[0]),axis=1)));db=float(np.linalg.det(np.stack((b[1]-b[0],b[2]-b[0],b[3]-b[0]),axis=1)));o=da*db>0;orientation&=o;element_rows.append({"element_tag":tag,"connectivity_preserved":c,"orientation_preserved":o,"linear_corner_det":da,"restored_corner_det":db,"warning":WARNING})
        post_membership={};membership=True;membership_rows=[]
        for group in pre_membership:
            dim=1 if group=="pocket_edge" else 2;tags=set()
            for entity in groups[group]:nodes,_,_=gmsh.model.mesh.getNodes(dim,entity,includeBoundary=True);tags.update(int(x) for x in nodes)
            post_membership[group]=tags;oldset=pre_membership[group].intersection(old_corners);mapped={old_to_new[t] for t in oldset};ok=mapped.issubset(tags);membership&=ok;membership_rows.append({"group":group,"old_corner_nodes":len(oldset),"mapped_corner_nodes":len(mapped),"post_nodes":len(tags),"membership_preserved":ok,"warning":WARNING})
        corners=new_corners;corner_i={t:i for i,t in enumerate(corners)};p=np.vstack([xyz[t] for t in corners]).T;t=np.asarray([[corner_i[int(x)] for x in tet[:4]] for tet in raw],dtype=np.int64).T;linear=MeshTet(p,t);curved=MeshTet2.from_mesh(linear);edgeblocks=np.asarray(gmsh.model.mesh.getElementEdgeNodes(tet10,primary=False),dtype=np.int64).reshape((-1,6,3));emap={};consistency=0.0
        for block in edgeblocks:
            for e in block:
                key=tuple(sorted((int(e[0]),int(e[1]))));candidate=xyz[int(e[2])]
                if key in emap:consistency=max(consistency,float(np.linalg.norm(emap[key][1]-candidate)))
                else:emap[key]=(int(e[2]),candidate)
        doflocs=curved.doflocs.copy();edge_rows=[];missing=0
        for ei,(a,b) in enumerate(curved.edges.T):
            key=tuple(sorted((corners[int(a)],corners[int(b)])))
            if key not in emap:missing+=1;continue
            dof=int(curved.dofs.edge_dofs[0,ei]);mid,loc=emap[key];doflocs[:,dof]=loc;edge_rows.append({"corner_a":key[0],"corner_b":key[1],"mid_tag":mid,"geometry_dof":dof,"x_mm":float(loc[0]),"y_mm":float(loc[1]),"z_mm":float(loc[2]),"warning":WARNING})
        curved=MeshTet2(doflocs,curved.t);screens=[];jacpass=True;wrongtotal=0;normfailtotal=0;minorient=float("inf");minnorm=float("inf")
        for q in (4,6,8):
            X,_=get_quadrature_tet(q);lm=linear.mapping();cm=curved.mapping();ld=np.asarray(lm.detDF(X));cd=np.asarray(cm.detDF(X));orient=cd*np.where(ld>=0,1,-1);DF=np.asarray(cm.DF(X));norm=orient/np.maximum(np.sqrt(np.sum(DF*DF,axis=(0,1)))**3,np.finfo(float).tiny);wrong=int(np.count_nonzero(orient<=0));nf=int(np.count_nonzero(norm<=NORM_GATE));ls=int(np.count_nonzero(np.abs(ld)<=LINEAR_DET_FLOOR));passed=wrong==nf==ls==0;jacpass&=passed;wrongtotal+=wrong;normfailtotal+=nf;minorient=min(minorient,float(np.min(orient)));minnorm=min(minnorm,float(np.min(norm)));screens.append({"quadrature_order":q,"points":int(cd.size),"linear_det_floor_fail":ls,"wrong_or_zero":wrong,"normalized_det_fail":nf,"minimum_oriented_det":float(np.min(orient)),"minimum_normalized_det":float(np.min(norm)),"gate":"PASS" if passed else "FAIL","warning":WARNING})
        rawpath=OUT/"raw-v04-constrained.npz";np.savez_compressed(rawpath,linear_node_tags=np.asarray(linear_ntags),linear_node_xyz=linear_points,linear_element_tags=np.asarray(linear_etags),linear_tet4=linear_raw,tet10_node_tags=np.asarray(ntags),tet10_node_xyz=points,tet10_element_tags=np.asarray(etags),tet10_connectivity=raw,linear_sicn=sicn,**{f"pre_{k}":np.asarray(sorted(v)) for k,v in pre_membership.items()},**{f"post_{k}":np.asarray(sorted(v)) for k,v in post_membership.items()})
        write_csv(OUT/"corner-correspondence.csv",correspondence);write_csv(OUT/"element-identity.csv",element_rows);write_csv(OUT/"occ-membership.csv",membership_rows);write_csv(OUT/"edge-map.csv",edge_rows);write_csv(OUT/"jacobian-screens.csv",screens)
        sicnpass=bool(np.min(sicn)>=.10 and np.mean(sicn<.20)<=.001);methodpass=bool(pre_bijection and restore_gate and connectivity and orientation and membership and missing==0 and consistency<=RESTORE_TOL and sicnpass and jacpass)
        result={"identifier":IDENT,"round":"R284","baseline_commit":"d36bb8d5979364c9fcf5a46101fcf79500c61f99","step_sha256":sha(STEP),"variant":"V04_REFINED_CONSTRAINED_HIGH_ORDER","corners":len(corners),"tet10_elements":len(etags),"global_edges":int(curved.edges.shape[1]),"pre_restore_bijection_tolerance_mm":BIJECTION_TOL,"pre_restore_bijection_max_distance_mm":float(np.max(dist)),"pre_restore_bijection_unique":pre_bijection,"post_restore_max_distance_mm":restore_max,"post_restore_tolerance_mm":RESTORE_TOL,"post_restore_gate":restore_gate,"optimized_midsides_retained":True,"element_connectivity_gate":connectivity,"element_orientation_gate":orientation,"occ_corner_membership_gate":membership,"missing_edges":missing,"midnode_consistency_max_mm":consistency,"minimum_linear_sicn":float(np.min(sicn)),"fraction_linear_sicn_below_0p20":float(np.mean(sicn<.20)),"linear_sicn_gate":sicnpass,"quadrature_orders":"4;6;8","jacobian_evidence_scope":"finite samples at solver-reference tetrahedral quadrature orders 4, 6, and 8; not a proof over the full curved element domain and not actual future structural-assembly quadrature unless that solver selects the same rule","wrong_or_zero_total":wrongtotal,"normalized_det_fail_total":normfailtotal,"minimum_oriented_det":minorient,"minimum_normalized_det":minnorm,"curved_jacobian_gate":jacpass,"raw_npz":rawpath.relative_to(ROOT).as_posix(),"raw_npz_sha256":sha(rawpath),"bounded_constrained_high_order_method_pass":methodpass,"corner_restoration_curved_entity_conformity_revalidated":False,"surface_deviation_from_brep_complete":False,"exact_facet_map_complete":False,"r279_c02_complete":False,"r278_h02_closed":False,"selected":False,"safety_credit":False,"capacity_credit":False,"work_authority":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"seconds":time.perf_counter()-start,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2));return 0 if methodpass else 2
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
