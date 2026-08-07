"""Fail-closed checks for the HR-V0 exact-coordinate arm candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.1"
REVISION = "HR-V0-ARM-ARCH-P0.1"
EXPECTED_FILES = {
    "HR-V0_arm_architecture_candidate.glb",
    "HR-V0_arm_architecture_candidate.step",
    "HR-V0_arm_architecture_candidate.svg",
    "architecture-summary.json",
    "collision-sweep.csv",
    "interface-schedule.csv",
    "transform-schedule.csv",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir():
        errors.append("candidate output directory is absent")
    else:
        actual = {p.name for p in OUT.iterdir() if p.is_file()}
        if actual != EXPECTED_FILES:
            errors.append(f"top-level artifact set changed: {sorted(actual)}")
        part_names = {p.name for p in (OUT / "parts").iterdir()} if (OUT / "parts").is_dir() else set()
        expected_parts = {"MV0-C01_pcd22_to_20-2040_adapter.step", "MV0-C02_20-2040_100mm_collision_envelope.step", "MV0-C03_20-2040_50mm_collision_envelope.step"}
        if part_names != expected_parts:
            errors.append(f"candidate part artifact set changed: {sorted(part_names)}")

    if not errors:
        summary = json.loads((OUT / "architecture-summary.json").read_text(encoding="utf-8"))
        if summary.get("revision") != REVISION:
            errors.append("candidate revision changed")
        if "NOT RELEASED" not in summary.get("warning", ""):
            errors.append("preliminary warning missing")
        geometry = summary.get("candidate_geometry_mm", {})
        if geometry.get("j1_to_j2_axis") != 191.5 or geometry.get("j2_to_g1_frame_origin") != 118.0 or geometry.get("reserved_g1_to_object_center_max") != 50.5:
            errors.append("candidate axis schedule changed")
        parallel = summary.get("axis_parallelism_math", {})
        if parallel.get("dot_product") != 1.0 or parallel.get("angular_difference_deg") != 0.0:
            errors.append("parallel-axis proof changed")
        collision = summary.get("collision_screen", {})
        if collision.get("sampled_j2_range_deg") != [15, 125] or collision.get("increment_deg") != 5:
            errors.append("collision-sweep range changed")
        if collision.get("maximum_positive_intersection_mm3", math.inf) > 1e-5:
            errors.append("positive self-intersection detected")
        source_hashes = summary.get("vendor_source_sha256", {})
        for filename in ("XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp", "FR12-H104K.stp"):
            if source_hashes.get(filename) != sha256(ROOT / "cad" / "vendor" / "robotis" / filename):
                errors.append(f"vendor source hash mismatch: {filename}")
        loads = summary.get("mass_and_load_screen", {})
        if loads.get("allocated_shoulder_gravity_nm") != 1.762 or loads.get("allocated_elbow_gravity_nm") != 0.478:
            errors.append("candidate gravity screen changed")
        if len(summary.get("open_release_items", [])) < 7:
            errors.append("open release-item list is incomplete")

        transforms = rows(OUT / "transform-schedule.csv")
        if len(transforms) != 5:
            errors.append("expected five transform records")
        j2 = next((row for row in transforms if row["item"] == "J2 body and S102"), {})
        if j2.get("ty_mm") != "191.5" or j2.get("rx_deg") != "90":
            errors.append("J2 body transform changed")
        output = next((row for row in transforms if row["item"] == "J2 H101 straight-reference pose"), {})
        if "-90 deg output offset" not in output.get("status", ""):
            errors.append("J2 output offset is not explicit")

        interfaces = rows(OUT / "interface-schedule.csv")
        if len(interfaces) != 7 or any(row["fasteners"] != "SELECTION REQUIRED" for row in interfaces):
            errors.append("interface schedule released or lost an interface")
        if any("not_released" not in row["status"] and "candidate" not in row["status"] and "open" not in row["status"] for row in interfaces):
            errors.append("interface status is not fail-closed")

        sweep = rows(OUT / "collision-sweep.csv")
        if len(sweep) != 23 or [int(row["j2_internal_deg"]) for row in sweep] != list(range(15, 126, 5)):
            errors.append("collision sample schedule changed")
        if any(row["result"] != "PASS" or float(row["sampled_pairwise_intersection_mm3"]) > 1e-5 for row in sweep):
            errors.append("collision screen contains a failing sample")

        try:
            root = ET.parse(OUT / "HR-V0_arm_architecture_candidate.svg").getroot()
            text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("text"))
            for token in (REVISION, "NOT RELEASED", "J1-J2 = 191.5 mm", "Do not fabricate"):
                if token not in text:
                    errors.append(f"readable view omits {token}")
        except ET.ParseError as exc:
            errors.append(f"readable SVG does not parse: {exc}")

        if (OUT / "HR-V0_arm_architecture_candidate.step").stat().st_size < 1_000_000:
            errors.append("combined exact-source STEP is unexpectedly small")
        if (OUT / "HR-V0_arm_architecture_candidate.glb").stat().st_size < 100_000:
            errors.append("interactive GLB is unexpectedly small")

    if errors:
        print("HR-V0 arm architecture validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 arm architecture validation: PASS")
    print("Exact ROBOTIS transforms; parallel J1/J2 axes; 23-pose self-collision screen; fail-closed interfaces")
    print("PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
