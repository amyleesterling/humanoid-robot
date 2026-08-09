#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 E2 control-only hardware configuration slice."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.2"
IDENTIFIER = "HR-V0-E2-HW-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

CONFIG = [
    ("E2-CFG-001", "ENC1/BP1", "Hammond PJ242010RT / 18P2117", "INSTALL CANDIDATE", "HOLD", "Panel and backplate candidate only; no drilling until received geometry, layout and qualified review close."),
    ("E2-CFG-002", "PSU2/J24", "GlobTek WR9QI1660YL4NKITR6B with factory YL4/C40337 locking cord + Kycon KPJX-PM-4S", "EXACT SOURCE/INTERFACE CANDIDATES", "24 V CONTROL SOURCE ONLY", "Received source-cord plug identity/fit, Q-NA blade retention, polarity, load/startup, panel interface, PCB/harness, protection, retention and physical application remain open."),
    ("E2-CFG-003", "PSU3", "Raspberry Pi 27 W USB-C Power Supply, US family", "INSTALL CANDIDATE", "5.1 V COMPUTE SOURCE ONLY", "Exact US SKU/color and retention remain selection required."),
    ("E2-CFG-004", "S0", "IDEC XW1E-BV402M-R", "INSTALL CANDIDATE", "CONTROL ONLY", "Received identity, positive-opening contact mapping, continuity and mounting evidence required."),
    ("E2-CFG-005", "S1", "IDEC HW1B-M1F10-B", "INSTALL CANDIDATE", "CONTROL ONLY", "Received-lot RESET terminal mapping required; schematic placeholders TBD-R1/TBD-R2 remain."),
    ("E2-CFG-006", "S2", "IDEC HW1B-M1F10-G", "INSTALL CANDIDATE", "CONTROL ONLY", "Received-lot ARM terminal mapping required; schematic placeholders TBD-A1/TBD-A2 remain."),
    ("E2-CFG-007", "H1", "IDEC HW1P-1FQD-A-24V", "INSTALL CANDIDATE", "DIAGNOSTIC ONLY; ZERO SAFETY CREDIT", "Execute HR-V0-H1-RCV-P0.1; TBD-HA/TBD-HB remain until received verification."),
    ("E2-CFG-008", "SR1/SRA1", "Pilz PNOZ s4 750104", "INSTALL CANDIDATE", "CONTROL ONLY", "Qualified application review, configuration, terminal protection, receiving and fault validation required."),
    ("E2-CFG-009", "KWD1/KWD2", "Phoenix Contact 2967060", "INSTALL CANDIDATE", "ORDINARY DIAGNOSTIC RELAYS; ZERO SAFETY CREDIT", "Received polarity and FMEA/fault evidence required."),
    ("E2-CFG-010", "K1/K2", "Schneider LC1D25BD", "INSTALL COIL/MIRROR CANDIDATE", "LOAD POLES UNSOURCED AND UNWIRED", "Coils and auxiliary/mirror contacts only at E2; loaded DC interruption remains prohibited."),
    ("E2-CFG-011", "WDPCB1", "Project Button PCB-P0.7 / HR-V0-WD-PCBA-RFI-P0.1", "INSTALL CANDIDATE", "CONTROL ONLY", "No current CAM release; assembler/supplier acceptance, new CAM review, fabrication, bare-board, assembly, HIL, fault, EMC and thermal evidence required."),
    ("E2-CFG-012", "DC1", "TRACO POWER TSR 1-2450", "INSTALL ON WDPCB1 CANDIDATE", "CONTROL ONLY", "Received identity plus PCB, brownout, EMC and thermal verification required."),
    ("E2-CFG-013", "PI1", "Raspberry Pi 5 8GB", "INSTALL CANDIDATE", "COMPUTE ONLY; NO SAFETY AUTHORITY", "GPIO cable, retention, image/hash and fresh-command controls remain open."),
    ("E2-CFG-014", "XT1", "5x Phoenix 3209510; 1x 3209523; 1x 3030417; 2x 3022218; 1x 0828734", "EXACT CATALOG/POSITION CANDIDATE", "CONTROL TERMINALS ONLY", "Position map frozen; conductors, ferrules, protection, marking and physical inspection remain open."),
    ("E2-CFG-015", "FSR1/FSR2", "Phoenix 3211861 holders + 3030420 end cover", "INSTALL HOLDER CANDIDATE", "NO FUSE LINK SELECTED", "Fuse links, coordination, grouping, conductor and received compatibility remain selection required."),
    ("E2-CFG-016", "PSA1/JA1", "Mean Well GST280A12-C6P actuator source and adapter", "PHYSICALLY ABSENT", "NO AC OR DC CONNECTION", "Must be removed from E2 boundary, capped and labeled."),
    ("E2-CFG-017", "F0/SD1", "Actuator source protection and master disconnect", "PHYSICALLY ABSENT OR UNWIRED", "NO ACTUATOR CURRENT PATH", "F0 remains selection required; no source/load conductors may be landed."),
    ("E2-CFG-018", "F1/F2/F3/INJ1", "Actuator branch protection and DXL-STAR board", "PHYSICALLY ABSENT OR UNWIRED", "NO ACTUATOR CURRENT PATH", "All protection and branch harness evidence remains open."),
    ("E2-CFG-019", "U1/J1/J2/J3", "U2D2 and actuator interfaces", "PHYSICALLY ABSENT OR DISCONNECTED", "COVERED, LABELED, VERIFIED DEAD", "No actuator, U2D2 power path or branch cable is permitted at E2."),
    ("E2-CFG-020", "SP1", "Project-added DC 0 V / PE star", "DNP", "PROHIBITED", "Do not fit; no project-added star is released for the mixed external factory-adapter architecture with source-defined bonding."),
    ("E2-CFG-021", "TP15/TP16/TP2", "Watchdog SWDIO/SWCLK/return test access", "EXISTING PCB TEST POINTS - NO TOOL CONNECTED FOR E2", "TOOL/DEBUG CONNECTION ABSENT", "No installed debug connector exists. Programmer, unpowered fixture and procedure remain selection required; no output bypass or back-power is permitted."),
    ("E2-CFG-022", "JFRAME1", "Frame/shield bonding interface", "DNP FOR E2", "NO INFERRED 0 V/PE/SHIELD LINK", "Bonding/EMC application remains selection required."),
    ("E2-CFG-023", "F24", "24 V control-source branch protection", "SELECTION REQUIRED", "NO PROTECTION VALUE OR HARDWARE RELEASED", "Fault current, inrush, time-current coordination, conductor/connector limits, cable length, ambient, bundling and jurisdiction remain open."),
]

