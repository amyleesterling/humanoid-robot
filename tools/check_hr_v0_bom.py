from __future__ import annotations

import csv
from pathlib import Path

from generate_hr_v0_bom_closure import (
    CLOSURE,
    EVALUATION_IDS,
    FIELDS,
    ROOT,
    SYSTEM_BOM,
    classification,
)


BATCH = ROOT / "bom" / "hr-v0-evaluation-batch-a.csv"
MECHANICAL_SUBSET = ROOT / "bom" / "hr-v0-unpowered-mechanical-evaluation.csv"
PROCEDURES = ROOT / "tests" / "procedures" / "procedure-registry.csv"
REQUIREMENTS = ROOT / "requirements" / "requirements.csv"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
RECEIVING_FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-batch-a-receiving-template.csv"
REQUIRED_DEPENDENCY_IDS = {f"BOM-{number:03d}" for number in range(58, 72)}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def ids(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


def main() -> None:
    errors: list[str] = []
    system_rows, system_headers = read_csv(SYSTEM_BOM)
    closure_rows, closure_headers = read_csv(CLOSURE)
    batch_rows, batch_headers = read_csv(BATCH)
    mechanical_rows, mechanical_headers = read_csv(MECHANICAL_SUBSET)
    procedure_rows, _ = read_csv(PROCEDURES)
    requirement_rows, _ = read_csv(REQUIREMENTS)
    gate_rows, _ = read_csv(GATES)

    if tuple(closure_headers) != FIELDS:
        errors.append(f"closure columns: expected {FIELDS}, got {tuple(closure_headers)}")
    required_system_headers = {
        "item_id", "subsystem", "manufacturer", "manufacturer_part_number",
        "quantity", "baseline_status", "selection_basis",
    }
    if not required_system_headers.issubset(system_headers):
        errors.append("system BOM is missing required columns")
    required_batch_headers = {
        "batch_line", "parent_item_id", "manufacturer", "order_code", "quantity",
        "purpose", "primary_source", "source_revision_or_access", "receiving_route",
        "approval_state", "release_use",
    }
    if not required_batch_headers.issubset(batch_headers):
        errors.append("evaluation batch is missing required columns")
    required_mechanical_headers = {
        "subset_line", "batch_line", "parent_item_id", "manufacturer", "order_code",
        "quantity", "mechanical_role", "allowed_action", "required_records", "status",
    }
    if not required_mechanical_headers.issubset(mechanical_headers):
        errors.append("unpowered mechanical subset is missing required columns")

    system_by_id = {row["item_id"]: row for row in system_rows}
    closure_by_id = {row["item_id"]: row for row in closure_rows}
    if len(system_by_id) != len(system_rows):
        errors.append("system BOM contains duplicate item IDs")
    if len(closure_by_id) != len(closure_rows):
        errors.append("closure register contains duplicate item IDs")
    if set(system_by_id) != set(closure_by_id):
        errors.append(
            f"closure coverage mismatch: missing={sorted(set(system_by_id)-set(closure_by_id))}; "
            f"extra={sorted(set(closure_by_id)-set(system_by_id))}"
        )
    if not REQUIRED_DEPENDENCY_IDS.issubset(system_by_id):
        errors.append(f"missing assembly-dependency rows: {sorted(REQUIRED_DEPENDENCY_IDS-set(system_by_id))}")

    for item_id, item in system_by_id.items():
        if not item["quantity"].strip() or not item["selection_basis"].strip():
            errors.append(f"{item_id}: blank quantity or selection basis")
        actual = closure_by_id.get(item_id)
        if actual is None:
            continue
        expected = {"item_id": item_id, **classification(item)}
        if actual != expected:
            errors.append(f"{item_id}: closure classification differs from controlled rule")
        if actual["application_state"] == "SELECTION REQUIRED" and actual["allowed_action"] not in {
            "HOLD", "PROGRAM OWNER APPROVAL REQUIRED FOR EVALUATION PURCHASE"
        }:
            errors.append(f"{item_id}: unresolved application has unsafe allowed action")

    procedure_ids = {row["verification_id"] for row in procedure_rows}
    batch_ids: set[str] = set()
    batch_parents: set[str] = set()
    for row_number, row in enumerate(batch_rows, start=2):
        batch_id = row["batch_line"]
        parent = row["parent_item_id"]
        if batch_id in batch_ids:
            errors.append(f"batch row {row_number}: duplicate {batch_id}")
        batch_ids.add(batch_id)
        batch_parents.add(parent)
        if parent not in EVALUATION_IDS or parent not in system_by_id:
            errors.append(f"{batch_id}: invalid evaluation parent {parent}")
        if row["approval_state"] != "PROGRAM OWNER APPROVAL REQUIRED":
            errors.append(f"{batch_id}: approval boundary changed")
        if row["release_use"] != "EVALUATION ONLY":
            errors.append(f"{batch_id}: release use must remain EVALUATION ONLY")
        if not row["primary_source"].startswith("https://"):
            errors.append(f"{batch_id}: missing primary HTTPS source")
        if "202" not in row["source_revision_or_access"]:
            errors.append(f"{batch_id}: source revision/access date missing")
        if not row["order_code"].strip() or "SELECTION REQUIRED" in row["order_code"].upper():
            errors.append(f"{batch_id}: evaluation order code is unresolved")
        unknown_routes = ids(row["receiving_route"]) - procedure_ids
        if unknown_routes:
            errors.append(f"{batch_id}: unknown receiving routes {sorted(unknown_routes)}")
    if batch_parents != EVALUATION_IDS:
        errors.append(
            f"evaluation batch parent coverage mismatch: missing={sorted(EVALUATION_IDS-batch_parents)}; "
            f"extra={sorted(batch_parents-EVALUATION_IDS)}"
        )

    batch_by_line = {row["batch_line"]: row for row in batch_rows}
    expected_mechanical_lines = {f"MEV-{number:03d}" for number in range(1, 8)}
    expected_batch_lines = {"EVA-002", "EVA-003", "EVA-004", "EVA-010", "EVA-011", "EVA-012", "EVA-013"}
    if {row["subset_line"] for row in mechanical_rows} != expected_mechanical_lines:
        errors.append("unpowered mechanical subset membership changed")
    if {row["batch_line"] for row in mechanical_rows} != expected_batch_lines:
        errors.append("unpowered mechanical subset does not cover the exact actuator/frame/gripper lines")
    for row in mechanical_rows:
        parent = batch_by_line.get(row["batch_line"])
        if parent is None:
            errors.append(f"{row['subset_line']}: missing parent batch line {row['batch_line']}")
            continue
        for field in ("parent_item_id", "manufacturer", "order_code", "quantity"):
            if row[field] != parent[field]:
                errors.append(f"{row['subset_line']}: {field} differs from {row['batch_line']}")
        if row["status"] != "PROGRAM OWNER APPROVAL REQUIRED":
            errors.append(f"{row['subset_line']}: purchase approval boundary changed")
        action = row["allowed_action"].lower()
        if "unpowered only" not in action or "program-owner purchase approval" not in action:
            errors.append(f"{row['subset_line']}: unpowered/action boundary weakened")
        if any(token in action for token in ("energize", "torque enable", "motion")):
            errors.append(f"{row['subset_line']}: prohibited powered action appears in allowed action")

    eva013 = batch_by_line.get("EVA-013", {})
    if eva013.get("parent_item_id") != "BOM-023" or eva013.get("order_code") != "FR13-S102K Set; SKU 903-0269-300" or eva013.get("quantity") != "2":
        errors.append("EVA-013 does not freeze two exact FR13-S102K sets")

    requirement_by_id = {row["id"]: row for row in requirement_rows}
    if requirement_by_id.get("CFG-003", {}).get("verification_id") != "AUDIT-BOM-001":
        errors.append("CFG-003/AUDIT-BOM-001 requirement link is missing")
    if not {"AUDIT-BOM-001", "INSPECT-BOM-001"}.issubset(procedure_ids):
        errors.append("BOM audit/receiving procedures are missing")
    if not RECEIVING_FORM.is_file():
        errors.append("evaluation receiving form is missing")

    gate_by_id = {row["gate_id"]: row for row in gate_rows}
    eg003 = gate_by_id.get("EG-003", {})
    if eg003.get("status") != "partial":
        errors.append("EG-003 must be partial after closure-register creation")
    for path in ("bom/hr-v0-bom-closure.csv", "bom/hr-v0-evaluation-batch-a.csv", "bom/hr-v0-unpowered-mechanical-evaluation.csv", "tools/check_hr_v0_bom.py"):
        if path not in eg003.get("evidence_location", ""):
            errors.append(f"EG-003 evidence does not cite {path}")

    if errors:
        raise SystemExit("HR-V0 BOM closure check failed:\n- " + "\n- ".join(errors))

    counts: dict[str, int] = {}
    for row in closure_rows:
        counts[row["closure_class"]] = counts.get(row["closure_class"], 0) + 1
    print(
        f"HR-V0 BOM closure check passed: {len(system_rows)} system items; "
        f"{len(batch_rows)} evaluation-only lines; {counts.get('selection_required', 0)} selection-required groups"
    )
    print("EG-003: PARTIAL; no production item or complete machine BOM is procurement-released")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
