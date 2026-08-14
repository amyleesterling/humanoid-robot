"""Complete the HR-30 P0.1 whole-body systems package around the native CAD.

This generator adds executable dynamics-model syntax, engineering budgets, the
candidate BOM, deterministic embodied-agent boundary, walking architecture and
the modular build/electrification sequence.  Values are architecture estimates,
not procurement, fabrication, motion or energization releases.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-WHOLE-BODY-P0.1"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def inertia_box(mass: float, size: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = size
    return (
        mass * (y * y + z * z) / 12.0,
        mass * (x * x + z * z) / 12.0,
        mass * (x * x + y * y) / 12.0,
    )


def link_rows() -> list[dict]:
    rows: list[dict] = [
        {"link": "base_link", "group": "pelvis/power", "mass": 1.65, "center": (0, 0, 0.390), "size": (0.155, 0.105, 0.070)},
        {"link": "torso", "group": "torso/compute/waist", "mass": 1.83, "center": (0, 0, 0.510), "size": (0.190, 0.110, 0.155)},
        {"link": "neck_pan_link", "group": "neck", "mass": 0.10, "center": (0, 0, 0.625), "size": (0.054, 0.054, 0.058)},
        {"link": "head", "group": "head/display/sensing", "mass": 0.40, "center": (0, 0, 0.706), "size": (0.150, 0.110, 0.112)},
    ]
    for side, sign in (("L", 1.0), ("R", -1.0)):
        rows.extend([
            {"link": f"{side}_shoulder_pitch_link", "group": f"{side} arm", "mass": 0.10, "center": (sign * 0.105, 0, 0.590), "size": (0.040, 0.072, 0.058)},
            {"link": f"{side}_upper_arm", "group": f"{side} arm", "mass": 0.27, "center": (sign * 0.115, 0, 0.515), "size": (0.052, 0.052, 0.150)},
            {"link": f"{side}_forearm", "group": f"{side} arm", "mass": 0.22, "center": (sign * 0.125, 0, 0.368), "size": (0.050, 0.050, 0.145)},
            {"link": f"{side}_hand", "group": f"{side} hand", "mass": 0.18, "center": (sign * 0.125, 0, 0.270), "size": (0.050, 0.058, 0.050)},
            {"link": f"{side}_gripper", "group": f"{side} hand", "mass": 0.03, "center": (sign * 0.125, 0, 0.232), "size": (0.044, 0.048, 0.046)},
            {"link": f"{side}_hip_yaw_link", "group": f"{side} leg", "mass": 0.08, "center": (sign * 0.0625, 0, 0.397), "size": (0.060, 0.070, 0.040)},
            {"link": f"{side}_hip_roll_link", "group": f"{side} leg", "mass": 0.08, "center": (sign * 0.0625, 0, 0.388), "size": (0.060, 0.070, 0.040)},
            {"link": f"{side}_thigh", "group": f"{side} leg", "mass": 0.66, "center": (sign * 0.0625, 0, 0.295), "size": (0.074, 0.076, 0.140)},
            {"link": f"{side}_shin", "group": f"{side} leg", "mass": 0.47, "center": (sign * 0.0625, 0, 0.128), "size": (0.068, 0.072, 0.145)},
            {"link": f"{side}_ankle_pitch_link", "group": f"{side} leg", "mass": 0.13, "center": (sign * 0.0625, 0, 0.045), "size": (0.066, 0.064, 0.052)},
            {"link": f"{side}_foot", "group": f"{side} foot", "mass": 0.605, "center": (sign * 0.0625, -0.025, 0.0175), "size": (0.090, 0.145, 0.035)},
        ])
    return rows


def frame_positions() -> dict[str, tuple[float, float, float]]:
    frames = {
        "base_link": (0, 0, 0.390), "torso": (0, 0, 0.425),
        "neck_pan_link": (0, 0, 0.650), "head": (0, 0, 0.690),
    }
    for side, sign in (("L", 1.0), ("R", -1.0)):
        frames.update({
            f"{side}_shoulder_pitch_link": (sign * 0.105, 0, 0.590),
            f"{side}_upper_arm": (sign * 0.105, 0, 0.590),
            f"{side}_forearm": (sign * 0.125, 0, 0.440),
            f"{side}_hand": (sign * 0.125, 0, 0.295),
            f"{side}_gripper": (sign * 0.125, 0, 0.252),
            f"{side}_hip_yaw_link": (sign * 0.0625, 0, 0.397),
            f"{side}_hip_roll_link": (sign * 0.0625, 0, 0.388),
            f"{side}_thigh": (sign * 0.0625, 0, 0.380),
            f"{side}_shin": (sign * 0.0625, 0, 0.210),
            f"{side}_ankle_pitch_link": (sign * 0.0625, 0, 0.045),
            f"{side}_foot": (sign * 0.0625, 0, 0.037),
        })
    return frames


def joint_rows() -> list[dict]:
    rows = [
        {"name": "WAIST_YAW", "parent": "base_link", "child": "torso", "type": "revolute", "axis": (0, 0, 1), "limit": (-0.52, 0.52, 0.25)},
        {"name": "HEAD_PAN", "parent": "torso", "child": "neck_pan_link", "type": "revolute", "axis": (0, 0, 1), "limit": (-1.40, 1.40, 1.0)},
        {"name": "HEAD_TILT", "parent": "neck_pan_link", "child": "head", "type": "revolute", "axis": (1, 0, 0), "limit": (-0.52, 0.52, 0.8)},
    ]
    for side, sign in (("L", 1.0), ("R", -1.0)):
        rows.extend([
            {"name": f"{side}_SHOULDER_PITCH", "parent": "torso", "child": f"{side}_shoulder_pitch_link", "type": "revolute", "axis": (1, 0, 0), "limit": (-1.57, 1.57, 0.6)},
            {"name": f"{side}_SHOULDER_ROLL", "parent": f"{side}_shoulder_pitch_link", "child": f"{side}_upper_arm", "type": "revolute", "axis": (0, 1, 0), "limit": (-1.22, 1.22, 0.6)},
            {"name": f"{side}_ELBOW_PITCH", "parent": f"{side}_upper_arm", "child": f"{side}_forearm", "type": "revolute", "axis": (1, 0, 0), "limit": (0.0, 2.20, 0.8)},
            {"name": f"{side}_WRIST_ROTATION", "parent": f"{side}_forearm", "child": f"{side}_hand", "type": "revolute", "axis": (0, 0, 1), "limit": (-1.57, 1.57, 1.0)},
            {"name": f"{side}_GRIPPER", "parent": f"{side}_hand", "child": f"{side}_gripper", "type": "prismatic", "axis": (1, 0, 0), "limit": (0.0, 0.026, 0.03)},
            {"name": f"{side}_HIP_YAW", "parent": "base_link", "child": f"{side}_hip_yaw_link", "type": "revolute", "axis": (0, 0, 1), "limit": (-0.52, 0.52, 0.5)},
            {"name": f"{side}_HIP_ROLL", "parent": f"{side}_hip_yaw_link", "child": f"{side}_hip_roll_link", "type": "revolute", "axis": (0, 1, 0), "limit": (-0.44, 0.44, 0.5)},
            {"name": f"{side}_HIP_PITCH", "parent": f"{side}_hip_roll_link", "child": f"{side}_thigh", "type": "revolute", "axis": (1, 0, 0), "limit": (-0.61, 0.79, 0.6)},
            {"name": f"{side}_KNEE_PITCH", "parent": f"{side}_thigh", "child": f"{side}_shin", "type": "revolute", "axis": (1, 0, 0), "limit": (0.0, 2.09, 0.7)},
            {"name": f"{side}_ANKLE_PITCH", "parent": f"{side}_shin", "child": f"{side}_ankle_pitch_link", "type": "revolute", "axis": (1, 0, 0), "limit": (-0.61, 0.52, 0.7)},
            {"name": f"{side}_ANKLE_ROLL", "parent": f"{side}_ankle_pitch_link", "child": f"{side}_foot", "type": "revolute", "axis": (0, 1, 0), "limit": (-0.35, 0.35, 0.7)},
        ])
    return rows


def add_urdf_geometry(link: ET.Element, row: dict, frame: tuple[float, float, float]) -> None:
    center = row["center"]
    relative = tuple(center[i] - frame[i] for i in range(3))
    size = row["size"]
    ixx, iyy, izz = inertia_box(row["mass"], size)
    inertial = ET.SubElement(link, "inertial")
    ET.SubElement(inertial, "origin", xyz=" ".join(f"{v:.6f}" for v in relative), rpy="0 0 0")
    ET.SubElement(inertial, "mass", value=f"{row['mass']:.6f}")
    ET.SubElement(inertial, "inertia", ixx=f"{ixx:.9f}", ixy="0", ixz="0", iyy=f"{iyy:.9f}", iyz="0", izz=f"{izz:.9f}")
    for kind in ("visual", "collision"):
        node = ET.SubElement(link, kind)
        ET.SubElement(node, "origin", xyz=" ".join(f"{v:.6f}" for v in relative), rpy="0 0 0")
        geometry = ET.SubElement(node, "geometry")
        ET.SubElement(geometry, "box", size=" ".join(f"{v:.6f}" for v in size))
        if kind == "visual":
            material = ET.SubElement(node, "material", name="button_sky")
            ET.SubElement(material, "color", rgba="0.49 0.83 0.98 1")


def write_urdf(rows: list[dict], joints: list[dict]) -> None:
    frames = frame_positions()
    robot = ET.Element("robot", name="hr30_whole_body_p01")
    for row in rows:
        add_urdf_geometry(ET.SubElement(robot, "link", name=row["link"]), row, frames[row["link"]])
    for joint in joints:
        parent_frame = frames[joint["parent"]]
        child_frame = frames[joint["child"]]
        origin = tuple(child_frame[i] - parent_frame[i] for i in range(3))
        node = ET.SubElement(robot, "joint", name=joint["name"], type=joint["type"])
        ET.SubElement(node, "parent", link=joint["parent"])
        ET.SubElement(node, "child", link=joint["child"])
        ET.SubElement(node, "origin", xyz=" ".join(f"{v:.6f}" for v in origin), rpy="0 0 0")
        ET.SubElement(node, "axis", xyz=" ".join(str(v) for v in joint["axis"]))
        low, high, vel = joint["limit"]
        ET.SubElement(node, "limit", lower=f"{low:.6f}", upper=f"{high:.6f}", effort="0.0", velocity=f"{vel:.6f}")
        ET.SubElement(node, "dynamics", damping="0.1", friction="0.0")
    ET.indent(robot)
    (OUT / "hr30.urdf").write_text(ET.tostring(robot, encoding="unicode") + "\n", encoding="utf-8")


def write_mjcf(rows: list[dict], joints: list[dict]) -> None:
    by_link = {row["link"]: row for row in rows}
    children: dict[str, list[dict]] = {}
    for joint in joints:
        children.setdefault(joint["parent"], []).append(joint)
    frames = frame_positions()
    model = ET.Element("mujoco", model="hr30_whole_body_p01")
    ET.SubElement(model, "compiler", angle="radian", coordinate="local")
    ET.SubElement(model, "option", gravity="0 0 -9.80665", timestep="0.002")
    defaults = ET.SubElement(model, "default")
    ET.SubElement(defaults, "joint", damping="0.1", armature="0.01", limited="true")
    ET.SubElement(defaults, "geom", type="box", density="0", rgba="0.49 0.83 0.98 1", contype="1", conaffinity="1")
    world = ET.SubElement(model, "worldbody")
    ET.SubElement(world, "geom", name="floor", type="plane", size="2 2 0.02", rgba="0.85 0.90 0.95 1")

    def add_body(parent_node: ET.Element, link_name: str, world_origin: tuple[float, float, float], parent_origin: tuple[float, float, float]) -> None:
        row = by_link[link_name]
        rel = tuple(world_origin[i] - parent_origin[i] for i in range(3))
        body = ET.SubElement(parent_node, "body", name=link_name, pos=" ".join(f"{v:.6f}" for v in rel))
        if link_name == "base_link":
            ET.SubElement(body, "freejoint", name="floating_base")
        visual_rel = tuple(row["center"][i] - world_origin[i] for i in range(3))
        ET.SubElement(body, "inertial", pos=" ".join(f"{v:.6f}" for v in visual_rel), mass=f"{row['mass']:.6f}", diaginertia=" ".join(f"{v:.9f}" for v in inertia_box(row["mass"], row["size"])))
        ET.SubElement(body, "geom", pos=" ".join(f"{v:.6f}" for v in visual_rel), size=" ".join(f"{v / 2:.6f}" for v in row["size"]))
        for joint in children.get(link_name, []):
            child_origin = frames[joint["child"]]
            child = by_link[joint["child"]]
            child_rel = tuple(child_origin[i] - world_origin[i] for i in range(3))
            child_body = ET.SubElement(body, "body", name=joint["child"], pos=" ".join(f"{v:.6f}" for v in child_rel))
            low, high, _ = joint["limit"]
            ET.SubElement(child_body, "joint", name=joint["name"], type="slide" if joint["type"] == "prismatic" else "hinge", axis=" ".join(str(v) for v in joint["axis"]), range=f"{low:.6f} {high:.6f}")
            child_visual_rel = tuple(child["center"][i] - child_origin[i] for i in range(3))
            ET.SubElement(child_body, "inertial", pos=" ".join(f"{v:.6f}" for v in child_visual_rel), mass=f"{child['mass']:.6f}", diaginertia=" ".join(f"{v:.9f}" for v in inertia_box(child["mass"], child["size"])))
            ET.SubElement(child_body, "geom", pos=" ".join(f"{v:.6f}" for v in child_visual_rel), size=" ".join(f"{v / 2:.6f}" for v in child["size"]))

            def recurse(existing: ET.Element, current: str, current_origin: tuple[float, float, float]) -> None:
                for grand in children.get(current, []):
                    go = frames[grand["child"]]
                    gr = by_link[grand["child"]]
                    gb = ET.SubElement(existing, "body", name=grand["child"], pos=" ".join(f"{go[i]-current_origin[i]:.6f}" for i in range(3)))
                    gl, gh, _ = grand["limit"]
                    ET.SubElement(gb, "joint", name=grand["name"], type="slide" if grand["type"] == "prismatic" else "hinge", axis=" ".join(str(v) for v in grand["axis"]), range=f"{gl:.6f} {gh:.6f}")
                    vr = tuple(gr["center"][i] - go[i] for i in range(3))
                    ET.SubElement(gb, "inertial", pos=" ".join(f"{v:.6f}" for v in vr), mass=f"{gr['mass']:.6f}", diaginertia=" ".join(f"{v:.9f}" for v in inertia_box(gr["mass"], gr["size"])))
                    ET.SubElement(gb, "geom", pos=" ".join(f"{v:.6f}" for v in vr), size=" ".join(f"{v / 2:.6f}" for v in gr["size"]))
                    recurse(gb, grand["child"], go)
            recurse(child_body, joint["child"], child_origin)

    add_body(world, "base_link", frames["base_link"], (0, 0, 0))
    actuator = ET.SubElement(model, "actuator")
    for joint in joints:
        ET.SubElement(actuator, "motor", name=f"M_{joint['name']}", joint=joint["name"], ctrllimited="true", ctrlrange="-1 1", gear="1")
    ET.indent(model)
    (OUT / "hr30.xml").write_text(ET.tostring(model, encoding="unicode") + "\n", encoding="utf-8")


def write_mass_budget(rows: list[dict]) -> dict:
    total_mass = sum(row["mass"] for row in rows)
    com = tuple(sum(row["mass"] * row["center"][i] for row in rows) / total_mass for i in range(3))
    total_inertia = [0.0, 0.0, 0.0]
    out_rows = []
    for row in rows:
        local = inertia_box(row["mass"], row["size"])
        dx, dy, dz = (row["center"][i] - com[i] for i in range(3))
        about_total = (
            local[0] + row["mass"] * (dy * dy + dz * dz),
            local[1] + row["mass"] * (dx * dx + dz * dz),
            local[2] + row["mass"] * (dx * dx + dy * dy),
        )
        total_inertia = [total_inertia[i] + about_total[i] for i in range(3)]
        out_rows.append({
            "link": row["link"], "assembly_group": row["group"], "allocated_mass_kg": f"{row['mass']:.6f}",
            "neutral_com_x_m": f"{row['center'][0]:.6f}", "neutral_com_y_m": f"{row['center'][1]:.6f}", "neutral_com_z_m": f"{row['center'][2]:.6f}",
            "local_ixx_kg_m2": f"{local[0]:.9f}", "local_iyy_kg_m2": f"{local[1]:.9f}", "local_izz_kg_m2": f"{local[2]:.9f}",
            "status": "P0.1 ALLOCATION ESTIMATE - NOT CAD/MEASURED MASS PROPERTY",
        })
    out_rows.append({
        "link": "TOTAL", "assembly_group": "whole robot", "allocated_mass_kg": f"{total_mass:.6f}",
        "neutral_com_x_m": f"{com[0]:.6f}", "neutral_com_y_m": f"{com[1]:.6f}", "neutral_com_z_m": f"{com[2]:.6f}",
        "local_ixx_kg_m2": f"{total_inertia[0]:.9f}", "local_iyy_kg_m2": f"{total_inertia[1]:.9f}", "local_izz_kg_m2": f"{total_inertia[2]:.9f}",
        "status": "P0.1 WHOLE-BODY BUDGET - MUST BE REPLACED BY AS-BUILT CAD AND SCALE/IDENTIFICATION",
    })
    write_csv(OUT / "mass-properties-budget.csv", out_rows)
    write_csv(OUT / "mass-allocation-register.csv", [
        {"assembly": "head and neck", "target_kg": 0.45, "maximum_kg": 0.55, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 0.500", "status": "WITHIN MAXIMUM - PHYSICAL PROPERTY OPEN"},
        {"assembly": "chest compute and waist", "target_kg": 1.20, "maximum_kg": 1.35, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 1.830", "status": "OVER MAXIMUM - REDESIGN/REALLOCATION REQUIRED"},
        {"assembly": "two arms and hands", "target_kg": 1.30, "maximum_kg": 1.50, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 1.600", "status": "OVER MAXIMUM - REDESIGN/REALLOCATION REQUIRED"},
        {"assembly": "pelvis power and restraint structure", "target_kg": 1.40, "maximum_kg": 1.75, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 1.650", "status": "WITHIN P0.1 REALLOCATED MAXIMUM - PHYSICAL PROPERTY OPEN"},
        {"assembly": "two legs and feet", "target_kg": 3.40, "maximum_kg": 3.80, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 4.050", "status": "OVER MAXIMUM - REDESIGN/REALLOCATION REQUIRED"},
        {"assembly": "wiring covers fasteners and uncertainty", "target_kg": 0.60, "maximum_kg": 0.80, "cad_mass_kg": "INTEGRATED INTO LINK ALLOCATIONS", "status": "OPEN - MUST BE SEPARATED IN DETAILED CAD"},
        {"assembly": "TOTAL", "target_kg": 8.00, "maximum_kg": 10.00, "cad_mass_kg": "P0.1 ALLOCATION ESTIMATE 9.630", "status": "WITHIN PROGRAM MAXIMUM BY BUDGET ONLY - AS-BUILT MASS OPEN"},
    ])
    return {"mass_kg": total_mass, "com_m": com, "inertia_kg_m2": tuple(total_inertia)}


def write_budgets_and_bom() -> None:
    power = [
        ("12 leg actuators", "ACTUATOR", 14.8, 96, 480, "simultaneous stall prohibited; measured gait duty required"),
        ("waist + shoulders + elbows", "ACTUATOR", 14.8, 35, 175, "candidate operating estimate; limits unverified"),
        ("wrists + grippers", "ACTUATOR", 14.8, 12, 48, "grip-force and duty-cycle proof required"),
        ("head pan/tilt", "ACTUATOR", 14.8, 2, 8, "candidate operating estimate"),
        ("Raspberry Pi 5 compute", "COMPUTE", 5.1, 18, 27, "official 27 W supply envelope is not installed consumption evidence"),
        ("motion/safety controllers + buses", "CONTROL", 5.0, 8, 15, "exact controller/transceiver selections required"),
        ("display/cameras/audio/network", "HMI", 5.0, 14, 30, "exact devices and audio duty required"),
        ("conversion/cooling allowance", "LOSS/MARGIN", 0, 12, 28, "converter curves and installed thermal test required"),
    ]
    write_csv(OUT / "power-energy-budget.csv", [{
        "load": r[0], "domain": r[1], "candidate_voltage_v": r[2] or "MULTIRAIL", "operating_budget_w": r[3], "short_peak_budget_w": r[4], "basis_and_hold": r[5],
        "status": "P0.1 BUDGET - PROTECTION/CONDUCTOR/SOURCE SELECTION REQUIRED",
    } for r in power] + [{
        "load": "WHOLE ROBOT", "domain": "TOTAL", "candidate_voltage_v": "14.8 V primary / regulated auxiliaries", "operating_budget_w": sum(r[3] for r in power), "short_peak_budget_w": sum(r[4] for r in power),
        "basis_and_hold": "tether-first; onboard concept 14.8 V nominal 12 Ah / 177.6 Wh with <=75% usable planning fraction gives about 42 minutes at budget load; chemistry/BMS/enclosure/disconnect/protection/charger remain SELECTION REQUIRED",
        "status": "P0.1 BUDGET - NO SOURCE OR ENERGIZATION AUTHORITY",
    }])
    thermal = [
        ("leg actuators", 58, "distributed aluminum housings; no enclosed hot pockets", "thermistor/current logging per joint"),
        ("upper-body actuators", 23, "conduct to frames plus natural/forced convection", "thermistor/current logging per joint"),
        ("compute", 18, "Pi Active Cooler candidate plus controlled torso airflow", "CPU throttling, fan tach and inlet/outlet temperatures"),
        ("display/audio/sensors", 9, "head vent path separated from microphones", "head inlet/outlet and panel temperature"),
        ("conversion/distribution", 12, "pelvis/torso conductive mounting and airflow", "converter, contactor and conductor temperatures"),
        ("uncertainty margin", 15, "reserved; must not be spent before measured closure", "whole-body thermal balance"),
    ]
    write_csv(OUT / "thermal-budget.csv", [{"domain": r[0], "candidate_heat_w": r[1], "heat_rejection_path": r[2], "required_telemetry": r[3], "status": "P0.1 ESTIMATE - INSTALLED STEADY/TRANSIENT THERMAL TEST REQUIRED"} for r in thermal] + [{"domain": "TOTAL", "candidate_heat_w": sum(r[1] for r in thermal), "heat_rejection_path": "forced-air architecture required by budget", "required_telemetry": "all domains plus ambient and shutdown reason", "status": "P0.1 135 W REJECTION BUDGET - UNVALIDATED"}])
    compute = [
        ("Conversational compute", "Raspberry Pi 5 8GB SC1112 candidate", 1, "OpenAI client, speech/UI, logging; never writes actuator registers", "Ethernet/Wi-Fi to network; authenticated localhost IPC"),
        ("Deterministic motion controller", "STM32H743-class controller board; exact order code SELECTION REQUIRED", 1, "state estimation, trajectory interpolation, limits, watchdogs", "five isolated/segmented RS-485 channels plus safety I/O"),
        ("Independent watchdog", "Raspberry Pi Pico 1 SC0915 candidate; non-safety-rated", 1, "heartbeat supervision only; zero functional-safety credit", "hardwired permit request to independent safety architecture"),
        ("Pelvis IMU", "industrial-grade 6/9-axis IMU SELECTION REQUIRED", 1, "body attitude/rate", "deterministic SPI/CAN candidate"),
        ("Foot force sensing", "four-corner load cells per foot + ADC SELECTION REQUIRED", 8, "support polygon and contact state", "two local deterministic sensor nodes"),
        ("Joint output encoders", "absolute encoders on all reduced leg axes; exact model SELECTION REQUIRED", 8, "post-transmission joint angle", "deterministic local buses"),
        ("Vision", "Raspberry Pi Camera Module 3 Wide-class candidate", 2, "stereo/depth-development input; no safety role", "CSI to conversational compute"),
        ("Microphones", "four-microphone array candidate", 1, "far-field speech capture; no safety role", "USB/I2S; privacy control required"),
        ("Speakers", "two 3 W full-range speakers + class-D amplifier", 2, "speech and non-safety status tones", "I2S; volume ceiling required"),
        ("Face screen", "5-inch 800x480 HDMI/DSI IPS candidate", 1, "expressions, status and privacy indication", "DSI/HDMI; exact panel SELECTION REQUIRED"),
        ("Actuator buses", "five independent RS-485 segments", 5, "left/right legs, left/right arms, head/waist", "termination only at physical ends; shield/return topology open"),
    ]
    write_csv(OUT / "compute-sensor-network-budget.csv", [{"function": r[0], "candidate": r[1], "quantity": r[2], "role_boundary": r[3], "interface": r[4], "status": "P0.1 CANDIDATE - EXACT DEVICE/INTERFACE/EMC/THERMAL EVIDENCE REQUIRED"} for r in compute])
    cost = [
        ("25 actuator population", 9700, "planning allowance; not vendor quotes"),
        ("transmissions, bearings and output encoders", 1900, "ratios and exact hardware open"),
        ("frames, machined plates, printed covers and fasteners", 2200, "Boston-area prototype allowance"),
        ("compute, sensing, display and audio", 1100, "exact device selection open"),
        ("power source, conversion, protection and harness", 1500, "tether/battery alternatives unresolved"),
        ("independent safety/control enclosure and restraint", 1800, "not a safety approval"),
        ("prototype spares, tooling and contingency", 2800, "development reserve"),
    ]
    write_csv(OUT / "cost-budget.csv", [{"cost_group": r[0], "planning_allowance_usd": r[1], "basis": r[2], "status": "BUDGETARY ALLOWANCE ONLY - NO PROCUREMENT AUTHORITY"} for r in cost] + [{"cost_group": "TOTAL", "planning_allowance_usd": sum(r[1] for r in cost), "basis": "P0.1 program planning total; excludes labor, qualified review, test facility and redesign", "status": "BUDGETARY ALLOWANCE ONLY"}])

    bom = [
        ("HR30-BOM-001", "leg actuator", "ROBOTIS", "XH540-W270-R evaluation candidate", 12, 525),
        ("HR30-BOM-002", "waist/shoulder/elbow actuator", "ROBOTIS", "XM540-W270-R candidate", 7, 355),
        ("HR30-BOM-003", "wrist actuator", "ROBOTIS", "XM430-W350-R candidate", 2, 250),
        ("HR30-BOM-004", "head/gripper actuator", "ROBOTIS", "XC330-class compact candidate; exact model SELECTION REQUIRED", 4, 105),
        ("HR30-BOM-005", "main compute", "Raspberry Pi", "Raspberry Pi 5 8GB SC1112 candidate", 1, 125),
        ("HR30-BOM-006", "compute cooling", "Raspberry Pi", "Active Cooler SC1148 candidate", 1, 12),
        ("HR30-BOM-007", "compute storage", "Kingston", "SDCIT2/64GBSP candidate", 1, 55),
        ("HR30-BOM-008", "motion controller", "SELECTION REQUIRED", "STM32H743-class controller board", 1, 120),
        ("HR30-BOM-009", "independent watchdog", "Raspberry Pi", "Pico 1 SC0915 candidate; non-safety-rated", 1, 8),
        ("HR30-BOM-010", "RS-485 interfaces", "ROBOTIS/custom", "U2D2 or isolated transceiver equivalent per segment", 5, 45),
        ("HR30-BOM-011", "face display", "SELECTION REQUIRED", "5-inch 800x480 HDMI/DSI IPS display", 1, 85),
        ("HR30-BOM-012", "camera", "Raspberry Pi", "Camera Module 3 Wide-class candidate", 2, 45),
        ("HR30-BOM-013", "microphone array", "SELECTION REQUIRED", "four-microphone USB/I2S array", 1, 70),
        ("HR30-BOM-014", "speaker", "SELECTION REQUIRED", "3 W full-range 40 mm candidate", 2, 12),
        ("HR30-BOM-015", "audio amplifier", "SELECTION REQUIRED", "stereo class-D I2S candidate", 1, 25),
        ("HR30-BOM-016", "pelvis IMU", "SELECTION REQUIRED", "industrial 6/9-axis IMU", 1, 160),
        ("HR30-BOM-017", "foot force sensing", "SELECTION REQUIRED", "four-corner load-cell and ADC set per foot", 2, 120),
        ("HR30-BOM-018", "output absolute encoder", "SELECTION REQUIRED", "reduced leg joint encoder", 8, 70),
        ("HR30-BOM-019", "leg reductions", "SELECTION REQUIRED", "1.5:1 pitch-axis and 2.0:1 roll-axis geometric candidates; exact belt, pulley, bearing and retention selections open", 10, 90),
        ("HR30-BOM-020", "joint support", "SELECTION REQUIRED", "dual-bearing shaft stack per load-bearing axis", 25, 35),
        ("HR30-BOM-021", "frame plates", "custom", "6061-T6/T651 machined plate set; drawings/material release open", 1, 900),
        ("HR30-BOM-022", "shells", "custom", "printed removable cover set; material/process open", 1, 450),
        ("HR30-BOM-023", "feet", "custom", "machined/printed foot core + replaceable compliant sole", 2, 180),
        ("HR30-BOM-024", "gripper pads", "custom", "replaceable broad compliant pad set", 2, 45),
        ("HR30-BOM-025", "development power", "SELECTION REQUIRED", "tethered current-limited 14.8 V-class source", 1, 500),
        ("HR30-BOM-026", "onboard energy", "SELECTION REQUIRED", "14.8 V nominal 12 Ah-class pack/BMS concept", 1, 600),
        ("HR30-BOM-027", "main disconnect/contactors", "SELECTION REQUIRED", "DC-rated redundant interruption architecture", 1, 450),
        ("HR30-BOM-028", "emergency stop/reset", "Pilz/IDEC/Schneider candidates", "dual-channel E-stop, monitored reset and EDM hardware", 1, 950),
        ("HR30-BOM-029", "fall restraint", "SELECTION REQUIRED", "rated overhead gantry/harness/load-limiter system", 1, 1200),
        ("HR30-BOM-030", "harness/connectors", "SELECTION REQUIRED", "segmented power/data harness with service loops", 1, 750),
        ("HR30-BOM-031", "cooling", "SELECTION REQUIRED", "torso/head filtered fan and duct set", 1, 150),
        ("HR30-BOM-032", "fasteners/inserts", "SELECTION REQUIRED", "metric serviceable fastener system", 1, 350),
    ]
    write_csv(OUT / "whole-robot-candidate-bom.csv", [{
        "item_id": r[0], "function": r[1], "manufacturer": r[2], "candidate": r[3], "quantity": r[4], "planning_allowance_usd_each": r[5],
        "selection_state": "CANDIDATE / SELECTION REQUIRED", "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY",
    } for r in bom])


def write_action_schema() -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://project-button.local/schemas/hr30-action-request-p0.1.json",
        "title": "HR-30 high-level action request P0.1",
        "type": "object", "additionalProperties": False,
        "required": ["request_id", "issued_at_utc", "expires_after_ms", "action", "parameters", "constraints"],
        "properties": {
            "request_id": {"type": "string", "pattern": "^[A-Za-z0-9_-]{8,64}$"},
            "issued_at_utc": {"type": "string", "format": "date-time"},
            "expires_after_ms": {"type": "integer", "minimum": 50, "maximum": 2000},
            "action": {"enum": ["SPEAK", "LOOK_AT", "OPEN_HAND", "CLOSE_HAND", "PRESENT_OBJECT", "RELEASE_OBJECT", "STAND_PREPARE", "WEIGHT_SHIFT_REQUEST", "STEP_REQUEST", "STOP_REQUEST"]},
            "parameters": {"type": "object", "additionalProperties": False, "properties": {
                "side": {"enum": ["LEFT", "RIGHT", "BOTH", "NONE"]},
                "target_frame": {"type": "string", "maxLength": 64},
                "text": {"type": "string", "maxLength": 500},
                "distance_m": {"type": "number", "minimum": 0, "maximum": 0.10},
                "duration_s": {"type": "number", "minimum": 0.05, "maximum": 10.0},
            }},
            "constraints": {"type": "object", "additionalProperties": False, "required": ["supervised", "require_confirmed_object", "max_speed_scale"], "properties": {
                "supervised": {"const": True}, "require_confirmed_object": {"type": "boolean"},
                "max_speed_scale": {"type": "number", "minimum": 0.0, "maximum": 0.25},
            }},
        },
    }
    (OUT / "structured-action-request.schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


def write_docs(mass_summary: dict) -> None:
    (OUT / "gripper-functional-specification.md").write_text(f"""# HR-30 two-hand gripper functional specification P0.1

