"""Generate the HR-V0 DXL protection carrier P0.1 review package.

This is a single-channel, three-variant evaluation carrier used to obtain
physical current, transient and thermal evidence for R155.  It is not the
robot electrical baseline and is not a fabrication or energization release.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier"
RELEASE = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.1"
PROJECT = "hr-v0-dxl-protection-carrier"
IDENTIFIER = "HR-V0-DXL-PROT-CARRIER-P0.1"
REVISION = "DXL-PROT-CARRIER-P0.1"
SILK_REVISION = "P0.1"
DATE = "2026-08-09"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SHEET_WARNING = "PRELIMINARY - NO SUPPLIER UPLOAD, FABRICATION, CONNECTION, OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")
KICAD_CLI = KICAD_ROOT / "bin" / "kicad-cli.exe"
FOOTPRINT_ROOT = KICAD_ROOT / "share" / "kicad" / "footprints"

TI_DS = "https://www.ti.com/lit/ds/symlink/tps25946.pdf"
TI_EVM = "https://www.ti.com/lit/ug/slvuc35a/slvuc35a.pdf"
JST_VH = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
TDK_1U = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1V105K080AC"
TDK_100N = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1H104K080AA"
TDK_2N2 = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608C0G1H222J080AA"
DIODE = "https://www.diodes.com/datasheet/download/B330A.pdf"


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("dxl_protection_carrier_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load KiCad schematic model")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.PROJECT = PROJECT
    model.REV = REVISION
    model.PROJECT_TITLE = "PROJECT BUTTON HR-V0 DXL PROTECTION CARRIER"
    model.PROJECT_SUBTITLE = "Single-channel R155 measurement carrier; assemble three controlled variants; no robot-baseline change."
    model.DATE = DATE
    return model


def components(model):
    Component, pn = model.Component, model.pn
    rpw = "ProjectButton_RPW.pretty:TI_RPW0010A_HotRodQFN_2x2mm_P0.475mm_CANDIDATE"
    r0603 = "Resistor_SMD:R_0603_1608Metric"
    c0603 = "Capacitor_SMD:C_0603_1608Metric"
    testpoint = "TestPoint:TestPoint_Keystone_5010-5014_Multipurpose"
    vh = "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical"
    items = [
        Component("JIN1", "JST B2P-VH INPUT", [pn("JIN1", "1", "FUSED +12 V", "BRANCH_FUSED_IN", "right"), pn("JIN1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT PCB HEADER; MATING HARNESS HELD", "B2P-VH; project pin 1 positive and pin 2 common return. Housing, contact, conductor, crimp and thermal application remain open.", JST_VH, "JST VH English catalog; rechecked 2026-08-09.", position=(45, 75), width=76, footprint=vh),
        Component("U1", "TPS259461LRPWR", [
            pn("U1", "1", "EN/UVLO", "UVLO_SET", "left"), pn("U1", "2", "OVLO", "OVLO_SET", "left"),
            pn("U1", "3", "SPLYGD", "SPLYGD_DIAG", "left"), pn("U1", "4", "FLT", "FLT_DIAG", "left"),
            pn("U1", "5", "IN", "BRANCH_FUSED_IN", "left"), pn("U1", "6", "OUT", "BRANCH_LIMITED_OUT", "right"),
            pn("U1", "7", "dVdt", "DVDT_SET", "right"), pn("U1", "9", "ILM", "ILM_SET", "right"),
            pn("U1", "10", "ITIMER OPEN", "INTENTIONALLY_OPEN_ITIMER", "right")],
                  "EXACT EVALUATION CANDIDATE", "Forward current limiting only. Reverse current is unbounded while ON. Custom RPW footprint is a drawing-derived review candidate, not independent footprint acceptance.", TI_DS, "SLVSGA8B Rev B, April 2022; active exact orderable rechecked 2026-08-09.", position=(190, 80), width=95, height=72, footprint=rpw),
        Component("U1G", "U1 PIN 8 GND", [pn("U1G", "8", "GND", "ACT_0V_PE_BONDED", "right")],
                  "SAME DEVICE CROSS-REFERENCE", "Graphical split for U1 pin 8; quantity zero.", TI_DS, "Same TPS259461LRPWR device.", position=(45, 140), width=64, quantity=0, footprint=rpw),
        Component("JOUT1", "JST B2P-VH OUTPUT", [pn("JOUT1", "1", "LIMITED +12 V", "BRANCH_LIMITED_OUT", "left"), pn("JOUT1", "2", "RETURN", "ACT_0V_PE_BONDED", "left")],
                  "EXACT PCB HEADER; MATING HARNESS HELD", "Output boundary to DXL-STAR. No current, connector-temperature or harness release.", JST_VH, "JST VH English catalog; rechecked 2026-08-09.", position=(350, 75), width=76, footprint=vh),
        Component("RILM1", "ASSEMBLY VARIANT: 1.65 k / 3.32 k", [pn("RILM1", "1", "ILM", "ILM_SET", "left"), pn("RILM1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT VARIANT MPN; APPLICATION HELD", "J1/J2 use RC0603FR-071K65L; G1 uses RC0603FR-073K32L. Threshold and temperature require received test.", TI_EVM, "1.65 k exact TI EVM BOM; 3.32 k exact Yageo family candidate.", position=(135, 145), width=82, footprint=r0603),
        Component("RUVT1", "365 k RC0603FR-07365KL", [pn("RUVT1", "1", "IN", "BRANCH_FUSED_IN", "left"), pn("RUVT1", "2", "UVLO", "UVLO_SET", "right")], "EXACT CANDIDATE", "Nominal 10 V UVLO upper resistor; tolerance validation open.", TI_DS, "Yageo exact order code; 0603 1% 0.1 W.", position=(45, 190), width=78, footprint=r0603),
        Component("RUVB1", "49.9 k RC0603FR-0749K9L", [pn("RUVB1", "1", "UVLO", "UVLO_SET", "left"), pn("RUVB1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT CANDIDATE", "Nominal 10 V UVLO lower resistor; tolerance validation open.", TI_DS, "Yageo exact order code; 0603 1% 0.1 W.", position=(135, 190), width=78, footprint=r0603),
        Component("ROVT1", "470 k RC0603FR-07470KL", [pn("ROVT1", "1", "IN", "BRANCH_FUSED_IN", "left"), pn("ROVT1", "2", "OVLO", "OVLO_SET", "right")], "EXACT CANDIDATE", "TI example OVLO upper resistor; project transient validation open.", TI_DS, "Yageo exact order code; 0603 1% 0.1 W.", position=(225, 190), width=78, footprint=r0603),
        Component("ROVB1", "44.2 k RC0603FR-0744K2L", [pn("ROVB1", "1", "OVLO", "OVLO_SET", "left"), pn("ROVB1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT CANDIDATE", "TI example OVLO lower resistor; project transient validation open.", TI_DS, "Yageo exact order code; 0603 1% 0.1 W.", position=(315, 190), width=78, footprint=r0603),
        Component("CDV1", "2.2 nF C1608C0G1H222J080AA", [pn("CDV1", "1", "dVdt", "DVDT_SET", "left"), pn("CDV1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "Slew-rate capacitor; startup and thermal behavior remain open.", TDK_2N2, "TDK current product page; 50 V C0G 0603.", position=(45, 235), width=82, footprint=c0603),
        Component("CINHF1", "0.1 uF C1608X7R1H104K080AA", [pn("CINHF1", "1", "IN", "BRANCH_FUSED_IN", "left"), pn("CINHF1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "High-frequency input bypass; placement and physical transient validation open.", TDK_100N, "TI minimum and EVM exact BOM; TDK 50 V X7R 0603.", position=(135, 235), width=82, footprint=c0603),
        Component("CINBULK1", "1 uF C1608X7R1V105K080AC", [pn("CINBULK1", "1", "IN", "BRANCH_FUSED_IN", "left"), pn("CINBULK1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "Input transient capacitor; received capacitance and waveform evidence open.", TDK_1U, "TI transient guidance and EVM exact BOM; TDK 35 V X7R 0603.", position=(225, 235), width=82, footprint=c0603),
        Component("COUTA1", "1 uF C1608X7R1V105K080AC", [pn("COUTA1", "1", "OUT", "BRANCH_LIMITED_OUT", "left"), pn("COUTA1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "First output capacitor; effective capacitance under bias remains a test hold.", TDK_1U, "TI requires at least 1 uF close to OUT for transient control.", position=(315, 235), width=82, footprint=c0603),
        Component("COUTB1", "1 uF C1608X7R1V105K080AC", [pn("COUTB1", "1", "OUT", "BRANCH_LIMITED_OUT", "left"), pn("COUTB1", "2", "RETURN", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "Second parallel output capacitor adds nominal margin only; not physical proof.", TDK_1U, "Same exact TDK candidate as COUTA1.", position=(45, 280), width=82, footprint=c0603),
        Component("DCLAMP1", "B330A-13-F", [pn("DCLAMP1", "1", "K CATHODE", "BRANCH_LIMITED_OUT", "left"), pn("DCLAMP1", "2", "A ANODE", "ACT_0V_PE_BONDED", "right")], "EXACT EVALUATION CANDIDATE", "Output Schottky transient clamp. Pulse energy and thermal suitability remain open.", DIODE, "Diodes Inc. Rev 19-2, April 2026; 3 A, 30 V SMA candidate.", position=(135, 280), width=82, footprint="Diode_SMD:D_SMA"),
    ]
    tp_specs = [
        ("TPVIN1", "Keystone 5010 VIN", "BRANCH_FUSED_IN", "red"),
        ("TPOUT1", "Keystone 5010 VOUT", "BRANCH_LIMITED_OUT", "red"),
        ("TPGND1", "Keystone 5011 GND", "ACT_0V_PE_BONDED", "black"),
        ("TPILM1", "Keystone 5012 ILM", "ILM_SET", "white"),
        ("TPSPLY1", "Keystone 5012 SPLYGD", "SPLYGD_DIAG", "white"),
        ("TPFLT1", "Keystone 5012 FLT", "FLT_DIAG", "white"),
    ]
    x = 225
    for i, (ref, value, net, color) in enumerate(tp_specs):
        items.append(Component(ref, value, [pn(ref, "1", net, net, "right")], "EXACT EVALUATION CANDIDATE", f"{color} EVM-family test point; probe method and loading remain open. SPLYGD/FLT are unpulled open-drain diagnostics with zero safety or motion credit.", TI_EVM, "TI EVM BOM exact Keystone test-point family.", position=(x + (i % 2) * 90, 280 + (i // 2) * 42), width=82, footprint=testpoint))
    return items


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_schematic(model, items):
    OUT.mkdir(parents=True, exist_ok=True)
    by_ref = {item.ref: item for item in items}
    sheet = model.Sheet(1, "01_protection_core.kicad_sch", "Single-channel DXL branch protection core", "Exact active, power boundaries and assembly-variant current setting.")
    sheet.components = [by_ref[ref] for ref in ("JIN1", "U1", "JOUT1", "U1G", "RILM1")]
    for item, position in zip(sheet.components, ((50, 70), (220, 68), (370, 70), (60, 170), (220, 170))): item.position = position
    by_ref["JIN1"].width = by_ref["JOUT1"].width = 60
    sheet.notes = [
        "TPS259461L limits forward current only; reverse current is unbounded while ON.",
        "ITIMER is deliberately open. SPLYGD and FLT are unpulled diagnostic test points only.",
        "J1/J2 assemble RILM=1.65 kOhm; G1 assembles RILM=3.32 kOhm. Never substitute variants without a controlled record.",
        SHEET_WARNING,
    ]
    bias = model.Sheet(2, "02_threshold_dividers.kicad_sch", "UVLO and OVLO threshold candidates", "Exact resistor identities; divider tolerance and physical thresholds remain open.")
    bias.components = [by_ref[ref] for ref in ("RUVT1", "RUVB1", "ROVT1", "ROVB1")]
    for item, position in zip(bias.components, ((115, 75), (305, 75), (115, 175), (305, 175))): item.position, item.width = position, 72
    bias.notes = [
        "RUVT1/RUVB1 create the nominal UVLO candidate; ROVT1/ROVB1 use TI's 14 V application-example values.",
        "Received resistor value, tolerance, temperature drift and measured thresholds remain test gates.",
        SHEET_WARNING,
    ]
    transient = model.Sheet(3, "03_bypass_and_transients.kicad_sch", "Bypass, slew and transient candidates", "Exact passive identities; physical transient, effective-capacitance and thermal proof remain open.")
    transient.components = [by_ref[ref] for ref in ("CDV1", "CINHF1", "CINBULK1", "COUTA1", "COUTB1", "DCLAMP1")]
    for item, position in zip(transient.components, ((115, 65), (305, 65), (115, 145), (305, 145), (115, 225), (305, 225))): item.position = position
    transient.notes = [
        "CINHF1 and CINBULK1 implement TI input guidance; COUTA1/COUTB1 provide nominal output-capacitance margin only.",
        "DCLAMP1 is the local output Schottky. The external regenerative shunt candidate is not installed on this carrier.",
        "TVS need and identity remain SELECTION REQUIRED pending actual interconnect-inductance and transient evidence.",
        SHEET_WARNING,
    ]
    measurement = model.Sheet(4, "04_measurement_points.kicad_sch", "Measurement and diagnostic points", "All measurements require a released method; no diagnostic has safety or motion authority.")
    measurement.components = [by_ref[ref] for ref in ("TPVIN1", "TPOUT1", "TPGND1", "TPILM1", "TPSPLY1", "TPFLT1")]
    for item, position in zip(measurement.components, ((115, 65), (305, 65), (115, 145), (305, 145), (115, 225), (305, 225))): item.position = position
    measurement.notes = [
        "ILM total parasitic and probe capacitance must remain below TI's 50 pF limit.",
        "SPLYGD and FLT are unpulled open-drain observations only; no safety, reset or motion credit is assigned.",
        "Test-plan and data records are blank. No physical test has been executed.",
        SHEET_WARNING,
    ]
    sheets = [sheet, bias, transient, measurement]
    net_counts = Counter(pin.net for item in items for pin in item.pins)
    wires = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr-v0-dxl-protection-carrier")
    project = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [
            {"name": "Default", "priority": 2147483647, "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4},
            {"name": "POWER", "priority": 1, "clearance": 0.25, "track_width": 3.0, "via_diameter": 1.2, "via_drill": 0.6}],
            "meta": {"version": 3}, "netclass_assignments": {"BRANCH_FUSED_IN": "POWER", "BRANCH_LIMITED_OUT": "POWER"}},
        "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REVISION},
    }
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for item in items]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "Controlled DXL protection-carrier symbols"))\n)\n', encoding="utf-8")
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "ProjectButton_RPW.pretty")(type "KiCad")(uri "${KIPRJMOD}/ProjectButton_RPW.pretty")(options "")(descr "Controlled TI RPW0010A candidate"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for child in sheets: (OUT / child.filename).write_text(model.child_schematic(root_uuid, child, net_counts, wires), encoding="utf-8")
    write_csv(OUT / "bom.csv", ["reference", "manufacturer", "manufacturer_part_number", "value", "quantity", "assembly_variant", "status", "evidence"], [
        {"reference": item.ref, "manufacturer": manufacturer(item.ref), "manufacturer_part_number": mpn(item.ref), "value": item.value, "quantity": item.quantity, "assembly_variant": variant(item.ref), "status": item.status, "evidence": item.evidence} for item in items
    ])
    write_csv(OUT / "terminal-schedule.csv", ["reference", "terminal", "pin_name", "net", "status"], [
        {"reference": item.ref, "terminal": pin.number, "pin_name": pin.name, "net": pin.net, "status": item.status} for item in items for pin in item.pins
    ])


def manufacturer(ref: str) -> str:
    if ref.startswith("J"): return "JST"
    if ref.startswith("U"): return "Texas Instruments"
    if ref.startswith("R"): return "Yageo"
    if ref.startswith("C"): return "TDK"
    if ref.startswith("D"): return "Diodes Incorporated"
    if ref.startswith("TP"): return "Keystone Electronics"
    return ""


def mpn(ref: str) -> str:
    return {
        "JIN1": "B2P-VH", "JOUT1": "B2P-VH", "U1": "TPS259461LRPWR", "U1G": "TPS259461LRPWR",
        "RILM1": "RC0603FR-071K65L / RC0603FR-073K32L", "RUVT1": "RC0603FR-07365KL", "RUVB1": "RC0603FR-0749K9L", "ROVT1": "RC0603FR-07470KL", "ROVB1": "RC0603FR-0744K2L",
        "CDV1": "C1608C0G1H222J080AA", "CINHF1": "C1608X7R1H104K080AA", "CINBULK1": "C1608X7R1V105K080AC", "COUTA1": "C1608X7R1V105K080AC", "COUTB1": "C1608X7R1V105K080AC", "DCLAMP1": "B330A-13-F",
        "TPVIN1": "5010", "TPOUT1": "5010", "TPGND1": "5011", "TPILM1": "5012", "TPSPLY1": "5012", "TPFLT1": "5012",
    }.get(ref, "")


def variant(ref: str) -> str:
    return "J1/J2=1.65k; G1=3.32k" if ref == "RILM1" else "ALL THREE"


def add_smd_pad(fp, number: str, x: float, y: float, sx: float, sy: float):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I_MM(sx, sy))
    pad.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    pad.SetLayerSet(pad.SMDMask())
    fp.Add(pad)


def create_rpw_footprint(parent=None):
    fp = pcbnew.FOOTPRINT(parent)
    fp.SetFPID(pcbnew.LIB_ID("ProjectButton_RPW.pretty", "TI_RPW0010A_HotRodQFN_2x2mm_P0.475mm_CANDIDATE"))
    fp.SetValue("TI RPW0010A DRAWING-DERIVED CANDIDATE")
    fp.SetLibDescription("Drawing-derived from TI RPW0010A land-pattern page in SLVSGA8B Rev B; independent assembler acceptance remains open.")
    ys = [0.7125, 0.2375, -0.2375, -0.7125]
    for number, y in zip(("1", "2", "3", "4"), ys): add_smd_pad(fp, number, -0.9, y, 0.6, 0.25)
    for number, y in zip(("10", "9", "8", "7"), ys): add_smd_pad(fp, number, 0.9, y, 0.6, 0.25)
    add_smd_pad(fp, "5", -0.25, 0.0, 0.30, 1.80)
    add_smd_pad(fp, "6", 0.25, 0.0, 0.30, 1.80)
    for number, x, y in (("1", -0.62, 0.67), ("4", -0.62, -0.67), ("10", 0.62, 0.67), ("7", 0.62, -0.67)):
        add_smd_pad(fp, number, x, y, 0.20, 0.42)
    for start, end in [((-1.0, -1.0), (1.0, -1.0)), ((1.0, -1.0), (1.0, 1.0)), ((1.0, 1.0), (-1.0, 1.0)), ((-1.0, 1.0), (-1.0, -1.0))]:
        shape = pcbnew.PCB_SHAPE(fp)
        shape.SetShape(pcbnew.SHAPE_T_SEGMENT); shape.SetStart(pcbnew.VECTOR2I_MM(*start)); shape.SetEnd(pcbnew.VECTOR2I_MM(*end)); shape.SetLayer(pcbnew.F_Fab); shape.SetWidth(pcbnew.FromMM(0.1)); fp.Add(shape)
    marker = pcbnew.PCB_SHAPE(fp); marker.SetShape(pcbnew.SHAPE_T_CIRCLE); marker.SetCenter(pcbnew.VECTOR2I_MM(-1.25, 0.8)); marker.SetEnd(pcbnew.VECTOR2I_MM(-1.15, 0.8)); marker.SetLayer(pcbnew.F_Fab); marker.SetWidth(pcbnew.FromMM(0.10)); fp.Add(marker)
    return fp


def footprint_location(identifier: str) -> tuple[Path, str]:
    library, name = identifier.split(":", 1)
    return FOOTPRINT_ROOT / f"{library}.pretty", name


def add_text(board, value, x, y, size, layer):
    item = pcbnew.PCB_TEXT(board); item.SetText(value); item.SetPosition(pcbnew.VECTOR2I_MM(x, y)); item.SetLayer(layer); item.SetTextSize(pcbnew.VECTOR2I_MM(size, size)); item.SetTextThickness(pcbnew.FromMM(max(0.18, size * 0.12))); board.Add(item)


def add_track(board, net, points, width, layer=pcbnew.F_Cu):
    for start, end in zip(points, points[1:]):
        if start == end: continue
        track = pcbnew.PCB_TRACK(board); track.SetStart(pcbnew.VECTOR2I_MM(*start)); track.SetEnd(pcbnew.VECTOR2I_MM(*end)); track.SetWidth(pcbnew.FromMM(width)); track.SetLayer(layer); track.SetNet(net); board.Add(track)


def pad_xy(fp, number: str):
    pads = [pad for pad in fp.Pads() if pad.GetNumber() == number]
    if not pads: raise RuntimeError(f"no pad {fp.GetReference()}.{number}")
    pos = pads[0].GetPosition(); return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)


def add_via(board, net, point, diameter=0.8, drill=0.4):
    via = pcbnew.PCB_VIA(board); via.SetPosition(pcbnew.VECTOR2I_MM(*point)); via.SetWidth(pcbnew.FromMM(diameter)); via.SetDrill(pcbnew.FromMM(drill)); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); board.Add(via)


def fanout_to_inner(board, net, pad_point, via_point):
    add_track(board, net, [pad_point, via_point], 0.18, pcbnew.F_Cu); add_via(board, net, via_point, 0.6, 0.3)


def write_board(items):
    lib = OUT / "ProjectButton_RPW.pretty"; lib.mkdir(exist_ok=True)
    pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib), create_rpw_footprint())
    board = pcbnew.BOARD(); board.SetCopperLayerCount(4)
    board.GetDesignSettings().m_MinClearance = pcbnew.FromMM(0.08)
    board.GetDesignSettings().m_SolderMaskMinWidth = pcbnew.FromMM(0.05)
    board.GetDesignSettings().m_TrackMinWidth = pcbnew.FromMM(0.15)
    board.GetDesignSettings().m_HoleClearance = pcbnew.FromMM(0.10)
    board.GetDesignSettings().m_NetSettings.GetDefaultNetclass().SetClearance(pcbnew.FromMM(0.08))
    names = sorted({pin.net for item in items for pin in item.pins if not pin.net.startswith("INTENTIONALLY_OPEN")})
    nets = {}
    for name in names:
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    placements = {
        "JIN1": (8, 30, 270), "JOUT1": (92, 30, 90), "U1": (50, 30, 0),
        "RUVT1": (40, 18, 0), "RUVB1": (44, 18, 0), "ROVT1": (40, 42, 0), "ROVB1": (44, 42, 0), "RILM1": (60, 42, 0),
        "CDV1": (60, 18, 0), "CINHF1": (32, 28, 0), "CINBULK1": (32, 36, 0), "COUTA1": (68, 26, 0), "COUTB1": (68, 31, 0), "DCLAMP1": (78, 20, 90),
        "TPVIN1": (16, 12, 0), "TPOUT1": (84, 12, 0), "TPGND1": (50, 52, 0), "TPILM1": (70, 42, 0), "TPSPLY1": (20, 22, 0), "TPFLT1": (20, 38, 0),
    }
    by_ref = {}
    for item in items:
        if item.quantity == 0: continue
        if item.ref == "U1": fp = create_rpw_footprint(board)
        else:
            library, name = footprint_location(item.footprint); fp = pcbnew.FootprintLoad(str(library), name)
            if fp is None: raise RuntimeError(f"cannot load {item.footprint}")
        fp.SetReference(item.ref); fp.SetValue(item.value); x, y, rot = placements[item.ref]; fp.SetPosition(pcbnew.VECTOR2I_MM(x, y)); fp.SetOrientationDegrees(rot); fp.Reference().SetVisible(False)
        pin_nets = {pin.number: pin.net for pin in item.pins}
        if item.ref == "U1": pin_nets["8"] = "ACT_0V_PE_BONDED"
        for pad in fp.Pads():
            net_name = pin_nets.get(pad.GetNumber(), "")
            if net_name in nets: pad.SetNet(nets[net_name])
        board.Add(fp); by_ref[item.ref] = fp
    for index, (x, y) in enumerate(((5, 5), (95, 5), (5, 55), (95, 55)), 1):
        hole = pcbnew.FootprintLoad(str(FOOTPRINT_ROOT / "MountingHole.pretty"), "MountingHole_3.2mm_M3"); hole.SetReference(f"MH{index}"); hole.SetValue("BOARD-ONLY M3; MOUNTING SELECTION REQUIRED"); hole.SetPosition(pcbnew.VECTOR2I_MM(x, y)); hole.SetBoardOnly(True); hole.SetExcludedFromBOM(True); hole.SetExcludedFromPosFiles(True); hole.Reference().SetVisible(False); board.Add(hole)
    outline = [(0, 0), (100, 0), (100, 60), (0, 60), (0, 0)]
    for start, end in zip(outline, outline[1:]):
        line = pcbnew.PCB_SHAPE(board); line.SetShape(pcbnew.SHAPE_T_SEGMENT); line.SetStart(pcbnew.VECTOR2I_MM(*start)); line.SetEnd(pcbnew.VECTOR2I_MM(*end)); line.SetLayer(pcbnew.Edge_Cuts); line.SetWidth(pcbnew.FromMM(0.25)); board.Add(line)
    # Taper the main power paths near U1 so the wide routes do not violate the fine-pitch package escape geometry.
    add_track(board, nets["BRANCH_FUSED_IN"], [pad_xy(by_ref["JIN1"], "1"), (24, 30), (24, 24), (43, 24)], 3.0)
    add_track(board, nets["BRANCH_FUSED_IN"], [(43, 24), (49.75, 24), (49.75, 29.1), pad_xy(by_ref["U1"], "5")], 0.30)
    add_track(board, nets["BRANCH_LIMITED_OUT"], [pad_xy(by_ref["U1"], "6"), (50.25, 35.8), (57, 35.8)], 0.30)
    add_track(board, nets["BRANCH_LIMITED_OUT"], [(57, 35.8), (85, 35.8), (85, 30), pad_xy(by_ref["JOUT1"], "1")], 3.0)
    # Power branches remain on F.Cu and are kept clear of the package signal fanout.
    input_points = [("RUVT1", "1", [(39.225, 18), (36, 18), (36, 24)]), ("ROVT1", "1", [(39.225, 42), (37, 42), (37, 24)]), ("CINHF1", "1", [(31.225, 28), (31.225, 24)]), ("CINBULK1", "1", [(31.225, 36), (29, 36), (29, 24)]), ("TPVIN1", "1", [(16, 12), (16, 24), (24, 24)])]
    for ref, pin, path in input_points: add_track(board, nets["BRANCH_FUSED_IN"], [pad_xy(by_ref[ref], pin), *path[1:]], 0.5)
    output_points = [("COUTA1", "1", [(67.225, 26), (65, 26), (65, 35.8)]), ("COUTB1", "1", [(67.225, 31), (67.225, 35.8)]), ("DCLAMP1", "1", [(78, 17), (82, 17), (82, 35.8)]), ("TPOUT1", "1", [(84, 12), (84, 35.8)])]
    for ref, pin, path in output_points: add_track(board, nets["BRANCH_LIMITED_OUT"], [pad_xy(by_ref[ref], pin), *path[1:]], 0.5)
    # Every fine-pitch support/diagnostic net escapes by a short F.Cu segment and then routes on In2.Cu.
    signal_routes = {
        "UVLO_SET": [((49.1, 30.7125), (45.0, 32.0)), ((40.775, 18), (42.0, 18.0)), ((43.225, 18), (43.225, 20.0))],
        "OVLO_SET": [((49.1, 30.2375), (47.0, 30.5)), ((40.775, 42), (42.0, 42.0)), ((43.225, 42), (43.225, 40.0))],
        "SPLYGD_DIAG": [((49.1, 29.7625), (45.0, 29.0)), ((20, 22), (20, 22))],
        "FLT_DIAG": [((49.1, 29.2875), (45.0, 27.5)), ((20, 38), (20, 38))],
        "DVDT_SET": [((50.9, 29.2875), (55.0, 27.5)), ((59.225, 18), (58.0, 18.0))],
        "ILM_SET": [((50.9, 30.2375), (55.0, 30.5)), ((59.225, 42), (58.0, 42.0)), ((70, 42), (70, 42))],
    }
    inner_paths = {
        "UVLO_SET": [(45.0, 32), (43.225, 32), (43.225, 20), (42.0, 20), (42.0, 18)],
        "OVLO_SET": [(47.0, 30.5), (47.0, 40), (43.225, 40), (43.225, 42), (42.0, 42)],
        "SPLYGD_DIAG": [(45.0, 29), (42, 26), (30, 23), (20, 22)],
        "FLT_DIAG": [(45.0, 27.5), (48, 27), (48, 45), (20, 45), (20, 38)],
        "DVDT_SET": [(55.0, 27.5), (56, 24), (56, 20), (58, 18)],
        "ILM_SET": [(55.0, 30.5), (55, 42), (58, 42), (70, 42)],
    }
    for netname, endpoints in signal_routes.items():
        for padpoint, via in endpoints:
            if padpoint != via: fanout_to_inner(board, nets[netname], padpoint, via)
        layer = pcbnew.B_Cu if netname in {"SPLYGD_DIAG", "FLT_DIAG"} else pcbnew.In2_Cu
        add_track(board, nets[netname], inner_paths[netname], 0.18, layer)
    # Ground every SMD return with an offset via into the two-plane return system.
    ground_refs = [("RUVB1", "2"), ("ROVB1", "2"), ("RILM1", "2"), ("CDV1", "2"), ("CINHF1", "2"), ("CINBULK1", "2"), ("COUTA1", "2"), ("COUTB1", "2"), ("DCLAMP1", "2"), ("U1", "8")]
    ground_offsets = {"CINHF1": (35, 30), "CINBULK1": (35, 38), "COUTA1": (71, 24), "COUTB1": (71, 29), "RUVB1": (47, 17), "ROVB1": (47, 43), "RILM1": (63, 44), "CDV1": (63, 16)}
    for index, (ref, pin) in enumerate(ground_refs):
        point = pad_xy(by_ref[ref], pin)
        if ref == "U1": offset = (54.0, 29.75)
        elif ref == "DCLAMP1": offset = (80.0, 18.0)
        elif ref in ground_offsets: offset = ground_offsets[ref]
        else: offset = (point[0] + 1.5, point[1] + (0.7 if index % 2 else -0.7))
        fanout_to_inner(board, nets["ACT_0V_PE_BONDED"], point, offset)
    for layer in (pcbnew.In1_Cu,):
        zone = pcbnew.ZONE(board); zone.SetLayer(layer); zone.SetNet(nets["ACT_0V_PE_BONDED"]); zone.SetLocalClearance(pcbnew.FromMM(0.25)); polygon = zone.Outline(); polygon.NewOutline()
        for point in ((0.8, 0.8), (99.2, 0.8), (99.2, 59.2), (0.8, 59.2)): polygon.Append(pcbnew.VECTOR2I_MM(*point))
        zone.SetMinThickness(pcbnew.FromMM(0.254)); board.Add(zone)
    add_text(board, f"{SILK_REVISION} EVALUATION CARRIER - NO ROBOT RELEASE", 28, 56, 1.0, pcbnew.F_SilkS)
    add_text(board, "VIN", 6, 23, 1.0, pcbnew.F_SilkS); add_text(board, "VOUT", 90, 23, 1.0, pcbnew.F_SilkS)
    add_text(board, "PRELIMINARY - NOT APPROVED FOR FABRICATION", 25, 5, 0.8, pcbnew.F_SilkS)
    add_text(board, "NO CONNECTION / MOTION / ENERGIZATION", 30, 8, 0.8, pcbnew.F_SilkS)
    pcbnew.SaveBoard(str(OUT / f"{PROJECT}.kicad_pcb"), board)


def run(command, log):
    result = subprocess.run([str(KICAD_CLI), *map(str, command)], cwd=ROOT, text=True, capture_output=True)
    log.extend(["$ " + subprocess.list2cmdline([str(KICAD_CLI), *map(str, command)]), result.stdout, result.stderr, f"exit={result.returncode}\n"])
    if result.returncode: raise RuntimeError("KiCad command failed: " + " ".join(map(str, command)))


def run_kicad():
    validation = RELEASE / "validation"; output = RELEASE / "output"; cam = RELEASE / "cam"; gerbers = cam / "gerbers"; drill = cam / "drill"
    for directory in (validation, output, gerbers, drill): directory.mkdir(parents=True, exist_ok=True)
    log = []; sch = OUT / f"{PROJECT}.kicad_sch"; pcb = OUT / f"{PROJECT}.kicad_pcb"
    commands = [
        ["sch", "erc", "--exit-code-violations", "--output", validation / f"{PROJECT}-erc.rpt", sch],
        ["sch", "export", "netlist", "--output", validation / f"{PROJECT}.net", sch],
        ["sch", "export", "pdf", "--output", output / f"{PROJECT}-preliminary.pdf", sch],
        ["sch", "export", "svg", "--output", output, sch],
        ["pcb", "drc", "--exit-code-violations", "--refill-zones", "--save-board", "--output", validation / f"{PROJECT}-drc.rpt", pcb],
        ["pcb", "render", "--output", output / f"{PROJECT}-top.png", "--width", "1600", "--height", "1000", "--side", "top", "--background", "opaque", pcb],
        ["pcb", "render", "--output", output / f"{PROJECT}-bottom.png", "--width", "1600", "--height", "1000", "--side", "bottom", "--background", "opaque", pcb],
        ["pcb", "export", "gerbers", "--output", gerbers, "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts", "--precision", "6", "--check-zones", pcb],
        ["pcb", "export", "drill", "--output", drill, "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "svg", "--generate-report", "--report-path", drill / f"{PROJECT}-drill-report.txt", pcb],
        ["pcb", "export", "pos", "--output", cam / f"{PROJECT}-all-pos.csv", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp", pcb],
        ["pcb", "export", "stats", "--output", cam / f"{PROJECT}-stats.json", "--format", "json", "--units", "mm", pcb],
    ]
    for command in commands: run(command, log)
    (validation / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def release_files(items):
    RELEASE.mkdir(parents=True, exist_ok=True)
    sources = [
        ("SRC-01", "Texas Instruments", "TPS25946 datasheet", "SLVSGA8B Rev B", "April 2022", TI_DS, "Pinout, limits, reverse-current warning, layout and thermal examples"),
        ("SRC-02", "Texas Instruments", "TPS25946EVM guide", "SLVUC35A Rev A", "August 2021", TI_EVM, "Exact EVM passive and test-point identities"),
        ("SRC-03", "JST", "VH connector catalog", "current English asset", "accessed 2026-08-09", JST_VH, "B2P-VH geometry and mating family; application held"),
        ("SRC-04", "TDK", "1 uF MLCC product record", "current", "accessed 2026-08-09", TDK_1U, "C1608X7R1V105K080AC identity"),
        ("SRC-05", "TDK", "0.1 uF MLCC product record", "current", "accessed 2026-08-09", TDK_100N, "C1608X7R1H104K080AA identity"),
        ("SRC-06", "TDK", "2.2 nF MLCC product record", "current", "accessed 2026-08-09", TDK_2N2, "C1608C0G1H222J080AA identity"),
        ("SRC-07", "Diodes Incorporated", "B330A datasheet", "Rev 19-2", "April 2026", DIODE, "B330A-13-F ratings and SMA package"),
    ]
    write_csv(RELEASE / "primary-source-register.csv", ["source_id", "manufacturer", "document", "revision", "date", "url", "used_for", "status", "warning"], [dict(zip(["source_id", "manufacturer", "document", "revision", "date", "url", "used_for"], row), status="PRIMARY SOURCE VERIFIED; APPLICATION NOT VALIDATED", warning=WARNING) for row in sources])
    write_csv(RELEASE / "assembly-variants.csv", ["variant", "quantity", "application", "RILM1_mpn", "catalog_current_window", "state", "warning"], [
        {"variant": "J1/J2", "quantity": 2, "application": "shoulder and elbow evaluation branches", "RILM1_mpn": "RC0603FR-071K65L", "catalog_current_window": "1.8-2.2 A before resistor tolerance", "state": "EVALUATION ONLY", "warning": WARNING},
        {"variant": "G1", "quantity": 1, "application": "gripper evaluation branch", "RILM1_mpn": "RC0603FR-073K32L", "catalog_current_window": "0.85-1.15 A before resistor tolerance", "state": "EVALUATION ONLY", "warning": WARNING},
    ])
    write_csv(RELEASE / "footprint-audit.csv", ["reference", "footprint", "source", "state", "evidence_needed", "warning"], [
        {"reference": "U1", "footprint": "TI_RPW0010A_HotRodQFN_2x2mm_P0.475mm_CANDIDATE", "source": "TI SLVSGA8B pages 41-46", "state": "DRAWING-DERIVED CANDIDATE - NOT INDEPENDENTLY ACCEPTED", "evidence_needed": "independent land-pattern audit; assembler DFM; solder-mask/paste aperture decision; first-article AOI and X-ray", "warning": WARNING},
        {"reference": "JIN1/JOUT1", "footprint": "KiCad JST_VH_B2P-VH", "source": JST_VH, "state": "LIBRARY FOOTPRINT; APPLICATION HELD", "evidence_needed": "independent dimension parity; received fit; conductor/crimp/thermal evidence", "warning": WARNING},
    ])
    holds = [
        ("R156-H01", "Custom RPW land pattern", "Independent footprint audit and assembler DFM acceptance"), ("R156-H02", "PCB stackup/copper", "Selected fabricator stackup, copper weight, laminate, finish and impedance/process limits"),
        ("R156-H03", "Thermal performance", "Physical steady-state and fault-pulse temperatures at released ambient/enclosure"), ("R156-H04", "Forward-current window", "Three physical variants; shunt-calibrated current and register capture"),
        ("R156-H05", "Reverse current", "Magnitude/duration/energy waveforms for single- and multi-axis regeneration"), ("R156-H06", "Clamp pulse energy", "Physical waveform and thermal proof for external Pololu 3771 candidate"),
        ("R156-H07", "Source/contactors/fuse coordination", "Fault current, source foldback, DC interruption and protection study"), ("R156-H08", "JST VH harness", "Exact housing/contact/wire/crimp/tool/length/retention/thermal release"),
        ("R156-H09", "ILM probing", "Total parasitic and probe capacitance below TI 50 pF limit"), ("R156-H10", "Input/output capacitance", "Received capacitance under DC bias plus transient captures"),
        ("R156-H11", "TVS requirement", "Measured interconnect inductance and transients; exact TVS selection if required"), ("R156-H12", "Grounding/PE", "Qualified review of the single DC 0 V/PE bond and test-fixture implementation"),
        ("R156-H13", "EMC/signal interaction", "Conducted/radiated and DXL waveform evidence with branch limiter installed"), ("R156-H14", "HIL/fault injection", "Open/short/reverse/backfeed/welded/failed-passive fault matrix execution"),
        ("R156-H15", "Qualified review", "Named electrical and functional-safety reviewers accept scope and evidence"), ("R156-H16", "Work authorization", "Signed configuration-specific fabrication/assembly/connection/energization authority"),
    ]
    write_csv(RELEASE / "residual-holds.csv", ["hold_id", "topic", "evidence_needed", "state", "warning"], [{"hold_id": a, "topic": b, "evidence_needed": c, "state": "OPEN", "warning": WARNING} for a, b, c in holds])
    tests = [
        ("R156-T01", "Unpowered BOM/variant inspection", "Correct exact MPNs; RILM variant matches traveler"), ("R156-T02", "Continuity and no-short", "Pin/net continuity and no unintended positive/return bridge"),
        ("R156-T03", "Controlled ramp/UVLO/OVLO", "Measured thresholds captured at min/nom/max ambient"), ("R156-T04", "Forward current limiting", "Threshold, response, latch behavior and temperature captured"),
        ("R156-T05", "Startup/inrush", "No nuisance trip or unsafe transient with actual actuator/cable"), ("R156-T06", "Reverse-current regeneration", "Magnitude, duration, energy and destination captured"),
        ("R156-T07", "Fault pulse/short", "Device, connector, trace and clamp remain within qualified limits"), ("R156-T08", "Thermal endurance", "Released duty/ambient/enclosure temperature limits met"),
        ("R156-T09", "Backfeed/contact opening", "No prohibited energized island; waveforms captured"), ("R156-T10", "DXL communications", "Waveform/error margin accepted with all three branches"),
    ]
    write_csv(RELEASE / "test-plan.csv", ["test_id", "test", "acceptance_candidate", "execution_state", "result", "reviewer", "evidence_uri", "warning"], [{"test_id": a, "test": b, "acceptance_candidate": c, "execution_state": "NOT EXECUTED", "result": "", "reviewer": "SELECTION REQUIRED", "evidence_uri": "", "warning": WARNING} for a, b, c in tests])
    write_csv(RELEASE / "test-data-template.csv", ["test_id", "article_serial", "variant", "date", "ambient_C", "input_V", "peak_A", "steady_A", "reverse_A", "pulse_ms", "case_C", "connector_C", "result", "evidence_uri", "reviewer"], [{"test_id": a, "article_serial": "", "variant": "", "date": "", "ambient_C": "", "input_V": "", "peak_A": "", "steady_A": "", "reverse_A": "", "pulse_ms": "", "case_C": "", "connector_C": "", "result": "", "evidence_uri": "", "reviewer": ""} for a, _, _ in tests])
    write_csv(RELEASE / "stackup-and-copper-register.csv", ["item", "candidate", "state", "evidence_needed", "warning"], [
        {"item": "layer count", "candidate": "4 copper layers", "state": "ENCODED REVIEW CANDIDATE", "evidence_needed": "fabricator stackup and qualified review", "warning": WARNING},
        {"item": "power routes", "candidate": "3.0 mm top-copper routes; TI requires path capacity at least 2x full load", "state": "GEOMETRY ONLY", "evidence_needed": "copper weight, temperature rise and fault study", "warning": WARNING},
        {"item": "ground", "candidate": "In1.Cu and B.Cu ground planes; local analog quiet-ground placement candidate", "state": "NOT PE IMPLEMENTATION PROOF", "evidence_needed": "qualified grounding/return audit", "warning": WARNING},
        {"item": "thermal vias", "candidate": "no via-in-pad in P0.1", "state": "SELECTION REQUIRED", "evidence_needed": "assembler DFM and measured thermal/fault performance", "warning": WARNING},
    ])
    status = {"identifier": IDENTIFIER, "review_round": "R156", "date": DATE, "warning": WARNING, "robot_baseline_changed": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "energization_authorized": False, "functional_safety_credit": False, "native_kicad_sheets": 5, "assembly_articles_proposed": 3, "tests_executed": 0, "open_holds": len(holds), "configuration_state": "EVALUATION CARRIER REVIEW CANDIDATE"}
    (RELEASE / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    # Copy controlled native source into the release so the web package cannot imply source synchronization without carrying it.
    controlled = RELEASE / "source"; controlled.mkdir(exist_ok=True)
    for path in OUT.rglob("*"):
        if path.is_file():
            destination = controlled / path.relative_to(OUT); destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, destination)
    write_readme(); write_html()


def write_readme():
    (RELEASE / "README.md").write_text(f"""# {IDENTIFIER}\n\n**{WARNING}**\n\nR156 converts the R155 forward-current limiter into one native, four-layer, single-channel KiCad carrier candidate. Assemble two J1/J2 variants with `RC0603FR-071K65L` and one G1 variant with `RC0603FR-073K32L`. The exact active, passives, headers, diode and test points are source-backed candidates.\n\nThis package does not alter the robot baseline, select a fabricator, authorize ordering or release physical work. KiCad ERC/DRC prove encoded connectivity and geometry only. The custom RPW footprint is drawing-derived and requires independent audit, assembler DFM and first-article evidence. All test results are blank.\n\nGenerate with KiCad 10 Python:\n\n`\"C:\\Program Files\\KiCad\\10.0\\bin\\python.exe\" tools/generate_hr_v0_dxl_protection_carrier_p01.py`\n""", encoding="utf-8")


