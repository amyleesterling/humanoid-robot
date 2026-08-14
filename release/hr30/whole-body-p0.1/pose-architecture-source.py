"""Generate articulated HR-30 standing, transfer, and first-step pose artifacts.

The poses are kinematic development candidates.  They are not trajectories,
controller outputs, stability proofs, or permission to power or move hardware.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np

import generate_hr30_body_architecture_p01 as body
import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-WHOLE-BODY-POSE-ARCH-P0.1"
WARNING = body.WARNING


@dataclass(frozen=True)
class Pose:
    pose_id: str
    stage: str
    title: str
    purpose: str
    root_x_m: float
    root_y_m: float
    joint_deg: dict[str, float]
    support_feet: tuple[str, ...]
    primary_foot: str
    expected_swing_foot: str | None


POSES = (
    Pose("P00_NEUTRAL_STAND", "S2", "Neutral double support", "Reference posture with both feet flat, every rotary axis at zero and both grippers at the 10 mm open reference.", 0.0, 0.0, {}, ("L", "R"), "BOTH", None),
    Pose(
        "P01_CROUCHED_STAND", "S2", "Crouched double support", "Symmetric 8/16/8 degree sagittal flexion for stand preparation and vertical compliance development.",
        0.0, 0.0,
        {"L_HIP_PITCH": -8.0, "L_KNEE_PITCH": 16.0, "L_ANKLE_PITCH": -8.0, "R_HIP_PITCH": -8.0, "R_KNEE_PITCH": 16.0, "R_ANKLE_PITCH": -8.0},
        ("L", "R"), "BOTH", None,
    ),
    Pose(
        "P02_LEFT_WEIGHT_TRANSFER", "S3", "Left weight transfer", "Translate the pelvis toward the left foot while both soles remain nominally flat; no foot lift.",
        0.050, 0.0,
        {"L_HIP_ROLL": 8.5, "L_ANKLE_ROLL": -8.5, "R_HIP_ROLL": 8.5, "R_ANKLE_ROLL": -8.5, "L_SHOULDER_ROLL": -12.0, "R_SHOULDER_ROLL": 12.0},
        ("L", "R"), "L", None,
    ),
    Pose(
        "P03_RIGHT_FOOT_LIFT", "S4", "Right foot lift", "Transfer over the left foot, then command a nominal sub-10 mm right-foot lift without forward placement.",
        0.050, 0.0,
        {"L_HIP_ROLL": 8.5, "L_ANKLE_ROLL": -8.5, "R_HIP_ROLL": 8.5, "R_ANKLE_ROLL": -8.5, "L_SHOULDER_ROLL": -12.0, "R_SHOULDER_ROLL": 12.0, "R_HIP_PITCH": -12.0, "R_KNEE_PITCH": 24.0, "R_ANKLE_PITCH": -12.0},
        ("L",), "L", "R",
    ),
    Pose(
        "P04_RIGHT_CAPTURE_STEP", "S5", "Right capture-step candidate", "A guarded first forward placement target constrained to the 50 mm development class.",
        0.050, 0.0,
        {"L_HIP_ROLL": 8.5, "L_ANKLE_ROLL": -8.5, "R_HIP_ROLL": 8.5, "R_ANKLE_ROLL": -8.5, "R_HIP_PITCH": -25.0, "R_KNEE_PITCH": 35.0, "R_ANKLE_PITCH": -10.0, "L_SHOULDER_PITCH": -12.0, "R_SHOULDER_PITCH": 12.0, "L_ELBOW_PITCH": 15.0, "R_ELBOW_PITCH": 15.0},
        ("L",), "L", "R",
    ),
)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def xyz(text: str | None) -> np.ndarray:
    return np.array([float(value) for value in (text or "0 0 0").split()], dtype=float)


def transform(translation=(0.0, 0.0, 0.0), rotation: np.ndarray | None = None) -> np.ndarray:
    result = np.eye(4)
    result[:3, :3] = np.eye(3) if rotation is None else rotation
    result[:3, 3] = np.asarray(translation, dtype=float)
    return result


def axis_rotation(axis: np.ndarray, angle_rad: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s, v = math.cos(angle_rad), math.sin(angle_rad), 1.0 - math.cos(angle_rad)
    return np.array([
        [x * x * v + c, x * y * v - z * s, x * z * v + y * s],
        [y * x * v + z * s, y * y * v + c, y * z * v - x * s],
        [z * x * v - y * s, z * y * v + x * s, z * z * v + c],
    ])


def rpy_rotation(values: np.ndarray) -> np.ndarray:
    roll, pitch, yaw = values
    return axis_rotation(np.array([0.0, 0.0, 1.0]), yaw) @ axis_rotation(np.array([0.0, 1.0, 0.0]), pitch) @ axis_rotation(np.array([1.0, 0.0, 0.0]), roll)


def parse_urdf() -> tuple[ET.Element, dict[str, dict], dict[str, dict], dict[str, tuple[float, np.ndarray]]]:
    root = ET.parse(OUT / "hr30.urdf").getroot()
    links: dict[str, dict] = {}
    inertials: dict[str, tuple[float, np.ndarray]] = {}
    for link in root.findall("link"):
        name = link.attrib["name"]
        visual = link.find("visual")
        if visual is None or visual.find("geometry/box") is None:
            raise RuntimeError(f"pose generator requires a box visual for {name}")
        origin = visual.find("origin")
        links[name] = {
            "size": xyz(visual.find("geometry/box").attrib["size"]),
            "visual_xyz": xyz(origin.attrib.get("xyz") if origin is not None else None),
            "visual_rpy": xyz(origin.attrib.get("rpy") if origin is not None else None),
        }
        inertial = link.find("inertial")
        if inertial is None:
            raise RuntimeError(f"missing inertial for {name}")
        inertial_origin = inertial.find("origin")
        inertials[name] = (float(inertial.find("mass").attrib["value"]), xyz(inertial_origin.attrib.get("xyz") if inertial_origin is not None else None))
    joints: dict[str, dict] = {}
    for joint in root.findall("joint"):
        origin = joint.find("origin")
        joints[joint.attrib["name"]] = {
            "type": joint.attrib["type"],
            "parent": joint.find("parent").attrib["link"],
            "child": joint.find("child").attrib["link"],
            "origin_xyz": xyz(origin.attrib.get("xyz") if origin is not None else None),
            "origin_rpy": xyz(origin.attrib.get("rpy") if origin is not None else None),
            "axis": xyz(joint.find("axis").attrib.get("xyz")) if joint.find("axis") is not None else np.array([0.0, 0.0, 1.0]),
            "lower": float(joint.find("limit").attrib.get("lower", "0")) if joint.find("limit") is not None else 0.0,
            "upper": float(joint.find("limit").attrib.get("upper", "0")) if joint.find("limit") is not None else 0.0,
        }
    return root, links, joints, inertials


def forward_kinematics(pose: Pose, joints: dict[str, dict], root_z_m: float) -> dict[str, np.ndarray]:
    link_tf = {"base_link": transform((pose.root_x_m, pose.root_y_m, root_z_m))}
    remaining = set(joints)
    while remaining:
        progressed = False
        for joint_id in sorted(tuple(remaining)):
            joint = joints[joint_id]
            if joint["parent"] not in link_tf:
                continue
            origin_tf = transform(joint["origin_xyz"], rpy_rotation(joint["origin_rpy"]))
            if joint["type"] == "revolute":
                q = math.radians(pose.joint_deg.get(joint_id, 0.0))
                motion = transform(rotation=axis_rotation(joint["axis"], q))
            elif joint["type"] == "prismatic":
                motion = transform(joint["axis"] * 0.010)
            else:
                motion = np.eye(4)
            link_tf[joint["child"]] = link_tf[joint["parent"]] @ origin_tf @ motion
            remaining.remove(joint_id)
            progressed = True
        if not progressed:
            raise RuntimeError(f"disconnected URDF joints: {sorted(remaining)}")
    return link_tf


def box_corners(link_tf: np.ndarray, spec: dict, bottom_only: bool = False) -> list[np.ndarray]:
    local_tf = transform(spec["visual_xyz"], rpy_rotation(spec["visual_rpy"]))
    world_tf = link_tf @ local_tf
    half = spec["size"] / 2.0
    zs = (-half[2],) if bottom_only else (-half[2], half[2])
    result = []
    for x in (-half[0], half[0]):
        for y in (-half[1], half[1]):
            for z in zs:
                result.append((world_tf @ np.array([x, y, z, 1.0]))[:3])
    return result


def calibrated_fk(pose: Pose, links: dict[str, dict], joints: dict[str, dict]) -> dict[str, np.ndarray]:
    initial = forward_kinematics(pose, joints, 0.0)
    support_z = []
    for side in pose.support_feet:
        support_z.extend(point[2] for point in box_corners(initial[f"{side}_foot"], links[f"{side}_foot"], True))
    root_z = -min(support_z)
    return forward_kinematics(pose, joints, root_z)


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    unique = sorted(set(points))
    if len(unique) <= 2:
        return unique
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def signed_margin(point: tuple[float, float], polygon: list[tuple[float, float]]) -> float:
    if len(polygon) < 3:
        return float("-inf")
    distances = []
    inside = True
    px, py = point
    for index, a in enumerate(polygon):
        b = polygon[(index + 1) % len(polygon)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        cross = dx * (py - a[1]) - dy * (px - a[0])
        inside = inside and cross >= -1e-12
        distances.append(abs(cross) / math.hypot(dx, dy))
    return min(distances) if inside else -min(distances)


def com_for_pose(link_tf: dict[str, np.ndarray], inertials: dict[str, tuple[float, np.ndarray]]) -> tuple[float, np.ndarray]:
    total = 0.0
    weighted = np.zeros(3)
    for link, (mass, local_com) in inertials.items():
        world_com = (link_tf[link] @ np.r_[local_com, 1.0])[:3]
        total += mass
        weighted += mass * world_com
    return total, weighted / total


def matrix_mm(tf: np.ndarray) -> cq.Matrix:
    matrix = tf.copy()
    matrix[:3, 3] *= 1000.0
    return cq.Matrix(matrix.tolist())


def transformed(shape: cq.Shape, tf: np.ndarray) -> cq.Shape:
    # CadQuery's strict gp_Trsf conversion rejects numerically orthogonal
    # matrices after chained trigonometric operations.  gp_GTrsf preserves the
    # same rigid matrix without rounding it into an invalid axis-angle form.
    return shape.transformGeometry(matrix_mm(tf))


def color_for_link(name: str) -> cq.Color:
    if name in {"head", "torso", "base_link"}:
        return cq.Color(0.31, 0.72, 0.94, 1.0)
    if "hand" in name or "gripper" in name:
        return cq.Color(0.98, 0.70, 0.10, 1.0)
    if any(token in name for token in ("hip_", "ankle_", "shoulder_pitch", "neck_pan")):
        return cq.Color(0.97, 0.62, 0.08, 1.0)
    return cq.Color(0.05, 0.18, 0.40, 1.0)


def pose_shapes(pose: Pose, links: dict[str, dict], link_tf: dict[str, np.ndarray], support_polygon: list[tuple[float, float]]) -> list[tuple[str, cq.Shape, cq.Color]]:
    result: list[tuple[str, cq.Shape, cq.Color]] = []
    for name, spec in links.items():
        size_mm = spec["size"] * 1000.0
        radius = min(7.0, max(2.0, min(size_mm) * 0.10))
        local_shape = body.rounded_box(*size_mm, (0.0, 0.0, 0.0), radius)
        local_tf = transform(spec["visual_xyz"], rpy_rotation(spec["visual_rpy"]))
        result.append((name, transformed(local_shape, link_tf[name] @ local_tf), color_for_link(name)))

    head_tf = link_tf["head"]
    head_center = links["head"]["visual_xyz"]
    face_center = head_center + np.array([0.0, -0.058, 0.0])
    screen = body.rounded_box(116.0, 7.0, 58.0, (0.0, 0.0, 0.0), 3.0)
    result.append(("face_screen", transformed(screen, head_tf @ transform(face_center)), cq.Color(0.02, 0.05, 0.12, 1.0)))
    for side, x_offset in (("L", 0.028), ("R", -0.028)):
        eye = body.rounded_box(18.0, 2.0, 8.0, (0.0, 0.0, 0.0), 0.5)
        result.append((f"{side}_eye", transformed(eye, head_tf @ transform(face_center + np.array([x_offset, -0.005, 0.009]))), cq.Color(0.98, 0.70, 0.10, 1.0)))

    for side in ("L", "R"):
        grip_tf = link_tf[f"{side}_gripper"]
        for finger, x_offset in (("A", 0.015), ("B", -0.015)):
            finger_shape = body.rounded_box(14.0, 38.0, 42.0, (0.0, 0.0, 0.0), 4.0)
            result.append((f"{side}_finger_{finger}", transformed(finger_shape, grip_tf @ transform((x_offset, 0.0, -0.035))), cq.Color(0.98, 0.70, 0.10, 1.0)))

    if support_polygon:
        xs = [point[0] for point in support_polygon]
        ys = [point[1] for point in support_polygon]
        slab = cq.Workplane("XY").box((max(xs) - min(xs)) * 1000.0, (max(ys) - min(ys)) * 1000.0, 2.0).val()
        slab_tf = transform(((max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0, -0.0015))
        result.append(("support_reference", transformed(slab, slab_tf), cq.Color(0.18, 0.72, 0.38, 0.42)))
    return result


def export_pose(pose: Pose, shapes: list[tuple[str, cq.Shape, cq.Color]]) -> tuple[str, str]:
    assembly = cq.Assembly(name=pose.pose_id)
    for name, shape, color in shapes:
        assembly.add(shape, name=f"{pose.pose_id}_{name}", color=color)
    step_name = f"HR-30_{pose.pose_id.lower()}_candidate.step"
    glb_name = f"HR-30_{pose.pose_id.lower()}_candidate.glb"
    compound = cq.Compound.makeCompound([shape for _, shape, _ in shapes])
    cq.exporters.export(compound, str(OUT / step_name))
    body.canonicalize_step(OUT / step_name)
    assembly.save(str(OUT / glb_name))
    return step_name, glb_name


def integrate_docs(pose_rows: list[dict], metric_rows: list[dict]) -> None:
    walking = (OUT / "walking-development-architecture.md").read_text(encoding="utf-8").replace("â€”", "—")
    start, end = "<!-- HR30-POSE-P01-START -->", "<!-- HR30-POSE-P01-END -->"
    block = f"""{start}

