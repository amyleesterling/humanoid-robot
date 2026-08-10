#!/usr/bin/env python3
"""Generate the R181 corrected two-run dynamic-trace analysis package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path

from analyze_hr_v0_dynamic_trace_p02 import analyze


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/hr-v0/dynamic-trace-p0.2"
WEB = ROOT / "release/hr-v0/dynamic-trace-analysis-p0.2"
FORMS = ROOT / "tests/forms"
IDENTIFIER = "HR-V0-DYN-TRACE-P0.2"
WARNING = "PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

META_FIELDS = (
    "dropped_scan_count", "sensor_saturation_flags", "run_id",
    "configuration_commit", "article_revision", "calibration_bundle_hash",
    "timing_budget_revision",
)
STOP_FIELDS = (
    "sample_index", "daq_time_s", "stop_event_state", "k1_coil_state",
    "k2_coil_state", "common_edm_chain_state", "k1_aux_status_state",
    "k2_aux_status_state", "source_voltage_V", "external_angle_deg",
    *META_FIELDS,
)
RESET_FIELDS = (
    "sample_index", "daq_time_s", "reset_event_state", "arm_event_state",
    "k1_coil_state", "k2_coil_state", "k1_aux_status_state",
    "k2_aux_status_state", "source_voltage_V", "external_angle_deg",
    *META_FIELDS,
)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def metadata(run_id: str, index: int, integrity_fault: bool = False) -> dict[str, object]:
    return {
        "dropped_scan_count": 1 if integrity_fault and index >= 100 else 0,
        "sensor_saturation_flags": 0,
        "run_id": run_id,
        "configuration_commit": "synthetic-validation-not-hardware",
        "article_revision": "SYNTHETIC-P0.2",
        "calibration_bundle_hash": "synthetic-calibration-not-physical",
        "timing_budget_revision": "SYNTHETIC-TIMING-P0.2",
    }


def make_stop(run_id: str, edm_fault: bool = False, integrity_fault: bool = False, motion_fault: bool = False) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    angle = 110.0
    for index in range(151):
        dt = 0.001
        if motion_fault and 70 <= index < 90:
            angle += 0.003
        row = {
            "sample_index": index + (1 if integrity_fault and index >= 100 else 0),
            "daq_time_s": f"{index * dt:.6f}",
            "stop_event_state": 1 if index >= 50 else 0,
            "k1_coil_state": 1 if index < 55 else 0,
            "k2_coil_state": 1 if index < 56 else 0,
            "common_edm_chain_state": 0 if edm_fault or index < 62 else 1,
            "k1_aux_status_state": 1 if index < 60 else 0,
            "k2_aux_status_state": 1 if index < 61 else 0,
            "source_voltage_V": "24.000000",
            "external_angle_deg": f"{angle:.9f}",
            **metadata(run_id, index, integrity_fault),
        }
        rows.append(row)
    return rows


def make_reset(run_id: str, reset_fault: bool = False) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    angle = 100.0
    for index in range(181):
        reset = 1 if 50 <= index < 60 else 0
        arm = 1 if index >= 120 else 0
        coil = 1 if index >= 125 else 0
        if reset_fault and 70 <= index < 90:
            coil = 1
            angle += 0.003
        row = {
            "sample_index": index,
            "daq_time_s": f"{index * 0.001:.6f}",
            "reset_event_state": reset,
            "arm_event_state": arm,
            "k1_coil_state": coil,
            "k2_coil_state": coil,
            "k1_aux_status_state": 1 if index >= 130 or (reset_fault and 75 <= index < 90) else 0,
            "k2_aux_status_state": 1 if index >= 131 or (reset_fault and 75 <= index < 90) else 0,
            "source_voltage_V": "24.000000",
            "external_angle_deg": f"{angle:.9f}",
            **metadata(run_id, index),
        }
        rows.append(row)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    synthetic = OUT / "synthetic"
    synthetic.mkdir(parents=True, exist_ok=True)

    common_template = {
        "schema": "project-button-hr-v0-dynamic-trace-config-p0.2",
        "status": WARNING,
        "analysis_mode": "PHYSICAL_TRACE",
        "expected_sample_interval_s": "SELECTION REQUIRED",
        "sample_interval_relative_tolerance": "SELECTION REQUIRED",
        "qualified_acceptance_reference": "SELECTION REQUIRED",
    }
    stop_template = {
        **common_template,
        "run_type": "STOP",
        "control_source_valid_min_v": "SELECTION REQUIRED",
        "e2_stop_observation_s": "SELECTION REQUIRED",
        "e2_motion_noise_deg": "SELECTION REQUIRED",
        "maximum_k1_coil_drop_time_s": "SELECTION REQUIRED",
        "maximum_k2_coil_drop_time_s": "SELECTION REQUIRED",
        "maximum_common_edm_close_time_s": "SELECTION REQUIRED",
        "maximum_k1_aux_open_time_s": "SELECTION REQUIRED",
        "maximum_k2_aux_open_time_s": "SELECTION REQUIRED",
    }
    reset_template = {
        **common_template,
        "run_type": "RESET_ARM",
        "minimum_reset_to_arm_interval_s": "SELECTION REQUIRED",
        "reset_motion_noise_deg": "SELECTION REQUIRED",
        "control_source_valid_min_v": "SELECTION REQUIRED",
    }
    stop_synthetic = {
        **stop_template,
        "analysis_mode": "SYNTHETIC_VALIDATION_ONLY",
        "expected_sample_interval_s": 0.001,
        "sample_interval_relative_tolerance": 0.001,
        "control_source_valid_min_v": 20.0,
        "e2_stop_observation_s": 0.050,
        "e2_motion_noise_deg": 0.050,
        "maximum_k1_coil_drop_time_s": 0.020,
        "maximum_k2_coil_drop_time_s": 0.020,
        "maximum_common_edm_close_time_s": 0.025,
        "maximum_k1_aux_open_time_s": 0.025,
        "maximum_k2_aux_open_time_s": 0.025,
        "qualified_acceptance_reference": "SYNTHETIC ALGORITHM TEST ONLY - NO PHYSICAL ACCEPTANCE",
    }
    reset_synthetic = {
        **reset_template,
        "analysis_mode": "SYNTHETIC_VALIDATION_ONLY",
        "expected_sample_interval_s": 0.001,
        "sample_interval_relative_tolerance": 0.001,
        "minimum_reset_to_arm_interval_s": 0.050,
        "reset_motion_noise_deg": 0.050,
        "control_source_valid_min_v": 20.0,
        "qualified_acceptance_reference": "SYNTHETIC ALGORITHM TEST ONLY - NO PHYSICAL ACCEPTANCE",
    }
    (OUT / "stop-config-template.json").write_text(json.dumps(stop_template, indent=2) + "\n", encoding="utf-8")
    (OUT / "reset-arm-config-template.json").write_text(json.dumps(reset_template, indent=2) + "\n", encoding="utf-8")
    (synthetic / "stop-synthetic-config.json").write_text(json.dumps(stop_synthetic, indent=2) + "\n", encoding="utf-8")
    (synthetic / "reset-arm-synthetic-config.json").write_text(json.dumps(reset_synthetic, indent=2) + "\n", encoding="utf-8")
    write_csv(synthetic / "pass-stop-trace.csv", STOP_FIELDS, make_stop("SYN-PASS-STOP-001"))
    write_csv(synthetic / "fail-edm-stop-trace.csv", STOP_FIELDS, make_stop("SYN-FAIL-EDM-001", edm_fault=True))
    write_csv(synthetic / "fail-integrity-stop-trace.csv", STOP_FIELDS, make_stop("SYN-FAIL-INTEGRITY-002", integrity_fault=True))
    write_csv(synthetic / "fail-motion-stop-trace.csv", STOP_FIELDS, make_stop("SYN-FAIL-MOTION-001", motion_fault=True))
    write_csv(synthetic / "pass-reset-arm-trace.csv", RESET_FIELDS, make_reset("SYN-PASS-RESET-001"))
    write_csv(synthetic / "fail-reset-motion-trace.csv", RESET_FIELDS, make_reset("SYN-FAIL-RESET-002", reset_fault=True))
    write_csv(FORMS / "hr-v0-dynamic-stop-trace-template-p0.2.csv", STOP_FIELDS, [])
    write_csv(FORMS / "hr-v0-dynamic-reset-arm-trace-template-p0.2.csv", RESET_FIELDS, [])

    results = {
        "pass-stop-result.json": analyze(synthetic / "pass-stop-trace.csv", synthetic / "stop-synthetic-config.json"),
        "fail-edm-stop-result.json": analyze(synthetic / "fail-edm-stop-trace.csv", synthetic / "stop-synthetic-config.json"),
        "fail-integrity-stop-result.json": analyze(synthetic / "fail-integrity-stop-trace.csv", synthetic / "stop-synthetic-config.json"),
        "fail-motion-stop-result.json": analyze(synthetic / "fail-motion-stop-trace.csv", synthetic / "stop-synthetic-config.json"),
        "pass-reset-arm-result.json": analyze(synthetic / "pass-reset-arm-trace.csv", synthetic / "reset-arm-synthetic-config.json"),
        "fail-reset-motion-result.json": analyze(synthetic / "fail-reset-motion-trace.csv", synthetic / "reset-arm-synthetic-config.json"),
    }
    for name, result in results.items():
        (synthetic / name).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    rules = [
        ("DTA2-001", "sample, timebase, metadata, loss and saturation integrity", "both", "physical timing budget and calibration evidence open"),
        ("DTA2-002", "one controlled STOP or RESET rising edge", "mode-specific", "polarity and threshold evidence open"),
        ("DTA2-003", "STOP: both coils and NO auxiliaries fall while one common EDM chain rises", "STOP", "auxiliaries diagnostic only; contact correlation open"),
        ("DTA2-004", "control source remains valid throughout the E2 observation window", "both", "voltage threshold and measurement uncertainty open"),
        ("DTA2-005", "disconnected-load E2 contains no measured motion", "both", "motion calibration, noise and uncertainty open"),
        ("DTA2-006", "STOP contact and EDM transitions meet accepted time limits", "STOP", "qualified transition-time allocation remains open"),
        ("DTA2-007", "RESET is distinct from ARM and cannot energize coils/auxiliaries or move", "RESET_ARM", "required repetitions and fault cases open"),
        ("DTA2-008", "NO auxiliaries remain diagnostic with zero safety credit", "both", "schema invariant; qualified acceptance still required"),
        ("DTA2-009", "computed PASS remains HOLD", "both", "signed configuration-specific disposition mandatory"),
    ]
    write_csv(OUT / "acceptance-rule-register.csv", ("rule_id", "rule", "run_type", "physical_boundary"), [dict(zip(("rule_id", "rule", "run_type", "physical_boundary"), row)) for row in rules])
    supersessions = [
        {"record_id":"DTSUP-001","superseded":"HR-V0-DYN-TRACE-P0.1 DTA-003","reason":"two mirror channels incorrectly represented one series EDM path as independent contact states","replacement":"DTA2-003: one common EDM-chain rising transition plus two diagnostic NO auxiliary falling transitions","state":"SUPERSEDED FOR CURRENT USE"},
        {"record_id":"DTSUP-002","superseded":"P0.1 single combined trace","reason":"combined STOP and RESET fields exceed the R180 eight-channel simultaneous allocation","replacement":"separate STOP and RESET_ARM trace schemas; no cross-run simultaneity claim","state":"SUPERSEDED FOR CURRENT USE"},
        {"record_id":"DTSUP-003","superseded":"P0.1 external_velocity_deg_s physical channel","reason":"R180 reserves one physical channel for independent angle/displacement","replacement":"velocity derived from the independent angle trace; filter/delay acceptance remains open","state":"SUPERSEDED FOR CURRENT USE"},
    ]
    write_csv(OUT / "supersession-register.csv", tuple(supersessions[0]), supersessions)
    sources = [
        {"source_id":"DTS2-001","source":"R180 event-observation correction","locator":"docs/hr-v0-event-observation-correction-p0.1.md","controlled_use":"one common EDM chain; separate diagnostic auxiliaries; two eight-channel allocations"},
        {"source_id":"DTS2-002","source":"Electrical V3-P1.15 net schedule","locator":"electrical/kicad/project-button-v3-p1.15-carrier-candidate/net-schedule.csv","controlled_use":"K1/K2 NC series topology and individual NO auxiliary nets"},
        {"source_id":"DTS2-003","source":"HR-V0-DYN-TRACE-P0.1","locator":"analysis/hr-v0/dynamic-trace-p0.1/","controlled_use":"historical algorithm and limits; superseded channel semantics"},
    ]
    write_csv(OUT / "source-register.csv", tuple(sources[0]), sources)
    (OUT / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "round": "R181",
        "status": WARNING,
        "physical_run_type_count": 2,
        "physical_channel_count_per_run": 8,
        "synthetic_trace_count": 6,
        "acceptance_rule_count": 9,
        "executed_physical_run_count": 0,
        "released_threshold_count": 0,
        "safety_function_credit": "ZERO",
        "release_effect": "NONE",
    }, indent=2) + "\n", encoding="utf-8")

    cards = "".join(f"<article class='card'><div class='eyebrow'>{escape(row[0])} &middot; {escape(row[2])}</div><h2>{escape(row[1])}</h2><p>{escape(row[3])}</p></article>" for row in rules)
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENTIFIER}</title><style>
:root{{--sky:#dff3ff;--blue:#092e66;--mid:#1267a5;--gold:#f5bd2e;--ink:#10213a;--paper:#fff;--hold:#8a2d0b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main,footer{{max-width:1180px;margin:auto;padding:24px}}.warning{{background:var(--blue);color:#fff;border-bottom:6px solid var(--gold);font-weight:800;padding:16px 24px}}h1{{font-size:clamp(34px,6vw,68px);line-height:1.04;margin:.25em 0}}h2{{font-size:23px;line-height:1.2}}h1,h2,p,.eyebrow{{overflow-wrap:anywhere}}.lead{{font-size:20px;max-width:900px}}.correction{{background:#fff4c7;border-left:8px solid var(--gold);padding:20px;margin:24px 0;font-size:18px}}.runs{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:24px 0}}.run,.card{{min-width:0;background:#fff;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--blue)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.eyebrow{{font-size:14px;font-weight:800;color:var(--mid);text-transform:uppercase;letter-spacing:.04em}}.held{{color:var(--hold);font-weight:900}}footer{{font-size:14px}}@media(max-width:650px){{header,main,footer{{padding:18px}}.runs,.grid{{grid-template-columns:minmax(0,1fr)}}}}
</style></head><body><div class='warning'>{WARNING}</div><header><div class='eyebrow'>R181 &middot; {IDENTIFIER}</div><h1>Two valid eight-channel E2 runs. No powered-motion claim.</h1><p class='lead'>P0.2 makes the analyzer match the disconnected-load commissioning boundary: STOP and RESET/ARM are separate simultaneous runs, the control source stays valid, and the same series EDM current is never counted twice.</p></header><main><div class='correction'><strong>Controlled correction:</strong> during E2 STOP, both coils and diagnostic NO auxiliaries fall while the one common NC-mirror EDM chain closes and no motion occurs. During RESET/ARM, RESET must remain distinct from ARM and must not energize either coil or cause measured motion while the control source is valid.</div><div class='runs'><section class='run'><div class='eyebrow'>E2 STOP &middot; 8 inputs</div><h2>Event + 2 coils + common EDM + 2 diagnostics + control source + motion</h2><p>The actuator source remains physically absent. This run can bound control/contact transitions and no-motion behavior; it cannot prove powered stopping time, travel or clearance.</p></section><section class='run'><div class='eyebrow'>RESET/ARM &middot; 8 inputs</div><h2>RESET + ARM + 2 coils + 2 diagnostics + control source + motion</h2><p>The no-motion window ends only at a distinct later ARM edge. Separate runs do not prove cross-run simultaneity.</p></section></div><h2>Nine fail-closed rules</h2><div class='grid'>{cards}</div><p class='held'>Six synthetic traces test code paths only. Zero physical runs, released limits, safety credit or work authority exist.</p></main><footer>{WARNING}</footer></body></html>"""
    (WEB / "index.html").write_text(html, encoding="utf-8")
    print(f"generated {IDENTIFIER}: 2 run types; 8 channels each; 6 synthetic traces; 0 physical runs")
    print(WARNING)


if __name__ == "__main__":
    main()
