#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-failure-localization-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-rail-jacobian-failure-localization-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_rail_jacobian_failure_localization_p01.py"
R303 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R304 localization check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {
        "README.md",
        "analysis-status.json",
        "curved-jacobian-failure-localization.csv",
        "exact-face-failure-summary.csv",
        "execution-provenance.json",
        "file-manifest.csv",
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
    failures = rows("curved-jacobian-failure-localization.csv")
    summary = rows("exact-face-failure-summary.csv")
    if provenance["generator_sha256"] != sha(GEN) or provenance["r303_status_sha256"] != sha(R303 / "analysis-status.json"):
        fail("provenance")
    if provenance["r303_raw_linear_sha256"] != sha(R303 / "raw-linear-mesh.npz") or provenance["r303_raw_tet10_sha256"] != sha(R303 / "raw-tet10-mesh.npz"):
        fail("raw provenance")
    if (
        len(failures) != status["failed_order_qp_pairs"]
        or len({row["element_tag"] for row in failures}) != status["unique_failed_elements"]
        or len({row["nearest_exact_face_signature_sha256"] for row in failures}) != status["nearest_exact_face_clusters"]
        or len(summary) != status["nearest_exact_face_clusters"]
    ):
        fail("counts")
    if not all(
        float(row["determinant"]) <= 0 or float(row["normalized_determinant"]) <= 1e-10 for row in failures
    ):
        fail("failure rows")
    for row in summary:
        subset = [
            item
            for item in failures
            if item["nearest_exact_face_signature_sha256"] == row["nearest_exact_face_signature_sha256"]
        ]
        if len(subset) != int(row["failed_order_qp_pairs"]) or len({item["element_tag"] for item in subset}) != int(row["unique_failed_elements"]):
            fail("face summary")
    for key in (
        "remesh_executed",
        "structural_solution_executed",
        "r279_c02_complete",
        "r278_h02_closed",
        "capacity_credit",
        "selected",
        "safety_credit",
        "work_authority",
    ):
        if status[key] is not False:
            fail(f"fail-closed {key}")
    print(
        f"PASS: R304 localizes {len(failures)} residual curved QPs across "
        f"{status['unique_failed_elements']} element(s)/{status['nearest_exact_face_clusters']} exact face cluster(s); "
        "structural/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
