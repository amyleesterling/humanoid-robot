"""Fail-closed checks for the corrected HR-V0 arm candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.2"
REVISION = "HR-V0-ARM-ARCH-P0.2"
EXPECTED_FILES = {
    "HR-V0_arm_architecture_candidate.glb",
    "HR-V0_arm_architecture_candidate.step",
    "HR-V0_arm_architecture_candidate.svg",
    "architecture-summary.json",
    "collision-sweep.csv",
    "fastener-candidate-schedule.csv",
    "interface-schedule.csv",
    "joint-load-screen.csv",
    "tool-access-screen.csv",
    "transform-schedule.csv",
}
EXPECTED_PARTS = {
    "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step",
    "MV0-C02_20-2040_100mm_vertical_collision_envelope.step",
    "MV0-C03_20-2040_50mm_vertical_collision_envelope.step",
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
        if part_names != EXPECTED_PARTS:
            errors.append(f"candidate part artifact set changed: {sorted(part_names)}")

    if not errors:
        summary = json.loads((OUT / "architecture-summary.json").read_text(encoding="utf-8"))
        if summary.get("revision") != REVISION:
            errors.append("candidate revision changed")
        if "NOT RELEASED" not in summary.get("warning", ""):
            errors.append("preliminary warning missing")

        geometry = summary.get("candidate_geometry_mm", {})
        if geometry.get("j1_to_j2_axis") != 193.025 or geometry.get("j2_to_g1_frame_origin") != 119.525 or geometry.get("reserved_g1_to_object_center_max") != 47.45:
            errors.append("candidate axis schedule changed")
        if geometry.get("adapter_envelope") != [48.0, 4.7625, 40.0] or geometry.get("upper_beam_envelope") != [20.0, 100.0, 40.0] or geometry.get("forearm_beam_envelope") != [20.0, 50.0, 40.0]:
            errors.append("20-2040 strong-axis orientation changed")
        pattern = geometry.get("robotis_rectangular_pattern", {})
        if pattern.get("x_centers") != [-16.0, 16.0] or pattern.get("z_centers") != [-8.0, 8.0]:
            errors.append("ROBOTIS rectangular frame pattern changed")
        taps = geometry.get("profile_end_tap_centers", {})
        if taps.get("x") != 0.0 or taps.get("z_centers") != [-10.0, 10.0] or taps.get("core_diameter") != 4.19:
            errors.append("20-2040 end-tap registration changed")

        registration = summary.get("actuator_axis_registration", {})
        if registration.get("matrix_3x3") != [[0, 0, -1], [1, 0, 0], [0, -1, 0]] or registration.get("joint_output_axis") != [-1, 0, 0]:
            errors.append("XM540 vendor-to-joint rotation changed")
        if registration.get("registered_s102_axes_yz") != [[13.5, 41.5], [-13.5, 41.5]]:
            errors.append("XM540/S102 hole-axis registration changed")
        parallel = summary.get("axis_parallelism_math", {})
        if parallel.get("dot_product") != 1.0 or parallel.get("angular_difference_deg") != 0.0:
            errors.append("parallel-axis proof changed")

        collision = summary.get("collision_screen", {})
        if collision.get("sampled_j2_range_deg") != [15, 125] or collision.get("increment_deg") != 0.5 or collision.get("sample_count") != 221 or collision.get("provisional_soft_limit_deg") != 120.0:
            errors.append("collision-sweep range changed")
        if collision.get("maximum_positive_intersection_mm3_within_provisional_limit", math.inf) > 1e-5 or collision.get("first_nominal_collision_deg") != 122.0:
            errors.append("provisional collision limit no longer matches the dense sweep")

        source_hashes = summary.get("vendor_source_sha256", {})
        for filename in ("XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp", "FR12-H104K.stp"):
            if source_hashes.get(filename) != sha256(ROOT / "cad" / "vendor" / "robotis" / filename):
                errors.append(f"vendor source hash mismatch: {filename}")
        source_hashes_8020 = summary.get("vendor_8020_source_sha256", {})
        for filename in ("20-2040-endview.svg", "20-2040-dimensions.jpg", "20-2040-30mm.EPRT"):
            if source_hashes_8020.get(filename) != sha256(ROOT / "cad" / "vendor" / "8020" / filename):
                errors.append(f"80/20 source hash mismatch: {filename}")

        loads = summary.get("mass_and_load_screen", {})
        if loads.get("allocated_shoulder_gravity_nm") != 1.777 or loads.get("allocated_elbow_gravity_nm") != 0.483:
            errors.append("candidate gravity screen changed")
        if len(summary.get("open_release_items", [])) < 9:
            errors.append("open release-item list is incomplete")

        transforms = rows(OUT / "transform-schedule.csv")
        if len(transforms) != 5:
            errors.append("expected five transform records")
        j2 = next((row for row in transforms if row["item"] == "J2 joint package and S102"), {})
        if j2.get("ty_mm") != "193.025" or j2.get("rx_deg") != "90":
            errors.append("J2 body transform changed")
        output = next((row for row in transforms if row["item"] == "J2 H101 straight-reference pose"), {})
        if "-90 deg output offset" not in output.get("status", ""):
            errors.append("J2 output offset is not explicit")

        interfaces = rows(OUT / "interface-schedule.csv")
        if len(interfaces) != 7 or not any("EXACT CANDIDATE HOLD" in row["fasteners"] for row in interfaces) or not any(row["fasteners"] == "SELECTION REQUIRED" for row in interfaces):
            errors.append("interface schedule lost its candidate/selection boundary")
        if any(not any(token in row["status"] for token in ("not_released", "candidate", "open", "static_proof_only")) for row in interfaces):
            errors.append("interface status is not fail-closed")

        fasteners = rows(OUT / "fastener-candidate-schedule.csv")
        if len(fasteners) != 3 or fasteners[0].get("candidate_order_code") != "SSK-M5-16-A2" or fasteners[1].get("candidate_order_code") != "SELECTION REQUIRED":
            errors.append("fastener candidate/selection boundary changed")
        access = rows(OUT / "tool-access-screen.csv")
        if len(access) != 5 or not any(row["result"] == "GEOMETRY PASS / STRENGTH OPEN" for row in access):
            errors.append("tool-access screen no longer fails closed on pull-through")
        load_screens = rows(OUT / "joint-load-screen.csv")
        if len(load_screens) != 4 or not any(row["status"] == "BLOCKER" for row in load_screens):
            errors.append("joint-load screen lost its unresolved blocker")

        sweep = rows(OUT / "collision-sweep.csv")
        expected_angles = [15.0 + 0.5 * index for index in range(221)]
        if len(sweep) != 221 or [float(row["j2_internal_deg"]) for row in sweep] != expected_angles:
            errors.append("collision sample schedule changed")
        within_limit = [row for row in sweep if float(row["j2_internal_deg"]) <= 120.0]
        collisions = [row for row in sweep if row["result"] == "COLLISION"]
        if any(row["result"] != "PASS" or float(row["sampled_pairwise_intersection_mm3"]) > 1e-5 for row in within_limit):
            errors.append("collision occurs within the provisional 120 degree soft limit")
        if not collisions or float(collisions[0]["j2_internal_deg"]) != 122.0 or len(collisions) != 7:
            errors.append("expected fail-closed collision boundary at 122 through 125 degrees changed")

        try:
            root = ET.parse(OUT / "HR-V0_arm_architecture_candidate.svg").getroot()
            text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("text"))
            for token in (REVISION, "NOT RELEASED", "J1-J2 = 193.0250 mm", "P0.1 is superseded", "Do not fabricate"):
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
    print("Corrected XM540/S102 registration; vertical 20-2040; 221-pose self-collision screen; fail-closed joint proof")
    print("PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
