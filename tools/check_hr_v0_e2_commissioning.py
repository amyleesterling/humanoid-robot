"""Fail-closed validation of the HR-V0 E2 control-only commissioning inputs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE = ROOT / "tests" / "e2" / "hr-v0-e2-control-only-sequence.csv"
FORMS = {
    "unpowered": ROOT / "tests" / "forms" / "hr-v0-e2-unpowered-configuration-template.csv",
    "mains_pe": ROOT / "tests" / "forms" / "hr-v0-e2-mains-pe-insulation-template.csv",
    "elv": ROOT / "tests" / "forms" / "hr-v0-e2-elv-point-to-point-template.csv",
    "logic": ROOT / "tests" / "forms" / "hr-v0-e2-safety-logic-template.csv",
    "authorization": ROOT / "tests" / "forms" / "hr-v0-e2-authorization-template.csv",
}
REQUIREMENTS = ROOT / "requirements" / "requirements.csv"
PROCEDURES = ROOT / "tests" / "procedures" / "procedure-registry.csv"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
DOC = ROOT / "docs" / "hr-v0-e2-control-only-energization-p0.1.md"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    paths = [SEQUENCE, REQUIREMENTS, PROCEDURES, GATES, DOC, *FORMS.values()]
    for path in paths:
        if not path.is_file():
            errors.append(f"missing controlled E2 artifact: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    sequence = rows(SEQUENCE)
    expected_steps = [f"E2-{value:03d}" for value in range(0, 141, 10)]
    if [row.get("step_id") for row in sequence] != expected_steps:
        errors.append("E2 step set/order changed")
    if any(row.get("status") != "NOT_EXECUTED" for row in sequence):
        errors.append("an E2 sequence step falsely claims execution")
    if any("NOT APPROVED FOR ENERGIZATION" not in row.get("warning", "") for row in sequence):
        errors.append("an E2 sequence row lost its preliminary warning")
    for row in sequence:
        if not row.get("required_actuator_source_state", "").startswith("PHYSICALLY ABSENT"):
            errors.append(f"{row.get('step_id')} does not require the actuator source physically absent")
        if "DISCONNECTED" not in row.get("required_actuator_branch_state", "").upper():
            errors.append(f"{row.get('step_id')} permits an actuator branch connection")
    energized = [row for row in sequence if row.get("required_24v_state") == "ON" or row.get("required_compute_state") == "ON"]
    if not energized or any(row.get("required_actuator_source_state", "").startswith("PHYSICALLY ABSENT") is False for row in energized):
        errors.append("energized E2 steps do not preserve the no-actuator-source boundary")
    if sequence[-1].get("phase") != "controlled_shutdown" or sequence[-1].get("required_24v_state") != "OFF" or sequence[-1].get("required_compute_state") != "OFF":
        errors.append("E2 sequence lacks a fail-closed final shutdown")

    requirements = {row["id"]: row for row in rows(REQUIREMENTS)}
    expected_requirements = {
        "COMM-001": "INSPECT-E2-001",
        "COMM-002": "INSPECT-E2-002",
        "COMM-003": "TEST-E2-001",
        "COMM-004": "TEST-E2-002",
        "COMM-005": "AUDIT-E2-001",
    }
    for requirement_id, verification_id in expected_requirements.items():
        row = requirements.get(requirement_id, {})
        if row.get("verification_id") != verification_id or row.get("status") != "draft":
            errors.append(f"{requirement_id} traceability/status changed")

    procedures = {row["verification_id"]: row for row in rows(PROCEDURES)}
    for verification_id, requirement_id in {value: key for key, value in expected_requirements.items()}.items():
        row = procedures.get(verification_id, {})
        if requirement_id not in row.get("linked_requirement_ids", "").split(";"):
            errors.append(f"{verification_id} lost {requirement_id} traceability")
        if row.get("status") != "selection_required" or row.get("selection_required") != "yes":
            errors.append(f"{verification_id} no longer fails closed")
    e2_test = procedures.get("TEST-E2-002", {})
    for requirement_id in ("SAFE-001", "SAFE-002", "SAFE-008", "CTRL-007"):
        if requirement_id not in e2_test.get("linked_requirement_ids", "").split(";"):
            errors.append(f"TEST-E2-002 lost {requirement_id} scope")
    if "disconnected-load subset" not in e2_test.get("notes", "") or "stopping" not in e2_test.get("notes", ""):
        errors.append("TEST-E2-002 lost its no-motion evidence boundary")

    unpowered = rows(FORMS["unpowered"])
    mains_pe = rows(FORMS["mains_pe"])
    elv = rows(FORMS["elv"])
    logic = rows(FORMS["logic"])
    authorization = rows(FORMS["authorization"])
    for name, form_rows in (("unpowered", unpowered), ("mains_pe", mains_pe), ("elv", elv), ("logic", logic), ("authorization", authorization)):
        if any(None in row for row in form_rows):
            errors.append(f"{name} form has more values than controlled columns")
        if any("NOT APPROVED FOR ENERGIZATION" not in row.get("warning", "") for row in form_rows):
            errors.append(f"{name} form lost its preliminary warning")
    if len(unpowered) != 1 or unpowered[0].get("status") != "NOT EXECUTED" or unpowered[0].get("actuator_source_physically_absent") != "NOT EXECUTED":
        errors.append("unpowered-configuration template execution boundary changed")
    if len(mains_pe) != 1 or mains_pe[0].get("status") != "NOT EXECUTED" or mains_pe[0].get("frame_pe_policy") != "SELECTION REQUIRED":
        errors.append("mains/PE template execution/selection boundary changed")
    if len(elv) != 1 or elv[0].get("status") != "NOT EXECUTED" or elv[0].get("expected_state") != "SELECTION REQUIRED":
        errors.append("ELV template execution/selection boundary changed")
    expected_cases = [f"E2-SL-{index:03d}" for index in range(1, 21)]
    if [row.get("case_id") for row in logic] != expected_cases or any(row.get("status") != "NOT EXECUTED" for row in logic):
        errors.append("E2 safety-logic case set or execution boundary changed")
    if any(row.get("actuator_source_absent") != "NOT EXECUTED" or row.get("actuator_branches_disconnected_covered") != "NOT EXECUTED" for row in logic):
        errors.append("E2 logic form no longer records both actuator isolation proofs")
    restoration = next((row for row in logic if row.get("case_id") == "E2-SL-011"), {})
    reset_only = next((row for row in logic if row.get("case_id") == "E2-SL-012"), {})
    if restoration.get("expected_k1_a1") != "OFF" or restoration.get("expected_k2_a1") != "OFF" or reset_only.get("expected_k1_a1") != "OFF" or reset_only.get("expected_k2_a1") != "OFF":
        errors.append("heartbeat restoration or RESET-only could permit coils")
    if len(authorization) != 1 or authorization[0].get("authorization_state") != "NOT AUTHORIZED" or authorization[0].get("status") != "NOT EXECUTED":
        errors.append("E2 authorization template does not fail closed")
    for field in (
        "test_director_signature",
        "qualified_electrical_reviewer_signature",
        "functional_safety_reviewer_signature",
        "independent_witness_signature",
    ):
        if field not in authorization[0]:
            errors.append(f"authorization form omits {field}")

    gates = {row["gate_id"]: row for row in rows(GATES)}
    expected_gate_paths = {
        "EG-018": "tests/forms/hr-v0-e2-unpowered-configuration-template.csv",
        "EG-019": "tests/forms/hr-v0-e2-mains-pe-insulation-template.csv",
        "EG-020": "tests/forms/hr-v0-e2-elv-point-to-point-template.csv",
        "EG-021": "tests/forms/hr-v0-e2-safety-logic-template.csv",
        "EG-022": "tests/forms/hr-v0-e2-authorization-template.csv",
    }
    for gate_id, evidence_path in expected_gate_paths.items():
        row = gates.get(gate_id, {})
        if row.get("status") != "partial" or evidence_path not in row.get("evidence_location", "") or str(SEQUENCE.relative_to(ROOT)).replace("\\", "/") not in row.get("evidence_location", ""):
            errors.append(f"{gate_id} E2 evidence/status boundary changed")

    doc = DOC.read_text(encoding="utf-8")
    for token in (
        "NOT AN AUTHORIZATION",
        "12 V actuator source must be physically absent",
        "cannot prove stopping distance",
        "NOT AUTHORIZED",
        "S1` RESET and `S2` ARM terminals remain `TBD-*`",
    ):
        if token not in doc:
            errors.append(f"E2 control document omits: {token}")

    if errors:
        return fail(errors)
    print("HR-V0 E2 commissioning-input validation: PASS")
    print("15 fail-closed sequence steps; 20 disconnected-load logic cases; five unexecuted evidence forms")
    print("EG-018 through EG-022: PARTIAL - templates only; NOT AUTHORIZED FOR ENERGIZATION")
    return 0


def fail(errors: list[str]) -> int:
    print("HR-V0 E2 commissioning-input validation: FAIL", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
