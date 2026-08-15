#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-STALE-AUTH-P0.1 / R196."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def need(value: bool, message: str) -> None:
        if not value:
            failures.append(message)

    form = rows(ROOT / "tests/forms/hr-v0-e2-software-authority-template-p0.1.csv")
    model = (ROOT / "firmware/supervisor/project_button_supervisor/model.py").read_text(encoding="utf-8")
    tests = (ROOT / "firmware/supervisor/tests/test_supervisor.py").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-stale-command-authority-p0.1.md").read_text(encoding="utf-8")
    page = (ROOT / "release/hr-v0/stale-command-authority-p0.1/index.html").read_text(encoding="utf-8")

    need(len(form) == 20, "software-authority form must bind all 20 E2-SL cases")
    need([row["case_id"] for row in form] == [f"E2-SL-{index:03d}" for index in range(1, 21)], "E2-SL IDs are incomplete or out of order")
    need(all(row["status"] == "NOT EXECUTED" and row["warning"] == WARNING for row in form), "form execution/release boundary changed")
    stale = next((row for row in form if row["case_id"] == "E2-SL-019"), {})
    need(stale.get("hardware_power_path_expected") == "ON", "E2-SL-019 must distinguish contactor power from motion authority")
    need(stale.get("expected_supervisor_state") == "ARMED", "E2-SL-019 supervisor state changed")
    need(stale.get("expected_active_trajectory") == "NONE", "E2-SL-019 stale target is not explicitly cleared")
    need(stale.get("expected_torque_enable_request") == "FALSE", "E2-SL-019 torque request is not explicitly false")
    need(stale.get("stale_replay_expected") == "REJECTED", "E2-SL-019 stale replay is not explicitly rejected")

    for token in ("self._invalidate_target()", "command.sequence <= self.last_sequence", "OperatingState.DRIVE_ENABLED"):
        need(token in model, f"supervisor authority token missing: {token}")
    for token in ("test_dropout_rearm_rejects_stale_replay_and_requires_new_sequence", "duplicate or out-of-order sequence", "command(sequence=2"):
        need(token in tests, f"R196 regression token missing: {token}")

    combined = doc + page
    for token in ("HR-V0-STALE-AUTH-P0.1", "R196", "ARMED", "NONE", "FALSE", "REJECTED", "zero safety credit", WARNING):
        need(token in combined, f"controlled R196 token missing: {token}")
    need("font:16px" in page and "font-size:14px" in page, "interactive guide text floors missing")
    need(not re.search(r"(?:font-size|font):\s*(?:1[0-3]|[0-9])px", page), "undersized CSS text declaration found")

    if failures:
        raise SystemExit("HR-V0 stale-command authority check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 stale-command authority check passed: 20/20 E2 cases bound; E2-SL-019 target NONE, torque FALSE, replay REJECTED")
    print("Physical E2/HIL evidence and qualified review remain open; no requirement or energization gate closes")
    print(WARNING)


if __name__ == "__main__":
    main()
