#!/usr/bin/env python3
"""Generate R260 observation-carrier mounting-stack correction and config P0.24."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

from generate_hr_v0_bom_closure import classification


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-OBS-MOUNT-STACK-P0.1"
CID = "HR-V0-CONFIG-REC-P0.24"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/integration/hr-v0-observation-mount-stack-p0.1"
REL = ROOT / "release/hr-v0/observation-mount-stack-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.23"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.24"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.24"
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
        {"source_id":"SRC-01","manufacturer":"Raspberry Pi","document":"HAT+ Specification","revision_or_date":"current PDF accessed 2026-08-12; Chapter 7","url":"https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf","controlled_fact":"15 mm minimum board spacing for Active Cooler; 16 mm ideal; increase for underside components","disposition":"16 mm candidate only; received no-strain stack proof required"},
        {"source_id":"SRC-02","manufacturer":"Raspberry Pi","document":"Raspberry Pi 5 mechanical drawing","revision_or_date":"portal update 2025-10-06; accessed 2026-08-12","url":"https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf","controlled_fact":"58 x 49 mm mounting pattern; dimensions are approximate/reference and physical board is required","disposition":"pattern basis only; no production acceptance from drawing"},
        {"source_id":"SRC-03","manufacturer":"Samtec","document":"ESQ-120-33-G-D product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.samtec.com/products/esq-120-33-g-d","controlled_fact":"2x20, 2.54 mm pitch, lead style 33; existing customers only and new customers must inquire for alternate","disposition":"candidate retained; procurement blocked"},
        {"source_id":"SRC-04","manufacturer":"Samtec","document":"ESQ series print F-226","revision_or_date":"Rev 16JUN26; accessed 2026-08-12","url":"https://suddendocs.samtec.com/catalog_english/esq_th.pdf","controlled_fact":"lead style 33 B dimension 16.13 mm; insertion depth 3.68-6.35 mm","disposition":"0.13 mm nominal spacer mismatch must be physically reconciled"},
        {"source_id":"SRC-05","manufacturer":"Essentra Components","document":"TNM3-6.5-10-1 product record","revision_or_date":"live listing accessed 2026-08-12","url":"https://www.essentracomponents.com/en-us/p/threaded-standoffs/tnm3-6-5-10-1","controlled_fact":"M3 female/female nylon standoff, 10 mm body, 6.5 mm diameter, 6 mm internal thread depth","disposition":"runtime exact candidate; received identity and dimensions required"},
        {"source_id":"SRC-06","manufacturer":"Essentra Components","document":"0120070000VR product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.essentracomponents.com/en-gb/p/machine-screws-pan/0120070000vr","controlled_fact":"M3 x 0.5 x 6 mm nylon pan screw; page also identifies replacement NSE-1580-M3-6","disposition":"legacy candidate retained; current orderable identity requires written confirmation"},
        {"source_id":"SRC-07","manufacturer":"Essentra Components","document":"300251659935 product record","revision_or_date":"live listing accessed 2026-08-12","url":"https://www.essentracomponents.com/en-gb/p/threaded-standoffs/300251659935","controlled_fact":"M2.5 female/female, 16 mm, 6 mm diameter, 7.5 mm internal thread, glass-filled Nylon 6","disposition":"Pi exact candidate; US availability and received dimensions required"},
        {"source_id":"SRC-08","manufacturer":"Essentra Components","document":"50M025045P006 product record","revision_or_date":"live listing accessed 2026-08-12","url":"https://www.essentracomponents.com/en-gb/p/machine-screws-pan/50m025045p006","controlled_fact":"M2.5 x 0.45 x 6 mm nylon pan-head screw, 5.0 mm head diameter, 1.6 mm head height","disposition":"Pi exact candidate; received identity and torque proof required"},
    ]
    hardware = [
        {"item_id":"MNT-OBS-01","assembly":"runtime observation carrier","manufacturer":"Essentra Components","manufacturer_part_number":"TNM3-6.5-10-1","quantity":4,"nominal_definition":"M3 F/F; 10 mm body; 6.5 mm diameter; 6 mm thread depth","state":"EXACT CANDIDATE HOLD - NOT RELEASED","remaining_evidence":"current orderability, received identity/dimensions, torque, creep, load, coating and panel proof"},
        {"item_id":"MNT-OBS-02","assembly":"runtime observation carrier","manufacturer":"Essentra Components","manufacturer_part_number":"0120070000VR / stated replacement NSE-1580-M3-6","quantity":8,"nominal_definition":"M3 x 0.5 x 6 mm nylon pan screw","state":"EXACT CANDIDATE HOLD - NOT RELEASED","remaining_evidence":"written current order-code equivalence, received identity/dimensions and installed torque/load proof"},
        {"item_id":"MNT-OBS-03","assembly":"Pi observation carrier","manufacturer":"Essentra Components","manufacturer_part_number":"300251659935","quantity":4,"nominal_definition":"M2.5 F/F; 16 mm body; 6 mm diameter; 7.5 mm thread depth; glass-filled Nylon 6","state":"EXACT CANDIDATE HOLD - NOT RELEASED","remaining_evidence":"US availability, received identity/dimensions, cooler/case fit, torque, creep and load proof"},
        {"item_id":"MNT-OBS-04","assembly":"Pi observation carrier","manufacturer":"Essentra Components","manufacturer_part_number":"50M025045P006","quantity":8,"nominal_definition":"M2.5 x 0.45 x 6 mm Nylon 6/6 pan screw","state":"EXACT CANDIDATE HOLD - NOT RELEASED","remaining_evidence":"received identity/dimensions, board stack, torque and load proof"},
    ]
    stack = [
        {"screen_id":"STK-OBS-01","assembly":"runtime","expression":"6.0 - 1.6","result_mm":4.40,"meaning":"nominal top screw engagement after candidate PCB thickness","acceptance":"SCREEN ONLY - tolerance/torque/load open"},
        {"screen_id":"STK-OBS-02","assembly":"runtime","expression":"6.0 - 2.54","result_mm":3.46,"meaning":"nominal panel-side screw engagement after candidate panel thickness","acceptance":"SCREEN ONLY - coating/tolerance/torque/load open"},
        {"screen_id":"STK-OBS-03","assembly":"runtime","expression":"4.5 - (6.5 / 2)","result_mm":1.25,"meaning":"nominal standoff-body edge margin on 120 x 90 mm board","acceptance":"SCREEN ONLY - fabricated outline/tolerance open"},
        {"screen_id":"STK-OBS-04","assembly":"Pi","expression":"6.0 - 1.6","result_mm":4.40,"meaning":"nominal carrier-side screw engagement after candidate PCB thickness","acceptance":"SCREEN ONLY - fabricated thickness/tolerance open"},
        {"screen_id":"STK-OBS-05","assembly":"Pi","expression":"3.5 - (6.0 / 2)","result_mm":0.50,"meaning":"nominal standoff-body edge margin on 65 x 56.5 mm carrier","acceptance":"SCREEN ONLY - fabricated outline/tolerance open"},
        {"screen_id":"STK-OBS-06","assembly":"Pi","expression":"16.13 - 16.00","result_mm":0.13,"meaning":"nominal Samtec lead-style-33 dimension above ideal Pi spacer height","acceptance":"MISMATCH - received no-clamp/no-board-strain fit test mandatory"},
    ]
    holes = [
        {"assembly":"runtime","hole":"MH1","local_x_mm":4.5,"local_y_mm":4.5,"candidate_panel_x_mm":437.5,"candidate_panel_y_mm":304.5,"state":"CENTER CANDIDATE - DO NOT DRILL"},
        {"assembly":"runtime","hole":"MH2","local_x_mm":115.5,"local_y_mm":4.5,"candidate_panel_x_mm":437.5,"candidate_panel_y_mm":415.5,"state":"CENTER CANDIDATE - DO NOT DRILL"},
        {"assembly":"runtime","hole":"MH3","local_x_mm":4.5,"local_y_mm":85.5,"candidate_panel_x_mm":518.5,"candidate_panel_y_mm":304.5,"state":"CENTER CANDIDATE - DO NOT DRILL"},
        {"assembly":"runtime","hole":"MH4","local_x_mm":115.5,"local_y_mm":85.5,"candidate_panel_x_mm":518.5,"candidate_panel_y_mm":415.5,"state":"CENTER CANDIDATE - DO NOT DRILL"},
        {"assembly":"Pi carrier","hole":"MH1","local_x_mm":3.5,"local_y_mm":3.5,"candidate_panel_x_mm":"N/A - mounts to received Pi stack","candidate_panel_y_mm":"N/A - mounts to received Pi stack","state":"58 x 49 mm PATTERN CANDIDATE - NO ASSEMBLY"},
        {"assembly":"Pi carrier","hole":"MH2","local_x_mm":61.5,"local_y_mm":3.5,"candidate_panel_x_mm":"N/A - mounts to received Pi stack","candidate_panel_y_mm":"N/A - mounts to received Pi stack","state":"58 x 49 mm PATTERN CANDIDATE - NO ASSEMBLY"},
        {"assembly":"Pi carrier","hole":"MH3","local_x_mm":3.5,"local_y_mm":52.5,"candidate_panel_x_mm":"N/A - mounts to received Pi stack","candidate_panel_y_mm":"N/A - mounts to received Pi stack","state":"58 x 49 mm PATTERN CANDIDATE - NO ASSEMBLY"},
        {"assembly":"Pi carrier","hole":"MH4","local_x_mm":61.5,"local_y_mm":52.5,"candidate_panel_x_mm":"N/A - mounts to received Pi stack","candidate_panel_y_mm":"N/A - mounts to received Pi stack","state":"58 x 49 mm PATTERN CANDIDATE - NO ASSEMBLY"},
    ]
    holds = [
        {"hold_id":"R260-H01","scope":"Samtec header procurement","state":"SELECTION REQUIRED","closure_evidence":"written Samtec-authorized generally orderable alternate or accepted existing-customer supply route; exact series-print match"},
        {"hold_id":"R260-H02","scope":"Pi header/spacer stack","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"received Pi, carrier, header, cooler/case and hardware; measured free stack; no clamp, bow or connector side load"},
        {"hold_id":"R260-H03","scope":"runtime screw current identity","state":"SELECTION REQUIRED","closure_evidence":"manufacturer confirmation whether 0120070000VR or NSE-1580-M3-6 is the current orderable equivalent"},
        {"hold_id":"R260-H04","scope":"mounting material and electrical boundary","state":"QUALIFIED REVIEW REQUIRED","closure_evidence":"insulation/bonding disposition; conductive Harwin alternative remains rejected unless bonding is formally resolved"},
        {"hold_id":"R260-H05","scope":"received geometry and tolerances","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"received boards, panel, Pi and hardware measured; drawing-reference limitations reconciled"},
        {"hold_id":"R260-H06","scope":"torque, creep, load and thermal behavior","state":"TEST REQUIRED","closure_evidence":"selected torque limits; calibrated tool; static/load/vibration/thermal/creep results and qualified disposition"},
        {"hold_id":"R260-H07","scope":"runtime panel holes and placement","state":"DESIGN REQUIRED","closure_evidence":"provider drawing, tolerances, diameter, deburr/coating process, physical overlay/connector sweep and separate work authorization"},
        {"hold_id":"R260-H08","scope":"field and compute harness routes/cuts","state":"SELECTION REQUIRED","closure_evidence":"received placement, exact endpoints/duct/case, cut and preparation schedules, separation, continuity/pull evidence"},
        {"hold_id":"R260-H09","scope":"qualified review and authority","state":"NOT EXECUTED","closure_evidence":"qualified electrical/mechanical/functional-safety review and separate written stage authorization"},
    ]
    fit = [
        {"test_id":f"R260-FIT-{i:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","operator":"","reviewer":""}
        for i, criterion in enumerate([
            "Record received manufacturer, part, lot and revision for every hardware item",
            "Measure both board outlines, thicknesses and all mounting-hole diameters/centers",
            "Measure runtime panel/flange/rear clearance and reconcile all four center candidates",
            "Mock up runtime carrier without marking or drilling metal and sweep connectors/wires/tools/cover",
            "Measure Pi/header/carrier/spacer free stack without fastener clamp",
            "Confirm no Pi or carrier bow, connector side load, incomplete insertion or cooler/case interference",
            "Establish qualified torque limits and verify installed engagement without bottoming",
            "Execute retained-load, vibration, thermal and creep checks under an accepted protocol",
            "Release exact harness routes/cuts only after received placements are frozen",
            "Obtain separate qualified disposition and written work-stage authorization",
        ], 1)
    ]
    acceptance = [
        {"acceptance_id":f"R260-ACC-{i:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}
        for i, criterion in enumerate([
            "BOM-107 identifies four TNM3-6.5-10-1 candidates and eight current-equivalent M3 x 6 screw candidates",
            "BOM-108 identifies four 300251659935 and eight 50M025045P006 candidates",
            "BOM-104 records the Samtec existing-customer restriction and alternate inquiry requirement",
            "Runtime board four-hole geometry and candidate panel centers agree with controlled sources",
            "Pi carrier and Pi reference patterns agree nominally at 58 x 49 mm",
            "Runtime nominal thread-engagement and edge-margin arithmetic is reproduced",
            "Pi nominal thread-engagement, edge-margin and 0.13 mm stack mismatch arithmetic is reproduced",
            "All panel coordinates remain DO NOT DRILL and all Pi assembly remains unperformed",
            "All physical fit, torque, load, thermal, creep, route and cut results remain open",
            "No procurement, fabrication, assembly, connection, powered test, motion, energization or safety credit is authorized",
            "Independent qualified review records dispositions without upgrading unsupported evidence",
            "A separate signed stage authorization is required after every applicable acceptance closes",
        ], 1)
    ]
    return {
        "source-register.csv": (["source_id","manufacturer","document","revision_or_date","url","controlled_fact","disposition","warning"], warned(sources)),
        "hardware-candidate-register.csv": (["item_id","assembly","manufacturer","manufacturer_part_number","quantity","nominal_definition","state","remaining_evidence","warning"], warned(hardware)),
        "stack-calculation.csv": (["screen_id","assembly","expression","result_mm","meaning","acceptance","warning"], warned(stack)),
        "hole-coordinate-register.csv": (["assembly","hole","local_x_mm","local_y_mm","candidate_panel_x_mm","candidate_panel_y_mm","state","warning"], warned(holes)),
        "unresolved-selections.csv": (["hold_id","scope","state","closure_evidence","warning"], warned(holds)),
        "fit-and-acceptance-form.csv": (["test_id","criterion","execution_state","result","evidence_uri","operator","reviewer","warning"], warned(fit)),
        "acceptance-matrix.csv": (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], warned(acceptance)),
    }


def guide(rows_by_name: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    hw = rows_by_name["hardware-candidate-register.csv"][1]
    stack = rows_by_name["stack-calculation.csv"][1]
    holes = rows_by_name["hole-coordinate-register.csv"][1]
    holds = rows_by_name["unresolved-selections.csv"][1]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>
:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}.state{{font-weight:850;color:var(--danger)}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}a{{font-size:16px;font-weight:750;color:#075ea8}}button{{font:inherit;font-weight:750;padding:10px 14px;border:2px solid var(--blue);background:white;border-radius:9px}}button.active{{background:var(--gold)}}.view{{display:none}}.view.active{{display:block}}@media(max-width:700px){{main{{padding:12px}}table{{min-width:820px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Observation mounting stack</h1><p>R260 defines exact, unreleased mounting candidates and exposes the physical evidence still required before metal, assembly or wiring.</p></header><main><div class='cards'><article class='card'><div class='big'>2</div><strong>mounting interfaces advanced</strong></article><article class='card'><div class='big'>20</div><strong>candidate hardware pieces</strong></article><article class='card'><div class='big'>0.13 mm</div><strong>nominal Pi stack mismatch</strong></article><article class='card'><div class='big'>0</div><strong>released purchases or holes</strong></article></div><section><h2>Choose a stack</h2><p><button class='active' data-view='runtime'>Runtime carrier</button> <button data-view='pi'>Pi carrier</button></p><div id='runtime' class='view active'><p><strong>Runtime:</strong> four 10 mm M3 nylon standoffs and eight M3 x 6 nylon screws. Nominal engagement screens pass, but current screw identity, tolerances, torque, creep, load, coating and received fit remain open.</p></div><div id='pi' class='view'><p><strong>Pi:</strong> four 16 mm M2.5 glass-filled-nylon standoffs and eight M2.5 x 6 nylon screws. The Samtec header dimension is nominally 0.13 mm above the ideal spacer height; fasteners must not be used to force the boards together.</p></div><p class='state'>Exact candidate is not the same thing as selected, received, accepted or released.</p></section>{table('Hardware candidates', hw, ['item_id','assembly','manufacturer_part_number','quantity','nominal_definition','state','remaining_evidence'])}{table('Nominal stack calculations', stack, ['screen_id','assembly','expression','result_mm','meaning','acceptance'])}{table('Mounting geometry', holes, ['assembly','hole','local_x_mm','local_y_mm','candidate_panel_x_mm','candidate_panel_y_mm','state'])}{table('Open evidence', holds, ['hold_id','scope','state','closure_evidence'])}<section><h2>Controlled records</h2><p><a href='source-register.csv'>Primary sources</a> · <a href='hardware-candidate-register.csv'>Hardware</a> · <a href='stack-calculation.csv'>Calculations</a> · <a href='hole-coordinate-register.csv'>Hole centers</a> · <a href='unresolved-selections.csv'>Open evidence</a> · <a href='fit-and-acceptance-form.csv'>Fit form</a> · <a href='acceptance-matrix.csv'>Acceptance</a></p></section><p class='warn'>{WARNING}</p></main><script>const bs=[...document.querySelectorAll('button[data-view]')],vs=[...document.querySelectorAll('.view')];bs.forEach(b=>b.onclick=()=>{{bs.forEach(x=>x.classList.toggle('active',x===b));vs.forEach(x=>x.classList.toggle('active',x.id===b.dataset.view))}});</script></body></html>"""


