"""Generate the P1.1 X430 lowered-forearm comparison candidate.

The forearm member pattern is shifted 7 mm downward while the FR12 frame
pattern, elbow axis, and external 118 degree stop surfaces remain fixed.  The
package is review evidence only and grants no work or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
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
import generate_hr_v0_x430_integrated_arm as p09  # noqa: E402
import generate_hr_v0_x430_clearance_arm as p10  # noqa: E402


REVISION = "HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE"
WARNING = (
    "PRELIMINARY - COMPARISON CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, "
    "PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p1.1-x430-lowered-forearm"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
VENDOR_X430 = VENDOR / "x430-fr12-r91"

J2_Y = p08.J2_Y
MOVING_FACE_Y = J2_Y + p08.J2_H101_FACE
G1_Y = J2_Y + p08.G1_LOCAL_Y
Q1_LO = -20.0
Q1_HI = 70.0
Q2_LO = 15.0
SOFT_LIMIT = 115.0
STOP_TARGET = 118.0
FOREARM_Z_OFFSET = -7.0
PLATE_Z_MIN = -27.0
PLATE_Z_MAX = 13.0
MEMBER_HOLE_Z = (3.0, -17.0)
LOBE_TOP_Z = p08.STOP_MOVING_WING_Z + 6.0
BASE_REQUIRED_CLEARANCE_MM = 0.75
CRITICAL_REQUIRED_CLEARANCE_MM = 4.75
PHYSICAL_RESIDUAL_REQUIREMENT_MM = 1.5
TOLERANCE_ALLOCATIONS_MM = {
    "part_profile_thickness": 0.25,
    "frame_actuator_registration_runout": 0.50,
    "joint_play_and_calibration": 0.50,
    "fastener_projection": 0.25,
    "stop_deformation_and_bumper": 0.75,
    "measurement_uncertainty": 0.25,
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cut_lowered_features(shape: cq.Shape, y0: float) -> cq.Shape:
    """Cut the fixed FR12 pattern and the 7 mm lowered 20-2040 pattern."""

    for x in (-12.0, 12.0):
        for z in (-6.0, 6.0):
            shape = shape.cut(
                cq.Solid.makeCylinder(
                    p08.FRAME_HOLE_D / 2.0,
                    p08.PLATE_T,
                    cq.Vector(x, y0, z),
                    cq.Vector(0.0, 1.0, 0.0),
                )
            )
    for z in MEMBER_HOLE_Z:
        shape = shape.cut(
            cq.Solid.makeCylinder(
                p08.END_HOLE_D / 2.0,
                p08.PLATE_T,
                cq.Vector(0.0, y0, z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        )
        shape = shape.cut(
            cq.Solid.makeCone(
                p07.END_CSK_D / 2.0,
                p08.END_HOLE_D / 2.0,
                p07.END_CSK_DEPTH,
                cq.Vector(0.0, y0, z),
                cq.Vector(0.0, 1.0, 0.0),
            )
        )
    return shape


def lowered_striker(y0: float) -> cq.Shape:
    """2.5-D adapter with a lowered member pattern and unchanged stop lobes."""

    base = cq.Solid.makeBox(
        48.0,
        p08.PLATE_T,
        PLATE_Z_MAX - PLATE_Z_MIN,
        cq.Vector(-24.0, y0, PLATE_Z_MIN),
    )
    lobe_height = LOBE_TOP_Z - PLATE_Z_MAX
    right = cq.Solid.makeBox(17.0, p08.PLATE_T, lobe_height, cq.Vector(24.0, y0, PLATE_Z_MAX))
    left = cq.Solid.makeBox(17.0, p08.PLATE_T, lobe_height, cq.Vector(-41.0, y0, PLATE_Z_MAX))
    return cut_lowered_features(base.fuse(right).fuse(left), y0)


def first_contact(fixed: cq.Shape, moving: cq.Shape, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if fixed.distance(p07.rotate_x(moving, mid, J2_Y)) > 1e-7:
            lo = mid
        else:
            hi = mid
    return hi


def profile_drawing(path: Path, stop_clearance: float, allocated: float, available: float) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1000" viewBox="0 0 1500 1000">
<style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:18px}}.h{{font-size:34px;font-weight:700;fill:#082b55}}.s{{font-size:24px;font-weight:700}}.w{{font-weight:700;fill:#9b1c1c}}.p{{stroke:#082b55;stroke-width:3;fill:#dff3ff}}.d{{stroke:#d59600;stroke-width:3;fill:none}}.box{{fill:#fff9e8;stroke:#d59600;stroke-width:3}}</style>
<rect width="1500" height="1000" fill="#f7fbff"/><text x="45" y="60" class="h">P11-C02 lowered-forearm moving-striker candidate</text>
<text x="45" y="98" class="w">{WARNING}</text>
<path d="M250 680 L250 360 L730 360 L730 680 Z M80 240 L250 240 L250 360 L80 360 Z M730 240 L900 240 L900 360 L730 360 Z" class="p"/>
<circle cx="490" cy="520" r="14" class="d"/><circle cx="610" cy="520" r="14" class="d"/><circle cx="490" cy="640" r="14" class="d"/><circle cx="610" cy="640" r="14" class="d"/>
<circle cx="550" cy="500" r="29" class="d"/><circle cx="550" cy="700" r="29" class="d"/>
<text x="970" y="210" class="s">Controlled nominal geometry</text>
<text x="970" y="255">Base: X = -24..+24; Z = {PLATE_Z_MIN:.0f}..+{PLATE_Z_MAX:.0f} mm</text><text x="970" y="292">Thickness: 9.525 mm nominal</text>
<text x="970" y="329">FR12 axes: X = +/-12; Z = +/-6 mm</text><text x="970" y="366">20-2040 axes: X = 0; Z = +{MEMBER_HOLE_Z[0]:.0f}, {MEMBER_HOLE_Z[1]:.0f} mm</text>
<text x="970" y="403">M5 countersink envelope: 11.40 mm maximum</text><text x="970" y="440">Minimum nominal countersink-edge land: 4.300 mm</text>
<rect x="940" y="490" width="500" height="315" rx="14" class="box"/><text x="975" y="540" class="s">Stop-sequencing screen</text>
<text x="975" y="585">Nominal X430 clearance at contact: {stop_clearance:.3f} mm</text><text x="975" y="622">Required physical residual: 1.500 mm</text>
<text x="975" y="659">Available adverse-variation budget: {available:.3f} mm</text><text x="975" y="696">Proposed acceptance allocations: {allocated:.3f} mm</text>
<text x="975" y="740" class="w">ALLOCATIONS ARE UNVERIFIED LIMITS, NOT RESULTS.</text><text x="975" y="775" class="w">DO NOT QUOTE OR FABRICATE FROM THIS DRAWING.</text>
<text x="45" y="865">Material candidate: 6061-T651 plate. Profile +/-0.10 mm, feature position +/-0.05 mm and thickness 9.45..9.60 mm are proposed supplier/FAI limits.</text>
<text x="45" y="905">MTR, DFM, FAI, received frame fit, screw seating, runout/play, deformation, stopping, proof and qualified acceptance remain required.</text>
<text x="45" y="950" class="w">PRELIMINARY - NO FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION AUTHORITY.</text></svg>''',
        encoding="utf-8",
        newline="\n",
    )


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

    if not {(-11.0, -32.0), (11.0, -32.0)} <= p08.exact_axes(x430_raw, "Z", 1.25):
        raise RuntimeError("controlled X430 STEP lost selected rear axes")
    if not {(-11.0, 11.0), (11.0, 11.0)} <= p08.exact_axes(fr12_s102_raw, "X", 1.3):
        raise RuntimeError("controlled FR12-S102 STEP lost selected side axes")

    j1_joint = p07.actuator_to_joint_frame(xm540)
    fixed_catch_y = J2_Y - p08.S102_FIXED_FACE - p08.PLATE_T
    column = p07.column_envelope()
    support = p07.shoulder_support_plate()
    j1_body = p07.rotate_x(j1_joint, 90.0)
    j1_s102 = p07.rotate_x(fr13_s102, 90.0)
    j1_h101 = fr13_h101
    upper_prox = p07.adapter(32.0)
    upper_beam = p07.beam(32.0 + p07.PLATE_T, p07.UPPER_BEAM_L)
    fixed_catch = p08.stop_adapter(fixed_catch_y, p08.STOP_FIXED_WING_Z)
    j2_x430 = p07.rotate_x(p08.x430_to_joint_frame(x430_raw), 90.0).translate((0.0, J2_Y, 0.0))
    j2_s102 = p07.rotate_x(fr12_s102_raw.translate((0.0, 0.0, p08.S102_LOCAL_Z_SHIFT)), 90.0).translate((0.0, J2_Y, 0.0))
    j2_h101 = fr12_h101.translate((0.0, J2_Y, 0.0))
    striker = lowered_striker(MOVING_FACE_Y)
    fore_beam = p07.beam(MOVING_FACE_Y + p08.PLATE_T, p08.FOREARM_BEAM_L).translate((0.0, 0.0, FOREARM_Z_OFFSET))
    distal = p07.gripper_adapter(MOVING_FACE_Y + p08.PLATE_T + p08.FOREARM_BEAM_L).translate((0.0, 0.0, FOREARM_Z_OFFSET))
    gripper = p07.rotate_x(h104, 180.0).translate((0.0, G1_Y, FOREARM_Z_OFFSET))

    fixed_base = {"COLUMN": column, "SHOULDER_SUPPORT": support, "J1_BODY": j1_body, "J1_S102": j1_s102}
    upper_zero = {
        "J1_H101": j1_h101,
        "UPPER_PROX_ADAPTER": upper_prox,
        "UPPER_MEMBER": upper_beam,
        "P11_FIXED_CATCH": fixed_catch,
        "J2_X430": j2_x430,
        "J2_FR12_S102": j2_s102,
    }
    unchanged_moving = {"J2_FR12_H101": j2_h101}
    changed_moving = {
        "P11_LOWERED_STRIKER": striker,
        "FORE_MEMBER_LOWERED": fore_beam,
        "FORE_DIST_H104_ADAPTER_LOWERED": distal,
        "G1_H104_LOWERED": gripper,
    }
    components = {**fixed_base, **upper_zero, **unchanged_moving, **changed_moving}
    assembly = cq.Assembly(name="HR_V0_P11_X430_LOWERED_FOREARM_CANDIDATE_NOT_RELEASED")
    for name, shape in components.items():
        assembly.add(shape, name=name, color=p09.colour(name))
    step = OUT / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step))
    p07.canonicalize_step(step)
    assembly.save(str(OUT / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.glb"))
    part = OUT / "parts" / "P11-C02_X430_lowered-forearm-moving-striker.step"
    cq.exporters.export(lowered_striker(0.0), str(part))
    p07.canonicalize_step(part)

    # Retain only P0.9 certificates for pairs whose two solids are unchanged.
    prior_dir = OUT.parent / "arm-architecture-p0.9-x430"
    prior_summary_path = prior_dir / "continuous-clearance-summary.csv"
    prior_cells_path = prior_dir / "continuous-clearance-cells.csv"
    prior_summary = list(csv.DictReader(prior_summary_path.open(encoding="utf-8", newline="")))
    prior_cells = list(csv.DictReader(prior_cells_path.open(encoding="utf-8", newline="")))
    changed_tokens = {"P09_MOVING_STRIKER", "FORE_MEMBER", "FORE_DIST_H104_ADAPTER", "G1_H104"}
    retained_rows = [row for row in prior_summary if not any(token in row["pair_id"] for token in changed_tokens)]
    retained_cells = [row for row in prior_cells if not any(token in row["pair_id"] for token in changed_tokens)]
    for row in retained_rows:
        row["pair_id"] = row["pair_id"].replace("P09_FIXED_CATCH", "P11_FIXED_CATCH")
        row["required_clearance_mm"] = f"{BASE_REQUIRED_CLEARANCE_MM:.9f}"
        row["evidence_origin"] = "P0.9 IDENTICAL-SOLID PAIR CERTIFICATE REUSED"
    for row in retained_cells:
        row["pair_id"] = row["pair_id"].replace("P09_FIXED_CATCH", "P11_FIXED_CATCH")
        row["required_clearance_mm"] = f"{BASE_REQUIRED_CLEARANCE_MM:.9f}"
        row["evidence_origin"] = "P0.9 IDENTICAL-SOLID PAIR CERTIFICATE REUSED"

    old_j2 = p07.J2_Y
    old_required = p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM
    p07.J2_Y = J2_Y
    try:
        changed_rows: list[dict[str, object]] = []
        changed_cells: list[dict[str, object]] = []
        for u_name, u_shape in upper_zero.items():
            for m_name, m_shape in changed_moving.items():
                if (u_name, m_name) == ("P11_FIXED_CATCH", "P11_LOWERED_STRIKER"):
                    continue
                required = CRITICAL_REQUIRED_CLEARANCE_MM if (u_name, m_name) == ("J2_X430", "P11_LOWERED_STRIKER") else BASE_REQUIRED_CLEARANCE_MM
                p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM = required
                row, cells = p07.certify_continuous_1d(
                    pair_id=f"UPPER_FORE:{u_name}:{m_name}",
                    fixed_shape=u_shape,
                    moving_shape=m_shape,
                    rotation_origin_y=J2_Y,
                    q_lo=Q2_LO,
                    q_hi=SOFT_LIMIT,
                    coordinate="J2",
                )
                row["required_clearance_mm"] = f"{required:.9f}"
                row["evidence_origin"] = "P1.1 CHANGED-SOLID PAIR RECALCULATED"
                for cell in cells:
                    cell["required_clearance_mm"] = f"{required:.9f}"
                    cell["evidence_origin"] = "P1.1 CHANGED-SOLID PAIR RECALCULATED"
                changed_rows.append(row)
                changed_cells.extend(cells)
        p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM = BASE_REQUIRED_CLEARANCE_MM
        for f_name, f_shape in fixed_base.items():
            for m_name, m_shape in changed_moving.items():
                row, cells = p07.certify_continuous_2d(
                    pair_id=f"BASE_FORE:{f_name}:{m_name}",
                    fixed_shape=f_shape,
                    moving_shape=m_shape,
                    q1_lo=Q1_LO,
                    q1_hi=Q1_HI,
                    q2_lo=Q2_LO,
                    q2_hi=SOFT_LIMIT,
                )
                row["required_clearance_mm"] = f"{BASE_REQUIRED_CLEARANCE_MM:.9f}"
                row["evidence_origin"] = "P1.1 CHANGED-SOLID PAIR RECALCULATED"
                for cell in cells:
                    cell["required_clearance_mm"] = f"{BASE_REQUIRED_CLEARANCE_MM:.9f}"
                    cell["evidence_origin"] = "P1.1 CHANGED-SOLID PAIR RECALCULATED"
                changed_rows.append(row)
                changed_cells.extend(cells)
    finally:
        p07.J2_Y = old_j2
        p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM = old_required

    continuous_rows = [*retained_rows, *changed_rows]
    cell_rows = [*retained_cells, *changed_cells]
    write_csv(OUT / "continuous-clearance-summary.csv", continuous_rows)
    write_csv(OUT / "continuous-clearance-cells.csv", cell_rows)
    write_csv(OUT / "certificate-supersession-basis.csv", [
        {"evidence_set": "P0.9 retained unchanged-solid pairs", "pair_count": len(retained_rows), "source_sha256": hashlib.sha256(prior_summary_path.read_bytes()).hexdigest().upper(), "basis": "neither solid changed; fixed-catch identifier renamed only", "status": "REUSED EXACT CERTIFICATE"},
        {"evidence_set": "P1.1 changed-solid pairs", "pair_count": len(changed_rows), "source_sha256": "GENERATED IN THIS PACKAGE", "basis": "every pair involving striker, forearm member, distal adapter, or H104 recomputed", "status": "NEW EXACT/BOUND CERTIFICATE"},
    ])

    exact_rows: list[dict[str, object]] = []
    for index in range(int((STOP_TARGET - Q2_LO) / 0.25) + 1):
        q2 = Q2_LO + index * 0.25
        moved = p07.rotate_x(striker, q2, J2_Y)
        stop_clearance = fixed_catch.distance(moved)
        exact_rows.append({
            "j2_deg": f"{q2:.2f}",
            "x430_to_striker_clearance_mm": f"{j2_x430.distance(moved):.9f}",
            "positive_stop_clearance_mm": f"{stop_clearance:.9f}",
            "positive_stop_state": "CONTACT" if stop_clearance <= 1e-7 else "CLEAR",
            "status": "EXACT NOMINAL BREP - PHYSICAL VARIATION/DEFORMATION/FASTENER PROJECTION OPEN",
        })
    write_csv(OUT / "critical-clearance-and-stop-sweep.csv", exact_rows)
    contact = first_contact(fixed_catch, striker, 116.0, 120.0)
    body_soft = j2_x430.distance(p07.rotate_x(striker, SOFT_LIMIT, J2_Y))
    body_stop = j2_x430.distance(p07.rotate_x(striker, STOP_TARGET, J2_Y))
    stop_gap_soft = fixed_catch.distance(p07.rotate_x(striker, SOFT_LIMIT, J2_Y))

    allocated = sum(TOLERANCE_ALLOCATIONS_MM.values())
    available = body_stop - PHYSICAL_RESIDUAL_REQUIREMENT_MM
    if allocated > available:
        raise RuntimeError(f"P1.1 tolerance allocations {allocated:.6f} exceed available {available:.6f}")
    budget_rows = []
    evidence = {
        "part_profile_thickness": "released drawing, supplier DFM and calibrated FAI",
        "frame_actuator_registration_runout": "received joint-stack metrology with uncertainty",
        "joint_play_and_calibration": "loaded bidirectional measurement over temperature and wear",
        "fastener_projection": "selected stack, received inspection and access/torque trial",
        "stop_deformation_and_bumper": "accepted structural model, proof and dynamic stop tests",
        "measurement_uncertainty": "approved measurement-system analysis and calibrated instruments",
    }
    for index, (source, limit) in enumerate(TOLERANCE_ALLOCATIONS_MM.items(), 1):
        budget_rows.append({"budget_id": f"P11-TOL-{index:02d}", "source": source, "maximum_adverse_contribution_mm": f"{limit:.3f}", "evidence": evidence[source], "state": "ALLOCATED ACCEPTANCE LIMIT - UNVERIFIED"})
    budget_rows.append({"budget_id": "P11-TOL-SUM", "source": "combined worst-case adverse variation", "maximum_adverse_contribution_mm": f"{allocated:.3f}", "evidence": f"must be <= {available:.6f} mm to preserve >= {PHYSICAL_RESIDUAL_REQUIREMENT_MM:.3f} mm physical residual", "state": "PROVISIONAL ALLOCATION PASS - ALL INPUTS UNVERIFIED"})
    write_csv(OUT / "stop-sequencing-tolerance-budget.csv", budget_rows)

    edge_land = min(PLATE_Z_MAX - MEMBER_HOLE_Z[0] - p07.END_CSK_D / 2.0, MEMBER_HOLE_Z[1] - p07.END_CSK_D / 2.0 - PLATE_Z_MIN)
    feature_rows = [
        {"check_id": "P11-FEAT-01", "feature": "upper M5 countersink to top profile", "result_mm": f"{edge_land:.3f}", "criterion": ">= 2.000 mm nominal", "status": "PASS NOMINAL; FAI/PROOF OPEN"},
        {"check_id": "P11-FEAT-02", "feature": "lower M5 countersink to bottom profile", "result_mm": f"{edge_land:.3f}", "criterion": ">= 2.000 mm nominal", "status": "PASS NOMINAL; FAI/PROOF OPEN"},
        {"check_id": "P11-FEAT-03", "feature": "M5 countersink-to-countersink", "result_mm": f"{abs(MEMBER_HOLE_Z[0] - MEMBER_HOLE_Z[1]) - p07.END_CSK_D:.3f}", "criterion": ">= 1.000 mm nominal", "status": "PASS NOMINAL; FAI/PROOF OPEN"},
        {"check_id": "P11-FEAT-04", "feature": "closest M5-to-FR12 hole envelopes", "result_mm": f"{math.hypot(12.0, 2.0) - p07.END_CSK_D / 2.0 - p08.FRAME_HOLE_D / 2.0:.3f}", "criterion": ">= 1.000 mm nominal", "status": "PASS NOMINAL; FAI/PROOF OPEN"},
    ]
    write_csv(OUT / "fastener-feature-screen.csv", feature_rows)
    write_csv(OUT / "transform-register.csv", [
        {"transform_id": "P11-TF-01", "item": "J2 axis", "x_mm": "0.000", "y_mm": f"{J2_Y:.3f}", "z_mm": "0.000", "status": "CONTROLLED NOMINAL"},
        {"transform_id": "P11-TF-02", "item": "FR12-H101 moving face / striker origin", "x_mm": "0.000", "y_mm": f"{MOVING_FACE_Y:.3f}", "z_mm": "0.000", "status": "CONTROLLED NOMINAL"},
        {"transform_id": "P11-TF-03", "item": "20-2040/H104 forearm offset", "x_mm": "0.000", "y_mm": "UNCHANGED", "z_mm": f"{FOREARM_Z_OFFSET:.3f}", "status": "P1.1 CHANGED TRANSFORM"},
    ])

    density = 2.70 / 1000.0
    striker_mass = striker.Volume() * density
    p10_mass = 576.040
    p10_striker_mass = 51.184
    subtotal = p10_mass - p10_striker_mass + striker_mass
    write_csv(OUT / "mass-comparison.csv", [
        {"configuration": "P1.0 clearance candidate", "moving_striker_cad_mass_g": f"{p10_striker_mass:.3f}", "incomplete_known_mass_g": f"{p10_mass:.3f}", "provisional_headroom_g": f"{750.0 - p10_mass:.3f}", "status": "NONSELECTED INCOMPLETE SCREEN"},
        {"configuration": "P1.1 lowered-forearm candidate", "moving_striker_cad_mass_g": f"{striker_mass:.3f}", "incomplete_known_mass_g": f"{subtotal:.3f}", "provisional_headroom_g": f"{750.0 - subtotal:.3f}", "status": "NONSELECTED INCOMPLETE SCREEN; RECEIVED MASS/COM/INERTIA OPEN"},
    ])

    holds = list(csv.DictReader((OUT.parent / "arm-architecture-p1.0-x430-clearance" / "architecture-holds.csv").open(encoding="utf-8", newline="")))
    for row in holds:
        if row["hold_id"] in {"ELBH-007", "ELBH-008", "ELBH-009"}:
            row["release_effect"] += "; P1.1 allocates larger nominal clearance but every physical allocation remains unverified"
    write_csv(OUT / "architecture-holds.csv", holds)

    profile_drawing(OUT / "P11-C02_lowered-forearm-moving-striker-review-drawing.svg", body_stop, allocated, available)
    minimum_all = min(float(row["minimum_guaranteed_clearance_mm"]) for row in continuous_rows)
    minimum_changed = min(float(row["minimum_guaranteed_clearance_mm"]) for row in changed_rows)
    critical_row = next(row for row in changed_rows if row["pair_id"] == "UPPER_FORE:J2_X430:P11_LOWERED_STRIKER")
    continuous = {
        "base_required_clearance_mm": BASE_REQUIRED_CLEARANCE_MM,
        "critical_x430_striker_required_clearance_mm": CRITICAL_REQUIRED_CLEARANCE_MM,
        "minimum_guaranteed_all_pairs_mm": round(minimum_all, 6),
        "minimum_guaranteed_changed_pairs_mm": round(minimum_changed, 6),
        "critical_x430_striker_guaranteed_clearance_mm": round(float(critical_row["minimum_guaranteed_clearance_mm"]), 6),
        "pair_count": len(continuous_rows),
        "retained_pair_count": len(retained_rows),
        "recomputed_changed_pair_count": len(changed_rows),
        "leaf_cell_count": len(cell_rows),
        "exact_brep_distance_calls": sum(int(row["exact_brep_distance_calls"]) for row in continuous_rows),
        "joint_domain_deg": {"j1": [Q1_LO, Q1_HI], "j2": [Q2_LO, SOFT_LIMIT]},
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE_ONLY",
    }
    flags = {"supersedes_p0_7": False, "supersedes_p1_0": False, "x430_selected": False, "quotation_authorized": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "motion_authorized": False, "connection_authorized": False, "energization_authorized": False}
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "configuration_disposition": "P1.1 comparison only; P0.7 remains controlled; X430 is not selected",
        "transform_controls": {"j2_axis_y_mm": J2_Y, "moving_face_y_mm": MOVING_FACE_Y, "forearm_z_offset_mm": FOREARM_Z_OFFSET},
        "feature_controls": {"base_z_mm": [PLATE_Z_MIN, PLATE_Z_MAX], "member_hole_z_mm": list(MEMBER_HOLE_Z), "nominal_minimum_countersink_edge_land_mm": round(edge_land, 3)},
        "certificate_supersession": {"retained_identical_pair_count": len(retained_rows), "recomputed_changed_pair_count": len(changed_rows), "full_pair_count": len(continuous_rows), "status": "ALL CHANGED-SOLID PAIRS RECOMPUTED"},
        "continuous_clearance": continuous,
        "stop_sequencing": {"soft_limit_deg": SOFT_LIMIT, "nominal_first_contact_deg": round(contact, 6), "x430_clearance_at_soft_limit_mm": round(body_soft, 6), "x430_clearance_at_stop_contact_mm": round(body_stop, 6), "stop_gap_at_soft_limit_mm": round(stop_gap_soft, 6), "required_physical_residual_at_stop_mm": PHYSICAL_RESIDUAL_REQUIREMENT_MM, "available_adverse_variation_mm": round(available, 6), "allocated_adverse_variation_mm": round(allocated, 6), "unallocated_margin_mm": round(available - allocated, 6), "status": "NOMINAL CAD PLUS UNVERIFIED ACCEPTANCE ALLOCATION"},
        "mass": {"moving_striker_cad_mass_g": round(striker_mass, 3), "incomplete_known_mass_g": round(subtotal, 3), "provisional_headroom_g": round(750.0 - subtotal, 3)},
        "hold_counts": {"open": sum(row["state"] == "OPEN" for row in holds), "partial": sum(row["state"] == "PARTIAL" for row in holds)},
        "release_flags": flags,
    }
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "continuous-clearance-analysis.json").write_text(json.dumps({"revision": REVISION, **continuous, "release_boundary": "nominal rigid solids only; tolerances, fastener projections, cables, guards, deformation, compliance and stopping travel excluded"}, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "package-status.json").write_text(json.dumps({"revision": REVISION, "state": "COMPARISON_CANDIDATE_NOT_SELECTED", "warning": WARNING, "release_flags": flags}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
