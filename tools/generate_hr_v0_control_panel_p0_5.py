"""Generate the P0.5 control-panel reconciliation from P0.4 and V3-P1.13."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.4"
OUT = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.5"
V3_WIRES = ROOT / "electrical" / "kicad" / "project-button-v3" / "wire-number-table.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
PANEL_REFS = {"S0", "S1", "S2", "H1", "SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "XT1"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SOURCE, OUT)
    for path in OUT.iterdir():
        if path.suffix.lower() in {".csv", ".svg"}:
            text = path.read_text(encoding="utf-8-sig")
            text = text.replace("HR-V0-CP-P0.4", "HR-V0-CP-P0.5").replace("V3-P1.12", "V3-P1.13")
            path.write_text(text, encoding="utf-8", newline="\n")

    bom = read_csv(OUT / "panel-bom.csv")
    kwd = next(row for row in bom if row["item_id"] == "PAN-015")
    kwd["description"] = "Two PLC-RSC-24DC/21-21 ordinary diagnostic relays; 11-14 NO contacts form a series SR1 A1 supply gate; zero safety credit"
    kwd["candidate_state"] = "EXACT V3-P1.13 CANDIDATE"
    kwd["physical_release"] = "HOLD - SUPPLY-GATE APPLICATION/FMEA TEST REQUIRED"
    kwd["evidence_revision_or_date"] = "official PDF data-maintenance 2026-04-01; rechecked 2026-08-08"
    kwd["closure_evidence_required"] = "received terminal identity/polarity; PNOZ 2.5 W steady and 0.5 A 5 ms inrush contact-duty review; supply-cycle endurance; stuck/weld/internal-short/open tests; routing segregation; replacement control; qualified review"
    write_csv(OUT / "panel-bom.csv", bom)

    old_wires = {row["wire_number"]: row for row in read_csv(SOURCE / "stationary-wire-schedule.csv")}
    new_source = [row for row in read_csv(V3_WIRES) if row["reference"] in PANEL_REFS]
    physical_rows: list[dict[str, str]] = []
    for row in new_source:
        old = old_wires[row["wire_number"]]
        route = old["routing_zone"]
        state = old["release_state"]
        if row["reference"] in {"KWD1", "KWD2"} and row["terminal"] in {"11", "14"}:
            route = "TOP RAIL / DIAGNOSTIC SUPPLY GATE - SEGREGATE FROM S0/SR1 INPUT RETURNS"
            state = "NOT RELEASED - SUPPLY-GATE ROUTING/FAULT TEST REQUIRED"
        if row["reference"] == "SR1" and row["terminal"] == "A1":
            route = "TOP RAIL / DIAGNOSTIC-GATED SR1 SUPPLY - SEGREGATE FROM INPUT RETURNS"
            state = "NOT RELEASED - SUPPLY-GATE ROUTING/POWER-CYCLE TEST REQUIRED"
        physical_rows.append({
            **row,
            "conductor_part_number": "SELECTION REQUIRED",
            "gauge": "SELECTION REQUIRED",
            "color": "SELECTION REQUIRED",
            "length_mm": "SELECTION REQUIRED",
            "termination_a": "SELECTION REQUIRED",
            "termination_b": "SELECTION REQUIRED",
            "routing_zone": route,
            "release_state": state,
            "warning": WARNING,
        })
    write_csv(OUT / "stationary-wire-schedule.csv", physical_rows)

    routes = [
        ("SGR-001", "SR1 supply gate stage 1 input", "SAFETY_24V", "KWD1:11", "top rail diagnostic supply-gate route", "separate from SR1_S11/S12/S21/S22"),
        ("SGR-002", "SR1 supply gate interstage", "WD_SUPPLY_INTERMEDIATE", "KWD1:14 -> KWD2:11", "short local top-rail jumper", "no door loom; no S0/input-return duct"),
        ("SGR-003", "SR1 gated supply output", "SR1_A1_WD_GATED", "KWD2:14 -> SR1:A1", "top rail diagnostic-gated supply route", "separate from SR1 input terminals/conductors"),
        ("SGR-004", "E-stop channel 1 direct return", "SR1_S11 / SR1_S12", "SR1:S11 -> S0:R-1/R-2 -> SR1:S12", "door loom safety channel 1", "no KWD or gated-supply terminal"),
        ("SGR-005", "E-stop channel 2 direct return", "SR1_S21 / SR1_S22", "SR1:S21 -> S0:L-1/L-2 -> SR1:S22", "door loom safety channel 2", "no KWD or gated-supply terminal"),
        ("SGR-006", "SR1 RESET", "SR1_S12 / SR1_START_RETURN", "SR1:S12 -> S1 -> SR1:S34", "door loom/reset safety route", "separate from KWD gate and feedback"),
        ("SGR-007", "SRA1 ARM/EDM", "SRA1_S12 / SRA1_START_RETURN", "SRA1:S12 -> S2 -> K1:21/22 -> K2:21/22 -> SRA1:S34", "door loom and top-rail safety route", "separate from KWD gate and feedback"),
        ("SGR-008", "KWD1 coil", "SAFETY_24V / WD1_COIL_N", "KWD1:A1/A2 -> JWP1:1/3", "ordinary diagnostic coil route", "segregate from S0/SR1 input returns"),
        ("SGR-009", "KWD2 coil", "SAFETY_24V / WD2_COIL_N", "KWD2:A1/A2 -> JWP1:1/4", "ordinary diagnostic coil route", "segregate from S0/SR1 input returns"),
        ("SGR-010", "KWD feedback", "WD1_NC_24V / WD2_NC_24V", "KWD1:21/22 and KWD2:21/22 -> JWF1", "ordinary diagnostic feedback route", "segregate from S0/SR1 input returns"),
        ("SGR-011", "supply-load screen", "SR1 A1/A2", "PNOZ s4 750104: 2.5 W DC; 0.5 A inrush for 5 ms", "analysis input only", "contact duty/endurance/coordination and measurement open"),
        ("SGR-012", "restart validation", "SR1/SRA1/K1/K2", "heartbeat loss -> SR1 supply loss -> RESET -> ARM -> fresh trajectory", "E2 control-only test subset", "all physical timing and qualified acceptance open"),
    ]
    route_rows = [{"route_id": a, "function": b, "net_or_boundary": c, "exact_terminals": d, "proposed_zone": e, "required_separation_or_evidence": f, "release_state": "NOT RELEASED", "warning": WARNING} for a, b, c, d, e, f in routes]
    write_csv(OUT / "supply-gate-routing-register.csv", route_rows)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc"><title id="title">HR-V0 P0.5 watchdog-gated SR1 supply</title><desc id="desc">Direct E-stop input channels are separated from the ordinary two-stage watchdog supply gate.</desc><style>text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:18px}}.title{{font-size:34px;font-weight:800}}.head{{font-size:24px;font-weight:800}}.warn{{font-size:20px;font-weight:800;fill:#7a3500}}.safety{{fill:#e5f7ee;stroke:#17663b;stroke-width:4}}.diag{{fill:#fff3cc;stroke:#c48700;stroke-width:4}}.box{{fill:#f5fbff;stroke:#0b4f8a;stroke-width:3}}.line{{fill:none;stroke:#0b4f8a;stroke-width:5}}.dash{{fill:none;stroke:#c48700;stroke-width:5;stroke-dasharray:12 8}}</style><rect width="1600" height="900" fill="#e7f6ff"/><text x="55" y="60" class="title">HR-V0 control-panel P0.5 - watchdog-gated SR1 supply</text><text x="55" y="100" class="warn">{WARNING}</text><rect x="55" y="160" width="370" height="250" rx="18" class="safety"/><text x="85" y="210" class="head">DIRECT E-STOP input loops</text><text x="85" y="260">SR1:S11 - S0 R NC - SR1:S12</text><text x="85" y="305">SR1:S21 - S0 L NC - SR1:S22</text><text x="85" y="355">No KWD terminal in either loop</text><rect x="520" y="160" width="520" height="250" rx="18" class="diag"/><text x="550" y="210" class="head">Ordinary diagnostic supply gate</text><text x="550" y="260">SAFETY_24V - KWD1:11/14</text><text x="550" y="305">- KWD2:11/14 - SR1:A1</text><text x="550" y="355">DF-01: ZERO SAFETY CREDIT</text><path d="M1040 285 H1150" class="dash"/><rect x="1150" y="160" width="395" height="250" rx="18" class="box"/><text x="1180" y="210" class="head">Manual restart chain</text><text x="1180" y="260">SR1 power restored</text><text x="1180" y="305">physical RESET, then ARM</text><text x="1180" y="350">fresh trajectory still required</text><rect x="55" y="485" width="1490" height="305" rx="18" class="box"/><text x="85" y="535" class="head">Controlled open evidence - NOT RELEASED</text><text x="85" y="585">- PNOZ supply screen: 2.5 W steady; 0.5 A startup pulse for 5 ms. Contact duty/endurance remains unapproved.</text><text x="85" y="630">- KWD welded/bypassed contacts can defeat the diagnostic gate, but are no longer connected to S0 return nodes.</text><text x="85" y="675">- Gate, coil and feedback conductors require released separation from SR1 input/RESET/ARM wiring.</text><text x="85" y="720">- Brownout, recovery, internal-short, contamination and power-cycle tests remain NOT EXECUTED.</text><text x="85" y="765" class="warn">No holes, wires, fabrication, fault injection or energization are authorized.</text></svg>'''
    (OUT / "watchdog-supply-gate.svg").write_text(svg, encoding="utf-8", newline="\n")
    print(f"Generated {OUT.relative_to(ROOT)} with {len(physical_rows)} bounded wire endpoints and {len(route_rows)} supply-gate controls")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
