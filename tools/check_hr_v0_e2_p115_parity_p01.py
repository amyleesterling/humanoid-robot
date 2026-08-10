#!/usr/bin/env python3
"""Fail-closed validation for HR-V0 P1.15 watchdog/E2 parity evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import re
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
CHANGED = {"F1", "F2", "F3", "INJ1", "J1", "J2", "J3"}
ADDED = {"LIM1", "LIM2", "LIM3"}
E2_REFS = {"PSU2", "J24", "F24", "PSU3", "S0", "S1", "S2", "H1", "SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "DC1", "WDCTRL1", "UDRV1", "UDRV2", "UFB1", "PI1", "XT1", "FSR1", "FSR2", "TP15", "TP16", "TP2", "SP1", "JFRAME1"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def native(path: Path) -> tuple[set[str], dict[tuple[str, str], str]]:
    text = path.read_text(encoding="utf-8-sig")
    refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', text))
    nodes: dict[tuple[str, str], str] = {}
    for block in sexpr_blocks(text, "net"):
        match = re.search(r'\(name "([^"]+)"\)', block)
        if match is None:
            continue
        for ref, pin in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block):
            nodes[(ref, pin)] = match.group(1)
    return refs, nodes


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {"README.md", "acceptance-matrix.csv", "component-parity-register.csv", "e2-scope-register.csv", "expected-change-register.csv", "file-manifest.csv", "index.html", "open-holds.csv", "package-status.json", "source-hash-register.csv", "terminal-parity-register.csv"}
    for directory in (ENG, REL):
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
        need(actual == expected, f"package membership changed: {directory}: {sorted(actual ^ expected)}")

    status = json.loads((REL / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R165", "status identity changed")
    for key, value in {"unchanged_component_refs": 69, "unchanged_terminal_rows": 263, "explicit_e2_refs": 28, "declared_changed_common_refs": 7, "declared_added_refs": 3, "open_holds": 12, "acceptance_rows": 8}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(status.get("digital_parity_complete") is True, "digital parity result not recorded")
    for key, value in status.items():
        if key.endswith("_authorized") or key in {"independent_review_complete", "physical_article_exists", "physical_test_executed", "safety_credit"}:
            need(value is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    source_rows = rows(REL / "source-hash-register.csv")
    need(len(source_rows) == 9, "expected nine source records")
    for row in source_rows:
        path = ROOT / row["path"]
        need(path.is_file(), f"source missing: {row['path']}")
        if path.is_file():
            need(row["sha256"] == digest(path) and int(row["bytes"]) == path.stat().st_size, f"source hash mismatch: {row['source_id']}")
        need(row["warning"] == WARNING, f"source warning changed: {row['source_id']}")

    base_erc = (BASE / "validation" / "project-button-v3-erc.rpt").read_text(encoding="utf-8-sig")
    cand_erc = (CAND / "validation" / "project-button-v3-p1.15-carrier-candidate-erc.rpt").read_text(encoding="utf-8-sig")
    need("ERC messages: 0  Errors 0  Warnings 0" in base_erc, "P1.14 native ERC not zero")
    need("ERC messages: 0  Errors 0  Warnings 0" in cand_erc, "P1.15 native ERC not zero")

    base_refs, base_nodes = native(BASE / "validation" / "project-button-v3.net")
    cand_refs, cand_nodes = native(CAND / "validation" / "project-button-v3-p1.15-carrier-candidate.net")
    need(not (base_refs - cand_refs), f"P1.15 removed refs: {sorted(base_refs-cand_refs)}")
    need(cand_refs - base_refs == ADDED, f"unexpected P1.15 added refs: {sorted(cand_refs-base_refs)}")
    unchanged = (base_refs & cand_refs) - CHANGED
    need(len(unchanged) == 69, "unchanged component set changed")

    def keyed(data: list[dict[str, str]], keys: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
        return {tuple(row[key] for key in keys): row for row in data}

    base_conn = keyed(rows(BASE / "connector-schedule.csv"), ("reference", "terminal"))
    cand_conn = keyed(rows(CAND / "connector-schedule.csv"), ("reference", "terminal"))
    expected_terminal_rows: list[tuple[str, str, str, str, str, str, str]] = []
    for ref in sorted(unchanged):
        b = {key: row for key, row in base_conn.items() if key[0] == ref}
        c = {key: row for key, row in cand_conn.items() if key[0] == ref}
        need(b == c, f"schedule parity changed outside actuator subset: {ref}")
        for key, row in sorted(b.items()):
            need(base_nodes.get(key) == cand_nodes.get(key), f"native net parity changed: {ref}:{key[1]}")
            expected_terminal_rows.append((ref, key[1], row["sheet"], row["pin_name"], row["net"], base_nodes.get(key, ""), cand_nodes.get(key, "")))

    package_terms = rows(REL / "terminal-parity-register.csv")
    actual_terminal_rows = [(row["reference"], row["terminal"], row["sheet"], row["pin_name"], row["net"], row["native_net_p114"], row["native_net_p115"]) for row in package_terms]
    need(actual_terminal_rows == expected_terminal_rows, "terminal parity register differs from native/schedule evidence")
    need(all(row["parity"] == "EXACT" and row["warning"] == WARNING for row in package_terms), "terminal parity/warning changed")

    component_rows = rows(REL / "component-parity-register.csv")
    need({row["reference"] for row in component_rows} == unchanged, "component parity membership changed")
    need(all(row["schedule_parity"] == "EXACT" and row["native_net_parity"] == "EXACT" and row["disposition"] == "UNCHANGED IN P1.15" for row in component_rows), "component parity disposition changed")
    e2_rows = rows(REL / "e2-scope-register.csv")
    need({row["reference"] for row in e2_rows} == E2_REFS, "explicit E2 parity scope changed")
    need(all(row["schedule_parity"] == "EXACT" and row["native_net_parity"] == "EXACT" and row["release_effect"] == "DIGITAL COMPATIBILITY EVIDENCE ONLY" for row in e2_rows), "E2 parity release boundary changed")
    changes = rows(REL / "expected-change-register.csv")
    need({row["reference"] for row in changes if row["change_class"] == "COMMON_REF_CHANGED"} == CHANGED, "changed-ref register differs")
    need({row["reference"] for row in changes if row["change_class"] == "ADDED"} == ADDED, "added-ref register differs")
    need(all(row["e2_power_state"] == "PHYSICALLY ABSENT OR UNWIRED" for row in changes), "actuator subset incorrectly permitted at E2")
    holds = rows(REL / "open-holds.csv")
    need(len(holds) == 12 and all(row["state"] == "OPEN" and row["warning"] == WARNING for row in holds), "twelve holds must remain open")
    acceptance = rows(REL / "acceptance-matrix.csv")
    need(len(acceptance) == 8 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "acceptance evidence must remain blank/open")

    page = (REL / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", "69</b>", "263</b>", "28</b>", "0</b>", "DIGITAL CONFIGURATION PARITY ONLY", "not physical validation or test authorization"):
        need(token in page, f"interactive guide token missing: {token}")
    for name in expected - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (REL / name).read_bytes(), f"engineering/release mirror differs: {name}")
    for directory in (ENG, REL):
        manifest = rows(directory / "file-manifest.csv")
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
        need({row["path"] for row in manifest} == actual, f"manifest membership changed: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(row["sha256"] == digest(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch: {directory.name}/{row['path']}")

    if failures:
        print(f"{IDENTIFIER} FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print(f"{IDENTIFIER} PASS")
    print("  69 unchanged refs / 263 exact terminals / 28 explicit E2 refs")
    print("  P1.15 changes limited to 7 declared actuator refs plus 3 carriers")
    print("  12 holds and 8 acceptance rows OPEN; no physical or authorization credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
