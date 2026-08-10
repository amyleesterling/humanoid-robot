#!/usr/bin/env python3
"""Fail-closed verification for HR-V0-GRIP-XC330-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "cad/vendor/robotis/xc330"
OUT = ROOT / "cad/hr-v0/generated/xc330-gripper-interface-p0.2"
GUIDE = ROOT / "release/hr-v0/xc330-gripper-interface-p0.2/index.html"
GENERATED_MANIFEST = ROOT / "cad/hr-v0/generated/SOURCE-MANIFEST.csv"

SOURCES = {
    "XL-XC-330-official-source.stp": (
        791238,
        "E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6",
        b"ISO-10303-21",
    ),
    "XL-XC-330-official-drawing.pdf": (
        149731,
        "948B707CB26A64501C03FC45B1A9557B69A554DD5D6934F02E8E6F86CF2B46C2",
        b"%PDF-",
    ),
    "FPX330-S101-official-source.step": (
        933875,
        "4FFEE845A49FADF7B91862EBECEE8DEBFE3801E7213F35BEBC3D9007CC25300E",
        b"ISO-10303-21",
    ),
    "FPX330-S101-official-drawing.pdf": (
        86902,
        "177C5F3EA6803CD1F68DC1342C5BA6F687E3580EEB8C8D90F53B523E1606C357",
        b"%PDF-",
    ),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def near(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def check_sources() -> tuple[cq.Workplane, cq.Workplane]:
    for filename, (size, expected_hash, magic) in SOURCES.items():
        path = VENDOR / filename
        assert path.is_file() and path.stat().st_size == size, filename
        assert path.read_bytes().startswith(magic), filename
        assert digest(path) == expected_hash, filename

    manifest = rows(VENDOR / "source-manifest-p0.1.csv")
    assert len(manifest) == 4
    by_file = {row["retrieval_path"]: row for row in manifest}
    assert set(by_file) == set(SOURCES)
    for filename, (_, expected_hash, _) in SOURCES.items():
        assert by_file[filename]["sha256"] == expected_hash
        assert by_file[filename]["access_date"] == "2026-08-10"
        assert "NO FABRICATION OR ENERGIZATION RELEASE" in by_file[filename]["release_boundary"]

    actuator = cq.importers.importStep(str(VENDOR / "XL-XC-330-official-source.stp"))
    frame = cq.importers.importStep(str(VENDOR / "FPX330-S101-official-source.step"))
    assert len(actuator.solids().vals()) == 15
    assert len(frame.solids().vals()) == 1
    actuator_box = actuator.val().BoundingBox()
    frame_box = frame.val().BoundingBox()
    near(actuator_box.xlen, 20.0, 4e-4)
    near(actuator_box.ylen, 34.0, 4e-4)
    near(actuator_box.zlen, 29.000000156, 4e-4)
    near(frame_box.xlen, 34.0, 2e-6)
    near(frame_box.ylen, 7.0, 2e-6)
    near(frame_box.zlen, 28.600000001, 2e-6)
    near(frame.val().Volume(), 1747.950519978, 2e-6)
    return actuator, frame


def check_registration(actuator: cq.Workplane, frame: cq.Workplane) -> None:
    raw = frame.val()
    plus = raw.rotate((0, 0, 0), (1, 1, 0), 180).translate((10.0, -7.5, -8.0))
    minus = raw.rotate((0, 0, 0), (0, 0, 1), 90).translate((-10.0, -7.5, -8.0))
    near(actuator.val().intersect(plus).Volume(), 0.0, 1e-8)
    near(actuator.val().intersect(minus).Volume(), 0.0, 1e-8)
    near(plus.intersect(minus).Volume(), 0.0, 1e-8)

    transforms = rows(OUT / "transform-register.csv")
    assert [row["item"] for row in transforms] == ["FPX330-S101 +X", "FPX330-S101 -X"]
    assert all(float(row["maximum_axis_residual_mm"]) == 0.0 for row in transforms)
    assert all(float(row["positive_volume_intersection_mm3"]) == 0.0 for row in transforms)
    assert transforms[0]["translation_mm"] == "(10.0,-7.5,-8.0)"
    assert transforms[1]["translation_mm"] == "(-10.0,-7.5,-8.0)"

    holes = rows(OUT / "hole-register.csv")
    frame_rows = [row for row in holes if row["interface"] == "S101 flange to XC330 body"]
    assert len(frame_rows) == 4
    expected = {
        ("+X", "8.000000", "-22.500000"),
        ("+X", "8.000000", "7.500000"),
        ("-X", "-8.000000", "-22.500000"),
        ("-X", "-8.000000", "7.500000"),
    }
    assert {(row["side"], row["x_mm"], row["y_mm"]) for row in frame_rows} == expected
    assert all("PHS M2x8 TAP" in row["use"] for row in frame_rows)


def check_exports() -> None:
    stems = [
        "hr-v0-xc330-gripper-u-base-p0.2",
        "hr-v0-xc330-gripper-cover-p0.2",
        "hr-v0-xc330-gripper-involute-pinion-p0.2",
        "hr-v0-xc330-gripper-left-rack-jaw-p0.2",
        "hr-v0-xc330-gripper-right-rack-jaw-p0.2",
        "hr-v0-xc330-gripper-left-pad-envelope-p0.2",
        "hr-v0-xc330-gripper-right-pad-envelope-p0.2",
    ]
    for stem in stems:
        step = OUT / f"{stem}.step"
        stl = OUT / f"{stem}.stl"
        assert step.read_bytes().startswith(b"ISO-10303-21")
        assert stl.is_file() and stl.stat().st_size > 100
        assert len(cq.importers.importStep(str(step)).solids().vals()) >= 1

    for pose in ("closed", "mid", "open"):
        step = OUT / f"hr-v0-xc330-gripper-interface-{pose}-pose-p0.2.step"
        glb = OUT / f"hr-v0-xc330-gripper-interface-{pose}-pose-p0.2.glb"
        assert step.read_bytes().startswith(b"ISO-10303-21")
        assert len(cq.importers.importStep(str(step)).solids().vals()) >= 10
        assert glb.read_bytes().startswith(b"glTF") and glb.stat().st_size > 1_000_000


def check_geometry_and_calculations() -> None:
    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == "HR-V0-GRIP-XC330-P0.2"
    assert summary["status"] == "PREFERRED SOURCE-BOUND FEASIBILITY BRANCH - NOT SELECTED"
    assert summary["actuator_solids"] == 15 and summary["frame_solids"] == 1
    assert summary["frame_bounds_mm"] == [34.0, 7.0, 28.600000001]
    near(summary["frame_axis_residual_mm"], 0.0)
    near(summary["frame_actuator_intersection_mm3"], 0.0)

    gear = rows(OUT / "gear-register.csv")
    assert len(gear) == 1
    gear = gear[0]
    near(float(gear["module_mm"]), 0.8)
    assert int(gear["teeth"]) == 20
    near(float(gear["pressure_angle_deg"]), 20.0)
    near(float(gear["pitch_radius_mm"]), 8.0)
    near(float(gear["base_radius_mm"]), 8.0 * math.cos(math.radians(20.0)), 1e-9)
    near(float(gear["outside_radius_mm"]), 8.8)
    near(float(gear["root_radius_mm"]), 7.0)
    near(float(gear["pair_backlash_candidate_mm"]), 0.15)
    minimum_teeth = 2.0 / math.sin(math.radians(20.0)) ** 2
    near(float(gear["minimum_full_depth_no_undercut_teeth"]), minimum_teeth, 1e-6)
    assert 20 > minimum_teeth
    assert gear["working_flank"] == "exact involute equation"
    assert "SELECTION REQUIRED" in gear["root_process"]

    samples = rows(OUT / "kinematic-samples.csv")
    assert [row["pose"] for row in samples] == ["closed", "mid", "open"]
    assert [float(row["hard_opening_mm"]) for row in samples] == [40.0, 58.0, 76.0]
    assert [float(row["padded_opening_mm"]) for row in samples] == [38.0, 56.0, 74.0]
    for row in samples:
        opening = float(row["hard_opening_mm"])
        displacement = (opening - 40.0) / 2.0
        near(float(row["each_rack_displacement_from_closed_mm"]), displacement)
        near(float(row["pinion_rotation_from_closed_deg"]), math.degrees(displacement / 8.0), 1e-6)

    near(summary["custom_full_density_calculation_mass_g"], 45.366713)
    near(summary["screen_subtotal_g"], 692.758 - 82.0 + 23.0 + 45.366713)
    near(summary["remaining_incomplete_headroom_g"], 750.0 - summary["screen_subtotal_g"])
    for exclusion in ("two FPX330-S101 frames", "all screws/nuts/washers", "cable", "bellows/guard", "print/process variation"):
        assert exclusion in summary["excluded_mass"]

    clearances = {row["screen"]: row for row in rows(OUT / "clearance-screen.csv")}
    for key in (
        "official +X frame vs official actuator",
        "official -X frame vs official actuator",
        "official frames mutually",
        "official actuator vs custom base",
        "S101 frames vs U-base",
    ):
        assert clearances[key]["value_mm_or_mm3"] == "0.000000000 mm3"
    assert clearances["hub radial clearance in base"]["value_mm_or_mm3"] == "0.400000 mm diametral"
    assert clearances["rack lateral guide clearance"]["value_mm_or_mm3"] == "0.300000 mm per constrained side"
    assert clearances["rack vertical cover clearance"]["value_mm_or_mm3"] == "0.500000 mm"


def check_release_boundaries() -> None:
    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    assert summary["open_holds"] == 16
    assert summary["requirements_closed"] == 0
    assert summary["energization_gates_closed"] == 0
    assert summary["sol_blockers_closed"] == 0
    for key in (
        "procurement_release",
        "fabrication_release",
        "assembly_release",
        "connection_release",
        "motion_release",
        "energization_release",
    ):
        assert summary[key] is False

    holds = rows(OUT / "hold-register.csv")
    assert [row["hold_id"] for row in holds] == [f"XG2-H{index:02d}" for index in range(1, 17)]
    assert all(row["status"] == "OPEN" for row in holds)
    assert all("NO PROCUREMENT" in row["release_effect"] for row in holds)

    controls = rows(OUT / "manufacturer-control-register.csv")
    controls_text = "\n".join(row["control"] for row in controls)
    assert "PHS M2x8 TAP" in controls_text and "PHS M2x6 TAP" in controls_text
    assert any("FOR REFERENCE ONLY" in row["status"] for row in controls)

    bom = rows(OUT / "candidate-bom.csv")
    assert bom[0]["order_code"] == "902-0171-000"
    assert bom[1]["order_code"] == "903-0301-000"
    assert all("REQUIRED" in row["state"] or "NOT SELECTED" in row["state"] for row in bom)

    active_ledger = (ROOT / "bom/hr-v0-moving-mass-ledger.csv").read_text(encoding="utf-8")
    assert "XM430-W350-T gripper actuator" in active_ledger
    assert "XC330-T288-T" not in active_ledger

    guide = GUIDE.read_text(encoding="utf-8")
    for token in (
        "PRELIMINARY INTERFACE CANDIDATE",
        "NOT SELECTED",
        "font:16px/1.55",
        "font-size:14px",
        "Exact frame. Exact horn pattern. Real involute teeth.",
        "What this does not prove",
        "No person may place a hand in the mechanism",
        "hr-v0-xc330-gripper-interface-mid-pose-p0.2.glb",
    ):
        assert token in guide
    assert "font-size:12px" not in guide and "font-size:11px" not in guide


def check_generated_manifest() -> None:
    manifest = rows(GENERATED_MANIFEST)
    by_name = {row["file"]: row for row in manifest}
    output_files = [path for path in OUT.iterdir() if path.is_file()]
    for path in output_files:
        rel = path.relative_to(ROOT / "cad/hr-v0/generated").as_posix()
        assert rel in by_name, rel
        assert by_name[rel]["sha256"] == digest(path)
        assert "NOT RELEASED FOR FABRICATION OR ENERGIZATION" in by_name[rel]["status"]


def main() -> int:
    actuator, frame = check_sources()
    check_registration(actuator, frame)
    check_exports()
    check_geometry_and_calculations()
    check_release_boundaries()
    check_generated_manifest()
    print("HR-V0 XC330 gripper interface P0.2 check passed: 4 official source hashes, exact two-frame registration, 7 native parts, 3 poses, involute geometry, calculations and 16 open holds verified")
    print("PRELIMINARY - NOT SELECTED - NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
