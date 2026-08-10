#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-Q4X-UNPOWERED-ACQ-P0.1."""

from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "procurement/hr-v0/q4x-unpowered-acquisition-p0.1"
FORM = ROOT / "tests/forms/hr-v0-q4x-unpowered-acquisition-authorization-template-p0.1.csv"
DOC = ROOT / "docs/hr-v0-q4x-unpowered-acquisition-p0.1.md"
REVISION = "HR-V0-Q4X-UNPOWERED-ACQ-P0.1"
EXPECTED = {
    "line-register.csv",
    "lot-register.csv",
    "source-register.csv",
    "purchase-decision-register.csv",
    "package-status.json",
    "index.html",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED:
        errors.append("artifact directory absent or membership changed")
    if not FORM.is_file() or not DOC.is_file():
        errors.append("authorization template or narrative absent")
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    lines = rows(OUT / "line-register.csv")
    lots = rows(OUT / "lot-register.csv")
    sources = rows(OUT / "source-register.csv")
    decisions = rows(OUT / "purchase-decision-register.csv")
    form = rows(FORM)
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    page = (OUT / "index.html").read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")

    expected_ids = [f"QRL-{index:03d}" for index in range(1, 11)]
    if [row["line_id"] for row in lines] != expected_ids:
        errors.append("ten R186 receiving-line identities/order changed")
    if [row["manufacturer_part_number"] for row in lines] != ["PJ1084T", "14F0907", "1207650", "53111000", "53119000", "1464484", "3209578", "3209510", "3030417", "3022218"]:
        errors.append("exact manufacturer part numbers changed")
    if len(sources) != 10 or any(not row["url"].startswith("https://") for row in sources):
        errors.append("ten-source commercial register changed")
    if [row["lot_id"] for row in lots] != ["LOT-Q4X-FIT", "LOT-Q4X-PTCB"]:
        errors.append("two decision-lot identities changed")
    if sum(int(row["evaluation_quantity"]) for row in lines) != 18:
        errors.append("R186 evidence-article count is not 18")
    if sum(int(row["seller_purchase_quantity"]) for row in lines) != 21:
        errors.append("seller purchase-unit count is not 21")
    total = sum(Decimal(row["extended_snapshot_usd"]) for row in lines)
    fit = sum(Decimal(row["extended_snapshot_usd"]) for row in lines if row["lot_id"] == "LOT-Q4X-FIT")
    ptcb = sum(Decimal(row["extended_snapshot_usd"]) for row in lines if row["lot_id"] == "LOT-Q4X-PTCB")
    if (fit, ptcb, total) != (Decimal("211.30"), Decimal("22.83"), Decimal("234.13")):
        errors.append("seller snapshot arithmetic changed")
    if any(row["authorization_state"] != "NOT AUTHORIZED" or row["order_state"] != "NOT ORDERED" or row["receiving_state"] != "NOT RECEIVED" or row["cart_state"] != "NOT EXECUTED" for row in lines):
        errors.append("a line was promoted")
    if any("drilling" not in row["prohibited_use"] or "energization" not in row["prohibited_use"] for row in lines):
        errors.append("line-level work boundary weakened")
    if any(row["decision_state"] != "NOT AUTHORIZED" or "INCOMPLETE" not in row["cost_boundary"] for row in lots):
        errors.append("lot cost or decision boundary weakened")
    if len(decisions) != 2 or any(row["program_owner_decision"] != "NOT AUTHORIZED" or row["maximum_authorized_usd"] != "NOT AUTHORIZED" for row in decisions):
        errors.append("purchase decision register was promoted")
    if len(form) != 1 or form[0]["decision"] != "NOT AUTHORIZED" or form[0]["maximum_spend_usd"] != "NOT AUTHORIZED":
        errors.append("authorization template was promoted")

    false_fields = [
        "current_cart_executed",
        "purchase_authorized",
        "order_placed",
        "physical_evidence_received",
        "fabrication_authorized",
        "drilling_authorized",
        "connection_authorized",
        "powered_test_authorized",
        "motion_authorized",
        "energization_authorized",
    ]
    if status["revision"] != REVISION or status["line_count"] != 10 or status["lot_count"] != 2 or any(status[field] for field in false_fields):
        errors.append("package status changed or authority promoted")
    if status["sol_r12_blockers_closed"] != 0 or status["combined_snapshot_subtotal_usd"] != "234.13":
        errors.append("R12 or price status changed")
    for token in ("$234.13", "LOT-Q4X-FIT", "LOT-Q4X-PTCB", "data-tab='decision'", "font:16px/1.55", "0</strong>work authorizations", "Every line is still NOT AUTHORIZED"):
        if token not in page:
            errors.append(f"interactive guide omits {token}")
    for token in ("18 BLOCKER, 30 MAJOR and 8 MINOR", "closes zero Sol blockers", "No cart was created", "closes no engineering release"):
        if token not in doc:
            errors.append(f"narrative omits {token}")
    text_paths = [*OUT.glob("*.csv"), OUT / "package-status.json", OUT / "index.html", FORM, DOC]
    if any("NOT APPROVED" not in path.read_text(encoding="utf-8") for path in text_paths):
        errors.append("preliminary warning missing from an artifact")

    if errors:
        print(f"{REVISION}: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{REVISION}: PASS")
    print("10 lines / 2 lots / 18 evidence articles / 21 seller units / $234.13 snapshot subtotal")
    print("0 carts / 0 authorized / 0 ordered / 0 received / 0 work or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
