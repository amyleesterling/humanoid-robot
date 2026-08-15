#!/usr/bin/env python3
"""Fail-closed checks for the exact-import P0.8 HR-V0 arm candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as p07


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.8-dwg-integrated"
OLD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.7"
BINDING = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv"
REVISION = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
P07_GENERATOR_SHA256 = "5ff2f6055b28f1a41a427e3268eaceb6f179fc70abb020fecc9fcefeb545ff73"

OUTPUT_NAMES = {
    "MV0-C01": "MV0-C01_rect32x16_to_20-2040_countersunk_adapter.step",
    "MV0-C04": "MV0-C04_H104_to_20-2040_countersunk_adapter.step",
    "MV0-C05": "MV0-C05_S102_to_40-4040_side_slot_support.step",
    "MV0-C06": "MV0-C06_J2_positive_moving_striker_adapter.step",
    "MV0-C07": "MV0-C07_J2_positive_fixed_catch_adapter.step",
}

SMALL_AXES = {
    "MV0-C01": {(-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)},
    "MV0-C04": {(-12.0, -6.0), (-11.0, 8.0), (11.0, 8.0), (12.0, -6.0)},
    "MV0-C05": {(-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)},
    "MV0-C06": {(-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)},
    "MV0-C07": {(-16.0, -8.0), (-16.0, 8.0), (16.0, -8.0), (16.0, 8.0)},
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(left: float, right: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(float(left), float(right), abs_tol=tolerance, rel_tol=0.0)


def bbox(shape: cq.Shape) -> tuple[float, ...]:
    box = shape.BoundingBox()
    return tuple(float(value) for value in (box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax))


def same_tree(left: Path, right: Path, names: tuple[str, ...]) -> bool:
    return all(digest(left / name) == digest(right / name) for name in names)


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    need(digest(ROOT / "tools/generate_hr_v0_arm_architecture.py") == P07_GENERATOR_SHA256,
         "historical P0.7 generator changed")
    need(OUT.is_dir(), "P0.8 integrated output directory missing")
    if not OUT.is_dir():
        for message in failures:
            print(f"- {message}", file=sys.stderr)
        return 1

    old_files = {path.relative_to(OLD).as_posix() for path in OLD.rglob("*") if path.is_file()}
    new_files = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(new_files == old_files | {"controlled-custom-part-integration.csv", "integration-status.json"},
         "P0.8 output membership differs from the P0.7 product plus two integration records")

    status = json.loads((OUT / "integration-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == REVISION and status.get("round") == "R214", "integration identity changed")
    need(status.get("source_binding") == BINDING.relative_to(ROOT).as_posix(), "source binding path changed")
    need(status.get("source_binding_sha256") == digest(BINDING), "source binding hash changed")
    need(status.get("direct_controlled_step_import") is True and status.get("controlled_part_count") == 5,
         "direct five-part import is not explicit")
    need(status.get("modeled_countersink") == {"diameter_mm": 11.3, "axial_depth_mm": 2.9, "included_angle_deg": 90.0},
         "nominal modeled countersink changed")
    need(status.get("independent_maximum_screens") == {"diameter_mm": 11.4, "axial_depth_mm": 3.1},
         "independent countersink screens changed")
    for field in ("physical_evidence_complete", "qualified_review_complete", "fabrication_authorized",
                  "assembly_authorized", "motion_authorized", "energization_authorized"):
        need(status.get(field) is False, f"{field} is not fail-closed")
    need(status.get("warning") == WARNING, "integration warning changed")
    assembly_path = ROOT / status.get("assembly_step", "")
    need(assembly_path.is_file() and status.get("assembly_step_sha256") == digest(assembly_path),
         "combined assembly identity changed")

    binding = {row["part_id"]: row for row in rows(BINDING)}
    integration = {row["part_id"]: row for row in rows(OUT / "controlled-custom-part-integration.csv")}
    need(set(binding) == set(OUTPUT_NAMES) == set(integration), "controlled part membership changed")
    for part_id, output_name in OUTPUT_NAMES.items():
        if part_id not in binding or part_id not in integration:
            continue
        source = ROOT / binding[part_id]["step_path"]
        output = OUT / "parts" / output_name
        record = integration[part_id]
        need(source.is_file() and output.is_file(), f"{part_id} STEP missing")
        if source.is_file() and output.is_file():
            expected_hash = binding[part_id]["step_sha256"]
            need(digest(source) == expected_hash == digest(output), f"{part_id} exact STEP identity not preserved")
            need(record.get("controlled_step_sha256") == expected_hash == record.get("integrated_part_sha256"),
                 f"{part_id} integration record hash mismatch")
            shape = cq.importers.importStep(str(output)).val()
            need(p07.cylindrical_axes(shape, radius=1.35, axis="Y") == SMALL_AXES[part_id],
                 f"{part_id} small-hole axes changed")
            if part_id == "MV0-C05":
                need(p07.cylindrical_axes(shape, radius=4.25, axis="Y") == {(0.0, -30.0), (0.0, 30.0)},
                     "C05 M8 axes changed")
            else:
                need(p07.cylindrical_axes(shape, radius=2.75, axis="Y") == {(0.0, -10.0), (0.0, 10.0)},
                     f"{part_id} M5 axes changed")
        need(record.get("assembly_use") == "DIRECT IMPORT AT EXISTING P0.7 TRANSFORM",
             f"{part_id} assembly-use provenance changed")
        need(record.get("fabrication_authorized") == "FALSE" and record.get("warning") == WARNING,
             f"{part_id} authorization boundary changed")

    summary = json.loads((OUT / "architecture-summary.json").read_text(encoding="utf-8"))
    need(summary.get("revision") == REVISION, "architecture summary revision changed")
    csk = summary.get("candidate_geometry_mm", {}).get("m5_countersink", {})
    need(csk == {
        "finished_diameter_range": [11.3, 11.4],
        "modeled_diameter": 11.3,
        "modeled_axial_depth": 2.9,
        "modeled_included_angle_deg": 90.0,
        "maximum_diameter_screen": 11.4,
        "maximum_depth_screen": 3.1,
        "screen_semantics": "independent conservative tolerance/inspection and clearance/residual-material screens; not the nominal STEP solid",
    }, "nominal-versus-maximum countersink semantics changed")
    provenance = summary.get("controlled_custom_part_integration", {})
    need(provenance.get("direct_imported_part_ids") == sorted(OUTPUT_NAMES), "summary direct-import membership changed")
    need(provenance.get("source_binding_sha256") == digest(BINDING), "summary source-binding hash changed")

    p07_summary = json.loads((OLD / "architecture-summary.json").read_text(encoding="utf-8"))
    p07_masses = p07_summary["mass_and_load_screen"]
    p08_masses = summary["mass_and_load_screen"]
    old_custom_mass = sum(float(p07_masses[key]) for key in (
        "one_adapter_candidate_mass_g", "gripper_adapter_candidate_mass_g",
        "j2_moving_striker_adapter_candidate_mass_g", "j2_fixed_catch_adapter_candidate_mass_g"))
    new_custom_mass = sum(float(p08_masses[key]) for key in (
        "one_adapter_candidate_mass_g", "gripper_adapter_candidate_mass_g",
        "j2_moving_striker_adapter_candidate_mass_g", "j2_fixed_catch_adapter_candidate_mass_g"))
    need(close(new_custom_mass - old_custom_mass, 0.196, 0.002), "integrated rounded custom-part mass delta changed")
    need(p08_masses.get("allocated_shoulder_gravity_nm") == 2.018 and p08_masses.get("allocated_elbow_gravity_nm") == 0.515,
         "rounded joint gravity screen changed")
    need("frames, fasteners, cables and final gripper mechanism remain incomplete" in p08_masses.get("status", ""),
         "mass-property incompleteness boundary lost")

    need(rows(OUT / "transform-schedule.csv") == rows(OLD / "transform-schedule.csv"),
         "P0.7-to-P0.8 transform schedule is not row-for-row identical")
    need(rows(OUT / "interface-schedule.csv") == rows(OLD / "interface-schedule.csv"),
         "P0.7-to-P0.8 interface schedule changed")
    transform_by_item = {row["item"]: row for row in rows(OUT / "transform-schedule.csv")}
    placements = {
        "MV0-C05 shoulder support": ("0", "-61.025", "-40.0"),
        "MV0-C07 fixed catch adapter": ("0", "141.525", "0"),
        "MV0-C06 moving striker adapter": ("0", "32.0", "0"),
    }
    for item, expected in placements.items():
        row = transform_by_item.get(item, {})
        need((row.get("tx_mm"), row.get("ty_mm"), row.get("tz_mm")) == expected,
             f"{item} placement changed")

    for filename in ("collision-sweep.csv", "continuous-clearance-summary.csv", "continuous-clearance-cells.csv",
                     "j2-positive-stop-sweep.csv", "j2-positive-stop-tolerance-screen.csv"):
        need(digest(OUT / filename) == digest(OLD / filename), f"{filename} differs from unchanged-envelope P0.7 evidence")

    collision = rows(OUT / "collision-sweep.csv")
    need(len(collision) == 40001, "collision sweep row count changed")
    need(sum(row["result"] == "COLLISION" for row in collision) == 1267, "collision classification count changed")
    need(all(row["result"] == "PASS" and float(row["sampled_pairwise_intersection_mm3"]) <= 1e-5
             for row in collision if float(row["j2_internal_deg"]) <= 115.0),
         "collision exists inside the candidate soft limit")

    continuous = json.loads((OUT / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    need(continuous.get("revision") == REVISION, "continuous-certificate revision changed")
    need(continuous.get("joint_domain_deg") == {"j1": [-20.0, 70.0], "j2": [15.0, 120.0]},
         "continuous-certificate domain changed")
    need(continuous.get("pair_count") == 69 and continuous.get("certified_leaf_cell_count") == 135,
         "continuous-certificate coverage changed")
    need(float(continuous.get("minimum_guaranteed_clearance_mm", 0)) >= 0.75,
         "continuous minimum guaranteed clearance fell below 0.75 mm")
    need(continuous.get("continuous_first_contact_j2_deg_numeric") == 121.643289,
         "first nominal body-contact angle changed")

    stop = json.loads((OUT / "j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    need(stop.get("parent_arm_revision") == REVISION and stop.get("target_metal_contact_deg") == 118.0,
         "positive-stop parent/target changed")
    need(abs(float(stop.get("nominal_metal_contact_deg", 0.0)) - 118.0) <= 0.002,
         "positive-stop nominal contact changed")
    need("PHYSICAL TEST" in stop.get("status", ""), "positive-stop physical-test hold lost")

    old_assembly = cq.importers.importStep(str(OLD / "HR-V0_arm_architecture_candidate.step")).val()
    new_assembly = cq.importers.importStep(str(OUT / "HR-V0_arm_architecture_candidate.step")).val()
    need(all(close(left, right, 1e-6) for left, right in zip(bbox(old_assembly), bbox(new_assembly))),
         "complete-arm external bounding box changed")
    exact_mass_delta = json.loads((ROOT / "release/hr-v0/countersink-mbd-p0.1/package-status.json").read_text(encoding="utf-8"))[
        "total_candidate_mass_delta_g_at_2_70_g_cm3"
    ]
    expected_volume_delta = float(exact_mass_delta) / 2.70 * 1000.0
    need(close(float(new_assembly.Volume()) - float(old_assembly.Volume()), expected_volume_delta, 0.002),
         "complete-arm volume delta does not equal the four controlled countersink corrections")

    need(same_tree(OUT, OLD, (
        "tool-access-screen.csv", "adapter-drawing-controls.csv", "new-interface-drawing-controls.csv",
        "fastener-candidate-schedule.csv", "hard-stop-allocation.csv")),
         "conservative screen/control records changed unexpectedly")
    need((OUT / "HR-V0_arm_architecture_candidate.step").stat().st_size > 1_000_000 and
         (OUT / "HR-V0_arm_architecture_candidate.glb").stat().st_size > 100_000,
         "combined STEP/GLB unexpectedly small")

    if failures:
        print("HR-V0 P0.8 integrated arm validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 P0.8 integrated arm validation: PASS")
    print("5 exact R213 STEP identities; unchanged transforms; 40,001-pose collision sweep; 69-pair continuous certificate; J2 stop regenerated")
    print("PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
