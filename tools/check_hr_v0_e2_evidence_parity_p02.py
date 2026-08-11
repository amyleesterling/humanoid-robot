"""Validate the fail-closed HR-V0 E2 evidence-parity contract P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "tests" / "e2" / "hr-v0-e2-evidence-contract-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
UNPOWERED = ROOT / "tests" / "forms" / "hr-v0-e2-unpowered-configuration-template-p0.2.csv"
AUTH = ROOT / "tests" / "forms" / "hr-v0-e2-authorization-template-p0.2.csv"
HARDWARE = ROOT / "tests" / "forms" / "hr-v0-e2-safety-logic-template.csv"
SOFTWARE = ROOT / "tests" / "forms" / "hr-v0-e2-software-authority-template-p0.1.csv"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
DOC = ROOT / "docs" / "hr-v0-e2-evidence-parity-p0.2.md"
GUIDE = ROOT / "release" / "hr-v0" / "e2-evidence-parity-p0.2" / "index.html"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    required = [
        DOC,
        GUIDE,
        UNPOWERED,
        AUTH,
        HARDWARE,
        SOFTWARE,
        GATES,
        PKG / "configuration-identity-register.csv",
        PKG / "case-pairing-register.csv",
        PKG / "form-sha256-register.csv",
        PKG / "open-holds.csv",
        PKG / "package-status.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    unpowered = read_csv(UNPOWERED)
    if len(unpowered) != 1 or None in unpowered[0] or any(value is None for value in unpowered[0].values()):
        errors.append("P0.2 unpowered form is not one aligned row")
    else:
        row = unpowered[0]
        expected = {
            "record_id": "NOT-EXECUTED",
            "release_candidate_id": "HR-V0-RC-P0.1",
            "file_manifest_sha256": "",
            "core_ecad_revision": "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
            "system_view_revision": "V3-P1.17-OBSERVATION-P0.5-CANDIDATE",
            "watchdog_pcb_revision": "PCB-P1.0 / HR-V0-WD-PCBA-DATA-P0.2 / HR-V0-WD-CAM-P0.2",
            "mechanical_arm_revision": "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE",
            "mechanical_manufacturing_revision": "HR-V0-MECH-BOM-BIND-P0.2 / HR-V0-MECH-MFG-REVIEW-P0.1",
            "configuration_reconciliation_id": "HR-V0-CONFIG-REC-P0.3",
            "actuator_source_physically_absent": "NOT EXECUTED",
            "actuator_branches_disconnected_covered": "NOT EXECUTED",
            "status": "NOT EXECUTED",
            "warning": WARNING,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"unpowered form {key!r} is {row.get(key)!r}, expected {value!r}")
        if "V3-P1.8" in ",".join(row.values()):
            errors.append("obsolete P1.8 leaked into P0.2 unpowered form")

    authorization = read_csv(AUTH)
    if len(authorization) != 1 or None in authorization[0] or any(value is None for value in authorization[0].values()):
        errors.append("P0.2 authorization form is not one aligned row")
    else:
        row = authorization[0]
        expected = {
            "release_candidate_id": "HR-V0-RC-P0.1",
            "configuration_reconciliation_id": "HR-V0-CONFIG-REC-P0.3",
            "e2_hardware_slice_id": "HR-V0-E2-HW-P0.4",
            "e2_evidence_contract_id": "HR-V0-E2-EVIDENCE-P0.2",
            "eg021_hardware_logic_record": "",
            "eg021_software_authority_record": "",
            "actuator_source_physically_absent": "NOT EXECUTED",
            "actuator_branches_disconnected_covered": "NOT EXECUTED",
            "authorization_state": "NOT AUTHORIZED",
            "status": "NOT EXECUTED",
            "warning": WARNING,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"authorization form {key!r} is {row.get(key)!r}, expected {value!r}")
        for field in (
            "test_director_signature",
            "qualified_electrical_reviewer_signature",
            "functional_safety_reviewer_signature",
            "independent_witness_signature",
        ):
            if field not in row or row[field]:
                errors.append(f"authorization signature field is missing or prefilled: {field}")

    identities = read_csv(PKG / "configuration-identity-register.csv")
    if len(identities) != 8 or any(row.get("execution_state") != "NOT EXECUTED" for row in identities):
        errors.append("configuration register must retain eight unexecuted identities")
    if any(row.get("warning") != WARNING for row in identities):
        errors.append("configuration register warning changed")

    hardware = {row["case_id"]: row for row in read_csv(HARDWARE)}
    software = {row["case_id"]: row for row in read_csv(SOFTWARE)}
    pairs = read_csv(PKG / "case-pairing-register.csv")
    expected_cases = [f"E2-SL-{index:03d}" for index in range(1, 21)]
    if [row.get("case_id") for row in pairs] != expected_cases:
        errors.append("case-pairing register must contain E2-SL-001 through E2-SL-020 in order")
    for row in pairs:
        case_id = row.get("case_id", "")
        hw = hardware.get(case_id, {})
        sw = software.get(case_id, {})
        if not hw or not sw:
            errors.append(f"{case_id} is not present in both source forms")
            continue
        checks = {
            "scope": sw.get("scope"),
            "hardware_power_path_expected": sw.get("hardware_power_path_expected"),
            "required_supervisor_state": sw.get("expected_supervisor_state"),
            "required_active_trajectory": sw.get("expected_active_trajectory"),
            "required_torque_enable_request": sw.get("expected_torque_enable_request"),
            "required_stale_replay_result": sw.get("stale_replay_expected"),
        }
        for key, value in checks.items():
            if row.get(key) != value:
                errors.append(f"{case_id} {key} diverges from software authority form")
        expected_hw_path = "ON" if hw.get("expected_k1_a1") == "ON" and hw.get("expected_k2_a1") == "ON" else "OFF"
        if row.get("hardware_power_path_expected") != expected_hw_path:
            errors.append(f"{case_id} pairing diverges from hardware coil expectation")
        if row.get("required_active_trajectory") != "NONE" or row.get("required_torque_enable_request") != "FALSE" or row.get("required_stale_replay_result") != "REJECTED":
            errors.append(f"{case_id} permits software motion authority")
        if row.get("execution_state") != "NOT EXECUTED" or row.get("disposition") != "OPEN" or row.get("warning") != WARNING:
            errors.append(f"{case_id} no longer fails closed")
    for case_id in ("E2-SL-005", "E2-SL-019"):
        row = next((item for item in pairs if item.get("case_id") == case_id), {})
        if row.get("hardware_power_path_expected") != "ON" or "actuator source is physically absent" not in row.get("combined_evidence_required", ""):
            errors.append(f"{case_id} lost its disconnected-load ON-path caveat")

    forms = read_csv(PKG / "form-sha256-register.csv")
    if len(forms) != 7:
        errors.append("form register must contain seven controlled inputs")
    for row in forms:
        path = ROOT / row.get("controlled_path", "")
        if not path.is_file():
            errors.append(f"form register path missing: {row.get('controlled_path')}")
        elif sha256(path) != row.get("sha256"):
            errors.append(f"form hash mismatch: {row.get('controlled_path')}")
        if row.get("warning") != WARNING:
            errors.append(f"form warning changed: {row.get('form_id')}")

    holds = read_csv(PKG / "open-holds.csv")
    if len(holds) != 7 or any(row.get("status") != "OPEN" or row.get("authority") != "FALSE" for row in holds):
        errors.append("seven E2 evidence holds must remain OPEN with authority FALSE")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-E2-EVIDENCE-P0.2" or status.get("round") != "R216":
        errors.append("package identity changed")
    for flag in ("all_cases_executed", "all_gates_closed", "run_authorized", "energization_authorized", "motion_authorized", "fabrication_authorized"):
        if status.get(flag) is not False:
            errors.append(f"package status {flag} must remain false")
    if status.get("warning") != WARNING:
        errors.append("package warning changed")

    gates = {row["gate_id"]: row for row in read_csv(GATES)}
    for gate_id in ("EG-018", "EG-019", "EG-020", "EG-021", "EG-022"):
        row = gates.get(gate_id, {})
        if row.get("status") != "partial" or "HR-V0-E2-EVIDENCE-P0.2" not in row.get("evidence_location", ""):
            errors.append(f"{gate_id} is not bound to the P0.2 contract while remaining partial")
    if "tests/forms/hr-v0-e2-software-authority-template-p0.1.csv" not in gates.get("EG-021", {}).get("evidence_location", ""):
        errors.append("EG-021 omits the mandatory software-authority evidence")
    if "tests/forms/hr-v0-e2-authorization-template-p0.2.csv" not in gates.get("EG-022", {}).get("evidence_location", ""):
        errors.append("EG-022 omits the superseding P0.2 authorization form")

    doc = DOC.read_text(encoding="utf-8")
    for token in ("obsolete Electrical V3-P1.8", "one-to-one evidence pair", "active trajectory `NONE`", "torque-enable request `FALSE`", "stale replay `REJECTED`", "EG-018 through EG-022 remain `partial`"):
        if token not in doc:
            errors.append(f"evidence-parity document omits: {token}")

    guide = GUIDE.read_text(encoding="utf-8")
    for token in ("HR-V0-E2-EVIDENCE-P0.2", "All 20 cases", "Coil path ON", "trajectory NONE", "NOT AUTHORIZED", "font:clamp(17px", "font-size:14px", "font-size:16px"):
        if token not in guide:
            errors.append(f"interactive guide omits: {token}")

    if errors:
        return fail(errors)
    print("HR-V0 E2 evidence-parity P0.2 check passed")
    print("8 configuration identities; 7 hash-bound forms; 20 hardware/software pairs; 7 open holds")
    print("EG-018 through EG-022 remain PARTIAL; NOT EXECUTED; NOT AUTHORIZED FOR ENERGIZATION")
    return 0


def fail(errors: list[str]) -> int:
    print("HR-V0 E2 evidence-parity P0.2 check failed", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
