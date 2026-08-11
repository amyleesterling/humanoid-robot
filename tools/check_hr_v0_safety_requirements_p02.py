#!/usr/bin/env python3
"""Validate the fail-closed HR-V0 safety-requirements P0.2 package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/safety-requirements-p0.2"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {
        "configuration-binding.csv",
        "safety-function-requirements.csv",
        "timing-budget.csv",
        "validation-matrix.csv",
        "common-cause-review-register.csv",
        "qualified-allocation-inputs.csv",
        "source-register.csv",
        "authority-boundary.csv",
        "package-status.json",
        "index.html",
    }
    need(OUT.is_dir(), "package directory missing")
    if OUT.is_dir():
        need({path.name for path in OUT.iterdir() if path.is_file()} == expected, "package file set changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-SRS-P0.2" and status.get("round") == "R218", "package identity changed")
    for key, expected_value in {
        "requirement_records": 15,
        "timing_records": 7,
        "validation_scenarios": 16,
        "common_cause_records": 12,
        "qualified_allocation_records": 2,
        "source_records": 6,
        "configuration_bindings": 7,
        "setup_candidate_speed_deg_s": 10.0,
        "setup_candidate_residual_travel_deg": 2.0,
        "setup_candidate_total_response_ms": 200.0,
        "automatic_candidate_total_response_ms": 66.667,
        "component_maximum_arithmetic_screen_ms": 44.0,
    }.items():
        need(status.get(key) == expected_value, f"status {key} changed")
    for key in (
        "plr_or_sil_assigned", "architecture_or_category_approved", "physical_validation_executed",
        "functional_safety_approved", "procurement_authorized", "fabrication_authorized",
        "assembly_authorized", "connection_authorized", "powered_test_authorized",
        "motion_authorized", "energization_authorized",
    ):
        need(status.get(key) is False, f"status falsely authorizes {key}")
    need(status.get("warning") == WARNING, "status warning changed")

    bindings = rows("configuration-binding.csv")
    need(len(bindings) == 7, "configuration binding count changed")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and digest(path) == row["sha256"], f"configuration source changed: {row['record_id']}")
        need(row["warning"] == WARNING, f"binding warning missing: {row['record_id']}")
    need({row["identifier"] for row in bindings} >= {
        "HR-V0-FSA-P0.1", "HR-V0-STOP-BUDGET-P0.1", "HR-V0-PNOZ-CONF-P0.1",
        "PNOZ-S4-750104-21396-EN-23", "HR-V0-K1K2-APP-P0.2",
    }, "controlled configuration set incomplete")

    requirements = rows("safety-function-requirements.csv")
    need(len(requirements) == 15, "requirement count changed")
    need({row["requirement_id"] for row in requirements} == {f"SRS-{index:03d}" for index in range(1, 16)}, "requirement ID set changed")
    need(all(row["approval_state"] == "NOT APPROVED" and row["warning"] == WARNING for row in requirements), "requirement approval/warning weakened")
    setup = next((row for row in requirements if row["requirement_id"] == "SRS-003"), {})
    need("200 ms" in setup.get("requirement", "") and "2.000 degrees" in setup.get("requirement", "") and "10.000 degrees per second" in setup.get("requirement", ""), "setup candidate limit changed")
    automatic = next((row for row in requirements if row["requirement_id"] == "SRS-005"), {})
    need(automatic.get("current_state") == "PROHIBITED" and "66.667 ms" in automatic.get("requirement", ""), "automatic motion boundary changed")
    need(any(row["function_id"] == "DF-01" and "zero safety credit" in row["requirement"].lower() for row in requirements), "DF-01 zero-credit boundary missing")
    need(any(row["function_id"] == "SF-01/SF-03" and row["current_state"] == "SELECTION REQUIRED" for row in requirements), "qualified allocation requirement missing")

    timing = rows("timing-budget.csv")
    need(len(timing) == 7, "timing row count changed")
    by_id = {row["record_id"]: row for row in timing}
    setup_ms = Decimal(by_id["SRS-TIM-001"]["travel_deg"]) / Decimal(by_id["SRS-TIM-001"]["speed_deg_s"]) * Decimal(1000)
    auto_ms = Decimal(by_id["SRS-TIM-002"]["travel_deg"]) / Decimal(by_id["SRS-TIM-002"]["speed_deg_s"]) * Decimal(1000)
    component_ms = Decimal(by_id["SRS-TIM-003"]["time_ms"]) + Decimal(by_id["SRS-TIM-004"]["time_ms"])
    need(setup_ms == Decimal("200.0") and Decimal(by_id["SRS-TIM-001"]["time_ms"]) == Decimal("200.000"), "setup timing arithmetic changed")
    need(abs(auto_ms - Decimal(by_id["SRS-TIM-002"]["time_ms"])) < Decimal("0.001"), "automatic timing arithmetic changed")
    need(component_ms == Decimal("44.000") == Decimal(by_id["SRS-TIM-005"]["time_ms"]), "component arithmetic screen changed")
    need(all(row["safety_credit"] == "NONE UNTIL QUALIFIED VALIDATION" and row["warning"] == WARNING for row in timing), "timing row implies safety credit")
    need(by_id["SRS-TIM-007"]["evidence_class"] == "NOT RELEASED", "automatic residual allocation released")

    validation = rows("validation-matrix.csv")
    need(len(validation) == 16 and {row["test_id"] for row in validation} == {f"SRS-VAL-{index:03d}" for index in range(1, 17)}, "validation matrix coverage changed")
    need(all(row["execution_state"] == "NOT EXECUTED" and row["approval_state"] == "NOT APPROVED" and row["warning"] == WARNING for row in validation), "validation matrix claims execution or approval")
    required_scenarios = ("prevented from opening", "RESET held", "Heartbeat restoration", "brownout", "stuck valid")
    combined = "\n".join(row["scenario"] for row in validation)
    need(all(token in combined for token in required_scenarios), "validation fault coverage incomplete")

    ccf = rows("common-cause-review-register.csv")
    need(len(ccf) == 12, "common-cause row count changed")
    need(all(row["current_disposition"] == "OPEN - NO EXCLUSION OR SAFETY CREDIT" and row["qualified_review_state"] == "NOT EXECUTED" and row["warning"] == WARNING for row in ccf), "common-cause boundary weakened")

    allocation = rows("qualified-allocation-inputs.csv")
    need({row["function_id"] for row in allocation} == {"SF-01", "SF-03"}, "allocation function set changed")
    for row in allocation:
        for field in ("severity_input", "frequency_exposure_input", "avoidance_input", "required_plr_or_sil", "architecture_or_category", "mttfd_or_b10d", "diagnostic_coverage", "ccf_score_and_measures", "reviewer", "qualification_basis", "independence_disposition"):
            need(row[field] == "SELECTION REQUIRED", f"allocation field falsely selected: {row['function_id']} {field}")
        need(row["fault_exclusions"] == "NONE ACCEPTED" and row["signature"] == "NOT EXECUTED" and row["approval_status"] == "NOT APPROVED" and row["warning"] == WARNING, f"allocation approval boundary weakened: {row['function_id']}")

    sources = rows("source-register.csv")
    need(len(sources) == 6 and all(row["access_date"] == "2026-08-11" for row in sources), "source provenance changed")
    need(all(row["project_acceptance_effect"] == "REFERENCE INPUT ONLY - NO PLR, APPLICATION OR SAFETY APPROVAL" and row["warning"] == WARNING for row in sources), "source claim boundary weakened")
    need({row["title"] for row in sources} >= {"ISO 13849-1:2023", "ISO 13849-2:2012", "ISO 13850:2015", "PNOZ s4 operating manual", "LC1D25BD product data sheet"}, "source set incomplete")

    authority = rows("authority-boundary.csv")
    need(len(authority) == 5, "authority row count changed")
    need(all(row["permitted_by_this_package"] == ("TRUE" if row["activity"] == "internal SRS review and redline" else "FALSE") and row["warning"] == WARNING for row in authority), "authority boundary changed")

    with (ROOT / "requirements/hr-v0-energization-gates.csv").open(newline="", encoding="utf-8") as handle:
        gates = {row["gate_id"]: row for row in csv.DictReader(handle)}
    for gate_id in ("EG-012", "EG-021", "EG-022", "EG-026"):
        need(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} status changed")
        need("requirements/hr-v0-gate-evidence-supplement-r218.csv" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} lacks R218 evidence")

    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    safety = next((item for item in candidate.get("current_products", []) if item.get("domain") == "functional_safety"), {})
    need(safety.get("identifier") == "HR-V0-FSA-P0.1", "functional-safety parent identity changed")
    need("HR-V0-SRS-P0.2" in safety.get("supporting_identifiers", []), "release candidate lacks SRS P0.2")
    need("HR-V0-FS-REVIEW-ROUTE-P0.1" in safety.get("supporting_identifiers", []), "release candidate lacks R219 reviewer route")
    need(safety.get("release_state") == "r235_p121_application_evidence_route_zero_safety_credit_questions_unsent_tests_unexecuted_plr_sil_and_qualified_review_open", "release safety state changed")
    need(safety.get("watchdog_permit_topology_proof") == "HR-V0-WD-PERMIT-TOPOLOGY-P0.1", "R225 watchdog topology proof missing")
    need(safety.get("watchdog_interlock_candidate") == "HR-V0-P120-WD-INTERLOCK-P0.1", "R232 watchdog interlock candidate missing")
    need(safety.get("p120_pnoz_kwd_application_dossier") == "HR-V0-PNOZ-KWD-APP-P0.2", "R233 PNOZ/KWD dossier missing")
    need(safety.get("p121_sra1_supply_watchdog_dossier") == "HR-V0-P121-SRA1-SUPPLY-WD-P0.1", "R234 P1.21 dossier missing")
    need(safety.get("p121_application_evidence_dossier") == "HR-V0-P121-APP-EVID-P0.1", "R235 P1.21 application evidence missing")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-SRS-P0.2", "font:clamp(16px", "font-size:14px", "data-filter=\"SF-01\"", "data-filter=\"SF-03\"", "data-filter=\"open\"", "200 ms", "2.000 deg", "0</strong>PLr/SIL"):
        need(token in page, f"interactive guide missing {token}")
    need("PLr d" not in page and "PLr e" not in page and "SIL 2" not in page and "SIL 3" not in page, "interactive guide invents integrity target")

    if failures:
        print("HR-V0 safety requirements P0.2: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 safety requirements P0.2: PASS")
    print("15 candidate requirements; 7 timing records; 16 unexecuted scenarios; 12 open common-cause records")
    print("No PLr/SIL assigned; no physical validation, safety approval, motion, or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
