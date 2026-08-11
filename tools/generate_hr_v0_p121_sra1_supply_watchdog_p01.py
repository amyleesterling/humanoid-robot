#!/usr/bin/env python3
"""Generate the R234 P1.21 SRA1-supply watchdog disposition package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P120 = ROOT / "electrical/kicad/project-button-v3-p1.20-watchdog-interlock-candidate"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
OUT = ROOT / "release/hr-v0/p121-sra1-supply-watchdog-p0.1"
SAFETY = ROOT / "safety/hr-v0-p121-sra1-supply-watchdog-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
IDENTIFIER = "HR-V0-P121-SRA1-SUPPLY-WD-P0.1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def terminal_delta() -> list[dict[str, object]]:
    old_rows = read_csv(P120 / "connector-schedule.csv")
    new_rows = read_csv(P121 / "connector-schedule.csv")
    key = lambda row: (row["sheet"], row["reference"], row["terminal"])
    old = {key(row): row for row in old_rows}
    new = {key(row): row for row in new_rows}
    result = []
    for item in sorted(old):
        if old[item]["net"] != new[item]["net"] or old[item]["pin_name"] != new[item]["pin_name"]:
            result.append({
                "sheet": item[0], "reference": item[1], "terminal": item[2],
                "p120_pin_name": old[item]["pin_name"], "p120_net": old[item]["net"],
                "p121_pin_name": new[item]["pin_name"], "p121_net": new[item]["net"],
                "reason": "Remove uncredited KWD contacts from PNOZ input loops and series-gate only downstream SRA1 A1.",
                "warning": WARNING,
            })
    return result


ALLOCATION = [
    ("SF-01", "CREDITED CANDIDATE", "S0 + SR1/SRA1 + K1/K2", "KWD1/KWD2 excluded from credited path", "E-stop demand still opens direct SR1-controlled SRA1 inputs even if both KWD contacts are welded or bypassed", "Qualified PLr/SIL/category allocation and physical validation required"),
    ("SF-03", "CREDITED CANDIDATE", "SRA1 monitored ARM + K1/K2 mirror contacts", "KWD supply dropout only resets SRA1; no KWD safety credit", "After a successful dropout, heartbeat restoration only repowers SRA1; a later falling-edge ARM is still required", "Physical restart traces, EDM fault injection and qualified validation required"),
    ("DF-01", "UNCREDITED DIAGNOSTIC", "Pi heartbeat + ordinary RP2040 + KWD1/KWD2", "ZERO SAFETY CREDIT", "A successful diagnostic opens SRA1 supply; stuck-valid/shared failure is assumed", "FMEA, HIL, routing, contact application and timing tests required"),
    ("PG-01", "PHYSICAL PROTECTIVE MEASURE", "Fixed tool-removable guard and catch envelope", "Must contain motion with DF-01 failed", "Guard—not watchdog success—must address assumed uncommanded arm motion", "Released guard, access, impact/drop, retention and qualified mechanical review required"),
]


SCREENS = [
    ("SCR-001", "Pilz SRA1 nominal consumption", "2.5", "W", "Pilz 21396-EN-23", "SOURCE VERIFIED", "Not a measured P1.21 load"),
    ("SCR-002", "Derived nominal SRA1 supply current", "0.10417", "A", "2.5 W / 24 V", "DERIVED SCREEN", "Nominal arithmetic only"),
    ("SCR-003", "Pilz maximum A1 startup pulse", "0.5 for 5", "A for ms", "Pilz 21396-EN-23", "SOURCE VERIFIED", "Not measured in the project circuit"),
    ("SCR-004", "Phoenix minimum contact load", "5 / 0.010", "V / A", "Phoenix 2967060 PDF", "SOURCE VERIFIED", "Does not prove electronic-load endurance"),
    ("SCR-005", "Phoenix maximum inrush envelope", "15 for 300", "A for ms", "Phoenix 2967060 PDF", "SOURCE VERIFIED", "Catalog limit, not application acceptance"),
    ("SCR-006", "Nominal current above minimum-load current", "10.42", "x", "0.10417 A / 0.010 A", "DERIVED SCREEN PASS", "Contact wetting under all states remains physical evidence"),
    ("SCR-007", "Startup current below published inrush current", "30.0", "x", "15 A / 0.5 A", "DERIVED SCREEN PASS", "Pulse shape, repetition and endurance remain open"),
    ("SCR-008", "Startup duration below published inrush duration", "60.0", "x", "300 ms / 5 ms", "DERIVED SCREEN PASS", "Does not establish life or coordination"),
    ("SCR-009", "Nominal voltage above minimum-load voltage", "4.8", "x", "24 V / 5 V", "DERIVED SCREEN PASS", "Actual brownout/recovery window remains unmeasured"),
]


FAULTS = [
    ("FT-001", "Normal heartbeat; KWD1/KWD2 closed; fresh monitored ARM", "SRA1 may become eligible; no motion command is created", "ELIGIBLE_CANDIDATE"),
    ("FT-002", "Heartbeat lost; both KWD contacts open", "SRA1 A1 is removed; SRA1 outputs and K1/K2 coil commands must drop", "SOURCE_TOPOLOGY_EXPECTS_OFF"),
    ("FT-003", "KWD1 11-14 welded; KWD2 opens", "Series SRA1 supply path opens at KWD2", "SINGLE_CONTACT_FAULT_ADDRESSED_IN_SOURCE"),
    ("FT-004", "KWD2 11-14 welded; KWD1 opens", "Series SRA1 supply path opens at KWD1", "SINGLE_CONTACT_FAULT_ADDRESSED_IN_SOURCE"),
    ("FT-005", "Both KWD contacts welded/bypassed or shared command stuck valid", "DF-01 is lost; SRA1 stays powered, but direct SR1 inputs still control its outputs", "DF01_LOST_PG01_REQUIRED"),
    ("FT-006", "E-stop demand with both KWD contacts welded", "SR1 outputs open both direct SRA1 input paths; SRA1 outputs must drop independently of KWD", "SOURCE_NONINTERFERENCE_PASS_PHYSICAL_TEST_REQUIRED"),
    ("FT-007", "Heartbeat restored after successful dropout; no new ARM", "SRA1 may repower but falling-edge monitored start must keep outputs off", "RESTART_TEST_REQUIRED"),
    ("FT-008", "Heartbeat restored; later fresh ARM; EDM healthy", "SRA1 may become eligible; supervisor still requires a fresh trajectory", "ELIGIBLE_CANDIDATE"),
    ("FT-009", "One KWD contact remains open with valid heartbeat", "SRA1 remains unpowered; nuisance-safe loss", "EXPECTED_OFF"),
    ("FT-010", "KWD source-to-output internal short keeps SRA1 A1 powered", "DF-01 may be lost; no modeled path to SR1/SRA1 input returns", "ROUTING_AND_PHYSICAL_FAULT_TEST_REQUIRED"),
    ("FT-011", "External bridge bypasses the complete SRA1 supply gate", "DF-01 is lost; SF-01/SF-03 source authority remains in SR1/SRA1 inputs and outputs", "PROTECTED_ROUTING_REQUIRED"),
    ("FT-012", "SRA1 A1 brownout, relay chatter or asynchronous KWD opening", "Response and recovery are not accepted from source logic", "MANUFACTURER_AND_PHYSICAL_TEST_REQUIRED"),
    ("FT-013", "KWD hot conductor bridges into an SRA1 input/start conductor", "Credited logic could be impaired", "HAZARDOUS_ROUTE_FAULT_OPEN"),
    ("FT-014", "SRA1 internal output fault or K1/K2 final-element fault", "KWD supply gate receives no credit for the safety function", "SF01_SF03_VALIDATION_OPEN"),
]


HOLDS = [
    ("P121-H01", "Independent terminal-by-terminal P1.21 review"),
    ("P121-H02", "Pilz written acceptance or qualified justification for switching/power-cycling SRA1 A1 in this application"),
    ("P121-H03", "Phoenix contact endurance, minimum-load, inrush and protection application evidence"),
    ("P121-H04", "Released protected route and separation preventing KWD supply conductors from bridging SRA1 input/start paths"),
    ("P121-H05", "Received component identity, terminal mapping, continuity, polarity and selector inspection"),
    ("P121-H06", "Authorized no-load brownout, chatter, dropout and restart traces across all source permutations"),
    ("P121-H07", "Authorized single/dual weld, bypass, short, open and common-cause fault injection"),
    ("P121-H08", "Measured K1/K2, actuator-rail, torque and total stopping response"),
    ("P121-H09", "Qualified PLr/SIL/category, CCF/DC/reliability allocation and validation"),
    ("P121-H10", "Released PG-01 guard/receiver and physical containment evidence with DF-01 assumed failed"),
    ("P121-H11", "Formal configuration promotion and separately signed work authorization"),
]


SOURCES = [
    ("SRC-001", "Pilz", "PNOZ s4 750104 operating manual 21396-EN-23", "2026-06-22 portal file; rechecked 2026-08-11", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "A1/A2 supply data, monitored falling-edge start and terminal functions", "No Project Button application acceptance"),
    ("SRC-002", "Phoenix Contact", "PLC-RSC-24DC/21-21 item 2967060 product PDF", "data maintenance 2026-04-01; PDF generated/rechecked 2026-08-11", "https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf", "Terminal identity, minimum load and inrush envelope", "Ordinary non-force-guided relay; no safety claim or Project Button acceptance"),
    ("SRC-003", "Project Button", "HR-V0 safety-function allocation", "current source rechecked 2026-08-11", "safety/hr-v0-safety-function-allocation.csv", "SF-01/SF-03 credited candidates; DF-01 zero credit; PG-01 assumes DF-01 failure", "Qualified allocation and physical evidence absent"),
    ("SRC-004", "Project Button", "HR-V0 watchdog P0.2 source", "current source rechecked 2026-08-11", "firmware/watchdog/src/pb_watchdog.c", "Three valid edges can restore ordinary relay commands after an uncomplicated timeout", "Firmware is uncredited and not deployed/HIL validated"),
]


def records(rows: list[tuple[str, ...]], fields: tuple[str, ...]) -> list[dict[str, object]]:
    return [dict(zip(fields, row)) | {"warning": WARNING} for row in rows]


def page(delta: list[dict[str, object]]) -> str:
    drows = "".join(f"<tr><td><strong>{html.escape(str(r['reference']))}:{html.escape(str(r['terminal']))}</strong></td><td><code>{html.escape(str(r['p120_net']))}</code></td><td><code>{html.escape(str(r['p121_net']))}</code></td></tr>" for r in delta)
    frows = "".join(f"<tr data-state='{html.escape(state)}'><td><strong>{fid}</strong></td><td>{html.escape(condition)}</td><td>{html.escape(response)}</td><td>{html.escape(state)}</td></tr>" for fid, condition, response, state in FAULTS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.21 SRA1-supply watchdog review</title><style>
:root{{--sky:#78cef2;--navy:#082b4c;--blue:#155d91;--gold:#f3b61f;--paper:#f5fbff;--line:#94b8ce}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eefaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2rem,5vw,4.4rem);line-height:1.04;max-width:19ch;margin:.35rem 0 1rem}}h2{{font-size:clamp(1.4rem,2.2vw,2.1rem)}}main{{max-width:1500px;margin:auto;padding:2rem clamp(1rem,4vw,3rem)}}.warning{{padding:1rem;border:3px solid #a87500;background:#fff3c4;border-radius:.8rem;font-weight:700}}.lead{{font-size:clamp(1.15rem,1.8vw,1.5rem);max-width:72rem}}.flow{{display:grid;grid-template-columns:repeat(6,minmax(170px,1fr));gap:.65rem;overflow:auto;padding:.8rem 0}}.node{{border:3px solid var(--blue);border-radius:.8rem;padding:1rem;background:var(--paper);min-height:120px}}.node strong{{display:block}}button{{font:inherit;font-weight:700;color:var(--navy);background:#fff;border:3px solid var(--blue);border-radius:.55rem;padding:.65rem .9rem;margin:.2rem}}button[aria-pressed=true]{{background:var(--gold)}}.table{{overflow:auto;border:2px solid var(--line);border-radius:.7rem;margin:1rem 0}}table{{width:100%;border-collapse:collapse;min-width:950px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b7ccd8}}th{{background:var(--navy);color:#fff;position:sticky;top:0}}code{{font-size:14px;white-space:normal}}[hidden]{{display:none!important}}@media(max-width:700px){{.flow{{grid-template-columns:repeat(6,200px)}}}}
</style></head><body><header><strong>{IDENTIFIER} / R234</strong><h1>Keep the watchdog outside the safety inputs</h1><div class="warning">{WARNING}</div></header><main><p class="lead">P1.21 moves both ordinary KWD contacts out of the PNOZ input loops. They series-gate only downstream SRA1 power. A successful heartbeat-loss dropout power-cycles SRA1, so heartbeat recovery alone cannot restore its outputs. The E-stop path remains direct and the watchdog still receives zero safety credit.</p><h2>Authority path</h2><div class="flow"><div class="node"><strong>S0</strong>Dual direct E-stop inputs</div><div class="node"><strong>SR1</strong>Independently powered eligibility stage</div><div class="node"><strong>SRA1 inputs</strong>Directly controlled by SR1</div><div class="node"><strong>KWD1 + KWD2</strong>Series A1 diagnostic gate only</div><div class="node"><strong>SRA1 outputs</strong>Separate high-side coil commands</div><div class="node"><strong>K1 + K2</strong>Series actuator-rail interruption</div></div><h2>Exactly seven terminal changes</h2><div class="table"><table><thead><tr><th>Terminal</th><th>P1.20</th><th>P1.21</th></tr></thead><tbody>{drows}</tbody></table></div><h2>Fault boundary</h2><div><button data-filter="ALL" aria-pressed="true">All 14</button><button data-filter="DF01_LOST_PG01_REQUIRED">DF-01 lost</button><button data-filter="RESTART_TEST_REQUIRED">Restart</button><button data-filter="HAZARDOUS_ROUTE_FAULT_OPEN">Hazardous/open</button></div><div class="table"><table><thead><tr><th>Case</th><th>Condition</th><th>Modeled response</th><th>Disposition</th></tr></thead><tbody>{frows}</tbody></table></div><h2>Release boundary</h2><p>Source topology, ERC and paper contact screens do not establish functional-safety performance, physical stopping, guard containment, contact life, manufacturer application acceptance or work authority. P1.15 remains current; P1.21 is unaccepted.</p></main><script>const bs=[...document.querySelectorAll('button[data-filter]')],rs=[...document.querySelectorAll('tbody tr[data-state]')];bs.forEach(b=>b.addEventListener('click',()=>{{bs.forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');const f=b.dataset.filter;rs.forEach(r=>r.hidden=f!=='ALL'&&r.dataset.state!==f)}}));</script></body></html>'''


def main() -> None:
    for directory in (OUT, SAFETY):
        directory.mkdir(parents=True, exist_ok=True)
    delta = terminal_delta()
    if len(delta) != 7:
        raise RuntimeError(f"expected seven terminal changes, found {len(delta)}")
    datasets = {
        "topology-delta.csv": (("sheet","reference","terminal","p120_pin_name","p120_net","p121_pin_name","p121_net","reason","warning"), delta),
        "safety-allocation-boundary.csv": (("function_id","classification","credited_or_protective_path","watchdog_boundary","modeled_result","required_closure_evidence","warning"), records(ALLOCATION, ("function_id","classification","credited_or_protective_path","watchdog_boundary","modeled_result","required_closure_evidence"))),
        "supply-duty-screen.csv": (("screen_id","parameter","value","unit","basis","disposition","limitation","warning"), records(SCREENS, ("screen_id","parameter","value","unit","basis","disposition","limitation"))),
        "fault-truth-table.csv": (("case_id","condition","modeled_response","disposition","warning"), records(FAULTS, ("case_id","condition","modeled_response","disposition"))),
        "source-register.csv": (("source_id","owner","document","revision_or_date","url_or_path","use","limitation","warning"), records(SOURCES, ("source_id","owner","document","revision_or_date","url_or_path","use","limitation"))),
        "open-holds.csv": (("hold_id","closure_evidence","state","warning"), [dict(hold_id=i, closure_evidence=e, state="OPEN", warning=WARNING) for i,e in HOLDS]),
    }
    parity = {
        "identifier": IDENTIFIER, "round": "R234", "p120": "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE",
        "p121": "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "native_sheets": 13,
        "components": 84, "modeled_terminals": 340, "named_nets": 106,
        "changed_terminal_assignments": 7, "unchanged_terminal_assignments": 333,
        "removed_nets": ["SR1_OUT1_TO_KWD1", "SR1_OUT2_TO_KWD2"],
        "added_nets": ["WD_SRA1_SUPPLY_INTERMEDIATE", "SRA1_A1_WD_GATED"],
        "erc_errors": 0, "erc_warnings": 0, "fault_cases": len(FAULTS), "open_holds": len(HOLDS),
        "p115_current": True, "p121_accepted": False, "watchdog_safety_credit": "NONE",
        "qualified_review": False, "work_authority": False, "warning": WARNING,
    }
    for directory in (OUT, SAFETY):
        for name, (fields, rows) in datasets.items():
            write_csv(directory / name, fields, rows)
        (directory / "parity-summary.json").write_text(json.dumps(parity, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR234 records the unaccepted P1.21 SRA1-supply watchdog candidate: seven exact terminal changes, 14 fault cases, nine supply/contact screens and 11 open holds. P1.15 remains current. DF-01 has zero safety credit.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(page(delta), encoding="utf-8", newline="\n")
    manifest = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        data = path.read_bytes()
        manifest.append({"file": path.name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", ("file","size_bytes","sha256","warning"), manifest)
    print(f"Wrote {IDENTIFIER}: 7 terminal changes, {len(FAULTS)} fault cases, {len(HOLDS)} open holds")
    print(WARNING)


if __name__ == "__main__":
    main()
