#!/usr/bin/env python3
"""Publish the controlled-stop evidence from the R306 discrete-mesh optimizer attempt."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-prereg-p0.1";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";ATTEMPT_GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_constrained_curving_mesh_p01.py";OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-constrained-curving-mesh-p0.1";IDENT="HR-V0-J2-C07-PE-CONSTRAINED-CURVING-MESH-P0.1";WARNING="PRELIMINARY - CONTROLLED-STOP CONSTRAINED CURVING ATTEMPT EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    protocol_path=PREREG/"frozen-constrained-curving-protocol.json";protocol=json.loads(protocol_path.read_text())
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    attempt={"attempt_id":"R306-ATTEMPT-01","candidate_id":protocol["candidate_id"],"command_argv_json":json.dumps([str(ROOT.parent/".venvs/hr-v0-cad/Scripts/python.exe"),"tools/generate_hr_v0_j2_c07_pe_constrained_curving_mesh_p01.py"],separators=(",",":")),"observed_start_utc":"2026-08-13T10:06:44Z","controlled_stop_utc":"2026-08-13T10:15:29.0609150Z","elapsed_wall_seconds_lower_bound":525,"last_observed_process_cpu_seconds":24.03125,"last_observed_working_set_bytes":1244221440,"last_observed_private_bytes":2271678464,"unchanged_observation_window_seconds_min":60,"optimizer":"HighOrder","force":False,"niter":1,"dim_tags":"C07-MATRIX volume only","result":"CONTROLLED STOP - NO NUMERICAL RESULT","stop_reason":"process CPU and memory counters remained exactly unchanged across the bounded observation interval; no result artifact was written","temporary_decompressed_mesh_removed":True,"source_r300_evidence_untouched":True,"warning":WARNING}
    write_csv(OUT/"attempt-register.csv",[attempt])
    status={"identifier":IDENT,"round":"R306","date":"2026-08-13","candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r300_status_sha256":sha(R300/"analysis-status.json"),"execution_started":True,"execution_completed":False,"controlled_stop":True,"numerical_result_available":False,"sampled_constrained_curving_candidate_pass":False,"exact_facet_revalidation_executed":False,"full_reference_domain_curved_jacobian_positive":False,"r279_c02_complete":False,"structural_solution_executed":False,"mesh_convergence_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n");(OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"publisher_sha256":sha(Path(__file__).resolve()),"attempt_generator_sha256":sha(ATTEMPT_GEN),"preregistration_sha256":sha(protocol_path),"r300_status_sha256":sha(R300/"analysis-status.json"),"r300_mesh_gzip_sha256":sha(R300/"c07-conformal-zone-mesh.msh.gz"),"warning":WARNING},indent=2)+"\n")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR306 attempted the single preregistered `HighOrder` operation on the retained discrete R300 mesh. The process produced no result and was stopped after its CPU and memory counters remained unchanged for at least 60 seconds. No alternate optimizer was substituted. Only the temporary decompressed copy was removed; R300 remains intact. The route is rejected for this toolchain.\n")
    write_csv(OUT/"open-holds.csv",[{"hold_id":"R306-H01","hold":"Move any successor high-order operation into the live OCC/CAD-resident meshing pipeline under a new preregistered candidate.","state":"OPEN","warning":WARNING},{"hold_id":"R306-H02","hold":"All exact facet, full-domain, R279-C02, structural, convergence, capacity and physical gates remain open.","state":"OPEN","warning":WARNING}])
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
