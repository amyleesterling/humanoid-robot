#!/usr/bin/env python3
"""Generate the HR-30 protective-earth and DC-reference candidate architecture."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "grounding-reference-architecture-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
IDENTIFIER = "HR30-GROUNDING-REFERENCE-ARCHITECTURE-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - UNBUILT GROUNDING CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def sources() -> list[dict[str, object]]:
    data = [
        ("GR-S01", "Mean Well", "RSP-500-12 specification", "RSP-500-SPEC; 2025-09-26", "https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF", "candidate source PE/FG boundary and AC/DC terminal identity; installation approval remains open"),
        ("GR-S02", "Mean Well", "SD-15 specification", "SD-15-SPEC; 2024-11-22", "https://www.meanwell.com/Upload/PDF/SD-15/SD-15-SPEC.PDF", "candidate auxiliary converter FG and input/output terminal identity"),
        ("GR-S03", "Anderson Power", "SBS connector assembly instructions", "1S6417; accessed 2026-08-16", "https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/SBS75G/1s6417-SBS-Assembly-Instructions.pdf", "SBS75G ground-contact family and assembly boundary"),
        ("GR-S04", "Anderson Power", "SBS75G product page", "live official page; accessed 2026-08-16", "https://www.andersonpower.com/product/sbs75g-silver-plated-pre-mate-wire-contacts-12-10-awg/", "third first-mate/last-break ground-or-power contact feature; application remains project-owned"),
        ("GR-S05", "SIGLENT", "SPD3303X/X-E Quick Start", "EN02A; 2024-09-02", "https://siglentna.com/wp-content/uploads/dlm_uploads/2022/11/SPD3303X_QuickStart_E02A.pdf", "independent-mode outputs insulated from ground; exact bench connection still requires review"),
        ("GR-S06", "STMicroelectronics", "STLINK-V3MINIE user manual", "UM2910 Rev 4; 2025-11", "https://www.st.com/resource/en/user_manual/um2910-stlinkv3minie-debuggerprogrammer-tiny-probe-for-stm32-microcontrollers-stmicroelectronics.pdf", "target GND and target-voltage sense pins; no isolation claim credited"),
        ("GR-S07", "Tektronix", "ABCs of Probes primer", "live official primer; accessed 2026-08-16", "https://www.tek.com/en/documents/whitepaper/abcs-probes-primer", "ground-referenced probes connect through oscilloscope protective earth; never defeat equipment ground"),
        ("GR-S08", "Tektronix", "Setting up and using an oscilloscope", "live official primer; accessed 2026-08-16", "https://www.tek.com/en/documents/primer/setting-and-using-oscilloscope", "oscilloscope protective grounding and shared-reference warning"),
    ]
    return [common({"source_id": i, "manufacturer": m, "document": d, "revision_or_date": rev, "accessed": DATE, "url": url, "verified_use": use}) for i, m, d, rev, url, use in data]


def bindings() -> list[dict[str, object]]:
    data = [
        ("GR-B01", "external source/tether candidate", "electrical/tether-power-core-p0.1/power-core-status.json"),
        ("GR-B02", "SBS75G project contact map", "electrical/tether-power-core-p0.1/connector-contact-map.csv"),
        ("GR-B03", "whole-body ECAD boundary", "electrical/kicad/hr30-whole-body-electrical-p0.1/electrical-status.json"),
        ("GR-B04", "whole-body physical harness", "harness/physical-p0.1/physical-harness-status.json"),
        ("GR-B05", "motion-controller boundary", "electrical/motion-controller-p0.1/controller-status.json"),
        ("GR-B06", "logic-only bench source", "electrical/logic-power-kit-p0.1/logic-power-status.json"),
        ("GR-B07", "SWD adapter", "electrical/swd-adapter-p0.1/adapter-status.json"),
    ]
    rows = []
    for ident, role, rel in data:
        path = WHOLE / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(common({"binding_id": ident, "role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    return rows


def domains() -> list[dict[str, object]]:
    data = [
        ("GR-D01", "FACILITY_PE", "protective earth", "external panel PE bar", "must remain continuous independently of DC return and control electronics"),
        ("GR-D02", "PANEL_PE", "protective bonding", "Hammond enclosure, source FG terminals and tether PE contact", "candidate equipotential panel network; exact bar, studs and conductors open"),
        ("GR-D03", "ROBOT_FRAME_PE", "protective bonding", "SBS75G G contact to one pelvis frame-bond hub and exposed conductive structure", "candidate first-mate/last-break robot frame path; shells/joints need continuity strategy"),
        ("GR-D04", "ACTUATOR_DC_RETURN", "power return", "RSP-500-12 negative output through tether P2 and robot return bus", "not protective earth; no frame-current routing allowed in normal operation"),
        ("GR-D05", "CTRL_GND", "logic reference", "controller, carriers, transceivers, sensors and logic supply return", "candidate single reference to ACTUATOR_DC_RETURN at distribution boundary; exact impedance/EMC treatment open"),
        ("GR-D06", "CABLE_SHIELD", "EMC shield", "connector shell/drain termination network", "bonding end(s), capacitance, 360-degree hardware and EMC evidence selection required"),
        ("GR-D07", "BENCH_FLOATING_RETURN", "temporary isolated-output reference", "SIGLENT CH1- before external equipment is attached", "no intentional PE bond; USB, SWD or oscilloscope can change this state"),
    ]
    return [common({"domain_id": i, "net_or_domain": net, "classification": cls, "extent": extent, "rule": rule, "approved": "NO"}) for i, net, cls, extent, rule in data]


def bonds() -> list[dict[str, object]]:
    data = [
        ("GR-PB01", "facility PE", "external panel PE bar", "permanent protective bond", "external panel", "SELECTION REQUIRED", "required candidate path; facility/enclosure assumptions open"),
        ("GR-PB02", "external panel PE bar", "Hammond enclosure bonding stud", "permanent protective bond", "external panel", "SELECTION REQUIRED", "paint removal, stud, washers and enclosure instructions open"),
        ("GR-PB03", "external panel PE bar", "RSP-500-12 FG", "permanent protective bond", "external panel", "SELECTION REQUIRED", "terminal and conductor release open"),
        ("GR-PB04", "external panel PE bar", "SD-15A-24 FG", "permanent protective bond", "external panel", "SELECTION REQUIRED", "terminal and conductor release open"),
        ("GR-PB05", "external panel PE bar", "XT1A SBS75G G", "permanent protective bond", "external panel/tether", "SELECTION REQUIRED", "ground contact first-mate feature candidate; contact/wire sizing open"),
        ("GR-PB06", "XT1B SBS75G G", "pelvis frame-bond hub", "permanent protective bond", "robot pelvis", "SELECTION REQUIRED", "one controlled landing point; exact stud/terminal open"),
        ("GR-PB07", "pelvis frame-bond hub", "torso, pelvis, both legs, both arms, head conductive frame zones", "segmented protective bonds", "whole robot", "SELECTION REQUIRED", "joint/bearing interfaces are not credited as bonds; flexible jumpers or qualified conductive interfaces required"),
        ("GR-PB08", "ACTUATOR_DC_RETURN bus RB0", "pelvis frame-bond hub", "single proposed removable DC0V/PE bond BR1", "robot pelvis distributor", "SELECTION REQUIRED", "SOLE INTENTIONAL DC RETURN/PE BOND CANDIDATE; qualified disposition and physical proof open"),
        ("GR-PB09", "CTRL_GND", "ACTUATOR_DC_RETURN bus RB0", "single logic-reference connection", "robot pelvis distributor", "SELECTION REQUIRED", "topology/impedance/EMC and fault-current behavior open"),
        ("GR-PB10", "cable shields/drains", "approved shield-bond hardware", "EMC bond", "connector boundaries", "SELECTION REQUIRED", "not a substitute for PE; termination scheme requires EMC testing"),
    ]
    return [common({"bond_id": i, "from_node": src, "to_node": dst, "bond_function": function, "candidate_location": location, "conductor_or_hardware": hardware, "disposition": disposition, "installed": "NO", "measured": "NO"}) for i, src, dst, function, location, hardware, disposition in data]


def instruments() -> list[dict[str, object]]:
    data = [
        ("GR-I01", "SIGLENT SPD3303X CH1 only", "CH1+ / CH1-", "manufacturer states output insulated from ground in independent mode", "BENCH_FLOATING_RETURN", "no intentional PE bond before other equipment", "review all other connections before mating J1"),
        ("GR-I02", "STLINK-V3MINIE + grounded USB host", "J2.1 CTRL_GND plus target-voltage sense", "manufacturer documents target GND but no galvanic-isolation claim is credited", "CTRL_GND", "possible additional reference path via USB host", "measure host-to-target ground path unpowered; use only approved isolated alternative if required"),
        ("GR-I03", "ground-referenced bench oscilloscope", "probe ground clip / BNC shell", "probe reference is normally tied through instrument protective earth", "APPROVED PE-REFERENCED NODE ONLY", "can create or bypass the proposed single bond", "never float or defeat oscilloscope PE; use approved differential/isolated probe architecture where needed"),
        ("GR-I04", "USB connection to Raspberry Pi", "USB shield and signal ground", "exact chassis/signal-ground path depends on received host and cable", "CTRL_GND / CABLE_SHIELD", "possible reference and shield bond", "characterize received equipment unpowered; no USB connection until matrix is approved"),
        ("GR-I05", "DMM in resistance/continuity mode", "two isolated test leads", "instrument model and ratings selection required", "UNPOWERED DOMAINS ONLY", "measurement burden/current may affect electronics", "remove all energy sources; verify discharge; use released method and limits"),
        ("GR-I06", "isolated differential probe candidate", "differential inputs only", "exact product/rating/order code selection required", "POWER OR LOGIC DOMAIN", "must not add an uncontrolled PE bond", "selection, calibration, common-mode and category review required"),
    ]
    return [common({"instrument_case_id": i, "equipment": equipment, "conductive_connection": connection, "manufacturer_or_design_basis": basis, "allowed_connection_domain": domain, "hazard_or_change": hazard, "candidate_rule": rule, "approved": "NO"}) for i, equipment, connection, basis, domain, hazard, rule in data]


def faults() -> list[dict[str, object]]:
    data = [
        ("GR-F01", "tether PE/G conductor open", "robot frame loses intended protective path", "detect before power by end-to-end continuity; connection prohibited"),
        ("GR-F02", "BR1 proposed DC0V/PE bond absent", "DC reference floats relative to frame", "record as configuration fault unless qualified alternate is released"),
        ("GR-F03", "second DC0V/PE bond added by instrument", "parallel return/ground current and ambiguous fault path", "unpowered topology measurement and connection-matrix review must detect it"),
        ("GR-F04", "DC return accidentally routed through frame", "normal current flows in structure/bearings/shields", "branch-return and frame-current checks; quarantine configuration"),
        ("GR-F05", "shield used as PE conductor", "shield/connector may carry protective fault current without rating", "reject; PE path must be independent"),
        ("GR-F06", "articulated joint interrupts frame bond", "distal exposed metal becomes unbonded", "module-by-module continuity with worst-case joint positions"),
        ("GR-F07", "probe ground connected to non-PE potential", "short through oscilloscope protective earth", "prohibited connection; use approved differential/isolated method"),
        ("GR-F08", "USB/debug cable silently adds reference", "bench floating assumption becomes false", "measure each accessory individually and in final combined setup"),
        ("GR-F09", "PE and DC conductors swapped at SBS75G", "touch and fault-current hazard", "contact-map inspection, polarity/continuity checks and independent witness"),
    ]
    return [common({"fault_id": i, "fault": fault, "consequence": consequence, "required_detection_or_response": response, "result": "NOT EXECUTED"}) for i, fault, consequence, response in data]


def measurements() -> list[dict[str, object]]:
    data = [
        ("GR-M01", "facility PE to panel PE bar", "ohm", "SELECTION REQUIRED"),
        ("GR-M02", "panel PE bar to enclosure/source FG/tether G", "ohm", "SELECTION REQUIRED"),
        ("GR-M03", "tether G end-to-end under flex", "ohm", "SELECTION REQUIRED"),
        ("GR-M04", "pelvis hub to every exposed conductive module at worst joint poses", "ohm", "SELECTION REQUIRED"),
        ("GR-M05", "BR1 DC return-to-frame bond resistance and physical location", "ohm", "SELECTION REQUIRED"),
        ("GR-M06", "number of intentional DC return-to-frame bonds", "count", "EXACTLY ONE IF CANDIDATE ARCHITECTURE IS APPROVED"),
        ("GR-M07", "power conductors to frame insulation with BR1 removed", "Mohm", "SELECTION REQUIRED"),
        ("GR-M08", "each external instrument reference to PE/CTRL_GND before connection", "ohm", "SELECTION REQUIRED"),
        ("GR-M09", "frame current during approved current-limited injection", "mA", "SELECTION REQUIRED"),
        ("GR-M10", "bond thermal rise during approved fault-current test", "degC", "SELECTION REQUIRED"),
    ]
    return [common({"measurement_id": i, "measurement": measurement, "unit": unit, "acceptance_limit": limit, "instrument_id": "UNASSIGNED", "measured_value": "NONE", "result": "NOT EXECUTED", "evidence_path": "NONE"}) for i, measurement, unit, limit in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("GR-H01", "jurisdiction, facility supply and enclosure classification not frozen", "site/facility record and qualified electrical disposition"),
        ("GR-H02", "PE conductor, terminal, stud and jumper selections unresolved", "fault current, clearing time, route, flex, corrosion and received-material evidence"),
        ("GR-H03", "single proposed BR1 DC0V/PE bond not approved", "EMC/fault analysis, location drawing, hardware selection and qualified review"),
        ("GR-H04", "all conductive body-part bonding interfaces unresolved", "as-built module list, jumper/interface drawings and worst-pose continuity evidence"),
        ("GR-H05", "shield termination architecture unresolved", "cable construction, connector shells, EMC testing and bonding hardware"),
        ("GR-H06", "USB/SWD/oscilloscope reference paths not physically characterized", "received equipment continuity matrix and approved test setup drawing"),
        ("GR-H07", "bond/insulation acceptance limits and instruments unreleased", "qualified procedure, ratings, calibration and test-current/voltage limits"),
        ("GR-H08", "package is design evidence only", "fabricated harness, inspection, measurements, fault tests and signed separate work release"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="850" viewBox="0 0 1500 850" role="img" aria-labelledby="title desc"><title id="title">HR-30 protective-earth and DC-reference candidate</title><desc id="desc">Protective earth travels from the facility through the external enclosure and first-mate tether contact to a robot frame bond hub. DC return remains separate except for one proposed removable bond at the robot distributor.</desc><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10z" fill="#0b4f91"/></marker></defs><style>text{{font:600 19px system-ui;fill:#102b46}}.h{{font-size:31px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.pe{{stroke:#16804a;stroke-width:11;fill:none}}.dc{{stroke:#17243a;stroke-width:9;fill:none}}.bond{{stroke:#f2b91d;stroke-width:9;stroke-dasharray:16 10}}.hold{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1500" height="850" fill="#eef8ff"/><text class="h" x="45" y="55">Whole-robot PE / DC-reference candidate — nothing is built or approved</text><rect class="box" x="45" y="115" width="280" height="220" rx="18"/><text x="75" y="160">Facility PE</text><text class="s" x="75" y="195">site + branch assumptions open</text><rect class="box" x="410" y="100" width="340" height="260" rx="18"/><text x="445" y="145">External panel PE bar</text><text class="s" x="445" y="182">enclosure bond</text><text class="s" x="445" y="212">RSP-500-12 FG</text><text class="s" x="445" y="242">SD-15A-24 FG</text><text class="s" x="445" y="272">XT1A SBS75G G</text><path class="pe" d="M325 230H410"/><rect class="box" x="850" y="100" width="300" height="260" rx="18"/><text x="885" y="145">Pelvis frame-bond hub</text><text class="s" x="885" y="182">via XT1B SBS75G G</text><text class="s" x="885" y="220">jumpers to every conductive</text><text class="s" x="885" y="250">whole-body module</text><path class="pe" d="M750 230H850"/><rect class="box" x="1225" y="100" width="230" height="260" rx="18"/><text x="1260" y="145">Robot frame</text><text class="s" x="1260" y="185">head + torso</text><text class="s" x="1260" y="215">arms + pelvis</text><text class="s" x="1260" y="245">legs + feet</text><path class="pe" d="M1150 230H1225"/><rect class="box" x="410" y="470" width="340" height="170" rx="18"/><text x="445" y="515">RSP +12 V / DC return</text><text class="s" x="445" y="552">power pair through tether P1/P2</text><text class="s" x="445" y="584">frame is not a normal-current path</text><rect class="box" x="850" y="470" width="300" height="170" rx="18"/><text x="885" y="515">Robot return bus RB0</text><text class="s" x="885" y="552">actuator return + CTRL_GND</text><text class="s" x="885" y="584">reference topology still open</text><path class="dc" d="M750 555H850"/><path class="bond" d="M1000 470V360"/><text x="1025" y="425">BR1</text><text class="s" x="1025" y="450">sole proposed bond</text><rect class="hold" x="45" y="705" width="1410" height="100" rx="18"/><text x="80" y="747">USB, SWD and oscilloscope grounds can create a second bond. Connection matrix review is mandatory.</text><text class="s" x="80" y="780">Conductor sizes, terminals, limits, enclosure/jurisdiction assumptions, physical tests and qualified approval remain open.</text></svg>'''


def page(domain_rows: list[dict[str, object]], bond_rows: list[dict[str, object]], instrument_rows: list[dict[str, object]], hold_rows: list[dict[str, object]]) -> str:
    domain_cards = "".join(f'<article><b>{html.escape(str(r["domain_id"]))}</b><h3>{html.escape(str(r["net_or_domain"]))}</h3><p>{html.escape(str(r["rule"]))}</p></article>' for r in domain_rows)
    instrument_cards = "".join(f'<article><b>{html.escape(str(r["instrument_case_id"]))}</b><h3>{html.escape(str(r["equipment"]))}</h3><p>{html.escape(str(r["hazard_or_change"]))}</p><strong>NOT APPROVED</strong></article>' for r in instrument_rows)
    holds_html = "".join(f'<li><b>{html.escape(str(r["hold_id"]))}</b> {html.escape(str(r["unresolved_item"]))}</li>' for r in hold_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 grounding and reference architecture</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article strong{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:980px}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>One grounding drawing for the whole humanoid.</h1><p>The candidate keeps protective earth continuous, keeps normal DC return off the frame, and proposes exactly one removable DC-return/PE bond. It is a design for review—not permission to connect anything.</p></header><main><section class="grid"><article><div class="metric">{len(domain_rows)}</div><p>controlled electrical domains</p></article><article><div class="metric">{len(bond_rows)}</div><p>candidate bond records</p></article><article><div class="metric">{len(instrument_rows)}</div><p>instrument connection cases</p></article><article><div class="metric">0</div><p>installed or measured bonds</p></article></section><section><h2>Candidate topology</h2><div class="scroll"><object data="grounding-reference-topology.svg" type="image/svg+xml" aria-label="Protective-earth and DC-reference topology"></object></div></section><section><h2>What each conductor is allowed to do</h2><div class="grid">{domain_cards}</div></section><section><h2>Grounded equipment can change the circuit</h2><div class="grid">{instrument_cards}</div></section><section class="panel"><h2>Controlled engineering records</h2><p><a href="bond-register.csv">Bond register</a> · <a href="instrument-connection-matrix.csv">Instrument matrix</a> · <a href="fault-case-register.csv">Fault cases</a> · <a href="measurement-traveler.csv">Blank measurement traveler</a> · <a href="primary-source-register.csv">Primary sources</a></p></section><section class="panel"><h2>Open holds</h2><ul>{holds_html}</ul></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(domain_count: int, bond_count: int, instrument_count: int) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "grounding_reference_architecture_present": True,
        "grounding_reference_domain_count": domain_count,
        "grounding_candidate_bond_count": bond_count,
        "grounding_instrument_case_count": instrument_count,
        "single_dc_return_pe_bond_candidate_defined": True,
        "pe_dc_reference_architecture_approved": False,
        "grounding_physical_measurements_executed": 0,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-GROUNDING-REFERENCE-P01-README-START -->", "<!-- HR30-GROUNDING-REFERENCE-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Whole-robot grounding and DC-reference architecture\n\nThe [interactive grounding guide](electrical/grounding-reference-architecture-p0.1/index.html) consolidates facility PE, the external panel, the SBS75G first-mate tether contact, every conductive robot module, DC return, control ground, shields and grounded test equipment into one candidate topology. It proposes one removable BR1 DC-return/PE bond at RB0 and **{bond_count} controlled bond records**. Conductor hardware, limits, measurements, jurisdiction and qualified approval remain open; it grants no work authority.\n{end}\n'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    root_page = WHOLE / "index.html"
    text = root_page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-GROUNDING-REFERENCE-P01-START -->", "<!-- HR30-GROUNDING-REFERENCE-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="grounding-reference"><h2>The whole robot now has one candidate PE/reference drawing</h2><div class="grid"><article class="card"><div class="metric">{domain_count}</div><p>controlled grounding/reference domains</p></article><article class="card"><div class="metric">{bond_count}</div><p>candidate bond records</p></article><article class="card hold"><div class="metric">0</div><p>installed or measured bonds</p></article></div><p><a href="electrical/grounding-reference-architecture-p0.1/index.html">Open the interactive grounding/reference guide</a>. The topology is explicit; approval and every physical result remain open.</p></section>{end}'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>", 1)
    root_page.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_rows, binding_rows = sources(), bindings()
    domain_rows, bond_rows = domains(), bonds()
    instrument_rows, fault_rows = instruments(), faults()
    measurement_rows, hold_rows = measurements(), holds()
    write_csv(OUT / "primary-source-register.csv", source_rows)
    write_csv(OUT / "source-binding.csv", binding_rows)
    write_csv(OUT / "reference-domain-register.csv", domain_rows)
    write_csv(OUT / "bond-register.csv", bond_rows)
    write_csv(OUT / "instrument-connection-matrix.csv", instrument_rows)
    write_csv(OUT / "fault-case-register.csv", fault_rows)
    write_csv(OUT / "measurement-traveler.csv", measurement_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "primary_source_count": len(source_rows), "source_binding_count": len(binding_rows),
        "reference_domain_count": len(domain_rows), "candidate_bond_count": len(bond_rows),
        "instrument_connection_case_count": len(instrument_rows), "fault_case_count": len(fault_rows),
        "measurement_count": len(measurement_rows), "open_hold_count": len(hold_rows),
        "protective_earth_path_candidate_defined": True,
        "normal_dc_return_through_frame_permitted": False,
        "single_removable_dc_return_pe_bond_candidate_defined": True,
        "shield_is_protective_earth": False,
        "architecture_approved": False, "bond_hardware_selected": False,
        "physical_measurements_executed": 0, "qualified_review_complete": False,
        "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "grounding-reference-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "grounding-reference-topology.svg").write_text(svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(domain_rows, bond_rows, instrument_rows, hold_rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 grounding and DC-reference architecture P0.1\n\n**{WARNING}**\n\nThis package defines one reviewable whole-robot PE, frame-bond, DC-return, control-reference, shield and instrument topology. It records no installation, measurement or authority. Use [index.html](index.html) for the interactive guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "grounding-reference-source.py")
    manifest = [common({"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}) for path in sorted(OUT.rglob("*")) if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(len(domain_rows), len(bond_rows), len(instrument_rows))
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