**{WARNING}**

Each wrist terminates in a visible, one-DOF, symmetric two-finger gripper: a 50 x 58 x 36 mm palm, two 18 x 44 x 46 mm broad fingers, and two replaceable 16 x 48 x 8 mm compliant-pad lands. The commanded closure axis is robot X. The palm packages one transversely mounted XC330-class compact actuator and a visible symmetric-coupler candidate; the final linkage and compliance element remain selection required.

The required behaviors are **grasp**, **hold**, **present**, and **release** a lightweight foam block. P0.1 provisional limits are a 26 mm coupled stroke, 0.25 speed scale, 20 N total normal-force ceiling, 0.5 kg object-mass ceiling, and mandatory current/force/position disagreement shutdown. These are development limits, not validated capability. Narrow scissor points, trapping gaps below the guarded minimum, self-locking closure without a manual release, and any cloud-originated raw position/current command are rejected.

Closure requires dimensioned linkage CAD, output-force/current calibration, compliant pad force-stroke and wear evidence, breakaway/manual-release test, object-presence sensing, pinch probe tests, holding-power-loss behavior, and supervised grasp/present/release trials.
""", encoding="utf-8")

    (OUT / "walking-development-architecture.md").write_text(f"""# HR-30 standing and walking-development architecture P0.1

