"""Independent fail-closed checker for HR-30 harness duty/thermal P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "harness" / "duty-thermal-screen-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_text_sha(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 2e-8) -> None:
    assert math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance), (a, b)


def stats(values: list[float]) -> tuple[float, float, float, float]:
    ordered = sorted(values)
    rank = 0.95 * (len(ordered) - 1)
    lo, hi = math.floor(rank), math.ceil(rank)
    p95 = ordered[lo] if lo == hi else ordered[lo] + (rank - lo) * (ordered[hi] - ordered[lo])
    return max(values), p95, math.sqrt(sum(v*v for v in values) / len(values)), sum(values) / len(values)


def main() -> int:
    status = json.loads((OUT / "duty-thermal-status.json").read_text(encoding="utf-8"))
    assert status["identifier"] == "HR30-HARNESS-DUTY-THERMAL-SCREEN-P0.1"
    assert status["axis_count"] == 25 and status["bus_count"] == 8 and status["power_corridor_count"] == 6
    assert status["sample_count"] == 26850 and status["bounded_torque_component_computed"] is True
    assert status["route_lengths_bound"] is True and status["corridor_bundle_counts_computed"] is True
    for key in ("total_normal_rms_released", "cf130_resistance_verified", "wire_selected", "contact_derating_validated",
                "branch_protection_selected", "thermal_validated", "procurement_authority", "fabrication_authority",
                "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False, key

    raw = rows(BODY / "harness" / "duty-current-envelope-p0.1" / "current-equivalent-samples.csv")
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in raw:
        grouped[row["axis_id"]].append(float(row["torque_producing_current_equivalent_a"]))
    axis = rows(OUT / "axis-duty-voltage-drop-screen.csv")
    assert len(axis) == 25 and {row["axis_id"] for row in axis} == set(grouped)
    by_axis = {row["axis_id"]: row for row in axis}
    for row in axis:
        expected = stats(grouped[row["axis_id"]])
        actual = tuple(float(row[key]) for key in ("bounded_peak_current_equivalent_a", "bounded_p95_current_equivalent_a", "bounded_rms_current_equivalent_a", "bounded_mean_current_equivalent_a"))
        for a, b in zip(actual, expected):
            close(a, b)
        length_km = float(row["round_trip_planning_length_mm"]) / 1_000_000.0
        r20 = length_km * 79.0
        r80 = r20 * (1.0 + 0.00393 * 60.0)
        close(float(row["comparison_loop_r20_ohm"]), r20)
        close(float(row["comparison_loop_r80_ohm"]), r80)
        close(float(row["bounded_rms_drop_80c_comparison_v"]), actual[2] * r80)
        close(float(row["bounded_peak_drop_80c_comparison_v"]), actual[0] * r80)
        close(float(row["bounded_rms_loss_80c_comparison_w"]), actual[2] ** 2 * r80)
        assert row["thermal_rating_credit"] == "NONE" and "CF130 DCR" in row["resistance_state"]

    contact = rows(OUT / "contact-utilization-screen.csv")
    assert len(contact) == 25
    for row in contact:
        a = by_axis[row["axis_id"]]
        close(float(row["bounded_peak_to_3a_headline_ratio"]), float(a["bounded_peak_current_equivalent_a"]) / 3.0)
        close(float(row["candidate_cap_to_3a_headline_ratio"]), float(a["candidate_internal_cap_a"]) / 3.0)
        assert "NO HOT CONTACT" in row["contact_disposition"]

    bus = rows(OUT / "bus-duty-loss-screen.csv")
    assert len(bus) == 8 and sum(int(row["axis_count"]) for row in bus) == 25
    for row in bus:
        members = row["axes"].split("; ")
        close(float(row["sum_axis_bounded_rms_loss_80c_comparison_w"]), sum(float(by_axis[a]["bounded_rms_loss_80c_comparison_w"]) for a in members))
        assert row["thermal_rating_credit"] == "NONE"

    corridors = rows(OUT / "corridor-bundle-duty-screen.csv")
    assert len(corridors) == 6 and sum(int(row["axis_count"]) for row in corridors) == 25
    for row in corridors:
        members = row["axes"].split("; ")
        assert int(row["insulated_conductor_count"]) == 2 * len(members)
        close(float(row["sum_bounded_rms_loss_80c_comparison_w"]), sum(float(by_axis[a]["bounded_rms_loss_80c_comparison_w"]) for a in members))
        assert row["ambient_c"] == "SELECTION REQUIRED" and "NO BUNDLE DERATING" in row["thermal_state"]

    successor = rows(OUT / "current-derating-successor-binding.csv")
    assert len(successor) == 25
    for row in successor:
        a = by_axis[row["axis_id"]]
        close(float(row["bounded_torque_component_rms_a"]), float(a["bounded_rms_current_equivalent_a"]))
        assert row["total_normal_rms_current_a"].startswith("SELECTION REQUIRED")
        assert row["fault_current_a"] == "SELECTION REQUIRED"
        assert row["thermal_rating_credit"] == "NONE"

    assert len(rows(OUT / "thermal-test-prescription.csv")) == 8
    assert all(row["state"] == "OPEN" for row in rows(OUT / "open-holds.csv"))
    basis = rows(OUT / "calculation-basis.csv")
    assert len(basis) == 5
    assert "53.149606299" in basis[0]["value"] and "NOT CF130" in basis[3]["use_boundary"]

    sources = rows(OUT / "source-binding.csv")
    assert len(sources) == 10
    for row in sources:
        path = ROOT / row["path"]
        assert path.is_file() and normalized_text_sha(path) == row["normalized_lf_sha256"]
        assert row["hash_boundary"] == "UTF-8 TEXT NORMALIZED TO LF"

    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(path.name for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    assert sorted(row["file"] for row in manifest) == expected
    for row in manifest:
        path = OUT / row["file"]
        assert int(row["bytes"]) == path.stat().st_size and sha(path) == row["sha256"]
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    assert source_files == release_files and all(sha(OUT / name) == sha(REL / name) for name in source_files)

    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:17px" in page and "font-size:16px" in page and "not</strong> the resistance of CF130" in page
    for path in (BODY / "README.md", BODY / "index.html", BODY / "harness" / "README.md", BODY / "harness" / "index.html",
                 BODY / "harness" / "physical-p0.1" / "README.md", BODY / "harness" / "physical-p0.1" / "index.html"):
        text = path.read_text(encoding="utf-8")
        assert "HR30-DUTY-THERMAL-P01-START" in text and "duty-thermal-screen-p0.1" in text

    print("PASS: 25-axis route-specific duty/drop/loss and 6 corridor bundle screens independently recomputed; hot ratings and all powered authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
