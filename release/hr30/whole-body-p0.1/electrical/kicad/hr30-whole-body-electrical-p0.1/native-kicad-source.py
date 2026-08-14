"""Generate the native HR-30 whole-body electrical P0.1 KiCad project.

The project is a connected, editable whole-body architecture.  It deliberately
uses logical terminal identifiers wherever exact device, connector, protection
or package pins remain unselected.  ERC therefore checks encoded connectivity
and annotation only; it is not permission to connect or energize hardware.
"""

from __future__ import annotations

import csv
import hashlib
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
    return module


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def component(model, ref, value, pins, description, position, width=72.0, datasheet="", evidence=""):
    return model.Component(
        ref=ref,
        value=value,
        pins=[model.pn(ref, number, name, net, side) for number, name, net, side in pins],
        status="SELECTION REQUIRED - LOGICAL CONNECTIVITY ONLY",
        description=description,
        datasheet=datasheet,
        evidence=evidence,
        position=position,
        width=width,
    )


def actuator_candidate(by_axis: dict[str, dict], axis: str) -> tuple[str, str]:
    candidate = by_axis[axis]["candidate_actuator"]
    if "XH540" in candidate:
        return candidate, "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/"
    if "XM540" in candidate:
        return candidate, "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/"
    if "XM430" in candidate:
        return candidate, "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/"
    if "XC330" in candidate:
        return candidate, "https://emanual.robotis.com/docs/en/dxl/x/xc330-m288/"
    raise SystemExit(f"unsupported actuator family for {axis}: {candidate}")


