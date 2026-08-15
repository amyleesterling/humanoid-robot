"""Generate R264 connector- and datum-aware carrier mounting interface P0.2."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

import generate_hr_v0_bom_closure as bom_closure


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-DXL-CARRIER-MOUNT-IF-P0.2"
CID = "HR-V0-CONFIG-REC-P0.28"
ROUND = "R264"
DATE = "2026-08-12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/mechanical/hr-v0-dxl-carrier-mount-p0.2"
REL = ROOT / "release/hr-v0/dxl-carrier-mount-p0.2"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.27"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.28"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.28"
BOM = ROOT / "bom/bom.csv"
CLOSURE = ROOT / "bom/hr-v0-bom-closure.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
SOURCES = {
    "pcb": ROOT / "electrical/kicad/hr-v0-dxl-protection-carrier-p0.3/hr-v0-dxl-protection-carrier-p0.3.kicad_pcb",
    "panel": ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement/candidate-backplate-layout.csv",
    "placement": ROOT / "electrical/harness/hr-v0-dxl-protection-carrier-harness-p0.2/placement-candidate.csv",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def warned(rows):
    return [{**row, "warning": WARNING} for row in rows]


def manifest(directory: Path) -> None:
    files = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], [
        {"path": p.relative_to(directory).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in files
    ])


def data_rows():
    source_rows = [
        {"source_id":"SRC-01","organization":"Project Button","document":SOURCES["pcb"].relative_to(ROOT).as_posix(),"revision_or_date":"P0.3; repository hash recorded 2026-08-12","url":"repository-local","controlled_fact":"100 x 60 mm PCB candidate; local mounting centers (5,5), (95,5), (5,55), (95,55); JIN1 (8,30); JOUT1 (92,30); 1.6 mm board thickness candidate","not_proved":"fabricated-board tolerances, received dimensions, populated height, connector sweep or fitness"},
        {"source_id":"SRC-02","organization":"Project Button","document":SOURCES["panel"].relative_to(ROOT).as_posix(),"revision_or_date":"P0.7; repository hash recorded 2026-08-12","url":"repository-local","controlled_fact":"533.4 x 685.8 mm panel coordinate system and current component/duct envelopes","not_proved":"received panel dimensions, installed depth or fabrication tolerance"},
        {"source_id":"SRC-03","organization":"Project Button","document":SOURCES["placement"].relative_to(ROOT).as_posix(),"revision_or_date":"R263 P0.2; repository hash recorded 2026-08-12","url":"repository-local","controlled_fact":"three 60 x 100 mm, 90-degree planning envelopes at x=438 and y=300/410/520","not_proved":"physical fit, drilling coordinates, connector service or thermal suitability"},
        {"source_id":"SRC-04","organization":"Hammond Manufacturing","document":"18P2721 product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.hammfg.com/part/18P2721","controlled_fact":"27 x 21 inch white steel inner-panel identity","not_proved":"received dimensions or installed panel-to-cover/rear clearance"},
        {"source_id":"SRC-05","organization":"Hammond Manufacturing","document":"18P2721 drawing","revision_or_date":"drawing dated 2020-02-07; accessed 2026-08-12","url":"https://www.hammfg.com/files/parts/pdf/18P2721.pdf","controlled_fact":"533.4 x 685.8 mm panel; 2.54 mm nominal thickness; 19.05 mm flange","not_proved":"installed clearance inside the selected enclosure"},
        {"source_id":"SRC-06","organization":"Hammond Manufacturing","document":"PJ302410RT product page and drawing","revision_or_date":"drawing issue 2014-06-13; live page accessed 2026-08-12","url":"https://www.hammfg.com/files/parts/pdf/PJ302410RT.pdf","controlled_fact":"762 x 610 x 257 mm external enclosure; drawing identifies optional 18P2721-size panel and nominal construction","not_proved":"usable internal component clearance with received panel, bosses, door and wiring"},
        {"source_id":"SRC-07","organization":"JST Mfg. Co.","document":"VH series eVH catalog","revision_or_date":"current retrieved catalog; accessed 2026-08-12","url":"https://www.jst-mfg.com/product/pdf/eng/eVH.pdf","controlled_fact":"3.96 mm pitch; B2P-VH top-entry header; catalog mounting height 16.5 mm and depth 10.5 mm","not_proved":"mated housing, contact, conductor, strain relief, bend or service envelope in this installation"},
        {"source_id":"SRC-08","organization":"Essentra Components","document":"TNM3-6.5-10-1 product page","revision_or_date":"no printed revision; accessed 2026-08-09; live US fetch unavailable 2026-08-12","url":"https://www.essentracomponents.com/en-us/p/pcb-standoffs-round-metric-threaded-insulator-nylon-brass/tnm3-6-5-10-1","controlled_fact":"held M3 female/female, 10 mm long, 6.5 mm body, 6 mm thread-depth candidate from prior controlled record","not_proved":"current supply status, received identity, tolerance, material/application or load suitability"},
        {"source_id":"SRC-09","organization":"Essentra Components","document":"0120070000VR product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.essentracomponents.com/en-gb/p/machine-screws-pan/0120070000vr","controlled_fact":"legacy nylon M3 x 0.5 x 6 mm geometry; official page identifies NSE-1580-M3-6 as replacement","not_proved":"received replacement equivalence, availability, tolerance, torque, creep or application suitability"},
        {"source_id":"SRC-10","organization":"Belden","document":"9918 product data sheet","revision_or_date":"Rev 0.515 dated 2026-02-20; accessed 2026-08-12","url":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/9918","controlled_fact":"18 AWG, 2.0 mm nominal OD and 20 mm minimum stationary/installation bend radius","not_proved":"installed route, bundling, support, temperature, fault or connector sweep"},
    ]
    transforms = [{"transform_id":"XF-01","source_frame":"P0.3 PCB local: x right, y down","target_frame":"P0.7 panel: x right, y down","rotation_deg":90,"equations":"x_panel = x0 + (60 - y_board); y_panel = y0 + x_board","board_envelope_mm":"100 x 60","panel_envelope_mm":"60 x 100","status":"DERIVED COORDINATE TRANSFORM - DO NOT DRILL"}]
    placements = [("LIM1","J1 shoulder",438.0,300.0),("LIM2","J2 elbow",438.0,410.0),("LIM3","G1 gripper",438.0,520.0)]
    local_holes = [("MH1",5.0,5.0),("MH2",95.0,5.0),("MH3",5.0,55.0),("MH4",95.0,55.0)]
    holes=[]
    anchors=[]
    for ref,axis,x0,y0 in placements:
        for hole,bx,by in local_holes:
            holes.append({"carrier":ref,"axis":axis,"hole":hole,"board_x_mm":bx,"board_y_mm":by,"panel_center_x_mm":x0+60-by,"panel_center_y_mm":y0+bx,"pcb_hole":"3.2 mm NPTH source candidate","panel_hole":"SELECTION REQUIRED","state":"CENTER DATUM ONLY - DO NOT MARK OR DRILL"})
        for connector,bx,by,role in (("JIN1",8.0,30.0,"protected branch input"),("JOUT1",92.0,30.0,"limited output to DXL star")):
            anchors.append({"carrier":ref,"axis":axis,"connector":connector,"role":role,"board_x_mm":bx,"board_y_mm":by,"panel_anchor_x_mm":x0+60-by,"panel_anchor_y_mm":y0+bx,"header_style":"B2P-VH TOP ENTRY","wire_exit_direction":"NOT DEFINED BY POINT DATUM; PHYSICAL SWEEP REQUIRED","state":"ANCHOR ONLY - NOT A ROUTE OR CUT LENGTH"})
    clearance = [
        {"screen_id":"CLR-01","objects":"all carrier left edges to WD2 right edge","nominal_clearance_mm":14.2,"basis":"438.0 - 423.8","result":"POSITIVE PLANAR GAP; CONNECTOR/WIRE SWEEP OPEN"},
        {"screen_id":"CLR-02","objects":"all carrier right edges to panel right edge","nominal_clearance_mm":35.4,"basis":"533.4 - 498.0","result":"POSITIVE PLANAR GAP; ENCLOSURE WALL/SERVICE OPEN"},
        {"screen_id":"CLR-03","objects":"LIM1 top to compute-retention bottom","nominal_clearance_mm":24.6,"basis":"300.0 - 275.4","result":"POSITIVE PLANAR GAP; THREE-DIMENSIONAL FIT OPEN"},
        {"screen_id":"CLR-04","objects":"LIM1 to LIM2","nominal_clearance_mm":10.0,"basis":"410.0 - 400.0","result":"POSITIVE PLANAR GAP; CONNECTOR/WIRE SWEEP OPEN"},
        {"screen_id":"CLR-05","objects":"LIM2 to LIM3","nominal_clearance_mm":10.0,"basis":"520.0 - 510.0","result":"POSITIVE PLANAR GAP; CONNECTOR/WIRE SWEEP OPEN"},
        {"screen_id":"CLR-06","objects":"LIM3 bottom to WD4 top","nominal_clearance_mm":5.0,"basis":"625.0 - 620.0","result":"SMALL POSITIVE PLANAR GAP; NO ROUTE OR SERVICE CLAIM"},
        {"screen_id":"CLR-07","objects":"carrier connector anchors to WD2 centerline","nominal_clearance_mm":64.2,"basis":"468.0 - 403.8","result":"POINT-TO-LINE SCREEN ONLY; TOP-ENTRY SWEEP NOT MODELED"},
        {"screen_id":"CLR-08","objects":"LIM3 JOUT1 anchor to WD4 top","nominal_clearance_mm":13.0,"basis":"625.0 - 612.0","result":"POINT SCREEN ONLY; DIRECT DOWNWARD ROUTE NOT INFERRED"},
        {"screen_id":"CLR-09","objects":"Belden 9918 bend envelope","nominal_clearance_mm":"SELECTION REQUIRED","basis":"20 mm minimum bend radius must be swept with exact connector/contact/support geometry","result":"OPEN - RECEIVED FULL-SCALE SWEEP REQUIRED"},
    ]
    stack = [
        {"screen_id":"STK-01","quantity":"PCB-side nominal thread engagement","inputs":"6.0 screw - 1.6 PCB","result_mm":4.4,"disposition":"SCREEN PASS; TOLERANCES/REPLACEMENT IDENTITY OPEN"},
        {"screen_id":"STK-02","quantity":"PCB-side bottom-out reserve","inputs":"6.0 thread depth - 4.4 engagement","result_mm":1.6,"disposition":"SCREEN PASS; RECEIVED TOLERANCES OPEN"},
        {"screen_id":"STK-03","quantity":"panel-side nominal thread engagement","inputs":"6.0 screw - 2.54 panel","result_mm":3.46,"disposition":"SCREEN PASS; COATING/TOLERANCES OPEN"},
        {"screen_id":"STK-04","quantity":"panel-side bottom-out reserve","inputs":"6.0 thread depth - 3.46 engagement","result_mm":2.54,"disposition":"SCREEN PASS; RECEIVED TOLERANCES OPEN"},
        {"screen_id":"STK-05","quantity":"PCB top above panel face","inputs":"10.0 standoff + 1.6 PCB","result_mm":11.6,"disposition":"SCREEN ONLY"},
        {"screen_id":"STK-06","quantity":"mounting screw top above panel face","inputs":"10.0 + 1.6 + 1.8","result_mm":13.4,"disposition":"EXCLUDES COMPONENTS/CONNECTORS"},
        {"screen_id":"STK-07","quantity":"catalog connector top above panel face candidate","inputs":"10.0 standoff + 16.5 catalog mounting height","result_mm":26.5,"disposition":"CATALOG SCREEN ONLY; MATING/WIRE SWEEP AND DIMENSION DATUM MUST BE VERIFIED"},
        {"screen_id":"STK-08","quantity":"nominal rear flange screen","inputs":"19.05 flange - 1.8 screw head","result_mm":17.25,"disposition":"NOT INSTALLED REAR CLEARANCE"},
        {"screen_id":"STK-09","quantity":"standoff body board-edge margin","inputs":"5.0 - 3.25","result_mm":1.75,"disposition":"SCREEN PASS; TOLERANCES/LOAD OPEN"},
        {"screen_id":"STK-10","quantity":"screw head board-edge margin","inputs":"5.0 - 2.95","result_mm":2.05,"disposition":"SCREEN PASS; RECEIVED REPLACEMENT GEOMETRY OPEN"},
    ]
    route = []
    for row in anchors:
        route.append({"carrier":row["carrier"],"connector":row["connector"],"anchor":"({:.1f},{:.1f})".format(row["panel_anchor_x_mm"],row["panel_anchor_y_mm"]),"nearest_planning_zone":"WD2 centerline x=403.8 mm","nominal_point_to_centerline_mm":64.2,"minimum_bend_radius_mm":20,"cut_length_mm":"SELECTION REQUIRED","route_state":"ANCHOR SCREEN ONLY; HEADER IS TOP ENTRY; NO EXIT VECTOR OR DUCT ENTRY INFERRED"})
    mockup = [
        {"item_id":"MOCK-01","article":"three nonconductive 60 x 100 mm carrier envelopes","quantity":3,"required_features":"four hole-center marks and two connector-anchor marks per article","physical_action":"loose placement only; no adhesive, punch or drill","result":"NOT EXECUTED"},
        {"item_id":"MOCK-02","article":"26.5 mm catalog-height connector gauges","quantity":6,"required_features":"clearly marked as catalog screen, not a validated mated envelope","physical_action":"fit/sweep with enclosure isolated and empty","result":"NOT EXECUTED"},
        {"item_id":"MOCK-03","article":"20 mm radius bend gauges","quantity":6,"required_features":"Belden stationary/installation radius only","physical_action":"sweep candidate wires without cutting production conductors","result":"NOT EXECUTED"},
        {"item_id":"MOCK-04","article":"1:1 coordinate overlay","quantity":1,"required_features":"scale bars in both axes and DO NOT DRILL warning","physical_action":"verify printer scale against calibrated rule; lay loose on unmodified panel","result":"NOT EXECUTED"},
    ]
    metrology_actions = [
        "Record enclosure and panel manufacturer, part, lot and received condition",
        "Measure received panel width, height, thickness, flange and flatness",
        "Measure installed panel-to-wall/boss rear gaps at all twelve candidate fasteners",
        "Measure closed-cover clearance at all three candidate carrier regions",
        "Record each carrier revision/serial and measure outline, thickness, holes and datums",
        "Record received standoff identity, body, length and both thread depths",
        "Record received replacement screw identity, length, head and material declaration",
        "Verify 1:1 overlay scale in both axes before loose placement",
        "Place three inert board envelopes; do not mark or modify the panel",
        "Place connector-height gauges and close the unpowered empty enclosure",
        "Mate exact JST housings/contacts and sweep actual wire samples without production cuts",
        "Verify 20 mm bend-radius, duct entry, strain relief and service-tool access",
        "Photograph front/rear/cover/service views with calibrated scales",
        "Reconcile deviations and obtain qualified review before separate drilling authority",
    ]
    metrology = [{"item_id":f"MET-{i:02d}","unpowered_no_drill_action":a,"required_record":"configuration, instrument ID/calibration, measured value, photo/evidence URI, operator and reviewer","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":""} for i,a in enumerate(metrology_actions,1)]
    hold_text = [
        "received panel and enclosure identity, dimensions, flatness and installed offsets",
        "received carrier outline, thickness, populated height, hole and connector datums",
        "current TNM3-6.5-10-1 supply identity and received dimensions/material",
        "NSE-1580-M3-6 replacement identity, received dimensions and legacy-equivalence disposition",
        "panel-hole diameter, tolerance, positional tolerance, burr and coating process",
        "mounting torque, driver, locking/reuse and witness-mark rules",
        "static pull, shear, creep, vibration and transport acceptance loads",
        "temperature, fire and creep suitability of the complete mounting stack",
        "mated JST/contact/wire/support three-dimensional envelope",
        "installed cover, rear, wall, boss and service-tool clearance",
        "six duct-entry vectors, supports, service loops and measured route paths",
        "all twelve production cut lengths and termination allowances",
        "thermal/airflow evidence around the three populated carrier assemblies",
        "qualified mechanical, electrical, enclosure and coating/bonding review",
        "separate written authority for each procurement, drilling and physical operation",
    ]
    holds=[{"hold_id":f"H-{i:02d}","scope":t,"state":"OPEN","closure_evidence":"configuration-bound received measurement, calculation/test and qualified signoff"} for i,t in enumerate(hold_text,1)]
    criteria = [
        "Coordinate transform is independently reproduced from the exact P0.3 PCB and R263 placement sources",
        "All twelve derived panel hole centers match the transformed four-hole PCB pattern",
        "All six connector anchors match transformed JIN1/JOUT1 PCB datums",
        "No coordinate or SVG is used as a drilling template or work instruction",
        "Received panel and all three received boards match controlled identities and dimensions",
        "Received screw identity resolves the manufacturer replacement without assumed equivalence",
        "Every thread has positive engagement and bottom-out reserve under accepted tolerances",
        "Every hole diameter, position, coating and deburr requirement is qualified before drilling",
        "All front, rear and closed-cover clearances are measured and positive to accepted limits",
        "Exact mated JST/contact/wire envelopes clear boards, duct, cover and service tools",
        "All six wire paths preserve the 20 mm minimum bend radius and accepted strain relief",
        "All twelve cut lengths derive from accepted installed paths rather than anchor distances",
        "Mounting stack passes accepted pull, shear, creep, vibration and transport tests",
        "Populated carriers pass accepted thermal and airflow tests at accepted duty and ambient",
        "Qualified mechanical review accepts mounting, access, tolerance and load evidence",
        "Qualified electrical/enclosure review accepts separation, insulation, heat and bonding interfaces",
        "A distinct written authorization releases only the next named physical operation",
        "No safety credit, powered-test authority or energization authority is inferred",
    ]
    acceptance=[{"acceptance_id":f"ACC-{i:02d}","criterion":t,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""} for i,t in enumerate(criteria,1)]
    hardware = [
        {"item_id":"MNT-01","role":"female/female insulating standoff","manufacturer":"Essentra Components","mpn":"TNM3-6.5-10-1","quantity":12,"state":"EXACT CANDIDATE HOLD","remaining_evidence":"current supply/received identity, dimensions, material, temperature/fire/creep, torque and load proof"},
        {"item_id":"MNT-02","role":"PCB-side and panel-side screw","manufacturer":"Essentra Components","mpn":"NSE-1580-M3-6; official replacement shown for legacy 0120070000VR","quantity":24,"state":"MANUFACTURER REPLACEMENT CANDIDATE HOLD","remaining_evidence":"current order route, received identity/dimensions, equivalence disposition, torque, creep and load proof"},
        {"item_id":"MNT-03","role":"backplate clearance holes","manufacturer":"SELECTION REQUIRED","mpn":"SELECTION REQUIRED","quantity":12,"state":"SELECTION REQUIRED - DO NOT DRILL","remaining_evidence":"diameter, tolerance, position, burr/coating process, received template fit and qualified approval"},
    ]
    return {
        "source-register.csv":(["source_id","organization","document","revision_or_date","url","controlled_fact","not_proved","warning"],warned(source_rows)),
        "transform-definition.csv":(["transform_id","source_frame","target_frame","rotation_deg","equations","board_envelope_mm","panel_envelope_mm","status","warning"],warned(transforms)),
        "hole-coordinate-register.csv":(["carrier","axis","hole","board_x_mm","board_y_mm","panel_center_x_mm","panel_center_y_mm","pcb_hole","panel_hole","state","warning"],warned(holes)),
        "connector-anchor-register.csv":(["carrier","axis","connector","role","board_x_mm","board_y_mm","panel_anchor_x_mm","panel_anchor_y_mm","header_style","wire_exit_direction","state","warning"],warned(anchors)),
        "clearance-screen.csv":(["screen_id","objects","nominal_clearance_mm","basis","result","warning"],warned(clearance)),
        "depth-stack-screen.csv":(["screen_id","quantity","inputs","result_mm","disposition","warning"],warned(stack)),
        "route-anchor-screen.csv":(["carrier","connector","anchor","nearest_planning_zone","nominal_point_to_centerline_mm","minimum_bend_radius_mm","cut_length_mm","route_state","warning"],warned(route)),
        "inert-mockup-definition.csv":(["item_id","article","quantity","required_features","physical_action","result","warning"],warned(mockup)),
        "hardware-bom.csv":(["item_id","role","manufacturer","mpn","quantity","state","remaining_evidence","warning"],warned(hardware)),
        "no-drill-metrology-form.csv":(["item_id","unpowered_no_drill_action","required_record","execution_state","result","evidence_uri","warning"],warned(metrology)),
        "open-holds.csv":(["hold_id","scope","state","closure_evidence","warning"],warned(holds)),
        "acceptance-matrix.csv":(["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"],warned(acceptance)),
    }


def panel_svg() -> str:
    boards=[]
    for ref,y in (("LIM1",300),("LIM2",410),("LIM3",520)):
        holes=[(493,y+5),(493,y+95),(443,y+5),(443,y+95)]
        circles="".join(f"<circle cx='{x}' cy='{yy}' r='4' class='hole'/>" for x,yy in holes)
        boards.append(f"<g data-carrier='{ref}'><rect x='438' y='{y}' width='60' height='100' rx='4' class='board'/>{circles}<circle cx='468' cy='{y+8}' r='5' class='jin'/><circle cx='468' cy='{y+92}' r='5' class='jout'/><text x='448' y='{y+48}' class='label'>{ref}</text><text x='448' y='{y+68}' class='small'>90 deg</text></g>")
    return """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 950 760' role='img' aria-labelledby='title desc'><title id='title'>Carrier datum overlay</title><desc id='desc'>P0.7 nominal backplate with three rotated carrier envelopes, mounting centers and connector anchors.</desc><style>text{font-family:system-ui,sans-serif;fill:#092f57}.title{font-size:24px;font-weight:800}.note{font-size:17px;font-weight:700}.label{font-size:18px;font-weight:800}.small{font-size:14px}.panel{fill:#f8fbfe;stroke:#092f57;stroke-width:3}.duct{fill:#d8e7f2;stroke:#396987}.board{fill:#dff3ff;stroke:#075ea8;stroke-width:3}.hole{fill:white;stroke:#092f57;stroke-width:2}.jin{fill:#f3bd28;stroke:#092f57;stroke-width:2}.jout{fill:#ff8a65;stroke:#092f57;stroke-width:2}</style><rect width='950' height='760' fill='white'/><text x='35' y='35' class='title'>P0.7 carrier datum screen - NOT A DRILL TEMPLATE</text><g transform='translate(40 55)'><rect x='0' y='0' width='533.4' height='685.8' class='panel'/><rect x='383.8' y='0' width='40' height='685.8' class='duct'/><text x='387' y='30' class='small'>WD2</text><rect x='54' y='625' width='323.8' height='40' class='duct'/><text x='65' y='652' class='small'>WD4</text>""" + "".join(boards) + """</g><g transform='translate(605 100)'><circle cx='0' cy='0' r='6' class='hole'/><text x='14' y='6' class='note'>hole datum</text><circle cx='0' cy='45' r='7' class='jin'/><text x='14' y='51' class='note'>JIN1</text><circle cx='0' cy='90' r='7' class='jout'/><text x='14' y='96' class='note'>JOUT1</text></g><text x='605' y='250' class='note'>Coordinates are</text><text x='605' y='275' class='note'>nominal centers.</text><text x='605' y='320' class='note'>No hole diameter.</text><text x='605' y='345' class='note'>No wire exit.</text><text x='605' y='390' class='note'>Measure received</text><text x='605' y='415' class='note'>parts first.</text></svg>"""


