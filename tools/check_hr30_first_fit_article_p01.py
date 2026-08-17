"""Fail-closed checker for the HR-30 G01 first-fit article P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "first-fit-article-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
WARNING = (
    "PRELIMINARY - UNPOWERED NONSTRUCTURAL MANUAL FIT ARTICLE ONLY - "
    "NOT APPROVED FOR PRODUCTION FABRICATION, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def check_manifest(root: Path) -> None:
    manifest = rows(root / "file-manifest.csv")
    actual = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    listed = sorted(row["path"] for row in manifest)
    assert listed == actual, f"manifest file set mismatch: {root}"
    for row in manifest:
        path = root / row["path"]
        assert int(row["bytes"]) == path.stat().st_size
        assert row["sha256"] == sha256(path)
        assert row["warning"] == WARNING


def binary_stl_triangle_count(path: Path) -> int:
    data = path.read_bytes()
    assert len(data) >= 84, f"short STL {path}"
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * count, f"non-binary/malformed STL {path}"
    assert count > 0
    return count


def main() -> int:
    assert OUT.is_dir() and RELEASE.is_dir()
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    assert source_files == release_files
    for relative in source_files:
        assert sha256(OUT / relative) == sha256(RELEASE / relative), relative

    check_manifest(OUT)
    check_manifest(RELEASE)
    assert (OUT / "first-fit-article-source.py").read_bytes() == (ROOT / "tools/generate_hr30_first_fit_article_p01.py").read_bytes()

    status = json.loads((OUT / "fit-article-status.json").read_text(encoding="utf-8"))
    assert status["identifier"] == "HR30-G01-FIRST-FIT-ARTICLE-P0.1"
    assert status["warning"] == WARNING
    assert status["printable_part_count"] == 11
    assert status["combined_plate_present"] is True
    assert status["combined_plate_bbox_mm"][0] <= 220.0
    assert status["combined_plate_bbox_mm"][1] <= 220.0
    assert status["clearance_coupon_present"] is True
    assert status["closed_cad_gap_mm"] == 8.0
    assert status["open_cad_gap_mm"] == 34.0
    assert status["manual_cycle_target"] == 50
    assert status["cad_fit_screen_count"] == 18
    assert status["cad_fit_screen_pass_count"] == 18
    assert status["built_part_count"] == 0
    assert status["physical_measurement_count"] == 0
    assert status["manual_cycle_count"] == 0
    for key in ("production_interchangeable", "actuator_installation_permitted", "structural_credit", "grasp_credit", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False, key

    parts = rows(OUT / "fit-article-part-register.csv")
    assert len(parts) == 11 and len({row["part_id"] for row in parts}) == 11
    assert all(row["built_quantity"] == "0" and row["production_interchangeable"] == "NO" for row in parts)
    assert len(rows(OUT / "fit-article-hardware-register.csv")) == 5
    assert len(rows(OUT / "fit-article-build-traveler.csv")) == 12
    assert len(rows(OUT / "fit-article-inspection-register.csv")) == 12
    assert len(rows(OUT / "fit-article-issue-register.csv")) == 8
    assert len(rows(OUT / "open-holds.csv")) == 5
    assert len(rows(OUT / "plate-placement-register.csv")) == 11
    assert len(rows(OUT / "source-binding.csv")) == 7
    for row in rows(OUT / "source-binding.csv"):
        source = ROOT / row["path"]
        assert source.is_file() and source.stat().st_size == int(row["bytes"])
        assert sha256(source) == row["sha256"]

    screens = rows(OUT / "fit-screen-register.csv")
    assert len(screens) == 18
    assert {row["state"] for row in screens} == {"CLOSED", "OPEN"}
    for row in screens:
        assert row["result"] == "PASS - CAD GEOMETRY ONLY"
        assert float(row["solid_interference_volume_mm3"]) <= 1e-6
        assert row["physical_credit"] == "NONE"
    guide_rows = [row for row in screens if "GUIDE" in row["screen"]]
    assert len(guide_rows) == 8 and all(float(row["minimum_solid_distance_mm"]) >= 0.174 for row in guide_rows)
    stop_rows = [row for row in screens if "STOP" in row["screen"]]
    assert len(stop_rows) == 4
    assert all(float(row["minimum_solid_distance_mm"]) <= 0.01 for row in stop_rows if row["state"] == "OPEN")
    assert all(float(row["minimum_solid_distance_mm"]) >= 12.0 for row in stop_rows if row["state"] == "CLOSED")

    states = rows(OUT / "kinematic-state-register.csv")
    assert [(row["state"], float(row["measured_cad_gap_mm"])) for row in states] == [("CLOSED", 8.0), ("OPEN", 34.0)]
    assert all(row["physical_result"] == "NOT EXECUTED" for row in states)

    for state in ("closed", "open"):
        step = OUT / f"HR30_G01_manual_fit_article_{state}_candidate.step"
        glb = OUT / f"HR30_G01_manual_fit_article_{state}_candidate.glb"
        imported = cq.importers.importStep(str(step)).val()
        assert imported.isValid() and len(imported.Solids()) == 11
        assert glb.read_bytes()[:4] == b"glTF"
    stls = sorted((OUT / "stl").glob("*.stl"))
    assert len(stls) == 11
    assert all(binary_stl_triangle_count(path) > 0 for path in stls)
    assert binary_stl_triangle_count(OUT / "HR30_G01_manual_fit_article_plate_candidate.stl") > sum(binary_stl_triangle_count(path) for path in stls) * 0.95
    assert binary_stl_triangle_count(OUT / "FFA_clearance_coupon.stl") > 0

    bundle = OUT / "HR30-G01-first-fit-article-p0.1.zip"
    assert sha256(bundle) == status["bundle_sha256"] and bundle.stat().st_size == status["bundle_bytes"]
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        assert "HR30_G01_manual_fit_article_plate_candidate.stl" in names
        assert "FFA_clearance_coupon.stl" in names
        assert len([name for name in names if name.startswith("stl/") and name.endswith(".stl")]) == 11

    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "The first hand now assembles and moves by hand." in page
    assert "0 built" in page and "Checkboxes are a browser convenience only" in page
    assert "HR30_G01_manual_fit_article_open_candidate.glb" in page
    for size in (int(value) for value in re.findall(r"font-size:\s*(\d+)px", page)):
        assert size >= 12, f"undersized web text: {size}px"
    assert "G01 first manual fit article" in (ROOT / "index.html").read_text(encoding="utf-8")
    assert "HR30-FIRST-FIT-ARTICLE-P01-START" in (WB / "README.md").read_text(encoding="utf-8")
    package_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    assert package_status["first_fit_article_present"] is True
    assert package_status["first_fit_article_part_count"] == 11
    assert package_status["first_fit_article_physical_parts_built"] == 0
    assert package_status["first_fit_article_energization_authority"] is False

    print("PASS: 11-part G01 manual fit article, 18 CAD fit screens, 8/34 mm states, one <=220 mm plate, zero physical execution or authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
