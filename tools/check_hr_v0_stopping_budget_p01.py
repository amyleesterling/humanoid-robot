#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-STOP-BUDGET-P0.1 / R124."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    budget = rows("controls/hr-v0-stopping-budget-p0.1.csv")
    form = rows("tests/forms/hr-v0-stopping-time-template-p0.1.csv")
    control = (ROOT / "docs/control.md").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-stopping-budget-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/stopping-budget-p0.1/index.html").read_text(encoding="utf-8")
    actuator = json.loads((ROOT / "firmware/supervisor/actuator-config.json").read_text(encoding="utf-8"))
    stop = json.loads((ROOT / "cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-analysis.json").read_text(encoding="utf-8"))

    require(len(budget) == 12, "stopping-budget register must contain 12 controlled rows", failures)
    require([item["record_id"] for item in budget] == [f"SB-{index:03d}" for index in range(1, 13)], "stopping-budget IDs changed", failures)
    by_id = {item["record_id"]: item for item in budget}
    for record_id, speed, expected_time in (("SB-001", 10.0, 300.0), ("SB-002", 30.0, 100.0)):
        item = by_id[record_id]
        actual = float(item["available_travel_deg"]) / float(item["commanded_speed_deg_s"]) * 1000.0
        require(abs(actual - expected_time) < 1e-9 and abs(float(item["time_to_metal_stop_ms"]) - expected_time) < 1e-9, f"{record_id} traversal arithmetic changed", failures)
    require("3.000 deg" in by_id["SB-003"]["additional_delay_or_travel"], "DF-01 setup travel screen changed", failures)
    require("9.000 deg" in by_id["SB-004"]["additional_delay_or_travel"] and "6.000 deg" in by_id["SB-004"]["additional_delay_or_travel"], "DF-01 automatic travel screen changed", failures)
    require("0.240 deg" in by_id["SB-005"]["additional_delay_or_travel"], "10 deg/s contactor component screen changed", failures)
    require("0.720 deg" in by_id["SB-006"]["additional_delay_or_travel"], "30 deg/s contactor component screen changed", failures)
    for record_id in ("SB-010", "SB-011", "SB-012"):
        require(by_id[record_id]["metal_stop_deg"] == "DESIGN REQUIRED" and by_id[record_id]["screen_result"] == "PROHIBITS MOTION RELEASE", f"{record_id} missing-stop hold weakened", failures)

    require(len(form) == 16, "stopping-time form must contain 16 blank cases", failures)
    require(all(item["status"] == "NOT EXECUTED" and item["authorized"] == "NOT AUTHORIZED" for item in form), "stopping-time form claims execution or authorization", failures)
    measured_fields = ("input_transition_ms", "contactor_pole_open_ms", "rail_below_torque_threshold_ms", "motion_stop_ms", "total_stop_time_ms", "residual_travel_deg")
    require(all(not item[field] for item in form for field in measured_fields), "stopping-time form contains invented physical results", failures)

    j2 = actuator["actuators"]["J2"]
    require((j2["minimum_engineering"], j2["maximum_engineering"]) == (15.0, 115.0), "active J2 actuator binding is not 15..115 degrees", failures)
    require(abs(float(stop["target_metal_contact_deg"]) - 118.0) < 1e-9, "J2 positive metal-stop target changed", failures)
    require("| Position | -20° to +70° | 15° to 115° |" in control, "active control narrative is not bound to J2 15..115 degrees", failures)
    require("| Position | -20° to +70° | 15° to 125° |" not in control, "obsolete active 125-degree J2 table returned", failures)
    require("zero safety credit" in doc.lower() and "EG-026" in doc, "stopping-budget document lost fail-closed boundary", failures)
    require("font:17px" in guide and "font-size:12px" in guide and "DF-01" in guide and "EG-026" in guide, "interactive guide legibility or warning controls changed", failures)

    if failures:
        print("HR-V0 stopping-budget P0.1 check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 stopping-budget P0.1 check passed: 12 calculation/hold rows and 16 unexecuted test cases")
    print("J2 current command binding 15..115 deg; nominal positive metal backup 118 deg; DF-01 retains zero safety credit")
    print("EG-026 remains OPEN; PRELIMINARY - NOT APPROVED FOR MOTION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
