"""Validate HR-V0-WD-PCBA-RFI-P0.1 fail-closed inquiry controls."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-rfi-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-rfi-p0.1" / "index.html"
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
LAND = ROOT / "release" / "hr-v0" / "watchdog-pcb-land-pattern-audit-p0.1" / "land-pattern-audit.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict]:
    with (PKG / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    placements = rows("placement-process-register.csv")
    conformance = rows("current-geometry-conformance-register.csv")
    providers = rows("provider-capability-screen.csv")
    requirements = rows("assembly-requirements.csv")
    questions = rows("capability-question-register.csv")
    files = rows("controlled-file-release-register.csv")
    holds = rows("closure-holds.csv")
    fai = rows("first-article-receiving-template.csv")
    sources = rows("source-register.csv")
    with LAND.open(newline="", encoding="utf-8") as handle:
        land_refs = {row["reference"] for row in csv.DictReader(handle)}

    if len(placements) != 46 or {row["reference"] for row in placements} != land_refs:
        failures.append("placement register does not cover the exact 46-reference current-board audit")
    counts = {kind: sum(row["process_class"] == kind for row in placements) for kind in ("SMD_REFLOW", "MANUAL_THT_POST_REFLOW", "MECHANICAL_NPTH")}
    if counts != {"SMD_REFLOW":38, "MANUAL_THT_POST_REFLOW":4, "MECHANICAL_NPTH":4}:
        failures.append(f"process split changed: {counts}")
    corrections = {row["current_geometry_correction"] for row in conformance}
    if len(conformance) != 9 or sum(int(row["quantity"]) for row in conformance) != 37 or corrections != {"NONE", "RECTANGLE APPLIED IN PCB-P0.7"}:
        failures.append("current-geometry reconciliation must cover 21 retained R89 references plus 16 R132 rectangular Harwin corrections")
    if len(providers) != 4 or {row["contact_state"] for row in providers} != {"NOT CONTACTED"}:
        failures.append("provider screen must contain four not-contacted routes")
    if len(requirements) != 20 or {row["state"] for row in requirements} != {"OPEN - SUPPLIER RESPONSE REQUIRED"}:
        failures.append("assembly requirements are incomplete or not fail-closed")
    if len(questions) != 24 or {row["state"] for row in questions} != {"NOT SENT"} or any(row["response"] for row in questions):
        failures.append("capability questions must be 24 blank, not-sent records")
    if len(files) != 10 or any("RELEASED" == row["state"] for row in files):
        failures.append("file-release register changed or releases a supplier artifact")
    if len(holds) != 14 or sum(row["status"] == "PARTIAL" for row in holds) != 3 or sum(row["status"] == "OPEN" for row in holds) != 11:
        failures.append("closure holds must remain 3 PARTIAL / 11 OPEN")
    if len(fai) != 24 or {row["state"] for row in fai} != {"NOT EXECUTED - NO ARTICLE"}:
        failures.append("first-article template must contain 24 unexecuted rows")
    if len(sources) != 16 or any(not row["revision_date"] or not row["locator"] for row in sources):
        failures.append("source register must contain sixteen dated locators")
    for name in ("placement-process-register.csv", "current-geometry-conformance-register.csv", "provider-capability-screen.csv", "assembly-requirements.csv", "capability-question-register.csv", "controlled-file-release-register.csv", "closure-holds.csv", "first-article-receiving-template.csv", "source-register.csv"):
        if any(row.get("warning") != WARNING for row in rows(name)):
            failures.append(f"warning missing or changed in {name}")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    expected_false = ("provider_selected", "provider_contacted", "files_uploaded", "quote_requested", "cam_released", "fabrication_authorized", "assembly_authorized", "physical_article_exists", "energization_authorized")
    if status.get("identifier") != "HR-V0-WD-PCBA-RFI-P0.1" or status.get("current_board") != "PCB-P0.7" or status.get("board_changed") is not True:
        failures.append("package identity/current-board binding changed")
    if any(status.get(key) is not False for key in expected_false):
        failures.append("one or more release/physical status flags are not false")
    if status.get("counts") != {"footprints":46,"smd":38,"tht":4,"mechanical":4}:
        failures.append("package-status counts changed")
    if status.get("board_sha256") != hashlib.sha256(BOARD.read_bytes()).hexdigest():
        failures.append("package-status board SHA-256 does not match current native source")
    if status.get("current_conformance_groups") != 9 or status.get("current_conformance_references") != 37:
        failures.append("package-status current-conformance counts changed")

    board_text = BOARD.read_text(encoding="utf-8-sig")
    for token in ('rev "PCB-P0.7 / Electrical V3-P1.13"', "TI_PW0016A_Example_Land", "TI_DBQ0016A_Example_Land", "VO618A_Option7_SMD", WARNING):
        if token not in board_text:
            failures.append(f"current native board missing {token}")
    html = WEB.read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-WD-PCBA-RFI-P0.1", "38", "SMD placements", "NOT CONTACTED", "font:17px", "font-size:14px", "font-size:16px"):
        if token not in html:
            failures.append(f"web guide missing {token}")
    for tiny in ("font-size:11px", "font-size:10px", "font-size:9px"):
        if tiny in html:
            failures.append(f"web guide contains prohibited {tiny}")
    for path in (
        ROOT / "docs" / "hr-v0-watchdog-pcba-capability-inquiry-p0.1.md",
        ROOT / "docs" / "reviews" / "2026-08-09-r132-independent-review-request.md",
        ROOT / "docs" / "reviews" / "2026-08-09-r132-validation-record.md",
        ROOT / "docs" / "reviews" / "2026-08-09-sol-r12-post-r132-status.md",
    ):
        if not path.is_file() or WARNING not in path.read_text(encoding="utf-8"):
            failures.append(f"controlled warning document missing: {path.relative_to(ROOT)}")

    if failures:
        print("HR-V0 watchdog PCBA inquiry check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCBA inquiry P0.1 check passed")
    print("PCB-P0.7: 46 references, 16 exact Harwin shape corrections, 38 SMD / 4 post-reflow THT / 4 NPTH; 4 provider routes; 20 requirements; 24 unsent questions; 14 holds")
    print("No provider contact, upload, quote, CAM, fabrication, assembly or energization authorization exists")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
