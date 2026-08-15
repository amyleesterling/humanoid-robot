#!/usr/bin/env python3
"""Disposition R295 and freeze the seam-free PE analysis-partition boundary."""
from __future__ import annotations
import csv, hashlib, json, shutil
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
R289=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
R291=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
R293=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
R295=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-mesh-p0.1"
R288=ROOT/"mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-disposition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-frontal-disposition-p0.1"
IDENT="HR-V0-J2-C07-PE-FRONTAL-DISPOSITION-P0.1"
WARNING="PRELIMINARY - FRONTAL TETRAHEDRALIZATION DISPOSITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(path:Path)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def write_csv(path:Path,data:list[dict[str,object]])->None:
    fields=[]
    for row in data:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as s:
        w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    statuses={name:json.loads((path/"analysis-status.json").read_text(encoding="utf-8")) for name,path in (("R289",R289),("R291",R291),("R293",R293),("R295",R295))}
    if statuses["R295"]["r279_c02_complete"] or statuses["R295"]["actual_quadrature_signed_jacobian_gate"] is not True:raise RuntimeError("R295 disposition state drift")
    summaries={name:{r["zone_id"]:r for r in rows(path/"zone-quality-summary.csv")} for name,path in (("R289",R289),("R291",R291),("R293",R293),("R295",R295))}
    pe_ids=[r["zone_id"] for r in rows(R288/"exact-zone-register.csv") if r["family"]=="C07-PE"]
    straight=[z for z in pe_ids if z.endswith("STRAIGHT")];corners=[z for z in pe_ids if z.endswith("R2")]
    if len(straight)!=4 or len(corners)!=4:raise RuntimeError("R288 PE subzone identity drift")
    for run in summaries:
        if any(summaries[run][z]["monitored_min_0p20_gate"]!="FAIL" for z in straight):raise RuntimeError(f"{run} straight failure pattern drift")
    if any(summaries["R295"][z]["monitored_min_0p20_gate"]!="PASS" for z in corners):raise RuntimeError("R295 R2 pass pattern drift")
    raw=np.load(R295/"raw-conformal-zone-mesh.npz");low=int(np.count_nonzero(raw["linear_sicn"]<.20))
    comparison=[]
    for run in ("R289","R291","R293","R295"):
        st=statuses[run]
        comparison.append({"run":run,"tetrahedra":st["linear_tetrahedra"],"global_minimum_sicn":st["global_sicn_minimum"],"cells_below_0p20":round(st["global_sicn_fraction_below_0p20"]*st["linear_tetrahedra"]),"failed_straight_zones":sum(summaries[run][z]["monitored_min_0p20_gate"]=="FAIL" for z in straight),"failed_r2_zones":sum(summaries[run][z]["monitored_min_0p20_gate"]=="FAIL" for z in corners),"actual_quadrature_jacobian_gate":st["actual_quadrature_signed_jacobian_gate"],"r279_c02":st["r279_c02_complete"],"warning":WARNING})
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT/"r289-r295-method-comparison.csv",comparison)
    write_csv(OUT/"pe-subzone-disposition.csv",[{"zone_id":z,"kind":"STRAIGHT" if z in straight else "R2","r289_minimum_sicn":summaries["R289"][z]["minimum_sicn"],"r291_minimum_sicn":summaries["R291"][z]["minimum_sicn"],"r293_minimum_sicn":summaries["R293"][z]["minimum_sicn"],"r295_minimum_sicn":summaries["R295"][z]["minimum_sicn"],"r295_gate":summaries["R295"][z]["monitored_min_0p20_gate"],"interpretation":"TANGENT INTERNAL SEAM ARTIFACT" if z in straight else "CURVED SUBZONE ITSELF MESHES CLEANLY","warning":WARNING} for z in sorted(pe_ids)])
    boundary={
        "identifier":IDENT,"round":"R296","date":"2026-08-13","r295_rejected":True,
        "evidence":"Delaunay, Delaunay+Relocate3D, and Frontal all retain four straight-zone minima near 0.094-0.098 while every R2 subzone passes; Frontal makes all non-PE zones pass",
        "required_next_analysis_partition":"preserve authoritative P0.13 C07 physical solid exactly; fuse only the eight internal R288 C07-PE analysis fragments into one seam-free exact perimeter-band material volume; retain the eight exact subzone solids and their volumes as classification definitions; all other 19 primary exact zones remain conformal material volumes",
        "conservative_quality_rule":"require minimum SICN >=0.20 for every tetrahedron in the fused exact PE band; because all eight retained PE subzones are exact subsets of that band, this proves the same cell-quality floor for every subzone without centroid classification or tangent internal seams",
        "physical_geometry_changed":False,"analysis_partition_internal_seams_changed":True,
        "mesh_algorithm":"Algorithm3D=4 Frontal followed by Netgen; no relocation; no high-order optimizer",
        "mesh_size_fields":"R291 exact face and PE refinements retained; no threshold changes",
        "stop_rule":"generate and validate the seam-free exact analysis partition before meshing; then execute one preregistered mesh only",
        "next_partition_executed":False,"next_mesh_executed":False,"structural_solution_executed":False,
        "r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING,
    }
    (OUT/"next-partition-boundary.json").write_text(json.dumps(boundary,indent=2)+"\n",encoding="utf-8")
    status={"identifier":IDENT,"round":"R296","r295_rejected":True,"r295_low_sicn_cells":low,"algorithm_invariant_straight_zone_failure":True,"r2_subzones_all_pass_r295":True,"non_pe_zones_all_pass_r295":True,"next_partition_executed":False,"next_mesh_executed":False,"structural_solution_executed":False,"r279_c02_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"generator_sha256":sha(Path(__file__).resolve()),"r288_zone_register_sha256":sha(R288/"exact-zone-register.csv"),"r289_status_sha256":sha(R289/"analysis-status.json"),"r291_status_sha256":sha(R291/"analysis-status.json"),"r293_status_sha256":sha(R293/"analysis-status.json"),"r295_status_sha256":sha(R295/"analysis-status.json"),"r295_raw_sha256":sha(R295/"raw-conformal-zone-mesh.npz"),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR296 rejects R295. Three linear-mesh methods leave the same four PE straight-zone defects, while every R2 subzone and every non-PE R295 zone passes. This is evidence that the four tangent internal analysis seams—not the authoritative part—force the low-quality cells.\n\nThe next partition removes only those internal analysis seams by representing the exact PE band as one fused material volume. Eight exact straight/corner solids remain retained classification subsets. Requiring every fused-band cell to meet SICN 0.20 conservatively proves the same floor for each subset. No physical CAD, requirement threshold, structural result, capacity conclusion, or work authority changes.\n",encoding="utf-8")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
