from __future__ import annotations

import csv
import json
from pathlib import Path

from analyze_hr_v0_dynamic_trace_p01 import AnalysisError, analyze


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "hr-v0" / "dynamic-trace-p0.1"
WEB = ROOT / "release" / "hr-v0" / "dynamic-trace-analysis-p0.1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    expected = {
        "acceptance-rule-register.csv",
        "analysis-config-template.json",
        "event-channel-extension.csv",
        "package-status.json",
        "source-register.csv",
        "synthetic",
    }
    require(errors, OUT.is_dir(), "dynamic trace analysis directory missing")
    if OUT.is_dir():
        require(errors, {path.name for path in OUT.iterdir()} == expected, "analysis package membership changed")
    synthetic = OUT / "synthetic"
    if synthetic.is_dir():
        require(
            errors,
            {path.name for path in synthetic.iterdir()} == {
                "synthetic-config.json",
                "pass-trace.csv",
                "fail-reset-trace.csv",
                "fail-integrity-trace.csv",
                "fail-early-start-trace.csv",
            },
            "synthetic fixture membership changed",
        )

    template = json.loads((OUT / "analysis-config-template.json").read_text(encoding="utf-8"))
    require(errors, template.get("analysis_mode") == "PHYSICAL_TRACE", "physical template mode changed")
    required_numeric = {
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
    require(
        errors,
        all(template.get(key) == "SELECTION REQUIRED" for key in required_numeric),
        "a physical-run numeric acceptance value appears released",
    )
    require(errors, template.get("stop_event_field") == "SELECTION REQUIRED", "physical stop event was selected")
    require(errors, template.get("motion_direction") == "SELECTION REQUIRED", "physical direction was selected")

    rules = read_csv(OUT / "acceptance-rule-register.csv")
    require(errors, len(rules) == 9, "expected nine analysis rules")
    require(errors, {row["rule_id"] for row in rules} == {f"DTA-{index:03d}" for index in range(1, 10)}, "rule identifiers changed")
    require(errors, rules[6]["rule_id"] == "DTA-007" and "Reset" in rules[6]["rule"], "reset interlock rule missing")
    require(errors, rules[-1]["state"] == "MANDATORY HOLD", "qualified disposition hold lost")

    extensions = read_csv(OUT / "event-channel-extension.csv")
    require(errors, len(extensions) == 4, "expected four event-channel extensions")
    require(
        errors,
        {row["field_name"] for row in extensions}
        == {"reset_input_state", "start_command_state", "motion_enable_command_state", "torque_enable_feedback"},
        "event-channel extension changed",
    )

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    require(errors, status.get("identifier") == "HR-V0-DYN-TRACE-P0.1", "wrong package identifier")
    require(errors, status.get("executed_physical_run_count") == 0, "physical evidence was invented")
    require(errors, status.get("authorized_powered_run_count") == 0, "powered run appears authorized")
    require(errors, status.get("release_effect") == "NONE", "package gained release authority")

    config = OUT / "synthetic" / "synthetic-config.json"
    pass_result = analyze(OUT / "synthetic" / "pass-trace.csv", config)
    reset_result = analyze(OUT / "synthetic" / "fail-reset-trace.csv", config)
    integrity_result = analyze(OUT / "synthetic" / "fail-integrity-trace.csv", config)
    early_start_result = analyze(OUT / "synthetic" / "fail-early-start-trace.csv", config)
    require(errors, pass_result["computed_result"] == "PASS", "synthetic pass trace did not pass")
    require(errors, pass_result["run_disposition"].startswith("HOLD"), "synthetic pass escaped qualified hold")
    require(errors, pass_result["release_effect"] == "NONE", "synthetic pass gained release effect")
    metrics = pass_result["event_metrics"]
    require(errors, abs(metrics["total_stop_time_s"] - 0.03) < 1e-12, "synthetic stop time changed")
    require(errors, abs(metrics["residual_travel_deg"] - 0.435) < 1e-9, "synthetic residual travel changed")
    require(errors, abs(metrics["endpoint_clearance_deg"] - 6.065) < 1e-9, "synthetic endpoint clearance changed")
    require(errors, reset_result["computed_result"] == "FAIL", "reset-driven motion fault was not rejected")
    reset_check = next(check for check in reset_result["checks"] if check["check_id"] == "DTA-007")
    require(errors, not reset_check["passed"], "reset interlock fault did not fail DTA-007")
    require(errors, integrity_result["computed_result"] == "FAIL", "data-integrity fault was not rejected")
    integrity_check = next(check for check in integrity_result["checks"] if check["check_id"] == "DTA-001")
    require(errors, not integrity_check["passed"], "data-integrity fault did not fail DTA-001")
    require(errors, early_start_result["computed_result"] == "FAIL", "early separate-start fault was not rejected")
    early_start_check = next(check for check in early_start_result["checks"] if check["check_id"] == "DTA-007")
    require(errors, not early_start_check["passed"] and "distinct_start=False" in early_start_check["detail"], "early start did not fail DTA-007")

    try:
        analyze(OUT / "synthetic" / "pass-trace.csv", OUT / "analysis-config-template.json")
    except AnalysisError as exc:
        require(errors, "remains unresolved" in str(exc), "physical template failed for the wrong reason")
    else:
        errors.append("unresolved physical template was accepted")

    source_rows = read_csv(OUT / "source-register.csv")
    require(errors, len(source_rows) == 4, "source register count changed")
    require(errors, all((ROOT / row["locator"]).exists() for row in source_rows), "source register locator missing")

    disposition = read_csv(ROOT / "tests" / "forms" / "hr-v0-dynamic-trace-disposition-template-p0.1.csv")
    require(errors, len(disposition) == 4, "expected four qualified disposition rows")
    require(errors, all(row["status"] == "NOT EXECUTED" for row in disposition), "disposition evidence was invented")
    require(errors, all(row["decision"] == "HOLD" for row in disposition), "blank disposition lost fail-closed HOLD")
    require(errors, all(row["reviewer"] == "SELECTION REQUIRED" for row in disposition), "reviewer was inferred")

    html = (WEB / "index.html").read_text(encoding="utf-8")
    for token in ("font:16px", "From trace to evidence", "DTA-007", "SELECTION REQUIRED", "release_effect: NONE", "NOT APPROVED"):
        require(errors, token in html, f"interactive guide missing {token!r}")
    require(errors, "font-size:16px" in html, "table text minimum was not declared")
    require(errors, "font-size:" not in html.replace("font-size:clamp", "").replace("font-size:16px", ""), "unexpected fixed font size introduced")

    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    mechanical = next(item for item in release["current_products"] if item.get("domain") == "mechanical")
    require(errors, "HR-V0-DYN-TRACE-P0.1" in mechanical["supporting_identifiers"], "release candidate lacks dynamic trace package")
    require(errors, "physical_evidence_open" in mechanical["release_state"], "mechanical physical-evidence hold lost")
    gates = read_csv(ROOT / "requirements" / "hr-v0-energization-gates.csv")
    gate = next(row for row in gates if row["gate_id"] == "EG-026")
    require(errors, gate["status"] == "partial", "EG-026 must be partial after analysis-path definition")
    require(errors, "dynamic-trace-p0.1" in gate["evidence_location"], "EG-026 lacks R174 evidence path")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 dynamic trace P0.1 check passed: 9 rules; 4 event channels; 4 synthetic traces")
    print("Synthetic pass held; reset-motion, early-start and data-integrity faults rejected; physical acceptance inputs remain unresolved")
    print("PRELIMINARY - NOT APPROVED FOR POWERED TESTING, MOTION, OR ENERGIZATION")


if __name__ == "__main__":
    main()
