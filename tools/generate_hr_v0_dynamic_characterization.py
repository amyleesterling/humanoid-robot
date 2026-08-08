from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures" / "hr-v0" / "dynamic-characterization-p0.1"
REVISION = "HR-V0-DYN-CHAR-P0.1"
WARNING = (
    "PRELIMINARY - MEASUREMENT AND FIXTURE INPUT ONLY - NOT APPROVED FOR POWERED "
    "TESTING, MOTION, CONNECTION, OR ENERGIZATION"
)


def write_csv(name: str, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    channels = [
        {"channel_id":"DCH-001","quantity":"common hardware trigger","primary_or_supplemental":"PRIMARY","method":"DAQ digital input plus visible LED in video","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"electrical edge-to-video proof","timing_credit":"YES only after DTE-001 through DTE-008 close","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-002","quantity":"independent joint angle","primary_or_supplemental":"PRIMARY","method":"external encoder or optical tracker independent of DYNAMIXEL","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"traceable angle calibration and installed zero check","timing_credit":"YES only after installed dynamic calibration","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-003","quantity":"independent joint velocity","primary_or_supplemental":"DERIVED PRIMARY","method":"validated derivative of DCH-002 with declared filter","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"synthetic-signal and known-motion validation","timing_credit":"YES only with filter delay in error budget","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-004","quantity":"bidirectional actuator-branch current","primary_or_supplemental":"PRIMARY","method":"isolated or appropriately referenced external transducer including regeneration polarity","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"zero plus positive and negative current calibration","timing_credit":"YES only after transducer delay proof","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-005","quantity":"actuator-source bus voltage","primary_or_supplemental":"PRIMARY","method":"differential isolated or qualified divider/interface","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"traceable DC and dynamic cross-check","timing_credit":"YES only after interface delay proof","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-006","quantity":"reaction force","primary_or_supplemental":"PRIMARY","method":"sensor in released fixture reaction path","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"traceable multi-point loading in installed direction","timing_credit":"YES only after installed ringing/delay characterization","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-007","quantity":"bumper displacement","primary_or_supplemental":"PRIMARY","method":"independent noncontact or contact displacement transducer","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"traceable travel calibration and alignment check","timing_credit":"YES only after installed proof","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-008","quantity":"K1 coil command","primary_or_supplemental":"PRIMARY","method":"isolated digital monitor at released test point","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"logic-state injection and isolation proof","timing_credit":"YES after propagation delay measured","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-009","quantity":"K2 coil command","primary_or_supplemental":"PRIMARY","method":"isolated digital monitor at released test point","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"logic-state injection and isolation proof","timing_credit":"YES after propagation delay measured","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-010","quantity":"K1 mirror feedback","primary_or_supplemental":"PRIMARY","method":"isolated digital monitor at released test point","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"contact-state injection and isolation proof","timing_credit":"YES after propagation and contact-bounce characterization","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-011","quantity":"K2 mirror feedback","primary_or_supplemental":"PRIMARY","method":"isolated digital monitor at released test point","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"contact-state injection and isolation proof","timing_credit":"YES after propagation and contact-bounce characterization","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-012","quantity":"high-speed video","primary_or_supplemental":"PRIMARY CORROBORATION","method":"camera viewing article scale marks trigger LED and containment","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"frame-rate shutter scale and trigger-latency proof","timing_credit":"YES only after dropped/duplicated-frame check","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-013","quantity":"DYNAMIXEL Realtime Tick position velocity current voltage temperature","primary_or_supplemental":"SUPPLEMENTAL ONLY","method":"U2D2 host polling or bulk read","range_bandwidth_resolution":"manufacturer register units","calibration_or_proof":"register decoding and rollover/reset handling","timing_credit":"NO primary stop-time impact-force or energy credit","selection_state":"DEFINED SUPPLEMENTAL CHANNEL"},
        {"channel_id":"DCH-014","quantity":"operator stop command and E-stop event","primary_or_supplemental":"PRIMARY","method":"isolated hardware edge captured by the same DAQ scan","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"edge injection at each released source","timing_credit":"YES after input-chain delay proof","selection_state":"SELECTION REQUIRED"},
        {"channel_id":"DCH-015","quantity":"DAQ sample clock or SPC witness","primary_or_supplemental":"PRIMARY METADATA","method":"scope or counter witness of actual sample timing","range_bandwidth_resolution":"SELECTION REQUIRED","calibration_or_proof":"run-start and run-end clock verification","timing_credit":"YES; mandatory for timing evidence","selection_state":"SELECTION REQUIRED"},
    ]
    write_csv("measurement-channel-register.csv", tuple(channels[0]), channels)

    daq = [
        {"screen_id":"DAQ-001","candidate":"LabJack T7 base model","verified_capability":"14 analog inputs; USB and Ethernet; hardware-timed stream","official_limit_or_fact":"T7 typical maximum 100 ksamples/s at +/-10 V and resolution index 0 or 1","project_disposition":"EVALUATION CANDIDATE ONLY; not selected"},
        {"screen_id":"DAQ-002","candidate":"T7 eight-address +/-10 V stream","verified_capability":"12.5 kscans/s table value at resolution index 1","official_limit_or_fact":"scan rate equals sample rate divided by address count","project_disposition":"MANUFACTURER SCREEN ONLY; actual channel list and rate SELECTION REQUIRED"},
        {"screen_id":"DAQ-003","candidate":"T7 scan timing","verified_capability":"hardware-timed constant scan pulses","official_limit_or_fact":"scan addresses are sampled sequentially after each clock pulse","project_disposition":"interchannel skew must be measured and included"},
        {"screen_id":"DAQ-004","candidate":"T7 triggered stream","verified_capability":"stream start can use a DIO_EF trigger","official_limit_or_fact":"T7 minimum firmware 1.0186 for triggered stream","project_disposition":"received firmware and edge latency must be recorded"},
        {"screen_id":"DAQ-005","candidate":"T7 externally clocked stream","verified_capability":"external scan clock on CIO3","official_limit_or_fact":"normal stream-rate limits still apply","project_disposition":"candidate synchronization route; not required or released"},
        {"screen_id":"DAQ-006","candidate":"T7-Pro","verified_capability":"extra high-resolution ADC exists","official_limit_or_fact":"high-resolution ADC indices 9-12 are model-specific and not a reason to infer stream performance","project_disposition":"NO PREFERENCE OR SELECTION; base T7 remains sufficient for evaluation"},
    ]
    write_csv("daq-candidate-screen.csv", tuple(daq[0]), daq)

    fixture = [
        {"control_id":"DFC-001","control":"Test one joint axis and one released article configuration at a time.","evidence_required":"configuration photo and serialized article record","state":"NOT EXECUTED"},
        {"control_id":"DFC-002","control":"Use the P0.7 joint geometry and exact received interfaces; do not substitute the full arm before single-axis closure.","evidence_required":"received-interface inspection and configuration hash","state":"NOT EXECUTED"},
        {"control_id":"DFC-003","control":"Rigidly anchor the fixture to a surveyed bench with a separate secondary restraint or catch.","evidence_required":"bench survey anchor calculation proof load and installed inspection","state":"SELECTION REQUIRED"},
        {"control_id":"DFC-004","control":"The outer guard may contain debris but shall not carry intended fixture reaction loads.","evidence_required":"independent load path drawing and inspection","state":"DESIGN REQUIRED"},
        {"control_id":"DFC-005","control":"Measure every inertial surrogate mass COM and attachment before use.","evidence_required":"traceable scale and balance record plus attachment inspection","state":"NOT EXECUTED"},
        {"control_id":"DFC-006","control":"Select force sensor overload capacity stiffness mounting and orientation from a bounded load case.","evidence_required":"released sensor/interface calculation and calibration","state":"SELECTION REQUIRED"},
        {"control_id":"DFC-007","control":"Keep all people outside the containment envelope and operate remotely with the E-stop reachable outside the hazard.","evidence_required":"approved layout work control and witnessed dry run","state":"NOT AUTHORIZED"},
        {"control_id":"DFC-008","control":"Use physical source current and voltage limiting independent of motion software.","evidence_required":"exact source protection settings and measured open-circuit behavior","state":"SELECTION REQUIRED"},
        {"control_id":"DFC-009","control":"Inspect fasteners witness marks cables stop bumper and sensor preload before and after every increment.","evidence_required":"signed pre/post inspection rows","state":"NOT EXECUTED"},
        {"control_id":"DFC-010","control":"Abort on unexpected motion noise heat smoke data loss fixture shift sensor saturation or guard contact.","evidence_required":"written abort criteria and recorded run disposition","state":"OPEN"},
        {"control_id":"DFC-011","control":"Do not infer safe limits from a catalog stall/no-load endpoint or a single successful run.","evidence_required":"qualified test plan with repetition and uncertainty treatment","state":"HOLD"},
        {"control_id":"DFC-012","control":"No powered stage may execute until its existing E2 E3 or E4 gate and written authorization are satisfied.","evidence_required":"configuration-specific signed authorization","state":"NOT AUTHORIZED"},
    ]
    write_csv("fixture-interface-controls.csv", tuple(fixture[0]), fixture)

    sequence = [
        {"stage_id":"DYN-00","stage":"configuration freeze","minimum_inputs":"immutable commit article serials instrument list and qualified test draft","authorization_gate":"E0/E1 prerequisites","execution_state":"NOT EXECUTED","stop_rule":"any mismatch or missing record"},
        {"stage_id":"DYN-01","stage":"unpowered mass COM and surrogate inertia input","minimum_inputs":"measured article and surrogate mass COM geometry","authorization_gate":"E1 work control","execution_state":"NOT EXECUTED","stop_rule":"unbounded attachment or measurement uncertainty"},
        {"stage_id":"DYN-02","stage":"fixture load-path and restraint proof","minimum_inputs":"bench anchor load path secondary catch and guard independence","authorization_gate":"EG-005 through EG-008 evidence","execution_state":"NOT EXECUTED","stop_rule":"shift damage permanent set or guard load"},
        {"stage_id":"DYN-03","stage":"installed sensor calibration","minimum_inputs":"all primary channels installed ranges overload protection calibration refs","authorization_gate":"qualified metrology review","execution_state":"NOT EXECUTED","stop_rule":"saturation drift polarity error or expired calibration"},
        {"stage_id":"DYN-04","stage":"synchronization injection","minimum_inputs":"common hardware edge DAQ clock witness and video trigger","authorization_gate":"unpowered instrumentation work control","execution_state":"NOT EXECUTED","stop_rule":"timing budget or data-integrity acceptance not released"},
        {"stage_id":"DYN-05","stage":"unpowered dry run","minimum_inputs":"remote operation abort recovery and inspection rehearsal","authorization_gate":"approved test-area work control","execution_state":"NOT EXECUTED","stop_rule":"person enters envelope or recovery is ambiguous"},
        {"stage_id":"DYN-06","stage":"actuator source open-circuit characterization","minimum_inputs":"source only no actuator branch connected","authorization_gate":"EG-019 through EG-023 plus written E3 authorization","execution_state":"NOT AUTHORIZED","stop_rule":"unexpected voltage ripple discharge or source interaction"},
        {"stage_id":"DYN-07","stage":"single unloaded actuator holding at lowest released limit","minimum_inputs":"received actuator branch protection and primary instrumentation","authorization_gate":"EG-023 and EG-024 plus written E4 authorization","execution_state":"NOT AUTHORIZED","stop_rule":"unexpected motion current heat communication or data behavior"},
        {"stage_id":"DYN-08","stage":"low-speed no-contact motion","minimum_inputs":"released current speed angle and travel bounds","authorization_gate":"EG-025 plus written E4 authorization","execution_state":"NOT AUTHORIZED","stop_rule":"any limit approach overshoot data loss or fixture shift"},
        {"stage_id":"DYN-09","stage":"torque-off and source-removal response","minimum_inputs":"released poses loads repetitions and trigger definitions","authorization_gate":"EG-025 plus qualified test authorization","execution_state":"NOT AUTHORIZED","stop_rule":"containment or timing anomaly"},
        {"stage_id":"DYN-10","stage":"lowest released bumper-contact energy","minimum_inputs":"selected bumper force chain proof energy and acceptance criteria","authorization_gate":"EG-026 and EG-028 test authorization","execution_state":"NOT AUTHORIZED","stop_rule":"damage permanent set rebound escape or acceptance exceedance"},
        {"stage_id":"DYN-11","stage":"released pose load and fault matrix","minimum_inputs":"approved statistical plan single faults and guard reconciliation","authorization_gate":"EG-026 through EG-030","execution_state":"NOT AUTHORIZED","stop_rule":"any deviation or unbounded result"},
    ]
    write_csv("dynamic-test-sequence.csv", tuple(sequence[0]), sequence)

    timing = [
        {"evidence_id":"DTE-001","quantity":"DAQ scan rate and complete scan list","required_record":"requested and measured rate every address and ordering","acceptance_value":"SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-002","quantity":"interchannel delay and jitter","required_record":"scope/SPC or common-edge measurement on received DAQ","acceptance_value":"SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-003","quantity":"analog sensor group delay","required_record":"installed step/impulse response including filters","acceptance_value":"SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-004","quantity":"digital input propagation and bounce","required_record":"edge injection at every monitored circuit","acceptance_value":"SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-005","quantity":"video frame timing and trigger latency","required_record":"common LED edge frame analysis and dropped-frame test","acceptance_value":"SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-006","quantity":"host transport loss","required_record":"backlog overflow skipped-scan and packet-loss counters","acceptance_value":"zero unexplained loss in accepted run; exact handling method SELECTION REQUIRED","state":"OPEN"},
        {"evidence_id":"DTE-007","quantity":"DYNAMIXEL polling latency and tick alignment","required_record":"host timestamp versus hardware trigger including 32767 ms rollover","acceptance_value":"supplemental only; no primary timing credit","state":"OPEN"},
        {"evidence_id":"DTE-008","quantity":"combined timing uncertainty","required_record":"signed error budget spanning trigger scan skew filters sensors video and analysis","acceptance_value":"SELECTION REQUIRED before test acceptance","state":"OPEN"},
    ]
    write_csv("timing-evidence-register.csv", tuple(timing[0]), timing)

    raw_fields = [
        ("run_id","text","immutable run identifier"),("configuration_commit","sha","tested repository commit"),("article_revision","text","exact fixture/article revision"),("sample_index","integer","monotonic DAQ sample index"),("daq_time_s","seconds","primary DAQ timebase"),("trigger_state","boolean","common hardware trigger"),("stop_command_state","boolean","operator or test stop edge"),("estop_state","boolean","isolated E-stop event monitor"),("source_voltage_V","V","external measured actuator bus voltage"),("source_current_A","A","external bidirectional current"),("k1_coil_state","boolean","isolated K1 coil command"),("k2_coil_state","boolean","isolated K2 coil command"),("k1_mirror_state","boolean","isolated K1 mirror feedback"),("k2_mirror_state","boolean","isolated K2 mirror feedback"),("external_angle_deg","deg","independent joint angle"),("external_velocity_deg_s","deg/s","declared-filter derivative"),("reaction_force_N","N","fixture reaction force"),("bumper_displacement_mm","mm","bumper compression"),("video_frame_id","integer","aligned high-speed video frame"),("video_time_s","seconds","verified video timebase"),("dxl_realtime_tick_ms","ms","supplemental actuator tick"),("dxl_present_current_raw","count","supplemental register"),("dxl_present_velocity_raw","count","supplemental register"),("dxl_present_position_raw","count","supplemental register"),("dxl_present_voltage_raw","count","supplemental register"),("dxl_present_temperature_raw","count","supplemental register"),("dropped_scan_count","integer","DAQ integrity counter"),("dxl_timeout_count","integer","supplemental transport counter"),("sensor_saturation_flags","bitfield","any range exceedance"),("filter_revision","text","velocity/force filtering identifier"),("calibration_bundle_hash","sha256","calibration evidence hash"),("timing_budget_revision","text","accepted error-budget identifier"),("operator_id","text","authorized test operator"),("witness_id","text","independent witness"),("run_disposition","enum","REJECTED ACCEPTED or HOLD; default HOLD")
    ]
    raw_rows = [{"field_id":f"DRF-{i:03d}","field_name":name,"unit_or_type":unit,"definition":definition,"required_for_accepted_run":"YES" if i <= 20 or i >= 27 else "SUPPLEMENTAL"} for i,(name,unit,definition) in enumerate(raw_fields,1)]
    write_csv("raw-data-schema.csv", tuple(raw_rows[0]), raw_rows)

    sources = [
        {"source_id":"DCS-001","organization":"ROBOTIS","document":"XM540-W270-T/R e-Manual","revision_or_date":"live page; no formal revision shown; accessed 2026-08-07","url":"https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/","verified_fact":"feedback registers and units include 1 ms Realtime Tick 2.69 mA/current unit 0.229 rpm/velocity unit and about 0.088 degree/position unit; position reset conditions apply"},
        {"source_id":"DCS-002","organization":"ROBOTIS","document":"U2D2 e-Manual","revision_or_date":"live page; no formal revision shown; accessed 2026-08-07","url":"https://emanual.robotis.com/docs/en/parts/interface/u2d2/","verified_fact":"USB communication converter supports TTL and RS-485 up to 6 Mbps; it does not supply actuator power"},
        {"source_id":"DCS-003","organization":"LabJack","document":"T-Series Datasheet","revision_or_date":"live documentation; no formal revision shown; accessed 2026-08-07","url":"https://support.labjack.com/docs/t-series-datasheet","verified_fact":"T7 family multifunction DAQ supports USB and Ethernet; model-specific features must not be inferred"},
        {"source_id":"DCS-004","organization":"LabJack","document":"3.2 Stream Mode T-Series Datasheet","revision_or_date":"live documentation; no formal revision shown; accessed 2026-08-07","url":"https://support.labjack.com/docs/3-2-stream-mode-t-series-datasheet","verified_fact":"stream scans use hardware-timed constant clock pulses and sequential address sampling"},
        {"source_id":"DCS-005","organization":"LabJack","document":"A-1-1 Stream Data Rates T-Series Datasheet","revision_or_date":"live documentation; no formal revision shown; accessed 2026-08-07","url":"https://support.labjack.com/docs/a-1-1-stream-data-rates-t-series-datasheet","verified_fact":"T7 typical maximum 100 ksamples/s at +/-10 V RI0/1 and 12.5 kscans/s for eight addresses at RI1; interchannel delay must be accounted for"},
        {"source_id":"DCS-006","organization":"LabJack","document":"3.2.2 Special Stream Modes T-Series Datasheet","revision_or_date":"live documentation; no formal revision shown; accessed 2026-08-07","url":"https://support.labjack.com/docs/3-2-2-special-stream-modes-t-series-datasheet","verified_fact":"T7 can use external clock and triggered stream; triggered stream requires minimum firmware 1.0186"},
        {"source_id":"DCS-007","organization":"Project Button","document":"HR-V0-GUARD-IMPACT-P0.1 and hard-stop validation P0.1","revision_or_date":"controlled repository state accessed 2026-08-07","url":"docs/hr-v0-guard-impact-basis-p0.1.md","verified_fact":"measured inertia speed current persistence force and synchronized video are blocking physical inputs"},
    ]
    write_csv("dynamic-source-register.csv", tuple(sources[0]), sources)

    summary = {
        "revision": REVISION,
        "status": WARNING,
        "parent_inputs": ["HR-V0-ARM-ARCH-P0.7", "HR-V0-HS-P0.3", "HR-V0-GUARD-IMPACT-P0.1"],
        "channel_count": len(channels),
        "primary_or_derived_channels": sum("SUPPLEMENTAL" not in r["primary_or_supplemental"] for r in channels),
        "supplemental_dxl_channels": 1,
        "fixture_control_count": len(fixture),
        "test_stage_count": len(sequence),
        "powered_stage_count": sum("actuator" in r["stage"] or "motion" in r["stage"] or "torque" in r["stage"] or "bumper" in r["stage"] or "fault" in r["stage"] for r in sequence),
        "authorized_powered_stage_count": 0,
        "timing_evidence_count": len(timing),
        "raw_field_count": len(raw_rows),
        "daq_candidate": "LabJack T7 evaluation candidate only; not selected for procurement",
        "release_state": "INPUT PACKAGE ONLY - ALL POWERED TESTS NOT AUTHORIZED",
    }
    (OUT / "dynamic-characterization-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    channel_cards = "".join(f"<article><h3>{r['channel_id']}: {r['quantity']}</h3><p class='kind'>{r['primary_or_supplemental']}</p><p>{r['method']}</p><p><strong>{r['selection_state']}</strong></p></article>" for r in channels)
    stage_rows = "".join(f"<tr><td>{r['stage_id']}</td><td>{r['stage']}</td><td>{r['authorization_gate']}</td><td>{r['execution_state']}</td></tr>" for r in sequence)
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{REVISION}</title><style>
:root{{--ink:#10244a;--blue:#1769aa;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#8b1e1e;--muted:#40536f}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:24px}}header{{background:var(--ink);color:#fff;max-width:none}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(30px,5vw,56px);line-height:1.05;margin:.25rem 0}}h2{{font-size:clamp(24px,3vw,34px);margin-top:2rem}}h3{{font-size:19px;margin:.2rem 0}}.warning{{background:#fff1c2;color:#391d00;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}article,.note{{background:white;border:2px solid #9fc9e7;border-radius:12px;padding:18px;box-shadow:0 4px 0 #c9e8fa;min-width:0}}.kind{{font-weight:800;color:var(--blue)}}.danger{{color:var(--danger);font-weight:800}}.tablewrap{{overflow-x:auto;border:2px solid #9fc9e7;border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{text-align:left;padding:14px;border-bottom:1px solid #b9d8ee;font-size:16px;vertical-align:top}}th{{background:var(--sky)}}code{{font-size:16px}}@media(max-width:800px){{header,main{{padding:18px}}.cards{{grid-template-columns:minmax(0,1fr)}}h1,p,td{{overflow-wrap:anywhere}}}}</style></head>
<body><header><div><p>PROJECT BUTTON - {REVISION}</p><h1>Measure the real joint</h1><p>External synchronized evidence for inertia, stopping, contact and energy.</p></div></header><main><p class='warning'>{WARNING}</p>
<section class='note'><h2>The key boundary</h2><p>DYNAMIXEL registers are useful corroboration, but USB and bus polling have no released host-latency or cross-channel timing guarantee. Primary stop-time and impact evidence therefore comes from one hardware-timed acquisition chain plus independent angle, current, voltage, force, displacement and trigger measurements.</p><p class='danger'>No powered test in this guide is authorized. Existing E2-E4 gates and configuration-specific written approval still control execution.</p></section>
<h2>Measurement channels</h2><div class='cards'>{channel_cards}</div>
<h2>Fail-closed sequence</h2><div class='tablewrap'><table><thead><tr><th>ID</th><th>Stage</th><th>Gate</th><th>State</th></tr></thead><tbody>{stage_rows}</tbody></table></div>
<h2>DAQ candidate, not a selection</h2><p>A LabJack T7 is a documented evaluation candidate because its stream is hardware-timed and its official table gives 12.5 kscans/s for eight +/-10 V addresses at resolution index 1. The exact scan list, ranges, isolation, signal conditioning, calibration, grounding, sample rate and timing budget remain <strong>SELECTION REQUIRED</strong>.</p>
<h2>What this unlocks</h2><p>Once built, calibrated, authorized and executed, this method can supply the missing physical inputs for moving mass and inertia, bumper/contact force, source-removal persistence, stopping time and guard proof-energy allocation. This file itself closes none of those tests.</p></main></body></html>"""
    (OUT / "HR-V0_dynamic-characterization-guide.html").write_text(html, encoding="utf-8")
    print(f"Generated {REVISION}: {len(channels)} channels, {len(sequence)} stages, {len(timing)} timing records, {len(raw_rows)} raw fields")
    print(WARNING)


if __name__ == "__main__":
    main()
