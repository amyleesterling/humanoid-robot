#!/usr/bin/env python3
"""Generate the held HR-V0 24 V source-interface candidate package."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-24v-interface-p0.2"
IDENTIFIER = "HR-V0-24V-IF-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

BOM = [
    ("24IF-001", "PSU2", "GlobTek", "WR9QI1660YL4NKITR6B", "EXACT SOURCE/OUTPUT-CORD CANDIDATE - APPLICATION HOLD", "24 V / 1.66 A / 40 W Class II wall adapter; Rev B includes YL4/C40337 locking output cord and Q blade kit; received identity, blade retention and site application remain open"),
    ("24IF-002", "J24", "Kycon", "KPJX-PM-4S", "EXACT PANEL-JACK CANDIDATE - SOURCE-CORD FIT/PHYSICAL HOLD", "Kycon recommends KPPX plugs; GlobTek identifies YL4 as KPPX-4P but permits an equal connector, so received plug identity, fit, view and continuity remain open"),
    ("24IF-003", "F24", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "Source current-limit/fault behavior, load inrush, time-current coordination, conductors, connector limits, ambient, bundling, length and jurisdiction required"),
    ("24IF-004", "J24 PCB/HARNESS", "SELECTION REQUIRED", "SELECTION REQUIRED", "DESIGN REQUIRED", "No board, harness, wire, solder, terminal, support or fabrication package released"),
    ("24IF-005", "J24 RETENTION/ENTRY", "SELECTION REQUIRED", "SELECTION REQUIRED", "DESIGN REQUIRED", "No panel hole, fastener, strain relief, ingress, bend-radius or pullout solution released"),
]

PINS = [
    ("24PIN-001", "PSU2", "YL4-1", "+24 V", "SAFETY_24V_RAW", "GlobTek WR9QI1660YL4NKITR6B Rev B", "VERIFY RECEIVED PLUG VIEW AND POLARITY"),
    ("24PIN-002", "PSU2", "YL4-2", "N/C", "NO NET / NO CONNECTION", "GlobTek WR9QI1660YL4NKITR6B Rev B", "DO NOT REPURPOSE"),
    ("24PIN-003", "PSU2", "YL4-3", "0 V / SHIELD RETURN", "SAFETY_0V", "GlobTek WR9QI1660YL4NKITR6B Rev B", "VERIFY RECEIVED PLUG VIEW AND CONTINUITY"),
    ("24PIN-004", "PSU2", "YL4-4", "N/C", "NO NET / NO CONNECTION", "GlobTek WR9QI1660YL4NKITR6B Rev B", "DO NOT REPURPOSE"),
    ("24PIN-005", "J24", "1", "+24 V", "SAFETY_24V_RAW", "GlobTek Rev B plus Kycon Rev C2", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-006", "J24", "2", "N/C", "NO NET / NO CONNECTION", "GlobTek Rev B plus Kycon Rev C2", "DO NOT REPURPOSE"),
    ("24PIN-007", "J24", "3", "0 V / SHIELD RETURN", "SAFETY_0V", "GlobTek Rev B plus Kycon Rev C2", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-008", "J24", "4", "N/C", "NO NET / NO CONNECTION", "GlobTek Rev B plus Kycon Rev C2", "DO NOT REPURPOSE"),
    ("24PIN-009", "F24", "IN", "SOURCE +24 V", "SAFETY_24V_RAW", "Project topology only", "PROTECTION SELECTION REQUIRED"),
    ("24PIN-010", "F24", "OUT", "PROTECTED +24 V", "SAFETY_24V", "Project topology only", "PROTECTION SELECTION REQUIRED"),
]

HOLDS = [
    ("24H-001", "SOURCE-CORD MATING", "Received PSU2 output plug identity and proof that the supplied YL4/KPPX-4P-or-equal plug mates correctly with exact KPJX-PM-4S"),
    ("24H-002", "LOAD/STARTUP", "Accepted continuous-load budget plus simultaneous pickup, startup, brownout, source-foldback and recovery evidence for the actual control assembly"),
    ("24H-003", "RECEIVING", "Photographed source, Q-NA blade and jack identities; blade retention; keyed orientation; power-off continuity and controlled polarity record"),
    ("24H-004", "PROTECTION", "F24 part/value based on fault current, inrush, time-current and downstream protection coordination"),
    ("24H-005", "CONDUCTORS", "Wire, PCB/harness, terminals and terminations based on length, ambient, bundling, connector limits and jurisdiction"),
    ("24H-006", "MECHANICAL", "Received Kycon geometry, panel/PCB design, mounting, retention, strain relief, bend radius, ingress and pullout proof"),
    ("24H-007", "PHYSICAL TEST", "Polarity, voltage drop, contact temperature, retention and abnormal-condition evidence at accepted worst case"),
    ("24H-008", "QUALIFIED REVIEW", "Qualified electrical review and controlled work authorization for the applicable stage"),
]

SOURCES = [
    ("24SRC-001", "GlobTek WR9QI1660YL4NKITR6B specification", "Rev B", "generated/rechecked 2026-08-08", "https://spec.globtek.info/spec/?id=01t0c000008jfZg", "Exact 24 V / 1.66 A / 40 W source, Class II floating output, Q blade kit, current-limit and thermal envelope, YL4/C40337 cord construction and pinout"),
    ("24SRC-002", "GlobTek WR9QI1660YL4NKITR6B product page", "current product page", "rechecked 2026-08-08", "https://www.globtek.com/_0/WR9QI1660YL4NKITR6B/o", "Current exact order-code identity and output configuration"),
    ("24SRC-003", "GlobTek YL4/KPPX-4P connector record", "current web record", "updated 2026-07-17; rechecked 2026-08-08", "https://www.globtek.com/en/news/circular-locking-connectors-in-3-pinpole-and-4-pinpole-din-style-configurations-terminate-low-voltage-cord-providing-secure-connections-and-high-current-carrying-capability-in-stock-part-kpp322464fkpp3r-and-kpp422464fkpp4r", "Identifies the locking plug family and listed mating-jack families; received exact plug remains mandatory because the source drawing permits an equal"),
    ("24SRC-004", "Kycon KPJX-PM catalog", "catalog index 0126", "2026-01", "https://www.kycon.com/Catalog_PDF/KPJX-PM.pdf", "KPJX-PM-4S identity, KPPX mating recommendation and manufacturer maxima"),
    ("24SRC-005", "Kycon KPJX-PM-4S engineering drawing", "Rev C2", "2026-01-08", "https://www.kycon.com/Pub_Eng_Draw/KPJX-PM-4S.pdf", "Pin view and dimensions; manufacturer maximum 7.5 A/pin at 48 VDC is not a project rating"),
    ("24SRC-006", "Pilz PNOZ s4 operating manual", "21396-EN-23", "2026-06", "https://www.pilz.com/en-INT/eshop/product/750104", "2.5 W per-device control-source load screen; exact startup/application remains open"),
    ("24SRC-007", "Schneider TeSys Deca contactors catalog", "MKTED210011EN", "2026", "https://download.schneider-electric.com/files?p_Doc_Ref=MKTED210011EN", "5.4 W per LC1D25BD coil screening value; pickup and application evidence remain open"),
    ("24SRC-008", "Phoenix Contact PLC-RSC-24DC/21-21 product data", "item 2967060", "data-maintenance 2026-04-01", "https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060", "18 mA typical per relay; typical value is not a guaranteed maximum"),
    ("24SRC-009", "IDEC HW Series screw-terminal catalog", "current catalog", "2026-07-23", "https://us.idec.com/idec-us/en/USD/medias/HWSeries-us.pdf", "0.36 W family LED-lamp screen only; exact H1 complete-assembly consumption remains open"),
    ("24SRC-010", "TRACO POWER TSR 1 Series datasheet", "Rev February 7 2024", "2024-02-07", "https://www.tracopower.com/tsr1-datasheet", "TSR 1-2450 5 V / 1 A output and typical efficiency record; project uses a separate conservative input-power design reserve pending measurement"),
]

LOADS = [
    ("24LOAD-001", "K1/K2", "Schneider published DC coil consumption", "2", "5.4", "10.800", "0.450000", "PUBLISHED OPERATING SCREEN", "Pickup transient, tolerance, duty and received coil behavior remain open"),
    ("24LOAD-002", "SR1/SRA1", "Pilz published power consumption", "2", "2.5", "5.000", "0.208333", "PUBLISHED OPERATING SCREEN", "Startup/input tolerance and installed configuration remain open"),
    ("24LOAD-003", "KWD1/KWD2", "Phoenix Contact typical input current converted at 24 V", "2", "0.432", "0.864", "0.036000", "TYPICAL SCREEN ONLY", "Maximum current, simultaneous pickup and received behavior remain open"),
    ("24LOAD-004", "H1", "IDEC HW family 24 V LED-lamp catalog screen", "1", "0.36", "0.360", "0.015000", "FAMILY SCREEN ONLY", "Exact complete-assembly mapping, current, polarity and received behavior remain open"),
    ("24LOAD-005", "WDPCB1/DC1", "Project continuous design reserve; not a component rating", "1", "10.0", "10.000", "0.416667", "CONSERVATIVE PROJECT RESERVE", "Measure actual startup, steady-state, brownout, fault and thermal behavior; independently accept the reserve"),
]


def write_csv(name: str, header: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow((*header, "warning"))
        writer.writerows((*row, WARNING) for row in rows)


def guide() -> str:
    pin_rows = "".join(f"<tr><td>{html.escape(r[1])}:{html.escape(r[2])}</td><td>{html.escape(r[3])}</td><td>{html.escape(r[4])}</td><td>{html.escape(r[6])}</td></tr>" for r in PINS)
    hold_rows = "".join(f"<tr><td>{html.escape(r[0])}</td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td></tr>" for r in HOLDS)
    load_rows = "".join(f"<tr><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td><td>{html.escape(r[5])} W</td><td>{html.escape(r[6])} A</td><td>{html.escape(r[7])}</td><td>{html.escape(r[8])}</td></tr>" for r in LOADS)
    load_w = sum(float(row[5]) for row in LOADS)
    load_a = sum(float(row[6]) for row in LOADS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#751b1b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:clamp(1.5rem,4vw,3rem)}}main{{max-width:1120px;margin:auto;padding:1.25rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.2rem)}}.warning{{background:var(--gold);color:#231800;font-weight:800;padding:.8rem;border:3px solid #231800}}.flow{{display:grid;grid-template-columns:repeat(7,max-content);align-items:center;gap:.6rem;overflow-x:auto;padding:1rem;background:white;border:2px solid var(--blue)}}.box{{padding:.8rem;border:2px solid var(--blue);border-radius:10px;min-width:160px}}.hold{{border-color:var(--danger);background:#fff4f4}}.arrow{{font-size:1.5rem}}.table{{overflow-x:auto;border:2px solid var(--blue);background:white}}table{{border-collapse:collapse;min-width:920px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #abc7df}}th{{background:var(--sky)}}small{{font-size:14px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}.metric{{background:white;border:2px solid var(--blue);padding:1rem;border-radius:10px}}.metric strong{{display:block;font-size:1.5rem}}footer{{margin-top:2rem;background:var(--ink);color:white;padding:1rem}}@media(max-width:600px){{main{{padding:.8rem}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - 2026-08-08</p><h1>24 V source interface</h1><p>A factory-terminated locking source candidate and an explicit preliminary load screen. Physical evidence and protection remain held open.</p></header><main><h2>Proposed boundary</h2><div class="flow"><div class="box">WR9QI1660YL4NKITR6B<br><small>24 V / 1.66 A Class II source</small></div><span class="arrow">-&gt;</span><div class="box">YL4/C40337<br><small>factory KPPX-4P-or-equal cord</small></div><span class="arrow">-&gt;</span><div class="box hold">KPJX-PM-4S<br><small>received fit/physical hold</small></div><span class="arrow">-&gt;</span><div class="box hold">F24<br><small>selection required</small></div></div><p>The source drawing assigns pin 1 to +24 V and pin 3 to return/shield; pins 2 and 4 are N/C and may not be repurposed. The Kycon manufacturer maximum is not adopted as a Project Button rating.</p><h2>Preliminary continuous-load screen</h2><div class="metrics"><div class="metric"><strong>{load_w:.3f} W / {load_a:.3f} A</strong>screened continuous allocation</div><div class="metric"><strong>{40.0 - load_w:.3f} W</strong>nameplate headroom through 40 C</div><div class="metric"><strong>{32.0 - load_w:.3f} W</strong>headroom at GlobTek's 50 C / 80% limit</div></div><p>This is not a released source-sizing result. The 10 W watchdog allocation is a conservative project reserve, not a manufacturer rating. Simultaneous pickup, tolerance, temperature, wiring loss, startup, brownout, foldback and fault behavior still require physical evidence.</p><div class="table"><table><thead><tr><th>Load</th><th>Basis</th><th>Power</th><th>Current at 24 V</th><th>Evidence class</th><th>Open evidence</th></tr></thead><tbody>{load_rows}</tbody></table></div><h2>Pin allocation candidate</h2><div class="table"><table><thead><tr><th>Point</th><th>Function</th><th>Net</th><th>Release condition</th></tr></thead><tbody>{pin_rows}</tbody></table></div><h2>Blocking evidence</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div><footer>No ordering, panel cutting, PCB/harness fabrication, wiring, connection or energization is authorized by this package.</footer></main></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv("interface-bom.csv", ("item_id", "reference", "manufacturer", "part_number", "state", "evidence_open"), BOM)
    write_csv("pin-allocation.csv", ("record_id", "reference", "pin", "function", "net", "basis", "verification"), PINS)
    write_csv("compatibility-holds.csv", ("hold_id", "scope", "evidence_required"), HOLDS)
    write_csv("source-register.csv", ("source_id", "document", "revision", "date", "official_url", "use_and_limit"), SOURCES)
    write_csv("load-budget.csv", ("load_id", "references", "basis", "quantity", "per_unit_w", "subtotal_w", "current_a_at_24v", "evidence_class", "open_evidence"), LOADS)
    load_w = sum(float(row[5]) for row in LOADS)
    load_a = sum(float(row[6]) for row in LOADS)
    (OUT / "interface-summary.json").write_text(json.dumps({"identifier": IDENTIFIER, "date": "2026-08-08", "electrical_baseline": "Project Button Electrical V3-P1.12", "bom_rows": len(BOM), "pin_rows": len(PINS), "hold_rows": len(HOLDS), "source_rows": len(SOURCES), "load_rows": len(LOADS), "source_rating_w": 40.0, "source_rating_a": 1.66, "screened_continuous_w": round(load_w, 3), "screened_continuous_a": round(load_a, 6), "headroom_through_40c_w": round(40.0 - load_w, 3), "headroom_at_50c_80pct_w": round(32.0 - load_w, 3), "load_screen_release": "NOT RELEASED - PHYSICAL STARTUP/BROWNOUT/FAULT EVIDENCE REQUIRED", "release": "NOT AUTHORIZED", "warning": WARNING}, indent=2) + "\n", encoding="utf-8")
    (OUT / "HR-V0_24v-interface-guide.html").write_text(guide(), encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {len(BOM)} BOM rows; {len(PINS)} pin rows; {len(HOLDS)} holds; {len(SOURCES)} sources; {len(LOADS)} load rows")
    print(WARNING)


if __name__ == "__main__":
    main()
