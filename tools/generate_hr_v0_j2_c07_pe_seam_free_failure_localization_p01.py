#!/usr/bin/env python3
"""Localize the residual R298 curved-Jacobian and global SICN failures."""
from __future__ import annotations
import csv,gzip,hashlib,json,shutil
from pathlib import Path
import gmsh,numpy as np

ROOT=Path(__file__).resolve().parents[1];R298=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";BREP=R297/"c07-pe-seam-free-analysis-partition.brep"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-failure-localization-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-failure-localization-p0.1";IDENT="HR-V0-J2-C07-PE-SEAM-FREE-FAILURE-LOCALIZATION-P0.1";WARNING="PRELIMINARY - SEAM-FREE MESH FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    if not data:raise RuntimeError(f"empty evidence {p}")
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def face_record(tag:int)->dict[str,object]:
    record={"geometry_type":gmsh.model.getType(2,tag),"bbox_mm":[round(float(v),9) for v in gmsh.model.getBoundingBox(2,tag)],"area_mm2":round(float(gmsh.model.occ.getMass(2,tag)),9),"center_mm":[round(float(v),9) for v in gmsh.model.occ.getCenterOfMass(2,tag)]}
    record["signature_sha256"]=stable(record);return record
def nearest(point:np.ndarray,faces:list[int])->dict[str,object]:
    best=None
    for tag in faces:
        closest,_=gmsh.model.getClosestPoint(2,tag,point.tolist());xyz=np.asarray(closest[:3]);distance=float(np.linalg.norm(xyz-point))
        if best is None or distance<best[0]:best=(distance,tag,xyz)
    assert best is not None;distance,tag,xyz=best;record=face_record(tag)
    return {"nearest_exact_face_tag_diagnostic_only":tag,"nearest_exact_face_signature_sha256":record["signature_sha256"],"nearest_exact_face_type":record["geometry_type"],"nearest_exact_face_bbox_mm_json":json.dumps(record["bbox_mm"],separators=(",",":")),"nearest_exact_face_area_mm2":record["area_mm2"],"nearest_exact_face_center_mm_json":json.dumps(record["center_mm"],separators=(",",":")),"nearest_exact_face_distance_mm":distance,"nearest_exact_point_mm_json":json.dumps([float(v) for v in xyz],separators=(",",":"))}
def main()->int:
    st=json.loads((R298/"analysis-status.json").read_text(encoding="utf-8"))
    if not st["global_sicn_gate"] or not st["monitored_zone_minimum_gate"] or st["actual_quadrature_signed_jacobian_gate"] or st["r279_c02_complete"]:raise RuntimeError("R298 residual failure state drift")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);working=OUT/"_working.msh";digest=hashlib.sha256()
    with gzip.open(R298/"c07-conformal-zone-mesh.msh.gz","rb") as source,working.open("wb") as target:
        while True:
            b=source.read(1024*1024)
            if not b:break
            target.write(b);digest.update(b)
    if digest.hexdigest()!=st["mesh_uncompressed_sha256"]:raise RuntimeError("mesh gzip identity")
    raw=np.load(R298/"raw-conformal-zone-mesh.npz");q=raw["linear_sicn"];tags=raw["linear_element_tags"];conn=raw["linear_tet4_connectivity"];nodes={int(t):xyz for t,xyz in zip(raw["linear_node_tags"],raw["linear_node_xyz"])}
    low=[]
    for i in np.flatnonzero(q<.20):
        xyz=np.vstack([nodes[int(t)] for t in conn[i]])
        low.append({"element_tag":int(tags[i]),"sicn":float(q[i]),"centroid_x_mm":float(np.mean(xyz[:,0])),"centroid_y_mm":float(np.mean(xyz[:,1])),"centroid_z_mm":float(np.mean(xyz[:,2])),"credit":"GLOBAL QUALITY DIAGNOSTIC; GLOBAL FRACTION GATE STILL PASSES","warning":WARNING})
    write_csv(OUT/"global-low-sicn-localization.csv",low)
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0);failures=[]
    try:
        gmsh.open(str(working));tet10=gmsh.model.mesh.getElementType("tetrahedron",2);matrix=None
        for d,p in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(d,p)=="C07-MATRIX":matrix=int(gmsh.model.getEntitiesForPhysicalGroup(d,p)[0])
        if matrix is None:raise RuntimeError("matrix physical volume")
        etags=None
        types,blocks,_=gmsh.model.mesh.getElements(3,matrix)
        for typ,block in zip(types,blocks):
            if int(typ)==int(tet10):etags=np.asarray(block,dtype=np.int64)
        if etags is None:raise RuntimeError("matrix Tet10 tags")
        for order in (4,6,8):
            local,_=gmsh.model.mesh.getIntegrationPoints(tet10,f"Gauss{order}");points=np.asarray(local).reshape((-1,3));jacraw,detraw,coordsraw=gmsh.model.mesh.getJacobians(tet10,local,matrix);det=np.asarray(detraw).reshape((len(etags),len(points)));jac=np.asarray(jacraw).reshape((len(etags),len(points),3,3));coords=np.asarray(coordsraw).reshape((len(etags),len(points),3));norm=det/np.maximum(np.sqrt(np.sum(jac*jac,axis=(2,3)))**3,np.finfo(float).tiny)
            for ei,qi in np.argwhere((det<=0)|(norm<=1e-10)):
                point=coords[ei,qi];failures.append({"quadrature_order":order,"element_tag":int(etags[ei]),"quadrature_point_index":int(qi),"physical_x_mm":float(point[0]),"physical_y_mm":float(point[1]),"physical_z_mm":float(point[2]),"determinant":float(det[ei,qi]),"normalized_determinant":float(norm[ei,qi]),"warning":WARNING})
        gmsh.clear();gmsh.model.add("R299_EXACT_FACE");gmsh.model.occ.importShapes(str(BREP));gmsh.model.occ.synchronize();faces=[t for d,t in gmsh.model.getEntities(2)]
        for r in failures:r.update(nearest(np.asarray([r["physical_x_mm"],r["physical_y_mm"],r["physical_z_mm"]]),faces))
    finally:gmsh.finalize()
    working.unlink();write_csv(OUT/"curved-jacobian-failure-localization.csv",failures)
    elements=sorted({r["element_tag"] for r in failures});face_sigs=sorted({r["nearest_exact_face_signature_sha256"] for r in failures})
    status={"identifier":IDENT,"round":"R299","date":"2026-08-13","r298_raw_sha256":sha(R298/"raw-conformal-zone-mesh.npz"),"global_low_sicn_cells":len(low),"curved_failed_order_qp_pairs":len(failures),"curved_unique_failed_elements":len(elements),"nearest_exact_face_clusters":len(face_sigs),"global_quality_gate_retained":True,"monitored_zone_gate_retained":True,"remesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"r298_status_sha256":sha(R298/"analysis-status.json"),"r298_raw_sha256":sha(R298/"raw-conformal-zone-mesh.npz"),"r298_mesh_gzip_sha256":sha(R298/"c07-conformal-zone-mesh.msh.gz"),"r297_brep_sha256":sha(BREP),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR299 localizes the residual R298 evidence: {len(low)} global cell below SICN 0.20 (permitted by the global fraction gate) and {len(failures)} failed Gauss-order/QP pairs across {len(elements)} curved Tet10 element(s). Exact nearest R297 B-Rep faces are retained for the next preregistration. No remesh or structural work is executed.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
