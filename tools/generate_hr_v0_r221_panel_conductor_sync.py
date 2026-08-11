#!/usr/bin/env python3
"""Synchronize R221 panel-conductor evidence without promoting gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = (
    "docs/hr-v0-panel-conductor-basis-p0.1.md; "
    "release/hr-v0/panel-conductor-basis-p0.1/; "
    "requirements/hr-v0-gate-evidence-supplement-r221.csv; "
    "tools/check_hr_v0_panel_conductor_basis_p01.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows, fields = list(reader), list(reader.fieldnames or [])
    targets = {"EG-003", "EG-004", "EG-010", "EG-015", "EG-018", "EG-020"}
    touched: set[str] = set()
    for row in rows:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R221 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R221 gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    support = electrical.setdefault("supporting_identifiers", [])
    if "HR-V0-PANEL-COND-P0.1" not in support:
        support.insert(support.index("HR-V0-CP-CONFIG-P0.1") + 1, "HR-V0-PANEL-COND-P0.1")
    electrical["control_panel_conductor_basis"] = "HR-V0-PANEL-COND-P0.1"
    electrical["release_state"] = "carrier_integrated_p115_direct_core_panel_current_identity_and_fixed_internal_conductor_family_candidate_physical_protection_and_supplier_evidence_absent"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R221 synchronized; six gates remain partial; no wire, protection or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
