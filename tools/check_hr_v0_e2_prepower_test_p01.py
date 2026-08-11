#!/usr/bin/env python3
"""Validate the R228 E2 pre-power test candidate fail closed."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "tests/e2/hr-v0-e2-prepower-test-p0.1"
OUT = ROOT / "release/hr-v0/e2-prepower-test-p0.1"
P2P = ROOT / "release/hr-v0/panel-point-to-point-p0.1/point-to-point-wire-schedule.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    try:
        names = ["wire-continuity-plan.csv", "isolation-plan.csv", "no-backfeed-plan.csv", "absence-of-voltage-plan.csv", "instrument-register.csv", "prohibition-register.csv", "open-holds.csv", "source-register.csv", "authority-boundary.csv"]
        for name in names:
            need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
        wire, source = rows(ENG / "wire-continuity-plan.csv"), rows(P2P)
        isolation, backfeed = rows(ENG / "isolation-plan.csv"), rows(ENG / "no-backfeed-plan.csv")
        voltage, instruments = rows(ENG / "absence-of-voltage-plan.csv"), rows(ENG / "instrument-register.csv")
        prohibitions, holds = rows(ENG / "prohibition-register.csv"), rows(ENG / "open-holds.csv")
        need(len(wire) == len(source) == 55, "expected 55 wire rows")
        for test, original in zip(wire, source):
            need(test["wire_id"] == original["wire_id"] and test["net"] == original["net"], f"wire identity mismatch: {original['wire_id']}")
            need(test["from_endpoint"] == f"{original['from_reference']}:{original['from_terminal']}" and test["to_endpoint"] == f"{original['to_reference']}:{original['to_terminal']}", f"endpoint mismatch: {original['wire_id']}")
        need(sum(r["candidate_class"] == "FIXED_INTERNAL_METHOD_CANDIDATE" for r in wire) == 45, "expected 45 fixed rows")
        need(sum(r["candidate_class"] == "DOOR_CONDUCTOR_BLOCKED" for r in wire) == 10, "expected 10 blocked door rows")
        need(len(isolation) == 16 and len(backfeed) == 8 and len(voltage) == 12, "matrix counts changed")
        need(len(instruments) == 5 and instruments[0]["candidate"] == "Keysight U1282A" and instruments[0]["accepted"] == "FALSE", "instrument candidate boundary changed")
        need(len(prohibitions) == 6 and all(r["state"] == "PROHIBITED" for r in prohibitions), "prohibitions weakened")
        need(len(holds) == 10 and all(r["state"] == "OPEN" and r["accepted"] == "FALSE" for r in holds), "holds must remain open")
        for group in (wire, isolation, backfeed, voltage, instruments, prohibitions, holds, rows(ENG / "source-register.csv"), rows(ENG / "authority-boundary.csv")):
            need(all(r["warning"] == WARNING for r in group), "warning missing")
        need(all(r["execution_state"] == "NOT_EXECUTED" and r["measured_value"] == "BLANK" and r["accepted"] == "FALSE" for group in (wire, isolation, backfeed, voltage) for r in group), "physical result leaked")
        need(all("SELECTION REQUIRED" in r["numeric_limit"] for r in wire), "wire limits must remain unresolved")
        need(all(r["method"].startswith("PROHIBITED") for r in backfeed), "backfeed injection authority leaked")
        authority = rows(ENG / "authority-boundary.csv")
        need(all(r["permitted"] == "FALSE" for r in authority if r["activity"] != "read-only engineering/configuration review"), "work authority leaked")
        status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
        need(status["identifier"] == "HR-V0-E2-PREPOWER-P0.1" and status["round"] == "R228", "status identity changed")
        need(status["numeric_limits_released"] == 0 and status["executed_results"] == 0 and status["p118_accepted"] is False, "fail-closed state changed")
        for key in ("physical_tests_executed", "qualified_review_received", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
            need(status[key] is False, f"{key} must remain false")
        for directory in (ENG, OUT):
            for row in rows(directory / "file-manifest.csv"):
                path = directory / row["path"]
                need(path.is_file() and str(path.stat().st_size) == row["bytes"] and digest(path) == row["sha256"], f"manifest mismatch: {path}")
        gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
        for gate in ("EG-004", "EG-019", "EG-020", "EG-022"):
            need(gates[gate]["status"] == "partial" and "docs/hr-v0-e2-prepower-test-p0.1.md" in gates[gate]["evidence_location"], f"{gate} sync/state wrong")
        release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        need("HR-V0-E2-PREPOWER-P0.1" in json.dumps(release), "release candidate lacks R228")
        page = (OUT / "index.html").read_text(encoding="utf-8")
        for token in (WARNING, "all 55 rows", "45 fixed-internal", "10 blocked door", "16 isolation pairs"):
            need(token in page, f"web guide missing {token}")
        print("HR-V0-E2-PREPOWER-P0.1: PASS")
        return 0
    except Exception as exc:
        print(f"HR-V0-E2-PREPOWER-P0.1: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