def table(title, rows, fields):
    head="".join(f"<th>{html.escape(f.replace('_',' ').title())}</th>" for f in fields)
    body="".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(f,'')))}</td>" for f in fields)+"</tr>" for r in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(data):
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),white);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,68px);line-height:1.08;color:var(--blue)}}h2{{font-size:clamp(24px,2.4vw,36px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:850}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin:24px 0}}.card,section{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}object{{width:100%;min-height:680px;border:0}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{padding:11px;text-align:left;vertical-align:top;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:white}}a{{font-size:16px;font-weight:750;color:#075ea8}}@media(max-width:700px){{main{{padding:12px}}object{{min-height:520px}}table{{min-width:820px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Exact datums. Still no holes.</h1><p>R264 maps the real P0.3 board holes and connector centers into the current rotated P0.7 panel candidates. It also exposes the remaining three-dimensional evidence instead of treating a rectangle as physical fit.</p></header><main><div class='cards'><article class='card'><div class='big'>12</div><strong>derived mounting centers</strong></article><article class='card'><div class='big'>6</div><strong>connector anchors</strong></article><article class='card'><div class='big'>0</div><strong>released hole diameters</strong></article><article class='card'><div class='big'>0</div><strong>executed fit checks</strong></article></div><section><h2>Panel datum screen</h2><object type='image/svg+xml' data='panel-datum-screen.svg'>Nominal panel datum screen.</object></section>{table('Hole centers — do not drill',data['hole-coordinate-register.csv'][1],['carrier','hole','panel_center_x_mm','panel_center_y_mm','panel_hole','state'])}{table('Connector anchors — not wire exits',data['connector-anchor-register.csv'][1],['carrier','connector','panel_anchor_x_mm','panel_anchor_y_mm','header_style','wire_exit_direction'])}{table('Clearance screens',data['clearance-screen.csv'][1],['screen_id','objects','nominal_clearance_mm','basis','result'])}{table('Evidence still open',data['open-holds.csv'][1],['hold_id','scope','state','closure_evidence'])}<section><h2>Controlled files</h2><p><a href='transform-definition.csv'>transform</a> · <a href='depth-stack-screen.csv'>depth stack</a> · <a href='route-anchor-screen.csv'>route anchors</a> · <a href='inert-mockup-definition.csv'>inert mock-up</a> · <a href='no-drill-metrology-form.csv'>metrology form</a> · <a href='acceptance-matrix.csv'>acceptance</a></p></section><p class='warn'>{WARNING}</p></main></body></html>"""


def update_bom():
    rows,fields=read_csv(BOM); by={r["item_id"]:r for r in rows}
    by["BOM-091"].update(manufacturer_part_number="NSE-1580-M3-6; official Essentra replacement shown for legacy 0120070000VR",selection_basis="R264 records the manufacturer page's replacement relation without assuming received equivalence. Twenty-four nylon M3 x 0.5 x 6 mm screw candidates remain held pending current order route, received identity/dimensions/material, tolerance stack, panel hole/coating, torque/locking/reuse, creep, pull/shear/vibration, rear clearance and qualified review. No procurement, drilling or mounting authority is issued.")
    by["BOM-107"].update(manufacturer_part_number="4 x TNM3-6.5-10-1; 8 x NSE-1580-M3-6 current manufacturer replacement candidate for legacy 0120070000VR",selection_basis="R264 records the current official replacement relation. Current order route, received replacement identity/dimensions, equivalence, tolerances, torque, creep, load, coating interface, panel-hole process and physical proof remain open. No drilling or procurement release.")
    write_csv(BOM,fields,rows)
    write_csv(CLOSURE,list(bom_closure.FIELDS),[{"item_id":r["item_id"],**bom_closure.classification(r)} for r in rows])


def update_release():
    data=json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","bill_of_materials","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]): product.setdefault("supporting_identifiers",[]).append(value)
            product["configuration_reconciliation"]=CID
            product["dxl_carrier_mount"]=ID
        if product.get("domain")=="electrical":
            product["dxl_carrier_mount_summary"]="12 transformed hole centers / 6 connector anchors / 90-degree P0.7 placement / current screw replacement relation / depth, sweep, holes, routes and physical evidence open"
    RELEASE.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def update_config(data):
    shutil.copytree(CFG0,CFG)
    current,fields=read_csv(CFG/"current-configuration-map.csv")
    row=next(r for r in current if r["record_id"]=="CFG-06")
    row.update(identifier=ID,source_path="release/hr-v0/dxl-carrier-mount-p0.2/package-status.json",configuration_state="CURRENT DATUM CANDIDATE",release_boundary="exact transformed hole/connector datums; no hole diameter, route, physical fit, drilling or work authority")
    write_csv(CFG/"current-configuration-map.csv",fields,current)
    supers,fields=read_csv(CFG/"supersession-map.csv")
    supers.extend([
        {"record_id":"SUP-41","prior_identifier":"HR-V0-DXL-CARRIER-MOUNT-IF-P0.1","current_or_required_successor":ID,"disposition":"SUPERSEDED: stale P0.6 placement replaced by P0.7 rotated datum mapping; historical evidence only","use_authorized":"NO","warning":WARNING},
        {"record_id":"SUP-42","prior_identifier":"HR-V0-CONFIG-REC-P0.27","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R264 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING},
    ])
    write_csv(CFG/"supersession-map.csv",fields,supers)
    bm,fields=read_csv(CFG/"bom-integration-map.csv")
    for r in bm:
        if r["item_id"] in {"BOM-090","BOM-091"}: r["bound_identifier"]=ID
    write_csv(CFG/"bom-integration-map.csv",fields,bm)
    gates,fields=read_csv(CFG/"gate-impact.csv")
    for r in gates:
        if r["gate_id"] in {"EG-002","EG-003","EG-014","EG-018","EG-020"}:
            r["evidence_added"] += f"; {ID} transformed hole/connector datums and inert fit-check contract"
            r["remaining_evidence"] += "; received three-dimensional fit; hole/process release; route/cut proof; load/thermal tests; qualified acceptance and separate authority"
    write_csv(CFG/"gate-impact.csv",fields,gates)
    holds,fields=read_csv(CFG/"open-holds.csv")
    for i,r in enumerate(data["open-holds.csv"][1],186): holds.append({"hold_id":f"HOLD-{i:03d}","hold":f"{ID}: {r['scope']}","state":"OPEN","closure_evidence":r["closure_evidence"],"warning":WARNING})
    write_csv(CFG/"open-holds.csv",fields,holds)
    acc,fields=read_csv(CFG/"acceptance-matrix.csv")
    for i,r in enumerate(data["acceptance-matrix.csv"][1],235): acc.append({"acceptance_id":f"ACC-{i:03d}","criterion":f"{ID}: {r['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"acceptance-matrix.csv",fields,acc)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"system_bom_groups":109,"current_records":45,"supersession_records":42,"bom_integration_records":30,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(acc),"dxl_carrier_mount":ID})
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR264 adds {ID}: twelve transformed hole centers, six connector anchors, current screw replacement disposition and an inert no-drill fit contract. {len(holds)} holds and {len(acc)} blank acceptances remain.\n",encoding="utf-8")
    (CFG/"index.html").write_text((REL/"index.html").read_text(encoding="utf-8"),encoding="utf-8")
    hashes=[]
    for r in current:
        path=ROOT/r["source_path"]
        hashes.append({"source_path":r["source_path"],"sha256":sha(path),"role":r["role"],"warning":WARNING})
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes)
    manifest(CFG); shutil.copytree(CFG,CFGR); manifest(CFGR)


def docs():
    (ROOT/"docs/hr-v0-dxl-carrier-mount-p0.2.md").write_text(f"""# HR-V0 DXL carrier mounting interface P0.2

> **{WARNING}**

R264 replaces the stale P0.6 mounting centers with exact coordinate transforms for the R263 rotated P0.7 planning candidates. The P0.3 PCB local datums map to twelve panel hole centers and six JIN1/JOUT1 connector anchors. The transform is `x_panel = x0 + (60 - y_board); y_panel = y0 + x_board` in the controlled y-down coordinate frames.

These are datums, not fabrication instructions. Panel-hole diameter, tolerance, coating/deburr process, received dimensions, connector and wire sweep, duct entry, cut length, component height, cover/rear clearance, torque, load, creep, vibration, thermal behavior and qualified acceptance remain open. The board-to-WD2 gap is 14.2 mm and the LIM3-to-WD4 gap is only 5.0 mm nominal; neither proves usable three-dimensional service space.

Essentra's current official page identifies `NSE-1580-M3-6` as the replacement for legacy `0120070000VR`. R264 records that relationship as a held candidate only. Current order route, received identity, dimensional equivalence and application evidence are required.

Interactive guide: [release package](../release/hr-v0/dxl-carrier-mount-p0.2/index.html).
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r264-validation-record.md").write_text(f"""# R264 validation record

> **{WARNING}**

Identifier: `{ID}`

Configuration: `{CID}`

Generation reproduces twelve hole centers and six connector anchors from the hashed P0.3 PCB, P0.7 panel and R263 placement sources. All 15 holds and 18 acceptance rows are open; all 14 metrology rows are unexecuted. The SVG is explicitly not a drill template. No physical article, measurement, drilling, procurement, connection, powered test, motion or energization occurred.

Automated validation result: the dedicated checker passes; 203 non-KiCad repository checks pass; 19 native board checks pass under KiCad 10 Python; generator/checker syntax compilation passes. Desktop browser QA found and corrected one clipped SVG legend, then confirmed the corrected diagram and no page-level horizontal overflow. Functional HTML text is 16 px body, 14 px tables and 14 px or larger in the SVG. The available viewport override did not change the browser's reported 1280 px width, so narrow-screen visual QA is not claimed; the responsive rule and horizontal table reflow are statically present. The staged release manifest passes with 6,276 package files.

No Sol R12 blocker receives qualified closure.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r264-independent-review-request.md").write_text(f"""# R264 independent review request

> **{WARNING}**

Independently reproduce `{ID}` from the exact hashed sources. Verify the 90-degree transform, all twelve hole centers, all six connector anchors, each planar/depth screen, the top-entry JST interpretation, Belden 20 mm bend-radius boundary and Essentra replacement relationship. Confirm that no hole diameter, wire-exit vector, route, cut length, received clearance, load, thermal result, drilling or work authority is implied. Review the inert mock-up and metrology contracts for completeness and confirm that every acceptance remains blank.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r264-status.md").write_text(f"""# Sol R12 status after R264

R264 responds narrowly to Sol's buildability findings by adding connector- and hole-aware carrier datums plus an executable inert fit-check contract. No Sol R12 blocker closes: no received article, executed measurement, fabrication drawing, physical test, qualified review or authority exists.

The Sol-reported baseline remains historical independent R12: 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62/62 reviewed requirements draft; 106 historical electrical selections unresolved; zero approved executed verification evidence. HR-V0 remains not build-ready and energization remains prohibited.

> **{WARNING}**
""",encoding="utf-8")


def update_narrative():
    readme=ROOT/"README.md"; text=readme.read_text(encoding="utf-8")
    marker="- [R263 carrier power-harness and panel-placement correction P0.2]"
    insert="- [R264 `HR-V0-DXL-CARRIER-MOUNT-IF-P0.2` connector- and datum-aware carrier mounting](docs/hr-v0-dxl-carrier-mount-p0.2.md)\n- [Interactive R264 no-drill mounting guide](release/hr-v0/dxl-carrier-mount-p0.2/index.html)\n- [Interactive configuration reconciliation P0.28](release/hr-v0/configuration-reconciliation-p0.28/index.html)\n- [R264 independent review request](docs/reviews/2026-08-12-r264-independent-review-request.md)\n- [Sol R12 status after R264](docs/reviews/2026-08-12-sol-r12-post-r264-status.md)\n"
    if insert not in text: text=text.replace(marker,insert+marker)
    old="Two hundred sixty-three rounds are complete: R01-R263."
    new="Two hundred sixty-four rounds are complete: R01-R264."
    text=text.replace(old,new)
    text=text.replace("R263 corrects the six carrier power-harness identities and minimum population", "R264 transforms the current rotated carrier candidates into twelve exact hole-center datums and six connector anchors while retaining a strict no-drill boundary. R263 corrected the six carrier power-harness identities and minimum population")
    readme.write_text(text,encoding="utf-8")
    hand=ROOT/"docs/handoff-current.md"; h=hand.read_text(encoding="utf-8")
    block=f"R264 carrier mounting-datum correction: **`{ID}` maps the P0.3 board through the R263 90-degree P0.7 placements into twelve exact nominal hole centers and six JIN1/JOUT1 connector anchors. It records the current Essentra `NSE-1580-M3-6` replacement relationship as held, screens 14.2 mm to WD2 and only 5.0 mm from LIM3 to WD4, and defines a fourteen-step inert no-drill metrology contract. Hole diameter/process, received depth/sweep, routes/cuts, torque/load/thermal evidence, qualified review and all work authority remain open. `{CID}` carries 45 current records, 42 supersessions, 30 BOM integrations, 200 holds and 252 blank acceptances. No Sol R12 blocker closes and energization remains prohibited.**\n\n"
    if not h.startswith(block): h=block+h
    hand.write_text(h,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; l=ledger.read_text(encoding="utf-8")
    row=f"| R264 | 2026-08-12 | Connector- and datum-aware carrier mounting correction | Codex mechanical/electrical/configuration pass; not independent and no physical work | Sol R12 buildability findings, P0.3 carrier, R263 rotated placement, P0.7 panel and current Hammond/JST/Essentra/Belden sources | Issued `{ID}` with twelve transformed hole-center datums, six connector anchors, ten depth-stack screens, nine clearance screens and a fourteen-step inert no-drill metrology form. Recorded the current Essentra replacement relation without approving equivalence. Fifteen holds and eighteen blank acceptances remain; no hole diameter, route, cut, received fit, load/thermal result, qualified approval or authority exists. No Sol blocker closes. | `docs/hr-v0-dxl-carrier-mount-p0.2.md`; `electrical/mechanical/hr-v0-dxl-carrier-mount-p0.2/`; `release/hr-v0/dxl-carrier-mount-p0.2/`; `configuration/hr-v0-config-reconciliation-p0.28/`; `docs/reviews/2026-08-12-sol-r12-post-r264-status.md` |\n"
    footer="Two hundred sixty-three rounds are complete (R01-R263)."
    if row not in l:
        pos=l.find("\n\n",l.find("| R263 |")); l=l[:pos+2]+row+l[pos+2:]
    l=l.replace(footer,"Two hundred sixty-four rounds are complete (R01-R264).")
    l=l.replace("R263 corrects the carrier power-harness undercount", "R264 adds exact transformed carrier hole/connector datums and a no-drill physical-fit contract; R263 corrected the carrier power-harness undercount")
    ledger.write_text(l,encoding="utf-8")


def main():
    for path in [*SOURCES.values(),CFG0,BOM,CLOSURE,RELEASE]:
        if not path.exists(): raise FileNotFoundError(path)
    for directory in (ENG,REL,CFG,CFGR):
        if directory.exists(): shutil.rmtree(directory)
    data=data_rows(); ENG.mkdir(parents=True)
    for name,(fields,rows) in data.items(): write_csv(ENG/name,fields,rows)
    (ENG/"panel-datum-screen.svg").write_text(panel_svg(),encoding="utf-8")
    status={"identifier":ID,"round":ROUND,"date":DATE,"carrier_count":3,"mounting_hole_centers":12,"connector_anchors":6,"stack_screens":10,"clearance_screens":9,"open_holds":15,"metrology_rows":14,"acceptance_rows":18,"all_acceptance_executed":False,"panel_hole_diameter_selected":False,"wire_exit_vectors_released":False,"route_or_cut_lengths_released":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"drilling_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"source_hashes":{k:sha(v) for k,v in SOURCES.items()},"warning":WARNING}
    (ENG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (ENG/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR264 defines exact nominal panel datums and an inert no-drill fit contract. It releases no hole, hardware, route, cut or physical work.\n",encoding="utf-8")
    manifest(ENG); shutil.copytree(ENG,REL)
    (REL/"index.html").write_text(guide(data),encoding="utf-8"); manifest(REL)
    update_bom(); update_release(); update_config(data); docs(); update_narrative()
    print(f"Generated {ID}: 12 hole centers / 6 connector anchors / 0 drilling authority")
    print(WARNING)


if __name__ == "__main__": main()
