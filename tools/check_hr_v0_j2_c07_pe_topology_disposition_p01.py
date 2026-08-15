#!/usr/bin/env python3
"""Check the R294 disposition of the failed R293 relocation candidate."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from hr_v0_mesh_raw_shards import load_shards


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-disposition-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-disposition-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_topology_disposition_p01.py"
R291 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
R293 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
WARNING = (
    "PRELIMINARY - PE-JUNCTION MESH-METHOD DISPOSITION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R294 disposition check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {
        "README.md", "analysis-status.json", "execution-provenance.json",
        "file-manifest.csv", "index.html", "next-method-boundary.json",
        "r291-r293-comparison.csv", "r293-low-sicn-localization.csv",
    }
    if {path.name for path in OUT.iterdir()} != required or {path.name for path in RELEASE.iterdir()} != required:
        fail("file set")
    manifest = rows("file-manifest.csv")
    if {row["relative_path"] for row in manifest} != required - {"file-manifest.csv"}:
        fail("manifest membership")
    for row in manifest:
        path = OUT / row["relative_path"]
        if sha(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            fail(f"manifest mismatch {path.name}")
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"mirror mismatch {name}")
    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    boundary = json.loads((OUT / "next-method-boundary.json").read_text(encoding="utf-8"))
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator binding")
    if provenance["r291_status_sha256"] != sha(R291 / "analysis-status.json"):
        fail("R291 status binding")
    r293_provenance = json.loads((R293 / "execution-provenance.json").read_text(encoding="utf-8"))
    if provenance["r293_status_sha256"] != r293_provenance["pre_raw_shard_migration_status_sha256"]:
        fail("R293 status binding")
    data291 = np.load(R291 / "raw-conformal-zone-mesh.npz")
    data293 = load_shards(R293)
    if not np.array_equal(data291["linear_element_tags"], data293["linear_element_tags"]):
        fail("element tag topology")
    if not np.array_equal(data291["linear_tet4_connectivity"], data293["linear_tet4_connectivity"]):
        fail("connectivity topology")
    q293 = data293["linear_sicn"]
    localization = rows("r293-low-sicn-localization.csv")
    if len(localization) != int(np.count_nonzero(q293 < 0.20)) or len(localization) != status["r293_low_sicn_cells"]:
        fail("low-quality cell count")
    if {row["exact_zone_id"] for row in localization} != set(status["r293_monitored_zone_failures"]) | {"C07-MATRIX"}:
        fail("localized zone set")
    if not status["r293_candidate_rejected"] or not status["linear_topology_unchanged"]:
        fail("disposition state")
    if boundary["next_candidate_id"] != "R295-C07-PE-FRONTAL-V01":
        fail("next candidate identity")
    if "Algorithm3D=4 (Frontal)" not in boundary["required_next_preregistration"]:
        fail("next algorithm boundary")
    for key in (
        "next_mesh_executed", "structural_solution_executed", "r279_c02_complete",
        "r278_h02_closed", "capacity_credit", "selected", "safety_credit", "work_authority",
    ):
        if status[key] is not False or boundary[key] is not False:
            fail(f"fail-closed state {key}")
    html = (OUT / "index.html").read_text(encoding="utf-8")
    if "font:17px" not in html or "font-size:16px" not in html or "overflow:auto" not in html or WARNING not in html:
        fail("interactive guide legibility/warning")
    print(f"PASS: R294 rejects relocation on raw unchanged topology; {len(localization)} low-quality cells retained; R295 Frontal candidate unexecuted; structural/H02/capacity/all authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
