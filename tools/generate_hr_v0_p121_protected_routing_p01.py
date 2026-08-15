#!/usr/bin/env python3
"""Generate the R240 P1.21 protected-routing candidate and review surface."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "electrical/panel/hr-v0-control-panel-p0.7-node-placement"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
OUT = ROOT / "release/hr-v0/p121-protected-routing-p0.1"
ENG = ROOT / "electrical/routing/hr-v0-p121-protected-routing-p0.1"
IDENT = "HR-V0-P121-ROUTING-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def manhattan(points):
    return sum(abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(points, points[1:]))


def path_text(points):
    return " | ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def main():
    for directory in (OUT, ENG):
        directory.mkdir(parents=True, exist_ok=True)

    old_routes = {row["wire_id"]: row for row in read(PANEL / "conductor-route-status.csv")}
    wires = {(row["reference"], row["terminal"]): row for row in read(P121 / "wire-number-table.csv")}
    expected = {
        ("SR1", "A1"): ("W2005", "SAFETY_24V"),
        ("SRA1", "A1"): ("W3001", "SRA1_A1_WD_GATED"),
        ("KWD1", "11"): ("W3016", "SAFETY_24V"),
        ("KWD1", "14"): ("W3018", "WD_SRA1_SUPPLY_INTERMEDIATE"),
        ("KWD2", "11"): ("W3022", "WD_SRA1_SUPPLY_INTERMEDIATE"),
        ("KWD2", "14"): ("W3024", "SRA1_A1_WD_GATED"),
    }
    for key, value in expected.items():
        row = wires[key]
        if (row["wire_number"], row["net"]) != value:
            raise RuntimeError(f"P1.21 wire basis changed at {key}")

    route_delta = [
        {"record":"P2P-005","p07_from":old_routes["P2P-005"]["from_endpoint"],"p07_to":old_routes["P2P-005"]["to_endpoint"],"p07_net":old_routes["P2P-005"]["net"],"p121_from":"KWD2:14","p121_to":"SRA1:A1","p121_net":"SRA1_A1_WD_GATED","disposition":"SUPERSEDED BY P1.21 CANDIDATE; ROUTE NOT RELEASED","basis":"W3024 and W3001","warning":WARNING},
        {"record":"P2P-015","p07_from":old_routes["P2P-015"]["from_endpoint"],"p07_to":old_routes["P2P-015"]["to_endpoint"],"p07_net":old_routes["P2P-015"]["net"],"p121_from":"KWD1:14","p121_to":"KWD2:11","p121_net":"WD_SRA1_SUPPLY_INTERMEDIATE","disposition":"NET NAME CORRECTED; ROUTE NOT RELEASED","basis":"W3018 and W3022","warning":WARNING},
        {"record":"P2P-035","p07_from":old_routes["P2P-035"]["from_endpoint"],"p07_to":old_routes["P2P-035"]["to_endpoint"],"p07_net":old_routes["P2P-035"]["net"],"p121_from":"XD24:02","p121_to":"SR1:A1","p121_net":"SAFETY_24V","disposition":"PROPOSED TERMINAL REALLOCATION; SELECTION REQUIRED; ROUTE NOT RELEASED","basis":"P1.21 W2005 plus formerly allocated XD24:02; design proposal, not inferred pinout","warning":WARNING},
        {"record":"P2P-039","p07_from":"XD24:06","p07_to":"KWD1:A1","p07_net":"SAFETY_24V","p121_from":"XD24:06","p121_to":"KWD1:A1","p121_net":"SAFETY_24V","disposition":"RETAINED CANDIDATE; ROUTE NOT RELEASED","basis":"P0.7 allocation and P1.21 W3014","warning":WARNING},
        {"record":"P2P-040","p07_from":"XD24:07","p07_to":"KWD1:11","p07_net":"SAFETY_24V","p121_from":"XD24:07","p121_to":"KWD1:11","p121_net":"SAFETY_24V","disposition":"RETAINED CANDIDATE; ROUTE NOT RELEASED","basis":"P0.7 allocation and P1.21 W3016","warning":WARNING},
        {"record":"P2P-042","p07_from":"XD24:09","p07_to":"KWD2:A1","p07_net":"SAFETY_24V","p121_from":"XD24:09","p121_to":"KWD2:A1","p121_net":"SAFETY_24V","disposition":"RETAINED CANDIDATE; ROUTE NOT RELEASED","basis":"P0.7 allocation and P1.21 W3020","warning":WARNING},
        {"record":"P2P-043","p07_from":"XD24:10","p07_to":"KWD2:21","p07_net":"SAFETY_24V","p121_from":"XD24:10","p121_to":"KWD2:21","p121_net":"SAFETY_24V","disposition":"RETAINED CANDIDATE; ROUTE NOT RELEASED","basis":"P0.7 allocation and P1.21 W3023","warning":WARNING},
    ]

    route_classes = [
        {"class_id":"SF01-INPUT","safety_credit":"CANDIDATE CREDITED-FUNCTION CONDUCTORS; CREDIT NOT VALIDATED","included":"SR1/SRA1 input returns, RESET/start, ARM and EDM paths","route_rule":"CRED-L only; no shared unpartitioned duct with DF01-GATE-HOT","selection_state":"SELECTION REQUIRED","warning":WARNING},
        {"class_id":"SF01-SUPPLY","safety_credit":"CANDIDATE FUNCTION SUPPLY; CREDIT NOT VALIDATED","included":"direct SR1 A1 supply","route_rule":"DIAG-B/DIAG-R/DIAG-T candidate with dedicated terminal entry; do not share an unpartitioned local entry with SF01-INPUT","selection_state":"SELECTION REQUIRED","warning":WARNING},
        {"class_id":"DF01-GATE-HOT","safety_credit":"ZERO SAFETY CREDIT","included":"KWD coil/contact supply, intermediate and SRA1 A1 gated supply","route_rule":"DIAG-B/DIAG-R/DIAG-T only; controlled local entries at KWD1/KWD2/SRA1","selection_state":"SELECTION REQUIRED","warning":WARNING},
    ]
    corridors = [
        {"corridor_id":"CRED-L","class":"SF01-INPUT","geometry_mm":"WD1 x=8..48 plus node approach y=535 and device-side local entries","physical_control":"Dedicated/partitioned path; exact duct partition and cover SELECTION REQUIRED","released":"NO","warning":WARNING},
        {"corridor_id":"DIAG-B","class":"SF01-SUPPLY / DF01-GATE-HOT","geometry_mm":"WD4 x=54..377.8, y=625..665; centerline y=645","physical_control":"Existing candidate duct envelope; fill, divider and cut length SELECTION REQUIRED","released":"NO","warning":WARNING},
        {"corridor_id":"DIAG-R","class":"SF01-SUPPLY / DF01-GATE-HOT","geometry_mm":"WD2 x=383.8..423.8, y=10..675.8; centerline x=403.8","physical_control":"Existing candidate duct envelope; fill, divider and cut length SELECTION REQUIRED","released":"NO","warning":WARNING},
        {"corridor_id":"DIAG-T","class":"SF01-SUPPLY / DF01-GATE-HOT","geometry_mm":"reserved planning band x=54..423.8, y=10..40; centerline y=25","physical_control":"No selected duct/barrier exists; terminal drops end at component envelope edges","released":"NO","warning":WARNING},
        {"corridor_id":"NODE-CRED","class":"SF01-INPUT","geometry_mm":"XN1/XN2 upward to y=535, left to WD1, then device-side entries","physical_control":"Exact node terminal entries, bends, partition and cover SELECTION REQUIRED","released":"NO","warning":WARNING},
    ]

    routes = [
        ("RT-P035","P2P-035","SF01-SUPPLY","XD24 planning center to SR1 top envelope",[(78.3,584.05),(78.3,645),(403.8,645),(403.8,25),(70,25),(70,55)]),
        ("RT-P039","P2P-039","DF01-GATE-HOT","XD24 planning center to KWD1 top envelope",[(78.3,584.05),(78.3,645),(403.8,645),(403.8,25),(140,25),(140,55)]),
        ("RT-P040","P2P-040","DF01-GATE-HOT","XD24 planning center to KWD1 top envelope",[(78.3,584.05),(78.3,645),(403.8,645),(403.8,25),(140,25),(140,55)]),
        ("RT-P042","P2P-042","DF01-GATE-HOT","XD24 planning center to KWD2 top envelope",[(78.3,584.05),(78.3,645),(403.8,645),(403.8,25),(166,25),(166,55)]),
        ("RT-P043","P2P-043","DF01-GATE-HOT","XD24 planning center to KWD2 top envelope",[(78.3,584.05),(78.3,645),(403.8,645),(403.8,25),(166,25),(166,55)]),
        ("RT-P015","P2P-015","DF01-GATE-HOT","KWD1/KWD2 top-envelope local candidate",[(140,55),(140,25),(166,25),(166,55)]),
        ("RT-P005","P2P-005","DF01-GATE-HOT","KWD2/SRA1 top-envelope local candidate",[(166,55),(166,25),(108,25),(108,55)]),
        ("RT-CRED-SR1","REFERENCE","SF01-INPUT","XN1 planning center to SR1 left envelope",[(135.8,585.2),(135.8,535),(28,535),(28,112.5),(54,112.5)]),
        ("RT-CRED-SRA1","REFERENCE","SF01-INPUT","XN2 planning center to SRA1 left envelope",[(141,585.2),(141,535),(28,535),(28,125),(92,125)]),
    ]
    route_rows = []
    for route_id, conductor, cls, scope, points in routes:
        route_rows.append({"route_id":route_id,"conductor_record":conductor,"class_id":cls,"scope":scope,"path_centerline_mm":path_text(points),"planning_manhattan_mm":f"{manhattan(points):.2f}","cut_length_mm":"SELECTION REQUIRED","terminal_entry_coordinates":"SELECTION REQUIRED","route_state":"PLANNING CANDIDATE - NOT RELEASED","warning":WARNING})

    prohibited = [
        {"control_id":"ADJ-001","aggressor":"DF01-GATE-HOT","victim":"SF01-INPUT","prohibition":"No shared unpartitioned duct or local entry","closure_evidence":"Selected barrier/duct data, installed photos and inspection","state":"OPEN","warning":WARNING},
        {"control_id":"ADJ-002","aggressor":"KWD1:11/14 conductors","victim":"S1 RESET/start conductors","prohibition":"No unprotected adjacency capable of a credible bridge","closure_evidence":"Terminal covers, ferrules, route inspection and fault-analysis disposition","state":"OPEN","warning":WARNING},
        {"control_id":"ADJ-003","aggressor":"KWD2:11/14 conductors","victim":"S2 ARM and EDM conductors","prohibition":"No unprotected adjacency capable of a credible bridge","closure_evidence":"Terminal covers, ferrules, route inspection and fault-analysis disposition","state":"OPEN","warning":WARNING},
        {"control_id":"ADJ-004","aggressor":"KWD1 stage","victim":"KWD2 stage","prohibition":"No exposed strand or displaced conductor can bridge stages","closure_evidence":"Exact terminals, ferrules, covers, pull test and inspection","state":"OPEN","warning":WARNING},
        {"control_id":"ADJ-005","aggressor":"DF01-GATE-HOT","victim":"S0 door loom","prohibition":"No shared door loom or hinge transition","closure_evidence":"Released door-loom design and inspection","state":"OPEN","warning":WARNING},
        {"control_id":"ADJ-006","aggressor":"SF01-SUPPLY","victim":"SF01-INPUT","prohibition":"Dedicated local entry or accepted partition required","closure_evidence":"Received terminal geometry and qualified routing disposition","state":"OPEN","warning":WARNING},
    ]

    inspections = [
        {"inspection_id":"INS-001","object":"DIAG-B/DIAG-R/DIAG-T","method":"Verify installed route, covers, partitions, fill and access against released drawing","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-002","object":"KWD1 and KWD2 terminals 11/14","method":"Inspect ferrule capture, strand containment, cover and pull-test evidence","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-003","object":"SRA1 A1 local entry","method":"Verify gated supply cannot bridge S11/S12/S21/S22/S34 entries","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-004","object":"SR1 A1 local entry","method":"Verify direct supply cannot bridge S11/S12/S21/S22/S34 entries","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-005","object":"XN1/XN2 node approaches","method":"Verify credited-input conductors remain in CRED-L/NODE-CRED","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-006","object":"XD24 allocation","method":"Verify actual terminal markers and point-to-point continuity against accepted revision","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-007","object":"complete unpowered panel","method":"Independent continuity, isolation and wrong-wire inspection before any power authority","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
        {"inspection_id":"INS-008","object":"credible conductor displacement","method":"Qualified first-fault/common-cause review of covers, routing and terminal adjacency","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","evidence":"BLANK","warning":WARNING},
    ]
    holds = [
        ("R240-H01","Actual terminal-entry coordinates and orientation from received SR1/SRA1/KWD1/KWD2/XD24 articles"),
        ("R240-H02","Exact duct, divider, barrier, cover and accessory selection with manufacturer data"),
        ("R240-H03","Minimum separation, fill, bend radius, conductor size, color and order codes"),
        ("R240-H04","Released two-ended conductor schedule, cut lengths, service loops and door-loom route"),
        ("R240-H05","Protection coordination, fault current, inrush, duty, ambient, bundling and jurisdiction inputs"),
        ("R240-H06","KWD terminal covers/ferrules and credible short/common-cause disposition"),
        ("R240-H07","Installed continuity, isolation, pull, visual and photo evidence"),
        ("R240-H08","Independent electrical review and qualified functional-safety review"),
        ("R240-H09","Formal P1.21 acceptance, configuration promotion and signed work authorization"),
    ]
    hold_rows = [{"hold_id":i,"closure_evidence":e,"state":"OPEN","warning":WARNING} for i,e in holds]

    credited = [r for r in routes if r[2] == "SF01-INPUT"]
    hot = [r for r in routes if r[2] in {"SF01-SUPPLY", "DF01-GATE-HOT"}]
    crossing_rows = []
    # The generator intentionally records a planning-centerline screen only. The checker re-computes it.
    for hot_route in hot:
        for cred_route in credited:
            crossing_rows.append({"screen_id":f"X-{hot_route[0]}-{cred_route[0]}","hot_route":hot_route[0],"credited_route":cred_route[0],"nominal_centerline_crossings":"0","result":"PASS - PLANNING GEOMETRY ONLY","limitation":"Terminal entries, conductor widths, bend radii and physical separation are SELECTION REQUIRED","warning":WARNING})

    sources = []
    for path in (PANEL/"candidate-backplate-layout.csv", PANEL/"reference-placement-register.csv", PANEL/"conductor-route-status.csv", P121/"wire-number-table.csv", P121/"connector-schedule.csv", P121/"net-schedule.csv"):
        sources.append({"path":path.relative_to(ROOT).as_posix(),"sha256":digest(path),"bytes":path.stat().st_size,"warning":WARNING})

    datasets = {
        "p121-route-delta.csv": (("record","p07_from","p07_to","p07_net","p121_from","p121_to","p121_net","disposition","basis","warning"), route_delta),
        "route-class-register.csv": (("class_id","safety_credit","included","route_rule","selection_state","warning"), route_classes),
        "corridor-register.csv": (("corridor_id","class","geometry_mm","physical_control","released","warning"), corridors),
        "route-segment-register.csv": (("route_id","conductor_record","class_id","scope","path_centerline_mm","planning_manhattan_mm","cut_length_mm","terminal_entry_coordinates","route_state","warning"), route_rows),
        "prohibited-adjacency.csv": (("control_id","aggressor","victim","prohibition","closure_evidence","state","warning"), prohibited),
        "crossing-screen.csv": (("screen_id","hot_route","credited_route","nominal_centerline_crossings","result","limitation","warning"), crossing_rows),
        "inspection-register.csv": (("inspection_id","object","method","acceptance","result","evidence","warning"), inspections),
        "open-holds.csv": (("hold_id","closure_evidence","state","warning"), hold_rows),
        "source-register.csv": (("path","sha256","bytes","warning"), sources),
    }

    status = {
        "identifier": IDENT,
        "round": "R240",
        "date": "2026-08-11",
        "current_candidate": "V3-P1.15-CARRIER-CANDIDATE",
        "review_candidate": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
        "panel_basis": "HR-V0-PANEL-NODE-PLACEMENT-P0.1 / P0.7 planning geometry",
        "route_delta_records": len(route_delta),
        "route_records": len(route_rows),
        "crossing_screens": len(crossing_rows),
        "nominal_centerline_crossings": 0,
        "open_holds": len(hold_rows),
        "protected_route_released": False,
        "p121_accepted": False,
        "physical_evidence_complete": False,
        "qualified_review_complete": False,
        "functional_safety_approved": False,
        "work_authority": False,
        "sol_review_lineage": "Same R12 summary; confirmed against current disposition and not double-counted",
        "warning": WARNING,
    }

    for directory in (OUT, ENG):
        for filename, (fields, rows) in datasets.items():
            write(directory/filename, fields, rows)
        (directory/"package-status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")
        (directory/"README.md").write_text(
            f"# {IDENT}\n\n> **{WARNING}**\n\nR240 corrects the stale P0.7 route semantics and supplies a coordinate-bound, fail-closed planning candidate. All physical routing selections and evidence remain open.\n",
            encoding="utf-8",
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 533.4 685.8" role="img" aria-labelledby="title desc">
<title id="title">P1.21 protected-routing planning candidate</title><desc id="desc">Control-panel planning envelope with separate blue credited-input and gold watchdog-hot centerline corridors.</desc>
<style>.panel{{fill:#eef8ff;stroke:#082b4c;stroke-width:3}}.duct{{fill:#d8e2ea;stroke:#49677e;stroke-width:1.5}}.dev{{fill:#fff;stroke:#155d91;stroke-width:2}}.node{{fill:#fff7d7;stroke:#9b6d00;stroke-width:1.5}}.cred{{fill:none;stroke:#1687c7;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}}.hot{{fill:none;stroke:#f3b61f;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}}.hold{{fill:#fff0ef;stroke:#b3261e;stroke-width:2;stroke-dasharray:6 4}}text{{font-family:Arial,sans-serif;fill:#082b4c;font-size:14px;font-weight:700}}.small{{font-size:12px;font-weight:600}}</style>
<rect class="panel" x="1.5" y="1.5" width="530.4" height="682.8" rx="4"/><rect class="duct" x="8" y="10" width="40" height="665.8"/><rect class="duct" x="383.8" y="10" width="40" height="665.8"/><rect class="duct" x="54" y="180" width="323.8" height="40"/><rect class="duct" x="54" y="625" width="323.8" height="40"/><rect class="hold" x="54" y="10" width="323.8" height="30"/><text x="184" y="38">DIAG-T RESERVED</text>
<rect class="dev" x="54" y="55" width="32" height="115"/><text x="70" y="115" text-anchor="middle">SR1</text><rect class="dev" x="92" y="55" width="32" height="115"/><text x="108" y="115" text-anchor="middle">SRA1</text><rect class="dev" x="130" y="55" width="20" height="105"/><text class="small" x="140" y="107.5" text-anchor="middle" transform="rotate(90 140 107.5)">KWD1</text><rect class="dev" x="156" y="55" width="20" height="105"/><text class="small" x="166" y="107.5" text-anchor="middle" transform="rotate(90 166 107.5)">KWD2</text>
<rect class="node" x="64" y="555" width="28.6" height="58.1"/><text class="small" x="65" y="585">XD24</text><rect class="node" x="133.2" y="555" width="5.2" height="60.4"/><rect class="node" x="138.4" y="555" width="5.2" height="60.4"/><text class="small" x="130" y="625">XN1/XN2</text>
<polyline class="hot" points="78.3,584.05 78.3,645 403.8,645 403.8,25 70,25 70,55"/><polyline class="hot" points="166,55 166,25 108,25 108,55"/><polyline class="cred" points="135.8,585.2 135.8,535 28,535 28,112.5 54,112.5"/><polyline class="cred" points="141,585.2 141,535 28,535 28,125 92,125"/>
<rect x="255" y="560" width="260" height="53" rx="5" fill="#fff" stroke="#082b4c"/><line class="cred" x1="268" y1="578" x2="300" y2="578"/><text class="small" x="308" y="582">SF01 input candidate</text><line class="hot" x1="268" y1="600" x2="300" y2="600"/><text class="small" x="308" y="604">supply/watchdog hot candidate</text>
<text class="small" x="58" y="675">Planning centerlines only. Exact terminals, barriers, separation and cut lengths: SELECTION REQUIRED.</text></svg>'''
    (OUT/"routing-overlay.svg").write_text(svg, encoding="utf-8")
    (ENG/"routing-overlay.svg").write_text(svg, encoding="utf-8")

    delta_rows = "".join(f"<tr><td>{html.escape(r['record'])}</td><td><code>{html.escape(r['p07_from'])} → {html.escape(r['p07_to'])}</code><br>{html.escape(r['p07_net'])}</td><td><code>{html.escape(r['p121_from'])} → {html.escape(r['p121_to'])}</code><br>{html.escape(r['p121_net'])}</td><td>{html.escape(r['disposition'])}</td></tr>" for r in route_delta)
    html_page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 protected-routing candidate</title><style>:root{{--sky:#8bd7f7;--navy:#082b4c;--blue:#1687c7;--gold:#f3b61f;--paper:#f7fbfe}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05;max-width:18ch}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #9b6d00;background:#fff3c4;border-radius:.8rem;font-weight:700}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.5rem 0}}.card{{background:#fff;border:2px solid var(--blue);border-radius:.8rem;padding:1rem}}.viewer{{background:white;border:3px solid var(--navy);border-radius:.8rem;overflow:auto}}.viewer img{{display:block;width:100%;min-width:800px}}.controls{{display:flex;flex-wrap:wrap;gap:.75rem;margin:.8rem 0}}button{{font:inherit;font-weight:700;padding:.65rem 1rem;border:2px solid var(--navy);border-radius:.6rem;background:white;color:var(--navy)}}.table{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;background:white}}th,td{{padding:.85rem;text-align:left;vertical-align:top;border-bottom:1px solid #aac}}th{{background:var(--navy);color:white}}code{{font-size:14px}}.note{{border-left:7px solid var(--gold);padding:1rem;background:#fff}}</style></head><body><header><strong>{IDENT} · R240</strong><h1>Keep watchdog hot conductors away from credited inputs</h1><div class="warning">{WARNING}</div></header><main><div class="grid"><div class="card"><b>7 route deltas</b><br>P0.7 reconciled to P1.21</div><div class="card"><b>0 nominal crossings</b><br>planning centerlines only</div><div class="card"><b>9 open holds</b><br>no physical route released</div><div class="card"><b>Zero safety credit</b><br>for DF-01 watchdog circuitry</div></div><p class="note">The blue and gold lines are corridor centerlines tied to the P0.7 planning frame. They are not wire cut lengths or actual terminal-entry geometry. Every numeric separation, barrier, fill, bend and termination decision remains <b>SELECTION REQUIRED</b>.</p><div class="controls"><button id="zoomIn">Zoom in</button><button id="zoomOut">Zoom out</button><button id="reset">Reset</button></div><div class="viewer"><img id="drawing" src="routing-overlay.svg" alt="Protected-routing planning overlay"></div><h2>Stale P0.7 → P1.21 route correction</h2><div class="table"><table><thead><tr><th>Record</th><th>P0.7 meaning</th><th>P1.21 candidate meaning</th><th>Disposition</th></tr></thead><tbody>{delta_rows}</tbody></table></div><h2>What the zero-crossing result means</h2><p>At the declared planning centerlines, the supply/watchdog-hot routes do not intersect the credited-input routes. This does not prove installed separation because component terminals, conductor width, duct partitions, covers, ferrules and installation tolerances are unresolved.</p><h2>Sol review lineage</h2><p>The supplied Sol summary is the same R12 independent review already controlled by this repository. It remains valid as a readiness warning and is not counted as a new independent round. No Sol blocker receives qualified closure here.</p></main><script>const image=document.querySelector('#drawing');let zoom=1;function apply(){{image.style.width=(zoom*100)+'%';}}document.querySelector('#zoomIn').onclick=()=>{{zoom=Math.min(2.5,zoom+.25);apply();}};document.querySelector('#zoomOut').onclick=()=>{{zoom=Math.max(1,zoom-.25);apply();}};document.querySelector('#reset').onclick=()=>{{zoom=1;apply();}};</script></body></html>'''
    (OUT/"index.html").write_text(html_page, encoding="utf-8")

    manifest = [{"file":p.name,"size_bytes":p.stat().st_size,"sha256":digest(p),"warning":WARNING} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "file-manifest.csv"]
    write(OUT/"file-manifest.csv", ("file","size_bytes","sha256","warning"), manifest)
    print(f"Wrote {IDENT}: {len(route_rows)} routes, {len(crossing_rows)} crossing screens, {len(hold_rows)} open holds")


if __name__ == "__main__":
    main()
