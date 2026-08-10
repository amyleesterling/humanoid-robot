#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-GOV-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "governance-p0.2"
WEB = ROOT / "release" / "hr-v0" / "governance-p0.2" / "index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    try:
        requirements = rows(ROOT / "requirements/requirements.csv")
        risks = rows(ROOT / "safety/risk-register.csv")
        gates = rows(ROOT / "requirements/hr-v0-energization-gates.csv")
        procedures = {row["verification_id"] for row in rows(ROOT / "tests/procedures/procedure-registry.csv")}
        req_control = rows(OUT / "requirement-control-register.csv")
        risk_control = rows(OUT / "risk-control-register.csv")
        gate_control = rows(OUT / "gate-control-register.csv")
        atomicity = rows(OUT / "requirement-atomicity-review.csv")
        holds = rows(OUT / "governance-holds.csv")
        sources = rows(OUT / "source-register.csv")
        summary = json.loads((OUT / "governance-summary.json").read_text(encoding="utf-8"))
        atomic_summary = json.loads((ROOT / "requirements/atomic-p0.1/atomic-requirements-summary.json").read_text(encoding="utf-8"))
        page = WEB.read_text(encoding="utf-8")

        if summary["identifier"] != "HR-V0-GOV-P0.2":
            fail("identifier changed")
        if (len(req_control), len(risk_control), len(gate_control)) != (81, 40, 30):
            fail("controlled coverage changed")
        if tuple(summary[key] for key in ("requirement_count", "risk_count", "gate_count")) != (81, 40, 30):
            fail("summary coverage changed")
        if (summary["compound_requirement_count"], summary["decomposed_candidate_parent_count"], summary["atomic_child_candidate_count"], summary["atomic_candidate_count"]) != (66, 66, 396, 15):
            fail("atomicity counts changed")
        if atomic_summary["parent_count"] != 66 or atomic_summary["child_count"] != 396:
            fail("atomic child source counts changed")
        if summary["open_hold_count"] != 9 or len(holds) != 9 or any(row["state"] != "OPEN" for row in holds):
            fail("governance holds changed or closed")
        for field in ("named_accountable_person_count", "named_approver_person_count", "approved_record_count", "executed_evidence_record_count"):
            if summary[field] != 0:
                fail(f"{field} became nonzero")
        if summary["governance_requirement_closed"] or summary["energization_authorized"]:
            fail("governance or energization authority became true")

        req_by_id = {row["id"]: row for row in requirements}
        if {row["record_id"] for row in req_control} != set(req_by_id):
            fail("requirement coverage mismatch")
        for row in req_control:
            source = req_by_id[row["record_id"]]
            if row["source_status"] != source["status"] or row["verification_id"] != source["verification_id"] or row["verification_id"] not in procedures:
                fail(f"requirement source binding mismatch: {row['record_id']}")

        if {row["record_id"] for row in risk_control} != {row["risk_id"] for row in risks}:
            fail("risk coverage mismatch")
        if {row["record_id"] for row in gate_control} != {row["gate_id"] for row in gates}:
            fail("gate coverage mismatch")
        for collection in (req_control, risk_control, gate_control):
            for row in collection:
                if row["accountable_person"] != "SELECTION REQUIRED" or row["approver_person"] != "SELECTION REQUIRED":
                    fail(f"invented person assignment: {row['record_id']}")
                if row["decision"] not in {"NOT APPROVED", "RESIDUAL RISK NOT ACCEPTED"}:
                    fail(f"fail-closed decision changed: {row['record_id']}")
                if WARNING != row["warning"]:
                    fail(f"warning changed: {row['record_id']}")

        compound = [row for row in atomicity if row["review_state"] == "DECOMPOSED CANDIDATE - INDEPENDENT REVIEW REQUIRED"]
        atomic = [row for row in atomicity if row["review_state"] == "ATOMIC CANDIDATE - INDEPENDENT REVIEW REQUIRED"]
        if len(atomicity) != 81 or len(compound) != 66 or len(atomic) != 15:
            fail("P0.2 atomicity coverage changed")
        if any(row["child_requirement_register"] != "requirements/atomic-p0.1/atomic-requirements.csv" for row in compound):
            fail("compound parent lost atomic child register")
        if any(row["approval_effect"] != "NONE - source requirement remains draft" for row in atomicity):
            fail("atomicity screen implies approval")

        # P0.2 is a historical snapshot. Validate its recorded path/hash identity;
        # do not compare old hashes to later live source revisions.
        expected_sources = {
            "requirements": (ROOT / "requirements/requirements.csv", "05f6f873a4bc34ca7727256e643bb176ff86ea5759a315d397602c920d430049"),
            "risks": (ROOT / "safety/risk-register.csv", "042ee76a4b50ba655fc0ee4b01d9c474f4bf444ec8e8050fe88f17a662a7dad5"),
            "gates": (ROOT / "requirements/hr-v0-energization-gates.csv", "faba0c88ac147282a424a6df54d40627bfda100d4e8120e5f12e386525f22a4b"),
            "procedures": (ROOT / "tests/procedures/procedure-registry.csv", "3e483e1d21e0f743d71ce8447b9d3d511ac8041ceab5b0b55b035844d5300e6a"),
            "atomic_requirements": (ROOT / "requirements/atomic-p0.1/atomic-requirements.csv", "536727b787d04a729cb245c71e5e9e6ddcc5eb2acea0ff739eb1c1744b845c96"),
            "atomic_requirements_summary": (ROOT / "requirements/atomic-p0.1/atomic-requirements-summary.json", "f7c246677e3fc179046251f050432b27980bc7aedcb134069c7090b1400802a5"),
        }
        if {row["source_id"] for row in sources} != set(expected_sources):
            fail("source set changed")
        for row in sources:
            path, snapshot_hash = expected_sources[row["source_id"]]
            if row["path"] != str(path.relative_to(ROOT)).replace("\\", "/"):
                fail(f"source path changed: {row['source_id']}")
            if row["sha256"] != snapshot_hash:
                fail(f"historical source hash changed: {row['source_id']}")

        for token in (WARNING, "HR-V0-GOV-P0.2", "R142", "font:16px", "396", "GOV-001", "Sol B-018", "SELECTION REQUIRED", "overflow:auto"):
            if token not in page:
                fail(f"interactive governance page missing {token}")

        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        governance = next((item for item in candidate["current_products"] if item["domain"] == "governance"), None)
        if (
            not governance
            or governance["identifier"] != "HR-V0-GOV-P0.3"
            or "HR-V0-GOV-P0.2" not in governance.get("supporting_identifiers", [])
            or "not_approved" not in governance["release_state"]
        ):
            fail("release candidate does not preserve P0.2 under the current fail-closed governance control")

        print("HR-V0-GOV-P0.2 PASS")
        print("  81 requirements / 40 risks / 30 gates / 151 controlled records")
        print("  66 decomposed parents / 396 child candidates / 9 open governance holds")
        print("  0 people / 0 evidence / 0 approvals; no energization authority")
        return 0
    except Exception as exc:
        print(f"HR-V0-GOV-P0.2 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
