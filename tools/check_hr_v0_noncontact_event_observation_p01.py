#!/usr/bin/env python3
"""Check the R179 non-contact event-observation correction package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical/analysis/hr-v0-noncontact-event-observation-p0.1"
WEB = ROOT / "release/hr-v0/noncontact-event-observation-p0.1/index.html"
FORM = ROOT / "tests/forms/hr-v0-noncontact-event-observation-template.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    conductors = read_csv("conductor-observation-map.csv")
    instruments = read_csv("instrument-register.csv")
    sources = read_csv("source-register.csv")
    holds = read_csv("closure-holds.csv")
    steps = read_csv("e2-comparison-sequence.csv")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")
    form_header = FORM.read_text(encoding="utf-8").splitlines()[0]

    assert len(conductors) == 7
    assert {row["net"] for row in conductors} == {"SR1_S12", "SR1_START_RETURN", "ARM_AFTER_S2", "K1_A1", "K2_A1", "EDM_K1_OUT", "SRA1_START_RETURN"}
    assert {row["wire_number"] for row in conductors} == {"W2008", "W2011", "W3021", "W4001", "W4007", "W4005", "W3007"}
    assert all(row["warning"] == WARNING for row in conductors + instruments + sources + holds + steps)
    assert len(instruments) == 4 and instruments[0]["identity"] == "TCP0030A"
    assert instruments[1]["selection_state"] == "SELECTION REQUIRED"
    assert len(sources) == 5 and any(row["document"] == "51W-19042-12" for row in sources)
    assert len(holds) == 12 and len(steps) == 9
    assert all(row["state"] == "NOT EXECUTED" for row in steps)
    assert status["electrical_field_tap_count"] == 0
    assert status["permanent_adapter_released_count"] == 0
    assert status["executed_physical_test_count"] == 0
    assert status["safety_function_credit"] == "ZERO"
    assert status["eg_025"] == "OPEN" and status["eg_026"] == "PARTIAL"
    assert "font:16px/1.55" in html and "font-size:14px" in html
    assert "font-size:13px" not in html and "font-size:12px" not in html
    assert html.count('class="card"') == 7
    assert "No electrical tap" in html and "zero safety credit" in html.lower()
    assert "current_trace_uri" in form_header and "motion_trace_uri" in form_header
    assert "result" in form_header and "reviewer" in form_header
    print("PASS: R179 non-contact event-observation package")
    print("7 conductor locations; 0 electrical taps; 12 open holds; 0 executed physical tests")
    print(WARNING)


if __name__ == "__main__":
    main()
