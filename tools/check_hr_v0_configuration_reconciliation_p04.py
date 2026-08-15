#!/usr/bin/env python3
"""Validate HR-V0-CONFIG-REC-P0.4 / R223."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.4"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.4"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md", "package-status.json", "current-configuration-map.csv", "supersession-map.csv", "bom-integration-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv", "source-hash-register.csv", "file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        need(directory.is_dir() and {path.name for path in directory.iterdir() if path.is_file()} == expected, f"membership mismatch: {directory}")
        need(not any(path.suffix.lower() in {".pdf", ".zip", ".7z", ".rar"} for path in directory.iterdir()), "PDF/archive prohibited")
        manifest = rows(directory / "file-manifest.csv")
        actual = {path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
        need({row["path"] for row in manifest} == actual, f"manifest membership mismatch: {directory}")
        for row in manifest:
            path = directory / row["path"]
            need(path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"], f"manifest mismatch: {path}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    counts = {"system_bom_groups": 95, "current_records": 23, "supersession_records": 11, "bom_integration_records": 15, "gate_records": 11, "open_holds": 26, "acceptance_rows": 24}
    need(status.get("identifier") == "HR-V0-CONFIG-REC-P0.4" and status.get("round") == "R223", "identity changed")
    need(status.get("current_core_electrical_identifier") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 no longer current")
    need(status.get("unaccepted_panel_topology_candidate") == "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "P1.18 boundary changed")
    for key, value in counts.items():
        need(status.get(key) == value, f"count mismatch: {key}")
    for key in ("all_acceptance_executed", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    current = rows(OUT / "current-configuration-map.csv")
    identifiers = {row["identifier"] for row in current}
    for identifier in ("Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "HR-V0-CP-CONFIG-P0.1", "HR-V0-PANEL-COND-P0.1", "HR-V0-PANEL-P2P-P0.1", "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "HR-V0-PANEL-NODE-PLACEMENT-P0.1"):
        need(identifier in identifiers, f"current/configured identifier missing: {identifier}")
    p118 = next(row for row in current if row["identifier"] == "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE")
    need(p118["configuration_state"] == "UNACCEPTED SUPPORTING ECAD CANDIDATE" and "P1.15 remains current" in p118["release_boundary"], "P1.18 falsely promoted")
    source_rows = rows(OUT / "source-hash-register.csv")
    need(len(source_rows) == 23, "source count changed")
    for row in source_rows:
        source = ROOT / row["source_path"]
        # P0.4 is the immutable R223 snapshot. The live BOM and release-candidate
        # files are intentionally advanced by later rounds and are reconciled by
        # the current successor rather than rewriting this historical package.
        if row["source_path"] in {"bom/bom.csv", "release/hr-v0/release-candidate.json"}:
            need(source.is_file(), f"historical source path missing: {row['source_path']}")
        else:
            need(source.is_file() and digest(source) == row["sha256"], f"source hash mismatch: {row['source_path']}")
    bom = rows(OUT / "bom-integration-map.csv")
    need(len(bom) == 15 and {row["item_id"] for row in bom[-7:]} == {"BOM-083", "BOM-084", "BOM-085", "BOM-092", "BOM-093", "BOM-094", "BOM-095"}, "R223 BOM integration changed")
    need(all(row["physical_evidence"] == "OPEN" and row["procurement_released"] == "NO" for row in bom), "BOM falsely released")
    gates = rows(OUT / "gate-impact.csv")
    need({row["gate_id"] for row in gates} == {"EG-002", "EG-003", "EG-004", "EG-005", "EG-006", "EG-010", "EG-012", "EG-014", "EG-015", "EG-018", "EG-020"}, "gate set changed")
    need(all(row["status"] == "partial" and row["gate_closed"] == "NO" for row in gates), "gate falsely closed")
    need(len(rows(OUT / "open-holds.csv")) == 26, "hold count changed")
    need(all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in rows(OUT / "acceptance-matrix.csv")), "acceptance falsely completed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:clamp(16px", "font-size:14px", "55", "95", "P1.15 remains current", "P1.18 is an unaccepted"):
        need(token in page, f"guide token missing: {token}")
    if failures:
        print("HR-V0-CONFIG-REC-P0.4 FAIL")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-CONFIG-REC-P0.4 PASS")
    print("23 current/configured records; P1.15 current; P1.18 unaccepted; 95 BOM groups; 26 holds")
    print("No procurement, fabrication, assembly, wiring, powered test, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
