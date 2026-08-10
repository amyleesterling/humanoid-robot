#!/usr/bin/env python3
"""Generate the R184 HR-V0 Q4X temporary interface-box candidate."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/q4x-box-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-q4x-box-p0.1"
WEB = ROOT / "release/hr-v0/q4x-box-p0.1"
DOC = ROOT / "docs/hr-v0-q4x-box-p0.1.md"
FORM = ROOT / "tests/forms/hr-v0-q4x-box-assembly-inspection-p0.1.csv"
PROJECT = "hr-v0-q4x-box-p0.1"
IDENTIFIER = "HR-V0-Q4X-BOX-P0.1"
REV = "R184 / P0.1"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - BENCH R&D CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")


def write_csv(path: Path, header: list[str], rows: list[tuple[object, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([*header, "warning"])
        for row in rows:
            writer.writerow([*row, WARNING])


PARTS = [
    ("QB-001", "PTCB1", "Phoenix Contact", "PTCB E1 24DC/0.1A NO", "1464484", "1", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Fixed 0.1 A electronic branch protection; remote contact DNP"),
    ("QB-002", "XQ1.1", "Phoenix Contact", "PT 2,5-QUATTRO", "3209578", "1", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Four-connection Q4X 0 V terminal"),
    ("QB-003", "XQ1.2-XQ1.6", "Phoenix Contact", "PT 2,5", "3209510", "5", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Protected positive, remote park, analog pair and drain park"),
    ("QB-004", "terminal covers", "Phoenix Contact", "D-ST 2,5-QUATTRO / D-ST 2,5", "3030514 / 3030417", "1 / 1", "EXACT EVALUATION CANDIDATES / NOT RELEASED", "End covers; received fit/orientation required"),
    ("QB-005", "rail ends", "Phoenix Contact", "CLIPFIX 35", "3022218", "2", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "DIN-rail end brackets"),
    ("QB-006", "rail", "Phoenix Contact", "NS 35/7,5 PERF 500MM", "1207650", "1 cut to 150.0 mm candidate", "EXACT EVALUATION CANDIDATE / CUT NOT RELEASED", "Cut, deburr, edge clearance and retention require inspection"),
    ("QB-007", "terminal markers", "Phoenix Contact", "UCT-TM 5 / UCT-TM 6", "0828734 / 0828736", "SELECTION REQUIRED", "EXACT FAMILY / PRINT QUANTITY NOT RELEASED", "Human-readable terminal and breaker labels"),
    ("QB-008", "FERR-22", "Phoenix Contact", "AI 0,34-8 TQ", "3203066", "SELECTION REQUIRED", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "22 AWG Banner cordset conductors"),
    ("QB-009", "FERR-18", "Phoenix Contact", "AI 0,75-8 WH", "3201110", "SELECTION REQUIRED", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "18 AWG source and internal conductors"),
    ("QB-010", "TOOL1", "Phoenix Contact", "CRIMPFOX 6", "1212034", "1", "EXACT PROCESS-TOOL CANDIDATE / NOT RELEASED", "0.25-6 mm2 ferrule crimp tool; received condition and trial crimps held"),
    ("QB-011", "ENC1", "Hammond Manufacturing", "PJ1084T", "PJ1084T", "1", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "257 x 210 x 105 mm fiberglass twist-latch enclosure"),
    ("QB-012", "PANEL1", "Hammond Manufacturing", "fiberglass inner panel", "14F0907", "1", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "222.25 x 174.75 mm nonconductive panel"),
    ("QB-013", "G1/G2", "LAPP", "SKINTOP ST-M 12x1.5", "53111000", "2", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "3.5-7 mm cable clamping range"),
    ("QB-014", "G1N/G2N", "LAPP", "SKINTOP GMP-GL-M 12x1.5 SGY", "53119000", "2", "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Counter nuts for thin-wall through holes"),
    ("QB-015", "CBL-PS1", "Alpha Wire", "2C 18 AWG unshielded control cable", "881802", "length and package SELECTION REQUIRED", "EXACT CABLE DESIGNATION / PROCUREMENT FORM NOT RELEASED", "Nominal OD 0.222 in; black/red conductors"),
    ("QB-016", "CBL-Q4X1", "Banner Engineering", "BC-M12F5-22-2-SF", "815158", "1", "R183 EXACT EVALUATION CANDIDATE / NOT RELEASED", "2 m, five 22 AWG conductors, M12 female; drain remains parked"),
    ("QB-017", "Q4X1", "Banner Engineering", "Q4XFULAF110-Q8", "97540", "1", "R183 EXACT EVALUATION CANDIDATE / NOT RELEASED", "0-10 V analog laser displacement witness; zero safety credit"),
    ("QB-018", "PS-Q4X1", "Keithley / Tektronix", "2220-30-1 channel 1 only", "2220-30-1", "1", "R183 EXACT EVALUATION CANDIDATE / NOT RELEASED", "24.0 V candidate; current limit SELECTION REQUIRED"),
    ("QB-019", "TEST1", "SELECTION REQUIRED", "isolated analog lead fixture", "SELECTION REQUIRED", "1", "SELECTION REQUIRED / NO PHYSICAL CONNECTION RELEASED", "Must mate TIVPMX10X without exposed conductive access"),
]


SOURCES = [
    ("QBS-001", "Phoenix Contact", "PTCB E1 24DC/0.1A NO product page", "live page; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/electronic-circuit-breaker-ptcb-e1-24dc-01a-no-1464484", "Exact part, 10-30 V, fixed 0.1 A, 300 A short-circuit switching capacity, typical current limitation, shutdown behavior, terminals and dimensions"),
    ("QBS-002", "Phoenix Contact", "PT 2,5-QUATTRO product data", "generated 2026-06-27; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/multi-conductor-terminal-block-pt-25-quattro-3209578?type=pdf", "Exact four-connection terminal and conductor range"),
    ("QBS-003", "Phoenix Contact", "AI 0,34-8 TQ product data", "generated 2026-06-11; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/ferrule-ai-034-8-tq-3203066?type=pdf", "Exact 22 AWG ferrule, 8 mm contact range and 10 mm strip"),
    ("QBS-004", "Phoenix Contact", "AI 0,75-8 WH product page", "live page; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/ferrule-ai-075-8-wh-3201110", "Exact 18 AWG ferrule, 8 mm contact range and 11 mm strip"),
    ("QBS-005", "Phoenix Contact", "CRIMPFOX 6 product page", "live page; checked 2026-08-10", "https://www.phoenixcontact.com/en-us/products/crimping-tool-crimpfox-6-1212034", "Exact ferrule tool and 0.25-6 mm2 range"),
    ("QBS-006", "Hammond Manufacturing", "PJ1084T product page", "live page; checked 2026-08-10", "https://www.hammfg.com/part/PJ1084T", "Exact fiberglass enclosure and external dimensions"),
    ("QBS-007", "Hammond Manufacturing", "PJ-series enclosure page", "live page; checked 2026-08-10", "https://www.hammfg.com/electrical/products/non-metallic/pj", "Component enclosure construction and ratings; no completed-box rating inferred"),
    ("QBS-008", "Hammond Manufacturing", "14-series inner-panel page", "live page; checked 2026-08-10", "https://www.hammfg.com/electrical/products/accessories/14p", "Exact 14F0907 fiberglass inner panel and dimensions"),
    ("QBS-009", "LAPP", "SKINTOP ST-M 12x1.5 product page/data", "data sheet valid 2025-01-24; checked 2026-08-10", "https://www.lapp.com/en_US/us/skintop-st-m/skintop-str-m/p/53111000", "Exact gland, M12x1.5, 3.5-7 mm range and component ratings"),
    ("QBS-010", "LAPP", "SKINTOP GMP-GL-M 12x1.5 product page", "live page; checked 2026-08-10", "https://www.lapp.com/en_US/us/skintop-gmp-gl-m/p/53119000", "Exact thin-wall lock nut"),
    ("QBS-011", "Alpha Wire", "881802 product page", "live page; checked 2026-08-10", "https://www.alphawire.com/en/products/cable/alpha-essentials/communication-and-control-cable/881802", "2C 18 AWG unshielded cable, black/red conductors, nominal/max OD and temperature/rating data"),
    ("QBS-012", "Banner Engineering", "BC-M12F5-22-2-SF product page", "live page; checked 2026-08-10", "https://www.bannerengineering.com/us/en/products/part.815158.html", "Exact 2 m cordset identity, 22 AWG conductors, 5.59 mm OD and floating drain wording"),
    ("QBS-013", "Banner Engineering", "Q4X analog sensor manual", "185624 Rev J; 2026-03-27", "https://info.bannerengineering.com/cs/groups/public/documents/literature/185624.pdf", "Exact pins, 12-30 V supply, less-than-675 mW consumption excluding load, 0-10 V output and 10 minute warm-up"),
    ("QBS-014", "Keithley / Tektronix", "Series 2200 specifications", "2220S-905-01 Rev B; 2013-12", "https://download.tek.com/manual/2220S-905-01_B_Dec_2013_Spec.pdf", "2220-30-1 isolated 0-30 V / 0-1.5 A channel capability; received instrument remains required"),
]


HOLDS = [
    ("QBH-001", "SOURCE SETTING", "Exact PS-Q4X1 current-limit setting, lock method, startup/inrush behavior and current-limit transient accepted on received equipment"),
    ("QBH-002", "PROTECTION", "Received PTCB identity, orientation, terminal inspection, trip/overload/short behavior and no-backfeed fault campaign accepted"),
    ("QBH-003", "CABLE", "Exact Alpha Wire procurement form, installed length, routing, bend radius, stripping, ferrule count and received cable identity released"),
    ("QBH-004", "ENCLOSURE", "Dimensioned hole/rail layout, gland torque, wall thickness, spacing, label plan and completed-enclosure environmental rating reviewed"),
    ("QBH-005", "RAIL", "150.0 mm rail cut, deburr, edge clearance, end-bracket retention and isolated mounting on received 14F0907 panel inspected"),
    ("QBH-006", "SHIELD", "Cordset drain verified and parked only at XQ1.6 with no bridge, PE, rail, chassis or 0 V connection; analog noise evidence accepted"),
    ("QBH-007", "GROUNDING", "No-PE-entry/no-bond fiberglass-box proposal accepted for Boston use; isolated DIN rail and all domain boundaries verified unpowered"),
    ("QBH-008", "TERMINATIONS", "Received terminal/ferrule/tool identities, strip lengths, crimp samples, insertion, retention and second-person wire trace accepted"),
    ("QBH-009", "THERMAL", "Installed ambient, closed-box rise, device derating and abnormal-condition temperatures accepted"),
    ("QBH-010", "TEST INTERFACE", "Exact guarded TIVPMX10X analog lead fixture selected; no exposed conductive access and no alternate ground path"),
    ("QBH-011", "SITE", "Boston build/test site, jurisdiction, supply connection practice, guarding and qualified electrical review accepted"),
    ("QBH-012", "WORK AUTHORITY", "Controlled receiving, assembly, unpowered continuity/isolation and later powered-test authorizations issued separately"),
    ("QBH-013", "CALIBRATION", "R183 received Q4X chain, target, support, configuration, calibration, uncertainty and no-motion threshold accepted"),
    ("QBH-014", "QUALIFIED REVIEW", "Qualified electrical and functional-safety reviewers accept the instrumentation boundary; zero safety credit retained"),
]


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("q4x_box_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REV
    model.DATE = DATE
    model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 Q4X TEMPORARY INTERFACE BOX"
    model.PROJECT_SUBTITLE = "STANDALONE 24 V INSTRUMENTATION DOMAIN; NO ROBOT-CIRCUIT CONNECTION; ZERO SAFETY CREDIT"
    return model


def build_ecad() -> None:
    model = load_model()
    pn, Component = model.pn, model.Component

    ps = Component("PS1", "Keithley 2220-30-1 CH1 ONLY", [
        pn("PS1", "CH1+", "0-30 V SOURCE POSITIVE", "Q4X_SRC_24V_RAW", "right"),
        pn("PS1", "CH1-", "ISOLATED SOURCE RETURN", "Q4X_0V", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "24.0 V candidate. Current-limit value, lock and received tests remain SELECTION REQUIRED. CH2 disabled and unconnected.", "Tektronix 2220S-905-01 Rev B", "Zero safety credit; no robot-domain connection.", position=(42, 95), width=55)
    cable = Component("CBLPS1", "Alpha Wire 881802 - 2C 18 AWG", [
        pn("CBLPS1", "PS-RD", "RED AT SUPPLY", "Q4X_SRC_24V_RAW", "left"),
        pn("CBLPS1", "BOX-RD", "RED AT BOX", "Q4X_SRC_24V_RAW", "right"),
        pn("CBLPS1", "PS-BK", "BLACK AT SUPPLY", "Q4X_0V", "left"),
        pn("CBLPS1", "BOX-BK", "BLACK AT BOX", "Q4X_0V", "right"),
    ], "EXACT DESIGNATION / LENGTH AND PROCUREMENT FORM NOT RELEASED", "Unshielded 2C 18 AWG; nominal 5.64 mm OD fits the selected 3.5-7 mm gland arithmetically. Received OD and gland retention required.", "Alpha Wire live 881802 page", "Cable is a pass-through assembly representation.", position=(112, 95), width=55)
    ptcb = Component("PTCB1", "Phoenix PTCB E1 24DC/0.1A NO / 1464484", [
        pn("PTCB1", "IN+", "SOURCE POSITIVE", "Q4X_SRC_24V_RAW", "left"),
        pn("PTCB1", "IN-", "SOURCE RETURN", "Q4X_0V", "left"),
        pn("PTCB1", "OUT", "PROTECTED OUTPUT", "Q4X_24V_PROTECTED", "right"),
        pn("PTCB1", "13", "REMOTE NO DNP", "INTENTIONALLY_UNCONNECTED_PTCB1_13", "right"),
        pn("PTCB1", "14", "REMOTE NO DNP", "INTENTIONALLY_UNCONNECTED_PTCB1_14", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Fixed 0.1 A electronic breaker. Typical 1.2x active limiting is not treated as a guaranteed hard ceiling. Remote contact is deliberately unwired.", "Phoenix Contact live page checked 2026-08-10", "300 A switching capacity; source catalog maximum 1.5 A does not trigger the catalog backup-fuse condition, but installed fault tests remain mandatory.", position=(182, 95), width=70)
    x0 = Component("XQ1.1", "Phoenix PT 2,5-QUATTRO / 3209578", [
        pn("XQ1.1", "A", "SOURCE RETURN", "Q4X_0V", "left"), pn("XQ1.1", "B", "PTCB IN-", "Q4X_0V", "left"),
        pn("XQ1.1", "C", "Q4X PIN 3 BLUE", "Q4X_0V", "right"), pn("XQ1.1", "D", "EMPTY TEST PORT", "Q4X_0V", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "One potential, four push-in connections. Port D has no conductor in the candidate assembly.", "Phoenix 3209578 product data", "No bridge or PE bond.", position=(252, 80), width=58)
    xp = Component("XQ1.2", "Phoenix PT 2,5 / 3209510", [
        pn("XQ1.2", "A", "PTCB OUT", "Q4X_24V_PROTECTED", "left"), pn("XQ1.2", "B", "Q4X PIN 1 BROWN", "Q4X_24V_PROTECTED", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Protected-positive feed-through terminal.", "Phoenix 3209510 product data", "No bridge.", position=(252, 120), width=58)
    sheet1 = model.Sheet(1, "01_source_and_protection.kicad_sch", "Isolated source, cable and 0.1 A branch protection", "Exact connected candidate; source setting and physical proof remain held.", compact=True)
    sheet1.components = [ps, cable, ptcb, x0, xp]
    sheet1.notes = [
        "PTCB1 typical 1.2 x IN limiting is catalog behavior, not a guaranteed hard fault-current ceiling.",
        "No upstream fuse value is released. Catalog backup-fuse condition is not triggered by the 1.5 A source rating, but received fault tests and qualified review remain mandatory.",
        "PTCB1 remote NO terminals 13/14 are DNP and physically unwired.",
    ]

    cord = Component("CBLQ4X1", "Banner BC-M12F5-22-2-SF / 815158", [
        pn("CBLQ4X1", "1-BN", "BROWN / PIN 1", "Q4X_24V_PROTECTED", "right"),
        pn("CBLQ4X1", "3-BU", "BLUE / PIN 3", "Q4X_0V", "right"),
        pn("CBLQ4X1", "2-WH", "WHITE / PIN 2", "Q4X_REMOTE_PARK", "right"),
        pn("CBLQ4X1", "4-BK", "BLACK / PIN 4", "Q4X_ANALOG_OUT", "right"),
        pn("CBLQ4X1", "5-GY", "GRAY / PIN 5", "Q4X_ANALOG_GND", "right"),
        pn("CBLQ4X1", "DRN", "FLOATING DRAIN", "Q4X_SHIELD_PARK", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "2 m 5x22 AWG cordset. Manufacturer wording says shield floating to drain; drain parks only at XQ1.6.", "Banner part 815158 live page", "No PE, rail, chassis or 0 V bond.", position=(55, 100), width=66)
    sensor = Component("Q4X1", "Banner Q4XFULAF110-Q8 / 97540", [
        pn("Q4X1", "1", "12-30 VDC", "Q4X_24V_PROTECTED", "left"), pn("Q4X1", "3", "DC COMMON", "Q4X_0V", "left"),
        pn("Q4X1", "2", "REMOTE INPUT", "Q4X_REMOTE_PARK", "left"), pn("Q4X1", "4", "0-10 V OUTPUT", "Q4X_ANALOG_OUT", "right"),
        pn("Q4X1", "5", "ANALOG GROUND", "Q4X_ANALOG_GND", "right"),
    ], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Independent displacement witness only. Pin 2 is parked and must be configured inactive. Pin 5 is not inferred to be identical to pin 3.", "Banner manual 185624 Rev J", "Less than 675 mW excluding load; zero safety credit.", position=(135, 100), width=64)
    park = Component("XQ1.3", "Phoenix PT 2,5 / 3209510", [pn("XQ1.3", "A", "Q4X PIN 2 WHITE", "Q4X_REMOTE_PARK", "left"), pn("XQ1.3", "B", "NO EXTERNAL CONDUCTOR", "Q4X_REMOTE_PARK", "right")], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Insulated remote-input parking potential; no external drive.", "Phoenix 3209510 product data", "Label REMOTE PARK - DO NOT CONNECT.", position=(218, 58), width=62)
    ao = Component("XQ1.4", "Phoenix PT 2,5 / 3209510", [pn("XQ1.4", "A", "Q4X PIN 4 BLACK", "Q4X_ANALOG_OUT", "left"), pn("XQ1.4", "B", "ISOLATED PROBE POSITIVE", "Q4X_ANALOG_OUT", "right")], "EXACT EVALUATION CANDIDATE / TEST FIXTURE OPEN", "Analog output feed-through.", "Phoenix 3209510 product data", "No chassis-referenced probe.", position=(218, 88), width=62)
    ag = Component("XQ1.5", "Phoenix PT 2,5 / 3209510", [pn("XQ1.5", "A", "Q4X PIN 5 GRAY", "Q4X_ANALOG_GND", "left"), pn("XQ1.5", "B", "ISOLATED PROBE NEGATIVE", "Q4X_ANALOG_GND", "right")], "EXACT EVALUATION CANDIDATE / TEST FIXTURE OPEN", "Analog-ground feed-through; not bonded to Q4X 0 V by project wiring.", "Phoenix 3209510 product data", "No PE/rail/chassis bond.", position=(218, 118), width=62)
    shield = Component("XQ1.6", "Phoenix PT 2,5 / 3209510", [pn("XQ1.6", "A", "CORDSET DRAIN", "Q4X_SHIELD_PARK", "left"), pn("XQ1.6", "B", "NO CONDUCTOR / NO BRIDGE", "Q4X_SHIELD_PARK", "right")], "EXACT EVALUATION CANDIDATE / NOT RELEASED", "Drain parking terminal only.", "Phoenix 3209510 product data", "Label SHIELD PARK - NO PE/0V CONNECTION.", position=(218, 148), width=62)
    test = Component("TEST1", "ISOLATED ANALOG LEAD FIXTURE - SELECTION REQUIRED", [pn("TEST1", "+", "TIVPMX10X POSITIVE", "Q4X_ANALOG_OUT", "left"), pn("TEST1", "-", "TIVPMX10X NEGATIVE", "Q4X_ANALOG_GND", "left")], "SELECTION REQUIRED / NO CONNECTION RELEASED", "Guarded physical lead fixture, touch protection, strain relief and isolation are unresolved.", "No manufacturer selected", "TIVP02 observation system receives zero safety credit.", position=(270, 103), width=72)
    sheet2 = model.Sheet(2, "02_sensor_and_signal.kicad_sch", "Q4X pins, parking terminals and isolated analog boundary", "Every physical pin is named; TEST1 remains an explicit unresolved interface.", compact=True)
    sheet2.components = [cord, sensor, park, ao, ag, shield, test]
    sheet2.notes = [
        "XQ1.6 parks the floating drain only: no bridge, PE, rail, chassis or 0 V connection.",
        "Q4X pin 5 analog ground is not project-bonded to pin 3 DC common.",
        "TEST1 remains SELECTION REQUIRED; this sheet is not a wiring or connection release.",
    ]
    sheets = [sheet1, sheet2]
    items = [component for sheet in sheets for component in sheet.components]
    counts = Counter(pin.net for component in items for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, counts)
    ECAD.mkdir(parents=True, exist_ok=True)
    for stale in ECAD.glob("*.kicad_sch"):
        stale.unlink()
    project_data = {"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}}
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1) for component in items]
    (ECAD / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (ECAD / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 Q4X temporary interface-box candidate"))\n)\n', encoding="utf-8")
    root_uuid = model.uid("root-hr-v0-q4x-box-p01")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    write_csv(ECAD / "connector-schedule.csv", ["sheet", "reference", "terminal", "function", "net", "state"], [(sheet.filename, component.ref, pin.number, pin.name, pin.net, component.status) for sheet in sheets for component in sheet.components for pin in component.pins])
    nets: dict[str, list[str]] = {}
    for sheet in sheets:
        for component in sheet.components:
            for pin in component.pins:
                nets.setdefault(pin.net, []).append(f"{sheet.filename}:{component.ref}:{pin.number}")
    write_csv(ECAD / "net-schedule.csv", ["net", "connection_count", "connections"], [(net, len(points), " | ".join(points)) for net, points in sorted(nets.items())])
    write_csv(ECAD / "bom.csv", ["reference", "value", "quantity", "state", "source"], [(component.ref, component.value, component.quantity, component.status, component.datasheet) for component in items])
    write_csv(ECAD / "wire-number-table.csv", ["wire_number", "sheet", "reference", "terminal", "net"], [(wire_numbers[(component.ref, pin.number)], sheet.filename, component.ref, pin.number, pin.net) for sheet in sheets for component in sheet.components for pin in component.pins if counts[pin.net] > 1])

    validation, output = ECAD / "validation", ECAD / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    for stale in list(output.glob("*.svg")) + list(output.glob("*.pdf")):
        stale.unlink()
    commands = [
        [str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(ECAD / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "svg", "--output", str(output), str(ECAD / f"{PROJECT}.kicad_sch")],
    ]
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
            raise SystemExit(result.returncode)
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    children = sorted(path for path in output.glob("*.svg") if path.name != f"{PROJECT}.svg")
    expected_exports = ["01_source_and_protection.svg", "02_sensor_and_signal.svg"]
    if len(children) != len(expected_exports):
        raise RuntimeError(f"expected {len(expected_exports)} child SVG exports, found {len(children)}")
    for source, target_name in zip(children, expected_exports):
        source.replace(output / target_name)
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(ECAD).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (ECAD / "SOURCE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n"); writer.writerow(["file", "sha256"]); writer.writerows(rows)


def write_package() -> None:
    PKG.mkdir(parents=True, exist_ok=True)
    write_csv(PKG / "candidate-bom.csv", ["item_id", "reference", "manufacturer", "description", "part_or_item", "quantity", "state", "use_limit"], PARTS)
    write_csv(PKG / "source-register.csv", ["source_id", "manufacturer", "document", "revision_or_date", "official_locator", "controlled_use"], SOURCES)
    write_csv(PKG / "closure-holds.csv", ["hold_id", "scope", "evidence_required"], HOLDS)
    write_csv(PKG / "enclosure-layout-candidate.csv", ["record_id", "item", "candidate_location_or_dimension", "state", "evidence_required"], [
        ("LAY-001", "ENC1", "PJ1084T external 257 x 210 x 105 mm", "CATALOG BOUND / NOT RELEASED", "received dimensional inspection"),
        ("LAY-002", "PANEL1", "14F0907 fiberglass 222.25 x 174.75 mm", "CATALOG BOUND / NOT RELEASED", "received hole pattern and enclosure fit"),
        ("LAY-003", "DIN rail", "150.0 mm horizontal centered candidate", "DIMENSION CANDIDATE / NOT RELEASED", "dimensioned drawing, cut/deburr and installed retention"),
        ("LAY-004", "G1 source cable", "M12 through hole on enclosure lower face; exact coordinate SELECTION REQUIRED", "SELECTION REQUIRED", "drill template, wall thickness, spacing and tool access"),
        ("LAY-005", "G2 sensor cordset", "M12 through hole on enclosure lower face; exact coordinate SELECTION REQUIRED", "SELECTION REQUIRED", "drill template, bend radius and separation"),
        ("LAY-006", "PTCB1 + XQ1", "single rail row; PTCB then return/protected/park/signal/drain terminals", "ARRANGEMENT CANDIDATE / NOT RELEASED", "received dimensions, covers, markers and wire-bend proof"),
        ("LAY-007", "metal DIN rail", "mechanically isolated on fiberglass panel; no PE wire in candidate", "QUALIFIED REVIEW REQUIRED", "unpowered isolation, site/jurisdiction and abnormal-condition review"),
    ])
    write_csv(PKG / "calculation-register.csv", ["calculation_id", "expression", "result", "classification", "limit"], [
        ("CAL-QB-001", "0.675 W / 24.0 V", "28.125 mA", "catalog upper-bound screen", "Q4X consumption excludes load"),
        ("CAL-QB-002", "28.125 mA + 5 mA", "33.125 mA", "candidate steady-source screen", "includes PTCB typical closed-circuit current; excludes inrush"),
        ("CAL-QB-003", "0.100 A / 0.033125 A", "3.019", "nominal ratio only", "not inrush margin and not a safety factor"),
        ("CAL-QB-004", "0.222 in x 25.4", "5.6388 mm nominal", "Alpha 881802 gland-fit screen", "received cable OD required"),
        ("CAL-QB-005", "5.59 mm inside 3.5-7 mm", "2.09 mm above min; 1.41 mm below max", "Banner cordset gland-fit screen", "installed retention required"),
        ("CAL-QB-006", "1.5 A source catalog maximum < 300 A PTCB switching capacity", "catalog backup-fuse trigger not met", "catalog coordination screen", "does not release source setting, fault test, or completed assembly"),
    ])
    write_csv(PKG / "connection-and-termination-schedule.csv", ["record_id", "from", "via", "to", "conductor_or_terminal", "candidate_state"], [
        ("CON-001", "PS1 CH1+", "CBLPS1 red; G1", "PTCB1 IN+", "Alpha 881802 red, 18 AWG; AI 0,75-8 WH", "NOT RELEASED"),
        ("CON-002", "PS1 CH1-", "CBLPS1 black; G1", "XQ1.1 A", "Alpha 881802 black, 18 AWG; AI 0,75-8 WH", "NOT RELEASED"),
        ("CON-003", "XQ1.1 B", "internal black jumper", "PTCB1 IN-", "Alpha 881802 black conductor; AI 0,75-8 WH", "NOT RELEASED"),
        ("CON-004", "PTCB1 OUT", "internal red jumper", "XQ1.2 A", "Alpha 881802 red conductor; AI 0,75-8 WH", "NOT RELEASED"),
        ("CON-005", "XQ1.2 B", "CBLQ4X1 brown; G2", "Q4X1 pin 1", "Banner 22 AWG; AI 0,34-8 TQ at terminal", "NOT RELEASED"),
        ("CON-006", "XQ1.1 C", "CBLQ4X1 blue; G2", "Q4X1 pin 3", "Banner 22 AWG; AI 0,34-8 TQ at terminal", "NOT RELEASED"),
        ("CON-007", "Q4X1 pin 2 / white", "CBLQ4X1", "XQ1.3 A; B empty", "Banner 22 AWG; AI 0,34-8 TQ", "PARK ONLY / NOT RELEASED"),
        ("CON-008", "Q4X1 pin 4 / black", "CBLQ4X1", "XQ1.4 then TEST1+", "Banner 22 AWG; physical TEST1 SELECTION REQUIRED", "NOT RELEASED"),
        ("CON-009", "Q4X1 pin 5 / gray", "CBLQ4X1", "XQ1.5 then TEST1-", "Banner 22 AWG; physical TEST1 SELECTION REQUIRED", "NOT RELEASED"),
        ("CON-010", "CBLQ4X1 drain", "G2", "XQ1.6 A; B empty", "AI 0,34-8 TQ if received drain construction accepts; verify", "PARK ONLY / NO BOND / NOT RELEASED"),
        ("CON-011", "PTCB1 remote 13/14", "none", "no connection", "DNP; individually insulated/guarded by device", "INTENTIONALLY UNWIRED"),
    ])
    status = {
        "identifier": IDENTIFIER, "round": "R184", "date": DATE, "status": WARNING,
        "candidate_bom_rows": len(PARTS), "source_records": len(SOURCES), "open_holds": len(HOLDS),
        "native_schematic_sheets_including_root": 3, "released_connections": 0, "authorized_procurement": 0,
        "authorized_fabrication": 0, "authorized_powered_runs": 0, "executed_physical_runs": 0,
        "robot_baseline_changes": 0, "safety_function_credit": "ZERO", "gate_effect": {"EG-025": "OPEN", "EG-026": "PARTIAL"},
    }
    (PKG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_csv(FORM, ["inspection_id", "article_or_connection", "planned_check", "measured_or_observed", "evidence_location", "inspector", "result", "disposition"], [
        (f"QBA-{i:03d}", subject, check, "", "", "SELECTION REQUIRED", "NOT EXECUTED", "HOLD") for i, (subject, check) in enumerate([
            ("ENC1/PANEL1", "received identity, dimensions, damage and panel fit"), ("rail", "150.0 mm cut, deburr, edges and retention"),
            ("G1/G2", "identity, hole diameter, wall condition, lock nut, torque and cable retention"), ("PTCB1", "identity, orientation, terminal condition and DNP remote pins"),
            ("XQ1.1-XQ1.6", "identity, end covers, markers, orientation and empty-port controls"), ("CBLPS1", "exact procurement form, length, OD, colors, continuity and no shield"),
            ("CBLQ4X1", "identity, OD, M12 pin-to-color continuity, drain construction and no unintended shorts"), ("ferrules", "identity, strip length, crimp die, visual inspection and pull/retention evidence"),
            ("CON-001..CON-011", "point-to-point wire trace against native KiCad and schedule"), ("domain boundary", "unpowered isolation from PE, rail, robot returns, safety, actuator and DXL circuits"),
            ("completed enclosure", "spacing, bend radius, strain relief, labels, covers and closed-lid clearance"), ("work authority", "separate approved scope before each later physical stage"),
        ], start=1)
    ])


def write_docs_and_web() -> None:
    DOC.write_text(f"""# HR-V0 Q4X temporary interface-box candidate P0.1

