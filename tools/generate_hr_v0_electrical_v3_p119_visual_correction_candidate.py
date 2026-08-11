#!/usr/bin/env python3
"""Generate a layout-only P1.19 successor to the P1.18 panel-topology candidate.

P1.19 preserves the P1.18 component, terminal, and net model.  It shortens only
title-block presentation strings, reflows notes, supplies bounded visible
component captions, and moves crowded symbols away from sheet edges.  P1.18 is
left immutable so the R222-R229 audit trail remains reproducible.
"""

from __future__ import annotations

import shutil
import sys
import types
from pathlib import Path

from generate_hr_v0_electrical_v3_p118_panel_topology_candidate import transformed_source as p118_source


ROOT = Path(__file__).resolve().parents[1]


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transformed_source() -> str:
    text = p118_source()
    text = once(
        text,
        'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.18-panel-topology-candidate"',
        'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.19-visual-correction-candidate"',
        "output path",
    )
    text = once(
        text,
        'PROJECT = "project-button-v3-p1.18-panel-topology-candidate"',
        'PROJECT = "project-button-v3-p1.19-visual-correction-candidate"',
        "project name",
    )
    text = once(
        text,
        'REV = "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE"',
        'REV = "V3-P1.19-VISUAL-CORRECTION-CANDIDATE"',
        "revision",
    )
    text = once(
        text,
        'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 PANEL-TOPOLOGY CANDIDATE"',
        'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 VISUAL-CORRECTION CANDIDATE"',
        "project title",
    )
    text = once(
        text,
        'PROJECT_SUBTITLE = "P1.15 logic plus explicit XD24/XD0 distribution and XN1/XN2/XN3 three-way nodes; no hidden splices."',
        'PROJECT_SUBTITLE = "P1.18 connectivity preserved; page layout corrected for bounded labels, readable notes, and reviewable title blocks."',
        "project subtitle",
    )

    # Keep the full warning as the prominent top-of-sheet text.  The KiCad
    # title block has finite cells, so it carries a short pointer instead of a
    # second overflowing copy of the warning or the long configuration name.
    text = once(
        text,
        '''  (title_block (title "PB HR-V0 {REV} - {sheet.number:02d}") (date "{DATE}") (rev "{REV}")
    (company "Project Button") (comment 1 "{WARNING}") (comment 2 "CONNECTED DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED"))''',
        '''  (title_block (title "PB HR-V0 ELEC P1.19 - {sheet.number:02d}") (date "{DATE}") (rev "P1.19")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED LAYOUT CANDIDATE"))''',
        "child title block",
    )
    text = once(
        text,
        '''  (title_block (title "{esc(PROJECT_TITLE)} index") (date "{DATE}") (rev "{REV}")
    (company "Project Button") (comment 1 "{WARNING}") (comment 2 "V2.1 PRESERVED; V3 IS A CONNECTED CANDIDATE"))''',
        '''  (title_block (title "PB HR-V0 ELEC P1.19 INDEX") (date "{DATE}") (rev "P1.19")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED LAYOUT CANDIDATE"))''',
        "root title block",
    )

    # Bound note width to the left side of the A3 sheet so it cannot enter the
    # title block.  Start high enough to accommodate the longest three-note
    # sheet without placing any line outside the frame.
    text = once(
        text,
        '    note_y = 164.0 if sheet.compact else 260.0',
        '    note_y = 164.0 if sheet.compact else 244.0',
        "note origin",
    )
    text = once(
        text,
        '''    border_x = 281.94 if sheet.compact else 406.40
    border_y = 184.15 if sheet.compact else 281.94
    note_y = 164.0 if sheet.compact else 244.0
    paper = "A4" if sheet.compact else "A3"''',
        '''    border_x = 281.94 if sheet.compact else 406.40
    border_y = 184.15 if sheet.compact else 281.94
    note_y = 164.0 if sheet.compact else 244.0
    paper = "A4" if sheet.compact else "A3"
    if sheet.number in (1, 2, 3, 7, 10):
        border_x, border_y, note_y, paper = 580.0, 405.0, 365.0, "A2"''',
        "A2 high-density sheets",
    )
    text = once(
        text,
        '        wrapped = textwrap.wrap(f"NOTE {idx+1}: {note}", width=92, subsequent_indent="        ") or [""]',
        '        wrapped = textwrap.wrap(f"NOTE {idx+1}: {note}", width=90, subsequent_indent="        ") or [""]',
        "note wrapping",
    )

    # Visible captions may be shorter than the exact hidden Value/BOM field.
    # This is a presentation-only mechanism and does not alter component
    # identity, netlist value, BOM, terminal schedules, or source evidence.
    display_expr = 'getattr(comp, "display", "") or comp.value'
    text = text.replace('property_block("Display", comp.value,', f'property_block("Display", {display_expr},')

    text = once(
        text,
        '''    s1.components = placed(
        ["PSA1", "JA1", "PSU2", "J24", "F24", "PSU3", "SP1", "XD24", "XD0"],
        [(65, 55), (205, 55), (345, 55), (65, 145), (205, 145), (345, 145), (65, 235), (205, 225), (345, 225)],
    )''',
        '''    s1.components = placed(
        ["PSA1", "JA1", "PSU2", "J24", "F24", "PSU3", "SP1", "XD24", "XD0"],
        [(100, 70), (300, 70), (470, 70), (100, 175), (300, 175), (470, 175), (100, 285), (300, 275), (470, 275)],
    )
    all_components["XD24"].display = "Phoenix Contact PTFIX 6/18 distribution block - 24 V"
    all_components["XD0"].display = "Phoenix Contact PTFIX 6/18 distribution block - 0 V"''',
        "sheet 01 layout",
    )
    text = once(
        text,
        '    s2.components = placed(["S0", "SR1", "S1", "H1", "XN1", "XN3"], [(65, 65), (205, 85), (345, 65), (65, 210), (205, 210), (345, 210)])',
        '''    s2.components = placed(["S0", "SR1", "S1", "H1", "XN1", "XN3"], [(100, 85), (300, 95), (470, 85), (100, 275), (300, 275), (470, 275)])
    all_components["XN1"].display = "Phoenix Contact PT 2,5-TWIN - SR1 S12 fanout"
    all_components["XN3"].display = "Phoenix Contact PT 2,5-TWIN - SR1 status fanout"''',
        "sheet 02 layout",
    )
    text = once(
        text,
        '    s3.components = placed(["SRA1", "KWD1", "KWD2", "S2", "XN2"], [(65, 85), (205, 75), (345, 75), (65, 210), (205, 210)])',
        '''    s3.components = placed(["SRA1", "KWD1", "KWD2", "S2", "XN2"], [(100, 95), (300, 85), (470, 85), (100, 275), (300, 275)])
    all_components["XN2"].display = "Phoenix Contact PT 2,5-TWIN - SRA1 S12 fanout"''',
        "sheet 03 layout",
    )
    text = once(
        text,
        '        [(95, 55), (190, 80), (305, 55), (340, 115), (105, 210), (250, 150), (95, 120), (250, 230), (95, 160)],',
        '        [(100, 70), (300, 70), (470, 70), (300, 190), (300, 300), (470, 190), (100, 190), (470, 300), (100, 300)],',
        "sheet 07 A2 layout",
    )
    text = once(
        text,
        '    s9.components = placed(["PI1", "XT1"], [(left, 85), (right, 150)])',
        '''    s9.components = placed(["PI1", "XT1"], [(105, 80), (285, 140)])
    all_components["XT1"].display = "Phoenix Contact PT 2,5 six-position terminal group"''',
        "sheet 09 layout",
    )
    text = once(
        text,
        '        ["U1", "INJ1", "J1", "J2", "J3", "JFRAME1"],\n        [(65, 65), (150, 150), (360, 65), (360, 145), (360, 225), (80, 225)],',
        '        ["U1", "INJ1", "J1", "J2", "J3", "JFRAME1"],\n        [(100, 75), (300, 190), (470, 75), (470, 190), (470, 305), (100, 300)],',
        "sheet 10 A2 layout",
    )
    text = once(
        text,
        '    s10.notes = ["The V0 bus is TTL; HR-30 RS-485 remains a separate architecture.",',
        '    all_components["JFRAME1"].display = "Frame/shield bonding interface - selection required"\n    s10.notes = ["The V0 bus is TTL; HR-30 RS-485 remains a separate architecture.",',
        "sheet 10 display caption",
    )

    text = text.replace(
        "Run the R222 panel-topology candidate generator with `--validate`",
        "Run the R230 visual-correction candidate generator with `--validate`",
    )
    return text


def main() -> int:
    name = "visual_correction_electrical_generator"
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
