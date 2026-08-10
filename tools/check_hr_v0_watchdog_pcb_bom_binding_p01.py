#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-WD-BOM-BIND-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
CAM = ROOT / "release" / "hr-v0" / "watchdog-pcb-cam-p0.2"
OUT = ROOT / "release" / "hr-v0" / "watchdog-pcb-bom-binding-p0.1"
BINDING = ROOT / "bom" / "hr-v0-watchdog-pcb-binding.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    binding_rows = rows(BINDING)
    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    assembly_status = json.loads((ASSEMBLY / "package-status.json").read_text(encoding="utf-8"))
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    assembly_bom = rows(ASSEMBLY / "board-assembly-bom.csv")
    placements = rows(ASSEMBLY / "assembly-placement-reference.csv")
    features = rows(ASSEMBLY / "mechanical-feature-register.csv")
    holds = rows(ASSEMBLY / "assembly-data-holds.csv")
    file_states = {row["file_id"]: row for row in rows(ASSEMBLY / "assembly-data-file-state.csv")}
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    cam_status = json.loads((CAM / "package-status.json").read_text(encoding="utf-8"))

    if len(binding_rows) != 1:
        errors.append("binding register is not exactly one BOM-048 row")
        binding = {}
    else:
        binding = binding_rows[0]
    expected_identity = {
        "bom_item_id": "BOM-048",
        "board_id": "PCB-P1.0",
        "electrical_revision": "Project Button Electrical V3-P1.15",
        "current_system_binding": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE / PCB-P1.0 direct native binding",
        "assembly_data_id": "HR-V0-WD-PCBA-DATA-P0.2",
        "populated_references": "42",
        "bom_lines": "16",
        "mechanical_features": "4",
        "cam_exists_at_issue": "FALSE",
        "current_cam_review_identifier": "HR-V0-WD-CAM-P0.2",
        "current_cam_review_exists": "TRUE",
        "supplier_xyrs_exists": "FALSE",
        "fabrication_authorized": "FALSE",
        "warning": WARNING,
    }
    for key, expected in expected_identity.items():
        if binding.get(key) != expected:
            errors.append(f"binding {key} != {expected!r}")
    for path_field, hash_field in (("native_pcb_path", "native_pcb_sha256"), ("assembly_bom_path", "assembly_bom_sha256"), ("placement_path", "placement_sha256")):
        path = ROOT / binding.get(path_field, "")
        if not path.is_file() or digest(path) != binding.get(hash_field):
            errors.append(f"binding file/hash mismatch: {path_field}")

    item = bom.get("BOM-048", {})
    expected_mpn = "Project Button watchdog PCB PCB-P1.0 / Electrical V3-P1.15 direct-bound; assembly data HR-V0-WD-PCBA-DATA-P0.2"
    if item.get("manufacturer") != "Custom PCB / provider SELECTION REQUIRED" or item.get("manufacturer_part_number") != expected_mpn or item.get("quantity") != "1" or item.get("baseline_status") != "exact_candidate_hold":
        errors.append("BOM-048 does not carry the exact held current PCB identity")
    closed = closure.get("BOM-048", {})
    if closed.get("closure_class") != "exact_candidate_hold" or closed.get("order_code_state") != "EXACT CANDIDATE" or closed.get("allowed_action") != "HOLD":
        errors.append("BOM-048 closure state is not exact-candidate hold")

    if assembly_status.get("board") != "PCB-P1.0 / Electrical V3-P1.15" or assembly_status.get("board_sha256") != binding.get("native_pcb_sha256"):
        errors.append("P0.2 assembly status board identity differs from binding")
    if assembly_status.get("cam_exists") is not True or assembly_status.get("cam_released") is not False:
        errors.append("P0.2 assembly status does not encode current quarantined CAM")
    for key in ("supplier_normalized_xyrs_exists", "provider_selected", "provider_contacted", "files_uploaded", "fabrication_authorized", "assembly_authorized", "physical_article_exists", "energization_authorized", "safety_credit"):
        if assembly_status.get(key) is not False:
            errors.append(f"P0.2 assembly status {key} is not false")
    if len(assembly_bom) != 16 or sum(int(row.get("quantity_per_board", "0")) for row in assembly_bom) != 42:
        errors.append("assembly BOM is not 16 lines totaling 42 populated references")
    if len(placements) != 42 or len(features) != 4:
        errors.append("placement/mechanical-feature counts differ from 42/4")
    if len(holds) != 12 or any(row.get("status") != "OPEN" for row in holds):
        errors.append("the twelve P0.2 assembly holds are not all open")
    for file_id, required_state in (("WD-FILE-006", "INTERNAL REVIEW EXISTS - NOT SUPPLIER RELEASED"), ("WD-FILE-008", "DOES NOT EXIST"), ("WD-FILE-010", "DOES NOT EXIST")):
        if file_states.get(file_id, {}).get("state") != required_state:
            errors.append(f"{file_id} absence state changed")

    for key in ("provider_selected", "provider_contacted", "files_uploaded", "supplier_normalized_xyrs_exists", "physical_article_exists", "fabrication_authorized", "assembly_authorized", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        if status.get(key) is not False:
            errors.append(f"binding package status {key} is not false")
    if status.get("cam_exists_at_issue") is not False or status.get("current_cam_review_exists") is not True or status.get("current_cam_review_released") is not False:
        errors.append("binding package does not distinguish R149 absence from current quarantined CAM")
    if status.get("identifier") != "HR-V0-WD-BOM-BIND-P0.1" or status.get("open_assembly_holds") != 12:
        errors.append("binding package identity or hold count changed")
    source_hashes = status.get("source_hashes", {})
    if len(source_hashes) != 9:
        errors.append("binding package does not hash exactly nine controlled sources")
    for relative, expected_hash in source_hashes.items():
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected_hash:
            errors.append(f"binding package source hash mismatch: {relative}")
    if cam_status.get("identifier") != "HR-V0-WD-CAM-P0.2" or cam_status.get("direct_p115_binding") is not True or cam_status.get("p115_parity_evidence") is not None or cam_status.get("cam_generated") is not True or cam_status.get("cam_released") is not False:
        errors.append("current CAM review package state is missing or released")
    for key in ("supplier_normalized_xyrs_exists", "supplier_selected", "supplier_contacted", "files_uploaded", "quotation_requested", "fabrication_authorized", "assembly_authorized", "physical_article_exists", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        if cam_status.get(key) is not False:
            errors.append(f"current CAM review package {key} is not false")

    products = release.get("current_products", [])
    electrical = next((x for x in products if x.get("domain") == "electrical"), {})
    bom_product = next((x for x in products if x.get("domain") == "bill_of_materials"), {})
    for product, label in ((electrical, "electrical"), (bom_product, "BOM")):
        if "HR-V0-WD-BOM-BIND-P0.1" not in product.get("supporting_identifiers", []):
            errors.append(f"release candidate {label} domain omits the binding")
    for gate_id in ("EG-003", "EG-004"):
        gate = gates.get(gate_id, {})
        if gate.get("status") != "partial" or "bom/hr-v0-watchdog-pcb-binding.csv" not in gate.get("evidence_location", ""):
            errors.append(f"{gate_id} does not retain partial status with binding evidence")
    for token in ("font:clamp(16px", "PCB-P1.0", "Historical P0.1 CAM", "HR-V0-WD-CAM-P0.2", "Electrical V3-P1.15", "42", "16", "Twelve assembly holds remain open", "NOT MACHINE XYRS"):
        if token not in guide:
            errors.append(f"interactive guide omits {token!r}")

    if errors:
        print("HR-V0 watchdog PCB BOM binding P0.1 check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0-WD-BOM-BIND-P0.1 PASS: BOM-048 binds PCB-P1.0 to P0.2 assembly data, 42 placements, 16 BOM lines and 4 NPTH features")
    print("Twelve assembly holds open; current CAM review exists but supplier XYRS/release, fabrication, assembly, connection, motion, energization and safety credit remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
