"""Fail-closed consistency and analytic interference checks for HR-V0-FRAME-P0.2."""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "bom" / "hr-v0-frame-joint-schedule.csv"
PLACEMENTS = ROOT / "cad" / "hr-v0" / "frame-joint-placement-p0.2.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-frame-joint-receiving-assembly-template.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def positive_overlap(a: tuple[float, float, float, float, float, float], b: tuple[float, float, float, float, float, float]) -> bool:
    """True only for positive-volume AABB intersection; touching faces are permitted."""
    return all(min(a[hi], b[hi]) - max(a[lo], b[lo]) > 1e-9 for lo, hi in ((0, 1), (2, 3), (4, 5)))


def main() -> None:
    errors: list[str] = []
    schedule = rows(SCHEDULE)
    placements = rows(PLACEMENTS)
    form = rows(FORM)
    expected_ids = [f"FJ-{index:03d}" for index in range(1, 7)]
    if [row["joint_id"] for row in schedule] != expected_ids:
        errors.append("joint schedule must contain ordered FJ-001 through FJ-006")
    if [row["joint_id"] for row in placements] != expected_ids:
        errors.append("placement schedule must contain ordered FJ-001 through FJ-006")
    if sum(int(row["bracket_qty"]) for row in schedule) != 6:
        errors.append("schedule must allocate six brackets")
    if sum(int(row["hardware_qty"]) for row in schedule) != 12:
        errors.append("schedule must allocate twelve bolt assemblies")
    if any(row["bracket_mpn"] != "40-4332" or row["hardware_mpn"] != "75-3422" for row in schedule):
        errors.append("catalog candidate identity changed")
    if any(row["configuration_state"] != "exact_candidate_hold" for row in schedule + placements):
        errors.append("a frame joint lost exact-candidate hold status")
    if any(float(row["nominal_edge_clearance_each_side_mm"]) != 2.0 for row in placements):
        errors.append("40-4332 / 40-4040 nominal face-edge screen changed")
    if any("SELECTION REQUIRED" not in row["bracket_and_tool_access_result"] for row in placements):
        errors.append("a placement improperly claims closed bracket/tool access")
    if [row["joint_id"] for row in form] != expected_ids:
        errors.append("inspection form does not seed all six joints")
    if any(row["record_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" for row in form):
        errors.append("inspection form looks executed")
    if any(row["bracket_qty"] != "1" or row["hardware_qty"] != "2" for row in form):
        errors.append("inspection form quantities disagree with P0.2")

    # Candidate 40 x 40 member envelopes in millimetres: xmin, xmax,
    # ymin, ymax, zmin, zmax.  The longitudinal/transverse pairs meet only at
    # faces and the upright begins at the base top.
    members = {
        "rear": (-250, 250, -160, -120, 0, 40),
        "front": (-250, 250, 120, 160, 0, 40),
        "left": (-230, -190, -120, 120, 0, 40),
        "right": (190, 230, -120, 120, 0, 40),
        "column": (-230, -190, -20, 20, 40, 540),
    }
    for first, second in (("rear", "left"), ("front", "left"), ("rear", "right"), ("front", "right"), ("left", "column")):
        if positive_overlap(members[first], members[second]):
            errors.append(f"positive-volume member collision: {first}/{second}")
    outside = (
        min(box[0] for name, box in members.items() if name != "column"),
        max(box[1] for name, box in members.items() if name != "column"),
        min(box[2] for name, box in members.items() if name != "column"),
        max(box[3] for name, box in members.items() if name != "column"),
    )
    if outside != (-250, 250, -160, 160):
        errors.append(f"base outside envelope changed: {outside}")

    expected_placement = {
        "FJ-001": ("-190", "-120", "20", "Z"),
        "FJ-002": ("-190", "120", "20", "Z"),
        "FJ-003": ("190", "-120", "20", "Z"),
        "FJ-004": ("190", "120", "20", "Z"),
        "FJ-005": ("-210", "-20", "40", "X"),
        "FJ-006": ("-210", "20", "40", "X"),
    }
    actual_placement = {
        row["joint_id"]: (row["ridge_x_mm"], row["ridge_y_mm"], row["ridge_z_mm"], row["ridge_axis"])
        for row in placements
    }
    if actual_placement != expected_placement:
        errors.append("controlled bracket-ridge placement changed")

    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    expected_bom = {
        "BOM-024": ("40-4040 40 Series T-Slot", "5"),
        "BOM-025": ("40-4332", "6"),
        "BOM-071": ("75-3422", "12"),
    }
    for item_id, (mpn, quantity) in expected_bom.items():
        row = bom.get(item_id, {})
        if row.get("manufacturer_part_number") != mpn or row.get("quantity") != quantity:
            errors.append(f"{item_id} identity or quantity changed")
        if row.get("baseline_status") != "exact_candidate_hold":
            errors.append(f"{item_id} lost exact-candidate hold status")

    components = rows(ROOT / "cad" / "hr-v0" / "mechanical-assembly-components.csv")
    if len(components) != 20 or components[-1].get("source_id") != "BOM-071" or components[-1].get("quantity") != "12":
        errors.append("mechanical assembly schedule must contain 20 groups and twelve BOM-071 assemblies")
    interfaces = {row["interface_id"]: row for row in rows(ROOT / "cad" / "hr-v0" / "mechanical-interface-control.csv")}
    if interfaces.get("MIC-003", {}).get("current_status") != "exact_candidate_hold":
        errors.append("MIC-003 lost exact-candidate hold status")

    requirements = {row["id"]: row for row in rows(ROOT / "requirements" / "requirements.csv")}
    procedures = {row["verification_id"]: row for row in rows(ROOT / "tests" / "procedures" / "procedure-registry.csv")}
    if requirements.get("MECH-003", {}).get("verification_id") != "INSPECT-MECH-010":
        errors.append("MECH-003 traceability missing")
    if procedures.get("INSPECT-MECH-010", {}).get("linked_requirement_ids") != "MECH-003":
        errors.append("INSPECT-MECH-010 traceability missing")

    proof_moment_nm = 11.49
    one_bracket_arm_m = 0.020
    one_bracket_screen_n = proof_moment_nm / one_bracket_arm_m
    ideal_shared_screen_n = one_bracket_screen_n / 2.0
    if not math.isclose(one_bracket_screen_n, 574.5) or not math.isclose(ideal_shared_screen_n, 287.25):
        errors.append("frame-joint load screen changed")

    cad_source = (ROOT / "cad" / "hr-v0" / "src" / "hr_v0_cad.py").read_text(encoding="utf-8")
    for token in ('Vector(0, -140, 20)', 'tslot_envelope(240, "y")', 'Vector(COLUMN_CENTER_X_MM, 0, 290)'):
        if token not in cad_source:
            errors.append(f"native CAD source lacks corrected geometry token {token}")

    controlled_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs" / "hr-v0-frame-joint-closure-p0.2.md",
            ROOT / "requirements" / "hr-v0-energization-gates.csv",
            ROOT / "references" / "primary-sources.md",
        )
    )
    for token in ("HR-V0-FRAME-P0.2", "40-4332", "75-3422", "13", "20", "INSPECT-MECH-010"):
        if token not in controlled_text:
            errors.append(f"controlled evidence lacks {token}")

    if errors:
        raise SystemExit("HR-V0 frame-joint check failed:\n- " + "\n- ".join(errors))
    print("HR-V0 frame-joint check passed: 6 exact-candidate 40-4332 brackets; 12 exact-candidate 75-3422 assemblies")
    print("500 x 320 mm outside frame: analytic AABB check found no positive-volume rail/upright overlap")
    print("11.49 N m screen => 574.5 N one-bracket / 287.25 N ideal-shared; neither is an allowable")
    print("INSPECT-MECH-010: NOT EXECUTED; received fit, tool access, torque, slip, proof and qualified disposition remain open")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
