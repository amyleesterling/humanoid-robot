#!/usr/bin/env python3
"""Validate P1.20 source parity and the R232 disposition package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P119 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.19-visual-correction-candidate"
P120 = ROOT / "electrical" / "kicad" / "project-button-v3-p1.20-watchdog-interlock-candidate"
OUT = ROOT / "release" / "hr-v0" / "p120-watchdog-interlock-p0.1"
ENG = ROOT / "electrical" / "reviews" / "hr-v0-p120-watchdog-interlock-p0.1"
DOC = ROOT / "docs" / "hr-v0-p120-watchdog-interlock-p0.1.md"
REQUEST = ROOT / "docs" / "reviews" / "2026-08-11-r232-independent-review-request.md"
SUPPLEMENT = ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r232.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def keyed(records: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    return {(r["sheet"], r["reference"], r["terminal"]): r for r in records}


def parse_sexp(path: Path) -> list[object]:
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', path.read_text(encoding="utf-8-sig"))
    stack: list[list[object]] = []
    root: list[object] = []
    current = root
    for token in tokens:
        if token == "(":
            child: list[object] = []
            current.append(child)
            stack.append(current)
            current = child
        elif token == ")":
            current = stack.pop()
        else:
            current.append(json.loads(token) if token.startswith('"') else token)
    need(not stack, f"unbalanced native netlist S-expression: {path}")
    return root[0]


def children(block: list[object], name: str) -> list[list[object]]:
    return [item for item in block[1:] if isinstance(item, list) and item and item[0] == name]


def field(block: list[object], name: str) -> str:
    matches = children(block, name)
    return str(matches[0][1]) if matches and len(matches[0]) > 1 else ""


def canonical_netlist(path: Path) -> dict[str, object]:
    root = parse_sexp(path)
    component_sections = children(root, "components")
    net_sections = children(root, "nets")
    need(len(component_sections) == len(net_sections) == 1, f"native netlist sections missing: {path}")
    components = {
        field(comp, "ref"): {"value": field(comp, "value"), "footprint": field(comp, "footprint")}
        for comp in children(component_sections[0], "comp")
    }
    nets = {}
    for net in children(net_sections[0], "net"):
        nets[field(net, "name")] = sorted(
            (field(node, "ref"), field(node, "pin"), field(node, "pinfunction"), field(node, "pintype"))
            for node in children(net, "node")
        )
    return {"components": components, "nets": nets}


def main() -> None:
    erc = (P120 / "validation" / "project-button-v3-p1.20-watchdog-interlock-candidate-erc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "P1.20 ERC is not 0/0")
    need(len(list(P120.glob("*.kicad_sch"))) == 13, "P1.20 native sheet count changed")
    old_bom, new_bom = rows(P119 / "bom.csv"), rows(P120 / "bom.csv")
    need(len(old_bom) == len(new_bom) == 82, "BOM count changed")
    old_identity = {(r["reference"], r["value"], r["quantity"]) for r in old_bom}
    new_identity = {(r["reference"], r["value"], r["quantity"]) for r in new_bom}
    need(old_identity == new_identity, "component identity or quantity changed")
    old_conn, new_conn = keyed(rows(P119 / "connector-schedule.csv")), keyed(rows(P120 / "connector-schedule.csv"))
    need(old_conn.keys() == new_conn.keys() and len(new_conn) == 340, "terminal identity/count changed")
    changed = {key: (old_conn[key]["net"], new_conn[key]["net"]) for key in old_conn if old_conn[key]["net"] != new_conn[key]["net"]}
    expected = {
        ("02_estop_eligibility.kicad_sch","SR1","A1"):("SR1_A1_WD_GATED","SAFETY_24V"),
        ("02_estop_eligibility.kicad_sch","SR1","14"):("SRA1_S12","SR1_OUT1_TO_KWD1"),
        ("02_estop_eligibility.kicad_sch","SR1","24"):("SRA1_S22","SR1_OUT2_TO_KWD2"),
        ("03_arm_watchdog_eligibility.kicad_sch","KWD1","11"):("SAFETY_24V","SR1_OUT1_TO_KWD1"),
        ("03_arm_watchdog_eligibility.kicad_sch","KWD1","14"):("WD_SUPPLY_INTERMEDIATE","SRA1_S12"),
        ("03_arm_watchdog_eligibility.kicad_sch","KWD2","11"):("WD_SUPPLY_INTERMEDIATE","SR1_OUT2_TO_KWD2"),
        ("03_arm_watchdog_eligibility.kicad_sch","KWD2","14"):("SR1_A1_WD_GATED","SRA1_S22"),
    }
    need(changed == expected, f"unexpected terminal/net delta: {changed}")
    for ref in ("S0","S1","S2","SRA1","K1","K2","FSR1","FSR2"):
        before = {(k[2], old_conn[k]["net"]) for k in old_conn if k[1] == ref}
        after = {(k[2], new_conn[k]["net"]) for k in new_conn if k[1] == ref}
        need(before == after, f"protected unchanged reference changed: {ref}")
    old_nets = {r["net"]:r for r in rows(P119 / "net-schedule.csv")}
    new_nets = {r["net"]:r for r in rows(P120 / "net-schedule.csv")}
    need(len(old_nets) == len(new_nets) == 106, "named-net count changed")
    need(set(old_nets)-set(new_nets) == {"SR1_A1_WD_GATED","WD_SUPPLY_INTERMEDIATE"}, "removed-net set changed")
    need(set(new_nets)-set(old_nets) == {"SR1_OUT1_TO_KWD1","SR1_OUT2_TO_KWD2"}, "added-net set changed")
    need(len(rows(P119 / "wire-number-table.csv")) == len(rows(P120 / "wire-number-table.csv")) == 301, "wire-table count changed")
    need(len(rows(P119 / "unresolved-selections.csv")) == len(rows(P120 / "unresolved-selections.csv")) == 63, "unresolved-selection count changed")
    old_native = canonical_netlist(P119 / "validation/project-button-v3-p1.19-visual-correction-candidate.net")
    new_native = canonical_netlist(P120 / "validation/project-button-v3-p1.20-watchdog-interlock-candidate.net")
    need(old_native["components"] == new_native["components"], "native netlist component/value/footprint identity changed")
    need(len(old_native["components"]) == 84, "native netlist component count changed")
    changed_native = {
        name: (old_native["nets"].get(name), new_native["nets"].get(name))
        for name in sorted(set(old_native["nets"]) | set(new_native["nets"]))
        if old_native["nets"].get(name) != new_native["nets"].get(name)
    }
    need(
        set(changed_native) == {
            "SAFETY_24V", "SR1_A1_WD_GATED", "SR1_OUT1_TO_KWD1", "SR1_OUT2_TO_KWD2",
            "SRA1_S12", "SRA1_S22", "WD_SUPPLY_INTERMEDIATE",
        },
        f"unexpected native net membership delta: {set(changed_native)}",
    )
    def node_keys(nodes: list[tuple[str, str, str, str]] | None) -> set[tuple[str, str]]:
        return {(node[0], node[1]) for node in (nodes or [])}
    expected_native_node_delta = {
        "SAFETY_24V": ({("KWD1", "11")}, {("SR1", "A1")}),
        "SR1_A1_WD_GATED": ({("KWD2", "14"), ("SR1", "A1")}, set()),
        "SR1_OUT1_TO_KWD1": (set(), {("KWD1", "11"), ("SR1", "14")}),
        "SR1_OUT2_TO_KWD2": (set(), {("KWD2", "11"), ("SR1", "24")}),
        "SRA1_S12": ({("SR1", "14")}, {("KWD1", "14")}),
        "SRA1_S22": ({("SR1", "24")}, {("KWD2", "14")}),
        "WD_SUPPLY_INTERMEDIATE": ({("KWD1", "14"), ("KWD2", "11")}, set()),
    }
    for name, (removed, added) in expected_native_node_delta.items():
        before = node_keys(changed_native[name][0])
        after = node_keys(changed_native[name][1])
        need(before - after == removed and after - before == added, f"{name}: native node delta changed")
    for directory in (OUT, ENG):
        need(len(rows(directory / "topology-delta.csv")) == 7, f"{directory}: topology delta count")
        faults = rows(directory / "fault-truth-table.csv")
        need(len(faults) == 12, f"{directory}: fault count")
        need({r["case_id"] for r in faults} == {f"FT-{i:03d}" for i in range(1,13)}, f"{directory}: fault IDs")
        need(sum(r["expected_sra1_output"] == "HAZARDOUS_UNRESOLVED" for r in faults) == 3, f"{directory}: hazardous case count")
        need(all(r["safety_credit"] == "NONE" and r["warning"] == WARNING for r in faults), f"{directory}: safety boundary")
        need(len(rows(directory / "source-register.csv")) == 3, f"{directory}: source count")
        holds = rows(directory / "open-holds.csv")
        need(len(holds) == 9 and all(r["state"] == "OPEN" for r in holds), f"{directory}: holds")
        parity = json.loads((directory / "parity-summary.json").read_text(encoding="utf-8"))
        need(parity["changed_terminal_net_assignments"] == 7 and parity["unchanged_terminal_net_assignments"] == 333, f"{directory}: parity")
        need(parity["native_netlist_component_value_footprint_identity_equal"] and parity["native_netlist_changed_net_memberships"] == 7, f"{directory}: native netlist parity")
        need(not parity["p120_accepted"] and parity["safety_credit"] == "NONE" and not parity["work_authority"], f"{directory}: authority")
    manifest = {r["file"]:r for r in rows(OUT / "file-manifest.csv")}
    actual = {p.name:p for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(set(manifest) == set(actual), "release package manifest membership")
    for name,path in actual.items():
        data=path.read_bytes(); need(manifest[name]["sha256"] == hashlib.sha256(data).hexdigest(), f"{name}: hash"); need(manifest[name]["size_bytes"] == str(len(data)), f"{name}: size")
    page=(OUT/"index.html").read_text(encoding="utf-8")
    need(WARNING in page and "zero safety credit" in page and "All 12" in page, "interactive guide boundary")
    for path in (DOC, REQUEST):
        text = path.read_text(encoding="utf-8")
        need(WARNING in text and "P1.20" in text, f"{path}: warning or candidate boundary missing")
    supplement = rows(SUPPLEMENT)
    need({r["gate_id"] for r in supplement} == {"EG-002", "EG-004", "EG-012", "EG-020", "EG-021", "EG-022"}, "R232 gate supplement changed")
    need(all(r["status"] == "REMAINS PARTIAL" and r["warning"] == WARNING for r in supplement), "R232 gate boundary weakened")
    candidate = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    safety = next(item for item in candidate["current_products"] if item["domain"] == "functional_safety")
    need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 current identity changed")
    need(electrical["watchdog_interlock_candidate"] == "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE", "P1.20 metadata binding missing")
    need(electrical["p120_watchdog_interlock_dossier"] == "HR-V0-P120-WD-INTERLOCK-P0.1", "R232 dossier binding missing")
    need(safety["watchdog_interlock_candidate"] == "HR-V0-P120-WD-INTERLOCK-P0.1", "functional-safety R232 binding missing")
    need("zero_safety_credit" in safety["release_state"] and "qualified_review_open" in safety["release_state"], "functional-safety boundary weakened")
    print("HR-V0 P1.20 watchdog-interlock check passed: 7 exact terminal deltas, 12 fault screens, ERC 0/0")
    print(WARNING)


if __name__ == "__main__":
    main()
