#!/usr/bin/env python3
"""Check the R183 Q4X E2 witness interface candidate package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-equipment/hr-v0/q4x-interface-p0.1"
WEB = ROOT / "release/hr-v0/q4x-interface-p0.1/index.html"
WARNING = "PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    equipment = rows(OUT / "equipment-register.csv")
    pins = rows(OUT / "pin-connection-schedule.csv")
    domains = rows(OUT / "domain-separation-register.csv")
    configs = rows(OUT / "configuration-candidate-register.csv")
    campaign = rows(OUT / "calibration-campaign.csv")
    sources = rows(OUT / "source-register.csv")
    holds = rows(OUT / "closure-holds.csv")
    receiving = rows(ROOT / "tests/forms/hr-v0-q4x-receiving-template-p0.1.csv")
    calibration = rows(ROOT / "tests/forms/hr-v0-q4x-static-calibration-template-p0.1.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")

    assert len(equipment) == 7
    exact = {row["item_id"]: row for row in equipment}
    assert exact["Q4X1"]["exact_model_or_part"] == "Q4XFULAF110-Q8 / 97540"
    assert exact["CBL-Q4X1"]["exact_model_or_part"] == "BC-M12F5-22-2-SF / 815158"
    assert exact["BR-Q4X1"]["exact_model_or_part"] == "SMBQ4XFA / 91512"
    assert exact["PS-Q4X1"]["exact_model_or_part"] == "2220-30-1, channel 1 only"
    assert exact["PROT-Q4X1"]["exact_model_or_part"] == "SELECTION REQUIRED"
    assert exact["TGT-Q4X1"]["exact_model_or_part"] == "SELECTION REQUIRED"
    assert all(row["safety_credit"] == "ZERO" for row in equipment)

    assert len(pins) == 8 and all(row["released"] == "NO" for row in pins)
    pin_text = " ".join(row["source"] + " " + row["destination"] for row in pins)
    for expected in ("pin 1", "pin 2", "pin 3", "pin 4", "pin 5", "shield/drain"):
        assert expected in pin_text
    assert "NO EXTERNAL DRIVE" in pin_text and "NO CONNECTION" in pin_text

    assert len(domains) == 6 and all(row["state"] == "HOLD" for row in domains)
    domain_text = " ".join(row["from_domain"] + " " + row["to_domain"] + " " + row["required_state"] for row in domains)
    for prohibited in ("SAFETY_24V", "protective earth", "contactor", "actuator source"):
        assert prohibited in domain_text

    assert len(configs) == 10
    cfg = {row["parameter_id"]: row for row in configs}
    assert cfg["CFG-QX-001"]["candidate"] == "24.0 Vdc"
    assert cfg["CFG-QX-002"]["candidate"] == "SELECTION REQUIRED"
    assert cfg["CFG-QX-009"]["candidate"] == "SELECTION REQUIRED"
    assert cfg["CFG-QX-009"]["release_state"] == "CATALOG VALUE PROHIBITED"

    assert len(campaign) == 10 and all(row["execution_state"] == "NOT EXECUTED" for row in campaign)
    assert any("10 minute" in row["action"] for row in campaign)
    assert len(sources) == 7 and all(row["verification_date"] == "2026-08-10" for row in sources)
    assert any("185624 Rev J" in row["revision_date"] for row in sources)
    assert any("2220S-905-01 Rev B" in row["revision_date"] for row in sources)

    assert len(holds) == 14 and all(row["state"] == "SELECTION REQUIRED" for row in holds)
    assert all(row["work_authority"] == "NONE" and row["warning"] == WARNING for row in holds)
    assert len(receiving) == 20 and all(row["result"] == "NOT EXECUTED" and row["disposition"] == "HOLD" for row in receiving)
    assert len(calibration) == 12 and all(row["result"] == "NOT EXECUTED" for row in calibration)

    assert status["identifier"] == "HR-V0-Q4X-IF-P0.1" and status["round"] == "R183"
    assert status["exact_candidate_count"] == 5 and status["selection_required_item_count"] == 2
    assert status["pin_schedule_row_count"] == 8 and status["domain_boundary_count"] == 6
    assert status["physical_run_count"] == 0 and status["released_connection_count"] == 0
    assert status["released_protection_count"] == 0 and status["robot_baseline_change_count"] == 0
    assert status["safety_function_credit"] == "ZERO"
    assert status["gate_effect"] == {"EG-025":"OPEN", "EG-026":"PARTIAL"}

    assert "font:16px/1.55" in html and "font-size:14px" in html
    assert "font-size:13px" not in html and "font-size:12px" not in html
    assert "overflow-x:auto" in html and "@media(max-width:720px)" in html
    assert html.count("class='card'") == 7 and html.count("class='hold'") == 14
    assert WARNING in html and "Nothing is released to connect" in html
    assert "zero physical runs" in html.lower() and "zero safety-function credit" in html.lower()

    print("PASS: R183 Q4X interface candidate")
    print("5 exact candidates; 8 pin rows; 6 boundaries; 14 holds; 0 released connections; 0 physical runs")
    print(WARNING)


if __name__ == "__main__":
    main()
