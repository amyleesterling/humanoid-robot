from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


WARNING = (
    "PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - "
    "NOT APPROVED FOR POWERED TESTING, MOTION, OR ENERGIZATION"
)

REQUIRED_COLUMNS = {
    "sample_index",
    "daq_time_s",
    "stop_command_state",
    "estop_state",
    "reset_input_state",
    "start_command_state",
    "motion_enable_command_state",
    "torque_enable_feedback",
    "source_voltage_V",
    "source_current_A",
    "k1_coil_state",
    "k2_coil_state",
    "k1_mirror_state",
    "k2_mirror_state",
    "external_angle_deg",
    "external_velocity_deg_s",
    "reaction_force_N",
    "bumper_displacement_mm",
    "dropped_scan_count",
    "sensor_saturation_flags",
    "run_id",
    "configuration_commit",
    "article_revision",
    "calibration_bundle_hash",
    "timing_budget_revision",
}

BOOL_COLUMNS = {
    "stop_command_state",
    "estop_state",
    "reset_input_state",
    "start_command_state",
    "motion_enable_command_state",
    "torque_enable_feedback",
    "k1_coil_state",
    "k2_coil_state",
    "k1_mirror_state",
    "k2_mirror_state",
}

FLOAT_COLUMNS = {
    "daq_time_s",
    "source_voltage_V",
    "source_current_A",
    "external_angle_deg",
    "external_velocity_deg_s",
    "reaction_force_N",
    "bumper_displacement_mm",
}

INTEGER_COLUMNS = {"sample_index", "dropped_scan_count", "sensor_saturation_flags"}

NUMERIC_CONFIG = {
    "expected_sample_interval_s",
    "sample_interval_relative_tolerance",
    "stop_velocity_threshold_deg_s",
    "stop_dwell_s",
    "stop_angle_band_deg",
    "rail_below_torque_threshold_v",
    "rail_dwell_s",
    "maximum_total_stop_time_s",
    "maximum_residual_travel_deg",
    "hard_stop_angle_deg",
    "minimum_endpoint_clearance_deg",
    "reset_observation_s",
    "reset_motion_noise_deg",
}


class AnalysisError(ValueError):
    pass


def parse_bool(value: str, field: str, row_number: int) -> int:
    normalized = value.strip().lower()
    if normalized in {"1", "true"}:
        return 1
    if normalized in {"0", "false"}:
        return 0
    raise AnalysisError(f"row {row_number}: {field} must be 0/1 or true/false")


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(NUMERIC_CONFIG - set(config))
    if missing:
        raise AnalysisError(f"configuration missing numeric keys: {', '.join(missing)}")
    unresolved = [key for key in NUMERIC_CONFIG if not isinstance(config[key], (int, float))]
    if unresolved:
        raise AnalysisError(
            "configuration remains unresolved for analysis: " + ", ".join(sorted(unresolved))
        )
    if config.get("stop_event_field") not in {"stop_command_state", "estop_state"}:
        raise AnalysisError("stop_event_field must be stop_command_state or estop_state")
    if config.get("motion_direction") not in {"POSITIVE", "NEGATIVE"}:
        raise AnalysisError("motion_direction must be POSITIVE or NEGATIVE")
    if config.get("analysis_mode") not in {"SYNTHETIC_VALIDATION_ONLY", "PHYSICAL_TRACE"}:
        raise AnalysisError("analysis_mode is invalid")
    for key in NUMERIC_CONFIG:
        if not math.isfinite(float(config[key])):
            raise AnalysisError(f"configuration value {key} is not finite")
    if float(config["expected_sample_interval_s"]) <= 0:
        raise AnalysisError("expected_sample_interval_s must be positive")
    if float(config["stop_dwell_s"]) <= 0 or float(config["rail_dwell_s"]) <= 0:
        raise AnalysisError("dwell times must be positive")
    return config