TERMINALS = [
    ("XT1-01", "SAFETY_24V", "3209510 gray", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
    ("XT1-02", "SAFETY_0V", "3209523 blue", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
    ("XT1-03", "SR1_STATUS", "3209510 gray", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
    ("XT1-04", "SRA1_STATUS", "3209510 gray", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
    ("XT1-05", "K1_STATUS", "3209510 gray", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
    ("XT1-06", "K2_STATUS", "3209510 gray", "EXACT POSITION CANDIDATE", "WIRING HOLD"),
]

SOURCES = [
    ("SRC-E2-24V", "PSU2/J24", "GlobTek WR9QI1660YL4NKITR6B YL4/C40337 + Kycon KPJX-PM-4S", "24 V / 1.66 A / 40 W Class II source; factory locking output cord; application not released", "GlobTek exact specification Rev B generated/rechecked 2026-08-08; Kycon KPJX-PM catalog 0126; KPJX-PM-4S Rev C2 2026-01-08", "https://www.globtek.com/_0/WR9QI1660YL4NKITR6B/o", "CONDITIONAL CANDIDATE; received plug identity/fit, blade retention, load/startup, F24, PCB/harness, retention and polarity open"),
    ("SRC-E2-5V", "PSU3", "Raspberry Pi 27 W USB-C Power Supply", "5.1 V / 5 A family record", "RP-008245-DS-1 October 2023; portal updated 2025-10-06", "https://www.raspberrypi.com/products/27w-power-supply/", "CONDITIONAL CANDIDATE; exact US SKU/color/retention open"),
    ("SRC-E2-ACT", "PSA1", "Mean Well GST280A12-C6P", "12 V actuator source", "GST280A-SPEC 2026-04-03", "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF", "PROHIBITED AT E2; physically absent, AC/DC disconnected"),
]

HOLDS = [
    ("E2-HOLD-001", "SITE", "Exact Boston site, receptacle, branch/GFCI basis, cords, LOTO and exclusion zone", "Accepted site record and qualified electrical disposition"),
    ("E2-HOLD-002", "RECEIVING", "Received identities and markings for every installed candidate", "Signed receiving records with photographs and traceability"),
    ("E2-HOLD-003", "OPERATOR MAPPING", "S1 RESET, S2 ARM and H1 terminals remain TBD", "Executed receiving/continuity procedures and independent comparison"),
    ("E2-HOLD-004", "24 V INTERFACE", "PSU2 factory locking cord and J24 catalog/topology candidate are frozen but not application or physically released", "Received GlobTek YL4/KPPX-4P-or-equal plug identity and fit to exact Kycon jack; Q-NA blade retention; polarity/continuity; load/startup/brownout; PCB/harness, cutout, retention and strain-relief proof"),
    ("E2-HOLD-005", "PROTECTION", "F24 and FSR1/FSR2 protection/link selections and coordination are open", "Fault current, inrush, time-current, conductor and device coordination"),
    ("E2-HOLD-006", "CONDUCTORS", "Wire, ferrule/lug, labels, glands and door loom not released", "Lengths, ambient, bundling, ampacity, voltage drop, connector limits, termination qualification and jurisdiction"),
    ("E2-HOLD-007", "ENCLOSURE", "Holes, rail/duct cuts, entries, touch protection and bonding not released", "Received measurements, drawings, fabrication inspection and qualified enclosure review"),
    ("E2-HOLD-008", "WATCHDOG PCB", "PCB-P0.7 has no CAM or manufacturing release; R88 PCB-P0.5 CAM and PCB-P0.6 are superseded", "Assembler/supplier acceptance, land/process review, new fabrication package, bare-board test, assembly, HIL/fault/EMC/thermal evidence"),
    ("E2-HOLD-009", "FIRMWARE", "Watchdog and supervisor release images not accepted", "Immutable hashes, review, HIL/fault results and configuration record"),
    ("E2-HOLD-010", "TEST EQUIPMENT", "No exact instruments, calibration or numerical limits accepted", "Instrument register, calibration evidence, CAT/isolation suitability and approved limits"),
    ("E2-HOLD-011", "AUTHORIZATION", "No four-role run authorization", "Test director, qualified electrical reviewer, functional-safety reviewer and independent witness signatures"),
    ("E2-HOLD-012", "ACTUATOR EXCLUSION", "Absence of the complete 12 V path not physically proven", "Signed configuration inspection and live-dead-live evidence before E2"),
]


def write_csv(name: str, header: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow((*row, WARNING))


def make_html() -> str:
    def cards(rows: list[tuple[str, ...]]) -> str:
        return "\n".join(
            f'<article class="card"><h3>{html.escape(row[1])}</h3><p class="state">{html.escape(row[3])}</p><p>{html.escape(row[2])}</p><p><strong>Boundary:</strong> {html.escape(row[4])}</p><p>{html.escape(row[5])}</p></article>'
            for row in rows
        )
    hold_rows = "\n".join(
        f'<tr><td>{html.escape(row[0])}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[2])}</td><td>{html.escape(row[3])}</td></tr>'
        for row in HOLDS
    )
    term_rows = "\n".join(
        f'<tr><td>{html.escape(row[0])}</td><td>{html.escape(row[1])}</td><td>{html.escape(row[2])}</td><td>{html.escape(row[4])}</td></tr>'
        for row in TERMINALS
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 E2 hardware slice P0.2</title>
<style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--hold:#7b1e1e}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:var(--ink);color:white;padding:clamp(1.4rem,4vw,3rem)}} main{{max-width:1180px;margin:auto;padding:1.25rem}}
h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:.25rem 0}} h2{{font-size:clamp(1.5rem,3vw,2.2rem);margin:2rem 0 1rem}} h3{{font-size:1.15rem;margin:0}}
.warning{{background:var(--gold);color:#231800;font-weight:800;padding:.75rem 1rem;border:3px solid #231800}} .lede{{font-size:1.2rem;max-width:75ch}}
.boundary{{background:var(--sky);border-left:8px solid var(--blue);padding:1rem 1.2rem;margin:1.25rem 0}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}
.card{{background:white;border:2px solid var(--blue);border-radius:12px;padding:1rem;box-shadow:4px 4px 0 #a9d9f5}} .state{{font-weight:800;color:var(--hold)}}
.table-wrap{{overflow-x:auto;background:white;border:2px solid var(--blue)}} table{{border-collapse:collapse;min-width:850px;width:100%}} th,td{{padding:.75rem;text-align:left;vertical-align:top;border-bottom:1px solid #aac7df}} th{{background:var(--sky)}}
code{{font-size:1rem}} footer{{margin-top:2rem;padding:1rem;background:var(--ink);color:white}} @media(max-width:600px){{main{{padding:.8rem}} .grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div class="warning">{WARNING}</div><p>{IDENTIFIER} · dated 2026-08-08</p><h1>E2 control-only hardware slice</h1><p class="lede">A configuration-exact candidate for reviewing the first control-only commissioning article. It is not a shopping list, wiring release, test authorization, or permission to connect power.</p></header>
<main><section class="boundary"><h2>Hard power boundary</h2><p>Only the accepted 24 V safety/control source and 5.1 V compute source may eventually be considered at E2. The 12 V actuator source, actuator branches, U2D2 power path and every actuator plug must be physically absent or disconnected, covered, labeled and proven dead. K1/K2 may be present only for coil and auxiliary/mirror-contact tests; their load poles remain unsourced and unwired.</p></section>
<h2>Installed, absent and DNP states</h2><div class="grid">{cards(CONFIG)}</div>
<h2>XT1 exact position candidate</h2><p>The catalog family and six position-to-net assignments are frozen. Every conductor and termination remains on hold.</p><div class="table-wrap"><table><thead><tr><th>Position</th><th>Net</th><th>Catalog body</th><th>Release</th></tr></thead><tbody>{term_rows}</tbody></table></div>
<h2>Blocking holds</h2><p>All twelve holds must be dispositioned through accepted evidence. Passing a repository checker does not close them.</p><div class="table-wrap"><table><thead><tr><th>ID</th><th>Scope</th><th>Open item</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div>
<footer><strong>Current verdict:</strong> configuration candidate only. No procurement, fabrication, wiring, connection, energization, motion, human exposure or child-adjacent use is authorized.</footer></main></body></html>"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv("e2-configuration-slice.csv", ("record_id", "reference", "candidate", "physical_state", "e2_boundary", "open_evidence", "warning"), CONFIG)
    write_csv("e2-terminal-register.csv", ("terminal", "net", "catalog_body", "mapping_state", "physical_release", "warning"), TERMINALS)
    write_csv("e2-source-register.csv", ("source_id", "reference", "candidate", "published_output", "document_revision_or_date", "official_source", "e2_state", "warning"), SOURCES)
    write_csv("e2-blocking-holds.csv", ("hold_id", "scope", "open_item", "evidence_needed", "warning"), HOLDS)
    summary = {
        "identifier": IDENTIFIER,
        "date": "2026-08-08",
        "warning": WARNING,
        "electrical_baseline": "Project Button Electrical V3-P1.12",
        "sequence_baseline": "HR-V0-E2-SEQ-P0.1",
        "configuration_rows": len(CONFIG),
        "terminal_rows": len(TERMINALS),
        "source_rows": len(SOURCES),
        "blocking_holds": len(HOLDS),
        "permitted_power_domains": ["24 V safety/control candidate", "5.1 V compute candidate"],
        "prohibited_power_domains": ["12 V actuator", "powered U2D2/actuator branches"],
        "authorization": "NOT AUTHORIZED",
    }
    (OUT / "e2-hardware-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "HR-V0_e2-hardware-guide.html").write_text(make_html(), encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {len(CONFIG)} configuration rows, {len(TERMINALS)} terminal rows, {len(HOLDS)} blocking holds")
    print(WARNING)


if __name__ == "__main__":
    main()
