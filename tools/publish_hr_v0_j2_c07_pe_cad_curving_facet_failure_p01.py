#!/usr/bin/env python3
"""Publish the fail-closed R308 exact-facet evaluation result."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-prereg-p0.1";WRAPPER=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_facet_p01.py";EVALUATOR=ROOT/"tools/generate_hr_v0_j2_c07_brep_facet_load_p01.py"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-p0.1";IDENT="HR-V0-J2-C07-PE-CAD-CURVING-FACET-P0.1";WARNING="PRELIMINARY - FAILED R307 EXACT FACET/B-REP/LOAD REVALIDATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    protocol_path=PREREG/"frozen-protocol.json";protocol=json.loads(protocol_path.read_text(encoding="utf-8"))
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    attempt={"attempt_id":"R308-ATTEMPT-01","candidate_id":protocol["candidate_id"],"result":"FAIL CLOSED - EXACT FACET MAP INCOMPLETE","exterior_facets":112646,"uniquely_mapped_facets":112569,"unmapped_facets":77,"multiply_mapped_facets":0,"candidate_count_distribution_json":json.dumps({"0":77,"1":112569},separators=(",",":")),"exception":"RuntimeError: exact facet map fail-closed: 77 exterior facets lack one exact OCC face; candidate-count distribution={0: 77, 1: 112569}; ambiguous pairs={(): 77}","mesh_or_threshold_tuning_performed":False,"r307_source_untouched":True,"warning":WARNING}
    write_csv(OUT/"attempt-register.csv",[attempt])
    status={"identifier":IDENT,"round":"R308","date":"2026-08-13","candidate_id":protocol["candidate_id"],"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"evaluation_executed":True,"evaluation_completed":False,"exact_facet_revalidation_executed":True,"exact_facet_map_complete":False,"exact_facet_revalidation_pass":False,"exterior_facets":112646,"uniquely_mapped_facets":112569,"unmapped_facets":77,"sampled_r307_candidate_pass":True,"r279_c02_complete":False,"structural_solution_executed":False,"mesh_convergence_complete":False,"r278_h02_closed":False,"capacity_credit":False,"selected":False,"safety_credit":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"execution-provenance.json").write_text(json.dumps({"identifier":IDENT,"publisher_sha256":sha(Path(__file__).resolve()),"wrapper_sha256":sha(WRAPPER),"transitive_evaluator_sha256":sha(EVALUATOR),"preregistration_sha256":sha(protocol_path),"r307_status_sha256":sha(R307/"analysis-status.json"),"r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nThe one frozen R308 evaluation stopped fail-closed before area/load credit: 112,569 of 112,646 exterior R307 quadratic facets mapped uniquely to an exact OCC face, while 77 mapped to none. No threshold, geometry, mesh or optimizer setting was changed. R307 remains valid only as bounded sampled Jacobian evidence. R279-C02, structural execution, H02, capacity, physical validation and every work authority remain open.\n",encoding="utf-8")
    write_csv(OUT/"open-holds.csv",[{"hold_id":"R308-H01","hold":"Preregister and execute localization of all 77 unmapped exterior facets without relaxing the exact-face tolerance.","state":"OPEN","warning":WARNING},{"hold_id":"R308-H02","hold":"Revalidate exact surface deviation, every face area and load geometry only under a new frozen successor after localization.","state":"OPEN","warning":WARNING},{"hold_id":"R308-H03","hold":"Full-domain positivity, R279-C02, structural convergence, H02, capacity and every work authority remain open.","state":"OPEN","warning":WARNING}])
    manifest=[]
    for path in sorted(OUT.iterdir()):
        if path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
