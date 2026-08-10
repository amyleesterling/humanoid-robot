"""Fail-closed validation for HR-V0-COLLAPSE-ENV-P0.1."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "power-loss-envelope-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-collapse-envelope-metrology-template-p0.1.csv"
GUIDE = ROOT / "release" / "hr-v0" / "collapse-envelope-p0.1" / "index.html"


def rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AssertionError(f"missing {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    summary = json.loads((OUT / "collapse-envelope-summary.json").read_text(encoding="utf-8"))
    assert summary["revision"] == "HR-V0-COLLAPSE-ENV-P0.1"
    assert summary["arm_revision"] == "HR-V0-ARM-ARCH-P0.7"
    assert summary["guard_revision"] == "HR-V0-GUARD-P0.3"
    assert math.isclose(summary["known_brep_radius_bound_mm"], 338.740914, abs_tol=0.000001)
    assert summary["controlled_ledger_radius_mm"] == 360.0
    assert summary["combined_known_input_radius_mm"] == 360.0
    assert summary["guard_reserved_radius_mm"] == 450.0
    assert summary["radial_unallocated_margin_mm"] == 90.0
    assert summary["known_x_extent_mm"] == [-42.0, 42.0]
    assert summary["known_input_z_extent_at_g0_mm"] == [140.0, 860.0]
    assert summary["object_catch_top_z_mm"] == 26.0
    assert summary["object_catch_to_controlled_arm_envelope_gap_mm"] == 114.0
    assert summary["known_input_fit"] is True
    assert summary["current_floor_tray_role"] == "OBJECT CATCH ENVELOPE ONLY - ZERO ARM SUPPORT OR ENERGY CREDIT"
    assert len(summary["open_exclusions"]) == 10

    components = rows(OUT / "collapse-envelope-components.csv")
    assert len(components) == 11
    assert {row["motion_group"] for row in components} == {"J1_MOVING", "J1_PLUS_J2_MOVING"}
    assert max(float(row["continuous_shoulder_radius_bound_mm"]) for row in components) == 338.740914

    fits = rows(OUT / "guard-fit-screen.csv")
    assert len(fits) == 8
    assert all("FAIL" not in row["result"] for row in fits)
    c8 = next(row for row in fits if row["fit_id"] == "CEF-008")
    assert c8["remaining_margin_mm"] == "114.000000"
    assert c8["result"] == "NO ARM CONTACT EXPECTED - OBJECT CATCH ROLE ONLY"

    roles = rows(OUT / "receiver-role-disposition.csv")
    assert len(roles) == 5
    floor = next(row for row in roles if row["role_id"] == "RCD-001")
    assert floor["controlled_role"] == "OBJECT CATCH ENVELOPE ONLY"
    assert floor["arm_support_credit"] == "ZERO"
    assert floor["energy_or_load_credit"] == "ZERO"
    assert all(row["status"] != "RELEASED" for row in roles)

    surveys = rows(FORM)
    assert len(surveys) == 18
    assert all(row["result"] == "NOT EXECUTED" for row in surveys)
    assert all(row["authorization"] == "NOT AUTHORIZED" for row in surveys)

    step = OUT / "HR-V0_collapse-envelope-review.step"
    glb = OUT / "HR-V0_collapse-envelope-review.glb"
    poster = OUT / "collapse-envelope-poster.svg"
    assert step.stat().st_size > 5_000
    assert glb.stat().st_size > 100_000
    assert poster.stat().st_size > 1_000
    imported = cq.importers.importStep(str(step))
    assert len(imported.solids().vals()) == 1

    html = GUIDE.read_text(encoding="utf-8")
    for required in (
        "The guard volume fits. The floor tray does not catch the arm.",
        "338.741 mm", "90.000 mm", "114.000 mm", "object-catch envelope only",
        "EG-008 and EG-009 do not close", "font:17px/1.55", "@media(max-width:760px)",
        "collapse-envelope-poster.svg",
    ):
        assert required.lower() in html.lower()

    gate_rows = rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")
    for gate_id in ("EG-008", "EG-009"):
        gate = next(row for row in gate_rows if row["gate_id"] == gate_id)
        assert gate["status"] == "partial"
        assert "docs/hr-v0-collapse-envelope-p0.1.md" in gate["evidence_location"]

    metadata = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    mechanical = next(item for item in metadata["current_products"] if item["identifier"] == "HR-V0-MECH-P0.6")
    assert "HR-V0-COLLAPSE-ENV-P0.1" in mechanical["supporting_identifiers"]

    print("HR-V0 collapse-envelope P0.1 check passed: 338.740914 mm known B-Rep radius; 360/450 mm controlled/reserved")
    print("P0.3 floor tray is OBJECT CATCH ONLY: 114 mm below the controlled arm envelope; zero arm-support credit")
    print("18 metrology rows NOT EXECUTED / NOT AUTHORIZED; EG-008 and EG-009 remain PARTIAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
