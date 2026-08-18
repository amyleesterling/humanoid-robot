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
    branches = rows("direct-branch-register.csv")
    transitions = rows("fixed-transition-register.csv")
    crossings = rows("joint-crossing-register.csv")
    guards = rows("guard-solid-register.csv")
    cable = rows("cable-selection-register.csv")
    dispositions = rows("architecture-disposition-register.csv")
    sources = rows("primary-source-register.csv")
    holds = rows("open-holds.csv")
    assert len(branches) == 25
    axes = {r["axis_id"] for r in branches}
    assert len(axes) == 25
    assert len(transitions) == 25 and {r["axis_id"] for r in transitions} == axes
    assert len(crossings) == 76
    assert len({r["crossing_id"] for r in crossings}) == 76
    assert {r["destination_axis"] for r in crossings} == axes
    assert {r["joint_axis"] for r in crossings} == axes
    by_branch = {r["branch_cable_id"]: 0 for r in branches}
    for crossing in crossings:
        by_branch[crossing["branch_cable_id"]] += 1
    assert sorted(by_branch.values()) == sorted(int(r["upstream_joint_crossings"]) for r in branches)
    assert sum(by_branch.values()) == 76
    assert all(int(r["electrical_splices_between_protection_and_transition"]) == 0 for r in branches)
    assert len(guards) == 50
    assert len({r["guard_id"] for r in guards}) == 50
    assert all(sum(r["axis_id"] == axis for r in guards) == 2 for axis in axes)
    assert len(cable) == 1 and cable[0]["candidate_part"] == "CF130.03.02.UL"
    assert abs(float(cable[0]["outer_diameter_max_mm"]) - 5.0) < 1e-6
    assert abs(float(cable[0]["continuous_flex_radius_mm"]) - 37.5) < 1e-6
    assert len(dispositions) == 3
    active = [r for r in dispositions if r["disposition"] == "ACTIVE P0.1 CONSTRUCTION CANDIDATE"]
    rejected = [r for r in dispositions if r["disposition"].startswith("REJECTED")]
    assert len(active) == 1 and "DIRECT" in active[0]["architecture"]
    assert len(rejected) == 2 and any("TAP BOARDS" in r["architecture"] for r in rejected)
    assert len(sources) == 11 and len(holds) == 13
    for dataset in [branches, transitions, crossings, guards, cable, dispositions, sources, holds]:
        assert all(r["warning"] == WARNING for r in dataset)
        assert all("NO PROCUREMENT" in r["authority"] for r in dataset)
    assert all(float(r["maximum_hr30_channel_cap_a"]) <= 2.5 for r in crossings)
    assert all(r["application_ampacity_state"].startswith("UNVERIFIED") for r in crossings)
    assert all(int(r["parallel_pair_count"]) <= 6 for r in crossings)
    assert all(r["joint_spanning"].startswith("NO") for r in guards if r["guard_type"].startswith("RIGID"))
    assert all(r["joint_spanning"].startswith("YES - FLEXIBLE ONLY") for r in guards if r["guard_type"].startswith("FLEXIBLE"))

    status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
    assert status["whole_limb_rigid_guard_rejected"] is True
    assert status["tap_board_cascade_selected"] is False and status["tap_board_count"] == 0
    assert status["direct_branch_architecture_selected"] is True
    assert status["axis_count"] == 25 and status["direct_branch_count"] == 25
    assert status["joint_crossing_segment_count"] == 76 and status["fixed_transition_count"] == 25
    assert status["guard_solid_record_count"] == 50
    assert status["application_ampacity_released"] is False
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
    assert "76 explicit crossing segments" in page and "tap-board cascade is rejected" in page
    assert not (OUT / "tap-board-register.csv").exists()
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
    print("PASS: 25 unspliced protected branches, 76 required joint crossings, 25 fixed transitions and 50 separate rigid/flexible guard records; tap-board cascade rejected; all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
