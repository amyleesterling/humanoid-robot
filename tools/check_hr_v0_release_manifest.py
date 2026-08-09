from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

from generate_hr_v0_release_manifest import (
    FIELDS,
    MANIFEST,
    MANIFEST_REL,
    ROOT,
    index_blobs,
    package_files,
    role_for,
    untracked_package_files,
)


METADATA = ROOT / "release" / "hr-v0" / "release-candidate.json"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail unless the repository has no tracked or untracked non-ignored changes.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    if not METADATA.is_file():
        errors.append("release-candidate.json is missing")
        metadata: dict[str, object] = {}
    else:
        metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    required_metadata = {
        "schema": "project-button-release-candidate-v1",
        "candidate_id": "HR-V0-RC-P0.1",
        "system_baseline": "HR-30-SYS-R0.2",
        "status": "PRELIMINARY_NOT_APPROVED_FOR_FABRICATION_OR_ENERGIZATION",
        "file_manifest": MANIFEST_REL,
    }
    for key, expected in required_metadata.items():
        if metadata.get(key) != expected:
            errors.append(f"metadata {key}: expected {expected!r}, got {metadata.get(key)!r}")

    products = metadata.get("current_products", [])
    identifiers = {
        item.get("identifier")
        for item in products
        if isinstance(item, dict)
    }
    required_identifiers = {
        "Project Button Electrical V3-P1.14",
        "HR-V0-MECH-P0.6",
        "HR-V0-FW-P0.4",
        "HR-V0-FSA-P0.1",
        "HR-V0-BOM-P0.1",
        "HR-V0-E2-SEQ-P0.1",
    }
    missing_identifiers = required_identifiers - identifiers
    if missing_identifiers:
        errors.append(f"metadata missing current product identifiers: {sorted(missing_identifiers)}")
    electrical_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "Project Button Electrical V3-P1.14"),
        {},
    )
    if electrical_product.get("supporting_identifiers") != [
        "PCB-P0.6",
        "HR-V0-WD-LAND-P0.1",
        "DXL-STAR-P0.1",
        "HR-V0-CP-P0.6",
        "HR-V0-COMPUTE-INSTALL-P0.1",
        "HR-V0-U2D2-USB-P0.1",
        "HR-V0-PANEL-RD-P0.1",
        "HR-V0-WD-SUPPLY-P0.1",
        "HR-V0-PNOZ-CONF-P0.1",
        "HR-V0-K1K2-APP-P0.2",
        "HR-V0-GND-BOND-P0.1",
        "HR-V0-COMPUTE-SEL-P0.1",
        "HR-V0-COMPUTE-SUBASM-P0.1",
        "HR-V0-SD-P0.2",
        "HR-V0-24V-IF-P0.2",
        "HR-V0-E2-HW-P0.2",
        "HR-V0-COMPUTE-IF-P0.1",
        "HR-V0-GRIP-ELEC-P0.1",
    ] or electrical_product.get("release_state") != "correction_candidate_not_released":
        errors.append("Electrical V3-P1.14 supporting identifiers or release state changed")
    safety_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-FSA-P0.1"),
        {},
    )
    if safety_product.get("supporting_identifiers") != ["DF-01 ZERO SAFETY CREDIT", "HR-V0-WD-SUPPLY-P0.1"] or safety_product.get("release_state") != "allocation_candidate_no_plr_or_sil_assigned":
        errors.append("HR-V0-FSA-P0.1 supporting identifiers or fail-closed state changed")
    mechanical_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-MECH-P0.6"),
        {},
    )
    if mechanical_product.get("supporting_identifiers") != [
        "HR-V0-ROBOTIS-IF-P0.1",
        "HR-V0-ARM-ARCH-P0.7",
        "HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE",
        "HR-V0-ARM-ARCH-P0.9-X430-INTEGRATED-CANDIDATE",
        "HR-V0-ARM-ARCH-P1.0-X430-CLEARANCE-CANDIDATE",
        "HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE",
        "HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE",
        "HR-V0-FR12-MASS-MET-P0.1",
        "HR-V0-X430-DUTY-P0.1",
        "HR-V0-X430-FIXTURE-P0.1",
        "HR-V0-X430-FIXTURE-IF-P0.2",
        "HR-V0-X430-FIXTURE-SUP-P0.1",
        "HR-V0-X430-LOAD-RIG-P0.1",
        "HR-V0-X430-OUTPUT-IF-P0.1",
        "HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.3",
        "HR-V0-X430-BRAKE-SUP-P0.1",
        "HR-V0-FX104-C01-FAB-P0.1",
        "HR-V0-HS-P0.3",
        "HR-V0-J2-STOP-P0.1",
        "HR-V0-STOP-REGION-P0.1",
        "HR-V0-STOP-BUDGET-P0.1",
        "HR-V0-ELBOW-TRADE-P0.1",
        "HR-V0-GRIP-P0.2",
        "HR-V0-GRIP-CAD-ACQ-P0.1",
        "HR-V0-GRIP-ACQ-P0.2",
        "HR-V0-GRIP-SRC-P0.3",
        "HR-V0-GRIP-SRC-ROUTE-P0.4",
        "HR-V0-GRIP-ALT-P0.1",
        "HR-V0-GRIP-ADAPT-P0.1",
        "HR-V0-GRIP-SEL-P0.1",
        "HR-V0-OBJ-CTRL-P0.1",
        "HR-V0-GRIP-H104-SRC-P0.1",
        "HR-V0-GUARD-P0.3",
        "HR-V0-GUARD-RET-P0.1",
        "HR-V0-GUARD-IMPACT-P0.1",
        "HR-V0-DYN-CHAR-P0.1",
        "HR-V0-FAB-SRC-P0.5",
        "HR-V0-BOSTON-FAB-ROUTE-P0.2",
        "HR-V0-MECH-R0.1-PRELIMINARY-SUPERSEDED-ARM",
        "HR-V0-FAB-RFI-P0.2-WITHDRAWN",
        "HR-V0-FRAME-P0.2",
    ]:
        errors.append("HR-V0-MECH-P0.6 supporting identifiers changed or are incomplete")
    if mechanical_product.get("release_state") != "integrated_exact_coordinate_candidate_not_released_for_fabrication_or_energization":
        errors.append("HR-V0-MECH-P0.6 fail-closed release state changed")
    firmware_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-FW-P0.4"),
        {},
    )
    if firmware_product.get("supporting_identifiers") != [
        "HR-V0-WD-BUILD-P0.2",
        "HR-V0-SUP-P0.3",
        "HR-V0-ACT-P0.3",
        "HR-V0-DXL-TRANSPORT-P0.3",
        "HR-V0-LIMITS-P0.2",
        "HR-V0-MECH-P0.6",
        "HR-V0-ARM-ARCH-P0.7",
        "HR-V0-HS-P0.3",
    ] or firmware_product.get("release_state") != (
        "source_transport_and_reproducible_watchdog_candidate_not_installed_flashed_connected_or_hil_validated"
    ):
        errors.append("HR-V0-FW-P0.4 supporting identifiers or fail-closed release state changed")
    bom_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-BOM-P0.1"),
        {},
    )
    if bom_product.get("supporting_identifiers") != ["EVALUATION-BATCH-A", "HR-V0-MECH-EVAL-P0.1"] or bom_product.get("release_state") != (
        "closure_register_candidate_no_complete_machine_procurement_release"
    ):
        errors.append("HR-V0-BOM-P0.1 supporting identifiers or fail-closed release state changed")
    commissioning_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-E2-SEQ-P0.1"),
        {},
    )
    if commissioning_product.get("supporting_identifiers") != [
        "HR-V0-E2-HW-P0.2",
        "AUDIT-ELEC-002",
        "INSPECT-ELEC-010",
        "TEST-ELEC-008",
        "INSPECT-E2-001",
        "INSPECT-E2-002",
        "TEST-E2-001",
        "TEST-E2-002",
        "AUDIT-E2-001",
    ] or commissioning_product.get("release_state") != "templates_not_executed_not_authorized_for_energization":
        errors.append("HR-V0-E2-SEQ-P0.1 supporting identifiers or fail-closed state changed")

    if not MANIFEST.is_file():
        errors.append(f"manifest missing: {MANIFEST_REL}")
        rows: list[dict[str, str]] = []
        headers: list[str] = []
    else:
        with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
        if tuple(headers) != FIELDS:
            errors.append(f"manifest columns: expected {FIELDS}, got {tuple(headers)}")

    actual_paths = package_files()
    blobs = index_blobs(actual_paths)
    untracked = untracked_package_files()
    if untracked:
        errors.append(f"untracked non-ignored package files are not allowed: {untracked}")
    manifested_paths = [row.get("path", "") for row in rows]
    if manifested_paths != sorted(manifested_paths):
        errors.append("manifest paths are not deterministically sorted")
    if len(manifested_paths) != len(set(manifested_paths)):
        errors.append("manifest contains duplicate paths")

    missing = sorted(set(actual_paths) - set(manifested_paths))
    extra = sorted(set(manifested_paths) - set(actual_paths))
    if missing:
        errors.append(f"manifest missing package files: {missing}")
    if extra:
        errors.append(f"manifest contains absent package files: {extra}")

    for row in rows:
        relative = row.get("path", "")
        if not relative or relative not in actual_paths:
            continue
        content = blobs[relative]
        expected_role = role_for(relative)
        if row.get("role") != expected_role:
            errors.append(f"{relative}: role {row.get('role')!r}, expected {expected_role!r}")
        expected_size = str(len(content))
        if row.get("size_bytes") != expected_size:
            errors.append(f"{relative}: size {row.get('size_bytes')!r}, expected {expected_size}")
        expected_hash = hashlib.sha256(content).hexdigest()
        if row.get("sha256") != expected_hash:
            errors.append(f"{relative}: SHA-256 mismatch")

    dirty = git("status", "--porcelain=v1", "--untracked-files=all")
    if args.require_clean:
        if dirty:
            errors.append("repository is not clean:\n" + dirty)

    if errors:
        raise SystemExit("HR-V0 release-candidate manifest check failed:\n- " + "\n- ".join(errors))

    head = git("rev-parse", "HEAD")
    print(f"HR-V0-RC-P0.1 manifest check passed: {len(rows)} package files")
    if dirty:
        print(f"Repository HEAD at check time: {head}; working candidate contains uncommitted changes")
    else:
        print(f"Git commit containing checked candidate: {head}")
    print("Configuration gate EG-002 remains PARTIAL until merge and formal acceptance.")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")


if __name__ == "__main__":
    main()
