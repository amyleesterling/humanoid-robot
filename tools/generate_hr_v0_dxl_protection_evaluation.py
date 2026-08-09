"""Generate the HR-V0 DXL branch-protection evaluation package.

This is a connected native KiCad application candidate and an evidence route.
It does not select hardware for the robot, release a PCB, or authorize powered
work.  The TPS25946 limits current only from IN to OUT while enabled; reverse
current and the external shunt therefore remain physical qualification gates.
"""

from __future__ import annotations

import csv
import hashlib
import html
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KICAD = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-eval"
RELEASE = ROOT / "release" / "hr-v0" / "dxl-protection-evaluation-p0.1"
PROJECT = "hr-v0-dxl-protection-eval"
IDENTIFIER = "HR-V0-DXL-PROT-EVAL-P0.1"
REVISION = "DXL-PROT-EVAL-P0.1"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
TI_URL = "https://www.ti.com/lit/ds/symlink/tps25946.pdf"
TI_PART_URL = "https://www.ti.com/product/TPS25946/part-details/TPS259461LRPWR"
POLOLU_URL = "https://www.pololu.com/product/3771"
MEAN_WELL_URL = "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF"
JST_URL = "https://www.jst-mfg.com/product/pdf/eng/eEH.pdf"
JST_VH_URL = "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf"
ROBOTIS_URL = "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/"


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("dxl_protection_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load KiCad schematic model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.PROJECT = PROJECT
    module.REV = REVISION
    module.PROJECT_TITLE = "PROJECT BUTTON HR-V0 DXL BRANCH-PROTECTION EVALUATION"
    module.PROJECT_SUBTITLE = "Forward current limiting plus short-pulse regenerative clamp candidate; reverse-current proof remains open."
    module.DATE = DATE
    return module


def channel_components(model, index: int):
    Component = model.Component
    pn = model.pn
    axis = {1: "J1 SHOULDER", 2: "J2 ELBOW", 3: "G1 GRIPPER"}[index]
    current_resistor = "1.65 kOhm 1%" if index in (1, 2) else "3.32 kOhm 1%"
    current_basis = "1.8-2.2 A catalog threshold before resistor tolerance" if index in (1, 2) else "0.85-1.15 A catalog threshold before resistor tolerance"
    prefix = f"B{index}"
    source = f"{prefix}_FUSED_IN"
    limited = f"{prefix}_LIMITED_OUT"
    return [
        Component(f"JIN{index}", f"JST B2P-VH {axis} fused input boundary",
                  [pn(f"JIN{index}", "1", "FUSED VDD IN", source, "right"),
                   pn(f"JIN{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "left")],
                  "EXACT FAMILY CANDIDATE - HARNESS/CONTACT SELECTION REQUIRED",
                  "Input from the separately fused branch. Exact mating housing, contact, conductor, crimp, retention and thermal evidence remain open.",
                  JST_VH_URL, "JST VH family application remains held; this evaluation schematic does not release a harness.",
                  position=(50, 65), width=72),
        Component(f"U{index}", "TI TPS259461LRPWR latch-off bidirectional-on-state eFuse",
                  [pn(f"U{index}", "1", "EN/UVLO", f"{prefix}_UVLO", "left"),
                   pn(f"U{index}", "2", "OVLO", f"{prefix}_OVLO", "left"),
                   pn(f"U{index}", "3", "SPLYGD", f"{prefix}_SPLYGD_DIAG", "left"),
                   pn(f"U{index}", "4", "FLT", f"{prefix}_FLT_DIAG", "left"),
                   pn(f"U{index}", "5", "IN", source, "left"),
                   pn(f"U{index}", "6", "OUT", limited, "right"),
                   pn(f"U{index}", "7", "dVdt", f"{prefix}_DVDT", "right"),
                   pn(f"U{index}", "9", "ILM", f"{prefix}_ILM", "right"),
                   pn(f"U{index}", "10", "ITIMER OPEN", f"INTENTIONALLY_OPEN_{prefix}_ITIMER", "right")],
                  "EXACT EVALUATION CANDIDATE - NOT SELECTED FOR ROBOT",
                  "Exact active TI orderable candidate. Forward overcurrent limiting only; no OUT-to-IN overcurrent protection while enabled. RPW land pattern, assembly process, thermal design and received validation remain open.",
                  TI_PART_URL, "TI product page active and datasheet SLVSGA8B, April 2022; rechecked 2026-08-09.",
                  position=(205, 90), width=100, height=72),
        Component(f"U{index}G", f"U{index} pin 8 GND cross-reference",
                  [pn(f"U{index}G", "8", "GND", "ACT_0V_PE_BONDED", "right")],
                  "CONTACT CROSS-REFERENCE - SAME DEVICE", f"Pin 8 belongs to the same TPS259461LRPWR represented by U{index}; do not count as another BOM device.",
                  TI_URL, "Split graphical unit preserves the exact pin while preventing adjacent global-label ambiguity.",
                  position=(50, 145), width=52, quantity=0),
        Component(f"JOUT{index}", f"JST B2P-VH {axis} limited output boundary",
                  [pn(f"JOUT{index}", "1", "LIMITED VDD OUT", limited, "left"),
                   pn(f"JOUT{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT FAMILY CANDIDATE - DXL-STAR INTERFACE HOLD",
                  "Output to the existing DXL-STAR protected-power input. Exact harness and physical integration remain open.",
                  JST_VH_URL, "JST VH family evidence only; no cable or contact application release.",
                  position=(350, 65), width=72),
        Component(f"RILM{index}", current_resistor,
                  [pn(f"RILM{index}", "1", "ILM", f"{prefix}_ILM", "left"),
                   pn(f"RILM{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "VALUE DERIVED - EXACT MPN SELECTION REQUIRED",
                  f"TI catalog basis: {current_basis}. The physical resistor order code and tolerance/temperature proof remain open.",
                  TI_URL, "TI equation and guaranteed threshold rows; no passive order code inferred.",
                  position=(150, 145), width=66),
        Component(f"RUVT{index}", "365 kOhm 1% UVLO upper",
                  [pn(f"RUVT{index}", "1", "IN", source, "left"), pn(f"RUVT{index}", "2", "UVLO", f"{prefix}_UVLO", "right")],
                  "VALUE DERIVED - EXACT MPN SELECTION REQUIRED", "Nominal 10 V turn-on divider upper resistor; tolerance screen only.", TI_URL,
                  "Derived with TI VUVLO limits; exact resistor selection remains open.", position=(50, 190), width=66),
        Component(f"RUVB{index}", "49.9 kOhm 1% UVLO lower",
                  [pn(f"RUVB{index}", "1", "UVLO", f"{prefix}_UVLO", "left"), pn(f"RUVB{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "VALUE DERIVED - EXACT MPN SELECTION REQUIRED", "Nominal 10 V turn-on divider lower resistor; tolerance screen only.", TI_URL,
                  "Derived with TI VUVLO limits; exact resistor selection remains open.", position=(150, 190), width=66),
        Component(f"ROVT{index}", "470 kOhm 1% OVLO upper",
                  [pn(f"ROVT{index}", "1", "IN", source, "left"), pn(f"ROVT{index}", "2", "OVLO", f"{prefix}_OVLO", "right")],
                  "TI EXAMPLE VALUE - EXACT MPN SELECTION REQUIRED", "TI 14 V application-divider example; project tolerance and transient validation remain open.", TI_URL,
                  "TI design example, not project application approval.", position=(250, 190), width=66),
        Component(f"ROVB{index}", "44.2 kOhm 1% OVLO lower",
                  [pn(f"ROVB{index}", "1", "OVLO", f"{prefix}_OVLO", "left"), pn(f"ROVB{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "TI EXAMPLE VALUE - EXACT MPN SELECTION REQUIRED", "TI 14 V application-divider example; project tolerance and transient validation remain open.", TI_URL,
                  "TI design example, not project application approval.", position=(350, 190), width=66),
        Component(f"CDV{index}", "2.2 nF dVdt candidate",
                  [pn(f"CDV{index}", "1", "dVdt", f"{prefix}_DVDT", "left"), pn(f"CDV{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "VALUE CANDIDATE - EXACT MPN SELECTION REQUIRED", "Slew-rate candidate; received actuator startup and thermal behavior remain open.", TI_URL,
                  "Value appears in TI application example; no project suitability inferred.", position=(50, 235), width=66),
        Component(f"CIN{index}", "0.1 uF minimum 25 V X7R input bypass candidate",
                  [pn(f"CIN{index}", "1", "IN", source, "left"), pn(f"CIN{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "REQUIREMENT FIXED - EXACT MPN SELECTION REQUIRED", "Locate at IN/GND; capacitance under bias, ripple and layout remain open.", TI_URL,
                  "TI recommends 0.1 uF or greater at IN; exact component not inferred.", position=(150, 235), width=66),
        Component(f"COUT{index}", "1.0 uF minimum 25 V X7R output bypass candidate",
                  [pn(f"COUT{index}", "1", "OUT", limited, "left"), pn(f"COUT{index}", "2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "REQUIREMENT FIXED - EXACT MPN SELECTION REQUIRED", "Locate at OUT/GND; actuator input capacitance and transient loop remain open.", TI_URL,
                  "TI recommends 1 uF or greater at OUT for inductive-load transients; exact component not inferred.", position=(250, 235), width=66),
        Component(f"TPILM{index}", "Harwin S1751-46R ILM test point",
                  [pn(f"TPILM{index}", "1", "ILM", f"{prefix}_ILM", "right")],
                  "EXACT TEST-POINT CANDIDATE - CAPACITIVE-LOADING HOLD", "Probe only under a released test method; total ILM capacitance must remain below TI's 50 pF stability limit.",
                  "https://www.harwin.com/products/S1751-46R", "Existing controlled Harwin test-point identity; bench probe loading remains open.", position=(250, 145), width=66),
        Component(f"TPFLT{index}", "Harwin S1751-46R FLT diagnostic test point",
                  [pn(f"TPFLT{index}", "1", "FLT open drain", f"{prefix}_FLT_DIAG", "right")],
                  "EXACT TEST-POINT CANDIDATE - NO INSTALLED PULLUP", "Open-drain diagnostic only. External pullup/interface is deliberately absent and SELECTION REQUIRED.",
                  "https://www.harwin.com/products/S1751-46R", "No safety or motion credit.", position=(350, 145), width=66),
    ]


def shunt_components(model):
    Component = model.Component
    pn = model.pn
    return [
        Component("SRC1", "Mean Well GST280A12-C6P source boundary",
                  [pn("SRC1", "+", "+12 V", "ACT_12V_SOURCE", "right"), pn("SRC1", "-", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT SOURCE CANDIDATE - REGENERATION APPLICATION HOLD", "12 V ±5% catalog source; reverse-current sinking is not documented.",
                  MEAN_WELL_URL, "GST280A-SPEC 2025-03-28; final equipment and regeneration behavior remain open.", position=(60, 80), width=88),
        Component("KCHAIN1", "K1/K2 redundant interruption output boundary",
                  [pn("KCHAIN1", "IN", "SOURCE", "ACT_12V_SOURCE", "left"), pn("KCHAIN1", "OUT", "SAFE BUS", "ACT_12V_BUS", "right")],
                  "SYSTEM BOUNDARY - CONTACT APPLICATION HOLD", "Represents the existing two-contactor series path only; no added safety credit.",
                  "", "Current V3-P1.14 boundary; loaded interruption and regeneration remain open.", position=(205, 80), width=88),
        Component("SH1", "Pololu item 3771 13.2 V 1.50 Ohm 15 W shunt regulator",
                  [pn("SH1", "+", "BUS +", "ACT_12V_BUS", "left"), pn("SH1", "-", "RETURN", "ACT_0V_PE_BONDED", "left")],
                  "EXACT EVALUATION CANDIDATE - SHORT PULSES ONLY", "Install across the post-contactor bus for evaluation. Manufacturer warns continuous above-setpoint voltage can destroy the board in under one second.",
                  POLOLU_URL, "Pololu item 3771 active/preferred page accessed 2026-08-09; fixed setpoint ±3%, pulse application only.", position=(350, 80), width=98),
        Component("TPBUS1", "Bus-voltage measurement point - SELECTION REQUIRED",
                  [pn("TPBUS1", "1", "ACTUATOR BUS", "ACT_12V_BUS", "right")],
                  "SELECTION REQUIRED", "Kelvin/probe method, category, spacing and fixture remain open.", position=(120, 175), width=85),
        Component("TPRET1", "Return measurement point - SELECTION REQUIRED",
                  [pn("TPRET1", "1", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "SELECTION REQUIRED", "Kelvin/probe method, category, spacing and fixture remain open.", position=(290, 175), width=85),
    ]


def write_kicad(model) -> None:
    KICAD.mkdir(parents=True, exist_ok=True)
    sheets = []
    for index in (1, 2, 3):
        sheet = model.Sheet(index, f"0{index}_branch_{index}.kicad_sch", f"Branch {index} TPS259461L evaluation circuit",
                            "Exact eFuse pinout with derived dividers, current setting, bypassing and diagnostic test points.")
        sheet.components = channel_components(model, index)
        sheet.notes = [
            "ITIMER is deliberately open for the minimum possible overcurrent delay; it is not a released timing value.",
            "TPS25946 protects overcurrent only from IN to OUT. Reverse current is not limited during ON state.",
            "All passive order codes, RPW footprint/land pattern, PCB thermal design, assembly process and physical evidence remain SELECTION REQUIRED.",
        ]
        sheets.append(sheet)
    sheet = model.Sheet(4, "04_regeneration_clamp.kicad_sch", "Source and regenerative-clamp evaluation boundary",
                        "The short-pulse shunt candidate is across the post-contactor bus; source sink behavior remains unproved.")
    sheet.components = shunt_components(model)
    sheet.notes = [
        "Pololu item 3771 is a short-pulse evaluation candidate, not a continuous dump load or safety function.",
        "The 12 V source may reach 12.6 V by tolerance; the shunt setpoint may be 12.804 V at -3%. Nuisance margin requires received measurement.",
        "Contact opening, eFuse UVLO/OVLO action, stored energy and three-axis simultaneous regeneration require captured waveforms.",
    ]
    sheets.append(sheet)

    all_components = [component for sheet in sheets for component in sheet.components]
    net_counts = Counter(pin.net for component in all_components for pin in component.pins)
    wire_numbers = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr-v0-dxl-protection-eval")
    project_data = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [{"name": "Default", "priority": 2147483647, "clearance": 0.2, "track_width": 0.25,
                                       "via_diameter": 0.8, "via_drill": 0.4}], "meta": {"version": 3}},
        "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REVISION},
    }
    (KICAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(component).replace(f'(symbol "PBV3:{component.ref}"', f'(symbol "{component.ref}"', 1)
               for component in all_components]
    (KICAD / f"{PROJECT}.kicad_sym").write_text(
        '(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '
        + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (KICAD / "sym-lib-table").write_text(
        f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 DXL protection evaluation symbols"))\n)\n',
        encoding="utf-8")
    (KICAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (KICAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wire_numbers), encoding="utf-8")

    with (KICAD / "bom.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reference", "value", "quantity", "status", "evidence"])
        for component in all_components:
            writer.writerow([component.ref, component.value, component.quantity, component.status, component.evidence])
    with (KICAD / "terminal-schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sheet", "reference", "terminal", "pin_name", "net", "status"])
        for sheet in sheets:
            for component in sheet.components:
                for pin in component.pins:
                    writer.writerow([sheet.number, component.ref, pin.number, pin.name, pin.net, component.status])


def run_kicad() -> None:
    output = KICAD / "output"
    validation = KICAD / "validation"
    output.mkdir(exist_ok=True)
    validation.mkdir(exist_ok=True)
    for path in (*output.glob("*.svg"), *output.glob("*.pdf")):
        path.unlink()
    cli = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(KICAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(KICAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "pdf", "--output", str(output / f"{PROJECT}-preliminary.pdf"), str(KICAD / f"{PROJECT}.kicad_sch")],
        [str(cli), "sch", "export", "svg", "--output", str(output), str(KICAD / f"{PROJECT}.kicad_sch")],
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
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")


def calculations():
    uv_min = 1.183 * ((365 * 0.99) + (49.9 * 1.01)) / (49.9 * 1.01)
    uv_max = 1.223 * ((365 * 1.01) + (49.9 * 0.99)) / (49.9 * 0.99)
    ov_min = 1.183 * ((470 * 0.99) + (44.2 * 1.01)) / (44.2 * 1.01)
    ov_max = 1.223 * ((470 * 1.01) + (44.2 * 0.99)) / (44.2 * 0.99)
    return [
        ("CAL-001", "J1/J2 forward current threshold with 1% RILM screen", "1.782178", "2.222222", "A", "TI 1.8-2.2 A guaranteed row adjusted inversely for ±1% resistor; application screen only"),
        ("CAL-002", "G1 forward current threshold with 1% RILM screen", "0.841584", "1.161616", "A", "TI 0.85-1.15 A guaranteed row adjusted inversely for ±1% resistor; application screen only"),
        ("CAL-003", "UVLO rising threshold screen", f"{uv_min:.6f}", f"{uv_max:.6f}", "V", "TI threshold min/max plus 365k/49.9k ±1% corner screen"),
        ("CAL-004", "OVLO rising threshold screen", f"{ov_min:.6f}", f"{ov_max:.6f}", "V", "TI threshold min/max plus 470k/44.2k ±1% corner screen"),
        ("CAL-005", "Pololu 3771 setpoint range", "12.804000", "13.596000", "V", "13.2 V ±3% manufacturer record"),
        ("CAL-006", "Mean Well source tolerance range", "11.400000", "12.600000", "V", "12 V ±5% manufacturer record; ripple considered separately"),
        ("CAL-007", "conservative source high plus full published ripple", "", "12.720000", "V", "12.6 V + 0.12 Vpp conservative screen; not a waveform prediction"),
        ("CAL-008", "minimum static shunt/source screen margin", "0.084000", "", "V", "12.804 - 12.720; received nuisance-clamp evidence required"),
        ("CAL-009", "shunt current at nominal setpoint and resistance", "8.800000", "", "A", "13.2 V / 1.50 ohm; not a guaranteed sink-current rating"),
        ("CAL-010", "instantaneous resistor dissipation arithmetic", "116.160000", "", "W", "13.2^2 / 1.50; demonstrates pulse-only boundary, not allowed duration or energy"),
    ]


def write_release() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    sources = [
        ("SRC-001", "Texas Instruments", "TPS25946 datasheet SLVSGA8B Rev B", "2022-04-04", TI_URL, "2.7-23 V; bidirectional ON; reverse blocking OFF; forward-only current limit; exact pinout; threshold rows; layout requirements"),
        ("SRC-002", "Texas Instruments", "TPS259461LRPWR orderable page", DATE, TI_PART_URL, "Active exact latch-off RPW orderable candidate; no project application approval"),
        ("SRC-003", "Pololu", "Item 3771 shunt regulator product page", DATE, POLOLU_URL, "13.2 V fixed ±3%; 1.50 ohm; 15 W relative average; occasional tens-of-ms pulses only"),
        ("SRC-004", "MEAN WELL", "GST280A series specification", "2025-03-28", MEAN_WELL_URL, "GST280A12-C6P 12 V ±5%, 21 A, 120 mVpp; reverse-current sinking not specified"),
        ("SRC-005", "JST", "EH series catalog", DATE, JST_URL, "3 A at AWG22 series condition; downstream actuator-connector application remains unproved"),
        ("SRC-006", "JST", "VH series catalog", DATE, JST_VH_URL, "B2P-VH family identity only; mating parts, conductor, crimp and thermal application remain unproved"),
        ("SRC-007", "ROBOTIS", "XM540-W270 e-Manual", DATE, ROBOTIS_URL, "10-14.8 V input; current-limit register basis; physical external current remains unproved"),
    ]
    decisions = [
        ("DEC-001", "TPS259461LRPWR", "RETAIN AS EXACT EVALUATION CANDIDATE", "Guaranteed forward threshold candidates can remain below the 3 A connector basis", "Reverse current is not limited; PCB/thermal/startup/short-circuit evidence absent"),
        ("DEC-002", "TPS25947 true reverse-current-blocking family", "REJECT FOR CURRENT REGENERATIVE PATH", "Always-on reverse blocking would isolate returned energy at the actuator side", "Could be reconsidered only with a validated local energy sink and overvoltage proof"),
        ("DEC-003", "Pololu item 3771", "RETAIN AS EXACT SHORT-PULSE EVALUATION CANDIDATE", "13.2 V ±3% is below the 14.8 V actuator maximum and intended for motor-regeneration spikes", "Pulse energy/duration, simultaneous axes, mounting, ventilation and failure behavior unproved"),
        ("DEC-004", "existing fuse-only path", "REJECT AS COMPLETE CONNECTOR-OVERLOAD CONTROL", "Time-current clearing does not set the intended operating current envelope", "Fuses remain required for fault coordination after source/fault evidence"),
        ("DEC-005", "robot release baseline", "NO CHANGE", "Candidate circuit has no PCB, passive MPNs, physical data or qualified acceptance", "Keep external current evidence SELECTION REQUIRED and all work-authority flags false"),
    ]
    interface = [
        ("IF-001", "F1 output", "JIN1.1", "B1_FUSED_IN", "candidate inserted boundary; not current V3 release"),
        ("IF-002", "JOUT1.1", "DXL-STAR JP1.1", "B1_LIMITED_OUT to J1_VDD", "candidate harness/board integration required"),
        ("IF-003", "F2 output", "JIN2.1", "B2_FUSED_IN", "candidate inserted boundary; not current V3 release"),
        ("IF-004", "JOUT2.1", "DXL-STAR JP2.1", "B2_LIMITED_OUT to J2_VDD", "candidate harness/board integration required"),
        ("IF-005", "F3 output", "JIN3.1", "B3_FUSED_IN", "candidate inserted boundary; not current V3 release"),
        ("IF-006", "JOUT3.1", "DXL-STAR JP3.1", "B3_LIMITED_OUT to J3_VDD", "candidate harness/board integration required"),
        ("IF-007", "SH1.+", "post-K2 ACT_12V_BUS", "ACT_12V_BUS", "parallel short-pulse clamp candidate"),
        ("IF-008", "all returns and SH1.-", "ACT_0V_PE_BONDED", "ACT_0V_PE_BONDED", "single controlled return net; physical star/bond proof remains open"),
    ]
    tests = [
        ("TST-001", "source and candidate receiving identity", "unpowered", "part marking, package, values, polarity and lot records match", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-002", "schematic-to-article continuity and resistance", "unpowered", "all terminal paths and deliberate opens match; no shorts", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-003", "UVLO/OVLO thresholds per channel", "current-limited bench source, no actuator", "measured rising/falling thresholds within qualified limits", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-004", "forward current limiting per channel", "electronic load, no actuator", "threshold, overshoot, foldback, latch and thermal response accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-005", "output short-circuit response", "protected fixture, no actuator", "peak, duration, temperature and latch response accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-006", "reverse-current injection", "bidirectional source/load, no actuator", "OUT-to-IN waveform proves absence/bounds of reverse limit and bus effect", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-007", "shunt threshold and pulse", "current-limited source, no actuator", "setpoint, pulse current, temperature and recovery accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-008", "source plus shunt nuisance margin", "received GST280A12-C6P, no actuator", "all line/load/ripple cases avoid nuisance clamp", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-009", "single received actuator startup", "guarded fixture", "startup, current limit, voltage and diagnostic waveforms accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-010", "single-axis regeneration", "guarded fixture", "reverse current, bus voltage, shunt pulse and temperatures accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-011", "K1/K2 dropout during accepted motion", "guarded fixture", "bus decay, eFuse state, shunt pulse and restart prevention accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-012", "simultaneous worst-case duty and thermal", "guarded representative assembly", "all connector/PCB/eFuse/shunt/source temperatures and waveforms accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-013", "DXL communication integrity", "representative harness", "waveform, error rate, latency and watchdog timing accepted", "NOT EXECUTED", "NOT AUTHORIZED"),
        ("TST-014", "fault injection and HIL", "received complete electrical assembly", "open/short/drift/thermal/unplug/brownout cases fail closed", "NOT EXECUTED", "NOT AUTHORIZED"),
    ]
    holds = [
        ("PROT-HOLD-001", "independent acceptance of current primary-source identity"),
        ("PROT-HOLD-002", "exact passive order codes, voltage coefficients, temperature coefficients and derating"),
        ("PROT-HOLD-003", "exact TI RPW land pattern, paste, assembly process and inspection acceptance"),
        ("PROT-HOLD-004", "PCB stackup, copper, thermal vias, trace widths, clearances and enclosure airflow"),
        ("PROT-HOLD-005", "exact terminal, harness, conductor, crimp, strain-relief and retention selection"),
        ("PROT-HOLD-006", "forward threshold/overshoot/foldback/short-circuit physical evidence"),
        ("PROT-HOLD-007", "reverse-current magnitude and duration physical evidence"),
        ("PROT-HOLD-008", "Pololu shunt pulse-energy, duration, cooling, simultaneous-axis and failure evidence"),
        ("PROT-HOLD-009", "GST280A12-C6P nuisance margin and regeneration interaction"),
        ("PROT-HOLD-010", "K1/K2 opening and bus-decay interaction"),
        ("PROT-HOLD-011", "received actuator startup, duty, torque and performance adequacy"),
        ("PROT-HOLD-012", "JST EH connector/cable temperature, voltage drop and retention"),
        ("PROT-HOLD-013", "F0/F1-F3 exact fuse and fault-clearing coordination"),
        ("PROT-HOLD-014", "DXL waveform, error-rate, EMC and watchdog timing"),
        ("PROT-HOLD-015", "main V3 and DXL-STAR native source integration if candidate is accepted"),
        ("PROT-HOLD-016", "received HIL fault injection"),
        ("PROT-HOLD-017", "qualified electrical/controls/mechanical review and independent acceptance"),
        ("PROT-HOLD-018", "separate written procurement/fabrication/assembly/connection/motion/energization authorization"),
    ]
    acceptance = [(f"PROT-A-{index:03d}", description, "", "NOT EXECUTED", "", "") for index, (_, description) in enumerate(holds, 1)]

    def write_csv(name, header, rows):
        with (RELEASE / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    write_csv("primary-source-register.csv", ["source_id", "manufacturer", "document", "revision_or_access_date", "url", "verified_scope"], sources)
    write_csv("candidate-decision-register.csv", ["decision_id", "candidate", "disposition", "reason", "remaining_boundary"], decisions)
    write_csv("system-interface-map.csv", ["interface_id", "from", "to", "net_or_mapping", "status"], interface)
    write_csv("calculation-register.csv", ["calculation_id", "quantity", "minimum", "maximum", "unit", "basis"], calculations())
    write_csv("test-plan.csv", ["test_id", "test", "configuration", "pass_basis", "result", "authorization"], tests)
    write_csv("residual-holds.csv", ["hold_id", "description", "state", "warning"], [(key, value, "OPEN", WARNING) for key, value in holds])
    write_csv("acceptance-matrix.csv", ["acceptance_id", "topic", "evidence_uri", "result", "approver", "date"], acceptance)
    write_csv("test-data-template.csv", ["test_id", "article_ids", "instrument_ids", "ambient_c", "configuration_hash", "data_uri", "result", "operator", "reviewer", "date"],
              [(row[0], "", "", "", "", "", "NOT EXECUTED", "", "", "") for row in tests])

    status = {
        "identifier": IDENTIFIER, "round": "R155", "date": DATE,
        "warning": WARNING, "selected_for_robot": False, "external_current_limit_released": False,
        "pcb_released": False, "procurement_authorized": False, "fabrication_authorized": False,
        "assembly_authorized": False, "connection_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False,
        "native_kicad_sheets": 5, "exact_evaluation_devices": 2, "open_holds": len(holds),
        "physical_tests_executed": 0,
    }
    (RELEASE / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (RELEASE / "README.md").write_text(
        f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR155 provides a connected native KiCad evaluation schematic for three exact TPS259461LRPWR candidates and one Pololu item 3771 short-pulse shunt candidate. It derives forward-current, UVLO, OVLO and setpoint screens and supplies blank test evidence. It deliberately does not revise the robot release baseline because reverse current, shunt pulse energy, PCB/passive definition and all physical evidence remain open.\n",
        encoding="utf-8")

    decisions_html = "".join(f"<tr><td>{html.escape(row[0])}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[2])}</td><td>{html.escape(row[4])}</td></tr>" for row in decisions)
    holds_html = "".join(f"<li><strong>{html.escape(key)}</strong>{html.escape(value)}</li>" for key, value in holds)
    diagrams = [
        ("Branch 1", "../../../electrical/kicad/hr-v0-dxl-protection-eval/output/hr-v0-dxl-protection-eval-01_branch_1.svg"),
        ("Branch 2", "../../../electrical/kicad/hr-v0-dxl-protection-eval/output/hr-v0-dxl-protection-eval-02_branch_2.svg"),
        ("Branch 3", "../../../electrical/kicad/hr-v0-dxl-protection-eval/output/hr-v0-dxl-protection-eval-03_branch_3.svg"),
        ("Regeneration clamp", "../../../electrical/kicad/hr-v0-dxl-protection-eval/output/hr-v0-dxl-protection-eval-04_regeneration_clamp.svg"),
    ]
    buttons = "".join(f'<button type="button" data-src="{path}">{label}</button>' for label, path in diagrams)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--sky:#b9e8ff;--navy:#082f58;--blue:#12669f;--gold:#f2b928;--paper:#f7fcff;--hold:#fff0b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.2rem,5.2vw,4.6rem);line-height:1.04;max-width:20ch;margin:.25rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.6rem)}}main{{max-width:1400px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:var(--hold);border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1.1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.tabs{{display:flex;gap:.7rem;flex-wrap:wrap;margin:1rem 0}}button{{font:700 16px/1.2 Arial;padding:.8rem 1rem;border:2px solid var(--navy);border-radius:.6rem;background:white;color:var(--navy);cursor:pointer}}button.active{{background:var(--navy);color:white}}.diagram{{display:block;width:100%;min-height:640px;border:3px solid #8bb8d1;border-radius:.8rem;background:white}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:980px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}code,.meta{{font-size:14px}}li{{margin:.75rem 0}}li strong{{display:block;font-size:14px}}a{{color:#075a96}}@media(max-width:600px){{.diagram{{min-height:500px}}}}</style></head><body><header><div class="meta">{IDENTIFIER} · R155 · {DATE}</div><h1>Limit motoring current. Give regeneration somewhere to go.</h1><div class="warning">{WARNING}. Exact candidates are for evaluation only; no robot baseline or work authority changes.</div></header><main><p>Three latch-off TPS259461L candidates provide forward current limiting. A 13.2 V Pololu shunt candidate sits across the post-contactor bus to evaluate short regenerative pulses. The eFuse does not limit reverse current, and the shunt is not a continuous dump load.</p><section class="grid"><article><b>5</b>native KiCad sheets</article><article><b>2</b>exact device candidates</article><article><b>14</b>blank physical tests</article><article><b>18</b>open holds</article></section><div class="boundary"><h2>The decisive limitation</h2><p>TI specifies current limiting only from IN to OUT. Returned energy can flow from OUT to IN while enabled. Pololu warns item 3771 is for occasional short pulses and that continuous above-setpoint voltage can destroy it quickly. The combination therefore remains a measured candidate, not a released protection function.</p></div><h2>Native schematic viewer</h2><div class="tabs">{buttons}</div><iframe id="diagram" class="diagram" title="Native KiCad branch-protection schematic" src="{diagrams[0][1]}"></iframe><h2>Candidate decisions</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Candidate</th><th>Disposition</th><th>Remaining boundary</th></tr></thead><tbody>{decisions_html}</tbody></table></div><div class="boundary"><h2>Eighteen holds remain open</h2><ol>{holds_html}</ol></div><p><a href="calculation-register.csv">calculations</a> · <a href="system-interface-map.csv">interface map</a> · <a href="test-plan.csv">test plan</a> · <a href="acceptance-matrix.csv">acceptance matrix</a> · <a href="primary-source-register.csv">sources</a></p></main><script>const buttons=[...document.querySelectorAll('button[data-src]')],viewer=document.getElementById('diagram');function select(button){{buttons.forEach(item=>item.classList.toggle('active',item===button));viewer.src=button.dataset.src}}buttons.forEach(button=>button.addEventListener('click',()=>select(button)));select(buttons[0]);</script></body></html>'''
    (RELEASE / "index.html").write_text(page, encoding="utf-8")


def write_manifests() -> None:
    for base, name in ((KICAD, "SOURCE-MANIFEST.csv"), (RELEASE, "file-manifest.csv")):
        rows = []
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.name != name:
                rows.append((path.relative_to(base).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper(), path.stat().st_size))
        with (base / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["file", "sha256", "size_bytes"])
            writer.writerows(rows)


def main() -> int:
    model = load_model()
    write_kicad(model)
    run_kicad()
    write_release()
    write_manifests()
    print(f"Generated {IDENTIFIER}: 5 native KiCad sheets / 14 blank tests / 18 open holds")
    print(WARNING)
    print("No robot selection, PCB release, physical evidence, work authority or safety credit was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
