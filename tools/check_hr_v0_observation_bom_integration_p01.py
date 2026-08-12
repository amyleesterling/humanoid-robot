#!/usr/bin/env python3
"""Fail-closed checks for R259 observation BOM integration."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import generate_hr_v0_observation_bom_integration_p01 as gen


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    for directory in (gen.OUT, gen.REL, gen.CFG, gen.CFGR):
        for row in rows(directory / "file-manifest.csv"):
            path = directory / row["path"]
            if not path.is_file() or str(path.stat().st_size) != row["bytes"] or sha(path) != row["sha256"]:
                errors.append(f"manifest mismatch: {path}")
    bom = {row["item_id"]: row for row in rows(gen.BOM)}
    closure = {row["item_id"]: row for row in rows(gen.CLOSURE)}
    expected = {f"BOM-{index:03d}" for index in range(99, 109)}
    if len(bom) != 108 or len(closure) != 108 or set(bom) != set(closure) or not expected <= set(bom):
        errors.append("108-group BOM/closure parity failed")
    if any(bom[item]["quantity"] != value for item, value in {"BOM-099":"1","BOM-100":"1","BOM-101":"1","BOM-102":"1","BOM-103":"2","BOM-104":"1","BOM-105":"1","BOM-106":"11","BOM-107":"1","BOM-108":"1"}.items()):
        errors.append("observation quantities changed")
    if "1751280" not in bom["BOM-103"]["manufacturer_part_number"] or "1751280" not in bom["BOM-105"]["manufacturer_part_number"] or "ESQ-120-33-G-D" not in bom["BOM-104"]["manufacturer_part_number"]:
        errors.append("connector identities changed")
    bindings = rows(gen.OUT / "item-binding.csv")
    assemblies = rows(gen.OUT / "assembly-quantity-register.csv")
    mounting = rows(gen.OUT / "mounting-interface-register.csv")
    conductors = rows(gen.OUT / "conductor-candidate-register.csv")
    holds = rows(gen.OUT / "selection-holds.csv")
    acceptance = rows(gen.OUT / "acceptance-matrix.csv")
    if len(bindings) != 10 or {row["item_id"] for row in bindings} != expected:
        errors.append("item binding coverage changed")
    if len(assemblies) != 4 or sum(int(row["quantity"]) for row in assemblies) != 4:
        errors.append("assembly quantities changed")
    if len(mounting) != 2 or {row["site_count"] for row in mounting} != {"4"} or any(row["hardware_identity"] != "SELECTION REQUIRED" for row in mounting):
        errors.append("mounting interface boundary changed")
    if len(conductors) != 11 or len({row["order_code"] for row in conductors}) != 11 or any(row["procurement_quantity"] != "SELECTION REQUIRED" or row["cut_length"] != "SELECTION REQUIRED" for row in conductors):
        errors.append("conductor boundary changed")
    if len(holds) != 8 or any(row["state"] not in {"OPEN","DESIGN REQUIRED","SELECTION REQUIRED","NOT EXECUTED"} for row in holds):
        errors.append("selection holds changed")
    if len(acceptance) != 10 or any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" or row["evidence_uri"] or row["approver"] for row in acceptance):
        errors.append("acceptance was promoted")
    mutable_successor_sources = {"bom/bom.csv", "bom/hr-v0-bom-closure.csv", "release/hr-v0/release-candidate.json"}
    for row in rows(gen.OUT / "source-register.csv"):
        path = gen.ROOT / row["path"]
        if not path.is_file() or (row["path"] not in mutable_successor_sources and sha(path) != row["sha256"]):
            errors.append(f"source hash mismatch: {row['path']}")
    status = json.loads((gen.OUT / "package-status.json").read_text(encoding="utf-8"))
    false_keys = ("exact_mounting_hardware_selected","cut_lengths_selected","physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")
    if status["identifier"] != gen.ID or status["system_bom_groups"] != 108 or status["new_bom_groups"] != 10 or not status["hierarchical_bom_integrated"] or any(status[key] for key in false_keys):
        errors.append("package status changed/promoted")
    cfg = json.loads((gen.CFG / "package-status.json").read_text(encoding="utf-8"))
    expected_counts = {"identifier":gen.CID,"system_bom_groups":108,"current_records":42,"supersession_records":35,"bom_integration_records":28,"open_holds":144,"acceptance_rows":179}
    if any(cfg.get(key) != value for key, value in expected_counts.items()):
        errors.append("configuration counts changed")
    current = rows(gen.CFG / "current-configuration-map.csv")
    source_hashes = {row["source_path"]: row["sha256"] for row in rows(gen.CFG / "source-hash-register.csv")}
    if len(current) != len(source_hashes) or any(source_hashes.get(row["source_path"]) != sha(gen.ROOT / row["source_path"]) for row in current if row["source_path"] not in mutable_successor_sources):
        errors.append("current-configuration source hash parity failed")
    hold15 = next((row for row in rows(gen.CFG / "open-holds.csv") if row["hold_id"] == "HOLD-15"), {})
    if gen.ID not in hold15.get("closure_evidence", "") or hold15.get("state") != "DESIGN REQUIRED":
        errors.append("HOLD-15 was hidden or improperly closed")
    release = json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    products = release["current_products"]
    bill = next(row for row in products if row.get("domain") == "bill_of_materials")
    electrical = next(row for row in products if row.get("domain") == "electrical")
    if bill.get("system_group_count") != 108 or bill.get("configuration_reconciliation") not in {gen.CID, "HR-V0-CONFIG-REC-P0.24"} or bill.get("observation_bom_integration") != gen.ID or gen.ID not in bill.get("supporting_identifiers", []):
        errors.append("release BOM metadata is stale")
    if electrical.get("configuration_reconciliation") not in {gen.CID, "HR-V0-CONFIG-REC-P0.24"} or electrical.get("observation_bom_integration") != gen.ID:
        errors.append("release electrical metadata is stale")
    for path in (gen.OUT / "index.html", gen.REL / "index.html", gen.CFG / "index.html", gen.CFGR / "index.html"):
        text = path.read_text(encoding="utf-8")
        for token in (gen.WARNING, "font:clamp(16px", "font-size:14px", "108", "Exact mounting hardware"):
            if token not in text:
                errors.append(f"{path} omits {token}")
    if errors:
        print("R259 observation BOM integration: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("R259 observation BOM integration: PASS")
    print("108 system groups; 10 observation groups; all physical/work authority remains false")
    print(gen.WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