def load_trace(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise AnalysisError(f"trace missing required columns: {', '.join(missing)}")
        rows: list[dict[str, Any]] = []
        for row_number, raw in enumerate(reader, start=2):
            row: dict[str, Any] = dict(raw)
            try:
                for field in BOOL_COLUMNS:
                    row[field] = parse_bool(raw[field], field, row_number)
                for field in FLOAT_COLUMNS:
                    row[field] = float(raw[field])
                for field in INTEGER_COLUMNS:
                    row[field] = int(raw[field])
            except (TypeError, ValueError) as exc:
                raise AnalysisError(f"row {row_number}: invalid numeric value: {exc}") from exc
            numeric_values = [row[field] for field in FLOAT_COLUMNS]
            if not all(math.isfinite(value) for value in numeric_values):
                raise AnalysisError(f"row {row_number}: non-finite measurement")
            rows.append(row)
    if len(rows) < 3:
        raise AnalysisError("trace must contain at least three samples")
    return rows


def rising_edge(rows: list[dict[str, Any]], field: str, start: int = 1) -> int | None:
    for index in range(max(1, start), len(rows)):
        if rows[index - 1][field] == 0 and rows[index][field] == 1:
            return index
    return None


def rising_edges(rows: list[dict[str, Any]], field: str, start: int = 1) -> list[int]:
    return [
        index
        for index in range(max(1, start), len(rows))
        if rows[index - 1][field] == 0 and rows[index][field] == 1
    ]


def falling_edge(rows: list[dict[str, Any]], field: str, start: int) -> int | None:
    for index in range(max(1, start), len(rows)):
        if rows[index - 1][field] == 1 and rows[index][field] == 0:
            return index
    return None


def falling_edges(rows: list[dict[str, Any]], field: str, start: int) -> list[int]:
    return [
        index
        for index in range(max(1, start), len(rows))
        if rows[index - 1][field] == 1 and rows[index][field] == 0
    ]


def first_sustained(
    rows: list[dict[str, Any]],
    start: int,
    dwell_s: float,
    predicate,
) -> int | None:
    for index in range(start, len(rows)):
        end = index
        while end < len(rows) and rows[end]["daq_time_s"] - rows[index]["daq_time_s"] < dwell_s:
            if not predicate(rows[end]):
                break
            end += 1
        if end < len(rows) and predicate(rows[end]) and rows[end]["daq_time_s"] - rows[index]["daq_time_s"] >= dwell_s:
            return index
    return None


def analyze(trace_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    rows = load_trace(trace_path)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(passed), "detail": detail})

    samples_sequential = all(
        rows[index]["sample_index"] == rows[index - 1]["sample_index"] + 1
        for index in range(1, len(rows))
    )
    times_monotonic = all(
        rows[index]["daq_time_s"] > rows[index - 1]["daq_time_s"]
        for index in range(1, len(rows))
    )
    expected_dt = float(config["expected_sample_interval_s"])
    dt_tolerance = float(config["sample_interval_relative_tolerance"])
    intervals = [
        rows[index]["daq_time_s"] - rows[index - 1]["daq_time_s"]
        for index in range(1, len(rows))
    ]
    interval_ok = times_monotonic and all(
        abs(interval - expected_dt) <= expected_dt * dt_tolerance for interval in intervals
    )
    metadata_fields = (
        "run_id",
        "configuration_commit",
        "article_revision",
        "calibration_bundle_hash",
        "timing_budget_revision",
    )
    metadata_ok = all(
        len({str(row[field]).strip() for row in rows}) == 1
        and bool(str(rows[0][field]).strip())
        for field in metadata_fields
    )
    no_drops = all(row["dropped_scan_count"] == 0 for row in rows)
    no_saturation = all(row["sensor_saturation_flags"] == 0 for row in rows)
    integrity_ok = samples_sequential and interval_ok and metadata_ok and no_drops and no_saturation
    record(
        "DTA-001",
        integrity_ok,
        f"sequential={samples_sequential}; interval_ok={interval_ok}; metadata_ok={metadata_ok}; no_drops={no_drops}; no_saturation={no_saturation}",
    )

    event_field = str(config["stop_event_field"])
    stop_indices = rising_edges(rows, event_field)
    stop_index = stop_indices[0] if stop_indices else None
    record("DTA-002", len(stop_indices) == 1, f"stop_event_field={event_field}; indices={stop_indices}")
    if stop_index is None:
        raise AnalysisError(f"no rising edge found on {event_field}")
    stop_time = rows[stop_index]["daq_time_s"]
    stop_angle = rows[stop_index]["external_angle_deg"]

    reset_indices = rising_edges(rows, "reset_input_state", stop_index + 1)
    stop_phase_end = reset_indices[0] if reset_indices else len(rows)
    stop_phase_rows = rows[:stop_phase_end]

    edge_fields = ("k1_coil_state", "k2_coil_state", "k1_mirror_state", "k2_mirror_state")
    edge_lists = {field: falling_edges(stop_phase_rows, field, stop_index) for field in edge_fields}
    edge_indices = {field: (indices[0] if indices else None) for field, indices in edge_lists.items()}
    all_edges = all(
        rows[stop_index][field] == 1 and len(edge_lists[field]) == 1
        for field in edge_fields
    )
    record("DTA-003", all_edges, "; ".join(f"{key}={value}" for key, value in edge_lists.items()))

    rail_threshold = float(config["rail_below_torque_threshold_v"])
    rail_index = first_sustained(
        stop_phase_rows,
        stop_index,
        float(config["rail_dwell_s"]),
        lambda row: row["source_voltage_V"] <= rail_threshold,
    )
    record("DTA-004", rail_index is not None, f"threshold_V={rail_threshold}; index={rail_index}")

    velocity_threshold = float(config["stop_velocity_threshold_deg_s"])
    angle_band = float(config["stop_angle_band_deg"])
    motion_stop_index: int | None = None
    dwell = float(config["stop_dwell_s"])
    for index in range(stop_index, len(stop_phase_rows)):
        base_angle = rows[index]["external_angle_deg"]
        motion_stop_index = first_sustained(
            stop_phase_rows,
            index,
            dwell,
            lambda row, base=base_angle: abs(row["external_velocity_deg_s"]) <= velocity_threshold
            and abs(row["external_angle_deg"] - base) <= angle_band,
        )
        if motion_stop_index is not None:
            break
    record(
        "DTA-005",
        motion_stop_index is not None,
        f"velocity_threshold_deg_s={velocity_threshold}; angle_band_deg={angle_band}; index={motion_stop_index}",
    )
    if motion_stop_index is None:
        raise AnalysisError("no sustained motion-stop condition found")

    motion_stop_time = rows[motion_stop_index]["daq_time_s"]
    total_stop_time_s = motion_stop_time - stop_time
    stop_slice = rows[stop_index : motion_stop_index + 1]
    direction = str(config["motion_direction"])
    if direction == "POSITIVE":
        worst_endpoint = max(row["external_angle_deg"] for row in stop_slice)
        residual_travel = worst_endpoint - stop_angle
        endpoint_clearance = float(config["hard_stop_angle_deg"]) - worst_endpoint
    else:
        worst_endpoint = min(row["external_angle_deg"] for row in stop_slice)
        residual_travel = stop_angle - worst_endpoint
        endpoint_clearance = worst_endpoint - float(config["hard_stop_angle_deg"])
    timing_pass = total_stop_time_s <= float(config["maximum_total_stop_time_s"])
    travel_pass = residual_travel <= float(config["maximum_residual_travel_deg"])
    clearance_pass = endpoint_clearance >= float(config["minimum_endpoint_clearance_deg"])
    record(
        "DTA-006",
        timing_pass and travel_pass and clearance_pass,
        f"total_stop_time_s={total_stop_time_s:.9f}; residual_travel_deg={residual_travel:.9f}; endpoint_clearance_deg={endpoint_clearance:.9f}",
    )

    reset_index = reset_indices[0] if reset_indices else None
    reset_ok = len(reset_indices) == 1
    reset_detail = f"reset_indices={reset_indices}"
    if reset_index is not None:
        reset_time = rows[reset_index]["daq_time_s"]
        start_indices = rising_edges(rows, "start_command_state", reset_index + 1)
        start_index = start_indices[0] if start_indices else None
        observation_s = float(config["reset_observation_s"])
        distinct_start = (
            len(start_indices) == 1
            and rows[reset_index]["start_command_state"] == 0
            and rows[start_index]["daq_time_s"] - reset_time >= observation_s
        ) if start_index is not None else False
        observation_end = start_index - 1 if start_index is not None else len(rows) - 1
        window = rows[reset_index : observation_end + 1]
        reset_angle = rows[reset_index]["external_angle_deg"]
        prohibited_state = any(
            row["motion_enable_command_state"]
            or row["torque_enable_feedback"]
            or row["k1_coil_state"]
            or row["k2_coil_state"]
            for row in window
        )
        unexpected_motion = any(
            abs(row["external_angle_deg"] - reset_angle) > float(config["reset_motion_noise_deg"])
            for row in window
        )
        reset_ok = len(reset_indices) == 1 and distinct_start and bool(window) and not prohibited_state and not unexpected_motion
        reset_detail = (
            f"reset_indices={reset_indices}; observation_end={observation_end}; start_indices={start_indices}; "
            f"distinct_start={distinct_start}; minimum_observation_s={observation_s}; "
            f"prohibited_state={prohibited_state}; unexpected_motion={unexpected_motion}"
        )
    record("DTA-007", reset_ok, reset_detail)

    peak_current_a = max(row["source_current_A"] for row in rows)
    minimum_current_a = min(row["source_current_A"] for row in rows)
    peak_force_n = max(abs(row["reaction_force_N"]) for row in rows)
    peak_displacement_mm = max(row["bumper_displacement_mm"] for row in rows)
    positive_contact_work_j = 0.0
    for previous, current in zip(rows, rows[1:]):
        dx_m = (current["bumper_displacement_mm"] - previous["bumper_displacement_mm"]) / 1000.0
        average_positive_force = max(0.0, (previous["reaction_force_N"] + current["reaction_force_N"]) / 2.0)
        positive_contact_work_j += max(0.0, dx_m) * average_positive_force

    computed_pass = all(check["passed"] for check in checks)
    mode = str(config["analysis_mode"])
    result = {
        "schema": "project-button-hr-v0-dynamic-trace-analysis-p0.1",
        "status": WARNING,
        "analysis_mode": mode,
        "trace": str(trace_path.as_posix()),
        "config": str(config_path.as_posix()),
        "run_id": rows[0]["run_id"],
        "configuration_commit": rows[0]["configuration_commit"],
        "sample_count": len(rows),
        "computed_result": "PASS" if computed_pass else "FAIL",
        "run_disposition": "HOLD - QUALIFIED REVIEW REQUIRED" if computed_pass else "REJECT",
        "release_effect": "NONE",
        "event_metrics": {
            "stop_event_time_s": stop_time,
            "motion_stop_time_s": motion_stop_time,
            "total_stop_time_s": total_stop_time_s,
            "residual_travel_deg": residual_travel,
            "worst_endpoint_deg": worst_endpoint,
            "endpoint_clearance_deg": endpoint_clearance,
            "k1_coil_drop_time_s": None if edge_indices["k1_coil_state"] is None else rows[edge_indices["k1_coil_state"]]["daq_time_s"],
            "k2_coil_drop_time_s": None if edge_indices["k2_coil_state"] is None else rows[edge_indices["k2_coil_state"]]["daq_time_s"],
            "k1_mirror_open_time_s": None if edge_indices["k1_mirror_state"] is None else rows[edge_indices["k1_mirror_state"]]["daq_time_s"],
            "k2_mirror_open_time_s": None if edge_indices["k2_mirror_state"] is None else rows[edge_indices["k2_mirror_state"]]["daq_time_s"],
            "rail_below_threshold_time_s": None if rail_index is None else rows[rail_index]["daq_time_s"],
        },
        "range_metrics": {
            "peak_source_current_a": peak_current_a,
            "minimum_source_current_a": minimum_current_a,
            "peak_reaction_force_n": peak_force_n,
            "peak_bumper_displacement_mm": peak_displacement_mm,
            "positive_contact_work_j": positive_contact_work_j,
        },
        "checks": checks,
        "interpretation_limits": [
            "A computed PASS is not an approved test result or work authorization.",
            "Measurement uncertainty and the accepted timing budget remain external evidence inputs.",
            "Positive contact work is a numerical integral only and receives no safety or absorber-rating credit.",
            "Qualified electrical, mechanical, functional-safety, metrology and test dispositions remain required as applicable.",
        ],
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze one Project Button HR-V0 synchronized dynamic trace")
    parser.add_argument("trace", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = analyze(args.trace, args.config)
    except (AnalysisError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"computed_result": "ERROR", "run_disposition": "REJECT", "error": str(exc), "status": WARNING}, indent=2))
        return 2
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["computed_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
