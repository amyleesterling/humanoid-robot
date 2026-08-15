#!/usr/bin/env python3
"""Checker for the R290 R289-failure localization evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-mesh-failure-localization-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-mesh-failure-localization-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_conformal_mesh_failure_localization_p01.py"
R289 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
WARNING = "PRELIMINARY - CONFORMAL MESH FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R290 localization check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {"README.md", "analysis-status.json", "curved-jacobian-failure-localization.csv", "execution-provenance.json", "file-manifest.csv", "index.html", "sicn-failure-localization.csv"}
    if {path.name for path in OUT.iterdir() if path.is_file()} != required or {path.name for path in RELEASE.iterdir() if path.is_file()} != required:
        fail("package file set drift")
    manifest = rows("file-manifest.csv")
    if {row["relative_path"] for row in manifest} != required - {"file-manifest.csv"}:
        fail("manifest membership drift")
    for row in manifest:
        path = OUT / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest hash/size drift: {path}")
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"source/release parity drift: {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    sicn = rows("sicn-failure-localization.csv")
    jac = rows("curved-jacobian-failure-localization.csv")
    if len(sicn) != status["sicn_failure_elements"] or len(jac) != status["curved_jacobian_failed_order_qp_pairs"]:
        fail("failure count status drift")
    if len({int(row["element_tag"]) for row in jac}) != status["curved_jacobian_unique_failed_elements"]:
        fail("unique curved failure element count drift")
    if set(row["exact_zone_id"] for row in sicn) != {"C07-PE-EAST-STRAIGHT", "C07-PE-NORTH-STRAIGHT", "C07-PE-SOUTH-STRAIGHT", "C07-PE-WEST-STRAIGHT"}:
        fail("SICN exact-zone cluster drift")
    if any(float(row["sicn"]) >= 0.20 for row in sicn):
        fail("nonfailure included in SICN localization")
    if any(float(row["determinant"]) > 0 and float(row["normalized_determinant"]) > 1e-10 for row in jac):
        fail("nonfailure included in Jacobian localization")
    if any(not row["nearest_exact_face_signature_sha256"] for row in jac):
        fail("curved failure lacks exact face binding")
    for key in ("remesh_executed", "r279_c02_complete", "r278_h02_closed", "capacity_credit", "selected", "safety_credit", "fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
        if status[key] is not False:
            fail(f"fail-closed state drift: {key}")
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    if provenance["generator_sha256"] != sha(GEN) or provenance["r289_raw_sha256"] != sha(R289 / "raw-conformal-zone-mesh.npz"):
        fail("provenance drift")
    if provenance["r289_mesh_gzip_sha256"] != sha(R289 / "c07-conformal-zone-mesh.msh.gz"):
        fail("compressed R289 mesh provenance drift")
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:16px/1.55", "font-size:16px", "overflow-x:auto", "R279-C02 remains open", WARNING):
        if token not in guide:
            fail(f"interactive guide token missing: {token}")
    print(f"PASS: R290 localized {len(sicn)} SICN failures and {len(jac)} failed order-QP pairs; successor remesh/H02/capacity/all authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
