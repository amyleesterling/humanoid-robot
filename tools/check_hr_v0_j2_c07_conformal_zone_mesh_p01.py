#!/usr/bin/env python3
"""Checker for the bounded R289 exact-zone conformal mesh evidence."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-zone-mesh-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
WARNING = "PRELIMINARY - EXACT-ZONE CONFORMAL MESH EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R289 conformal-zone mesh check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def verify_manifest(directory: Path) -> None:
    with (directory / "file-manifest.csv").open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    listed = {row["relative_path"] for row in manifest}
    actual = {path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
    if listed != actual or len(listed) != len(manifest):
        fail(f"manifest membership drift: {directory}")
    for row in manifest:
        path = directory / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest hash/size drift: {path}")


def main() -> int:
    required = {
        "README.md", "actual-quadrature-jacobian-register.csv", "analysis-status.json",
        "c07-conformal-zone-mesh.msh.gz", "execution-provenance.json", "file-manifest.csv",
        "open-holds.csv", "raw-conformal-zone-mesh.npz", "sicn-histogram.csv",
        "zone-quality-summary.csv", "zone-volume-integration.csv",
    }
    if {path.name for path in OUT.iterdir() if path.is_file()} != required:
        fail("source package file set drift")
    if {path.name for path in RELEASE.iterdir() if path.is_file()} != required:
        fail("release package file set drift")
    verify_manifest(OUT)
    verify_manifest(RELEASE)
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"source/release parity drift: {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    if status["identifier"] != "HR-V0-J2-C07-CONFORMAL-ZONE-MESH-P0.1" or status["round"] != "R289":
        fail("identifier/round drift")
    if not status["exact_zone_element_provenance_complete"] or not status["monitored_zone_histograms_complete"]:
        fail("exact provenance/histogram completion drift")
    for key in (
        "full_reference_domain_curved_jacobian_positive", "structural_solution_executed",
        "mesh_convergence_complete", "r278_h02_closed", "capacity_credit", "selected",
        "safety_credit", "procurement_authorized", "fabrication_authorized",
        "assembly_authorized", "connection_authorized", "powered_testing_authorized",
        "motion_authorized", "energization_authorized",
    ):
        if status[key] is not False:
            fail(f"fail-closed state drift: {key}")
    # R279-C02 is data-driven: a bounded pass is permitted only when every
    # constituent gate passes; it never closes H02 or work authority.
    derived_c02 = bool(status["global_sicn_gate"] and status["monitored_zone_minimum_gate"] and status["actual_quadrature_signed_jacobian_gate"])
    if status["r279_c02_complete"] != derived_c02:
        fail("R279-C02 derivation drift")

    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator provenance drift")
    if provenance["r288_brep_sha256"] != sha(R288 / "c07-exact-zone-fragmented.brep"):
        fail("R288 B-Rep provenance drift")
    mesh_gzip = OUT / "c07-conformal-zone-mesh.msh.gz"
    if status["mesh_gzip_sha256"] != sha(mesh_gzip):
        fail("compressed mesh status hash drift")
    digest = hashlib.sha256()
    uncompressed_bytes = 0
    with gzip.open(mesh_gzip, "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            uncompressed_bytes += len(block)
    if digest.hexdigest() != status["mesh_uncompressed_sha256"] or uncompressed_bytes != status["mesh_uncompressed_bytes"]:
        fail("compressed mesh does not reproduce recorded uncompressed bytes")

    data = np.load(OUT / "raw-conformal-zone-mesh.npz")
    linear_tags = data["linear_element_tags"]
    tet10_tags = data["tet10_element_tags"]
    sicn = data["linear_sicn"]
    zone_codes = data["element_zone_code"]
    if len(linear_tags) != status["linear_tetrahedra"] or len(tet10_tags) != status["tet10_tetrahedra"]:
        fail("raw element count drift")
    if len(sicn) != len(linear_tags) or len(zone_codes) != len(linear_tags) or not np.all(np.isfinite(sicn)):
        fail("raw quality/provenance array drift")
    if abs(float(np.min(sicn)) - status["global_sicn_minimum"]) > 1e-14:
        fail("raw SICN minimum drift")
    if abs(float(np.mean(sicn < 0.20)) - status["global_sicn_fraction_below_0p20"]) > 1e-14:
        fail("raw SICN fraction drift")

    hist = rows("sicn-histogram.csv")
    global_rows = [row for row in hist if row["scope"] == "GLOBAL"]
    if len(global_rows) != 10 or sum(int(row["count"]) for row in global_rows) != len(sicn):
        fail("global histogram reconciliation drift")
    summaries = rows("zone-quality-summary.csv")
    if len(summaries) != 28 or len({row["zone_id"] for row in summaries}) != 28:
        fail("exact zone summary count/identity drift")
    for summary in summaries:
        zone_hist = [row for row in hist if row["scope"] == "EXACT_ZONE" and row["zone_id"] == summary["zone_id"]]
        if len(zone_hist) != 10 or sum(int(row["count"]) for row in zone_hist) != int(summary["tetrahedra"]):
            fail(f"zone histogram reconciliation drift: {summary['zone_id']}")

    jac = rows("actual-quadrature-jacobian-register.csv")
    if {int(row["quadrature_order"]) for row in jac} != {4, 6, 8}:
        fail("quadrature-order set drift")
    derived_jac = all(int(row["wrong_or_zero_count"]) == 0 and int(row["normalized_floor_fail_count"]) == 0 for row in jac)
    if status["actual_quadrature_signed_jacobian_gate"] != derived_jac:
        fail("actual-quadrature Jacobian derivation drift")
    if any(row["full_reference_domain_positivity"] != "UNVERIFIED" for row in jac):
        fail("finite quadrature screen overclaimed full-domain positivity")

    print(
        f"PASS: R289 synchronized; {len(linear_tags)} conformal tetrahedra, 28 exact-zone histograms; "
        f"global={status['global_sicn_gate']} monitored={status['monitored_zone_minimum_gate']} "
        f"actual_quadrature={status['actual_quadrature_signed_jacobian_gate']} R279-C02={status['r279_c02_complete']}; "
        "structural convergence/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
