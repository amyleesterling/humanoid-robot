#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-ECAD-WEB-REVIEW-P0.1 / R224."""

from __future__ import annotations

import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
ENG = ROOT / "electrical/reviews/hr-v0-p118-ecad-web-review-p0.1"
OUT = ROOT / "release/hr-v0/ecad-web-review-p1.18-p0.1"
IDENTIFIER = "HR-V0-ECAD-WEB-REVIEW-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.sheet_buttons = 0
        self.images = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "button" and values.get("data-page") is not None:
            self.sheet_buttons += 1
        if tag == "img":
            self.images += 1
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md", "sheet-register.csv", "source-hash-register.csv", "open-holds.csv", "authority-boundary.csv", "package-status.json", "file-manifest.csv"}
    need({p.name for p in ENG.iterdir() if p.is_file()} == common, "engineering package membership changed")
    need({p.name for p in OUT.iterdir() if p.is_file()} == common | {"index.html"}, "release package membership changed")

    sheet_rows = rows(ENG / "sheet-register.csv")
    need(len(sheet_rows) == 13 and [int(row["page"]) for row in sheet_rows] == list(range(13)), "sheet sequence is not exactly 0..12")
    need(len({row["native_sheet_path"] for row in sheet_rows}) == 13 and len({row["svg_path"] for row in sheet_rows}) == 13, "sheet/source paths are not unique")
    for row in sheet_rows:
        native = ROOT / row["native_sheet_path"]
        svg = ROOT / row["svg_path"]
        need(native.is_file() and digest(native) == row["native_sheet_sha256"], f"native source mismatch: page {row['page']}")
        need(svg.is_file() and digest(svg) == row["svg_sha256"] and svg.stat().st_size == int(row["svg_bytes"]), f"SVG mismatch: page {row['page']}")
        need(row["width"] == "419.9890mm" and row["height"] == "297.0022mm" and row["viewbox"] == "0.0000 0.0000 419.9890 297.0022", f"SVG geometry changed: page {row['page']}")
        need(row["automated_export_structure"] == "PASS" and row["internal_visual_review"] == "OPEN" and row["qualified_review"] == "OPEN" and row["warning"] == WARNING, f"review boundary weakened: page {row['page']}")

    source_rows = rows(ENG / "source-hash-register.csv")
    need(len(source_rows) == 4, "source register must contain four records")
    for row in source_rows:
        path = ROOT / row["path"]
        need(path.is_file() and digest(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"source identity mismatch: {row['source_id']}")
        need(row["warning"] == WARNING and "does not establish" not in row["verified_fact"].lower(), f"source boundary changed: {row['source_id']}")
    erc = (ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate-erc.rpt").read_text(encoding="utf-8")
    log = (ECAD / "validation/kicad-cli.log").read_text(encoding="utf-8")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "ERC report is not 0/0")
    need(log.count("Plotted to '") == 14 and "Found 0 violations" in log, "KiCad CLI export log does not contain PDF plus thirteen SVG plots and clean ERC")

    hold_rows = rows(ENG / "open-holds.csv")
    need(len(hold_rows) == 8 and all(row["state"] in {"OPEN", "NOT EXECUTED"} and row["gate_effect"] == "NONE - REMAINS OPEN/PARTIAL" and row["warning"] == WARNING for row in hold_rows), "eight holds are not fail-closed")
    authority = rows(ENG / "authority-boundary.csv")
    need(len(authority) == 4 and authority[0]["allowed"] == "TRUE" and all(row["allowed"] == "FALSE" for row in authority[1:]) and all(row["warning"] == WARNING for row in authority), "authority boundary changed")

    status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
    expected = {
        "identifier": IDENTIFIER, "round": "R224", "ecad_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "current_system_ecad": "V3-P1.15-CARRIER-CANDIDATE", "sheet_count": 13, "native_sheet_count": 13,
        "svg_export_count": 13, "erc_errors": 0, "erc_warnings": 0, "structural_export_checks_passed": 13,
        "internal_full_sheet_visual_review_complete": False, "independent_review_complete": False,
        "p118_accepted": False, "work_authority": False, "energization_authorized": False,
    }
    for key, expected_value in expected.items():
        need(status.get(key) == expected_value, f"package status {key} changed")
    need(status.get("warning") == WARNING, "package warning changed")

    for directory, expected_files in ((ENG, common), (OUT, common | {"index.html"})):
        manifest_rows = rows(directory / "file-manifest.csv")
        actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
        need({row["path"] for row in manifest_rows} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest_rows:
            path = directory / row["path"]
            need(digest(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {path}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release parity mismatch: {name}")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(page)
    need(parser.sheet_buttons == 13 and parser.images == 1, "web viewer does not expose 13 sheet controls and one controlled image")
    need({"sheet-search", "sheet-image", "sheet-frame", "previous", "next", "focus", "open-svg"} <= parser.ids, "web viewer controls missing")
    for token in (WARNING, IDENTIFIER, "P1.15 remains current", "P1.18 remains an unaccepted", "0 / 0", "font:16px", "font:600 14px", "overflow:auto", "data-zoom=\"2\"", "Focus schematic", ".workspace.focus", "location.hash"):
        need(token in page, f"web viewer token missing: {token}")
    need(".pdf" not in page.lower(), "web viewer links to a PDF")

    if failures:
        print(f"{IDENTIFIER} FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS: 13 native sheets / 13 SHA-bound KiCad SVGs / ERC 0 errors and 0 warnings")
    print("P1.15 remains current; P1.18, internal full-sheet visual review, independent review and every physical/work gate remain open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
