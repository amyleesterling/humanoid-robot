#!/usr/bin/env python3
"""Fail-closed validation for the R188 Q4X quote-readiness amendment."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "procurement/hr-v0/q4x-quote-readiness-p0.1"
DOC = ROOT / "docs/hr-v0-q4x-quote-readiness-p0.1.md"
REVISION = "HR-V0-Q4X-QUOTE-READINESS-P0.1"
EXPECTED = {"source-delta.csv", "line-disposition.csv", "cost-reconciliation.csv", "package-status.json", "index.html"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    if not OUT.is_dir() or {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED:
        failures.append("package membership changed")
    if not DOC.is_file():
        failures.append("narrative missing")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    sources = rows(OUT / "source-delta.csv")
    dispositions = rows(OUT / "line-disposition.csv")
    costs = rows(OUT / "cost-reconciliation.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    page = (OUT / "index.html").read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    if [row["line_id"] for row in sources] != ["QRL-002", "QRL-006"]:
        failures.append("source delta line identities changed")
    if [row["exact_manufacturer_part_number"] for row in sources] != ["14F0907", "1464484"]:
        failures.append("exact MPNs changed")
    if [row["seller_order_code"] for row in sources] != ["14F0907-ND", "277-1464484-ND"]:
        failures.append("seller order codes changed")
    if [row["unit_price_snapshot_usd"] for row in sources] != ["29.80", "22.83"]:
        failures.append("direct price snapshots changed")
    if "FACTORY STOCK 60" not in sources[0]["availability_snapshot"] or "IN-STOCK 0" not in sources[1]["availability_snapshot"]:
        failures.append("availability facts weakened")
    if any(row["checkout_state"].startswith("NOT READY") is False for row in dispositions):
        failures.append("checkout hold removed")
    if [row["r188_snapshot_subtotal_usd"] for row in costs] != ["211.63", "22.83", "234.46"]:
        failures.append("cost reconciliation changed")
    false_fields = ["cart_executed", "quote_received", "purchase_authorized", "order_placed", "physical_evidence_received", "fabrication_authorized", "connection_authorized", "energization_authorized"]
    if status["revision"] != REVISION or any(status[name] for name in false_fields):
        failures.append("status or authority boundary changed")
    if status["sol_r12_blockers_closed"] != 0 or status["combined_snapshot_subtotal_usd"] != "234.46":
        failures.append("Sol or cost state changed")
    for token in ("$234.46", "0 in stock", "No cart, quote, order or work authority", "data-tab='lines'", "font:16px/1.55"):
        if token not in page:
            failures.append(f"guide omits {token}")
    for token in ("zero stock", "No cart", "closes zero Sol R12 blockers", "not checkout-ready"):
        if token not in doc:
            failures.append(f"narrative omits {token}")
    text_paths = [*OUT.glob("*.csv"), OUT / "package-status.json", OUT / "index.html", DOC]
    if any("NOT APPROVED" not in path.read_text(encoding="utf-8") for path in text_paths):
        failures.append("preliminary warning missing")
    if failures:
        print(f"{REVISION}: FAIL", file=sys.stderr)
        print("\n".join(f"- {item}" for item in failures), file=sys.stderr)
        return 1
    print(f"{REVISION}: PASS")
    print("2 direct lines / corrected $234.46 snapshot / 1 explicit zero-stock hold")
    print("0 carts / 0 quotes / 0 purchases / 0 work or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
