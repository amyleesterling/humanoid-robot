#!/usr/bin/env python3
"""Fail-closed checker for the HR-V0 P1.21 no-load fixture candidate."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures/hr-v0-p121-no-load-fixture-p0.1"
REL = ROOT / "release/hr-v0/p121-no-load-fixture-p0.1"
P121 = ROOT / "electrical/kicad/project-button-v3-p1.21-sra1-supply-watchdog-candidate"
APP = ROOT / "safety/hr-v0-p121-application-evidence-p0.1"
PROJECT = "hr-v0-p121-no-load-fixture-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def fail(message: str) -> None:
    raise AssertionError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def endpoint_parts(value: str) -> tuple[str, str] | None:
    if value.startswith("FIX:"):
        return None
    ref, terminal = value.split(":", 1)
    return ref, terminal


def main() -> int:
    required = {
        f"{PROJECT}.kicad_pro", f"{PROJECT}.kicad_sch", f"{PROJECT}.kicad_sym",
        "01_power_and_absence_boundary.kicad_sch", "02_estop_and_eligibility_chain.kicad_sch",
        "03_watchdog_gate_and_stimulus.kicad_sch", "04_isolated_measurement_fanout.kicad_sch",
        "point-to-point-schedule.csv", "signal-binding-register.csv", "test-binding-register.csv",
        "authorization-gate-register.csv", "physical-absence-register.csv", "fixture-layout-register.csv",
        "candidate-bom.csv", "source-register.csv", "open-holds.csv", "fixture-layout.svg", "index.html",
        "README.md", "fixture-status.json", "fixture-source.py", "fixture-checker.py", "file-manifest.csv",
        f"validation/{PROJECT}-erc.rpt", f"validation/{PROJECT}.net", "validation/kicad-cli.log",
    }
    actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}
    require(required <= actual, f"missing required files: {sorted(required - actual)}")
    require(len(list(OUT.glob("*.kicad_sch"))) == 5, "native KiCad sheet count is not five")

    erc = (OUT / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    require("ERC messages: 0  Errors 0  Warnings 0" in erc, "ERC is not 0/0")
    log = (OUT / "validation/kicad-cli.log").read_text(encoding="utf-8")
    require(log.count("exit=0") == 3, "KiCad CLI did not complete ERC/netlist/SVG export cleanly")

    status = json.loads((OUT / "fixture-status.json").read_text(encoding="utf-8"))
    expected = {"native_kicad_sheet_count": 5, "point_to_point_rows": 42, "required_signal_count": 15, "test_count": 18, "authorization_gate_count": 10, "physical_absence_checks": 5, "erc_errors": 0, "erc_warnings": 0}
    for key, value in expected.items():
        require(status.get(key) == value, f"status mismatch: {key}")
    for key in ("p121_accepted", "fixture_independently_checked", "fixture_physically_built", "fixture_unpowered_inspection_complete", "functional_safety_credit", "procurement_authority", "fabrication_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        require(status.get(key) is False, f"authority boundary changed: {key}")

    source_schedule = rows(P121 / "connector-schedule.csv")
    native = {(r["reference"], r["terminal"]): r for r in source_schedule}
    p2p = rows(OUT / "point-to-point-schedule.csv")
    require(len(p2p) == 42 and len({r["wire_id"] for r in p2p}) == 42, "point-to-point schedule count/identity")
    allowed_fixture_substitution = {("SRA1", t) for t in ("13", "14", "23", "24", "33", "34", "41", "42")}
    for row in p2p:
        require(row["warning"] == WARNING and row["installation_state"] == "NOT ASSEMBLED" and row["inspection_state"] == "NOT EXECUTED", f"P2P authority drift: {row['wire_id']}")
        for field in ("from_terminal", "to_terminal"):
            endpoint = endpoint_parts(row[field])
            if endpoint is None:
                continue
            require(endpoint in native, f"unknown P1.21 DUT endpoint {endpoint} in {row['wire_id']}")
            source_net = native[endpoint]["net"]
            if source_net != row["fixture_net"]:
                require(endpoint in allowed_fixture_substitution and "isolated low-energy" in row["function"], f"uncontrolled net substitution {endpoint}: {source_net} -> {row['fixture_net']}")

    signals = rows(OUT / "signal-binding-register.csv")
    tests = rows(OUT / "test-binding-register.csv")
    auth = rows(OUT / "authorization-gate-register.csv")
    require(len(signals) == 15 and {r["signal_id"] for r in signals} == {r["signal_id"] for r in rows(APP / "signal-capture-register.csv")}, "signal spine mismatch")
    require(len(tests) == 18 and all(r["execution_state"] == "NOT EXECUTED" for r in tests), "test spine mismatch/executed state")
    require(len(auth) == 10 and all(r["state"] == "OPEN" for r in auth), "authorization gate count/state")
    auth4 = next(r for r in auth if r["prerequisite_id"] == "AUTH-004")
    require(auth4["fixture_disposition"] == "ARTIFACT ISSUED; GATE REMAINS OPEN", "AUTH-004 overclaim")

    absence = rows(OUT / "physical-absence-register.csv")
    require(len(absence) == 5 and all(r["state"] == "NOT EXECUTED" for r in absence), "absence inspection state")
    absence_text = " ".join(r["prohibited_item"] for r in absence).lower()
    for token in ("actuator source", "k1 and k2", "all actuators", "mains wiring", "ai"):
        require(token in absence_text, f"missing physical-absence class: {token}")

    fixture_connectors = rows(OUT / "connector-schedule.csv")
    refs = {r["reference"] for r in fixture_connectors}
    require(not ({"PSA1", "JA1", "K1", "K2"} & refs), "prohibited robot power hardware encoded in fixture")
    require(not any(r["net"].startswith("ACT_12V") for r in fixture_connectors), "actuator rail encoded in fixture")

    sources = rows(OUT / "source-register.csv")
    require(len(sources) == 7, "source register count")
    for row in sources:
        path = ROOT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"], f"source hash mismatch: {row['source_id']}")

    html_text = (OUT / "index.html").read_text(encoding="utf-8")
    require("font:clamp(16px" in html_text and "font-size:14px" in html_text, "web text minimums missing")
    require("Still not permission to connect or energize" in html_text, "web authority warning missing")
    for match in re.findall(r'data="(output/[^"]+\.svg)"', html_text):
        require((OUT / html.unescape(match)).is_file(), f"broken schematic SVG reference: {match}")

    manifest = rows(OUT / "file-manifest.csv")
    listed = {r["path"] for r in manifest}
    payload = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
    require(listed == payload, "fixture manifest membership mismatch")
    for row in manifest:
        path = OUT / row["path"]
        require(path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"], f"fixture manifest mismatch: {row['path']}")
        require(row["warning"] == WARNING, f"manifest warning drift: {row['path']}")

    source_files = {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL).as_posix(): sha(p) for p in REL.rglob("*") if p.is_file()}
    require(source_files == release_files, "source/release mirror mismatch")

    root_page = (ROOT / "index.html").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require(root_page.count("<!-- HRV0-P121-FIXTURE-START -->") == 1 and root_page.count("<!-- HRV0-P121-FIXTURE-END -->") == 1, "root page integration marker")
    require(root_readme.count("<!-- HRV0-P121-FIXTURE-START -->") == 1 and root_readme.count("<!-- HRV0-P121-FIXTURE-END -->") == 1, "README integration marker")
    require("test-fixtures/hr-v0-p121-no-load-fixture-p0.1/index.html" in root_page, "root page fixture link missing")

    print("PASS: P1.21 control-only fixture has native 5-sheet KiCad, ERC 0/0, 42 checked P2P rows, 15 signals, 18 unexecuted tests, all authority gates open")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
