#!/usr/bin/env python3
"""Check the R297 seam-free PE analysis partition."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import gmsh
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-partition-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_partition_p01.py";R288=ROOT/"mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1/c07-exact-zone-fragmented.brep"
WARNING="PRELIMINARY - SEAM-FREE PE ANALYSIS PARTITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R297 seam-free partition check failed: {m}")
def rows(name:str)->list[dict[str,str]]:
    with (OUT/name).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def mass(path:Path)->tuple[int,float]:
    gmsh.clear();gmsh.model.add(path.stem);gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();vols=gmsh.model.getEntities(3);return len(vols),sum(float(gmsh.model.occ.getMass(3,t)) for d,t in vols)
def main()->int:
    required={"README.md","analysis-fragment-register.csv","analysis-status.json","analysis-zone-register.csv","c07-pe-eight-subzone-classification.brep","c07-pe-seam-free-analysis-partition.brep","execution-provenance.json","file-manifest.csv","retained-pe-subzone-classification-register.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest membership")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]) or r["warning"]!=WARNING:fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));prov=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if prov["generator_sha256"]!=sha(GEN) or st["source_r288_brep_sha256"]!=sha(R288) or st["brep_sha256"]!=sha(OUT/"c07-pe-seam-free-analysis-partition.brep"):fail("provenance")
    analysis=rows("analysis-fragment-register.csv");zones=rows("analysis-zone-register.csv");classrows=rows("retained-pe-subzone-classification-register.csv")
    if len(analysis)!=21 or len(zones)!=21 or sum(r["zone_id"]=="C07-PE-FUSED" for r in analysis)!=1:fail("analysis register")
    if len(classrows)!=8 or any(r["subset_of"]!="C07-PE-FUSED" for r in classrows):fail("classification register")
    gmsh.initialize(["-nopopup"]);gmsh.option.setNumber("General.Terminal",0)
    try:
        source_count,source_mass=mass(R288);analysis_count,analysis_mass=mass(OUT/"c07-pe-seam-free-analysis-partition.brep");class_count,class_mass=mass(OUT/"c07-pe-eight-subzone-classification.brep")
    finally:gmsh.finalize()
    if source_count!=28 or analysis_count!=21 or class_count!=8:fail("B-Rep counts")
    if abs(source_mass-analysis_mass)/source_mass>1e-10:fail("total material closure")
    registered_pe=sum(float(r["exact_material_volume_mm3"]) for r in classrows)
    if abs(class_mass-registered_pe)/registered_pe>1e-10:fail("classification volume closure")
    if st["authoritative_physical_geometry_changed"] or not st["internal_tangent_pe_seams_removed"] or not st["conformal_shared_interface_refragmented"] or st["maximum_one_to_one_mapping_relative_volume_error"]>1e-10:fail("scope state")
    for key in ("mesh_generated","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if st[key] is not False:fail(f"fail-closed {key}")
    print(f"PASS: R297 seam-free analysis partition; source={source_count} volumes, analysis={analysis_count}, classification={class_count}; physical material volume unchanged; mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
