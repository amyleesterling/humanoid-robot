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
<path d="M317 355 H960" stroke="#d32424" stroke-width="18" fill="none"/><path d="M317 420 H960" stroke="#111" stroke-width="18" fill="none"/><text x="510" y="337" font-family="system-ui" font-size="20" font-weight="700" fill="#a21414">BH-W01 RED, 20 AWG, 1000 +/- 5 mm first cut</text><text x="510" y="458" font-family="system-ui" font-size="20" font-weight="700" fill="#082f58">BH-W02 BLACK, 20 AWG, 1000 +/- 5 mm first cut</text>
<rect x="960" y="304" width="150" height="172" rx="18" fill="#f2b928" stroke="#082f58" stroke-width="5"/><text x="982" y="340" font-family="system-ui" font-size="22" font-weight="800" fill="#082f58">J1</text><text x="982" y="369" font-family="system-ui" font-size="18" fill="#082f58">39-01-2020</text><circle cx="1000" cy="405" r="20" fill="#111"/><text x="1030" y="412" font-family="system-ui" font-size="19" fill="#082f58">1 GND</text><circle cx="1000" cy="454" r="20" fill="#c62828"/><text x="1030" y="461" font-family="system-ui" font-size="19" fill="#082f58">2 VDD</text>
<rect x="1160" y="210" width="280" height="250" rx="24" fill="#d6f1ff" stroke="#082f58" stroke-width="5"/><text x="1190" y="260" font-family="system-ui" font-size="27" font-weight="800" fill="#082f58">ROBOTIS PHB</text><text x="1190" y="300" font-family="system-ui" font-size="19" fill="#082f58">Mini-Fit input only</text><text x="1190" y="344" font-family="system-ui" font-size="19" fill="#082f58">barrel EMPTY</text><text x="1190" y="378" font-family="system-ui" font-size="19" fill="#082f58">screw input EMPTY</text><text x="1190" y="418" font-family="system-ui" font-size="19" font-weight="800" fill="#082f58">one X3P OR X4P</text>
<path d="M1110 390 H1160" stroke="#082f58" stroke-width="8"/><rect x="445" y="540" width="610" height="150" rx="20" fill="#fff" stroke="#14689c" stroke-width="4"/><text x="478" y="580" font-family="system-ui" font-size="23" font-weight="800" fill="#082f58">Independent de-energized inspection</text><text x="478" y="617" font-family="system-ui" font-size="19" fill="#082f58">1. J1 pin 1 to BLACK return; J1 pin 2 to RED positive.</text><text x="478" y="650" font-family="system-ui" font-size="19" fill="#082f58">2. No cross-short; terminal lock and strain-free 12.7 mm minimum free lead.</text><text x="478" y="680" font-family="system-ui" font-size="19" fill="#082f58">3. As-built record and qualified signoff required before connection.</text></svg>'''


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write_csv(OUT / "harness-assembly-register.csv", [{
        "assembly_id":"BH-A01","description":"current-limited source to U2D2 Power Hub Mini-Fit input lead","quantity":1,
        "source_end":"two Pomona 4933 sheathed 4 mm plugs","load_end":"Molex 39-01-2020 with two 39-00-0038 female contacts",
        "conductor_count":2,"first_cut_length_mm":1000,"finished_length":"AS-MEASURED AFTER APPROVED BANANA TERMINATION",
        "configuration_limit":"11.0 V / 0.25 A first power; 2.0 A station absolute configuration ceiling",
        "allowed_role":"one mechanically restrained and whole-body-disconnected actuator only","state":"DESIGN COMPLETE / ASSEMBLY NOT EXECUTED","authority":AUTHORITY,
    }])
    write_csv(OUT / "conductor-preparation-register.csv", [
        {"wire_id":"BH-W01","function":"VDD positive","color":"RED","material":"Alpha Wire 3073; 20 AWG; 10/30 tinned copper; nominal OD 2.565 mm","first_cut_length_mm":"1000 +/- 5","j1_strip_length_mm":"3.00-3.30","j1_target_strip_mm":"3.15","j1_conductor_crimp_height_mm":"0.83-0.93","minimum_pull_force_n":"58.7","source_end_preparation":"Pomona D1094280 Rev 100; solder or crimp method requires qualified process selection","free_wire_at_j1_mm":"12.7 minimum before first tie or imposed bend","label":"BH-W01 VDD RED","state":"NOT ASSEMBLED"},
        {"wire_id":"BH-W02","function":"DC return / GND","color":"BLACK","material":"Alpha Wire 3073; 20 AWG; 10/30 tinned copper; nominal OD 2.565 mm","first_cut_length_mm":"1000 +/- 5","j1_strip_length_mm":"3.00-3.30","j1_target_strip_mm":"3.15","j1_conductor_crimp_height_mm":"0.83-0.93","minimum_pull_force_n":"58.7","source_end_preparation":"Pomona D1094280 Rev 100; solder or crimp method requires qualified process selection","free_wire_at_j1_mm":"12.7 minimum before first tie or imposed bend","label":"BH-W02 GND BLACK","state":"NOT ASSEMBLED"},
    ])
    write_csv(OUT / "connector-contact-map.csv", [
        {"connector":"PS1-RED","manufacturer_part":"Pomona 4933-2","contact":"single","function":"VDD positive","wire_id":"BH-W01","mate":"approved E36313A positive output jack","polarity_check":"J1-2 continuity only; open to J1-1","state":"NOT EXECUTED"},
        {"connector":"PS1-BLACK","manufacturer_part":"Pomona 4933-0","contact":"single","function":"DC return / GND","wire_id":"BH-W02","mate":"same E36313A channel return jack","polarity_check":"J1-1 continuity only; open to J1-2","state":"NOT EXECUTED"},
        {"connector":"J1","manufacturer_part":"Molex 39-01-2020 / 39-00-0038","contact":"1","function":"GND","wire_id":"BH-W02","mate":"PHB power pin 1","polarity_check":"BLACK only","state":"NOT EXECUTED"},
        {"connector":"J1","manufacturer_part":"Molex 39-01-2020 / 39-00-0038","contact":"2","function":"VDD","wire_id":"BH-W01","mate":"PHB power pin 2","polarity_check":"RED only","state":"NOT EXECUTED"},
    ])
    write_csv(OUT / "tooling-register.csv", [
        {"tool_id":"BH-T01","manufacturer":"Molex","order_code":"63819-0901","description":"Type 4D hand crimp tool for Mini-Fit Jr male/female terminals, 18-24 AWG","document":"638190901 Rev D, 2025-03-31","application":"39-00-0038 on Alpha 3073 20 AWG","disposition":"CANDIDATE; RECEIPT/CALIBRATION/CRIMP VALIDATION REQUIRED"},
        {"tool_id":"BH-T02","manufacturer":"Molex","order_code":"11-03-0044","description":"HT60630B extraction tool","document":"ATS-011030044 Rev N, 2023-05-05","application":"remove a misinserted 39-00-0038; extracted terminal must not be reused","disposition":"CANDIDATE; RECEIPT INSPECTION REQUIRED"},
        {"tool_id":"BH-T03","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"calibrated crimp-height micrometer with blade/anvil suitable for open-barrel crimps","document":"calibration certificate required","application":"measure 0.83-0.93 mm conductor crimp height without damaging terminal","disposition":"SELECTION REQUIRED"},
        {"tool_id":"BH-T04","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"calibrated tensile tester with suitable terminal/wire grips","document":"calibration certificate required","application":"destructive process coupon must exceed 58.7 N with insulation support removed from influence","disposition":"SELECTION REQUIRED"},
        {"tool_id":"BH-T05","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"wire stripper for 20 AWG stranded copper","document":"tool setup/coupon inspection required","application":"3.00-3.30 mm strip; no nicked or cut strands","disposition":"SELECTION REQUIRED"},
        {"tool_id":"BH-T06","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"Pomona 4933 termination tooling/process","document":"must implement Pomona D1094280 Rev 100 without exposed conductor","application":"qualified crimp or solder process at both source ends","disposition":"SELECTION REQUIRED"},
    ])
    write_csv(OUT / "assembly-traveler.csv", [
        {"step":"A01","operation":"verify exact received part numbers, wire colors, lot/traceability and undamaged insulation","acceptance":"all match candidate BOM; record lot and photo","record":"BH-R01","state":"NOT EXECUTED","stop_rule":"STOP on mismatch"},
        {"step":"A02","operation":"cut BH-W01 red and BH-W02 black separately","acceptance":"1000 +/- 5 mm before termination; measure each","record":"BH-R02/BH-R03","state":"NOT EXECUTED","stop_rule":"STOP outside length"},
        {"step":"A03","operation":"prepare Mini-Fit ends","acceptance":"strip 3.00-3.30 mm; no cut/nicked strands; insulation OD within 3.1 mm tool maximum","record":"BH-R04/BH-R05","state":"NOT EXECUTED","stop_rule":"discard damaged wire end"},
        {"step":"A04","operation":"make and destructively test one process coupon before production contacts","acceptance":"20 AWG conductor crimp height 0.83-0.93 mm and pull force > 58.7 N; insulation crimp removed from pull influence","record":"BH-R06","state":"NOT EXECUTED","stop_rule":"STOP until process passes"},
        {"step":"A05","operation":"crimp production contacts with 63819-0901 20-24 AWG profile","acceptance":"full ratchet cycle; visible conductor brush/bellmouth; crimp height 0.83-0.93 mm; no deformation","record":"BH-R07/BH-R08","state":"NOT EXECUTED","stop_rule":"reject nonconforming contact"},
        {"step":"A06","operation":"insert black contact into J1 cavity 1 and red contact into J1 cavity 2","acceptance":"stop tab down per Molex application specification; audible/physical lock; gentle retention check","record":"BH-R09","state":"NOT EXECUTED","stop_rule":"do not force; extracted contact may not be reused"},
        {"step":"A07","operation":"terminate Pomona 4933-0 black and 4933-2 red ends using separately approved process","acceptance":"threaded bodies secure; no exposed conductor; polarity color matches conductor","record":"BH-R10","state":"NOT EXECUTED","stop_rule":"STOP without approved source-end process"},
        {"step":"A08","operation":"apply labels and dress paired lead","acceptance":"BH-W01/BH-W02 labels readable; 12.7 mm minimum relaxed free length behind J1; no tight tie or sharp bend","record":"BH-R11","state":"NOT EXECUTED","stop_rule":"rework strain/bend violation"},
        {"step":"A09","operation":"independent de-energized continuity/polarity/short inspection","acceptance":"red plug to J1-2 only; black plug to J1-1 only; open between circuits and to exposed housing","record":"BH-R12","state":"NOT EXECUTED","stop_rule":"quarantine on any ambiguity"},
        {"step":"A10","operation":"as-built review and bag/label assembly","acceptance":"all records complete; qualified reviewer signs; warning label attached","record":"BH-R13","state":"NOT EXECUTED","stop_rule":"no connection without separate authorization"},
    ])
    write_csv(OUT / "as-built-record.csv", [
        {"record_id":"BH-R01","field":"received part/lot/photo record","required_value":"all exact candidates or documented approved deviation","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R02","field":"BH-W01 red first-cut length","required_value":"1000 +/- 5 mm","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R03","field":"BH-W02 black first-cut length","required_value":"1000 +/- 5 mm","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R04","field":"BH-W01 strip/strand inspection","required_value":"3.00-3.30 mm; zero damaged strands","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R05","field":"BH-W02 strip/strand inspection","required_value":"3.00-3.30 mm; zero damaged strands","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R06","field":"destructive crimp process coupon","required_value":"0.83-0.93 mm and >58.7 N","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R07","field":"BH-W01 production crimp height/visual","required_value":"0.83-0.93 mm and acceptable visual","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R08","field":"BH-W02 production crimp height/visual","required_value":"0.83-0.93 mm and acceptable visual","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R09","field":"terminal insertion/retention and cavity identity","required_value":"black J1-1; red J1-2; both locked","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R10","field":"source-end termination","required_value":"approved Pomona process; no exposed conductor","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R11","field":"labels/free length/bend inspection","required_value":"labels correct; >=12.7 mm relaxed free lead at J1","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R12","field":"independent polarity/continuity/short test","required_value":"red-J1/2 only; black-J1/1 only; no cross-short","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
        {"record_id":"BH-R13","field":"final as-built disposition","required_value":"qualified signed acceptance plus separate connection procedure","observed_value":"NOT RECORDED","operator":"UNASSIGNED","reviewer":"UNASSIGNED","date_utc":"NOT EXECUTED","result":"OPEN"},
    ])
    write_csv(OUT / "candidate-bom.csv", [
        {"item":"BH-01","quantity":1,"manufacturer":"Molex","order_code":"39-01-2020","description":"2-circuit Mini-Fit Jr receptacle housing","disposition":"CANDIDATE"},
        {"item":"BH-02","quantity":2,"manufacturer":"Molex","order_code":"39-00-0038","description":"5556 female crimp contact for 20 AWG","disposition":"CANDIDATE"},
        {"item":"BH-03","quantity":"1.0 m first cut","manufacturer":"Alpha Wire","order_code":"3073 RED","description":"20 AWG red VDD lead","disposition":"CANDIDATE"},
        {"item":"BH-04","quantity":"1.0 m first cut","manufacturer":"Alpha Wire","order_code":"3073 BLACK","description":"20 AWG black return lead","disposition":"CANDIDATE"},
        {"item":"BH-05","quantity":1,"manufacturer":"Pomona","order_code":"4933-2","description":"red sheathed 4 mm banana plug","disposition":"CANDIDATE; TERMINATION PROCESS OPEN"},
        {"item":"BH-06","quantity":1,"manufacturer":"Pomona","order_code":"4933-0","description":"black sheathed 4 mm banana plug","disposition":"CANDIDATE; TERMINATION PROCESS OPEN"},
        {"item":"BH-07","quantity":1,"manufacturer":"Molex","order_code":"63819-0901","description":"Mini-Fit Jr hand crimp tool","disposition":"CANDIDATE; RECEIPT/CALIBRATION OPEN"},
        {"item":"BH-08","quantity":1,"manufacturer":"Molex","order_code":"11-03-0044","description":"Mini-Fit extraction tool","disposition":"CANDIDATE"},
        {"item":"BH-09","quantity":"as required","manufacturer":"SELECTION REQUIRED","order_code":"SELECTION REQUIRED","description":"durable wire and assembly warning labels","disposition":"SELECTION REQUIRED"},
    ])
    write_csv(OUT / "primary-source-register.csv", [
        {"source_id":"MOLEX-TOOL","manufacturer":"Molex","document":"638190901 Rev D","document_date":"2025-03-31","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63819/638190901-000.pdf","verified_scope":"63819-0901; 39-00-0038; 18-24 AWG; 3.00-3.30 mm strip; 20 AWG crimp and pull criteria"},
        {"source_id":"MOLEX-APPLICATION","manufacturer":"Molex","document":"55560002-AS Rev A1","document_date":"2025-01-09","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/555/5556/55560002-AS-000.pdf","verified_scope":"terminal handling/insertion; no live mate/unmate; 12.7 mm free wire for 2-circuit housing; extracted terminal not reused"},
        {"source_id":"MOLEX-PRODUCT","manufacturer":"Molex","document":"PS-5556-001 Rev H2","document_date":"2026-06-22","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/555/5556/PS-5556-001-001.pdf","verified_scope":"current Mini-Fit Jr product-system boundary; application-specific derating remains required"},
        {"source_id":"MOLEX-EXTRACT","manufacturer":"Molex","document":"ATS-011030044 Rev N","document_date":"2023-05-05","accessed":"2026-08-15","official_url":"https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/606/60630/ATS-011030044-001.pdf","verified_scope":"11-03-0044 applies to 39-00-0038"},
        {"source_id":"ALPHA-3073","manufacturer":"Alpha Wire","document":"live official product page; revision not stated","document_date":"accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://www.alphawire.com/products/wire/hook-up-wire/premium/3073","verified_scope":"20 AWG 10/30 tinned copper; nominal OD 0.101 +/- 0.004 in; 105 C; 600 V; 5x diameter bend radius"},
        {"source_id":"POMONA-4933","manufacturer":"Pomona Electronics","document":"D1094280 Rev 100","document_date":"2010","accessed":"2026-08-15","official_url":"https://www.pomonaelectronics.com/files/datasheets/sheathed-banana-plug-for-18-20-22-awg-wire.pdf","verified_scope":"4933 accepts 18/20/22 AWG; threaded two-piece solder-or-crimp design; -0 black and -2 red"},
        {"source_id":"ROBOTIS-PHB","manufacturer":"ROBOTIS","document":"live official Docs; revision not visible","document_date":"accessed 2026-08-15","accessed":"2026-08-15","official_url":"https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/","verified_scope":"3.5-24 V; 10 A maximum; one power input only; Mini-Fit pin 1 GND / pin 2 VDD"},
    ])
    write_csv(OUT / "open-holds.csv", [
        {"hold_id":"BH-H01","unresolved_evidence":"qualified approval of complete harness drawing, assembly traveler and inspection method","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H02","unresolved_evidence":"received exact wire/connectors/tooling, lot records and calibration certificates","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H03","unresolved_evidence":"qualified Pomona 4933 source-end solder-or-crimp process and retention evidence","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H04","unresolved_evidence":"executed destructive crimp coupon, production crimp-height and terminal-retention records","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H05","unresolved_evidence":"executed independent continuity, short and polarity inspection plus signed as-built disposition","state":"OPEN","authority":AUTHORITY},
        {"hold_id":"BH-H06","unresolved_evidence":"separate qualified station connection and first-power authorization","state":"OPEN","authority":AUTHORITY},
    ])
    (OUT / "bench-harness.svg").write_text(schematic_svg(), encoding="utf-8")
    (OUT / "harness-status.json").write_text(json.dumps({
        "identifier":"HR30-AXIS-BENCH-HARNESS-P0.1","warning":WARNING,"assembly_count":1,"conductor_count":2,
        "physical_connector_contact_count":4,"exact_mini_fit_tool_candidate_selected":True,"exact_cut_and_strip_definition_present":True,
        "assembly_traveler_step_count":10,"as_built_record_count":13,"source_end_termination_process_selected":False,
        "physical_assembly_executed":False,"inspection_executed":False,"qualified_review_complete":False,
        "connection_authority":False,"powered_test_authority":False,"motion_authority":False,"energization_authority":False,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f'''# HR-30 axis-commissioning bench harness P0.1

