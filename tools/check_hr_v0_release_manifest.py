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
        "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "HR-V0-MECH-P0.6",
        "HR-V0-FW-P0.4",
        "HR-V0-FSA-P0.1",
        "HR-V0-BOM-P0.1",
        "HR-V0-E2-SEQ-P0.1",
        "HR-V0-DYN-INST-P0.1",
        "HR-V0-DYN-EVENT-IF-P0.1",
        "HR-V0-DYN-EVENT-AIN-P0.1",
        "HR-V0-GOV-P0.3",
        "HR-V0-REQ-ATOMIC-P0.2",
        "HR-V0-BUILD-TRAVELER-P0.1",
    }
    missing_identifiers = required_identifiers - identifiers
    if missing_identifiers:
        errors.append(f"metadata missing current product identifiers: {sorted(missing_identifiers)}")
    electrical_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE"),
        {},
    )
    if electrical_product.get("correction_identifier") != "HR-V0-WD-P115-ID-P0.1":
        errors.append("Electrical V3-P1.15 current correction identifier changed")
    if electrical_product.get("supporting_identifiers", [])[:76] != [
        "PCB-P1.0-P1.15-DIRECT",
        "HR-V0-WD-IC-META-P0.1",
        "HR-V0-WD-LAND-P0.1",
        "HR-V0-WD-MOUNT-IF-P0.1",
        "HR-V0-WD-PCBA-RFI-P0.1",
        "HR-V0-WD-PCBA-DATA-P0.2",
        "HR-V0-WD-BOM-BIND-P0.1",
        "HR-V0-WD-CAM-P0.2",
        "HR-V0-E2-HW-P0.4",
        "DXL-STAR-P0.2-CARRIER-CANDIDATE",
        "HR-V0-DXL-STAR-MFG-P0.2",
        "HR-V0-DXL-INJECT-BIND-P0.1",
        "HR-V0-DXL-HARNESS-ALLOC-P0.1",
        "HR-V0-DXL-CURRENT-ENV-P0.1",
        "HR-V0-DXL-PROT-EVAL-P0.1",
        "HR-V0-DXL-PROT-CARRIER-P0.3",
        "HR-V0-DXL-PROT-DFM-P0.1",
        "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1",
        "HR-V0-DXL-CARRIER-INTEGRATION-P0.1",
        "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1",
        "HR-V0-CONFIG-REC-P0.3",
        "HR-V0-CP-P0.6",
        "HR-V0-CP-CONFIG-P0.1",
        "HR-V0-PANEL-COND-P0.1",
        "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE",
        "HR-V0-PANEL-P2P-P0.1",
        "HR-V0-PANEL-NODE-PLACEMENT-P0.1",
        "HR-V0-CONFIG-REC-P0.4",
        "HR-V0-ECAD-WEB-REVIEW-P0.1",
        "HR-V0-COMPUTE-INSTALL-P0.1",
        "HR-V0-U2D2-USB-P0.1",
        "HR-V0-PANEL-RD-P0.1",
        "HR-V0-WD-SUPPLY-P0.1",
        "HR-V0-PNOZ-CONF-P0.1",
        "HR-V0-K1K2-APP-P0.2",
        "HR-V0-GND-BOND-P0.1",
        "HR-V0-COMPUTE-SEL-P0.1",
        "HR-V0-COMPUTE-SUBASM-P0.1",
        "HR-V0-COMPUTE-STORAGE-P0.2",
        "HR-V0-SD-P0.2",
        "HR-V0-24V-IF-P0.2",
        "HR-V0-COMPUTE-IF-P0.1",
        "HR-V0-GRIP-ELEC-P0.1",
        "HR-V0-ACT-AC-CORD-P0.1",
        "HR-V0-XT1-P0.1",
        "HR-V0-LABEL-P0.1",
        "HR-V0-RUNTIME-OBS-IF-P0.1",
        "V3-P1.17-OBSERVATION-P0.5-CANDIDATE",
        "HR-V0-RUNTIME-OBS-CARRIER-P0.5",
        "HR-V0-PI-OBS-CARRIER-P0.1",
        "HR-V0-OBSERVATION-FIELD-HARNESS-P0.1",
        "HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1",
        "HR-V0-RUNTIME-OBS-PINMAP-P0.1",
        "HR-V0-K1K2-APP-P0.3",
        "HR-V0-E2-GND-BOUNDARY-P0.1",
        "HR-V0-E2-PREPOWER-P0.1",
        "HR-V0-P118-DISPOSITION-P0.1",
        "V3-P1.19-VISUAL-CORRECTION-CANDIDATE",
        "HR-V0-P119-VISUAL-CORRECTION-P0.1",
        "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE",
        "HR-V0-P120-WD-INTERLOCK-P0.1",
        "HR-V0-PNOZ-KWD-APP-P0.2",
        "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE",
        "HR-V0-P121-SRA1-SUPPLY-WD-P0.1",
        "HR-V0-P121-APP-EVID-P0.1",
        "HR-V0-P121-CONSOLIDATED-REVIEW-P0.1",
        "HR-V0-P121-VISUAL-REVIEW-P0.1",
        "HR-V0-P121-ROUTING-P0.1",
        "HR-V0-P121-SEGREGATION-HW-P0.1",
        "HR-V0-CONFIG-REC-P0.5",
        "HR-V0-P121-CONDUCTOR-FILL-P0.1",
        "HR-V0-CONFIG-REC-P0.6",
        "HR-V0-P121-TERM-P0.1",
        "HR-V0-CONFIG-REC-P0.7",
        "HR-V0-P121-DCR-DROP-P0.1",
        "HR-V0-CONFIG-REC-P0.8",
    ] or electrical_product.get("supporting_identifiers", [])[76:] != ["HR-V0-OBS-BOM-INTEGRATION-P0.1", "HR-V0-CONFIG-REC-P0.23"] or electrical_product.get("release_state") != "p115_current_p121_unaccepted_r244_nominal_dcr_drop_and_bit_disposition_only_received_complete_circuit_physical_qualified_and_authority_open" or electrical_product.get("control_panel_configuration") != "HR-V0-CP-CONFIG-P0.1" or electrical_product.get("control_panel_geometry_basis") != "HR-V0-CP-P0.6" or electrical_product.get("control_panel_conductor_basis") != "HR-V0-PANEL-COND-P0.1" or electrical_product.get("panel_topology_candidate") != "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE" or electrical_product.get("panel_point_to_point_candidate") != "HR-V0-PANEL-P2P-P0.1" or electrical_product.get("control_panel_node_placement_candidate") != "HR-V0-PANEL-NODE-PLACEMENT-P0.1" or electrical_product.get("configuration_reconciliation") != "HR-V0-CONFIG-REC-P0.23" or electrical_product.get("observation_bom_integration") != "HR-V0-OBS-BOM-INTEGRATION-P0.1" or electrical_product.get("ecad_web_review_surface") != "HR-V0-ECAD-WEB-REVIEW-P0.1" or electrical_product.get("contactor_application_record") != "HR-V0-K1K2-APP-P0.3" or electrical_product.get("contactor_configuration_binding") != "P1.15 current and P1.18 unaccepted contain 32 identical contactor-critical terminal/net rows" or electrical_product.get("e2_grounding_boundary") != "HR-V0-E2-GND-BOUNDARY-P0.1" or electrical_product.get("e2_grounding_configuration_binding") != "26 source/frame/shield endpoint rows identical; SAFETY_0V explicitly differs 41 to 49 through XD0" or electrical_product.get("e2_prepower_test_candidate") != "HR-V0-E2-PREPOWER-P0.1" or electrical_product.get("e2_prepower_configuration_binding") != "55 P1.18 conductor rows; 45 fixed-internal method candidates; 10 blocked door rows; zero released limits or results" or electrical_product.get("p118_disposition_dossier") != "HR-V0-P118-DISPOSITION-P0.1" or electrical_product.get("p118_disposition_summary") != "77 BOM and 308 terminal rows preserved; 106 net names preserved; five nodes and 32 node terminals added; P1.18 remains unaccepted" or electrical_product.get("panel_visual_correction_candidate") != "V3-P1.19-VISUAL-CORRECTION-CANDIDATE" or electrical_product.get("p119_visual_correction_dossier") != "HR-V0-P119-VISUAL-CORRECTION-P0.1" or electrical_product.get("p119_visual_correction_summary") != "84 components, 106 native nets and five synchronized schedules unchanged; 13 project visual passes; P1.19 remains unaccepted" or electrical_product.get("watchdog_interlock_candidate") != "V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE" or electrical_product.get("p120_watchdog_interlock_dossier") != "HR-V0-P120-WD-INTERLOCK-P0.1" or electrical_product.get("p120_watchdog_interlock_summary") != "84 component identities unchanged; exactly seven terminal/net and seven native-net-membership changes; 12 fault screens; 9 open holds; P1.20 remains unaccepted with zero safety credit" or electrical_product.get("p120_pnoz_kwd_application_dossier") != "HR-V0-PNOZ-KWD-APP-P0.2" or electrical_product.get("sra1_supply_watchdog_candidate") != "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE" or electrical_product.get("p121_sra1_supply_watchdog_dossier") != "HR-V0-P121-SRA1-SUPPLY-WD-P0.1" or electrical_product.get("p121_application_evidence_dossier") != "HR-V0-P121-APP-EVID-P0.1" or electrical_product.get("p121_consolidated_review_dossier") != "HR-V0-P121-CONSOLIDATED-REVIEW-P0.1" or electrical_product.get("p121_visual_review_dossier") != "HR-V0-P121-VISUAL-REVIEW-P0.1" or electrical_product.get("p121_protected_routing_dossier") != "HR-V0-P121-ROUTING-P0.1" or electrical_product.get("p121_protected_routing_summary") != "7 route deltas; 9 coordinate-bound planning routes; 14 hot-versus-credited pairs with zero nominal centerline crossings; 9 physical and qualified holds open; no route released" or electrical_product.get("p121_segregation_hardware_dossier") != "HR-V0-P121-SEGREGATION-HW-P0.1" or electrical_product.get("p121_segregation_hardware_summary") != "Phoenix Contact 3240187 exact 25 x 25 x 2000 mm planning candidate; 369.8 mm WD5 envelope; 7 logical conductors; junction, fill, physical and qualified evidence open; no safety credit or route release" or electrical_product.get("p121_conductor_fill_dossier") != "HR-V0-P121-CONDUCTOR-FILL-P0.1" or electrical_product.get("p121_conductor_fill_summary") != "Belden 3057 BL005 exact held 16 AWG candidate for 7 routes; WD5 8.89 percent and WD2 enumerated maximum 2.66 percent geometry screens; total fill, color, DCR, cuts, protection, thermal, physical and qualified evidence open" or electrical_product.get("p121_termination_dossier") != "HR-V0-P121-TERM-P0.1" or electrical_product.get("p121_termination_summary") != "14 endpoint candidates: 12 Phoenix 3200043 insulated 8 mm and 2 Phoenix 3200263 uninsulated 7 mm; exact primary tools held; received qualification, exact bits, installed evidence and acceptance open" or electrical_product.get("p121_dcr_drop_dossier") != "HR-V0-P121-DCR-DROP-P0.1" or electrical_product.get("p121_dcr_drop_summary") != "manufacturer-nominal 4.4 ohm/1000 ft at 20 C; four one-way centerline conductor-only numeric screens; received DCR/cuts/complete circuit and exact bits open":
        errors.append("Electrical V3-P1.15 supporting identifiers or release state changed")
    safety_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-FSA-P0.1"),
        {},
    )
    if safety_product.get("supporting_identifiers") != ["DF-01 ZERO SAFETY CREDIT", "HR-V0-WD-SUPPLY-P0.1", "HR-V0-POWERLOSS-P0.1", "HR-V0-PASSIVE-ARM-RECEIVER-P0.1", "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1", "HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2", "HR-V0-RECEIVER-GUIDE-IF-P0.1", "HR-V0-SRS-P0.2", "HR-V0-FS-REVIEW-ROUTE-P0.1", "HR-V0-WD-PERMIT-TOPOLOGY-P0.1", "HR-V0-P120-WD-INTERLOCK-P0.1", "HR-V0-PNOZ-KWD-APP-P0.2", "HR-V0-P121-SRA1-SUPPLY-WD-P0.1", "HR-V0-P121-APP-EVID-P0.1"] or safety_product.get("release_state") != "r235_p121_application_evidence_route_zero_safety_credit_questions_unsent_tests_unexecuted_plr_sil_and_qualified_review_open" or safety_product.get("watchdog_permit_topology_proof") != "HR-V0-WD-PERMIT-TOPOLOGY-P0.1" or safety_product.get("watchdog_interlock_candidate") != "HR-V0-P120-WD-INTERLOCK-P0.1" or safety_product.get("p120_pnoz_kwd_application_dossier") != "HR-V0-PNOZ-KWD-APP-P0.2" or safety_product.get("p121_sra1_supply_watchdog_dossier") != "HR-V0-P121-SRA1-SUPPLY-WD-P0.1" or safety_product.get("p121_application_evidence_dossier") != "HR-V0-P121-APP-EVID-P0.1":
        errors.append("HR-V0-FSA-P0.1 supporting identifiers or fail-closed state changed")
    mechanical_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-MECH-P0.6"),
        {},
    )
    if mechanical_product.get("supporting_identifiers") != [
        "HR-V0-ROBOTIS-IF-P0.1",
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
        "HR-V0-COLLAPSE-ENV-P0.1",
        "HR-V0-PASSIVE-ARM-RECEIVER-P0.1",
        "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1",
        "HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2",
        "HR-V0-RECEIVER-GUIDE-IF-P0.1",
        "HR-V0-ELBOW-TRADE-P0.1",
        "HR-V0-GRIP-P0.2",
        "HR-V0-GRIP-CAD-ACQ-P0.1",
        "HR-V0-GRIP-CAD-ACQ-P0.2",
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
        "HR-V0-DYN-TRACE-P0.1",
        "HR-V0-FAB-SRC-P0.5",
        "HR-V0-BOSTON-FAB-ROUTE-P0.3",
        "HR-V0-BOSTON-FAB-ROUTE-P0.4",
        "HR-V0-FAB-INPUT-P0.1",
        "HR-V0-MECH-DFM-DATA-P0.1",
        "HR-V0-MECH-BOM-BIND-P0.2",
        "HR-V0-MECH-MFG-REVIEW-P0.1",
        "HR-V0-MECH-PARITY-P0.1",
        "HR-V0-MECH-R0.1-PRELIMINARY-SUPERSEDED-ARM",
        "HR-V0-FAB-RFI-P0.2-WITHDRAWN",
        "HR-V0-FRAME-P0.2",
        "HR-V0-CONFIG-REC-P0.3",
        "HR-V0-ARM-ARCH-P0.7",
        "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
    ]:
        errors.append("integrated P0.8 mechanical supporting identifiers changed or are incomplete")
    if mechanical_product.get("coordinate_convention") != "HR-V0-FRAME-CONV-P0.1":
        errors.append("integrated P0.8 coordinate convention missing or changed")
    if mechanical_product.get("release_state") != "integrated_p06_hold_with_exact_p08_complete_arm_p07_inherited_basis_physical_evidence_open_qualified_release_open":
        errors.append("integrated P0.8 fail-closed release state changed")
    if mechanical_product.get("current_arm_architecture") != "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE" or mechanical_product.get("inherited_analytical_basis") != ["HR-V0-MECH-P0.6", "HR-V0-ARM-ARCH-P0.7"] or mechanical_product.get("manufacturing_identity") != "HR-V0-MECH-BOM-BIND-P0.2":
        errors.append("integrated P0.8 analytical/manufacturing identity split changed")
    firmware_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-FW-P0.4"),
        {},
    )
    if firmware_product.get("supporting_identifiers") != [
        "HR-V0-WD-BUILD-P0.2",
        "HR-V0-SUP-P0.3",
        "HR-V0-ACT-P0.3",
        "HR-V0-DXL-TRANSPORT-P0.3",
        "HR-V0-DXL-CURRENT-ENV-P0.1",
        "HR-V0-LIMITS-P0.2",
        "HR-V0-HS-P0.3",
        "HR-V0-HOST-DEPLOY-P0.1",
        "HR-V0-RPI-OS-SBOM-P0.1",
        "HR-V0-STALE-AUTH-P0.1",
        "HR-V0-KIN-P0.1",
        "HR-V0-RUNTIME-P0.1",
        "HR-V0-RUNTIME-BACKENDS-P0.1",
        "HR-V0-RUNTIME-OBS-PINMAP-P0.1",
        "HR-V0-EVID-LOG-P0.1",
        "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
        "HR-V0-MECH-BOM-BIND-P0.2",
    ] or firmware_product.get("release_state") != (
        "r236_required_hash_chained_runtime_evidence_sink_source_tested_configuration_calibration_timing_storage_target_hil_and_physical_evidence_unresolved"
    ) or firmware_product.get("inherited_kinematic_basis") != "HR-V0-ARM-ARCH-P0.7" or firmware_product.get("runtime_evidence_log") != "HR-V0-EVID-LOG-P0.1":
        errors.append("HR-V0-FW-P0.4 supporting identifiers or fail-closed release state changed")
    bom_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-BOM-P0.1"),
        {},
    )
    if bom_product.get("supporting_identifiers", [])[:28] != ["EVALUATION-BATCH-A", "HR-V0-MECH-EVAL-P0.1", "HR-V0-EVAL-BATCH-A-ACQ-P0.1", "HR-V0-EVAL-BATCH-A-RCV-P0.1", "HR-V0-ACT-AC-CORD-P0.1", "HR-V0-MECH-BOM-BIND-P0.2", "HR-V0-WD-BOM-BIND-P0.1", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "HR-V0-DXL-STAR-MFG-P0.2", "HR-V0-DXL-INJECT-BIND-P0.1", "HR-V0-DXL-HARNESS-ALLOC-P0.1", "HR-V0-DXL-PROT-CARRIER-P0.3", "HR-V0-DXL-PROT-CARRIER-HARNESS-P0.1", "HR-V0-DXL-CARRIER-INTEGRATION-P0.1", "HR-V0-CONFIG-REC-P0.3", "HR-V0-PANEL-NODE-PLACEMENT-P0.1", "HR-V0-CONFIG-REC-P0.4", "HR-V0-P121-SEGREGATION-HW-P0.1", "HR-V0-CONFIG-REC-P0.5", "HR-V0-P121-CONDUCTOR-FILL-P0.1", "HR-V0-CONFIG-REC-P0.6", "HR-V0-P121-TERM-P0.1", "HR-V0-CONFIG-REC-P0.7", "HR-V0-CONFIG-REC-P0.8", "HR-V0-XT1-P0.1", "HR-V0-LABEL-P0.1", "HR-V0-COMPUTE-STORAGE-P0.2", "HR-V0-LOT-A-SRC-P0.1"] or bom_product.get("supporting_identifiers", [])[28:] != ["HR-V0-OBS-BOM-INTEGRATION-P0.1", "HR-V0-CONFIG-REC-P0.23"] or bom_product.get("release_state") != (
        "r259_108_group_bom_with_source_bound_observation_assemblies_and_quantities_mounting_cut_physical_qualified_and_authority_evidence_open_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    ) or bom_product.get("system_group_count") != 108 or bom_product.get("configuration_reconciliation") != "HR-V0-CONFIG-REC-P0.23" or bom_product.get("observation_bom_integration") != "HR-V0-OBS-BOM-INTEGRATION-P0.1" or bom_product.get("p121_segregation_hardware") != "HR-V0-P121-SEGREGATION-HW-P0.1" or bom_product.get("p121_conductor_fill") != "HR-V0-P121-CONDUCTOR-FILL-P0.1" or bom_product.get("p121_termination") != "HR-V0-P121-TERM-P0.1" or bom_product.get("lot_a_source_reconciliation") != "HR-V0-LOT-A-SRC-P0.1":
        errors.append("HR-V0-BOM-P0.1 supporting identifiers or fail-closed release state changed")
    commissioning_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-E2-SEQ-P0.1"),
        {},
    )
    if commissioning_product.get("supporting_identifiers") != [
        "HR-V0-E2-HW-P0.4",
        "HR-V0-E2-EVIDENCE-P0.2",
        "HR-V0-E2-GND-BOUNDARY-P0.1",
        "HR-V0-E2-PREPOWER-P0.1",
        "HR-V0-STALE-AUTH-P0.1",
        "AUDIT-ELEC-002",
        "INSPECT-ELEC-010",
        "TEST-ELEC-008",
        "INSPECT-E2-001",
        "INSPECT-E2-002",
        "TEST-E2-001",
        "TEST-E2-002",
        "AUDIT-E2-001",
    ] or commissioning_product.get("release_state") != "e2_grounding_and_prepower_candidates_controlled_zero_limits_results_or_authority_not_authorized_for_connection_or_energization" or commissioning_product.get("prepower_test_candidate") != "HR-V0-E2-PREPOWER-P0.1":
        errors.append("HR-V0-E2-SEQ-P0.1 supporting identifiers or fail-closed state changed")
    instrumentation_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-DYN-INST-P0.1"),
        {},
    )
    if instrumentation_product.get("supporting_identifiers") != ["HR-V0-DYN-CHAR-P0.1", "HR-V0-DYN-TRACE-P0.1", "HR-V0-DYN-EVENT-IF-P0.1", "HR-V0-DYN-EVENT-AIN-P0.1", "HR-V0-EVENT-TAP-DISP-P0.1", "EG-025", "EG-026"] or instrumentation_product.get("release_state") != (
        "four_exact_evaluation_candidates_complete_physical_chain_ranges_calibration_and_authority_open_no_safety_credit"
    ):
        errors.append("HR-V0-DYN-INST-P0.1 supporting identifiers or fail-closed state changed")
    event_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-DYN-EVENT-IF-P0.1"),
        {},
    )
    if event_product.get("supporting_identifiers") != ["TE-009", "DCH-001", "DCH-008", "DCH-009", "DCH-010", "DCH-011", "DCH-014", "DCH-X01", "DCH-X02", "EG-025", "EG-026"] or event_product.get("release_state") != (
        "historical_not_preferred_two_exact_iso1212evm_evaluation_candidates_native_connected_ecad_erc_clean_field_connection_prohibited_noninterference_timing_physical_evidence_and_qualified_review_open_zero_safety_credit"
    ):
        errors.append("HR-V0-DYN-EVENT-IF-P0.1 supporting identifiers or fail-closed state changed")
    event_ain_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-DYN-EVENT-AIN-P0.1"),
        {},
    )
    if event_ain_product.get("supporting_identifiers") != ["TE-009B", "HR-V0-EVENT-TAP-DISP-P0.1", "DCH-008", "DCH-009", "DCH-010", "DCH-011", "DCH-014", "DCH-X01", "DCH-X02", "EG-025", "EG-026"] or event_ain_product.get("release_state") != (
        "preferred_output_side_evaluation_branch_seven_exact_amc3330evm_candidates_all_seven_t7_differential_pairs_native_ecad_erc_clean_catalog_only_field_adapter_selection_rejected_all_field_connections_prohibited_noninterference_timing_physical_evidence_and_qualified_review_open_zero_safety_credit"
    ):
        errors.append("HR-V0-DYN-EVENT-AIN-P0.1 supporting identifiers or fail-closed state changed")
    governance_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-GOV-P0.3"),
        {},
    )
    if governance_product.get("supporting_identifiers") != ["HR-V0-GOV-P0.2", "HR-V0-GOV-P0.1", "GOV-001", "AUDIT-GOV-001", "SOL-R12-B-018", "HR-V0-REQ-ATOMIC-P0.2"] or governance_product.get("release_state") != (
        "coverage_snapshot_internally_audited_atomic_children_candidate_people_evidence_approval_history_open_not_approved"
    ):
        errors.append("HR-V0-GOV-P0.3 supporting identifiers or fail-closed state changed")
    requirements_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-REQ-ATOMIC-P0.2"),
        {},
    )
    if requirements_product.get("supporting_identifiers") != ["HR-V0-REQ-ATOMIC-P0.1", "GOV-001", "SOL-R12-N-004", "HR-V0-GOV-P0.3"] or requirements_product.get("release_state") != (
        "internally_audited_atomic_child_candidate_all_draft_unexecuted_unapproved_independent_review_required_not_approved"
    ):
        errors.append("HR-V0-REQ-ATOMIC-P0.2 supporting identifiers or fail-closed state changed")
    assembly_product = next(
        (item for item in products if isinstance(item, dict) and item.get("identifier") == "HR-V0-BUILD-TRAVELER-P0.1"),
        {},
    )
    if assembly_product.get("supporting_identifiers") != ["HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "HR-V0-E2-SEQ-P0.1", "HR-V0-GOV-P0.3", "HR-V0-CONFIG-REC-P0.3", "HR-V0-CONFIG-REC-P0.4", "HR-V0-CONFIG-REC-P0.5", "HR-V0-CONFIG-REC-P0.6", "HR-V0-CONFIG-REC-P0.7", "HR-V0-CONFIG-REC-P0.8", "HR-V0-MECH-BOM-BIND-P0.2", "HR-V0-CONFIG-REC-P0.23"] or assembly_product.get("release_state") != (
        "integrated_unpowered_sequence_bound_to_held_p08_mechanics_all_steps_not_authorized_not_executed_connection_and_energization_prohibited_not_approved"
    ):
        errors.append("HR-V0-BUILD-TRAVELER-P0.1 supporting identifiers or fail-closed state changed")

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
