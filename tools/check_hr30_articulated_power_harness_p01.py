#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 articulated power-harness package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "articulated-power-harness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
WARNING = "PRELIMINARY - ARTICULATED ACTUATOR-POWER HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(base: Path) -> None:
    with (base / "file-manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    actual = sorted(p.name for p in base.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    assert sorted(r["path"] for r in manifest) == actual
    for row in manifest:
        path = base / row["path"]
        assert int(row["bytes"]) == path.stat().st_size
        assert row["sha256"] == sha(path)
        assert row["warning"] == WARNING


def main() -> int:
    boards = rows("tap-board-register.csv")
    crossings = rows("joint-crossing-register.csv")
    guards = rows("guard-solid-register.csv")
    cable = rows("cable-selection-register.csv")
    sources = rows("primary-source-register.csv")
    holds = rows("open-holds.csv")
    assert len(boards) == 25
    assert len({r["axis_id"] for r in boards}) == 25
    assert len(crossings) == 45
    assert len({r["cable_piece_id"] for r in crossings}) == 45
    assert {r["joint_axis"] for r in crossings} == {r["axis_id"] for r in boards}
    assert len(guards) == 50
    assert len({r["guard_id"] for r in guards}) == 50
    assert all(sum(r["axis_id"] == axis for r in guards) == 2 for axis in {r["axis_id"] for r in boards})
    assert len(cable) == 1 and cable[0]["candidate_part"] == "969M101-22-4-MC"
    assert abs(float(cable[0]["continuous_flex_radius_mm"]) - 27.94) < 1e-6
    assert len(sources) == 7 and len(holds) == 11
    for dataset in [boards, crossings, guards, cable, sources, holds]:
        assert all(r["warning"] == WARNING for r in dataset)
        assert all("NO PROCUREMENT" in r["authority"] for r in dataset)
    assert all(r["catalog_current_screen"].startswith("PASS CATALOG NUMBER ONLY") for r in crossings)
    assert all(float(r["maximum_hr30_channel_cap_a"]) <= 2.5 for r in crossings)
    assert all(int(r["parallel_piece_count"]) <= 3 for r in crossings)
    assert all(r["joint_spanning"].startswith("NO") for r in guards if r["guard_type"].startswith("RIGID"))
    assert all(r["joint_spanning"].startswith("YES - FLEXIBLE ONLY") for r in guards if r["guard_type"].startswith("FLEXIBLE"))

    status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
    assert status["whole_limb_rigid_guard_rejected"] is True
    assert status["axis_count"] == 25 and status["flat_cable_piece_count"] == 45
    assert status["guard_solid_record_count"] == 50
    for key in [
        "full_pose_collision_complete", "full_range_flex_complete", "termination_complete",
        "thermal_derating_complete", "physical_validation_complete", "procurement_authority",
        "fabrication_authority", "connection_authority", "powered_test_authority",
        "motion_authority", "energization_authority",
    ]:
        assert status[key] is False
    assert WARNING in (OUT / "README.md").read_text(encoding="utf-8")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert WARNING in page and "font-size:16px" in page and "font:17px" in page
    for name in [
        "HR-30_articulated_power_harness_candidate.step",
        "HR-30_articulated_power_harness_candidate.glb",
        "HR-30_whole_body_articulated_power_harness_candidate.glb",
        "articulated-power-harness-preview.png",
    ]:
        assert (OUT / name).stat().st_size > 100_000
    check_manifest(OUT)
    check_manifest(RELEASE)
    assert sorted(p.name for p in OUT.iterdir()) == sorted(p.name for p in RELEASE.iterdir())
    assert all(sha(p) == sha(RELEASE / p.name) for p in OUT.iterdir() if p.is_file())
    for parent in [WHOLE / "README.md", WHOLE / "index.html", WHOLE / "harness" / "README.md", WHOLE / "harness" / "index.html"]:
        assert "HR30-ARTICULATED-POWER-HARNESS-P01-START" in parent.read_text(encoding="utf-8")
    print("PASS: 25 tap boards, 45 joint cable pieces, 50 separate rigid/flexible guard records; all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
