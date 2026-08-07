"""Generate the strengthened exact-coordinate HR-V0 arm candidate for R56.

The exported geometry is a feasibility/configuration candidate.  It is not a
fabrication release.  Purchased 80/20 stock remains a conservative 20 x 40 mm
collision envelope, while the manufacturer-published end-tap coordinates,
ROBOTIS frame hole patterns, candidate countersunk fastener envelope and
vendor-coordinate actuator rotation are modeled explicitly.  Tolerances,
torque, physical fit and proof requirements remain open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad" / "vendor" / "robotis"
VENDOR_8020 = ROOT / "cad" / "vendor" / "8020"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.3"
REVISION = "HR-V0-ARM-ARCH-P0.3"
WARNING = "PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION"

PLATE_T = 9.525
PLATE_MIN_T = 9.0
PLATE_MAX_T = 10.0
UPPER_BEAM_L = 100.0
FOREARM_BEAM_L = 50.0
J2_Y = round(32.0 + PLATE_T + UPPER_BEAM_L + PLATE_T + 51.5, 4)
G1_Y = round(J2_Y + 32.0 + PLATE_T + FOREARM_BEAM_L + PLATE_T + 28.0, 4)
FRAME_HOLE_D = 2.70
END_HOLE_D = 5.50
END_CSK_D = 10.07
END_CSK_D_MIN = 9.43
END_CSK_DEPTH = 3.10
END_TAP_SPACING = 20.0
M5_SCREW_LENGTH = 20.0
M2_5_SCREW_LENGTH = 16.0
H101_LINK_FACE_T = 2.0
H101_LINK_FACE_MAX_T = 2.2
M2_5_NUT_T = 2.0
ACTUATOR_AXIAL_OFFSET_X = 1.75
COLLISION_INCREMENT_DEG = 0.5
PROVISIONAL_J2_SOFT_LIMIT_DEG = 120.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonicalize_step(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']*'",
        r"\1'1980-01-01T00:00:00'",
        text,
        count=1,
    )
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def import_step(name: str) -> cq.Shape:
    return cq.importers.importStep(str(VENDOR / name)).val()


def rotate_x(shape: cq.Shape, angle_deg: float, origin_y: float = 0.0) -> cq.Shape:
    return shape.rotate((0.0, origin_y, 0.0), (1.0, origin_y, 0.0), angle_deg)


def actuator_to_joint_frame(shape: cq.Shape) -> cq.Shape:
    """Map ROBOTIS actuator STEP coordinates into the FR13 joint frame.

    The proper rotation is fixed by two independent registrations:
    local actuator +Z (output axis) maps to joint -X, and the two bottom
    mounting axes at local (x=+/-13.5, y=-41.5) map exactly to the S102 axes
    at joint (y=+/-13.5, z=41.5).  The X translation only places the axial
    display envelope; received horn/idler stack measurement remains open.
    """
    transform = gp_Trsf()
    transform.SetValues(
        0.0, 0.0, -1.0, ACTUATOR_AXIAL_OFFSET_X,
        1.0, 0.0, 0.0, 0.0,
        0.0, -1.0, 0.0, 0.0,
    )
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, transform, True).Shape())


def adapter(y0: float) -> cq.Shape:
    solid = cq.Solid.makeBox(48.0, PLATE_T, 40.0, cq.Vector(-24.0, y0, -20.0))
    # ROBOTIS's assembly precedent uses the rectangular +/-16 x +/-8 pattern,
    # not the PCD22 horn pattern incorrectly used in P0.1.
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            hole = cq.Solid.makeCylinder(FRAME_HOLE_D / 2.0, PLATE_T, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
            solid = solid.cut(hole)
    # The purchased profile's published 4.19 mm cores lie on the 40 mm axis,
    # 20 mm apart.  A 90-degree countersink keeps the M5 candidate flush under
    # the ROBOTIS frame.  R56 increases the adapter from 4.7625 mm to nominal
    # 9.525 mm and sets a 9.0 mm finished minimum; material certification,
    # countersink inspection and physical proof remain release gates.
    for z in (-10.0, 10.0):
        hole = cq.Solid.makeCylinder(END_HOLE_D / 2.0, PLATE_T, cq.Vector(0, y0, z), cq.Vector(0, 1, 0))
        solid = solid.cut(hole)
        countersink = cq.Solid.makeCone(
            END_CSK_D / 2.0,
            END_HOLE_D / 2.0,
            END_CSK_DEPTH,
            cq.Vector(0, y0, z),
            cq.Vector(0, 1, 0),
        )
        solid = solid.cut(countersink)
    return solid


def beam(y0: float, length: float) -> cq.Shape:
    # The purchased section remains a conservative envelope.  The 40 mm axis is
    # vertical so the two end taps at z=+/-10 provide a torque-resisting couple
    # about the X joint axis; P0.1's horizontal orientation did not.
    return cq.Solid.makeBox(20.0, length, 40.0, cq.Vector(-10.0, y0, -20.0))


def matrix_x(angle_deg: float, tx: float, ty: float, tz: float) -> list[list[float]]:
    c = round(math.cos(math.radians(angle_deg)), 12)
    s = round(math.sin(math.radians(angle_deg)), 12)
    return [[1.0, 0.0, 0.0, tx], [0.0, c, -s, ty], [0.0, s, c, tz], [0.0, 0.0, 0.0, 1.0]]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def positive_intersection(a: cq.Shape, b: cq.Shape) -> float:
    try:
        return max(0.0, a.intersect(b).Volume())
    except Exception:
        return float("inf")


def boxes_overlap(a: cq.Shape, b: cq.Shape, tolerance: float = 1e-6) -> bool:
    aa = a.BoundingBox()
    bb = b.BoundingBox()
    return not (
        aa.xmax < bb.xmin - tolerance or bb.xmax < aa.xmin - tolerance
        or aa.ymax < bb.ymin - tolerance or bb.ymax < aa.ymin - tolerance
        or aa.zmax < bb.zmin - tolerance or bb.zmax < aa.zmin - tolerance
    )


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    xm540 = import_step("XMHD-540.N101.I101.STP")
    h101 = import_step("FR13-H101K.stp")
    s102 = import_step("FR13-S102K.stp")
    h104 = import_step("FR12-H104K.stp")

    # Reference pose: J1 and J2 axes are parallel +X.  The raw actuator STEP
    # output axis is local Z and must first be mapped into the joint frame.  The
    # J2 fixed package is then rolled +90 degrees about X so the S102 broad face
    # opposes the upper-link distal adapter.  A -90 degree output reference
    # returns H101 and the straight forearm to project +Y.
    joint_body = actuator_to_joint_frame(xm540)
    j1_body = joint_body
    j1_h101 = h101
    upper_p = adapter(32.0)
    upper_b = beam(32.0 + PLATE_T, UPPER_BEAM_L)
    upper_d = adapter(32.0 + PLATE_T + UPPER_BEAM_L)
    j2_body = rotate_x(joint_body, 90.0).translate((0.0, J2_Y, 0.0))
    j2_s102 = rotate_x(s102, 90.0).translate((0.0, J2_Y, 0.0))
    j2_h101 = h101.translate((0.0, J2_Y, 0.0))
    fore_p_y = J2_Y + 32.0
    fore_p = adapter(fore_p_y)
    fore_b = beam(fore_p_y + PLATE_T, FOREARM_BEAM_L)
    fore_d = adapter(fore_p_y + PLATE_T + FOREARM_BEAM_L)
    gripper_frame = rotate_x(h104, 180.0).translate((0.0, G1_Y, 0.0))

    components = {
        "J1_XM540": j1_body,
        "J1_H101": j1_h101,
        "UL_PROX_ADAPTER": upper_p,
        "UL_20-2040_VERTICAL_ENVELOPE": upper_b,
        "UL_DIST_ADAPTER": upper_d,
        "J2_XM540_RX90": j2_body,
        "J2_S102_RX90": j2_s102,
        "J2_H101_OUTPUT_REFERENCE": j2_h101,
        "FA_PROX_ADAPTER": fore_p,
        "FA_20-2040_VERTICAL_50MM_ENVELOPE": fore_b,
        "FA_DIST_ADAPTER": fore_d,
        "G1_H104_RX180": gripper_frame,
    }

    assembly = cq.Assembly(name="HR_V0_ARM_ARCHITECTURE_CANDIDATE_NOT_RELEASED")
    colors = {
        "J1_XM540": cq.Color(0.05, 0.25, 0.50),
        "J2_XM540_RX90": cq.Color(0.05, 0.25, 0.50),
        "J1_H101": cq.Color(0.95, 0.70, 0.10),
        "J2_H101_OUTPUT_REFERENCE": cq.Color(0.95, 0.70, 0.10),
        "J2_S102_RX90": cq.Color(0.40, 0.78, 0.96),
        "G1_H104_RX180": cq.Color(0.40, 0.78, 0.96),
    }
    for name, solid in components.items():
        assembly.add(solid, name=name, color=colors.get(name, cq.Color(0.65, 0.69, 0.73)))
    step_path = OUT / "HR-V0_arm_architecture_candidate.step"
    # Assembly STEP presentation records are emitted in nondeterministic map
    # order by OCC.  The controlled STEP is therefore an ordered geometry
    # compound; the GLB carries the component names and review colors.
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step_path))
    canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_arm_architecture_candidate.glb"))

    # Native candidate custom parts.  These define topology for review but are
    # expressly excluded from quotation/fabrication until tolerances, material,
    # fasteners, access and proof are released.
    part_dir = OUT / "parts"
    part_dir.mkdir()
    for name, solid in {
        "MV0-C01_rect32x16_to_20-2040_countersunk_adapter": adapter(0.0),
        "MV0-C02_20-2040_100mm_vertical_collision_envelope": beam(0.0, UPPER_BEAM_L),
        "MV0-C03_20-2040_50mm_vertical_collision_envelope": beam(0.0, FOREARM_BEAM_L),
    }.items():
        part_path = part_dir / f"{name}.step"
        cq.exporters.export(solid, str(part_path))
        canonicalize_step(part_path)

    actuator_matrix = [[0.0, 0.0, -1.0, ACTUATOR_AXIAL_OFFSET_X], [1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    transform_rows = [
        {"item": "J1 XM540 body", "parent": "J1 frame", "tx_mm": ACTUATOR_AXIAL_OFFSET_X, "ty_mm": 0, "tz_mm": 0, "rx_deg": "proper axis-map", "matrix_4x4_row_major": json.dumps(actuator_matrix), "status": "axis and S102 hole registration exact; axial horn/idler stack candidate only"},
        {"item": "J1 H101 output reference", "parent": "J1 output", "tx_mm": 0, "ty_mm": 0, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, 0, 0)), "status": "exact vendor geometry; fastener stack open"},
        {"item": "J2 joint package and S102", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 90, "matrix_4x4_row_major": json.dumps(matrix_x(90, 0, J2_Y, 0)), "status": "package roll exact; internal XM540 uses the recorded actuator axis-map"},
        {"item": "J2 H101 straight-reference pose", "parent": "WORLD", "tx_mm": 0, "ty_mm": J2_Y, "tz_mm": 0, "rx_deg": 0, "matrix_4x4_row_major": json.dumps(matrix_x(0, 0, J2_Y, 0)), "status": "requires -90 deg output offset relative J2 body"},
        {"item": "G1 H104 frame", "parent": "WORLD", "tx_mm": 0, "ty_mm": G1_Y, "tz_mm": 0, "rx_deg": 180, "matrix_4x4_row_major": json.dumps(matrix_x(180, 0, G1_Y, 0)), "status": "candidate frame only; gripper transform open"},
    ]
    write_csv(OUT / "transform-schedule.csv", transform_rows)

    interface_rows = [
        {"interface": "A01", "from": "J1 H101 outside broad face", "to": "upper proximal adapter", "plane_world": "Y=32.0000 mm", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "WF2339 + WF1254 EXACT CANDIDATE HOLD; torque/retention/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A02", "from": "upper proximal adapter", "to": "20-2040 end", "plane_world": f"Y={32.0 + PLATE_T:.4f} mm", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; 90-deg flush countersinks", "fasteners": "WF2563 EXACT CANDIDATE HOLD; torque/retention SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A03", "from": "20-2040 end", "to": "upper distal adapter", "plane_world": f"Y={32.0 + PLATE_T + UPPER_BEAM_L:.4f} mm", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; 90-deg flush countersinks", "fasteners": "WF2563 EXACT CANDIDATE HOLD; torque/retention SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A04", "from": "upper distal adapter", "to": "J2 S102 outside broad face", "plane_world": f"Y={J2_Y - 51.5:.4f} mm", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "WF2339 + WF1254 EXACT CANDIDATE HOLD; torque/retention/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A05", "from": "J2 H101 outside broad face", "to": "forearm proximal adapter", "plane_world": f"Y={fore_p_y:.4f} mm at straight reference", "pattern": "4 x manufacturer dia 2.5 thru at X=+/-16 Z=+/-8; adapter dia 2.70", "fasteners": "WF2339 + WF1254 EXACT CANDIDATE HOLD; torque/retention/received stack SELECTION REQUIRED", "status": "rectangular_pattern_registered_static_proof_only"},
        {"interface": "A06", "from": "forearm beam", "to": "forearm adapters", "plane_world": f"Y={fore_p_y + PLATE_T:.4f} and {fore_p_y + PLATE_T + FOREARM_BEAM_L:.4f} mm at straight reference", "pattern": "2 x M5x0.8 end taps at X=0 Z=+/-10; 90-deg flush countersinks", "fasteners": "WF2563 EXACT CANDIDATE HOLD; torque/retention SELECTION REQUIRED", "status": "manufacturer_coordinates_registered_static_proof_only"},
        {"interface": "A07", "from": "forearm distal adapter", "to": "H104 outside broad face", "plane_world": f"Y={fore_p_y + 2 * PLATE_T + FOREARM_BEAM_L:.4f} mm at straight reference", "pattern": "manufacturer broad-face pattern; final subset and adapter holes SELECTION REQUIRED", "fasteners": "SELECTION REQUIRED", "status": "transform_candidate_pattern_open"},
    ]
    write_csv(OUT / "interface-schedule.csv", interface_rows)

    fixed_upper = {
        "J1_BODY": j1_body,
        "J1_H101": j1_h101,
        "UPPER_PROX_ADAPTER": upper_p,
        "UPPER_MEMBER": upper_b,
        "UPPER_DIST_ADAPTER": upper_d,
        "J2_BODY": j2_body,
        "J2_S102": j2_s102,
    }
    moving_zero = {
        "J2_H101": j2_h101,
        "FORE_PROX_ADAPTER": fore_p,
        "FORE_MEMBER": fore_b,
        "FORE_DIST_ADAPTER": fore_d,
        "G1_H104": gripper_frame,
    }
    intentional_joint_pairs = {("J2_BODY", "J2_H101"), ("J2_S102", "J2_H101")}
    sweep_rows: list[dict[str, object]] = []
    worst = 0.0
    sample_count = int(round((125.0 - 15.0) / COLLISION_INCREMENT_DEG)) + 1
    for sample in range(sample_count):
        q_deg = 15.0 + sample * COLLISION_INCREMENT_DEG
        moving = {name: rotate_x(item, q_deg, J2_Y) for name, item in moving_zero.items()}
        volume = 0.0
        tested_pairs = 0
        colliding_pairs: list[str] = []
        for fixed_name, fixed_shape in fixed_upper.items():
            for moving_name, moving_shape in moving.items():
                if (fixed_name, moving_name) in intentional_joint_pairs:
                    continue
                if boxes_overlap(fixed_shape, moving_shape):
                    tested_pairs += 1
                    pair_volume = positive_intersection(fixed_shape, moving_shape)
                    volume += pair_volume
                    if pair_volume > 1e-5:
                        colliding_pairs.append(f"{fixed_name}:{moving_name}={pair_volume:.6f}")
        worst = max(worst, volume)
        if q_deg <= PROVISIONAL_J2_SOFT_LIMIT_DEG:
            result = "PASS" if volume <= 1e-5 else "COLLISION_WITHIN_PROVISIONAL_LIMIT"
        else:
            result = "COLLISION" if volume > 1e-5 else "OUTSIDE_PROVISIONAL_LIMIT"
        sweep_rows.append({"j2_internal_deg": f"{q_deg:.1f}", "broadphase_pairs_requiring_boolean": tested_pairs, "colliding_pairs": ";".join(colliding_pairs), "sampled_pairwise_intersection_mm3": f"{volume:.6f}", "result": result, "scope": "0.5-deg dense self-collision screen; intentional J2 frame/body interfaces excluded; provisional soft limit 120 deg; cables, tools, guards, stops and between-sample proof excluded"})
    write_csv(OUT / "collision-sweep.csv", sweep_rows)
    collision_angles = [float(row["j2_internal_deg"]) for row in sweep_rows if row["result"] in ("COLLISION", "COLLISION_WITHIN_PROVISIONAL_LIMIT")]
    first_nominal_collision_deg = min(collision_angles) if collision_angles else None
    max_intersection_within_limit = max(
        float(row["sampled_pairwise_intersection_mm3"])
        for row in sweep_rows
        if float(row["j2_internal_deg"]) <= PROVISIONAL_J2_SOFT_LIMIT_DEG
    )

    mass_per_m_kg = 0.0428 * 0.45359237 / 0.0254
    upper_beam_mass_g = mass_per_m_kg * (UPPER_BEAM_L / 1000.0) * 1000.0
    forearm_beam_mass_g = mass_per_m_kg * (FOREARM_BEAM_L / 1000.0) * 1000.0
    plate_mass_g = adapter(0.0).Volume() / 1000.0 * 2.70
    upper_link_mass_g = upper_beam_mass_g + 2 * plate_mass_g
    forearm_link_mass_g = forearm_beam_mass_g + 2 * plate_mass_g
    gravity = 9.80665
    upper_com_y = (32.0 + (J2_Y - 51.5)) / 2.0
    fore_com_y = J2_Y + 32.0 + PLATE_T + FOREARM_BEAM_L / 2.0
    shoulder_nm = gravity * (0.12 * upper_com_y / 1000.0 + 0.20 * J2_Y / 1000.0 + 0.12 * fore_com_y / 1000.0 + 0.21 * G1_Y / 1000.0 + 0.10 * 0.360)
    elbow_nm = gravity * (0.12 * (fore_com_y - J2_Y) / 1000.0 + 0.21 * (G1_Y - J2_Y) / 1000.0 + 0.10 * (360.0 - J2_Y) / 1000.0)
    shoulder_screen_nm = shoulder_nm * 2.25

    frame_to_end_center_mm = math.hypot(16.0, 2.0)
    feature_clearance_mm = frame_to_end_center_mm - END_CSK_D / 2.0 - FRAME_HOLE_D / 2.0
    m5_engagement_mm = M5_SCREW_LENGTH - PLATE_T
    m5_min_engagement_mm = M5_SCREW_LENGTH - PLATE_MAX_T
    m2_5_nominal_protrusion_mm = M2_5_SCREW_LENGTH - H101_LINK_FACE_T - PLATE_T - M2_5_NUT_T
    m2_5_screen_min_protrusion_mm = M2_5_SCREW_LENGTH - H101_LINK_FACE_MAX_T - PLATE_MAX_T - M2_5_NUT_T
    m5_couple_force_n = shoulder_screen_nm * 1000.0 / END_TAP_SPACING
    aluminum_shear_yield_mpa = 0.577 * 172.37
    thread_shear_area_mm2 = math.pi * 4.19 * m5_engagement_mm * 0.5
    thread_shear_capacity_n = thread_shear_area_mm2 * aluminum_shear_yield_mpa
    beam_bending_stress_mpa = shoulder_screen_nm * 1000.0 * 20.0 / (4.5357 * 10000.0)
    adapter_min_residual_mm = PLATE_MIN_T - END_CSK_DEPTH
    adapter_required_punching_shear_mpa = m5_couple_force_n / (math.pi * END_HOLE_D * adapter_min_residual_mm)
    adapter_head_annulus_mm2 = math.pi / 4.0 * (END_CSK_D_MIN ** 2 - END_HOLE_D ** 2)
    adapter_head_average_pressure_mpa = m5_couple_force_n / adapter_head_annulus_mm2
    kaiser_typical_yield_mpa = 276.0
    kaiser_typical_shear_yield_mpa = 0.577 * kaiser_typical_yield_mpa

    fastener_rows = [
        {"fastener_id": "FAST-C01", "interfaces": "A02;A03;A06", "candidate_order_code": "WF2563", "description": "M5 x 20 ISO 10642 90-degree socket countersunk screw; A2 stainless", "quantity_candidate": 8, "controlled_dimensions": "L=20 mm; head dia=9.43..10.07 mm; head height=2.669..3.100 mm; 3 mm socket; M5x0.8", "modeled_engagement_mm": f"{m5_engagement_mm:.4f} nominal; {m5_min_engagement_mm:.4f} screen minimum", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received full-thread confirmation, torque, lubrication/anti-galling, locking, countersink inspection and proof"},
        {"fastener_id": "FAST-C02", "interfaces": "A01;A04;A05", "candidate_order_code": "WF2339", "description": "M2.5 x 16 ISO 4762 socket head cap screw; A2 stainless", "quantity_candidate": 12, "controlled_dimensions": "L=16 mm; head dia max=4.5 mm; head height max=2.5 mm; 2 mm socket; M2.5x0.45; full thread at this length", "modeled_engagement_mm": f"{m2_5_nominal_protrusion_mm:.4f} nominal protrusion beyond 2 mm nut; {m2_5_screen_min_protrusion_mm:.4f} geometric screen minimum", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received frame/plate/nut stack, screw-length tolerance, protrusion, torque, locking, wrench access and proof"},
        {"fastener_id": "FAST-C03", "interfaces": "A01;A04;A05", "candidate_order_code": "WF1254", "description": "M2.5 DIN 934 full hex nut; A2 stainless", "quantity_candidate": 12, "controlled_dimensions": "M2.5x0.45; thickness 1.75 min / 2.00 max; across flats 4.82 min / 5.00 max", "modeled_engagement_mm": f"paired with WF2339; {m2_5_screen_min_protrusion_mm:.4f} geometric screen minimum before screw-length tolerance", "status": "EXACT CANDIDATE HOLD", "remaining_evidence": "received dimensions, torque, anti-galling/locking method, 5 mm tool envelope and proof"},
        {"fastener_id": "FAST-C04", "interfaces": "purchased member ends", "candidate_order_code": "20-7047", "description": "80/20 two-hole M5x0.8 end-tap service for 20-2040", "quantity_candidate": 4, "controlled_dimensions": "two taps; 22.23 mm published depth; 4.19 mm cores at 20 mm spacing", "modeled_engagement_mm": f"{m5_engagement_mm:.4f} nominal; {m5_min_engagement_mm:.4f} screen minimum", "status": "EXACT SERVICE CANDIDATE HOLD", "remaining_evidence": "written supplier confirmation, received thread gauge/depth inspection and proof joint"},
    ]
    write_csv(OUT / "fastener-candidate-schedule.csv", fastener_rows)

    access_rows = [
        {"check": "TA-01", "features": "M5 countersink to nearest M2.5 clearance hole", "result_mm": f"{feature_clearance_mm:.4f}", "criterion": ">= 1.0 mm nominal feature clearance", "result": "PASS NOMINAL", "release_effect": "does not release tolerance or machining process"},
        {"check": "TA-02", "features": "two M5 countersunk heads", "result_mm": f"{END_TAP_SPACING - END_CSK_D:.4f}", "criterion": ">= 1.0 mm nominal head-envelope clearance", "result": "PASS NOMINAL", "release_effect": "heads install before frame; service requires frame removal"},
        {"check": "TA-03", "features": "M2.5 clearance-hole edge at X=+/-16", "result_mm": f"{24.0 - 16.0 - FRAME_HOLE_D / 2.0:.4f}", "criterion": ">= 2d preliminary edge screen", "result": "PASS NOMINAL", "release_effect": "WF1254 nut fits nominally; 5 mm tool outer envelope remains SELECTION REQUIRED"},
        {"check": "TA-04", "features": "M5 countersink edge at Z=+/-10", "result_mm": f"{20.0 - 10.0 - END_CSK_D / 2.0:.4f}", "criterion": ">= 2.0 mm nominal edge clearance", "result": "PASS NOMINAL", "release_effect": "pull-through and fatigue proof remain open"},
        {"check": "TA-05", "features": "material remaining below maximum M5 countersink at finished minimum thickness", "result_mm": f"{adapter_min_residual_mm:.4f}", "criterion": ">= 5.0 mm project geometry screen; structural acceptance still requires proof", "result": "PASS NOMINAL / PROOF OPEN", "release_effect": "physical countersink inspection material certificate local analysis and proof remain required"},
        {"check": "TA-06", "features": "WF2339 protrusion beyond maximum-thickness WF1254 stack", "result_mm": f"{m2_5_screen_min_protrusion_mm:.4f}", "criterion": ">= 1.35 mm (3 x 0.45 mm pitch) geometric screen before screw-length tolerance", "result": "PASS NOMINAL / RECEIVED STACK OPEN", "release_effect": "received screw length frame/plate/nut stack and tool proof remain required"},
    ]
    write_csv(OUT / "tool-access-screen.csv", access_rows)

    load_rows = [
        {"screen": "LS-01", "item": "M5 end-tap bolt couple", "input": f"{shoulder_screen_nm:.4f} N m / {END_TAP_SPACING:.1f} mm", "result": f"{m5_couple_force_n:.2f} N", "basis": "no clamp-friction credit; already includes 2.25 screening multiplier", "status": "STATIC SCREEN PASS; PROOF OPEN"},
        {"screen": "LS-02", "item": "6063-T6 internal-thread shear", "input": f"4.19 mm core; {m5_engagement_mm:.4f} mm engagement; 0.5 circumference; 0.577 x 172.37 MPa", "result": f"{thread_shear_capacity_n:.1f} N capacity / {thread_shear_capacity_n / m5_couple_force_n:.1f} ratio", "basis": "conservative project inference from published yield; ignores preload, fatigue and countersink pull-through", "status": "STATIC SCREEN PASS; PHYSICAL PROOF OPEN"},
        {"screen": "LS-03", "item": "20-2040 strong-axis bending stress", "input": f"M={shoulder_screen_nm:.4f} N m; c=20 mm; I=4.5357 cm^4", "result": f"{beam_bending_stress_mpa:.4f} MPa / 172.37 MPa published yield", "basis": "purchased-section global bending only", "status": "STATIC SCREEN PASS; JOINT/DEFLECTION/FATIGUE OPEN"},
        {"screen": "LS-04", "item": "adapter countersink punching-shear demand", "input": f"{m5_couple_force_n:.2f} N / (pi x {END_HOLE_D:.2f} mm x {adapter_min_residual_mm:.3f} mm)", "result": f"{adapter_required_punching_shear_mpa:.4f} MPa demand; {kaiser_typical_shear_yield_mpa / adapter_required_punching_shear_mpa:.1f} ratio to Kaiser typical T651 shear-yield inference", "basis": "9.0 mm finished minimum and 3.1 mm max countersink; comparison uses typical 276 MPa yield from Kaiser Rev 05/06, not a minimum allowable", "status": "INDICATIVE STATIC SCREEN PASS; CERTIFICATE/PROOF OPEN"},
        {"screen": "LS-05", "item": "adapter countersunk-head annular average pressure", "input": f"{m5_couple_force_n:.2f} N / annulus({END_CSK_D_MIN:.2f} mm head min, {END_HOLE_D:.2f} mm hole)", "result": f"{adapter_head_average_pressure_mpa:.4f} MPa average pressure; {kaiser_typical_yield_mpa / adapter_head_average_pressure_mpa:.1f} ratio to Kaiser typical T651 yield", "basis": "average-pressure screen only; does not resolve conical contact, prying, local bending, preload, fatigue or impact", "status": "INDICATIVE STATIC SCREEN PASS; FEA/PROOF OPEN"},
    ]
    write_csv(OUT / "joint-load-screen.csv", load_rows)
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "disposition": "strengthened exact-coordinate architecture candidate; R55/P0.2 superseded; exact fastener candidates remain on hold; no part or assembly released",
        "vendor_source_sha256": {name: sha256(VENDOR / name) for name in ("XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp", "FR12-H104K.stp")},
        "vendor_8020_source_sha256": {name: sha256(VENDOR_8020 / name) for name in ("20-2040-endview.svg", "20-2040-dimensions.jpg", "20-2040-30mm.EPRT")},
        "candidate_geometry_mm": {
            "j1_to_j2_axis": round(J2_Y, 4),
            "j2_to_g1_frame_origin": round(G1_Y - J2_Y, 4),
            "j1_to_g1_frame_origin": round(G1_Y, 4),
            "adapter_thickness": PLATE_T,
            "adapter_finished_thickness_range": [PLATE_MIN_T, PLATE_MAX_T],
            "adapter_envelope": [48.0, PLATE_T, 40.0],
            "upper_beam_envelope": [20.0, UPPER_BEAM_L, 40.0],
            "forearm_beam_envelope": [20.0, FOREARM_BEAM_L, 40.0],
            "reserved_g1_to_object_center_max": round(360.0 - G1_Y, 4),
            "robotis_rectangular_pattern": {"x_centers": [-16.0, 16.0], "z_centers": [-8.0, 8.0], "hole_diameter": FRAME_HOLE_D},
            "profile_end_tap_centers": {"x": 0.0, "z_centers": [-10.0, 10.0], "core_diameter": 4.19},
            "m5_countersink": {"diameter": END_CSK_D, "depth": END_CSK_DEPTH, "included_angle_deg": 90.0},
        },
        "actuator_axis_registration": {
            "matrix_3x3": [[0, 0, -1], [1, 0, 0], [0, -1, 0]],
            "raw_output_axis": [0, 0, 1],
            "joint_output_axis": [-1, 0, 0],
            "raw_bottom_mount_axes": [[13.5, -41.5], [-13.5, -41.5]],
            "registered_s102_axes_yz": [[13.5, 41.5], [-13.5, 41.5]],
            "axial_translation_x_mm": ACTUATOR_AXIAL_OFFSET_X,
            "axial_translation_status": "candidate display placement; received horn/idler stack measurement required",
        },
        "axis_parallelism_math": {"j1_direction": [1, 0, 0], "j2_direction": [1, 0, 0], "dot_product": 1.0, "angular_difference_deg": 0.0},
        "reference_output_offset_deg": -90.0,
        "collision_screen": {"sampled_j2_range_deg": [15, 125], "increment_deg": COLLISION_INCREMENT_DEG, "sample_count": sample_count, "provisional_soft_limit_deg": PROVISIONAL_J2_SOFT_LIMIT_DEG, "first_nominal_collision_deg": first_nominal_collision_deg, "maximum_positive_intersection_mm3_full_requested_range": round(worst, 6), "maximum_positive_intersection_mm3_within_provisional_limit": round(max_intersection_within_limit, 6), "scope": "dense self-collision screen only; commanded range is not released; continuous between-sample and stopping-overtravel proof remain open"},
        "mass_and_load_screen": {
            "20_2040_mass_basis_kg_per_m": round(mass_per_m_kg, 6),
            "one_100mm_upper_beam_mass_g": round(upper_beam_mass_g, 3),
            "one_50mm_forearm_beam_mass_g": round(forearm_beam_mass_g, 3),
            "one_adapter_candidate_mass_g": round(plate_mass_g, 3),
            "upper_beam_plus_two_adapters_mass_g": round(upper_link_mass_g, 3),
            "forearm_beam_plus_two_adapters_mass_g": round(forearm_link_mass_g, 3),
            "allocated_shoulder_gravity_nm": round(shoulder_nm, 3),
            "allocated_elbow_gravity_nm": round(elbow_nm, 3),
            "screening_multiplier": 2.25,
            "shoulder_screen_nm": round(shoulder_screen_nm, 3),
            "elbow_screen_nm": round(elbow_nm * 2.25, 3),
            "status": "screen only; received masses, COM, inertia, continuous torque and thermal proof required",
        },
        "nominal_joint_screens": {
            "nearest_m5_countersink_to_m2_5_hole_clearance_mm": round(feature_clearance_mm, 4),
            "m5_thread_engagement_mm": round(m5_engagement_mm, 4),
            "m5_min_thread_engagement_screen_mm": round(m5_min_engagement_mm, 4),
            "m2_5_nominal_protrusion_mm": round(m2_5_nominal_protrusion_mm, 4),
            "m2_5_geometric_min_protrusion_screen_mm": round(m2_5_screen_min_protrusion_mm, 4),
            "m5_couple_force_n": round(m5_couple_force_n, 2),
            "inferred_internal_thread_shear_capacity_n": round(thread_shear_capacity_n, 1),
            "20_2040_strong_axis_bending_stress_mpa": round(beam_bending_stress_mpa, 4),
            "adapter_min_residual_below_countersink_mm": round(adapter_min_residual_mm, 4),
            "adapter_punching_shear_demand_mpa": round(adapter_required_punching_shear_mpa, 4),
            "adapter_head_annular_average_pressure_mpa": round(adapter_head_average_pressure_mpa, 4),
            "status": "indicative static screening only; typical material properties are not allowables and no fatigue, preload, local bending, tolerance or physical proof credit is taken",
        },
        "candidate_primary_sources": {
            "adapter_material_typical_properties": "Kaiser Aluminum Sheet Coil & Plate Alloy 6061, Rev. 05/06; typical T6/T651 yield 276 MPa; not a minimum allowable",
            "m5_countersunk_screw": "Westfield Fasteners WF2563, live product page accessed 2026-08-07",
            "m2_5_socket_screw": "Westfield Fasteners WF2339, live product page accessed 2026-08-07",
            "m2_5_hex_nut": "Westfield Fasteners WF1254 and DIN 934 guide, live pages accessed 2026-08-07",
        },
        "open_release_items": [
            "supplier confirmation and received inspection for 20-2040 two-hole M5 end-tap service",
            "adapter 6061-T651 minimum properties/certificate, 9.0 to 10.0 mm finished thickness, countersink tolerances, manufacturing process and first article",
            "received WF2339/WF1254 stack, screw-length tolerance, torque, anti-galling/locking, wrench envelope and proof",
            "received WF2563 full-thread confirmation, torque, anti-galling/locking method, countersink inspection and physical proof",
            "received horn/idler axial stack and complete actuator/frame assembly fit",
            "tool access, cable routing, connector sweep and strain relief",
            "continuous between-sample joint-space collision proof including base, guard, stops and gripper",
            "J2 hard-stop/soft-limit allocation and measured stopping overtravel below the current nominal first-collision pose",
            "adapter conical contact/local bending FEA or accepted equivalent plus joint-slip, preload, fatigue, impact and proof analyses",
            "received-part fit, first-article inspection and qualified mechanical approval",
        ],
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    first_collision_label = f"{first_nominal_collision_deg:.1f} deg" if first_nominal_collision_deg is not None else "none in sampled range"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="920" viewBox="0 0 1500 920">
<style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:700}}.sub{{font-size:23px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#8a3b00}}.axis{{stroke:#0b4f8a;stroke-width:4}}.part{{fill:#66c7f4;stroke:#0b4f8a;stroke-width:3}}.frame{{fill:#f3b61f;stroke:#8a5a00;stroke-width:3}}.note{{fill:#fff4cd;stroke:#f3b61f;stroke-width:3}}</style>
<rect width="1500" height="920" fill="#f7fbff"/>
<text x="40" y="55" class="title">HR-V0 strengthened exact-coordinate arm candidate</text>
<text x="40" y="92" class="warn">{REVISION} - {WARNING}</text>
<text x="40" y="145" class="sub">Straight reference pose, side elevation (Y horizontal, Z vertical)</text>
<line x1="150" y1="370" x2="1330" y2="370" stroke="#b7cad9" stroke-width="2"/>
<circle cx="190" cy="370" r="18" fill="#0b4f8a"/><text x="155" y="420">J1 Y=0</text>
<rect x="220" y="330" width="54" height="80" class="frame"/>
<rect x="274" y="330" width="400" height="80" class="part"/><text x="300" y="315">100 mm 20-2040 vertical envelope + two 9.525 mm adapters</text>
<circle cx="714" cy="370" r="18" fill="#0b4f8a"/><text x="635" y="440">J2 Y={J2_Y:.4f}</text>
<rect x="744" y="330" width="54" height="80" class="frame"/>
<rect x="798" y="330" width="250" height="80" class="part"/><text x="840" y="315">50 mm vertical forearm member</text>
<rect x="1048" y="330" width="54" height="80" class="frame"/><text x="980" y="440">G1 Y={G1_Y:.4f}</text>
<line x1="190" y1="480" x2="714" y2="480" class="axis"/><text x="350" y="512">J1-J2 = {J2_Y:.4f} mm candidate</text>
<line x1="714" y1="550" x2="1102" y2="550" class="axis"/><text x="800" y="582">J2-G1 = {G1_Y-J2_Y:.4f} mm candidate</text>
<rect x="70" y="640" width="1360" height="210" rx="14" class="note"/>
<text x="100" y="690" class="sub">What this fixes</text>
<text x="100" y="730">P0.2 is superseded: nominal adapter thickness is 9.525 mm with a 9.0 mm finished minimum.</text>
<text x="100" y="766">Exact candidates: WF2563 M5 x 20, WF2339 M2.5 x 16 and WF1254 M2.5 nut. No torque is released.</text>
<text x="100" y="802">G1 leaves {360.0-G1_Y:.4f} mm. Provisional J2 ceiling is {PROVISIONAL_J2_SOFT_LIMIT_DEG:.1f} deg; first nominal collision: {first_collision_label}.</text>
<text x="100" y="838" class="warn">Stopping overtravel, material allowables, local FEA, cables and physical proof remain open. Do not fabricate.</text>
</svg>'''
    (OUT / "HR-V0_arm_architecture_candidate.svg").write_text(svg, encoding="utf-8", newline="\n")

    print(f"Generated {REVISION}: J1-J2 {J2_Y:.4f} mm; J2-G1 {G1_Y-J2_Y:.4f} mm; {sample_count} collision samples; max {worst:.6f} mm3")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
