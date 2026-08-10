#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-BOSTON-SITE-P0.2 / R194."""
from __future__ import annotations
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "configuration" / "hr-v0-boston-site-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION POWERED TESTING MOTION OR ENERGIZATION"

def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def main() -> None:
    failures: list[str] = []
    def require(value: bool, message: str) -> None:
        if not value:
            failures.append(message)

    jurisdiction = rows("jurisdiction-register.csv")
    sources = rows("source-register.csv")
    sites = rows("site-selection-register.csv")
    premises = rows("premises-input-template.csv")
    holds = rows("hold-register.csv")
    gates = list(csv.DictReader((ROOT / "requirements/hr-v0-gate-evidence-supplement-r194.csv").open(encoding="utf-8-sig", newline="")))
    doc = (ROOT / "docs/hr-v0-boston-site-jurisdiction-p0.2.md").read_text(encoding="utf-8")
    page = (ROOT / "release/hr-v0/boston-site-p0.2/index.html").read_text(encoding="utf-8")

    require(len(jurisdiction) == 8, "jurisdiction register must contain 8 records")
    require(len(sources) == 8, "source register must contain 8 records")
    require(len(sites) == 6, "site-selection register must contain 6 records")
    require(len(premises) == 20, "premises template must contain 20 records")
    require(len(holds) == 8, "hold register must contain 8 records")
    require(all(row["warning"] == WARNING for row in jurisdiction + sources + sites + premises + holds), "controlled warning changed")
    require(all(row["current_state"] == "SELECTION REQUIRED" and not row["completed_value"] for row in premises), "a premises input was inferred or prefilled")
    require(all(row["state"] == "OPEN" for row in holds), "a site hold was falsely closed")
    require({row["gate_id"] for row in gates} == {"EG-001", "EG-022"}, "R194 gate set changed")
    require(all(row["state"] == "REMAINS PARTIAL" for row in gates), "R194 claims a gate closure")
    combined = doc + page
    for token in ("2026-04-24", "Boston Public Library", "Hatch Makerspace", "Kontrast4D", "20 site inputs", "0 gates closed", "R194"):
        require(token.lower() in combined.lower(), f"missing controlled token {token}")
    require("font:16px" in page and "font-size:14px" in page, "interactive guide text floors missing")
    require("data-filter=\"test\"" in page and "data-filter=\"prototype\"" in page and "data-filter=\"cnc\"" in page, "interactive role filters missing")
    require(not re.search(r"(?:font-size|font):\s*1[123]px", page), "undersized CSS text declaration found")

    if failures:
        raise SystemExit("HR-V0 Boston site P0.2 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 Boston site P0.2 check passed: 8 jurisdiction facts, 8 sources, 6 site roles, 20 blank premises inputs and 8 open holds")
    print("EG-001 and EG-022 remain partial; no provider or premises is selected and no connection, powered test, motion or energization is authorized")
    print(WARNING)

if __name__ == "__main__":
    main()
