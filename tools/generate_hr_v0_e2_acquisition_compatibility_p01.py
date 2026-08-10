#!/usr/bin/env python3
"""Generate the R182 E2 acquisition-compatibility candidate package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-equipment/hr-v0/e2-acquisition-compatibility-p0.1"
WEB = ROOT / "release/hr-v0/e2-acquisition-compatibility-p0.1"
IDENTIFIER = "HR-V0-E2-ACQ-COMPAT-P0.1"
WARNING = (
    "PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, "
    "FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    channels = [
        {"channel":"CH1","bank":"1-4","probe":"TCP0030A","max_probe_power_W":"8.4","stop_role":"SR1_S12 stop-event current","reset_arm_role":"SR1_START_RETURN reset-event current","physical_interface":"R180 controlled conductor; received wire identity and jaw fit remain open","state":"CANDIDATE / HOLD"},
        {"channel":"CH2","bank":"1-4","probe":"TCP0030A","max_probe_power_W":"8.4","stop_role":"K1_A1 coil current","reset_arm_role":"ARM_AFTER_S2 arm-event current","physical_interface":"R180 controlled conductor; S2 received terminal remains open","state":"CANDIDATE / HOLD"},
        {"channel":"CH3","bank":"1-4","probe":"TIVP02 + TIVPMX10X","max_probe_power_W":"9.5","stop_role":"K1_STATUS diagnostic voltage","reset_arm_role":"K1_STATUS diagnostic voltage","physical_interface":"protected diagnostic load and return are SELECTION REQUIRED; zero safety credit","state":"CANDIDATE / HOLD"},
        {"channel":"CH4","bank":"1-4","probe":"TIVP02 + TIVPMX10X","max_probe_power_W":"9.5","stop_role":"K2_STATUS diagnostic voltage","reset_arm_role":"K2_STATUS diagnostic voltage","physical_interface":"protected diagnostic load and return are SELECTION REQUIRED; zero safety credit","state":"CANDIDATE / HOLD"},
        {"channel":"CH5","bank":"5-8","probe":"TCP0030A","max_probe_power_W":"8.4","stop_role":"K2_A1 coil current","reset_arm_role":"K1_A1 coil current","physical_interface":"R180 controlled conductor; received wire identity and jaw fit remain open","state":"CANDIDATE / HOLD"},
        {"channel":"CH6","bank":"5-8","probe":"TCP0030A","max_probe_power_W":"8.4","stop_role":"common SRA1_START_RETURN EDM-chain current","reset_arm_role":"K2_A1 coil current","physical_interface":"one series-chain observation only; no individual mirror-contact identity","state":"CANDIDATE / HOLD"},
        {"channel":"CH7","bank":"5-8","probe":"TIVP02 + TIVPMX10X","max_probe_power_W":"9.5","stop_role":"SAFETY_24V relative to SAFETY_0V","reset_arm_role":"SAFETY_24V relative to SAFETY_0V","physical_interface":"exact protected test points and connection method are SELECTION REQUIRED","state":"CANDIDATE / HOLD"},
        {"channel":"CH8","bank":"5-8","probe":"TIVP02 + TIVPMX10X","max_probe_power_W":"9.5","stop_role":"Q4X analog independent no-motion witness","reset_arm_role":"Q4X analog independent no-motion witness","physical_interface":"Q4X pin 4 analog out relative to pin 5 analog ground; cable, supply, mount, target and limits remain open","state":"CANDIDATE / HOLD"},
    ]
    write_csv("channel-population.csv", channels)

    budgets = [
        {"scope":"MSO58B channels 1-4","tcp0030a_count":"2","tivp02_count":"2","calculated_max_W":"35.8","manufacturer_limit_W":"40.0","margin_W":"4.2","arithmetic_state":"PASS ON DOCUMENTED MAXIMA","release_state":"HOLD - physical compatibility not executed"},
        {"scope":"MSO58B channels 5-8","tcp0030a_count":"2","tivp02_count":"2","calculated_max_W":"35.8","manufacturer_limit_W":"40.0","margin_W":"4.2","arithmetic_state":"PASS ON DOCUMENTED MAXIMA","release_state":"HOLD - physical compatibility not executed"},
        {"scope":"MSO58B total","tcp0030a_count":"4","tivp02_count":"4","calculated_max_W":"71.6","manufacturer_limit_W":"80.0","margin_W":"8.4","arithmetic_state":"PASS ON DOCUMENTED MAXIMA","release_state":"HOLD - exact host configuration, firmware and installed-probe check open"},
    ]
    write_csv("probe-power-budget.csv", budgets)

    motion = [
        {"record_id":"MW-001","item":"Banner Q4XFULAF110-Q8 / part 97540","controlled_fact":"flush-mount Class 1 visible-red laser; 35-110 mm; 0-10 V; 12-30 Vdc; 5-pin M12; 0.5 ms minimum response","source_state":"VERIFIED IN CURRENT MANUFACTURER PRODUCT PAGE AND 27-MAR-2026 MANUAL","release_state":"EXACT EVALUATION CANDIDATE / HOLD"},
        {"record_id":"MW-002","item":"Q4X analog interface","controlled_fact":"pin 4 black analog out relative to pin 5 gray analog ground; Q4X..U load resistance 2.5 kohm minimum","source_state":"VERIFIED IN MANUAL","release_state":"TIVP02 connection candidate only; no cable or field connection released"},
        {"record_id":"MW-003","item":"Q4X power/interface","controlled_fact":"pin 1 brown 12-30 Vdc; pin 3 blue supply return; pin 2 white remote input; shield shown separately","source_state":"VERIFIED IN MANUAL","release_state":"instrumentation supply, overcurrent protection, shield termination and cable are SELECTION REQUIRED"},
        {"record_id":"MW-004","item":"TIVP02 + TIVPMX10X observation","controlled_fact":"200 MHz; +/-50 V differential range; 10 Mohm || 2.8 pF; 18.3 ns 2 m propagation delay","source_state":"VERIFIED IN CURRENT TEKTRONIX DATA","release_state":"loading arithmetic is compatible on paper; physical connection and deskew remain open"},
        {"record_id":"MW-005","item":"E2 interpretation","controlled_fact":"Q4X is an independent displacement witness only for guarded disconnected-load no-motion evidence","source_state":"PROJECT BOUNDARY","release_state":"no joint-angle, powered stopping, clearance or safety-function credit"},
    ]
    write_csv("motion-witness-register.csv", motion)

    sources = [
        {"source_id":"SRC-001","manufacturer":"Tektronix","document":"5 Series B MSO Specifications and Performance Verification","revision_date":"077172502; 2025-07-29","locator":"https://www.tek.com/en/support/datasheets-manuals-software-downloads?series=5+Series+B+MSO","controlled_use":"8 TekVPI inputs; 80 W total; 40 W channels 1-4 and 40 W channels 5-8; 20 W software limit per channel","verification_date":"2026-08-10"},
        {"source_id":"SRC-002","manufacturer":"Tektronix","document":"TekVPI Probe Power Requirements","revision_date":"55W-28827-8; May 2024","locator":"https://download.tek.com/document/TekVPI%20Power%20Requirements%2055W-28827-8%201.pdf","controlled_use":"TCP0030/A maximum 8.4 W; TIVP02/05/1 maximum 9.5 W","verification_date":"2026-08-10"},
        {"source_id":"SRC-003","manufacturer":"Tektronix","document":"TCP0030A Datasheet","revision_date":"51W-19042-12; 2025-04-10","locator":"https://download.tek.com/datasheet/TCP0030A-Datasheet_51W1904212.pdf","controlled_use":"30 A / 5 A ranges; DC to >120 MHz; 5 mm conductor; 14.5 ns signal delay","verification_date":"2026-08-10"},
        {"source_id":"SRC-004","manufacturer":"Tektronix","document":"TIVP1 TIVP05 TIVP02 Datasheet","revision_date":"51W-61655-7; 2026-06-14","locator":"https://www.tek.com/en/datasheet/isolated-measurement-systems-tivp1-tivp05-tivp02-datasheet","controlled_use":"TIVP02 200 MHz; TIVPMX10X +/-50 V, 10 Mohm || 2.8 pF; 18.3 ns 2 m delay","verification_date":"2026-08-10"},
        {"source_id":"SRC-005","manufacturer":"Banner Engineering","document":"Q4XFULAF110-Q8 product page / part 97540","revision_date":"live page checked 2026-08-10","locator":"https://www.bannerengineering.com/us/en/products/part.97540.html","controlled_use":"35-110 mm; 0-10 V; 12-30 Vdc; 5-pin M12; Class 1; 0.5 ms minimum response","verification_date":"2026-08-10"},
        {"source_id":"SRC-006","manufacturer":"Banner Engineering","document":"Q4X Stainless Steel Analog Laser Sensor Product Manual","revision_date":"185624 Rev J; 2026-03-27","locator":"https://info.bannerengineering.com/cs/groups/public/documents/literature/185624.pdf","controlled_use":"model/output/range; power; wiring; loading; response; resolution; mount/orientation requirements","verification_date":"2026-08-10"},
    ]
    write_csv("source-register.csv", sources)

    holds = [
        ("H-001","MSO58B exact order configuration, installed firmware, serial number and calibration status"),
        ("H-002","four TCP0030A and four TIVP02 received identities, calibration, self-check and balanced installed-probe power check"),
        ("H-003","current-probe jaw fit, conductor separation, polarity, loading/noninterference and as-built wire identity"),
        ("H-004","K1/K2 protected diagnostic loads, return paths, thresholds and single-fault analysis"),
        ("H-005","exact protected SAFETY_24V/SAFETY_0V test points and connection method"),
        ("H-006","Q4X M12 cordset order code, length, bend/retention, shield termination and pin-continuity evidence"),
        ("H-007","isolated instrumentation supply, branch protection, grounding and no-backfeed evidence for Q4X"),
        ("H-008","Q4X mount, target material/geometry, 35-110 mm operating distance, occlusion and cross-axis-motion controls"),
        ("H-009","Q4X configuration: teach points, slope, base rate, averaging, loss-of-signal behavior and locked setup"),
        ("H-010","accepted no-motion threshold derived from calibration, repeatability, target reflectance, temperature, alignment and uncertainty"),
        ("H-011","scope sample rate, record length, trigger, coupling, ranges, deskew, filtering, timebase and uncertainty budget"),
        ("H-012","complete physical channel connection schedule, checkout procedure and qualified pre-test review"),
        ("H-013","authorized guarded disconnected-load E2 run, immutable raw traces and independent witness"),
        ("H-014","separate powered-motion stopping architecture; Q4X E2 candidate does not close powered stopping or clearance"),
        ("H-015","qualified electrical and functional-safety disposition; all instrumentation retains zero safety credit"),
    ]
    write_csv("closure-holds.csv", [
        {"hold_id": key, "unresolved_selection_or_evidence": value, "state":"SELECTION REQUIRED", "work_authority":"NONE", "warning":WARNING}
        for key, value in holds
    ])

    inquiries = [
        {"inquiry_id":"INQ-001","recipient":"Tektronix technical support","question":"Confirm current supported simultaneous population of four TCP0030A and four TIVP02 on an MSO58B, balanced as two plus two per bank, and identify any firmware/configuration/calibration restrictions.","state":"NOT SENT","authority":"NONE"},
        {"inquiry_id":"INQ-002","recipient":"Banner Engineering technical support","question":"Confirm Q4XFULAF110-Q8 suitability for sub-millimeter no-motion witnessing at the proposed target distance/material after the exact mount and acceptance threshold are defined; confirm recommended cordset and shield treatment.","state":"NOT SENT","authority":"NONE"},
    ]
    write_csv("manufacturer-inquiry-register.csv", inquiries)

    status = {
        "identifier": IDENTIFIER,
        "round": "R182",
        "status": WARNING,
        "host_candidate": "MSO58B",
        "channel_count": 8,
        "tcp0030a_count": 4,
        "tivp02_count": 4,
        "documented_max_probe_power_W": 71.6,
        "host_total_limit_W": 80.0,
        "bank_max_probe_power_W": 35.8,
        "host_bank_limit_W": 40.0,
        "motion_candidate": "Q4XFULAF110-Q8 / 97540",
        "open_hold_count": len(holds),
        "physical_compatibility_run_count": 0,
        "released_connection_count": 0,
        "safety_function_credit": "ZERO",
        "gate_effect": {"EG-025":"OPEN", "EG-026":"PARTIAL"},
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    power_cards = "".join(
        f"<article class='card'><h3>{escape(row['scope'])}</h3><p class='big'>{row['calculated_max_W']} W / {row['manufacturer_limit_W']} W</p><p>Documented margin: {row['margin_W']} W.</p><span class='badge'>{escape(row['release_state'])}</span></article>"
        for row in budgets
    )
    hold_cards = "".join(
        f"<article class='hold'><h3>{escape(key)}</h3><p>{escape(value)}</p><span class='badge'>SELECTION REQUIRED</span></article>"
        for key, value in holds
    )
    channel_rows = "".join(
        f"<tr><td>{escape(row['channel'])}</td><td>{escape(row['bank'])}</td><td>{escape(row['probe'])}</td><td>{escape(row['stop_role'])}</td><td>{escape(row['reset_arm_role'])}</td></tr>"
        for row in channels
    )
    html = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{IDENTIFIER}</title><style>
:root{{--sky:#dff4ff;--blue:#0b2d5c;--mid:#1469a8;--gold:#f3bf26;--ink:#102033;--paper:#f8fbff;--line:#8fb8d5}}
*{{box-sizing:border-box}} body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}
header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}
main{{max-width:1200px;margin:auto;padding:clamp(18px,4vw,48px)}} h1{{font-size:clamp(32px,6vw,64px);line-height:1.05;color:var(--blue);margin:.25rem 0 1rem}} h2{{font-size:clamp(24px,3vw,36px);color:var(--blue);margin-top:2.2rem}} h3{{font-size:18px;color:var(--blue);margin:.1rem 0 .6rem}}
.warn{{background:#fff3c4;border:3px solid #805d00;padding:18px;font-weight:750;color:#503900}} .lead{{font-size:20px;max-width:900px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:16px}} .card,.hold{{min-width:0;background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #cfe8f7}} .big{{font-size:28px;font-weight:800;color:var(--mid);margin:.4rem 0}}
.badge{{display:inline-block;font-size:14px;font-weight:750;background:var(--gold);color:#17253b;border-radius:999px;padding:5px 10px;overflow-wrap:anywhere}}
.table-wrap{{overflow-x:auto;border:2px solid var(--line);border-radius:12px;background:#fff}} table{{width:100%;border-collapse:collapse;min-width:850px}} th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #c8dce9;font-size:14px}} th{{background:var(--blue);color:white}}
.decision{{border-left:8px solid var(--gold);background:var(--sky);padding:18px;margin:18px 0}} code{{font-size:14px;overflow-wrap:anywhere}} a{{color:#075b99}} footer{{margin-top:36px;padding:24px;background:var(--blue);color:white}}
@media(max-width:520px){{header,main{{padding:18px}} .lead{{font-size:18px}} .card,.hold{{padding:15px}}}}
</style></head><body><header><p class='badge'>R182 · ACQUISITION COMPATIBILITY</p><h1>Eight channels fit on paper. Physical use stays held.</h1><p class='lead'>A balanced MSO58B population can support the two R181 disconnected-load E2 runs while adding an exact Banner laser-displacement candidate for the independent no-motion channel.</p></header><main>
<p class='warn'>{escape(WARNING)}</p>
<section><h2>Decision</h2><div class='decision'><strong>Documented power arithmetic passes.</strong> Four TCP0030A probes and four TIVP02 probes total 71.6 W. Each four-channel bank carries 35.8 W. This does not prove a received instrument population, calibration, physical connection, noninterference, or a test result.</div><div class='grid'>{power_cards}</div></section>
<section><h2>One population, two separate runs</h2><p>STOP and RESET/ARM remain separate acquisitions. No cross-run simultaneity is claimed.</p><div class='table-wrap'><table><thead><tr><th>Channel</th><th>Bank</th><th>Probe</th><th>STOP role</th><th>RESET/ARM role</th></tr></thead><tbody>{channel_rows}</tbody></table></div></section>
<section><h2>Independent E2 no-motion witness</h2><div class='decision'><strong>Exact evaluation candidate:</strong> Banner <code>Q4XFULAF110-Q8</code>, part <code>97540</code>. Manufacturer data gives 35–110 mm range, 0–10 V output, 12–30 Vdc input and 0.5 ms minimum response. CH8 observes pin 4 relative to pin 5 through a fourth TIVP02. The cable, supply, protection, mount, target, configuration and acceptance limit remain <strong>SELECTION REQUIRED</strong>.</div><p>This sensor can witness absence of displacement in guarded disconnected-load E2. It is not credited as a safety device and does not close joint-angle measurement, powered stopping time, residual travel or guard clearance.</p></section>
<section><h2>What still blocks connection</h2><div class='grid'>{hold_cards}</div></section>
<section><h2>Gate effect</h2><p><strong>EG-025 remains OPEN. EG-026 remains PARTIAL.</strong> Zero physical compatibility runs, zero released connections and zero safety-function credit exist.</p></section>
</main><footer>{escape(WARNING)}</footer></body></html>"""
    (WEB / "index.html").write_text(html, encoding="utf-8")

    print(f"generated {IDENTIFIER}: 8 channels, 71.6 W total, 15 holds, 0 physical runs")


if __name__ == "__main__":
    main()
