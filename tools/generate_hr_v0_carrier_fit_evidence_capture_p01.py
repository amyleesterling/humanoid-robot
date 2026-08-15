"""Generate R265 inert, unpowered carrier-fit evidence capture package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-CARRIER-FIT-EVID-CAP-P0.1"
CID = "HR-V0-CONFIG-REC-P0.29"
ROUND = "R265"
DATE = "2026-08-12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, MARKING, DRILLING, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "tests/hr-v0-carrier-fit-evidence-capture-p0.1"
REL = ROOT / "release/hr-v0/carrier-fit-evidence-capture-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.28"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.29"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.29"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
MOUNT = ROOT / "release/hr-v0/dxl-carrier-mount-p0.2"
SOURCES = {
    "mount_status": MOUNT / "package-status.json",
    "holes": MOUNT / "hole-coordinate-register.csv",
    "anchors": MOUNT / "connector-anchor-register.csv",
    "metrology": MOUNT / "no-drill-metrology-form.csv",
    "mockup": MOUNT / "inert-mockup-definition.csv",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def warned(records):
    return [{**row, "warning": WARNING} for row in records]


def manifest(directory: Path) -> None:
    paths = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", ["path","bytes","sha256"], [
        {"path":p.relative_to(directory).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in paths
    ])


def measurement_plan():
    result=[]
    def add(group, article, characteristic, unit, nominal="", source="R264", method="SELECTION REQUIRED"):
        result.append({"measurement_id":f"MEAS-{len(result)+1:03d}","group":group,"article":article,"characteristic":characteristic,"unit":unit,"nominal_or_reference":nominal,"acceptance_limit":"SELECTION REQUIRED","method_or_instrument":method,"raw_value":"","instrument_id":"","evidence_uri":"","operator":"","reviewer":"","execution_state":"NOT EXECUTED","result":"OPEN"})
    for name,nominal in (("width",533.4),("height",685.8),("thickness",2.54),("formed flange",19.05),("flatness deviation","SELECTION REQUIRED")):
        add("panel","18P2721",name,"mm",nominal)
    for carrier in ("LIM1","LIM2","LIM3"):
        for hole in ("MH1","MH2","MH3","MH4"):
            add("rear clearance",carrier,f"panel-side screw/head to enclosure wall or boss at {hole}","mm")
    for carrier in ("LIM1","LIM2","LIM3"):
        add("cover clearance",carrier,"populated assembly to closed cover minimum","mm")
    for carrier in ("LIM1","LIM2","LIM3"):
        for characteristic,nominal in (("board width",100),("board height",60),("board thickness",1.6),("MH1-MH2 center span",90),("MH1-MH3 center span",50),("JIN1-JOUT1 anchor span",84),("maximum populated height","SELECTION REQUIRED")):
            add("received carrier",carrier,characteristic,"mm",nominal)
    for characteristic,nominal in (("minimum body length",10),("maximum body diameter",6.5),("minimum thread depth end A",6),("minimum thread depth end B",6)):
        add("standoff lot","TNM3-6.5-10-1",characteristic,"mm",nominal)
    for characteristic,nominal in (("screw length",6),("head diameter",5.9),("head height",1.8)):
        add("screw lot","NSE-1580-M3-6 replacement candidate",characteristic,"mm",nominal)
    add("print calibration","mockup sheet","100 mm horizontal scale-bar measured length","mm",100)
    add("print calibration","mockup sheet","100 mm vertical scale-bar measured length","mm",100)
    for carrier in ("LIM1","LIM2","LIM3"):
        for side in ("left","right","top","bottom"):
            add("loose placement",carrier,f"minimum boundary clearance: {side}","mm")
    for carrier in ("LIM1","LIM2","LIM3"):
        for connector in ("JIN1","JOUT1"):
            add("connector sweep",carrier,f"{connector} mated housing/wire minimum clearance","mm")
            add("bend sweep",carrier,f"{connector} achieved minimum bend radius","mm",20)
            add("service access",carrier,f"{connector} minimum tool/finger access","mm")
    return result


def package_rows():
    source_rows=[
        {"source_id":"SRC-01","record":SOURCES["mount_status"].relative_to(ROOT).as_posix(),"revision_or_date":"R264 / 2026-08-12 / SHA-256 bound","controlled_use":"authority flags and source lineage","not_proved":"any physical result or authority"},
        {"source_id":"SRC-02","record":SOURCES["holes"].relative_to(ROOT).as_posix(),"revision_or_date":"R264 / 2026-08-12 / SHA-256 bound","controlled_use":"twelve nominal center datums","not_proved":"panel hole diameter, tolerance, received alignment or drilling release"},
        {"source_id":"SRC-03","record":SOURCES["anchors"].relative_to(ROOT).as_posix(),"revision_or_date":"R264 / 2026-08-12 / SHA-256 bound","controlled_use":"six nominal connector anchor datums","not_proved":"wire exit vector, connector sweep, route or cut length"},
        {"source_id":"SRC-04","record":SOURCES["metrology"].relative_to(ROOT).as_posix(),"revision_or_date":"R264 / 2026-08-12 / SHA-256 bound","controlled_use":"fourteen-step unpowered no-drill inspection sequence","not_proved":"execution or acceptance"},
        {"source_id":"SRC-05","record":SOURCES["mockup"].relative_to(ROOT).as_posix(),"revision_or_date":"R264 / 2026-08-12 / SHA-256 bound","controlled_use":"disposable mockup intent and required features","not_proved":"printer scale, received fit or permission to modify hardware"},
    ]
    articles=[]
    for aid,role,identity in (
        ("ART-01","enclosure","Hammond PJ302410RT candidate"),("ART-02","panel","Hammond 18P2721 candidate"),
        ("ART-03","carrier","LIM1 P0.3 received PCBA or dimensionally controlled inert surrogate"),("ART-04","carrier","LIM2 P0.3 received PCBA or dimensionally controlled inert surrogate"),("ART-05","carrier","LIM3 P0.3 received PCBA or dimensionally controlled inert surrogate"),
        ("ART-06","standoffs","twelve TNM3-6.5-10-1 candidates"),("ART-07","screws","twenty-four NSE-1580-M3-6 replacement candidates"),
        ("ART-08","connector/wire samples","six B2P-VH/VHR-2N/SVH-21T-P1.1/Belden 9918 sample interfaces"),("ART-09","printed mockups","three disposable paper/card carrier envelopes")):
        articles.append({"article_id":aid,"role":role,"required_identity":identity,"manufacturer":"","part_number":"","lot_serial_revision":"","received_state":"NOT RECEIVED OR NOT RECORDED","photo_uri":"","review_state":"OPEN"})
    instruments=[]
    for iid,role,minimum in (
        ("INST-01","panel/board/standoff/screw dimensional measurement","resolution, range, uncertainty and current traceable calibration SELECTION REQUIRED"),
        ("INST-02","flatness measurement","surface/reference method, indicator resolution and uncertainty SELECTION REQUIRED"),
        ("INST-03","depth/rear/cover clearance measurement","probe geometry, range and uncertainty SELECTION REQUIRED"),
        ("INST-04","print-scale verification","calibrated rule or equivalent with accepted uncertainty SELECTION REQUIRED"),
        ("INST-05","photographic scale/reference","scale artifact identity and distortion-control method SELECTION REQUIRED")):
        instruments.append({"instrument_id":iid,"role":role,"minimum_record":minimum,"make_model":"","serial":"","range":"","resolution":"","calibration_due":"","uncertainty":"","state":"SELECTION REQUIRED"})
    photos=[]
    photo_defs=[
        ("PH-01","all article labels and received condition"),("PH-02","panel front with full scale and orientation datum"),("PH-03","panel rear with full scale and enclosure bosses"),
        ("PH-04","printed horizontal and vertical 100 mm scale checks"),("PH-05","LIM1 loose envelope, front and side"),("PH-06","LIM2 loose envelope, front and side"),("PH-07","LIM3 loose envelope, front and side"),
        ("PH-08","all twelve candidate rear-fastener locations without marking"),("PH-09","closed-cover gauge condition"),("PH-10","six mated connector/wire sweeps"),
        ("PH-11","six bend-radius and duct-entry sweeps"),("PH-12","service-tool access and every interference/deviation"),
    ]
    for pid,view in photo_defs:
        photos.append({"photo_id":pid,"required_view":view,"configuration_label_visible":"REQUIRED","scale_visible":"REQUIRED","orientation_visible":"REQUIRED","file_uri":"","captured":"NO","reviewed":"NO"})
    stops=[]
    for sid,condition,action in (
        ("STOP-01","any electrical source, battery, charger or powered conductor is present","stop; isolate and remove source; this session is zero-energy only"),
        ("STOP-02","panel or enclosure would need marking, punching, drilling, cutting, adhesive or permanent fastener","stop; no material modification is authorized"),
        ("STOP-03","printed scale bars are not reconciled to 100 mm in both axes","stop; reject print and do not use its geometry"),
        ("STOP-04","article identity or revision is missing or differs from the controlled candidate","stop; quarantine evidence and open deviation"),
        ("STOP-05","instrument identity, calibration or uncertainty is absent","stop affected measurement; record no accepted result"),
        ("STOP-06","a surrogate is treated as a received PCBA or connector","stop; label surrogate and limit evidence to its proven dimensions"),
        ("STOP-07","any part must be forced, bent, clamped or loaded to fit","stop; photograph interference without forcing"),
        ("STOP-08","cover closure contacts or loads a gauge, board, connector or wire","stop; do not latch cover; record interference"),
        ("STOP-09","20 mm wire bend radius cannot be maintained","stop that route; record deviation; do not cut production wire"),
        ("STOP-10","service access requires removing a credited guard, duct, terminal or safety component","stop; record inaccessible condition"),
        ("STOP-11","any raw value is edited into a pass/accept statement without an approved limit","stop review; raw evidence only"),
        ("STOP-12","scope, supervision or authorization is unclear","stop session and obtain written direction")):
        stops.append({"stop_id":sid,"condition":condition,"mandatory_action":action,"state":"ACTIVE"})
    deviations=[]
    for i in range(1,13):
        deviations.append({"deviation_id":f"DEV-{i:02d}","article_or_measurement":"","description":"","discovery_photo_uri":"","containment":"","owner":"","disposition":"OPEN / NOT ENTERED","qualified_approval":"","closed":"NO"})
    authority=[
        {"authority_id":"AUTH-01","scope":"open empty enclosure and loosely place disposable paper/card envelopes and nonconductive gauges","requester":"","approver":"","authorization_reference":"","state":"NOT AUTHORIZED"},
        {"authority_id":"AUTH-02","scope":"measure and photograph unpowered, unmodified candidate articles with controlled instruments","requester":"","approver":"","authorization_reference":"","state":"NOT AUTHORIZED"},
        {"authority_id":"AUTH-03","scope":"mate loose connector/wire samples solely for non-energized sweep evidence","requester":"","approver":"","authorization_reference":"","state":"NOT AUTHORIZED"},
    ]
    signoff=[]
    for role in ("session lead","configuration witness","metrology reviewer","mechanical reviewer","electrical/enclosure reviewer","program owner"):
        signoff.append({"role":role,"name":"","organization":"","competence_reference":"","review_scope":"","signature_reference":"","date":"","decision":"NOT SIGNED / NO ACCEPTANCE"})
    holds_text=[
        "separate written authority for the exact zero-energy session scope",
        "received article identities and dimensional-surrogate limitations",
        "selected instruments, methods, calibration and uncertainty budgets",
        "two-axis print-scale verification before any mockup use",
        "complete raw measurement and photo set with immutable evidence paths",
        "all deviations contained and dispositioned against approved limits",
        "received connector/wire sweeps with 20 mm bend-radius evidence",
        "front/rear/closed-cover/service clearances with no forced fit",
        "qualified mechanical and electrical/enclosure review",
        "separate successor authorization before marking, drilling or assembly",
    ]
    holds=[{"hold_id":f"H-{i:02d}","scope":t,"state":"OPEN","closure_evidence":"configuration-bound evidence plus named qualified signoff"} for i,t in enumerate(holds_text,1)]
    criteria=[
        "Session authority names exact articles, people, place, date and zero-energy/no-modification scope",
        "All nine article identities and surrogate limitations are recorded and photographed",
        "All used instruments have accepted method, calibration and uncertainty records",
        "Both 100 mm print scale bars are measured and accepted before mockup use",
        "All 80 measurement rows retain raw evidence and immutable evidence paths",
        "All twelve required photo groups show configuration, scale and orientation",
        "No article is forced, loaded, marked, drilled, cut, bonded or permanently installed",
        "All six connector sweeps preserve accepted clearance and 20 mm minimum bend radius",
        "All rear, cover and service clearances are positive to separately approved limits",
        "Every deviation is contained and receives qualified written disposition",
        "Qualified reviewers accept only the exact evidence configuration and limitations",
        "A separate successor release is required before any marking, drilling, assembly or powered work",
    ]
    acceptance=[{"acceptance_id":f"ACC-{i:02d}","criterion":c,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,c in enumerate(criteria,1)]
    return {
        "source-register.csv":(["source_id","record","revision_or_date","controlled_use","not_proved","warning"],warned(source_rows)),
        "article-identity-register.csv":(["article_id","role","required_identity","manufacturer","part_number","lot_serial_revision","received_state","photo_uri","review_state","warning"],warned(articles)),
        "instrument-register.csv":(["instrument_id","role","minimum_record","make_model","serial","range","resolution","calibration_due","uncertainty","state","warning"],warned(instruments)),
        "measurement-plan.csv":(["measurement_id","group","article","characteristic","unit","nominal_or_reference","acceptance_limit","method_or_instrument","raw_value","instrument_id","evidence_uri","operator","reviewer","execution_state","result","warning"],warned(measurement_plan())),
        "photo-shot-list.csv":(["photo_id","required_view","configuration_label_visible","scale_visible","orientation_visible","file_uri","captured","reviewed","warning"],warned(photos)),
        "stop-work-register.csv":(["stop_id","condition","mandatory_action","state","warning"],warned(stops)),
        "deviation-register.csv":(["deviation_id","article_or_measurement","description","discovery_photo_uri","containment","owner","disposition","qualified_approval","closed","warning"],warned(deviations)),
        "session-authorization-template.csv":(["authority_id","scope","requester","approver","authorization_reference","state","warning"],warned(authority)),
        "signoff-register.csv":(["role","name","organization","competence_reference","review_scope","signature_reference","date","decision","warning"],warned(signoff)),
        "open-holds.csv":(["hold_id","scope","state","closure_evidence","warning"],warned(holds)),
        "acceptance-matrix.csv":(["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"],warned(acceptance)),
    }


def mockup_svg():
    def board(x,y,label):
        holes="".join(f"<circle cx='{x+dx}' cy='{y+dy}' r='1.6'/>" for dx,dy in ((5,5),(95,5),(5,55),(95,55)))
        return f"<g><rect x='{x}' y='{y}' width='100' height='60' class='board'/>{holes}<line x1='{x+8}' y1='{y+27}' x2='{x+8}' y2='{y+33}'/><line x1='{x+5}' y1='{y+30}' x2='{x+11}' y2='{y+30}'/><line x1='{x+92}' y1='{y+27}' x2='{x+92}' y2='{y+33}'/><line x1='{x+89}' y1='{y+30}' x2='{x+95}' y2='{y+30}'/><text x='{x+50}' y='{y+27}' text-anchor='middle' class='label'>{label}</text><text x='{x+50}' y='{y+43}' text-anchor='middle' class='small'>100 x 60 mm envelope</text><text x='{x+8}' y='{y+24}' class='tiny'>JIN1</text><text x='{x+76}' y='{y+24}' class='tiny'>JOUT1</text></g>"
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='279.4mm' height='215.9mm' viewBox='0 0 279.4 215.9' role='img' aria-labelledby='title desc'><title id='title'>Disposable carrier-fit mockups</title><desc id='desc'>US Letter landscape sheet containing three 100 by 60 millimetre inert carrier envelopes and two 100 millimetre calibration bars.</desc><style>text{{font-family:Arial,sans-serif;fill:#092f57}}.title{{font-size:6px;font-weight:700}}.warn{{font-size:4.3px;font-weight:700;fill:#75151d}}.label{{font-size:6px;font-weight:700}}.small{{font-size:3.8px}}.tiny{{font-size:3.2px}}.board{{fill:#dff3ff;stroke:#092f57;stroke-width:.6}}circle,line{{fill:white;stroke:#092f57;stroke-width:.45}}</style><rect width='279.4' height='215.9' fill='white'/><text x='12' y='12' class='title'>R265 DISPOSABLE INERT FIT MOCKUPS - PRINT AT 100%</text><text x='12' y='20' class='warn'>NOT A DRILL TEMPLATE. DO NOT TRANSFER CENTERS TO METAL. VERIFY BOTH SCALE BARS.</text>{board(12,30,'LIM1')}{board(124,30,'LIM2')}{board(12,102,'LIM3')}<g><line x1='124' y1='115' x2='224' y2='115'/><line x1='124' y1='111' x2='124' y2='119'/><line x1='224' y1='111' x2='224' y2='119'/><text x='174' y='109' text-anchor='middle' class='label'>100 mm horizontal</text><line x1='250' y1='102' x2='250' y2='202'/><line x1='246' y1='102' x2='254' y2='102'/><line x1='246' y1='202' x2='254' y2='202'/><text x='242' y='152' text-anchor='middle' class='label' transform='rotate(-90 242 152)'>100 mm vertical</text></g><text x='124' y='140' class='warn'>CUT PAPER/CARD ONLY AFTER</text><text x='124' y='147' class='warn'>TWO-AXIS SCALE ACCEPTANCE.</text><text x='124' y='160' class='small'>Crosshairs: connector anchors only.</text><text x='124' y='167' class='small'>Circles: source-board hole envelopes.</text><text x='124' y='174' class='small'>All tolerances and physical acceptance remain open.</text><text x='12' y='194' class='warn'>PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, MARKING, DRILLING,</text><text x='12' y='202' class='warn'>ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION</text></svg>"""


