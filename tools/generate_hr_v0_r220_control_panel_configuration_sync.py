#!/usr/bin/env python3
"""Synchronize R220 control-panel configuration evidence without gate promotion."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = (
    "docs/hr-v0-control-panel-configuration-p0.1.md; "
    "release/hr-v0/control-panel-configuration-p0.1/; "
    "requirements/hr-v0-gate-evidence-supplement-r220.csv; "
    "tools/check_hr_v0_control_panel_configuration_p01.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle); rows, fields = list(reader), list(reader.fieldnames or [])
    targets = {"EG-002", "EG-003", "EG-004", "EG-018", "EG-020"}
    touched: set[str] = set()
    for row in rows:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R220 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R220 gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    support = electrical.setdefault("supporting_identifiers", [])
    support[:] = [item for item in support if item != "HR-V0-CP-CONFIG-P0.1"]
    support.insert(support.index("HR-V0-CP-P0.6") + 1, "HR-V0-CP-CONFIG-P0.1")
    electrical["control_panel_configuration"] = "HR-V0-CP-CONFIG-P0.1"
    electrical["control_panel_geometry_basis"] = "HR-V0-CP-P0.6"
    electrical["release_state"] = "carrier_integrated_p115_direct_core_panel_current_identity_overlay_physical_and_supplier_evidence_absent"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R220 synchronized; EG-002/003/004/018/020 remain partial; no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
