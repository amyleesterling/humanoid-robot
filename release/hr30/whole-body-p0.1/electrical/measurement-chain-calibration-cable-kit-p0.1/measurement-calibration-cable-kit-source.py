#!/usr/bin/env python3
"""Generate the HR-30 measurement calibration cable and fault-adapter kit P0.1."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "measurement-chain-calibration-cable-kit-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
FIXTURE = WHOLE / "electrical" / "measurement-chain-calibration-fixture-p0.1"
CAD_PYTHON = ROOT.parent / ".venvs" / "hr-v0-cad" / "Scripts" / "python.exe"
DATE = "2026-08-19"
IDENTIFIER = "HR30-MEASUREMENT-CALIBRATION-CABLE-KIT-P0.1"
WARNING = "PRELIMINARY - UNBUILT OFF-ROBOT CALIBRATION CABLE AND FAULT-ADAPTER KIT - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, ROBOT CONNECTION, POWERED ROBOT TESTING, MOTION, WALKING OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, ROBOT CONNECTION, POWERED-ROBOT-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"

URLS = {
    "mueller": "https://www.muellerelectric.com/product_files/21/DS-BU-0061-M-%40.pdf",
    "mueller_list": "https://ww2.muellerelectric.com/wp-content/uploads/2025/10/Mueller-UKCA-and-CE-parts-101525.pdf",
    "alpha_cable": "https://www.alphawire.com/products/cable/alpha-essentials/tray-cable/5610b2201",
    "alpha_shrink": "https://www.alphawire.com/products/wire-management/heat-shrink-tubing/fit-221",
    "plug": "https://www.phoenixcontact.com/en-us/products/pcb-connector-mstb-25-2-st-508-1757019",
    "ferrule22": "https://www.phoenixcontact.com/en-us/products/ferrule-ai-034-8-tq-3203066",
    "ferrule18": "https://www.phoenixcontact.com/en-us/products/ferrule-ai-1-6-rd-3200742",
    "crimper": "https://www.phoenixcontact.com/en-us/products/crimping-pliers-crimpfox-centrus-10s-1213154",
    "tl930": "https://www.fluke.com/en-us/product/accessories/adapters/fluke-tl930",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name: str, records: list[dict[str, object]]) -> None:
    if not records:
        raise RuntimeError(f"empty register: {name}")
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def run(command: list[str]) -> None:
    cp = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if cp.returncode:
        raise RuntimeError(f"command failed {cp.returncode}: {' '.join(command)}\n{cp.stdout}\n{cp.stderr}")


def assemblies() -> list[dict[str, object]]:
    return [
        {"assembly_id":"CK-01","name":"isolated source lead pair","function":"Keysight output 2 or 3 to fixture JPS","construction":"two manufacturer-assembled Mueller 18 AWG silicone leads; factory tin-dipped ends removed and re-terminated","finished_length_mm":"975 target; record actual; 950 minimum","end_a":"BU-0061-M-39-2 red and -0 black shrouded 4 mm bananas","end_b":"one Phoenix 1757019, contact 1 red HI and contact 2 black LO","label_color":"WHITE body / RED HI / BLACK LO","maximum_use":"24 V DC candidate, 10 mA source-current-limit candidate","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-02","name":"normal transfer cable","function":"fixture JDUT to selected pod JIN","construction":"Alpha 5610B2201, both conductors populated straight through; shield and drain isolated at both ends","finished_length_mm":"300 +/-5 jacket span","end_a":"Phoenix 1757019 JDUT","end_b":"Phoenix 1757019 POD JIN","label_color":"BLUE - NORMAL ONLY","maximum_use":"24 V DC candidate, one disconnected chain","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-03","name":"reversed-polarity adapter","function":"controlled negative-response characterization","construction":"Alpha 5610B2201, contacts crossed; shield and drain isolated at both ends","finished_length_mm":"300 +/-5 jacket span","end_a":"Phoenix 1757019 JDUT","end_b":"Phoenix 1757019 POD JIN","label_color":"RED - REVERSE POLARITY","maximum_use":"24 V DC candidate only under CF-P10","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-04","name":"HI-open adapter","function":"controlled CAL_HI open characterization","construction":"Alpha 5610B2201; black LO conductor only; white conductor and shield/drain cut back and insulated","finished_length_mm":"300 +/-5 jacket span","end_a":"Phoenix 1757019 JDUT; contact 1 physically empty","end_b":"Phoenix 1757019 POD JIN; contact 1 physically empty","label_color":"ORANGE - HI OPEN","maximum_use":"24 V DC candidate only under CF-P11","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-05","name":"LO-open adapter","function":"controlled CAL_LO open characterization","construction":"Alpha 5610B2201; white HI conductor only; black conductor and shield/drain cut back and insulated","finished_length_mm":"300 +/-5 jacket span","end_a":"Phoenix 1757019 JDUT; contact 2 physically empty","end_b":"Phoenix 1757019 POD JIN; contact 2 physically empty","label_color":"ORANGE - LO OPEN","maximum_use":"24 V DC candidate only under CF-P11","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-06","name":"current-limit shorting adapter","function":"controlled CAL_HI-to-CAL_LO short at JDUT","construction":"one Phoenix 1757019 with an 80 +/-5 mm 22 AWG insulated loop; two ferrules","finished_length_mm":"80 +/-5 conductor before termination","end_a":"Phoenix 1757019 contact 1 to contact 2","end_b":"NONE - capped single-ended adapter","label_color":"BLACK/YELLOW - SHORT; OUTPUT OFF TO FIT/REMOVE","maximum_use":"candidate 10 mA current-limit characterization only","state":"UNBUILT","warning":WARNING},
        {"assembly_id":"CK-07","name":"reference-DMM patch pair","function":"fixture JHI/JLO to Fluke V/ohm and COM","construction":"unaltered manufacturer-assembled Fluke TL930 red/black pair","finished_length_mm":"610 manufacturer nominal","end_a":"red/black multi-stacking 4 mm plugs to JHI/JLO","end_b":"red to V/ohm, black to COM; both current jacks empty","label_color":"GREEN - REFERENCE DMM ONLY","maximum_use":"30 V RMS / 60 V DC, 8 A manufacturer rating; fixture candidate <=24 V DC","state":"UNBUILT / RECEIVE AND INSPECT","warning":WARNING},
    ]


def contact_map() -> list[dict[str, object]]:
    specs = {
        "CK-01":[("KEYSIGHT + RED","4 mm plug","JPS","1","CAL_HI","red 18 AWG"),("KEYSIGHT - BLACK","4 mm plug","JPS","2","CAL_LO","black 18 AWG")],
        "CK-02":[("JDUT","1","POD JIN","1","CAL_HI","white 22 AWG"),("JDUT","2","POD JIN","2","CAL_LO","black 22 AWG")],
        "CK-03":[("JDUT","1","POD JIN","2","CROSSED HI TO LO","white 22 AWG"),("JDUT","2","POD JIN","1","CROSSED LO TO HI","black 22 AWG")],
        "CK-04":[("JDUT","1 EMPTY","POD JIN","1 EMPTY","CONTROLLED HI OPEN","NO CONDUCTOR"),("JDUT","2","POD JIN","2","CAL_LO","black 22 AWG")],
        "CK-05":[("JDUT","1","POD JIN","1","CAL_HI","white 22 AWG"),("JDUT","2 EMPTY","POD JIN","2 EMPTY","CONTROLLED LO OPEN","NO CONDUCTOR")],
        "CK-06":[("JDUT","1","JDUT","2","CONTROLLED HI-LO SHORT","22 AWG offcut loop")],
        "CK-07":[("JHI RED","4 mm jack","FLUKE","V/OHM","CAL_HI REFERENCE","red TL930"),("JLO BLACK","4 mm jack","FLUKE","COM","CAL_LO REFERENCE","black TL930")],
    }
    rows=[]
    for aid, entries in specs.items():
        for n,(a,ac,b,bc,signal,wire) in enumerate(entries,1):
            rows.append({"assembly_id":aid,"circuit":n,"from_connector":a,"from_contact":ac,"to_connector":b,"to_contact":bc,"signal_or_fault":signal,"conductor":wire,"shield_or_drain":"CUT BACK AND INSULATED BOTH ENDS" if aid in {"CK-02","CK-03","CK-04","CK-05"} else "NOT PRESENT","continuity_target":"<1 ohm after lead-null; actual recorded" if "EMPTY" not in ac and "NO CONDUCTOR" not in wire else ">10 Mohm; actual recorded","state":"NOT EXECUTED","warning":WARNING})
    return rows


def cut_list() -> list[dict[str, object]]:
    return [
        {"cut_id":"CUT-01","assembly_id":"CK-01","material":"Mueller BU-0061-M-39-2 red","quantity":1,"raw_length_mm":"990.6 nominal manufacturer assembly","finished_length_mm":"975 target; 950 minimum","end_preparation":"retain banana end; remove complete tin-dipped segment; strip 9 mm; crimp 3200742","tolerance_or_gate":"record actual; reject below 950 mm or with insulation damage","warning":WARNING},
        {"cut_id":"CUT-02","assembly_id":"CK-01","material":"Mueller BU-0061-M-39-0 black","quantity":1,"raw_length_mm":"990.6 nominal manufacturer assembly","finished_length_mm":"975 target; 950 minimum","end_preparation":"retain banana end; remove complete tin-dipped segment; strip 9 mm; crimp 3200742","tolerance_or_gate":"record actual; reject below 950 mm or with insulation damage","warning":WARNING},
        *[{"cut_id":f"CUT-{i:02d}","assembly_id":aid,"material":"Alpha Wire 5610B2201","quantity":1,"raw_length_mm":"360","finished_length_mm":"300 +/-5 jacket span","end_preparation":"remove 30 +/-1 mm jacket each end; cut foil/drain flush; sleeve 20 +/-2 mm FIT-221-1/4; strip populated conductors 10 mm; crimp 3203066","tolerance_or_gate":"no shield strand, nicked conductor or exposed copper; empty contacts physically unpopulated","warning":WARNING} for i,aid in enumerate(("CK-02","CK-03","CK-04","CK-05"),3)],
        {"cut_id":"CUT-07","assembly_id":"CK-06","material":"one insulated 22 AWG conductor from 5610B2201 controlled offcut","quantity":1,"raw_length_mm":"100","finished_length_mm":"80 +/-5 before termination","end_preparation":"strip 10 mm each end; crimp one 3203066 per end; form loop without sharp bend","tolerance_or_gate":"minimum inside bend radius 10 mm; no exposed copper","warning":WARNING},
        {"cut_id":"CUT-08","assembly_id":"CK-07","material":"Fluke TL930 part 1616671","quantity":1,"raw_length_mm":"610 nominal","finished_length_mm":"DO NOT CUT OR MODIFY","end_preparation":"receive, inspect, label only","tolerance_or_gate":"reject damaged insulation, loose plug, wrong colors or failed continuity","warning":WARNING},
    ]


def traveler() -> list[dict[str, object]]:
    steps = [
        ("TR-01","kit segregation","Clear bench; no robot, battery, safety circuit, actuator, USB-grounded equipment or live source connected.","Photograph empty bench and fixture isolation","STOP on any robot or energized circuit connection"),
        ("TR-02","incoming inspection","Record manufacturer, order code, lot and quantity for every cable, connector, ferrule, shrink and tool.","Incoming record and photographs","STOP on substitution or damage"),
        ("TR-03","cut and strip","Process one assembly at a time from wire-cut-list.csv; use calibrated length and stripping gauges.","Actual lengths and strip measurements","STOP on nicked strands or tolerance failure"),
        ("TR-04","shield isolation","For CK-02..05 cut foil/drain flush at both ends and cover with 20 +/-2 mm FIT-221-1/4 sleeve.","No shield/drain continuity to any contact","STOP on exposed shield strand"),
        ("TR-05","ferrule crimp","Use CRIMPFOX CENTRUS 10S: 3200742 on 18 AWG source leads; 3203066 on 22 AWG conductors.","Lot/tool ID, visual crimp inspection and coupon pull record","STOP on wrong ferrule/tool or incomplete insertion"),
        ("TR-06","plug termination","Insert to contact map; tighten every Phoenix 1757019 screw to 0.50-0.60 N m with in-calibration torque driver.","Contact, torque value, driver serial/date","STOP on loose strand, exposed copper or torque miss"),
        ("TR-07","labels","Apply both-end assembly ID, role, direction and fault label; orange open adapters name the open conductor; short adapter states OUTPUT OFF TO FIT/REMOVE.","Two-person label-to-map check","STOP on ambiguity or unreadable text"),
        ("TR-08","continuity and isolation","Four-wire/lead-null continuity per populated path; >10 Mohm between open contacts, shield/drain and populated circuits at a qualified test voltage not yet released.","Raw readings and instrument identities","STOP until insulation test voltage is selected"),
        ("TR-09","polarity fixture","With no source connected, use continuity to verify CK-02 straight, CK-03 crossed, CK-04 HI open, CK-05 LO open and CK-06 short.","Signed connector/contact matrix","STOP on any mismatch"),
        ("TR-10","retention and bend","Perform qualified axial retention coupon/test and verify minimum 49 mm cable bend radius for 5610B2201 assemblies.","Force, duration, displacement and post-test continuity","STOP because numeric retention limit remains open"),
        ("TR-11","DMM pair","Verify CK-07 red JHI-to-V/ohm and black JLO-to-COM; meter current jacks remain visibly empty.","Photograph and continuity readings","STOP on current-jack use"),
        ("TR-12","bag and control","Cap contacts; bag each assembly separately; store CK-03..06 in FAULT ADAPTER compartment physically separated from CK-02.","Inventory, seal and custodian","No adapter may be left attached"),
    ]
    return [{"step_id":a,"operation":b,"instruction":c,"required_record":d,"stop_rule":e,"result":"NOT EXECUTED","authority":AUTHORITY,"warning":WARNING} for a,b,c,d,e in steps]


def tests() -> list[dict[str, object]]:
    tests=[
        ("CK-T01","identity and count","all seven assemblies present; order codes and lots recorded"),
        ("CK-T02","contact population","every populated and intentionally empty contact matches connector-contact-map.csv"),
        ("CK-T03","continuity","every populated path <1 ohm after lead-null; actual readings retained; final numeric limit qualified"),
        ("CK-T04","open isolation","intended opens and shield/drain >10 Mohm at qualified test voltage; voltage selection remains open"),
        ("CK-T05","polarity","CK-01/02/07 straight; CK-03 crossed; CK-04/05 single-conductor; CK-06 short only"),
        ("CK-T06","screw torque","every 1757019 terminal 0.50-0.60 N m with in-calibration driver; actual value recorded"),
        ("CK-T07","crimp coupons","18 AWG/3200742 and 22 AWG/3203066 visual and pull coupons accepted to a released numeric limit"),
        ("CK-T08","strain and bend","no conductor load at terminal; 5610B2201 bend radius >=49 mm in use"),
        ("CK-T09","labels","fault adapters recognizable from either end and segregated from blue normal cable"),
        ("CK-T10","low-energy dry rehearsal","source absent; correct cable selected from procedure and returned after each simulated step"),
    ]
    return [{"test_id":a,"test":b,"acceptance_or_evidence":c,"result":"NOT EXECUTED","review":"REQUIRED","warning":WARNING} for a,b,c in tests]


def bom() -> list[dict[str, object]]:
    items=[
        ("CK-B01",1,"Mueller Electric","BU-0061-M-39-2","red 39 inch 18 AWG silicone shrouded-banana lead","EXACT CANDIDATE"),
        ("CK-B02",1,"Mueller Electric","BU-0061-M-39-0","black 39 inch 18 AWG silicone shrouded-banana lead","EXACT CANDIDATE"),
        ("CK-B03",2,"m","Alpha Wire","5610B2201","one-pair shielded 22 AWG cable","EXACT CANDIDATE; includes process scrap"),
        ("CK-B04",10,"Phoenix Contact","1757019","two-position 5.08 mm screw plug","EXACT CANDIDATE"),
        ("CK-B05",4,"Phoenix Contact","3200742","AI 1-6 RD ferrule for 18 AWG source leads plus two coupons/spares","EXACT CANDIDATE"),
        ("CK-B06",20,"Phoenix Contact","3203066","AI 0.34-8 TQ ferrule for 22 AWG assemblies plus coupons/spares","EXACT CANDIDATE"),
        ("CK-B07",1,"Phoenix Contact","1213154","CRIMPFOX CENTRUS 10S hand crimper","EXACT TOOL CANDIDATE; calibration/inspection open"),
        ("CK-B08",1,"Alpha Wire","FIT-KIT-221BK","black FIT-221 heat-shrink kit containing 1/4 inch tubing","EXACT MATERIAL CANDIDATE; shrink process open"),
        ("CK-B09",1,"Fluke","TL930 / part 1616671","61 cm red/black 4 mm patch-cord pair","EXACT CANDIDATE; do not modify"),
        ("CK-B10",1,"SELECTION REQUIRED","SELECTION REQUIRED","calibrated 0.50-0.60 N m torque driver and bit","SELECTION REQUIRED"),
        ("CK-B11",1,"PROJECT PRINT","CK-LABEL-P0.1","water-resistant two-ended cable and fault labels","MATERIAL/ADHESION SELECTION REQUIRED"),
        ("CK-B12",1,"SELECTION REQUIRED","SELECTION REQUIRED","latching divided storage case with normal/fault physical segregation","SELECTION REQUIRED"),
    ]
    rows=[]
    for item in items:
        if len(item)==6: i,q,m,o,d,s=item; unit="each"
        else: i,q,unit,m,o,d,s=item
        rows.append({"item_id":i,"quantity":q,"unit":unit,"manufacturer":m,"order_code":o,"description":d,"selection_state":s,"procurement_released":"NO","warning":WARNING})
    return rows


def sources() -> list[dict[str, object]]:
    return [
        {"source_id":"CK-S01","manufacturer":"Mueller Electric","document":"DS-BU-0061-M-@","revision_or_date":"live official PDF accessed 2026-08-19; revision not stated","url":URLS["mueller"],"verified":"BU-0061-M family; manufacturer-assembled shrouded banana to tin-dipped free end; 18 AWG 413/44 UL3577 silicone; 39 inch standard","open_boundary":"received lot and retermination process","warning":WARNING},
        {"source_id":"CK-S02","manufacturer":"Mueller Electric","document":"UKCA and CE parts 101525","revision_or_date":"2025-10-15; accessed 2026-08-19","url":URLS["mueller_list"],"verified":"BU-0061-M-39-0 black and BU-0061-M-39-2 red listed","open_boundary":"received identity","warning":WARNING},
        {"source_id":"CK-S03","manufacturer":"Alpha Wire","document":"5610B2201 product record","revision_or_date":"live official page accessed 2026-08-19","url":URLS["alpha_cable"],"verified":"one 22 AWG twisted pair, shield/drain, 105 C, 300 Vrms, 4.88 mm maximum OD class, 10x diameter bend radius","open_boundary":"received OD/lot and termination process","warning":WARNING},
        {"source_id":"CK-S04","manufacturer":"Phoenix Contact","document":"MSTB 2,5/2-ST-5,08 1757019","revision_or_date":"live official page accessed 2026-08-19","url":URLS["plug"],"verified":"24-12 AWG; flexible with ferrule 0.25-2.5 mm2; 7 mm terminal strip reference; 0.5-0.6 N m; do not mate under load","open_boundary":"received lot/application retention","warning":WARNING},
        {"source_id":"CK-S05","manufacturer":"Phoenix Contact","document":"AI 0,34-8 TQ 3203066","revision_or_date":"live official page accessed 2026-08-19","url":URLS["ferrule22"],"verified":"0.34 mm2/AWG22; 8 mm contact; 10 mm strip; DIN 46228-4/UL 486F-E dimensions","open_boundary":"crimp coupon and tool condition","warning":WARNING},
        {"source_id":"CK-S06","manufacturer":"Phoenix Contact","document":"AI 1-6 RD 3200742","revision_or_date":"official catalog PDF generated 2026-07-04; accessed 2026-08-19","url":URLS["ferrule18"],"verified":"1.0 mm2/AWG18; 6 mm contact; 9 mm strip; DIN 46228-4/UL 486F-E dimensions","open_boundary":"crimp coupon and fit in 1757019","warning":WARNING},
        {"source_id":"CK-S07","manufacturer":"Phoenix Contact","document":"CRIMPFOX CENTRUS 10S","revision_or_date":"current official 2025 tools catalog and live page accessed 2026-08-19","url":URLS["crimper"],"verified":"order 1213154; automatic adjustment; ferrules 0.14-10 mm2 / AWG26-8","open_boundary":"received tool inspection/calibration and operator qualification","warning":WARNING},
        {"source_id":"CK-S08","manufacturer":"Alpha Wire","document":"FIT-221 heat-shrink family","revision_or_date":"live official page accessed 2026-08-19","url":URLS["alpha_shrink"],"verified":"FIT-221 2:1 irradiated PVC family; FIT-KIT-221BK candidate contains 1/4 inch tubing","open_boundary":"shrink temperature/time and label adhesion","warning":WARNING},
        {"source_id":"CK-S09","manufacturer":"Fluke","document":"TL930 product page","revision_or_date":"live official page accessed 2026-08-19; revision not stated","url":URLS["tl930"],"verified":"part 1616671; red/black multi-stacking 4 mm patch pair; 61 cm; 30 V RMS/60 V DC, 8 A","open_boundary":"received condition and 87V MAX/73099 fit","warning":WARNING},
    ]


def holds() -> list[dict[str, object]]:
    items=[
        ("CK-H01","received parts and lots","supplier records, identity and incoming inspection"),
        ("CK-H02","source-lead tin removal and final length","released work instruction plus actual lengths >=950 mm"),
        ("CK-H03","crimp pull limits","qualified 18 AWG and 22 AWG coupon values, sample count and results"),
        ("CK-H04","insulation test voltage and limit","qualified low-energy test method compatible with connected components"),
        ("CK-H05","torque tool","exact calibrated driver/bit selection and in-date certificate"),
        ("CK-H06","label and storage materials","durability/adhesion and physical fault-adapter segregation"),
        ("CK-H07","fixture and received-mating FAI","73099/TL930 fit, 1757019 mating, enclosure access and bend clearance"),
        ("CK-H08","fabrication and inspection","signed traveler and all CK-T01..10 evidence"),
        ("CK-H09","qualified electrical/metrology review","accept contact maps, tests and calibration-procedure use"),
        ("CK-H10","FER-G11 and work authority","separate signed staged authorization; this kit cannot grant it"),
    ]
    return [{"hold_id":a,"open_item":b,"closure_evidence":c,"state":"OPEN","authority":AUTHORITY,"warning":WARNING} for a,b,c in items]


def labels() -> list[dict[str, object]]:
    return [{"assembly_id":r["assembly_id"],"body_text":f'{r["assembly_id"]} - {str(r["name"]).upper()}',"end_a_text":str(r["end_a"]),"end_b_text":str(r["end_b"]),"background":str(r["label_color"]),"minimum_text_height_mm":3.0,"placement":"within 50 mm of each end; readable without rotating connector","material":"SELECTION REQUIRED","inspection":"two-person map-to-label check","warning":WARNING} for r in assemblies()]


def make_svg() -> None:
    cards=[]
    colors={"CK-01":"#f2b91d","CK-02":"#72c8f0","CK-03":"#ff7b6e","CK-04":"#ffb14d","CK-05":"#ffb14d","CK-06":"#1b2735","CK-07":"#65c985"}
    for i,row in enumerate(assemblies()):
        x=60+(i%2)*760; y=150+(i//2)*185
        fg="#fff" if row["assembly_id"]=="CK-06" else "#102b46"
        cards.append(f'<rect x="{x}" y="{y}" width="700" height="145" rx="18" fill="{colors[row["assembly_id"]]}" stroke="#082d67" stroke-width="4"/><text x="{x+24}" y="{y+36}" class="id" fill="{fg}">{row["assembly_id"]} · {html.escape(str(row["name"]))}</text><text x="{x+24}" y="{y+72}" class="t" fill="{fg}">{html.escape(str(row["function"]))}</text><text x="{x+24}" y="{y+108}" class="s" fill="{fg}">{html.escape(str(row["finished_length_mm"]))}</text>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1580" height="910" viewBox="0 0 1580 910" role="img"><style>.h{{font:900 34px system-ui}}.id{{font:800 21px system-ui}}.t{{font:700 17px system-ui}}.s{{font:600 15px system-ui}}</style><rect width="1580" height="910" fill="#eef8ff"/><text x="55" y="58" class="h" fill="#082d67">Seven controlled leads - one normal cable, four unmistakable fault tools</text><text x="55" y="100" class="t" fill="#102b46">Every connection change occurs with the source output OFF. No cable may connect to the robot.</text>{''.join(cards)}<text x="820" y="845" class="t" fill="#982520">CK-03 through CK-06 live in a separate FAULT ADAPTER compartment.</text></svg>'''
    (OUT/"cable-kit-layout.svg").write_text(svg+"\n",encoding="utf-8")


def write_cad() -> None:
    import cadquery as cq
    from cadquery.occ_impl.exporters.assembly import exportAssembly, exportGLTF
    asm=cq.Assembly(name="HR30_MEASUREMENT_CALIBRATION_CABLE_KIT")
    lengths={"CK-01":975,"CK-02":300,"CK-03":300,"CK-04":300,"CK-05":300,"CK-06":80,"CK-07":610}
    colors={"CK-01":cq.Color(.95,.65,.05),"CK-02":cq.Color(.25,.65,.9),"CK-03":cq.Color(.9,.1,.08),"CK-04":cq.Color(1,.45,.05),"CK-05":cq.Color(1,.45,.05),"CK-06":cq.Color(.03,.03,.03),"CK-07":cq.Color(.1,.65,.3)}
    scale=.55
    for i,(aid,length) in enumerate(lengths.items()):
        y=(i-3)*45
        cable=cq.Workplane("YZ").circle(2.45 if aid not in {"CK-01","CK-07"} else 2.0).extrude(length*scale).translate((-length*scale/2,y,0))
        left=cq.Workplane("XY").box(18,18,14).translate((-length*scale/2-9,y,0))
        right=cq.Workplane("XY").box(18,18,14).translate((length*scale/2+9,y,0)) if aid!="CK-06" else cq.Workplane("XY").box(18,18,14).translate((-length*scale/2-9,y,0))
        asm.add(cable,name=f"{aid}_CABLE",color=colors[aid]); asm.add(left,name=f"{aid}_END_A",color=cq.Color(.12,.45,.25)); asm.add(right,name=f"{aid}_END_B",color=cq.Color(.12,.45,.25))
        tag=cq.Workplane("XY").box(44,22,2).translate((0,y,8)); asm.add(tag,name=f"{aid}_LABEL",color=colors[aid])
    tray=cq.Workplane("XY").box(600,360,4).translate((0,0,-12)); asm.add(tray,name="SEGREGATED_STORAGE_TRAY_ENVELOPE",color=cq.Color(.05,.14,.28,.35))
    if not exportAssembly(asm,str(OUT/"HR30_measurement_calibration_cable_kit_candidate.step")): raise RuntimeError("STEP export failed")
    if not exportGLTF(asm,str(OUT/"HR30_measurement_calibration_cable_kit_candidate.glb"),binary=True): raise RuntimeError("GLB export failed")


def table(name: str, title: str) -> str:
    with (OUT/name).open(encoding="utf-8",newline="") as h: data=list(csv.DictReader(h))
    fields=list(data[0]); head=''.join(f'<th>{html.escape(x.replace("_"," ").title())}</th>' for x in fields)
    body=''.join('<tr>'+''.join(f'<td>{html.escape(r[f])}</td>' for f in fields)+'</tr>' for r in data)
    return f'<section><h2>{html.escape(title)}</h2><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>'


def make_html() -> None:
    tables=''.join([table("cable-assembly-register.csv","Seven controlled assemblies"),table("connector-contact-map.csv","Contact-by-contact wiring"),table("wire-cut-list.csv","Cut, strip and ferrule definition"),table("assembly-traveler.csv","Fabrication traveler"),table("inspection-test-register.csv","Inspection and test record"),table("candidate-bom.csv","Candidate BOM"),table("open-holds.csv","Open before fabrication or use")])
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 calibration cable kit</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1450px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:16ch}}h2{{font-size:clamp(28px,4vw,44px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--blue);border-radius:16px;padding:20px;box-shadow:6px 6px 0 var(--sky)}}.hold{{background:#fff2cd;border-color:#9a6500}}.metric{{font-size:clamp(34px,5vw,56px);font-weight:900;color:var(--blue)}}section{{margin:44px 0}}.scroll,.viewer{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:14px}}object{{display:block;width:100%;min-width:1000px;min-height:575px}}model-viewer{{width:100%;height:560px;background:radial-gradient(circle,#fff,#d9f2ff)}}table{{border-collapse:collapse;width:max-content;min-width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid #a8c4e4;vertical-align:top;max-width:520px}}th{{position:sticky;top:0;background:var(--deep);color:white;font-size:14px;text-align:left}}td{{font-size:16px}}a{{color:#075b9b;font-weight:800}}@media(max-width:600px){{body{{font-size:16px}}th,td{{min-width:180px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 / off-robot metrology / FER-G11 preparation</p><h1>The fixture now has the exact leads it needs.</h1><p>One blue normal cable. Four physically segregated fault tools. A manufacturer-built source pair and DMM patch pair. Every conductor, empty contact, strip length, ferrule and torque step is controlled.</p></header><main><section class="grid"><article><div class="metric">7</div><h2>assemblies</h2><p>Source, normal, reverse, HI-open, LO-open, short and reference-DMM pairs.</p></article><article><div class="metric">10</div><h2>Phoenix plugs</h2><p>Each contact is mapped; intentional opens are physically empty.</p></article><article><div class="metric">0.50-0.60</div><h2>N m</h2><p>Phoenix terminal torque; actual values and tool identity must be recorded.</p></article><article class="hold"><div class="metric">0</div><h2>built</h2><p>Parts, crimp coupons, insulation limit and qualified review remain open.</p></article></section><section><h2>Visual kit map</h2><div class="scroll"><object data="cable-kit-layout.svg" type="image/svg+xml" aria-label="Seven calibration cable assemblies"></object></div></section><section><h2>Editable physical layout</h2><div class="viewer"><model-viewer src="HR30_measurement_calibration_cable_kit_candidate.glb" camera-controls auto-rotate shadow-intensity="1" alt="Seven-piece HR-30 calibration cable and fault-adapter kit"></model-viewer></div></section><section class="grid"><article><h2>Normal path</h2><p>CK-02 is blue and straight-through. It is the only transfer cable used for ordinary point calibration.</p></article><article><h2>Fault tools</h2><p>CK-03 through CK-06 are red, orange or black/yellow, kept in a separate compartment and removed after each controlled case.</p></article><article class="hold"><h2>Output off to change</h2><p>No plug, adapter or meter lead is fitted, removed or rerouted with the source output enabled.</p></article></section>{tables}<section class="panel"><h2>Engineering files</h2><p><a href="connector-contact-map.csv">contact map</a> · <a href="wire-cut-list.csv">cut list</a> · <a href="assembly-traveler.csv">traveler</a> · <a href="HR30_measurement_calibration_cable_kit_candidate.step">STEP</a> · <a href="primary-source-register.csv">primary sources</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''
    (OUT/"index.html").write_text(page,encoding="utf-8")


def integrate() -> None:
    status_path=WHOLE/"package-status.json"; status=json.loads(status_path.read_text(encoding="utf-8"))
    status.update({"measurement_calibration_cable_kit_candidate_present":True,"measurement_calibration_cable_kit_assembly_count":7,"measurement_calibration_cable_kit_built":False,"measurement_calibration_cable_kit_inspected":False,"measurement_chain_calibration_executed":False,"fer_g11_closed":False,"connection_authority":False,"energization_authority":False})
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    start,end="<!-- HR30-MEASUREMENT-CAL-CABLE-KIT-P01-START -->","<!-- HR30-MEASUREMENT-CAL-CABLE-KIT-P01-END -->"
    readme=WHOLE/"README.md"; text=readme.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    block=f'''{start}\n## Measurement calibration cable and fault-adapter kit\n\nThe [interactive cable-kit guide](electrical/{OUT.name}/index.html) defines **seven physical assemblies** for the off-robot measurement-chain fixture: exact source and DMM candidates, a blue normal cable, red reverse cable, two orange open-lead adapters and a black/yellow current-limit shorting adapter. The package includes contact maps, dimensions, cut/strip/ferrule instructions, the Phoenix terminal torque range, labels, a signed traveler, inspection tests, STEP/GLB layout and manufacturer evidence. Parts are not procured; crimp/insulation limits, build, inspection, metrology review, FER-G11 and every robot authority remain open.\n{end}\n'''
    readme.write_text(text.rstrip()+"\n\n"+block,encoding="utf-8")
    page=WHOLE/"index.html"; text=page.read_text(encoding="utf-8")
    if start in text and end in text: text=text.split(start,1)[0]+text.split(end,1)[1]
    section=f'''{start}<section id="measurement-calibration-cable-kit"><h2>Seven controlled leads make the calibration fixture physically usable</h2><div class="grid"><article class="card pass"><div class="metric">7</div><p>dimensioned source, normal, fault and DMM assemblies now have contact maps.</p></article><article class="card pass"><h3>Faults cannot masquerade as normal</h3><p>Reverse, open and short adapters use distinct colors and a separate storage compartment.</p></article><article class="card hold"><h3>Still unbuilt</h3><p>Crimp coupons, insulation limit, tool calibration, assembly and qualified review remain open.</p></article></div><p><a href="electrical/{OUT.name}/index.html">Open the interactive calibration cable-kit guide</a>.</p></section>{end}'''
    page.write_text(text.replace("</main>",section+"</main>",1),encoding="utf-8")


def generate() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv("cable-assembly-register.csv",assemblies()); write_csv("connector-contact-map.csv",contact_map()); write_csv("wire-cut-list.csv",cut_list()); write_csv("assembly-traveler.csv",traveler()); write_csv("inspection-test-register.csv",tests()); write_csv("candidate-bom.csv",bom()); write_csv("primary-source-register.csv",sources()); write_csv("open-holds.csv",holds()); write_csv("label-register.csv",labels())
    binding={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"fixture_port_register_sha256":sha(FIXTURE/"fixture-port-register.csv"),"fixture_fault_register_sha256":sha(FIXTURE/"fault-injection-register.csv"),"fixture_procedure_register_sha256":sha(FIXTURE/"procedure-register.csv"),"scope":"OFF-ROBOT CALIBRATION FIXTURE LEADS ONLY; NO ROBOT CONNECTION"}
    (OUT/"source-binding.json").write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")
    status={"identifier":IDENTIFIER,"date":DATE,"warning":WARNING,"assembly_count":7,"phoenix_plug_count":10,"contact_map_rows":len(contact_map()),"fixture_only":True,"robot_connection_permitted":False,"parts_received":False,"crimp_coupons_accepted":False,"insulation_test_limit_released":False,"kit_built":False,"inspection_executed":False,"qualified_review_accepted":False,"fer_g11_closed":False,"functional_safety_credit":False,"procurement_authority":False,"fabrication_authority":False,"assembly_authority":False,"connection_authority":False,"powered_robot_test_authority":False,"motion_authority":False,"walking_authority":False,"energization_authority":False}
    (OUT/"cable-kit-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f'''# HR-30 measurement calibration cable and fault-adapter kit P0.1\n\n**{WARNING}**\n\nThis package turns the off-robot calibration fixture's cable requirement into seven controlled assemblies. It defines both endpoints, every populated or intentionally empty contact, conductor, nominal length, cut/strip/ferrule process, Phoenix 1757019 terminal torque, labels, physical fault-adapter segregation, inspection tests and an editable physical layout.\n\nThe source pair uses exact Mueller BU-0061-M-39 red/black candidates; the four fabricated transfer/fault assemblies use Alpha Wire 5610B2201; the reference meter uses an unmodified Fluke TL930 pair. Hardware remains unprocured and unbuilt. Crimp pull limits, insulation-test voltage, torque-tool selection, received-part FAI, qualified review, FER-G11 and all robot authority remain open.\n''',encoding="utf-8")
    make_svg(); write_cad(); make_html()
    shutil.copy2(Path(__file__),OUT/"measurement-calibration-cable-kit-source.py")
    shutil.copy2(ROOT/"tools"/"check_hr30_measurement_calibration_cable_kit_p01.py",OUT/"measurement-calibration-cable-kit-checker.py")
    files=sorted(p for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    write_csv("file-manifest.csv",[{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in files])
    if REL.exists(): shutil.rmtree(REL)
    shutil.copytree(OUT,REL)
    integrate()
    run([str(CAD_PYTHON),"-c","import sys;sys.path.insert(0,'tools');import generate_hr30_system_package_p01 as s;s.refresh_manifest_and_release()"])
    print(json.dumps({"identifier":IDENTIFIER,"assemblies":7,"contact_rows":len(contact_map()),"built":False,"robot_connection":False,"authorities":0},indent=2))


if __name__ == "__main__":
    generate()
