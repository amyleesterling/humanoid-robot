#!/usr/bin/env python3
"""Generate the unaccepted P1.20 dual-channel watchdog-interlock candidate.

P1.20 starts from the visually corrected P1.19 source.  It leaves both direct
S0 input loops and all final-element circuits intact, powers SR1 directly from
SAFETY_24V, and inserts one ordinary KWD NO contact in each SRA1 input return.
The ordinary watchdog retains zero safety credit; this candidate only improves
the source-level single-contact fault boundary and manual-rearm behavior.
"""

from __future__ import annotations

import shutil
import sys
import types
from pathlib import Path

from generate_hr_v0_electrical_v3_p119_visual_correction_candidate import transformed_source as p119_source


ROOT = Path(__file__).resolve().parents[1]


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def between(text: str, start: str, end: str, new: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) < 1:
        raise RuntimeError(f"{label}: source boundary missing or ambiguous")
    first = text.index(start)
    last = text.index(end, first)
    return text[:first] + new + text[last:]


def transformed_source() -> str:
    text = p119_source()
    replacements = [
        ('OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.19-visual-correction-candidate"', 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"', "output path"),
        ('PROJECT = "project-button-v3-p1.19-visual-correction-candidate"', 'PROJECT = "project-button-v3-p1.20-watchdog-interlock-candidate"', "project name"),
        ('REV = "V3-P1.19-VISUAL-CORRECTION-CANDIDATE"', 'REV = "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE"', "revision"),
        ('PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 VISUAL-CORRECTION CANDIDATE"', 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 WATCHDOG-INTERLOCK CANDIDATE"', "project title"),
        ('PROJECT_SUBTITLE = "P1.18 connectivity preserved; page layout corrected for bounded labels, readable notes, and reviewable title blocks."', 'PROJECT_SUBTITLE = "P1.19 layout preserved; two ordinary watchdog contacts interrupt separate SRA1 input returns; zero safety credit."', "project subtitle"),
        ('''  (title_block (title "PB HR-V0 ELEC P1.19 - {sheet.number:02d}") (date "{DATE}") (rev "P1.19")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED LAYOUT CANDIDATE"))''', '''  (title_block (title "PB HR-V0 ELEC P1.20 - {sheet.number:02d}") (date "{DATE}") (rev "P1.20")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED INTERLOCK CANDIDATE"))''', "child title block"),
        ('''  (title_block (title "PB HR-V0 ELEC P1.19 INDEX") (date "{DATE}") (rev "P1.19")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED LAYOUT CANDIDATE"))''', '''  (title_block (title "PB HR-V0 ELEC P1.20 INDEX") (date "{DATE}") (rev "P1.20")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED INTERLOCK CANDIDATE"))''', "root title block"),
    ]
    for old, new, label in replacements:
        text = once(text, old, new, label)

    text = once(
        text,
        '''        pnoz("SR1", (210, 95), {"A1":"SR1_A1_WD_GATED", "S11":"SR1_S11", "S12":"SR1_S12", "S21":"SR1_S21", "S22":"SR1_S22", "S34":"SR1_START_RETURN",
                                   "13":"SRA1_S11", "14":"SRA1_S12", "23":"SRA1_S21", "24":"SRA1_S22",
                                   "33":"INTENTIONALLY_UNUSED_SR1_33", "34":"INTENTIONALLY_UNUSED_SR1_34",
                                   "41":"SAFETY_24V", "42":"SR1_DIAG_NC", "Y32":"SR1_STATUS"},
             "First-stage E-stop eligibility relay."),''',
        '''        pnoz("SR1", (210, 95), {"A1":"SAFETY_24V", "S11":"SR1_S11", "S12":"SR1_S12", "S21":"SR1_S21", "S22":"SR1_S22", "S34":"SR1_START_RETURN",
                                   "13":"SRA1_S11", "14":"SR1_OUT1_TO_KWD1", "23":"SRA1_S21", "24":"SR1_OUT2_TO_KWD2",
                                   "33":"INTENTIONALLY_UNUSED_SR1_33", "34":"INTENTIONALLY_UNUSED_SR1_34",
                                   "41":"SAFETY_24V", "42":"SR1_DIAG_NC", "Y32":"SR1_STATUS"},
             "First-stage E-stop eligibility relay; A1 remains powered independently of the ordinary watchdog."),''',
        "SR1 terminal allocation",
    )

    kwd = '''        Component("KWD1", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD1", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD1", "A2", "DRIVER RETURN", "WD1_COIL_N", "left"),
                   pn("KWD1", "11", "SRA1 CH1 INTERLOCK IN", "SR1_OUT1_TO_KWD1", "left"), pn("KWD1", "14", "SRA1 CH1 INTERLOCK OUT", "SRA1_S12", "right"),
                   pn("KWD1", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD1_12", "right"), pn("KWD1", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD1", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD1_24", "right"), pn("KWD1", "22", "CH2 NC FEEDBACK", "WD1_NC_24V", "right")],
                  "PROPOSED - SRA1 INPUT-INTERLOCK APPLICATION/FMEA/RECEIVED VERIFICATION REQUIRED", "First ordinary watchdog interlock. Its 11-14 NO contact interrupts only the SRA1 channel-1 return between SR1:14 and SRA1:S12. KWD2 separately interrupts channel 2. A single welded KWD1 contact cannot preserve SRA1 eligibility when KWD2 opens. Ordinary relay, not force-guided and not safety-rated; no PL/SIL credit. Received terminal identity, input-current/contact duty, polarity, continuity, wear and fault tests remain open.",
                  "https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060",
                  "Phoenix Contact official product record and generated PDF; data-maintenance date 2026-04-01; rechecked 2026-08-11. Circuit diagram identifies A1/A2, 11-12-14 and 21-22-24; 24 VDC, 18 mA typical, 8 ms pickup, 10 ms release.", (210, 72), 82),
        Component("KWD2", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD2", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD2", "A2", "DRIVER RETURN", "WD2_COIL_N", "left"),
                   pn("KWD2", "11", "SRA1 CH2 INTERLOCK IN", "SR1_OUT2_TO_KWD2", "left"), pn("KWD2", "14", "SRA1 CH2 INTERLOCK OUT", "SRA1_S22", "right"),
                   pn("KWD2", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD2_12", "right"), pn("KWD2", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD2", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD2_24", "right"), pn("KWD2", "22", "CH2 NC FEEDBACK", "WD2_NC_24V", "right")],
                  "PROPOSED - SRA1 INPUT-INTERLOCK APPLICATION/FMEA/RECEIVED VERIFICATION REQUIRED", "Second ordinary watchdog interlock. Its 11-14 NO contact interrupts only the SRA1 channel-2 return between SR1:24 and SRA1:S22. A single welded KWD2 contact cannot preserve SRA1 eligibility when KWD1 opens. Dual weld/bypass, common controller/supply faults, contact application, received verification and physical validation remain open. No PL/SIL credit.",
                  "https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060",
                  "Phoenix Contact official product record and generated PDF; data-maintenance date 2026-04-01; rechecked 2026-08-11.", (340, 72), 82),
'''
    text = between(text, '        Component("KWD1"', '        Component("S2"', kwd, "KWD component block")

    text = once(
        text,
        '"Heartbeat loss removes SR1 A1 through the separate two-contact supply gate; recovery alone cannot restore the monitored RESET stage."',
        '"Heartbeat loss opens both SRA1 input returns while SR1 remains powered; recovery alone cannot restore the monitored ARM stage."',
        "sheet 02 note",
    )
    text = once(
        text,
        's3 = Sheet(3, "03_arm_watchdog_eligibility.kicad_sch", "Distinct ARM and watchdog-gated SR1 supply",\n               "Two ordinary KWD contacts gate SR1 A1; SRA1 still requires SR1 outputs, EDM proof and a new ARM action.")',
        's3 = Sheet(3, "03_arm_watchdog_eligibility.kicad_sch", "Distinct ARM and dual-channel watchdog interlock",\n               "Separate ordinary KWD contacts interrupt the two SRA1 input returns; both stages retain zero safety credit.")',
        "sheet 03 title",
    )
    text = once(
        text,
        '''    s3.notes = ["Required after E-stop/watchdog dropout: cause healthy -> KWD supply restored -> RESET press/release -> SAFE_READY -> distinct ARM press/release.",
                "KWD contacts are in series with SR1 A1 only; S0 remains direct in both SR1 input returns and SRA1 receives both SR1 safety outputs directly."]''',
        '''    s3.notes = ["After a successful watchdog dropout: cause healthy -> both KWD contacts restored -> SR1 remains SAFE_READY -> distinct monitored ARM press/release -> K1/K2 may energize.",
                "KWD1 interrupts SR1:14 to SRA1:S12 and KWD2 interrupts SR1:24 to SRA1:S22. One welded contact is defeated by the other opening; dual/common-cause failures remain hazardous and receive zero safety credit."]''',
        "sheet 03 notes",
    )
    text = text.replace(
        "Run the R230 visual-correction candidate generator with `--validate`",
        "Run the R232 watchdog-interlock candidate generator with `--validate`",
    )
    text = text.replace(
        "KWD1:11-14 and KWD2:11-14 are series SR1 A1 supply gates, not E-stop input contacts.",
        "KWD1:11-14 and KWD2:11-14 interrupt separate SRA1 input returns, not SR1 power or either S0 input loop.",
    )
    text = once(
        text,
        "- Two separately driven ordinary watchdog relay contacts are in series with the SR1 A1 supply. Heartbeat loss power-cycles SR1 and forces the physical RESET stage to drop, while S0 remains direct in both SR1 input loops. Internal KWD A1/21-to-14 shorts can defeat the diagnostic gate but cannot inject downstream of S0. Supply switching, protected routing, common-cause analysis and physical proof remain open; the watchdog receives zero safety credit.",
        "- Two separately driven ordinary watchdog relay contacts interrupt separate SRA1 input returns while SR1 remains powered independently. A successful heartbeat-loss dropout opens SRA1 outputs and therefore both contactor-coil paths; monitored ARM must be performed again before the contactors can return. Either single KWD 11-14 weld is defeated by the other channel opening. Dual weld/bypass, common controller/supply failure, input-contact application, protected routing, physical proof and qualified allocation remain open; the watchdog receives zero safety credit.",
        "README topology summary",
    )
    return text


def main() -> int:
    name = "watchdog_interlock_electrical_generator"
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
