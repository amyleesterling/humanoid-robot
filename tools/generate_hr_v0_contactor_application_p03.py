#!/usr/bin/env python3
"""Generate the R226 P1.15/P1.18-bound K1/K2 application record."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
ENG = ROOT / "electrical/reviews/hr-v0-contactor-application-p0.3"
OUT = ROOT / "release/hr-v0/contactor-application-p0.3"
IDENTIFIER = "HR-V0-K1K2-APP-P0.3"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


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


def source_register() -> list[dict[str, str]]:
    local = [
        ("KAP3-SRC-001", P115 / "04_contactor_edm.kicad_sch", "current P1.15 K1/K2 coil, mirror-contact and diagnostic topology"),
        ("KAP3-SRC-002", P115 / "05_actuator_interruption.kicad_sch", "current P1.15 six-pole actuator interruption topology"),
        ("KAP3-SRC-003", P115 / "wire-number-table.csv", "current P1.15 terminal/net schedule"),
        ("KAP3-SRC-004", P115 / "validation/project-button-v3-p1.15-carrier-candidate.net", "current P1.15 machine netlist"),
        ("KAP3-SRC-005", P118 / "04_contactor_edm.kicad_sch", "unaccepted P1.18 K1/K2 coil, mirror-contact and diagnostic topology"),
        ("KAP3-SRC-006", P118 / "05_actuator_interruption.kicad_sch", "unaccepted P1.18 six-pole actuator interruption topology"),
        ("KAP3-SRC-007", P118 / "wire-number-table.csv", "unaccepted P1.18 terminal/net schedule"),
        ("KAP3-SRC-008", P118 / "validation/project-button-v3-p1.18-panel-topology-candidate.net", "unaccepted P1.18 machine netlist"),
        ("KAP3-SRC-009", ROOT / "electrical/contactor/hr-v0-lc1d25bd-application-inputs-p0.2.csv", "R117 application-envelope register retained without inventing measurements"),
        ("KAP3-SRC-010", ROOT / "docs/hr-v0-contactor-application-p0.2.md", "R117 controlled application rationale"),
    ]
    records = [
        {
            "source_id": source_id,
            "source": path.relative_to(ROOT).as_posix(),
            "revision_or_date": "repository source rechecked 2026-08-11",
            "sha256": digest(path),
            "verified_use": use,
            "boundary": "source/configuration evidence only; no physical or application-suitability proof",
            "warning": WARNING,
        }
        for source_id, path, use in local
    ]
    records.extend([
        {
            "source_id": "KAP3-SRC-011",
            "source": "https://www.se.com/us/en/download/document/MKTED210011EN/",
            "revision_or_date": "MKTED210011EN version 17.1; 2026-07-10; rechecked 2026-08-11",
            "sha256": "REMOTE_PRIMARY_SOURCE; R117 controlled PDF hash ACE31998C5091FAAC5BD15C6BE1CC272E52501161B96D3184BDBBB64F9EA8293",
            "verified_use": "Schneider directs DC applications to DC-1 through DC-5 tables and three-pole series selection; critical-current warning retained",
            "boundary": "catalog table is not a Project Button application disposition",
            "warning": WARNING,
        },
        {
            "source_id": "KAP3-SRC-012",
            "source": "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF",
            "revision_or_date": "LC1D25BD product sheet dated 2017-09-13; rechecked 2026-08-11",
            "sha256": "REMOTE_PRIMARY_SOURCE; R117 controlled PDF hash 333EFD8170CDFADAAFBBA19CF07518E0C379380BC4BDA85D2A9355A4DB360D63",
            "verified_use": "24 VDC coil, 16..24 ms opening, 1NO+1NC mechanically linked, NC mirror contact, 5 mA at 17 V signalling minimum",
            "boundary": "the sheet expressly disclaims application-suitability determination; AC marketing ratings are not DC interruption approval",
            "warning": WARNING,
        },
        {
            "source_id": "KAP3-SRC-013",
            "source": "https://www.se.com/uk/en/faqs/FAQ000273244/",
            "revision_or_date": "published 2025-04-04; modified 2026-05-02; rechecked 2026-08-11",
            "sha256": "NOT_APPLICABLE_REMOTE_PRIMARY_SOURCE",
            "verified_use": "official direction to use TeSys catalog chapter A5 DC-1 through DC-5 tables and coordination guidance",
            "boundary": "FAQ does not classify or approve the electronic/capacitive/regenerative robot load",
            "warning": WARNING,
        },
    ])
    return records


def parity_register() -> list[dict[str, str]]:
    a = read_csv(P115 / "wire-number-table.csv")
    b = read_csv(P118 / "wire-number-table.csv")
    records: list[dict[str, str]] = []
    counter = 1
    for sheet, domain in (("04_contactor_edm.kicad_sch", "coil_edm"), ("05_actuator_interruption.kicad_sch", "power_path")):
        left = [row for row in a if row["sheet"] == sheet]
        right = [row for row in b if row["sheet"] == sheet]
        if left != right:
            raise RuntimeError(f"P1.15/P1.18 contactor-critical rows changed on {sheet}")
        for row in left:
            records.append({
                "parity_id": f"KAP3-P-{counter:03d}",
                "domain": domain,
                "sheet": sheet,
                "wire_number": row["wire_number"],
                "reference": row["reference"],
                "terminal": row["terminal"],
                "pin_name": row["pin_name"],
                "net": row["net"],
                "p115_state": "EXACT",
                "p118_state": "EXACT",
                "comparison": "IDENTICAL",
                "warning": WARNING,
            })
            counter += 1
    return records


def chain_register() -> list[dict[str, str]]:
    steps = [
        ("F0:1", "ACT_12V_RAW", "source enters unresolved upstream protection"),
        ("F0:2", "ACT_12V_FUSED", "protection output; rating remains SELECTION REQUIRED"),
        ("SD1:TBD-IN", "ACT_12V_FUSED", "service-disconnect input; terminal remains unresolved"),
        ("SD1:TBD-OUT", "K1_P1_IN", "service-disconnect output; terminal remains unresolved"),
        ("KP1:1L1", "K1_P1_IN", "K1 pole 1 input"),
        ("KP1:2T1", "K1_J12", "series jumper to K1:3L2"),
        ("KP1:3L2", "K1_J12", "K1 pole 2 input"),
        ("KP1:4T2", "K1_J23", "series jumper to K1:5L3"),
        ("KP1:5L3", "K1_J23", "K1 pole 3 input"),
        ("KP1:6T3", "K1_OUT", "K1 output to K2:1L1"),
        ("KP2:1L1", "K1_OUT", "K2 pole 1 input"),
        ("KP2:2T1", "K2_J12", "series jumper to K2:3L2"),
        ("KP2:3L2", "K2_J12", "K2 pole 2 input"),
        ("KP2:4T2", "K2_J23", "series jumper to K2:5L3"),
        ("KP2:5L3", "K2_J23", "K2 pole 3 input"),
        ("KP2:6T3", "ACT_12V_BUS", "switched actuator-bus output"),
    ]
    return [{"step": str(i), "endpoint": ep, "net": net, "interpretation": note, "configuration_result": "P1.15/P1.18 IDENTICAL", "application_result": "NOT APPROVED", "warning": WARNING} for i, (ep, net, note) in enumerate(steps, 1)]


def applicability_register() -> list[dict[str, str]]:
    rows = [
        ("KAP3-A-001", "device identity", "LC1D25BD / 24 VDC coil", "SOURCE CONTROLLED CANDIDATE", "received label and order documentation"),
        ("KAP3-A-002", "main-pole topology", "three poles in series per device; two devices in series", "SOURCE CONNECTED", "point-to-point inspection of accepted configuration"),
        ("KAP3-A-003", "coil/opening component data", "5.4 W at 20 C; 16..24 ms opening", "CATALOG SCREEN ONLY", "received timing and coil-current traces"),
        ("KAP3-A-004", "mirror-contact identity", "integral 21-22 NC catalog mirror contact", "CATALOG SCREEN ONLY", "received contact-state and welded-main-contact validation"),
        ("KAP3-A-005", "normal and peak forward current", "SELECTION REQUIRED", "NOT MEASURED", "configuration-bound bidirectional current traces"),
        ("KAP3-A-006", "current and voltage at opening", "SELECTION REQUIRED", "NOT MEASURED", "synchronized voltage/current/contact traces"),
        ("KAP3-A-007", "regenerative/reverse current", "SELECTION REQUIRED", "NOT MEASURED", "worst-case deceleration and source-response traces"),
        ("KAP3-A-008", "bus capacitance and equivalent time constant", "SELECTION REQUIRED", "NOT MEASURED", "accepted measurement/derivation for exact bus"),
        ("KAP3-A-009", "prospective fault current and protection", "SELECTION REQUIRED", "OPEN", "source current-limit evidence plus selected protection coordination"),
        ("KAP3-A-010", "DC utilization/application classification", "SELECTION REQUIRED", "MANUFACTURER DISPOSITION REQUIRED", "written Schneider response tied to the completed load envelope"),
        ("KAP3-A-011", "critical-current durability", "SELECTION REQUIRED", "MANUFACTURER DISPOSITION REQUIRED", "written response plus required life/cycles and loaded endurance"),
        ("KAP3-A-012", "total stopping performance", "200 ms / 2.000 deg is only the unvalidated J2-positive setup candidate", "NOT VALIDATED", "qualified allocation and executed loaded stop evidence"),
    ]
    return [{"item_id": i, "subject": subject, "value": value, "state": state, "closure_evidence": evidence, "gate": "EG-013 PARTIAL", "warning": WARNING} for i, subject, value, state, evidence in rows]


def holds() -> list[dict[str, str]]:
    items = [
        ("KAP3-H-001", "P1.18 disposition", "formal independent parity review and configuration acceptance or correction"),
        ("KAP3-H-002", "received K1/K2 identity", "received-label, terminal, coil polarity and contact-state records"),
        ("KAP3-H-003", "measured load envelope", "normal/peak/opening/reverse current, contact voltage, capacitance and time constant"),
        ("KAP3-H-004", "source and fault envelope", "source current-limit/regeneration response and prospective fault current"),
        ("KAP3-H-005", "protection coordination", "selected F0/branch devices, curves, interrupting capacity and coordination"),
        ("KAP3-H-006", "conductors and terminations", "exact power conductors, jumpers, lugs/ferrules, lengths, routes and terminal acceptance"),
        ("KAP3-H-007", "environment and duty", "ambient, enclosure, mounting, cycles/hour, required life and maintenance policy"),
        ("KAP3-H-008", "manufacturer application disposition", "identifiable written Schneider response tied to the complete measured envelope"),
        ("KAP3-H-009", "physical loaded interruption", "authorized guarded rail-decay, weld-equivalent, repeated interruption and endurance evidence"),
        ("KAP3-H-010", "stopping requirement/validation", "qualified numerical allocation and executed motion/stopping evidence"),
        ("KAP3-H-011", "qualified review", "configuration-specific electrical and functional-safety signed disposition"),
    ]
    return [{"hold_id": i, "subject": subject, "state": "OPEN", "closure_evidence": evidence, "accepted": "FALSE", "warning": WARNING} for i, subject, evidence in items]


def guide(parity: list[dict[str, str]], chain: list[dict[str, str]], applicability: list[dict[str, str]]) -> str:
    parity_rows = "".join(f"<tr data-domain='{html.escape(r['domain'])}'><td>{html.escape(r['parity_id'])}</td><td>{html.escape(r['domain'])}</td><td>{html.escape(r['reference'])}:{html.escape(r['terminal'])}</td><td>{html.escape(r['net'])}</td><td>{html.escape(r['comparison'])}</td></tr>" for r in parity)
    chain_cards = "".join(f"<article><span>{r['step']}</span><strong>{html.escape(r['endpoint'])}</strong><code>{html.escape(r['net'])}</code><p>{html.escape(r['interpretation'])}</p></article>" for r in chain)
    app_rows = "".join(f"<tr><td>{html.escape(r['item_id'])}</td><td>{html.escape(r['subject'])}</td><td>{html.escape(r['value'])}</td><td>{html.escape(r['state'])}</td><td>{html.escape(r['closure_evidence'])}</td></tr>" for r in applicability)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 K1/K2 application P0.3</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8;--hold:#fff2bd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(26px,3vw,40px)}}.warning{{background:var(--hold);color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}.chain{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}article{{background:white;border:2px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:7px}}article span{{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:var(--gold);font-weight:900}}article strong{{font-size:18px}}code{{font-size:14px;overflow-wrap:anywhere}}label,select{{font-size:16px}}select{{padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white;margin:12px 0 28px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9c;font-weight:750}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} | R226</p><h1>The contactor source now matches the current configuration.</h1><p>P1.15 and P1.18 contain the same 32 contactor-critical terminal/net rows. That closes a stale-baseline ambiguity, not DC application suitability.</p></header><main><div class="verdict"><strong>Verified:</strong> 16 coil/EDM rows and 16 main-power rows are identical. <strong>Still open:</strong> measured break/regeneration duty, protection, durability, stopping evidence, manufacturer disposition, and qualified acceptance.</div><h2>Six-pole actuator interruption chain</h2><div class="chain">{chain_cards}</div><h2>Configuration parity</h2><label for="domain">Show </label><select id="domain"><option value="">all 32 rows</option><option value="coil_edm">coil and EDM</option><option value="power_path">power path</option></select><p id="count" aria-live="polite"></p><div class="tablewrap"><table><thead><tr><th>ID</th><th>Domain</th><th>Endpoint</th><th>Net</th><th>P1.15 vs P1.18</th></tr></thead><tbody id="parity">{parity_rows}</tbody></table></div><h2>Application evidence</h2><div class="tablewrap"><table><thead><tr><th>ID</th><th>Subject</th><th>Value</th><th>State</th><th>Needed to close</th></tr></thead><tbody>{app_rows}</tbody></table></div><div class="warning">EG-013 remains PARTIAL. P1.18 remains unaccepted. No procurement, fabrication, assembly, connection, powered testing, motion, functional-safety approval, or energization authority is created.</div><p><a href="parity-register.csv">32-row parity</a> | <a href="power-chain-register.csv">power chain</a> | <a href="application-evidence-register.csv">application evidence</a> | <a href="open-holds.csv">11 open holds</a> | <a href="source-register.csv">source register</a></p></main><script>const select=document.querySelector('#domain'),rows=[...document.querySelectorAll('#parity tr')],count=document.querySelector('#count');function apply(){{let n=0;rows.forEach(r=>{{const show=!select.value||r.dataset.domain===select.value;r.hidden=!show;if(show)n++}});count.textContent=n+' rows shown'}}select.addEventListener('change',apply);apply();</script></body></html>'''


def main() -> None:
    parity = parity_register()
    chain = chain_register()
    app = applicability_register()
    hold_rows = holds()
    sources = source_register()
    authority = [
        {"activity": "read-only engineering/configuration review", "permitted": "TRUE", "boundary": "repository evidence only", "warning": WARNING},
        {"activity": "supplier contact", "permitted": "FALSE", "boundary": "R117 query remains UNSENT until prerequisites and owner authorization", "warning": WARNING},
        {"activity": "procurement/fabrication/assembly/connection/testing", "permitted": "FALSE", "boundary": "application, physical and qualified evidence remains open", "warning": WARNING},
        {"activity": "motion/energization", "permitted": "FALSE", "boundary": "EG-013 and every applicable stage gate remain unresolved", "warning": WARNING},
    ]
    status = {
        "identifier": IDENTIFIER,
        "round": "R226",
        "date": "2026-08-11",
        "current_electrical": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "unaccepted_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "coil_edm_rows_identical": 16,
        "power_path_rows_identical": 16,
        "open_holds": len(hold_rows),
        "eg_013_status": "partial",
        "p118_accepted": False,
        "dc_application_approved": False,
        "manufacturer_disposition_received": False,
        "physical_tests_executed": False,
        "qualified_review_received": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        write_csv(directory / "parity-register.csv", parity)
        write_csv(directory / "power-chain-register.csv", chain)
        write_csv(directory / "application-evidence-register.csv", app)
        write_csv(directory / "open-holds.csv", hold_rows)
        write_csv(directory / "source-register.csv", sources)
        write_csv(directory / "authority-boundary.csv", authority)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR226 proves 32 exact contactor-critical terminal/net rows are identical between current P1.15 and unaccepted P1.18. It does not approve LC1D25BD for the Project Button DC load. EG-013 remains partial and eleven holds remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(parity, chain, app), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENTIFIER}: 16 coil/EDM + 16 power-path rows identical; {len(hold_rows)} holds; EG-013 partial")


if __name__ == "__main__":
    main()
