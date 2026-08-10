#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-BUILD-TRAVELER-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

from generate_hr_v0_build_traveler import PHASES, SOURCES, STEP_GROUPS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assembly/hr-v0-build-traveler-p0.1"
WEB = ROOT / "release/hr-v0/build-traveler-p0.1/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    try:
        phases = rows(OUT / "build-phases.csv")
        steps = rows(OUT / "build-steps.csv")
        gates = rows(OUT / "gate-phase-matrix.csv")
        holds = rows(OUT / "hold-points.csv")
        sources = rows(OUT / "source-register.csv")
        summary = json.loads((OUT / "build-traveler-summary.json").read_text(encoding="utf-8"))
        page = WEB.read_text(encoding="utf-8")

        if summary["identifier"] != "HR-V0-BUILD-TRAVELER-P0.1":
            fail("identifier changed")
        if (len(phases), len(steps), len(gates), len(holds)) != (14, 85, 21, 14):
            fail("traveler coverage counts changed")
        if (summary["phase_count"], summary["step_count"], summary["through_e2_gate_count"]) != (14, 85, 21):
            fail("summary counts changed")
        if summary["open_phase_count"] != 13 or summary["prohibited_phase_count"] != 1:
            fail("phase state counts changed")
        if any(summary[key] != 0 for key in ("authorized_step_count", "executed_step_count", "closed_hold_count")):
            fail("traveler implies authorization, execution or hold closure")
        if any(summary[key] for key in ("fabrication_authorized", "connection_authorized", "energization_authorized")):
            fail("traveler implies work authority")

        expected_phase_ids = [item[0] for item in PHASES]
        if [row["phase_id"] for row in phases] != expected_phase_ids:
            fail("phase order changed")
        known: set[str] = set()
        for row in phases:
            dependencies = [] if row["depends_on"] == "NONE" else row["depends_on"].split(",")
            if any(dependency not in known for dependency in dependencies):
                fail(f"forward or unknown phase dependency: {row['phase_id']}")
            known.add(row["phase_id"])
            if row["named_authorizer"] != "SELECTION REQUIRED" or row["decision"] != "NOT APPROVED" or row["warning"] != WARNING:
                fail(f"phase authority invented: {row['phase_id']}")
        if phases[-1]["phase_id"] != "BT-P13" or phases[-1]["status"] != "PROHIBITED" or phases[-1]["energy_boundary"] != "PROHIBITED":
            fail("powered-work boundary changed")
        if any(row["status"] != "OPEN" for row in phases[:-1]):
            fail("an unpowered phase became closed")

        expected_step_ids = []
        for phase_id in expected_phase_ids:
            expected_step_ids.extend(f"{phase_id}-S{index:02d}" for index in range(1, len(STEP_GROUPS[phase_id]) + 1))
        if [row["step_id"] for row in steps] != expected_step_ids or len(set(expected_step_ids)) != 85:
            fail("step order or uniqueness changed")
        for row in steps:
            if row["named_executor"] != "SELECTION REQUIRED" or row["named_reviewer"] != "SELECTION REQUIRED":
                fail(f"step invents people: {row['step_id']}")
            if row["authorization_state"] != "NOT AUTHORIZED" or row["result"] != "NOT EXECUTED" or row["evidence_uri"] != "NOT EXECUTED":
                fail(f"step implies execution: {row['step_id']}")
            if row["stop_work_on_failure"] != "YES" or row["energization_effect"] != "NONE" or row["warning"] != WARNING:
                fail(f"step fail-closed boundary changed: {row['step_id']}")

        gate_ids = [row["gate_id"] for row in gates]
        if gate_ids != [f"EG-{index:03d}" for index in range(1, 9)] + [f"EG-{index:03d}" for index in range(10, 23)]:
            fail("through-E2 gate set changed")
        if any(row["current_status"] != "partial" or row["traveler_effect"] != "BLOCKS ENTRY OR RELEASE - DOES NOT CLOSE GATE" for row in gates):
            fail("traveler implies gate closure")
        if any(row["state"] != "OPEN" for row in holds[:-1]) or holds[-1]["state"] != "PROHIBITED":
            fail("hold state changed")
        if any(row["named_releaser"] != "SELECTION REQUIRED" or row["warning"] != WARNING for row in holds):
            fail("hold invents release authority")

        if {row["source_id"] for row in sources} != set(SOURCES):
            fail("source set changed")
        for row in sources:
            path = SOURCES[row["source_id"]]
            if row["path"] != str(path.relative_to(ROOT)).replace("\\", "/"):
                fail(f"source path changed: {row['source_id']}")
            if row["source_id"] == "release_manifest":
                if row["sha256"] != "SELF-REFERENTIAL-MANIFEST-HASH-OMITTED":
                    fail("release-manifest self-reference marker changed")
                if row["state"] != "CONTROLLED INPUT; HASH OMITTED TO AVOID MANIFEST CYCLE":
                    fail("release-manifest self-reference state changed")
            elif row["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                fail(f"source hash mismatch: {row['source_id']}")

        for token in (WARNING, "HR-V0-BUILD-TRAVELER-P0.1", "R144", "font:16px", "14", "85", "21", "0", "BT-P13", "PROHIBITED", "overflow:auto"):
            if token not in page:
                fail(f"interactive traveler missing {token}")

        candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        product = next((item for item in candidate["current_products"] if item["domain"] == "assembly"), None)
        if not product or product["identifier"] != "HR-V0-BUILD-TRAVELER-P0.1" or "not_approved" not in product["release_state"]:
            fail("release candidate does not bind fail-closed build traveler")

        print("HR-V0-BUILD-TRAVELER-P0.1 PASS")
        print("  14 phases / 85 steps / 21 through-E2 gates / 14 holds")
        print("  0 authorized / 0 executed / BT-P13 prohibited")
        print("  integrated sequence only; no fabrication, connection, motion or energization authority")
        return 0
    except Exception as exc:
        print(f"HR-V0-BUILD-TRAVELER-P0.1 FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
