#!/usr/bin/env python3
"""Synchronize R224 ECAD web-review evidence without promoting P1.18 or gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
IDENTIFIER = "HR-V0-ECAD-WEB-REVIEW-P0.1"
FRAGMENT = "docs/hr-v0-ecad-web-review-p0.1.md; electrical/reviews/hr-v0-p118-ecad-web-review-p0.1/; release/hr-v0/ecad-web-review-p1.18-p0.1/; requirements/hr-v0-gate-evidence-supplement-r224.csv; tools/check_hr_v0_ecad_web_review_p01.py"


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        gate_rows, fields = list(reader), list(reader.fieldnames or [])
    targets = {"EG-002", "EG-004"}
    touched: set[str] = set()
    for row in gate_rows:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R224 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R224 gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(gate_rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    identifiers = electrical["supporting_identifiers"]
    if IDENTIFIER not in identifiers:
        identifiers.insert(identifiers.index("HR-V0-CONFIG-REC-P0.4") + 1, IDENTIFIER)
    electrical["ecad_web_review_surface"] = IDENTIFIER
    electrical["release_state"] = "p115_current_p118_topology_unaccepted_r224_native_sheets_web_bound_full_independent_and_qualified_review_selections_physical_evidence_and_work_authority_absent"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R224 synchronized; EG-002/004 remain partial; P1.15 remains current; P1.18 and every work authority remain unaccepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
