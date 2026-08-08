#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-24V-IF-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-24v-interface-p0.1"
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
    summary = json.loads((OUT / "interface-summary.json").read_text(encoding="utf-8"))
    guide = (OUT / "HR-V0_24v-interface-guide.html").read_text(encoding="utf-8")

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(len(bom) == 6 and len(pins) == 8 and len(holds) == 8 and len(sources) == 5, "package row counts changed")
    require(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.10", "electrical baseline mismatch")
    require(summary.get("release") == "NOT AUTHORIZED", "interface appears released")
    require({(r["reference"], r["pin"]): r["net"] for r in pins if r["reference"] == "J24"} == {("J24", "1"): "SAFETY_24V_RAW", ("J24", "2"): "SAFETY_0V", ("J24", "3"): "SAFETY_0V", ("J24", "4"): "SAFETY_24V_RAW"}, "J24 pin map changed")
    combined = "\n".join(str(value) for row in bom + pins + holds + sources for value in row.values()) + guide
    for token in ("GST40A24-P1J", "DC PLUG-P1J-R7B", "KPJX-PM-4S", "F24", "COMPATIBILITY HOLD", "SELECTION REQUIRED", "no parallel-contact current-sharing", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        require(token.lower() in combined.lower(), f"required fail-closed token missing: {token}")
    require("font:16px" in guide and "font-size:14px" in guide, "guide text floor is not explicit")
    require(all(row.get("warning") == WARNING for row in bom + pins + holds + sources), "warning missing from CSV row")
    if failures:
        print("HR-V0 24 V interface check: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("HR-V0 24 V interface check passed: exact conversion/jack candidates; 8 pin records; 8 open holds")
    print("Compatibility, current application, protection, physical design and test remain unreleased")
    print(WARNING)


if __name__ == "__main__":
    main()
