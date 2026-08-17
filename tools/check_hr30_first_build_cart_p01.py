"""Fail-closed checks for the HR-30 first physical-build cart."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "first-build-cart-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_first_build_cart_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release first-build cart missing")
    status = json.loads((OUT / "cart-status.json").read_text(encoding="utf-8"))
    bindings = rows(OUT / "project-source-binding.csv")
    sources = rows(OUT / "primary-source-register.csv")
    purchase = rows(OUT / "purchase-candidate-register.csv")
    samples = rows(OUT / "sample-quote-register.csv")
    borrow = rows(OUT / "borrow-contract-register.csv")
    holds = rows(OUT / "do-not-buy-yet-register.csv")
    actions = rows(OUT / "first-build-action-register.csv")
    inspections = rows(OUT / "receiving-inspection-register.csv")
    need(len(bindings) == 12, "project-source binding count drift")
    for row in bindings:
        path = WB / row["source_path"]
        need(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"bound input drift: {row['source_path']}")
    need(len(sources) == 12 and all(row["url"].startswith("https://") and row["accessed_date"] == "2026-08-17" for row in sources), "primary-source register drift")
    need({row["order_code"] for row in purchase} == {"902-0132-000", "902-0145-001"}, "priced cart item drift")
    subtotal = round(sum(float(row["extended_price_usd"]) for row in purchase), 2)
    need(subtotal == 58.77 == status["priced_candidate_subtotal_usd"], "priced subtotal drift")
    need(all("HUMAN APPROVAL REQUIRED" in row["disposition"] and "NO ORDER PLACED" in row["authority"] for row in purchase), "purchase approval boundary missing")
    need(len(samples) == 8 and {row["source_item_id"] for row in samples} == {"ACC-B01", "ACC-B02", "ACC-B04", "ACC-B05", "ACC-B08", "ACC-B09", "ACC-B10", "ACC-B11"}, "sample quote set drift")
    need(len(borrow) == 6 and all(row["disposition"].startswith(("BORROW", "CONTRACT")) for row in borrow), "borrow/contract register drift")
    need(len(holds) == 8 and all("BUY" in row["state"] or "REJECT" in row["state"] or "QUOTE" in row["state"] or "SAMPLES" in row["state"] or "BORROW" in row["state"] or "NOT NEEDED" in row["state"] for row in holds), "do-not-buy boundary drift")
    need(len(actions) == 6 and [int(row["sequence"]) for row in actions] == list(range(1, 7)), "action sequence drift")
    need(all(row["state"].startswith(("OPEN", "ACTIVE")) for row in actions), "execution invented")
    need(len(inspections) == 7 and all(row["state"] != "PASS" for row in inspections), "receiving inspection invented")
    for key in ["shipping_tax_included", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed state violated: {key}")
    for key in ["orders_placed", "supplier_contacts_executed", "quotes_received", "parts_printed", "coupons_built", "physical_tests_executed"]:
        need(status[key] == 0, f"physical execution invented: {key}")
    need(status["human_purchase_approval_required"] is True and status["gripper_fit_plate_part_count"] == 9 and status["whole_body_fit_check_stl_count"] == 98, "cart scope drift")
    need((OUT / "first-build-cart-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(sorted(row["path"] for row in manifest) == expected, "package manifest membership drift")
    need(all(int(row["bytes"]) == (OUT / row["path"]).stat().st_size and row["sha256"] == sha(OUT / row["path"]) for row in manifest), "package manifest hash/size drift")
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    need(source_files == release_files and all(sha(OUT / path) == sha(RELEASE / path) for path in source_files), "source/release parity drift")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "localStorage" in page and "Buy less. Build the first evidence." in page, "interactive/legible guide drift")
    need("$58.77" in page and "0 ordered" in page and "HUMAN APPROVAL" in page, "page approval boundary drift")
    root_page = (WB / "index.html").read_text(encoding="utf-8")
    need("HR30-FIRST-BUILD-CART-P01-START" in root_page and "$58.77" in root_page and "0 ordered" in root_page, "whole-body integration missing")
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["first_build_cart_present"] is True and root_status["first_build_cart_orders_placed"] == 0 and root_status["first_build_cart_procurement_authority"] is False, "root status overclaim")
    print("PASS: first-build cart binds 12 project inputs, two USD 58.77 bench candidates, eight sample quotes, six borrow/contract tools and eight do-not-buy holds; zero orders or authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
