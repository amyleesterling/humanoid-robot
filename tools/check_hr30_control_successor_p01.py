"""Fail-closed internal checker for the HR-30 control successor P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "control-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
WARNING = "PRELIMINARY - WHOLE-BODY CONTROL CANDIDATE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    status = json.loads((OUT / "control-successor-status.json").read_text(encoding="utf-8"))
    assert status["all_sequences_pass_bounded_control_screen"] is True
    assert status["rotary_kp_factor"] == 8.0 and status["rotary_kd_factor"] == 0.8
    assert status["maximum_rotary_tracking_error_deg"] <= 5.0
    assert status["maximum_rotary_saturation_fraction"] <= 0.10
    assert status["axes_failing_bounded_screen"] == []
    assert status["inverse_demand_within_candidate_endpoints_for_selected_leg_axes"] is True
    assert status["physical_execution_count"] == 0
    for key in ("controller_robustness_validated", "continuous_capacity_validated", "connection_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority"):
        assert status[key] is False, key

    summaries = rows(OUT / "sequence-control-summary.csv")
    axes = rows(OUT / "axis-control-results.csv")
    margins = rows(OUT / "torque-margin-register.csv")
    assert len(summaries) == 2 and all(row["result"].startswith("PASS") for row in summaries)
    assert len(axes) == 50 and not any(row["screen_state"].startswith("FAIL") for row in axes)
    assert len(margins) == 10 and all(float(row["endpoint_to_inverse_peak_ratio"]) >= 1.0 for row in margins)
    assert all(row["warning"] == WARNING for table in (summaries, axes, margins) for row in table)

    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(path.name for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    assert sorted(row["file"] for row in manifest) == expected
    for row in manifest:
        path = OUT / row["file"]
        assert int(row["bytes"]) == path.stat().st_size
        assert row["sha256"] == sha(path)
    assert sha(OUT / "control-successor-source.py") == sha(ROOT / "tools" / "generate_hr30_control_successor_p01.py")
    source_files = sorted(path.name for path in OUT.iterdir() if path.is_file())
    release_files = sorted(path.name for path in REL.iterdir() if path.is_file())
    assert source_files == release_files
    assert all(sha(OUT / name) == sha(REL / name) for name in source_files)

    source_rows = rows(OUT / "source-binding.csv")
    for row in source_rows:
        path = ROOT / row["path"]
        assert path.is_file() and sha(path) == row["sha256"]
    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:17px" in page and "font-size:16px" in page
    assert "No command from this package may be sent to hardware" in page
    assert "HR30-CONTROL-SUCCESSOR-P01-START" in (BODY / "README.md").read_text(encoding="utf-8")
    assert "HR30-CONTROL-SUCCESSOR-P01-START" in (BODY / "index.html").read_text(encoding="utf-8")
    print("PASS: complete HR-30 clears bounded 8/0.8 control screen; physical authority remains closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
