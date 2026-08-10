#!/usr/bin/env python3
"""Fail-closed consistency check for HR-V0 branch-fault validation P0.1."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "electrical" / "hr-v0-branch-fault-matrix-p0.1.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-branch-fault-validation-template.csv"
DOC = ROOT / "docs" / "hr-v0-branch-fault-validation-p0.1.md"
WEB = ROOT / "release" / "hr-v0" / "branch-fault-validation-p0.1" / "index.html"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    matrix = read_csv(MATRIX)
    form = read_csv(FORM)
    gates = {row["gate_id"]: row for row in read_csv(GATES)}
    expected_ids = [f"BF-{n:03d}" for n in range(1, 25)]
    if [row.get("case_id") for row in matrix] != expected_ids:
        failures.append("matrix must contain exactly BF-001 through BF-024 in order")
    if [row.get("case_id") for row in form] != expected_ids:
        failures.append("blank form must contain exactly BF-001 through BF-024 in order")
    expected_stages = {
        "A - UNPOWERED", "B - LIMITED ENERGY",
        "C - GUARDED FAULT FIXTURE", "D - CONFIGURED DISTRIBUTION",
    }
    if {row.get("stage") for row in matrix} != expected_stages:
        failures.append("all four dependency stages are required")
    for row in matrix:
        case_id = row.get("case_id", "<missing>")
        for field in ("references", "nets", "source_state", "injection_or_action",
                      "required_monitors", "acceptance_basis", "mandatory_prerequisites"):
            if not row.get(field, "").strip():
                failures.append(f"{case_id}: blank {field}")
        if row.get("execution_state") != "NOT EXECUTED":
            failures.append(f"{case_id}: matrix appears executed")
        if row.get("warning") != WARNING:
            failures.append(f"{case_id}: warning changed")
    for row in form:
        case_id = row.get("case_id", "<missing>")
        if row.get("execution_state") != "NOT EXECUTED" or row.get("result") != "NOT EXECUTED":
            failures.append(f"{case_id}: blank record appears executed")
        if row.get("warning") != WARNING:
            failures.append(f"{case_id}: form warning changed")
        forbidden = ("operator", "qualified_test_owner", "authorization_record",
                     "raw_trace_directory", "reviewer_disposition")
        if any(row.get(field, "").strip() for field in forbidden):
            failures.append(f"{case_id}: execution evidence must remain blank")
    gate = gates.get("EG-024")
    if not gate:
        failures.append("EG-024 is missing")
    else:
        if gate.get("status") != "open":
            failures.append("EG-024 must remain open until physical acceptance")
        for required in (
            "docs/hr-v0-branch-fault-validation-p0.1.md",
            "electrical/hr-v0-branch-fault-matrix-p0.1.csv",
            "tests/forms/hr-v0-branch-fault-validation-template.csv",
        ):
            if required not in gate.get("evidence_location", ""):
                failures.append(f"EG-024 evidence_location missing {required}")
    for path in (DOC, WEB):
        text = path.read_text(encoding="utf-8")
        for phrase in (WARNING, "24", "EG-024", "NOT EXECUTED", "direct uncontrolled short"):
            if phrase not in text:
                failures.append(f"{path.name}: missing phrase {phrase}")
    web_text = WEB.read_text(encoding="utf-8")
    if "font:18px" not in web_text or "font-size:14px" not in web_text:
        failures.append("web typography does not preserve the 18/14 px readability floor")
    if failures:
        print("HR-V0 branch-fault validation check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 branch-fault validation OK: 24/24 blank cases, four stages, EG-024 open, zero execution claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
