#!/usr/bin/env python3
"""Validate R243 P1.21 termination-process evidence and config P0.7."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/termination/hr-v0-p121-termination-p0.1"
OUT = ROOT / "release/hr-v0/p121-termination-p0.1"
CFG_ENG = ROOT / "configuration/hr-v0-config-reconciliation-p0.7"
CFG_OUT = ROOT / "release/hr-v0/configuration-reconciliation-p0.7"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_dir(directory: Path, expected: set[str], fail) -> None:
    fail(not directory.is_dir() or {p.name for p in directory.iterdir() if p.is_file()} != expected, f"membership: {directory}")
    manifest = rows(directory / "file-manifest.csv")
    actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    fail({row["path"] for row in manifest} != actual, f"manifest membership: {directory}")
    for row in manifest:
        path = directory / row["path"]
        fail(not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"], f"manifest mismatch: {path}")


def main() -> int:
    errors: list[str] = []
    fail = lambda condition, message: errors.append(message) if condition else None
    common = {"README.md","source-register.csv","exact-material-candidates.csv","tool-candidate-register.csv","endpoint-termination-schedule.csv","termination-process-plan.csv","torque-installation-plan.csv","pull-test-criteria.csv","r242-hold-disposition.csv","open-holds.csv","inspection-register.csv","termination-candidate-diagram.svg","package-status.json","file-manifest.csv"}
    check_dir(ENG, common, fail)
    check_dir(OUT, common | {"index.html"}, fail)
    for name in common - {"file-manifest.csv"}:
        fail((ENG / name).read_bytes() != (OUT / name).read_bytes(), f"engineering/release mismatch: {name}")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    expected_status = {
        "identifier":"HR-V0-P121-TERM-P0.1", "round":"R243", "conductor_candidates":7,
        "endpoint_candidates":14, "eight_mm_insulated_endpoints":12, "seven_mm_uninsulated_endpoints":2,
        "exact_ferrule_order_codes":["3200043","3200263"],
        "exact_primary_tool_candidates":["1212034","1212150","1212224"],
        "crimp_coupon_force_N":40, "crimp_coupon_duration_s":60,
        "open_holds":12, "blank_inspections":20, "warning":WARNING,
    }
    for key, value in expected_status.items():
        fail(status.get(key) != value, f"status: {key}")
    for key in ("r242_h02_closed","received_crimp_evidence_exists","terminal_application_accepted","driver_bits_selected","tool_calibration_accepted","installed_termination_evidence_exists","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        fail(status.get(key) is not False, f"{key} must be false")
    materials = {row["item"]: row for row in rows(OUT / "exact-material-candidates.csv")}
    fail(set(materials) != {"3200043","3200263"}, "exact ferrule set")
    fail(materials.get("3200043",{}).get("application_quantity") != "12 ferrules" or materials.get("3200263",{}).get("application_quantity") != "2 ferrules", "application quantities")
    fail(any(row["procurement_released"] != "NO" or row["state"] != "EXACT HELD CANDIDATE" for row in materials.values()), "ferrule hold state")
    tools = {row["item"]: row for row in rows(OUT / "tool-candidate-register.csv")}
    fail(not {"1212034","1212150","1212224","SELECTION REQUIRED"}.issubset(tools), "tool register")
    fail(any(row["purchase_authorized"] != "NO" for row in tools.values()), "tool purchase must remain unauthorized")
    endpoints = rows(OUT / "endpoint-termination-schedule.csv")
    fail(len(endpoints) != 14 or len({row["endpoint_id"] for row in endpoints}) != 14 or len({row["endpoint"] for row in endpoints}) != 14, "fourteen unique endpoints")
    fail(sum("3200043" in row["ferrule_candidate"] for row in endpoints) != 12, "twelve 8 mm endpoints")
    fail(sum("3200263" in row["ferrule_candidate"] for row in endpoints) != 2, "two 7 mm endpoints")
    fail({row["endpoint"] for row in endpoints if "3200263" in row["ferrule_candidate"]} != {"SR1:A1","SRA1:A1"}, "Pilz-only 7 mm split")
    fail(any(row["physical_result"] != "NOT EXECUTED" or row["state"] != "CANDIDATE - NOT INSTALLED" for row in endpoints), "endpoint fail-closed state")
    pull = {row["test_id"]: row for row in rows(OUT / "pull-test-criteria.csv")}
    fail(set(pull) != {"PULL-001","PULL-002","PULL-003"}, "pull test membership")
    fail(any(pull[key]["force_N"] != "40" or pull[key]["duration_s"] != "60" or pull[key]["state"] != "NOT EXECUTED" for key in ("PULL-001","PULL-002")), "coupon criteria")
    fail(pull["PULL-003"]["force_N"] != "SELECTION REQUIRED" or pull["PULL-003"]["state"] != "OPEN", "installed pull must remain unresolved")
    torque = rows(OUT / "torque-installation-plan.csv")
    fail(len(torque) != 3 or any(row["state"] != "OPEN" for row in torque), "torque plan open")
    fail(not any("0.5 N m" in row["project_candidate"] for row in torque), "Pilz torque")
    fail(not any("0.7 N m" in row["project_candidate"] and "0.6 to 0.8" in row["manufacturer_requirement"] for row in torque), "KWD candidate torque")
    disposition = rows(OUT / "r242-hold-disposition.csv")
    fail(len(disposition) != 1 or disposition[0]["prior_hold"] != "R242-H02" or disposition[0]["disposition"] != "PARTIALLY ADDRESSED - OPEN", "R242-H02 disposition")
    fail(len(rows(OUT / "open-holds.csv")) != 12 or any(row["state"] != "OPEN" for row in rows(OUT / "open-holds.csv")), "holds")
    inspections = rows(OUT / "inspection-register.csv")
    fail(len(inspections) != 20 or any(row["state"] != "NOT EXECUTED" or row["result"] or row["evidence_uri"] for row in inspections), "blank inspections")
    source_text = " ".join(" ".join(row.values()) for row in rows(OUT / "source-register.csv"))
    for token in ("3200043","3200263","1212034","1212150","1212224","40 N","60 seconds","21396-EN-23"):
        fail(token not in source_text, f"source token: {token}")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","12 × item 3200043","2 × item 3200263","40 N · 60 s","R242-H02","Zoom in"):
        fail(token not in page, f"guide token: {token}")
    cfg_common = {"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    check_dir(CFG_ENG, cfg_common, fail)
    check_dir(CFG_OUT, cfg_common | {"index.html"}, fail)
    cfg = json.loads((CFG_OUT / "package-status.json").read_text(encoding="utf-8"))
    for key, value in {"identifier":"HR-V0-CONFIG-REC-P0.7","round":"R243","system_bom_groups":98,"current_records":26,"supersession_records":14,"bom_integration_records":18,"gate_records":11,"open_holds":35,"acceptance_rows":41}.items():
        fail(cfg.get(key) != value, f"config: {key}")
    fail(cfg.get("current_core_electrical_identifier") != "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 current")
    fail(cfg.get("unaccepted_panel_topology_candidate") != "V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE", "P1.21 unaccepted")
    bom = {row["item_id"]: row for row in rows(ROOT / "bom/bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom/hr-v0-bom-closure.csv")}
    fail(len(bom) != 98 or len(closure) != 98 or set(bom) != set(closure), "98-group BOM coverage")
    fail("3200043" not in bom.get("BOM-098",{}).get("manufacturer_part_number","") or "3200263" not in bom.get("BOM-098",{}).get("manufacturer_part_number", ""), "BOM-098 identities")
    fail(closure.get("BOM-098",{}).get("closure_class") != "exact_candidate_hold" or closure.get("BOM-098",{}).get("allowed_action") != "HOLD", "BOM-098 hold")
    integration = {row["item_id"]: row for row in rows(CFG_OUT / "bom-integration-map.csv")}
    fail(len(integration) != 18 or integration.get("BOM-098",{}).get("procurement_released") != "NO", "config BOM integration")
    sources = rows(CFG_OUT / "source-hash-register.csv")
    fail(len(sources) != 26, "config source count")
    for row in sources:
        source = ROOT / row["source_path"]
        if row["source_path"] == "release/hr-v0/release-candidate.json":
            fail(len(row["sha256"]) != 64, "historical P0.7 release-candidate hash format")
        else:
            fail(not source.is_file() or digest(source) != row["sha256"], f"config source hash: {row['source_path']}")
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    for gate in ("EG-002","EG-003","EG-004","EG-012","EG-015","EG-018","EG-020","EG-022"):
        fail(gates.get(gate,{}).get("status") != "partial" or "p121-termination-p0.1" not in gates.get(gate,{}).get("evidence_location", ""), f"gate sync: {gate}")
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    bill = next(product for product in release["current_products"] if product["domain"] == "bill_of_materials")
    fail(bill.get("system_group_count") != 98 or bill.get("configuration_reconciliation") != "HR-V0-CONFIG-REC-P0.8", "current release BOM metadata")
    if errors:
        print("HR-V0 R243 P1.21 termination process: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("HR-V0 R243 P1.21 termination process: PASS")
    print("14 endpoints; 12 x 3200043 and 2 x 3200263 held; 40 N / 60 s coupons unexecuted; 12 holds")
    print("No procurement, fabrication, assembly, connection, powered test, motion, safety credit or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