**{WARNING}**

The whole body has six commanded axes per leg: hip yaw/roll/pitch, knee pitch, and ankle pitch/roll. Pitch joints reserve 1.5:1 belt reductions, dual-supported outputs and output encoders; hip roll reserves a higher-reduction path and remains blocked from direct-drive release. Each foot is 90 x 145 mm with four-corner force sensing and a replaceable compliant sole. The neutral estimated mass is {mass_summary['mass_kg']:.2f} kg with estimated COM Z={mass_summary['com_m'][2]:.3f} m; these are allocation-model values, not measured properties.

Control layers are: embedded actuator current/velocity loops; a deterministic local motion controller for joint interpolation, state estimation, support-polygon checks and limits; a separately powered watchdog/permit path with zero safety credit until validated; and a Raspberry Pi/OpenAI conversational layer that can request only named behaviors. Loss or staleness of the conversational layer never becomes a motion request.

Development sequence:

1. **S0 — unpowered/suspended:** verify axes, hard stops, cable sweep, mass, COM, encoder sign and restraint clearances.
2. **S1 — individually powered/suspended:** one joint at a time under current and travel limits; characterize torque, decay, regeneration and thermal behavior.
3. **S2 — restrained double support:** feet on force plates, overhead restraint carrying no nominal weight; establish stand preparation and power-loss capture.
4. **S3 — weight transfer:** slow lateral/fore-aft COM shifts within a measured support margin; no foot lift.
5. **S4 — tethered step initiation:** unload one foot, lift <=10 mm, replace it at the same location, then arrest and inspect.
6. **S5 — tethered capture steps:** predeclared <=50 mm steps on a level guarded surface with stopping and recovery envelopes.
7. **S6 — repeated tethered walking:** only after thermal, power, bus-latency, state-estimation and restraint results close.
8. **S7 — untethered walking:** future program gate; prohibited by P0.1.