def _interactive_html(data):
    plan=data["measurement-plan.csv"][1]
    grouped={}
    for row in plan: grouped.setdefault(row["group"],[]).append(row)
    sections=[]
    for group,items in grouped.items():
        trs="".join(f"<tr><td><code>{r['measurement_id']}</code></td><td>{html.escape(r['article'])}</td><td>{html.escape(r['characteristic'])}<small>Reference: {html.escape(str(r['nominal_or_reference']))} {html.escape(r['unit'])}</small></td><td><input type='number' step='any' inputmode='decimal' data-id='{r['measurement_id']}' aria-label='{html.escape(r['measurement_id'])} raw value'></td><td><input type='text' data-inst='{r['measurement_id']}' aria-label='{html.escape(r['measurement_id'])} instrument'></td><td><input type='text' data-uri='{r['measurement_id']}' aria-label='{html.escape(r['measurement_id'])} evidence URI'></td></tr>" for r in items)
        sections.append(f"<details><summary>{html.escape(group.title())} <span>{len(items)} rows</span></summary><div class='scroll'><table><thead><tr><th>ID</th><th>Article</th><th>Characteristic</th><th>Raw value</th><th>Instrument</th><th>Evidence URI</th></tr></thead><tbody>{trs}</tbody></table></div></details>")
    stops=data["stop-work-register.csv"][1]
    stop_cards="".join(f"<article><strong>{r['stop_id']}</strong><p>{html.escape(r['condition'])}</p><p>{html.escape(r['mandatory_action'])}</p></article>" for r in stops)
    schema=json.dumps([{"measurement_id":r["measurement_id"],"group":r["group"],"article":r["article"],"characteristic":r["characteristic"],"unit":r["unit"],"nominal_or_reference":r["nominal_or_reference"],"acceptance_limit":"SELECTION REQUIRED"} for r in plan],separators=(",",":"))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,62px);background:linear-gradient(135deg,var(--sky),white);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,68px);line-height:1.06;color:var(--blue)}}h2{{font-size:clamp(24px,2.4vw,36px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:850}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:14px}}article,section,details{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}}article strong{{font-size:18px;color:var(--danger)}}summary{{font-size:20px;font-weight:800;cursor:pointer}}summary span{{font-size:14px;background:var(--sky);padding:4px 8px;border-radius:8px}}.scroll{{overflow-x:auto;margin-top:14px}}table{{width:100%;border-collapse:collapse;min-width:1080px;font-size:14px}}th,td{{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #bed5e6}}th{{background:var(--blue);color:white}}td small{{display:block;font-size:14px}}input{{width:100%;min-width:150px;font:16px/1.35 system-ui;padding:8px;border:2px solid #759bb8;border-radius:7px}}button,a.button{{display:inline-block;font:800 16px/1.2 system-ui;padding:12px 16px;border:2px solid var(--blue);border-radius:9px;background:white;color:var(--blue);text-decoration:none;margin:5px}}button.primary{{background:var(--gold);color:#17253a}}.meter{{font-size:24px;font-weight:850;color:var(--blue)}}object{{width:100%;min-height:820px;border:2px solid var(--line)}}code{{font-size:14px}}@media(max-width:700px){{main{{padding:12px}}header{{padding:24px 16px}}object{{min-height:520px}}table{{min-width:940px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Measure first. Modify nothing.</h1><p>This local-only guide captures raw, unpowered fit evidence. It does not calculate pass/fail, transmit data or authorize a physical operation.</p></header><main><section><div class='meter'><span id='complete'>0</span> / {len(plan)} raw values recorded</div><p>Completeness is not acceptance. Every limit remains <strong>SELECTION REQUIRED</strong>.</p><button class='primary' id='json'>Download raw JSON</button><button id='csv'>Download raw CSV</button><button id='clear'>Clear this unsaved form</button><a class='button' href='disposable-mockups-letter.svg'>Open 1:1 disposable mockups</a></section><section><h2>Session identity</h2><div class='cards'><label>Session reference<input id='session' type='text'></label><label>Date/time<input id='when' type='datetime-local'></label><label>Location<input id='location' type='text'></label><label>Operator<input id='operator' type='text'></label><label>Authorization reference<input id='authority' type='text' placeholder='Must exist before physical session'></label></div></section><section><h2>Stop conditions</h2><div class='cards'>{stop_cards}</div></section><section><h2>Disposable mockups</h2><p>Print US Letter landscape at 100%, then measure both scale bars. Reject any print whose two-axis result is not accepted under the selected instrument uncertainty. Never transfer these centers to metal.</p><object type='image/svg+xml' data='disposable-mockups-letter.svg'>Disposable carrier mockups.</object></section><h2>Raw measurement capture</h2>{''.join(sections)}<p class='warn'>{WARNING}</p></main><script>const schema={schema};function collect(){{return{{package:'{ID}',warning:{json.dumps(WARNING)},session:document.querySelector('#session').value,when:document.querySelector('#when').value,location:document.querySelector('#location').value,operator:document.querySelector('#operator').value,authorization_reference:document.querySelector('#authority').value,acceptance_limits:'SELECTION REQUIRED',measurements:schema.map(r=>({{...r,raw_value:document.querySelector(`[data-id="${{r.measurement_id}}"]`).value,instrument_id:document.querySelector(`[data-inst="${{r.measurement_id}}"]`).value,evidence_uri:document.querySelector(`[data-uri="${{r.measurement_id}}"]`).value,result:'OPEN'}}))}}}}function count(){{document.querySelector('#complete').textContent=collect().measurements.filter(r=>r.raw_value!=='').length}}document.addEventListener('input',count);function download(name,type,text){{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{{type}}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}document.querySelector('#json').onclick=()=>download('hr-v0-carrier-fit-raw.json','application/json',JSON.stringify(collect(),null,2));document.querySelector('#csv').onclick=()=>{{const d=collect(),q=v=>'"'+String(v??'').replaceAll('"','""')+'"',head=['measurement_id','group','article','characteristic','unit','nominal_or_reference','acceptance_limit','raw_value','instrument_id','evidence_uri','result'],lines=[head.join(','),...d.measurements.map(r=>head.map(k=>q(r[k])).join(','))];download('hr-v0-carrier-fit-raw.csv','text/csv',lines.join('\n'))}};document.querySelector('#clear').onclick=()=>{{if(confirm('Clear every unsaved field on this page?'))location.reload()}};window.projectButtonCollect=collect;</script></body></html>"""


def interactive_parts(data):
    page = _interactive_html(data)
    page = page.replace("lines.join('\n')", "lines.join('\\n')")
    page = page.replace(
        "This local-only guide captures raw, unpowered fit evidence. It does not calculate pass/fail, transmit data or authorize a physical operation.",
        "This local-only guide captures raw, unpowered fit evidence. This page transmits nothing, calculates no pass/fail result, and authorizes no physical operation.",
    )
    script_start = page.index("<script>")
    script_end = page.index("</script>", script_start)
    script = page[script_start + len("<script>"):script_end]
    page = page[:script_start] + "<script src='capture.js'></script>" + page[script_end + len("</script>"):]
    return page, script + "\n"


def interactive_html(data):
    return interactive_parts(data)[0]


def update_release():
    data=json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]): product.setdefault("supporting_identifiers",[]).append(value)
            product["configuration_reconciliation"]=CID
            product["carrier_fit_evidence_capture"]=ID
        if product.get("domain")=="commissioning":
            product["carrier_fit_evidence_capture_summary"]="80 blank raw measurements / 12 photo groups / 12 active stop conditions / 10 holds / 12 blank acceptances / zero physical session or authority"
    RELEASE.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def update_config(data):
    shutil.copytree(CFG0,CFG)
    current,fields=read_csv(CFG/"current-configuration-map.csv")
    current.append({"record_id":"CFG-46","role":"carrier fit evidence capture","identifier":ID,"source_path":"release/hr-v0/carrier-fit-evidence-capture-p0.1/package-status.json","configuration_state":"CURRENT BLANK EVIDENCE CONTRACT","release_boundary":"raw unpowered data capture only; session and every physical operation remain unauthorized","warning":WARNING})
    write_csv(CFG/"current-configuration-map.csv",fields,current)
    supers,fields=read_csv(CFG/"supersession-map.csv")
    supers.append({"record_id":"SUP-43","prior_identifier":"HR-V0-CONFIG-REC-P0.28","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R265 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG/"supersession-map.csv",fields,supers)
    gates,fields=read_csv(CFG/"gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-003","EG-014","EG-018","EG-020"}:
            row["evidence_added"] += f"; {ID} blank raw physical-fit capture and stop-work contract"
            row["remaining_evidence"] += "; separately authorized session; received identities; calibrated instruments; executed raw measurements/photos; deviation disposition; qualified acceptance"
    write_csv(CFG/"gate-impact.csv",fields,gates)
    holds,fields=read_csv(CFG/"open-holds.csv")
    for i,row in enumerate(data["open-holds.csv"][1],201):
        holds.append({"hold_id":f"HOLD-{i:03d}","hold":f"{ID}: {row['scope']}","state":"OPEN","closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG/"open-holds.csv",fields,holds)
    accept,fields=read_csv(CFG/"acceptance-matrix.csv")
    for i,row in enumerate(data["acceptance-matrix.csv"][1],253):
        accept.append({"acceptance_id":f"ACC-{i:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"acceptance-matrix.csv",fields,accept)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"warning":WARNING,"system_bom_groups":109,"current_records":46,"supersession_records":43,"bom_integration_records":30,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(accept),"carrier_fit_evidence_capture":ID})
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR265 adds {ID}, a blank local-only physical-fit evidence contract. It authorizes no session or physical work. {len(holds)} holds and {len(accept)} blank acceptances remain.\n",encoding="utf-8")
    (CFG/"index.html").write_text((REL/"index.html").read_text(encoding="utf-8"),encoding="utf-8")
    (CFG/"capture.js").write_text((REL/"capture.js").read_text(encoding="utf-8"),encoding="utf-8")
    hashes=[]
    for row in current:
        path=ROOT/row["source_path"]
        hashes.append({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes)
    manifest(CFG); shutil.copytree(CFG,CFGR); manifest(CFGR)


def docs():
    (ROOT/"docs/hr-v0-carrier-fit-evidence-capture-p0.1.md").write_text(f"""# HR-V0 carrier-fit evidence capture P0.1

> **{WARNING}**

R265 converts R264's blank metrology contract into an executable local-only evidence surface. It contains 80 raw measurement rows, nine article identities, five instrument records, twelve photo groups, twelve active stop conditions, twelve deviation slots, three blank authorization rows, six blank reviewer signoffs, ten holds and twelve blank acceptance criteria.

The US Letter landscape SVG contains three disposable 100 x 60 mm paper/card carrier envelopes and independent horizontal/vertical 100 mm calibration bars. It is not a drill template. It must be rejected unless both scale bars are measured and accepted under a separately selected instrument/uncertainty method. Centers may not be transferred to metal.

The browser form runs locally and exports raw JSON/CSV only when the operator activates a download button. It has no network submission and performs no pass/fail calculation. Completeness is not acceptance; all limits remain `SELECTION REQUIRED`.

No session is authorized. No article, instrument, measurement, photo, deviation disposition or signature is recorded. Interactive guide: [release package](../release/hr-v0/carrier-fit-evidence-capture-p0.1/index.html).
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r265-validation-record.md").write_text(f"""# R265 validation record

> **{WARNING}**

Package: `{ID}`

Configuration: `{CID}`

Generation binds the exact R264 source hashes and produces 80 blank measurement rows, twelve blank photo groups, twelve active stop conditions, ten open holds and twelve blank acceptance rows. Both scale bars and all three board envelopes are encoded in millimetres on a US Letter landscape SVG. No physical session, download, measurement, photo, result, signature or authority is claimed.

Automated validation passed 206 non-native repository checks and 19 KiCad-native checks. The dedicated R265 checker and `node --check` of the external capture script passed. Browser QA at the effective 1280 x 720 viewport confirmed 16 px body/input text, 14 px table text, no page-level horizontal overflow, readable unclipped mockup art, successful script loading, and a completeness change from 0 to 1 after one dummy raw-value entry. No download was activated. The requested 390 x 844 viewport override remained at 1280 x 720, so narrow-mobile visual QA is explicitly unverified; the static CSS breakpoint and internal table scrolling were checked only from source.

The staged master release manifest passed with 6,340 package files. No Sol R12 blocker receives qualified closure.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r265-independent-review-request.md").write_text(f"""# R265 independent review request

> **{WARNING}**

Independently audit `{ID}` against the exact R264 source hashes. Verify all 80 measurement identities, units and source nominals; the nine article, five instrument, twelve photo, twelve stop-work, twelve deviation, three authorization and six signoff rows; the two 100 mm SVG calibration bars; and the three 100 x 60 mm envelopes with four 3.2 mm source-board holes and JIN1/JOUT1 anchors. Confirm the interactive form transmits nothing, computes no acceptance and exports only raw local JSON/CSV after a user action. Confirm no session, marking, drilling, fabrication, assembly, connection, powered test or energization authority is implied.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r265-status.md").write_text(f"""# Sol R12 status after R265

R265 makes one R264 physical-evidence route executable as a blank local capture package. No Sol R12 blocker closes: no article is received, no session is authorized, no measurement or test is executed, and no qualified reviewer accepts evidence.

The historical R12 verdict remains the independent baseline. HR-V0 remains not build-ready and energization remains prohibited.

> **{WARNING}**
""",encoding="utf-8")


def update_narrative():
    readme=ROOT/"README.md"; text=readme.read_text(encoding="utf-8")
    marker="- [R264 `HR-V0-DXL-CARRIER-MOUNT-IF-P0.2`"
    insert="- [R265 `HR-V0-CARRIER-FIT-EVID-CAP-P0.1` unpowered evidence capture](docs/hr-v0-carrier-fit-evidence-capture-p0.1.md)\n- [Interactive R265 carrier-fit measurement guide](release/hr-v0/carrier-fit-evidence-capture-p0.1/index.html)\n- [Interactive configuration reconciliation P0.29](release/hr-v0/configuration-reconciliation-p0.29/index.html)\n- [R265 independent review request](docs/reviews/2026-08-12-r265-independent-review-request.md)\n- [Sol R12 status after R265](docs/reviews/2026-08-12-sol-r12-post-r265-status.md)\n"
    if insert not in text: text=text.replace(marker,insert+marker)
    text=text.replace("Two hundred sixty-four rounds are complete: R01-R264.","Two hundred sixty-five rounds are complete: R01-R265.")
    text=text.replace("R264 transforms the current rotated carrier candidates", "R265 adds a local-only 80-row raw carrier-fit evidence surface and disposable calibrated mockups without authorizing a session. R264 transformed the current rotated carrier candidates")
    readme.write_text(text,encoding="utf-8")
    hand=ROOT/"docs/handoff-current.md"; h=hand.read_text(encoding="utf-8")
    block=f"R265 carrier-fit evidence capture: **`{ID}` turns the R264 no-drill contract into a local-only interactive form with 80 raw measurement rows, nine article identities, five instrument records, twelve photo groups, twelve active stop conditions, two 100 mm scale bars and three disposable 100 x 60 mm paper/card mockups. The page transmits nothing and computes no acceptance. `{CID}` carries 46 current records, 43 supersessions, 30 BOM integrations, 210 holds and 264 blank acceptances. No session, download, measurement, photo, result, signature, marking, drilling or other physical work is authorized or claimed. No Sol R12 blocker closes and energization remains prohibited.**\n\n"
    if not h.startswith(block): h=block+h
    hand.write_text(h,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; l=ledger.read_text(encoding="utf-8")
    row=f"| R265 | 2026-08-12 | Unpowered carrier-fit evidence capture | Codex test/configuration pass; not independent and no physical session | R264 mounting datums, metrology and mockup definitions | Issued `{ID}` with 80 blank raw measurements, nine article identities, five instrument rows, twelve photo groups, twelve active stops, two calibrated scale bars and a local-only export form. Ten holds and twelve blank acceptances remain. No session, data, result, acceptance or authority exists; no Sol blocker closes. | `docs/hr-v0-carrier-fit-evidence-capture-p0.1.md`; `tests/hr-v0-carrier-fit-evidence-capture-p0.1/`; `release/hr-v0/carrier-fit-evidence-capture-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.29/`; `docs/reviews/2026-08-12-sol-r12-post-r265-status.md` |\n"
    if row not in l:
        pos=l.find("\n\n",l.find("| R264 |")); l=l[:pos+2]+row+l[pos+2:]
    l=l.replace("Two hundred sixty-four rounds are complete (R01-R264).","Two hundred sixty-five rounds are complete (R01-R265).")
    l=l.replace("R264 adds exact transformed carrier hole/connector datums", "R265 adds an executable blank carrier-fit capture surface; R264 added exact transformed carrier hole/connector datums")
    ledger.write_text(l,encoding="utf-8")


def main():
    for path in [*SOURCES.values(),CFG0,RELEASE]:
        if not path.exists(): raise FileNotFoundError(path)
    for directory in (ENG,REL,CFG,CFGR):
        if directory.exists(): shutil.rmtree(directory)
    data=package_rows(); ENG.mkdir(parents=True)
    for name,(fields,records) in data.items(): write_csv(ENG/name,fields,records)
    (ENG/"disposable-mockups-letter.svg").write_text(mockup_svg(),encoding="utf-8")
    schema={"schema":"project-button-carrier-fit-raw-v1","package":ID,"measurement_rows":len(data["measurement-plan.csv"][1]),"acceptance_limits":"SELECTION REQUIRED","network_submission":False,"authority_released":False,"warning":WARNING}
    (ENG/"evidence-schema.json").write_text(json.dumps(schema,indent=2)+"\n",encoding="utf-8")
    status={"identifier":ID,"round":ROUND,"date":DATE,"measurement_rows":80,"article_rows":9,"instrument_rows":5,"photo_groups":12,"stop_conditions":12,"deviation_rows":12,"authorization_rows":3,"signoff_rows":6,"open_holds":10,"acceptance_rows":12,"all_measurements_blank":True,"all_acceptance_executed":False,"network_submission":False,"physical_session_authorized":False,"physical_session_executed":False,"download_executed":False,"measurement_executed":False,"photo_captured":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"marking_authorized":False,"drilling_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"source_hashes":{k:sha(v) for k,v in SOURCES.items()},"warning":WARNING}
    (ENG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (ENG/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR265 is a blank local-only raw evidence capture surface. It authorizes no session or physical work and computes no acceptance.\n",encoding="utf-8")
    manifest(ENG); shutil.copytree(ENG,REL)
    page,script=interactive_parts(data)
    (REL/"index.html").write_text(page,encoding="utf-8")
    (REL/"capture.js").write_text(script,encoding="utf-8")
    manifest(REL)
    update_release(); update_config(data); docs(); update_narrative()
    print(f"Generated {ID}: 80 measurements / 12 photos / 12 stops / 0 authority")
    print(WARNING)


if __name__ == "__main__": main()
