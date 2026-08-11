#!/usr/bin/env python3
"""Generate the R227 E2 control-only grounding/bonding boundary package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
ENG = ROOT / "electrical/grounding/hr-v0-e2-grounding-boundary-p0.1"
OUT = ROOT / "release/hr-v0/e2-grounding-boundary-p0.1"
IDENTIFIER = "HR-V0-E2-GND-BOUNDARY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
GATE_EVIDENCE = "docs/hr-v0-e2-grounding-boundary-p0.1.md; electrical/grounding/hr-v0-e2-grounding-boundary-p0.1/; release/hr-v0/e2-grounding-boundary-p0.1/; requirements/hr-v0-gate-evidence-supplement-r227.csv; tools/check_hr_v0_e2_grounding_boundary_p01.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    if not records:
        raise RuntimeError(f"empty CSV prohibited: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sync_gates() -> None:
    path = ROOT / "requirements/hr-v0-energization-gates.csv"
    records = read_csv(path)
    touched = set()
    for row in records:
        if row["gate_id"] in {"EG-001", "EG-004", "EG-016", "EG-022"}:
            pieces = [piece.strip() for piece in row["evidence_location"].split(";") if piece.strip()]
            for piece in GATE_EVIDENCE.split(";"):
                if piece.strip() not in pieces:
                    pieces.append(piece.strip())
            row["evidence_location"] = "; ".join(pieces)
            touched.add(row["gate_id"])
    if touched != {"EG-001", "EG-004", "EG-016", "EG-022"}:
        raise RuntimeError(f"gate sync incomplete: {sorted(touched)}")
    write_csv(path, records)


def source_register() -> list[dict[str, str]]:
    local = [
        ("E2GB-SRC-001", P115 / "01_external_sources.kicad_sch", "current source and intentional-no-bond topology"),
        ("E2GB-SRC-002", P115 / "10_actuator_interfaces.kicad_sch", "current frame and cable-shield placeholders"),
        ("E2GB-SRC-003", P115 / "connector-schedule.csv", "current terminal/net schedule"),
        ("E2GB-SRC-004", P115 / "net-schedule.csv", "current named-net membership"),
        ("E2GB-SRC-005", P118 / "01_external_sources.kicad_sch", "unaccepted source and intentional-no-bond topology"),
        ("E2GB-SRC-006", P118 / "10_actuator_interfaces.kicad_sch", "unaccepted frame and cable-shield placeholders"),
        ("E2GB-SRC-007", P118 / "connector-schedule.csv", "unaccepted terminal/net schedule"),
        ("E2GB-SRC-008", P118 / "net-schedule.csv", "unaccepted named-net membership"),
        ("E2GB-SRC-009", ROOT / "docs/hr-v0-grounding-bonding-closure-p0.1.md", "R118 system grounding/bonding interpretation"),
        ("E2GB-SRC-010", ROOT / "electrical/e2/hr-v0-e2-hardware-p0.4/e2-configuration-slice.csv", "current E2 hardware inclusion/exclusion rules"),
        ("E2GB-SRC-011", ROOT / "docs/hr-v0-e2-control-only-energization-p0.1.md", "controlled E2 commissioning boundary"),
        ("E2GB-SRC-012", ROOT / "docs/hr-v0-boston-site-jurisdiction-p0.2.md", "Boston jurisdiction and premises hold basis"),
    ]
    records = [{
        "source_id": sid,
        "source": path.relative_to(ROOT).as_posix(),
        "revision_or_date": "repository source rechecked 2026-08-11",
        "sha256": digest(path),
        "verified_use": use,
        "boundary": "configuration evidence only; received/installed/qualified evidence remains open",
        "warning": WARNING,
    } for sid, path, use in local]
    remote = [
        ("E2GB-SRC-013", "https://www.globtek.com/_0/WR9QI1660YL4NKITR6B/o", "live exact-model record rechecked 2026-08-11", "24 V, 1.66 A, 40 W; Q-series input; YL4/C40337 output; pin 1 +V, pin 3 -V/shield; Double Insulation", "catalog record does not prove the received unit, blade retention, installation or final-machine compliance"),
        ("E2GB-SRC-014", "https://spec.globtek.info/spec/pdf/WR9QI1660YL4NKITR6B", "exact specification Rev B; rechecked 2026-08-11", "exact output-cord and Class II/floating source basis retained from R118", "received continuity, polarity, cord identity and application remain open"),
        ("E2GB-SRC-015", "https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf", "published October 2023; portal updated 2025-10-06; rechecked 2026-08-11", "US/Canada Type A plug and 5.1 V/5 A USB-C family record", "brief does not establish USB-shell/DC-return continuity or the exact received SKU"),
        ("E2GB-SRC-016", "https://pip-assets.raspberrypi.com/categories/900-approvals/documents/RP-005063-CF-1-rpi-27W-PSU%20Authorisation%20of%20UL%20mark%20US%20Variant.pdf", "UL authorization dated 2023-09-20; rechecked 2026-08-11", "US model investigated to UL/CUL 62368-1 Ed.3", "authorization letter does not prove the received mark, condition, installation or shell relationship"),
        ("E2GB-SRC-017", "https://pip-assets.raspberrypi.com/categories/900-approvals/documents/RP-005066-CF-1-rpi-27W-PSU%20IEC%20CB%20Scheme%20Grant.pdf", "CB certificate DK-145484-UL dated 2023-09-20; rechecked 2026-08-11", "all plug variants including US evaluated to IEC 62368-1:2018 with national differences", "certificate does not release a Project Button installation"),
        ("E2GB-SRC-018", "https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF", "GST280A-SPEC 2026-04-03; rechecked 2026-08-11", "C14 Class-I actuator-source basis and manufacturer-internal -V/AC-FG relationship", "actuator source is physically absent and prohibited at E2; future actuator-domain application remains open"),
    ]
    records.extend({
        "source_id": sid,
        "source": source,
        "revision_or_date": revision,
        "sha256": "REMOTE_PRIMARY_SOURCE",
        "verified_use": use,
        "boundary": boundary,
        "warning": WARNING,
    } for sid, source, revision, use, boundary in remote)
    return records


def node_parity() -> list[dict[str, str]]:
    a = {r["net"]: r for r in read_csv(P115 / "net-schedule.csv")}
    b = {r["net"]: r for r in read_csv(P118 / "net-schedule.csv")}
    records = []
    for index, net in enumerate(("ACT_0V_PE_BONDED", "SAFETY_0V", "COMPUTE_0V", "ROBOT_FRAME", "CABLE_SHIELD_TERM"), 1):
        left, right = a[net], b[net]
        same = left["connections"] == right["connections"]
        interpretation = "IDENTICAL" if same else "P1.18 ADDS XD0 LINE PLUS 01..07 DISTRIBUTION TERMINALS"
        if net != "SAFETY_0V" and not same:
            raise RuntimeError(f"unexpected P1.15/P1.18 grounding-node delta: {net}")
        if net == "SAFETY_0V" and (left["connection_count"], right["connection_count"]) != ("41", "49"):
            raise RuntimeError("unexpected SAFETY_0V count delta")
        records.append({
            "node_id": f"E2GB-N-{index:03d}", "net": net,
            "p115_connections": left["connection_count"], "p118_connections": right["connection_count"],
            "comparison": interpretation,
            "e2_interpretation": {
                "ACT_0V_PE_BONDED": "OUTSIDE ENERGIZED E2 BOUNDARY; PSA1/JA1 AND ALL ACTUATOR POWER CONNECTIONS ABSENT",
                "SAFETY_0V": "ENERGIZED ELV RETURN; NO PROJECT-DEFINED PE/FRAME BOND",
                "COMPUTE_0V": "ENERGIZED ELV RETURN; NO PROJECT-DEFINED PE/FRAME BOND; USB-SHELL CONTINUITY OPEN",
                "ROBOT_FRAME": "ONE-TERMINAL PLACEHOLDER; JFRAME1 DNP FOR E2",
                "CABLE_SHIELD_TERM": "ONE-TERMINAL PLACEHOLDER; JFRAME1 DNP FOR E2",
            }[net],
            "warning": WARNING,
        })
    return records


def endpoint_parity() -> list[dict[str, str]]:
    refs = {"PSA1", "PSU2", "J24", "PSU3", "SP1", "JFRAME1"}
    a = [r for r in read_csv(P115 / "connector-schedule.csv") if r["reference"] in refs]
    b = [r for r in read_csv(P118 / "connector-schedule.csv") if r["reference"] in refs]
    if a != b:
        raise RuntimeError("P1.15/P1.18 E2 grounding endpoint rows differ")
    return [{
        "endpoint_id": f"E2GB-P-{i:03d}", "sheet": r["sheet"], "reference": r["reference"],
        "terminal": r["terminal"], "pin_name": r["pin_name"], "net": r["net"],
        "p115_state": "EXACT", "p118_state": "EXACT", "comparison": "IDENTICAL",
        "warning": WARNING,
    } for i, r in enumerate(a, 1)]


def boundary_register() -> list[dict[str, str]]:
    rows = [
        ("E2GB-B-001", "PSU2 factory adapter", "EXTERNAL TO PROJECT ENCLOSURE", "FACTORY AC L/N only", "MAY BE ENERGIZED ONLY IN AN AUTHORIZED E2 RUN", "Double-insulated/Class-II exact-model candidate; no project PE conductor enters through J24", "received unit, Q-NA blade, marks, condition and premises acceptance"),
        ("E2GB-B-002", "J24 control-power inlet", "PROJECT ELV BOUNDARY", "SAFETY_24V_RAW / SAFETY_0V", "E2 ENERGIZED DOMAIN", "pins 1 and 3 only; pins 2 and 4 intentionally not connected", "received fit, polarity, retention, protection and load evidence"),
        ("E2GB-B-003", "PSU3 factory adapter", "EXTERNAL TO PROJECT ENCLOSURE", "factory Type-A AC to USB-C", "MAY BE ENERGIZED ONLY IN AN AUTHORIZED E2 RUN", "US family is UL/CUL 62368-1 investigated; no project mains or PE conductor enters through USB-C", "exact SKU, received marks/condition, retention and premises acceptance"),
        ("E2GB-B-004", "PI1 compute input", "PROJECT ELV BOUNDARY", "COMPUTE_5V / COMPUTE_0V", "E2 ENERGIZED DOMAIN", "no intentional project bond to SAFETY_0V, frame or PE", "USB shell/DC-return continuity survey and installed isolation evidence"),
        ("E2GB-B-005", "PSA1/JA1 actuator source", "OUTSIDE E2", "FACTORY AC plus ACT_12V_RAW / ACT_0V_PE_BONDED", "PHYSICALLY ABSENT; AC AND DC DISCONNECTED", "Mean Well internal -V/FG relationship cannot enter E2", "absence inspection, capped/labelled interfaces and zero-voltage witness"),
        ("E2GB-B-006", "actuator power network", "OUTSIDE E2", "all ACT_12V* and actuator-power plugs", "DISCONNECTED AND ZERO VOLTS", "no actuator may receive power during E2", "point-to-point absence/isolation and zero-voltage records"),
        ("E2GB-B-007", "SP1", "PROJECT INTENTIONAL BOND PLACEHOLDER", "two isolated intentionally-unconnected nets", "DNP / PROHIBITED", "no project-added actuator 0V-to-PE star", "accepted ECAD/BOM/DNP inspection"),
        ("E2GB-B-008", "JFRAME1", "FRAME/SHIELD PLACEHOLDER", "ROBOT_FRAME / CABLE_SHIELD_TERM", "DNP FOR E2", "no inferred frame, shield, return or PE link", "physical survey and later qualified bonding/EMC disposition"),
        ("E2GB-B-009", "panel metalwork", "ELV-ONLY E2 ENCLOSURE", "backplate, DIN rail, duct and exposed hardware", "NO SAFETY CREDIT; NO INTENTIONAL BOND DEFINED", "model assumes no mains conductor/source inside and actuator source absent", "material inventory, accidental-continuity survey, insulation/fault review and qualified acceptance"),
        ("E2GB-B-010", "factory adapters and cords", "OUTSIDE PROJECT ENCLOSURE", "unmodified manufacturer assemblies", "NO INTERNAL MAINS WORK", "adapters are not enclosed, opened, rewired or panel-mounted", "exact placement, strain relief, trip/ingress protection and site review"),
    ]
    return [{"boundary_id": i, "item": item, "location": location, "conductors_or_nets": nets, "e2_state": state, "controlled_rule": rule, "closure_evidence": evidence, "warning": WARNING} for i, item, location, nets, state, rule, evidence in rows]


def inspection_register() -> list[dict[str, str]]:
    rows = [
        ("E2GB-I-001", "verify exact PSU2 model, Q-NA blade, safety marks and intact case", "visual/receiving record", "exact identity and acceptable condition", "UNEXECUTED"),
        ("E2GB-I-002", "verify J24/PSU2 cord fit, pin identity and polarity", "de-energized continuity/polarity method approved by reviewer", "pins 1/3 exact; 2/4 open", "UNEXECUTED"),
        ("E2GB-I-003", "verify exact PSU3 US SKU, marks and intact case/cable", "visual/receiving record", "exact identity and acceptable condition", "UNEXECUTED"),
        ("E2GB-I-004", "verify PSA1 and actuator AC cord physically absent", "independent visual inspection", "absent; interfaces capped and labelled", "UNEXECUTED"),
        ("E2GB-I-005", "verify JA1 and every actuator-power plug disconnected", "point-to-point inspection", "all disconnected and protected", "UNEXECUTED"),
        ("E2GB-I-006", "verify SP1 not populated", "ECAD/BOM/physical inspection", "DNP with no conductive bridge", "UNEXECUTED"),
        ("E2GB-I-007", "verify JFRAME1 not populated for E2", "ECAD/BOM/physical inspection", "DNP with no frame/shield link", "UNEXECUTED"),
        ("E2GB-I-008", "survey SAFETY_0V to COMPUTE_0V", "reviewer-approved de-energized resistance/continuity method", "numeric limit SELECTION REQUIRED", "UNEXECUTED"),
        ("E2GB-I-009", "survey each ELV return to panel metalwork/frame/shields", "reviewer-approved de-energized resistance/continuity method", "numeric limit SELECTION REQUIRED", "UNEXECUTED"),
        ("E2GB-I-010", "survey USB shells to COMPUTE_0V and metalwork", "four-wire/continuity method as accepted", "relationship recorded; no assumption", "UNEXECUTED"),
        ("E2GB-I-011", "confirm no mains conductor or adapter is inside enclosure", "independent visual inspection", "none present", "UNEXECUTED"),
        ("E2GB-I-012", "confirm actuator rails remain at zero throughout E2", "independent meter channels with pre/post checks", "numeric tolerance and instrument SELECTION REQUIRED", "UNEXECUTED"),
        ("E2GB-I-013", "confirm premises/receptacle/branch/GFCI facts", "signed Boston site-input record", "qualified reviewer acceptance", "UNEXECUTED"),
        ("E2GB-I-014", "perform control-domain first-fault review", "qualified electrical/functional-safety review", "accepted disposition tied to exact configuration", "UNEXECUTED"),
        ("E2GB-I-015", "authorize or reject the written E2 run", "signed EG-022 authorization", "all named prerequisites accepted and unexpired", "UNEXECUTED"),
    ]
    return [{"inspection_id": i, "subject": subject, "method": method, "acceptance": acceptance, "state": state, "result": "BLANK", "evidence_uri": "BLANK", "warning": WARNING} for i, subject, method, acceptance, state in rows]


def holds() -> list[dict[str, str]]:
    rows = [
        ("E2GB-H-001", "Boston premises", "exact receptacle, branch, OCPD, GFCI, grounding, ambient and authority record"),
        ("E2GB-H-002", "received PSU2", "identity, marks, blade/cord, polarity, load/startup/brownout and condition evidence"),
        ("E2GB-H-003", "received PSU3", "exact US SKU, marks, condition, retention, target load and shell/return evidence"),
        ("E2GB-H-004", "24 V interface", "J24 fit, retention, pin continuity/polarity, protection and strain relief"),
        ("E2GB-H-005", "actuator-domain absence", "PSA1/cord/JA1/actuator-plug absence plus zero-voltage evidence"),
        ("E2GB-H-006", "DNP proof", "SP1 and JFRAME1 accepted ECAD/BOM/physical inspection"),
        ("E2GB-H-007", "metalwork inventory", "exact backplate/rail/duct/enclosure/guard/frame materials and exposed conductive parts"),
        ("E2GB-H-008", "continuity/insulation method", "qualified numeric limits, instruments, uncertainty and exact test points"),
        ("E2GB-H-009", "USB shell relationship", "received installed continuity/isolation survey"),
        ("E2GB-H-010", "control-domain first fault", "accepted shock/fire/fault-clearing/noninterference analysis for the exact E2 boundary"),
        ("E2GB-H-011", "configuration acceptance", "P1.18 acceptance or exact accepted P1.15 implementation plus synchronized build records"),
        ("E2GB-H-012", "qualified E2 authorization", "signed, competent, independent, configuration-specific EG-022 disposition"),
    ]
    return [{"hold_id": i, "subject": subject, "state": "OPEN", "closure_evidence": evidence, "accepted": "FALSE", "warning": WARNING} for i, subject, evidence in rows]


def guide(nodes: list[dict[str, str]], boundary: list[dict[str, str]], inspections: list[dict[str, str]]) -> str:
    cards = "".join(f"<article data-state='{html.escape(r['e2_state'])}'><strong>{html.escape(r['item'])}</strong><span>{html.escape(r['e2_state'])}</span><code>{html.escape(r['conductors_or_nets'])}</code><p>{html.escape(r['controlled_rule'])}</p></article>" for r in boundary)
    node_rows = "".join(f"<tr><td>{html.escape(r['net'])}</td><td>{r['p115_connections']}</td><td>{r['p118_connections']}</td><td>{html.escape(r['comparison'])}</td><td>{html.escape(r['e2_interpretation'])}</td></tr>" for r in nodes)
    inspect_rows = "".join(f"<tr><td>{html.escape(r['inspection_id'])}</td><td>{html.escape(r['subject'])}</td><td>{html.escape(r['acceptance'])}</td><td>{html.escape(r['state'])}</td></tr>" for r in inspections)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 E2 grounding boundary</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8;--hold:#fff2bd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(26px,3vw,40px)}}.warning{{background:var(--hold);color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}article{{background:white;border:2px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:8px}}article strong{{font-size:18px}}article span{{font-size:14px;font-weight:850;background:var(--sky);padding:5px 8px;border-radius:6px}}code{{font-size:14px;overflow-wrap:anywhere}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white;margin:12px 0 28px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9c;font-weight:750}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} | R227</p><h1>Only the control and compute ELV domains may enter E2.</h1><p>The actuator source, actuator rails, project-added 0 V/PE star, and frame/shield link remain physically absent or DNP.</p></header><main><div class="verdict"><strong>Controlled boundary:</strong> external unmodified factory adapters remain outside the project enclosure. J24 and USB-C carry ELV into the E2 enclosure. This is a design boundary, not an authorization to plug in.</div><h2>Ten controlled boundary items</h2><div class="grid">{cards}</div><h2>Native ECAD node reconciliation</h2><div class="tablewrap"><table><thead><tr><th>Net</th><th>P1.15</th><th>P1.18</th><th>Comparison</th><th>E2 meaning</th></tr></thead><tbody>{node_rows}</tbody></table></div><h2>Unexecuted evidence route</h2><div class="tablewrap"><table><thead><tr><th>ID</th><th>Inspection/test</th><th>Acceptance</th><th>State</th></tr></thead><tbody>{inspect_rows}</tbody></table></div><div class="warning">EG-001, EG-004, EG-016 and EG-022 remain PARTIAL. Numeric continuity/insulation limits, the premises record, received hardware, physical evidence and qualified authorization remain open.</div><p><a href="boundary-register.csv">boundary register</a> | <a href="node-parity-register.csv">node parity</a> | <a href="endpoint-parity-register.csv">endpoint parity</a> | <a href="inspection-register.csv">inspection route</a> | <a href="open-holds.csv">12 holds</a> | <a href="source-register.csv">sources</a></p></main></body></html>'''


def main() -> None:
    sync_gates()
    nodes = node_parity()
    endpoints = endpoint_parity()
    boundary = boundary_register()
    inspections = inspection_register()
    hold_rows = holds()
    sources = source_register()
    authority = [
        {"activity": "read-only engineering/configuration review", "permitted": "TRUE", "boundary": "repository and current primary-source evidence only", "warning": WARNING},
        {"activity": "procurement/fabrication/assembly/connection/testing", "permitted": "FALSE", "boundary": "received, physical and qualified evidence remains open", "warning": WARNING},
        {"activity": "plugging in either E2 adapter", "permitted": "FALSE", "boundary": "requires complete EG-021 evidence and signed EG-022 authorization", "warning": WARNING},
        {"activity": "actuator power/motion/energization", "permitted": "FALSE", "boundary": "PSA1 and actuator network are prohibited and physically absent at E2", "warning": WARNING},
    ]
    status = {
        "identifier": IDENTIFIER, "round": "R227", "date": "2026-08-11",
        "current_electrical": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "unaccepted_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "endpoint_rows_identical": len(endpoints), "node_rows": len(nodes),
        "intentional_p118_delta": "SAFETY_0V 41 to 49 connections through XD0 LINE plus 01..07",
        "boundary_items": len(boundary), "unexecuted_inspections": len(inspections), "open_holds": len(hold_rows),
        "eg_001_status": "partial", "eg_004_status": "partial", "eg_016_status": "partial", "eg_022_status": "partial",
        "p118_accepted": False, "physical_tests_executed": False, "qualified_review_received": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "warning": WARNING,
    }
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory / "node-parity-register.csv", nodes)
        write_csv(directory / "endpoint-parity-register.csv", endpoints)
        write_csv(directory / "boundary-register.csv", boundary)
        write_csv(directory / "inspection-register.csv", inspections)
        write_csv(directory / "open-holds.csv", hold_rows)
        write_csv(directory / "source-register.csv", sources)
        write_csv(directory / "authority-boundary.csv", authority)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR227 freezes the E2 control-only grounding/bonding boundary against current P1.15 and unaccepted P1.18. It does not authorize plugging in, powered testing, actuator power or motion. Twelve holds remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(nodes, boundary, inspections), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENTIFIER}: {len(endpoints)} endpoint rows; 5 nodes; 10 boundary items; 15 unexecuted inspections; 12 holds")


if __name__ == "__main__":
    main()
