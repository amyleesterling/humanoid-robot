"""Validate the HR-V0 safety-credit boundary and unexecuted allocation package."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOCATION = ROOT / "safety" / "hr-v0-safety-function-allocation.csv"
FMEA = ROOT / "safety" / "hr-v0-watchdog-boundary-fmea.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-functional-safety-allocation-template.csv"
REQUIREMENTS = ROOT / "requirements" / "requirements.csv"
PROCEDURES = ROOT / "tests" / "procedures" / "procedure-registry.csv"
DOC = ROOT / "docs" / "hr-v0-functional-safety-allocation-p0.1.md"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    allocations = rows(ALLOCATION)
    expected = {
        "SF-01": "credited_candidate",
        "SF-03": "credited_candidate",
        "PG-01": "physical_protective_measure",
        "DF-01": "uncredited_diagnostic",
        "SF-02": "future_safety_function",
        "SF-04": "future_safety_function",
        "SF-05": "future_safety_function",
        "SF-06": "future_safety_function",
    }
    by_id = {row.get("function_id"): row for row in allocations}
    if len(allocations) != len(expected) or set(by_id) != set(expected):
        errors.append(f"allocation must contain exactly {sorted(expected)}")
    for function_id, classification in expected.items():
        row = by_id.get(function_id, {})
        if row.get("classification") != classification:
            errors.append(f"{function_id} classification expected {classification!r}")
        if row.get("status") in {"released", "approved", "passed"}:
            errors.append(f"{function_id} falsely appears released")
        if not row.get("required_closure_evidence"):
            errors.append(f"{function_id} lacks closure evidence")

    diagnostic = by_id.get("DF-01", {})
    if diagnostic.get("credited_risk_reduction") != "no":
        errors.append("DF-01 must receive zero credited risk reduction")
    if diagnostic.get("plr_or_sil") != "NO SAFETY CREDIT":
        errors.append("DF-01 must state NO SAFETY CREDIT")
    if diagnostic.get("architecture_claim") != "NONE—ORDINARY CONTROL":
        errors.append("DF-01 must not claim a safety architecture")
    for function_id in ("SF-01", "SF-03", "SF-02", "SF-04", "SF-05", "SF-06"):
        if by_id.get(function_id, {}).get("plr_or_sil") != "SELECTION REQUIRED":
            errors.append(f"{function_id} must retain unresolved PLr/SIL")
    if by_id.get("PG-01", {}).get("plr_or_sil") != "NOT AN SRP/CS":
        errors.append("PG-01 must not carry a PL label")

    fmea_rows = rows(FMEA)
    fmea_by_id = {row.get("fmea_id"): row for row in fmea_rows}
    expected_fmea = {f"WDF-{index:03d}" for index in range(1, 33)}
    if len(fmea_rows) != len(expected_fmea) or set(fmea_by_id) != expected_fmea:
        errors.append("watchdog FMEA must contain WDF-001 through WDF-032")
    for row in fmea_rows:
        if row.get("status") != "open" or not row.get("required_control") or not row.get("verification"):
            errors.append(f"{row.get('fmea_id')} lacks an open control/verification route")
    bypass = fmea_by_id.get("WDF-008", {})
    if bypass.get("safe_by_design") != "no" or "can be impaired" not in bypass.get("sf01_effect", ""):
        errors.append("WDF-008 must remain an explicit credited E-stop impairment case")
    injection = fmea_by_id.get("WDF-012", {})
    if (
        injection.get("safe_by_design") != "conditional"
        or "P1.13" not in injection.get("sf01_effect", "")
        or "physical separation" not in injection.get("sf01_effect", "").lower()
    ):
        errors.append("WDF-012 must preserve the conditional P1.13 disposition with physical proof open")

    form_rows = rows(FORM)
    if len(form_rows) != len(expected) or {row.get("function_id") for row in form_rows} != set(expected):
        errors.append("allocation template must contain one seed row per controlled function/measure")
    for row in form_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("approval_status") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking allocation template row: {row.get('function_id')}")

    requirements = {row["id"]: row for row in rows(REQUIREMENTS)}
    if "no safety credit" not in requirements.get("SAFE-003", {}).get("statement", ""):
        errors.append("SAFE-003 must deny safety credit to the ordinary watchdog")
    if requirements.get("CTRL-007", {}).get("verification_id") != "TEST-SAFE-002":
        errors.append("CTRL-007 must retain the controlled diagnostic test identifier")
    procedures = {row["verification_id"]: row for row in rows(PROCEDURES)}
    for procedure_id in ("ANALYSIS-SAFE-001", "ANALYSIS-SAFE-002", "TEST-SAFE-002"):
        if procedure_id not in procedures:
            errors.append(f"missing controlled procedure {procedure_id}")
    if procedures.get("TEST-SAFE-002", {}).get("linked_requirement_ids") != "CTRL-007":
        errors.append("TEST-SAFE-002 must be linked only to the uncredited diagnostic requirement")

    doc = DOC.read_text(encoding="utf-8")
    for phrase in (
        "uncredited diagnostic control",
        "with DF-01 failure assumed",
        "PLr",
        "WDF-008",
        "does not close Sol `B-005` or `B-006`",
        "NOT APPROVED FOR ENERGIZATION",
    ):
        if phrase not in doc:
            errors.append(f"allocation document missing controlled phrase: {phrase}")

    if errors:
        print("HR-V0 safety allocation check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 safety allocation check passed: 8 controlled functions/measures; 32 open watchdog FMEA cases")
    print("DF-01 safety credit: ZERO; SF-01/SF-03 PLr and architecture: SELECTION REQUIRED")
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
