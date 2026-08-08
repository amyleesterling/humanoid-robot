#!/usr/bin/env python3
"""Generate the native KiCad HR-V0 gripper ordinary-control candidate."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical/kicad/hr-v0-gripper-interface"
PROJECT = "hr-v0-gripper-interface"
REV = "HR-V0-GRIP-ELEC-P0.1"
WARNING = "PRELIMINARY - ORDINARY CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
KICAD_ROOT = Path(r"C:\Program Files\KiCad\10.0")


def load_model():
    path = ROOT / "tools/generate_hr_v0_electrical_v3.py"
    spec = importlib.util.spec_from_file_location("gripper_schematic_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load schematic model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.PROJECT = PROJECT
    module.REV = REV
    module.PROJECT_TITLE = "PROJECT BUTTON HR-V0 GRIPPER ORDINARY-CONTROL CANDIDATE"
    module.PROJECT_SUBTITLE = "Logical terminals only; physical connectors, pads, protection and settings remain SELECTION REQUIRED. ZERO SAFETY CREDIT."
    return module


def components(model):
    pn, Component = model.pn, model.Component
    common = "Logical terminal identifiers are not connector pin numbers or pad positions. Physical implementation is SELECTION REQUIRED."
    return [
        Component("JGIN1", "POST-K1/K2 branch - SELECTION REQUIRED", [pn("JGIN1","PWR","POST-K1/K2 +24 V","POST_K1_K2_24V","right"), pn("JGIN1","RTN","0 V return","GRIP_0V","right")], "INTERFACE SELECTION REQUIRED", common, "Project Button Electrical V3-P1.13", "Actuator-power removal boundary only; connector and conductors not released.", position=(35,55), width=30),
        Component("FGRIP1", "BRANCH PROTECTION - SELECTION REQUIRED", [pn("FGRIP1","IN","SOURCE","POST_K1_K2_24V","left"), pn("FGRIP1","OUT","PROTECTED","GRIP_24V_PROTECTED","right")], "VALUE/MPN SELECTION REQUIRED", "Fault current, cable, inrush, regulator behavior, ambient, bundling, connector limits and jurisdiction required.", "No manufacturer selected", "No value or order code released.", position=(122.5,55), width=35),
        Component("DCGRIP1", "Pololu D24V22F6 item 2859 - PREFERRED EVALUATION CANDIDATE", [pn("DCGRIP1","VIN","VIN","GRIP_24V_PROTECTED","left"), pn("DCGRIP1","GND","GND","GRIP_0V","left"), pn("DCGRIP1","VOUT","6 V OUT","GRIP_6V","right"), pn("DCGRIP1","PG","POWER GOOD","GRIP_PG_SENSE","right"), pn("DCGRIP1","EN","ENABLE - NO EXTERNAL CONNECTION","NC_DCGRIP_EN","right")], "NOT SELECTED", "EN is represented by an isolated logical stub and shall have no external connection in this candidate. Carrier, terminals, thermal/noise/inrush/capacitance and protection remain open.", "https://www.pololu.com/product/2859", "Product page current 2026; dimension drawing 12 November 2015. Typical current is not a released Project Button capacity.", position=(220,55), width=60),
        Component("JUSB1", "Raspberry Pi USB host - SELECTION REQUIRED", [pn("JUSB1","VBUS","USB VBUS","PI_USB_5V","right"), pn("JUSB1","D-","USB D-","USB_D_MINUS","right"), pn("JUSB1","D+","USB D+","USB_D_PLUS","right"), pn("JUSB1","GND","USB GND","GRIP_0V","right")], "CABLE/PORT SELECTION REQUIRED", "Exact Pi port, cable, retention, enumeration, disconnect and EMC evidence remain open.", "Raspberry Pi host boundary", "No connector order code released.", position=(35,125), width=30),
        Component("UGRIP1", "Pololu Micro Maestro 6 item 1350 - ORDINARY CONTROL", [pn("UGRIP1","USB5V","USB logic power","PI_USB_5V","left"), pn("UGRIP1","USB_D-","USB D-","USB_D_MINUS","left"), pn("UGRIP1","USB_D+","USB D+","USB_D_PLUS","left"), pn("UGRIP1","GND","COMMON GND","GRIP_0V","left"), pn("UGRIP1","SERVO_PWR","SERVO POWER RAIL","GRIP_6V","right"), pn("UGRIP1","5V","5 V LOGIC OUT","MAESTRO_5V","right"), pn("UGRIP1","CH0","PWM OUT","GRIP_PWM","right"), pn("UGRIP1","CH1","FEEDBACK ANALOG IN","GRIP_FB","right"), pn("UGRIP1","CH2","POWER-GOOD ANALOG IN","GRIP_PG_SENSE","right")], "PREFERRED EVALUATION CANDIDATE - ZERO SAFETY CREDIT", "Internal script empty; run-on-startup disabled; CH0 startup/error Off; CH1/CH2 inputs; nonzero serial timeout and all endpoints/speed/acceleration SELECTION REQUIRED and HIL validation required.", "https://www.pololu.com/product/1350/", "User guide copyright 2001-2022; product page current 2026. Not safety rated or credited.", position=(137.5,125), width=55),
        Component("RPG1", "10 kOhm PG pull-up candidate", [pn("RPG1","1","MAESTRO 5 V","MAESTRO_5V","left"), pn("RPG1","2","PG SENSE","GRIP_PG_SENSE","right")], "IMPLEMENTATION SELECTION REQUIRED", "Exact placement/carrier/termination and application review remain open.", "Panasonic ERJ-6ENF1002V record already controlled in Electrical V3", "10 kOhm exact resistor candidate; no carrier released.", position=(220,115), width=35),
        Component("MGRIP1", "Pololu item 3551 FS90-FB gripper - NOT SELECTED", [pn("MGRIP1","6V","SERVO +","GRIP_6V","left"), pn("MGRIP1","GND","SERVO GND","GRIP_0V","left"), pn("MGRIP1","PWM","SERVO PWM","GRIP_PWM","left"), pn("MGRIP1","FB","GREEN FEEDBACK","GRIP_FB","left")], "PREFERRED EVALUATION CANDIDATE - NOT SELECTED", "Received identity, exact connector mapping, endpoints, feedback correlation, current/thermal behavior, guard and stalling/backdrive proof remain open.", "https://www.pololu.com/product/3551 and https://www.pololu.com/product/3436", "Product records current 2026; item 3551 drawing 31 August 2018.", position=(220,150), width=50),
    ]


def write_files(model, items):
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = model.Sheet(1, "01_gripper_interface.kicad_sch", "Protected 6 V / PWM / feedback candidate", "Post-K1/K2 power removal; USB ordinary control; zero functional-safety credit.", compact=True)
    sheet.components = items
    sheet.notes = [
        "LOGICAL TERMINALS ONLY; no physical pin order. EN has no external connection. ZERO SAFETY CREDIT.",
        "No restart motion: CH0 stays Off pending RESET + ARM and a fresh command. All settings/hardware/HIL evidence OPEN.",
    ]
    counts = Counter(pin.net for comp in items for pin in comp.pins)
    wire_numbers = model.build_wire_numbers([sheet], counts)
    root_uuid = model.uid("root-hr-v0-gripper-interface")
    project_data = {"board":{},"boards":[],"cvpcb":{},"erc":{},"libraries":{},"meta":{"filename":f"{PROJECT}.kicad_pro","version":1},"net_settings":{"classes":[],"meta":{"version":3}},"pcbnew":{},"schematic":{},"text_variables":{"PROJECT_STATUS":WARNING,"REVISION":REV}}
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps(project_data, indent=2) + "\n", encoding="utf-8")
    symbols = [model.lib_symbol(comp).replace(f'(symbol "PBV3:{comp.ref}"', f'(symbol "{comp.ref}"', 1) for comp in items]
    (OUT / f"{PROJECT}.kicad_sym").write_text('(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  ' + "\n".join(symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "HR-V0 gripper logical-interface symbols"))\n)\n', encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(model.root_schematic(root_uuid, [sheet]), encoding="utf-8")
    (OUT / sheet.filename).write_text(model.child_schematic(root_uuid, sheet, counts, wire_numbers), encoding="utf-8")
    with (OUT / "connector-schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["reference","logical_terminal","function","net","state","warning"])
        for comp in items:
            for pin in comp.pins:
                writer.writerow([comp.ref,pin.number,pin.name,pin.net,comp.status,WARNING])
    with (OUT / "bom.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(["reference","value","quantity","state","evidence","warning"])
        for comp in items:
            writer.writerow([comp.ref,comp.value,1,comp.status,comp.evidence,WARNING])


def run_cli():
    validation, output = OUT / "validation", OUT / "output"
    validation.mkdir(exist_ok=True); output.mkdir(exist_ok=True)
    cli = KICAD_ROOT / "bin/kicad-cli.exe"
    commands = [
        [str(cli),"sch","erc","--exit-code-violations","--output",str(validation / f"{PROJECT}-erc.rpt"),str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli),"sch","export","netlist","--output",str(validation / f"{PROJECT}.net"),str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli),"sch","export","pdf","--output",str(output / f"{PROJECT}-preliminary.pdf"),str(OUT / f"{PROJECT}.kicad_sch")],
        [str(cli),"sch","export","svg","--output",str(output),str(OUT / f"{PROJECT}.kicad_sch")],
    ]
    logs=[]
    for command in commands:
        result=subprocess.run(command,text=True,capture_output=True)
        logs.append("$ "+subprocess.list2cmdline(command)+"\n"+result.stdout+result.stderr+f"\nexit={result.returncode}\n")
        if result.returncode:
            (validation / "kicad-cli.log").write_text("\n".join(logs),encoding="utf-8")
            raise SystemExit(result.returncode)
    for svg in output.glob("*.svg"):
        svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)",b"",svg.read_bytes()))
    (validation / "kicad-cli.log").write_text("\n".join(logs),encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)


def write_docs():
    (OUT / "README.md").write_text(f'''# HR-V0 gripper ordinary-control candidate {REV}\n\n**{WARNING}**\n\nThis native KiCad project encodes a proposed post-K1/K2 24 V branch feeding a held fuse, Pololu D24V22F6 6 V regulator candidate, Micro Maestro 6 ordinary controller candidate and Pololu item 3551 feedback-servo gripper candidate. Component terminals are logical functional identifiers, not physical connector pin numbers or pad positions.\n\nThe Maestro receives logic power/control over Raspberry Pi USB. Its servo rail receives the separate regulated 6 V branch. CH0 is PWM, CH1 is feedback and CH2 is regulator power-good through a held 10 kOhm pull-up. The D24V22F6 EN terminal has no external connection.\n\nRequired fail-passive configuration is not released: empty internal script, run-on-startup disabled, CH0 startup/error Off, CH1/CH2 inputs, and a nonzero serial timeout accepted against the stopping-time budget. E-stop release/reset cannot itself issue a PWM command; actuator power may return only to an Off output until RESET + ARM validation and a deliberate fresh command. All of this remains ordinary control with zero safety credit.\n\nFGRIP1 value/MPN, cable, connectors, carrier, capacitance, thermal/noise/EMC, settings, received mapping and HIL/fault evidence are SELECTION REQUIRED. ERC validates encoded connectivity only. No procurement, PCB/harness fabrication, connection or energization is authorized.\n''',encoding="utf-8")
    rows=[]
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(OUT).as_posix(),hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (OUT / "SOURCE-MANIFEST.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.writer(handle); writer.writerow(["file","sha256"]); writer.writerows(rows)


def main() -> int:
    model=load_model(); items=components(model); write_files(model,items); run_cli(); write_docs()
    print(f"Generated {PROJECT}: {len(items)} logical blocks; native KiCad ERC/netlist/PDF/SVG completed")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
