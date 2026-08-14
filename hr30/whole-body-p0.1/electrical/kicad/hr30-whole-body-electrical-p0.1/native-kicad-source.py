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
    """Render the fifteen-child HR-30 hierarchy without changing the frozen HR-V0 generator."""
    positions = [(12.0 + col * 100.0, 42.0 + row * 56.0) for row in range(4) for col in range(4)]
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


def component(model, ref, value, pins, description, position, width=72.0, datasheet="", evidence="", status="SELECTION REQUIRED - LOGICAL CONNECTIVITY ONLY"):
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
            ("2", "VDD", f"{bus_id}_VDD", "left"),
            ("1", "GND", f"{bus_id}_RET", "left"),
            ("3", "DATA+", f"{bus_id}_DP", "right"),
            ("4", "DATA-", f"{bus_id}_DN", "right"),
        ]
    else:
        pins = [
            ("2", "VDD", f"{bus_id}_VDD", "left"),
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
    sheet = model.Sheet(number, filename, title, f"Connected {bus_id} data segment and separately protected actuator-power branch.")
    protocol = "RS-485" if bus_id.startswith("RS-") else "TTL"
    data_pins = [
        ("LOG-RET", "DATA REFERENCE", f"{bus_id}_RET", "left"),
        ("LOG-DP", "DATA+", f"{bus_id}_DP", "right"),
        ("LOG-DN", "DATA-", f"{bus_id}_DN", "right"),
    ] if protocol == "RS-485" else [
        ("LOG-RET", "DATA REFERENCE", f"{bus_id}_RET", "left"),
        ("LOG-DATA", "HALF-DUPLEX DATA", f"{bus_id}_DATA", "right"),
    ]
    sheet.components.append(component(
        model, "PORT_" + bus_id.replace("-", "_"), f"{bus_id} DATA-ONLY HARNESS PORT - CONNECTOR SELECTION REQUIRED", data_pins,
        "Logical data-only boundary from the matching controller interface. Exact connector, pins, reference conductor, shield and strain relief remain open.",
        (105, 55), width=115.0,
    ))
    source_net = "ACT_14V8_SAFE" if protocol == "RS-485" else "ACT_12V_SAFE"
    sheet.components.append(component(
        model, "PBR_" + bus_id.replace("-", "_"), f"{bus_id} BRANCH PROTECTION / TELEMETRY - SELECTION REQUIRED",
        [("LOG-IN", "INTERRUPTED SOURCE", source_net, "left"), ("LOG-OUT", "PROTECTED VDD", f"{bus_id}_VDD", "right"),
         ("LOG-RET-IN", "SOURCE RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-RET-OUT", "BRANCH RETURN", f"{bus_id}_RET", "right"),
         ("LOG-TLM", "BRANCH TELEMETRY", f"TLM_{bus_id}", "right")],
        "No fuse, limiter, conductor or connector rating is released. Fault current, inrush, cable length, ambient, bundling, duty cycle and jurisdiction remain required inputs.",
        (285, 90), width=140.0,
    ))
    if len(axes) == 6:
        locations = [(145, 130), (330, 130), (145, 185), (330, 185), (145, 235), (330, 235)]
    elif len(axes) == 3:
        locations = [(145, 145), (330, 145), (240, 210)]
    elif len(axes) == 2:
        locations = [(145, 175), (330, 175)]
    elif len(axes) == 1:
        locations = [(240, 165)]
    else:
        raise SystemExit(f"unsupported segment population for {bus_id}: {len(axes)}")
    for axis, position in zip(axes, locations):
        sheet.components.append(axis_component(model, by_axis, axis, bus_id, position))
    sheet.notes = [
        "The segment shares data and branch power only among the listed axes; it does not join any other protected branch VDD.",
        "AX_* terminals use current official ROBOTIS actuator-side pin numbers; all LOG-* identifiers remain functional ports, not physical connector or IC pins.",
        "Termination, bias, actuator IDs, baud rate, cable length, waveform, latency, EMC, thermal and fault behavior remain unvalidated.",
    ]
    return sheet


def build_sheets(model):
    allocation = read_csv(PACKAGE / "actuator-transmission-allocation.csv")
    by_axis = {row["axis_id"]: row for row in allocation}
    expected = {axis for axes in BUS_AXES.values() for axis in axes}
    if len(allocation) != 25 or set(by_axis) != expected:
        raise SystemExit("whole-body actuator allocation drift")

    sheets = []
    s1 = model.Sheet(1, "01_energy_precharge_conversion.kicad_sch", "Energy, service disconnect, precharge and conversion", "Whole-body DC source and interrupted 14.8/12 V boundaries; every physical selection remains open.")
    s1.components = [
        component(model, "BATT1", "4S 14.8 V 12 Ah PACK EVALUATION CANDIDATE - COMPLETE SOURCE SELECTION OPEN",
                  [("LOG-POS", "PACK POSITIVE", "BATT_POS_RAW", "right"), ("LOG-NEG", "PACK NEGATIVE", "BATT_0V_RAW", "right"),
                   ("LOG-TEMP", "PACK TEMPERATURE", "TLM_PACK_TEMP", "right"), ("LOG-BMS", "BMS STATUS", "TLM_BMS_STATUS", "right")],
                  "Pack envelope exists in CAD. BMS/PCM, containment, retention, connector, protection, charger and fault behavior remain unselected.", (66, 88), width=88.0),
        component(model, "SD1", "DC SERVICE DISCONNECT - SELECTION REQUIRED",
                  [("LOG-IN", "RAW POSITIVE IN", "BATT_POS_RAW", "left"), ("LOG-OUT", "ISOLATED POSITIVE OUT", "SD_POS_OUT", "right")],
                  "DC voltage/current/fault rating, touch safety, interlock and mounting remain open.", (178, 88), width=80.0),
        component(model, "PRE1", "PRECHARGE / DISCHARGE NETWORK - DESIGN REQUIRED",
                  [("LOG-IN", "DISCONNECT OUTPUT", "SD_POS_OUT", "left"), ("LOG-MAIN", "CONTACTOR INPUT", "CONTACTOR_POS_IN", "right"),
                   ("LOG-CMD", "PRECHARGE REQUEST", "PRECHARGE_REQUEST", "left"), ("LOG-OK", "PRECHARGE STATUS", "PRECHARGE_STATUS", "right")],
                  "Resistance, energy, timing, welded/bypass faults, discharge time and control device remain selection/calculation/test work.", (291, 88), width=88.0),
        component(model, "DCDC1", "INTERRUPTED 14.8 V TO 12 V CONVERTER - SELECTION REQUIRED",
                  [("LOG-IN", "INTERRUPTED 14.8 V", "ACT_14V8_SAFE", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"),
                   ("LOG-OUT", "12 V ACTUATOR SOURCE", "ACT_12V_SAFE", "right"), ("LOG-RET-OUT", "12 V RETURN", "ACT_0V_CONTROLLED", "right"),
                   ("LOG-EN", "CONVERTER ENABLE", "SAFETY_PERMIT_HARDWIRED", "left"), ("LOG-TLM", "CONVERTER TELEMETRY", "TLM_DCDC12", "right")],
                  "Exact converter, input/output protection, isolation/bonding, regeneration behavior, inrush, thermal and EMC evidence remain open.", (178, 176), width=92.0),
        component(model, "CHG1", "CHARGER PORT / INTERLOCK - SELECTION REQUIRED",
                  [("LOG-POS", "CHARGE POSITIVE", "CHARGE_POS", "right"), ("LOG-NEG", "CHARGE RETURN", "CHARGE_RET", "right"),
                   ("LOG-INT", "CHARGER PRESENT INTERLOCK", "CHARGER_INTERLOCK", "right")],
                  "No charger, connector, charge path or interlock circuit is selected; powered charging is prohibited.", (291, 176), width=86.0),
        component(model, "RET1", "DC RETURN / FRAME / PE BOUNDARY - DESIGN REQUIRED",
                  [("LOG-BATT", "PACK RETURN", "BATT_0V_RAW", "left"), ("LOG-ACT", "CONTROLLED ACTUATOR RETURN", "ACT_0V_CONTROLLED", "right"),
                   ("LOG-PE", "PROTECTIVE EARTH / FRAME", "FRAME_PE_BOUNDARY", "right")],
                  "Single-point bond, floating/onboard mode, charger/tether PE, shield treatment and fault-current path require jurisdiction-specific qualified design.", (66, 176), width=88.0),
    ]
    s1.notes = ["No fuse value, conductor size, connector rating or physical pin is released.", "Charger presence must inhibit actuator permit, but the exact fail-safe implementation is not selected."]
    sheets.append(s1)

    s2 = model.Sheet(2, "02_estop_permit_contactors.kicad_sch", "Dual-channel E-stop, monitored reset, permit and redundant interruption", "Logical whole-body safety interruption architecture; no functional-safety approval or application release.")
    s2.components = [
        component(model, "S0", "DUAL-CHANNEL E-STOP DEVICE - SELECTION REQUIRED",
                  [("LOG-C1F", "CHANNEL 1 FEED", "ESTOP_CH1_FEED", "left"), ("LOG-C1R", "CHANNEL 1 RETURN", "ESTOP_CH1_RETURN", "right"),
                   ("LOG-C2F", "CHANNEL 2 FEED", "ESTOP_CH2_FEED", "left"), ("LOG-C2R", "CHANNEL 2 RETURN", "ESTOP_CH2_RETURN", "right")],
                  "Exact device, contacts, terminals, enclosure, spacing and direct-opening application remain selection and qualified review work.", (65, 87), width=86.0),
        component(model, "S1", "MONITORED MANUAL RESET DEVICE - SELECTION REQUIRED",
                  [("LOG-FEED", "RESET FEED", "RESET_FEED", "left"), ("LOG-RETURN", "RESET RETURN", "RESET_RETURN", "right")],
                  "Reset is eligibility only and must not command motion. Exact anti-tie-down/contact/terminal behavior requires selection and physical test.", (175, 87), width=82.0),
        component(model, "SR1", "SAFETY CONTROL / EDM FUNCTION - APPLICATION SELECTION REQUIRED",
                  [("LOG-C1F", "E-STOP CH1 FEED", "ESTOP_CH1_FEED", "right"), ("LOG-C1R", "E-STOP CH1 RETURN", "ESTOP_CH1_RETURN", "left"),
                   ("LOG-C2F", "E-STOP CH2 FEED", "ESTOP_CH2_FEED", "right"), ("LOG-C2R", "E-STOP CH2 RETURN", "ESTOP_CH2_RETURN", "left"),
                   ("LOG-RF", "RESET FEED", "RESET_FEED", "right"), ("LOG-RR", "RESET / EDM RETURN", "RESET_RETURN", "left"),
                   ("LOG-PERMIT", "HARDWIRED PERMIT", "SAFETY_PERMIT_HARDWIRED", "right"), ("LOG-EDM1", "K1 MIRROR RETURN", "EDM_K1", "left"),
                   ("LOG-EDM2", "K2 MIRROR RETURN", "EDM_K2", "left"), ("LOG-CHG", "CHARGER INHIBIT", "CHARGER_INTERLOCK", "left")],
                  "Required PLr/SIL, exact architecture/category, common-cause, diagnostic coverage, reset mode, reaction time and validation are not established.", (292, 105), width=96.0),
        component(model, "K1", "DC CONTACTOR 1 WITH MIRROR CONTACT - SELECTION REQUIRED",
                  [("LOG-MIN", "MAIN INPUT", "CONTACTOR_POS_IN", "left"), ("LOG-MOUT", "MAIN OUTPUT", "K1_POS_OUT", "right"),
                   ("LOG-COIL", "COIL PERMIT", "SAFETY_PERMIT_HARDWIRED", "left"), ("LOG-MIR", "MIRROR / EDM", "EDM_K1", "right")],
                  "DC interruption duty, coil suppression, mirror-contact semantics, fault current and life require manufacturer application confirmation.", (122, 187), width=88.0),
        component(model, "K2", "DC CONTACTOR 2 WITH MIRROR CONTACT - SELECTION REQUIRED",
                  [("LOG-MIN", "MAIN INPUT", "K1_POS_OUT", "left"), ("LOG-MOUT", "MAIN OUTPUT", "ACT_14V8_SAFE", "right"),
                   ("LOG-COIL", "COIL PERMIT", "SAFETY_PERMIT_HARDWIRED", "left"), ("LOG-MIR", "MIRROR / EDM", "EDM_K2", "right")],
                  "Second series interruption channel; common-cause, welded-contact and energy-removal behavior remain unvalidated.", (250, 187), width=88.0),
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
        component(model, "MCU1", "DETERMINISTIC MOTION CONTROLLER - EXACT BOARD SELECTION REQUIRED", mcu_pins,
                  "Owns state estimation, bounded trajectories, joint limits, bus timing and fault states. Exact MCU board, I/O pins, isolation, real-time performance and firmware evidence remain open.", (210, 85), width=90.0),
        component(model, "WD1", "INDEPENDENT ORDINARY WATCHDOG - SELECTION REQUIRED / ZERO SAFETY CREDIT",
                  [("LOG-HB", "MOTION HEARTBEAT INPUT", "MOTION_WD_HEARTBEAT", "left"), ("LOG-REQ", "PERMIT REQUEST DIAGNOSTIC", "WD_PERMIT_REQUEST", "right")],
                  "Heartbeat supervision is diagnostic only and may not bypass S0, monitored reset, EDM or deterministic motion authorization.", (355, 55), width=75.0),
    ]
    io_positions = [(115, 125), (315, 125), (115, 165), (315, 165), (115, 205), (315, 205), (115, 235), (315, 235)]
    for index, (bus_id, position) in enumerate(zip(BUS_AXES, io_positions)):
        side = "left" if index % 2 == 0 else "right"
        port = component(
            model, "MCU_IO_" + bus_id.replace("-", "_"), f"MCU1 LOGICAL UART BANK - {bus_id}",
            [(f"LOG-{bus_id}-TX", "UART TX", f"UART_{bus_id}_TX", side),
             (f"LOG-{bus_id}-RX", "UART RX", f"UART_{bus_id}_RX", side),
             (f"LOG-{bus_id}-DIR", "DIRECTION", f"UART_{bus_id}_DIR", side)],
            "This is an alternate logical-unit view of MCU1, not an additional controller or released package pin assignment.",
            position, width=100.0,
        )
        port.quantity = 0
        s3.components.append(port)
    s3.notes = ["Conversational compute emits expiring high-level actions only; it never writes actuator registers.", "Hardwired permit loss forces controller outputs disabled; permit restoration alone must not start motion."]
    sheets.append(s3)

    s4 = model.Sheet(4, "04_eight_actuator_bus_interfaces.kicad_sch", "Five isolated RS-485 and three protected TTL interface channels", "Logical UART-to-field conversion for all eight independently identified actuator buses.")
    positions = [(115, 65), (315, 65), (115, 115), (315, 115), (115, 165), (315, 165), (115, 215), (315, 215)]
    for (bus_id, axes), position in zip(BUS_AXES.items(), positions):
        if bus_id.startswith("RS-"):
            pins = [("LOG-TX", "UART TX", f"UART_{bus_id}_TX", "left"), ("LOG-RX", "UART RX", f"UART_{bus_id}_RX", "left"),
                    ("LOG-DIR", "DIRECTION", f"UART_{bus_id}_DIR", "left"), ("LOG-DP", "FIELD DATA+", f"{bus_id}_DP", "right"),
                    ("LOG-DN", "FIELD DATA-", f"{bus_id}_DN", "right"), ("LOG-REF", "FIELD REFERENCE", f"{bus_id}_RET", "right")]
            value = f"{bus_id} ISOLATED HALF-DUPLEX RS-485 CHANNEL - SELECTION REQUIRED"
        else:
            pins = [("LOG-TX", "UART TX", f"UART_{bus_id}_TX", "left"), ("LOG-RX", "UART RX", f"UART_{bus_id}_RX", "left"),
                    ("LOG-DIR", "DIRECTION", f"UART_{bus_id}_DIR", "left"), ("LOG-DATA", "FIELD HALF-DUPLEX DATA", f"{bus_id}_DATA", "right"),
                    ("LOG-REF", "FIELD REFERENCE", f"{bus_id}_RET", "right")]
            value = f"{bus_id} PROTECTED 3.3 V / TTL HALF-DUPLEX CHANNEL - SELECTION REQUIRED"
        s4.components.append(component(model, "IF_" + bus_id.replace("-", "_"), value, pins,
                                       "Exact transceiver/buffer, isolated supply, package pins, passives, termination/bias or level shifting, protection and layout are not selected.", position, width=100.0))
    s4.notes = ["The eight boxes are functional channels, not released circuits or PCB footprints.", "Five RS-485 and three TTL channels exactly match actuator-bus-topology.csv."]
    sheets.append(s4)

    sheets.append(bus_sheet(model, 5, "05_left_leg_rs485.kicad_sch", "Left-leg RS-485 and protected branch", "RS-LLEG", BUS_AXES["RS-LLEG"], by_axis))
    sheets.append(bus_sheet(model, 6, "06_right_leg_rs485.kicad_sch", "Right-leg RS-485 and protected branch", "RS-RLEG", BUS_AXES["RS-RLEG"], by_axis))
    # Proximal arm plus waist sheets preserve one physical segment per named bus.
    sheets.append(bus_sheet(model, 7, "07_left_arm_rs485.kicad_sch", "Left proximal-arm RS-485 and protected branch", "RS-LARM", BUS_AXES["RS-LARM"], by_axis))
    sheets.append(bus_sheet(model, 8, "08_right_arm_rs485.kicad_sch", "Right proximal-arm RS-485 and protected branch", "RS-RARM", BUS_AXES["RS-RARM"], by_axis))
    sheets.append(bus_sheet(model, 9, "09_waist_rs485.kicad_sch", "Waist RS-485 and protected branch", "RS-WAIST", BUS_AXES["RS-WAIST"], by_axis))
    sheets.append(bus_sheet(model, 10, "10_left_distal_ttl.kicad_sch", "Left wrist/gripper TTL and protected branch", "TTL-LDIST", BUS_AXES["TTL-LDIST"], by_axis))
    sheets.append(bus_sheet(model, 11, "11_right_distal_ttl.kicad_sch", "Right wrist/gripper TTL and protected branch", "TTL-RDIST", BUS_AXES["TTL-RDIST"], by_axis))

    s12 = bus_sheet(model, 12, "12_head_ttl_sensors_hmi.kicad_sch", "Head TTL, cameras, face display, audio and cooling", "TTL-HEAD", BUS_AXES["TTL-HEAD"], by_axis)
    s12.components.extend([
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
    sheets.append(s12)

    s13 = model.Sheet(13, "13_pelvis_aux_imu.kicad_sch", "Auxiliary conversion and pelvis inertial sensing", "Logical 5 V auxiliary rail and pelvis IMU boundary.")
    s13.components = [
        component(model, "AUXD1", "14.8 V TO 5.1 V AUXILIARY CONVERTER - SELECTION REQUIRED", [("LOG-IN", "INTERRUPTED INPUT", "ACT_14V8_SAFE", "left"), ("LOG-RET-IN", "CONTROLLED RETURN", "ACT_0V_CONTROLLED", "left"), ("LOG-OUT", "AUXILIARY 5 V", "AUX_5V_SAFE", "right"), ("LOG-RET-OUT", "AUXILIARY RETURN", "AUX_0V", "right"), ("LOG-TLM", "CONVERTER TELEMETRY", "TLM_AUXD1", "right")], "Exact converter, protection, isolation/bonding, inrush, thermal and EMC evidence remain open.", (125, 115), width=96.0),
        component(model, "IMU1", "PELVIS 6/9-AXIS IMU - SELECTION REQUIRED", [("LOG-5V", "5 V POWER", "AUX_5V_SAFE", "left"), ("LOG-RET", "RETURN", "AUX_0V", "left"), ("LOG-DATA", "DETERMINISTIC SENSOR DATA", "PELVIS_IMU_DATA", "right"), ("LOG-INT", "DATA READY / FAULT", "PELVIS_IMU_INT", "right")], "Exact device, range, bandwidth, timestamping, calibration, connector and physical pins remain open.", (315, 115), width=92.0),
        component(model, "MCU_AUX", "MCU1 AUXILIARY SENSOR PORTS - LOGICAL UNIT", [("LOG-IMU", "PELVIS IMU DATA", "PELVIS_IMU_DATA", "left"), ("LOG-IMU-INT", "PELVIS IMU INTERRUPT", "PELVIS_IMU_INT", "left"), ("LOG-LFOOT", "LEFT FOOT SENSOR DATA", "L_FOOT_SENSOR_DATA", "right"), ("LOG-RFOOT", "RIGHT FOOT SENSOR DATA", "R_FOOT_SENSOR_DATA", "right")], "Alternate logical view of MCU1; exact package pins and interfaces remain open.", (220, 215), width=100.0),
    ]
    sheets.append(s13)

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

    sheets.append(foot_sheet(14, "left"))
    sheets.append(foot_sheet(15, "right"))
    if len(sheets) != 15:
        raise SystemExit("controlled fifteen-child-sheet architecture drift")
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
    (ECAD / "README.md").write_text("# HR-30 whole-body electrical P0.1\n\n"
        f"**{WARNING}**\n\n"
        "This is the native KiCad 10 whole-body architecture for the current 25-axis HR-30 candidate. It contains a root index plus fifteen populated child sheets. Five RS-485 and three TTL actuator segments match the whole-body bus allocation exactly; individual head HMI devices, pelvis IMU and bilateral four-point foot sensing are also represented.\n\n"
        "AX_* actuator terminals use current official ROBOTIS actuator-side pin numbers. All `LOG-*` terminal identifiers are functional ports, not physical connector or IC pin numbers. Controller/interface pins, exact devices, order codes, fuse/limiter values, conductors, connectors, grounding, shield treatment, safety allocation, stopping time and physical behavior remain unresolved. The historical mixed HR-V0/HR-30 project is not incorporated as verified wiring.\n\n"
        "## Sheets\n\n" + "\n".join(f"{s.number}. `{s.filename}` — {s.title}" for s in sheets) + "\n\n"
        "KiCad ERC checks encoded passive-pin connectivity and annotation only. It grants no functional-safety credit and no authority to order, fabricate, connect, power, move or energize the robot.\n",
        encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "kicad_version": "10.0.5", "native_sheet_count": 16,
        "child_sheet_count": 15, "axis_binding_count": 25, "actuator_bus_segment_count": 8,
        "rs485_segment_count": 5, "ttl_segment_count": 3,
        "native_kicad_parsed": True, "erc_errors": 0, "erc_warnings": 0,
        "logical_connectivity_reconciled": True, "actuator_side_physical_pin_mapping_reconciled": True,
        "physical_pin_mapping_reconciled": False,
        "interface_devices_selected": False, "protection_values_selected": False,
        "functional_safety_validated": False, "connection_authority": False,
        "fabrication_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False, "warning": WARNING,
    }
    (ECAD / "electrical-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    svg_files = sorted((ECAD / "output").glob("*.svg"), key=lambda path: (path.name != f"{PROJECT}.svg", path.name))
    if len(svg_files) != 16:
        raise SystemExit("interactive electrical guide requires root plus fifteen SVG exports")
    panels = []
    nav = []
    for index, svg in enumerate(svg_files):
        title = "Whole-project hierarchy" if svg.name == f"{PROJECT}.svg" else svg.stem.removeprefix(PROJECT + "-")
        anchor = "sheet-" + ("root" if index == 0 else f"{index:02d}")
        nav.append(f'<a href="#{anchor}">{html.escape(title)}</a>')
        panels.append(f'''<details id="{anchor}"{' open' if index == 0 else ''}><summary>{html.escape(title)}</summary><div class="sheet"><object data="output/{html.escape(svg.name, quote=True)}" type="image/svg+xml" aria-label="{html.escape(title, quote=True)} electrical diagram"></object></div><p><a href="output/{html.escape(svg.name, quote=True)}">Open this SVG directly for pan and zoom</a></p></details>''')
    (ECAD / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 interactive electrical guide P0.1</title><style>:root{{--ink:#061a36;--sky:#8ed8ff;--blue:#0a4b91;--gold:#f5bd2b;--paper:#f6fbff}}*{{box-sizing:border-box}}body{{margin:0;font:17px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{max-width:none;background:var(--ink);color:white}}header>div{{max-width:1180px;margin:auto}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}.warning{{border:3px solid var(--gold);padding:14px;font-weight:900}}nav{{display:flex;flex-wrap:wrap;gap:10px}}nav a,details>p a{{display:inline-block;color:#064f91;font-weight:800}}nav a{{padding:9px 12px;background:white;border:2px solid var(--blue);border-radius:10px;text-decoration:none}}details{{margin:18px 0;background:white;border:2px solid var(--blue);border-radius:14px;overflow:hidden}}summary{{padding:16px 18px;font-size:18px;font-weight:850;cursor:pointer;background:#e4f6ff}}.sheet{{width:100%;height:clamp(520px,72vh,820px);overflow:auto;background:#fff}}object{{display:block;width:100%;height:100%;min-width:900px}}details>p{{margin:0;padding:12px 18px;border-top:1px solid #9ccfe8}}small{{font-size:14px}}@media(max-width:680px){{body{{font-size:16px}}header,main{{padding:20px 14px}}summary{{font-size:17px}}.sheet{{height:560px}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>Explore all 16 native KiCad sheets.</h1><p>The hierarchy and every populated child sheet are embedded below. Pan within a diagram or open its SVG directly for browser zoom.</p></div></header><main><nav>{''.join(nav)}</nav><section><h2>Connected logical architecture</h2><p>KiCad 10 ERC reports 0 errors and 0 warnings. That verifies encoded connectivity and annotation only. Physical controller pins, exact devices, protection, grounding, safety validation, and all connection or energization authority remain open.</p>{''.join(panels)}</section></main></body></html>''', encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), ECAD / "native-kicad-source.py")


def update_package():
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "native_hr30_kicad_present": True,
        "native_hr30_kicad_sheet_count": 16,
        "native_hr30_kicad_axis_binding_count": 25,
        "native_hr30_kicad_logical_connectivity_reconciled": True,
        "native_hr30_kicad_actuator_side_pins_reconciled": True,
        "native_hr30_kicad_reconciled": False,
        "native_hr30_kicad_physical_pins_selected": False,
        "native_hr30_kicad_erc_errors": 0,
        "native_hr30_kicad_erc_warnings": 0,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds_path = PACKAGE / "open-holds.csv"
    holds = read_csv(holds_path)
    for row in holds:
        if row["hold_id"] == "HR30-P01-H11":
            row["unresolved_item"] = "A native 16-sheet HR-30 KiCad project now binds all 25 axes to five RS-485 and three TTL segments, separates the head HMI devices, and includes the pelvis IMU plus bilateral four-point foot sensing with zero ERC violations. Current ROBOTIS documentation closes actuator-side pins only. Controller/interface devices and pins, cable/breakout hardware, protection values, termination/bias/level shifting, data-only harness isolation, grounding, EMC, timing/latency, sensing calibration, safety allocation and physical fault tests remain open."
    with holds_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(holds[0]))
        writer.writeheader(); writer.writerows(holds)
    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-NATIVE-KICAD-P01-START -->"; end = "<!-- HR30-NATIVE-KICAD-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = '<section id="actuator-buses">'
    section = f'''{start}<section id="native-electrical"><h2>The whole robot now has native KiCad source</h2><div class="grid"><article class="card pass"><h3>16 native sheets</h3><p>One hierarchy page and fifteen populated child sheets cover energy, interruption, compute/control, every actuator bus, individual head HMI devices, pelvis IMU and both instrumented feet.</p></article><article class="card pass"><h3>25 axes connected</h3><p>All nineteen RS-485 and six TTL actuator candidates appear in the native netlist on their assigned whole-body segments.</p></article><article class="card pass"><h3>Whole-body sensing shown</h3><p>The face display, cameras, microphone, amplifier, speakers, fan, pelvis IMU and eight sole sensors have explicit logical terminals.</p></article><article class="card hold"><h3>ERC: 0 / 0</h3><p>KiCad 10 reports zero errors and zero warnings for encoded connectivity. ERC is not a physical, safety, or energization approval.</p></article></div><div class="viewer"><object data="electrical/kicad/{PROJECT}/output/{PROJECT}.svg" type="image/svg+xml" aria-label="Interactive HR-30 native KiCad hierarchy diagram"></object><p><a href="electrical/kicad/{PROJECT}/index.html">Open the interactive 16-sheet electrical guide</a>, or download the <a href="electrical/kicad/{PROJECT}/{PROJECT}.kicad_pro">KiCad project</a>, <a href="electrical/kicad/{PROJECT}/connector-schedule.csv">terminal schedule</a>, <a href="electrical/kicad/{PROJECT}/net-schedule.csv">net schedule</a>, and <a href="electrical/kicad/{PROJECT}/validation/{PROJECT}-erc.rpt">complete ERC report</a>.</p></div></section>{end}'''
    if marker not in page:
        raise SystemExit("actuator bus web marker missing")
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
    print(json.dumps({"identifier": IDENTIFIER, "native_sheets": 16, "axes": 25, "segments": 8, "erc_errors": 0, "erc_warnings": 0, "physical_pin_mapping_reconciled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
