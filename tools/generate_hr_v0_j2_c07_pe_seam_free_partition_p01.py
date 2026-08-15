#!/usr/bin/env python3
"""Create the R297 seam-free PE analysis partition from the exact R288 B-Rep."""
from __future__ import annotations
import csv,hashlib,json,platform,shutil,sys
from pathlib import Path
import gmsh

ROOT=Path(__file__).resolve().parents[1]
R288=ROOT/"mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
R296=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-disposition-p0.1"
SOURCE_BREP=R288/"c07-exact-zone-fragmented.brep";SOURCE_FRAGMENTS=R288/"fragment-volume-register.csv";SOURCE_ZONES=R288/"exact-zone-register.csv"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-partition-p0.1"
IDENT="HR-V0-J2-C07-PE-SEAM-FREE-PARTITION-P0.1";WARNING="PRELIMINARY - SEAM-FREE PE ANALYSIS PARTITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
def rows(p:Path)->list[dict[str,str]]:
    with p.open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def bbox(dim:int,tag:int)->list[float]:return [round(float(v),9) for v in gmsh.model.getBoundingBox(dim,tag)]
def signature(dim:int,tag:int)->str:
    record={"dimension":dim,"geometry_type":gmsh.model.getType(dim,tag),"bbox_mm":bbox(dim,tag),"measure":round(float(gmsh.model.occ.getMass(dim,tag)),9),"center_of_mass_mm":[round(float(v),9) for v in gmsh.model.occ.getCenterOfMass(dim,tag)]}
    children=[]
    for d,t in gmsh.model.getBoundary([(dim,tag)],combined=False,oriented=False):children.append({"dimension":d,"geometry_type":gmsh.model.getType(d,t),"bbox_mm":bbox(d,t),"measure":round(float(gmsh.model.occ.getMass(d,t)),9)})
    record["boundary"]=sorted(children,key=lambda x:json.dumps(x,sort_keys=True));return stable(record)
def only_volume(out:list[tuple[int,int]],label:str)->int:
    v=[t for d,t in out if d==3]
    if len(v)!=1:raise RuntimeError(f"{label}: expected one volume, got {out}")
    return v[0]
