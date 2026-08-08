#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-COMPUTE-IF-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-compute-debug-interface-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []
    pins = rows("pin-allocation.csv")
    holds = rows("compatibility-holds.csv")
    sources = rows("source-register.csv")
    summary = json.loads((OUT / "interface-summary.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "firmware" / "supervisor" / "compute-interface-config.json").read_text(encoding="utf-8"))
    guide = (OUT / "HR-V0_compute-debug-interface-guide.html").read_text(encoding="utf-8")

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(len(pins) == 9 and len(holds) == 10 and len(sources) == 6, "package row counts changed")
    require(summary.get("identifier") == "HR-V0-COMPUTE-IF-P0.1", "interface identifier mismatch")
    require(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.12", "electrical baseline mismatch")
    require(summary.get("installed_debug_connector") == "NONE", "an installed debug connector appears released")
    require(summary.get("release") == "NOT AUTHORIZED" and summary.get("safety_credit") == "NONE", "release or safety-credit boundary changed")
    pin_map = {(row["reference"], row["pin"]): row["net"] for row in pins}
    expected = {("PI1", "USB-C-VBUS"): "COMPUTE_5V", ("PI1", "USB-C-GND"): "COMPUTE_0V", ("PI1", "HDR40-6"): "COMPUTE_0V", ("PI1", "HDR40-11"): "PI_HEARTBEAT", ("JWH1", "1"): "PI_HEARTBEAT", ("JWH1", "2"): "COMPUTE_0V", ("TP15", "1"): "WD_SWDIO", ("TP16", "1"): "WD_SWCLK", ("TP2", "1"): "SAFETY_0V"}
    require(pin_map == expected, "compute/debug pin allocation changed")
    heartbeat = config.get("heartbeat", {})
    debug = config.get("watchdog_debug", {})
    require(config.get("identifier") == "HR-V0-COMPUTE-IF-P0.1", "firmware binding identifier mismatch")
    require(heartbeat.get("gpio_numbering") == "BCM" and heartbeat.get("gpio") == 17 and heartbeat.get("physical_header_pin") == 11 and heartbeat.get("return_physical_header_pin") == 6, "firmware heartbeat binding changed")
    require("HIGH_IMPEDANCE" in heartbeat.get("startup_state", "") and heartbeat.get("runtime_backend") == "SELECTION REQUIRED" and heartbeat.get("safety_credit") == "NONE", "fail-closed heartbeat boundary changed")
    require(debug.get("installed_connector") == "NONE" and debug.get("programmer") == "SELECTION REQUIRED" and debug.get("fixture") == "SELECTION REQUIRED" and debug.get("back_power_or_bypass") == "PROHIBITED", "debug boundary changed")
    combined = "\n".join(str(value) for row in pins + holds + sources for value in row.values()) + guide + json.dumps(config)
    for token in ("GPIO17", "HDR40-11", "HDR40-6", "TP15", "TP16", "TP2", "SELECTION REQUIRED", "no safety credit", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        require(token.lower() in combined.lower(), f"required fail-closed token missing: {token}")
    require("JDBG1" not in combined and "TBD-GPIO-HB" not in combined, "superseded invented/TBD interface remains")
    require("font:16px" in guide and "font-size:14px" in guide, "guide text floor is not explicit")
    require(all(row.get("warning") == WARNING for row in pins + holds + sources), "warning missing from CSV row")
    if failures:
        print("HR-V0 compute/debug interface check: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("HR-V0 compute/debug interface check passed: GPIO17/header 11; header 6 return; TP15/TP16/TP2; no installed debug connector")
    print("Harness, runtime, timing, fixture, physical evidence and qualified review remain open")
    print(WARNING)


if __name__ == "__main__":
    main()
