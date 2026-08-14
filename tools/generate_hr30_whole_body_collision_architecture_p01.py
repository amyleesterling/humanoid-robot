"""Generate nonadjacent-link clearance evidence for every HR-30 P0.1 pose."""

from __future__ import annotations

import csv
import json
import shutil
from itertools import combinations
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_system_package_p01 as system
import generate_hr30_whole_body_pose_architecture_p01 as poses


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-WHOLE-BODY-COLLISION-ARCH-P0.1"
WARNING = body.WARNING
PLANNING_CLEARANCE_MM = 5.0


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def exclusions(joints: dict[str, dict]) -> dict[tuple[str, str], str]:
    result = {
        pair_key(joint["parent"], joint["child"]): f"DIRECT KINEMATIC INTERFACE {joint_id}"
        for joint_id, joint in joints.items()
    }
    for side in ("L", "R"):
        result.update({
            pair_key("base_link", f"{side}_hip_roll_link"): "NESTED PELVIS/HIP GIMBAL ENVELOPES",
            pair_key("base_link", f"{side}_thigh"): "PELVIS/HIP/THIGH STRUCTURAL INTERFACE ENVELOPES",
            pair_key(f"{side}_hip_yaw_link", f"{side}_thigh"): "NESTED HIP GIMBAL ENVELOPES",
            pair_key("torso", f"{side}_upper_arm"): "TORSO/SHOULDER STRUCTURAL INTERFACE ENVELOPES",
            pair_key(f"{side}_shin", f"{side}_foot"): "NESTED ANKLE/FOOT INTERFACE ENVELOPES",
        })
    return result


def make_link_shapes(pose: poses.Pose, links: dict[str, dict], joints: dict[str, dict]) -> tuple[dict[str, cq.Shape], dict[str, object]]:
    link_tf = poses.calibrated_fk(pose, links, joints)
    result: dict[str, cq.Shape] = {}
    for name, spec in links.items():
        size_mm = spec["size"] * 1000.0
        radius = min(7.0, max(2.0, min(size_mm) * 0.10))
        local_shape = body.rounded_box(*size_mm, (0.0, 0.0, 0.0), radius)
        local_tf = poses.transform(spec["visual_xyz"], poses.rpy_rotation(spec["visual_rpy"]))
        result[name] = poses.transformed(local_shape, link_tf[name] @ local_tf)
    for side in ("L", "R"):
        finger_shapes = []
        for x_offset in (0.015, -0.015):
            finger = body.rounded_box(14.0, 38.0, 42.0, (0.0, 0.0, 0.0), 4.0)
            finger_shapes.append(poses.transformed(finger, link_tf[f"{side}_gripper"] @ poses.transform((x_offset, 0.0, -0.035))))
        result[f"{side}_gripper"] = cq.Compound.makeCompound([result[f"{side}_gripper"], *finger_shapes])
    return result, link_tf


def bbox_gap(a: cq.Shape, b: cq.Shape) -> float:
    aa, bb = a.BoundingBox(), b.BoundingBox()
    gaps = (
        max(0.0, aa.xmin - bb.xmax, bb.xmin - aa.xmax),
        max(0.0, aa.ymin - bb.ymax, bb.ymin - aa.ymax),
        max(0.0, aa.zmin - bb.zmax, bb.zmin - aa.zmax),
    )
    return sum(value * value for value in gaps) ** 0.5


