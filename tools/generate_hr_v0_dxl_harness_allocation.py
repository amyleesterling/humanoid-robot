"""Generate the R153 DXL harness allocation and qualification-boundary package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-harness-allocation-p0.1"
IDENTIFIER = "HR-V0-DXL-HARNESS-ALLOC-P0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SOURCES = [
    ROOT / "bom" / "bom.csv",
    ROOT / "bom" / "hr-v0-bom-closure.csv",
    ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv",
    ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "connector-schedule.csv",
    ROOT / "firmware" / "supervisor" / "actuator-config.json",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    for path in SOURCES:
        if not path.is_file():
            raise FileNotFoundError(path)
    if OUT.exists():
        resolved = OUT.resolve()
        if resolved.parent != (ROOT / "release" / "hr-v0").resolve() or resolved.name != "dxl-harness-allocation-p0.1":
            raise RuntimeError(f"refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    OUT.mkdir(parents=True)

    source_data = [
        ("HRSRC-001", "ROBOTIS", "DYNAMIXEL XM540-W270-T product page", "https://www.robotis.us/dynamixel-xm540-w270-t/", "SKU 902-0137-000; package includes one Robot Cable-X3P 180mm JST-JST; 4.4 A stall current at 12 V", "received construction, continuous duty, connector transient allowance and project suitability"),
        ("HRSRC-002", "ROBOTIS", "DYNAMIXEL XM430-W350-T product page", "https://www.robotis.us/dynamixel-xm430-w350-t/", "SKU 902-0124-000; package includes one Robot Cable-X3P 180mm JST-JST; 2.3 A stall current at 12 V", "received construction, continuous duty, connector transient allowance and project suitability"),
        ("HRSRC-003", "ROBOTIS", "Robot Cable-X3P 180mm (10pcs) product page", "https://robotis.us/robot-cable-x3p-180mm-10pcs/", "standalone reference SKU 903-0249-000; 180 mm; JST-JST; X-Series TTL compatibility", "availability, conductor gauge, current rating, contact crimp and installed bend life"),
        ("HRSRC-004", "ROBOTIS", "U2D2 e-Manual", "https://emanual.robotis.com/docs/en/parts/interface/u2d2/", "TTL pin 1 GND, pin 2 VDD, pin 3 DATA; EHR-3/B3B-EH-A/SEH-001T-P0.6; U2D2 does not supply DYNAMIXEL power", "exact Project Button harness construction or permission to terminate a live VDD wire at an unused pin"),
        ("HRSRC-005", "JST", "EH connector catalog eEH.pdf", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "3 A AC/DC at AWG 22; AWG 32-22; -25 to +85 C including current temperature rise; B3B-EH-A/EHR-3/SEH-001T-P0.6", "21 AWG compatibility, overload/transient allowance, derating and XM540 application approval"),
        ("HRSRC-006", "ROBOTIS", "XM540-W270-T/R e-Manual", "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", "10.6 N m / 4.4 A stall endpoint at 12 V; Current Limit about 2.69 mA/raw; stall is momentary and not continuous", "external branch-current waveform, continuous torque and EH transient application"),
    ]
    source_rows = [{"source_id": i, "manufacturer": m, "document_or_page": d, "revision_or_access": "live source; no formal revision displayed; accessed 2026-08-09", "url": u, "controlled_fact": f, "not_proved": n, "warning": WARNING} for i, m, d, u, f, n in source_data]
    write_csv(OUT / "primary-source-register.csv", source_rows)

    allocations = [
        ("HAR-CTRL", "controller data/return only", "BOM-003;BOM-051;BOM-061", "U2D2 TTL", "DXL-STAR JC1", "SELECTION REQUIRED", "2", "GND to CTRL_GND", "EMPTY at both ends / JC1.2 NO_NET_NO_COPPER", "DATA to DXL_DATA", "CUSTOM CABLE - NOT RELEASED", "YES - AFTER SELECTION AND AUTHORIZATION", "wire, colors, length, shield, tool, crimp, pull, strain relief, continuity, isolation, no-backfeed and waveform evidence"),
        ("HAR-J1", "shoulder branch power/data", "BOM-005;BOM-051;BOM-086", "DXL-STAR JA1", "XM540 J1", "180", "3", "GND", "VDD1", "DXL_DATA", "INCLUDED ROBOTIS X3P CABLE - RECEIVING/QUALIFICATION HOLD", "NO", "received identity/pin orientation, construction, current/thermal, retention, routing, bend and waveform evidence"),
        ("HAR-J2", "elbow branch power/data", "BOM-006;BOM-051;BOM-086", "DXL-STAR JA2", "XM540 J2", "180", "3", "GND", "VDD2", "DXL_DATA", "INCLUDED ROBOTIS X3P CABLE - RECEIVING/QUALIFICATION HOLD", "NO", "received identity/pin orientation, construction, current/thermal, retention, routing, bend and waveform evidence"),
        ("HAR-G1", "gripper branch power/data", "BOM-007;BOM-051;BOM-086", "DXL-STAR JA3", "XM430 G1", "180", "3", "GND", "VDD3", "DXL_DATA", "INCLUDED ROBOTIS X3P CABLE - RECEIVING/QUALIFICATION HOLD", "NO", "received identity/pin orientation, construction, current/thermal, retention, routing, bend and waveform evidence"),
    ]
    allocation_rows = [{"harness_id": i, "role": role, "parent_bom_items": parents, "source_end": start, "destination_end": end, "nominal_length_mm": length, "conductor_count": count, "cavity_1": c1, "cavity_2": c2, "cavity_3": c3, "allocation": allocation, "separate_purchase": purchase, "residual": residual, "warning": WARNING} for i, role, parents, start, end, length, count, c1, c2, c3, allocation, purchase, residual in allocations]
    write_csv(OUT / "harness-allocation.csv", allocation_rows)

    parity_data = [
        ("BOM-052", "JST B3B-EH-A", "4", "4", "JC1 plus JA1-JA3 board headers"),
        ("BOM-054", "JST EHR-3 loose housing", "8", "2", "HAR-CTRL two ends only; factory branch housings move to BOM-086"),
        ("BOM-055", "JST SEH-001T-P0.6 loose contact", "22", "4", "HAR-CTRL cavities 1 and 3 at both ends; factory branch contacts move to BOM-086"),
        ("BOM-061", "custom U2D2-to-JC1 cable", "1 mixed harness set", "1 controller cable", "two populated conductors; cavity 2 empty at both ends"),
        ("BOM-086", "ROBOTIS X3P 180mm JST-JST included cable", "not separately allocated", "3 integrated", "one included with each BOM-005/BOM-006/BOM-007 actuator"),
    ]
    parity_rows = [{"item_id": i, "identity": ident, "old_quantity": old, "new_quantity": new, "allocation": allocation, "result": "PASS", "warning": WARNING} for i, ident, old, new, allocation in parity_data]
    write_csv(OUT / "connector-bom-parity.csv", parity_rows)

    pin_data = [
        ("U2D2 TTL", "1", "GND", "CTRL_GND", "POPULATED", "JC1.1", "continuity only to JC1.1"),
        ("U2D2 TTL", "2", "VDD", "NONE", "EMPTY", "NONE", "no contact and no conductor"),
        ("U2D2 TTL", "3", "DATA", "DXL_DATA", "POPULATED", "JC1.3", "continuity only to JC1.3"),
        ("DXL-STAR JC1", "1", "CTRL_GND", "CTRL_GND", "POPULATED", "U2D2.1", "continuity only to U2D2.1"),
        ("DXL-STAR JC1", "2", "INTENTIONALLY_UNUSED_U2D2_VDD", "NONE", "EMPTY", "NONE", "no contact/conductor; native pad remains NO_NET_NO_COPPER"),
        ("DXL-STAR JC1", "3", "DXL_DATA", "DXL_DATA", "POPULATED", "U2D2.3", "continuity only to U2D2.3"),
    ]
    pin_rows = [{"end": end, "cavity": cavity, "official_name": name, "project_net": net, "population": population, "destination": destination, "acceptance": acceptance, "warning": WARNING} for end, cavity, name, net, population, destination, acceptance in pin_data]
    write_csv(OUT / "controller-cable-pinmap.csv", pin_rows)

    question_data = [
        ("HRQ-001", "ROBOTIS", "Confirm exact conductor size, strand construction, insulation and contact termination in the 180 mm X3P cable supplied with XM540/XM430 packages."),
        ("HRQ-002", "ROBOTIS", "State continuous, RMS and peak current limits, permitted peak duration/duty, ambient/bundling basis and temperature-rise test basis for the supplied X3P cable with XM540-W270-T."),
        ("HRQ-003", "ROBOTIS", "Explain the e-Manual 21 AWG statement against JST EH's published AWG 22 maximum and identify any manufacturer-approved terminal/contact construction."),
        ("HRQ-004", "ROBOTIS", "State whether Current Limit raw 800 or another setting can bound external branch-supply current below 3 A under startup, reversal, stall and regenerative conditions; provide test basis if available."),
        ("HRQ-005", "JST", "For B3B-EH-A/EHR-3/SEH-001T-P0.6, provide any published pulse/overcurrent curve or permissible current-versus-duration data beyond the 3 A AWG 22 rating."),
        ("HRQ-006", "JST", "Confirm whether any 21 AWG conductor is approved with SEH-001T-P0.6 and identify conductor-area, insulation-diameter, tooling and crimp-height boundaries."),
        ("HRQ-007", "JST", "Provide the applicable temperature-rise test method, derating guidance, circuit-count/bundling effects and mating-cycle/contact-resistance limits for this application."),
        ("HRQ-008", "ROBOTIS and JST", "State whether the XM540 4.4 A momentary stall endpoint through the supplied EH cable is within an approved application envelope and list every required condition."),
    ]
    question_rows = [{"question_id": i, "recipient": recipient, "question": question, "status": "NOT SENT", "response_evidence": "", "warning": WARNING} for i, recipient, question in question_data]
    write_csv(OUT / "manufacturer-questions.csv", question_rows)

    acceptance_data = [
        ("HRA-001", "received branch-cable identity", "three received 180 mm JST-JST X3P cables traced to their actuator packages", "NOT EXECUTED"),
        ("HRA-002", "factory-cable continuity/polarity", "pin-by-pin continuity and no shorts for HAR-J1/HAR-J2/HAR-G1", "NOT EXECUTED"),
        ("HRA-003", "controller-cable construction", "HAR-CTRL only cavities 1 and 3 populated at both ends; exact selected wire/tool/process accepted", "SELECTION REQUIRED"),
        ("HRA-004", "controller-cable continuity/isolation", "1-to-1 and 3-to-3 continuity; cavity 2 absent; all unintended pairs isolated", "NOT EXECUTED"),
        ("HRA-005", "no-backfeed/power sequencing", "no VDD transfer into U2D2 or between VDD1/VDD2/VDD3 for every controlled sequence/fault case", "NOT EXECUTED"),
        ("HRA-006", "XM540 branch current", "externally measured waveform and RMS within a qualified connector/cable envelope; no unpublished transient allowance inferred", "NOT EXECUTED"),
        ("HRA-007", "current-limit relationship", "external branch current characterized at every guarded internal-current setting and representative duty", "NOT EXECUTED"),
        ("HRA-008", "connector/cable temperature", "stabilized temperatures meet a qualified limit under worst accepted duty, ambient and bundling", "SELECTION REQUIRED"),
        ("HRA-009", "waveform/communication", "baud/topology/route error-rate, edge, ringing and common-mode evidence accepted", "NOT EXECUTED"),
        ("HRA-010", "protection/fault clearing", "source, conductor, connector and protection coordination accepted for overload, short, inrush and regeneration", "SELECTION REQUIRED"),
    ]
    acceptance_rows = [{"acceptance_id": i, "subject": subject, "acceptance_basis": basis, "execution_state": state, "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for i, subject, basis, state in acceptance_data]
    write_csv(OUT / "acceptance-matrix.csv", acceptance_rows)

    hold_subjects = [
        "BOM-061 controller conductor and exact length", "BOM-054/BOM-055 wire-contact compatibility and controlled crimp process",
        "received BOM-086 cable identity, construction, continuity and polarity", "cable routing, strain relief, service loop, flex/bend and abrasion evidence",
        "JST EH 3 A versus XM540 4.4 A application disposition", "external branch-current measurement and internal-current relationship",
        "connector/conductor thermal stabilization and ambient/bundling basis", "BOM-015 branch protection and fault-clearing coordination",
        "no-backfeed and all power-sequence/fault evidence", "DXL waveform, baud, topology, EMC and error-rate evidence",
        "manufacturer responses or qualified written application disposition", "received DXL-STAR first article and harness mating/retention evidence",
        "independent electrical/manufacturing review", "separate written procurement, fabrication, assembly and powered-work authority",
    ]
    hold_rows = [{"hold_id": f"DXL-HAR-HOLD-{idx:03d}", "subject": subject, "status": "OPEN", "evidence_needed": "executed accepted record linked to the applicable acceptance row", "warning": WARNING} for idx, subject in enumerate(hold_subjects, start=1)]
    write_csv(OUT / "residual-holds.csv", hold_rows)

    receiving_fields = ["record_id", "date_utc", "operator", "reviewer", "harness_id", "parent_actuator_item", "actuator_serial", "cable_marking", "measured_length_mm", "end_a_orientation", "end_b_orientation", "pin1_continuity", "pin2_continuity", "pin3_continuity", "pin1_pin2_isolation", "pin1_pin3_isolation", "pin2_pin3_isolation", "retention_result", "visual_result", "instrument_ids", "calibration_ids", "raw_data_uri", "result", "nonconformance_id", "approver", "approval_date", "notes"]
    receiving_rows = []
    for idx, (harness, parent) in enumerate((("HAR-CTRL", "BOM-061"), ("HAR-J1", "BOM-005"), ("HAR-J2", "BOM-006"), ("HAR-G1", "BOM-007")), start=1):
        row = {field: "" for field in receiving_fields}
        row.update(record_id=f"HRR-{idx:03d}", harness_id=harness, parent_actuator_item=parent, result="NOT EXECUTED")
        receiving_rows.append(row)
    write_csv(OUT / "receiving-template.csv", receiving_rows)

    current_fields = ["record_id", "date_utc", "operator", "reviewer", "harness_id", "axis", "actuator_model", "serial_number", "firmware_version", "supply_source", "source_limit_setting", "branch_protection", "current_limit_raw", "goal_current_raw", "profile_velocity_raw", "profile_acceleration_raw", "test_case", "duty_definition", "ambient_c", "bundling_configuration", "sample_rate_hz", "analog_bandwidth_hz", "peak_current_a", "peak_duration_ms", "rms_window_ms", "rms_current_a", "connector_start_c", "connector_max_c", "cable_max_c", "actuator_max_c", "branch_min_v", "branch_max_v", "dxl_error_count", "instrument_ids", "calibration_ids", "raw_data_uri", "manufacturer_disposition_uri", "acceptance_basis", "result", "nonconformance_id", "approver", "approval_date", "notes"]
    current_rows = []
    cases = (("CUR-001", "HAR-J1", "J1", 200, "TORQUE_OFF_BASELINE"), ("CUR-002", "HAR-J1", "J1", 400, "LOADED_HOLD"), ("CUR-003", "HAR-J1", "J1", 600, "BIDIRECTIONAL_MOTION"), ("CUR-004", "HAR-J1", "J1", 800, "REPRESENTATIVE_DUTY"), ("CUR-005", "HAR-J2", "J2", 800, "REPRESENTATIVE_DUTY"), ("CUR-006", "HAR-G1", "G1", 300, "GRIPPER_DUTY"), ("CUR-007", "HAR-J1", "J1", 800, "REVERSAL_REGENERATION"))
    for rid, harness, axis, limit, case in cases:
        row = {field: "" for field in current_fields}
        row.update(record_id=rid, harness_id=harness, axis=axis, actuator_model="XM430-W350-T" if axis == "G1" else "XM540-W270-T", current_limit_raw=str(limit), goal_current_raw=str(limit), test_case=case, acceptance_basis="SELECTION REQUIRED", result="NOT EXECUTED")
        current_rows.append(row)
    write_csv(OUT / "current-qualification-template.csv", current_rows)

    status = {
        "identifier": IDENTIFIER, "round": "R153", "date": "2026-08-09",
        "harness_allocations": 4, "integrated_factory_branch_cables": 3, "custom_controller_cables": 1,
        "loose_ehr3_housings": 2, "loose_seh_contacts": 4, "primary_sources": 6,
        "manufacturer_questions": 8, "acceptance_rows": 10, "residual_holds": 14,
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in SOURCES},
        "duplicate_branch_housings_removed": 6, "duplicate_branch_contacts_removed": 18,
        "bom086_separate_purchase_required": False, "controller_vdd_conductor_allowed": False,
        "connector_current_conflict_closed": False, "harness_fully_selected": False,
        "manufacturer_contacted": False, "manufacturer_response_received": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "physical_article_exists": False, "connection_authorized": False, "powered_test_authorized": False,
        "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING,
    }
    write_text(OUT / "package-status.json", json.dumps(status, indent=2) + "\n")
    write_text(OUT / "README.md", f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR153 corrects DXL harness allocation. Each held ROBOTIS actuator package includes one assembled 180 mm JST-JST X3P cable, so the three branch cables are integrated as `BOM-086`; six loose EHR-3 housings and eighteen loose contacts are no longer double-counted. `BOM-061` now covers only one custom U2D2-to-JC1 data/return cable with cavity 2 empty at both ends.\n\nThis does not close the JST EH 3 A versus XM540 4.4 A condition, select controller wire or protection, authorize fabrication, or permit connection or powered testing. Fourteen holds remain open.\n")

    hold_html = "".join(f"<li><strong>{r['hold_id']}</strong><span>{html.escape(r['subject'])}</span></li>" for r in hold_rows)
    allocation_html = "".join(f"<tr><td>{r['harness_id']}</td><td>{html.escape(r['role'])}</td><td>{html.escape(r['source_end'])} → {html.escape(r['destination_end'])}</td><td>{r['conductor_count']} conductors; cavity 2 {html.escape(r['cavity_2'])}</td><td>{html.escape(r['allocation'])}</td></tr>" for r in allocation_rows)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.25rem,5.3vw,4.7rem);line-height:1.04;max-width:19ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.6rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:960px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code,.meta,li span{{font-size:14px}}li{{margin:.75rem 0}}li strong{{display:block}}a{{color:#075a96}}</style></head><body><header><div class="meta">{IDENTIFIER} · R153 · 2026-08-09</div><h1>Three cables were already in the boxes.</h1><div class="warning">{WARNING}. This corrects allocation; it does not qualify current or release a harness.</div></header><main><p>Each held ROBOTIS actuator package includes one 180 mm JST-to-JST X3P cable. Those three assembled branch cables are integrated as <code>BOM-086</code>. The only custom signal harness is the two-conductor U2D2-to-JC1 cable.</p><section class="grid"><article><b>3</b>included branch cables</article><article><b>1</b>custom controller cable</article><article><b>22</b>duplicate loose pieces removed</article><article><b>0</b>work authorizations</article></section><div class="boundary"><h2>The important electrical boundary</h2><p>U2D2 cavity 2 is VDD. HAR-CTRL must leave cavity 2 empty at both ends; only GND and DATA are populated. JC1.2 remains no-net/no-copper. This allocation does not resolve the JST EH 3 A rating versus the XM540 4.4 A stall endpoint.</p></div><h2>Harness allocation</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Role</th><th>From → to</th><th>Population</th><th>Disposition</th></tr></thead><tbody>{allocation_html}</tbody></table></div><div class="boundary"><h2>Fourteen holds remain open</h2><ol>{hold_html}</ol></div><p><a href="harness-allocation.csv">allocation</a> · <a href="controller-cable-pinmap.csv">controller pin map</a> · <a href="connector-bom-parity.csv">BOM parity</a> · <a href="acceptance-matrix.csv">acceptance matrix</a> · <a href="manufacturer-questions.csv">manufacturer questions</a> · <a href="receiving-template.csv">receiving form</a> · <a href="current-qualification-template.csv">current form</a></p></main></body></html>'''
    write_text(OUT / "index.html", page)
    manifest_rows = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")]
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    print(f"{IDENTIFIER}: 3 integrated branch cables / 1 custom controller cable / 22 duplicate loose pieces removed / 14 holds OPEN")
    print(WARNING)


if __name__ == "__main__":
    main()