The fall-restraint architecture is a rated overhead gantry, swivel, energy-limiting element and torso/pelvis harness attached to a dedicated structural interface. It must prevent head/floor contact throughout the development envelope without becoming a lifting command or destabilizing tether. Exact working-load limit, dynamic arrest load, attachment geometry and qualified inspection remain selection required.
""", encoding="utf-8")

    (OUT / "embodied-agent-architecture.md").write_text(f"""# HR-30 conversational and embodied-agent architecture P0.1

**{WARNING}**

OpenAI is used only for conversation, perception-assisted intent formation and a **high-level structured action request**. The official OpenAI function-calling guide describes function tools as JSON-schema-defined interfaces and model outputs as tool-call requests that application code may handle; it does not grant the model authority over hardware. Source: [OpenAI Function calling guide](https://developers.openai.com/api/docs/guides/function-calling), accessed 2026-08-13.

The cloud-facing process runs on the Raspberry Pi and exposes one tool shaped by `structured-action-request.schema.json`. Exact model/API/voice-pipeline selection remains open. It has no actuator-bus credentials, no safety-I/O handle and no raw joint/current/torque tool. Requests are authenticated over local IPC and include a unique ID, timestamp, <=2 s expiry, named action, bounded parameters and supervised constraint.

The deterministic local gateway rejects a request unless schema, signature/session, freshness, replay protection, current operating mode, supervisor-enable state, scene/object preconditions, joint/velocity/force limits, support state and behavior availability all pass. It translates an accepted request only into a versioned local behavior primitive. `STEP_REQUEST`, `WEIGHT_SHIFT_REQUEST` and powered arm actions remain disabled until their physical development gates are separately released. Any invalid/stale request, communications loss, watchdog loss, sensor disagreement or E-stop yields reject/hold/controlled stop according to the validated local state machine—never a guessed fallback motion.

Data flow is: microphones/cameras -> local privacy/status gate -> conversational process -> structured request -> deterministic validator -> approved behavior library -> trajectory generator -> local motion controller -> segmented RS-485 buses. Feedback and denial reasons may return upward; the cloud process never closes the permit chain. Audio/video retention, consent, child/privacy policy, network security and offline behavior remain open.
""", encoding="utf-8")

    (OUT / "modular-fabrication-assembly-electrification-plan.md").write_text(f"""# HR-30 modular fabrication, assembly and staged-electrification plan P0.1

**{WARNING}**

The authoritative modules are: H01 head/screen/audio/vision; N01 two-axis neck; T01 torso/frame/compute; P01 pelvis/power/restraint; A01/A02 left/right arms; G01/G02 left/right grippers; L01/L02 left/right legs; F01/F02 left/right feet; C01 local controller; S01 independent safety enclosure; and HN01 segmented harness. Each has a released interface-control drawing, mass ceiling, connector boundary, datum set and revision before fabrication.

Fabrication route: machine the load-bearing joint side plates, shafts and bearing lands from released metal stock; print only removable shells, ducts, fixtures and non-credited covers from a selected process/material; buy exact bearings, reductions, actuators, fasteners and connectors; inspect received identities and material certificates; then perform first-article dimensional inspection. Library/makerspace CNC capability may support prototype plates only after DFM, fixturing, tool-access, tolerance and supervision review. Safety-credited or fall-load parts require a qualified supplier/reviewer disposition.

Assembly order: feet -> ankle modules -> shins -> knees -> thighs -> pelvis -> restraint interface -> torso -> neck/head -> arms -> grippers -> stationary harness -> moving-joint service loops -> covers. At every module boundary, complete fastener torque witness, free-motion/stop check, encoder sign/zero, continuity/isolation, pull/retention and mass record before adding the next module.

Electrification stages are deliberately separate:

1. **E0 unpowered:** dimensional/assembly inspection, bonding plan, continuity/isolation, connector keying, E-stop contact inspection and manual motion.
2. **E1 controls only:** current-limited auxiliary supply; no actuator rail connected; boot, logging, watchdog and all failure-state tests.
3. **E2 one actuator on a bench:** mechanical joint removed from the body or rigidly restrained; characterize current, torque proxy, thermal, comms and power removal.
4. **E3 one suspended limb:** branch protection and local stop limits; no ground contact.
5. **E4 suspended whole body:** all buses enumerated with outputs disabled, then one axis at a time under approved test authorization.
6. **E5 restrained standing:** overhead arrest and guarded zone, double support only.
7. **E6 walking development:** only the S2-S6 sequence in the walking architecture.

Every stage requires an explicit, signed test authorization tied to exact as-built hardware. P0.1 supplies architecture, not that authorization.
""", encoding="utf-8")


def update_web_and_status(mass_summary: dict) -> None:
    page = (OUT / "index.html").read_text(encoding="utf-8")
    page = page.replace('<div class="metric">43</div><p>Candidate physical envelopes', '<div class="metric">52</div><p>Candidate physical envelopes')
    marker = '<section><h2>Download the engineering artifacts</h2>'
    start_marker = "<!-- HR30-SYSTEM-P01-START -->"
    end_marker = "<!-- HR30-SYSTEM-P01-END -->"
    if start_marker in page and end_marker in page:
        page = page.split(start_marker, 1)[0] + page.split(end_marker, 1)[1]
    added = f'''{start_marker}<section><h2>The P0.1 engineering package is whole-body</h2><div class="grid"><article class="card pass"><h3>Floating-base dynamics</h3><p>URDF and MJCF cover all 25 commanded axes with an unanchored base and provisional masses, inertias, geometry and limits.</p></article><article class="card hold"><h3>Mass and energy</h3><p>{mass_summary['mass_kg']:.2f} kg allocation estimate, {mass_summary['com_m'][2]:.3f} m neutral COM height, 197 W operating power budget and 135 W heat-rejection budget. All require physical closure.</p></article><article class="card pass"><h3>Embodied-agent boundary</h3><p>OpenAI produces expiring high-level JSON requests only. Deterministic local software and independent hardware retain every motion and permit decision.</p></article><article class="card hold"><h3>Walking path</h3><p>Suspended characterization, restrained standing, weight transfer, capture steps and tethered walking are separate development gates.</p></article></div></section>
<section><h2>System artifacts</h2><div class="panel"><p><a href="hr30.urdf">URDF</a> · <a href="hr30.xml">MJCF</a> · <a href="mass-properties-budget.csv">Mass/COM/inertia</a> · <a href="power-energy-budget.csv">Power/energy</a> · <a href="thermal-budget.csv">Thermal</a> · <a href="compute-sensor-network-budget.csv">Compute/sensors/network</a> · <a href="cost-budget.csv">Cost</a> · <a href="whole-robot-candidate-bom.csv">Whole-robot BOM</a> · <a href="gripper-functional-specification.md">Hands</a> · <a href="walking-development-architecture.md">Walking</a> · <a href="embodied-agent-architecture.md">OpenAI/local-control boundary</a> · <a href="structured-action-request.schema.json">Action schema</a> · <a href="modular-fabrication-assembly-electrification-plan.md">Build/electrification plan</a> · <a href="HR-30_modular_fabrication_candidate.step">Fabrication-candidate STEP</a> · <a href="fabrication-part-register.csv">Part register</a> · <a href="service-panel-interface-register.csv">Service panels</a> · <a href="harness-route-register.csv">Harness routes</a></p></div></section>
<section><h2>Inspect the modular frame, covers, and harness routes</h2><div class="viewer"><model-viewer src="HR-30_modular_fabrication_reference.glb" alt="Interactive preliminary HR-30 modular fabrication architecture with frame plates, removable covers, and harness route corridors" camera-controls camera-orbit="35deg 76deg 95%" min-camera-orbit="auto auto 20%" max-camera-orbit="auto auto 240%" field-of-view="26deg" shadow-intensity="0.85" exposure="1.05" interaction-prompt="auto"></model-viewer><p>Dark blue is the candidate metal frame, sky and mid blue are separately removable covers, gold is the uncredited restraint bridge, orange reserves actuator-power routing, and cyan reserves data and low-voltage routing. These are dimensioned architecture parts and corridors, not released manufacturing drawings or selected cables.</p></div></section>
{end_marker}'''
    if marker not in page:
        raise SystemExit("download marker missing from web guide")
    page = page.replace(marker, added + marker)
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    readme = (OUT / "README.md").read_text(encoding="utf-8").split("\n\n## Whole-body systems completion", 1)[0].rstrip()
    readme += f"""

## Whole-body systems completion

P0.1 now also includes floating-base 25-DOF URDF and MJCF models, a {mass_summary['mass_kg']:.2f} kg allocation model with neutral COM/inertia, power/thermal/compute/network/cost budgets, a whole-robot candidate BOM, two-hand functional requirements, staged standing/walking development, a modular build/electrification plan, and the OpenAI-to-deterministic-controller action boundary. These artifacts make the architecture coherent and simulatable; none converts the open selections or physical validation into work authority.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    status.update({
        "whole_body_system_package_present": True, "urdf_present": True, "mjcf_present": True, "floating_base_dynamics_present": True,
        "provisional_mass_com_inertia_budget_present": True, "power_thermal_compute_network_cost_budgets_present": True,
        "whole_robot_candidate_bom_present": True, "walking_architecture_present": True,
        "embodied_agent_boundary_present": True, "modular_build_plan_present": True,
        "estimated_mass_kg": round(mass_summary["mass_kg"], 6), "estimated_neutral_com_z_m": round(mass_summary["com_m"][2], 6),
        "dynamics_validated": False, "walking_validated": False, "physical_build_ready": False,
    })
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def refresh_manifest_and_release() -> None:
    manifest_path = OUT / "file-manifest.csv"
    if manifest_path.exists():
        manifest_path.unlink()
    files = [path for path in OUT.rglob("*") if path.is_file()]
    write_csv(manifest_path, [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "warning": WARNING} for path in sorted(files)])
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)


