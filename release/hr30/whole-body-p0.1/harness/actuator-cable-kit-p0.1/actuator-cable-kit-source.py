#!/usr/bin/env python3
"""Generate the HR-30 actuator cable-kit engineering candidate.

This package turns the verified ROBOTIS/JST device interface and the existing
25-axis physical/current-policy datasets into explicit incoming and outgoing
connector cavity records.  Cable families remain test-coupon candidates where
manufacturer compatibility, bus behavior, or flex behavior is unresolved.
Nothing generated here releases procurement, fabrication, connection or power.
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
PHYSICAL = WHOLE / "harness" / "physical-p0.1"
POLICY = WHOLE / "harness" / "current-policy-binding-p0.1"
OUT = WHOLE / "harness" / "actuator-cable-kit-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-ACTUATOR-CABLE-KIT-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - UNBUILT ACTUATOR CABLE-KIT CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


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


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def source_rows() -> list[dict[str, object]]:
    local = [
        ("ACK-S01", POLICY / "axis-power-policy-binding.csv", "25-axis current-cap and routed-length binding"),
        ("ACK-S02", PHYSICAL / "bus-physical-link-register.csv", "25 physical bus links and outgoing-link topology"),
        ("ACK-S03", PHYSICAL / "actuator-interface-verification-register.csv", "manufacturer actuator interface verification"),
        ("ACK-S04", PHYSICAL / "manufacturer-interface-discrepancy-register.csv", "existing interface discrepancy register"),
    ]
    rows = []
    for ident, path, role in local:
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(common({"source_id": ident, "publisher": "Project Button", "document": role, "revision_or_date": "current generated P0.1 input", "official_url_or_path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "verified_scope": role}))
    official = [
        ("ACK-S05", "JST", "EH connector series product page", "live official page; accessed 2026-08-16", "https://www.jst-mfg.com/product/index.php?lang=2&series=58", "2.5 mm pitch; 3 A at AWG22; AWG32-22 / 0.032-0.33 mm2; EHR-3 and EHR-4 housings"),
        ("ACK-S06", "JST", "EH connector series data sheet", "current official PDF; accessed 2026-08-16", "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf", "SEH-001T-P0.6 standard contact; AWG30-22; low-insertion-force contacts less vibration resistant"),
        ("ACK-S07", "ROBOTIS", "DYNAMIXEL X-series and U2D2 interface documentation", "live official documentation; accessed 2026-08-16", "https://docs.robotis.com/docs/parts/interface/u2d2/", "RS-485 pin 1 GND/2 VDD/3 D+/4 D-; TTL pin 1 GND/2 VDD/3 DATA; EHR-04/EHR-03 notation"),
        ("ACK-S08", "igus", "chainflex CF130-UL product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CF130_UL", "CF130.03.02.UL is 2 x 22 AWG / 0.34 mm2, PVC, medium duty, class 4.4.1.2; bend-life table published"),
        ("ACK-S09", "igus", "chainflex CF240 product page", "live official page; accessed 2026-08-16", "https://www.igus.com/product/CF240", "CF240.01.03 is shielded 3 x 26 AWG / 0.14 mm2, PVC, medium duty, class 4.4.2.1; twist/controlled impedance not established on page"),
    ]
    rows.extend(common({"source_id": i, "publisher": p, "document": d, "revision_or_date": rev, "official_url_or_path": url, "sha256": "N/A - LIVE PRIMARY SOURCE", "verified_scope": scope}) for i, p, d, rev, url, scope in official)
    return rows


def connector_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-C01", "RS-485 actuator input", "JST EHR-4", "JST SEH-001T-P0.6", "JST B4B-EH-A device header", "4", "CANONICAL CANDIDATE ORDER CODES BOUND; RECEIVED FIT/KEYING/RETENTION AND CRIMP VALIDATION OPEN"),
        ("ACK-C02", "TTL actuator input", "JST EHR-3", "JST SEH-001T-P0.6", "JST B3B-EH-A device header", "3", "CANONICAL CANDIDATE ORDER CODES BOUND; RECEIVED FIT/KEYING/RETENTION AND CRIMP VALIDATION OPEN"),
        ("ACK-C03", "contact style", "standard insertion-force contact", "JST SEH-001T-P0.6", "EHR-3/EHR-4", "N/A", "CANDIDATE - LOW-INSERTION-FORCE L-CONTACTS REJECTED FOR WALKING-VIBRATION APPLICATION"),
        ("ACK-C04", "ROBOTIS EHR-03/EHR-04 notation", "JST canonical EHR-3/EHR-4", "JST SEH-001T-P0.6", "ROBOTIS device headers", "3/4", "NOMENCLATURE RECONCILED AT CANDIDATE ORDER-CODE LEVEL; RECEIVED MATING INSPECTION OPEN"),
    ]
    return [common({"decision_id": i, "interface": interface, "candidate_housing": housing, "candidate_contact": contact, "mating_boundary": mate, "positions": positions, "disposition": disposition, "procurement_released": "NO"}) for i, interface, housing, contact, mate, positions, disposition in data]


def axis_rows() -> list[dict[str, object]]:
    policy = read_csv(POLICY / "axis-power-policy-binding.csv")
    if len(policy) != 25:
        raise RuntimeError("25-axis policy input required")
    rows = []
    for source in policy:
        cap = float(source["candidate_internal_limit_a"])
        stall = float(source["published_stall_endpoint_a"])
        if cap > 2.499010 + 1e-9:
            raise RuntimeError(f"unexpected current-cap drift: {source['axis_id']}")
        rows.append(common({
            "axis_id": source["axis_id"], "bus_id": source["bus_id"], "actuator_model": source["actuator_model"],
            "destination_connector": source["destination_connector"], "positive_net": source["positive_net"], "return_net": source["return_net"],
            "candidate_internal_limit_a": f"{cap:.6f}", "published_stall_endpoint_a": f"{stall:.3f}",
            "stall_is_normal_demand": "NO", "one_way_planning_length_mm": source["one_way_planning_length_mm"],
            "round_trip_planning_length_mm": source["round_trip_planning_length_mm"],
            "power_pair_test_coupon_candidate": "igus CF130.03.02.UL; 2 x 22 AWG / 0.34 mm2",
            "jst_eh_published_conductor_range": "AWG30-22; maximum 0.33 mm2 for SEH-001T-P0.6",
            "wire_contact_compatibility": "OPEN - 0.34 mm2 CABLE NOMINAL EXCEEDS JST 0.33 mm2 PUBLISHED MAXIMUM BY 0.01 mm2",
            "voltage_drop": "NOT CALCULATED - EXACT ACCEPTED CABLE RESISTANCE/TEMPERATURE/RMS DUTY OPEN",
            "branch_protection": "SELECTION REQUIRED", "cut_length_and_service_slack": "SELECTION REQUIRED",
            "selection_state": "CURRENT CAP BOUND; POWER CABLE IS TEST-COUPON CANDIDATE ONLY",
        }))
    return rows


def data_candidates() -> list[dict[str, object]]:
    data = [
        ("ACK-D01", "RS-485 data plus reference", "igus CF240.01.03", "3 x 26 AWG / 0.14 mm2; overall shield; PVC; class 4.4.2.1", "HOLD", "official page does not establish twisted pair or controlled differential impedance; waveform/termination/EMC validation required"),
        ("ACK-D02", "TTL data plus reference", "igus CF240.01.03", "3 x 26 AWG / 0.14 mm2; overall shield; PVC; class 4.4.2.1", "TEST-COUPON CANDIDATE", "electrical level, ground-offset, bend, connector and EMC tests required"),
        ("ACK-D03", "inter-actuator X4P links", "standard ROBOTIS X4P cable", "contains GND, VDD, DATA+, DATA-", "REJECT", "would parallel separately protected actuator power branches"),
        ("ACK-D04", "inter-actuator X3P links", "standard ROBOTIS X3P cable", "contains GND, VDD, DATA", "REJECT", "would parallel separately protected actuator power branches"),
    ]
    return [common({"candidate_id": i, "service": service, "candidate": candidate, "published_construction": construction, "disposition": disposition, "remaining_evidence": evidence, "selected": "NO"}) for i, service, candidate, construction, disposition, evidence in data]


def cavity_rows() -> list[dict[str, object]]:
    links = read_csv(PHYSICAL / "bus-physical-link-register.csv")
    if len(links) != 25:
        raise RuntimeError("25 physical bus links required")
    rows: list[dict[str, object]] = []
    for link in links:
        rs485 = link["protocol"].startswith("RS-485")
        pins = ((1, "GND", "INDIVIDUAL BRANCH RETURN", "POPULATED"), (2, "VDD", "INDIVIDUAL PROTECTED BRANCH POSITIVE", "POPULATED"), (3, "DATA+" if rs485 else "DATA", "SERIAL DATA", "POPULATED"))
        if rs485:
            pins += ((4, "DATA-", "SERIAL DATA", "POPULATED"),)
        for pin, signal, role, state in pins:
            rows.append(common({"cavity_id": f"IN-{link['axis_id']}-{pin}", "connector_id": link["to_endpoint"], "connector_role": "ACTUATOR INPUT", "axis_id": link["axis_id"], "bus_id": link["bus_id"], "pin": pin, "signal": signal, "physical_role": role, "required_population": state, "actual_population": "NOT INSPECTED", "continuity_target": "INDIVIDUAL PBR" if pin in (1, 2) else link["bus_id"], "no_backfeed_requirement": "VERIFY ISOLATED FROM ADJACENT POWER BRANCHES" if pin in (1, 2) else "N/A"}))
        if link["next_endpoint"].startswith("J-OUT-"):
            outgoing = ((1, "GND", "MUST REMAIN EMPTY", "EMPTY"), (2, "VDD", "MUST REMAIN EMPTY", "EMPTY"), (3, "DATA+" if rs485 else "DATA", "SERIAL DATA", "POPULATED"))
            if rs485:
                outgoing += ((4, "DATA-", "SERIAL DATA", "POPULATED"),)
            for pin, signal, role, state in outgoing:
                rows.append(common({"cavity_id": f"OUT-{link['axis_id']}-{pin}", "connector_id": link["next_endpoint"], "connector_role": "DATA-ONLY OUTGOING", "axis_id": link["axis_id"], "bus_id": link["bus_id"], "pin": pin, "signal": signal, "physical_role": role, "required_population": state, "actual_population": "NOT INSPECTED", "continuity_target": "OPEN CIRCUIT" if state == "EMPTY" else link["bus_id"], "no_backfeed_requirement": "NO CONTINUITY TO GND/VDD OR ANY ADJACENT ACTUATOR BRANCH" if state == "EMPTY" else "N/A"}))
    return rows


def inspection_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-T01", "verify received EHR-3/EHR-4 and SEH-001T-P0.6 identity and lot", "100% visual/label/CoC", "exact candidate family and traceable lot"),
        ("ACK-T02", "approve conductor/contact compatibility before crimping production harness", "supplier application review", "written approval or revised compatible wire/contact selection"),
        ("ACK-T03", "prepare representative crimp coupons with controlled tooling", "tool/height/cross-section record", "SELECTION REQUIRED"),
        ("ACK-T04", "perform crimp pull tests by wire lot and setup", "N and failure mode", "SELECTION REQUIRED BY ACCEPTED STANDARD/REVIEWER"),
        ("ACK-T05", "inspect all 94 actuator-input cavities", "100% visual and pin gauge", "correct position, latch and polarity"),
        ("ACK-T06", "inspect all 65 outgoing data-only cavities", "100% visual and pin gauge", "GND/VDD empty; data contacts populated as specified"),
        ("ACK-T07", "continuity test every populated contact end-to-end", "ohm", "SELECTION REQUIRED; recorded by serialized assembly"),
        ("ACK-T08", "verify every outgoing GND/VDD cavity is open to every power branch", "ohm/insulation", "SELECTION REQUIRED; no measurable backfeed path"),
        ("ACK-T09", "measure branch voltage drop and connector temperature rise at accepted current waveform", "V/degC/time", "SELECTION REQUIRED"),
        ("ACK-T10", "cycle every service loop through joint travel without power", "cycles/visual", "SELECTION REQUIRED; no snag, twist, latch damage or bend violation"),
        ("ACK-T11", "validate RS-485 and TTL waveforms at the final cable lengths/topology", "scope/error count", "SELECTION REQUIRED"),
        ("ACK-T12", "fault-inject adjacent-branch short/backfeed conditions on protected fixture", "A/V/clearing time", "SELECTION REQUIRED; protection and isolation response accepted"),
    ]
    return [common({"test_id": i, "inspection_or_test": test, "method_or_unit": method, "acceptance_limit": limit, "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE"}) for i, test, method, limit in data]


def hold_rows() -> list[dict[str, object]]:
    data = [
        ("ACK-H01", "CF130.03.02.UL 0.34 mm2 nominal conductor exceeds JST EH 0.33 mm2 published maximum", "written JST/igus application approval or a different compatible wire/contact family plus received crimp validation"),
        ("ACK-H02", "normal RMS, peak duration, diversity and regeneration waveforms are unmeasured", "accepted whole-body trajectories with synchronized current/voltage/temperature records"),
        ("ACK-H03", "branch fuse/eFuse/current-limiter coordination is unselected", "fault current, impedance, inrush, regeneration, interruption and connector-protection tests"),
        ("ACK-H04", "CF130 is a bending cable, not a released torsional joint cable", "route-specific motion classification, bend/twist model and representative cycle test"),
        ("ACK-H05", "CF240.01.03 is not verified as an RS-485 differential cable", "manufacturer suitability statement or bus waveform/termination/EMC evidence at final topology"),
        ("ACK-H06", "cut lengths, service slack, clamp positions and retention hardware are unselected", "as-built route measurement and dimensioned assembly drawings"),
        ("ACK-H07", "contact crimp tooling, setup, pull limit and cross-section acceptance are unselected", "controlled process specification, coupons and qualified inspection"),
        ("ACK-H08", "data-only outgoing cavity construction is unbuilt and uninspected", "serialized 100% cavity, continuity, isolation and no-backfeed records"),
        ("ACK-H09", "whole-body bus termination, bias, baud and shielding remain unvalidated", "final controller, cable and topology tests across motion/power states"),
        ("ACK-H10", "qualified electrical and functional-safety review is absent", "signed review of the identical frozen as-built harness and test evidence"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980" role="img" aria-labelledby="title desc"><title id="title">HR-30 actuator cable-kit architecture</title><desc id="desc">Each actuator receives an individual protected power pair and serial data. Outgoing inter-actuator connectors omit ground and voltage contacts.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:34px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.data{{stroke:#28a9df;stroke-width:8;fill:none}}.power{{stroke:#f2b91d;stroke-width:9;fill:none}}.empty{{fill:#fff;stroke:#982520;stroke-width:5}}.pin{{fill:#d9f2ff;stroke:#0b4f91;stroke-width:3}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="980" fill="#eef8ff"/><text class="h" x="50" y="60">HR-30 split actuator harness candidate</text><rect class="box" x="55" y="180" width="330" height="270" rx="20"/><text x="90" y="225">25-channel protected PDU</text><text class="s" x="90" y="270">one positive + return pair per axis</text><text class="s" x="90" y="310">candidate internal cap ≤ 2.499 A</text><text class="s" x="90" y="350">branch protection: selection required</text><rect class="box" x="620" y="130" width="390" height="380" rx="20"/><text x="655" y="175">Actuator input EHR-4 / EHR-3</text><circle class="pin" cx="690" cy="235" r="24"/><text x="680" y="242">1</text><text class="s" x="735" y="242">GND — individual return</text><circle class="pin" cx="690" cy="300" r="24"/><text x="680" y="307">2</text><text class="s" x="735" y="307">VDD — individual protected feed</text><circle class="pin" cx="690" cy="365" r="24"/><text x="680" y="372">3</text><text class="s" x="735" y="372">DATA / DATA+</text><circle class="pin" cx="690" cy="430" r="24"/><text x="680" y="437">4</text><text class="s" x="735" y="437">DATA− on RS-485 only</text><path class="power" d="M385 270 C500 270 520 235 620 235"/><path class="power" d="M385 340 C500 340 520 300 620 300"/><rect class="box" x="1160" y="130" width="370" height="380" rx="20"/><text x="1195" y="175">Outgoing data-only housing</text><circle class="empty" cx="1230" cy="235" r="24"/><text x="1220" y="242">1</text><text class="s" x="1275" y="242">EMPTY — no GND pass-through</text><circle class="empty" cx="1230" cy="300" r="24"/><text x="1220" y="307">2</text><text class="s" x="1275" y="307">EMPTY — no VDD pass-through</text><circle class="pin" cx="1230" cy="365" r="24"/><text x="1220" y="372">3</text><text class="s" x="1275" y="372">DATA / DATA+</text><circle class="pin" cx="1230" cy="430" r="24"/><text x="1220" y="437">4</text><text class="s" x="1275" y="437">DATA− on RS-485 only</text><path class="data" d="M1010 365 L1160 365"/><path class="data" d="M1010 430 L1160 430"/><rect class="warn" x="110" y="610" width="1380" height="230" rx="20"/><text class="h" x="155" y="665">Unresolved physical interface</text><text x="155" y="720">CF130.03.02.UL is a test-coupon candidate only: 0.34 mm² nominal exceeds JST's 0.33 mm² maximum.</text><text x="155" y="765">CF240.01.03 is shielded and flexible, but RS-485 twist/impedance suitability is not established.</text><text x="155" y="810">No cable is approved to crimp, connect or energize.</text><text class="s" x="50" y="940">{html.escape(WARNING)}</text></svg>'''


def render(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> str:
    axis_table = "".join(f"<tr><td>{html.escape(str(r['axis_id']))}</td><td>{html.escape(str(r['bus_id']))}</td><td>{r['candidate_internal_limit_a']} A</td><td>{r['published_stall_endpoint_a']} A</td><td>{r['round_trip_planning_length_mm']} mm</td><td>{html.escape(str(r['wire_contact_compatibility']))}</td></tr>" for r in axis)
    empty_count = sum(r["required_population"] == "EMPTY" for r in cavities)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 actuator cable kit</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}article,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.hold{{border-color:var(--red)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:14px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1180px}}th,td{{padding:14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--deep);color:white;position:sticky;top:0}}img{{max-width:100%;height:auto;border:2px solid var(--line);border-radius:16px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The 25 actuator cables now have explicit pin populations.</h1><p>Every actuator gets an individual protected power pair. Every inter-actuator outgoing housing is data-only, with power cavities intentionally empty.</p></header><main><section class="grid"><article><div class="metric">25 / 25</div><p>axis power pairs bound to current caps and planning lengths</p></article><article><div class="metric">159</div><p>controlled actuator connector-cavity records</p></article><article><div class="metric">{empty_count}</div><p>outgoing GND/VDD cavities required empty</p></article><article class="hold"><div class="metric">0</div><p>released cables, crimp processes, protection devices or powered permissions</p></article></section><section><h2>Physical topology</h2><img src="actuator-cable-kit.svg" alt="Individual actuator power pair and data-only outgoing connector architecture"></section><section><h2>Connector disposition</h2><div class="panel"><p>ROBOTIS uses EHR-03/EHR-04 notation. JST's current canonical housing models are <strong>EHR-3</strong> and <strong>EHR-4</strong>, with standard contact <strong>SEH-001T-P0.6</strong>. Low-insertion-force contacts are rejected for this walking-vibration candidate because JST identifies reduced vibration resistance.</p><p>The order-code family is now explicit, but received mating fit, tooling, crimp quality and retention are still unverified.</p></div></section><section><h2>Power-cable blocker</h2><div class="panel hold"><p><strong>Do not crimp CF130.03.02.UL into this contact yet.</strong> igus publishes 0.34 mm² nominal conductors; JST publishes a 0.33 mm² maximum for the standard EH contact. The 0.01 mm² mismatch requires written supplier approval or a different cable/contact choice plus coupon tests.</p></div></section><section><h2>All 25 axis feeds</h2><div class="scroll"><table><thead><tr><th>Axis</th><th>Bus</th><th>Candidate cap</th><th>Published stall endpoint</th><th>Round-trip planning length</th><th>Wire/contact disposition</th></tr></thead><tbody>{axis_table}</tbody></table></div></section><section><h2>Controlled records</h2><div class="panel"><p><a href="connector-family-disposition.csv">Connector family</a> · <a href="axis-power-cable-candidate.csv">25 axis candidates</a> · <a href="connector-cavity-population.csv">159 cavity records</a> · <a href="data-cable-candidate.csv">Data candidates</a> · <a href="inspection-test-plan.csv">Inspection/test plan</a> · <a href="open-holds.csv">Open holds</a> · <a href="primary-source-register.csv">Primary sources</a></p><small>All measured values remain NONE and every execution state remains NOT EXECUTED.</small></div></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root(axis: list[dict[str, object]], cavities: list[dict[str, object]]) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "actuator_cable_kit_present": True,
        "actuator_cable_kit_axis_count": len(axis),
        "actuator_cable_kit_cavity_record_count": len(cavities),
        "actuator_cable_kit_required_empty_cavity_count": sum(r["required_population"] == "EMPTY" for r in cavities),
        "actuator_cable_kit_current_caps_propagated": True,
        "actuator_connector_candidate_order_codes_bound": True,
        "actuator_power_cable_selected": False,
        "actuator_data_cable_selected": False,
        "actuator_crimp_process_selected": False,
        "actuator_cable_kit_built": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-START -->", "<!-- HR30-ACTUATOR-CABLE-KIT-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Actuator cable kit\n\nThe [interactive actuator cable-kit guide](harness/actuator-cable-kit-p0.1/index.html) assigns all **25 axis feeds** their accepted candidate current caps and planning lengths, binds JST **EHR-3/EHR-4 + SEH-001T-P0.6** candidate order-code families, and defines **{len(cavities)} connector-cavity records**. Outgoing inter-actuator housings intentionally leave every GND/VDD cavity empty so the 25 separately protected power branches cannot be paralleled. No wire is released: the current CF130 0.34 mm² test-coupon candidate exceeds JST's published 0.33 mm² maximum and stays blocked pending supplier disposition or reselection.\n{end}\n'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-README-START -->"
    readme.write_text(text.replace(marker, block + marker), encoding="utf-8", newline="\n")

    page = WHOLE / "index.html"
    text = page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-ACTUATOR-CABLE-KIT-P01-START -->", "<!-- HR30-ACTUATOR-CABLE-KIT-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="actuator-cable-kit"><h2>The actuator pin population is explicit</h2><div class="grid"><article class="card pass"><div class="metric">25 / 25</div><p>axis feeds carry their deterministic candidate current caps and routed planning lengths.</p></article><article class="card"><div class="metric">{len(cavities)}</div><p>controlled actuator connector-cavity records.</p></article><article class="card"><div class="metric">34</div><p>outgoing GND/VDD cavities required to remain empty across 17 data-only links.</p></article><article class="card hold"><h3>Wire remains unselected</h3><p>CF130's 0.34 mm² nominal conductor exceeds JST's 0.33 mm² maximum; supplier disposition or reselection is required.</p></article></div><p><a href="harness/actuator-cable-kit-p0.1/index.html">Open the interactive actuator cable-kit guide</a>. It defines the candidate architecture but grants no procurement, crimping, connection or powered-work authority.</p></section>{end}'''
    marker = "<!-- HR30-FIRST-ENERGIZATION-P01-START -->"
    page.write_text(text.replace(marker, section + marker), encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    sources, connectors = source_rows(), connector_rows()
    axes, data, cavities = axis_rows(), data_candidates(), cavity_rows()
    tests, holds = inspection_rows(), hold_rows()
    write_csv(OUT / "primary-source-register.csv", sources)
    write_csv(OUT / "connector-family-disposition.csv", connectors)
    write_csv(OUT / "axis-power-cable-candidate.csv", axes)
    write_csv(OUT / "data-cable-candidate.csv", data)
    write_csv(OUT / "connector-cavity-population.csv", cavities)
    write_csv(OUT / "inspection-test-plan.csv", tests)
    write_csv(OUT / "open-holds.csv", holds)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "source_count": len(sources), "connector_decision_count": len(connectors),
        "axis_count": len(axes), "data_candidate_count": len(data), "cavity_record_count": len(cavities),
        "required_empty_cavity_count": sum(r["required_population"] == "EMPTY" for r in cavities),
        "inspection_test_count": len(tests), "open_hold_count": len(holds), "current_caps_propagated": True,
        "canonical_jst_order_code_family_bound": True, "cf130_jst_cross_section_compatibility": False,
        "power_cable_selected": False, "data_cable_selected": False, "crimp_process_selected": False,
        "built_cable_count": 0, "executed_test_count": 0, "procurement_authority": False, "fabrication_authority": False,
        "connection_authority": False, "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "actuator-cable-kit-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 actuator cable kit P0.1\n\n**{WARNING}**\n\nThis package defines the 25-axis split power/data cable-kit candidate down to every actuator connector cavity. Current caps are propagated, but no physical wire, protection device or crimp process is released.\n", encoding="utf-8", newline="\n")
    (OUT / "actuator-cable-kit.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render(axes, cavities), encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "actuator-cable-kit-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root(axes, cavities)
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
