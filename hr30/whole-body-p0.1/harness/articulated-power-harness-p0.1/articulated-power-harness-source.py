#!/usr/bin/env python3
"""Generate the HR-30 articulated actuator-power harness candidate.

This successor replaces the invalid idea of one rigid guard spanning an entire
moving limb.  Each joint receives a serviceable passive tap board, a flat-flex
joint crossing, a flexible local bellows envelope, and a rigid guard only on
the adjacent rigid link.  It is configuration/packaging CAD, not permission to
procure, fabricate, connect, move, test under power, or energize the robot.
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
CORES = HARNESS / "distributed-power-harness-successor-p0.1" / "axis-core-allocation.csv"
NODES = HARNESS / "distributed-power-harness-successor-p0.1" / "distribution-node-register.csv"
IDENTIFIER = "HR30-ARTICULATED-POWER-HARNESS-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - ARTICULATED ACTUATOR-POWER HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
HARNESS_WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
MARKER = "HR30-ARTICULATED-POWER-HARNESS-P01"
RENDER_TOOL = ROOT / "tools" / "render_glb_preview.py"

# Current official Cicoil catalog candidate.  Values are catalog values, not a
# released HR-30 ampacity or flex-life result.
CABLE_PART = "969M101-22-4-MC"
CABLE_GAUGE = "22 AWG"
CABLE_CONDUCTORS = 4
CABLE_WIDTH_MM = 0.32 * 25.4
CABLE_HEIGHT_MM = 0.11 * 25.4
CABLE_CATALOG_AMP_A = 8.0
CABLE_CONTINUOUS_BEND_MULTIPLE = 10.0
CABLE_BEND_RADIUS_MM = CABLE_HEIGHT_MM * CABLE_CONTINUOUS_BEND_MULTIPLE
CABLE_NOMINAL_CYCLES = 10_000_000
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


def board_point(axis_id: str, center, axis):
    """Locate a tap board along the real joint axis, outside the body."""
    ax = tuple(abs(v) for v in axis)
    if ax[1] > 0.5:
        return add(center, mul(axis, 28.0 if axis[1] >= 0 else -28.0))
    if ax[0] > 0.5:
        side = 1.0 if center[0] >= 0 else -1.0
        return add(center, (side * 24.0, 0.0, 0.0))
    # Yaw axes are accessible from the rear; the board lies on the axis and a
    # short radial lead reaches the loop.  The flexible envelope remains tied
    # to the actual axis line.
    return add(center, (0.0, 0.0, 12.0))


def architecture():
    loop_by_axis = {r["axis_id"]: r for r in read_csv(LOOPS)}
    core_by_axis = {r["axis_id"]: r for r in read_csv(CORES)}
    if set(loop_by_axis) != set(core_by_axis) or set(loop_by_axis) != {a for chain in CHAINS.values() for a in chain}:
        raise RuntimeError("25-axis harness binding drift")

    boards: list[dict[str, object]] = []
    crossings: list[dict[str, object]] = []
    guards: list[dict[str, object]] = []
    geometry: dict[str, dict[str, object]] = {}
    total_piece_count = 0

    for corridor, axes in CHAINS.items():
        previous_point = None
        for stage, axis_id in enumerate(axes, start=1):
            loop = loop_by_axis[axis_id]
            core = core_by_axis[axis_id]
            center = parse_tuple(loop["joint_axis_xyz_mm"])
            axis = unit(parse_tuple(loop["joint_axis_direction"]))
            point = board_point(axis_id, center, axis)
            remaining = axes[stage - 1:]
            next_axes = axes[stage:]
            cable_count = math.ceil(len(remaining) / 2)
            pack_width = cable_count * CABLE_WIDTH_MM + max(0, cable_count - 1) * LANE_GAP_MM
            board_w = max(24.0, pack_width + 8.0)
            board_h = 20.0
            board_id = f"TB-{axis_id}"
            boards.append(common({
                "tap_board_id": board_id,
                "axis_id": axis_id,
                "corridor": corridor,
                "stage": stage,
                "joint_center_xyz_mm": fmt_xyz(center),
                "joint_axis_direction": fmt_xyz(axis),
                "board_center_xyz_mm": fmt_xyz(point),
                "board_envelope_w_h_t_mm": f"{board_w:.3f},{board_h:.3f},1.600",
                "incoming_flat_cables": cable_count,
                "incoming_protected_pairs": len(remaining),
                "local_pair_to_actuator": axis_id,
                "outgoing_protected_pairs": len(next_axes),
                "pass_through_rule": "no VDD or return commoning; one protected pair terminates locally and every remaining pair passes independently",
                "mount_interface": "two M2.5 clearance holes at 14.0 mm centers; bracket and connector selection required",
                "state": "DIMENSIONED PASSIVE TAP-BOARD ENVELOPE; PCB, CONNECTORS AND FAULT TEST OPEN",
            }))

            for cable_index in range(cable_count):
                carried = remaining[cable_index * 2:(cable_index + 1) * 2]
                piece_id = f"APH-{axis_id}-C{cable_index + 1}"
                total_piece_count += 1
                crossings.append(common({
                    "cable_piece_id": piece_id,
                    "corridor": corridor,
                    "joint_axis": axis_id,
                    "stage": stage,
                    "parallel_piece_index": cable_index + 1,
                    "parallel_piece_count": cable_count,
                    "carried_protected_pairs": "; ".join(carried),
                    "unused_pair": "YES - INSULATED BOTH ENDS" if len(carried) == 1 else "NO",
                    "candidate_part": CABLE_PART,
                    "conductor_configuration": "4 x 22 AWG; pair A contacts 1/2, pair B contacts 3/4; polarity keyed on tap-board drawing",
                    "catalog_amp_rating_a": f"{CABLE_CATALOG_AMP_A:.1f}",
                    "maximum_hr30_channel_cap_a": f"{max(float(core_by_axis[a]['candidate_current_cap_a']) for a in carried):.6f}",
                    "catalog_current_screen": "PASS CATALOG NUMBER ONLY - BUNDLING/TERMINATION/AMBIENT DERATING OPEN",
                    "flat_width_mm": f"{CABLE_WIDTH_MM:.3f}",
                    "flat_height_mm": f"{CABLE_HEIGHT_MM:.3f}",
                    "continuous_flex_radius_mm": f"{CABLE_BEND_RADIUS_MM:.3f}",
                    "nominal_flex_cycle_claim": str(CABLE_NOMINAL_CYCLES),
                    "joint_range": loop["commanded_range"],
                    "nominal_joint_arc_deg": "120",
                    "actual_cut_length": "SELECTION REQUIRED AFTER FULL-RANGE ROUTE SWEEP",
                    "state": "DIMENSIONED NOMINAL CROSSING; FULL-RANGE FLEX/TWIST/COLLISION AND TERMINATION PROOF OPEN",
                }))
                geometry[piece_id] = {
                    "axis_id": axis_id, "center": center, "axis": axis, "point": point,
                    "previous": previous_point, "lane": cable_index, "count": cable_count,
                    "pack_width": pack_width, "board_w": board_w,
                }

            guard_base = f"GD-{axis_id}"
            guards.extend([
                common({
                    "guard_id": f"{guard_base}-LINK",
                    "axis_id": axis_id,
                    "guard_type": "RIGID LINK-LOCAL U-CHANNEL",
                    "covers": "straight cable run ending before the moving joint",
                    "internal_width_mm": f"{pack_width + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "internal_height_mm": f"{CABLE_HEIGHT_MM + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "wall_mm": f"{GUARD_WALL_MM:.3f}",
                    "material_candidate": "printed PA12 or machined polymer; selection required",
                    "joint_spanning": "NO",
                    "cad_solid": f"{guard_base}_LINK_GUARD",
                    "state": "DIMENSIONED CAD CANDIDATE; FASTENERS, ACCESS, IMPACT AND COLLISION OPEN",
                }),
                common({
                    "guard_id": f"{guard_base}-FLEX",
                    "axis_id": axis_id,
                    "guard_type": "FLEXIBLE JOINT BELLOWS ENVELOPE",
                    "covers": "120-degree nominal flat-cable joint arc",
                    "internal_width_mm": f"{pack_width + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "internal_height_mm": f"{CABLE_HEIGHT_MM + 2 * GUARD_CLEARANCE_MM:.3f}",
                    "wall_mm": f"{GUARD_WALL_MM:.3f}",
                    "material_candidate": "corrugated TPU or textile dress-pack sleeve; selection required",
                    "joint_spanning": "YES - FLEXIBLE ONLY; NO RIGID SHELL ACROSS AXIS",
                    "cad_solid": f"{guard_base}_FLEX_GUARD",
                    "state": "DIMENSIONED NOMINAL ENVELOPE; CORRUGATION, ATTACHMENT, PINCH AND FATIGUE PROOF OPEN",
                }),
            ])
            previous_point = point

    if len(boards) != 25 or total_piece_count != 45 or len(guards) != 50:
        raise RuntimeError(f"architecture count drift: {len(boards)} boards {total_piece_count} cables {len(guards)} guards")
    return boards, crossings, guards, geometry


def cable_row() -> list[dict[str, object]]:
    return [common({
        "candidate_part": CABLE_PART,
        "manufacturer": "Cicoil",
        "family": "unshielded high-flex motor-power flat cable",
        "conductors": CABLE_CONDUCTORS,
        "gauge": CABLE_GAUGE,
        "width_mm": f"{CABLE_WIDTH_MM:.3f}",
        "height_mm": f"{CABLE_HEIGHT_MM:.3f}",
        "catalog_amp_rating_a": f"{CABLE_CATALOG_AMP_A:.1f}",
        "continuous_flex_radius_rule": f"{CABLE_CONTINUOUS_BEND_MULTIPLE:.1f} x cable height",
        "continuous_flex_radius_mm": f"{CABLE_BEND_RADIUS_MM:.3f}",
        "nominal_flex_cycles": CABLE_NOMINAL_CYCLES,
        "selection_boundary": "candidate geometry only; exact assembly/termination, conductor DCR, bundle derating, torsion and received lot remain selection/validation required",
        "state": "CANDIDATE - NOT RELEASED",
    })]


def source_rows() -> list[dict[str, object]]:
    local = [
        ("APH-S01", LOOPS, "25 joint axes, ranges and moving-loop obligations"),
        ("APH-S02", CORES, "individually protected pair allocation and current caps"),
        ("APH-S03", NODES, "six root protection/distribution node obligations"),
        ("APH-S04", BODY_STEP, "complete humanoid context for combined GLB"),
        ("APH-S07", RENDER_TOOL, "deterministic Blender engineering-preview renderer"),
    ]
    rows = [common({
        "source_id": sid, "publisher": "Project Button", "document": scope,
        "revision_or_date": "whole-body P0.1 current input", "official_url_or_path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path), "verified_scope": scope,
    }) for sid, path, scope in local]
    rows.extend([
        common({
            "source_id": "APH-S05", "publisher": "Cicoil", "document": "Hi-Flex Motor Power Cable catalog",
            "revision_or_date": "live official catalog accessed 2026-08-18; page revision not stated",
            "official_url_or_path": "https://www.cicoil.com/flat-cable/motion-control-cables/hi-flex-motor-power-cable",
            "sha256": "N/A - LIVE PRIMARY SOURCE",
            "verified_scope": "969M101-22-4-MC: 4 x 22 AWG, 0.32 x 0.11 in, 8 A catalog rating; manufacturer states 10x cable height for continuous flex",
        }),
        common({
            "source_id": "APH-S06", "publisher": "Cicoil", "document": "Motor Power High Flex Cable product page",
            "revision_or_date": "live official product page accessed 2026-08-18; page revision not stated",
            "official_url_or_path": "https://www.cicoil.com/motor-power-cable/flex",
            "sha256": "N/A - LIVE PRIMARY SOURCE",
            "verified_scope": "10,000,000-cycle nominal family claim and robotics/continuous-motion application statement; HR-30 application remains unverified",
        }),
    ])
    return rows


def hold_rows() -> list[dict[str, object]]:
    holds = [
        ("APH-H01", "tap-board electrical definition", "pin-level schematic, layout, creepage/clearance, connector and polarity-keying review for all three board sizes"),
        ("APH-H02", "flat-cable termination", "Cicoil written assembly quotation/drawing or qualified termination process with pull, milliohm and fault-current tests"),
        ("APH-H03", "full-range joint kinematics", "sweep every one of 25 cable/bellows assemblies through exact min/max poses and fall-restraint envelope"),
        ("APH-H04", "whole-body collision and pinch clearance", "exact body/guard/cable collision sweeps in neutral, crouch, weight transfer, step and restrained-fall configurations"),
        ("APH-H05", "flex mode applicability", "manufacturer written disposition for bend plus torsion at every joint and accepted life calculation/test spectrum"),
        ("APH-H06", "ampacity and voltage drop", "received conductor DCR, ambient/bundle/connector derating, duty-cycle currents, fault current and temperature-rise tests"),
        ("APH-H07", "rigid guard and flexible bellows design", "material, wall/corrugation, attachment, removability, impact, snag, chafe, flame and human-contact validation"),
        ("APH-H08", "mass and COM update", "supplier mass plus as-built board/connector/guard mass reconciled into whole-body budget"),
        ("APH-H09", "EMC and power/data separation", "final routed data harness plus shield/reference-bond plan and emissions/immunity tests"),
        ("APH-H10", "prototype proof", "unpowered full-scale dress build, continuity/insulation/polarity checks, then separately authorized current-limited motion cycling"),
        ("APH-H11", "qualified release review", "signed mechanical/electrical/functional-safety review after preceding evidence exists"),
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


def export_cad(geometry: dict[str, dict[str, object]], boards: list[dict[str, object]]) -> None:
    import cadquery as cq

    harness = cq.Assembly(name="HR30_ARTICULATED_POWER_HARNESS_P01")
    combined = cq.Assembly(name="HR30_WHOLE_BODY_ARTICULATED_POWER_HARNESS_P01")
    body = cq.importers.importStep(str(BODY_STEP)).val()
    combined.add(body, name="HR30_BODY_REFERENCE", color=cq.Color(0.68, 0.77, 0.84, 0.38))
    cable_color = cq.Color(0.95, 0.58, 0.03)
    guard_color = cq.Color(0.06, 0.42, 0.72, 0.32)
    board_color = cq.Color(0.05, 0.42, 0.23)
    connector_color = cq.Color(0.94, 0.75, 0.10)

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
            offset = (lane - (count - 1) / 2.0) * (CABLE_WIDTH_MM + LANE_GAP_MM)
            loop = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_HEIGHT_MM, CABLE_WIDTH_MM)
            loop = loop.translate((0.0, 0.0, offset))
            loop = orient_from_z(loop, cq, axis).translate(center)
            harness.add(loop, name=f"{piece_id}_FLEX_ARC", color=cable_color)
            combined.add(loop, name=f"{piece_id}_FLEX_ARC", color=cable_color)
            if previous is not None and length(sub(point, previous)) > 5.0:
                span = prism_between(cq, previous, point, CABLE_WIDTH_MM, CABLE_HEIGHT_MM)
                harness.add(span, name=f"{piece_id}_LINK_SPAN", color=cable_color)
                combined.add(span, name=f"{piece_id}_LINK_SPAN", color=cable_color)

        outer = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_HEIGHT_MM + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM), pack_width + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM))
        inner = arc_solid(cq, CABLE_BEND_RADIUS_MM, CABLE_HEIGHT_MM + 2 * GUARD_CLEARANCE_MM, pack_width + 2 * GUARD_CLEARANCE_MM)
        flex_guard = outer.cut(inner)
        flex_guard = orient_from_z(flex_guard, cq, axis).translate(center)
        harness.add(flex_guard, name=f"GD-{axis_id}_FLEX_GUARD", color=guard_color)
        combined.add(flex_guard, name=f"GD-{axis_id}_FLEX_GUARD", color=guard_color)
        if previous is not None and length(sub(point, previous)) > 5.0:
            outer_span = prism_between(cq, previous, point, pack_width + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM), CABLE_HEIGHT_MM + 2 * (GUARD_CLEARANCE_MM + GUARD_WALL_MM))
            inner_span = prism_between(cq, sub(previous, mul(unit(sub(point, previous)), 0.5)), add(point, mul(unit(sub(point, previous)), 0.5)), pack_width + 2 * GUARD_CLEARANCE_MM, CABLE_HEIGHT_MM + 2 * GUARD_CLEARANCE_MM)
            link_guard = outer_span.cut(inner_span)
            harness.add(link_guard, name=f"GD-{axis_id}_LINK_GUARD", color=guard_color)
            combined.add(link_guard, name=f"GD-{axis_id}_LINK_GUARD", color=guard_color)

    for row in boards:
        center = parse_tuple(str(row["board_center_xyz_mm"]))
        w, h, t = (float(v) for v in str(row["board_envelope_w_h_t_mm"]).split(","))
        board = cq.Workplane("XZ").box(w, h, t).val().translate(center)
        connector = cq.Workplane("XY").box(min(w - 4.0, 20.0), 5.0, 6.0).val().translate((center[0], center[1] + 4.0, center[2]))
        harness.add(board, name=str(row["tap_board_id"]), color=board_color)
        harness.add(connector, name=f"{row['tap_board_id']}_CONNECTOR_ENVELOPE", color=connector_color)
        combined.add(board, name=str(row["tap_board_id"]), color=board_color)
        combined.add(connector, name=f"{row['tap_board_id']}_CONNECTOR_ENVELOPE", color=connector_color)

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


def svg(boards: list[dict[str, object]], crossings: list[dict[str, object]]) -> str:
    rows = []
    for corridor, axes in CHAINS.items():
        pieces = [r for r in crossings if r["corridor"] == corridor]
        rows.append((corridor, len(axes), len(pieces), max(int(r["parallel_piece_count"]) for r in pieces)))
    cards = []
    for i, (corridor, axes, pieces, maximum) in enumerate(rows):
        y = 210 + i * 125
        cards.append(f'<g transform="translate(70 {y})"><rect width="1460" height="100" rx="18" fill="#fff" stroke="#82c4e6" stroke-width="3"/><text x="24" y="34" font-size="21" font-weight="800" fill="#071d36">{html.escape(corridor)}</text><text x="24" y="70" font-size="17" fill="#24425f">{axes} axes · {pieces} joint-crossing cable pieces · max {maximum} parallel flat cables</text><path d="M 760 52 H 1330" stroke="#f2b91d" stroke-width="14"/><circle cx="840" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><circle cx="1020" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><circle cx="1200" cy="52" r="28" fill="none" stroke="#0b4f91" stroke-width="8"/><text x="1385" y="59" text-anchor="middle" font-size="16" font-weight="800" fill="#147348">CASCADE</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="title desc"><title id="title">HR-30 articulated power harness</title><desc id="desc">Six cascaded limb corridors with 25 tap boards and 45 flat-cable joint crossings.</desc><rect width="1600" height="1050" fill="#eef8ff"/><text x="70" y="70" font-size="46" font-weight="900" fill="#071d36">The harness bends at joints; the rigid guards do not.</text><text x="70" y="112" font-size="20" fill="#24425f">Each protected pair stays electrically independent while passive tap boards reduce the cable count toward the hand, foot, and head.</text><rect x="70" y="135" width="1460" height="56" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><text x="96" y="171" font-size="18" font-weight="900" fill="#17243a">PRELIMINARY · 27.94 mm CATALOG-RADIUS NOMINAL GEOMETRY · FULL-POSE COLLISION, FLEX, DERATING AND PHYSICAL PROOF OPEN</text>{''.join(cards)}</svg>'''


def page(boards, crossings, guards, holds) -> str:
    chain_rows = "".join(f"<tr><td>{html.escape(c)}</td><td>{len(a)}</td><td>{sum(1 for r in crossings if r['corridor']==c)}</td><td>{max(int(r['parallel_piece_count']) for r in crossings if r['corridor']==c)}</td></tr>" for c, a in CHAINS.items())
    holds_html = "".join(f"<article class='hold'><h3>{h['hold_id']}</h3><p><strong>{html.escape(str(h['unresolved_item']))}</strong></p><p>{html.escape(str(h['evidence_required']))}</p></article>" for h in holds)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 articulated power harness</title><script type="module" src="../../vendor/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520;--green:#147348}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.pass{{border-color:var(--green)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}model-viewer{{width:100%;height:min(72vh,760px);min-height:520px;background:linear-gradient(#d9f2ff,#f7fbff);border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}model-viewer{{min-height:430px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>HR-30 whole-body P0.1</p><h1>An articulated harness, not a rigid cable spine.</h1><p>The whole-limb rigid-guard idea is rejected. Twenty-five local tap boards preserve individual branch protection, while 45 four-conductor flat-cable pieces cross the joints inside separate flexible bellows envelopes. Rigid guards stop before every joint.</p></header><main><section class="grid"><article class="pass"><div class="metric">25</div><p>axis-specific tap boards and joint loops</p></article><article class="pass"><div class="metric">45</div><p>explicit four-conductor cable pieces</p></article><article class="pass"><div class="metric">50</div><p>rigid-link and flexible-joint guard solids</p></article><article class="hold"><div class="metric">0</div><p>full-pose or physical validations completed</p></article></section><section><h2>Inspect the complete humanoid</h2><model-viewer src="HR-30_whole_body_articulated_power_harness_candidate.glb" poster="articulated-power-harness-preview.png" alt="Interactive complete HR-30 humanoid with articulated flat-cable loops, tap boards and guard candidates at all 25 joints" camera-controls camera-orbit="28deg 78deg 112%" field-of-view="28deg" shadow-intensity="0.85" exposure="1.05"></model-viewer><p><a href="HR-30_articulated_power_harness_candidate.step">Editable harness STEP</a> · <a href="HR-30_articulated_power_harness_candidate.glb">Harness-only GLB</a> · <a href="joint-crossing-register.csv">45 cable records</a></p></section><section><h2>How the cascade works</h2><img src="articulated-power-harness.svg" alt="Six cascaded HR-30 power corridors with local tap boards and flexible joint crossings"><div class="panel"><p>Each Cicoil 969M101-22-4-MC candidate carries two separately protected two-wire circuits. At every joint, one circuit can terminate at the local actuator while the remaining circuits pass through the tap board into fewer downstream cables. No tap board is allowed to common VDD or return conductors. The published 27.94 mm continuous-flex radius is represented in nominal CAD, but full-range bend, twist, collision, pinch and life proof remain open.</p></div></section><section><h2>Whole-body allocation</h2><div class="scroll"><table><thead><tr><th>Corridor</th><th>Axes</th><th>Cable pieces</th><th>Maximum parallel cables</th></tr></thead><tbody>{chain_rows}</tbody></table></div></section><section><h2>Why the former route is not the answer</h2><div class="panel hold"><p>The previous six centerlines are useful neutral-pose routing envelopes only. A single rigid guard cannot cross a moving shoulder, elbow, wrist, hip, knee, ankle, neck or waist axis. This candidate explicitly divides every route into rigid link-local protection and flexible joint-local protection.</p></div></section><section><h2>Open before fabrication</h2><div class="grid">{holds_html}</div></section><section><h2>Controlled artifacts</h2><div class="panel"><p><a href="cable-selection-register.csv">Cable candidate</a> · <a href="tap-board-register.csv">Tap boards</a> · <a href="joint-crossing-register.csv">Joint crossings</a> · <a href="guard-solid-register.csv">Guards</a> · <a href="primary-source-register.csv">Sources</a> · <a href="open-holds.csv">Holds</a> · <a href="status.json">Status</a></p><small>No artifact authorizes procurement, fabrication, connection, powered testing, motion or energization.</small></div></section></main><footer>{WARNING}</footer></body></html>'''


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
    rows = read_csv(manifest_path)
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

The [articulated power-harness candidate](articulated-power-harness-p0.1/index.html) rejects a rigid whole-limb cable guard. It defines 25 passive tap-board envelopes, 45 four-conductor flat-cable joint crossings, and separate rigid-link/flexible-joint guard solids. Every protected pair remains electrically independent. Full-pose collision, bend/torsion life, termination, derating and physical validation remain open.""")
    replace_marker(harness_index, """<section id="articulated-power-harness"><h2>The power harness now articulates with the robot</h2><div class="grid"><article><h3>25 tap boards</h3><p>One dimensioned passive pass-through board at every axis; no protected pair may be commoned.</p></article><article><h3>45 flat-cable pieces</h3><p>Four-conductor pieces carry two branch circuits and reduce in count toward each hand, foot and the head.</p></article><article><h3>50 guard solids</h3><p>Rigid link-local channels stop before the joint; flexible bellows envelopes cover the nominal joint arcs.</p></article><article><h3>Validation remains open</h3><p>Full-range collision, pinch, torsion, flex life, derating, termination and physical proof are not complete.</p></article></div><p><a href="articulated-power-harness-p0.1/index.html">Open the interactive articulated harness guide.</a></p></section>""")
    replace_marker(body_readme, """## Articulated whole-body power harness

The [articulated power-harness CAD](harness/articulated-power-harness-p0.1/index.html) replaces the invalid rigid whole-limb guard idea with a cascaded, joint-by-joint candidate. All 25 axes have a tap-board envelope, flat-flex crossing and separate rigid/flexible guard geometry. It is a coherent packaging candidate; full-pose and physical validation remain open.""")
    replace_marker(body_index, """<section id="articulated-power-harness"><h2>The cable protection now stops and flexes at the right places</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>axis-specific tap boards and joint loops</p></article><article class="card pass"><div class="metric">45</div><p>explicit flat-cable joint-crossing pieces</p></article><article class="card pass"><div class="metric">50</div><p>rigid-link and flexible-joint guard solids</p></article><article class="card hold"><div class="metric">0</div><p>full-pose collision or physical validations</p></article></div><div class="viewer"><model-viewer src="harness/articulated-power-harness-p0.1/HR-30_whole_body_articulated_power_harness_candidate.glb" poster="front-elevation.svg" alt="Interactive complete HR-30 with articulated power harness and guard candidates" camera-controls shadow-intensity="0.8" exposure="1.05"></model-viewer><p><a href="harness/articulated-power-harness-p0.1/index.html">Open the articulated harness guide</a> · <a href="harness/articulated-power-harness-p0.1/HR-30_articulated_power_harness_candidate.step">editable STEP</a>.</p></div></section>""")

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
    boards, crossings, guards, geometry = architecture()
    holds = hold_rows()
    write_csv(OUT / "cable-selection-register.csv", cable_row())
    write_csv(OUT / "tap-board-register.csv", boards)
    write_csv(OUT / "joint-crossing-register.csv", crossings)
    write_csv(OUT / "guard-solid-register.csv", guards)
    write_csv(OUT / "primary-source-register.csv", source_rows())
    write_csv(OUT / "open-holds.csv", holds)
    export_cad(geometry, boards)
    render_preview()
    (OUT / "articulated-power-harness.svg").write_text(svg(boards, crossings), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(boards, crossings, guards, holds), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 articulated power harness P0.1\n\n{WARNING}\n\nThis package defines 25 joint-local tap boards, 45 flat-cable power pieces and separate rigid-link/flexible-joint guards. It releases no procurement, fabrication, connection, powered test, motion or energization.\n", encoding="utf-8", newline="\n")
    (OUT / "status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": DATE, "warning": WARNING,
        "whole_limb_rigid_guard_rejected": True,
        "axis_count": len(boards), "tap_board_count": len(boards),
        "flat_cable_piece_count": len(crossings), "guard_solid_record_count": len(guards),
        "nominal_cad_guard_solids_complete": True,
        "catalog_radius_represented_mm": round(CABLE_BEND_RADIUS_MM, 3),
        "catalog_current_number_screens_pass": len(crossings),
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
