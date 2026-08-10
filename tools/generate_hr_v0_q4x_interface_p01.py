#!/usr/bin/env python3
"""Generate the R183 Q4X E2 witness physical-interface candidate package."""

from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-equipment/hr-v0/q4x-interface-p0.1"
WEB = ROOT / "release/hr-v0/q4x-interface-p0.1"
FORM_DIR = ROOT / "tests/forms"
IDENTIFIER = "HR-V0-Q4X-IF-P0.1"
WARNING = (
    "PRELIMINARY - EVALUATION CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, "
    "FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    FORM_DIR.mkdir(parents=True, exist_ok=True)

    equipment = [
        {"item_id":"Q4X1","manufacturer":"Banner Engineering","exact_model_or_part":"Q4XFULAF110-Q8 / 97540","role":"independent displacement witness for guarded disconnected-load E2 only","controlled_fact":"12-30 Vdc; 0-10 V; 35-110 mm; 5-pin M12; Class 1 laser","state":"EXACT EVALUATION CANDIDATE / HOLD","safety_credit":"ZERO"},
        {"item_id":"CBL-Q4X1","manufacturer":"Banner Engineering","exact_model_or_part":"BC-M12F5-22-2-SF / 815158","role":"sensor-to-flying-lead cordset","controlled_fact":"2 m; single-ended M12 5-pin straight female; five 22 AWG conductors; black PVC; shielded","state":"EXACT EVALUATION CANDIDATE / HOLD","safety_credit":"ZERO"},
        {"item_id":"BR-Q4X1","manufacturer":"Banner Engineering","exact_model_or_part":"SMBQ4XFA / 91512","role":"Q4X pan/tilt bracket on a later selected 12 mm rod/support","controlled_fact":"zinc Zamak; Q4X-compatible; pan/tilt; mounting hardware included; official bolt-length records disagree","state":"EXACT EVALUATION CANDIDATE / MANUFACTURER CLARIFICATION REQUIRED","safety_credit":"ZERO"},
        {"item_id":"PS-Q4X1","manufacturer":"Keithley / Tektronix","exact_model_or_part":"2220-30-1, channel 1 only","role":"temporary independent floating Q4X instrumentation source","controlled_fact":"two independent isolated 0-30 V / 0-1.5 A channels; independently controlled outputs; linear supply","state":"EXACT EVALUATION CANDIDATE / HOLD","safety_credit":"ZERO"},
        {"item_id":"VP-Q4X1","manufacturer":"Tektronix","exact_model_or_part":"TIVP02 + TIVPMX10X","role":"isolated observation of Q4X analog output","controlled_fact":"positive observes pin 4; negative observes pin 5; physical lead arrangement remains held","state":"R182 EXACT EVALUATION CANDIDATE / HOLD","safety_credit":"ZERO"},
        {"item_id":"PROT-Q4X1","manufacturer":"SELECTION REQUIRED","exact_model_or_part":"SELECTION REQUIRED","role":"Q4X instrumentation-source branch protection and termination enclosure","controlled_fact":"rating, interrupting capability, terminals, conductor, enclosure and location unresolved","state":"SELECTION REQUIRED","safety_credit":"ZERO"},
        {"item_id":"TGT-Q4X1","manufacturer":"SELECTION REQUIRED","exact_model_or_part":"SELECTION REQUIRED","role":"calibration and no-motion witness target","controlled_fact":"material, finish, dimensions, mounting and reflectance unresolved; BRT-Q4X-60X50 is not selected","state":"SELECTION REQUIRED","safety_credit":"ZERO"},
    ]
    write_csv(OUT / "equipment-register.csv", equipment)

    pins = [
        {"record_id":"IF-001","source":"PS-Q4X1 CH1 positive","intermediate":"PROT-Q4X1 exact device/terminals SELECTION REQUIRED","destination":"CBL-Q4X1 brown -> Q4X1 pin 1","candidate_function":"sensor supply positive; 24.0 V candidate","released":"NO","hold":"protection, conductor termination, enclosure, current limit and received continuity"},
        {"record_id":"IF-002","source":"PS-Q4X1 CH1 negative","intermediate":"exact terminal/termination SELECTION REQUIRED","destination":"CBL-Q4X1 blue -> Q4X1 pin 3","candidate_function":"sensor supply return inside temporary instrumentation domain","released":"NO","hold":"termination, isolation measurement and received continuity"},
        {"record_id":"IF-003","source":"CBL-Q4X1 white -> Q4X1 pin 2","intermediate":"separately insulated identified parking terminal SELECTION REQUIRED","destination":"NO EXTERNAL DRIVE","candidate_function":"remote input left inactive; configuration must be verified","released":"NO","hold":"exact parking terminal/enclosure and locked sensor setup"},
        {"record_id":"IF-004","source":"CBL-Q4X1 black -> Q4X1 pin 4","intermediate":"TIVPMX10X positive lead","destination":"TIVP02 / MSO58B CH8","candidate_function":"0-10 V analog displacement observation","released":"NO","hold":"received continuity, lead arrangement, range, deskew and calibration"},
        {"record_id":"IF-005","source":"CBL-Q4X1 gray -> Q4X1 pin 5","intermediate":"TIVPMX10X negative lead","destination":"TIVP02 / MSO58B CH8","candidate_function":"analog ground reference only inside Q4X domain","released":"NO","hold":"received continuity, lead arrangement and domain isolation"},
        {"record_id":"IF-006","source":"CBL-Q4X1 shield/drain","intermediate":"labeled isolated shield terminal SELECTION REQUIRED","destination":"SELECTION REQUIRED","candidate_function":"shield treatment must follow accepted EMI/grounding review","released":"NO","hold":"termination end/location and chassis/PE decision"},
        {"record_id":"IF-007","source":"PS-Q4X1 CH1 remote-sense terminals","intermediate":"NONE","destination":"NO CONNECTION CANDIDATE","candidate_function":"local sensing only unless later selected and verified","released":"NO","hold":"received setup and manufacturer-compliant configuration"},
        {"record_id":"IF-008","source":"PS-Q4X1 channel 2 and other outputs","intermediate":"NONE","destination":"NO CONNECTION","candidate_function":"remain disabled for this candidate","released":"NO","hold":"pre-use configuration inspection"},
    ]
    write_csv(OUT / "pin-connection-schedule.csv", pins)

    domains = [
        {"boundary_id":"DB-001","from_domain":"Q4X temporary instrumentation domain","to_domain":"robot SAFETY_24V / SAFETY_0V","required_state":"NO INTENTIONAL CONNECTION","verification":"unpowered isolation measurement method and acceptance limit SELECTION REQUIRED","state":"HOLD"},
        {"boundary_id":"DB-002","from_domain":"Q4X temporary instrumentation domain","to_domain":"protective earth / chassis","required_state":"NO INTENTIONAL CONNECTION unless qualified review explicitly selects a point","verification":"unpowered isolation measurement and visual inspection","state":"HOLD"},
        {"boundary_id":"DB-003","from_domain":"Q4X temporary instrumentation domain","to_domain":"contactor / E-stop / reset / watchdog circuits","required_state":"NO CONNECTION","verification":"independent second-person wire trace before any authorized run","state":"HOLD"},
        {"boundary_id":"DB-004","from_domain":"Q4X temporary instrumentation domain","to_domain":"actuator source / DXL rails / DXL returns","required_state":"NO CONNECTION","verification":"unpowered isolation measurement and visual inspection","state":"HOLD"},
        {"boundary_id":"DB-005","from_domain":"Q4X analog pair","to_domain":"MSO58B chassis","required_state":"only through received TIVP02 isolated measurement system","verification":"received probe identity, calibration, self-check and permitted-lead inspection","state":"HOLD"},
        {"boundary_id":"DB-006","from_domain":"PS-Q4X1 CH1","to_domain":"other 2220-30-1 channel","required_state":"independent isolated outputs retained; CH2 disabled and unconnected","verification":"received-instrument configuration and isolation test","state":"HOLD"},
    ]
    write_csv(OUT / "domain-separation-register.csv", domains)

    configs = [
        {"parameter_id":"CFG-QX-001","parameter":"PS-Q4X1 output voltage","candidate":"24.0 Vdc","release_state":"CANDIDATE / NOT RELEASED","closure_evidence":"received supply accuracy check, voltage-drop budget and qualified acceptance"},
        {"parameter_id":"CFG-QX-002","parameter":"PS-Q4X1 current limit","candidate":"SELECTION REQUIRED","release_state":"NOT RELEASED","closure_evidence":"sensor/cable/protection limits, low-setting behavior, inrush and fault campaign"},
        {"parameter_id":"CFG-QX-003","parameter":"PROT-Q4X1 protection","candidate":"SELECTION REQUIRED","release_state":"NOT RELEASED","closure_evidence":"available fault current, interrupting capability, conductor/terminal limits and jurisdiction"},
        {"parameter_id":"CFG-QX-004","parameter":"operating distance","candidate":"within manufacturer 35-110 mm range","release_state":"EXACT DISTANCE NOT RELEASED","closure_evidence":"selected target, support geometry, full-stroke clearance and calibration"},
        {"parameter_id":"CFG-QX-005","parameter":"base response / averaging","candidate":"0.3 ms + average 1 timing screen OR 0.3 ms + average 16 repeatability screen","release_state":"CONTROLLED ALTERNATIVES / NOT RELEASED","closure_evidence":"received-sensor tests and E2 timing/uncertainty budget"},
        {"parameter_id":"CFG-QX-006","parameter":"teach endpoints / slope / output mapping","candidate":"SELECTION REQUIRED","release_state":"NOT RELEASED","closure_evidence":"fixture travel, target and analyzer convention"},
        {"parameter_id":"CFG-QX-007","parameter":"remote-input function","candidate":"inactive/off","release_state":"CANDIDATE / VERIFY ON RECEIVED SENSOR","closure_evidence":"locked configuration record and reset/power-cycle persistence test"},
        {"parameter_id":"CFG-QX-008","parameter":"loss-of-signal behavior","candidate":"SELECTION REQUIRED","release_state":"NOT RELEASED","closure_evidence":"fault injection and fail-closed analyzer disposition"},
        {"parameter_id":"CFG-QX-009","parameter":"no-motion acceptance threshold","candidate":"SELECTION REQUIRED","release_state":"CATALOG VALUE PROHIBITED","closure_evidence":"received calibration, uncertainty, drift, fixture stiffness, reflectance, alignment and temperature"},
        {"parameter_id":"CFG-QX-010","parameter":"scope range / timebase / record / trigger / deskew / filtering","candidate":"SELECTION REQUIRED","release_state":"NOT RELEASED","closure_evidence":"complete R181 E2 timing contract and received acquisition stack"},
    ]
    write_csv(OUT / "configuration-candidate-register.csv", configs)

    campaign = [
        {"step_id":"CAL-001","stage":"receiving","action":"record exact Q4X, cordset, bracket, supply and probe identities, labels, condition and calibration state","required_evidence":"photos, serials, certificates/status and quarantine disposition","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
        {"step_id":"CAL-002","stage":"unpowered continuity","action":"prove cordset conductor-to-M12-pin identity and absence of unintended conductor/shield shorts","required_evidence":"meter identity, raw readings and second-person witness","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
        {"step_id":"CAL-003","stage":"unpowered isolation","action":"prove Q4X domain isolation from robot returns, PE/chassis and other supply channel","required_evidence":"accepted method, instrument, raw readings and connection photos","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
        {"step_id":"CAL-004","stage":"fixture inspection","action":"verify selected target, 35-110 mm geometry, rigidity, fastener retention, full-stroke clearance, occlusion and cross-axis rejection","required_evidence":"dimensioned as-built record and photographs","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
        {"step_id":"CAL-005","stage":"configuration","action":"record output voltage/current limit, Q4X teach/slope/rate/averaging/remote/loss settings and scope setup","required_evidence":"configuration snapshot and independent check","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
        {"step_id":"CAL-006","stage":"warm-up","action":"allow at least the manufacturer-recommended 10 minute warm-up before optimum-performance calibration","required_evidence":"timestamped log","execution_state":"NOT EXECUTED","acceptance":"10 minutes minimum after authorized power application"},
        {"step_id":"CAL-007","stage":"static calibration","action":"collect repeated sensor-display and analog-output data over selected distances after power cycles and connector re-seats","required_evidence":"immutable raw data, configuration hash and witness","execution_state":"NOT EXECUTED","acceptance":"repetitions/distances SELECTION REQUIRED"},
        {"step_id":"CAL-008","stage":"environment / nuisance","action":"repeat at accepted ambient range, target orientations and alignment offsets; record saturation/loss flags","required_evidence":"raw data and uncertainty components","execution_state":"NOT EXECUTED","acceptance":"campaign bounds SELECTION REQUIRED"},
        {"step_id":"CAL-009","stage":"analysis","action":"fit accepted voltage-to-displacement mapping and calculate repeatability, drift, noise and complete uncertainty","required_evidence":"versioned analysis and independent review","execution_state":"NOT EXECUTED","acceptance":"method and limit SELECTION REQUIRED"},
        {"step_id":"CAL-010","stage":"E2 release review","action":"select no-motion threshold only from received calibration and reconcile it with R181 acquisition/timing contract","required_evidence":"signed qualified electrical and functional-safety disposition","execution_state":"NOT EXECUTED","acceptance":"SELECTION REQUIRED"},
    ]
    write_csv(OUT / "calibration-campaign.csv", campaign)

    sources = [
        {"source_id":"SRC-QX-001","manufacturer":"Banner Engineering","document":"Q4XFULAF110-Q8 product page, part 97540","revision_date":"live page checked 2026-08-10","locator":"https://www.bannerengineering.com/us/en/products/part.97540.html","controlled_use":"exact sensor identity and headline electrical/optical attributes","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-002","manufacturer":"Banner Engineering","document":"Q4X Stainless Steel Analog Laser Sensor Product Manual","revision_date":"185624 Rev J; 2026-03-27","locator":"https://info.bannerengineering.com/cs/groups/public/documents/literature/185624.pdf","controlled_use":"pins, colors, power, output, range, response/averaging, warm-up and bracket family","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-003","manufacturer":"Banner Engineering","document":"BC-M12F5-22-2-SF product page, part 815158","revision_date":"live page checked 2026-08-10","locator":"https://www.bannerengineering.com/us/en/products/part.815158.html","controlled_use":"exact 2 m shielded five-conductor M12-female-to-flying-lead cordset candidate","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-004","manufacturer":"Banner Engineering","document":"SMBQ4XFA product page, part 91512","revision_date":"live page checked 2026-08-10","locator":"https://www.bannerengineering.com/be/en/products/part.91512.html","controlled_use":"exact Q4X pan/tilt bracket candidate and product-page hardware statement","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-005","manufacturer":"Banner Engineering","document":"BRT-Q4X-60X50 product page, part 95777","revision_date":"live page checked 2026-08-10","locator":"https://www.bannerengineering.com/us/en/products/part.95777.html","controlled_use":"candidate screened but not selected due application/laser-compatibility ambiguity","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-006","manufacturer":"Keithley / Tektronix","document":"Series 2200 multiple-channel DC power supplies product page","revision_date":"live page checked 2026-08-10","locator":"https://www.tek.com/en/products/dc-power-supplies/2220-2230-2231-series","controlled_use":"2220-30-1 current product identity and isolated independently controlled outputs","verification_date":"2026-08-10"},
        {"source_id":"SRC-QX-007","manufacturer":"Keithley / Tektronix","document":"Series 2200 multiple-channel power supplies specifications","revision_date":"2220S-905-01 Rev B; December 2013","locator":"https://download.tek.com/manual/2220S-905-01_B_Dec_2013_Spec.pdf","controlled_use":"2220-30-1 two independent isolated 0-30 V / 0-1.5 A channels, accuracy and noise","verification_date":"2026-08-10"},
    ]
    write_csv(OUT / "source-register.csv", sources)

    holds = [
        ("H-001","received identities, calibration/status and condition for sensor, cordset, bracket, supply and isolated probe"),
        ("H-002","exact branch protection, current limit, conductors, terminations, enclosure, available fault current and site/jurisdiction review"),
        ("H-003","accepted unpowered isolation/no-backfeed method and limits for robot returns, PE/chassis and other supply channels"),
        ("H-004","remote-input parking terminal and shield termination end/location; no connection may be inferred"),
        ("H-005","SMBQ4XFA official bolt-length discrepancy plus exact 12 mm support rod, base, fasteners, stiffness and retention"),
        ("H-006","exact target material, finish, dimensions, attachment and reflectance; BRT-Q4X-60X50 is not selected"),
        ("H-007","exact operating distance, alignment, travel clearance, occlusion and cross-axis rejection"),
        ("H-008","locked teach points, slope, response/averaging, remote-input and loss-of-signal configuration"),
        ("H-009","executed static calibration, repeatability/drift/noise data, complete uncertainty and accepted no-motion threshold"),
        ("H-010","scope range, timebase, sample rate, record length, trigger, coupling, deskew and filtering"),
        ("H-011","complete released physical connection schedule, checkout procedure and independent qualified pre-test review"),
        ("H-012","authorized guarded disconnected-load E2 run, immutable raw traces and independent witness"),
        ("H-013","separate powered-motion stopping architecture; this witness does not establish stopping or clearance"),
        ("H-014","qualified electrical and functional-safety disposition; all instrumentation retains zero safety credit"),
    ]
    write_csv(OUT / "closure-holds.csv", [
        {"hold_id": key, "unresolved_selection_or_evidence": value, "state":"SELECTION REQUIRED", "work_authority":"NONE", "warning":WARNING}
        for key, value in holds
    ])

    receiving = []
    for item in ("Q4X1","CBL-Q4X1","BR-Q4X1","PS-Q4X1","VP-Q4X1"):
        for check in ("identity","condition","documentation","calibration_or_status"):
            receiving.append({"item_id":item,"check":check,"observed_value":"","evidence_location":"","inspector":"SELECTION REQUIRED","date_time":"","result":"NOT EXECUTED","disposition":"HOLD"})
    write_csv(FORM_DIR / "hr-v0-q4x-receiving-template-p0.1.csv", receiving)

    calibration = []
    for run in range(1, 13):
        calibration.append({"run_id":f"QX-CAL-{run:03d}","timestamp":"","configuration_hash":"","power_cycle_id":"","supply_V":"","supply_A":"","ambient_C":"","target_id":"SELECTION REQUIRED","commanded_distance_mm":"","sensor_display_mm":"","analog_output_V":"","tivp_output_V":"","inferred_displacement_mm":"","alignment_state":"","saturation_or_loss_flag":"","raw_data_location":"","witness":"SELECTION REQUIRED","result":"NOT EXECUTED"})
    write_csv(FORM_DIR / "hr-v0-q4x-static-calibration-template-p0.1.csv", calibration)

    status = {
        "identifier": IDENTIFIER,
        "round": "R183",
        "status": WARNING,
        "exact_candidate_count": 5,
        "selection_required_item_count": 2,
        "pin_schedule_row_count": len(pins),
        "domain_boundary_count": len(domains),
        "configuration_row_count": len(configs),
        "calibration_step_count": len(campaign),
        "source_count": len(sources),
        "open_hold_count": len(holds),
        "physical_run_count": 0,
        "released_connection_count": 0,
        "released_protection_count": 0,
        "robot_baseline_change_count": 0,
        "safety_function_credit": "ZERO",
        "gate_effect": {"EG-025":"OPEN", "EG-026":"PARTIAL"},
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    equipment_cards = "".join(
        f"<article class='card'><p class='eyebrow'>{escape(row['item_id'])}</p><h3>{escape(row['exact_model_or_part'])}</h3><p>{escape(row['role'])}</p><span class='badge'>{escape(row['state'])}</span></article>"
        for row in equipment
    )
    pin_rows = "".join(
        f"<tr><td>{escape(row['record_id'])}</td><td>{escape(row['source'])}</td><td>{escape(row['destination'])}</td><td>{escape(row['candidate_function'])}</td><td>{escape(row['hold'])}</td></tr>"
        for row in pins
    )
    hold_cards = "".join(
        f"<article class='hold'><h3>{escape(key)}</h3><p>{escape(value)}</p><span class='badge'>SELECTION REQUIRED</span></article>"
        for key, value in holds
    )
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{IDENTIFIER}</title><style>
:root{{--sky:#dff4ff;--blue:#0b2d5c;--mid:#1469a8;--gold:#f3bf26;--ink:#102033;--paper:#f8fbff;--line:#8fb8d5}}
*{{box-sizing:border-box}} body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}
header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}} main{{max-width:1200px;margin:auto;padding:clamp(18px,4vw,48px)}}
h1{{font-size:clamp(34px,6vw,68px);line-height:1.04;color:var(--blue);margin:.3rem 0 1rem}} h2{{font-size:clamp(25px,3vw,38px);color:var(--blue);margin-top:2.4rem}} h3{{font-size:18px;color:var(--blue);margin:.2rem 0 .7rem}}
.lead{{font-size:20px;max-width:920px}} .warn{{background:#fff3c4;border:3px solid #805d00;padding:18px;font-weight:800;color:#503900}}
.decision{{border-left:8px solid var(--gold);background:var(--sky);padding:20px;margin:18px 0}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:16px}}
.card,.hold{{min-width:0;background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #cfe8f7}} .eyebrow{{font-size:14px;font-weight:800;color:var(--mid);margin:0}}
.badge{{display:inline-block;font-size:14px;font-weight:800;background:var(--gold);color:#17253b;border-radius:999px;padding:6px 10px;overflow-wrap:anywhere}}
.table-wrap{{overflow-x:auto;border:2px solid var(--line);border-radius:12px;background:#fff}} table{{width:100%;border-collapse:collapse;min-width:1000px}} th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #c8dce9;font-size:14px}} th{{background:var(--blue);color:#fff}}
.flow{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center;background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px}} .node{{padding:15px;background:var(--sky);border-radius:10px;font-weight:750}} .arrow{{font-size:24px;color:var(--mid)}} code{{font-size:14px;overflow-wrap:anywhere}} footer{{margin-top:36px;padding:24px;background:var(--blue);color:#fff}}
@media(max-width:720px){{.flow{{grid-template-columns:1fr}} .arrow{{transform:rotate(90deg);text-align:center}} header,main{{padding:18px}} .lead{{font-size:18px}}}}
</style></head><body><header><p class='badge'>R183 - Q4X INTERFACE CANDIDATE</p><h1>The witness has a route. Nothing is released to connect.</h1><p class='lead'>An exact sensor, cordset, bracket, isolated bench-supply channel and isolated probe can now be reviewed as one temporary E2 instrumentation chain. Protection, target, grounding details, fixture geometry and calibration still stop physical use.</p></header><main>
<p class='warn'>{escape(WARNING)}</p>
<section><h2>Controlled boundary</h2><div class='decision'><strong>Robot baseline unchanged.</strong> The Q4X domain must not borrow robot safety power and must not connect to E-stop, reset, watchdog, contactor, actuator or DXL circuits. All listed connections are candidates for qualified review, not wiring instructions.</div><div class='flow'><div class='node'>Keithley 2220-30-1<br>isolated CH1</div><div class='arrow' aria-hidden='true'>-&gt;</div><div class='node'>Protection and terminals<br>SELECTION REQUIRED</div><div class='arrow' aria-hidden='true'>-&gt;</div><div class='node'>Banner Q4X<br>through BC-M12F5-22-2-SF</div></div></section>
<section><h2>Exact candidates and explicit gaps</h2><div class='grid'>{equipment_cards}</div></section>
<section><h2>Pin-level candidate schedule</h2><p>Every row remains unreleased. Received cable continuity and an independent wire check are mandatory before a future qualified disposition.</p><div class='table-wrap'><table><thead><tr><th>ID</th><th>Source</th><th>Destination</th><th>Candidate function</th><th>Remaining hold</th></tr></thead><tbody>{pin_rows}</tbody></table></div></section>
<section><h2>Why calibration comes before a threshold</h2><div class='decision'>The no-motion limit cannot be copied from catalog resolution or repeatability. It must come from the received sensor, selected target, rigid as-built fixture, operating distance, alignment, temperature, response/averaging mode, analog chain and complete uncertainty.</div><p>The campaign contains ten unexecuted steps: receiving, continuity, isolation, fixture inspection, configuration, warm-up, repeated static calibration, nuisance/environment trials, analysis and qualified E2 release review.</p></section>
<section><h2>Fourteen blockers to any connection</h2><div class='grid'>{hold_cards}</div></section>
<section><h2>Gate effect</h2><p><strong>EG-025 remains OPEN. EG-026 remains PARTIAL.</strong> There are zero physical runs, zero released connections, zero released protection devices, zero robot-baseline changes and zero safety-function credit.</p></section>
</main><footer>{escape(WARNING)}</footer></body></html>"""
    (WEB / "index.html").write_text(html, encoding="utf-8")
    print(f"generated {IDENTIFIER}: 5 exact candidates, 14 holds, 0 connections, 0 physical runs")


if __name__ == "__main__":
    main()
