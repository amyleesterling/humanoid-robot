#!/usr/bin/env python3
"""Validate the R235 P1.21 manufacturer-RFI and no-load evidence package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
DIRECTORIES = (
    ROOT / "electrical/reviews/hr-v0-p121-application-evidence-p0.1",
    ROOT / "safety/hr-v0-p121-application-evidence-p0.1",
    ROOT / "release/hr-v0/p121-application-evidence-p0.1",
)
RELEASE = DIRECTORIES[2]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    schedule = {(r["reference"], r["terminal"]): r["net"] for r in rows(P121 / "connector-schedule.csv")}
    for terminal, net in {
        ("KWD1", "11"): "SAFETY_24V",
        ("KWD1", "14"): "WD_SRA1_SUPPLY_INTERMEDIATE",
        ("KWD2", "11"): "WD_SRA1_SUPPLY_INTERMEDIATE",
        ("KWD2", "14"): "SRA1_A1_WD_GATED",
        ("SRA1", "A1"): "SRA1_A1_WD_GATED",
        ("SR1", "14"): "SRA1_S12",
        ("SR1", "24"): "SRA1_S22",
    }.items():
        need(schedule.get(terminal) == net, f"P1.21 source drift: {terminal}")

    csv_names = (
        "source-register.csv", "submission-route-register.csv", "manufacturer-question-register.csv",
        "response-acceptance-register.csv", "authorization-prerequisites.csv", "signal-capture-register.csv",
        "test-case-register.csv", "open-holds.csv", "manufacturer-response-template.csv", "test-result-template.csv",
    )
    for directory in DIRECTORIES:
        for name in csv_names:
            data = rows(directory / name)
            need(data and all(row["warning"] == WARNING for row in data), f"{directory}: warning missing from {name}")
        questions = rows(directory / "manufacturer-question-register.csv")
        need(len(questions) == 13 and {r["addressee"] for r in questions} == {"Pilz", "Phoenix Contact"}, f"{directory}: question set")
        need(all(r["sent"] == "NOT SENT" and r["response_state"] == "OPEN" for r in questions), f"{directory}: RFI represented as sent/answered")
        routes = rows(directory / "submission-route-register.csv")
        need(len(routes) == 6 and all(r["state"] in {"NOT SENT", "NOT USED"} for r in routes), f"{directory}: route state")
        need(len(rows(directory / "response-acceptance-register.csv")) == 12, f"{directory}: response control count")
        need(len(rows(directory / "authorization-prerequisites.csv")) == 10, f"{directory}: authorization prerequisite count")
        need(len(rows(directory / "signal-capture-register.csv")) == 15, f"{directory}: signal count")
        tests = rows(directory / "test-case-register.csv")
        need(len(tests) == 18 and all(r["execution_state"] == "NOT EXECUTED" for r in tests), f"{directory}: test state")
        need(len(rows(directory / "open-holds.csv")) == 14 and all(r["state"] == "OPEN" for r in rows(directory / "open-holds.csv")), f"{directory}: hold state")
        result_template = rows(directory / "test-result-template.csv")
        need(all(r["result"] == "NOT EXECUTED" and r["selected_limit"] == "SELECTION REQUIRED" for r in result_template), f"{directory}: result template is not fail-closed")
        response_template = rows(directory / "manufacturer-response-template.csv")
        need(all(r["disposition"] == "OPEN" and r["qualified_review"] == "NOT REVIEWED" and not r["ticket_or_message_id"] for r in response_template), f"{directory}: response template is not blank/open")
        state = json.loads((directory / "package-status.json").read_text(encoding="utf-8"))
        need(state["identifier"] == "HR-V0-P121-APP-EVID-P0.1" and state["round"] == "R235", f"{directory}: identity")
        need(state["messages_sent"] == state["manufacturer_responses"] == state["tests_executed"] == state["tests_passed"] == 0, f"{directory}: activity falsely claimed")
        need(not state["p121_accepted"] and state["watchdog_safety_credit"] == "NONE", f"{directory}: configuration/safety boundary")
        need(not state["powered_test_authority"] and not state["energization_authority"], f"{directory}: authority boundary")
        procedure = (directory / "test-procedure.md").read_text(encoding="utf-8")
        need(WARNING in procedure and "NOT EXECUTED - NOT AUTHORIZED" in procedure and "actuator source" in procedure, f"{directory}: procedure boundary")

    page = (RELEASE / "index.html").read_text(encoding="utf-8")
    need(WARNING in page and "P1.15 remains current" in page and "font:clamp(16px" in page, "interactive guide boundary/legibility")
    need("data-group=\"maker\"" in page and "data-group=\"mode\"" in page, "interactive filters missing")
    manifest = {r["file"]: r for r in rows(RELEASE / "file-manifest.csv")}
    actual = {p.name: p for p in RELEASE.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "release manifest membership")
    for name, path in actual.items():
        data = path.read_bytes()
        need(manifest[name]["size_bytes"] == str(len(data)), f"{name}: size")
        need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest(), f"{name}: hash")
    print("HR-V0 P1.21 application-evidence check passed: 13 unsent questions, 18 unexecuted tests, 14 open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
