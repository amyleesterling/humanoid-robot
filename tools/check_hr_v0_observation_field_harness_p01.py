#!/usr/bin/env python3
"""Fail-closed validation for the R206 observation field-harness candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/harness/hr-v0-observation-field-harness-p0.1"
WEB = ROOT / "release/hr-v0/observation-field-harness-p0.1"
IDENTIFIER = "HR-V0-OBSERVATION-FIELD-HARNESS-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {"README.md", "SOURCE-MANIFEST.csv", "acceptance-matrix.csv", "conductor-schedule.csv", "field-harness.svg", "harness-bom.csv", "index.html", "interface-control.csv", "package-status.json", "route-length-calculation.csv", "selection-holds.csv", "source-register.csv", "termination-process.csv"}
    for directory in (ENG, WEB):
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
        need(actual == expected, f"package membership changed: {directory}")
        manifest = rows(directory / "SOURCE-MANIFEST.csv")
        need({row["file"] for row in manifest} == expected - {"SOURCE-MANIFEST.csv"}, f"manifest membership changed: {directory.name}")
        for row in manifest:
            path = directory / row["file"]
            need(row["sha256"] == digest(path).upper(), f"manifest digest mismatch: {directory.name}/{row['file']}")
    for name in expected - {"SOURCE-MANIFEST.csv"}:
        need((ENG / name).read_bytes() == (WEB / name).read_bytes(), f"engineering/web mirror differs: {name}")

    status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R206", "package identity changed")
    for key, value in {"conductor_rows": 5, "interface_rows": 6, "selection_holds": 12, "acceptance_rows": 12}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(status.get("digital_mapping_complete") is True, "digital mapping is not recorded complete")
    need(abs(status.get("rounded_centerline_screen_mm", 0) - round(276 + 2 * (math.pi / 2 - 2) * 15, 1)) < 0.01, "rounded route calculation changed")
    for key, value in status.items():
        if key.endswith("_authorized") or key in {"cut_lengths_selected", "physical_route_accepted", "harness_released", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "safety_credit"}:
            need(value is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")

    conductors = rows(ENG / "conductor-schedule.csv")
    expected_map = {
        "W9008": ("SR1_STATUS", "XT1-03", "OBS1 JFIELD1:1", "3051 WB005", "white/black"),
        "W9009": ("SRA1_STATUS", "XT1-04", "OBS1 JFIELD1:2", "3051 WO005", "white/orange"),
        "W9010": ("K1_STATUS", "XT1-05", "OBS1 JFIELD1:3", "3051 WV005", "white/violet"),
        "W9011": ("K2_STATUS", "XT1-06", "OBS1 JFIELD1:4", "3051 WY005", "white/yellow"),
        "W9007": ("SAFETY_0V", "XT1-02", "OBS1 JFIELD1:5", "3051 WU005", "white/blue"),
    }
    need(len(conductors) == 5 and {row["wire_number"] for row in conductors} == set(expected_map), "five-wire membership changed")
    for row in conductors:
        expected_row = expected_map.get(row["wire_number"])
        if expected_row:
            net, start, end, part, color = expected_row
            need((row["net"], row["from"], row["to"]) == (net, start, end), f"interface mapping changed: {row['wire_number']}")
            need(part in row["wire_candidate"] and row["color"] == color, f"wire/color candidate changed: {row['wire_number']}")
        need(row["cut_length_mm"] == "SELECTION REQUIRED", f"cut length prematurely selected: {row['wire_number']}")
        need(row["termination"] == "direct-stripped flexible conductor; no ferrule candidate", f"termination candidate changed: {row['wire_number']}")
        need(row["warning"] == WARNING, f"warning changed: {row['wire_number']}")

    interface = rows(ENG / "interface-control.csv")
    need(len(interface) == 6, "expected five conductors plus one deliberate no-connect")
    nc = [row for row in interface if row["receiver_terminal"] == "OBS1 JFIELD1:6"]
    need(len(nc) == 1 and nc[0]["mapping"] == "DELIBERATE NO-CONNECT" and nc[0]["physical_state"] == "MUST REMAIN UNWIRED", "JFIELD1:6 no-connect boundary changed")
    process = rows(ENG / "termination-process.csv")
    need(len(process) == 2, "expected two termination process rows")
    by_end = {row["end"]: row for row in process}
    need("8-10 mm" in by_end["XT1"]["candidate_preparation"] and "push button" in by_end["XT1"]["candidate_preparation"], "XT1 preparation changed")
    need("5 mm" in by_end["JFIELD1"]["candidate_preparation"] and by_end["JFIELD1"]["torque"] == "0.22-0.25 N m", "JFIELD1 preparation/torque changed")

    source = rows(ENG / "source-register.csv")
    need(len(source) == 7, "source-register row count changed")
    for token in ("3209510", "1751280", "revision 0.118 dated 2026-06-30"):
        need(any(token in " ".join(row.values()) for row in source), f"primary-source evidence missing: {token}")
    for row in source:
        if row["manufacturer"] == "Project Button":
            path = ROOT / row["uri"]
            need(path.is_file(), f"controlled source missing: {row['uri']}")
            name = row["document"]
            need(status["source_hashes"].get(name) == digest(path), f"controlled source hash mismatch: {name}")

    holds = rows(ENG / "selection-holds.csv")
    acceptance = rows(ENG / "acceptance-matrix.csv")
    need(len(holds) == 12 and all(row["state"].startswith("OPEN") and row["warning"] == WARNING for row in holds), "all 12 holds must remain open")
    need(len(acceptance) == 12 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "all 12 acceptance rows must remain unexecuted/open")

    page = (WEB / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", WARNING, "Cut length: SELECTION REQUIRED", "Five wires, exact endpoints", "../../../electrical/"):
        need(token in page or token in (WEB / "field-harness.svg").read_text(encoding="utf-8"), f"web guide token missing: {token}")
    need("font-size:13px" not in page and "font-size:12px" not in page, "web interface text was reduced below 14 px")

    if failures:
        print(f"{IDENTIFIER} FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS")
    print("  exact five-wire mapping and catalog/color candidates; JFIELD1:6 remains unconnected")
    print("  12 selection holds and 12 acceptance rows remain open")
    print("  no procurement, fabrication, connection, powered-test, motion, safety, or energization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
