#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";R309=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";R310=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-surface-imprint-disposition-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_trimmed_facet_audit_p01.py";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-trimmed-facet-audit-prereg-p0.1";IDENT="HR-V0-J2-C07-PE-TRIMMED-FACET-AUDIT-PREREG-P0.1";WARNING="PRELIMINARY - CORRECTED EXACT TRIMMED-FACE AUDIT PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True);protocol={"identifier":IDENT,"round":"R311-PREREG","date":"2026-08-13","candidate_id":"R311-C07-R307-CORRECTED-TRIMMED-FACET-AUDIT-V01","r307_status_sha256":sha(R307/"analysis-status.json"),"r308_status_sha256":sha(R308/"analysis-status.json"),"r309_status_sha256":sha(R309/"analysis-status.json"),"r310_status_sha256":sha(R310/"analysis-status.json"),"generator_sha256":sha(GEN),"boundary_scope":"every exterior R307 Tet10 facet and every one of its six nodes","underlying_surface_tolerance_mm":1e-7,"exact_trim_rule":"candidate membership requires distance <=1e-7 mm AND gmsh.model.isInside on the closest point; every facet requires one common exact trimmed face after interior-point disambiguation","execution":"one corrected audit; no mesh, geometry, optimizer, threshold or tolerance change","audit_executed":False,"exact_facet_revalidation_pass":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"work_authority":False,"warning":WARNING};(OUT/"frozen-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"analysis-status.json").write_text(json.dumps(protocol,indent=2)+"\n");(OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR311 preregisters a corrected exact trimmed-face audit after a read-only check disproved the R310 containment premise. No topology operation may execute until this full boundary audit is disposed.\n");write_csv(OUT/"file-manifest.csv",[{"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(OUT.iterdir())]);
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(protocol,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
