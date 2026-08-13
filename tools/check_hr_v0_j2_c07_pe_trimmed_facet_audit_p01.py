#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-trimmed-facet-audit-p0.1";R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";R309=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";R310=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-surface-imprint-disposition-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-prereg-p0.1/frozen-protocol.json";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_trimmed_facet_audit_p01.py"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def fail(message:str):raise SystemExit(f"R311 check failed: {message}")
def main()->int:
    required={"README.md","analysis-status.json","execution-provenance.json","failed-trimmed-facet-register.csv","failure-cluster-summary.csv","file-manifest.csv","method-correction.json","open-holds.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for row in manifest:
        path=OUT/row["relative_path"]
        if sha(path)!=row["sha256"] or path.stat().st_size!=int(row["bytes"]):fail(f"manifest {path.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    st=json.loads((OUT/"analysis-status.json").read_text());prov=json.loads((OUT/"execution-provenance.json").read_text());correction=json.loads((OUT/"method-correction.json").read_text())
    if prov["generator_sha256"]!=sha(GEN) or st["preregistration_sha256"]!=sha(PREREG) or st["r307_status_sha256"]!=sha(R307/"analysis-status.json") or st["r308_status_sha256"]!=sha(R308/"analysis-status.json") or st["r309_status_sha256"]!=sha(R309/"analysis-status.json") or st["r310_status_sha256"]!=sha(R310/"analysis-status.json"):fail("provenance")
    failed=rows(OUT/"failed-trimmed-facet-register.csv");clusters=rows(OUT/"failure-cluster-summary.csv")
    if len(failed)!=247 or len(clusters)!=32 or sum(int(r["failed_facets"]) for r in clusters)!=247 or {r["classification"] for r in failed}!={"UNMAPPED"}:fail("failure evidence")
    face_tags={int(face) for row in failed for face in json.loads(row["union_exact_trimmed_face_tags_json"])}
    if len(face_tags)!=24 or st["uniquely_mapped_facets"]!=112399 or st["unmapped_facets"]!=247 or st["multiply_mapped_facets"]!=0 or st["underlying_hits_rejected_by_exact_trim"]!=5852:fail("corrected totals")
    if not all(correction.values()):fail("correction flags")
    for key in ("corrected_exact_trimmed_face_map_complete","exact_facet_revalidation_pass","r279_c02_complete","structural_solution_executed","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority","energization_authorized"):
        if st[key] is not False:fail(f"authority {key}")
    print("PASS: R311 synchronized; corrected exact-trim audit maps 112399/112646, leaves 247 unmapped in 32 clusters across 24 faces; R308-R310 mapping premise superseded; no downstream credit");return 0
if __name__=="__main__":raise SystemExit(main())
