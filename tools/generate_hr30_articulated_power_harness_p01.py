#!/usr/bin/env python3
"""Generate the HR-30 articulated direct-branch power-harness candidate.

This successor rejects both a rigid guard spanning a moving limb and the
intermediate tap-board cascade that briefly conflicted with the authoritative
25 individually protected branch architecture.  Each actuator keeps one
unspliced two-conductor moving branch from its protection channel to its one
fixed-side transition.  Distal branches cross every upstream joint, so the
whole body contains 76 explicit joint-crossing obligations, not merely one
power loop per actuator.  Rigid guards end before each axis and flexible local
envelopes cover only the moving crossings.  Nothing generated here authorizes
procurement, fabrication, connection, powered testing, motion or energization.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
HARNESS = WHOLE / "harness"
OUT = HARNESS / "articulated-power-harness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
RELEASE_WHOLE = ROOT / "release" / "hr30" / "whole-body-p0.1"
BODY_STEP = WHOLE / "HR-30_body_architecture_candidate.step"
LOOPS = HARNESS / "physical-p0.1" / "service-loop-register.csv"
ROUTE_POINTS = HARNESS / "physical-p0.1" / "route-point-register.csv"
DROPS = HARNESS / "physical-p0.1" / "actuator-power-drop-register.csv"
TRANSITIONS = HARNESS / "physical-p0.1" / "actuator-power-transition-register.csv"
CORES = HARNESS / "distributed-power-harness-successor-p0.1" / "axis-core-allocation.csv"
NODES = HARNESS / "distributed-power-harness-successor-p0.1" / "distribution-node-register.csv"
TRANSITION_STEP = HARNESS / "actuator-transition-brackets-p0.1" / "HR30_25_axis_transition_brackets_candidate.step"
IDENTIFIER = "HR30-ARTICULATED-POWER-HARNESS-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - ARTICULATED ACTUATOR-POWER HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
HARNESS_WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
MARKER = "HR30-ARTICULATED-POWER-HARNESS-P01"
RENDER_TOOL = ROOT / "tools" / "render_glb_preview.py"

# Current direct-branch construction candidate. Values are manufacturer
# geometry/service-life inputs, not an HR-30 ampacity or flex-life release.
CABLE_PART = "CF130.03.02.UL"
CABLE_MANUFACTURER = "igus"
CABLE_GAUGE = "22 AWG"
CABLE_CONDUCTORS = 2
CABLE_OD_MM = 5.0
CABLE_CONTINUOUS_BEND_MULTIPLE = 7.5
CABLE_BEND_RADIUS_MM = CABLE_OD_MM * CABLE_CONTINUOUS_BEND_MULTIPLE
CABLE_NOMINAL_DOUBLE_STROKES = 5_000_000
LANE_GAP_MM = 1.5
GUARD_WALL_MM = 1.5
GUARD_CLEARANCE_MM = 2.0


CHAINS = {
    "HN01_TORSO_POWER_SPINE": ["WAIST_YAW"],
    "HN01_HEAD_POWER_BRANCH": ["HEAD_PAN", "HEAD_TILT"],
    "HN01_L_ARM_POWER": ["L_SHOULDER_PITCH", "L_SHOULDER_ROLL", "L_ELBOW_PITCH", "L_WRIST_ROTATION", "L_GRIPPER"],
    "HN01_R_ARM_POWER": ["R_SHOULDER_PITCH", "R_SHOULDER_ROLL", "R_ELBOW_PITCH", "R_WRIST_ROTATION", "R_GRIPPER"],
    "HN01_L_LEG_POWER": ["L_HIP_YAW", "L_HIP_ROLL", "L_HIP_PITCH", "L_KNEE_PITCH", "L_ANKLE_PITCH", "L_ANKLE_ROLL"],
    "HN01_R_LEG_POWER": ["R_HIP_YAW", "R_HIP_ROLL", "R_HIP_PITCH", "R_KNEE_PITCH", "R_ANKLE_PITCH", "R_ANKLE_ROLL"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "authority": AUTHORITY, "warning": WARNING}


def parse_tuple(text: str) -> tuple[float, float, float]:
    return tuple(float(v.strip()) for v in text.strip().strip("()").split(","))


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def mul(a, s):
    return tuple(a[i] * s for i in range(3))


def length(a):
    return math.sqrt(sum(v * v for v in a))


def unit(a):
    n = length(a)
    if n <= 1e-9:
        raise RuntimeError("zero vector")
    return tuple(v / n for v in a)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def fmt_xyz(p):
    return "{:.3f},{:.3f},{:.3f}".format(*p)


def service_point(axis_id: str, center, axis):
    """Locate the external cable-pack center adjacent to the real joint axis."""
    ax = tuple(abs(v) for v in axis)
    if ax[1] > 0.5:
        return add(center, mul(axis, 28.0 if axis[1] >= 0 else -28.0))
    if ax[0] > 0.5:
        side = 1.0 if center[0] >= 0 else -1.0
        return add(center, (side * 24.0, 0.0, 0.0))
    # Yaw axes are accessible from the rear.  The flexible envelope remains
    # tied to the actual axis line; exact clamps remain unresolved.
    return add(center, (0.0, 0.0, 12.0))


def architecture():
    loop_by_axis = {r["axis_id"]: r for r in read_csv(LOOPS)}
    core_by_axis = {r["axis_id"]: r for r in read_csv(CORES)}
    drop_by_axis = {r["axis_id"]: r for r in read_csv(DROPS)}
    transition_by_axis = {r["axis_id"]: r for r in read_csv(TRANSITIONS)}
    axes = {a for chain in CHAINS.values() for a in chain}
    if any(set(source) != axes for source in (loop_by_axis, core_by_axis, drop_by_axis, transition_by_axis)):
        raise RuntimeError("25-axis direct-branch harness binding drift")

    route_points = read_csv(ROUTE_POINTS)
    root_by_corridor = {}
    for corridor in CHAINS:
        candidates = [r for r in route_points if r["segment_id"] == corridor]
        if len(candidates) != 2:
            raise RuntimeError(f"expected two fixed corridor points for {corridor}")
        first = min(candidates, key=lambda r: int(r["sequence"]))
        root_by_corridor[corridor] = (float(first["x_mm"]), float(first["y_mm"]), float(first["z_mm"]))

    branches: list[dict[str, object]] = []
    transitions: list[dict[str, object]] = []
    for corridor, chain in CHAINS.items():
        for destination in chain:
            core = core_by_axis[destination]
            drop = drop_by_axis[destination]
            transition = transition_by_axis[destination]
            branches.append(common({
                "branch_cable_id": f"DB-{destination}",
                "axis_id": destination,
                "corridor": corridor,
                "bus_id": core["bus_id"],
                "protected_output": drop["protection_topology"],
                "positive_net": drop["branch_net"],
                "return_net": drop["return_net"],
                "candidate_part": CABLE_PART,
                "construction": "2 x 22 AWG / 0.34 mm2; unshielded PVC moving cable",
                "candidate_current_cap_a": core["candidate_current_cap_a"],
                "published_stall_endpoint_a": core["published_stall_endpoint_a"],
                "upstream_joint_crossings": chain.index(destination) + 1,
                "electrical_splices_between_protection_and_transition": 0,
                "fixed_transition": transition["transition_id"],
                "state": "DIRECT INDIVIDUALLY PROTECTED BRANCH CANDIDATE; CUT LENGTH, CRIMP, DERATING AND PHYSICAL PROOF OPEN",
            }))
            transitions.append(common({
                "transition_id": transition["transition_id"],
                "axis_id": destination,
                "power_loop": transition["power_loop"],
                "location_candidate": transition["location_candidate"],
                "moving_cable": transition["moving_cable"],
                "moving_connector": transition["moving_connector"],
                "moving_housing_terminal": transition["moving_housing_terminal"],
                "panel_connector": transition["panel_connector"],
                "panel_housing_terminal": transition["panel_housing_terminal"],
                "pigtail": transition["pigtail"],
                "load_path": transition["load_path"],
                "state": "EXISTING DIMENSIONED FIXED-SIDE TRANSITION CANDIDATE; RECEIVED FIT AND PROCESS VALIDATION OPEN",
            }))

    crossings: list[dict[str, object]] = []
    guards: list[dict[str, object]] = []
    geometry: dict[str, dict[str, object]] = {}
    for corridor, chain in CHAINS.items():
        previous_point = root_by_corridor[corridor]
        for stage, joint_axis in enumerate(chain, start=1):
            loop = loop_by_axis[joint_axis]
            center = parse_tuple(loop["joint_axis_xyz_mm"])
            axis = unit(parse_tuple(loop["joint_axis_direction"]))
            point = service_point(joint_axis, center, axis)
            remaining = chain[stage - 1:]
            cable_count = len(remaining)
            pack_width = cable_count * CABLE_OD_MM + max(0, cable_count - 1) * LANE_GAP_MM
            for lane, destination in enumerate(remaining):
                crossing_id = f"DB-{destination}-AT-{joint_axis}"
                core = core_by_axis[destination]
                crossings.append(common({
                    "crossing_id": crossing_id,
                    "branch_cable_id": f"DB-{destination}",
                    "corridor": corridor,
                    "joint_axis": joint_axis,
                    "destination_axis": destination,
                    "stage": stage,
                    "parallel_pair_index": lane + 1,
                    "parallel_pair_count": cable_count,
                    "crosses_destination_axis": "YES" if destination == joint_axis else "NO - CONTINUES TO DISTAL AXIS",
                    "candidate_part": CABLE_PART,
                    "conductor_configuration": "2 x 22 AWG / 0.34 mm2; one protected VDD and return pair; no intermediate splice",
                    "maximum_hr30_channel_cap_a": f"{float(core['candidate_current_cap_a']):.6f}",
                    "application_ampacity_state": "UNVERIFIED - NO HR-30 BUNDLE/CONNECTOR/TEMPERATURE RELEASE",
                    "outer_diameter_max_mm": f"{CABLE_OD_MM:.3f}",
                    "continuous_flex_radius_factor_d": f"{CABLE_CONTINUOUS_BEND_MULTIPLE:.1f}",
                    "continuous_flex_radius_mm": f"{CABLE_BEND_RADIUS_MM:.3f}",
                    "service_life_input": f"{CABLE_NOMINAL_DOUBLE_STROKES} double strokes at +15..+60 C and 7.5xd manufacturer table boundary",
                    "joint_range": loop["commanded_range"],
                    "nominal_joint_arc_deg": "120",
                    "actual_cut_length": "SELECTION REQUIRED AFTER FULL-RANGE ROUTE SWEEP",
                    "state": "DIMENSIONED NOMINAL DIRECT-BRANCH CROSSING; FULL-RANGE BEND/TWIST/COLLISION AND TERMINATION PROOF OPEN",
                }))
                geometry[crossing_id] = {
                    "axis_id": joint_axis,
                    "destination_axis": destination,
                    "center": center,
                    "axis": axis,
                    "point": point,
                    "previous": previous_point,
                    "lane": lane,
                    "count": cable_count,
                    "pack_width": pack_width,
                }

            guard_base = f"GD-{joint_axis}"
            guards.extend([
                common({
                    "guard_id": f"{guard_base}-LINK",
                    "axis_id": joint_axis,
                    "guard_type": "RIGID LINK-LOCAL U-CHANNEL",
                    "covers": f"{cable_count} direct branch pairs on rigid link; stops before axis",
                    "internal_width_mm": f"{pack_width + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "internal_height_mm": f"{CABLE_OD_MM + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "wall_mm": f"{GUARD_WALL_MM:.3f}",
                    "material_candidate": "printed PA12 or machined polymer; selection required",
                    "joint_spanning": "NO",
                    "cad_solid": f"{guard_base}_LINK_GUARD",
                    "state": "DIMENSIONED CAD CANDIDATE; FASTENERS, ACCESS, IMPACT AND COLLISION OPEN",
                }),
                common({
                    "guard_id": f"{guard_base}-FLEX",
                    "axis_id": joint_axis,
                    "guard_type": "FLEXIBLE JOINT DRESS-PACK ENVELOPE",
                    "covers": f"120-degree nominal arc for {cable_count} independent CF130 pairs",
                    "internal_width_mm": f"{pack_width + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "internal_height_mm": f"{CABLE_OD_MM + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "wall_mm": f"{GUARD_WALL_MM:.3f}",
                    "material_candidate": "corrugated TPU or textile dress-pack sleeve; selection required",
                    "joint_spanning": "YES - FLEXIBLE ONLY; NO RIGID SHELL ACROSS AXIS",
                    "cad_solid": f"{guard_base}_FLEX_GUARD",
                    "state": "DIMENSIONED NOMINAL ENVELOPE; CORRUGATION, ATTACHMENT, PINCH AND FATIGUE PROOF OPEN",
                }),
            ])
            previous_point = point

    if len(branches) != 25 or len(transitions) != 25 or len(crossings) != 76 or len(guards) != 50:
        raise RuntimeError(
            f"direct architecture count drift: {len(branches)} branches {len(transitions)} transitions "
            f"{len(crossings)} crossings {len(guards)} guards"
        )
    return branches, transitions, crossings, guards, geometry


def cable_row() -> list[dict[str, object]]:
    return [common({
        "candidate_part": CABLE_PART,
        "manufacturer": CABLE_MANUFACTURER,
        "family": "chainflex medium-duty unshielded moving control cable",
        "conductors": CABLE_CONDUCTORS,
        "gauge": CABLE_GAUGE,
        "nominal_conductor_area_mm2": "0.34",
        "outer_diameter_max_mm": f"{CABLE_OD_MM:.3f}",
        "application_ampacity": "SELECTION REQUIRED - MANUFACTURER TABLE IS NOT AN HR-30 BUNDLE/CONNECTOR RATING",
        "continuous_flex_radius_rule": f"{CABLE_CONTINUOUS_BEND_MULTIPLE:.1f} x cable diameter at +15..+60 C / 5 million double strokes / <10 m travel",
        "continuous_flex_radius_mm": f"{CABLE_BEND_RADIUS_MM:.3f}",
        "nominal_double_strokes": CABLE_NOMINAL_DOUBLE_STROKES,
        "selection_boundary": "candidate geometry only; exact termination, core OD, conductor DCR, bundle derating, torsion and received lot remain selection/validation required",
        "state": "ACTIVE CONSTRUCTION CANDIDATE - NOT RELEASED",
    })]


def disposition_rows() -> list[dict[str, object]]:
    return [
        common({
            "topology_id": "APH-T01", "architecture": "25 DIRECT INDIVIDUALLY PROTECTED TWO-WIRE BRANCHES",
            "disposition": "ACTIVE P0.1 CONSTRUCTION CANDIDATE",
            "reason": "matches physical-p0.1 and actuator-cable-kit-p0.1; zero intermediate electrical splices; one fixed transition per actuator; 76 upstream joint crossings now modeled",
            "selection_credit": "CONFIGURATION CONSISTENCY ONLY - PHYSICAL VALIDATION OPEN",
        }),
        common({
            "topology_id": "APH-T02", "architecture": "25 PASSIVE TAP BOARDS + 45 FOUR-CONDUCTOR CICOIL PIECES",
            "disposition": "REJECTED / SUPERSEDED FOR P0.1",
            "reason": "conflicted with the authoritative direct-branch harness and added 25 boards plus intermediate terminations without a demonstrated packaging, reliability or mass benefit",
            "selection_credit": "NONE",
        }),
        common({
            "topology_id": "APH-T03", "architecture": "ONE RIGID GUARD OR CABLE SPINE ACROSS AN ENTIRE MOVING LIMB",
            "disposition": "REJECTED",
            "reason": "would lock or collide with articulated shoulder, elbow, wrist, hip, knee, ankle, neck or waist joints",
            "selection_credit": "NONE",
        }),
    ]


def source_rows() -> list[dict[str, object]]:
    local = [
        ("APH-S01", LOOPS, "25 named joint axes, ranges and legacy final-axis loop obligations"),
        ("APH-S02", ROUTE_POINTS, "whole-body fixed corridors and route datums"),
        ("APH-S03", CORES, "25 individually protected pair allocations and current caps"),
        ("APH-S04", DROPS, "25 protected output and return-net bindings"),
        ("APH-S05", TRANSITIONS, "25 fixed-side Micro-Fit transition bindings"),
        ("APH-S06", TRANSITION_STEP, "25 placed transition-bracket candidate assemblies"),
        ("APH-S07", NODES, "six root protection/distribution node obligations"),
        ("APH-S08", BODY_STEP, "complete humanoid context for combined GLB"),
        ("APH-S09", RENDER_TOOL, "deterministic Blender engineering-preview renderer"),
    ]
    rows = [common({
        "source_id": sid, "publisher": "Project Button", "document": scope,
        "revision_or_date": "whole-body P0.1 current input", "official_url_or_path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path), "verified_scope": scope,
    }) for sid, path, scope in local]
    rows.extend([
        common({
            "source_id": "APH-S10", "publisher": "igus", "document": "chainflex CF130-UL official product page",
            "revision_or_date": "live official page accessed 2026-08-18; page revision not stated",
            "official_url_or_path": "https://www.igus.com/product/CF130_UL",
            "sha256": "N/A - LIVE PRIMARY SOURCE",
            "verified_scope": "CF130.03.02.UL is 2 x 22 AWG / 0.34 mm2; 5 million double strokes use 7.5xd at +15..+60 C for <10 m travel; application-specific routing remains unverified",
        }),
        common({
            "source_id": "APH-S11", "publisher": "igus", "document": "chainflex control-cable catalog",
            "revision_or_date": "official catalog published 2025; accessed 2026-08-18",
            "official_url_or_path": "https://toolbox.igus.com/wp-content/uploads/2023/08/chainflex-control-cables-catalog.pdf",
            "sha256": "N/A - LIVE PRIMARY SOURCE",
            "verified_scope": "CF130-03-02-UL outer diameter maximum 5.0 mm and nominal weight 27 kg/km",
        }),
    ])
    return rows


def hold_rows() -> list[dict[str, object]]:
    holds = [
        ("APH-H00", "tap-board/Cicoil cascade predecessor", "REJECTED; preserve only in history and do not procure, draw or install intermediate boards"),
        ("APH-H01", "complete path and cut length", "route each of 25 direct branches from its protection output across every registered upstream joint to the fixed transition; measure on a full-scale dressed body"),
        ("APH-H02", "CF130-to-Micro-Fit termination", "igus core-OD drawing or written disposition, received-lot measurement, exact tool/process, crimp cross-section and pull tests"),
        ("APH-H03", "full-range bend and torsion applicability", "manufacturer application review plus exact 25-axis motion spectrum and service-life calculation/cycling"),
        ("APH-H04", "fixed transition physical proof", "received 43025/43020 fit, bracket/fastener/clamp proof, pigtail length, retention and no-load-at-contact test"),
        ("APH-H05", "full-range joint kinematics", "sweep all 76 direct-branch crossings through exact min/max poses and fall-restraint envelope"),
        ("APH-H06", "whole-body collision and pinch clearance", "exact body/guard/cable collision sweeps in neutral, crouch, weight transfer, step and restrained-fall configurations"),
        ("APH-H07", "ampacity and voltage drop", "received conductor DCR, ambient/bundle/connector derating, duty-cycle currents, fault current and temperature-rise tests"),
        ("APH-H08", "rigid guard and flexible dress-pack design", "material, wall/corrugation, attachment, removability, impact, snag, chafe, flame and human-contact validation"),
        ("APH-H09", "mass and COM update", "supplier mass plus as-built cable/connector/guard mass reconciled into whole-body budget"),
        ("APH-H10", "EMC and power/data separation", "final routed data harness plus shield/reference-bond plan and emissions/immunity tests"),
        ("APH-H11", "prototype proof", "unpowered full-scale dress build, continuity/insulation/polarity checks, then separately authorized current-limited motion cycling"),
        ("APH-H12", "qualified release review", "signed mechanical/electrical/functional-safety review after preceding evidence exists"),
    ]
    return [common({"hold_id": hid, "unresolved_item": item, "evidence_required": evidence, "state": "OPEN", "execution": "NOT EXECUTED"}) for hid, item, evidence in holds]


def orient_from_z(shape, cq, axis):
    if abs(axis[2]) > 0.9:
        if axis[2] < 0:
            return shape.rotate((0, 0, 0), (1, 0, 0), 180)
        return shape
    if abs(axis[0]) > 0.9:
        return shape.rotate((0, 0, 0), (0, 1, 0), 90 if axis[0] > 0 else -90)
    return shape.rotate((0, 0, 0), (1, 0, 0), -90 if axis[1] > 0 else 90)


def arc_solid(cq, radius, radial_thickness, axial_width, angle=120.0):
    return (
        cq.Workplane("XZ")
        .moveTo(radius, 0.0)
        .rect(radial_thickness, axial_width)
        .revolve(angle, (0, 0), (0, 1))
        .val()
        .rotate((0, 0, 0), (0, 0, 1), -angle / 2.0)
    )


def prism_between(cq, p0, p1, width, height):
    direction = unit(sub(p1, p0))
    reference = (0.0, 0.0, 1.0) if abs(dot(direction, (0.0, 0.0, 1.0))) < 0.9 else (1.0, 0.0, 0.0)
    xdir = unit(cross(reference, direction))
    plane = cq.Plane(origin=cq.Vector(*p0), xDir=cq.Vector(*xdir), normal=cq.Vector(*direction))
    return cq.Workplane(plane).rect(width, height).extrude(length(sub(p1, p0))).val()


def offset_span(p0, p1, offset):
    direction = unit(sub(p1, p0))
    reference = (0.0, 0.0, 1.0) if abs(dot(direction, (0.0, 0.0, 1.0))) < 0.9 else (1.0, 0.0, 0.0)
    lateral = unit(cross(reference, direction))
    return add(p0, mul(lateral, offset)), add(p1, mul(lateral, offset))


def export_cad(geometry: dict[str, dict[str, object]]) -> None:
    import cadquery as cq

    harness = cq.Assembly(name="HR30_ARTICULATED_POWER_HARNESS_P01")
    combined = cq.Assembly(name="HR30_WHOLE_BODY_ARTICULATED_POWER_HARNESS_P01")
    body = cq.importers.importStep(str(BODY_STEP)).val()
    combined.add(body, name="HR30_BODY_REFERENCE", color=cq.Color(0.68, 0.77, 0.84, 0.38))
    cable_color = cq.Color(0.95, 0.58, 0.03)
    guard_color = cq.Color(0.06, 0.42, 0.72, 0.32)
    transition_color = cq.Color(0.05, 0.42, 0.23)

    by_axis: dict[str, list[tuple[str, dict[str, object]]]] = {}
    for piece_id, geom in geometry.items():
        by_axis.setdefault(str(geom["axis_id"]), []).append((piece_id, geom))

    for axis_id, pieces in sorted(by_axis.items()):
        exemplar = pieces[0][1]
        center = exemplar["center"]
        axis = exemplar["axis"]
        count = int(exemplar["count"])
        pack_width = float(exemplar["pack_width"])
        previous = exemplar["previous"]
        point = exemplar["point"]
        for piece_id, geom in sorted(pieces):
            lane = int(geom["lane"])
            offset = (lane - (count - 1) / 2.0) * (CABLE_OD_MM + LANE_GAP_MM)
            loop = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_OD_MM, CABLE_OD_MM)
            loop = loop.translate((0.0, 0.0, offset))
            loop = orient_from_z(loop, cq, axis).translate(center)
            harness.add(loop, name=f"{piece_id}_DIRECT_FLEX_ARC", color=cable_color)
            combined.add(loop, name=f"{piece_id}_DIRECT_FLEX_ARC", color=cable_color)
            if previous is not None and length(sub(point, previous)) > 5.0:
                span_start, span_end = offset_span(previous, point, offset)
                span = prism_between(cq, span_start, span_end, CABLE_OD_MM, CABLE_OD_MM)
                harness.add(span, name=f"{piece_id}_DIRECT_LINK_SPAN", color=cable_color)
                combined.add(span, name=f"{piece_id}_DIRECT_LINK_SPAN", color=cable_color)

        outer = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_OD_MM + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM), pack_width + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM))
        inner = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_OD_MM + 2 * GUARD_CLEARANCE_MM, pack_width + 2 * GUARD_CLEARANCE_MM)
        flex_guard = outer.cut(inner)
        flex_guard = orient_from_z(flex_guard, cq, axis).translate(center)
        harness.add(flex_guard, name=f"GD-{axis_id}_FLEX_GUARD", color=guard_color)
        combined.add(flex_guard, name=f"GD-{axis_id}_FLEX_GUARD", color=guard_color)
        if previous is not None and length(sub(point, previous)) > 5.0:
            outer_span = prism_between(cq, previous, point, pack_width + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM), CABLE_OD_MM + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM))
            inner_span = prism_between(cq, sub(previous, mul(unit(sub(point, previous)), 0.5)), add(point, mul(unit(sub(point, previous)), 0.5)), pack_width + 2 * GUARD_CLEARANCE_MM, CABLE_OD_MM + 2 * GUARD_CLEARANCE_MM)
            link_guard = outer_span.cut(inner_span)
            harness.add(link_guard, name=f"GD-{axis_id}_LINK_GUARD", color=guard_color)
            combined.add(link_guard, name=f"GD-{axis_id}_LINK_GUARD", color=guard_color)

    transitions = cq.importers.importStep(str(TRANSITION_STEP)).val()
    harness.add(transitions, name="HR30_25_AXIS_FIXED_TRANSITIONS", color=transition_color)
    combined.add(transitions, name="HR30_25_AXIS_FIXED_TRANSITIONS", color=transition_color)

    harness.save(str(OUT / "HR-30_articulated_power_harness_candidate.step"))
    harness.save(str(OUT / "HR-30_articulated_power_harness_candidate.glb"), tolerance=0.35, angularTolerance=0.22)
    combined.save(str(OUT / "HR-30_whole_body_articulated_power_harness_candidate.glb"), tolerance=0.65, angularTolerance=0.30)


def render_preview() -> None:
    candidates = [
        shutil.which("blender"),
        r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
    ]
    blender = next((Path(value) for value in candidates if value and Path(value).is_file()), None)
    if blender is None:
        raise RuntimeError("Blender is required to regenerate the articulated-harness poster")
    subprocess.run([
        str(blender), "--background", "--python", str(RENDER_TOOL), "--",
        str(OUT / "HR-30_whole_body_articulated_power_harness_candidate.glb"),
        str(OUT / "articulated-power-harness-preview.png"),
    ], check=True)


def svg_rejected_tap_board_predecessor(boards: list[dict[str, object]], crossings: list[dict[str, object]]) -> str:
    rows = []
    for corridor, axes in CHAINS.items():
        pieces = [r for r in crossings if r["corridor"] == corridor]
        rows.append((corridor, len(axes), len(pieces), max(int(r["parallel_piece_count"]) for r in pieces)))
    cards = []
    for i, (corridor, axes, pieces, maximum) in enumerate(rows):
        y = 210 + i * 125
        cards.append(f'<g transform="translate(70 {y})"><rect width="1460" height="100" rx="18" fill="#fff" stroke="#82c4e6" stroke-width="3"/><text x="24" y="34" font-size="21" font-weight="800" fill="#071d36">{html.escape(corridor)}</text><text x="24" y="70" font-size="17" fill="#24425f">{axes} axes · {pieces} joint-crossing cable pieces · max {maximum} parallel flat cables</text><path d="M 760 52 H 1330" stroke="#f2b91d" stroke-width="14"/><circle cx="840" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><circle cx="1020" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><circle cx="1200" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><text x="1385" y="59" text-anchor="middle" font-size="16" font-weight="800" fill="#147348">CASCADE</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="title desc"><title id="title">HR-30 articulated power harness</title><desc id="desc">Six cascaded limb corridors with 25 tap boards and 45 flat-cable joint crossings.</desc><rect width="1600" height="1050" fill="#eef8ff"/><text x="70" y="70" font-size="46" font-weight="900" fill="#071d36">The harness bends at joints; the rigid guards do not.</text><text x="70" y="112" font-size="20" fill="#24425f">Each protected pair stays electrically independent while passive tap boards reduce the cable count toward the hand, foot, and head.</text><rect x="70" y="135" width="1460" height="56" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="96" y="171" font-size="18" font-weight="900" fill="#17243a">PRELIMINARY · 27.94 mm CATALOG-RADIUS NOMINAL GEOMETRY · FULL-POSE COLLISION, FLEX, DERATING AND PHYSICAL PROOF OPEN</text>{''.join(cards)}</svg>'''


def page_rejected_tap_board_predecessor(boards, crossings, guards, holds) -> str:
    chain_rows = "".join(f"<tr><td>{html.escape(c)}</td><td>{len(a)}</td><td>{sum(1 for r in crossings if r['corridor']==c)}</td><td>{max(int(r['parallel_piece_count']) for r in crossings if r['corridor']==c)}</td></tr>" for c, a in CHAINS.items())
    holds_html = "".join(f"<article class='hold'><h3>{h['hold_id']}</h3><p><strong>{html.escape(str(h['unresolved_item']))}</strong></p><p>{html.escape(str(h['evidence_required']))}</p></article>" for h in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 articulated power harness</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520;--green:#147348}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.pass{{border-color:var(--green)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#d9f2ff,#f7fbff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{min-height:430px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>HR-30 whole-body P0.1</p><h1>An articulated harness, not a rigid cable spine.</h1><p>The whole-limb rigid-guard idea is rejected. Twenty-five local tap boards preserve individual branch protection, while 45 four-conductor flat-cable pieces cross the joints inside separate flexible bellows envelopes. Rigid guards stop before every joint.</p></header><main><section class="grid"><article class="pass"><div class="metric">25</div><p>axis-specific tap boards and joint loops</p></article><article class="pass"><div class="metric">45</div><p>explicit four-conductor cable pieces</p></article><article class="pass"><div class="metric">50</div><p>rigid-link and flexible-joint guard solids</p></article><article class="hold"><div class="metric">0</div><p>full-pose or physical validations completed</p></article></section><section><h2>Inspect the complete humanoid</h2><model-viewer src="HR-30_whole_body_articulated_power_harness_candidate.glb" poster="articulated-power-harness-preview.png" alt="Interactive complete HR-30 humanoid with articulated flat-cable loops, tap boards and guard candidates at all 25 joints" camera-controls camera-orbit="28deg 78deg 112%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_articulated_power_harness_candidate.step">Editable harness STEP</a> · <a href="HR-30_articulated_power_harness_candidate.glb">Harness-only GLB</a> · <a href="joint-crossing-register.csv">45 cable records</a></p></section><section><h2>How the cascade works</h2><img src="articulated-power-harness.svg" alt="Six cascaded HR-30 power corridors with local tap boards and flexible joint crossings"><div class="panel"><p>Each Cicoil 969M101-22-4-MC candidate carries two separately protected two-wire circuits. At every joint, one circuit can terminate at the local actuator while the remaining circuits pass through the tap board into fewer downstream cables. No tap board is allowed to common VDD or return conductors. The published 27.94 mm continuous-flex radius is represented in nominal CAD, but full-range bend, twist, collision, pinch and life proof remain open.</p></div></section><section><h2>Whole-body allocation</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Axes</th><th>Cable pieces</th><th>Maximum parallel cables</th></tr></thead><tbody>{chain_rows}</tbody></table></div></section><section><h2>Why the former route is not the answer</h2><div class="panel hold"><p>The previous six centerlines are useful neutral-pose routing envelopes only. A single rigid guard cannot cross a moving shoulder, elbow, wrist, hip, knee, ankle, neck or waist axis. This candidate explicitly divides every route into rigid link-local protection and flexible joint-local protection.</p></div></section><section><h2>Open before fabrication</h2><div class="grid">{holds_html}</div></section><section><h2>Controlled artifacts</h2><div class="panel"><p><a href="cable-selection-register.csv">Cable candidate</a> · <a href="tap-board-register.csv">Tap boards</a> · <a href="joint-crossing-register.csv">Joint crossings</a> · <a href="guard-solid-register.csv">Guards</a> · <a href="primary-source-register.csv">Sources</a> · <a href="open-holds.csv">Holds</a> · <a href="status.json">Status</a></p><small>No artifact authorizes procurement, fabrication, connection, powered testing, motion or energization.</small></div></section></main><footer>{WARNING}</footer></body></html>'''


def svg(branches: list[dict[str, object]], crossings: list[dict[str, object]]) -> str:
    cards = []
    for i, (corridor, axes) in enumerate(CHAINS.items()):
        corridor_crossings = [r for r in crossings if r["corridor"] == corridor]
        maximum = max(int(r["parallel_pair_count"]) for r in corridor_crossings)
        y = 210 + i * 125
        cards.append(
            f'<g transform="translate(70 {y})"><rect width="1460" height="100" rx="18" fill="#fff" stroke="#82c4e6" stroke-width="3"/>'
            f'<text x="24" y="34" font-size="21" font-weight="800" fill="#071d36">{html.escape(corridor)}</text>'
            f'<text x="24" y="70" font-size="17" fill="#24425f">{len(axes)} direct branches · {len(corridor_crossings)} joint-crossing segments · max {maximum} parallel pairs</text>'
            '<path d="M 760 52 H 1330" stroke="#f2b91d" stroke-width="14"/>'
            '<circle cx="840" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/>'
            '<circle cx="1020" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/>'
            '<circle cx="1200" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/>'
            '<text x="1385" y="59" text-anchor="middle" font-size="16" font-weight="800" fill="#147348">NO SPLICES</text></g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="title desc"><title id="title">HR-30 articulated direct-branch power harness</title><desc id="desc">Six whole-body corridors with 25 direct protected branches and 76 explicit joint crossings.</desc><rect width="1600" height="1050" fill="#eef8ff"/><text x="70" y="70" font-size="46" font-weight="900" fill="#071d36">One protected pair per actuator. No intermediate tap boards.</text><text x="70" y="112" font-size="20" fill="#24425f">A distal branch crosses every upstream joint before reaching its one fixed transition; rigid guards stop before every axis.</text><rect x="70" y="135" width="1460" height="56" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="96" y="171" font-size="18" font-weight="900" fill="#17243a">PRELIMINARY · 37.5 mm NOMINAL CATALOG-RADIUS INPUT · FULL-POSE COLLISION, FLEX, DERATING AND PHYSICAL PROOF OPEN</text>{''.join(cards)}</svg>'''


def page(branches, transitions, crossings, guards, holds) -> str:
    chain_rows = "".join(
        f"<tr><td>{html.escape(corridor)}</td><td>{len(axes)}</td>"
        f"<td>{sum(1 for r in crossings if r['corridor'] == corridor)}</td>"
        f"<td>{max(int(r['parallel_pair_count']) for r in crossings if r['corridor'] == corridor)}</td></tr>"
        for corridor, axes in CHAINS.items()
    )
    holds_html = "".join(
        f"<article class='hold'><h3>{h['hold_id']}</h3><p><strong>{html.escape(str(h['unresolved_item']))}</strong></p>"
        f"<p>{html.escape(str(h['evidence_required']))}</p></article>" for h in holds
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 articulated direct-branch power harness</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520;--green:#147348}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.pass{{border-color:var(--green)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#d9f2ff,#f7fbff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{min-height:430px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>HR-30 whole-body P0.1</p><h1>Twenty-five protected branches, routed through every joint they actually cross.</h1><p>The tap-board cascade is rejected. Each actuator retains one unspliced two-conductor moving branch from its protected output to one fixed-side transition. Distal cables cross every upstream joint, producing 76 explicit crossing segments. Rigid guards stop before every axis.</p></header><main><section class="grid"><article class="pass"><div class="metric">25</div><p>direct individually protected actuator branches</p></article><article class="pass"><div class="metric">76</div><p>explicit upstream joint-crossing segments</p></article><article class="pass"><div class="metric">25</div><p>existing fixed Micro-Fit transition candidates</p></article><article class="pass"><div class="metric">50</div><p>rigid-link and flexible-joint guard solids</p></article><article class="hold"><div class="metric">0</div><p>full-pose or physical validations completed</p></article></section><section><h2>Inspect the complete humanoid</h2><model-viewer src="HR-30_whole_body_articulated_power_harness_candidate.glb" poster="articulated-power-harness-preview.png" alt="Interactive complete HR-30 humanoid with 25 direct actuator-power branches crossing all required upstream joints and separate rigid and flexible guard candidates" camera-controls camera-orbit="28deg 78deg 112%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_articulated_power_harness_candidate.step">Editable harness STEP</a> · <a href="HR-30_articulated_power_harness_candidate.glb">Harness-only GLB</a> · <a href="joint-crossing-register.csv">76 crossing records</a></p></section><section><h2>The selected P0.1 topology</h2><img src="articulated-power-harness.svg" alt="Six HR-30 corridors with 25 direct protected branches and 76 explicit joint crossings"><div class="panel"><p>Each igus CF130.03.02.UL candidate is one two-conductor VDD/return pair. It has no intermediate electrical splice between its protection channel and fixed-side transition. A cable feeding a distal ankle, hand or head axis crosses each upstream joint and is represented at every one of those joints. The manufacturer 5.0 mm maximum OD and 7.5xd radius input produce a 37.5 mm nominal CAD bend; actual bend plus torsion, collision, pinch, thermal and life proof remain open.</p></div></section><section><h2>Architecture correction</h2><div class="grid"><article class="pass"><h3>Direct branches retained</h3><p>The construction candidate remains consistent with the physical harness, protected branch PDU and cable-kit packages.</p></article><article class="hold"><h3>Tap-board cascade rejected</h3><p>The 25-board/45-piece Cicoil concept added intermediate terminations and contradicted the controlled direct-branch architecture. It receives no procurement or design credit.</p></article><article class="hold"><h3>Rigid whole-limb guard rejected</h3><p>No rigid guard may span a shoulder, elbow, wrist, hip, knee, ankle, neck or waist axis.</p></article></div><p><a href="architecture-disposition-register.csv">Open the controlled topology disposition</a>.</p></section><section><h2>Whole-body allocation</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Direct branches</th><th>Joint crossings</th><th>Maximum parallel pairs</th></tr></thead><tbody>{chain_rows}</tbody></table></div></section><section><h2>Open before fabrication</h2><div class="grid">{holds_html}</div></section><section><h2>Controlled artifacts</h2><div class="panel"><p><a href="cable-selection-register.csv">Cable candidate</a> · <a href="direct-branch-register.csv">25 branches</a> · <a href="joint-crossing-register.csv">76 crossings</a> · <a href="fixed-transition-register.csv">25 transitions</a> · <a href="guard-solid-register.csv">Guards</a> · <a href="primary-source-register.csv">Sources</a> · <a href="open-holds.csv">Holds</a> · <a href="status.json">Status</a></p><small>No artifact authorizes procurement, fabrication, connection, powered testing, motion or energization.</small></div></section></main><footer>{WARNING}</footer></body></html>'''


def replace_marker(path: Path, body: str) -> None:
    start = f"<!-- {MARKER}-START -->"
    end = f"<!-- {MARKER}-END -->"
    block = f"{start}\n{body.rstrip()}\n{end}"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before.rstrip() + "\n\n" + block + after
    elif path.suffix.lower() == ".html" and "</main>" in text:
        text = text.replace("</main>", block + "\n</main>", 1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def update_manifest(manifest_path: Path, base: Path, paths: list[Path], warning: str) -> None:
    # Drop records for artifacts removed by this package revision before
    # updating changed paths.  Without this, the recursive whole-body manifest
    # can retain a ghost entry such as the rejected tap-board register.
    rows = [row for row in read_csv(manifest_path) if (base / row["path"]).is_file()]
    mapping = {r["path"]: r for r in rows}
    order = [r["path"] for r in rows]
    for path in paths:
        rel = path.relative_to(base).as_posix()
        mapping[rel] = {"path": rel, "bytes": str(path.stat().st_size), "sha256": sha(path), "warning": warning}
        if rel not in order:
            order.append(rel)
    write_csv(manifest_path, [mapping[k] for k in order])


def manifest() -> None:
    rows = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", rows)


def integrate() -> None:
    body_readme = WHOLE / "README.md"
    body_index = WHOLE / "index.html"
    harness_readme = HARNESS / "README.md"
    harness_index = HARNESS / "index.html"
    replace_marker(harness_readme, """## Articulated power harness