def update_bom() -> None:
    rows, fields = read_csv(BOM)
    by_id = {row["item_id"]: row for row in rows}
    by_id["BOM-104"].update({
        "selection_basis":"One exact 2x20 elevated socket candidate. Samtec currently restricts the part to existing customers and directs new customers to inquire for an alternate. Received Pi/header fit, land/drill DFM, 16.13 mm header versus 16.00 mm spacer reconciliation, mechanical support and physical acceptance remain open."
    })
    by_id["BOM-107"].update({
        "manufacturer":"Essentra Components",
        "manufacturer_part_number":"4 x TNM3-6.5-10-1; 8 x 0120070000VR or manufacturer-confirmed replacement NSE-1580-M3-6",
        "baseline_status":"exact_candidate_hold",
        "selection_basis":"Exact four-site M3 nylon candidate stack. Current screw order-code equivalence, received identity/dimensions, tolerances, torque, creep, load, coating interface, panel-hole process and physical proof remain open. No drilling or procurement release."
    })
    by_id["BOM-108"].update({
        "manufacturer":"Essentra Components",
        "manufacturer_part_number":"4 x 300251659935; 8 x 50M025045P006",
        "baseline_status":"exact_candidate_hold",
        "selection_basis":"Exact four-site M2.5 nylon candidate stack. US availability, received dimensions, 0.13 mm nominal header/spacer mismatch, Pi/cooler/case fit, torque, creep, load and physical proof remain open. No assembly or procurement release."
    })
    write_csv(BOM, fields, sorted(rows, key=lambda row: int(row["item_id"].split("-")[1])))
    _, closure_fields = read_csv(CLOSURE)
    write_csv(CLOSURE, closure_fields, [{"item_id": row["item_id"], **classification(row)} for row in rows])


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical", "bill_of_materials", "assembly"}:
            for value in (ID, CID):
                if value not in product.get("supporting_identifiers", []):
                    product.setdefault("supporting_identifiers", []).append(value)
            product["configuration_reconciliation"] = CID
            product["observation_mount_stack"] = ID
        if product.get("domain") == "bill_of_materials":
            product["system_group_count"] = 108
            product["release_state"] = "r260_108_group_bom_observation_mounting_exact_candidates_defined_procurement_received_fit_routes_physical_qualified_and_authority_evidence_open_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_config() -> None:
    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-43","role":"Observation carrier mounting-stack candidate definition","identifier":ID,"source_path":"release/hr-v0/observation-mount-stack-p0.1/package-status.json","configuration_state":"CURRENT EXACT CANDIDATES - NO PROCUREMENT OR PHYSICAL RELEASE","release_boundary":"two mounting interfaces advanced to exact-candidate hold; Samtec availability, received fit, routes, cuts, tests and authority open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id":"SUP-36","prior_identifier":"HR-V0-CONFIG-REC-P0.23","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R260 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    integration, fields = read_csv(CFG / "bom-integration-map.csv")
    for row in integration:
        if row["item_id"] in {"BOM-104","BOM-107","BOM-108"}:
            source = next(item for item in read_csv(BOM)[0] if item["item_id"] == row["item_id"])
            row["bound_identifier"] = source["manufacturer_part_number"]
            row["closure_class"] = source["baseline_status"]
    write_csv(CFG / "bom-integration-map.csv", fields, integration)
    gates, fields = read_csv(CFG / "gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-003","EG-010","EG-015"}:
            row["evidence_added"] += f"; {ID} exact mounting candidates and nominal stack screens"
            row["remaining_evidence"] += "; current orderability, received no-strain fit, torque/load/thermal/creep, drilling, routes/cuts and qualified acceptance"
    write_csv(CFG / "gate-impact.csv", fields, gates)
    holds, fields = read_csv(CFG / "open-holds.csv")
    for row in holds:
        if row["hold_id"] == "HOLD-15":
            row.update({"hold":"Observation assemblies, quantities and exact mounting candidates are integrated through BOM-108; procurement, received fit, cuts/routes and physical closure remain","state":"PARTIALLY ADDRESSED - OPEN","closure_evidence":f"{ID}; current orderability; received no-strain fit; released drilling/cut/termination schedules; torque/load/thermal/creep evidence; qualified acceptance"})
    new_holds = package_rows()["unresolved-selections.csv"][1]
    for index, row in enumerate(new_holds, 145):
        holds.append({"hold_id":f"HOLD-{index:03d}","hold":f"{ID}: {row['scope']}","state":row["state"],"closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    new_acc = package_rows()["acceptance-matrix.csv"][1]
    for index, row in enumerate(new_acc, 180):
        acceptance.append({"acceptance_id":f"ACC-{index:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":"R260","date":"2026-08-12","system_bom_groups":108,"current_records":43,"supersession_records":36,"bom_integration_records":28,"gate_records":11,"open_holds":153,"acceptance_rows":191,"observation_mount_stack":ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR260 adds {ID}. BOM-107 and BOM-108 now contain exact but unreleased candidate hardware; BOM-104 records restricted Samtec availability and the nominal 0.13 mm stack mismatch. 153 holds and 191 unexecuted acceptances remain.\n", encoding="utf-8")
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
    readme = f"# {ID}\n\n> **{WARNING}**\n\nR260 defines exact candidate mounting stacks for the runtime and Raspberry Pi observation carriers. It records manufacturer documentation, nominal calculations, candidate hole centers and an unexecuted physical-fit protocol. The candidates are not released; received fit, orderability, torque, creep, load, thermal, drilling, routing, cuts and qualified acceptance remain open.\n"
    (ENG / "README.md").write_text(readme, encoding="utf-8")
    status = {
        "identifier":ID,"round":"R260","date":"2026-08-12","system_bom_groups":108,
        "mounting_interfaces_advanced":2,"exact_candidate_hardware_pieces":24,"source_records":8,
        "stack_screens":6,"mounting_geometry_rows":8,"open_holds":9,"fit_rows":10,"acceptance_rows":12,
        "exact_mounting_hardware_candidates_defined":True,"mounting_hardware_selected":False,
        "samtec_general_orderability_confirmed":False,"mounting_stack_physically_accepted":False,
        "panel_holes_released":False,"cut_lengths_selected":False,"physical_article_exists":False,
        "physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,
        "fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,
        "powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,
        "safety_credit":False,"warning":WARNING
    }
    (ENG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    page = guide(rows_by_name).replace("<div class='big'>20</div><strong>candidate hardware pieces", "<div class='big'>24</div><strong>candidate hardware pieces")
    (ENG / "index.html").write_text(page, encoding="utf-8")
    manifest(ENG)
    shutil.copytree(ENG, REL)
    manifest(REL)
    update_release()
    update_config()
    print(f"Generated {ID}: two exact-candidate mounting interfaces; zero work authority")


if __name__ == "__main__":
    main()
