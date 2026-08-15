#!/usr/bin/env python3
"""Validate HR-V0-LOT-A-SRC-P0.1 and its mirrored web package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRS = (
    ROOT / "procurement/hr-v0/lot-a-source-reconciliation-p0.1",
    ROOT / "release/hr-v0/lot-a-source-reconciliation-p0.1",
)
IDENTIFIER = "HR-V0-LOT-A-SRC-P0.1"
EXPECTED = {"README.md", "item-register.csv", "source-register.csv", "source-fact-register.csv", "anomaly-register.csv", "supplier-question-register.csv", "decision-gate.csv", "receiving-acceptance-template.csv", "package-status.json", "index.html", "file-manifest.csv"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    for directory in DIRS:
        if not directory.is_dir() or {p.name for p in directory.iterdir() if p.is_file()} != EXPECTED:
            errors.append(f"{directory}: membership changed")
    if errors:
        print("\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1
    for name in EXPECTED:
        if (DIRS[0] / name).read_bytes() != (DIRS[1] / name).read_bytes():
            errors.append(f"mirror mismatch: {name}")
    items = rows(DIRS[0] / "item-register.csv")
    facts = rows(DIRS[0] / "source-fact-register.csv")
    anomalies = rows(DIRS[0] / "anomaly-register.csv")
    questions = rows(DIRS[0] / "supplier-question-register.csv")
    gates = rows(DIRS[0] / "decision-gate.csv")
    receiving = rows(DIRS[0] / "receiving-acceptance-template.csv")
    sources = rows(DIRS[0] / "source-register.csv")
    status = json.loads((DIRS[0] / "package-status.json").read_text(encoding="utf-8"))
    page = (DIRS[0] / "index.html").read_text(encoding="utf-8")
    if [r["item_id"] for r in items] != ["LOT-A-001", "LOT-A-002", "LOT-A-003"] or sum(int(r["quantity"]) for r in items) != 6:
        errors.append("three item groups / six physical units changed")
    if sum(Decimal(r["extended_visible_usd"]) for r in items) != Decimal("1182.22"):
        errors.append("visible subtotal changed")
    if items[0]["order_code"] != "902-0137-000" or "VARIANT CLARIFICATION" not in items[0]["decision_state"]:
        errors.append("XM540 purchase blocker missing")
    if len(sources) != 4 or any("accessed 2026-08-11" not in r["revision_or_date"] for r in sources):
        errors.append("current primary-source register changed")
    if len(facts) != 13 or not any(r["fact_id"] == "LAF-005" and "XM540-W270-R" in r["observed_fact"] for r in facts):
        errors.append("-T/-R fact evidence missing")
    if len(anomalies) != 4 or sum(r["severity"] == "BLOCKER" for r in anomalies) != 1 or any(r["state"] != "OPEN" for r in anomalies):
        errors.append("anomaly controls changed")
    if "XM540-W270-T" not in anomalies[0]["observation"] or "XM540-W270-R" not in anomalies[0]["observation"]:
        errors.append("variant contradiction not explicit")
    if len(questions) != 8 or any(r["state"] != "UNSENT" for r in questions):
        errors.append("supplier questions sent or changed")
    if len(gates) != 10 or any(r["state"] != "OPEN" for r in gates):
        errors.append("decision gates promoted or changed")
    if len(receiving) != 12 or any(r["result"] != "NOT_EXECUTED" or r["disposition"] != "NOT_ACCEPTED" for r in receiving):
        errors.append("receiving template implies execution")
    expected_status = {"identifier": IDENTIFIER, "unique_item_count": 3, "physical_unit_count": 6, "official_page_visible_subtotal_usd": "1182.22", "source_fact_count": 13, "open_anomaly_count": 4, "blocker_count": 1, "unsent_question_count": 8, "open_decision_gate_count": 10, "unexecuted_receiving_record_count": 12}
    for key, value in expected_status.items():
        if status.get(key) != value:
            errors.append(f"status mismatch: {key}")
    for key in ("purchase_authorized", "article_received", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        if status.get(key) is not False:
            errors.append(f"status improperly true: {key}")
    for token in (IDENTIFIER, "$1,182.22", "XM540-W270-T", "XM540-W270-R", "font:clamp(16px", "overflow:auto", "UNSENT"):
        if token not in page:
            errors.append(f"web guide missing {token}")
    for directory in DIRS:
        manifest = rows(directory / "file-manifest.csv")
        actual = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        if [r["path"] for r in manifest] != [p.name for p in actual]:
            errors.append(f"{directory}: manifest membership changed")
        for row, path in zip(manifest, actual):
            if row["bytes"] != str(path.stat().st_size) or row["sha256"] != digest(path):
                errors.append(f"{directory}: stale manifest {path.name}")
    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    bom = next((p for p in candidate["current_products"] if p["domain"] == "bill_of_materials"), {})
    if IDENTIFIER not in bom.get("supporting_identifiers", []) or "lot_a_purchase_blocker" not in bom.get("release_state", ""):
        errors.append("release candidate does not bind R237")
    if errors:
        print(f"{IDENTIFIER} FAIL:", file=sys.stderr)
        print("\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1
    print(f"{IDENTIFIER} PASS: 6 units / $1,182.22 visible subtotal / 13 facts / 4 open anomalies / 8 unsent questions")
    print("Official XM540 page -T/-R contradiction remains a purchase BLOCKER; no stock inference or authority")
    print("All 10 decision gates OPEN; all 12 receiving rows NOT EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
