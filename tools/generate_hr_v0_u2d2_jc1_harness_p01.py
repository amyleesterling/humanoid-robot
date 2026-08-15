#!/usr/bin/env python3
"""Generate R261 U2D2-to-JC1 data/reference harness candidate and config P0.25."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

from generate_hr_v0_bom_closure import classification


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-U2D2-JC1-HARNESS-P0.1"
CID = "HR-V0-CONFIG-REC-P0.25"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/harness/hr-v0-u2d2-jc1-harness-p0.1"
REL = ROOT / "release/hr-v0/u2d2-jc1-harness-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.24"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.25"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.25"
BOM = ROOT / "bom/bom.csv"
CLOSURE = ROOT / "bom/hr-v0-bom-closure.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def warned(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row | {"warning": WARNING} for row in rows]


def manifest(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path)} for path in files
    ])


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def package_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    sources = [
        {"source_id":"SRC-01","manufacturer":"ROBOTIS","document":"U2D2 e-Manual","revision_or_date":"live e-Manual accessed 2026-08-12; Type-C note current from August 2025","url":"https://emanual.robotis.com/docs/en/parts/interface/u2d2/","controlled_fact":"TTL connector pin 1 GND, pin 2 VDD, pin 3 DATA; U2D2 does not supply actuator power; maximum communication speed 6 Mbps; ground potential difference can disturb or damage communication","disposition":"authoritative U2D2 pin identity; project intentionally omits pin-2 conductor/contact"},
        {"source_id":"SRC-02","manufacturer":"JST","document":"EH connector catalog","revision_or_date":"current catalog PDF accessed 2026-08-12","url":"https://www.jst-mfg.com/product/pdf/eng/eEH.pdf","controlled_fact":"2.5 mm pitch; EHR-3 housing; SEH-001T-P0.6 contact supports AWG 30-22 and 1.0-1.9 mm insulation OD; EH rating 3 A at AWG 22 under catalog conditions","disposition":"exact connector/contact fit candidate; rating is not a released circuit limit"},
        {"source_id":"SRC-03","manufacturer":"JST","document":"Crimping Machines and Tools catalog","revision_or_date":"current tooling catalog accessed 2026-08-12","url":"https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf","controlled_fact":"SEH-001T-P0.6 is mapped to YRS-260 and YC-260R hand tools; WC-260 applies to loose-form BEH-001T-P0.6","disposition":"YRS-260 exact manufacturing-tool candidate; do not substitute loose-form contact/tool without revision"},
        {"source_id":"SRC-04","manufacturer":"JST","document":"Handling Precautions for Terminals and Connectors","revision_or_date":"current PDF accessed 2026-08-12","url":"https://www.jst-mfg.com/precaution/eP-Handling.pdf","controlled_fact":"use specified tools; confirm applicable wire and crimp height; prevent external load/resonance; do not disconnect live","disposition":"received official crimp-height, strip-length, pull and inspection instructions remain required"},
        {"source_id":"SRC-05","manufacturer":"Belden","document":"3051 product page / technical data","revision_or_date":"Rev 0.118 dated 2026-06-30; accessed 2026-08-12","url":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3051","controlled_fact":"22 AWG 7x30 tinned copper, nominal 1.6 mm PVC-insulated OD, 300 V, -40 to +105 C, 15 mm stationary minimum bend radius; BK005 and WH005 are 100 ft reels","disposition":"black GND and white DATA exact conductor candidates; installed electrical performance remains unverified"},
    ]
    pinmap = [
        {"end_a":"U2D2 TTL","cavity_a":1,"signal":"CTRL_GND","conductor":"Belden 3051 BK005 black 22 AWG","cavity_b":1,"end_b":"JC1 controller","termination":"SEH-001T-P0.6 both ends","state":"EXACT CANDIDATE HOLD"},
        {"end_a":"U2D2 TTL","cavity_a":2,"signal":"VDD","conductor":"NONE - NO WIRE AND NO CONTACT","cavity_b":2,"end_b":"JC1 controller","termination":"EMPTY both ends; JC1.2 NO_NET_NO_COPPER","state":"MANDATORY EMPTY - VERIFY PHYSICALLY"},
        {"end_a":"U2D2 TTL","cavity_a":3,"signal":"DXL_DATA","conductor":"Belden 3051 WH005 white 22 AWG","cavity_b":3,"end_b":"JC1 controller","termination":"SEH-001T-P0.6 both ends","state":"EXACT CANDIDATE HOLD"},
    ]
    hbom = [
        {"line_id":"HAR-CTRL-01","item":"connector housing","manufacturer":"JST","order_code":"EHR-3","quantity":2,"system_bom_binding":"BOM-054","release_state":"EXACT CANDIDATE HOLD"},
        {"line_id":"HAR-CTRL-02","item":"crimp contact","manufacturer":"JST","order_code":"SEH-001T-P0.6","quantity":4,"system_bom_binding":"BOM-055","release_state":"EXACT CANDIDATE HOLD"},
        {"line_id":"HAR-CTRL-03","item":"GND conductor","manufacturer":"Belden","order_code":"3051 BK005","quantity":"one length; raw cut SELECTION REQUIRED","system_bom_binding":"BOM-106 shared stock","release_state":"EXACT CANDIDATE HOLD"},
        {"line_id":"HAR-CTRL-04","item":"DATA conductor","manufacturer":"Belden","order_code":"3051 WH005","quantity":"one length; raw cut SELECTION REQUIRED","system_bom_binding":"BOM-106 shared stock","release_state":"EXACT CANDIDATE HOLD"},
        {"line_id":"HAR-CTRL-05","item":"finished harness","manufacturer":"project-controlled custom","order_code":ID,"quantity":1,"system_bom_binding":"BOM-061","release_state":"EXACT CANDIDATE HOLD - NOT RELEASED"},
        {"line_id":"HAR-CTRL-TOOL-01","item":"hand crimp tool candidate","manufacturer":"JST","order_code":"YRS-260","quantity":"manufacturing tool; not system BOM","system_bom_binding":"N/A","release_state":"EXACT TOOL CANDIDATE HOLD"},
    ]
    build = [
        {"characteristic":"finished length","candidate":"500 +/- 5 mm","definition":"unloaded harness centerline between rear wire-exit planes of the two EHR-3 housings","status":"EXACT CANDIDATE HOLD","closure":"received placement, route and service-loop fit"},
        {"characteristic":"raw cut length","candidate":"SELECTION REQUIRED","definition":"supplier/process value required to achieve accepted finished length after twist, strip, crimp and trim","status":"OPEN","closure":"official contact processing data, crimp coupon and first article"},
        {"characteristic":"pair lay","candidate":"25 +/- 5 mm per turn","definition":"project EMC candidate: twist black GND and white DATA together after cut; no shield or drain","status":"EXACT CANDIDATE HOLD","closure":"waveform/error-rate and flex/strain-relief results"},
        {"characteristic":"minimum stationary bend radius","candidate":">= 15 mm","definition":"applies to each Belden 3051 conductor; larger connector/installed requirement governs","status":"SOURCE-BOUND MINIMUM","closure":"received route and connector-exit inspection"},
        {"characteristic":"cavity 2","candidate":"empty at both ends","definition":"no wire and no crimp contact; no U2D2 VDD path","status":"MANDATORY INTERFACE RULE","closure":"100 percent visual, continuity and isolation evidence"},
        {"characteristic":"routing","candidate":"separate low-level data route; reviewed right-angle crossings only where unavoidable","definition":"do not share bundle or strain relief with actuator-current conductors","status":"INSTALLATION CANDIDATE HOLD","closure":"received panel route, clearance, support and waveform evidence"},
        {"characteristic":"labels","candidate":"HAR-CTRL at both ends; U2D2 and JC1 endpoint tags","definition":"durable readable identification; no label over latch or bend zone","status":"DESIGN CANDIDATE HOLD","closure":"selected label material and installed inspection"},
    ]
    route = [
        {"screen_id":"ROUTE-01","point":"U2D2 retained-envelope center","x_mm":471.75,"y_mm":172.70,"basis":"BP-023 envelope x 440 y 160 w 63.5 h 25.4","status":"PLANNING POINT ONLY"},
        {"screen_id":"ROUTE-02","point":"JC1 candidate point","x_mm":254.00,"y_mm":280.00,"basis":"INJ1 origin x 224 y 230 plus current 0-degree PCB JC1 local x 30 y 50","status":"PLANNING POINT ONLY"},
        {"screen_id":"ROUTE-03","point":"absolute delta","x_mm":217.75,"y_mm":107.30,"basis":"absolute coordinate difference","status":"CALCULATED"},
        {"screen_id":"ROUTE-04","point":"Manhattan center-to-center screen","x_mm":"N/A","y_mm":"N/A","basis":"217.75 + 107.30 = 325.05 mm","status":"CALCULATED - NOT A CUT LENGTH"},
        {"screen_id":"ROUTE-05","point":"candidate residual over Manhattan screen","x_mm":"N/A","y_mm":"N/A","basis":"500.00 - 325.05 = 174.95 mm","status":"SERVICE/ROUTE MARGIN SCREEN ONLY"},
    ]
    process = [
        {"step_id":"PROC-01","operation":"verify received material","required_record":"manufacturer/order code/lot, wire AWG and OD, housing/contact identity, tool identity and calibration","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-02","operation":"obtain official contact-processing limits","required_record":"applicable strip length, conductor/insulation crimp-height limits, inspection and pull criteria for SEH-001T-P0.6 plus selected wire","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-03","operation":"make and section crimp coupons","required_record":"tool/die setting, crimp heights, bellmouth/brush/insulation support, microsection or accepted equivalent, pull results","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-04","operation":"derive raw cuts and twist","required_record":"trial raw lengths, accepted lay, finished-length result and conductor damage inspection","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-05","operation":"terminate and populate","required_record":"pin-by-pin traveler; cavities 1 and 3 only; latch orientation; insertion/retention verification","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-06","operation":"unpowered electrical inspection","required_record":"continuity, isolation, pin-2 absence, resistance baseline, polarity/orientation and no-backfeed evidence","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-07","operation":"received-route fit","required_record":"bend radius, support, strain relief, separation, service loop, cover/tool clearance and as-built photos","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-08","operation":"guarded communication characterization","required_record":"accepted test authorization; waveform/error rate at selected rates and worst actuator-current transients","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
        {"step_id":"PROC-09","operation":"qualified disposition","required_record":"electrical/controls reviewer signatures and separate work-stage authorization","execution_state":"NOT EXECUTED","authority":"NOT AUTHORIZED"},
    ]
    continuity = [
        {"test_id":"ELEC-01","from":"U2D2.1","to":"JC1.1","expected":"CONTINUITY; resistance limit SELECTION REQUIRED","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-02","from":"U2D2.3","to":"JC1.3","expected":"CONTINUITY; resistance limit SELECTION REQUIRED","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-03","from":"U2D2.2","to":"JC1.2","expected":"OPEN; both cavities empty","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-04","from":"U2D2.1","to":"U2D2.2 and U2D2.3","expected":"ISOLATED; test voltage/resistance limit SELECTION REQUIRED","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-05","from":"U2D2.2","to":"U2D2.3 and all harness material","expected":"ISOLATED; no VDD conductor/contact","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-06","from":"JC1.1","to":"JC1.2 and JC1.3","expected":"ISOLATED; test voltage/resistance limit SELECTION REQUIRED","execution_state":"NOT EXECUTED","result":"OPEN"},
        {"test_id":"ELEC-07","from":"all source-off/on combinations","to":"U2D2 pin 2 and host USB","expected":"NO BACKFEED; limits and method SELECTION REQUIRED","execution_state":"NOT EXECUTED","result":"OPEN"},
    ]
    holds = [
        {"hold_id":"R261-H01","scope":"received endpoint placement and route","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"received U2D2 and star-carrier connector datums, route, clearances, support and service-loop acceptance"},
        {"hold_id":"R261-H02","scope":"finished length","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"500 +/- 5 mm candidate passes received route and does not load connectors"},
        {"hold_id":"R261-H03","scope":"raw cut and process allowance","state":"SELECTION REQUIRED","closure_evidence":"official contact-processing data, accepted crimp coupons and first-article trim/twist record"},
        {"hold_id":"R261-H04","scope":"crimp tool/process and inspection","state":"SELECTION REQUIRED","closure_evidence":"received YRS-260 identity/calibration, official crimp limits, accepted section/visual/pull evidence"},
        {"hold_id":"R261-H05","scope":"wire orderability and received identity","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"3051 BK005/WH005 received lot, construction, OD, DCR and compatibility evidence"},
        {"hold_id":"R261-H06","scope":"housing/contact received identity","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"EHR-3 and SEH-001T-P0.6 lot, dimensions, orientation and retention evidence"},
        {"hold_id":"R261-H07","scope":"continuity/isolation and pin-2 omission","state":"TEST REQUIRED","closure_evidence":"completed unpowered matrix with accepted limits and independent review"},
        {"hold_id":"R261-H08","scope":"no-backfeed","state":"TEST REQUIRED","closure_evidence":"all accepted source-off/on combinations prove no unintended U2D2 VDD/USB energy path"},
        {"hold_id":"R261-H09","scope":"signal integrity","state":"TEST REQUIRED","closure_evidence":"waveform and error-rate evidence at selected DXL rates and worst actuator-current transients"},
        {"hold_id":"R261-H10","scope":"routing separation and strain relief","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"as-built photos/measurements show accepted bend radius, separation, support and connector load"},
        {"hold_id":"R261-H11","scope":"label and as-built record","state":"SELECTION REQUIRED","closure_evidence":"selected label material, both-end identification and signed as-built pin/length record"},
        {"hold_id":"R261-H12","scope":"qualified review and work authority","state":"NOT EXECUTED","closure_evidence":"qualified electrical/controls disposition and separate written authorization for each physical stage"},
    ]
    acceptance = [
        {"acceptance_id":f"R261-ACC-{i:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}
        for i, criterion in enumerate([
            "U2D2 and JC1 cavity mapping is 1 GND, 2 empty, 3 DATA at both ends",
            "No contact, conductor or electrical path exists at cavity 2",
            "Two EHR-3 housings and four SEH-001T-P0.6 contacts match BOM-054/055",
            "Black 3051 BK005 GND and white 3051 WH005 DATA fit the published contact AWG/OD range",
            "YRS-260 is the exact current candidate for SEH-001T-P0.6 and no loose-form-contact substitution occurred",
            "Finished 500 +/- 5 mm candidate passes received route; raw cut remains process-derived",
            "The 25 +/- 5 mm pair-lay candidate and 15 mm minimum bend radius are physically verified",
            "Continuity, isolation, contact retention and pin-2 absence pass accepted limits",
            "No-backfeed testing covers all accepted source sequencing combinations",
            "Waveform/error-rate characterization passes selected rates and worst actuator-current transients",
            "As-built routing is supported and segregated from actuator-current conductors",
            "BOM-061 is exact_candidate_hold and BOM-107/108 canonical status drift is corrected",
            "No procurement, fabrication, assembly, connection, powered testing, motion, energization or safety credit is authorized",
        ], 1)
    ]
    return {
        "source-register.csv": (["source_id","manufacturer","document","revision_or_date","url","controlled_fact","disposition","warning"], warned(sources)),
        "interface-pinmap.csv": (["end_a","cavity_a","signal","conductor","cavity_b","end_b","termination","state","warning"], warned(pinmap)),
        "harness-bom.csv": (["line_id","item","manufacturer","order_code","quantity","system_bom_binding","release_state","warning"], warned(hbom)),
        "conductor-and-build-register.csv": (["characteristic","candidate","definition","status","closure","warning"], warned(build)),
        "route-screen.csv": (["screen_id","point","x_mm","y_mm","basis","status","warning"], warned(route)),
        "process-and-inspection-plan.csv": (["step_id","operation","required_record","execution_state","authority","warning"], warned(process)),
        "continuity-isolation-matrix.csv": (["test_id","from","to","expected","execution_state","result","warning"], warned(continuity)),
        "open-holds.csv": (["hold_id","scope","state","closure_evidence","warning"], warned(holds)),
        "acceptance-matrix.csv": (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], warned(acceptance)),
    }


def guide(rows_by_name: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    pinmap = rows_by_name["interface-pinmap.csv"][1]
    build = rows_by_name["conductor-and-build-register.csv"][1]
    route = rows_by_name["route-screen.csv"][1]
    holds = rows_by_name["open-holds.csv"][1]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>
:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721;--ok:#176c45}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}.state{{font-weight:850;color:var(--danger)}}.pin{{display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;margin:12px 0;padding:14px;border:2px solid var(--line);border-radius:12px}}.wire{{height:10px;background:var(--ok);min-width:120px}}.empty{{height:10px;background:repeating-linear-gradient(90deg,var(--danger),var(--danger) 8px,transparent 8px,transparent 16px)}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}a{{font-size:16px;font-weight:750;color:#075ea8}}@media(max-width:700px){{main{{padding:12px}}.pin{{grid-template-columns:1fr}}table{{min-width:820px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Two wires. Pin 2 stays empty.</h1><p>R261 turns the U2D2-to-JC1 controller link into an exact, testable harness candidate while preserving every physical and authorization hold.</p></header><main><div class='cards'><article class='card'><div class='big'>500 +/- 5 mm</div><strong>finished-length candidate</strong></article><article class='card'><div class='big'>2</div><strong>conductors only</strong></article><article class='card'><div class='big'>174.95 mm</div><strong>margin over planning Manhattan screen</strong></article><article class='card'><div class='big'>0</div><strong>released cuts or connections</strong></article></div><section><h2>Connector map</h2><div class='pin'><strong>1 · GND</strong><div class='wire'></div><strong>1 · CTRL_GND</strong></div><div class='pin'><strong>2 · VDD</strong><div class='empty'></div><strong>2 · EMPTY / NO COPPER</strong></div><div class='pin'><strong>3 · DATA</strong><div class='wire'></div><strong>3 · DXL_DATA</strong></div><p class='state'>Cavity 2 has no crimp contact and no conductor at either end. This is an intentional anti-backfeed boundary.</p></section>{table('Pin-level definition', pinmap, ['end_a','cavity_a','signal','conductor','cavity_b','end_b','termination','state'])}{table('Build characteristics', build, ['characteristic','candidate','definition','status','closure'])}{table('Route arithmetic', route, ['screen_id','point','x_mm','y_mm','basis','status'])}{table('Open evidence', holds, ['hold_id','scope','state','closure_evidence'])}<section><h2>Controlled records</h2><p><a href='source-register.csv'>Primary sources</a> · <a href='interface-pinmap.csv'>Pin map</a> · <a href='harness-bom.csv'>Harness BOM</a> · <a href='conductor-and-build-register.csv'>Build definition</a> · <a href='route-screen.csv'>Route screen</a> · <a href='process-and-inspection-plan.csv'>Process plan</a> · <a href='continuity-isolation-matrix.csv'>Electrical tests</a> · <a href='open-holds.csv'>Open holds</a> · <a href='acceptance-matrix.csv'>Acceptance</a></p></section><p class='warn'>{WARNING}</p></main></body></html>"""


