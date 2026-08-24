"""Fail-closed checker for HR-30 harness duty-current envelope P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "harness" / "duty-current-envelope-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-8) -> None:
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)


def summary(values: list[float]) -> tuple[float, float, float, float]:
    vector = np.asarray(values, dtype=float)
    return (
        float(np.max(vector)),
        float(np.percentile(vector, 95)),
        float(np.sqrt(np.mean(np.square(vector)))),
        float(np.mean(vector)),
    )


def main() -> int:
    status = json.loads((OUT / "duty-current-status.json").read_text(encoding="utf-8"))
    assert status["identifier"] == "HR30-HARNESS-DUTY-CURRENT-ENVELOPE-P0.1"
    assert status["sequence_count"] == 2
    assert status["axis_count"] == 25 and status["rotary_axis_count"] == 23 and status["gripper_axis_count"] == 2
    assert status["bus_count"] == 8 and status["bounded_sequence_rms_computed"] is True
    mass_summary = json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    close(status["control_model_mass_kg"], mass_summary["active_tether_dynamics_planning_mass_kg"], tolerance=5e-6)
    assert status["all_control_sequences_passed_source_screen"] is True
    for key in (
        "active_object_grip_included", "electronics_idle_and_loss_current_included", "regeneration_included",
        "normal_rms_demand_released", "wire_construction_selected", "branch_protection_selected",
        "thermal_validated", "procurement_authority", "connection_authority", "powered_test_authority",
        "motion_authority", "walking_authority", "energization_authority",
    ):
        assert status[key] is False, key

    bindings = rows(BODY / "actuator-bus-axis-binding.csv")
    bus_by_axis = {row["axis_id"]: row["bus_id"] for row in bindings}
    assert len(bus_by_axis) == 25 and len(set(bus_by_axis.values())) == 8
    current = {row["axis_id"]: row for row in rows(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")}
    source_summaries = rows(BODY / "control-successor-p0.1" / "sequence-control-summary.csv")
    expected_logged = sum(int(row["logged_sample_count"]) for row in source_summaries)

    samples = rows(OUT / "current-equivalent-samples.csv")
    assert len(samples) == expected_logged * 25 == status["axis_sample_count"]
    assert {row["axis_id"] for row in samples} == set(bus_by_axis)
    assert {row["sequence_id"] for row in samples} == {"WS-L01", "WS-R01"}
    by_key: dict[tuple[str, str], list[float]] = defaultdict(list)
    bus_time: dict[tuple[str, str, str], float] = defaultdict(float)
    whole_time: dict[tuple[str, str], float] = defaultdict(float)
    for row in samples:
        axis = row["axis_id"]
        assert row["bus_id"] == bus_by_axis[axis]
        command = float(row["absolute_command"])
        torque = float(row["equivalent_output_torque_nm"])
        equivalent = float(row["torque_producing_current_equivalent_a"])
        candidate = float(current[axis]["candidate_current_a"])
        if axis.endswith("_GRIPPER"):
            close(torque, command * 0.01, 2e-8)
            endpoint = float(current[axis]["current_limited_linear_endpoint_nm"])
            assert "ACTIVE OBJECT GRIP" in row["calibration_boundary"]
        else:
            close(torque, command, 2e-8)
            endpoint = float(current[axis]["current_limited_linear_endpoint_nm"])
            if axis in {"L_HIP_PITCH", "L_HIP_ROLL", "R_HIP_PITCH", "R_HIP_ROLL"}:
                endpoint *= 4.0 / float(current[axis]["transmission_ratio"])
            assert "IDLE/LOSS/TRANSIENT/REGEN EXCLUDED" in row["calibration_boundary"]
        close(equivalent, torque / endpoint * candidate, 2e-8)
        key = (row["sequence_id"], axis)
        by_key[key].append(equivalent)
        time_key = (row["sequence_id"], row["time_s"])
        bus_time[(time_key[0], time_key[1], row["bus_id"])] += equivalent
        whole_time[time_key] += equivalent

    axis_envelopes = rows(OUT / "axis-current-duty-envelope.csv")
    assert len(axis_envelopes) == status["axis_sequence_envelope_count"] == 50
    for row in axis_envelopes:
        values = by_key[(row["sequence_id"], row["axis_id"])]
        assert int(row["sample_count"]) == len(values)
        for actual, expected in zip(
            (float(row["peak_current_equivalent_a"]), float(row["p95_current_equivalent_a"]), float(row["rms_current_equivalent_a"]), float(row["mean_current_equivalent_a"])),
            summary(values),
        ):
            close(actual, expected, 2e-8)
        assert row["thermal_rating_credit"] == "NONE"

    bus_envelopes = rows(OUT / "bus-current-duty-envelope.csv")
    assert len(bus_envelopes) == status["bus_sequence_envelope_count"] == 24
    for row in bus_envelopes:
        sequences = [row["sequence_id"]] if row["sequence_id"] != "ALL-BOUND-TRACES" else ["WS-L01", "WS-R01"]
        values = [value for (sequence, _time, bus), value in bus_time.items() if sequence in sequences and bus == row["bus_id"]]
        assert int(row["sample_count"]) == len(values)
        for actual, expected in zip(
            (float(row["peak_current_equivalent_a"]), float(row["p95_current_equivalent_a"]), float(row["rms_current_equivalent_a"]), float(row["mean_current_equivalent_a"])),
            summary(values),
        ):
            close(actual, expected, 2e-8)
        assert row["released_normal_demand"] == "NO" and row["thermal_rating_credit"] == "NONE"

    whole = rows(OUT / "whole-body-current-duty-envelope.csv")
    assert len(whole) == 3
    for row in whole:
        sequences = [row["sequence_id"]] if row["sequence_id"] != "ALL-BOUND-TRACES" else ["WS-L01", "WS-R01"]
        values = [value for (sequence, _time), value in whole_time.items() if sequence in sequences]
        assert int(row["sample_count"]) == len(values)
        for actual, expected in zip(
            (float(row["peak_current_equivalent_a"]), float(row["p95_current_equivalent_a"]), float(row["rms_current_equivalent_a"]), float(row["mean_current_equivalent_a"])),
            summary(values),
        ):
            close(actual, expected, 2e-8)
        assert row["released_supply_demand"] == "NO" and row["thermal_rating_credit"] == "NONE"

    aggregate_bus = [row for row in bus_envelopes if row["sequence_id"] == "ALL-BOUND-TRACES"]
    close(status["maximum_bounded_bus_peak_current_equivalent_a"], max(float(row["peak_current_equivalent_a"]) for row in aggregate_bus))
    close(status["maximum_bounded_bus_rms_current_equivalent_a"], max(float(row["rms_current_equivalent_a"]) for row in aggregate_bus))
    close(status["whole_body_bounded_peak_current_equivalent_a"], float(whole[-1]["peak_current_equivalent_a"]))
    close(status["whole_body_bounded_rms_current_equivalent_a"], float(whole[-1]["rms_current_equivalent_a"]))

    source_bindings = rows(OUT / "source-binding.csv")
    assert len(source_bindings) == 10
    for row in source_bindings:
        path = ROOT / row["path"]
        assert path.is_file() and row["sha256"] == sha(path)

    manifest = rows(OUT / "file-manifest.csv")
    expected_files = sorted(path.name for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    assert sorted(row["file"] for row in manifest) == expected_files
    for row in manifest:
        path = OUT / row["file"]
        assert int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path)

    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    assert source_files == release_files
    assert all(sha(OUT / name) == sha(REL / name) for name in source_files)

    page = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:17px" in page and "font-size:16px" in page
    assert "cannot release conductors or protection" in page
    for path in (BODY / "README.md", BODY / "index.html", BODY / "harness" / "README.md", BODY / "harness" / "index.html"):
        text = path.read_text(encoding="utf-8")
        assert "HR30-DUTY-CURRENT-P01-START" in text and "duty-current-envelope-p0.1" in text

    print(
        "PASS: 25-axis/8-bus bounded current-duty envelopes independently recomputed; "
        "normal demand, thermal rating and all powered authority remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
