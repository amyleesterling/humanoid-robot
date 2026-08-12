#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-JOINT-MEAS-DEF-P0.1."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_joint_measurement_definition_p01 as gen  # noqa: E402


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(condition: bool, message: str, errors: list[str]) -> None:
    if condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    out = gen.OUT
    rel = gen.REL
    status = json.loads((out / "package-status.json").read_text(encoding="utf-8"))
    _, derived = gen.derive_features()
    actual = rows(out / "feature-register.csv")
    measurands = rows(out / "measurand-definition.csv")
    hsi = rows(out / "hsi-closure-map.csv")
    results = rows(out / "execution-result-template.csv")
    selections = rows(out / "selection-register.csv")
    acceptance = rows(out / "acceptance-matrix.csv")
    fail(status["identifier"] != gen.ID, "wrong identifier", errors)
    fail(status["source_bound_features"] != len(derived), "feature count mismatch", errors)
    fail(len(actual) != len(derived), "feature-register row count mismatch", errors)
    expected = {row["feature_id"]: row["geometric_signature"] for row in derived}
    observed = {row["feature_id"]: row["geometric_signature"] for row in actual}
    fail(expected != observed, "source-derived geometric signatures do not reproduce", errors)
    fail(len(measurands) != 18 or len(results) != 18, "expected 18 characteristics and result rows", errors)
    fail(len(hsi) != 20 or {row["hsi_id"] for row in hsi} != {f"HSI-{index:03d}" for index in range(1, 21)}, "HSI coverage is incomplete", errors)
    fail(any(row["reported_result"] or row["expanded_uncertainty"] for row in measurands), "measurand result fields must remain blank", errors)
    fail(any(row["reported_result"] or row["expanded_uncertainty"] or row["raw_evidence_uri"] or row["approver"] for row in results), "execution result template is not blank", errors)
    fail(any(row["state"] != "SELECTION REQUIRED" for row in selections), "a selection is not held", errors)
    fail(any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" or row["approver"] for row in acceptance), "an acceptance row is not blank/open", errors)
    fail(any(status[key] for key in ("provider_selected", "physical_work_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "qualified_review_complete", "safety_credit")), "authority or acceptance flag is true", errors)
    fail(status["cad_nominal_is_received_evidence"], "CAD nominal incorrectly promoted to received evidence", errors)
    for source in rows(out / "source-binding.csv")[:3]:
        fail(sha(ROOT / source["path"]) != source["sha256"], f"source hash mismatch: {source['article']}", errors)
    for directory in (out, rel, gen.CFG, gen.CFGR):
        for item in rows(directory / "file-manifest.csv"):
            fail(sha(directory / item["path"]) != item["sha256"], f"manifest mismatch: {directory.name}/{item['path']}", errors)
    for path in sorted(item for item in out.rglob("*") if item.is_file()):
        if path.name != "file-manifest.csv" and path.suffix.lower() in {".csv", ".json", ".html", ".svg"}:
            fail(gen.WARNING not in path.read_text(encoding="utf-8"), f"warning absent: {path.name}", errors)
    config = json.loads((gen.CFG / "package-status.json").read_text(encoding="utf-8"))
    fail((config["current_records"], config["supersession_records"], config["open_holds"], config["acceptance_rows"]) != (39, 31, 109, 142), "configuration counts mismatch", errors)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS {gen.ID}: {len(actual)} source features; 18 characteristics; 20 HSI routes; zero results/authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
