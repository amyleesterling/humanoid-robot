#!/usr/bin/env python3
"""Freeze exact P0.13 C07 OCC feature identities for an R285 remesh attempt.

Tags are diagnostic only.  Stable identity is the STEP hash plus geometric and
owner-boundary signatures.  This tool creates no mesh and grants no authority.
"""
from __future__ import annotations
import csv,hashlib,json,math,shutil
from pathlib import Path
import gmsh

ROOT=Path(__file__).resolve().parents[1]
STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-target-feature-identity-p0.1"
IDENT="HR-V0-J2-C07-TARGET-FEATURE-IDENTITY-P0.1"
WARNING="PRELIMINARY - EXACT FEATURE-IDENTITY AND REMESH-PRESCRIPTION PROTOTYPE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
TOL=2e-3

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(value:object)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
def close(a:float,b:float)->bool:return abs(a-b)<=TOL
def bbox(dim:int,tag:int)->tuple[float,...]:return tuple(float(x) for x in gmsh.model.getBoundingBox(dim,tag))
def write_csv(path:Path,records:list[dict[str,object]])->None:
    if not records:raise RuntimeError(f"empty table {path}")
    fields=[]
    for row in records:
        for key in row:
            if key not in fields:fields.append(key)
    with path.open("w",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)

def geom_record(dim:int,tag:int)->dict[str,object]:
    b=bbox(dim,tag);center=gmsh.model.occ.getCenterOfMass(dim,tag)
    kind=gmsh.model.getType(dim,tag);radius=None
    if kind in ("Cylinder","Circle"):radius=round(max(b[3]-b[0],b[5]-b[2])/2.0,9)
    return {"dimension":dim,"geometry_type":kind,"bbox_mm":[round(x,9) for x in b],"center_of_mass_mm":[round(float(x),9) for x in center],"axis_direction":[0.0,1.0,0.0] if kind in ("Cylinder","Circle") else None,"axis_xz_mm":[round((b[0]+b[3])/2.0,9),round((b[2]+b[5])/2.0,9)] if kind in ("Cylinder","Circle") else None,"radius_mm":radius,"measure_mm_or_mm2":round(float(gmsh.model.occ.getMass(dim,tag)),9)}

def curve_signature(tag:int)->tuple[str,dict[str,object]]:
    record=geom_record(1,tag);return stable(record),record

def face_signature(tag:int)->tuple[str,dict[str,object]]:
    record=geom_record(2,tag);boundary=sorted({curve_signature(curve)[0] for dim,curve in gmsh.model.getBoundary([(2,tag)],combined=False,oriented=False) if dim==1});record["unique_boundary_curve_signatures"]=boundary
    return stable(record),record

def boss_name(b:tuple[float,...])->str:
    x=(b[0]+b[3])/2;z=(b[2]+b[5])/2;return f"BOSS_X{'P' if x>0 else 'M'}16_Z{'P' if z>0 else 'M'}8"

def bore_name(b:tuple[float,...])->str:
    x=round((b[0]+b[3])/2);z=round((b[2]+b[5])/2)
    return {(-16,-8):"H1_XM16_ZM8",(-16,8):"H2_XM16_ZP8",(16,-8):"H3_XP16_ZM8",(16,8):"H4_XP16_ZP8",(0,-10):"E1_X0_ZM10",(0,10):"E2_X0_ZP10"}[(x,z)]

