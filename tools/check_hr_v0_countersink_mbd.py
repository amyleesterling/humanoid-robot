#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-CSK-MBD-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "countersink-mbd-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cone_major_edges(shape: cq.Shape) -> list[tuple[float, float, float]]:
    found: set[tuple[float, float, float]] = set()
    for face in shape.Faces():
        if face.geomType() != "CONE":
            continue
        center = face.Center()
        for edge in face.Edges():
            try:
                radius = float(edge.radius())
            except Exception:
                continue
            if math.isclose(radius, 5.65, abs_tol=1e-6):
                found.add((round(center.x, 6), round(center.z, 6), round(radius, 6)))
    return sorted(found)


def main() -> int:
    errors: list[str] = []
    comparisons = rows("part-comparison.csv")
    features = rows("feature-certificate.csv")
    decisions = rows("decision-register.csv")
    findings = rows("finding-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-countersink-mbd-p0.1.md").read_text(encoding="utf-8")

    expected_parts = ["MV0-C01", "MV0-C04", "MV0-C06", "MV0-C07"]
    if [row.get("part_id") for row in comparisons] != expected_parts:
        errors.append("comparison rows are not exactly C01/C04/C06/C07")
    if len(features) != 8 or len(decisions) != 5 or len(findings) != 3:
        errors.append(f"unexpected counts: features={len(features)} decisions={len(decisions)} findings={len(findings)}")

    for row in comparisons:
        part_id = row.get("part_id", "")
        source = ROOT / row.get("p0_7_source_path", "")
        candidate = ROOT / row.get("p0_8_candidate_path", "")
        if not source.is_file() or digest(source) != row.get("p0_7_sha256"):
            errors.append(f"{part_id} P0.7 source identity mismatch")
            continue
        if not candidate.is_file() or digest(candidate) != row.get("p0_8_candidate_sha256"):
            errors.append(f"{part_id} P0.8 candidate identity mismatch")
            continue
        source_shape = cq.importers.importStep(str(source)).val()
        candidate_shape = cq.importers.importStep(str(candidate)).val()
        if len(source_shape.Solids()) != 1 or len(candidate_shape.Solids()) != 1:
            errors.append(f"{part_id} source/candidate is not one solid")
        if row.get("maximum_bbox_delta_mm") != "0.0":
            errors.append(f"{part_id} bounding envelope changed")
        if float(row.get("candidate_added_material_mm3", "0")) <= 0.0:
            errors.append(f"{part_id} candidate did not add the expected bounded material")
        if row.get("selection_state") != "NONSELECTED CANDIDATE" or row.get("warning") != WARNING:
            errors.append(f"{part_id} release state changed")
        edges = cone_major_edges(candidate_shape)
        if edges != [(0.0, -10.0, 5.65), (0.0, 10.0, 5.65)]:
            errors.append(f"{part_id} candidate cone edges changed: {edges}")

    for row in features:
        numeric_expected = {
            "through_hole_diameter_mm": 5.5,
            "p0_7_modeled_major_diameter_mm": 11.4,
            "p0_7_modeled_axial_depth_mm": 3.1,
            "p0_7_derived_included_angle_deg": 87.159469,
            "p0_8_nominal_major_diameter_mm": 11.3,
            "p0_8_nominal_axial_depth_mm": 2.9,
            "p0_8_derived_included_angle_deg": 90.0,
            "worst_case_diameter_screen_mm": 11.4,
            "worst_case_depth_screen_mm": 3.1,
        }
        for key, expected in numeric_expected.items():
            if not math.isclose(float(row.get(key, "nan")), expected, abs_tol=1e-6):
                errors.append(f"{row.get('feature_id')} {key} changed")
        if row.get("selection_state") != "NONSELECTED CANDIDATE" or row.get("warning") != WARNING:
            errors.append(f"{row.get('feature_id')} release state changed")

    if any(row.get("state") not in {"SELECTION REQUIRED", "HOLD"} or row.get("warning") != WARNING for row in decisions):
        errors.append("decision register is not fail closed")
    if [row.get("priority") for row in findings] != ["MAJOR", "MAJOR", "BLOCKER"]:
        errors.append("finding priorities changed")
    if any(row.get("status") not in {"CANDIDATE CORRECTION - INDEPENDENT REVIEW OPEN", "OPEN"} or row.get("warning") != WARNING for row in findings):
        errors.append("finding register is not open")

    expected_status = {
        "part_count": 4,
        "feature_count": 8,
        "decision_count": 5,
        "finding_count": 3,
        "p0_7_remains_controlled": True,
        "candidate_selected": False,
        "supplier_contacted": False,
        "quotation_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
    }
    for key, expected in expected_status.items():
        if status.get(key) != expected:
            errors.append(f"package status {key} != {expected}")
    if not math.isclose(status.get("p0_7_derived_angle_deg", 0.0), 87.159469, abs_tol=1e-6) or status.get("p0_8_derived_angle_deg") != 90.0:
        errors.append("package angle summary changed")
    if status.get("warning") != WARNING:
        errors.append("package warning changed")

    for token in ("font:16px", "font-size:14px", "font-size:13px", "One countersink, two different meanings", "P0.7 remains controlled", "0</strong>fabrication releases", "decision-register.csv"):
        if token not in guide:
            errors.append(f"guide omits {token!r}")
    for token in ("87.159469° cone", "nominal axial depth 2.90 mm", "P0.7 remains the controlled architecture", "does not prove manufacturing capability"):
        if token not in doc:
            errors.append(f"document omits {token!r}")

    if errors:
        print("HR-V0 countersink MBD check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 countersink MBD P0.1 check passed: 4 candidate STEP parts; 8 nominal 90-degree countersinks; unchanged bounding envelopes; 5 decisions; 3 open findings")
    print("Candidate is not selected; no quotation, fabrication, assembly, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
