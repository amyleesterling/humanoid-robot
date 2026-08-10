#!/usr/bin/env python3
"""Check the R182 E2 acquisition-compatibility candidate package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-equipment/hr-v0/e2-acquisition-compatibility-p0.1"
WEB = ROOT / "release/hr-v0/e2-acquisition-compatibility-p0.1/index.html"
WARNING = "PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    channels = read_csv("channel-population.csv")
    budgets = read_csv("probe-power-budget.csv")
    motion = read_csv("motion-witness-register.csv")
    sources = read_csv("source-register.csv")
    holds = read_csv("closure-holds.csv")
    inquiries = read_csv("manufacturer-inquiry-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")

    assert len(channels) == 8 and [row["channel"] for row in channels] == [f"CH{i}" for i in range(1, 9)]
    assert sum(row["probe"] == "TCP0030A" for row in channels) == 4
    assert sum(row["probe"] == "TIVP02 + TIVPMX10X" for row in channels) == 4
    for bank in ("1-4", "5-8"):
        bank_rows = [row for row in channels if row["bank"] == bank]
        assert len(bank_rows) == 4
        assert abs(sum(float(row["max_probe_power_W"]) for row in bank_rows) - 35.8) < 1e-9
        assert sum(row["probe"] == "TCP0030A" for row in bank_rows) == 2
        assert sum(row["probe"] == "TIVP02 + TIVPMX10X" for row in bank_rows) == 2

    assert len(budgets) == 3
    assert all(float(row["calculated_max_W"]) < float(row["manufacturer_limit_W"]) for row in budgets)
    assert float(budgets[2]["calculated_max_W"]) == 71.6 and float(budgets[2]["margin_W"]) == 8.4
    assert len(motion) == 5 and motion[0]["item"] == "Banner Q4XFULAF110-Q8 / part 97540"
    assert "35-110 mm" in motion[0]["controlled_fact"] and "0-10 V" in motion[0]["controlled_fact"]
    assert "pin 4" in motion[1]["controlled_fact"] and "pin 5" in motion[1]["controlled_fact"]
    assert len(sources) == 6 and all(row["verification_date"] == "2026-08-10" for row in sources)
    assert len(holds) == 15 and all(row["state"] == "SELECTION REQUIRED" for row in holds)
    assert all(row["work_authority"] == "NONE" and row["warning"] == WARNING for row in holds)
    assert len(inquiries) == 2 and all(row["state"] == "NOT SENT" and row["authority"] == "NONE" for row in inquiries)

    assert status["channel_count"] == 8 and status["tcp0030a_count"] == 4 and status["tivp02_count"] == 4
    assert status["documented_max_probe_power_W"] == 71.6 and status["bank_max_probe_power_W"] == 35.8
    assert status["physical_compatibility_run_count"] == 0 and status["released_connection_count"] == 0
    assert status["safety_function_credit"] == "ZERO"
    assert status["gate_effect"] == {"EG-025":"OPEN", "EG-026":"PARTIAL"}

    assert "font:16px/1.55" in html and "font-size:14px" in html
    assert "font-size:13px" not in html and "font-size:12px" not in html
    assert html.count("class='card'") == 3 and html.count("class='hold'") == 15
    assert WARNING in html and "71.6 W" in html and "35.8 W" in html
    assert "Zero physical compatibility runs" in html and "zero safety-function credit" in html.lower()

    print("PASS: R182 E2 acquisition compatibility")
    print("8 channels; 4 TCP0030A; 4 TIVP02; 71.6 W total; 35.8 W per bank; 15 holds; 0 physical runs")
    print(WARNING)


if __name__ == "__main__":
    main()
