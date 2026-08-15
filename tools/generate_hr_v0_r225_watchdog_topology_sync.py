#!/usr/bin/env python3
"""Synchronize R225 watchdog topology evidence into gates and release metadata."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
SUPPLEMENT = ROOT / "requirements/hr-v0-gate-evidence-supplement-r225.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
IDENTIFIER = "HR-V0-WD-PERMIT-TOPOLOGY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
EVIDENCE = "docs/hr-v0-watchdog-permit-topology-p0.1.md; electrical/reviews/hr-v0-watchdog-permit-topology-p0.1/; release/hr-v0/watchdog-permit-topology-p0.1/; requirements/hr-v0-gate-evidence-supplement-r225.csv; tools/check_hr_v0_watchdog_permit_topology_p01.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    supplements = [
        {"gate_id": "EG-004", "round": "R225", "artifact": IDENTIFIER, "evidence_location": EVIDENCE, "status_effect": "REMAINS PARTIAL", "remaining_evidence": "P1.18 formal disposition; full independent sheet/parity review; physical connector/wiring evidence; qualified acceptance", "warning": WARNING},
        {"gate_id": "EG-012", "round": "R225", "artifact": IDENTIFIER, "evidence_location": EVIDENCE, "status_effect": "REMAINS PARTIAL", "remaining_evidence": "qualified allocation; common-cause/dependent-failure treatment; relay duty and received identity; protected routing; physical fault injection; PLr/SIL validation and signature", "warning": WARNING},
    ]
    write_rows(SUPPLEMENT, supplements)
    gates = read_rows(GATES)
    for row in gates:
        if row["gate_id"] in {"EG-004", "EG-012"}:
            parts = [p.strip() for p in row["evidence_location"].split(";") if p.strip()]
            for part in EVIDENCE.split("; "):
                if part not in parts:
                    parts.append(part)
            row["evidence_location"] = "; ".join(parts)
            row["status"] = "partial"
    write_rows(GATES, gates)

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    product = next(p for p in release["current_products"] if p["domain"] == "functional_safety")
    if IDENTIFIER not in product["supporting_identifiers"]:
        product["supporting_identifiers"].append(IDENTIFIER)
    product["watchdog_permit_topology_proof"] = IDENTIFIER
    product["release_state"] = "r225_two_series_ordinary_watchdog_contacts_source_proved_zero_safety_credit_common_cause_physical_validation_plr_sil_and_qualified_review_open"
    RELEASE.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R225 synchronized: EG-004/EG-012 remain partial; safety credit and all work authority remain false")


if __name__ == "__main__":
    main()
