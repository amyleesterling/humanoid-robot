#!/usr/bin/env python3
"""Generate the unaccepted P1.21 SRA1-supply watchdog candidate.

P1.21 starts from P1.20. It removes ordinary KWD contacts from the credited
PNOZ input loops and instead puts both normally-open contacts in series with
only the downstream SRA1 A1 supply. SR1 and both E-stop channels remain direct
and independently powered. A successful watchdog dropout power-cycles SRA1,
so heartbeat recovery cannot restore its outputs without a new monitored ARM.
DF-01 remains an ordinary diagnostic with zero safety credit; PG-01 containment
continues to assume DF-01 stuck valid or otherwise failed to demand a stop.
"""

from __future__ import annotations

import shutil
import sys
import types
from pathlib import Path

from generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate import transformed_source as p120_source


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
    text = p120_source()
    replacements = [
        ('OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"', 'OUT = ROOT / "electrical" / "kicad" / "project-button-v3-p1.21-sra1-supply-watchdog-candidate"', "output path"),
        ('PROJECT = "project-button-v3-p1.20-watchdog-interlock-candidate"', 'PROJECT = "project-button-v3-p1.21-sra1-supply-watchdog-candidate"', "project name"),
        ('REV = "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE"', 'REV = "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE"', "revision"),
        ('PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 WATCHDOG-INTERLOCK CANDIDATE"', 'PROJECT_TITLE = "PROJECT BUTTON HR-V0 ELECTRICAL V3 SRA1-SUPPLY-WATCHDOG CANDIDATE"', "project title"),
        ('PROJECT_SUBTITLE = "P1.19 layout preserved; two ordinary watchdog contacts interrupt separate SRA1 input returns; zero safety credit."', 'PROJECT_SUBTITLE = "P1.20 layout preserved; ordinary watchdog contacts removed from PNOZ inputs and series-gate only SRA1 A1; zero safety credit."', "project subtitle"),
        ('''  (title_block (title "PB HR-V0 ELEC P1.20 - {sheet.number:02d}") (date "{DATE}") (rev "P1.20")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED INTERLOCK CANDIDATE"))''', '''  (title_block (title "PB HR-V0 ELEC P1.21 - {sheet.number:02d}") (date "{DATE}") (rev "P1.21")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED SRA1-SUPPLY CANDIDATE"))''', "child title block"),
        ('''  (title_block (title "PB HR-V0 ELEC P1.20 INDEX") (date "{DATE}") (rev "P1.20")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED INTERLOCK CANDIDATE"))''', '''  (title_block (title "PB HR-V0 ELEC P1.21 INDEX") (date "{DATE}") (rev "P1.21")
    (company "Project Button") (comment 1 "SEE FULL PRELIMINARY WARNING ABOVE") (comment 2 "UNACCEPTED SRA1-SUPPLY CANDIDATE"))''', "root title block"),
    ]
    for old, new, label in replacements:
        text = once(text, old, new, label)

    text = once(
        text,
        '''        pnoz("SR1", (210, 95), {"A1":"SAFETY_24V", "S11":"SR1_S11", "S12":"SR1_S12", "S21":"SR1_S21", "S22":"SR1_S22", "S34":"SR1_START_RETURN",
                                   "13":"SRA1_S11", "14":"SR1_OUT1_TO_KWD1", "23":"SRA1_S21", "24":"SR1_OUT2_TO_KWD2",
                                   "33":"INTENTIONALLY_UNUSED_SR1_33", "34":"INTENTIONALLY_UNUSED_SR1_34",
                                   "41":"SAFETY_24V", "42":"SR1_DIAG_NC", "Y32":"SR1_STATUS"},
             "First-stage E-stop eligibility relay; A1 remains powered independently of the ordinary watchdog."),''',
        '''        pnoz("SR1", (210, 95), {"A1":"SAFETY_24V", "S11":"SR1_S11", "S12":"SR1_S12", "S21":"SR1_S21", "S22":"SR1_S22", "S34":"SR1_START_RETURN",
                                   "13":"SRA1_S11", "14":"SRA1_S12", "23":"SRA1_S21", "24":"SRA1_S22",
                                   "33":"INTENTIONALLY_UNUSED_SR1_33", "34":"INTENTIONALLY_UNUSED_SR1_34",
                                   "41":"SAFETY_24V", "42":"SR1_DIAG_NC", "Y32":"SR1_STATUS"},
             "First-stage E-stop eligibility relay; all inputs, supply and outputs remain independent of the ordinary watchdog."),''',
        "SR1 terminal allocation",
    )

    text = once(
        text,
        '''        pnoz("SRA1", (82, 92), {"S11":"SRA1_S11", "S12":"SRA1_S12", "S21":"SRA1_S21", "S22":"SRA1_S22", "S34":"SRA1_START_RETURN",''',
        '''        pnoz("SRA1", (82, 92), {"A1":"SRA1_A1_WD_GATED", "S11":"SRA1_S11", "S12":"SRA1_S12", "S21":"SRA1_S21", "S22":"SRA1_S22", "S34":"SRA1_START_RETURN",''',
        "SRA1 A1 allocation",
    )

    kwd = '''        Component("KWD1", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD1", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD1", "A2", "DRIVER RETURN", "WD1_COIL_N", "left"),
                   pn("KWD1", "11", "SRA1 SUPPLY GATE IN", "SAFETY_24V", "left"), pn("KWD1", "14", "SRA1 SUPPLY GATE STAGE 1", "WD_SRA1_SUPPLY_INTERMEDIATE", "right"),
                   pn("KWD1", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD1_12", "right"), pn("KWD1", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD1", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD1_24", "right"), pn("KWD1", "22", "CH2 NC FEEDBACK", "WD1_NC_24V", "right")],
                  "PROPOSED - SRA1 SUPPLY-GATE APPLICATION/FMEA/RECEIVED VERIFICATION REQUIRED", "First ordinary diagnostic supply-gate stage. KWD1:11-14 is in series with KWD2 before only SRA1:A1. SR1 and both E-stop input loops remain independent. One welded contact is defeated by the other opening. Ordinary relay, not force-guided or safety-rated; no PL/SIL credit. Received identity, contact duty, protection, brownout and fault tests remain open.",
                  "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060",
                  "Phoenix Contact official product PDF generated 2026-08-11; data-maintenance date 2026-04-01. Item 2967060: 24 VDC coil, 18 mA typical, 5 V/10 mA minimum contact load and 15 A for 300 ms maximum inrush; exact switched-SRA1 application remains open.", (210, 72), 82),
        Component("KWD2", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD2", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD2", "A2", "DRIVER RETURN", "WD2_COIL_N", "left"),
                   pn("KWD2", "11", "SRA1 SUPPLY GATE STAGE 1", "WD_SRA1_SUPPLY_INTERMEDIATE", "left"), pn("KWD2", "14", "SRA1 A1 GATED SUPPLY", "SRA1_A1_WD_GATED", "right"),
                   pn("KWD2", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD2_12", "right"), pn("KWD2", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD2", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD2_24", "right"), pn("KWD2", "22", "CH2 NC FEEDBACK", "WD2_NC_24V", "right")],
                  "PROPOSED - SRA1 SUPPLY-GATE APPLICATION/FMEA/RECEIVED VERIFICATION REQUIRED", "Second ordinary diagnostic supply-gate stage. KWD2:11-14 completes the series path to SRA1:A1. A successful dropout removes SRA1 power; restored heartbeat can only repower SRA1, whose falling-edge monitored ARM must still be performed. Shared stuck-valid and dual-bypass failures lose DF-01 but cannot bypass direct SR1-controlled SRA1 inputs. No PL/SIL credit.",
                  "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060",
                  "Phoenix Contact official product PDF generated 2026-08-11; data-maintenance date 2026-04-01; manufacturer application acceptance and physical validation remain open.", (340, 72), 82),
'''
    text = between(text, '        Component("KWD1"', '        Component("S2"', kwd, "KWD component block")

    text = once(
        text,
        '"Heartbeat loss opens both SRA1 input returns while SR1 remains powered; recovery alone cannot restore the monitored ARM stage."',
        '"Heartbeat loss removes only SRA1 A1 through two series ordinary contacts; SR1 remains powered and direct. Repowered SRA1 still requires monitored ARM."',
        "sheet 02 note",
    )
    text = once(
        text,
        's3 = Sheet(3, "03_arm_watchdog_eligibility.kicad_sch", "Distinct ARM and dual-channel watchdog interlock",\n               "Separate ordinary KWD contacts interrupt the two SRA1 input returns; both stages retain zero safety credit.")',
        's3 = Sheet(3, "03_arm_watchdog_eligibility.kicad_sch", "Distinct ARM and SRA1 diagnostic supply gate",\n               "Two series ordinary KWD contacts gate only SRA1 A1; SR1 and both E-stop input loops remain independent.")',
        "sheet 03 title",
    )
    text = once(
        text,
        '''    s3.notes = ["After a successful watchdog dropout: cause healthy -> both KWD contacts restored -> SR1 remains SAFE_READY -> distinct monitored ARM press/release -> K1/K2 may energize.",
                "KWD1 interrupts SR1:14 to SRA1:S12 and KWD2 interrupts SR1:24 to SRA1:S22. One welded contact is defeated by the other opening; dual/common-cause failures remain hazardous and receive zero safety credit."]''',
        '''    s3.notes = ["After watchdog dropout: heartbeat healthy -> both KWD contacts restore SRA1 supply -> distinct monitored ARM press/release -> K1/K2 may become eligible. Heartbeat restoration alone must remain OFF.",
                "KWD1:11-14 and KWD2:11-14 series-gate only SRA1:A1. SR1 supply, S0 input returns and SR1-to-SRA1 input paths remain direct; DF-01 receives zero safety credit."]''',
        "sheet 03 notes",
    )
    text = text.replace(
        "Run the R232 watchdog-interlock candidate generator with `--validate`",
        "Run the R234 SRA1-supply-watchdog candidate generator with `--validate`",
    )
    text = text.replace(
        "KWD1:11-14 and KWD2:11-14 interrupt separate SRA1 input returns, not SR1 power or either S0 input loop.",
        "KWD1:11-14 and KWD2:11-14 series-gate only SRA1 A1; they do not touch SR1 supply, either S0 input loop, or the SR1-to-SRA1 input returns.",
    )
    text = once(
        text,
        "- Two separately driven ordinary watchdog relay contacts interrupt separate SRA1 input returns while SR1 remains powered independently. A successful heartbeat-loss dropout opens SRA1 outputs and therefore both contactor-coil paths; monitored ARM must be performed again before the contactors can return. Either single KWD 11-14 weld is defeated by the other channel opening. Dual weld/bypass, common controller/supply failure, input-contact application, protected routing, physical proof and qualified allocation remain open; the watchdog receives zero safety credit.",
        "- Two separately driven ordinary watchdog relay contacts series-gate only SRA1 A1 while SR1 and both E-stop loops remain powered and direct. A successful heartbeat-loss dropout power-cycles SRA1; heartbeat restoration can repower it but cannot close its outputs until the falling-edge monitored ARM sequence is performed. Either single KWD 11-14 weld is defeated by the other opening. Dual weld/bypass or shared stuck-valid failure loses only uncredited DF-01 and cannot bypass SR1-controlled SRA1 inputs. Supply switching, contact duty, protected routing, brownout/recovery, internal faults, physical proof and qualified allocation remain open; the watchdog receives zero safety credit.",
        "README topology summary",
    )
    return text


def main() -> int:
    name = "sra1_supply_watchdog_electrical_generator"
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
