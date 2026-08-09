"""Fail-closed checks for HR-V0-CONFIG-REC-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "configuration" / "hr-v0-config-reconciliation-p0.1"
OUT = ROOT / "release" / "hr-v0" / "configuration-reconciliation-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda value, message: failures.append(message) if not value else None
    common = {"README.md", "package-status.json", "current-configuration-map.csv", "supersession-map.csv", "bom-integration-map.csv", "gate-impact.csv", "open-holds.csv", "acceptance-matrix.csv", "source-hash-register.csv", "file-manifest.csv"}
    for directory, expected in ((ENG, common), (OUT, common | {"index.html"})):
        actual = {p.name for p in directory.iterdir() if p.is_file()}
        need(actual == expected, f"package membership mismatch: {directory}")
        need(not any(p.suffix.lower() in {".zip", ".pdf", ".7z", ".rar"} for p in directory.iterdir()), "archives/PDFs prohibited")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-CONFIG-REC-P0.1" and status.get("round") == "R163+R164+R165-SYNCHRONIZED", "identity changed")
    need(status.get("current_electrical_identifier") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "current electrical identity changed")
    for key, value in {"system_bom_groups":91,"current_records":11,"supersession_records":5,"bom_integration_records":7,"gate_records":5,"open_holds":10,"acceptance_rows":8}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    need(status.get("current_p02_cam_exists") is True, "current P0.2 CAM review must be recorded")
    for key in ("all_acceptance_executed", "physical_article_exists", "physical_test_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized", "assembly_authorized", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "warning changed")

    current = csv_rows(OUT / "current-configuration-map.csv")
    need(len(current) == 11, "current map count changed")
    identifiers = {r["identifier"] for r in current}
    for value in ("Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "HR-V0-DXL-STAR-MFG-P0.2", "HR-V0-DXL-PROT-CARRIER-P0.3", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "HR-V0-DXL-CARRIER-INTEGRATION-P0.1", "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1", "HR-V0-E2-P115-PARITY-P0.1", "HR-V0-E2-HW-P0.4", "HR-V0-BOM-P0.1"):
        need(value in identifiers, f"current identifier missing: {value}")
    need(all(r["warning"] == WARNING for r in current), "current map warning changed")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next(r for r in release["current_products"] if r["domain"] == "electrical")
    need(electrical["identifier"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "release candidate is stale")
    for value in ("DXL-STAR-P0.2-CARRIER-CANDIDATE", "HR-V0-DXL-PROT-CARRIER-P0.3", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "HR-V0-DXL-CARRIER-INTEGRATION-P0.1", "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1", "HR-V0-E2-P115-PARITY-P0.1", "HR-V0-E2-HW-P0.4", "HR-V0-CONFIG-REC-P0.1"):
        need(value in electrical["supporting_identifiers"], f"release support missing: {value}")

    bom = {r["item_id"]: r for r in csv_rows(ROOT / "bom/bom.csv")}
    need(len(bom) == 91 and len(set(bom)) == 91, "system BOM must contain exactly 91 unique groups")
    for item in ("BOM-035", "BOM-051", "BOM-087", "BOM-088", "BOM-089", "BOM-090", "BOM-091"):
        need(item in bom, f"integrated BOM item missing: {item}")
    need("P0.2-CARRIER-CANDIDATE" in bom["BOM-051"]["manufacturer_part_number"], "BOM-051 is stale")
    need("HR-V0-DXL-STAR-MFG-P0.2" in bom["BOM-051"]["manufacturer_part_number"], "P0.2 CAM review binding missing")

    reports = [
        ROOT / "electrical/kicad/project-button-v3-p1.15-carrier-candidate/validation/project-button-v3-p1.15-carrier-candidate-erc.rpt",
        ROOT / "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/validation/hr-v0-dxl-star-p0.2-carrier-candidate-erc.rpt",
        ROOT / "electrical/kicad/hr-v0-dxl-star-p0.2-carrier-candidate/validation/hr-v0-dxl-star-p0.2-carrier-candidate-drc.rpt",
        ROOT / "release/hr-v0/dxl-protection-carrier-p0.3/validation/hr-v0-dxl-protection-carrier-p0.3-erc.rpt",
        ROOT / "release/hr-v0/dxl-protection-carrier-p0.3/validation/hr-v0-dxl-protection-carrier-p0.3-drc.rpt",
    ]
    for report in reports:
        text = report.read_text(encoding="utf-8", errors="replace")
        need("0  Errors 0  Warnings" in text or "0 violations" in text.lower() or "0 unconnected" in text.lower(), f"zero-result evidence missing: {report.name}")

    supersession = csv_rows(OUT / "supersession-map.csv")
    need(len(supersession) == 5 and all(r["use_authorized"] == "NO" for r in supersession), "supersession map released historical data")
    need(any("P0.1 CAM" in r["disposition"] and "prohibited" in r["disposition"] for r in supersession), "historical P0.1 CAM not quarantined")
    gate_rows = csv_rows(OUT / "gate-impact.csv")
    need({r["gate_id"] for r in gate_rows} == {"EG-002","EG-003","EG-004","EG-014","EG-015"}, "gate impact membership changed")
    need(all(r["status"] == "partial" and r["gate_closed"] == "NO" for r in gate_rows), "gate falsely closed")
    system_gates = {r["gate_id"]: r for r in csv_rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    for gate_id in ("EG-002", "EG-003", "EG-004", "EG-014", "EG-015"):
        need(system_gates[gate_id]["status"] == "partial", f"{gate_id} must remain partial")
        need("HR-V0-CONFIG-REC-P0.1" not in system_gates[gate_id]["evidence_location"], f"identifier token must remain path-based for {gate_id}")
        need("configuration/hr-v0-config-reconciliation-p0.1/" in system_gates[gate_id]["evidence_location"], f"R163 evidence path missing from {gate_id}")
    acceptance = csv_rows(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 8 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" and not r["approver"] for r in acceptance), "acceptance falsely completed")

    source_hashes = csv_rows(OUT / "source-hash-register.csv")
    for row in source_hashes:
        source = ROOT / row["source_path"]
        need(source.exists() and digest(source) == row["sha256"], f"source hash mismatch: {row['source_path']}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "One carrier-integrated candidate", "V3-P1.15", "91 groups", "E2 P0.4 is current", "Do not drill", WARNING):
        need(token.lower() in page.lower(), f"guide token missing: {token}")
    for name in common - {"file-manifest.csv"}:
        need((ENG / name).read_bytes() == (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    for directory in (ENG, OUT):
        manifest = csv_rows(directory / "file-manifest.csv")
        actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
        need({r["path"] for r in manifest} == actual, f"manifest membership mismatch: {directory.name}")
        for row in manifest:
            path = directory / row["path"]
            need(digest(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest mismatch: {path}")

    if failures:
        print("HR-V0-CONFIG-REC-P0.1 FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-CONFIG-REC-P0.1 PASS")
    print("  carrier-integrated P1.15/P0.2/P0.3 configuration and 91-group BOM reconciled")
    print("  10 holds and 8 acceptance rows remain OPEN; all authority remains false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