**{WARNING}**

This package defines the exact two-conductor station power lead from one current-limited Keysight output to the Mini-Fit input of the ROBOTIS U2D2 Power Hub. It fixes the Mini-Fit contact map, wire/color identity, first-cut length, strip length, crimp-height band, process-coupon pull force, free-lead rule, assembly traveler and as-built record. The Pomona source-end termination process, received tooling/calibration, physical fabrication, inspection, qualified review and every connection/power/motion authority remain open.
''', encoding="utf-8")
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 bench harness P0.1</title><style>:root{{--navy:#082f58;--blue:#14689c;--sky:#d6f1ff;--gold:#f2b928;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold)}}header>div,main{{max-width:1200px;margin:auto}}h1{{font-size:clamp(2.2rem,6vw,4.8rem);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(1.7rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #a86f00;background:#fff0b5;border-radius:16px;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:1rem;margin:1.5rem 0}}article,.panel{{padding:1rem;background:#fff;border:2px solid var(--blue);border-radius:16px}}.drawing{{overflow:auto;border:2px solid var(--blue);border-radius:16px;background:#fff}}.drawing img{{display:block;width:100%;min-width:820px;height:auto}}.tablewrap{{overflow:auto;border:2px solid var(--blue);border-radius:16px}}table{{border-collapse:collapse;width:100%;min-width:900px;background:#fff}}th,td{{padding:.8rem;border-bottom:1px solid #c7dfec;text-align:left;font-size:14px;vertical-align:top}}th{{background:var(--navy);color:#fff}}a{{color:#075d98;font-weight:800}}code{{font-size:14px}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Two wires. One keyed input. Zero guessed contacts.</h1><p>The station harness is now an assembly-controlled artifact, not a line on a schematic.</p></div></header><main><div class="hold"><h2>Still not permission to build or connect</h2><p>The design fixes the Mini-Fit end. The Pomona source-end process, received tool calibration, destructive coupon, as-built inspection, qualified review and signed connection procedure remain open.</p></div><h2>Point-to-point assembly drawing</h2><div class="drawing"><img src="bench-harness.svg" alt="Bench harness drawing from Keysight output to the keyed ROBOTIS Power Hub input"></div><div class="grid"><article><h3>J1 is explicit</h3><p>Cavity 1 is BLACK/GND. Cavity 2 is RED/VDD. The keyed housing mates only to the PHB Mini-Fit input.</p></article><article><h3>Crimp process is measurable</h3><p>Strip 3.00-3.30 mm. For 20 AWG, conductor crimp height is 0.83-0.93 mm and the destructive coupon must exceed 58.7 N.</p></article><article><h3>One power path</h3><p>The PHB barrel and screw-terminal inputs stay empty. Only one X3P or X4P actuator cable may be present.</p></article></div><h2>Assembly traveler</h2><div class="tablewrap"><table><thead><tr><th>Step</th><th>Operation</th><th>Acceptance</th><th>Stop rule</th></tr></thead><tbody>{''.join(f'<tr><td>{s}</td><td>{o}</td><td>{a}</td><td>{stop}</td></tr>' for s,o,a,stop in [("A01","Verify exact parts and lots","Record part, lot and photo","Stop on mismatch"),("A02","Cut red and black separately","1000 +/- 5 mm first cut","Stop outside length"),("A03","Prepare Mini-Fit ends","3.00-3.30 mm; zero damaged strands","Discard damaged end"),("A04","Destructive process coupon","0.83-0.93 mm and >58.7 N","Stop until passed"),("A05-A06","Crimp and insert","black J1-1; red J1-2; both locked","Reject nonconformance"),("A07","Terminate source ends","approved Pomona process; no exposed conductor","Stop if process unapproved"),("A08-A10","Label, inspect, sign","continuity/polarity/short and as-built complete","No connection without authority")])}</tbody></table></div><p><a href="assembly-traveler.csv">complete traveler</a> · <a href="as-built-record.csv">as-built record</a> · <a href="conductor-preparation-register.csv">cut and crimp register</a> · <a href="connector-contact-map.csv">contact map</a> · <a href="tooling-register.csv">tooling</a> · <a href="primary-source-register.csv">primary sources</a> · <a href="open-holds.csv">open holds</a></p></main></body></html>''', encoding="utf-8")