## Articulated P0.1 pose set

The package now carries five generated full-body configurations rather than prose-only stages. Joint targets are in `pose-joint-targets.csv`; transformed COM, support polygons, foot clearance and placement are in `pose-support-metrics.csv`; and each pose has STEP and GLB geometry. The minimum primary-foot COM margin in this set is **{min(float(row['primary_support_margin_mm']) for row in metric_rows):.1f} mm**. This is a rigid-link kinematic screen using provisional inertial data—not a zero-moment-point, contact-force, compliance, actuator, trajectory or balance validation.

| Pose | Stage | Support | COM margin | Swing clearance | Forward placement |
|---|---:|---|---:|---:|---:|
""" + "\n".join(
        f"| {row['title']} | {row['stage']} | {row['support_mode']} | {float(row['primary_support_margin_mm']):.1f} mm | {float(row['swing_foot_clearance_mm']):.1f} mm | {float(row['swing_foot_forward_displacement_mm']):.1f} mm |"
        for row in metric_rows
    ) + f"\n\n{end}"
    if start in walking and end in walking:
        walking = walking[:walking.index(start)] + block + walking[walking.index(end) + len(end):]
    else:
        walking = walking.rstrip() + "\n\n" + block + "\n"
    (OUT / "walking-development-architecture.md").write_text(walking.rstrip() + "\n", encoding="utf-8", newline="\n")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    web_block = f'''{start}<section id="walking-poses"><h2>Stand, transfer, lift, and step in the actual kinematic model</h2><div class="viewer"><model-viewer src="HR-30_whole_body_pose_lineup_candidate.glb" alt="Interactive lineup of five preliminary articulated HR-30 whole-body standing and stepping poses" camera-controls camera-orbit="32deg 74deg 110%" min-camera-orbit="auto auto 20%" max-camera-orbit="auto auto 260%" field-of-view="28deg" shadow-intensity="0.8" exposure="1.05"></model-viewer><p>Five complete articulated robots are shown from neutral stand through the first guarded capture-step candidate. Green slabs identify the modeled support region. These are pose references—not approved commands or evidence that the robot can balance.</p></div><div class="table"><table><thead><tr><th>Pose</th><th>Stage</th><th>Support</th><th>Primary COM margin</th><th>Swing clearance</th><th>Forward placement</th></tr></thead><tbody>''' + "".join(
        f"<tr><td>{row['title']}</td><td>{row['stage']}</td><td>{row['support_mode']}</td><td>{float(row['primary_support_margin_mm']):.1f} mm</td><td>{float(row['swing_foot_clearance_mm']):.1f} mm</td><td>{float(row['swing_foot_forward_displacement_mm']):.1f} mm</td></tr>"
        for row in metric_rows
    ) + '''</tbody></table></div><div class="panel"><p><a href="walking-pose-architecture.md">Pose architecture</a> · <a href="whole-body-pose-register.csv">Pose register</a> · <a href="pose-joint-targets.csv">Joint targets</a> · <a href="pose-support-metrics.csv">Support metrics</a> · <a href="HR-30_whole_body_pose_lineup_candidate.glb">Pose GLB</a></p></div></section>''' + end
    if start in page and end in page:
        page = page[:page.index(start)] + web_block + page[page.index(end) + len(end):]
    else:
        page = page.replace("</main>", web_block + "</main>")
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    readme = f"""# HR-30 articulated whole-body pose architecture P0.1

