#!/usr/bin/env python3
"""Fail-closed validation for the P1.0 X430 clearance candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p1.0-x430-clearance"
P09 = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.9-x430"
DOC = ROOT / "docs" / "hr-v0-x430-arm-p1.0.md"
GUIDE = ROOT / "release" / "hr-v0" / "arm-architecture-p1.0-x430-clearance" / "index.html"
REVISION = "HR-V0-ARM-ARCH-P1.0-X430-CLEARANCE-CANDIDATE"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(value: object, expected: float, tolerance: float = 0.002) -> bool:
    return math.isclose(float(value), expected, abs_tol=tolerance)


def main() -> int:
    errors: list[str] = []
    summary = json.loads((PKG / "architecture-summary.json").read_text(encoding="utf-8"))
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    continuous = json.loads((PKG / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    pairs = rows("continuous-clearance-summary.csv")
    cells = rows("continuous-clearance-cells.csv")
    sweep = rows("critical-clearance-and-stop-sweep.csv")
    basis = rows("certificate-supersession-basis.csv")
    budget = rows("stop-sequencing-tolerance-budget.csv")
    mass = rows("mass-comparison.csv")
    holds = rows("architecture-holds.csv")

    if summary.get("revision") != REVISION or status.get("revision") != REVISION:
        errors.append("revision identity changed")
    if status.get("state") != "COMPARISON_CANDIDATE_NOT_SELECTED":
        errors.append("candidate selection state changed")
    if summary.get("configuration_disposition") != "P1.0 comparison only; P0.7 remains controlled; P0.9 remains prior comparison; XM430 is not selected":
        errors.append("configuration disposition changed")
    flags = summary.get("release_flags", {})
    if len(flags) != 10 or any(value is not False for value in flags.values()):
        errors.append("one or more release flags are absent or not false")

    contour = summary.get("contour_mm", {})
    for key, expected in {"base_top_z": 15.0, "m5_boss_top_z": 17.0, "m5_boss_half_width": 8.0, "original_stop_surface_preserved_from_z": 19.9167}.items():
        if not close(contour.get(key, -1), expected):
            errors.append(f"contour control changed: {key}")
    sequencing = summary.get("stop_sequencing", {})
    for key, expected in {
        "soft_limit_deg": 115.0,
        "nominal_first_contact_deg": 118.0,
        "x430_clearance_at_soft_limit_mm": 3.942108,
        "x430_clearance_at_stop_contact_mm": 2.491516,
        "stop_gap_at_soft_limit_mm": 1.913782,
        "required_physical_residual_at_stop_mm": 1.0,
        "maximum_combined_adverse_variation_mm": 1.491516,
    }.items():
        if not close(sequencing.get(key, -1), expected):
            errors.append(f"stop-sequencing value changed: {key}")

    cert = summary.get("continuous_clearance", {})
    expected_cert = {
        "retained_pair_required_clearance_mm": 0.75,
        "changed_striker_pair_required_clearance_mm": 3.0,
        "minimum_guaranteed_all_pairs_mm": 1.040321,
        "minimum_guaranteed_changed_striker_pairs_mm": 3.242248,
    }
    for key, expected in expected_cert.items():
        if not close(cert.get(key, -1), expected, 0.000002):
            errors.append(f"continuous result changed: {key}")
    for key, expected in {"pair_count": 69, "retained_pair_count": 60, "recomputed_changed_pair_count": 9, "leaf_cell_count": 136, "exact_brep_distance_calls": 94}.items():
        if cert.get(key) != expected:
            errors.append(f"continuous accounting changed: {key}")
    if continuous.get("joint_domain_deg") != {"j1": [-20.0, 70.0], "j2": [15.0, 115.0]}:
        errors.append("continuous domain changed")
    if len(pairs) != 69 or len(cells) != 136:
        errors.append("continuous CSV pair/cell count changed")
    retained = [row for row in pairs if row["evidence_origin"] == "P0.9 IDENTICAL-SOLID PAIR CERTIFICATE REUSED"]
    changed = [row for row in pairs if row["evidence_origin"] == "P1.0 CHANGED-PART PAIR RECALCULATED"]
    if len(retained) != 60 or len(changed) != 9:
        errors.append("certificate origin partition is not 60 retained / 9 changed")
    if any(float(row["minimum_guaranteed_clearance_mm"]) < 0.75 for row in retained):
        errors.append("retained certificate below 0.75 mm")
    if any(float(row["minimum_guaranteed_clearance_mm"]) < 3.0 for row in changed):
        errors.append("changed-part certificate below 3.0 mm")
    if any("P09_MOVING_STRIKER" in row["pair_id"] for row in pairs):
        errors.append("superseded P09 moving-striker pair remains in current certificate")

    prior_hash = hashlib.sha256((P09 / "continuous-clearance-summary.csv").read_bytes()).hexdigest().upper()
    if len(basis) != 2 or basis[0]["source_sha256"] != prior_hash or basis[0]["pair_count"] != "60" or basis[1]["pair_count"] != "9":
        errors.append("certificate supersession basis changed or source hash mismatched")
    if len(sweep) != 413 or sweep[0]["j2_deg"] != "15.00" or sweep[-1]["j2_deg"] != "118.00":
        errors.append("critical clearance sweep domain/count changed")
    if max(float(row["positive_stop_clearance_mm"]) for row in sweep if row["positive_stop_state"] == "CONTACT") > 1e-7:
        errors.append("contact state contains positive gap")

    mass_now = mass[-1]
    for key, expected in {"moving_striker_cad_mass_g": 51.184, "incomplete_known_mass_g": 576.040, "provisional_headroom_g": 173.960}.items():
        if not close(mass_now[key], expected):
            errors.append(f"mass value changed: {key}")
    if not close(float(mass_now["incomplete_known_mass_g"]) + float(mass_now["provisional_headroom_g"]), 750.0):
        errors.append("mass and headroom do not close to 750 g")
    if len(budget) != 6 or any(row["state"] != "OPEN" for row in budget[:-1]) or budget[-1]["state"] != "UNALLOCATED_OPEN_LIMIT":
        errors.append("tolerance budget is not five OPEN sources plus one unallocated limit")
    if len(holds) != 12 or sum(row["state"] == "OPEN" for row in holds) != 8 or sum(row["state"] == "PARTIAL" for row in holds) != 4:
        errors.append("hold register is not 8 OPEN / 4 PARTIAL")

    required = (
        "HR-V0_arm_P1.0_X430_clearance_candidate.step",
        "HR-V0_arm_P1.0_X430_clearance_candidate.glb",
        "parts/P10-C02_X430_relief-moving-striker.step",
        "P10-C02_relief-moving-striker-review-drawing.svg",
    )
    for name in required:
        if not (PKG / name).is_file():
            errors.append(f"missing generated artifact: {name}")
    if (PKG / required[0]).is_file() and not (PKG / required[0]).read_bytes().startswith(b"ISO-10303-21;"):
        errors.append("STEP header invalid")
    if (PKG / required[1]).is_file() and not (PKG / required[1]).read_bytes().startswith(b"glTF"):
        errors.append("GLB header invalid")

    guide = GUIDE.read_text(encoding="utf-8") if GUIDE.is_file() else ""
    doc = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for token in (REVISION, "3.242248", "3.942108", "2.491516", "1.491516", "576.040", "P0.7 remains controlled", "XM430 is not selected", "NOT APPROVED"):
        if token not in guide or token not in doc:
            errors.append(f"controlled explanatory token missing: {token}")
    for token in ("model-viewer", "font:17px", "font-size:16px", "font-size:13px"):
        if token not in guide:
            errors.append(f"guide legibility/model token missing: {token}")
    for unsafe in ("approved for energization", "XM430 is selected", "ready for fabrication"):
        if unsafe.lower() in (guide + doc).lower():
            errors.append(f"unsafe release claim present: {unsafe}")

    if errors:
        print("HR-V0 P1.0 X430 clearance-arm check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 P1.0 X430 clearance-arm check: PASS")
    print("60 unchanged certificates retained; 9 changed pairs recomputed at 3.0 mm; changed minimum 3.242248 mm")
    print("118 deg nominal stop; 2.491516 mm nominal X430 clearance; 1.491516 mm unallocated variation limit")
    print("P0.7 remains controlled; P0.9/P1.0 are unselected; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
