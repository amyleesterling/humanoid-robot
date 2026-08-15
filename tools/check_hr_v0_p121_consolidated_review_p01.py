#!/usr/bin/env python3
"""Validate the R238 consolidated P1.21 review surface."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/p121-consolidated-review-p0.1"
REVIEW = ROOT / "electrical/reviews/hr-v0-p121-consolidated-review-p0.1"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def main() -> None:
    p119_gen = (ROOT / "tools/generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate.py").read_text(encoding="utf-8")
    p120_gen = (ROOT / "tools/generate_hr_v0_electrical_v3_p121_sra1_supply_watchdog_candidate.py").read_text(encoding="utf-8")
    need("from generate_hr_v0_electrical_v3_p119_visual_correction_candidate import transformed_source as p119_source" in p119_gen, "P1.20 no longer inherits P1.19")
    need("from generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate import transformed_source as p120_source" in p120_gen, "P1.21 no longer inherits P1.20")
    need(len(list(P121.glob("*.kicad_sch"))) == 13, "native sheet count changed")
    erc = (P121 / "validation/project-button-v3-p1.21-sra1-supply-watchdog-candidate-erc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "P1.21 ERC is not 0/0")
    for directory in (OUT, REVIEW):
        need(len(rows(directory / "lineage-register.csv")) == 4, "lineage count changed")
        need(len(rows(directory / "sheet-review-register.csv")) == 13, "sheet review coverage changed")
        need(len(rows(directory / "terminal-delta.csv")) == 6, "P1.19-to-P1.21 delta count changed")
        need(len(rows(directory / "source-register.csv")) == 9, "source register count changed")
        need(len(rows(directory / "open-holds.csv")) == 11, "open hold count changed")
        status = json.loads((directory / "package-status.json").read_text(encoding="utf-8"))
        need(status["current_candidate"] == "V3-P1.15-CARRIER-CANDIDATE", "current candidate promoted")
        need(status["consolidated_review_candidate"] == "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE" and not status["p121_accepted"], "P1.21 boundary changed")
        need(status["native_sheets"] == 13 and status["components"] == 84 and status["named_nets"] == 106, "count drift")
        need(status["erc_errors"] == 0 and status["erc_warnings"] == 0 and status["erc_scope"] == "CONNECTIVITY_AND_ANNOTATION_ONLY", "ERC boundary changed")
        need(not status["qualified_review_complete"] and not status["functional_safety_approved"] and not status["work_authority"], "authority promoted")
        for name in ("lineage-register.csv", "sheet-review-register.csv", "terminal-delta.csv", "source-register.csv", "open-holds.csv"):
            need(all(row["warning"] == WARNING for row in rows(directory / name)), f"warning missing in {name}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "One candidate, all thirteen native sheets", "P1.15 remains current", "P1.21 remains unaccepted", "font-size:14px"):
        need(token in page, f"interactive guide token missing: {token}")
    need("font-size:12px" not in page and "font-size:11px" not in page, "undersized text introduced")
    manifest = {row["file"]: row for row in rows(OUT / "file-manifest.csv")}
    actual = {p.name: p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "manifest membership mismatch")
    for name, path in actual.items():
        data = path.read_bytes()
        need(manifest[name]["size_bytes"] == str(len(data)), f"manifest size mismatch: {name}")
        need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest().upper(), f"manifest hash mismatch: {name}")
    print("PASS: R238 P1.21 is lineage-bound as the unaccepted consolidated native-KiCad review candidate")
    print(WARNING)


if __name__ == "__main__":
    main()
