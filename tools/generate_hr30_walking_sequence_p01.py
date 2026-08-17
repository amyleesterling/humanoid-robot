"""Generate simulator-only HR-30 stand, weight-transfer, and single-step trajectories.

The output is a deterministic kinematic development candidate.  It is not a
hardware command stream, a balance proof, or authority to power or move the
robot.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

import generate_hr30_system_package_p01 as system
import generate_hr30_whole_body_pose_architecture_p01 as poses


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "walking-sequence-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "walking-sequence-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-WALKING-SEQUENCE-P0.1"
WARNING = "PRELIMINARY - SIMULATOR-ONLY KINEMATIC SEQUENCE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
DT = 0.02
ROOT_SPEED_LIMIT_M_S = 0.03


SEQUENCES = (
    {
        "sequence_id": "WS-R01",
        "title": "Right 40 mm single-step candidate",
        "swing": "R",
        "keyframes": ("P00_NEUTRAL_STAND", "P01_CROUCHED_STAND", "P02_LEFT_WEIGHT_TRANSFER", "P03_RIGHT_FOOT_LIFT", "P04_RIGHT_CAPTURE_STEP", "P08_RIGHT_TOUCHDOWN"),
        "single_support": "L",
    },
    {
        "sequence_id": "WS-L01",
        "title": "Left 40 mm single-step candidate",
        "swing": "L",
        "keyframes": ("P00_NEUTRAL_STAND", "P01_CROUCHED_STAND", "P05_RIGHT_WEIGHT_TRANSFER", "P06_LEFT_FOOT_LIFT", "P07_LEFT_CAPTURE_STEP", "P09_LEFT_TOUCHDOWN"),
        "single_support": "R",
    },
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pose_map() -> dict[str, poses.Pose]:
    return {pose.pose_id: pose for pose in poses.POSES}


def joint_value(pose: poses.Pose, joint_id: str, joint: dict) -> float:
    if joint["type"] == "prismatic":
        return pose.joint_deg.get(joint_id, 10.0) / 1000.0
    return math.radians(pose.joint_deg.get(joint_id, 0.0))


def segment_duration(start: poses.Pose, end: poses.Pose, joints: dict[str, dict]) -> float:
    required = 1.5
    for joint_id, joint in joints.items():
        delta = abs(joint_value(end, joint_id, joint) - joint_value(start, joint_id, joint))
        velocity = max(float(joint["velocity"]), 1e-9)
        required = max(required, 1.30 * 1.875 * delta / velocity)
    root_delta = math.hypot(end.root_x_m - start.root_x_m, end.root_y_m - start.root_y_m)
    required = max(required, 1.30 * 1.875 * root_delta / ROOT_SPEED_LIMIT_M_S)
    return math.ceil(required / DT) * DT


def blend(u: float) -> tuple[float, float, float]:
    s = 10.0 * u**3 - 15.0 * u**4 + 6.0 * u**5
    ds = 30.0 * u**2 - 60.0 * u**3 + 30.0 * u**4
    d2s = 60.0 * u - 180.0 * u**2 + 120.0 * u**3
    return s, ds, d2s


def interpolated_pose(start: poses.Pose, end: poses.Pose, s: float, support: tuple[str, ...]) -> poses.Pose:
    joint_ids = set(start.joint_deg) | set(end.joint_deg)
    joint_deg = {joint_id: start.joint_deg.get(joint_id, 0.0) + s * (end.joint_deg.get(joint_id, 0.0) - start.joint_deg.get(joint_id, 0.0)) for joint_id in joint_ids}
    return poses.Pose(
        f"{start.pose_id}_TO_{end.pose_id}", end.stage, end.title, end.purpose,
        start.root_x_m + s * (end.root_x_m - start.root_x_m),
        start.root_y_m + s * (end.root_y_m - start.root_y_m),
        joint_deg, support, support[0] if len(support) == 1 else "BOTH", end.expected_swing_foot,
    )


def support_for_segment(sequence: dict, segment_index: int, u: float) -> tuple[str, ...]:
    # Neutral/crouch/transfer are double support.  Lift, reach and descent are
    # single support; the landing sample alone returns to double support.
    if segment_index < 2:
        return ("L", "R")
    if segment_index == len(sequence["keyframes"]) - 2 and u >= 1.0 - 1e-12:
        return ("L", "R")
    return (sequence["single_support"],)


def link_points(link_tf: dict[str, np.ndarray], links: dict[str, dict]) -> dict[str, list[float]]:
    result = {}
    for link_id, tf in link_tf.items():
        point = (tf @ np.r_[links[link_id]["visual_xyz"], 1.0])[:3] * 1000.0
        result[link_id] = [round(float(value), 2) for value in point]
    return result


def build_trajectory() -> tuple[list[dict], list[dict], list[dict], list[dict], dict, dict]:
    _, links, joints, inertials = poses.parse_urdf()
    all_poses = pose_map()
    neutral_tf = poses.calibrated_fk(all_poses["P00_NEUTRAL_STAND"], links, joints)
    neutral_centers = {side: np.mean(poses.box_corners(neutral_tf[f"{side}_foot"], links[f"{side}_foot"]), axis=0) for side in ("L", "R")}
    sequence_rows: list[dict] = []
    keyframe_rows: list[dict] = []
    sample_rows: list[dict] = []
    joint_rows: list[dict] = []
    preview: dict[str, list[dict]] = {}
    global_stats = {"minimum_support_margin_mm": float("inf"), "minimum_swing_clearance_mm": float("inf"), "maximum_joint_velocity_ratio": 0.0}

    for sequence in SEQUENCES:
        frames = [all_poses[pose_id] for pose_id in sequence["keyframes"]]
        elapsed = 0.0
        sample_index = 0
        sequence_preview: list[dict] = []
        final_forward = 0.0
        sequence_min_margin = float("inf")
        sequence_min_clearance = float("inf")
        sequence_max_ratio = 0.0

        keyframe_rows.append({"sequence_id": sequence["sequence_id"], "keyframe_index": 0, "pose_id": frames[0].pose_id, "time_s": "0.000", "support_mode": "DOUBLE", "state": "SIMULATOR REFERENCE ONLY", "warning": WARNING})
        for segment_index, (start, end) in enumerate(zip(frames, frames[1:])):
            duration = segment_duration(start, end, joints)
            steps = int(round(duration / DT))
            for local_index in range(steps + 1):
                if segment_index and local_index == 0:
                    continue
                u = local_index / steps
                s, ds, d2s = blend(u)
                support = support_for_segment(sequence, segment_index, u)
                pose = interpolated_pose(start, end, s, support)
                link_tf = poses.calibrated_fk(pose, links, joints)
                mass, com = poses.com_for_pose(link_tf, inertials)
                support_points = []
                for side in support:
                    support_points.extend((point[0], point[1]) for point in poses.box_corners(link_tf[f"{side}_foot"], links[f"{side}_foot"], True))
                support_polygon = poses.convex_hull(support_points)
                margin = poses.signed_margin((float(com[0]), float(com[1])), support_polygon) * 1000.0
                swing = sequence["swing"]
                swing_bottom = min(point[2] for point in poses.box_corners(link_tf[f"{swing}_foot"], links[f"{swing}_foot"], True)) * 1000.0
                swing_center = np.mean(poses.box_corners(link_tf[f"{swing}_foot"], links[f"{swing}_foot"]), axis=0)
                forward = -(swing_center[1] - neutral_centers[swing][1]) * 1000.0
                root = link_tf["base_link"][:3, 3]
                time_s = elapsed + local_index * DT

                sample_rows.append({
                    "sequence_id": sequence["sequence_id"], "sample_index": sample_index, "time_s": f"{time_s:.3f}",
                    "segment_index": segment_index, "from_pose": start.pose_id, "to_pose": end.pose_id,
                    "support_mode": "DOUBLE" if len(support) == 2 else f"{support[0]} SINGLE",
                    "root_x_m": f"{root[0]:.9f}", "root_y_m": f"{root[1]:.9f}", "root_z_m": f"{root[2]:.9f}",
                    "mass_kg": f"{mass:.9f}", "com_x_mm": f"{com[0] * 1000.0:.6f}", "com_y_mm": f"{com[1] * 1000.0:.6f}", "com_z_mm": f"{com[2] * 1000.0:.6f}",
                    "support_margin_mm": f"{margin:.6f}", "swing_foot_clearance_mm": f"{swing_bottom:.6f}", "swing_foot_forward_mm": f"{forward:.6f}",
                    "execution_state": "SIMULATOR-ONLY REFERENCE - NOT A HARDWARE COMMAND", "warning": WARNING,
                })

                max_ratio_this_sample = 0.0
                for joint_id, joint in sorted(joints.items()):
                    q0 = joint_value(start, joint_id, joint)
                    q1 = joint_value(end, joint_id, joint)
                    delta = q1 - q0
                    q = q0 + s * delta
                    qd = ds * delta / duration
                    qdd = d2s * delta / duration**2
                    ratio = abs(qd) / max(float(joint["velocity"]), 1e-12)
                    max_ratio_this_sample = max(max_ratio_this_sample, ratio)
                    joint_rows.append({
                        "sequence_id": sequence["sequence_id"], "sample_index": sample_index, "time_s": f"{time_s:.3f}",
                        "joint_id": joint_id, "position_si": f"{q:.9f}", "velocity_si_s": f"{qd:.9f}", "acceleration_si_s2": f"{qdd:.9f}",
                        "unit": "m" if joint["type"] == "prismatic" else "rad", "urdf_velocity_limit_si_s": f"{float(joint['velocity']):.9f}",
                        "velocity_limit_ratio": f"{ratio:.9f}", "execution_state": "SIMULATOR-ONLY REFERENCE", "warning": WARNING,
                    })

                sequence_min_margin = min(sequence_min_margin, margin)
                sequence_min_clearance = min(sequence_min_clearance, swing_bottom)
                sequence_max_ratio = max(sequence_max_ratio, max_ratio_this_sample)
                final_forward = forward
                if sample_index % 5 == 0 or local_index == steps:
                    sequence_preview.append({
                        "sample": sample_index, "time": round(time_s, 2), "margin": round(margin, 2), "clearance": round(swing_bottom, 2),
                        "forward": round(forward, 2), "support": "D" if len(support) == 2 else support[0], "com": [round(float(com[0] * 1000.0), 2), round(float(com[1] * 1000.0), 2), round(float(com[2] * 1000.0), 2)],
                        "links": link_points(link_tf, links),
                    })
                sample_index += 1
            elapsed += duration
            keyframe_rows.append({"sequence_id": sequence["sequence_id"], "keyframe_index": segment_index + 1, "pose_id": end.pose_id, "time_s": f"{elapsed:.3f}", "support_mode": "DOUBLE" if len(end.support_feet) == 2 else f"{end.support_feet[0]} SINGLE", "state": "SIMULATOR REFERENCE ONLY", "warning": WARNING})

        sequence_rows.append({
            "sequence_id": sequence["sequence_id"], "title": sequence["title"], "swing_foot": sequence["swing"],
            "keyframe_count": len(frames), "sample_rate_hz": int(round(1.0 / DT)), "sample_count": sample_index,
            "duration_s": f"{elapsed:.3f}", "minimum_support_margin_mm": f"{sequence_min_margin:.6f}",
            "minimum_swing_clearance_mm": f"{sequence_min_clearance:.6f}", "final_forward_placement_mm": f"{final_forward:.6f}",
            "maximum_joint_velocity_ratio": f"{sequence_max_ratio:.9f}", "state": "KINEMATIC SIMULATOR CANDIDATE", "authority": "NO HARDWARE MOTION OR WALKING AUTHORITY", "warning": WARNING,
        })
        preview[sequence["sequence_id"]] = sequence_preview
        global_stats["minimum_support_margin_mm"] = min(global_stats["minimum_support_margin_mm"], sequence_min_margin)
        global_stats["minimum_swing_clearance_mm"] = min(global_stats["minimum_swing_clearance_mm"], sequence_min_clearance)
        global_stats["maximum_joint_velocity_ratio"] = max(global_stats["maximum_joint_velocity_ratio"], sequence_max_ratio)

    return sequence_rows, keyframe_rows, sample_rows, joint_rows, preview, global_stats


def write_mjcf_keyframes(keyframe_rows: list[dict]) -> int:
    all_poses = pose_map()
    _, links, joints, _ = poses.parse_urdf()
    source = BODY / "hr30_tether.xml"
    root = ET.parse(source).getroot()
    # MuJoCo may include an unnamed root/free joint. Only named hinge joints
    # belong to the authoritative 25-axis actuator order.
    mjcf_joint_order = [node.attrib["name"] for node in root.findall(".//joint") if node.attrib.get("name")]
    if len(mjcf_joint_order) != 25 or set(mjcf_joint_order) != set(joints):
        raise RuntimeError("MJCF joint order does not match the authoritative 25-axis model")
    keys = []
    for row in keyframe_rows:
        pose = all_poses[row["pose_id"]]
        link_tf = poses.calibrated_fk(pose, links, joints)
        xyz = link_tf["base_link"][:3, 3].tolist()
        qpos = xyz + [1.0, 0.0, 0.0, 0.0] + [joint_value(pose, joint_id, joints[joint_id]) for joint_id in mjcf_joint_order]
        if len(qpos) != 32:
            raise RuntimeError("unexpected MJCF qpos width")
        keys.append(f'    <key name="{row["sequence_id"]}_{int(row["keyframe_index"]):02d}_{row["pose_id"]}" qpos="{" ".join(f"{value:.9f}" for value in qpos)}" />')
    text = source.read_text(encoding="utf-8")
    block = "  <keyframe>\n" + "\n".join(keys) + "\n  </keyframe>\n"
    if "</mujoco>" not in text:
        raise RuntimeError("invalid source MJCF")
    (OUT / "hr30_tether_walking_keyframes.xml").write_text(text.replace("</mujoco>", block + "</mujoco>"), encoding="utf-8", newline="\n")
    return len(keys)


def render_page(sequence_rows: list[dict]) -> None:
    cards = "".join(
        f'<article><h3>{html.escape(row["title"])}</h3><p><strong>{row["duration_s"]} s</strong> · {row["sample_count"]} samples · minimum modeled support margin {float(row["minimum_support_margin_mm"]):.1f} mm · final placement {float(row["final_forward_placement_mm"]):.1f} mm.</p></article>'
        for row in sequence_rows
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 walking sequence P0.1</title><script type="module" src="../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--line:#9acfe8;--ink:#142a40}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main{{max-width:1280px;margin:auto;padding:28px 20px}}header{{max-width:none;background:var(--deep);color:white}}header>div{{max-width:1280px;margin:auto}}h1{{font-size:clamp(38px,6vw,72px);line-height:1.02;margin:.25em 0}}h2{{font-size:clamp(28px,4vw,44px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}article,.panel,.sim{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0;box-shadow:0 3px 0 #c3e2f1}}model-viewer{{display:block;width:100%;height:520px;background:radial-gradient(circle,#fff,var(--paper));border-radius:12px}}label,select,input{{font:inherit}}select{{padding:10px;border:2px solid var(--blue);border-radius:9px}}input[type=range]{{width:100%}}.views{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}svg{{width:100%;height:520px;background:#f8fcff;border:1px solid var(--line);border-radius:10px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}}.metrics p{{margin:0;background:#e7f6fd;padding:10px;border-radius:8px}}a{{color:#075b9b;font-weight:800}}code{{overflow-wrap:anywhere}}small{{font-size:14px}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}.views{{grid-template-columns:1fr}}svg{{height:420px}}model-viewer{{height:430px}}}}</style></head><body><header><div><div class="warning">{WARNING}</div><h1>Two feet now have timed, grounded step candidates.</h1><p>Scrub the complete 25-axis tether-first robot through a minimum-jerk right or left 40 mm step. This is executable simulator data, never a hardware command.</p></div></header><main><section class="sim"><h2>Interactive whole-body sequence</h2><p><label for="sequence"><strong>Sequence:</strong></label> <select id="sequence">{''.join(f'<option value="{row["sequence_id"]}">{html.escape(row["title"])}</option>' for row in sequence_rows)}</select></p><input id="scrub" type="range" min="0" max="1" step="1" value="0" aria-label="Trajectory frame"><div class="metrics"><p><strong id="time">0.00 s</strong><br>time</p><p><strong id="margin">—</strong><br>COM support margin</p><p><strong id="clearance">—</strong><br>swing clearance</p><p><strong id="forward">—</strong><br>foot placement</p><p><strong id="support">—</strong><br>declared contact</p></div><div class="views"><div><h3>Front</h3><svg id="front" viewBox="-240 -780 480 800" aria-label="Animated front-view whole-body skeleton"></svg></div><div><h3>Side</h3><svg id="side" viewBox="-220 -780 440 800" aria-label="Animated side-view whole-body skeleton"></svg></div></div></section><section><h2>Sequence inventory</h2><div class="grid">{cards}</div></section><section class="panel"><h2>Inspect the articulated source model</h2><model-viewer src="../HR-30_whole_body_pose_lineup_candidate.glb" alt="Interactive lineup of ten preliminary HR-30 standing stepping and touchdown poses" camera-controls camera-orbit="32deg 74deg 110%" field-of-view="28deg" shadow-intensity="0.8"></model-viewer></section><section class="panel"><h2>Machine-readable handoff</h2><p><a href="trajectory-sequence-register.csv">sequence register</a> · <a href="trajectory-keyframe-register.csv">keyframes</a> · <a href="trajectory-samples.csv">50 Hz base/COM/contact samples</a> · <a href="joint-trajectory.csv">25-axis positions, velocities and accelerations</a> · <a href="hr30_tether_walking_keyframes.xml">loadable tether MJCF keyframes</a> · <a href="trajectory-preview.json">preview data</a></p><p>The CSV and MJCF artifacts are simulator inputs only. They are intentionally not encoded as DYNAMIXEL packets, firmware commands, ROS control messages, or actuator IDs.</p></section><section class="panel"><h2>What this does not prove</h2><p>Minimum-jerk interpolation and a positive projected-COM margin do not prove balance, contact force, zero-moment point, capture point, actuator capacity, current demand, thermal performance, floor contact, foot friction, backlash, compliance, tracking, collision clearance, restraint behavior, stopping distance, or recovery. The robot may not execute these trajectories until physical characterization and qualified release close the corresponding gates.</p></section></main><script>const parents={json.dumps({joint['child']: joint['parent'] for joint in poses.parse_urdf()[2].values()})};const data=await fetch('trajectory-preview.json').then(r=>r.json());const select=document.getElementById('sequence'),scrub=document.getElementById('scrub');function draw(svg,frame,axes){{const pts=frame.links;const lines=Object.entries(parents).filter(([c,p])=>pts[c]&&pts[p]).map(([c,p])=>`<line x1="${{pts[p][axes[0]]}}" y1="${{-pts[p][2]}}" x2="${{pts[c][axes[0]]}}" y2="${{-pts[c][2]}}" stroke="#0b4f91" stroke-width="7" stroke-linecap="round"/>`).join('');const joints=Object.values(pts).map(v=>`<circle cx="${{v[axes[0]]}}" cy="${{-v[2]}}" r="5" fill="#f2b91d" stroke="#071d36" stroke-width="2"/>`).join('');const comAxis=axes[0]===0?frame.com[0]:-frame.com[1];svg.innerHTML=`<line x1="-200" y1="0" x2="200" y2="0" stroke="#173c5e" stroke-width="3"/>${{lines}}${{joints}}<circle cx="${{comAxis}}" cy="${{-frame.com[2]}}" r="9" fill="#c82828"/><text x="${{comAxis+12}}" y="${{-frame.com[2]+5}}" font-size="16" fill="#8b1111">COM</text>`}}function update(){{const frames=data[select.value],i=Math.min(+scrub.value,frames.length-1),f=frames[i];scrub.max=frames.length-1;document.getElementById('time').textContent=f.time.toFixed(2)+' s';document.getElementById('margin').textContent=f.margin.toFixed(1)+' mm';document.getElementById('clearance').textContent=f.clearance.toFixed(1)+' mm';document.getElementById('forward').textContent=f.forward.toFixed(1)+' mm';document.getElementById('support').textContent=f.support==='D'?'double':f.support+' single';draw(document.getElementById('front'),f,[0,2]);draw(document.getElementById('side'),f,[1,2])}}select.addEventListener('change',()=>{{scrub.value=0;update()}});scrub.addEventListener('input',update);update();</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")


def replace_marked(path: Path, start: str, end: str, block: str, before: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text[:text.index(start)] + block + text[text.index(end) + len(end):]
    elif before and before in text:
        text = text.replace(before, block + "\n" + before, 1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_manifest() -> None:
    rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sequence_rows, keyframe_rows, sample_rows, joint_rows, preview, stats = build_trajectory()
    if stats["minimum_support_margin_mm"] <= 0.0:
        raise RuntimeError("a trajectory sample leaves its declared support polygon")
    if stats["minimum_swing_clearance_mm"] < -0.02:
        raise RuntimeError("a trajectory sample penetrates the floor")
    if stats["maximum_joint_velocity_ratio"] > 1.0 + 1e-9:
        raise RuntimeError("a trajectory sample exceeds a URDF velocity limit")

    write_csv(OUT / "trajectory-sequence-register.csv", sequence_rows)
    write_csv(OUT / "trajectory-keyframe-register.csv", keyframe_rows)
    write_csv(OUT / "trajectory-samples.csv", sample_rows)
    write_csv(OUT / "joint-trajectory.csv", joint_rows)
    (OUT / "trajectory-preview.json").write_text(json.dumps(preview, separators=(",", ":")) + "\n", encoding="utf-8")
    mjcf_key_count = write_mjcf_keyframes(keyframe_rows)
    source_rows = []
    for role, path in (
        ("active tether URDF", BODY / "hr30_tether.urdf"), ("active tether MJCF", BODY / "hr30_tether.xml"),
        ("pose register", BODY / "whole-body-pose-register.csv"), ("pose targets", BODY / "pose-joint-targets.csv"),
        ("pose metrics", BODY / "pose-support-metrics.csv"), ("pose generator", ROOT / "tools" / "generate_hr30_whole_body_pose_architecture_p01.py"),
    ):
        source_rows.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING})
    write_csv(OUT / "source-binding.csv", source_rows)
    holds = [
        ("WS-H01", "continuous self-collision and tolerance-aware cable/cover clearance not evaluated"),
        ("WS-H02", "contact-force distribution, ZMP, capture point, friction and compliance not modeled"),
        ("WS-H03", "actuator torque/current/thermal capability and tracking error not validated"),
        ("WS-H04", "foot sensors, IMU, state estimator and floor geometry not physically characterized"),
        ("WS-H05", "fall-restraint force, geometry and stopping envelope not selected or tested"),
        ("WS-H06", "power-loss, bus-loss, watchdog and emergency-stop behavior not correlated to motion"),
        ("WS-H07", "no received robot has executed any trajectory sample"),
        ("WS-H08", "qualified controls, mechanical, electrical and functional-safety review remains open"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": hold_id, "unresolved": text, "state": "OPEN", "authority": "BLOCKS HARDWARE MOTION AND WALKING", "warning": WARNING} for hold_id, text in holds])
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "dynamics_source": "hr30_tether.urdf", "dynamics_mass_kg": 9.958224,
        "sequence_count": len(sequence_rows), "keyframe_count": len(keyframe_rows), "sample_rate_hz": 50,
        "sample_count": len(sample_rows), "joint_sample_count": len(joint_rows), "mjcf_keyframe_count": mjcf_key_count,
        "minimum_support_margin_mm": stats["minimum_support_margin_mm"], "minimum_swing_clearance_mm": stats["minimum_swing_clearance_mm"],
        "maximum_joint_velocity_ratio": stats["maximum_joint_velocity_ratio"], "bilateral_40mm_touchdown_present": True,
        "simulator_reference_present": True, "hardware_command_encoding_present": False, "continuous_collision_validated": False,
        "balance_validated": False, "actuator_capacity_validated": False, "physical_execution_count": 0,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "walking_authority": False, "energization_authority": False,
    }
    (OUT / "walking-sequence-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(__file__, OUT / "walking-sequence-source.py")
    render_page(sequence_rows)
    readme = f"""# HR-30 whole-body walking sequence P0.1

