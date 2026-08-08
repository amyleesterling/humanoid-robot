#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-24V-IF-P0.2."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-24v-interface-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []
    bom = rows("interface-bom.csv")
    pins = rows("pin-allocation.csv")
    holds = rows("compatibility-holds.csv")
    sources = rows("source-register.csv")
    loads = rows("load-budget.csv")
    summary = json.loads((OUT / "interface-summary.json").read_text(encoding="utf-8"))
    guide = (OUT / "HR-V0_24v-interface-guide.html").read_text(encoding="utf-8")

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(len(bom) == 5 and len(pins) == 10 and len(holds) == 8 and len(sources) == 10 and len(loads) == 5, "package row counts changed")
    require(summary.get("identifier") == "HR-V0-24V-IF-P0.2", "interface identifier mismatch")
    require(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.11", "electrical baseline mismatch")
    require(summary.get("release") == "NOT AUTHORIZED", "interface appears released")
    require({(r["reference"], r["pin"]): r["net"] for r in pins if r["reference"] == "J24"} == {("J24", "1"): "SAFETY_24V_RAW", ("J24", "2"): "NO NET / NO CONNECTION", ("J24", "3"): "SAFETY_0V", ("J24", "4"): "NO NET / NO CONNECTION"}, "J24 pin map changed")
    require({(r["reference"], r["pin"]): r["net"] for r in pins if r["reference"] == "PSU2"} == {("PSU2", "YL4-1"): "SAFETY_24V_RAW", ("PSU2", "YL4-2"): "NO NET / NO CONNECTION", ("PSU2", "YL4-3"): "SAFETY_0V", ("PSU2", "YL4-4"): "NO NET / NO CONNECTION"}, "PSU2 YL4 pin map changed")
    load_w = sum(float(row["subtotal_w"]) for row in loads)
    load_a = sum(float(row["current_a_at_24v"]) for row in loads)
    require(abs(load_w - 27.024) < 0.0005 and abs(load_a - 1.126) < 0.00001, "load-screen sum changed")
    require(summary.get("screened_continuous_w") == 27.024 and summary.get("headroom_through_40c_w") == 12.976 and summary.get("headroom_at_50c_80pct_w") == 4.976, "source/load headroom calculation changed")
    require("NOT RELEASED" in summary.get("load_screen_release", ""), "load screen appears released")
    combined = "\n".join(str(value) for row in bom + pins + holds + sources + loads for value in row.values()) + guide
    for token in ("WR9QI1660YL4NKITR6B", "YL4/C40337", "KPPX-4P", "KPJX-PM-4S", "F24", "SOURCE-CORD FIT", "SELECTION REQUIRED", "DO NOT REPURPOSE", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        require(token.lower() in combined.lower(), f"required fail-closed token missing: {token}")
    require("GST40A24-P1J" not in combined and "DC PLUG-P1J-R7B" not in combined, "superseded conversion chain remains in P0.2")
    require("font:16px" in guide and "font-size:14px" in guide, "guide text floor is not explicit")
    require(all(row.get("warning") == WARNING for row in bom + pins + holds + sources + loads), "warning missing from CSV row")
    if failures:
        print("HR-V0 24 V interface check: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("HR-V0 24 V interface check passed: factory locking source candidate; 10 pin records; 8 open holds; 5 load rows")
    print("Source-cord fit, startup, protection, physical design and test remain unreleased")
    print(WARNING)


if __name__ == "__main__":
    main()
