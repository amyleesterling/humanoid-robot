#!/usr/bin/env python3
"""Generate R276 exact-contact J2 soft-pad boundary P0.2.

P0.2 supersedes the radius-based force/velocity numbers in P0.1 with the
configuration-bound P0.12 CAD contact normal and J2 moment arm.  It remains a
development screen: no material, stop, work stage, or safety function is
released.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P01 = ROOT / "mechanical/stops/hr-v0-j2-soft-contact-pad-p0.1"
PKG = ROOT / "mechanical/stops/hr-v0-j2-soft-contact-pad-p0.2"
REL = ROOT / "release/hr-v0/j2-soft-contact-pad-p0.2"
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.39"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.40"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.40"
IDENT = "HR-V0-J2-SOFT-CONTACT-PAD-P0.2"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.40"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    records = [
        {"relative_path": p.relative_to(directory).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size, "warning": WARNING}
        for p in sorted(directory.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"
    ]
    write_csv(directory / "file-manifest.csv", records)


def table(records: list[dict[str, object]]) -> str:
    fields = list(records[0])
    head = "".join(f"<th>{html.escape(k.replace('_', ' '))}</th>" for k in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(r.get(k, '')))}</td>" for k in fields) + "</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    for target in (PKG, REL, CFG, CFG_REL):
        if target.exists():
            shutil.rmtree(target)
    PKG.mkdir(parents=True)

    contact_path = CAD / "cad-contact-normal-evidence.json"
    static_path = CAD / "corrected-static-stop-screen.csv"
    inertia_path = CAD / "j2-positive-stop-analysis.json"
    contact = json.loads(contact_path.read_text(encoding="utf-8"))["selected_conservative_solution"]
    static = rows(static_path)[-1]
    inertia_doc = json.loads(inertia_path.read_text(encoding="utf-8"))
    arm_mm = float(contact["j2_effective_normal_moment_arm_mm"])
    force_n = float(static["single_rail_normal_force_n"])
    drive_nm = float(static["drive_torque_nm"])
    gravity_nm = float(static["worst_sign_gravity_nm"])
    reaction_nm = float(static["reaction_torque_nm"])
    inertia = float(inertia_doc["allocated_elbow_inertia_kg_m2_excludes_reflected_rotor"])
    travel_mm = 0.75
    area_mm2 = 42.0 * 12.0
    e10 = 0.5 * inertia * math.radians(10.0) ** 2
    e30 = 0.5 * inertia * math.radians(30.0) ** 2
    local_angle_rad = travel_mm / arm_mm
    local_angle_deg = math.degrees(local_angle_rad)
    drive_force_n = drive_nm * 1000.0 / arm_mm
    gravity_force_n = gravity_nm * 1000.0 / arm_mm
    upper_work_j = force_n * travel_mm / 1000.0
    normal_speed_mps = arm_mm / 1000.0 * math.radians(10.0)
    ace_min_mps = 1.89 * 0.3048
    pressure_single_mpa = force_n / area_mm2
    pressure_twin_mpa = force_n / (2.0 * area_mm2)
    published_max_cfd_mpa = 0.058
    published_one_coupon_n = published_max_cfd_mpa * area_mm2
    published_two_coupon_n = 2.0 * published_one_coupon_n

    candidate = rows(P01 / "candidate-definition.csv")
    candidate[0]["selection_state"] = "PREFERRED TEST-COUPON CANDIDATE / UNSELECTED / P0.2 EXACT-CONTACT REVIEW"
    candidate[0]["functional_role"] = "sacrificial contact/noise/rebound pad only; P0.12 metal rails remain structural backup"
    write_csv(PKG / "candidate-definition.csv", candidate)

    source_records = rows(P01 / "source-register.csv")
    for record in source_records:
        record["state"] = record["state"].replace("PREFERRED TEST-COUPON CANDIDATE / UNSELECTED", "PREFERRED TEST-COUPON CANDIDATE / UNSELECTED / P0.2 EXACT-CONTACT REVIEW")
        if record["source_id"] == "PAD-SRC-004":
            record["boundary"] = f"4 mm stroke exceeds 0.75 mm envelope and catalog minimum speed is {ace_min_mps/normal_speed_mps:.1f}x the P0.12 local-normal 10 deg/s speed"
    write_csv(PKG / "source-register.csv", source_records)

    bindings = [
        {"binding_id":"PAD-BIND-001","source_path":contact_path.relative_to(ROOT).as_posix(),"sha256":sha(contact_path),"accepted_use":"exact nominal contact point, normal and 44.072041 mm local moment arm","excluded_use":"tolerance, deformation, wear, as-built contact","warning":WARNING},
        {"binding_id":"PAD-BIND-002","source_path":static_path.relative_to(ROOT).as_posix(),"sha256":sha(static_path),"accepted_use":"P0.12 endpoint plus worst-sign gravity demand screen","excluded_use":"continuous torque, measured current decay, dynamic impact, allowable","warning":WARNING},
        {"binding_id":"PAD-BIND-003","source_path":inertia_path.relative_to(ROOT).as_posix(),"sha256":sha(inertia_path),"accepted_use":"arithmetic sensitivity using 0.010144 kg m2 project estimate","excluded_use":"accepted/as-built inertia or reflected rotor inertia","warning":WARNING},
    ]
    write_csv(PKG / "configuration-source-binding.csv", bindings)

    load_cases = [
        {"case_id":"PAD2-LC-001","case":"10 deg/s kinetic approach","formula":"0.5*I_eff*omega^2","inputs":f"I_eff={inertia:.6f} kg m2 excludes reflected rotor; omega=10 deg/s","result":f"{e10:.9f} J","disposition":"ARITHMETIC ONLY; INERTIA UNACCEPTED","required_successor":"accepted as-built inertia incl reflected rotor and maximum measured speed","warning":WARNING},
        {"case_id":"PAD2-LC-002","case":"30 deg/s kinetic sensitivity","formula":"0.5*I_eff*omega^2","inputs":"same unaccepted I_eff; omega=30 deg/s","result":f"{e30:.9f} J","disposition":"SENSITIVITY ONLY; 30 DEG/S NOT RELEASED","required_successor":"fault/overspeed allocation and physical verification","warning":WARNING},
        {"case_id":"PAD2-LC-003","case":"P0.12 endpoint plus gravity local-normal force","formula":"F_n=(T_drive+T_gravity)/|r x n|","inputs":f"{drive_nm:.3f}+{gravity_nm:.3f} N m; exact nominal arm {arm_mm:.6f} mm","result":f"{force_n:.3f} N single-rail fail-safe demand","disposition":"CONFIGURATION-BOUND STATIC DEMAND SCREEN ONLY","required_successor":"accepted torque/current decay, contact tolerance and nonlinear joined model","warning":WARNING},
        {"case_id":"PAD2-LC-004","case":"upper-bound work over full 0.75 mm contact-to-backup envelope","formula":"W_upper=F_n*s using local constant-force/arm approximation","inputs":f"{force_n:.3f} N; {travel_mm:.3f} mm; local angle {local_angle_deg:.6f} deg","result":f"{upper_work_j:.9f} J; {upper_work_j/e10:.1f}x 10 deg/s kinetic estimate","disposition":"CONSERVATIVE GEOMETRIC UPPER-BOUND WARNING; NOT ACTUAL PAD STROKE","required_successor":"released metal-backup gap plus measured force-stroke and torque-decay integration","warning":WARNING},
        {"case_id":"PAD2-LC-005","case":"single-rail full-coupon average pressure","formula":"F_n/(42*12 mm2)","inputs":"one full coupon; no edge concentration","result":f"{pressure_single_mpa:.6f} MPa","disposition":"{:.2f}x PUBLISHED 25% CFD MAX; PAD CANNOT CARRY STATIC ENDPOINT DEMAND".format(pressure_single_mpa/published_max_cfd_mpa),"required_successor":"dynamic force-stroke/bottom-out test at actual rate, temperature and tolerance","warning":WARNING},
        {"case_id":"PAD2-LC-006","case":"ideal two-coupon equal-share average pressure","formula":"F_n/(2*42*12 mm2)","inputs":"perfect equal share only; receives no fail-safe credit","result":f"{pressure_twin_mpa:.6f} MPa","disposition":"{:.2f}x PUBLISHED 25% CFD MAX; NOT FAIL-SAFE".format(pressure_twin_mpa/published_max_cfd_mpa),"required_successor":"worst-tolerance first-contact and single-rail physical tests","warning":WARNING},
        {"case_id":"PAD2-LC-007","case":"ACE catalog minimum-speed comparison","formula":"v_local=omega*|r x n|","inputs":f"P0.12 local normal speed {normal_speed_mps:.6f} m/s; ACE minimum {ace_min_mps:.6f} m/s","result":f"ACE minimum is {ace_min_mps/normal_speed_mps:.1f}x local approach speed","disposition":"MC5M-3-B REJECTED FOR CURRENT ENVELOPE/SPEED","required_successor":"architecture change plus written ACE sizing if a structural absorber is required","warning":WARNING},
    ]
    write_csv(PKG / "exact-contact-load-case-register.csv", load_cases)

    capacity = [
        {"screen_id":"PAD2-CAP-001","basis":"Rogers published maximum 25% CFD for 2300327","pressure_mpa":f"{published_max_cfd_mpa:.6f}","area_mm2":f"{area_mm2:.3f}","published_force_n":f"{published_one_coupon_n:.3f}","p012_demand_n":f"{force_n:.3f}","demand_over_published_force":f"{force_n/published_one_coupon_n:.3f}","interpretation":"one coupon cannot carry endpoint demand at published 25% CFD boundary","warning":WARNING},
        {"screen_id":"PAD2-CAP-002","basis":"two coupons at published maximum 25% CFD with ideal sharing","pressure_mpa":f"{published_max_cfd_mpa:.6f}","area_mm2":f"{2*area_mm2:.3f}","published_force_n":f"{published_two_coupon_n:.3f}","p012_demand_n":f"{force_n:.3f}","demand_over_published_force":f"{force_n/published_two_coupon_n:.3f}","interpretation":"ideal pair still cannot carry endpoint demand and receives no fail-safe credit","warning":WARNING},
    ]
    write_csv(PKG / "published-force-boundary.csv", capacity)

    tests = rows(P01 / "verification-matrix.csv")
    for index, record in enumerate(tests, 1):
        record["test_id"] = f"PAD2-T-{index:02d}"
    tests.extend([
        {"test_id":"PAD2-T-11","test":"measure installed pad protrusion and metal-backup gap at all four contact corners","configuration":"received C06/C07, captive pad coupons and calibrated depth metrology; exact repetitions SELECTION REQUIRED","acceptance":"qualified numerical gap/tolerance limits required before execution","execution":"NOT EXECUTED","result":"OPEN","evidence_uri":"","warning":WARNING},
        {"test_id":"PAD2-T-12","test":"integrate current/torque and joint motion from first pad contact to metal backup","configuration":"guarded instrumented stop fixture with synchronized current, voltage, force, J2 angle and backup-contact event; exact fixture/limits SELECTION REQUIRED","acceptance":"qualified energy, force, travel and stopping-time limits required before powered authorization","execution":"NOT EXECUTED","result":"OPEN","evidence_uri":"","warning":WARNING},
    ])
    write_csv(PKG / "verification-matrix.csv", tests)

    holds_text = [
        "Current supplier quote, exact 2300327 identity, lot and CoC accepted",
        "Incoming thickness, coupon geometry and captive retention pass inspection",
        "Installed protrusion and metal-backup gap are dimensioned, toleranced and accepted",
        "Exact contact point/normal/work path through tolerance and deformation are accepted",
        "As-built inertia including reflected rotor is measured and accepted",
        "Maximum approach/fault speed and current/torque decay are measured",
        "Dynamic force-stroke, hysteresis, bottom-out and rebound are characterized",
        "Temperature, aging, contamination, compression-set and life limits are qualified",
        "Single-rail and twin-rail tests correlate with accepted nonlinear model",
        "Metal backup C06/C07 and full joined load path are accepted independently",
        "Guard/overtravel/pinch envelope includes pad tolerance, loss and failure",
        "Qualified release plus separate procurement, assembly and powered-work authorities are signed",
    ]
    holds = [{"hold_id":f"R276-H{i:02d}","hold":x,"state":"OPEN","execution":"NOT EXECUTED","release_effect":"BLOCKS PAD SELECTION AND MOTION","warning":WARNING} for i, x in enumerate(holds_text, 1)]
    write_csv(PKG / "open-holds.csv", holds)
    write_csv(PKG / "acceptance-matrix.csv", [{"acceptance_id":f"R276-ACC-{i:02d}","criterion":x,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i, x in enumerate(holds_text, 1)])

    status = {
        "identifier":IDENT,"round":"R276","date":"2026-08-12","supersedes":"HR-V0-J2-SOFT-CONTACT-PAD-P0.1 for current calculation use",
        "candidate":"Rogers 2300327","cad_configuration":"HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE","exact_nominal_moment_arm_mm":round(arm_mm, 9),
        "endpoint_plus_gravity_force_n":round(force_n, 6),"upper_bound_work_j":round(upper_work_j, 12),"candidate_selected":False,"sole_structural_stop":False,
        "procurement_authorized":False,"assembly_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"open_holds":12,"warning":WARNING,
    }
    (PKG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (PKG / "README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR276 supersedes P0.1's radius-based force/velocity warning with P0.12's exact nominal contact normal and {arm_mm:.6f} mm J2 moment arm. Rogers 2300327 remains an unselected sacrificial contact pad; the metal rails remain the structural stop and every physical/qualified hold remains open.\n", encoding="utf-8")

    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R276 exact-contact pad boundary</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#79abd0;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(20px,4vw,52px)}}header{{background:linear-gradient(135deg,var(--blue),#0879be);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);padding:15px;border-radius:12px;font-size:clamp(16px,1.4vw,21px);font-weight:850;color:#fff1b5}}h1{{font-size:clamp(36px,5.5vw,70px);line-height:1.03}}h2{{font-size:clamp(25px,3vw,40px);line-height:1.15}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px}}.metric,.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:19px}}.metric strong{{display:block;color:#075e9c;font-size:31px}}.hold{{background:var(--hold);border:3px solid var(--gold);border-radius:14px;padding:20px}}section{{margin:34px 0}}label{{font-weight:800;display:block;margin-top:12px}}input{{font:16px system-ui;width:100%;max-width:300px;padding:8px}}output{{font-size:24px;font-weight:900;color:#075e9c}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1120px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #c6deed;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}@media(max-width:600px){{header,main{{padding:18px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R276 &middot; {IDENT} &middot; exact nominal contact, zero selection</p><h1>The pad warning now uses the actual stop geometry.</h1><p>P0.12's CAD contact normal gives a {arm_mm:.3f} mm J2 moment arm. That raises the endpoint-plus-gravity demand and strengthens the conclusion: the pad cannot be the structural stop.</p></div></header><main><section class='metrics'><div class='metric'><strong>{arm_mm:.3f} mm</strong>exact nominal moment arm</div><div class='metric'><strong>{force_n:.1f} N</strong>single-rail static demand</div><div class='metric'><strong>{upper_work_j:.3f} J</strong>0.75 mm upper work bound</div><div class='metric'><strong>{upper_work_j/e10:.0f}x</strong>work / 10 deg/s kinetic</div><div class='metric'><strong>{pressure_single_mpa:.3f} MPa</strong>single-coupon pressure</div><div class='metric'><strong>0</strong>safety credit</div></section><section class='hold'><h2>The decision is unchanged, but the evidence is stricter</h2><p>Rogers 2300327 is only a test-coupon candidate for contact noise and rebound. The full 0.75 mm value is a conservative contact-to-backup travel envelope, not an available foam stroke. The backup gap, pad protrusion, torque decay and force-stroke curve must be measured and released.</p></section><section class='card'><h2>Explore the local static screen</h2><p>This calculator is a dimensional warning only. It cannot predict impact or authorize a test.</p><div class='metrics'><label>Total reaction torque N m<input id='t' type='number' step='.001' value='{reaction_nm:.3f}'></label><label>Effective moment arm mm<input id='a' type='number' step='.001' value='{arm_mm:.6f}'></label><label>Contact-to-backup travel mm<input id='s' type='number' step='.001' value='{travel_mm:.3f}'></label></div><p><output id='out'>{force_n:.3f} N; {upper_work_j:.6f} J</output></p></section><section><h2>Exact-contact load cases</h2>{table(load_cases)}</section><section><h2>Published-force boundary</h2>{table(capacity)}</section><section><h2>Configuration bindings</h2>{table(bindings)}</section><section><h2>Evidence still required</h2>{table(holds)}</section></main><script>const q=x=>Number(document.getElementById(x).value);function u(){{const f=q('t')*1000/q('a'),w=f*q('s')/1000;document.getElementById('out').value=f.toFixed(3)+' N; '+w.toFixed(6)+' J'}}['t','a','s'].forEach(x=>document.getElementById(x).addEventListener('input',u));u();</script></body></html>"""
    (PKG / "index.html").write_text(page, encoding="utf-8")
    manifest(PKG)
    shutil.copytree(PKG, REL)
    manifest(REL)

    shutil.copytree(CFG0, CFG)
    current = rows(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-59","role":"P0.12 exact-contact soft-pad demand and evidence boundary","identifier":IDENT,"source_path":"release/hr-v0/j2-soft-contact-pad-p0.2/package-status.json","configuration_state":"CURRENT REVIEW EVIDENCE - P0.2 TEST COUPON UNSELECTED","release_boundary":"pad has no structural-stop/safety credit; backup gap, dynamics, joined load path, physical and qualified closure open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", current)
    supers = rows(CFG / "supersession-map.csv")
    supers.append({"record_id":"SUP-54","prior_identifier":"HR-V0-CONFIG-REC-P0.39","current_or_required_successor":CFG_IDENT,"disposition":"superseded for package indexing; pad P0.2 supersedes P0.1 for current force/velocity calculation use; P0.12 and pad remain unselected","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", supers)
    ch = rows(CFG / "open-holds.csv")
    ca = rows(CFG / "acceptance-matrix.csv")
    for hold in holds:
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled physical result and qualified acceptance","warning":WARNING})
        ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "open-holds.csv", ch)
    write_csv(CFG / "acceptance-matrix.csv", ca)
    bmap = rows(CFG / "bom-integration-map.csv")
    bmap.append({"item_id":"BOM-110","role":"two J2 soft-contact coupons from quoted Rogers 2300327 stock/converter route","bound_identifier":IDENT,"closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO","warning":WARNING})
    write_csv(CFG / "bom-integration-map.csv", bmap)
    gates = rows(CFG / "gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005", "EG-006", "EG-007", "EG-028"}:
            gate["evidence_added"] += f"; {IDENT} exact P0.12 contact/force/work and pad published-force boundary"
            gate["remaining_evidence"] += "; released backup gap/protrusion, received coupons, force-stroke, torque-decay integration, joined nonlinear model and physical proof"
    write_csv(CFG / "gate-impact.csv", gates)
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    cfg_status.update({"identifier":CFG_IDENT,"round":"R276","current_records":len(current),"supersession_records":len(supers),"open_holds":len(ch),"acceptance_rows":len(ca),"j2_soft_contact_review":IDENT,"j2_pad_selected":False,"procurement_authorized":False,"assembly_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False})
    (CFG / "package-status.json").write_text(json.dumps(cfg_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR276 indexes P0.2's exact P0.12 contact-load boundary. Rogers 2300327 remains an unselected sacrificial test coupon with no structural-stop or safety credit.\n", encoding="utf-8")
    write_csv(CFG / "source-hash-register.csv", [{"source_path":r["source_path"],"sha256":sha(ROOT / r["source_path"]),"role":r["role"],"warning":WARNING} for r in current])
    shutil.copy2(PKG / "index.html", CFG / "index.html")
    manifest(CFG)
    shutil.copytree(CFG, CFG_REL)
    manifest(CFG_REL)

    doc = ROOT / "docs/hr-v0-j2-soft-contact-pad-p0.2.md"
    doc.write_text(f"# HR-V0 J2 soft-contact pad P0.2\n\n> **{WARNING}**\n\nR276 supersedes P0.1 for current calculation use. P0.12's exact nominal contact normal gives a {arm_mm:.6f} mm J2 moment arm and {force_n:.3f} N single-rail endpoint-plus-gravity demand. A local constant-force upper bound through the full 0.75 mm contact-to-backup envelope is {upper_work_j:.9f} J, {upper_work_j/e10:.1f} times the unaccepted 10 deg/s kinetic estimate. The 0.75 mm value is not an available pad stroke.\n\nAt Rogers' published 58 kPa maximum 25% CFD boundary, one 42 x 12 mm coupon corresponds to {published_one_coupon_n:.3f} N and two ideal-sharing coupons to {published_two_coupon_n:.3f} N. Both remain below the P0.12 endpoint demand. Rogers 2300327 therefore remains only an unselected sacrificial contact/noise/rebound candidate; the metal backup is mandatory.\n\n[Interactive exact-contact guide](../release/hr-v0/j2-soft-contact-pad-p0.2/index.html)\n", encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r276-independent-review-request.md").write_text(f"# R276 independent review request\n\n> **{WARNING}**\n\nPlease independently review `{IDENT}` for exact P0.12 source binding, torque-to-normal-force arithmetic, local travel/work boundary, approach velocity, published CFD interpretation, structural-backup requirement, BOM/configuration integration, physical test completeness and fail-closed authority. P0.2 selects no pad or stop and authorizes no work.\n", encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r276-status.md").write_text(f"# Sol R12 post-R276 status\n\n> **{WARNING}**\n\nR276 corrects the current soft-pad calculation boundary to the exact P0.12 contact normal and moment arm. It strengthens the evidence that the pad cannot be the structural stop. It does not close a Sol R12 blocker: B-003, B-007, B-010 and B-013 remain `PARTIALLY_ADDRESSED_OPEN`; every received, dynamic, joined-load, physical, qualified-review and authority prerequisite remains open.\n", encoding="utf-8")

    bom_path = ROOT / "bom/bom.csv"
    bom = rows(bom_path)
    if not any(r["item_id"] == "BOM-110" for r in bom):
        bom.append({"item_id":"BOM-110","subsystem":"j2_soft_contact_pad","manufacturer":"Rogers Corporation","manufacturer_part_number":"2300327; PORON 4790-92-25024-04P; converter/cut-piece order route SELECTION REQUIRED","quantity":"2 finished 42 x 12 mm coupons from one quoted stock/converter route","baseline_status":"exact_candidate_hold","selection_basis":f"R276 exact material/product candidate for sacrificial contact/noise/rebound use only. Quote, converter/cut order code, lot/CoC, thickness, retention, installed gap, dynamic force-stroke, life, physical proof and qualified acceptance remain open. {WARNING}"})
        write_csv(bom_path, bom)

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Start here\n\n"
    links = "- [R276 exact-contact J2 pad boundary](docs/hr-v0-j2-soft-contact-pad-p0.2.md)\n- [R276 independent review request](docs/reviews/2026-08-12-r276-independent-review-request.md)\n- [R276 validation record](docs/reviews/2026-08-12-r276-validation-record.md)\n- [Interactive R276 exact-contact guide](release/hr-v0/j2-soft-contact-pad-p0.2/index.html)\n- [Interactive configuration reconciliation P0.40](release/hr-v0/configuration-reconciliation-p0.40/index.html)\n"
    if links.splitlines()[0] not in text:
        text = text.replace(marker, marker + links)
    text = text.replace("Two hundred seventy-five rounds are complete: R01-R275.", "Two hundred seventy-six rounds are complete: R01-R276.")
    text = text.replace("R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad and retains the metal rails as the structural backup.", "R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad; R276 supersedes its radius-based warning with P0.12's exact contact normal and retains the metal rails as the structural backup.")
    readme.write_text(text, encoding="utf-8")

    handoff = ROOT / "docs/handoff-current.md"
    old = handoff.read_text(encoding="utf-8")
    block = f"R276 exact-contact J2 pad correction: **`{IDENT}` supersedes P0.1's radius-based force/velocity warning with P0.12's exact 44.072041 mm moment arm. The endpoint-plus-gravity demand is {force_n:.3f} N; the full-envelope work warning is {upper_work_j:.6f} J. Rogers 2300327 remains unselected, the metal rails remain structural, twelve holds remain open and zero work/safety authority exists.**\n\n"
    handoff.write_text(old if old.startswith("R276 exact-contact J2 pad correction:") else block + old, encoding="utf-8")

    ledger = ROOT / "docs/review-ledger.md"
    text = ledger.read_text(encoding="utf-8").replace("Two hundred seventy-five rounds are complete (R01-R275).", "Two hundred seventy-six rounds are complete (R01-R276).")
    text = text.replace("R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad and retains the metal rails as the structural backup.", "R275 names Rogers 2300327 only as an unselected sacrificial soft-contact pad; R276 supersedes its radius-based warning with P0.12's exact contact normal and retains the metal rails as the structural backup.")
    if "| R276 |" not in text:
        text = text.rstrip() + f"\n| R276 | 2026-08-12 | Exact-contact J2 soft-pad boundary correction | Codex project-owned mechanical/calculation/configuration correction; not independent or qualified review | R275 retained a superseded radius-based force and tangent-speed value as a warning, understating the current P0.12 nominal contact demand. | Issued P0.2 bound to exact P0.12 contact sources: {arm_mm:.6f} mm moment arm, {force_n:.3f} N endpoint-plus-gravity demand, {upper_work_j:.6f} J full-envelope upper work warning and {normal_speed_mps:.6f} m/s local-normal speed. Added BOM-110, physical gap/energy tests and P0.40. Pad remains unselected; metal backup and all physical/qualified holds remain. | `docs/hr-v0-j2-soft-contact-pad-p0.2.md`; `release/hr-v0/j2-soft-contact-pad-p0.2/`; `configuration/hr-v0-config-reconciliation-p0.40/` |\n"
    ledger.write_text(text, encoding="utf-8")

    import generate_hr_v0_collapse_envelope as generated_manifest
    generated_manifest.write_generated_source_manifest()
    print(f"Generated R276 {IDENT}; force={force_n:.3f} N, upper work={upper_work_j:.9f} J; no authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