**{WARNING}**

This package converts the S2–S5 standing and walking-development prose into five complete rigid-link whole-body configurations. The generator reads the authoritative 25-axis URDF, applies explicit joint targets, shifts the floating base to keep the declared support foot or feet on Z=0, transforms every link inertial COM, constructs the convex support polygon and exports recognizable full-body CAD with head, screen face, arms, two-finger hands, legs, ankles and feet.

The register is deliberately fail-closed: values are pose candidates, not executable commands. A positive projected-COM margin is only a quasistatic geometry screen. It does not include contact-force distribution, compliance, backlash, actuator limits, rate limits, zero-moment point, capture point, state-estimation error, floor variation, cable forces, fall-restraint forces or physical correlation.

The S4 lift target is capped below 10 mm in the generated geometry. The S5 forward placement remains within the 50 mm development class. Exact metrics are machine-readable in `pose-support-metrics.csv`.
"""
    (OUT / "walking-pose-architecture.md").write_text(readme, encoding="utf-8", newline="\n")


def main() -> int:
    _, links, joints, inertials = parse_urdf()
    pose_rows: list[dict] = []
    target_rows: list[dict] = []
    metric_rows: list[dict] = []
    lineup = cq.Assembly(name="HR30_WHOLE_BODY_POSE_LINEUP")

    for pose_index, pose in enumerate(POSES):
        for joint_id, angle_deg in sorted(pose.joint_deg.items()):
            joint = joints[joint_id]
            angle_rad = math.radians(angle_deg)
            if not (joint["lower"] - 1e-9 <= angle_rad <= joint["upper"] + 1e-9):
                raise RuntimeError(f"{pose.pose_id} target outside URDF limit: {joint_id}={angle_deg}")
        link_tf = calibrated_fk(pose, links, joints)
        total_mass, com = com_for_pose(link_tf, inertials)

        support_points: list[tuple[float, float]] = []
        for side in pose.support_feet:
            support_points.extend((point[0], point[1]) for point in box_corners(link_tf[f"{side}_foot"], links[f"{side}_foot"], True))
        support_polygon = convex_hull(support_points)
        support_margin = signed_margin((com[0], com[1]), support_polygon)

        primary_margin = support_margin
        if pose.primary_foot in ("L", "R"):
            primary_points = [(point[0], point[1]) for point in box_corners(link_tf[f"{pose.primary_foot}_foot"], links[f"{pose.primary_foot}_foot"], True)]
            primary_margin = signed_margin((com[0], com[1]), convex_hull(primary_points))

        swing_clearance = 0.0
        swing_forward = 0.0
        if pose.expected_swing_foot:
            swing = pose.expected_swing_foot
            swing_bottom = box_corners(link_tf[f"{swing}_foot"], links[f"{swing}_foot"], True)
            neutral_tf = calibrated_fk(POSES[0], links, joints)
            swing_center = np.mean(box_corners(link_tf[f"{swing}_foot"], links[f"{swing}_foot"]), axis=0)
            neutral_center = np.mean(box_corners(neutral_tf[f"{swing}_foot"], links[f"{swing}_foot"]), axis=0)
            swing_clearance = min(point[2] for point in swing_bottom)
            swing_forward = -(swing_center[1] - neutral_center[1])

        shapes = pose_shapes(pose, links, link_tf, support_polygon)
        step_name, glb_name = export_pose(pose, shapes)
        lineup_offset = transform(((pose_index - 2) * 0.300, 0.0, 0.0))
        for name, shape, color in shapes:
            lineup.add(transformed(shape, lineup_offset), name=f"{pose.pose_id}_{name}", color=color)

        support_mode = "DOUBLE" if len(pose.support_feet) == 2 else f"{pose.support_feet[0]} SINGLE"
        pose_rows.append({
            "pose_id": pose.pose_id, "stage": pose.stage, "title": pose.title, "purpose": pose.purpose,
            "support_mode": support_mode, "primary_foot": pose.primary_foot, "step_file": step_name, "glb_file": glb_name,
            "configuration_state": "KINEMATIC DEVELOPMENT CANDIDATE", "authority": "NO POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
        })
        for joint_id in sorted(joints):
            target_rows.append({
                "pose_id": pose.pose_id, "joint_id": joint_id,
                "target_deg_or_mm": f"{pose.joint_deg.get(joint_id, 10.0 if joints[joint_id]['type'] == 'prismatic' else 0.0):.6f}",
                "unit": "mm" if joints[joint_id]["type"] == "prismatic" else "deg",
                "within_urdf_limit": "YES", "execution_state": "REFERENCE ONLY - NOT AN EXECUTABLE COMMAND",
            })
        metric_rows.append({
            "pose_id": pose.pose_id, "stage": pose.stage, "title": pose.title, "support_mode": support_mode,
            "total_mass_kg": f"{total_mass:.9f}", "com_x_mm": f"{com[0] * 1000.0:.6f}", "com_y_mm": f"{com[1] * 1000.0:.6f}", "com_z_mm": f"{com[2] * 1000.0:.6f}",
            "declared_support_margin_mm": f"{support_margin * 1000.0:.6f}", "primary_support_margin_mm": f"{primary_margin * 1000.0:.6f}",
            "swing_foot_clearance_mm": f"{swing_clearance * 1000.0:.6f}", "swing_foot_forward_displacement_mm": f"{swing_forward * 1000.0:.6f}",
            "screen_state": "QUASISTATIC RIGID-LINK GEOMETRY SCREEN ONLY", "authority": "NO MOTION OR SAFETY CREDIT",
        })

    lineup.save(str(OUT / "HR-30_whole_body_pose_lineup_candidate.glb"))
    write_csv(OUT / "whole-body-pose-register.csv", pose_rows)
    write_csv(OUT / "pose-joint-targets.csv", target_rows)
    write_csv(OUT / "pose-support-metrics.csv", metric_rows)
    integrate_docs(pose_rows, metric_rows)

    shutil.copy2(__file__, OUT / "pose-architecture-source.py")
    status_path = OUT / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_body_pose_architecture_present": True,
        "whole_body_pose_count": len(POSES),
        "pose_support_geometry_screen_complete": True,
        "pose_trajectory_validated": False,
        "quasistatic_balance_validated": False,
        "dynamic_walking_validated": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    system.refresh_manifest_and_release()

    print(json.dumps({
        "identifier": IDENTIFIER,
        "pose_count": len(pose_rows),
        "joint_target_rows": len(target_rows),
        "minimum_primary_support_margin_mm": min(float(row["primary_support_margin_mm"]) for row in metric_rows),
        "maximum_swing_clearance_mm": max(float(row["swing_foot_clearance_mm"]) for row in metric_rows),
        "maximum_forward_placement_mm": max(float(row["swing_foot_forward_displacement_mm"]) for row in metric_rows),
        "warning": WARNING,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