def axis_component(model, by_axis, axis, bus_id, position):
    candidate, source = actuator_candidate(by_axis, axis)
    ref = "AX_" + axis
    if bus_id.startswith("RS-"):
        pins = [
            ("LOG-PWR", "BRANCH VDD", f"{bus_id}_VDD", "left"),
            ("LOG-RET", "BRANCH RETURN", f"{bus_id}_RET", "left"),
            ("LOG-DP", "RS-485 DATA+", f"{bus_id}_DP", "right"),
            ("LOG-DN", "RS-485 DATA-", f"{bus_id}_DN", "right"),
        ]
    else:
        pins = [
            ("LOG-PWR", "BRANCH VDD", f"{bus_id}_VDD", "left"),
            ("LOG-RET", "BRANCH RETURN", f"{bus_id}_RET", "left"),
            ("LOG-DATA", "TTL HALF-DUPLEX DATA", f"{bus_id}_DATA", "right"),
        ]
    return component(
        model, ref, candidate, pins,
        "Axis identity and protocol are allocated. Exact order code, actuator ID, physical connector pins, cable, branch current/protection and installed thermal/communication behavior remain selection and test work.",
        position, width=74.0, datasheet=source,
        evidence="Official ROBOTIS e-Manual interface family checked 2026-08-14; no physical robot pin map released.",
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
        "All terminal identifiers beginning LOG- are functional ports, not manufacturer connector or package pin numbers.",
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
                   ("LOG-AUDIO", "AUDIO / VISION IPC", "HMI_SENSOR_IPC", "right")],
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

    s12 = bus_sheet(model, 12, "12_head_ttl_sensors_hmi.kicad_sch", "Head TTL, sensing, display and audio", "TTL-HEAD", BUS_AXES["TTL-HEAD"], by_axis)
    s12.components.extend([
        component(model, "CAM1", "LEFT CAMERA MODULE - SELECTION REQUIRED", [("LOG-IPC", "VISION IPC", "HMI_SENSOR_IPC", "right")], "No safety role; exact module, optics, privacy and mounting remain open.", (153, 236), width=66.0),
        component(model, "CAM2", "RIGHT CAMERA MODULE - SELECTION REQUIRED", [("LOG-IPC", "VISION IPC", "HMI_SENSOR_IPC", "right")], "No safety role; exact module, optics, synchronization and mounting remain open.", (238, 236), width=66.0),
        component(model, "HMI1", "FACE DISPLAY / MICROPHONES / SPEAKERS - SELECTION REQUIRED", [("LOG-IPC", "HMI IPC", "HMI_SENSOR_IPC", "left")], "Exact screen, audio hardware, power, privacy indication and acoustic limits remain open.", (323, 236), width=72.0),
    ])
    sheets.append(s12)
    if len(sheets) != 12:
        raise SystemExit("controlled twelve-sheet architecture drift")
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
        "This is the native KiCad 10 whole-body architecture for the current 25-axis HR-30 candidate. It contains a root index plus twelve populated child sheets. Five RS-485 and three TTL actuator segments match the whole-body bus allocation exactly.\n\n"
        "All `LOG-*` terminal identifiers are functional ports, not physical connector or IC pin numbers. Exact devices, pins, order codes, fuse/limiter values, conductors, connectors, grounding, shield treatment, safety allocation, stopping time and physical behavior remain unresolved. The historical mixed HR-V0/HR-30 project is not incorporated as verified wiring.\n\n"
        "## Sheets\n\n" + "\n".join(f"{s.number}. `{s.filename}` — {s.title}" for s in sheets) + "\n\n"
        "KiCad ERC checks encoded passive-pin connectivity and annotation only. It grants no functional-safety credit and no authority to order, fabricate, connect, power, move or energize the robot.\n",
        encoding="utf-8", newline="\n")
    status = {
        "identifier": IDENTIFIER, "kicad_version": "10.0.5", "native_sheet_count": 13,
        "child_sheet_count": 12, "axis_binding_count": 25, "actuator_bus_segment_count": 8,
        "rs485_segment_count": 5, "ttl_segment_count": 3,
        "native_kicad_parsed": True, "erc_errors": 0, "erc_warnings": 0,
        "logical_connectivity_reconciled": True, "physical_pin_mapping_reconciled": False,
        "interface_devices_selected": False, "protection_values_selected": False,
        "functional_safety_validated": False, "connection_authority": False,
        "fabrication_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False, "warning": WARNING,
    }
    (ECAD / "electrical-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), ECAD / "native-kicad-source.py")


def update_package():
    status_path = PACKAGE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "native_hr30_kicad_present": True,
        "native_hr30_kicad_sheet_count": 13,
        "native_hr30_kicad_axis_binding_count": 25,
        "native_hr30_kicad_logical_connectivity_reconciled": True,
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
            row["unresolved_item"] = "A native 13-sheet HR-30 KiCad project now binds all 25 axes to five RS-485 and three TTL segments with zero ERC violations. Physical controller/interface devices and pins, connector/breakout hardware, protection values, termination/bias/level shifting, data-only harness isolation, grounding, EMC, timing/latency, safety allocation and physical fault tests remain open."
    with holds_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(holds[0]))
        writer.writeheader(); writer.writerows(holds)
    page_path = PACKAGE / "index.html"
    page = page_path.read_text(encoding="utf-8")
    start = "<!-- HR30-NATIVE-KICAD-P01-START -->"; end = "<!-- HR30-NATIVE-KICAD-P01-END -->"
    if start in page and end in page:
        page = page.split(start, 1)[0] + page.split(end, 1)[1]
    marker = '<section id="actuator-buses">'
    section = f'''{start}<section id="native-electrical"><h2>The whole robot now has native KiCad source</h2><div class="grid"><article class="card pass"><h3>13 native sheets</h3><p>One hierarchy page and twelve populated child sheets cover energy, interruption, compute/control, eight bus interfaces, every actuator, and head sensing/HMI.</p></article><article class="card pass"><h3>25 axes connected</h3><p>All nineteen RS-485 and six TTL actuator candidates appear in the native netlist on their assigned whole-body segments.</p></article><article class="card hold"><h3>ERC: 0 / 0</h3><p>KiCad 10 reports zero errors and zero warnings for encoded connectivity. ERC is not a physical, safety, or energization approval.</p></article><article class="card hold"><h3>Physical design remains open</h3><p>Exact interface devices, pins, connectors, protection, grounding, cable construction, EMC, and safety validation remain selection work.</p></article></div><div class="viewer"><object data="electrical/kicad/{PROJECT}/output/{PROJECT}.svg" type="image/svg+xml" aria-label="Interactive HR-30 native KiCad hierarchy diagram"></object><p>Open the hierarchy above, or download the <a href="electrical/kicad/{PROJECT}/{PROJECT}.kicad_pro">KiCad project</a>, <a href="electrical/kicad/{PROJECT}/connector-schedule.csv">terminal schedule</a>, <a href="electrical/kicad/{PROJECT}/net-schedule.csv">net schedule</a>, and <a href="electrical/kicad/{PROJECT}/validation/{PROJECT}-erc.rpt">complete ERC report</a>.</p></div></section>{end}'''
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
    print(json.dumps({"identifier": IDENTIFIER, "native_sheets": 13, "axes": 25, "segments": 8, "erc_errors": 0, "erc_warnings": 0, "physical_pin_mapping_reconciled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
