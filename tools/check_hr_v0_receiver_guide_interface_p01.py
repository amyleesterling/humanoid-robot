"""Fail-closed validation for the R130 receiver guide-interface correction."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq

from hr_v0_r213_compat import R213_MECHANICAL_RELEASE_STATE, r213_mechanical_successor_is_controlled


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "receiver-guide-interface-p0.1"
DOC = ROOT / "docs" / "hr-v0-receiver-guide-interface-p0.1.md"
GUIDE = ROOT / "release" / "hr-v0" / "receiver-guide-interface-p0.1" / "index.html"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
RELEASE = ROOT / "release" / "hr-v0" / "release-candidate.json"
MANIFEST = ROOT / "cad" / "hr-v0" / "generated" / "SOURCE-MANIFEST.csv"
IDENTIFIER = "HR-V0-RECEIVER-GUIDE-IF-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    required = {
        "FAB-REC-004-guide-angle-coordinate-drawing.svg",
        "FAB-REC-004-guide-angle-hole-free-envelope.step",
        "HR-V0_receiver-guide-interface-review.glb",
        "HR-V0_receiver-guide-interface-review.step",
        "catalog-coordinate-register.csv",
        "closure-holds.csv",
        "guide-interface-summary.json",
        "hole-center-control.csv",
        "incompatibility-and-pattern-proof.csv",
        "interface-register.csv",
        "load-and-mass-screen.csv",
        "source-register.csv",
        "supplier-rfi-unsent.md",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    assert actual == required, f"R130 artifact drift: missing={sorted(required-actual)} extra={sorted(actual-required)}"

    summary = json.loads((OUT / "guide-interface-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == IDENTIFIER and summary["warning"] == WARNING
    assert summary["supersedes_interface_artifact"] == "R129 FAB-REC-003 20 x 50 mm guide tab envelope"
    assert summary["catalog_pattern_mm"] == {"A2": 53.0, "C2": 40.0, "K2": "M6", "max_torque_Nm": 1.84}
    assert summary["bracket_envelope_mm"] == {"flange_reach": 40.0, "face_width": 73.0, "height": 80.0, "wall": 6.35}
    assert close(summary["bracket_volume_mm3"], 52682.4575)
    assert close(summary["bracket_nominal_mass_kg"], 0.14224263525)
    assert close(summary["four_brackets_plus_platen_nominal_mass_kg"], 3.037850541)
    assert close(summary["derived_rail_end_spacing_mm"], 30.0)
    assert summary["coordinate_rows"] == 12 and summary["hole_center_rows"] == 24 and summary["hold_rows"] == 10
    assert summary["gate_state"] == "EG-008 AND EG-009 REMAIN PARTIAL"

    bracket = cq.importers.importStep(str(OUT / "FAB-REC-004-guide-angle-hole-free-envelope.step")).val()
    bounds = bracket.BoundingBox()
    for actual_value, expected in ((bounds.xmin,0.0),(bounds.xmax,40.0),(bounds.ymin,-36.5),(bounds.ymax,36.5),(bounds.zmin,0.0),(bounds.zmax,80.0)):
        assert close(actual_value, expected), (actual_value, expected)
    assert close(bracket.Volume(), 52682.4575)

    assembly = cq.importers.importStep(str(OUT / "HR-V0_receiver-guide-interface-review.step")).val().BoundingBox()
    for actual_value, expected in ((assembly.xmin,-125.0),(assembly.xmax,125.0),(assembly.ymin,-400.0),(assembly.ymax,400.0),(assembly.zmin,184.125),(assembly.zmax,310.475)):
        assert close(actual_value, expected, 2e-6), (actual_value, expected)

    catalog = rows(OUT / "catalog-coordinate-register.csv")
    assert len(catalog) == 12
    by_id = {row["coordinate_id"]: row for row in catalog}
    assert by_id["GUIDE-CAT-005"]["value_mm"] == "53.0"
    assert by_id["GUIDE-CAT-006"]["value_mm"] == "40.0"
    assert by_id["GUIDE-CAT-007"]["value_mm"] == "M6" and "thread depth" in by_id["GUIDE-CAT-007"]["tolerance"]
    assert by_id["GUIDE-CAT-012"]["value_mm"] == "30.0" and "not a configured order release" in by_id["GUIDE-CAT-012"]["release_boundary"]

    proof = rows(OUT / "incompatibility-and-pattern-proof.csv")
    assert len(proof) == 4
    assert proof[0]["available_face_mm"] == "20 x 50" and proof[0]["shortfall_mm"] == "33 x 0" and proof[0]["result"].startswith("FAIL")
    assert proof[1]["available_face_mm"] == "50 x 20" and proof[1]["shortfall_mm"] == "3 x 20" and proof[1]["result"].startswith("FAIL")
    assert proof[2]["available_face_mm"] == "73 x 80" and "NOMINAL COVERAGE ONLY" in proof[2]["result"]

    holes = rows(OUT / "hole-center-control.csv")
    assert len(holes) == 24
    assert sum(row["hole_id"].startswith("K2-") for row in holes) == 16
    assert sum(row["hole_id"].startswith("PLATEN-") for row in holes) == 8
    assert all("SELECTION REQUIRED" in row["diameter_or_thread"] and "NOT RELEASED" in row["status"] or "OPEN" in row["status"] for row in holes)
    assert {row["x_mm"] for row in holes if row["hole_id"].startswith("K2-")} == {"-95.000", "95.000"}
    assert {row["z_mm"] for row in holes if row["hole_id"].startswith("K2-")} == {"243.625", "283.625"}

    interfaces = rows(OUT / "interface-register.csv")
    assert len(interfaces) == 4
    assert sum(row["status"].startswith("PARTIAL") for row in interfaces) == 2
    assert sum(row["status"].startswith("OPEN") for row in interfaces) == 2
    assert any("OVERCONSTRAINT" in row["status"] for row in interfaces)

    loads = rows(OUT / "load-and-mass-screen.csv")
    assert len(loads) == 7
    assert next(row for row in loads if row["load_id"] == "GUIDE-LD-007")["value"] == "SELECTION REQUIRED"
    assert all("ACCEPT" not in row["status"] for row in loads)

    holds = rows(OUT / "closure-holds.csv")
    assert len(holds) == 10
    assert sum(row["status"] == "PARTIAL" for row in holds) == 2
    assert sum(row["status"] == "OPEN" for row in holds) == 8
    assert all(row["release_effect"] == "BLOCKS FABRICATION MOTION AND ENERGIZATION" for row in holds)

    sources = rows(OUT / "source-register.csv")
    assert len(sources) == 6
    assert all(row["manufacturer"].startswith("igus") and row["accessed"] == "2026-08-09" and row["url"].startswith("https://") for row in sources)
    assert any("no CAD file acquired or claimed" in row["boundary"] for row in sources)
    rfi = (OUT / "supplier-rfi-unsent.md").read_text(encoding="utf-8")
    assert "UNSENT - NO EXTERNAL CONTACT AUTHORIZED" in rfi and "No order, fabrication" in rfi

    for path in (DOC, GUIDE):
        text = path.read_text(encoding="utf-8")
        assert IDENTIFIER in text and WARNING in text
        assert "20 x 50" in text and "53 x 40" in text and "73 x 80" in text
    html = GUIDE.read_text(encoding="utf-8")
    for required_text in ("font:17px/1.55", "font-size:14px", "EG-008 and EG-009 remain partial", "HR-V0_receiver-guide-interface-review.glb"):
        assert required_text in html, required_text

    gates = {row["gate_id"]: row for row in rows(GATES)}
    for gate_id in ("EG-008", "EG-009"):
        assert gates[gate_id]["status"] == "partial"
        for evidence in ("docs/hr-v0-receiver-guide-interface-p0.1.md", "cad/hr-v0/generated/receiver-guide-interface-p0.1/", "release/hr-v0/receiver-guide-interface-p0.1/index.html", "tools/check_hr_v0_receiver_guide_interface_p01.py", IDENTIFIER):
            assert evidence in gates[gate_id]["evidence_location"], (gate_id, evidence)

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    mechanical = next(item for item in release["current_products"] if item["identifier"] == "HR-V0-MECH-P0.6")
    safety = next(item for item in release["current_products"] if item["identifier"] == "HR-V0-FSA-P0.1")
    assert IDENTIFIER in mechanical["supporting_identifiers"] and IDENTIFIER in safety["supporting_identifiers"]
    assert mechanical["release_state"] == R213_MECHANICAL_RELEASE_STATE
    assert r213_mechanical_successor_is_controlled(ROOT)
    assert "HR-V0-FAB-INPUT-P0.1" in mechanical["supporting_identifiers"]
    assert "HR-V0-DYN-TRACE-P0.1" in mechanical["supporting_identifiers"]
    assert safety["release_state"] == "r235_p121_application_evidence_route_zero_safety_credit_questions_unsent_tests_unexecuted_plr_sil_and_qualified_review_open"
    assert safety["watchdog_permit_topology_proof"] == "HR-V0-WD-PERMIT-TOPOLOGY-P0.1"
    assert safety["watchdog_interlock_candidate"] == "HR-V0-P120-WD-INTERLOCK-P0.1"
    assert safety["p121_sra1_supply_watchdog_dossier"] == "HR-V0-P121-SRA1-SUPPLY-WD-P0.1"
    assert safety["p121_application_evidence_dossier"] == "HR-V0-P121-APP-EVID-P0.1"
    assert "HR-V0-SRS-P0.2" in safety["supporting_identifiers"]
    assert "HR-V0-FS-REVIEW-ROUTE-P0.1" in safety["supporting_identifiers"]
    assert "receiver-guide-interface-p0.1/guide-interface-summary.json" in MANIFEST.read_text(encoding="utf-8")
    assert WARNING in (OUT / "FAB-REC-004-guide-angle-coordinate-drawing.svg").read_text(encoding="utf-8")

    print("HR-V0 receiver guide interface P0.1 check passed")
    print("R129 tab rejected; 12 catalog rows; 24 controlled centers; 10 fail-closed holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
