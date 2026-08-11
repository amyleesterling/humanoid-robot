#!/usr/bin/env python3
"""Synchronize R218 safety-requirements evidence into current release records."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
EVIDENCE = ROOT / "docs/evidence-maturity.md"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = (
    "docs/hr-v0-safety-requirements-p0.2.md; "
    "release/hr-v0/safety-requirements-p0.2/; "
    "requirements/hr-v0-gate-evidence-supplement-r218.csv; "
    "tools/check_hr_v0_safety_requirements_p02.py"
)


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    touched: set[str] = set()
    target_gates = {"EG-012", "EG-021", "EG-022", "EG-026"}
    for row in rows:
        if row["gate_id"] in target_gates:
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            if row["status"] != "partial":
                raise SystemExit(f"R218 may not promote {row['gate_id']} from {row['status']}")
            touched.add(row["gate_id"])
    if touched != target_gates:
        raise SystemExit(f"R218 gate set incomplete: {sorted(touched)}")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    text = EVIDENCE.read_text(encoding="utf-8")
    old_stop = "`HR-V0-STOP-BUDGET-P0.1` arithmetic screens; `HR-V0-DYN-TRACE-P0.1` fail-closed analysis"
    new_stop = "`HR-V0-SRS-P0.2` adds a 200 ms / 2.000 degree J2-positive setup candidate, keeps 30 degree/s automatic motion prohibited on this evidence, and controls sixteen unexecuted fault/restart scenarios; `HR-V0-STOP-BUDGET-P0.1` arithmetic screens; `HR-V0-DYN-TRACE-P0.1` fail-closed analysis"
    if old_stop in text:
        text = text.replace(old_stop, new_stop, 1)
    elif new_stop not in text:
        raise SystemExit("stopping evidence maturity phrase not found")
    old_gov = "traceability links; controlled safety-allocation/FMEA/BOM/mechanical-release/frame-joint/bench-anchor/J2-limit/gripper-datum/E2 commissioning/transport-HIL inputs"
    new_gov = "traceability links; `HR-V0-SRS-P0.2` with fifteen measurable candidate requirements, seven timing records, sixteen unexecuted scenarios, twelve open common-cause records and two blank qualified-allocation records; controlled safety-allocation/FMEA/BOM/mechanical-release/frame-joint/bench-anchor/J2-limit/gripper-datum/E2 commissioning/transport-HIL inputs"
    if old_gov in text:
        text = text.replace(old_gov, new_gov, 1)
    elif new_gov not in text:
        raise SystemExit("governance evidence maturity phrase not found")
    EVIDENCE.write_text(text, encoding="utf-8", newline="\n")

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    products = candidate.get("current_products", [])
    safety = next((item for item in products if item.get("domain") == "functional_safety"), None)
    if not isinstance(safety, dict) or safety.get("identifier") != "HR-V0-FSA-P0.1":
        raise SystemExit("functional-safety parent product not found")
    supporting = safety.setdefault("supporting_identifiers", [])
    if "HR-V0-SRS-P0.2" not in supporting:
        supporting.append("HR-V0-SRS-P0.2")
    safety["release_state"] = "measurable_srs_candidate_no_plr_or_sil_assigned_no_physical_validation"
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R218 synchronized: EG-012/021/022/026 remain partial; no PLr/SIL or authority assigned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
