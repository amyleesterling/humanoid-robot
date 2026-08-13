#!/usr/bin/env python3
"""Execute the preregistered R312 24-face exterior analysis-surface imprint."""
from __future__ import annotations
import csv,hashlib,json,platform,shutil,sys
from pathlib import Path
import gmsh
import generate_hr_v0_j2_c07_pe_seam_free_partition_p01 as r297
import generate_hr_v0_j2_c07_target_feature_identity_p01 as feature
ROOT=Path(__file__).resolve().parents[1];R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R311=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-corrected-surface-imprint-prereg-p0.1";STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-corrected-surface-imprint-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-corrected-surface-imprint-p0.1";IDENT="HR-V0-J2-C07-PE-CORRECTED-SURFACE-IMPRINT-P0.1";WARNING="PRELIMINARY - CORRECTED 24-FACE ANALYSIS-SURFACE IMPRINT EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def write_csv(path:Path,data:list[dict[str,object]])->None:
    fields=[]
    for row in data:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    protocol_path=PREREG/"frozen-protocol.json";protocol=json.loads(protocol_path.read_text())
    if protocol["topology_execution_complete"] or protocol["executor_sha256"]!=sha(Path(__file__).resolve()):raise RuntimeError("R312 protocol state")
    expected=set(protocol["exact_face_signatures_sha256"]);source_rows=rows(R297/"analysis-fragment-register.csv");source_by_sig={row["fragment_signature_sha256"]:row for row in source_rows}
    if len(expected)!=24 or sha(R297/"c07-pe-seam-free-analysis-partition.brep")!=protocol["source_r297_analysis_brep_sha256"]:raise RuntimeError("R312 source identity")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        # Build a controlled surface-tool B-Rep from the exact STEP faces.
        gmsh.model.add("R312_EXACT_SURFACE_TOOLS");gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize();selected={tag:feature.face_signature(tag)[0] for _d,tag in gmsh.model.getEntities(2) if feature.face_signature(tag)[0] in expected}
        if set(selected.values())!=expected or len(selected)!=24:raise RuntimeError(f"target face resolution {len(selected)}")
        gmsh.model.occ.remove(gmsh.model.getEntities(3),recursive=False);gmsh.model.occ.remove([(2,tag) for _d,tag in gmsh.model.getEntities(2) if tag not in selected],recursive=False);gmsh.model.occ.synchronize()
        if len(gmsh.model.getEntities(3))!=0 or len(gmsh.model.getEntities(2))!=24:raise RuntimeError("surface tool isolation")
        tool_path=OUT/"exact-24-face-imprint-tools.brep";gmsh.write(str(tool_path))

        gmsh.clear();gmsh.model.add("R312_CORRECTED_SURFACE_IMPRINT");gmsh.model.occ.importShapes(str(R297/"c07-pe-seam-free-analysis-partition.brep"));gmsh.model.occ.synchronize();old_volumes=[tag for _d,tag in gmsh.model.getEntities(3)];old_by_tag={tag:r297.signature(3,tag) for tag in old_volumes}
        if set(old_by_tag.values())!=set(source_by_sig) or len(old_volumes)!=21:raise RuntimeError("R297 volume signatures")
        old_zone={tag:source_by_sig[sig]["zone_id"] for tag,sig in old_by_tag.items()};old_mass={tag:float(gmsh.model.occ.getMass(3,tag)) for tag in old_volumes};old_bbox={tag:r297.bbox(3,tag) for tag in old_volumes};old_com={tag:[float(v) for v in gmsh.model.occ.getCenterOfMass(3,tag)] for tag in old_volumes}
        imported=gmsh.model.occ.importShapes(str(tool_path));gmsh.model.occ.synchronize();tool_faces=[tag for dim,tag in imported if dim==2]
        if len(tool_faces)!=24 or {feature.face_signature(tag)[0] for tag in tool_faces}!=expected:raise RuntimeError("imported surface tools")
        _out,mapping=gmsh.model.occ.fragment([(3,tag) for tag in old_volumes],[(2,tag) for tag in tool_faces],removeObject=True,removeTool=True);gmsh.model.occ.synchronize()
        if len(mapping)!=45:raise RuntimeError(f"fragment mapping count {len(mapping)}")
        zone_by_new={};mapping_rows=[];max_volume=max_bbox=max_com=0.0
        for old_tag,mapped in zip(old_volumes,mapping[:len(old_volumes)]):
            new=[tag for dim,tag in mapped if dim==3]
            if len(new)!=1:raise RuntimeError(f"zone {old_zone[old_tag]} mapped to {new}")
            new_tag=new[0]
            if new_tag in zone_by_new:raise RuntimeError(f"duplicate mapped volume {new_tag}")
            zone_by_new[new_tag]=old_zone[old_tag];mass=float(gmsh.model.occ.getMass(3,new_tag));box=r297.bbox(3,new_tag);com=[float(v) for v in gmsh.model.occ.getCenterOfMass(3,new_tag)];volume_error=abs(mass-old_mass[old_tag])/old_mass[old_tag];bbox_error=max(abs(a-b) for a,b in zip(box,old_bbox[old_tag]));com_error=max(abs(a-b) for a,b in zip(com,old_com[old_tag]));max_volume=max(max_volume,volume_error);max_bbox=max(max_bbox,bbox_error);max_com=max(max_com,com_error);mapping_rows.append({"zone_id":old_zone[old_tag],"source_volume_tag_diagnostic_only":old_tag,"imprinted_volume_tag_diagnostic_only":new_tag,"source_volume_mm3":old_mass[old_tag],"imprinted_volume_mm3":mass,"relative_volume_error":volume_error,"maximum_bbox_delta_mm":bbox_error,"maximum_center_of_mass_delta_mm":com_error,"one_to_one_gate":"PASS","warning":WARNING})
        new_volumes=[tag for _d,tag in gmsh.model.getEntities(3)]
        if len(new_volumes)!=21 or set(new_volumes)!=set(zone_by_new):raise RuntimeError(f"output volume set {len(new_volumes)}")
        total_old=sum(old_mass.values());total_new=sum(float(gmsh.model.occ.getMass(3,tag)) for tag in new_volumes);total_error=abs(total_new-total_old)/total_old
        face_sig_to_tags={}
        for _d,tag in gmsh.model.getEntities(2):face_sig_to_tags.setdefault(feature.face_signature(tag)[0],[]).append(tag)
        target_rows=[];present=set()
        for signature in sorted(expected):
            tags=face_sig_to_tags.get(signature,[]);owners=sorted({int(owner) for tag in tags for owner in gmsh.model.getAdjacencies(2,tag)[0]});gate=len(tags)==1 and len(owners)==1
            if gate:present.add(signature)
            target_rows.append({"exact_face_signature_sha256":signature,"output_face_tags_diagnostic_only_json":json.dumps(tags,separators=(",",":")),"output_owner_volume_tags_diagnostic_only_json":json.dumps(owners,separators=(",",":")),"exact_single_face_single_exterior_owner_gate":"PASS" if gate else "FAIL","warning":WARNING})
        all_faces=present==expected;pe_tags=[tag for tag,zone in zone_by_new.items() if zone=="C07-PE-FUSED"];pe_one=len(pe_tags)==1
        topology_pass=bool(total_error<=1e-12 and max_volume<=1e-12 and max_bbox<=1e-9 and max_com<=1e-9 and len(zone_by_new)==21 and pe_one and all_faces)
        output_brep=OUT/"c07-pe-corrected-surface-imprint-analysis-partition.brep";gmsh.write(str(output_brep));write_csv(OUT/"zone-equivalence-register.csv",sorted(mapping_rows,key=lambda row:row["zone_id"]));write_csv(OUT/"exact-imprinted-face-register.csv",target_rows)
        status={"identifier":IDENT,"round":"R312","date":"2026-08-13","candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"source_r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"tool_brep_sha256":sha(tool_path),"output_brep_sha256":sha(output_brep),"exact_tool_faces":24,"source_analysis_volumes":21,"output_analysis_volumes":len(new_volumes),"zone_one_to_one_mapping_complete":len(zone_by_new)==21,"maximum_zone_relative_volume_error":max_volume,"total_material_relative_volume_error":total_error,"maximum_zone_bbox_delta_mm":max_bbox,"maximum_zone_center_of_mass_delta_mm":max_com,"fused_pe_volume_count":len(pe_tags),"internal_tangent_pe_seams_absent":pe_one,"exact_24_exterior_faces_present":all_faces,"topology_execution_complete":True,"topology_acceptance_pass":topology_pass,"mesh_executed":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"energization_authorized":False,"warning":WARNING};(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"executor_sha256":sha(Path(__file__).resolve()),"preregistration_sha256":sha(protocol_path),"r297_generator_sha256":sha(Path(r297.__file__).resolve()),"feature_signature_generator_sha256":sha(Path(feature.__file__).resolve()),"r311_status_sha256":sha(R311/"analysis-status.json"),"step_sha256":sha(STEP),"gmsh_build":gmsh.option.getString("General.BuildInfo"),"python":sys.version,"platform":platform.platform(),"warning":WARNING},indent=2)+"\n");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR312 executes the one frozen 24-face surface imprint across all 21 R297 analysis volumes. It grants topology evidence only if every zone maps one-to-one with volume/bbox/COM closure, the fused PE band remains one volume, and every corrected exact trimmed face is present with one exterior owner. No mesh or structural solve is executed.\n",encoding="utf-8");write_csv(OUT/"open-holds.csv",[{"hold_id":"R312-H01","hold":"Preregister and execute a successor mesh only if topology acceptance passes.","state":"OPEN","warning":WARNING},{"hold_id":"R312-H02","hold":"Repeat corrected exact-trim ownership, Q4/Q6/Q8, B-Rep area and load preservation on that mesh.","state":"OPEN","warning":WARNING},{"hold_id":"R312-H03","hold":"R279-C02, structural convergence, H02, capacity and all work authority remain open.","state":"OPEN","warning":WARNING}]);manifest=[]
        for path in sorted(OUT.iterdir()):
            if path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",manifest)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0 if topology_pass else 2
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
