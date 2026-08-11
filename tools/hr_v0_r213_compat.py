"""Fail-closed compatibility checks for the controlled R213 mechanical successor."""

from __future__ import annotations

import csv
import json
from pathlib import Path


R213_IDENTIFIER = "HR-V0-MECH-BOM-BIND-P0.2"
R213_ARCHITECTURE = "HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE"
R213_MECHANICAL_RELEASE_STATE = (
    "integrated_p06_system_placement_with_corrected_p08_custom_part_review_candidate_"
    "physical_evidence_open_qualified_release_open"
)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def r213_mechanical_successor_is_controlled(root: Path) -> bool:
    try:
        status = json.loads((root / "release/hr-v0/mechanical-bom-binding-p0.2/package-status.json").read_text(encoding="utf-8"))
        release = json.loads((root / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        bom = {row["item_id"]: row for row in _rows(root / "bom/bom.csv")}
        closure = {row["item_id"]: row for row in _rows(root / "bom/hr-v0-bom-closure.csv")}
        binding = _rows(root / "bom/hr-v0-mechanical-custom-part-binding-p0.2.csv")
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError):
        return False
    mechanical = next((row for row in release.get("current_products", []) if row.get("domain") == "mechanical"), {})
    bill = next((row for row in release.get("current_products", []) if row.get("domain") == "bill_of_materials"), {})
    item = bom.get("BOM-027", {})
    closed = closure.get("BOM-027", {})
    expected_parts = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]
    return all((
        status.get("identifier") == R213_IDENTIFIER,
        status.get("controlled_custom_part_candidate") == R213_ARCHITECTURE,
        status.get("current_for_qualified_design_review") is True,
        status.get("qualified_review_complete") is False,
        status.get("fabrication_authorized") is False,
        status.get("energization_authorized") is False,
        [row.get("part_id") for row in binding] == expected_parts,
        all(row.get("fabrication_authorized") == "FALSE" for row in binding),
        R213_ARCHITECTURE in item.get("manufacturer_part_number", ""),
        item.get("quantity") == "5",
        item.get("baseline_status") == "exact_candidate_hold",
        closed.get("closure_class") == "exact_candidate_hold",
        closed.get("allowed_action") == "HOLD",
        closed.get("closure_basis") == item.get("selection_basis"),
        R213_IDENTIFIER in mechanical.get("supporting_identifiers", []),
        R213_IDENTIFIER in bill.get("supporting_identifiers", []),
        mechanical.get("release_state") == R213_MECHANICAL_RELEASE_STATE,
    ))


def r213_allows_historical_source_hash(root: Path, relative: str) -> bool:
    return relative in {
        "bom/bom.csv",
        "bom/hr-v0-bom-closure.csv",
        "release/hr-v0/release-candidate.json",
    } and r213_mechanical_successor_is_controlled(root)
