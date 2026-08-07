"""Generate the connected Project Button HR-V0 Electrical V3 KiCad candidate.

The generator is the native editable source for the block-level wiring model.
It deliberately preserves unresolved terminals as ``TBD-*`` and selections as
``SELECTION REQUIRED``.  Passive schematic pins keep ERC scoped to modeled
connectivity; ERC is never treated as a safety approval.

PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import textwrap
import uuid
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "project-button-v3"
PROJECT = "project-button-v3"
REV = "V3-P1.1"
DATE = "2026-08-06"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
NS = uuid.UUID("4cb40c84-3194-4ded-b2c7-d78df616c5c0")


def uid(key: str) -> str:
    return str(uuid.uuid5(NS, key))


def esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def q(value: float) -> float:
    """Snap connection geometry to KiCad's 1.27 mm (50 mil) grid."""
    return round(value / 1.27) * 1.27


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    net: str
    side: str = "left"


@dataclass
class Component:
    ref: str
    value: str
    pins: list[Pin]
    status: str
    description: str
    datasheet: str = ""
    evidence: str = ""
    position: tuple[float, float] = (0.0, 0.0)
    width: float = 72.0
    height: float | None = None
    quantity: int = 1
    footprint: str = ""
    watchdog_pcb: bool = False

    def side_pins(self, side: str) -> list[Pin]:
        return [pin for pin in self.pins if pin.side == side]

    def box_height(self) -> float:
        if self.height is not None:
            return self.height
        count = max(len(self.side_pins("left")), len(self.side_pins("right")), 1)
        return max(25.4, count * 5.08 + 5.08)


@dataclass
class Sheet:
    number: int
    filename: str
    title: str
    purpose: str
    components: list[Component] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    sheet_uuid: str = ""
    compact: bool = False

    def __post_init__(self):
        if not self.sheet_uuid:
            self.sheet_uuid = uid(f"sheet:{self.filename}")


def pn(ref: str, number: str, name: str, net: str, side: str) -> Pin:
    return Pin(number=number, name=name, net=net, side=side)


PNOZ_PINS = [
    ("A1", "24V SUPPLY", "SAFETY_24V", "left"),
    ("A2", "0V SUPPLY", "SAFETY_0V", "left"),
    ("S11", "INPUT CH1 FEED", "", "left"),
    ("S12", "INPUT CH1 RETURN / START FEED", "", "left"),
    ("S21", "INPUT CH2 FEED", "", "left"),
    ("S22", "INPUT CH2 RETURN", "", "left"),
    ("S34", "START / EDM RETURN", "", "left"),
    ("13", "SAFETY OUT1 IN", "", "right"),
    ("14", "SAFETY OUT1 OUT", "", "right"),
    ("23", "SAFETY OUT2 IN", "", "right"),
    ("24", "SAFETY OUT2 OUT", "", "right"),
    ("33", "SAFETY OUT3 IN", "", "right"),
    ("34", "SAFETY OUT3 OUT", "", "right"),
    ("41", "AUX NC IN", "", "right"),
    ("42", "AUX NC OUT", "", "right"),
    ("Y32", "SEMICONDUCTOR STATUS", "", "right"),
]


def pnoz(ref: str, position: tuple[float, float], nets: dict[str, str], purpose: str) -> Component:
    pins = [pn(ref, number, name, nets.get(number, default), side)
            for number, name, default, side in PNOZ_PINS]
    return Component(
        ref=ref,
        value="Pilz PNOZ s4 24 VDC 3 n/o 1 n/c, order 750104",
        pins=pins,
        status="PROPOSED - QUALIFIED APPLICATION REVIEW REQUIRED",
        description=purpose + " Mode: short-cross detection plus monitored start on falling edge; seal and inspect selector with power removed.",
        datasheet="https://www.pilz.com/en-INT/eshop/product/750104",
        evidence="Pilz operating manual 21396-EN-23, product file 2026-06-22; terminals and timing rechecked 2026-08-06.",
        position=position,
        width=82.0,
    )


