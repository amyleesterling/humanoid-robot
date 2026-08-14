"""Generate the HR-30 P0.1 whole-body mechanical interface atlas.

This is a design artifact built from the authoritative body, joint, mass,
fabrication and harness registers.  It consolidates every body module into a
dimensioned interface-control record and a web-first atlas.  It is not a
released manufacturing drawing or work authorization.
"""

from __future__ import annotations

import csv
import html
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-INTERFACE-ATLAS-P0.1"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)


MODULES = [
    {
        "id": "H01", "segment": "Head, screen face and sensor shell", "side": "C", "region": "head",
        "envelopes": ["HEAD_SHELL_ENVELOPE", "FACE_SCREEN_PANEL"], "mass_groups": ["head/display/sensing"],
        "axes": [], "actuated_by": ["HEAD_TILT"], "datum": "HEAD_TILT @ (0, 0, 690) mm",
        "upstream": "N01 tilt cradle at HEAD_TILT", "downstream": "Face screen, stereo vision, microphones and speakers",
        "route_tokens": ["HEAD_BRANCH"],
        "refinement": "Select display/cameras/audio; define bezel lands, thermal path, privacy indication, fasteners and impact-safe edges.",
    },
    {
        "id": "N01", "segment": "Two-axis articulated neck", "side": "C", "region": "neck",
        "envelopes": ["NECK_COLUMN_ENVELOPE"], "mass_groups": ["neck"],
        "axes": ["HEAD_PAN", "HEAD_TILT"], "actuated_by": [], "datum": "HEAD_PAN @ (0, 0, 650) mm",
        "upstream": "T01 shoulder crossmember / pan module", "downstream": "H01 tilt cradle",
        "route_tokens": ["HEAD_BRANCH"],
        "refinement": "Close pan/tilt stops, shaft/bearing fits, moving cable loop, head retention, backlash and neck pinch guarding.",
    },
    {
        "id": "T01", "segment": "Torso frame, compute and cooling", "side": "C", "region": "trunk",
        "envelopes": ["TORSO_SHELL_ENVELOPE", "TORSO_LEFT_FRAME_RAIL", "TORSO_RIGHT_FRAME_RAIL", "TORSO_SHOULDER_CROSSMEMBER"],
        "mass_groups": ["torso/compute/waist"], "axes": [], "actuated_by": ["WAIST_YAW"],
        "datum": "WAIST_YAW @ (0, 0, 425) mm",
        "upstream": "P01 waist bearing/output interface", "downstream": "N01 neck and A01/A02 shoulder interfaces",
        "route_tokens": ["TORSO_POWER", "TORSO_DATA", "HEAD_BRANCH"],
        "refinement": "Release rail/crossmember drawings, compute retention, airflow, battery-cassette isolation, shoulder load path and service clearances.",
    },
    {
        "id": "P01", "segment": "Pelvis, power bay and restraint bridge", "side": "C", "region": "trunk",
        "envelopes": ["PELVIS_SHELL_ENVELOPE", "PELVIS_LOAD_FRAME_ENVELOPE", "WAIST_BEARING_STACK_RESERVATION"],
        "mass_groups": ["pelvis/power"], "axes": ["WAIST_YAW"], "actuated_by": [],
        "datum": "PELVIS / WAIST datum @ Z=425 mm",
        "upstream": "L01/L02 hip-yaw modules and external fall-restraint system", "downstream": "T01 waist output",
        "route_tokens": ["TORSO_POWER", "TORSO_DATA", "LEG_POWER", "LEG_DATA"],
        "refinement": "Close hip and waist load paths, battery/PDU containment, service disconnect access, IMU datum and rated restraint interface.",
    },
    {
        "id": "A01", "segment": "Left shoulder, upper arm, elbow, forearm and wrist", "side": "L", "region": "arm",
        "envelopes": ["L_SHOULDER_HOUSING_ENVELOPE", "L_UPPER_ARM_SHELL_ENVELOPE", "L_ELBOW_HOUSING_ENVELOPE", "L_FOREARM_SHELL_ENVELOPE", "L_WRIST_HOUSING_ENVELOPE"],
        "mass_groups": ["L arm"], "axes": ["L_SHOULDER_PITCH", "L_SHOULDER_ROLL", "L_ELBOW_PITCH", "L_WRIST_ROTATION"],
        "actuated_by": [], "datum": "L_SHOULDER pair @ (105, 0, 590) mm",
        "upstream": "T01 left shoulder crossmember", "downstream": "G01 palm at L_WRIST_ROTATION",
        "route_tokens": ["L_ARM"],
        "refinement": "Close gimbal packaging, link plates, elbow/wrist shafts, stops, covers, service loops and the current arm-mass overrun.",
    },
    {
        "id": "G01", "segment": "Left hand-shaped parallel gripper", "side": "L", "region": "hand",
        "envelopes": ["L_HAND_PALM_ENVELOPE", "L_INBOARD_GRIPPER_FINGER", "L_OUTBOARD_GRIPPER_FINGER"],
        "mass_groups": ["L hand"], "axes": ["L_GRIPPER"], "actuated_by": [],
        "datum": "L_GRIPPER @ (140, 0, 252) mm", "upstream": "A01 supported wrist shaft",
        "downstream": "Two broad fingers and replaceable compliant pad lands", "route_tokens": ["L_ARM"],
        "refinement": "Select equalizer, pads, force/current limit, object sensing, mechanical end stops, retention and pinch-safe finger gaps.",
    },
    {
        "id": "A02", "segment": "Right shoulder, upper arm, elbow, forearm and wrist", "side": "R", "region": "arm",
        "envelopes": ["R_SHOULDER_HOUSING_ENVELOPE", "R_UPPER_ARM_SHELL_ENVELOPE", "R_ELBOW_HOUSING_ENVELOPE", "R_FOREARM_SHELL_ENVELOPE", "R_WRIST_HOUSING_ENVELOPE"],
        "mass_groups": ["R arm"], "axes": ["R_SHOULDER_PITCH", "R_SHOULDER_ROLL", "R_ELBOW_PITCH", "R_WRIST_ROTATION"],
        "actuated_by": [], "datum": "R_SHOULDER pair @ (-105, 0, 590) mm",
        "upstream": "T01 right shoulder crossmember", "downstream": "G02 palm at R_WRIST_ROTATION",
        "route_tokens": ["R_ARM"],
        "refinement": "Close gimbal packaging, link plates, elbow/wrist shafts, stops, covers, service loops and the current arm-mass overrun.",
    },
    {
        "id": "G02", "segment": "Right hand-shaped parallel gripper", "side": "R", "region": "hand",
        "envelopes": ["R_HAND_PALM_ENVELOPE", "R_INBOARD_GRIPPER_FINGER", "R_OUTBOARD_GRIPPER_FINGER"],
        "mass_groups": ["R hand"], "axes": ["R_GRIPPER"], "actuated_by": [],
        "datum": "R_GRIPPER @ (-140, 0, 252) mm", "upstream": "A02 supported wrist shaft",
        "downstream": "Two broad fingers and replaceable compliant pad lands", "route_tokens": ["R_ARM"],
        "refinement": "Select equalizer, pads, force/current limit, object sensing, mechanical end stops, retention and pinch-safe finger gaps.",
    },
    {
        "id": "L01", "segment": "Left hip, thigh, knee, shin and ankle", "side": "L", "region": "leg",
        "envelopes": ["L_HIP_HOUSING_ENVELOPE", "L_THIGH_SHELL_ENVELOPE", "L_KNEE_HOUSING_ENVELOPE", "L_SHIN_SHELL_ENVELOPE", "L_ANKLE_HOUSING_ENVELOPE"],
        "mass_groups": ["L leg"],
        "axes": ["L_HIP_YAW", "L_HIP_ROLL", "L_HIP_PITCH", "L_KNEE_PITCH", "L_ANKLE_PITCH", "L_ANKLE_ROLL"],
        "actuated_by": [], "datum": "L_HIP_PITCH @ (62.5, 0, 380) mm",
        "upstream": "P01 left hip stack", "downstream": "F01 sole carrier at L_ANKLE_ROLL",
        "route_tokens": ["L_LEG"],
        "refinement": "Close reduced-joint transmissions, output encoders, shafts, bearings, link stiffness, covers, thermal paths and moving cable loops.",
    },
    {
        "id": "F01", "segment": "Left ankle output, foot and sole interface", "side": "L", "region": "foot",
        "envelopes": ["L_FOOT_SHELL_ENVELOPE"], "mass_groups": ["L foot"], "axes": [],
        "actuated_by": ["L_ANKLE_ROLL"], "datum": "Floor Z=0; L_ANKLE_ROLL @ (62.5, 0, 37) mm",
        "upstream": "L01 ankle-roll output", "downstream": "Replaceable sole/contact and force-sensing layers",
        "route_tokens": ["L_LEG"],
        "refinement": "Select sole material, contact sensing, fasteners, toe/heel edge treatment, friction target and structural proof under single support.",
    },
    {
        "id": "L02", "segment": "Right hip, thigh, knee, shin and ankle", "side": "R", "region": "leg",
        "envelopes": ["R_HIP_HOUSING_ENVELOPE", "R_THIGH_SHELL_ENVELOPE", "R_KNEE_HOUSING_ENVELOPE", "R_SHIN_SHELL_ENVELOPE", "R_ANKLE_HOUSING_ENVELOPE"],
        "mass_groups": ["R leg"],
        "axes": ["R_HIP_YAW", "R_HIP_ROLL", "R_HIP_PITCH", "R_KNEE_PITCH", "R_ANKLE_PITCH", "R_ANKLE_ROLL"],
        "actuated_by": [], "datum": "R_HIP_PITCH @ (-62.5, 0, 380) mm",
        "upstream": "P01 right hip stack", "downstream": "F02 sole carrier at R_ANKLE_ROLL",
        "route_tokens": ["R_LEG"],
        "refinement": "Close reduced-joint transmissions, output encoders, shafts, bearings, link stiffness, covers, thermal paths and moving cable loops.",
    },
    {
        "id": "F02", "segment": "Right ankle output, foot and sole interface", "side": "R", "region": "foot",
        "envelopes": ["R_FOOT_SHELL_ENVELOPE"], "mass_groups": ["R foot"], "axes": [],
        "actuated_by": ["R_ANKLE_ROLL"], "datum": "Floor Z=0; R_ANKLE_ROLL @ (-62.5, 0, 37) mm",
        "upstream": "L02 ankle-roll output", "downstream": "Replaceable sole/contact and force-sensing layers",
        "route_tokens": ["R_LEG"],
        "refinement": "Select sole material, contact sensing, fasteners, toe/heel edge treatment, friction target and structural proof under single support.",
    },
]


