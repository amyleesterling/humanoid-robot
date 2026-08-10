#!/usr/bin/env python3
"""Fail-closed checks for the P1.1 X430 lowered-forearm candidate."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p1.1-x430-lowered-forearm"
DOC = ROOT / "docs" / "hr-v0-x430-lowered-forearm-p1.1.md"
GUIDE = ROOT / "release" / "hr-v0" / "arm-architecture-p1.1-x430-lowered-forearm" / "index.html"
REVISION = "HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(value: object, expected: float, tolerance: float = 0.002) -> bool:
    return math.isclose(float(value), expected, abs_tol=tolerance)


def main() -> int:
    errors: list[str] = []
    expected = {
        "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.glb",
        "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.step",
        "P11-C02_lowered-forearm-moving-striker-review-drawing.svg",
        "architecture-holds.csv",
        "architecture-summary.json",
        "certificate-supersession-basis.csv",
        "continuous-clearance-analysis.json",
        "continuous-clearance-cells.csv",
        "continuous-clearance-summary.csv",
        "critical-clearance-and-stop-sweep.csv",
        "fastener-feature-screen.csv",
        "mass-comparison.csv",
        "package-status.json",
        "parts/P11-C02_X430_lowered-forearm-moving-striker.step",
        "stop-sequencing-tolerance-budget.csv",
        "transform-register.csv",
    }
    actual = {str(path.relative_to(PKG)).replace("\\", "/") for path in PKG.rglob("*") if path.is_file()}
    if actual != expected:
        errors.append(f"package file set mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")

    try:
        summary = json.loads((PKG / "architecture-summary.json").read_text(encoding="utf-8"))
        status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
        analysis = json.loads((PKG / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
        pairs = rows("continuous-clearance-summary.csv")
        cells = rows("continuous-clearance-cells.csv")
        sweep = rows("critical-clearance-and-stop-sweep.csv")
        budget = rows("stop-sequencing-tolerance-budget.csv")
        features = rows("fastener-feature-screen.csv")
        transforms = rows("transform-register.csv")
        holds = rows("architecture-holds.csv")
        basis = rows("certificate-supersession-basis.csv")
    except Exception as exc:
        print(f"P1.1 package parse failure: {exc}")
        return 1

    if summary.get("revision") != REVISION or status.get("revision") != REVISION or analysis.get("revision") != REVISION:
        errors.append("revision mismatch")
    warning = summary.get("warning", "")
    if "NOT APPROVED" not in warning or "ENERGIZATION" not in warning:
        errors.append("preliminary warning missing")
    if summary.get("configuration_disposition") != "P1.1 comparison only; P0.7 remains controlled; X430 is not selected":
        errors.append("configuration disposition changed")

    transform = summary.get("transform_controls", {})
    feature = summary.get("feature_controls", {})
    if not close(transform.get("j2_axis_y_mm", -1), 191.55) or not close(transform.get("moving_face_y_mm", -1), 219.55):
        errors.append("J2-to-H101 moving-face transform changed")
    if not close(transform.get("forearm_z_offset_mm", 0), -7.0):
        errors.append("forearm offset is not -7 mm")
    if feature.get("base_z_mm") != [-27.0, 13.0] or feature.get("member_hole_z_mm") != [3.0, -17.0]:
        errors.append("lowered plate/member geometry changed")
    if not close(feature.get("nominal_minimum_countersink_edge_land_mm", 0), 4.3):
        errors.append("countersink edge land changed")

    continuous = summary.get("continuous_clearance", {})
    expected_counts = {"pair_count": 69, "retained_pair_count": 30, "recomputed_changed_pair_count": 39, "leaf_cell_count": 140, "exact_brep_distance_calls": 106}
    for key, expected_value in expected_counts.items():
        if continuous.get(key) != expected_value:
            errors.append(f"{key} expected {expected_value}, got {continuous.get(key)}")
    if len(pairs) != 69 or len(cells) != 140:
        errors.append("certificate row counts changed")
    if sum(row["evidence_origin"].startswith("P0.9") for row in pairs) != 30 or sum(row["evidence_origin"].startswith("P1.1") for row in pairs) != 39:
        errors.append("retained/recomputed origin counts changed")
    critical = [row for row in pairs if row["pair_id"] == "UPPER_FORE:J2_X430:P11_LOWERED_STRIKER"]
    if len(critical) != 1 or float(critical[0]["minimum_guaranteed_clearance_mm"]) < 4.75 or critical[0]["required_clearance_mm"] != "4.750000000":
        errors.append("critical X430/striker continuous certificate failed")
    if not close(continuous.get("minimum_guaranteed_all_pairs_mm", 0), 1.313579) or not close(continuous.get("critical_x430_striker_guaranteed_clearance_mm", 0), 4.798163):
        errors.append("continuous minima changed")
    if len(basis) != 2 or [int(row["pair_count"]) for row in basis] != [30, 39]:
        errors.append("certificate supersession basis changed")

    stop = summary.get("stop_sequencing", {})
    stop_expected = {
        "nominal_first_contact_deg": 117.999977,
        "x430_clearance_at_soft_limit_mm": 4.875499,
        "x430_clearance_at_stop_contact_mm": 4.369402,
        "stop_gap_at_soft_limit_mm": 1.913782,
        "required_physical_residual_at_stop_mm": 1.5,
        "available_adverse_variation_mm": 2.869402,
        "allocated_adverse_variation_mm": 2.5,
        "unallocated_margin_mm": 0.369402,
    }
    for key, expected_value in stop_expected.items():
        if not close(stop.get(key, -100), expected_value):
            errors.append(f"{key} changed")
    if len(sweep) != 413 or sweep[0]["j2_deg"] != "15.00" or sweep[-1]["j2_deg"] != "118.00":
        errors.append("exact stop sweep range/count changed")
    sweep_by_q = {row["j2_deg"]: row for row in sweep}
    if not close(sweep_by_q.get("115.00", {}).get("x430_to_striker_clearance_mm", -1), 4.875499) or not close(sweep_by_q.get("118.00", {}).get("x430_to_striker_clearance_mm", -1), 4.369402):
        errors.append("exact sweep critical clearances changed")
    if sweep_by_q.get("118.00", {}).get("positive_stop_state") != "CONTACT":
        errors.append("nominal stop contact missing")

    if len(budget) != 7 or not close(sum(float(row["maximum_adverse_contribution_mm"]) for row in budget[:-1]), 2.5):
        errors.append("tolerance allocation count/sum changed")
    if any("UNVERIFIED" not in row["state"] for row in budget):
        errors.append("tolerance budget overclaims verification")
    if len(features) != 4 or any("PASS NOMINAL" not in row["status"] or "OPEN" not in row["status"] for row in features):
        errors.append("fastener feature screen state changed")
    if len(transforms) != 3 or transforms[1]["y_mm"] != "219.550" or transforms[2]["z_mm"] != "-7.000":
        errors.append("transform regression register changed")
    if len(holds) != 12 or sum(row["state"] == "OPEN" for row in holds) != 8 or sum(row["state"] == "PARTIAL" for row in holds) != 4:
        errors.append("hold register does not remain 8 OPEN / 4 PARTIAL")

    flags = status.get("release_flags", {})
    if set(flags) != {"supersedes_p0_7", "supersedes_p1_0", "x430_selected", "quotation_authorized", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "motion_authorized", "connection_authorized", "energization_authorized"} or any(flags.values()):
        errors.append("release flags are missing or non-false")
    for path in (DOC, GUIDE):
        if not path.exists():
            errors.append(f"missing synchronized artifact {path.relative_to(ROOT)}")
        elif "NOT APPROVED" not in path.read_text(encoding="utf-8") or REVISION not in path.read_text(encoding="utf-8"):
            errors.append(f"warning/revision missing from {path.relative_to(ROOT)}")
    if (PKG / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.glb").stat().st_size < 1_000_000:
        errors.append("GLB is unexpectedly small")
    if (PKG / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.step").stat().st_size < 1_000_000:
        errors.append("STEP is unexpectedly small")

    if errors:
        print("HR-V0 P1.1 lowered-forearm check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 P1.1 lowered-forearm check: PASS")
    print("30 unchanged certificates retained; 39 changed-solid pairs recomputed; 69 complete pairs")
    print("4.798163 mm certified X430/striker floor; 4.369402 mm nominal clearance at 118 deg contact")
    print("2.500 mm unverified allocation; 1.500 mm residual requirement; 0.369402 mm nominal allocation margin")
    print("P0.7 remains controlled; P1.1/X430 unselected; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
