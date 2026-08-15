#!/usr/bin/env python3
"""Generate the R232 P1.20 watchdog-interlock disposition package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P119 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.19-visual-correction-candidate"
P120 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"
OUT = ROOT / "release" / "hr-v0" / "p120-watchdog-interlock-p0.1"
ENG = ROOT / "electrical" / "reviews" / "hr-v0-p120-watchdog-interlock-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
IDENTIFIER = "HR-V0-P120-WD-INTERLOCK-P0.1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def terminal_delta() -> list[dict[str, object]]:
    old_rows = read_csv(P119 / "connector-schedule.csv")
    new_rows = read_csv(P120 / "connector-schedule.csv")
    key = lambda row: (row["sheet"], row["reference"], row["terminal"])
    old = {key(row): row for row in old_rows}
    new = {key(row): row for row in new_rows}
    result = []
    for item in sorted(old):
        if old[item]["net"] != new[item]["net"] or old[item]["pin_name"] != new[item]["pin_name"]:
            result.append({
                "sheet": item[0], "reference": item[1], "terminal": item[2],
                "old_pin_name": old[item]["pin_name"], "old_net": old[item]["net"],
                "new_pin_name": new[item]["pin_name"], "new_net": new[item]["net"],
                "reason": "Move the ordinary watchdog from SR1 supply gating to one independently interrupted SRA1 input return per channel.",
                "warning": WARNING,
            })
    return result


FAULTS = [
    ("FT-001", "Normal heartbeat and a fresh monitored ARM event", "CLOSED", "CLOSED", "PRESENT", "YES", "ELIGIBLE", "SRA1 may close only after its configured monitored start and EDM conditions; no motion command is created."),
    ("FT-002", "Heartbeat lost; both KWD paths open", "OPEN", "OPEN", "ABSENT", "NO", "OFF", "Both SRA1 input returns open and both SRA1 outputs must drop."),
    ("FT-003", "KWD1 11-14 welded; heartbeat lost", "WELDED_CLOSED", "OPEN", "ABSENT", "NO", "OFF", "KWD2 opens channel 2, so one welded KWD contact cannot preserve SRA1 eligibility."),
    ("FT-004", "KWD2 11-14 welded; heartbeat lost", "OPEN", "WELDED_CLOSED", "ABSENT", "NO", "OFF", "KWD1 opens channel 1, so one welded KWD contact cannot preserve SRA1 eligibility."),
    ("FT-005", "Both KWD 11-14 contacts welded or bypassed", "WELDED_CLOSED", "WELDED_CLOSED", "ABSENT", "NO", "HAZARDOUS_UNRESOLVED", "Both SRA1 input returns can remain complete. This common-cause case is not controlled by source topology."),
    ("FT-006", "Shared controller or driver command holds both relays on", "CLOSED", "CLOSED", "ABSENT", "NO", "HAZARDOUS_UNRESOLVED", "Both ordinary contacts can remain closed despite heartbeat loss. No safety credit or fault exclusion is allowed."),
    ("FT-007", "Only channel-1 field conductor bypassed", "BYPASSED_CLOSED", "OPEN", "ABSENT", "NO", "OFF", "The independent channel-2 return still opens."),
    ("FT-008", "Only channel-2 field conductor bypassed", "OPEN", "BYPASSED_CLOSED", "ABSENT", "NO", "OFF", "The independent channel-1 return still opens."),
    ("FT-009", "Both SRA1 watchdog-interlock paths bypassed", "BYPASSED_CLOSED", "BYPASSED_CLOSED", "ABSENT", "NO", "HAZARDOUS_UNRESOLVED", "Protected routing, separation and credible-short disposition remain mandatory."),
    ("FT-010", "One KWD path open while heartbeat is valid", "OPEN", "CLOSED", "PRESENT", "YES", "OFF", "SRA1 cannot become or remain eligible; nuisance loss is fail-closed."),
    ("FT-011", "Heartbeat restored after a successful dropout; no new ARM", "CLOSED", "CLOSED", "RESTORED", "NO", "OFF", "The configured monitored ARM stage must not restart from contact restoration alone."),
    ("FT-012", "Heartbeat restored; fresh monitored ARM; all other conditions healthy", "CLOSED", "CLOSED", "RESTORED", "YES", "ELIGIBLE", "Eligibility may return, but RESET/ARM still creates no trajectory or torque request."),
]


def fault_records() -> list[dict[str, object]]:
    return [
        {
            "case_id": case, "condition": condition, "kwd1_11_14": k1, "kwd2_11_14": k2,
            "heartbeat": heartbeat, "fresh_arm_event": arm, "expected_sra1_output": output,
            "disposition": disposition, "safety_credit": "NONE", "warning": WARNING,
        }
        for case, condition, k1, k2, heartbeat, arm, output, disposition in FAULTS
    ]


def sources() -> list[dict[str, object]]:
    return [
        {"source_id":"SRC-001","manufacturer":"Phoenix Contact","subject":"PLC-RSC-24DC/21-21 item 2967060","document":"Official product record and generated product PDF","revision_date":"data maintenance 2026-04-01; rechecked 2026-08-11","url":"https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060","use":"A1/A2 and 11-12-14/21-22-24 terminal identity; typical coil current and switching times only","limitation":"Not force-guided or safety-rated; no Project Button application acceptance","warning":WARNING},
        {"source_id":"SRC-002","manufacturer":"Pilz","subject":"PNOZ s4 order 750104","document":"Operating Manual 21396-EN-23","revision_date":"2026-06-22; rechecked 2026-08-11","url":"https://www.pilz.com/en-US/eshop/product/750104","use":"Dual-channel input, monitored-start and positive-guided output architecture basis","limitation":"Exact Project Button circuit/configuration, external ordinary contacts and achieved PL/SIL require qualified acceptance and validation","warning":WARNING},
        {"source_id":"SRC-003","manufacturer":"Schneider Electric","subject":"LC1D25BD","document":"Official product record plus MKTED210011EN catalog","revision_date":"product record rechecked 2026-08-11; catalog 2026","url":"https://www.se.com/us/en/product/LC1D25BD/","use":"Exact 24 VDC contactor identity; final-element boundary retained unchanged","limitation":"DC critical-current, interruption, suppression, life and Project Button application remain open","warning":WARNING},
    ]


def holds() -> list[dict[str, object]]:
    data = [
        ("WDH-H01", "Independent P1.20 topology review", "Independent electrical review of every changed terminal/net and all unchanged safety/power-critical paths"),
        ("WDH-H02", "PNOZ input and monitored-start application", "Qualified confirmation of exact SRA1 configuration, channel behavior, reset/ARM sequencing, external-contact suitability and fault response"),
        ("WDH-H03", "Ordinary KWD contact application", "Selected input current/wetting, minimum load, bounce, contamination, endurance and received terminal/contact evidence"),
        ("WDH-H04", "Common cause and dependent failure", "Accepted analysis of controller, clock, supply, PCB, driver, harness and environmental common causes; no unsupported fault exclusion"),
        ("WDH-H05", "Protected routing and separation", "Released two-channel point-to-point routes, separation, terminal allocation, inspection and credible-short disposition"),
        ("WDH-H06", "Manual re-arm proof", "Executed trace proving heartbeat restoration alone cannot energize SRA1, K1 or K2 and that a later distinct ARM event is required"),
        ("WDH-H07", "Fault injection and stopping evidence", "Authorized current-limited tests for single/dual weld, bypass, open, stuck output, power loss, rail decay, torque decay and stopping response"),
        ("WDH-H08", "Functional-safety allocation and validation", "Qualified PLr/SIL/category determination, CCF/DC/MTTFd or SIL calculation, validation plan, execution and signature"),
        ("WDH-H09", "Configuration promotion", "Formal decision before P1.20 may supersede P1.15; P1.18/P1.19/P1.20 remain unaccepted"),
    ]
    return [{"hold_id":i,"subject":s,"state":"OPEN","closure_evidence":e,"warning":WARNING} for i,s,e in data]


def html_page(delta: list[dict[str, object]], faults: list[dict[str, object]]) -> str:
    delta_rows = "".join(f"<tr><td>{html.escape(str(r['reference']))}:{html.escape(str(r['terminal']))}</td><td><code>{html.escape(str(r['old_net']))}</code></td><td><code>{html.escape(str(r['new_net']))}</code></td></tr>" for r in delta)
    fault_rows = "".join(f"<tr data-output='{html.escape(str(r['expected_sra1_output']))}'><td>{html.escape(str(r['case_id']))}</td><td>{html.escape(str(r['condition']))}</td><td>{html.escape(str(r['kwd1_11_14']))}</td><td>{html.escape(str(r['kwd2_11_14']))}</td><td><strong>{html.escape(str(r['expected_sra1_output']))}</strong></td><td>{html.escape(str(r['disposition']))}</td></tr>" for r in faults)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.20 watchdog interlock review</title><style>
:root{{--sky:#79cff3;--navy:#082b4c;--blue:#145b8d;--gold:#f3b61f;--paper:#f5fbff;--line:#9bbbcf}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#edfaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.5rem);line-height:1.04;max-width:18ch;margin:.35rem 0 1rem}}h2{{font-size:clamp(1.4rem,2.2vw,2.1rem)}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #a87500;background:#fff3c4;border-radius:.8rem;font-weight:700}}.summary{{font-size:clamp(1.15rem,1.8vw,1.5rem);max-width:68rem}}.flow{{display:grid;grid-template-columns:repeat(5,minmax(160px,1fr));gap:.65rem;overflow:auto;padding:.7rem 0}}.node{{border:3px solid var(--blue);border-radius:.8rem;padding:1rem;background:var(--paper);min-height:110px}}.node strong{{display:block}}button{{font:inherit;font-weight:700;color:var(--navy);background:#fff;border:3px solid var(--blue);border-radius:.55rem;padding:.6rem .85rem;margin:.2rem}}button[aria-pressed=true]{{background:var(--gold)}}.table-wrap{{overflow:auto;border:2px solid var(--line);border-radius:.7rem;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{padding:.75rem;text-align:left;vertical-align:top;border-bottom:1px solid #b8ccd8}}th{{background:var(--navy);color:#fff;position:sticky;top:0}}code{{font-size:14px;white-space:normal}}[hidden]{{display:none!important}}@media(max-width:650px){{.flow{{grid-template-columns:repeat(5,190px)}}}}
</style></head><body><header><strong>{IDENTIFIER} / R232</strong><h1>Watchdog loss now interrupts ARM eligibility</h1><div class="warning">{WARNING}</div></header><main><p class="summary">P1.20 removes the ordinary watchdog from SR1’s power supply. KWD1 interrupts SRA1 channel 1; KWD2 independently interrupts channel 2. Either single welded watchdog contact is defeated by the other channel opening. Dual/common-cause failure remains hazardous, so the watchdog still receives zero safety credit.</p>
<h2>Candidate signal path</h2><div class="flow"><div class="node"><strong>SR1 output 14</strong>E-stop eligibility channel 1</div><div class="node"><strong>KWD1 11–14</strong>Ordinary interlock, zero safety credit</div><div class="node"><strong>SRA1 S12</strong>ARM channel 1 return</div><div class="node"><strong>SRA1 outputs</strong>Two separately protected coil commands</div><div class="node"><strong>K1 + K2</strong>Series actuator-power interruption</div></div><div class="flow"><div class="node"><strong>SR1 output 24</strong>E-stop eligibility channel 2</div><div class="node"><strong>KWD2 11–14</strong>Ordinary interlock, zero safety credit</div><div class="node"><strong>SRA1 S22</strong>ARM channel 2 return</div><div class="node"><strong>Fresh ARM required</strong>Restoration alone must remain OFF</div><div class="node"><strong>Motion command separate</strong>ARM never creates trajectory authority</div></div>
<h2>Seven-terminal topology delta</h2><div class="table-wrap"><table><thead><tr><th>Terminal</th><th>P1.19 net</th><th>P1.20 net</th></tr></thead><tbody>{delta_rows}</tbody></table></div>
<h2>Fault screens</h2><div><button data-filter="ALL" aria-pressed="true">All 12</button><button data-filter="OFF">Expected off</button><button data-filter="ELIGIBLE">Eligible</button><button data-filter="HAZARDOUS_UNRESOLVED">Hazardous/open</button></div><div class="table-wrap"><table><thead><tr><th>Case</th><th>Condition</th><th>KWD1</th><th>KWD2</th><th>SRA1 expectation</th><th>Boundary</th></tr></thead><tbody>{fault_rows}</tbody></table></div>
<h2>What remains open</h2><p>Exact PNOZ input/start application, KWD minimum-load and endurance suitability, two-channel routing, common-cause analysis, received identity, physical fault injection, stopping measurement, PLr/SIL allocation and qualified review. P1.15 remains current; P1.20 is unaccepted.</p></main><script>const bs=[...document.querySelectorAll('button[data-filter]')],rs=[...document.querySelectorAll('tbody tr[data-output]')];bs.forEach(b=>b.addEventListener('click',()=>{{bs.forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');const f=b.dataset.filter;rs.forEach(r=>r.hidden=f!=='ALL'&&r.dataset.output!==f)}}));</script></body></html>"""


