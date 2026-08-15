#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-failure-localization-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-failure-localization-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_failure_localization_p01.py";R298=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1"
WARNING="PRELIMINARY - SEAM-FREE MESH FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R299 localization check failed: {m}")
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","curved-jacobian-failure-localization.csv","execution-provenance.json","file-manifest.csv","global-low-sicn-localization.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    for r in rows("file-manifest.csv"):
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));prov=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"));jac=rows("curved-jacobian-failure-localization.csv");low=rows("global-low-sicn-localization.csv")
    r298_provenance=json.loads((R298/"execution-provenance.json").read_text(encoding="utf-8"))
    if prov["generator_sha256"]!=sha(GEN) or prov["r298_status_sha256"]!=r298_provenance["pre_raw_shard_migration_status_sha256"]:fail("provenance")
    if len(low)!=st["global_low_sicn_cells"] or len(jac)!=st["curved_failed_order_qp_pairs"] or len({r["element_tag"] for r in jac})!=st["curved_unique_failed_elements"] or len({r["nearest_exact_face_signature_sha256"] for r in jac})!=st["nearest_exact_face_clusters"]:fail("count derivation")
    if {int(r["quadrature_order"]) for r in jac}!={4,6,8} or not all(float(r["determinant"])<=0 or float(r["normalized_determinant"])<=1e-10 for r in jac):fail("failure rows")
    for key in ("remesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if st[key] is not False:fail(f"fail-closed {key}")
    print(f"PASS: R299 localizes {len(jac)} curved failed QPs across {st['curved_unique_failed_elements']} element(s)/{st['nearest_exact_face_clusters']} exact face(s); mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
