#!/usr/bin/env python3
"""Validate the R227 E2 grounding/bonding boundary package fail closed."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/grounding/hr-v0-e2-grounding-boundary-p0.1"
OUT = ROOT / "release/hr-v0/e2-grounding-boundary-p0.1"
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
        names = ["node-parity-register.csv", "endpoint-parity-register.csv", "boundary-register.csv", "inspection-register.csv", "open-holds.csv", "source-register.csv", "authority-boundary.csv"]
        for name in names:
            need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
        nodes = rows(ENG / "node-parity-register.csv")
        endpoints = rows(ENG / "endpoint-parity-register.csv")
        boundary = rows(ENG / "boundary-register.csv")
        inspections = rows(ENG / "inspection-register.csv")
        holds = rows(ENG / "open-holds.csv")
        sources = rows(ENG / "source-register.csv")
        authority = rows(ENG / "authority-boundary.csv")
        need(len(nodes) == 5, "expected five grounding nodes")
        counts = {r["net"]: (r["p115_connections"], r["p118_connections"]) for r in nodes}
        need(counts == {"ACT_0V_PE_BONDED": ("24", "24"), "SAFETY_0V": ("41", "49"), "COMPUTE_0V": ("5", "5"), "ROBOT_FRAME": ("1", "1"), "CABLE_SHIELD_TERM": ("1", "1")}, "node counts changed")
        need(len(endpoints) == 26 and all(r["comparison"] == "IDENTICAL" for r in endpoints), "expected 26 identical endpoint rows")
        need(len(boundary) == 10, "expected ten boundary items")
        need(len(inspections) == 15 and all(r["state"] == "UNEXECUTED" and r["result"] == "BLANK" for r in inspections), "inspection evidence must remain blank")
        need(len(holds) == 12 and all(r["state"] == "OPEN" and r["accepted"] == "FALSE" for r in holds), "holds must remain open")
        need(len(sources) == 18, "expected 18 source rows")
        need(all(r["warning"] == WARNING for group in (nodes, endpoints, boundary, inspections, holds, sources, authority) for r in group), "warning missing")
        need(any(r["reference"] == "SP1" and r["net"].startswith("INTENTIONALLY_NOT_CONNECTED") for r in endpoints), "SP1 DNP nets missing")
        need(any(r["reference"] == "JFRAME1" and r["net"] == "ROBOT_FRAME" for r in endpoints), "frame placeholder missing")
        need(any(r["reference"] == "JFRAME1" and r["net"] == "CABLE_SHIELD_TERM" for r in endpoints), "shield placeholder missing")
        need(any(r["reference"] == "PSA1" and r["net"] == "ACT_0V_PE_BONDED" for r in endpoints), "Mean Well PE-bonded return missing")
        need(all(r["permitted"] == "FALSE" for r in authority if r["activity"] != "read-only engineering/configuration review"), "work authority leaked")
        status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
        need(status["identifier"] == "HR-V0-E2-GND-BOUNDARY-P0.1" and status["round"] == "R227", "status identity changed")
        for key in ("p118_accepted", "physical_tests_executed", "qualified_review_received", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
            need(status[key] is False, f"{key} must remain false")
        for directory in (ENG, OUT):
            manifest = rows(directory / "file-manifest.csv")
            for row in manifest:
                path = directory / row["path"]
                need(path.is_file() and str(path.stat().st_size) == row["bytes"] and digest(path) == row["sha256"], f"manifest mismatch: {path}")
        gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
        for gate in ("EG-001", "EG-004", "EG-016", "EG-022"):
            need(gates[gate]["status"] == "partial", f"{gate} must remain partial")
            need("docs/hr-v0-e2-grounding-boundary-p0.1.md" in gates[gate]["evidence_location"], f"{gate} lacks R227 evidence")
        release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        need("HR-V0-E2-GND-BOUNDARY-P0.1" in json.dumps(release), "release candidate lacks R227 identifier")
        text = (OUT / "index.html").read_text(encoding="utf-8")
        need("Only the control and compute ELV domains may enter E2" in text and WARNING in text, "web guide content missing")
        need("energization_authorized\": true" not in json.dumps(status).lower(), "energization authority leaked")
        print("HR-V0-E2-GND-BOUNDARY-P0.1: PASS")
        return 0
    except Exception as exc:
        print(f"HR-V0-E2-GND-BOUNDARY-P0.1: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
