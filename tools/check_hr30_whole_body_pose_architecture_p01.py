"""Check the articulated HR-30 P0.1 pose architecture and synchronized release."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rows(name: str) -> list[dict]:
    with (SRC / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    poses = rows("whole-body-pose-register.csv")
    targets = rows("pose-joint-targets.csv")
    metrics = rows("pose-support-metrics.csv")
    expected_pose_ids = {
        "P00_NEUTRAL_STAND", "P01_CROUCHED_STAND",
        "P02_LEFT_WEIGHT_TRANSFER", "P03_RIGHT_FOOT_LIFT", "P04_RIGHT_CAPTURE_STEP",
        "P05_RIGHT_WEIGHT_TRANSFER", "P06_LEFT_FOOT_LIFT", "P07_LEFT_CAPTURE_STEP",
        "P08_RIGHT_TOUCHDOWN", "P09_LEFT_TOUCHDOWN",
    }
    require(len(poses) == 10 and {row["pose_id"] for row in poses} == expected_pose_ids and {row["stage"] for row in poses} == {"S2", "S3", "S4", "S5"}, "bilateral pose/stage set incomplete")
    require(len(targets) == 250 and all(row["within_urdf_limit"] == "YES" for row in targets), "25-axis bilateral pose targets incomplete or outside limits")
    require(len(metrics) == 10 and all(float(row["primary_support_margin_mm"]) > 0 for row in metrics), "projected COM leaves a declared primary support polygon")
    mass_summary = json.loads((SRC / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    expected_mass = float(mass_summary["active_tether_dynamics_planning_mass_kg"])
    require(all(abs(float(row["total_mass_kg"]) - expected_mass) < 1e-6 for row in metrics), "pose metrics are not bound to the active tether-first dynamics mass")
    right_lift = next(row for row in metrics if row["pose_id"] == "P03_RIGHT_FOOT_LIFT")
    right_step = next(row for row in metrics if row["pose_id"] == "P04_RIGHT_CAPTURE_STEP")
    left_lift = next(row for row in metrics if row["pose_id"] == "P06_LEFT_FOOT_LIFT")
    left_step = next(row for row in metrics if row["pose_id"] == "P07_LEFT_CAPTURE_STEP")
    right_touchdown = next(row for row in metrics if row["pose_id"] == "P08_RIGHT_TOUCHDOWN")
    left_touchdown = next(row for row in metrics if row["pose_id"] == "P09_LEFT_TOUCHDOWN")
    for lift in (right_lift, left_lift):
        require(0 < float(lift["swing_foot_clearance_mm"]) <= 10.0 and abs(float(lift["swing_foot_forward_displacement_mm"])) <= 5.0, "S4 lift geometry violates the no-placement/sub-10 mm boundary")
    for step in (right_step, left_step):
        require(10.0 < float(step["swing_foot_clearance_mm"]) < 30.0 and 35.0 <= float(step["swing_foot_forward_displacement_mm"]) <= 50.0, "S5 step geometry outside declared development class")
    for touchdown in (right_touchdown, left_touchdown):
        require(abs(float(touchdown["swing_foot_clearance_mm"])) <= 0.01 and 39.0 <= float(touchdown["swing_foot_forward_displacement_mm"]) <= 41.0, "S5 touchdown does not place a nominally grounded foot at 40 mm")
    for pose in poses:
        require((SRC / pose["step_file"]).stat().st_size > 20_000 and (SRC / pose["glb_file"]).stat().st_size > 10_000, f"empty pose export: {pose['pose_id']}")
        require("NO POWERED TEST" in pose["authority"], f"pose authority overclaim: {pose['pose_id']}")
    require((SRC / "HR-30_whole_body_pose_lineup_candidate.glb").stat().st_size > 50_000, "pose lineup GLB missing")
    require(sha(SRC / "pose-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_pose_architecture_p01.py"), "pose generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    walking = (SRC / "walking-development-architecture.md").read_text(encoding="utf-8")
    require(page.count('id="walking-poses"') == 1 and "HR-30_whole_body_pose_lineup_candidate.glb" in page, "interactive pose guide missing")
    require("## Articulated P0.1 pose set" in walking and not any(token in walking for token in ("â", "Ã", "Â")), "walking pose section missing or mojibake retained")
    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_pose_architecture_present"] and status["whole_body_pose_count"] == 10 and status["pose_support_geometry_screen_complete"], "pose package status incomplete")
    require(status["pose_dynamics_source"] == "hr30_tether.urdf" and abs(float(status["pose_dynamics_mass_kg"]) - expected_mass) < 1e-6, "pose status does not identify the active tether-first dynamics source")
    require(not any(status[key] for key in ("pose_trajectory_validated", "quasistatic_balance_validated", "dynamic_walking_validated", "motion_authority", "energization_authority")), "pose validation/authority overclaim")
    for name in ("whole-body-pose-register.csv", "pose-joint-targets.csv", "pose-support-metrics.csv", "walking-pose-architecture.md", "HR-30_whole_body_pose_lineup_candidate.glb"):
        require((REL / name).exists() and sha(SRC / name) == sha(REL / name), f"release pose artifact drift: {name}")
    print(f"PASS: HR-30 has ten complete articulated whole-body S2-S5 pose candidates and 250 in-limit joint targets on the {expected_mass:.3f} kg tether model; projected support margins remain positive, bilateral S4 lifts are {float(right_lift['swing_foot_clearance_mm']):.1f}/{float(left_lift['swing_foot_clearance_mm']):.1f} mm, and both 40 mm S5 touchdown configurations return to double support; no balance, motion, or safety credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
