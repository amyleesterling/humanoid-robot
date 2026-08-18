#!/usr/bin/env python3
"""Publish the physical hardware/fabrication definition for the HR-30 E1 fixture.

This module is called after the complete E1 logic wiring has been generated.
It binds the revised CAD to exact hardware candidates, dimensioned fabrication
drawings and inspection records.  Nothing here grants fabrication, connection
or powered-test authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "electrical" / "e1-controls-only-fixture-p0.1"
IDENTIFIER = "HR30-E1-FIXTURE-HARDWARE-P0.1"
WARNING = (
    "PRELIMINARY - UNBUILT E1 FIXTURE HARDWARE CANDIDATE - NOT APPROVED FOR "
    "CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
AUTHORITY = "NO FABRICATION, CONNECTION, POWERED-TEST, MOTION, WALKING OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, data: list[dict]) -> None:
    if not data:
        raise RuntimeError(f"refusing empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before + block + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_registers() -> None:
    selections = [
        {"selection_id": "FH-S01", "assembly": "base panel", "quantity": 1, "candidate": "SABIC LEXAN 9034 clear polycarbonate sheet", "order_code": "LEXAN 9034 / RECEIVED STOCK TRACE REQUIRED", "defined_geometry": "360 x 240 x 6.0 mm; R8 corners; 4 x dia5.5 foot; 14 x dia3.0 PCB; 8 x dia3.4 cover holes; four logic slots", "disposition": "CANDIDATE FROZEN; SUPPLIER CUT SIZE AND COC REQUIRED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S02", "assembly": "carrier covers", "quantity": 2, "candidate": "SABIC LEXAN 9034 clear polycarbonate sheet", "order_code": "LEXAN 9034 / RECEIVED STOCK TRACE REQUIRED", "defined_geometry": "98 x 58 x 28 shell; 3.0 mm wall/top; 110 x 70 x 3 flange; four dia3.4 holes each", "disposition": "CNC-MACHINED CANDIDATE; THERMOFORMING NOT RELEASED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S03", "assembly": "under-panel raceway", "quantity": 1, "candidate": "SABIC LEXAN 9034 polycarbonate sheet", "order_code": "LEXAN 9034 / RECEIVED STOCK TRACE REQUIRED", "defined_geometry": "245 x 150 x 16 mm outside envelope; 2.0 mm base/walls; open top", "disposition": "CNC-CUT / MECHANICALLY FASTENED OR QUALIFIED-BOND PROCESS REQUIRED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S04", "assembly": "PCB pedestal", "quantity": 14, "candidate": "SABIC LEXAN 9034 clear polycarbonate", "order_code": "PROJECT PART E1-PED-6X3", "defined_geometry": "dia6.0 x 3.0 mm ring; dia2.8 clearance", "disposition": "CNC/WATERJET FROM 3.0 MM SHEET; RECEIVED FIT REQUIRED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S05", "assembly": "PCB standoff", "quantity": 14, "candidate": "Wuerth Elektronik WA-SPAII plastic internal/internal spacer", "order_code": "970080155", "defined_geometry": "5 mm AF; 8.0 +/-0.1 mm; M2.5 both ends; black PA", "disposition": "EXACT CANDIDATE; AVAILABILITY AND RECEIVED THREAD FIT REQUIRED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S06", "assembly": "PCB top screw", "quantity": 14, "candidate": "Essentra nylon crossed pan screw", "order_code": "50M025045P006 / ITEM 10295533", "defined_geometry": "M2.5 x 0.45; 6.0 mm; head dia5.0 x 1.6 mm", "disposition": "EXACT CANDIDATE; TORQUE/ENGAGEMENT PROCESS OPEN", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S07", "assembly": "PCB bottom screw", "quantity": 14, "candidate": "Essentra nylon slotted cheese screw", "order_code": "50M025045D012 / ITEM 10325643", "defined_geometry": "M2.5 x 0.45; 12.0 mm; project envelope head dia4.5 x 1.6 mm", "disposition": "EXACT CANDIDATE; 3.0 MM MINIMUM NOMINAL ENGAGEMENT; TORQUE OPEN", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S08", "assembly": "cover screw", "quantity": 8, "candidate": "Essentra nylon crossed pan screw", "order_code": "50M030050P012 / ITEM 10397367", "defined_geometry": "M3 x 0.5; 12.0 mm; head dia5.6 x 2.4 mm", "disposition": "EXACT CANDIDATE; TORQUE PROCESS OPEN", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S09", "assembly": "cover nut", "quantity": 8, "candidate": "Essentra black nylon hex nut", "order_code": "496241 / ITEM 10279151", "defined_geometry": "M3; 5.5 mm AF; 2.4 mm high", "disposition": "EXACT CANDIDATE; WITNESS/RETENTION PROCESS OPEN", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S10", "assembly": "bench-foot riser", "quantity": 4, "candidate": "SABIC LEXAN 9034 clear polycarbonate", "order_code": "PROJECT PART E1-FOOT-223X79", "defined_geometry": "dia22.3 x 7.9 mm; dia5.5 through; dia9.5 x 4.8 bottom counterbore", "disposition": "CNC FROM 8 MM STOCK TO 7.9 MM FINISH; INSPECT BEFORE BUMPER BOND", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S11", "assembly": "bench-foot bumper", "quantity": 4, "candidate": "3M Bumpon clear protective product", "order_code": "SJ5309 / 3M ID 7000029678", "defined_geometry": "dia22.3 x 10.1 mm nominal; acrylic A-20 adhesive", "disposition": "EXACT CANDIDATE; SURFACE PREP/ADHESION/LOAD/AGING TEST OPEN", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S12", "assembly": "bench-foot screw", "quantity": 4, "candidate": "Essentra nylon round-head screw", "order_code": "ITEM 10374603", "defined_geometry": "M5; 16.0 mm; head dia9.0 x 4.5 mm", "disposition": "EXACT DISTRIBUTOR ITEM CANDIDATE; MANUFACTURER PART CODE/RECEIVED DRAWING REQUIRED", "built": "NO", "warning": WARNING},
        {"selection_id": "FH-S13", "assembly": "bench-foot nut", "quantity": 4, "candidate": "Essentra natural nylon hex nut", "order_code": "0030030000VR / ITEM 10041420", "defined_geometry": "M5; 8.0 mm AF; 4.2 mm high", "disposition": "EXACT CANDIDATE; TORQUE/WITNESS PROCESS OPEN", "built": "NO", "warning": WARNING},
    ]
    write_csv(OUT / "fixture-hardware-selection-register.csv", selections)

    write_csv(OUT / "fixture-fastener-stack-register.csv", [
        {"stack_id": "FH-ST01", "location_count": 14, "direction": "bottom screw upward / top screw downward", "layers_mm": "bottom head 1.6; panel 6.0; pedestal 3.0; standoff 8.0; PCB 1.6; top head 1.6", "candidate_fasteners": "50M025045D012 bottom + 970080155 + 50M025045P006 top", "nominal_thread_engagement": "bottom 3.0 mm; top 4.4 mm", "interference_rule": "no screw may enter component/copper keepout or cable volume", "torque": "SELECTION REQUIRED FROM RECEIVED-HARDWARE TEST", "validation": "NOT EXECUTED", "warning": WARNING},
        {"stack_id": "FH-ST02", "location_count": 8, "direction": "cover screw downward", "layers_mm": "head 2.4; flange 3.0; panel 6.0; nut 2.4", "candidate_fasteners": "50M030050P012 + 496241", "nominal_thread_engagement": "full 2.4 mm nut; approx 0.6 mm nominal protrusion", "interference_rule": "no screw/nut may enter fixed logic-harness corridor", "torque": "SELECTION REQUIRED FROM COVER RETENTION TEST", "validation": "NOT EXECUTED", "warning": WARNING},
        {"stack_id": "FH-ST03", "location_count": 4, "direction": "foot screw upward", "layers_mm": "recessed head 4.5; remaining riser 3.4; panel 6.0; nut 4.2; bumper 10.1 below riser", "candidate_fasteners": "ITEM 10374603 + 0030030000VR + SJ5309", "nominal_thread_engagement": "full 4.2 mm nut; approx 2.4 mm nominal protrusion above nut", "interference_rule": "foot screw only at corner keepouts; bumper fully covers recessed head", "torque": "SELECTION REQUIRED; DO NOT CRAZE POLYCARBONATE", "validation": "NOT EXECUTED", "warning": WARNING},
    ])

    write_csv(OUT / "fixture-material-register.csv", [
        {"material_id": "FH-M01", "material": "SABIC LEXAN 9034 general-purpose polycarbonate sheet", "used_for": "panel; covers; raceway; pedestals; foot risers", "candidate_gauges_mm": "2.0; 3.0; 6.0; 8.0 stock machined to 7.9", "source_range_mm": "0.76 to 12.70 in cited Americas portfolio", "critical_process": "CNC tool/coolant/edge-finish plan and stress-craze compatibility", "incoming_evidence": "supplier COC; grade; lot; actual thickness; flatness; protective film", "state": "SELECTION FROZEN / PROCUREMENT AND PROCESS OPEN", "warning": WARNING},
        {"material_id": "FH-M02", "material": "Wuerth black polyamide WA-SPAII", "used_for": "14 PCB standoffs", "candidate_gauges_mm": "5 AF x 8.0", "source_range_mm": "-30 to +110 C; UL94 HB stated by manufacturer", "critical_process": "M2.5 thread fit and torque", "incoming_evidence": "bag label; order code; dimensional/thread inspection", "state": "EXACT CANDIDATE / RECEIPT OPEN", "warning": WARNING},
        {"material_id": "FH-M03", "material": "nylon fasteners", "used_for": "PCB, cover and foot fastening", "candidate_gauges_mm": "M2.5; M3; M5", "source_range_mm": "individual live product pages", "critical_process": "creep/relaxation; thread engagement; torque; witness marking", "incoming_evidence": "order-code labels; dimensional fit; lot trace", "state": "EXACT CANDIDATES / PROCESS OPEN", "warning": WARNING},
        {"material_id": "FH-M04", "material": "3M SJ5309 urethane Bumpon", "used_for": "four nonslip contact pads", "candidate_gauges_mm": "dia22.3 x 10.1", "source_range_mm": "A-20 acrylic adhesive; transparent", "critical_process": "surface preparation; adhesion; static load; creep/aging", "incoming_evidence": "3M label/lot; dimensions; shelf condition", "state": "EXACT CANDIDATE / PROCESS OPEN", "warning": WARNING},
    ])

    write_csv(OUT / "fixture-fabrication-drawing-register.csv", [
        {"drawing_id": "FH-D01", "file": "base-panel-fabrication-drawing.svg", "part": "E1 base panel", "datum": "center X/Y; lower sheet face Z", "general_tolerance_mm": "+/-0.20 UNLESS NOTED", "critical_dimensions": "360 x 240 x 6; R8; hole/slot coordinates from DXF; dia3.0/3.4/5.5", "process": "3-axis CNC router/mill; deburr without flame polishing", "release": "CANDIDATE - DFM AND FIRST ARTICLE OPEN", "warning": WARNING},
        {"drawing_id": "FH-D02", "file": "carrier-cover-fabrication-drawing.svg", "part": "sealed carrier cover", "datum": "cover center; flange lower face", "general_tolerance_mm": "+/-0.20 UNLESS NOTED", "critical_dimensions": "110 x 70 flange; 98 x 58 x 28 shell; 3 wall/top/flange; 92 x 52 cavity; 4 x dia3.4", "process": "3-axis CNC from clear PC; no field-port opening", "release": "CANDIDATE - RECEIVED CONNECTOR CLEARANCE OPEN", "warning": WARNING},
        {"drawing_id": "FH-D03", "file": "under-panel-raceway-fabrication-drawing.svg", "part": "logic-cable raceway", "datum": "tray center and panel underside", "general_tolerance_mm": "+/-0.30 UNLESS NOTED", "critical_dimensions": "245 x 150 x 16 outside; 2 wall/base; open top", "process": "CNC-cut sheet plus mechanically fastened corners or qualified bond", "release": "CANDIDATE - JOINING METHOD OPEN", "warning": WARNING},
        {"drawing_id": "FH-D04", "file": "fixture-hardware-assembly-map.svg", "part": "complete hardware map", "datum": "panel center", "general_tolerance_mm": "SEE COMPONENT DRAWINGS", "critical_dimensions": "14 PCB stacks; 8 cover stacks; 4 foot stacks", "process": "controlled assembly traveler", "release": "CANDIDATE - NO FABRICATION AUTHORITY", "warning": WARNING},
    ])

    inspection = [
        ("FH-I01", "panel material identity and thickness", "LEXAN 9034 COC/lot; 6.0 +/-0.20 mm", "COC + micrometer map"),
        ("FH-I02", "panel outside profile/flatness", "360/240/R8 within drawing; <=0.75 mm total flatness candidate", "CMM/height gauge"),
        ("FH-I03", "all panel holes and slots", "4 foot +14 PCB +8 cover holes and four slots present; no burr/chip", "CMM + visual"),
        ("FH-I04", "cover walls/flange/cavity", "two covers; 3.0 mm nominal walls/top/flange; four dia3.4 holes each", "caliper/CMM"),
        ("FH-I05", "field-port exclusion", "cover closes on received carrier without contact; zero external field-port access", "fit gauge + visual"),
        ("FH-I06", "PCB support stack", "14 pedestals +14 order-code 970080155; board plane 14.0 mm nominal Z", "height gauge + label trace"),
        ("FH-I07", "fastener fit", "M2.5/M3/M5 start by hand; no cross-thread; no cracking/crazing", "controlled fit inspection"),
        ("FH-I08", "foot height and raceway clearance", "four finished foot stacks 18.0 mm nominal; tray bottom at least 2.0 mm above bench candidate", "height gauge/flat plate"),
        ("FH-I09", "SJ5309 adhesion", "full contact/no edge lift after defined dwell and proof load", "process/test definition required"),
        ("FH-I10", "assembled fixture stability", "all four feet contact; no rocking; covers retained; cable tray clear", "flat plate + witnessed record"),
    ]
    write_csv(OUT / "fixture-dimensional-inspection-register.csv", [
        {"inspection_id": iid, "feature": feature, "candidate_acceptance": acceptance, "method": method, "result": "NOT EXECUTED", "nonconformance_rule": "STOP / QUARANTINE / DO NOT ASSEMBLE", "authority": AUTHORITY, "warning": WARNING}
        for iid, feature, acceptance, method in inspection
    ])

    sources = [
        ("FH-P01", "SABIC", "LEXAN sheet portfolio brochure - Americas", "live official PDF accessed 2026-08-18; publication revision not stated", "https://www.sabic.com/en/Images/SABIC-LEXAN-Sheet-Portfolio-Brochure-English-Americas_tcm1010-5016.pdf", "LEXAN 9030/9034 is general-purpose polycarbonate sheet; cited gauge range 0.76-12.70 mm"),
        ("FH-P02", "Wuerth Elektronik", "970080155 datasheet", "rev 001.003 dated 2023-09-28; accessed 2026-08-18", "https://www.we-online.com/components/products/datasheet/970080155.pdf", "WA-SPAII; 5 mm AF; 8.0 +/-0.1 mm; M2.5 internal/internal; black polyamide"),
        ("FH-P03", "Essentra", "50M025045P006 live product page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-us/p/plastic-pan-head-screws/50m025045p006", "M2.5 x 6 nylon crossed pan screw; dia5.0 x 1.6 head"),
        ("FH-P04", "Essentra", "50M025045D012 live product page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-us/p/nylon-cheese-head-screws/50m025045d012", "M2.5 x 12 nylon cheese-head screw; dia4.5 x 1.6 head"),
        ("FH-P05", "Essentra", "50M030050P012 live product page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-gb/p/machine-screws-pan/50m030050p012", "M3 x 12 nylon crossed pan screw; dia5.6 x 2.4 head"),
        ("FH-P06", "Essentra", "496241 live product page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-gb/p/standard-hex-nuts-plastic/496241", "M3 black nylon nut; 5.5 mm AF x 2.4 mm"),
        ("FH-P07", "Essentra", "M5 round screw family live page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-gb/p/machine-screws-round", "item 10374603 lists M5 x 16 nylon round screw; dia9.0 x 4.5 head"),
        ("FH-P08", "Essentra", "0030030000VR live product page", "accessed 2026-08-18; page revision not stated", "https://www.essentracomponents.com/en-gb/p/standard-hex-nuts-plastic/0030030000vr", "M5 natural nylon nut; 8.0 mm AF x 4.2 mm"),
        ("FH-P09", "3M", "SJ5309 official product page", "live page accessed 2026-08-18; revision not stated", "https://www.3m.com/3M/en_US/p/d/b5005035188/", "SJ5309 clear; 3M ID 7000029678; urethane; pressure-sensitive adhesive; high skid resistance"),
        ("FH-P10", "3M", "Bumpon protective bumpers brochure", "2024 brochure; accessed 2026-08-18", "https://multimedia.3m.com/mws/media/2530717O/3m-bumpon-protective-bumpers-brochure-2024.pdf", "SJ5309 dia22.3 x 10.1 mm; transparent; acrylic A-20 adhesive"),
    ]
    write_csv(OUT / "fixture-hardware-primary-source-register.csv", [
        {"source_id": sid, "manufacturer": maker, "document": doc, "revision_date": rev, "url": url, "verified": verified, "warning": WARNING}
        for sid, maker, doc, rev, url, verified in sources
    ])

    bindings = [
        ("fixture generator", ROOT / "tools/generate_hr30_e1_controls_fixture_p01.py"),
        ("hardware generator", Path(__file__)),
        ("native MCU PCB", BODY / "electrical/motion-controller-p0.1/board/hr30-motion-controller-p0.1.kicad_pcb"),
        ("native carrier A PCB", BODY / "electrical/carriers-p0.1/carrier-a/hr30-carrier-a-p0.1.kicad_pcb"),
        ("native carrier B PCB", BODY / "electrical/carriers-p0.1/carrier-b/hr30-carrier-b-p0.1.kicad_pcb"),
        ("native SWD PCB", BODY / "electrical/swd-adapter-p0.1/board/hr30-swd-adapter-p0.1.kicad_pcb"),
    ]
    write_csv(OUT / "fixture-hardware-source-binding.csv", [
        {"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING}
        for role, path in bindings
    ])

    holds = [
        ("FH-H01", "LEXAN stock supplier/cut sizes/lot and machining process are not released", "supplier quotation/COC, DFM, coolant/tooling compatibility and first-article inspection"),
        ("FH-H02", "PCB standoff/screw thread engagement and torque are unvalidated", "received order-code inspection plus torque/creep/relaxation and keepout validation"),
        ("FH-H03", "carrier connector envelopes and cover clearance are not validated on received boards", "received-board fit, closure, contact, access and fastener inspection"),
        ("FH-H04", "raceway corner joining/retention method is not selected", "mechanical-fastener or qualified bonding drawing/process and pull inspection"),
        ("FH-H05", "SJ5309 surface preparation, adhesion, load and aging are unvalidated", "3M-compatible process plus dwell, proof-load, slip, creep and aging records"),
        ("FH-H06", "no fixture part has been fabricated or dimensionally inspected", "completed traveler, incoming records, FAI and as-built configuration record"),
        ("FH-H07", "no qualified mechanical/electrical reviewer has accepted the as-built fixture", "named review and separate stage-specific connection/powered-test authorization"),
    ]
    write_csv(OUT / "fixture-hardware-open-holds.csv", [
        {"hold_id": hid, "unresolved": issue, "closure": closure, "state": "OPEN", "authority": AUTHORITY, "warning": WARNING}
        for hid, issue, closure in holds
    ])


def svg_shell(title: str, body: str, width: int = 1200, height: int = 760) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#eef8fe"/><style>text{{font-family:system-ui,Segoe UI,sans-serif;fill:#142a40}}.title{{font-size:34px;font-weight:800}}.h{{font-size:22px;font-weight:750}}.t{{font-size:16px}}.d{{stroke:#0b4f91;stroke-width:2;fill:none}}.part{{stroke:#071d36;stroke-width:3;fill:#dff4ff}}.gold{{fill:#f2b91d;stroke:#805600;stroke-width:2}}</style><rect x="24" y="22" width="1152" height="56" rx="10" class="gold"/><text x="44" y="58" class="h">{html.escape(WARNING)}</text><text x="40" y="122" class="title">{html.escape(title)}</text>{body}</svg>'''


def write_svgs() -> None:
    body = '''<rect x="180" y="190" width="720" height="480" rx="16" class="part"/><text x="455" y="450" class="h">360 x 240 x 6 mm</text><circle cx="210" cy="220" r="11" class="d"/><circle cx="870" cy="220" r="11" class="d"/><circle cx="210" cy="640" r="11" class="d"/><circle cx="870" cy="640" r="11" class="d"/><text x="920" y="220" class="t">4 x dia5.5 foot axes at +/-165, +/-105</text><text x="920" y="270" class="t">14 x dia3.0 PCB axes</text><text x="920" y="315" class="t">8 x dia3.4 cover axes</text><text x="920" y="360" class="t">R8 corners</text><text x="920" y="405" class="t">General +/-0.20 mm</text><path d="M180 155h720M180 145v20M900 145v20" class="d"/><text x="505" y="148" class="t">360 mm</text><path d="M135 190v480M125 190h20M125 670h20" class="d"/><text x="75" y="445" class="t" transform="rotate(-90 75 445)">240 mm</text>'''
    (OUT / "base-panel-fabrication-drawing.svg").write_text(svg_shell("E1 base-panel fabrication candidate", body), encoding="utf-8", newline="\n")

    body = '''<rect x="180" y="260" width="660" height="210" class="part"/><rect x="216" y="290" width="588" height="156" fill="white" stroke="#0b4f91" stroke-width="2"/><circle cx="198" cy="278" r="10" class="d"/><circle cx="822" cy="278" r="10" class="d"/><circle cx="198" cy="452" r="10" class="d"/><circle cx="822" cy="452" r="10" class="d"/><path d="M245 260v-170h530v170" class="part"/><text x="420" y="180" class="h">98 x 58 x 28 shell</text><text x="420" y="215" class="t">3 mm sides and top; 92 x 52 cavity</text><text x="875" y="290" class="t">110 x 70 x 3 flange</text><text x="875" y="335" class="t">4 x dia3.4 on +/-52, +/-32</text><text x="875" y="380" class="t">NO FIELD-PORT OPENING</text><text x="875" y="425" class="t">General +/-0.20 mm</text>'''
    (OUT / "carrier-cover-fabrication-drawing.svg").write_text(svg_shell("Carrier field-port cover fabrication candidate", body), encoding="utf-8", newline="\n")

    body = '''<rect x="175" y="275" width="735" height="300" class="part"/><rect x="187" y="287" width="711" height="264" fill="white" stroke="#0b4f91" stroke-width="2"/><text x="440" y="430" class="h">245 x 150 x 16 mm</text><text x="440" y="465" class="t">2 mm base and walls; OPEN TOP</text><text x="940" y="300" class="t">Mechanically fasten corners</text><text x="940" y="345" class="t">or qualify a bond process</text><text x="940" y="390" class="t">No loose chips or sharp edges</text><text x="940" y="435" class="t">General +/-0.30 mm</text>'''
    (OUT / "under-panel-raceway-fabrication-drawing.svg").write_text(svg_shell("Under-panel logic-cable raceway candidate", body), encoding="utf-8", newline="\n")

    body = '''<rect x="90" y="180" width="1010" height="500" rx="22" class="part"/><text x="130" y="235" class="h">14 x PCB stack</text><text x="130" y="275" class="t">6 mm panel + 3 mm PC pedestal + 8 mm WA-SPAII + 1.6 mm PCB</text><text x="130" y="315" class="t">M2.5 x 12 bottom screw / M2.5 x 6 top screw</text><text x="130" y="385" class="h">8 x cover stack</text><text x="130" y="425" class="t">3 mm flange + 6 mm panel + M3 x 12 screw + M3 nut</text><text x="130" y="495" class="h">4 x foot stack</text><text x="130" y="535" class="t">7.9 mm machined PC riser + recessed M5 x 16 + M5 nut</text><text x="130" y="575" class="t">10.1 mm 3M SJ5309 bonded below = 18.0 mm total nominal foot</text><text x="130" y="635" class="t">Every torque, fit, adhesion and dimensional inspection remains NOT EXECUTED.</text>'''
    (OUT / "fixture-hardware-assembly-map.svg").write_text(svg_shell("E1 fixture hardware assembly map", body), encoding="utf-8", newline="\n")


def update_fixture_records() -> None:
    bom_path = OUT / "candidate-bom.csv"
    old = rows(bom_path)
    keep = [row for row in old if row["item"] not in {"E1-01", "E1-02", "E1-03", "E1-04", "E1-05", "E1-06"}]
    replacement = [
        {"item": "E1-01", "quantity": 1, "part": "base panel", "candidate": "SABIC LEXAN 9034 CLEAR PC; 360 x 240 x 6 MM", "fabrication": "3-AXIS CNC; DXF/STEP/DRAWING PROVIDED; FAI OPEN", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-02", "quantity": 2, "part": "flanged carrier field-port cover", "candidate": "SABIC LEXAN 9034 CLEAR PC; 3 MM WALL/FLANGE", "fabrication": "3-AXIS CNC; STEP/STL/DRAWING PROVIDED; RECEIVED FIT OPEN", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-03", "quantity": 14, "part": "M2.5 PCB pedestal + standoff", "candidate": "PROJECT E1-PED-6X3 + WUERTH 970080155", "fabrication": "CNC PEDESTAL + PURCHASE STANDOFF", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-04", "quantity": 14, "part": "M2.5 top/bottom screw pair", "candidate": "50M025045P006 + 50M025045D012", "fabrication": "PURCHASE; TORQUE/FIT PROCESS OPEN", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-05", "quantity": 8, "part": "M3 cover screw/nut set", "candidate": "50M030050P012 + 496241", "fabrication": "PURCHASE; TORQUE/WITNESS PROCESS OPEN", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-06", "quantity": 4, "part": "18 mm bench-foot stack", "candidate": "PROJECT E1-FOOT-223X79 + SJ5309 + ITEM 10374603 + 0030030000VR", "fabrication": "CNC RISER + PURCHASE HARDWARE; ADHESION/LOAD TEST OPEN", "release": "NO", "warning": old[0]["warning"]},
        {"item": "E1-06A", "quantity": 1, "part": "under-panel logic raceway", "candidate": "SABIC LEXAN 9034; 245 x 150 x 16; 2 MM WALL/BASE", "fabrication": "CNC CUT; JOINING METHOD/FAI OPEN", "release": "NO", "warning": old[0]["warning"]},
    ]
    write_csv(bom_path, replacement + keep)

    holds_path = OUT / "open-holds.csv"
    holds = rows(holds_path)
    for row in holds:
        if row["hold_id"] == "E1-H03":
            row["unresolved"] = "panel, covers, raceway, PCB stacks and foot stacks now have defined CAD and exact material/hardware candidates but remain unbuilt/uninspected"
            row["closure"] = "supplier COCs, DFM, fabrication travelers, FAI, received fit, torque/creep, foot adhesion/load and as-built review"
    write_csv(holds_path, holds)

    status_path = OUT / "e1-fixture-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "fixture_hardware_candidate_present": True,
        "fixture_material_candidate": "SABIC LEXAN 9034 POLYCARBONATE",
        "pcb_support_stack_count": 14,
        "cover_fastener_count": 8,
        "bench_foot_stack_count": 4,
        "fabrication_drawing_count": 4,
        "dimensional_inspection_count": 10,
        "fixture_hardware_built": False,
        "fixture_hardware_received_fit_validated": False,
        "fixture_hardware_fai_executed": False,
        "fixture_hardware_review_accepted": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    root_status_path = BODY / "package-status.json"
    root_status = json.loads(root_status_path.read_text(encoding="utf-8"))
    root_status.update({
        "e1_fixture_hardware_candidate_present": True,
        "e1_fixture_hardware_selection_count": 13,
        "e1_fixture_fabrication_drawing_count": 4,
        "e1_fixture_hardware_built": False,
        "e1_fixture_hardware_validated": False,
    })
    root_status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_docs() -> None:
    readme = OUT / "README.md"
    block = f"""## Physical fixture hardware and fabrication definition

