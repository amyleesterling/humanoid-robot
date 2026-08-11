#!/usr/bin/env python3
"""Synchronize release metadata for the R213 mechanical binding."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "release" / "hr-v0" / "release-candidate.json"
CURRENT = "HR-V0-MECH-BOM-BIND-P0.2"
HISTORICAL = "HR-V0-MECH-BOM-BIND-P0.1"


def replace(product: dict[str, object]) -> None:
    values = list(product.get("supporting_identifiers", []))
    values = [CURRENT if value == HISTORICAL else value for value in values]
    if CURRENT not in values:
        values.append(CURRENT)
    product["supporting_identifiers"] = values


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    products = data.get("current_products", [])
    for domain in ("mechanical", "bill_of_materials"):
        product = next(item for item in products if item.get("domain") == domain)
        replace(product)
        if domain == "mechanical":
            product["release_state"] = "integrated_p06_system_placement_with_corrected_p08_custom_part_review_candidate_physical_evidence_open_qualified_release_open"
        else:
            product["release_state"] = "closure_register_candidate_with_corrected_p08_custom_part_identity_no_complete_machine_procurement_release"
    historical = data.setdefault("historical_metadata_records", [])
    if not any(item.get("identifier") == HISTORICAL for item in historical):
        historical.append({
            "identifier": HISTORICAL,
            "state": "historical_after_r213",
            "successor": CURRENT,
            "scope": "P0.7 BOM-027 STEP/DXF/drawing identity; audit only",
        })
    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Release metadata synchronized to {CURRENT}; {HISTORICAL} historical")


if __name__ == "__main__":
    main()