def sheets() -> list[Sheet]:
    s1 = Sheet(1, "01_external_sources.kicad_sch", "External listed sources and DC boundaries",
               "Factory-sealed adapters eliminate project-built mains wiring.")
    s1.components = [
        Component("PSA1", "Mean Well GST280A12-C6P, 12 V 21 A 252 W",
                  [pn("PSA1", "C6P-1", "+VO 1", "ACT_12V_RAW", "right"),
                   pn("PSA1", "C6P-2", "+VO 2", "ACT_12V_RAW", "right"),
                   pn("PSA1", "C6P-3", "+VO 3", "ACT_12V_RAW", "right"),
                   pn("PSA1", "C6P-4", "-VO 1", "ACT_0V_PE_BONDED", "right"),
                   pn("PSA1", "C6P-5", "-VO 2", "ACT_0V_PE_BONDED", "right"),
                   pn("PSA1", "C6P-6", "-VO 3", "ACT_0V_PE_BONDED", "right"),
                   pn("PSA1", "C14-L", "FACTORY AC L", "FACTORY_AC_L_ACT", "left"),
                   pn("PSA1", "C14-N", "FACTORY AC N", "FACTORY_AC_N_ACT", "left"),
                   pn("PSA1", "C14-PE", "FACTORY PE / INTERNAL -V BOND", "ACT_0V_PE_BONDED", "left")],
                  "PROPOSED - SOURCE APPLICATION REVIEW OPEN",
                  "External Class I adapter. Pins 1-3 are +Vo and 4-6 are -Vo; -Vo is bonded to incoming PE inside the source. Do not add a second 0V/PE bond.",
                  "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF",
                  "GST280A-SPEC 2026-04-03", (80, 82), 82),
        Component("JA1", "Molex 39012066 housing; 6x 444783112 HCS male contacts; 16 AWG",
                  [pn("J12V1", str(i), f"C6P {i}", "ACT_12V_RAW" if i <= 3 else "ACT_0V_PE_BONDED", "left") for i in range(1, 7)],
                  "PROPOSED - CONNECTOR SYSTEM FROZEN; HARNESS/THERMAL VERIFICATION REQUIRED",
                  "Mates the source's 39-01-2060-equivalent receptacle. Use six individual 16 AWG copper conductors, one per contact, and Molex tool 63819-0900. Pins 1-3 are +12 V and 4-6 are bonded 0 V. Do not hot-plug or use current sharing as a safety assumption.",
                  "https://www.molex.com/en-us/products/part-detail/39012066",
                  "Molex 5559 and 44478 series data accessed 2026-08-06; PS-44476-001 rev D dated 2003-06-12; ATS-638190900 rev H dated 2015-08-28. Six-contact 16 AWG HCS project-side screen is 21 A / 3 = 7 A per contact versus the published 11 A HCS guideline. The adapter-side contact construction and real current division are not published, so received-harness thermal, crimp and current-division tests remain mandatory.",
                  position=(210, 82), width=78),
        Component("PSU2", "Mean Well GST40A24-P1J, 24 V 1.67 A 40 W",
                  [pn("PS24A", "P1J-C", "CENTER +24V", "SAFETY_24V_RAW", "right"),
                   pn("PS24A", "P1J-S", "SLEEVE 0V", "SAFETY_0V", "right"),
                   pn("PS24A", "C14-L", "FACTORY AC L", "FACTORY_AC_L_CTL", "left"),
                   pn("PS24A", "C14-N", "FACTORY AC N", "FACTORY_AC_N_CTL", "left"),
                   pn("PS24A", "C14-PE", "FACTORY PE", "SITE_PE_CONTROL_SOURCE", "left")],
                  "PROPOSED - LOCKING DC INTERFACE OPEN",
                  "External Class I adapter. P1J is center-positive; output -V is not internally bonded to PE.",
                  "https://www.meanwell.com/Upload/PDF/GST40A/GST40A-SPEC.PDF",
                  "GST40A-SPEC 2026-04-03", (340, 82), 78),
        Component("JC1", "Locking 24 V DC inlet/interface",
                  [pn("J24V1", "TBD-24+", "+24V", "SAFETY_24V_RAW", "left"),
                   pn("J24V1", "TBD-24-", "0V", "SAFETY_0V", "left"),
                   pn("J24V1", "TBD-OUT+", "PROTECTED +24V", "SAFETY_24V", "right"),
                   pn("J24V1", "TBD-OUT-", "0V", "SAFETY_0V", "right")],
                  "SELECTION REQUIRED", "Add locking conversion, branch protection, strain relief and enclosure interface without exposing the non-locking barrel plug.", position=(80, 175), width=78),
        Component("PSU3", "Raspberry Pi 27W USB-C Power Supply US; color/SKU unresolved",
                  [pn("PS5A", "USB-C-VBUS", "+5V COMPUTE", "COMPUTE_5V", "right"),
                   pn("PS5A", "USB-C-GND", "COMPUTE GND", "COMPUTE_0V", "right"),
                   pn("PS5A", "AC-FACTORY", "FACTORY AC", "FACTORY_AC_COMPUTE", "left")],
                  "SELECTION REQUIRED - US SKU / COLOR / RETENTION", "Official US Type-A regional model is frozen. Raspberry Pi's current primary portal lists twelve family SKUs without mapping each SKU to region/color, so the exact order code must not be inferred. Compute remains powered for diagnostics during E-stop and has no safety authority.",
                  "https://pip-assets.raspberrypi.com/categories/898-raspberry-pi-27w-usb-c-power-supply",
                  "Raspberry Pi product brief RP-008245-DS-1, published October 2023 and portal-updated 2025-10-06; rechecked 2026-08-06.", position=(210, 175), width=78),
        Component("SP1", "Project-added DC 0V / PE star point",
                  [pn("SP1", "1", "ACTUATOR 0V", "INTENTIONALLY_NOT_CONNECTED_SP1_A", "left"),
                   pn("SP1", "2", "PE", "INTENTIONALLY_NOT_CONNECTED_SP1_B", "right")],
                  "DNP - PROHIBITED WITH GST280A12-C6P", "The source already bonds -V to PE. Do not fit SP1 or add a parallel robot-frame bond.", position=(340, 175), width=78),
    ]
    s1.notes = ["All AC conductors shown are factory boundaries, not project-built wiring.",
                "Site cords, receptacles, GFCI/code basis and source application review remain open."]

    s2 = Sheet(2, "02_estop_eligibility.kicad_sch", "Dual-channel E-stop and RESET eligibility",
               "Each SR1 input return contains one E-stop NC and one watchdog NO contact; RESET cannot energize K1/K2.")
    s2.components = [
        Component("S0", "IDEC XW1E-BV402M-R dual-NC E-stop candidate",
                  [pn("S0", "R-1", "CH1 RIGHT NC MARK 1", "SR1_S11", "left"), pn("S0", "R-2", "CH1 RIGHT NC MARK 2", "WD1_SAFETY_IN", "right"),
                   pn("S0", "L-1", "CH2 LEFT NC MARK 1", "SR1_S21", "left"), pn("S0", "L-2", "CH2 LEFT NC MARK 2", "WD2_SAFETY_IN", "right")],
                  "PROPOSED - TERMINAL POSITIONS FROZEN; RECEIVED VERIFICATION REQUIRED", "Candidate is documented as 40 mm mushroom, turn/pull reset, 2NC, screw terminal and terminal cover. With TOP up in the manufacturer bottom view, project channel 1 is the right NC pair marked 1-2 and channel 2 is the left NC pair marked 1-2. R-/L- prefixes are project-unique KiCad designators, not extra manufacturer markings. Verify orientation, markings and both positively opening NC channels on the received device before wiring.",
                  "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/emergency-stop-switches/xw-22mm-estop/xw1e-bv402m-r",
                  "IDEC XW product page plus XW-Indicator-Datasheet terminal arrangement, rechecked 2026-08-06; exact received device still requires bottom-view and continuity verification.", position=(75, 82), width=82),
        pnoz("SR1", (210, 95), {"S11":"SR1_S11", "S12":"SR1_S12", "S21":"SR1_S21", "S22":"SR1_S22", "S34":"SR1_START_RETURN",
                                   "13":"SRA1_S11", "14":"SRA1_S12", "23":"SRA1_S21", "24":"SRA1_S22",
                                   "33":"INTENTIONALLY_UNUSED_SR1_33", "34":"INTENTIONALLY_UNUSED_SR1_34",
                                   "41":"SAFETY_24V", "42":"SR1_DIAG_NC", "Y32":"SR1_STATUS"},
             "First-stage E-stop eligibility relay."),
        Component("S1", "IDEC HW1B-M1F10-B black momentary 1NO RESET",
                  [pn("S1", "TBD-R1", "RESET IN", "SR1_S12", "left"), pn("S1", "TBD-R2", "RESET OUT", "SR1_START_RETURN", "right")],
                  "PROPOSED - EXACT OPERATOR/COLOR FROZEN; RECEIVED VERIFICATION REQUIRED", "Exact black flush momentary 1NO screw-terminal operator is frozen for RESET. The panel shall carry the explicit RESET legend and remain outside the swept envelope. Panel spacing/guarding and physical contact-terminal mapping remain open; verify the received device by bottom-view record and continuity test.",
                  "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-b",
                  "IDEC US product page and HW Series Catalog_Screw dated 2026-07-23; rechecked 2026-08-06.", position=(340, 82), width=82),
        Component("H1", "SAFE ELIGIBLE indicator interface",
                  [pn("H1", "TBD-H+", "+", "SR1_STATUS", "left"), pn("H1", "TBD-H-", "-", "SAFETY_0V", "right")],
                  "SELECTION REQUIRED", "Diagnostic indicator only; no safety credit and no motion authority.", position=(75, 190), width=82),
    ]
    s2.notes = ["Each E-stop return passes through one watchdog NO contact before SR1; heartbeat loss therefore drops SR1.",
                "RESET release may make SR1 eligible, but SRA1 and K1/K2 remain de-energized until a later ARM.",
                "Unused SR1 outputs are explicitly named; do not bridge them during wiring."]

    s3 = Sheet(3, "03_arm_edm_contactors.kicad_sch", "Distinct ARM, watchdog channels, EDM and contactors",
               "SRA1 accepts ARM only after SR1 and both watchdog channels are healthy and K1/K2 mirror contacts prove open.")
    s3.components = [
        pnoz("SRA1", (82, 92), {"S11":"SRA1_S11", "S12":"SRA1_S12", "S21":"SRA1_S21", "S22":"SRA1_S22", "S34":"SRA1_START_RETURN",
                                     "13":"SAFETY_24V", "14":"SRA1_K1_RAW", "23":"SAFETY_24V", "24":"SRA1_K2_RAW",
                                     "33":"INTENTIONALLY_UNUSED_SRA1_33", "34":"INTENTIONALLY_UNUSED_SRA1_34",
                                     "41":"SAFETY_24V", "42":"SRA1_DIAG_NC", "Y32":"SRA1_STATUS"},
             "Final ARM and external-device-monitoring relay."),
        Component("KWD1", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD1", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD1", "A2", "DRIVER RETURN", "WD1_COIL_N", "left"),
                   pn("KWD1", "11", "CH1 COM", "WD1_SAFETY_IN", "left"), pn("KWD1", "14", "CH1 NO", "SR1_S12", "right"),
                   pn("KWD1", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD1_12", "right"), pn("KWD1", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD1", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD1_24", "right"), pn("KWD1", "22", "CH2 NC FEEDBACK", "WD1_NC_24V", "right")],
                  "PROPOSED - RECEIVED POLARITY/FMEA VERIFICATION REQUIRED", "First independent watchdog relay channel. Ordinary relay, not force-guided and not safety-rated; no PL/SIL credit. Received polarity, continuity and welded-contact tests remain open.",
                  "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf",
                  "Official product PDF generated 2026-08-04; data-maintenance date 2026-04-01. Circuit diagram identifies A1/A2, 11-12-14 and 21-22-24; 24 VDC, 18 mA typical, 8 ms pickup, 10 ms release.", (210, 72), 82),
        Component("KWD2", "Phoenix Contact PLC-RSC-24DC/21-21, item 2967060",
                  [pn("KWD2", "A1", "COIL +24V", "SAFETY_24V", "left"), pn("KWD2", "A2", "DRIVER RETURN", "WD2_COIL_N", "left"),
                   pn("KWD2", "11", "CH1 COM", "WD2_SAFETY_IN", "left"), pn("KWD2", "14", "CH1 NO", "SR1_S22", "right"),
                   pn("KWD2", "12", "CH1 NC UNUSED", "INTENTIONALLY_UNUSED_KWD2_12", "right"), pn("KWD2", "21", "CH2 COM +24V", "SAFETY_24V", "left"),
                   pn("KWD2", "24", "CH2 NO UNUSED", "INTENTIONALLY_UNUSED_KWD2_24", "right"), pn("KWD2", "22", "CH2 NC FEEDBACK", "WD2_NC_24V", "right")],
                  "PROPOSED - RECEIVED POLARITY/FMEA VERIFICATION REQUIRED", "Second independently driven watchdog relay channel; exact terminals follow the official circuit diagram, while received verification and common controller/supply failures remain open.",
                  "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf",
                  "Official product PDF generated 2026-08-04; data-maintenance date 2026-04-01.", (340, 72), 82),
        Component("S2", "IDEC HW1B-M1F10-G green momentary 1NO ARM",
                  [pn("S2", "TBD-A1", "ARM IN", "SRA1_S12", "left"), pn("S2", "TBD-A2", "ARM OUT", "ARM_AFTER_S2", "right")],
                  "PROPOSED - EXACT OPERATOR/COLOR FROZEN; RECEIVED VERIFICATION REQUIRED", "Exact green flush momentary 1NO screw-terminal operator is frozen for ARM, distinct from the black RESET operator. The panel shall carry the explicit ARM legend; spacing/guarding and physical contact-terminal mapping remain open. ARM must actuate and release after every safety dropout.",
                  "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-g",
                  "IDEC US product page and HW Series Catalog_Screw dated 2026-07-23; rechecked 2026-08-06.", position=(82, 205), width=82),
        Component("K1", "Schneider TeSys D LC1D25BD, 24 VDC coil",
                  [pn("K1", "A1", "COIL +", "K1_A1", "left"), pn("K1", "A2", "COIL -", "SAFETY_0V", "left"),
                   pn("K1", "21", "MIRROR NC IN", "ARM_AFTER_S2", "left"), pn("K1", "22", "MIRROR NC OUT", "EDM_K1_OUT", "right"),
                   pn("K1", "13", "AUX NO IN", "SAFETY_24V", "left"), pn("K1", "14", "AUX NO OUT", "K1_STATUS", "right")],
                  "PROPOSED - DC APPLICATION CONFIRMATION REQUIRED", "First redundant series contactor. BD coil has built-in bidirectional peak-limiting diode; do not add assumed external suppression.",
                  "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", "Schneider product sheet rechecked 2026-08-06; loaded DC interruption/coordination not established.", (210, 205), 82),
        Component("K2", "Schneider TeSys D LC1D25BD, 24 VDC coil",
                  [pn("K2", "A1", "COIL +", "K2_A1", "left"), pn("K2", "A2", "COIL -", "SAFETY_0V", "left"),
                   pn("K2", "21", "MIRROR NC IN", "EDM_K1_OUT", "left"), pn("K2", "22", "MIRROR NC OUT", "SRA1_START_RETURN", "right"),
                   pn("K2", "13", "AUX NO IN", "SAFETY_24V", "left"), pn("K2", "14", "AUX NO OUT", "K2_STATUS", "right")],
                  "PROPOSED - DC APPLICATION CONFIRMATION REQUIRED", "Second redundant series contactor.",
                  "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", position=(340, 205), width=82),
        Component("FSR1", "SRA1 output-contact protection for K1 coil",
                  [pn("FSR1", "1", "IN", "SRA1_K1_RAW", "left"), pn("FSR1", "2", "OUT", "K1_A1", "right")],
                  "SELECTION REQUIRED", "Select from fault current, coil transient, conductor and PNOZ contact-protection limits; published maxima are not selections.", position=(145, 255), width=72),
        Component("FSR2", "SRA1 output-contact protection for K2 coil",
                  [pn("FSR2", "1", "IN", "SRA1_K2_RAW", "left"), pn("FSR2", "2", "OUT", "K2_A1", "right")],
                  "SELECTION REQUIRED", "Same coordination gate as FSR1.", position=(275, 255), width=72),
    ]
    s3.notes = ["Required sequence after E-stop or watchdog dropout: cause healthy -> RESET press/release -> SAFE_READY -> distinct ARM press/release -> K1/K2 may energize.",
                "Heartbeat restoration closes only KWD contacts; SR1 remains in monitored-start state until RESET."]

    s4 = Sheet(4, "04_actuator_distribution.kicad_sch", "Redundant 12 V interruption and separately protected actuator branches",
               "No branch fuse, conductor, connector or service disconnect is released without fault-current and harness evidence.")
    s4.components = [
        Component("F0", "12 V source protection",
                  [pn("F0", "1", "SOURCE", "ACT_12V_RAW", "left"), pn("F0", "2", "PROTECTED", "ACT_12V_FUSED", "right")],
                  "SELECTION REQUIRED", "Fuse/holder family, rating, interrupting capacity and thermal coordination remain open.", position=(65, 70), width=72),
        Component("SD1", "Accessible DC service disconnect",
                  [pn("SD1", "TBD-IN", "IN", "ACT_12V_FUSED", "left"), pn("SD1", "TBD-OUT", "OUT", "K1_P1_IN", "right")],
                  "SELECTION REQUIRED", "Select a DC-rated lockable disconnect with exact terminals, enclosure and current/fault rating.", position=(180, 70), width=72),
        Component("KP1", "K1 three main poles represented in series",
                  [pn("K1P", "1L1", "POLE1 IN", "K1_P1_IN", "left"), pn("K1P", "2T1", "POLE1 OUT", "K1_J12", "right"),
                   pn("K1P", "3L2", "POLE2 IN", "K1_J12", "left"), pn("K1P", "4T2", "POLE2 OUT", "K1_J23", "right"),
                   pn("K1P", "5L3", "POLE3 IN", "K1_J23", "left"), pn("K1P", "6T3", "POLE3 OUT", "K1_OUT", "right")],
                  "CONTACT CROSS-REFERENCE ONLY - SAME DEVICE K1", "Do not count as a second BOM device. External nets series-connect the three poles; Schneider application confirmation remains required.", position=(295, 70), width=82, quantity=0),
        Component("KP2", "K2 three main poles represented in series",
                  [pn("K2P", "1L1", "POLE1 IN", "K1_OUT", "left"), pn("K2P", "2T1", "POLE1 OUT", "K2_J12", "right"),
                   pn("K2P", "3L2", "POLE2 IN", "K2_J12", "left"), pn("K2P", "4T2", "POLE2 OUT", "K2_J23", "right"),
                   pn("K2P", "5L3", "POLE3 IN", "K2_J23", "left"), pn("K2P", "6T3", "POLE3 OUT", "ACT_12V_BUS", "right")],
                  "CONTACT CROSS-REFERENCE ONLY - SAME DEVICE K2", "Do not count as a second BOM device.", position=(65, 155), width=82, quantity=0),
        Component("F1", "J1 shoulder branch protection", [pn("F1", "1", "IN", "ACT_12V_BUS", "left"), pn("F1", "2", "OUT", "J1_VDD", "right")],
                  "SELECTION REQUIRED", "Requires fault current, cable, connector, inrush, regeneration, duty and ambient evidence.", position=(180, 145), width=72),
        Component("F2", "J2 elbow branch protection", [pn("F2", "1", "IN", "ACT_12V_BUS", "left"), pn("F2", "2", "OUT", "J2_VDD", "right")],
                  "SELECTION REQUIRED", "Same evidence gate as F1.", position=(295, 145), width=72),
        Component("F3", "Gripper branch protection", [pn("F3", "1", "IN", "ACT_12V_BUS", "left"), pn("F3", "2", "OUT", "J3_VDD", "right")],
                  "SELECTION REQUIRED", "Same evidence gate as F1.", position=(65, 230), width=72),
        Component("INJ1", "J1 data/power injection module",
                  [pn("INJ1", "TBD-BI-G", "BUS IN GND", "ACT_0V_PE_BONDED", "left"), pn("INJ1", "TBD-BI-D", "BUS IN DATA", "DXL_TTL_DATA", "left"),
                   pn("INJ1", "TBD-P", "FUSED VDD", "J1_VDD", "left"), pn("INJ1", "TBD-A-G", "ACT GND", "ACT_0V_PE_BONDED", "right"),
                   pn("INJ1", "TBD-A-V", "ACT VDD", "J1_VDD", "right"), pn("INJ1", "TBD-A-D", "ACT DATA", "DXL_TTL_DATA", "right"),
                   pn("INJ1", "TBD-BO-G", "BUS OUT GND", "ACT_0V_PE_BONDED", "right"), pn("INJ1", "TBD-BO-D", "BUS OUT DATA", "DXL_TTL_DATA", "right")],
                  "DESIGN REQUIRED", "Custom inline module omits VDD on inter-actuator bus cables so protected branches cannot backfeed. PCB/harness design and tests open.", position=(180, 230), width=82),
        Component("INJ2", "J2 data/power injection module",
                  [pn("INJ2", "TBD-BI-G", "BUS IN GND", "ACT_0V_PE_BONDED", "left"), pn("INJ2", "TBD-BI-D", "BUS IN DATA", "DXL_TTL_DATA", "left"),
                   pn("INJ2", "TBD-P", "FUSED VDD", "J2_VDD", "left"), pn("INJ2", "TBD-A-G", "ACT GND", "ACT_0V_PE_BONDED", "right"),
                   pn("INJ2", "TBD-A-V", "ACT VDD", "J2_VDD", "right"), pn("INJ2", "TBD-A-D", "ACT DATA", "DXL_TTL_DATA", "right"),
                   pn("INJ2", "TBD-BO-G", "BUS OUT GND", "ACT_0V_PE_BONDED", "right"), pn("INJ2", "TBD-BO-D", "BUS OUT DATA", "DXL_TTL_DATA", "right")],
                  "DESIGN REQUIRED", "Second injection module.", position=(295, 230), width=82),
    ]
    s4.notes = ["Series jumpers: K1 2T1->3L2, 4T2->5L3, 6T3->K2 1L1; repeat through K2 to ACT_12V_BUS.",
                "INJ3 and exact actuator connectors continue on the harness sheet; U2D2 Power Hub is excluded from actuator current."]

    s5 = Sheet(5, "05_watchdog_control.kicad_sch", "Independent watchdog controller and two relay drivers",
               "Ordinary controller/relays provide diagnostics and restart forcing but receive no safety integrity credit by assertion.")
    s5.components = [
        Component("DC1", "TRACO POWER TSR 1-2450, 24 V to 5 V 1 A non-isolated",
                  [pn("DC1", "1", "+VIN", "SAFETY_24V", "left"),
                   pn("DC1", "2", "GND", "SAFETY_0V", "left"),
                   pn("DC1", "3", "+VOUT 5V", "WD_5V", "right")],
                  "PROPOSED - ORDER CODE/PINOUT FROZEN; BROWNOUT/EMC/THERMAL VERIFICATION REQUIRED",
                  "Pin 1 +Vin, pin 2 common GND, pin 3 +Vout. Non-isolated by design; changing isolation requires a new driver/interface and grounding review. Published input range is 6.5-36 VDC; external capacitance is not required below 32 V, but branch protection, load budget, startup, brownout, conducted/radiated emissions and enclosure thermal tests remain open.",
                  "https://www.tracopower.com/tsr1-datasheet",
                  "TRACO POWER TSR 1 Series datasheet dated 2024-02-07, accessed 2026-08-06.", position=(65, 80), width=82,
                  footprint="Converter_DCDC:Converter_DCDC_TRACO_TSR-1_THT"),
        Component("ISO1", "Vishay VO618A-4X017T heartbeat optocoupler",
                  [pn("ISO1", "1", "ANODE", "HB_LED_A", "left"),
                   pn("ISO1", "2", "CATHODE", "COMPUTE_0V", "left"),
                   pn("ISO1", "3", "EMITTER", "SAFETY_0V", "right"),
                   pn("ISO1", "4", "COLLECTOR", "WD_HEARTBEAT", "right")],
                  "PROPOSED - ORDER CODE/PINOUT FROZEN; PCB/HIL/FAULT VERIFICATION REQUIRED",
                  "Ordinary signal isolation only; no safety-integrity credit. Verify received identity, PCB creepage/clearance, GPIO levels, LED current, edge timing, leakage, EMC, brownout and open/short faults in the released assembly.",
                  "https://www.vishay.com/docs/83432/vo618a.pdf",
                  "Vishay document 83432, VO618A datasheet Rev. 2.1 dated 2025-01-22, accessed 2026-08-06.", position=(180, 80), width=82,
                  footprint="PBV3_Footprints:VO618A_Option7_SMD"),
        Component("RHB1", "Panasonic ERJ6ENF9100V, 910 Ohm 1% 0805 0.125 W",
                  [pn("RHB1", "1", "GPIO SIDE", "PI_HEARTBEAT", "left"),
                   pn("RHB1", "2", "LED ANODE SIDE", "HB_LED_A", "right")],
                  "PROPOSED - ORDER CODE FROZEN; PCB/HIL VERIFICATION REQUIRED",
                  "Screens approximately 1.04 mA at a project 2.6 V GPIO-high floor and 1.65 V LED maximum, and 2.53 mA at 3.3 V with 1.0 V LED minimum. The 2.6 V floor is a project screen, not a released Raspberry Pi 5 guarantee; measure the actual source across load and temperature.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF9100V",
                  "Panasonic ERJ6ENF9100V current product page and specification, accessed 2026-08-06.", position=(180, 130), width=82,
                  footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("RHP1", "Panasonic ERJ6ENF1002V, 10.0 kOhm 1% 0805 0.125 W",
                  [pn("RHP1", "1", "PULLUP SUPPLY", "WD_3V3", "left"),
                   pn("RHP1", "2", "HEARTBEAT NODE", "WD_HEARTBEAT", "right")],
                  "PROPOSED - ORDER CODE FROZEN; PCB/HIL VERIFICATION REQUIRED",
                  "The 10 kOhm pullup draws 0.33 mA at 3.3 V. Confirm logic thresholds, leakage, power sequencing, waveform rise/fall time and fault response on the released PCB.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V",
                  "Panasonic ERJ6ENF1002V current product page and specification, accessed 2026-08-06.", position=(180, 180), width=82,
                  footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("WDCTRL1", "Raspberry Pi Pico 1, order SC0915 / RP2040",
                  [pn("WDCTRL1", "39", "VSYS 5V INPUT", "WD_5V", "left"), pn("WDCTRL1", "38", "GROUND", "SAFETY_0V", "left"),
                   pn("WDCTRL1", "36", "3V3 OUTPUT", "WD_3V3", "left"), pn("WDCTRL1", "4", "GP2 HEARTBEAT IN", "WD_HEARTBEAT", "left"),
                   pn("WDCTRL1", "5", "GP3 RELAY1 DRIVE", "WD1_DRIVE", "right"), pn("WDCTRL1", "6", "GP4 RELAY2 DRIVE", "WD2_DRIVE", "right"),
                   pn("WDCTRL1", "9", "GP6 RELAY1 FEEDBACK", "WD1_NC_DIAG", "right"), pn("WDCTRL1", "10", "GP7 RELAY2 FEEDBACK", "WD2_NC_DIAG", "right"),
                   pn("WDCTRL1", "D3", "SWDIO", "WD_SWDIO", "right"), pn("WDCTRL1", "D1", "SWCLK", "WD_SWCLK", "right"),
                   pn("WDCTRL1", "D2", "DEBUG GROUND", "SAFETY_0V", "right")],
                  "PROPOSED - GPIO FROZEN; PLATFORM RELEASE OPEN", "Monotonic heartbeat monitor. Physical GPIO candidates are frozen for review; platform startup, external bias, compilation, HIL and shared failures remain open and receive no safety credit.",
                  "https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf", "Official Pico datasheet and current pinout documentation rechecked 2026-08-06.", (300, 80), 82,
                  footprint="Module:RaspberryPi_Pico_SMD"),
        Component("UDRV1", "Texas Instruments TPL7407LPWR channel-1 relay driver",
                  [pn("UDRV1", "1", "IN1", "WD1_DRIVE", "left"),
                   pn("UDRV1", "2", "IN2 TIED LOW", "SAFETY_0V", "left"), pn("UDRV1", "3", "IN3 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV1", "4", "IN4 TIED LOW", "SAFETY_0V", "left"), pn("UDRV1", "5", "IN5 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV1", "6", "IN6 TIED LOW", "SAFETY_0V", "left"), pn("UDRV1", "7", "IN7 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV1", "8", "GND", "SAFETY_0V", "left"), pn("UDRV1", "9", "COM", "SAFETY_24V", "left"),
                   pn("UDRV1", "10", "OUT7 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_10", "right"), pn("UDRV1", "11", "OUT6 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_11", "right"),
                   pn("UDRV1", "12", "OUT5 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_12", "right"), pn("UDRV1", "13", "OUT4 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_13", "right"),
                   pn("UDRV1", "14", "OUT3 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_14", "right"), pn("UDRV1", "15", "OUT2 UNUSED", "INTENTIONALLY_UNUSED_UDRV1_15", "right"),
                   pn("UDRV1", "16", "OUT1 COIL RETURN", "WD1_COIL_N", "right")],
                  "PROPOSED - ORDER CODE/PINOUT FROZEN; PCB/HIL/FAULT VERIFICATION REQUIRED",
                  "Dedicated package for channel 1. COM is tied to the 24 V coil rail for the internal clamp; unused inputs are tied low and unused outputs are no-connect. Default-off, hot-plug/COM slew, clamp interaction with the relay module, thermal, brownout, open/short and cross-channel faults remain open.",
                  "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf",
                  "TI TPL7407L datasheet SLRS066D, revised 2016-03; TPL7407LPWR active orderable status checked 2026-08-06.", position=(95, 190), width=82,
                  footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm"),
        Component("UDRV2", "Texas Instruments TPL7407LPWR channel-2 relay driver",
                  [pn("UDRV2", "1", "IN1", "WD2_DRIVE", "left"),
                   pn("UDRV2", "2", "IN2 TIED LOW", "SAFETY_0V", "left"), pn("UDRV2", "3", "IN3 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV2", "4", "IN4 TIED LOW", "SAFETY_0V", "left"), pn("UDRV2", "5", "IN5 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV2", "6", "IN6 TIED LOW", "SAFETY_0V", "left"), pn("UDRV2", "7", "IN7 TIED LOW", "SAFETY_0V", "left"),
                   pn("UDRV2", "8", "GND", "SAFETY_0V", "left"), pn("UDRV2", "9", "COM", "SAFETY_24V", "left"),
                   pn("UDRV2", "10", "OUT7 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_10", "right"), pn("UDRV2", "11", "OUT6 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_11", "right"),
                   pn("UDRV2", "12", "OUT5 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_12", "right"), pn("UDRV2", "13", "OUT4 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_13", "right"),
                   pn("UDRV2", "14", "OUT3 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_14", "right"), pn("UDRV2", "15", "OUT2 UNUSED", "INTENTIONALLY_UNUSED_UDRV2_15", "right"),
                   pn("UDRV2", "16", "OUT1 COIL RETURN", "WD2_COIL_N", "right")],
                  "PROPOSED - ORDER CODE/PINOUT FROZEN; PCB/HIL/FAULT VERIFICATION REQUIRED",
                  "Separate package for channel 2 to avoid one driver-package fault controlling both coils. The controller, supplies, clock and firmware remain common causes; no safety credit is claimed.",
                  "https://www.ti.com/lit/ds/symlink/tpl7407l.pdf",
                  "TI TPL7407L datasheet SLRS066D, revised 2016-03; TPL7407LPWR active orderable status checked 2026-08-06.", position=(210, 190), width=82,
                  footprint="Package_SO:TSSOP-16_4.4x5mm_P0.65mm"),
        Component("CDRV1", "Murata GRM21BR71H104KA01L, 100 nF 50 V X7R 0805",
                  [pn("CDRV1", "1", "COM RAIL", "SAFETY_24V", "left"), pn("CDRV1", "2", "RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - ORDER CODE FROZEN; COM-SLEW/PCB VERIFICATION REQUIRED",
                  "Local COM bypass candidate for UDRV1. Capacitance alone does not prove TI's less-than-0.5 V/us COM slew requirement; scope hot-plug and repetitive transients in the released layout.",
                  "https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810",
                  "Murata GRM21BR71H104KA01L official specification asset, updated 2025 and accessed 2026-08-06.", position=(95, 245), width=82,
                  footprint="Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"),
        Component("CDRV2", "Murata GRM21BR71H104KA01L, 100 nF 50 V X7R 0805",
                  [pn("CDRV2", "1", "COM RAIL", "SAFETY_24V", "left"), pn("CDRV2", "2", "RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - ORDER CODE FROZEN; COM-SLEW/PCB VERIFICATION REQUIRED",
                  "Local COM bypass candidate for UDRV2; the same physical slew and fault evidence remains mandatory.",
                  "https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810",
                  "Murata GRM21BR71H104KA01L official specification asset, updated 2025 and accessed 2026-08-06.", position=(210, 245), width=82,
                  footprint="Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"),
        Component("UFB1", "Texas Instruments ISO1212DBQ dual 24 V input receiver",
                  [pn("UFB1", "1", "GND1", "SAFETY_0V", "left"), pn("UFB1", "2", "VCC1", "WD_3V3", "left"),
                   pn("UFB1", "3", "EN TIED HIGH", "WD_3V3", "left"), pn("UFB1", "4", "OUT1", "UFB_OUT1", "right"),
                   pn("UFB1", "5", "OUT2", "UFB_OUT2", "right"), pn("UFB1", "6", "NC", "INTENTIONALLY_UNUSED_UFB1_6", "right"),
                   pn("UFB1", "7", "NC", "INTENTIONALLY_UNUSED_UFB1_7", "right"), pn("UFB1", "8", "GND1", "SAFETY_0V", "left"),
                   pn("UFB1", "9", "FGND2", "SAFETY_0V", "left"), pn("UFB1", "10", "IN2", "FB_IN2", "left"),
                   pn("UFB1", "11", "SENSE2", "FB_SENSE2", "left"), pn("UFB1", "12", "SUB2 FLOAT", "INTENTIONALLY_UNUSED_UFB1_12", "right"),
                   pn("UFB1", "13", "SUB1 FLOAT", "INTENTIONALLY_UNUSED_UFB1_13", "right"), pn("UFB1", "14", "FGND1", "SAFETY_0V", "left"),
                   pn("UFB1", "15", "IN1", "FB_IN1", "left"), pn("UFB1", "16", "SENSE1", "FB_SENSE1", "left")],
                  "PROPOSED - PCB/EMC VERIFICATION REQUIRED", "Exact dual-channel receiver candidate. Logic and field grounds both return to SAFETY_0V in this non-isolated system, so no galvanic-isolation or safety-integrity credit is claimed. Layout, thermal, EMC, fault-injection and received-part tests remain open.",
                  "https://www.ti.com/lit/ds/symlink/iso1211.pdf", "TI ISO1211/ISO1212 datasheet SLLSEY7G, revised February 2025; ISO1212DBQ active tube orderable confirmed 2026-08-06.", position=(205, 115), width=82,
                  footprint="Package_SO:SSOP-16_3.9x4.9mm_P0.635mm"),
        Component("RTH1", "Vishay MMA02040C1001FB300, 1.00 kOhm 1% 0.4 W MELF",
                  [pn("RTH1", "1", "FIELD INPUT", "WD1_NC_24V", "left"), pn("RTH1", "2", "SENSE", "FB_SENSE1", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/PULSE/THERMAL", "Exact order code frozen. Exact MELF candidate for TI Type-3 threshold/surge limiting. Screened steady loss is 7.6 mW at 2.75 mA; PCB land pattern, pulse/surge, temperature and enclosure derating still require release evidence.",
                  "https://www.vishay.com/docs/28963/mmu0102_mma0204_mmb0207.pdf", "Vishay document 28963, revision 2026-06-02; MMA0204 order-code construction and 0.4 W power-mode rating checked 2026-08-06.", position=(55, 60), width=50, footprint="Resistor_SMD:R_MiniMELF_MMA-0204"),
        Component("RSN1", "Panasonic ERJ6ENF5620V, 562 Ohm 1% 0805",
                  [pn("RSN1", "1", "SENSE", "FB_SENSE1", "left"), pn("RSN1", "2", "IN", "FB_IN1", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/THERMAL/FAULT", "Exact order code frozen. Exact 0.125 W candidate for TI current-limit resistor between SENSE1 and IN1. Screened steady loss is 4.3 mW at 2.75 mA; layout, tolerance and fault evidence remain open.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF5620V", "Panasonic current product page, 562 ohm 1%, 0805, 0.125 W; accessed 2026-08-06.", position=(55, 120), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("CFI1", "TDK CGA3E2X7R1H103K080AA, 10 nF 50 V X7R 0603",
                  [pn("CFI1", "1", "SENSE", "FB_SENSE1", "left"), pn("CFI1", "2", "FIELD RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: DC-BIAS/PCB/EMC", "Exact order code frozen. Exact AEC-Q200 X7R candidate for TI Type-3 input filter. Nominal value is not credited at 24.6 V until DC-bias, tolerance, temperature and received-board capacitance are verified; locate at UFB1.",
                  "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E2X7R1H103K080AA", "TDK current product page: production, 10 nF +/-10%, 50 VDC, X7R, 0603, -55 to 125 C; accessed 2026-08-06.", position=(55, 180), width=50, footprint="Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"),
        Component("RW1", "Vishay CRCW12102K70FKEA, 2.70 kOhm 1% 0.5 W 1210",
                  [pn("RW1", "1", "FIELD INPUT", "WD1_NC_24V", "left"), pn("RW1", "2", "FIELD RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/PULSE/THERMAL", "Exact order code frozen. Exact 0.5 W candidate for the parallel wetting load. Worst screened steady loss is 0.226 W, 45.2% of the 70 C rating; PCB/enclosure temperature, pulse and fault derating remain open.",
                  "https://www.vishay.com/docs/20035/dcrcwe3.pdf", "Vishay document 20035, revision 2026-04-14; CRCW1210 0.5 W rating and order-code construction checked 2026-08-06.", position=(55, 225), width=50, footprint="Resistor_SMD:R_1210_3225Metric_Pad1.30x2.65mm_HandSolder"),
        Component("RTH2", "Vishay MMA02040C1001FB300, 1.00 kOhm 1% 0.4 W MELF",
                  [pn("RTH2", "1", "FIELD INPUT", "WD2_NC_24V", "left"), pn("RTH2", "2", "SENSE", "FB_SENSE2", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/PULSE/THERMAL", "Exact order code frozen. Same exact threshold/surge candidate and open physical evidence as channel 1.",
                  "https://www.vishay.com/docs/28963/mmu0102_mma0204_mmb0207.pdf", "Vishay document 28963, revision 2026-06-02; checked 2026-08-06.", position=(355, 60), width=50, footprint="Resistor_SMD:R_MiniMELF_MMA-0204"),
        Component("RSN2", "Panasonic ERJ6ENF5620V, 562 Ohm 1% 0805",
                  [pn("RSN2", "1", "SENSE", "FB_SENSE2", "left"), pn("RSN2", "2", "IN", "FB_IN2", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/THERMAL/FAULT", "Exact order code frozen. Same exact current-limit candidate and open physical evidence as channel 1.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF5620V", "Panasonic current product page; accessed 2026-08-06.", position=(355, 120), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("CFI2", "TDK CGA3E2X7R1H103K080AA, 10 nF 50 V X7R 0603",
                  [pn("CFI2", "1", "SENSE", "FB_SENSE2", "left"), pn("CFI2", "2", "FIELD RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: DC-BIAS/PCB/EMC", "Exact order code frozen. Same exact input-filter candidate and open DC-bias/physical evidence as channel 1.",
                  "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E2X7R1H103K080AA", "TDK current production page; accessed 2026-08-06.", position=(355, 180), width=50, footprint="Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"),
        Component("RW2", "Vishay CRCW12102K70FKEA, 2.70 kOhm 1% 0.5 W 1210",
                  [pn("RW2", "1", "FIELD INPUT", "WD2_NC_24V", "left"), pn("RW2", "2", "FIELD RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/PULSE/THERMAL", "Exact order code frozen. Same exact wetting-load candidate and open physical evidence as channel 1.",
                  "https://www.vishay.com/docs/20035/dcrcwe3.pdf", "Vishay document 20035, revision 2026-04-14; checked 2026-08-06.", position=(355, 225), width=50, footprint="Resistor_SMD:R_1210_3225Metric_Pad1.30x2.65mm_HandSolder"),
        Component("CDEC1", "Murata GRM21BR71H104KA01L, 100 nF 50 V X7R 0805",
                  [pn("CDEC1", "1", "3V3", "WD_3V3", "left"), pn("CDEC1", "2", "GND1", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/PLACEMENT", "Exact order code frozen. Exact 0805 candidate required at UFB1 VCC1/GND1; placement within 2 mm, land pattern and received-board capacitance remain open.",
                  "https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810", "Murata official GRM21BR71H104KA01L specification asset, updated 2025 and accessed 2026-08-06.", position=(140, 190), width=50, footprint="Capacitor_SMD:C_0805_2012Metric"),
        Component("RSO1", "Panasonic ERJ6ENF1001V, 1.00 kOhm 1% 0805",
                  [pn("RSO1", "1", "RECEIVER OUT", "UFB_OUT1", "left"), pn("RSO1", "2", "PICO INPUT", "WD1_NC_DIAG", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/FAULT", "Exact order code frozen. Exact 0.125 W series candidate. A 3.3 V contention screen is 10.9 mW; it does not make contention safe or provide isolation.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1001V", "Panasonic current product page, 1 kilohm 1%, 0805, 0.125 W; accessed 2026-08-06.", position=(220, 190), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("RSO2", "Panasonic ERJ6ENF1001V, 1.00 kOhm 1% 0805",
                  [pn("RSO2", "1", "RECEIVER OUT", "UFB_OUT2", "left"), pn("RSO2", "2", "PICO INPUT", "WD2_NC_DIAG", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/FAULT", "Exact order code frozen. Same exact output-series candidate and open fault evidence as channel 1.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1001V", "Panasonic current product page; accessed 2026-08-06.", position=(300, 190), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("RPD1", "Panasonic ERJ6ENF1002V, 10.0 kOhm 1% 0805",
                  [pn("RPD1", "1", "PICO INPUT", "WD1_NC_DIAG", "left"), pn("RPD1", "2", "LOGIC RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/BROWNOUT/FAULT", "Exact order code frozen. Exact 0.125 W default-low candidate. It biases the GPIO low during high impedance; the documented VCC1 brownout region remains a fault-injection/HIL case. Firmware treats raw high as NC closed.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V", "Panasonic current product page, 10 kilohm 1%, 0805, 0.125 W; accessed 2026-08-06.", position=(220, 230), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("RPD2", "Panasonic ERJ6ENF1002V, 10.0 kOhm 1% 0805",
                  [pn("RPD2", "1", "PICO INPUT", "WD2_NC_DIAG", "left"), pn("RPD2", "2", "LOGIC RETURN", "SAFETY_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED: PCB/BROWNOUT/FAULT", "Exact order code frozen. Same exact default-low candidate and open physical evidence as channel 1.",
                  "https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V", "Panasonic current product page; accessed 2026-08-06.", position=(300, 230), width=50, footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"),
        Component("JDBG1", "Watchdog programming/debug connector",
                  [pn("JDBG1", "TBD-SWDIO", "SWDIO", "WD_SWDIO", "left"), pn("JDBG1", "TBD-SWCLK", "SWCLK", "WD_SWCLK", "left"),
                   pn("JDBG1", "TBD-GND", "GND", "SAFETY_0V", "left")],
                  "SELECTION REQUIRED", "Tool-only interface; must not enable or bypass outputs during operation.", position=(325, 190), width=82),
        Component("PI1", "Raspberry Pi 5 8GB high-level compute",
                  [pn("PI1", "USB-C-VBUS", "+5V INPUT", "COMPUTE_5V", "left"), pn("PI1", "GND", "COMPUTE GND", "COMPUTE_0V", "left"),
                   pn("PI1", "TBD-GPIO-HB", "HEARTBEAT OUT", "PI_HEARTBEAT", "right"), pn("PI1", "USB-U2D2", "USB TO U2D2", "PI_USB_U2D2", "right")],
                  "PROPOSED - GPIO/CABLE/RETENTION OPEN", "High-level compute and logger. It never owns the hardware safety function or directly restores contactors.",
                  "https://www.raspberrypi.com/products/raspberry-pi-5/", position=(325, 245), width=82),
    ]
    s5.notes = ["Power-up, brownout, clock failure, stuck GPIO, held heartbeat and firmware-corruption tests are mandatory.",
                "A qualified review must decide whether watchdog loss is credited or only diagnostic."]

    s6 = Sheet(6, "06_harness_interfaces.kicad_sch", "HR-V0 connectors, injection modules and terminal schedule",
               "Every TBD terminal remains a fabrication blocker; connector orientation must be checked on received parts.")
    s6.components = [
        Component("U1", "ROBOTIS U2D2 TTL interface, SKU 902-0132-000",
                  [pn("U2D2", "TTL-1", "GND", "ACT_0V_PE_BONDED", "right"), pn("U2D2", "TTL-2", "VDD OMITTED", "INTENTIONALLY_UNUSED_U2D2_VDD", "right"),
                   pn("U2D2", "TTL-3", "DATA", "DXL_TTL_DATA", "right"), pn("U2D2", "USB", "USB TO PI", "PI_USB_U2D2", "left")],
                  "PROPOSED - CUSTOM DATA-ONLY HARNESS REQUIRED", "Pin 2 VDD is intentionally omitted from the project cable. Standard fully populated cables are prohibited in the protected-branch topology.",
                  "https://emanual.robotis.com/docs/en/parts/interface/u2d2/", position=(65, 75), width=82),
        Component("INJ3", "Gripper data/power injection module",
                  [pn("INJ3", "TBD-BI-G", "BUS IN GND", "ACT_0V_PE_BONDED", "left"), pn("INJ3", "TBD-BI-D", "BUS IN DATA", "DXL_TTL_DATA", "left"),
                   pn("INJ3", "TBD-P", "FUSED VDD", "J3_VDD", "left"), pn("INJ3", "TBD-A-G", "ACT GND", "ACT_0V_PE_BONDED", "right"),
                   pn("INJ3", "TBD-A-V", "ACT VDD", "J3_VDD", "right"), pn("INJ3", "TBD-A-D", "ACT DATA", "DXL_TTL_DATA", "right")],
                  "DESIGN REQUIRED", "Final inline injection module; no VDD conductor continues beyond the actuator connection.", position=(180, 75), width=82),
        Component("J1", "XM540-W270-T shoulder actuator port",
                  [pn("J1", "1", "GND", "ACT_0V_PE_BONDED", "left"), pn("J1", "2", "VDD", "J1_VDD", "left"), pn("J1", "3", "DATA", "DXL_TTL_DATA", "left")],
                  "PROPOSED - RECEIVED ORIENTATION TEST REQUIRED", "ROBOTIS TTL pin names are controlled; plug/socket orientation and injection harness exact parts remain open.",
                  "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", position=(295, 75), width=82),
        Component("J2", "XM540-W270-T elbow actuator port",
                  [pn("J2", "1", "GND", "ACT_0V_PE_BONDED", "left"), pn("J2", "2", "VDD", "J2_VDD", "left"), pn("J2", "3", "DATA", "DXL_TTL_DATA", "left")],
                  "PROPOSED - RECEIVED ORIENTATION TEST REQUIRED", "Same interface control as J1.",
                  "https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/", position=(65, 170), width=82),
        Component("J3", "XM430-W350-T gripper actuator port",
                  [pn("J3", "1", "GND", "ACT_0V_PE_BONDED", "left"), pn("J3", "2", "VDD", "J3_VDD", "left"), pn("J3", "3", "DATA", "DXL_TTL_DATA", "left")],
                  "PROPOSED - RECEIVED ORIENTATION TEST REQUIRED", "Exact actuator and gripper mechanical release remain open.",
                  "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/", position=(180, 170), width=82),
        Component("XT1", "24 V control terminal block group",
                  [pn("XT1", "TBD-1", "+24V", "SAFETY_24V", "left"), pn("XT1", "TBD-2", "0V", "SAFETY_0V", "left"),
                   pn("XT1", "TBD-3", "SR1 STATUS", "SR1_STATUS", "right"), pn("XT1", "TBD-4", "SRA1 STATUS", "SRA1_STATUS", "right"),
                   pn("XT1", "TBD-5", "K1 STATUS", "K1_STATUS", "right"), pn("XT1", "TBD-6", "K2 STATUS", "K2_STATUS", "right")],
                  "SELECTION REQUIRED", "Exact terminal family, end covers, jumpers, markers, conductor range and torque open.", position=(295, 170), width=82),
        Component("JFRAME1", "Frame/shield bonding interface",
                  [pn("JFRAME1", "TBD-FRAME", "ROBOT FRAME", "ROBOT_FRAME", "left"), pn("JFRAME1", "TBD-SHIELD", "CABLE SHIELDS", "CABLE_SHIELD_TERM", "right")],
                  "SELECTION REQUIRED", "Do not connect frame or shield to 0V/PE until EMC and parallel-path review accepts the implementation.", position=(180, 245), width=92),
        Component("JWP1", "Phoenix Contact MKDS 1/4-3,5, item 1751264",
                  [pn("JWP1", "1", "SAFETY +24 V", "SAFETY_24V", "right"),
                   pn("JWP1", "2", "SAFETY 0 V", "SAFETY_0V", "right"),
                   pn("JWP1", "3", "WATCHDOG 1 COIL SINK", "WD1_COIL_N", "right"),
                   pn("JWP1", "4", "WATCHDOG 2 COIL SINK", "WD2_COIL_N", "right")],
                  "PROPOSED - VERIFICATION REQUIRED",
                  "Project pin allocation is frozen for the PCB candidate. Manufacturer identity, 3.5 mm pitch, 1.1 mm PCB hole, conductor range and torque are controlled; branch protection, current, temperature, ferrule, harness, marking and received orientation remain open.",
                  "https://www.phoenixcontact.com/gb/products/1751264/pdf",
                  "Phoenix Contact official product PDF for item 1751264 generated 2026-08-06; 17.5 A nominal, 200 V nominal, AWG 26-16, 0.22-0.25 N m and 5 mm strip data recorded. Application release remains open.",
                  position=(95, 85), width=100, footprint="PBV3_Footprints:MKDS_1_4_3P5"),
        Component("JWF1", "Phoenix Contact MKDS 1/2-3,5, item 1751248",
                  [pn("JWF1", "1", "WATCHDOG 1 NC +24 V", "WD1_NC_24V", "right"),
                   pn("JWF1", "2", "WATCHDOG 2 NC +24 V", "WD2_NC_24V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED",
                  "Project pin allocation is frozen for the PCB candidate. Exact relay-contact harness, conductor, marking, torque, strain relief, received orientation and application evidence remain open.",
                  "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248",
                  "Phoenix Contact official product data for item 1751248 accessed 2026-08-06; 3.5 mm pitch, 1.1 mm PCB hole, 17.5 A nominal, 200 V nominal, AWG 26-16 and 0.22-0.25 N m recorded.",
                  position=(95, 170), width=100, footprint="PBV3_Footprints:MKDS_1_2_3P5"),
        Component("JWH1", "Phoenix Contact MKDS 1/2-3,5, item 1751248",
                  [pn("JWH1", "1", "COMPUTE HEARTBEAT", "PI_HEARTBEAT", "right"),
                   pn("JWH1", "2", "COMPUTE 0 V", "COMPUTE_0V", "right")],
                  "PROPOSED - VERIFICATION REQUIRED",
                  "Project pin allocation is frozen for the ordinary isolated heartbeat input. GPIO source identity, cable, shielding, retention, strain relief, received orientation and EMC evidence remain open.",
                  "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248",
                  "Phoenix Contact official product data for item 1751248 accessed 2026-08-06; 3.5 mm pitch, 1.1 mm PCB hole, conductor range and torque recorded. No safety credit is assigned.",
                  position=(95, 235), width=100, footprint="PBV3_Footprints:MKDS_1_2_3P5"),
    ]
    s6.notes = ["The V0 bus is TTL because the selected -T actuators are TTL variants; HR-30 RS-485 remains a separate architecture.",
                "All injection modules require released PCB/harness source, continuity, isolation, pull and no-backfeed tests."]

    # Repartition the logical model onto focused two-column pages.  This avoids
    # hiding real connectivity behind overlapping global labels while retaining
    # every component, terminal and net from the connected candidate.
    all_components = {
        comp.ref: comp
        for source_sheet in (s1, s2, s3, s4, s5, s6)
        for comp in source_sheet.components
    }

    def placed(refs: list[str], positions: list[tuple[float, float]]) -> list[Component]:
        result = []
        for ref, position in zip(refs, positions, strict=True):
            comp = all_components[ref]
            comp.position = position
            result.append(comp)
        return result

    left, right = 95.0, 300.0
    s1 = Sheet(1, "01_external_sources.kicad_sch", "External listed sources and DC boundaries",
               "Factory-sealed adapters eliminate project-built mains wiring.")
    s1.components = placed(
        ["PSA1", "JA1", "PSU2", "JC1", "PSU3", "SP1"],
        [(left, 65), (right, 65), (left, 145), (right, 145), (left, 225), (260, 225)],
    )
    s1.notes = ["All AC conductors shown are factory boundaries, not project-built wiring.",
                "Site cords, receptacles, GFCI/code basis and source application review remain open."]

    s2 = Sheet(2, "02_estop_eligibility.kicad_sch", "Dual-channel E-stop and RESET eligibility",
               "Each SR1 input return contains one E-stop NC and one watchdog NO contact; RESET cannot energize K1/K2.")
    s2.components = placed(["S0", "SR1", "S1", "H1"], [(left, 85), (right, 95), (left, 205), (right, 205)])
    s2.notes = ["Heartbeat loss opens both SR1 input returns; recovery alone cannot restore the monitored RESET stage.",
                "RESET release may make SR1 eligible, but SRA1 and K1/K2 remain de-energized until a later ARM."]

    s3 = Sheet(3, "03_arm_watchdog_eligibility.kicad_sch", "Distinct ARM and watchdog eligibility",
               "SRA1 requires SR1 eligibility, two watchdog channels, EDM proof and a new ARM action.")
    s3.components = placed(["SRA1", "KWD1", "S2", "KWD2"], [(left, 85), (right, 85), (left, 205), (right, 205)])
    s3.notes = ["Required after E-stop/watchdog dropout: cause healthy -> RESET press/release -> SAFE_READY -> distinct ARM press/release.",
                "KWD contacts are in the SR1 returns; SRA1 receives the two SR1 safety outputs directly."]

    s4 = Sheet(4, "04_contactor_edm.kicad_sch", "Contactor coils, mirror contacts and EDM",
               "K1 and K2 are distinct final elements; their mirror contacts form the monitored restart return.")
    s4.components = placed(["K1", "K2", "FSR1", "FSR2"], [(left, 85), (right, 85), (left, 205), (right, 205)])
    s4.notes = ["SRA1 outputs are separately protected before K1 and K2 coils; exact protection remains selection required.",
                "Loaded DC interruption, suppression behavior, mirror-contact use and coordination require qualified review."]

    s5 = Sheet(5, "05_actuator_interruption.kicad_sch", "Redundant actuator-power interruption",
               "Source protection, service disconnect and all three poles of K1 then K2 are represented in series.")
    s5.components = placed(["F0", "SD1", "KP1", "KP2"], [(left, 75), (right, 75), (left, 195), (right, 195)])
    s5.notes = ["Series jumpers: K1 2T1->3L2, 4T2->5L3, 6T3->K2 1L1; repeat through K2 to ACT_12V_BUS.",
                "No fuse, disconnect, conductor, connector or contactor application is released without fault-current evidence."]

    s6 = Sheet(6, "06_branches_and_injection.kicad_sch", "Protected actuator branches and VDD-isolating injection",
               "Each actuator has a separate protected VDD branch; inter-actuator data cables must omit VDD.")
    s6.components = placed(
        ["F1", "INJ1", "F2", "INJ2", "F3", "INJ3"],
        [(left, 60), (right, 60), (left, 145), (right, 145), (left, 230), (245, 230)],
    )
    s6.notes = ["Standard fully populated ROBOTIS TTL daisy-chain cables are prohibited because they would parallel branch VDD.",
                "Every injection module requires released source, continuity, isolation, pull and no-backfeed tests."]

    s7 = Sheet(7, "07_watchdog_control.kicad_sch", "Independent watchdog power, controller and drivers",
               "The ordinary watchdog controller and drivers receive no safety-integrity credit by assertion.")
    s7.components = placed(
        ["DC1", "RHB1", "ISO1", "RHP1", "WDCTRL1", "UDRV1", "CDRV1", "UDRV2", "CDRV2"],
        [(75, 55), (190, 80), (305, 55), (340, 115), (85, 210), (250, 150), (75, 120), (250, 230), (75, 160)],
    )
    s7.notes = ["Power-up, brownout, clock, stuck-GPIO and firmware tests are mandatory.",
                "Qualified review decides whether watchdog loss is credited or diagnostic only; current safety credit is NONE."]

    s8 = Sheet(8, "08_watchdog_feedback_interface.kicad_sch", "Calculated dual-channel 24 V watchdog feedback",
               "ISO1212DBQ converts both relay NC diagnostics to default-low 3.3 V logic; no isolation or safety credit is claimed.")
    s8.components = placed(
        ["UFB1", "RTH1", "RSN1", "CFI1", "RW1", "RTH2", "RSN2", "CFI2", "RW2", "CDEC1", "RSO1", "RSO2", "RPD1", "RPD2"],
        [(205, 105), (70, 55), (70, 105), (70, 155), (70, 210), (350, 55), (350, 105), (350, 155), (350, 210),
         (205, 160), (140, 190), (270, 190), (140, 230), (270, 230)],
    )
    s8.notes = ["Type-3 values: RTHR=1.00 kOhm, RSENSE=562 Ohm, CIN=10 nF; calculated wetting load is 2.70 kOhm 1% 0.5 W per channel.",
                "Both grounds are SAFETY_0V; the ISO1212 barrier is not credited. Passive identities are frozen; PCB, derating, EMC and fault tests remain open."]

    s9 = Sheet(9, "09_compute_and_control_terminals.kicad_sch", "Compute, debug and control terminals",
               "High-level compute and diagnostic wiring have no authority to bypass or restore the safety chain.")
    s9.components = placed(["PI1", "JDBG1", "XT1"], [(left, 80), (right, 80), (left, 200)])
    s9.notes = ["Programming/debug connections must not enable outputs during operation.",
                "Terminal family, markers, conductor range, torque and enclosure layout remain selection required."]

    s10 = Sheet(10, "10_actuator_interfaces.kicad_sch", "U2D2, actuator ports and bonding boundary",
               "The U2D2 cable carries DATA and GND only; protected VDD is injected at each actuator.")
    s10.components = placed(
        ["U1", "J1", "J2", "J3", "JFRAME1"],
        [(left, 70), (right, 70), (left, 165), (right, 165), (180, 225)],
    )
    s10.notes = ["The V0 bus is TTL; HR-30 RS-485 remains a separate architecture.",
                "Do not bond frame or shields to 0V/PE until EMC and parallel-path review accepts the exact implementation."]

    s11 = Sheet(11, "11_watchdog_pcb_connectors.kicad_sch", "Watchdog PCB external connectors",
                "Exact PCB terminal-block candidates and project pin allocations define the board boundary; harness release remains open.")
    s11.components = placed(["JWP1", "JWF1", "JWH1"], [(75, 78), (185, 78), (140, 140)])
    for comp in s11.components:
        comp.width = 100
        comp.height = 35
    s11.compact = True
    s11.notes = ["Terminal numbering follows the PCB footprint and must be confirmed against received parts before wiring.",
                 "Nominal terminal ratings do not release branch protection, conductor, ferrule, harness, enclosure or thermal application."]

    test_points = [
        ("TP1", "SAFETY 24 V", "SAFETY_24V"),
        ("TP2", "SAFETY 0 V", "SAFETY_0V"),
        ("TP3", "WATCHDOG 5 V", "WD_5V"),
        ("TP4", "WATCHDOG 3V3", "WD_3V3"),
        ("TP5", "COMPUTE HEARTBEAT", "PI_HEARTBEAT"),
        ("TP6", "WATCHDOG HEARTBEAT", "WD_HEARTBEAT"),
        ("TP7", "WATCHDOG DRIVE 1", "WD1_DRIVE"),
        ("TP8", "WATCHDOG DRIVE 2", "WD2_DRIVE"),
        ("TP9", "WATCHDOG COIL 1 SINK", "WD1_COIL_N"),
        ("TP10", "WATCHDOG COIL 2 SINK", "WD2_COIL_N"),
        ("TP11", "WATCHDOG NC 1 INPUT", "WD1_NC_24V"),
        ("TP12", "WATCHDOG NC 2 INPUT", "WD2_NC_24V"),
        ("TP13", "FEEDBACK RECEIVER 1 OUT", "UFB_OUT1"),
        ("TP14", "FEEDBACK RECEIVER 2 OUT", "UFB_OUT2"),
        ("TP15", "WATCHDOG SWDIO", "WD_SWDIO"),
        ("TP16", "WATCHDOG SWCLK", "WD_SWCLK"),
    ]
    s12 = Sheet(12, "12_watchdog_pcb_test_access.kicad_sch", "Watchdog PCB test access",
                "Exact clip-compatible test terminals expose controlled nodes without granting safety or operating authority.")
    positions = [(55 + column * 90, 60 + row * 55) for row in range(4) for column in range(4)]
    s12.components = [
        Component(
            ref,
            "Harwin S1751-46R SMT test point",
            [pn(ref, "1", label, net, "right")],
            "PROPOSED - ACCESS VERIFICATION REQUIRED",
            "Dedicated clip/probe point. Confirm probe compatibility, installed access, clearance, marking, retention and no-short test method on the assembled guarded board.",
            "https://www.harwin.com/products/S1751-46R",
            "Harwin drawing S1751-XXR, issue 10 dated 2023-02-15; product page and drawing accessed 2026-08-06. Recommended PCB pad is 3.45 x 1.85 mm.",
            position=position,
            width=70,
            height=20,
            footprint="PBV3_Footprints:Harwin_S1751_46R",
        )
        for (ref, label, net), position in zip(test_points, positions, strict=True)
    ]
    s12.notes = ["Test terminals are diagnostic features only; they provide no safety integrity or bypass authority.",
                 "Verify clip clearance with guards, harnesses and power removed before any live measurement procedure is released."]

    for comp in [*s7.components, *s8.components, *s11.components, *s12.components]:
        comp.watchdog_pcb = True

    return [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]


def font(size: float = 1.8, justify: str = "") -> str:
    just = f" (justify {justify})" if justify else ""
    return f"(effects (font (size {size:.2f} {size:.2f})){just})"


def property_block(name: str, value: str, x: float, y: float, *, hidden: bool = False, justify: str = "") -> str:
    hide = " (hide yes)" if hidden else ""
    just = f" (justify {justify})" if justify else ""
    return (f'(property "{esc(name)}" "{esc(value)}" (at {x:.2f} {y:.2f} 0) '
            f'(effects (font (size 1.50 1.50)){just}{hide}))')


def lib_symbol(comp: Component) -> str:
    half_w = q(comp.width / 2.0)
    half_h = q(comp.box_height() / 2.0)
    left = comp.side_pins("left")
    right = comp.side_pins("right")

    def coords(items: list[Pin]):
        return [(pin, q((i - (len(items) - 1) / 2.0) * 5.08)) for i, pin in enumerate(items)]

    pin_text = []
    for side, items in (("left", left), ("right", right)):
        for pin, y in coords(items):
            x = -half_w - 2.54 if side == "left" else half_w + 2.54
            rot = 0 if side == "left" else 180
            pin_text.append(
                f'(pin passive line (at {x:.2f} {y:.2f} {rot}) (length 2.54) '
                f'(name "{esc(pin.name)}" (effects (font (size 1.27 1.27)))) '
                f'(number "{esc(pin.number)}" (effects (font (size 1.27 1.27)))))'
            )
    return f'''(symbol "PBV3:{esc(comp.ref)}"
      (pin_names (offset 1.016))
      (exclude_from_sim no) (in_bom yes) (on_board yes)
      {property_block("Reference", comp.ref, -half_w, -half_h-4, justify="left bottom")}
      {property_block("Value", comp.value, 0, 0, hidden=True)}
      {property_block("Footprint", comp.footprint, 0, 0, hidden=True)}
      {property_block("Datasheet", comp.datasheet, 0, 0, hidden=True)}
      {property_block("Description", comp.description, 0, 0, hidden=True)}
      {property_block("Status", comp.status, 0, half_h+3, justify="bottom")}
      {property_block("Evidence", comp.evidence, 0, 0, hidden=True)}
      {property_block("Display", comp.value, -half_w, -half_h-0.8, justify="left bottom")}
      (symbol "{esc(comp.ref)}_0_1"
        (rectangle (start {-half_w:.2f} {-half_h:.2f}) (end {half_w:.2f} {half_h:.2f})
          (stroke (width 0.45) (type solid)) (fill (type background))))
      (symbol "{esc(comp.ref)}_1_1" {' '.join(pin_text)})
      (embedded_fonts no))'''


def component_instance(comp: Component, root_uuid: str, sheet: Sheet) -> str:
    x, y = q(comp.position[0]), q(comp.position[1])
    half_w = q(comp.width / 2.0)
    half_h = q(comp.box_height() / 2.0)
    pins = "\n".join(f'      (pin "{esc(pin.number)}" (uuid "{uid(f"pin:{sheet.filename}:{comp.ref}:{pin.number}")}"))' for pin in comp.pins)
    return f'''(symbol
      (lib_id "PBV3:{esc(comp.ref)}") (at {x:.2f} {y:.2f} 0) (unit 1)
      (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {'yes' if comp.status.startswith('DNP') else 'no'})
      (uuid "{uid(f"inst:{sheet.filename}:{comp.ref}")}")
      {property_block("Reference", comp.ref, x-half_w, y-half_h-4, justify="left bottom")}
      {property_block("Value", comp.value, x, y, hidden=True)}
      {property_block("Footprint", comp.footprint, x, y, hidden=True)}
      {property_block("Datasheet", comp.datasheet, x, y, hidden=True)}
      {property_block("Description", comp.description, x, y, hidden=True)}
      {property_block("Status", comp.status, x, y+half_h+3, justify="bottom")}
      {property_block("Evidence", comp.evidence, x, y, hidden=True)}
      {property_block("Display", comp.value, x-half_w, y-half_h-0.8, justify="left bottom")}
{pins}
      (instances (project "{PROJECT}" (path "/{root_uuid}/{sheet.sheet_uuid}" (reference "{esc(comp.ref)}") (unit 1)))))'''


def build_wire_numbers(items: list[Sheet], net_counts: dict[str, int]) -> dict[tuple[str, str], str]:
    wire_numbers: dict[tuple[str, str], str] = {}
    for sheet in items:
        wire_index = 1
        for comp in sheet.components:
            for side in ("left", "right"):
                for pin in comp.side_pins(side):
                    if net_counts.get(pin.net, 0) > 1:
                        wire_numbers[(comp.ref, pin.number)] = f"W{sheet.number}{wire_index:03d}"
                        wire_index += 1
    return wire_numbers


def pin_graphics(comp: Component, sheet: Sheet, net_counts: dict[str, int],
                 wire_numbers: dict[tuple[str, str], str]) -> str:
    x, y = q(comp.position[0]), q(comp.position[1])
    half_w = q(comp.width / 2.0)
    output = []
    for side in ("left", "right"):
        pins = comp.side_pins(side)
        for i, pin in enumerate(pins):
            # KiCad symbol-library coordinates use positive Y upward while the
            # schematic canvas uses positive Y downward.  Mirror the local pin
            # ordinate so each drawn label lands on the terminal named in the
            # generated library and exported native netlist.
            py = q(y - q((i - (len(pins) - 1) / 2.0) * 5.08))
            endpoint = x - half_w - 2.54 if side == "left" else x + half_w + 2.54
            label_x = endpoint - 10.16 if side == "left" else endpoint + 10.16
            endpoint, label_x = q(endpoint), q(label_x)
            if net_counts.get(pin.net, 0) == 1:
                output.append(f'''(no_connect (at {endpoint:.2f} {py:.2f})
                  (uuid "{uid(f"noconnect:{sheet.filename}:{comp.ref}:{pin.number}")}"))''')
                continue
            output.append(f'''(wire (pts (xy {endpoint:.2f} {py:.2f}) (xy {label_x:.2f} {py:.2f}))
              (stroke (width 0) (type default)) (uuid "{uid(f"wire:{sheet.filename}:{comp.ref}:{pin.number}")}"))''')
            rotation = 180 if side == "left" else 0
            justify = "right" if side == "left" else "left"
            output.append(f'''(global_label "{esc(pin.net)}" (shape bidirectional) (at {label_x:.2f} {py:.2f} {rotation})
              (fields_autoplaced yes) (effects (font (size 1.50 1.50)) (justify {justify}))
              (uuid "{uid(f"label:{sheet.filename}:{comp.ref}:{pin.number}")}")
              (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {label_x:.2f} {py+2.54:.2f} 0)
                (effects (font (size 1.27 1.27)) (hide yes))))''')
            wire_number = wire_numbers[(comp.ref, pin.number)]
            output.append(f'''(text "{wire_number}" (exclude_from_sim no)
              (at {(endpoint+label_x)/2:.2f} {py-2.0:.2f} 0) (effects (font (size 1.27 1.27)) (justify bottom))
              (uuid "{uid(f"wiretext:{sheet.filename}:{comp.ref}:{pin.number}")}"))''')
    return "\n".join(output)


def text_item(value: str, x: float, y: float, size: float, key: str) -> str:
    return f'''(text "{esc(value)}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0)
      (effects (font (size {size:.2f} {size:.2f})) (justify left bottom)) (uuid "{uid(key)}"))'''


def child_schematic(root_uuid: str, sheet: Sheet, net_counts: dict[str, int],
                    wire_numbers: dict[tuple[str, str], str]) -> str:
    libs = "\n".join(lib_symbol(comp) for comp in sheet.components)
    graphics = []
    graphics.append(text_item(WARNING, 17.78, 10.16, 2.54, f"warn:{sheet.filename}"))
    graphics.append(text_item(f"{sheet.number:02d}  {sheet.title}", 17.78, 19.05, 2.20, f"title:{sheet.filename}"))
    graphics.append(text_item(sheet.purpose, 17.78, 26.67, 1.80, f"purpose:{sheet.filename}"))
    border_x = 281.94 if sheet.compact else 406.40
    border_y = 184.15 if sheet.compact else 281.94
    note_y = 164.0 if sheet.compact else 260.0
    paper = "A4" if sheet.compact else "A3"
    graphics.append(f'''(rectangle (start 12.70 31.75) (end {border_x:.2f} {border_y:.2f})
      (stroke (width 0.50) (type solid)) (fill (type none)) (uuid "{uid(f"border:{sheet.filename}")}"))''')
    for comp in sheet.components:
        graphics.append(pin_graphics(comp, sheet, net_counts, wire_numbers))
    note_lines: list[str] = []
    for idx, note in enumerate(sheet.notes):
        wrapped = textwrap.wrap(f"NOTE {idx+1}: {note}", width=92, subsequent_indent="        ") or [""]
        note_lines.extend(wrapped)
    for idx, line in enumerate(note_lines):
        graphics.append(text_item(line, 17.78, note_y + idx*5.5, 1.50, f"note:{sheet.filename}:{idx}"))
    instances = "\n".join(component_instance(comp, root_uuid, sheet) for comp in sheet.components)
    return f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0")
  (uuid "{uid(f"file:{sheet.filename}")}") (paper "{paper}")
  (title_block (title "PB HR-V0 Electrical V3 - {sheet.number:02d}") (date "{DATE}") (rev "{REV}")
    (company "Project Button") (comment 1 "{WARNING}") (comment 2 "CONNECTED DESIGN CANDIDATE - QUALIFIED REVIEW REQUIRED"))
  (lib_symbols {libs})
  {' '.join(graphics)}
  {instances}
  (embedded_fonts no))
'''


def root_schematic(root_uuid: str, items: list[Sheet]) -> str:
    blocks = []
    positions = [
        (17.78 + col * 132.08, 42.0 + row * 56.0)
        for row in range(4)
        for col in range(3)
    ]
    for sheet, (x, y) in zip(items, positions):
        blocks.append(f'''(sheet (at {x:.2f} {y:.2f}) (size 116.84 40.64)
          (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
          (stroke (width 0.5) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "{sheet.sheet_uuid}")
          (property "Sheetname" "{sheet.number:02d} {esc(sheet.title)}" (at {x+2.54:.2f} {y+10.16:.2f} 0) {font(1.8, 'left bottom')})
          (property "Sheetfile" "{sheet.filename}" (at {x+2.54:.2f} {y+25.4:.2f} 0) {font(1.5, 'left top')})
          (instances (project "{PROJECT}" (path "/{root_uuid}" (page "{sheet.number+1}")))))''')
    return f'''(kicad_sch
  (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid "{root_uuid}") (paper "A3")
  (title_block (title "Project Button HR-V0 Electrical V3 index") (date "{DATE}") (rev "{REV}")
    (company "Project Button") (comment 1 "{WARNING}") (comment 2 "V2.1 PRESERVED; V3 IS A CONNECTED CANDIDATE"))
  (lib_symbols)
  {text_item(WARNING,17.78,10.16,2.54,'root-warning')}
  {text_item('PROJECT BUTTON HR-V0 ELECTRICAL V3 CONNECTED CANDIDATE',17.78,19.05,2.54,'root-title')}
  {text_item('Separate RESET and ARM, two PNOZ stages, dual watchdog contacts, external adapters, redundant actuator interruption.',17.78,27.0,1.8,'root-subtitle')}
  {' '.join(blocks)}
  (sheet_instances (path "/" (page "1"))) (embedded_fonts no))
'''


def write_tables(items: list[Sheet], net_counts: dict[str, int],
                 wire_numbers: dict[tuple[str, str], str]):
    components = [(sheet, comp) for sheet in items for comp in sheet.components]
    with (OUT / "bom.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["sheet", "reference", "value", "quantity", "status", "datasheet", "evidence"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for sheet, comp in components:
            if comp.quantity:
                writer.writerow({"sheet": sheet.filename, "reference": comp.ref, "value": comp.value,
                                 "quantity": comp.quantity, "status": comp.status, "datasheet": comp.datasheet, "evidence": comp.evidence})
    with (OUT / "connector-schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["sheet", "reference", "terminal", "pin_name", "net", "status"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for sheet, comp in components:
            for pin in comp.pins:
                writer.writerow({"sheet": sheet.filename, "reference": comp.ref, "terminal": pin.number,
                                 "pin_name": pin.name, "net": pin.net, "status": comp.status})
    nets: dict[str, list[str]] = {}
    for sheet, comp in components:
        for pin in comp.pins:
            nets.setdefault(pin.net, []).append(f"{sheet.filename}:{comp.ref}:{pin.number}")
    with (OUT / "net-schedule.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["net", "connection_count", "connections"])
        for net, connections in sorted(nets.items()):
            writer.writerow([net, len(connections), " | ".join(connections)])
    with (OUT / "wire-number-table.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["wire_number", "sheet", "reference", "terminal", "pin_name", "net"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for sheet, comp in components:
            for side in ("left", "right"):
                for pin in comp.side_pins(side):
                    if net_counts.get(pin.net, 0) > 1:
                        writer.writerow({"wire_number": wire_numbers[(comp.ref, pin.number)],
                                         "sheet": sheet.filename, "reference": comp.ref,
                                         "terminal": pin.number, "pin_name": pin.name, "net": pin.net})
    with (OUT / "unresolved-selections.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sheet", "reference", "status", "evidence_needed"])
        for sheet, comp in components:
            if any(key in comp.status for key in ("SELECTION REQUIRED", "DESIGN REQUIRED", "CONFIRMATION REQUIRED", "VERIFICATION REQUIRED", "RELEASE OPEN")):
                writer.writerow([sheet.filename, comp.ref, comp.status, comp.description])


def write_docs(items: list[Sheet]):
    text = f"""# Project Button HR-V0 Electrical {REV}

**{WARNING}**

This is a generated, connected native KiCad candidate derived from `tools/generate_hr_v0_electrical_v3.py`. It does not supersede the reviewed Electrical V2.1 package until exact selections, application reviews, calculations, physical tests and qualified review close.

## Pages

""" + "\n".join(f"{sheet.number}. `{sheet.filename}` — {sheet.title}" for sheet in items) + """

## Material corrections relative to V2.1

- Separate SR1 RESET eligibility and SRA1 ARM/EDM stages.
- Two separately driven watchdog relay contacts interrupt the two SR1 input returns so heartbeat loss forces the physical RESET stage to drop.
- Phoenix relay terminals are frozen from the official circuit diagram. Both 24 V NC diagnostics pass through the calculated ISO1212DBQ input network before the Pico GPIO. Exact proposed passive order codes are frozen; PCB, received measurements, derating and physical validation remain open.
- Compute heartbeat crosses an exact VO618A-4X017T optical interface with exact 910 Ohm input and 10 kOhm pullup candidates. Two separate TPL7407LPWR packages drive the two relay coils, with unused inputs tied low, unused outputs open, and local 100 nF COM bypass candidates. These ordinary circuits receive no safety credit and still require PCB, timing, hot-plug, fault-injection, EMC and qualified review.
- The ISO1212 feedback network uses exact proposed Vishay, Panasonic, TDK and Murata passive order codes. Receiving, PCB land-pattern/placement, DC-bias, pulse, thermal, EMC, fault and HIL evidence remain mandatory.
- Three exact Phoenix Contact PCB terminal-block candidates freeze the project pin allocation for 24 V/control return, two coil sinks, two NC feedback channels and the isolated heartbeat pair. Harness, conductor, ferrule, protection, enclosure, received-orientation and thermal evidence remain open.
- `project-button-v3.kicad_pcb` is the native PCB-P0.4 routed/test-access candidate. It retains the corrected ISO1212 DBQ footprint and field/control zoning, adds sixteen exact Harwin S1751-46R test terminals and separate TI-recommended 2 mm x 2 mm SUB1/SUB2 floating copper planes, and must pass native DRC plus independent connectivity/isolation checks. It is not a Gerber or fabrication release; exact stack-up/fabricator capability, 0.10 mm breakout acceptance, installed probe access, protection coordination, schematic parity review, creepage/clearance, thermal, EMC and HIL evidence remain gates.
- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.
- External Mean Well adapters replace project-built mains wiring.
- The GST280A12-C6P source bond is explicit; project star point SP1 is DNP/prohibited.
- Three poles per candidate contactor are represented in series, pending Schneider application confirmation.
- U2D2 VDD is omitted and protected power is injected by three custom modules; those modules remain a design gate.

## Validate

Run `python tools/generate_hr_v0_electrical_v3.py --validate` with KiCad 10 installed. Generated ERC proves only modeled connectivity/annotation. Every `TBD-*`, `SELECTION REQUIRED`, `DESIGN REQUIRED`, and application-confirmation item remains a release blocker.

No drawing in this directory authorizes ordering, wiring, fabrication or energization.
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def manifest():
    rows = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SOURCE-MANIFEST.csv":
            rows.append((path.relative_to(OUT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest().upper()))
    with (OUT / "SOURCE-MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "sha256"])
        writer.writerows(rows)


def find_kicad_cli() -> Path | None:
    candidates = [Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"), Path(r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe")]
    found = shutil.which("kicad-cli")
    if found:
        candidates.insert(0, Path(found))
    return next((path for path in candidates if path.exists()), None)


def validate_with_kicad(cli: Path) -> int:
    validation = OUT / "validation"
    exports = OUT / "output"
    validation.mkdir(exist_ok=True)
    exports.mkdir(exist_ok=True)
    for path in exports.iterdir():
        if path.is_file():
            path.unlink()
    project = OUT / f"{PROJECT}.kicad_sch"
    commands = [
        [str(cli), "sch", "erc", "--exit-code-violations", "--output", str(validation / f"{PROJECT}-erc.rpt"), str(project)],
        [str(cli), "sch", "export", "netlist", "--output", str(validation / f"{PROJECT}.net"), str(project)],
        [str(cli), "sch", "export", "pdf", "--output", str(exports / f"{PROJECT}-preliminary.pdf"), str(project)],
        [str(cli), "sch", "export", "svg", "--output", str(exports), str(project)],
    ]
    rc = 0
    logs = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + subprocess.list2cmdline(command) + "\n" + result.stdout + result.stderr + f"\nexit={result.returncode}\n")
        if result.returncode:
            rc = result.returncode
            break
    # KiCad's SVG writer can leave line-ending spaces in newly emitted groups.
    # Normalize only trailing horizontal whitespace so generated exports remain
    # deterministic and pass repository whitespace checks without changing art.
    if rc == 0:
        for svg in exports.glob("*.svg"):
            content = svg.read_bytes()
            svg.write_bytes(re.sub(rb"[ \t]+(?=\r?\n)", b"", content))
    (validation / "kicad-cli.log").write_text("\n".join(logs), encoding="utf-8")
    return rc


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.kicad_sch"):
        path.unlink()
    items = sheets()
    root_uuid = uid("root-project-button-v3")
    net_counts: dict[str, int] = {}
    for sheet in items:
        for comp in sheet.components:
            for pin in comp.pins:
                net_counts[pin.net] = net_counts.get(pin.net, 0) + 1
    wire_numbers = build_wire_numbers(items, net_counts)
    (OUT / f"{PROJECT}.kicad_pro").write_text(json.dumps({
        "board": {}, "boards": [], "cvpcb": {}, "erc": {}, "libraries": {},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {"classes": [], "meta": {"version": 3}}, "pcbnew": {}, "schematic": {},
        "text_variables": {"PROJECT_STATUS": WARNING, "REVISION": REV}
    }, indent=2), encoding="utf-8")
    library_symbols = []
    for sheet in items:
        for comp in sheet.components:
            library_symbols.append(lib_symbol(comp).replace(f'(symbol "PBV3:{comp.ref}"', f'(symbol "{comp.ref}"', 1))
    (OUT / f"{PROJECT}.kicad_sym").write_text(
        '(kicad_symbol_lib\n  (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n  '
        + "\n".join(library_symbols) + "\n)\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(
        f'(sym_lib_table\n  (version 7)\n  (lib (name "PBV3")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "Generated HR-V0 Electrical V3 symbols"))\n)\n',
        encoding="utf-8")
    (OUT / "fp-lib-table").write_text(
        '(fp_lib_table\n  (version 7)\n  (lib (name "PBV3_Footprints")(type "KiCad")(uri "${KIPRJMOD}/PBV3_Footprints.pretty")(options "")(descr "Project Button watchdog PCB candidate footprints"))\n)\n',
        encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_sch").write_text(root_schematic(root_uuid, items), encoding="utf-8")
    for sheet in items:
        (OUT / sheet.filename).write_text(child_schematic(root_uuid, sheet, net_counts, wire_numbers), encoding="utf-8")
    write_tables(items, net_counts, wire_numbers)
    write_docs(items)
    cli = find_kicad_cli()
    rc = 0
    if "--validate" in sys.argv:
        if cli is None:
            print("KiCad CLI not found", file=sys.stderr)
            return 3
        rc = validate_with_kicad(cli)
    # KiCad may create a per-user local-preferences file during CLI parsing.
    # It is not controlled engineering source and must not enter the manifest.
    (OUT / f"{PROJECT}.kicad_prl").unlink(missing_ok=True)
    manifest()
    component_count = sum(len(sheet.components) for sheet in items)
    pin_count = sum(len(comp.pins) for sheet in items for comp in sheet.components)
    print(f"Generated {len(items)+1} pages, {component_count} component blocks, {pin_count} modeled terminals")
    print(WARNING)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