The [articulated power-harness candidate](articulated-power-harness-p0.1/index.html) rejects both a rigid whole-limb cable guard and the conflicting intermediate tap-board cascade. The controlled construction candidate keeps 25 individually protected two-wire branches, represents all 76 upstream joint crossings, reuses the 25 fixed Micro-Fit transition candidates, and separates rigid-link from flexible-joint guard solids. Full-pose collision, bend/torsion life, termination, derating and physical validation remain open.""")
    replace_marker(harness_index, """<section id="articulated-power-harness"><h2>The power harness now follows the actual direct branches</h2><div class="grid"><article><h3>25 direct branches</h3><p>One protected VDD/return pair runs from its protection channel to one actuator transition without an intermediate splice.</p></article><article><h3>76 joint crossings</h3><p>Every distal branch is represented at every upstream joint it must physically cross.</p></article><article><h3>50 guard solids</h3><p>Rigid link-local channels stop before each axis; flexible dress-pack envelopes cover the nominal joint arcs.</p></article><article><h3>Tap boards rejected</h3><p>The conflicting 25-board/45-piece Cicoil cascade receives no selection or procurement credit.</p></article><article><h3>Validation remains open</h3><p>Full-range collision, pinch, torsion, flex life, derating, termination and physical proof are not complete.</p></article></div><p><a href="articulated-power-harness-p0.1/index.html">Open the interactive articulated harness guide.</a></p></section>""")
    replace_marker(body_readme, """## Articulated whole-body power harness

