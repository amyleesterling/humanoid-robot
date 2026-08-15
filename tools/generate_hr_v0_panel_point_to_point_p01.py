#!/usr/bin/env python3
"""Generate the R222 explicit HR-V0 control-panel point-to-point candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release/hr-v0/panel-conductor-basis-p0.1/endpoint-conductor-candidate-schedule.csv"
OLD_PANEL = ROOT / "electrical/panel/hr-v0-control-panel-p0.6/stationary-wire-schedule.csv"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
OUT = ROOT / "release/hr-v0/panel-point-to-point-p0.1"
IDENTIFIER = "HR-V0-PANEL-P2P-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def ep(ref: str, terminal: str) -> str:
    return f"{ref}:{terminal}"


def main() -> int:
    source_rows = read(SOURCE)
    if len(source_rows) != 66:
        raise RuntimeError(f"expected 66 R221 endpoints, found {len(source_rows)}")
    legacy_by_key = {(row["reference"], row["terminal"]): row for row in source_rows}
    if len(legacy_by_key) != 66:
        raise RuntimeError("duplicate R221 endpoint")
    old_routes = {row["wire_number"]: row["routing_zone"] for row in read(OLD_PANEL)}
    by_net: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        by_net[row["net"]].append(row)

    direct_nets = sorted(net for net, rows in by_net.items() if len(rows) == 2)
    three_nodes = {"SR1_S12": "XN1", "SRA1_S12": "XN2", "SR1_STATUS": "XN3"}
    single_targets = {
        "K1_A1": ("FSR1", "2"), "K2_A1": ("FSR2", "2"),
        "SRA1_K1_RAW": ("FSR1", "1"), "SRA1_K2_RAW": ("FSR2", "1"),
        "WD1_COIL_N": ("JWP1", "3"), "WD2_COIL_N": ("JWP1", "4"),
        "WD1_NC_24V": ("JWF1", "1"), "WD2_NC_24V": ("JWF1", "2"),
    }
    if set(net for net, rows in by_net.items() if len(rows) == 3) != set(three_nodes):
        raise RuntimeError("unexpected three-endpoint net set")
    if set(net for net, rows in by_net.items() if len(rows) == 1) != set(single_targets):
        raise RuntimeError("unexpected one-endpoint net set")
    if {"SAFETY_24V", "SAFETY_0V"} - set(by_net):
        raise RuntimeError("common rail missing")

    wires: list[dict[str, object]] = []
    endpoint_map: list[dict[str, object]] = []
    used_legacy: set[str] = set()

    def add(net: str, a_ref: str, a_term: str, b_ref: str, b_term: str,
            a_legacy: str = "", b_legacy: str = "", route: str = "FIXED INTERNAL PANEL") -> None:
        wire_id = f"P2P-{len(wires) + 1:03d}"
        legacy_ids = [value for value in (a_legacy, b_legacy) if value]
        for legacy_id in legacy_ids:
            if legacy_id in used_legacy:
                raise RuntimeError(f"legacy endpoint reused: {legacy_id}")
            used_legacy.add(legacy_id)
        door = any(legacy_by_key[(row["reference"], row["terminal"])]["reference"] in {"S0", "S1", "S2", "H1"}
                   for row in source_rows if row["wire_number"] in legacy_ids)
        family = "SELECTION REQUIRED" if door else "Belden 3057 family"
        gauge = "SELECTION REQUIRED" if door else "16 AWG / approximately 1.31 mm2"
        state = "NO DYNAMIC-FLEX CANDIDATE" if door else "FIXED-INTERNAL FAMILY/GAUGE CANDIDATE ONLY"
        wires.append({
            "wire_id": wire_id, "net": net,
            "from_reference": a_ref, "from_terminal": a_term,
            "to_reference": b_ref, "to_terminal": b_term,
            "from_legacy_endpoint": a_legacy, "to_legacy_endpoint": b_legacy,
            "conductor_family_candidate": family, "gauge_candidate": gauge,
            "exact_color_order_code": "SELECTION REQUIRED", "cut_length_mm": "SELECTION REQUIRED",
            "termination_from": "SELECTION REQUIRED", "termination_to": "SELECTION REQUIRED",
            "route_zone": route, "candidate_state": state, "release_state": "NOT RELEASED",
            "warning": WARNING,
        })
        for end, ref, term, legacy_id in (("A", a_ref, a_term, a_legacy), ("B", b_ref, b_term, b_legacy)):
            if legacy_id:
                source = next(row for row in source_rows if row["wire_number"] == legacy_id)
                endpoint_map.append({
                    "legacy_endpoint_id": legacy_id, "sheet": source["sheet"], "reference": ref,
                    "terminal": term, "net": net, "physical_wire_id": wire_id, "wire_end": end,
                    "mapping_state": "EXACT CANDIDATE", "warning": WARNING,
                })

    for net in direct_nets:
        if net in {"SAFETY_24V", "SAFETY_0V"}:
            continue
        rows = sorted(by_net[net], key=lambda row: row["wire_number"])
        route = " / ".join(sorted({old_routes[row["wire_number"]] for row in rows}))
        add(net, rows[0]["reference"], rows[0]["terminal"], rows[1]["reference"], rows[1]["terminal"],
            rows[0]["wire_number"], rows[1]["wire_number"], route)

    for net, node in three_nodes.items():
        for position, row in enumerate(sorted(by_net[net], key=lambda item: item["wire_number"]), 1):
            add(net, row["reference"], row["terminal"], node, str(position), row["wire_number"], "",
                old_routes[row["wire_number"]])

    for net, (target_ref, target_term) in single_targets.items():
        row = by_net[net][0]
        add(net, row["reference"], row["terminal"], target_ref, target_term, row["wire_number"], "",
            old_routes[row["wire_number"]])

    rail_defs = {
        "SAFETY_24V": ("XD24", ("F24", "OUT"), ("JWP1", "1")),
        "SAFETY_0V": ("XD0", ("J24", "3"), ("JWP1", "2")),
    }
    for net, (node, feed, pcb_load) in rail_defs.items():
        add(net, feed[0], feed[1], node, "LINE", "", "", "CONTROL SOURCE / DISTRIBUTION FEED")
        rows = sorted(by_net[net], key=lambda row: row["wire_number"])
        for position, row in enumerate(rows, 1):
            add(net, node, f"{position:02d}", row["reference"], row["terminal"], "", row["wire_number"],
                old_routes[row["wire_number"]])
        add(net, node, f"{len(rows) + 1:02d}", pcb_load[0], pcb_load[1], "", "", "WATCHDOG PCB INTERFACE")

    if len(wires) != 55:
        raise RuntimeError(f"expected 55 physical conductors, found {len(wires)}")
    if used_legacy != {row["wire_number"] for row in source_rows}:
        raise RuntimeError("not every R221 endpoint is mapped exactly once")

    wire_fields = list(wires[0])
    write("point-to-point-wire-schedule.csv", wire_fields, wires)
    endpoint_map.sort(key=lambda row: row["legacy_endpoint_id"])
    write("endpoint-to-wire-map.csv", list(endpoint_map[0]), endpoint_map)

    nodes = [
        {"reference": "XD24", "function": "SAFETY_24V distribution", "manufacturer": "Phoenix Contact", "mpn": "3273114", "description": "PTFIX 6/18X2,5-NS35 RD", "modeled_positions": "LINE;01..14", "physical_spares": "15..18 - live potential; cover and mark", "catalog_state": "EXACT CATALOG CANDIDATE", "application_state": "SELECTION REQUIRED", "warning": WARNING},
        {"reference": "XD0", "function": "SAFETY_0V distribution", "manufacturer": "Phoenix Contact", "mpn": "3273112", "description": "PTFIX 6/18X2,5-NS35 BU", "modeled_positions": "LINE;01..07", "physical_spares": "08..18 - live potential; cover and mark", "catalog_state": "EXACT CATALOG CANDIDATE", "application_state": "SELECTION REQUIRED", "warning": WARNING},
        {"reference": "XN1", "function": "SR1_S12 explicit three-way node", "manufacturer": "Phoenix Contact", "mpn": "3209549", "description": "PT 2,5-TWIN", "modeled_positions": "1..3", "physical_spares": "NONE", "catalog_state": "EXACT CATALOG CANDIDATE", "application_state": "SELECTION REQUIRED", "warning": WARNING},
        {"reference": "XN2", "function": "SRA1_S12 explicit three-way node", "manufacturer": "Phoenix Contact", "mpn": "3209549", "description": "PT 2,5-TWIN", "modeled_positions": "1..3", "physical_spares": "NONE", "catalog_state": "EXACT CATALOG CANDIDATE", "application_state": "SELECTION REQUIRED", "warning": WARNING},
        {"reference": "XN3", "function": "SR1_STATUS explicit diagnostic three-way node", "manufacturer": "Phoenix Contact", "mpn": "3209549", "description": "PT 2,5-TWIN", "modeled_positions": "1..3", "physical_spares": "NONE", "catalog_state": "EXACT CATALOG CANDIDATE", "application_state": "SELECTION REQUIRED", "warning": WARNING},
    ]
    write("terminal-node-register.csv", list(nodes[0]), nodes)

    sources = [
        {"source_id": "P2P-SRC-001", "manufacturer": "Project Button", "artifact": "R221 endpoint conductor schedule", "revision_or_date": "HR-V0-PANEL-COND-P0.1; 2026-08-11", "official_url_or_path": SOURCE.relative_to(ROOT).as_posix(), "verified_fact": "66 unique one-ended panel records", "does_not_establish": "A buildable two-ended schedule", "warning": WARNING},
        {"source_id": "P2P-SRC-002", "manufacturer": "Project Button", "artifact": "P1.18 native KiCad panel-topology candidate", "revision_or_date": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE; 2026-08-11", "official_url_or_path": P118.relative_to(ROOT).as_posix() + "/", "verified_fact": "XD24/XD0/XN1/XN2/XN3 are explicit native ECAD component blocks", "does_not_establish": "Physical correctness, protection or release", "warning": WARNING},
        {"source_id": "P2P-SRC-003", "manufacturer": "Phoenix Contact", "artifact": "PTFIX 6/18X2,5-NS35 RD", "revision_or_date": "item 3273114; generated PDF 2026-08-10; accessed 2026-08-11", "official_url_or_path": "https://www.phoenixcontact.com/us/products/3273114", "verified_fact": "19 connections; NS35; line 0.5-10 mm2 flexible; load 0.14-4 mm2 flexible; 24 A nominal", "does_not_establish": "Project protection, current, wire, spare cover or physical acceptance", "warning": WARNING},
        {"source_id": "P2P-SRC-004", "manufacturer": "Phoenix Contact", "artifact": "PTFIX 6/18X2,5-NS35 BU", "revision_or_date": "item 3273112; live record accessed 2026-08-11", "official_url_or_path": "https://www.phoenixcontact.com/us/products/3273112", "verified_fact": "19 connections; NS35; line 0.5-10 mm2 flexible; load 0.14-4 mm2 flexible; 24 A nominal", "does_not_establish": "Project return policy, protection, wire or physical acceptance", "warning": WARNING},
        {"source_id": "P2P-SRC-005", "manufacturer": "Phoenix Contact", "artifact": "PT 2,5-TWIN", "revision_or_date": "item 3209549; generated PDF 2026-08-10; accessed 2026-08-11", "official_url_or_path": "https://www.phoenixcontact.com/us/products/3209549", "verified_fact": "three independent push-in connections; 0.14-4 mm2 flexible; 8-10 mm strip; 24 A nominal", "does_not_establish": "Project conductor, marker, rail placement or safety acceptance", "warning": WARNING},
        {"source_id": "P2P-SRC-006", "manufacturer": "Phoenix Contact", "artifact": "PT 4-HESI (5X20)", "revision_or_date": "item 3211861; live record accessed 2026-08-11", "official_url_or_path": "https://www.phoenixcontact.com/en-us/products/fuse-terminal-block-pt-4-hesi-5x20-3211861", "verified_fact": "two push-in connections; flexible 0.2-4 mm2; 10-12 mm strip; fuse link not supplied", "does_not_establish": "Fuse-link selection or coordination", "warning": WARNING},
    ]
    write("source-register.csv", list(sources[0]), sources)

    holds = [
        ("P2P-H-001", "configuration promotion", "P1.18 is a candidate and is not the accepted system ECAD", "Independent ECAD/electrical review and formal configuration disposition"),
        ("P2P-H-002", "distribution application", "XD24/XD0 catalog identities do not establish Project Button loading or protection", "Fault/inrush/current totals, protection coordination, temperature and qualified application review"),
        ("P2P-H-003", "door loom", "Ten moving-door endpoints have no cable candidate", "Exact dynamic-flex cable, bend/torsion/abrasion/separation/cycle-life evidence"),
        ("P2P-H-004", "wire identities", "Every exact color/order code remains open", "Accepted color convention and exact current order codes"),
        ("P2P-H-005", "cut list and routing", "Every cut length and detailed route remains open", "Received enclosure/door geometry, route measurement, service loops and duct allocation"),
        ("P2P-H-006", "termination process", "Every end preparation remains open", "Direct/ferrule/lug selection, tool/die, strip, torque, inspection and pull test"),
        ("P2P-H-007", "electrical sizing", "DCR, voltage drop, ampacity, bundling and duct fill are unclosed", "Lengths, DCR/temperature basis, currents, ambient, bundle, jurisdiction and calculation"),
        ("P2P-H-008", "physical placement", "Five new nodes have no accepted rail coordinate or access proof", "Updated panel layout, bend/access/cover/marker fit and received metrology"),
        ("P2P-H-009", "received identity", "All terminal and operator identities remain unreceived", "Receiving, terminal markings, continuity, polarity and accessory reconciliation"),
        ("P2P-H-010", "installed verification and release", "No conductor has been cut, installed or tested", "Point-to-point, pull, label, torque, separation, continuity, polarity, isolation, thermal/fault tests and signed review"),
    ]
    hold_rows = [{"hold_id": i, "subject": s, "current_state": st, "closure_evidence": ev, "accepted": "FALSE", "warning": WARNING} for i, s, st, ev in holds]
    write("open-holds.csv", list(hold_rows[0]), hold_rows)

    authority = [
        {"action": "internal generation and review", "allowed": "TRUE", "boundary": "Read-only review, redline and checker execution", "warning": WARNING},
        {"action": "procurement or supplier contact", "allowed": "FALSE", "boundary": "Separate written authority required", "warning": WARNING},
        {"action": "cut, terminate, install or connect wire", "allowed": "FALSE", "boundary": "All P2P-H holds and stage gate must close", "warning": WARNING},
        {"action": "powered test, motion or energization", "allowed": "FALSE", "boundary": "Separate qualified stage authorization required", "warning": WARNING},
    ]
    write("authority-boundary.csv", list(authority[0]), authority)

    status = {
        "identifier": IDENTIFIER, "date": "2026-08-11", "round": "R222",
        "source_endpoint_count": 66, "physical_conductor_count": 55,
        "legacy_endpoints_mapped_once": 66, "explicit_terminal_nodes": 5,
        "door_endpoints_without_conductor_candidate": 10, "open_holds": 10,
        "ecad_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "current_system_ecad_unchanged": "V3-P1.15-CARRIER-CANDIDATE",
        "fabrication_approved": False, "connection_approved": False, "energization_approved": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    rows_html = "".join(
        f'<tr data-net="{html.escape(str(row["net"]))}" data-state="{html.escape(str(row["candidate_state"]))}">'
        f'<td>{html.escape(str(row["wire_id"]))}</td><td>{html.escape(str(row["net"]))}</td>'
        f'<td>{html.escape(ep(str(row["from_reference"]), str(row["from_terminal"])))}</td>'
        f'<td>{html.escape(ep(str(row["to_reference"]), str(row["to_terminal"])))}</td>'
        f'<td>{html.escape(str(row["conductor_family_candidate"]))}</td>'
        f'<td>{html.escape(str(row["route_zone"]))}</td><td>{html.escape(str(row["candidate_state"]))}</td></tr>'
        for row in wires
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--sky:#e7f6ff;--blue:#083b66;--mid:#0b67a3;--gold:#f3b61f;--paper:#fff;--line:#aacfe6;--danger:#7a3500}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--blue);font:16px/1.5 system-ui,sans-serif}}header,main{{max-width:1500px;margin:auto;padding:24px}}header{{background:var(--blue);color:white;max-width:none}}header>div{{max-width:1500px;margin:auto}}h1{{font-size:clamp(28px,4vw,52px);line-height:1.1;margin:.3rem 0}}h2{{font-size:clamp(22px,2.5vw,34px)}}.warning{{background:var(--gold);color:#3a2800;padding:14px 18px;font-weight:800;border-radius:8px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:20px 0}}.card{{background:white;border:2px solid var(--line);border-radius:12px;padding:16px}}.card strong{{display:block;font-size:30px}}label{{font-weight:700}}input,select{{font:inherit;min-height:44px;padding:8px;border:2px solid var(--mid);border-radius:7px;background:white}}.controls{{display:flex;gap:14px;flex-wrap:wrap;align-items:end;margin:18px 0}}.control{{display:grid;gap:5px;min-width:240px}}.table-wrap{{overflow:auto;background:white;border:2px solid var(--line);border-radius:10px}}table{{border-collapse:collapse;width:100%;min-width:1150px}}th,td{{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{position:sticky;top:0;background:var(--blue);color:white;font-size:14px}}td{{font-size:14px}}code{{font-size:14px}}.note{{border-left:6px solid var(--gold);background:white;padding:16px;margin:18px 0}}a{{color:var(--mid)}}footer{{font-size:14px;padding:24px}}@media(max-width:600px){{header,main{{padding:16px}}.control{{min-width:100%}}}}
</style></head><body><header><div><div class="warning">{WARNING}</div><h1>HR-V0 explicit point-to-point candidate</h1><p>R222 converts 66 one-ended ECAD records into 55 two-ended physical conductor candidates with five explicit terminal nodes and no undocumented splice.</p></div></header><main>
<section class="cards"><div class="card"><strong>66/66</strong>legacy endpoints mapped once</div><div class="card"><strong>55</strong>physical conductors</div><div class="card"><strong>5</strong>explicit terminal nodes</div><div class="card"><strong>10</strong>door endpoints still unselected</div><div class="card"><strong>10</strong>open holds</div></section>
<div class="note"><strong>What changed:</strong> XD24 and XD0 make the 24 V and 0 V fanouts explicit. XN1, XN2 and XN3 replace the three implicit three-way junctions. P1.18 is a review candidate; P1.15 remains the current system ECAD until independent acceptance.</div>
<h2>Wire explorer</h2><div class="controls"><div class="control"><label for="q">Search</label><input id="q" placeholder="Wire, net, device, terminal"></div><div class="control"><label for="state">Candidate state</label><select id="state"><option value="">All</option><option>FIXED-INTERNAL FAMILY/GAUGE CANDIDATE ONLY</option><option>NO DYNAMIC-FLEX CANDIDATE</option></select></div></div>
<p id="count" aria-live="polite">Showing 55 conductors</p><div class="table-wrap"><table><thead><tr><th>Wire</th><th>Net</th><th>From</th><th>To</th><th>Conductor</th><th>Route zone</th><th>State</th></tr></thead><tbody id="rows">{rows_html}</tbody></table></div>
<h2>What remains open</h2><p>Exact wire order codes and colors, all lengths and routes, all end preparations, dynamic door cable, protection coordination, DCR/voltage drop, ampacity/bundling/duct fill, terminal receipt, physical installation, testing and qualified review remain unresolved.</p>
<p>Machine-readable evidence: <a href="point-to-point-wire-schedule.csv">wire schedule</a>, <a href="endpoint-to-wire-map.csv">endpoint map</a>, <a href="terminal-node-register.csv">terminal nodes</a>, <a href="open-holds.csv">open holds</a>, and <a href="package-status.json">package status</a>.</p></main><footer>{WARNING}</footer><script>
const q=document.querySelector('#q'),s=document.querySelector('#state'),rows=[...document.querySelectorAll('#rows tr')],count=document.querySelector('#count');function filter(){{const needle=q.value.trim().toLowerCase(),state=s.value;let shown=0;for(const row of rows){{const ok=(!needle||row.textContent.toLowerCase().includes(needle))&&(!state||row.dataset.state===state);row.hidden=!ok;if(ok)shown++}}count.textContent=`Showing ${{shown}} of ${{rows.length}} conductors`}}q.addEventListener('input',filter);s.addEventListener('change',filter);
</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Generated {IDENTIFIER}: {len(wires)} physical conductors / {len(endpoint_map)} mapped endpoints / {len(nodes)} nodes")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