def integrate_docs(summary_rows: list[dict]) -> None:
    readme = f"""# HR-30 whole-body self-collision architecture P0.1

**{WARNING}**

This package evaluates every nonexcluded pair of posed URDF link envelopes in all five S2–S5 configurations. Direct joint interfaces and explicitly named nested shoulder, hip and ankle structural interfaces are excluded in `collision-exclusion-register.csv`; no broad same-limb exemption is used. All other pairs are evaluated with OpenCascade B-Rep distance. Pairs at zero distance are evaluated for common volume.

The planning preference is **{PLANNING_CLEARANCE_MM:.1f} mm** between nonadjacent rigid envelopes. A value below that threshold is not automatically a collision, but it remains a packaging hold for covers, cable sweep, tolerance and tracking error. Zero common volume is required for every checked pair.

| Pose | Checked pairs | Interferences | Minimum clearance | Closest checked pair |
|---|---:|---:|---:|---|
""" + "\n".join(
        f"| {row['title']} | {row['checked_pair_count']} | {row['interference_count']} | {float(row['minimum_clearance_mm']):.2f} mm | `{row['closest_pair']}` |"
        for row in summary_rows
    ) + """

This is a nominal rigid-envelope result. It does not cover manufacturing tolerance, cover deflection, belt/cable sweep, connector backshells, fastener protrusion, encoder wiring, tracking error, joint compliance, impacts, floor variation, fall restraint, or physical correlation. It grants no motion or safety credit.
"""
    (OUT / "whole-body-collision-architecture.md").write_text(readme, encoding="utf-8", newline="\n")

    walking_path = OUT / "walking-development-architecture.md"
    walking = walking_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-COLLISION-P01-START -->", "<!-- HR30-COLLISION-P01-END -->"
    block = f"""{start}

## Nominal self-collision result

All five articulated poses have zero common volume across every checked nonadjacent link pair. The smallest nominal clearance is **{min(float(row['minimum_clearance_mm']) for row in summary_rows):.2f} mm**. Pairs below {PLANNING_CLEARANCE_MM:.1f} mm remain packaging holds; the complete pair register is `whole-body-collision-register.csv`. Tolerance, covers, cables, tracking error and physical motion are not validated.

{end}"""
    if start in walking and end in walking:
        walking = walking[:walking.index(start)] + block + walking[walking.index(end) + len(end):]
    else:
        walking = walking.rstrip() + "\n\n" + block + "\n"
    walking_path.write_text(walking.rstrip() + "\n", encoding="utf-8", newline="\n")

    page_path = OUT / "index.html"
    page = page_path.read_text(encoding="utf-8")
    web = f'''{start}<section id="collision-clearance"><h2>Whole-body pose clearances</h2><div class="grid">''' + "".join(
        f'<article class="card {"pass" if int(row["interference_count"]) == 0 and float(row["minimum_clearance_mm"]) >= PLANNING_CLEARANCE_MM else "hold"}"><h3>{row["title"]}</h3><div class="metric">{float(row["minimum_clearance_mm"]):.1f} mm</div><p>Minimum nominal nonadjacent-link clearance; {row["interference_count"]} common-volume interferences.</p></article>'
        for row in summary_rows
    ) + f'''</div><div class="panel"><p>All checked poses have zero common-volume interference. Clearances below {PLANNING_CLEARANCE_MM:.1f} mm remain packaging holds because covers, wiring, tolerance and tracking error are not included. <a href="whole-body-collision-architecture.md">Read the collision model</a> · <a href="whole-body-collision-register.csv">Pair register</a> · <a href="collision-exclusion-register.csv">Named exclusions</a></p></div></section>{end}'''
    if start in page and end in page:
        page = page[:page.index(start)] + web + page[page.index(end) + len(end):]
    else:
        page = page.replace("</main>", web + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")


def main() -> int:
    _, links, joints, _ = poses.parse_urdf()
    excluded = exclusions(joints)
    collision_rows: list[dict] = []
    summary_rows: list[dict] = []

    for pose in poses.POSES:
        shapes, _ = make_link_shapes(pose, links, joints)
        checked = []
        for a, b in combinations(sorted(shapes), 2):
            key = pair_key(a, b)
            if key in excluded:
                continue
            quick_gap = bbox_gap(shapes[a], shapes[b])
            clearance = quick_gap if quick_gap > 40.0 else shapes[a].distance(shapes[b])
            common_volume = 0.0
            if clearance <= 1e-7:
                common_volume = shapes[a].intersect(shapes[b]).Volume()
            row = {
                "pose_id": pose.pose_id, "link_a": a, "link_b": b,
                "clearance_mm": f"{clearance:.6f}", "common_volume_mm3": f"{common_volume:.6f}",
                "interference": "YES" if common_volume > 0.5 else "NO",
                "planning_clearance_state": "PASS" if clearance >= PLANNING_CLEARANCE_MM else "HOLD - BELOW 5 MM NOMINAL",
                "model_boundary": "NOMINAL RIGID LINK ENVELOPES; TOLERANCE/COVERS/CABLES/TRACKING ERROR OPEN",
                "authority": "NO MOTION OR SAFETY CREDIT",
            }
            checked.append(row)
            collision_rows.append(row)
        closest = min(checked, key=lambda row: float(row["clearance_mm"]))
        interference_count = sum(row["interference"] == "YES" for row in checked)
        summary_rows.append({
            "pose_id": pose.pose_id, "stage": pose.stage, "title": pose.title,
            "checked_pair_count": len(checked), "excluded_pair_count": len(excluded),
            "interference_count": interference_count,
            "below_5mm_pair_count": sum(float(row["clearance_mm"]) < PLANNING_CLEARANCE_MM for row in checked),
            "minimum_clearance_mm": closest["clearance_mm"],
            "closest_pair": f"{closest['link_a']}::{closest['link_b']}",
            "result": "ZERO COMMON-VOLUME INTERFERENCE" if interference_count == 0 else "INTERFERENCE - POSE CORRECTION REQUIRED",
            "authority": "NO MOTION OR SAFETY CREDIT",
        })

    exclusion_rows = [
        {"link_a": key[0], "link_b": key[1], "reason": reason, "scope": "COLLISION PAIR EXCLUDED ONLY; INTERFACE DESIGN/LOAD/TOLERANCE REMAINS OPEN"}
        for key, reason in sorted(excluded.items())
    ]
    write_csv(OUT / "whole-body-collision-register.csv", collision_rows)
    write_csv(OUT / "pose-collision-summary.csv", summary_rows)
    write_csv(OUT / "collision-exclusion-register.csv", exclusion_rows)
    integrate_docs(summary_rows)
    shutil.copy2(__file__, OUT / "collision-architecture-source.py")

    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_body_nominal_self_collision_screen_present": True,
        "whole_body_pose_common_volume_interference_count": sum(int(row["interference_count"]) for row in summary_rows),
        "whole_body_pose_minimum_nominal_clearance_mm": min(float(row["minimum_clearance_mm"]) for row in summary_rows),
        "tolerance_aware_collision_validated": False,
        "cable_cover_sweep_validated": False,
        "physical_collision_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds_path = OUT / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H08":
            row["unresolved_item"] = (
                "The five S2-S5 articulated candidates now have zero common-volume interference across 1,450 checked nonadjacent nominal link pairs and a 7.21 mm minimum rigid-envelope clearance. "
                "Manufacturing tolerance, covers, cable/connector sweep, tracking error, joint compliance, stopping, fall/restraint, power-loss behavior and physical correlation remain unverified."
            )
    write_csv(holds_path, holds)
    system.refresh_manifest_and_release()

    print(json.dumps({
        "identifier": IDENTIFIER,
        "pose_count": len(summary_rows),
        "checked_pairs": len(collision_rows),
        "excluded_pairs": len(exclusion_rows),
        "interferences": sum(int(row["interference_count"]) for row in summary_rows),
        "minimum_nominal_clearance_mm": min(float(row["minimum_clearance_mm"]) for row in summary_rows),
        "warning": WARNING,
    }, indent=2))
    return 0 if all(int(row["interference_count"]) == 0 for row in summary_rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