> **{WARNING}**

Artifact: **{IDENTIFIER}**

Round: **R184**

Date: **{DATE}**

## Outcome

R184 converts the R183 Q4X protection/termination placeholder into a connected, native KiCad candidate with exact branch protection, terminals, ferrules, crimp tool, fiberglass enclosure, fiberglass panel, DIN rail, glands, lock nuts and cable designation. It remains a review candidate, not a build or connection release.

The temporary Q4X system remains a separately powered 24 V instrumentation domain. It has no intentional connection to robot safety 24 V/0 V, PE, contactor, watchdog, reset, actuator or DYNAMIXEL circuits and receives zero safety credit.

## Protection conclusion

The exact candidate is Phoenix Contact `PTCB E1 24DC/0.1A NO`, item `1464484`. The Q4X catalog upper-bound screen at 24.0 V is 28.125 mA; adding the PTCB's typical 5 mA closed-circuit current gives 33.125 mA before inrush. The resulting 3.019 ratio to 0.1 A is only a nominal steady-state screen. It is not an inrush margin or safety factor.

Phoenix publishes typical active limiting of 1.2 times nominal, not a guaranteed hard fault-current ceiling. R184 therefore does not claim a 0.12 A maximum. The Keithley channel's 1.5 A catalog maximum is below the PTCB's 300 A short-circuit switching capacity, so the manufacturer's catalog condition for an upstream backup fuse is not triggered. No fuse value is released, and source-current setting, overload, short, backfeed and abnormal-condition tests remain mandatory.

