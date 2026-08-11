#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-CONFIG-REC-P0.3."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.3"
OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.3"
IDENTIFIER = "HR-V0-CONFIG-REC-P0.3"
MECHANICAL = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
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
        need(directory.is_dir() and {path.name for path in directory.iterdir() if path.is_file()} == expected, f"package membership mismatch: {directory}")
        need(not any(path.suffix.lower() in {".zip", ".pdf", ".7z", ".rar"} for path in directory.iterdir()), "archive/PDF prohibited")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == IDENTIFIER and status.get("round") == "R214", "identity changed")
    need(status.get("current_mechanical_identifier") == MECHANICAL, "current mechanical identity changed")
    for key, value in {"current_records": 18, "supersession_records": 10, "bom_integration_records": 8, "gate_records": 9, "open_holds": 19, "acceptance_rows": 16}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in ("all_acceptance_executed", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    current = rows(OUT / "current-configuration-map.csv")
    mechanical = [row for row in current if row["identifier"] == MECHANICAL]
    need(len(current) == 18 and len(mechanical) == 1, "current mechanical record missing or duplicated")
    need(mechanical and "DFM, FAI" in mechanical[0]["release_boundary"], "mechanical release boundary weakened")
    need(all(row["warning"] == WARNING for row in current), "current-map warning changed")
    bom = rows(OUT / "bom-integration-map.csv")
    bom027 = [row for row in bom if row["item_id"] == "BOM-027"]
    need(len(bom) == 8 and len(bom027) == 1 and bom027[0]["closure_class"] == "exact_candidate_hold" and bom027[0]["physical_evidence"] == "OPEN" and bom027[0]["procurement_released"] == "NO", "BOM-027 integration boundary changed")
    supersession = rows(OUT / "supersession-map.csv")
    need(len(supersession) == 10 and all(row["use_authorized"] == "NO" for row in supersession), "supersession map authorizes historical use")
    need(any("ARM-ARCH-P0.7" in row["prior_identifier"] and MECHANICAL in row["current_or_required_successor"] for row in supersession), "mechanical supersession row missing")

    gates = rows(OUT / "gate-impact.csv")
    need({row["gate_id"] for row in gates} == {"EG-002", "EG-003", "EG-004", "EG-005", "EG-006", "EG-010", "EG-012", "EG-014", "EG-015"}, "gate membership changed")
    need(all(row["status"] == "partial" and row["gate_closed"] == "NO" and row["evidence_added"] == IDENTIFIER for row in gates), "gate falsely closed")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 16 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" and not row["approver"] for row in acceptance), "acceptance falsely completed")
    need(len(rows(OUT / "open-holds.csv")) == 19, "hold count changed")

    source_rows = rows(OUT / "source-hash-register.csv")
    need(len(source_rows) == 18, "source-hash record count changed")
    for row in source_rows:
        source = ROOT / row["source_path"]
        need(source.is_file() and digest(source) == row["sha256"], f"current source hash mismatch: {row['source_path']}")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "40,001", "69", "5 / 5", "EG-003, EG-005 and EG-006 remain partial", WARNING):
        need(token in page, f"guide token missing: {token}")
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
        print("HR-V0-CONFIG-REC-P0.3 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-CONFIG-REC-P0.3 PASS")
    print("  integrated P0.8 mechanical identity is current; P0.7 is historical analytical basis only")
    print("  19 holds and 16 acceptance rows remain open; every work authority remains false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