def main() -> int:
    if not (OUT / "HR-30_body_architecture_candidate.step").exists():
        raise SystemExit("run generate_hr30_body_architecture_p01.py first")
    rows = link_rows()
    joints = joint_rows()
    if len(joints) != 25 or abs(sum(row["mass"] for row in rows) - 9.63) > 1e-9:
        raise SystemExit("controlled joint/mass allocation drift")
    write_urdf(rows, joints)
    write_mjcf(rows, joints)
    mass_summary = write_mass_budget(rows)
    write_budgets_and_bom()
    write_action_schema()
    write_docs(mass_summary)
    shutil.copy2(Path(__file__), OUT / "system-package-source.py")
    update_web_and_status(mass_summary)
    import generate_hr30_fabrication_architecture_p01 as fabrication
    fabrication.generate_into_package()
    import generate_hr30_mass_reconciliation_p01 as mass_reconciliation
    mass_summary = mass_reconciliation.generate_into_package()
    refresh_manifest_and_release()
    print(json.dumps({
        "identifier": IDENTIFIER,
        "dof": len(joints),
        "mass_kg": mass_summary["reconciled_dynamics_planning_mass_kg"],
        "com_m": mass_summary["reconciled_dynamics_neutral_com_m"],
        "mass_status": mass_summary["program_mass_target_status"],
        "source": str(OUT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
