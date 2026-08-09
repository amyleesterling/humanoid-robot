#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-REQ-ATOMIC-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements" / "atomic-p0.1"
WEB = ROOT / "release" / "hr-v0" / "atomic-requirements-p0.1" / "index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    try:
        parents = {row["id"]: row for row in rows(ROOT / "requirements/requirements.csv")}
        procedures = {row["verification_id"] for row in rows(ROOT / "tests/procedures/procedure-registry.csv")}
        screen = {row["requirement_id"]: row for row in rows(ROOT / "requirements/governance-p0.1/requirement-atomicity-review.csv")}
        children = rows(OUT / "atomic-requirements.csv")
        summaries = rows(OUT / "parent-decomposition-summary.csv")
        holds = rows(OUT / "atomic-requirement-holds.csv")
        sources = rows(OUT / "source-register.csv")
        summary = json.loads((OUT / "atomic-requirements-summary.json").read_text(encoding="utf-8"))
        page = WEB.read_text(encoding="utf-8")

        compound_ids = {key for key, row in screen.items() if row["review_state"].startswith("COMPOUND")}
        if len(compound_ids) != 66:
            fail("R141 compound screen changed")
        if summary["identifier"] != "HR-V0-REQ-ATOMIC-P0.1":
            fail("identifier changed")
        if summary["parent_count"] != 66 or summary["child_count"] != 396 or summary["covered_r141_compound_parent_count"] != 66:
            fail("controlled coverage counts changed")
        if summary["minimum_children_per_parent"] != 2 or summary["maximum_children_per_parent"] != 23:
            fail("controlled decomposition range changed")
        if summary["open_hold_count"] != 8 or len(holds) != 8 or any(row["state"] != "OPEN" for row in holds):
            fail("atomic-requirement holds changed or closed")
        if any(summary[key] != 0 for key in ("executed_evidence_count", "approved_child_count", "approved_parent_count")):
            fail("an evidence or approval count became nonzero")
        if summary["governance_requirement_closed"] or summary["energization_authorized"]:
            fail("governance or energization authority became true")

        if len(children) != 396 or len({row["child_id"] for row in children}) != 396:
            fail("child ID coverage or uniqueness changed")
        by_parent: dict[str, list[dict[str, str]]] = {}
        for row in children:
            by_parent.setdefault(row["parent_id"], []).append(row)
            parent = parents[row["parent_id"]]
            if row["level"] != parent["level"] or row["priority"] != parent["priority"] or row["verification_id"] != parent["verification_id"]:
                fail(f"parent metadata binding changed: {row['child_id']}")
            if row["verification_id"] not in procedures:
                fail(f"missing verification procedure: {row['child_id']}")
            if row["child_statement"].lower().count(" shall ") != 1 or ";" in row["child_statement"]:
                fail(f"child is not a single-clause candidate: {row['child_id']}")
            if row["status"] != "draft" or row["evidence_uri"] != "NOT EXECUTED" or row["decision"] != "NOT APPROVED":
                fail(f"child state is not fail closed: {row['child_id']}")
            if row["accountable_person"] != "SELECTION REQUIRED" or row["approver_person"] != "SELECTION REQUIRED":
                fail(f"invented person assignment: {row['child_id']}")
            if row["child_acceptance_binding"] != "CHILD-SPECIFIC RESULT REQUIRED IN PARENT PROCEDURE RECORD" or row["warning"] != WARNING:
                fail(f"child evidence/warning boundary changed: {row['child_id']}")

        summary_by_parent = {row["parent_id"]: row for row in summaries}
        if set(by_parent) != compound_ids or set(summary_by_parent) != compound_ids:
            fail("parent summary coverage changed")
        for parent_id in sorted(compound_ids):
            actual = sorted(by_parent[parent_id], key=lambda row: int(row["sequence"]))
            expected_count = int(summary_by_parent[parent_id]["child_count"])
            expected_ids = [f"{parent_id}-A{index:02d}" for index in range(1, expected_count + 1)]
            if [row["child_id"] for row in actual] != expected_ids:
                fail(f"child sequence changed: {parent_id}")
            control = summary_by_parent[parent_id]
            parent = parents[parent_id]
            if control["parent_status"] != parent["status"] or control["verification_id"] != parent["verification_id"]:
                fail(f"parent summary binding changed: {parent_id}")
            if control["child_count"] != str(len(actual)) or control["approval_effect"] != "NONE - PARENT AND CHILDREN REMAIN DRAFT":
                fail(f"parent decomposition state changed: {parent_id}")

        expected_sources = {
            "parent_requirements": ROOT / "requirements/requirements.csv",
            "procedures": ROOT / "tests/procedures/procedure-registry.csv",
            "r141_atomicity_screen": ROOT / "requirements/governance-p0.1/requirement-atomicity-review.csv",
        }
        if {row["source_id"] for row in sources} != set(expected_sources) | {"controlled_decomposition_data"}:
            fail("source set changed")
        for row in sources:
            if row["source_id"] == "controlled_decomposition_data":
                if row["path"] != "tools/hr_v0_atomic_requirement_data.py" or row["sha256"] != "bd9af942ec789d6290db55e23a4b5dead59d8bded94b1fa975b0e9803849adcd":
                    fail("historical P0.1 decomposition-source identity changed")
                continue
            path = expected_sources[row["source_id"]]
            if row["path"] != str(path.relative_to(ROOT)).replace("\\", "/"):
                fail(f"source path changed: {row['source_id']}")
            if row["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                fail(f"source hash mismatch: {row['source_id']}")

        for token in (WARNING, "HR-V0-REQ-ATOMIC-P0.1", "font:16px", "66", "396", "0", "GOV-001", "Sol N-004", "overflow:auto"):
            if token not in page:
                fail(f"interactive atomic-requirements page missing {token}")

        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        product = next((item for item in candidate["current_products"] if item["domain"] == "requirements"), None)
        if (
            not product
            or product["identifier"] != "HR-V0-REQ-ATOMIC-P0.2"
            or "HR-V0-REQ-ATOMIC-P0.1" not in product.get("supporting_identifiers", [])
            or "not_approved" not in product["release_state"]
        ):
            fail("release candidate does not preserve P0.1 under the current fail-closed atomic-requirement product")

        print("HR-V0-REQ-ATOMIC-P0.1 PASS")
        print("  66 compound parents / 396 stable child candidates / 8 open holds")
        print("  0 evidence / 0 approvals / all parents and children remain draft")
        print("  GOV-001 and Sol N-004 remain open pending independent acceptance")
        return 0
    except Exception as exc:
        print(f"HR-V0-REQ-ATOMIC-P0.1 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
