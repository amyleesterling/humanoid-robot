#!/usr/bin/env python3
"""Synchronize R226 contactor parity evidence into gates and release metadata."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
SUPPLEMENT = ROOT / "requirements/hr-v0-gate-evidence-supplement-r226.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
IDENTIFIER = "HR-V0-K1K2-APP-P0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
EVIDENCE = "docs/hr-v0-contactor-application-p0.3.md; electrical/reviews/hr-v0-contactor-application-p0.3/; release/hr-v0/contactor-application-p0.3/; requirements/hr-v0-gate-evidence-supplement-r226.csv; tools/check_hr_v0_contactor_application_p03.py"


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
        {"gate_id": "EG-002", "round": "R226", "artifact": IDENTIFIER, "evidence_location": EVIDENCE, "status_effect": "REMAINS PARTIAL", "remaining_evidence": "P1.18 formal acceptance/merge; immutable baseline; clean-clone reproduction; signatures", "warning": WARNING},
        {"gate_id": "EG-004", "round": "R226", "artifact": IDENTIFIER, "evidence_location": EVIDENCE, "status_effect": "REMAINS PARTIAL", "remaining_evidence": "full independent page/parity review; accepted selected configuration; physical wire/terminal evidence", "warning": WARNING},
        {"gate_id": "EG-013", "round": "R226", "artifact": IDENTIFIER, "evidence_location": EVIDENCE, "status_effect": "REMAINS PARTIAL", "remaining_evidence": "measured break/regeneration/fault envelope; protection coordination; Schneider disposition; received device; loaded interruption/stopping/endurance; qualified review", "warning": WARNING},
    ]
    write_rows(SUPPLEMENT, supplements)
    gates = read_rows(GATES)
    for row in gates:
        if row["gate_id"] in {"EG-002", "EG-004", "EG-013"}:
            parts = [part.strip() for part in row["evidence_location"].split(";") if part.strip()]
            for part in EVIDENCE.split("; "):
                if part not in parts:
                    parts.append(part)
            row["evidence_location"] = "; ".join(parts)
            row["status"] = "partial"
    write_rows(GATES, gates)

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    electrical = next(product for product in release["current_products"] if product["domain"] == "electrical")
    if IDENTIFIER not in electrical["supporting_identifiers"]:
        electrical["supporting_identifiers"].append(IDENTIFIER)
    electrical["contactor_application_record"] = IDENTIFIER
    electrical["contactor_configuration_binding"] = "P1.15 current and P1.18 unaccepted contain 32 identical contactor-critical terminal/net rows"
    electrical["release_state"] = "p115_current_p118_unaccepted_k1k2_32_row_parity_proved_dc_application_protection_physical_tests_and_qualified_acceptance_open"
    RELEASE.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R226 synchronized: EG-002/004/013 remain partial; all physical/work authority remains false")


if __name__ == "__main__":
    main()
