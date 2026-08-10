#!/usr/bin/env python3
"""Analyze one corrected HR-V0 STOP or RESET/ARM dynamic trace."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Callable


WARNING = (
    "PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - "
    "NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)

COMMON_COLUMNS = {
    "sample_index", "daq_time_s", "source_voltage_V", "external_angle_deg",
    "dropped_scan_count", "sensor_saturation_flags", "run_id",
    "configuration_commit", "article_revision", "calibration_bundle_hash",
    "timing_budget_revision",
}
STOP_BOOL_COLUMNS = {
    "stop_event_state", "k1_coil_state", "k2_coil_state",
    "common_edm_chain_state", "k1_aux_status_state", "k2_aux_status_state",
}
RESET_BOOL_COLUMNS = {
    "reset_event_state", "arm_event_state", "k1_coil_state", "k2_coil_state",
    "k1_aux_status_state", "k2_aux_status_state",
}
COMMON_NUMERIC_CONFIG = {
    "expected_sample_interval_s", "sample_interval_relative_tolerance",
}
STOP_NUMERIC_CONFIG = {
    "control_source_valid_min_v", "e2_stop_observation_s", "e2_motion_noise_deg",
    "maximum_k1_coil_drop_time_s", "maximum_k2_coil_drop_time_s",
    "maximum_common_edm_close_time_s", "maximum_k1_aux_open_time_s",
    "maximum_k2_aux_open_time_s",
}
RESET_NUMERIC_CONFIG = {
    "minimum_reset_to_arm_interval_s", "reset_motion_noise_deg",
    "control_source_valid_min_v",
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
    if config.get("analysis_mode") not in {"SYNTHETIC_VALIDATION_ONLY", "PHYSICAL_TRACE"}:
        raise AnalysisError("analysis_mode is invalid")
    run_type = config.get("run_type")
    if run_type not in {"STOP", "RESET_ARM"}:
        raise AnalysisError("run_type must be STOP or RESET_ARM")
    required = set(COMMON_NUMERIC_CONFIG)
    required |= STOP_NUMERIC_CONFIG if run_type == "STOP" else RESET_NUMERIC_CONFIG
    missing = sorted(required - set(config))
    if missing:
        raise AnalysisError("configuration missing numeric keys: " + ", ".join(missing))
    unresolved = sorted(key for key in required if not isinstance(config[key], (int, float)))
    if unresolved:
        raise AnalysisError("configuration remains unresolved for analysis: " + ", ".join(unresolved))
    for key in required:
        if not math.isfinite(float(config[key])):
            raise AnalysisError(f"configuration value {key} is not finite")
    if float(config["expected_sample_interval_s"]) <= 0:
        raise AnalysisError("expected_sample_interval_s must be positive")
    if run_type == "STOP" and float(config["e2_stop_observation_s"]) <= 0:
        raise AnalysisError("e2_stop_observation_s must be positive")
    return config


def load_trace(path: Path, run_type: str) -> list[dict[str, Any]]:
    bool_columns = STOP_BOOL_COLUMNS if run_type == "STOP" else RESET_BOOL_COLUMNS
    required = COMMON_COLUMNS | bool_columns
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise AnalysisError("trace missing required columns: " + ", ".join(missing))
        rows: list[dict[str, Any]] = []
        for row_number, raw in enumerate(reader, start=2):
            row: dict[str, Any] = dict(raw)
            try:
                for field in bool_columns:
                    row[field] = parse_bool(raw[field], field, row_number)
                row["sample_index"] = int(raw["sample_index"])
                row["dropped_scan_count"] = int(raw["dropped_scan_count"])
                row["sensor_saturation_flags"] = int(raw["sensor_saturation_flags"])
                row["daq_time_s"] = float(raw["daq_time_s"])
                row["source_voltage_V"] = float(raw["source_voltage_V"])
                row["external_angle_deg"] = float(raw["external_angle_deg"])
            except (TypeError, ValueError) as exc:
                raise AnalysisError(f"row {row_number}: invalid numeric value: {exc}") from exc
            if not all(math.isfinite(row[field]) for field in ("daq_time_s", "source_voltage_V", "external_angle_deg")):
                raise AnalysisError(f"row {row_number}: non-finite measurement")
            rows.append(row)
    if len(rows) < 3:
        raise AnalysisError("trace must contain at least three samples")
    for index, row in enumerate(rows):
        if index == 0:
            dt = rows[1]["daq_time_s"] - row["daq_time_s"]
            da = rows[1]["external_angle_deg"] - row["external_angle_deg"]
        else:
            dt = row["daq_time_s"] - rows[index - 1]["daq_time_s"]
            da = row["external_angle_deg"] - rows[index - 1]["external_angle_deg"]
        row["derived_velocity_deg_s"] = da / dt if dt > 0 else float("nan")
    return rows


def rising_edges(rows: list[dict[str, Any]], field: str, start: int = 1) -> list[int]:
    return [i for i in range(max(1, start), len(rows)) if rows[i - 1][field] == 0 and rows[i][field] == 1]


def falling_edges(rows: list[dict[str, Any]], field: str, start: int = 1) -> list[int]:
    return [i for i in range(max(1, start), len(rows)) if rows[i - 1][field] == 1 and rows[i][field] == 0]


def first_sustained(
    rows: list[dict[str, Any]], start: int, dwell_s: float,
    predicate: Callable[[dict[str, Any]], bool],
) -> int | None:
    for index in range(start, len(rows)):
        end = index
        while end < len(rows) and predicate(rows[end]):
            if rows[end]["daq_time_s"] - rows[index]["daq_time_s"] >= dwell_s:
                return index
            end += 1
    return None


def integrity_check(rows: list[dict[str, Any]], config: dict[str, Any]) -> tuple[bool, str]:
    sequential = all(rows[i]["sample_index"] == rows[i - 1]["sample_index"] + 1 for i in range(1, len(rows)))
    expected_dt = float(config["expected_sample_interval_s"])
    tolerance = float(config["sample_interval_relative_tolerance"])
    intervals = [rows[i]["daq_time_s"] - rows[i - 1]["daq_time_s"] for i in range(1, len(rows))]
    interval_ok = all(dt > 0 and abs(dt - expected_dt) <= expected_dt * tolerance for dt in intervals)
    metadata = ("run_id", "configuration_commit", "article_revision", "calibration_bundle_hash", "timing_budget_revision")
    metadata_ok = all(len({str(row[field]).strip() for row in rows}) == 1 and str(rows[0][field]).strip() for field in metadata)
    no_drops = all(row["dropped_scan_count"] == 0 for row in rows)
    no_saturation = all(row["sensor_saturation_flags"] == 0 for row in rows)
    passed = sequential and interval_ok and metadata_ok and no_drops and no_saturation
    return passed, f"sequential={sequential}; interval_ok={interval_ok}; metadata_ok={metadata_ok}; no_drops={no_drops}; no_saturation={no_saturation}"


def analyze(trace_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    run_type = str(config["run_type"])
    rows = load_trace(trace_path, run_type)
    checks: list[dict[str, Any]] = []

    def record(check_id: str, passed: bool | None, detail: str) -> None:
        checks.append({"check_id": check_id, "applicable": passed is not None, "passed": passed, "detail": detail})

    integrity_ok, integrity_detail = integrity_check(rows, config)
    record("DTA2-001", integrity_ok, integrity_detail)
    event_metrics: dict[str, Any] = {}

    if run_type == "STOP":
        stop_edges = rising_edges(rows, "stop_event_state")
        stop_index = stop_edges[0] if stop_edges else None
        record("DTA2-002", len(stop_edges) == 1, f"stop_event_rising_edges={stop_edges}")
        if stop_index is None:
            raise AnalysisError("no STOP event rising edge")
        stop_time = rows[stop_index]["daq_time_s"]
        stop_angle = rows[stop_index]["external_angle_deg"]
        observation_s = float(config["e2_stop_observation_s"])
        observation_end = next(
            (index for index in range(stop_index, len(rows)) if rows[index]["daq_time_s"] - stop_time >= observation_s),
            None,
        )
        window = rows[stop_index:observation_end + 1] if observation_end is not None else rows[stop_index:]

        falling = {
            field: falling_edges(rows, field, stop_index)
            for field in ("k1_coil_state", "k2_coil_state", "k1_aux_status_state", "k2_aux_status_state")
        }
        edm_rising = rising_edges(rows, "common_edm_chain_state", stop_index)
        preconditions = (
            rows[stop_index]["k1_coil_state"] == 1
            and rows[stop_index]["k2_coil_state"] == 1
            and rows[stop_index]["k1_aux_status_state"] == 1
            and rows[stop_index]["k2_aux_status_state"] == 1
            and rows[stop_index]["common_edm_chain_state"] == 0
        )
        transitions_ok = preconditions and all(len(value) == 1 for value in falling.values()) and len(edm_rising) == 1
        record("DTA2-003", transitions_ok, f"preconditions={preconditions}; falling={falling}; common_edm_rising={edm_rising}; auxiliaries_diagnostic_only=true")

        source_valid = observation_end is not None and all(
            row["source_voltage_V"] >= float(config["control_source_valid_min_v"]) for row in window
        )
        record("DTA2-004", source_valid, f"control_source_valid={source_valid}; observation_end={observation_end}; minimum_V={config['control_source_valid_min_v']}")

        maximum_angle_delta = max((abs(row["external_angle_deg"] - stop_angle) for row in window), default=float("inf"))
        no_motion = observation_end is not None and maximum_angle_delta <= float(config["e2_motion_noise_deg"])
        record("DTA2-005", no_motion, f"disconnected_load_e2=true; maximum_angle_delta_deg={maximum_angle_delta:.9f}; limit_deg={config['e2_motion_noise_deg']}")

        transition_indices = {
            "k1_coil": falling["k1_coil_state"][0] if falling["k1_coil_state"] else None,
            "k2_coil": falling["k2_coil_state"][0] if falling["k2_coil_state"] else None,
            "common_edm": edm_rising[0] if edm_rising else None,
            "k1_aux": falling["k1_aux_status_state"][0] if falling["k1_aux_status_state"] else None,
            "k2_aux": falling["k2_aux_status_state"][0] if falling["k2_aux_status_state"] else None,
        }
        transition_delays = {
            name: None if index is None else rows[index]["daq_time_s"] - stop_time
            for name, index in transition_indices.items()
        }
        limit_map = {
            "k1_coil": "maximum_k1_coil_drop_time_s",
            "k2_coil": "maximum_k2_coil_drop_time_s",
            "common_edm": "maximum_common_edm_close_time_s",
            "k1_aux": "maximum_k1_aux_open_time_s",
            "k2_aux": "maximum_k2_aux_open_time_s",
        }
        limits_ok = transitions_ok and all(
            transition_delays[name] is not None
            and float(transition_delays[name]) <= float(config[limit_key])
            for name, limit_key in limit_map.items()
        )
        record("DTA2-006", limits_ok, f"transition_delays_s={transition_delays}; accepted_limits={{{', '.join(f'{name}:{config[key]}' for name, key in limit_map.items())}}}")
        record("DTA2-007", None, "RESET/ARM separation is evaluated in a separate eight-channel RESET_ARM run")
        event_metrics = {
            "stop_event_time_s": stop_time,
            "e2_observation_end_time_s": rows[observation_end]["daq_time_s"] if observation_end is not None else None,
            "maximum_e2_angle_delta_deg": maximum_angle_delta,
            "k1_coil_drop_time_s": rows[falling["k1_coil_state"][0]]["daq_time_s"] if falling["k1_coil_state"] else None,
            "k2_coil_drop_time_s": rows[falling["k2_coil_state"][0]]["daq_time_s"] if falling["k2_coil_state"] else None,
            "common_edm_chain_close_time_s": rows[edm_rising[0]]["daq_time_s"] if edm_rising else None,
            "k1_aux_open_time_s": rows[falling["k1_aux_status_state"][0]]["daq_time_s"] if falling["k1_aux_status_state"] else None,
            "k2_aux_open_time_s": rows[falling["k2_aux_status_state"][0]]["daq_time_s"] if falling["k2_aux_status_state"] else None,
            "control_source_minimum_observed_v": min((row["source_voltage_V"] for row in window), default=None),
        }
    else:
        reset_edges = rising_edges(rows, "reset_event_state")
        arm_edges = rising_edges(rows, "arm_event_state")
        reset_index = reset_edges[0] if reset_edges else None
        record("DTA2-002", len(reset_edges) == 1, f"reset_event_rising_edges={reset_edges}")
        if reset_index is None:
            raise AnalysisError("no RESET event rising edge")
        arm_after_reset = [index for index in arm_edges if index > reset_index]
        arm_index = arm_after_reset[0] if arm_after_reset else None
        interval_ok = (
            len(arm_edges) == 1 and arm_index is not None
            and rows[arm_index]["daq_time_s"] - rows[reset_index]["daq_time_s"] >= float(config["minimum_reset_to_arm_interval_s"])
        )
        observation_end = arm_index if arm_index is not None else len(rows)
        window = rows[reset_index:observation_end]
        source_valid = bool(window) and all(row["source_voltage_V"] >= float(config["control_source_valid_min_v"]) for row in window)
        record("DTA2-003", None, "common EDM transition is evaluated in a separate eight-channel STOP run")
        record("DTA2-004", source_valid, f"source_valid={source_valid}; minimum_V={config['control_source_valid_min_v']}")

        reset_angle = rows[reset_index]["external_angle_deg"]
        unexpected_motion = any(abs(row["external_angle_deg"] - reset_angle) > float(config["reset_motion_noise_deg"]) for row in window)
        record("DTA2-005", bool(window) and not unexpected_motion, f"window_samples={len(window)}; unexpected_motion={unexpected_motion}")
        record("DTA2-006", None, "stop time/travel/clearance are evaluated in a separate eight-channel STOP run")

        prohibited_state = any(
            row["k1_coil_state"] or row["k2_coil_state"]
            or row["k1_aux_status_state"] or row["k2_aux_status_state"]
            for row in window
        )
        reset_ok = interval_ok and source_valid and bool(window) and not prohibited_state and not unexpected_motion
        record("DTA2-007", reset_ok, f"reset_edges={reset_edges}; arm_edges={arm_edges}; interval_ok={interval_ok}; prohibited_state={prohibited_state}; unexpected_motion={unexpected_motion}")
        event_metrics = {
            "reset_event_time_s": rows[reset_index]["daq_time_s"],
            "arm_event_time_s": rows[arm_index]["daq_time_s"] if arm_index is not None else None,
            "reset_to_arm_interval_s": rows[arm_index]["daq_time_s"] - rows[reset_index]["daq_time_s"] if arm_index is not None else None,
            "maximum_reset_window_angle_delta_deg": max((abs(row["external_angle_deg"] - reset_angle) for row in window), default=None),
        }

    record("DTA2-008", True, "K1/K2 NO auxiliary channels are diagnostic only; safety_function_credit=ZERO")
    applicable_pass = all(check["passed"] for check in checks if check["applicable"])
    record("DTA2-009", applicable_pass, "computed PASS remains HOLD; qualified configuration-specific disposition required")
    computed_pass = all(check["passed"] for check in checks if check["applicable"])
    return {
        "schema": "project-button-hr-v0-dynamic-trace-analysis-p0.2",
        "status": WARNING,
        "analysis_mode": config["analysis_mode"],
        "run_type": run_type,
        "trace": trace_path.as_posix(),
        "config": config_path.as_posix(),
        "run_id": rows[0]["run_id"],
        "configuration_commit": rows[0]["configuration_commit"],
        "sample_count": len(rows),
        "computed_result": "PASS" if computed_pass else "FAIL",
        "run_disposition": "HOLD - QUALIFIED REVIEW REQUIRED" if computed_pass else "REJECT",
        "release_effect": "NONE",
        "event_metrics": event_metrics,
        "checks": checks,
        "interpretation_limits": [
            "The NC mirror contacts are represented by one common series-EDM chain; two series points are never treated as independent contact states.",
            "K1/K2 NO auxiliary channels are diagnostic corroboration only and receive zero safety-function credit.",
            "STOP and RESET_ARM are separate eight-channel physical runs; sequential runs cannot prove cross-run simultaneity.",
            "The STOP schema is restricted to disconnected-load E2 with the actuator source absent; it cannot prove powered-motion stopping time, travel, or clearance.",
            "A computed PASS is not an approved result or work authorization.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze one corrected HR-V0 STOP or RESET/ARM trace")
    parser.add_argument("trace", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(args.trace, args.config)
    except AnalysisError as exc:
        print(f"ERROR: {exc}")
        return 2
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["computed_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
