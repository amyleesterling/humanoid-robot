from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "x430-duty-characterization-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-x430-duty-characterization-template.csv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    sources = [
        {
            "source_id": "X430-DUTY-SRC-01",
            "title": "ROBOTIS XM430-W350-T/R e-Manual",
            "locator": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/",
            "revision_or_date": "live page; no formal document revision shown; accessed 2026-08-08",
            "use": "82 g catalog mass; 12 V stall endpoint; operating voltage and temperature; control-table units and ranges; stall-rating warning",
            "evidence_state": "CURRENT PRIMARY SOURCE",
            "sha256": "LIVE PRIMARY PAGE - NO LOCAL SNAPSHOT",
        },
        {
            "source_id": "X430-DUTY-SRC-02",
            "title": "HR-V0 P1.1 X430 load basis",
            "locator": "cad/hr-v0/generated/arm-load-basis-p1.1-x430/load-basis-summary.json",
            "revision_or_date": "HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE; 2026-08-08",
            "use": "incomplete gravity and analytical screen references only",
            "evidence_state": "CONTROLLED LOCAL SOURCE",
        },
        {
            "source_id": "X430-DUTY-SRC-03",
            "title": "HR-V0 generic dynamic-characterization input",
            "locator": "docs/hr-v0-dynamic-characterization-p0.1.md",
            "revision_or_date": "HR-V0-DYN-CHAR-P0.1; 2026-08-07",
            "use": "supplemental telemetry boundary and fail-closed powered-stage precedent",
            "evidence_state": "CONTROLLED LOCAL SOURCE",
        },
        {
            "source_id": "X430-DUTY-SRC-04",
            "title": "HR-V0 actuator current-envelope P0.2",
            "locator": "docs/hr-v0-actuator-current-envelope-p0.2.md",
            "revision_or_date": "P0.2; 2026-08-07",
            "use": "program-current-candidate boundary; does not provide a P1.1 X430 J2 rating",
            "evidence_state": "CONTROLLED LOCAL SOURCE",
        },
    ]
    for row in sources:
        if row.get("sha256") is None:
            row["sha256"] = digest(ROOT / str(row["locator"]))
    write_csv(OUT / "source-register.csv", list(sources[0]), sources)

    sensitivities = []
    for raw in (100, 200, 300, 400, 500, 600, 700):
        amps = raw * 0.00269
        sensitivities.append({
            "raw_current_units": raw,
            "nominal_internal_current_a": f"{amps:.6f}",
            "ideal_stall_line_torque_nm": f"{amps * (4.1 / 2.3):.6f}",
            "incomplete_gravity_ratio": f"{amps * (4.1 / 2.3) / 0.483257699:.6f}",
            "incomplete_2_25x_screen_ratio": f"{amps * (4.1 / 2.3) / 1.087329823:.6f}",
            "authority": "SENSITIVITY ONLY - NOT A COMMAND OR CONTINUOUS RATING",
        })
    write_csv(OUT / "current-torque-sensitivity.csv", list(sensitivities[0]), sensitivities)

    channels = [
        ("CH-01", "external actuator-branch current", "bidirectional current transducer plus independent acquisition", "A", "Primary electrical evidence; DYNAMIXEL current is supplemental", "SELECTION REQUIRED"),
        ("CH-02", "actuator terminal voltage", "differential measurement at received actuator connector", "V", "Capture source droop and wiring loss at the device", "SELECTION REQUIRED"),
        ("CH-03", "reaction torque", "calibrated force transducer at measured perpendicular lever arm", "N and m", "Primary mechanical output evidence", "SELECTION REQUIRED"),
        ("CH-04", "actuator metal-case temperature", "bonded calibrated contact sensor", "degC", "Primary external thermal evidence", "SELECTION REQUIRED"),
        ("CH-05", "actuator connector contact temperature", "calibrated contact sensor without compromising insulation", "degC", "Connector-heating evidence", "SELECTION REQUIRED"),
        ("CH-06", "moving-cable temperature", "calibrated contact sensor at worst credible bend/bundle location", "degC", "Harness-heating evidence", "SELECTION REQUIRED"),
        ("CH-07", "ambient air temperature", "shielded calibrated sensor near test article", "degC", "Reference for temperature-rise calculations", "SELECTION REQUIRED"),
        ("CH-08", "J2 output angle", "independent external angle reference", "deg", "Do not rely on actuator position alone", "SELECTION REQUIRED"),
        ("CH-09", "fixture deflection", "independent displacement measurement", "mm", "Detect invalid torque-arm geometry/compliance", "SELECTION REQUIRED"),
        ("CH-10", "hardware synchronization", "shared isolated trigger or demonstrably aligned clocks", "s", "Bound channel-to-channel timing uncertainty", "SELECTION REQUIRED"),
        ("CH-11", "DYNAMIXEL Present Current 126", "Protocol 2.0 telemetry", "raw and 2.69 mA/raw", "Supplemental correlation only", "CATALOG UNIT VERIFIED; RATE SELECTION REQUIRED"),
        ("CH-12", "DYNAMIXEL Present Input Voltage 144", "Protocol 2.0 telemetry", "0.1 V/raw", "Supplemental correlation only", "CATALOG UNIT VERIFIED; RATE SELECTION REQUIRED"),
        ("CH-13", "DYNAMIXEL Present Temperature 146", "Protocol 2.0 telemetry", "1 degC/raw", "Supplemental correlation only", "CATALOG UNIT VERIFIED; RATE SELECTION REQUIRED"),
        ("CH-14", "DYNAMIXEL Hardware Error Status 70", "Protocol 2.0 telemetry", "bitfield", "Record every transition with raw value", "CATALOG ADDRESS VERIFIED; DECODER/RATE REQUIRED"),
        ("CH-15", "command and safety-state log", "controller log plus physical enable/contactor observations", "state and time", "Correlate permitted, commanded and physically powered states", "SELECTION REQUIRED"),
    ]
    channel_rows = [dict(zip(("channel_id", "quantity", "method", "unit", "evidence_role", "state"), row)) for row in channels]
    write_csv(OUT / "instrument-channel-register.csv", list(channel_rows[0]), channel_rows)

    fixture = [
        ("FX-01", "Rigid bench and fixture load path", "Deflection and fastener capacity supported by calculation plus inspection", "OPEN"),
        ("FX-02", "Independent physical catch", "Contains link and load with actuator unpowered and after any single test-fixture control failure", "OPEN"),
        ("FX-03", "Full moving-volume guard", "Prevents access to pinch/sweep volume while allowing instrumentation", "OPEN"),
        ("FX-04", "Known torque-arm radius", "As-built perpendicular distance measured with uncertainty; no nominal-only credit", "OPEN"),
        ("FX-05", "Force-sensor line of action", "Alignment and off-axis sensitivity quantified across all test angles", "OPEN"),
        ("FX-06", "Load application", "No human-held weights, force gauges or straps inside the moving volume", "OPEN"),
        ("FX-07", "Branch current interruption", "Independent, accessible removal of actuator-branch energy; exact device/duty selection required", "OPEN"),
        ("FX-08", "Current limiting", "External source limit and actuator register limit independently reviewed and recorded", "OPEN"),
        ("FX-09", "Reverse-energy behavior", "Source, wiring and interruption devices reviewed for regenerated/back-driven energy", "OPEN"),
        ("FX-10", "Thermal sensor retention", "Attachment method does not insulate the case or enter moving/pinch paths", "OPEN"),
        ("FX-11", "Cable routing", "Strain relief, bend radius, separation and temperature-sensor locations documented", "OPEN"),
        ("FX-12", "Witnessed preflight", "Qualified mechanical/electrical reviewers sign the as-built fixture and limits before powered work", "OPEN"),
    ]
    fixture_rows = [dict(zip(("control_id", "control", "acceptance_evidence", "state"), row)) for row in fixture]
    write_csv(OUT / "fixture-control-register.csv", list(fixture_rows[0]), fixture_rows)

    stages = [
        ("DUT-00", "Configuration freeze", "Unpowered", "Bind actuator serial/model/firmware, fixture drawing, wiring revision, instrument IDs/calibrations and software hash", "Signed traveler; no substitution", "NOT EXECUTED"),
        ("DUT-01", "Fixture proof and catch check", "Unpowered", "Apply qualified proof method to load path and independently confirm catch/guard coverage", "Approved physical evidence", "NOT EXECUTED"),
        ("DUT-02", "Sensor zero/span and synchronization", "Unpowered", "Record pre/post zero, applied standards and timing alignment", "Uncertainty budget accepted", "NOT EXECUTED"),
        ("DUT-03", "Control-only communications", "Actuator branch physically isolated", "Read model/firmware/register configuration; exercise controller logging without actuator power", "Exact model and fail-closed state confirmed", "NOT EXECUTED"),
        ("DUT-04", "First torque-enable", "POWERED - NOT AUTHORIZED", "Guard closed; no external load; lowest independently approved current/PWM/velocity/acceleration limits", "No unexpected motion/fault; all primary channels valid", "BLOCKED"),
        ("DUT-05", "Incremental static map", "POWERED - NOT AUTHORIZED", "Approved increments of direction, angle and reaction torque with cool-down/abort logic", "Measured torque-current-voltage-temperature map with uncertainty", "BLOCKED"),
        ("DUT-06", "Bounded gravity hold", "POWERED - NOT AUTHORIZED", "Use complete accepted moving mass/COM and approved hold duration; never use the current incomplete screen as a released load", "Temperature rise and current remain within qualified project limits", "BLOCKED"),
        ("DUT-07", "No-payload cyclic duty", "POWERED - NOT AUTHORIZED", "Execute frozen representative trajectory/dwell/count only after LOAD-OPEN-04 closes", "Cycle-resolved electrical/mechanical/thermal evidence", "BLOCKED"),
        ("DUT-08", "Soft-payload cyclic duty", "POWERED - NOT AUTHORIZED", "Repeat only after payload retention, gripper force and guard evidence close", "Cycle-resolved evidence with retained payload", "BLOCKED"),
        ("DUT-09", "Worst credible released duty", "POWERED - NOT AUTHORIZED", "Execute only the qualified envelope derived from complete trajectory, ambient, mass, current, connector and cooling evidence", "Sustained/cyclic capability disposition", "BLOCKED"),
        ("DUT-10", "Branch-power removal", "POWERED - NOT AUTHORIZED", "At separately approved low-energy condition, remove actuator branch power and verify physical decay/state logging", "Measured response; no safety credit inferred", "BLOCKED"),
        ("DUT-11", "Post-test inspection and data seal", "Unpowered", "Record temperatures through cool-down, inspect actuator/connector/harness/fixture and hash raw data", "Qualified disposition or quarantine", "NOT EXECUTED"),
    ]
    stage_rows = [dict(zip(("stage_id", "stage", "energy_state", "method", "required_result", "state"), row)) for row in stages]
    write_csv(OUT / "duty-test-sequence.csv", list(stage_rows[0]), stage_rows)

    equations = [
        ("EQ-01", "external current RMS", "sqrt(integral(i_ext^2 dt)/duration)", "window and sample treatment must be frozen", "SELECTION REQUIRED"),
        ("EQ-02", "mechanical output torque", "force * perpendicular_as_built_lever_arm", "alignment, lever-arm and force uncertainty included", "SELECTION REQUIRED"),
        ("EQ-03", "case temperature rise", "max(case_temp - ambient_temp)", "project limit must be below applicable product/material/skin-contact constraints", "SELECTION REQUIRED"),
        ("EQ-04", "connector temperature rise", "max(connector_temp - ambient_temp)", "connector and termination limits must be manufacturer-supported", "SELECTION REQUIRED"),
        ("EQ-05", "late-window thermal slope", "linear_fit(case_temp versus time) over frozen terminal window", "steady-state criterion and window selected before test", "SELECTION REQUIRED"),
        ("EQ-06", "telemetry-current error", "DXL_present_current - synchronized_external_current", "external channel is primary; sign, delay and bandwidth accounted", "SELECTION REQUIRED"),
        ("EQ-07", "voltage margin", "min(actuator_terminal_voltage) versus released device/source envelope", "10.0-14.8 V is catalog envelope, not a system acceptance margin", "SELECTION REQUIRED"),
        ("EQ-08", "torque repeatability", "qualified statistic over repeated identical cases", "repeat count and allowable selected before test", "SELECTION REQUIRED"),
        ("EQ-09", "thermal cool-down", "time until all monitored temperatures return within approved band of ambient", "cool-down band and restart rule selected before test", "SELECTION REQUIRED"),
        ("EQ-10", "fault-free completion", "no unexpected hardware-error, shutdown, watchdog, reset or state mismatch", "raw states retained; any event forces quarantine/disposition", "SELECTION REQUIRED"),
    ]
    equation_rows = [dict(zip(("equation_id", "metric", "equation", "constraint", "acceptance_limit"), row)) for row in equations]
    write_csv(OUT / "acceptance-equation-register.csv", list(equation_rows[0]), equation_rows)

    form_fields = [
        "run_id", "stage_id", "execution_state", "configuration_commit", "actuator_serial", "actuator_model_readback",
        "firmware_version", "fixture_revision", "instrument_set", "calibration_record", "operator", "witnesses", "date_time_utc",
        "trajectory_id", "load_case_id", "current_limit_raw", "pwm_limit_raw", "velocity_limit_raw", "acceleration_limit_raw",
        "ambient_c", "external_current_rms_a", "external_current_peak_a", "terminal_voltage_min_v", "torque_mean_nm", "torque_peak_nm",
        "case_temp_max_c", "connector_temp_max_c", "cable_temp_max_c", "late_window_case_slope_c_per_min", "dxl_current_error_rms_a",
        "hardware_error_events", "abort_events", "raw_data_sha256", "review_disposition", "notes",
    ]
    form_rows = []
    for stage in stage_rows:
        form_rows.append({field: "" for field in form_fields} | {
            "run_id": f"RUN-{stage['stage_id']}",
            "stage_id": stage["stage_id"],
            "execution_state": "NOT EXECUTED",
            "review_disposition": "SELECTION REQUIRED",
        })
    write_csv(FORM, form_fields, form_rows)

    raw_fields = [
        "run_id", "sample_index", "host_time_utc", "sync_time_s", "command_state", "safety_state", "branch_power_state",
        "j2_angle_deg", "external_current_a", "terminal_voltage_v", "reaction_force_n", "lever_arm_m", "computed_torque_nm",
        "case_temp_c", "connector_temp_c", "cable_temp_c", "ambient_temp_c", "fixture_deflection_mm", "dxl_current_raw",
        "dxl_voltage_raw", "dxl_temperature_raw", "dxl_hardware_error_raw", "dxl_position_raw", "dxl_velocity_raw", "event_marker",
    ]
    write_csv(OUT / "raw-data-schema.csv", raw_fields, [])

    holds = [
        ("DUTY-HOLD-01", "Complete accepted moving mass, COM and inertia", "LOAD-OPEN-01/02/03; MASS-002", "OPEN"),
        ("DUTY-HOLD-02", "Frozen speed, acceleration, dwell, duty, cycle count and trajectory", "LOAD-OPEN-04", "OPEN"),
        ("DUTY-HOLD-03", "Reflected drive inertia, efficiency, backlash and compliance", "LOAD-OPEN-05", "OPEN"),
        ("DUTY-HOLD-04", "Exact received XM430-W350-T identity, firmware and connector interface", "INSPECT-BOM-001; INSPECT-CTRL-001", "OPEN"),
        ("DUTY-HOLD-05", "Approved branch source, protection, conductor, connector and reverse-energy limits", "EG-003; EG-004; EG-005", "OPEN"),
        ("DUTY-HOLD-06", "Released external current/PWM/velocity/acceleration limits", "TEST-CTRL-006", "OPEN"),
        ("DUTY-HOLD-07", "Selected calibrated instruments, acquisition rate/bandwidth and uncertainty budget", "HR-V0-DYN-CHAR-P0.1", "OPEN"),
        ("DUTY-HOLD-08", "Buildable reviewed fixture drawing, catch, guard and proof evidence", "EG-009; EG-025", "OPEN"),
        ("DUTY-HOLD-09", "Qualified temperature, temperature-rise, slope and cool-down limits", "TEST-THERM-001", "OPEN"),
        ("DUTY-HOLD-10", "Accepted abort logic and independent branch-power interruption", "EG-016; EG-020; EG-022", "OPEN"),
        ("DUTY-HOLD-11", "Payload retention and gripper-force evidence for payload stages", "TEST-GRIP-001; TEST-GRIP-002", "OPEN"),
        ("DUTY-HOLD-12", "Signed powered-work authorization by required qualified reviewers", "EG-024; EG-025", "OPEN"),
    ]
    hold_rows = [dict(zip(("hold_id", "closure_needed", "traceability", "state"), row)) for row in holds]
    write_csv(OUT / "open-hold-register.csv", list(hold_rows[0]), hold_rows)

    status = {
        "identifier": "HR-V0-X430-DUTY-P0.1",
        "parent_configuration": "HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE",
        "status": "PRELIMINARY_NOT_APPROVED_FOR_POWERED_TEST_OR_ENERGIZATION",
        "open_holds": [row["hold_id"] for row in hold_rows],
        "powered_stages_authorized": False,
        "test_fixture_buildable": False,
        "current_limit_released": False,
        "duty_profile_released": False,
        "thermal_limits_released": False,
        "continuous_torque_verified": False,
        "x430_selected": False,
        "p1_1_selected": False,
        "motion_released": False,
        "connection_released": False,
        "energization_released": False,
        "load_open_08_closed": False,
        "note": "This package defines the configuration-specific evidence route. It contains no executed physical data and no current or temperature acceptance value.",
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 X430 duty characterization P0.1</title>
<style>
:root{--sky:#dff4ff;--blue:#102a56;--mid:#1268a8;--gold:#f2bc2e;--paper:#f8fbff;--warn:#fff3c4;--line:#8fb8d4}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--blue);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
header{background:linear-gradient(135deg,var(--sky),#fff);border-bottom:5px solid var(--gold);padding:clamp(24px,5vw,64px)}
main{max-width:1180px;margin:auto;padding:28px 20px 64px}h1{font-size:clamp(32px,6vw,64px);line-height:1.05;margin:.2em 0}h2{font-size:clamp(24px,3vw,34px);margin:1.6em 0 .5em}h3{font-size:21px}.badge{display:inline-block;background:var(--gold);padding:7px 12px;border:2px solid var(--blue);border-radius:999px;font-size:13px;font-weight:800}.warning{background:var(--warn);border:3px solid var(--blue);padding:18px;border-radius:14px;font-weight:750}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}.card{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 5px 0 #d2e7f3}.metric{font-size:clamp(28px,4vw,44px);font-weight:850;color:var(--mid)}label{display:block;font-weight:750;margin-top:12px}input{width:100%;font:inherit;padding:10px;border:2px solid var(--line);border-radius:8px}output{font-weight:850;color:var(--mid)}.table-wrap{overflow-x:auto;border:2px solid var(--line);border-radius:12px;background:white}table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:12px;text-align:left;border-bottom:1px solid var(--line);font-size:16px;vertical-align:top}th{background:var(--sky)}code{font-size:14px;background:#eef6fb;padding:2px 5px;border-radius:4px}.small{font-size:14px}.stop{color:#8a2600;font-weight:850}.ok{color:#096238;font-weight:800}a{color:#064f88}
</style></head><body>
<header><span class="badge">HR-V0-X430-DUTY-P0.1</span><h1>Measure duty capability. Do not guess it.</h1><p class="warning">PRELIMINARY — NOT APPROVED FOR POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION. Every powered stage is blocked.</p></header>
<main>
<section class="grid"><article class="card"><h2>What is known</h2><div class="metric">4.1 N·m</div><p>ROBOTIS’s 12 V, 2.3 A <strong>stall endpoint</strong>. It is momentary, not continuous.</p></article><article class="card"><h2>What is open</h2><div class="metric">12 holds</div><p>Fixture, load, source, limits, instruments, duty, thermal criteria, interruption and authorization.</p></article><article class="card"><h2>Executed evidence</h2><div class="metric">0 runs</div><p>No physical article has been powered by this package.</p></article></section>
<h2>Non-authorizing current sensitivity</h2><p>This calculator converts the official 2.69 mA/raw unit and applies the ideal 12 V stall-line ratio. It is an exploratory comparison only. It does not select a register value, current limit, torque capacity or duty.</p>
<section class="grid"><article class="card"><label for="raw">Raw current units</label><input id="raw" type="range" min="0" max="700" step="1" value="200"><p><output id="rawOut">200</output> raw = <output id="ampOut">0.538</output> A nominal telemetry units</p><p>Ideal stall-line torque: <output id="torqueOut">0.959</output> N·m</p><p class="stop">NOT A COMMAND OR CONTINUOUS RATING</p></article><article class="card"><label for="lever">As-built lever arm (mm)</label><input id="lever" type="number" min="1" step="0.1" value="100"><label for="torque">Measured torque target (N·m)</label><input id="torque" type="number" min="0" step="0.01" value="0.5"><p>Ideal perpendicular reaction: <output id="forceOut">5.000</output> N</p><p class="small">The physical fixture must measure lever arm, alignment and uncertainty. This arithmetic does not release a fixture.</p></article></section>
<h2>Fail-closed sequence</h2><div class="table-wrap"><table><thead><tr><th>Stage</th><th>Energy state</th><th>Purpose</th><th>Current state</th></tr></thead><tbody>""" + "".join(
        f"<tr><td>{row['stage_id']} — {row['stage']}</td><td>{row['energy_state']}</td><td>{row['method']}</td><td class={'stop' if row['state']=='BLOCKED' else 'ok'}>{row['state']}</td></tr>" for row in stage_rows
    ) + """</tbody></table></div>
<h2>Primary evidence channels</h2><p>External current, actuator-terminal voltage, reaction torque, case/connector/cable/ambient temperature, external angle and synchronized state logs are primary. DYNAMIXEL telemetry is supplemental correlation evidence.</p>
<div class="table-wrap"><table><thead><tr><th>Channel</th><th>Quantity</th><th>Evidence role</th><th>State</th></tr></thead><tbody>""" + "".join(
        f"<tr><td>{row['channel_id']}</td><td>{row['quantity']}</td><td>{row['evidence_role']}</td><td>{row['state']}</td></tr>" for row in channel_rows
    ) + """</tbody></table></div>
<h2>Source and boundary</h2><p>The current <a href="https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/">ROBOTIS e-Manual</a> states that stall torque differs from continuous output and expected real-world performance. The catalog operating envelope and default control-table values are not Project Button acceptance limits. Qualified reviewers must establish lower application-specific limits from complete load, conductor, connector, enclosure, ambient and duty evidence.</p>
<p class="warning">Passing the package checker proves only internal arithmetic and fail-closed state. It does not prove continuous torque, thermal capacity, safe stopping, functional safety or permission to energize.</p>
</main><script>
const raw=document.getElementById('raw'),rawOut=document.getElementById('rawOut'),ampOut=document.getElementById('ampOut'),torqueOut=document.getElementById('torqueOut');
function currentCalc(){const a=Number(raw.value)*.00269;rawOut.value=raw.value;ampOut.value=a.toFixed(3);torqueOut.value=(a*(4.1/2.3)).toFixed(3)}raw.addEventListener('input',currentCalc);currentCalc();
const lever=document.getElementById('lever'),torque=document.getElementById('torque'),forceOut=document.getElementById('forceOut');
function forceCalc(){const r=Number(lever.value)/1000;forceOut.value=(r>0?Number(torque.value)/r:0).toFixed(3)}lever.addEventListener('input',forceCalc);torque.addEventListener('input',forceCalc);forceCalc();
</script></body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")

    print("Generated HR-V0-X430-DUTY-P0.1")
    print("12 holds open; 7 powered stages blocked; 0 executed runs")


if __name__ == "__main__":
    main()
