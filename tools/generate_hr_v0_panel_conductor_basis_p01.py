#!/usr/bin/env python3
"""Generate the fail-closed HR-V0 panel conductor engineering basis."""

from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/panel-conductor-basis-p0.1"
SOURCE = ROOT / "release/hr-v0/control-panel-configuration-p0.1/current-stationary-wire-schedule.csv"
IDENTIFIER = "HR-V0-PANEL-COND-P0.1"
DATE = "2026-08-11"
ROUND = "R221"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)
DOOR_REFS = {"S0", "S1", "S2", "H1"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty register: {name}")
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    row["warning"] = WARNING
    return row


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    endpoints = read(SOURCE)
    if len(endpoints) != 66:
        raise SystemExit(f"expected 66 current panel endpoint records, found {len(endpoints)}")

    sources = [
        ("PCS-SRC-001", "Belden", "3057 live product record", "revision 0.120 dated 2026-06-30; accessed 2026-08-11", "https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3057", "16 AWG 26x30 tinned-copper PVC; 2.3 mm nominal OD; 300 V AWM; -40 to 105 C; 23 mm stationary bend radius; active color/put-up suffixes", "No published DCR on the controlled live page; no dynamic-flex rating, installed ampacity, bundle derating, route or application release"),
        ("PCS-SRC-002", "Pilz", "PNOZ s4 operating manual", "21396-EN-23; 2026-02 document; accessed 2026-08-11", "https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf", "750104 screw terminals: one flexible conductor 0.25 to 2.5 mm2 / AWG 24 to 12; 0.5 N m; 7 mm strip", "Does not select Project Button wire, ferrule, routing, protection or achieved safety performance"),
        ("PCS-SRC-003", "Phoenix Contact", "PLC-RSC-24DC/21-21 product record", "item 2967060; data maintenance 2026-04-01; accessed 2026-08-11", "https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060", "Screw connection; flexible 0.14 to 2.5 mm2; AWG 26 to 14; single ferrule 0.2 to 2.5 mm2; 8 mm strip; 0.6 to 0.8 N m", "Ordinary relay only; zero safety credit; installed contact and conductor application remain open"),
        ("PCS-SRC-004", "Schneider Electric", "LC1D25BD product data sheet", "SQD-LC1D25BD.PDF dated 2017-09-13; live identity rechecked 2026-08-11", "https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF", "Control screw terminals: one flexible conductor 1 to 4 mm2 with or without cable end; 1.7 N m; 24 VDC coil; 5.4 W at 20 C", "Sheet does not publish strip length or prove DC actuator interruption, Project Button coordination or received behavior"),
        ("PCS-SRC-005", "Phoenix Contact", "PT 2,5 product record", "item 3209510; live record accessed 2026-08-11", "https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-3209510", "Push-in; flexible 0.14 to 4 mm2; ferrule 0.14 to 2.5 mm2; AWG 26 to 12; 8 to 10 mm strip", "Nominal component data does not establish Project Button conductor protection, temperature or installed acceptance"),
        ("PCS-SRC-006", "IDEC", "HW screw-terminal catalog and exact HW product records", "HW Series Catalog_Screw dated 2026-07-23; accessed 2026-08-11", "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/22mm-25mm-30mm-switches/hw-22mm-heavy-duty/hw1p-1fqd-a-24v", "HW screw-terminal family; connectable wire up to 2 mm2 recorded by manufacturer", "Exact complete-assembly terminal/lug method, received markings, door flex route and dynamic cable are unverified"),
        ("PCS-SRC-007", "IDEC", "XW1E-BV402M-R product record and XW catalog", "exact product page current; XW catalog dated 2024-06-24; accessed 2026-08-11", "https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/emergency-stop-switches/xw-22mm-estop/xw1e-bv402m-r", "Exact dual-NC screw-terminal E-stop identity", "Exact wire range, terminal accessory, lug method, received positive-opening identity and dynamic door route remain open"),
        ("PCS-SRC-008", "Phoenix Contact", "MKDS 1/2-3,5 product record", "item 1751248; accessed 2026-08-11", "https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248", "Flexible conductor 0.14 to 1.5 mm2; AWG 26 to 16; ferrule limited to 0.25 to 0.5 mm2; 5 mm strip; 0.22 to 0.25 N m", "Not one of the 66 panel-device endpoint rows; recorded to prevent an incompatible 16 AWG ferrule at watchdog-board terminals"),
    ]
    write("source-register.csv", [warned({
        "source_id": sid, "manufacturer": manufacturer, "artifact": artifact,
        "revision_or_date": revision, "official_url": url,
        "verified_fact": fact, "does_not_establish": limit,
    }) for sid, manufacturer, artifact, revision, url, fact, limit in sources])

    candidates = [
        ("PCS-COND-001", "fixed internal panel point-to-point", "Belden 3057 family", "16 AWG / approximately 1.31 mm2", "26x30 tinned copper; PVC; 2.3 mm nominal OD", "SOURCE-CONTROLLED FAMILY CANDIDATE", "Exact color/put-up suffix, DCR, cut length, installed ampacity, bundling, ambient, routing, protection, ferrule/direct method and received-lot evidence"),
        ("PCS-COND-002", "door loom for S0/S1/S2/H1", "SELECTION REQUIRED", "SELECTION REQUIRED", "Dynamic-flex-rated construction required", "NO CANDIDATE", "Flex cycles, bend radius, torsion, abrasion, temperature, door travel, strain relief, separation, exact wire/cable and terminal accessories"),
        ("PCS-COND-003", "protective-earth bonding", "SELECTION REQUIRED", "SELECTION REQUIRED", "Green/yellow alone does not select a bonding conductor", "OUTSIDE THIS 66-ENDPOINT CONTROL SCHEDULE", "Fault current, clearing time, jurisdiction, stud/lug hardware, coating removal, flex bonds and measured impedance"),
        ("PCS-COND-004", "actuator-current conductors", "SELECTION REQUIRED", "SELECTION REQUIRED", "Separate high-current architecture", "OUTSIDE THIS 66-ENDPOINT CONTROL SCHEDULE", "Fault current, inrush, duty, cable length, ambient, bundling, connector limits, voltage drop and protection coordination"),
    ]
    write("conductor-family-candidates.csv", [warned({
        "candidate_id": cid, "scope": scope, "family_or_selection": family,
        "gauge": gauge, "construction": construction, "candidate_state": state,
        "closure_evidence_required": evidence,
    }) for cid, scope, family, gauge, construction, state, evidence in candidates])

    terminal_rows = [
        ("PCS-TERM-001", "S0", "IDEC XW1E-BV402M-R screw terminal", "SELECTION REQUIRED", "SELECTION REQUIRED", "SELECTION REQUIRED", "NOT PROVEN", "Door-loom conductor absent; exact XW terminal range/accessory and lug/direct method must be controlled"),
        ("PCS-TERM-002", "S1/S2/H1", "IDEC HW screw terminal", "up to 2 mm2 family maximum", "SELECTION REQUIRED", "SELECTION REQUIRED", "GAUGE ENVELOPE ONLY", "Door-loom conductor absent; exact complete-assembly terminal, lug/direct method and received identity remain open"),
        ("PCS-TERM-003", "SR1/SRA1", "Pilz 750104 screw terminal", "0.25 to 2.5 mm2 flexible; AWG 24 to 12", "7 mm", "0.5 N m", "16 AWG GAUGE FIT", "Single/twin conductor allocation, ferrule/direct method, exact ferrule/tool and installed pull/torque evidence remain open"),
        ("PCS-TERM-004", "KWD1/KWD2", "Phoenix 2967060 screw terminal", "0.14 to 2.5 mm2 flexible; AWG 26 to 14", "8 mm", "0.6 to 0.8 N m", "16 AWG GAUGE FIT", "Exact ferrule/direct method, polarity, installed pull/torque and supply-gate fault testing remain open"),
        ("PCS-TERM-005", "K1/K2 control terminals", "Schneider LC1D25BD screw clamp", "1 to 4 mm2 one flexible conductor", "SELECTION REQUIRED", "1.7 N m", "16 AWG GAUGE FIT; 22 AWG REJECTED", "Strip length, cable-end method, received markings, coil behavior and DC application/coordination remain open"),
        ("PCS-TERM-006", "XT1", "Phoenix PT 2,5 push-in", "0.14 to 4 mm2 flexible; 0.14 to 2.5 mm2 with ferrule", "8 to 10 mm", "NOT APPLICABLE - PUSH-IN", "16 AWG GAUGE FIT", "Direct/ferrule method, exact ferrule/tool, installed pull and temperature evidence remain open"),
        ("PCS-TERM-007", "watchdog PCB terminals (interface caution)", "Phoenix MKDS 1/2-3,5 item 1751248", "0.14 to 1.5 mm2 flexible; ferrule only 0.25 to 0.5 mm2", "5 mm", "0.22 to 0.25 N m", "16 AWG DIRECT-WIRE GAUGE FIT ONLY; 16 AWG FERRULE REJECTED", "Not in the 66 endpoint schedule; direct/ferrule process and received terminal evidence remain open"),
    ]
    write("terminal-compatibility.csv", [warned({
        "record_id": rid, "references": refs, "terminal_family": family,
        "published_conductor_envelope": envelope, "published_strip_length": strip,
        "published_torque": torque, "candidate_disposition": disposition,
        "remaining_evidence": remaining,
    }) for rid, refs, family, envelope, strip, torque, disposition, remaining in terminal_rows])

    schedule: list[dict[str, object]] = []
    for row in endpoints:
        door = row["reference"] in DOOR_REFS
        schedule.append(warned({
            "wire_number": row["wire_number"], "sheet": row["sheet"],
            "reference": row["reference"], "terminal": row["terminal"],
            "pin_name": row["pin_name"], "net": row["net"],
            "physical_model": "ENDPOINT RECORD - OPPOSITE END NOT YET FROZEN",
            "conductor_family_candidate": "SELECTION REQUIRED" if door else "Belden 3057 family",
            "gauge_candidate": "SELECTION REQUIRED" if door else "16 AWG / approximately 1.31 mm2",
            "exact_color_order_code": "SELECTION REQUIRED",
            "cut_length_mm": "SELECTION REQUIRED",
            "listed_endpoint_termination": "SELECTION REQUIRED",
            "opposite_endpoint": "SELECTION REQUIRED",
            "opposite_endpoint_termination": "SELECTION REQUIRED",
            "route": "SELECTION REQUIRED",
            "candidate_state": "NO DYNAMIC-FLEX CANDIDATE" if door else "FIXED-INTERNAL GAUGE/FAMILY CANDIDATE ONLY",
            "release_state": "NOT RELEASED",
        }))
    write("endpoint-conductor-candidate-schedule.csv", schedule)

    loads = [
        ("PCS-LOAD-001", "K1/K2", "2 x 5.4 W / 24 V", "0.450 A", "Published steady arithmetic only; pickup, tolerance and duty unverified"),
        ("PCS-LOAD-002", "SR1/SRA1", "2 x 2.5 W / 24 V", "0.208 A", "Published device consumption arithmetic; start/input pulses and installed configuration open"),
        ("PCS-LOAD-003", "KWD1/KWD2", "2 x 18 mA typical", "0.036 A", "Typical, not guaranteed maximum; coil driver and fault states open"),
        ("PCS-LOAD-004", "H1", "0.360 W / 24 V project screen", "0.015 A", "Exact received current/polarity/brightness open; door-loom conductor absent"),
        ("PCS-LOAD-005", "WDPCB1/DC1 reserve", "10 W / 24 V project reserve", "0.417 A", "Not a manufacturer maximum; startup, brownout and fault behavior must be measured"),
        ("PCS-LOAD-006", "screen total", "controlled P0.2 load budget", "1.126 A", "Does not select any conductor or F24; simultaneous pickup and source foldback unverified"),
    ]
    write("load-envelope.csv", [warned({
        "record_id": rid, "load": load, "basis": basis,
        "screened_current": current, "limitation": limit,
    }) for rid, load, basis, current, limit in loads])

    screens = [
        ("PCS-SCREEN-001", "Belden 3057 voltage drop", "NOT CALCULATED", "Exact DCR absent from controlled live record and every cut length is unresolved", "Manufacturer DCR or received-lot four-wire resistance plus frozen route/cut lengths and accepted temperature factor"),
        ("PCS-SCREEN-002", "Fixed-endpoint wire volume", f"{56 * math.pi * (2.3 / 2) ** 2:.1f} mm2 summed circular envelope", "Conservative geometry only; 56 endpoint records are not 56 independently routed point-to-point wires", "Frozen from/to wire list, route allocation, duct occupancy method, bend/service loops and received OD"),
        ("PCS-SCREEN-003", "Door-loom bend/flex", "NOT CALCULATED", "Belden 3057 publishes a 23 mm stationary radius only", "Selected dynamic-flex conductor, door travel model, cycle target, radius/torsion limit, strain relief and cycle test"),
        ("PCS-SCREEN-004", "F24 coordination", "NOT CALCULATED / SELECTION REQUIRED", "Source fault behavior, inrush, route, ambient, bundling, connector and conductor limits remain open", "Measured fault/current-limit behavior, simultaneous inrush, time-current curves, cable lengths, ambient/bundle derating, terminal limits and Boston-qualified review"),
    ]
    write("engineering-screens.csv", [warned({
        "screen_id": rid, "subject": subject, "result": result,
        "why_not_released": why, "closure_evidence_required": evidence,
    }) for rid, subject, result, why, evidence in screens])

    holds = [
        ("PCS-HOLD-001", "from/to topology", "Convert 66 endpoint records into an accepted point-to-point from/to schedule with no implicit splices"),
        ("PCS-HOLD-002", "door loom", "Select dynamic-flex cable/wire; freeze door travel, bend, torsion, abrasion, separation and cycle-life evidence"),
        ("PCS-HOLD-003", "wire colors and order codes", "Qualified electrical reviewer accepts color convention; exact active Belden suffixes or alternate MPNs frozen"),
        ("PCS-HOLD-004", "cut lengths and routes", "Received panel/door geometry, measured routes, service loops, bend radii, duct allocation and cut-list approval"),
        ("PCS-HOLD-005", "termination processes", "Exact direct/ferrule/lug choice per end; accessory MPN, tool/die, strip, torque, inspection and pull-test method"),
        ("PCS-HOLD-006", "DCR and voltage drop", "Controlled DCR/temperature basis or received-lot measurement plus frozen lengths and maximum branch currents"),
        ("PCS-HOLD-007", "ampacity and bundling", "Accepted jurisdictional method, ambient, conductor count, duty, duct fill, enclosure temperature and derating"),
        ("PCS-HOLD-008", "F24 and branch protection", "Measured source/fault/inrush behavior and coordinated fuse/holder/terminal/conductor time-current evidence"),
        ("PCS-HOLD-009", "received terminal identity", "Received markings, range, strip/torque, polarity and terminal accessory reconciliation for every family"),
        ("PCS-HOLD-010", "installed inspection", "Point-to-point, polarity, isolation, torque, pull, labels, separation, cover fit and deviation records"),
        ("PCS-HOLD-011", "thermal/fault testing", "Worst-duty temperature survey plus open/short/cross-short/ground fault injection under controlled authorization"),
        ("PCS-HOLD-012", "qualified release", "Signed electrical and functional-safety review plus separate stage-specific work authorization"),
    ]
    write("unresolved-selection-register.csv", [warned({
        "hold_id": rid, "subject": subject, "state": "SELECTION REQUIRED",
        "evidence_required": evidence, "accepted": "FALSE",
    }) for rid, subject, evidence in holds])

    authority = [
        ("internal source and gauge-fit review", "TRUE", "Digital engineering review only"),
        ("order wire, terminals, ferrules or fuses", "FALSE", "Exact selections and authorization absent"),
        ("cut, strip, crimp, terminate or label", "FALSE", "From/to, length and process release absent"),
        ("install or connect", "FALSE", "Received and inspection evidence absent"),
        ("powered test, motion or energization", "FALSE", "Applicable gates and qualified validation remain open"),
    ]
    write("authority-boundary.csv", [warned({
        "activity": activity, "permitted_by_this_package": permitted, "boundary": boundary,
    }) for activity, permitted, boundary in authority])

    status = {
        "identifier": IDENTIFIER, "round": ROUND, "date": DATE,
        "source_records": len(sources), "endpoint_records": len(schedule),
        "fixed_internal_candidate_endpoints": sum(r["candidate_state"].startswith("FIXED") for r in schedule),
        "door_loom_unselected_endpoints": sum(r["candidate_state"].startswith("NO DYNAMIC") for r in schedule),
        "terminal_family_records": len(terminal_rows), "open_holds": len(holds),
        "point_to_point_schedule_released": False, "wire_order_codes_released": False,
        "cut_lengths_released": False, "termination_process_released": False,
        "f24_selected": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_test_authorized": False,
        "motion_authorized": False, "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    terminal_cards = "".join(
        f'<article><p class="tag">{html.escape(rid)}</p><h2>{html.escape(refs)}</h2>'
        f'<p><strong>{html.escape(disposition)}</strong></p><p>{html.escape(envelope)}</p>'
        f'<p class="hold">{html.escape(remaining)}</p></article>'
        for rid, refs, _family, envelope, _strip, _torque, disposition, remaining in terminal_rows
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 panel conductor basis</title><style>
:root{{--sky:#bfe8ff;--blue:#072a5e;--gold:#f6c445;--paper:#f7fbff;--ink:#10243d;--line:#8fbedd}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.25vw,19px)/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold);padding:clamp(24px,5vw,68px)}}main{{max-width:1180px;margin:auto;padding:28px}}h1{{color:var(--blue);font-size:clamp(34px,6vw,66px);line-height:1.05;margin:.2em 0}}.warning{{background:var(--blue);color:white;padding:16px;border-left:12px solid var(--gold);font-weight:750}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:20px;margin:25px 0}}.metric,article{{background:white;border:2px solid var(--line);border-radius:18px;padding:22px;box-shadow:7px 7px 0 var(--sky)}}.metric b{{display:block;font-size:36px;color:var(--blue)}}.tag{{font-size:14px;font-weight:800;color:var(--blue)}}.hold{{border-left:6px solid var(--gold);padding-left:12px;font-weight:700}}code{{font-size:16px}}footer{{margin-top:30px;font-size:14px}}@media(max-width:480px){{main{{padding:20px}}}}
</style></head><body><header><p class="tag">{ROUND} &middot; {IDENTIFIER}</p><h1>One wire size does not solve the whole panel.</h1><p>A 16 AWG family is a fixed-internal candidate. The moving door loom, every exact color/order code, each cut length, every termination process and all protection remain unresolved.</p></header><main><p class="warning">{WARNING}</p><section class="metrics"><div class="metric"><b>56</b>fixed internal endpoint candidates</div><div class="metric"><b>10</b>door-loom endpoints unselected</div><div class="metric"><b>22 AWG</b>rejected at LC1D25BD controls</div><div class="metric"><b>12</b>open closure holds</div></section><h2>Terminal compatibility is only a gauge screen</h2><section class="grid">{terminal_cards}</section><h2>Why this still is not a wire list</h2><p>The current electrical table identifies 66 device endpoints, not 66 complete point-to-point conductors. The opposite ends, splice policy, physical routes and cut lengths must be frozen from the received panel before a wiring package exists. <code>F24</code> is still <strong>SELECTION REQUIRED</strong>.</p><footer>{WARNING}</footer></main></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"generated {IDENTIFIER}: 56 fixed endpoint candidates; 10 door endpoints unselected; 12 holds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
