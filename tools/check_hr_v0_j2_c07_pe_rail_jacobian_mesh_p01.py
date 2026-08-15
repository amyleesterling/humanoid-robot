#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from hr_v0_mesh_raw_shards import load_shards

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-rail-jacobian-mesh-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_rail_jacobian_mesh_p01.py"
PRIOR = ROOT / "tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py"
BASE = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
SHARD_HELPER = ROOT / "tools/hr_v0_mesh_raw_shards.py"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-prereg-p0.1"
BORE_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-prereg-p0.1"
R300 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R303 mesh check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {
        "README.md",
        "actual-quadrature-jacobian-register.csv",
        "analysis-status.json",
        "bore-wall-field-resolution.csv",
        "c07-conformal-zone-mesh.msh.gz",
        "execution-provenance.json",
        "file-manifest.csv",
        "frozen-rail-jacobian-protocol.json",
        "open-holds.csv",
        "rail-transition-field-resolution.csv",
        "raw-linear-mesh.npz",
        "raw-tet10-mesh.npz",
        "retained-pe-subzone-quality-inference.csv",
        "seam-free-field-resolution.csv",
        "sicn-histogram.csv",
        "zone-quality-summary.csv",
        "zone-volume-integration.csv",
    }
    if {path.name for path in OUT.iterdir()} != required or {path.name for path in RELEASE.iterdir()} != required:
        fail("file set")
    manifest = rows("file-manifest.csv")
    if {row["relative_path"] for row in manifest} != required - {"file-manifest.csv"}:
        fail("manifest set")
    for row in manifest:
        path = OUT / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest {path.name}")
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"mirror {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    protocol_path = PREREG / "frozen-rail-jacobian-protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if status["candidate_id"] != protocol["candidate_id"] or status["preregistration_sha256"] != sha(protocol_path):
        fail("preregistration binding")
    if status["r300_current_status_sha256"] != sha(R300 / "analysis-status.json"):
        fail("R300 binding")
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator binding")
    if provenance["transitive_r298_generator_sha256"] != sha(PRIOR) or provenance["transitive_r289_generator_sha256"] != sha(BASE):
        fail("transitive generator binding")
    if provenance["raw_shard_helper_sha256"] != sha(SHARD_HELPER):
        fail("shard helper binding")
    if provenance["bore_target_register_sha256"] != sha(BORE_PREREG / "exact-bore-wall-target-register.csv"):
        fail("bore target binding")
    if provenance["rail_target_register_sha256"] != sha(PREREG / "exact-rail-transition-target-register.csv"):
        fail("rail target binding")
    bore = rows("bore-wall-field-resolution.csv")
    rail = rows("rail-transition-field-resolution.csv")
    if len(bore) != 4 or len(rail) != 2 or any(row["gate"] != "PASS" for row in bore + rail):
        fail("field resolution")
    if len({row["resolved_occ_tag_diagnostic_only"] for row in bore + rail}) != 6:
        fail("resolved targets not unique")

    if sha(OUT / "raw-linear-mesh.npz") != status["raw_linear_mesh_sha256"] or sha(OUT / "raw-tet10-mesh.npz") != status["raw_tet10_mesh_sha256"]:
        fail("raw shard hash")
    raw = load_shards(OUT)
    quality = raw["linear_sicn"]
    if len(quality) != status["linear_tetrahedra"] or abs(float(np.min(quality)) - status["global_sicn_minimum"]) > 1e-14:
        fail("raw quality")
    global_gate = float(np.min(quality)) >= 0.10 and float(np.mean(quality < 0.20)) <= 0.001
    summaries = rows("zone-quality-summary.csv")
    histogram = rows("sicn-histogram.csv")
    if len(summaries) != 21:
        fail("zone count")
    for summary in summaries:
        zone_rows = [
            row for row in histogram if row["scope"] == "EXACT_ZONE" and row["zone_id"] == summary["zone_id"]
        ]
        if len(zone_rows) != 10 or sum(int(row["count"]) for row in zone_rows) != int(summary["tetrahedra"]):
            fail(f"histogram {summary['zone_id']}")
    monitored = not any(
        row["zone_id"] != "C07-MATRIX" and row["monitored_min_0p20_gate"] != "PASS" for row in summaries
    )
    fused = [row for row in summaries if row["zone_id"] == "C07-PE-FUSED"]
    if len(fused) != 1:
        fail("fused PE summary")
    fused_gate = float(fused[0]["minimum_sicn"]) >= 0.20
    inference = rows("retained-pe-subzone-quality-inference.csv")
    if len(inference) != 8 or any((row["conservative_inference_gate"] == "PASS") != fused_gate for row in inference):
        fail("PE subzone inference")

    jacobian = rows("actual-quadrature-jacobian-register.csv")
    if {int(row["quadrature_order"]) for row in jacobian} != {4, 6, 8}:
        fail("Jacobian orders")
    if any(row["full_reference_domain_positivity"] != "UNVERIFIED" for row in jacobian):
        fail("Jacobian scope")
    jacobian_gate = all(
        int(row["wrong_or_zero_count"]) == 0 and int(row["normalized_floor_fail_count"]) == 0
        for row in jacobian
    )
    sampled_candidate = bool(global_gate and monitored and jacobian_gate)
    if (
        status["global_sicn_gate"] != global_gate
        or status["monitored_zone_minimum_gate"] != monitored
        or status["actual_quadrature_signed_jacobian_gate"] != jacobian_gate
        or status["sampled_mesh_quality_candidate_pass"] != sampled_candidate
        or status["fused_pe_quality_gate"] != fused_gate
    ):
        fail("gate derivation")
    if status["r279_c02_complete"] is not False or not status["r279_c02_completion_hold"]:
        fail("R279-C02 fail-closed boundary")

    digest = hashlib.sha256()
    byte_count = 0
    with gzip.open(OUT / "c07-conformal-zone-mesh.msh.gz", "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            byte_count += len(block)
    if digest.hexdigest() != status["mesh_uncompressed_sha256"] or byte_count != status["mesh_uncompressed_bytes"]:
        fail("compressed mesh")

    for key in (
        "full_reference_domain_curved_jacobian_positive",
        "structural_solution_executed",
        "mesh_convergence_complete",
        "r278_h02_closed",
        "capacity_credit",
        "selected",
        "safety_credit",
        "procurement_authorized",
        "fabrication_authorized",
        "assembly_authorized",
        "connection_authorized",
        "powered_testing_authorized",
        "motion_authorized",
        "energization_authorized",
    ):
        if status[key] is not False:
            fail(f"fail-closed {key}")

    print(
        "PASS: R303 synchronized; "
        f"tets={len(quality)} global={global_gate} monitored={monitored} jacobian={jacobian_gate} "
        f"sampled_candidate={sampled_candidate}; full-domain/R279-C02/structural/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
