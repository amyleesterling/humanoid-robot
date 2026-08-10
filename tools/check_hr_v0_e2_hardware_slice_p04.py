#!/usr/bin/env python3
"""Validate the P1.15-bound HR-V0 E2 control-only hardware slice P0.4."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.4"
REL = ROOT / "release" / "hr-v0" / "e2-hardware-p0.4"
IDENTIFIER = "HR-V0-E2-HW-P0.4"
PARITY = "HR-V0-E2-P115-PARITY-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {"README.md", "HR-V0_e2-hardware-guide.html", "e2-blocking-holds.csv", "e2-configuration-slice.csv", "e2-hardware-summary.json", "e2-source-register.csv", "e2-terminal-register.csv", "file-manifest.csv", "source-hash-register.csv"}
    for directory in (ENG, REL):
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
        need(actual == expected, f"package membership changed: {directory.name}: {sorted(actual ^ expected)}")

    config = rows(REL / "e2-configuration-slice.csv")
    terminals = rows(REL / "e2-terminal-register.csv")
    sources = rows(REL / "e2-source-register.csv")
    holds = rows(REL / "e2-blocking-holds.csv")
    hashes = rows(REL / "source-hash-register.csv")
    summary = json.loads((REL / "e2-hardware-summary.json").read_text(encoding="utf-8"))
    page = (REL / "HR-V0_e2-hardware-guide.html").read_text(encoding="utf-8")

    need(len(config) == 23, "expected 23 configuration rows")
    need(len(terminals) == 6, "expected six XT1 positions")
    need(len(sources) == 3, "expected three source-domain rows")
    need(len(holds) == 12, "expected twelve blocking holds")
    need(len(hashes) == 7, "expected seven source hashes")
    need(summary.get("identifier") == IDENTIFIER and summary.get("round") == "R165+R166-SYNCHRONIZED", "summary identity changed")
    need(summary.get("electrical_baseline") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE / PCB-P0.9 / HR-V0-WD-PCBA-DATA-P0.2", "P1.15 baseline changed")
    need(summary.get("parity_evidence") == PARITY and summary.get("p115_parity_verified_by_checker") is True, "P1.15 parity binding missing")
    need(summary.get("authorization") == "NOT AUTHORIZED", "E2 authorization must remain denied")
    for key in ("physical_configuration_verified", "run_authorized", "fabrication_authorized", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(summary.get(key) is False, f"{key} must remain false")
    need(summary.get("prohibited_power_domains") == ["12 V actuator", "powered U2D2/actuator branches"], "actuator-domain prohibition changed")

    for row in hashes:
        path = ROOT / row["path"]
        need(path.is_file(), f"source missing: {row['path']}")
        if path.is_file():
            need(row["sha256"] == digest(path) and int(row["bytes"]) == path.stat().st_size, f"source hash mismatch: {row['source_id']}")
        need(row["warning"] == WARNING, f"source warning changed: {row['source_id']}")
    need(summary.get("source_hashes") == {row["path"]: row["sha256"] for row in hashes}, "summary/source register hash map differs")

    config_by_id = {row["record_id"]: row for row in config}
    wd = config_by_id.get("E2-CFG-011", {})
    actuator = config_by_id.get("E2-CFG-018", {})
    need(PARITY in wd.get("candidate", "") and "P1.15-PARITY INSTALL CANDIDATE" == wd.get("physical_state"), "watchdog P1.15 identity not synchronized")
    need("current internal CAM exists" in wd.get("open_evidence", "") and "supplier-normalized XYRS" in wd.get("open_evidence", ""), "watchdog CAM/process boundary changed")
    need("P0.3 limiter carriers" in actuator.get("candidate", "") and "DXL-STAR-P0.2-CARRIER-CANDIDATE" in actuator.get("candidate", ""), "current actuator subset identity missing")
    need(actuator.get("physical_state") == "PHYSICALLY ABSENT OR UNWIRED" and actuator.get("e2_boundary") == "NO ACTUATOR CURRENT PATH", "actuator subset incorrectly permitted at E2")
    need({(row["terminal"], row["net"]) for row in terminals} == {("XT1-01", "SAFETY_24V"), ("XT1-02", "SAFETY_0V"), ("XT1-03", "SR1_STATUS"), ("XT1-04", "SRA1_STATUS"), ("XT1-05", "K1_STATUS"), ("XT1-06", "K2_STATUS")}, "XT1 map changed")
    need(all(row["warning"] == WARNING for row in config + terminals + sources + holds), "warning missing from a package row")
    need(all("NOT EXECUTED" not in row.values() for row in config), "configuration slice contains an execution claim field")
    hold_by_id = {row["hold_id"]: row for row in holds}
    need("machine-checked P1.15 system parity" in hold_by_id.get("E2-HOLD-008", {}).get("open_item", ""), "P1.15 parity hold disposition missing")
    need("Independent P1.15 parity acceptance" in hold_by_id.get("E2-HOLD-008", {}).get("evidence_needed", ""), "independent parity acceptance not retained")

    combined = "\n".join(str(value) for row in config + terminals + sources + holds for value in row.values()) + page
    for token in ("WR9QI1660YL4NKITR6B", "KPJX-PM-4S", "F24", "TP15/TP16/TP2", "TOOL/DEBUG CONNECTION ABSENT", "PHYSICALLY ABSENT", "LOAD POLES UNSOURCED AND UNWIRED", "NO FUSE LINK SELECTED", "NOT APPROVED FOR FABRICATION OR ENERGIZATION"):
        need(token in combined, f"fail-closed token missing: {token}")
    for stale in ("GST40A24-P1J", "DC PLUG-P1J-R7B", "JDBG1", "Project Button Electrical V3-P1.14 / PCB-P0.9"):
        need(stale not in combined and stale not in json.dumps(summary), f"stale configuration remains: {stale}")
    need("font:16px" in page and "font-size:1rem" in page, "guide text floor changed")
    need("Â" not in page and "Ã" not in page and "â" not in page, "guide contains malformed encoding")

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
    print("  P1.15 parity bound / 23 configuration rows / 6 XT1 rows / 12 holds")
    print("  actuator source and branches absent or unwired; physical evidence and authorization remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
