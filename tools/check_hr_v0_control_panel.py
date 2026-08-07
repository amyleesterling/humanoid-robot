"""Fail-closed checks for the HR-V0 control-panel physical-definition candidate."""

from __future__ import annotations

import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.3"
V3 = ROOT / "electrical" / "kicad" / "project-button-v3"
FORM = ROOT / "tests" / "forms" / "hr-v0-control-panel-receiving-assembly-template.csv"
H1_FORM = ROOT / "tests" / "forms" / "hr-v0-h1-receiving-template.csv"
DOC = ROOT / "docs" / "hr-v0-control-panel-p0.3.md"
H1_DOC = ROOT / "docs" / "hr-v0-h1-receiving-p0.1.md"
PRIMARY_SOURCES = ROOT / "references" / "primary-sources.md"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
H1_WARNING = "PRELIMINARY - NOT APPROVED FOR PANEL WIRING OR ROBOT ENERGIZATION"
PANEL_REFS = {"S0", "S1", "S2", "H1", "SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "XT1"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    return rows


def require_warning(rows: list[dict[str, str]], name: str, errors: list[str]) -> None:
    for index, row in enumerate(rows, 1):
        if row.get("warning") != WARNING:
            errors.append(f"{name} row {index} lacks exact warning")
        if row.get(None):
            errors.append(f"{name} row {index} has extra CSV fields")


def main() -> int:
    errors: list[str] = []
    expected_files = {
        "panel-bom.csv",
        "backplate-layout.csv",
        "door-layout.csv",
        "terminal-allocation.csv",
        "cable-entry-schedule.csv",
        "stationary-wire-schedule.csv",
        "thermal-space-screen.csv",
        "panel-layout.svg",
    }
    actual_files = {path.name for path in PACKAGE.iterdir()} if PACKAGE.is_dir() else set()
    if actual_files != expected_files:
        errors.append(f"panel package membership expected {sorted(expected_files)}, got {sorted(actual_files)}")

    tables = {
        name: read_csv(PACKAGE / name)
        for name in expected_files
        if name.endswith(".csv") and (PACKAGE / name).is_file()
    }
    for name, rows in tables.items():
        require_warning(rows, name, errors)

    bom = tables.get("panel-bom.csv", [])
    if len(bom) != 24 or {row.get("item_id") for row in bom} != {f"PAN-{i:03d}" for i in range(1, 25)}:
        errors.append("panel BOM must contain exactly PAN-001..PAN-024")
    required_mpn = {
        "PAN-001": "PJ242010RT",
        "PAN-002": "18P2117",
        "PAN-003": "3209510",
        "PAN-004": "3209523",
        "PAN-005": "3030417",
        "PAN-006": "3022218",
        "PAN-007": "0828734",
        "PAN-008": "1207650",
        "PAN-009": "3240189",
        "PAN-010": "HW1P-1FQD-A-24V",
        "PAN-011": "XW1E-BV402M-R",
        "PAN-012": "HW1B-M1F10-B",
        "PAN-013": "HW1B-M1F10-G",
        "PAN-014": "750104",
        "PAN-015": "2967060",
        "PAN-016": "LC1D25BD",
        "PAN-017": "PCB-P0.5",
        "PAN-018": "DXL-STAR-P0.1",
        "PAN-021": "PT 4-HESI (5X20), item 3211861",
        "PAN-022": "5025",
        "PAN-023": "FHAC0002SXJ",
        "PAN-024": "D-ST 4, item 3030420",
    }
    by_item = {row.get("item_id", ""): row for row in bom}
    for item_id, mpn in required_mpn.items():
        if by_item.get(item_id, {}).get("manufacturer_part_number") != mpn:
            errors.append(f"{item_id} exact candidate must remain {mpn}")
    if "HR-V0-H1-RCV-P0.1" not in by_item.get("PAN-010", {}).get("closure_evidence_required", ""):
        errors.append("PAN-010 does not require the controlled H1 receiving/characterization route")
    for item_id in ("PAN-019", "PAN-020"):
        if by_item.get(item_id, {}).get("manufacturer_part_number") != "SELECTION REQUIRED":
            errors.append(f"{item_id} must remain SELECTION REQUIRED")
    for row in bom:
        if not any(token in row.get("physical_release", "") for token in ("HOLD", "NO ")):
            errors.append(f"{row.get('item_id')} has released-looking physical state")

    backplate = tables.get("backplate-layout.csv", [])
    if len(backplate) != 20:
        errors.append(f"backplate layout expected 20 rows, found {len(backplate)}")
    for row in backplate:
        try:
            x = float(row["x_mm"])
            y = float(row["y_mm"])
            width = float(row["width_mm"])
            height = float(row["height_mm"])
        except (KeyError, ValueError):
            errors.append(f"{row.get('layout_id')} has nonnumeric geometry")
            continue
        if min(x, y, width, height) < 0 or x + width > 431.8 + 1e-6 or y + height > 533.4 + 1e-6:
            errors.append(f"{row.get('layout_id')} leaves nominal 18P2117 boundary")
        if not any(token in row.get("release_state", "") for token in ("HOLD", "CANDIDATE", "SELECTION REQUIRED")):
            errors.append(f"{row.get('layout_id')} has released-looking layout state")
    reserve = next((row for row in backplate if row.get("layout_id") == "BP-020"), {})
    for ref in ("JC1", "SD1", "F0-F3 LINKS", "FSR1-FSR2 LINKS"):
        if ref not in reserve.get("reference", ""):
            errors.append(f"selection reserve omits {ref}")
    bottom_expected = {
        "BP-016": (54.0, 385.0, 100.0, 130.0),
        "BP-018": (175.0, 385.0, 25.0, 75.0),
        "BP-019": (210.0, 385.0, 30.0, 130.0),
        "BP-020": (250.0, 375.0, 127.8, 140.0),
    }
    for layout_id, expected in bottom_expected.items():
        row = next((entry for entry in backplate if entry.get("layout_id") == layout_id), {})
        try:
            actual = tuple(float(row[field]) for field in ("x_mm", "y_mm", "width_mm", "height_mm"))
        except (KeyError, ValueError):
            actual = ()
        if actual != expected:
            errors.append(f"{layout_id} protection/reserve envelope changed: {actual}")

    door = tables.get("door-layout.csv", [])
    if len(door) != 5 or {row.get("reference") for row in door} != {"S0", "S1", "S2", "H1", "DOOR-LEGEND"}:
        errors.append("door layout must contain S0/S1/S2/H1 and limitation legend")
    h1 = next((row for row in door if row.get("reference") == "H1"), {})
    h1_text = " ".join(h1.values()).upper()
    for required in ("DIAGNOSTIC", "NO SAFETY CREDIT"):
        if required not in h1_text:
            errors.append(f"H1 door record omits {required}")
    if "NO CUTOUT" not in h1.get("release_state", ""):
        errors.append("H1 door cutout is not fail-closed")

    terminals = tables.get("terminal-allocation.csv", [])
    expected_terminals = {
        "XT1-01": ("3209510", "TBD-1", "SAFETY_24V"),
        "XT1-02": ("3209523", "TBD-2", "SAFETY_0V"),
        "XT1-03": ("3209510", "TBD-3", "SR1_STATUS"),
        "XT1-04": ("3209510", "TBD-4", "SRA1_STATUS"),
        "XT1-05": ("3209510", "TBD-5", "K1_STATUS"),
        "XT1-06": ("3209510", "TBD-6", "K2_STATUS"),
    }
    if len(terminals) != 6:
        errors.append(f"terminal allocation expected 6 positions, found {len(terminals)}")
    for row in terminals:
        expected = expected_terminals.get(row.get("position", ""))
        actual = (row.get("manufacturer_part_number"), row.get("schematic_terminal"), row.get("net"))
        if expected != actual:
            errors.append(f"{row.get('position')} terminal allocation mismatch: {actual}")
        if row.get("bridge_state") != "NO BRIDGE":
            errors.append(f"{row.get('position')} contains an unapproved bridge")

    entries = tables.get("cable-entry-schedule.csv", [])
    if len(entries) != 6 or {row.get("entry_id") for row in entries} != {f"CE-{i:02d}" for i in range(1, 7)}:
        errors.append("cable entries must contain exactly CE-01..CE-06")
    for row in entries:
        if row.get("entry_hardware") != "SELECTION REQUIRED" or row.get("entry_release") != "NO HOLE / NO GLAND RELEASE":
            errors.append(f"{row.get('entry_id')} releases or infers cable-entry hardware")

    thermal = tables.get("thermal-space-screen.csv", [])
    if len(thermal) != 12 or {row.get("screen_id") for row in thermal} != {f"TS-{i:03d}" for i in range(1, 13)}:
        errors.append("thermal/space screen must contain exactly TS-001..TS-012")
    if sum(row.get("status") == "FAIL-CLOSED HOLD" for row in thermal) < 6:
        errors.append("thermal/space screen does not retain all required no-conclusion holds")

    source_wires = read_csv(V3 / "wire-number-table.csv")
    expected_wires = {
        row["wire_number"]: (row["sheet"], row["reference"], row["terminal"], row["pin_name"], row["net"])
        for row in source_wires
        if row.get("reference") in PANEL_REFS
    }
    physical_wires = tables.get("stationary-wire-schedule.csv", [])
    actual_wires = {
        row.get("wire_number", ""): (row.get("sheet"), row.get("reference"), row.get("terminal"), row.get("pin_name"), row.get("net"))
        for row in physical_wires
    }
    if len(expected_wires) != 66 or actual_wires != expected_wires:
        missing = sorted(set(expected_wires) - set(actual_wires))
        extra = sorted(set(actual_wires) - set(expected_wires))
        changed = sorted(key for key in set(expected_wires) & set(actual_wires) if expected_wires[key] != actual_wires[key])
        errors.append(f"physical wire schedule differs from bounded V3 endpoints; missing={missing}, extra={extra}, changed={changed}")
    physical_fields = ("conductor_part_number", "gauge", "color", "length_mm", "termination_a", "termination_b")
    for row in physical_wires:
        for field in physical_fields:
            if row.get(field) != "SELECTION REQUIRED":
                errors.append(f"{row.get('wire_number')} infers unreleased {field}: {row.get(field)!r}")
        if not row.get("release_state", "").startswith("NOT RELEASED"):
            errors.append(f"{row.get('wire_number')} has released-looking state")
    required_tbd = {"TBD-R1", "TBD-R2", "TBD-A1", "TBD-A2", "TBD-HA", "TBD-HB", "TBD-1", "TBD-2", "TBD-3", "TBD-4", "TBD-5", "TBD-6"}
    actual_tbd = {row.get("terminal") for row in physical_wires if row.get("terminal", "").startswith("TBD-")}
    if actual_tbd != required_tbd:
        errors.append(f"TBD terminal boundary changed: {sorted(actual_tbd)}")

    form = read_csv(FORM) if FORM.is_file() else []
    require_warning(form, FORM.name, errors)
    if len(form) != 22 or {row.get("step_id") for row in form} != {f"CP-{i:03d}" for i in range(1, 23)}:
        errors.append("panel receiving/assembly form must contain exactly CP-001..CP-022")
    for row in form:
        if row.get("record_id") != "NOT-EXECUTED" or row.get("status") != "NOT EXECUTED":
            errors.append(f"{row.get('step_id')} contains executed-looking evidence")

    h1_form = read_csv(H1_FORM) if H1_FORM.is_file() else []
    if len(h1_form) != 14 or {row.get("step_id") for row in h1_form} != {f"H1-{i:03d}" for i in range(1, 15)}:
        errors.append("H1 receiving form must contain exactly H1-001..H1-014")
    for row in h1_form:
        if row.get(None):
            errors.append(f"{row.get('step_id')} has extra CSV fields")
        if row.get("record_id") != "NOT-EXECUTED" or row.get("status") != "NOT EXECUTED":
            errors.append(f"{row.get('step_id')} contains executed-looking H1 evidence")
        if row.get("warning") != H1_WARNING:
            errors.append(f"{row.get('step_id')} lacks the exact H1 preliminary warning")

    doc = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for required in (
        "HR-V0-CP-P0.3",
        "P0.1 reserve is physically insufficient",
        "PJ242010RT",
        "PT 4-HESI (5X20)` item `3211861",
        "D-ST 4`, item `3030420",
        "84.20 x 124.31 mm",
        "No backplate, enclosure, DIN-rail, duct, or door hole coordinate is released",
        "A project-added DC 0 V/PE star point remains prohibited",
        "zero functional-safety credit",
        "66 V3 wire-number endpoints",
    ):
        if required not in doc:
            errors.append(f"control-panel document omits: {required}")

    h1_doc = H1_DOC.read_text(encoding="utf-8") if H1_DOC.is_file() else ""
    for required in (
        "HR-V0-H1-RCV-P0.1",
        "Project Button Electrical V3-P1.7",
        "TBD-HA` and `TBD-HB` are project placeholders only",
        "does not choose a current limit, fuse, test-lead rating, or source",
        "RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY",
        "must never be described as \"safe\" or \"armed\"",
    ):
        if required not in h1_doc:
            errors.append(f"H1 receiving procedure omits: {required}")

    primary_sources = PRIMARY_SOURCES.read_text(encoding="utf-8") if PRIMARY_SOURCES.is_file() else ""
    for required in (
        "HW1P-1FQD-A-24V",
        "official product page rechecked 2026-08-07",
        "current `HW Series Catalog_Screw` supporting document is dated 2026-07-23",
        "does not close received terminal markings, internal polarity/bridge behavior",
        "HR-V0-H1-RCV-P0.1",
        "PT 4-HESI (5X20)`, item `3211861",
        "D-ST 4",
        "3030420",
        "PJ242010RT",
        "18P2117",
        "84.20 x 124.31 mm body",
    ):
        if required not in primary_sources:
            errors.append(f"primary-source register omits H1 evidence limit: {required}")

    svg = PACKAGE / "panel-layout.svg"
    if svg.is_file():
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            errors.append(f"panel-layout.svg does not parse: {exc}")
        svg_text = svg.read_text(encoding="utf-8")
        for required in ("NO FABRICATION OUTPUTS", "SELECTION RESERVE", "P0.1 DOES NOT FIT", "NO DRILLING", "NO MOTION AUTHORITY", "NOT “SAFE” · NOT “ARMED”"):
            if required not in svg_text:
                errors.append(f"panel-layout.svg omits: {required}")
        font_sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", svg_text)]
        if not font_sizes or min(font_sizes) < 16:
            errors.append(f"panel-layout.svg functional font size below 16 px: {font_sizes}")

    if errors:
        print("HR-V0 control-panel check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("HR-V0 control-panel P0.3 check passed: 24 BOM rows; 20 backplate allocations; 66 V3 wire endpoints")
    print("Six cable entries, twelve thermal/space screens, twenty-two panel records and fourteen H1 records remain fail-closed")
    print("No hole, cut length, wire, fuse, PE bond, cable entry, PCB fabrication, assembly or energization release exists")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