**{WARNING}**

This package converts the active 9.958 kg tether-first whole-body model into two complete 50 Hz minimum-jerk step candidates. Each sequence begins in neutral double support, crouches, transfers weight, lifts one foot, reaches a 40 mm capture-step target and ends in a nominally flat double-support touchdown. All 25 joint positions, velocities and accelerations are present at every sample, and the exact keyframes are loadable in the tether MJCF model.

The web guide animates the entire body from the generated link transforms. It is an engineering visualization and simulator handoff, not a motion-control interface. No DYNAMIXEL packet, actuator ID, torque-enable request or firmware command is emitted.

Positive projected-COM margin and in-limit interpolation are narrow kinematic screens. They do not establish dynamic balance, actuator capability, contact behavior, tracking, collision clearance, fall restraint, stopping, recovery or safety.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    write_manifest()

    start, end = "<!-- HR30-WALKING-SEQUENCE-P01-START -->", "<!-- HR30-WALKING-SEQUENCE-P01-END -->"
    readme_block = f'''{start}
## Timed whole-body walking sequence P0.1

The [interactive walking-sequence guide](walking-sequence-p0.1/index.html) binds the active 9.958 kg tether-first URDF/MJCF to two bilateral 50 Hz minimum-jerk step candidates. Each trajectory ends with both feet nominally flat and one foot advanced 40 mm; all 25 joint positions, velocities and accelerations are exported. The data is simulator-only and carries no hardware motion or walking authority.
{end}'''
    replace_marked(BODY / "README.md", start, end, readme_block)
    web_block = f'''{start}<section class="panel" id="walking-sequence"><h2>Scrub the first complete timed steps</h2><p>The active tether-first model now has bilateral 50 Hz minimum-jerk sequences from neutral stand through a grounded 40 mm touchdown. <a href="walking-sequence-p0.1/index.html">Open the interactive whole-body walking-sequence guide.</a> Simulator data is not a hardware command or motion authority.</p></section>{end}'''
    replace_marked(BODY / "index.html", start, end, web_block, "</main>")
    package_status_path = BODY / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({
        "whole_body_walking_sequence_present": True, "walking_sequence_count": len(sequence_rows),
        "walking_sequence_sample_count": len(sample_rows), "walking_sequence_dynamics_source": "hr30_tether.urdf",
        "bilateral_grounded_touchdown_present": True, "walking_sequence_physically_validated": False,
    })
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
