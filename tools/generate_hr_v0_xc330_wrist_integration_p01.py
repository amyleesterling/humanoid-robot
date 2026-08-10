#!/usr/bin/env python3
"""Generate the HR-V0 XC330-to-H104 wrist integration P0.1 candidate.

This source binds the nonselected XC330 gripper P0.2 to the controlled P0.7
arm/H104 reference geometry.  It does not select the branch or authorize any
procurement, fabrication, assembly, connection, motion, or energization.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_xc330_gripper_interface_p02 as grip


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/xc330-wrist-integration-p0.1"
GUIDE = ROOT / "release/hr-v0/xc330-wrist-integration-p0.1"
GENERATED_ROOT = ROOT / "cad/hr-v0/generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
IDENTIFIER = "HR-V0-XC330-WRIST-P0.1"
REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
WARNING = (
    "PRELIMINARY WRIST-INTEGRATION CANDIDATE - NOT SELECTED - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)

# Gripper P0.2 to H104 local transform.  Rx(+90) maps the gripper's +Z tool
# direction to H104 -Y, which becomes world +Y under the controlled H104 Rx180.
GRIPPER_RX_H104_DEG = 90.0
GRIPPER_T_H104_MM = (0.0, 4.0, 13.5)
OBJECT_CENTER_GRIPPER_MM = (0.0, 0.0, 31.0)

# Project-owned bridge candidate.  H104 inside width is 38 mm from the source
# drawing and 1.5 mm side thickness; the P0.2 U-base ears terminate at x=+/-16.
BRIDGE_INNER_X_MM = 16.0
BRIDGE_OUTER_X_MM = 19.0
BRIDGE_Y_MIN_MM = 4.5
BRIDGE_Y_MAX_MM = 24.5
BRIDGE_Z_MIN_MM = -10.0
BRIDGE_Z_MAX_MM = 21.5
BRIDGE_HOLE_D_MM = 2.2
BRIDGE_DENSITY_G_CM3 = 2.70  # 6061-family screening assumption; not selected
H104_M2_TAP_AXES_YZ = ((22.5, -8.0), (22.5, 8.0))

COLLISION_INCREMENT_DEG = 5.0
J1_LIMITS_DEG = (-20.0, 70.0)
J2_LIMITS_DEG = (15.0, 115.0)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generated_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_generated_source_manifest() -> None:
    rows = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            rows.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_sha256(path),
                "revision": REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, rows)


def shape_value(value: cq.Shape | cq.Workplane) -> cq.Shape:
    return value.val() if isinstance(value, cq.Workplane) else value


def to_h104(value: cq.Shape | cq.Workplane) -> cq.Shape:
    shape = shape_value(value)
    return arm.rotate_x(shape, GRIPPER_RX_H104_DEG).translate(GRIPPER_T_H104_MM)


def h104_to_world(value: cq.Shape | cq.Workplane) -> cq.Shape:
    shape = shape_value(value)
    return arm.rotate_x(shape, 180.0).translate((0.0, arm.G1_Y, 0.0))


def gripper_to_world(value: cq.Shape | cq.Workplane) -> cq.Shape:
    return h104_to_world(to_h104(value))


def transformed_point_h104(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    tx, ty, tz = GRIPPER_T_H104_MM
    return (x + tx, -z + ty, y + tz)


def transformed_point_world(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = transformed_point_h104(point)
    return (x, -y + arm.G1_Y, -z)


def bridge(sign: int) -> cq.Shape:
    if sign not in (-1, 1):
        raise ValueError(sign)
    x0 = BRIDGE_INNER_X_MM if sign > 0 else -BRIDGE_OUTER_X_MM
    part = cq.Solid.makeBox(
        BRIDGE_OUTER_X_MM - BRIDGE_INNER_X_MM,
        BRIDGE_Y_MAX_MM - BRIDGE_Y_MIN_MM,
        BRIDGE_Z_MAX_MM - BRIDGE_Z_MIN_MM,
        cq.Vector(x0, BRIDGE_Y_MIN_MM, BRIDGE_Z_MIN_MM),
    )
    pcd_offset = 8.0 / math.sqrt(2.0)
    pcd_axes = [
        transformed_point_h104((0.0, y, z))[1:]
        for y in (-pcd_offset, pcd_offset)
        for z in (-8.0 - pcd_offset, -8.0 + pcd_offset)
    ]
    for y, z in [*H104_M2_TAP_AXES_YZ, *pcd_axes]:
        hole = cq.Solid.makeCylinder(
            BRIDGE_HOLE_D_MM / 2.0,
            5.0,
            cq.Vector(-2.5 if sign < 0 else 15.0, y, z),
            cq.Vector(1, 0, 0),
        )
        if sign < 0:
            hole = cq.Solid.makeCylinder(
                BRIDGE_HOLE_D_MM / 2.0,
                5.0,
                cq.Vector(-20.0, y, z),
                cq.Vector(1, 0, 0),
            )
        part = part.cut(hole)
    return part


def gripper_components(opening_mm: float) -> dict[str, cq.Shape]:
    actuator = cq.importers.importStep(str(grip.XC_STEP))
    frame = cq.importers.importStep(str(grip.FRAME_STEP)).val()
    frame_plus = grip.positive_frame(frame)
    frame_minus = grip.negative_frame(frame)
    base = grip.gripper_base()
    lid = grip.cover()
    gear = grip.involute_pinion()
    left = grip.top_rack_jaw()
    right = left.rotate((0, 0, 0), (0, 0, 1), 180)
    pad_left = grip.left_pad()
    pad_right = pad_left.rotate((0, 0, 0), (0, 0, 1), 180)
    displacement = (opening_mm - grip.HARD_OPENING_MIN) / 2.0
    angle_deg = math.degrees(displacement / grip.PITCH_RADIUS)
    return {
        "XC330_OFFICIAL": actuator.val(),
        "FPX330_S101_PLUS_OFFICIAL": frame_plus,
        "FPX330_S101_MINUS_OFFICIAL": frame_minus,
        "CUSTOM_U_BASE_P02": base.val(),
        "CUSTOM_COVER_P02": lid.val(),
        "CUSTOM_INVOLUTE_PINION_P02": gear.rotate((0, 0, 0), (0, 0, 1), angle_deg).val(),
        "CUSTOM_LEFT_RACK_JAW_P02": left.translate((-opening_mm / 2.0, 0, 0)).val(),
        "CUSTOM_RIGHT_RACK_JAW_P02": right.translate((opening_mm / 2.0, 0, 0)).val(),
        "LEFT_PAD_ENVELOPE_P02": pad_left.translate((-opening_mm / 2.0, 0, 0)).val(),
        "RIGHT_PAD_ENVELOPE_P02": pad_right.translate((opening_mm / 2.0, 0, 0)).val(),
    }


def export_part(stem: str, part: cq.Shape) -> None:
    step = OUT / f"{stem}.step"
    stl = OUT / f"{stem}.stl"
    cq.exporters.export(part, str(step))
    grip.normalize_step(step)
    cq.exporters.export(part, str(stl), tolerance=0.02, angularTolerance=0.1)


def build_arm_reference_components() -> dict[str, cq.Shape]:
    xm540 = arm.import_step("XMHD-540.N101.I101.STP")
    h101 = arm.import_step("FR13-H101K.stp")
    s102 = arm.import_step("FR13-S102K.stp")
    joint_body = arm.actuator_to_joint_frame(xm540)
    j1_body = arm.rotate_x(joint_body, 90.0)
    j1_s102 = arm.rotate_x(s102, 90.0)
    j2_body = arm.rotate_x(joint_body, 90.0).translate((0.0, arm.J2_Y, 0.0))
    j2_s102 = arm.rotate_x(s102, 90.0).translate((0.0, arm.J2_Y, 0.0))
    fore_p_y = arm.J2_Y + 32.0
    return {
        "COLUMN_40_4040_ENVELOPE": arm.column_envelope(),
        "MV0_C05_SHOULDER_SUPPORT": arm.shoulder_support_plate(),
        "J1_XM540": j1_body,
        "J1_S102": j1_s102,
        "J1_H101": h101,
        "MV0_C01_UPPER_PROX_ADAPTER": arm.adapter(32.0),
        "UPPER_20_2040_ENVELOPE": arm.beam(32.0 + arm.PLATE_T, arm.UPPER_BEAM_L),
        "MV0_C07_FIXED_CATCH": arm.j2_positive_catch_adapter(32.0 + arm.PLATE_T + arm.UPPER_BEAM_L),
        "J2_XM540": j2_body,
        "J2_S102": j2_s102,
        "J2_H101": h101.translate((0.0, arm.J2_Y, 0.0)),
        "MV0_C06_MOVING_STRIKER": arm.j2_positive_striker_adapter(fore_p_y),
        "FORE_20_2040_ENVELOPE": arm.beam(fore_p_y + arm.PLATE_T, arm.FOREARM_BEAM_L),
        "MV0_C04_H104_ADAPTER": arm.gripper_adapter(fore_p_y + arm.PLATE_T + arm.FOREARM_BEAM_L),
    }


def collision_sweep(gripper_world: dict[str, cq.Shape], arm_components: dict[str, cq.Shape]) -> tuple[list[dict[str, object]], dict[str, object]]:
    fixed = {
        key: arm_components[key]
        for key in ("COLUMN_40_4040_ENVELOPE", "MV0_C05_SHOULDER_SUPPORT", "J1_XM540", "J1_S102")
    }
    upper = {
        key: arm_components[key]
        for key in ("J1_H101", "MV0_C01_UPPER_PROX_ADAPTER", "UPPER_20_2040_ENVELOPE", "MV0_C07_FIXED_CATCH", "J2_XM540", "J2_S102")
    }
    fixed_bounds = {name: arm.bbox_tuple(shape) for name, shape in fixed.items()}
    q1_values = [J1_LIMITS_DEG[0] + i * COLLISION_INCREMENT_DEG for i in range(int(round((J1_LIMITS_DEG[1] - J1_LIMITS_DEG[0]) / COLLISION_INCREMENT_DEG)) + 1)]
    q2_values = [J2_LIMITS_DEG[0] + i * COLLISION_INCREMENT_DEG for i in range(int(round((J2_LIMITS_DEG[1] - J2_LIMITS_DEG[0]) / COLLISION_INCREMENT_DEG)) + 1)]

    upper_by_q2: dict[float, tuple[float, list[str], dict[str, cq.Shape]]] = {}
    for q2 in q2_values:
        relative = {name: arm.rotate_x(shape, q2, arm.J2_Y) for name, shape in gripper_world.items()}
        volume = 0.0
        pairs: list[str] = []
        for upper_name, upper_shape in upper.items():
            for gripper_name, gripper_shape in relative.items():
                if arm.boxes_overlap(upper_shape, gripper_shape):
                    value = arm.positive_intersection(upper_shape, gripper_shape)
                    volume += value
                    if value > 1e-5:
                        pairs.append(f"{upper_name}:{gripper_name}={value:.6f}")
        upper_by_q2[q2] = (volume, pairs, relative)

    rows: list[dict[str, object]] = []
    maximum = 0.0
    collision_count = 0
    for q2 in q2_values:
        upper_volume, upper_pairs, relative = upper_by_q2[q2]
        relative_bounds = {name: arm.bbox_tuple(shape) for name, shape in relative.items()}
        for q1 in q1_values:
            volume = upper_volume
            pairs = list(upper_pairs)
            transformed_cache: dict[str, cq.Shape] = {}
            for fixed_name, fixed_shape in fixed.items():
                for gripper_name, relative_shape in relative.items():
                    rotated_bounds = arm.rotate_bbox_x(relative_bounds[gripper_name], q1)
                    if not arm.bbox_values_overlap(fixed_bounds[fixed_name], rotated_bounds):
                        continue
                    transformed = transformed_cache.setdefault(gripper_name, arm.rotate_x(relative_shape, q1))
                    value = arm.positive_intersection(fixed_shape, transformed)
                    volume += value
                    if value > 1e-5:
                        pairs.append(f"{fixed_name}:{gripper_name}={value:.6f}")
            maximum = max(maximum, volume)
            if volume > 1e-5:
                collision_count += 1
            rows.append({
                "j1_deg": f"{q1:.1f}",
                "j2_internal_deg": f"{q2:.1f}",
                "positive_intersection_mm3": f"{volume:.9f}",
                "colliding_pairs": ";".join(pairs),
                "result": "PASS_NOMINAL_SAMPLE" if volume <= 1e-5 else "COLLISION",
                "scope": f"new XC330 wrist components versus controlled P0.7 fixed/upper bodies; exact booleans after per-component conservative AABB broadphase; {COLLISION_INCREMENT_DEG:.0f} degree samples only; cables guards tolerances deformation and between-sample proof excluded",
            })
    summary = {
        "samples": len(rows),
        "increment_deg": COLLISION_INCREMENT_DEG,
        "j1_limits_deg": list(J1_LIMITS_DEG),
        "j2_limits_deg": list(J2_LIMITS_DEG),
        "collision_samples": collision_count,
        "maximum_positive_intersection_mm3": round(maximum, 9),
        "status": "NOMINAL SAMPLED SCREEN ONLY - PHYSICAL AND CONTINUOUS PROOF OPEN",
    }
    return rows, summary


def guide_html(summary: dict[str, object]) -> str:
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{IDENTIFIER}</title><script type=\"module\" src=\"https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js\"></script><style>:root{{--sky:#8ed8f8;--navy:#102a56;--blue:#245aa6;--gold:#f2b827;--paper:#f7fbff;--ink:#14213d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}.warn{{background:var(--gold);color:#17223f;font-weight:800;padding:14px 18px;font-size:16px}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:clamp(24px,5vw,64px)}}header p{{max-width:78ch}}main{{max-width:1180px;margin:auto;padding:24px}}h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1.05;margin:.2em 0}}h2{{color:var(--navy);font-size:clamp(1.4rem,3vw,2.2rem)}}small{{font-size:14px}}.viewers,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}model-viewer{{width:100%;height:min(62vh,620px);min-height:420px;background:linear-gradient(#dff4ff,#fff);border:2px solid var(--navy);border-radius:18px}}.card{{background:white;border:2px solid var(--sky);border-radius:16px;padding:18px;box-shadow:0 6px 18px #102a5615}}.metric{{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;color:var(--blue)}}@media(max-width:520px){{main{{padding:16px}}model-viewer{{min-height:360px}}}}</style></head><body><div class=\"warn\">{WARNING}</div><header><small>R192 WRIST LOAD-PATH CORRECTION</small><h1>One controlled transform from forearm to object.</h1><p>The exact H104, XC330 and FPX330 source geometry now share one reviewable coordinate chain. Two project-owned bridge candidates connect the H104 side features to the existing S101/U-base field. Fasteners, tolerance, strength, cable, guarding and physical acceptance remain open.</p></header><main><section class=\"viewers\"><model-viewer src=\"hr-v0-xc330-wrist-integrated-mid-p0.1.glb\" camera-controls auto-rotate shadow-intensity=\"1\" alt=\"Interactive H104 and XC330 wrist integration candidate\"></model-viewer><model-viewer src=\"hr-v0-arm-xc330-integrated-reference-p0.1.glb\" camera-controls auto-rotate shadow-intensity=\"1\" alt=\"Interactive full HR-V0 arm with XC330 wrist candidate\"></model-viewer></section><section class=\"grid\"><article class=\"card\"><h2>H104 to gripper</h2><div class=\"metric\">Rx +90 deg</div><p>Translation (0, 4.0, 13.5) mm. Combined world reference is Rx 270 deg at (0, 327.6, -13.5) mm.</p></article><article class=\"card\"><h2>Nominal object center</h2><div class=\"metric\">Y 358.6 mm</div><p>The retained 31 mm pad-center datum sits 1.4 mm inside the existing 360 mm reach reserve.</p></article><article class=\"card\"><h2>Sampled arm screen</h2><div class=\"metric\">{summary['collision_samples']} / {summary['samples']}</div><p>Positive-collision samples over J1 -20..70 deg and J2 15..115 deg at {summary['increment_deg']:.0f} deg increments. This is not continuous or as-built proof.</p></article><article class=\"card\"><h2>Incomplete headroom</h2><div class=\"metric\">{summary['headroom_g']:.3f} g</div><p>After two full-density 2.70 g/cm3 bridge candidates. H104, FPX frames, fasteners, cable, guard and physical variation remain excluded.</p></article></section><section class=\"card\"><h2>What remains held</h2><p>The H104 drawing is for reference only and omits released project tolerances and tap engagement. GRIP-002 still names the OpenMANIPULATOR mechanism, so selecting this XC330 branch requires controlled requirement/configuration disposition. Every H104 screw, shared S101 stack, bridge material/process, tool path, cable route, guard, receiver, load proof, received fit and qualified review remains open. No person may enter the mechanism or treat this page as assembly authority.</p></section></main></body></html>"""


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    GUIDE.mkdir(parents=True, exist_ok=True)

    h104 = arm.import_step("FR12-H104K.stp")
    plus_bridge = bridge(1)
    minus_bridge = bridge(-1)
    export_part("hr-v0-xc330-h104-bridge-plus-p0.1", plus_bridge)
    export_part("hr-v0-xc330-h104-bridge-minus-p0.1", minus_bridge)

    pose_sets = {name: gripper_components(opening) for name, opening in (("closed", 40.0), ("mid", 58.0), ("open", 76.0))}
    contact_rows: list[dict[str, object]] = []
    for pose, components in pose_sets.items():
        transformed = {name: to_h104(shape) for name, shape in components.items()}
        group = cq.Compound.makeCompound(list(transformed.values()))
        contact_rows.append({
            "pose": pose,
            "pair": "official H104 versus complete P0.2 gripper",
            "positive_intersection_mm3": f"{h104.intersect(group).Volume():.9f}",
            "minimum_distance_mm": f"{h104.distance(group):.9f}",
            "status": "intentional nominal contact allowed; positive volume prohibited; received fit open",
        })
    base_h104 = to_h104(grip.gripper_base())
    for label, candidate in (("+X", plus_bridge), ("-X", minus_bridge)):
        contact_rows.extend([
            {
                "pose": "all",
                "pair": f"H104 versus {label} bridge",
                "positive_intersection_mm3": f"{h104.intersect(candidate).Volume():.9f}",
                "minimum_distance_mm": f"{h104.distance(candidate):.9f}",
                "status": "intentional nominal face contact; physical tolerance and seating open",
            },
            {
                "pose": "all",
                "pair": f"P0.2 U-base versus {label} bridge",
                "positive_intersection_mm3": f"{base_h104.intersect(candidate).Volume():.9f}",
                "minimum_distance_mm": f"{base_h104.distance(candidate):.9f}",
                "status": "intentional nominal ear-face contact; physical tolerance and seating open",
            },
        ])
    write_csv(OUT / "contact-clearance-register.csv", contact_rows)

    bridge_mass_g = (plus_bridge.Volume() + minus_bridge.Volume()) / 1000.0 * BRIDGE_DENSITY_G_CM3
    subtotal_g = 679.124713 + bridge_mass_g
    headroom_g = 750.0 - subtotal_g

    object_h104 = transformed_point_h104(OBJECT_CENTER_GRIPPER_MM)
    object_world = transformed_point_world(OBJECT_CENTER_GRIPPER_MM)
    combined_world_translation = transformed_point_world((0.0, 0.0, 0.0))
    transform_rows = [
        {"item": "G1 H104 frame", "parent": "WORLD", "translation_mm": "(0.0,331.6,0.0)", "rotation": "Rx 180 deg", "result": "controlled P0.7 transform; received A07 fit open"},
        {"item": "XC330 gripper root", "parent": "G1 H104", "translation_mm": "(0.0,4.0,13.5)", "rotation": "Rx +90 deg", "result": "exact source-coordinate candidate; not selected"},
        {"item": "XC330 gripper root", "parent": "WORLD", "translation_mm": f"({combined_world_translation[0]:.1f},{combined_world_translation[1]:.1f},{combined_world_translation[2]:.1f})", "rotation": "Rx 270 deg", "result": "matrix-composed reference pose"},
        {"item": "nominal pad/object center", "parent": "G1 H104", "translation_mm": f"({object_h104[0]:.1f},{object_h104[1]:.1f},{object_h104[2]:.1f})", "rotation": "point datum", "result": "nominal CAD only; installed pad calibration open"},
        {"item": "nominal pad/object center", "parent": "WORLD", "translation_mm": f"({object_world[0]:.1f},{object_world[1]:.1f},{object_world[2]:.1f})", "rotation": "point datum", "result": "world Y is 1.4 mm inside retained 360 mm reserve"},
    ]
    write_csv(OUT / "transform-register.csv", transform_rows)

    pcd_offset = 8.0 / math.sqrt(2.0)
    pcd_axes = [
        transformed_point_h104((0.0, y, z))[1:]
        for y in (-pcd_offset, pcd_offset)
        for z in (-8.0 - pcd_offset, -8.0 + pcd_offset)
    ]
    hole_rows: list[dict[str, object]] = []
    for side in ("+X", "-X"):
        for y, z in H104_M2_TAP_AXES_YZ:
            hole_rows.append({"interface": "H104 to bridge", "side": side, "y_mm": f"{y:.6f}", "z_mm": f"{z:.6f}", "source_feature": "M2 tap; STEP minor cylinder 1.567 mm; drawing 4-M2 tap", "bridge_hole": "diameter 2.20 mm candidate clearance", "fastener": "SELECTION REQUIRED", "status": "received thread/engagement/access/proof open"})
        for y, z in pcd_axes:
            hole_rows.append({"interface": "S101/U-base to bridge", "side": side, "y_mm": f"{y:.6f}", "z_mm": f"{z:.6f}", "source_feature": "S101 PCD16 transformed field", "bridge_hole": "diameter 2.20 mm candidate clearance", "fastener": "SELECTION REQUIRED", "status": "complete shared stack/engagement/access/proof open"})
    write_csv(OUT / "hole-register.csv", hole_rows)

    fastener_rows = [
        {"stack_id": "WRI-F01", "interface": "H104 M2 taps to two bridge plates", "quantity": 4, "order_code": "SELECTION REQUIRED", "known_source": "FR12-H104 drawing identifies 4-M2 tap; exact transverse axes from STEP", "unknowns": "screw type/length/head/tool/engagement/torque/locking/reuse/material and received thread quality", "state": "OPEN - NO ASSEMBLY RELEASE"},
        {"stack_id": "WRI-F02", "interface": "S101 PCD16 plus P0.2 U-base ear plus bridge", "quantity": 8, "order_code": "SELECTION REQUIRED", "known_source": "exact transformed PCD16 axes; nominal 7 mm frame + 3 mm ear + 3 mm bridge geometry", "unknowns": "received stack, screw/nut/washer identity, length, head/tool, protrusion, torque, locking and reuse", "state": "OPEN - NO ASSEMBLY RELEASE"},
        {"stack_id": "WRI-F03", "interface": "existing MV0-C04 to H104 A07", "quantity": 4, "order_code": "SCB2.5-20 + HNN-M2.5-A2 EXACT CANDIDATE HOLD", "known_source": "controlled P0.7 stack unchanged by bridge topology", "unknowns": "received identity/stack/tolerance/protrusion/torque/access/proof and qualified acceptance", "state": "OPEN - NO ASSEMBLY RELEASE"},
    ]
    write_csv(OUT / "fastener-stack-register.csv", fastener_rows)

    bridge_rows = [
        {"part": "hr-v0-xc330-h104-bridge-plus-p0.1", "side": "+X", "envelope_mm": "3.0 x 20.0 x 31.5", "volume_mm3": f"{plus_bridge.Volume():.9f}", "mass_screen_g": f"{plus_bridge.Volume() / 1000.0 * BRIDGE_DENSITY_G_CM3:.6f}", "material_process": "6061-family 2.70 g/cm3 screening assumption; exact stock/temper/MTR/process SELECTION REQUIRED", "state": "NATIVE CANDIDATE - NOT RELEASED"},
        {"part": "hr-v0-xc330-h104-bridge-minus-p0.1", "side": "-X", "envelope_mm": "3.0 x 20.0 x 31.5", "volume_mm3": f"{minus_bridge.Volume():.9f}", "mass_screen_g": f"{minus_bridge.Volume() / 1000.0 * BRIDGE_DENSITY_G_CM3:.6f}", "material_process": "6061-family 2.70 g/cm3 screening assumption; exact stock/temper/MTR/process SELECTION REQUIRED", "state": "NATIVE CANDIDATE - NOT RELEASED"},
    ]
    write_csv(OUT / "bridge-register.csv", bridge_rows)

    source_rows = [
        {"source_id": "WRI-S01", "record": "ROBOTIS FR12-H104K STEP", "locator": "cad/vendor/robotis/FR12-H104K.stp", "revision_date": "drawing family 2017-08-31; retrieved 2026-08-06", "sha256": sha256(ROOT / "cad/vendor/robotis/FR12-H104K.stp"), "use": "exact H104 B-Rep, inner faces and feature axes"},
        {"source_id": "WRI-S02", "record": "ROBOTIS FR12-H104K reference drawing", "locator": "cad/vendor/robotis/FR12-H104K.pdf", "revision_date": "2017-08-31; marked FOR REFERENCE ONLY", "sha256": sha256(ROOT / "cad/vendor/robotis/FR12-H104K.pdf"), "use": "38 mm inside width, 1.5 mm side stock, hole-family and M2-tap labels"},
        {"source_id": "WRI-S03", "record": "controlled arm architecture P0.7", "locator": "cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json", "revision_date": "2026-08-07", "sha256": sha256(ROOT / "cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json"), "use": "A07/G1 transforms, limits, collision and reach reserve"},
        {"source_id": "WRI-S04", "record": "XC330 gripper interface P0.2", "locator": "cad/hr-v0/generated/xc330-gripper-interface-p0.2/package-summary.json", "revision_date": "2026-08-10", "sha256": sha256(ROOT / "cad/hr-v0/generated/xc330-gripper-interface-p0.2/package-summary.json"), "use": "exact actuator/frame branch, PCD16 field, kinematics and incomplete mass basis"},
    ]
    write_csv(OUT / "source-register.csv", source_rows)

    mid_h104_components = {name: to_h104(shape) for name, shape in pose_sets["mid"].items()}
    wrist_assembly = cq.Assembly(name=f"{IDENTIFIER}-WRIST-MID")
    wrist_assembly.add(h104, name="H104_OFFICIAL", color=cq.Color(0.30, 0.65, 0.88))
    wrist_assembly.add(plus_bridge, name="BRIDGE_PLUS", color=cq.Color(0.95, 0.45, 0.10))
    wrist_assembly.add(minus_bridge, name="BRIDGE_MINUS", color=cq.Color(0.95, 0.45, 0.10))
    for name, shape in mid_h104_components.items():
        wrist_assembly.add(shape, name=name, color=cq.Color(0.12, 0.35, 0.68) if "CUSTOM" not in name else cq.Color(0.20, 0.72, 0.90))
    wrist_step = OUT / "hr-v0-xc330-wrist-integrated-mid-p0.1.step"
    wrist_glb = OUT / "hr-v0-xc330-wrist-integrated-mid-p0.1.glb"
    wrist_assembly.save(str(wrist_step)); grip.normalize_step(wrist_step)
    wrist_assembly.save(str(wrist_glb))

    arm_components = build_arm_reference_components()
    mid_world = {name: gripper_to_world(shape) for name, shape in pose_sets["mid"].items()}
    bridge_world = {"BRIDGE_PLUS": h104_to_world(plus_bridge), "BRIDGE_MINUS": h104_to_world(minus_bridge)}
    h104_world = h104_to_world(h104)
    full_assembly = cq.Assembly(name=f"{IDENTIFIER}-FULL-ARM-REFERENCE")
    for name, shape in arm_components.items():
        full_assembly.add(shape, name=name, color=cq.Color(0.55, 0.59, 0.64))
    full_assembly.add(h104_world, name="G1_H104_OFFICIAL", color=cq.Color(0.30, 0.65, 0.88))
    for name, shape in bridge_world.items():
        full_assembly.add(shape, name=name, color=cq.Color(0.95, 0.45, 0.10))
    for name, shape in mid_world.items():
        full_assembly.add(shape, name=name, color=cq.Color(0.12, 0.35, 0.68) if "CUSTOM" not in name else cq.Color(0.20, 0.72, 0.90))
    full_step = OUT / "hr-v0-arm-xc330-integrated-reference-p0.1.step"
    full_glb = OUT / "hr-v0-arm-xc330-integrated-reference-p0.1.glb"
    full_assembly.save(str(full_step)); grip.normalize_step(full_step)
    full_assembly.save(str(full_glb))

    gripper_collision_world = {name: gripper_to_world(shape) for name, shape in pose_sets["open"].items()}
    gripper_collision_world.update(bridge_world)
    sweep_rows, sweep_summary = collision_sweep(gripper_collision_world, arm_components)
    write_csv(OUT / "collision-sweep.csv", sweep_rows)
    (OUT / "collision-summary.json").write_text(json.dumps(sweep_summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    hold_rows = [
        ("WRI-H01", "CONFIGURATION/REQUIREMENT", "Approve or reject the XC330 branch and formally disposition GRIP-002 before any active baseline change."),
        ("WRI-H02", "RECEIVED H104", "Receive, identify, inspect and gauge the exact H104 frame including inside width, side flatness, all selected axes and M2 taps."),
        ("WRI-H03", "BRIDGE MATERIAL", "Select exact stock/alloy/temper/MTR, corrosion treatment, process, grain orientation and finished-part controls."),
        ("WRI-H04", "BRIDGE DRAWING/FAI", "Release tolerances, edge treatment, positional controls, flatness/parallelism and execute first-article inspection."),
        ("WRI-H05", "H104 FASTENERS", "Select and prove exact H104 M2-tap screw identity, length, head/tool access, engagement, torque, locking and reuse."),
        ("WRI-H06", "S101 SHARED STACK", "Select and prove the complete S101/U-base/bridge screw, nut, washer, protrusion, torque and locking stack."),
        ("WRI-H07", "ASSEMBLY SEQUENCE", "Demonstrate an unpowered assembly/disassembly sequence with tool access, no forced alignment and service access."),
        ("WRI-H08", "TOLERANCE CLOSURE", "Close H104/bridge/U-base/S101 tolerance, seating, parallelism and no-preload-deflection stack with received data."),
        ("WRI-H09", "LOAD PATH", "Calculate and prove jaw/payload/jam loads through S101, U-base, bridges, H104, A07 and forearm including fatigue and fastener effects."),
        ("WRI-H10", "COLLISION", "Replace the 5-degree nominal sample with tolerance-aware continuous gripper/arm/cable/guard collision proof and as-built sweep."),
        ("WRI-H11", "CABLE", "Define exact XC330 cable, connector, bend/twist envelope, route, clamp, strain relief, flex life and full-pose inspection."),
        ("WRI-H12", "GUARD", "Design retained fixed guarding/bellows for every rack, pinion, slot, jaw and wrist pinch line and probe-test it."),
        ("WRI-H13", "RECEIVER/OBJECT", "Correlate the Y=358.6 mm nominal object datum to the fixed receiver and prove all release/fault/power-loss containment poses."),
        ("WRI-H14", "MASS/COM/INERTIA", "Measure H104, FPX frames, bridges, fasteners, cable, guard and complete assembly; reconcile mass, COM and inertia."),
        ("WRI-H15", "FORCE/CURRENT/THERMAL", "Execute calibrated grip-force, current, repeatability, temperature, wear and duty characterization."),
        ("WRI-H16", "PHYSICAL FIT/PROOF", "Execute received dry fit, FAI, guarded no-load, low-energy, jam, fault and proof tests under authorized procedures."),
        ("WRI-H17", "FUNCTIONAL SAFETY", "Allocate and validate guarding, restart, power-loss and receiver controls without assigning safety credit to ordinary control logic."),
        ("WRI-H18", "QUALIFIED REVIEW", "Obtain signed mechanical, electrical and safety review of one frozen as-built configuration before release changes."),
    ]
    write_csv(OUT / "hold-register.csv", [{"hold_id": hid, "scope": scope, "evidence_required": evidence, "status": "OPEN", "release_effect": "NO PROCUREMENT/FABRICATION/ASSEMBLY/CONNECTION/MOTION/ENERGIZATION"} for hid, scope, evidence in hold_rows])

    mass_rows = [
        {"item": "P0.2 incomplete subtotal before wrist bridges", "mass_g": "679.124713", "basis": "R191 screen", "boundary": "H104, FPX frames, hardware, cable, guard and variation excluded"},
        {"item": "two bridge candidates", "mass_g": f"{bridge_mass_g:.6f}", "basis": "native volume at 2.70 g/cm3", "boundary": "screening assumption; exact material/process/FAI/measured mass open"},
        {"item": "P0.1 wrist-integrated incomplete subtotal", "mass_g": f"{subtotal_g:.6f}", "basis": "arithmetic", "boundary": "not mass closure"},
        {"item": "remaining incomplete headroom to 750 g", "mass_g": f"{headroom_g:.6f}", "basis": "750 - subtotal", "boundary": "must cover every excluded received item and variation"},
    ]
    write_csv(OUT / "mass-screen.csv", mass_rows)

    summary = {
        "identifier": IDENTIFIER,
        "date": "2026-08-10",
        "status": "SOURCE-BOUND WRIST-INTEGRATION CANDIDATE - NOT SELECTED",
        "h104_step_sha256": sha256(ROOT / "cad/vendor/robotis/FR12-H104K.stp"),
        "h104_pdf_sha256": sha256(ROOT / "cad/vendor/robotis/FR12-H104K.pdf"),
        "gripper_identifier": "HR-V0-GRIP-XC330-P0.2",
        "arm_identifier": "HR-V0-ARM-ARCH-P0.7",
        "gripper_to_h104_translation_mm": list(GRIPPER_T_H104_MM),
        "gripper_to_h104_rx_deg": GRIPPER_RX_H104_DEG,
        "gripper_world_translation_mm": list(combined_world_translation),
        "gripper_world_rx_deg": 270.0,
        "nominal_object_center_h104_mm": list(object_h104),
        "nominal_object_center_world_mm": list(object_world),
        "world_y_reach_reserve_mm": 360.0 - object_world[1],
        "bridge_pair_mass_screen_g": round(bridge_mass_g, 6),
        "screen_subtotal_g": round(subtotal_g, 6),
        "remaining_incomplete_headroom_g": round(headroom_g, 6),
        "collision_screen": sweep_summary,
        "open_holds": len(hold_rows),
        "requirements_closed": 0,
        "energization_gates_closed": 0,
        "sol_blockers_closed": 0,
        "procurement_release": False,
        "fabrication_release": False,
        "assembly_release": False,
        "connection_release": False,
        "motion_release": False,
        "energization_release": False,
        "warning": WARNING,
    }
    (OUT / "package-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    shutil.copy2(wrist_glb, GUIDE / wrist_glb.name)
    shutil.copy2(full_glb, GUIDE / full_glb.name)
    (GUIDE / "index.html").write_text(guide_html({**sweep_summary, "headroom_g": headroom_g}), encoding="utf-8", newline="\n")
    write_generated_source_manifest()

    print(f"Generated {IDENTIFIER}: H104->gripper Rx90 T(0,4,13.5); object world Y={object_world[1]:.1f}; sampled collisions {sweep_summary['collision_samples']}/{sweep_summary['samples']}; incomplete headroom {headroom_g:.3f} g")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