def main()->int:
    boundary=json.loads((R296/"next-partition-boundary.json").read_text(encoding="utf-8"));source_status=json.loads((R288/"analysis-status.json").read_text(encoding="utf-8"))
    if boundary["next_partition_executed"] or boundary["physical_geometry_changed"]:raise RuntimeError("R296 boundary drift")
    if sha(SOURCE_BREP)!=source_status["brep_sha256"]:raise RuntimeError("R288 B-Rep drift")
    source_fragments=rows(SOURCE_FRAGMENTS);source_zones=rows(SOURCE_ZONES)
    pe_zones={r["zone_id"] for r in source_zones if r["family"]=="C07-PE"}
    pe_signatures={r["fragment_signature_sha256"] for r in source_fragments if r["zone_id"] in pe_zones}
    if len(pe_zones)!=8 or len(pe_signatures)!=8:raise RuntimeError("R288 PE identity drift")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        # Retain the eight exact material subzone solids independently.
        gmsh.model.add("R297_PE_CLASSIFICATION")
        gmsh.model.occ.importShapes(str(SOURCE_BREP));gmsh.model.occ.synchronize()
        by_sig={signature(3,t):t for d,t in gmsh.model.getEntities(3)}
        if not pe_signatures.issubset(by_sig):raise RuntimeError("PE signatures did not reproduce")
        remove=[(3,t) for sig,t in by_sig.items() if sig not in pe_signatures]
        gmsh.model.occ.remove(remove,recursive=True);gmsh.model.occ.synchronize()
        if len(gmsh.model.getEntities(3))!=8:raise RuntimeError("classification B-Rep volume count")
        class_path=OUT/"c07-pe-eight-subzone-classification.brep";gmsh.write(str(class_path))

        gmsh.clear();gmsh.model.add("R297_SEAM_FREE_ANALYSIS_PARTITION")
        gmsh.model.occ.importShapes(str(SOURCE_BREP));gmsh.model.occ.synchronize()
        by_sig={signature(3,t):t for d,t in gmsh.model.getEntities(3)}
        source_by_sig={r["fragment_signature_sha256"]:r for r in source_fragments}
        if set(by_sig)!=set(source_by_sig):raise RuntimeError("full R288 signature set drift")
        pe_tags=[by_sig[s] for s in sorted(pe_signatures)]
        original_total=sum(float(gmsh.model.occ.getMass(3,t)) for d,t in gmsh.model.getEntities(3))
        original_pe=sum(float(gmsh.model.occ.getMass(3,t)) for t in pe_tags)
        # Fuse the full connected ring in one Boolean operation.  A sequential
        # signature-sorted fuse can begin with two nonadjacent sectors and
        # legitimately return two intermediate volumes.
        out,_=gmsh.model.occ.fuse([(3,pe_tags[0])],[(3,tag) for tag in pe_tags[1:]],removeObject=True,removeTool=True)
        current=only_volume(out,"eight-piece PE fuse")
        gmsh.model.occ.synchronize()
        volumes=[t for d,t in gmsh.model.getEntities(3)]
        if len(volumes)!=21:raise RuntimeError(f"seam-free partition volume count {len(volumes)}")
        fused_volume=float(gmsh.model.occ.getMass(3,current))
        other_tags=sorted(t for t in volumes if t!=current)
        input_tags=[current,*other_tags]
        input_zone={current:"C07-PE-FUSED"}
        input_mass={current:fused_volume}
        for tag in other_tags:
            sig=signature(3,tag)
            if sig not in source_by_sig:raise RuntimeError(f"unaffected pre-fragment volume signature changed {sig}")
            input_zone[tag]=source_by_sig[sig]["zone_id"]
            input_mass[tag]=float(gmsh.model.occ.getMass(3,tag))

        # Re-fragment the full 21-volume compound so every remaining material
        # interface is topologically shared.  The removed PE-to-PE seams cannot
        # return because the PE ring is now one input volume.
        out,mapping=gmsh.model.occ.fragment([(3,current)],[(3,tag) for tag in other_tags],removeObject=True,removeTool=True)
        gmsh.model.occ.synchronize()
        if len(mapping)!=21:raise RuntimeError(f"conformal re-fragment mapping count {len(mapping)}")
        zone_by_tag={}
        max_mapping_volume_error=0.0
        for old_tag,mapped in zip(input_tags,mapping):
            mapped_volumes=[tag for dim,tag in mapped if dim==3]
            if len(mapped_volumes)!=1:raise RuntimeError(f"analysis volume {input_zone[old_tag]} mapped to {mapped_volumes}")
            new_tag=mapped_volumes[0]
            if new_tag in zone_by_tag:raise RuntimeError(f"duplicate conformal output volume {new_tag}")
            zone_by_tag[new_tag]=input_zone[old_tag]
            mapped_mass=float(gmsh.model.occ.getMass(3,new_tag))
            max_mapping_volume_error=max(max_mapping_volume_error,abs(mapped_mass-input_mass[old_tag])/input_mass[old_tag])
        volumes=[t for d,t in gmsh.model.getEntities(3)]
        if len(volumes)!=21 or set(volumes)!=set(zone_by_tag):raise RuntimeError("conformal re-fragment output identity drift")
        current=next(tag for tag,zone_id in zone_by_tag.items() if zone_id=="C07-PE-FUSED")
        fused_volume=float(gmsh.model.occ.getMass(3,current));new_total=sum(float(gmsh.model.occ.getMass(3,t)) for t in volumes)
        pe_error=abs(fused_volume-original_pe)/original_pe;total_error=abs(new_total-original_total)/original_total
        if pe_error>1e-10 or total_error>1e-10 or max_mapping_volume_error>1e-10:raise RuntimeError(f"volume closure PE={pe_error} total={total_error} map={max_mapping_volume_error}")
        analysis_path=OUT/"c07-pe-seam-free-analysis-partition.brep";gmsh.write(str(analysis_path))
        analysis_rows=[]
        for tag in volumes:
            sig=signature(3,tag);volume=float(gmsh.model.occ.getMass(3,tag))
            zone_id=zone_by_tag[tag]
            if zone_id=="C07-PE-FUSED":
                zone_id="C07-PE-FUSED";family="C07-PE";source="UNION OF EIGHT EXACT R288 PE MATERIAL SUBZONES"
            else:
                family="C07-MATRIX" if zone_id=="C07-MATRIX" else next(r["family"] for r in source_zones if r["zone_id"]==zone_id);source="ONE-TO-ONE R288 MATERIAL VOLUME AFTER CONFORMAL RE-FRAGMENT"
            analysis_rows.append({"fragment_tag_diagnostic_only":tag,"fragment_signature_sha256":sig,"bbox_mm_json":json.dumps(bbox(3,tag),separators=(",",":")),"center_of_mass_mm_json":json.dumps([round(float(v),9) for v in gmsh.model.occ.getCenterOfMass(3,tag)],separators=(",",":")),"volume_mm3":volume,"zone_id":zone_id,"family":family,"source":source,"warning":WARNING})
        write_csv(OUT/"analysis-fragment-register.csv",sorted(analysis_rows,key=lambda r:r["zone_id"]))
        zone_rows=[]
        for r in analysis_rows:zone_rows.append({"zone_id":r["zone_id"],"family":r["family"],"material_fragment_count":1,"material_volume_mm3":r["volume_mm3"],"quality_rule":"ALL FUSED PE CELLS >=0.20 CONSERVATIVELY COVERS EACH EXACT PE SUBZONE" if r["zone_id"]=="C07-PE-FUSED" else "DIRECT CONFORMAL MATERIAL-VOLUME MEMBERSHIP","classification":"EXACT OCC MATERIAL VOLUME","warning":WARNING})
        write_csv(OUT/"analysis-zone-register.csv",sorted(zone_rows,key=lambda r:r["zone_id"]))
        class_rows=[]
        for r in source_zones:
            if r["zone_id"] in pe_zones:class_rows.append({"zone_id":r["zone_id"],"family":"C07-PE","exact_material_volume_mm3":r["material_volume_mm3"],"source_fragment_signatures_sha256_json":r["fragment_signatures_sha256_json"],"subset_of":"C07-PE-FUSED","conservative_quality_inheritance":"if every C07-PE-FUSED cell SICN >=0.20 then every cell intersecting this exact subset also meets >=0.20","classification_brep_sha256":"PENDING AFTER WRITE","warning":WARNING})
        class_sha=sha(class_path)
        for r in class_rows:r["classification_brep_sha256"]=class_sha
        write_csv(OUT/"retained-pe-subzone-classification-register.csv",sorted(class_rows,key=lambda r:r["zone_id"]))
        status={"identifier":IDENT,"round":"R297","date":"2026-08-13","source_r288_brep_sha256":sha(SOURCE_BREP),"analysis_brep_sha256":sha(analysis_path),"brep_sha256":sha(analysis_path),"classification_brep_sha256":class_sha,"authoritative_physical_geometry_changed":False,"r288_material_volume_count":28,"seam_free_material_volume_count":21,"fused_pe_material_volume_count":1,"retained_exact_pe_subzone_count":8,"unaffected_material_volume_count":20,"pe_union_relative_volume_error":pe_error,"total_material_relative_volume_error":total_error,"maximum_one_to_one_mapping_relative_volume_error":max_mapping_volume_error,"conformal_shared_interface_refragmented":True,"internal_tangent_pe_seams_removed":True,"mesh_generated":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING}
        (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        (OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_path":Path(__file__).resolve().relative_to(ROOT).as_posix(),"generator_sha256":sha(Path(__file__).resolve()),"r288_brep_sha256":sha(SOURCE_BREP),"r288_fragment_register_sha256":sha(SOURCE_FRAGMENTS),"r288_zone_register_sha256":sha(SOURCE_ZONES),"r296_boundary_sha256":sha(R296/"next-partition-boundary.json"),"python":sys.version,"platform":platform.platform(),"gmsh_build":gmsh.option.getString("General.BuildInfo"),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
        (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR297 removes only four internal tangent seam planes from the analysis partition by fusing the eight exact R288 PE material fragments into one exact `C07-PE-FUSED` material volume. The authoritative P0.13 physical solid is unchanged. Eight original PE subzone solids are retained in a separate classification B-Rep with exact volumes and signatures.\n\nThe 21 volumes are re-fragmented together after the PE union so every remaining interface is topologically shared; each input maps one-to-one to one output volume and the removed PE-to-PE seams do not return. PE, per-volume, and total material volumes close within 1e-10 relative error. No mesh or structural solve is executed.\n",encoding="utf-8")
        manifest=[]
        for p in sorted(OUT.iterdir()):
            if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",manifest)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
        print(json.dumps(status,indent=2));return 0
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
