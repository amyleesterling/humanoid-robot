#!/usr/bin/env python3
"""Validate the fail-closed Boston fabrication route P0.2 package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "release" / "hr-v0" / "boston-fabrication-route-p0.2"
ROUTES = PACKAGE / "route-comparison.csv"
SOURCES = PACKAGE / "source-register.csv"
GEOMETRY = PACKAGE / "geometry-file-register.csv"
STATUS = PACKAGE / "package-status.json"
GUIDE = PACKAGE / "index.html"
DOC = ROOT / "docs" / "hr-v0-boston-fabrication-decision-p0.2.md"
CURRENT_SOURCE = ROOT / "docs" / "hr-v0-fabrication-sourcing-boston.md"
CURRENT_REGISTER = ROOT / "cad" / "hr-v0" / "manufacturing" / "hr-v0-r69-fabrication-route-register.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION FABRICATION OR ENERGIZATION"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    routes = read_csv(ROUTES)
    sources = read_csv(SOURCES)
    geometry = read_csv(GEOMETRY)
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    guide = GUIDE.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    current = CURRENT_SOURCE.read_text(encoding="utf-8")
    register = read_csv(CURRENT_REGISTER)

    expected_routes = [f"BFR-{index:03d}" for index in range(1, 7)]
    expected_sources = [f"BFS-{index:03d}" for index in range(1, 10)]
    if [row.get("route_id") for row in routes] != expected_routes:
        errors.append("route package is not exactly BFR-001 through BFR-006")
    if [row.get("source_id") for row in sources] != expected_sources:
        errors.append("source register is not exactly BFS-001 through BFS-009")
    if len(geometry) != 15:
        errors.append(f"geometry register has {len(geometry)} rows instead of 15")
    expected_parts = {"MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"}
    if {row.get("part_id") for row in geometry} != expected_parts:
        errors.append("geometry register does not cover exactly C01/C04/C05/C06/C07")
    for row in geometry:
        path = ROOT / row.get("repository_path", "")
        if not path.is_file():
            errors.append(f"geometry file missing: {row.get('repository_path')}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if int(row.get("bytes", "-1")) != path.stat().st_size or row.get("sha256") != digest:
            errors.append(f"geometry identity mismatch: {row.get('repository_path')}")
        if row.get("authorization_state") != "NO UPLOAD OR QUOTATION AUTHORITY" or row.get("warning") != WARNING:
            errors.append(f"geometry row is not fail closed: {row.get('repository_path')}")
    for row in routes:
        if row.get("warning") != WARNING:
            errors.append(f"{row.get('route_id')} warning changed")
        if not row.get("critical_hold") or not row.get("next_permitted_action"):
            errors.append(f"{row.get('route_id')} lacks hold/action boundary")

    excluded = next((row for row in routes if row.get("route_id") == "BFR-003"), {})
    excluded_text = " ".join(excluded.values())
    for token in ("EXCLUDED", "+/-0.381 mm", "10 mm M5 countersink", "Do not upload"):
        if token not in excluded_text:
            errors.append(f"BFR-003 omits {token}")

    for key in (
        "provider_contacted",
        "supplier_selected",
        "upload_authorized",
        "quotation_authorized",
        "fabrication_authorized",
        "first_article_authorized",
        "energization_authorized",
    ):
        if status.get(key) is not False:
            errors.append(f"package status {key} is not false")
    if status.get("route_count") != 6 or status.get("source_count") != 9 or status.get("geometry_file_count") != 15:
        errors.append("package status counts do not match CSVs")

    required_guide = (
        "Do not use the earlier 4.75 mm plate suggestion",
        "9.525 mm nominal",
        "SendCutSend is not acceptable",
        "font:16px",
        "font-size:13px",
        "No provider has been contacted or selected",
    )
    for token in required_guide:
        if token not in guide:
            errors.append(f"interactive guide omits {token!r}")

    for text, label in ((doc, "decision document"), (current, "current sourcing document")):
        for token in ("HR-V0-ARM-ARCH-P0.7", "9.525 mm", "4.75 mm", "SendCutSend"):
            if token not in text:
                errors.append(f"{label} omits {token}")

    r69_007 = next((row for row in register if row.get("route_id") == "R69-FAB-007"), {})
    if "finished-part route excluded" not in " ".join(r69_007.values()):
        errors.append("current R69 route register does not exclude SendCutSend finished parts")

    if errors:
        print("HR-V0 Boston fabrication route check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HR-V0 Boston fabrication route P0.2 check passed: 6 routes; 9 current source records; 15 exact review-only geometry identities")
    print("4.75 mm advice rejected; SendCutSend finished-part route excluded")
    print("No provider contact, supplier selection, upload, quotation, first article, fabrication, or energization authorization exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
