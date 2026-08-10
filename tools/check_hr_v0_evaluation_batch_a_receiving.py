"""Fail-closed validation for HR-V0-EVAL-BATCH-A-RCV-P0.1."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bom" / "hr-v0-evaluation-batch-a.csv"
ACQ = ROOT / "procurement" / "hr-v0" / "evaluation-batch-a-acquisition-p0.1" / "line-register.csv"
OUT = ROOT / "tests" / "receiving" / "hr-v0-evaluation-batch-a-receiving-p0.1"
WEB = ROOT / "release" / "hr-v0" / "evaluation-batch-a-receiving-p0.1" / "index.html"
FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-batch-a-unit-receiving-template-p0.1.csv"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release" / "hr-v0" / "release-candidate.json"
REVISION = "HR-V0-EVAL-BATCH-A-RCV-P0.1"
EXPECTED = {"receiving-unit-register.csv", "receiving-traveler.csv", "evidence-file-manifest-template.csv", "quarantine-label-register.csv", "package-status.json"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED:
        errors.append("receiving artifact membership changed")
    if not WEB.is_file() or not FORM.is_file():
        errors.append("web guide or execution form missing")
    if errors:
        print(f"{REVISION}: FAIL", file=sys.stderr)
        return 1

    source = rows(SOURCE)
    acquisition = rows(ACQ)
    units = rows(OUT / "receiving-unit-register.csv")
    traveler = rows(OUT / "receiving-traveler.csv")
    evidence = rows(OUT / "evidence-file-manifest-template.csv")
    labels = rows(OUT / "quarantine-label-register.csv")
    form = rows(FORM)
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    gates = rows(GATES)
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

    expected_units: list[tuple[str, dict[str, str], dict[str, str], int]] = []
    for src, acq in zip(source, acquisition):
        if src["batch_line"] != acq["line_id"]:
            errors.append("source/acquisition line parity changed")
        for index in range(1, int(src["quantity"]) + 1):
            expected_units.append((f'{src["batch_line"]}-U{index:02d}', src, acq, index))
    if len(expected_units) != 21 or [row["unit_id"] for row in units] != [item[0] for item in expected_units]:
        errors.append("21-unit identity/order changed")
    for unit, (unit_id, src, acq, index) in zip(units, expected_units):
        expected = {
            "unit_id": unit_id,
            "line_id": src["batch_line"],
            "lot_id": acq["lot_id"],
            "parent_item_id": src["parent_item_id"],
            "manufacturer": src["manufacturer"],
            "expected_order_code": src["order_code"],
            "unit_index": str(index),
            "line_quantity": src["quantity"],
            "required_receiving_routes": src["receiving_route"],
        }
        if any(unit[key] != value for key, value in expected.items()):
            errors.append(f"{unit_id}: source parity changed")
        if unit["authorization_state"] != "NOT AUTHORIZED" or unit["order_state"] != "NOT ORDERED" or unit["receiving_state"] != "NOT RECEIVED":
            errors.append(f"{unit_id}: acquisition/receiving state promoted")
        if unit["disposition"] != "QUARANTINE REQUIRED - NOT ACCEPTED" or any(unit[key] != "NO" for key in ("connection_authorized", "motion_authorized", "energization_authorized")):
            errors.append(f"{unit_id}: quarantine or power boundary weakened")

    if len(traveler) != 252 or len({row["record_id"] for row in traveler}) != 252:
        errors.append("traveler must contain 21 x 12 unique records")
    if set(row["step_id"] for row in traveler) != {f"RCV-{index:02d}" for index in range(12)}:
        errors.append("twelve-step traveler set changed")
    if any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "NOT EXECUTED" or row["authorization_state"] != "NOT AUTHORIZED" for row in traveler):
        errors.append("a traveler record implies authority or execution")
    if form != traveler:
        errors.append("execution form is not exact traveler copy")

    if len(evidence) != 147 or len({row["evidence_id"] for row in evidence}) != 147:
        errors.append("evidence manifest must contain 21 x 7 unique placeholders")
    if any(row["state"] != "NOT EXECUTED" or row["sha256"] != "NOT EXECUTED" or row["captured_file"] != "NOT EXECUTED" for row in evidence):
        errors.append("evidence placeholder implies capture")
    if len(labels) != 21 or [row["unit_id"] for row in labels] != [row["unit_id"] for row in units]:
        errors.append("quarantine-label coverage changed")
    if any(row["initial_state"] != "NOT RECEIVED - HOLD" or row["disposition"] != "QUARANTINE - NO CONNECTION OR USE" for row in labels):
        errors.append("quarantine label boundary weakened")

    expected_status = {
        "revision": REVISION,
        "source_batch": "EVALUATION-BATCH-A",
        "source_acquisition": "HR-V0-EVAL-BATCH-A-ACQ-P0.1",
        "line_count": 17,
        "physical_unit_count": 21,
        "traveler_step_count_per_unit": 12,
        "traveler_record_count": 252,
        "evidence_category_count_per_unit": 7,
        "evidence_placeholder_count": 147,
        "quarantine_label_count": 21,
        "authorized_unit_count": 0,
        "received_unit_count": 0,
        "executed_traveler_record_count": 0,
        "captured_evidence_count": 0,
        "accepted_for_machine_use_count": 0,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION",
    }
    if status != expected_status:
        errors.append("package status changed")
    gate = next((row for row in gates if row["gate_id"] == "EG-003"), None)
    required_gate_tokens = (
        "docs/hr-v0-evaluation-batch-a-receiving-p0.1.md",
        "tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/",
        "tools/check_hr_v0_evaluation_batch_a_receiving.py",
    )
    if not gate or gate["status"] != "partial" or any(token not in gate["evidence_location"] for token in required_gate_tokens):
        errors.append("EG-003 receiving evidence route changed or was promoted")
    bom_product = next((item for item in candidate["current_products"] if item["domain"] == "bill_of_materials"), None)
    if not bom_product or "HR-V0-EVAL-BATCH-A-RCV-P0.1" not in bom_product["supporting_identifiers"] or "no_complete_machine_procurement_release" not in bom_product["release_state"]:
        errors.append("release candidate does not bind the receiving campaign fail-closed")
    page = WEB.read_text(encoding="utf-8")
    for token in (REVISION, "Receive 21 evaluation units", "252", "147", "font:clamp(16px", "Printable quarantine labels", "Do not mate connectors", 'data-lot="LOT-D"'):
        if token not in page:
            errors.append(f"web guide omits {token}")
    if errors:
        print(f"{REVISION}: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{REVISION}: PASS")
    print("17 lines / 21 units / 252 traveler records / 147 evidence placeholders / 21 quarantine labels")
    print("0 authorized / 0 ordered / 0 received / 0 executed / 0 accepted for machine use")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
