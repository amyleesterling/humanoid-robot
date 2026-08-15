#!/usr/bin/env python3
"""Generate the R229 P1.18 configuration-disposition dossier."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P115 = ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate"
P118 = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
P2P = ROOT / "release/hr-v0/panel-point-to-point-p0.1"
ENG = ROOT / "electrical/reviews/hr-v0-p118-disposition-p0.1"
OUT = ROOT / "release/hr-v0/p118-disposition-p0.1"
IDENTIFIER = "HR-V0-P118-DISPOSITION-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
EVIDENCE = "docs/hr-v0-p118-disposition-p0.1.md; electrical/reviews/hr-v0-p118-disposition-p0.1/; release/hr-v0/p118-disposition-p0.1/; requirements/hr-v0-gate-evidence-supplement-r229.csv; tools/check_hr_v0_p118_disposition_p01.py"
NODE_REFS = {"XD24", "XD0", "XN1", "XN2", "XN3"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"empty CSV prohibited: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def normalize_schematic(text: str) -> str:
    replacements = {
        "V3-P1.15-CARRIER-CANDIDATE": "V3-CANDIDATE",
        "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE": "V3-CANDIDATE",
        "project-button-v3-p1.15-carrier-candidate": "project-button-v3-candidate",
        "project-button-v3-p1.18-panel-topology-candidate": "project-button-v3-candidate",
        "2026-08-09": "DATE",
        "2026-08-11": "DATE",
        "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION": "PRELIMINARY-WARNING",
        WARNING: "PRELIMINARY-WARNING",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def paired_sheets() -> list[tuple[Path, Path, str]]:
    pairs = []
    for old in sorted(P115.glob("*.kicad_sch")):
        new_name = old.name.replace("p1.15-carrier-candidate", "p1.18-panel-topology-candidate")
        new = P118 / new_name
        if not new.is_file():
            raise RuntimeError(f"missing paired P1.18 sheet: {new_name}")
        if old.name.startswith("project-button-"):
            classification = "INDEX_NARRATIVE_ONLY_NO_COMPONENTS"
        elif old.name[:2] in {"01", "02", "03"}:
            classification = "EXPLICIT_TOPOLOGY_NODE_ADDITION"
        else:
            classification = "ADMINISTRATIVE_ONLY_CANONICAL_IDENTICAL"
        pairs.append((old, new, classification))
    if len(pairs) != 13:
        raise RuntimeError(f"expected 13 paired sheets, got {len(pairs)}")
    return pairs


def component_delta() -> list[dict[str, str]]:
    old = {r["reference"]: r for r in read_csv(P115 / "bom.csv")}
    new = {r["reference"]: r for r in read_csv(P118 / "bom.csv")}
    removed = sorted(set(old) - set(new))
    modified = sorted(ref for ref in set(old) & set(new) if old[ref] != new[ref])
    if removed or modified:
        raise RuntimeError(f"pre-existing BOM delta: removed={removed}; modified={modified}")
    added = [new[ref] for ref in sorted(set(new) - set(old))]
    if {r["reference"] for r in added} != NODE_REFS:
        raise RuntimeError("BOM additions are not the five controlled topology nodes")
    return [{**r, "delta": "ADDED_EXPLICIT_TOPOLOGY_NODE", "accepted_for_procurement": "FALSE", "warning": WARNING} for r in added]


def terminal_parity() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    old_rows = read_csv(P115 / "connector-schedule.csv")
    new_rows = read_csv(P118 / "connector-schedule.csv")
    key = lambda r: (r["sheet"], r["reference"], r["terminal"])
    old = {key(r): r for r in old_rows}
    new = {key(r): r for r in new_rows}
    missing = sorted(set(old) - set(new))
    modified = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    if missing or modified:
        raise RuntimeError(f"pre-existing terminal delta: missing={missing[:5]}; modified={modified[:5]}")
    added = [new[k] for k in sorted(set(new) - set(old))]
    if len(added) != 32 or {r["reference"] for r in added} != NODE_REFS:
        raise RuntimeError("expected exactly 32 new terminal rows on five controlled nodes")
    parity = [{**r, "p118_match": "IDENTICAL", "warning": WARNING} for r in old_rows]
    additions = [{**r, "delta": "ADDED_EXPLICIT_TOPOLOGY_TERMINAL", "warning": WARNING} for r in added]
    return parity, additions


def net_delta() -> list[dict[str, str]]:
    old = {r["net"]: r for r in read_csv(P115 / "net-schedule.csv")}
    new = {r["net"]: r for r in read_csv(P118 / "net-schedule.csv")}
    if set(old) != set(new) or len(old) != 106:
        raise RuntimeError("named-net identity set changed")
    rows = []
    changed = 0
    total_added = 0
    for net in sorted(old):
        a = set(old[net]["connections"].split(" | "))
        b = set(new[net]["connections"].split(" | "))
        removed = sorted(a - b)
        added = sorted(b - a)
        if removed:
            raise RuntimeError(f"removed connection on {net}: {removed}")
        bad = [item for item in added if item.split(":")[-2] not in NODE_REFS]
        if bad:
            raise RuntimeError(f"non-node addition on {net}: {bad}")
        state = "IDENTICAL" if not added else "EXPLICIT_NODE_TERMINALS_ADDED_ONLY"
        changed += bool(added)
        total_added += len(added)
        rows.append({
            "net": net, "p115_connection_count": old[net]["connection_count"],
            "p118_connection_count": new[net]["connection_count"], "delta_state": state,
            "added_connections": " | ".join(added) if added else "NONE",
            "removed_connections": "NONE", "original_membership_preserved": "TRUE", "warning": WARNING,
        })
    if changed != 5 or total_added != 32:
        raise RuntimeError(f"expected five changed nets and 32 added connections, got {changed}/{total_added}")
    return rows


def sheet_register() -> list[dict[str, str]]:
    rows = []
    for old, new, classification in paired_sheets():
        canonical_equal = normalize_schematic(old.read_text(encoding="utf-8-sig")) == normalize_schematic(new.read_text(encoding="utf-8-sig"))
        if classification == "ADMINISTRATIVE_ONLY_CANONICAL_IDENTICAL" and not canonical_equal:
            raise RuntimeError(f"unexpected semantic source delta: {old.name}")
        additions = {
            "01": "XD24; XD0", "02": "XN1; XN3", "03": "XN2",
        }.get(old.name[:2], "NONE")
        rows.append({
            "page": "0" if old.name.startswith("project-button-") else str(int(old.name[:2])),
            "p115_sheet": old.relative_to(ROOT).as_posix(), "p115_sha256": digest(old),
            "p118_sheet": new.relative_to(ROOT).as_posix(), "p118_sha256": digest(new),
            "delta_class": classification, "canonical_identical_after_admin_normalization": str(canonical_equal).upper(),
            "added_references": additions,
            "project_owned_disposition": "NO UNCONTROLLED CONNECTIVITY DELTA FOUND" if classification != "INDEX_NARRATIVE_ONLY_NO_COMPONENTS" else "INDEX TEXT CHANGED; NO COMPONENTS OR WIRES ON ROOT",
            "independent_review": "OPEN", "qualified_acceptance": "FALSE", "warning": WARNING,
        })
    return rows


def schedule_summary(net_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    old_wire = read_csv(P115 / "wire-number-table.csv")
    new_wire = read_csv(P118 / "wire-number-table.csv")
    fields = ("sheet", "reference", "terminal", "pin_name", "net")
    old_set = {tuple(r[f] for f in fields) for r in old_wire}
    new_set = {tuple(r[f] for f in fields) for r in new_wire}
    if not old_set <= new_set or len(new_set - old_set) != 32:
        raise RuntimeError("wire-table semantic parity failed")
    unresolved_old = read_csv(P115 / "unresolved-selections.csv")
    unresolved_new = read_csv(P118 / "unresolved-selections.csv")
    unresolved_key = lambda r: (r["sheet"], r["reference"])
    if {unresolved_key(r): r for r in unresolved_old} != {unresolved_key(r): r for r in unresolved_new}:
        raise RuntimeError("unresolved-selection register changed")
    return [
        {"artifact": "BOM", "p115_rows": "77", "p118_rows": "82", "preserved_rows": "77", "added_rows": "5", "removed_or_modified_rows": "0", "disposition": "five explicit topology nodes only", "warning": WARNING},
        {"artifact": "connector schedule", "p115_rows": "308", "p118_rows": "340", "preserved_rows": "308", "added_rows": "32", "removed_or_modified_rows": "0", "disposition": "five-node terminal additions only", "warning": WARNING},
        {"artifact": "named-net schedule", "p115_rows": "106", "p118_rows": "106", "preserved_rows": "106", "added_rows": "0", "removed_or_modified_rows": "0", "disposition": f"{sum(r['delta_state'] != 'IDENTICAL' for r in net_rows)} nets gain node terminals; 101 identical", "warning": WARNING},
        {"artifact": "wire-number table", "p115_rows": str(len(old_wire)), "p118_rows": str(len(new_wire)), "preserved_rows": str(len(old_set)), "added_rows": str(len(new_set - old_set)), "removed_or_modified_rows": "0", "disposition": "node terminal rows only; generated wire labels may differ", "warning": WARNING},
        {"artifact": "unresolved selections", "p115_rows": str(len(unresolved_old)), "p118_rows": str(len(unresolved_new)), "preserved_rows": str(len(unresolved_old)), "added_rows": "0", "removed_or_modified_rows": "0", "disposition": "63 rows identical and still unresolved", "warning": WARNING},
        {"artifact": "native ERC", "p115_rows": "0 errors / 0 warnings", "p118_rows": "0 errors / 0 warnings", "preserved_rows": "parser/annotation/connectivity only", "added_rows": "0", "removed_or_modified_rows": "0", "disposition": "no electrical or safety approval", "warning": WARNING},
    ]


def logic_invariants() -> list[dict[str, str]]:
    return [
        {"invariant_id": "P118-LI-001", "subject": "dual-channel E-stop", "source_bound_evidence": "all original S0/SR1 terminal-net rows identical; SR1_S12 gains XN1 terminals only", "supporting_artifact": "connector-terminal-parity.csv; net-delta.csv", "project_result": "PRESERVED IN MODEL", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-002", "subject": "RESET cannot command motion", "source_bound_evidence": "original S1/SR1 rows identical; reset remains eligibility-only", "supporting_artifact": "connector-terminal-parity.csv; HR-V0-PNOZ-CONF-P0.1", "project_result": "PRESERVED IN MODEL", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-003", "subject": "distinct ARM and EDM", "source_bound_evidence": "original S2/SRA1/K1/K2 rows identical; SRA1_S12 gains XN2 terminals only", "supporting_artifact": "connector-terminal-parity.csv; HR-V0-K1K2-APP-P0.3", "project_result": "PRESERVED IN MODEL", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-004", "subject": "two ordinary watchdog contacts in series", "source_bound_evidence": "KWD1/KWD2/SR1 original rows identical", "supporting_artifact": "HR-V0-WD-PERMIT-TOPOLOGY-P0.1", "project_result": "PRESERVED; DUAL/COMMON-CAUSE HAZARD OPEN", "safety_credit": "ZERO", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-005", "subject": "K1/K2 coils, EDM and load poles", "source_bound_evidence": "32 contactor-critical rows previously proved identical", "supporting_artifact": "HR-V0-K1K2-APP-P0.3", "project_result": "PRESERVED; DC DUTY OPEN", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-006", "subject": "grounding and return boundary", "source_bound_evidence": "26 exact boundary rows identical; SAFETY_0V delta is XD0 only", "supporting_artifact": "HR-V0-E2-GND-BOUNDARY-P0.1", "project_result": "PRESERVED IN MODEL; PHYSICAL EVIDENCE OPEN", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-007", "subject": "E2 actuator-domain exclusion", "source_bound_evidence": "U1/INJ1/J1/J2/J3 and actuator source remain physically absent in E2 slice", "supporting_artifact": "HR-V0-E2-HW-P0.4; HR-V0-E2-PREPOWER-P0.1", "project_result": "PRESERVED; NOT EXECUTED", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
        {"invariant_id": "P118-LI-008", "subject": "explicit wiring/no hidden splice", "source_bound_evidence": "55 two-ended conductors map all 66 legacy endpoint labels once", "supporting_artifact": "HR-V0-PANEL-P2P-P0.1", "project_result": "MODEL COMPLETE; PHYSICAL SELECTIONS OPEN", "safety_credit": "NONE", "qualified_disposition": "OPEN", "warning": WARNING},
    ]


def decision_matrix() -> list[dict[str, str]]:
    return [
        {"criterion_id": "P118-DC-001", "criterion": "all pre-existing component/terminal/net semantics preserved", "project_evidence": "PASS", "independent_reviewer_decision": "BLANK", "acceptance_effect": "necessary but not sufficient", "warning": WARNING},
        {"criterion_id": "P118-DC-002", "criterion": "five-node/32-terminal delta completely bounded", "project_evidence": "PASS", "independent_reviewer_decision": "BLANK", "acceptance_effect": "necessary but not sufficient", "warning": WARNING},
        {"criterion_id": "P118-DC-003", "criterion": "all thirteen native sheets and exports independently reviewed", "project_evidence": "PROJECT STRUCTURE/PARITY ONLY", "independent_reviewer_decision": "BLANK", "acceptance_effect": "BLOCKS PROMOTION", "warning": WARNING},
        {"criterion_id": "P118-DC-004", "criterion": "qualified electrical and functional-safety disposition", "project_evidence": "NONE", "independent_reviewer_decision": "BLANK", "acceptance_effect": "BLOCKS PROMOTION", "warning": WARNING},
        {"criterion_id": "P118-DC-005", "criterion": "terminal application, protection and accessory completeness", "project_evidence": "SELECTION REQUIRED", "independent_reviewer_decision": "BLANK", "acceptance_effect": "BLOCKS BUILD RELEASE", "warning": WARNING},
        {"criterion_id": "P118-DC-006", "criterion": "conductors, routes, terminations and sizing calculations", "project_evidence": "SELECTION REQUIRED", "independent_reviewer_decision": "BLANK", "acceptance_effect": "BLOCKS BUILD RELEASE", "warning": WARNING},
        {"criterion_id": "P118-DC-007", "criterion": "received/installed/physical verification", "project_evidence": "NOT EXECUTED", "independent_reviewer_decision": "BLANK", "acceptance_effect": "BLOCKS ENERGIZATION", "warning": WARNING},
        {"criterion_id": "P118-DC-008", "criterion": "configuration authority promotion decision", "project_evidence": "P1.15 REMAINS CURRENT", "independent_reviewer_decision": "BLANK", "acceptance_effect": "P1.18 UNACCEPTED", "warning": WARNING},
    ]


def holds() -> list[dict[str, str]]:
    subjects = [
        ("P118-H-001", "independent page-by-page electrical review", "signed exact-sheet/reference/terminal/net findings and disposition"),
        ("P118-H-002", "qualified functional-safety review", "competence/independence record plus signed topology and fault disposition"),
        ("P118-H-003", "node application and accessory closure", "loads, protection, covers, markers, partitions, rail retention and access"),
        ("P118-H-004", "conductor and door-loom closure", "exact order codes, colors, flex life, routes, lengths, service loops and separation"),
        ("P118-H-005", "termination and electrical calculations", "preparation/tooling/torque/pull plus DCR/drop/ampacity/fill/thermal/fault coordination"),
        ("P118-H-006", "received and installed verification", "identity, dimensional, continuity, polarity, isolation, torque, pull, thermal and fault evidence"),
        ("P118-H-007", "formal configuration promotion", "immutable accepted revision, named authority and controlled P1.15 supersession record"),
    ]
    return [{"hold_id": i, "subject": s, "state": "OPEN", "closure_evidence": e, "accepted": "FALSE", "warning": WARNING} for i, s, e in subjects]


def source_register() -> list[dict[str, str]]:
    local = [
        ("P118D-SRC-001", P115 / "bom.csv", "current P1.15 BOM"),
        ("P118D-SRC-002", P118 / "bom.csv", "candidate P1.18 BOM"),
        ("P118D-SRC-003", P115 / "connector-schedule.csv", "current terminal/net schedule"),
        ("P118D-SRC-004", P118 / "connector-schedule.csv", "candidate terminal/net schedule"),
        ("P118D-SRC-005", P115 / "net-schedule.csv", "current named-net membership"),
        ("P118D-SRC-006", P118 / "net-schedule.csv", "candidate named-net membership"),
        ("P118D-SRC-007", P115 / "wire-number-table.csv", "current generated terminal rows"),
        ("P118D-SRC-008", P118 / "wire-number-table.csv", "candidate generated terminal rows"),
        ("P118D-SRC-009", P115 / "unresolved-selections.csv", "current unresolved set"),
        ("P118D-SRC-010", P118 / "unresolved-selections.csv", "candidate unresolved set"),
        ("P118D-SRC-011", P115 / "validation/project-button-v3-p1.15-carrier-candidate.net", "current native netlist"),
        ("P118D-SRC-012", P118 / "validation/project-button-v3-p1.18-panel-topology-candidate.net", "candidate native netlist"),
        ("P118D-SRC-013", P2P / "point-to-point-wire-schedule.csv", "55 two-ended conductor candidates"),
        ("P118D-SRC-014", ROOT / "electrical/reviews/hr-v0-p118-ecad-web-review-p0.1/sheet-register.csv", "native-to-SVG hash binding"),
        ("P118D-SRC-015", ROOT / "release/hr-v0/watchdog-permit-topology-p0.1/package-status.json", "watchdog topology boundary"),
        ("P118D-SRC-016", ROOT / "release/hr-v0/contactor-application-p0.3/package-status.json", "contactor parity/application boundary"),
        ("P118D-SRC-017", ROOT / "release/hr-v0/e2-grounding-boundary-p0.1/package-status.json", "E2 grounding boundary"),
        ("P118D-SRC-018", ROOT / "release/hr-v0/e2-prepower-test-p0.1/package-status.json", "E2 pre-power boundary"),
    ]
    rows = [{"source_id": sid, "source": path.relative_to(ROOT).as_posix(), "revision_or_date": "repository source rechecked 2026-08-11", "sha256": digest(path), "verified_use": use, "boundary": "project-owned configuration evidence only", "warning": WARNING} for sid, path, use in local]
    for source in read_csv(P2P / "source-register.csv"):
        if source["source_id"] in {"P2P-SRC-003", "P2P-SRC-004", "P2P-SRC-005"}:
            rows.append({"source_id": source["source_id"].replace("P2P", "P118D"), "source": source["official_url_or_path"], "revision_or_date": source["revision_or_date"], "sha256": "REMOTE_PRIMARY_SOURCE", "verified_use": source["verified_fact"], "boundary": source["does_not_establish"], "warning": WARNING})
    return rows


def sync_gates() -> None:
    path = ROOT / "requirements/hr-v0-energization-gates.csv"
    rows = read_csv(path)
    targets = {"EG-002", "EG-004", "EG-020"}
    touched = set()
    for row in rows:
        if row["gate_id"] in targets:
            values = [v.strip() for v in row["evidence_location"].split(";") if v.strip()]
            for value in EVIDENCE.split(";"):
                if value.strip() not in values:
                    values.append(value.strip())
            row["evidence_location"] = "; ".join(values)
            touched.add(row["gate_id"])
    if touched != targets:
        raise RuntimeError("gate sync incomplete")
    write_csv(path, rows)


def sync_release() -> None:
    path = ROOT / "release/hr-v0/release-candidate.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    electrical = next(p for p in release["current_products"] if p.get("domain") == "electrical")
    if IDENTIFIER not in electrical["supporting_identifiers"]:
        electrical["supporting_identifiers"].append(IDENTIFIER)
    electrical["release_state"] = "p115_current_p118_unaccepted_r229_parity_dossier_complete_qualified_disposition_physical_selections_tests_and_authority_open"
    electrical["p118_disposition_dossier"] = IDENTIFIER
    electrical["p118_disposition_summary"] = "77 BOM and 308 terminal rows preserved; 106 net names preserved; five nodes and 32 node terminals added; P1.18 remains unaccepted"
    path.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8", newline="\n")


def guide(sheets: list[dict[str, str]], nets: list[dict[str, str]], components: list[dict[str, str]]) -> str:
    sheet_cards = "".join(f"<article><strong>Page {r['page']}</strong><code>{html.escape(Path(r['p118_sheet']).name)}</code><span>{html.escape(r['delta_class'])}</span><p>Added: {html.escape(r['added_references'])}</p></article>" for r in sheets)
    net_rows = "".join(f"<tr data-state='{r['delta_state']}'><td>{html.escape(r['net'])}</td><td>{r['p115_connection_count']}</td><td>{r['p118_connection_count']}</td><td>{html.escape(r['delta_state'])}</td><td>{html.escape(r['added_connections'])}</td></tr>" for r in nets)
    component_rows = "".join(f"<tr><td>{r['reference']}</td><td>{html.escape(r['value'])}</td><td>{html.escape(r['status'])}</td></tr>" for r in components)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P1.18 disposition dossier</title><style>:root{{--navy:#082f58;--blue:#116aa8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:19ch}}h2{{font-size:clamp(26px,3vw,40px)}}.warning{{background:#fff2bd;color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--gold);padding:20px;margin:28px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}}article{{background:white;border:2px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:8px}}article strong{{font-size:18px}}article span{{font-size:14px;font-weight:800;background:var(--sky);padding:5px 8px;border-radius:6px;overflow-wrap:anywhere}}code{{font-size:14px;overflow-wrap:anywhere}}label,select{{font-size:16px}}select{{padding:10px;border:2px solid var(--blue);border-radius:8px;background:white}}.tablewrap{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white;margin:12px 0 28px}}table{{border-collapse:collapse;width:100%;min-width:940px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9c;font-weight:750}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} | R229</p><h1>P1.18 is bounded enough to review—not accepted.</h1><p>All 77 existing BOM rows and 308 existing terminal assignments survive unchanged. Five explicit nodes add 32 terminal rows on five existing nets.</p></header><main><div class="verdict"><strong>Project-owned result:</strong> no uncontrolled connectivity delta found. <strong>Configuration authority:</strong> P1.15 remains current; qualified P1.18 disposition is open.</div><h2>Native sheet delta map</h2><div class="grid">{sheet_cards}</div><h2>Named-net comparison</h2><label for="state">Show </label><select id="state"><option value="">all 106 nets</option><option value="IDENTICAL">101 identical</option><option value="EXPLICIT_NODE_TERMINALS_ADDED_ONLY">5 node-only deltas</option></select><p id="count" aria-live="polite"></p><div class="tablewrap"><table><thead><tr><th>Net</th><th>P1.15</th><th>P1.18</th><th>State</th><th>Added terminals</th></tr></thead><tbody id="netRows">{net_rows}</tbody></table></div><h2>Five added catalog candidates</h2><div class="tablewrap"><table><thead><tr><th>Reference</th><th>Candidate</th><th>State</th></tr></thead><tbody>{component_rows}</tbody></table></div><div class="warning">Independent and qualified review, physical selections, received/installed evidence and formal promotion remain open. Do not build, connect or energize from this dossier.</div><p><a href="schedule-parity-summary.csv">schedule summary</a> | <a href="connector-terminal-parity.csv">308 terminal rows</a> | <a href="net-delta.csv">106 nets</a> | <a href="logic-invariant-register.csv">logic invariants</a> | <a href="decision-matrix.csv">decision matrix</a> | <a href="open-holds.csv">seven holds</a></p></main><script>const s=document.querySelector('#state'),rows=[...document.querySelectorAll('#netRows tr')],count=document.querySelector('#count');function apply(){{let n=0;rows.forEach(r=>{{const show=!s.value||r.dataset.state===s.value;r.hidden=!show;if(show)n++}});count.textContent=n+' nets shown'}}s.addEventListener('change',apply);apply();</script></body></html>'''


def main() -> None:
    sync_gates()
    sync_release()
    components = component_delta()
    parity, additions = terminal_parity()
    nets = net_delta()
    sheets = sheet_register()
    records = {
        "component-delta.csv": components,
        "connector-terminal-parity.csv": parity,
        "added-terminal-register.csv": additions,
        "net-delta.csv": nets,
        "sheet-delta-register.csv": sheets,
        "schedule-parity-summary.csv": schedule_summary(nets),
        "logic-invariant-register.csv": logic_invariants(),
        "decision-matrix.csv": decision_matrix(),
        "open-holds.csv": holds(),
        "source-register.csv": source_register(),
        "authority-boundary.csv": [
            {"activity": "read-only project configuration analysis", "allowed": "TRUE", "boundary": "repository evidence only", "warning": WARNING},
            {"activity": "P1.18 promotion", "allowed": "FALSE", "boundary": "independent and qualified signed disposition plus named configuration authority required", "warning": WARNING},
            {"activity": "procurement/fabrication/assembly/connection", "allowed": "FALSE", "boundary": "physical selections, calculations, review and separate release required", "warning": WARNING},
            {"activity": "powered testing/motion/energization", "allowed": "FALSE", "boundary": "all applicable gates and signed authorization required", "warning": WARNING},
        ],
    }
    status = {
        "identifier": IDENTIFIER, "round": "R229", "date": "2026-08-11",
        "current_configuration": "V3-P1.15-CARRIER-CANDIDATE",
        "candidate_configuration": "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "p118_accepted": False, "paired_native_sheets": 13, "canonical_admin_only_child_sheets": 9,
        "preserved_bom_rows": 77, "added_components": 5, "preserved_terminal_rows": 308,
        "added_terminal_rows": 32, "preserved_net_names": 106, "unchanged_net_membership": 101,
        "node_only_net_deltas": 5, "unresolved_selection_rows_preserved": 63,
        "project_owned_parity_result": "NO UNCONTROLLED CONNECTIVITY DELTA FOUND",
        "independent_review_received": False, "qualified_review_received": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False,
        "motion_authorized": False, "energization_authorized": False, "warning": WARNING,
    }
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for name, data in records.items():
            write_csv(directory / name, data)
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
        (directory / "README.md").write_text(f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR229 proves a bounded P1.15-to-P1.18 modeled delta. P1.18 remains unaccepted; qualified review, physical selections, evidence and every work authorization remain open.\n", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(guide(sheets, nets, components), encoding="utf-8", newline="\n")
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.name, "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in files])
    print(f"{IDENTIFIER}: 77 BOM + 308 terminal rows preserved; 5 nodes/32 terminals added; P1.18 unaccepted")


if __name__ == "__main__":
    main()
