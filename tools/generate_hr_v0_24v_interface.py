#!/usr/bin/env python3
"""Generate the held HR-V0 24 V source-interface candidate package."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "interfaces" / "hr-v0-24v-interface-p0.1"
IDENTIFIER = "HR-V0-24V-IF-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

BOM = [
    ("24IF-001", "PSU2", "Mean Well", "GST40A24-P1J", "SOURCE CANDIDATE", "24 V / 1.67 A; factory mains boundary; received identity and site application open"),
    ("24IF-002", "J24-A", "Mean Well", "DC PLUG-P1J-R7B", "EXACT ACCESSORY CANDIDATE - COMPATIBILITY HOLD", "Do not order until Mean Well confirms compatibility with GST40A24-P1J and publishes or confirms the adapter current/application envelope"),
    ("24IF-003", "J24-B", "Kycon", "KPJX-PM-4S", "EXACT PANEL-JACK CANDIDATE - PHYSICAL HOLD", "Catalog and drawing identity frozen; PCB/harness, mounting, cutout, touch protection and received pin-view proof open"),
    ("24IF-004", "F24", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "Source fault current, inrush, time-current coordination, conductors, connector limits, ambient, bundling, length and jurisdiction required"),
    ("24IF-005", "J24 PCB/HARNESS", "SELECTION REQUIRED", "SELECTION REQUIRED", "DESIGN REQUIRED", "No board, harness, wire, solder, terminal, support or fabrication package released"),
    ("24IF-006", "J24 RETENTION/ENTRY", "SELECTION REQUIRED", "SELECTION REQUIRED", "DESIGN REQUIRED", "No panel hole, fastener, strain relief, ingress, bend-radius or pullout solution released"),
]

PINS = [
    ("24PIN-001", "PSU2", "P1J-C", "CENTER +24 V", "SAFETY_24V_RAW", "Mean Well GST40A specification", "VERIFY RECEIVED POLARITY"),
    ("24PIN-002", "PSU2", "P1J-S", "SLEEVE 0 V", "SAFETY_0V", "Mean Well GST40A specification", "VERIFY RECEIVED POLARITY"),
    ("24PIN-003", "J24", "1", "+24 V A", "SAFETY_24V_RAW", "Mean Well R7B pin assignment", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-004", "J24", "2", "0 V A", "SAFETY_0V", "Mean Well R7B pin assignment", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-005", "J24", "3", "0 V B", "SAFETY_0V", "Mean Well R7B pin assignment", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-006", "J24", "4", "+24 V B", "SAFETY_24V_RAW", "Mean Well R7B pin assignment", "RECONCILE PLUG/JACK VIEW ON RECEIPT"),
    ("24PIN-007", "F24", "IN", "SOURCE +24 V", "SAFETY_24V_RAW", "Project topology only", "PROTECTION SELECTION REQUIRED"),
    ("24PIN-008", "F24", "OUT", "PROTECTED +24 V", "SAFETY_24V", "Project topology only", "PROTECTION SELECTION REQUIRED"),
]

HOLDS = [
    ("24H-001", "COMPATIBILITY", "Mean Well written confirmation that DC PLUG-P1J-R7B is compatible with GST40A24-P1J"),
    ("24H-002", "ADAPTER RATING", "Mean Well current/application envelope for DC PLUG-P1J-R7B, including whether all four R7B contacts are intended to be paralleled"),
    ("24H-003", "RECEIVING", "Photographed part identities, pin markings, keyed orientation and live-dead-live polarity/continuity record"),
    ("24H-004", "PROTECTION", "F24 part/value based on fault current, inrush, time-current and downstream protection coordination"),
    ("24H-005", "CONDUCTORS", "Wire, PCB/harness, terminals and terminations based on length, ambient, bundling, connector limits and jurisdiction"),
    ("24H-006", "MECHANICAL", "Received Kycon geometry, panel/PCB design, mounting, retention, strain relief, bend radius, ingress and pullout proof"),
    ("24H-007", "PHYSICAL TEST", "Polarity, voltage drop, contact temperature, retention and abnormal-condition evidence at accepted worst case"),
    ("24H-008", "QUALIFIED REVIEW", "Qualified electrical review and controlled work authorization for the applicable stage"),
]

SOURCES = [
    ("24SRC-001", "Mean Well GST40A specification", "GST40A-SPEC", "2026-04-03", "https://www.meanwell.com/Upload/PDF/GST40A/GST40A-SPEC.PDF", "P1J geometry/polarity and 24 V / 1.67 A source record"),
    ("24SRC-002", "Mean Well accessory product page", "current product-series page", "rechecked 2026-08-08", "https://www.meanwell.com/productSeriesP.aspx?c=75&i=90", "DC PLUG-P1J-R7B accessory identity; GST40A compatibility/current not closed"),
    ("24SRC-003", "Mean Well industrial catalog", "current online catalog page 62", "rechecked 2026-08-08", "https://www.meanwell.com/catalog/product/files/basic-html/page62.html", "R7B pin assignment: 1/4 +Vo and 2/3 -Vo"),
    ("24SRC-004", "Kycon KPJX-PM catalog", "catalog index 0126", "2026-01", "https://www.kycon.com/Catalog_PDF/KPJX-PM.pdf", "KPJX-PM-4S identity, snap-and-lock family and manufacturer maxima"),
    ("24SRC-005", "Kycon KPJX-PM-4S engineering drawing", "Rev C2", "2026-01-08", "https://www.kycon.com/Pub_Eng_Draw/KPJX-PM-4S.pdf", "Pin view and dimensions; manufacturer maximum 7.5 A/pin at 48 VDC is not a project rating"),
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
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff;--danger:#751b1b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:clamp(1.5rem,4vw,3rem)}}main{{max-width:1120px;margin:auto;padding:1.25rem}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05}}h2{{font-size:clamp(1.5rem,3vw,2.2rem)}}.warning{{background:var(--gold);color:#231800;font-weight:800;padding:.8rem;border:3px solid #231800}}.flow{{display:grid;grid-template-columns:repeat(7,max-content);align-items:center;gap:.6rem;overflow-x:auto;padding:1rem;background:white;border:2px solid var(--blue)}}.box{{padding:.8rem;border:2px solid var(--blue);border-radius:10px;min-width:145px}}.hold{{border-color:var(--danger);background:#fff4f4}}.arrow{{font-size:1.5rem}}.table{{overflow-x:auto;border:2px solid var(--blue);background:white}}table{{border-collapse:collapse;min-width:820px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #abc7df}}th{{background:var(--sky)}}small{{font-size:14px}}footer{{margin-top:2rem;background:var(--ink);color:white;padding:1rem}}@media(max-width:600px){{main{{padding:.8rem}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} · 2026-08-08</p><h1>24 V source interface</h1><p>Exact catalog and topology candidates, with compatibility and physical evidence deliberately held open.</p></header><main><h2>Proposed boundary</h2><div class="flow"><div class="box">GST40A24-P1J<br><small>factory source</small></div><span class="arrow">→</span><div class="box hold">DC PLUG-P1J-R7B<br><small>compatibility hold</small></div><span class="arrow">→</span><div class="box hold">KPJX-PM-4S<br><small>physical hold</small></div><span class="arrow">→</span><div class="box hold">F24<br><small>selection required</small></div></div><p>No parallel-contact current-sharing or safety credit is taken. The manufacturer maximum printed for the Kycon jack is not adopted as a project rating.</p><h2>Pin allocation candidate</h2><div class="table"><table><thead><tr><th>Point</th><th>Function</th><th>Net</th><th>Release condition</th></tr></thead><tbody>{pin_rows}</tbody></table></div><h2>Blocking evidence</h2><div class="table"><table><thead><tr><th>ID</th><th>Scope</th><th>Evidence required</th></tr></thead><tbody>{hold_rows}</tbody></table></div><footer>No ordering, panel cutting, PCB/harness fabrication, wiring, connection or energization is authorized by this package.</footer></main></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv("interface-bom.csv", ("item_id", "reference", "manufacturer", "part_number", "state", "evidence_open"), BOM)
    write_csv("pin-allocation.csv", ("record_id", "reference", "pin", "function", "net", "basis", "verification"), PINS)
    write_csv("compatibility-holds.csv", ("hold_id", "scope", "evidence_required"), HOLDS)
    write_csv("source-register.csv", ("source_id", "document", "revision", "date", "official_url", "use_and_limit"), SOURCES)
    (OUT / "interface-summary.json").write_text(json.dumps({"identifier": IDENTIFIER, "date": "2026-08-08", "electrical_baseline": "Project Button Electrical V3-P1.10", "bom_rows": len(BOM), "pin_rows": len(PINS), "hold_rows": len(HOLDS), "source_rows": len(SOURCES), "release": "NOT AUTHORIZED", "warning": WARNING}, indent=2) + "\n", encoding="utf-8")
    (OUT / "HR-V0_24v-interface-guide.html").write_text(guide(), encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {len(BOM)} BOM rows; {len(PINS)} pin rows; {len(HOLDS)} holds; {len(SOURCES)} sources")
    print(WARNING)


if __name__ == "__main__":
    main()
