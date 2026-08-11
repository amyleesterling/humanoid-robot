#!/usr/bin/env python3
"""Generate R243 P1.21 termination-process evidence and config P0.7."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/termination/hr-v0-p121-termination-p0.1"
OUT = ROOT / "release/hr-v0/p121-termination-p0.1"
CFG_SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.6"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.7"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.7"
IDENT = "HR-V0-P121-TERM-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.7"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing headerless CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, str]) -> dict[str, str]:
    return {**row, "warning": WARNING}


def manifest(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    write(directory / "file-manifest.csv", [
        {"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files
    ])


def package_data() -> dict[str, list[dict[str, str]]]:
    sources = [
        warned({"source_id":"R243-SRC-001","manufacturer_or_owner":"Phoenix Contact","artifact":"AI 1,5 - 8 BK item 3200043","revision_or_date":"current official US catalog record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/ferrule-ai-15-8-bk-3200043","controlled_fact":"1.5 mm2 / AWG 16 insulated ferrule; 8 mm contact range; 11 mm conductor stripping length; 100-piece minimum order; DIN 46228-4 and UL 486F-E","does_not_establish":"compatibility with every receiving terminal, received crimp quality, installed retention or application release"}),
        warned({"source_id":"R243-SRC-002","manufacturer_or_owner":"Phoenix Contact","artifact":"A 1,5 - 7 item 3200263","revision_or_date":"current official US catalog record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/ferrule-a-15-7-3200263","controlled_fact":"1.5 mm2 / AWG 16 uninsulated ferrule; 7 mm sleeve/contact range and 7 mm stripping length; 1000-piece minimum order; DIN 46228-1 and UL 486F-A","does_not_establish":"Pilz application acceptance, received crimp quality, installed retention or application release"}),
        warned({"source_id":"R243-SRC-003","manufacturer_or_owner":"Phoenix Contact","artifact":"CRIMPFOX 6 item 1212034","revision_or_date":"current official US catalog record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/crimping-tool-crimpfox-6-1212034","controlled_fact":"trapezoidal ferrule crimper; station 2 covers 1.0 to 1.5 mm2 / AWG 18 to 16; unlockable pressure lock","does_not_establish":"received calibration, wear condition, crimp height, operator qualification or production acceptance"}),
        warned({"source_id":"R243-SRC-004","manufacturer_or_owner":"Phoenix Contact","artifact":"UL-certified ferrule/tool combinations","revision_or_date":"current official overview published 2025; accessed 2026-08-11","official_or_controlled_uri":"https://assets.phoenixcontact.com/file/d820f27b-c6a0-47ab-8e61-e698e1886ad5/media/original?EN_Info_UL-zertifizierte_Kombinationen_LoRes.pdf=","controlled_fact":"items 3200043 and 3200263 are listed with CRIMPFOX 6 item 1212034 for 1.5 mm2 / AWG 16","does_not_establish":"Project Button terminal compatibility, received-lot identity or installed acceptance"}),
        warned({"source_id":"R243-SRC-005","manufacturer_or_owner":"Phoenix Contact","artifact":"WIREFOX 10 item 1212150","revision_or_date":"current official US catalog record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/stripping-tool-wirefox-10-1212150","controlled_fact":"self-adjusting stripper covers 0.02 to 10 mm2 / AWG 34 to 8 with 2 to 18 mm adjustable strip length","does_not_establish":"blade condition, settings, damage-free stripping of the received Belden lot or production acceptance"}),
        warned({"source_id":"R243-SRC-006","manufacturer_or_owner":"Phoenix Contact","artifact":"TSD-M 1,2NM item 1212224","revision_or_date":"current official US catalog record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/torque-tool-tsd-m-12nm-1212224","controlled_fact":"adjustable 0.3 to 1.2 N m torque screwdriver; published accuracy plus or minus 6 percent; external hexagonal output","does_not_establish":"calibration state, bit choice, terminal access, accepted project setting or witnessed torque"}),
        warned({"source_id":"R243-SRC-007","manufacturer_or_owner":"Phoenix Contact","artifact":"2025 Tools handbook pull-out table","revision_or_date":"2025 handbook; current official asset accessed 2026-08-11","official_or_controlled_uri":"https://assets.phoenixcontact.com/file/654b9ef5-f5d2-4503-949e-8aa342730567/media/original?1357900_EN_SG_Tools_LoRes.pdf=","controlled_fact":"published cross-section pull-out value for 1.5 mm2 / AWG 16 is 40 N; described test applies the force for 60 seconds without damage to the crimp point","does_not_establish":"sample count, test fixture, calibrated equipment, installed-terminal pull criterion or Project Button acceptance"}),
        warned({"source_id":"R243-SRC-008","manufacturer_or_owner":"Pilz","artifact":"PNOZ s4 operating manual","revision_or_date":"21396-EN-23 dated 2026-06-22; accessed 2026-08-11","official_or_controlled_uri":"electrical/vendor/pilz/pnoz-s4-750104-r116/PNOZ_s4_21396-EN-23.pdf","controlled_fact":"750104 screw terminals accept one flexible 0.25 to 2.5 mm2 / AWG 24 to 12 conductor; 7 mm stripping length; 0.5 N m torque","does_not_establish":"specific Phoenix ferrule approval, driver-bit geometry, installed retention or achieved safety performance"}),
        warned({"source_id":"R243-SRC-009","manufacturer_or_owner":"Phoenix Contact","artifact":"PLC-RSC-24DC/21-21 item 2967060","revision_or_date":"data maintenance 2026-04-01; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060","controlled_fact":"single ferrule range 0.2 to 2.5 mm2; 8 mm stripping length; tightening torque 0.6 to 0.8 N m","does_not_establish":"specific ferrule/tool application acceptance, selected torque, bit geometry or installed result"}),
        warned({"source_id":"R243-SRC-010","manufacturer_or_owner":"Phoenix Contact","artifact":"PTFIX 6/18X2,5-NS35 RD item 3273114","revision_or_date":"official PDF generated 2026-05-21; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/distributor-terminal-block-ptfix-618x25-ns35-rd-3273114?type=pdf","controlled_fact":"load contacts accept ferruled flexible conductors 0.14 to 2.5 mm2; published strip range 8 to 10 mm; push-in connection has no screw-torque step","does_not_establish":"specific ferrule insertion acceptance, received fit, pull retention or color convention"}),
        warned({"source_id":"R243-SRC-011","manufacturer_or_owner":"Project Button","artifact":"R242 conductor/fill package","revision_or_date":"HR-V0-P121-CONDUCTOR-FILL-P0.1 dated 2026-08-11","official_or_controlled_uri":"release/hr-v0/p121-conductor-fill-p0.1/package-status.json","controlled_fact":"seven Belden 3057 BL005 held conductor candidates create exactly fourteen listed endpoints","does_not_establish":"cut lengths, terminations, installed evidence, P1.21 acceptance or work authority"}),
    ]
    materials = [
        warned({"candidate_id":"TERM-MAT-001","manufacturer":"Phoenix Contact","item":"3200043","designation":"AI 1,5 - 8 BK","application_quantity":"12 ferrules","order_quantity":"1 minimum pack of 100","scope":"five XD24 and seven KWD endpoints","contact_length_mm":"8","conductor_strip_mm":"11","state":"EXACT HELD CANDIDATE","procurement_released":"NO"}),
        warned({"candidate_id":"TERM-MAT-002","manufacturer":"Phoenix Contact","item":"3200263","designation":"A 1,5 - 7","application_quantity":"2 ferrules","order_quantity":"1 minimum pack of 1000","scope":"SR1:A1 and SRA1:A1 only","contact_length_mm":"7","conductor_strip_mm":"7","state":"EXACT HELD CANDIDATE","procurement_released":"NO"}),
    ]
    tools = [
        warned({"tool_id":"TERM-TOOL-001","manufacturer":"Phoenix Contact","item":"1212034","designation":"CRIMPFOX 6","purpose":"trapezoidal crimp at marked station 2 for 1.0 to 1.5 mm2 / AWG 18 to 16","candidate_state":"EXACT EVALUATION TOOL ON HOLD","required_before_use":"received identity, clean/wear inspection, valid calibration or controlled capability check, operator qualification","purchase_authorized":"NO"}),
        warned({"tool_id":"TERM-TOOL-002","manufacturer":"Phoenix Contact","item":"1212150","designation":"WIREFOX 10","purpose":"prepare 7 mm and 11 mm strip lengths on received Belden 3057","candidate_state":"EXACT EVALUATION TOOL ON HOLD","required_before_use":"received identity, blade inspection, setting verification and damage-free strip coupons","purchase_authorized":"NO"}),
        warned({"tool_id":"TERM-TOOL-003","manufacturer":"Phoenix Contact","item":"1212224","designation":"TSD-M 1,2NM","purpose":"candidate torque driver covering Pilz 0.5 N m and Phoenix 0.6 to 0.8 N m ranges","candidate_state":"EXACT EVALUATION TOOL ON HOLD","required_before_use":"current calibration certificate, exact compatible bit for each terminal, access and repeatability verification","purchase_authorized":"NO"}),
        warned({"tool_id":"TERM-TOOL-OPEN","manufacturer":"SELECTION REQUIRED","item":"SELECTION REQUIRED","designation":"calibrated axial pull-test fixture and grips","purpose":"apply and record 40 N for 60 seconds to sacrificial crimp coupons without loading robot devices","candidate_state":"SELECTION REQUIRED","required_before_use":"range, accuracy, calibration, grip method, sample plan and qualified acceptance","purchase_authorized":"NO"}),
    ]

    conductor_rows = read(ROOT / "release/hr-v0/p121-conductor-fill-p0.1/p121-conductor-schedule.csv")
    endpoint_rows: list[dict[str, str]] = []
    for conductor in conductor_rows:
        for end, endpoint in (("A", conductor["from"]), ("B", conductor["to"])):
            if endpoint.startswith("XD24:"):
                device, device_item, ferrule, contact, strip, torque, method = "XD24", "Phoenix Contact 3273114", "3200043 / AI 1,5 - 8 BK", "8", "11", "NOT APPLICABLE - PUSH-IN", "insert ferrule fully into assigned PTFIX load contact; received fit/retention proof required"
            elif endpoint in {"SR1:A1", "SRA1:A1"}:
                device, device_item, ferrule, contact, strip, torque, method = endpoint.split(":")[0], "Pilz 750104", "3200263 / A 1,5 - 7", "7", "7", "0.5", "single uninsulated 7 mm ferrule candidate; exact bit and Pilz application acceptance required"
            else:
                device, device_item, ferrule, contact, strip, torque, method = endpoint.split(":")[0], "Phoenix Contact 2967060", "3200043 / AI 1,5 - 8 BK", "8", "11", "0.7 PROPOSED WITHIN PUBLISHED 0.6 TO 0.8", "single insulated 8 mm ferrule candidate; exact bit and received fit required"
            endpoint_rows.append(warned({
                "endpoint_id": f"{conductor['allocation_id']}-{end}", "conductor_id": conductor["allocation_id"],
                "endpoint": endpoint, "device": device, "device_item": device_item, "conductor":"Belden 3057 BL005 / AWG 16",
                "ferrule_candidate": ferrule, "ferrule_contact_length_mm": contact, "conductor_preparation_strip_mm": strip,
                "crimp_tool":"Phoenix Contact 1212034 / station 2", "terminal_torque_Nm": torque,
                "installation_method": method, "state":"CANDIDATE - NOT INSTALLED", "physical_result":"NOT EXECUTED"
            }))

    process = [
        warned({"step_id":"TERM-P01","step":"Verify received Belden 3057 BL005, ferrule lot and tool identities against controlled records","input":"received labels, lot/date codes and certificates","acceptance":"exact identities recorded; no substitution","state":"NOT EXECUTED"}),
        warned({"step_id":"TERM-P02","step":"Prepare sacrificial strip coupons with WIREFOX 10","input":"7 mm for item 3200263; 11 mm for item 3200043","acceptance":"no nicked, cut, missing or splayed strands; dimensions recorded with calibrated equipment","state":"NOT EXECUTED"}),
        warned({"step_id":"TERM-P03","step":"Crimp each ferrule format with CRIMPFOX 6 station 2","input":"received conductor/ferrule lots and qualified operator","acceptance":"full pressure-lock cycle; conductor visible at sleeve end; collar/strand capture and crimp geometry pass approved inspection","state":"NOT EXECUTED"}),
        warned({"step_id":"TERM-P04","step":"Qualify sacrificial crimp coupons","input":"minimum proposed three coupons per ferrule format; final sample plan requires qualified approval","acceptance":"each coupon withstands 40 N axial force for 60 seconds without crimp-point damage; raw force-time record retained","state":"NOT EXECUTED"}),
        warned({"step_id":"TERM-P05","step":"Verify ferrule fit in one received terminal of each family without robot wiring","input":"3273114, 2967060 and 750104 received samples","acceptance":"full insertion, no exposed strand, no collar interference, no adjacent-contact bridge and accepted terminal retention","state":"NOT EXECUTED"}),
        warned({"step_id":"TERM-P06","step":"Install only under a separately signed work instruction","input":"released cuts, endpoint schedule, calibrated torque tool, exact accepted bits and witnesses","acceptance":"all fourteen endpoints match schedule; torque/retention/photographic records complete; continuity and isolation pass","state":"NOT EXECUTED"}),
    ]
    torque = [
        warned({"interface":"XD24 / 3273114","endpoints":"5","manufacturer_requirement":"push-in; ferruled range 0.14 to 2.5 mm2; published strip range 8 to 10 mm","project_candidate":"3200043 with 8 mm contact sleeve; no torque","tool":"WIREFOX 10 + CRIMPFOX 6","open_input":"received insertion depth, collar clearance, retention criterion and qualified application acceptance","state":"OPEN"}),
        warned({"interface":"SR1/SRA1 / Pilz 750104","endpoints":"2","manufacturer_requirement":"7 mm strip; 0.5 N m torque; single flexible conductor 0.25 to 2.5 mm2","project_candidate":"3200263 with 7 mm uninsulated sleeve; 0.5 N m candidate setting","tool":"WIREFOX 10 + CRIMPFOX 6 + TSD-M 1,2NM; BIT SELECTION REQUIRED","open_input":"written/qualified ferrule application acceptance, exact bit, calibrated torque witness and received retention","state":"OPEN"}),
        warned({"interface":"KWD1/KWD2 / 2967060","endpoints":"7","manufacturer_requirement":"single ferrule 0.2 to 2.5 mm2; 8 mm strip; 0.6 to 0.8 N m","project_candidate":"3200043 with 8 mm contact sleeve; proposed 0.7 N m setting","tool":"WIREFOX 10 + CRIMPFOX 6 + TSD-M 1,2NM; BIT SELECTION REQUIRED","open_input":"qualified approval of 0.7 N m project setting, exact bit, calibrated torque witness and received retention","state":"OPEN"}),
    ]
    pull = [
        warned({"test_id":"PULL-001","scope":"sacrificial 3200043 / Belden 3057 crimp coupons","published_basis":"Phoenix Contact 2025 tool handbook: 40 N for 1.5 mm2 / AWG 16; force held 60 s without crimp-point damage","project_sample_candidate":"3 coupons minimum; qualified sample plan approval required","force_N":"40","duration_s":"60","acceptance":"no slip, separation or crimp-point damage; force-time trace and photos retained","state":"NOT EXECUTED"}),
        warned({"test_id":"PULL-002","scope":"sacrificial 3200263 / Belden 3057 crimp coupons","published_basis":"Phoenix Contact 2025 tool handbook: 40 N for 1.5 mm2 / AWG 16; force held 60 s without crimp-point damage","project_sample_candidate":"3 coupons minimum; qualified sample plan approval required","force_N":"40","duration_s":"60","acceptance":"no slip, separation or crimp-point damage; force-time trace and photos retained","state":"NOT EXECUTED"}),
        warned({"test_id":"PULL-003","scope":"installed terminal retention","published_basis":"NO PROJECT CRITERION RELEASED","project_sample_candidate":"SELECTION REQUIRED","force_N":"SELECTION REQUIRED","duration_s":"SELECTION REQUIRED","acceptance":"manufacturer/qualified procedure required; do not apply destructive coupon load to robot devices by inference","state":"OPEN"}),
    ]
    disposition = [warned({
        "prior_hold":"R242-H02", "disposition":"PARTIALLY ADDRESSED - OPEN",
        "new_evidence":"exact two-ferrule split, exact stripping/crimp/torque-tool candidates, fourteen-endpoint schedule and 40 N / 60 s sacrificial coupon criterion",
        "remaining":"terminal-manufacturer application acceptance, exact driver bits, calibrated tools, received-lot coupons, final sample plan, installed retention/torque evidence and qualified approval"
    })]
    hold_text = [
        "Qualified acceptance of the two-ferrule application at Phoenix 3273114/2967060 and Pilz 750104 terminals",
        "Received Belden/ferrule lot dimensional fit and damage-free strip/crimp coupons",
        "Exact compatible driver bit for Pilz 750104 screw terminals and access proof",
        "Exact compatible driver bit for Phoenix 2967060 screw terminals and access proof",
        "Current calibration and as-found/as-left record for TSD-M 1,2NM candidate",
        "CRIMPFOX 6 condition/capability record and qualified operator process",
        "WIREFOX 10 blade/setting verification and strand-damage inspection",
        "Calibrated pull fixture, grips, uncertainty and qualified coupon sample plan",
        "Executed 40 N / 60 s force-time records for both ferrule formats",
        "Installed fourteen-endpoint torque/retention/photographic/continuity/isolation evidence",
        "Qualified Boston/US conductor, ferrule-collar, marker and terminal-block color disposition",
        "Formal P1.21 acceptance and signed work authorization after every applicable gate closes",
    ]
    holds = [warned({"hold_id":f"R243-H{i:02d}","hold":value,"state":"OPEN","evidence":"SELECTION REQUIRED / NOT EXECUTED"}) for i,value in enumerate(hold_text,1)]
    inspection = []
    for row in endpoint_rows:
        inspection.append(warned({"inspection_id":f"INS-{len(inspection)+1:02d}","object":row["endpoint"],"required_record":"received identity, strip dimension, ferrule identity/orientation, crimp inspection, insertion, torque if applicable, retention, wire number and photograph","state":"NOT EXECUTED","result":"","evidence_uri":""}))
    for ferrule in ("3200043", "3200263"):
        for coupon in range(1,4):
            inspection.append(warned({"inspection_id":f"INS-{len(inspection)+1:02d}","object":f"{ferrule} sacrificial coupon {coupon}","required_record":"strip measurement, pre/post photo, force-time trace to 40 N for 60 s and no-damage result","state":"NOT EXECUTED","result":"","evidence_uri":""}))
    return {
        "source-register.csv": sources, "exact-material-candidates.csv": materials,
        "tool-candidate-register.csv": tools, "endpoint-termination-schedule.csv": endpoint_rows,
        "termination-process-plan.csv": process, "torque-installation-plan.csv": torque,
        "pull-test-criteria.csv": pull, "r242-hold-disposition.csv": disposition,
        "open-holds.csv": holds, "inspection-register.csv": inspection,
    }


def diagram() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 720" role="img" aria-labelledby="title desc"><title id="title">P1.21 endpoint termination candidates</title><desc id="desc">Five XD24 and seven KWD endpoints use an eight millimeter ferrule candidate. Two Pilz endpoints use a seven millimeter ferrule candidate. All are held.</desc><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:16px}}.small{{font-size:14px}}.title{{font-size:22px;font-weight:700}}.box{{fill:#fff;stroke:#1268a8;stroke-width:3}}.gold{{fill:#fff0b3;stroke:#9b6d00;stroke-width:3}}.line{{stroke:#1268a8;stroke-width:5}}.wire{{stroke:#1c87c9;stroke-width:10}}.ferr{{fill:#d9e1e6;stroke:#082b4c;stroke-width:2}}.collar{{fill:#111}}.hold{{fill:#fff7d8;stroke:#9b6d00;stroke-width:3;stroke-dasharray:8 5}}</style><rect width="1180" height="720" fill="#f7fbfe"/><text x="34" y="42" class="title">{IDENT} · candidate process, not a wiring release</text><rect x="50" y="78" width="1080" height="550" rx="12" class="box"/><text x="80" y="120" class="title">Belden 3057 BL005 · 16 AWG</text><path d="M90 170 H310" class="wire"/><rect x="295" y="153" width="105" height="34" class="collar"/><rect x="385" y="158" width="105" height="24" class="ferr"/><text x="80" y="225">Strip 11 mm · item 3200043 · 8 mm contact sleeve</text><path d="M490 170 H600" class="line"/><rect x="600" y="125" width="220" height="90" rx="8" class="gold"/><text x="625" y="160" class="title">12 endpoints</text><text x="625" y="190">5 × XD24 + 7 × KWD</text><path d="M90 325 H310" class="wire"/><rect x="295" y="313" width="195" height="24" class="ferr"/><text x="80" y="380">Strip 7 mm · item 3200263 · 7 mm uninsulated sleeve</text><path d="M490 325 H600" class="line"/><rect x="600" y="280" width="220" height="90" rx="8" class="gold"/><text x="625" y="315" class="title">2 endpoints</text><text x="625" y="345">SR1:A1 + SRA1:A1</text><rect x="860" y="120" width="230" height="250" rx="10" class="hold"/><text x="885" y="155" class="title">Qualification chain</text><text x="885" y="195">WIREFOX 10</text><text x="885" y="225">CRIMPFOX 6 station 2</text><text x="885" y="255">40 N for 60 seconds</text><text x="885" y="285">calibrated torque tool</text><text x="885" y="315">received terminal fit</text><text x="885" y="345">qualified acceptance</text><rect x="80" y="465" width="1010" height="120" rx="10" class="hold"/><text x="105" y="505" class="title">Still open</text><text x="105" y="540">Exact bits · calibration · received coupons · installed retention · color/markers · P1.21 acceptance · work authorization</text><text x="105" y="575">No safety credit is assigned to an ordinary ferrule, tool, pull coupon, terminal or wire route.</text><text x="48" y="680" class="small">{WARNING}</text></svg>'''


def guide(records: dict[str, list[dict[str, str]]]) -> str:
    endpoint_rows = "".join(f"<tr><td>{html.escape(r['endpoint_id'])}</td><td>{html.escape(r['endpoint'])}</td><td>{html.escape(r['ferrule_candidate'])}</td><td>{html.escape(r['conductor_preparation_strip_mm'])} mm</td><td>{html.escape(r['terminal_torque_Nm'])}</td><td>{html.escape(r['state'])}</td></tr>" for r in records["endpoint-termination-schedule.csv"])
    tool_rows = "".join(f"<tr><td>{html.escape(r['designation'])}</td><td>{html.escape(r['item'])}</td><td>{html.escape(r['purpose'])}</td><td>{html.escape(r['required_before_use'])}</td></tr>" for r in records["tool-candidate-register.csv"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R243 P1.21 termination evidence</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05;max-width:22ch}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.5rem 0}}.card{{background:#fff;border:2px solid var(--blue);border-radius:.8rem;padding:1rem}}.note{{border-left:7px solid var(--gold);padding:1rem;background:#fff}}.viewer{{background:#fff;border:3px solid var(--navy);border-radius:.8rem;overflow:auto}}.viewer img{{display:block;width:100%;min-width:900px}}.controls{{display:flex;gap:.75rem;flex-wrap:wrap;margin:.8rem 0}}button{{font:inherit;font-weight:700;padding:.7rem 1rem;border:2px solid var(--navy);border-radius:.6rem;background:white;color:var(--navy)}}.table{{overflow:auto;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:1000px;background:#fff}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}@media(max-width:700px){{main{{padding:1.25rem 1rem}}}}</style></head><body><header><strong>{IDENT} · R243</strong><h1>Fourteen ends. Two honest ferrule formats.</h1><div class="warning">{WARNING}</div></header><main><div class="grid"><article class="card"><b>12 × item 3200043</b><br>8 mm insulated ferrule candidates for XD24 and KWD</article><article class="card"><b>2 × item 3200263</b><br>7 mm uninsulated candidates for Pilz A1</article><article class="card"><b>40 N · 60 s</b><br>Phoenix-published sacrificial crimp-coupon screen</article><article class="card"><b>12 open holds</b><br>No installed termination or work authority</article></div><p class="note">R242-H02 is only partially addressed. The exact ferrules and primary tools are now named, but received-lot coupons, exact torque bits, calibration, terminal application acceptance, installed retention and qualified review remain mandatory.</p><div class="controls"><button id="zi">Zoom in</button><button id="zo">Zoom out</button><button id="zr">Reset</button></div><div class="viewer"><img id="drawing" src="termination-candidate-diagram.svg" alt="P1.21 endpoint termination candidate diagram"></div><h2>Fourteen endpoint candidates</h2><div class="table"><table><thead><tr><th>ID</th><th>Endpoint</th><th>Ferrule</th><th>Conductor strip</th><th>Terminal torque N·m</th><th>State</th></tr></thead><tbody>{endpoint_rows}</tbody></table></div><h2>Exact tool candidates</h2><div class="table"><table><thead><tr><th>Tool</th><th>Item</th><th>Purpose</th><th>Before use</th></tr></thead><tbody>{tool_rows}</tbody></table></div><h2>Why the formats differ</h2><p>Pilz manual 21396-EN-23 specifies a 7 mm strip and 0.5 N·m for the 750104 screw terminals. Phoenix item 3200263 has a 7 mm uninsulated sleeve. The PTFIX and PLC relay endpoints instead receive the 8 mm contact sleeve of item 3200043. This is a held application candidate, not manufacturer or functional-safety approval.</p><h2>What remains open</h2><p>Terminal-manufacturer application acceptance, exact driver bits, calibrated tooling, strip/crimp dimensions on the received conductor, executed coupon tests, installed torque and retention, color/marker disposition, physical inspection, P1.21 acceptance and signed work authorization.</p></main><script>const im=document.querySelector('#drawing');let z=1;const set=()=>im.style.width=(z*100)+'%';document.querySelector('#zi').onclick=()=>{{z=Math.min(2.5,z+.25);set()}};document.querySelector('#zo').onclick=()=>{{z=Math.max(1,z-.25);set()}};document.querySelector('#zr').onclick=()=>{{z=1;set()}};</script></body></html>'''


def config_data() -> dict[str, list[dict[str, str]]]:
    names = ("current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv")
    cfg = {name: read(CFG_SOURCE / name) for name in names}
    cfg["current-configuration-map.csv"].append(warned({"record_id":"CFG-26","role":"P1.21 endpoint termination evidence","identifier":IDENT,"source_path":"release/hr-v0/p121-termination-p0.1/package-status.json","configuration_state":"CURRENT HELD TERMINATION CANDIDATE","release_boundary":"two exact ferrule formats and three exact tool candidates; received qualification, bits, installed evidence, P1.21 acceptance and authority open"}))
    cfg["supersession-map.csv"].append(warned({"record_id":"SUP-14","prior_identifier":"HR-V0-CONFIG-REC-P0.6","current_or_required_successor":CFG_IDENT,"disposition":"P0.6 remains immutable R242 snapshot; P0.7 adds R243/BOM-098 without promoting P1.21 or any work gate","use_authorized":"NO"}))
    cfg["bom-integration-map.csv"].append(warned({"item_id":"BOM-098","role":"P1.21 ferrule material candidates","bound_identifier":"Phoenix Contact 3200043 x1 minimum pack and 3200263 x1 minimum pack","closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO"}))
    for row in cfg["gate-impact.csv"]:
        row["evidence_added"] = IDENT
        row["remaining_evidence"] += "; R243 terminal application, bits, calibration, received coupons, installed retention/torque and qualified acceptance"
        row["gate_closed"] = "NO"
    for n, value in enumerate((
        "P1.21 exact terminal application and driver-bit acceptance",
        "Received strip/crimp/pull and calibrated torque-tool evidence",
        "Installed fourteen-endpoint retention, torque, continuity, isolation and qualified acceptance",
    ), 33):
        cfg["open-holds.csv"].append(warned({"hold_id":f"HOLD-{n:02d}","hold":value,"state":"NOT EXECUTED","closure_evidence":"signed source-backed physical and qualified record"}))
    criteria = (
        "Both ferrule identities, order quantities and endpoint counts are independently confirmed",
        "All fourteen P1.21 endpoints match the P1.21/R242 source schedule",
        "CRIMPFOX 6 and the exact ferrules are confirmed as the current Phoenix UL combination",
        "Both ferrule formats pass the accepted received-lot strip/crimp and 40 N / 60 s coupon plan",
        "All terminal fits, torque settings, bits, calibration and installed retention evidence are accepted",
        "P1.15 remains current and P1.21/R243 remain unaccepted until formal disposition",
    )
    for n, criterion in enumerate(criteria, 36):
        cfg["acceptance-matrix.csv"].append(warned({"acceptance_id":f"ACC-{n:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    return cfg


def main() -> None:
    records = package_data()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in records.items():
            write(directory / name, rows)
        text(directory / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR243 assigns exact held ferrule and primary-tool candidates to all fourteen P1.21 endpoints. Received qualification, exact bits, installed evidence, P1.21 acceptance and all work authority remain open.\n")
        text(directory / "termination-candidate-diagram.svg", diagram())
        status = {
            "identifier": IDENT, "round": "R243", "date": "2026-08-11",
            "conductor_candidates": 7, "endpoint_candidates": 14,
            "eight_mm_insulated_endpoints": 12, "seven_mm_uninsulated_endpoints": 2,
            "exact_ferrule_order_codes": ["3200043", "3200263"],
            "exact_primary_tool_candidates": ["1212034", "1212150", "1212224"],
            "crimp_coupon_force_N": 40, "crimp_coupon_duration_s": 60,
            "open_holds": 12, "blank_inspections": 20,
            "r242_h02_closed": False, "received_crimp_evidence_exists": False,
            "terminal_application_accepted": False, "driver_bits_selected": False,
            "tool_calibration_accepted": False, "installed_termination_evidence_exists": False,
            "qualified_review_complete": False, "procurement_authorized": False,
            "fabrication_authorized": False, "assembly_authorized": False,
            "connection_authorized": False, "powered_testing_authorized": False,
            "motion_authorized": False, "energization_authorized": False,
            "safety_credit": False, "warning": WARNING,
        }
        text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    text(OUT / "index.html", guide(records))
    manifest(ENG)
    manifest(OUT)

    cfg = config_data()
    for directory in (CFG_ENG, CFG_OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in cfg.items():
            write(directory / name, rows)
        text(directory / "README.md", f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR243 adds held BOM-098 and {IDENT}. P1.15 remains current; P1.21 is unaccepted; no gate or work authority closes.\n")
        status = {
            "identifier": CFG_IDENT, "round": "R243", "date": "2026-08-11",
            "current_core_electrical_identifier":"Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "unaccepted_panel_topology_candidate":"V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
            "system_bom_groups":98, "current_records":26, "supersession_records":14,
            "bom_integration_records":18, "gate_records":11, "open_holds":35,
            "acceptance_rows":41, "all_acceptance_executed":False,
            "physical_article_exists":False, "physical_test_executed":False,
            "qualified_review_complete":False, "procurement_authorized":False,
            "fabrication_authorized":False, "assembly_authorized":False,
            "connection_authorized":False, "powered_testing_authorized":False,
            "motion_authorized":False, "energization_authorized":False,
            "safety_credit":False, "warning":WARNING,
        }
        text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    cfg_sources = []
    for row in cfg["current-configuration-map.csv"]:
        path = ROOT / row["source_path"]
        cfg_sources.append(warned({"source_path":row["source_path"],"sha256":digest(path),"role":"current configuration evidence"}))
    for directory in (CFG_ENG, CFG_OUT):
        write(directory / "source-hash-register.csv", cfg_sources)
        manifest(directory)
    text(CFG_OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CFG_IDENT}</title><style>body{{margin:0;background:#f7fbfe;color:#082b4c;font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(32px,5vw,58px)}}.warning{{padding:16px;background:#fff3c4;border:3px solid #9b6d00;font-weight:800}}.card{{padding:18px;margin:18px 0;background:#fff;border:2px solid #1268a8;border-radius:12px}}</style></head><body><main><div class="warning">{WARNING}</div><h1>{CFG_IDENT}</h1><div class="card"><b>98 covered BOM groups</b><p>BOM-098 contains two exact Phoenix ferrule pack candidates on hold. Tool candidates are controlled in R243 and are not robot BOM parts.</p></div><div class="card"><b>P1.15 remains current</b><p>P1.21 and R243 remain unaccepted. No procurement, fabrication, wiring, powered test, motion or energization is authorized.</p></div></main></body></html>''')
    manifest(CFG_OUT)
    print(f"{IDENT}: 14 endpoints; 12 x 8 mm and 2 x 7 mm held candidates; 12 holds")
    print(f"{CFG_IDENT}: 98 BOM groups; P1.15 current; P1.21 unaccepted")


if __name__ == "__main__":
    main()
