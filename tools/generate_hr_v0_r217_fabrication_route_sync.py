#!/usr/bin/env python3
"""Synchronize R217 fabrication-route evidence into current gate and maturity records."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
EVIDENCE = ROOT / "docs/evidence-maturity.md"
FRAGMENT = (
    "docs/hr-v0-boston-fabrication-decision-p0.4.md; "
    "release/hr-v0/boston-fabrication-route-p0.4/; "
    "requirements/hr-v0-gate-evidence-supplement-r217.csv; "
    "tools/check_hr_v0_boston_fabrication_route_p04.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    touched = set()
    for row in rows:
        if row["gate_id"] in {"EG-003", "EG-006", "EG-007"}:
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != {"EG-003", "EG-006", "EG-007"}:
        raise SystemExit(f"R217 gate set incomplete: {sorted(touched)}")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    text = EVIDENCE.read_text(encoding="utf-8")
    old = "`HR-V0-BOSTON-FAB-ROUTE-P0.3` screens ten uncontacted machining routes"
    new = "`HR-V0-BOSTON-FAB-ROUTE-P0.4` binds the exact P0.8/R215 chain and screens six uncontacted or excluded routes"
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit("evidence-maturity fabrication-route phrase not found")
    EVIDENCE.write_text(text, encoding="utf-8", newline="\n")
    print("R217 gate/maturity synchronization complete: EG-003/006/007 remain partial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
