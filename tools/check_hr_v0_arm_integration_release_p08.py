#!/usr/bin/env python3
"""Fail-closed validation for the R214 integrated-arm release surface."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/arm-architecture-p0.8-dwg-integrated"
DOC = ROOT / "docs/hr-v0-arm-architecture-p0.8-dwg-integrated.md"
IDENTIFIER = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    expected = {"index.html", "package-status.json", "evidence-summary.csv", "open-holds.csv", "source-hash-register.csv", "file-manifest.csv"}
    need(OUT.is_dir() and {path.name for path in OUT.iterdir() if path.is_file()} == expected, "release package membership changed")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R214", "identity changed")
    need((status.get("controlled_part_count"), status.get("collision_pose_count"), status.get("continuous_pair_count"), status.get("open_hold_count")) == (5, 40001, 69, 12), "evidence counts changed")
    for field in ("physical_article_exists", "physical_test_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(field) is False, f"{field} must remain false")
    need(status.get("warning") == WARNING, "warning changed")
    need(len(rows(OUT / "evidence-summary.csv")) == 6, "evidence-summary count changed")
    need(len(rows(OUT / "open-holds.csv")) == 12 and all(row["state"] == "OPEN" for row in rows(OUT / "open-holds.csv")), "holds changed or closed")
    for row in rows(OUT / "source-hash-register.csv"):
        source = ROOT / row["source_path"]
        need(source.is_file() and digest(source) == row["sha256"], f"source hash changed: {row['source_path']}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "Five corrected metal parts", "Interactive 3D model", "Twelve holds remain open", WARNING):
        need(token in page, f"guide token missing: {token}")
    doc = DOC.read_text(encoding="utf-8")
    for token in (IDENTIFIER, "40,001-pose", "69-pair", "121.643289", "does not authorize"):
        need(token in doc, f"document token missing: {token}")
    manifest = rows(OUT / "file-manifest.csv")
    actual = {path.name for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
    need({row["path"] for row in manifest} == actual, "manifest membership changed")
    for row in manifest:
        path = OUT / row["path"]
        need(digest(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {path}")
    if failures:
        print("HR-V0 P0.8 integrated-arm release surface FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 P0.8 integrated-arm release surface PASS")
    print("  interactive guide + 6 evidence records + 12 open holds; every authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
