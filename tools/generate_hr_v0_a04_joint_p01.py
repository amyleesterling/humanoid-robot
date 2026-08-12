#!/usr/bin/env python3
"""Generate R274 A04 exact-candidate joint definition and evidence contract."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "mechanical/joints/hr-v0-a04-joint-p0.1"
REL = ROOT / "release/hr-v0/a04-joint-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.37"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.38"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.38"
IDENT = "HR-V0-A04-JOINT-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.38"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    records = [
        {"relative_path": p.relative_to(directory).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size, "warning": WARNING}
        for p in sorted(directory.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"
    ]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, str]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{html.escape(x.replace('_', ' '))}</th>" for x in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(r.get(x, ''))}</td>" for x in fields) + "</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    if PKG.exists():
        shutil.rmtree(PKG)
    PKG.mkdir(parents=True)

    sources = [
        {"source_id":"A04-SRC-001","organization":"McMaster-Carr","exact_identity":"91290A303","document_or_page":"Black-oxide alloy-steel socket-head screw catalog","revision_or_access_date":"live U.S. catalog; checked 2026-08-12","official_url":"https://www.mcmaster.com/products/91251A541/","verified_fields":"M2.5 x 0.45; 18 mm under-head length; fully threaded; 4.5 mm head diameter; 2.5 mm head height; 2 mm socket; Class 12.9; 170000 psi listed tensile strength; package 5","boundary":"Supplier catalog does not freeze manufacturer, lot, actual tolerance, certificate or installed performance.","state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","warning":WARNING},
        {"source_id":"A04-SRC-002","organization":"McMaster-Carr","exact_identity":"98688A148","document_or_page":"ISO 7089 metric washer catalog","revision_or_access_date":"live U.S. catalog; checked 2026-08-12","official_url":"https://www.mcmaster.com/products/washers/specifications-met~iso-7089/","verified_fields":"M2.5; 2.7 mm ID; 6.0 mm OD; 0.5 to 0.6 mm thickness; Class 10.9","boundary":"Supplier catalog identity is not a received material certificate or bearing allowable.","state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","warning":WARNING},
        {"source_id":"A04-SRC-003","organization":"McMaster-Carr","exact_identity":"90576A161","document_or_page":"DIN 985 / ISO 10511 nylon-insert locknut catalog","revision_or_access_date":"live U.S. catalog; checked 2026-08-12","official_url":"https://www.mcmaster.com/products/din-985-nuts","verified_fields":"M2.5 x 0.45; zinc-plated steel; Class 8; 5 mm width; 3.8 mm height; nylon insert maximum 185 F; package 50","boundary":"Manufacturer, lot, nut proof load, prevailing-torque distribution, temperature margin and reuse performance are unverified.","state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","warning":WARNING},
        {"source_id":"A04-SRC-004","organization":"Wiha","exact_identity":"36852","document_or_page":"TorqueVario-S ESD adjustable torque screwdriver","revision_or_access_date":"live manufacturer page; checked 2026-08-12","official_url":"https://wiha.com/int/en/tools/torque-tools/wiha-torquevario-s-esd/handle/torque-screwdriver-torquevario-s-esd/26865","verified_fields":"0.1 to 0.6 N m range; 4 mm blade interface; +/-6 percent listed accuracy; DIN EN ISO 6789; works inspection protocol","boundary":"Project torque remains undeveloped; current calibration and the exact useful accuracy interval require receiving verification.","state":"EXACT TOOL CANDIDATE HOLD","warning":WARNING},
        {"source_id":"A04-SRC-005","organization":"Wiha","exact_identity":"26060","document_or_page":"Straight hex torque interchangeable blade","revision_or_access_date":"live manufacturer page; checked 2026-08-12","official_url":"https://wiha.com/tools/torque-tools/wiha-torque-interchangeable-blades/interchangeable-blade/26200","verified_fields":"straight 2.0 mm hex; 4 mm blade diameter; 175 mm overall; 42 mm visible blade; 1.8 N m listed maximum","boundary":"Received straight-tip identity, runout, well fit, socket engagement and torque transfer require physical inspection.","state":"EXACT TOOL CANDIDATE HOLD","warning":WARNING},
        {"source_id":"A04-SRC-006","organization":"Bossard","exact_identity":"Technical information F-009","document_or_page":"Materials screws and nuts / ISO 898 property-class tables","revision_or_access_date":"current technical PDF; checked 2026-08-12","official_url":"https://media.bossard.com/global-en/-/media/bossard-group/website/documents/technical-resources/en/f-009-en.pdf","verified_fields":"ISO 898 property-class framework and nut/bolt compatibility tables","boundary":"Reference-class values are not received-lot allowables and do not establish this mixed supplier stack.","state":"REFERENCE ONLY","warning":WARNING},
        {"source_id":"A04-SRC-007","organization":"Bossard","exact_identity":"Selecting a Fastener Finish","document_or_page":"Fastener finish white paper","revision_or_access_date":"current manufacturer technical paper; checked 2026-08-12","official_url":"https://www.bossard.com/-/media/bossard-group/website/documents/white-paper/bossard-whitepaper-selecting-a-fastener-finish-en.pdf","verified_fields":"High-strength electroplated fasteners are susceptible to hydrogen embrittlement; baking reduces but does not eliminate risk.","boundary":"Supports retaining black oxide as the study finish; corrosion control and received identity remain open.","state":"REFERENCE ONLY","warning":WARNING},
        {"source_id":"A04-SRC-008","organization":"ROBOTIS","exact_identity":"FR13-S102K drawing and STEP","document_or_page":"Controlled local vendor sources","revision_or_access_date":"drawing date 2026-01-07; checked 2026-08-12","official_url":"https://www.robotis.us/fr13-s102k-set/","verified_fields":"four M2.5 x 0.45 tapped-through axes at X +/-16 and Z +/-8; broad C1.4 sheet callout","boundary":"Drawing is marked for reference only; received sheet thickness, material, thread and structural capacity remain open.","state":"CONTROLLED REFERENCE / RECEIPT OPEN","warning":WARNING},
    ]
    write_csv(PKG / "source-register.csv", sources)

    schedule = [
        {"line_id":"A04-CAND-001","role":"screw","supplier":"McMaster-Carr","supplier_order_code":"91290A303","candidate_description":"M2.5 x 0.45 x 18 mm black-oxide alloy-steel socket-head screw; Class 12.9","installed_quantity":4,"development_quantity":"20 screws / four catalog packs; project-owner decision required","selection_state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","unresolved":"current cart/quote, manufacturer/lot, CoC, actual length/head/socket, finish, thread gauge, proof data and received inspection","warning":WARNING},
        {"line_id":"A04-CAND-002","role":"washer under nut","supplier":"McMaster-Carr","supplier_order_code":"98688A148","candidate_description":"M2.5 ISO 7089 Class 10.9 steel washer; 2.7 ID x 6.0 OD x 0.5..0.6 mm","installed_quantity":4,"development_quantity":"one catalog pack; project-owner decision required","selection_state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","unresolved":"current cart/quote, manufacturer/lot, material/finish certificate, flatness, hardness and received dimensions","warning":WARNING},
        {"line_id":"A04-CAND-003","role":"single-use prevailing-torque nut","supplier":"McMaster-Carr","supplier_order_code":"90576A161","candidate_description":"M2.5 x 0.45 zinc-plated Class 8 DIN 985 / ISO 10511 nylon-insert locknut","installed_quantity":4,"development_quantity":"one catalog pack; project-owner decision required","selection_state":"EXACT SUPPLIER-ORDER CANDIDATE HOLD","unresolved":"current cart/quote, manufacturer/lot, nut proof load, prevailing torque, received height/thread and accepted temperature envelope","warning":WARNING},
        {"line_id":"A04-CAND-004","role":"calibratable torque handle","supplier":"Wiha or authorized U.S. distributor","supplier_order_code":"36852","candidate_description":"TorqueVario-S ESD 0.1..0.6 N m adjustable 4 mm handle","installed_quantity":0,"development_quantity":"1 tool plus current calibration evidence","selection_state":"EXACT TOOL CANDIDATE HOLD","unresolved":"U.S. order route, current calibration, accepted working range and periodic calibration interval","warning":WARNING},
        {"line_id":"A04-CAND-005","role":"straight access-well blade","supplier":"Wiha or authorized U.S. distributor","supplier_order_code":"26060","candidate_description":"2.0 mm straight hex torque blade; 4 mm shaft; 42 mm visible blade","installed_quantity":0,"development_quantity":"2 blades; one controlled working and one spare","selection_state":"EXACT TOOL CANDIDATE HOLD","unresolved":"U.S. order route, received straight-tip identity, access-well fit, engagement and runout","warning":WARNING},
    ]
    write_csv(PKG / "exact-candidate-schedule.csv", schedule)

    stack = [
        {"parameter":"screw actual under-head length","symbol":"L_s","catalog_min_mm":"NOT PUBLISHED","catalog_nominal_mm":"18.000","catalog_max_mm":"NOT PUBLISHED","measurement_method":"calibrated micrometer; ten-piece lot sample plus every installed screw","required_record":"received-stack-measurements.csv","release_effect":"fails closed until supplier tolerance and received values are accepted","warning":WARNING},
        {"parameter":"C07 original mounting-land grip","symbol":"t_C07","catalog_min_mm":"9.000 project finished limit","catalog_nominal_mm":"9.525","catalog_max_mm":"10.000 project finished limit","measurement_method":"micrometer map around every A04 axis","required_record":"received-stack-measurements.csv","release_effect":"no use until C07 FAI is accepted","warning":WARNING},
        {"parameter":"S102 broad sheet","symbol":"t_S102","catalog_min_mm":"NOT PUBLISHED","catalog_nominal_mm":"1.400 reference callout","catalog_max_mm":"NOT PUBLISHED","measurement_method":"received-frame thickness map clear of coatings/radii","required_record":"received-stack-measurements.csv","release_effect":"no stack or bearing conclusion until tolerance/material are accepted","warning":WARNING},
        {"parameter":"washer thickness","symbol":"t_w","catalog_min_mm":"0.500","catalog_nominal_mm":"0.550","catalog_max_mm":"0.600","measurement_method":"calibrated micrometer; ten-piece lot sample plus every installed washer","required_record":"received-stack-measurements.csv","release_effect":"catalog bounds remain unverified until receipt","warning":WARNING},
        {"parameter":"nut overall height","symbol":"h_n","catalog_min_mm":"NOT PUBLISHED","catalog_nominal_mm":"3.800","catalog_max_mm":"NOT PUBLISHED","measurement_method":"calibrated micrometer; ten-piece lot sample plus every installed nut","required_record":"received-stack-measurements.csv","release_effect":"thread projection fails closed until supplier tolerance and received height are accepted","warning":WARNING},
        {"parameter":"thread beyond complete nut","symbol":"p_out","catalog_min_mm":"UNRESOLVED","catalog_nominal_mm":"2.725 at nominal dimensions","catalog_max_mm":"UNRESOLVED","measurement_method":"p_out=L_s-t_C07-t_S102-t_w-h_n; divide by 0.45 mm pitch","required_record":"received-stack-calculation.csv","release_effect":"qualified reviewer must define and accept minimum complete-thread projection","warning":WARNING},
        {"parameter":"access well to straight blade radial clearance","symbol":"c_tool","catalog_min_mm":"UNRESOLVED WITH TOLERANCE","catalog_nominal_mm":"0.600 from 5.20 well and 4.00 blade","catalog_max_mm":"UNRESOLVED","measurement_method":"C07 FAI plus received blade gauge/dry fit","required_record":"tool-access-and-seat-inspection.csv","release_effect":"must allow axial seating without blade/well contact","warning":WARNING},
    ]
    write_csv(PKG / "tolerance-chain.csv", stack)

    as_mm2 = math.pi / 4 * (2.5 - 0.9382 * 0.45) ** 2
    axial = 392.085
    shear = 112.275
    axial_stress = axial / as_mm2
    shear_stress = shear / as_mm2
    vm = math.sqrt(axial_stress**2 + 3 * shear_stress**2)
    head_area = math.pi / 4 * (4.5**2 - 2.7**2)
    washer_area = math.pi / 4 * (6.0**2 - 2.7**2)
    screens = [
        {"screen_id":"A04-SCR-001","subject":"maximum elastic bolt-group reaction","input_or_formula":"R273 one-rail endpoint/gravity demand; all external load assigned elastically to four axes","result":f"axial {axial:.3f} N; in-plane shear {shear:.3f} N; vector {math.hypot(axial,shear):.3f} N","comparison":"demand only","disposition":"CALCULATED DEMAND / NO CAPACITY CLAIM","excluded":"preload, friction/slip, separation, prying, S102 flexibility, tolerance, impact and fatigue","warning":WARNING},
        {"screen_id":"A04-SCR-002","subject":"M2.5 screw direct combined stress","input_or_formula":f"As=pi/4*(d-0.9382p)^2={as_mm2:.4f} mm2; sqrt(sigma^2+3tau^2)","result":f"sigma={axial_stress:.3f} MPa; tau={shear_stress:.3f} MPa; von Mises={vm:.3f} MPa","comparison":"Class 12.9 reference property only; received proof allowable not accepted","disposition":"REFERENCE-CLASS SCREEN ONLY / NO PASS CLAIM","excluded":"preload stress, thread bending, notch, fatigue, nut stripping, prying and lot properties","warning":WARNING},
        {"screen_id":"A04-SCR-003","subject":"C07 nominal screw-head bearing","input_or_formula":"392.085 N / [pi/4*(4.5^2-2.7^2)]","result":f"{axial/head_area:.3f} MPa nominal average","comparison":"240 MPa project MTR threshold is not a bearing allowable","disposition":"GEOMETRIC STRESS SCREEN ONLY / NO PASS CLAIM","excluded":"countersurface flatness, edge pressure, prying, plasticity, finish and fatigue","warning":WARNING},
        {"screen_id":"A04-SCR-004","subject":"S102 nominal washer bearing","input_or_formula":"392.085 N / [pi/4*(6.0^2-2.7^2)]","result":f"{axial/washer_area:.3f} MPa nominal average","comparison":"S102 material and allowable are not published/accepted","disposition":"DEMAND ONLY / NO PASS CLAIM","excluded":"sheet bending, local indentation, washer coning, edge distance, material and fatigue","warning":WARNING},
        {"screen_id":"A04-SCR-005","subject":"slip and separation resistance","input_or_formula":"requires accepted minimum preload, friction distribution, joint stiffness and eccentric-load factor","result":"NO RESULT","comparison":"torque alone is not preload evidence","disposition":"SELECTION REQUIRED / PHYSICAL DEVELOPMENT REQUIRED","excluded":"none may be inferred","warning":WARNING},
        {"screen_id":"A04-SCR-006","subject":"nut/thread/head/washer capacity","input_or_formula":"requires exact manufacturer lot, applicable standard evidence, effective engagement and received geometry","result":"NO RESULT","comparison":"supplier class labels are not configuration allowables","disposition":"SELECTION REQUIRED / QUALIFIED ANALYSIS REQUIRED","excluded":"stripping, embedment, proof load, prevailing torque and mixed-class compatibility","warning":WARNING},
    ]
    write_csv(PKG / "analytical-screen.csv", screens)

    receiving = []
    for i in range(1, 11):
        receiving.append({"record_id":f"A04-REC-{i:02d}","article_role":"screw/washer/nut sample","supplier_order_code":"","manufacturer":"","lot_or_heat":"","coc_uri":"","screw_length_mm":"","head_diameter_mm":"","socket_go_no_go":"","washer_id_od_thickness_mm":"","nut_height_mm":"","thread_gauge_result":"","visual_finish_result":"","disposition":"NOT EXECUTED","inspector":"","date":"","warning":WARNING})
    write_csv(PKG / "received-stack-measurements.csv", receiving)

    torque = []
    for i in range(1, 13):
        torque.append({"trial_id":f"A04-TT-{i:02d}","new_screw_id":"","new_washer_id":"","new_nut_id":"","representative_c07_coupon_id":"","received_s102_id":"","condition":"dry-as-received candidate; any change starts a new series","run_on_prevailing_torque_nm":"","target_total_torque_nm":"","measured_peak_torque_nm":"","measured_clamp_force_n":"","relaxation_10min_n":"","breakaway_after_hold_nm":"","thread_or_surface_damage":"","result":"NOT EXECUTED","raw_data_uri":"","witness":"","warning":WARNING})
    write_csv(PKG / "torque-preload-development.csv", torque)

    install = []
    for axis in ("X-16/Z-8", "X-16/Z+8", "X+16/Z-8", "X+16/Z+8"):
        install.append({"a04_axis":axis,"c07_part_serial":"","s102_serial":"","screw_id":"","washer_id":"","new_nut_id":"","calibrated_handle_id":"","blade_id":"","accepted_total_torque_nm":"","prevailing_torque_observed_nm":"","final_trigger_count":"","thread_projection_mm":"","thread_projection_pitches":"","head_fully_seated":"NOT EXECUTED","blade_well_contact":"NOT EXECUTED","witness_mark":"NOT EXECUTED","independent_inspection":"NOT EXECUTED","result":"NOT EXECUTED","warning":WARNING})
    write_csv(PKG / "installation-traveler.csv", install)

    tests = [
        {"step_id":"A04-TP-001","sequence":1,"activity":"Quarantine and reconcile exact supplier order codes, manufacturer/lot and certificates.","instrument_or_fixture":"receiving station; calibrated dimensional instruments; thread/socket gauges","acceptance":"all identity and certificate fields accepted; no substitutions","state":"NOT EXECUTED","evidence":"completed receiving records and photographs","warning":WARNING},
        {"step_id":"A04-TP-002","sequence":2,"activity":"Measure the full received stack and calculate worst measured thread projection at every axis.","instrument_or_fixture":"micrometer/CMM; controlled spreadsheet or checker","acceptance":"qualified reviewer-defined projection, seating and clearance limits met","state":"NOT EXECUTED","evidence":"raw measurements, uncertainty and calculation","warning":WARNING},
        {"step_id":"A04-TP-003","sequence":3,"activity":"Develop torque-to-clamp-force relation on representative C07/S102 coupons with new nuts for every trial.","instrument_or_fixture":"calibrated torque transducer/handle and independent clamp-force measurement","acceptance":"separately approved preload window achieved across the accepted torque/tool interval without damage","state":"NOT EXECUTED","evidence":"twelve raw traces, statistics and qualified disposition","warning":WARNING},
        {"step_id":"A04-TP-004","sequence":4,"activity":"Complete joined nonlinear analysis including preload, separation, friction/slip, prying, S102 flexibility, nut/thread/head/washer and tolerances.","instrument_or_fixture":"controlled calculation and converged contact FEA","acceptance":"qualified factors/allowables and correlated model accepted","state":"NOT EXECUTED","evidence":"model, convergence, sensitivity and signed review","warning":WARNING},
        {"step_id":"A04-TP-005","sequence":5,"activity":"Dry-fit the 4 mm straight blade through each 5.2 mm access well and verify full 2 mm socket engagement and head seating.","instrument_or_fixture":"received C07/S102/XM540 stack; borescope and depth gauges","acceptance":"no well contact during axial tightening; no hardware/XM540 contact; seat and ligament accepted","state":"NOT EXECUTED","evidence":"FAI, images and signed fit record","warning":WARNING},
        {"step_id":"A04-TP-006","sequence":6,"activity":"Proof the assembled joint in single-rail and twin-rail fixtures without motor power.","instrument_or_fixture":"guarded calibrated force/strain/displacement fixture","acceptance":"separately approved load, displacement, slip, damage and residual-torque limits met","state":"NOT EXECUTED","evidence":"raw traces, before/after metrology and independent witness","warning":WARNING},
        {"step_id":"A04-TP-007","sequence":7,"activity":"Authorize one configuration-specific installation only after qualified acceptance.","instrument_or_fixture":"controlled traveler and release record","acceptance":"all prior rows complete; new nuts; calibrated tool; four-axis independent inspection","state":"NOT EXECUTED","evidence":"signed traveler and configuration release","warning":WARNING},
    ]
    write_csv(PKG / "verification-plan.csv", tests)

    holds_text = [
        "Current same-session supplier quote/cart confirms every exact order code and quantity",
        "Manufacturer/lot identity and required certificates are received and accepted",
        "Screw length and nut-height tolerances plus received measurements close thread projection",
        "S102 thickness, material, thread condition and structural allowables are accepted",
        "Nut proof, prevailing-torque distribution and mixed Class 12.9/Class 8 compatibility are accepted",
        "Torque-preload trials define an accepted dry installation torque and clamp-force window",
        "Joined analysis closes slip, separation, prying, sheet flexibility, bearing and thread/head/nut/washer modes",
        "Straight blade, access well, socket engagement, seating and XM540 clearance pass physical FAI",
        "Single-use nut, witness-mark, calibration, corrosion, temperature and inspection controls are released",
        "Unpowered single-rail and twin-rail proof tests pass qualified limits",
        "Configuration-bound qualified mechanical acceptance is signed",
        "Separate procurement, assembly and any later powered-work authorities are signed",
    ]
    holds = [{"hold_id":f"R274-H{i:02d}","hold":v,"state":"OPEN","execution":"NOT EXECUTED","closure_evidence":"see verification-plan.csv and controlled raw evidence","release_effect":"BLOCKS A04 SELECTION AND STRUCTURAL USE","warning":WARNING} for i,v in enumerate(holds_text,1)]
    write_csv(PKG / "open-holds.csv", holds)
    acceptance = [{"acceptance_id":f"R274-ACC-{i:02d}","criterion":v,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,v in enumerate(holds_text,1)]
    write_csv(PKG / "acceptance-matrix.csv", acceptance)

    status = {
        "identifier": IDENT, "round": "R274", "date": "2026-08-12",
        "parent_cad": "HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE",
        "candidate_lines": len(schedule), "source_records": len(sources), "analytical_screens": len(screens),
        "torque_trials": len(torque), "open_holds": len(holds), "acceptance_rows": len(acceptance),
        "hardware_selected": False, "procurement_authorized": False, "assembly_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "safety_credit": False, "warning": WARNING,
    }
    (PKG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (PKG / "README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR274 replaces unavailable dimensional placeholders at A04 with five exact supplier/tool candidates and a fail-closed stack, torque-preload, joined-load and proof evidence contract. No hardware is selected or authorized for purchase or use.\n", encoding="utf-8")

    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R274 A04 joint evidence</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#78acd0;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,52px)}}header{{background:linear-gradient(135deg,var(--blue),#0879be);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);padding:15px;border-radius:12px;font-size:clamp(16px,1.4vw,21px);font-weight:850;color:#fff1b5}}h1{{font-size:clamp(36px,5.5vw,70px);line-height:1.03}}h2{{font-size:clamp(25px,3vw,40px);line-height:1.15}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px}}.metric,.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:19px}}.metric strong{{display:block;color:#075e9c;font-size:32px}}.hold{{background:var(--hold);border:3px solid var(--gold);border-radius:14px;padding:20px}}section{{margin:34px 0}}label{{font-weight:800;display:block;margin-top:12px}}input{{font:16px system-ui;width:100%;max-width:300px;padding:8px}}output{{font-size:27px;font-weight:900;color:#075e9c}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1120px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #c6deed;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}a{{color:#075d9b;font-weight:750}}@media(max-width:600px){{header,main{{padding:18px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R274 &middot; {IDENT} &middot; exact candidates, zero selection</p><h1>A04 now has a purchasable candidate stack and a real closure route.</h1><p>The package names the screw, washer, locknut, torque handle and straight blade. It also records precisely why none may be installed yet.</p></div></header><main><section class='metrics'><div class='metric'><strong>5</strong>exact candidate lines</div><div class='metric'><strong>4</strong>installed fastener sets</div><div class='metric'><strong>12</strong>blank torque/preload trials</div><div class='metric'><strong>{vm:.1f} MPa</strong>direct bolt stress screen</div><div class='metric'><strong>12</strong>open holds</div><div class='metric'><strong>0</strong>work authorities</div></section><section class='hold'><h2>What this does not prove</h2><p>Supplier catalog classes are not lot allowables. Torque is not preload. The S102 frame material and thread capacity are not released. Slip, separation, prying, local sheet bending, fatigue, impact and physical fit still require execution and qualified acceptance.</p></section><section class='card'><h2>Explore the nominal stack</h2><p>This calculator is a dimensional aid only. Enter measured values after receipt; no minimum projection criterion is released.</p><div class='metrics'><label>Screw length mm<input id='ls' type='number' step='.001' value='18'></label><label>C07 grip mm<input id='c7' type='number' step='.001' value='9.525'></label><label>S102 thickness mm<input id='s1' type='number' step='.001' value='1.4'></label><label>Washer thickness mm<input id='ww' type='number' step='.001' value='.55'></label><label>Nut height mm<input id='nn' type='number' step='.001' value='3.8'></label></div><p>Thread beyond full nut: <output id='out'>2.725 mm / 6.056 pitches</output></p></section><section><h2>Exact candidate schedule</h2>{table([{k:str(v) for k,v in r.items()} for r in schedule])}</section><section><h2>Analytical boundary</h2>{table([{k:str(v) for k,v in r.items()} for r in screens])}</section><section><h2>Open closure evidence</h2>{table([{k:str(v) for k,v in r.items()} for r in holds])}</section></main><script>const ids=['ls','c7','s1','ww','nn'];function u(){{const v=ids.map(x=>Number(document.getElementById(x).value)),p=v[0]-v[1]-v[2]-v[3]-v[4];document.getElementById('out').value=p.toFixed(3)+' mm / '+(p/.45).toFixed(3)+' pitches'}}ids.forEach(x=>document.getElementById(x).addEventListener('input',u));u();</script></body></html>"""
    (PKG / "index.html").write_text(page, encoding="utf-8")
    manifest(PKG)
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(PKG, REL)
    manifest(REL)

    for target in (CFG, CFG_REL):
        if target.exists():
            shutil.rmtree(target)
    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-57","role":"A04 exact-candidate hardware and joined-load evidence contract","identifier":IDENT,"source_path":"release/hr-v0/a04-joint-p0.1/package-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - EXACT CANDIDATES UNSELECTED","release_boundary":"received identity/tolerance, torque-preload, joined analysis, FAI, proof and qualified acceptance open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-52","prior_identifier":"HR-V0-CONFIG-REC-P0.37","current_or_required_successor":CFG_IDENT,"disposition":"superseded for package indexing only; P0.8 remains current unaccepted mechanical identity and P0.12/A04 P0.1 remain unselected","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    cholds = rows(CFG / "open-holds.csv")
    for h in holds:
        cholds.append({"hold_id":f"HOLD-{len(cholds)+1:03d}","hold":f"{IDENT}: {h['hold']}","state":"NOT EXECUTED","closure_evidence":h["closure_evidence"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", cholds)
    acc = rows(CFG / "acceptance-matrix.csv")
    for a in acceptance:
        acc.append({"acceptance_id":f"ACC-{len(acc)+1:03d}","criterion":f"{IDENT}: {a['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", acc)
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R274","current_records":len(current),"supersession_records":len(supers),"open_holds":len(cholds),"acceptance_rows":len(acc),"a04_joint_review":IDENT,"a04_hardware_selected":False,"procurement_authorized":False,"assembly_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG / "package-status.json").write_text(json.dumps(cfg_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR274 indexes the unselected A04 P0.1 exact-candidate and verification package. P0.8 remains the current unaccepted mechanical identity; no procurement or structural-use authority exists.\n", encoding="utf-8")
    write_csv(CFG / "source-hash-register.csv", [{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(PKG / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFG_REL)
    manifest(CFG_REL)

    doc = ROOT / "docs/hr-v0-a04-joint-p0.1.md"
    doc.write_text(f"# HR-V0 A04 joint P0.1\n\n> **{WARNING}**\n\nR274 replaces unavailable A04 dimensional placeholders with exact supplier-order candidates: McMaster `91290A303`, `98688A148`, `90576A161`, and Wiha `36852` plus straight blade `26060`. They remain unselected pending same-session availability, manufacturer/lot and certificates.\n\nThe nominal 18 mm stack projects 2.725 mm, or 6.056 pitches, beyond a nominal 3.8 mm nut. This is not a tolerance result: screw-length, nut-height and S102-thickness bounds are unpublished or unaccepted. The corrected direct bolt-demand screen is {vm:.3f} MPa using the R273 elastic-group axial and shear reactions. It omits preload and is not a capacity release.\n\nTwelve blank torque/preload trials, ten receiving rows, a four-axis installation traveler and seven-step verification plan now define the missing evidence. Until those records, a full joined nonlinear model, proof tests and qualified acceptance exist, the A04 joint may not be procured, assembled or structurally credited.\n\n[Interactive A04 guide](../release/hr-v0/a04-joint-p0.1/index.html)\n", encoding="utf-8")

    req = ROOT / "docs/reviews/2026-08-12-r274-independent-review-request.md"
    req.write_text(f"# R274 independent review request\n\n> **{WARNING}**\n\nPlease independently review `{IDENT}` for exact catalog identity, availability boundaries, tolerance-chain completeness, corrected direct-stress arithmetic, tool access, torque/preload development, joined-load scope, proof sequence and fail-closed authority. Confirm that no catalog value has been promoted into a lot allowable and that every physical result remains unexecuted.\n", encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Start here\n\n"
    links = "- [R274 A04 exact-candidate joint package](docs/hr-v0-a04-joint-p0.1.md)\n- [R274 independent review request](docs/reviews/2026-08-12-r274-independent-review-request.md)\n- [R274 validation record](docs/reviews/2026-08-12-r274-validation-record.md)\n- [Interactive R274 A04 guide](release/hr-v0/a04-joint-p0.1/index.html)\n- [Interactive configuration reconciliation P0.38](release/hr-v0/configuration-reconciliation-p0.38/index.html)\n"
    if links.splitlines()[0] not in text:
        text = text.replace(marker, marker + links)
    text = text.replace("Two hundred seventy-three rounds are complete: R01-R273.", "Two hundred seventy-four rounds are complete: R01-R274.")
    readme.write_text(text, encoding="utf-8")

    handoff = ROOT / "docs/handoff-current.md"
    old = handoff.read_text(encoding="utf-8")
    block = f"R274 A04 exact-candidate joint package: **`{IDENT}` names five current supplier/tool candidates and adds stack, torque-preload, joined-analysis, FAI and proof evidence surfaces. No hardware is selected; twelve holds remain open; no procurement, assembly, structural-use or energization authority exists.**\n\n"
    if not old.startswith("R274 A04 exact-candidate joint package:"):
        handoff.write_text(block + old, encoding="utf-8")

    ledger = ROOT / "docs/review-ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("Two hundred seventy-three rounds are complete (R01-R273).", "Two hundred seventy-four rounds are complete (R01-R274).")
    if "| R274 |" not in text:
        text = text.rstrip() + "\n| R274 | 2026-08-12 | A04 exact-candidate joint and evidence-contract pass | Codex project-owned procurement/mechanical correction informed by Sol review; not independent or qualified review | P0.12 restored the original grip but retained unavailable hardware placeholders and no torque/preload or joined-load closure route. | Named five current supplier/tool candidates; corrected the direct combined-stress arithmetic; added measured-stack, torque/preload, installation and proof templates; retained twelve explicit holds and zero work authority. | `docs/hr-v0-a04-joint-p0.1.md`; `release/hr-v0/a04-joint-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.38/` |\n"
    ledger.write_text(text, encoding="utf-8")

    for path in (ROOT / "bom/bom.csv", ROOT / "bom/hr-v0-bom-closure.csv"):
        text = path.read_text(encoding="utf-8")
        text = text.replace("R57 freezes Accu SHKL-M5-20-A2-R360 plus MISUMI SCB2.5-20 and Accu HNN-M2.5-A2 as exact arm-interface candidates on hold; received stack tolerance engagement torque anti-galling locking reuse witness marking physical proof and all remaining structural fasteners remain SELECTION REQUIRED", "R274 defines McMaster 91290A303/98688A148/90576A161 and Wiha 36852/26060 as unselected A04 exact supplier/tool candidates; current quote lot certificates received tolerance torque-preload joined-load fit proof qualified acceptance and all other structural fasteners remain SELECTION REQUIRED")
        path.write_text(text, encoding="utf-8")
    proc = ROOT / "tests/procedures/procedure-registry.csv"
    text = proc.read_text(encoding="utf-8")
    text = text.replace("Accepted configuration received SHKL-M5-20-A2-R360 SCB2.5-20 and HNN-M2.5-A2 lots certificates calibrated gauges torque instrumentation anti-galling/locking plan proof fixture and qualified numerical acceptance limits", "Accepted configuration and interface-specific candidates; for A04 received 91290A303 98688A148 90576A161 lots/certificates and Wiha 36852/26060; calibrated gauges torque/clamp instrumentation locking plan proof fixture and qualified numerical acceptance limits")
    text = text.replace("Exact candidates and templates exist; received-lot fit torque locking reuse physical proof and qualified acceptance remain SELECTION REQUIRED and no assembly or energization is authorized", "R274 supplies exact A04 candidates and blank evidence surfaces; same-session availability received-lot fit torque-preload joined analysis single-use locking physical proof and qualified acceptance remain SELECTION REQUIRED and no procurement assembly or energization is authorized")
    proc.write_text(text, encoding="utf-8")

    # The repository-wide generated-source manifest is refreshed separately
    # under the CAD runtime; this package itself has no CadQuery dependency.
    print("Generated R274 A04 exact-candidate joint package; no authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
