"""Fail-closed validation for R129 receiver detail P0.2."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq

from hr_v0_r213_compat import R213_MECHANICAL_RELEASE_STATE, r213_mechanical_successor_is_controlled


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-detail-p0.2"
DOC = ROOT / "docs" / "hr-v0-passive-arm-receiver-detail-p0.2.md"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-detail-p0.2" / "index.html"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
RELEASE = ROOT / "release" / "hr-v0" / "release-candidate.json"
MANIFEST = ROOT / "cad" / "hr-v0" / "generated" / "SOURCE-MANIFEST.csv"
IDENTIFIER = "HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    required = {
        "closure-holds.csv", "contact-layer-cut-plan.csv", "exact-candidate-bom.csv",
        "FAB-REC-001-platen-blank-drawing.svg", "FAB-REC-001-platen-blank.step", "FAB-REC-001-platen-blank.dxf",
        "FAB-REC-002-shock-plate-blank.step", "FAB-REC-002-shock-plate-blank.dxf",
        "FAB-REC-003-guide-tab-blank.step", "FAB-REC-003-guide-tab-blank.dxf",
        "HR-V0_passive-arm-receiver-detail-candidate.step", "HR-V0_passive-arm-receiver-detail-review.glb",
        "interface-register.csv", "load-path-register.csv", "receiver-detail-summary.json",
        "receiver-section-drawing.svg", "source-register.csv", "tolerance-stack.csv",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    assert actual == required, f"R129 artifact set drift: missing={sorted(required-actual)} extra={sorted(actual-required)}"

    summary = json.loads((OUT / "receiver-detail-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == IDENTIFIER
    assert summary["warning"] == WARNING
    assert summary["parent_identifiers"] == ["HR-V0-PASSIVE-ARM-RECEIVER-P0.1", "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1"]
    assert close(summary["receiver_top_z_mm"], 320.0)
    assert close(summary["platen_bottom_z_mm"], 304.125)
    assert close(summary["backup_stop_top_z_mm"], 294.5)
    assert close(summary["backup_gap_mm"], 9.625)
    assert close(summary["catalog_stroke_mm"], 8.128)
    assert close(summary["nominal_residual_after_catalog_stroke_mm"], 1.497)
    assert close(summary["known_commanded_clearance_mm"], 63.10647837214253)
    fit = summary["assembly_bounds_and_guard_margins"]
    for key, value in {
        "x_min_mm": -125.0, "x_max_mm": 125.0, "y_min_mm": -430.0, "y_max_mm": 430.0,
        "z_min_mm": 20.0, "z_max_mm": 320.0, "guard_x_margin_left_mm": 75.0,
        "guard_x_margin_right_mm": 75.0, "guard_y_margin_front_mm": 20.0, "guard_y_margin_rear_mm": 20.0,
    }.items():
        assert close(fit[key], value), (key, fit[key], value)
    assert summary["bom_rows"] == 16 and summary["interface_rows"] == 7 and summary["hold_rows"] == 12
    assert summary["gate_state"] == "EG-008 AND EG-009 REMAIN PARTIAL"

    assembly = cq.importers.importStep(str(OUT / "HR-V0_passive-arm-receiver-detail-candidate.step"))
    bounds = assembly.val().BoundingBox()
    for actual_value, expected in ((bounds.xmin,-125.0),(bounds.xmax,125.0),(bounds.ymin,-430.0),(bounds.ymax,430.0),(bounds.zmin,20.0),(bounds.zmax,320.0)):
        assert close(actual_value, expected), (actual_value, expected)

    blanks = {
        "FAB-REC-001-platen-blank.step": (180.0, 800.0, 6.35),
        "FAB-REC-002-shock-plate-blank.step": (160.0, 40.0, 6.35),
        "FAB-REC-003-guide-tab-blank.step": (20.0, 50.0, 6.35),
    }
    for filename, expected in blanks.items():
        part = cq.importers.importStep(str(OUT / filename)).val().BoundingBox()
        measured = (part.xlen, part.ylen, part.zlen)
        assert all(close(a,b) for a,b in zip(measured, expected)), (filename, measured, expected)
        dxf = (OUT / Path(filename).with_suffix(".dxf").name).read_text(encoding="ascii", errors="strict")
        # Match DXF entity records, not header variables such as $DIMARCSYM.
        assert "\nCIRCLE\n" not in dxf and "\nARC\n" not in dxf, f"{filename} blank DXF unexpectedly contains drilled/curved features"

    bom = rows(OUT / "exact-candidate-bom.csv")
    assert len(bom) == 16
    by_item = {row["item"]: row for row in bom}
    assert by_item["REC-BOM-008"]["part_or_drawing"] == "20-4113" and by_item["REC-BOM-008"]["quantity"] == "8"
    assert by_item["REC-BOM-009"]["part_or_drawing"] == "11-5308" and by_item["REC-BOM-009"]["quantity"] == "32"
    assert by_item["REC-BOM-010"]["part_or_drawing"] == "14122" and by_item["REC-BOM-010"]["quantity"] == "32"
    assert by_item["REC-BOM-011"]["part_or_drawing"] == "TWA-01-20" and by_item["REC-BOM-011"]["quantity"] == "4"
    assert by_item["REC-BOM-012"]["part_or_drawing"] == "TS-01-20" and "CONFIGURED LENGTH/HOLE ORDER CODE SELECTION REQUIRED" in by_item["REC-BOM-012"]["selection_state"]
    assert by_item["REC-BOM-013"]["part_or_drawing"] == "MA30M" and "ACE APPLICATION ACCEPTANCE REQUIRED" in by_item["REC-BOM-013"]["selection_state"]
    assert by_item["REC-BOM-014"]["part_or_drawing"] == "0212037-50-10" and by_item["REC-BOM-014"]["quantity"] == "3"
    assert by_item["REC-BOM-015"]["part_or_drawing"] == "SELECTION REQUIRED"
    assert by_item["REC-BOM-016"]["part_or_drawing"] == "SELECTION REQUIRED"
    assert all("RELEASED" not in row["selection_state"] or "NOT RELEASED" in row["selection_state"] for row in bom)

    cuts = rows(OUT / "contact-layer-cut-plan.csv")
    assert [row["finished_y_mm"] for row in cuts] == ["266.7", "266.6", "266.7"]
    assert all(row["source_part"] == "0212037-50-10" and row["retention"] == "SELECTION REQUIRED" for row in cuts)
    assert close(sum(float(row["finished_y_mm"]) for row in cuts), 800.0)

    interfaces = rows(OUT / "interface-register.csv")
    assert len(interfaces) == 7
    assert sum(row["status"].startswith("PARTIAL") for row in interfaces) == 1
    assert sum(row["status"].startswith("OPEN") for row in interfaces) == 6
    assert any("DO NOT INFER THREAD PATTERN" in row["status"] for row in interfaces)

    loads = rows(OUT / "load-path-register.csv")
    assert len(loads) == 8
    assert next(row for row in loads if row["load_id"] == "REC-LD-005")["value"] == "2000.000"
    assert next(row for row in loads if row["load_id"] == "REC-LD-008")["value"] == "SELECTION REQUIRED"
    assert all("PASS" not in row["disposition"] for row in loads)

    tolerances = rows(OUT / "tolerance-stack.csv")
    assert len(tolerances) == 6
    assert next(row for row in tolerances if row["stack_id"] == "REC-TOL-005")["nominal_mm"] == "1.497"
    assert sum(row["status"].startswith("OPEN") for row in tolerances) == 5

    holds = rows(OUT / "closure-holds.csv")
    assert len(holds) == 12
    assert sum(row["status"] == "PARTIAL" for row in holds) == 4
    assert sum(row["status"] == "OPEN" for row in holds) == 8
    assert all(row["release_effect"] == "BLOCKS FABRICATION MOTION AND ENERGIZATION" for row in holds)

    sources = rows(OUT / "source-register.csv")
    assert len(sources) == 10
    assert {row["manufacturer"] for row in sources} >= {"ACE Controls Inc.", "igus", "80/20 Inc.", "Sorbothane Inc.", "ASTM International"}
    assert all(row["accessed"] and row["revision_or_date"] and row["url"].startswith("https://") for row in sources)

    for path in (DOC, GUIDE):
        text = path.read_text(encoding="utf-8")
        assert IDENTIFIER in text and WARNING in text
        assert "not a fabrication release" in text.lower() or "zero fabrication" in text.lower()
    html = GUIDE.read_text(encoding="utf-8")
    for required_text in ("font:17px/1.55", "font-size:14px", "TWA-01-20", "0212037-50-10", "20-4113", "EG-008 and EG-009 remain partial"):
        assert required_text in html, required_text
    assert "HR-V0_passive-arm-receiver-detail-review.glb" in html

    gates = {row["gate_id"]: row for row in rows(GATES)}
    for gate_id in ("EG-008", "EG-009"):
        assert gates[gate_id]["status"] == "partial"
        for evidence in ("docs/hr-v0-passive-arm-receiver-detail-p0.2.md", "cad/hr-v0/generated/passive-arm-receiver-detail-p0.2/", "release/hr-v0/passive-arm-receiver-detail-p0.2/index.html", "tools/check_hr_v0_passive_arm_receiver_detail_p02.py", IDENTIFIER):
            assert evidence in gates[gate_id]["evidence_location"], (gate_id, evidence)

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    mechanical = next(item for item in release["current_products"] if item["identifier"] == "HR-V0-MECH-P0.6")
    safety = next(item for item in release["current_products"] if item["identifier"] == "HR-V0-FSA-P0.1")
    assert IDENTIFIER in mechanical["supporting_identifiers"] and IDENTIFIER in safety["supporting_identifiers"]
    assert mechanical["release_state"] == R213_MECHANICAL_RELEASE_STATE
    assert r213_mechanical_successor_is_controlled(ROOT)
    assert "HR-V0-FAB-INPUT-P0.1" in mechanical["supporting_identifiers"]
    assert "HR-V0-DYN-TRACE-P0.1" in mechanical["supporting_identifiers"]
    assert safety["release_state"] == "measurable_srs_candidate_no_plr_or_sil_assigned_no_physical_validation"
    assert "HR-V0-SRS-P0.2" in safety["supporting_identifiers"]

    manifest_text = MANIFEST.read_text(encoding="utf-8")
    assert "passive-arm-receiver-detail-p0.2/receiver-detail-summary.json" in manifest_text
    assert WARNING in (OUT / "receiver-section-drawing.svg").read_text(encoding="utf-8")

    print("HR-V0 passive receiver detail P0.2 check passed")
    print("16 BOM rows; 7 interfaces; 12 holds; exact guide/contact/joint candidates remain unreleased")
    print("Nominal catch gap 9.625 mm; residual after catalog stroke 1.497 mm; tolerance stack remains open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
