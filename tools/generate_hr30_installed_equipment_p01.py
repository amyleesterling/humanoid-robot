"""Generate the HR-30 P0.1 installed-equipment and harness layout.

This converts the former empty bay reservations into located candidate hardware
envelopes with mounting planes, service directions, harness endpoints, mass,
power, and heat planning values.  Exact procurement selections and physical
validation remain open.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_fabrication_architecture_p01 as fabrication


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
IDENTIFIER = "HR-30-INSTALLED-EQUIPMENT-P0.1"
WARNING = body.WARNING
ACCESSED = "2026-08-14"
BATTERY = {
    "manufacturer": "Grepow / Tattu",
    "model": "TAA12K4S30EC5",
    "nominal_voltage_v": 14.8,
    "capacity_ah": 12.0,
    "energy_wh": 177.6,
    "discharge_c": 30.0,
    "mass_kg": 1.057,
    "size_mm": (72.0, 37.0, 193.0),
    "url": "https://www.grepow.com/uav-battery/tattu-4s-12000mah-14-8v-30c-lipo-drone-battery.html",
    "revision": "live manufacturer product page; no document revision/date published; accessed 2026-08-14",
}


@dataclass(frozen=True)
class Equipment:
    item_id: str
    module: str
    role: str
    candidate: str
    shape: cq.Shape
    planning_mass_kg: float
    power_w: float
    heat_w: float
    mounting_plane: str
    service_direction: str
    connector_boundary: str
    source_url: str
    source_revision: str
    evidence_state: str
    dynamic_link: str
    color: tuple[float, float, float, float]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def box(width: float, depth: float, height: float, center, radius: float = 1.5) -> cq.Shape:
    return body.rounded_box(width, depth, height, center, min(radius, width / 3, depth / 3, height / 3))


def build() -> list[Equipment]:
    compute = (0.10, 0.48, 0.82, 1.0)
    control = (0.12, 0.72, 0.70, 1.0)
    power = (0.96, 0.58, 0.08, 1.0)
    battery = (0.18, 0.70, 0.28, 1.0)
    sensor = (0.48, 0.82, 0.98, 1.0)
    audio = (0.40, 0.30, 0.72, 1.0)
    safety = (0.78, 0.14, 0.14, 1.0)
    compliant = (0.92, 0.72, 0.16, 1.0)
    harness = (0.20, 0.86, 0.92, 0.72)
    items: list[Equipment] = []

    def add(item_id, module, role, candidate, shape, mass, watts, heat, plane, service, connector,
            url, revision, evidence, link, color):
        if shape.isNull() or not shape.isValid() or shape.Volume() <= 1e-6:
            raise RuntimeError(f"invalid equipment geometry {item_id}")
        items.append(Equipment(item_id, module, role, candidate, shape, mass, watts, heat, plane,
                               service, connector, url, revision, evidence, link, color))

    # Torso compute/control stack. Board envelopes are oriented in the XZ plane
    # so both split torso covers can be removed without disturbing the frame.
    add("EQ-T01-PI5", "T01", "main compute", "Raspberry Pi 5 8GB SC1112 candidate",
        box(85, 12, 58, (0, -24, 527), 2), 0.050, 18, 14,
        "rear face of front compute tray, Y=-18 mm", "-Y front-cover withdrawal",
        "5.1 V, Ethernet, USB, two CSI/DSI FFCs; exact locking/strain relief open",
        "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf",
        "Raspberry Pi 5 mechanical drawing; portal updated 2025-10-06",
        "85 x 56 mm official reference drawing; 50 g installed mass allowance is not manufacturer-published",
        "torso", compute)
    add("EQ-T01-PI5-COOLER", "T01", "compute cooling", "Raspberry Pi Active Cooler SC1148 candidate",
        box(60, 13, 45, (0, -10.5, 527), 2), 0.032, 2.5, 2.5,
        "Pi 5 processor side", "+Y fan/service clearance",
        "Pi fan header; tach/failure telemetry required",
        "https://www.raspberrypi.com/products/active-cooler/", "live official product page; accessed 2026-08-14",
        "envelope and installed mass remain incoming-inspection items", "torso", compute)
    add("EQ-T01-MOTION", "C01", "deterministic motion controller",
        "custom STM32H743ZIT6 LQFP144 motion-controller carrier candidate",
        box(74, 10, 44, (0, 24, 482), 2), 0.055, 4.0, 3.0,
        "torso rear electronics tray", "+Y rear-cover withdrawal",
        "JMCU_A/JMCU_B each JST BM15B-GHS-TBT; eight sourced UART pin groups; watchdog/permit and remaining board pins open",
        "https://www.st.com/en/microcontrollers-microprocessors/stm32h743zi.html", "ST DS12110 Rev 11; live product page accessed 2026-08-14",
        "exact MCU order-code and eight actuator-bus package pins selected; PCB, power/reset/debug, firmware and safety credit remain open", "torso", control)
    add("EQ-T01-WATCHDOG", "S01", "independent watchdog",
        "Raspberry Pi Pico-class non-safety-rated diagnostic watchdog candidate",
        box(22, 8, 52, (-49, 22, 535), 1.5), 0.012, 0.5, 0.5,
        "torso rear electronics tray", "+Y rear-cover withdrawal",
        "isolated heartbeat input and dry permit interface; exact circuit open",
        "https://www.raspberrypi.com/products/raspberry-pi-pico/", "live official product page; accessed 2026-08-14",
        "diagnostic only; cannot be credited as a safety function", "torso", safety)

    for suffix, x, buses, candidate, watts, heat, source, revision in (
        ("A", -48, "RS-LLEG | RS-RLEG | RS-LARM | RS-RARM",
         "four-channel carrier with 4x TI ISOW1432DFMR and 4x JST BM03B-GHS-TBT data-only field headers",
         3.0, 2.2, "https://www.ti.com/product/ISOW1432", "TI SLLSF86C Rev C; March 2022; accessed 2026-08-14"),
        ("B", 48, "RS-WAIST | TTL-LDIST | TTL-RDIST | TTL-HEAD",
         "four-channel carrier with 1x TI ISOW1432DFMR, 3x SN74LVC1T45DCKR and exact JST GH data-only field headers",
         1.5, 1.0, "https://www.ti.com/product/SN74LVC1T45", "TI SCES515N Rev N; June 2024; accessed 2026-08-14"),
    ):
        add(f"EQ-T01-BUS-CARRIER-{suffix}", "C01", "four-channel actuator-bus interface carrier",
            f"{candidate}; buses {buses}",
            box(82, 14, 42, (x, 11, 526), 2), 0.045, watts, heat,
            "torso rear electronics tray", "+Y rear-cover withdrawal",
            "JST GHR-15V-S logic-only controller cable plus per-segment BM02/BM03B-GHS-TBT field headers; no actuator VDD contacts",
            source, revision,
            "complete sourced application circuit and 82 x 42 mm native PCB placement candidate exist; copper routing, stackup/isolation geometry, EMC, thermal and physical validation remain open; U2D2 stays external commissioning-only",
            "torso", control)

    # Pelvis tether-first power hardware.  The source, safety relay and both
    # GV121CAC series contactors remain in the external panel.  The robot
    # carries only the touch-safe inlet and passive main/eight-branch protected
    # distribution candidate; it carries no high-current contactor.
    add("EQ-P01-TETHER-INLET", "P01", "tether inlet and service disconnect",
        "Anderson SBS75GBLK three-position inlet candidate; project contacts P1=controlled +12 V, G=pre-mate frame reference, P2=return",
        box(42, 24, 34, (0, 35, 378), 3), 0.110, 0, 0,
        "rear pelvis bulkhead", "+Y external tool access",
        "1339G2 primary contacts and 1340G1 pre-mate contact are 6 AWG family candidates; exact cable, polarity marking, frame bond, retention and flex validation open",
        "https://www.andersonpower.com/content/dam/app/ecommerce/product-pdfs/SBS75G/1s6417-SBS-Assembly-Instructions.pdf",
        "Anderson 1S6417; accessed 2026-08-15", "housing/contact family identified; installed harness and application remain open", "base_link", safety)
    add("EQ-P01-EIGHT-BRANCH-DISTRIBUTOR", "P01", "main plus eight electrically separate actuator-bus feeds",
        "146 x 34 x 66 mm insulated distributor candidate with nine Littelfuse 04980923ZXT covered MIDI holders; all fuse values SELECTION REQUIRED",
        box(146, 34, 66, (0, 12, 382), 3), 0.325, 0.0, 2.0,
        "rear pelvis power tray", "+Y rear-cover withdrawal",
        "one inlet, one main holder and exact separate feeds to RS-LLEG/RS-RLEG/RS-LARM/RS-RARM/RS-WAIST/TTL-LDIST/TTL-RDIST/TTL-HEAD boards; fuse values, conductors, lugs and torque open",
        "https://www.littelfuse.com/products/fuse-blocks-fuseholders-and-fuse-accessories/automotive-and-commercial-vehicle-fuse-holders/midi-498/04980923zxt.aspx",
        "MIDI 498 datasheet 012826-A; accessed 2026-08-15", "physical holder/enclosure allocation only; no fuse, conductor, thermal, fault or safety credit", "base_link", power)
    # Eight real 124 x 45 mm walking-power board envelopes replace the former
    # five-board grouping.  The leg boards are oriented along Z inside the
    # removable rear thigh covers.  The arm and distal boards use two separated
    # rear-torso layers; the waist board is on the pelvis tray and the head-bus
    # board is above them.  Each envelope includes
    # the 1.6 mm PCB, connector height and a small non-credited mounting gap.
    # Board mass is a controlled planning allowance until a received assembly
    # is weighed; the eight allowances total 0.360 kg.
    for board_id, module, center, dims, link, allocation, plane in (
        ("WPS-RS-LLEG", "L01", (62.5, 19.0, 294.0), (45, 8, 124), "L_thigh", "six left-leg axes", "inside left rear thigh cover"),
        ("WPS-RS-RLEG", "L02", (-62.5, 19.0, 294.0), (45, 8, 124), "R_thigh", "six right-leg axes", "inside right rear thigh cover"),
        ("WPS-RS-LARM", "T01", (46.0, 31.0, 522.0), (45, 8, 124), "torso", "three left-arm axes plus three DNP channels", "right half of rear torso outer electronics layer"),
        ("WPS-RS-RARM", "T01", (-46.0, 31.0, 522.0), (45, 8, 124), "torso", "three right-arm axes plus three DNP channels", "left half of rear torso outer electronics layer"),
        ("WPS-TTL-LDIST", "T01", (46.0, 21.0, 522.0), (45, 8, 124), "torso", "left wrist and gripper plus four DNP channels", "right half of rear torso inner electronics layer"),
        ("WPS-TTL-RDIST", "T01", (-46.0, 21.0, 522.0), (45, 8, 124), "torso", "right wrist and gripper plus four DNP channels", "left half of rear torso inner electronics layer"),
        ("WPS-TTL-HEAD", "T01", (0.0, 11.0, 605.0), (124, 8, 45), "torso", "head pan and tilt plus four DNP channels", "upper torso inner electronics tray"),
        ("WPS-RS-WAIST", "P01", (0.0, -18.0, 382.0), (124, 8, 45), "base_link", "waist axis plus five DNP channels", "front pelvis power tray"),
    ):
        add(f"EQ-{board_id}", module, "six-channel actuator branch protection board",
            f"routed 124 x 45 mm ten-layer {board_id} instance; {allocation}",
            box(*dims, center, 2), 0.045, 0.1, 0.8,
            plane, "removable-cover withdrawal before connector service",
            "one bus-specific controlled feed input, six paired bidirectional branch outputs, six disable/PG control boundaries",
            "electrical/walking-power-successor-p0.1", "native KiCad architecture candidate generated 2026-08-17",
            "native schematic ERC 0/0 for connectivity/annotation; PCB, stackup, connector temperature, regeneration, physical fit and thermal proof remain open",
            link, power)
    for suffix, x, output_net in (
        ("LDIST", 50.0, "TTL_LDIST_SAFE_9V"),
        ("RDIST", 0.0, "TTL_RDIST_SAFE_9V"),
        ("HEAD", -50.0, "TTL_HEAD_SAFE_9V"),
    ):
        add(f"EQ-T01-TTL-REG-{suffix}", "T01", "dedicated 12 V to 9 V actuator-bus regulator",
            f"Pololu S18V20F9 item 2576 candidate in 45 x 22 x 14 mm installed clearance envelope; output {output_net}",
            box(45, 14, 22, (x, 1, 450), 2), 0.018, 18.0, 2.2,
            "lower torso isolated converter rail", "-Y front-cover withdrawal",
            f"separate ACT_MAIN_SAFE_12V input and {output_net} output; no regulator outputs may be paralleled; exact contacts and reverse-energy behavior open",
            "https://www.pololu.com/product/2576", "live official product page; revision not stated; accessed 2026-08-14",
            "exact product family candidate and installed clearance envelope; current margin, transients, protection, thermal behavior and reverse-energy validation remain open",
            "torso", power)
    add("EQ-P01-AUX-CONVERTER", "P01", "auxiliary power conversion",
        "isolated 14.8 V to 5.1 V compute/HMI converter candidate; exact model required",
        box(62, 18, 24, (-35, -4, 408), 2), 0.095, 0.0, 6.0,
        "upper pelvis conductive tray", "-Y front-cover withdrawal",
        "protected primary input; separate compute and control outputs; grounding scheme open",
        "SELECTION REQUIRED", "SELECTION REQUIRED", "planning envelope/mass/loss only", "base_link", power)
    add("EQ-P01-IMU", "P01", "pelvis inertial sensor",
        "industrial 6/9-axis IMU module candidate; exact model required",
        box(34, 10, 34, (43, -4, 408), 2), 0.025, 0.8, 0.8,
        "machined pelvis datum pad", "-Y front-cover withdrawal",
        "isolated CAN/SPI and keyed power; axis/latency/calibration interface open",
        "SELECTION REQUIRED", "SELECTION REQUIRED", "datum envelope and mass allowance only", "base_link", sensor)
    add("EQ-P01-RESTRAINT-ANCHOR", "P01", "fall-restraint body hardpoint",
        "through-bolted dual-lug restraint anchor candidate",
        box(34, 28, 24, (0, 43, 414), 3), 0.085, 0, 0,
        "rear pelvis restraint bridge", "+Y external inspection/access",
        "rated connector geometry/load path remains open",
        "SELECTION REQUIRED", "SELECTION REQUIRED", "visible metal candidate; no fall-load credit", "base_link", safety)

    # The untethered walking candidate carries a removable rear-torso battery
    # cassette.  The exact Grepow/Tattu pack envelope is modeled inside a
    # separate structural/thermal cassette and protection-monitor reservation.
    # The product page does not state that the pack contains a BMS/PCM, so no
    # such protection is inferred or credited here.
    battery_center = (0.0, 76.0, 530.0)
    battery_shape = box(*BATTERY["size_mm"], battery_center, 4)
    cassette_outer = box(84.0, 49.0, 205.0, battery_center, 6)
    cassette_inner = box(76.0, 41.0, 197.0, battery_center, 4)
    cassette_shape = cassette_outer.cut(cassette_inner)
    add("EQ-T01-BATTERY-PACK", "T01", "legacy onboard-energy packaging envelope",
        f"REJECTED direct source: Grepow/Tattu {BATTERY['model']} 4S pack; envelope retained for redesign visibility only",
        battery_shape, BATTERY["mass_kg"], 0.0, 0.0,
        "rear-torso removable battery cassette datum X=0, Y=+76, Z=530 mm", "+Y keyed cassette withdrawal",
        "high-current power and balance/telemetry connectors SELECTION REQUIRED; no BMS/PCM inferred",
        BATTERY["url"], BATTERY["revision"],
        "manufacturer publishes 193 x 72 x 37 mm, 1057 g, 14.8 V, 12 Ah and 30C; direct actuator-bus use rejected because 14.8 V nominal equals the XH/XM published maximum and charged maximum is not closed",
        "torso", battery)
    add("EQ-T01-BATTERY-CASSETTE", "T01", "battery enclosure and retention",
        "84 x 49 x 205 mm removable ventilated metal cassette candidate",
        cassette_shape, 0.220, 0.0, 0.0,
        "four-point rear-torso frame interface around battery datum", "+Y tool-released cassette withdrawal",
        "mechanical keying, secondary retention, venting, containment and fall-load path SELECTION REQUIRED",
        "SELECTION REQUIRED", "SELECTION REQUIRED",
        "dimensioned hollow cassette geometry and mass allowance only; no impact/fire/retention credit",
        "torso", safety)
    add("EQ-T01-BATTERY-PROTECTION", "T01", "battery protection and telemetry",
        "4S high-current protection, cell monitor and temperature interface reservation; exact hardware SELECTION REQUIRED",
        box(70, 6, 24, (0, 98, 530), 1.5), 0.080, 0.8, 1.5,
        "inside rear cassette service wall", "+Y cassette service",
        "cell taps, dual temperature inputs, pack current, precharge and hardwired inhibit; ratings/pinout open",
        "SELECTION REQUIRED", "SELECTION REQUIRED",
        "pack product page does not state integrated BMS/PCM; independent protection remains mandatory and unselected",
        "torso", safety)

    # Head HMI/sensing stack. The 4-inch panel replaces the former BOM 5-inch
    # concept because it fits the controlled 116 x 58 mm face window.
    add("EQ-H01-DISPLAY", "H01", "face display",
        "Waveshare 4inch HDMI LCD (H), SKU 16340, rotated landscape candidate",
        box(98, 14.6, 58, (0, -48, 704), 3), 0.123, 5.0, 4.0,
        "rear of face bezel", "-Y bezel withdrawal",
        "remote micro-HDMI-to-full-HDMI link from torso Pi 5, separately protected 5 V, and optional touch SPI; direct GPIO stacking rejected by packaging",
        "https://www.waveshare.com/4inch-HDMI-LCD-H.htm", "live manufacturer product page; accessed 2026-08-14",
        "manufacturer lists 4-inch 480x800 display and 0.123 kg; final 3D drawing/incoming fit required",
        "head", sensor)
    for side, x in (("L", 34), ("R", -34)):
        add(f"EQ-H01-CAMERA-{side}", "H01", "stereo/wide vision",
            "Raspberry Pi Camera Module 3 Wide candidate",
            box(25, 12.4, 24, (x, -51, 744), 2), 0.012, 1.5, 1.2,
            "upper face bezel camera datum", "-Y bezel withdrawal",
            "official Standard-Mini camera cable family: Pi 5 22-way FPC to Camera Module 3 15-pin FPC; 300 mm route candidate; privacy indicator interlock open",
            "https://www.raspberrypi.com/products/camera-module-3/", "live official product page; accessed 2026-08-14",
            "25 x 24 x 12.4 mm Wide envelope verified; 12 g installed allowance is not published mass",
            "head", sensor)
    add("EQ-H01-MIC-ARRAY", "H01", "far-field microphone array",
        "Seeed Studio reSpeaker Flex XVF3800 Linear-4, SKU 100099135, microphone daughterboard candidate",
        box(110, 10, 18, (0, -48, 664), 2), 0.040, 0.1, 0.1,
        "lower face bezel isolated mount", "-Y bezel withdrawal",
        "included 24-pin 0.5 mm-pitch 200 mm FPC to rear-head XVF3800 core; acoustic seals, vibration isolation and privacy mute circuit open",
        "https://www.seeedstudio.com/reSpeaker-Flex-XVF3800-Linear-4-p-6738.html",
        "live official product page and wiki updated 2026-03-26; accessed 2026-08-16",
        "110 x 10 x 18 mm planning envelope derived from the published 4 x 33 mm microphone spacing; official 2D DXF and received-board fit remain required", "head", audio)
    for side, x in (("L", 58), ("R", -58)):
        add(f"EQ-H01-SPEAKER-{side}", "H01", "speech output",
            "Seeed Studio Mono Enclosed Speaker 4R 5W, SKU 114993346 candidate",
            box(12, 40, 40, (x, 22, 704), 3), 0.030, 0.0, 5.0,
            "head side acoustic baffle", f"{'+' if x > 0 else '-'}X side-cover service",
            "two-wire 4 ohm speaker link from reSpeaker Flex core; exact mating connector, grille, seal and acoustic test open",
            "https://www.seeedstudio.com/Mono-Enclosed-Speaker-4R-5W-p-5931.html",
            "live official product page; accessed 2026-08-16",
            "40 mm planning envelope/mass allowance remains subject to received-part measurement", "head", audio)
    add("EQ-H01-AUDIO-AMP", "H01", "audio amplifier",
        "Seeed Studio reSpeaker Flex XVF3800 core board included with SKU 100099135 candidate",
        box(65, 12, 45, (0, 35, 676), 2), 0.055, 12.0, 3.0,
        "rear head electronics tray", "+Y rear-cover withdrawal",
        "locking PH2.0 USB UAC/DFU host link, 12 V auxiliary power, included 24-pin microphone FPC and two 4 ohm speaker outputs; exact connector contacts and gain/EMC validation open",
        "https://wiki.seeedstudio.com/respeaker_flex_introduction/",
        "official wiki updated 2026-03-26; accessed 2026-08-16",
        "65 x 12 x 45 mm planning envelope; official 2D/3D files and received-board fit remain required", "head", audio)
    add("EQ-H01-FAN", "H01", "head ventilation",
        "Sunon MF30100V3-10000-A99 30 x 30 x 10 mm 5 V fan candidate",
        box(30, 10, 30, (0, 43, 739), 2), 0.0078, 0.23, 0.23,
        "rear head vent frame", "+Y rear-cover withdrawal",
        "5 V two-wire fan; protected feed, current-based failure detection, filter, duct, noise and finger guard open; no tach signal inferred",
        "https://www.sunon.com/eu/MANAGE/Docs/PRODUCT/299/502/DC%20Fan_20241225%28255-E%29.pdf",
        "Sunon DC fan catalog dated 2024-12-25; accessed 2026-08-16",
        "manufacturer lists 5 V, 45 mA, 0.23 W, 6000 rpm, 2.5 CFM, 10.2 dBA and 7.8 g; exact received lead/connector suffix remains open", "head", compute)

    # Foot sensing, soles and gripper contact pads are visible functional items.
    for side, sign, link in (("L", 1, "L_foot"), ("R", -1, "R_foot")):
        x0 = sign * body.HIP_HALF_WIDTH
        add(f"EQ-F0{1 if side == 'L' else 2}-SOLE", f"F0{1 if side == 'L' else 2}", "compliant sole",
            "replaceable 2.5 mm patterned TPU/rubber tread candidate", box(86, 138, 2.5, (x0, 25, 1.25), 2),
            0.0375, 0, 0, "underside of sole carrier", "-Z replacement",
            "mechanical adhesive/fastener pattern; friction/wear selection open",
            "SELECTION REQUIRED", "SELECTION REQUIRED", "planning geometry/mass only", link, compliant)
        for iy, y in enumerate((-18, 68), start=1):
            for ix, dx in enumerate((-25, 25), start=1):
                add(f"EQ-F0{1 if side == 'L' else 2}-LOAD-{iy}{ix}", f"F0{1 if side == 'L' else 2}",
                    "foot normal-force sensor", "miniature load-cell/force-sensor puck candidate",
                    box(18, 18, 6, (x0 + dx, y, 10), 2), 0.010, 0.05, 0.05,
                    "sole carrier four-corner datum", "+Z top-cover service",
                    "four-wire bridge or local ADC; overload stop and calibration open",
                    "SELECTION REQUIRED", "SELECTION REQUIRED", "planning envelope/mass only", link, sensor)

    for side, sign, link in (("L", 1, "L_hand"), ("R", -1, "R_hand")):
        for finger, x in (("INBOARD", sign * (body.WRIST_X - 13)), ("OUTBOARD", sign * (body.WRIST_X + 13))):
            add(f"EQ-G0{1 if side == 'L' else 2}-{finger}-PAD", f"G0{1 if side == 'L' else 2}",
                "gripper contact pad", "replaceable compliant urethane/silicone pad candidate",
                box(16, 4, 8, (x, -24, body.FINGERTIP_Z), 1.5), 0.005, 0, 0,
                "finger contact land", "-Y replacement",
                "mechanical captive pocket/adhesive selection open",
                "SELECTION REQUIRED", "SELECTION REQUIRED", "planning geometry/mass only", link, compliant)

    # Installed harness bundles occupy the already-controlled route corridors.
    fab_parts, _panels, routes = fabrication.build()
    route_by_id = {row["route_id"]: row for row in routes}
    for part in fab_parts:
        if part.role != "harness corridor reference":
            continue
        route = route_by_id[part.name]
        diameter = float(route["corridor_diameter_mm"])
        length_mm = part.shape.Volume() / (3.141592653589793 * (diameter / 2.0) ** 2)
        power_route = route["service_class"] == "ACTUATOR POWER"
        linear_mass = 0.040 if power_route else 0.024
        mass = length_mm / 1000.0 * linear_mass + 0.012
        link = "base_link" if "LEG" in part.name else ("torso" if "TORSO" in part.name or "HEAD" in part.name else "torso")
        add(f"EQ-{part.name}", "HN01", "installed harness bundle",
            f"segregated {'power' if power_route else 'data/encoder'} cable bundle plus two connector allowances",
            part.shape, mass, 0, 0, "controlled route corridor", "module-end connector withdrawal",
            route["connector_boundary"], "SELECTION REQUIRED", "SELECTION REQUIRED",
            f"{length_mm:.1f} mm route-derived planning length; conductor/connector selection remains open", link, harness)

    # Distributed installation hardware is explicit mass, but its envelope is a
    # distribution region rather than a claim that screws occupy a solid block.
    for item_id, module, link, center, dims, mass in (
        ("EQ-FST-CENTRAL", "T01/P01/H01", "base_link", (0, 0, 478), (110, 60, 120), 0.120),
        ("EQ-FST-LEFT-ARM", "A01/G01", "L_upper_arm", (128, 0, 410), (48, 40, 180), 0.040),
        ("EQ-FST-RIGHT-ARM", "A02/G02", "R_upper_arm", (-128, 0, 410), (48, 40, 180), 0.040),
        ("EQ-FST-LEFT-LEG", "L01/F01", "L_thigh", (62.5, 0, 220), (58, 50, 360), 0.070),
        ("EQ-FST-RIGHT-LEG", "L02/F02", "R_thigh", (-62.5, 0, 220), (58, 50, 360), 0.070),
    ):
        add(item_id, module, "distributed fasteners/inserts/retainers",
            "metric service fastener set; exact count/grade/torque/locking SELECTION REQUIRED",
            box(*dims, center, 2), mass, 0, 0, "distributed mounting interfaces", "tool-access directions per panel register",
            "mechanical only", "SELECTION REQUIRED", "SELECTION REQUIRED",
            "mass distribution envelope only; not literal merged fastener geometry", link, safety)

    return items


def update_package(items: list[Equipment]) -> None:
    physical = cq.Compound.makeCompound([item.shape for item in items])
    step = OUT / "HR-30_installed_equipment_candidate.step"
    cq.exporters.export(physical, str(step))
    body.canonicalize_step(step)
    assembly = cq.Assembly(name="HR30_INSTALLED_EQUIPMENT_IN_WHOLE_BODY_P01_NOT_RELEASED")
    fab_parts, _panels, _routes = fabrication.build()
    integrated_solids = [part.shape for part in fab_parts if part.density_kg_m3 > 1.0]
    for part in fab_parts:
        if part.density_kg_m3 <= 1.0:
            continue
        assembly.add(part.shape, name=f"BODY_{part.name}", color=cq.Color(*part.color))
    body_components, _axes, _bindings, _transforms = body.build()
    for part in body_components:
        if not (
            part.name.startswith("JMOD_")
            or part.name.startswith("FACE_")
            or "HAND_PALM" in part.name
            or "GRIPPER_FINGER" in part.name
            or "SOFT_PAD_LAND" in part.name
        ):
            continue
        visual = part.visual_shape if part.visual_shape is not None else part.shape
        assembly.add(visual, name=f"BODY_{part.name}", color=cq.Color(*part.color))
        if part.physical:
            integrated_solids.append(part.shape)
    for item in items:
        assembly.add(item.shape, name=item.item_id, color=cq.Color(*item.color))
    assembly.save(str(OUT / "HR-30_installed_equipment_candidate.glb"))
    integrated_solids.extend(item.shape for item in items)
    integrated_step = OUT / "HR-30_integrated_whole_robot_candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(integrated_solids), str(integrated_step))
    body.canonicalize_step(integrated_step)

    rows = []
    for item in items:
        bb = item.shape.BoundingBox()
        c = item.shape.Center()
        rows.append({
            "item_id": item.item_id, "module": item.module, "role": item.role, "candidate": item.candidate,
            "bbox_x_mm": f"{bb.xlen:.3f}", "bbox_y_mm": f"{bb.ylen:.3f}", "bbox_z_mm": f"{bb.zlen:.3f}",
            "center_x_mm": f"{c.x:.3f}", "center_y_mm": f"{c.y:.3f}", "center_z_mm": f"{c.z:.3f}",
            "planning_mass_kg": f"{item.planning_mass_kg:.6f}", "operating_power_w": f"{item.power_w:.3f}",
            "candidate_heat_w": f"{item.heat_w:.3f}", "mounting_plane": item.mounting_plane,
            "service_direction": item.service_direction, "connector_boundary": item.connector_boundary,
            "dynamic_link": item.dynamic_link, "evidence_state": item.evidence_state, "warning": WARNING,
        })
    write_csv(OUT / "installed-equipment-register.csv", rows)
    source_rows = []
    seen = set()
    for item in items:
        key = (item.candidate, item.source_url)
        if key in seen:
            continue
        seen.add(key)
        source_rows.append({
            "candidate": item.candidate, "manufacturer_source_url": item.source_url,
            "document_revision_or_date": item.source_revision, "accessed_date": ACCESSED,
            "verified_or_provisional": item.evidence_state, "selection_state": "CANDIDATE / SELECTION REQUIRED",
            "warning": WARNING,
        })
    write_csv(OUT / "installed-equipment-source-register.csv", source_rows)
    operating_current = 179.0 / BATTERY["nominal_voltage_v"]
    peak_current = 727.0 / BATTERY["nominal_voltage_v"]
    usable_energy = BATTERY["energy_wh"] * 0.75
    write_csv(OUT / "battery-energy-source-register.csv", [{
        "manufacturer": BATTERY["manufacturer"], "model": BATTERY["model"],
        "nominal_voltage_v": f"{BATTERY['nominal_voltage_v']:.1f}",
        "capacity_ah": f"{BATTERY['capacity_ah']:.1f}", "published_energy_wh": f"{BATTERY['energy_wh']:.1f}",
        "published_discharge_rate_c": f"{BATTERY['discharge_c']:.1f}",
        "published_mass_kg": f"{BATTERY['mass_kg']:.3f}",
        "published_dimensions_mm": "193 x 72 x 37",
        "arithmetic_30c_current_a": f"{BATTERY['capacity_ah'] * BATTERY['discharge_c']:.1f}",
        "whole_robot_operating_current_screen_a": f"{operating_current:.3f}",
        "whole_robot_short_peak_current_screen_a": f"{peak_current:.3f}",
        "planning_usable_energy_75pct_wh": f"{usable_energy:.1f}",
        "ideal_budget_runtime_at_179w_min": f"{usable_energy / 179.0 * 60.0:.1f}",
        "official_url": BATTERY["url"], "document_revision_or_date": BATTERY["revision"],
        "protection_boundary": "NO INTEGRATED BMS/PCM CLAIM; REJECTED FOR DIRECT ACTUATOR BUS: 14.8 V nominal equals the XH/XM published maximum and the page does not close charged maximum; envelope retained as legacy geometry only",
        "selection_state": "REJECTED DIRECT SOURCE - LEGACY GEOMETRY ONLY - SUPERSEDED BY ENERGY-SAFETY-SPINE-P0.1", "warning": WARNING,
    }])

    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "installed_item_count": len(items),
        "planning_installed_mass_kg": round(sum(item.planning_mass_kg for item in items), 9),
        "modeled_operating_power_w": round(sum(item.power_w for item in items), 3),
        "modeled_candidate_heat_w": round(sum(item.heat_w for item in items), 3),
        "all_geometry_valid": all(item.shape.isValid() for item in items),
        "minimum_z_mm": min(item.shape.BoundingBox().zmin for item in items),
        "maximum_z_mm": max(item.shape.BoundingBox().zmax for item in items),
        "empty_component_bays_replaced": True, "tether_first_configuration": True,
        "tether_development_interface_retained": True,
        "onboard_energy_candidate_geometry_present": True,
        "onboard_energy_installed": False, "exact_selections_closed": False,
        "electrical_schematic_released": False, "thermal_validated": False,
        "fabrication_authority": False, "powered_test_authority": False,
        "motion_authority": False, "energization_authority": False,
    }
    (OUT / "installed-equipment-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(Path(__file__), OUT / "installed-equipment-source.py")

    readme_path = OUT / "README.md"
    readme = re.sub(r"(?:^|\n)## Installed equipment layout[\s\S]*?(?=\n## |\Z)", "", readme_path.read_text(encoding="utf-8")).rstrip()
    readme += f"""

