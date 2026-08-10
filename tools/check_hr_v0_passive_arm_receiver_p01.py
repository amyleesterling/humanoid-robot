"""Validate the R127 passive arm-receiver candidate and its fail-closed boundary."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-passive-arm-receiver-template-p0.1.csv"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-p0.1" / "index.html"
WARNING = "PRELIMINARY - DESIGN AND SIZING CANDIDATE ONLY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def close(actual: float, expected: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance)


def main() -> int:
    failures: list[str] = []
    required = {
        "absorber-application-screen.csv", "commanded-envelope-screen.csv",
        "HR-V0_passive-arm-receiver-candidate.step", "HR-V0_passive-arm-receiver-review.glb",
        "receiver-closure-holds.csv", "receiver-geometry.csv", "receiver-load-path-screen.csv",
        "receiver-poster.svg", "receiver-summary.json", "source-register.csv",
    }
    require({item.name for item in OUT.iterdir()} == required, "generated file set differs from the controlled ten artifacts", failures)
    summary = json.loads((OUT / "receiver-summary.json").read_text(encoding="utf-8"))
    require(summary.get("identifier") == "HR-V0-PASSIVE-ARM-RECEIVER-P0.1", "identifier mismatch", failures)
    require(summary.get("warning") == WARNING, "summary warning mismatch", failures)
    envelope = summary.get("commanded_envelope", {})
    require(envelope.get("sample_count") == 144761, "commanded grid count differs from 144,761", failures)
    require(close(float(envelope.get("sampled_min_z_mm", 0)), 384.14261888640146), "sampled lower Z changed", failures)
    require(close(float(envelope.get("continuous_cell_motion_bound_mm", 0)), 1.0361405142589042), "continuous cell bound changed", failures)
    require(close(float(envelope.get("continuous_min_z_bound_mm", 0)), 383.10647837214253), "continuous lower Z changed", failures)
    require(close(float(envelope.get("receiver_clearance_mm", 0)), 63.10647837214253), "receiver clearance changed", failures)
    require(envelope.get("controlling_component") == "H104_FRAME" and envelope.get("controlling_q1_deg") == -20.0 and envelope.get("controlling_q2_deg") == 15.0, "controlling pose changed", failures)
    require(summary.get("absorber_candidate", {}).get("type") == "ACE MA30M" and summary.get("absorber_candidate", {}).get("quantity") == 3, "absorber type/count changed", failures)
    require(close(float(summary.get("absorber_candidate", {}).get("catalog_total_energy_j", 0)), 10.507589, 1e-6), "catalog energy arithmetic changed", failures)
    require(close(float(summary.get("absorber_candidate", {}).get("catalog_to_gravity_ratio", 0)), 1.984215, 1e-6), "catalog/gravity ratio changed", failures)
    require(summary.get("absorber_candidate", {}).get("status") == "EVALUATION ONLY - APPLICATION APPROVAL REQUIRED", "absorber hold missing", failures)
    require(summary.get("structural_screen", {}).get("input_n") == 2000.0, "structural screen input changed", failures)
    require(summary.get("structural_screen", {}).get("status") == "NOMINAL SCREEN ONLY - NO ALLOWABLE OR JOINT PASS", "structural limitation missing", failures)
    require(summary.get("closure_holds") == 12 and summary.get("physical_records") == 28, "hold/evidence counts changed", failures)
    require(summary.get("gate_state") == "EG-008 AND EG-009 REMAIN PARTIAL", "gate hold changed", failures)

    require(len(rows("commanded-envelope-screen.csv")) == 6, "expected six envelope screens", failures)
    require(len(rows("receiver-geometry.csv")) == 6, "expected six geometry groups", failures)
    require(len(rows("absorber-application-screen.csv")) == 7, "expected seven absorber screens", failures)
    require(len(rows("receiver-load-path-screen.csv")) == 7, "expected seven load-path screens", failures)
    hold_rows = rows("receiver-closure-holds.csv")
    require(len(hold_rows) == 12 and all(item["status"] == "OPEN - BLOCKS FABRICATION MOTION AND ENERGIZATION" for item in hold_rows), "closure holds are not twelve fail-closed rows", failures)
    source_rows = rows("source-register.csv")
    require(len(source_rows) == 4, "source register count differs from four", failures)
    require(all(item["accessed"] in {"2026-08-07", "2026-08-09"} and item["document_revision_date"] for item in source_rows), "source revision/access evidence incomplete", failures)
    require(any(item["source_id"] == "REC-SRC-002" and "21_22_0019" in item["document_revision_date"] and "05.2022" in item["document_revision_date"] for item in source_rows), "ACE manual revision record missing", failures)

    with FORM.open(newline="", encoding="utf-8") as handle:
        evidence = list(csv.DictReader(handle))
    require(len(evidence) == 28, "expected 28 physical evidence rows", failures)
    require(all(item["result"] == "NOT EXECUTED" and item["authorization"] == "NOT AUTHORIZED" and item["warning"] == WARNING for item in evidence), "physical evidence form is not entirely fail closed", failures)

    require((OUT / "HR-V0_passive-arm-receiver-review.glb").stat().st_size > 1_000_000, "review GLB is implausibly small", failures)
    step = cq.importers.importStep(str(OUT / "HR-V0_passive-arm-receiver-candidate.step"))
    require(len(step.vals()) >= 1 and step.val().Volume() > 1_000_000, "receiver STEP does not parse as substantial solid geometry", failures)
    guide = GUIDE.read_text(encoding="utf-8")
    require(WARNING in guide and "63.106" in guide and "10.508 J" in guide, "interactive guide lacks controlled result/warning", failures)
    require("application rating" in guide and "NOT EXECUTED" in guide and "EG-008 and EG-009 remain partial" in guide, "interactive guide overstates evidence", failures)
    require("font:17px/1.55" in guide and "font-size:14px" in guide, "interactive guide legibility controls changed", failures)

    gates = list(csv.DictReader((ROOT / "requirements" / "hr-v0-energization-gates.csv").open(newline="", encoding="utf-8")))
    gate_by_id = {item["gate_id"]: item for item in gates}
    for gate_id in ("EG-008", "EG-009"):
        require(gate_by_id.get(gate_id, {}).get("status") == "partial", f"{gate_id} no longer remains partial", failures)
        require("HR-V0-PASSIVE-ARM-RECEIVER-P0.1" in gate_by_id.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} lacks R127 evidence reference", failures)

    if failures:
        print("HR-V0 passive arm-receiver P0.1 check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 passive arm-receiver P0.1 check passed: continuous known commanded minimum Z 383.106478 mm; receiver top Z 320 mm; 63.106478 mm residual")
    print("Three ACE MA30M units provide 10.507589 J arithmetic catalog capacity; application, guides, load path, stops and physical proof remain open")
    print("28 evidence rows NOT EXECUTED / NOT AUTHORIZED; EG-008 and EG-009 remain PARTIAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
