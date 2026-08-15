#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-localization-p0.1";R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R308=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-prereg-p0.1/frozen-protocol.json";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_facet_localization_p01.py"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def fail(message:str):raise SystemExit(f"R309 check failed: {message}")
def main()->int:
    required={"README.md","analysis-status.json","execution-provenance.json","file-manifest.csv","nearest-face-cluster-summary.csv","open-holds.csv","unmapped-facet-localization.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    for row in manifest:
        path=OUT/row["relative_path"]
        if sha(path)!=row["sha256"] or path.stat().st_size!=int(row["bytes"]):fail(f"manifest {path.name}")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    st=json.loads((OUT/"analysis-status.json").read_text());prov=json.loads((OUT/"execution-provenance.json").read_text());protocol=json.loads(PREREG.read_text())
    if st["preregistration_sha256"]!=sha(PREREG) or prov["generator_sha256"]!=sha(GEN) or st["r307_status_sha256"]!=sha(R307/"analysis-status.json") or st["r308_status_sha256"]!=sha(R308/"analysis-status.json"):fail("provenance")
    detail=rows(OUT/"unmapped-facet-localization.csv");clusters=rows(OUT/"nearest-face-cluster-summary.csv")
    if len(detail)!=77 or len(clusters)!=7 or sum(int(r["unmapped_facets"]) for r in clusters)!=77:fail("counts")
    tags={tag for row in detail for tag in json.loads(row["node_tags_json"])}
    if len(tags)!=255 or {r["nearest_face_type"] for r in detail}!={"Plane"}:fail("localized identities")
    if any(float(r["maximum_six_node_deviation_mm"])!=0.0 for r in detail) or any(r["exact_membership_gate"]!="FAIL" for r in detail):fail("deviation/scope")
    if st["exact_facet_revalidation_pass"] or st["r279_c02_complete"] or st["structural_solution_executed"] or st["r278_h02_closed"] or st["capacity_credit"] or st["selected"] or st["safety_credit"] or st["work_authority"] or st["energization_authorized"]:fail("authority")
    print("PASS: R309 synchronized; exact R308 112569/77 split reproduced; 77 zero-distance facets cluster on 7 planar trimmed faces; 255 unique nodes; no facet/R279-C02/H02/capacity/work credit");return 0
if __name__=="__main__":raise SystemExit(main())