def read_csv(name: str) -> list[dict]:
    with (PACKAGE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict]) -> None:
    with (PACKAGE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def number(row: dict, key: str) -> float:
    return float(row[key])


def union_bbox(rows: list[dict]) -> tuple[float, float, float, float, float, float]:
    return (
        min(number(r, "xmin_mm") for r in rows), max(number(r, "xmax_mm") for r in rows),
        min(number(r, "ymin_mm") for r in rows), max(number(r, "ymax_mm") for r in rows),
        min(number(r, "zmin_mm") for r in rows), max(number(r, "zmax_mm") for r in rows),
    )


def module_rows() -> tuple[list[dict], dict[str, dict], list[dict]]:
    envelope_rows = read_csv("component-envelope-schedule.csv")
    envelopes = {row["component"]: row for row in envelope_rows}
    axes = {row["axis_id"]: row for row in read_csv("joint-axis-schedule.csv")}
    allocations = {row["axis_id"]: row for row in read_csv("actuator-transmission-allocation.csv")}
    bindings = {row["axis_id"]: row for row in read_csv("joint-module-axis-binding.csv")}
    mass_by_group: dict[str, float] = defaultdict(float)
    for row in read_csv("mass-properties-budget.csv"):
        if row["link"] != "TOTAL":
            mass_by_group[row["assembly_group"]] += float(row["allocated_mass_kg"])
    parts_by_module: dict[str, list[dict]] = defaultdict(list)
    for row in read_csv("fabrication-part-register.csv"):
        parts_by_module[row["module"]].append(row)
    panels_by_module: dict[str, list[str]] = defaultdict(list)
    for row in read_csv("service-panel-interface-register.csv"):
        panels_by_module[row["module"]].append(row["panel_id"])
    routes = read_csv("harness-route-register.csv")

    output = []
    for module in MODULES:
        missing = [name for name in module["envelopes"] if name not in envelopes]
        if missing:
            raise SystemExit(f"{module['id']} missing envelope sources: {missing}")
        source_rows = [envelopes[name] for name in module["envelopes"]]
        xmin, xmax, ymin, ymax, zmin, zmax = union_bbox(source_rows)
        owned = module["axes"]
        interface_axes = owned or module["actuated_by"]
        interface_summaries = []
        for axis_id in interface_axes:
            b = bindings[axis_id]
            interface_summaries.append(
                f"{axis_id}: {b['family_id']}; plate {b['plate_candidate_mm']}; {b['external_mount_pattern']}"
            )
        actuation = []
        for axis_id in owned:
            a = allocations[axis_id]
            actuation.append(f"{axis_id}: {a['candidate_actuator']} / {a['candidate_transmission']}")
        if not actuation:
            actuation.append("PASSIVE MODULE; moved through " + ", ".join(module["actuated_by"]))
        route_ids = [r["route_id"] for r in routes if any(token in r["route_id"] for token in module["route_tokens"])]
        mass = sum(mass_by_group[group] for group in module["mass_groups"])
        output.append({
            "module_id": module["id"], "body_segment": module["segment"], "side": module["side"], "region": module["region"],
            "envelope_sources": "; ".join(module["envelopes"]),
            "bbox_width_x_mm": f"{xmax-xmin:.3f}", "bbox_depth_y_mm": f"{ymax-ymin:.3f}", "bbox_height_z_mm": f"{zmax-zmin:.3f}",
            "bbox_min_xyz_mm": f"({xmin:.3f}, {ymin:.3f}, {zmin:.3f})", "bbox_max_xyz_mm": f"({xmax:.3f}, {ymax:.3f}, {zmax:.3f})",
            "primary_datum": module["datum"], "upstream_interface": module["upstream"], "downstream_interface": module["downstream"],
            "owned_axis_count": str(len(owned)), "owned_axes": "; ".join(owned) if owned else "NONE - PASSIVE BODY MODULE",
            "actuated_by": "; ".join(module["actuated_by"]) if module["actuated_by"] else "OWNED AXES",
            "joint_interface_summary": " | ".join(interface_summaries),
            "planning_mass_kg": f"{mass:.9f}", "fabrication_part_count": str(len(parts_by_module[module["id"]])),
            "service_panels": "; ".join(panels_by_module[module["id"]]) or "NONE DEFINED",
            "harness_routes": "; ".join(route_ids) or "NO DEDICATED ROUTE - INTERFACE CLOSURE REQUIRED",
            "candidate_actuation": " | ".join(actuation), "refinement_path": module["refinement"],
            "release_state": "DIMENSIONED WHOLE-BODY INTERFACE CANDIDATE - DETAIL DRAWING/GD&T/SELECTION/DFM/FAI/PHYSICAL VALIDATION OPEN",
            "warning": WARNING,
        })
    if set(axes) != {axis for module in MODULES for axis in module["axes"]}:
        raise SystemExit("25-axis ownership is not complete and unique")
    return output, envelopes, list(axes.values())


def assembly_rows() -> list[dict]:
    steps = [
        (1, "A", "F01", "NONE", "Assemble left sole carrier, top bridge, contact layers and removable cover."),
        (1, "B", "F02", "NONE", "Assemble right sole carrier, top bridge, contact layers and removable cover."),
        (2, "A", "L01", "F01", "Build ankle-to-hip left leg stack around released axes and connect foot interface."),
        (2, "B", "L02", "F02", "Build ankle-to-hip right leg stack around released axes and connect foot interface."),
        (3, "A", "P01", "L01; L02", "Join both hip stacks to pelvis frame; install waist and uncredited restraint bridge."),
        (4, "A", "T01", "P01", "Install torso rails, shoulder crossmember, compute bay and waist output interface."),
        (5, "A", "N01", "T01", "Install neck pan/tilt stack and moving head harness loop."),
        (6, "A", "H01", "N01", "Install screen-face head shell, cameras, microphones, speakers and rear service cover."),
        (7, "A", "A01", "T01", "Install left shoulder gimbal, upper arm, elbow, forearm and wrist."),
        (7, "B", "A02", "T01", "Install right shoulder gimbal, upper arm, elbow, forearm and wrist."),
        (8, "A", "G01", "A01", "Install left palm, coupled fingers, pads and service cover."),
        (8, "B", "G02", "A02", "Install right palm, coupled fingers, pads and service cover."),
    ]
    return [{
        "assembly_step": step, "parallel_group": group, "module_id": module, "prerequisite_modules": prerequisites,
        "candidate_operation": operation,
        "required_unpowered_checkpoint": "Interface datums/fasteners/free motion/stop clearance/continuity-isolation/mass record; exact criteria require released build traveler.",
        "release_state": "ASSEMBLY SEQUENCE CANDIDATE - NO ASSEMBLY OR POWERED-WORK AUTHORITY", "warning": WARNING,
    } for step, group, module, prerequisites, operation in steps]


def color_for(component: str) -> str:
    if "HEAD" in component or "FACE" in component:
        return "#77c9f2"
    if "TORSO" in component or "PELVIS" in component or "NECK" in component or "WAIST" in component:
        return "#183c67"
    if "HAND" in component or "GRIPPER" in component or "FINGER" in component:
        return "#f2b91d"
    if "FOOT" in component:
        return "#2f6fa4"
    return "#58aee0"


def render_svg(envelopes: dict[str, dict], axes: list[dict]) -> str:
    draw_names = [
        "HEAD_SHELL_ENVELOPE", "FACE_SCREEN_PANEL", "NECK_COLUMN_ENVELOPE", "TORSO_SHELL_ENVELOPE", "PELVIS_SHELL_ENVELOPE",
        "L_SHOULDER_HOUSING_ENVELOPE", "L_UPPER_ARM_SHELL_ENVELOPE", "L_ELBOW_HOUSING_ENVELOPE", "L_FOREARM_SHELL_ENVELOPE", "L_WRIST_HOUSING_ENVELOPE", "L_HAND_PALM_ENVELOPE", "L_INBOARD_GRIPPER_FINGER", "L_OUTBOARD_GRIPPER_FINGER",
        "R_SHOULDER_HOUSING_ENVELOPE", "R_UPPER_ARM_SHELL_ENVELOPE", "R_ELBOW_HOUSING_ENVELOPE", "R_FOREARM_SHELL_ENVELOPE", "R_WRIST_HOUSING_ENVELOPE", "R_HAND_PALM_ENVELOPE", "R_INBOARD_GRIPPER_FINGER", "R_OUTBOARD_GRIPPER_FINGER",
        "L_HIP_HOUSING_ENVELOPE", "L_THIGH_SHELL_ENVELOPE", "L_KNEE_HOUSING_ENVELOPE", "L_SHIN_SHELL_ENVELOPE", "L_ANKLE_HOUSING_ENVELOPE", "L_FOOT_SHELL_ENVELOPE",
        "R_HIP_HOUSING_ENVELOPE", "R_THIGH_SHELL_ENVELOPE", "R_KNEE_HOUSING_ENVELOPE", "R_SHIN_SHELL_ENVELOPE", "R_ANKLE_HOUSING_ENVELOPE", "R_FOOT_SHELL_ENVELOPE",
    ]
    front_origin, side_origin, base_y, z_scale, x_scale, y_scale = 390.0, 1050.0, 965.0, 1.0, 1.45, 2.0
    parts = []
    for name in draw_names:
        row = envelopes[name]
        xmin, xmax = number(row, "xmin_mm"), number(row, "xmax_mm")
        ymin, ymax = number(row, "ymin_mm"), number(row, "ymax_mm")
        zmin, zmax = number(row, "zmin_mm"), number(row, "zmax_mm")
        fill = color_for(name)
        parts.append(f'<rect x="{front_origin+xmin*x_scale:.2f}" y="{base_y-zmax*z_scale:.2f}" width="{(xmax-xmin)*x_scale:.2f}" height="{(zmax-zmin)*z_scale:.2f}" rx="7" fill="{fill}" fill-opacity="0.38" stroke="{fill}" stroke-width="2"/>')
        if name.startswith("R_"):
            continue
        parts.append(f'<rect x="{side_origin+ymin*y_scale:.2f}" y="{base_y-zmax*z_scale:.2f}" width="{(ymax-ymin)*y_scale:.2f}" height="{(zmax-zmin)*z_scale:.2f}" rx="7" fill="{fill}" fill-opacity="0.30" stroke="{fill}" stroke-width="2"/>')
    axis_parts = []
    for axis in axes:
        x, y, z = float(axis["x_mm"]), float(axis["y_mm"]), float(axis["z_mm"])
        axis_parts.append(f'<circle cx="{front_origin+x*x_scale:.2f}" cy="{base_y-z*z_scale:.2f}" r="5.5" fill="#d63b31" stroke="white" stroke-width="2"><title>{html.escape(axis["axis_id"])} @ ({x:g}, {y:g}, {z:g}) mm; direction ({axis["direction_x"]}, {axis["direction_y"]}, {axis["direction_z"]})</title></circle>')
        axis_parts.append(f'<circle cx="{side_origin+y*y_scale:.2f}" cy="{base_y-z*z_scale:.2f}" r="4.8" fill="#d63b31" stroke="white" stroke-width="2"><title>{html.escape(axis["axis_id"])}</title></circle>')
    dimension_z = [(0, "floor"), (37, "ankle roll"), (45, "ankle pitch"), (210, "knee"), (380, "hip pitch"), (425, "waist"), (590, "shoulder"), (650, "neck pan"), (690, "head tilt"), (762, "shell top")]
    dims = []
    for z, label in dimension_z:
        y = base_y - z*z_scale
        dims.append(f'<line x1="70" y1="{y:.2f}" x2="650" y2="{y:.2f}" stroke="#9ab8cc" stroke-width="1" stroke-dasharray="5 6"/><text x="72" y="{y-5:.2f}" class="dim">{z} mm · {label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1040" role="img" aria-labelledby="title desc">
<title id="title">HR-30 P0.1 dimensioned whole-body interface atlas</title><desc id="desc">Front and side projections of the 762 millimetre humanoid with all 25 joint axes and controlled height datums.</desc>
<style>.title{{font:800 34px system-ui;fill:#132f55}}.sub{{font:600 18px system-ui;fill:#335c7d}}.label{{font:800 21px system-ui;fill:#132f55}}.dim{{font:700 14px system-ui;fill:#335c7d}}.note{{font:600 15px system-ui;fill:#335c7d}}</style>
<rect width="1600" height="1040" fill="#f7fbfe"/><rect x="28" y="24" width="1544" height="70" rx="14" fill="#f2b91d" stroke="#8a5b00" stroke-width="3"/>
<text x="52" y="55" class="title">HR-30 whole-body mechanical interface atlas · P0.1</text><text x="52" y="80" class="sub">PRELIMINARY CONFIGURATION CAD — NOT A FABRICATION, MOTION OR ENERGIZATION RELEASE</text>
<text x="300" y="138" class="label">FRONT · X/Z</text><text x="970" y="138" class="label">LEFT SIDE · Y/Z</text>
{''.join(dims)}{''.join(parts)}{''.join(axis_parts)}
<line x1="58" y1="965" x2="1450" y2="965" stroke="#132f55" stroke-width="3"/><line x1="45" y1="965" x2="45" y2="203" stroke="#132f55" stroke-width="2"/>
<line x1="45" y1="965" x2="45" y2="203" stroke="#132f55" stroke-width="2"/><path d="M39 210 L45 198 L51 210" fill="#132f55"/><text x="24" y="590" transform="rotate(-90 24 590)" class="label">762 mm nominal floor-to-shell top</text>
<circle cx="690" cy="985" r="6" fill="#d63b31"/><text x="706" y="991" class="note">25 named joint axes</text><rect x="925" y="976" width="28" height="16" rx="4" fill="#77c9f2"/><text x="965" y="991" class="note">shell/body envelopes</text><rect x="1200" y="976" width="28" height="16" rx="4" fill="#f2b91d"/><text x="1240" y="991" class="note">hands/grippers</text>
</svg>'''


def render_html(rows: list[dict], axes: list[dict]) -> str:
    cards = []
    for row in rows:
        cards.append(f'''<article class="module" data-region="{html.escape(row['region'])}" id="module-{row['module_id'].lower()}"><header><span class="module-id">{row['module_id']}</span><div><h3>{html.escape(row['body_segment'])}</h3><p>{row['bbox_width_x_mm']} × {row['bbox_depth_y_mm']} × {row['bbox_height_z_mm']} mm · {row['planning_mass_kg']} kg planning mass</p></div></header><div class="module-grid"><div><strong>Datum</strong><p>{html.escape(row['primary_datum'])}</p></div><div><strong>Interfaces</strong><p>{html.escape(row['upstream_interface'])} → {html.escape(row['downstream_interface'])}</p></div><div><strong>Axes / motion</strong><p>{html.escape(row['owned_axes'])}; actuated by {html.escape(row['actuated_by'])}</p></div><div><strong>Mechanical interface candidate</strong><p>{html.escape(row['joint_interface_summary'])}</p></div><div><strong>Service and harness</strong><p>Panels: {html.escape(row['service_panels'])}<br>Routes: {html.escape(row['harness_routes'])}</p></div><div><strong>Next physical definition</strong><p>{html.escape(row['refinement_path'])}</p></div></div><details><summary>Actuator and transmission allocation</summary><p>{html.escape(row['candidate_actuation'])}</p></details></article>''')
    axis_rows = []
    for axis in axes:
        axis_rows.append(f'''<tr><td>{html.escape(axis['axis_id'])}</td><td>{html.escape(axis['region'])} / {html.escape(axis['side'])}</td><td>({float(axis['x_mm']):g}, {float(axis['y_mm']):g}, {float(axis['z_mm']):g}) mm</td><td>({axis['direction_x']}, {axis['direction_y']}, {axis['direction_z']})</td><td>{html.escape(axis['provisional_commanded_range'])}</td></tr>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-body interface atlas P0.1</title><script type="module" src="vendor/model-viewer.min.js"></script><style>
:root{{--navy:#132f55;--deep:#0b203a;--sky:#77c9f2;--mid:#2f6fa4;--gold:#f2b91d;--pale:#eef8fd;--line:#b8d7e8;--ink:#17243a}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}header.hero{{background:var(--deep);color:white;padding:34px max(20px,calc((100vw - 1320px)/2))}}h1{{font-size:clamp(35px,5vw,62px);line-height:1.04;margin:.15em 0}}h2{{font-size:clamp(27px,3vw,40px);color:var(--navy)}}h3{{font-size:22px;margin:0;color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:16px 18px;font-weight:900}}main{{width:100%;max-width:1320px;min-width:0;margin:auto;padding:24px 20px 80px}}.hero p{{max-width:950px}}.atlas,.viewer,.module,.table{{max-width:100%;min-width:0;background:white;border:2px solid var(--line);border-radius:17px;overflow:hidden;box-shadow:0 3px 0 #c4e2f1}}.atlas-scroll{{width:100%;max-width:100%;overflow:auto}}.atlas object{{display:block;width:100%;min-width:900px;height:auto;aspect-ratio:1600/1040}}model-viewer{{width:100%;height:650px;background:radial-gradient(circle,#fff,var(--pale))}}.viewer p,.atlas p{{padding:0 20px 18px}}.filters{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}}button{{font:800 16px system-ui;padding:10px 16px;border:2px solid var(--navy);border-radius:999px;background:white;color:var(--navy);cursor:pointer}}button.active{{background:var(--navy);color:white}}.modules{{display:grid;gap:18px;min-width:0}}.module{{padding:20px}}.module>header{{display:flex;align-items:flex-start;gap:15px}}.module-id{{display:grid;place-items:center;min-width:62px;height:44px;border-radius:12px;background:var(--gold);border:2px solid #8a5b00;font-weight:900}}.module header p{{margin:.2em 0}}.module-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:18px}}.module-grid>div{{min-width:0;background:var(--pale);border-left:6px solid var(--sky);padding:12px 14px}}.module-grid p{{margin:.25em 0;overflow-wrap:anywhere}}details{{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}}summary{{font-weight:850;color:var(--navy);cursor:pointer}}.table{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:960px}}th,td{{padding:13px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:16px}}th{{background:var(--navy);color:white;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}footer{{background:var(--deep);color:white;padding:30px max(20px,calc((100vw - 1320px)/2))}}@media(max-width:760px){{.module-grid{{grid-template-columns:1fr}}model-viewer{{height:520px}}}}
</style></head><body><header class="hero"><div class="warning">{WARNING}</div><h1>Every part of the 762 mm robot, in one interface map.</h1><p>This atlas joins the actual whole-body CAD to 12 build modules, all 25 joint axes, current mass allocation, actuator/transmission candidates, service panels, harness corridors, and staged assembly dependencies. It is an editable P0.1 engineering candidate—not a released manufacturing drawing.</p></header><main>
<section><h2>Dimensioned whole-body reference</h2><div class="atlas"><div class="atlas-scroll"><object data="whole-body-interface-atlas.svg" type="image/svg+xml" aria-label="Dimensioned front and side HR-30 body reference"></object></div><p>Red points are the exact joint-axis datums from <a href="joint-axis-schedule.csv">joint-axis-schedule.csv</a>. Hover them in a desktop browser for axis identity and coordinates. On a narrow screen, scroll the drawing horizontally rather than shrinking its technical labels.</p></div></section>
<section><h2>Inspect the integrated assembly</h2><div class="viewer"><model-viewer src="HR-30_installed_equipment_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 whole robot with installed equipment" camera-controls camera-orbit="35deg 76deg 95%" field-of-view="26deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>The interactive GLB contains the recognizable complete robot and located equipment. Download the <a href="HR-30_integrated_whole_robot_candidate.step">editable integrated STEP</a> for exact CAD inspection.</p></div></section>
<section><h2>Separate the robot into build modules</h2><div class="viewer"><model-viewer src="module-cad/HR-30_module_exploded_candidate.glb" poster="front-elevation.svg" alt="Interactive exploded view of the 12 HR-30 whole-body modules" camera-controls camera-orbit="35deg 76deg 115%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p>The 12 modules retain their internal datums while presentation offsets expose every interface. <a href="module-cad/index.html">Open the module CAD guide</a> or download the <a href="module-cad/HR-30_module_exploded_candidate.step">exploded STEP</a>.</p></div></section>
<section><h2>Module interface control</h2><div class="filters" role="group" aria-label="Filter modules"><button class="active" data-filter="all">All 12</button><button data-filter="head">Head</button><button data-filter="neck">Neck</button><button data-filter="trunk">Torso + pelvis</button><button data-filter="arm">Arms</button><button data-filter="hand">Hands</button><button data-filter="leg">Legs</button><button data-filter="foot">Feet</button></div><div class="modules">{''.join(cards)}</div></section>
<section><h2>All 25 controlled axes</h2><div class="table"><table><thead><tr><th>Axis</th><th>Region / side</th><th>Origin</th><th>Direction</th><th>P0.1 commanded range</th></tr></thead><tbody>{''.join(axis_rows)}</tbody></table></div></section>
<section><h2>Editable source records</h2><p><a href="module-interface-control-register.csv">12-module interface register</a> · <a href="module-assembly-sequence.csv">assembly dependency sequence</a> · <a href="joint-module-axis-binding.csv">joint mount patterns</a> · <a href="fabrication-part-register.csv">66 fabrication candidates</a> · <a href="service-panel-interface-register.csv">service panels</a> · <a href="harness-route-register.csv">harness corridors</a> · <a href="interface-atlas-source.py">atlas generator source</a></p></section>
</main><footer>Project Button · HR-30 whole-body P0.1 · adult-operated experimental machinery · no procurement, fabrication, assembly, powered-test, motion or energization authority</footer><script>const buttons=[...document.querySelectorAll('[data-filter]')],cards=[...document.querySelectorAll('.module')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');const f=b.dataset.filter;cards.forEach(c=>c.hidden=f!=='all'&&c.dataset.region!==f)}}));</script></body></html>'''


def update_package(rows: list[dict]) -> None:
    write_csv("module-interface-control-register.csv", rows)
    write_csv("module-assembly-sequence.csv", assembly_rows())
    _, envelopes, axes = module_rows()
    (PACKAGE / "whole-body-interface-atlas.svg").write_text(render_svg(envelopes, axes), encoding="utf-8", newline="\n")
    (PACKAGE / "whole-body-interface-atlas.html").write_text(render_html(rows, axes), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), PACKAGE / "interface-atlas-source.py")

    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "whole_body_interface_atlas_present": True,
        "module_interface_control_count": 12,
        "module_interface_axis_ownership_count": 25,
        "module_interface_mass_reconciliation_kg": round(sum(float(r["planning_mass_kg"]) for r in rows), 9),
        "module_interface_mass_rounding_delta_kg": round(
            float(next(r["allocated_mass_kg"] for r in read_csv("mass-properties-budget.csv") if r["link"] == "TOTAL"))
            - sum(float(r["planning_mass_kg"]) for r in rows), 9
        ),
        "dimensioned_whole_body_front_side_reference_present": True,
        "manufacturing_detail_complete": False,
        "fabrication_drawings_released": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    holds = read_csv("open-holds.csv")
    for hold in holds:
        if hold["hold_id"] == "HR30-P01-H10":
            hold["unresolved_item"] = "A whole-body interface atlas consolidates 12 modules, all 25 axes, dimensions, masses, mount-pattern candidates, service panels, harness routes and assembly dependencies; twelve module-specific fabrication/integration STEP pairs, an exploded STEP/GLB, and individual candidate files for all 66 physical fabrication parts now implement that partition. Released manufacturing drawings, tolerances/GD&T, material/process selections, fasteners, DFM, FAI, proof, physical test and qualified review remain open."
    write_csv("open-holds.csv", holds)

    readme_path = PACKAGE / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Whole-body joint-load architecture\n"
    addition = "\n## Whole-body interface atlas\n\nThe web-first interface atlas now consolidates the actual 12 build modules, all 25 owned axes, union-envelope dimensions, current mass allocation, candidate joint mount patterns, service panels, harness corridors, adjacent-module interfaces and staged assembly dependencies. It is generated from the authoritative CAD registers and links directly to the integrated STEP/GLB. It is a P0.1 interface-control candidate; released part drawings, GD&T, material/process selections, fasteners, DFM, FAI and physical validation remain open.\n"
    if addition.strip() not in readme:
        if marker not in readme:
            raise SystemExit("README insertion marker missing")
        readme = readme.replace(marker, addition + marker)
        readme_path.write_text(readme, encoding="utf-8", newline="\n")

    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-INTERFACE-ATLAS-P01-START -->", "<!-- HR30-INTERFACE-ATLAS-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = "<section><h2>System artifacts</h2>"
    planning_mass = sum(float(row["planning_mass_kg"]) for row in rows)
    section = f'''{start}<section id="whole-body-interface-atlas"><h2>The complete robot now has one interface atlas</h2><div class="grid"><article class="card pass"><div class="metric">12</div><p>Head, neck, torso, pelvis, bilateral arms, functional hands, legs and feet have controlled module records.</p></article><article class="card pass"><div class="metric">25 / 25</div><p>Every axis has exactly one owning module and a dimensioned candidate mount family.</p></article><article class="card pass"><div class="metric">11.458 kg</div><p>Module masses reconcile to the current whole-body planning model.</p></article><article class="card hold"><div class="metric">0</div><p>Released manufacturing drawings or fabrication approvals; P0.1 remains preliminary.</p></article></div><div class="viewer"><object style="display:block;width:100%;height:auto;aspect-ratio:1600/1040" data="whole-body-interface-atlas.svg" type="image/svg+xml" aria-label="Dimensioned HR-30 whole-body interface drawing"></object><p><a href="whole-body-interface-atlas.html">Open the interactive interface atlas</a> · <a href="module-interface-control-register.csv">12-module register</a> · <a href="module-assembly-sequence.csv">assembly dependencies</a>.</p></div></section>{end}'''
    section = section.replace("11.458 kg", f"{planning_mass:.3f} kg")
    if marker not in page:
        raise SystemExit("web insertion marker missing")
    page = page.replace(marker, section + marker)
    page = page.replace("<h3>KiCad remains open</h3><p>The historical mixed project is not an HR-30 whole-body wiring release. A native HR-30-only eight-segment schematic must follow this allocation.</p>", "<h3>Native KiCad follows this allocation</h3><p>The 16-sheet HR-30 project connects the same five RS-485 and three TTL segments and adds head, pelvis-IMU and bilateral foot-sensing interfaces. Physical controller devices, pins and harnesses remain open.</p>")
    page = page.replace("The 13-sheet HR-30 project connects", "The 16-sheet HR-30 project connects")
    page_path.write_text(page, encoding="utf-8", newline="\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def main() -> int:
    rows, _, _ = module_rows()
    if len(rows) != 12 or sum(int(r["owned_axis_count"]) for r in rows) != 25:
        raise SystemExit("controlled whole-body interface coverage drift")
    update_package(rows)
    print(json.dumps({
        "identifier": IDENTIFIER,
        "modules": len(rows),
        "owned_axes": sum(int(r["owned_axis_count"]) for r in rows),
        "planning_mass_kg": round(sum(float(r["planning_mass_kg"]) for r in rows), 6),
        "fabrication_drawings_released": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
