#!/usr/bin/env python3
"""Check the fail-closed HR-V0 functional-safety reviewer route."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/functional-safety-review-route-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    expected = {
        "configuration-binding.csv", "provider-route-comparison.csv", "source-register.csv",
        "competence-independence-criteria.csv", "scope-of-work.csv", "capability-inquiry-register.csv",
        "capability-inquiry-authorization-template.csv", "reviewer-declaration-template.csv",
        "deliverable-acceptance-matrix.csv", "authority-boundary.csv", "package-status.json", "index.html",
    }
    need(OUT.is_dir(), "package missing")
    if OUT.is_dir():
        need({p.name for p in OUT.iterdir() if p.is_file()} == expected, "package file set changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-FS-REVIEW-ROUTE-P0.1" and status.get("round") == "R219", "identity changed")
    for key, value in {
        "configuration_bindings": 8, "provider_routes": 4, "source_records": 9,
        "competence_criteria": 12, "scope_records": 10, "capability_questions": 10,
        "deliverable_records": 16,
    }.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in (
        "provider_selected", "provider_contacted", "files_uploaded", "quote_requested",
        "contract_authorized", "named_reviewer_accepted", "plr_or_sil_assigned",
        "physical_validation_executed", "functional_safety_approved", "energization_authorized",
    ):
        need(status.get(key) is False, f"status falsely closes {key}")
    need(status.get("warning") == WARNING, "status warning changed")

    bindings = rows("configuration-binding.csv")
    need(len(bindings) == 8, "binding count changed")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and digest(path) == row["sha256"], f"bound source changed: {row['record_id']}")
        need(row["warning"] == WARNING, f"binding warning missing: {row['record_id']}")

    providers = rows("provider-route-comparison.csv")
    need({r["route_id"] for r in providers} == {"FSR-TUVSUD", "FSR-TUVR", "FSR-PILZ", "FSR-TECNICUM"}, "provider set changed")
    for row in providers:
        for field in ("selected", "contacted", "files_uploaded", "quote_requested", "contract_authorized"):
            need(row[field] == "FALSE", f"provider activity falsely claimed: {row['route_id']} {field}")
        need(row["warning"] == WARNING, f"provider warning missing: {row['route_id']}")
    pilz = next(r for r in providers if r["route_id"] == "FSR-PILZ")
    need("component-supplier" in pilz["independence_issue"], "Pilz component conflict missing")
    tec = next(r for r in providers if r["route_id"] == "FSR-TECNICUM")
    need("does not by itself prove" in tec["independence_issue"], "tec.nicum scope boundary missing")

    sources = rows("source-register.csv")
    need(len(sources) == 9 and all(r["access_date"] == "2026-08-11" for r in sources), "source provenance changed")
    need(all("UNVERIFIED" in r["project_acceptance_effect"] and r["warning"] == WARNING for r in sources), "source boundary weakened")

    competence = rows("competence-independence-criteria.csv")
    need(len(competence) == 12, "competence criteria count changed")
    need(all(r["evidence_received"] == "FALSE" and r["accepted"] == "FALSE" and r["warning"] == WARNING for r in competence), "competence falsely accepted")
    joined = "\n".join(r["requirement"] for r in competence)
    for token in ("ISO 13849-1:2023", "ISO 13849-2:2012", "no person approves their own work", "Boston"):
        need(token.lower() in joined.lower(), f"competence coverage missing: {token}")

    scope = rows("scope-of-work.csv")
    need({r["phase"] for r in scope} == {"A pre-design", "B before E2", "C before E4"}, "scope phases changed")
    need(all(r["provider_accepted"] == r["executed"] == r["accepted_by_project"] == "FALSE" for r in scope), "scope falsely accepted or executed")
    need(any("P1.15" in r["task"] and "P1.17" in r["task"] for r in scope), "ECAD authority boundary missing")

    inquiries = rows("capability-inquiry-register.csv")
    need(len(inquiries) == 10 and all(r["response"] == "NOT SENT" and r["accepted"] == "FALSE" for r in inquiries), "inquiry activity falsely claimed")
    authorization = rows("capability-inquiry-authorization-template.csv")
    values = {r["field"]: r["value"] for r in authorization}
    need(values.get("files approved for transmission") == "NONE" and values.get("send state") == "NOT SENT" and values.get("quote request") == "NOT AUTHORIZED", "inquiry authorization weakened")

    declarations = rows("reviewer-declaration-template.csv")
    need(len(declarations) == 13 and all(r["review_state"] == "NOT EXECUTED" and r["project_acceptance"] == "NOT ACCEPTED" for r in declarations), "reviewer declaration falsely executed")
    deliverables = rows("deliverable-acceptance-matrix.csv")
    need(len(deliverables) == 16 and all(r["received"] == r["configuration_bound"] == r["technically_accepted"] == r["signed"] == "FALSE" for r in deliverables), "deliverable falsely received or accepted")

    authority = rows("authority-boundary.csv")
    need(len(authority) == 7, "authority row count changed")
    need(sum(r["permitted_by_this_package"] == "TRUE" for r in authority) == 1, "authority scope widened")
    need(all(r["permitted_by_this_package"] == "FALSE" for r in authority if "energize" in r["activity"] or "powered" in r["activity"]), "powered authority granted")

    with (ROOT / "requirements/hr-v0-energization-gates.csv").open(newline="", encoding="utf-8") as handle:
        gates = {r["gate_id"]: r for r in csv.DictReader(handle)}
    for gate in ("EG-012", "EG-021", "EG-022", "EG-026"):
        need(gates.get(gate, {}).get("status") == "partial", f"{gate} promoted")
        need("requirements/hr-v0-gate-evidence-supplement-r219.csv" in gates.get(gate, {}).get("evidence_location", ""), f"{gate} missing R219")

    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    safety = next((item for item in candidate.get("current_products", []) if item.get("domain") == "functional_safety"), {})
    need("HR-V0-FS-REVIEW-ROUTE-P0.1" in safety.get("supporting_identifiers", []), "release candidate lacks reviewer route")
    need(safety.get("release_state") == "measurable_srs_candidate_reviewer_route_open_no_provider_selected_no_plr_or_sil_no_physical_validation", "functional-safety state changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-FS-REVIEW-ROUTE-P0.1", "font:clamp(16px", "font-size:14px", 'data-filter="local"', 'data-filter="full"', 'data-filter="consulting"'):
        need(token in page, f"interactive guide missing {token}")

    if failures:
        print("HR-V0 functional-safety review route P0.1: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 functional-safety review route P0.1: PASS")
    print("4 capability leads; 12 competence criteria; 10 scope records; 16 unreceived deliverables")
    print("No provider selected/contacted; no PLr/SIL, validation, safety approval or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
