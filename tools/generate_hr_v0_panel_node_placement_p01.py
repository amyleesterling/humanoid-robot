#!/usr/bin/env python3
"""Generate the fail-closed R223 panel-node placement and route-anchor candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "release/hr-v0/control-panel-configuration-p0.1/current-backplate-layout.csv"
DOOR = ROOT / "electrical/panel/hr-v0-control-panel-p0.6/door-layout.csv"
P2P = ROOT / "release/hr-v0/panel-point-to-point-p0.1/point-to-point-wire-schedule.csv"
ENG = ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement"
OUT = ROOT / "release/hr-v0/panel-node-placement-p0.1"
IDENTIFIER = "HR-V0-PANEL-NODE-PLACEMENT-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    if not records:
        raise RuntimeError(f"empty CSV prohibited: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layout() -> list[dict[str, str]]:
    base = [row for row in rows(BASE) if row["reference"] != "OPEN-LOWER-ZONE"]
    extra = [
        ("BP-027", "din_rail", "DR5", 54, 545, 160, 7.5, "Phoenix Contact 1207648 NS 35/7.5; planning segment allocated from existing RAIL-B stock", "HOLD - CUT/DRILL/HOLES NOT RELEASED", "received stock; kerf; final node/accessory widths; cut/drill/deburr/coating; fasteners; bonding; load and retention proof"),
        ("BP-028", "wire_duct", "WD4", 54, 625, 323.8, 40, "Phoenix Contact 3240189 CD 40X40; planning segment allocated from existing DUCT-A stock", "HOLD - CUT LENGTH NOT RELEASED", "received stock; kerf; fill; separation; bend/service access; cover; fastening; thermal and inspection evidence"),
        ("BP-029", "distribution_block_envelope", "XD24", 64, 555, 28.6, 58.1, "Phoenix Contact PTFIX 6/18X2,5-NS35 RD item 3273114 catalog envelope", "EXACT CATALOG CANDIDATE - RECEIVED FIT REQUIRED", "received dimensions; rail engagement; access; markers; spare-position treatment; conductor bends; loading/protection/thermal review"),
        ("BP-030", "distribution_block_envelope", "XD0", 98.6, 555, 28.6, 58.1, "Phoenix Contact PTFIX 6/18X2,5-NS35 BU item 3273112 catalog envelope", "EXACT CATALOG CANDIDATE - RECEIVED FIT REQUIRED", "received dimensions; rail engagement; access; markers; spare-position treatment; return/grounding policy; conductor bends; loading/thermal review"),
        ("BP-031", "terminal_envelope", "XN1", 133.2, 555, 5.2, 60.4, "Phoenix Contact PT 2,5-TWIN item 3209549 catalog width/height", "EXACT CATALOG CANDIDATE - ACCESSORIES/FIT REQUIRED", "received dimensions; end cover/partition/marker; rail retention; access; conductor bends; continuity and pull evidence"),
        ("BP-032", "terminal_envelope", "XN2", 138.4, 555, 5.2, 60.4, "Phoenix Contact PT 2,5-TWIN item 3209549 catalog width/height", "EXACT CATALOG CANDIDATE - ACCESSORIES/FIT REQUIRED", "received dimensions; end cover/partition/marker; rail retention; access; conductor bends; continuity and pull evidence"),
        ("BP-033", "terminal_envelope", "XN3", 143.6, 555, 5.2, 60.4, "Phoenix Contact PT 2,5-TWIN item 3209549 catalog width/height", "EXACT CATALOG CANDIDATE - ACCESSORIES/FIT REQUIRED", "received dimensions; end cover/partition/marker; diagnostic segregation; rail retention; access; continuity and pull evidence"),
        ("BP-034", "reserved_unallocated_envelope", "OPEN-LOWER-UPPER-RIGHT", 224, 533.4, 153.8, 82, "Residual P0.6 lower-zone planning reserve after DR5/node allocation; not an installation release", "SELECTION REQUIRED - NO DRILLING", "final parts; conductor bends; separation; heat; service access; qualified layout review"),
    ]
    for layout_id, object_type, reference, x, y, w, h, basis, state, evidence in extra:
        base.append({
            "layout_id": layout_id, "object_type": object_type, "reference": reference,
            "x_mm": str(x), "y_mm": str(y), "width_mm": str(w), "height_mm": str(h),
            "mounting_basis": basis, "release_state": state, "required_evidence": evidence,
            "warning": WARNING,
        })
    for row in base:
        row["warning"] = WARNING
    return base


def placement_register(layout_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    indexed = {row["reference"]: row for row in layout_rows}
    result: list[dict[str, str]] = []
    for ref in ("SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "XT1", "XD24", "XD0", "XN1", "XN2", "XN3"):
        row = indexed[ref]
        result.append({
            "reference": ref, "coordinate_frame": "BACKPLATE-CATALOG-CANDIDATE",
            "anchor_x_mm": f'{float(row["x_mm"]) + float(row["width_mm"]) / 2:.3f}',
            "anchor_y_mm": f'{float(row["y_mm"]) + float(row["height_mm"]) / 2:.3f}',
            "anchor_basis": "catalog/planning envelope center; not a terminal entry point",
            "terminal_position_state": "SELECTION REQUIRED", "cut_length_use": "PROHIBITED",
            "warning": WARNING,
        })
    for ref, x in (("FSR1", 181.0), ("FSR2", 193.0)):
        result.append({"reference": ref, "coordinate_frame": "BACKPLATE-CATALOG-CANDIDATE", "anchor_x_mm": f"{x:.3f}", "anchor_y_mm": "422.500", "anchor_basis": "planning sub-anchor inside shared BP-018 envelope; not a received terminal point", "terminal_position_state": "SELECTION REQUIRED", "cut_length_use": "PROHIBITED", "warning": WARNING})
    for ref, basis in (("F24", "unallocated BP-020 subregion"), ("J24", "unallocated BP-020 subregion"), ("JWF1", "unallocated connector within BP-012 PCB envelope"), ("JWP1", "unallocated connector within BP-012 PCB envelope")):
        result.append({"reference": ref, "coordinate_frame": "BACKPLATE-CATALOG-CANDIDATE", "anchor_x_mm": "SELECTION REQUIRED", "anchor_y_mm": "SELECTION REQUIRED", "anchor_basis": basis, "terminal_position_state": "SELECTION REQUIRED", "cut_length_use": "PROHIBITED", "warning": WARNING})
    for row in rows(DOOR):
        if row["reference"] in {"S0", "S1", "S2", "H1"}:
            result.append({"reference": row["reference"], "coordinate_frame": "DOOR-FACE-CATALOG-CANDIDATE", "anchor_x_mm": row["center_x_mm"], "anchor_y_mm": row["center_y_mm"], "anchor_basis": "door-face candidate center; hinge/loom transition not defined", "terminal_position_state": "SELECTION REQUIRED", "cut_length_use": "PROHIBITED", "warning": WARNING})
    return sorted(result, key=lambda row: row["reference"])


def route_status(placements: list[dict[str, str]]) -> list[dict[str, str]]:
    by_ref = {row["reference"]: row for row in placements}
    result = []
    for wire in rows(P2P):
        a, b = by_ref[wire["from_reference"]], by_ref[wire["to_reference"]]
        same_backplate = a["coordinate_frame"] == b["coordinate_frame"] == "BACKPLATE-CATALOG-CANDIDATE"
        numeric = same_backplate and a["anchor_x_mm"] != "SELECTION REQUIRED" and b["anchor_x_mm"] != "SELECTION REQUIRED"
        screen = "NOT CALCULATED"
        if numeric:
            screen = f'{abs(float(a["anchor_x_mm"]) - float(b["anchor_x_mm"])) + abs(float(a["anchor_y_mm"]) - float(b["anchor_y_mm"])):.3f}'
        result.append({
            "wire_id": wire["wire_id"], "net": wire["net"],
            "from_endpoint": f'{wire["from_reference"]}:{wire["from_terminal"]}',
            "to_endpoint": f'{wire["to_reference"]}:{wire["to_terminal"]}',
            "from_anchor_state": a["anchor_basis"], "to_anchor_state": b["anchor_basis"],
            "center_to_center_manhattan_screen_mm": screen,
            "screen_meaning": "planning-envelope arithmetic only; excludes terminal offsets, duct path, bends, service loops, door loom, segregation and installation allowance",
            "cut_length_mm": "SELECTION REQUIRED", "route_release": "NOT RELEASED",
            "warning": WARNING,
        })
    return result


def svg(layout_rows: list[dict[str, str]]) -> str:
    colors = {"wire_duct": "#dff3ff", "din_rail": "#9bb3c7", "distribution_block_envelope": "#f5bd18", "terminal_envelope": "#91cfff", "reserved_unallocated_envelope": "#f4f7fa"}
    shapes = []
    for row in layout_rows:
        if row["reference"] == "BP1":
            continue
        x, y, w, h = (float(row[key]) for key in ("x_mm", "y_mm", "width_mm", "height_mm"))
        fill = colors.get(row["object_type"], "#ffffff")
        dash = ' stroke-dasharray="6 5"' if "reserved" in row["object_type"] else ""
        shapes.append(f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="#0b2447" stroke-width="1"{dash}/><text x="{x + 2}" y="{y + min(13, max(8, h / 2))}" font-size="9" font-weight="700">{html.escape(row["reference"])}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 533.4 685.8" role="img" aria-labelledby="title desc"><title id="title">HR-V0 P0.7 candidate backplate layout</title><desc id="desc">Catalog-envelope planning view with DR5, WD4, XD24, XD0 and XN1 through XN3. No holes or cuts are released.</desc><rect width="533.4" height="685.8" fill="#f8fbff" stroke="#0b2447" stroke-width="3"/>{''.join(shapes)}</svg>'''


def guide(route_rows: list[dict[str, str]]) -> str:
    table = "".join(f'<tr data-state="{html.escape(row["route_release"])}"><td>{html.escape(row["wire_id"])}</td><td>{html.escape(row["net"])}</td><td>{html.escape(row["from_endpoint"])}</td><td>{html.escape(row["to_endpoint"])}</td><td>{html.escape(row["center_to_center_manhattan_screen_mm"])}</td><td>{html.escape(row["cut_length_mm"])}</td></tr>' for row in route_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 panel node placement</title><style>:root{{--ink:#092746;--blue:#1268a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f8fbff;--line:#82b9dd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--ink),#0c5c99);color:white;padding:28px max(20px,5vw);border-bottom:7px solid var(--gold)}}main{{max-width:1200px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(34px,5vw,60px);line-height:1.06}}h2{{font-size:clamp(26px,3vw,38px)}}.warn{{background:#fff2bd;color:#402d00;border:3px solid var(--gold);padding:16px;font-weight:850}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:15px}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px}}.metric{{font-size:34px;font-weight:900;color:var(--blue)}}.drawing{{background:white;border:2px solid var(--line);padding:14px;max-height:800px;overflow:auto}}.drawing img{{display:block;width:min(100%,720px);margin:auto}}label{{font-weight:800}}input{{font:inherit;width:100%;padding:12px;border:2px solid var(--line);border-radius:8px;margin:8px 0 16px}}.tablewrap{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:820px;background:white;font-size:14px}}th,td{{border:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}}th{{background:var(--sky);position:sticky;top:0}}a{{color:#07599b;font-weight:700}}@media(max-width:700px){{main{{padding:20px 14px 48px}}.grid{{grid-template-columns:1fr}}}}</style></head><body><header><div class="warn">{WARNING}</div><p>{IDENTIFIER} · R223</p><h1>Five real nodes now have a candidate place.</h1><p>The lower reserve receives a planning rail and duct. This is a catalog-envelope fit and stock-allocation screen—not a drilling, cutting, wiring or energization release.</p></header><main><section class="grid"><article class="card"><div class="metric">5</div><p>Explicit topology nodes placed.</p></article><article class="card"><div class="metric">160 mm</div><p>DR5 planning rail.</p></article><article class="card"><div class="metric">323.8 mm</div><p>WD4 planning duct.</p></article><article class="card"><div class="metric">0</div><p>Released holes, cuts or wires.</p></article></section><h2>Candidate backplate view</h2><div class="drawing"><img src="panel-layout.svg" alt="Candidate backplate layout showing the new lower DR5 rail, WD4 duct, XD24, XD0 and XN1 through XN3"></div><h2>Stock arithmetic</h2><div class="grid"><article class="card"><strong>Rail B</strong><p>500 − 153.8 − 100 − 160 = <b>86.2 mm</b> before kerf.</p></article><article class="card"><strong>Duct A</strong><p>2000 − 665.8 − 665.8 − 323.8 − 323.8 = <b>20.8 mm</b> before kerf.</p></article></div><div class="warn">The 20.8 mm duct residual is not a cut release. Kerf, tolerance, damage allowance and received stock must be accepted first.</div><h2>Conductor route closure</h2><p>Numeric values below are center-to-center Manhattan screens between planning envelopes only. They are deliberately prohibited as cut lengths.</p><label for="search">Search conductor or net</label><input id="search" type="search" placeholder="P2P-023 or SAFETY_24V"><div class="tablewrap"><table><thead><tr><th>Wire</th><th>Net</th><th>From</th><th>To</th><th>Planning screen mm</th><th>Cut length</th></tr></thead><tbody id="routes">{table}</tbody></table></div><h2>Controlled records</h2><p><a href="candidate-backplate-layout.csv">Layout</a> · <a href="reference-placement-register.csv">Placement anchors</a> · <a href="conductor-route-status.csv">Route status</a> · <a href="stock-allocation-screen.csv">Stock screen</a> · <a href="bom-integration.csv">BOM integration</a> · <a href="open-holds.csv">Open holds</a></p><div class="warn">Every terminal position, cut length, end preparation and physical result remains open. No procurement, drilling, cutting, wiring, connection, powered testing, motion or energization is authorized.</div></main><script>const q=document.querySelector('#search'),rs=[...document.querySelectorAll('#routes tr')];q.addEventListener('input',()=>{{const v=q.value.toLowerCase();rs.forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(v))}});</script></body></html>'''


def main() -> None:
    layout_rows = layout()
    placements = placement_register(layout_rows)
    route_rows = route_status(placements)
    stock = [
        {"stock_id": "RAIL-B", "manufacturer_item": "Phoenix Contact 1207648", "stock_length_mm": "500", "prior_allocations_mm": "153.8 + 100", "new_allocation": "DR5 160", "residual_before_kerf_mm": "86.2", "result": "CATALOG STOCK SCREEN PASS; NO CUT RELEASE", "warning": WARNING},
        {"stock_id": "DUCT-A", "manufacturer_item": "Phoenix Contact 3240189", "stock_length_mm": "2000", "prior_allocations_mm": "665.8 + 665.8 + 323.8", "new_allocation": "WD4 323.8", "residual_before_kerf_mm": "20.8", "result": "ARITHMETIC PASS; KERF/TOLERANCE/RECEIVED STOCK HOLD", "warning": WARNING},
    ]
    bom = [
        {"item_id": "BOM-083", "candidate": "Phoenix Contact 1207648", "quantity": "2", "R223_effect": "DR5 160 mm added within existing two-stock arithmetic; no added stock", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-084", "candidate": "Phoenix Contact 3240189", "quantity": "1", "R223_effect": "WD4 323.8 mm added within existing stock arithmetic; 20.8 mm before kerf", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-085", "candidate": "Phoenix Contact 3022218", "quantity": "8", "R223_effect": "two held DR5 end-bracket candidates added", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-092", "candidate": "Phoenix Contact 3273114 x1; 3273112 x1", "quantity": "2", "R223_effect": "XD24 and XD0 distribution-block candidates", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-093", "candidate": "Phoenix Contact 3209549", "quantity": "3", "R223_effect": "XN1/XN2/XN3 junction-terminal candidates", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-094", "candidate": "Phoenix Contact 3030488", "quantity": "1", "R223_effect": "PT 2,5-TWIN open-side end-cover candidate", "state": "EXACT CANDIDATE HOLD", "warning": WARNING},
        {"item_id": "BOM-095", "candidate": "SELECTION REQUIRED", "quantity": "SYSTEM GROUP", "R223_effect": "node markers, partitions/covers and any additional accessories", "state": "SELECTION REQUIRED", "warning": WARNING},
    ]
    sources = [
        {"source_id": "NPL-SRC-001", "manufacturer": "Phoenix Contact", "item": "3273114", "document_revision_or_date": "online-catalog PDF generated 2026-08-10; accessed 2026-08-11", "official_url": "https://www.phoenixcontact.com/us/products/3273114", "verified_fact": "28.6 mm width; 58.1 mm height; 32.4 mm depth on NS35/7.5; 19 connections", "does_not_establish": "Project loading, protection, received fit or release", "warning": WARNING},
        {"source_id": "NPL-SRC-002", "manufacturer": "Phoenix Contact", "item": "3273112", "document_revision_or_date": "online catalog accessed 2026-08-11", "official_url": "https://www.phoenixcontact.com/us/products/3273112", "verified_fact": "blue member of same PTFIX 6/18X2.5-NS35 family; candidate envelope controlled as 28.6 x 58.1 mm", "does_not_establish": "received identity, project return policy, application or release", "warning": WARNING},
        {"source_id": "NPL-SRC-003", "manufacturer": "Phoenix Contact", "item": "3209549", "document_revision_or_date": "online-catalog PDF generated 2026-08-10; accessed 2026-08-11", "official_url": "https://www.phoenixcontact.com/us/products/3209549", "verified_fact": "5.2 mm width; 60.4 mm height; 36.8 mm depth on NS35/7.5; open side; 3030488 listed end cover", "does_not_establish": "project accessory completeness, segregation, received fit or release", "warning": WARNING},
        {"source_id": "NPL-SRC-004", "manufacturer": "Project Button", "item": "HR-V0-CP-CONFIG-P0.1 / HR-V0-PANEL-P2P-P0.1", "document_revision_or_date": "R220/R222; 2026-08-11", "official_url": "release/hr-v0/control-panel-configuration-p0.1/; release/hr-v0/panel-point-to-point-p0.1/", "verified_fact": "controlled P0.6 geometry overlay and 55 two-ended conductors", "does_not_establish": "received geometry, terminal entry coordinates or cut lengths", "warning": WARNING},
    ]
    holds = [
        ("NPL-H-001", "P1.18 configuration disposition", "Independent ECAD/electrical review and formal acceptance or correction"),
        ("NPL-H-002", "received enclosure/backplate geometry", "received measurements and accepted coordinate reconciliation"),
        ("NPL-H-003", "DR5/WD4 cut release", "received stock, kerf/tolerance, cut/deburr/coating and inspection plan"),
        ("NPL-H-004", "node received fit and terminal access", "received identity/dimensions, rail engagement, bend/tool/marker/cover access"),
        ("NPL-H-005", "PTFIX support/accessories", "manufacturer/application disposition for adapters, alignment, end support, covers and markings"),
        ("NPL-H-006", "PT terminal end cover/segregation", "accepted 3030488 use plus partition/marker and different-potential adjacency disposition"),
        ("NPL-H-007", "holes, fasteners and bonding", "released coordinates, hardware, coating preparation, torque, PE/bonding and load proof"),
        ("NPL-H-008", "point-to-point routes and cut lengths", "terminal entry coordinates, duct path, bend/service loops, segregation and measured cut list"),
        ("NPL-H-009", "door loom", "dynamic-flex cable, hinge path, bend/torsion/abrasion/cycle-life and strain relief"),
        ("NPL-H-010", "duct fill and separation", "accepted conductor set, fill/temperature/bundle/separation calculations and cover access"),
        ("NPL-H-011", "loading, protection and thermal", "fault/inrush/current totals, F24/branch coordination and temperature-rise evidence"),
        ("NPL-H-012", "installed inspection and qualified release", "received/as-built point-to-point, pull, torque, label, continuity, polarity, isolation, thermal/fault evidence and signatures"),
    ]
    hold_rows = [{"hold_id": hid, "subject": subject, "state": "OPEN", "closure_evidence": evidence, "accepted": "FALSE", "warning": WARNING} for hid, subject, evidence in holds]
    authority = [{"activity": activity, "permitted": permitted, "boundary": boundary, "warning": WARNING} for activity, permitted, boundary in [
        ("internal catalog-envelope review", "TRUE", "read-only review and correction only"),
        ("procurement", "FALSE", "no part or stock purchase released"),
        ("cutting/drilling/assembly", "FALSE", "no cut, hole, fastener or installation released"),
        ("wiring/connection/powered testing", "FALSE", "no conductor preparation, connection or power"),
        ("motion/energization", "FALSE", "all energization gates remain unresolved"),
    ]]
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory / "candidate-backplate-layout.csv", layout_rows)
        write_csv(directory / "reference-placement-register.csv", placements)
        write_csv(directory / "conductor-route-status.csv", route_rows)
        write_csv(directory / "stock-allocation-screen.csv", stock)
        write_csv(directory / "bom-integration.csv", bom)
        write_csv(directory / "source-register.csv", sources)
        write_csv(directory / "open-holds.csv", hold_rows)
        write_csv(directory / "authority-boundary.csv", authority)
        (directory / "panel-layout.svg").write_text(svg(layout_rows), encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR223 places the five R222 topology nodes on a held DR5/WD4 catalog-envelope candidate. No terminal entry coordinate, hole, cut, wire or physical result is released.\n", encoding="utf-8", newline="\n")
        status = {"identifier": IDENTIFIER, "round": "R223", "date": "2026-08-11", "layout_records": len(layout_rows), "explicit_nodes": 5, "route_records": len(route_rows), "routes_with_planning_screen": sum(row["center_to_center_manhattan_screen_mm"] != "NOT CALCULATED" for row in route_rows), "released_cut_lengths": 0, "open_holds": len(hold_rows), "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "warning": WARNING}
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(route_rows), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": path.name, "bytes": str(path.stat().st_size), "sha256": digest(path)} for path in files])
    print(f"{IDENTIFIER}: {len(layout_rows)} layout records; 5 nodes; {len(route_rows)} conductor route states; 12 holds")
    print("DR5/WD4 fit existing stock arithmetically; zero holes, cuts, wires or work authority")


if __name__ == "__main__":
    main()
