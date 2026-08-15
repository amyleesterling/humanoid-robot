#!/usr/bin/env python3
"""Synchronize R222 point-to-point evidence without promoting gates or P1.18."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = (
    "docs/hr-v0-panel-point-to-point-p0.1.md; "
    "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate/; "
    "release/hr-v0/panel-point-to-point-p0.1/; "
    "requirements/hr-v0-gate-evidence-supplement-r222.csv; "
    "tools/check_hr_v0_panel_point_to_point_p01.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows, fields = list(reader), list(reader.fieldnames or [])
    targets = {"EG-002", "EG-003", "EG-004", "EG-010", "EG-014", "EG-015", "EG-018", "EG-020"}
    touched: set[str] = set()
    for row in rows:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R222 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R222 gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    support = electrical.setdefault("supporting_identifiers", [])
    insert_after = "HR-V0-PANEL-COND-P0.1"
    for identifier in ("V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "HR-V0-PANEL-P2P-P0.1"):
        if identifier not in support:
            support.insert(support.index(insert_after) + 1, identifier)
            insert_after = identifier
    electrical["panel_topology_candidate"] = "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE"
    electrical["panel_point_to_point_candidate"] = "HR-V0-PANEL-P2P-P0.1"
    electrical["release_state"] = "p115_current_p118_explicit_panel_topology_unaccepted_lengths_terminations_protection_physical_evidence_and_work_authority_absent"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R222 synchronized; eight gates remain partial; P1.15 remains current; no wiring or work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
