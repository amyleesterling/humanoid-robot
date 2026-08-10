from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-current-envelope-p0.1"
IDENTIFIER = "HR-V0-DXL-CURRENT-ENV-P0.1"
ROUND = "R154"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
SOURCE_PATHS = [
    ROOT / "firmware" / "supervisor" / "actuator-config.json",
    ROOT / "firmware" / "supervisor" / "project_button_supervisor" / "actuator_config.py",
    ROOT / "firmware" / "supervisor" / "project_button_supervisor" / "dynamixel_bus.py",
    ROOT / "firmware" / "supervisor" / "tests" / "test_dynamixel_bus.py",
    ROOT / "bom" / "bom.csv",
    ROOT / "electrical" / "hr-v0-protection-coordination-inputs.csv",
    ROOT / "release" / "hr-v0" / "dxl-harness-allocation-p0.1" / "current-qualification-template.csv",
]


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warning(row: dict[str, object]) -> dict[str, object]:
    return {**row, "warning": WARNING}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = json.loads(SOURCE_PATHS[0].read_text(encoding="utf-8"))
    unit = float(config["current_unit_a"])

    sources = [
        warning({"source_id": "CESRC-001", "manufacturer": "ROBOTIS", "document": "XM540-W270 e-Manual", "revision_date": "live page; no formal revision displayed; accessed 2026-08-09", "url": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", "used_for": "Current Limit and Goal Current unit about 2.69 mA; Current Limit range 0-2047; current-based position behavior; stall endpoint", "not_established": "external branch current, connector thermal limit, continuous torque, fuse or application approval"}),
        warning({"source_id": "CESRC-002", "manufacturer": "ROBOTIS", "document": "XM430-W350 e-Manual", "revision_date": "live page; no formal revision displayed; accessed 2026-08-09", "url": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/", "used_for": "Current Limit and Goal Current unit about 2.69 mA; Current Limit range 0-1193; current-based position behavior", "not_established": "external branch current, cable temperature, fuse or application approval"}),
        warning({"source_id": "CESRC-003", "manufacturer": "JST", "document": "EH series official PDF", "revision_date": "no formal revision/date displayed; accessed 2026-08-09", "url": "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "used_for": "3 A AC/DC at AWG 22; -25 to +85 C including temperature rise; contact-resistance basis", "not_established": "permission to exceed 3 A, received ROBOTIS cable construction or Project Button duty"}),
        warning({"source_id": "CESRC-004", "manufacturer": "Littelfuse", "document": "287 ATOF datasheet", "revision_date": "Rev. 02/04/2025; accessed 2026-08-09", "url": "https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40", "used_for": "available ratings, typical derating and time-current evidence boundary", "not_established": "F1-F3 rating, connector-overload protection, final terminals/wire or clearing approval"}),
        warning({"source_id": "CESRC-005", "manufacturer": "Project Button", "document": "HR-V0-ACT-P0.3 source and R154 current invariant", "revision_date": "repository-controlled source; generated 2026-08-09", "url": "../../../../firmware/supervisor/actuator-config.json", "used_for": "raw candidate settings and fail-closed evidence binding", "not_established": "physical current, thermal behavior, connector suitability or safety credit"}),
    ]

    envelope: list[dict[str, object]] = []
    for axis, harness in (("J1", "HAR-J1"), ("J2", "HAR-J2"), ("GRIPPER", "HAR-G1")):
        item = config["actuators"][axis]
        raw = int(item["current_limit_raw_candidate"])
        nominal = raw * unit
        connector = 3.0
        envelope.append(warning({
            "axis": axis,
            "harness_id": harness,
            "model": item["model"],
            "current_limit_raw_candidate": raw,
            "goal_current_max_raw_candidate": item["goal_current_max_raw_candidate"],
            "manufacturer_unit_a_approx": f"{unit:.5f}",
            "nominal_internal_current_screen_a": f"{nominal:.3f}",
            "jst_eh_series_basis_a_at_awg22": f"{connector:.1f}",
            "arithmetic_headroom_a_not_a_tolerance": f"{connector - nominal:.3f}",
            "arithmetic_headroom_percent_not_a_release": f"{100.0 * (connector - nominal) / connector:.1f}",
            "released_external_branch_limit_a": "SELECTION REQUIRED",
            "disposition": "GUARDED TEST CANDIDATE ONLY - PHYSICAL QUALIFICATION REQUIRED",
        }))

    controls = [
        ("CI-001", "before port open", "Current-envelope evidence hash must be accepted and external limit numeric", "ActuatorConfiguration.release_selections_closed", "source test plus accepted physical evidence", "CANDIDATE - FAIL CLOSED"),
        ("CI-002", "configuration", "Torque is forced off before discovery or current-register writes", "connect_and_configure", "source test and received-HIL trace", "CANDIDATE"),
        ("CI-003", "configuration", "Current Limit is written and read back exactly", "_configure_one", "source test and received-HIL trace", "CANDIDATE"),
        ("CI-004", "trajectory start", "Goal Current candidate is written before torque enable", "start_trajectory", "source test and received-HIL trace", "CANDIDATE"),
        ("CI-005", "every motion sample", "Current Limit is re-read; exact drift faults and forces torque-off", "poll_telemetry", "source fault-injection test and HIL", "R154 ADDED - ZERO SAFETY CREDIT"),
        ("CI-006", "every motion sample", "Goal Current is re-read; exact drift faults and forces torque-off", "poll_telemetry", "source fault-injection test and HIL", "R154 ADDED - ZERO SAFETY CREDIT"),
        ("CI-007", "every motion sample", "Present Current magnitude may not exceed configured raw limit", "poll_telemetry", "source fault-injection test and external synchronized measurement", "CANDIDATE"),
        ("CI-008", "any polling/write failure", "Best-effort torque-off and trajectory invalidation", "write_sample exception boundary", "source test and HIL timing evidence", "CANDIDATE - NOT SAFETY RATED"),
    ]
    control_rows = [warning({"control_id": a, "phase": b, "invariant": c, "implementation": d, "evidence_required": e, "state": f}) for a, b, c, d, e, f in controls]

    alternatives = [
        ("BP-001", "ATOF fuse alone as connector overload limiter", "REJECT AS SOLE CONTROL", "A fuse is retained for fault-clearing study but its time-current curve does not create an instantaneous 3 A ceiling", "Select rating only after source fault, load, cable, connector and clearing evidence"),
        ("BP-002", "Internal Current Limit + continuous readback + branch fuse", "RETAIN FOR GUARDED QUALIFICATION", "Raw 800 gives a 2.152 A nominal internal screen, but external current and overshoot remain unproven", "Execute the complete R154 measurement/thermal/protection matrix and obtain qualified disposition"),
        ("BP-003", "Add hardware eFuse/current limiter to each branch", "ALTERNATIVE - NOT SELECTED", "Could create an external ceiling but adds dissipation, fault, startup and regeneration behavior and requires DXL-STAR redesign", "Select exact device/topology only after regeneration and no-backfeed analysis"),
        ("BP-004", "Change actuator or connector/power architecture", "ALTERNATIVE - NOT SELECTED", "Removes the present interface assumption but changes validated mechanical/control architecture", "Invoke if BP-002 cannot pass without exceeding accepted electrical/thermal limits"),
    ]
    decision_rows = [warning({"option_id": a, "option": b, "disposition": c, "reason": d, "closure_action": e}) for a, b, c, d, e in alternatives]

    plans = [
        ("CUR-Q-001", "unpowered", "All harnesses", "identity, polarity, cavity population, contact retention and continuity", "received cables and custom controller cable", "INSPECTION ONLY"),
        ("CUR-Q-002", "source-only", "GST280A12-C6P path", "source load/current-limit/foldback and bus rise", "programmable electronic load; no actuator", "NOT EXECUTED"),
        ("CUR-Q-003", "torque off", "each branch", "idle/inrush/current-sensor zero and DXL integrity", "one received actuator at a time", "NOT EXECUTED"),
        ("CUR-Q-004", "staged load", "J1", "raw 200/400/600/800 external peak/RMS and temperature", "guarded load fixture; abort boundary SELECTION REQUIRED below 3 A", "NOT EXECUTED"),
        ("CUR-Q-005", "staged load", "J2", "raw 200/400/600/800 external peak/RMS and temperature", "guarded load fixture; abort boundary SELECTION REQUIRED below 3 A", "NOT EXECUTED"),
        ("CUR-Q-006", "representative duty", "GRIPPER", "raw 300 external peak/RMS, grip cycle and temperature", "guarded gripper fixture", "NOT EXECUTED"),
        ("CUR-Q-007", "thermal dwell", "J1/J2/G1", "connector/cable/board stabilization at accepted duty and worst ambient/bundle", "duration and temperature limits SELECTION REQUIRED", "NOT EXECUTED"),
        ("CUR-Q-008", "reversal", "J1/J2", "regeneration, bus rise, no-backfeed and source response", "guarded low-energy reversal first", "NOT EXECUTED"),
        ("CUR-Q-009", "simultaneous duty", "J1+J2+G1", "summed current, voltage sag, errors and temperature", "only after individual branches pass", "NOT EXECUTED"),
        ("CUR-Q-010", "fault fixture", "F1/F2/F3", "ampere-specific fuse clearing before damage", "separate controlled non-robot fixture; no direct uncontrolled short", "NOT EXECUTED"),
        ("CUR-Q-011", "HIL fault injection", "current registers", "Current Limit/Goal Current drift forces torque-off and requires fresh authority", "received actuator packet trace plus external current/timing", "SOURCE TEST PASS; PHYSICAL HIL NOT EXECUTED"),
    ]
    plan_rows = [warning({"test_id": a, "stage": b, "scope": c, "measurement": d, "fixture_boundary": e, "state": f}) for a, b, c, d, e, f in plans]

    acceptance_topics = [
        ("CUR-A-001", "official source identity", "current official ROBOTIS/JST/Littelfuse records independently accepted"),
        ("CUR-A-002", "received cable identity", "construction, pin orientation, continuity and retention accepted"),
        ("CUR-A-003", "raw-to-external mapping", "synchronized raw Present Current and calibrated external branch current characterized"),
        ("CUR-A-004", "operating peak/RMS", "every accepted duty stays below a qualified connector/conductor limit with stated margin"),
        ("CUR-A-005", "thermal", "connector, cable, board and actuator temperatures pass accepted stabilized limits"),
        ("CUR-A-006", "voltage drop", "branch minimum voltage and drop pass accepted limits"),
        ("CUR-A-007", "protection", "exact F1-F3 links/holders/terminals clear accepted faults before damage without nuisance opening"),
        ("CUR-A-008", "regeneration/no-backfeed", "all released reversal and power-sequence cases pass"),
        ("CUR-A-009", "Current Limit invariant", "source and received-HIL drift injection force torque-off"),
        ("CUR-A-010", "Goal Current invariant", "source and received-HIL drift injection force torque-off"),
        ("CUR-A-011", "duty definition", "profiles, accelerations, loads, dwell, ambient and bundling are frozen"),
        ("CUR-A-012", "DXL integrity", "waveform/error rate and watchdog timing pass with the measured harness"),
        ("CUR-A-013", "qualified review", "electrical, controls and mechanical reviewers sign the configuration-bound evidence"),
        ("CUR-A-014", "work authorization", "separate written authorization names exact hardware, fixture, people and limits"),
    ]
    acceptance = [warning({"acceptance_id": a, "topic": b, "pass_basis": c, "evidence_uri": "", "result": "NOT EXECUTED", "approver": "", "approval_date": ""}) for a, b, c in acceptance_topics]
    holds = [warning({"hold_id": f"DXL-CUR-HOLD-{i:03d}", "description": topic, "state": "OPEN", "closure_evidence": basis}) for i, (_, topic, basis) in enumerate(acceptance_topics, 1)]

    template_fields = ["record_id", "date_utc", "operator", "reviewer", "test_id", "axis", "harness_id", "actuator_model", "serial_number", "firmware_version", "source_id", "branch_protection_id", "current_limit_raw", "goal_current_raw", "profile_velocity_raw", "profile_acceleration_raw", "load_case", "duty_cycle", "ambient_c", "bundle_count", "sample_rate_hz", "bandwidth_hz", "external_peak_a", "peak_duration_ms", "external_rms_a", "present_current_peak_raw", "connector_start_c", "connector_max_c", "cable_max_c", "board_max_c", "actuator_max_c", "branch_min_v", "bus_max_v", "dxl_error_count", "torque_off_time_ms", "instrument_ids", "calibration_ids", "raw_data_uri", "photo_uri", "thermal_uri", "waveform_uri", "acceptance_basis", "result", "nonconformance_id", "approver", "approval_date", "notes", "warning"]
    test_rows = []
    for index, row in enumerate(plan_rows, 1):
        record = {field: "" for field in template_fields}
        record.update(record_id=f"CUR-EV-{index:03d}", test_id=row["test_id"], acceptance_basis="SELECTION REQUIRED", result="NOT EXECUTED", warning=WARNING)
        test_rows.append(record)

    write_csv("primary-source-register.csv", sources)
    write_csv("derived-current-envelope.csv", envelope)
    write_csv("control-invariant-register.csv", control_rows)
    write_csv("branch-protection-decision.csv", decision_rows)
    write_csv("measurement-plan.csv", plan_rows)
    write_csv("acceptance-matrix.csv", acceptance)
    write_csv("residual-holds.csv", holds)
    write_csv("test-data-template.csv", test_rows)

    status = {
        "identifier": IDENTIFIER,
        "round": ROUND,
        "date": DATE,
        "axes": len(envelope),
        "control_invariants": len(control_rows),
        "branch_protection_options": len(decision_rows),
        "measurement_steps": len(plan_rows),
        "acceptance_rows": len(acceptance),
        "residual_holds": len(holds),
        "source_hashes": {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in SOURCE_PATHS},
        "xm540_raw_candidate": 800,
        "xm540_nominal_internal_current_screen_a": 2.152,
        "external_branch_current_limit_a": "SELECTION REQUIRED",
        "fuse_values_released": False,
        "connector_current_conflict_closed": False,
        "physical_testing_executed": False,
        "qualified_review_complete": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    (OUT / "README.md").write_text(
        f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR154 derives the present internal current screens and hardens the supervisor so every motion-sample poll re-reads Current Limit and Goal Current. Any drift faults and forces torque-off. The XM540 raw-800 candidate is approximately 2.152 A internally, leaving 0.848 A of arithmetic distance to JST's published 3 A series basis. That arithmetic distance is not a tolerance, external-current limit, fuse selection, or application approval.\n\nFourteen acceptance/hold groups remain open. External current, connector/cable temperature, voltage drop, regeneration, no-backfeed, fault clearing, representative duty, received identity, qualified review and written work authorization are still required.\n",
        encoding="utf-8", newline="\n"
    )

    envelope_html = "".join(f"<tr><td>{html.escape(str(row['axis']))}</td><td>{html.escape(str(row['model']))}</td><td>{row['current_limit_raw_candidate']}</td><td>{row['nominal_internal_current_screen_a']} A</td><td>{row['arithmetic_headroom_a_not_a_tolerance']} A</td><td>{html.escape(str(row['released_external_branch_limit_a']))}</td></tr>" for row in envelope)
    decision_html = "".join(f"<tr><td>{row['option_id']}</td><td>{html.escape(str(row['option']))}</td><td><strong>{html.escape(str(row['disposition']))}</strong></td><td>{html.escape(str(row['reason']))}</td></tr>" for row in decision_rows)
    hold_html = "".join(f"<li><strong>{row['hold_id']}: {html.escape(str(row['description']))}</strong><span>{html.escape(str(row['closure_evidence']))}</span></li>" for row in holds)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.25rem,5.3vw,4.7rem);line-height:1.04;max-width:20ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.6rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem;margin:1rem 0 2rem}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code,.meta,li span{{font-size:14px}}li{{margin:.85rem 0}}li strong{{display:block}}a{{color:#075a96}}</style></head><body><header><div class="meta">{IDENTIFIER} · R154 · 2026-08-09</div><h1>Current has a software ceiling. The wire still needs proof.</h1><div class="warning">{WARNING}. Zero safety credit. No fuse value or external current limit is released.</div></header><main><p>The XM540 raw-800 candidate corresponds to an internal nominal screen of about 2.152 A. The supervisor now re-reads both current-bound registers during every motion sample and forces torque-off on drift. External branch current can differ; only physical synchronized measurements can close that boundary.</p><section class="grid"><article><b>2.152 A</b>internal XM540 screen</article><article><b>0 A</b>released external limit</article><article><b>14</b>open evidence groups</article><article><b>0</b>work authorizations</article></section><div class="boundary"><h2>The non-negotiable boundary</h2><p>JST publishes 3 A for EH at AWG 22 under its stated conditions. The 0.848 A arithmetic distance from the raw-800 internal screen is not measurement uncertainty, transient margin or thermal proof. Reaching 3 A is a test-abort ceiling until a stricter pre-trigger and complete acceptance basis are approved.</p></div><h2>Derived candidate envelope</h2><div class="table-wrap"><table><thead><tr><th>Axis</th><th>Model</th><th>Raw candidate</th><th>Internal screen</th><th>Arithmetic distance</th><th>Released external limit</th></tr></thead><tbody>{envelope_html}</tbody></table></div><h2>Architecture decision</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Option</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{decision_html}</tbody></table></div><div class="boundary"><h2>Fourteen evidence groups remain open</h2><ol>{hold_html}</ol></div><p><a href="derived-current-envelope.csv">derived envelope</a> · <a href="control-invariant-register.csv">control invariants</a> · <a href="branch-protection-decision.csv">architecture decision</a> · <a href="measurement-plan.csv">measurement plan</a> · <a href="test-data-template.csv">test record</a> · <a href="acceptance-matrix.csv">acceptance matrix</a> · <a href="primary-source-register.csv">sources</a></p></main></body></html>'''
    page = page.replace("<article><b>0 A</b>released external limit</article>", "<article><b>NONE</b>released external limit</article>")
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

    package_files = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    manifest = [warning({"path": path.name, "sha256": digest(path), "bytes": path.stat().st_size}) for path in package_files]
    write_csv("file-manifest.csv", manifest)

    print(f"{IDENTIFIER}: {len(envelope)} axes / {len(control_rows)} current invariants / {len(plan_rows)} measurement steps / {len(holds)} holds OPEN")
    print("No external current limit or fuse value released; all work-authority flags remain false")
    print(WARNING)


if __name__ == "__main__":
    main()
