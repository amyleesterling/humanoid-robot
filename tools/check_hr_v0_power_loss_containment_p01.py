"""Fail-closed checks for HR-V0-POWERLOSS-P0.1."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "safety" / "hr-v0-power-loss-containment-p0.1"
BOUND = OUT / "power-loss-energy-bound.csv"
STRATEGY = OUT / "power-loss-strategy.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-power-loss-containment-template-p0.1.csv"
GUIDE = ROOT / "release" / "hr-v0" / "power-loss-containment-p0.1" / "index.html"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
METADATA = ROOT / "release" / "hr-v0" / "release-candidate.json"


def rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AssertionError(f"missing {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    ledger = rows(ROOT / "bom" / "hr-v0-moving-mass-ledger.csv")
    allocations: dict[str, float] = {}
    radii: list[float] = []
    for row in ledger:
        allocation = float(row["bucket_allocation_g"])
        bucket = row["allocation_bucket"]
        if bucket in allocations:
            assert math.isclose(allocations[bucket], allocation, abs_tol=1e-12)
        allocations[bucket] = allocation
        if row["shoulder_radius_mm"]:
            radii.append(float(row["shoulder_radius_mm"]))
    assert math.isclose(sum(allocations.values()), 750.0, abs_tol=1e-12)
    assert math.isclose(max(radii), 360.0, abs_tol=1e-12)

    bounds = rows(BOUND)
    assert len(bounds) == 12
    by_id = {row["bound_id"]: row for row in bounds}
    assert math.isclose(float(by_id["PLB-005"]["value"]), 5.295591, abs_tol=0.000001)
    assert by_id["PLB-005"]["status"] == "NOT AN IMPACT RATING"
    assert by_id["PLB-008"]["value"] == "SELECTION REQUIRED"
    assert by_id["PLB-012"]["value"] == "NOT COVERED"

    strategy = rows(STRATEGY)
    assert len(strategy) == 10
    combined = "\n".join(" ".join(row.values()) for row in strategy)
    for required in (
        "fixed guard plus passive receiver",
        "actuator holding torque",
        "DF-01",
        "cable tension as restraint",
        "warnings, training, supervision alone",
        "RESET then distinct ARM then fresh trajectory",
    ):
        assert required in combined

    tests = rows(FORM)
    assert len(tests) == 72
    assert len({row["record_id"] for row in tests}) == 72
    assert {row["j1_command_deg"] for row in tests} == {"-20", "25", "70"}
    assert {row["j2_command_deg"] for row in tests} == {"15", "65", "115"}
    assert {row["payload_state"] for row in tests} == {"EMPTY_OPEN", "FOAM_100G_MAX_CLOSED"}
    assert {row["energy_loss_cause"] for row in tests} == {
        "E_STOP_DEMAND", "ACTUATOR_SOURCE_LOSS", "CONTROL_POWER_LOSS", "BUS_WATCHDOG_TORQUE_OFF"
    }
    assert all(row["pose_coverage"] == "3x3 GRID ONLY - CONTINUOUS COVERAGE REQUIRED" for row in tests)
    assert all(row["execution_status"] == "NOT EXECUTED" for row in tests)
    assert all(row["authorization"] == "NOT AUTHORIZED" for row in tests)

    gate_rows = rows(GATES)
    eg009 = next(row for row in gate_rows if row["gate_id"] == "EG-009")
    assert eg009["status"] == "partial"
    for evidence in (
        "docs/hr-v0-power-loss-containment-p0.1.md",
        "safety/hr-v0-power-loss-containment-p0.1/power-loss-energy-bound.csv",
        "tests/forms/hr-v0-power-loss-containment-template-p0.1.csv",
    ):
        assert evidence in eg009["evidence_location"]

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    safety = next(item for item in metadata["current_products"] if item["identifier"] == "HR-V0-FSA-P0.1")
    assert safety["supporting_identifiers"] == [
        "DF-01 ZERO SAFETY CREDIT",
        "HR-V0-WD-SUPPLY-P0.1",
        "HR-V0-POWERLOSS-P0.1",
        "HR-V0-PASSIVE-ARM-RECEIVER-P0.1",
    ]
    assert safety["release_state"] == "allocation_candidate_no_plr_or_sil_assigned"

    html = GUIDE.read_text(encoding="utf-8")
    for required in (
        "Assume the arm falls.",
        "5.296",
        "not a receiver rating or impact prediction",
        "EG-009 remains partial",
        "font:17px/1.55",
        "@media(max-width:760px)",
    ):
        assert required.lower() in html.lower()

    print("HR-V0 power-loss containment P0.1 check passed: 5.295591 J gravitational-only bound")
    print("10 strategy rows; 72 test cases remain NOT EXECUTED / NOT AUTHORIZED; EG-009 remains PARTIAL")
    print("PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
