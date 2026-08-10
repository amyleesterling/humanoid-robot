#!/usr/bin/env python3
"""Fail-closed verification for HR-V0-GRIP-XC330-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad/vendor/robotis/xc330"
SOURCE = VENDOR / "XL-XC-330-official-source.stp"
OUT = ROOT / "cad/hr-v0/generated/xc330-gripper-feasibility-p0.1"
GUIDE = ROOT / "release/hr-v0/xc330-gripper-feasibility-p0.1/index.html"
EXPECTED_SOURCE_SHA256 = "E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def near(actual: float, expected: float, tolerance: float = 1e-5) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def check_source() -> None:
    assert SOURCE.is_file() and SOURCE.stat().st_size == 791238
    assert SOURCE.read_bytes().startswith(b"ISO-10303-21")
    assert digest(SOURCE) == EXPECTED_SOURCE_SHA256
    manifest = rows(VENDOR / "source-manifest-p0.1.csv")
    assert len(manifest) == 1
    assert manifest[0]["artifact_id"] == "R190-XC330-001"
    assert manifest[0]["sha256"] == EXPECTED_SOURCE_SHA256
    assert manifest[0]["access_date"] == "2026-08-10"
    assert "NO FABRICATION OR ENERGIZATION RELEASE" in manifest[0]["release_boundary"]

    shape = cq.importers.importStep(str(SOURCE))
    assert len(shape.solids().vals()) == 15
    box = shape.val().BoundingBox()
    near(box.xlen, 20.0, 2e-4)
    near(box.ylen, 34.0, 2e-4)
    near(box.zlen, 29.000000156, 2e-4)


def check_exports() -> None:
    expected = [
        "hr-v0-xc330-gripper-base-p0.1",
        "hr-v0-xc330-gripper-cover-p0.1",
        "hr-v0-xc330-gripper-pinion-p0.1",
        "hr-v0-xc330-gripper-rack-a-p0.1",
        "hr-v0-xc330-gripper-rack-b-p0.1",
        "hr-v0-xc330-gripper-left-jaw-p0.1",
        "hr-v0-xc330-gripper-right-jaw-p0.1",
        "hr-v0-xc330-gripper-left-pad-envelope-p0.1",
        "hr-v0-xc330-gripper-right-pad-envelope-p0.1",
    ]
    for stem in expected:
        step = OUT / f"{stem}.step"
        stl = OUT / f"{stem}.stl"
        assert step.read_bytes().startswith(b"ISO-10303-21")
        assert stl.is_file() and stl.stat().st_size > 100
        parsed = cq.importers.importStep(str(step))
        assert len(parsed.solids().vals()) >= 1
    for pose in ("closed", "mid", "open"):
        assert (OUT / f"hr-v0-xc330-gripper-{pose}-pose-p0.1.step").read_bytes().startswith(b"ISO-10303-21")
        assert (OUT / f"hr-v0-xc330-gripper-{pose}-pose-p0.1.glb").read_bytes().startswith(b"glTF")


def check_calculations() -> None:
    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == "HR-V0-GRIP-XC330-P0.1"
    assert summary["status"] == "PREFERRED LIGHTWEIGHT FEASIBILITY BRANCH - NOT SELECTED"
    assert summary["source_step_sha256"] == EXPECTED_SOURCE_SHA256
    assert summary["actuator_model"] == "XC330-T288-T"
    assert summary["actuator_sku"] == "902-0171-000"
    assert summary["actuator_mass_g"] == 23.0
    assert summary["hard_opening_mm"] == [40.0, 76.0]
    assert summary["nominal_padded_opening_mm"] == [38.0, 74.0]
    assert summary["required_object_dimension_mm"] == [40.0, 70.0]
    near(summary["full_travel_rotation_deg"], math.degrees(36.0 / 16.0), 1e-6)
    near(summary["screen_subtotal_g"], 692.758 - 82.0 + 23.0 + summary["custom_full_density_calculation_mass_g"], 2e-6)
    near(summary["remaining_incomplete_headroom_g"], 750.0 - summary["screen_subtotal_g"], 2e-6)
    assert summary["open_holds"] == 15 and summary["requirements_closed"] == 0 and summary["sol_blockers_closed"] == 0
    for key in ("procurement_release", "fabrication_release", "connection_release", "motion_release", "energization_release"):
        assert summary[key] is False

    samples = rows(OUT / "kinematic-samples.csv")
    assert [float(row["hard_jaw_opening_mm"]) for row in samples] == [40.0, 46.0, 52.0, 58.0, 64.0, 70.0, 76.0]
    for row in samples:
        hard = float(row["hard_jaw_opening_mm"])
        near(float(row["nominal_padded_opening_mm"]), hard - 2.0)
        near(float(row["each_rack_translation_mm"]), (hard - 40.0) / 2.0)
        near(float(row["pinion_rotation_deg"]), math.degrees((hard - 40.0) / 16.0), 1e-6)
        assert "OPEN" in row["claim_boundary"]

    forces = rows(OUT / "force-screen.csv")
    assert len(forces) == 2
    near(float(forces[0]["ideal_each_jaw_force_n"]), 11.5, 1e-3)
    near(float(forces[1]["ideal_each_jaw_force_n"]), 57.5, 1e-3)
    assert "NOT A PROJECT RATING" in forces[0]["credit"]
    assert "NO CONTINUOUS" in forces[1]["credit"]


def check_release_boundaries() -> None:
    holds = rows(OUT / "hold-register.csv")
    assert [row["hold_id"] for row in holds] == [f"XGH-{index:03d}" for index in range(1, 16)]
    assert all(row["status"] == "OPEN" for row in holds)
    assert all("NO PROCUREMENT" in row["release_effect"] for row in holds)

    bom = rows(OUT / "candidate-bom.csv")
    assert [row["item"] for row in bom] == [f"XGB-{index:03d}" for index in range(1, 7)]
    assert bom[0]["order_code"] == "902-0171-000"
    assert bom[1]["order_code"] == "903-0301-000"
    assert all("REQUIRED" in row["state"] or "NOT SELECTED" in row["state"] for row in bom)

    active_ledger = (ROOT / "bom/hr-v0-moving-mass-ledger.csv").read_text(encoding="utf-8")
    assert "XM430-W350-T gripper actuator" in active_ledger
    assert "XC330-T288-T" not in active_ledger

    guide = GUIDE.read_text(encoding="utf-8")
    for token in (
        "PRELIMINARY FEASIBILITY BRANCH",
        "NOT SELECTED",
        "font:clamp(16px",
        "font-size:14px",
        "Stall torque is not continuous torque",
        "No ordering, printing, machining, assembly, connection, powered test, motion or energization",
    ):
        assert token in guide
    assert "font-size:12px" not in guide and "font-size:11px" not in guide


def main() -> int:
    check_source()
    check_exports()
    check_calculations()
    check_release_boundaries()
    print("HR-V0 XC330 gripper feasibility P0.1 check passed: official STEP hash/15 solids, 9 native parts, 3 poses, calculations and 15 open holds verified")
    print("PRELIMINARY - NOT SELECTED - NO PROCUREMENT, FABRICATION, CONNECTION, MOTION, OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
