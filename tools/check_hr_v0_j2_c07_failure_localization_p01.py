#!/usr/bin/env python3
"""Fail-closed checks for the R284 C07 failure-localization package."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1";RELEASE_OUT=ROOT/"release/hr-v0/j2-c07-failure-localization-p0.1";SOURCE=ROOT/"mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
def need(x,m):
    if not x:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    status=json.loads((OUT/"analysis-status.json").read_text());need(status["identifier"]=="HR-V0-J2-C07-FAILURE-LOCALIZATION-P0.1","identity")
    for key in ("remeshing_executed","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","work_authority"):need(status[key] is False,key)
    summary={r["screen_id"]:r for r in rows(OUT/"variant-localization-summary.csv")};need(set(summary)=={"R284-V03-REFINED","R284-V06-FINE","R284-V08-ULTRAFINE"},"variants")
    need(int(summary["R284-V03-REFINED"]["unique_failed_elements"])>0,"V03 failures");need(int(summary["R284-V08-ULTRAFINE"]["unique_failed_elements"])>0,"V08 failures");need(int(summary["R284-V06-FINE"]["unique_failed_elements"])==0,"V06 comparator")
    failed=rows(OUT/"failed-element-localization.csv");need(len(failed)==sum(int(summary[x]["unique_failed_elements"]) for x in summary),"failure count")
    need(all(int(r["element_tag"])>0 and float(r["worst_normalized_determinant"])<=0 for r in failed),"failed identities")
    need(all(float(r["corner_edge_min_mm"])>0 and float(r["corner_edge_max_mm"])>=float(r["corner_edge_min_mm"]) for r in failed),"mesh size")
    need(all(int(r["nearest_occ_edge_tag"])>0 and int(r["nearest_occ_face_tag"])>0 for r in failed),"OCC localization")
    zones={}
    for r in failed:zones[r["coordinate_diagnostic_zone"]]=zones.get(r["coordinate_diagnostic_zone"],0)+1
    need(zones.get("BACKSIDE_MOUNTING_BOSS_CYLINDER")==8 and zones.get("HOLES")==2,"V03 cylinder cluster")
    need(zones.get("NEGATIVE_X_RAIL_TOP_TRANSITION")==2,"cross-level rail cluster")
    recommendation=json.loads((OUT/"actionable-meshing-correction.json").read_text());need(recommendation["h02_closed"] is False and "V06 size triplet" in recommendation["action"],"recommendation boundary")
    provenance=json.loads((OUT/"execution-provenance.json").read_text());need(provenance["generator_sha256"]==sha(ROOT/"tools/generate_hr_v0_j2_c07_failure_localization_p01.py"),"generator provenance")
    need(provenance["source_package"]==SOURCE.relative_to(ROOT).as_posix(),"source package binding")
    expected_evidence={
        "variant-summary.csv":SOURCE/"variant-summary.csv",
        "r284-v03-refined/analysis-status.json":SOURCE/"r284-v03-refined/analysis-status.json",
        "r284-v03-refined/file-manifest.csv":SOURCE/"r284-v03-refined/file-manifest.csv",
        "r284-v06-fine/analysis-status.json":SOURCE/"r284-v06-fine/analysis-status.json",
        "r284-v06-fine/file-manifest.csv":SOURCE/"r284-v06-fine/file-manifest.csv",
        "r284-v08-ultrafine/analysis-status.json":SOURCE/"r284-v08-ultrafine/analysis-status.json",
        "r284-v08-ultrafine/file-manifest.csv":SOURCE/"r284-v08-ultrafine/file-manifest.csv",
    }
    need(provenance["source_evidence_sha256"]=={name:sha(path) for name,path in expected_evidence.items()},"nested source evidence binding")
    expected_npz={"R284-V03-REFINED":SOURCE/"r284-v03-refined/raw-r284_v03_refined_fixed.npz","R284-V06-FINE":SOURCE/"r284-v06-fine/raw-r284_v06_fine_fixed.npz","R284-V08-ULTRAFINE":SOURCE/"r284-v08-ultrafine/raw-r284_v08_ultrafine_fixed.npz"}
    need(provenance["source_npz_path"]=={screen:path.relative_to(ROOT).as_posix() for screen,path in expected_npz.items()},"source-owned NPZ paths")
    for screen,relative in provenance["source_npz_path"].items():
        path=(ROOT/relative).resolve();need(path.is_relative_to(SOURCE.resolve()) and path.is_file(),f"source path {screen}");need(provenance["source_npz_sha256"][screen]==sha(path),f"source {screen}")
    manifest=rows(OUT/"file-manifest.csv");actual=[p for p in OUT.iterdir() if p.is_file() and p.name!="file-manifest.csv"];need(len(manifest)==len(actual),"manifest count");mapped={r["relative_path"]:r for r in manifest}
    for p in actual:need(mapped[p.name]["sha256"]==sha(p) and int(mapped[p.name]["bytes"])==p.stat().st_size,f"manifest {p.name}")
    need(RELEASE_OUT.is_dir(),"release mirror missing");release=[p for p in RELEASE_OUT.iterdir() if p.is_file()]
    need({p.name for p in release}=={p.name for p in OUT.iterdir() if p.is_file()},"release file set")
    for p in OUT.iterdir():
        if p.is_file():need(sha(p)==sha(RELEASE_OUT/p.name),f"release hash {p.name}")
    print("PASS: R284 failed curved elements localized; V06 comparator clean; remeshing, convergence, H02 and authority remain open")
if __name__=="__main__":main()
