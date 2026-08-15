#!/usr/bin/env python3
"""Generate a P1.16 system-level candidate with the R202/R204 observation chain."""

from __future__ import annotations

import shutil
import sys
import types
from pathlib import Path

from generate_hr_v0_electrical_v3_p115_carrier_candidate import transformed_source as p115_source


ROOT = Path(__file__).resolve().parents[1]


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transformed_source() -> str:
    text = p115_source()
    text = once(text, 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"', 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.16-observation-candidate"', "output path")
    text = once(text, 'PROJECT = "project-button-v3-p1.15-carrier-candidate"', 'PROJECT = "project-button-v3-p1.16-observation-candidate"', "project name")
    text = once(text, 'REV = "V3-P1.15-CARRIER-CANDIDATE"', 'REV = "V3-P1.16-OBSERVATION-CANDIDATE"', "revision")
    text = once(text, 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 CARRIER-INTEGRATED CANDIDATE"', 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 OBSERVATION-INTEGRATED CANDIDATE"', "title")
    text = once(text, 'PROJECT_SUBTITLE = "P0.3 branch limiters inserted between F1/F2/F3 and DXL-STAR; pre/post rails are distinct."', 'PROJECT_SUBTITLE = "P1.15 limiter chain plus exact R202/R204 field and compute observation interfaces; zero safety credit."', "subtitle")
    text = once(text, 'DATE = "2026-08-09"', 'DATE = "2026-08-10"', "date")
    text = once(
        text,
        'WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"',
        'WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"',
        "controlled warning",
    )
    text = once(
        text,
        '''    positions = [
        (17.78 + col * 132.08, 42.0 + row * 56.0)
        for row in range(4)
        for col in range(3)
    ]''',
        '''    positions = [
        (17.78 + col * 132.08, 42.0 + row * 50.0)
        for row in range(5)
        for col in range(3)
    ]''',
        "root hierarchy capacity",
    )

    observation_components = '''        Component("OBS1", "HR-V0-RUNTIME-OBS-CARRIER-P0.2 diagnostic receiver assembly",
                  [pn("OBS1", "JFIELD1:1", "SR1 STATUS", "SR1_STATUS", "left"),
                   pn("OBS1", "JFIELD1:2", "SRA1 STATUS", "SRA1_STATUS", "left"),
                   pn("OBS1", "JFIELD1:3", "K1 STATUS", "K1_STATUS", "left"),
                   pn("OBS1", "JFIELD1:4", "K2 STATUS", "K2_STATUS", "left"),
                   pn("OBS1", "JFIELD1:5", "FIELD RETURN", "SAFETY_0V", "left"),
                   pn("OBS1", "JFIELD1:6", "INTENTIONALLY UNUSED", "INTENTIONALLY_UNUSED_OBS1_JFIELD1_6", "left"),
                   pn("OBS1", "JLOGIC1:1", "PI 3V3 SOURCE CANDIDATE", "PI_3V3_CANDIDATE", "right"),
                   pn("OBS1", "JLOGIC1:2", "COMPUTE RETURN", "COMPUTE_0V", "right"),
                   pn("OBS1", "JLOGIC1:3", "SR1 DIAGNOSTIC", "OBS_SR1_PI", "right"),
                   pn("OBS1", "JLOGIC1:4", "SRA1 DIAGNOSTIC", "OBS_SRA1_PI", "right"),
                   pn("OBS1", "JLOGIC1:5", "K1 DIAGNOSTIC", "OBS_K1_PI", "right"),
                   pn("OBS1", "JLOGIC1:6", "K2 DIAGNOSTIC", "OBS_K2_PI", "right")],
                  "EXACT NATIVE SUBASSEMBLY CANDIDATE - PHYSICAL/HARNESS/REVIEW HOLD",
                  "R202 four-layer receiver assembly. Field and compute domains remain separated inside the subassembly; this system block assigns no safety credit and releases no fabrication, harness, connection or powered work.",
                  "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/",
                  "R202 native source: five sheets, Phoenix item 1751280 at both boundaries, ERC/DRC 0; fourteen physical/application holds remain open.",
                  position=(95, 140), width=125, height=48),
        Component("PIOBS1", "HR-V0-PI-OBS-CARRIER-P0.1 passive Pi observation carrier",
                  [pn("PIOBS1", "JOBS1:1", "PI 3V3 SOURCE CANDIDATE", "PI_3V3_CANDIDATE", "left"),
                   pn("PIOBS1", "JOBS1:2", "COMPUTE RETURN", "COMPUTE_0V", "left"),
                   pn("PIOBS1", "JOBS1:3", "SR1 DIAGNOSTIC", "OBS_SR1_PI", "left"),
                   pn("PIOBS1", "JOBS1:4", "SRA1 DIAGNOSTIC", "OBS_SRA1_PI", "left"),
                   pn("PIOBS1", "JOBS1:5", "K1 DIAGNOSTIC", "OBS_K1_PI", "left"),
                   pn("PIOBS1", "JOBS1:6", "K2 DIAGNOSTIC", "OBS_K2_PI", "left"),
                   pn("PIOBS1", "JPI1:17", "PI PHYSICAL 17 / 3V3", "PI_3V3_CANDIDATE", "right"),
                   pn("PIOBS1", "JPI1:20", "PI PHYSICAL 20 / GND", "COMPUTE_0V", "right"),
                   pn("PIOBS1", "JPI1:15", "PI PHYSICAL 15 / GPIO22", "OBS_SR1_PI", "right"),
                   pn("PIOBS1", "JPI1:16", "PI PHYSICAL 16 / GPIO23", "OBS_SRA1_PI", "right"),
                   pn("PIOBS1", "JPI1:18", "PI PHYSICAL 18 / GPIO24", "OBS_K1_PI", "right"),
                   pn("PIOBS1", "JPI1:22", "PI PHYSICAL 22 / GPIO25", "OBS_K2_PI", "right")],
                  "EXACT NATIVE PASSIVE CARRIER CANDIDATE - STACK/HARNESS/REVIEW HOLD",
                  "R204 carries only six named nets and no 5 V, ID EEPROM or unused-GPIO copper. The represented Pi pins are diagnostic/ordinary-control inputs with zero safety credit.",
                  "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/",
                  "R204 native source: two sheets, Samtec ESQ-120-33-G-D and Phoenix item 1751280 candidates, ERC/DRC 0; ten holds remain open.",
                  position=(300, 140), width=125, height=48),
'''
    text = once(
        text,
        '    ]\n    s6.notes = ["The V0 bus is TTL because the selected -T actuators are TTL variants; HR-30 RS-485 remains a separate architecture.",',
        observation_components + '    ]\n    s6.notes = ["The V0 bus is TTL because the selected -T actuators are TTL variants; HR-30 RS-485 remains a separate architecture.",',
        "observation component insertion",
    )

    sheet13 = '''
    s13 = Sheet(13, "13_runtime_observation_system.kicad_sch", "Runtime diagnostic observation interfaces",
                "XT1 status conductors feed the R202 isolated receiver; R204 carries six compute-side nets to exact Pi physical pins.")
    s13.components = placed(["OBS1", "PIOBS1"], [(95, 140), (300, 140)])
    s13.notes = ["OBS1 JFIELD1.1-.5 bind directly to XT1-03, -04, -05, -06 and -02 by named net; JFIELD1.6 is deliberately unused.",
                 "The compute harness binds JLOGIC1.1-.6 to JOBS1.1-.6 one-for-one; Pi physical pins are 17, 20, 15, 16, 18 and 22.",
                 "Heartbeat GPIO17 on Pi physical pin 11 and return pin 6 remain a separate ordinary interface on JWH1.",
                 "The observation chain is diagnostic only: it cannot command, restore, latch or preserve motion and receives zero functional-safety credit."]

'''
    text = once(
        text,
        '    for comp in [*s7.components, *s8.components, *s11.components, *s12.components]:',
        sheet13 + '    for comp in [*s7.components, *s8.components, *s11.components, *s12.components]:',
        "sheet 13 insertion",
    )
    text = once(
        text,
        '    return [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]',
        '    return [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]',
        "sheet return list",
    )
    text = text.replace("Run the R161 carrier-candidate generator with `--validate`", "Run the R206 observation-candidate generator with `--validate`")
    return text


def main() -> int:
    name = "observation_integrated_electrical_generator"
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "tools/generate_hr_v0_electrical_v3.py")
    sys.modules[name] = module
    exec(compile(transformed_source(), module.__file__, "exec"), module.__dict__)
    footprint_source = ROOT / "electrical/kicad/project-button-v3/PBV3_Footprints.pretty"
    footprint_target = module.OUT / "PBV3_Footprints.pretty"
    footprint_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(footprint_source, footprint_target, dirs_exist_ok=True)
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
