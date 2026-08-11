#!/usr/bin/env python3
"""Generate R241 protected-routing segregation hardware and configuration P0.5."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/routing/hr-v0-p121-segregation-hardware-p0.1"
OUT = ROOT / "release/hr-v0/p121-segregation-hardware-p0.1"
CFG_SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.4"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.5"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.5"
IDENT = "HR-V0-P121-SEGREGATION-HW-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.5"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(record: dict[str, str]) -> dict[str, str]:
    return {**record, "warning": WARNING}


def manifest(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    write(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])


def routing_data() -> dict[str, list[dict[str, str]]]:
    catalog = [
        warned({"candidate_id":"WD5-CANDIDATE","manufacturer":"Phoenix Contact","description":"CD 25X25 cable duct; mounting base plus upper part","item_number":"3240187","material":"PVC; stone gray RAL 7030; UL 94 V0","width_mm":"25","height_mm":"25","stock_length_mm":"2000","usage_cross_section_mm2":"327","catalog_60_percent_example":"10 cables; 2.5 mm2; diameter 3.4 mm","operating_temperature_C":"-25..60","approvals":"UL Recognized E328576; CSA 80202282; VDE drawing approval 40058456","packing_and_order":"packing unit 24; minimum order quantity 24; GTIN 4046356459105","primary_source":"https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-25x25-3240187","source_revision_or_access":"current official US product page accessed 2026-08-11","project_state":"EXACT PLANNING CANDIDATE; SELECTION REQUIRED; HOLD"}),
        warned({"candidate_id":"EXISTING-DUCT-A","manufacturer":"Phoenix Contact","description":"CD 40X40 cable duct; current WD1-WD4 stock candidate","item_number":"3240189","material":"PVC; stone gray RAL 7030; UL 94 V0","width_mm":"40","height_mm":"40","stock_length_mm":"2000","usage_cross_section_mm2":"1235","catalog_60_percent_example":"40 cables; 2.5 mm2; diameter 3.4 mm","operating_temperature_C":"-25..60","approvals":"UL Recognized E328576; CSA 80202282; VDE drawing approval 40058456","packing_and_order":"packing unit 26; minimum order quantity 26; GTIN 4046356459143","primary_source":"https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-40x40-3240189","source_revision_or_access":"current official US product page accessed 2026-08-11","project_state":"EXISTING EXACT PLANNING CANDIDATE; CANNOT SUPPLY WD5 FROM RESIDUAL"}),
    ]
    geometry = [warned({
        "reference":"WD5","role":"separate top horizontal candidate for SF01-SUPPLY and DF01-GATE-HOT planning routes","x_mm":"54.0","y_mm":"10.0","width_mm":"369.8","height_mm":"25.0","backplate_boundary":"533.4 x 685.8 mm usable backplate","top_margin_mm":"10.0","gap_to_DR1_mm":"10.0","gap_to_device_envelopes_mm":"20.0","intersection":"WD2 overlap x=383.8..423.8 y=10..35; intentional planning junction only","release_state":"GEOMETRY SCREEN PASS; INSTALLATION/CUT/JUNCTION NOT RELEASED"
    })]
    stock = [
        warned({"stock_id":"DUCT-A","item_number":"3240189","stock_length_mm":"2000.0","existing_allocation_mm":"1979.2","new_allocation_mm":"0.0","residual_before_kerf_mm":"20.8","result":"FAIL FOR WD5: residual is shorter than 369.8 mm before kerf","procurement_state":"EXISTING CANDIDATE HOLD"}),
        warned({"stock_id":"DUCT-B","item_number":"3240187","stock_length_mm":"2000.0","existing_allocation_mm":"0.0","new_allocation_mm":"369.8","residual_before_kerf_mm":"1630.2","result":"PLANNING LENGTH PASS ONLY; kerf, tolerance, cut plan and order pack unresolved","procurement_state":"SELECTION REQUIRED; APPLICATION QUANTITY 1 IS NOT MANUFACTURER ORDER QUANTITY 24"}),
    ]
    conductor_names = [
        ("C-01","XD24:02 to SR1:A1","SAFETY_24V","SF01-SUPPLY"),
        ("C-02","XD24:06 to KWD1:A1","SAFETY_24V","DF01-GATE-HOT"),
        ("C-03","XD24:07 to KWD1:11","SAFETY_24V","DF01-GATE-HOT"),
        ("C-04","XD24:09 to KWD2:A1","SAFETY_24V","DF01-GATE-HOT"),
        ("C-05","XD24:10 to KWD2:21","SAFETY_24V","DF01-GATE-HOT"),
        ("C-06","KWD1:14 to KWD2:11","WD_SRA1_SUPPLY_INTERMEDIATE","DF01-GATE-HOT"),
        ("C-07","KWD2:14 to SRA1:A1","SRA1_A1_WD_GATED","DF01-GATE-HOT"),
    ]
    conductors = [warned({"allocation_id":cid,"logical_conductor":scope,"net":net,"route_class":cls,"count":"1","candidate_duct":"WD5 plus WD2 transition","exact_order_code":"SELECTION REQUIRED","conductor_size":"SELECTION REQUIRED","outside_diameter_mm":"SELECTION REQUIRED","ampacity_and_derating":"SELECTION REQUIRED","bend_and_termination":"SELECTION REQUIRED","fill_disposition":"NOT CALCULATED; Phoenix catalog example is not a project release"}) for cid,scope,net,cls in conductor_names]
    junction = [
        warned({"control_id":"JCT-01","object":"WD5-to-WD2 planning junction","geometry":"40 x 25 mm overlap at x=383.8..423.8 y=10..35","manufacturer_fact":"CD 25X25 page states removable bars, cover retention and optional retaining clips; no project-reviewed internal divider or T-junction accessory is documented","required_selection":"exact breakout/cutout, rib removal, edge treatment, cover access, retaining clips and junction drawing","state":"SELECTION REQUIRED"}),
        warned({"control_id":"JCT-02","object":"WD5 device drops","geometry":"planning drops to SR1/SRA1/KWD1/KWD2 envelope tops at y=55","manufacturer_fact":"received terminal entry geometry is not available","required_selection":"terminal orientation, entry point, bend radius, ferrule, cover and short-circuit/common-cause control","state":"SELECTION REQUIRED"}),
    ]
    domains = [
        warned({"corridor":"WD1","occupancy":"credited input candidate","exclusivity":"CANDIDATE EXCLUSIVE; NOT PHYSICALLY VERIFIED","safety_credit":"NOT VALIDATED","remaining_issue":"received route, partitions/covers, terminal entries and common-cause review"}),
        warned({"corridor":"WD5","occupancy":"SF01 direct supply plus ordinary watchdog-hot conductors","exclusivity":"TOP CORRIDOR CANDIDATE","safety_credit":"ZERO FOR DF-01; DUCT ITSELF IS NOT A SAFETY COMPONENT","remaining_issue":"selection, fill, cut/junction, received fit and qualified review"}),
        warned({"corridor":"WD2","occupancy":"mixed ordinary diagnostics, observation compute harness and WD5 hot-route transition","exclusivity":"NOT EXCLUSIVE","safety_credit":"NONE CLAIMED","remaining_issue":"interaction, fill, thermal, adjacency, fault and junction acceptance"}),
    ]
    holds = [
        "Phoenix Contact application confirmation for the exact WD5/WD2 junction and accessories",
        "Exact junction cutout, rib removal, end treatment, cover access, clips, fasteners and labels",
        "Exact conductor family, gauge, color, order code, outside diameter and insulation rating",
        "Duct fill and thermal calculation including all WD2 occupants, ambient, bundling and duty",
        "Minimum separation and common-cause/fault disposition by qualified electrical and functional-safety reviewers",
        "Received duct identity, dimensions, fit, material, approvals and accessory compatibility",
        "Released cut/kerf/tolerance/fastening drawing and backplate hole/bonding disposition",
        "Installed route, cover, continuity, isolation, pull, visual and photographic evidence",
        "Formal P1.21 acceptance and signed work authorization",
    ]
    open_holds = [warned({"hold_id":f"R241-H{i:02d}","hold":hold,"state":"OPEN","closure_evidence":"SELECTION REQUIRED; no evidence accepted"}) for i,hold in enumerate(holds,1)]
    inspections = [warned({"inspection_id":f"R241-I{i:02d}","object":obj,"acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","approver":""}) for i,obj in enumerate(("received CD 25X25 identity","WD5 cut and edges","WD5 fastening and cover","WD5/WD2 junction","seven-conductor allocation","duct fill and thermal","credited/hot corridor adjacency","complete installed route"),1)]
    sources = [warned({"source_path":"release/hr-v0/p121-protected-routing-p0.1/package-status.json","sha256":digest(ROOT / "release/hr-v0/p121-protected-routing-p0.1/package-status.json"),"role":"R240 protected-routing basis"}), warned({"source_path":"release/hr-v0/panel-node-placement-p0.1/candidate-backplate-layout.csv","sha256":digest(ROOT / "release/hr-v0/panel-node-placement-p0.1/candidate-backplate-layout.csv"),"role":"controlled panel geometry basis"})]
    return {"catalog-candidate-register.csv":catalog,"wd5-geometry-register.csv":geometry,"stock-screen.csv":stock,"conductor-allocation-screen.csv":conductors,"junction-control-register.csv":junction,"domain-occupancy-register.csv":domains,"open-holds.csv":open_holds,"inspection-register.csv":inspections,"source-register.csv":sources}


def svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 760" role="img" aria-labelledby="title desc"><title id="title">WD5 segregation hardware planning overlay</title><desc id="desc">A scaled plan view of the candidate panel showing separate WD1, WD5 and WD2 corridor envelopes.</desc><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:16px}}.small{{font-size:14px}}.label{{font-weight:700}}.box{{fill:#fff;stroke:#082b4c;stroke-width:3}}.duct{{fill:#8bd7f7;stroke:#1268a8;stroke-width:3}}.hot{{fill:#f3b61f;stroke:#8a6100;stroke-width:3}}.hold{{fill:#fff1bd;stroke:#9b6d00;stroke-width:3;stroke-dasharray:8 5}}</style><rect width="980" height="760" fill="#f7fbfe"/><text x="40" y="42" class="label">{IDENT} · scaled planning view</text><rect x="155" y="65" width="533.4" height="685.8" class="box"/><text x="700" y="90" class="small">Usable backplate</text><rect x="163" y="75" width="40" height="665.8" class="duct"/><line x1="110" y1="150" x2="163" y2="150" stroke="#1268a8" stroke-width="3"/><text x="35" y="140" class="label">WD1</text><text x="35" y="165" class="small">credited input</text><rect x="209" y="75" width="369.8" height="25" class="hot"/><text x="220" y="94" class="label">WD5 · 3240187 · 25 × 25</text><rect x="209" y="110" width="323.8" height="7.5" fill="#b9c5cf" stroke="#52606b" stroke-width="2"/><text x="220" y="137" class="small">10 mm gap to DR1; 20 mm to devices</text><rect x="538.8" y="75" width="40" height="665.8" class="duct"/><line x1="578.8" y1="150" x2="610" y2="150" stroke="#1268a8" stroke-width="3"/><text x="620" y="142" class="label">WD2</text><text x="620" y="167" class="small">mixed occupancy</text><rect x="538.8" y="75" width="40" height="25" class="hold"/><line x1="578.8" y1="88" x2="780" y2="210" stroke="#9b6d00" stroke-width="3"/><rect x="700" y="190" width="240" height="120" rx="10" class="hold"/><text x="718" y="220" class="label">Junction hold</text><text x="718" y="248">Exact breakout, ribs,</text><text x="718" y="274">edges, cover and clips</text><text x="718" y="300">SELECTION REQUIRED</text><rect x="209" y="175" width="369.8" height="430" fill="#fff" stroke="#8294a4" stroke-width="2" stroke-dasharray="6 6"/><text x="220" y="205">Device region begins y = 55 mm</text><text x="40" y="710" class="small">Duct envelopes are not released cut geometry and establish no functional-safety credit.</text><text x="40" y="738" class="small">{WARNING}</text></svg>'''


def guide(data: dict[str, list[dict[str, str]]]) -> str:
    rows = "".join(f"<tr><td>{html.escape(r['allocation_id'])}</td><td>{html.escape(r['logical_conductor'])}</td><td>{html.escape(r['net'])}</td><td>{html.escape(r['fill_disposition'])}</td></tr>" for r in data["conductor-allocation-screen.csv"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 segregation hardware</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05;max-width:20ch}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.5rem 0}}.card{{background:#fff;border:2px solid var(--blue);border-radius:.8rem;padding:1rem}}.viewer{{background:white;border:3px solid var(--navy);border-radius:.8rem;overflow:auto}}.viewer img{{display:block;width:100%;min-width:820px}}.controls{{display:flex;gap:.75rem;flex-wrap:wrap;margin:.8rem 0}}button{{font:inherit;font-weight:700;padding:.7rem 1rem;border:2px solid var(--navy);border-radius:.6rem;background:white;color:var(--navy)}}.table{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:960px;background:#fff}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:white}}code{{font-size:14px}}.note{{border-left:7px solid var(--gold);padding:1rem;background:#fff}}</style></head><body><header><strong>{IDENT} · R241</strong><h1>A real duct candidate, still not a released route</h1><div class="warning">{WARNING}</div></header><main><div class="grid"><article class="card"><b>3240187</b><br>Phoenix Contact CD 25X25 exact candidate</article><article class="card"><b>369.8 mm</b><br>WD5 planning length</article><article class="card"><b>7 conductors</b><br>logical allocation; physical wire unselected</article><article class="card"><b>9 open holds</b><br>zero safety credit or work authority</article></div><p class="note">The separate 25 × 25 mm duct body and cover replace the undocumented idea of an internal divider. The WD5/WD2 junction, conductor outside diameter, fill, thermal conditions, bend and separation are still <b>SELECTION REQUIRED</b>.</p><div class="controls"><button id="zoomIn">Zoom in</button><button id="zoomOut">Zoom out</button><button id="reset">Reset</button></div><div class="viewer"><img id="drawing" src="segregation-overlay.svg" alt="Segregation hardware planning overlay"></div><h2>Seven logical conductors</h2><div class="table"><table><thead><tr><th>ID</th><th>Endpoints</th><th>Net</th><th>Fill disposition</th></tr></thead><tbody>{rows}</tbody></table></div><h2>What is actually resolved</h2><p>Phoenix Contact item 3240187 is an exact purchasable catalog candidate with a 25 × 25 × 2000 mm envelope. One 369.8 mm WD5 planning piece fits the declared panel envelope with 10 mm to DR1 and 20 mm to the device region. Existing item 3240189 stock cannot supply it because only 20.8 mm remains before kerf.</p><h2>What remains unresolved</h2><p>No numeric safety separation is claimed. WD2 is mixed-occupancy, the T-junction is not released, the manufacturer’s ten-cable example is not a project fill calculation, and no conductor, fastener, label, cutout, physical inspection or qualified acceptance exists.</p></main><script>const im=document.querySelector('#drawing');let z=1;const set=()=>im.style.width=(z*100)+'%';document.querySelector('#zoomIn').onclick=()=>{{z=Math.min(2.5,z+.25);set()}};document.querySelector('#zoomOut').onclick=()=>{{z=Math.max(1,z-.25);set()}};document.querySelector('#reset').onclick=()=>{{z=1;set()}};</script></body></html>'''


def config_data() -> dict[str, list[dict[str, str]]]:
    names = ("current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv")
    data = {name: read(CFG_SOURCE / name) for name in names}
    data["current-configuration-map.csv"].append(warned({"record_id":"CFG-24","role":"P1.21 protected-routing segregation hardware","identifier":IDENT,"source_path":"release/hr-v0/p121-segregation-hardware-p0.1/package-status.json","configuration_state":"CURRENT HELD PHYSICAL-ROUTING CANDIDATE","release_boundary":"exact duct body/cover and planning envelope only; junction, conductors, fill, installation, safety credit and authority open"}))
    data["supersession-map.csv"].append(warned({"record_id":"SUP-12","prior_identifier":"HR-V0-CONFIG-REC-P0.4","current_or_required_successor":CFG_IDENT,"disposition":"P0.4 remains the immutable R223 snapshot; P0.5 adds R241/BOM-096 without promoting P1.21 or any physical/work gate","use_authorized":"NO"}))
    data["bom-integration-map.csv"].append(warned({"item_id":"BOM-096","role":"separate P1.21 top routing duct body and cover candidate","bound_identifier":"Phoenix Contact CD 25X25 item 3240187; application quantity 1; manufacturer MOQ/pack 24","closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO"}))
    for row in data["gate-impact.csv"]:
        row["evidence_added"] = IDENT
        if row["gate_id"] in {"EG-002","EG-003","EG-004","EG-012","EG-018","EG-020"}:
            row["remaining_evidence"] += "; R241 junction/conductor/fill/physical/qualified closure"
    for n,(hold,state,evidence) in enumerate((("WD5/WD2 exact junction and accessory application","SELECTION REQUIRED","manufacturer or qualified accepted junction drawing"),("WD5 conductor/fill/thermal and adjacency closure","NOT EXECUTED","accepted calculations and physical inspection"),("P1.21/R241 independent and qualified disposition","NOT EXECUTED","signed configuration and safety review")),27):
        data["open-holds.csv"].append(warned({"hold_id":f"HOLD-{n:02d}","hold":hold,"state":state,"closure_evidence":evidence}))
    for n,criterion in enumerate(("BOM-096 exact item and hold classification match the current Phoenix Contact source","WD5 envelope fits the controlled backplate with declared nominal gaps","Existing DUCT-A residual is not reused for WD5","Junction, fill, conductor and physical evidence remain unresolved","P1.15 remains current and P1.21 remains unaccepted"),25):
        data["acceptance-matrix.csv"].append(warned({"acceptance_id":f"ACC-{n:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    return data


def main() -> None:
    data = routing_data()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, records in data.items(): write(directory / name, records)
        text(directory / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR241 controls an exact 25 x 25 mm duct body/cover candidate and panel fit screen. Junction, conductors, fill, installation, safety credit and all authority remain open.\n")
        text(directory / "segregation-overlay.svg", svg())
        status = {"identifier":IDENT,"round":"R241","date":"2026-08-11","catalog_candidates":2,"selected_planning_candidate":"Phoenix Contact 3240187","wd5_length_mm":369.8,"logical_conductors":7,"open_holds":9,"blank_inspections":8,"numeric_safety_separation_released":False,"fill_calculation_complete":False,"junction_released":False,"physical_evidence_exists":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
        text(directory / "package-status.json", json.dumps(status,indent=2)+"\n")
    text(OUT / "index.html", guide(data))
    manifest(ENG); manifest(OUT)

    cfg = config_data()
    for directory in (CFG_ENG, CFG_OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, records in cfg.items(): write(directory / name, records)
        text(directory / "README.md", f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR241 adds held BOM-096 and {IDENT}. P1.15 remains current; P1.21 is unaccepted; no work gate closes.\n")
        status = {"identifier":CFG_IDENT,"round":"R241","date":"2026-08-11","current_core_electrical_identifier":"Project Button Electrical V3-P1.15-CARRIER-CANDIDATE","unaccepted_panel_topology_candidate":"V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE","system_bom_groups":96,"current_records":24,"supersession_records":12,"bom_integration_records":16,"gate_records":11,"open_holds":29,"acceptance_rows":29,"all_acceptance_executed":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
        text(directory / "package-status.json",json.dumps(status,indent=2)+"\n")
    cfg_sources = []
    for row in cfg["current-configuration-map.csv"]:
        path = ROOT / row["source_path"]
        cfg_sources.append(warned({"source_path":row["source_path"],"sha256":digest(path),"role":"current configuration evidence"}))
    for directory in (CFG_ENG, CFG_OUT):
        write(directory / "source-hash-register.csv",cfg_sources)
        manifest(directory)
    text(CFG_OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CFG_IDENT}</title><style>body{{margin:0;background:#f7fbfe;color:#082b4c;font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(32px,5vw,58px)}}.warning{{padding:16px;background:#fff3c4;border:3px solid #9b6d00;font-weight:800}}.card{{padding:18px;margin:18px 0;background:white;border:2px solid #1268a8;border-radius:12px}}code{{font-size:14px}}</style></head><body><main><div class="warning">{WARNING}</div><h1>{CFG_IDENT}</h1><div class="card"><b>96 covered BOM groups</b><p>BOM-096 is an exact Phoenix Contact 3240187 candidate on hold. It is not procurement-released.</p></div><div class="card"><b>P1.15 remains current</b><p>P1.21 and R241 remain unaccepted candidates. Junction, conductors, physical evidence, qualified review and every work authorization remain open.</p></div></main></body></html>''')
    manifest(CFG_OUT)
    print(f"{IDENT}: exact duct candidate; 9 holds; no route, safety credit or authority")
    print(f"{CFG_IDENT}: 96 BOM groups; P1.15 current; P1.21 unaccepted")


if __name__ == "__main__": main()
