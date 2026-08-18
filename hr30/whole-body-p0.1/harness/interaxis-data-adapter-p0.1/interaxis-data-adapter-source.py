#!/usr/bin/env python3
"""Generate the HR-30 17-link inter-axis data-cable adaptation candidate.

The package reuses factory-terminated ROBOTIS X4P/X3P cables only as
controlled adaptation candidates.  It never treats an unmodified powered
daisy cable as compatible with the individually protected actuator feeds.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
PHYSICAL = WHOLE / "harness" / "physical-p0.1"
CABLE_KIT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
OUT = WHOLE / "harness" / "interaxis-data-adapter-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-INTERAXIS-DATA-ADAPTER-P0.1"
DATE = "2026-08-18"
WARNING = "PRELIMINARY - UNBUILT INTER-AXIS DATA ADAPTER CANDIDATE - NOT APPROVED FOR PROCUREMENT, MODIFICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, MODIFICATION, ASSEMBLY, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


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
        ("IAD-S01", "physical serial-data links", PHYSICAL / "serial-data-link-register.csv", "25 controller/inter-axis serial links and endpoints"),
        ("IAD-S02", "controlled connector-cavity population", CABLE_KIT / "connector-cavity-population.csv", "upstream empty cavities and downstream combined power/data housing population"),
        ("IAD-S03", "actuator service-loop obligations", PHYSICAL / "service-loop-register.csv", "joint axes and unresolved physical loop validation"),
        ("IAD-S04", "actuator data-cable disposition", CABLE_KIT / "data-cable-candidate.csv", "unmodified powered ROBOTIS daisy cables rejected"),
        ("IAD-S05", "eight-bus reference architecture", CABLE_KIT / "bus-reference-register.csv", "no inter-actuator GND/VDD conductor and single-point reference intent"),
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
        ("IAD-S06", "ROBOTIS", "Robot Cable-X4P 240 mm, 10 pieces", "live official store page; accessed 2026-08-18; revision not stated", "https://robotis.us/robot-cable-x4p-240mm-10pcs/", "SKU 903-0245-000; 240 mm RS-485 X/P-series cable family; received end construction still requires inspection"),
        ("IAD-S07", "ROBOTIS", "Robot Cable-X3P 180 mm, 10 pieces", "live official store page; accessed 2026-08-18; revision not stated", "https://robotis.us/robot-cable-x3p-180mm-10pcs/", "SKU 903-0249-000; 180 mm TTL X-series cable family; received end construction still requires inspection"),
        ("IAD-S08", "ROBOTIS", "XH540-W270 connector information", "ROBOTIS Docs live page; accessed 2026-08-18; page revision not stated", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/", "RS-485 device interface pin 1 GND, pin 2 VDD, pin 3 DATA+, pin 4 DATA-"),
        ("IAD-S09", "ROBOTIS", "XC330-T288 connector information", "ROBOTIS Docs live page; accessed 2026-08-18; page revision not stated", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/", "TTL device interface pin 1 GND, pin 2 VDD, pin 3 DATA"),
        ("IAD-S10", "JST", "EH connector data sheet", "current official PDF; accessed 2026-08-18", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "EH housing/contact family boundaries; no cable-modification approval inferred"),
    ]
    for sid, publisher, document, revision, url, scope in official:
        rows.append(controlled({
            "source_id": sid, "publisher": publisher, "document": document,
            "revision_or_date": revision, "official_url_or_path": url,
            "sha256": "NOT APPLICABLE - EXTERNAL PRIMARY SOURCE", "verified_scope": scope,
        }))
    return rows


def point(text: str) -> tuple[float, float, float]:
    return tuple(float(value) for value in text.strip("()").split(","))  # type: ignore[return-value]


def adapters() -> list[dict[str, object]]:
    links = read_csv(PHYSICAL / "serial-data-link-register.csv")
    loops = {row["axis_id"]: row for row in read_csv(PHYSICAL / "service-loop-register.csv")}
    interaxis = [row for row in links if row["from_endpoint"].startswith("J-OUT-")]
    if len(interaxis) != 17:
        raise RuntimeError(f"expected 17 inter-axis links, found {len(interaxis)}")
    rows: list[dict[str, object]] = []
    for link in interaxis:
        destination_axis = link["link_id"].removeprefix("DATA-")
        source_axis = link["from_endpoint"].removeprefix("J-OUT-")
        a, b = point(loops[source_axis]["joint_axis_xyz_mm"]), point(loops[destination_axis]["joint_axis_xyz_mm"])
        spacing = math.dist(a, b)
        if link["bus_id"].startswith("RS-"):
            protocol = "RS-485"
        elif link["bus_id"].startswith("TTL-"):
            protocol = "TTL"
        else:
            raise RuntimeError(f"unrecognized actuator bus family: {link['bus_id']}")
        rs485 = protocol == "RS-485"
        rows.append(controlled({
            "adapter_id": f"IAD-{link['bus_id']}-{int(link['ordinal']):02d}",
            "link_id": link["link_id"], "bus_id": link["bus_id"], "protocol": protocol,
            "source_axis": source_axis, "destination_axis": destination_axis,
            "source_connector": link["from_endpoint"], "destination_connector": link["to_endpoint"],
            "base_cable": "ROBOTIS Robot Cable-X4P 240 mm" if rs485 else "ROBOTIS Robot Cable-X3P 180 mm",
            "robotis_sku": "903-0245-000" if rs485 else "903-0249-000",
            "nominal_cable_length_mm": 240 if rs485 else 180,
            "joint_axis_spacing_mm": f"{spacing:.3f}",
            "nominal_length_minus_axis_spacing_mm": f"{(240 if rs485 else 180) - spacing:.3f}",
            "factory_data_contacts_retained": "SOURCE+DESTINATION CAVITY 3 DATA+ AND CAVITY 4 DATA-" if rs485 else "SOURCE+DESTINATION CAVITY 3 DATA",
            "factory_power_conductors_removed": "GND CAVITY 1 AND VDD CAVITY 2 - REMOVE COMPLETE CONDUCTORS AND FOUR TERMINALS",
            "source_cavity_1": "EMPTY", "source_cavity_2": "EMPTY",
            "destination_cavity_1": "INSERT DEDICATED BRANCH RETURN CONTACT",
            "destination_cavity_2": "INSERT DEDICATED BRANCH VDD CONTACT",
            "destination_data_cavities": "3,4" if rs485 else "3",
            "required_label": f"DATA-ONLY UPSTREAM / BRANCH-POWERED {destination_axis}",
            "adaptation_state": "UNBUILT CANDIDATE - RECEIVED CABLE, EXTRACTION, REINSERTION, ROUTE AND COMMUNICATION VALIDATION REQUIRED",
        }))
    return rows


def bom(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        controlled({"item_id": "IAD-B01", "manufacturer": "ROBOTIS", "order_code": "903-0245-000", "description": "Robot Cable-X4P 240 mm, 10-piece package", "planning_quantity": "2 packages / 20 cables", "assigned_quantity": sum(r["protocol"].startswith("RS-485") for r in rows), "planning_spares": 6, "selection_state": "QUOTE / RECEIPT-INSPECTION CANDIDATE ONLY"}),
        controlled({"item_id": "IAD-B02", "manufacturer": "ROBOTIS", "order_code": "903-0249-000", "description": "Robot Cable-X3P 180 mm, 10-piece package", "planning_quantity": "1 package / 10 cables", "assigned_quantity": sum(r["protocol"].startswith("TTL") for r in rows), "planning_spares": 7, "selection_state": "QUOTE / RECEIPT-INSPECTION CANDIDATE ONLY"}),
        controlled({"item_id": "IAD-B03", "manufacturer": "SELECTION REQUIRED", "order_code": "SELECTION REQUIRED", "description": "damage-controlled EH contact extraction tool/process compatible with received factory assembly", "planning_quantity": 1, "assigned_quantity": 0, "planning_spares": 0, "selection_state": "UNRESOLVED - DO NOT SUBSTITUTE OR MODIFY CABLE"}),
        controlled({"item_id": "IAD-B04", "manufacturer": "Project Button", "order_code": "SERIALIZED DATA-ONLY LABEL SET", "description": "17 upstream/downstream orientation labels plus cable serial labels", "planning_quantity": "17 sets", "assigned_quantity": 17, "planning_spares": "SELECTION REQUIRED", "selection_state": "ARTWORK / MATERIAL / RETENTION TEST REQUIRED"}),
    ]


def traveler() -> list[dict[str, object]]:
    actions = [
        ("IAD-W01", "record supplier, SKU, package/lot, received quantity, cable length and both connector end styles", "incoming record complete; any end-style mismatch stops work"),
        ("IAD-W02", "serialize each cable and photograph both housings before modification", "cavity numbering/orientation visible; do not identify cavities by wire color alone"),
        ("IAD-W03", "select and qualify a damage-controlled extraction method on sacrificial samples", "housing lance, terminal and insulation damage criteria approved before production-candidate work"),
        ("IAD-W04", "extract complete factory GND and VDD conductors from cavities 1 and 2 at both ends", "two complete conductors and four terminals removed; no cut-flush or hidden unterminated conductor"),
        ("IAD-W05", "inspect retained data terminals, housing lances and empty upstream cavities", "no visible damage; retained data terminals locked; upstream cavities 1 and 2 empty"),
        ("IAD-W06", "insert the destination actuator's separately qualified branch-return and branch-VDD contacts into cavities 1 and 2", "polarity, full insertion and retention recorded against adapter register"),
        ("IAD-W07", "perform 100 percent point-to-point continuity and wrong-cavity inspection", "only required data paths and destination power contacts present"),
        ("IAD-W08", "measure isolation from upstream cavities 1/2 to every conductor and destination power contact", "acceptance resistance and test voltage SELECTION REQUIRED by qualified electrical reviewer"),
        ("IAD-W09", "perform pull/retention and repeated-mate inspection on sacrificial/qualification samples", "force, cycles and damage limits SELECTION REQUIRED; no production-candidate reuse without disposition"),
        ("IAD-W10", "route the nominal cable length through the exact joint pair and full commanded range", "no tension, pinch, connector load or bend violation; final clamp/slack disposition recorded"),
        ("IAD-W11", "apply orientation and data-only labels at both ends", "label readable after routing; upstream end cannot be mistaken for a powered input"),
        ("IAD-W12", "run unpowered continuity/no-backfeed matrix with all 17 adapters and 25 branch-power pairs installed", "no inter-axis GND/VDD continuity; expected data continuity only"),
        ("IAD-W13", "execute one-segment current-limited communication test only after separate powered-test authorization", "baud, termination, waveform, errors and reference offset recorded"),
        ("IAD-W14", "qualified harness/electrical reviewer issues disposition for identical serialized assemblies", "signed record references exact lots, extraction process, route state and test evidence"),
    ]
    return [controlled({"step_id": sid, "action": action, "completion_evidence": evidence, "recorded_value": "NONE", "performed_by": "UNASSIGNED", "witness": "UNASSIGNED", "result": "NOT EXECUTED"}) for sid, action, evidence in actions]


def inspections(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [controlled({
        "adapter_id": row["adapter_id"], "serial_number": "UNASSIGNED", "received_sku": "NONE",
        "received_length_mm": "NONE", "end_style_verified": "NOT EXECUTED",
        "source_cavities_1_2_empty": "NOT EXECUTED", "destination_power_contacts_present": "NOT EXECUTED",
        "data_continuity": "NOT EXECUTED", "power_isolation": "NOT EXECUTED",
        "terminal_retention": "NOT EXECUTED", "route_sweep": "NOT EXECUTED",
        "communication_test": "NOT EXECUTED", "result": "NOT EXECUTED", "evidence": "NONE",
    }) for row in rows]


def holds() -> list[dict[str, object]]:
    data = [
        ("IAD-H01", "ROBOTIS does not publish approval for the proposed GND/VDD conductor removal and hybrid destination housing", "written manufacturer disposition or qualified internal modification process with destructive evidence"),
        ("IAD-H02", "the exact received X4P/X3P connector-end construction and cavity indexing have not been inspected", "received-lot inspection against SKU, length, housings, contacts and cavity numbering"),
        ("IAD-H03", "a damage-controlled extraction tool and terminal/housing reuse rule are not selected", "sacrificial extraction trials, magnified inspection, retention tests and approved scrap/reuse rule"),
        ("IAD-H04", "ROBOTIS does not publish cable bend life, minimum bend radius, pair impedance, shield construction or torsional life", "received construction review plus route-specific bend/torsion and waveform/error qualification"),
        ("IAD-H05", "240 mm and 180 mm nominal lengths are not validated in the joined production-body geometry", "full-range physical routing and tolerance-aware CAD sweep with clamps, slack, pinch and connector-load evidence"),
        ("IAD-H06", "destination power-contact insertion depends on the still-unreleased actuator power pigtail crimp process", "accepted power-branch crimp/retention/thermal process before hybrid-housing assembly"),
        ("IAD-H07", "RS-485 baud, termination, common-mode, reflections, shielding and error-rate behavior are untested", "serialized five-bus waveform/error validation across route, load and motion states"),
        ("IAD-H08", "TTL reference offset, high/low margins and edge behavior are untested", "serialized three-bus TTL waveform/margin validation across branch-current and motion states"),
        ("IAD-H09", "the eight carrier-to-first-actuator harnesses are outside this 17-link package and remain undefined physically", "separate exact carrier breakout harness design with contact maps, reference-star conductors and route validation"),
        ("IAD-H10", "no adapter has been built, inspected, routed, communication-tested or accepted", "completed traveler and signed qualified electrical/harness review for identical serialized assemblies"),
    ]
    return [controlled({"hold_id": sid, "unresolved_item": issue, "closure_evidence": closure, "state": "OPEN"}) for sid, issue, closure in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc"><title id="title">HR-30 inter-axis data adapter candidate</title><desc id="desc">A factory ROBOTIS data cable has its GND and VDD conductors removed. The upstream actuator housing keeps cavities one and two empty; the destination housing receives that actuator's dedicated branch power contacts while factory data contacts remain.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.empty{{fill:#fff0b5;stroke:#982520;stroke-width:4}}.data{{stroke:#28a9df;stroke-width:10;fill:none}}.power{{stroke:#f2b91d;stroke-width:10;fill:none}}.ret{{stroke:#0b4f91;stroke-width:10;fill:none}}</style><rect width="1600" height="900" fill="#eef8ff"/><text class="h" x="55" y="65">Adapt the cable; do not daisy-chain actuator power</text><rect class="box" x="60" y="150" width="430" height="330" rx="20"/><text x="95" y="200">Upstream actuator output housing</text><rect class="empty" x="110" y="245" width="100" height="62" rx="12"/><text x="145" y="285">1</text><rect class="empty" x="230" y="245" width="100" height="62" rx="12"/><text x="265" y="285">2</text><rect class="box" x="110" y="330" width="100" height="62" rx="12"/><text x="145" y="370">3</text><rect class="box" x="230" y="330" width="100" height="62" rx="12"/><text x="265" y="370">4</text><text class="s" x="105" y="435">Cavities 1/2 EMPTY; data only</text><path class="data" d="M330 350 C600 350 750 350 1030 350"/><path class="data" d="M330 385 C600 385 750 385 1030 385"/><rect class="box" x="1030" y="150" width="500" height="330" rx="20"/><text x="1065" y="200">Destination combined input housing</text><rect class="box" x="1080" y="245" width="100" height="62" rx="12"/><text x="1115" y="285">1</text><rect class="box" x="1200" y="245" width="100" height="62" rx="12"/><text x="1235" y="285">2</text><rect class="box" x="1080" y="330" width="100" height="62" rx="12"/><text x="1115" y="370">3</text><rect class="box" x="1200" y="330" width="100" height="62" rx="12"/><text x="1235" y="370">4</text><path class="ret" d="M1130 245 V110"/><path class="power" d="M1250 245 V110"/><text class="s" x="1330" y="265">1 dedicated return</text><text class="s" x="1330" y="300">2 dedicated VDD</text><text class="s" x="1330" y="355">3/4 factory data</text><rect x="115" y="585" width="1370" height="180" rx="20" fill="#fff0b5" stroke="#982520" stroke-width="4"/><text x="160" y="635">Remove both factory GND/VDD conductors completely; never cut them flush or leave hidden live ends.</text><text x="160" y="680">Insert only the destination actuator's separately qualified branch-power contacts into cavities 1 and 2.</text><text x="160" y="725">All extraction, retention, routing, no-backfeed and communication tests remain unexecuted.</text><text class="s" x="55" y="850">{html.escape(WARNING)}</text></svg>'''


def render(rows: list[dict[str, object]]) -> str:
    table_rows = "".join(
        f"<tr><td>{html.escape(str(r['adapter_id']))}</td><td>{html.escape(str(r['source_axis']))} → {html.escape(str(r['destination_axis']))}</td><td>{html.escape(str(r['robotis_sku']))}</td><td>{r['nominal_cable_length_mm']} mm</td><td>{r['joint_axis_spacing_mm']} mm</td><td>{html.escape(str(r['destination_data_cavities']))}</td><td>{html.escape(str(r['adaptation_state']))}</td></tr>"
        for r in rows
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 inter-axis data adapters</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:17ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1400px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>Seventeen inter-axis links now have a physical adaptation candidate.</h1><p>Factory data contacts stay intact. Factory power conductors come out. Each destination housing receives only its own protected branch-power contacts.</p></header><main><section class="grid"><article><div class="metric">17</div><p>inter-axis cable adaptations</p></article><article><div class="metric">14 + 3</div><p>RS-485 X4P and TTL X3P links</p></article><article><div class="metric">34</div><p>factory power conductors removed completely</p></article><article class="hold"><div class="metric">0</div><p>built, inspected, routed or communication-tested adapters</p></article></section><section><h2>One cable, two different ends</h2><img src="interaxis-data-adapter.svg" alt="Data-only upstream housing and branch-powered destination housing"></section><section><h2>Construction boundary</h2><div class="panel hold"><p>This is not an instruction to modify purchased cables yet. ROBOTIS does not publish approval for this adaptation, the extraction method is unresolved, and the received connector construction must be inspected first. The destination power contacts depend on the separately qualified actuator-power process.</p></div></section><section><h2>All 17 link candidates</h2><div class="scroll"><table><thead><tr><th>Adapter</th><th>Axis pair</th><th>Base SKU</th><th>Nominal length</th><th>Axis spacing</th><th>Data cavities</th><th>State</th></tr></thead><tbody>{table_rows}</tbody></table></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="interaxis-adapter-register.csv">17-link register</a> | <a href="adapter-bom.csv">Candidate BOM</a> | <a href="adapter-build-traveler.csv">Build traveler</a> | <a href="adapter-inspection-register.csv">Blank inspection records</a> | <a href="open-holds.csv">Open holds</a> | <a href="primary-source-register.csv">Primary sources</a></p><small>The eight controller-to-first-actuator harnesses are not hidden here; they remain a separate explicit open boundary.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(rows: list[dict[str, object]]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "interaxis_data_adapter_candidate_defined": True,
        "interaxis_data_adapter_count": len(rows),
        "interaxis_data_adapter_rs485_count": sum(r["protocol"].startswith("RS-485") for r in rows),
        "interaxis_data_adapter_ttl_count": sum(r["protocol"].startswith("TTL") for r in rows),
        "interaxis_factory_power_conductor_removal_count": len(rows) * 2,
        "interaxis_extracted_terminal_count": len(rows) * 4,
        "interaxis_destination_branch_power_contact_count": len(rows) * 2,
        "interaxis_upstream_empty_power_cavity_count": len(rows) * 2,
        "interaxis_data_adapter_built_count": 0,
        "interaxis_data_adapter_inspected_count": 0,
        "interaxis_data_adapter_communication_tested_count": 0,
        "interaxis_data_adapter_selected": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    start, end = "<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-README-START -->", "<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-README-END -->"
    path = WHOLE / "README.md"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Inter-axis data adapters\n\nThe [interactive 17-link adaptation guide](harness/interaxis-data-adapter-p0.1/index.html) binds **14 RS-485 X4P** and **3 TTL X3P** inter-actuator links to exact ROBOTIS cable-family SKUs. Each candidate removes both factory power conductors completely, leaves upstream cavities 1/2 empty, retains factory data contacts, and inserts the destination actuator's dedicated protected branch-power contacts into its combined input housing. Zero adapters have been modified, inspected, routed or communication-tested; the eight carrier-to-first-actuator harnesses remain a separate open boundary.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text + "\n" + block
    path.write_text(text, encoding="utf-8", newline="\n")

    start, end = "<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-START -->", "<!-- HR30-INTERAXIS-DATA-ADAPTER-P01-END -->"
    path = WHOLE / "index.html"
    text = path.read_text(encoding="utf-8")
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="interaxis-data-adapter"><h2>Seventeen inter-axis data links now have a physical adaptation candidate</h2><div class="grid"><article class="card pass"><div class="metric">17 / 17</div><p>inter-axis links map to exact X4P/X3P cable-family SKUs and cavity actions.</p></article><article class="card"><div class="metric">14 + 3</div><p>RS-485 and TTL link candidates.</p></article><article class="card"><div class="metric">34</div><p>factory GND/VDD conductors removed completely; upstream power cavities remain empty.</p></article><article class="card hold"><h3>Unbuilt adaptation</h3><p>Extraction, destination power-contact insertion, routing, retention, no-backfeed and communication tests remain unexecuted.</p></article></div><p><a href="harness/interaxis-data-adapter-p0.1/index.html">Open the interactive inter-axis data-adapter guide</a>. The eight carrier leads remain explicitly open, and no work authority follows.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    src, rows = sources(), adapters()
    parts, steps, checks, open_holds = bom(rows), traveler(), inspections(rows), holds()
    write_csv(OUT / "primary-source-register.csv", src)
    write_csv(OUT / "interaxis-adapter-register.csv", rows)
    write_csv(OUT / "adapter-bom.csv", parts)
    write_csv(OUT / "adapter-build-traveler.csv", steps)
    write_csv(OUT / "adapter-inspection-register.csv", checks)
    write_csv(OUT / "open-holds.csv", open_holds)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "date": DATE,
        "interaxis_adapter_count": len(rows),
        "rs485_x4p_adapter_count": sum(r["protocol"].startswith("RS-485") for r in rows),
        "ttl_x3p_adapter_count": sum(r["protocol"].startswith("TTL") for r in rows),
        "factory_power_conductor_removal_count": len(rows) * 2,
        "extracted_factory_terminal_count": len(rows) * 4,
        "destination_branch_power_contact_insertion_count": len(rows) * 2,
        "upstream_required_empty_power_cavity_count": len(rows) * 2,
        "carrier_to_first_axis_harness_count_in_scope": 0,
        "carrier_to_first_axis_harness_count_open": 8,
        "base_cable_family_order_codes_bound": True,
        "cavity_adaptation_defined": True,
        "unmodified_powered_daisy_cable_approved": False,
        "extraction_process_selected": False,
        "destination_power_contact_process_selected": False,
        "built_adapter_count": 0, "inspected_adapter_count": 0,
        "route_validated_adapter_count": 0, "communication_tested_adapter_count": 0,
        "adapter_selected": False, "procurement_authority": False,
        "modification_authority": False, "assembly_authority": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "interaxis-data-adapter-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 inter-axis data adapter P0.1\n\n**{WARNING}**\n\nThis package defines a physical adaptation candidate for all 17 actuator-to-actuator serial links. It retains factory data contacts, removes complete factory GND/VDD conductors, leaves upstream power cavities empty, and inserts only the destination actuator's dedicated branch-power contacts into the downstream combined housing. It does not authorize modifying a purchased cable.\n", encoding="utf-8", newline="\n")
    (OUT / "interaxis-data-adapter.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(rows), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "interaxis-data-adapter-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(rows)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
