#!/usr/bin/env python3
"""Fail-closed checker for the R288 exact C07 analysis-zone partition."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import gmsh


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-exact-zone-partition-p0.1"
GEN = ROOT / "tools/generate_hr_v0_j2_c07_exact_zone_partition_p01.py"
WARNING = "PRELIMINARY - EXACT ANALYSIS-ZONE CAD PARTITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"R288 exact-zone partition check failed: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def verify_manifest(path: Path) -> None:
    records = []
    with (path / "file-manifest.csv").open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    listed = {record["relative_path"] for record in records}
    actual = {item.name for item in path.iterdir() if item.is_file() and item.name != "file-manifest.csv"}
    if listed != actual or len(listed) != len(records):
        fail(f"manifest membership drift in {path}")
    for record in records:
        item = path / record["relative_path"]
        if sha(item) != record["sha256"] or item.stat().st_size != int(record["bytes"]):
            fail(f"manifest hash/size drift: {item}")
        if record["warning"] != WARNING:
            fail(f"manifest warning drift: {item}")


def main() -> int:
    required = {
        "README.md", "analysis-status.json", "c07-exact-zone-fragmented.brep",
        "exact-zone-register.csv", "execution-provenance.json", "file-manifest.csv",
        "fragment-volume-register.csv", "hole-geometry-erratum.csv", "open-holds.csv",
        "validation-register.csv",
    }
    if {item.name for item in OUT.iterdir() if item.is_file()} != required:
        fail("source package file set drift")
    if {item.name for item in RELEASE.iterdir() if item.is_file()} != required:
        fail("release package file set drift")
    verify_manifest(OUT)
    verify_manifest(RELEASE)
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"source/release parity drift: {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    if status["identifier"] != "HR-V0-J2-C07-EXACT-ZONE-PARTITION-P0.1" or status["round"] != "R288":
        fail("identifier/round drift")
    if status["primary_exact_zone_count"] != 27 or not status["exact_occ_fragment_membership_complete"]:
        fail("exact zone completion/count drift")
    if status["primary_zone_positive_volume_overlap_count"] != 0 or status["fragment_volume_relative_closure_error"] > 1e-10:
        fail("overlap or volume-closure gate failed")
    for key in (
        "hole_fixed_offset_gauge_volume_definition_complete", "conformal_mesh_generated",
        "exact_zone_quality_histograms_complete", "structural_solution_executed",
        "mesh_convergence_complete", "r279_c02_complete", "r278_h02_closed",
        "capacity_credit", "selected", "safety_credit", "procurement_authorized",
        "fabrication_authorized", "assembly_authorized", "connection_authorized",
        "powered_testing_authorized", "motion_authorized", "energization_authorized",
    ):
        if status[key] is not False:
            fail(f"fail-closed authority/state drift: {key}")
    if status["brep_sha256"] != sha(OUT / "c07-exact-zone-fragmented.brep"):
        fail("B-Rep status hash drift")

    zones = rows("exact-zone-register.csv")
    counts = {family: sum(row["family"] == family for row in zones) for family in {row["family"] for row in zones}}
    if counts != {"C07-PE": 8, "C07-PF": 1, "HOLE-SINGULAR-RIM": 12, "HOLE-LIGAMENT": 6}:
        fail(f"zone family count drift: {counts}")
    if len({row["zone_id"] for row in zones}) != 27 or any(float(row["material_volume_mm3"]) <= 0 for row in zones):
        fail("zone identity or positive-volume drift")
    if any("EXACT OCC FRAGMENT" not in row["classification"] for row in zones):
        fail("zone classification weakened")

    fragments = rows("fragment-volume-register.csv")
    if any(int(row["zone_membership_count"]) > 1 for row in fragments):
        fail("multiply assigned primary fragment")
    if len({row["fragment_signature_sha256"] for row in fragments}) != len(fragments):
        fail("nonunique fragment signatures")
    if len(fragments) != status["fragmented_material_volume_count"]:
        fail("fragment count status drift")

    holes = rows("hole-geometry-erratum.csv")
    by_id = {row["hole_id"]: row for row in holes}
    if set(by_id) != {"H1", "H2", "H3", "H4", "E1", "E2"}:
        fail("hole identity set drift")
    if any(float(by_id[hole]["exact_wall_front_y_mm"]) != 0.0 for hole in ("H1", "H2", "H3", "H4")):
        fail("M2.5 front datum drift")
    if any(float(by_id[hole]["exact_wall_front_y_mm"]) != 2.9 for hole in ("E1", "E2")):
        fail("M5 front datum correction drift")
    if any("OPEN" not in row["fixed_offset_gauge_volume_definition"] for row in holes):
        fail("unfrozen fixed-offset gauge thickness was invented")

    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    if provenance["generator_sha256"] != sha(GEN):
        fail("generator provenance drift")
    if provenance["step_sha256"] != status["step_sha256"]:
        fail("STEP provenance drift")

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.add("R288_CHECK")
        imported = gmsh.model.occ.importShapes(str(OUT / "c07-exact-zone-fragmented.brep"))
        gmsh.model.occ.synchronize()
        volumes = [tag for dim, tag in imported if dim == 3]
        if len(volumes) != len(fragments):
            fail(f"retained B-Rep volume count drift: {len(volumes)} != {len(fragments)}")
        imported_volume = sum(float(gmsh.model.occ.getMass(3, tag)) for tag in volumes)
        registered_volume = sum(float(row["volume_mm3"]) for row in fragments)
        if abs(imported_volume - registered_volume) / registered_volume > 1e-10:
            fail("retained B-Rep volume differs from fragment register")
    finally:
        gmsh.finalize()

    print(
        f"PASS: R288 exact C07 partition synchronized; 27 positive-volume zones, "
        f"{len(fragments)} conformal CAD fragments, zero overlap and volume closure pass; "
        "mesh/structural convergence/R279-C02/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
