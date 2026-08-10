"""Generate the P1.0 X430 full-arm clearance-margin comparison.

This nonselected branch contours the P0.9 moving striker so the unused upper
plate edge cannot consume the nominal stop-sequencing margin.  It remains a
review candidate and grants no fabrication, motion, or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as p07  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as p08  # noqa: E402
import generate_hr_v0_x430_integrated_arm as p09  # noqa: E402


REVISION = "HR-V0-ARM-ARCH-P1.0-X430-CLEARANCE-CANDIDATE"
WARNING = (
    "PRELIMINARY - COMPARISON CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, "
    "PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p1.0-x430-clearance"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
VENDOR_X430 = VENDOR / "x430-fr12-r91"

J2_Y = p08.J2_Y
G1_Y = J2_Y + p08.G1_LOCAL_Y
Q1_LO = -20.0
Q1_HI = 70.0
Q2_LO = 15.0
SOFT_LIMIT = 115.0
STOP_TARGET = 118.0
SAMPLE_INCREMENT = 1.0
CONTINUOUS_REQUIRED_MM = 3.0
PHYSICAL_RESIDUAL_REQUIREMENT_MM = 1.0
MOVING_PLATE_TOP_Z = 15.0
MOVING_M5_BOSS_TOP_Z = 17.0
MOVING_M5_BOSS_HALF_WIDTH = 8.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def relieved_moving_striker(y0: float) -> cq.Shape:
    """2.5-D plate with a local M5 boss and integral external stop lobes."""

    base = cq.Solid.makeBox(
        48.0,
        p08.PLATE_T,
        MOVING_PLATE_TOP_Z + 20.0,
        cq.Vector(-24.0, y0, -20.0),
    )
    boss = cq.Solid.makeBox(
        MOVING_M5_BOSS_HALF_WIDTH * 2.0,
        p08.PLATE_T,
        MOVING_M5_BOSS_TOP_Z - MOVING_PLATE_TOP_Z,
        cq.Vector(-MOVING_M5_BOSS_HALF_WIDTH, y0, MOVING_PLATE_TOP_Z),
    )
    lobe_height = p08.STOP_MOVING_WING_Z + 6.0 - MOVING_PLATE_TOP_Z
    right = cq.Solid.makeBox(17.0, p08.PLATE_T, lobe_height, cq.Vector(24.0, y0, MOVING_PLATE_TOP_Z))
    left = cq.Solid.makeBox(17.0, p08.PLATE_T, lobe_height, cq.Vector(-41.0, y0, MOVING_PLATE_TOP_Z))
    return p08.cut_adapter_features(base.fuse(boss).fuse(right).fuse(left), y0)


def profile_drawing(path: Path) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
<style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:34px;font-weight:700;fill:#082b55}}.w{{font-weight:700;fill:#9b1c1c}}.p{{stroke:#082b55;stroke-width:3;fill:#e4f6ff}}.d{{stroke:#f4b942;stroke-width:3;fill:none}}.c{{stroke:#9b1c1c;stroke-width:2}}</style>
<rect width="1200" height="800" fill="#f7fbff"/><text x="45" y="60" class="h">P10-C02 relieved X430 moving-striker candidate</text>
<text x="45" y="100" class="w">{WARNING}</text>
<path d="M260 610 L260 330 L420 330 L420 290 L580 290 L580 330 L740 330 L740 610 Z" class="p"/>
<path d="M90 250 L260 250 L260 330 L90 330 Z M740 250 L910 250 L910 330 L740 330 Z" class="p"/>
<circle cx="420" cy="470" r="13" class="d"/><circle cx="580" cy="470" r="13" class="d"/><circle cx="420" cy="550" r="13" class="d"/><circle cx="580" cy="550" r="13" class="d"/>
<circle cx="500" cy="410" r="30" class="d"/><circle cx="500" cy="570" r="30" class="d"/>
<line x1="500" y1="200" x2="500" y2="650" class="c"/><line x1="60" y1="490" x2="950" y2="490" class="c"/>
<text x="45" y="690">Base contour Z=-20..+15 mm; local M5 boss X=±8 mm, Z=+15..+17 mm; external lobes preserve the P0.9 stop surface.</text>
<text x="45" y="725">Nominal 9.525 mm thickness. Hole axes remain X=±12,Z=±6 and X=0,Z=±10. Exact tolerance/material/fasteners remain SELECTION REQUIRED.</text>
<text x="45" y="770" class="w">DO NOT QUOTE OR FABRICATE FROM THIS REVIEW DRAWING.</text></svg>''',
        encoding="utf-8",
        newline="\n",
    )


def first_contact(fixed: cq.Shape, moving: cq.Shape, lo: float, hi: float) -> float:
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if fixed.distance(p07.rotate_x(moving, mid, J2_Y)) > 1e-7:
            lo = mid
        else:
            hi = mid
    return hi


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
    moving_y = J2_Y + p08.J2_H101_FACE
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
    moving_striker = relieved_moving_striker(moving_y)
    fore_beam = p07.beam(moving_y + p08.PLATE_T, p08.FOREARM_BEAM_L)
    distal = p07.gripper_adapter(moving_y + p08.PLATE_T + p08.FOREARM_BEAM_L)
    gripper = p07.rotate_x(h104, 180.0).translate((0.0, G1_Y, 0.0))

    fixed_base = {"COLUMN": column, "SHOULDER_SUPPORT": support, "J1_BODY": j1_body, "J1_S102": j1_s102}
    upper_zero = {
        "J1_H101": j1_h101,
        "UPPER_PROX_ADAPTER": upper_prox,
        "UPPER_MEMBER": upper_beam,
        "P10_FIXED_CATCH": fixed_catch,
        "J2_X430": j2_x430,
        "J2_FR12_S102": j2_s102,
    }
    moving_zero = {
        "J2_FR12_H101": j2_h101,
        "P10_RELIEVED_STRIKER": moving_striker,
        "FORE_MEMBER": fore_beam,
        "FORE_DIST_H104_ADAPTER": distal,
        "G1_H104": gripper,
    }
    intentional_j1 = {("J1_BODY", "J1_H101"), ("J1_S102", "J1_H101")}
    intentional_j2 = {("J2_X430", "J2_FR12_H101"), ("J2_FR12_S102", "J2_FR12_H101")}
    intentional_stop = {("P10_FIXED_CATCH", "P10_RELIEVED_STRIKER")}

    components = {**fixed_base, **upper_zero, **moving_zero}
    assembly = cq.Assembly(name="HR_V0_P10_X430_CLEARANCE_CANDIDATE_NOT_RELEASED")
    for name, shape in components.items():
        assembly.add(shape, name=name, color=p09.colour(name))
    step = OUT / "HR-V0_arm_P1.0_X430_clearance_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step))
    p07.canonicalize_step(step)
    assembly.save(str(OUT / "HR-V0_arm_P1.0_X430_clearance_candidate.glb"))
    part = OUT / "parts" / "P10-C02_X430_relief-moving-striker.step"
    cq.exporters.export(relieved_moving_striker(0.0), str(part))
    p07.canonicalize_step(part)
    profile_drawing(OUT / "P10-C02_relief-moving-striker-review-drawing.svg")

    # P1.0 changes only P09_MOVING_STRIKER. Reuse the 60 continuous certificates
    # whose two solids are byte-for-byte/configuration-identical, and recompute
    # every one of the nine pair groups involving the changed part. The changed
    # pairs must meet a stricter 3 mm nominal floor.
    prior_dir = OUT.parent / "arm-architecture-p0.9-x430"
    prior_summary_path = prior_dir / "continuous-clearance-summary.csv"
    prior_cells_path = prior_dir / "continuous-clearance-cells.csv"
    with prior_summary_path.open(encoding="utf-8", newline="") as handle:
        prior_summary = list(csv.DictReader(handle))
    with prior_cells_path.open(encoding="utf-8", newline="") as handle:
        prior_cells = list(csv.DictReader(handle))
    retained_rows = [row for row in prior_summary if "P09_MOVING_STRIKER" not in row["pair_id"]]
    retained_cells = [row for row in prior_cells if "P09_MOVING_STRIKER" not in row["pair_id"]]
    for row in retained_rows:
        row["pair_id"] = row["pair_id"].replace("P09_FIXED_CATCH", "P10_FIXED_CATCH")
        row["required_clearance_mm"] = "0.750000000"
        row["evidence_origin"] = "P0.9 IDENTICAL-SOLID PAIR CERTIFICATE REUSED"
    for row in retained_cells:
        row["pair_id"] = row["pair_id"].replace("P09_FIXED_CATCH", "P10_FIXED_CATCH")
        row["required_clearance_mm"] = "0.750000000"
        row["evidence_origin"] = "P0.9 IDENTICAL-SOLID PAIR CERTIFICATE REUSED"

    old_j2 = p07.J2_Y
    old_required = p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM
    p07.J2_Y = J2_Y
    p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM = CONTINUOUS_REQUIRED_MM
    try:
        changed_rows: list[dict[str, object]] = []
        changed_cells: list[dict[str, object]] = []
        for u_name, u_shape in upper_zero.items():
            if (u_name, "P10_RELIEVED_STRIKER") in intentional_stop:
                continue
            row, cells = p07.certify_continuous_1d(pair_id=f"UPPER_FORE:{u_name}:P10_RELIEVED_STRIKER", fixed_shape=u_shape, moving_shape=moving_striker, rotation_origin_y=J2_Y, q_lo=Q2_LO, q_hi=SOFT_LIMIT, coordinate="J2")
            changed_rows.append(row); changed_cells.extend(cells)
        for f_name, f_shape in fixed_base.items():
            row, cells = p07.certify_continuous_2d(pair_id=f"BASE_FORE:{f_name}:P10_RELIEVED_STRIKER", fixed_shape=f_shape, moving_shape=moving_striker, q1_lo=Q1_LO, q1_hi=Q1_HI, q2_lo=Q2_LO, q2_hi=SOFT_LIMIT)
            changed_rows.append(row); changed_cells.extend(cells)
    finally:
        p07.J2_Y = old_j2
        p07.CONTINUOUS_CERTIFIED_CLEARANCE_MM = old_required
    for row in changed_rows:
        row["required_clearance_mm"] = f"{CONTINUOUS_REQUIRED_MM:.9f}"
        row["evidence_origin"] = "P1.0 CHANGED-PART PAIR RECALCULATED"
    for row in changed_cells:
        row["required_clearance_mm"] = f"{CONTINUOUS_REQUIRED_MM:.9f}"
        row["evidence_origin"] = "P1.0 CHANGED-PART PAIR RECALCULATED"
    continuous_rows = [*retained_rows, *changed_rows]
    cell_rows = [*retained_cells, *changed_cells]
    write_csv(OUT / "continuous-clearance-summary.csv", continuous_rows)
    write_csv(OUT / "continuous-clearance-cells.csv", cell_rows)
    continuous_min = min(float(row["minimum_guaranteed_clearance_mm"]) for row in continuous_rows)
    changed_min = min(float(row["minimum_guaranteed_clearance_mm"]) for row in changed_rows)
    write_csv(OUT / "certificate-supersession-basis.csv", [
        {"evidence_set": "P0.9 retained pairs", "pair_count": len(retained_rows), "required_clearance_mm": "0.750", "source_sha256": hashlib.sha256(prior_summary_path.read_bytes()).hexdigest().upper(), "basis": "neither solid changed; fixed-catch pair IDs renamed only", "status": "REUSED EXACT CERTIFICATE"},
        {"evidence_set": "P1.0 changed-striker pairs", "pair_count": len(changed_rows), "required_clearance_mm": f"{CONTINUOUS_REQUIRED_MM:.3f}", "source_sha256": "GENERATED IN THIS PACKAGE", "basis": "every pair involving changed P10-C02 recomputed", "status": "NEW EXACT/BOUND CERTIFICATE"},
    ])

    # Exact critical-pair and stop sequencing sweep.
    exact_rows: list[dict[str, object]] = []
    exact_increment = 0.25
    for i in range(int((STOP_TARGET - Q2_LO) / exact_increment) + 1):
        q2 = Q2_LO + i * exact_increment
        moved = p07.rotate_x(moving_striker, q2, J2_Y)
        stop_clearance = fixed_catch.distance(moved)
        exact_rows.append({
            "j2_deg": f"{q2:.2f}",
            "x430_to_relief_striker_clearance_mm": f"{j2_x430.distance(moved):.9f}",
            "positive_stop_clearance_mm": f"{stop_clearance:.9f}",
            "positive_stop_state": "CONTACT" if stop_clearance <= 1e-7 else "CLEAR",
            "status": "EXACT NOMINAL BREP - PHYSICAL VARIATION/DEFORMATION/FASTENER PROJECTION OPEN",
        })
    write_csv(OUT / "critical-clearance-and-stop-sweep.csv", exact_rows)
    contact = first_contact(fixed_catch, moving_striker, 116.0, 120.0)
    body_soft = j2_x430.distance(p07.rotate_x(moving_striker, SOFT_LIMIT, J2_Y))
    body_stop = j2_x430.distance(p07.rotate_x(moving_striker, STOP_TARGET, J2_Y))
    stop_gap_soft = fixed_catch.distance(p07.rotate_x(moving_striker, SOFT_LIMIT, J2_Y))

    budget_rows = [
        {"budget_id": "P10-TOL-01", "source": "adapter contour/profile and thickness", "maximum_adverse_contribution_mm": "SELECTION REQUIRED", "evidence": "released drawing tolerance, DFM, calibrated FAI", "state": "OPEN"},
        {"budget_id": "P10-TOL-02", "source": "X430/FR12 axial registration and runout", "maximum_adverse_contribution_mm": "SELECTION REQUIRED", "evidence": "received joint-stack metrology with uncertainty", "state": "OPEN"},
        {"budget_id": "P10-TOL-03", "source": "bearing/gear/frame play and calibration error", "maximum_adverse_contribution_mm": "SELECTION REQUIRED", "evidence": "loaded bidirectional measurement over temperature and wear", "state": "OPEN"},
        {"budget_id": "P10-TOL-04", "source": "fastener head/nut/washer projection", "maximum_adverse_contribution_mm": "SELECTION REQUIRED", "evidence": "exact selected stack, received inspection, torque/access trial", "state": "OPEN"},
        {"budget_id": "P10-TOL-05", "source": "elastic/impact deformation and bumper behavior", "maximum_adverse_contribution_mm": "SELECTION REQUIRED", "evidence": "accepted structural model, proof and dynamic stop tests", "state": "OPEN"},
        {"budget_id": "P10-TOL-SUM", "source": "combined worst-case adverse variation", "maximum_adverse_contribution_mm": f"<={body_stop - PHYSICAL_RESIDUAL_REQUIREMENT_MM:.6f}", "evidence": f"worst-case stack must preserve >={PHYSICAL_RESIDUAL_REQUIREMENT_MM:.3f} mm X430/body clearance at first stop contact", "state": "UNALLOCATED_OPEN_LIMIT"},
    ]
    write_csv(OUT / "stop-sequencing-tolerance-budget.csv", budget_rows)

    density = 2.70 / 1000.0
    catch_mass = fixed_catch.Volume() * density
    striker_mass = moving_striker.Volume() * density
    subtotal = 692.758 - 165.0 - 66.870 - 70.265 + 82.0 + catch_mass + striker_mass
    write_csv(OUT / "mass-comparison.csv", [
        {"configuration": "P0.9 integrated candidate", "moving_striker_cad_mass_g": "52.234", "incomplete_known_mass_g": "577.091", "provisional_headroom_g": "172.909", "status": "NONSELECTED INCOMPLETE SCREEN"},
        {"configuration": "P1.0 clearance candidate", "moving_striker_cad_mass_g": f"{striker_mass:.3f}", "incomplete_known_mass_g": f"{subtotal:.3f}", "provisional_headroom_g": f"{750.0 - subtotal:.3f}", "status": "NONSELECTED INCOMPLETE SCREEN; RECEIVED MASS/COM/INERTIA OPEN"},
    ])

    holds = list(csv.DictReader((OUT.parent / "arm-architecture-p0.9-x430" / "architecture-holds.csv").open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] in {"ELBH-007", "ELBH-008", "ELBH-009"}:
            row["release_effect"] += "; P1.0 increases nominal clearance but tolerance allocation and physical proof remain open"
    write_csv(OUT / "architecture-holds.csv", holds)

    continuous = {
        "retained_pair_required_clearance_mm": 0.75,
        "changed_striker_pair_required_clearance_mm": CONTINUOUS_REQUIRED_MM,
        "minimum_guaranteed_all_pairs_mm": round(continuous_min, 6),
        "minimum_guaranteed_changed_striker_pairs_mm": round(changed_min, 6),
        "pair_count": len(continuous_rows),
        "retained_pair_count": len(retained_rows),
        "recomputed_changed_pair_count": len(changed_rows),
        "leaf_cell_count": len(cell_rows),
        "exact_brep_distance_calls": sum(int(row["exact_brep_distance_calls"]) for row in continuous_rows),
        "joint_domain_deg": {"j1": [Q1_LO, Q1_HI], "j2": [Q2_LO, SOFT_LIMIT]},
        "status": "CERTIFIED_NOMINAL_MODEL_SPACE_ONLY",
    }
    flags = {"supersedes_p0_7": False, "supersedes_p0_9": False, "xm430_selected": False, "quotation_authorized": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "motion_authorized": False, "connection_authorized": False, "energization_authorized": False}
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "configuration_disposition": "P1.0 comparison only; P0.7 remains controlled; P0.9 remains prior comparison; XM430 is not selected",
        "contour_mm": {"base_top_z": MOVING_PLATE_TOP_Z, "m5_boss_top_z": MOVING_M5_BOSS_TOP_Z, "m5_boss_half_width": MOVING_M5_BOSS_HALF_WIDTH, "original_stop_surface_preserved_from_z": p08.STOP_MOVING_WING_Z},
        "certificate_supersession": {"retained_identical_pair_count": len(retained_rows), "recomputed_changed_pair_count": len(changed_rows), "full_pair_count": len(continuous_rows), "status": "ALL CHANGED-PART PAIRS RECOMPUTED; NO SAMPLED-SWEEP SUBSTITUTION"},
        "continuous_clearance": continuous,
        "stop_sequencing": {"soft_limit_deg": SOFT_LIMIT, "nominal_first_contact_deg": round(contact, 6), "x430_clearance_at_soft_limit_mm": round(body_soft, 6), "x430_clearance_at_stop_contact_mm": round(body_stop, 6), "stop_gap_at_soft_limit_mm": round(stop_gap_soft, 6), "required_physical_residual_at_stop_mm": PHYSICAL_RESIDUAL_REQUIREMENT_MM, "maximum_combined_adverse_variation_mm": round(body_stop - PHYSICAL_RESIDUAL_REQUIREMENT_MM, 6), "status": "NOMINAL CAD AND UNALLOCATED REQUIREMENT ONLY"},
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
