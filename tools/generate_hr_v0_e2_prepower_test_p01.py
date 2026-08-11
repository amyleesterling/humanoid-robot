#!/usr/bin/env python3
"""Generate the R228 configuration-bound E2 pre-power verification candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
P2P = ROOT / "release/hr-v0/panel-point-to-point-p0.1/point-to-point-wire-schedule.csv"
ENG = ROOT / "tests/e2/hr-v0-e2-prepower-test-p0.1"
OUT = ROOT / "release/hr-v0/e2-prepower-test-p0.1"
IDENTIFIER = "HR-V0-E2-PREPOWER-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
GATE_EVIDENCE = "docs/hr-v0-e2-prepower-test-p0.1.md; tests/e2/hr-v0-e2-prepower-test-p0.1/; release/hr-v0/e2-prepower-test-p0.1/; requirements/hr-v0-gate-evidence-supplement-r228.csv; tools/check_hr_v0_e2_prepower_test_p01.py"


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
    target = {"EG-004", "EG-019", "EG-020", "EG-022"}
    touched = set()
    for row in records:
        if row["gate_id"] in target:
            pieces = [item.strip() for item in row["evidence_location"].split(";") if item.strip()]
            for item in GATE_EVIDENCE.split(";"):
                if item.strip() not in pieces:
                    pieces.append(item.strip())
            row["evidence_location"] = "; ".join(pieces)
            touched.add(row["gate_id"])
    if touched != target:
        raise RuntimeError(f"gate sync incomplete: {sorted(touched)}")
    write_csv(path, records)


def sync_release_candidate() -> None:
    path = ROOT / "release/hr-v0/release-candidate.json"
    candidate = json.loads(path.read_text(encoding="utf-8"))
    products = candidate["current_products"]
    electrical = next(item for item in products if item.get("domain") == "electrical")
    commissioning = next(item for item in products if item.get("domain") == "commissioning")
    if IDENTIFIER not in electrical["supporting_identifiers"]:
        electrical["supporting_identifiers"].append(IDENTIFIER)
    electrical["release_state"] = "p115_current_p118_unaccepted_e2_grounding_and_prepower_candidates_bound_zero_limits_results_or_authority_k1k2_dc_application_protection_and_qualified_acceptance_open"
    electrical["e2_prepower_test_candidate"] = IDENTIFIER
    electrical["e2_prepower_configuration_binding"] = "55 P1.18 conductor rows; 45 fixed-internal method candidates; 10 blocked door rows; zero released limits or results"
    if IDENTIFIER not in commissioning["supporting_identifiers"]:
        commissioning["supporting_identifiers"].insert(3, IDENTIFIER)
    commissioning["release_state"] = "e2_grounding_and_prepower_candidates_controlled_zero_limits_results_or_authority_not_authorized_for_connection_or_energization"
    commissioning["prepower_test_candidate"] = IDENTIFIER
    path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")


def source_register() -> list[dict[str, str]]:
    local = [
        ("E2PT-SRC-001", P2P, "all 55 unaccepted P1.18 physical-conductor candidates"),
        ("E2PT-SRC-002", ROOT / "release/hr-v0/panel-point-to-point-p0.1/package-status.json", "P1.18/P1.15 authority and open-selection boundary"),
        ("E2PT-SRC-003", P115 / "connector-schedule.csv", "current endpoint/net identities"),
        ("E2PT-SRC-004", P115 / "net-schedule.csv", "current named-net membership"),
        ("E2PT-SRC-005", P118 / "connector-schedule.csv", "unaccepted physical-topology endpoint identities"),
        ("E2PT-SRC-006", ROOT / "electrical/e2/hr-v0-e2-hardware-p0.4/e2-configuration-slice.csv", "exact E2 installed/absent/DNP states"),
        ("E2PT-SRC-007", ROOT / "docs/hr-v0-e2-grounding-boundary-p0.1.md", "R227 external-adapter/ELV-only boundary"),
        ("E2PT-SRC-008", ROOT / "electrical/grounding/hr-v0-e2-grounding-boundary-p0.1/boundary-register.csv", "R227 boundary items"),
        ("E2PT-SRC-009", ROOT / "tests/e2/hr-v0-e2-control-only-sequence.csv", "current E2 phase/abort sequence"),
        ("E2PT-SRC-010", ROOT / "tests/forms/hr-v0-e2-elv-point-to-point-template.csv", "existing one-row generic form retained as historical-name evidence shell"),
        ("E2PT-SRC-011", ROOT / "tests/forms/hr-v0-e2-mains-pe-insulation-template.csv", "existing site/PE/insulation evidence shell"),
        ("E2PT-SRC-012", ROOT / "tests/e2/hr-v0-e2-evidence-contract-p0.2/form-sha256-register.csv", "current form contract; not modified by this candidate"),
    ]
    rows = [{"source_id": sid, "source": p.relative_to(ROOT).as_posix(), "revision_or_date": "repository source rechecked 2026-08-11", "sha256": digest(p), "verified_use": use, "boundary": "configuration/test-definition evidence only; no executed result or acceptance", "warning": WARNING} for sid, p, use in local]
    remote = [
        ("E2PT-SRC-013", "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.333", "29 CFR 1910.333 current page rechecked 2026-08-11", "qualified-person test of exposed circuit elements plus induced/backfeed verification; applicability determined by qualified reviewer", "does not supply Project Button limits or authorization"),
        ("E2PT-SRC-014", "https://www.fluke.com/en-us/learn/blog/electrical/absence-of-voltage-testing", "current manufacturer guidance rechecked 2026-08-11", "live-dead-live principle and warning that visual/LOTO state alone is insufficient", "manufacturer guidance is not a substitute for applicable law or site procedure"),
        ("E2PT-SRC-015", "https://www.keysight.com/us/en/product/U1282A/handheld-digital-multimeter-4-5-digit-ip67.html", "current product page rechecked 2026-08-11", "U1282A exact candidate: DCV, two-wire resistance, continuity, 60,000 counts, CAT III 1000 V/CAT IV 600 V", "exact calibration option, leads, proving reference, connected-electronics suitability and procurement remain open"),
        ("E2PT-SRC-016", "https://www.keysight.com/us/en/assets/7018-04867/data-sheets/5992-0847.pdf", "U1280 data sheet portal updated 2024-06-07; rechecked 2026-08-11", "0.025 percent basic DCV and 60,000-count family screen", "catalog performance is not executed uncertainty or calibration evidence"),
    ]
    rows.extend({"source_id": sid, "source": source, "revision_or_date": revision, "sha256": "REMOTE_PRIMARY_SOURCE", "verified_use": use, "boundary": boundary, "warning": WARNING} for sid, source, revision, use, boundary in remote)
    return rows


def wire_plan() -> list[dict[str, str]]:
    rows = []
    for i, source in enumerate(read_csv(P2P), 1):
        blocked = source["candidate_state"] == "NO DYNAMIC-FLEX CANDIDATE"
        rows.append({
            "test_id": f"E2PT-W-{i:03d}", "wire_id": source["wire_id"], "net": source["net"],
            "from_endpoint": f"{source['from_reference']}:{source['from_terminal']}",
            "to_endpoint": f"{source['to_reference']}:{source['to_terminal']}",
            "test_setup": "both conductor ends disconnected; all sources removed; stored energy discharged",
            "method": "BLOCKED - exact conductor/terminal unresolved" if blocked else "lead-compensated low-energy two-wire resistance plus end-to-end identity check",
            "numeric_limit": "SELECTION REQUIRED after exact cut length, conductor, termination and instrument uncertainty",
            "expected_result": "correct endpoints; continuous inside approved limit; no continuity to any non-net conductor",
            "candidate_class": "DOOR_CONDUCTOR_BLOCKED" if blocked else "FIXED_INTERNAL_METHOD_CANDIDATE",
            "execution_state": "NOT_EXECUTED", "measured_value": "BLANK", "evidence_uri": "BLANK", "accepted": "FALSE", "warning": WARNING,
        })
    return rows


def isolation_plan() -> list[dict[str, str]]:
    pairs = [
        ("SAFETY_24V", "SAFETY_0V", "control-domain opposite conductors"),
        ("SAFETY_24V", "COMPUTE_5V", "control-to-compute positive domains"),
        ("SAFETY_24V", "COMPUTE_0V", "control positive to compute return"),
        ("SAFETY_0V", "COMPUTE_5V", "control return to compute positive"),
        ("SAFETY_0V", "COMPUTE_0V", "independent returns; ISO1 is not a conductive bridge"),
        ("SAFETY_24V", "ROBOT_FRAME", "control positive to frame placeholder"),
        ("SAFETY_0V", "ROBOT_FRAME", "control return to frame placeholder"),
        ("COMPUTE_5V", "ROBOT_FRAME", "compute positive to frame placeholder"),
        ("COMPUTE_0V", "ROBOT_FRAME", "compute return to frame placeholder"),
        ("CABLE_SHIELD_TERM", "ROBOT_FRAME", "two JFRAME1 placeholders; JFRAME1 DNP"),
        ("SAFETY_0V", "CABLE_SHIELD_TERM", "control return to shield placeholder"),
        ("COMPUTE_0V", "CABLE_SHIELD_TERM", "compute return to shield placeholder"),
        ("ACT_0V_PE_BONDED", "COMPUTE_0V", "U1 and actuator network physically absent at E2"),
        ("ACT_0V_PE_BONDED", "SAFETY_0V", "actuator domain physically absent at E2"),
        ("ACT_12V_RAW", "SAFETY_24V", "actuator source/domain physically absent"),
        ("INTENTIONALLY_NOT_CONNECTED_SP1_A", "INTENTIONALLY_NOT_CONNECTED_SP1_B", "SP1 DNP/prohibited"),
    ]
    return [{"test_id": f"E2PT-I-{i:03d}", "node_a": a, "node_b": b, "rationale": why, "setup": "all sources removed; affected electronics and intentional parallel paths disconnected; test voltage/current approved before probing", "method": "low-energy resistance/isolation screen; high-voltage insulation test prohibited", "numeric_limit": "SELECTION REQUIRED", "expected_result": "no unintended conductive path", "execution_state": "NOT_EXECUTED", "measured_value": "BLANK", "evidence_uri": "BLANK", "accepted": "FALSE", "warning": WARNING} for i, (a, b, why) in enumerate(pairs, 1)]


def no_backfeed_plan() -> list[dict[str, str]]:
    rows = [
        ("E2PT-B-001", "SAFETY_24V downstream", "J24:1 upstream", "F24 boundary", "reverse feed toward external control adapter"),
        ("E2PT-B-002", "COMPUTE_5V", "SAFETY_24V", "ISO1/JWH1 boundary", "compute supply must not energize control positive"),
        ("E2PT-B-003", "SAFETY_24V", "COMPUTE_5V", "ISO1/JWH1 boundary", "control supply must not energize compute positive"),
        ("E2PT-B-004", "COMPUTE_0V", "SAFETY_0V", "ISO1 boundary", "returns remain conductively separated in accepted assembly"),
        ("E2PT-B-005", "SAFETY_24V", "ACT_12V_RAW", "physically absent actuator domain", "control source cannot create actuator-source voltage"),
        ("E2PT-B-006", "COMPUTE_5V", "DXL_TTL_DATA/ACT_0V", "U1 absent", "compute source cannot reach absent actuator interface"),
        ("E2PT-B-007", "J1_LIMITED_VDD", "J2_LIMITED_VDD", "three absent branch carriers/star interfaces", "one branch cannot energize another"),
        ("E2PT-B-008", "J1/J2/J3 VDD", "ACT_12V_BUS", "absent/disconnected actuator plugs", "load-side injection cannot backfeed main bus"),
    ]
    return [{"test_id": i, "stimulus_domain": source, "observe_domain": observe, "boundary": boundary, "hazard": hazard, "stimulus_voltage_v": "SELECTION REQUIRED", "current_limit_a": "SELECTION REQUIRED", "method": "PROHIBITED until exact electronics-safe fixture and limits are qualified", "expected_result": "no hazardous or unintended backfeed", "execution_state": "NOT_EXECUTED", "measured_value": "BLANK", "evidence_uri": "BLANK", "accepted": "FALSE", "warning": WARNING} for i, source, observe, boundary, hazard in rows]


def voltage_plan() -> list[dict[str, str]]:
    rows = [
        ("E2PT-V-001", "J24:1", "J24:3", "control inlet"),
        ("E2PT-V-002", "XD24:LINE", "XD0:LINE", "control distribution"),
        ("E2PT-V-003", "JWP1:1", "JWP1:2", "watchdog PCB power inlet"),
        ("E2PT-V-004", "PI1:USB-C-VBUS", "PI1:USB-C-GND", "compute input"),
        ("E2PT-V-005", "JA1:1", "JA1:4", "actuator source interface; physically absent"),
        ("E2PT-V-006", "F0:1", "ACT_0V_PE_BONDED", "actuator source feed; physically absent"),
        ("E2PT-V-007", "SD1:TBD-OUT", "ACT_0V_PE_BONDED", "service disconnect output; physically absent"),
        ("E2PT-V-008", "KP1:1L1", "ACT_0V_PE_BONDED", "K1 load input; unsourced/unwired"),
        ("E2PT-V-009", "KP2:6T3", "ACT_0V_PE_BONDED", "actuator bus output; unsourced/unwired"),
        ("E2PT-V-010", "F1/F2/F3:1", "ACT_0V_PE_BONDED", "branch inputs; physically absent"),
        ("E2PT-V-011", "J1/J2/J3:2", "J1/J2/J3:1", "actuator interfaces; physically absent"),
        ("E2PT-V-012", "panel metalwork", "each ELV return", "unintended voltage to exposed conductive parts"),
    ]
    return [{"test_id": i, "positive_point": pos, "reference_point": ref, "purpose": purpose, "precondition": "sources unplugged/removed; stored-energy wait complete; qualified person; accepted meter and proving reference", "sequence": "prove meter on accepted same-type/magnitude reference; test point; re-prove meter", "absence_threshold_v": "SELECTION REQUIRED", "expected_result": "below approved absence threshold or independently witnessed physical absence where point is not installed", "execution_state": "NOT_EXECUTED", "measured_value": "BLANK", "evidence_uri": "BLANK", "accepted": "FALSE", "warning": WARNING} for i, pos, ref, purpose in rows]


def instrument_register() -> list[dict[str, str]]:
    rows = [
        ("E2PT-M-001", "ELV DMM candidate", "Keysight U1282A", "DCV, two-wire resistance, continuity; 60,000 counts; CAT III 1000 V/CAT IV 600 V", "exact calibration option/certificate, test leads, burden/test energy, uncertainty and availability"),
        ("E2PT-M-002", "voltage proving reference", "SELECTION REQUIRED", "known stable AC/DC source at accepted type and representative magnitude", "exact source, traceability, output limits and safe connection fixture"),
        ("E2PT-M-003", "site receptacle/PE equipment", "SELECTION REQUIRED BY QUALIFIED ELECTRICIAN", "appropriate to exact Boston receptacle/branch and applicable procedure", "exact instruments, ratings, calibration, method and limits"),
        ("E2PT-M-004", "low-energy isolation fixture", "SELECTION REQUIRED", "electronics-safe open-circuit voltage/current with protected pin probes", "exact source/resistor/protection values and every connected-device limit"),
        ("E2PT-M-005", "evidence capture", "SELECTION REQUIRED", "raw reading export or photographed display with point identity and timestamp", "data-integrity, clock, operator, calibration and evidence-hash procedure"),
    ]
    return [{"instrument_id": i, "role": role, "candidate": candidate, "verified_capability": capability, "closure_evidence": evidence, "selection_state": "EXACT CANDIDATE HOLD" if candidate == "Keysight U1282A" else "SELECTION REQUIRED", "accepted": "FALSE", "warning": WARNING} for i, role, candidate, capability, evidence in rows]


def prohibition_register() -> list[dict[str, str]]:
    rows = [
        ("E2PT-P-001", "megohmmeter/hipot across any connected PCB, Pi, relay, contactor coil, indicator, adapter output or USB interface", "PROHIBITED", "component damage and invalid system-level inference"),
        ("E2PT-P-002", "insulation test applied to either sealed factory adapter", "PROHIBITED", "use manufacturer/certification/received-condition evidence unless qualified procedure expressly permits otherwise"),
        ("E2PT-P-003", "continuity beeper used as a quantitative resistance acceptance", "PROHIBITED", "audible threshold is not the selected loop-corrected resistance limit"),
        ("E2PT-P-004", "non-contact voltage indication used as absence-of-voltage proof", "PROHIBITED", "indicator cannot replace direct qualified measurement"),
        ("E2PT-P-005", "no-backfeed injection before voltage/current/energy and connection fixture are qualified", "PROHIBITED", "uncontrolled injection may damage or energize a domain"),
        ("E2PT-P-006", "source connection based only on visual inspection, checker output or blank form", "PROHIBITED", "executed evidence and signed authorization are required"),
    ]
    return [{"rule_id": i, "activity": activity, "state": state, "reason": reason, "override": "configuration-specific qualified written procedure only; no repository artifact grants override", "warning": WARNING} for i, activity, state, reason in rows]


def holds() -> list[dict[str, str]]:
    rows = [
        ("E2PT-H-001", "P1.18 disposition", "independent review and formal acceptance/correction of exact physical topology"),
        ("E2PT-H-002", "ten door conductors", "exact terminals, dynamic-flex conductor, routing, protection and terminations"),
        ("E2PT-H-003", "45 fixed conductors", "exact color/order code, cut length, route and terminations"),
        ("E2PT-H-004", "continuity limits", "length/material/termination model plus lead compensation and uncertainty"),
        ("E2PT-H-005", "isolation limits", "electronics-safe test voltage/current and accepted numeric threshold for each state"),
        ("E2PT-H-006", "no-backfeed fixture", "isolated source, protection, injection values, observation points and fault controls"),
        ("E2PT-H-007", "absence threshold", "qualified numeric AC/DC threshold tied to meter accuracy/noise and hazard basis"),
        ("E2PT-H-008", "instrument set", "exact instruments/leads/proving source/calibration/uncertainty and received condition"),
        ("E2PT-H-009", "physical execution", "completed raw readings, photos, hashes, nonconformance closure and witness"),
        ("E2PT-H-010", "qualified authorization", "electrical and functional-safety acceptance plus configuration-specific EG-022 signatures"),
    ]
    return [{"hold_id": i, "subject": subject, "state": "OPEN", "closure_evidence": evidence, "accepted": "FALSE", "warning": WARNING} for i, subject, evidence in rows]


def guide(wires: list[dict[str, str]], isolation: list[dict[str, str]], voltage: list[dict[str, str]]) -> str:
    wire_rows = "".join(f"<tr data-kind='{html.escape(r['candidate_class'])}'><td>{r['test_id']}</td><td>{r['wire_id']}</td><td>{html.escape(r['net'])}</td><td>{html.escape(r['from_endpoint'])}</td><td>{html.escape(r['to_endpoint'])}</td><td>{html.escape(r['candidate_class'])}</td></tr>" for r in wires)
    iso_rows = "".join(f"<tr><td>{r['test_id']}</td><td>{html.escape(r['node_a'])}</td><td>{html.escape(r['node_b'])}</td><td>{html.escape(r['numeric_limit'])}</td></tr>" for r in isolation)
    volt_rows = "".join(f"<article><strong>{r['test_id']}</strong><code>{html.escape(r['positive_point'])} → {html.escape(r['reference_point'])}</code><p>{html.escape(r['purpose'])}</p><span>threshold: SELECTION REQUIRED</span></article>" for r in voltage)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 E2 pre-power test</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8;--hold:#fff2bd}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(26px,3vw,40px)}}.warning{{background:var(--hold);color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}label,select{{font-size:16px}}select{{padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}}article{{background:white;border:2px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:8px}}article strong{{font-size:18px}}article span{{font-size:14px;font-weight:850;background:var(--sky);padding:5px 8px;border-radius:6px}}code{{font-size:14px;overflow-wrap:anywhere}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white;margin:12px 0 28px}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9c;font-weight:750}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} | R228</p><h1>Every proposed wire now has a pre-power test row.</h1><p>Fifty-five P1.18 conductor candidates are mapped. Forty-five are fixed-internal method candidates; ten remain blocked door conductors. No numeric limit or test result is invented.</p></header><main><div class="verdict"><strong>Configuration-complete candidate:</strong> 55 continuity rows, 16 isolation pairs, eight no-backfeed cases and twelve absence-of-voltage points. <strong>Authority:</strong> zero.</div><h2>Point-to-point continuity plan</h2><label for="kind">Show </label><select id="kind"><option value="">all 55 rows</option><option value="FIXED_INTERNAL_METHOD_CANDIDATE">45 fixed-internal</option><option value="DOOR_CONDUCTOR_BLOCKED">10 blocked door</option></select><p id="count" aria-live="polite"></p><div class="tablewrap"><table><thead><tr><th>Test</th><th>Wire</th><th>Net</th><th>From</th><th>To</th><th>State</th></tr></thead><tbody id="wireRows">{wire_rows}</tbody></table></div><h2>Critical isolation pairs</h2><div class="tablewrap"><table><thead><tr><th>Test</th><th>Node A</th><th>Node B</th><th>Limit</th></tr></thead><tbody>{iso_rows}</tbody></table></div><h2>Absence-of-voltage points</h2><div class="grid">{volt_rows}</div><div class="warning">P1.18 remains unaccepted. All resistance, isolation, injection and absence thresholds remain SELECTION REQUIRED. EG-004/019/020/022 remain PARTIAL. Do not connect a source.</div><p><a href="wire-continuity-plan.csv">55 wire rows</a> | <a href="isolation-plan.csv">isolation</a> | <a href="no-backfeed-plan.csv">no-backfeed</a> | <a href="absence-of-voltage-plan.csv">voltage points</a> | <a href="instrument-register.csv">instruments</a> | <a href="prohibition-register.csv">prohibitions</a> | <a href="open-holds.csv">10 holds</a></p></main><script>const s=document.querySelector('#kind'),rows=[...document.querySelectorAll('#wireRows tr')],count=document.querySelector('#count');function apply(){{let n=0;rows.forEach(r=>{{const show=!s.value||r.dataset.kind===s.value;r.hidden=!show;if(show)n++}});count.textContent=n+' rows shown'}}s.addEventListener('change',apply);apply();</script></body></html>'''


def main() -> None:
    sync_gates()
    sync_release_candidate()
    wires, isolation, backfeed, voltage = wire_plan(), isolation_plan(), no_backfeed_plan(), voltage_plan()
    instruments, prohibitions, hold_rows, sources = instrument_register(), prohibition_register(), holds(), source_register()
    authority = [
        {"activity": "read-only engineering/configuration review", "permitted": "TRUE", "boundary": "repository and current primary-source evidence only", "warning": WARNING},
        {"activity": "unpowered probing", "permitted": "FALSE", "boundary": "exact accepted configuration, qualified method, instruments, limits and written work authority required", "warning": WARNING},
        {"activity": "no-backfeed injection", "permitted": "FALSE", "boundary": "fixture and every stimulus limit unresolved", "warning": WARNING},
        {"activity": "source connection/powered testing/motion", "permitted": "FALSE", "boundary": "all applicable gates and EG-022 authorization remain unresolved", "warning": WARNING},
    ]
    status = {
        "identifier": IDENTIFIER, "round": "R228", "date": "2026-08-11",
        "current_electrical": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "test_target_candidate": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "p118_accepted": False,
        "wire_rows": len(wires), "fixed_internal_rows": sum(r["candidate_class"].startswith("FIXED") for r in wires),
        "blocked_door_rows": sum(r["candidate_class"].startswith("DOOR") for r in wires),
        "isolation_rows": len(isolation), "no_backfeed_rows": len(backfeed), "absence_voltage_rows": len(voltage),
        "open_holds": len(hold_rows), "numeric_limits_released": 0, "executed_results": 0,
        "eg_004_status": "partial", "eg_019_status": "partial", "eg_020_status": "partial", "eg_022_status": "partial",
        "physical_tests_executed": False, "qualified_review_received": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False,
        "warning": WARNING,
    }
    records = {
        "wire-continuity-plan.csv": wires, "isolation-plan.csv": isolation, "no-backfeed-plan.csv": backfeed,
        "absence-of-voltage-plan.csv": voltage, "instrument-register.csv": instruments,
        "prohibition-register.csv": prohibitions, "open-holds.csv": hold_rows, "source-register.csv": sources,
        "authority-boundary.csv": authority,
    }
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, data in records.items():
            write_csv(directory / name, data)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR228 maps all 55 unaccepted P1.18 conductor candidates into a fail-closed pre-power verification plan. Ten door conductors, every numeric limit, all physical results and qualified authorization remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(wires, isolation, voltage), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENTIFIER}: 55 wires; 16 isolation; 8 backfeed; 12 voltage; 10 holds; zero authority")


if __name__ == "__main__":
    main()
