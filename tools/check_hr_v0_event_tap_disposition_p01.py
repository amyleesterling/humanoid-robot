#!/usr/bin/env python3
"""Check the R178 field-node observation disposition package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical/analysis/hr-v0-event-tap-disposition-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-event-tap-disposition-p0.1"
WEB = ROOT / "release/hr-v0/event-tap-disposition-p0.1/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected = {"node-disposition.csv", "source-register.csv", "selection-holds.csv", "calculation-screen.csv", "package-status.json"}
    need(errors, PKG.is_dir() and {p.name for p in PKG.iterdir()} == expected, "package membership changed")
    nodes = rows(PKG / "node-disposition.csv")
    need(errors, len(nodes) == 7, "expected seven nodes")
    need(errors, {r["net"] for r in nodes} == {"SR1_S12", "SR1_START_RETURN", "ARM_AFTER_S2", "K1_A1", "K2_A1", "EDM_K1_OUT", "SRA1_START_RETURN"}, "exact node set changed")
    need(errors, all("NOT RELEASED" in r["disposition"] or r["disposition"] == "DIVIDER DESIGN HELD" for r in nodes), "a field tap gained release")
    need(errors, all(r["warning"] == WARNING for r in nodes), "warning changed")
    sources = rows(PKG / "source-register.csv")
    need(errors, len(sources) == 5 and {r["manufacturer"] for r in sources} == {"Pilz", "Schneider Electric", "Texas Instruments"}, "primary-source set changed")
    holds = rows(PKG / "selection-holds.csv")
    need(errors, len(holds) == 10, "ten closure holds required")
    calc = rows(PKG / "calculation-screen.csv")
    need(errors, len(calc) == 6 and sum(r["result"] == "SELECTION REQUIRED" for r in calc) == 4, "calculation holds changed")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    for key in ("permanent_passive_tap_released_count", "divider_design_released_count", "authorized_connection_count", "executed_physical_test_count"):
        need(errors, status.get(key) == 0, f"{key} is not zero")
    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(errors, len(sheets) == 4, "expected root plus three native sheets")
    erc = (ECAD / "validation/hr-v0-event-tap-disposition-p0.1-erc.rpt").read_text(encoding="utf-8")
    need(errors, "0  Errors 0  Warnings" in erc, "native ERC is not 0/0")
    need(errors, len(list((ECAD / "output").glob("tap-disposition-*.svg"))) == 3, "expected three child SVG exports")
    schedule = rows(ECAD / "connector-schedule.csv")
    held_refs = {r["reference"] for r in schedule if r["reference"].startswith("HOLD") and ("NOT RELEASED" in r["state"] or r["state"] == "DIVIDER DESIGN HELD")}
    need(errors, held_refs == {f"HOLD{i}" for i in range(1, 8)}, "seven one-sided no-connect boundaries required")
    html = WEB.read_text(encoding="utf-8")
    for token in ("Seven nodes. Zero released taps.", "font:16px", "font-size:14px", "data-filter=\"pilz\"", "NO FIELD TAP", "zero released taps"):
        need(errors, token.lower() in html.lower(), f"web guide missing {token!r}")
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    instrumentation = next((item for item in release["current_products"] if item.get("identifier") == "HR-V0-DYN-INST-P0.1"), {})
    event_ain = next((item for item in release["current_products"] if item.get("identifier") == "HR-V0-DYN-EVENT-AIN-P0.1"), {})
    need(errors, "HR-V0-EVENT-TAP-DISP-P0.1" in instrumentation.get("supporting_identifiers", []), "instrumentation product lacks R178")
    need(errors, "HR-V0-EVENT-TAP-DISP-P0.1" in event_ain.get("supporting_identifiers", []), "event AIN product lacks R178")
    need(errors, "all_field_connections_prohibited" in event_ain.get("release_state", "") and "zero_safety_credit" in event_ain.get("release_state", ""), "event AIN release state gained authority")
    gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    need(errors, gates["EG-025"]["status"] == "open" and "hr-v0-gate-evidence-supplement-r178.csv" in gates["EG-025"]["evidence_location"], "EG-025 state/evidence changed")
    need(errors, gates["EG-026"]["status"] == "partial" and "hr-v0-gate-evidence-supplement-r178.csv" in gates["EG-026"]["evidence_location"], "EG-026 state/evidence changed")
    for path in (ROOT / "docs/hr-v0-event-tap-disposition-p0.1.md", ROOT / "docs/reviews/2026-08-10-r178-independent-review-request.md", ROOT / "docs/reviews/2026-08-10-r178-validation-record.md", ROOT / "docs/reviews/2026-08-10-sol-r12-post-r178-status.md", ROOT / "requirements/hr-v0-gate-evidence-supplement-r178.csv"):
        need(errors, path.is_file(), f"missing synchronized artifact: {path.name}")
    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))
    print("HR-V0 event-tap disposition P0.1 check passed: 7 exact nodes, 10 holds, native ERC 0/0")
    print("0 released taps, 0 released divider designs, 0 authorized connections, 0 physical tests, zero safety credit")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
