#!/usr/bin/env python3
"""Check the frozen R293 PE-junction mesh-method preregistration."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-prereg-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_topology_prereg_p01.py"
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1/c07-exact-zone-fragmented.brep"
R291_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
R291_STATUS = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1/analysis-status.json"
R292_BOUNDARY = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-disposition-p0.1/next-method-boundary.json"
WARNING = (
    "PRELIMINARY - PE-JUNCTION MESH-METHOD PREREGISTRATION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R293 preregistration check failed: {message}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    required = {
        "README.md", "analysis-status.json", "execution-provenance.json",
        "file-manifest.csv", "frozen-pe-topology-protocol.json",
        "inherited-target-register.csv",
    }
    if {path.name for path in OUT.iterdir()} != required:
        fail("source file set")
    if {path.name for path in RELEASE.iterdir()} != required:
        fail("release file set")
    manifest = rows(OUT / "file-manifest.csv")
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
    protocol = json.loads((OUT / "frozen-pe-topology-protocol.json").read_text(encoding="utf-8"))
    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    if protocol["candidate_id"] != "R293-C07-PE-TOPOLOGY-V01":
        fail("candidate identity")
    if protocol["linear_mesh_method"]["optimizer_sequence"] != ["Netgen", "Relocate3D"]:
        fail("optimizer sequence")
    if protocol["linear_mesh_method"]["high_order_optimizer"] != "NONE":
        fail("high-order optimizer")
    if not protocol["thresholds_unchanged"] or not status["single_candidate_frozen"]:
        fail("freeze state")
    if protocol["r288_brep_sha256"] != sha(R288):
        fail("R288 B-Rep binding")
    if protocol["r291_protocol_sha256"] != sha(R291_PREREG / "frozen-successor-protocol.json"):
        fail("R291 protocol binding")
    if protocol["r291_status_sha256"] != sha(R291_STATUS):
        fail("R291 status binding")
    if protocol["r292_method_boundary_sha256"] != sha(R292_BOUNDARY):
        fail("R292 boundary binding")
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator binding")
    targets = rows(OUT / "inherited-target-register.csv")
    if sum(row["target_kind"] == "EXACT_FAILED_POCKET_VOLUME" for row in targets) != 4:
        fail("volume target count")
    if sum(row["target_kind"] == "SYMMETRY_CLOSED_EXACT_CYLINDER_FACE" for row in targets) != 6:
        fail("face target count")
    for key in (
        "mesh_executed", "structural_solution_executed", "r279_c02_complete",
        "r278_h02_closed", "capacity_credit", "selected", "safety_credit",
        "work_authority",
    ):
        if status[key] is not False or protocol[key] is not False:
            fail(f"fail-closed state {key}")
    print("PASS: R293 PE-junction candidate frozen before execution; all size fields and thresholds unchanged; mesh/structural/H02/capacity/all authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
