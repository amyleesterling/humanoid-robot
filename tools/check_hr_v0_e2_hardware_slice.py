#!/usr/bin/env python3
"""Validate the HR-V0 E2 control-only hardware slice."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []
    config = rows("e2-configuration-slice.csv")
    terminals = rows("e2-terminal-register.csv")
    sources = rows("e2-source-register.csv")
    holds = rows("e2-blocking-holds.csv")
    summary = json.loads((OUT / "e2-hardware-summary.json").read_text(encoding="utf-8"))
    guide = (OUT / "HR-V0_e2-hardware-guide.html").read_text(encoding="utf-8")

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(len(config) == 23, "expected 23 configuration rows")
    require(len(terminals) == 6, "expected six XT1 positions")
    require(len(sources) == 3, "expected three source-domain rows")
    require(len(holds) == 12, "expected twelve blocking holds")
    require(summary.get("identifier") == "HR-V0-E2-HW-P0.3", "E2 hardware identifier mismatch")
    require(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.14 / PCB-P0.9 / HR-V0-WD-PCBA-DATA-P0.2", "electrical baseline mismatch")
    require(summary.get("authorization") == "NOT AUTHORIZED", "authorization must remain denied")
    require({r["terminal"]: r["net"] for r in terminals} == {
        "XT1-01": "SAFETY_24V", "XT1-02": "SAFETY_0V", "XT1-03": "SR1_STATUS",
        "XT1-04": "SRA1_STATUS", "XT1-05": "K1_STATUS", "XT1-06": "K2_STATUS",
    }, "XT1 map differs from frozen candidate")
    combined = "\n".join(str(v) for row in config + terminals + sources + holds for v in row.values()) + guide
    for token in ("3209510", "3209523", "3030417", "3022218", "0828734", "WR9QI1660YL4NKITR6B", "YL4/C40337", "KPJX-PM-4S", "F24", "TP15/TP16/TP2", "TOOL/DEBUG CONNECTION ABSENT", "PHYSICALLY ABSENT", "LOAD POLES UNSOURCED AND UNWIRED", "NO FUSE LINK SELECTED", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        require(token in combined, f"required fail-closed token missing: {token}")
    require("GST40A24-P1J" not in combined and "DC PLUG-P1J-R7B" not in combined,
            "superseded 24 V conversion chain remains in E2 P0.2")
    require("JDBG1" not in combined, "removed installed debug connector remains in current E2 slice")
    require("PCB-P0.9" in combined and "HR-V0-WD-PCBA-DATA-P0.2" in combined and "42 native exact identity" in combined,
            "current watchdog PCB identity/assembly package is not synchronized")
    require("12 V actuator" in guide and "physically absent" in guide, "guide does not state actuator-source exclusion")
    require("font:16px" in guide and "font-size:1rem" in guide, "guide text floor is not explicit")
    require(all(row["warning"] == WARNING for row in config + terminals + sources + holds), "warning missing from a CSV row")
    if failures:
        print("HR-V0 E2 hardware slice: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("HR-V0 E2 hardware slice check passed: 23 configuration rows; 6 exact XT1 positions; 3 source-domain rows; 12 blocking holds")
    print("Actuator source/branches remain physically absent or disconnected; K1/K2 load poles remain unsourced and unwired")
    print(WARNING)


if __name__ == "__main__":
    main()
