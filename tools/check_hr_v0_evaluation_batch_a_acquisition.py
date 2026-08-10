"""Fail-closed validation for HR-V0-EVAL-BATCH-A-ACQ-P0.1."""

from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bom" / "hr-v0-evaluation-batch-a.csv"
OUT = ROOT / "procurement" / "hr-v0" / "evaluation-batch-a-acquisition-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-batch-a-authorization-template.csv"
REVISION = "HR-V0-EVAL-BATCH-A-ACQ-P0.1"
EXPECTED = {"line-register.csv", "lot-register.csv", "purchase-authorization-register.csv", "source-register.csv", "package-status.json", "index.html"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED:
        errors.append("artifact directory absent or membership changed")
    if not FORM.is_file():
        errors.append("authorization template absent")
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    source = rows(SOURCE)
    lines = rows(OUT / "line-register.csv")
    lots = rows(OUT / "lot-register.csv")
    auth = rows(OUT / "purchase-authorization-register.csv")
    sources = rows(OUT / "source-register.csv")
    form = rows(FORM)
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    expected_ids = [f"EVA-{i:03d}" for i in range(1, 18)]
    if [row["line_id"] for row in lines] != expected_ids:
        errors.append("17 evaluation line identities/order changed")
    if [row["batch_line"] for row in source] != expected_ids:
        errors.append("source Evaluation Batch A membership changed")
    if sum(int(row["quantity"]) for row in lines) != 21:
        errors.append("physical-unit count is not 21")
    for src, line in zip(source, lines):
        for source_field, line_field in (("parent_item_id", "parent_item_id"), ("manufacturer", "manufacturer"), ("order_code", "order_code"), ("quantity", "quantity"), ("primary_source", "official_source"), ("receiving_route", "receiving_route")):
            if src[source_field] != line[line_field]:
                errors.append(f"{line['line_id']}: source parity failed for {source_field}")
    known = sum(Decimal(row["extended_known_usd"]) for row in lines)
    quote_count = sum(row["unit_price_usd"] == "QUOTE REQUIRED" for row in lines)
    if known != Decimal("1864.73") or quote_count != 8:
        errors.append("known price floor or quote-required count changed")
    if any(row["authorization_state"] != "NOT AUTHORIZED" or row["order_state"] != "NOT ORDERED" or row["evidence_state"] != "NOT RECEIVED" for row in lines):
        errors.append("a line was promoted")
    if any("connection" not in row["prohibited_use"].lower() or "energization" not in row["prohibited_use"].lower() for row in lines):
        errors.append("line prohibited-use boundary weakened")
    if [row["lot_id"] for row in lots] != ["LOT-A", "LOT-B", "LOT-C", "LOT-D"]:
        errors.append("lot identities changed")
    if sum(int(row["line_count"]) for row in lots) != 17 or sum(int(row["physical_unit_count"]) for row in lots) != 21:
        errors.append("lot coverage does not reconcile")
    if any(row["decision_state"] != "NOT AUTHORIZED" or "INCOMPLETE" not in row["total_cost_state"] for row in lots):
        errors.append("lot cost/decision boundary weakened")
    if len(auth) != 4 or any(row["program_owner_decision"] != "NOT AUTHORIZED" or row["maximum_authorized_usd"] != "NOT AUTHORIZED" or row["approver_name"] != "SELECTION REQUIRED" for row in auth):
        errors.append("purchase authorization register was promoted")
    if len(sources) != 15 or any(not row["revision_or_access"].endswith("2026-08-09") for row in sources):
        errors.append("15-source current register changed")
    if len(form) != 1 or form[0].get("decision") != "NOT AUTHORIZED" or form[0].get("program_owner_name") != "SELECTION REQUIRED":
        errors.append("authorization form was promoted")
    expected_status = {
        "revision": REVISION,
        "source_batch": "EVALUATION-BATCH-A",
        "line_count": 17,
        "physical_unit_count": 21,
        "lot_count": 4,
        "official_web_known_price_floor_usd": "1864.73",
        "quote_required_line_count": 8,
        "shipping_tax_fees_included": False,
        "purchase_authorized": False,
        "order_placed": False,
        "physical_evidence_received": False,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": "PRELIMINARY - EVALUATION ACQUISITION DECISION ONLY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION",
    }
    if status != expected_status:
        errors.append("package status changed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (REVISION, "17 controlled evaluation lines", "$1,864.73", "eight lines still require written pricing", "font:clamp(16px", 'data-filter="LOT-D"', "No checkout, payment, order, shipment"):
        if token not in page:
            errors.append(f"interactive guide omits {token}")
    if errors:
        print(f"{REVISION}: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{REVISION}: PASS")
    print("17 lines / 21 units / 4 lots / $1,864.73 known floor / 8 quote-required")
    print("0 authorized / 0 ordered / 0 received; no fabrication, connection, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