def update_bom() -> None:
    rows, fields = read_csv(BOM)
    by_id = {row["item_id"]: row for row in rows}
    by_id["BOM-061"].update({
        "manufacturer":"Project-controlled custom / JST / Belden",
        "manufacturer_part_number":f"{ID}; 2 x EHR-3; 4 x SEH-001T-P0.6; 500 +/- 5 mm finished; 3051 BK005 GND + 3051 WH005 DATA; cavity 2 empty both ends",
        "baseline_status":"exact_candidate_hold",
        "selection_basis":"Exact data/reference-only candidate: U2D2 1 GND to JC1.1 CTRL_GND, 2 empty with no contact or conductor to JC1.2 NO_NET_NO_COPPER, 3 DATA to JC1.3 DXL_DATA. Finished length and twist lay are candidates only; raw cuts, official crimp limits, received route, pull/continuity/isolation/no-backfeed/waveform evidence and qualified release remain open."
    })
    by_id["BOM-106"]["selection_basis"] = "Eleven exact 22 AWG color/spool candidates cover one unique conductor color each. BK005 and WH005 are also allocated to BOM-061 without a duplicate system-BOM purchase group. Purchase quantity, process allowance, received identity/DCR, all raw cut lengths, application review and physical evidence remain open."
    write_csv(BOM, fields, sorted(rows, key=lambda row: int(row["item_id"].split("-")[1])))
    closure_fields = read_csv(CLOSURE)[1]
    write_csv(CLOSURE, closure_fields, [{"item_id": row["item_id"], **classification(row)} for row in rows])


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical", "bill_of_materials", "assembly"}:
            for value in (ID, CID):
                if value not in product.get("supporting_identifiers", []):
                    product.setdefault("supporting_identifiers", []).append(value)
            product["configuration_reconciliation"] = CID
            product["u2d2_jc1_harness"] = ID
        if product.get("domain") == "bill_of_materials":
            product["system_group_count"] = 108
            product["release_state"] = "r261_108_group_bom_u2d2_jc1_exact_harness_candidate_defined_raw_cuts_received_route_crimp_physical_qualified_and_authority_evidence_open_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_config() -> None:
    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-44","role":"U2D2-to-JC1 controller data/reference harness candidate","identifier":ID,"source_path":"release/hr-v0/u2d2-jc1-harness-p0.1/package-status.json","configuration_state":"CURRENT EXACT CANDIDATE - NO CUT, ASSEMBLY, CONNECTION OR TEST RELEASE","release_boundary":"pin map, material, tooling, finished-length and twist candidates defined; raw cut, received route, process, physical tests, qualified review and authority open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id":"SUP-37","prior_identifier":"HR-V0-CONFIG-REC-P0.24","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R261 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    integration, fields = read_csv(CFG / "bom-integration-map.csv")
    bom_rows = {row["item_id"]: row for row in read_csv(BOM)[0]}
    target = next((row for row in integration if row["item_id"] == "BOM-061"), None)
    if target is None:
        target = {"item_id":"BOM-061","role":"U2D2-to-JC1 controller harness","bound_identifier":ID,"closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO","warning":WARNING}
        integration.append(target)
    for item_id in {"BOM-061", "BOM-107", "BOM-108"}:
        row = next((item for item in integration if item["item_id"] == item_id), None)
        if row:
            row["closure_class"] = bom_rows[item_id]["baseline_status"]
            if item_id == "BOM-061":
                row["bound_identifier"] = ID
    write_csv(CFG / "bom-integration-map.csv", fields, integration)
    gates, fields = read_csv(CFG / "gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002", "EG-003", "EG-015", "EG-018", "EG-020"}:
            row["evidence_added"] += f"; {ID} exact data/reference-only harness candidate and blank physical evidence contract"
            row["remaining_evidence"] += "; received endpoint route; raw cut/crimp process; continuity/isolation/no-backfeed/waveform evidence; qualified acceptance and stage authority"
    write_csv(CFG / "gate-impact.csv", fields, gates)
    holds, fields = read_csv(CFG / "open-holds.csv")
    new_holds = package_rows()["open-holds.csv"][1]
    for index, row in enumerate(new_holds, 154):
        holds.append({"hold_id":f"HOLD-{index:03d}","hold":f"{ID}: {row['scope']}","state":row["state"],"closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    new_acc = package_rows()["acceptance-matrix.csv"][1]
    for index, row in enumerate(new_acc, 192):
        acceptance.append({"acceptance_id":f"ACC-{index:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":"R261","date":"2026-08-12","system_bom_groups":108,"current_records":44,"supersession_records":37,"bom_integration_records":len(integration),"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(acceptance),"u2d2_jc1_harness":ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR261 adds {ID}. BOM-061 is now an exact but unreleased two-conductor harness candidate and the canonical BOM closure now agrees that BOM-107/108 are exact-candidate holds. {len(holds)} holds and {len(acceptance)} unexecuted acceptances remain.\n", encoding="utf-8")
    (CFG / "index.html").write_text((REL / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    source_rows = []
    for row in current:
        path = ROOT / row["source_path"]
        source_rows.append({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], source_rows)
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def main() -> None:
    for directory in (ENG, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    update_bom()
    rows_by_name = package_rows()
    ENG.mkdir(parents=True)
    for name, (fields, rows) in rows_by_name.items():
        write_csv(ENG / name, fields, rows)
    (ENG / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR261 defines an exact but unreleased two-conductor U2D2-to-JC1 data/reference harness candidate. Cavity 2 is empty at both ends. Finished length, materials and tooling are candidates; raw cuts, received route, crimp-process limits, physical electrical evidence, waveform evidence, qualified review and authorization remain open.\n", encoding="utf-8")
    status = {
        "identifier":ID,"round":"R261","date":"2026-08-12","system_bom_groups":108,
        "source_records":5,"pinmap_rows":3,"harness_bom_rows":6,"build_characteristics":7,
        "route_screen_rows":5,"process_rows":9,"electrical_test_rows":7,"open_holds":12,"acceptance_rows":13,
        "exact_harness_candidate_defined":True,"finished_length_candidate_mm":500,"pair_lay_candidate_mm":25,
        "u2d2_vdd_contact_or_conductor_present":False,"raw_cut_length_released":False,"physical_harness_exists":False,
        "physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,
        "fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,
        "powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,
        "safety_credit":False,"warning":WARNING
    }
    (ENG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (ENG / "index.html").write_text(guide(rows_by_name), encoding="utf-8")
    manifest(ENG)
    shutil.copytree(ENG, REL)
    manifest(REL)
    update_release()
    update_config()
    print(f"Generated {ID}: exact two-conductor candidate; zero work authority")


if __name__ == "__main__":
    main()
