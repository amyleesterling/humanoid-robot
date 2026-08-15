#!/usr/bin/env python3
"""Generate R242 P1.21 conductor/fill evidence and configuration P0.6."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/routing/hr-v0-p121-conductor-fill-p0.1"
OUT = ROOT / "release/hr-v0/p121-conductor-fill-p0.1"
CFG_SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.5"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.6"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.6"
IDENT = "HR-V0-P121-CONDUCTOR-FILL-P0.1"
CFG_IDENT = "HR-V0-CONFIG-REC-P0.6"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, str]) -> dict[str, str]:
    return {**row, "warning": WARNING}


def manifest(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    write(directory / "file-manifest.csv", [
        {"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files
    ])


def data() -> dict[str, list[dict[str, str]]]:
    od_3057 = 2.3
    area_3057 = math.pi * (od_3057 / 2) ** 2
    area_3051 = math.pi * (1.6 / 2) ** 2
    wd5_area = 7 * area_3057
    wd2_p121 = 5 * area_3057
    wd2_compute = 6 * area_3051
    wd2_field = 5 * area_3051
    wd2_known_max = wd2_p121 + max(wd2_compute, wd2_field)

    sources = [
        warned({"source_id":"R242-SRC-001","manufacturer_or_owner":"Belden","artifact":"3057 live product record","revision_or_date":"revision 0.120 dated 2026-06-30; accessed 2026-08-11","official_or_controlled_uri":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3057","controlled_fact":"3057 BL005 is active blue 100 ft reel; 16 AWG 26x30 tinned copper; PVC; 2.3 mm nominal OD; 300 V; -40 to 105 C; stationary minimum bend radius 23 mm","does_not_establish":"installed ampacity, dynamic flex, DCR, cut length, color-code acceptance, protection, fill, thermal result or application release"}),
        warned({"source_id":"R242-SRC-002","manufacturer_or_owner":"Phoenix Contact","artifact":"CD 25X25 item 3240187","revision_or_date":"current official product record accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-25x25-3240187","controlled_fact":"25 x 25 x 2000 mm; 327 mm2 usable cross-section; manufacturer publishes ten 3.4 mm cables at 60 percent filling volume as a catalog example","does_not_establish":"project fill rule, WD5/WD2 junction, installed cover fit, thermal result or application release"}),
        warned({"source_id":"R242-SRC-003","manufacturer_or_owner":"Phoenix Contact","artifact":"PTFIX 6/18X2,5-NS35 RD item 3273114","revision_or_date":"official PDF generated 2026-05-21; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/distributor-terminal-block-ptfix-618x25-ns35-rd-3273114?type=pdf","controlled_fact":"load contact flexible 0.14 to 4 mm2; ferruled 0.14 to 2.5 mm2; 8 to 10 mm strip; 16 AWG geometry fits","does_not_establish":"color convention, end preparation, tool, pull result, loading, protection or installed acceptance"}),
        warned({"source_id":"R242-SRC-004","manufacturer_or_owner":"Pilz","artifact":"PNOZ s4 operating manual","revision_or_date":"21396-EN-23; 2026-02 document; accessed 2026-08-11","official_or_controlled_uri":"https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf","controlled_fact":"750104 screw terminal accepts one flexible 0.25 to 2.5 mm2 / AWG 24 to 12; 7 mm strip; 0.5 N m; 24 V unit has 2.5 W DC supply consumption and 0.5 A / 5 ms A1 inrush","does_not_establish":"Project Button conductor release, supply tolerance at the device, restart behavior, achieved PL/SIL or validation"}),
        warned({"source_id":"R242-SRC-005","manufacturer_or_owner":"Phoenix Contact","artifact":"PLC-RSC-24DC/21-21 item 2967060","revision_or_date":"data maintenance 2026-04-01; accessed 2026-08-11","official_or_controlled_uri":"https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060","controlled_fact":"flexible 0.14 to 2.5 mm2; single ferrule 0.2 to 2.5 mm2; 8 mm strip; 0.6 to 0.8 N m; 24 V coil typical current 18 mA","does_not_establish":"maximum coil current, conductor release, safety credit, contact application, installed voltage or thermal result"}),
        warned({"source_id":"R242-SRC-006","manufacturer_or_owner":"Project Button","artifact":"R240 protected-routing package","revision_or_date":"HR-V0-P121-ROUTING-P0.1; 2026-08-11","official_or_controlled_uri":"release/hr-v0/p121-protected-routing-p0.1/route-segment-register.csv","controlled_fact":"seven coordinate-bound P1.21 planning routes and centerline lengths","does_not_establish":"cut lengths, terminal entry, bend radius, installation or accepted route"}),
        warned({"source_id":"R242-SRC-007","manufacturer_or_owner":"Project Button","artifact":"R241 segregation-hardware package","revision_or_date":"HR-V0-P121-SEGREGATION-HW-P0.1; 2026-08-11","official_or_controlled_uri":"release/hr-v0/p121-segregation-hardware-p0.1/package-status.json","controlled_fact":"WD5 item 3240187 candidate, 369.8 mm envelope, WD2 junction hold and seven logical conductors","does_not_establish":"conductor release, fill completion, thermal result, junction or physical acceptance"}),
        warned({"source_id":"R242-SRC-008","manufacturer_or_owner":"Project Button","artifact":"R205/R206/R207 observation harness sources","revision_or_date":"current controlled repository artifacts; 2026-08-10","official_or_controlled_uri":"release/hr-v0/pi-observation-integration-p0.1/harness-route.csv","controlled_fact":"six 1.6 mm compute candidates occupy WD2 y119.25 to 306; five 1.6 mm field candidates occupy WD2 y342 to 414","does_not_establish":"installed occupancy, cut lengths, packing, separation, labels, ties, cover fit or total WD2 fill"}),
    ]

    exact = [warned({
        "candidate_id":"R242-COND-001","scope":"seven stationary P1.21 WD5/WD2 conductors","manufacturer":"Belden","exact_order_code":"3057 BL005","description":"blue 16 AWG hook-up wire; 100 ft / 30.48 m reel","construction":"1 conductor; 26x30 tinned copper; PVC; nominal OD 2.3 mm","ratings":"300 V AWM 1007/1569; -40 to 105 C; stationary bend radius 23 mm","candidate_state":"EXACT ORDERABLE CANDIDATE ON HOLD","selection_boundary":"blue is a project candidate, not a code conclusion; XD24 red/XD0 blue identification conflict and qualified Boston/NFPA disposition remain open","procurement_released":"NO"
    })]

    route_specs = [
        ("C-01","RT-P035","XD24:02","SR1:A1","SAFETY_24V","SF01-SUPPLY",1370.25,"WD2 + WD5",True,"Pilz 2.5 W steady / 0.5 A 5 ms inrush source screen"),
        ("C-02","RT-P039","XD24:06","KWD1:A1","SAFETY_24V","DF01-GATE-HOT",1300.25,"WD2 + WD5",True,"Phoenix 18 mA typical only; maximum unresolved"),
        ("C-03","RT-P040","XD24:07","KWD1:11","SAFETY_24V","DF01-GATE-HOT",1300.25,"WD2 + WD5",True,"series SRA1 A1 path; see C-03+C-06+C-07 screen"),
        ("C-04","RT-P042","XD24:09","KWD2:A1","SAFETY_24V","DF01-GATE-HOT",1274.25,"WD2 + WD5",True,"Phoenix 18 mA typical only; maximum unresolved"),
        ("C-05","RT-P043","XD24:10","KWD2:21","SAFETY_24V","DF01-GATE-HOT",1274.25,"WD2 + WD5",True,"feedback burden maximum unresolved"),
        ("C-06","RT-P015","KWD1:14","KWD2:11","WD_SRA1_SUPPLY_INTERMEDIATE","DF01-GATE-HOT",86.0,"WD5",False,"series SRA1 A1 path; see C-03+C-06+C-07 screen"),
        ("C-07","RT-P005","KWD2:14","SRA1:A1","SRA1_A1_WD_GATED","DF01-GATE-HOT",118.0,"WD5",False,"series SRA1 A1 path; see C-03+C-06+C-07 screen"),
    ]
    conductors = [warned({
        "allocation_id":cid,"route_id":route,"from":frm,"to":to,"net":net,"route_class":klass,
        "planning_centerline_mm":f"{length:.2f}","candidate_duct":duct,"traverses_WD2":"YES" if wd2 else "NO",
        "exact_order_code":"Belden 3057 BL005 - HELD","gauge":"16 AWG / approximately 1.31 mm2","nominal_od_mm":"2.3",
        "color":"blue candidate; qualified convention review open","minimum_stationary_bend_radius_mm":"23","cut_length_mm":"SELECTION REQUIRED",
        "termination":"SELECTION REQUIRED","current_basis":current,"release_state":"NOT RELEASED"
    }) for cid,route,frm,to,net,klass,length,duct,wd2,current in route_specs]

    terminals = [
        warned({"interface":"XD24 load contacts","manufacturer_item":"Phoenix Contact 3273114","endpoints":"XD24:02,06,07,09,10","published_flexible_range":"0.14 to 4 mm2","published_ferruled_range":"0.14 to 2.5 mm2","strip_mm":"8 to 10","torque_Nm":"not applicable to push-in load contact","3057_1p31mm2_fit":"GAUGE FIT","unresolved":"ferrule/direct preparation, insertion process, pull inspection, color convention and received verification"}),
        warned({"interface":"SR1/SRA1 A1 screw terminals","manufacturer_item":"Pilz 750104","endpoints":"SR1:A1; SRA1:A1","published_flexible_range":"0.25 to 2.5 mm2 / AWG 24 to 12","published_ferruled_range":"manual family range; exact ferrule/process not selected","strip_mm":"7","torque_Nm":"0.5","3057_1p31mm2_fit":"GAUGE FIT","unresolved":"ferrule/direct preparation, exact ferrule, crimp tool/die, torque witness and received verification"}),
        warned({"interface":"KWD1/KWD2 screw terminals","manufacturer_item":"Phoenix Contact 2967060","endpoints":"KWD1:A1,11,14; KWD2:A1,11,14,21","published_flexible_range":"0.14 to 2.5 mm2","published_ferruled_range":"0.2 to 2.5 mm2","strip_mm":"8","torque_Nm":"0.6 to 0.8","3057_1p31mm2_fit":"GAUGE FIT","unresolved":"ferrule/direct preparation, exact ferrule, crimp tool/die, torque witness and received verification"}),
    ]

    total_route_mm = sum(row[6] for row in route_specs)
    lengths = [
        warned({"screen_id":"LEN-001","scope":"seven route centerlines","quantity":"7","value_mm":f"{total_route_mm:.2f}","equivalent":"6.72325 m / 22.06 ft","comparison":"30.48 m catalog reel is 4.53 times this geometry-only centerline sum","result":"CATALOG PUT-UP SCREEN PASS ONLY","not_included":"terminal entry, 23 mm bend arcs, service loops, stripping, labels, routing tolerance, waste, defects or other panel conductors"}),
        warned({"screen_id":"LEN-002","scope":"released cut schedule","quantity":"7","value_mm":"SELECTION REQUIRED","equivalent":"SELECTION REQUIRED","comparison":"received panel and terminal geometry required","result":"OPEN - DO NOT CUT","not_included":"all physical allowances and approval"}),
    ]

    occupancy = [
        warned({"screen_id":"FILL-WD5","duct":"WD5 / Phoenix 3240187","published_usable_cross_section_mm2":"327","known_conductors":"7 x Belden 3057 at nominal OD 2.3 mm","known_circular_envelope_mm2":f"{wd5_area:.2f}","known_percent_of_usable_area":f"{100*wd5_area/327:.2f}","cross_section_location":"all WD5 planning sections; route-specific entry/drop geometry unresolved","result":"GEOMETRY INPUT ONLY - TOTAL FILL NOT ACCEPTED","exclusions":"packing, labels, ties, bend space, terminal drops, cover clearance, junction geometry, ambient, duty, heating and qualified application rule"}),
        warned({"screen_id":"FILL-WD2-A","duct":"WD2 / Phoenix 3240189","published_usable_cross_section_mm2":"1235","known_conductors":"5 x Belden 3057 at nominal OD 2.3 mm","known_circular_envelope_mm2":f"{wd2_p121:.2f}","known_percent_of_usable_area":f"{100*wd2_p121/1235:.2f}","cross_section_location":"P1.21 transition path along WD2 y25 to y645","result":"KNOWN MINIMUM ONLY","exclusions":"all unenumerated WD2 occupants and physical factors"}),
        warned({"screen_id":"FILL-WD2-B","duct":"WD2 / Phoenix 3240189","published_usable_cross_section_mm2":"1235","known_conductors":"5 x 3057 plus 6 x 3051 compute candidates","known_circular_envelope_mm2":f"{wd2_known_max:.2f}","known_percent_of_usable_area":f"{100*wd2_known_max/1235:.2f}","cross_section_location":"documented maximum known cross-section over y119.25 to y306","result":"KNOWN MAXIMUM AMONG ENUMERATED ROUTES ONLY","exclusions":"all unenumerated WD2 occupants and physical factors"}),
        warned({"screen_id":"FILL-WD2-C","duct":"WD2 / Phoenix 3240189","published_usable_cross_section_mm2":"1235","known_conductors":"5 x 3057 plus 5 x 3051 field candidates","known_circular_envelope_mm2":f"{wd2_p121+wd2_field:.2f}","known_percent_of_usable_area":f"{100*(wd2_p121+wd2_field)/1235:.2f}","cross_section_location":"enumerated cross-section over y342 to y414","result":"KNOWN MINIMUM ONLY","exclusions":"all unenumerated WD2 occupants and physical factors"}),
    ]

    wd2 = [
        warned({"occupant_id":"WD2-OCC-001","source":"R240 P1.21 route screen","longitudinal_extent":"y25 to y645 planning path","count":"5","nominal_od_mm":"2.3","circular_envelope_mm2":f"{wd2_p121:.2f}","overlap_disposition":"baseline known occupancy across the documented WD2 path","physical_state":"NOT INSTALLED / ROUTE NOT RELEASED"}),
        warned({"occupant_id":"WD2-OCC-002","source":"R205/R207 observation compute harness","longitudinal_extent":"y119.25 to y306 planning path","count":"6","nominal_od_mm":"1.6","circular_envelope_mm2":f"{wd2_compute:.2f}","overlap_disposition":"overlaps the five P1.21 candidates in this segment","physical_state":"NOT INSTALLED / CUT LENGTH NOT RELEASED"}),
        warned({"occupant_id":"WD2-OCC-003","source":"R205/R206 observation field harness","longitudinal_extent":"y342 to y414 planning path","count":"5","nominal_od_mm":"1.6","circular_envelope_mm2":f"{wd2_field:.2f}","overlap_disposition":"overlaps the five P1.21 candidates; does not longitudinally overlap compute bundle","physical_state":"NOT INSTALLED / CUT LENGTH NOT RELEASED"}),
        warned({"occupant_id":"WD2-OCC-OPEN","source":"complete installed panel","longitudinal_extent":"all WD2 sections","count":"SELECTION REQUIRED","nominal_od_mm":"SELECTION REQUIRED","circular_envelope_mm2":"SELECTION REQUIRED","overlap_disposition":"ordinary diagnostics and any other routes must be enumerated before fill/thermal acceptance","physical_state":"OPEN BLOCKING INPUT"}),
    ]

    voltage = [
        warned({"screen_id":"VD-001","path":"XD24:02 to SR1:A1 / C-01","planning_length_m":"1.37025","current_input":"0.1042 A derived from 2.5 W / 24 V steady; 0.5 A for 5 ms published inrush","resistance_input":"received-lot ohm/m at recorded temperature SELECTION REQUIRED","equation":"Vdrop = I x R_lot_per_m x actual_cut_length_m","numeric_result":"NOT CALCULATED","reason":"Belden live record has no controlled DCR and actual cut length is unresolved"}),
        warned({"screen_id":"VD-002","path":"XD24:06 to KWD1:A1 / C-02","planning_length_m":"1.30025","current_input":"18 mA typical only; maximum SELECTION REQUIRED","resistance_input":"received-lot ohm/m SELECTION REQUIRED","equation":"Vdrop = I_max x R_lot_per_m x actual_cut_length_m","numeric_result":"NOT CALCULATED","reason":"maximum current, DCR and cut length unresolved"}),
        warned({"screen_id":"VD-003","path":"XD24:07 through KWD1/KWD2 to SRA1:A1 / C-03+C-06+C-07","planning_length_m":"1.50425","current_input":"0.1042 A derived steady; 0.5 A for 5 ms published inrush","resistance_input":"received-lot ohm/m SELECTION REQUIRED","equation":"Vdrop = I x R_lot_per_m x sum(actual series cut lengths)","numeric_result":"NOT CALCULATED","reason":"DCR, cut lengths, contact drops and supply tolerance unresolved"}),
        warned({"screen_id":"VD-004","path":"XD24:09 to KWD2:A1 / C-04","planning_length_m":"1.27425","current_input":"18 mA typical only; maximum SELECTION REQUIRED","resistance_input":"received-lot ohm/m SELECTION REQUIRED","equation":"Vdrop = I_max x R_lot_per_m x actual_cut_length_m","numeric_result":"NOT CALCULATED","reason":"maximum current, DCR and cut length unresolved"}),
        warned({"screen_id":"VD-005","path":"XD24:10 to KWD2:21 feedback / C-05","planning_length_m":"1.27425","current_input":"complete feedback burden SELECTION REQUIRED","resistance_input":"received-lot ohm/m SELECTION REQUIRED","equation":"Vdrop = I_max x R_lot_per_m x actual_cut_length_m","numeric_result":"NOT CALCULATED","reason":"load envelope, DCR and cut length unresolved"}),
    ]

    thermal = [
        warned({"screen_id":"TH-001","scope":"Belden 3057 installed ampacity","input":"manufacturer live record does not publish project installed ampacity","calculation":"NOT CALCULATED","result":"OPEN","required_evidence":"applicable-code and enclosure method; ambient; bundle; duty; conductor temperature; terminal limits; F24 coordination"}),
        warned({"screen_id":"TH-002","scope":"WD5 conductor I-squared-R loss","input":"actual cut lengths, received-lot DCR and maximum currents incomplete","calculation":"sum(I_max^2 x R_lot_per_m x actual_length_m)","result":"OPEN","required_evidence":"VD inputs plus enclosure heat model and measured worst-case temperature"}),
        warned({"screen_id":"TH-003","scope":"WD2 combined occupancy and heating","input":"only three route families are enumerated; other occupants unknown","calculation":"NOT CALCULATED","result":"OPEN","required_evidence":"segment-by-segment complete occupancy, current/duty per conductor, packing, covers, ambient and physical validation"}),
        warned({"screen_id":"TH-004","scope":"branch protection and fault clearing","input":"F24, source fault current and conductor fault path unresolved","calculation":"NOT CALCULATED","result":"BLOCKING","required_evidence":"prospective fault current; protective-device selection/curve; conductor/terminal withstand; clearing time; jurisdiction and qualified coordination"}),
    ]

    color = [
        warned({"finding_id":"COLOR-001","object":"Belden 3057 BL005","observation":"blue is an exact active 100 ft candidate for the seven positive 24 VDC control conductors","disposition":"HELD CANDIDATE ONLY","closure":"qualified Boston/US code and project identification review; both-end wire-number and marker system acceptance"}),
        warned({"finding_id":"COLOR-002","object":"XD24 red item 3273114 and XD0 blue item 3273112","observation":"current component-color convention can conflict with a blue positive-24-V conductor candidate and must not be treated as self-explanatory","disposition":"CONFIGURATION CONFLICT OPEN","closure":"qualified disposition of conductor, terminal-block and label colors; revise exact items if required before procurement"}),
        warned({"finding_id":"COLOR-003","object":"protective earth identification","observation":"3057 BL005 is not allocated to PE; green/yellow remains excluded from ordinary control use","disposition":"BOUNDARY RECORDED; PE CONDUCTOR STILL SELECTION REQUIRED","closure":"separate PE/bonding conductor selection and qualified grounding review"}),
    ]

    hold_text = [
        "Qualified Boston/US code and project color-identification disposition including XD24 red and XD0 blue blocks",
        "Exact termination method, ferrules if used, manufacturer-compatible crimp tool/die, strip lengths, torque and pull criteria",
        "Received-lot Belden identity and four-wire DCR measurement at recorded temperature with calibrated equipment",
        "Received-panel terminal-entry geometry, 23 mm stationary bend-radius proof, service allowance and released seven-wire cut schedule",
        "F24 selection and coordination using measured/site fault current, clearing curve, conductor/terminal limits and jurisdiction",
        "Complete segment-by-segment WD2 occupant register including ordinary diagnostics, labels, ties, partitions and covers",
        "Ambient, bundling, duty-cycle, enclosure heat and conductor-temperature calculation plus measured validation",
        "WD5/WD2 junction, bar removal, edge treatment, cover access, clips and bend geometry",
        "Continuity, polarity, pull, isolation, route, cover and photographic as-built evidence",
        "Formal P1.21 acceptance and configuration-controlled point-to-point schedule update",
        "Qualified electrical and functional-safety review; no safety credit from color, duct or ordinary relay routing",
        "Signed work authorization after all applicable procurement, assembly, connection and E2 gates are independently satisfied",
    ]
    holds = [warned({"hold_id":f"R242-H{i:02d}","hold":value,"state":"OPEN","evidence":"SELECTION REQUIRED / NOT EXECUTED"}) for i,value in enumerate(hold_text,1)]
    inspections = [warned({"inspection_id":f"R242-I{i:02d}","inspection":value,"procedure":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence_uri":"","operator":"","reviewer":""}) for i,value in enumerate((
        "received 3057 BL005 identity, markings, OD and put-up",
        "four-wire DCR and temperature record",
        "each seven-wire cut length and both-end wire number",
        "strip/ferrule/crimp/torque/pull result",
        "WD5/WD2 segment occupancy and cover fit",
        "23 mm bend radius and terminal entry",
        "continuity and polarity",
        "conductor-to-conductor and conductor-to-PE isolation",
        "cold and worst-case conductor/duct temperature",
        "qualified as-built review and signed release gate",
    ),1)]

    return {
        "source-register.csv": sources,
        "exact-conductor-candidate.csv": exact,
        "p121-conductor-schedule.csv": conductors,
        "terminal-compatibility.csv": terminals,
        "route-length-screen.csv": lengths,
        "duct-occupancy-screen.csv": occupancy,
        "wd2-known-occupancy.csv": wd2,
        "voltage-drop-screen.csv": voltage,
        "thermal-screen.csv": thermal,
        "color-identification-hold.csv": color,
        "open-holds.csv": holds,
        "inspection-register.csv": inspections,
    }


def overlay() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 720" role="img" aria-labelledby="title desc"><title id="title">R242 candidate conductor and known duct occupancy</title><desc id="desc">Seven blue candidate conductors in WD5 and segment-specific known occupancy in WD2, with all results held.</desc><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:16px}}.small{{font-size:14px}}.label{{font-weight:700}}.panel{{fill:#fff;stroke:#082b4c;stroke-width:3}}.duct{{fill:#d8f2ff;stroke:#1268a8;stroke-width:3}}.wire{{stroke:#1578bd;stroke-width:4;fill:none}}.gold{{fill:#fff0b3;stroke:#9b6d00;stroke-width:3}}.hold{{fill:#fff7d8;stroke:#9b6d00;stroke-width:3;stroke-dasharray:8 5}}</style><rect width="1100" height="720" fill="#f7fbfe"/><text x="35" y="42" class="label">{IDENT} · geometry screen, not a fill approval</text><rect x="70" y="80" width="700" height="590" rx="8" class="panel"/><rect x="130" y="120" width="570" height="55" class="gold"/><text x="150" y="105" class="label">WD5 · 327 mm² usable</text><text x="150" y="210">7 × Ø2.3 mm = 29.09 mm² = 8.90%</text><path d="M160 137 H670 M160 143 H670 M160 149 H670 M160 155 H670 M160 161 H670 M160 167 H670 M160 173 H670" class="wire"/><rect x="630" y="120" width="70" height="520" class="duct"/><text x="720" y="145" class="label">WD2 · 1235 mm² usable</text><text x="720" y="175">Five P1.21 wires traverse the duct.</text><text x="720" y="205">Known worst segment adds six</text><text x="720" y="230">Ø1.6 mm compute wires:</text><text x="720" y="260" class="label">32.84 mm² · 2.66%</text><rect x="815" y="305" width="245" height="150" rx="10" class="hold"/><text x="835" y="338" class="label">Still open</text><text x="835" y="370">Other WD2 occupants</text><text x="835" y="400">Packing · bends · labels</text><text x="835" y="430">Heat · cover · junction</text><text x="90" y="700" class="small">{WARNING}</text></svg>'''


def guide(records: dict[str, list[dict[str, str]]]) -> str:
    conductor_rows = "".join(f"<tr><td>{html.escape(r['allocation_id'])}</td><td>{html.escape(r['from'])} → {html.escape(r['to'])}</td><td>{html.escape(r['planning_centerline_mm'])}</td><td>{html.escape(r['candidate_duct'])}</td><td>{html.escape(r['cut_length_mm'])}</td></tr>" for r in records["p121-conductor-schedule.csv"])
    fill_rows = "".join(f"<tr><td>{html.escape(r['screen_id'])}</td><td>{html.escape(r['known_conductors'])}</td><td>{html.escape(r['known_circular_envelope_mm2'])}</td><td>{html.escape(r['known_percent_of_usable_area'])}%</td><td>{html.escape(r['result'])}</td></tr>" for r in records["duct-occupancy-screen.csv"])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R242 conductor and fill evidence</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1268a8;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05;max-width:20ch}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.5rem 0}}.card{{background:#fff;border:2px solid var(--blue);border-radius:.8rem;padding:1rem}}.note{{border-left:7px solid var(--gold);padding:1rem;background:#fff}}.viewer{{background:#fff;border:3px solid var(--navy);border-radius:.8rem;overflow:auto}}.viewer img{{display:block;width:100%;min-width:850px}}.controls{{display:flex;gap:.75rem;flex-wrap:wrap;margin:.8rem 0}}button{{font:inherit;font-weight:700;padding:.7rem 1rem;border:2px solid var(--navy);border-radius:.6rem;background:white;color:var(--navy)}}.table{{overflow:auto;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:980px;background:#fff}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #9bb}}th{{background:var(--navy);color:#fff}}code{{font-size:14px}}@media(max-width:700px){{main{{padding:1.25rem 1rem}}}}</style></head><body><header><strong>{IDENT} · R242</strong><h1>Exact wire candidate. Honest fill boundary.</h1><div class="warning">{WARNING}</div></header><main><div class="grid"><article class="card"><b>Belden 3057 BL005</b><br>Exact blue 16 AWG, 100 ft candidate on hold</article><article class="card"><b>8.90%</b><br>WD5 nominal-area geometry screen</article><article class="card"><b>2.66%</b><br>Worst currently enumerated WD2 cross-section</article><article class="card"><b>12 open holds</b><br>No cut length, protection, thermal result or work authority</article></div><p class="note">The seven P1.21 wires now have an exact orderable construction candidate. Blue is not released as the project color convention: the current red XD24 and blue XD0 distribution-block colors create an identification conflict that a qualified US/Boston electrical review must disposition before procurement.</p><div class="controls"><button id="zi">Zoom in</button><button id="zo">Zoom out</button><button id="zr">Reset</button></div><div class="viewer"><img id="drawing" src="conductor-fill-overlay.svg" alt="Candidate conductor and known duct occupancy diagram"></div><h2>Fill arithmetic</h2><div class="table"><table><thead><tr><th>Screen</th><th>Known conductors</th><th>Area mm²</th><th>Published-area ratio</th><th>Disposition</th></tr></thead><tbody>{fill_rows}</tbody></table></div><p>These ratios use nominal circular outside-diameter envelopes. They are not fill or thermal approval because installed packing, labels, ties, bends, covers, junction geometry, ambient, duty and additional WD2 occupants are unresolved.</p><h2>Seven candidate conductors</h2><div class="table"><table><thead><tr><th>ID</th><th>Endpoints</th><th>Centerline mm</th><th>Planning duct</th><th>Cut length</th></tr></thead><tbody>{conductor_rows}</tbody></table></div><h2>Voltage drop remains open</h2><p>Belden's controlled live record does not publish DCR, and received cut lengths do not exist. The package therefore records the exact equations and a four-wire received-lot measurement requirement instead of inventing a resistance value.</p><h2>What this does not close</h2><p>F24 and fault-current coordination, final colors, terminations, ferrules/tools, cut lengths, full WD2 occupancy, conductor heating, bend/entry geometry, installed inspection, P1.21 acceptance and qualified electrical/functional-safety review all remain open.</p></main><script>const im=document.querySelector('#drawing');let z=1;const set=()=>im.style.width=(z*100)+'%';document.querySelector('#zi').onclick=()=>{{z=Math.min(2.5,z+.25);set()}};document.querySelector('#zo').onclick=()=>{{z=Math.max(1,z-.25);set()}};document.querySelector('#zr').onclick=()=>{{z=1;set()}};</script></body></html>'''


def config_data() -> dict[str, list[dict[str, str]]]:
    names = ("current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv")
    cfg = {name: read(CFG_SOURCE / name) for name in names}
    cfg["current-configuration-map.csv"].append(warned({"record_id":"CFG-25","role":"P1.21 conductor and duct occupancy evidence","identifier":IDENT,"source_path":"release/hr-v0/p121-conductor-fill-p0.1/package-status.json","configuration_state":"CURRENT HELD CONDUCTOR/FILL CANDIDATE","release_boundary":"exact 3057 BL005 order-code candidate and geometry-only occupancy screens; color, DCR, cut, protection, thermal, physical and qualified closure open"}))
    cfg["supersession-map.csv"].append(warned({"record_id":"SUP-13","prior_identifier":"HR-V0-CONFIG-REC-P0.5","current_or_required_successor":CFG_IDENT,"disposition":"P0.5 remains immutable R241 snapshot; P0.6 adds R242/BOM-097 without promoting P1.21 or any work gate","use_authorized":"NO"}))
    cfg["bom-integration-map.csv"].append(warned({"item_id":"BOM-097","role":"P1.21 WD5/WD2 stationary control-conductor candidate","bound_identifier":"Belden 3057 BL005; blue 16 AWG; 100 ft reel; application allocation seven conductors","closure_class":"exact_candidate_hold","physical_evidence":"OPEN","procurement_released":"NO"}))
    for row in cfg["gate-impact.csv"]:
        row["evidence_added"] = IDENT
        if row["gate_id"] in {"EG-002","EG-003","EG-004","EG-010","EG-012","EG-015","EG-018","EG-020"}:
            row["remaining_evidence"] += "; R242 color/DCR/cut/protection/full-fill/thermal/physical/qualified closure"
    additions = (
        ("P1.21 conductor color and XD24/XD0 identification convention","SELECTION REQUIRED","qualified Boston/US code and project identification disposition"),
        ("P1.21 DCR, cut length, voltage-drop, ampacity, protection and thermal closure","NOT EXECUTED","received measurements, calculations, coordination and accepted limits"),
        ("complete WD2 occupancy and installed conductor-route acceptance","NOT EXECUTED","segment register, as-built inspection and qualified review"),
    )
    for n,(hold,state,evidence) in enumerate(additions,30):
        cfg["open-holds.csv"].append(warned({"hold_id":f"HOLD-{n:02d}","hold":hold,"state":state,"closure_evidence":evidence}))
    criteria = (
        "Belden 3057 BL005 current exact identity and held status are independently confirmed",
        "Seven P1.21 endpoints and route lengths match P1.21/R240 sources",
        "WD5 and segment-specific WD2 arithmetic is independently reproduced",
        "Blue wire and XD24/XD0 component-color convention is qualified and frozen",
        "DCR/cut/voltage/protection/thermal and full occupancy evidence is accepted",
        "P1.15 remains current and P1.21/R242 remain unaccepted until formal disposition",
    )
    for n,criterion in enumerate(criteria,30):
        cfg["acceptance-matrix.csv"].append(warned({"acceptance_id":f"ACC-{n:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    return cfg


def main() -> None:
    records = data()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in records.items():
            write(directory / name, rows)
        text(directory / "README.md", f"# {IDENT}\n\n> **{WARNING}**\n\nR242 binds an exact Belden 3057 BL005 held candidate to seven P1.21 stationary planning routes and records geometry-only duct occupancy. Color convention, DCR, cut lengths, terminations, protection, total fill, thermal, physical and qualified evidence remain open.\n")
        text(directory / "conductor-fill-overlay.svg", overlay())
        status = {
            "identifier": IDENT, "round": "R242", "date": "2026-08-11",
            "exact_conductor_candidate": "Belden 3057 BL005", "candidate_color": "blue",
            "candidate_put_up_m": 30.48, "logical_conductors": 7,
            "planning_centerline_total_m": 6.72325,
            "wd5_known_circular_area_mm2": round(7 * math.pi * (2.3 / 2) ** 2, 2),
            "wd5_known_percent_of_published_usable_area": round(100 * 7 * math.pi * (2.3 / 2) ** 2 / 327, 2),
            "wd2_max_enumerated_cross_section_area_mm2": round(5 * math.pi * (2.3 / 2) ** 2 + 6 * math.pi * (1.6 / 2) ** 2, 2),
            "wd2_max_enumerated_percent_of_published_usable_area": round(100 * (5 * math.pi * (2.3 / 2) ** 2 + 6 * math.pi * (1.6 / 2) ** 2) / 1235, 2),
            "open_holds": 12, "blank_inspections": 10,
            "color_convention_accepted": False, "dcr_controlled": False, "cut_lengths_released": False,
            "total_duct_fill_complete": False, "thermal_calculation_complete": False, "protection_coordinated": False,
            "physical_evidence_exists": False, "qualified_review_complete": False,
            "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
            "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
            "energization_authorized": False, "safety_credit": False, "warning": WARNING,
        }
        text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    text(OUT / "index.html", guide(records))
    manifest(ENG)
    manifest(OUT)

    cfg = config_data()
    for directory in (CFG_ENG, CFG_OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, rows in cfg.items():
            write(directory / name, rows)
        text(directory / "README.md", f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR242 adds held BOM-097 and {IDENT}. P1.15 remains current; P1.21 is unaccepted; no work gate closes.\n")
        status = {
            "identifier": CFG_IDENT, "round": "R242", "date": "2026-08-11",
            "current_core_electrical_identifier": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "unaccepted_panel_topology_candidate": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
            "system_bom_groups": 97, "current_records": 25, "supersession_records": 13,
            "bom_integration_records": 17, "gate_records": 11, "open_holds": 32, "acceptance_rows": 35,
            "all_acceptance_executed": False, "physical_article_exists": False, "physical_test_executed": False,
            "qualified_review_complete": False, "procurement_authorized": False, "fabrication_authorized": False,
            "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False,
            "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING,
        }
        text(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    cfg_sources = []
    for row in cfg["current-configuration-map.csv"]:
        path = ROOT / row["source_path"]
        cfg_sources.append(warned({"source_path":row["source_path"],"sha256":digest(path),"role":"current configuration evidence"}))
    for directory in (CFG_ENG, CFG_OUT):
        write(directory / "source-hash-register.csv", cfg_sources)
        manifest(directory)
    text(CFG_OUT / "index.html", f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{CFG_IDENT}</title><style>body{{margin:0;background:#f7fbfe;color:#082b4c;font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif}}main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(32px,5vw,58px)}}.warning{{padding:16px;background:#fff3c4;border:3px solid #9b6d00;font-weight:800}}.card{{padding:18px;margin:18px 0;background:#fff;border:2px solid #1268a8;border-radius:12px}}</style></head><body><main><div class="warning">{WARNING}</div><h1>{CFG_IDENT}</h1><div class="card"><b>97 covered BOM groups</b><p>BOM-097 is exact Belden 3057 BL005 on hold. Color convention, DCR, cuts, protection, fill, thermal and physical evidence remain open.</p></div><div class="card"><b>P1.15 remains current</b><p>P1.21 and R242 remain unaccepted. No procurement, fabrication, wiring, powered test, motion or energization is authorized.</p></div></main></body></html>''')
    manifest(CFG_OUT)
    print(f"{IDENT}: exact held conductor; WD5 8.90%; WD2 enumerated max 2.66%; 12 holds")
    print(f"{CFG_IDENT}: 97 BOM groups; P1.15 current; P1.21 unaccepted")


if __name__ == "__main__":
    main()
