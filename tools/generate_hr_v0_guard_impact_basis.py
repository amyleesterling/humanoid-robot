from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-impact-basis-p0.1"
REVISION = "HR-V0-GUARD-IMPACT-P0.1"
WARNING = (
    "PRELIMINARY - IMPACT ALLOCATION INPUT ONLY - NOT APPROVED FOR PANEL SELECTION, "
    "PROCUREMENT, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION"
)

PAYLOAD_KG = 0.100
MOVING_MASS_CEILING_KG = 0.750
TCP_SPEED_M_S = 0.150
DROP_HEIGHT_M = 0.950
J1_RADIUS_M = 0.360
J2_PAYLOAD_RADIUS_M = 0.15745
XM540_NO_LOAD_RPM_12V = 30.0
XM430_NO_LOAD_RPM_12V = 46.0
RAW_800_TORQUE_LINE_NM = 5.18
XM540_STALL_ENDPOINT_NM_12V = 10.6
G_M_S2 = 9.80665


def write_csv(name: str, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def f6(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    omega_xm540 = XM540_NO_LOAD_RPM_12V * 2.0 * math.pi / 60.0
    payload_translation_j = 0.5 * PAYLOAD_KG * TCP_SPEED_M_S**2
    moving_translation_j = 0.5 * MOVING_MASS_CEILING_KG * TCP_SPEED_M_S**2
    payload_drop_j = PAYLOAD_KG * G_M_S2 * DROP_HEIGHT_M
    payload_drop_plus_translation_j = payload_drop_j + payload_translation_j
    single_axis_mass_ceiling_j = (
        0.5 * MOVING_MASS_CEILING_KG * (J1_RADIUS_M * omega_xm540) ** 2
    )
    combined_axis_mass_ceiling_j = 0.5 * MOVING_MASS_CEILING_KG * (
        (J1_RADIUS_M + J2_PAYLOAD_RADIUS_M) * omega_xm540
    ) ** 2
    raw_800_work_per_degree_j = RAW_800_TORQUE_LINE_NM * math.pi / 180.0
    stall_work_per_degree_j = XM540_STALL_ENDPOINT_NM_12V * math.pi / 180.0

    input_rows = [
        {"input_id": "GII-001", "input": "maximum permitted payload mass", "value": "0.100", "unit": "kg", "basis": "SYS-002", "maturity": "REQUIREMENT CEILING"},
        {"input_id": "GII-002", "input": "maximum automatic TCP speed", "value": "0.150", "unit": "m/s", "basis": "SYS-004", "maturity": "REQUIREMENT CEILING; ENFORCEMENT UNVALIDATED"},
        {"input_id": "GII-003", "input": "moving assembly mass ceiling including payload", "value": "0.750", "unit": "kg", "basis": "MASS-002", "maturity": "ALLOCATION CEILING; ACTUAL MASS/COM/INERTIA OPEN"},
        {"input_id": "GII-004", "input": "maximum J1-to-object-center radius", "value": "0.360", "unit": "m", "basis": "SYS-003", "maturity": "REQUIREMENT CEILING; AS-BUILT INSPECTION OPEN"},
        {"input_id": "GII-005", "input": "maximum J2-to-object-center radius", "value": "0.15745", "unit": "m", "basis": "HR-V0-ARM-ARCH-P0.7: 129.05 mm plus 28.40 mm reserve", "maturity": "CANDIDATE GEOMETRY"},
        {"input_id": "GII-006", "input": "guard internal top release height", "value": "0.950", "unit": "m", "basis": "HR-V0-GUARD-P0.3", "maturity": "CANDIDATE ENCLOSURE HEIGHT"},
        {"input_id": "GII-007", "input": "XM540-W270 no-load speed at 12 V", "value": "30", "unit": "rev/min", "basis": "ROBOTIS current e-Manual", "maturity": "CATALOG ENDPOINT; NOT AN ALLOWED SPEED OR PHYSICAL MAXIMUM"},
        {"input_id": "GII-008", "input": "XM430-W350 no-load speed at 12 V", "value": "46", "unit": "rev/min", "basis": "ROBOTIS current e-Manual", "maturity": "CATALOG ENDPOINT; GRIPPER RADIUS/INERTIA OPEN"},
        {"input_id": "GII-009", "input": "XM540 RAW 800 ideal torque-line screen", "value": "5.18", "unit": "N m", "basis": "HR-V0-ACT-P0.3 project conversion", "maturity": "GUARDED TEST CANDIDATE; NOT CONTINUOUS OR MEASURED TORQUE"},
        {"input_id": "GII-010", "input": "XM540 stall endpoint at 12 V", "value": "10.6", "unit": "N m", "basis": "ROBOTIS current e-Manual", "maturity": "MOMENTARY ZERO-SPEED ENDPOINT; NOT SIMULTANEOUS WITH NO-LOAD SPEED"},
        {"input_id": "GII-011", "input": "test-energy multiplier", "value": "SELECTION REQUIRED", "unit": "-", "basis": "qualified risk and test-method review", "maturity": "UNRESOLVED"},
        {"input_id": "GII-012", "input": "effective/reflected drive inertia", "value": "SELECTION REQUIRED", "unit": "kg m^2", "basis": "guarded physical characterization", "maturity": "UNRESOLVED"},
        {"input_id": "GII-013", "input": "continued drive angle/time after contact", "value": "SELECTION REQUIRED", "unit": "deg or s", "basis": "measured detection and energy-removal response", "maturity": "UNRESOLVED"},
        {"input_id": "GII-014", "input": "largest credible detached item mass, shape, speed and direction", "value": "SELECTION REQUIRED", "unit": "configuration", "basis": "released BOM, retention analysis and fault review", "maturity": "UNRESOLVED"},
        {"input_id": "GII-015", "input": "static panel push-out and access-probe load", "value": "SELECTION REQUIRED", "unit": "N", "basis": "qualified guarding method and site review", "maturity": "UNRESOLVED"},
    ]
    write_csv(
        "impact-input-register.csv",
        ("input_id", "input", "value", "unit", "basis", "maturity"),
        input_rows,
    )

    energy_rows = [
        {"case_id": "GIE-001", "hazard_class": "controlled payload translation", "equation": "0.5 * 0.100 kg * (0.150 m/s)^2", "calculated_energy_j": f6(payload_translation_j), "use": "normal-command payload subcase", "limitations": "does not include drop, rebound, link contact, overspeed, drive persistence or detached parts", "state": "CALCULATED SUBCASE; NOT A GUARD RATING"},
        {"case_id": "GIE-002", "hazard_class": "controlled moving-mass equivalent", "equation": "0.5 * 0.750 kg * (0.150 m/s)^2", "calculated_energy_j": f6(moving_translation_j), "use": "conservative controlled-mode translation screen", "limitations": "lumps the full moving-mass ceiling at TCP speed; actual rigid-body inertia and contact point remain open", "state": "CALCULATED SCREEN; NOT A GUARD RATING"},
        {"case_id": "GIE-003", "hazard_class": "payload vertical drop", "equation": "0.100 kg * 9.80665 m/s^2 * 0.950 m", "calculated_energy_j": f6(payload_drop_j), "use": "receiver/catch test input", "limitations": "does not address rebound, off-axis release, link contact or metal debris", "state": "CALCULATED SUBCASE; TEST METHOD OPEN"},
        {"case_id": "GIE-004", "hazard_class": "payload drop plus allowed translation", "equation": "GIE-003 + GIE-001", "calculated_energy_j": f6(payload_drop_plus_translation_j), "use": "combined payload-only planning screen", "limitations": "scalar energy sum is intentionally conservative but does not define direction, impactor or acceptance", "state": "CALCULATED SUBCASE; TEST METHOD OPEN"},
        {"case_id": "GIE-005", "hazard_class": "single-axis catalog no-load mass-ceiling screen", "equation": "0.5 * 0.750 kg * (0.360 m * 30 rpm * 2*pi/60)^2", "calculated_energy_j": f6(single_axis_mass_ceiling_j), "use": "overspeed sensitivity only", "limitations": "point-mass ceiling; excludes reflected inertia, gravity, compliance, current persistence and voltage fault; no-load speed is not a guaranteed physical maximum", "state": "ENDPOINT SCREEN ONLY; INCOMPLETE"},
        {"case_id": "GIE-006", "hazard_class": "combined-axis catalog no-load mass-ceiling screen", "equation": "0.5 * 0.750 kg * ((0.360+0.15745) m * 30 rpm * 2*pi/60)^2", "calculated_energy_j": f6(combined_axis_mass_ceiling_j), "use": "simultaneous-axis overspeed sensitivity only", "limitations": "deliberately places all mass at the outer radius; still excludes reflected inertia, gravity, compliance, drive persistence, voltage fault and actual contact geometry", "state": "ENDPOINT SCREEN ONLY; INCOMPLETE"},
        {"case_id": "GIE-007", "hazard_class": "RAW 800 drive persistence sensitivity", "equation": "5.18 N m * pi/180 rad", "calculated_energy_j": f6(raw_800_work_per_degree_j), "use": "energy added per degree per XM540 while candidate torque persists", "limitations": "actual angle/time, dynamic torque and simultaneous-axis behavior are unresolved", "state": "UNIT SENSITIVITY ONLY; CASE NOT CLOSED"},
        {"case_id": "GIE-008", "hazard_class": "stall-endpoint persistence sensitivity", "equation": "10.6 N m * pi/180 rad", "calculated_energy_j": f6(stall_work_per_degree_j), "use": "forbidden endpoint sensitivity per degree per XM540", "limitations": "stall torque is momentary and zero-speed; it cannot be combined with no-load speed", "state": "CATALOG ENDPOINT SENSITIVITY; NOT A DESIGN LOAD"},
        {"case_id": "GIE-009", "hazard_class": "detached hardware or tool", "equation": "0.5 * m_detached * v_detached^2 plus rotational terms", "calculated_energy_j": "SELECTION REQUIRED", "use": "outer-panel and top containment", "limitations": "exact retained parts, failure mode, mass, shape, velocity, direction and rebound are unresolved", "state": "BLOCKING INPUT OPEN"},
        {"case_id": "GIE-010", "hazard_class": "powered link bearing on panel", "equation": "integral(torque dtheta) plus pre-contact kinetic and gravity energy", "calculated_energy_j": "SELECTION REQUIRED", "use": "panel/frame/joint/anchor structural case", "limitations": "contact point, force path, detection latency, energy removal, effective inertia and compliance are unresolved", "state": "BLOCKING INPUT OPEN"},
        {"case_id": "GIE-011", "hazard_class": "static access and push-out", "equation": "released force/displacement method", "calculated_energy_j": "SELECTION REQUIRED", "use": "panel retention, frame and access validation", "limitations": "qualified method, force, probe, application and acceptance values are unresolved", "state": "BLOCKING INPUT OPEN"},
    ]
    write_csv(
        "impact-energy-cases.csv",
        ("case_id", "hazard_class", "equation", "calculated_energy_j", "use", "limitations", "state"),
        energy_rows,
    )

    direction_rows = [
        {"direction_id": "GID-001", "hazard": "payload release/drop/rebound", "targets": "receiver; front; rear; left; right", "basis": "all released poses and power-loss/open-gripper faults", "required_evidence": "pose matrix plus TEST-DROP-001 raw rebound/escape results", "state": "OPEN"},
        {"direction_id": "GID-002", "hazard": "commanded or overspeed link contact", "targets": "front; rear; left; right; top where sweep permits", "basis": "complete swept volume plus measured stopping overtravel", "required_evidence": "as-built kinematics, contact map, effective inertia and energy-removal response", "state": "OPEN"},
        {"direction_id": "GID-003", "hazard": "detached actuator/frame/fastener/tool", "targets": "all outer panels; receiver; top", "basis": "retention and single-fault analysis", "required_evidence": "released BOM, fastener/retention proof, projectile definition and impact tests", "state": "OPEN"},
        {"direction_id": "GID-004", "hazard": "base or column detachment", "targets": "frame; panels; anchors; bench interface", "basis": "R-006 structural fault", "required_evidence": "Boston bench survey, anchor design, proof load and collapse envelope", "state": "OPEN"},
        {"direction_id": "GID-005", "hazard": "static external push or access attempt", "targets": "every panel center/edge/corner; joints; cable entry", "basis": "fixed-guard integrity and access prevention", "required_evidence": "qualified load/probe method and installed inspection", "state": "OPEN"},
        {"direction_id": "GID-006", "hazard": "receiver rebound or ricochet", "targets": "receiver floor/walls; adjacent outer panels", "basis": "100 g foam at every released pose", "required_evidence": "conditioned payload matrix, high-speed video and no-escape acceptance", "state": "OPEN"},
    ]
    write_csv(
        "impact-direction-matrix.csv",
        ("direction_id", "hazard", "targets", "basis", "required_evidence", "state"),
        direction_rows,
    )

    control_rows = [
        {"control_id": "GIC-001", "control": "Keep payload, moving-link, detached-part, drive-persistence and static-access cases separate.", "evidence_required": "signed final hazard-to-test allocation", "state": "OPEN"},
        {"control_id": "GIC-002", "control": "Measure the exact moving assembly mass, local COM and effective/reflected inertia before releasing link-impact energy.", "evidence_required": "closed MASS-002 ledger and guarded inertia characterization", "state": "NOT EXECUTED"},
        {"control_id": "GIC-003", "control": "Measure maximum speed, stop/contact response, current persistence, gravity contribution, compliance and rebound for each released fault case.", "evidence_required": "time-synchronized angle, velocity, current, force and high-speed video", "state": "NOT EXECUTED"},
        {"control_id": "GIC-004", "control": "Define the largest credible detached component/tool and prove its retention or include its mass, shape, direction and speed in containment tests.", "evidence_required": "released BOM/fastener FMEA and projectile definition", "state": "SELECTION REQUIRED"},
        {"control_id": "GIC-005", "control": "Select test-energy multipliers, impactor geometry, conditioning, support condition, location, direction, repeats and acceptance criteria through qualified review.", "evidence_required": "approved test specification and applicable licensed standards", "state": "SELECTION REQUIRED"},
        {"control_id": "GIC-006", "control": "Test the exact sheet lot, edge finish, gasket, engagement, frame, joints, anchors and cable entries; coupons alone cannot release the installed guard.", "evidence_required": "traceable coupon correlation plus full installed proof", "state": "NOT EXECUTED"},
        {"control_id": "GIC-007", "control": "Condition the guard at accepted temperature and aging bounds before applicable impact and retention tests.", "evidence_required": "released environment profile and conditioned raw results", "state": "SELECTION REQUIRED"},
        {"control_id": "GIC-008", "control": "Require no escape, no loss of edge engagement, no hazardous opening or fragment, and acceptable frame/joint/anchor condition after each test.", "evidence_required": "quantified acceptance limits and signed inspection", "state": "SELECTION REQUIRED"},
        {"control_id": "GIC-009", "control": "Do not add no-load-speed kinetic energy and stall torque as simultaneous motor performance points.", "evidence_required": "qualified calculation review", "state": "OPEN"},
        {"control_id": "GIC-010", "control": "Do not select nominal 3 mm TUFFAK or credit 12004 retention from these calculations.", "evidence_required": "all blocking cases closed plus physical proof and qualified selection", "state": "HOLD"},
        {"control_id": "GIC-011", "control": "Do not treat ISO 14120 metadata or OSHA 1910.212 as a project-specific test-energy value.", "evidence_required": "licensed-standard applicability review and released test method", "state": "OPEN"},
        {"control_id": "GIC-012", "control": "Any guard change requires rerunning sweep, stopping, mass, stability, access, thermal-fit and containment evidence.", "evidence_required": "configuration-controlled validation matrix", "state": "OPEN"},
    ]
    write_csv(
        "impact-test-controls.csv",
        ("control_id", "control", "evidence_required", "state"),
        control_rows,
    )

    source_rows = [
        {"source_id": "GIS-001", "organization": "ROBOTIS", "document": "XM540-W270-T/R e-Manual", "revision_or_date": "live page; no formal revision shown; accessed 2026-08-07", "url": "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", "verified_fact": "30 rev/min no-load speed and 10.6 N m at 12 V; stall is momentary and differs from continuous/real-world output"},
        {"source_id": "GIS-002", "organization": "ROBOTIS", "document": "XM430-W350-T/R e-Manual", "revision_or_date": "live page; no formal revision shown; accessed 2026-08-07", "url": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/", "verified_fact": "46 rev/min no-load speed and 4.1 N m at 12 V; stall is momentary and differs from continuous/real-world output"},
        {"source_id": "GIS-003", "organization": "ISO", "document": "ISO 14120:2015", "revision_or_date": "Edition 2; published 2015-11; current page checked 2026-08-07", "url": "https://www.iso.org/standard/59545.html", "verified_fact": "general guard design/construction/selection scope; no project test-energy value taken from public metadata"},
        {"source_id": "GIS-004", "organization": "OSHA", "document": "29 CFR 1910.212", "revision_or_date": "current electronic regulation checked 2026-08-07", "url": "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212", "verified_fact": "guarding required for listed hazards; guards affixed where possible and must not create a hazard"},
        {"source_id": "GIS-005", "organization": "Project Button", "document": "requirements.csv", "revision_or_date": "HR-30-SYS-R0.2 repository state accessed 2026-08-07", "url": "requirements/requirements.csv", "verified_fact": "SYS-002, SYS-003, SYS-004, SAFE-010 and SAFE-011 inputs"},
        {"source_id": "GIS-006", "organization": "Project Button", "document": "HR-V0-ARM-ARCH-P0.7", "revision_or_date": "R69 controlled candidate dated 2026-08-07", "url": "cad/hr-v0/generated/arm-architecture-p0.7/architecture-summary.json", "verified_fact": "J1/J2/G1 geometry and explicit missing inertia/physical proof"},
    ]
    write_csv(
        "impact-source-register.csv",
        ("source_id", "organization", "document", "revision_or_date", "url", "verified_fact"),
        source_rows,
    )

    summary = {
        "revision": REVISION,
        "status": WARNING,
        "parent_guard": "HR-V0-GUARD-P0.3",
        "retention_study": "HR-V0-GUARD-RET-P0.1",
        "payload_translation_j": round(payload_translation_j, 6),
        "moving_mass_translation_j": round(moving_translation_j, 6),
        "payload_drop_j": round(payload_drop_j, 6),
        "payload_drop_plus_translation_j": round(payload_drop_plus_translation_j, 6),
        "single_axis_catalog_endpoint_screen_j": round(single_axis_mass_ceiling_j, 6),
        "combined_axis_catalog_endpoint_screen_j": round(combined_axis_mass_ceiling_j, 6),
        "raw_800_work_per_degree_per_xm540_j": round(raw_800_work_per_degree_j, 6),
        "stall_endpoint_work_per_degree_per_xm540_j": round(stall_work_per_degree_j, 6),
        "calculated_numeric_cases": 8,
        "blocking_open_energy_cases": 3,
        "direction_rows": len(direction_rows),
        "test_controls": len(control_rows),
        "selection_state": "NO PANEL, RETENTION SYSTEM, TEST ENERGY, OR IMPACT RATING SELECTED",
    }
    (OUT / "guard-impact-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    case_cards = "\n".join(
        f"<article><h3>{row['case_id']}: {row['hazard_class']}</h3>"
        f"<div class='value'>{row['calculated_energy_j']} J</div>"
        f"<p class='state'>{row['state']}</p><p>{row['limitations']}</p></article>"
        for row in energy_rows
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{REVISION} guard impact basis</title>
<style>
:root{{--ink:#10244a;--blue:#1769aa;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#8b1e1e;--muted:#40536f}}
*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
header,main{{max-width:1180px;margin:auto;padding:24px}}header{{background:var(--ink);color:#fff;max-width:none}}header>div{{max-width:1180px;margin:auto}}
h1{{font-size:clamp(30px,5vw,56px);line-height:1.05;margin:.25rem 0}}h2{{font-size:clamp(24px,3vw,34px);margin-top:2rem}}h3{{font-size:19px;margin:.2rem 0}}
.warning{{background:#fff1c2;color:#391d00;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:16px;margin:24px 0;min-width:0}}
article,.note{{background:#fff;border:2px solid #9fc9e7;border-radius:12px;padding:18px;box-shadow:0 4px 0 #c9e8fa;min-width:0}}.value{{font-size:clamp(25px,3vw,38px);font-weight:800;color:var(--blue);overflow-wrap:anywhere}}.state{{font-weight:800;color:var(--danger)}}
.classes{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}}.classes div{{background:var(--sky);border:2px solid #72b4df;border-radius:10px;padding:14px;font-weight:750;text-align:center}}
code{{font-size:16px}}.muted{{color:var(--muted)}}
@media(max-width:800px){{header,main{{padding:18px;min-width:0}}.cards,.classes{{grid-template-columns:minmax(0,1fr)}}h1,p,.value{{overflow-wrap:anywhere}}}}
</style></head><body>
<header><div><p>PROJECT BUTTON - {REVISION}</p><h1>What could hit the guard?</h1><p>Impact-energy allocation input, not a panel rating or build release.</p></div></header>
<main><p class="warning">{WARNING}</p>
<h2>Five hazards, not one magic number</h2><div class="classes"><div>Foam payload</div><div>Moving links</div><div>Runaway drive</div><div>Detached hardware</div><div>Static access</div></div>
<p>The payload-only calculations are closed arithmetic. The installed guard cannot be selected from them because moving-link inertia, drive persistence, detached parts, direction, test multiplier and structural acceptance remain open.</p>
<h2>Calculated and open cases</h2><div class="cards">{case_cards}</div>
<section class="note"><h2>Interpretation</h2><p><strong>0.932757 J</strong> is the combined payload-only drop-plus-translation screen. <strong>{single_axis_mass_ceiling_j:.6f} J</strong> and <strong>{combined_axis_mass_ceiling_j:.6f} J</strong> are deliberately conservative mass-ceiling sensitivity screens using the XM540 12 V catalog no-load endpoint. They are not credible maximum energies and still omit reflected inertia and drive work after contact.</p><p>At the guarded RAW 800 torque-line candidate, every unresolved degree of continued drive adds <strong>{raw_800_work_per_degree_j:.6f} J per XM540</strong> before gravity, impact dynamics and simultaneous-axis effects. That is why stop/contact response must be measured before panel proof energy is released.</p></section>
<h2>Release boundary</h2><p>Nominal 3 mm TUFFAK and 80/20 12004 remain nonselected. The exact installed sheet, edge finish, gasket, frame, joints, anchors and cable entries require a qualified test specification and physical proof. No calculation here authorizes buying, cutting, assembling, moving, connecting or energizing the robot.</p>
</main></body></html>"""
    (OUT / "HR-V0_guard-impact-basis.html").write_text(html, encoding="utf-8")

    print(
        f"Generated {REVISION}: {len(input_rows)} inputs, {len(energy_rows)} energy cases, "
        f"{len(direction_rows)} direction rows, {len(control_rows)} controls"
    )
    print(WARNING)


if __name__ == "__main__":
    main()
