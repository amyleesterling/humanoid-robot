#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-MECH-DFM-DATA-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-dfm-data-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    parts = rows("part-register.csv")
    geometry = rows("geometry-file-register.csv")
    controls = rows("inspection-control-register.csv")
    fai = rows("first-article-plan.csv")
    questions = rows("dfm-question-register.csv")
    holds = rows("hold-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-mechanical-dfm-data-p0.1.md").read_text(encoding="utf-8")

    expected_parts = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]
    if [row.get("part_id") for row in parts] != expected_parts:
        errors.append("part register is not exactly C01/C04/C05/C06/C07")
    counts = {"geometry": (len(geometry), 15), "controls": (len(controls), 26), "fai": (len(fai), 30), "questions": (len(questions), 12), "holds": (len(holds), 15)}
    for label, (actual, expected) in counts.items():
        if actual != expected:
            errors.append(f"{label} count {actual} != {expected}")
    if {row.get("part_id") for row in geometry} != set(expected_parts):
        errors.append("geometry register part coverage mismatch")
    for row in geometry:
        path = ROOT / row.get("repository_path", "")
        if not path.is_file():
            errors.append(f"missing geometry {path}")
            continue
        if int(row.get("bytes", "-1")) != path.stat().st_size or row.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"geometry identity mismatch {path}")
        if row.get("upload_authorized") != "FALSE" or row.get("warning") != WARNING:
            errors.append(f"geometry row not fail closed {path}")
    if any(row.get("fabrication_authorized") != "FALSE" for row in parts):
        errors.append("a part row implies fabrication authority")
    if any(row.get("execution_state") != "UNEXECUTED" or row.get("next_work_authorized") != "FALSE" for row in fai):
        errors.append("FAI plan is not unexecuted/fail closed")
    if any(row.get("sent_state") != "NOT SENT" or row.get("commercial_action_authorized") != "FALSE" for row in questions):
        errors.append("DFM question register is not unsent/fail closed")
    if any(row.get("status") != "OPEN" for row in holds):
        errors.append("a DFM hold is not open")
    for key in ("comparison_selected", "provider_contacted", "supplier_selected", "upload_authorized", "quotation_authorized", "purchase_authorized", "first_article_authorized", "fabrication_authorized", "assembly_authorized", "motion_authorized", "energization_authorized"):
        if status.get(key) is not False:
            errors.append(f"status {key} is not false")
    for key, expected in (("part_count", 5), ("geometry_file_count", 15), ("inspection_control_count", 26), ("first_article_operation_count", 30), ("dfm_question_count", 12), ("open_hold_count", 15)):
        if status.get(key) != expected:
            errors.append(f"status {key} != {expected}")
    for token in ("font:16px", "font-size:14px", "font-size:13px", "Five parts", "P1.1/X430", "No provider contact", "first-article-plan.csv"):
        if token not in guide:
            errors.append(f"guide omits {token!r}")
    for token in ("P0.8 through P1.1 comparison evidence now exists", "P0.7 remains the controlled architecture", "Every FAI operation is `UNEXECUTED`"):
        if token not in doc:
            errors.append(f"document omits {token!r}")

    if errors:
        print("HR-V0 mechanical DFM data check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 mechanical DFM data P0.1 check passed: 5 parts; 15 hashed geometry files; 26 controls; 30 unexecuted FAI operations; 12 unsent questions; 15 open holds")
    print("P1.1/X430 comparison recorded as available but nonselected; all external-action and authorization flags remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
