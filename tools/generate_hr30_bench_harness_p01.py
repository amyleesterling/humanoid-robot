#!/usr/bin/env python3
"""Generate the HR-30 one-axis commissioning bench-harness package P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
STATION = WB / "electrical" / "axis-commissioning-station-p0.1"
OUT = STATION / "bench-harness-p0.1"
REL_STATION = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1"
WARNING = "PRELIMINARY - BENCH-HARNESS FABRICATION CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
WHOLE_WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_block(path: Path, start: str, end: str, block: str, before: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", text)
    if before not in text:
        raise RuntimeError(f"integration anchor missing in {path}: {before}")
    path.write_text(text.replace(before, block + before), encoding="utf-8")


def schematic_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="760" viewBox="0 0 1500 760" role="img" aria-labelledby="title desc">
<title id="title">HR-30 one-axis commissioning bench harness</title><desc id="desc">A red positive and black return lead connect one current-limited Keysight output to the keyed two-contact Mini-Fit input of the ROBOTIS Power Hub. Only one actuator cable is fitted.</desc>
<rect width="1500" height="760" fill="#f8fcff"/><rect x="24" y="24" width="1452" height="92" rx="16" fill="#fff0b5" stroke="#a86f00" stroke-width="4"/><text x="52" y="62" font-family="system-ui" font-size="22" font-weight="800" fill="#082f58">{WARNING}</text><text x="52" y="94" font-family="system-ui" font-size="18" fill="#082f58">All assembly and inspection steps are de-energized. Qualified approval and a signed connection procedure remain open.</text>
<rect x="60" y="210" width="280" height="250" rx="24" fill="#d6f1ff" stroke="#082f58" stroke-width="5"/><text x="88" y="260" font-family="system-ui" font-size="28" font-weight="800" fill="#082f58">Keysight E36313A</text><text x="88" y="300" font-family="system-ui" font-size="20" fill="#082f58">one output only</text><circle cx="290" cy="355" r="27" fill="#c62828"/><text x="80" y="363" font-family="system-ui" font-size="20" fill="#082f58">RED +</text><circle cx="290" cy="420" r="27" fill="#111"/><text x="80" y="428" font-family="system-ui" font-size="20" fill="#082f58">BLACK -</text>
<path d="M317 355 H960" stroke="#d32424" stroke-width="18" fill="none"/><path d="M317 420 H960" stroke="#111" stroke-width="18" fill="none"/><text x="455" y="337" font-family="system-ui" font-size="20" font-weight="700" fill="#a21414">BH-W01 BU-0061-M-39-2, RED, 18 AWG</text><text x="455" y="458" font-family="system-ui" font-size="20" font-weight="700" fill="#082f58">BH-W02 BU-0061-M-39-0, BLACK, 18 AWG</text>
<rect x="960" y="304" width="150" height="172" rx="18" fill="#f2b928" stroke="#082f58" stroke-width="5"/><text x="982" y="340" font-family="system-ui" font-size="22" font-weight="800" fill="#082f58">J1</text><text x="982" y="369" font-family="system-ui" font-size="18" fill="#082f58">39-01-2020</text><circle cx="1000" cy="405" r="20" fill="#111"/><text x="1030" y="412" font-family="system-ui" font-size="19" fill="#082f58">1 GND</text><circle cx="1000" cy="454" r="20" fill="#c62828"/><text x="1030" y="461" font-family="system-ui" font-size="19" fill="#082f58">2 VDD</text>
<rect x="1160" y="210" width="280" height="250" rx="24" fill="#d6f1ff" stroke="#082f58" stroke-width="5"/><text x="1190" y="260" font-family="system-ui" font-size="27" font-weight="800" fill="#082f58">ROBOTIS PHB</text><text x="1190" y="300" font-family="system-ui" font-size="19" fill="#082f58">Mini-Fit input only</text><text x="1190" y="344" font-family="system-ui" font-size="19" fill="#082f58">barrel EMPTY</text><text x="1190" y="378" font-family="system-ui" font-size="19" fill="#082f58">screw input EMPTY</text><text x="1190" y="418" font-family="system-ui" font-size="19" font-weight="800" fill="#082f58">one X3P OR X4P</text>
<path d="M1110 390 H1160" stroke="#082f58" stroke-width="8"/><rect x="445" y="540" width="610" height="150" rx="20" fill="#fff" stroke="#14689c" stroke-width="4"/><text x="478" y="580" font-family="system-ui" font-size="23" font-weight="800" fill="#082f58">Independent de-energized inspection</text><text x="478" y="617" font-family="system-ui" font-size="19" fill="#082f58">1. J1 pin 1 to BLACK return; J1 pin 2 to RED positive.</text><text x="478" y="650" font-family="system-ui" font-size="19" fill="#082f58">2. No cross-short; terminal lock and strain-free 12.7 mm minimum free lead.</text><text x="478" y="680" font-family="system-ui" font-size="19" fill="#082f58">3. As-built record and qualified signoff required before connection.</text></svg>'''


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "harness-assembly-register.csv", [{
        "assembly_id":"BH-A01","description":"current-limited source to U2D2 Power Hub Mini-Fit input lead","quantity":1,
        "source_end":"manufacturer-assembled Mueller BU-0061-M-39-2 red and BU-0061-M-39-0 black shrouded 4 mm plugs","load_end":"Molex 39-01-2020 with two 39-00-0038 female contacts",
        "conductor_count":2,"catalog_nominal_length":"39 in / 990.6 mm before sacrificial tin-dipped-tip removal","finished_length":"AS-MEASURED AFTER COMPLETE TIN-DIPPED-TIP REMOVAL AND MINI-FIT TERMINATION",
        "configuration_limit":"11.0 V / 0.25 A first power; 2.0 A station absolute configuration ceiling",
        "allowed_role":"one mechanically restrained and whole-body-disconnected actuator only","state":"DESIGN COMPLETE / ASSEMBLY NOT EXECUTED","authority":AUTHORITY,
    }])
    write_csv(OUT / "conductor-preparation-register.csv", [
        {"wire_id":"BH-W01","function":"VDD positive","color":"RED","manufacturer_part":"Mueller BU-0061-M-39-2","material":"18 AWG (413/44) UL 3577 highly flexible silicone cable; conductor plating and jacket OD not published","catalog_nominal_length":"39 in / 990.6 mm; tolerance not published","open_end_preparation":"cut off and discard the complete manufacturer tin-dipped segment; no fused/dipped segment or solder wick may enter the crimp zone","j1_strip_length_mm":"3.00-3.30","j1_target_strip_mm":"3.15","j1_conductor_crimp_height_mm":"1.00-1.10","minimum_pull_force_n":"88.0","source_end_preparation":"manufacturer-assembled shrouded banana; no field termination","free_wire_at_j1_mm":"12.7 minimum before first tie or imposed bend","label":"BH-W01 VDD RED","state":"NOT ASSEMBLED"},
        {"wire_id":"BH-W02","function":"DC return / GND","color":"BLACK","manufacturer_part":"Mueller BU-0061-M-39-0","material":"18 AWG (413/44) UL 3577 highly flexible silicone cable; conductor plating and jacket OD not published","catalog_nominal_length":"39 in / 990.6 mm; tolerance not published","open_end_preparation":"cut off and discard the complete manufacturer tin-dipped segment; no fused/dipped segment or solder wick may enter the crimp zone","j1_strip_length_mm":"3.00-3.30","j1_target_strip_mm":"3.15","j1_conductor_crimp_height_mm":"1.00-1.10","minimum_pull_force_n":"88.0","source_end_preparation":"manufacturer-assembled shrouded banana; no field termination","free_wire_at_j1_mm":"12.7 minimum before first tie or imposed bend","label":"BH-W02 GND BLACK","state":"NOT ASSEMBLED"},
    ])
    write_csv(OUT / "connector-contact-map.csv", [
        {"connector":"PS1-RED","manufacturer_part":"Mueller BU-0061-M-39-2 manufacturer-assembled plug","contact":"single","function":"VDD positive","wire_id":"BH-W01","mate":"approved E36313A positive output jack","polarity_check":"J1-2 continuity only; open to J1-1","state":"NOT EXECUTED"},
        {"connector":"PS1-BLACK","manufacturer_part":"Mueller BU-0061-M-39-0 manufacturer-assembled plug","contact":"single","function":"DC return / GND","wire_id":"BH-W02","mate":"same E36313A channel return jack","polarity_check":"J1-1 continuity only; open to J1-2","state":"NOT EXECUTED"},
        {"connector":"J1","manufacturer_part":"Molex 39-01-2020 / 39-00-0038","contact":"1","function":"GND","wire_id":"BH-W02","mate":"PHB power pin 1","polarity_check":"BLACK only","state":"NOT EXECUTED"},
        {"connector":"J1","manufacturer_part":"Molex 39-01-2020 / 39-00-0038","contact":"2","function":"VDD","wire_id":"BH-W01","mate":"PHB power pin 2","polarity_check":"RED only","state":"NOT EXECUTED"},
    ])
    write_csv(OUT / "tooling-register.csv", [
        {"tool_id":"BH-T01","manufacturer":"Molex","order_code":"63819-0901","description":"Type 4D hand crimp tool for Mini-Fit Jr male/female terminals, 18-24 AWG","document":"638190901 Rev D, 2025-03-31","application":"39-00-0038 on received Mueller 18 AWG lead after compatibility inspection","disposition":"CANDIDATE; RECEIPT/CALIBRATION/CRIMP VALIDATION REQUIRED"},
        {"tool_id":"BH-T02","manufacturer":"Molex","order_code":"11-03-0044","description":"HT60630B extraction tool","document":"ATS-011030044 Rev N, 2023-05-05","application":"remove a misinserted 39-00-0038; extracted terminal must not be reused","disposition":"CANDIDATE; RECEIPT INSPECTION REQUIRED"},
        {"tool_id":"BH-T03","manufacturer":"Mitutoyo","order_code":"342-271-30","description":"Series 342 metric Digimatic crimp-height micrometer; pointed spindle and blade anvil; 0-20 mm range; 0.001 mm resolution; +/-0.003 mm stated accuracy","document":"current official Series 342 product page; revision/date not stated","application":"measure the 1.00-1.10 mm conductor crimp height at the specified crimp section; received calibration certificate and measurement-method qualification required","disposition":"CANDIDATE SELECTED; RECEIPT/CALIBRATION/MEASUREMENT-SYSTEM VALIDATION REQUIRED"},
        {"tool_id":"BH-T04","manufacturer":"Mark-10","order_code":"WT-205M + CERT","description":"motorized wire-crimp pull tester with installed terminal turret and wedge grip; 1000 N capacity; 0.5 N resolution; +/-0.2% full-scale stated accuracy","document":"32-1278 Rev 1225; CERT is certificate of calibration with 10 data points","application":"axial destructive coupon at 25 +/-6 mm/min; result must exceed 88.0 N with the insulation crimp removed from influence; received Mini-Fit/sample grip suitability must be confirmed","disposition":"CANDIDATE SELECTED; RECEIPT/CALIBRATION/GRIP-SUITABILITY/METHOD VALIDATION REQUIRED"},
        {"tool_id":"BH-T05","manufacturer":"KNIPEX","order_code":"95 11 165","description":"cable shears for copper and aluminum single/multi-stranded wire; precision-ground blades; clean cut without crushing/deformation","document":"current official product page; revision/date not stated","application":"remove and discard the complete tin-dipped segment before stripping; received 413/44 lead cut quality must be inspected","disposition":"CANDIDATE SELECTED; RECEIPT/COUPON VALIDATION REQUIRED"},
        {"tool_id":"BH-T06","manufacturer":"KNIPEX","order_code":"12 12 14","description":"form-fit automatic wire stripper for 16-26 AWG including silicone insulation; replaceable shaped blades and length stop","document":"current official product page; revision/date not stated","application":"strip fresh 18 AWG conductor to 3.00-3.30 mm; do not infer the stop setting; independently measure strip length and inspect for zero cut/nicked strands on received 413/44 lead","disposition":"CANDIDATE SELECTED; RECEIPT/SETUP/COUPON VALIDATION REQUIRED"},
    ])
    write_csv(OUT / "assembly-traveler.csv", [
        {"step":"A01","operation":"verify exact received Mueller/Molex part numbers, colors, lot/traceability, catalog nominal length and undamaged insulation","acceptance":"BU-0061-M-39-2 red and -39-0 black plus exact Molex parts; record lots/photos/as-received lengths","record":"BH-R01","state":"NOT EXECUTED","stop_rule":"STOP on mismatch"},
        {"step":"A02","operation":"remove and discard each complete tin-dipped free-end segment; record discarded and remaining finished lengths","acceptance":"fresh flexible strands at the preparation end; no fused/dipped segment or solder wick remains in the future crimp zone","record":"BH-R02/BH-R03","state":"NOT EXECUTED","stop_rule":"STOP if the dipped boundary is ambiguous"},
        {"step":"A03","operation":"inspect received cable compatibility and prepare Mini-Fit ends","acceptance":"jacket OD <=3.1 mm; conductor construction accepted by qualified reviewer; strip 3.00-3.30 mm; no cut/nicked strands","record":"BH-R04/BH-R05","state":"NOT EXECUTED","stop_rule":"STOP on unknown/incompatible material, oversize jacket or damaged strands"},
        {"step":"A04","operation":"make and destructively test one process coupon before production contacts","acceptance":"18 AWG conductor crimp height 1.00-1.10 mm; axial pull at 25 +/-6 mm/min; pull force >88.0 N; insulation crimp removed from pull influence","record":"BH-R06","state":"NOT EXECUTED","stop_rule":"STOP until calibrated tools, suitable grips and the process pass"},
        {"step":"A05","operation":"crimp production contacts with 63819-0901 18 AWG profile","acceptance":"full ratchet cycle; visible conductor brush/bellmouth; crimp height 1.00-1.10 mm; no deformation","record":"BH-R07/BH-R08","state":"NOT EXECUTED","stop_rule":"reject nonconforming contact"},
        {"step":"A06","operation":"insert black contact into J1 cavity 1 and red contact into J1 cavity 2","acceptance":"stop tab down per Molex application specification; audible/physical lock; gentle retention check","record":"BH-R09","state":"NOT EXECUTED","stop_rule":"do not force; extracted contact may not be reused"},
        {"step":"A07","operation":"inspect manufacturer-assembled Mueller source ends without modifying them","acceptance":"shrouds, strain reliefs, plugs and cable exits undamaged; red/black identity matches conductor and contact map","record":"BH-R10","state":"NOT EXECUTED","stop_rule":"quarantine any damaged, loose or mismarked lead"},
        {"step":"A08","operation":"apply labels and dress paired lead","acceptance":"BH-W01/BH-W02 labels readable; 12.7 mm minimum relaxed free length behind J1; no tight tie or sharp bend","record":"BH-R11","state":"NOT EXECUTED","stop_rule":"rework strain/bend violation"},
        {"step":"A09","operation":"independent de-energized continuity/polarity/short inspection","acceptance":"red plug to J1-2 only; black plug to J1-1 only; open between circuits and to exposed housing","record":"BH-R12","state":"NOT EXECUTED","stop_rule":"quarantine on any ambiguity"},
        {"step":"A10","operation":"as-built review and bag/label assembly","acceptance":"all records complete; qualified reviewer signs; warning label attached","record":"BH-R13","state":"NOT EXECUTED","stop_rule":"no connection without separate authorization"},
    ])
    write_csv(OUT / "as-built-record.csv", [
        {"record_id":"BH-R01","field":"received part/lot/photo record","required_value":"all exact candidates or documented approved deviation","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R02","field":"BH-W01 red tin-dipped-tip removal and finished length","required_value":"complete dipped segment removed; discarded and finished lengths recorded","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R03","field":"BH-W02 black tin-dipped-tip removal and finished length","required_value":"complete dipped segment removed; discarded and finished lengths recorded","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R04","field":"BH-W01 OD/material/strip/strand inspection","required_value":"OD <=3.1 mm; accepted conductor construction; 3.00-3.30 mm; zero damaged strands; no fused/dipped segment in crimp zone","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R05","field":"BH-W02 OD/material/strip/strand inspection","required_value":"OD <=3.1 mm; accepted conductor construction; 3.00-3.30 mm; zero damaged strands; no fused/dipped segment in crimp zone","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R06","field":"destructive crimp process coupon","required_value":"1.00-1.10 mm; axial pull at 25 +/-6 mm/min; >88.0 N; insulation crimp removed from influence","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R07","field":"BH-W01 production crimp height/visual","required_value":"1.00-1.10 mm and acceptable visual","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R08","field":"BH-W02 production crimp height/visual","required_value":"1.00-1.10 mm and acceptable visual","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R09","field":"terminal insertion/retention and cavity identity","required_value":"black J1-1; red J1-2; both locked","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R10","field":"manufacturer-assembled source-end inspection","required_value":"correct Mueller parts/colors; shrouds, plugs, strain reliefs and cable exits undamaged","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R11","field":"labels/free length/bend inspection","required_value":"labels correct; >=12.7 mm relaxed free lead at J1","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R12","field":"independent polarity/continuity/short test","required_value":"red-J1/2 only; black-J1/1 only; no cross-short","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R13","field":"final as-built disposition","required_value":"qualified signed acceptance plus separate connection procedure","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
    ])
    write_csv(OUT / "candidate-bom.csv", [
        {"item":"BH-01","quantity":1,"manufacturer":"Molex","order_code":"39-01-2020","description":"2-circuit Mini-Fit Jr receptacle housing","disposition":"CANDIDATE"},
        {"item":"BH-02","quantity":2,"manufacturer":"Molex","order_code":"39-00-0038","description":"5556 female crimp contact for 18 AWG","disposition":"CANDIDATE"},
        {"item":"BH-03","quantity":1,"manufacturer":"Mueller Electric","order_code":"BU-0061-M-39-2","description":"red 39 inch manufacturer-assembled shrouded-banana to tin-dipped 18 AWG silicone lead","disposition":"CANDIDATE; RECEIPT/COMPATIBILITY VALIDATION OPEN"},
        {"item":"BH-04","quantity":1,"manufacturer":"Mueller Electric","order_code":"BU-0061-M-39-0","description":"black 39 inch manufacturer-assembled shrouded-banana to tin-dipped 18 AWG silicone lead","disposition":"CANDIDATE; RECEIPT/COMPATIBILITY VALIDATION OPEN"},
        {"item":"BH-05","quantity":1,"manufacturer":"Molex","order_code":"63819-0901","description":"Mini-Fit Jr hand crimp tool","disposition":"CANDIDATE; RECEIPT/CALIBRATION OPEN"},
        {"item":"BH-06","quantity":1,"manufacturer":"Molex","order_code":"11-03-0044","description":"Mini-Fit extraction tool","disposition":"CANDIDATE"},
        {"item":"BH-07","quantity":"as required","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"durable wire and assembly warning labels","disposition":"SELECTION REQUIRED"},
        {"item":"BH-08","quantity":1,"manufacturer":"Mitutoyo","order_code":"342-271-30","description":"Series 342 metric Digimatic crimp-height micrometer","disposition":"CANDIDATE; RECEIPT/CALIBRATION/MEASUREMENT-SYSTEM VALIDATION OPEN"},
        {"item":"BH-09","quantity":1,"manufacturer":"Mark-10","order_code":"WT-205M","description":"motorized 1000 N wire-crimp pull tester with standard turret and wedge grip","disposition":"CANDIDATE; RECEIPT/GRIP-SUITABILITY/METHOD VALIDATION OPEN"},
        {"item":"BH-10","quantity":1,"manufacturer":"Mark-10","order_code":"CERT","description":"certificate of calibration with ten data points for WT-205M","disposition":"CANDIDATE; RECEIVED CERTIFICATE ACCEPTANCE OPEN"},
        {"item":"BH-11","quantity":1,"manufacturer":"KNIPEX","order_code":"95 11 165","description":"cable shears for complete tin-dipped-segment removal","disposition":"CANDIDATE; RECEIPT/COUPON VALIDATION OPEN"},
        {"item":"BH-12","quantity":1,"manufacturer":"KNIPEX","order_code":"12 12 14","description":"16-26 AWG form-fit stripper for silicone insulation","disposition":"CANDIDATE; RECEIPT/SETUP/COUPON VALIDATION OPEN"},
    ])
    write_csv(OUT / "primary-source-register.csv", [
        {"source_id":"MOLEX-TOOL","manufacturer":"Molex","document":"638190901 Rev D","document_date":"2025-03-31","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63819/638190901-000.pdf","verified_scope":"63819-0901; 39-00-0038; 18-24 AWG; 3.00-3.30 mm strip; 18 AWG 1.00-1.10 mm crimp-height and >88.0 N pull criteria"},
        {"source_id":"MOLEX-APPLICATION","manufacturer":"Molex","document":"55560002-AS Rev A1","document_date":"2025-01-09","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/555/5556/55560002-AS-000.pdf","verified_scope":"terminal handling/insertion; no live mate/unmate; 12.7 mm free wire for 2-circuit housing; extracted terminal not reused"},
        {"source_id":"MOLEX-PRODUCT","manufacturer":"Molex","document":"PS-5556-001 Rev H2","document_date":"2026-06-22","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/555/5556/PS-5556-001-001.pdf","verified_scope":"current Mini-Fit Jr product-system boundary; application-specific derating remains required"},
        {"source_id":"MOLEX-EXTRACT","manufacturer":"Molex","document":"ATS-011030044 Rev N","document_date":"2023-05-05","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/606/60630/ATS-011030044-001.pdf","verified_scope":"11-03-0044 applies to 39-00-0038"},
        {"source_id":"MUELLER-LEAD","manufacturer":"Mueller Electric","document":"DS-BU-0061-M-@; revision/date not stated","document_date":"live official data sheet accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://www.muellerelectric.com/product_files/21/DS-BU-0061-M-%40.pdf","verified_scope":"BU-0061-M family; manufacturer-assembled 4 mm shrouded banana; tin-dipped free end; 18 AWG 413/44 UL 3577 highly flexible silicone; 39 inch standard length; black suffix -0 and red suffix -2"},
        {"source_id":"MUELLER-LIST","manufacturer":"Mueller Electric","document":"Mueller UKCA and CE parts 101525","document_date":"2025-10-15","accessed":"2026-08-15","official_url":"https://ww2.muellerelectric.com/wp-content/uploads/2025/10/Mueller-UKCA-and-CE-parts-101525.pdf","verified_scope":"current official list includes BU-0061-M-39-0 black and BU-0061-M-39-2 red"},
        {"source_id":"ROBOTIS-PHB","manufacturer":"ROBOTIS","document":"live official Docs; revision not visible","document_date":"accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/","verified_scope":"3.5-24 V; 10 A maximum; one power input only; Mini-Fit pin 1 GND / pin 2 VDD"},
        {"source_id":"MITUTOYO-CRIMP","manufacturer":"Mitutoyo","document":"Series 342 Crimp Height Micrometer product page; revision/date not stated","document_date":"live official product page accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://dev.pim.mitutoyo.com/products/small-tool-instruments-and-data-management/micrometers/digimatic-micrometers/crimp-height-micrometer/","verified_scope":"342-271-30; pointed spindle/blade anvil; 0-20 mm; 0.001 mm resolution; +/-0.003 mm accuracy; instrument calibration and method acceptance remain open"},
        {"source_id":"MARK10-PULL","manufacturer":"Mark-10","document":"WT-205M data sheet 32-1278 Rev 1225","document_date":"2025-12","accessed":"2026-08-15","official_url":"https://mark-10.com/downloads/product-downloads/DataSheetWT-205M.pdf","verified_scope":"WT-205M; 1000 N capacity; 0.5 N resolution; +/-0.2% full-scale; 10-300 mm/min; installed turret and wedge grip; CERT option with 10 data points; sample/grip suitability remains open"},
        {"source_id":"KNIPEX-CUT","manufacturer":"KNIPEX","document":"95 11 165 product page; revision/date not stated","document_date":"live official product page accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://www.knipex-tools.com/products/cable-and-wire-rope-shears/cable-shears/cable-shears-1000v-insulated/9511165","verified_scope":"95 11 165; copper/aluminum single and multi-stranded cable; precision-ground blades; clean cut without crushing/deformation"},
        {"source_id":"KNIPEX-STRIP","manufacturer":"KNIPEX","document":"12 12 14 product page; revision/date not stated","document_date":"live official product page accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://www.knipex-tools.com/products/wire-strippers-and-dismantling-tools/automatic-wire-strippers/automatic-wire-stripper-mm2/121214","verified_scope":"12 12 14; 16-26 AWG; form-fit stripping of silicone and other difficult insulation; shaped blade and length stop; exact 3.00-3.30 mm setup and received 413/44 compatibility remain open"},
    ])
    write_csv(OUT / "open-holds.csv", [
        {"hold_id":"BH-H01","unresolved_evidence":"qualified approval of complete harness drawing, assembly traveler and inspection method","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H02","unresolved_evidence":"received exact Mueller leads, Molex connectors/tooling, Mitutoyo 342-271-30 calibration, Mark-10 WT-205M + CERT calibration data, KNIPEX tools, lot records and inspection status","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H03","unresolved_evidence":"received Mueller jacket OD and conductor construction compatibility; complete tin-dipped-segment removal; manufacturer source-end identity, fit and integrity inspection","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H04","unresolved_evidence":"executed destructive crimp coupon, production crimp-height and terminal-retention records","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H05","unresolved_evidence":"executed independent continuity, short and polarity inspection plus signed as-built disposition","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H06","unresolved_evidence":"separate qualified station connection and first-power authorization","state":"OPEN","authority":AUTHORITY},
    ])
    (OUT / "bench-harness.svg").write_text(schematic_svg(), encoding="utf-8")
    (OUT / "harness-status.json").write_text(json.dumps({
        "identifier":"HR30-AXIS-BENCH-HARNESS-P0.1","warning":WARNING,"assembly_count":1,"conductor_count":2,
        "physical_connector_contact_count":4,"exact_mini_fit_tool_candidate_selected":True,"exact_inspection_tool_candidates_selected":True,"exact_cut_and_strip_tool_candidates_selected":True,"exact_cut_and_strip_definition_present":True,
        "assembly_traveler_step_count":10,"as_built_record_count":13,"manufacturer_assembled_source_end_selected":True,
        "source_end_termination_process_selected":True,"received_lead_compatibility_validated":False,
        "physical_assembly_executed":False,"inspection_executed":False,"qualified_review_complete":False,
        "connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f'''# HR-30 axis-commissioning bench harness P0.1

**{WARNING}**

This package defines the exact two-conductor station power lead from one current-limited Keysight output to the Mini-Fit input of the ROBOTIS U2D2 Power Hub. It uses exact 39 inch red and black Mueller manufacturer-assembled shrouded-banana leads and fixes the Mini-Fit contact map, sacrificial tin-dipped-tip removal, strip length, 18 AWG crimp-height band, 25 +/-6 mm/min process-coupon pull method, free-lead rule, exact candidate preparation/inspection tools, assembly traveler and as-built record. Received cable OD/conductor compatibility, tool receipt/calibration and suitability, physical fabrication, inspection, qualified review and every connection/power/motion authority remain open.
''', encoding="utf-8")
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 bench harness P0.1</title><style>:root{{--navy:#082f58;--blue:#14689c;--sky:#d6f1ff;--gold:#f2b928;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1200px;margin:auto}}h1{{font-size:clamp(2.2rem,6vw,4.8rem);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(1.7rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #a86f00;background:#fff0b5;border-radius:16px;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:1rem;margin:1.5rem 0}}article,.panel{{padding:1rem;background:#fff;border:2px solid var(--blue);border-radius:16px}}.drawing{{overflow:auto;border:2px solid var(--blue);border-radius:16px;background:#fff}}.drawing img{{display:block;width:100%;min-width:820px;height:auto}}.tablewrap{{overflow:auto;border:2px solid var(--blue);border-radius:16px}}table{{border-collapse:collapse;width:100%;min-width:900px;background:#fff}}th,td{{padding:.8rem;border-bottom:1px solid #c7dfec;text-align:left;font-size:14px;vertical-align:top}}th{{background:var(--navy);color:#fff}}a{{color:#075d98;font-weight:800}}code{{font-size:14px}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Two wires. One keyed input. Zero guessed contacts.</h1><p>The station harness is now an assembly-controlled artifact, not a line on a schematic.</p></div></header><main><div class="hold"><h2>Still not permission to build or connect</h2><p>Exact tooling candidates remove purchase ambiguity; they do not replace received calibration, sample-fit checks, coupon results, qualified review or a signed connection procedure.</p></div><h2>Point-to-point assembly drawing</h2><div class="drawing"><img src="bench-harness.svg" alt="Bench harness drawing from Keysight output to the keyed ROBOTIS Power Hub input"></div><div class="grid"><article><h3>Exact source leads</h3><p>Red BU-0061-M-39-2 and black BU-0061-M-39-0 are 39-inch, 18 AWG shrouded-banana leads. Their tin-dipped tips are sacrificial.</p></article><article><h3>Measured crimp and pull</h3><p>342-271-30 measures the 1.00-1.10 mm crimp. WT-205M + CERT applies the axial pull at 25 +/-6 mm/min; the coupon must exceed 88.0 N.</p></article><article><h3>Controlled wire preparation</h3><p>95 11 165 removes the entire dipped segment. 12 12 14 strips the fresh silicone lead; every 3.00-3.30 mm result and every strand still requires inspection.</p></article><article><h3>J1 is explicit</h3><p>Cavity 1 is BLACK/GND. Cavity 2 is RED/VDD. The PHB barrel and screw inputs stay empty.</p></article></div><h2>Assembly traveler</h2><div class="tablewrap"><table><thead><tr><th>Step</th><th>Operation</th><th>Acceptance</th><th>Stop rule</th></tr></thead><tbody>{''.join(f'<tr><td>{s}</td><td>{o}</td><td>{a}</td><td>{stop}</td></tr>' for s,o,a,stop in [("A01","Verify exact Mueller and Molex parts","Record identity, lots, photos and received lengths","Stop on mismatch"),("A02","Remove tin-dipped free-end segments","No fused/dipped segment in either crimp zone","Stop if boundary is ambiguous"),("A03","Inspect and prepare Mini-Fit ends","OD <=3.1 mm; 3.00-3.30 mm strip; zero damaged strands","Stop on incompatibility"),("A04","Destructive process coupon","1.00-1.10 mm; 25 +/-6 mm/min; >88.0 N","Stop until calibrated tools, suitable grips and the process pass"),("A05-A06","Crimp and insert","black J1-1; red J1-2; both locked","Reject nonconformance"),("A07","Inspect manufacturer source ends","Correct, undamaged shrouds/plugs/strain reliefs","Quarantine damage or mismatch"),("A08-A10","Label, inspect, sign","continuity/polarity/short and as-built complete","No connection without authority")])}</tbody></table></div><p><a href="assembly-traveler.csv">complete traveler</a> · <a href="as-built-record.csv">as-built record</a> · <a href="conductor-preparation-register.csv">cut and crimp register</a> · <a href="connector-contact-map.csv">contact map</a> · <a href="tooling-register.csv">tooling</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="open-holds.csv">open holds</a></p></main></body></html>''', encoding="utf-8")


def integrate() -> None:
    shutil.copy2(Path(__file__), OUT / "bench-harness-source.py")
    station_status_path = STATION / "commissioning-status.json"
    status = json.loads(station_status_path.read_text(encoding="utf-8"))
    status.update({
        "bench_harness_design_present":True,"bench_harness_assembly_count":1,"bench_harness_conductor_count":2,
        "bench_harness_exact_mini_fit_tool_selected":True,"bench_harness_exact_inspection_tools_selected":True,"bench_harness_exact_preparation_tools_selected":True,"bench_harness_manufacturer_assembled_source_end_selected":True,
        "bench_harness_source_end_process_selected":True,"bench_harness_received_lead_compatibility_validated":False,
        "bench_harness_physically_assembled":False,"bench_harness_inspection_executed":False,"bench_harness_qualified_review_complete":False,
    })
    station_status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds_path = STATION / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "CS-H04":
            row["unresolved_evidence"] = "received Mueller lead identity/length/jacket OD/conductor construction, complete tin-dipped-segment removal, received/calibrated 63819-0901, 342-271-30 and WT-205M + CERT, received 11-03-0044/95 11 165/12 12 14 tools, executed 25 +/-6 mm/min 18 AWG Mini-Fit crimp-height/pull/polarity records and signed BH-A01 as-built disposition"
    write_csv(holds_path, holds)
    start, end = "<!-- BENCH-HARNESS-P01 START -->", "<!-- BENCH-HARNESS-P01 END -->"
    block = f'''{start}<h2>Assembly-controlled bench harness</h2><div class="panel"><p>The two-wire source lead now uses exact manufacturer-assembled Mueller leads, an exact Mini-Fit contact map and exact candidate crimp, measurement, pull-test, cutting and silicone-stripping tools. The traveler controls the 1.00-1.10 mm crimp and 25 +/-6 mm/min, greater-than-88 N coupon. Receipt, calibration, sample compatibility and all physical evidence remain open.</p><p><a href="bench-harness-p0.1/index.html">Open the interactive bench-harness guide</a> · <a href="bench-harness-p0.1/bench-harness.svg">assembly drawing</a> · <a href="bench-harness-p0.1/as-built-record.csv">as-built record</a>.</p></div>{end}'''
    replace_block(STATION / "index.html", start, end, block, "</main>")
    station_readme = STATION / "README.md"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", station_readme.read_text(encoding="utf-8")).rstrip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    station_readme.write_text(text + f"\n\n{start}\n## Bench harness\n\nThe current-limited source lead is defined in `bench-harness-p0.1/` with exact manufacturer-assembled Mueller source leads, explicit contacts, sacrificial tin-dipped-tip removal, exact candidate preparation/inspection tools, a 25 +/-6 mm/min destructive-pull method, inspection traveler and as-built record. Receipt, calibration, compatibility, fabrication, inspection, qualified review and all connection/power authority remain open.\n{end}\n", encoding="utf-8")
    root_status_path = WB / "package-status.json"
    root_status = json.loads(root_status_path.read_text(encoding="utf-8"))
    root_status.update({
        "axis_commissioning_bench_harness_present":True,"axis_commissioning_bench_harness_assembly_count":1,
        "axis_commissioning_bench_harness_contact_map_complete":True,"axis_commissioning_bench_harness_exact_inspection_tools_selected":True,"axis_commissioning_bench_harness_exact_preparation_tools_selected":True,"axis_commissioning_bench_harness_manufacturer_assembled_source_end_selected":True,
        "axis_commissioning_bench_harness_source_end_process_selected":True,"axis_commissioning_bench_harness_received_lead_compatibility_validated":False,
        "axis_commissioning_bench_harness_physically_validated":False,
    })
    root_status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    root_block = f'''{start}<section id="bench-harness"><h2>Commissioning bench harness</h2><div class="grid"><article class="card pass"><h3>Exact manufacturer source leads</h3><p>Red and black Mueller 39-inch shrouded-banana leads remove the custom plug-termination ambiguity.</p></article><article class="card pass"><h3>Exact process tools</h3><p>Candidate crimp, crimp-height, pull-test, cut and silicone-strip tools now have exact order codes and primary-source boundaries.</p></article><article class="card pass"><h3>Explicit J1 polarity</h3><p>Black/GND is cavity 1; red/VDD is cavity 2. Tip removal, strip, crimp and 25 +/-6 mm/min pull criteria are controlled.</p></article><article class="card hold"><h3>Physical evidence open</h3><p>Receipt, calibration, compatibility, coupon, inspection and connection authority remain unresolved.</p></article></div><p><a href="electrical/axis-commissioning-station-p0.1/bench-harness-p0.1/index.html">Open the interactive bench-harness guide</a>.</p></section>{end}'''
    replace_block(WB / "index.html", start, end, root_block, "</main>")
    root_readme = WB / "README.md"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", root_readme.read_text(encoding="utf-8")).rstrip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    root_readme.write_text(text + f"\n\n{start}\n## Commissioning bench harness\n\nThe one-axis station now includes an assembly-controlled two-wire source harness with exact manufacturer-assembled Mueller source leads, Mini-Fit polarity, sacrificial tin-dipped-tip removal, exact candidate crimp/measurement/pull/cut/strip tools, a controlled 25 +/-6 mm/min destructive-pull method, inspection traveler and as-built record. Receipt, calibration, lead/tool compatibility, physical fabrication, qualified review and every connection/powered-test/motion/energization authority remain open.\n{end}\n", encoding="utf-8")


def manifests_and_release() -> None:
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path":p.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in files])
    station_files = sorted(p for p in STATION.rglob("*") if p.is_file() and p != STATION / "file-manifest.csv")
    write_csv(STATION / "file-manifest.csv", [{"path":p.relative_to(STATION).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WARNING} for p in station_files])
    if REL_STATION.exists():
        shutil.rmtree(REL_STATION)
    shutil.copytree(STATION, REL_STATION)
    root_manifest = WB / "file-manifest.csv"
    root_files = sorted(p for p in WB.rglob("*") if p.is_file() and p != root_manifest)
    write_csv(root_manifest, [{"path":p.relative_to(WB).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p),"warning":WHOLE_WARNING} for p in root_files])
    release_root = ROOT / "release" / "hr30" / "whole-body-p0.1"
    for name in ("README.md", "index.html", "package-status.json", "file-manifest.csv"):
        shutil.copy2(WB / name, release_root / name)


def main() -> int:
    build()
    integrate()
    manifests_and_release()
    print(f"generated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
