#!/usr/bin/env python3
"""Generate the HR-30 head HMI physical harness candidate.

This package turns the installed head equipment into explicit camera, display,
audio, privacy and cooling links.  Manufacturer cable internals are treated as
opaque assemblies; no unpublished pinout, connector order code or rating is
invented.  Nothing generated here grants work or energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "head-hmi-harness-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-HEAD-HMI-HARNESS-P0.1"
DATE = "2026-08-16"
WARNING = "PRELIMINARY - UNBUILT HEAD HMI HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
AUTHORITY = "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED-TEST, MOTION OR ENERGIZATION AUTHORITY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def common(row: dict[str, object]) -> dict[str, object]:
    return {**row, "execution_state": "NOT EXECUTED", "authority": AUTHORITY, "warning": WARNING}


def sources() -> list[dict[str, object]]:
    data = [
        ("HH-S01", "Raspberry Pi", "Camera Module 3 product page", "live page; accessed 2026-08-16", "https://www.raspberrypi.com/products/camera-module-3/?variant=camera-module-3-wide", "camera-side 15 x 1 mm FPC; Wide dimensions 25 x 24 x 12.4 mm; 120 degree diagonal FOV"),
        ("HH-S02", "Raspberry Pi", "Camera hardware documentation", "live documentation; accessed 2026-08-16", "https://www.raspberrypi.com/documentation/accessories/camera.html", "all Raspberry Pi cameras use standard 15-pin connector; Pi 5 uses mini 22-pin connector and Standard-Mini cable"),
        ("HH-S03", "Raspberry Pi", "Camera Cable", "live product page; accessed 2026-08-16", "https://www.raspberrypi.com/products/camera-cable/?variant=camera-cable-std-mini-300", "shielded Standard-Mini family offered in 200, 300 and 500 mm lengths; exact order code not published on page"),
        ("HH-S04", "Raspberry Pi", "15 to 22 pin camera cables Rev 2 PCN", "RP-009201-PC-1; Rev 2; updated 2025-10-06", "https://pip-assets.raspberrypi.com/categories/1267-pcn/documents/RP-009201-PC-1-15%20to%2022%20pin%20camera%20cables%20Rev%202.pdf", "current manufacturer change record for Standard-Mini camera cable construction"),
        ("HH-S05", "Raspberry Pi", "Raspberry Pi 5 product brief", "RP-008348-DS-5; accessed 2026-08-16", "https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-5-raspberry-pi-5-product-brief.pdf", "two four-lane MIPI camera/display transceivers; two cameras consume both shared MIPI ports"),
        ("HH-S06", "Waveshare", "4inch HDMI LCD (H)", "SKU 16340; live product page; accessed 2026-08-16", "https://www.waveshare.com/product/4inch-hdmi-lcd-h.htm", "480 x 800 HDMI display, SPI resistive touch, 0.123 kg; package includes HDMI-to-micro-HDMI adapter"),
        ("HH-S07", "Waveshare", "4inch HDMI LCD (H) wiki", "live wiki; accessed 2026-08-16", "https://www.waveshare.com/wiki/4inch_HDMI_LCD_%28H%29", "26-pin interface: 5 V on 2/4, grounds 6/9/14/20/25, touch SPI on 19/21/22/23/26"),
        ("HH-S08", "Seeed Studio", "reSpeaker Flex XVF3800 Linear-4", "SKU 100099135; live product page; accessed 2026-08-16", "https://www.seeedstudio.com/reSpeaker-Flex-XVF3800-Linear-4-p-6738.html", "current in-stock split four-microphone embodied-AI candidate"),
        ("HH-S09", "Seeed Studio", "reSpeaker Flex getting-started guide", "official wiki updated 2026-03-26; accessed 2026-08-16", "https://wiki.seeedstudio.com/respeaker_flex_introduction/", "USB UAC 2.0/DFU, locking PH2.0, 24-pin 0.5 mm FPC with included 200 mm cable, 12 V external input, 4-ohm speaker output"),
        ("HH-S10", "Seeed Studio", "Mono Enclosed Speaker 4R 5W", "SKU 114993346; live product page; accessed 2026-08-16", "https://www.seeedstudio.com/Mono-Enclosed-Speaker-4R-5W-p-5931.html", "current 4-ohm 5-watt enclosed-speaker candidate; exact received dimensions/lead termination remain open"),
        ("HH-S11", "Sunon", "30 x 30 x 10 mm DC fan catalog", "catalog dated 2024-12-25; accessed 2026-08-16", "https://www.sunon.com/eu/MANAGE/Docs/PRODUCT/299/502/DC%20Fan_20241225%28255-E%29.pdf", "MF30100V3-10000-A99: 5 V, 45 mA, 0.23 W, 6000 rpm, 2.5 CFM, 10.2 dBA, 7.8 g; no tach output inferred"),
    ]
    return [common({"source_id": i, "publisher": p, "document": d, "revision_or_date": rev, "official_url": url, "verified_scope": scope}) for i, p, d, rev, url, scope in data]


def bindings() -> list[dict[str, object]]:
    data = [
        ("HH-B01", "whole-body installed equipment", "installed-equipment-register.csv"),
        ("HH-B02", "whole-body physical harness status", "harness/physical-p0.1/physical-harness-status.json"),
        ("HH-B03", "physical equipment interfaces", "harness/physical-p0.1/equipment-interface-register.csv"),
        ("HH-B04", "physical routed segments", "harness/physical-p0.1/route-segment-register.csv"),
        ("HH-B05", "compute/HMI budget source", "whole-robot-candidate-bom.csv"),
        ("HH-B06", "embodied-agent/local-control boundary", "embodied-agent-architecture.md"),
    ]
    result = []
    for ident, role, rel in data:
        path = WHOLE / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        result.append(common({"binding_id": ident, "role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    return result


def equipment() -> list[dict[str, object]]:
    ids = ["EQ-H01-DISPLAY", "EQ-H01-CAMERA-L", "EQ-H01-CAMERA-R", "EQ-H01-MIC-ARRAY", "EQ-H01-SPEAKER-L", "EQ-H01-SPEAKER-R", "EQ-H01-AUDIO-AMP", "EQ-H01-FAN"]
    source = {row["item_id"]: row for row in read_csv(WHOLE / "installed-equipment-register.csv")}
    if set(ids) - set(source):
        raise RuntimeError("head installed-equipment coverage drift")
    return [common({
        "item_id": ident, "role": source[ident]["role"], "candidate": source[ident]["candidate"],
        "center_xyz_mm": f"({source[ident]['center_x_mm']},{source[ident]['center_y_mm']},{source[ident]['center_z_mm']})",
        "envelope_mm": f"{source[ident]['bbox_x_mm']} x {source[ident]['bbox_y_mm']} x {source[ident]['bbox_z_mm']}",
        "planning_mass_kg": source[ident]["planning_mass_kg"], "connector_boundary": source[ident]["connector_boundary"],
        "fit_verified": "NO", "procurement_released": "NO",
    }) for ident in ids]


def links() -> list[dict[str, object]]:
    data = [
        ("HH-L01", "left vision", "EQ-T01-PI5 CAM/DISP0 22-way", "EQ-H01-CAMERA-L 15-pin", "Raspberry Pi Standard-Mini Camera Cable 300 mm candidate", "OPAQUE MANUFACTURER CABLE - INTERNAL PIN MAP NOT RECREATED", 300, 221),
        ("HH-L02", "right vision", "EQ-T01-PI5 CAM/DISP1 22-way", "EQ-H01-CAMERA-R 15-pin", "Raspberry Pi Standard-Mini Camera Cable 300 mm candidate", "OPAQUE MANUFACTURER CABLE - INTERNAL PIN MAP NOT RECREATED", 300, 221),
        ("HH-L03", "face video", "EQ-T01-PI5 HDMI0 micro-HDMI", "EQ-H01-DISPLAY full-size HDMI", "shielded flexible micro-HDMI-to-HDMI cable, 300 mm candidate", "EXACT CABLE/RETENTION SELECTION REQUIRED", 300, 179),
        ("HH-L04", "face power", "HN01 protected 5 V head branch", "EQ-H01-DISPLAY 5 V/GND", "keyed two-conductor flexible harness", "WIRE/CONTACT/PROTECTION SELECTION REQUIRED", 260, 0),
        ("HH-L05", "touch SPI", "EQ-T01-PI5 protected GPIO/SPI breakout", "EQ-H01-DISPLAY pins 19/21/22/23/26 plus reference", "keyed shielded low-voltage harness", "REMOTE BREAKOUT/LEVEL/CONNECTOR SELECTION REQUIRED", 300, 179),
        ("HH-L06", "audio USB", "EQ-T01-PI5 USB 2.0", "EQ-H01-AUDIO-AMP locking PH2.0 USB", "locking PH2.0 USB UAC/DFU harness candidate", "EXACT PH2.0 CABLE ASSEMBLY/PI-END RETENTION REQUIRED", 300, 157),
        ("HH-L07", "audio power", "HN01 protected 12 V auxiliary branch", "EQ-H01-AUDIO-AMP external power terminal", "keyed two-conductor flexible harness", "WIRE/CONTACT/PROTECTION SELECTION REQUIRED", 240, 0),
        ("HH-L08", "microphone array", "EQ-H01-AUDIO-AMP 24-pin FPC", "EQ-H01-MIC-ARRAY 24-pin FPC", "included keyed 24-pin 0.5 mm-pitch 200 mm FPC", "MANUFACTURER ASSEMBLY; RETENTION/ACOUSTIC ROUTE VALIDATION OPEN", 200, 84),
        ("HH-L09", "left speech", "EQ-H01-AUDIO-AMP speaker output L", "EQ-H01-SPEAKER-L 4 ohm", "two-conductor speaker lead", "EXACT JST/LEAD POLARITY/STRAIN RELIEF REQUIRED", 180, 72),
        ("HH-L10", "right speech", "EQ-H01-AUDIO-AMP speaker output R", "EQ-H01-SPEAKER-R 4 ohm", "two-conductor speaker lead", "EXACT JST/LEAD POLARITY/STRAIN RELIEF REQUIRED", 180, 72),
        ("HH-L11", "head cooling", "HN01 protected 5 V head branch", "EQ-H01-FAN red/black leads", "two-conductor fan harness", "EXACT MATING CONNECTOR/PROTECTION/CURRENT SENSE REQUIRED", 180, 68),
    ]
    return [common({"link_id": i, "service": service, "from_interface": start, "to_interface": end, "candidate_assembly": cable, "contact_definition": contacts, "candidate_length_mm": length, "straight_line_screen_mm": straight, "length_margin_mm": length - straight if straight else "ROUTE MEASUREMENT REQUIRED", "physical_link_built": "NO"}) for i, service, start, end, cable, contacts, length, straight in data]


def routes(link_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    data = [
        ("HH-R01", "HH-L01", "torso compute tray -> left neck service channel -> left upper bezel", "45 mm minimum candidate; exact FFC supplier limit open", "two broad-radius clamps; no fold at connector"),
        ("HH-R02", "HH-L02", "torso compute tray -> right neck service channel -> right upper bezel", "45 mm minimum candidate; exact FFC supplier limit open", "two broad-radius clamps; no fold at connector"),
        ("HH-R03", "HH-L03", "torso compute tray -> segregated neck signal channel -> rear face display", "30 mm candidate", "connector shell retention at both ends"),
        ("HH-R04", "HH-L04", "head power trunk -> display rear", "10 x cable OD candidate", "service disconnect before bezel removal"),
        ("HH-R05", "HH-L05", "torso GPIO breakout -> segregated neck signal channel -> display touch header", "10 x cable OD candidate", "keyed remote adapter; direct stacking prohibited"),
        ("HH-R06", "HH-L06", "torso compute tray -> neck data channel -> rear head audio tray", "10 x cable OD candidate", "locking head end; retained Pi end"),
        ("HH-R07", "HH-L07", "head auxiliary power trunk -> rear head audio tray", "10 x cable OD candidate", "separate from microphone FPC"),
        ("HH-R08", "HH-L08", "rear head audio tray -> side-return loop -> lower face microphone array", "20 mm candidate; manufacturer FPC limit not published", "no sharp fold; isolated from speaker baffles"),
        ("HH-R09", "HH-L09", "rear head audio tray -> left acoustic baffle", "10 x cable OD candidate", "strain relief before removable side cover"),
        ("HH-R10", "HH-L10", "rear head audio tray -> right acoustic baffle", "10 x cable OD candidate", "strain relief before removable side cover"),
        ("HH-R11", "HH-L11", "head power trunk -> rear vent frame", "10 x cable OD candidate", "guarded away from blades; service plug before fan frame"),
    ]
    return [common({"route_id": i, "link_id": link, "route_description": desc, "minimum_bend_radius": bend, "retention_and_service_rule": retention, "neck_worst_pose_checked": "NO", "interference_checked": "NO"}) for i, link, desc, bend, retention in data]


def controls() -> list[dict[str, object]]:
    data = [
        ("HH-C01", "camera electrical activity indication", "dedicated externally visible indicator driven by deterministic local I/O", "SELECTION REQUIRED", "software UI icon alone is not credited"),
        ("HH-C02", "camera disable", "hardware removal/gate of both camera links or camera supply where manufacturer-compatible", "SELECTION REQUIRED", "must not damage MIPI interface or imply safety function"),
        ("HH-C03", "microphone hard mute", "serviceable hardware control that removes or gates capture independently of cloud agent", "SELECTION REQUIRED", "software mute alone is not credited"),
        ("HH-C04", "microphone mute indication", "visible local indicator tied to actual mute state", "SELECTION REQUIRED", "human factors and failure-state behavior open"),
        ("HH-C05", "speaker level limit", "deterministic local maximum gain and startup-muted state", "SELECTION REQUIRED", "sound-pressure limit and measurement distance open"),
        ("HH-C06", "face display role", "expressive HMI/status only", "DEFINED", "no safety, guarding or permission indication credit"),
        ("HH-C07", "network/agent loss", "local controller retains HMI/audio safe-state ownership", "DEFINED ARCHITECTURE", "physical implementation and fault injection open"),
        ("HH-C08", "service isolation", "all head links de-energized before bezel, side cover or rear cover removal", "DEFINED PROCEDURAL OBLIGATION", "interlock and connector sequence open"),
    ]
    return [common({"control_id": i, "function": function, "required_architecture": required, "current_state": state, "remaining_evidence": evidence, "validated": "NO"}) for i, function, required, state, evidence in data]


def tests() -> list[dict[str, object]]:
    data = [
        ("HH-T01", "verify both camera cables are Standard-Mini 22-to-15 and record received length/revision", "visual/dimensional", "SELECTION REQUIRED"),
        ("HH-T02", "inspect every FPC insertion, latch and local strain relief", "visual/pull", "SELECTION REQUIRED"),
        ("HH-T03", "sweep neck and head through full unpowered range while monitoring cable bend/clearance", "mm/visual", "SELECTION REQUIRED"),
        ("HH-T04", "verify camera enumeration and left/right identity with robot restrained and motion disabled", "identity", "SELECTION REQUIRED"),
        ("HH-T05", "verify face HDMI mode, rotation and recovery after disconnect", "video", "SELECTION REQUIRED"),
        ("HH-T06", "verify touch SPI polarity, levels and IRQ without direct GPIO stacking", "logic", "SELECTION REQUIRED"),
        ("HH-T07", "verify microphone USB identity, capture channels, mute and indicator state", "audio/state", "SELECTION REQUIRED"),
        ("HH-T08", "measure speaker polarity, gain, distortion and maximum SPL at defined distance", "dBA/percent", "SELECTION REQUIRED"),
        ("HH-T09", "verify camera/microphone privacy controls under host crash and reboot", "fault injection", "SELECTION REQUIRED"),
        ("HH-T10", "measure 5 V and 12 V head branch current/inrush/voltage drop", "A/V", "SELECTION REQUIRED"),
        ("HH-T11", "measure fan current, airflow direction, temperatures, noise and blocked-fan response", "A/degC/dBA", "SELECTION REQUIRED"),
        ("HH-T12", "perform EMC/data-integrity observation with actuators switching on an isolated staged fixture", "errors/noise", "SELECTION REQUIRED"),
    ]
    return [common({"test_id": i, "inspection_or_test": test, "unit_or_method": unit, "acceptance_limit": limit, "measured_value": "NONE", "result": "NOT EXECUTED", "evidence": "NONE"}) for i, test, unit, limit in data]


def holds() -> list[dict[str, object]]:
    data = [
        ("HH-OH01", "exact current order codes for the 300 mm Standard-Mini camera cables are not published on the official product page", "written supplier quotation/label plus received PCN/revision inspection"),
        ("HH-OH02", "camera FFC routing has only a straight-line and nominal-length screen", "as-built route measurement, bend-radius limit, neck sweep and retention test"),
        ("HH-OH03", "remote display HDMI, power and touch breakout assemblies are unselected", "connector/cable order codes, contact map, protection, fit and received assembly"),
        ("HH-OH04", "reSpeaker official 2D/3D geometry and received fit are not reconciled to the planning envelopes", "manufacturer CAD import, collision check and incoming dimensional inspection"),
        ("HH-OH05", "speaker received geometry, mating plug, baffle and acoustic result are open", "received part, controlled drawing, connector/retention and acoustic test"),
        ("HH-OH06", "head auxiliary 5 V/12 V branch protection and conductor sizing are open", "fault/inrush/duty/length/bundling/connector inputs and qualified sizing"),
        ("HH-OH07", "privacy controls and indicators are architecture obligations only", "hardware design, deterministic control, host-fault tests and human-factors review"),
        ("HH-OH08", "fan lead/connector, guard, duct, current-sense failure detection and thermal limits are open", "received fan, harness, guard/duct drawing and thermal/blocked-fan test"),
        ("HH-OH09", "whole-head EMC, speaker-to-microphone coupling and camera data integrity are untested", "instrumented integrated-head test across representative actuator/noise states"),
        ("HH-OH10", "nothing is procured, assembled, connected, powered or qualified", "as-built serial configuration, completed traveler/tests and separate signed authority"),
    ]
    return [common({"hold_id": i, "unresolved_item": item, "closure_evidence": evidence, "state": "OPEN"}) for i, item, evidence in data]


def drawing() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="980" viewBox="0 0 1600 980" role="img" aria-labelledby="title desc"><title id="title">HR-30 head HMI harness candidate</title><desc id="desc">Torso Raspberry Pi links to two head cameras, face display, split microphone and audio system, two speakers and fan.</desc><style>text{{font:600 18px system-ui;fill:#102b46}}.h{{font-size:32px;font-weight:900}}.s{{font-size:16px}}.box{{fill:#fff;stroke:#0b4f91;stroke-width:4}}.data{{stroke:#28a9df;stroke-width:8;fill:none}}.power{{stroke:#f2b91d;stroke-width:9;fill:none}}.audio{{stroke:#6942a7;stroke-width:8;fill:none}}.open{{stroke:#982520;stroke-width:5;stroke-dasharray:14 9;fill:none}}.warn{{fill:#fff0b5;stroke:#982520;stroke-width:4}}</style><rect width="1600" height="980" fill="#eef8ff"/><text class="h" x="45" y="55">HR-30 head HMI physical harness candidate</text><rect class="box" x="55" y="140" width="310" height="330" rx="20"/><text x="85" y="185">Torso Raspberry Pi 5</text><text class="s" x="85" y="225">CAM/DISP0 → left camera</text><text class="s" x="85" y="260">CAM/DISP1 → right camera</text><text class="s" x="85" y="295">HDMI0 → face display</text><text class="s" x="85" y="330">USB 2.0 → audio core</text><text class="s" x="85" y="365">GPIO breakout → touch</text><rect class="box" x="1180" y="105" width="350" height="160" rx="20"/><text x="1215" y="150">Two Camera Module 3 Wide</text><text class="s" x="1215" y="190">Pi 5 22-way → camera 15-pin</text><text class="s" x="1215" y="225">300 mm Standard-Mini candidates</text><rect class="box" x="1180" y="310" width="350" height="150" rx="20"/><text x="1215" y="355">Waveshare face display</text><text class="s" x="1215" y="395">micro-HDMI + protected 5 V</text><text class="s" x="1215" y="430">remote SPI touch; no stacking</text><rect class="box" x="690" y="560" width="380" height="180" rx="20"/><text x="725" y="605">reSpeaker Flex XVF3800 core</text><text class="s" x="725" y="645">locking USB + protected 12 V</text><text class="s" x="725" y="680">24-pin FPC + two 4 Ω outputs</text><rect class="box" x="1160" y="545" width="370" height="185" rx="20"/><text x="1195" y="590">Linear four-mic array</text><text class="s" x="1195" y="630">included 200 mm keyed FPC</text><text class="s" x="1195" y="665">4 × microphones, 33 mm spacing</text><rect class="box" x="420" y="790" width="760" height="105" rx="20"/><text x="455" y="835">Left/right 4 Ω speakers · 5 V two-wire fan · privacy/mute controls OPEN</text><path class="data" d="M365 210 C690 130 875 150 1180 175"/><path class="data" d="M365 290 C690 300 870 370 1180 380"/><path class="data" d="M365 350 C500 460 585 590 690 630"/><path class="audio" d="M1070 645 C1115 640 1125 640 1160 640"/><path class="audio" d="M880 740 C820 780 740 805 680 810"/><path class="power" d="M520 500 C700 500 760 545 825 560"/><path class="power" d="M1070 730 C1110 780 1080 800 1040 810"/><rect class="warn" x="55" y="910" width="1475" height="50" rx="12"/><text class="s" x="85" y="942">{html.escape(WARNING)}</text></svg>'''


def page(eq: list[dict[str, object]], link_rows: list[dict[str, object]], hold_rows: list[dict[str, object]]) -> str:
    equipment_cards = "".join(f"<article><h3>{html.escape(str(r['role']))}</h3><p>{html.escape(str(r['candidate']))}</p><small>{html.escape(str(r['envelope_mm']))}</small></article>" for r in eq)
    link_table = "".join(f"<tr><td>{r['link_id']}</td><td>{html.escape(str(r['service']))}</td><td>{html.escape(str(r['from_interface']))}</td><td>{html.escape(str(r['to_interface']))}</td><td>{html.escape(str(r['candidate_assembly']))}</td><td>{r['candidate_length_mm']}</td></tr>" for r in link_rows)
    hold_list = "".join(f"<li><b>{r['hold_id']}</b> {html.escape(str(r['unresolved_item']))}</li>" for r in hold_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 head HMI harness</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#d9f2ff;--gold:#f2b91d;--paper:#f7fbff;--ink:#142a40;--line:#82c4e6;--red:#982520}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main,footer{{padding:clamp(24px,5vw,64px) max(18px,calc((100vw - 1280px)/2))}}header,footer{{background:linear-gradient(135deg,var(--deep),var(--blue));color:white}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05;max-width:18ch}}h2{{font-size:clamp(28px,4vw,42px)}}h3{{font-size:21px}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:16px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}article,.panel,li{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:18px}}.metric{{font-size:clamp(34px,5vw,54px);font-weight:900;color:var(--blue)}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:16px;background:#fff}}table{{border-collapse:collapse;min-width:1200px;width:100%}}th,td{{padding:14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;font-size:16px}}th{{background:var(--sky)}}small{{font-size:14px}}a{{color:#075b9b;font-weight:800}}img{{width:100%;height:auto;border:2px solid var(--line);border-radius:16px;background:white}}ul{{display:grid;gap:12px;padding:0;list-style:none}}@media(max-width:560px){{body{{font-size:16px}}th,td{{font-size:16px}}}}</style></head><body><header><div class="warning">{html.escape(WARNING)}</div><p>HR-30 whole-body P0.1</p><h1>The robot now has a routed head nervous system.</h1><p>Two corrected camera links, an independently routed face display, current audio hardware and explicit privacy/cooling boundaries replace the former generic head connector notes.</p></header><main><section class="grid"><article><div class="metric">8</div><p>located head equipment items</p></article><article><div class="metric">11</div><p>physical HMI links</p></article><article><div class="metric">2</div><p>22-to-15 camera links</p></article><article><div class="metric">0</div><p>built or powered links</p></article></section><section><h2>Physical architecture</h2><img src="head-hmi-harness.svg" alt="Head HMI physical harness architecture"></section><section><h2>Installed equipment</h2><div class="grid">{equipment_cards}</div></section><section><h2>Link schedule</h2><div class="scroll"><table><thead><tr><th>ID</th><th>Service</th><th>From</th><th>To</th><th>Candidate assembly</th><th>mm</th></tr></thead><tbody>{link_table}</tbody></table></div></section><section><h2>Open before hardware</h2><ul>{hold_list}</ul></section><section class="panel"><h2>Controlled records</h2><p><a href="head-equipment-register.csv">Equipment</a> · <a href="head-interface-link-register.csv">Links</a> · <a href="head-route-retention-register.csv">Routes</a> · <a href="privacy-control-boundary.csv">Privacy/control</a> · <a href="inspection-test-plan.csv">Tests</a> · <a href="open-holds.csv">Holds</a></p></section></main><footer>{html.escape(WARNING)}</footer></body></html>'''


def integrate(eq_count: int, link_count: int, camera_count: int) -> None:
    status_path = WHOLE / "package-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "head_hmi_harness_package_present": True,
        "head_hmi_equipment_count": eq_count,
        "head_hmi_physical_link_count": link_count,
        "head_hmi_camera_link_count": camera_count,
        "head_hmi_camera_interface_corrected": True,
        "head_hmi_physical_validation_complete": False,
        "head_hmi_privacy_controls_validated": False,
        "head_hmi_procurement_released": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "energization_authority": False,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    readme = WHOLE / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- HR30-HEAD-HMI-HARNESS-P01-README-START -->", "<!-- HR30-HEAD-HMI-HARNESS-P01-README-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    block = f'''{start}\n## Physical head HMI harness\n\nThe [interactive head HMI harness guide](harness/head-hmi-harness-p0.1/index.html) replaces generic connector notes with **{eq_count} located equipment records** and **{link_count} routed physical links**. Both cameras now correctly use Pi 5 22-way to Camera Module 3 15-pin Standard-Mini cable candidates; the former 200 mm assumption is replaced by a 300 mm route candidate. The face display is remote rather than GPIO-stacked, and a current ReSpeaker Flex linear array/core plus two speaker candidates and a specific 5 V fan define the audio/cooling path. Exact cables, privacy controls, protection, physical fit and tests remain open.\n{end}\n'''
    marker = "<!-- HR30-PROTECTIVE-BONDING-P01-README-START -->"
    text = text.replace(marker, block + marker) if marker in text else text.rstrip() + "\n\n" + block
    readme.write_text(text, encoding="utf-8", newline="\n")

    root_page = WHOLE / "index.html"
    text = root_page.read_text(encoding="utf-8")
    start, end = "<!-- HR30-HEAD-HMI-HARNESS-P01-START -->", "<!-- HR30-HEAD-HMI-HARNESS-P01-END -->"
    if start in text and end in text:
        text = text.split(start, 1)[0] + text.split(end, 1)[1]
    section = f'''{start}<section id="head-hmi-harness"><h2>The complete head now has physical links</h2><div class="grid"><article class="card"><div class="metric">{eq_count}</div><p>located head HMI items</p></article><article class="card"><div class="metric">{link_count}</div><p>routed physical links</p></article><article class="card"><div class="metric">{camera_count}</div><p>correct 22-to-15 camera links</p></article><article class="card hold"><div class="metric">0</div><p>built or powered links</p></article></div><p><a href="harness/head-hmi-harness-p0.1/index.html">Open the interactive head HMI harness guide</a>. The selected architecture is a candidate, not a procurement or energization release.</p></section>{end}'''
    marker = "<!-- HR30-PROTECTIVE-BONDING-P01-START -->"
    text = text.replace(marker, section + marker) if marker in text else text.replace("</main>", section + "</main>")
    root_page.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    source_rows, binding_rows, eq_rows = sources(), bindings(), equipment()
    link_rows = links()
    route_rows, control_rows, test_rows, hold_rows = routes(link_rows), controls(), tests(), holds()
    write_csv(OUT / "primary-source-register.csv", source_rows)
    write_csv(OUT / "source-binding.csv", binding_rows)
    write_csv(OUT / "head-equipment-register.csv", eq_rows)
    write_csv(OUT / "head-interface-link-register.csv", link_rows)
    write_csv(OUT / "head-route-retention-register.csv", route_rows)
    write_csv(OUT / "privacy-control-boundary.csv", control_rows)
    write_csv(OUT / "inspection-test-plan.csv", test_rows)
    write_csv(OUT / "open-holds.csv", hold_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING,
        "primary_source_count": len(source_rows), "source_binding_count": len(binding_rows),
        "head_equipment_count": len(eq_rows), "physical_link_count": len(link_rows),
        "camera_link_count": sum("vision" in str(r["service"]) for r in link_rows),
        "route_count": len(route_rows), "privacy_control_count": len(control_rows),
        "inspection_test_count": len(test_rows), "open_hold_count": len(hold_rows),
        "camera_interface_corrected": True, "former_200_mm_camera_assumption_rejected": True,
        "received_hardware_count": 0, "built_link_count": 0, "executed_test_count": 0,
        "physical_fit_verified": False, "privacy_controls_validated": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "head-hmi-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "head-hmi-harness.svg").write_text(drawing(), encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(eq_rows, link_rows, hold_rows), encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"# HR-30 head HMI harness P0.1\n\n**{WARNING}**\n\nThis package defines the physical camera, face-display, audio, privacy and cooling links for the complete head. It corrects the camera connector/length error and records no physical test or authority. Open [index.html](index.html) for the guide.\n", encoding="utf-8", newline="\n")
    shutil.copy2(Path(__file__), OUT / "head-hmi-source.py")
    manifest = [{"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p), "warning": WARNING} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(OUT, RELEASE)
    integrate(len(eq_rows), len(link_rows), status["camera_link_count"])
    import generate_hr30_system_package_p01 as system_package
    system_package.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
