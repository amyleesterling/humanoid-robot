"""Generate the HR-V0 passive power-loss containment planning package.

The calculation deliberately grants no holding, brake, software, watchdog, or
controlled-stop credit.  It bounds gravitational potential only; it is not an
impact prediction or a physical validation result.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "bom" / "hr-v0-moving-mass-ledger.csv"
OUT = ROOT / "safety" / "hr-v0-power-loss-containment-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-power-loss-containment-template-p0.1.csv"
GUIDE = ROOT / "release" / "hr-v0" / "power-loss-containment-p0.1" / "index.html"
REVISION = "HR-V0-POWERLOSS-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"
G = 9.80665


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def controlled_limits() -> tuple[float, float]:
    with LEDGER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    bucket_allocations: dict[str, float] = {}
    radii: list[float] = []
    for row in rows:
        bucket = row["allocation_bucket"]
        allocation = float(row["bucket_allocation_g"])
        if bucket in bucket_allocations and not math.isclose(bucket_allocations[bucket], allocation):
            raise RuntimeError(f"inconsistent allocation for {bucket}")
        bucket_allocations[bucket] = allocation
        if row["shoulder_radius_mm"]:
            radii.append(float(row["shoulder_radius_mm"]))
    mass_kg = sum(bucket_allocations.values()) / 1000.0
    reach_m = max(radii) / 1000.0
    if not math.isclose(mass_kg, 0.750, abs_tol=1e-12):
        raise RuntimeError(f"expected controlled 0.750 kg allocation, got {mass_kg}")
    if not math.isclose(reach_m, 0.360, abs_tol=1e-12):
        raise RuntimeError(f"expected controlled 0.360 m radius, got {reach_m}")
    return mass_kg, reach_m


def main() -> int:
    mass_kg, reach_m = controlled_limits()
    vertical_excursion_m = 2.0 * reach_m
    energy_j = mass_kg * G * vertical_excursion_m
    payload_energy_j = 0.100 * G * vertical_excursion_m
    free_fall_speed_m_s = math.sqrt(2.0 * G * vertical_excursion_m)

    bound_rows = [
        {"bound_id":"PLB-001","quantity":"controlled moving-system mass ceiling","expression":"sum of unique allocation buckets","value":f"{mass_kg:.6f}","unit":"kg","basis":"bom/hr-v0-moving-mass-ledger.csv","authority":"PROJECT REQUIREMENT CEILING","closure_evidence":"replace estimates with received mass/COM/inertia without exceeding the controlled ceiling","status":"BOUND INPUT - PHYSICAL CLOSURE OPEN"},
        {"bound_id":"PLB-002","quantity":"maximum controlled shoulder radius","expression":"max recorded shoulder_radius_mm / 1000","value":f"{reach_m:.6f}","unit":"m","basis":"bom/hr-v0-moving-mass-ledger.csv payload radius","authority":"PROJECT GEOMETRIC CEILING","closure_evidence":"as-built swept-volume and pose metrology","status":"BOUND INPUT - PHYSICAL CLOSURE OPEN"},
        {"bound_id":"PLB-003","quantity":"configuration-independent vertical point excursion","expression":"2 * radius","value":f"{vertical_excursion_m:.6f}","unit":"m","basis":"diameter of the controlled radius sphere","authority":"CONSERVATIVE GEOMETRIC BOUND","closure_evidence":"continuous as-built pose and receiver analysis","status":"CALCULATED BOUND"},
        {"bound_id":"PLB-004","quantity":"standard gravity","expression":"defined constant","value":f"{G:.5f}","unit":"m/s^2","basis":"project calculation convention","authority":"CALCULATION CONSTANT","closure_evidence":"none for arithmetic; test-site gravity correction not required at this resolution","status":"CALCULATION INPUT"},
        {"bound_id":"PLB-005","quantity":"whole moving-system gravitational potential bound","expression":"mass * g * 2 * radius","value":f"{energy_j:.6f}","unit":"J","basis":"PLB-001 through PLB-004","authority":"GRAVITATIONAL-ONLY ALLOCATION INPUT","closure_evidence":"selected receiver/guard load path, material properties, uncertainty, proof and dynamic test","status":"NOT AN IMPACT RATING"},
        {"bound_id":"PLB-006","quantity":"100 g payload gravitational potential bound","expression":"0.100 * g * 2 * radius","value":f"{payload_energy_j:.6f}","unit":"J","basis":"controlled payload ceiling and PLB-002 through PLB-004","authority":"PAYLOAD-ONLY ALLOCATION INPUT","closure_evidence":"selected foam object, drop height, rebound and receiver proof","status":"NOT AN IMPACT RATING"},
        {"bound_id":"PLB-007","quantity":"ideal point-mass free-fall speed screen","expression":"sqrt(2 * g * 2 * radius)","value":f"{free_fall_speed_m_s:.6f}","unit":"m/s","basis":"PLB-002 through PLB-004","authority":"SCREEN ONLY","closure_evidence":"measured joint/link velocity from released power-loss tests","status":"NOT A ROBOT SPEED OR IMPACT PREDICTION"},
        {"bound_id":"PLB-008","quantity":"receiver design energy","expression":"selection required from configured mass/COM/inertia, continued-drive exclusion and accepted factor","value":"SELECTION REQUIRED","unit":"J","basis":"PLB-005 is gravitational input only","authority":"QUALIFIED MECHANICAL DECISION REQUIRED","closure_evidence":"accepted load cases, factor, material/retention design and proof plan","status":"OPEN - BLOCKS FABRICATION AND MOTION"},
        {"bound_id":"PLB-009","quantity":"allowable receiver travel","expression":"selection required","value":"SELECTION REQUIRED","unit":"mm","basis":"access, clearance, cable and rebound limits","authority":"QUALIFIED MECHANICAL DECISION REQUIRED","closure_evidence":"guard/receiver CAD and physical measurement","status":"OPEN - BLOCKS FABRICATION AND MOTION"},
        {"bound_id":"PLB-010","quantity":"allowable peak receiver reaction","expression":"selection required","value":"SELECTION REQUIRED","unit":"N","basis":"complete load path and accepted material allowables","authority":"QUALIFIED MECHANICAL DECISION REQUIRED","closure_evidence":"analysis, calibrated force measurement and proof","status":"OPEN - BLOCKS FABRICATION AND MOTION"},
        {"bound_id":"PLB-011","quantity":"allowable rebound and final resting envelope","expression":"selection required","value":"SELECTION REQUIRED","unit":"mm","basis":"fixed-guard access and secondary-contact analysis","authority":"QUALIFIED SAFETY/MECHANICAL DECISION REQUIRED","closure_evidence":"high-speed video, as-built sweep and access assessment","status":"OPEN - BLOCKS MOTION"},
        {"bound_id":"PLB-012","quantity":"coverage beyond gravitational collapse","expression":"continued drive + stored energy + electrical regeneration + detached parts","value":"NOT COVERED","unit":"case set","basis":"separate HR-V0-GUARD-IMPACT-P0.1 allocations","authority":"EXPLICIT EXCLUSION","closure_evidence":"separate accepted cases and physical evidence","status":"OPEN - NO EXTRAPOLATION PERMITTED"},
    ]
    write_csv(OUT / "power-loss-energy-bound.csv", bound_rows)

    strategy_rows = [
        {"strategy_id":"PLC-001","subject":"J1 shoulder axis","assumed_power_loss_behavior":"may backdrive or move through the full physically available range","credited_protection_after_acceptance":"fixed guard plus passive receiver and released bidirectional hard stops","explicitly_uncredited":"actuator holding torque, friction, software, DF-01, controlled stop","evidence_to_close":"J1 min/max stop design, receiver load path, continuous sweep and physical drop/backdrive test","status":"SELECTED STRATEGY - IMPLEMENTATION OPEN"},
        {"strategy_id":"PLC-002","subject":"J2 elbow axis","assumed_power_loss_behavior":"may backdrive or move until a physical boundary or receiver contact","credited_protection_after_acceptance":"fixed guard plus passive receiver and released bidirectional hard stops","explicitly_uncredited":"XM540 holding, present J2-positive CAD candidate, software, DF-01","evidence_to_close":"J2-min stop, positive-stop physical validation, receiver proof and full-pose test","status":"SELECTED STRATEGY - IMPLEMENTATION OPEN"},
        {"strategy_id":"PLC-003","subject":"gripper mechanism","assumed_power_loss_behavior":"may open, close, relax or release the object","credited_protection_after_acceptance":"fixed object receiver/catch inside the inaccessible enclosure","explicitly_uncredited":"servo holding, friction, commanded close, software","evidence_to_close":"selected gripper, object, catch, release/drop/rebound testing","status":"SELECTED STRATEGY - IMPLEMENTATION OPEN"},
        {"strategy_id":"PLC-004","subject":"100 g foam object","assumed_power_loss_behavior":"may fall from any released pose","credited_protection_after_acceptance":"fixed receiver with no escape into an accessible area","explicitly_uncredited":"grip force, adhesion, operator catch","evidence_to_close":"serialized object, all-pose drop coverage and receiver inspection","status":"SELECTED STRATEGY - IMPLEMENTATION OPEN"},
        {"strategy_id":"PLC-005","subject":"cables and connectors","assumed_power_loss_behavior":"may be loaded by the collapse path","credited_protection_after_acceptance":"routing/strain relief outside contact and pinch load paths","explicitly_uncredited":"cable tension as restraint","evidence_to_close":"as-built continuous sweep, pull/strain inspection and post-test teardown","status":"DESIGN REQUIRED"},
        {"strategy_id":"PLC-006","subject":"operator and bystanders","assumed_power_loss_behavior":"no access to the collapse, pinch, rebound or object-drop region","credited_protection_after_acceptance":"fixed guard with controlled access and restart prevention","explicitly_uncredited":"warnings, training, supervision alone","evidence_to_close":"access assessment, interlock/allocation decision and physical inspection","status":"DESIGN REQUIRED"},
        {"strategy_id":"PLC-007","subject":"actuator source and contactors","assumed_power_loss_behavior":"rail decay and regeneration are unknown until measured","credited_protection_after_acceptance":"passive containment remains adequate after drive energy is absent","explicitly_uncredited":"assumed immediate torque loss or published component opening time as total stop time","evidence_to_close":"rail waveform, contactor application acceptance and synchronized motion/force records","status":"TEST REQUIRED"},
        {"strategy_id":"PLC-008","subject":"continued-drive fault","assumed_power_loss_behavior":"outside this gravitational-only calculation","credited_protection_after_acceptance":"separate guard/stop/load allocation","explicitly_uncredited":"PLB-005 energy bound","evidence_to_close":"HR-V0-GUARD-IMPACT-P0.1 powered-contact case closure","status":"SEPARATE BLOCKER"},
        {"strategy_id":"PLC-009","subject":"final resting state","assumed_power_loss_behavior":"arm, gripper and object may remain at any passive boundary","credited_protection_after_acceptance":"stable supported pose with no accessible pinch and no spontaneous restart","explicitly_uncredited":"operator support or re-energization for recovery","evidence_to_close":"recovery procedure, access check, stability/secondary-motion test","status":"DESIGN AND TEST REQUIRED"},
        {"strategy_id":"PLC-010","subject":"restart after power restoration","assumed_power_loss_behavior":"stored command and trajectory are invalid","credited_protection_after_acceptance":"RESET then distinct ARM then fresh trajectory","explicitly_uncredited":"heartbeat return, reboot, reset alone","evidence_to_close":"configuration-specific restart fault injection with contained mechanism","status":"PHYSICAL VALIDATION REQUIRED"},
    ]
    write_csv(OUT / "power-loss-strategy.csv", strategy_rows)

    pose_values = ((-20, 15), (-20, 65), (-20, 115), (25, 15), (25, 65), (25, 115), (70, 15), (70, 65), (70, 115))
    payload_states = (("EMPTY_OPEN", "0"), ("FOAM_100G_MAX_CLOSED", "100"))
    causes = ("E_STOP_DEMAND", "ACTUATOR_SOURCE_LOSS", "CONTROL_POWER_LOSS", "BUS_WATCHDOG_TORQUE_OFF")
    test_rows: list[dict[str, object]] = []
    case_number = 0
    for j1, j2 in pose_values:
        for payload_state, payload_mass in payload_states:
            for cause in causes:
                case_number += 1
                test_rows.append({
                    "record_id":f"PLT-{case_number:03d}","date":"","witness":"","repo_commit":"","mechanical_revision":"","guard_receiver_revision":"","pose_coverage":"3x3 GRID ONLY - CONTINUOUS COVERAGE REQUIRED","j1_command_deg":j1,"j2_command_deg":j2,"payload_state":payload_state,"payload_mass_g":payload_mass,"energy_loss_cause":cause,"actuator_rail_start_v":"","actuator_rail_below_torque_threshold_ms":"","j1_final_deg":"","j2_final_deg":"","maximum_point_travel_mm":"","receiver_contact_location":"","receiver_travel_mm":"","peak_receiver_force_n":"","maximum_rebound_mm":"","object_escape":"","accessible_hazard":"","cable_or_connector_damage":"","structure_or_guard_damage":"","restart_without_reset_arm":"","raw_log_reference":"","video_reference":"","calibration_reference":"","deviation_reference":"","disposition":"NOT EXECUTED","execution_status":"NOT EXECUTED","authorization":"NOT AUTHORIZED","warning":WARNING,
                })
    write_csv(FORM, test_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>HR-V0 passive power-loss containment</title>
<style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#a83220;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,40px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}.card,.calc,.flow>div{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,58px);font-weight:900;color:#075b9b}}label{{display:block;font-weight:850;margin:14px 0 5px}}input[type=range]{{width:100%;min-height:32px}}.formula{{font:700 17px/1.5 ui-monospace,Consolas,monospace;background:#f5fbff;padding:12px;border-radius:10px}}.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}.flow strong{{display:block;color:var(--navy)}}.hold{{color:var(--red);font-weight:850}}.small{{font-size:14px}}footer{{background:var(--deep);color:white;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}.flow{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div><p class=\"warning\">PRELIMINARY - CALCULATION AND STRATEGY ONLY. NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION.</p><p class=\"eyebrow\">{REVISION}</p><h1>Assume the arm falls.</h1><p>No actuator hold, friction, software, heartbeat or controlled-stop credit. The fixed guard and passive receiver must contain the outcome even after drive energy disappears.</p></div></header>
<main>
<section><h2>Explore the gravitational bound</h2><div class=\"grid\"><article class=\"calc\"><label for=\"mass\">Moving mass: <span id=\"massOut\">0.750</span> kg</label><input id=\"mass\" type=\"range\" min=\"0.100\" max=\"0.750\" value=\"0.750\" step=\"0.005\"><label for=\"reach\">Maximum radius: <span id=\"reachOut\">0.360</span> m</label><input id=\"reach\" type=\"range\" min=\"0.100\" max=\"0.360\" value=\"0.360\" step=\"0.005\"></article><article class=\"card\"><div class=\"metric\"><span id=\"energy\">5.296</span> J</div><p>Configuration-independent gravitational potential bound.</p><p class=\"formula\">E = m × 9.80665 × (2r)</p><p class=\"hold\">This is not a receiver rating or impact prediction.</p></article></div></section>
<section><h2>The passive protection chain</h2><div class=\"flow\"><div><strong>1. Lose energy</strong>Any credited or uncredited loss cause.</div><div><strong>2. Assume motion</strong>Both joints and gripper may move.</div><div><strong>3. Stay enclosed</strong>No person can reach the collapse region.</div><div><strong>4. Catch passively</strong>Receiver supports arm and object without control.</div><div><strong>5. Latch restart</strong>RESET, distinct ARM and a fresh trajectory remain required.</div></div></section>
<section><h2>What must still be selected and proved</h2><div class=\"grid\"><article class=\"card\"><strong>Receiver design</strong><p>Material, geometry, energy factor, travel, peak force, rebound and load path.</p></article><article class=\"card\"><strong>All-pose coverage</strong><p>Continuous as-built sweep plus the 72-case test scaffold; a 3×3 test grid alone is not every pose.</p></article><article class=\"card\"><strong>Physical behavior</strong><p>Backdrive, rail decay, link travel, cable loading, object release, final rest and recovery.</p></article><article class=\"card\"><strong>Separate hazards</strong><p>Continued drive, stored energy, regeneration and detached parts are excluded from 5.296 J and need their own cases.</p></article></div></section>
<section><h2>Gate status</h2><div class=\"card\"><p><strong>EG-009 remains partial.</strong> The strategy and gravitational input are bounded; the receiver/guard is not selected, built or tested.</p><p class=\"small\">Default inputs come from the controlled 750 g moving-system allocation and 360 mm shoulder-radius ceiling. Slider values are exploratory only.</p></div></section>
</main><footer><p>Project Button · {REVISION} · zero functional-safety credit · no fabrication, motion or energization approval</p></footer>
<script>const m=document.querySelector('#mass'),r=document.querySelector('#reach'),mo=document.querySelector('#massOut'),ro=document.querySelector('#reachOut'),eo=document.querySelector('#energy');function update(){{mo.textContent=Number(m.value).toFixed(3);ro.textContent=Number(r.value).toFixed(3);eo.textContent=(Number(m.value)*9.80665*2*Number(r.value)).toFixed(3)}}m.addEventListener('input',update);r.addEventListener('input',update);update();</script>
</body></html>""", encoding="utf-8", newline="\n")

    print(f"Generated {REVISION}: {energy_j:.6f} J gravitational-only bound; {len(test_rows)} unexecuted cases")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