**{WARNING}**

The fixture CAD now contains the hardware it previously only named. Fourteen board locations use a 3 mm project-owned LEXAN pedestal, an 8 mm Wuerth `970080155` internal/internal M2.5 standoff, and separate 12 mm bottom / 6 mm top nylon screws. The two carrier covers now have 3 mm flanges, four physical fastener holes each, and eight M3 screw/nut stacks. Four 18 mm bench feet combine a machined 7.9 mm LEXAN riser with a recessed M5 fastener and a 10.1 mm 3M `SJ5309` nonslip bumper.

The base, covers, raceway, pedestals and foot risers are dimensioned for SABIC LEXAN 9034 sheet. STEP/GLB hardware CAD, four readable fabrication drawings, exact candidate/order-code registers and ten first-article inspections are included. Supplier stock, machining process, torque, received fit, adhesion, load, FAI and qualified acceptance remain open.
"""
    replace_marker(readme, "<!-- HR30-E1-FIXTURE-HARDWARE-P01-START -->", "<!-- HR30-E1-FIXTURE-HARDWARE-P01-END -->", block)

    section = f'''<section id="e1-fixture-hardware" class="panel"><h2>The fixture hardware is now physically defined</h2><div class="grid"><article><div class="metric">14</div><p>two-ended PCB support stacks with real pedestals and threaded standoffs</p></article><article><div class="metric">8</div><p>new physical cover fastener locations</p></article><article><div class="metric">4</div><p>18 mm riser-and-Bumpon foot stacks</p></article><article class="hold"><div class="metric">0</div><p>fabricated or accepted hardware sets</p></article></div><model-viewer src="HR30_E1_fixture_hardware_candidate.glb" camera-controls shadow-intensity="0.8" exposure="1.05" alt="Interactive HR-30 E1 fixture hardware showing PCB supports, cover fasteners and four foot stacks"></model-viewer><p>The base, covers, raceway, PCB pedestals and foot risers are dimensioned for clear SABIC LEXAN 9034 polycarbonate. Exact Wuerth, Essentra and 3M candidates are bound to the modeled stacks.</p><p><a href="HR30_E1_fixture_hardware_candidate.step">hardware STEP</a> &middot; <a href="base-panel-fabrication-drawing.svg">base drawing</a> &middot; <a href="carrier-cover-fabrication-drawing.svg">cover drawing</a> &middot; <a href="under-panel-raceway-fabrication-drawing.svg">raceway drawing</a> &middot; <a href="fixture-hardware-assembly-map.svg">assembly map</a></p><div class="scroll"><table><thead><tr><th>Stack</th><th>Count</th><th>Candidate hardware</th><th>Validation</th></tr></thead><tbody><tr><td>PCB</td><td>14</td><td>970080155 + M2.5 x 12 / x 6</td><td>Not executed</td></tr><tr><td>Cover</td><td>8</td><td>M3 x 12 + M3 nut</td><td>Not executed</td></tr><tr><td>Foot</td><td>4</td><td>M5 x 16 + M5 nut + SJ5309</td><td>Not executed</td></tr></tbody></table></div><p><strong>{html.escape(AUTHORITY)}.</strong></p></section>'''
    index = OUT / "index.html"
    text = index.read_text(encoding="utf-8")
    start, end = "<!-- HR30-E1-FIXTURE-HARDWARE-P01-START -->", "<!-- HR30-E1-FIXTURE-HARDWARE-P01-END -->"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before.rstrip() + after.lstrip()
    if "</main>" not in text:
        raise RuntimeError("E1 guide lost main element")
    text = text.replace("</main>", f"{start}\n{section}\n{end}\n</main>", 1)
    index.write_text(text, encoding="utf-8", newline="\n")

    root_block = """## E1 fixture hardware and fabrication

