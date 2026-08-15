#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_facet_localization_p01.py";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-localization-prereg-p0.1";IDENT="HR-V0-J2-C07-PE-CAD-CURVING-FACET-LOCALIZATION-PREREG-P0.1";WARNING="PRELIMINARY - R308 UNMAPPED-FACET LOCALIZATION PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    r308=json.loads((R308/"analysis-status.json").read_text())
    if r308["unmapped_facets"]!=77 or r308["exact_facet_revalidation_pass"]:raise RuntimeError("R308 source state")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);protocol={"identifier":IDENT,"round":"R309-PREREG","date":"2026-08-13","candidate_id":"R309-C07-R308-UNMAPPED-FACET-LOCALIZATION-V01","r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"r308_status_sha256":sha(R308/"analysis-status.json"),"generator_sha256":sha(GEN),"expected_exterior_facets":112646,"expected_uniquely_mapped_facets":112569,"expected_unmapped_facets":77,"node_face_membership_tolerance_mm":1e-7,"nearest_face_search_envelope_mm":0.05,"execution":"one diagnostic localization; no mesh, CAD, optimizer, threshold or membership-tolerance change","localization_executed":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"work_authority":False,"warning":WARNING};(OUT/"frozen-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"analysis-status.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR309 freezes one diagnostic reproduction and nearest-exact-face localization of the 77 R308 failures. It cannot relax the membership tolerance or alter the mesh.\n")
    write_csv(OUT/"file-manifest.csv",[{"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(OUT.iterdir())]);
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(protocol,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
