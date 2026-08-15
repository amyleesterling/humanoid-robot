#!/usr/bin/env python3
"""Validate the fail-closed R229 P1.18 disposition dossier."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/reviews/hr-v0-p118-disposition-p0.1"
OUT = ROOT / "release/hr-v0/p118-disposition-p0.1"
IDENTIFIER = "HR-V0-P118-DISPOSITION-P0.1"
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
        names = ["component-delta.csv", "connector-terminal-parity.csv", "added-terminal-register.csv", "net-delta.csv", "sheet-delta-register.csv", "schedule-parity-summary.csv", "logic-invariant-register.csv", "decision-matrix.csv", "open-holds.csv", "source-register.csv", "authority-boundary.csv"]
        for name in names:
            need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
        components, parity = rows(ENG / "component-delta.csv"), rows(ENG / "connector-terminal-parity.csv")
        added, nets = rows(ENG / "added-terminal-register.csv"), rows(ENG / "net-delta.csv")
        sheets, summary = rows(ENG / "sheet-delta-register.csv"), rows(ENG / "schedule-parity-summary.csv")
        logic, decisions, holds = rows(ENG / "logic-invariant-register.csv"), rows(ENG / "decision-matrix.csv"), rows(ENG / "open-holds.csv")
        need(len(components) == 5 and {r["reference"] for r in components} == {"XD24", "XD0", "XN1", "XN2", "XN3"}, "component delta changed")
        need(len(parity) == 308 and all(r["p118_match"] == "IDENTICAL" for r in parity), "terminal parity changed")
        need(len(added) == 32 and {r["reference"] for r in added} == {"XD24", "XD0", "XN1", "XN2", "XN3"}, "terminal additions changed")
        need(len(nets) == 106 and sum(r["delta_state"] == "IDENTICAL" for r in nets) == 101 and sum(r["delta_state"] != "IDENTICAL" for r in nets) == 5, "net delta count changed")
        need(all(r["removed_connections"] == "NONE" and r["original_membership_preserved"] == "TRUE" for r in nets), "net removal detected")
        need(len(sheets) == 13 and sum(r["delta_class"] == "ADMINISTRATIVE_ONLY_CANONICAL_IDENTICAL" and r["canonical_identical_after_admin_normalization"] == "TRUE" for r in sheets) == 9, "sheet delta boundary changed")
        need(len(summary) == 6 and all(r["removed_or_modified_rows"] == "0" for r in summary[:5]), "schedule parity changed")
        need(len(logic) == 8 and all(r["qualified_disposition"] == "OPEN" for r in logic), "logic boundary changed")
        need(len(decisions) == 8 and all(r["independent_reviewer_decision"] == "BLANK" for r in decisions), "reviewer decision invented")
        need(len(holds) == 7 and all(r["state"] == "OPEN" and r["accepted"] == "FALSE" for r in holds), "hold boundary changed")
        for group in (components, parity, added, nets, sheets, summary, logic, decisions, holds, rows(ENG / "source-register.csv"), rows(ENG / "authority-boundary.csv")):
            need(all(r["warning"] == WARNING for r in group), "warning missing")
        status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
        need(status["identifier"] == IDENTIFIER and status["round"] == "R229", "status identity changed")
        need(status["p118_accepted"] is False and status["project_owned_parity_result"] == "NO UNCONTROLLED CONNECTIVITY DELTA FOUND", "status boundary changed")
        for key in ("independent_review_received", "qualified_review_received", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
            need(status[key] is False, f"{key} must remain false")
        for directory in (ENG, OUT):
            for row in rows(directory / "file-manifest.csv"):
                path = directory / row["path"]
                need(path.is_file() and str(path.stat().st_size) == row["bytes"] and digest(path) == row["sha256"], f"manifest mismatch: {path}")
        gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
        for gate in ("EG-002", "EG-004", "EG-020"):
            need(gates[gate]["status"] == "partial" and "docs/hr-v0-p118-disposition-p0.1.md" in gates[gate]["evidence_location"], f"{gate} state/sync changed")
        release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        electrical = next(p for p in release["current_products"] if p.get("domain") == "electrical")
        need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 no longer current")
        need(electrical.get("p118_disposition_dossier") == IDENTIFIER and IDENTIFIER in electrical["supporting_identifiers"], "release candidate lacks R229")
        page = (OUT / "index.html").read_text(encoding="utf-8")
        for token in (WARNING, "all 106 nets", "101 identical", "5 node-only deltas", "P1.15 remains current"):
            need(token in page, f"guide missing {token}")
        print(f"{IDENTIFIER}: PASS")
        print("77 BOM and 308 terminal rows preserved; 5 nodes/32 terminals added; P1.18 remains unaccepted")
        return 0
    except Exception as exc:
        print(f"{IDENTIFIER}: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
