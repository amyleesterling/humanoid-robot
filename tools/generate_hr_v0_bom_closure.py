from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYSTEM_BOM = ROOT / "bom" / "bom.csv"
CLOSURE = ROOT / "bom" / "hr-v0-bom-closure.csv"
FIELDS = (
    "item_id",
    "closure_class",
    "order_code_state",
    "quantity_state",
    "primary_source_state",
    "application_state",
    "allowed_action",
    "closure_basis",
)

EVALUATION_IDS = {
    "BOM-003", "BOM-005", "BOM-006", "BOM-007", "BOM-010", "BOM-011",
    "BOM-012", "BOM-013", "BOM-014", "BOM-018", "BOM-021", "BOM-022",
    "BOM-023", "BOM-029", "BOM-030", "BOM-031", "BOM-032",
}
EXACT_HOLD_IDS = {
    "BOM-001", "BOM-002",
    "BOM-024", "BOM-025", "BOM-026", "BOM-034",
    "BOM-036", "BOM-037", "BOM-046", "BOM-047", "BOM-049", "BOM-050",
    "BOM-019", "BOM-041", "BOM-042", "BOM-052", "BOM-053", "BOM-054", "BOM-055", "BOM-056", "BOM-057", "BOM-071", "BOM-073",
    "BOM-058", "BOM-074", "BOM-075", "BOM-076", "BOM-077", "BOM-079",
    "BOM-070", "BOM-080", "BOM-081", "BOM-082",
}
GROUPED_HOLD_IDS = {"BOM-033", "BOM-038", "BOM-043"}
HISTORICAL_OR_DNP_IDS = {"BOM-004", "BOM-008", "BOM-009", "BOM-016"}
INTEGRATED_IDS = {"BOM-020"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def classification(item: dict[str, str]) -> dict[str, str]:
    item_id = item["item_id"]
    basis = item["selection_basis"]
    if item_id in EVALUATION_IDS:
        return {
            "closure_class": "evaluation_candidate",
            "order_code_state": "EXACT CANDIDATE",
            "quantity_state": "FROZEN FOR EVALUATION",
            "primary_source_state": "CURRENT PRIMARY SOURCE RECORDED",
            "application_state": "SELECTION REQUIRED",
            "allowed_action": "PROGRAM OWNER APPROVAL REQUIRED FOR EVALUATION PURCHASE",
            "closure_basis": basis,
        }
    if item_id in EXACT_HOLD_IDS:
        return {
            "closure_class": "exact_candidate_hold",
            "order_code_state": "EXACT CANDIDATE",
            "quantity_state": "CANDIDATE QUANTITY ONLY",
            "primary_source_state": "CURRENT PRIMARY SOURCE RECORDED",
            "application_state": "SELECTION REQUIRED",
            "allowed_action": "HOLD",
            "closure_basis": basis,
        }
    if item_id in GROUPED_HOLD_IDS:
        return {
            "closure_class": "grouped_components_hold",
            "order_code_state": "COMPONENT EXPANSION REQUIRED",
            "quantity_state": "SYSTEM GROUP ONLY",
            "primary_source_state": "CURRENT PRIMARY SOURCE RECORDED",
            "application_state": "SELECTION REQUIRED",
            "allowed_action": "HOLD",
            "closure_basis": basis,
        }
    if item_id in HISTORICAL_OR_DNP_IDS:
        return {
            "closure_class": "excluded_from_hr_v0_candidate",
            "order_code_state": "NOT APPLICABLE TO CURRENT CANDIDATE",
            "quantity_state": "NOT APPLICABLE",
            "primary_source_state": "HISTORICAL RECORD",
            "application_state": "EXCLUDED",
            "allowed_action": "EXCLUDED",
            "closure_basis": basis,
        }
    if item_id in INTEGRATED_IDS:
        return {
            "closure_class": "integrated_no_separate_purchase",
            "order_code_state": "INTEGRATED IN PARENT ITEM",
            "quantity_state": "PARENT QUANTITY CONTROLS",
            "primary_source_state": "CURRENT PRIMARY SOURCE RECORDED",
            "application_state": "RECEIVED VERIFICATION REQUIRED",
            "allowed_action": "INTEGRATED NO SEPARATE PURCHASE",
            "closure_basis": basis,
        }
    return {
        "closure_class": "selection_required",
        "order_code_state": "SELECTION REQUIRED",
        "quantity_state": "SYSTEM GROUP OR CANDIDATE ONLY",
        "primary_source_state": "SELECTION REQUIRED",
        "application_state": "SELECTION REQUIRED",
        "allowed_action": "HOLD",
        "closure_basis": basis,
    }


def main() -> None:
    items = read_csv(SYSTEM_BOM)
    rows = []
    for item in items:
        rows.append({"item_id": item["item_id"], **classification(item)})

    with CLOSURE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["closure_class"]] = counts.get(row["closure_class"], 0) + 1
    print(f"Wrote {CLOSURE.relative_to(ROOT).as_posix()}: {len(rows)} system BOM items")
    print("; ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    print("PRELIMINARY—NOT A PROCUREMENT, FABRICATION, OR ENERGIZATION RELEASE")


if __name__ == "__main__":
    main()
