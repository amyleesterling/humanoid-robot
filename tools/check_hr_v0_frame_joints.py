"""Fail-closed consistency checks for HR-V0-FRAME-P0.1."""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "bom" / "hr-v0-frame-joint-schedule.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-frame-joint-receiving-assembly-template.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    errors: list[str] = []
    schedule = rows(SCHEDULE)
    form = rows(FORM)
    expected_ids = [f"FJ-{index:03d}" for index in range(1, 7)]
    if [row["joint_id"] for row in schedule] != expected_ids:
        errors.append("joint schedule must contain ordered FJ-001 through FJ-006")
    if sum(int(row["bracket_qty"]) for row in schedule) != 6:
        errors.append("schedule must allocate six brackets")
    if sum(int(row["hardware_qty"]) for row in schedule) != 24:
        errors.append("schedule must allocate twenty-four bolt assemblies")
    if any(row["bracket_mpn"] != "40-4334" or row["hardware_mpn"] != "75-3422" for row in schedule):
        errors.append("catalog candidate identity changed")
    if any(row["configuration_state"] != "exact_candidate_hold" for row in schedule):
        errors.append("a frame joint lost exact-candidate hold status")
    if [row["joint_id"] for row in form] != expected_ids:
        errors.append("inspection form does not seed all six joints")
    if any(row["record_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" for row in form):
        errors.append("inspection form looks executed")

    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    expected_bom = {
        "BOM-024": ("40-4040 40 Series T-Slot", "5"),
        "BOM-025": ("40-4334", "6"),
        "BOM-071": ("75-3422", "24"),
    }
    for item_id, (mpn, quantity) in expected_bom.items():
        row = bom.get(item_id, {})
        if row.get("manufacturer_part_number") != mpn or row.get("quantity") != quantity:
            errors.append(f"{item_id} identity or quantity changed")
        if row.get("baseline_status") != "exact_candidate_hold":
            errors.append(f"{item_id} lost exact-candidate hold status")

    components = rows(ROOT / "cad" / "hr-v0" / "mechanical-assembly-components.csv")
    if len(components) != 20 or components[-1].get("source_id") != "BOM-071":
        errors.append("mechanical assembly schedule must contain 20 groups and BOM-071")
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
    nominal_face_separation_m = 0.040
    couple_force_n = proof_moment_nm / nominal_face_separation_m
    average_two_fastener_force_n = couple_force_n / 2.0
    if not math.isclose(couple_force_n, 287.25) or not math.isclose(average_two_fastener_force_n, 143.625):
        errors.append("frame-joint load screen changed")

    controlled_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs" / "hr-v0-frame-joint-closure-p0.1.md",
            ROOT / "requirements" / "hr-v0-energization-gates.csv",
            ROOT / "references" / "primary-sources.md",
        )
    )
    for token in ("HR-V0-FRAME-P0.1", "40-4334", "75-3422", "13", "20", "INSPECT-MECH-010"):
        if token not in controlled_text:
            errors.append(f"controlled evidence lacks {token}")

    if errors:
        raise SystemExit("HR-V0 frame-joint check failed:\n- " + "\n- ".join(errors))
    print("HR-V0 frame-joint check passed: 6 exact candidate brackets; 24 exact candidate bolt assemblies")
    print("11.49 N m screen => 287.25 N nominal 40 mm couple; no allowable or application release claimed")
    print("INSPECT-MECH-010: NOT EXECUTED; torque, slip, proof and qualified disposition remain open")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
