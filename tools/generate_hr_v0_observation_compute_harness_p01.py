#!/usr/bin/env python3
"""Generate the R207 six-conductor observation compute-harness candidate."""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from generate_hr_v0_observation_field_harness_p01 import digest, manifest, table, write, write_csv


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/harness/hr-v0-observation-compute-harness-p0.1"
WEB = ROOT / "release/hr-v0/observation-compute-harness-p0.1"
DOC = ROOT / "docs/hr-v0-observation-compute-harness-p0.1.md"
IDENTIFIER = "HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1"
ROUND = "R207"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
R205 = ROOT / "electrical/integration/hr-v0-pi-observation-integration-p0.1"
P116 = ROOT / "electrical/kicad/project-button-v3-p1.16-observation-candidate"


def main() -> int:
    source_paths = {
        "R202 connector schedule": R202 / "connector-schedule.csv",
        "R202 logic-load budget": R202 / "load-budget.csv",
        "R204 connector schedule": R204 / "connector-schedule.csv",
        "R204 harness interface": R204 / "harness-interface.csv",
        "R205 compute-route screen": R205 / "harness-length-calculation.csv",
        "P1.16 connector schedule": P116 / "connector-schedule.csv",
        "P1.16 native netlist": P116 / "validation/project-button-v3-p1.16-observation-candidate.net",
    }
    for path in source_paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    ENG.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    conductors = [
        ("W14001", "PI_3V3_CANDIDATE", "JLOGIC1:1", "JOBS1:1", "3051 RD005", "red", "POWER CANDIDATE"),
        ("W14002", "COMPUTE_0V", "JLOGIC1:2", "JOBS1:2", "3051 BK005", "black", "RETURN"),
        ("W14003", "OBS_SR1_PI", "JLOGIC1:3", "JOBS1:3", "3051 BL005", "blue", "DIAGNOSTIC INPUT"),
        ("W14004", "OBS_SRA1_PI", "JLOGIC1:4", "JOBS1:4", "3051 OR005", "orange", "DIAGNOSTIC INPUT"),
        ("W14005", "OBS_K1_PI", "JLOGIC1:5", "JOBS1:5", "3051 VI005", "violet", "DIAGNOSTIC INPUT"),
        ("W14006", "OBS_K2_PI", "JLOGIC1:6", "JOBS1:6", "3051 WH005", "white", "DIAGNOSTIC INPUT"),
    ]
    schedule = [{
        "wire_number": wire, "net": net, "from": start, "to": end, "role": role,
        "wire_candidate": f"Belden {part}", "color": color,
        "construction": "22 AWG / 7x30 tinned copper / PVC / nominal OD 1.6 mm",
        "termination": "direct-stripped flexible conductor; no ferrule candidate",
        "cut_length_mm": "SELECTION REQUIRED", "state": "CATALOG CANDIDATE - NOT CUT OR INSTALLED", "warning": WARNING,
    } for wire, net, start, end, part, color, role in conductors]
    write_csv(ENG / "conductor-schedule.csv", schedule)
    write_csv(ENG / "harness-bom.csv", [{
        "reference": f"WIRE-{wire}", "manufacturer": "Belden", "order_code": part,
        "quantity": "SELECTION REQUIRED - measured cut length plus process allowance",
        "status": "EXACT COLOR/SPOOL CANDIDATE; PROCUREMENT NOT AUTHORIZED",
        "evidence": "Belden 3051 technical data revision 0.118 dated 2026-06-30", "warning": WARNING,
    } for wire, _, _, _, part, _, _ in conductors])

    interfaces = [{
        "wire_number": wire, "net": net, "r202_terminal": start,
        "r202_terminal_candidate": "Phoenix Contact MKDS 1/6-3,5 item 1751280",
        "r204_terminal": end, "r204_terminal_candidate": "Phoenix Contact MKDS 1/6-3,5 item 1751280",
        "p116_native_left_label": f"OBS1 {start}", "p116_native_right_label": f"PIOBS1 {end}",
        "mapping": "EXACT SOURCE PARITY", "physical_state": "NOT BUILT / NOT CONNECTED", "warning": WARNING,
    } for wire, net, start, end, _, _, _ in conductors]
    write_csv(ENG / "interface-control.csv", interfaces)

    process = [{
        "end": end, "terminal": "MKDS 1/6-3,5 item 1751280",
        "wire_envelope": "flexible 0.14-1.5 mm2; ferrule 0.25-0.5 mm2",
        "candidate_preparation": "direct strip 5 mm; support PCB terminal during connection",
        "torque": "0.22-0.25 N m", "candidate_conductors_per_clamp": "one",
        "required_controls": "received identity/orientation; calibrated strip gage and torque driver; no nicked/escaped strands; insertion, pull and post-torque inspection",
        "state": "PROCESS QUALIFICATION OPEN", "warning": WARNING,
    } for end in ("R202 JLOGIC1", "R204 JOBS1")]
    write_csv(ENG / "termination-process.csv", process)

    manhattan = 335.4
    radius = 15.0
    rounded = manhattan + 2.0 * (math.pi / 2.0 - 2.0) * radius
    write_csv(ENG / "route-length-calculation.csv", [{
        "route": "R202 JLOGIC1 to R204 JOBS1", "r205_manhattan_screen_mm": f"{manhattan:.1f}",
        "bend_count": 2, "candidate_min_stationary_bend_radius_mm": f"{radius:.1f}",
        "rounded_centerline_screen_mm": f"{rounded:.1f}", "equation": "335.4 + 2*(pi/2 - 2)*15",
        "cut_length_mm": "SELECTION REQUIRED",
        "unknown_addends": "received Pi/case/carrier transform; exact connector exits; service loop; termination allowance; strain relief; tolerance",
        "state": "GEOMETRIC SCREEN ONLY - DO NOT CUT", "warning": WARNING,
    }])
    bare_area = 6.0 * math.pi * (1.6 / 2.0) ** 2
    write_csv(ENG / "bundle-area-screen.csv", [{
        "conductor_count": 6, "nominal_od_each_mm": "1.6", "sum_bare_circular_area_mm2": f"{bare_area:.2f}",
        "equation": "6*pi*(1.6/2)^2", "duct_fill_percent": "SELECTION REQUIRED",
        "not_included": "packing inefficiency; labels; ties; bend space; other WD2 occupancy; cover clearance; separation",
        "state": "AREA INPUT ONLY - NOT A DUCT-FILL RESULT", "warning": WARNING,
    }])
    write_csv(ENG / "electrical-budget-screen.csv", [{
        "net": "PI_3V3_CANDIDATE", "r202_load_screen": "<=5.0 mA calculation screen",
        "basis": "2 x 1.9 mA max ISO1212 logic ICC1 plus <=4 x 3.3 V / 11 kohm",
        "cable_drop": "SELECTION REQUIRED - manufacturer DCR and measured cut length not frozen",
        "pi_external_load_approval": "NOT ESTABLISHED", "back_power_behavior": "NOT ESTABLISHED",
        "state": "SOURCE LOAD SCREEN ONLY", "warning": WARNING,
    }])

    sources = [
        {"source_id": "OCH-SRC-001", "manufacturer": "Phoenix Contact", "document": "MKDS 1/6-3,5 item 1751280 current product data", "revision_date": "current web data accessed 2026-08-10", "uri": "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-6-35-1751280", "verified_fact": "six positions; 3.5 mm pitch; flexible 0.14-1.5 mm2; 5 mm strip; 0.22-0.25 N m; support during connection", "not_proved": "received identity/orientation, installed process, pull performance or application acceptance", "warning": WARNING},
        {"source_id": "OCH-SRC-002", "manufacturer": "Belden", "document": "3051 technical data", "revision_date": "revision 0.118 dated 2026-06-30; accessed 2026-08-10", "uri": "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3051", "verified_fact": "active/global; 22 AWG 7x30 tinned copper PVC; OD 1.6 mm; 15 mm stationary radius; RD005/BK005/BL005/OR005/VI005/WH005 listed as 100 ft variants", "not_proved": "robot application acceptance, actual route, signal behavior, cut length or Pi load approval", "warning": WARNING},
        *[{"source_id": f"OCH-SRC-{index:03d}", "manufacturer": "Project Button", "document": name, "revision_date": "controlled source hashed 2026-08-10", "uri": path.relative_to(ROOT).as_posix(), "verified_fact": "digital interface, load or geometry source only", "not_proved": "physical article, installation, powered behavior, safety credit or authorization", "warning": WARNING} for index, (name, path) in enumerate(source_paths.items(), 3)],
    ]
    write_csv(ENG / "source-register.csv", sources)

    hold_topics = [
        "received R202/R204 terminal identity, orientation, soldering and damage inspection",
        "received Pi/case/cooler/bracket/R204 stack transform and exact harness endpoints",
        "measured physical route and exact cut length for W14001-W14006",
        "service loop, termination allowance, tolerance, labels and strain relief",
        "usable WD2 area, existing occupancy, packing, cover fit and domain separation",
        "15 mm stationary bend radius and transition support in the installed route",
        "qualified direct-strip process, calibrated strip gage and torque driver",
        "strand damage, exposed copper, insertion, torque, pull and post-torque records at both ends",
        "manufacturer DCR plus selected length voltage-drop/return-shift calculation",
        "Raspberry Pi 3V3 external-load, GPIO threshold, pull, startup and brownout acceptance",
        "open/short/cross-short/return-loss/source-loss and back-power fault evidence",
        "continuity, polarity, isolation, crosstalk, EMC, thermal and timing evidence",
        "qualified electrical/compute/panel review and separate written work authorization",
    ]
    holds = [{"hold_id": f"OCH-HOLD-{index:03d}", "topic": topic, "state": "OPEN - SELECTION/EVIDENCE REQUIRED", "evidence_uri": "", "warning": WARNING} for index, topic in enumerate(hold_topics, 1)]
    write_csv(ENG / "selection-holds.csv", holds)
    acceptance_topics = ["source/interface parity", "received terminals/boards", "received compute-stack geometry", "route measurement", "cut schedule/labels", "duct fill/separation", "bend/strain relief", "strip/torque process", "pull/visual inspection", "continuity/polarity/isolation", "3V3 load/drop/back-power", "GPIO/cable fault/EMC/thermal/timing", "qualified review and written authority"]
    acceptance = [{"acceptance_id": f"OCH-ACC-{index:03d}", "subject": topic, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for index, topic in enumerate(acceptance_topics, 1)]
    write_csv(ENG / "acceptance-matrix.csv", acceptance)

    status = {
        "identifier": IDENTIFIER, "round": ROUND, "date": DATE, "conductor_rows": 6,
        "interface_rows": 6, "source_rows": len(sources), "selection_holds": len(holds), "acceptance_rows": len(acceptance),
        "manhattan_screen_mm": manhattan, "rounded_centerline_screen_mm": round(rounded, 1), "bare_bundle_area_screen_mm2": round(bare_area, 2),
        "wire_family_candidate": "Belden 3051 22 AWG", "terminal_candidate_both_ends": "Phoenix Contact 1751280",
        "termination_candidate": "direct strip at both ends; no ferrule", "digital_mapping_complete": True,
        "cut_lengths_selected": False, "physical_route_accepted": False, "duct_fill_accepted": False,
        "pi_external_load_accepted": False, "back_power_accepted": False, "harness_released": False,
        "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False,
        "source_hashes": {name: digest(path) for name, path in source_paths.items()}, "warning": WARNING,
    }
    write(ENG / "package-status.json", json.dumps(status, indent=2) + "\n")

    colors = ["#d22b2b", "#111", "#1479c9", "#ef7d00", "#7d3cb5", "#e9e9e9"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 700" role="img" aria-labelledby="title desc"><title id="title">Six-conductor observation compute harness</title><desc id="desc">Exact proposed conductors between R202 JLOGIC1 and R204 JOBS1; every cut length and physical result remains open.</desc><style>text{{font-family:system-ui,sans-serif;fill:#082b55}}.t{{font-size:27px;font-weight:800}}.l{{font-size:17px;font-weight:700}}.n{{font-size:15px}}.box{{fill:#eef8ff;stroke:#0b4f8a;stroke-width:3}}.wire{{fill:none;stroke-width:8}}.hold{{fill:#fff4c2;stroke:#a06a00;stroke-width:2}}</style><text x="40" y="45" class="t">R202 JLOGIC1 → R204 JOBS1 compute harness candidate</text><rect x="40" y="85" width="250" height="475" rx="16" class="box"/><rect x="830" y="85" width="250" height="475" rx="16" class="box"/><text x="70" y="125" class="l">OBS1 / JLOGIC1</text><text x="860" y="125" class="l">PIOBS1 / JOBS1</text>'''
    for index, ((wire, net, start, end, _, color, _), stroke) in enumerate(zip(conductors, colors)):
        y = 175 + index * 62
        outline = f'<path d="M290 {y} C485 {y},635 {y},830 {y}" class="wire" stroke="#456" stroke-width="12"/>' if color == "white" else ""
        svg += f'<text x="62" y="{y+6}" class="n">{start} · {wire}</text>{outline}<path d="M290 {y} C485 {y},635 {y},830 {y}" class="wire" stroke="{stroke}"/><text x="380" y="{y-11}" class="n">{net} · {color}</text><text x="855" y="{y+6}" class="n">{end}</text>'
    svg += f'<rect x="40" y="595" width="1040" height="70" rx="12" class="hold"/><text x="62" y="624" class="l">Cut length: SELECTION REQUIRED · Pi 3V3 load/back-power acceptance: OPEN</text><text x="62" y="650" class="n">{WARNING}</text></svg>'
    write(ENG / "compute-harness.svg", svg)

    readme = f"""# {IDENTIFIER}\n\n**{WARNING}**\n\nR207 promotes the six already source-bound R204 wire candidates into a synchronized harness-definition package. It controls W14001-W14006, exact endpoints, both-end terminal process envelopes, route arithmetic, load boundaries, evidence holds and blank acceptance records. It does not release a harness.\n\nThe 335.4 mm R205 Manhattan path becomes a {rounded:.1f} mm rounded-centerline geometry screen with two 15 mm-radius corners. Neither value is a cut length. The {bare_area:.2f} mm2 sum of six bare circular wire areas is not a duct-fill result.\n\nGenerated by `tools/generate_hr_v0_observation_compute_harness_p01.py`.\n"""
    write(ENG / "README.md", readme)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R207 observation compute harness</title><style>:root{{--sky:#dff3ff;--blue:#082b55;--gold:#f5bd21;--paper:#f8fbfd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--blue);font:clamp(16px,1.2vw,19px)/1.55 system-ui,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:var(--sky);border-bottom:5px solid var(--gold)}}h1{{font-size:clamp(32px,5vw,62px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(24px,3vw,36px)}}.warning{{padding:18px;background:#fff4c2;border:3px solid #9c6800;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.card{{padding:20px;background:white;border:2px solid #8db8d9;border-radius:14px}}.card b{{font-size:30px;display:block}}.scroll{{overflow:auto;border:2px solid #8db8d9;border-radius:12px;background:white}}table{{width:100%;border-collapse:collapse;min-width:880px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid #b8d2e5;font-size:14px}}th{{background:var(--blue);color:white}}img{{width:100%;height:auto;background:white;border:2px solid #8db8d9;border-radius:14px}}a{{color:#075ea8}}@media(max-width:520px){{header,main{{padding:18px}}th,td{{font-size:14px}}}}</style></head><body><header><p>Project Button · R207 controlled engineering guide</p><h1>Six exact conductors. Physical evidence still required.</h1><p class="warning">{WARNING}</p></header><main><div class="cards"><div class="card"><b>6</b>exact wire/color candidates</div><div class="card"><b>{rounded:.1f} mm</b>rounded geometry screen—not cut length</div><div class="card"><b>≤5.0 mA</b>source load screen—not Pi approval</div><div class="card"><b>13</b>open acceptance rows</div></div><h2>Interactive wiring view</h2><img src="compute-harness.svg" alt="Six exact proposed conductors from R202 JLOGIC1 to R204 JOBS1"><h2>Conductor schedule</h2>{table(schedule,["wire_number","net","from","to","wire_candidate","color","cut_length_mm","state"])}<h2>Both-end process boundary</h2>{table(process,["end","terminal","wire_envelope","candidate_preparation","torque","required_controls","state"])}<h2>Open holds</h2>{table(holds,["hold_id","topic","state"])}<p><a href="../../../electrical/harness/hr-v0-observation-compute-harness-p0.1/electrical-budget-screen.csv">Open load boundary</a> · <a href="conductor-schedule.csv">Download conductor schedule</a> · <a href="source-register.csv">Primary-source register</a></p></main></body></html>'''
    write(ENG / "index.html", page)
    for path in ENG.iterdir():
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            shutil.copy2(path, WEB / path.name)
    manifest(ENG)
    manifest(WEB)
    write(DOC, f"# R207 observation compute harness candidate\n\n**{WARNING}**\n\n`{IDENTIFIER}` controls six exact proposed Belden 3051 conductors from R202 JLOGIC1 to R204 JOBS1, both-end Phoenix 1751280 preparation limits, route/bundle/load screens and fail-closed acceptance evidence. Every cut length, physical route, Pi load/back-power result, physical test, qualified review and work authorization remains open.\n")
    print(f"Generated {IDENTIFIER}: 6 conductors / 13 holds / 13 open acceptance rows")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
