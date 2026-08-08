#!/usr/bin/env python3
"""Validate the HR-V0 E2 control-only hardware slice."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.1"
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

    require(len(config) == 22, "expected 22 configuration rows")
    require(len(terminals) == 6, "expected six XT1 positions")
    require(len(sources) == 3, "expected three source-domain rows")
    require(len(holds) == 12, "expected twelve blocking holds")
    require(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.9", "electrical baseline mismatch")
    require(summary.get("authorization") == "NOT AUTHORIZED", "authorization must remain denied")
    require({r["terminal"]: r["net"] for r in terminals} == {
        "XT1-01": "SAFETY_24V", "XT1-02": "SAFETY_0V", "XT1-03": "SR1_STATUS",
        "XT1-04": "SRA1_STATUS", "XT1-05": "K1_STATUS", "XT1-06": "K2_STATUS",
    }, "XT1 map differs from frozen candidate")
    combined = "\n".join(str(v) for row in config + terminals + sources + holds for v in row.values()) + guide
    for token in ("3209510", "3209523", "3030417", "3022218", "0828734", "PHYSICALLY ABSENT", "LOAD POLES UNSOURCED AND UNWIRED", "NO FUSE LINK SELECTED", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        require(token in combined, f"required fail-closed token missing: {token}")
    require("12 V actuator" in guide and "physically absent" in guide, "guide does not state actuator-source exclusion")
    require("font:16px" in guide and "font-size:1rem" in guide, "guide text floor is not explicit")
    require(all(row["warning"] == WARNING for row in config + terminals + sources + holds), "warning missing from a CSV row")
    if failures:
        print("HR-V0 E2 hardware slice: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("HR-V0 E2 hardware slice check passed: 22 configuration rows; 6 exact XT1 positions; 3 source-domain rows; 12 blocking holds")
    print("Actuator source/branches remain physically absent or disconnected; K1/K2 load poles remain unsourced and unwired")
    print(WARNING)


if __name__ == "__main__":
    main()
