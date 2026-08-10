#!/usr/bin/env python3
"""Check the R180 event-observation independence correction package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/event-observation-correction-p0.1"
WEB = ROOT / "release/hr-v0/event-observation-correction-p0.1/index.html"
FORM = ROOT / "tests/forms/hr-v0-event-observation-correction-template.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    supersessions = read_csv("supersession-register.csv")
    instruments = read_csv("instrument-register.csv")
    channels = read_csv("channel-allocation.csv")
    cases = read_csv("test-case-allocation.csv")
    loads = read_csv("diagnostic-load-holds.csv")
    holds = read_csv("closure-holds.csv")
    sources = read_csv("source-register.csv")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")
    form_header = FORM.read_text(encoding="utf-8").splitlines()[0]

    all_rows = supersessions + instruments + channels + cases + loads + holds + sources
    assert all(row["warning"] == WARNING for row in all_rows)
    assert len(supersessions) == 4 and any(row["affected_record"] == "R174 DTA-003" for row in supersessions)
    assert len(instruments) == 5 and instruments[0]["identity"] == "MSO58B"
    assert instruments[1]["identity"] == "TCP0030A" and "QUANTITY 4" in instruments[1]["selection_state"]
    assert instruments[2]["identity"].startswith("TIVP02") and "QUANTITY 3" in instruments[2]["selection_state"]
    assert len(channels) == 16
    for run_type in {"STOP", "RESET_ARM"}:
        rows = [row for row in channels if row["run_type"] == run_type]
        assert len(rows) == 8 and {row["host_channel"] for row in rows} == {f"CH{i}" for i in range(1, 9)}
    stop = [row for row in channels if row["run_type"] == "STOP"]
    assert sum(row["purpose"] == "common series EDM-chain current" for row in stop) == 1
    assert {row["signal"] for row in stop if "individual" in row["purpose"]} == {"K1_STATUS", "K2_STATUS"}
    assert all("zero safety credit" in row["interpretation_limit"].lower() for row in stop if row["signal"] in {"K1_STATUS", "K2_STATUS"})
    assert len(cases) == 4 and all(row["state"] == "NOT EXECUTED" for row in cases)
    assert len(loads) == 8 and len(holds) == 12 and len(sources) == 7
    assert status["corrected_false_independence_count"] == 1
    assert status["simultaneous_host_channel_count"] == 8
    assert status["selected_host_order_configuration_count"] == 0
    assert status["released_diagnostic_load_count"] == 0
    assert status["released_connection_count"] == 0
    assert status["executed_physical_test_count"] == 0
    assert status["safety_function_credit"] == "ZERO"
    assert status["eg_025"] == "OPEN" and status["eg_026"] == "PARTIAL"
    assert "font:16px/1.55" in html and "font-size:14px" in html
    assert "font-size:13px" not in html and "font-size:12px" not in html
    assert html.count('class="card"') == 8
    assert "One EDM chain is not two contact states" in html
    assert "No diagnostic load" in html and "zero safety credit" in html.lower()
    assert "channel_id" in form_header and "trace_uri" in form_header and "reviewer" in form_header
    print("PASS: R180 event-observation independence correction")
    print("1 false-independence correction; 8 simultaneous channels; 0 released connections; 0 executed tests")
    print(WARNING)


if __name__ == "__main__":
    main()
