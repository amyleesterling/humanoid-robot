#!/usr/bin/env python3
"""Validate the fail-closed R230 P1.19 visual-correction dossier."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from generate_hr_v0_p119_visual_correction_p01 import IDENTIFIER, OUT, P119, ROOT, WARNING, parity


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    try:
        result = parity()
        need(result["component_count"] == 84, "component count changed")
        need(result["net_count"] == 106, "net count changed")
        need(result["csv_rows"] == {"bom.csv": 82, "connector-schedule.csv": 340, "net-schedule.csv": 106, "wire-number-table.csv": 301, "unresolved-selections.csv": 63}, "schedule row counts changed")

        sheets = sorted(P119.glob("*.kicad_sch"))
        need(len(sheets) == 13, "P1.19 must contain root plus twelve native child sheets")
        for sheet in sheets:
            text = sheet.read_text(encoding="utf-8-sig")
            need(WARNING in text, f"full warning missing: {sheet.name}")
            need('(rev "P1.19")' in text, f"bounded title revision missing: {sheet.name}")
            need('comment 1 "SEE FULL PRELIMINARY WARNING ABOVE"' in text, f"title warning pointer missing: {sheet.name}")
            need('comment 2 "UNACCEPTED LAYOUT CANDIDATE"' in text, f"candidate title state missing: {sheet.name}")
            if sheet.name[:2] in {"01", "02", "03", "07", "10"}:
                need('(paper "A2")' in text, f"dense sheet not A2: {sheet.name}")
            elif not sheet.name.startswith("project-button-"):
                need('(paper "A3")' in text, f"ordinary child sheet not A3: {sheet.name}")

        review = read_csv(OUT / "sheet-review.csv")
        need(len(review) == 13 and {row["page"] for row in review} == {str(i) for i in range(13)}, "sheet review coverage changed")
        need(all(row["project_visual_result"] == "PASS" for row in review), "project visual pass missing")
        need(all(row["independent_review"] == "OPEN" and row["qualified_electrical_review"] == "OPEN" for row in review), "external review state promoted")
        need(all(row["warning"] == WARNING for row in review), "sheet warning changed")

        status = json.loads((OUT / "parity-summary.json").read_text(encoding="utf-8"))
        need(status["identifier"] == IDENTIFIER and status["round"] == "R230", "status identity changed")
        need(status["netlist_semantic_parity"] is True and status["erc_errors"] == 0 and status["erc_warnings"] == 0, "parity/ERC result changed")
        need(status["p115_current"] is True and status["p118_accepted"] is False and status["p119_accepted"] is False, "configuration authority changed")
        for key in ("independent_review_complete", "qualified_electrical_review_complete", "functional_safety_approved", "fabrication_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
            need(status[key] is False, f"unauthorized state: {key}")

        holds = read_csv(OUT / "open-holds.csv")
        need(len(holds) == 7 and all(row["status"] == "OPEN" for row in holds), "seven open holds required")
        gates = read_csv(ROOT / "requirements/hr-v0-gate-evidence-supplement-r230.csv")
        need({row["gate_id"] for row in gates} == {"EG-002", "EG-004", "EG-020"}, "gate set changed")
        need(all(row["status"] == "partial" and row["authority_added"] == "NO" for row in gates), "gate authority changed")

        guide = (OUT / "index.html").read_text(encoding="utf-8")
        for token in (WARNING, "Baseline P1.18", "Corrected P1.19 candidate", "sheet-review.csv", "P1.19 remains unaccepted"):
            need(token in guide, f"guide token missing: {token}")
        need("font-size:12px" not in guide and "font-size:11px" not in guide, "undersized interface text introduced")
        for path in (ROOT / "docs/hr-v0-p119-visual-correction-p0.1.md", ROOT / "docs/reviews/2026-08-11-r230-independent-review-request.md"):
            need(path.is_file() and WARNING in path.read_text(encoding="utf-8"), f"controlled document missing/warning absent: {path}")
        release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
        electrical = next(item for item in release["current_products"] if item["domain"] == "electrical")
        need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 is no longer current")
        need(electrical.get("panel_visual_correction_candidate") == "V3-P1.19-VISUAL-CORRECTION-CANDIDATE", "P1.19 supporting candidate missing")
        need(electrical.get("p119_visual_correction_dossier") == IDENTIFIER, "R230 dossier missing from release metadata")
        need(all(item in electrical["supporting_identifiers"] for item in ("V3-P1.19-VISUAL-CORRECTION-CANDIDATE", IDENTIFIER)), "R230 support identities missing")
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: R230 P1.19 visual-correction dossier is fail-closed and semantically parity-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
