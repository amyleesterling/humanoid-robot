#!/usr/bin/env python3
"""Generate the HR-30 logic-only controller power-kit candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "logic-power-kit-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
IDENTIFIER = "HR30-LOGIC-POWER-KIT-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - UNBUILT LOGIC-ONLY POWER FIXTURE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
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
    return [
        common({"source_id": "LP-S01", "manufacturer": "SIGLENT", "document": "SPD3303X/X-E series product page and datasheet", "revision_or_date": "datasheet EN03A; 2024-09-02", "accessed": DATE, "url": "https://www.siglent.com/na/products-overview/spd3303x-x-e/", "verified_use": "SPD3303X exact model; isolated independently controlled outputs; CH1/CH2 0-32 V and 0-3.2 A; 1 mV/1 mA resolution"}),
        common({"source_id": "LP-S02", "manufacturer": "SIGLENT", "document": "SPD3303X/X-E Quick Start", "revision_or_date": "EN02A; 2024-09-02", "accessed": DATE, "url": "https://siglentna.com/wp-content/uploads/dlm_uploads/2022/11/SPD3303X_QuickStart_E02A.pdf", "verified_use": "independent-mode outputs insulated from ground; voltage/current entry; OCP action; per-channel output control"}),
        common({"source_id": "LP-S03", "manufacturer": "JST", "document": "VH connector catalogue", "revision_or_date": "revision/date not stated", "accessed": DATE, "url": "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf", "verified_use": "VHR-2N housing; SVH-21T-P1.1 contacts; AWG22-18 and 1.7-3.0 mm insulation range"}),
        common({"source_id": "LP-S04", "manufacturer": "Alpha Wire", "document": "3051 customer specification", "revision_or_date": "live manufacturer specification; revision/date not stated", "accessed": DATE, "url": "https://www.alphawire.com/Products/Wire/Hook-Up-Wire/Premium/3051", "verified_use": "3051 stranded 22 AWG 7/30 tinned copper; PVC; 300 V; -40 to 105 C; red and black colors"}),
        common({"source_id": "LP-S05", "manufacturer": "Pomona Electronics", "document": "Model 5934 do-it-yourself in-line 4 mm banana plug", "revision_or_date": "D1094503 Rev 101; 2007-10-01", "accessed": DATE, "url": "https://www.pomonaelectronics.com/sites/default/files/d5934_101.pdf", "verified_use": "5934-0 black and 5934-2 red; solderless set-screw assembly; compatible with AWG18-22"}),
    ]


def bindings() -> list[dict[str, object]]:
    items = [
        ("LP-B01", "motion-controller status", WHOLE / "electrical/motion-controller-p0.1/controller-status.json"),
        ("LP-B02", "motion-controller terminal register", WHOLE / "electrical/motion-controller-p0.1/terminal-register.csv"),
        ("LP-B03", "motion-controller component register", WHOLE / "electrical/motion-controller-p0.1/component-register.csv"),
    ]
    return [common({"binding_id": i, "role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}) for i, role, path in items]


def equipment() -> list[dict[str, object]]:
    data = [
        ("LP-P01", "programmable isolated bench supply", "SIGLENT", "SPD3303X", 1, "EXACT CANDIDATE - RECEIPT/CALIBRATION/REVIEW OPEN"),
        ("LP-P02", "controller-end 2-position housing", "JST", "VHR-2N", 1, "EXACT CANDIDATE"),
        ("LP-P03", "crimp contacts", "JST", "SVH-21T-P1.1", 2, "EXACT CANDIDATE - CRIMP PROCESS VALIDATION OPEN"),
        ("LP-P04", "positive conductor, 100 ft spool", "Alpha Wire", "3051 RD005", 1, "EXACT CANDIDATE"),
        ("LP-P05", "return conductor, 100 ft spool", "Alpha Wire", "3051 BK005", 1, "EXACT CANDIDATE"),
        ("LP-P06", "positive 4 mm banana plug", "Pomona Electronics", "5934-2", 1, "EXACT CANDIDATE"),
        ("LP-P07", "return 4 mm banana plug", "Pomona Electronics", "5934-0", 1, "EXACT CANDIDATE"),
        ("LP-P08", "two-conductor sleeve/strain relief and labels", "SELECTION REQUIRED", "SELECTION REQUIRED", 1, "MATERIAL, SIZE, MARKING AND RETENTION OPEN"),
    ]
    return [common({"item_id": i, "function": function, "manufacturer": manufacturer, "manufacturer_part_number": mpn, "quantity": quantity, "selection_state": state, "procurement_released": "NO"}) for i, function, manufacturer, mpn, quantity, state in data]


def contacts() -> list[dict[str, object]]:
    data = [
        ("LP-C01", "SPD3303X", "CH1 +", "Pomona 5934-2", "Alpha 3051 RD005", "red", "1000 mm CUT-LENGTH CANDIDATE", "J1.2", "AUX_5V_SAFE", "POSITIVE"),
        ("LP-C02", "SPD3303X", "CH1 -", "Pomona 5934-0", "Alpha 3051 BK005", "black", "1000 mm CUT-LENGTH CANDIDATE", "J1.1", "CTRL_GND", "RETURN"),
    ]
    return [common({"map_id": i, "source_equipment": source, "source_terminal": terminal, "source_connector": plug, "conductor": wire, "color": color, "candidate_cut_length": length, "destination_contact": destination, "net": net, "polarity": polarity, "continuity_result": "NOT EXECUTED", "short_to_other_contact_result": "NOT EXECUTED", "retention_result": "NOT EXECUTED"}) for i, source, terminal, plug, wire, color, length, destination, net, polarity in data]


def configuration() -> list[dict[str, object]]:
    data = [
        ("LP-CFG01", "supply model", "SIGLENT SPD3303X", "FROZEN CANDIDATE; RECEIPT REQUIRED"),
        ("LP-CFG02", "output channel", "CH1 only", "FROZEN CANDIDATE"),
        ("LP-CFG03", "operating mode", "independent", "FROZEN CANDIDATE"),
        ("LP-CFG04", "nominal voltage request", "5.000 V", "CANDIDATE ONLY - DO NOT APPLY UNTIL RECEIVED-BOARD LIMIT REVIEW"),
        ("LP-CFG05", "released voltage setpoint/tolerance", "SELECTION REQUIRED", "OPEN"),
        ("LP-CFG06", "released current limit", "SELECTION REQUIRED", "OPEN - ASSEMBLED LOAD/INRUSH/FAULT REVIEW REQUIRED"),
        ("LP-CFG07", "released OCP threshold", "SELECTION REQUIRED", "OPEN"),
        ("LP-CFG08", "DC return to protective earth", "NO INTENTIONAL BOND IN CANDIDATE BENCH FIXTURE", "QUALIFIED REFERENCE DISPOSITION OPEN; GROUNDED INSTRUMENTS CAN CHANGE THIS"),
        ("LP-CFG09", "unused channels", "CH2 OFF; CH3 OFF; no connections", "FROZEN CANDIDATE"),
        ("LP-CFG10", "default state before mating J1", "CH1 OUTPUT OFF", "MANDATORY; PHYSICAL CHECK NOT EXECUTED"),
    ]
    return [common({"configuration_id": i, "parameter": parameter, "candidate_value": value, "release_state": state, "approved_value": "NONE", "reviewer": "UNASSIGNED", "evidence_path": "NONE"}) for i, parameter, value, state in data]


def gates() -> list[dict[str, object]]:
    data = [
        ("LP-G01", "Received supply identity", "SPD3303X model/serial/firmware and intact mains lead recorded"),
        ("LP-G02", "Calibration and self-test", "in-date calibration basis and startup self-test recorded"),
        ("LP-G03", "Received controller identity", "board revision/serial/J1 orientation and input-population inspection recorded"),
        ("LP-G04", "Setpoint release", "qualified reviewer freezes voltage tolerance, current limit and OCP from received-board evidence"),
        ("LP-G05", "Reference release", "floating-output assumption, PE/DC-reference disposition and all grounded instruments reviewed"),
        ("LP-G06", "Cable assembly acceptance", "crimp height/pull, polarity, continuity, shorts, length, labels and strain relief pass"),
        ("LP-G07", "No-actuator boundary", "every carrier/bus/actuator connector physically absent and photographed"),
        ("LP-G08", "Pre-connection source check", "CH1 OFF while mating; then approved open-circuit voltage/OCP behavior measured before controller connection"),
        ("LP-G09", "Controlled connection authority", "named electrical reviewer signs this exact supply/cable/controller configuration"),
    ]
    return [common({"gate_id": i, "gate": gate, "objective_evidence": evidence, "result": "NOT EXECUTED", "evidence_path": "NONE", "performed_by": "UNASSIGNED", "witness": "UNASSIGNED"}) for i, gate, evidence in data]


def measurements() -> list[dict[str, object]]:
    data = [
        ("LP-M01", "cable positive continuity CH1+ to J1.2", "ohm", "SELECTION REQUIRED"),
        ("LP-M02", "cable return continuity CH1- to J1.1", "ohm", "SELECTION REQUIRED"),
        ("LP-M03", "cross-contact isolation J1.1 to J1.2", "Mohm", "SELECTION REQUIRED"),
        ("LP-M04", "open-circuit output voltage", "V", "SELECTION REQUIRED"),
        ("LP-M05", "current-limit/OCP response into approved electronic load", "A/ms", "SELECTION REQUIRED"),
        ("LP-M06", "CH1 return to PE resistance before instruments", "Mohm", "SELECTION REQUIRED"),
        ("LP-M07", "controller inrush", "A/ms", "SELECTION REQUIRED"),
        ("LP-M08", "controller steady-state current", "A", "SELECTION REQUIRED"),
        ("LP-M09", "controller 5 V input and internal 3.3 V rail", "V", "SELECTION REQUIRED"),
        ("LP-M10", "wire/connector temperature after approved dwell", "degC", "SELECTION REQUIRED"),
    ]
    return [common({"measurement_id": i, "measurement": measurement, "unit": unit, "acceptance_limit": limit, "instrument_id": "UNASSIGNED", "calibration_due": "UNRECORDED", "measured_value": "NONE", "result": "NOT EXECUTED", "evidence_path": "NONE"}) for i, measurement, unit, limit in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("LP-H01", "supply not received or calibrated", "receipt, serial, firmware, inspection and calibration evidence"),
        ("LP-H02", "cable not built", "controlled crimp/set-screw assembly and full inspection record"),
        ("LP-H03", "controller input protection/value not physically accepted", "received-board inspection and exact input/fuse/rail limit disposition"),
        ("LP-H04", "voltage/current/OCP limits not released", "as-built load, inrush, fault response and qualified electrical review"),
        ("LP-H05", "DC reference/grounded-instrument plan open", "approved drawing covering supply isolation, PE and every oscilloscope/USB/debug connection"),
        ("LP-H06", "strain relief/label materials unresolved", "exact materials, assembly drawing and pull/retention acceptance"),
        ("LP-H07", "physical tests unexecuted", "all nine gates and ten measurements completed against one frozen configuration"),
        ("LP-H08", "connection authority absent", "named qualified reviewer signs a separate connection release"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="660" viewBox="0 0 1280 660" role="img" aria-labelledby="title desc"><title id="title">HR-30 logic-only power fixture</title><desc id="desc">SIGLENT SPD3303X channel one connects through exact red and black cable parts to controller J1. Actuator connections remain absent.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:30px;font-weight:900}}.s{{font-size:15px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.hold{{fill:#fff0b5;stroke:#982520;stroke-width:4}}.red{{stroke:#b32025;stroke-width:8;fill:none}}.black{{stroke:#17243a;stroke-width:8;fill:none}}</style><rect width="1280" height="660" fill="#eef8ff"/><text class="h" x="48" y="54">Logic-only power fixture — physical results remain blank</text><rect class="box" x="48" y="120" width="270" height="250" rx="20"/><text x="82" y="170">SIGLENT SPD3303X</text><text class="s" x="82" y="207">CH1 · independent mode</text><text class="s" x="82" y="240">output OFF before mating</text><circle cx="280" cy="285" r="13" fill="#b32025"/><circle cx="280" cy="330" r="13" fill="#17243a"/><path class="red" d="M293 285H720"/><path class="black" d="M293 330H720"/><text class="s" x="390" y="267">5934-2 · 3051 RD005 · red</text><text class="s" x="390" y="355">5934-0 · 3051 BK005 · black</text><rect class="box" x="720" y="205" width="225" height="195" rx="20"/><text x="755" y="255">JST VHR-2N</text><text class="s" x="755" y="290">J1.2 AUX_5V_SAFE</text><text class="s" x="755" y="325">J1.1 CTRL_GND</text><rect class="box" x="1010" y="205" width="220" height="195" rx="20"/><text x="1045" y="255">STM32 controller</text><text class="s" x="1045" y="290">logic only</text><text class="s" x="1045" y="325">unreceived / untested</text><path d="M945 302H1010" stroke="#0b4f91" stroke-width="5"/><rect class="hold" x="390" y="475" width="840" height="120" rx="18"/><text x="430" y="520">Actuator power, carrier boards and all eight buses: PHYSICALLY ABSENT</text><text class="s" x="430" y="558">Setpoints, DC reference and connection remain unreleased.</text></svg>'''


def page(gate_rows: list[dict[str, object]], hold_rows: list[dict[str, object]]) -> str:
    gate_cards = "".join(f'<article><b>{html.escape(str(row["gate_id"]))}</b><h3>{html.escape(str(row["gate"]))}</h3><p>{html.escape(str(row["objective_evidence"]))}</p><strong>NOT EXECUTED</strong></article>' for row in gate_rows)
    hold_cards = "".join(f'<li><b>{html.escape(str(row["hold_id"]))}</b> {html.escape(str(row["unresolved_item"]))}</li>' for row in hold_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 logic power kit</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,70px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(28px,4vw,44px)}}h3{{font-size:22px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:white;border:2px solid var(--line);border-radius:16px;padding:19px}}article strong{{color:var(--red)}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:white}}object{{display:block;width:100%;min-width:900px}}a{{color:#075b9b;font-weight:800}}li{{margin:12px 0}}small{{font-size:14px}}@media(max-width:560px){{body{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>A real cable and supply candidate—still no permission to plug it in.</h1><p>The controller power boundary now has exact purchasable parts and an inspection path. Limits, grounding and every physical result remain open.</p></header><main><section class="grid"><article><div class="metric">8</div><p>candidate line items</p></article><article><div class="metric">2</div><p>fully mapped conductors</p></article><article><div class="metric">9</div><p>release gates</p></article><article><div class="metric">0</div><p>built cables or powered tests</p></article></section><section><h2>Connection boundary</h2><div class="scroll"><object data="logic-power-boundary.svg" type="image/svg+xml" aria-label="Logic-only power fixture wiring"></object></div></section><section><h2>Build and release records</h2><div class="grid"><article><h3>Exact parts</h3><p><a href="equipment-register.csv">Supply, JST, wire and plugs</a></p></article><article><h3>Two contacts</h3><p><a href="connector-contact-map.csv">Source-to-J1 map</a></p></article><article><h3>Settings</h3><p><a href="supply-configuration-register.csv">Candidate and unreleased values</a></p></article><article><h3>Measurements</h3><p><a href="measurement-register.csv">Blank physical record</a></p></article></div></section><section><h2>Nine gates before connection</h2><div class="grid">{gate_cards}</div></section><section class="panel"><h2>Open holds</h2><ul>{hold_cards}</ul><p><a href="logic-power-status.json">Machine-readable status</a> · <a href="primary-source-register.csv">Primary sources</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate_root() -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "logic_power_kit_package_present": True,
        "logic_power_exact_supply_candidate_selected": True,
        "logic_power_exact_cable_components_selected": True,
        "logic_power_cable_built": False,
        "logic_power_limits_released": False,
        "logic_power_reference_approved": False,
        "logic_power_connection_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LOGIC-POWER-KIT-P01-README-START -->", "<!-- HR30-LOGIC-POWER-KIT-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Logic-only controller power kit\n\nThe [interactive logic-power guide](electrical/logic-power-kit-p0.1/index.html) selects a SIGLENT SPD3303X, the exact two-contact JST boundary, red/black Alpha Wire conductors and Pomona banana plugs. The cable is unbuilt; voltage/current/OCP limits, DC-reference approval and every physical test remain open. It grants no connection or powered-work authority.\n{end}\n'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")
    page_path = WHOLE / "index.html"
    text = page_path.read_text(encoding="utf-8")
    start, end = "<!-- HR30-LOGIC-POWER-KIT-P01-START -->", "<!-- HR30-LOGIC-POWER-KIT-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="logic-power-kit"><h2>The controller now has a buildable logic-power fixture</h2><div class="grid"><article class="card"><div class="metric">8</div><p>exact or controlled candidate line items</p></article><article class="card"><div class="metric">2</div><p>mapped power contacts</p></article><article class="card hold"><div class="metric">0</div><p>built cables or powered tests</p></article></div><p><a href="electrical/logic-power-kit-p0.1/index.html">Open the interactive logic-power kit guide</a>. Setpoints, grounding and connection remain unreleased.</p></section>{end}'''
    marker = "<!-- HR30-STM32-BRINGUP-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>", 1)
    page_path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_rows, binding_rows = sources(), bindings()
    equipment_rows, contact_rows = equipment(), contacts()
    configuration_rows, gate_rows = configuration(), gates()
    measurement_rows, hold_rows = measurements(), holds()
    write_csv(OUT / "primary-source-register.csv", source_rows)
    write_csv(OUT / "source-binding.csv", binding_rows)
    write_csv(OUT / "equipment-register.csv", equipment_rows)
    write_csv(OUT / "connector-contact-map.csv", contact_rows)
    write_csv(OUT / "supply-configuration-register.csv", configuration_rows)
    write_csv(OUT / "setup-gate-register.csv", gate_rows)
    write_csv(OUT / "measurement-register.csv", measurement_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "primary_source_count": len(source_rows), "source_binding_count": len(binding_rows),
        "equipment_line_count": len(equipment_rows), "contact_map_count": len(contact_rows),
        "configuration_record_count": len(configuration_rows), "setup_gate_count": len(gate_rows),
        "measurement_count": len(measurement_rows), "open_hold_count": len(hold_rows),
        "exact_supply_candidate_selected": True, "exact_controller_connector_selected": True,
        "exact_conductor_and_source_plug_candidates_selected": True,
        "supply_received": False, "supply_calibration_verified": False, "cable_built": False,
        "output_voltage_setpoint_released": False, "current_limit_released": False,
        "ocp_threshold_released": False, "dc_reference_disposition_approved": False,
        "physical_measurements_executed": 0, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "logic-power-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "logic-power-boundary.svg").write_text(svg(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(gate_rows, hold_rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 logic-only power kit P0.1\n\n**{WARNING}**\n\nThis package defines exact candidate supply and cable hardware for the controller's J1 logic input. It records no assembly, measurement or authority. Use [index.html](index.html) for the interactive guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "logic-power-kit-source.py")
    manifest = [common({"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}) for path in sorted(OUT.rglob("*")) if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate_root()
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
