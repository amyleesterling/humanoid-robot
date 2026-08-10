"""Generate a carrier-integrated Electrical V3-P1.15 native KiCad candidate.

The current V3-P1.14 baseline remains untouched. This controlled derivative
inserts three explicit P0.3 limiter blocks and separates every pre-limiter rail
from its post-limiter rail.
"""

from __future__ import annotations

import sys
import types
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools" / "generate_hr_v0_electrical_v3.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transformed_source() -> str:
    text = BASE.read_text(encoding="utf-8-sig")
    text = once(text, 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3"', 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"', "output path")
    text = once(text, 'PROJECT = "project-button-v3"', 'PROJECT = "project-button-v3-p1.15-carrier-candidate"', "project name")
    text = once(text, 'REV = "V3-P1.14"', 'REV = "V3-P1.15-CARRIER-CANDIDATE"', "revision")
    text = once(text, 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 CONNECTED CANDIDATE"', 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 CARRIER-INTEGRATED CANDIDATE"', "title")
    text = once(text, 'PROJECT_SUBTITLE = "Direct dual-channel E-stop inputs, watchdog-gated SR1 supply, separate RESET/ARM, redundant actuator interruption."', 'PROJECT_SUBTITLE = "P0.3 branch limiters inserted between F1/F2/F3 and DXL-STAR; pre/post rails are distinct."', "subtitle")
    text = once(text, 'DATE = "2026-08-08"', 'DATE = "2026-08-09"', "date")

    for axis in (1, 2, 3):
        text = once(
            text,
            f'pn("F{axis}", "2", "OUT", "J{axis}_VDD", "right")',
            f'pn("F{axis}", "2", "OUT", "J{axis}_FUSED_PRELIMIT", "right")',
            f"F{axis} output net",
        )
        text = once(
            text,
            f'pn("INJ1", "PWR{axis}:1", "J{axis} FUSED VDD", "J{axis}_VDD", "left")',
            f'pn("INJ1", "PWR{axis}:1", "J{axis} LIMITED VDD", "J{axis}_LIMITED_VDD", "left")',
            f"INJ PWR{axis}",
        )
        text = once(
            text,
            f'pn("INJ1", "ACT{axis}:2", "J{axis} VDD", "J{axis}_VDD", "right")',
            f'pn("INJ1", "ACT{axis}:2", "J{axis} LIMITED VDD", "J{axis}_LIMITED_VDD", "right")',
            f"INJ ACT{axis}",
        )
        text = once(
            text,
            f'pn("J{axis}", "2", "VDD", "J{axis}_VDD", "left")',
            f'pn("J{axis}", "2", "VDD AFTER LIMITER", "J{axis}_LIMITED_VDD", "left")',
            f"J{axis} actuator port",
        )

    limiter_components = '''        Component("LIM1", "HR-V0 DXL protection carrier P0.3 - shoulder branch",
                  [pn("LIM1", "JIN1:1", "FUSED +12 V", "J1_FUSED_PRELIMIT", "left"),
                   pn("LIM1", "JIN1:2", "RETURN", "ACT_0V_PE_BONDED", "left"),
                   pn("LIM1", "JOUT1:1", "LIMITED +12 V", "J1_LIMITED_VDD", "right"),
                   pn("LIM1", "JOUT1:2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT PCB CANDIDATE - FABRICATION/APPLICATION/PHYSICAL EVIDENCE HELD",
                  "P0.3 native carrier candidate only. Forward-current, reverse-energy, thermal, harness, DFM, first-article, fault and qualified-review evidence remain open; no safety credit.",
                  position=(180, 230), width=92),
        Component("LIM2", "HR-V0 DXL protection carrier P0.3 - elbow branch",
                  [pn("LIM2", "JIN1:1", "FUSED +12 V", "J2_FUSED_PRELIMIT", "left"),
                   pn("LIM2", "JIN1:2", "RETURN", "ACT_0V_PE_BONDED", "left"),
                   pn("LIM2", "JOUT1:1", "LIMITED +12 V", "J2_LIMITED_VDD", "right"),
                   pn("LIM2", "JOUT1:2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT PCB CANDIDATE - FABRICATION/APPLICATION/PHYSICAL EVIDENCE HELD",
                  "Same P0.3 candidate and evidence boundary as LIM1.", position=(295, 230), width=92),
        Component("LIM3", "HR-V0 DXL protection carrier P0.3 - gripper branch",
                  [pn("LIM3", "JIN1:1", "FUSED +12 V", "J3_FUSED_PRELIMIT", "left"),
                   pn("LIM3", "JIN1:2", "RETURN", "ACT_0V_PE_BONDED", "left"),
                   pn("LIM3", "JOUT1:1", "LIMITED +12 V", "J3_LIMITED_VDD", "right"),
                   pn("LIM3", "JOUT1:2", "RETURN", "ACT_0V_PE_BONDED", "right")],
                  "EXACT PCB CANDIDATE - FABRICATION/APPLICATION/PHYSICAL EVIDENCE HELD",
                  "P0.3 G1 assembly variant remains an evaluation candidate; same evidence boundary as LIM1.", position=(65, 265), width=92),
'''
    text = once(text, '        Component("INJ1", "HR-V0 DXL-STAR-P0.1 central branch-isolating injection board",', limiter_components + '        Component("INJ1", "HR-V0 DXL-STAR-P0.1 central branch-isolating injection board",', "limiter insertion")

    text = once(
        text,
        '        ["F1", "F2", "F3", "INJ1"],\n        [(left, 55), (left, 130), (left, 205), (right, 130)],',
        '        ["F1", "LIM1", "F2", "LIM2", "F3", "LIM3"],\n        [(75, 55), (280, 55), (75, 130), (280, 130), (75, 205), (280, 205)],',
        "focused sheet placement",
    )
    text = once(
        text,
        '    s6 = Sheet(6, "06_branches_and_injection.kicad_sch", "Protected actuator branches and central DYNAMIXEL star injection",\n               "Each actuator has a separate protected VDD branch; U2D2 pin 2 and inter-actuator VDD paths are omitted.")',
        '    s6 = Sheet(6, "06_branches_and_limiters.kicad_sch", "Protected actuator branches and current-limiter carriers",\n               "Each fuse output and carrier output has a distinct positive rail; physical protection performance remains unproved.")',
        "focused sheet title",
    )
    text = once(
        text,
        '        ["U1", "J1", "J2", "J3", "JFRAME1"],\n        [(left, 70), (right, 70), (left, 165), (right, 165), (180, 225)],',
        '        ["U1", "INJ1", "J1", "J2", "J3", "JFRAME1"],\n        [(65, 65), (150, 150), (360, 65), (360, 145), (360, 225), (80, 225)],',
        "actuator/star sheet placement",
    )
    text = once(
        text,
        '    s10 = Sheet(10, "10_actuator_interfaces.kicad_sch", "U2D2, actuator ports and bonding boundary",\n               "The U2D2 cable carries DATA and GND only; protected VDD is injected at each actuator.")',
        '    s10 = Sheet(10, "10_actuator_interfaces.kicad_sch", "U2D2, DXL star, actuator ports and bonding boundary",\n               "U2D2 pin 2 is omitted; DXL-STAR accepts three distinct limited positive rails and routes DATA/return.")',
        "actuator/star sheet title",
    )
    text = text.replace("DXL-STAR-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE")
    text = text.replace("project-button-v3.kicad_pcb", "PCB-P0.9 baseline watchdog board (separate unchanged native source)")
    text = text.replace("Run `python tools/generate_hr_v0_electrical_v3.py --validate`", "Run the R161 carrier-candidate generator with `--validate`")
    return text


def main() -> int:
    name = "carrier_integrated_electrical_generator"
    module = types.ModuleType(name)
    module.__file__ = str(BASE)
    sys.modules[name] = module
    exec(compile(transformed_source(), str(BASE), "exec"), module.__dict__)
    footprint_source = ROOT / "electrical" / "kicad" / "project-button-v3" / "PBV3_Footprints.pretty"
    footprint_target = module.OUT / "PBV3_Footprints.pretty"
    footprint_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(footprint_source, footprint_target, dirs_exist_ok=True)
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
