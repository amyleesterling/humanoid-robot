#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-disposition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-conformal-successor-disposition-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_conformal_successor_disposition_p01.py";R291=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1";WARNING="PRELIMINARY - CONFORMAL SUCCESSOR DISPOSITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m):raise SystemExit(f"R292 disposition check failed: {m}")
def rows(n):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main():
    req={"README.md","analysis-status.json","execution-provenance.json","file-manifest.csv","index.html","next-method-boundary.json","r289-r291-comparison.csv","r291-low-sicn-localization.csv"}
    if {p.name for p in OUT.iterdir()}!=req or {p.name for p in RELEASE.iterdir()}!=req:fail("file set")
    man=rows("file-manifest.csv")
    for r in man:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or sha(p)!=sha(RELEASE/r["relative_path"]):fail(f"manifest/mirror {p}")
    st=json.loads((OUT/"analysis-status.json").read_text());low=rows("r291-low-sicn-localization.csv");bound=json.loads((OUT/"next-method-boundary.json").read_text())
    if len(low)!=19 or st["r291_low_sicn_elements"]!=19 or not st["r291_curved_jacobian_gate"]:fail("outcome count/state")
    if not st["pocket_refinement_method_rejected"] or "Relocate3D" not in bound["required_next_preregistration"]:fail("method boundary")
    for k in ("next_mesh_executed","r279_c02_complete","r278_h02_closed","capacity_credit","safety_credit","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if st[k] is not False:fail(f"authority {k}")
    prov=json.loads((OUT/"execution-provenance.json").read_text())
    if prov["generator_sha256"]!=sha(GEN) or prov["r291_status_sha256"]!=sha(R291/"analysis-status.json"):fail("provenance")
    guide=(OUT/"index.html").read_text()
    for token in ("font:16px/1.55","font-size:16px","overflow-x:auto","R279-C02",WARNING):
        if token not in guide:fail(f"guide token {token}")
    print("PASS: R292 disposition synchronized; Jacobians advanced, SICN method rejected; next mesh/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
