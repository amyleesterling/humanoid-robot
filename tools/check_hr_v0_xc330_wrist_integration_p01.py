#!/usr/bin/env python3
"""Fail-closed verification for HR-V0-XC330-WRIST-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/xc330-wrist-integration-p0.1"
GUIDE = ROOT / "release/hr-v0/xc330-wrist-integration-p0.1/index.html"
MANIFEST = ROOT / "cad/hr-v0/generated/SOURCE-MANIFEST.csv"
H104_STEP = ROOT / "cad/vendor/robotis/FR12-H104K.stp"
H104_PDF = ROOT / "cad/vendor/robotis/FR12-H104K.pdf"
H104_STEP_HASH = "75BA58D2668D7D25802D1277A5393445C4FB7A8C565566E56CE76FEFC0E59F7D"
H104_PDF_HASH = "3FA377719C8FAA1235054D76D0913511A4EB37FBA746C60392385E40BE18E5B0"


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


def check_sources() -> None:
    assert H104_STEP.stat().st_size == 229070 and H104_STEP.read_bytes().startswith(b"ISO-10303-21")
    assert H104_PDF.stat().st_size == 72806 and H104_PDF.read_bytes().startswith(b"%PDF-")
    assert digest(H104_STEP) == H104_STEP_HASH
    assert digest(H104_PDF) == H104_PDF_HASH
    shape = cq.importers.importStep(str(H104_STEP))
    assert len(shape.solids().vals()) == 1
    box = shape.val().BoundingBox()
    for actual, expected in zip((box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax), (-20.5, 20.5, -2.5, 28.0, -11.25, 35.25)):
        near(actual, expected, 1e-5)
    near(shape.val().Volume(), 4314.613722, 1e-5)

    source_rows = rows(OUT / "source-register.csv")
    assert len(source_rows) == 4
    assert source_rows[0]["sha256"] == H104_STEP_HASH
    assert source_rows[1]["sha256"] == H104_PDF_HASH
    assert "FOR REFERENCE ONLY" in source_rows[1]["revision_date"]
    for row in source_rows:
        assert digest(ROOT / row["locator"]) == row["sha256"]


def check_transforms_and_interfaces() -> None:
    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == "HR-V0-XC330-WRIST-P0.1"
    assert summary["gripper_to_h104_translation_mm"] == [0.0, 4.0, 13.5]
    near(summary["gripper_to_h104_rx_deg"], 90.0)
    assert summary["gripper_world_translation_mm"] == [0.0, 327.6, -13.5]
    near(summary["gripper_world_rx_deg"], 270.0)
    assert summary["nominal_object_center_h104_mm"] == [0.0, -27.0, 13.5]
    assert summary["nominal_object_center_world_mm"] == [0.0, 358.6, -13.5]
    near(summary["world_y_reach_reserve_mm"], 1.4)

    transforms = rows(OUT / "transform-register.csv")
    assert [row["item"] for row in transforms] == [
        "G1 H104 frame", "XC330 gripper root", "XC330 gripper root", "nominal pad/object center", "nominal pad/object center"
    ]
    assert transforms[-1]["translation_mm"] == "(0.0,358.6,-13.5)"

    holes = rows(OUT / "hole-register.csv")
    assert len(holes) == 12
    h104 = [row for row in holes if row["interface"] == "H104 to bridge"]
    assert len(h104) == 4
    assert {(row["side"], row["y_mm"], row["z_mm"]) for row in h104} == {
        ("+X", "22.500000", "-8.000000"), ("+X", "22.500000", "8.000000"),
        ("-X", "22.500000", "-8.000000"), ("-X", "22.500000", "8.000000"),
    }
    assert all("STEP minor cylinder 1.567 mm" in row["source_feature"] for row in h104)
    pcd = [row for row in holes if row["interface"] == "S101/U-base to bridge"]
    assert len(pcd) == 8
    expected_pcd = {("17.656854", "7.843146"), ("6.343146", "7.843146"), ("17.656854", "19.156854"), ("6.343146", "19.156854")}
    assert {(row["y_mm"], row["z_mm"]) for row in pcd} == expected_pcd
    assert all(row["fastener"] == "SELECTION REQUIRED" for row in holes)


def check_parts_contacts_and_mass() -> None:
    for stem in ("hr-v0-xc330-h104-bridge-plus-p0.1", "hr-v0-xc330-h104-bridge-minus-p0.1"):
        step = OUT / f"{stem}.step"
        stl = OUT / f"{stem}.stl"
        assert step.read_bytes().startswith(b"ISO-10303-21")
        assert stl.is_file() and stl.stat().st_size > 100
        part = cq.importers.importStep(str(step))
        assert len(part.solids().vals()) == 1
        near(part.val().Volume(), 1821.576112005, 1e-5)

    for stem in ("hr-v0-xc330-wrist-integrated-mid-p0.1", "hr-v0-arm-xc330-integrated-reference-p0.1"):
        step = OUT / f"{stem}.step"
        glb = OUT / f"{stem}.glb"
        assert step.read_bytes().startswith(b"ISO-10303-21")
        assert len(cq.importers.importStep(str(step)).solids().vals()) > 10
        assert glb.read_bytes().startswith(b"glTF") and glb.stat().st_size > 1_000_000

    contacts = rows(OUT / "contact-clearance-register.csv")
    assert len(contacts) == 7
    assert all(float(row["positive_intersection_mm3"]) == 0.0 for row in contacts)
    assert all(float(row["minimum_distance_mm"]) == 0.0 for row in contacts)
    assert all("physical" in row["status"] or "received" in row["status"] for row in contacts)

    bridges = rows(OUT / "bridge-register.csv")
    assert len(bridges) == 2
    assert all(row["envelope_mm"] == "3.0 x 20.0 x 31.5" for row in bridges)
    assert all("SELECTION REQUIRED" in row["material_process"] for row in bridges)

    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    near(summary["bridge_pair_mass_screen_g"], 9.836511)
    near(summary["screen_subtotal_g"], 688.961224)
    near(summary["remaining_incomplete_headroom_g"], 61.038776)
    active = (ROOT / "bom/hr-v0-moving-mass-ledger.csv").read_text(encoding="utf-8")
    assert "XM430-W350-T gripper actuator" in active and "XC330-T288-T" not in active


def check_collision_and_boundaries() -> None:
    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    screen = summary["collision_screen"]
    assert screen["samples"] == 399 and screen["increment_deg"] == 5.0
    assert screen["j1_limits_deg"] == [-20.0, 70.0] and screen["j2_limits_deg"] == [15.0, 115.0]
    assert screen["collision_samples"] == 0 and screen["maximum_positive_intersection_mm3"] == 0.0
    sweep = rows(OUT / "collision-sweep.csv")
    assert len(sweep) == 399
    assert (sweep[0]["j1_deg"], sweep[0]["j2_internal_deg"]) == ("-20.0", "15.0")
    assert (sweep[-1]["j1_deg"], sweep[-1]["j2_internal_deg"]) == ("70.0", "115.0")
    assert all(row["result"] == "PASS_NOMINAL_SAMPLE" for row in sweep)
    assert all("5 degree samples only" in row["scope"] for row in sweep)

    assert summary["open_holds"] == 18
    assert summary["requirements_closed"] == summary["energization_gates_closed"] == summary["sol_blockers_closed"] == 0
    for key in ("procurement_release", "fabrication_release", "assembly_release", "connection_release", "motion_release", "energization_release"):
        assert summary[key] is False
    holds = rows(OUT / "hold-register.csv")
    assert [row["hold_id"] for row in holds] == [f"WRI-H{index:02d}" for index in range(1, 19)]
    assert all(row["status"] == "OPEN" and "NO PROCUREMENT" in row["release_effect"] for row in holds)

    guide = GUIDE.read_text(encoding="utf-8")
    for token in (
        "PRELIMINARY WRIST-INTEGRATION CANDIDATE", "NOT SELECTED", "font:16px/1.55", "font-size:14px",
        "0 / 399", "at 5 deg increments", "This is not continuous or as-built proof",
        "hr-v0-xc330-wrist-integrated-mid-p0.1.glb", "hr-v0-arm-xc330-integrated-reference-p0.1.glb",
    ):
        assert token in guide
    assert "font-size:12px" not in guide and "font-size:11px" not in guide


def check_manifest() -> None:
    manifest = {row["file"]: row for row in rows(MANIFEST)}
    for path in OUT.iterdir():
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT / "cad/hr-v0/generated").as_posix()
        assert rel in manifest, rel
        assert manifest[rel]["sha256"] == digest(path)
        assert "NOT RELEASED FOR FABRICATION OR ENERGIZATION" in manifest[rel]["status"]


def main() -> int:
    check_sources()
    check_transforms_and_interfaces()
    check_parts_contacts_and_mass()
    check_collision_and_boundaries()
    check_manifest()
    print("HR-V0 XC330 wrist integration P0.1 check passed: exact H104 source, transform chain, 2 bridge parts, 7 nominal contacts, 399 sampled poses, calculations and 18 open holds verified")
    print("PRELIMINARY - NOT SELECTED - NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