def main() -> None:
    for directory in (OUT, ENG):
        directory.mkdir(parents=True, exist_ok=True)
    delta = terminal_delta()
    faults = fault_records()
    need = lambda condition, message: (_ for _ in ()).throw(RuntimeError(message)) if not condition else None
    need(len(delta) == 7, f"expected seven terminal deltas, found {len(delta)}")
    parity = {
        "identifier": IDENTIFIER, "round": "R232", "p119": "V3-P1.19-VISUAL-CORRECTION-CANDIDATE",
        "p120": "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE", "native_sheets": 13,
        "components": 84, "modeled_terminals": 340, "named_nets": 106,
        "unchanged_terminal_net_assignments": 333, "changed_terminal_net_assignments": 7,
        "native_netlist_component_value_footprint_identity_equal": True,
        "native_netlist_changed_net_memberships": 7,
        "removed_nets": ["SR1_A1_WD_GATED", "WD_SUPPLY_INTERMEDIATE"],
        "added_nets": ["SR1_OUT1_TO_KWD1", "SR1_OUT2_TO_KWD2"],
        "erc_errors": 0, "erc_warnings": 0, "p115_current": True,
        "p120_accepted": False, "safety_credit": "NONE", "work_authority": False,
        "warning": WARNING,
    }
    datasets = {
        "topology-delta.csv": (("sheet","reference","terminal","old_pin_name","old_net","new_pin_name","new_net","reason","warning"), delta),
        "fault-truth-table.csv": (("case_id","condition","kwd1_11_14","kwd2_11_14","heartbeat","fresh_arm_event","expected_sra1_output","disposition","safety_credit","warning"), faults),
        "source-register.csv": (("source_id","manufacturer","subject","document","revision_date","url","use","limitation","warning"), sources()),
        "open-holds.csv": (("hold_id","subject","state","closure_evidence","warning"), holds()),
    }
    for directory in (OUT, ENG):
        for name, (fields, records) in datasets.items():
            write_csv(directory / name, fields, records)
        (directory / "parity-summary.json").write_text(json.dumps(parity, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR232 records the exact seven-terminal P1.19-to-P1.20 watchdog-interlock delta and twelve fault screens. P1.20 remains unaccepted and the ordinary watchdog receives zero safety credit.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(html_page(delta, faults), encoding="utf-8", newline="\n")
    manifest_rows = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        data = path.read_bytes()
        manifest_rows.append({"file":path.name,"size_bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"warning":WARNING})
    write_csv(OUT / "file-manifest.csv", ("file","size_bytes","sha256","warning"), manifest_rows)
    print(f"Wrote {IDENTIFIER}: {len(delta)} terminal deltas, {len(faults)} fault cases, {len(holds())} open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
