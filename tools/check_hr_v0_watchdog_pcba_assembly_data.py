"""Fail-closed validation for HR-V0-WD-PCBA-DATA-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-assembly-data-p0.1" / "index.html"
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
R132 = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-rfi-p0.1" / "placement-process-register.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    placements = rows("assembly-placement-reference.csv")
    mechanical = rows("mechanical-feature-register.csv")
    bom = rows("board-assembly-bom.csv")
    controls = rows("coordinate-orientation-control.csv")
    notes = rows("assembly-note-register.csv")
    file_states = rows("assembly-data-file-state.csv")
    holds = rows("assembly-data-holds.csv")
    sources = rows("source-register.csv")
    with R132.open(newline="", encoding="utf-8") as handle:
        r132 = list(csv.DictReader(handle))
    r132_populated = {row["reference"] for row in r132 if row["process_class"] != "MECHANICAL_NPTH"}
    r132_mechanical = {row["reference"] for row in r132 if row["process_class"] == "MECHANICAL_NPTH"}

    if len(placements) != 42 or {row["reference"] for row in placements} != r132_populated:
        failures.append("placement data must cover the exact 42 populated R132 references")
    if len(mechanical) != 4 or {row["reference"] for row in mechanical} != r132_mechanical:
        failures.append("mechanical data must cover the exact four R132 NPTH references")
    if sum(int(row["quantity_per_board"]) for row in bom) != 42 or len(bom) != 16:
        failures.append("board BOM must contain 16 exact-MPN lines totaling 42 parts")
    bom_refs = {ref for row in bom for ref in row["references"].split(";")}
    if bom_refs != r132_populated:
        failures.append("BOM references do not reconcile to placement membership")
    if any(row["manufacturer_part_number"] in ("", "SELECTION REQUIRED") for row in bom):
        failures.append("every populated BOM line must retain its explicit exact candidate MPN")
    if any(row["alternate_policy"] != "NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION" for row in bom):
        failures.append("no-alternate policy changed")
    if len(controls) != 5 or {row["control_id"] for row in controls} != {f"WD-DATA-{i:03d}" for i in range(1, 6)}:
        failures.append("coordinate/orientation control register changed")
    if not any(row["state"] == "PROHIBITED UNTIL SUPPLIER CONVENTION ACCEPTED" for row in controls):
        failures.append("machine-import prohibition is missing")
    if len(notes) != 10 or len(holds) != 12 or {row["status"] for row in holds} != {"OPEN"}:
        failures.append("assembly notes/holds changed or a hold appears closed")
    if len(file_states) != 10:
        failures.append("file-state register must contain ten records")
    prohibited_release = ("RELEASED CAM", "MACHINE READY", "FABRICATION AUTHORIZED", "ASSEMBLY AUTHORIZED")
    if any(any(token in row["state"] for token in prohibited_release) for row in file_states):
        failures.append("file-state register contains a released-looking state")
    if len(sources) != 10 or any(not row["revision_date"] or not row["locator"] for row in sources):
        failures.append("source register must retain ten dated locator rows")
    for name in ("assembly-placement-reference.csv","mechanical-feature-register.csv","board-assembly-bom.csv","coordinate-orientation-control.csv","assembly-note-register.csv","assembly-data-file-state.csv","assembly-data-holds.csv","source-register.csv"):
        if any(row.get("warning") != WARNING for row in rows(name)):
            failures.append(f"exact warning missing from {name}")

    if {row["side"] for row in placements} != {"TOP"}:
        failures.append("all populated references must remain top-side")
    if sum(row["process_class"] == "SMD_REFLOW" for row in placements) != 38 or sum(row["process_class"] == "MANUAL_THT_POST_REFLOW" for row in placements) != 4:
        failures.append("38 SMD / 4 THT split changed")
    if any(row["assembler_transform_state"] != "SELECTION REQUIRED - DO NOT IMPORT AS MACHINE XYRS" for row in placements):
        failures.append("placement rows do not retain the machine-import hold")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-WD-PCBA-DATA-P0.1" or status.get("board") != "PCB-P0.7":
        failures.append("package identifier or board binding changed")
    if status.get("board_sha256") == hashlib.sha256(BOARD.read_bytes()).hexdigest():
        failures.append("historical R133 P0.7 hash unexpectedly equals current metadata-only P0.8 source")
    for key in ("supplier_normalized_xyrs_exists","cam_exists","provider_selected","provider_contacted","files_uploaded","fabrication_authorized","assembly_authorized","physical_article_exists","energization_authorized"):
        if status.get(key) is not False:
            failures.append(f"{key} must remain false")
    if status.get("internal_review_only") is not True or status.get("populated_references") != 42 or status.get("bom_lines") != 16:
        failures.append("internal-review status/counts changed")

    svg = (PKG / "assembly-top-reference.svg").read_text(encoding="utf-8")
    for token in ("PCB-P0.7 top assembly reference map", WARNING, "Not machine-ready XYRS"):
        if token not in svg:
            failures.append(f"assembly map missing {token}")
    web = WEB.read_text(encoding="utf-8")
    for token in (WARNING,"HR-V0-WD-PCBA-DATA-P0.1","42","exact-MPN BOM lines","data-filter=\"SMD_REFLOW\"","font:17px","font-size:14px","font-size:16px"):
        if token not in web:
            failures.append(f"interactive guide missing {token}")
    for tiny in ("font-size:11px","font-size:10px","font-size:9px"):
        if tiny in web:
            failures.append(f"interactive guide contains prohibited {tiny}")

    required_docs = (
        ROOT / "docs" / "hr-v0-watchdog-pcba-assembly-data-p0.1.md",
        ROOT / "docs" / "reviews" / "2026-08-09-r133-validation-record.md",
        ROOT / "docs" / "reviews" / "2026-08-09-r133-independent-review-request.md",
        ROOT / "docs" / "reviews" / "2026-08-09-sol-r12-post-r133-status.md",
    )
    for path in required_docs:
        if not path.is_file() or WARNING not in path.read_text(encoding="utf-8"):
            failures.append(f"controlled warning document missing: {path.relative_to(ROOT)}")

    if failures:
        print("HR-V0 watchdog PCBA assembly-data check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCBA assembly-data P0.1 check passed")
    print("Historical PCB-P0.7: 42 populated refs, 16 exact-MPN BOM lines, 38 SMD / 4 THT, 4 NPTH; current PCB-P0.8 is geometry/topology-identical under R138")
    print("Internal review only; no supplier-normalized XYRS, CAM, upload, fabrication, assembly or energization authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