The [articulated power-harness CAD](harness/articulated-power-harness-p0.1/index.html) now follows the authoritative 25 individually protected branches instead of the rejected tap-board cascade. Distal cables appear at every upstream joint, giving 76 explicit joint-crossing segments plus 25 fixed transitions and separate rigid/flexible guards. It is a coherent packaging candidate; full-pose and physical validation remain open.""")
    # Keep the existing marker stable while replacing the predecessor topology.
    replace_marker(body_index, """<section id="articulated-power-harness"><h2>The cable protection now follows every direct branch</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>individually protected direct actuator branches</p></article><article class="card pass"><div class="metric">76</div><p>explicit upstream joint-crossing segments</p></article><article class="card pass"><div class="metric">25</div><p>fixed transition candidates</p></article><article class="card pass"><div class="metric">50</div><p>rigid-link and flexible-joint guard solids</p></article><article class="card hold"><div class="metric">0</div><p>full-pose collision or physical validations</p></article></div><div class="viewer"><model-viewer src="harness/articulated-power-harness-p0.1/HR-30_whole_body_articulated_power_harness_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 with 25 direct power branches, 76 joint crossings and guard candidates" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer><p><a href="harness/articulated-power-harness-p0.1/index.html">Open the articulated harness guide</a> · <a href="harness/articulated-power-harness-p0.1/HR-30_articulated_power_harness_candidate.step">editable STEP</a>.</p></div></section>""")

    package_files = sorted(p for p in OUT.iterdir() if p.is_file())
    harness_manifest = HARNESS / "file-manifest.csv"
    # The harness-root manifest intentionally covers only files at the harness
    # root.  Nested packages have their own manifest and are bound by the
    # whole-body recursive manifest.
    harness_rows = [r for r in read_csv(harness_manifest) if not r["path"].startswith(f"{OUT.name}/")]
    write_csv(harness_manifest, harness_rows)
    update_manifest(harness_manifest, HARNESS, [harness_readme, harness_index], HARNESS_WARNING)
    update_manifest(WHOLE / "file-manifest.csv", WHOLE, [body_readme, body_index, harness_readme, harness_index, harness_manifest, *package_files], WHOLE_WARNING)

    RELEASE_WHOLE.mkdir(parents=True, exist_ok=True)
    for source in [body_readme, body_index, WHOLE / "file-manifest.csv"]:
        shutil.copy2(source, RELEASE_WHOLE / source.name)
    release_harness = RELEASE_WHOLE / "harness"
    release_harness.mkdir(parents=True, exist_ok=True)
    for source in [harness_readme, harness_index, harness_manifest]:
        shutil.copy2(source, release_harness / source.name)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    branches, transitions, crossings, guards, geometry = architecture()
    holds = hold_rows()
    write_csv(OUT / "cable-selection-register.csv", cable_row())
    write_csv(OUT / "direct-branch-register.csv", branches)
    write_csv(OUT / "fixed-transition-register.csv", transitions)
    write_csv(OUT / "joint-crossing-register.csv", crossings)
    write_csv(OUT / "guard-solid-register.csv", guards)
    write_csv(OUT / "architecture-disposition-register.csv", disposition_rows())
    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "open-holds.csv", holds)
    export_cad(geometry)
    render_preview()
    (OUT / "articulated-power-harness.svg").write_text(svg(branches, crossings), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(branches, transitions, crossings, guards, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 articulated direct-branch power harness P0.1\n\n{WARNING}\n\nThis package preserves 25 individually protected unspliced actuator branches, expands them into all 76 physical upstream joint-crossing obligations, binds 25 existing fixed transitions, and provides separate rigid-link/flexible-joint guard candidates. The conflicting tap-board/Cicoil cascade is rejected. It releases no procurement, fabrication, connection, powered test, motion or energization.\n", encoding="utf-8", newline="\n")
    (OUT / "status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "whole_limb_rigid_guard_rejected": True,
        "tap_board_cascade_selected": False, "tap_board_count": 0,
        "direct_branch_architecture_selected": True,
        "axis_count": len(branches), "direct_branch_count": len(branches),
        "joint_crossing_segment_count": len(crossings), "fixed_transition_count": len(transitions),
        "guard_solid_record_count": len(guards),
        "nominal_cad_guard_solids_complete": True,
        "nominal_direct_crossing_solids_complete": True,
        "catalog_radius_represented_mm": round(CABLE_BEND_RADIUS_MM, 3),
        "application_ampacity_released": False,
        "full_pose_collision_complete": False, "full_range_flex_complete": False,
        "termination_complete": False, "thermal_derating_complete": False,
        "physical_validation_complete": False, "procurement_authority": False,
        "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False,
        "energization_authority": False,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "articulated-power-harness-source.py")
    manifest()
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    integrate()


if __name__ == "__main__":
    main()
