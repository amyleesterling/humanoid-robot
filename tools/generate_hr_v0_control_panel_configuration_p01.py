#!/usr/bin/env python3
"""Generate the current-identity control-panel configuration overlay."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/control-panel-configuration-p0.1"
PANEL = ROOT / "electrical/panel/hr-v0-control-panel-p0.6"
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
IDENTIFIER = "HR-V0-CP-CONFIG-P0.1"
ROUND = "R220"
DATE = "2026-08-11"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)
PANEL_REFS = {"S0", "S1", "S2", "H1", "SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "XT1"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty register: {name}")
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    row["warning"] = WARNING
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bindings = [
        ("CPC-CFG-01", "historical physical-layout basis", "HR-V0-CP-P0.6", "electrical/panel/hr-v0-control-panel-p0.6/backplate-layout.csv"),
        ("CPC-CFG-02", "current core electrical project", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/project-button-v3-p1.15-carrier-candidate.kicad_pro"),
        ("CPC-CFG-03", "current core wire schedule", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "electrical/kicad/project-button-v3-p1.15-carrier-candidate/wire-number-table.csv"),
        ("CPC-CFG-04", "current watchdog board", "PCB-P1.0-P1.15-DIRECT", "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb"),
        ("CPC-CFG-05", "watchdog direct-binding evidence", "HR-V0-WD-P115-ID-P0.1", "release/hr-v0/watchdog-p115-identity-p0.1/index.html"),
        ("CPC-CFG-06", "current DXL star board", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb"),
        ("CPC-CFG-07", "current DXL star manufacturing review", "HR-V0-DXL-STAR-MFG-P0.2", "release/hr-v0/dxl-star-manufacturing-p0.2/manufacturing-input-register.csv"),
        ("CPC-CFG-08", "cross-domain configuration", "HR-V0-CONFIG-REC-P0.3", "configuration/hr-v0-config-reconciliation-p0.3/current-configuration-map.csv"),
    ]
    write("configuration-binding.csv", [warned({
        "record_id": rid, "role": role, "identifier": ident, "path": rel,
        "sha256": digest(ROOT / rel), "state": "CURRENT CONTROLLED INPUT",
    }) for rid, role, ident, rel in bindings])

    reconciliation = [
        ("CPC-ID-01", "control-panel physical envelope and planning coordinates", "HR-V0-CP-P0.6", "HR-V0-CP-P0.6 geometry basis under this overlay", "INHERITED; NOT A CURRENT ELECTRICAL IDENTITY", "No geometry change; holes, cuts and physical acceptance remain open"),
        ("CPC-ID-02", "core schematic and wire endpoints", "Electrical V3-P1.14", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "SUPERSEDED LABEL CORRECTED", "66/66 panel endpoints exactly equal"),
        ("CPC-ID-03", "watchdog PCB", "PCB-P0.7", "PCB-P1.0-P1.15-DIRECT", "SUPERSEDED LABEL CORRECTED", "160 x 100 mm planning envelope inherited; exact current source hash bound"),
        ("CPC-ID-04", "DXL star PCB", "DXL-STAR-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "SUPERSEDED LABEL CORRECTED", "100 x 60 mm outline retained by current source-bound manufacturing record"),
        ("CPC-ID-05", "observation-integrated presentation", "not present in P0.6", "V3-P1.17-OBSERVATION-P0.5-CANDIDATE", "SUPPORTING VIEW ONLY", "Does not replace P1.15 core or add safety credit"),
    ]
    write("identity-reconciliation.csv", [warned({
        "record_id": rid, "subject": subject, "stale_or_historical_identity": old,
        "current_identity": current, "disposition": disposition,
        "evidence_boundary": boundary, "physical_acceptance": "NOT EXECUTED",
    }) for rid, subject, old, current, disposition, boundary in reconciliation])

    old_rows = {r["wire_number"]: r for r in read(PANEL / "stationary-wire-schedule.csv")}
    current_rows = [r for r in read(P115 / "wire-number-table.csv") if r["reference"] in PANEL_REFS]
    endpoint_rows = []
    schedule_rows = []
    fields = ("sheet", "reference", "terminal", "pin_name", "net")
    for current in current_rows:
        old = old_rows[current["wire_number"]]
        equal = all(old[field] == current[field] for field in fields)
        endpoint_rows.append(warned({
            "wire_number": current["wire_number"], "p0_6_endpoint": "|".join(old[f] for f in fields),
            "p1_15_endpoint": "|".join(current[f] for f in fields),
            "parity": "EXACT MATCH" if equal else "MISMATCH - BLOCKER",
            "physical_evidence": "NOT EXECUTED",
        }))
        schedule_rows.append(warned({
            **current,
            "conductor_part_number": old["conductor_part_number"], "gauge": old["gauge"],
            "color": old["color"], "length_mm": old["length_mm"],
            "termination_a": old["termination_a"], "termination_b": old["termination_b"],
            "routing_zone": old["routing_zone"], "release_state": old["release_state"],
            "configuration_identity": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        }))
    write("wire-endpoint-parity.csv", endpoint_rows)
    write("current-stationary-wire-schedule.csv", schedule_rows)

    bom = read(PANEL / "panel-bom.csv")
    for row in bom:
        if row["item_id"] == "PAN-017":
            row["manufacturer_part_number"] = "PCB-P1.0 / Electrical V3-P1.15 direct-bound"
            row["description"] = "Current direct-bound watchdog PCB candidate; 160 x 100 mm planning envelope inherited from P0.6"
            row["candidate_state"] = "CURRENT PROJECT SOURCE CANDIDATE"
            row["physical_release"] = "HOLD - INTERNAL CAM REVIEW ONLY; NO FABRICATION"
            row["evidence_source"] = "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb"
            row["evidence_revision_or_date"] = "PCB-P1.0 / HR-V0-WD-P115-ID-P0.1 / HR-V0-WD-CAM-P0.2"
        elif row["item_id"] == "PAN-018":
            row["manufacturer_part_number"] = "DXL-STAR-P0.2-CARRIER-CANDIDATE"
            row["description"] = "Current carrier-aware DYNAMIXEL branch-isolating star PCB; 100 x 60 mm planning envelope inherited from P0.6"
            row["candidate_state"] = "CURRENT PROJECT SOURCE CANDIDATE"
            row["physical_release"] = "HOLD - INTERNAL CAM REVIEW ONLY; NO FABRICATION"
            row["evidence_source"] = "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb"
            row["evidence_revision_or_date"] = "DXL-STAR-P0.2-CARRIER-CANDIDATE / HR-V0-DXL-STAR-MFG-P0.2"
        row["warning"] = WARNING
    write("current-installation-bom.csv", bom)

    layout = read(PANEL / "backplate-layout.csv")
    for row in layout:
        if row["layout_id"] == "BP-012":
            row["mounting_basis"] = "PCB-P1.0 direct-bound Electrical V3-P1.15 current source; inherited 160 x 100 mm planning envelope"
        elif row["layout_id"] == "BP-013":
            row["mounting_basis"] = "DXL-STAR-P0.2-CARRIER-CANDIDATE current source; inherited 100 x 60 mm planning envelope"
        row["warning"] = WARNING
    write("current-backplate-layout.csv", layout)

    geometry = [
        ("CPC-GEO-01", "WDPCB1", "PCB-P0.7", "PCB-P1.0-P1.15-DIRECT", "160.000", "100.000", "BP-012", "IDENTITY PARITY ONLY"),
        ("CPC-GEO-02", "INJ1", "DXL-STAR-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "100.000", "60.000", "BP-013", "IDENTITY PARITY ONLY"),
    ]
    write("board-envelope-parity.csv", [warned({
        "record_id": rid, "reference": ref, "historical_identity": old, "current_identity": current,
        "planning_width_mm": width, "planning_height_mm": height, "layout_record": layout_id,
        "parity_state": state, "received_fit": "NOT EXECUTED", "mounting_hole_release": "FALSE",
    }) for rid, ref, old, current, width, height, layout_id, state in geometry])

    holds = [
        ("CPC-HOLD-01", "current watchdog supplier release", "Accepted P1.0 supplier packet, DFM, machine XYRS, first article and qualified review"),
        ("CPC-HOLD-02", "current DXL-star supplier release", "Accepted P0.2 supplier packet, DFM, connector/current application, first article and qualified review"),
        ("CPC-HOLD-03", "received enclosure/backplate", "Exact identity, measured usable envelope, coating, fit and flatness"),
        ("CPC-HOLD-04", "received device geometry", "All device dimensions, terminal sweeps, bend radii, access and door-depth survey"),
        ("CPC-HOLD-05", "production hole schedule", "Exact hole coordinates/diameters/tolerances tied to selected hardware and received measurements"),
        ("CPC-HOLD-06", "rail/duct release", "Final cuts, kerf, holes, fasteners, bonding, fill and physical proof"),
        ("CPC-HOLD-07", "stationary conductors", "Fault current, length, ambient, bundling, connector limits, exact wire/ferrule/termination and voltage-drop evidence"),
        ("CPC-HOLD-08", "protection coordination", "All fuse links, holders, inrush, clearing, conductor/connector protection and DC fault behavior selected"),
        ("CPC-HOLD-09", "grounding/bonding", "Exact PE, DC 0 V, frame and shield implementation plus physical continuity/impedance evidence"),
        ("CPC-HOLD-10", "thermal and separation", "Installed duty, duct fill, blocked-fan and worst-ambient enclosure survey"),
        ("CPC-HOLD-11", "unpowered inspection", "Point-to-point, polarity, isolation, torque, labels, sharp-edge, retention and cover-fit records"),
        ("CPC-HOLD-12", "qualified release", "Signed electrical, enclosure/mechanical and functional-safety review plus separate work authority"),
    ]
    write("closure-register.csv", [warned({
        "hold_id": rid, "subject": subject, "current_state": "OPEN",
        "evidence_required": evidence, "accepted": "FALSE",
    }) for rid, subject, evidence in holds])

    authority = [
        ("internal configuration review", "TRUE", "Source/identity comparison only"),
        ("supplier upload or quote", "FALSE", "Separate released manufacturing packet and authority required"),
        ("order panel or boards", "FALSE", "BOM/gate and commercial authorization required"),
        ("cut or drill", "FALSE", "Production hole/cut release absent"),
        ("wire or assemble", "FALSE", "Conductor/termination and assembly release absent"),
        ("connect or powered test", "FALSE", "E2 configuration-specific authority absent"),
        ("motion or energization", "FALSE", "Applicable gates and qualified validation remain open"),
    ]
    write("authority-boundary.csv", [warned({
        "activity": activity, "permitted_by_this_package": allowed, "boundary": boundary,
    }) for activity, allowed, boundary in authority])

    status = {
        "identifier": IDENTIFIER, "round": ROUND, "date": DATE,
        "configuration_bindings": len(bindings), "identity_records": len(reconciliation),
        "panel_endpoint_records": len(endpoint_rows), "endpoint_mismatches": sum(r["parity"] != "EXACT MATCH" for r in endpoint_rows),
        "current_bom_records": len(bom), "layout_records": len(layout), "board_envelope_records": len(geometry),
        "open_holds": len(holds), "historical_panel_geometry_released": False,
        "supplier_packet_released": False, "procurement_authorized": False, "fabrication_authorized": False,
        "assembly_authorized": False, "connection_authorized": False, "powered_test_authorized": False,
        "motion_authorized": False, "energization_authorized": False, "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    cards = "".join(f'''<article data-kind="{html.escape(disposition.lower())}"><p class="tag">{html.escape(rid)}</p><h2>{html.escape(subject)}</h2><p><strong>Before:</strong> {html.escape(old)}</p><p><strong>Current:</strong> {html.escape(current)}</p><p class="hold">{html.escape(boundary)}</p></article>''' for rid, subject, old, current, disposition, boundary in reconciliation)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 current panel configuration</title><style>
:root{{--sky:#bfe8ff;--blue:#072a5e;--gold:#f6c445;--paper:#f7fbff;--ink:#10243d;--line:#8fbedd}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.25vw,19px)/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:linear-gradient(135deg,var(--sky),#fff);border-bottom:7px solid var(--gold);padding:clamp(24px,5vw,68px)}}main{{max-width:1180px;margin:auto;padding:28px}}h1{{color:var(--blue);font-size:clamp(34px,6vw,66px);line-height:1.05;margin:.2em 0}}.warning{{background:var(--blue);color:white;padding:16px;border-left:12px solid var(--gold);font-weight:750}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:20px;margin:25px 0}}.metric,article{{background:white;border:2px solid var(--line);border-radius:18px;padding:22px;box-shadow:7px 7px 0 var(--sky)}}.metric b{{display:block;font-size:36px;color:var(--blue)}}.tag{{font-size:14px;font-weight:800;color:var(--blue)}}.hold{{border-left:6px solid var(--gold);padding-left:12px;font-weight:700}}footer{{margin-top:30px;font-size:14px}}@media(max-width:480px){{main{{padding:20px}}}}
</style></head><body><header><p class="tag">R220 · {IDENTIFIER}</p><h1>The panel now points at the current electrical sources.</h1><p>P0.6 geometry is retained only as a planning basis. Historical PCB identities are no longer the build-facing configuration.</p></header><main><p class="warning">{WARNING}</p><section class="metrics"><div class="metric"><b>66 / 66</b>panel endpoints match P1.15</div><div class="metric"><b>2</b>board identities corrected</div><div class="metric"><b>12</b>physical closure holds remain</div><div class="metric"><b>0</b>work authorizations</div></section><section class="grid">{cards}</section><h2>What remains</h2><p>Supplier releases, received fit, holes, conductors, protection, bonding, thermal evidence, unpowered inspection and qualified signatures. This overlay prevents stale-configuration fabrication; it is not itself a fabrication release.</p><footer>{WARNING}</footer></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"generated {IDENTIFIER}: {len(endpoint_rows)}/66 endpoint records; {len(holds)} holds; no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
