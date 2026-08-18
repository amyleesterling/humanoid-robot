#!/usr/bin/env python3
"""Generate the HR-30 eight carrier-to-first-axis harness candidate package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
PHYSICAL = WHOLE / "harness" / "physical-p0.1"
CABLE_KIT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
CARRIERS = WHOLE / "electrical" / "carriers-p0.1"
OUT = WHOLE / "harness" / "carrier-first-axis-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-CARRIER-FIRST-AXIS-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - UNBUILT CARRIER-TO-FIRST-AXIS HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def controlled(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def sources() -> list[dict[str, object]]:
    local = [
        ("CFA-S01", "serial link topology", PHYSICAL / "serial-data-link-register.csv", "eight ordinal-one carrier-to-first-axis links and planning lengths"),
        ("CFA-S02", "carrier terminal register", CARRIERS / "carrier-terminal-register.csv", "J101-J105/J201-J203 exact field-connector nets and pads"),
        ("CFA-S03", "bus reference register", CABLE_KIT / "bus-reference-register.csv", "five isolated field-reference star paths and three single CTRL_GND paths"),
        ("CFA-S04", "actuator connector cavity register", CABLE_KIT / "connector-cavity-population.csv", "first-axis combined power/data housing population"),
        ("CFA-S05", "data cable candidates", CABLE_KIT / "data-cable-candidate.csv", "existing candidate conductor families and direct-crimp incompatibility boundary"),
        ("CFA-S06", "inter-axis adapter package", WHOLE / "harness/interaxis-data-adapter-p0.1/interaxis-adapter-register.csv", "downstream data-only topology continuity"),
    ]
    rows: list[dict[str, object]] = []
    for sid, document, path, scope in local:
        rows.append(controlled({
            "source_id": sid, "publisher": "Project Button", "document": document,
            "revision_or_date": "current generated P0.1 input",
            "official_url_or_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
            "verified_scope": scope,
        }))
    official = [
        ("CFA-S07", "JST", "GH connector family", "live official product page; accessed 2026-08-18", "https://www.jst-mfg.com/product/index.php?lang=2&series=105", "GHR-02V-S/GHR-03V-S; SSHL-002T-P0.2; AWG30-26 / 0.05-0.13 mm2; 0.76-1.0 mm insulation OD"),
        ("CFA-S08", "JST", "EH connector family", "official eEH catalog; accessed 2026-08-18", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "EHR-3/EHR-4 and SEH-001T-P0.6; AWG30-22 / 0.05-0.33 mm2"),
        ("CFA-S09", "ROBOTIS", "XH540-W270 connector information", "ROBOTIS Docs live page; accessed 2026-08-18", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/", "RS-485 actuator pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-"),
        ("CFA-S10", "ROBOTIS", "XC330-T288 connector information", "ROBOTIS Docs live page; accessed 2026-08-18", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/", "TTL actuator pin 1 GND, 2 VDD, 3 DATA"),
        ("CFA-S11", "igus", "CFBUS.PVC.001", "live official product page; accessed 2026-08-18", "https://www.igus.com/product/CFBUS_PVC?artnr=CFBUS-PVC-001", "2 x 24 AWG / 0.25 mm2 shielded pair; too large for direct GH contact crimp; test-coupon only"),
        ("CFA-S12", "igus", "CF240.01.03", "live official product page; accessed 2026-08-18", "https://www.igus.com/product/CF240", "3 x 26 AWG / 0.14 mm2; exceeds published GH 0.13 mm2 maximum; test-coupon only"),
    ]
    for sid, publisher, document, revision, url, scope in official:
        rows.append(controlled({
            "source_id": sid, "publisher": publisher, "document": document,
            "revision_or_date": revision, "official_url_or_path": url,
            "sha256": "NOT APPLICABLE - EXTERNAL PRIMARY SOURCE", "verified_scope": scope,
        }))
    return rows


def first_links() -> list[dict[str, str]]:
    rows = [row for row in read_csv(PHYSICAL / "serial-data-link-register.csv") if row["ordinal"] == "1"]
    if len(rows) != 8 or len({row["bus_id"] for row in rows}) != 8:
        raise RuntimeError("expected one ordinal-one link on each of eight buses")
    return rows


def assemblies(links: list[dict[str, str]]) -> list[dict[str, object]]:
    refs = {row["bus_id"]: row for row in read_csv(CABLE_KIT / "bus-reference-register.csv")}
    rows: list[dict[str, object]] = []
    for link in links:
        bus = link["bus_id"]
        ref = refs[bus]
        rs = bus.startswith("RS-")
        carrier_reference, carrier_pin = ref["carrier_reference_terminal"].split(".")
        if carrier_pin != "1":
            raise RuntimeError(f"carrier reference pin drift: {bus}")
        axis = link["link_id"].removeprefix("DATA-")
        rows.append(controlled({
            "assembly_id": f"CFA-{bus}", "bus_id": bus,
            "protocol": "RS-485 HALF-DUPLEX" if rs else "TTL HALF-DUPLEX",
            "carrier_board": ref["carrier_board"], "carrier_connector": carrier_reference,
            "carrier_housing_candidate": "GHR-03V-S" if rs else "GHR-02V-S",
            "carrier_contact_candidate": "SSHL-002T-P0.2",
            "first_axis": axis, "destination_connector": link["to_endpoint"],
            "destination_housing_candidate": "EHR-4" if rs else "EHR-3",
            "destination_contact_candidate": "SEH-001T-P0.6",
            "data_conductor_count": 2 if rs else 1,
            "field_reference_leg_count": 1 if rs else 0,
            "carrier_empty_reference_cavity_count": 0 if rs else 1,
            "planning_data_length_mm": link["planning_length_mm"],
            "reference_path": "J10x.1 FIELD RETURN TO UNIQUE RB0 STAR LANDING" if rs else "NO FIELD REFERENCE CONDUCTOR; CTRL_GND USES ONLY GR-PB09 TO RB0",
            "data_conductor_candidate": "SELECTION REQUIRED - GH-compatible impedance/flex construction",
            "shield_rule": "SELECTION REQUIRED - single-end bond and EMC evidence" if rs else "SELECTION REQUIRED - do not create duplicate CTRL_GND path",
            "construction_state": "CONTACT MAP DEFINED - CONDUCTOR, STAR TERMINAL, CRIMP, ROUTE AND TEST RELEASE OPEN",
        }))
    return rows


def contacts(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        aid, bus = str(item["assembly_id"]), str(item["bus_id"])
        c, d = str(item["carrier_connector"]), str(item["destination_connector"])
        rs = bus.startswith("RS-")
        if rs:
            specs = [
                ("01", c, "1", f"RB0-REF-{bus}", "SELECTION REQUIRED", f"{bus}_RET", "POPULATED", "SSHL-002T-P0.2 AT GH; RB0 TERMINAL SELECTION REQUIRED", "UNIQUE FIELD-REFERENCE LEG; NO ACTUATOR PIN-1 CONNECTION"),
                ("02", c, "2", d, "3", f"{bus}_DP", "POPULATED", "SSHL-002T-P0.2 TO SEH-001T-P0.6", "DATA+ ONLY"),
                ("03", c, "3", d, "4", f"{bus}_DN", "POPULATED", "SSHL-002T-P0.2 TO SEH-001T-P0.6", "DATA- ONLY"),
                ("04", "PBR-" + str(item["first_axis"]), "RET", d, "1", "ACTUATOR_BRANCH_RET", "POPULATED BY POWER BRANCH", "SEPARATE POWER-BRANCH PROCESS", "NOT PART OF SERIAL LEAD; COMBINED DESTINATION HOUSING INTERFACE"),
                ("05", "PBR-" + str(item["first_axis"]), "VDD", d, "2", "ACTUATOR_BRANCH_VDD", "POPULATED BY POWER BRANCH", "SEPARATE POWER-BRANCH PROCESS", "NOT PART OF SERIAL LEAD; COMBINED DESTINATION HOUSING INTERFACE"),
            ]
        else:
            specs = [
                ("01", c, "1", "NONE", "NONE", "CTRL_GND", "EMPTY", "NO CONTACT", "DO NOT ADD A SECOND CTRL_GND-TO-RB0 PATH"),
                ("02", c, "2", d, "3", f"{bus}_DATA", "POPULATED", "SSHL-002T-P0.2 TO SEH-001T-P0.6", "TTL DATA ONLY"),
                ("03", "PBR-" + str(item["first_axis"]), "RET", d, "1", "ACTUATOR_BRANCH_RET", "POPULATED BY POWER BRANCH", "SEPARATE POWER-BRANCH PROCESS", "ACTUATOR REFERENCE RETURNS THROUGH ITS OWN POWER PAIR"),
                ("04", "PBR-" + str(item["first_axis"]), "VDD", d, "2", "ACTUATOR_BRANCH_VDD", "POPULATED BY POWER BRANCH", "SEPARATE POWER-BRANCH PROCESS", "NOT PART OF SERIAL LEAD; COMBINED DESTINATION HOUSING INTERFACE"),
            ]
        for suffix, fc, fp, tc, tp, signal, population, termination, rule in specs:
            rows.append(controlled({
                "contact_map_id": f"{aid}-C{suffix}", "assembly_id": aid, "bus_id": bus,
                "from_connector": fc, "from_contact": fp, "to_connector": tc, "to_contact": tp,
                "signal": signal, "required_population": population,
                "termination_candidate": termination, "topology_rule": rule,
                "inspection_result": "NOT EXECUTED",
            }))
    return rows


def routes(items: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in items:
        bus, axis = str(item["bus_id"]), str(item["first_axis"])
        rows.append(controlled({
            "route_leg_id": f"CFA-{bus}-DATA", "assembly_id": item["assembly_id"],
            "service": "RS-485 DATA PAIR" if bus.startswith("RS-") else "TTL DATA",
            "from_interface": item["carrier_connector"], "to_interface": item["destination_connector"],
            "planning_length_mm": item["planning_data_length_mm"],
            "route_basis": f"existing ordinal-one physical link to {axis}",
            "conductor_candidate": "SELECTION REQUIRED - DIRECT GH CRIMP RANGE MUST BE MET",
            "minimum_bend_radius_mm": "SELECTION REQUIRED", "clamp_and_strain_relief": "SELECTION REQUIRED",
            "route_validation": "NOT EXECUTED",
        }))
        if bus.startswith("RS-"):
            rows.append(controlled({
                "route_leg_id": f"CFA-{bus}-REF", "assembly_id": item["assembly_id"],
                "service": "ISOLATED FIELD REFERENCE", "from_interface": f"{item['carrier_connector']}.1",
                "to_interface": f"RB0-REF-{bus}", "planning_length_mm": "SELECTION REQUIRED",
                "route_basis": "carrier-to-pelvis-star path requires exact installed-board/RB0 placement",
                "conductor_candidate": "SELECTION REQUIRED - 0.05 TO 0.13 mm2 GH CONTACT RANGE",
                "minimum_bend_radius_mm": "SELECTION REQUIRED", "clamp_and_strain_relief": "SELECTION REQUIRED",
                "route_validation": "NOT EXECUTED",
            }))
    return rows


def bom() -> list[dict[str, object]]:
    data = [
        ("CFA-B01", "JST", "GHR-03V-S", "three-position GH carrier housing for five RS-485 links", 5, "EXACT FAMILY CANDIDATE - RECEIPT/KEYING CHECK OPEN"),
        ("CFA-B02", "JST", "GHR-02V-S", "two-position GH carrier housing for three TTL links", 3, "EXACT FAMILY CANDIDATE - PIN 1 INTENTIONALLY EMPTY"),
        ("CFA-B03", "JST", "SSHL-002T-P0.2", "GH crimp contact; 15 RS contacts plus 3 TTL data contacts", 18, "EXACT CONTACT CANDIDATE - CRIMP TOOL/HEIGHT/PULL TEST OPEN"),
        ("CFA-B04", "JST", "EHR-4", "integrated first-axis RS-485 actuator housing; shared with power branch", 5, "INTERFACE RESPONSIBILITY - NOT ADDITIVE TO POWER-HARNESS BOM"),
        ("CFA-B05", "JST", "EHR-3", "integrated first-axis TTL actuator housing; shared with power branch", 3, "INTERFACE RESPONSIBILITY - NOT ADDITIVE TO POWER-HARNESS BOM"),
        ("CFA-B06", "JST", "SEH-001T-P0.6", "first-axis actuator data contacts; 10 RS plus 3 TTL", 13, "EXACT CONTACT CANDIDATE - CRIMP TOOL/HEIGHT/PULL TEST OPEN"),
        ("CFA-B07", "SELECTION REQUIRED", "SELECTION REQUIRED", "GH-compatible flexible impedance-controlled RS-485 pair or qualified transition splice", 5, "NO COMPATIBLE DIRECT-CRIMP CABLE RELEASED"),
        ("CFA-B08", "SELECTION REQUIRED", "SELECTION REQUIRED", "GH-compatible flexible TTL data conductor", 3, "NO COMPATIBLE DIRECT-CRIMP CABLE RELEASED"),
        ("CFA-B09", "SELECTION REQUIRED", "SELECTION REQUIRED", "five unique RB0 field-reference landing contacts/terminals", 5, "STAR HARDWARE AND RETENTION OPEN"),
    ]
    return [controlled({"item_id": i, "manufacturer": m, "order_code": o, "description": d, "planning_quantity": q, "selection_state": s}) for i, m, o, d, q, s in data]


def tests() -> list[dict[str, object]]:
    data = [
        ("CFA-T01", "received connector identity", "verify exact GH/EH housings, keys, cavity numbering and mating headers", "zero mismatch"),
        ("CFA-T02", "wire/contact compatibility", "measure conductor cross-section/strand construction and insulation OD against both contact ranges", "within published range or written manufacturer disposition"),
        ("CFA-T03", "crimp process qualification", "cross-section, crimp height, pull and retention samples for every wire/contact pair", "limits selected and accepted by qualified harness reviewer"),
        ("CFA-T04", "contact-map inspection", "100 percent independent cavity-to-cavity inspection", "37 of 37 map rows conform"),
        ("CFA-T05", "continuity", "measure every populated data/reference path end-to-end", "limit selection required"),
        ("CFA-T06", "no-backfeed isolation", "verify no carrier connector provides actuator VDD and no serial lead parallels actuator returns", "zero unintended continuity"),
        ("CFA-T07", "RS field-reference uniqueness", "trace each J101-J105 pin 1 to one unique RB0 landing and nowhere else", "five unique single paths"),
        ("CFA-T08", "TTL reference uniqueness", "trace CTRL_GND to RB0 only through GR-PB09 with J201-J203 pin 1 empty", "one system path; three empty field-reference cavities"),
        ("CFA-T09", "shield/bond inspection", "verify shield treatment matches reviewed topology and cannot create a second reference path", "selection-specific result required"),
        ("CFA-T10", "routing and strain relief", "sweep each linked joint/body route over full commanded range", "no pinch, tension, bend or contact load violation"),
        ("CFA-T11", "RS-485 waveform", "test all five buses at selected baud/termination under branch-current and motion states", "mask/common-mode/error limits selected and met"),
        ("CFA-T12", "TTL margins", "test all three buses at selected baud under worst reference offset and branch current", "VIH/VIL/noise/error limits selected and met"),
        ("CFA-T13", "fault injection", "open each reference/return/data leg and apply defined short/miswire cases through limited-energy fixture", "deterministic fault response without unintended actuation"),
        ("CFA-T14", "qualified disposition", "review serialized build, inspection, route and electrical evidence", "signed acceptance for exact revision and lots"),
    ]
    return [controlled({"test_id": i, "test": name, "method": method, "acceptance": acceptance, "recorded_result": "NONE", "performed_by": "UNASSIGNED", "witness": "UNASSIGNED", "result": "NOT EXECUTED"}) for i, name, method, acceptance in data]


def inspections(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return [controlled({
        "assembly_id": item["assembly_id"], "serial_number": "UNASSIGNED",
        "carrier_connector_identity": "NOT EXECUTED", "destination_connector_identity": "NOT EXECUTED",
        "contact_map": "NOT EXECUTED", "crimp_and_retention": "NOT EXECUTED",
        "continuity": "NOT EXECUTED", "no_backfeed": "NOT EXECUTED",
        "reference_path": "NOT EXECUTED", "route_sweep": "NOT EXECUTED",
        "waveform_or_margin": "NOT EXECUTED", "evidence": "NONE", "result": "NOT EXECUTED",
    }) for item in items]


def holds() -> list[dict[str, object]]:
    data = [
        ("CFA-H01", "exact RS-485 conductor construction is unselected", "GH-compatible 0.05-0.13 mm2 pair or qualified pigtail/splice with impedance, flex and waveform evidence"),
        ("CFA-H02", "the current CFBUS.PVC.001 0.25 mm2 candidate exceeds the GH contact conductor range", "alternate conductor or written JST-approved transition process plus crimp/splice qualification"),
        ("CFA-H03", "the current CF240.01.03 0.14 mm2 TTL candidate exceeds the GH 0.13 mm2 maximum", "alternate conductor or written JST-approved transition process plus crimp/splice qualification"),
        ("CFA-H04", "five RB0 star landing terminals, retention and installed lengths are unselected", "exact PDU/RB0 hardware drawing, one-to-one landing map, route lengths and physical inspection"),
        ("CFA-H05", "shield/bond construction is unresolved", "reviewed one-end shield rule with EMC and fault evidence and no duplicate return path"),
        ("CFA-H06", "GH/EH crimp tools, crimp heights, pull limits and inspection criteria are unselected", "manufacturer tooling/process data and qualified cross-section/pull/retention evidence"),
        ("CFA-H07", "the eight planning lengths are not validated in the joined physical robot", "tolerance-aware installed routing, joint sweep, service slack, clamps and strain-relief evidence"),
        ("CFA-H08", "RS-485 termination, baud, common-mode and error performance are unvalidated", "five-bus waveform/error/fault testing with exact harnesses and actuator loads"),
        ("CFA-H09", "TTL reference offset and logic margins are unvalidated", "three-bus voltage/margin/error/fault testing with exact harnesses and branch currents"),
        ("CFA-H10", "zero carrier-first-axis assemblies have been built or reviewed", "completed serialized traveler, inspection/test register and signed qualified disposition"),
    ]
    return [controlled({"hold_id": i, "unresolved_item": issue, "closure_evidence": evidence, "state": "OPEN"}) for i, issue, evidence in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="920" viewBox="0 0 1600 920" role="img" aria-labelledby="t d"><title id="t">HR-30 carrier-to-first-axis harness topology</title><desc id="d">Five isolated RS-485 channels use data plus a separate field-reference leg to RB0. Three TTL channels use data only and leave the carrier reference cavity empty. Every first-axis housing receives its own protected power pair separately.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}.data{{stroke:#22a7dd;stroke-width:10;fill:none}}.ref{{stroke:#0b4f91;stroke-width:10;fill:none}}.pwr{{stroke:#f2b91d;stroke-width:10;fill:none}}</style><rect width="1600" height="920" fill="#eef8ff"/><text class="h" x="55" y="65">Eight carrier leads; one reference topology</text><rect class="box" x="65" y="145" width="360" height="285" rx="20"/><text x="100" y="195">Carrier field connector</text><text x="100" y="240">RS: GH-3 (REF, D+, D-)</text><text x="100" y="280">TTL: GH-2 (EMPTY, DATA)</text><path class="data" d="M425 275 C680 275 820 275 1085 275"/><path class="ref" d="M260 430 V560 H720"/><text class="s" x="440" y="530">RS only: five unique reference legs</text><rect class="box" x="1085" y="145" width="440" height="285" rx="20"/><text x="1120" y="195">First-axis combined EH housing</text><text x="1120" y="240">1 dedicated branch return</text><text x="1120" y="280">2 dedicated branch VDD</text><text x="1120" y="320">3 DATA / DATA+</text><text x="1120" y="360">4 DATA- (RS only)</text><path class="pwr" d="M1260 145 V90"/><rect class="box" x="720" y="500" width="430" height="150" rx="20"/><text x="765" y="555">RB0 / PDU common return star</text><text class="s" x="765" y="600">Five RS field returns land once.</text><rect class="warn" x="80" y="720" width="1440" height="120" rx="18"/><text x="125" y="770">TTL carrier pin 1 stays empty: CTRL_GND already reaches RB0 once through GR-PB09.</text><text x="125" y="810">No serial lead carries actuator VDD or duplicates an actuator branch return.</text><text class="s" x="55" y="890">{html.escape(WARNING)}</text></svg>'''


def render(items: list[dict[str, object]]) -> str:
    table_rows = "".join(f"<tr><td>{html.escape(str(r['assembly_id']))}</td><td>{html.escape(str(r['protocol']))}</td><td>{html.escape(str(r['carrier_connector']))} / {html.escape(str(r['carrier_housing_candidate']))}</td><td>{html.escape(str(r['destination_connector']))} / {html.escape(str(r['destination_housing_candidate']))}</td><td>{r['planning_data_length_mm']} mm</td><td>{html.escape(str(r['reference_path']))}</td><td>{html.escape(str(r['construction_state']))}</td></tr>" for r in items)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 carrier-to-first-axis harnesses</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:1500px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:#fff;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>Every carrier now reaches its first joint on paper.</h1><p>Five isolated RS-485 channels split data from a unique star-reference leg. Three TTL channels carry data only and leave the carrier reference cavity empty.</p></header><main><section class="grid"><article><div class="metric">8 / 8</div><p>carrier-to-first-axis maps defined</p></article><article><div class="metric">5 + 3</div><p>isolated RS-485 and non-isolated TTL topologies</p></article><article><div class="metric">37</div><p>controlled contact-map rows</p></article><article class="hold"><div class="metric">0</div><p>built, routed or electrically tested harnesses</p></article></section><section><h2>The reference split matters</h2><img src="carrier-first-axis.svg" alt="Five RS field-reference legs land once at RB0 while TTL data does not add a second ground path"></section><section><h2>Connector boundary</h2><div class="panel hold"><p>JST GH and EH housing/contact families are bound, but no conductor is released. The current RS candidate is too large for a direct GH crimp, and the current TTL candidate exceeds the published GH conductor maximum. A compatible cable or a qualified transition splice is still required.</p></div></section><section><h2>Eight controlled candidates</h2><div class="scroll"><table><thead><tr><th>Assembly</th><th>Protocol</th><th>Carrier end</th><th>First-axis end</th><th>Planning length</th><th>Reference path</th><th>State</th></tr></thead><tbody>{table_rows}</tbody></table></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="carrier-first-axis-register.csv">Assembly register</a> | <a href="contact-map.csv">37-contact map</a> | <a href="route-leg-register.csv">Route legs</a> | <a href="candidate-bom.csv">Candidate BOM</a> | <a href="test-plan.csv">Test plan</a> | <a href="inspection-register.csv">Blank inspections</a> | <a href="open-holds.csv">Open holds</a> | <a href="primary-source-register.csv">Sources</a></p><small>This closes a definition gap, not a physical or energization gate.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(items: list[dict[str, object]]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "carrier_first_axis_candidate_defined": True,
        "carrier_first_axis_assembly_count": 8,
        "carrier_first_axis_rs485_count": 5,
        "carrier_first_axis_ttl_count": 3,
        "carrier_first_axis_contact_map_count": 37,
        "carrier_first_axis_rs_reference_leg_count": 5,
        "carrier_first_axis_ttl_empty_reference_cavity_count": 3,
        "carrier_first_axis_conductor_selected": False,
        "carrier_first_axis_built_count": 0,
        "carrier_first_axis_tested_count": 0,
        "carrier_first_axis_selected": False,
        "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    start, end = "<!-- HR30-CARRIER-FIRST-AXIS-P01-README-START -->", "<!-- HR30-CARRIER-FIRST-AXIS-P01-README-END -->"
    path = WHOLE / "README.md"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Carrier-to-first-axis harnesses\n\nThe [interactive eight-lead guide](harness/carrier-first-axis-p0.1/index.html) binds every carrier output to its first actuator through **37 controlled contact-map rows**. Five isolated RS-485 connectors use a separate unique field-reference leg to RB0; three TTL connectors leave the field reference cavity empty so `CTRL_GND` still reaches RB0 only through `GR-PB09`. JST GH/EH housing and contact families are explicit. The conductor, reference landing, crimp process, physical routing, waveform evidence and qualified disposition remain open; zero assemblies exist.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text + "\n" + block
    path.write_text(text, encoding="utf-8", newline="\n")

    start, end = "<!-- HR30-CARRIER-FIRST-AXIS-P01-START -->", "<!-- HR30-CARRIER-FIRST-AXIS-P01-END -->"
    path = WHOLE / "index.html"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="carrier-first-axis"><h2>Eight carrier leads now have exact contact maps</h2><div class="grid"><article class="card pass"><div class="metric">8 / 8</div><p>carrier-to-first-axis interfaces defined.</p></article><article class="card"><div class="metric">37</div><p>controlled contact-map rows.</p></article><article class="card"><div class="metric">5 + 3</div><p>unique RS field-reference legs and intentionally empty TTL reference cavities.</p></article><article class="card hold"><h3>Conductor still open</h3><p>The published GH range rejects direct crimp of both existing planning cable candidates.</p></article></div><p><a href="harness/carrier-first-axis-p0.1/index.html">Open the interactive carrier-to-first-axis guide</a>. It defines the boundary without granting physical work or energization authority.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    links = first_links()
    items = assemblies(links)
    src = sources()
    cmap, legs, parts = contacts(items), routes(items), bom()
    test_rows, inspection_rows, hold_rows = tests(), inspections(items), holds()
    if (len(items), len(cmap), len(legs), len(parts), len(test_rows), len(inspection_rows), len(hold_rows)) != (8, 37, 13, 9, 14, 8, 10):
        raise RuntimeError("carrier-first-axis package coverage drift")
    write_csv(OUT / "primary-source-register.csv", src)
    write_csv(OUT / "carrier-first-axis-register.csv", items)
    write_csv(OUT / "contact-map.csv", cmap)
    write_csv(OUT / "route-leg-register.csv", legs)
    write_csv(OUT / "candidate-bom.csv", parts)
    write_csv(OUT / "test-plan.csv", test_rows)
    write_csv(OUT / "inspection-register.csv", inspection_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "date": DATE,
        "assembly_count": 8, "rs485_assembly_count": 5, "ttl_assembly_count": 3,
        "contact_map_row_count": 37, "route_leg_count": 13,
        "rs_field_reference_leg_count": 5, "ttl_empty_reference_cavity_count": 3,
        "carrier_connector_family_bound": True, "destination_connector_family_bound": True,
        "conductor_selected": False, "rb0_star_landing_selected": False,
        "shield_topology_selected": False, "crimp_process_selected": False,
        "built_assembly_count": 0, "inspected_assembly_count": 0,
        "route_validated_assembly_count": 0, "electrically_tested_assembly_count": 0,
        "assembly_selected": False, "procurement_authority": False,
        "fabrication_authority": False, "assembly_authority": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "carrier-first-axis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 carrier-to-first-axis harness P0.1\n\n**{WARNING}**\n\nThis package closes the eight-link physical definition gap between the two interface-carrier boards and each bus's first actuator. It freezes contact maps and reference topology while leaving incompatible planning cables, exact star hardware, crimping, routing, electrical tests and qualified acceptance open.\n", encoding="utf-8", newline="\n")
    (OUT / "carrier-first-axis.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(items), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "carrier-first-axis-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(items)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
