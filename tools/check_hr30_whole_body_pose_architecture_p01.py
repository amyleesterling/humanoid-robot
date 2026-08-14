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
    require(len(poses) == 5 and {row["stage"] for row in poses} == {"S2", "S3", "S4", "S5"}, "pose/stage set incomplete")
    require(len(targets) == 125 and all(row["within_urdf_limit"] == "YES" for row in targets), "25-axis pose targets incomplete or outside limits")
    require(len(metrics) == 5 and all(float(row["primary_support_margin_mm"]) > 0 for row in metrics), "projected COM leaves a declared primary support polygon")
    lift = next(row for row in metrics if row["pose_id"] == "P03_RIGHT_FOOT_LIFT")
    step = next(row for row in metrics if row["pose_id"] == "P04_RIGHT_CAPTURE_STEP")
    require(0 < float(lift["swing_foot_clearance_mm"]) <= 10.0 and abs(float(lift["swing_foot_forward_displacement_mm"])) <= 5.0, "S4 lift geometry violates the no-placement/sub-10 mm boundary")
    require(10.0 < float(step["swing_foot_clearance_mm"]) < 30.0 and 35.0 <= float(step["swing_foot_forward_displacement_mm"]) <= 50.0, "S5 step geometry outside declared development class")
    for pose in poses:
        require((SRC / pose["step_file"]).stat().st_size > 20_000 and (SRC / pose["glb_file"]).stat().st_size > 10_000, f"empty pose export: {pose['pose_id']}")
        require("NO POWERED TEST" in pose["authority"], f"pose authority overclaim: {pose['pose_id']}")
    require((SRC / "HR-30_whole_body_pose_lineup_candidate.glb").stat().st_size > 50_000, "pose lineup GLB missing")
    require(sha(SRC / "pose-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_pose_architecture_p01.py"), "pose generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    walking = (SRC / "walking-development-architecture.md").read_text(encoding="utf-8")
    require(page.count('id="walking-poses"') == 1 and "HR-30_whole_body_pose_lineup_candidate.glb" in page, "interactive pose guide missing")
    require("## Articulated P0.1 pose set" in walking and "â€”" not in walking, "walking pose section missing or mojibake retained")
    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_pose_architecture_present"] and status["whole_body_pose_count"] == 5 and status["pose_support_geometry_screen_complete"], "pose package status incomplete")
    require(not any(status[key] for key in ("pose_trajectory_validated", "quasistatic_balance_validated", "dynamic_walking_validated", "motion_authority", "energization_authority")), "pose validation/authority overclaim")
    for name in ("whole-body-pose-register.csv", "pose-joint-targets.csv", "pose-support-metrics.csv", "walking-pose-architecture.md", "HR-30_whole_body_pose_lineup_candidate.glb"):
        require((REL / name).exists() and sha(SRC / name) == sha(REL / name), f"release pose artifact drift: {name}")
    print(f"PASS: HR-30 has five complete articulated whole-body S2-S5 pose candidates and 125 in-limit joint targets; projected support margins remain positive, S4 lift is {float(lift['swing_foot_clearance_mm']):.1f} mm, S5 placement is {float(step['swing_foot_forward_displacement_mm']):.1f} mm; no balance, motion, or safety credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
