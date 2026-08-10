#!/usr/bin/env python3
"""Check the R181 corrected two-run dynamic-trace analysis package."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from analyze_hr_v0_dynamic_trace_p02 import AnalysisError, analyze


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/hr-v0/dynamic-trace-p0.2"
WEB = ROOT / "release/hr-v0/dynamic-trace-analysis-p0.2/index.html"
FORMS = ROOT / "tests/forms"
WARNING = "PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rules = read_csv("acceptance-rule-register.csv")
    supersessions = read_csv("supersession-register.csv")
    sources = read_csv("source-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    html = WEB.read_text(encoding="utf-8")
    synthetic = OUT / "synthetic"

    assert len(rules) == 9 and {row["rule_id"] for row in rules} == {f"DTA2-00{i}" for i in range(1, 10)}
    assert len(supersessions) == 3 and all(row["state"] == "SUPERSEDED FOR CURRENT USE" for row in supersessions)
    assert len(sources) == 3
    assert status["physical_run_type_count"] == 2
    assert status["physical_channel_count_per_run"] == 8
    assert status["synthetic_trace_count"] == 6
    assert status["executed_physical_run_count"] == 0
    assert status["released_threshold_count"] == 0
    assert status["safety_function_credit"] == "ZERO"

    stop_header = (FORMS / "hr-v0-dynamic-stop-trace-template-p0.2.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    reset_header = (FORMS / "hr-v0-dynamic-reset-arm-trace-template-p0.2.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    assert len(stop_header) == 17 and len(reset_header) == 17
    assert "common_edm_chain_state" in stop_header
    assert "k1_mirror_state" not in stop_header and "k2_mirror_state" not in stop_header
    assert "reset_event_state" in reset_header and "arm_event_state" in reset_header
    assert "common_edm_chain_state" not in reset_header

    cases = {
        "pass-stop": ("pass-stop-trace.csv", "stop-synthetic-config.json", "PASS"),
        "fail-edm": ("fail-edm-stop-trace.csv", "stop-synthetic-config.json", "FAIL"),
        "fail-integrity": ("fail-integrity-stop-trace.csv", "stop-synthetic-config.json", "FAIL"),
        "fail-motion": ("fail-motion-stop-trace.csv", "stop-synthetic-config.json", "FAIL"),
        "pass-reset": ("pass-reset-arm-trace.csv", "reset-arm-synthetic-config.json", "PASS"),
        "fail-reset": ("fail-reset-motion-trace.csv", "reset-arm-synthetic-config.json", "FAIL"),
    }
    for name, (trace, config, expected) in cases.items():
        result = analyze(synthetic / trace, synthetic / config)
        assert result["computed_result"] == expected, name
        assert result["release_effect"] == "NONE"
        assert any("zero safety-function credit" in item for item in result["interpretation_limits"])
        stored_name = {
            "pass-stop": "pass-stop-result.json", "fail-edm": "fail-edm-stop-result.json",
            "fail-integrity": "fail-integrity-stop-result.json", "pass-reset": "pass-reset-arm-result.json",
            "fail-motion": "fail-motion-stop-result.json",
            "fail-reset": "fail-reset-motion-result.json",
        }[name]
        stored = json.loads((synthetic / stored_name).read_text(encoding="utf-8"))
        assert stored == result

    stop_result = analyze(synthetic / "pass-stop-trace.csv", synthetic / "stop-synthetic-config.json")
    dta3 = next(row for row in stop_result["checks"] if row["check_id"] == "DTA2-003")
    assert dta3["passed"] and "common_edm_rising" in dta3["detail"] and "auxiliaries_diagnostic_only=true" in dta3["detail"]
    reset_result = analyze(synthetic / "pass-reset-arm-trace.csv", synthetic / "reset-arm-synthetic-config.json")
    dta7 = next(row for row in reset_result["checks"] if row["check_id"] == "DTA2-007")
    assert dta7["passed"] and "interval_ok=True" in dta7["detail"]

    for template, trace in (("stop-config-template.json", "pass-stop-trace.csv"), ("reset-arm-config-template.json", "pass-reset-arm-trace.csv")):
        try:
            analyze(synthetic / trace, OUT / template)
        except AnalysisError as exc:
            assert "configuration remains unresolved" in str(exc)
        else:
            raise AssertionError(f"physical template unexpectedly accepted: {template}")

    assert "font:16px/1.55" in html and "font-size:14px" in html
    assert "font-size:13px" not in html and "font-size:12px" not in html
    assert html.count("class='card'") == 9
    assert "No powered-motion claim" in html
    assert WARNING in html and "Zero physical runs" in html and "Six synthetic traces" in html
    print("PASS: R181 corrected two-run dynamic-trace analysis")
    print("2 eight-channel run types; 6 synthetic traces; 9 rules; 0 physical runs; 0 safety credit")
    print(WARNING)


if __name__ == "__main__":
    main()
