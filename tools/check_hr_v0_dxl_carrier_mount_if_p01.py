"""Fail-closed checks for the R162 no-drill carrier mounting package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "mechanical" / "hr-v0-dxl-carrier-mount-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-carrier-mount-p0.1"
PCB = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "hr-v0-dxl-protection-carrier-p0.3.kicad_pcb"
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "backplate-layout.csv"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    common = {
        "README.md", "package-status.json", "file-manifest.csv", "source-register.csv",
        "hardware-bom.csv", "stack-calculation.csv", "hole-coordinate-register.csv",
        "clearance-screen.csv", "unresolved-selections.csv", "no-drill-metrology-form.csv",
        "acceptance-matrix.csv",
    }
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
        need(actual == expected, f"membership mismatch {directory.name}: {sorted(actual ^ expected)}")
        need(not any(p.suffix.lower() in {".zip", ".7z", ".rar", ".pdf"} for p in directory.rglob("*")), "archive/PDF prohibited")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1", "identifier changed")
    need(status.get("round") == "R162", "round changed")
    counts = {
        "carrier_count": 3, "mounting_hole_centers": 12, "exact_standoff_candidates": 12,
        "exact_screw_candidates": 24, "stack_calculations": 9, "clearance_screens": 8,
        "unresolved_selections": 14, "metrology_rows": 10, "acceptance_rows": 12,
    }
    for key, value in counts.items():
        need(status.get(key) == value, f"status count changed: {key}")
    false_keys = {
        "r161_route_screens_still_current", "panel_hole_diameter_selected", "mounting_released",
        "hardware_procurement_authorized", "physical_article_exists", "physical_test_executed",
        "qualified_review_complete", "supplier_upload_authorized", "quotation_authorized",
        "procurement_authorized", "fabrication_authorized", "assembly_authorized",
        "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit",
    }
    for key in false_keys:
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    sources = {PCB.relative_to(ROOT).as_posix(): PCB, PANEL.relative_to(ROOT).as_posix(): PANEL}
    need(set(status.get("source_hashes", {})) == set(sources), "source hash membership changed")
    for rel, path in sources.items():
        need(status["source_hashes"].get(rel) == digest(path), f"source hash mismatch: {rel}")
    pcb_text = PCB.read_text(encoding="utf-8")
    need("(thickness 1.6)" in pcb_text, "PCB thickness candidate changed")
    for token in ('"MH1"', '"MH2"', '"MH3"', '"MH4"', '"JIN1"', '"JOUT1"'):
        need(token in pcb_text, f"PCB reference missing: {token}")

    source_rows = rows(OUT / "source-register.csv")
    need(len(source_rows) == 7 and all(r["warning"] == WARNING for r in source_rows), "source register changed")
    for domain in ("hammfg.com", "essentracomponents.com", "jst-mfg.com"):
        need(any(domain in r["url"] for r in source_rows), f"primary source missing: {domain}")
    need(all(r["document_revision_date"] for r in source_rows), "source revision/access field blank")

    hardware = rows(OUT / "hardware-bom.csv")
    need(len(hardware) == 4, "hardware BOM row count changed")
    need(sum(int(r["quantity_for_three_carriers"]) for r in hardware if r["item_id"] == "MNT-01") == 12, "standoff quantity changed")
    need(sum(int(r["quantity_for_three_carriers"]) for r in hardware if r["item_id"] in {"MNT-02", "MNT-03"}) == 24, "screw quantity changed")
    need(next(r for r in hardware if r["item_id"] == "MNT-04")["manufacturer_part_number"] == "SELECTION REQUIRED", "panel hole falsely selected")
    need(all("NOT RELEASED" in r["state"] or "DO NOT DRILL" in r["state"] for r in hardware), "hardware released")

    stack = rows(OUT / "stack-calculation.csv")
    expected = {"STK-01": 4.4, "STK-02": 1.6, "STK-03": 3.46, "STK-04": 2.54, "STK-05": 11.6, "STK-06": 13.4, "STK-07": 17.25, "STK-08": 1.75, "STK-09": 2.05}
    need(len(stack) == 9, "stack row count changed")
    for row in stack:
        need(float(row["result_mm"]) == expected[row["screen_id"]], f"stack arithmetic changed: {row['screen_id']}")
        need(row["release_effect"] == "none" and row["warning"] == WARNING, f"stack row grants release: {row['screen_id']}")

    holes = rows(OUT / "hole-coordinate-register.csv")
    need(len(holes) == 12 and len({(r["carrier_reference"], r["hole_reference"]) for r in holes}) == 12, "hole register changed")
    origins = {"LIM1": (64.0, 539.6), "LIM2": (174.0, 539.6), "LIM3": (64.0, 609.6)}
    rels = {"MH1": (5.0, 5.0), "MH2": (95.0, 5.0), "MH3": (5.0, 55.0), "MH4": (95.0, 55.0)}
    for row in holes:
        x, y = origins[row["carrier_reference"]]
        dx, dy = rels[row["hole_reference"]]
        need(float(row["candidate_panel_center_x_mm"]) == x + dx and float(row["candidate_panel_center_y_mm"]) == y + dy, f"hole coordinate changed: {row['carrier_reference']}/{row['hole_reference']}")
        need(row["panel_hole"] == "SELECTION REQUIRED" and row["state"] == "CENTER CANDIDATE - DO NOT DRILL", "hole released")

    clearance = rows(OUT / "clearance-screen.csv")
    need(len(clearance) == 8, "clearance row count changed")
    need(any(r["nominal_clearance_mm"] == "SELECTION REQUIRED" for r in clearance), "open physical clearances hidden")
    unresolved = rows(OUT / "unresolved-selections.csv")
    need(len(unresolved) == 14 and all(r["state"] == "SELECTION REQUIRED" for r in unresolved), "open selections changed")
    metrology = rows(OUT / "no-drill-metrology-form.csv")
    need(len(metrology) == 10 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["operator"] and not r["reviewer"] for r in metrology), "metrology evidence falsely completed")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 12 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in acceptance), "acceptance evidence falsely completed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "svg text{font:14px", "Carrier mounting, measured before metal", "0</div><b>released holes", "DO NOT DRILL", "Before any hole exists", WARNING):
        need(token in page, f"interactive guide token missing: {token}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    for directory in (ENG, OUT):
        manifest = rows(directory / "file-manifest.csv")
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(row["sha256"] == digest(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch: {directory.name}/{row['path']}")

    if failures:
        print("HR-V0-DXL-CARRIER-MOUNT-IF-P0.1 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-CARRIER-MOUNT-IF-P0.1 PASS")
    print("  3 re-centered carriers; 12 center candidates; exact but unreleased mounting stack")
    print("  14 selections, 10 metrology rows and 12 acceptance rows remain OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
