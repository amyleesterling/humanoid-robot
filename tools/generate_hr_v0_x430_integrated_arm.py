"""Generate the full HR-V0 P0.9 X430 integrated-arm comparison.

The package joins the controlled P0.7 shoulder/column geometry to the corrected
P0.8 X430/FR12 elbow coordinates.  It is review evidence only: it does not
select XM430, supersede P0.7, or authorize external work or energization.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as p07  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as p08  # noqa: E402


REVISION = "HR-V0-ARM-ARCH-P0.9-X430-INTEGRATED-CANDIDATE"
WARNING = (
    "PRELIMINARY - COMPARISON CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, "
    "PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.9-x430"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
VENDOR_X430 = VENDOR / "x430-fr12-r91"

J2_Y = p08.J2_Y
G1_Y = J2_Y + p08.G1_LOCAL_Y
OBJECT_CENTER_Y = p08.OBJECT_CENTER_Y
Q1_LO = -20.0
Q1_HI = 70.0
Q2_LO = 15.0
SOFT_LIMIT = 115.0
STOP_TARGET = 118.0
SAMPLE_INCREMENT = 1.0
CONTINUOUS_REQUIRED_MM = 0.75


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def first_contact(fixed: cq.Shape, moving: cq.Shape, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if fixed.distance(p07.rotate_x(moving, mid, J2_Y)) > 1e-7:
            lo = mid
        else:
            hi = mid
    return hi


def colour(name: str) -> cq.Color:
    if "COLUMN" in name:
        return cq.Color(0.40, 0.46, 0.52)
    if "SUPPORT" in name:
        return cq.Color(0.78, 0.82, 0.86)
    if "X430" in name or "XM540" in name:
        return cq.Color(0.05, 0.25, 0.50)
    if "H101" in name or "H104" in name:
        return cq.Color(0.96, 0.70, 0.12)
    if "S102" in name:
        return cq.Color(0.40, 0.78, 0.96)
    if "CATCH" in name:
        return cq.Color(0.72, 0.16, 0.12)
    if "STRIKER" in name:
        return cq.Color(0.95, 0.42, 0.10)
    return cq.Color(0.62, 0.68, 0.74)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "parts").mkdir(parents=True)

    xm540 = p07.import_step("XMHD-540.N101.I101.STP")
    fr13_h101 = p07.import_step("FR13-H101K.stp")
    fr13_s102 = p07.import_step("FR13-S102K.stp")
    h104 = p07.import_step("FR12-H104K.stp")
    x430_raw = cq.importers.importStep(str(VENDOR_X430 / "x-430_idle.stp")).val()
    fr12_h101 = cq.importers.importStep(str(VENDOR_X430 / "fr12_h101.stp")).val()
    fr12_s102_raw = cq.importers.importStep(str(VENDOR_X430 / "fr12_s102.stp")).val()

    # Exact controlled-source checks prevent a silent datum substitution.
    if not {(-11.0, -32.0), (11.0, -32.0)} <= p08.exact_axes(x430_raw, "Z", 1.25):
        raise RuntimeError("controlled X430 STEP lost selected rear axes")
    if not {(-11.0, 11.0), (11.0, 11.0)} <= p08.exact_axes(fr12_s102_raw, "X", 1.3):
        raise RuntimeError("controlled FR12-S102 STEP lost selected side axes")
    if not {(-12.0, -6.0), (-12.0, 6.0), (12.0, -6.0), (12.0, 6.0)} <= p08.exact_axes(fr12_h101, "Y", 1.3):
        raise RuntimeError("controlled FR12-H101 STEP lost selected link axes")

    # P0.7 J1/column are retained without selecting their unresolved hardware.
    j1_joint = p07.actuator_to_joint_frame(xm540)
    column = p07.column_envelope()
    support = p07.shoulder_support_plate()
    j1_body = p07.rotate_x(j1_joint, 90.0)
    j1_s102 = p07.rotate_x(fr13_s102, 90.0)
    j1_h101 = fr13_h101
    upper_prox = p07.adapter(32.0)
    upper_beam = p07.beam(32.0 + p07.PLATE_T, p07.UPPER_BEAM_L)

    # Corrected P0.8 J2 package and positive-stop adapters, located in the
    # complete arm rather than assessed as an isolated elbow subassembly.
    fixed_catch_y = J2_Y - p08.S102_FIXED_FACE - p08.PLATE_T
    j2_x430 = p07.rotate_x(p08.x430_to_joint_frame(x430_raw), 90.0).translate((0.0, J2_Y, 0.0))
    j2_s102 = p07.rotate_x(
        fr12_s102_raw.translate((0.0, 0.0, p08.S102_LOCAL_Z_SHIFT)), 90.0
    ).translate((0.0, J2_Y, 0.0))
    fixed_catch = p08.stop_adapter(fixed_catch_y, p08.STOP_FIXED_WING_Z)
    j2_h101 = fr12_h101.translate((0.0, J2_Y, 0.0))
    moving_striker_y = J2_Y + p08.J2_H101_FACE
    moving_striker = p08.stop_adapter(moving_striker_y, p08.STOP_MOVING_WING_Z)
    fore_beam = p07.beam(moving_striker_y + p08.PLATE_T, p08.FOREARM_BEAM_L)
    distal = p07.gripper_adapter(moving_striker_y + p08.PLATE_T + p08.FOREARM_BEAM_L)
    gripper_frame = p07.rotate_x(h104, 180.0).translate((0.0, G1_Y, 0.0))

    fixed_base = {
        "COLUMN": column,
        "SHOULDER_SUPPORT": support,
        "J1_BODY": j1_body,
        "J1_S102": j1_s102,
    }
    upper_zero = {
        "J1_H101": j1_h101,
        "UPPER_PROX_ADAPTER": upper_prox,
        "UPPER_MEMBER": upper_beam,
        "P09_FIXED_CATCH": fixed_catch,
        "J2_X430": j2_x430,
        "J2_FR12_S102": j2_s102,
    }
    moving_zero = {
        "J2_FR12_H101": j2_h101,
        "P09_MOVING_STRIKER": moving_striker,
        "FORE_MEMBER": fore_beam,
        "FORE_DIST_H104_ADAPTER": distal,
        "G1_H104": gripper_frame,
    }
    components = {**fixed_base, **upper_zero, **moving_zero}
    intentional_j1 = {("J1_BODY", "J1_H101"), ("J1_S102", "J1_H101")}
    intentional_j2 = {
        ("J2_X430", "J2_FR12_H101"),
        ("J2_FR12_S102", "J2_FR12_H101"),
    }
    intentional_stop = {("P09_FIXED_CATCH", "P09_MOVING_STRIKER")}

    assembly = cq.Assembly(name="HR_V0_P09_X430_INTEGRATED_CANDIDATE_NOT_RELEASED")
    for name, shape in components.items():
        assembly.add(shape, name=name, color=colour(name))
    step_path = OUT / "HR-V0_arm_P0.9_X430_integrated_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step_path))
    p07.canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_arm_P0.9_X430_integrated_candidate.glb"))

    for name, shape in {
        "P09-C01_X430_fixed-catch-adapter": fixed_catch.translate((0.0, -fixed_catch_y, 0.0)),
        "P09-C02_X430_moving-striker-adapter": moving_striker.translate((0.0, -moving_striker_y, 0.0)),
    }.items():
        path = OUT / "parts" / f"{name}.step"
        cq.exporters.export(shape, str(path))
        p07.canonicalize_step(path)
    p08.drawing_svg(OUT / "P09-C01_fixed-catch-review-drawing.svg", "P09-C01", p08.STOP_FIXED_WING_Z, "fixed catch")
    p08.drawing_svg(OUT / "P09-C02_moving-striker-review-drawing.svg", "P09-C02", p08.STOP_MOVING_WING_Z, "moving striker")

    # Full two-axis nominal sampling.  Continuous separation through the soft
    # limit is certified separately below; this table is visualization/audit
    # evidence and is never used as between-sample proof.
    q1_values = [Q1_LO + i * SAMPLE_INCREMENT for i in range(int((Q1_HI - Q1_LO) / SAMPLE_INCREMENT) + 1)]
    q2_values = [Q2_LO + i * SAMPLE_INCREMENT for i in range(int((STOP_TARGET - Q2_LO) / SAMPLE_INCREMENT) + 1)]
    fixed_bounds = {name: p07.bbox_tuple(shape) for name, shape in fixed_base.items()}
    base_upper: dict[float, tuple[float, list[str]]] = {}
    for q1 in q1_values:
        moved_upper = {name: p07.rotate_x(shape, q1) for name, shape in upper_zero.items()}
        total = 0.0
        pairs: list[str] = []
        for f_name, f_shape in fixed_base.items():
            for u_name, u_shape in moved_upper.items():
                if (f_name, u_name) in intentional_j1 or not p07.boxes_overlap(f_shape, u_shape):
                    continue
                value = p07.positive_intersection(f_shape, u_shape)
                total += value
                if value > 1e-5:
                    pairs.append(f"{f_name}:{u_name}={value:.6f}")
        base_upper[q1] = (total, pairs)

    upper_fore: dict[float, tuple[float, list[str]]] = {}
    for q2 in q2_values:
        moved_fore = {name: p07.rotate_x(shape, q2, J2_Y) for name, shape in moving_zero.items()}
        total = 0.0
        pairs: list[str] = []
        for u_name, u_shape in upper_zero.items():
            for m_name, m_shape in moved_fore.items():
                if (u_name, m_name) in intentional_j2 | intentional_stop or not p07.boxes_overlap(u_shape, m_shape):
                    continue
                value = p07.positive_intersection(u_shape, m_shape)
                total += value
                if value > 1e-5:
                    pairs.append(f"{u_name}:{m_name}={value:.6f}")
        upper_fore[q2] = (total, pairs)

    sweep_rows: list[dict[str, object]] = []
    max_soft = 0.0
    for q2 in q2_values:
        relative = {name: p07.rotate_x(shape, q2, J2_Y) for name, shape in moving_zero.items()}
        relative_bounds = {name: p07.bbox_tuple(shape) for name, shape in relative.items()}
        for q1 in q1_values:
            total = base_upper[q1][0] + upper_fore[q2][0]
            pairs = list(base_upper[q1][1]) + list(upper_fore[q2][1])
            for f_name, f_shape in fixed_base.items():
                for m_name, m_shape in relative.items():
                    if not p07.bbox_values_overlap(fixed_bounds[f_name], p07.rotate_bbox_x(relative_bounds[m_name], q1)):
                        continue
                    value = p07.positive_intersection(f_shape, p07.rotate_x(m_shape, q1))
                    total += value
                    if value > 1e-5:
                        pairs.append(f"{f_name}:{m_name}={value:.6f}")
            if q2 <= SOFT_LIMIT:
                max_soft = max(max_soft, total)
            sweep_rows.append(
                {
                    "j1_deg": f"{q1:.1f}",
                    "j2_deg": f"{q2:.1f}",
                    "nonintentional_intersection_mm3": f"{total:.9f}",
                    "colliding_pairs": ";".join(pairs),
                    "classification": "SOFT_LIMIT" if q2 == SOFT_LIMIT else ("STOP_TARGET" if q2 == STOP_TARGET else "SAMPLED_POSE"),
                    "status": "NOMINAL SAMPLE ONLY - CONTINUOUS PROOF IS SEPARATE; CABLE/GUARD/TOLERANCE/DEFORMATION OPEN",
                }
            )
    write_csv(OUT / "full-arm-collision-sweep.csv", sweep_rows)

    # Adaptive interval certificate for every nonintentional solid pair over
    # the full commanded domain through the 115-degree software limit.
    old_j2 = p07.J2_Y
    p07.J2_Y = J2_Y
    try:
        summary_rows: list[dict[str, object]] = []
        cell_rows: list[dict[str, object]] = []
        for f_name, f_shape in fixed_base.items():
            for u_name, u_shape in upper_zero.items():
                if (f_name, u_name) in intentional_j1:
                    continue
                summary, cells = p07.certify_continuous_1d(
                    pair_id=f"BASE_UPPER:{f_name}:{u_name}", fixed_shape=f_shape,
                    moving_shape=u_shape, rotation_origin_y=0.0,
                    q_lo=Q1_LO, q_hi=Q1_HI, coordinate="J1",
                )
                summary_rows.append(summary); cell_rows.extend(cells)
        for u_name, u_shape in upper_zero.items():
            for m_name, m_shape in moving_zero.items():
                if (u_name, m_name) in intentional_j2 | intentional_stop:
                    continue
                summary, cells = p07.certify_continuous_1d(
                    pair_id=f"UPPER_FORE:{u_name}:{m_name}", fixed_shape=u_shape,
                    moving_shape=m_shape, rotation_origin_y=J2_Y,
                    q_lo=Q2_LO, q_hi=SOFT_LIMIT, coordinate="J2",
                )
                summary_rows.append(summary); cell_rows.extend(cells)
        for f_name, f_shape in fixed_base.items():
            for m_name, m_shape in moving_zero.items():
                summary, cells = p07.certify_continuous_2d(
                    pair_id=f"BASE_FORE:{f_name}:{m_name}", fixed_shape=f_shape,
                    moving_shape=m_shape, q1_lo=Q1_LO, q1_hi=Q1_HI,
                    q2_lo=Q2_LO, q2_hi=SOFT_LIMIT,
                )
                summary_rows.append(summary); cell_rows.extend(cells)
    finally:
        p07.J2_Y = old_j2
    write_csv(OUT / "continuous-clearance-summary.csv", summary_rows)
    write_csv(OUT / "continuous-clearance-cells.csv", cell_rows)
    min_continuous = min(float(row["minimum_guaranteed_clearance_mm"]) for row in summary_rows)

    contact = first_contact(fixed_catch, moving_striker, 116.0, 120.0)
    stop_rows: list[dict[str, object]] = []
    for i in range(61):
        q2 = SOFT_LIMIT + i * 0.05
        moved = p07.rotate_x(moving_striker, q2, J2_Y)
        stop_rows.append({
            "j2_deg": f"{q2:.2f}",
            "metal_clearance_mm": f"{fixed_catch.distance(moved):.9f}",
            "metal_intersection_mm3": f"{fixed_catch.intersect(moved).Volume():.9f}",
            "classification": "SOFT_LIMIT" if i == 0 else ("STOP_TARGET" if i == 60 else "APPROACH"),
            "status": "NOMINAL CAD ONLY - BUMPER/TOLERANCE/LOAD/STOPPING/REBOUND/PHYSICAL PROOF OPEN",
        })
    write_csv(OUT / "hard-stop-sweep.csv", stop_rows)

    transform_rows = [
        {"item": "J1/column package", "parent": "J1", "transform": "identical to controlled P0.7", "evidence": "P0.7 exact-coordinate source", "state": "CARRIED FOR COMPARISON; P0.7 HARDWARE HOLDS REMAIN"},
        {"item": "X430 actuator", "parent": "J2", "transform": f"raw +Z to joint -X; Tx=2.35; package Rx=90; Ty={J2_Y:.3f}", "evidence": "rear case axes local Z X=+/-11,Y=-32", "state": "EXACT MODEL; RECEIVED FIT OPEN"},
        {"item": "FR12-S102", "parent": "J2", "transform": f"local Tz=21; package Rx=90; Ty={J2_Y:.3f}", "evidence": "side axes local X Y=+/-11,Z=11 register at Z=32", "state": "EXACT MODEL; RECEIVED FIT OPEN"},
        {"item": "FR12-H101", "parent": "J2 moving", "transform": f"identity straight reference; Ty={J2_Y:.3f}; rotate about J2 +X", "evidence": "outside face 28 mm; link axes X=+/-12,Z=+/-6", "state": "EXACT MODEL; RECEIVED FIT OPEN"},
        {"item": "G1 H104", "parent": "J2 moving", "transform": f"Rx=180; straight-reference Ty={G1_Y:.3f}", "evidence": "P0.7 exact selected H104 axes", "state": "EXACT MODEL; GRIPPER DATUM/RECEIVED FIT OPEN"},
    ]
    write_csv(OUT / "transform-schedule.csv", transform_rows)

    interface_rows = [
        {"interface": "P09-A00..A03", "from": "P0.7 column/J1/upper proximal interfaces", "to": "upper 20-2040 distal face", "coordinates": "unchanged through Y=141.525", "fastener_state": "P0.7 exact candidates remain HOLD", "status": "NOT REQUALIFIED; RECEIVED/FAI/PRELOAD/PROOF OPEN"},
        {"interface": "P09-A04", "from": "upper 20-2040", "to": "P09-C01 and FR12-S102", "coordinates": "beam X=0,Z=+/-10; frame X=+/-12,Z=+/-6; fixed face Y=151.050", "fastener_state": "M5 beam and M2.5 frame stacks SELECTION REQUIRED", "status": "NOMINAL AXES REGISTERED; ACCESS/ENGAGEMENT/BOTTOMING/PROOF OPEN"},
        {"interface": "P09-A05", "from": "FR12-H101", "to": "P09-C02 and forearm 20-2040", "coordinates": "frame X=+/-12,Z=+/-6; beam X=0,Z=+/-10; moving face Y=219.550", "fastener_state": "M2.5 through/nut and M5 beam stacks SELECTION REQUIRED", "status": "NOMINAL AXES REGISTERED; ACCESS/ENGAGEMENT/PRELOAD/PROOF OPEN"},
        {"interface": "P09-A06..A07", "from": "forearm beam/distal adapter", "to": "H104/gripper datum", "coordinates": f"H104 origin Y={G1_Y:.3f}; object screen Y={OBJECT_CENTER_Y:.3f}", "fastener_state": "P0.7 candidates remain HOLD", "status": "GRIPPER MECHANISM/DATUM/MASS/PROOF OPEN"},
        {"interface": "P09-HS-J2", "from": "P09-C02 integral wings", "to": "P09-C01 integral wings", "coordinates": f"nominal first metal contact {contact:.6f} deg", "fastener_state": "bumper material/order/retention SELECTION REQUIRED", "status": "NOMINAL CAD; TOLERANCE/LOAD/STOPPING/PHYSICAL PROOF OPEN"},
    ]
    write_csv(OUT / "interface-schedule.csv", interface_rows)

    fastener_rows = [
        {"stack_id": "P09-FS-01", "interface": "FR12-S102 to P09-C01", "nominal_stack_mm": "frame tapped interface plus adapter face; exact usable thread depth unknown", "requirements": "M2.5; no bottoming; manufacturer-approved engagement; head clears X430/frame; removable with installed beam", "candidate": "SELECTION REQUIRED", "evidence_to_close": "received section/threads, official torque, tolerance stack, access trial, preload/slip/proof review", "state": "OPEN"},
        {"stack_id": "P09-FS-02", "interface": "FR12-H101 to P09-C02", "nominal_stack_mm": "H101 sheet plus 9.525 nominal adapter plus nut if through-bolted", "requirements": "M2.5; full nut engagement; no moving-envelope projection; tool access; retained against loosening", "candidate": "SELECTION REQUIRED", "evidence_to_close": "received sheet thickness, nut/screw dimensions, tolerance stack, access trial, preload/slip/proof review", "state": "OPEN"},
        {"stack_id": "P09-FS-03", "interface": "20-2040 ends to P09-C01/C02", "nominal_stack_mm": "9.525 adapter with countersink to M5 end tap", "requirements": "M5; flush head below frame envelope; adequate thread engagement; no bottoming; edge distance retained", "candidate": "SELECTION REQUIRED", "evidence_to_close": "received profile tap depth, countersink FAI, screw drawing, torque, preload/slip/proof review", "state": "OPEN"},
        {"stack_id": "P09-FS-04", "interface": "X430 to FR12-S102 and FR12-H101", "nominal_stack_mm": "manufacturer frame/actuator stack", "requirements": "exact official accessory compatibility and received hardware; horn/idler seating; no cable pinch", "candidate": "SELECTION REQUIRED", "evidence_to_close": "official kit BOM/revision, received inspection, assembly trial, axial play/runout measurement", "state": "OPEN"},
    ]
    write_csv(OUT / "fastener-stack-requirements.csv", fastener_rows)

    tolerance_rows = [
        {"control_id": "P09-TOL-01", "feature": "adapter finished thickness", "nominal": "9.525 mm", "allowed": "SELECTION REQUIRED", "effect": "fastener length, stop angle, frame seating", "evidence": "DFM plus calibrated FAI at defined points", "state": "OPEN"},
        {"control_id": "P09-TOL-02", "feature": "FR12 frame hole/thread true position", "nominal": "official nominal axes", "allowed": "SELECTION REQUIRED", "effect": "assembly stress, joint registration", "evidence": "received metrology and manufacturer tolerance disposition", "state": "OPEN"},
        {"control_id": "P09-TOL-03", "feature": "C01/C02 stop-wing profile and relative clocking", "nominal": f"metal contact {contact:.6f} deg", "allowed": "SELECTION REQUIRED", "effect": "soft-to-stop margin, impact/rebound", "evidence": "worst-case stack, FAI, as-built contact-angle measurement", "state": "OPEN"},
        {"control_id": "P09-TOL-04", "feature": "joint stack axial offset/runout/play", "nominal": "model Tx=2.35 mm", "allowed": "SELECTION REQUIRED", "effect": "frame clearance, cable path, stop load", "evidence": "received assembly metrology under HR-V0-JOINT-MET-P0.1", "state": "OPEN"},
        {"control_id": "P09-TOL-05", "feature": "cable/connector/guard swept envelope", "nominal": "not modeled", "allowed": "SELECTION REQUIRED", "effect": "collision and pinch protection", "evidence": "released harness/guard CAD plus tolerance/deformation sweep and physical trial", "state": "OPEN"},
    ]
    write_csv(OUT / "tolerance-control-register.csv", tolerance_rows)

    density = 2.70 / 1000.0
    catch_mass = fixed_catch.Volume() * density
    striker_mass = moving_striker.Volume() * density
    p09_incomplete = 692.758 - 165.0 - 66.870 - 70.265 + 82.0 + catch_mass + striker_mass
    headroom = 750.0 - p09_incomplete
    beam_mass_per_m_kg = 0.0428 * 0.45359237 / 0.0254
    fore_beam_mass = beam_mass_per_m_kg * (p08.FOREARM_BEAM_L / 1000.0) * 1000.0
    distal_mass = distal.Volume() * density
    fore_subtotal = striker_mass + fore_beam_mass + distal_mass
    fore_com = (
        striker_mass * (p08.J2_H101_FACE + p08.PLATE_T / 2.0)
        + fore_beam_mass * (p08.J2_H101_FACE + p08.PLATE_T + p08.FOREARM_BEAM_L / 2.0)
        + distal_mass * (p08.J2_H101_FACE + p08.PLATE_T + p08.FOREARM_BEAM_L + p08.PLATE_T / 2.0)
    ) / fore_subtotal
    elbow_gravity = 9.80665 * (
        fore_subtotal / 1000.0 * fore_com / 1000.0
        + 0.21 * p08.G1_LOCAL_Y / 1000.0
        + 0.10 * (OBJECT_CENTER_Y - J2_Y) / 1000.0
    )
    elbow_screen = elbow_gravity * 2.25
    write_csv(OUT / "mass-load-screen.csv", [{
        "configuration": REVISION,
        "incomplete_known_mass_g": f"{p09_incomplete:.3f}",
        "provisional_headroom_g": f"{headroom:.3f}",
        "elbow_gravity_nm": f"{elbow_gravity:.3f}",
        "elbow_2_25_screen_nm": f"{elbow_screen:.3f}",
        "xm430_12v_stall_endpoint_ratio_only": f"{4.1 / elbow_screen:.3f}",
        "missing": "received frames; exact fasteners; bumper; gripper mechanism; connectors; strain relief; moving harness; measured COM/inertia",
        "status": "INCOMPLETE SCREEN - NOT MASS, CONTINUOUS-TORQUE, THERMAL, OR STRUCTURAL CLOSURE",
    }])

    holds = list(csv.DictReader((OUT.parent / "elbow-architecture-p0.8" / "architecture-holds.csv").open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "ELBH-002":
            row["release_effect"] += "; P0.9 full-arm nominal integration now exists"
        if row["hold_id"] == "ELBH-008":
            row["release_effect"] += "; P0.9 continuously certifies nominal solids only through the software limit"
        if row["hold_id"] == "ELBH-009":
            row["state"] = "PARTIAL"
            row["release_effect"] += "; P0.9 defines explicit fastener/tolerance closure evidence but no stack is selected or proved"
    write_csv(OUT / "architecture-holds.csv", holds)

    continuous_analysis = {
        "revision": REVISION,
        "method": "adaptive interval cover using exact/AABB center distance minus rigid-body chord bounds",
        "joint_domain_deg": {"j1": [Q1_LO, Q1_HI], "j2": [Q2_LO, SOFT_LIMIT]},
        "required_certified_clearance_mm": CONTINUOUS_REQUIRED_MM,
        "minimum_guaranteed_clearance_mm": round(min_continuous, 6),
        "pair_count": len(summary_rows),
        "leaf_cell_count": len(cell_rows),
        "exact_brep_distance_calls": sum(int(row["exact_brep_distance_calls"]) for row in summary_rows),
        "excluded_intentional_interfaces": sorted(f"{a}:{b}" for a, b in intentional_j1 | intentional_j2 | intentional_stop),
        "release_boundary": "nominal solids through software limit only; tolerances, cables, connectors, guards, deformation and stopping travel excluded",
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE_NOT_A_PHYSICAL_OR_MOTION_RELEASE",
    }
    (OUT / "continuous-clearance-analysis.json").write_text(json.dumps(continuous_analysis, indent=2) + "\n", encoding="utf-8", newline="\n")

    flags = {
        "supersedes_p0_7": False, "xm430_selected": False,
        "quotation_authorized": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False,
        "motion_authorized": False, "connection_authorized": False,
        "energization_authorized": False,
    }
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "configuration_disposition": "P0.9 integrated comparison only; P0.7 remains controlled and XM430 is not selected",
        "geometry_mm": {"j1_to_j2": J2_Y, "j2_to_g1": p08.G1_LOCAL_Y, "object_center_from_j1": OBJECT_CENTER_Y},
        "sampled_collision": {"increment_deg": SAMPLE_INCREMENT, "pose_count": len(sweep_rows), "maximum_nonintentional_intersection_through_soft_limit_mm3": round(max_soft, 9)},
        "continuous_clearance": continuous_analysis,
        "positive_stop": {"soft_limit_deg": SOFT_LIMIT, "nominal_first_metal_contact_deg": round(contact, 6), "status": "nominal CAD only; physical stack and stopping evidence open"},
        "mass_load": {"incomplete_known_mass_g": round(p09_incomplete, 3), "provisional_headroom_g": round(headroom, 3), "elbow_2_25_screen_nm": round(elbow_screen, 3), "xm430_stall_endpoint_ratio_only": round(4.1 / elbow_screen, 3)},
        "hold_counts": {"open": sum(r["state"] == "OPEN" for r in holds), "partial": sum(r["state"] == "PARTIAL" for r in holds)},
        "release_flags": flags,
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "package-status.json").write_text(json.dumps({"revision": REVISION, "state": "COMPARISON_CANDIDATE_NOT_SELECTED", "warning": WARNING, "release_flags": flags}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