## Installed equipment layout

The former empty torso, pelvis, head and foot reservations now contain {len(items)} located equipment, harness, contact, sole and installation-hardware candidates with explicit mounting planes, service directions, connector boundaries and dynamic-link placement. Their provisional as-installed planning mass is {status['planning_installed_mass_kg']:.3f} kg. Eight bus-specific 124 x 45 mm walking-power board instances are now visibly installed in the pelvis, torso and both thighs; no board input serves more than one actuator bus or regulator output. The rear-torso model retains the former Grepow/Tattu pack envelope so the superseded packaging assumption remains visible, but that direct 4S source is rejected. Tether-first is the primary development configuration; Bioenno BLF-1209WS remains an onboard-later evaluation candidate requiring a new cassette. Battery current delivery, containment, retention, connector, charger, thermal and abuse evidence remain open.
"""
    readme_path.write_text(readme.rstrip() + "\n", encoding="utf-8", newline="\n")

    index_path = OUT / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(r'<section id="equipment-layout">[\s\S]*?</section>', "", html)
    insert = f'''<section id="equipment-layout"><h2>Installed equipment—not empty bays</h2><div class="viewer"><model-viewer src="HR-30_installed_equipment_candidate.glb" alt="Interactive 3D layout of preliminary HR-30 installed electronics, eight bus-specific walking-power boards, legacy battery envelope, sensing, harness, soles and contact hardware" camera-controls camera-orbit="35deg 76deg 95%" field-of-view="26deg" shadow-intensity="0.8" exposure="1.05"></model-viewer><p>{len(items)} located candidate items, {status['planning_installed_mass_kg']:.3f} kg provisional as-installed mass. Eight one-bus walking-power boards are visible in the pelvis, torso and thighs. The rear-torso battery envelope is retained as rejected legacy geometry; tether-first is primary and every physical energy selection remains open.</p><p><a href="installed-equipment-register.csv">Equipment register</a> · <a href="HR-30_installed_equipment_candidate.step">Equipment STEP</a> · <a href="HR-30_integrated_whole_robot_candidate.step">Integrated whole-robot STEP</a> · <a href="battery-energy-source-register.csv">Battery-source boundary</a>.</p></div></section>'''
    html = html.replace("</main>", insert + "</main>")
    html = re.sub(r'<a href="installed-equipment-register\.csv">Installed equipment</a>[\s\S]*?(?=<a href="mass-properties-budget\.csv">)', "", html, count=1)
    html = html.replace('<a href="mass-properties-budget.csv">Mass/COM/inertia</a>', '<a href="installed-equipment-register.csv">Installed equipment</a> · <a href="installed-equipment-source-register.csv">Equipment sources</a> · <a href="battery-energy-source-register.csv">Battery source and runtime screen</a> · <a href="HR-30_installed_equipment_candidate.step">Equipment STEP</a> · <a href="HR-30_integrated_whole_robot_candidate.step">Integrated whole-robot STEP</a> · <a href="mass-properties-budget.csv">Mass/COM/inertia</a>')
    index_path.write_text(html, encoding="utf-8", newline="\n")

    bom_path = OUT / "whole-robot-candidate-bom.csv"
    bom = list(csv.DictReader(bom_path.open(encoding="utf-8")))
    for row in bom:
        if row["item_id"] == "HR30-BOM-011":
            row["manufacturer"] = "Waveshare"
            row["candidate"] = "4inch HDMI LCD (H), SKU 16340, rotated landscape; installed envelope/mass modeled"
        elif row["item_id"] == "HR30-BOM-030":
            row["candidate"] = "12 located route-derived cable bundles with connector mass allowances; exact conductors/connectors/fill/EMC/current remain open"
        elif row["item_id"] == "HR30-BOM-031":
            row["candidate"] = "Pi Active Cooler plus head tach fan; installed envelopes/masses modeled; torso duct/fan selection open"
        elif row["item_id"] == "HR30-BOM-032":
            row["candidate"] = "distributed 0.340 kg planning allowance placed by module; exact counts/grades/torques/locking remain open"
    write_csv(bom_path, bom)

    package_status_path = OUT / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({
        "installed_equipment_layout_present": True,
        "installed_equipment_item_count": len(items),
        "installed_equipment_planning_mass_kg": status["planning_installed_mass_kg"],
        "empty_component_bays_only": False,
        "tether_first_equipment_configuration": True,
        "tether_development_interface_retained": True,
        "onboard_energy_candidate_geometry_present": True,
        "onboard_energy_installed": False,
    })
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")

    holds_path = OUT / "open-holds.csv"
    holds = list(csv.DictReader(holds_path.open(encoding="utf-8")))
    for row in holds:
        if row["hold_id"] == "HR30-P01-H04":
            row["unresolved_item"] = ("The whole-body CAD retains the superseded 177.6 Wh Grepow/Tattu pack envelope only as legacy packaging evidence; that direct 4S actuator-bus source is rejected. Tether-first is the active development configuration, while the Bioenno BLF-1209WS remains an onboard-later evaluation candidate requiring a new cassette. Exact battery configuration, protection, connector, current/thermal capability, containment, retention, charger, regeneration handling, grounding and pinout remain unselected and unvalidated.")
        elif row["hold_id"] == "HR30-P01-H07":
            row["unresolved_item"] = ("Fourteen module harness assemblies and 62 route segments now have planning geometry, mass allowances and connector boundaries, including separate neck power/data paths and 25 individually routed actuator-power pairs from eight bus-specific walking-power boards. Exact conductor selections, fill, flex life, service-loop validation, production connectors, strain relief, shielding, current derating, EMC and thermal evidence remain open.")
    write_csv(holds_path, holds)


def main() -> int:
    required = (OUT / "HR-30_modular_fabrication_candidate.step", OUT / "whole-robot-candidate-bom.csv")
    if not all(path.exists() for path in required):
        raise RuntimeError("generate body/system/fabrication artifacts before installed equipment")
    items = build()
    update_package(items)
    manifest = OUT / "file-manifest.csv"
    if manifest.exists():
        manifest.unlink()
    files = [path for path in OUT.rglob("*") if path.is_file()]
    write_csv(manifest, [{"path": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size,
                         "sha256": sha256(path), "warning": WARNING} for path in sorted(files)])
    release = ROOT / "release" / "hr30" / "whole-body-p0.1"
    if release.exists():
        shutil.rmtree(release)
    shutil.copytree(OUT, release)
    print(json.dumps({"identifier": IDENTIFIER, "items": len(items),
                      "planning_mass_kg": sum(item.planning_mass_kg for item in items)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