## Ground and shield rule

The nonconductive enclosure and inner panel contain an isolated metal DIN rail. No PE conductor enters this candidate box. The Banner cordset drain lands only on `XQ1.6`, an ordinary insulated terminal labeled `SHIELD PARK - NO PE/0V CONNECTION`; there is no bridge or shield clamp. Q4X pin 5 analog ground is not project-bonded to pin 3 DC common. These are proposals pending Boston site and qualified electrical review, not generalized grounding rules.

## Native electrical source

- root plus two connected child sheets: `electrical/kicad/{PROJECT}/`;
- sheet 01: source cable, return distribution and exact 0.1 A protection;
- sheet 02: exact sensor pins, remote-input park, analog pair, drain park and unresolved isolated test fixture;
- KiCad ERC and exported SVGs: `electrical/kicad/{PROJECT}/validation/` and `output/`; and
- synchronized BOM, net, connector and wire schedules in the same directory.

## Still blocking physical work

All fourteen `QBH-*` holds remain open. The most immediate are the exact source-cable procurement form and length, dimensioned gland-hole/rail coordinates, received identities, current-limit setting, terminal/crimp trials, unpowered isolation, closed-box thermal behavior, exact guarded analog test fixture, Boston site/jurisdiction review and separate work authorization.

R184 changes neither the robot electrical baseline nor Sol R12's verdict. `EG-025` remains open, `EG-026` remains partial, and no Sol blocker closes.

