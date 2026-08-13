#!/usr/bin/env python3
"""Check the single preregistered R293 PE-junction mesh-method execution."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
from hr_v0_mesh_raw_shards import load_shards


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-mesh-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_topology_mesh_p01.py"
PRIOR_GEN = ROOT / "tools/generate_hr_v0_j2_c07_conformal_successor_mesh_p01.py"
BASE_GEN = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1/frozen-pe-topology-protocol.json"
R291_STATUS = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1/analysis-status.json"
WARNING = (
    "PRELIMINARY - PREREGISTERED PE-JUNCTION MESH-METHOD EVIDENCE ONLY - NOT "
    "APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, "
    "POWERED TESTING, MOTION, OR ENERGIZATION"
)
MIGRATION = ROOT / "tools/migrate_hr_v0_mesh_raw_to_shards_p01.py"
SHARD_HELPER = ROOT / "tools/hr_v0_mesh_raw_shards.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R293 PE topology mesh check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {
        "README.md", "actual-quadrature-jacobian-register.csv", "analysis-status.json",
        "c07-conformal-zone-mesh.msh.gz", "execution-provenance.json",
        "file-manifest.csv", "frozen-pe-topology-protocol.json",
        "method-baseline-register.csv", "method-execution-register.csv", "open-holds.csv",
        "raw-linear-mesh.npz", "raw-tet10-mesh.npz", "sicn-histogram.csv",
        "successor-field-resolution.csv", "zone-quality-summary.csv",
        "zone-volume-integration.csv",
    }
    if {path.name for path in OUT.iterdir()} != required:
        fail("source file set")
    if {path.name for path in RELEASE.iterdir()} != required:
        fail("release file set")
    manifest = rows("file-manifest.csv")
    if {row["relative_path"] for row in manifest} != required - {"file-manifest.csv"}:
        fail("manifest membership")
    for row in manifest:
        path = OUT / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest mismatch {path.name}")
        if row["warning"] != WARNING:
            fail(f"manifest warning {path.name}")
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"source/release mismatch {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    protocol = json.loads(PREREG.read_text(encoding="utf-8"))
    if status["identifier"] != "HR-V0-J2-C07-PE-TOPOLOGY-MESH-P0.1" or status["round"] != "R293":
        fail("identity")
    if status["candidate_id"] != protocol["candidate_id"]:
        fail("candidate binding")
    if status["preregistration_sha256"] != sha(PREREG):
        fail("preregistration binding")
    if status["r291_baseline_status_sha256"] != sha(R291_STATUS):
        fail("R291 baseline binding")
    if status["linear_optimizer_sequence"] != ["Netgen", "Relocate3D"]:
        fail("status optimizer sequence")
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator binding")
    if provenance["transitive_r291_generator_sha256"] != sha(PRIOR_GEN):
        fail("R291 generator binding")
    if provenance["transitive_r289_generator_sha256"] != sha(BASE_GEN):
        fail("R289 generator binding")
    if provenance["linear_optimizer_sequence"] != ["Netgen", "Relocate3D"]:
        fail("provenance optimizer sequence")
    if provenance["raw_shard_migration_generator_sha256"] != sha(MIGRATION) or provenance["raw_shard_helper_sha256"] != sha(SHARD_HELPER):
        fail("raw shard provenance")
    method = rows("method-execution-register.csv")
    if len(method) != 1 or method[0]["stage_1"] != "Netgen" or method[0]["stage_2"] != "Relocate3D":
        fail("method execution record")

    raw = load_shards(OUT)
    sicn = raw["linear_sicn"]
    if len(sicn) != status["linear_tetrahedra"]:
        fail("raw tetrahedron count")
    if abs(float(np.min(sicn)) - status["global_sicn_minimum"]) > 1.0e-14:
        fail("raw SICN minimum")
    if abs(float(np.mean(sicn < 0.20)) - status["global_sicn_fraction_below_0p20"]) > 1.0e-14:
        fail("raw SICN fraction")
    derived_global = float(np.min(sicn)) >= 0.10 and float(np.mean(sicn < 0.20)) <= 0.001
    if status["global_sicn_gate"] != derived_global:
        fail("global gate derivation")
    summaries = rows("zone-quality-summary.csv")
    hist = rows("sicn-histogram.csv")
    if len(summaries) != 28 or len({row["zone_id"] for row in summaries}) != 28:
        fail("zone summary set")
    for summary in summaries:
        zone_hist = [row for row in hist if row["scope"] == "EXACT_ZONE" and row["zone_id"] == summary["zone_id"]]
        if len(zone_hist) != 10 or sum(int(row["count"]) for row in zone_hist) != int(summary["tetrahedra"]):
            fail(f"zone histogram {summary['zone_id']}")
    derived_monitored = not any(
        row["zone_id"] != "C07-MATRIX" and row["monitored_min_0p20_gate"] != "PASS"
        for row in summaries
    )
    if status["monitored_zone_minimum_gate"] != derived_monitored:
        fail("monitored-zone derivation")
    jac = rows("actual-quadrature-jacobian-register.csv")
    if {int(row["quadrature_order"]) for row in jac} != {4, 6, 8}:
        fail("quadrature order set")
    derived_jac = all(
        int(row["wrong_or_zero_count"]) == 0 and int(row["normalized_floor_fail_count"]) == 0
        for row in jac
    )
    if status["actual_quadrature_signed_jacobian_gate"] != derived_jac:
        fail("Jacobian gate derivation")
    if any(row["full_reference_domain_positivity"] != "UNVERIFIED" for row in jac):
        fail("full-domain overclaim")
    derived_c02 = bool(derived_global and derived_monitored and derived_jac)
    if status["r279_c02_complete"] != derived_c02:
        fail("R279-C02 derivation")

    digest = hashlib.sha256()
    count = 0
    with gzip.open(OUT / "c07-conformal-zone-mesh.msh.gz", "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            count += len(block)
    if digest.hexdigest() != status["mesh_uncompressed_sha256"] or count != status["mesh_uncompressed_bytes"]:
        fail("gzip reproduction")
    for key in (
        "full_reference_domain_curved_jacobian_positive", "structural_solution_executed",
        "mesh_convergence_complete", "r278_h02_closed", "capacity_credit", "selected",
        "safety_credit", "procurement_authorized", "fabrication_authorized",
        "assembly_authorized", "connection_authorized", "powered_testing_authorized",
        "motion_authorized", "energization_authorized",
    ):
        if status[key] is not False:
            fail(f"fail-closed state {key}")
    print(
        f"PASS: R293 PE topology execution synchronized; tets={len(sicn)} "
        f"global={derived_global} monitored={derived_monitored} jacobian={derived_jac} "
        f"R279-C02={derived_c02}; structural/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
