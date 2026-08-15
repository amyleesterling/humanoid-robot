#!/usr/bin/env python3
"""Generate R225 source-bound proof of the current P1.18 watchdog permit topology."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
NATIVE = ECAD / "03_arm_watchdog_eligibility.kicad_sch"
NETLIST = ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate.net"
WIRES = ECAD / "wire-number-table.csv"
ERC = ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate-erc.rpt"
SRS = ROOT / "docs/hr-v0-safety-requirements-p0.2.md"
ENG = ROOT / "electrical/reviews/hr-v0-watchdog-permit-topology-p0.1"
OUT = ROOT / "release/hr-v0/watchdog-permit-topology-p0.1"
IDENTIFIER = "HR-V0-WD-PERMIT-TOPOLOGY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    if not records:
        raise RuntimeError(f"empty CSV prohibited: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def source_register() -> list[dict[str, str]]:
    return [
        {"source_id": "WPT-SRC-001", "source": NATIVE.relative_to(ROOT).as_posix(), "sha256": digest(NATIVE), "revision_or_date": "V3-P1.18; generated 2026-08-11", "verified_use": "native symbols, terminal names, descriptions and net labels", "boundary": "unaccepted topology candidate; source identity does not establish safety performance", "warning": WARNING},
        {"source_id": "WPT-SRC-002", "source": NETLIST.relative_to(ROOT).as_posix(), "sha256": digest(NETLIST), "revision_or_date": "KiCad 10.0.5 netlist; generated 2026-08-11", "verified_use": "machine-readable endpoint membership for the permit and E-stop nets", "boundary": "connectivity only; no contact mechanics, timing, duty or physical fault exclusion", "warning": WARNING},
        {"source_id": "WPT-SRC-003", "source": WIRES.relative_to(ROOT).as_posix(), "sha256": digest(WIRES), "revision_or_date": "V3-P1.18; generated 2026-08-11", "verified_use": "wire-number parity for KWD1/KWD2 and SR1 endpoints", "boundary": "not a released conductor or installation schedule", "warning": WARNING},
        {"source_id": "WPT-SRC-004", "source": ERC.relative_to(ROOT).as_posix(), "sha256": digest(ERC), "revision_or_date": "KiCad 10.0.5; 2026-08-11", "verified_use": "recorded ERC 0 errors and 0 warnings", "boundary": "ERC does not prove functional safety, ratings or physical correctness", "warning": WARNING},
        {"source_id": "WPT-SRC-005", "source": SRS.relative_to(ROOT).as_posix(), "sha256": digest(SRS), "revision_or_date": "HR-V0-SRS-P0.2 / R218 / 2026-08-11", "verified_use": "DF-01 zero-credit boundary and open allocation/validation state", "boundary": "candidate requirements only; no PLr/SIL selection or validation", "warning": WARNING},
        {"source_id": "WPT-SRC-006", "source": "https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060", "sha256": "NOT_APPLICABLE_REMOTE_PRIMARY_SOURCE", "revision_or_date": "official product data maintenance 2026-04-01; project recheck 2026-08-11", "verified_use": "item 2967060 has two changeover contacts with terminals 11/12/14 and 21/22/24; 24 V DC coil", "boundary": "ordinary relay; no force-guided or safety-function credit inferred; received identity and application remain open", "warning": WARNING},
    ]


def topology_register() -> list[dict[str, str]]:
    return [
        {"path_id": "WPT-PATH-001", "function": "watchdog supply gate stage 1", "net": "SAFETY_24V", "from_endpoint": "protected 24 V distribution", "through_contact": "KWD1:11-14 NO", "to_net_or_endpoint": "WD_SUPPLY_INTERMEDIATE", "source_proof": "netlist + sheet 03 + W3016/W3018", "result": "SOURCE CONNECTED", "safety_credit": "ZERO", "warning": WARNING},
        {"path_id": "WPT-PATH-002", "function": "watchdog supply gate stage 2", "net": "WD_SUPPLY_INTERMEDIATE", "from_endpoint": "KWD1:14", "through_contact": "KWD2:11-14 NO", "to_net_or_endpoint": "SR1_A1_WD_GATED -> SR1:A1", "source_proof": "netlist + sheet 03 + W3022/W3024/W2005", "result": "SOURCE CONNECTED IN SERIES", "safety_credit": "ZERO", "warning": WARNING},
        {"path_id": "WPT-PATH-003", "function": "E-stop channel 1", "net": "SR1_S11 / SR1_S12", "from_endpoint": "SR1:S11", "through_contact": "S0:R-1/R-2 NC", "to_net_or_endpoint": "SR1:S12", "source_proof": "netlist + sheet 02", "result": "NO KWD ENDPOINT IN INPUT LOOP", "safety_credit": "CANDIDATE SF-01; QUALIFIED ALLOCATION OPEN", "warning": WARNING},
        {"path_id": "WPT-PATH-004", "function": "E-stop channel 2", "net": "SR1_S21 / SR1_S22", "from_endpoint": "SR1:S21", "through_contact": "S0:L-1/L-2 NC", "to_net_or_endpoint": "SR1:S22", "source_proof": "netlist + sheet 02", "result": "NO KWD ENDPOINT IN INPUT LOOP", "safety_credit": "CANDIDATE SF-01; QUALIFIED ALLOCATION OPEN", "warning": WARNING},
    ]


def truth_table() -> list[dict[str, str]]:
    cases = [
        ("WPT-F-001", "heartbeat absent; no weld", 0, 0, 0, 0),
        ("WPT-F-002", "KWD1 commanded only", 1, 0, 0, 0),
        ("WPT-F-003", "KWD2 commanded only", 0, 1, 0, 0),
        ("WPT-F-004", "both stages commanded", 1, 1, 0, 0),
        ("WPT-F-005", "KWD1 contact welded; heartbeat absent", 0, 0, 1, 0),
        ("WPT-F-006", "KWD2 contact welded; heartbeat absent", 0, 0, 0, 1),
        ("WPT-F-007", "KWD1 welded; KWD2 commanded", 0, 1, 1, 0),
        ("WPT-F-008", "KWD2 welded; KWD1 commanded", 1, 0, 0, 1),
        ("WPT-F-009", "both contacts welded or bypassed", 0, 0, 1, 1),
    ]
    records = []
    for case_id, condition, c1, c2, w1, w2 in cases:
        e1, e2 = int(bool(c1 or w1)), int(bool(c2 or w2))
        permit = int(bool(e1 and e2))
        records.append({
            "case_id": case_id, "condition": condition,
            "kwd1_commanded": str(c1), "kwd2_commanded": str(c2),
            "kwd1_welded_or_bypassed": str(w1), "kwd2_welded_or_bypassed": str(w2),
            "kwd1_effective_closed": str(e1), "kwd2_effective_closed": str(e2),
            "sr1_a1_supply_permitted": str(permit),
            "interpretation": "single weld cannot preserve permit when the other stage opens" if w1 + w2 == 1 and c1 == c2 == 0 else ("permit remains possible; dual/common-cause physical fault remains open" if w1 and w2 else "series Boolean screen only"),
            "physical_validation": "NOT EXECUTED", "safety_credit": "ZERO", "warning": WARNING,
        })
    return records


def finding_register() -> list[dict[str, str]]:
    return [
        {"finding_id": "SOL-SUMMARY-WD-01", "review_claim": "single non-safety watchdog permit contact can defeat heartbeat removal under a welded-contact fault", "current_source_disposition": "TOPOLOGY ASSERTION DOES NOT MATCH CURRENT P1.18 SOURCE", "current_evidence": "KWD1:11-14 and KWD2:11-14 are series contacts from SAFETY_24V to SR1:A1; neither is in an S0 input loop", "what_is_resolved": "one welded KWD contact alone does not maintain the modeled SR1:A1 supply path when the other series stage opens", "what_remains_open": "P1.18 acceptance; common-cause/dual weld or bypass; shared controller/supply; contact duty; protected routing; physical injection; PLr/SIL allocation; qualified validation", "reviewer_closure": "NOT CLAIMED", "warning": WARNING},
    ]


def holds() -> list[dict[str, str]]:
    items = [
        ("WPT-H-001", "P1.18 design disposition", "independent sheet/netlist parity review and formal acceptance or correction"),
        ("WPT-H-002", "ordinary relay safety credit", "qualified allocation; DF-01 and both KWD stages retain zero safety credit"),
        ("WPT-H-003", "common-cause and dependent failure", "shared controller/supply/PCB/routing analysis plus accepted fault model"),
        ("WPT-H-004", "contact application and duty", "PNOZ supply inrush/steady duty, suppression, endurance and received relay application evidence"),
        ("WPT-H-005", "received identity and terminal state", "received item, polarity, terminal continuity/contact-state and substitution control"),
        ("WPT-H-006", "physical routing and bypass prevention", "released protected routing, separation, inspection and credible-short disposition"),
        ("WPT-H-007", "fault injection", "authorized current-limited no-load procedure and executed single/dual weld, bypass, open and stuck-output evidence"),
        ("WPT-H-008", "functional-safety allocation and validation", "qualified PLr/SIL/category determination, calculation, validation plan, executed evidence and signature"),
    ]
    return [{"hold_id": i, "subject": s, "state": "OPEN", "closure_evidence": e, "accepted": "FALSE", "warning": WARNING} for i, s, e in items]


def guide(paths: list[dict[str, str]], faults: list[dict[str, str]], finding: list[dict[str, str]]) -> str:
    path_rows = "".join(f"<tr><td>{html.escape(r['path_id'])}</td><td>{html.escape(r['function'])}</td><td>{html.escape(r['through_contact'])}</td><td>{html.escape(r['result'])}</td><td>{html.escape(r['safety_credit'])}</td></tr>" for r in paths)
    fault_rows = "".join(f"<tr><td>{html.escape(r['case_id'])}</td><td>{html.escape(r['condition'])}</td><td>{r['kwd1_effective_closed']}</td><td>{r['kwd2_effective_closed']}</td><td>{r['sr1_a1_supply_permitted']}</td><td>{html.escape(r['interpretation'])}</td></tr>" for r in faults)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 watchdog permit topology proof</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);background:var(--paper);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(26px,3vw,40px)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}.warning{{background:#fff2bd;color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}.flow{{display:grid;grid-template-columns:repeat(5,minmax(150px,1fr));gap:10px;align-items:center;margin:24px 0}}.box{{background:white;border:3px solid var(--blue);border-radius:12px;padding:18px;text-align:center;font-weight:800}}.arrow{{text-align:center;font-size:30px;font-weight:900}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white}}table{{border-collapse:collapse;width:100%;min-width:900px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}code{{font-size:14px}}a{{color:#075b9c;font-weight:750}}@media(max-width:850px){{.flow{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg)}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} · R225</p><h1>Two series stages. Still zero safety credit.</h1><p>Machine-checked against the current P1.18 native KiCad sheet, netlist and wire-number table.</p></header><main><div class="verdict"><strong>Current-source correction:</strong> the summarized single-contact claim does not match P1.18. A single welded KWD contact does not preserve the modeled SR1 supply path when the other contact opens. This does not validate the watchdog as a safety function.</div><section class="flow"><div class="box">SAFETY_24V</div><div class="arrow">→</div><div class="box">KWD1 11–14<br>ordinary NO</div><div class="arrow">→</div><div class="box">WD_SUPPLY_INTERMEDIATE</div><div class="arrow">→</div><div class="box">KWD2 11–14<br>ordinary NO</div><div class="arrow">→</div><div class="box">SR1:A1</div></section><h2>Source paths</h2><div class="tablewrap"><table><thead><tr><th>ID</th><th>Function</th><th>Contact</th><th>Result</th><th>Credit</th></tr></thead><tbody>{path_rows}</tbody></table></div><h2>Weld/bypass truth table</h2><p>This is a Boolean topology screen. It is not contact, timing, diagnostic, CCF or physical validation.</p><div class="tablewrap"><table><thead><tr><th>Case</th><th>Condition</th><th>KWD1 closed</th><th>KWD2 closed</th><th>SR1:A1 permit</th><th>Interpretation</th></tr></thead><tbody>{fault_rows}</tbody></table></div><h2>What remains open</h2><div class="warning">{html.escape(finding[0]['what_remains_open'])}. No reviewer closure, PLr/SIL claim, connection, test, motion or energization authority is created.</div><p><a href="topology-register.csv">Topology register</a> · <a href="fault-truth-table.csv">Fault table</a> · <a href="finding-reconciliation.csv">Finding reconciliation</a> · <a href="open-holds.csv">Eight open holds</a> · <a href="source-register.csv">Source hashes</a></p></main></body></html>'''


def main() -> None:
    path_rows = topology_register()
    fault_rows = truth_table()
    findings = finding_register()
    hold_rows = holds()
    sources = source_register()
    authority = [
        {"activity": "read-only engineering review and correction", "permitted": "TRUE", "boundary": "no physical access or work", "warning": WARNING},
        {"activity": "procurement/fabrication/assembly/wiring", "permitted": "FALSE", "boundary": "all physical selections and acceptance remain open", "warning": WARNING},
        {"activity": "connection/powered testing/fault injection", "permitted": "FALSE", "boundary": "no authorized physical procedure or qualified approval", "warning": WARNING},
        {"activity": "motion/energization", "permitted": "FALSE", "boundary": "all applicable gates remain unresolved", "warning": WARNING},
    ]
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory / "topology-register.csv", path_rows)
        write_csv(directory / "fault-truth-table.csv", fault_rows)
        write_csv(directory / "finding-reconciliation.csv", findings)
        write_csv(directory / "source-register.csv", sources)
        write_csv(directory / "open-holds.csv", hold_rows)
        write_csv(directory / "authority-boundary.csv", authority)
        status = {"identifier": IDENTIFIER, "round": "R225", "date": "2026-08-11", "bound_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "current_accepted_electrical": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "series_permit_contacts": 2, "estop_input_loops_with_kwd_endpoint": 0, "truth_table_cases": len(fault_rows), "open_holds": len(hold_rows), "reviewer_closure_claimed": False, "functional_safety_credit": False, "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "warning": WARNING}
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR225 proves the modeled two-contact series watchdog supply gate in P1.18 and the absence of KWD endpoints from both direct E-stop input loops. It assigns zero safety credit and leaves eight holds open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(path_rows, fault_rows, findings), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENTIFIER}: 2 series permit contacts / 0 KWD endpoints in E-stop loops / {len(fault_rows)} fault screens / {len(hold_rows)} holds")
    print("DF-01 and KWD1/KWD2 retain zero safety credit; no physical or energization authority")


if __name__ == "__main__":
    main()
