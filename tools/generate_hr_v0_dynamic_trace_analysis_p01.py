from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "hr-v0" / "dynamic-trace-p0.1"
WEB = ROOT / "release" / "hr-v0" / "dynamic-trace-analysis-p0.1"
REVISION = "HR-V0-DYN-TRACE-P0.1"
WARNING = (
    "PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - "
    "NOT APPROVED FOR POWERED TESTING, MOTION, OR ENERGIZATION"
)

TRACE_FIELDS = (
    "sample_index",
    "daq_time_s",
    "trigger_state",
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
)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_trace(run_id: str, reset_fault: bool = False, integrity_fault: bool = False, early_start_fault: bool = False) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    angle = 110.0
    dt = 0.001
    for index in range(251):
        time_s = round(index * dt, 6)
        if index < 50:
            velocity = 30.0
        elif index <= 80:
            velocity = max(0.0, 30.0 * (80 - index) / 30.0)
        elif index >= 190:
            velocity = 5.0
        else:
            velocity = 0.0
        if index:
            angle += velocity * dt
        stop = 1 if 50 <= index < 110 else 0
        reset = 1 if 120 <= index < 130 else 0
        start = 1 if index >= (125 if early_start_fault else 180) else 0
        motion_enable = 1 if index < 52 or index >= 185 else 0
        torque_enable = 1 if index < 57 or index >= 185 else 0
        k1 = 1 if index < 55 or index >= 185 else 0
        k2 = 1 if index < 56 or index >= 185 else 0
        m1 = 1 if index < 60 or index >= 185 else 0
        m2 = 1 if index < 61 or index >= 185 else 0
        if reset_fault and 121 <= index < 140:
            motion_enable = torque_enable = k1 = k2 = 1
            angle += 0.01
        if index < 56:
            voltage = 24.0
        elif index < 70:
            voltage = 24.0 * (70 - index) / 14.0
        else:
            voltage = 0.0 if index < 185 else 24.0
        current = 1.2 if index < 50 else max(-0.4, 1.2 - 0.08 * (index - 50))
        if index >= 80:
            current = 0.0 if index < 185 else 0.3
        row = {
            "sample_index": index + (1 if integrity_fault and index >= 100 else 0),
            "daq_time_s": f"{time_s:.6f}",
            "trigger_state": 1 if index >= 50 else 0,
            "stop_command_state": stop,
            "estop_state": stop,
            "reset_input_state": reset,
            "start_command_state": start,
            "motion_enable_command_state": motion_enable,
            "torque_enable_feedback": torque_enable,
            "source_voltage_V": f"{voltage:.6f}",
            "source_current_A": f"{current:.6f}",
            "k1_coil_state": k1,
            "k2_coil_state": k2,
            "k1_mirror_state": m1,
            "k2_mirror_state": m2,
            "external_angle_deg": f"{angle:.9f}",
            "external_velocity_deg_s": f"{velocity:.6f}",
            "reaction_force_N": "0.000000",
            "bumper_displacement_mm": "0.000000",
            "dropped_scan_count": 1 if integrity_fault and index >= 100 else 0,
            "sensor_saturation_flags": 0,
            "run_id": run_id,
            "configuration_commit": "synthetic-validation-not-hardware",
            "article_revision": "SYNTHETIC-P0.1",
            "calibration_bundle_hash": "synthetic-calibration-not-physical",
            "timing_budget_revision": "SYNTHETIC-TIMING-P0.1",
        }
        rows.append(row)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    synthetic = OUT / "synthetic"
    synthetic.mkdir(parents=True, exist_ok=True)

    template_config = {
        "schema": "project-button-hr-v0-dynamic-trace-config-p0.1",
        "status": WARNING,
        "analysis_mode": "PHYSICAL_TRACE",
        "stop_event_field": "SELECTION REQUIRED",
        "motion_direction": "SELECTION REQUIRED",
        "expected_sample_interval_s": "SELECTION REQUIRED",
        "sample_interval_relative_tolerance": "SELECTION REQUIRED",
        "stop_velocity_threshold_deg_s": "SELECTION REQUIRED",
        "stop_dwell_s": "SELECTION REQUIRED",
        "stop_angle_band_deg": "SELECTION REQUIRED",
        "rail_below_torque_threshold_v": "SELECTION REQUIRED",
        "rail_dwell_s": "SELECTION REQUIRED",
        "maximum_total_stop_time_s": "SELECTION REQUIRED",
        "maximum_residual_travel_deg": "SELECTION REQUIRED",
        "hard_stop_angle_deg": "SELECTION REQUIRED",
        "minimum_endpoint_clearance_deg": "SELECTION REQUIRED",
        "reset_observation_s": "SELECTION REQUIRED",
        "reset_motion_noise_deg": "SELECTION REQUIRED",
        "qualified_acceptance_reference": "SELECTION REQUIRED",
    }
    synthetic_config = {
        **template_config,
        "analysis_mode": "SYNTHETIC_VALIDATION_ONLY",
        "stop_event_field": "estop_state",
        "motion_direction": "POSITIVE",
        "expected_sample_interval_s": 0.001,
        "sample_interval_relative_tolerance": 0.001,
        "stop_velocity_threshold_deg_s": 0.5,
        "stop_dwell_s": 0.010,
        "stop_angle_band_deg": 0.010,
        "rail_below_torque_threshold_v": 4.0,
        "rail_dwell_s": 0.005,
        "maximum_total_stop_time_s": 0.050,
        "maximum_residual_travel_deg": 0.600,
        "hard_stop_angle_deg": 118.0,
        "minimum_endpoint_clearance_deg": 3.0,
        "reset_observation_s": 0.050,
        "reset_motion_noise_deg": 0.050,
        "qualified_acceptance_reference": "SYNTHETIC ALGORITHM TEST ONLY - NO PHYSICAL ACCEPTANCE",
    }
    (OUT / "analysis-config-template.json").write_text(json.dumps(template_config, indent=2) + "\n", encoding="utf-8")
    (synthetic / "synthetic-config.json").write_text(json.dumps(synthetic_config, indent=2) + "\n", encoding="utf-8")
    write_csv(synthetic / "pass-trace.csv", TRACE_FIELDS, make_trace("SYN-PASS-001"))
    write_csv(synthetic / "fail-reset-trace.csv", TRACE_FIELDS, make_trace("SYN-FAIL-RESET-001", reset_fault=True))
    write_csv(synthetic / "fail-integrity-trace.csv", TRACE_FIELDS, make_trace("SYN-FAIL-INTEGRITY-001", integrity_fault=True))
    write_csv(synthetic / "fail-early-start-trace.csv", TRACE_FIELDS, make_trace("SYN-FAIL-EARLY-START-001", early_start_fault=True))

    extensions = [
        {"channel_id":"DCH-X01","field_name":"reset_input_state","type":"boolean","purpose":"monitored reset edge on common DAQ timebase","acceptance_boundary":"reset alone shall not energize K1/K2 enable torque or cause motion","state":"INTERFACE REQUIRED"},
        {"channel_id":"DCH-X02","field_name":"start_command_state","type":"boolean","purpose":"separate deliberate start edge on common DAQ timebase","acceptance_boundary":"must remain distinct from reset","state":"INTERFACE REQUIRED"},
        {"channel_id":"DCH-X03","field_name":"motion_enable_command_state","type":"boolean","purpose":"supervisor motion request witness","acceptance_boundary":"shall remain false in reset observation window","state":"INTERFACE REQUIRED"},
        {"channel_id":"DCH-X04","field_name":"torque_enable_feedback","type":"boolean","purpose":"actuator torque-enable state witness","acceptance_boundary":"shall remain false in reset observation window","state":"INTERFACE REQUIRED"},
    ]
    write_csv(OUT / "event-channel-extension.csv", tuple(extensions[0]), extensions)

    rules = [
        {"rule_id":"DTA-001","rule":"Sample index timebase metadata loss and saturation integrity","computed_output":"integrity pass/fail","physical_acceptance_input":"accepted timing budget calibration hashes and zero unexplained loss","state":"PHYSICAL ACCEPTANCE INPUT OPEN"},
        {"rule_id":"DTA-002","rule":"Exactly controlled rising stop-event edge","computed_output":"stop edge time","physical_acceptance_input":"selected isolated event channel and polarity proof","state":"PHYSICAL ACCEPTANCE INPUT OPEN"},
        {"rule_id":"DTA-003","rule":"Both coil commands and both mirror channels open after event","computed_output":"four edge times","physical_acceptance_input":"contact bounce propagation and pole-state correlation","state":"PHYSICAL ACCEPTANCE INPUT OPEN"},
        {"rule_id":"DTA-004","rule":"Measured source rail remains below selected torque threshold","computed_output":"rail threshold time","physical_acceptance_input":"actuator-specific torque-loss voltage and dwell","state":"SELECTION REQUIRED"},
        {"rule_id":"DTA-005","rule":"Independent angle and velocity satisfy sustained stop window","computed_output":"motion-stop time","physical_acceptance_input":"noise filter delay dwell and uncertainty","state":"SELECTION REQUIRED"},
        {"rule_id":"DTA-006","rule":"Time travel and endpoint clearance each meet configuration limits","computed_output":"three bounded metrics","physical_acceptance_input":"qualified safety-function allocation and guard/stop reconciliation","state":"SELECTION REQUIRED"},
        {"rule_id":"DTA-007","rule":"Reset observation contains no coil torque-enable motion request or measured motion before separate start","computed_output":"reset interlock pass/fail","physical_acceptance_input":"complete reset/start channel proof and required repetitions/fault cases","state":"PHYSICAL ACCEPTANCE INPUT OPEN"},
        {"rule_id":"DTA-008","rule":"Peak current force displacement and positive compression work reported without rating credit","computed_output":"range metrics","physical_acceptance_input":"calibration uncertainty structural and absorber application acceptance","state":"PHYSICAL ACCEPTANCE INPUT OPEN"},
        {"rule_id":"DTA-009","rule":"Computed pass remains HOLD pending qualified disposition","computed_output":"release effect NONE","physical_acceptance_input":"named competent reviewers signed configuration-specific record","state":"MANDATORY HOLD"},
    ]
    write_csv(OUT / "acceptance-rule-register.csv", tuple(rules[0]), rules)

    sources = [
        {"source_id":"DTS-001","source":"HR-V0-DYN-CHAR-P0.1","locator":"docs/hr-v0-dynamic-characterization-p0.1.md","controlled_use":"15-channel measurement architecture and raw-data evidence boundary"},
        {"source_id":"DTS-002","source":"HR-V0-STOP-BUDGET-P0.1","locator":"docs/hr-v0-stopping-budget-p0.1.md","controlled_use":"3-degree positive J2 approach and unresolved total-stop allocation"},
        {"source_id":"DTS-003","source":"R173 fabrication input reconciliation","locator":"release/hr-v0/fabrication-input-basis-p0.1/kinematic-screens.csv","controlled_use":"draft 10/30 deg/s limits and 0.15 m/s TCP constraint reconciliation"},
        {"source_id":"DTS-004","source":"HR-V0 electrical P1.15 candidate","locator":"electrical/kicad/project-button-v3/","controlled_use":"K1 K2 event and mirror signal identities; ECAD connectivity only"},
    ]
    write_csv(OUT / "source-register.csv", tuple(sources[0]), sources)

    status = {
        "identifier": REVISION,
        "status": WARNING,
        "physical_trace_config_state": "ALL NUMERIC ACCEPTANCE INPUTS SELECTION REQUIRED",
        "synthetic_trace_count": 4,
        "acceptance_rule_count": len(rules),
        "event_channel_extension_count": len(extensions),
        "executed_physical_run_count": 0,
        "authorized_powered_run_count": 0,
        "release_effect": "NONE",
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    disposition_rows = [
        {"record_id":"DTR-DISP-001","run_id":"","trace_sha256":"","config_sha256":"","result_sha256":"","discipline":"electrical","reviewer":"SELECTION REQUIRED","competence_evidence":"SELECTION REQUIRED","independence_evidence":"SELECTION REQUIRED","decision":"HOLD","signature":"","date":"","status":"NOT EXECUTED","warning":WARNING},
        {"record_id":"DTR-DISP-002","run_id":"","trace_sha256":"","config_sha256":"","result_sha256":"","discipline":"mechanical","reviewer":"SELECTION REQUIRED","competence_evidence":"SELECTION REQUIRED","independence_evidence":"SELECTION REQUIRED","decision":"HOLD","signature":"","date":"","status":"NOT EXECUTED","warning":WARNING},
        {"record_id":"DTR-DISP-003","run_id":"","trace_sha256":"","config_sha256":"","result_sha256":"","discipline":"functional_safety","reviewer":"SELECTION REQUIRED","competence_evidence":"SELECTION REQUIRED","independence_evidence":"SELECTION REQUIRED","decision":"HOLD","signature":"","date":"","status":"NOT EXECUTED","warning":WARNING},
        {"record_id":"DTR-DISP-004","run_id":"","trace_sha256":"","config_sha256":"","result_sha256":"","discipline":"independent_test_witness","reviewer":"SELECTION REQUIRED","competence_evidence":"SELECTION REQUIRED","independence_evidence":"SELECTION REQUIRED","decision":"HOLD","signature":"","date":"","status":"NOT EXECUTED","warning":WARNING},
    ]
    write_csv(
        ROOT / "tests" / "forms" / "hr-v0-dynamic-trace-disposition-template-p0.1.csv",
        tuple(disposition_rows[0]),
        disposition_rows,
    )

    rule_rows = "".join(
        f"<tr data-state='{row['state']}'><td>{row['rule_id']}</td><td>{row['rule']}</td><td>{row['computed_output']}</td><td>{row['state']}</td></tr>"
        for row in rules
    )
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{REVISION}</title><style>
:root{{--ink:#09264d;--blue:#125e9b;--sky:#d9f1ff;--gold:#f2b91f;--paper:#f7fbff;--danger:#861d2c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}header,main{{padding:24px}}header>div,main{{max-width:1180px;margin:auto}}header{{background:var(--ink);color:#fff;border-bottom:8px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.05;margin:.25rem 0}}h2{{font-size:clamp(24px,3vw,34px)}}.warning{{background:#fff2bd;border:3px solid var(--gold);padding:16px;font-weight:800}}.flow{{display:grid;grid-template-columns:repeat(5,minmax(150px,1fr));gap:12px}}.flow div,.card{{background:#fff;border:2px solid #9ac8e8;border-radius:12px;padding:18px;box-shadow:0 4px 0 #cae8fa}}.arrow{{font-weight:800;color:var(--blue)}}.tablewrap{{overflow-x:auto;border:2px solid #9ac8e8;border-radius:12px;background:#fff}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:14px;text-align:left;border-bottom:1px solid #bad9ed;font-size:16px;vertical-align:top}}th{{background:var(--sky)}}code{{font-size:16px}}.danger{{color:var(--danger);font-weight:800}}@media(max-width:820px){{header,main{{padding:18px}}.flow{{grid-template-columns:1fr}}h1,p,td{{overflow-wrap:anywhere}}}}
</style></head><body><header><div><p>PROJECT BUTTON / R174</p><h1>From trace to evidence</h1><p>A deterministic, fail-closed analysis path for stopping and reset behavior.</p></div></header><main><p class='warning'>{WARNING}</p>
<section><h2>Evidence flow</h2><div class='flow'><div>1. Common-clock raw trace</div><div><span class='arrow'>2.</span> Integrity checks</div><div><span class='arrow'>3.</span> Event edges</div><div><span class='arrow'>4.</span> Time, travel and reset checks</div><div><span class='arrow'>5.</span> HOLD for qualified disposition</div></div></section>
<section class='card'><h2>What changed</h2><p>The R78 channel plan now has an executable analysis contract. It detects stop, coil, mirror, rail and motion-stop events; verifies residual travel and endpoint clearance; and explicitly rejects reset-driven re-energization or motion before a separate start command.</p><p class='danger'>The numeric values in the synthetic configuration test the algorithm only. Every physical-run value remains SELECTION REQUIRED.</p></section>
<h2>Acceptance rules</h2><div class='tablewrap'><table><thead><tr><th>ID</th><th>Rule</th><th>Output</th><th>State</th></tr></thead><tbody>{rule_rows}</tbody></table></div>
<section class='card'><h2>Run locally</h2><p><code>python tools/analyze_hr_v0_dynamic_trace_p01.py TRACE.csv CONFIG.json --output RESULT.json</code></p><p>A computed PASS still has <code>release_effect: NONE</code> and <code>run_disposition: HOLD - QUALIFIED REVIEW REQUIRED</code>.</p></section></main></body></html>"""
    (WEB / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated {REVISION}: {len(rules)} rules; {len(extensions)} event channels; 4 synthetic traces")
    print(WARNING)


if __name__ == "__main__":
    main()
