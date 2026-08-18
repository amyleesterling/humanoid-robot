"""Fail-closed checker for the HR-30 lightweight hip successor P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "lightweight-hip-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    status = json.loads((OUT / "lightweight-hip-status.json").read_text(encoding="utf-8"))
    assert status["complete_humanoid_present"] is True
    assert status["hip_axis_count"] == 4 and status["stage_count_per_axis"] == 1
    assert status["total_transmission_ratio"] == 4.0
    assert status["new_hip_pair_interference_count"] == 0
    assert status["program_mass_maximum_met"] is True
    assert status["projected_active_tether_mass_kg"] <= 10.0
    assert status["bounded_control_screen_passed"] is True
    for key in ("tooth_geometry_released", "capacity_validated", "thermal_validated", "fabrication_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority"):
        assert status[key] is False, key
    transmissions = rows(OUT / "hip-transmission-register.csv")
    assert len(transmissions) == 4 and all(row["ratio"] == "4.000:1" for row in transmissions)
    assert all(row["belt"] == "GBN340EV5GT-090" for row in transmissions)
    clearances = rows(OUT / "hip-clearance-register.csv")
    assert len(clearances) == 6 and not any(row["state"] == "INTERFERENCE" for row in clearances)
    same_side = [row for row in clearances if row["first_axis"][0] == row["second_axis"][0]]
    assert len(same_side) == 2
    assert all(float(row["minimum_nominal_distance_mm"]) >= 2.0 for row in same_side)
    replacement = rows(OUT / "replacement-boundary.csv")
    assert len(replacement) == 68
    prefix_counts = {
        prefix: sum(row["item_id"].startswith(prefix + "-") for row in replacement)
        for prefix in ("ACT", "BELT", "JF", "JHW")
    }
    assert prefix_counts == {"ACT": 4, "BELT": 4, "JF": 32, "JHW": 28}
    assert len(rows(OUT / "hip-mass-budget.csv")) >= 50
    whole = cq.importers.importStep(str(OUT / "HR-30_light4_whole_body_candidate.step")).val()
    box = whole.BoundingBox()
    assert abs(box.zlen - 762.0) <= 0.01
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    assert sorted(row["path"] for row in manifest) == expected
    for row in manifest:
        path = OUT / row["path"]
        assert int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path)
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    assert source_files == release_files and all(sha(OUT / name) == sha(REL / name) for name in source_files)
    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:17px" in page and "font-size:16px" in page
    assert "no work or energization authority" in page
    print(f"PASS: four one-stage 4:1 hips; {status['projected_active_tether_mass_kg']:.6f} kg; authority closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
