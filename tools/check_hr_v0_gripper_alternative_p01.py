"""Fail-closed checks for HR-V0-GRIP-ALT-P0.1.

Run with the controlled CadQuery interpreter because this checker imports both
manufacturer STEP payloads and verifies that the archived files still parse.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
POL = ROOT / "cad/vendor/pololu/micro-gripper-3551-r111"
SC = ROOT / "cad/vendor/servocity/3219-0002-0002-r111"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def near(actual: float, expected: float, tolerance: float = 1e-4) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def check_files() -> None:
    manifests = rows(POL / "source-manifest-p0.1.csv") + rows(SC / "source-manifest-p0.1.csv")
    assert [row["artifact_id"] for row in manifests] == [
        "R111-POL-001", "R111-POL-002", "R111-POL-003",
        "R111-SC-001", "R111-SC-002", "R111-SC-003", "R111-SC-004",
    ]
    paths = {
        "R111-POL-001": POL / "micro-gripper-dimensions.pdf",
        "R111-POL-002": POL / "micro-gripper.step",
        "R111-POL-003": POL / "fs90-specs.pdf",
        "R111-SC-001": SC / "3219-0002-0002-assembly-instructions.pdf",
        "R111-SC-002": SC / "3219-0002-0002-spec-sheet.pdf",
        "R111-SC-003": SC / "3219-0002-0002-step.zip",
        "R111-SC-004": SC / "step/3219-0002-0002.step",
    }
    signatures = {"PDF": b"%PDF", "STEP": b"ISO-10303-21", "ZIP": b"PK"}
    for row in manifests:
        path = paths[row["artifact_id"]]
        assert path.is_file()
        assert path.stat().st_size == int(row["size_bytes"])
        assert digest(path) == row["sha256"]
        assert path.read_bytes()[:16].startswith(signatures[row["format"]])
        assert row["access_date"] == "2026-08-08"
        assert "release" in row["release_boundary"].lower() or "open" in row["release_boundary"].lower()


def check_geometry() -> None:
    candidates = (
        (POL / "micro-gripper.step", 3, (48.3233046, 62.3000002, 36.6002866), 23009.7925),
        (SC / "step/3219-0002-0002.step", 43, (60.9235229, 132.0163877, 54.2000002), 62716.6826),
    )
    for path, solid_count, expected_box, expected_volume in candidates:
        shape = cq.importers.importStep(str(path))
        solids = shape.solids().vals()
        assert len(solids) == solid_count
        box = shape.val().BoundingBox()
        for actual, expected in zip((box.xlen, box.ylen, box.zlen), expected_box):
            near(actual, expected)
        near(sum(s.Volume() for s in solids), expected_volume)


def check_decision() -> None:
    trade = rows(ROOT / "references/gripper/hr-v0-gripper-alternative-trade-p0.1.csv")
    assert [row["candidate_id"] for row in trade] == ["GRALT-POL3551", "GRALT-SC3219", "GRALT-RMX52"]
    assert trade[0]["decision_state"] == "PREFERRED EVALUATION CANDIDATE - NOT SELECTED"
    assert all("NOT SELECTED" in row["decision_state"] or "SOURCE HELD" in row["decision_state"] for row in trade)
    assert trade[0]["catalog_mass_g"] == "30" and trade[0]["usable_opening_mm"] == "32"

    holds = rows(ROOT / "cad/hr-v0/gripper-alternative-interface-holds-p0.1.csv")
    assert [row["hold_id"] for row in holds] == [f"GAH-{i:03d}" for i in range(1, 13)]
    assert all(row["status"] == "OPEN" for row in holds)
    interfaces = rows(ROOT / "electrical/interfaces/hr-v0-feedback-servo-gripper-interface-p0.1.csv")
    assert [row["interface_id"] for row in interfaces] == [f"GSI-{i:03d}" for i in range(1, 7)]
    assert all("no " in row["release_boundary"].lower() for row in interfaces)

    doc = (ROOT / "docs/hr-v0-gripper-alternative-trade-p0.1.md").read_text(encoding="utf-8")
    for token in (
        "PREFERRED EVALUATION CANDIDATE ONLY; NOT SELECTED",
        "750 - 577.091 - 30 = 142.909 g",
        "GRIP-002",
        "E-stop release and manual reset must leave the PWM output in a nonmoving state",
        "closes no requirement",
        "energization remains prohibited",
    ):
        assert token in doc

    guide = (ROOT / "release/hr-v0/gripper-alternative-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("PRELIMINARY", "NOT SELECTED", "font:16px", "font-size:14px", "font-size:12px", "data-filter", "addEventListener"):
        assert token in guide
    assert "@media(max-width:780px)" in guide


def main() -> int:
    check_files()
    check_geometry()
    check_decision()
    print("HR-V0 gripper alternative P0.1 check passed: 7 files hash/type checked; 46 STEP solids parsed; all 12 selection holds open")
    print("PRELIMINARY - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
