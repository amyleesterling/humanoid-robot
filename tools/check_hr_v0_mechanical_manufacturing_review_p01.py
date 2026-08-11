#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-MECH-MFG-REVIEW-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/mechanical-manufacturing-review-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {
        "authority-boundary.csv", "document-precedence.csv", "fastener-candidate-register.csv",
        "index.html", "interface-fastener-stack.csv", "open-holds.csv", "package-status.json",
        "part-release-matrix.csv", "provider-dfm-response-template.csv",
        "qualified-review-checklist.csv", "qualified-review-decision-template.csv",
        "source-freshness-register.csv", "source-hash-register.csv",
    }
    need(OUT.is_dir(), "package directory missing")
    if not OUT.is_dir():
        return 1
    need({p.name for p in OUT.iterdir() if p.is_file()} == expected, "package membership changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-MECH-MFG-REVIEW-P0.1", "identifier changed")
    need(status.get("round") == "R215", "round changed")
    expected_counts = {
        "part_count": 5, "drawing_count": 5, "dxf_count": 5, "step_count": 5,
        "drawing_explicit_control_count": 26, "fai_operation_count": 30,
        "interface_count": 9, "fastener_candidate_count": 6,
        "qualified_review_item_count": 18, "provider_dfm_question_count": 12,
        "open_hold_count": 12,
    }
    for key, value in expected_counts.items():
        need(status.get(key) == value, f"{key} changed")
    for key in (
        "qualified_review_complete", "provider_contacted", "quotation_authorized",
        "procurement_authorized", "fabrication_authorized", "assembly_authorized",
        "connection_authorized", "powered_test_authorized", "motion_authorized",
        "energization_authorized",
    ):
        need(status.get(key) is False, f"{key} is not false")
    need(status.get("warning") == WARNING, "status warning changed")

    parts = rows("part-release-matrix.csv")
    need({r["part_id"] for r in parts} == {"MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"}, "part set changed")
    # Two stop controls apply to both C06 and C07, so the five per-part coverage
    # counts sum to 28 while the unique source-control count remains 26.
    need(sum(int(r["explicit_control_count"]) for r in parts) == 28, "per-part control coverage total changed")
    need(sum(int(r["fai_operation_count"]) for r in parts) == 30, "part FAI total changed")
    for row in parts:
        for path_field, hash_field in (("drawing_path", "drawing_sha256"), ("dxf_path", "dxf_sha256"), ("step_path", "step_sha256")):
            path = ROOT / row[path_field]
            need(path.is_file() and digest(path) == row[hash_field], f"{row['part_id']} {path_field} identity changed")
        need(row["qualified_review"] == "OPEN" and row["fai"] == "UNEXECUTED" and row["fabrication_authorized"] == "FALSE", f"{row['part_id']} release state changed")
        need(row["warning"] == WARNING, f"{row['part_id']} warning changed")

    need(len(rows("interface-fastener-stack.csv")) == 9, "interface count changed")
    need(all(r["assembly_authorized"] == "FALSE" and r["proof"] == "UNEXECUTED" for r in rows("interface-fastener-stack.csv")), "interface state is not fail-closed")
    need(len(rows("qualified-review-checklist.csv")) == 18, "review checklist count changed")
    need(all(r["state"] == "NOT REVIEWED" and r["evidence"] == "NOT EXECUTED" for r in rows("qualified-review-checklist.csv")), "review checklist claims execution")
    need(len(rows("provider-dfm-response-template.csv")) == 12, "DFM question count changed")
    need(all(r["response"] == "NOT SENT / NO RESPONSE" and r["commercial_action_authorized"] == "FALSE" for r in rows("provider-dfm-response-template.csv")), "DFM template claims external action")
    need(len(rows("open-holds.csv")) == 12 and all(r["state"] == "OPEN" and r["external_or_physical_evidence"] == "ABSENT" for r in rows("open-holds.csv")), "hold set is not fully open")
    need(any(r["verification"].startswith("UNVERIFIED") for r in rows("source-freshness-register.csv")), "current availability uncertainty was erased")
    need(all(r["procurement_authorized"] == "FALSE" for r in rows("fastener-candidate-register.csv")), "fastener procurement authority appeared")
    need(all(r["exists"] == "TRUE" and digest(ROOT / r["source_path"]) == r["sha256"] for r in rows("source-hash-register.csv")), "source hash binding changed")
    need(all(r["permitted_by_this_package"] == ("TRUE" if r["activity"] == "internal qualified mechanical review" else "FALSE") for r in rows("authority-boundary.csv")), "authority boundary changed")

    with (ROOT / "requirements/hr-v0-energization-gates.csv").open(newline="", encoding="utf-8") as handle:
        gates = {row["gate_id"]: row for row in csv.DictReader(handle)}
    for gate_id in ("EG-003", "EG-005", "EG-006"):
        need(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} status changed")
        need("requirements/hr-v0-gate-evidence-supplement-r215.csv" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} lacks R215 evidence")
    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    mechanical = next((item for item in candidate.get("current_products", []) if item.get("domain") == "mechanical"), {})
    need("HR-V0-MECH-MFG-REVIEW-P0.1" in mechanical.get("supporting_identifiers", []), "release candidate lacks R215 mechanical support")
    need(mechanical.get("release_state") == "integrated_p06_hold_with_exact_p08_complete_arm_p07_inherited_basis_physical_evidence_open_qualified_release_open", "mechanical release state changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    need(WARNING in page, "interactive warning missing")
    need("font:16px/1.55" in page and "font-size:14px" in page, "legibility floors changed")
    need("None silently overrides another" in page, "conflict-stop rule missing")

    if failures:
        print("HR-V0 mechanical manufacturing review P0.1: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 mechanical manufacturing review P0.1: PASS")
    print("5 parts; 26 drawing controls; 30 FAI operations; 9 interfaces; 12 holds open")
    print("Qualified review/external action/physical work/energization authority: FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