def integrate() -> None:
    shutil.copy2(Path(__file__), OUT / "bench-harness-source.py")
    station_status_path = STATION / "commissioning-status.json"
    status = json.loads(station_status_path.read_text(encoding="utf-8"))
    status.update({
        "bench_harness_design_present":True,"bench_harness_assembly_count":1,"bench_harness_conductor_count":2,
        "bench_harness_exact_mini_fit_tool_selected":True,"bench_harness_source_end_process_selected":False,
        "bench_harness_physically_assembled":False,"bench_harness_inspection_executed":False,"bench_harness_qualified_review_complete":False,
    })
    station_status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds_path = STATION / "open-holds.csv"
    with holds_path.open(encoding="utf-8", newline="") as handle:
        holds = list(csv.DictReader(handle))
    for row in holds:
        if row["hold_id"] == "CS-H04":
            row["unresolved_evidence"] = "received 63819-0901/11-03-0044 tooling and calibration, approved Pomona source-end process, executed Mini-Fit crimp-height/pull/polarity records and signed BH-A01 as-built disposition"
    write_csv(holds_path, holds)
    start, end = "<!-- BENCH-HARNESS-P01 START -->", "<!-- BENCH-HARNESS-P01 END -->"
    block = f'''{start}<h2>Assembly-controlled bench harness</h2><div class="panel"><p>The two-wire source lead now has an exact Mini-Fit contact map, cut/strip dimensions, candidate 63819-0901 crimp tool, measurable crimp and pull criteria, a ten-step traveler and a thirteen-field as-built record. The Pomona termination process and all physical evidence remain open.</p><p><a href="bench-harness-p0.1/index.html">Open the interactive bench-harness guide</a> · <a href="bench-harness-p0.1/bench-harness.svg">assembly drawing</a> · <a href="bench-harness-p0.1/as-built-record.csv">as-built record</a>.</p></div>{end}'''
    replace_block(STATION / "index.html", start, end, block, "</main>")
    station_readme = STATION / "README.md"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", station_readme.read_text(encoding="utf-8")).rstrip()
    station_readme.write_text(text + f"\n\n{start}\n## Bench harness\n\nThe current-limited source lead is defined in `bench-harness-p0.1/` with explicit contacts, wire preparation, tooling, inspection traveler and as-built record. The Pomona source-end process, fabrication, inspection, qualified review and all connection/power authority remain open.\n{end}\n", encoding="utf-8")
    root_status_path = WB / "package-status.json"
    root_status = json.loads(root_status_path.read_text(encoding="utf-8"))
    root_status.update({
        "axis_commissioning_bench_harness_present":True,"axis_commissioning_bench_harness_assembly_count":1,
        "axis_commissioning_bench_harness_contact_map_complete":True,"axis_commissioning_bench_harness_source_end_process_selected":False,
        "axis_commissioning_bench_harness_physically_validated":False,
    })
    root_status_path.write_text(json.dumps(root_status, indent=2) + "\n", encoding="utf-8")
    root_block = f'''{start}<section id="bench-harness"><h2>Commissioning bench harness</h2><div class="grid"><article class="card pass"><h3>Explicit J1 polarity</h3><p>Black/GND is cavity 1; red/VDD is cavity 2. Cut, strip and crimp dimensions are controlled.</p></article><article class="card pass"><h3>As-built traveler</h3><p>Ten assembly operations feed thirteen inspection and signoff records.</p></article><article class="card hold"><h3>Physical evidence open</h3><p>The source-end process, received tooling, coupon, inspection and connection authority remain unresolved.</p></article></div><p><a href="electrical/axis-commissioning-station-p0.1/bench-harness-p0.1/index.html">Open the interactive bench-harness guide</a>.</p></section>{end}'''
    replace_block(WB / "index.html", start, end, root_block, "</main>")
    root_readme = WB / "README.md"
    text = re.sub(re.escape(start) + r"[\s\S]*?" + re.escape(end), "", root_readme.read_text(encoding="utf-8")).rstrip()
    root_readme.write_text(text + f"\n\n{start}\n## Commissioning bench harness\n\nThe one-axis station now includes an assembly-controlled two-wire source harness with exact Mini-Fit polarity, wire preparation, candidate tooling, inspection traveler and as-built record. Physical fabrication, source-end process approval, qualified review and every connection/powered-test/motion/energization authority remain open.\n{end}\n", encoding="utf-8")


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
