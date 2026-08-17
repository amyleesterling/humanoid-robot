#!/usr/bin/env python3
"""Generate the HR-30 actuator-cable coupon and route-measurement package.

This is a controlled physical-development package, not a released harness.
It deliberately separates test-specimen lengths from final robot cut lengths.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-coupon-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-ACTUATOR-CABLE-COUPON-P0.1"
WARNING = "PRELIMINARY - UNBUILT CABLE COUPON PLAN - NOT APPROVED FOR PROCUREMENT, PRODUCTION CUTTING, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, PRODUCTION-CUTTING, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


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
        ("ACC-S01", "Project Button", "25-axis cable candidate register", "harness/actuator-cable-kit-p0.1/axis-power-cable-candidate.csv", "candidate cable, current caps and geometric planning lengths"),
        ("ACC-S02", "Project Button", "25-axis moving-loop obligations", "harness/physical-p0.1/service-loop-register.csv", "joint axes, ranges and unresolved loop requirements"),
        ("ACC-S03", "Project Button", "whole-body route segments", "harness/physical-p0.1/route-segment-register.csv", "fixed corridors and moving-loop planning geometry"),
        ("ACC-S04", "Project Button", "actuator connector cavity population", "harness/actuator-cable-kit-p0.1/connector-cavity-population.csv", "contact population and controlled empty cavities"),
    ]
    rows: list[dict[str, object]] = []
    for sid, publisher, document, rel, scope in local:
        path = WHOLE / rel
        rows.append(controlled({"source_id": sid, "publisher": publisher, "document": document, "revision_or_date": "current generated P0.1 input", "official_url_or_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "verified_scope": scope}))
    official = [
        ("ACC-S05", "JST", "EH connector product page", "live page; accessed 2026-08-16", "https://www.jst-mfg.com/product/index.php?lang=2&series=58", "AWG32-22 / 0.032-0.33 mm2; 3 A headline applies at AWG22; insulation OD 0.5-1.9 mm"),
        ("ACC-S06", "JST", "EH connector data sheet", "current official PDF; accessed 2026-08-16", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "SEH-001T-P0.6 AWG30-22 / 0.05-0.33 mm2; insulation OD 1.0-1.9 mm; AP-K2N/MKS-L/APLMK SEH001-06 production path"),
        ("ACC-S07", "JST", "Crimping machines and tools", "current official PDF; accessed 2026-08-16", "https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf", "YRS-260 strip-terminal tool; YC-260R loose-piece tool; BEH-001T-P0.6 loose terminal; EJ-PH extraction tool"),
        ("ACC-S08", "igus", "chainflex CF9.UL product page", "live page; accessed 2026-08-16", "https://www.igus.com/product/CF9_UL", "CF9.UL.02.02 is 2 x 0.25 mm2 / 24 AWG TPE continuous-flex/torsion candidate"),
        ("ACC-S09", "igus", "chainflex CF9.UL data sheet", "current official PDF; accessed 2026-08-16; visible footer 2014", "https://www.igus.com/contentData/Product_Files/Download/pdf/CF9-UL_en.pdf", "construction and published 5xd normal-temperature minimum bend radius; route-specific validation still required"),
    ]
    for item in official:
        sid, publisher, document, revision, url, scope = item
        rows.append(controlled({"source_id": sid, "publisher": publisher, "document": document, "revision_or_date": revision, "official_url_or_path": url, "sha256": "NOT APPLICABLE - EXTERNAL PRIMARY SOURCE", "verified_scope": scope}))
    return rows


def tooling() -> list[dict[str, object]]:
    data = [
        ("ACC-T01", "prototype loose-piece crimp", "JST YC-260R", "JST BEH-001T-P0.6", "preferred coupon path", "candidate only; CF9 TPE insulation and exact crimp settings are not qualified by the cited JST table"),
        ("ACC-T02", "strip-terminal hand crimp", "JST YRS-260", "JST SEH-001T-P0.6", "production-development alternative", "candidate only; strip supply and CF9-specific crimp validation required"),
        ("ACC-T03", "production applicator", "JST AP-K2N + MKS-L + APLMK SEH001-06", "JST SEH-001T-P0.6", "contract harness-maker alternative", "candidate only; machine setup, applicator condition and sample approval required"),
        ("ACC-T04", "contact extraction", "JST EJ-PH", "EHR housing / EH contact", "inspection and rework candidate", "extraction damage limits and reuse rule require an approved process"),
    ]
    return [controlled({"tool_id": i, "operation": op, "candidate_tool": tool, "terminal_or_interface": terminal, "intended_role": role, "release_boundary": boundary, "selection_state": "CANDIDATE - NOT SELECTED"}) for i, op, tool, terminal, role, boundary in data]


def bom() -> list[dict[str, object]]:
    data = [
        ("ACC-B01", "igus", "CF9.UL.02.02", "2 x 0.25 mm2 / 24 AWG cable", "10 m evaluation quantity or supplier-cut sample", "quote, current availability, lot/CoC and received construction required"),
        ("ACC-B02", "JST", "BEH-001T-P0.6", "loose-piece EH contact", "50 evaluation pieces", "supplier quote and confirmation of genuine current material required"),
        ("ACC-B03", "JST", "YC-260R", "loose-piece hand crimp tool", "1", "availability, serial/condition and calibration/inspection basis required"),
        ("ACC-B04", "JST", "EHR-3", "3-position EH housing", "10 evaluation pieces", "received lot and dimensional/fit inspection required"),
        ("ACC-B05", "JST", "EHR-4", "4-position EH housing", "10 evaluation pieces", "received lot and dimensional/fit inspection required"),
        ("ACC-B06", "JST", "EJ-PH", "EH extraction tool", "1", "availability and damage-free extraction trial required"),
        ("ACC-B07", "JST", "YRS-260 + SEH-001T-P0.6", "strip-terminal alternative", "quote only", "do not buy both crimp paths before process-owner disposition"),
    ]
    return [controlled({"item_id": i, "manufacturer": maker, "order_code": code, "description": desc, "planning_quantity": qty, "procurement_hold": hold, "selection_state": "QUOTE / SAMPLE CANDIDATE ONLY"}) for i, maker, code, desc, qty, hold in data]


def specimens() -> list[dict[str, object]]:
    data = [
        ("ACC-C01", "crimp setup and sectioning", 300, 10, "two terminated conductors per specimen; reserve failed setup pieces", "strip length, conductor crimp, insulation support, section and visual criteria require process owner"),
        ("ACC-C02", "pull/retention development", 300, 10, "terminated lead in controlled pull fixture", "speed, minimum force and failure mode require qualified standard/process selection"),
        ("ACC-C03", "continuity and four-wire resistance", 1000, 3, "terminated cable pair", "baseline and post-test resistance limits require instrument uncertainty and temperature correction"),
        ("ACC-C04", "current/temperature-rise characterization", 1000, 3, "terminated cable pair in representative free-air and bundled fixtures", "current steps, steady-state criterion and maximum temperature require duty/ambient allocation"),
        ("ACC-C05", "repeated-bend coupon", 500, 3, "cable-only then terminated assembly", "mandrel, travel, cycles and termination restraint require route measurement"),
        ("ACC-C06", "torsion coupon", 1000, 3, "cable-only active gauge length", "published +/-90 deg/m is a manufacturer boundary, not the robot acceptance limit"),
        ("ACC-C07", "housing insertion/extraction", 300, 6, "terminated lead in EHR-3/EHR-4", "contact retention, extraction damage and reuse acceptance require process definition"),
    ]
    return [controlled({"specimen_id": i, "purpose": purpose, "specimen_length_mm": length, "planned_quantity": qty, "construction": construction, "acceptance_boundary": boundary, "is_production_cut_length": "NO", "built_quantity": 0, "tested_quantity": 0}) for i, purpose, length, qty, construction, boundary in data]


def traveler() -> list[dict[str, object]]:
    actions = [
        ("ACC-W01", "record supplier, order code, lot, CoC and received quantities", "incoming record complete"),
        ("ACC-W02", "measure conductor and jacket construction including individual insulation OD", "measured values recorded; no published-range assumption"),
        ("ACC-W03", "record tool model, serial, condition, calibration/inspection status and die station", "tool traceability complete"),
        ("ACC-W04", "run strip-length trials and inspect for cut strands or insulation damage", "approved strip setting selected by process owner"),
        ("ACC-W05", "crimp setup samples; record every tool setting and sample ID", "repeatable setup evidence attached"),
        ("ACC-W06", "perform visual and destructive section inspection", "approved conductor/insulation-crimp criteria recorded"),
        ("ACC-W07", "perform pull/retention trials at approved speed", "approved minimum and failure-mode criteria met"),
        ("ACC-W08", "insert contacts into EHR-3 and EHR-4; verify cavity, latch and retention", "no back-out or housing damage"),
        ("ACC-W09", "extract with EJ-PH and inspect contact/housing", "reuse/scrap rule disposition recorded"),
        ("ACC-W10", "measure continuity, polarity and four-wire resistance before environmental tests", "baseline and uncertainty recorded"),
        ("ACC-W11", "execute free-air and representative-bundle current/temperature-rise test", "duty-derived current/temperature criteria met"),
        ("ACC-W12", "execute bend and torsion cycling with representative termination restraint", "route-derived cycles and post-test checks met"),
        ("ACC-W13", "repeat continuity, resistance, visual, retention and insulation checks", "no unacceptable change or damage"),
        ("ACC-W14", "qualified harness reviewer issues candidate disposition", "signed disposition references exact lots/tools/settings/results"),
    ]
    return [controlled({"step_id": i, "action": action, "completion_evidence": evidence, "recorded_value": "NONE", "performed_by": "UNASSIGNED", "witness": "UNASSIGNED", "result": "NOT EXECUTED"}) for i, action, evidence in actions]


def measurements() -> list[dict[str, object]]:
    names = [
        ("ACC-M01", "individual conductor insulation OD", "mm"), ("ACC-M02", "jacket OD", "mm"),
        ("ACC-M03", "strip length", "mm"), ("ACC-M04", "conductor crimp height", "mm"),
        ("ACC-M05", "insulation support height", "mm"), ("ACC-M06", "pull force", "N"),
        ("ACC-M07", "initial four-wire loop resistance at recorded temperature", "ohm"),
        ("ACC-M08", "steady-state conductor/contact temperature rise", "degC"),
        ("ACC-M09", "post-flex resistance change", "%"), ("ACC-M10", "contact retention force", "N"),
    ]
    return [controlled({"measurement_id": i, "measurement": name, "unit": unit, "acceptance_limit": "SELECTION REQUIRED - QUALIFIED PROCESS / TEST PLAN", "instrument_id": "UNASSIGNED", "measured_value": "NONE", "result": "NOT EXECUTED"}) for i, name, unit in names]


def precut_routes() -> list[dict[str, object]]:
    axes = read_csv(WHOLE / "harness/actuator-cable-kit-p0.1/axis-power-cable-candidate.csv")
    loops = {r["axis_id"]: r for r in read_csv(WHOLE / "harness/physical-p0.1/service-loop-register.csv")}
    rows = []
    for axis in axes:
        loop = loops[axis["axis_id"]]
        rows.append(controlled({
            "axis_id": axis["axis_id"], "bus_id": axis["bus_id"], "destination_connector": axis["destination_connector"],
            "geometric_one_way_planning_length_mm": axis["one_way_planning_length_mm"], "planning_length_basis": "straight-point geometry plus generator allowance; not routed as-built measurement",
            "joint_axis_xyz_mm": loop["joint_axis_xyz_mm"], "commanded_range": loop["commanded_range"],
            "mockup_pull_string_length_mm": "MEASURE ON ASSEMBLED ROBOT", "service_slack_mm": "SELECTION REQUIRED AFTER FULL JOINT SWEEP",
            "connector_termination_allowance_mm": "SELECTION REQUIRED FROM APPROVED CRIMP/ASSEMBLY PROCESS", "final_cut_length_mm": "SELECTION REQUIRED - MEASURE ON ASSEMBLED ROBOT",
            "clamp_and_strain_relief_locations": "SELECTION REQUIRED AFTER CAD/PHYSICAL SWEEP", "minimum_bend_radius": "SELECTION REQUIRED - APPLY RECEIVED CABLE OD AND ROUTE CONDITIONS",
            "precut_action": "DO NOT CUT PRODUCTION CABLE", "route_measurement_state": "NOT EXECUTED",
        }))
    return rows


def holds() -> list[dict[str, object]]:
    data = [
        ("ACC-H01", "received CF9 individual-conductor insulation OD not verified against the SEH-001T-P0.6 1.0-1.9 mm range", "supplier drawing or received measurement"),
        ("ACC-H02", "JST hand-tool examples do not qualify the exact CF9 TPE insulation/conductor construction", "JST/process-owner disposition plus destructive coupons"),
        ("ACC-H03", "strip length, crimp heights and pull-force acceptance are unresolved", "qualified crimp specification and calibrated measurement plan"),
        ("ACC-H04", "genuine current parts/tools and lot traceability are unconfirmed", "supplier quote, order acknowledgement, CoC and incoming inspection"),
        ("ACC-H05", "AWG24 current capacity, contact temperature rise and bundle derating are unverified", "duty-derived thermal test with representative bundling/ambient"),
        ("ACC-H06", "bend/torsion/cycle life and termination restraint are unverified", "route-specific cycling with post-test electrical/mechanical inspection"),
        ("ACC-H07", "all 25 production cut lengths, slack and clamp locations are unmeasured", "assembled robot pull-string measurements through full joint sweeps"),
        ("ACC-H08", "branch protection and regeneration/fault behavior remain unselected", "measured duty/fault/inrush/regeneration plus coordinated protection design"),
        ("ACC-H09", "no physical coupon has been built or tested", "completed traveler and traceable raw measurements"),
        ("ACC-H10", "qualified harness disposition absent", "signed review of exact received materials, tooling, process and results"),
    ]
    return [controlled({"hold_id": i, "unresolved_item": item, "evidence_required": evidence, "state": "OPEN"}) for i, item, evidence in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="720" viewBox="0 0 1440 720" role="img" aria-labelledby="t d"><title id="t">HR-30 actuator cable coupon workflow</title><desc id="d">Official candidate materials and tooling feed coupon construction and tests before any whole-robot cut length is allowed.</desc><rect width="1440" height="720" fill="#f7fbff"/><rect x="30" y="24" width="1380" height="94" rx="14" fill="#f2b91d" stroke="#805600" stroke-width="3"/><g font-family="system-ui" font-size="21" font-weight="800" fill="#17243a"><text x="60" y="64">PRELIMINARY - UNBUILT CABLE COUPON PLAN - NO PROCUREMENT, PRODUCTION CUTTING OR FABRICATION</text><text x="60" y="96">NO CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION AUTHORITY</text></g><g font-family="system-ui" fill="#142a40"><text x="60" y="170" font-size="34" font-weight="900">Candidate materials</text><rect x="60" y="200" width="350" height="180" rx="18" fill="#d9f2ff" stroke="#0b4f91" stroke-width="3"/><text x="85" y="245" font-size="22" font-weight="800">CF9.UL.02.02</text><text x="85" y="282" font-size="18">2 x 0.25 mm2 / 24 AWG</text><text x="85" y="315" font-size="18">BEH-001T-P0.6 + EHR-3/4</text><text x="85" y="348" font-size="18">YC-260R + EJ-PH</text><text x="545" y="170" font-size="34" font-weight="900">Coupon evidence</text><rect x="500" y="200" width="420" height="180" rx="18" fill="#fff" stroke="#0b4f91" stroke-width="3"/><text x="530" y="245" font-size="18">strip + crimp section</text><text x="530" y="278" font-size="18">pull + retention</text><text x="530" y="311" font-size="18">resistance + temperature</text><text x="530" y="344" font-size="18">bend + torsion cycling</text><text x="1050" y="170" font-size="34" font-weight="900">Robot routing</text><rect x="1010" y="200" width="370" height="180" rx="18" fill="#fff" stroke="#982520" stroke-width="3"/><text x="1040" y="245" font-size="18">25 pull-string measurements</text><text x="1040" y="278" font-size="18">full joint sweeps</text><text x="1040" y="311" font-size="18">slack + clamps + bend radius</text><text x="1040" y="350" font-size="20" font-weight="900" fill="#982520">DO NOT CUT PRODUCTION CABLE</text><path d="M410 290 H500" stroke="#0b4f91" stroke-width="7" marker-end="url(#a)"/><path d="M920 290 H1010" stroke="#0b4f91" stroke-width="7" marker-end="url(#a)"/><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#0b4f91"/></marker></defs><rect x="170" y="470" width="1100" height="150" rx="18" fill="#071d36"/><text x="720" y="514" text-anchor="middle" font-size="23" fill="#fff" font-weight="800">Promotion requires received-lot coupons + qualified disposition</text><text x="720" y="548" text-anchor="middle" font-size="23" fill="#fff" font-weight="800">plus measured robot routes</text><text x="720" y="582" text-anchor="middle" font-size="21" fill="#fff">0 coupons built  |  0 tests executed  |  0 final cut lengths released</text><text x="720" y="610" text-anchor="middle" font-size="18" fill="#f2b91d">No connection, powered test, motion, or energization authority</text></g></svg>'''


def render(routes: list[dict[str, object]]) -> str:
    route_rows = "".join(f"<tr><td>{html.escape(str(r['axis_id']))}</td><td>{r['geometric_one_way_planning_length_mm']} mm</td><td>{html.escape(str(r['commanded_range']))}</td><td>{r['final_cut_length_mm']}</td><td>{r['precut_action']}</td></tr>" for r in routes)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator cable coupon</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:17ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>Build and break coupons before cutting robot cables.</h1><p>The candidate parts and tools are now explicit. Their exact combination is not qualified, so the package defines the evidence needed to earn a production process.</p></header><main><section class="grid"><article><div class="metric">4</div><p>candidate tooling paths and operations</p></article><article><div class="metric">7</div><p>controlled coupon specimen families</p></article><article><div class="metric">25</div><p>axis routes requiring as-built measurement</p></article><article class="hold"><div class="metric">0</div><p>built coupons, executed tests, or released cut lengths</p></article></section><section><h2>Evidence flow</h2><img src="coupon-architecture.svg" alt="Cable coupon validation and robot route measurement workflow"></section><section><h2>Prototype tooling path</h2><div class="panel"><p><strong>Loose-piece trial:</strong> JST <strong>BEH-001T-P0.6</strong> contact, <strong>YC-260R</strong> hand tool, EHR-3/EHR-4 housings and <strong>EJ-PH</strong> extraction tool. The alternative strip path is SEH-001T-P0.6 + YRS-260. These are manufacturer-linked candidates—not a released process for CF9's TPE construction.</p></div></section><section><h2>Production lengths remain deliberately blank</h2><div class="panel hold"><p>The existing geometry values are planning lengths, not cable cut lengths. Each axis must be measured on the assembled robot with pull string through its complete joint range. Connector termination allowance, service slack, clamps, bend radius and collision clearance must then be frozen.</p></div><div class="scroll"><table><thead><tr><th>Axis</th><th>Geometry planning length</th><th>Commanded range</th><th>Final cut length</th><th>Action</th></tr></thead><tbody>{route_rows}</tbody></table></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="tooling-candidate-register.csv">Tooling</a> | <a href="coupon-bom.csv">Coupon BOM</a> | <a href="coupon-specimen-register.csv">Specimens</a> | <a href="coupon-build-traveler.csv">Build traveler</a> | <a href="coupon-measurement-record.csv">Measurements</a> | <a href="precut-route-register.csv">25 route measurements</a> | <a href="open-holds.csv">Open holds</a> | <a href="primary-source-register.csv">Primary sources</a></p><small>No acceptance limit has been invented. Unresolved values are explicitly SELECTION REQUIRED.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(routes: list[dict[str, object]]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "actuator_cable_coupon_package_present": True, "actuator_cable_coupon_tooling_candidate_count": 4,
        "actuator_cable_coupon_specimen_family_count": 7, "actuator_cable_coupon_route_measurement_count": len(routes),
        "actuator_cable_coupon_built_count": 0, "actuator_cable_coupon_executed_test_count": 0,
        "actuator_cable_coupon_process_selected": False, "actuator_cable_final_cut_lengths_selected": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-COUPON-P01-README-START -->", "<!-- HR30-ACTUATOR-CABLE-COUPON-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Actuator cable coupon and route measurement\n\nThe [interactive coupon guide](harness/actuator-cable-coupon-p0.1/index.html) binds the JST loose-piece **BEH-001T-P0.6 + YC-260R** prototype path, the strip-terminal **SEH-001T-P0.6 + YRS-260** alternative, seven destructive/measurement specimen families, and a **25-axis** as-built route register. No production cut length or crimp setting is released: every robot cable must be measured after assembly and swept through its complete joint range.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    if marker not in text:
        raise RuntimeError("README integration marker missing")
    readme.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-COUPON-P01-START -->", "<!-- HR30-ACTUATOR-CABLE-COUPON-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="actuator-cable-coupon"><h2>The cable process now has a physical coupon path</h2><div class="grid"><article class="card pass"><div class="metric">4</div><p>manufacturer-linked candidate tooling operations.</p></article><article class="card pass"><div class="metric">7</div><p>coupon specimen families from crimp sections through torsion.</p></article><article class="card"><div class="metric">25</div><p>axis routes awaiting measured pull-string cut lengths.</p></article><article class="card hold"><div class="metric">0</div><p>built coupons, executed tests or production cut lengths.</p></article></div><p><a href="harness/actuator-cable-coupon-p0.1/index.html">Open the interactive coupon and route-measurement guide</a>. Do not cut production cable from the geometric planning values.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    if marker not in text:
        raise RuntimeError("web integration marker missing")
    page.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_rows, tool_rows, bom_rows = sources(), tooling(), bom()
    specimen_rows, traveler_rows, measurement_rows = specimens(), traveler(), measurements()
    route_rows, hold_rows = precut_routes(), holds()
    write_csv(OUT / "primary-source-register.csv", source_rows)
    write_csv(OUT / "tooling-candidate-register.csv", tool_rows)
    write_csv(OUT / "coupon-bom.csv", bom_rows)
    write_csv(OUT / "coupon-specimen-register.csv", specimen_rows)
    write_csv(OUT / "coupon-build-traveler.csv", traveler_rows)
    write_csv(OUT / "coupon-measurement-record.csv", measurement_rows)
    write_csv(OUT / "precut-route-register.csv", route_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "source_count": len(source_rows), "tooling_candidate_count": len(tool_rows),
        "bom_item_count": len(bom_rows), "specimen_family_count": len(specimen_rows), "traveler_step_count": len(traveler_rows),
        "measurement_record_count": len(measurement_rows), "route_measurement_count": len(route_rows), "open_hold_count": len(hold_rows),
        "loose_piece_tooling_path_bound": True, "strip_terminal_tooling_path_bound": True,
        "cf9_specific_crimp_process_selected": False, "built_coupon_count": 0, "executed_test_count": 0,
        "measured_robot_route_count": 0, "released_final_cut_length_count": 0,
        "procurement_authority": False, "production_cutting_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "coupon-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 actuator cable coupon P0.1\n\n**{WARNING}**\n\nThis package converts the cable candidate into a controlled coupon-build and route-measurement workflow. It records zero physical execution and releases no production cable.\n", encoding="utf-8", newline="\n")
    (OUT / "coupon-architecture.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(route_rows), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "actuator-cable-coupon-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(route_rows)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
