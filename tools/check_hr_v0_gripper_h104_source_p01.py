"""Fail-closed checks for HR-V0-GRIP-H104-SRC-P0.1."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "cad/vendor/robotis/fr12-h104k-r115"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
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
    manifest = rows(SRC / "source-manifest-p0.1.csv")
    assert [row["artifact_id"] for row in manifest] == ["R115-SRC-001", "R115-SRC-002", "R115-SRC-003"]
    assert [row["format"] for row in manifest] == ["DWG", "PDF", "STEP"]
    assert all(row["manufacturer"] == "ROBOTIS" for row in manifest)
    assert all(row["access_date"] == "2026-08-08" for row in manifest)
    assert all(row["document_date"] == "2017-08-31" for row in manifest)
    assert [row["manufacturer_download_endpoint"].rsplit("=", 1)[-1] for row in manifest] == ["646", "647", "648"]
    assert all("emanual.robotis.com" in row["source_page"] for row in manifest)

    expected_heads = {"DWG": b"AC1015", "PDF": b"%PDF", "STEP": b"ISO-10303-21;"}
    for row in manifest:
        path = (SRC / row["payload_path"]).resolve()
        assert path.is_file()
        assert path.stat().st_size == int(row["size_bytes"])
        assert sha256(path) == row["sha256"]
        assert path.read_bytes().startswith(expected_heads[row["format"]])
        assert not path.read_bytes()[:64].lstrip().lower().startswith((b"<!doctype", b"<html"))

    step = (SRC / "../FR12-H104K.stp").resolve()
    shape = cq.importers.importStep(str(step))
    solids = shape.solids().vals()
    assert len(solids) == 1
    box = shape.val().BoundingBox()
    center = shape.val().Center()
    for actual, expected in zip((box.xlen, box.ylen, box.zlen), (41.000000100, 30.500000261, 46.500000015)):
        close(actual, expected)
    close(sum(solid.Volume() for solid in solids), 4314.613722204)
    for actual, expected in zip((center.x, center.y, center.z), (0.000000085, 22.276497270, 8.999152628)):
        close(actual, expected)

    geometry = rows(SRC / "geometry-summary-p0.1.csv")
    assert len(geometry) == 1
    assert geometry[0]["source_sha256"] == sha256(step)
    assert "not an H104-to-gripper-carrier assembly transform" in geometry[0]["release_boundary"]

    dispositions = rows(ROOT / "cad/hr-v0/gripper-h104-source-disposition-p0.1.csv")
    assert [row["control_id"] for row in dispositions] == [f"HSD-{i:03d}" for i in range(1, 8)]
    assert [row["status"] for row in dispositions].count("OPEN") == 3
    assert [row["status"] for row in dispositions].count("PARTIAL") == 4
    assert not any(row["status"] in {"CLOSED", "RELEASED", "PASS"} for row in dispositions)

    doc = (ROOT / "docs/hr-v0-gripper-h104-source-correction-p0.1.md").read_text(encoding="utf-8")
    for token in (WARNING, "FOR REFERENCE ONLY", "GDC-001", "GDC-007", "GRH-001", "GRH-002", "closes no requirement"):
        assert token in doc

    guide = (ROOT / "release/hr-v0/gripper-h104-source-p0.1/index.html").read_text(encoding="utf-8")
    for token in (WARNING, "Endpoint 646", "Endpoint 647", "Endpoint 648", "GDC-001..007", "GRH-001/002"):
        assert token in guide
    assert "font:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide
    assert "data-filter" in guide and "addEventListener" in guide

    print("HR-V0 H104 source P0.1 check passed: official three-file provenance controlled; STEP solid parsed")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