## Primary sources

The complete current-source register is `test-equipment/hr-v0/q4x-box-p0.1/source-register.csv`. Manufacturer component ratings do not transfer automatically to the completed drilled and wired assembly.
""", encoding="utf-8")

    part_cards = "".join(f"<article class='card'><p class='tag'>{escape(p[0])}</p><h3>{escape(p[3])}</h3><p>{escape(p[2])} · {escape(p[4])}</p><p>{escape(p[7])}</p><span>{escape(p[6])}</span></article>" for p in PARTS)
    hold_cards = "".join(f"<article class='hold'><h3>{escape(h[0])} · {escape(h[1])}</h3><p>{escape(h[2])}</p></article>" for h in HOLDS)
    source_rows = "".join(f"<tr><td>{escape(s[0])}</td><td>{escape(s[1])}</td><td><a href='{escape(s[4])}'>{escape(s[2])}</a></td><td>{escape(s[3])}</td><td>{escape(s[5])}</td></tr>" for s in SOURCES)
    html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENTIFIER}</title><style>
:root{{--sky:#dff4ff;--blue:#092f63;--mid:#1469a8;--gold:#f5bf27;--ink:#102033;--paper:#f7fbff;--line:#8bb6d3}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1240px;margin:auto;padding:clamp(18px,4vw,48px)}}h1{{font-size:clamp(36px,6vw,70px);line-height:1.05;color:var(--blue);margin:.3rem 0}}h2{{font-size:clamp(26px,3vw,40px);color:var(--blue);margin-top:2.4rem}}h3{{font-size:18px;color:var(--blue)}}.lead{{font-size:20px;max-width:920px}}.warn{{background:#fff2bd;border:3px solid #765800;padding:18px;font-weight:800;color:#473400}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px}}.card,.hold,.decision{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 0 #d3eaf7}}.card span,.tag,.badge{{display:inline-block;font-size:14px;font-weight:800;background:var(--gold);color:#17253b;border-radius:999px;padding:6px 10px;overflow-wrap:anywhere}}.tag{{background:var(--sky);color:var(--blue);margin:0}}.flow{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:12px;align-items:center}}.node{{background:var(--sky);border:2px solid var(--mid);padding:18px;border-radius:12px;font-weight:750}}.arrow{{font-size:28px;color:var(--mid)}}.tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}}button{{font:inherit;font-weight:750;border:2px solid var(--blue);background:white;color:var(--blue);padding:10px 14px;border-radius:9px;cursor:pointer}}button[aria-selected='true']{{background:var(--blue);color:white}}.sheet{{display:none;background:white;border:2px solid var(--line);border-radius:12px;overflow:auto}}.sheet.active{{display:block}}.sheet img{{display:block;min-width:900px;width:100%;height:auto}}.table-wrap{{overflow-x:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1000px;background:white}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #c6dce9;font-size:14px}}th{{background:var(--blue);color:white}}footer{{margin-top:36px;padding:24px;background:var(--blue);color:white}}@media(max-width:720px){{header,main{{padding:18px}}.lead{{font-size:18px}}.flow{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);text-align:center}}}}
</style></head><body><header><p class='badge'>R184 · CONNECTED NATIVE KICAD CANDIDATE</p><h1>The sensor box is defined. It is still not cleared to build.</h1><p class='lead'>Exact protection, terminals, ferrules, enclosure, panel, rail, glands and cable families now form one reviewable Q4X instrumentation branch. Fourteen evidence holds still prevent procurement, drilling, wiring and power.</p></header><main><p class='warn'>{escape(WARNING)}</p>
<section><h2>What the circuit does</h2><div class='flow'><div class='node'>Keithley CH1<br>24.0 V candidate<br>current limit open</div><div class='arrow'>→</div><div class='node'>PTCB 0.1 A<br>exact item 1464484<br>remote contact DNP</div><div class='arrow'>→</div><div class='node'>Banner Q4X<br>separate domain<br>zero safety credit</div></div><div class='decision'><strong>No robot-domain connection.</strong> The fiberglass box does not intentionally connect to robot safety power, PE, reset, watchdog, contactor, actuator or DXL circuits.</div></section>
<section><h2>Native schematic viewer</h2><p>These are KiCad-generated SVG exports, not decorative redraws. ERC establishes modeled connectivity and annotation only.</p><div class='tabs'><button aria-selected='true' data-target='s0'>Index</button><button aria-selected='false' data-target='s1'>01 · source + protection</button><button aria-selected='false' data-target='s2'>02 · sensor + signal</button></div><div id='s0' class='sheet active'><img alt='KiCad project index' src='../../../electrical/kicad/{PROJECT}/output/{PROJECT}.svg'></div><div id='s1' class='sheet'><img alt='KiCad source and protection sheet' src='../../../electrical/kicad/{PROJECT}/output/01_source_and_protection.svg'></div><div id='s2' class='sheet'><img alt='KiCad sensor and signal sheet' src='../../../electrical/kicad/{PROJECT}/output/02_sensor_and_signal.svg'></div></section>
<section><h2>Exact candidates and explicit gaps</h2><div class='grid'>{part_cards}</div></section><section><h2>Protection arithmetic without wishful thinking</h2><div class='decision'><strong>33.125 mA is a steady-state catalog screen, not an inrush result.</strong> The 3.019 ratio to the 0.1 A breaker is not a safety factor. Phoenix's 1.2× current-limiting figure is typical, so R184 does not claim a hard 0.12 A ceiling.</div></section>
<section><h2>Drain and ground treatment</h2><div class='decision'>The cordset drain parks on insulated terminal XQ1.6. There is no bridge, shield clamp, PE, rail, chassis or 0 V connection. Q4X analog ground pin 5 is not project-bonded to DC common pin 3. Received noise and isolation tests can reject this proposal.</div></section>
<section><h2>Fourteen holds block all physical work</h2><div class='grid'>{hold_cards}</div></section><section><h2>Current manufacturer evidence</h2><div class='table-wrap'><table><thead><tr><th>ID</th><th>Maker</th><th>Document</th><th>Revision/date</th><th>Controlled use</th></tr></thead><tbody>{source_rows}</tbody></table></div></section>
<section><h2>Gate effect</h2><p><strong>None.</strong> EG-025 stays open; EG-026 stays partial. There are zero released connections, zero authorized purchases, zero authorized fabrication steps, zero powered runs and zero safety-function credit.</p></section></main><footer>{escape(WARNING)}</footer><script>document.querySelectorAll('button[data-target]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('button[data-target]').forEach(x=>x.setAttribute('aria-selected','false'));document.querySelectorAll('.sheet').forEach(x=>x.classList.remove('active'));b.setAttribute('aria-selected','true');document.getElementById(b.dataset.target).classList.add('active')}}));</script></body></html>"""
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    write_package()
    build_ecad()
    write_docs_and_web()
    print(f"generated {IDENTIFIER}: 3 native sheets, {len(PARTS)} BOM rows, {len(HOLDS)} holds, 0 releases")


if __name__ == "__main__":
    main()
