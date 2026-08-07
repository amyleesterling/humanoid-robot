"""Fail-closed checks for the fabrication-defined HR-V0 arm candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.5"
ARM_SOURCE_REGISTER = ROOT / "cad" / "vendor" / "arm-interface-source-register.csv"
REVISION = "HR-V0-ARM-ARCH-P0.5"
EXPECTED_FILES = {
    "HR-V0_arm_architecture_candidate.glb",
    "HR-V0_arm_architecture_candidate.step",
    "HR-V0_arm_architecture_candidate.svg",
    "architecture-summary.json",
    "adapter-drawing-controls.csv",
    "adapter-proof-analysis.csv",
    "collision-sweep.csv",
    "column-support-analysis.csv",
    "fastener-candidate-schedule.csv",
    "interface-feature-evidence.csv",
    "interface-schedule.csv",
    "joint-load-screen.csv",
    "MV0-C01_adapter-candidate-drawing.svg",
    "MV0-C04_gripper-adapter-candidate-drawing.svg",
    "MV0-C05_shoulder-support-candidate-drawing.svg",
    "new-interface-drawing-controls.csv",
    "tool-access-screen.csv",
    "transform-schedule.csv",
}
EXPECTED_PARTS = {
    "MV0-C01_adapter-finished-profile.dxf",
    "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step",
    "MV0-C02_20-2040_100mm_vertical_collision_envelope.step",
    "MV0-C03_20-2040_50mm_vertical_collision_envelope.step",
    "MV0-C04_gripper-adapter-finished-profile.dxf",
    "MV0-C04_H104_to_20-2040_countersunk_adapter.step",
    "MV0-C05_S102_to_40-4040_side_slot_support.step",
    "MV0-C05_shoulder-support-finished-profile.dxf",
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
        source_rows = rows(ARM_SOURCE_REGISTER)
        expected_source_codes = ["SELECTION REQUIRED", "SELECTION REQUIRED", "1249", "SHKL-M5-20-A2-R360", "SCB2.5-20", "HNN-M2.5-A2", "20-7047", "40-4040", "17-8520", "13035", "40006-BP", "FR12-H104K", "FR13-S102K"]
        if len(source_rows) != 13 or [row.get("order_code") for row in source_rows] != expected_source_codes:
            errors.append("controlled arm-interface source register changed")
        if any(row.get("access_date") != "2026-08-07" or not row.get("source_url", "").startswith("https://") for row in source_rows):
            errors.append("arm-interface source register lost its dated primary URL boundary")
        if "Typical" not in source_rows[0].get("release_effect", "") or "not design allowables" not in (ROOT / "cad" / "vendor" / "arm-interface-source-register.md").read_text(encoding="utf-8"):
            errors.append("material typical-value caveat is incomplete")

        summary = json.loads((OUT / "architecture-summary.json").read_text(encoding="utf-8"))
        if summary.get("revision") != REVISION:
            errors.append("candidate revision changed")
        if "NOT RELEASED" not in summary.get("warning", ""):
            errors.append("preliminary warning missing")

        geometry = summary.get("candidate_geometry_mm", {})
        if geometry.get("j1_to_j2_axis") != 202.55 or geometry.get("j2_to_g1_frame_origin") != 129.05 or geometry.get("reserved_g1_to_object_center_max") != 28.4:
            errors.append("candidate axis schedule changed")
        if geometry.get("adapter_envelope") != [48.0, 9.525, 40.0] or geometry.get("gripper_adapter_envelope") != [48.0, 9.525, 40.0] or geometry.get("shoulder_support_envelope") != [48.0, 9.525, 80.0] or geometry.get("adapter_finished_thickness_range") != [9.0, 10.0] or geometry.get("upper_beam_envelope") != [20.0, 100.0, 40.0] or geometry.get("forearm_beam_envelope") != [20.0, 50.0, 40.0]:
            errors.append("20-2040 strong-axis orientation changed")
        if geometry.get("h104_selected_local_axes_xz") != [[-11.0, -8.0], [11.0, -8.0], [-12.0, 6.0], [12.0, 6.0]] or geometry.get("support_m8_axes_xz") != [[0.0, -30.0], [0.0, 30.0]] or geometry.get("j1_a0_transform_mm") != [-210.0, 81.025, 500.0]:
            errors.append("integrated shoulder/H104 interface coordinates changed")
        pattern = geometry.get("robotis_rectangular_pattern", {})
        if pattern.get("x_centers") != [-16.0, 16.0] or pattern.get("z_centers") != [-8.0, 8.0]:
            errors.append("ROBOTIS rectangular frame pattern changed")
        taps = geometry.get("profile_end_tap_centers", {})
        if taps.get("x") != 0.0 or taps.get("z_centers") != [-10.0, 10.0] or taps.get("core_diameter") != 4.19:
            errors.append("20-2040 end-tap registration changed")
        countersink = geometry.get("m5_countersink", {})
        if countersink.get("finished_diameter_range") != [11.3, 11.4] or countersink.get("maximum_depth_screen") != 3.1:
            errors.append("M5 countersink fabrication envelope changed")

        registration = summary.get("actuator_axis_registration", {})
        if registration.get("matrix_3x3") != [[0, 0, -1], [1, 0, 0], [0, -1, 0]] or registration.get("joint_output_axis") != [-1, 0, 0]:
            errors.append("XM540 vendor-to-joint rotation changed")
        if registration.get("registered_s102_axes_yz") != [[13.5, 41.5], [-13.5, 41.5]]:
            errors.append("XM540/S102 hole-axis registration changed")
        parallel = summary.get("axis_parallelism_math", {})
        if parallel.get("dot_product") != 1.0 or parallel.get("angular_difference_deg") != 0.0:
            errors.append("parallel-axis proof changed")

        collision = summary.get("collision_screen", {})
        if collision.get("sampled_j1_range_deg") != [-20, 70] or collision.get("sampled_j2_range_deg") != [15, 125] or collision.get("increment_deg") != 0.5 or collision.get("sample_count") != 40001 or collision.get("provisional_soft_limit_deg") != 120.0:
            errors.append("collision-sweep range changed")
        if collision.get("maximum_positive_intersection_mm3_within_provisional_limit", math.inf) > 1e-5 or collision.get("first_nominal_collision_j2_deg") != 122.0:
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
        if loads.get("allocated_shoulder_gravity_nm") != 1.858 or loads.get("allocated_elbow_gravity_nm") != 0.498:
            errors.append("candidate gravity screen changed")
        if len(summary.get("open_release_items", [])) < 9:
            errors.append("open release-item list is incomplete")

        transforms = rows(OUT / "transform-schedule.csv")
        if len(transforms) != 8:
            errors.append("expected eight integrated transform records")
        j1 = next((row for row in transforms if row["item"] == "J1 XM540 body and S102"), {})
        if j1.get("rx_deg") != "90":
            errors.append("J1 fixed package roll changed")
        j2 = next((row for row in transforms if row["item"] == "J2 joint package and S102"), {})
        if j2.get("ty_mm") != "202.55" or j2.get("rx_deg") != "90":
            errors.append("J2 body transform changed")
        output = next((row for row in transforms if row["item"] == "J2 H101 straight-reference pose"), {})
        if "-90 deg output offset" not in output.get("status", ""):
            errors.append("J2 output offset is not explicit")
        base_transform = next((row for row in transforms if row["item"] == "J1 local frame"), {})
        if (base_transform.get("tx_mm"), base_transform.get("ty_mm"), base_transform.get("tz_mm")) != ("-210.0", "81.025", "500.0"):
            errors.append("J1-to-base candidate transform changed")

        interfaces = rows(OUT / "interface-schedule.csv")
        if len(interfaces) != 8 or [row.get("interface") for row in interfaces] != ["A00", "A01", "A02", "A03", "A04", "A05", "A06", "A07"] or not any("17-8520 + 13035" in row["fasteners"] for row in interfaces) or not any("SHKL-M5-20-A2-R360 EXACT CANDIDATE HOLD" in row["fasteners"] for row in interfaces) or not any("SCB2.5-20 + ACCU HNN-M2.5-A2 EXACT CANDIDATE HOLD" in row["fasteners"] for row in interfaces):
            errors.append("interface schedule lost its candidate/selection boundary")
        if any(not any(token in row["status"] for token in ("not_released", "candidate", "open", "static_proof_only")) for row in interfaces):
            errors.append("interface status is not fail-closed")

        fasteners = rows(OUT / "fastener-candidate-schedule.csv")
        if len(fasteners) != 6 or [row.get("candidate_order_code") for row in fasteners] != ["SHKL-M5-20-A2-R360", "SCB2.5-20", "HNN-M2.5-A2", "20-7047", "17-8520", "13035"] or any(row.get("status") not in ("EXACT CANDIDATE HOLD", "EXACT SERVICE CANDIDATE HOLD") for row in fasteners):
            errors.append("fastener candidate/selection boundary changed")
        access = rows(OUT / "tool-access-screen.csv")
        if len(access) != 8 or not any(row["result"] == "PASS NOMINAL / PROOF OPEN" for row in access) or not any(row["result"] == "PASS NOMINAL / RECEIVED STACK OPEN" for row in access) or not any(row["result"] == "PASS NOMINAL / TOOL PROOF OPEN" for row in access):
            errors.append("tool-access screen no longer retains proof/received-stack holds")
        load_screens = rows(OUT / "joint-load-screen.csv")
        if len(load_screens) != 5 or any(row["status"] == "BLOCKER" for row in load_screens) or sum("INDICATIVE STATIC SCREEN PASS" in row["status"] for row in load_screens) != 2:
            errors.append("joint-load screen lost the strengthened adapter boundary")
        drawing_controls = rows(OUT / "adapter-drawing-controls.csv")
        if len(drawing_controls) != 10 or [row.get("control_id") for row in drawing_controls] != [f"ADP-{index:03d}" for index in range(1, 11)]:
            errors.append("adapter drawing-control schedule changed")
        if any("FAI REQUIRED" not in row.get("status", "") for row in drawing_controls):
            errors.append("adapter drawing controls lost the first-article hold")
        if not any(row.get("control_id") == "ADP-006" and "SHKL-M5-20-A2-R360" in row.get("inspection", "") for row in drawing_controls):
            errors.append("countersink functional-gauge control changed")
        proof_analysis = rows(OUT / "adapter-proof-analysis.csv")
        if len(proof_analysis) != 10 or [row.get("screen_id") for row in proof_analysis] != [f"ADP-LC-{index:02d}" for index in range(1, 11)]:
            errors.append("adapter proof-analysis schedule changed")
        else:
            if any("PASS" not in row.get("result", "") for row in proof_analysis[1:]) or "QUALIFIED ACCEPTANCE OPEN" not in proof_analysis[0].get("result", ""):
                errors.append("adapter analysis lost its pass/open release boundary")
            if min(float(row["ratio"]) for row in proof_analysis[1:]) < 1.5:
                errors.append("adapter analytical screen ratio fell below 1.5")
        interface_controls = rows(OUT / "new-interface-drawing-controls.csv")
        if len(interface_controls) != 10 or [row.get("control_id") for row in interface_controls] != [f"C04-{index:03d}" for index in range(1, 6)] + [f"C05-{index:03d}" for index in range(1, 6)]:
            errors.append("new interface drawing-control schedule changed")
        if not all("REQUIRED" in row.get("status", "") for row in interface_controls):
            errors.append("new interface controls lost the FAI/fit hold")
        support_analysis = rows(OUT / "column-support-analysis.csv")
        if len(support_analysis) != 6 or [row.get("screen_id") for row in support_analysis] != [f"SUP-LC-{index:02d}" for index in range(1, 7)]:
            errors.append("column-support analysis schedule changed")
        if not any(row.get("ratio") == "SELECTION REQUIRED" and "PHYSICAL PROOF" in row.get("result", "") for row in support_analysis):
            errors.append("column-support T-slot capacity was released without physical evidence")
        feature_evidence = rows(OUT / "interface-feature-evidence.csv")
        if len(feature_evidence) != 2 or [row.get("feature_id") for row in feature_evidence] != ["FEAT-H104-001", "FEAT-S102-001"]:
            errors.append("manufacturer STEP feature evidence changed")
        if any("exact cylinder-axis subset present" not in row.get("verification", "") for row in feature_evidence):
            errors.append("manufacturer STEP feature evidence lost exact-axis verification")
        nominal = summary.get("nominal_joint_screens", {})
        if nominal.get("adapter_min_residual_below_countersink_mm") != 5.9 or nominal.get("m5_min_thread_engagement_screen_mm") != 10.0 or nominal.get("m2_5_geometric_min_protrusion_screen_mm") != 4.2:
            errors.append("adapter/fastener geometry screens changed")
        if "typical material properties are not allowables" not in nominal.get("status", ""):
            errors.append("typical material properties were promoted to allowables")
        if nominal.get("proof_screen_multiplier_on_2_25_gravity_case") != 3.0 or nominal.get("project_mtr_minimum_yield_mpa") != 240.0:
            errors.append("adapter proof/MTR acceptance boundary changed")

        sweep = rows(OUT / "collision-sweep.csv")
        expected_q1 = [-20.0 + 0.5 * index for index in range(181)]
        expected_q2 = [15.0 + 0.5 * index for index in range(221)]
        expected_pairs = [(q1, q2) for q2 in expected_q2 for q1 in expected_q1]
        actual_pairs = [(float(row["j1_deg"]), float(row["j2_internal_deg"])) for row in sweep]
        if len(sweep) != 40001 or actual_pairs != expected_pairs:
            errors.append("collision sample schedule changed")
        within_limit = [row for row in sweep if float(row["j2_internal_deg"]) <= 120.0]
        collisions = [row for row in sweep if row["result"] == "COLLISION"]
        if any(row["result"] != "PASS" or float(row["sampled_pairwise_intersection_mm3"]) > 1e-5 for row in within_limit):
            errors.append("collision occurs within the provisional 120 degree soft limit")
        if not collisions or min(float(row["j2_internal_deg"]) for row in collisions) != 122.0 or len(collisions) != 1267:
            errors.append("expected two-axis fail-closed collision boundary at J2 122 through 125 degrees changed")
        if any("conservative rotated-AABB broadphase" not in row.get("scope", "") for row in sweep):
            errors.append("collision sweep lost its conservative broadphase/exact-boolean method record")

        try:
            architecture_svg = OUT / "HR-V0_arm_architecture_candidate.svg"
            root = ET.parse(architecture_svg).getroot()
            text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("text"))
            for token in (REVISION, "NOT RELEASED", "J1-J2 = 202.5500 mm", "A00 closes candidate column/J1 geometry", "40001 sampled J1/J2 poses", "Do not fabricate"):
                if token not in text:
                    errors.append(f"readable view omits {token}")
            style = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("style"))
            if "font-size:18px" not in style or "font-size:34px" not in style:
                errors.append("architecture SVG lost its 18 px minimum body-text control")
        except ET.ParseError as exc:
            errors.append(f"readable SVG does not parse: {exc}")
        try:
            drawing_svg = OUT / "MV0-C01_adapter-candidate-drawing.svg"
            drawing_root = ET.parse(drawing_svg).getroot()
            drawing_text = " ".join(node.text or "" for node in drawing_root.iter() if node.tag.endswith("text"))
            for token in (REVISION, "OnlineMetals part 1249", "SHKL-M5-20-A2-R360", "DO NOT FABRICATE OR ENERGIZE"):
                if token not in drawing_text:
                    errors.append(f"adapter drawing omits {token}")
            drawing_style = " ".join(node.text or "" for node in drawing_root.iter() if node.tag.endswith("style"))
            if "font-size:18px" not in drawing_style or "font-size:34px" not in drawing_style:
                errors.append("adapter drawing lost its 18 px minimum body-text control")
        except ET.ParseError as exc:
            errors.append(f"adapter drawing SVG does not parse: {exc}")
        for filename, tokens in (
            ("MV0-C04_gripper-adapter-candidate-drawing.svg", (REVISION, "H104-to-20-2040", "FR12-H104K STEP", "DO NOT FABRICATE")),
            ("MV0-C05_shoulder-support-candidate-drawing.svg", (REVISION, "S102-to-40-4040", "17-8520 plus 13035", "DO NOT FABRICATE")),
        ):
            try:
                interface_root = ET.parse(OUT / filename).getroot()
                interface_text = " ".join(node.text or "" for node in interface_root.iter() if node.tag.endswith("text"))
                for token in tokens:
                    if token not in interface_text:
                        errors.append(f"{filename} omits {token}")
                interface_style = " ".join(node.text or "" for node in interface_root.iter() if node.tag.endswith("style"))
                if "font-size:18px" not in interface_style or "font-size:34px" not in interface_style:
                    errors.append(f"{filename} lost its 18 px minimum body-text control")
            except ET.ParseError as exc:
                errors.append(f"{filename} does not parse: {exc}")
        dxf_text = (OUT / "parts" / "MV0-C01_adapter-finished-profile.dxf").read_text(encoding="ascii")
        for token in ("FINISHED_PROFILE", "M2_5_CLEARANCE", "M5_CLEARANCE", "M5_COUNTERSINK_NOMINAL"):
            if token not in dxf_text:
                errors.append(f"adapter DXF omits layer {token}")
        gripper_dxf = (OUT / "parts" / "MV0-C04_gripper-adapter-finished-profile.dxf").read_text(encoding="ascii")
        for token in ("FINISHED_PROFILE", "M2_5_CLEARANCE", "M5_CLEARANCE", "M5_COUNTERSINK_NOMINAL"):
            if token not in gripper_dxf:
                errors.append(f"gripper adapter DXF omits layer {token}")
        support_dxf = (OUT / "parts" / "MV0-C05_shoulder-support-finished-profile.dxf").read_text(encoding="ascii")
        for token in ("FINISHED_PROFILE", "M2_5_CLEARANCE", "M8_CLEARANCE"):
            if token not in support_dxf:
                errors.append(f"shoulder support DXF omits layer {token}")

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
    print("Integrated A00-A07 candidate geometry; exact U.S.-orderable candidates on hold; 40,001-pose two-axis collision screen; fail-closed proof boundary")
    print("PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
