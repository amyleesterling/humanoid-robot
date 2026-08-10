#!/usr/bin/env python3
"""Check the R184 Q4X temporary interface-box candidate."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/q4x-box-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-q4x-box-p0.1"
WEB = ROOT / "release/hr-v0/q4x-box-p0.1/index.html"
DOC = ROOT / "docs/hr-v0-q4x-box-p0.1.md"
WARNING = "PRELIMINARY - BENCH R&D CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks: list[tuple[bool, str]] = []
    need = lambda cond, label: checks.append((bool(cond), label))
    bom = rows(PKG / "candidate-bom.csv")
    sources = rows(PKG / "source-register.csv")
    holds = rows(PKG / "closure-holds.csv")
    connections = rows(PKG / "connection-and-termination-schedule.csv")
    layout = rows(PKG / "enclosure-layout-candidate.csv")
    calcs = rows(PKG / "calculation-register.csv")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(len(bom) == 19, "19 candidate BOM rows")
    need(len(sources) == 14, "14 primary-source records")
    need(len(holds) == 14, "14 open holds")
    need(len(connections) == 11, "11 connection/termination rows")
    need(len(layout) == 7, "7 enclosure-layout rows")
    need(len(calcs) == 6, "6 controlled calculations")
    need(all(row["warning"] == WARNING for table in (bom, sources, holds, connections, layout, calcs) for row in table), "warning on all package CSV rows")
    need(status["released_connections"] == status["authorized_procurement"] == status["authorized_fabrication"] == status["authorized_powered_runs"] == status["executed_physical_runs"] == 0, "all authority/execution counts remain zero")
    need(status["safety_function_credit"] == "ZERO", "zero safety-function credit")
    need(status["gate_effect"] == {"EG-025": "OPEN", "EG-026": "PARTIAL"}, "no gate inflation")
    required_parts = {"1464484", "3209578", "3209510", "PJ1084T", "14F0907", "53111000", "53119000", "881802", "815158", "97540"}
    joined = " ".join(row["part_or_item"] for row in bom)
    need(all(part in joined for part in required_parts), "exact selected/evaluation part identities present")
    need("SELECTION REQUIRED" in joined, "unresolved physical test interface remains explicit")
    need(any("NO BOND" in row["candidate_state"] for row in connections), "shield no-bond state explicit")
    need(any("INTENTIONALLY UNWIRED" in row["candidate_state"] for row in connections), "PTCB remote contact DNP explicit")

    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(len(sheets) == 3, "root plus two native KiCad sheets")
    for name in ("hr-v0-q4x-box-p0.1.kicad_pro", "hr-v0-q4x-box-p0.1.kicad_sym", "connector-schedule.csv", "net-schedule.csv", "wire-number-table.csv", "bom.csv", "SOURCE-MANIFEST.csv"):
        need((ECAD / name).is_file(), f"ECAD artifact {name}")
    erc = (ECAD / "validation/hr-v0-q4x-box-p0.1-erc.rpt").read_text(encoding="utf-8", errors="replace")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "native KiCad ERC 0/0")
    need(len(list((ECAD / "output").glob("*.svg"))) == 3, "three native KiCad SVG exports")
    need(all((ECAD / "output" / name).is_file() for name in ("hr-v0-q4x-box-p0.1.svg", "01_source_and_protection.svg", "02_sensor_and_signal.svg")), "stable web-linked SVG export names")
    schedule = rows(ECAD / "connector-schedule.csv")
    need(any(row["reference"] == "PTCB1" and row["terminal"] == "IN+" for row in schedule), "PTCB IN+ modeled")
    need(any(row["reference"] == "Q4X1" and row["terminal"] == "5" and row["net"] == "Q4X_ANALOG_GND" for row in schedule), "Q4X pin 5 modeled separately")
    need(any(row["reference"] == "XQ1.6" and row["net"] == "Q4X_SHIELD_PARK" for row in schedule), "shield park terminal modeled")
    need(any(row["reference"] == "TEST1" and "SELECTION REQUIRED" in row["state"] for row in schedule), "unresolved test fixture modeled")

    html = WEB.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    need(WARNING.replace("&", "&amp;") in html and WARNING in doc, "warning in web and engineering note")
    need("font:16px" in html and "font-size:14px" in html, "legible web type floors")
    need("button[data-target]" in html and html.count("class='sheet") == 3, "interactive three-sheet viewer")
    need("not a guaranteed hard fault-current ceiling" in doc, "PTCB typical-limit caveat in engineering note")
    need("No fuse value is released" in doc, "no inferred fuse value")
    need("no Sol blocker closes" in doc, "Sol baseline not overstated")

    failed = [label for ok, label in checks if not ok]
    for ok, label in checks:
        print(("PASS " if ok else "FAIL ") + label)
    print(f"summary: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
