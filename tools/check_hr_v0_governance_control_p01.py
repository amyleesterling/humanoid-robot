#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-GOV-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "governance-p0.1"
WEB = ROOT / "release" / "hr-v0" / "governance-p0.1" / "index.html"
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
        page = WEB.read_text(encoding="utf-8")

        if summary["identifier"] != "HR-V0-GOV-P0.1":
            fail("identifier changed")
        expected_counts = (81, 40, 30)
        actual_counts = (len(req_control), len(risk_control), len(gate_control))
        if actual_counts != expected_counts or tuple(summary[key] for key in ("requirement_count", "risk_count", "gate_count")) != expected_counts:
            fail(f"coverage changed: {actual_counts}")
        if summary["compound_requirement_count"] != 66 or summary["atomic_candidate_count"] != 15:
            fail("atomicity screen counts changed")
        if summary["open_hold_count"] != 9 or len(holds) != 9 or any(row["state"] != "OPEN" for row in holds):
            fail("governance holds changed or closed")
        authority_fields = ("named_accountable_person_count", "named_approver_person_count", "approved_record_count", "executed_evidence_record_count")
        if any(summary[field] != 0 for field in authority_fields):
            fail("an evidence/person/approval count became nonzero")
        if summary["governance_requirement_closed"] or summary["energization_authorized"]:
            fail("governance or energization authority became true")

        req_by_id = {row["id"]: row for row in requirements}
        if {row["record_id"] for row in req_control} != set(req_by_id):
            fail("requirement coverage mismatch")
        for row in req_control:
            source = req_by_id[row["record_id"]]
            if row["source_status"] != source["status"] or row["verification_id"] != source["verification_id"]:
                fail(f"requirement source binding mismatch: {row['record_id']}")
            if row["verification_id"] not in procedures:
                fail(f"missing procedure: {row['verification_id']}")

        risk_by_id = {row["risk_id"]: row for row in risks}
        if {row["record_id"] for row in risk_control} != set(risk_by_id):
            fail("risk coverage mismatch")
        for row in risk_control:
            source = risk_by_id[row["record_id"]]
            if row["source_status"] != source["status"] or row["linked_requirements"] != source["linked_requirements"]:
                fail(f"risk source binding mismatch: {row['record_id']}")

        gate_by_id = {row["gate_id"]: row for row in gates}
        if {row["record_id"] for row in gate_control} != set(gate_by_id):
            fail("gate coverage mismatch")
        for row in gate_control:
            source = gate_by_id[row["record_id"]]
            if row["source_status"] != source["status"] or row["accountable_role_candidate"] != source["owner"]:
                fail(f"gate source binding mismatch: {row['record_id']}")

        for collection in (req_control, risk_control, gate_control):
            for row in collection:
                if row["accountable_person"] != "SELECTION REQUIRED" or row["approver_person"] != "SELECTION REQUIRED":
                    fail(f"invented person assignment: {row['record_id']}")
                if row["evidence_uri"] not in {"NOT EXECUTED", ""} and row["record_type"] != "gate":
                    fail(f"non-gate evidence unexpectedly populated: {row['record_id']}")
                if row["decision"] not in {"NOT APPROVED", "RESIDUAL RISK NOT ACCEPTED"}:
                    fail(f"fail-closed decision changed: {row['record_id']}")
                if "prior record-level history NOT BACKFILLED" not in row["change_history"]:
                    fail(f"history limitation lost: {row['record_id']}")
                if WARNING != row["warning"]:
                    fail(f"warning changed: {row['record_id']}")

        if len(atomicity) != 81 or {row["requirement_id"] for row in atomicity} != set(req_by_id):
            fail("atomicity screen does not cover every requirement")
        compound = [row for row in atomicity if row["review_state"].startswith("COMPOUND")]
        if len(compound) != 66 or any(row["child_requirement_register"] != "NOT ISSUED" for row in compound):
            fail("compound requirement hold changed")
        if any(row["approval_effect"] != "NONE - source requirement remains draft" for row in atomicity):
            fail("atomicity screen implies approval")

        expected_sources = {
            "requirements": ROOT / "requirements/requirements.csv",
            "risks": ROOT / "safety/risk-register.csv",
            "gates": ROOT / "requirements/hr-v0-energization-gates.csv",
            "procedures": ROOT / "tests/procedures/procedure-registry.csv",
        }
        if {row["source_id"] for row in sources} != set(expected_sources):
            fail("source set changed")
        for row in sources:
            path = expected_sources[row["source_id"]]
            if row["path"] != str(path.relative_to(ROOT)).replace("\\", "/"):
                fail(f"source path changed: {row['source_id']}")
            if row["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                fail(f"source hash mismatch: {row['source_id']}")

        required_tokens = (WARNING, "HR-V0-GOV-P0.1", "font:16px", "81", "40", "30", "0", "GOV-001", "Sol B-018", "SELECTION REQUIRED", "overflow:auto")
        for token in required_tokens:
            if token not in page:
                fail(f"interactive governance page missing {token}")

        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        governance = next((item for item in candidate["current_products"] if item["domain"] == "governance"), None)
        if not governance or governance["identifier"] != "HR-V0-GOV-P0.1" or "not_approved" not in governance["release_state"]:
            fail("release candidate does not bind fail-closed governance control")

        print("HR-V0-GOV-P0.1 PASS")
        print("  81 requirements / 40 risks / 30 gates / 151 total records")
        print("  66 compound screens / 9 open holds / 0 people / 0 approvals")
        print("  GOV-001 and Sol B-018 remain open; no energization authority")
        return 0
    except Exception as exc:
        print(f"HR-V0-GOV-P0.1 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
