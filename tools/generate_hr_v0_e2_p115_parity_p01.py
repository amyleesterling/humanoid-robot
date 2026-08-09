#!/usr/bin/env python3
"""Generate P1.14-to-P1.15 watchdog/E2 configuration parity evidence."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "electrical" / "kicad" / "project-button-v3"
CAND = ROOT / "electrical" / "kicad" / "project-button-v3-p1.15-carrier-candidate"
ENG = ROOT / "electrical" / "e2" / "hr-v0-e2-p115-parity-p0.1"
REL = ROOT / "release" / "hr-v0" / "e2-p115-parity-p0.1"
IDENTIFIER = "HR-V0-E2-P115-PARITY-P0.1"
WARNING = (
    "PRELIMINARY - DIGITAL CONFIGURATION PARITY ONLY - NOT APPROVED FOR "
    "FABRICATION, CONNECTION, TEST, MOTION, OR ENERGIZATION"
)
CHANGED_COMMON = {"F1", "F2", "F3", "INJ1", "J1", "J2", "J3"}
ADDED = {"LIM1", "LIM2", "LIM3"}
E2_REFS = {
    "PSU2": "24 V control source",
    "J24": "24 V control-source interface",
    "F24": "unselected 24 V control protection",
    "PSU3": "compute source",
    "S0": "dual-NC emergency stop",
    "S1": "RESET operator",
    "S2": "ARM operator",
    "H1": "diagnostic indicator",
    "SR1": "primary safety relay candidate",
    "SRA1": "secondary safety relay candidate",
    "KWD1": "ordinary watchdog gate relay 1",
    "KWD2": "ordinary watchdog gate relay 2",
    "K1": "actuator interruption contactor 1",
    "K2": "actuator interruption contactor 2",
    "DC1": "watchdog control converter",
    "WDCTRL1": "watchdog controller",
    "UDRV1": "watchdog relay driver 1",
    "UDRV2": "watchdog relay driver 2",
    "UFB1": "watchdog feedback receiver",
    "PI1": "supervisor compute",
    "XT1": "control terminal strip",
    "FSR1": "safety relay protection holder 1",
    "FSR2": "safety relay protection holder 2",
    "TP15": "watchdog SWDIO access",
    "TP16": "watchdog SWCLK access",
    "TP2": "watchdog debug return",
    "SP1": "prohibited project-added 0 V/PE star",
    "JFRAME1": "held frame/shield interface",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def sexpr_blocks(text: str, head: str) -> list[str]:
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*\({re.escape(head)}\s*$", text):
        start = text.find("(", match.start())
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start:index + 1])
                    break
    return blocks


def native_nodes(path: Path) -> tuple[set[str], dict[tuple[str, str], str]]:
    text = path.read_text(encoding="utf-8-sig")
    refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', text))
    result: dict[tuple[str, str], str] = {}
    for block in sexpr_blocks(text, "net"):
        match = re.search(r'\(name "([^"]+)"\)', block)
        if match is None:
            raise RuntimeError("native net without a name")
        net = match.group(1)
        for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            key = (ref, pin)
            if key in result:
                raise RuntimeError(f"duplicate native terminal {ref}:{pin}")
            result[key] = net
    return refs, result


def keyed(data: list[dict[str, str]], keys: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    return {tuple(row[key] for key in keys): row for row in data}


def source_paths() -> dict[str, Path]:
    return {
        "p114_connector_schedule": BASE / "connector-schedule.csv",
        "p115_connector_schedule": CAND / "connector-schedule.csv",
        "p114_bom": BASE / "bom.csv",
        "p115_bom": CAND / "bom.csv",
        "p114_netlist": BASE / "validation" / "project-button-v3.net",
        "p115_netlist": CAND / "validation" / "project-button-v3-p1.15-carrier-candidate.net",
        "p114_erc": BASE / "validation" / "project-button-v3-erc.rpt",
        "p115_erc": CAND / "validation" / "project-button-v3-p1.15-carrier-candidate-erc.rpt",
        "p115_generator": ROOT / "tools" / "generate_hr_v0_electrical_v3_p115_carrier_candidate.py",
    }


def derive() -> dict[str, object]:
    base_connectors = rows(BASE / "connector-schedule.csv")
    cand_connectors = rows(CAND / "connector-schedule.csv")
    base_bom = rows(BASE / "bom.csv")
    cand_bom = rows(CAND / "bom.csv")
    base_refs, base_nodes = native_nodes(BASE / "validation" / "project-button-v3.net")
    cand_refs, cand_nodes = native_nodes(CAND / "validation" / "project-button-v3-p1.15-carrier-candidate.net")

    if cand_refs - base_refs != ADDED or base_refs - cand_refs:
        raise RuntimeError(f"unexpected component membership delta: removed={sorted(base_refs-cand_refs)} added={sorted(cand_refs-base_refs)}")
    shared = base_refs & cand_refs
    unchanged = shared - CHANGED_COMMON
    base_conn = keyed(base_connectors, ("reference", "terminal"))
    cand_conn = keyed(cand_connectors, ("reference", "terminal"))
    base_bom_by_ref = keyed(base_bom, ("reference",))
    cand_bom_by_ref = keyed(cand_bom, ("reference",))

    component_rows: list[dict[str, str]] = []
    terminal_rows: list[dict[str, str]] = []
    for ref in sorted(unchanged):
        base_term = sorted((key, row) for key, row in base_conn.items() if key[0] == ref)
        cand_term = sorted((key, row) for key, row in cand_conn.items() if key[0] == ref)
        if base_term != cand_term:
            raise RuntimeError(f"connector schedule changed outside declared actuator subset: {ref}")
        base_bom_row = base_bom_by_ref.get((ref,))
        cand_bom_row = cand_bom_by_ref.get((ref,))
        if base_bom_row != cand_bom_row:
            raise RuntimeError(f"BOM identity changed outside declared actuator subset: {ref}")
        for key, row in base_term:
            native_base = base_nodes.get(key, "")
            native_cand = cand_nodes.get(key, "")
            if native_base != native_cand:
                raise RuntimeError(f"native net changed outside declared actuator subset: {ref}:{key[1]}")
            terminal_rows.append({
                "reference": ref,
                "terminal": key[1],
                "sheet": row["sheet"],
                "pin_name": row["pin_name"],
                "net": row["net"],
                "native_net_p114": native_base,
                "native_net_p115": native_cand,
                "parity": "EXACT",
                "warning": WARNING,
            })
        component_rows.append({
            "reference": ref,
            "sheet": base_term[0][1]["sheet"] if base_term else "",
            "terminal_count": str(len(base_term)),
            "bom_parity": "EXACT" if base_bom_row is not None else "NOT POPULATED / NON-BOM",
            "schedule_parity": "EXACT",
            "native_net_parity": "EXACT",
            "disposition": "UNCHANGED IN P1.15",
            "warning": WARNING,
        })

    e2_rows: list[dict[str, str]] = []
    for ref, role in E2_REFS.items():
        comp = next((row for row in component_rows if row["reference"] == ref), None)
        if comp is None:
            raise RuntimeError(f"E2 parity reference missing or changed: {ref}")
        e2_rows.append({
            "reference": ref,
            "e2_role": role,
            "terminal_count": comp["terminal_count"],
            "schedule_parity": comp["schedule_parity"],
            "native_net_parity": comp["native_net_parity"],
            "release_effect": "DIGITAL COMPATIBILITY EVIDENCE ONLY",
            "warning": WARNING,
        })

    expected_changes = [
        ("F1", "COMMON_REF_CHANGED", "sheet 06 renamed; output becomes J1_FUSED_PRELIMIT"),
        ("F2", "COMMON_REF_CHANGED", "sheet 06 renamed; output becomes J2_FUSED_PRELIMIT"),
        ("F3", "COMMON_REF_CHANGED", "sheet 06 renamed; output becomes J3_FUSED_PRELIMIT"),
        ("INJ1", "COMMON_REF_CHANGED", "moved to sheet 10; P0.2 identity; positive inputs become J1/J2/J3_LIMITED_VDD"),
        ("J1", "COMMON_REF_CHANGED", "positive terminal becomes J1_LIMITED_VDD"),
        ("J2", "COMMON_REF_CHANGED", "positive terminal becomes J2_LIMITED_VDD"),
        ("J3", "COMMON_REF_CHANGED", "positive terminal becomes J3_LIMITED_VDD"),
        ("LIM1", "ADDED", "P0.3 shoulder branch limiter carrier interface"),
        ("LIM2", "ADDED", "P0.3 elbow branch limiter carrier interface"),
        ("LIM3", "ADDED", "P0.3 gripper branch limiter carrier interface"),
    ]
    change_rows = [{"reference": ref, "change_class": cls, "controlled_change": desc, "e2_power_state": "PHYSICALLY ABSENT OR UNWIRED", "warning": WARNING} for ref, cls, desc in expected_changes]
    return {
        "component_rows": component_rows,
        "terminal_rows": terminal_rows,
        "e2_rows": e2_rows,
        "change_rows": change_rows,
        "base_refs": base_refs,
        "cand_refs": cand_refs,
    }


HOLDS = [
    ("P115-HOLD-001", "PARITY SCOPE", "Digital schedules/netlists do not prove physical wiring, ratings, routing, workmanship or safety performance."),
    ("P115-HOLD-002", "INDEPENDENT REVIEW", "A qualified reviewer has not independently accepted the P1.15 parity argument."),
    ("P115-HOLD-003", "WATCHDOG PCBA", "Current internal CAM exists; supplier-normalized XYRS, process acceptance, fabricated article and first article do not."),
    ("P115-HOLD-004", "RECEIVING", "Installed device identities, terminal markings, contact states and continuity remain unverified."),
    ("P115-HOLD-005", "OPERATOR MAPPING", "RESET, ARM and H1 lot-specific terminal maps remain open."),
    ("P115-HOLD-006", "PROTECTION", "F24, FSR1/FSR2 and actuator protection selections and coordination remain open."),
    ("P115-HOLD-007", "CONDUCTORS", "Wire, termination, routing, segregation, shielding and connector limits remain open."),
    ("P115-HOLD-008", "ENCLOSURE/BONDING", "Enclosure fabrication, entries, touch protection, PE and return/shield implementation remain open."),
    ("P115-HOLD-009", "FIRMWARE/HIL", "Installed firmware, target execution, fault injection and HIL evidence remain absent."),
    ("P115-HOLD-010", "TEST DEFINITION", "Exact instruments, calibration, uncertainty and numerical acceptance limits remain open."),
    ("P115-HOLD-011", "ACTUATOR EXCLUSION", "The E2 physical absence/disconnection boundary has not been inspected or proven dead."),
    ("P115-HOLD-012", "AUTHORIZATION", "No qualified four-role E2 run authorization exists."),
]


def render_page(data: dict[str, object]) -> str:
    e2_rows = data["e2_rows"]
    change_rows = data["change_rows"]
    holds = "".join(f"<li><strong>{html.escape(hid)} - {html.escape(scope)}</strong><span>{html.escape(text)}</span></li>" for hid, scope, text in HOLDS)
    e2_table = "".join(f"<tr><td>{html.escape(row['reference'])}</td><td>{html.escape(row['e2_role'])}</td><td>{html.escape(row['terminal_count'])}</td><td>EXACT</td></tr>" for row in e2_rows)
    changes = "".join(f"<tr><td>{html.escape(row['reference'])}</td><td>{html.escape(row['change_class'])}</td><td>{html.escape(row['controlled_change'])}</td></tr>" for row in change_rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>:root{{--navy:#082f58;--blue:#12669f;--sky:#c8ecff;--gold:#f2b928;--paper:#f7fcff}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.1vw,19px)/1.5 Arial,sans-serif}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#effaff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.2rem,5vw,4.6rem);line-height:1.04;max-width:19ch;margin:.3rem 0 1rem}}h2{{font-size:clamp(1.55rem,3vw,2.5rem)}}main{{max-width:1380px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{background:#fff0b8;border:3px solid #ad7500;border-radius:.8rem;padding:1rem;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:1rem;margin:2rem 0}}article{{border:3px solid var(--blue);border-radius:1rem;padding:1rem;background:var(--paper)}}article b{{display:block;font-size:clamp(2rem,4vw,3.4rem)}}.table-wrap{{overflow:auto;border:2px solid #93b8ce;border-radius:.7rem;margin:1rem 0 2rem}}table{{border-collapse:collapse;width:100%;min-width:860px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #bdd0dc}}th{{background:var(--navy);color:white}}li{{margin:.9rem 0}}li span{{display:block;font-size:14px}}code{{font-size:14px}}a{{color:#075d98}}</style></head><body><header><div>{IDENTIFIER} &middot; R165 &middot; 2026-08-09</div><h1>P1.15 keeps the watchdog and E2 control subset unchanged.</h1><div class="warning">{WARNING}. Exact digital parity is not physical validation or test authorization.</div></header><main><section class="grid"><article><b>{len(data['component_rows'])}</b><span>shared components exactly unchanged</span></article><article><b>{len(data['terminal_rows'])}</b><span>terminals at schedule and native-net parity</span></article><article><b>{len(e2_rows)}</b><span>explicit E2 references at exact parity</span></article><article><b>0</b><span>physical tests or authorizations</span></article></section><h2>Explicit E2 scope</h2><div class="table-wrap"><table><thead><tr><th>Reference</th><th>E2 role</th><th>Terminals</th><th>P1.15 parity</th></tr></thead><tbody>{e2_table}</tbody></table></div><h2>Only the actuator branch subset changes</h2><p>These ten records are the complete declared component membership/change boundary. They remain physically absent or unwired for E2.</p><div class="table-wrap"><table><thead><tr><th>Reference</th><th>Class</th><th>Controlled change</th></tr></thead><tbody>{changes}</tbody></table></div><h2>Twelve holds remain open</h2><ol>{holds}</ol><p><a href="component-parity-register.csv">component parity</a> &middot; <a href="terminal-parity-register.csv">terminal parity</a> &middot; <a href="source-hash-register.csv">source hashes</a></p></main></body></html>'''


def write_package(target: Path, data: dict[str, object]) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    source_rows = [{"source_id": key, "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": str(path.stat().st_size), "warning": WARNING} for key, path in source_paths().items()]
    write_csv(target / "source-hash-register.csv", ["source_id", "path", "sha256", "bytes", "warning"], source_rows)
    write_csv(target / "component-parity-register.csv", ["reference", "sheet", "terminal_count", "bom_parity", "schedule_parity", "native_net_parity", "disposition", "warning"], data["component_rows"])
    write_csv(target / "terminal-parity-register.csv", ["reference", "terminal", "sheet", "pin_name", "net", "native_net_p114", "native_net_p115", "parity", "warning"], data["terminal_rows"])
    write_csv(target / "e2-scope-register.csv", ["reference", "e2_role", "terminal_count", "schedule_parity", "native_net_parity", "release_effect", "warning"], data["e2_rows"])
    write_csv(target / "expected-change-register.csv", ["reference", "change_class", "controlled_change", "e2_power_state", "warning"], data["change_rows"])
    hold_rows = [{"hold_id": hid, "scope": scope, "open_evidence": text, "state": "OPEN", "warning": WARNING} for hid, scope, text in HOLDS]
    write_csv(target / "open-holds.csv", ["hold_id", "scope", "open_evidence", "state", "warning"], hold_rows)
    acceptance = [{"acceptance_id": f"P115-ACCEPT-{index:02d}", "claim": claim, "execution_state": "NOT EXECUTED", "result": "OPEN", "approver": "", "warning": WARNING} for index, claim in enumerate((
        "independent source-hash reproduction", "independent native netlist comparison", "independent schedule comparison", "P1.15 ERC reproduction", "E2 scope review", "actuator-exclusion review", "qualified electrical review", "configuration acceptance"), 1)]
    write_csv(target / "acceptance-matrix.csv", ["acceptance_id", "claim", "execution_state", "result", "approver", "warning"], acceptance)
    status = {
        "identifier": IDENTIFIER,
        "round": "R165",
        "date": "2026-08-09",
        "warning": WARNING,
        "base": "Project Button Electrical V3-P1.14",
        "candidate": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "unchanged_component_refs": len(data["component_rows"]),
        "unchanged_terminal_rows": len(data["terminal_rows"]),
        "explicit_e2_refs": len(data["e2_rows"]),
        "declared_changed_common_refs": len(CHANGED_COMMON),
        "declared_added_refs": len(ADDED),
        "open_holds": len(HOLDS),
        "acceptance_rows": len(acceptance),
        "p114_erc_errors": 0,
        "p114_erc_warnings": 0,
        "p115_erc_errors": 0,
        "p115_erc_warnings": 0,
        "digital_parity_complete": True,
        "independent_review_complete": False,
        "physical_article_exists": False,
        "physical_test_executed": False,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "test_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
    }
    (target / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (target / "README.md").write_text(f"# {IDENTIFIER}\n\n{WARNING}\n\nThis package proves exact schedule and native-net parity for the unchanged P1.14/P1.15 component set and the explicit E2 subset. It does not prove physical construction, suitability, safety performance or authority to energize.\n", encoding="utf-8")
    (target / "index.html").write_text(render_page(data), encoding="utf-8")
    manifest = [{"path": path.relative_to(target).as_posix(), "bytes": str(path.stat().st_size), "sha256": sha256(path)} for path in sorted(p for p in target.rglob("*") if p.is_file() and p.name != "file-manifest.csv")]
    write_csv(target / "file-manifest.csv", ["path", "bytes", "sha256"], manifest)


def main() -> int:
    for path in source_paths().values():
        if not path.is_file():
            raise FileNotFoundError(path)
    for path in (BASE / "validation" / "project-button-v3-erc.rpt", CAND / "validation" / "project-button-v3-p1.15-carrier-candidate-erc.rpt"):
        if "ERC messages: 0  Errors 0  Warnings 0" not in path.read_text(encoding="utf-8-sig"):
            raise RuntimeError(f"native ERC is not zero: {path}")
    data = derive()
    write_package(ENG, data)
    write_package(REL, data)
    print(f"{IDENTIFIER}: {len(data['component_rows'])} unchanged refs / {len(data['terminal_rows'])} terminal rows / {len(data['e2_rows'])} explicit E2 refs")
    print("P1.15 digital parity only; twelve holds OPEN; zero physical or authorization claims")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
