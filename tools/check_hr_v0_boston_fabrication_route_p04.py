#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-BOSTON-FAB-ROUTE-P0.4 / R217."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/boston-fabrication-route-p0.4"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    need = lambda condition, message: failures.append(message) if not condition else None
    expected = {
        "authority-boundary.csv", "capability-inquiry-authorization-template.csv",
        "capability-inquiry-register.csv", "configuration-binding.csv", "index.html",
        "input-reconciliation.csv", "package-status.json", "route-comparison.csv",
        "source-register.csv",
    }
    need(OUT.is_dir() and {path.name for path in OUT.iterdir() if path.is_file()} == expected, "package membership changed")
    if not OUT.is_dir():
        return 1

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-BOSTON-FAB-ROUTE-P0.4" and status.get("round") == "R217", "identity changed")
    for key, value in {"part_count": 5, "configuration_bindings": 5, "route_records": 6, "source_records": 10, "input_records": 10, "inquiry_questions": 9}.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in (
        "qualified_provider_selected", "supplier_contacted", "files_uploaded", "quote_requested",
        "procurement_authorized", "fabrication_authorized", "assembly_authorized",
        "connection_authorized", "powered_test_authorized", "motion_authorized", "energization_authorized",
    ):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")

    routes = rows("route-comparison.csv")
    need({row["route_id"] for row in routes} == {"BOS-K4D", "ONLINE-PROTOLABS", "ONLINE-XOMETRY", "BOS-ARTISANS", "BOS-DIGITALFAB", "BOS-BPL-EXCLUDED"}, "route set changed")
    need(all(row["selected"] == row["contacted"] == row["files_uploaded"] == row["quote_requested"] == row["fabrication_authorized"] == "FALSE" for row in routes), "route implies external action")
    need("6061-T651" in next(row for row in routes if row["route_id"] == "ONLINE-PROTOLABS")["published_capability"], "Protolabs exact-material evidence missing")
    need("NOT A QUALIFIED FIRST-ARTICLE PROVIDER" in next(row for row in routes if row["route_id"] == "BOS-ARTISANS")["disposition"], "makerspace boundary weakened")
    need("EXCLUDED" in next(row for row in routes if row["route_id"] == "BOS-BPL-EXCLUDED")["disposition"], "BPL exclusion missing")

    sources = rows("source-register.csv")
    need(len(sources) == 10 and all(row["access_date"] == "2026-08-11" for row in sources), "source provenance changed")
    need(all(row["project_acceptance_effect"] == "CAPABILITY SCREEN ONLY - NO PROVIDER OR APPLICATION ACCEPTANCE" for row in sources), "source claim boundary weakened")
    need({row["provider"] for row in sources} >= {"Kontrast4D", "Protolabs", "Xometry", "Artisans Asylum", "Boston Digital Fabrication", "Boston Public Library"}, "provider source coverage changed")

    bindings = rows("configuration-binding.csv")
    need(len(bindings) == 5, "configuration binding count changed")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and digest(path) == row["sha256"], f"configuration source changed: {row['record_id']}")
    need({row["identifier"] for row in bindings} >= {"HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "HR-V0-MECH-BOM-BIND-P0.2", "HR-V0-MECH-MFG-REVIEW-P0.1", "HR-V0-FAB-INPUT-P0.1"}, "current identity binding incomplete")

    inputs = rows("input-reconciliation.csv")
    need(len(inputs) == 10 and {row["input_id"] for row in inputs} == {f"FAB-IN-{index:03d}" for index in range(1, 11)}, "input coverage changed")
    need(inputs[0]["state"] == "CONTROLLED DRAFT - INDEPENDENT ACCEPTANCE REQUIRED" and "<=100 g" in inputs[0]["current_controlled_statement"], "payload correction regressed")
    need(inputs[1]["state"] == inputs[2]["state"] == "PARTIAL", "duty/motion state changed")
    need(inputs[-1]["state"] == "NOT AUTHORIZED", "work authority changed")
    need(all(row["state"] != "CLOSED" for row in inputs), "input falsely closed")

    inquiries = rows("capability-inquiry-register.csv")
    need(len(inquiries) == 9 and all(row["response"] == "NOT SENT / NO RESPONSE" and row["external_action_authorized"] == "FALSE" for row in inquiries), "inquiry register claims external action")
    authorization = rows("capability-inquiry-authorization-template.csv")
    need(len(authorization) == 1 and authorization[0]["state"] == "NOT AUTHORIZED" and authorization[0]["permitted_files"] == "NONE", "capability authorization became active")
    authority = rows("authority-boundary.csv")
    need(all(row["permitted_by_this_package"] == ("TRUE" if row["activity"] == "internal route research and qualified review" else "FALSE") for row in authority), "authority boundary changed")
    for register in (routes, sources, bindings, inputs, inquiries, authorization, authority):
        need(all(row["warning"] == WARNING for row in register), "warning missing")

    with (ROOT / "requirements/hr-v0-energization-gates.csv").open(newline="", encoding="utf-8") as handle:
        gates = {row["gate_id"]: row for row in csv.DictReader(handle)}
    for gate_id in ("EG-003", "EG-006", "EG-007"):
        need(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} status changed")
        need("requirements/hr-v0-gate-evidence-supplement-r217.csv" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} lacks R217 evidence")
    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    mechanical = next((item for item in candidate.get("current_products", []) if item.get("domain") == "mechanical"), {})
    need("HR-V0-BOSTON-FAB-ROUTE-P0.4" in mechanical.get("supporting_identifiers", []), "release candidate lacks P0.4 route")
    need(mechanical.get("current_arm_architecture") == "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "release mechanical identity changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-BOSTON-FAB-ROUTE-P0.4", "font:clamp(16px", "font-size:14px", "data-filter=\"local\"", "data-filter=\"online\"", "data-filter=\"excluded\"", "P0.8/R215"):
        need(token in page, f"interactive guide missing {token}")
    if failures:
        print("HR-V0 Boston fabrication route P0.4: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 Boston fabrication route P0.4: PASS")
    print("5 bound current inputs; 6 routes; 10 official sources; 10 unresolved inputs; 9 unsent inquiry questions")
    print("No provider selected/contacted; no upload, quote, fabrication, assembly, motion, or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