The controls-only fixture now has [interactive hardware CAD and readable fabrication drawings](electrical/e1-controls-only-fixture-p0.1/index.html#e1-fixture-hardware). Its 14 PCB stacks, eight cover fasteners and four full-height foot stacks are dimensioned and bound to exact candidate hardware. The covers now have real flanges and mounting holes. Fabrication, received fit, torque, adhesive/load testing, FAI and qualified acceptance remain open."""
    replace_marker(BODY / "README.md", "<!-- HR30-E1-FIXTURE-HARDWARE-P01-START -->", "<!-- HR30-E1-FIXTURE-HARDWARE-P01-END -->", root_block)


def write_status() -> None:
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "material_selection_count": 4,
        "hardware_selection_count": 13,
        "pcb_support_stack_count": 14,
        "cover_fastener_stack_count": 8,
        "bench_foot_stack_count": 4,
        "fabrication_drawing_count": 4,
        "dimensional_inspection_count": 10,
        "hardware_step_present": (OUT / "HR30_E1_fixture_hardware_candidate.step").is_file(),
        "hardware_glb_present": (OUT / "HR30_E1_fixture_hardware_candidate.glb").is_file(),
        "fixture_built": False,
        "supplier_coc_received": False,
        "machining_process_released": False,
        "received_fit_validated": False,
        "torque_creep_validated": False,
        "foot_adhesion_load_validated": False,
        "fai_executed": False,
        "qualified_review_accepted": False,
        "fabrication_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "fixture-hardware-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")


def generate_into_fixture() -> dict:
    for required in (
        OUT / "HR30_E1_controls_only_fixture_candidate.step",
        OUT / "HR30_E1_fixture_hardware_candidate.step",
        OUT / "HR30_E1_fixture_hardware_candidate.glb",
    ):
        if not required.is_file():
            raise RuntimeError(f"fixture hardware prerequisite missing: {required}")
    write_registers()
    write_svgs()
    update_fixture_records()
    write_docs()
    write_status()
    shutil.copy2(__file__, OUT / "e1-fixture-hardware-source.py")
    return {"hardware_selection_count": 13, "pcb_stack_count": 14, "cover_stack_count": 8, "foot_stack_count": 4}


def main() -> int:
    print(json.dumps(generate_into_fixture(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
