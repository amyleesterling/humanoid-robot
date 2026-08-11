#!/usr/bin/env python3
"""Validate R225 watchdog permit topology proof against the P1.18 netlist."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/project-button-v3-p1.18-panel-topology-candidate"
NETLIST = ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate.net"
NATIVE = ECAD / "03_arm_watchdog_eligibility.kicad_sch"
WIRES = ECAD / "wire-number-table.csv"
ENG = ROOT / "electrical/reviews/hr-v0-watchdog-permit-topology-p0.1"
OUT = ROOT / "release/hr-v0/watchdog-permit-topology-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def net_members(text: str) -> dict[str, set[tuple[str, str]]]:
    result: dict[str, set[tuple[str, str]]] = {}
    in_nets = False
    current: list[str] | None = None
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "(nets":
            in_nets = True
            continue
        if in_nets and current is None and stripped == "(net":
            current = [line]
            depth = line.count("(") - line.count(")")
            continue
        if current is not None:
            current.append(line)
            depth += line.count("(") - line.count(")")
            if depth == 0:
                block = "\n".join(current)
                name_match = re.search(r'\(name "([^"]+)"\)', block)
                if name_match:
                    members = set(re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', block, flags=re.S))
                    result[name_match.group(1)] = members
                current = None
    return result


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md", "topology-register.csv", "fault-truth-table.csv", "finding-reconciliation.csv", "source-register.csv", "open-holds.csv", "authority-boundary.csv", "package-status.json", "file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {p.name for p in directory.iterdir() if p.is_file()} if directory.is_dir() else set()
        need(actual == expected, f"package membership mismatch: {directory}")
        need(not any(p.suffix.lower() in {".pdf", ".zip", ".7z", ".rar"} for p in directory.iterdir()), f"PDF/archive prohibited: {directory}")
        manifest = rows(directory / "file-manifest.csv")
        controlled = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == controlled, f"manifest membership mismatch: {directory}")
        for row in manifest:
            path = directory / row["path"]
            need(path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"], f"manifest mismatch: {path}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")

    source_rows = {r["source_id"]: r for r in rows(OUT / "source-register.csv")}
    expected_sources = {
        "WPT-SRC-001": NATIVE,
        "WPT-SRC-002": NETLIST,
        "WPT-SRC-003": WIRES,
        "WPT-SRC-004": ECAD / "validation/project-button-v3-p1.18-panel-topology-candidate-erc.rpt",
        "WPT-SRC-005": ROOT / "docs/hr-v0-safety-requirements-p0.2.md",
    }
    need(set(source_rows) == set(expected_sources) | {"WPT-SRC-006"}, "source register membership changed")
    for source_id, path in expected_sources.items():
        need(source_rows.get(source_id, {}).get("sha256") == digest(path), f"source hash mismatch: {source_id}")
    need(source_rows.get("WPT-SRC-006", {}).get("sha256") == "NOT_APPLICABLE_REMOTE_PRIMARY_SOURCE", "remote source boundary changed")

    nets = net_members(NETLIST.read_text(encoding="utf-8"))
    need({("KWD1", "14"), ("KWD2", "11")} == nets.get("WD_SUPPLY_INTERMEDIATE"), "series intermediate net endpoints changed")
    need({("KWD2", "14"), ("SR1", "A1")} == nets.get("SR1_A1_WD_GATED"), "gated SR1 A1 net endpoints changed")
    need(("KWD1", "11") in nets.get("SAFETY_24V", set()), "KWD1 stage input is not on SAFETY_24V")
    expected_estop = {
        "SR1_S11": {("S0", "R-1"), ("SR1", "S11")},
        "SR1_S12": {("S0", "R-2"), ("SR1", "S12")},
        "SR1_S21": {("S0", "L-1"), ("SR1", "S21")},
        "SR1_S22": {("S0", "L-2"), ("SR1", "S22")},
    }
    for net, mandatory in expected_estop.items():
        members = nets.get(net, set())
        need(mandatory <= members, f"E-stop mandatory endpoints changed: {net}")
        need(not any(ref in {"KWD1", "KWD2"} for ref, _ in members), f"KWD endpoint entered E-stop loop: {net}")

    native = NATIVE.read_text(encoding="utf-8")
    for token in ("First ordinary watchdog supply-gate stage", "Second ordinary watchdog supply-gate stage", "WD_SUPPLY_INTERMEDIATE", "SR1_A1_WD_GATED", "No PL/SIL credit"):
        need(token in native, f"native sheet token missing: {token}")
    wire_rows = rows(WIRES)
    wire_map = {(r["reference"], r["terminal"]): (r["net"], r["wire_number"]) for r in wire_rows}
    expected_wires = {
        ("KWD1", "11"): ("SAFETY_24V", "W3016"),
        ("KWD1", "14"): ("WD_SUPPLY_INTERMEDIATE", "W3018"),
        ("KWD2", "11"): ("WD_SUPPLY_INTERMEDIATE", "W3022"),
        ("KWD2", "14"): ("SR1_A1_WD_GATED", "W3024"),
        ("SR1", "A1"): ("SR1_A1_WD_GATED", "W2005"),
    }
    for endpoint, expected in expected_wires.items():
        need(wire_map.get(endpoint) == expected, f"wire-table parity changed: {endpoint}")

    faults = rows(OUT / "fault-truth-table.csv")
    need(len(faults) == 9, "fault table must contain nine cases")
    for row in faults:
        c1, c2, w1, w2 = (int(row[k]) for k in ("kwd1_commanded", "kwd2_commanded", "kwd1_welded_or_bypassed", "kwd2_welded_or_bypassed"))
        e1, e2 = int(bool(c1 or w1)), int(bool(c2 or w2))
        need(int(row["kwd1_effective_closed"]) == e1 and int(row["kwd2_effective_closed"]) == e2, f"effective state mismatch: {row['case_id']}")
        need(int(row["sr1_a1_supply_permitted"]) == int(bool(e1 and e2)), f"series logic mismatch: {row['case_id']}")
        need(row["physical_validation"] == "NOT EXECUTED" and row["safety_credit"] == "ZERO", f"fault case overclaims evidence: {row['case_id']}")
    by_id = {r["case_id"]: r for r in faults}
    need(by_id.get("WPT-F-005", {}).get("sr1_a1_supply_permitted") == "0" and by_id.get("WPT-F-006", {}).get("sr1_a1_supply_permitted") == "0", "single-weld fail-open screen changed")
    need(by_id.get("WPT-F-009", {}).get("sr1_a1_supply_permitted") == "1", "dual-weld/common-cause hazard must remain visible")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {"identifier": "HR-V0-WD-PERMIT-TOPOLOGY-P0.1", "round": "R225", "series_permit_contacts": 2, "estop_input_loops_with_kwd_endpoint": 0, "truth_table_cases": 9, "open_holds": 8}.items():
        need(status.get(key) == value, f"status mismatch: {key}")
    for key in ("reviewer_closure_claimed", "functional_safety_credit", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
        need(status.get(key) is False, f"{key} must remain false")
    holds = rows(OUT / "open-holds.csv")
    need(len(holds) == 8 and all(r["state"] == "OPEN" and r["accepted"] == "FALSE" for r in holds), "hold falsely closed")
    finding = rows(OUT / "finding-reconciliation.csv")
    need(len(finding) == 1 and finding[0]["reviewer_closure"] == "NOT CLAIMED" and "DOES NOT MATCH" in finding[0]["current_source_disposition"], "finding disposition overclaims closure")
    authority = rows(OUT / "authority-boundary.csv")
    need(len(authority) == 4 and sum(r["permitted"] == "TRUE" for r in authority) == 1, "authority boundary changed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:clamp(16px", "font-size:14px", "Two series stages", "zero safety credit", "WPT-F-009", "Eight open holds"):
        need(token in page, f"web guide missing token: {token}")
    for filename in ("topology-register.csv", "fault-truth-table.csv", "finding-reconciliation.csv", "source-register.csv", "open-holds.csv", "authority-boundary.csv"):
        need(all(r.get("warning") == WARNING for r in rows(OUT / filename)), f"warning missing: {filename}")

    if failures:
        print("HR-V0 watchdog permit topology P0.1: FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 watchdog permit topology P0.1: PASS")
    print("2 series contacts / 0 KWD endpoints in E-stop loops / 9 Boolean fault screens / 8 holds")
    print("Single-contact summary assertion contradicted by P1.18 source; zero safety credit and no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
