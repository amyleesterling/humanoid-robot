"""Generate the native HR-30 whole-body electrical P0.1 KiCad project.

The project is a connected, editable whole-body architecture.  It deliberately
uses logical terminal identifiers wherever exact device, connector, protection
or package pins remain unselected.  ERC therefore checks encoded connectivity
and annotation only; it is not permission to connect or energize hardware.
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


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
ECAD = PACKAGE / "electrical" / "kicad" / "hr30-whole-body-electrical-p0.1"
PROJECT = "hr30-whole-body-electrical-p0.1"
IDENTIFIER = "HR30-WHOLE-BODY-ELECTRICAL-P0.1"
REV = "P0.1"
DATE = "2026-08-14"
WARNING = "PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")


BUS_AXES = {
    "RS-LLEG": ["L_HIP_YAW", "L_HIP_ROLL", "L_HIP_PITCH", "L_KNEE_PITCH", "L_ANKLE_PITCH", "L_ANKLE_ROLL"],
    "RS-RLEG": ["R_HIP_YAW", "R_HIP_ROLL", "R_HIP_PITCH", "R_KNEE_PITCH", "R_ANKLE_PITCH", "R_ANKLE_ROLL"],
    "RS-LARM": ["L_SHOULDER_PITCH", "L_SHOULDER_ROLL", "L_ELBOW_PITCH"],
    "RS-RARM": ["R_SHOULDER_PITCH", "R_SHOULDER_ROLL", "R_ELBOW_PITCH"],
    "RS-WAIST": ["WAIST_YAW"],
    "TTL-LDIST": ["L_WRIST_ROTATION", "L_GRIPPER"],
    "TTL-RDIST": ["R_WRIST_ROTATION", "R_GRIPPER"],
    "TTL-HEAD": ["HEAD_PAN", "HEAD_TILT"],
}

UART_ALLOCATIONS = {
    "RS-LLEG": {"carrier": "A", "uart": "USART1", "tx": ("PA9", "101", "AF7"), "rx": ("PA10", "102", "AF7"), "de": ("PA12", "104", "AF7")},
    "RS-RLEG": {"carrier": "A", "uart": "USART2", "tx": ("PD5", "119", "AF7"), "rx": ("PD6", "122", "AF7"), "de": ("PD4", "118", "AF7")},
    "RS-LARM": {"carrier": "A", "uart": "USART3", "tx": ("PD8", "77", "AF7"), "rx": ("PD9", "78", "AF7"), "de": ("PD12", "81", "AF7")},
    "RS-RARM": {"carrier": "A", "uart": "USART6", "tx": ("PC6", "96", "AF7"), "rx": ("PC7", "97", "AF7"), "de": ("PG8", "93", "AF7")},
    "RS-WAIST": {"carrier": "B", "uart": "UART4", "tx": ("PC10", "111", "AF8"), "rx": ("PC11", "112", "AF8"), "de": ("PA15", "110", "AF8")},
    "TTL-LDIST": {"carrier": "B", "uart": "UART5", "tx": ("PC12", "113", "AF8"), "rx": ("PD2", "116", "AF8"), "de": ("PC8", "98", "AF8")},
    "TTL-RDIST": {"carrier": "B", "uart": "UART7", "tx": ("PE8", "62", "AF7"), "rx": ("PE7", "61", "AF7"), "de": ("PE9", "63", "AF7")},
    "TTL-HEAD": {"carrier": "B", "uart": "UART8", "tx": ("PE1", "142", "AF8"), "rx": ("PE0", "141", "AF8"), "de": ("PD15", "86", "AF8")},
}

ST_H743_SOURCE = "https://www.st.com/resource/en/datasheet/stm32h742bg.pdf"
TI_ISOW1432_SOURCE = "https://www.ti.com/lit/ds/symlink/isow1432.pdf"
TI_LVC1T45_SOURCE = "https://www.ti.com/lit/ds/symlink/sn74lvc1t45.pdf"
JST_GH_SOURCE = "https://www.jst-mfg.com/product/pdf/eng/eGH.pdf"


def load_model():
    path = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_kicad_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load native schematic model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.OUT = ECAD
    module.PROJECT = PROJECT
    module.REV = REV
    module.DATE = DATE
    module.WARNING = WARNING
    module.PROJECT_TITLE = "PROJECT BUTTON HR-30 WHOLE-BODY ELECTRICAL P0.1"
    module.PROJECT_SUBTITLE = "25 axes; five RS-485 and three TTL buses; logical terminals until physical selections close."
    module.root_schematic = lambda root_uuid, items: hr30_root_schematic(module, root_uuid, items)
    return module


def hr30_root_schematic(model, root_uuid: str, items: list) -> str:
    """Render the whole-body hierarchy without changing the frozen HR-V0 generator."""
    positions = [(12.0 + col * 100.0, 38.0 + row * 50.0) for row in range(5) for col in range(4)]
    if len(items) > len(positions):
        raise SystemExit("HR-30 hierarchy exceeds controlled A3 index capacity")
    blocks = []
    for sheet, (x, y) in zip(items, positions):
        blocks.append(f'''(sheet (at {x:.2f} {y:.2f}) (size 92.0 40.64)
          (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
          (stroke (width 0.5) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "{sheet.sheet_uuid}")
          (property "Sheetname" "{sheet.number:02d} {model.esc(sheet.title)}" (at {x+2.54:.2f} {y+10.16:.2f} 0) {model.font(1.5, 'left bottom')})
          (property "Sheetfile" "{sheet.filename}" (at {x+2.54:.2f} {y+25.4:.2f} 0) {model.font(1.3, 'left top')})
          (instances (project "{PROJECT}" (path "/{root_uuid}" (page "{sheet.number+1}")))))''')
    return f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid "{root_uuid}") (paper "A3")
  (title_block (title "{model.esc(model.PROJECT_TITLE)} index") (date "{DATE}") (rev "{REV}")
    (company "Project Button") (comment 1 "{WARNING}") (comment 2 "WHOLE-BODY LOGICAL ARCHITECTURE - PHYSICAL SELECTIONS OPEN"))
  (lib_symbols)
  {model.text_item(WARNING,12.0,10.16,2.54,'hr30-root-warning')}
  {model.text_item(model.PROJECT_TITLE,12.0,19.05,2.54,'hr30-root-title')}
  {model.text_item(model.PROJECT_SUBTITLE,12.0,27.0,1.8,'hr30-root-subtitle')}
  {' '.join(blocks)}
  (sheet_instances (path "/" (page "1"))) (embedded_fonts no))
'''


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def component(model, ref, value, pins, description, position, width=72.0, datasheet="", evidence="", status="SELECTION REQUIRED - LOGICAL CONNECTIVITY ONLY", footprint=""):
    return model.Component(
        ref=ref,
        value=value,
        pins=[model.pn(ref, number, name, net, side) for number, name, net, side in pins],
        status=status,
        description=description,
        datasheet=datasheet,
        evidence=evidence,
        position=position,
        width=width,
        footprint=footprint,
    )


def actuator_candidate(by_axis: dict[str, dict], axis: str) -> tuple[str, str]:
    candidate = by_axis[axis]["candidate_actuator"]
    if "XH540" in candidate:
        return candidate, "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/"
    if "XM540" in candidate:
        return candidate, "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/"
    if "XM430" in candidate:
        return candidate, "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/"
    if "XC330" in candidate:
        return candidate, "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/"
    raise SystemExit(f"unsupported actuator family for {axis}: {candidate}")


def axis_component(model, by_axis, axis, bus_id, position):
    candidate, source = actuator_candidate(by_axis, axis)
    ref = "AX_" + axis
    if bus_id.startswith("RS-"):
        pins = [
            ("2", "VDD", f"{axis}_VDD", "left"),
            ("1", "GND", f"{bus_id}_RET", "left"),
            ("3", "DATA+", f"{bus_id}_DP", "right"),
            ("4", "DATA-", f"{bus_id}_DN", "right"),
        ]
    else:
        pins = [
            ("2", "VDD", f"{axis}_VDD", "left"),
            ("1", "GND", f"{bus_id}_RET", "left"),
            ("3", "DATA", f"{bus_id}_DATA", "right"),
        ]
    return component(
        model, ref, candidate, pins,
        "Axis identity, protocol and manufacturer actuator-side pins are allocated. Exact order code, actuator ID, cable assembly, controller-side connector, branch current/protection and installed thermal/communication behavior remain selection and test work.",
        position, width=74.0, datasheet=source,
        evidence="Current official ROBOTIS Docs checked 2026-08-14: actuator-side 1=GND, 2=VDD and 3=DATA (TTL) or 3=DATA+/4=DATA- (RS-485).",
        status="ACTUATOR-SIDE PINOUT VERIFIED - HARNESS AND CONTROLLER SIDE SELECTION REQUIRED",
    )


def bus_sheet(model, number, filename, title, bus_id, axes, by_axis):
    sheet = model.Sheet(number, filename, title, f"Connected {bus_id} data-only segment and one separately protected power feed per actuator.")
    protocol = "RS-485" if bus_id.startswith("RS-") else "TTL"
    data_pins = [
        ("LOG-RET", "DATA REFERENCE", f"{bus_id}_RET", "left"),
        ("LOG-DP", "DATA+", f"{bus_id}_DP", "right"),
        ("LOG-DN", "DATA-", f"{bus_id}_DN", "right"),
    ] if protocol == "RS-485" else [
        ("LOG-RET", "DATA REFERENCE", f"{bus_id}_RET", "left"),
        ("LOG-DATA", "HALF-DUPLEX DATA", f"{bus_id}_DATA", "right"),
    ]
    data_port = component(
        model, "PORT_" + bus_id.replace("-", "_"), f"{bus_id} DATA-ONLY HARNESS PORT - CONNECTOR SELECTION REQUIRED", data_pins,
        "Logical data-only boundary from the matching controller interface. Exact connector, pins, reference conductor, shield and strain relief remain open.",
        (210, 44), width=115.0,
    )
    if len(axes) == 6:
        data_port.status = ""
    sheet.components.append(data_port)
    source_net = "ACT_MAIN_SAFE_12V" if protocol == "RS-485" else {
        "TTL-LDIST": "TTL_LDIST_SAFE_9V",
        "TTL-RDIST": "TTL_RDIST_SAFE_9V",
        "TTL-HEAD": "TTL_HEAD_SAFE_9V",
    }[bus_id]
    if len(axes) == 6:
        rows = [76, 108, 140, 172, 204, 236]
    elif len(axes) == 3:
        rows = [100, 165, 230]
    elif len(axes) == 2:
        rows = [120, 205]
    elif len(axes) == 1:
        rows = [165]
    else:
        raise SystemExit(f"unsupported segment population for {bus_id}: {len(axes)}")
    for axis, y in zip(axes, rows):
        feed_boundary = component(
            model, "PBR_" + axis, f"{axis} INDIVIDUAL PROTECTION / TELEMETRY - SELECTION REQUIRED",
            [("LOG-IN", "INTERRUPTED SOURCE", source_net, "left"), ("LOG-OUT", "PROTECTED ACTUATOR VDD", f"{axis}_VDD", "right"),
             ("LOG-RET-IN", "SOURCE RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-RET-OUT", "ACTUATOR / DATA REFERENCE", f"{bus_id}_RET", "right"),
             ("LOG-TLM", "INDIVIDUAL FEED TELEMETRY", f"TLM_PWR_{axis}", "right")],
            "One independently protected feed is allocated to this actuator. No fuse, limiter, conductor or connector rating is released; fault current, inrush, cable length, ambient, bundling, duty cycle and jurisdiction remain required inputs.",
            (105, y), width=128.0,
        )
        actuator = axis_component(model, by_axis, axis, bus_id, (315, y))
        if len(axes) == 6:
            feed_boundary.status = ""
            actuator.status = ""
        sheet.components.append(feed_boundary)
        sheet.components.append(actuator)
    # Six-axis leg sheets use the full A3 height for connected circuit blocks.
    # Their title/purpose and component labels carry the architecture statement;
    # repeating prose notes would collide with the native KiCad title block.
    sheet.notes = [] if len(axes) == 6 else [
        "The listed axes share only data and reference. Each pin-2 VDD has a distinct protected feed; no standard VDD-carrying daisy cable may parallel those feeds.",
        "AX_* terminals use current official ROBOTIS actuator-side pin numbers; all LOG-* identifiers remain functional ports, not physical connector or IC pins.",
        "A custom/de-pinned data-only harness or breakout is SELECTION REQUIRED. Termination, IDs, baud rate, cable, EMC, thermal and fault behavior remain unvalidated.",
    ]
    return sheet


def build_sheets(model):
    allocation = read_csv(PACKAGE / "actuator-transmission-allocation.csv")
    by_axis = {row["axis_id"]: row for row in allocation}
    expected = {axis for axes in BUS_AXES.values() for axis in axes}
    if len(allocation) != 25 or set(by_axis) != expected:
        raise SystemExit("whole-body actuator allocation drift")

    sheets = []
    s1 = model.Sheet(1, "01_energy_precharge_conversion.kicad_sch", "Tether-first energy, regulated rails and onboard-later boundary", "External 12 V tether-first source, three regulated 9 V TTL rails and a disconnected onboard-later evaluation boundary.")
    s1.components = [
        component(model, "ACB1", "FACILITY AC / PE PANEL BOUNDARY - SELECTION REQUIRED",
                  [("LOG-L", "FACILITY LINE", "FACILITY_AC_L", "right"), ("LOG-N", "FACILITY NEUTRAL", "FACILITY_AC_N", "right"), ("LOG-PE", "FACILITY PROTECTIVE EARTH", "PANEL_PE", "right")],
                  "Mains inlet, disconnect, branch protection, enclosure, terminals, conductor sizes and Boston installation jurisdiction require qualified selection.", (70, 72), width=82.0),
        component(model, "PS1", "MEAN WELL RSP-500-12 TETHER SUPPLY CANDIDATE",
                  [("LOG-L", "AC LINE FUNCTION", "FACILITY_AC_L", "left"), ("LOG-N", "AC NEUTRAL FUNCTION", "FACILITY_AC_N", "left"), ("LOG-PE", "PROTECTIVE EARTH FUNCTION", "PANEL_PE", "left"),
                   ("LOG-VPOS", "12 V PANEL OUTPUT", "PANEL_DC_POS_RAW", "right"), ("LOG-VNEG", "PANEL DC RETURN", "PANEL_DC_RET", "right")],
                  "Official RSP-500 specification gives 12 V / 41.7 A. Exact physical terminals, adjustment lock, protection, enclosure cooling, regeneration behavior and application rating remain open.", (200, 72), width=100.0,
                  datasheet="https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF", evidence="Official Mean Well RSP-500 specification accessed 2026-08-14.", status="TETHER-FIRST SUPPLY CANDIDATE - PANEL DESIGN AND VALIDATION REQUIRED"),
        component(model, "CTRLPS1", "MEAN WELL SD-15A-24 SAFETY-CONTROL SUPPLY CANDIDATE",
                  [("LOG-IN", "PANEL DC POSITIVE", "PANEL_DC_POS_RAW", "left"), ("LOG-RET-IN", "PANEL DC RETURN", "PANEL_DC_RET", "left"),
                   ("LOG-OUT", "24 V SAFETY CONTROL", "SAFETY_24V", "right"), ("LOG-RET-OUT", "SAFETY CONTROL RETURN", "SAFETY_0V", "right")],
                  "Official SD-15 specification gives 9.2-18 V input and 24 V / 0.625 A output. Protection, loading, grounding, thermal and EMC integration remain open.", (340, 72), width=100.0,
                  datasheet="https://www.meanwell.com/Upload/PDF/SD-15/SD-15-SPEC.PDF", evidence="Official Mean Well SD-15 specification accessed 2026-08-14.", status="24 V SAFETY-CONTROL SUPPLY CANDIDATE - APPLICATION VALIDATION REQUIRED"),
        component(model, "TETH1", "TOUCH-SAFE ROBOT DC / PE TETHER BOUNDARY - SELECTION REQUIRED",
                  [("LOG-PANEL-P", "CONTACTOR-SWITCHED PANEL POSITIVE", "TETHER_MAIN_POS", "left"), ("LOG-PANEL-N", "PANEL DC RETURN", "PANEL_DC_RET", "left"), ("LOG-PANEL-PE", "PANEL PE", "PANEL_PE", "left"),
                   ("LOG-ROBOT-P", "ROBOT CONTROLLED MAIN", "ACT_MAIN_SAFE_12V", "right"), ("LOG-ROBOT-N", "ROBOT CONTROLLED RETURN", "ACT_0V_CONTROLLED", "right"), ("LOG-ROBOT-PE", "ROBOT FRAME / PE BOUNDARY", "FRAME_PE_BOUNDARY", "right")],
                  "Connector, current/fault rating, contact sequence, breakaway/retention, flex cable, strain relief and PE treatment remain SELECTION REQUIRED.", (120, 190), width=112.0),
        component(model, "REG_TTL_L", "LEFT DISTAL 9 V BUCK-BOOST CANDIDATE - POLOLU S18V20F9",
                  [("LOG-IN", "CONTROLLED 12 V INPUT", "ACT_MAIN_SAFE_12V", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-OUT", "LEFT DISTAL 9 V", "TTL_LDIST_SAFE_9V", "right"), ("LOG-RET-OUT", "RETURN", "ACT_0V_CONTROLLED", "right"), ("LOG-TLM", "REGULATOR TELEMETRY", "TLM_TTL_LDIST_REG", "right")],
                  "Item 2576 is a 9 V candidate. Current margin, input/output transients, protection, thermal behavior, mounting and exact contacts remain open.", (280, 120), width=96.0, datasheet="https://www.pololu.com/product/2576"),
        component(model, "REG_TTL_R", "RIGHT DISTAL 9 V BUCK-BOOST CANDIDATE - POLOLU S18V20F9",
                  [("LOG-IN", "CONTROLLED 12 V INPUT", "ACT_MAIN_SAFE_12V", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-OUT", "RIGHT DISTAL 9 V", "TTL_RDIST_SAFE_9V", "right"), ("LOG-RET-OUT", "RETURN", "ACT_0V_CONTROLLED", "right"), ("LOG-TLM", "REGULATOR TELEMETRY", "TLM_TTL_RDIST_REG", "right")],
                  "Item 2576 is a 9 V candidate. Current margin, input/output transients, protection, thermal behavior, mounting and exact contacts remain open.", (280, 175), width=96.0, datasheet="https://www.pololu.com/product/2576"),
        component(model, "REG_TTL_H", "HEAD 9 V BUCK-BOOST CANDIDATE - POLOLU S18V20F9",
                  [("LOG-IN", "CONTROLLED 12 V INPUT", "ACT_MAIN_SAFE_12V", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-OUT", "HEAD ACTUATOR 9 V", "TTL_HEAD_SAFE_9V", "right"), ("LOG-RET-OUT", "RETURN", "ACT_0V_CONTROLLED", "right"), ("LOG-TLM", "REGULATOR TELEMETRY", "TLM_TTL_HEAD_REG", "right")],
                  "Item 2576 is a 9 V candidate. Current margin, input/output transients, protection, thermal behavior, mounting and exact contacts remain open.", (280, 230), width=96.0, datasheet="https://www.pololu.com/product/2576"),
    ]
    s1.notes = ["The 14.8 V direct-actuator architecture is absent. No fuse value, conductor size, connector rating or unresolved physical pin is released.", "The onboard-later battery/precharge/charger path is deliberately disconnected from ACT_MAIN_SAFE_12V until a separate reviewed change closes its holds."]
    sheets.append(s1)

    s2 = model.Sheet(2, "02_estop_permit_contactors.kicad_sch", "Dual-channel E-stop, monitored reset, permit and redundant interruption", "Logical whole-body safety interruption architecture; no functional-safety approval or application release.")
    s2.components = [
        component(model, "S0", "IDEC XW DUAL-NC E-STOP FAMILY CANDIDATE - EXACT ORDER CODE REQUIRED",
                  [("LOG-C1F", "CHANNEL 1 FEED", "ESTOP_CH1_FEED", "left"), ("LOG-C1R", "CHANNEL 1 RETURN", "ESTOP_CH1_RETURN", "right"),
                   ("LOG-C2F", "CHANNEL 2 FEED", "ESTOP_CH2_FEED", "left"), ("LOG-C2R", "CHANNEL 2 RETURN", "ESTOP_CH2_RETURN", "right")],
                  "Exact device, contacts, terminals, enclosure, spacing and direct-opening application remain selection and qualified review work.", (105, 82), width=86.0),
        component(model, "S1", "IDEC HW1B-M1F11-G MANUAL RESET CANDIDATE",
                  [("LOG-FEED", "RESET FEED", "RESET_FEED", "left"), ("LOG-RETURN", "RESET RETURN", "RESET_RETURN", "right")],
                  "Reset is eligibility only and must not command motion. Exact anti-tie-down/contact/terminal behavior requires selection and physical test.", (200, 82), width=82.0),
        component(model, "SR1", "PILZ PNOZ s4 750104 SAFETY-RELAY CANDIDATE - APPLICATION OPEN",
                  [("LOG-C1F", "E-STOP CH1 FEED", "ESTOP_CH1_FEED", "right"), ("LOG-C1R", "E-STOP CH1 RETURN", "ESTOP_CH1_RETURN", "left"),
                   ("LOG-C2F", "E-STOP CH2 FEED", "ESTOP_CH2_FEED", "right"), ("LOG-C2R", "E-STOP CH2 RETURN", "ESTOP_CH2_RETURN", "left"),
                   ("LOG-RF", "RESET FEED", "RESET_FEED", "right"), ("LOG-RR", "RESET / EDM RETURN", "RESET_RETURN", "left"), ("LOG-24V", "24 V CONTROL", "SAFETY_24V", "left"), ("LOG-0V", "CONTROL RETURN", "SAFETY_0V", "left"),
                   ("LOG-OUT1", "SAFETY OUTPUT TO K1", "SAFETY_OUT_K1", "right"), ("LOG-OUT2", "SAFETY OUTPUT TO K2", "SAFETY_OUT_K2", "right"), ("LOG-PERMIT", "PERMIT STATUS TO MOTION CONTROL", "SAFETY_PERMIT_HARDWIRED", "right"),
                   ("LOG-EDM1", "K1 LINKED AUXILIARY RETURN", "EDM_K1_AUX", "left"), ("LOG-EDM2", "K2 LINKED AUXILIARY RETURN", "EDM_K2_AUX", "left"),
                   ("LOG-CHG", "CHARGER INHIBIT", "CHARGER_INTERLOCK", "left"), ("LOG-WD", "ORDINARY WATCHDOG INHIBIT", "WATCHDOG_INHIBIT_OK", "left")],
                  "Manual 21396-EN-23 supports monitored manual start and EDM application concepts. Required PLr/SIL, exact terminal wiring, category, common-cause, diagnostic coverage, reset mode, reaction time and validation are not established.", (305, 155), width=112.0,
                  datasheet="https://www.pilz.com/en-US/eshop/product/750104", evidence="Pilz manual 21396-EN-23 dated 2026-06-22; accessed 2026-08-14.", status="SAFETY-RELAY CANDIDATE - NO FUNCTIONAL-SAFETY APPROVAL"),
        component(model, "WD_INH1", "ORDINARY WATCHDOG INHIBIT INTERFACE - DESIGN REQUIRED / ZERO SAFETY CREDIT",
                  [("LOG-IN", "WATCHDOG REQUEST", "WD_PERMIT_REQUEST", "left"), ("LOG-OUT", "FAIL-LOW INHIBIT ELIGIBILITY", "WATCHDOG_INHIBIT_OK", "right")],
                  "The ordinary watchdog may only remove eligibility; it can never bypass S0, reset, EDM or issue motion. Exact fail-low interface and fault validation remain open.", (105, 155), width=104.0),
        component(model, "K1", "SENSATA GIGAVAC GV12-FAMILY DC CONTACTOR 1 CANDIDATE",
                  [("LOG-MIN", "MAIN INPUT", "PANEL_DC_POS_RAW", "left"), ("LOG-MOUT", "MAIN OUTPUT", "K1_POS_OUT", "right"),
                   ("LOG-COIL-P", "COIL POSITIVE", "SAFETY_OUT_K1", "left"), ("LOG-COIL-N", "COIL RETURN", "SAFETY_0V", "left"), ("LOG-AUX", "MECHANICALLY LINKED AUXILIARY CANDIDATE", "EDM_K1_AUX", "right")],
                  "Family datasheet lists an optional mechanically linked auxiliary; it is not claimed as an IEC mirror contact. Exact order code, DC duty, coil suppression, EDM suitability, fault current and life require confirmation.", (150, 225), width=102.0, datasheet="https://www.sensata.com/sites/default/files/a/sensata-gigavac-gv12-series-100v-contactors-datasheet.pdf"),
        component(model, "K2", "SENSATA GIGAVAC GV12-FAMILY DC CONTACTOR 2 CANDIDATE",
                  [("LOG-MIN", "MAIN INPUT", "K1_POS_OUT", "left"), ("LOG-MOUT", "MAIN OUTPUT TO TETHER", "TETHER_MAIN_POS", "right"),
                   ("LOG-COIL-P", "COIL POSITIVE", "SAFETY_OUT_K2", "left"), ("LOG-COIL-N", "COIL RETURN", "SAFETY_0V", "left"), ("LOG-AUX", "MECHANICALLY LINKED AUXILIARY CANDIDATE", "EDM_K2_AUX", "right")],
                  "Second series interruption candidate. Exact order code, common-cause, welded-contact detection, DC interruption and energy-removal behavior remain unvalidated.", (310, 225), width=102.0, datasheet="https://www.sensata.com/sites/default/files/a/sensata-gigavac-gv12-series-100v-contactors-datasheet.pdf"),
    ]
    s2.notes = ["E-stop release or reset can only restore eligibility; MCU1 must still require a fresh bounded motion request.", "No safety performance level, SIL, stopping-time or energization approval is claimed."]
    sheets.append(s2)

    s3 = model.Sheet(3, "03_compute_motion_watchdog.kicad_sch", "Conversational compute, deterministic motion controller and watchdog", "OpenAI/high-level requests remain separated from deterministic joint and hardwired permit control.")
    mcu_pins = [("LOG-PERMIT", "HARDWIRED PERMIT INPUT", "SAFETY_PERMIT_HARDWIRED", "left"),
                ("LOG-ACTION", "AUTHENTICATED ACTION REQUEST", "ACTION_REQUEST_AUTH", "left"),
                ("LOG-WD", "WATCHDOG HEARTBEAT", "MOTION_WD_HEARTBEAT", "right"),
                ("LOG-PREQ", "PRECHARGE REQUEST", "PRECHARGE_REQUEST", "right"),
                ("LOG-PSTAT", "PRECHARGE STATUS", "PRECHARGE_STATUS", "left")]
    s3.components = [
        component(model, "CPU1", "RASPBERRY PI 5 CONVERSATIONAL COMPUTE CANDIDATE",
                  [("LOG-NET", "NETWORK / OPENAI CLIENT", "EXTERNAL_NETWORK", "left"), ("LOG-ACTION", "STRUCTURED ACTION REQUEST", "ACTION_REQUEST_AUTH", "right"),
                   ("LOG-CAM-L", "LEFT CAMERA IPC", "HEAD_CAM_L_IPC", "right"), ("LOG-CAM-R", "RIGHT CAMERA IPC", "HEAD_CAM_R_IPC", "right"),
                   ("LOG-DISPLAY", "FACE DISPLAY IPC", "HEAD_DISPLAY_IPC", "right"), ("LOG-TOUCH", "FACE TOUCH IPC", "HEAD_TOUCH_IPC", "right"),
                   ("LOG-MIC", "MICROPHONE IPC", "HEAD_MIC_IPC", "right"), ("LOG-AUDIO", "AUDIO OUTPUT IPC", "HEAD_AUDIO_IPC", "right"),
                   ("LOG-FAN-PWM", "HEAD FAN PWM", "HEAD_FAN_PWM", "right"), ("LOG-FAN-TACH", "HEAD FAN TACH", "HEAD_FAN_TACH", "left")],
                  "No actuator-bus credentials or raw joint-register authority. Exact power, storage, cooling, privacy and network controls remain open.", (65, 55), width=80.0,
                  datasheet="https://www.raspberrypi.com/products/raspberry-pi-5/"),
        component(model, "MCU1", "STM32H743ZIT6 LQFP144 MOTION-CONTROL CARRIER CANDIDATE", mcu_pins,
                  "Active 2 MB STM32H743 LQFP144 candidate. Owns state estimation, bounded trajectories, joint limits, eight UARTs, bus timing and fault states. Clock, power, reset, debug, Ethernet/CAN, PCB layout, firmware and real-time validation remain open.",
                  (210, 85), width=90.0, datasheet=ST_H743_SOURCE,
                  evidence="ST DS12110 Rev 11 and current product page checked 2026-08-14; STM32H743ZIT6 is active/in volume production. Eight UART TX/RX/DE pin candidates are recorded on this sheet and interface-carrier-pinout.csv.",
                  status="EXACT MCU ORDER-CODE CANDIDATE - BOARD DESIGN AND VALIDATION REQUIRED"),
        component(model, "WD1", "INDEPENDENT ORDINARY WATCHDOG - SELECTION REQUIRED / ZERO SAFETY CREDIT",
                  [("LOG-HB", "MOTION HEARTBEAT INPUT", "MOTION_WD_HEARTBEAT", "left"), ("LOG-REQ", "PERMIT REQUEST DIAGNOSTIC", "WD_PERMIT_REQUEST", "right")],
                  "Heartbeat supervision is diagnostic only and may not bypass S0, monitored reset, EDM or deterministic motion authorization.", (355, 55), width=75.0),
    ]
    io_positions = [(115, 125), (315, 125), (115, 165), (315, 165), (115, 205), (315, 205), (115, 235), (315, 235)]
    for index, (bus_id, position) in enumerate(zip(BUS_AXES, io_positions)):
        side = "left" if index % 2 == 0 else "right"
        allocation = UART_ALLOCATIONS[bus_id]
        tx_name, tx_pin, tx_af = allocation["tx"]
        rx_name, rx_pin, rx_af = allocation["rx"]
        de_name, de_pin, de_af = allocation["de"]
        ttl = bus_id.startswith("TTL-")
        port = component(
            model, "MCU_IO_" + bus_id.replace("-", "_"), f"MCU1 {allocation['uart']} PHYSICAL PIN UNIT - {bus_id}",
            [(tx_pin, f"{tx_name} {tx_af} {'HALF-DUPLEX IO' if ttl else 'TX'}", f"UART_{bus_id}_TX", side),
             (rx_pin, f"{rx_name} {rx_af} {'RESERVED / NOT USED IN P0.1 TTL MODE' if ttl else 'RX'}", f"INTENTIONALLY_UNUSED_{bus_id}_RX" if ttl else f"UART_{bus_id}_RX", side),
             (de_pin, f"{de_name} {de_af} RTS/DE", f"UART_{bus_id}_DIR", side)],
            "Alternate physical-pin unit of MCU1, not another controller. TTL segments use the documented STM32 single-wire half-duplex mode on TX/IO; their RX package pin is intentionally unused in P0.1.",
            position, width=112.0, datasheet=ST_H743_SOURCE,
            evidence="ST DS12110 Rev 11 LQFP144 pinout and alternate-function tables checked 2026-08-14.",
            status="PHYSICAL MCU PACKAGE PIN AND ALTERNATE FUNCTION VERIFIED - PCB VALIDATION REQUIRED",
        )
        port.quantity = 0
        s3.components.append(port)
    s3.notes = ["Conversational compute emits expiring high-level actions only; it never writes actuator registers.", "Hardwired permit loss forces controller outputs disabled; permit restoration alone must not start motion."]
    sheets.append(s3)

    def carrier_connector_pins(carrier: str):
        pins = [("1", "CONTROL 5 V", "CTRL_5V", "left"), ("2", "CONTROL 3.3 V", "CTRL_3V3", "left"), ("3", "CONTROL GROUND", "CTRL_GND", "left")]
        if carrier == "A":
            order = ("RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM")
            for base, bus_id in zip((4, 7, 10, 13), order):
                pins.extend([(str(base), f"{bus_id} TX", f"UART_{bus_id}_TX", "right"),
                             (str(base + 1), f"{bus_id} RX", f"UART_{bus_id}_RX", "right"),
                             (str(base + 2), f"{bus_id} DE", f"UART_{bus_id}_DIR", "right")])
        else:
            pins.extend([
                ("4", "RS-WAIST TX", "UART_RS-WAIST_TX", "right"), ("5", "RS-WAIST RX", "UART_RS-WAIST_RX", "right"),
                ("6", "RS-WAIST DE", "UART_RS-WAIST_DIR", "right"),
                ("7", "TTL-LDIST HALF-DUPLEX IO", "UART_TTL-LDIST_TX", "right"), ("8", "TTL-LDIST DIR", "UART_TTL-LDIST_DIR", "right"),
                ("9", "TTL-RDIST HALF-DUPLEX IO", "UART_TTL-RDIST_TX", "right"), ("10", "TTL-RDIST DIR", "UART_TTL-RDIST_DIR", "right"),
                ("11", "TTL-HEAD HALF-DUPLEX IO", "UART_TTL-HEAD_TX", "right"), ("12", "TTL-HEAD DIR", "UART_TTL-HEAD_DIR", "right"),
                ("13", "RESERVED - NO CONNECTION", "INTENTIONALLY_UNUSED_CARRIER_B_13", "right"),
                ("14", "RESERVED - NO CONNECTION", "INTENTIONALLY_UNUSED_CARRIER_B_14", "right"),
                ("15", "RESERVED - NO CONNECTION", "INTENTIONALLY_UNUSED_CARRIER_B_15", "right"),
            ])
        return pins

    s4 = model.Sheet(4, "04_motion_controller_carrier_connectors.kicad_sch", "STM32H743 motion-controller power and carrier connectors", "Physical two-board interface for the eight UART channels; no field actuator power enters either connector.")
    s4.components = [
        component(model, "REG1", "CONTROL 5 V TO 3.3 V REGULATOR - DESIGN REQUIRED",
                  [("LOG-5V-IN", "AUXILIARY 5 V INPUT", "AUX_5V_SAFE", "left"), ("LOG-RET-IN", "AUXILIARY RETURN", "AUX_0V", "left"),
                   ("LOG-5V", "CONTROL 5 V", "CTRL_5V", "right"), ("LOG-3V3", "CONTROL 3.3 V", "CTRL_3V3", "right"), ("LOG-GND", "CONTROL GROUND", "CTRL_GND", "right")],
                  "The exact regulator, filtering, sequencing, brownout, protection, thermal and EMC design remains open. This block does not authorize powering MCU1 or either carrier.", (205, 65), width=108.0),
        component(model, "JMCU_A", "JST BM15B-GHS-TBT - CARRIER A CONTROLLER HEADER", carrier_connector_pins("A"),
                  "Exact active 15-circuit JST GH top-entry header candidate. Mates GHR-15V-S with SSHL-002T-P0.2 contacts. Carries only logic rails and four UART triplets; no actuator VDD.",
                  (120, 165), width=112.0, datasheet=JST_GH_SOURCE,
                  evidence="JST GH official product page and eGH catalog checked 2026-08-14: 1.25 mm secure-lock, 15-circuit header/housing family, 1 A at AWG26 family rating.",
                  status="EXACT CONNECTOR FAMILY/ORDER-CODE CANDIDATE - HARNESS AND PCB VALIDATION REQUIRED"),
        component(model, "JMCU_B", "JST BM15B-GHS-TBT - CARRIER B CONTROLLER HEADER", carrier_connector_pins("B"),
                  "Exact active 15-circuit JST GH top-entry header candidate. Carries one RS-485 UART triplet, three TTL IO/DIR pairs and three reserved open contacts; no actuator VDD.",
                  (310, 165), width=112.0, datasheet=JST_GH_SOURCE,
                  evidence="JST GH official product page and eGH catalog checked 2026-08-14.",
                  status="EXACT CONNECTOR FAMILY/ORDER-CODE CANDIDATE - HARNESS AND PCB VALIDATION REQUIRED"),
    ]
    s4.notes = ["Carrier cable candidate: GHR-15V-S housing with SSHL-002T-P0.2 contacts and AWG26 conductors; exact length, assembly supplier, routing and flex life remain open.",
                "JMCU_A/B carry logic only. No contact may be repurposed for actuator power. The controller PCB, regulator and power sequencing remain design work."]
    sheets.append(s4)

    def isow_component(bus_id: str, position):
        ref = "ISO_" + bus_id.replace("-", "_")
        return component(model, ref, f"TI ISOW1432DFMR 12 Mbps ISOLATED RS-485 - {bus_id}",
            [("1", "VIO", "CTRL_3V3", "left"), ("2", "D", f"UART_{bus_id}_TX", "left"),
             ("3", "DE", f"UART_{bus_id}_DIR", "left"), ("4", "R", f"UART_{bus_id}_RX", "left"),
             ("5", "RE ACTIVE LOW", f"UART_{bus_id}_DIR", "left"), ("6", "GNDIO", "CTRL_GND", "left"),
             ("7", "OUT UNUSED", f"INTENTIONALLY_UNUSED_{ref}_7", "left"), ("8", "EN/FLT DEFAULT ENABLE", f"INTENTIONALLY_UNUSED_{ref}_8", "left"),
             ("9", "VDD CONVERTER", "CTRL_5V", "left"), ("10", "GND1", "CTRL_GND", "left"),
             ("11", "GND2", f"{bus_id}_RET", "right"), ("12", "VISOOUT", f"ISO_PWR_{bus_id}", "right"),
             ("13", "MODE = GND2", f"{bus_id}_RET", "right"), ("14", "IN UNUSED", f"INTENTIONALLY_UNUSED_{ref}_14", "right"),
             ("15", "GISOIN", f"{bus_id}_RET", "right"), ("16", "VISOIN", f"ISO_PWR_{bus_id}", "right"),
             ("17", "Y DRIVER NONINVERTING", f"{bus_id}_DP", "right"), ("18", "Z DRIVER INVERTING", f"{bus_id}_DN", "right"),
             ("19", "B RECEIVER INVERTING", f"{bus_id}_DN", "right"), ("20", "A RECEIVER NONINVERTING", f"{bus_id}_DP", "right")],
            "Integrated isolated-power candidate. DE and active-low RE share the hardware DE net for half duplex. Y/A and Z/B form the two-wire bus. Exact decoupling/ferrites, termination, bias, surge/ESD, emissions layout and fault behavior remain design and test work.",
            position, width=120.0, datasheet=TI_ISOW1432_SOURCE,
            evidence="TI ISOW1412/ISOW1432 datasheet SLLSF86C Rev C, March 2022, checked 2026-08-14; ISOW1432DFMR is active, 12 Mbps, 20-pin DFM wide SOIC.",
            status="EXACT TRANSCEIVER ORDER-CODE CANDIDATE - APPLICATION CIRCUIT/LAYOUT/TEST REQUIRED",
            footprint="Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm")

    def rs_field_connector(bus_id: str, position):
        return component(model, "J_" + bus_id.replace("-", "_"), "JST BM03B-GHS-TBT DATA-ONLY FIELD HEADER",
            [("1", "DATA REFERENCE / GND", f"{bus_id}_RET", "left"), ("2", "DATA+", f"{bus_id}_DP", "left"), ("3", "DATA-", f"{bus_id}_DN", "left")],
            "Three-contact data-only connector. It intentionally has no actuator VDD contact. Mating GHR-03V-S/SSHL-002T-P0.2 cable, shield/bond, termination, protection and routing remain open.",
            position, width=72.0, datasheet=JST_GH_SOURCE,
            evidence="JST GH official eGH catalog checked 2026-08-14.",
            status="EXACT DATA-ONLY CONNECTOR CANDIDATE - HARNESS/EMC VALIDATION REQUIRED")

    s5 = model.Sheet(5, "05_carrier_a_four_isolated_rs485.kicad_sch", "Carrier A - four isolated RS-485 channels", "Exact ISOW1432 pin-level candidates for both legs and both proximal arms.")
    s5.components.append(component(model, "JCA1", "JST GHR-15V-S CARRIER A CABLE RECEPTACLE", carrier_connector_pins("A"),
                  "Mates JMCU_A through the logic-only carrier cable candidate.", (210, 60), width=112.0, datasheet=JST_GH_SOURCE,
                  evidence="JST GH official product page/eGH catalog checked 2026-08-14.", status="EXACT CONNECTOR CANDIDATE - CABLE ASSEMBLY VALIDATION REQUIRED"))
    for bus_id, position, field_position in zip(("RS-LLEG", "RS-RLEG", "RS-LARM", "RS-RARM"),
                                                ((100, 115), (300, 115), (100, 195), (300, 195)),
                                                ((55, 242), (155, 242), (255, 242), (355, 242))):
        s5.components.extend([isow_component(bus_id, position), rs_field_connector(bus_id, field_position)])
    s5.notes = ["All four channels are galvanically isolated from CTRL_GND by their candidate ISOW1432 device; isolation layout and barrier spacing are not yet a PCB release.",
                "Field headers carry reference/data only. Protection device, common-mode choke, optional 120 ohm termination fit decision and bus waveform tests remain SELECTION REQUIRED."]
    sheets.append(s5)

    s6 = model.Sheet(6, "06_carrier_b_waist_and_ttl.kicad_sch", "Carrier B - waist RS-485 and three translated TTL channels", "One isolated waist bus plus three 3.3 V to 5 V single-wire half-duplex translators.")
    s6.components = [
        component(model, "JCB1", "JST GHR-15V-S CARRIER B CABLE RECEPTACLE", carrier_connector_pins("B"),
                  "Mates JMCU_B through the logic-only carrier cable candidate.", (210, 60), width=112.0, datasheet=JST_GH_SOURCE,
                  evidence="JST GH official product page/eGH catalog checked 2026-08-14.", status="EXACT CONNECTOR CANDIDATE - CABLE ASSEMBLY VALIDATION REQUIRED"),
        isow_component("RS-WAIST", (120, 130)), rs_field_connector("RS-WAIST", (320, 130)),
    ]
    for bus_id, x in (("TTL-LDIST", 80), ("TTL-RDIST", 210), ("TTL-HEAD", 340)):
        ref = "LVL_" + bus_id.replace("-", "_")
        s6.components.append(component(model, ref, f"TI SN74LVC1T45DCKR 3.3 V / 5 V TRANSLATOR - {bus_id}",
            [("1", "VCCA 3.3 V", "CTRL_3V3", "left"), ("2", "GND", "CTRL_GND", "left"),
             ("3", "A MCU HALF-DUPLEX IO", f"UART_{bus_id}_TX", "left"), ("4", "B 5 V BUS DATA", f"{bus_id}_DATA", "right"),
             ("5", "DIR HIGH = MCU TO BUS", f"UART_{bus_id}_DIR", "left"), ("6", "VCCB 5 V", "CTRL_5V", "left")],
            "Direction-controlled dual-supply translator. MCU UART TX pin is configured as STM32 single-wire half-duplex IO; RX package pin is intentionally unused. DIR defaults and rail sequencing, series resistance, ESD, loading and waveform behavior require PCB/HIL validation.",
            (x, 205), width=92.0, datasheet=TI_LVC1T45_SOURCE,
            evidence="TI SN74LVC1T45 datasheet SCES515N Rev N, June 2024, checked 2026-08-14; SN74LVC1T45DCKR is active.",
            status="EXACT LEVEL-TRANSLATOR ORDER-CODE CANDIDATE - APPLICATION VALIDATION REQUIRED",
            footprint="Package_TO_SOT_SMD:SOT-363_SC-70-6"))
        s6.components.append(component(model, "J_" + bus_id.replace("-", "_"), "JST BM02B-GHS-TBT DATA-ONLY FIELD HEADER",
            [("1", "DATA REFERENCE / GND", f"{bus_id}_RET", "left"), ("2", "HALF-DUPLEX DATA", f"{bus_id}_DATA", "left")],
            "Two-contact data-only connector; no actuator VDD contact. Mating GHR-02V-S/SSHL-002T-P0.2 cable, protection and routing remain open.",
            (x, 245), width=92.0, datasheet=JST_GH_SOURCE,
            evidence="JST GH official eGH catalog checked 2026-08-14.", status="EXACT DATA-ONLY CONNECTOR CANDIDATE - HARNESS/EMC VALIDATION REQUIRED"))
    s6.notes = ["The three TTL buses use STM32 single-wire half-duplex mode on the listed TX/IO pins. Their dedicated RX pins remain intentionally unused in P0.1.",
                "Carrier B shares CTRL_GND with TTL field reference; only the waist RS-485 channel is galvanically isolated. ESD, return/shield topology and physical fault tests remain open."]
    sheets.append(s6)

    sheets.append(bus_sheet(model, 7, "07_left_leg_rs485.kicad_sch", "Left-leg RS-485 data bus and individual feeds", "RS-LLEG", BUS_AXES["RS-LLEG"], by_axis))
    sheets.append(bus_sheet(model, 8, "08_right_leg_rs485.kicad_sch", "Right-leg RS-485 data bus and individual feeds", "RS-RLEG", BUS_AXES["RS-RLEG"], by_axis))
    sheets.append(bus_sheet(model, 9, "09_left_arm_rs485.kicad_sch", "Left proximal-arm RS-485 data bus and individual feeds", "RS-LARM", BUS_AXES["RS-LARM"], by_axis))
    sheets.append(bus_sheet(model, 10, "10_right_arm_rs485.kicad_sch", "Right proximal-arm RS-485 data bus and individual feeds", "RS-RARM", BUS_AXES["RS-RARM"], by_axis))
    sheets.append(bus_sheet(model, 11, "11_waist_rs485.kicad_sch", "Waist RS-485 data bus and individual feed", "RS-WAIST", BUS_AXES["RS-WAIST"], by_axis))
    sheets.append(bus_sheet(model, 12, "12_left_distal_ttl.kicad_sch", "Left wrist/gripper TTL data bus and individual feeds", "TTL-LDIST", BUS_AXES["TTL-LDIST"], by_axis))
    sheets.append(bus_sheet(model, 13, "13_right_distal_ttl.kicad_sch", "Right wrist/gripper TTL data bus and individual feeds", "TTL-RDIST", BUS_AXES["TTL-RDIST"], by_axis))

    s14 = bus_sheet(model, 14, "14_head_ttl_sensors_hmi.kicad_sch", "Head TTL, cameras, face display, audio and cooling", "TTL-HEAD", BUS_AXES["TTL-HEAD"], by_axis)
    s14.components.extend([
        component(model, "HPWR1", "PROTECTED HEAD AUXILIARY DISTRIBUTION - DESIGN REQUIRED", [("LOG-IN", "AUXILIARY 5 V INPUT", "AUX_5V_SAFE", "left"), ("LOG-RET-IN", "AUXILIARY RETURN", "AUX_0V", "left"), ("LOG-OUT", "HEAD 5 V", "HEAD_5V", "right"), ("LOG-RET-OUT", "HEAD RETURN", "HEAD_0V", "right")], "Branch protection, filtering, connector and current allocation remain open.", (70, 235), width=82.0),
        component(model, "CAM1", "LEFT CAMERA MODULE - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-IPC", "VISION IPC", "HEAD_CAM_L_IPC", "right")], "No safety role; exact module, optics, privacy and mounting remain open.", (175, 235), width=64.0),
        component(model, "CAM2", "RIGHT CAMERA MODULE - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-IPC", "VISION IPC", "HEAD_CAM_R_IPC", "right")], "No safety role; exact module, optics, synchronization and mounting remain open.", (260, 235), width=64.0),
        component(model, "DISP1", "FACE DISPLAY - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-IPC", "DISPLAY IPC", "HEAD_DISPLAY_IPC", "right"), ("LOG-TOUCH", "TOUCH IPC", "HEAD_TOUCH_IPC", "right")], "Exact screen, controller, luminance and touch interface remain open.", (350, 235), width=68.0),
        component(model, "MIC1", "MICROPHONE ARRAY - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-IPC", "AUDIO INPUT IPC", "HEAD_MIC_IPC", "right")], "Exact microphones, privacy indication and acoustic behavior remain open.", (90, 285), width=64.0),
        component(model, "AMP1", "AUDIO AMPLIFIER - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-IN", "AUDIO INPUT IPC", "HEAD_AUDIO_IPC", "left"), ("LOG-LP", "LEFT SPEAKER +", "SPK_L_POS", "right"), ("LOG-LN", "LEFT SPEAKER -", "SPK_L_NEG", "right"), ("LOG-RP", "RIGHT SPEAKER +", "SPK_R_POS", "right"), ("LOG-RN", "RIGHT SPEAKER -", "SPK_R_NEG", "right")], "Output power, protection, acoustic limit and exact pins remain open.", (200, 285), width=76.0),
        component(model, "SPK1", "LEFT SPEAKER - SELECTION REQUIRED", [("LOG-P", "SPEAKER +", "SPK_L_POS", "left"), ("LOG-N", "SPEAKER -", "SPK_L_NEG", "left")], "Exact driver, enclosure and sound-pressure limit remain open.", (295, 285), width=58.0),
        component(model, "SPK2", "RIGHT SPEAKER - SELECTION REQUIRED", [("LOG-P", "SPEAKER +", "SPK_R_POS", "left"), ("LOG-N", "SPEAKER -", "SPK_R_NEG", "left")], "Exact driver, enclosure and sound-pressure limit remain open.", (370, 285), width=58.0),
        component(model, "FAN1", "HEAD COOLING FAN - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "HEAD_5V", "left"), ("LOG-RET", "RETURN", "HEAD_0V", "left"), ("LOG-PWM", "PWM", "HEAD_FAN_PWM", "right"), ("LOG-TACH", "TACHOMETER", "HEAD_FAN_TACH", "right")], "Airflow, noise, finger guarding and failure detection remain open.", (405, 285), width=58.0),
    ])
    sheets.append(s14)

    s15 = model.Sheet(15, "15_pelvis_aux_imu.kicad_sch", "Auxiliary conversion and pelvis inertial sensing", "Logical 5 V auxiliary rail and pelvis IMU boundary.")
    s15.components = [
        component(model, "AUXD1", "CONTROLLED 12 V TO 5.1 V AUXILIARY CONVERTER - SELECTION REQUIRED", [("LOG-IN", "CONTROLLED 12 V INPUT", "ACT_MAIN_SAFE_12V", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-OUT", "AUXILIARY 5 V", "AUX_5V_SAFE", "right"), ("LOG-RET-OUT", "AUXILIARY RETURN", "AUX_0V", "right"), ("LOG-TLM", "CONVERTER TELEMETRY", "TLM_AUXD1", "right")], "Exact converter, protection, isolation/bonding, inrush, thermal and EMC evidence remain open.", (125, 115), width=96.0),
        component(model, "IMU1", "PELVIS 6/9-AXIS IMU - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "AUX_5V_SAFE", "left"), ("LOG-RET", "RETURN", "AUX_0V", "left"), ("LOG-DATA", "DETERMINISTIC SENSOR DATA", "PELVIS_IMU_DATA", "right"), ("LOG-INT", "DATA READY / FAULT", "PELVIS_IMU_INT", "right")], "Exact device, range, bandwidth, timestamping, calibration, connector and physical pins remain open.", (315, 115), width=92.0),
        component(model, "MCU_AUX", "MCU1 AUXILIARY SENSOR PORTS - LOGICAL UNIT", [("LOG-IMU", "PELVIS IMU DATA", "PELVIS_IMU_DATA", "left"), ("LOG-IMU-INT", "PELVIS IMU INTERRUPT", "PELVIS_IMU_INT", "left"), ("LOG-LFOOT", "LEFT FOOT SENSOR DATA", "L_FOOT_SENSOR_DATA", "right"), ("LOG-RFOOT", "RIGHT FOOT SENSOR DATA", "R_FOOT_SENSOR_DATA", "right")], "Alternate logical view of MCU1; exact package pins and interfaces remain open.", (220, 215), width=100.0),
    ]
    sheets.append(s15)

    def foot_sheet(number, side):
        prefix = "L" if side == "left" else "R"
        sheet = model.Sheet(number, f"{number:02d}_{side}_foot_load_sensing.kicad_sch", f"{side.title()} foot four-point load sensing", "Four physical sole-sensor locations and one local acquisition boundary.")
        signal_pins = []
        positions = [(105, 95), (305, 95), (105, 205), (305, 205)]
        for corner, position in zip(("FL", "FR", "RL", "RR"), positions):
            signal_pins.extend([(f"LOG-{corner}-P", f"{corner} SIGNAL +", f"{prefix}_FOOT_{corner}_SIG_P", "left"), (f"LOG-{corner}-N", f"{corner} SIGNAL -", f"{prefix}_FOOT_{corner}_SIG_N", "left")])
            sheet.components.append(component(model, f"LOAD_{prefix}_{corner}", f"{side.upper()} FOOT {corner} LOAD SENSOR - SELECTION REQUIRED", [("LOG-EXC-P", "EXCITATION +", f"{prefix}_FOOT_EXC_P", "left"), ("LOG-EXC-N", "EXCITATION -", f"{prefix}_FOOT_EXC_N", "left"), ("LOG-SIG-P", "SIGNAL +", f"{prefix}_FOOT_{corner}_SIG_P", "right"), ("LOG-SIG-N", "SIGNAL -", f"{prefix}_FOOT_{corner}_SIG_N", "right")], "Exact sensor type, range, overload, mounting, connector, calibration and physical pins remain open.", position, width=78.0))
        sheet.components.append(component(model, f"ADC_{prefix}_FOOT", f"{side.upper()} FOOT LOAD ACQUISITION - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "AUX_5V_SAFE", "left"), ("LOG-RET", "RETURN", "AUX_0V", "left"), ("LOG-EXC-P", "EXCITATION +", f"{prefix}_FOOT_EXC_P", "right"), ("LOG-EXC-N", "EXCITATION -", f"{prefix}_FOOT_EXC_N", "right"), ("LOG-DATA", "UPSTREAM SENSOR DATA", f"{prefix}_FOOT_SENSOR_DATA", "right")] + signal_pins, "Exact ADC, excitation, anti-aliasing, protection, timing, calibration and connector pins remain open.", (205, 280), width=112.0))
        sheet.notes = ["The four sensor locations correspond to the physical installed-equipment register; no sensor order code or force accuracy is released.", "Foot data supports state estimation only after calibration and fault validation; it carries no independent safety credit."]
        return sheet

    sheets.append(foot_sheet(16, "left"))
    sheets.append(foot_sheet(17, "right"))
    s18 = model.Sheet(18, "18_onboard_later_energy_evaluation.kicad_sch", "Onboard-later isolated energy evaluation", "Disconnected LiFePO4, service-disconnect, precharge and charger-interlock candidate path; not tied to the tether-first main.")
    s18.components = [
        component(model, "BATT_LATER", "BIOENNO BLF-1209WS ONBOARD-LATER EVALUATION CANDIDATE",
                  [("LOG-POS", "LATER PACK POSITIVE", "ONBOARD_LATER_POS", "right"), ("LOG-NEG", "LATER PACK RETURN", "ONBOARD_LATER_RET", "right"), ("LOG-TEMP", "PACK TEMPERATURE / STATUS BOUNDARY", "TLM_ONBOARD_LATER_PACK", "right")],
                  "This candidate is not connected to the tether-first main. Its 18 A continuous / 40 A for 2 s limits do not close the provisional whole-body peak; cassette, PCM behavior and fault evidence remain open.", (75, 105), width=104.0, datasheet="https://www.bioennopower.com/products/12v-9ah-lfp-battery-abs-sealed-green-case-1", status="ONBOARD-LATER EVALUATION ONLY - NOT A SELECTED SOURCE"),
        component(model, "SD_LATER", "ONBOARD-LATER SERVICE DISCONNECT - SELECTION REQUIRED",
                  [("LOG-IN", "LATER PACK POSITIVE", "ONBOARD_LATER_POS", "left"), ("LOG-OUT", "LATER DISCONNECTED OUTPUT", "ONBOARD_LATER_SD_POS", "right")],
                  "DC voltage/current/fault rating, touch safety, interlock and mounting remain open.", (205, 105), width=88.0),
        component(model, "PRE_LATER", "ONBOARD-LATER PRECHARGE / DISCHARGE - DESIGN REQUIRED",
                  [("LOG-IN", "LATER DISCONNECT OUTPUT", "ONBOARD_LATER_SD_POS", "left"), ("LOG-OUT", "LATER SOURCE BOUNDARY", "ONBOARD_LATER_SOURCE_OUT", "right"), ("LOG-RET", "LATER PACK RETURN", "ONBOARD_LATER_RET", "left"),
                   ("LOG-CMD", "PRECHARGE REQUEST", "PRECHARGE_REQUEST", "left"), ("LOG-OK", "PRECHARGE STATUS", "PRECHARGE_STATUS", "right")],
                  "This disconnected evaluation path has no tie to ACT_MAIN_SAFE_12V. Resistance, energy, timing, regeneration, bypass faults and discharge time remain open.", (315, 160), width=100.0),
        component(model, "CHG_LATER", "BPC-1502C ONBOARD-LATER CHARGER / INTERLOCK CANDIDATE",
                  [("LOG-POS", "LATER CHARGE POSITIVE", "ONBOARD_LATER_CHARGE_POS", "right"), ("LOG-NEG", "LATER CHARGE RETURN", "ONBOARD_LATER_CHARGE_RET", "right"), ("LOG-INT", "CHARGER PRESENT INHIBIT", "CHARGER_INTERLOCK", "right")],
                  "No charger wiring, connector, charge path or fail-safe interlock circuit is released; powered charging is prohibited.", (110, 215), width=102.0, datasheet="https://www.bioennopower.com/products/14-6v-2a-ac-to-dc-charger-for-12v-lifepo4-batteries-black-anderson"),
    ]
    s18.notes = ["This entire sheet is an isolated future configuration. ONBOARD_LATER_SOURCE_OUT has no connection to ACT_MAIN_SAFE_12V.", "No battery, disconnect, precharge, charger, protection value, connector or conductor is selected or released."]
    sheets.append(s18)
    if len(sheets) != 18:
        raise SystemExit("controlled eighteen-child-sheet architecture drift")
    return sheets


def write_native_project(model, sheets):
    ECAD.mkdir(parents=True, exist_ok=True)
    for path in ECAD.rglob("*"):
        if path.is_file():
            path.unlink()
    net_counts = Counter(pin.net for sheet in sheets for comp in sheet.components for pin in comp.pins)
    wire_numbers = model.build_wire_numbers(sheets, net_counts)
    root_uuid = model.uid("root-hr30-whole-body-electrical-p01")
    (ECAD / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (ECAD / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, net_counts, wire_numbers), encoding="utf-8")
    project_data = {
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}},
        "pcbnew": {}, "schematic": {},
        "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV},
    }
    (ECAD / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    components = [comp for sheet in sheets for comp in sheet.components]
    symbols = [model.lib_symbol(comp).replace(f'(symbol "PBV3:{comp.ref}"', f'(symbol "{comp.ref}"', 1) for comp in components]
    (ECAD / f"{PROJECT}.kicad_sym").write_text(
        '(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '
        + "\n".join(symbols) + "\n)\n", encoding="utf-8",
    )
    (ECAD / "sym-lib-table").write_text(
        f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 P0.1 generated logical symbols"))\n)\n',
        encoding="utf-8",
    )
    model.write_tables(sheets, net_counts, wire_numbers)
    return net_counts


def run_kicad():
    if not KICAD.exists():
        raise SystemExit("KiCad 10 CLI missing")
    validation = ECAD / "validation"
    output = ECAD / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
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
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    (ECAD / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs(sheets):
    contact_map = {
        "RS-LLEG": "JMCU_A/JCA1 contacts 4 TX, 5 RX, 6 DE", "RS-RLEG": "JMCU_A/JCA1 contacts 7 TX, 8 RX, 9 DE",
        "RS-LARM": "JMCU_A/JCA1 contacts 10 TX, 11 RX, 12 DE", "RS-RARM": "JMCU_A/JCA1 contacts 13 TX, 14 RX, 15 DE",
        "RS-WAIST": "JMCU_B/JCB1 contacts 4 TX, 5 RX, 6 DE", "TTL-LDIST": "JMCU_B/JCB1 contacts 7 IO, 8 DIR",
        "TTL-RDIST": "JMCU_B/JCB1 contacts 9 IO, 10 DIR", "TTL-HEAD": "JMCU_B/JCB1 contacts 11 IO, 12 DIR",
    }
    pin_rows = []
    for bus_id, allocation in UART_ALLOCATIONS.items():
        ttl = bus_id.startswith("TTL-")
        tx_name, tx_pin, tx_af = allocation["tx"]
        rx_name, rx_pin, rx_af = allocation["rx"]
        de_name, de_pin, de_af = allocation["de"]
        pin_rows.append({
            "bus_id": bus_id, "carrier": allocation["carrier"], "protocol": "TTL SINGLE-WIRE HALF-DUPLEX" if ttl else "RS-485 HALF-DUPLEX",
            "stm32_peripheral": allocation["uart"], "mcu_tx_or_io": f"{tx_name} package pin {tx_pin} {tx_af}",
            "mcu_rx": f"{rx_name} package pin {rx_pin} {rx_af} - INTENTIONALLY UNUSED IN P0.1" if ttl else f"{rx_name} package pin {rx_pin} {rx_af}",
            "mcu_de": f"{de_name} package pin {de_pin} {de_af}", "internal_connector_contacts": contact_map[bus_id],
            "interface_device": "SN74LVC1T45DCKR" if ttl else "ISOW1432DFMR",
            "field_header": "BM02B-GHS-TBT; 1=reference, 2=data; NO VDD" if ttl else "BM03B-GHS-TBT; 1=reference, 2=data+, 3=data-; NO VDD",
            "selection_boundary": "PCB layout, passives/protection, exact cable assembly, termination/EMC/timing and physical validation remain open",
            "warning": WARNING,
        })
    with (ECAD / "interface-carrier-pinout.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pin_rows[0])); writer.writeheader(); writer.writerows(pin_rows)
    source_rows = [
        {"source_id": "STM32H743ZI", "manufacturer": "STMicroelectronics", "document": "STM32H742xI/G and STM32H743xI/G datasheet", "revision_or_date": "DS12110 Rev 11", "accessed": DATE, "url": ST_H743_SOURCE, "verified": "STM32H743ZIT6 active LQFP144; eight UART/USART peripherals; selected TX/RX/RTS-DE package pins and alternate functions"},
        {"source_id": "ISOW1432", "manufacturer": "Texas Instruments", "document": "ISOW1412/ISOW1432 datasheet", "revision_or_date": "SLLSF86C Rev C; March 2022", "accessed": DATE, "url": TI_ISOW1432_SOURCE, "verified": "ISOW1432DFMR active; 20-pin DFM; exact pins 1-20; 12 Mbps; integrated isolated DC/DC; half-duplex Y/Z and A/B binding"},
        {"source_id": "SN74LVC1T45", "manufacturer": "Texas Instruments", "document": "SN74LVC1T45 datasheet", "revision_or_date": "SCES515N Rev N; June 2024", "accessed": DATE, "url": TI_LVC1T45_SOURCE, "verified": "SN74LVC1T45DCKR active; exact six-pin DCK mapping; 1.65-5.5 V dual rails; DIR high A-to-B"},
        {"source_id": "JST-GH", "manufacturer": "JST", "document": "GH connector catalog", "revision_or_date": "live official catalog; revision not stated", "accessed": DATE, "url": JST_GH_SOURCE, "verified": "GHR-02/03/15V-S housings; BM02/03/15B-GHS-TBT headers; SSHL-002T-P0.2 contact; 1.25 mm secure-lock family"},
        {"source_id": "OPENCR-REF", "manufacturer": "ROBOTIS", "document": "OpenCR Rev H schematic and BOM", "revision_or_date": "Rev H; schematic dated 2020-02-26; official repository checked 2026-08-14", "accessed": DATE, "url": "https://github.com/ROBOTIS-GIT/OpenCR-Hardware", "verified": "manufacturer reference confirms separate UART TX/RX/DIR half-duplex topology and DYNAMIXEL TTL/RS-485 connector conventions; HR-30 uses newer selected devices"},
        {"source_id": "RSP-500-12", "manufacturer": "Mean Well", "document": "RSP-500 series specification", "revision_or_date": "official datasheet; revision not stated", "accessed": DATE, "url": "https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF", "verified": "12 V / 41.7 A / 500.4 W tether-supply candidate; exact panel terminals and application remain open"},
        {"source_id": "SD-15A-24", "manufacturer": "Mean Well", "document": "SD-15 series specification", "revision_or_date": "official datasheet; revision not stated", "accessed": DATE, "url": "https://www.meanwell.com/Upload/PDF/SD-15/SD-15-SPEC.PDF", "verified": "9.2-18 V input to 24 V / 0.625 A safety-control supply candidate"},
        {"source_id": "PNOZ-S4-750104", "manufacturer": "Pilz", "document": "PNOZ s4 operating manual", "revision_or_date": "21396-EN-23; 2026-06-22", "accessed": DATE, "url": "https://www.pilz.com/en-US/eshop/product/750104", "verified": "24 VDC safety-relay candidate; monitored manual start and EDM application concepts; exact circuit and validation open"},
        {"source_id": "GV12", "manufacturer": "Sensata GIGAVAC", "document": "GV12 series datasheet", "revision_or_date": "2022-04-28", "accessed": DATE, "url": "https://www.sensata.com/sites/default/files/a/sensata-gigavac-gv12-series-100v-contactors-datasheet.pdf", "verified": "100 V / 200 A family candidate with optional mechanically linked auxiliary; no IEC mirror-contact claim"},
        {"source_id": "S18V20F9", "manufacturer": "Pololu", "document": "9 V step-up/step-down regulator item 2576", "revision_or_date": "live official product page; revision not stated", "accessed": DATE, "url": "https://www.pololu.com/product/2576", "verified": "9 V regulator candidate for each two-axis XC330 branch; current/thermal/transient proof open"},
    ]
    with (ECAD / "interface-carrier-source-register.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(source_rows[0])); writer.writeheader(); writer.writerows(source_rows)
    (ECAD / "README.md").write_text("# HR-30 whole-body electrical P0.1\n\n"
        f"**{WARNING}**\n\n"
        "This is the native KiCad 10 whole-body architecture for the current 25-axis HR-30 candidate. It contains a root index plus eighteen populated child sheets. Five RS-485 and three TTL data-only segments match the whole-body bus allocation exactly; all 25 actuators have distinct protected-feed boundaries. Individual head HMI devices, pelvis IMU, bilateral four-point foot sensing and a separate isolated onboard-later energy sheet are also represented.\n\n"
        "The actuator interface is now a pin-level candidate, not eight abstract boxes. STM32H743ZIT6 LQFP144 package pins are allocated to all eight UART channels; Carrier A contains four ISOW1432DFMR isolated RS-485 candidates; Carrier B contains one ISOW1432DFMR plus three SN74LVC1T45DCKR 3.3/5 V single-wire TTL translators. Exact JST GH controller and data-only field connectors are shown. The field connectors intentionally contain no actuator VDD contact.\n\n"
        "Sheet 01 now encodes the tether-first controlled 12 V source, three regulated 9 V TTL rails and a deliberately disconnected onboard-later battery/charger path. Sheet 02 encodes two independently commanded series contactor coils, linked-auxiliary EDM candidates, dual-channel E-stop, monitored reset, charger inhibit and an ordinary-watchdog inhibit that has zero safety credit. Reset restores eligibility only and cannot command motion.\n\n"
        "AX_* actuator terminals use current official ROBOTIS actuator-side pin numbers. Remaining `LOG-*` identifiers are unresolved functional ports elsewhere in the architecture. Standard ROBOTIS cables carry VDD, so the 25 distinct feeds require a custom/de-pinned data-only harness or breakout. Fuse/limiter values, conductors, connector selections, grounding, safety allocation, timing and physical behavior remain unresolved. The historical mixed HR-V0/HR-30 project is not incorporated as verified wiring.\n\n"
        "## Sheets\n\n" + "\n".join(f"{s.number}. `{s.filename}` — {s.title}" for s in sheets) + "\n\n"
        "KiCad ERC checks encoded passive-pin connectivity and annotation only. It grants no functional-safety credit and no authority to order, fabricate, connect, power, move or energize the robot.\n",
        encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "kicad_version": "10.0.5", "native_sheet_count": 19,
        "child_sheet_count": 18, "axis_binding_count": 25, "actuator_bus_segment_count": 8,
        "rs485_segment_count": 5, "ttl_segment_count": 3,
        "native_kicad_parsed": True, "erc_errors": 0, "erc_warnings": 0,
        "logical_connectivity_reconciled": True, "actuator_side_physical_pin_mapping_reconciled": True,
        "actuator_bus_controller_physical_pin_mapping_reconciled": True,
        "actuator_bus_interface_device_candidates_selected": True,
        "actuator_bus_data_only_connector_candidates_selected": True,
        "tether_first_energy_topology_encoded": True,
        "direct_14v8_actuator_source_absent": True,
        "individual_actuator_power_feed_count": 25,
        "regulated_ttl_branch_count": 3,
        "reset_can_command_motion": False,
        "physical_pin_mapping_reconciled": False,
        "interface_devices_selected": False, "protection_values_selected": False,
        "functional_safety_validated": False, "connection_authority": False,
        "fabrication_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False, "warning": WARNING,
    }
    (ECAD / "electrical-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    svg_files = sorted((ECAD / "output").glob("*.svg"), key=lambda path: (path.name != f"{PROJECT}.svg", path.name))
    if len(svg_files) != 19:
        raise SystemExit("interactive electrical guide requires root plus eighteen SVG exports")
    panels = []
    nav = []
    for index, svg in enumerate(svg_files):
        title = "Whole-project hierarchy" if svg.name == f"{PROJECT}.svg" else svg.stem.removeprefix(PROJECT + "-")
        anchor = "sheet-" + ("root" if index == 0 else f"{index:02d}")
        nav.append(f'<a href="#{anchor}">{html.escape(title)}</a>')
        panels.append(f'''<details id="{anchor}"{' open' if index == 0 else ''}><summary>{html.escape(title)}</summary><div class="sheet"><object data="output/{html.escape(svg.name, quote=True)}" type="image/svg+xml" aria-label="{html.escape(title, quote=True)} electrical diagram"></object></div><p><a href="output/{html.escape(svg.name, quote=True)}">Open this SVG directly for pan and zoom</a></p></details>''')
    (ECAD / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 interactive electrical guide P0.1</title><style>:root{{--ink:#061a36;--sky:#8ed8ff;--blue:#0a4b91;--gold:#f5bd2b;--paper:#f6fbff}}*{{box-sizing:border-box}}body{{margin:0;font:17px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{max-width:none;background:var(--ink);color:white}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}.warning{{border:3px solid var(--gold);padding:14px;font-weight:900}}nav{{display:flex;flex-wrap:wrap;gap:10px}}nav a,details>p a{{display:inline-block;color:#064f91;font-weight:800}}nav a{{padding:9px 12px;background:white;border:2px solid var(--blue);border-radius:10px;text-decoration:none}}details{{margin:18px 0;background:white;border:2px solid var(--blue);border-radius:14px;overflow:hidden}}summary{{padding:16px 18px;font-size:18px;font-weight:850;cursor:pointer;background:#e4f6ff}}.sheet{{width:100%;height:clamp(520px,72vh,820px);overflow:auto;background:#fff}}object{{display:block;width:100%;height:100%;min-width:900px}}details>p{{margin:0;padding:12px 18px;border-top:1px solid #9ccfe8}}small{{font-size:14px}}@media(max-width:680px){{body{{font-size:16px}}header,main{{padding:20px 14px}}summary{{font-size:17px}}.sheet{{height:560px}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Explore all 19 native KiCad sheets.</h1><p>The project now encodes the tether-first 12 V architecture, three regulated 9 V TTL rails, 25 individual actuator feeds and sourced controller-interface candidates.</p></div></header><main><nav>{''.join(nav)}</nav><section><h2>Connected preliminary architecture</h2><p>KiCad 10 ERC reports 0 errors and 0 warnings. That verifies encoded connectivity and annotation only. All protection values, physical energy/safety terminals, conductor sizes, grounding, stopping behavior, safety validation, and connection or energization authority remain open.</p><p><a href="interface-carrier-pinout.csv">Eight-channel physical pin map</a> · <a href="interface-carrier-source-register.csv">Primary-source register</a></p>{''.join(panels)}</section></main></body></html>''', encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), ECAD / "native-kicad-source.py")


def update_package():
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "native_hr30_kicad_present": True,
        "native_hr30_kicad_sheet_count": 19,
        "native_hr30_kicad_axis_binding_count": 25,
        "native_hr30_kicad_logical_connectivity_reconciled": True,
        "native_hr30_kicad_actuator_side_pins_reconciled": True,
        "native_hr30_kicad_reconciled": False,
        "native_hr30_kicad_actuator_bus_controller_pins_selected": True,
        "native_hr30_kicad_interface_device_candidates_selected": True,
        "native_hr30_kicad_data_only_connector_candidates_selected": True,
        "native_hr30_kicad_tether_first_energy_topology_encoded": True,
        "native_hr30_kicad_direct_14v8_actuator_source_absent": True,
        "native_hr30_kicad_individual_actuator_power_feed_count": 25,
        "native_hr30_kicad_regulated_ttl_branch_count": 3,
        "native_hr30_kicad_physical_pins_selected": False,
        "native_hr30_kicad_erc_errors": 0,
        "native_hr30_kicad_erc_warnings": 0,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds_path = PACKAGE / "open-holds.csv"
    holds = read_csv(holds_path)
    for row in holds:
        if row["hold_id"] == "HR30-P01-H11":
            row["unresolved_item"] = "The native 19-sheet HR-30 KiCad project binds all 25 axes, encodes the tether-first 12 V energy path, three regulated 9 V TTL rails, 25 separate actuator power-feed boundaries, eight verified UART pin groups, and five ISOW1432DFMR plus three SN74LVC1T45DCKR data-interface candidates. The onboard-later source remains isolated on its own sheet. Exact energy/safety terminals, protection values, termination/bias, custom data-only cable assemblies, grounding, EMC, timing, sensing calibration, safety allocation and physical fault tests remain open."
    with holds_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(holds[0]))
        writer.writeheader(); writer.writerows(holds)
    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-NATIVE-KICAD-P01-START -->"; end = "<!-- HR30-NATIVE-KICAD-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    # A clean build creates the native electrical source before the derived
    # actuator-bus section.  Anchor both at the stable system-artifacts section
    # instead of requiring either generated section to pre-exist.
    marker = '<section><h2>System artifacts</h2>'
    section = f'''{start}<section id="native-electrical"><h2>The whole robot now has a tether-first native electrical architecture</h2><div class="grid"><article class="card pass"><h3>19 native sheets</h3><p>One hierarchy page and eighteen populated child sheets cover energy, safety, compute, every actuator segment, head HMI, pelvis IMU, both feet and the isolated onboard-later path.</p></article><article class="card pass"><h3>25 separate feeds</h3><p>Every actuator pin-2 VDD now has its own unresolved protection/telemetry boundary; the multidrop harness carries data and reference only.</p></article><article class="card pass"><h3>12 V + three 9 V rails</h3><p>The rejected direct 14.8 V path is gone. XH/XM use the controlled tether rail while each XC330 segment has a regulated 9 V candidate.</p></article><article class="card hold"><h3>ERC: 0 / 0</h3><p>KiCad validates encoded connectivity only. Protection values, physical energy/safety terminals, stopping behavior and validation remain open.</p></article></div><div class="viewer"><object data="electrical/kicad/{PROJECT}/output/{PROJECT}.svg" type="image/svg+xml" aria-label="Interactive HR-30 native KiCad hierarchy diagram"></object><p><a href="electrical/kicad/{PROJECT}/index.html">Open the interactive 19-sheet electrical guide</a>, inspect the <a href="electrical/kicad/{PROJECT}/interface-carrier-pinout.csv">eight-channel pin map</a>, or download the <a href="electrical/kicad/{PROJECT}/{PROJECT}.kicad_pro">KiCad project</a>, <a href="electrical/kicad/{PROJECT}/connector-schedule.csv">terminal schedule</a>, <a href="electrical/kicad/{PROJECT}/net-schedule.csv">net schedule</a>, and <a href="electrical/kicad/{PROJECT}/validation/{PROJECT}-erc.rpt">complete ERC report</a>.</p></div></section>{end}'''
    if marker not in page:
        raise SystemExit("system artifact web marker missing")
    page_path.write_text(page.replace(marker, section + marker), encoding="utf-8", newline="\n")
    import generate_hr30_system_package_p01 as system
    system.refresh_manifest_and_release()


def write_manifest():
    rows = []
    for path in sorted(ECAD.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(ECAD).as_posix(), path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest()))
    with (ECAD / "SOURCE-MANIFEST.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle); writer.writerow(["path", "bytes", "sha256"]); writer.writerows(rows)


def main() -> int:
    model = load_model()
    sheets = build_sheets(model)
    write_native_project(model, sheets)
    run_kicad()
    write_docs(sheets)
    write_manifest()
    update_package()
    print(json.dumps({"identifier": IDENTIFIER, "native_sheets": 19, "axes": 25, "segments": 8, "erc_errors": 0, "erc_warnings": 0, "actuator_bus_controller_pins_reconciled": True, "whole_project_physical_pin_mapping_reconciled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
