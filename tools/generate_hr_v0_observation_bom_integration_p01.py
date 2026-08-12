#!/usr/bin/env python3
"""Generate R259 observation BOM integration and configuration P0.23."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

from generate_hr_v0_bom_closure import classification


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-OBS-BOM-INTEGRATION-P0.1"
CID = "HR-V0-CONFIG-REC-P0.23"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "bom/hr-v0-observation-bom-integration-p0.1"
REL = ROOT / "release/hr-v0/observation-bom-integration-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.22"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.23"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.23"
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
    write_csv(
        directory / "file-manifest.csv",
        ["path", "bytes", "sha256"],
        [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path)} for path in files],
    )


def observation_rows() -> list[dict[str, object]]:
    return [
        {"item_id":"BOM-099","subsystem":"diagnostic_observation","manufacturer":"Custom PCB / provider SELECTION REQUIRED","manufacturer_part_number":"HR-V0-RUNTIME-OBS-CARRIER-P0.5 PCBA; 49 mounted components; four M3 mounting interfaces","quantity":1,"baseline_status":"exact_candidate_hold","selection_basis":"One source-bound diagnostic receiver PCBA. Native source, connector map and population are exact; provider, process, stackup, DFM, first article, physical tests and qualified review remain open. Zero safety credit."},
        {"item_id":"BOM-100","subsystem":"diagnostic_observation","manufacturer":"Custom PCB / provider SELECTION REQUIRED","manufacturer_part_number":"HR-V0-PI-OBS-CARRIER-P0.1 PCBA; two mounted connectors; four M2.5 mounting interfaces","quantity":1,"baseline_status":"exact_candidate_hold","selection_basis":"One source-bound passive Pi observation carrier. Provider, process, received Pi/header geometry, stack, physical tests and qualified review remain open. Zero safety credit."},
        {"item_id":"BOM-101","subsystem":"diagnostic_observation_harness","manufacturer":"Custom harness / selection required","manufacturer_part_number":"HR-V0-OBSERVATION-FIELD-HARNESS-P0.1; five point-to-point conductors","quantity":1,"baseline_status":"design_required","selection_basis":"One field harness assembly with five exact net/color candidates. Every cut length, installed route, support, preparation, pull/continuity result and physical acceptance remains SELECTION REQUIRED."},
        {"item_id":"BOM-102","subsystem":"diagnostic_observation_harness","manufacturer":"Custom harness / selection required","manufacturer_part_number":"HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1; six point-to-point conductors","quantity":1,"baseline_status":"design_required","selection_basis":"One compute harness assembly with six exact net/color candidates. Every cut length, installed route, separation, preparation, pull/continuity result and physical acceptance remains SELECTION REQUIRED."},
        {"item_id":"BOM-103","subsystem":"diagnostic_observation_pcba_component","manufacturer":"Phoenix Contact","manufacturer_part_number":"MKDS 1/6-3,5; item 1751280; JFIELD1 and JLOGIC1","quantity":2,"baseline_status":"exact_candidate_hold","selection_basis":"Two exact six-position runtime-carrier terminal candidates. Land, orientation, conductor preparation, torque, received identity, DFM and installed evidence remain open."},
        {"item_id":"BOM-104","subsystem":"diagnostic_observation_pcba_component","manufacturer":"Samtec","manufacturer_part_number":"ESQ-120-33-G-D; JPI1","quantity":1,"baseline_status":"exact_candidate_hold","selection_basis":"One exact 2x20 elevated socket candidate. Received Pi/header fit, land/drill DFM, stack height, mechanical support and physical acceptance remain open."},
        {"item_id":"BOM-105","subsystem":"diagnostic_observation_pcba_component","manufacturer":"Phoenix Contact","manufacturer_part_number":"MKDS 1/6-3,5; item 1751280; JOBS1","quantity":1,"baseline_status":"exact_candidate_hold","selection_basis":"One exact six-position Pi-carrier terminal candidate. Land, orientation, conductor preparation, torque, received identity, DFM and installed evidence remain open."},
        {"item_id":"BOM-106","subsystem":"diagnostic_observation_harness_material","manufacturer":"Belden","manufacturer_part_number":"3051 WB005, WO005, WV005, WY005, WU005, RD005, BK005, BL005, OR005, VI005 and WH005","quantity":11,"baseline_status":"exact_candidate_hold","selection_basis":"Eleven exact 22 AWG color/spool candidates cover one unique conductor color each. Purchase quantity, process allowance, received identity/DCR, cut lengths, application review and physical evidence remain open."},
        {"item_id":"BOM-107","subsystem":"diagnostic_observation_mounting","manufacturer":"Selection required","manufacturer_part_number":"Runtime observation carrier four-site M3 standoff/fastener/panel interface set","quantity":1,"baseline_status":"design_required","selection_basis":"One four-site mounting set is required by the controlled 3.2 mm board holes. Exact standoffs, screws, panel hardware, material, height, thread engagement, torque, coating interface and proof remain SELECTION REQUIRED."},
        {"item_id":"BOM-108","subsystem":"diagnostic_observation_mounting","manufacturer":"Selection required","manufacturer_part_number":"Pi observation carrier four-site M2.5 stack/fastener interface set","quantity":1,"baseline_status":"design_required","selection_basis":"One four-site stack set is required by the controlled 2.7 mm board holes. Exact spacers/standoffs, screws, stack height, thread engagement, torque, case/cooler clearance and physical fit remain SELECTION REQUIRED."},
    ]


def update_system_bom() -> None:
    new_rows = observation_rows()
    rows, fields = read_csv(BOM)
    rows = [row for row in rows if row["item_id"] not in {item["item_id"] for item in new_rows}]
    rows.extend(new_rows)
    rows.sort(key=lambda row: int(str(row["item_id"]).split("-")[1]))
    write_csv(BOM, fields, rows)

    _, closure_fields = read_csv(CLOSURE)
    closure = [{"item_id": row["item_id"], **classification(row)} for row in rows]
    write_csv(CLOSURE, closure_fields, closure)


def update_release_metadata() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    products = data["current_products"]
    electrical = next(row for row in products if row.get("domain") == "electrical")
    for value in (ID, CID):
        if value not in electrical["supporting_identifiers"]:
            electrical["supporting_identifiers"].append(value)
    electrical["configuration_reconciliation"] = CID
    electrical["observation_bom_integration"] = ID
    bom = next(row for row in products if row.get("domain") == "bill_of_materials")
    for value in (ID, CID):
        if value not in bom["supporting_identifiers"]:
            bom["supporting_identifiers"].append(value)
    bom["release_state"] = "r259_108_group_bom_with_source_bound_observation_assemblies_and_quantities_mounting_cut_physical_qualified_and_authority_evidence_open_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    bom["system_group_count"] = 108
    bom["configuration_reconciliation"] = CID
    bom["observation_bom_integration"] = ID
    assembly = next(row for row in products if row.get("domain") == "assembly")
    if CID not in assembly["supporting_identifiers"]:
        assembly["supporting_identifiers"].append(CID)
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(items: list[dict[str, object]], assemblies: list[dict[str, object]], mounting: list[dict[str, object]], holds: list[dict[str, object]]) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin:24px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}.state{{font-weight:850;color:var(--danger)}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}a{{font-size:16px;font-weight:750;color:#075ea8}}@media(max-width:700px){{main{{padding:12px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Observation BOM integration</h1><p>R259 binds the diagnostic receiver, Pi carrier, two harnesses, constituent connectors, conductor candidates and mounting interfaces into the system BOM.</p></header><main><div class='cards'><article class='card'><div class='big'>108</div><strong>system BOM groups</strong></article><article class='card'><div class='big'>10</div><strong>new observation groups</strong></article><article class='card'><div class='big'>11</div><strong>controlled conductors</strong></article><article class='card'><div class='big'>0</div><strong>released purchases or work steps</strong></article></div><section><h2>What changed</h2><p>The system BOM now names one runtime receiver PCBA, one Pi carrier PCBA, one five-conductor field harness, one six-conductor compute harness, three exact Phoenix terminal candidates, one exact Samtec header candidate, eleven exact Belden color/spool candidates, and two four-site mounting-interface groups.</p><p class='state'>Exact mounting hardware, cable cuts, processes, received articles, DFM, physical tests and qualified acceptance remain open.</p></section>{table('BOM bindings',items,['item_id','role','bound_identifier','quantity','closure_class','remaining_evidence'])}{table('Assembly quantities',assemblies,['assembly_id','identifier','quantity','constituent_scope','physical_state'])}{table('Mounting interfaces',mounting,['interface_id','assembly_id','site_count','nominal_hole','hardware_identity','state'])}{table('Open selection and evidence holds',holds,['hold_id','scope','evidence_required','state'])}<section><h2>Controlled records</h2><p><a href='item-binding.csv'>Item binding</a> · <a href='assembly-quantity-register.csv'>Assembly quantities</a> · <a href='mounting-interface-register.csv'>Mounting interfaces</a> · <a href='conductor-candidate-register.csv'>Conductor candidates</a> · <a href='acceptance-matrix.csv'>Acceptance matrix</a></p></section><p class='warn'>{WARNING}</p></main></body></html>"""


