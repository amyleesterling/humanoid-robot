"""Validate the HR-30 whole-body fabrication sourcing/RFQ package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
MFG = WB / "manufacturing-files"
OUT = WB / "fabrication-sourcing-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "fabrication-sourcing-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-FABRICATION-SOURCING-P0.1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    status = json.loads((OUT / "fabrication-sourcing-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == IDENTIFIER, "identifier mismatch")
    require(status["part_count"] == 98 and status["module_count"] == 12, "whole-body part/module coverage mismatch")
    require(status["planar_dxf_count"] == 45 and status["printed_fit_article_count"] == 24, "derivative file coverage mismatch")
    require(status["provider_route_count"] == 7 and status["quote_batch_count"] == 5, "shop route or quote batch count mismatch")
    for gate in (
        "supplier_contact_executed", "quotes_received", "materials_selected",
        "tolerances_gdt_released", "dfm_complete", "fai_complete",
        "structural_capacity_validated", "procurement_authority",
        "fabrication_authority", "assembly_authority", "powered_test_authority",
        "motion_authority", "energization_authority",
    ):
        require(status[gate] is False, f"unsafe authority/closure overclaim: {gate}")

    source_parts = read_csv(MFG / "part-file-register.csv")
    routes = read_csv(OUT / "part-to-shop-route.csv")
    require(len(source_parts) == len(routes) == 98, "part route count mismatch")
    require({row["part_id"] for row in source_parts} == {row["part_id"] for row in routes}, "part route IDs do not exactly match manufacturing package")
    require(len({row["part_id"] for row in routes}) == 98, "duplicate part route")
    require(len({row["step_sha256"] for row in routes}) == 98, "STEP hashes are not unique for all controlled parts")
    for row in routes:
        relative = row["step_upload_path"].removeprefix("../manufacturing-files/")
        step = MFG / relative
        require(step.is_file() and sha256(step) == row["step_sha256"], f"STEP binding mismatch: {row['part_id']}")
        require("PRE-RFQ PACKAGE ONLY" in row["order_release_state"] and "RELEASE OPEN" in row["order_release_state"] and row["authority"].startswith("NO PROCUREMENT"), f"authority boundary missing: {row['part_id']}")
    route_counts = {route: sum(row["route_id"] == route for row in routes) for route in {row["route_id"] for row in routes}}
    require(sum(route_counts.values()) == 98 and set(route_counts) == {"FLAT-PROFILE", "CNC-METAL", "CNC-POLYMER", "PRECISION-ROD", "FIT-PRINT"}, "route family coverage mismatch")

    stock = read_csv(OUT / "flat-stock-gap-register.csv")
    require(len(stock) == 45, "flat stock screen does not cover every DXF")
    exact = sum(row["exact_stock_match_within_0_02_mm"] == "TRUE" for row in stock)
    require(exact == status["exact_sendcutsend_stock_match_count"], "exact stock-match summary mismatch")
    require(len(stock) - exact == status["stock_mismatch_or_unlisted_count"], "stock mismatch summary mismatch")
    require(all("DO NOT SUBSTITUTE" in row["disposition"] for row in stock if row["exact_stock_match_within_0_02_mm"] != "TRUE"), "stock mismatch permits silent substitution")

    sources = read_csv(OUT / "primary-source-register.csv")
    providers = read_csv(OUT / "shop-route-register.csv")
    batches = read_csv(OUT / "quote-batch-register.csv")
    dfm = read_csv(OUT / "dfm-request-register.csv")
    require(len(sources) == 10 and len(providers) == 7 and len(batches) == 5 and len(dfm) == 10, "controlled sourcing register count mismatch")
    require(all(row["official_url"].startswith("https://") and row["accessed"] == "2026-08-15" for row in sources), "source URL/access-date evidence incomplete")
    require(sum(int(row["part_count"]) for row in batches) == 98, "quote batches do not allocate every part")
    require(all(int(row["part_count"]) > 0 for row in batches), "empty quote batch is not a real RFQ package")
    require(all(row["release_state"] == "NOT RELEASED FOR ORDER" for row in batches), "quote batch overclaims order release")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for required in (
        "Make every body part quotable", "98 / 98", "Boston and online routes",
        "part-to-shop-route.csv", "flat-stock-gap-register.csv",
        "font:17px/1.55", "font-size:14px", "font-size:16px",
        "overflow:auto", "PRELIMINARY", "NOT APPROVED FOR PROCUREMENT",
    ):
        require(required.lower() in page.lower(), f"web guide missing required legible/control text: {required}")
    require("font-size:11" not in page and "font-size:10" not in page, "web guide contains undersized interface text")

    manifest = read_csv(OUT / "file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    require(listed == actual, "package manifest file set mismatch")
    for row in manifest:
        path = OUT / row["path"]
        require(path.stat().st_size == int(row["bytes"]) and sha256(path) == row["sha256"], f"package manifest mismatch: {row['path']}")
    source_files = {path.relative_to(OUT).as_posix(): sha256(path) for path in OUT.rglob("*") if path.is_file()}
    release_files = {path.relative_to(RELEASE).as_posix(): sha256(path) for path in RELEASE.rglob("*") if path.is_file()}
    require(source_files == release_files, "source/release fabrication sourcing package mismatch")

    whole_page = (WB / "index.html").read_text(encoding="utf-8")
    root_page = (ROOT / "index.html").read_text(encoding="utf-8")
    whole_readme = (WB / "README.md").read_text(encoding="utf-8")
    package_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    require("fabrication-sourcing-p0.1/index.html" in whole_page and "fabrication-sourcing-p0.1/index.html" in root_page, "public navigation does not expose sourcing guide")
    require("Whole-body fabrication sourcing P0.1" in whole_readme, "whole-body README integration missing")
    require(package_status["fabrication_sourcing_part_count"] == 98 and package_status["fabrication_materials_selected"] is False, "whole-body status integration mismatch")
    holds = read_csv(WB / "open-holds.csv")
    hold = next(row for row in holds if row["hold_id"] == "HR30-P01-H06")
    require("seven-route Boston/online pre-RFQ allocation" in hold["unresolved_item"] and hold["state"] == "OPEN", "fabrication hold not accurately advanced")

    print(
        "PASS: all 98 HR-30 parts have controlled pre-RFQ routes, hashes, five nonempty quote batches, "
        "seven verified Boston/online shop paths and fail-closed stock substitution; material, "
        "drawing, DFM, FAI, structural and every work authority remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