def write_html():
    (RELEASE / "index.html").write_text(f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>R156 DXL protection carrier</title><style>
:root{{--sky:#7dd3fc;--navy:#0b2a55;--blue:#1557a5;--gold:#f5c242;--paper:#f7fbff;--ink:#10233f;--warn:#fff3bf}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:2rem max(5vw,1rem)}}header p{{max-width:70rem}}main{{max-width:1180px;margin:auto;padding:1.5rem}}.warning{{background:var(--gold);color:#17233a;font-weight:800;padding:1rem;border:3px solid var(--navy)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}section,.card{{background:white;border:2px solid var(--navy);border-radius:14px;padding:1.2rem;margin:1rem 0}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.45rem,3vw,2.2rem)}}.meta{{font-size:14px}}iframe{{width:100%;height:720px;border:2px solid var(--navy);background:white}}img{{max-width:100%;height:auto;border:2px solid var(--navy);border-radius:10px}}a{{color:var(--blue);font-weight:700}}code{{font-size:14px}}@media(max-width:650px){{iframe{{height:520px}}}}
</style></head><body><header><div class=\"meta\">PROJECT BUTTON · R156 · {IDENTIFIER}</div><h1>DXL branch-protection carrier</h1><p>A native single-channel measurement carrier proposed in three controlled assembly variants. It creates the evidence route Sol found missing; it does not make the robot buildable or energizable.</p></header><main><div class=\"warning\">{WARNING}</div>
<section><h2>What changed</h2><div class=\"grid\"><div class=\"card\"><h3>Exact candidate parts</h3><p>TPS259461LRPWR, source-backed passives, B330A-13-F, JST B2P-VH and Keystone test points.</p></div><div class=\"card\"><h3>Three variants</h3><p>Two 1.65 kΩ J1/J2 articles and one 3.32 kΩ G1 article. No substitutions are released.</p></div><div class=\"card\"><h3>Physical evidence route</h3><p>Blank current, reverse-energy, transient, thermal and fault-injection records. Nothing has been executed.</p></div></div></section>
<section><h2>Native schematic</h2><p><a href=\"output/01_protection_core.svg\">Core</a> · <a href=\"output/02_threshold_dividers.svg\">Thresholds</a> · <a href=\"output/03_bypass_and_transients.svg\">Bypass/transients</a> · <a href=\"output/04_measurement_points.svg\">Measurements</a> · <a href=\"source/{PROJECT}.kicad_pro\">KiCad project</a> · <a href=\"source/{PROJECT}.kicad_pcb\">KiCad PCB</a></p><iframe title=\"Native KiCad protection carrier core schematic\" src=\"output/01_protection_core.svg\"></iframe></section>
<section><h2>Board review renders</h2><div class=\"grid\"><figure><img src=\"output/{PROJECT}-top.png\" alt=\"Top render of carrier candidate\"><figcaption>Top review render</figcaption></figure><figure><img src=\"output/{PROJECT}-bottom.png\" alt=\"Bottom render of carrier candidate\"><figcaption>Bottom review render</figcaption></figure></div></section>
<section><h2>Closure records</h2><ul><li><a href=\"assembly-variants.csv\">Assembly variants</a></li><li><a href=\"footprint-audit.csv\">Footprint audit</a></li><li><a href=\"residual-holds.csv\">Residual holds</a></li><li><a href=\"test-plan.csv\">Test plan</a></li><li><a href=\"primary-source-register.csv\">Primary sources</a></li><li><a href=\"validation/{PROJECT}-erc.rpt\">ERC report</a></li><li><a href=\"validation/{PROJECT}-drc.rpt\">DRC report</a></li></ul></section>
</main></body></html>""", encoding="utf-8")


def manifest():
    rows = []
    for path in sorted(RELEASE.rglob("*")):
        if path.is_file() and path.name != "file-manifest.csv": rows.append({"file": path.relative_to(RELEASE).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()})
    write_csv(RELEASE / "file-manifest.csv", ["file", "sha256"], rows)


def main() -> int:
    model = load_model(); items = components(model)
    if OUT.exists(): shutil.rmtree(OUT)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    write_schematic(model, items); write_board(items); run_kicad(); release_files(items); manifest()
    print(f"Generated {IDENTIFIER}: 5 native sheets, {sum(item.quantity for item in items)} physical BOM placements, 3 controlled variants")
    print(WARNING); print("No physical test or qualified approval is claimed.")
    return 0


if __name__ == "__main__": raise SystemExit(main())
