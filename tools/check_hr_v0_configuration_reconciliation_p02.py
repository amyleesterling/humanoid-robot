#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-CONFIG-REC-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from hr_v0_r213_compat import r213_allows_historical_source_hash


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.2"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    common = {"README.md","package-status.json","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","source-hash-register.csv","file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        need({path.name for path in directory.iterdir() if path.is_file()} == expected, f"package membership mismatch: {directory}")
        need(not any(path.suffix.lower() in {".zip",".pdf",".7z",".rar"} for path in directory.iterdir()), "archive/PDF prohibited")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    expected_counts = {"system_bom_groups":91,"current_records":17,"supersession_records":9,"bom_integration_records":7,"gate_records":7,"open_holds":15,"acceptance_rows":12}
    need(status.get("identifier") == "HR-V0-CONFIG-REC-P0.2" and status.get("round") == "R212", "identity changed")
    need(status.get("current_core_electrical_identifier") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "core identity changed")
    need(status.get("current_system_view_identifier") == "V3-P1.17-OBSERVATION-P0.5-CANDIDATE", "system-view identity changed")
    for key, value in expected_counts.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in ("all_acceptance_executed","physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    current = rows(OUT / "current-configuration-map.csv")
    identifiers = {row["identifier"] for row in current}
    for identifier in ("Project Button Electrical V3-P1.15-CARRIER-CANDIDATE","V3-P1.17-OBSERVATION-P0.5-CANDIDATE","HR-V0-RUNTIME-OBS-CARRIER-P0.5","HR-V0-PI-OBS-CARRIER-P0.1","HR-V0-OBSERVATION-FIELD-HARNESS-P0.1","HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1","DXL-STAR-P0.2-CARRIER-CANDIDATE","HR-V0-WD-CAM-P0.2","HR-V0-E2-HW-P0.4"):
        need(identifier in identifiers, f"current identifier missing: {identifier}")
    need(len(current) == 17 and all(row["warning"] == WARNING for row in current), "current map count/warning changed")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(row for row in release["current_products"] if row["domain"] == "electrical")
    need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "release core identity changed")
    for identifier in ("V3-P1.17-OBSERVATION-P0.5-CANDIDATE","HR-V0-RUNTIME-OBS-CARRIER-P0.5","HR-V0-PI-OBS-CARRIER-P0.1","HR-V0-OBSERVATION-FIELD-HARNESS-P0.1","HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1","HR-V0-CONFIG-REC-P0.3"):
        need(identifier in electrical["supporting_identifiers"], f"release support missing: {identifier}")
    need("HR-V0-RUNTIME-OBS-CARRIER-P0.2" not in electrical["supporting_identifiers"], "superseded P0.2 remains current")

    p117 = ROOT / "electrical/kicad/project-button-v3-p1.17-observation-p05-candidate"
    need("ERC messages: 0  Errors 0  Warnings 0" in (p117 / "validation/project-button-v3-p1.17-observation-p05-candidate-erc.rpt").read_text(encoding="utf-8-sig"), "P1.17 ERC not 0/0")
    p05 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5"
    need("ERC messages: 0  Errors 0  Warnings 0" in (p05 / "validation/hr-v0-runtime-observation-carrier-p0.5-erc.rpt").read_text(encoding="utf-8-sig"), "P0.5 ERC not 0/0")
    need("0 drc violations" in (p05 / "validation/hr-v0-runtime-observation-carrier-p0.5-drc.rpt").read_text(encoding="utf-8-sig").lower(), "P0.5 DRC not zero")

    supersession = rows(OUT / "supersession-map.csv")
    need(len(supersession) == 9 and all(row["use_authorized"] == "NO" for row in supersession), "supersession map released historical data")
    combined = " ".join(row["prior_identifier"] + " " + row["disposition"] for row in supersession)
    for token in ("V3-P1.16", "RUNTIME-OBS-CARRIER-P0.2", "CONFIG-REC-P0.1", "prohibited"):
        need(token.lower() in combined.lower(), f"supersession token missing: {token}")
    gates = rows(OUT / "gate-impact.csv")
    need({row["gate_id"] for row in gates} == {"EG-002","EG-003","EG-004","EG-010","EG-012","EG-014","EG-015"}, "gate membership changed")
    need(all(row["status"] == "partial" and row["gate_closed"] == "NO" and row["evidence_added"] == "HR-V0-CONFIG-REC-P0.2" for row in gates), "gate falsely closed")
    system_gates = {row["gate_id"]: row for row in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    need(all(system_gates[gate]["status"] == "partial" for gate in ("EG-002","EG-003","EG-004","EG-010","EG-012","EG-014","EG-015")), "system gate state changed")
    supplement = rows(ROOT / "requirements/hr-v0-gate-evidence-supplement-r212.csv")
    need({row["gate_id"] for row in supplement} == {"EG-002","EG-003","EG-004","EG-010","EG-012","EG-014","EG-015"}, "R212 gate-supplement membership changed")
    need(all(row["round"] == "R212" and row["state"] == "REMAINS PARTIAL" and row["warning"] == WARNING.replace(",", "") for row in supplement), "R212 gate supplement falsely closes or changes a boundary")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 12 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "acceptance falsely completed")
    need(len(rows(OUT / "open-holds.csv")) == 15, "hold count changed")

    for row in rows(OUT / "source-hash-register.csv"):
        source = ROOT / row["source_path"]
        need(
            source.exists() and (digest(source) == row["sha256"] or r213_allows_historical_source_hash(ROOT, row["source_path"])),
            f"source hash mismatch: {row['source_path']}",
        )
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "P1.15 core + P1.17 observation view", "Observation P0.5", "All seven affected gates remain partial", WARNING):
        need(token.lower() in page.lower(), f"guide token missing: {token}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    for directory in (ENG, OUT):
        manifest = rows(directory / "file-manifest.csv")
        actual = {path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv"}
        need({row["path"] for row in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(digest(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {path}")

    if failures:
        print("HR-V0-CONFIG-REC-P0.2 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-CONFIG-REC-P0.2 PASS")
    print("  P1.15 core plus parity-checked P1.17/P0.5 observation chain reconciled")
    print("  15 holds and 12 acceptance rows remain open; every authority remains false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