def select_faces()->dict[str,list[int]]:
    groups={"BACKSIDE_BOSS_SURFACES":[],"ORIGINAL_BORE_SURFACES":[],"TOP_RAIL_TRANSITION_SURFACES":[]}
    bore_specs=((-16,-8,1.35,0,9.525),(-16,8,1.35,0,9.525),(16,-8,1.35,0,9.525),(16,8,1.35,0,9.525),(0,-10,2.75,2.9,9.525),(0,10,2.75,2.9,9.525))
    for _,tag in gmsh.model.getEntities(2):
        if gmsh.model.getType(2,tag)!="Cylinder":continue
        b=bbox(2,tag);cx=(b[0]+b[3])/2;cz=(b[2]+b[5])/2;rx=(b[3]-b[0])/2;rz=(b[5]-b[2])/2
        if close(b[1],-15.875) and close(b[4],0) and close(rx,2.6) and close(rz,2.6) and any(close(cx,x) and close(cz,z) for x in (-16,16) for z in (-8,8)):
            groups["BACKSIDE_BOSS_SURFACES"].append(tag)
        if any(close(cx,x) and close(cz,z) and close(rx,r) and close(rz,r) and close(b[1],y0) and close(b[4],y1) for x,z,r,y0,y1 in bore_specs):
            groups["ORIGINAL_BORE_SURFACES"].append(tag)
        top_specs=((-49.2,20.2),(49.2,20.2))
        if close(b[1],8.005) and close(b[4],8.525) and close(rx,1.0) and close(rz,1.0) and any(close(cx,x) and close(cz,z) for x,z in top_specs):
            groups["TOP_RAIL_TRANSITION_SURFACES"].append(tag)
    expected={"BACKSIDE_BOSS_SURFACES":4,"ORIGINAL_BORE_SURFACES":6,"TOP_RAIL_TRANSITION_SURFACES":2}
    actual={key:len(value) for key,value in groups.items()}
    if actual!=expected:raise RuntimeError(f"face selector drift expected={expected} actual={actual}")
    return groups