def main() -> None:
    for directory in (OUT, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    update_system_bom()
    update_release_metadata()
    OUT.mkdir(parents=True)

    system_items = {row["item_id"]: row for row in read_csv(BOM)[0]}
    bindings = []
    roles = {
        "BOM-099":"runtime observation carrier PCBA", "BOM-100":"Pi observation carrier PCBA",
        "BOM-101":"field observation harness", "BOM-102":"compute observation harness",
        "BOM-103":"runtime carrier terminal pair", "BOM-104":"Pi stacking header",
        "BOM-105":"Pi carrier terminal", "BOM-106":"observation conductor stock candidates",
        "BOM-107":"runtime carrier mounting interface set", "BOM-108":"Pi carrier mounting interface set",
    }
    remaining = {
        "BOM-099":"provider/process/DFM/FAI/received/physical/qualified evidence",
        "BOM-100":"provider/process/DFM/received Pi fit/physical/qualified evidence",
        "BOM-101":"five exact cut lengths/routes/preparation/continuity/pull evidence",
        "BOM-102":"six exact cut lengths/routes/separation/preparation/continuity/pull evidence",
        "BOM-103":"DFM, received identity, torque and installed evidence",
        "BOM-104":"received fit, stack, land/drill DFM and support evidence",
        "BOM-105":"DFM, received identity, torque and installed evidence",
        "BOM-106":"procurement quantity, received identity/DCR, cuts and application evidence",
        "BOM-107":"exact standoffs, screws, panel hardware, height, torque and proof",
        "BOM-108":"exact spacers/standoffs, screws, stack height, torque and fit",
    }
    for item_id in roles:
        row = system_items[item_id]
        bindings.append({"item_id":item_id,"role":roles[item_id],"bound_identifier":row["manufacturer_part_number"],"quantity":row["quantity"],"closure_class":row["baseline_status"],"remaining_evidence":remaining[item_id]})
    write_csv(OUT / "item-binding.csv", list(bindings[0]) + ["warning"], warned(bindings))

    assemblies = [
        {"assembly_id":"R259-ASSY-01","identifier":"HR-V0-RUNTIME-OBS-CARRIER-P0.5 PCBA","quantity":1,"constituent_scope":"49 mounted components; two six-position terminals; four M3 interfaces","physical_state":"NO ARTICLE / NOT RELEASED"},
        {"assembly_id":"R259-ASSY-02","identifier":"HR-V0-PI-OBS-CARRIER-P0.1 PCBA","quantity":1,"constituent_scope":"one 2x20 header; one six-position terminal; four M2.5 interfaces","physical_state":"NO ARTICLE / NOT RELEASED"},
        {"assembly_id":"R259-ASSY-03","identifier":"HR-V0-OBSERVATION-FIELD-HARNESS-P0.1","quantity":1,"constituent_scope":"five point-to-point 22 AWG conductors","physical_state":"NO ARTICLE / CUTS SELECTION REQUIRED"},
        {"assembly_id":"R259-ASSY-04","identifier":"HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1","quantity":1,"constituent_scope":"six point-to-point 22 AWG conductors","physical_state":"NO ARTICLE / CUTS SELECTION REQUIRED"},
    ]
    write_csv(OUT / "assembly-quantity-register.csv", list(assemblies[0]) + ["warning"], warned(assemblies))
    mounting = [
        {"interface_id":"R259-MNT-01","assembly_id":"R259-ASSY-01","site_count":4,"nominal_hole":"3.2 mm clearance / project M3 interface","hardware_identity":"SELECTION REQUIRED","state":"DESIGN REQUIRED / NOT RELEASED"},
        {"interface_id":"R259-MNT-02","assembly_id":"R259-ASSY-02","site_count":4,"nominal_hole":"2.7 mm clearance / project M2.5 interface","hardware_identity":"SELECTION REQUIRED","state":"DESIGN REQUIRED / NOT RELEASED"},
    ]
    write_csv(OUT / "mounting-interface-register.csv", list(mounting[0]) + ["warning"], warned(mounting))

    conductor_codes = ["3051 WB005","3051 WO005","3051 WV005","3051 WY005","3051 WU005","3051 RD005","3051 BK005","3051 BL005","3051 OR005","3051 VI005","3051 WH005"]
    conductors = [{"conductor_id":f"R259-COND-{index:02d}","manufacturer":"Belden","order_code":code,"application_quantity":1,"procurement_quantity":"SELECTION REQUIRED","cut_length":"SELECTION REQUIRED","state":"EXACT CANDIDATE / NOT RELEASED"} for index, code in enumerate(conductor_codes, 1)]
    write_csv(OUT / "conductor-candidate-register.csv", list(conductors[0]) + ["warning"], warned(conductors))

    holds = [
        {"hold_id":"R259-H01","scope":"runtime carrier fabrication and assembly","evidence_required":"provider/process/stackup/DFM/XYRS/first article and received inspection","state":"OPEN"},
        {"hold_id":"R259-H02","scope":"Pi carrier fabrication and assembly","evidence_required":"provider/process/DFM/header land/stack/first article and received inspection","state":"OPEN"},
        {"hold_id":"R259-H03","scope":"runtime mounting hardware","evidence_required":"exact four-site hardware identities, stack, panel interface, torque and proof","state":"DESIGN REQUIRED"},
        {"hold_id":"R259-H04","scope":"Pi mounting hardware","evidence_required":"exact four-site hardware identities, stack, cooler/case clearance, torque and fit","state":"DESIGN REQUIRED"},
        {"hold_id":"R259-H05","scope":"field harness","evidence_required":"five cut lengths, routes, support, preparations, labels and physical results","state":"SELECTION REQUIRED"},
        {"hold_id":"R259-H06","scope":"compute harness","evidence_required":"six cut lengths, routes, separation, support, preparations, labels and physical results","state":"SELECTION REQUIRED"},
        {"hold_id":"R259-H07","scope":"conductor material allocation","evidence_required":"make/buy strategy, actual procurement quantities, received identity/DCR and process allowance","state":"SELECTION REQUIRED"},
        {"hold_id":"R259-H08","scope":"qualified review and authority","evidence_required":"qualified electrical/mechanical/functional-safety dispositions and separate written stage authority","state":"NOT EXECUTED"},
    ]
    write_csv(OUT / "selection-holds.csv", list(holds[0]) + ["warning"], warned(holds))
    criteria = [
        "BOM-099 through BOM-108 exist exactly once in the hierarchical BOM and closure register",
        "Runtime PCBA quantity and 49-component/four-hole source scope agree",
        "Pi PCBA quantity and two-component/four-hole source scope agree",
        "Runtime and Pi terminal allocations total three item 1751280 candidates without duplication",
        "One Samtec ESQ-120-33-G-D candidate is allocated only to JPI1",
        "Field harness has one assembly and five conductor identities",
        "Compute harness has one assembly and six conductor identities",
        "Eleven distinct Belden color/order-code candidates cover all eleven conductor rows",
        "Both four-site mounting interfaces remain unresolved and unreleased",
        "No procurement, fabrication, assembly, connection, powered testing, motion, energization or safety credit is authorized",
    ]
    acceptance = [{"acceptance_id":f"R259-ACC-{index:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for index, criterion in enumerate(criteria, 1)]
    write_csv(OUT / "acceptance-matrix.csv", list(acceptance[0]) + ["warning"], warned(acceptance))

    source_paths = [
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/hr-v0-runtime-observation-carrier-p0.5.kicad_pro",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/bom.csv",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/validation/pcb-summary.json",
        "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5/selection-holds.csv",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/hr-v0-pi-observation-carrier-p0.1.kicad_pro",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/bom.csv",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/validation/validation-summary.json",
        "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/selection-holds.csv",
        "electrical/harness/hr-v0-observation-field-harness-p0.1/package-status.json",
        "electrical/harness/hr-v0-observation-field-harness-p0.1/harness-bom.csv",
        "electrical/harness/hr-v0-observation-compute-harness-p0.1/package-status.json",
        "electrical/harness/hr-v0-observation-compute-harness-p0.1/harness-bom.csv",
        "bom/bom.csv", "bom/hr-v0-bom-closure.csv", "release/hr-v0/release-candidate.json",
    ]
    sources = [{"source_id":f"R259-SRC-{index:02d}","path":path,"sha256":sha(ROOT / path),"role":"controlled observation BOM source"} for index, path in enumerate(source_paths, 1)]
    write_csv(OUT / "source-register.csv", list(sources[0]) + ["warning"], warned(sources))
    status = {"identifier":ID,"round":"R259","date":"2026-08-12","system_bom_groups":108,"new_bom_groups":10,"assembly_rows":4,"mounting_interfaces":2,"conductor_candidates":11,"selection_holds":8,"acceptance_rows":10,"hierarchical_bom_integrated":True,"exact_mounting_hardware_selected":False,"cut_lengths_selected":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR259 adds BOM-099 through BOM-108 and binds four observation assemblies, exact connector/conductor candidates and two unresolved mounting-interface sets. Exact hardware, cable cuts, provider/process evidence, received articles, tests and qualified acceptance remain open.\n", encoding="utf-8")
    (OUT / "index.html").write_text(guide(bindings, assemblies, mounting, holds), encoding="utf-8")
    manifest(OUT)
    shutil.copytree(OUT, REL)
    manifest(REL)

    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    for row in current:
        if row["record_id"] == "CFG-07":
            row["release_boundary"] = "108 groups through BOM-108; observation assemblies integrated; not a procurement release"
    current.append({"record_id":"CFG-42","role":"Observation assemblies and hierarchical BOM integration","identifier":ID,"source_path":"release/hr-v0/observation-bom-integration-p0.1/package-status.json","configuration_state":"CURRENT CONTROLLED BOM INTEGRATION - NO PHYSICAL RELEASE","release_boundary":"ten system groups added; mounting hardware, cable cuts, DFM, physical and qualified evidence open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id":"SUP-35","prior_identifier":"HR-V0-CONFIG-REC-P0.22","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R259 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    integration, fields = read_csv(CFG / "bom-integration-map.csv")
    integration.extend({"item_id":row["item_id"],"role":roles[row["item_id"]],"bound_identifier":row["manufacturer_part_number"],"closure_class":row["baseline_status"],"physical_evidence":"OPEN","procurement_released":"NO","warning":WARNING} for row in observation_rows())
    write_csv(CFG / "bom-integration-map.csv", fields, integration)
    gates, fields = read_csv(CFG / "gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-003","EG-010","EG-015"}:
            row["evidence_added"] = f"{row['evidence_added']}; {ID}"
            row["remaining_evidence"] = f"{row['remaining_evidence']}; exact observation mounting/cuts, provider/received/physical/qualified evidence"
    write_csv(CFG / "gate-impact.csv", fields, gates)
    config_holds, fields = read_csv(CFG / "open-holds.csv")
    for row in config_holds:
        if row["hold_id"] == "HOLD-15":
            row["hold"] = "Observation assemblies and quantities are integrated through BOM-108; exact mounting hardware, cuts and physical closure remain"
            row["state"] = "DESIGN REQUIRED"
            row["closure_evidence"] = f"{ID}; exact mounting hardware and released cut/termination schedules plus receiving evidence"
    for index, row in enumerate(holds, 137):
        config_holds.append({"hold_id":f"HOLD-{index:03d}","hold":f"{ID}: {row['scope']}","state":row["state"],"closure_evidence":row["evidence_required"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", fields, config_holds)
    config_acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for index, row in enumerate(acceptance, 170):
        config_acceptance.append({"acceptance_id":f"ACC-{index:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, config_acceptance)
    config_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    config_status.update({"identifier":CID,"round":"R259","date":"2026-08-12","system_bom_groups":108,"current_records":42,"supersession_records":35,"bom_integration_records":28,"open_holds":144,"acceptance_rows":179,"observation_bom_integration":ID})
    (CFG / "package-status.json").write_text(json.dumps(config_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR259 adds {ID}, BOM-099 through BOM-108, and corrects current release metadata to 108 groups. Exact mounting hardware, cable cuts, provider/received evidence, physical tests, qualified review and all work authority remain open. 144 holds and 179 unexecuted acceptances remain.\n", encoding="utf-8")
    (CFG / "index.html").write_text(guide(bindings, assemblies, mounting, holds), encoding="utf-8")
    source_rows = []
    for row in current:
        path = ROOT / row["source_path"]
        source_rows.append({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], source_rows)
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)
    print(f"Generated {ID}: 108 BOM groups; 10 observation groups; zero work authority")


if __name__ == "__main__":
    main()
