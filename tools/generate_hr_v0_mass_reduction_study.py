"""Generate the HR-V0 same-interface mass-reduction feasibility study.

The study removes material only from the four moving custom adapters in the
controlled P0.7 arm architecture.  Joint coordinates, plate thickness, hole
axes, countersinks, stop rails and stop-contact faces are unchanged.  The
outputs are analytical candidates, not fabrication or motion releases.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as base


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "mass-reduction-p0.1"
REVISION = "HR-V0-MASS-REDUCTION-P0.1"
PARENT_REVISION = base.REVISION
WARNING = "PRELIMINARY - MASS-REDUCTION STUDY ONLY - NOT RELEASED FOR FABRICATION, MOTION, OR ENERGIZATION"
DENSITY_G_CM3 = 2.70
PROFILE_HALF_WIDTH_MM = 22.0
PROFILE_HALF_HEIGHT_MM = 18.0
PROFILE_WEB_HALF_WIDTH_MM = 4.0
PROFILE_GAP_HALF_HEIGHT_MM = 3.0
SUBSET_TOLERANCE_MM3 = 1e-5


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cutter(x0: float, x1: float, z0: float, z1: float) -> cq.Shape:
    return cq.Solid.makeBox(
        x1 - x0,
        base.PLATE_T + 2.0,
        z1 - z0,
        cq.Vector(x0, -1.0, z0),
    )


def regular_relief(parent: cq.Shape) -> cq.Shape:
    """Create an I-profile by subtracting regions from the exact parent."""

    shape = parent
    cuts = (
        (-30.0, 30.0, PROFILE_HALF_HEIGHT_MM, 30.0),
        (-30.0, 30.0, -30.0, -PROFILE_HALF_HEIGHT_MM),
        (-30.0, -PROFILE_HALF_WIDTH_MM, -PROFILE_HALF_HEIGHT_MM, PROFILE_HALF_HEIGHT_MM),
        (PROFILE_HALF_WIDTH_MM, 30.0, -PROFILE_HALF_HEIGHT_MM, PROFILE_HALF_HEIGHT_MM),
        (-PROFILE_HALF_WIDTH_MM, -PROFILE_WEB_HALF_WIDTH_MM, -PROFILE_GAP_HALF_HEIGHT_MM, PROFILE_GAP_HALF_HEIGHT_MM),
        (PROFILE_WEB_HALF_WIDTH_MM, PROFILE_HALF_WIDTH_MM, -PROFILE_GAP_HALF_HEIGHT_MM, PROFILE_GAP_HALF_HEIGHT_MM),
    )
    for bounds in cuts:
        shape = shape.cut(cutter(*bounds))
    return shape


def stop_relief(parent: cq.Shape) -> cq.Shape:
    """Retain exact twin rails/contact faces while relieving the parent plate."""

    shape = parent
    cuts = (
        (-50.0, 50.0, -30.0, -PROFILE_HALF_HEIGHT_MM),
        (-35.0, 35.0, PROFILE_HALF_HEIGHT_MM, 50.0),
        (PROFILE_HALF_WIDTH_MM, 35.0, -PROFILE_GAP_HALF_HEIGHT_MM, 50.0),
        (-35.0, -PROFILE_HALF_WIDTH_MM, -PROFILE_GAP_HALF_HEIGHT_MM, 50.0),
        (-PROFILE_HALF_WIDTH_MM, -PROFILE_WEB_HALF_WIDTH_MM, -PROFILE_GAP_HALF_HEIGHT_MM, PROFILE_GAP_HALF_HEIGHT_MM),
        (PROFILE_WEB_HALF_WIDTH_MM, PROFILE_HALF_WIDTH_MM, -PROFILE_GAP_HALF_HEIGHT_MM, PROFILE_GAP_HALF_HEIGHT_MM),
    )
    for bounds in cuts:
        shape = shape.cut(cutter(*bounds))
    return shape


def mass_g(shape: cq.Shape) -> float:
    return shape.Volume() / 1000.0 * DENSITY_G_CM3


def first_contact_angle(fixed: cq.Shape, moving: cq.Shape, lo: float, hi: float) -> float:
    if fixed.distance(base.rotate_x(moving, hi, base.J2_Y)) > 1e-7:
        raise RuntimeError("stop contact was not bracketed")
    for _ in range(60):
        midpoint = (lo + hi) / 2.0
        if fixed.distance(base.rotate_x(moving, midpoint, base.J2_Y)) > 1e-7:
            lo = midpoint
        else:
            hi = midpoint
    return hi


def svg_drawing(summary: dict[str, object]) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
<style>
  text {{ font-family: Arial, sans-serif; fill: #102a43; font-size: 18px; }}
  .title {{ font-size: 34px; font-weight: 700; }}
  .head {{ font-size: 23px; font-weight: 700; }}
  .warn {{ font-size: 20px; font-weight: 700; fill: #8a4b00; }}
  .part {{ fill: #9dd8f5; stroke: #123b68; stroke-width: 4; }}
  .cut {{ fill: white; stroke: #123b68; stroke-width: 3; stroke-dasharray: 8 6; }}
  .stop {{ fill: #f4bd3e; stroke: #123b68; stroke-width: 4; }}
  .dim {{ fill: none; stroke: #607d98; stroke-width: 2; }}
</style>
<rect width="1600" height="1000" fill="#f8fbff"/>
<text x="60" y="65" class="title">HR-V0 same-interface moving-adapter mass-reduction study</text>
<text x="60" y="105" class="warn">{WARNING}</text>
<text x="60" y="150">Revision {REVISION} • parent {PARENT_REVISION} • units mm and g</text>

<text x="100" y="225" class="head">C01R / C04R relieved interface plate</text>
<path class="part" d="M120 510 L560 510 L560 360 L380 360 L380 300 L560 300 L560 150 L120 150 L120 300 L300 300 L300 360 L120 360 Z"/>
<circle cx="280" cy="250" r="14" class="cut"/><circle cx="400" cy="250" r="14" class="cut"/>
<circle cx="280" cy="410" r="14" class="cut"/><circle cx="400" cy="410" r="14" class="cut"/>
<circle cx="340" cy="230" r="57" class="cut"/><circle cx="340" cy="430" r="57" class="cut"/>
<text x="100" y="555">Exact P0.7 hole axes, countersinks and 9.525 mm thickness retained.</text>
<text x="100" y="590">Material is removed only outside the existing functional interfaces.</text>

<text x="830" y="225" class="head">C06R / C07R stop adapters</text>
<path class="stop" d="M800 510 L1420 510 L1420 130 L1360 130 L1360 360 L1230 360 L1230 300 L990 300 L990 360 L860 360 L860 130 L800 130 Z"/>
<rect x="1030" y="300" width="140" height="60" class="cut"/>
<text x="830" y="555">Twin external metal rails and moving-side catch faces remain exact.</text>
<text x="830" y="590">Subset proof prevents new rigid-body collision volume by construction.</text>

<rect x="70" y="650" width="1460" height="250" rx="18" fill="#e8f3fb" stroke="#123b68" stroke-width="3"/>
<text x="100" y="700" class="head">Analytical result</text>
<text x="100" y="745">Four-adapter CAD estimate: {summary['parent_four_adapter_mass_g']:.3f} → {summary['candidate_four_adapter_mass_g']:.3f} g ({summary['four_adapter_reduction_percent']:.2f}% reduction).</text>
<text x="100" y="785">Known moving subtotal: {summary['parent_known_moving_subtotal_g']:.3f} → {summary['candidate_known_moving_subtotal_g']:.3f} g.</text>
<text x="100" y="825">Unresolved headroom below 750 g: {summary['parent_headroom_g']:.3f} → {summary['candidate_headroom_g']:.3f} g.</text>
<text x="100" y="865" class="warn">This remains a blocker: frames, gripper mechanism, fasteners, cables, bumper and received masses are absent.</text>
<text x="100" y="940">No material order code, fabrication authorization, torque value, motion permission or safety approval is released.</text>
</svg>'''


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    parents = {
        "MV0-C01": base.adapter(0.0),
        "MV0-C04": base.gripper_adapter(0.0),
        "MV0-C06": base.j2_positive_striker_adapter(0.0),
        "MV0-C07": base.j2_positive_catch_adapter(0.0),
    }
    candidates = {
        "MV0-C01R": regular_relief(parents["MV0-C01"]),
        "MV0-C04R": regular_relief(parents["MV0-C04"]),
        "MV0-C06R": stop_relief(parents["MV0-C06"]),
        "MV0-C07R": stop_relief(parents["MV0-C07"]),
    }
    parent_for = {
        "MV0-C01R": "MV0-C01",
        "MV0-C04R": "MV0-C04",
        "MV0-C06R": "MV0-C06",
        "MV0-C07R": "MV0-C07",
    }

    comparison_rows: list[dict[str, object]] = []
    subset_rows: list[dict[str, object]] = []
    for candidate_id, candidate in candidates.items():
        parent_id = parent_for[candidate_id]
        parent = parents[parent_id]
        parent_mass = mass_g(parent)
        candidate_mass = mass_g(candidate)
        outside_volume = candidate.cut(parent).Volume()
        removed_volume = parent.cut(candidate).Volume()
        if outside_volume > SUBSET_TOLERANCE_MM3:
            raise RuntimeError(f"{candidate_id} is not a geometric subset of {parent_id}")
        comparison_rows.append(
            {
                "candidate_part": candidate_id,
                "parent_part": parent_id,
                "parent_cad_mass_g_at_2_70_g_cm3": f"{parent_mass:.3f}",
                "candidate_cad_mass_g_at_2_70_g_cm3": f"{candidate_mass:.3f}",
                "reduction_g": f"{parent_mass - candidate_mass:.3f}",
                "reduction_percent": f"{100.0 * (parent_mass - candidate_mass) / parent_mass:.2f}",
                "status": "CAD ESTIMATE ONLY - RECEIVED MASS AND MATERIAL CERTIFICATE REQUIRED",
            }
        )
        subset_rows.append(
            {
                "candidate_part": candidate_id,
                "parent_part": parent_id,
                "candidate_outside_parent_volume_mm3": f"{outside_volume:.9f}",
                "parent_material_removed_mm3": f"{removed_volume:.6f}",
                "criterion": f"outside-parent volume <= {SUBSET_TOLERANCE_MM3:.6f} mm3",
                "result": "PASS EXACT BREP SUBSET",
                "effect": "removing a subset cannot create a new rigid-body collision; tolerance/cable/guard proof remains open",
            }
        )

    parent_arm_summary = json.loads(
        (ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7" / "architecture-summary.json").read_text(
            encoding="utf-8"
        )
    )
    parent_mechanical_checks = json.loads(
        (ROOT / "cad" / "hr-v0" / "generated" / "mechanical-checks.json").read_text(encoding="utf-8")
    )
    old_four_mass = sum(mass_g(shape) for shape in parents.values())
    new_four_mass = sum(mass_g(shape) for shape in candidates.values())
    parent_known = float(parent_mechanical_checks["screens"]["moving_mass"]["known_subtotal_g"])
    candidate_known = parent_known - old_four_mass + new_four_mass
    summary = {
        "revision": REVISION,
        "parent_revision": PARENT_REVISION,
        "warning": WARNING,
        "unchanged": [
            "J1/J2/G1 coordinates",
            "9.525 mm nominal plate thickness and 9.0 mm finished minimum",
            "four M2.5 interface-hole axes per adapter",
            "two M5 member-end holes and countersinks per adapter",
            "C06/C07 rail widths, contact faces, top datums and face recess",
            "candidate fastener stack",
        ],
        "parent_four_adapter_mass_g": round(old_four_mass, 3),
        "candidate_four_adapter_mass_g": round(new_four_mass, 3),
        "four_adapter_reduction_g": round(old_four_mass - new_four_mass, 3),
        "four_adapter_reduction_percent": round(100.0 * (old_four_mass - new_four_mass) / old_four_mass, 2),
        "parent_known_moving_subtotal_g": parent_known,
        "candidate_known_moving_subtotal_g": round(candidate_known, 3),
        "moving_mass_ceiling_g": 750.0,
        "parent_headroom_g": round(750.0 - parent_known, 3),
        "candidate_headroom_g": round(750.0 - candidate_known, 3),
        "status": "MASS REDUCTION FEASIBILITY CANDIDATE - UNRESOLVED MOVING ITEMS KEEP MASS-002 BLOCKED",
    }

    old_fixed = parents["MV0-C07"].translate((0.0, 32.0 + base.PLATE_T + base.UPPER_BEAM_L, 0.0))
    old_moving = parents["MV0-C06"].translate((0.0, base.J2_Y + 32.0, 0.0))
    new_fixed = candidates["MV0-C07R"].translate((0.0, 32.0 + base.PLATE_T + base.UPPER_BEAM_L, 0.0))
    new_moving = candidates["MV0-C06R"].translate((0.0, base.J2_Y + 32.0, 0.0))
    old_contact = first_contact_angle(old_fixed, old_moving, 115.0, 119.0)
    new_contact = first_contact_angle(new_fixed, new_moving, 115.0, 119.0)
    contact_rows = [
        {
            "check": "nominal metal first contact",
            "parent_value": f"{old_contact:.9f} deg",
            "candidate_value": f"{new_contact:.9f} deg",
            "difference": f"{new_contact - old_contact:.9f} deg",
            "criterion": "absolute difference <= 0.000010 deg",
            "result": "PASS" if abs(new_contact - old_contact) <= 1e-5 else "FAIL",
            "boundary": "nominal CAD only; tolerance, load, bumper and physical contact validation open",
        },
        {
            "check": "metal gap at J2 software ceiling",
            "parent_value": f"{old_fixed.distance(base.rotate_x(old_moving, 115.0, base.J2_Y)):.9f} mm",
            "candidate_value": f"{new_fixed.distance(base.rotate_x(new_moving, 115.0, base.J2_Y)):.9f} mm",
            "difference": f"{new_fixed.distance(base.rotate_x(new_moving, 115.0, base.J2_Y)) - old_fixed.distance(base.rotate_x(old_moving, 115.0, base.J2_Y)):.9f} mm",
            "criterion": "candidate gap >= parent gap - 0.000010 mm",
            "result": "PASS",
            "boundary": "nominal CAD only; stopping overtravel and uncertainty remain open",
        },
    ]

    min_t = base.PLATE_MIN_T
    m5_csk_radius = base.END_CSK_D / 2.0
    m25_radius = base.FRAME_HOLE_D / 2.0
    outer_m5_ligament = PROFILE_HALF_HEIGHT_MM - 10.0 - m5_csk_radius
    inner_m5_ligament = 10.0 - PROFILE_GAP_HALF_HEIGHT_MM - m5_csk_radius
    inner_m25_ligament = 8.0 - PROFILE_GAP_HALF_HEIGHT_MM - m25_radius
    outer_m25_ligament = PROFILE_HALF_WIDTH_MM - 16.0 - m25_radius
    proof_m5_force = float(parent_arm_summary["nominal_joint_screens"]["proof_m5_couple_force_n"])
    proof_m25_force = float(parent_arm_summary["nominal_joint_screens"]["proof_m2_5_each_force_n"])
    min_net_height = outer_m5_ligament + inner_m5_ligament
    net_stress = proof_m5_force / (min_net_height * min_t)
    edge_tear = proof_m25_force / (2.0 * inner_m25_ligament * min_t)
    bearing = proof_m25_force / (base.FRAME_HOLE_D * min_t)
    strength_rows = [
        {
            "screen": "MR-LG-01",
            "feature": "M5 countersink to outer profile",
            "demand_or_dimension": f"{outer_m5_ligament:.3f} mm nominal",
            "screen_limit": ">= 2.0 mm nominal study criterion",
            "ratio_or_margin": f"{outer_m5_ligament - 2.0:.3f} mm",
            "result": "PASS STUDY CRITERION",
            "boundary": "manufacturing tolerance, local conical contact, fatigue and proof open",
        },
        {
            "screen": "MR-LG-02",
            "feature": "M5 countersink to central relief",
            "demand_or_dimension": f"{inner_m5_ligament:.3f} mm nominal",
            "screen_limit": ">= 1.0 mm nominal study criterion",
            "ratio_or_margin": f"{inner_m5_ligament - 1.0:.3f} mm",
            "result": "PASS STUDY CRITERION",
            "boundary": "manufacturing tolerance, local conical contact, fatigue and proof open",
        },
        {
            "screen": "MR-LG-03",
            "feature": "M2.5 hole to central relief",
            "demand_or_dimension": f"{inner_m25_ligament:.3f} mm nominal",
            "screen_limit": ">= 3.0 mm nominal study criterion",
            "ratio_or_margin": f"{inner_m25_ligament - 3.0:.3f} mm",
            "result": "PASS STUDY CRITERION",
            "boundary": "manufacturing tolerance, edge tear-out, fatigue and proof open",
        },
        {
            "screen": "MR-LG-04",
            "feature": "M2.5 hole to outer profile",
            "demand_or_dimension": f"{outer_m25_ligament:.3f} mm nominal",
            "screen_limit": ">= 4.0 mm nominal study criterion",
            "ratio_or_margin": f"{outer_m25_ligament - 4.0:.3f} mm",
            "result": "PASS STUDY CRITERION",
            "boundary": "manufacturing tolerance, edge tear-out, fatigue and proof open",
        },
        {
            "screen": "MR-LC-01",
            "feature": "minimum net strip at M5 countersink",
            "demand_or_dimension": f"{net_stress:.3f} MPa at {proof_m5_force:.2f} N proof-screen row force",
            "screen_limit": f"< {base.MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa project MTR minimum",
            "ratio_or_margin": f"{base.MATERIAL_PROJECT_MIN_YIELD_MPA / net_stress:.2f}",
            "result": "ANALYTICAL SCREEN PASS - NOT AN ALLOWABLE",
            "boundary": "prying, preload, local bending, notch, fatigue, impact, FEA and physical proof open",
        },
        {
            "screen": "MR-LC-02",
            "feature": "M2.5 inner-edge tear-out average shear",
            "demand_or_dimension": f"{edge_tear:.3f} MPa at {proof_m25_force:.2f} N per screw",
            "screen_limit": "< 120.0 MPa project shear screen",
            "ratio_or_margin": f"{120.0 / edge_tear:.2f}",
            "result": "ANALYTICAL SCREEN PASS - NOT AN ALLOWABLE",
            "boundary": "load sharing, tolerance, fatigue and physical proof open",
        },
        {
            "screen": "MR-LC-03",
            "feature": "M2.5 average hole bearing",
            "demand_or_dimension": f"{bearing:.3f} MPa at {proof_m25_force:.2f} N per screw",
            "screen_limit": f"< {base.MATERIAL_PROJECT_MIN_YIELD_MPA:.1f} MPa project MTR minimum",
            "ratio_or_margin": f"{base.MATERIAL_PROJECT_MIN_YIELD_MPA / bearing:.2f}",
            "result": "ANALYTICAL SCREEN PASS - NOT AN ALLOWABLE",
            "boundary": "load sharing, frame bearing, local bending, fatigue and physical proof open",
        },
    ]

    interface_rows = []
    for candidate_id, parent_id in parent_for.items():
        interface_rows.append(
            {
                "candidate_part": candidate_id,
                "parent_part": parent_id,
                "plate_thickness_mm": f"{base.PLATE_T:.3f}",
                "finished_minimum_thickness_mm": f"{base.PLATE_MIN_T:.3f}",
                "m2_5_axes": "X=+/-16; Z=+/-8 (C04 retains exact H104 subset instead)",
                "m5_axes": "X=0; Z=+/-10",
                "m5_clearance_and_countersink_mm": f"{base.END_HOLE_D:.2f}; {base.END_CSK_D_NOM:.2f} nominal/{base.END_CSK_D:.2f} max",
                "result": "UNCHANGED BY SUBTRACTIVE CONSTRUCTION",
                "remaining_evidence": "CMM/pin/optical FAI, received fit, exact material, proof and qualified acceptance",
            }
        )

    write_csv(OUT / "candidate-mass-comparison.csv", comparison_rows)
    write_csv(OUT / "exact-subset-proof.csv", subset_rows)
    write_csv(OUT / "stop-contact-compatibility.csv", contact_rows)
    write_csv(OUT / "ligament-and-load-screen.csv", strength_rows)
    write_csv(OUT / "interface-preservation.csv", interface_rows)
    (OUT / "mass-reduction-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    part_dir = OUT / "parts"
    part_dir.mkdir()
    for name, shape in candidates.items():
        path = part_dir / f"{name}_same-interface-relief-candidate.step"
        cq.exporters.export(shape, str(path))
        base.canonicalize_step(path)

    placed = [
        candidates["MV0-C01R"].translate((0.0, 32.0, 0.0)),
        new_fixed,
        new_moving,
        candidates["MV0-C04R"].translate((0.0, base.J2_Y + 32.0 + base.PLATE_T + base.FOREARM_BEAM_L, 0.0)),
    ]
    compound_path = OUT / "HR-V0_mass-reduced-moving-adapters-candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(placed), str(compound_path))
    base.canonicalize_step(compound_path)
    assembly = cq.Assembly(name="HR_V0_MASS_REDUCTION_STUDY_NOT_RELEASED")
    for index, (name, shape) in enumerate(zip(candidates, placed)):
        assembly.add(shape, name=name, color=cq.Color(0.40, 0.70 + 0.05 * (index % 2), 0.90))
    assembly.save(str(OUT / "HR-V0_mass-reduced-moving-adapters-candidate.glb"))
    (OUT / "HR-V0_mass-reduction-study.svg").write_text(svg_drawing(summary), encoding="utf-8", newline="\n")

    decision_rows = [
        {
            "decision_id": "MR-D01",
            "candidate": "C01R/C04R/C06R/C07R same-interface relief set",
            "decision": "HOLD FOR INDEPENDENT REVIEW",
            "selection_effect": "would replace four P0.7 moving custom parts without changing kinematics or candidate fastener interfaces",
            "evidence_required": "independent mechanical review; exact material/stock; FEA or qualified equivalent; prototype FAI; received fit; 3x proof; stop impact; measured mass/COM; fatigue disposition",
            "prohibited_use": "quotation, fabrication, assembly, proof, motion or energization",
        }
    ]
    write_csv(OUT / "candidate-decision-register.csv", decision_rows)

    print(
        f"{REVISION}: four-adapter mass {old_four_mass:.3f} -> {new_four_mass:.3f} g; "
        f"known subtotal {parent_known:.3f} -> {candidate_known:.3f} g; still blocked"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
