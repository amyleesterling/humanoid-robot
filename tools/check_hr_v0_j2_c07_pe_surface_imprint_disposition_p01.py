#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-surface-imprint-disposition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-surface-imprint-disposition-p0.1";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R309=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-localization-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_surface_imprint_disposition_p01.py"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def fail(message:str):raise SystemExit(f"R310 check failed: {message}")
def main()->int:
    required={"README.md","affected-node-comparison.csv","analysis-status.json","exact-face-cluster-register.csv","execution-provenance.json","file-manifest.csv","frozen-surface-imprint-protocol.json","open-holds.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for row in manifest:
        path=OUT/row["relative_path"]
        if sha(path)!=row["sha256"] or path.stat().st_size!=int(row["bytes"]):fail(f"manifest {path.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    st=json.loads((OUT/"analysis-status.json").read_text());prov=json.loads((OUT/"execution-provenance.json").read_text());comparison=rows(OUT/"affected-node-comparison.csv")[0];clusters=rows(OUT/"exact-face-cluster-register.csv")
    if prov["generator_sha256"]!=sha(GEN) or st["source_r300_status_sha256"]!=sha(R300/"analysis-status.json") or st["source_r307_status_sha256"]!=sha(R307/"analysis-status.json") or st["source_r309_status_sha256"]!=sha(R309/"analysis-status.json"):fail("provenance")
    if int(comparison["unique_affected_nodes"])!=255 or float(comparison["r300_r307_coordinate_max_delta_mm"])!=0 or comparison["all_coordinates_exact"]!="True" or len(clusters)!=7 or sum(int(r["unmapped_facets"]) for r in clusters)!=77:fail("disposition evidence")
    if st["topology_execution_complete"] or st["mesh_executed"] or st["exact_facet_revalidation_pass"] or st["r279_c02_complete"] or st["structural_solution_executed"] or st["r278_h02_closed"] or st["capacity_credit"] or st["selected"] or st["safety_credit"] or st["work_authority"]:fail("authority")
    print("PASS: R310 synchronized; all 255 affected nodes identical R300/R307; coordinate restoration rejected; seven-face exterior-imprint candidate preregistered but unexecuted; all downstream authority open");return 0
if __name__=="__main__":raise SystemExit(main())
