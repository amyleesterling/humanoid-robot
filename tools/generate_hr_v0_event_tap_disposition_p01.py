#!/usr/bin/env python3
"""Generate the R178 field-node observation disposition package."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical/analysis/hr-v0-event-tap-disposition-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-event-tap-disposition-p0.1"
WEB = ROOT / "release/hr-v0/event-tap-disposition-p0.1"
PROJECT = "hr-v0-event-tap-disposition-p0.1"
IDENTIFIER = "HR-V0-EVENT-TAP-DISP-P0.1"
REV = "R178 / P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")


NODES = [
    ("ETD-001", "SR1_S12", "Pilz input/start feed", "SR1:S12; S0:R-2; S1:TBD-R1", "50 mA DC; 0.2 A / 100 ms input inrush", "PERMANENT PASSIVE TAP NOT RELEASED", "Manufacturer allowable parallel load and tap-fault behavior are not published; protected/separate start wiring and physical noninterference evidence required"),
    ("ETD-002", "SR1_START_RETURN", "Pilz monitored RESET return", "SR1:S34; S1:TBD-R2", "50 mA DC; 0.2 A / 15 ms start inrush", "PERMANENT PASSIVE TAP NOT RELEASED", "Published manual does not define allowable parallel observer load or resulting falling-edge timing/error behavior"),
    ("ETD-003", "ARM_AFTER_S2", "Pilz monitored ARM/EDM chain", "S2:TBD-A2; K1:21", "50 mA DC; 0.2 A / 15 ms start/feedback inrush", "PERMANENT PASSIVE TAP NOT RELEASED", "Additional wiring enters a start/feedback path whose shorts are not detected; qualified fault-exclusion and waveform evidence required"),
    ("ETD-004", "K1_A1", "Schneider K1 24 VDC coil", "FSR1:2; K1:A1; return K1:A2/SAFETY_0V", "24 VDC; 5.4 W at 20 C; 0.7..1.25 Uc operational; 0.1..0.25 Uc dropout", "DIVIDER DESIGN HELD", "Built-in bidirectional suppressor is verified, but clamp voltage, external-tap limit, FSR1 and installed transient envelope remain unresolved"),
    ("ETD-005", "K2_A1", "Schneider K2 24 VDC coil", "FSR2:2; K2:A1; return K2:A2/SAFETY_0V", "24 VDC; 5.4 W at 20 C; 0.7..1.25 Uc operational; 0.1..0.25 Uc dropout", "DIVIDER DESIGN HELD", "Built-in bidirectional suppressor is verified, but clamp voltage, external-tap limit, FSR2 and installed transient envelope remain unresolved"),
    ("ETD-006", "EDM_K1_OUT", "Pilz EDM chain between mirror contacts", "K1:22; K2:21", "50 mA DC; 0.2 A / 15 ms feedback inrush", "PERMANENT PASSIVE TAP NOT RELEASED", "Parallel return path could affect EDM state or expose undetected short faults; manufacturer/application and physical fault evidence required"),
    ("ETD-007", "SRA1_START_RETURN", "Pilz monitored ARM/EDM return", "K2:22; SRA1:S34", "50 mA DC; 0.2 A / 15 ms start/feedback inrush", "PERMANENT PASSIVE TAP NOT RELEASED", "Published manual does not define allowable parallel observer load or resulting falling-edge/EDM behavior"),
]

SOURCES = [
    ("ETS-001", "Pilz", "PNOZ s4 operating manual", "21396-EN-23", "PDF metadata 2026-06-17; portal file 2026-06-22; accessed 2026-08-08", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "Input/start/feedback voltage and current, inrush pulses, start behavior, wiring/short-detection limitations"),
    ("ETS-002", "Pilz", "PNOZ s4 750104 live product record", "750104", "accessed 2026-08-10", "https://www.pilz.com/en-INT/eshop/product/750104", "Exact order-code identity, 24 VDC supply and product-level data"),
    ("ETS-003", "Schneider Electric", "LC1D25BD product data sheet", "SQD-LC1D25BD.PDF", "2017-09-13; accessed 2026-08-10", "https://iportal2.schneider-electric.com/Contents/docs/SQD-LC1D25BD.PDF", "24 VDC coil, 5.4 W, opening/closing time, dropout/operating limits, time constant and built-in bidirectional suppressor"),
    ("ETS-004", "Schneider Electric", "LC1D25BD live US product record", "LC1D25BD", "accessed 2026-08-10", "https://www.se.com/us/en/product/LC1D25BD/iec-contactor-tesys-deca-nonreversing-25a-15hp-at-480vac-up-to-100ka-sccr-3-phase-3-no-24vdc-coil-open-style/", "Current exact order-code identity and 24 VDC coil listing"),
    ("ETS-005", "Texas Instruments", "AMC3330 datasheet", "SBASA34B", "June 2020; revised August 2024; accessed 2026-08-10", "https://www.ti.com/lit/ds/symlink/amc3330.pdf", "Divider-design method, 100 uA example maximum cross current, input ranges, impedances, capacitance and absolute limits"),
]

HOLDS = [
    ("ETH-001", "ALLOWABLE PARALLEL LOAD", "Identifiable Pilz/Schneider application evidence or qualified analysis accepts maximum tap current and capacitance at every exact node"),
    ("ETH-002", "NODE ENVELOPE", "Minimum/nominal/maximum/reverse/transient voltage and source impedance measured with traceable equipment in the exact unmodified circuit"),
    ("ETH-003", "DIAGNOSTIC NONINTERFERENCE", "Tap-absent versus tap-present traces prove no input, monitored-start, EDM, simultaneity, dropout or diagnostic change"),
    ("ETH-004", "SINGLE-FAULT BEHAVIOR", "Every divider/protection open, short, drift, ground, harness and isolation fault is analyzed and physically injected where safe"),
    ("ETH-005", "PROTECTED ROUTING", "Start/feedback tap wiring, if retained, has accepted protected/separate installation and common-cause disposition"),
    ("ETH-006", "COIL TRANSIENT", "Installed K1/K2 A1-A2 waveform and built-in suppressor clamp envelope are measured across supply, temperature and opening cases"),
    ("ETH-007", "EXACT PARTS", "Resistors, protection, PCB, connectors, insulation, creepage/clearance and harness order codes are selected from current controlled data"),
    ("ETH-008", "TIMING UNCERTAINTY", "Divider/amplifier/DAQ threshold and skew are calibrated into the R174 uncertainty budget"),
    ("ETH-009", "QUALIFIED DISPOSITION", "Qualified electrical and functional-safety reviewers accept the exact temporary or permanent observation method"),
    ("ETH-010", "WORK AUTHORIZATION", "Separate controlled authorization defines guarded setup, actuator isolation, personnel, PPE, probes and abort conditions"),
]


def write_csv(path: Path, header: list[str], rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("tap_disposition_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = "2026-08-10"
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 EVENT-TAP DISPOSITION"
    model.PROJECT_SUBTITLE = "NO FIELD TAP OR AMC3330EVM CONNECTION RELEASED; ZERO SAFETY CREDIT"
    return model


def build_ecad() -> None:
    model = load_model()
    pn, Component = model.pn, model.Component
    groups = [(1, NODES[:3], "Pilz input, RESET and ARM nodes"), (2, NODES[3:5], "Schneider K1/K2 coil nodes"), (3, NODES[5:], "Pilz EDM return nodes")]
    sheets = []
    for sheet_no, group, title in groups:
        comps = []
        ys = [55, 105, 150] if len(group) == 3 else [70, 140]
        for y, node in zip(ys, group):
            node_id, net, role, terminals, published, disposition, reason = node
            source = Component(f"SRC{node_id[-1]}", f"EXISTING CIRCUIT NODE: {net}", [
                pn(f"SRC{node_id[-1]}", "FIELD", terminals, f"ETD_{node_id[-1]}_EXISTING", "right"),
            ], "EXISTING P1.15 LOGICAL NODE", role, "Project Button Electrical V3-P1.15", published, position=(62, y), width=65)
            hold = Component(f"HOLD{node_id[-1]}", "OBSERVATION BOUNDARY - NO CONNECTION", [
                pn(f"HOLD{node_id[-1]}", "NODE", net, f"ETD_{node_id[-1]}_EXISTING", "left"),
            ], disposition, reason, "R178 source/application review", "AMC3330EVM and field adapter remain physically absent.", position=(225, y), width=78)
            comps.extend([source, hold])
        sheet = model.Sheet(sheet_no, f"0{sheet_no}_{'pilz_inputs' if sheet_no == 1 else 'coil_nodes' if sheet_no == 2 else 'edm_returns'}.kicad_sch", title, "", compact=True)
        sheet.components = comps
        sheet.notes = []
        sheets.append(sheet)

    items = [component for sheet in sheets for component in sheet.components]
    counts = Counter(pin.net for component in items for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    root_uuid = model.uid("root-hr-v0-event-tap-disposition-p01")
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 event-tap disposition"))\n)\n', encoding="utf-8")
    root_text = model.root_schematic(root_uuid, sheets).replace("CONNECTED DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED", "DISPOSITION RECORD - NO FIELD TAP RELEASED")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(root_text, encoding="utf-8")
    for sheet in sheets:
        child_text = model.child_schematic(root_uuid, sheet, counts, wire_numbers).replace("CONNECTED DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED", "DISPOSITION RECORD - NO FIELD TAP RELEASED")
        (ECAD / sheet.filename).write_text(child_text, encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["reference", "terminal", "function", "net", "state"], [(component.ref, pin.number, pin.name, pin.net, component.status) for component in items for pin in component.pins])
    write_csv(ECAD / "bom.csv", ["reference", "manufacturer", "part_number", "quantity", "state"], [("SRC1-SRC7", "N/A", "existing V3-P1.15 logical nodes", "7", "REFERENCE ONLY"), ("HOLD1-HOLD7", "SELECTION REQUIRED", "NO CONNECTION", "7", "NO FIELD ADAPTER RELEASED")])
    validation, output = ECAD / "validation", ECAD / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    for stale in validation.glob("page-*.png"):
        stale.unlink()
    for stale in list(output.glob("*.svg")) + list(output.glob("*.pdf")):
        stale.unlink()
    cli = KICAD_ROOT / "bin/kicad-cli.exe"
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "pdf", "--output", str(output / f"{PROJECT}-preliminary.pdf"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "svg", "--output", str(output), str(ECAD / f"{PROJECT}.kicad_sch")],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("COMMAND: " + subprocess.list2cmdline(command) + f"\nEXIT: {result.returncode}\n{result.stdout}{result.stderr}")
        if result.returncode:
            raise RuntimeError(logs[-1])
    (validation / "kicad-cli.log").write_text("\n\n".join(logs), encoding="utf-8")
    for svg in output.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    for index, source in enumerate(sorted(p for p in output.glob("*.svg") if p.name != f"{PROJECT}.svg"), 1):
        source.rename(output / f"tap-disposition-{index}.svg")
    for local_settings in ECAD.glob("*.kicad_prl"):
        local_settings.unlink()
    manifest_rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            manifest_rows.append((path.relative_to(ECAD).as_posix(), str(path.stat().st_size), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    write_csv(ECAD / "SOURCE-MANIFEST.csv", ["path", "bytes", "sha256"], manifest_rows)


def build_package() -> None:
    write_csv(PKG / "node-disposition.csv", ["node_id", "net", "circuit_role", "exact_terminals", "published_electrical_data", "disposition", "reason"], NODES)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "title", "document", "revision_or_date", "official_locator", "engineering_use"], SOURCES)
    write_csv(PKG / "selection-holds.csv", ["hold_id", "topic", "closure_evidence"], HOLDS)
    write_csv(PKG / "calculation-screen.csv", ["screen_id", "quantity", "expression", "result", "status", "use_limit"], [
        ("ETC-001", "PNOZ steady-input current", "published directly", "50 mA", "SOURCE CONTROLLED", "Not an allowable observer-load specification"),
        ("ETC-002", "PNOZ observer-loading ratio", "I_tap / 50 mA", "SELECTION REQUIRED", "OPEN", "No acceptance percentage inferred"),
        ("ETC-003", "LC1D25BD arithmetic coil current", "5.4 W / 24 V", "0.225 A", "DERIVED SCREEN", "Not measured and not an observer-load allowance"),
        ("ETC-004", "coil observer-loading ratio", "I_tap / 0.225 A", "SELECTION REQUIRED", "OPEN", "No acceptance percentage inferred"),
        ("ETC-005", "AMC3330 divider cross current", "V_node / R_total", "SELECTION REQUIRED", "OPEN", "TI application example uses 100 uA maximum; Project Button limit not selected"),
        ("ETC-006", "AMC3330 input voltage", "V_node * R_sense / R_total", "SELECTION REQUIRED", "OPEN", "Must remain within +/-1 V linear and +/-1.25 V clipping limits for accepted envelope/faults"),
    ])
    (PKG / "package-status.json").write_text(json.dumps({
        "identifier": IDENTIFIER, "date": "2026-08-10", "status": WARNING,
        "node_count": 7, "pilz_path_node_count": 5, "coil_node_count": 2,
        "permanent_passive_tap_released_count": 0, "divider_design_released_count": 0,
        "authorized_connection_count": 0, "executed_physical_test_count": 0,
        "open_hold_count": len(HOLDS), "safety_function_credit": "ZERO",
        "r177_effect": "AMC3330EVM output-side candidate retained; all seven field adapter connections remain prohibited",
        "release_effect": "NONE",
    }, indent=2) + "\n", encoding="utf-8")


def build_web() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    cards = []
    for node in NODES:
        node_id, net, role, terminals, published, disposition, reason = node
        kind = "coil" if net in {"K1_A1", "K2_A1"} else "pilz"
        cards.append(f'''<article class="card" data-kind="{kind}"><div class="eyebrow">{escape(node_id)} · {kind.upper()}</div><h2>{escape(net)}</h2><p><strong>{escape(role)}</strong></p><dl><dt>Exact terminals</dt><dd>{escape(terminals)}</dd><dt>Published data</dt><dd>{escape(published)}</dd><dt>Disposition</dt><dd class="held">{escape(disposition)}</dd></dl><p>{escape(reason)}</p></article>''')
    source_items = "".join(f'<li><a href="{escape(s[5])}">{escape(s[1])}: {escape(s[2])} ({escape(s[3])})</a> — {escape(s[4])}</li>' for s in SOURCES)
    svg_links = "".join(f'<a class="diagram" href="../../../../electrical/kicad/{PROJECT}/output/tap-disposition-{i}.svg">Open KiCad sheet {i}</a>' for i in range(1, 4))
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 event-tap disposition P0.1</title><style>
:root{{--sky:#dff3ff;--blue:#092e66;--mid:#1267a5;--gold:#f5bd2e;--ink:#10213a;--paper:#fff;--hold:#8a2d0b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header,main,footer{{max-width:1180px;margin:auto;padding:24px}}.warning{{background:var(--blue);color:#fff;border-bottom:6px solid var(--gold);font-weight:800;padding:16px 24px}}h1{{font-size:clamp(34px,6vw,70px);line-height:1.02;margin:.25em 0}}h2{{font-size:25px;margin:.25em 0}}.lead{{font-size:20px;max-width:850px}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}}button,.diagram{{font-family:inherit;font-size:16px;line-height:1.2;font-weight:700;border:2px solid var(--blue);border-radius:999px;padding:12px 18px;background:#fff;color:var(--blue);cursor:pointer;text-decoration:none}}button[aria-pressed="true"]{{background:var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}}.card{{background:var(--paper);border:2px solid var(--blue);border-radius:18px;padding:20px;box-shadow:6px 6px 0 var(--blue)}}.eyebrow,dt{{font-size:14px;font-weight:800;color:var(--mid);text-transform:uppercase;letter-spacing:.04em}}dd{{margin:0 0 12px}}.held{{color:var(--hold);font-weight:900}}section{{margin:36px 0}}.diagram-row{{display:flex;flex-wrap:wrap;gap:12px}}li{{margin:10px 0}}footer{{font-size:14px}}[hidden]{{display:none!important}}@media(max-width:520px){{header,main,footer{{padding:18px}}.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="warning">{escape(WARNING)}</div><header><div class="eyebrow">R178 · HR-V0-EVENT-TAP-DISP-P0.1</div><h1>Seven nodes. Zero released taps.</h1><p class="lead"><strong>No field tap is released.</strong> The catalog evidence is sufficient to classify each proposed observation point, but not to authorize a permanent passive tap. This guide shows exactly why.</p></header><main><div class="controls" aria-label="Filter nodes"><button data-filter="all" aria-pressed="true">All 7</button><button data-filter="pilz" aria-pressed="false">Pilz paths</button><button data-filter="coil" aria-pressed="false">Coil nodes</button></div><div class="grid">{''.join(cards)}</div><section><h2>Native KiCad disposition drawings</h2><p>These drawings deliberately end every observation branch at a held no-connect boundary. They are disposition records, not wiring instructions.</p><div class="diagram-row">{svg_links}</div></section><section><h2>What closes the hold</h2><ol>{''.join(f'<li><strong>{escape(h[1])}:</strong> {escape(h[2])}</li>' for h in HOLDS)}</ol></section><section><h2>Primary manufacturer sources</h2><ul>{source_items}</ul></section></main><footer>{escape(WARNING)} · No DAQ, EVM, adapter, or test host receives safety credit.</footer><script>
const buttons=[...document.querySelectorAll('button[data-filter]')],cards=[...document.querySelectorAll('.card')];buttons.forEach(b=>b.addEventListener('click',()=>{{buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));cards.forEach(c=>c.hidden=b.dataset.filter!=='all'&&c.dataset.kind!==b.dataset.filter)}}));
</script></body></html>'''
    (WEB / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    build_package()
    build_ecad()
    build_web()
    print(f"generated {IDENTIFIER}: 7 node dispositions, 0 released taps, native ERC artifacts")
    print(WARNING)


if __name__ == "__main__":
    main()