def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R285_FEATURE_IDENTITY");imported=gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize()
        if len(imported)!=1 or imported[0][0]!=3:raise RuntimeError(f"unexpected STEP volumes {imported}")
        face_groups=select_faces();rows=[];summaries=[];all_signatures=set()
        for group,faces in face_groups.items():
            face_rows=[];curve_tags=set()
            for face in faces:
                b=bbox(2,face);owner=boss_name(b) if group.startswith("BACKSIDE") else bore_name(b) if group.startswith("ORIGINAL") else f"TOP_RAIL_X{'P' if (b[0]+b[3])/2>0 else 'M'}"
                fsig,detail=face_signature(face);all_signatures.add(fsig);boundary=sorted({tag for dim,tag in gmsh.model.getBoundary([(2,face)],combined=False,oriented=False) if dim==1})
                curve_tags.update(boundary);face_rows.append((owner,face,fsig,detail,boundary))
                rows.append({"feature_group":group,"stable_owner":owner,"entity_role":"CYLINDRICAL_SURFACE","dimension":2,"occ_tag_diagnostic_only":face,"geometric_signature_sha256":fsig,"geometry_type":detail["geometry_type"],"bbox_mm_json":json.dumps(detail["bbox_mm"],separators=(",",":")),"center_of_mass_mm_json":json.dumps(detail["center_of_mass_mm"],separators=(",",":")),"axis_direction_json":json.dumps(detail["axis_direction"],separators=(",",":")),"axis_xz_mm_json":json.dumps(detail["axis_xz_mm"],separators=(",",":")),"radius_mm":detail["radius_mm"],"measure_mm_or_mm2":detail["measure_mm_or_mm2"],"owner_face_signature_sha256":"SELF","identity_rule":"STEP SHA + exact geometry + unique boundary signatures; OCC tag diagnostic only","warning":WARNING})
            curve_role_counts={}
            for owner,face,fsig,_detail,boundary in face_rows:
                for curve in boundary:
                    csig,cdetail=curve_signature(curve);b=cdetail["bbox_mm"];kind=cdetail["geometry_type"]
                    if group=="BACKSIDE_BOSS_SURFACES":role="BACK_RIM" if close(b[1],-15.875) and close(b[4],-15.875) else "FRONT_INTERSECTION_RIM" if kind!="Line" else "AXIAL_SEAM"
                    elif group=="ORIGINAL_BORE_SURFACES":role="BORE_RIM" if kind!="Line" else "AXIAL_SEAM"
                    else:role="LOWER_R2_ARC" if kind=="Circle" and close(b[1],8.005) else "UPPER_R2_ARC" if kind=="Circle" and close(b[1],8.525) else "AXIAL_SEAM"
                    key=(fsig,csig)
                    if any(row.get("owner_face_signature_sha256")==fsig and row["geometric_signature_sha256"]==csig for row in rows):continue
                    all_signatures.add(csig);curve_role_counts[role]=curve_role_counts.get(role,0)+1
                    rows.append({"feature_group":group.replace("_SURFACES","_BOUNDARY_CURVES"),"stable_owner":owner,"entity_role":role,"dimension":1,"occ_tag_diagnostic_only":curve,"geometric_signature_sha256":csig,"geometry_type":kind,"bbox_mm_json":json.dumps(b,separators=(",",":")),"center_of_mass_mm_json":json.dumps(cdetail["center_of_mass_mm"],separators=(",",":")),"axis_direction_json":json.dumps(cdetail["axis_direction"],separators=(",",":")) if cdetail["axis_direction"] else "N/A","axis_xz_mm_json":json.dumps(cdetail["axis_xz_mm"],separators=(",",":")) if cdetail["axis_xz_mm"] else "N/A","radius_mm":cdetail["radius_mm"] if cdetail["radius_mm"] is not None else "N/A","measure_mm_or_mm2":cdetail["measure_mm_or_mm2"],"owner_face_signature_sha256":fsig,"identity_rule":"STEP SHA + exact curve geometry + owner-face signature; OCC tag diagnostic only","warning":WARNING})
            expected_roles={"BACKSIDE_BOSS_SURFACES":{"BACK_RIM":4,"FRONT_INTERSECTION_RIM":12,"AXIAL_SEAM":4},"ORIGINAL_BORE_SURFACES":{"BORE_RIM":12,"AXIAL_SEAM":6},"TOP_RAIL_TRANSITION_SURFACES":{"LOWER_R2_ARC":2,"UPPER_R2_ARC":2,"AXIAL_SEAM":4}}[group]
            if curve_role_counts!=expected_roles:raise RuntimeError(f"{group} topology drift expected={expected_roles} actual={curve_role_counts}")
            summaries.append({"surface_group":group,"surface_count":len(faces),"unique_boundary_curve_count":len(curve_tags),"curve_role_counts_json":json.dumps(curve_role_counts,sort_keys=True,separators=(",",":")),"topology_gate":"PASS","warning":WARNING})
        if len(all_signatures)!=len(rows):raise RuntimeError("nonunique geometric/entity-owner signatures")
        write_csv(OUT/"exact-feature-identity-register.csv",rows);write_csv(OUT/"feature-topology-summary.csv",summaries)
        owner_faces={row["stable_owner"]:row for row in rows if row["dimension"]==2}
        symmetry_pairs=[("BOSS_XM16_ZM8","BOSS_XP16_ZM8","X_MIRROR"),("BOSS_XM16_ZP8","BOSS_XP16_ZP8","X_MIRROR"),("H1_XM16_ZM8","H3_XP16_ZM8","X_MIRROR"),("H2_XM16_ZP8","H4_XP16_ZP8","X_MIRROR"),("E1_X0_ZM10","E1_X0_ZM10","X_SELF"),("E2_X0_ZP10","E2_X0_ZP10","X_SELF"),("TOP_RAIL_XM","TOP_RAIL_XP","X_MIRROR")]
        symmetry=[]
        for left,right,operation in symmetry_pairs:
            a=owner_faces[left];b=owner_faces[right];ba=json.loads(a["bbox_mm_json"]);bb=json.loads(b["bbox_mm_json"])
            passed=close(ba[0],-bb[3]) and close(ba[3],-bb[0]) and all(close(ba[i],bb[i]) for i in (1,2,4,5)) and close(float(a["radius_mm"]),float(b["radius_mm"])) and close(float(a["measure_mm_or_mm2"]),float(b["measure_mm_or_mm2"]))
            if not passed:raise RuntimeError(f"symmetry drift {left} {right}")
            symmetry.append({"left_owner":left,"right_owner":right,"operation":operation,"left_signature_sha256":a["geometric_signature_sha256"],"right_signature_sha256":b["geometric_signature_sha256"],"radius_and_measure_match":passed,"bbox_x_mirror_match":passed,"gate":"PASS","warning":WARNING})
        write_csv(OUT/"symmetry-pair-register.csv",symmetry)
        fields=[
            {"field_id":"R285-F01","entities":"ORIGINAL_BORE_SURFACES + ORIGINAL_BORE_BOUNDARY_CURVES","size_min_mm":0.75,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":3.0,"basis":"V06 passing hole_h=0.75 mm; retains source grading","status":"RECOMMENDED BOUNDED RETRY; NOT ACCEPTED PRODUCTION","warning":WARNING},
            {"field_id":"R285-F02","entities":"BACKSIDE_BOSS_SURFACES + BACKSIDE_BOSS_BOUNDARY_CURVES","size_min_mm":0.75,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":3.0,"basis":"8/11 V03 failed elements localized on previously ungrouped boss cylinders; match V06 hole scale","status":"RECOMMENDED BOUNDED RETRY; NOT ACCEPTED PRODUCTION","warning":WARNING},
            {"field_id":"R285-F03","entities":"TOP_RAIL_TRANSITION_SURFACES + TOP_RAIL_TRANSITION_BOUNDARY_CURVES","size_min_mm":0.50,"size_max_mm":3.0,"dist_min_mm":0.0,"dist_max_mm":2.5,"basis":"V06 passing pocket-scale start; cross-level V03/V08 negative-X cluster","status":"RECOMMENDED BOUNDED RETRY; NOT ACCEPTED PRODUCTION","warning":WARNING},
            {"field_id":"R285-F04","entities":"TOP_RAIL_TRANSITION_SURFACES + TOP_RAIL_TRANSITION_BOUNDARY_CURVES","size_min_mm":0.35,"size_max_mm":2.0,"dist_min_mm":0.0,"dist_max_mm":2.5,"basis":"only for V08 nominal-level retry; matches V08 pocket scale","status":"ALTERNATE DIAGNOSTIC RETRY; DO NOT COMBINE WITH R285-F03","warning":WARNING},
        ];write_csv(OUT/"recommended-distance-fields.csv",fields)
        prereg={"identifier":IDENT,"step_sha256":sha(STEP),"identity_policy":"Match exact entity geometry and owner adjacency to these signatures before using transient OCC tags; exact count mismatch or empty group stops meshing.","groups":{},"distance_fields":fields,"authority":{"mesh_generation":False,"h02":False,"capacity":False,"work":False},"warning":WARNING}
        for group in face_groups:
            curve_group=group.replace("_SURFACES","_BOUNDARY_CURVES")
            prereg["groups"][group]={"dimension":2,"expected_count":sum(row["feature_group"]==group for row in rows),"expected_geometry_type":"Cylinder","geometric_signatures_sha256":sorted(row["geometric_signature_sha256"] for row in rows if row["feature_group"]==group)}
            prereg["groups"][curve_group]={"dimension":1,"expected_count":sum(row["feature_group"]==curve_group for row in rows),"owner_face_required":True,"geometric_signatures_sha256":sorted(row["geometric_signature_sha256"] for row in rows if row["feature_group"]==curve_group)}
        (OUT/"factor-model-feature-preregistration.json").write_text(json.dumps(prereg,indent=2)+"\n",encoding="utf-8")
        status={"identifier":IDENT,"round":"R285-FEATURE-FREEZE","step_sha256":sha(STEP),"surface_groups_frozen":3,"surface_entities":12,"boundary_curve_entities":46,"feature_topology_gate":True,"mesh_generated":False,"curved_jacobian_screen_executed":False,"structural_solution_executed":False,"mesh_convergence_complete":False,"r278_h02_closed":False,"capacity_credit":False,"work_authority":False,"warning":WARNING}
        (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        provenance={"generator_sha256":sha(Path(__file__).resolve()),"step_path":STEP.relative_to(ROOT).as_posix(),"step_sha256":sha(STEP),"gmsh_build":gmsh.option.getString("General.BuildInfo"),"warning":WARNING};(OUT/"execution-provenance.json").write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
        files=[]
        for path in sorted(OUT.iterdir()):
            if path.is_file() and path.name!="file-manifest.csv":files.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",files)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
