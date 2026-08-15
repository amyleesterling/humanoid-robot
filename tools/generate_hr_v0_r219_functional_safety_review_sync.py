#!/usr/bin/env python3
"""Synchronize R219 reviewer-route evidence without promoting any gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = (
    "docs/hr-v0-functional-safety-review-route-p0.1.md; "
    "release/hr-v0/functional-safety-review-route-p0.1/; "
    "requirements/hr-v0-gate-evidence-supplement-r219.csv; "
    "tools/check_hr_v0_functional_safety_review_route_p01.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows, fields = list(reader), list(reader.fieldnames or [])
    wanted = {"EG-012", "EG-021", "EG-022", "EG-026"}
    touched: set[str] = set()
    for row in rows:
        if row["gate_id"] in wanted:
            if row["status"] != "partial":
                raise SystemExit(f"R219 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != wanted:
        raise SystemExit("target gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    safety = next(item for item in candidate["current_products"] if item["domain"] == "functional_safety")
    support = safety.setdefault("supporting_identifiers", [])
    if "HR-V0-FS-REVIEW-ROUTE-P0.1" not in support:
        support.append("HR-V0-FS-REVIEW-ROUTE-P0.1")
    safety["release_state"] = "measurable_srs_candidate_reviewer_route_open_no_provider_selected_no_plr_or_sil_no_physical_validation"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R219 synchronized; four gates remain partial; no provider, PLr/SIL, validation or authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
