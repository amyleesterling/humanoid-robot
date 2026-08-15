#!/usr/bin/env python3
"""Validate the R231 Sol R12 current-disposition package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "sol-r12-current-disposition-r231"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    expected = {f"B-{number:03d}" for number in range(1, 19)}
    records = rows(OUT / "blocker-disposition.csv")
    need({row["finding_id"] for row in records} == expected, "Sol blocker ID set is incomplete or duplicated")
    need(len(records) == 18, "expected exactly 18 blocker dispositions")
    allowed = {"PARTIALLY_ADDRESSED_OPEN", "OPEN_BLOCKER", "OPEN_HR30_BLOCKER"}
    need(all(row["current_disposition"] in allowed for row in records), "invalid or closed disposition found")
    need(all(row["warning"] == WARNING for row in records), "warning missing from blocker register")
    need(all(row["current_evidence"] and row["evidence_location"] for row in records), "empty evidence boundary")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-SOL-R12-STATUS-R231", "identifier changed")
    need(status["blockers_qualified_closed"] == 0, "R231 must not claim qualified closure")
    need(status["partially_addressed_open"] == 12, "partial count changed")
    need(status["open_hr_v0_blocker"] == 1, "HR-V0 open count changed")
    need(status["open_hr30_blocker"] == 5, "HR-30 open count changed")
    need(not status["independent_review"] and not status["qualified_review"] and not status["work_authority"], "authority boundary changed")
    need(status["warning"] == WARNING, "status warning changed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need(WARNING in page and "zero of the 18 findings" in page, "HTML boundary missing")
    manifest = {row["file"]: row for row in rows(OUT / "file-manifest.csv")}
    actual = {path.name: path for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "package manifest membership mismatch")
    for name, path in actual.items():
        data = path.read_bytes()
        need(manifest[name]["size_bytes"] == str(len(data)), f"{name}: size mismatch")
        need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest(), f"{name}: hash mismatch")
        need(manifest[name]["warning"] == WARNING, f"{name}: manifest warning missing")
    print("HR-V0 Sol R12 R231 current-disposition check passed: 18 / 18 blocker records; 0 qualified closed")
    print(WARNING)


if __name__ == "__main__":
    main()
