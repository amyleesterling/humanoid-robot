#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-corrected-surface-imprint-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-corrected-surface-imprint-p0.1"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-corrected-surface-imprint-prereg-p0.1"
PREREG_RELEASE = ROOT / "release/hr-v0/j2-c07-pe-corrected-surface-imprint-prereg-p0.1"
EXECUTOR = ROOT / "tools/generate_hr_v0_j2_c07_pe_corrected_surface_imprint_p01.py"
R297 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1"
R311 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-trimmed-facet-audit-p0.1"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))

def fail(message: str) -> None:
    raise SystemExit(f"R312 check failed: {message}")

def verify_package(source: Path, mirror: Path, required: set[str]) -> None:
    if {p.name for p in source.iterdir()} != required or {p.name for p in mirror.iterdir()} != required:
        fail(f"file set {source.name}")
    manifest = rows(source / "file-manifest.csv")
    if {r["relative_path"] for r in manifest} != required - {"file-manifest.csv"}:
        fail(f"manifest set {source.name}")
    for row in manifest:
        path = source / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest {source.name}/{path.name}")
    for name in required:
        if sha(source / name) != sha(mirror / name):
            fail(f"mirror {source.name}/{name}")

def main() -> int:
    verify_package(PREREG, PREREG_RELEASE, {"README.md", "analysis-status.json", "exact-24-face-target-register.csv", "file-manifest.csv", "frozen-protocol.json"})
    required = {"README.md", "analysis-status.json", "c07-pe-corrected-surface-imprint-analysis-partition.brep", "exact-24-face-imprint-tools.brep", "exact-imprinted-face-register.csv", "execution-provenance.json", "file-manifest.csv", "open-holds.csv", "zone-equivalence-register.csv"}
    verify_package(OUT, RELEASE, required)
    protocol = json.loads((PREREG / "frozen-protocol.json").read_text())
    status = json.loads((OUT / "analysis-status.json").read_text())
    provenance = json.loads((OUT / "execution-provenance.json").read_text())
    targets = rows(OUT / "exact-imprinted-face-register.csv")
    zones = rows(OUT / "zone-equivalence-register.csv")
    if len(rows(PREREG / "exact-24-face-target-register.csv")) != 24 or protocol["exact_face_count"] != 24:
        fail("preregistered target count")
    if protocol["executor_sha256"] != sha(EXECUTOR) or status["preregistration_sha256"] != sha(PREREG / "frozen-protocol.json"):
        fail("preregistration identity")
    if provenance["executor_sha256"] != sha(EXECUTOR) or provenance["r311_status_sha256"] != sha(R311 / "analysis-status.json"):
        fail("execution provenance")
    if status["source_r297_analysis_brep_sha256"] != sha(R297 / "c07-pe-seam-free-analysis-partition.brep"):
        fail("R297 source")
    passed = [r for r in targets if r["exact_single_face_single_exterior_owner_gate"] == "PASS"]
    failed = [r for r in targets if r["exact_single_face_single_exterior_owner_gate"] == "FAIL"]
    if len(targets) != 24 or len(passed) != 8 or len(failed) != 16:
        fail("face result counts")
    if len(zones) != 21 or {r["one_to_one_gate"] for r in zones} != {"PASS"}:
        fail("zone mapping")
    if status["output_analysis_volumes"] != 21 or status["fused_pe_volume_count"] != 1 or not status["zone_one_to_one_mapping_complete"]:
        fail("topology counts")
    if status["maximum_zone_relative_volume_error"] > 1e-12 or status["total_material_relative_volume_error"] > 1e-12 or status["maximum_zone_bbox_delta_mm"] > 1e-9 or status["maximum_zone_center_of_mass_delta_mm"] > 1e-9:
        fail("equivalence limits")
    if status["exact_24_exterior_faces_present"] is not False or status["topology_acceptance_pass"] is not False:
        fail("rejection state")
    for key in ("mesh_executed", "exact_facet_revalidation_pass", "r279_c02_complete", "structural_solution_executed", "r278_h02_closed", "capacity_credit", "selected", "safety_credit", "work_authority", "energization_authorized"):
        if status[key] is not False:
            fail(f"authority {key}")
    print("PASS: R312 synchronized; 21/21 volumes and fused PE preserve geometry, but only 8/24 exact faces remain one-face/one-owner; candidate rejected; no mesh, capacity, or work authority")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
