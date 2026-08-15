#!/usr/bin/env python3
"""Generate the HR-30 one-axis commissioning station P0.1.

This is support equipment derived from the authoritative 25-axis whole-body
design.  It intentionally powers only one disconnected actuator at a time from
a current-limited, safety-listed bench supply.  It is not the walking power
system and grants no authority to connect or energize hardware.
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

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "electrical" / "axis-commissioning-station-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1"
PROJECT = "hr30-axis-commissioning-station-p0.1"
IDENTIFIER = "HR30-AXIS-COMMISSIONING-STATION-P0.1"
DATE = "2026-08-15"
WARNING = "PRELIMINARY - SUPPORT EQUIPMENT CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
AUTHORITY = "NO CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY"
KICAD = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")

SOURCES = {
    "KEYSIGHT": ("Keysight", "E36313A", "5992-2124EN; live official data sheet accessed 2026-08-15", "https://www.keysight.com/us/en/assets/7018-05629/data-sheets/5992-2124.pdf"),
    "U2D2": ("ROBOTIS", "U2D2 / SKU 902-0132-000", "ROBOTIS Docs current page; accessed 2026-08-15", "https://docs.robotis.com/docs/parts/interface/u2d2/"),
    "PHB": ("ROBOTIS", "U2D2 Power Hub Board Set / SKU 902-0145-001", "ROBOTIS Docs current page; accessed 2026-08-15", "https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/"),
    "X4P": ("ROBOTIS", "Robot Cable-X4P 180 mm / SKU 903-0244-000", "live official product page; accessed 2026-08-15", "https://www.robotis.us/robot-cable-x4p-180mm-10pcs/"),
    "X3P": ("ROBOTIS", "Robot Cable-X3P 180 mm / SKU 903-0249-000", "live official product page; accessed 2026-08-15", "https://www.robotis.us/robot-cable-x3p-180mm-10pcs/"),
    "MOLEX": ("Molex", "39-01-2020 housing / 39-00-0038 contacts", "Mini-Fit Jr application-tooling specification accessed 2026-08-15", "https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63860/ATS-638601000-001.pdf"),
    "WIRE": ("Alpha Wire", "3073, 20 AWG stranded hook-up wire", "live official product page; accessed 2026-08-15", "https://www.alphawire.com/products/wire/hook-up-wire/premium/3073"),
    "BANANA": ("Pomona Electronics", "4933-2 red / 4933-0 black sheathed 4 mm plugs", "live official product family; accessed 2026-08-15", "https://www.pomonaelectronics.com/products/banana-plugs-jacks-and-hardware/banana-plugs-and-jacks"),
    "XH540": ("ROBOTIS", "XH540-W270-R", "ROBOTIS-GIT/emanual b0c64501f080d20088d044c65569f45279351ade; 2025-06-19; accessed 2026-08-15", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh540-w270/"),
    "XM540": ("ROBOTIS", "XM540-W270-R", "ROBOTIS-GIT/emanual b0c64501f080d20088d044c65569f45279351ade; 2025-06-19; accessed 2026-08-15", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm540-w270/"),
    "XM430": ("ROBOTIS", "XM430-W350-R", "ROBOTIS-GIT/emanual b0c64501f080d20088d044c65569f45279351ade; 2025-06-19; accessed 2026-08-15", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xm_series/xm430-w350/"),
    "XC330": ("ROBOTIS", "XC330-T288-T", "ROBOTIS-GIT/emanual 91f72d1ddd3f86d94d74b35ab037f7ec8c8c4dbe; 2026-01-27; accessed 2026-08-15", "https://docs.robotis.com/docs/dxl/model_reference/x_series/xc_series/xc330-t288/"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty register: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_model():
    source = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("hr30_commission_model", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("native KiCad model unavailable")
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    model.OUT = OUT
    model.PROJECT = PROJECT
    model.REV = "P0.1"
    model.DATE = DATE
    model.WARNING = WARNING
    model.PROJECT_TITLE = "PROJECT BUTTON HR-30 AXIS COMMISSIONING STATION P0.1"
    model.PROJECT_SUBTITLE = "One disconnected actuator; current-limited read-only first power; torque disabled."
    return model


def component(model, ref, value, pins, description, position, width=100, source="", evidence="", status="CANDIDATE / VALIDATION OPEN"):
    return model.Component(
        ref=ref,
        value=value,
        pins=[model.pn(ref, number, name, net, side) for number, name, net, side in pins],
        status=status,
        description=description,
        datasheet=source,
        evidence=evidence,
        position=position,
        width=width,
    )


def build_sheets(model):
    sheets = []
    s1 = model.Sheet(1, "01_current_limited_source.kicad_sch", "Safety-listed current-limited DC source", "E36313A output 2 or 3 used alone; output off while making connections.")
    s1.components = [
        component(model, "PS1", "KEYSIGHT E36313A OUTPUT 2 OR 3", [("+", "PROGRAMMABLE POSITIVE", "CL_POS", "right"), ("-", "PROGRAMMABLE RETURN", "CL_RET", "right"), ("PE", "CLASS I PROTECTIVE EARTH", "FACILITY_PE", "left")], "UL/CSA/IEC 61010-1 listed bench instrument. Candidate setting is 11.0 V with 0.25 A current limit for read-only first power; 25 V/2 A channel maximum is below the JST EH 3 A catalog boundary. Exact instrument calibration and qualified procedure approval remain open.", (115, 100), 115, SOURCES["KEYSIGHT"][3], SOURCES["KEYSIGHT"][2]),
        component(model, "P1", "POMONA 4933-2 / 4933-0 SHEATHED PLUG PAIR", [("RED", "SOURCE POSITIVE", "CL_POS", "left"), ("BLACK", "SOURCE RETURN", "CL_RET", "left"), ("RED-OUT", "20 AWG RED", "LEAD_POS", "right"), ("BLACK-OUT", "20 AWG BLACK", "LEAD_RET", "right")], "One metre bench lead candidate. No stacking, adapters or exposed clip ends. Polarity and insulation require 100% inspection.", (305, 100), 110, SOURCES["BANANA"][3], SOURCES["BANANA"][2]),
    ]
    s1.notes = ["Use one E36313A channel only. Output remains OFF until the complete point-to-point inspection is complete.", "This station is intentionally limited to one disconnected actuator. It must never feed a robot PDU, a bus chain, or multiple actuators."]
    sheets.append(s1)

    s2 = model.Sheet(2, "02_power_hub_and_usb.kicad_sch", "U2D2 and Power Hub boundary", "Only the Mini-Fit Jr power input is populated; every other PHB power inlet remains empty.")
    s2.components = [
        component(model, "J1", "MOLEX 39-01-2020 / 39-00-0038", [("1", "POWER RETURN", "LEAD_RET", "left"), ("2", "POWER POSITIVE", "LEAD_POS", "left")], "20 AWG Alpha 3073 red/black lead into the PHB Mini-Fit Jr input. Contact crimp height, pull test and received polarity remain validation work.", (90, 100), 100, SOURCES["MOLEX"][3], SOURCES["MOLEX"][2]),
        component(model, "PHB1", "ROBOTIS U2D2 POWER HUB 902-0145-001", [("P1", "MINI-FIT RETURN", "LEAD_RET", "left"), ("P2", "MINI-FIT POSITIVE", "LEAD_POS", "left"), ("G3", "TTL GND", "DUT_GND", "right"), ("V3", "TTL VDD", "DUT_VDD", "right"), ("D3", "TTL DATA", "TTL_DATA", "right"), ("G4", "RS485 GND", "DUT_GND", "right"), ("V4", "RS485 VDD", "DUT_VDD", "right"), ("D+", "RS485 DATA+", "RS485_DP", "right"), ("D-", "RS485 DATA-", "RS485_DN", "right")], "Manufacturer maximum is 10 A, but this station is source-limited to 0.25 A for first power and 2.0 A absolute equipment configuration maximum. The barrel and screw-terminal inputs must remain physically empty.", (235, 125), 116, SOURCES["PHB"][3], SOURCES["PHB"][2]),
        component(model, "U1", "ROBOTIS U2D2 902-0132-000", [("USB", "USB-C OR RECEIVED REVISION", "HOST_USB", "left"), ("TTL", "TTL DATA", "TTL_DATA", "right"), ("D+", "RS485 DATA+", "RS485_DP", "right"), ("D-", "RS485 DATA-", "RS485_DN", "right")], "U2D2 supplies communication only. Confirm received USB revision; units changed from Micro-B to USB-C in August 2025. Keep the internal 120 ohm switch OFF for the one-actuator first-power setup unless a qualified waveform test directs otherwise.", (395, 125), 110, SOURCES["U2D2"][3], SOURCES["U2D2"][2]),
    ]
    s2.notes = ["ROBOTIS prohibits using more than one PHB power input at once.", "Do not connect or disconnect a DYNAMIXEL cable while PHB power is on."]
    sheets.append(s2)

    s3 = model.Sheet(3, "03_one_actuator_selection.kicad_sch", "One-actuator cable selection", "Fit exactly one X3P or X4P cable; the other output remains empty.")
    s3.components = [
        component(model, "X4", "ROBOTIS X4P 180 MM 903-0244-000", [("1", "GND", "DUT_GND", "left"), ("2", "VDD", "DUT_VDD", "left"), ("3", "DATA+", "RS485_DP", "left"), ("4", "DATA-", "RS485_DN", "left"), ("DUT", "ONE RS485 ACTUATOR", "DUT_RS485", "right")], "For XH540-R, XM540-R or XM430-R only. One actuator is physically disconnected from the whole-body harness before connection.", (135, 95), 112, SOURCES["X4P"][3], SOURCES["X4P"][2]),
        component(model, "X3", "ROBOTIS X3P 180 MM 903-0249-000", [("1", "GND", "DUT_GND", "left"), ("2", "VDD", "DUT_VDD", "left"), ("3", "DATA", "TTL_DATA", "left"), ("DUT", "ONE TTL ACTUATOR", "DUT_TTL", "right")], "For XC330-T only. One actuator is physically disconnected from the whole-body harness before connection.", (335, 95), 112, SOURCES["X3P"][3], SOURCES["X3P"][2]),
    ]
    s3.notes = ["X3P and X4P are mutually exclusive station configurations; never populate both DUT cables during commissioning.", "The standard ROBOTIS cable is acceptable here because only one actuator is powered. It is not approval for whole-body power daisy chaining."]
    sheets.append(s3)

    s4 = model.Sheet(4, "04_no_motion_boundary.kicad_sch", "Read-only no-motion boundary", "First energization reads identity and telemetry with Torque Enable held at zero.")
    s4.components = [
        component(model, "HOST1", "QUALIFIED HOST / DYNAMIXEL WIZARD 2.0", [("USB", "USB TO U2D2", "HOST_USB", "right"), ("TORQUE", "TORQUE ENABLE MUST READ 0", "TORQUE_ZERO", "right"), ("READ", "PING / MODEL / VOLTAGE / TEMPERATURE / ERROR", "READ_ONLY_REQUEST", "right")], "No goal position, velocity, current, PWM, reboot, factory reset or firmware update command is allowed in the first-power stage.", (130, 110), 118),
        component(model, "DUT1", "ONE DISCONNECTED HR-30 ACTUATOR", [("RS", "RS485 FAMILY INPUT", "DUT_RS485", "left"), ("TTL", "TTL FAMILY INPUT", "DUT_TTL", "left"), ("T0", "TORQUE ENABLE = 0", "TORQUE_ZERO", "left"), ("READ", "READ-ONLY TELEMETRY", "READ_ONLY_REQUEST", "left")], "Actuator output hardware is mechanically supported and cannot drive a body link during first power. Proposed ID assignment is a later separately authorized configuration step.", (350, 110), 118),
    ]
    s4.notes = ["Power-up defaults are not accepted as proof. The operator must read back Torque Enable = 0 before any other write.", "Any unexpected motion, current-limit state, odor, smoke, noise, temperature rise, communication ambiguity or identity mismatch requires immediate output-off and investigation."]
    sheets.append(s4)
    return sheets


def write_ecad(sheets, model):
    root_uuid = model.uid("hr30-axis-commissioning-root")
    counts = Counter(pin.net for sheet in sheets for item in sheet.components for pin in item.pins)
    wires = model.build_wire_numbers(sheets, counts)
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, sheets), encoding="utf-8")
    for sheet in sheets:
        (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wires), encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps({"board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {}, "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {}, "text_variables": {"PROJECT_STATUS": WARNING}}, indent=2) + "\n", encoding="utf-8")
    components = [item for sheet in sheets for item in sheet.components]
    symbols = [model.lib_symbol(item).replace(f'(symbol "PBV3:{item.ref}"', f'(symbol "{item.ref}"', 1) for item in components]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-30 axis commissioning symbols"))\n)\n', encoding="utf-8")
    model.write_tables(sheets, counts, wires)
    validation, output = OUT / "validation", OUT / "output"
    validation.mkdir(exist_ok=True)
    output.mkdir(exist_ok=True)
    commands = [
        [str(KICAD), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(OUT / f"{PROJECT}.kicad_sch")],
        [str(KICAD), "sch", "export", "svg", "--output", str(output), str(OUT / f"{PROJECT}.kicad_sch")],
    ]
    log = []
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        log.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
            raise SystemExit(result.returncode)
    (validation / "kicad-cli.log").write_text("\n".join(log), encoding="utf-8")
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", svg.read_bytes()))
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def rounded_box(x, y, z, p=(0, 0, 0), r=2):
    return cq.Workplane("XY").box(x, y, z).edges("|Z").fillet(min(r, x / 4, y / 4)).translate(p).val()


def write_cad():
    # A universal nonconductive tray: slots accept hook-and-loop straps, so no
    # unverified PHB mounting-hole pattern is fabricated into the part.
    base = cq.Workplane("XY").box(190, 120, 5).edges("|Z").fillet(5)
    for x in (-70, -25, 25, 70):
        for y in (-42, 42):
            base = base.cut(cq.Workplane("XY").box(18, 4, 8).translate((x, y, 0)))
    wall = cq.Workplane("XY").rect(190, 120).rect(180, 110).extrude(28).translate((0, 0, 2.5))
    wall = wall.cut(cq.Workplane("XZ").box(34, 10, 18).translate((0, -58, 17)))
    tray = base.union(wall).val()
    lid = cq.Workplane("XY").box(190, 120, 3).edges("|Z").fillet(5).translate((0, 0, 34)).val()
    phb_clearance = rounded_box(90, 65, 18, (5, 0, 13), 3)
    u2d2 = rounded_box(48, 18, 14.9, (-45, 0, 16), 2)
    lead = cq.Workplane("XY").cylinder(5, 3).translate((72, -40, 10)).val()
    assy = cq.Assembly(name="HR30_AXIS_COMMISSIONING_STATION_P01_NOT_RELEASED")
    assy.add(tray, name="PRINTED_UNIVERSAL_TRAY", color=cq.Color(0.10, 0.30, 0.58, 1))
    assy.add(lid, name="TRANSPARENT_COVER_CANDIDATE", color=cq.Color(0.65, 0.88, 1.0, 0.35))
    assy.add(phb_clearance, name="PHB_CLEARANCE_ENVELOPE_RECEIPT_MEASURE", color=cq.Color(0.20, 0.70, 0.35, 1))
    assy.add(u2d2, name="U2D2_48x18x14p9", color=cq.Color(0.95, 0.72, 0.08, 1))
    assy.add(lead, name="SINGLE_MINIFIT_POWER_INPUT", color=cq.Color(0.82, 0.12, 0.10, 1))
    step_path = OUT / "HR30_axis_commissioning_station_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound([tray, lid, phb_clearance, u2d2, lead]), str(step_path))
    # OpenCascade emits harmless trailing spaces in STEP text records. Normalize
    # them so the versioned engineering export passes repository whitespace checks.
    step_path.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", step_path.read_bytes()))
    assy.save(str(OUT / "HR30_axis_commissioning_station_candidate.glb"))
    cq.exporters.export(tray, str(OUT / "HR30_axis_commissioning_tray_candidate.stl"), tolerance=0.1)
    cq.exporters.export(lid, str(OUT / "HR30_axis_commissioning_cover_candidate.stl"), tolerance=0.1)


def axis_rows():
    axes = read_csv(WB / "actuator-bus-axis-binding.csv")
    result = []
    for proposed_id, axis in enumerate(axes, 1):
        family = axis["actuator_family"]
        is_rs = axis["protocol"].startswith("RS-485")
        result.append({
            "sequence": proposed_id,
            "axis_id": axis["axis_id"],
            "region": axis["region"],
            "candidate_actuator": axis["candidate_actuator"],
            "family": family,
            "protocol": axis["protocol"],
            "station_cable": "X4P 180 mm / 903-0244-000" if is_rs else "X3P 180 mm / 903-0249-000",
            "proposed_global_id": proposed_id,
            "initial_voltage_v": "11.0",
            "initial_current_limit_a": "0.25",
            "required_initial_readback": "model number; firmware; present voltage; present temperature; hardware error; Torque Enable=0",
            "first_power_motion_command": "PROHIBITED",
            "execution_result": "NOT EXECUTED",
            "authority": AUTHORITY,
        })
    return result


def write_registers():
    write_csv(OUT / "primary-source-register.csv", [
        {"source_id": key, "manufacturer": value[0], "candidate": value[1], "document_revision_or_date": value[2], "accessed": DATE, "official_url": value[3], "verified_scope": {
            "KEYSIGHT": "E36313A; two 25 V / 2 A outputs; UL 61010-1, CAN/CSA-C22.2 61010-1-12 and IEC 61010-1:2010",
            "U2D2": "48 x 18 x 14.9 mm; USB communication only; TTL and RS-485; no actuator power; optional 120 ohm termination",
            "PHB": "3.5-24 V; 10 A maximum; only one power input at a time; Mini-Fit power pin 1 GND / pin 2 VDD",
            "X4P": "RS-485 X-series JST-JST 180 mm stocked cable family",
            "X3P": "TTL X-series JST-JST 180 mm stocked cable family",
            "MOLEX": "39-01-2020 housing and 39-00-0038 contact; 20 AWG PHB manufacturer interface",
            "WIRE": "3073 stranded 20 AWG tinned copper; UL AWM 1015/1230; 105 C; 600 V; VW-1",
            "BANANA": "4933 sheathed 4 mm plug family for 18/20/22 AWG wire",
            "XH540": "10.0-14.8 V operating range; 12 V recommended; RS-485 interface",
            "XM540": "10.0-14.8 V operating range; 12 V recommended; RS-485 interface",
            "XM430": "10.0-14.8 V operating range; 12 V recommended; RS-485 interface",
            "XC330": "6.5-12.0 V operating range; 11.1 V recommended; TTL interface",
        }[key], "application_boundary": "PHYSICAL ASSEMBLY, CALIBRATION AND QUALIFIED PROCEDURE APPROVAL OPEN", "warning": WARNING}
        for key, value in SOURCES.items()
    ])
    write_csv(OUT / "candidate-bom.csv", [
        {"item": "CS-01", "quantity": 1, "manufacturer": "Keysight", "order_code": "E36313A", "description": "triple-output bench supply; use output 2 or 3 only", "disposition": "EVALUATION CANDIDATE; CHECK MAKERSPACE AVAILABILITY", "authority": AUTHORITY},
        {"item": "CS-02", "quantity": 1, "manufacturer": "ROBOTIS", "order_code": "902-0132-000", "description": "U2D2 USB interface; received USB revision inspection required", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-03", "quantity": 1, "manufacturer": "ROBOTIS", "order_code": "902-0145-001", "description": "U2D2 Power Hub Board Set", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-04", "quantity": 1, "manufacturer": "ROBOTIS", "order_code": "903-0244-000", "description": "X4P 180 mm cable; package contains 10", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-05", "quantity": 1, "manufacturer": "ROBOTIS", "order_code": "903-0249-000", "description": "X3P 180 mm cable; package contains 10", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-06", "quantity": 1, "manufacturer": "Molex", "order_code": "39-01-2020", "description": "two-circuit Mini-Fit Jr receptacle housing", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-07", "quantity": 2, "manufacturer": "Molex", "order_code": "39-00-0038", "description": "female Mini-Fit Jr crimp contact for 20 AWG lead", "disposition": "CANDIDATE; CRIMP VALIDATION OPEN", "authority": AUTHORITY},
        {"item": "CS-08", "quantity": 1, "manufacturer": "Alpha Wire", "order_code": "3073 RED", "description": "20 AWG red lead, 1.0 m first-cut candidate", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-09", "quantity": 1, "manufacturer": "Alpha Wire", "order_code": "3073 BLACK", "description": "20 AWG black lead, 1.0 m first-cut candidate", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-10", "quantity": 1, "manufacturer": "Pomona", "order_code": "4933-2", "description": "red sheathed 4 mm banana plug", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-11", "quantity": 1, "manufacturer": "Pomona", "order_code": "4933-0", "description": "black sheathed 4 mm banana plug", "disposition": "CANDIDATE", "authority": AUTHORITY},
        {"item": "CS-12", "quantity": 1, "manufacturer": "PROJECT BUTTON", "order_code": "PRINT FROM INCLUDED STL", "description": "universal insulated tray and transparent cover", "disposition": "FABRICATION CANDIDATE; RECEIPT FIT CHECK OPEN", "authority": AUTHORITY},
    ])
    write_csv(OUT / "connector-contact-map.csv", [
        {"connector": "PS1-BANANA", "contact": "RED", "function": "+11.0 V candidate", "wire": "Alpha 3073 red 20 AWG", "destination": "J1/2", "inspection": "polarity and shrouding 100%", "state": "NOT EXECUTED"},
        {"connector": "PS1-BANANA", "contact": "BLACK", "function": "DC return", "wire": "Alpha 3073 black 20 AWG", "destination": "J1/1", "inspection": "polarity and shrouding 100%", "state": "NOT EXECUTED"},
        {"connector": "J1 MINI-FIT", "contact": "1", "function": "GND", "wire": "Alpha 3073 black 20 AWG", "destination": "PHB power pin 1", "inspection": "continuity and pull test", "state": "NOT EXECUTED"},
        {"connector": "J1 MINI-FIT", "contact": "2", "function": "VDD", "wire": "Alpha 3073 red 20 AWG", "destination": "PHB power pin 2", "inspection": "continuity and pull test", "state": "NOT EXECUTED"},
        {"connector": "X4P", "contact": "1/2/3/4", "function": "GND/VDD/DATA+/DATA-", "wire": "ROBOTIS 903-0244-000", "destination": "one RS-485 actuator", "inspection": "manufacturer cable; polarity/continuity before use", "state": "NOT EXECUTED"},
        {"connector": "X3P", "contact": "1/2/3", "function": "GND/VDD/DATA", "wire": "ROBOTIS 903-0249-000", "destination": "one TTL actuator", "inspection": "manufacturer cable; polarity/continuity before use", "state": "NOT EXECUTED"},
    ])
    write_csv(OUT / "axis-commissioning-matrix.csv", axis_rows())
    write_csv(OUT / "controlled-settings.csv", [
        {"stage": "S0", "setting": "supply output", "value": "OFF", "reason": "all connections and inspection occur de-energized", "release_state": "CANDIDATE PROCEDURE / NOT EXECUTED"},
        {"stage": "S1", "setting": "voltage", "value": "11.0 V", "reason": "inside all four candidate actuator input ranges; below 12 V nominal", "release_state": "QUALIFIED APPROVAL AND CALIBRATED MEASUREMENT REQUIRED"},
        {"stage": "S1", "setting": "current limit", "value": "0.25 A", "reason": "low-energy identity/telemetry discovery only; no motion", "release_state": "QUALIFIED APPROVAL AND PHYSICAL TEST REQUIRED"},
        {"stage": "S1", "setting": "over-voltage protection", "value": "12.0 V candidate", "reason": "detects gross setup error; exact trip behavior/calibration open", "release_state": "QUALIFIED APPROVAL REQUIRED"},
        {"stage": "S1", "setting": "PHB power inputs", "value": "Mini-Fit only", "reason": "ROBOTIS prohibits simultaneous power inputs", "release_state": "MANDATORY"},
        {"stage": "S1", "setting": "actuator population", "value": "exactly one", "reason": "prevents ID collisions and bounds source energy", "release_state": "MANDATORY"},
        {"stage": "S1", "setting": "Torque Enable", "value": "0 readback", "reason": "first power permits no motion", "release_state": "MANDATORY"},
        {"stage": "S2", "setting": "proposed ID write", "value": "matrix value 1-25", "reason": "global uniqueness; separately authorized after read-only S1 passes", "release_state": "NOT PART OF FIRST ENERGIZATION"},
    ])
    steps = [
        ("P01", "before hardware", "qualified electrical reviewer approves the station drawing, instrument choice, limits, test location and restraint", "signed approval", "STOP if absent"),
        ("P02", "de-energized", "inspect received U2D2/PHB revision, supplied standoffs, connectors, cables, lead crimps and tray fit", "100% visual/record", "STOP on mismatch"),
        ("P03", "de-energized", "verify Mini-Fit pin 1 to black/negative and pin 2 to red/positive; verify no shorts", "continuity record", "STOP on failure"),
        ("P04", "de-energized", "disconnect one named actuator from every whole-body power/data connector and mechanically support its output", "axis signoff", "STOP if coupled to a load"),
        ("P05", "de-energized", "fit exactly one matching X3P or X4P cable; keep the unused DUT port and both unused PHB power inlets empty", "photo/check", "STOP if ambiguous"),
        ("P06", "output off", "configure calibrated supply to candidate 11.0 V, 0.25 A current limit and candidate 12.0 V OVP", "independent readback", "STOP if configuration cannot be locked"),
        ("P07", "output off", "connect USB; discover only the expected protocol with no broadcast write and no torque/motion command", "host log started", "STOP on multiple devices"),
        ("P08", "first power", "turn PHB switch on, then enable supply output; keep a hand on output-off control", "current/voltage trace", "output off immediately on any anomaly"),
        ("P09", "read only", "ping and read model, firmware, present voltage, temperature, hardware error and Torque Enable", "saved readback", "PASS only if Torque Enable=0 and identity matches"),
        ("P10", "shutdown", "disable supply output, switch PHB off, wait for voltage to decay, disconnect DUT, label record", "zero-voltage verification", "do not unplug under power"),
        ("P11", "later stage", "assign proposed global ID only under a separately signed configuration procedure", "write/readback audit", "not first-energization authority"),
    ]
    write_csv(OUT / "first-power-procedure.csv", [{"step": a, "state": b, "action": c, "required_record": d, "fail_closed_rule": e, "execution": "NOT EXECUTED", "authority": AUTHORITY} for a, b, c, d, e in steps])
    write_csv(OUT / "fixture-part-register.csv", [
        {"part": "CS-TRAY", "dimensions_mm": "190 x 120 x 33 overall", "material": "electrically insulating FDM material selection required", "manufacturing_file": "HR30_axis_commissioning_tray_candidate.stl", "interface": "eight 18 x 4 mm strap slots; no inferred PHB hole pattern", "state": "CANDIDATE / PRINT SETTINGS AND RECEIPT FIT OPEN"},
        {"part": "CS-COVER", "dimensions_mm": "190 x 120 x 3", "material": "transparent insulating cover candidate", "manufacturing_file": "HR30_axis_commissioning_cover_candidate.stl", "interface": "removable cover; retention method selection required", "state": "CANDIDATE / RETENTION AND ACCESS OPEN"},
    ])
    holds = [
        ("CS-H01", "qualified electrical approval of the complete station and first-power procedure"),
        ("CS-H02", "availability/calibration record for exact E36313A or a formally re-reviewed equivalent"),
        ("CS-H03", "received U2D2 USB revision, PHB dimensions, supplied standoffs and connector inspection"),
        ("CS-H04", "Mini-Fit crimp tooling, crimp-height specification, pull test and polarity inspection"),
        ("CS-H05", "tray/cover material, print settings, cover retention, labeling and received fit check"),
        ("CS-H06", "mechanical restraint that prevents each installed actuator output from driving a body link"),
        ("CS-H07", "approved host software/version and logging method that prevents broadcast or motion writes"),
        ("CS-H08", "executed records for all 25 axes; proposed IDs remain unwritten until separately authorized"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": h, "unresolved_evidence": text, "state": "OPEN", "authority": AUTHORITY} for h, text in holds])


def write_docs(sheets):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 720" role="img" aria-labelledby="t d"><title id="t">HR-30 one-axis commissioning station</title><desc id="d">A safety-listed current-limited bench supply feeds one U2D2 Power Hub and exactly one disconnected DYNAMIXEL actuator. First power is read only and torque remains disabled.</desc><style>text{{font-family:system-ui,sans-serif;fill:#082f58}}.box{{fill:white;stroke:#14689c;stroke-width:4}}.safe{{fill:#d6f1ff}}.gold{{fill:#fff0b5}}.line{{stroke:#14689c;stroke-width:7;fill:none;marker-end:url(#a)}}.h{{font-size:28px;font-weight:800}}.b{{font-size:19px}}.s{{font-size:14px}}</style><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L9 3L0 6z" fill="#14689c"/></marker></defs><rect width="1500" height="720" fill="#f8fcff"/><text x="40" y="45" class="h">{WARNING}</text><rect class="box safe" x="55" y="110" width="300" height="180" rx="20"/><text x="85" y="155" class="h">Keysight E36313A</text><text x="85" y="195" class="b">Output 2 or 3 only</text><text x="85" y="230" class="b">11.0 V · 0.25 A first power</text><text x="85" y="265" class="s">UL / CSA / IEC 61010-1</text><path class="line" d="M355 200H505"/><rect class="box gold" x="520" y="90" width="390" height="230" rx="20"/><text x="550" y="140" class="h">U2D2 + Power Hub</text><text x="550" y="185" class="b">Mini-Fit input only</text><text x="550" y="220" class="b">Barrel and screw input EMPTY</text><text x="550" y="255" class="b">One X3P or X4P DUT cable</text><path class="line" d="M910 200H1060"/><rect class="box" x="1075" y="110" width="360" height="180" rx="20"/><text x="1105" y="155" class="h">ONE actuator</text><text x="1105" y="195" class="b">Disconnected from robot harness</text><text x="1105" y="230" class="b">Output mechanically restrained</text><text x="1105" y="265" class="b">Torque Enable = 0</text><rect class="box" x="320" y="410" width="860" height="220" rx="24"/><text x="365" y="462" class="h">First power permits reads—not motion.</text><text x="365" y="510" class="b">Read: model · firmware · voltage · temperature · hardware error · Torque Enable</text><text x="365" y="555" class="b">Never send: goal position · velocity · current · PWM · reboot · reset · firmware update</text><text x="365" y="600" class="b">Any anomaly → supply output OFF → PHB OFF → investigate</text></svg>'''
    (OUT / "station-architecture.svg").write_text(svg, encoding="utf-8")
    panels = "".join(f'<details><summary>{sheet.number:02d} · {html.escape(sheet.title)}</summary><div class="drawing"><object data="output/{Path(sheet.filename).stem}.svg" type="image/svg+xml" aria-label="{html.escape(sheet.title)}"></object></div></details>' for sheet in sheets)
    axis = axis_rows()
    rows = "".join(f'<tr><td>{a["sequence"]}</td><td>{html.escape(a["axis_id"])}</td><td>{html.escape(a["family"])}</td><td>{html.escape(a["station_cable"])}</td><td>{a["proposed_global_id"]}</td></tr>' for a in axis)
    (OUT / "index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 axis commissioning station</title><script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script><style>:root{{--navy:#082f58;--blue:#14689c;--sky:#d6f1ff;--gold:#f2b928;--paper:#f8fcff}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold);padding:clamp(1.5rem,5vw,4rem)}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(2.3rem,6vw,5rem);line-height:1.03;max-width:18ch}}h2{{font-size:clamp(1.7rem,3vw,2.8rem)}}main{{padding:2rem clamp(1rem,4vw,3rem) 5rem}}.warning,.hold{{border:3px solid #a86f00;background:#fff0b5;border-radius:14px;padding:1rem;font-weight:850}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:1rem;margin:2rem 0}}article,details,.panel{{background:white;border:2px solid var(--blue);border-radius:16px;padding:1rem}}article b{{display:block;font-size:clamp(2rem,4vw,3.5rem)}}model-viewer{{width:100%;height:480px;background:white;border:2px solid #8bc5e5}}summary{{font-size:18px;font-weight:850;cursor:pointer}}.drawing{{height:620px;overflow:auto}}object{{width:100%;height:100%;min-width:900px}}.tablewrap{{overflow:auto;border:2px solid var(--blue);border-radius:16px}}table{{border-collapse:collapse;width:100%;min-width:800px;background:white}}th,td{{padding:.8rem;text-align:left;border-bottom:1px solid #c7dfec;font-size:14px}}th{{background:var(--navy);color:white}}a{{color:#075d98;font-weight:800}}@media(max-width:650px){{main{{padding:1.2rem .8rem 4rem}}model-viewer{{height:390px}}}}</style></head><body><header><div><p class="warning">{WARNING}</p><h1>First power, one actuator at a time.</h1><p>The complete HR-30 remains the program deliverable. This removable station bounds the first electrical inspection to one disconnected actuator, a 0.25 A source limit, and read-only telemetry.</p></div></header><main><section class="grid"><article><b>25</b>whole-body axes in the matrix</article><article><b>1</b>actuator physically connected</article><article><b>0.25 A</b>candidate first-power limit</article><article><b>ERC 0/0</b>native four-sheet design</article></section><div class="hold"><h2>This does not authorize energization</h2><p>A qualified reviewer must approve the received hardware, calibrated limits, restraint, host configuration and signed procedure. First power permits no torque or motion command.</p></div><h2>Wiring architecture</h2><object data="station-architecture.svg" type="image/svg+xml" style="width:100%;min-height:520px" aria-label="One-axis current-limited commissioning architecture"></object><h2>Printable station fixture</h2><model-viewer src="HR30_axis_commissioning_station_candidate.glb" camera-controls shadow-intensity="0.9" alt="Interactive U2D2 and Power Hub commissioning tray"></model-viewer><p><a href="HR30_axis_commissioning_station_candidate.step">station STEP</a> · <a href="HR30_axis_commissioning_tray_candidate.stl">tray STL</a> · <a href="HR30_axis_commissioning_cover_candidate.stl">cover STL</a> · <a href="{PROJECT}.kicad_pro">native KiCad</a></p><h2>Twenty-five-axis work order</h2><div class="tablewrap"><table><thead><tr><th>Seq.</th><th>Axis</th><th>Family</th><th>Station cable</th><th>Proposed ID</th></tr></thead><tbody>{rows}</tbody></table></div><p><a href="axis-commissioning-matrix.csv">Download the complete matrix</a> · <a href="first-power-procedure.csv">first-power procedure</a> · <a href="candidate-bom.csv">candidate BOM</a> · <a href="open-holds.csv">open holds</a></p><h2>Editable schematic sheets</h2>{panels}</main></body></html>''', encoding="utf-8")
    (OUT / "README.md").write_text(f"# HR-30 axis commissioning station P0.1\n\n**{WARNING}**\n\nThis support-equipment package gives the complete 25-axis HR-30 a controlled path to first electrical inspection without using the unreleased walking-power system. A Keysight E36313A candidate supplies one U2D2 Power Hub through one Mini-Fit input; exactly one disconnected actuator is attached with the matching ROBOTIS X3P or X4P cable. Candidate first power is 11.0 V with a 0.25 A current limit, read-only telemetry and Torque Enable read back as zero. Qualified approval, calibrated received hardware, restraint, executed inspection and a separately signed test authorization remain mandatory.\n", encoding="utf-8")


def integrate():
    status_path = WB / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "axis_commissioning_station_present": True,
        "axis_commissioning_native_sheet_count": 5,
        "axis_commissioning_axis_count": 25,
        "axis_commissioning_one_actuator_limit": True,
        "axis_commissioning_first_power_current_limit_candidate_a": 0.25,
        "axis_commissioning_no_motion_boundary_present": True,
        "axis_commissioning_proposed_global_id_count": 25,
        "axis_commissioning_physically_validated": False,
        "axis_commissioning_connection_authority": False,
        "axis_commissioning_energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    marker_a, marker_b = "<!-- HR30-AXIS-COMMISSION-START -->", "<!-- HR30-AXIS-COMMISSION-END -->"
    page = WB / "index.html"
    text = re.sub(re.escape(marker_a) + r"[\s\S]*?" + re.escape(marker_b), "", page.read_text(encoding="utf-8"))
    block = f'''{marker_a}<section id="axis-commissioning"><h2>One-axis first-power station</h2><div class="grid"><article class="card pass"><h3>25-axis work order</h3><p>Every whole-body actuator has a cable selection, proposed global ID and read-only commissioning row.</p></article><article class="card pass"><h3>0.25 A candidate limit</h3><p>One disconnected actuator at 11.0 V; torque and motion commands are prohibited.</p></article><article class="card hold"><h3>Qualified approval still required</h3><p>The station is not permission to connect or energize hardware.</p></article></div><div class="viewer"><object data="electrical/axis-commissioning-station-p0.1/station-architecture.svg" type="image/svg+xml" aria-label="HR-30 current-limited one-axis commissioning station"></object><p><a href="electrical/axis-commissioning-station-p0.1/index.html">Open the interactive commissioning guide</a> · <a href="electrical/axis-commissioning-station-p0.1/{PROJECT}.kicad_pro">native KiCad</a> · <a href="electrical/axis-commissioning-station-p0.1/axis-commissioning-matrix.csv">25-axis matrix</a>.</p></div></section>{marker_b}'''
    page.write_text(text.replace("</main>", block + "</main>"), encoding="utf-8")
    readme = WB / "README.md"
    text = re.sub(re.escape(marker_a) + r"[\s\S]*?" + re.escape(marker_b), "", readme.read_text(encoding="utf-8")).rstrip()
    text += f"\n\n{marker_a}\n## One-axis first-power station\n\nThe whole-body package now includes a removable, source-limited commissioning station rather than relying on the unreleased walking-power tree for first inspection. It uses a safety-listed Keysight E36313A candidate, ROBOTIS U2D2/Power Hub, exact X3P/X4P cable families, a native four-child-sheet KiCad design, printable tray/cover files and a 25-axis work order. Candidate first power is one mechanically restrained, whole-body-disconnected actuator at 11.0 V / 0.25 A with read-only telemetry and Torque Enable required to read zero. Qualified review, received-hardware inspection, calibration, restraint and separately signed connection/energization authority remain open. See `electrical/axis-commissioning-station-p0.1/index.html`.\n{marker_b}\n"
    readme.write_text(text, encoding="utf-8")


def sync_release_and_manifest():
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)
    release_root = ROOT / "release" / "hr30" / "whole-body-p0.1"
    for name in ("README.md", "index.html", "package-status.json"):
        shutil.copy2(WB / name, release_root / name)
    root_manifest = WB / "file-manifest.csv"
    files = sorted(p for p in WB.rglob("*") if p.is_file() and p != root_manifest)
    write_csv(root_manifest, [{"path": p.relative_to(WB).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"} for p in files])
    shutil.copy2(root_manifest, release_root / "file-manifest.csv")


def main() -> int:
    if not KICAD.exists():
        raise RuntimeError("KiCad 10 CLI is required")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    model = load_model()
    sheets = build_sheets(model)
    write_ecad(sheets, model)
    write_cad()
    write_registers()
    write_docs(sheets)
    integrate()
    shutil.copy2(Path(__file__), OUT / "commissioning-station-source.py")
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "native_sheet_count": 5,
        "child_sheet_count": 4,
        "erc_errors": 0,
        "erc_warnings": 0,
        "axis_count": 25,
        "simultaneous_actuator_limit": 1,
        "candidate_first_power_voltage_v": 11.0,
        "candidate_first_power_current_limit_a": 0.25,
        "absolute_station_configuration_current_a": 2.0,
        "torque_or_motion_command_permitted": False,
        "whole_body_power_role": "REJECT",
        "walking_power_role": "REJECT",
        "physical_validation_complete": False,
        "qualified_procedure_approved": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    }
    (OUT / "commissioning-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    write_csv(OUT / "file-manifest.csv", [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in files])
    sync_release_and_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
