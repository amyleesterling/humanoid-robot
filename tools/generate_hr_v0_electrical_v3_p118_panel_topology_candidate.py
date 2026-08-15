#!/usr/bin/env python3
"""Generate a P1.18 system ECAD candidate with explicit panel distribution nodes.

This derivative preserves the P1.15 safety/control logic and adds only physical
terminal-node candidates needed by the R222 point-to-point schedule.  It does
not select conductors, protection, or authorize construction.
"""

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
    text = once(text, 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"',
                'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.18-panel-topology-candidate"', "output path")
    text = once(text, 'PROJECT = "project-button-v3-p1.15-carrier-candidate"',
                'PROJECT = "project-button-v3-p1.18-panel-topology-candidate"', "project name")
    text = once(text, 'REV = "V3-P1.15-CARRIER-CANDIDATE"',
                'REV = "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE"', "revision")
    text = once(text, 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 CARRIER-INTEGRATED CANDIDATE"',
                'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 PANEL-TOPOLOGY CANDIDATE"', "title")
    text = once(text,
                'PROJECT_SUBTITLE = "P0.3 branch limiters inserted between F1/F2/F3 and DXL-STAR; pre/post rails are distinct."',
                'PROJECT_SUBTITLE = "P1.15 logic plus explicit XD24/XD0 distribution and XN1/XN2/XN3 three-way nodes; no hidden splices."',
                "subtitle")
    text = once(text, 'DATE = "2026-08-09"', 'DATE = "2026-08-11"', "date")
    text = once(text,
                'WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"',
                'WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"',
                "warning")

    xd24 = '''        Component("XD24", "Phoenix Contact PTFIX 6/18X2,5-NS35 RD, item 3273114",
                  [pn("XD24", "LINE", "PROTECTED 24 V FEED", "SAFETY_24V", "left")] +
                  [pn("XD24", f"{i:02d}", f"24 V LOAD {i:02d}", "SAFETY_24V", "right") for i in range(1, 15)],
                  "EXACT CATALOG CANDIDATE - TOPOLOGY/PROTECTION/PHYSICAL REVIEW HOLD",
                  "One red NS35 distribution block: one line contact and fourteen allocated load contacts. Load positions 15-18 remain physically live spare contacts and shall be covered/marked; they are intentionally omitted from the modeled wire schedule. Current, protection, conductor, fill, temperature and received identity remain open.",
                  "https://www.phoenixcontact.com/us/products/3273114",
                  "Official generated product PDF dated 2026-08-10; nineteen connections total, one 0.5-10 mm2 flexible line contact and eighteen 0.14-4 mm2 flexible load contacts; 24 A nominal. Project application remains unapproved.",
                  position=(75, 295), width=112, height=88),
        Component("XD0", "Phoenix Contact PTFIX 6/18X2,5-NS35 BU, item 3273112",
                  [pn("XD0", "LINE", "CONTROL 0 V FEED", "SAFETY_0V", "left")] +
                  [pn("XD0", f"{i:02d}", f"0 V LOAD {i:02d}", "SAFETY_0V", "right") for i in range(1, 8)],
                  "EXACT CATALOG CANDIDATE - TOPOLOGY/PROTECTION/PHYSICAL REVIEW HOLD",
                  "One blue NS35 distribution block: one line contact and seven allocated load contacts. Load positions 08-18 remain physically live spare contacts and shall be covered/marked; they are intentionally omitted from the modeled wire schedule. Return policy, protection, conductor, fill, temperature and received identity remain open.",
                  "https://www.phoenixcontact.com/us/products/3273112",
                  "Official live product record accessed 2026-08-11; nineteen connections total, one 0.5-10 mm2 flexible line contact and eighteen 0.14-4 mm2 flexible load contacts; 24 A nominal. Project application remains unapproved.",
                  position=(245, 295), width=112, height=64),
'''
    text = once(text, '    ]\n    s1.notes = ["All AC conductors shown are factory boundaries, not project-built wiring.",',
                xd24 + '    ]\n    s1.notes = ["All AC conductors shown are factory boundaries, not project-built wiring.",',
                "source-sheet distribution insertion")

    s2_nodes = '''        Component("XN1", "Phoenix Contact PT 2,5-TWIN, item 3209549 - SR1 S12 fanout",
                  [pn("XN1", "1", "SR1 S12", "SR1_S12", "left"),
                   pn("XN1", "2", "S0 CH1 RETURN", "SR1_S12", "right"),
                   pn("XN1", "3", "RESET FEED", "SR1_S12", "right")],
                  "EXACT CATALOG CANDIDATE - TOPOLOGY/PHYSICAL REVIEW HOLD",
                  "Three independent push-in clamping points replace an implicit three-way splice. Position allocation is controlled only by the R222 point-to-point schedule; conductor, marking, installation and safety review remain open.",
                  "https://www.phoenixcontact.com/us/products/3209549",
                  "Official generated product PDF dated 2026-08-10; three connections, 0.14-4 mm2 flexible, 8-10 mm strip, 24 A nominal.",
                  position=(210, 245), width=96),
        Component("XN3", "Phoenix Contact PT 2,5-TWIN, item 3209549 - SR1 status fanout",
                  [pn("XN3", "1", "SR1 Y32", "SR1_STATUS", "left"),
                   pn("XN3", "2", "H1 DIAGNOSTIC", "SR1_STATUS", "right"),
                   pn("XN3", "3", "XT1-03 DIAGNOSTIC", "SR1_STATUS", "right")],
                  "EXACT CATALOG CANDIDATE - TOPOLOGY/PHYSICAL REVIEW HOLD",
                  "Diagnostic-only three-way node. No safety credit. Conductor, loading, marking, installation and received verification remain open.",
                  "https://www.phoenixcontact.com/us/products/3209549",
                  "Official generated product PDF dated 2026-08-10; same terminal envelope as XN1.",
                  position=(340, 245), width=96),
'''
    text = once(text, '    ]\n    s2.notes = ["S0 connects directly to both SR1 input returns; no ordinary watchdog terminal is present in either input loop.",',
                s2_nodes + '    ]\n    s2.notes = ["S0 connects directly to both SR1 input returns; no ordinary watchdog terminal is present in either input loop.",',
                "estop-sheet node insertion")

    s3_node = '''        Component("XN2", "Phoenix Contact PT 2,5-TWIN, item 3209549 - SRA1 S12 fanout",
                  [pn("XN2", "1", "SR1 OUTPUT 14", "SRA1_S12", "left"),
                   pn("XN2", "2", "SRA1 S12", "SRA1_S12", "right"),
                   pn("XN2", "3", "ARM FEED", "SRA1_S12", "right")],
                  "EXACT CATALOG CANDIDATE - TOPOLOGY/PHYSICAL REVIEW HOLD",
                  "Three independent push-in clamping points replace an implicit three-way splice in the ARM eligibility feed. Conductor, marking, installation and safety review remain open.",
                  "https://www.phoenixcontact.com/us/products/3209549",
                  "Official generated product PDF dated 2026-08-10; three connections, 0.14-4 mm2 flexible, 8-10 mm strip, 24 A nominal.",
                  position=(340, 270), width=96),
'''
    text = once(text, '    ]\n    s3.notes = ["Required sequence after E-stop or watchdog dropout:',
                s3_node + '    ]\n    s3.notes = ["Required sequence after E-stop or watchdog dropout:',
                "arm-sheet node insertion")

    text = once(
        text,
        '''    s1.components = placed(
        ["PSA1", "JA1", "PSU2", "J24", "F24", "PSU3", "SP1"],
        [(100, 60), (325, 60), (100, 140), (325, 140), (100, 210), (325, 210), (210, 255)],
    )''',
        '''    s1.components = placed(
        ["PSA1", "JA1", "PSU2", "J24", "F24", "PSU3", "SP1", "XD24", "XD0"],
        [(65, 55), (205, 55), (345, 55), (65, 145), (205, 145), (345, 145), (65, 235), (205, 225), (345, 225)],
    )''',
        "focused source-sheet placement",
    )
    text = once(
        text,
        '    s2.components = placed(["S0", "SR1", "S1", "H1"], [(left, 85), (right, 95), (left, 205), (right, 205)])',
        '    s2.components = placed(["S0", "SR1", "S1", "H1", "XN1", "XN3"], [(65, 65), (205, 85), (345, 65), (65, 210), (205, 210), (345, 210)])',
        "focused estop-sheet placement",
    )
    text = once(
        text,
        '    s3.components = placed(["SRA1", "KWD1", "S2", "KWD2"], [(left, 85), (right, 85), (left, 205), (right, 205)])',
        '    s3.components = placed(["SRA1", "KWD1", "KWD2", "S2", "XN2"], [(65, 85), (205, 75), (345, 75), (65, 210), (205, 210)])',
        "focused arm-sheet placement",
    )

    text = text.replace("Run the R161 carrier-candidate generator with `--validate`",
                        "Run the R222 panel-topology candidate generator with `--validate`")
    return text


def main() -> int:
    name = "panel_topology_electrical_generator"
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
