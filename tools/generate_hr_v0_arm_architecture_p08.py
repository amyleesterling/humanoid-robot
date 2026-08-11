#!/usr/bin/env python3
"""Generate the complete P0.8 arm using the R213 drawing-controlled solids.

This wrapper deliberately leaves the historical P0.7 output untouched. The
base generator reads its geometry constants at runtime, so the wrapper can
model the corrected nominal 90-degree countersink while retaining the P0.7
upper-bound clearance and residual-material screens.
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


ROOT = Path(__file__).resolve().parents[1]
REVISION = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
BINDING = ROOT / "bom" / "hr-v0-mechanical-custom-part-binding-p0.2.csv"
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.8-dwg-integrated"

OUTPUT_NAMES = {
    "MV0-C01": "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step",
    "MV0-C04": "MV0-C04_H104_to_20-2040_countersunk_adapter.step",
    "MV0-C05": "MV0-C05_S102_to_40-4040_side_slot_support.step",
    "MV0-C06": "MV0-C06_J2_positive_moving_striker_adapter.step",
    "MV0-C07": "MV0-C07_J2_positive_fixed_catch_adapter.step",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_binding() -> dict[str, dict[str, str]]:
    with BINDING.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_part = {row["part_id"]: row for row in rows}
    if set(by_part) != set(OUTPUT_NAMES):
        raise RuntimeError(f"R213 binding membership changed: {sorted(by_part)}")
    for part_id, row in by_part.items():
        source = ROOT / row["step_path"]
        if row["architecture_id"] != "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE":
            raise RuntimeError(f"{part_id} architecture binding changed")
        if not source.is_file() or digest(source) != row["step_sha256"]:
            raise RuntimeError(f"{part_id} controlled STEP identity mismatch")
        if row["fabrication_authorized"] != "FALSE" or row["quotation_authorized"] != "FALSE":
            raise RuntimeError(f"{part_id} authorization boundary changed")
    return by_part


def translated(shape: cq.Shape, y0: float) -> cq.Shape:
    return shape if math.isclose(y0, 0.0) else shape.translate((0.0, y0, 0.0))


def main() -> int:
    binding = read_binding()
    sources = {part_id: ROOT / row["step_path"] for part_id, row in binding.items()}
    shapes = {part_id: cq.importers.importStep(str(path)).val() for part_id, path in sources.items()}

    arm.OUT = OUT
    arm.REVISION = REVISION

    # Use the exact R213-controlled files in the assembly and collision sets.
    # Only non-nominal stop-tolerance variants return to the parametric builder.
    original_striker = arm.j2_positive_striker_adapter
    original_catch = arm.j2_positive_catch_adapter
    arm.adapter = lambda y0: translated(shapes["MV0-C01"], y0)
    arm.gripper_adapter = lambda y0: translated(shapes["MV0-C04"], y0)
    arm.shoulder_support_plate = lambda: shapes["MV0-C05"]

    def bound_striker(y0: float, top_z_mm: float = arm.STOP_STRIKER_TOP_Z_MM) -> cq.Shape:
        if math.isclose(top_z_mm, arm.STOP_STRIKER_TOP_Z_MM):
            return translated(shapes["MV0-C06"], y0)
        old_diameter, old_depth = arm.END_CSK_D, arm.END_CSK_DEPTH
        try:
            arm.END_CSK_D, arm.END_CSK_DEPTH = 11.30, 2.90
            return original_striker(y0, top_z_mm)
        finally:
            arm.END_CSK_D, arm.END_CSK_DEPTH = old_diameter, old_depth

    def bound_catch(y0: float, face_recess_mm: float = arm.STOP_CATCH_FACE_RECESS_MM) -> cq.Shape:
        if math.isclose(face_recess_mm, arm.STOP_CATCH_FACE_RECESS_MM):
            return translated(shapes["MV0-C07"], y0)
        old_diameter, old_depth = arm.END_CSK_D, arm.END_CSK_DEPTH
        try:
            arm.END_CSK_D, arm.END_CSK_DEPTH = 11.30, 2.90
            return original_catch(y0, face_recess_mm)
        finally:
            arm.END_CSK_D, arm.END_CSK_DEPTH = old_diameter, old_depth

    arm.j2_positive_striker_adapter = bound_striker
    arm.j2_positive_catch_adapter = bound_catch

    result = arm.main()
    if result:
        return result

    # Preserve exact manufacturing identity in the successor part directory;
    # the combined assembly was already built from these imported shapes.
    integration_rows: list[dict[str, str]] = []
    for part_id, output_name in OUTPUT_NAMES.items():
        source = sources[part_id]
        output = OUT / "parts" / output_name
        shutil.copyfile(source, output)
        integration_rows.append({
            "part_id": part_id,
            "r213_binding_path": BINDING.relative_to(ROOT).as_posix(),
            "controlled_step_path": source.relative_to(ROOT).as_posix(),
            "controlled_step_sha256": digest(source),
            "integrated_part_path": output.relative_to(ROOT).as_posix(),
            "integrated_part_sha256": digest(output),
            "assembly_use": "DIRECT IMPORT AT EXISTING P0.7 TRANSFORM",
            "configuration_state": "CURRENT HELD DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED",
            "fabrication_authorized": "FALSE",
            "warning": WARNING,
        })
    with (OUT / "controlled-custom-part-integration.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(integration_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(integration_rows)

    summary_path = OUT / "architecture-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["disposition"] = (
        "complete arm/column candidate built by direct import of all five R213-controlled custom-part STEP identities at the unchanged P0.7 transforms; "
        "nominal model-space collision and stop evidence regenerated; material, received fit, DFM, FAI, physical proof, cable, guard and qualified release gates remain open; no part or assembly released"
    )
    summary["candidate_geometry_mm"]["m5_countersink"] = {
        "finished_diameter_range": [11.30, 11.40],
        "modeled_diameter": 11.30,
        "modeled_axial_depth": 2.90,
        "modeled_included_angle_deg": 90.0,
        "maximum_diameter_screen": 11.40,
        "maximum_depth_screen": 3.10,
        "screen_semantics": "independent conservative tolerance/inspection and clearance/residual-material screens; not the nominal STEP solid",
    }
    summary["controlled_custom_part_integration"] = {
        "source_binding": BINDING.relative_to(ROOT).as_posix(),
        "source_binding_sha256": digest(BINDING),
        "direct_imported_part_ids": sorted(OUTPUT_NAMES),
        "transform_basis": "unchanged HR-V0-ARM-ARCH-P0.7 transform-schedule.csv",
        "integration_register": (OUT / "controlled-custom-part-integration.csv").relative_to(ROOT).as_posix(),
    }
    summary["open_release_items"].insert(
        0,
        "independent qualified review of direct R213 STEP identity integration and successor collision/stop evidence",
    )
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    status = {
        "identifier": REVISION,
        "round": "R214",
        "source_binding": BINDING.relative_to(ROOT).as_posix(),
        "source_binding_sha256": digest(BINDING),
        "direct_controlled_step_import": True,
        "controlled_part_count": len(integration_rows),
        "historical_transform_basis": "HR-V0-ARM-ARCH-P0.7",
        "modeled_countersink": {"diameter_mm": 11.30, "axial_depth_mm": 2.90, "included_angle_deg": 90.0},
        "independent_maximum_screens": {"diameter_mm": 11.40, "axial_depth_mm": 3.10},
        "assembly_step": (OUT / "HR-V0_arm_architecture_candidate.step").relative_to(ROOT).as_posix(),
        "assembly_step_sha256": digest(OUT / "HR-V0_arm_architecture_candidate.step"),
        "physical_evidence_complete": False,
        "qualified_review_complete": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "integration-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
