#!/usr/bin/env python3
"""Generate the R206 five-conductor observation field-harness candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/harness/hr-v0-observation-field-harness-p0.1"
WEB = ROOT / "release/hr-v0/observation-field-harness-p0.1"
DOC = ROOT / "docs/hr-v0-observation-field-harness-p0.1.md"
IDENTIFIER = "HR-V0-OBSERVATION-FIELD-HARNESS-P0.1"
ROUND = "R206"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
P116 = ROOT / "electrical/kicad/project-button-v3-p1.16-observation-candidate"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R205 = ROOT / "electrical/integration/hr-v0-pi-observation-integration-p0.1"


def write_csv(path: Path, data: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory: Path) -> None:
    target = directory / "SOURCE-MANIFEST.csv"
    data = [{"file": path.relative_to(directory).as_posix(), "sha256": digest(path).upper()}
            for path in sorted(directory.rglob("*")) if path.is_file() and path != target]
    write_csv(target, data)


def table(data: list[dict[str, object]], keys: list[str]) -> str:
    headings = "".join(f"<th>{html.escape(key.replace('_', ' ').title())}</th>" for key in keys)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key in keys) + "</tr>" for row in data)
    return f'<div class="scroll"><table><thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table></div>'


def main() -> int:
    source_paths = {
        "P1.16 connector schedule": P116 / "connector-schedule.csv",
        "P1.16 native netlist": P116 / "validation/project-button-v3-p1.16-observation-candidate.net",
        "R202 connector schedule": R202 / "connector-schedule.csv",
        "R205 route screen": R205 / "harness-length-calculation.csv",
    }
    for path in source_paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    ENG.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    conductors = [
        ("W9008", "SR1_STATUS", "XT1-03", "OBS1 JFIELD1:1", "Belden 3051 WB005", "white/black"),
        ("W9009", "SRA1_STATUS", "XT1-04", "OBS1 JFIELD1:2", "Belden 3051 WO005", "white/orange"),
        ("W9010", "K1_STATUS", "XT1-05", "OBS1 JFIELD1:3", "Belden 3051 WV005", "white/violet"),
        ("W9011", "K2_STATUS", "XT1-06", "OBS1 JFIELD1:4", "Belden 3051 WY005", "white/yellow"),
        ("W9007", "SAFETY_0V", "XT1-02", "OBS1 JFIELD1:5", "Belden 3051 WU005", "white/blue"),
    ]
    schedule = [{
        "wire_number": wire, "net": net, "from": start, "to": end, "wire_candidate": part,
        "color": color, "construction": "22 AWG / 7x30 tinned copper / PVC / nominal OD 1.6 mm",
        "termination": "direct-stripped flexible conductor; no ferrule candidate",
        "cut_length_mm": "SELECTION REQUIRED", "state": "CATALOG CANDIDATE - NOT CUT OR INSTALLED", "warning": WARNING,
    } for wire, net, start, end, part, color in conductors]
    write_csv(ENG / "conductor-schedule.csv", schedule)

    bom = [
        {"reference": f"WIRE-{wire}", "manufacturer": "Belden", "order_code": part.removeprefix("Belden "), "quantity": "SELECTION REQUIRED - measured cut length plus process allowance", "status": "EXACT COLOR/SPOOL CANDIDATE; PROCUREMENT NOT AUTHORIZED", "evidence": "Belden 3051 technical data revision 0.118 dated 2026-06-30", "warning": WARNING}
        for wire, _, _, _, part, _ in conductors
    ]
    write_csv(ENG / "harness-bom.csv", bom)

    interfaces = []
    for wire, net, start, end, _, _ in conductors:
        interfaces.append({"wire_number": wire, "net": net, "panel_terminal": start, "panel_terminal_candidate": "Phoenix Contact PT 2,5 item 3209510" if start != "XT1-02" else "Phoenix Contact PT 2,5 BU item 3209523", "receiver_terminal": end, "receiver_terminal_candidate": "Phoenix Contact MKDS 1/6-3,5 item 1751280", "mapping": "EXACT SOURCE PARITY", "physical_state": "NOT BUILT / NOT CONNECTED", "warning": WARNING})
    interfaces.append({"wire_number": "NONE", "net": "INTENTIONALLY_UNUSED_OBS1_JFIELD1_6", "panel_terminal": "NONE", "panel_terminal_candidate": "NONE", "receiver_terminal": "OBS1 JFIELD1:6", "receiver_terminal_candidate": "Phoenix Contact MKDS 1/6-3,5 item 1751280", "mapping": "DELIBERATE NO-CONNECT", "physical_state": "MUST REMAIN UNWIRED", "warning": WARNING})
    write_csv(ENG / "interface-control.csv", interfaces)

    process = [
        {"end": "XT1", "terminal": "PT 2,5 / PT 2,5 BU", "wire_envelope": "flexible 0.14-4 mm2; ferrule 0.14-2.5 mm2", "candidate_preparation": "direct strip 8-10 mm; insert using push button", "torque": "not applicable to push-in conductor connection", "required_controls": "received identity/orientation; calibrated strip gage; no nicked/escaped strands; insertion and pull inspection", "state": "PROCESS QUALIFICATION OPEN", "warning": WARNING},
        {"end": "JFIELD1", "terminal": "MKDS 1/6-3,5 item 1751280", "wire_envelope": "flexible 0.14-1.5 mm2; ferrule 0.25-0.5 mm2", "candidate_preparation": "direct strip 5 mm; support PCB terminal during connection", "torque": "0.22-0.25 N m", "required_controls": "received identity/orientation; calibrated strip gage and torque driver; no nicked/escaped strands; pull and post-torque inspection", "state": "PROCESS QUALIFICATION OPEN", "warning": WARNING},
    ]
    write_csv(ENG / "termination-process.csv", process)

    radius = 15.0
    manhattan = 276.0
    rounded = manhattan + 2.0 * (math.pi / 2.0 - 2.0) * radius
    lengths = [{"route": "XT1 to OBS1 JFIELD1", "r205_manhattan_screen_mm": f"{manhattan:.1f}", "bend_count": 2, "candidate_min_stationary_bend_radius_mm": f"{radius:.1f}", "rounded_centerline_screen_mm": f"{rounded:.1f}", "equation": "276 + 2*(pi/2 - 2)*15", "cut_length_mm": "SELECTION REQUIRED", "unknown_addends": "exact XT1 coordinates; received connector exits; service loop; termination allowance; strain relief; tolerance", "state": "GEOMETRIC SCREEN ONLY - DO NOT CUT", "warning": WARNING}]
    write_csv(ENG / "route-length-calculation.csv", lengths)

    sources = [
        {"source_id": "OFH-SRC-001", "manufacturer": "Phoenix Contact", "document": "PT 2,5 item 3209510 current product data", "revision_date": "current web data accessed 2026-08-10", "uri": "https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-3209510", "verified_fact": "push-in; 8-10 mm strip; flexible 0.14-4 mm2; ferrule 0.14-2.5 mm2", "not_proved": "received identity, installed process, pull performance, enclosure suitability", "warning": WARNING},
        {"source_id": "OFH-SRC-002", "manufacturer": "Phoenix Contact", "document": "MKDS 1/6-3,5 item 1751280 current product data", "revision_date": "current web data accessed 2026-08-10", "uri": "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-6-35-1751280", "verified_fact": "six positions; 3.5 mm pitch; flexible 0.14-1.5 mm2; 5 mm strip; 0.22-0.25 N m", "not_proved": "received identity/orientation, PCB support, process or pull performance", "warning": WARNING},
        {"source_id": "OFH-SRC-003", "manufacturer": "Belden", "document": "3051 technical data", "revision_date": "revision 0.118 dated 2026-06-30; accessed 2026-08-10", "uri": "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3051", "verified_fact": "22 AWG 7x30 tinned copper PVC; OD 1.6 mm; 300 V AWM; 15 mm stationary bend radius; exact color order codes", "not_proved": "robot application acceptance, actual route, bundle thermal/EMC behavior or cut length", "warning": WARNING},
        *[{"source_id": f"OFH-SRC-{index:03d}", "manufacturer": "Project Button", "document": name, "revision_date": "controlled source hashed 2026-08-10", "uri": path.relative_to(ROOT).as_posix(), "verified_fact": "digital interface or geometry source only", "not_proved": "physical article, installation, powered behavior or authorization", "warning": WARNING} for index, (name, path) in enumerate(source_paths.items(), 4)],
    ]
    write_csv(ENG / "source-register.csv", sources)

    hold_topics = [
        "received XT1 and R202 terminal identity, orientation and damage inspection",
        "exact installed XT1 and JFIELD1 endpoint coordinates and connector exit directions",
        "measured physical route and exact cut length for each of W9007-W9011",
        "service loop, termination allowance, tolerance and strain-relief definition",
        "usable duct area, existing occupancy, fill, cover fit and status/power separation",
        "15 mm minimum stationary bend radius and transition support in the installed route",
        "qualified direct-strip process, strip gages and calibrated torque driver",
        "strand damage, exposed copper, insertion, torque, pull and post-torque inspection records",
        "both-end wire labels and independent continuity/polarity/no-short inspection",
        "field-to-compute isolation, startup/brownout/back-power and cable-fault evidence",
        "installed EMC and thermal evidence with actuator-current conductors present",
        "qualified electrical/panel review and separate written work authorization",
    ]
    holds = [{"hold_id": f"OFH-HOLD-{index:03d}", "topic": topic, "state": "OPEN - SELECTION/EVIDENCE REQUIRED", "evidence_uri": "", "warning": WARNING} for index, topic in enumerate(hold_topics, 1)]
    write_csv(ENG / "selection-holds.csv", holds)
    acceptance_topics = ["source and interface parity", "received parts", "route measurement", "cut schedule", "duct fill/separation", "bend/strain relief", "strip and torque process", "pull/visual inspection", "labels and continuity", "polarity/no-short/isolation", "EMC/thermal/cable fault", "qualified review and written authority"]
    acceptance = [{"acceptance_id": f"OFH-ACC-{index:03d}", "subject": topic, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for index, topic in enumerate(acceptance_topics, 1)]
    write_csv(ENG / "acceptance-matrix.csv", acceptance)

    status = {"identifier": IDENTIFIER, "round": ROUND, "date": DATE, "conductor_rows": 5, "interface_rows": 6, "source_rows": len(sources), "selection_holds": len(holds), "acceptance_rows": len(acceptance), "manhattan_screen_mm": manhattan, "rounded_centerline_screen_mm": round(rounded, 1), "wire_family_candidate": "Belden 3051 22 AWG", "termination_candidate": "direct strip at both ends; no ferrule", "digital_mapping_complete": True, "cut_lengths_selected": False, "physical_route_accepted": False, "harness_released": False, "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "source_hashes": {name: digest(path) for name, path in source_paths.items()}, "warning": WARNING}
    write(ENG / "package-status.json", json.dumps(status, indent=2) + "\n")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 620" role="img" aria-labelledby="title desc"><title id="title">Five-conductor observation field harness</title><desc id="desc">Exact proposed wires from XT1 positions to R202 JFIELD1; all cut lengths and physical acceptance remain open.</desc><style>text{{font-family:system-ui,sans-serif;fill:#082b55}}.t{{font-size:26px;font-weight:800}}.l{{font-size:17px;font-weight:700}}.n{{font-size:15px}}.box{{fill:#eef8ff;stroke:#0b4f8a;stroke-width:3}}.wire{{fill:none;stroke-width:7}}.hold{{fill:#fff4c2;stroke:#a06a00;stroke-width:2}}</style><text x="40" y="44" class="t">XT1 → R202 JFIELD1 diagnostic harness candidate</text><rect x="40" y="80" width="250" height="410" rx="16" class="box"/><rect x="810" y="80" width="250" height="410" rx="16" class="box"/><text x="70" y="120" class="l">Panel XT1</text><text x="840" y="120" class="l">OBS1 / JFIELD1</text>'''
    colors = ["#222", "#ef7d00", "#7d3cb5", "#e0b400", "#1479c9"]
    for index, ((wire, net, start, end, _, color), stroke) in enumerate(zip(conductors, colors)):
        y = 170 + index * 66
        svg += f'<text x="62" y="{y+6}" class="n">{start} · {wire}</text><path d="M290 {y} C480 {y},620 {y},810 {y}" class="wire" stroke="{stroke}"/><text x="365" y="{y-10}" class="n">{net} · {html.escape(color)}</text><text x="835" y="{y+6}" class="n">{end}</text>'
    svg += f'<rect x="40" y="520" width="1020" height="65" rx="12" class="hold"/><text x="62" y="548" class="l">Cut length: SELECTION REQUIRED · direct-strip process: qualification open</text><text x="62" y="572" class="n">{WARNING}</text></svg>'
    write(ENG / "field-harness.svg", svg)

    readme = f"""# {IDENTIFIER}\n\n**{WARNING}**\n\nR206 freezes an exact five-wire catalog candidate and exact digital mapping from XT1 to the R202 observation receiver. It does not release a harness. All cut lengths, installed routing, duct fill, separation, termination qualification and physical acceptance remain open.\n\nThe 276.0 mm R205 Manhattan path becomes a {rounded:.1f} mm rounded-centerline geometry screen when two 15 mm-radius corners replace two sharp corners. Neither value is a cut length.\n\nGenerated by `tools/generate_hr_v0_observation_field_harness_p01.py`.\n"""
    write(ENG / "README.md", readme)

    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R206 observation field harness</title><style>:root{{--sky:#dff3ff;--blue:#082b55;--gold:#f5bd21;--paper:#f8fbfd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--blue);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:5px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning{{padding:18px;background:#fff4c2;border:3px solid #9c6800;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card{{padding:20px;background:white;border:2px solid #8db8d9;border-radius:14px}}.card b{{font-size:30px;display:block}}.scroll{{overflow:auto;border:2px solid #8db8d9;border-radius:12px;background:white}}table{{width:100%;border-collapse:collapse;min-width:880px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid #b8d2e5;font-size:14px}}th{{background:var(--blue);color:white}}img{{width:100%;height:auto;background:white;border:2px solid #8db8d9;border-radius:14px}}a{{color:#075ea8}}code{{font-size:14px}}@media(max-width:520px){{header,main{{padding:18px}}th,td{{font-size:14px}}}}</style></head><body><header><p>Project Button · R206 controlled engineering guide</p><h1>Five wires, exact endpoints, no permission to build yet.</h1><p class="warning">{WARNING}</p></header><main><div class="cards"><div class="card"><b>5</b>exact wire/color candidates</div><div class="card"><b>6</b>interface rows including deliberate no-connect</div><div class="card"><b>{rounded:.1f} mm</b>rounded geometry screen—not cut length</div><div class="card"><b>12</b>open acceptance rows</div></div><h2>Interactive wiring view</h2><img src="field-harness.svg" alt="Five exact proposed conductors from XT1 to R202 JFIELD1"><h2>Conductor schedule</h2>{table(schedule,["wire_number","net","from","to","wire_candidate","color","cut_length_mm","state"])}<h2>Termination process boundary</h2>{table(process,["end","terminal","wire_envelope","candidate_preparation","torque","required_controls","state"])}<h2>Open holds</h2>{table(holds,["hold_id","topic","state"])}<p><a href="../../../../electrical/kicad/project-button-v3-p1.16-observation-candidate/13_runtime_observation_system.kicad_sch">Open native page 13 source</a> · <a href="conductor-schedule.csv">Download conductor schedule</a> · <a href="source-register.csv">Primary-source register</a></p></main></body></html>'''
    page = page.replace("../../../../electrical/", "../../../electrical/")
    write(ENG / "index.html", page)
    for path in ENG.iterdir():
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            shutil.copy2(path, WEB / path.name)
    manifest(ENG)
    manifest(WEB)
    write(DOC, f"# R206 observation field harness candidate\n\n**{WARNING}**\n\nThe synchronized engineering and web package is `{IDENTIFIER}`. Exact proposed catalog identities and digital endpoints are recorded for W9007-W9011. Cut lengths, installed routing, duct fill/separation, termination qualification, physical tests, qualified review and all work authorization remain open.\n")
    print(f"Generated {IDENTIFIER}: 5 conductors / 12 holds / 12 open acceptance rows")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
