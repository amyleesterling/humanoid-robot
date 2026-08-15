#!/usr/bin/env python3
"""Validate the fail-closed HR-V0 panel conductor engineering basis."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/panel-conductor-basis-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {
        "source-register.csv", "conductor-family-candidates.csv", "terminal-compatibility.csv",
        "endpoint-conductor-candidate-schedule.csv", "load-envelope.csv", "engineering-screens.csv",
        "unresolved-selection-register.csv", "authority-boundary.csv", "package-status.json", "index.html",
    }
    need(OUT.is_dir(), "package directory missing")
    if OUT.is_dir():
        need({p.name for p in OUT.iterdir() if p.is_file()} == expected, "package file set changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {
        "identifier": "HR-V0-PANEL-COND-P0.1", "round": "R221", "source_records": 8,
        "endpoint_records": 66, "fixed_internal_candidate_endpoints": 56,
        "door_loom_unselected_endpoints": 10, "terminal_family_records": 7, "open_holds": 12,
    }.items():
        need(status.get(key) == value, f"status changed: {key}")
    for key in (
        "point_to_point_schedule_released", "wire_order_codes_released", "cut_lengths_released",
        "termination_process_released", "f24_selected", "procurement_authorized",
        "fabrication_authorized", "assembly_authorized", "connection_authorized",
        "powered_test_authorized", "motion_authorized", "energization_authorized",
    ):
        need(status.get(key) is False, f"status falsely authorizes {key}")
    need(status.get("warning") == WARNING, "status warning changed")

    source_rows = rows("source-register.csv")
    need(len(source_rows) == 8 and all(r["official_url"].startswith("https://") for r in source_rows), "primary source register incomplete")
    need(all(r["warning"] == WARNING for r in source_rows), "source warning missing")

    candidate_rows = rows("conductor-family-candidates.csv")
    by_scope = {r["scope"]: r for r in candidate_rows}
    need(by_scope.get("fixed internal panel point-to-point", {}).get("family_or_selection") == "Belden 3057 family", "fixed candidate changed")
    need(by_scope.get("door loom for S0/S1/S2/H1", {}).get("family_or_selection") == "SELECTION REQUIRED", "door loom falsely selected")
    need(all(r["warning"] == WARNING for r in candidate_rows), "candidate warning missing")

    terminal = rows("terminal-compatibility.csv")
    need(len(terminal) == 7, "terminal-family coverage changed")
    dispositions = {r["references"]: r["candidate_disposition"] for r in terminal}
    need(dispositions.get("K1/K2 control terminals") == "16 AWG GAUGE FIT; 22 AWG REJECTED", "Schneider minimum-size control lost")
    need(dispositions.get("S0") == "NOT PROVEN", "S0 terminal falsely proven")
    need("16 AWG FERRULE REJECTED" in dispositions.get("watchdog PCB terminals (interface caution)", ""), "watchdog ferrule incompatibility lost")

    schedule = rows("endpoint-conductor-candidate-schedule.csv")
    need(len(schedule) == 66 and len({r["wire_number"] for r in schedule}) == 66, "endpoint coverage changed")
    fixed = [r for r in schedule if r["candidate_state"].startswith("FIXED")]
    door = [r for r in schedule if r["candidate_state"].startswith("NO DYNAMIC")]
    need(len(fixed) == 56 and len(door) == 10, "fixed/door split changed")
    need({r["reference"] for r in door} == {"S0", "S1", "S2", "H1"}, "door reference set changed")
    for row in schedule:
        for field in (
            "exact_color_order_code", "cut_length_mm", "listed_endpoint_termination",
            "opposite_endpoint", "opposite_endpoint_termination", "route",
        ):
            need(row[field] == "SELECTION REQUIRED", f"{row['wire_number']} invents {field}")
        need(row["physical_model"] == "ENDPOINT RECORD - OPPOSITE END NOT YET FROZEN", f"{row['wire_number']} implies point-to-point completion")
        need(row["release_state"] == "NOT RELEASED" and row["warning"] == WARNING, f"{row['wire_number']} release boundary weakened")
    need(all(r["conductor_family_candidate"] == "SELECTION REQUIRED" for r in door), "door wire candidate invented")
    need(all(r["conductor_family_candidate"] == "Belden 3057 family" for r in fixed), "fixed family candidate changed")

    screens = rows("engineering-screens.csv")
    by_subject = {r["subject"]: r for r in screens}
    need(by_subject.get("Belden 3057 voltage drop", {}).get("result") == "NOT CALCULATED", "voltage drop falsely closed")
    need(by_subject.get("F24 coordination", {}).get("result") == "NOT CALCULATED / SELECTION REQUIRED", "F24 falsely selected")

    holds = rows("unresolved-selection-register.csv")
    need(len(holds) == 12 and {r["hold_id"] for r in holds} == {f"PCS-HOLD-{i:03d}" for i in range(1, 13)}, "hold coverage changed")
    need(all(r["state"] == "SELECTION REQUIRED" and r["accepted"] == "FALSE" and r["warning"] == WARNING for r in holds), "hold falsely closed")

    authority = rows("authority-boundary.csv")
    need(len(authority) == 5 and sum(r["permitted_by_this_package"] == "TRUE" for r in authority) == 1, "authority scope changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-PANEL-COND-P0.1", "font:clamp(16px", "font-size:14px", "56</b>", "10</b>", "22 AWG", "SELECTION REQUIRED"):
        need(token in page, f"interactive guide missing {token}")

    if failures:
        print("HR-V0 panel conductor basis P0.1: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 panel conductor basis P0.1: PASS")
    print("56 fixed endpoint candidates; 10 door endpoints unselected; 12 holds open")
    print("No wire order, cut, termination, protection, connection, powered-test, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
