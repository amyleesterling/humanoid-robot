#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-REQ-ATOMIC-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

from hr_v0_atomic_requirement_data import DECOMPOSITIONS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "atomic-p0.2"
WEB = ROOT / "release" / "hr-v0" / "atomic-requirements-p0.2" / "index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"
RESULT_FIELDS = "child_id|configuration_id|procedure_id|procedure_revision|observed_value_or_state|acceptance_limit|result_PASS_or_FAIL|evidence_uri|executor|timestamp|reviewer|decision"
KNOWN_MULTI_DUTY_FRAGMENTS = (
    " or write a register",
    "conductor, terminal and connector",
    " and require controlled shutdown",
    "torque or motion",
    "fabrication, assembly and energization",
    "cable and connector",
    "bend and twist",
    "hard stops, pinch points",
    "relays, drivers, firmware",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    try:
        parents = {row["id"]: row for row in rows(ROOT / "requirements/requirements.csv")}
        procedures = {row["verification_id"]: row for row in rows(ROOT / "tests/procedures/procedure-registry.csv")}
        screen = {row["requirement_id"]: row for row in rows(ROOT / "requirements/governance-p0.1/requirement-atomicity-review.csv")}
        children = rows(OUT / "atomic-requirements.csv")
        summaries = rows(OUT / "parent-decomposition-summary.csv")
        acceptance = rows(OUT / "child-acceptance-record-template.csv")
        audit = rows(OUT / "internal-atomicity-audit.csv")
        holds = rows(OUT / "atomic-requirement-holds.csv")
        sources = rows(OUT / "source-register.csv")
        summary = json.loads((OUT / "atomic-requirements-summary.json").read_text(encoding="utf-8"))
        page = WEB.read_text(encoding="utf-8")

        compound_ids = {key for key, row in screen.items() if row["review_state"].startswith("COMPOUND")}
        if set(DECOMPOSITIONS) != compound_ids or len(compound_ids) != 66:
            fail("decomposition set does not exactly cover the R141 compound screen")
        if summary["identifier"] != "HR-V0-REQ-ATOMIC-P0.2":
            fail("identifier changed")
        if (summary["parent_count"], summary["child_count"], summary["r142_child_count"], summary["newly_separated_duty_count"]) != (66, 458, 396, 62):
            fail("controlled coverage or correction counts changed")
        if (summary["minimum_children_per_parent"], summary["maximum_children_per_parent"]) != (2, 28):
            fail("controlled decomposition range changed")
        if summary["open_hold_count"] != 8 or len(holds) != 8 or any(row["state"] != "OPEN" for row in holds):
            fail("atomic holds changed or closed")
        if any(summary[key] != 0 for key in ("executed_evidence_count", "approved_child_count", "approved_parent_count")):
            fail("evidence or approval count became nonzero")
        if summary["governance_requirement_closed"] or summary["energization_authorized"]:
            fail("governance or energization authority became true")

        if len(children) != 458 or len({row["child_id"] for row in children}) != 458:
            fail("child ID coverage or uniqueness changed")
        by_parent: dict[str, list[dict[str, str]]] = {}
        for row in children:
            by_parent.setdefault(row["parent_id"], []).append(row)
            parent = parents[row["parent_id"]]
            if row["level"] != parent["level"] or row["priority"] != parent["priority"] or row["verification_id"] != parent["verification_id"]:
                fail(f"parent binding changed: {row['child_id']}")
            if row["verification_id"] not in procedures:
                fail(f"missing procedure: {row['child_id']}")
            statement = row["child_statement"].lower()
            if statement.count(" shall ") != 1 or ";" in statement:
                fail(f"child is not a one-clause candidate: {row['child_id']}")
            if any(fragment in statement for fragment in KNOWN_MULTI_DUTY_FRAGMENTS):
                fail(f"known R142 multi-duty construction remains: {row['child_id']}")
            if row["required_result_fields"] != RESULT_FIELDS or not row["child_acceptance_criterion_candidate"].startswith(f"PASS only if executed {row['verification_id']}"):
                fail(f"child acceptance binding incomplete: {row['child_id']}")
            if row["status"] != "draft" or row["evidence_uri"] != "NOT EXECUTED" or row["decision"] != "NOT APPROVED":
                fail(f"child state is not fail closed: {row['child_id']}")
            if row["accountable_person"] != "SELECTION REQUIRED" or row["approver_person"] != "SELECTION REQUIRED":
                fail(f"invented person: {row['child_id']}")
            if row["warning"] != WARNING:
                fail(f"warning changed: {row['child_id']}")

        summary_by_parent = {row["parent_id"]: row for row in summaries}
        if set(by_parent) != compound_ids or set(summary_by_parent) != compound_ids:
            fail("parent summary coverage changed")
        for parent_id, expected_statements in DECOMPOSITIONS.items():
            actual = sorted(by_parent[parent_id], key=lambda row: int(row["sequence"]))
            expected_ids = [f"{parent_id}-A{index:02d}" for index in range(1, len(expected_statements) + 1)]
            if [row["child_id"] for row in actual] != expected_ids or [row["child_statement"] for row in actual] != expected_statements:
                fail(f"child sequence or statement drift: {parent_id}")
            control = summary_by_parent[parent_id]
            if control["child_count"] != str(len(expected_statements)) or control["approval_effect"] != "NONE - PARENT AND CHILDREN REMAIN DRAFT":
                fail(f"parent control changed: {parent_id}")

        child_ids = {row["child_id"] for row in children}
        if len(acceptance) != 458 or {row["child_id"] for row in acceptance} != child_ids:
            fail("acceptance template coverage changed")
        for row in acceptance:
            if row["result_PASS_or_FAIL"] != "NOT EXECUTED" or row["evidence_uri"] != "NOT EXECUTED" or row["decision"] != "NOT APPROVED":
                fail(f"acceptance template implies execution: {row['child_id']}")
            if row["executor"] != "SELECTION REQUIRED" or row["reviewer"] != "SELECTION REQUIRED" or row["warning"] != WARNING:
                fail(f"acceptance template invents authority: {row['child_id']}")
        if len(audit) != 458 or {row["child_id"] for row in audit} != child_ids:
            fail("internal audit coverage changed")
        if any(row["internal_disposition"] != "CANDIDATE SCREENED - INDEPENDENT COVERAGE AND ATOMICITY ACCEPTANCE REQUIRED" for row in audit):
            fail("internal audit implies independent acceptance")

        expected_sources = {
            "parent_requirements": ROOT / "requirements/requirements.csv",
            "procedures": ROOT / "tests/procedures/procedure-registry.csv",
            "r141_atomicity_screen": ROOT / "requirements/governance-p0.1/requirement-atomicity-review.csv",
            "controlled_decomposition_data": ROOT / "tools/hr_v0_atomic_requirement_data.py",
        }
        if {row["source_id"] for row in sources} != set(expected_sources):
            fail("source set changed")
        for row in sources:
            path = expected_sources[row["source_id"]]
            if row["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                fail(f"source hash mismatch: {row['source_id']}")

        for token in (WARNING, "HR-V0-REQ-ATOMIC-P0.2", "R143", "font:16px", "458", "62", "0", "GOV-001", "Sol N-004", "overflow:auto"):
            if token not in page:
                fail(f"interactive page missing {token}")

        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        product = next((item for item in candidate["current_products"] if item["domain"] == "requirements"), None)
        if not product or product["identifier"] != "HR-V0-REQ-ATOMIC-P0.2" or "not_approved" not in product["release_state"]:
            fail("release candidate does not bind fail-closed P0.2 requirements")

        print("HR-V0-REQ-ATOMIC-P0.2 PASS")
        print("  66 parents / 458 child candidates / 62 R142 multi-duty separations")
        print("  458 blank acceptance rows / 8 open holds / 0 evidence / 0 approvals")
        print("  internal screen only; GOV-001 and Sol N-004 remain open")
        return 0
    except Exception as exc:
        print(f"HR-V0-REQ-ATOMIC-P0.2 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
