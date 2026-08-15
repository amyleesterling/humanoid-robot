#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-p0.1";R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-prereg-p0.1/frozen-protocol.json";WRAPPER=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_facet_p01.py";EVALUATOR=ROOT/"tools/generate_hr_v0_j2_c07_brep_facet_load_p01.py";PUBLISHER=ROOT/"tools/publish_hr_v0_j2_c07_pe_cad_curving_facet_failure_p01.py"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def fail(message:str):raise SystemExit(f"R308 failure check failed: {message}")
def main()->int:
    required={"README.md","analysis-status.json","attempt-register.csv","execution-provenance.json","file-manifest.csv","open-holds.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for row in manifest:
        path=OUT/row["relative_path"]
        if sha(path)!=row["sha256"] or path.stat().st_size!=int(row["bytes"]):fail(f"manifest {path.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    st=json.loads((OUT/"analysis-status.json").read_text());prov=json.loads((OUT/"execution-provenance.json").read_text());protocol=json.loads(PREREG.read_text())
    if st["candidate_id"]!=protocol["candidate_id"] or st["preregistration_sha256"]!=sha(PREREG):fail("protocol")
    if st["r307_status_sha256"]!=sha(R307/"analysis-status.json") or prov["publisher_sha256"]!=sha(PUBLISHER) or prov["wrapper_sha256"]!=sha(WRAPPER) or prov["transitive_evaluator_sha256"]!=sha(EVALUATOR):fail("provenance")
    attempt=rows(OUT/"attempt-register.csv")[0]
    if int(attempt["exterior_facets"])!=112646 or int(attempt["uniquely_mapped_facets"])!=112569 or int(attempt["unmapped_facets"])!=77 or int(attempt["multiply_mapped_facets"])!=0:fail("observed counts")
    if st["exact_facet_revalidation_executed"] is not True or st["exact_facet_map_complete"] is not False or st["exact_facet_revalidation_pass"] is not False:fail("disposition")
    for key in ("r279_c02_complete","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if st[key] is not False:fail(f"authority {key}")
    print("PASS: R308 fail-closed result synchronized; 112569/112646 facets mapped, 77 unmapped; R279-C02/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
