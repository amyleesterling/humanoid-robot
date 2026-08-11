#!/usr/bin/env python3
"""Generate R223 configuration reconciliation for explicit panel topology/placement."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configuration/hr-v0-config-reconciliation-p0.3"
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.4"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.4"
IDENTIFIER = "HR-V0-CONFIG-REC-P0.4"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(record: dict[str, str]) -> dict[str, str]:
    record["warning"] = WARNING
    return record


def build() -> dict[str, list[dict[str, str]]]:
    names = ("current-configuration-map.csv", "supersession-map.csv", "bom-integration-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv")
    data = {name: rows(SOURCE / name) for name in names}
    current_additions = [
        ("CFG-19", "control-panel current-identity overlay", "HR-V0-CP-CONFIG-P0.1", "release/hr-v0/control-panel-configuration-p0.1/package-status.json", "CURRENT PANEL IDENTITY CONTROL", "P0.6 remains planning geometry; P1.15/PCB-P1.0/DXL-STAR-P0.2 identities bound; physical evidence open"),
        ("CFG-20", "panel conductor family/gauge basis", "HR-V0-PANEL-COND-P0.1", "release/hr-v0/panel-conductor-basis-p0.1/package-status.json", "CURRENT HELD CONDUCTOR BASIS", "fixed-internal family/gauge candidate only; door cable and all exact physical conductor fields open"),
        ("CFG-21", "explicit point-to-point topology", "HR-V0-PANEL-P2P-P0.1", "release/hr-v0/panel-point-to-point-p0.1/package-status.json", "CURRENT HELD TOPOLOGY EVIDENCE", "55 two-ended conductors map 66 labels; no cut length, termination or wiring release"),
        ("CFG-22", "native panel-topology ECAD", "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate/project-button-v3-p1.18-panel-topology-candidate.kicad_pro", "UNACCEPTED SUPPORTING ECAD CANDIDATE", "P1.15 remains current until independent review and formal P1.18 disposition"),
        ("CFG-23", "panel node placement and route-anchor basis", "HR-V0-PANEL-NODE-PLACEMENT-P0.1", "release/hr-v0/panel-node-placement-p0.1/package-status.json", "CURRENT HELD PLACEMENT CANDIDATE", "five node envelopes and stock arithmetic only; zero holes, cuts, wires or physical results"),
    ]
    for record_id, role, identifier, source_path, state, boundary in current_additions:
        data["current-configuration-map.csv"].append(warned({"record_id": record_id, "role": role, "identifier": identifier, "source_path": source_path, "configuration_state": state, "release_boundary": boundary}))
    data["supersession-map.csv"].append(warned({"record_id": "SUP-11", "prior_identifier": "HR-V0-CONFIG-REC-P0.3", "current_or_required_successor": IDENTIFIER, "disposition": "P0.3 remains the R214 mechanical-integration snapshot; P0.4 adds the R220-R223 panel/BOM chain without promoting P1.18 or any work gate", "use_authorized": "NO"}))
    additions = [
        ("BOM-083", "two 500 mm DIN-rail stock candidates", "Phoenix Contact 1207648 / DR1-DR5 stock allocation", "exact_candidate_hold"),
        ("BOM-084", "one 2000 mm wire-duct stock candidate", "Phoenix Contact 3240189 / WD1-WD4 stock allocation", "exact_candidate_hold"),
        ("BOM-085", "eight rail end-bracket candidates", "Phoenix Contact 3022218", "exact_candidate_hold"),
        ("BOM-092", "XD24/XD0 distribution blocks", "Phoenix Contact 3273114 x1 / 3273112 x1", "exact_candidate_hold"),
        ("BOM-093", "XN1/XN2/XN3 junction terminals", "Phoenix Contact 3209549 x3", "exact_candidate_hold"),
        ("BOM-094", "junction group end-cover candidate", "Phoenix Contact 3030488 x1", "exact_candidate_hold"),
        ("BOM-095", "remaining node accessories", "SELECTION REQUIRED", "selection_required"),
    ]
    for item_id, role, bound, closure in additions:
        data["bom-integration-map.csv"].append(warned({"item_id": item_id, "role": role, "bound_identifier": bound, "closure_class": closure, "physical_evidence": "OPEN", "procurement_released": "NO"}))
    for row in data["gate-impact.csv"]:
        row["evidence_added"] = IDENTIFIER
        if row["gate_id"] in {"EG-002", "EG-003", "EG-004", "EG-010", "EG-014", "EG-015"}:
            row["remaining_evidence"] += "; R223 panel topology/placement independent review, received fit and physical closure"
    for gate_id, domain, remaining in [
        ("EG-018", "unpowered panel installation", "released holes/cuts/wires/terminations; received parts; as-built point-to-point, pull, torque, label, continuity, polarity and isolation evidence; signed release"),
        ("EG-020", "electrical application evidence", "fault/inrush/current/ambient/bundle/length inputs; protection coordination; temperature/fault/no-backfeed evidence; qualified acceptance"),
    ]:
        data["gate-impact.csv"].append(warned({"gate_id": gate_id, "domain": domain, "status": "partial", "evidence_added": IDENTIFIER, "remaining_evidence": remaining, "gate_closed": "NO"}))
    for number, (hold, state, evidence) in enumerate([
        ("Independent P1.18 point-to-point topology and P1.15 logic-parity disposition", "SELECTION REQUIRED", "signed review against exact native source/netlist/schedules"),
        ("Received enclosure/backplate/node/rail/duct dimensional reconciliation", "NOT EXECUTED", "received identities and accepted measurements in the controlled frame"),
        ("DR5/WD4 kerf, tolerance, cut, deburr, coating, hole, fastener and bonding release", "DESIGN REQUIRED", "qualified manufacturing/electrical disposition and released drawings"),
        ("Exact node accessories, markers, partitions/covers, rail retention and access", "SELECTION REQUIRED", "accepted complete accessory BOM and received-fit evidence"),
        ("Exact conductor entry points, routes, cut lengths, door loom and end preparations", "DESIGN REQUIRED", "released route/cut/termination schedule with calculations and samples"),
        ("Duct fill, separation, loading, protection, thermal and fault closure", "NOT EXECUTED", "accepted calculations plus calibrated physical evidence"),
        ("Installed point-to-point and qualified electrical/functional-safety acceptance", "NOT EXECUTED", "signed as-built inspection, test and review records"),
    ], start=20):
        data["open-holds.csv"].append(warned({"hold_id": f"HOLD-{number:02d}", "hold": hold, "state": state, "closure_evidence": evidence}))
    criteria = [
        "All 66 R221 endpoints map exactly once into 55 R222 two-ended conductors",
        "P1.18 adds only five topology nodes while P1.15 logic remains unchanged",
        "XD24/XD0/XN1/XN2/XN3 identities and terminal allocations match native ECAD",
        "Five node envelopes and DR5/WD4 lie inside the controlled backplate planning boundary",
        "RAIL-B and DUCT-A arithmetic retains positive pre-kerf residual without increasing stock quantity",
        "BOM-092 through BOM-095 and revised BOM-083/084/085 are fully covered and held",
        "Every cut length, terminal entry, hole, termination and physical result remains unreleased",
        "Independent qualified review and every affected gate remain open",
    ]
    for number, criterion in enumerate(criteria, start=17):
        data["acceptance-matrix.csv"].append(warned({"acceptance_id": f"ACC-{number:02d}", "criterion": criterion, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}))
    return data


def page(data: dict[str, list[dict[str, str]]]) -> str:
    cards = "".join(f'<article class="card"><span>{html.escape(row["configuration_state"])}</span><h3>{html.escape(row["identifier"])}</h3><p>{html.escape(row["release_boundary"])}</p></article>' for row in data["current-configuration-map.csv"][-5:])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 configuration P0.4</title><style>:root{{--ink:#092746;--blue:#1268a8;--sky:#dff3ff;--gold:#f5bd18;--paper:#f8fbff;--line:#82b9dd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--ink),#0d5c99);color:white;padding:28px max(20px,5vw);border-bottom:7px solid var(--gold)}}main{{max-width:1180px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(34px,5vw,60px);line-height:1.06}}h2{{font-size:clamp(26px,3vw,38px)}}h3{{font-size:21px;overflow-wrap:anywhere}}.warn{{background:#fff2bd;color:#402d00;border:3px solid var(--gold);padding:16px;font-weight:850}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px}}.card span{{font-size:14px;font-weight:850;color:var(--blue)}}.metric{{font-size:35px;font-weight:900;color:var(--blue)}}a{{color:#07599b;font-weight:700}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><header><div class="warn">{WARNING}</div><p>{IDENTIFIER} · R223</p><h1>One controlled chain from schematic node to panel place.</h1><p>P1.15 remains current. P1.18 is an unaccepted supporting candidate. The BOM now exposes every R222/R223 node and accessory dependency.</p></header><main><section class="grid"><article class="card"><div class="metric">55</div><p>Two-ended conductor candidates.</p></article><article class="card"><div class="metric">5</div><p>Explicit node candidates.</p></article><article class="card"><div class="metric">95</div><p>Covered system BOM groups.</p></article><article class="card"><div class="metric">0</div><p>Released holes, cuts, wires or powered actions.</p></article></section><h2>R223 configuration additions</h2><div class="grid">{cards}</div><h2>Machine-readable records</h2><p><a href="current-configuration-map.csv">Current map</a> · <a href="supersession-map.csv">Supersession</a> · <a href="bom-integration-map.csv">BOM integration</a> · <a href="gate-impact.csv">Gate impact</a> · <a href="open-holds.csv">Open holds</a> · <a href="acceptance-matrix.csv">Acceptance</a></p><div class="warn">All 30 energization gates remain unresolved. P1.18 is not promoted. No procurement, fabrication, assembly, connection, powered testing, motion or energization is authorized.</div></main></body></html>'''


def main() -> None:
    data = build()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, records in data.items():
            write_csv(directory / name, records)
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR223 reconciles P1.15 current identity with the unaccepted P1.18 topology, explicit P2P schedule, held node placement and 95-group covered BOM. No physical or work gate closes.\n", encoding="utf-8", newline="\n")
        status = {"identifier": IDENTIFIER, "round": "R223", "date": "2026-08-11", "current_core_electrical_identifier": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "unaccepted_panel_topology_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "system_bom_groups": 95, "current_records": 23, "supersession_records": 11, "bom_integration_records": 15, "gate_records": 11, "open_holds": 26, "acceptance_rows": 24, "all_acceptance_executed": False, "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING}
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(data), encoding="utf-8", newline="\n")
    sources = [ROOT / row["source_path"] for row in data["current-configuration-map.csv"]]
    source_rows = [warned({"source_path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "current configuration evidence"}) for path in sources]
    for directory in (ENG, OUT):
        write_csv(directory / "source-hash-register.csv", source_rows)
        files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": path.name, "bytes": str(path.stat().st_size), "sha256": digest(path)} for path in files])
    print(f"{IDENTIFIER}: 23 current records; 95 BOM groups; 26 holds; no work authority")


if __name__ == "__main__":
    main()
