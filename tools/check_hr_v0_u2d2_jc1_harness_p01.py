#!/usr/bin/env python3
"""Fail-closed validation for R261 U2D2-to-JC1 harness candidate."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-U2D2-JC1-HARNESS-P0.1"
CID = "HR-V0-CONFIG-REC-P0.25"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ENG = ROOT / "electrical/harness/hr-v0-u2d2-jc1-harness-p0.1"
REL = ROOT / "release/hr-v0/u2d2-jc1-harness-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.25"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.25"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    required = {
        "source-register.csv": 5,
        "interface-pinmap.csv": 3,
        "harness-bom.csv": 6,
        "conductor-and-build-register.csv": 7,
        "route-screen.csv": 5,
        "process-and-inspection-plan.csv": 9,
        "continuity-isolation-matrix.csv": 7,
        "open-holds.csv": 12,
        "acceptance-matrix.csv": 13,
    }
    for directory in (ENG, REL):
        for name, count in required.items():
            path = directory / name
            if not path.is_file():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            data = rows(path)
            if len(data) != count:
                errors.append(f"{path.relative_to(ROOT)} expected {count} rows, got {len(data)}")
            if any(row.get("warning") != WARNING for row in data):
                errors.append(f"warning drift in {path.relative_to(ROOT)}")
        if not (directory / "index.html").is_file() or WARNING not in (directory / "index.html").read_text(encoding="utf-8"):
            errors.append(f"warning/page missing in {directory.relative_to(ROOT)}")
        manifests = {row["path"]: row for row in rows(directory / "file-manifest.csv")}
        actual = sorted(path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        if sorted(manifests) != actual:
            errors.append(f"manifest membership mismatch in {directory.relative_to(ROOT)}")
        for name in actual:
            if manifests[name]["sha256"] != sha(directory / name) or int(manifests[name]["bytes"]) != (directory / name).stat().st_size:
                errors.append(f"manifest digest/size mismatch: {directory.relative_to(ROOT) / name}")

    pinmap = rows(ENG / "interface-pinmap.csv")
    expected = {
        "1": ("CTRL_GND", "1", "Belden 3051 BK005 black 22 AWG"),
        "2": ("VDD", "2", "NONE - NO WIRE AND NO CONTACT"),
        "3": ("DXL_DATA", "3", "Belden 3051 WH005 white 22 AWG"),
    }
    for row in pinmap:
        exp = expected.get(row["cavity_a"])
        if exp is None or (row["signal"], row["cavity_b"], row["conductor"]) != exp:
            errors.append(f"pin map mismatch at U2D2 cavity {row['cavity_a']}")
    pin2 = next((row for row in pinmap if row["cavity_a"] == "2"), {})
    if "EMPTY" not in pin2.get("state", "") or "NO WIRE AND NO CONTACT" not in pin2.get("conductor", ""):
        errors.append("cavity 2 does not fail closed")

    hbom = rows(ENG / "harness-bom.csv")
    exact = {(r["order_code"], r["quantity"], r["system_bom_binding"]) for r in hbom}
    for wanted in {
        ("EHR-3", "2", "BOM-054"), ("SEH-001T-P0.6", "4", "BOM-055"),
        ("3051 BK005", "one length; raw cut SELECTION REQUIRED", "BOM-106 shared stock"),
        ("3051 WH005", "one length; raw cut SELECTION REQUIRED", "BOM-106 shared stock"),
        ("YRS-260", "manufacturing tool; not system BOM", "N/A"),
    }:
        if wanted not in exact:
            errors.append(f"missing exact harness/tool candidate {wanted}")

    build = {row["characteristic"]: row for row in rows(ENG / "conductor-and-build-register.csv")}
    if build.get("finished length", {}).get("candidate") != "500 +/- 5 mm":
        errors.append("finished-length candidate drift")
    if build.get("raw cut length", {}).get("candidate") != "SELECTION REQUIRED":
        errors.append("raw cut must remain selection required")
    if build.get("pair lay", {}).get("candidate") != "25 +/- 5 mm per turn":
        errors.append("pair-lay candidate drift")
    if build.get("minimum stationary bend radius", {}).get("candidate") != ">= 15 mm":
        errors.append("bend-radius floor drift")

    route = {row["screen_id"]: row for row in rows(ENG / "route-screen.csv")}
    dx = abs(float(route["ROUTE-01"]["x_mm"]) - float(route["ROUTE-02"]["x_mm"]))
    dy = abs(float(route["ROUTE-01"]["y_mm"]) - float(route["ROUTE-02"]["y_mm"]))
    if not math.isclose(dx, 217.75) or not math.isclose(dy, 107.30):
        errors.append("route delta arithmetic mismatch")
    if "325.05" not in route["ROUTE-04"]["basis"] or "174.95" not in route["ROUTE-05"]["basis"]:
        errors.append("route Manhattan/residual screen drift")

    for name in ("process-and-inspection-plan.csv", "acceptance-matrix.csv"):
        data = rows(ENG / name)
        if any(row.get("execution_state") != "NOT EXECUTED" for row in data):
            errors.append(f"executed row found in {name}")
    if any(row["result"] != "OPEN" or row["execution_state"] != "NOT EXECUTED" for row in rows(ENG / "continuity-isolation-matrix.csv")):
        errors.append("physical electrical matrix must be entirely blank/open")

    status = json.loads((ENG / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != ID or status.get("round") != "R261" or not status.get("exact_harness_candidate_defined"):
        errors.append("package identity/candidate state mismatch")
    for field in (
        "u2d2_vdd_contact_or_conductor_present", "raw_cut_length_released", "physical_harness_exists",
        "physical_test_executed", "qualified_review_complete", "procurement_authorized", "fabrication_authorized",
        "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized",
        "energization_authorized", "safety_credit",
    ):
        if status.get(field) is not False:
            errors.append(f"fail-closed package field changed: {field}")

    bom = {row["item_id"]: row for row in rows(ROOT / "bom/bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom/hr-v0-bom-closure.csv")}
    integration = {row["item_id"]: row for row in rows(CFG / "bom-integration-map.csv")}
    for item_id in ("BOM-061", "BOM-107", "BOM-108"):
        states = (bom[item_id]["baseline_status"], closure[item_id]["closure_class"], integration[item_id]["closure_class"])
        if states != ("exact_candidate_hold", "exact_candidate_hold", "exact_candidate_hold"):
            errors.append(f"canonical/config BOM status mismatch for {item_id}: {states}")
    if len(bom) < 108:
        errors.append(f"system BOM group count expected at least 108, got {len(bom)}")

    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    expected_cfg = {"identifier":CID,"round":"R261","current_records":44,"supersession_records":37,"bom_integration_records":29,"gate_records":11,"open_holds":165,"acceptance_rows":204}
    for key, value in expected_cfg.items():
        if cfg_status.get(key) != value:
            errors.append(f"config {key}: expected {value!r}, got {cfg_status.get(key)!r}")
    if any(row.get("execution_state") != "NOT EXECUTED" or row.get("result") != "OPEN" for row in rows(CFG / "acceptance-matrix.csv")):
        errors.append("configuration acceptance rows must remain blank/open")
    if not any(row["record_id"] == "CFG-44" and row["identifier"] == ID for row in rows(CFG / "current-configuration-map.csv")):
        errors.append("CFG-44 missing")
    if not any(row["record_id"] == "SUP-37" and row["current_or_required_successor"] == CID for row in rows(CFG / "supersession-map.csv")):
        errors.append("SUP-37 missing")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    for domain in ("electrical", "bill_of_materials", "assembly"):
        product = next((p for p in release["current_products"] if p.get("domain") == domain), None)
        if not product or product.get("configuration_reconciliation") not in {CID, "HR-V0-CONFIG-REC-P0.26", "HR-V0-CONFIG-REC-P0.27", "HR-V0-CONFIG-REC-P0.28", "HR-V0-CONFIG-REC-P0.29"} or product.get("u2d2_jc1_harness") != ID:
            errors.append(f"release metadata not synchronized for {domain}")
        elif ID not in product.get("supporting_identifiers", []) or CID not in product.get("supporting_identifiers", []):
            errors.append(f"release metadata identifiers missing for {domain}")

    for left, right in ((ENG, REL), (CFG, CFGR)):
        left_files = sorted(path.name for path in left.iterdir() if path.is_file())
        right_files = sorted(path.name for path in right.iterdir() if path.is_file())
        if left_files != right_files:
            errors.append(f"mirror membership mismatch {left.relative_to(ROOT)} -> {right.relative_to(ROOT)}")
        for name in left_files:
            if sha(left / name) != sha(right / name):
                errors.append(f"mirror digest mismatch: {name}")

    if errors:
        print("R261 U2D2-to-JC1 harness validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("R261 U2D2-to-JC1 harness validation: PASS")
    print("5 sources; 3 pin rows; 6 BOM/tool rows; 12 holds; 13 blank acceptances")
    print("BOM-061/107/108 exact-candidate parity: PASS")
    print("No raw cut, physical harness, test, work authority, safety credit or energization authority exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
