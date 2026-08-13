#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
import gmsh
import generate_hr_v0_j2_c07_target_feature_identity_p01 as feature
ROOT=Path(__file__).resolve().parents[1];R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R311=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-p0.1";STEP=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step";EXEC=ROOT/"tools/generate_hr_v0_j2_c07_pe_corrected_surface_imprint_p01.py";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-corrected-surface-imprint-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-corrected-surface-imprint-prereg-p0.1";IDENT="HR-V0-J2-C07-PE-CORRECTED-SURFACE-IMPRINT-PREREG-P0.1";WARNING="PRELIMINARY - CORRECTED 24-FACE ANALYSIS-SURFACE IMPRINT PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
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
    failures=rows(R311/"failed-trimmed-facet-register.csv");expected={signature for row in rows(R311/"failure-cluster-summary.csv") for signature in json.loads(row["face_signatures_sha256_json"])}
    if len(failures)!=247 or len(expected)!=24:raise RuntimeError("R311 corrected set")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        gmsh.model.add("R312_PREREG_FACE_IDENTITY");gmsh.model.occ.importShapes(str(STEP));gmsh.model.occ.synchronize();face_rows=[];curve_sigs=set()
        for _d,tag in gmsh.model.getEntities(2):
            signature,detail=feature.face_signature(tag)
            if signature not in expected:continue
            curves=[]
            for dim,curve in gmsh.model.getBoundary([(2,tag)],combined=False,oriented=False):
                if dim==1:
                    csig,cdetail=feature.curve_signature(curve);curve_sigs.add(csig);curves.append(csig)
            face_rows.append({"exact_face_signature_sha256":signature,"occ_face_tag_diagnostic_only":tag,"geometry_type":detail["geometry_type"],"bbox_mm_json":json.dumps(detail["bbox_mm"],separators=(",",":")),"area_mm2":detail["measure_mm_or_mm2"],"owner_boundary_curve_signatures_sha256_json":json.dumps(sorted(set(curves)),separators=(",",":")),"warning":WARNING})
        if len(face_rows)!=24 or {row["exact_face_signature_sha256"] for row in face_rows}!=expected:raise RuntimeError("exact face identity")
        write_csv(OUT/"exact-24-face-target-register.csv",sorted(face_rows,key=lambda row:row["exact_face_signature_sha256"]))
        protocol={"identifier":IDENT,"round":"R312-PREREG","date":"2026-08-13","candidate_id":"R312-C07-R297-CORRECTED-24-FACE-SURFACE-IMPRINT-V01","source_step_sha256":sha(STEP),"source_r297_analysis_brep_sha256":sha(R297/"c07-pe-seam-free-analysis-partition.brep"),"source_r297_fragment_register_sha256":sha(R297/"analysis-fragment-register.csv"),"source_r311_status_sha256":sha(R311/"analysis-status.json"),"executor_sha256":sha(EXEC),"exact_face_count":24,"unique_owner_boundary_curve_signatures":len(curve_sigs),"exact_face_signatures_sha256":sorted(expected),"operation":"Gmsh OCC fragment all 21 R297 volumes as objects with the isolated 24 exact STEP faces as surface tools; remove objects/tools; no other CAD operation","acceptance":{"output_analysis_volumes":21,"zone_one_to_one_mapping":True,"maximum_zone_relative_volume_error":1e-12,"total_material_relative_volume_error":1e-12,"maximum_zone_bbox_delta_mm":1e-9,"maximum_zone_center_of_mass_delta_mm":1e-9,"fused_pe_volume_count":1,"exact_24_faces_each_present_once_with_one_exterior_owner":True},"stop_rule":"one topology execution only; no alternate Boolean, tolerance, healing or target tuning","topology_execution_complete":False,"mesh_executed":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"work_authority":False,"warning":WARNING};(OUT/"frozen-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"analysis-status.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR312 freezes one corrected surface-imprint operation using all 24 exact STEP faces implicated by the R311 trimmed-face audit. The earlier R310 seven-plane candidate is rejected. No Boolean or mesh has executed.\n");manifest=[]
        for path in sorted(OUT.iterdir()):
            if path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
        write_csv(OUT/"file-manifest.csv",manifest)
        if RELEASE.exists():shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(protocol,indent=2));return 0
    finally:gmsh.finalize()
if __name__=="__main__":raise SystemExit(main())
