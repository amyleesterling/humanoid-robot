#!/usr/bin/env python3
"""Generate the held HR-V0 compute-heartbeat and watchdog-debug package."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-compute-debug-interface-p0.1"
IDENTIFIER = "HR-V0-COMPUTE-IF-P0.1"
BASELINE = "Project Button Electrical V3-P1.12"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

PINS = [
    ("CIPIN-001", "PI1", "USB-C-VBUS", "+5 V input", "COMPUTE_5V", "Existing compute power boundary", "Exact PSU SKU and retention remain open"),
    ("CIPIN-002", "PI1", "USB-C-GND", "USB-C power return", "COMPUTE_0V", "Existing compute power boundary", "Verify on received power path"),
    ("CIPIN-003", "PI1", "HDR40-6", "GPIO header ground", "COMPUTE_0V", "Raspberry Pi current GPIO documentation", "Verify physical header orientation and continuity before harness construction"),
    ("CIPIN-004", "PI1", "HDR40-11", "BCM GPIO17 heartbeat output", "PI_HEARTBEAT", "Raspberry Pi current GPIO documentation", "Reserve GPIO17; verify startup, logic level, load, waveform and fault behavior"),
    ("CIPIN-005", "JWH1", "1", "isolated heartbeat input", "PI_HEARTBEAT", "PCB-P0.5 exact connector allocation", "Harness connector, contacts, wire and retention remain open"),
    ("CIPIN-006", "JWH1", "2", "compute-domain return", "COMPUTE_0V", "PCB-P0.5 exact connector allocation", "Harness connector, contacts, wire and retention remain open"),
    ("CIPIN-007", "TP15", "1", "watchdog SWDIO test access", "WD_SWDIO", "PCB-P0.5 exact Harwin test point", "Unpowered fixture and programmer selection required"),
    ("CIPIN-008", "TP16", "1", "watchdog SWCLK test access", "WD_SWCLK", "PCB-P0.5 exact Harwin test point", "Unpowered fixture and programmer selection required"),
    ("CIPIN-009", "TP2", "1", "watchdog debug return", "SAFETY_0V", "PCB-P0.5 exact Harwin test point", "Unpowered fixture and no-back-power proof required"),
]

HOLDS = [
    ("CIH-001", "HEARTBEAT HARNESS", "Exact Pi-header contact/housing or controlled individual-contact solution, JWH1 mate, conductor, length, strain relief, retention and assembly drawing"),
    ("CIH-002", "GPIO RUNTIME", "Pinned operating system, GPIO backend, permissions, startup sequence and proof that GPIO17 is not claimed by an overlay or alternate function"),
    ("CIH-003", "STARTUP/SHUTDOWN", "Oscilloscope evidence for boot, application start, normal stop, crash, reboot, brownout and power removal; no valid heartbeat before explicit supervisor control"),
    ("CIH-004", "ELECTRICAL LOAD", "Received voltage/current/load evidence through the exact cable and VO618A interface, including open/short/reversed/miswire fault cases"),
    ("CIH-005", "TIMING/HIL", "Accepted heartbeat period, duty, jitter, watchdog timeout, output-drop timing and fault-injection evidence against the compiled supervisor and watchdog builds"),
    ("CIH-006", "DEBUG FIXTURE", "Exact programmer, clip/pogo/hook fixture, lead assignment, isolation/no-back-power method, mechanical clearance and controlled work instruction"),
    ("CIH-007", "DEBUG DEFAULT-OFF", "Proof that connect, halt, reset, flash, disconnect, abandoned session and tool faults cannot assert either watchdog output or restore motion eligibility"),
    ("CIH-008", "EMC/RETENTION", "Installed routing separation, shielding decision, bend radius, connector retention, emission/immunity and disturbance evidence"),
    ("CIH-009", "RECEIVING", "Photographs and continuity records for Pi header orientation, JWH1, TP2/TP15/TP16 access and assembled harness"),
    ("CIH-010", "QUALIFIED REVIEW", "Qualified electrical, controls and functional-safety review; no safety credit is assigned by this package"),
]

SOURCES = [
    ("CISRC-001", "Raspberry Pi computer hardware documentation - GPIO and 40-pin header", "current web documentation; no document revision stated", "accessed 2026-08-08", "https://www.raspberrypi.com/documentation/computers/raspberry-pi.html", "Raspberry Pi 5 has the standard 40-pin header; GPIO outputs are 3.3 V; SPI1 mapping identifies physical pin 11 as GPIO17"),
    ("CISRC-002", "Raspberry Pi 5 product brief", "current PDF; no revision identifier stated", "accessed 2026-08-08", "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf", "Raspberry Pi 5 product identity, USB-C 5 V/5 A power and standard 40-pin header; does not select the project cable"),
    ("CISRC-003", "Raspberry Pi Touch Display documentation", "current web documentation; no document revision stated", "accessed 2026-08-08", "https://www.raspberrypi.com/documentation/accessories/display.html", "Manufacturer documentation explicitly identifies physical header pin 6 as GND"),
    ("CISRC-004", "Harwin S1751-46R product page", "current product page", "accessed 2026-08-08", "https://www.harwin.com/products/S1751-46R", "Exact installed SMT test point; Harwin states compatibility with standard probes, lead clips and hooks; fixture is not selected"),
    ("CISRC-005", "Harwin S1751-XXR technical drawing", "issue 10", "2023-02-15; accessed 2026-08-08", "https://www.harwin.com/products/S1751-46R", "Exact test-point geometry and recommended pad; does not define a debug cable or programmer"),
    ("CISRC-006", "Project Button watchdog PCB-P0.5 source and checker", "PCB-P0.5", "repository state 2026-08-08", "../../kicad/project-button-v3/project-button-v3.kicad_pcb", "Exact TP2/TP15/TP16 net allocation and Harwin footprint; no fabricated board or installed access evidence"),
]


def write_csv(name: str, header: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow((*header, "warning"))
        writer.writerows((*row, WARNING) for row in rows)


def guide() -> str:
    pin_rows = "".join(f"<tr><td>{html.escape(r[1])}:{html.escape(r[2])}</td><td>{html.escape(r[3])}</td><td>{html.escape(r[4])}</td><td>{html.escape(r[6])}</td></tr>" for r in PINS)
    hold_rows = "".join(f"<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td></tr>" for r in HOLDS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#751b1b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:clamp(1.5rem,4vw,3rem)}}main{{max-width:1120px;margin:auto;padding:1.25rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.2rem)}}.warning{{background:var(--gold);color:#231800;font-weight:800;padding:.8rem;border:3px solid #231800}}.flow{{display:grid;grid-template-columns:repeat(7,max-content);align-items:center;gap:.6rem;overflow-x:auto;padding:1rem;background:white;border:2px solid var(--blue)}}.box{{padding:.8rem;border:2px solid var(--blue);border-radius:10px;min-width:170px}}.hold{{border-color:var(--danger);background:#fff4f4}}.arrow{{font-size:1.5rem}}.table{{overflow-x:auto;border:2px solid var(--blue);background:white}}table{{border-collapse:collapse;min-width:920px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #abc7df}}th{{background:var(--sky)}}small{{font-size:14px}}footer{{margin-top:2rem;background:var(--ink);color:white;padding:1rem}}@media(max-width:600px){{main{{padding:.8rem}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - 2026-08-08</p><h1>Compute heartbeat and watchdog debug</h1><p>One documented heartbeat pin and three existing test points replace unresolved terminal labels and an invented installed connector.</p></header><main><h2>Heartbeat path</h2><div class="flow"><div class="box">Pi header pin 11<br><small>BCM GPIO17, ordinary 3.3 V output</small></div><span class="arrow">-&gt;</span><div class="box hold">two-conductor harness<br><small>selection and physical evidence required</small></div><span class="arrow">-&gt;</span><div class="box">JWH1 pins 1/2<br><small>heartbeat plus compute return</small></div><span class="arrow">-&gt;</span><div class="box">VO618A interface<br><small>no safety credit</small></div></div><p>Pi physical header pin 6 is the compute-domain return. The GPIO remains input/high-impedance until explicitly configured. Valid timing, cable, runtime, electrical loading and fault behavior are not released.</p><h2>Debug access</h2><div class="flow"><div class="box">TP15<br><small>WD_SWDIO</small></div><div class="box">TP16<br><small>WD_SWCLK</small></div><div class="box">TP2<br><small>SAFETY_0V</small></div><span class="arrow">-&gt;</span><div class="box hold">unpowered fixture<br><small>programmer and lead assignment required</small></div></div><p>No installed debug connector exists. Connecting, halting, flashing or abandoning a debug session may not enable outputs, back-power the board or bypass a protective function.</p><h2>Controlled pin records</h2><div class="table"><table><thead><tr><th>Point</th><th>Function</th><th>Net</th><th>Evidence still required</th></tr></thead><tbody>{pin_rows}</tbody></table></div><h2>Blocking evidence</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div><footer>No cable fabrication, programming connection, powered debug, motion, safety credit or energization is authorized by this package.</footer></main></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv("pin-allocation.csv", ("record_id", "reference", "pin", "function", "net", "basis", "verification"), PINS)
    write_csv("compatibility-holds.csv", ("hold_id", "scope", "evidence_required"), HOLDS)
    write_csv("source-register.csv", ("source_id", "document", "revision", "date", "official_url", "use_and_limit"), SOURCES)
    config = json.loads((ROOT / "firmware" / "supervisor" / "compute-interface-config.json").read_text(encoding="utf-8"))
    summary = {"identifier": IDENTIFIER, "date": "2026-08-08", "electrical_baseline": BASELINE, "pin_rows": len(PINS), "hold_rows": len(HOLDS), "source_rows": len(SOURCES), "installed_debug_connector": "NONE", "heartbeat_gpio_bcm": 17, "heartbeat_physical_header_pin": 11, "heartbeat_return_physical_header_pin": 6, "test_points": ["TP15", "TP16", "TP2"], "firmware_binding": config["identifier"], "safety_credit": "NONE", "release": "NOT AUTHORIZED", "warning": WARNING}
    (OUT / "interface-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "HR-V0_compute-debug-interface-guide.html").write_text(guide(), encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {len(PINS)} pin rows; {len(HOLDS)} holds; {len(SOURCES)} sources")
    print(WARNING)


if __name__ == "__main__":
    main()
