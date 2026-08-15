#!/usr/bin/env python3
"""Validate the R234 P1.21 SRA1-supply watchdog package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
OUT = ROOT / "release/hr-v0/p121-sra1-supply-watchdog-p0.1"
SAFETY = ROOT / "safety/hr-v0-p121-sra1-supply-watchdog-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    expected = {
        ("SR1","14"): "SRA1_S12", ("SR1","24"): "SRA1_S22",
        ("SRA1","A1"): "SRA1_A1_WD_GATED", ("KWD1","11"): "SAFETY_24V",
        ("KWD1","14"): "WD_SRA1_SUPPLY_INTERMEDIATE", ("KWD2","11"): "WD_SRA1_SUPPLY_INTERMEDIATE",
        ("KWD2","14"): "SRA1_A1_WD_GATED",
    }
    schedule = {(r["reference"],r["terminal"]):r["net"] for r in rows(P121 / "connector-schedule.csv")}
    for key, net in expected.items():
        need(schedule.get(key) == net, f"P1.21 terminal drift: {key}")
    need(len(rows(P121 / "connector-schedule.csv")) == 340, "terminal count changed")
    need(len(rows(P121 / "net-schedule.csv")) == 106, "named net count changed")
    need(len(rows(P121 / "bom.csv")) == 82, "BOM row count changed")
    erc = (P121 / "validation/project-button-v3-p1.21-sra1-supply-watchdog-candidate-erc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "ERC is not 0/0")
    for directory in (OUT, SAFETY):
        delta = rows(directory / "topology-delta.csv")
        need(len(delta) == 7, f"{directory}: delta count")
        need(len(rows(directory / "fault-truth-table.csv")) == 14, f"{directory}: fault count")
        need(len(rows(directory / "supply-duty-screen.csv")) == 9, f"{directory}: screen count")
        need(len(rows(directory / "open-holds.csv")) == 11, f"{directory}: hold count")
        need(all(r["warning"] == WARNING for name in ("topology-delta.csv","safety-allocation-boundary.csv","supply-duty-screen.csv","fault-truth-table.csv","source-register.csv","open-holds.csv") for r in rows(directory / name)), f"{directory}: warning missing")
        status = json.loads((directory / "parity-summary.json").read_text(encoding="utf-8"))
        need(status["p121"] == "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", f"{directory}: identity")
        need(status["p115_current"] and not status["p121_accepted"], f"{directory}: configuration boundary")
        need(status["watchdog_safety_credit"] == "NONE" and not status["work_authority"], f"{directory}: authority boundary")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need(WARNING in page and "font-size:14px" in page and "P1.15 remains current" in page, "HTML boundary/legibility missing")
    manifest = {r["file"]:r for r in rows(OUT / "file-manifest.csv")}
    actual = {p.name:p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "manifest membership mismatch")
    for name, path in actual.items():
        data = path.read_bytes()
        need(manifest[name]["size_bytes"] == str(len(data)), f"{name}: size mismatch")
        need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest(), f"{name}: hash mismatch")
    print("HR-V0 P1.21 SRA1-supply watchdog check passed: 7 changes, 14 faults, ERC 0/0")
    print(WARNING)


if __name__ == "__main__":
    main()
