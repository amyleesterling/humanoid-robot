"""Fail-closed checks for HR-V0-GRIP-SRC-P0.3.

Run with the controlled CadQuery interpreter because this checker imports the
manufacturer STEP payloads and confirms their solid geometry.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "cad/vendor/robotis/fr12-g101gm-r109"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def close(actual: float, expected: float, tolerance: float = 1e-5) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected, tolerance)


def main() -> int:
    manifest = csv_rows(SRC / "source-manifest-p0.1.csv")
    assert [row["artifact_id"] for row in manifest] == [f"R109-SRC-{i:03d}" for i in range(1, 7)]
    assert {(row["part"], row["format"]) for row in manifest} == {
        (part, fmt) for part in ("FR12-E170", "FR12-E171") for fmt in ("DWG", "PDF", "STEP")
    }
    assert all(row["manufacturer"] == "ROBOTIS" for row in manifest)
    assert all(row["access_date"] == "2026-08-08" for row in manifest)
    assert all(row["document_date"] == "2017-08-31" for row in manifest)
    assert all("emanual.robotis.com" in row["source_page"] for row in manifest)
    assert {row["manufacturer_download_endpoint"].rsplit("=", 1)[-1] for row in manifest} == {
        str(i) for i in range(637, 643)
    }
    assert all("reference" in row["release_boundary"].lower() for row in manifest)

    for row in manifest:
        suffix = {"DWG": ".dwg", "PDF": ".pdf", "STEP": ".stp"}[row["format"]]
        path = SRC / f"{row['part'].lower()}{suffix}"
        assert path.is_file()
        assert path.stat().st_size == int(row["size_bytes"])
        assert sha256(path) == row["sha256"]
        head = path.read_bytes()[:32]
        if row["format"] == "DWG":
            assert head.startswith(b"AC1015")
        elif row["format"] == "PDF":
            assert head.startswith(b"%PDF-1.6")
        else:
            assert head.startswith(b"ISO-10303-21;")
        assert not head.lstrip().lower().startswith((b"<!doctype", b"<html"))

    expected = {
        "FR12-E170": ([37.0, 14.0000001, 87.74066664678702], 5837.452710497621, [0.0, 1.4223454102726845, 23.787577988684202]),
        "FR12-E171": ([54.0, 47.99871130598771, 94.8482238596511], 8322.633439822826, [-0.0002553572609793037, 12.217384282522406, 38.10664277471259]),
    }
    geometry = {row["part"]: row for row in csv_rows(SRC / "geometry-summary-p0.1.csv")}
    assert set(geometry) == set(expected)
    for part, (expected_bbox, expected_volume, expected_center) in expected.items():
        shape = cq.importers.importStep(str(SRC / f"{part.lower()}.stp"))
        solids = shape.solids().vals()
        assert len(solids) == 1 == int(geometry[part]["solid_count"])
        box = shape.val().BoundingBox()
        center = shape.val().Center()
        for actual, target in zip((box.xlen, box.ylen, box.zlen), expected_bbox):
            close(actual, target)
        close(sum(solid.Volume() for solid in solids), expected_volume)
        for actual, target in zip((center.x, center.y, center.z), expected_center):
            close(actual, target)
        assert "not an assembly transform" in geometry[part]["release_boundary"]

    for step_name in ("fr12-e170.stp", "fr12-e171.stp"):
        header = (SRC / step_name).read_text(encoding="ascii", errors="ignore")[:500]
        assert "2017-08-31T" in header
        assert "PRO/ENGINEER" in header
        assert "CONFIG_CONTROL_DESIGN" in header

    doc = (ROOT / "docs/hr-v0-gripper-frame-source-correction-p0.3.md").read_text(encoding="utf-8")
    for token in (
        WARNING,
        "FOR REFERENCE ONLY",
        "GRH-001",
        "GRH-002",
        "REJECTED AS THE SOLE COMPLETE MECHANISM SOURCE",
        "closes no energization gate",
    ):
        assert token in doc

    guide = (ROOT / "release/hr-v0/gripper-frame-source-p0.3/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "FR12-E170", "FR12-E171", "FOR REFERENCE ONLY", "GRH-001", "GRH-002"):
        assert token in guide
    assert "font-size:16px" in guide
    assert "font-size:14px" in guide
    assert "font-size:12px" in guide
    assert "data-part" in guide and "addEventListener" in guide

    print("HR-V0 gripper source P0.3 check passed: six manufacturer payloads hash/type checked; two STEP solids parsed")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
