#!/usr/bin/env python3
"""Validate the R185 Q4X box layout candidate."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/q4x-box-layout-p0.1"
CAD = ROOT / "cad/hr-v0-q4x-box-layout-p0.1"
WEB = ROOT / "release/hr-v0/q4x-box-layout-p0.1/index.html"
DOC = ROOT / "docs/hr-v0-q4x-box-layout-p0.1.md"
FORM = ROOT / "tests/forms/hr-v0-q4x-box-layout-inspection-p0.1.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks: list[tuple[bool, str]] = []

    def need(condition: bool, label: str) -> None:
        checks.append((condition, label))

    for path in [PKG / "source-register.csv", PKG / "dimension-register.csv", PKG / "panel-layout.csv", PKG / "closure-holds.csv", PKG / "vendor-file-hashes.csv", PKG / "package-status.json", CAD / "panel-layout.svg", CAD / "enclosure-entry-decision.svg", CAD / "build.py", CAD / "hr-v0-q4x-box-layout-p0.1.step", CAD / "14F0907-review-proxy.stl", WEB, DOC, FORM]:
        need(path.is_file() and path.stat().st_size > 0, f"exists: {path.relative_to(ROOT)}")

    dims = {r["dimension_id"]: r for r in rows(PKG / "dimension-register.csv")}
    need(dims["QLD-001"]["value"] == "174.498", "corrected 14F0907 X")
    need(dims["QLD-002"]["value"] == "222.250", "14F0907 Y")
    need(dims["QLD-003"]["value"] == "3.175", "14F0907 thickness")
    need(dims["QLD-009"]["value"] == "60.800", "device width arithmetic")
    need(dims["QLD-010"]["value"] == "12.249", "rail-edge clearance arithmetic")
    need(dims["QLD-017"]["value"] == "SELECTION REQUIRED", "gland bore held")

    layout = rows(PKG / "panel-layout.csv")
    need(any(r["record_id"] == "QLP-008" and "SELECTION REQUIRED" in r["coordinate_or_extent"] for r in layout), "rail fastener coordinates held")
    need(any(r["record_id"] == "QLP-009" and "SELECTION REQUIRED" in r["coordinate_or_extent"] for r in layout), "gland coordinates held")
    need(len(rows(PKG / "closure-holds.csv")) == 12, "twelve closure holds")
    need(len(rows(PKG / "source-register.csv")) == 14, "fourteen primary-source records")
    need(len(rows(FORM)) == 10 and all(r["result"] == "NOT EXECUTED" for r in rows(FORM)), "blank inspection form")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(status["round"] == "R185", "R185 status")
    need(status["released_drill_holes"] == 0, "zero released holes")
    need(status["authorized_fabrication"] == 0 and status["authorized_energization"] == 0, "no physical authority")
    need(status["gate_effect"] == {"EG-025": "OPEN", "EG-026": "PARTIAL"}, "gate state unchanged")

    html = WEB.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    need("font:16px" in html and "font-size:14px" in html, "legible web type floors")
    need(html.count("class='diagram'") == 1 and "class='diagram active'" in html, "interactive two-diagram viewer")
    need("0</strong>released drill holes" in html, "web says zero released holes")
    need("174.75 mm" in doc and "174.498 mm" in doc, "dimension correction documented")
    need("closes no Sol R12 blocker" in doc, "Sol baseline not overstated")
    need("NO DRILLING OR FABRICATION RELEASE" in (CAD / "panel-layout.svg").read_text(encoding="utf-8"), "SVG warning")
    need("NO HOLE DIAMETER OR LOCATION IS RELEASED" in (CAD / "enclosure-entry-decision.svg").read_text(encoding="utf-8"), "entry SVG hold")

    failed = [label for ok, label in checks if not ok]
    for ok, label in checks:
        print(("PASS " if ok else "FAIL ") + label)
    print(f"summary: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
