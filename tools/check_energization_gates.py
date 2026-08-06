#!/usr/bin/env python3
"""Validate and report the controlled HR-V0 energization gate register."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "requirements" / "hr-v0-energization-gates.csv"
STAGES = {f"E{index}": index for index in range(7)}
STATUSES = {"open", "partial", "closed", "not_applicable"}
REQUIRED_FIELDS = {
    "gate_id",
    "domain",
    "requirement",
    "required_evidence",
    "evidence_location",
    "status",
    "required_before_stage",
    "owner",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--through-stage",
        choices=sorted(STAGES, key=STAGES.get),
        default="E6",
        help="Report readiness through this stage (default: E6).",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit 2 unless every applicable gate through the selected stage is closed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with REGISTER.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing_fields = REQUIRED_FIELDS - fields
        if missing_fields:
            raise SystemExit(f"Missing columns: {', '.join(sorted(missing_fields))}")
        rows = list(reader)

    errors: list[str] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        gate_id = row["gate_id"].strip()
        if not gate_id or gate_id in seen:
            errors.append(f"row {number}: missing or duplicate gate_id {gate_id!r}")
        seen.add(gate_id)
        if row["status"] not in STATUSES:
            errors.append(f"{gate_id}: invalid status {row['status']!r}")
        if row["required_before_stage"] not in STAGES:
            errors.append(
                f"{gate_id}: invalid stage {row['required_before_stage']!r}"
            )
        for field in ("domain", "requirement", "required_evidence", "owner"):
            if not row[field].strip():
                errors.append(f"{gate_id}: missing {field}")
        if row["status"] == "closed" and not row["evidence_location"].strip():
            errors.append(f"{gate_id}: closed without an evidence_location")

    if errors:
        print("Energization gate register INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    target = STAGES[args.through_stage]
    applicable = [
        row for row in rows if STAGES[row["required_before_stage"]] <= target
    ]
    counts = Counter(row["status"] for row in applicable)
    unresolved = [
        row
        for row in applicable
        if row["status"] not in {"closed", "not_applicable"}
    ]

    print(
        f"Energization gate register schema OK: {len(rows)} gates; "
        f"{len(applicable)} apply through {args.through_stage}."
    )
    print(
        "Status: "
        + ", ".join(f"{status}={counts.get(status, 0)}" for status in sorted(STATUSES))
    )
    if unresolved:
        print(f"NOT READY through {args.through_stage}: {len(unresolved)} gates unresolved.")
        for row in unresolved:
            print(
                f"- {row['gate_id']} [{row['status']}] "
                f"before {row['required_before_stage']}: {row['requirement']}"
            )
        return 2 if args.require_ready else 0

    print(f"REGISTER READY through {args.through_stage}; qualified review still controls release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
