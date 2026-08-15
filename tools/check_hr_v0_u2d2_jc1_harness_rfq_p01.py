#!/usr/bin/env python3
"""Fail-closed checks for R262 custom-harness RFQ package."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-U2D2-JC1-HARNESS-RFQ-P0.1"
HID = "HR-V0-U2D2-JC1-HARNESS-P0.1"
CID = "HR-V0-CONFIG-REC-P0.26"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "procurement/hr-v0/u2d2-jc1-harness-rfq-p0.1"
REL = ROOT / "release/hr-v0/u2d2-jc1-harness-rfq-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.26"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.26"
ZIP_NAME = f"{ID}-UNSENT.zip"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    required = {
        "source-register.csv": 8,
        "supplier-route.csv": 3,
        "harness-requirement.csv": 12,
        "provider-question-register.csv": 18,
        "response-evaluation.csv": 12,
        "transmission-register.csv": 1,
        "open-holds.csv": 10,
        "acceptance-matrix.csv": 12,
    }
    for directory in (OUT, REL):
        for name, count in required.items():
            path = directory / name
            need(path.is_file(), f"missing {path.relative_to(ROOT)}")
            if path.is_file():
                data = rows(path)
                need(len(data) == count, f"{name} expected {count} rows, got {len(data)}")
                need(all(row.get("warning") == WARNING for row in data), f"warning drift in {name}")
        for name in ("assembly-definition.svg", "request-message.txt", "package-status.json", "index.html", ZIP_NAME):
            need((directory / name).is_file(), f"missing {directory.relative_to(ROOT) / name}")
        manifest = {row["path"]: row for row in rows(directory / "file-manifest.csv")}
        actual = sorted(path.name for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
        need(sorted(manifest) == actual, f"manifest membership mismatch in {directory.relative_to(ROOT)}")
        for name in actual:
            need(manifest[name]["sha256"] == sha(directory / name), f"manifest hash mismatch {directory.relative_to(ROOT) / name}")
            need(int(manifest[name]["bytes"]) == (directory / name).stat().st_size, f"manifest size mismatch {directory.relative_to(ROOT) / name}")

    routes = {row["route_id"]: row for row in rows(OUT / "supplier-route.csv")}
    need(routes["ROUTE-01"]["disposition"] == "PRIMARY UNSENT EVIDENCE/QUOTE ROUTE" and routes["ROUTE-01"]["external_action"] == "NOT SENT", "GAM route state drift")
    need(routes["ROUTE-02"]["disposition"] == "BACKUP HOLD", "project crimp route must remain held")
    need(routes["ROUTE-03"]["disposition"] == "REJECT AS COMPLETE HARNESS; COUPON OPTION ONLY" and "304.8" in routes["ROUTE-03"]["reason"], "catalog-lead rejection drift")

    reqs = {row["req_id"]: row for row in rows(OUT / "harness-requirement.csv")}
    for req_id in ("RFQ-REQ-02", "RFQ-REQ-03"):
        need("cavity 2 physically empty" in reqs[req_id]["requirement"], f"cavity-2 omission missing from {req_id}")
    need("A1-to-B1" in reqs["RFQ-REQ-04"]["requirement"] and "A3-to-B3" in reqs["RFQ-REQ-04"]["requirement"] and "no splice" in reqs["RFQ-REQ-04"]["requirement"], "connectivity request drift")
    need("500 +/- 5 mm" in reqs["RFQ-REQ-06"]["requirement"], "finished-length request drift")
    need("25 +/- 5 mm" in reqs["RFQ-REQ-07"]["requirement"], "pair-lay request drift")
    need("do not infer" in reqs["RFQ-REQ-08"]["requirement"], "orientation ambiguity control missing")

    questions = rows(OUT / "provider-question-register.csv")
    need(len(questions) == 18 and all(row["state"] == "UNSENT" for row in questions), "provider questions must remain 18/18 UNSENT")
    evaluation = rows(OUT / "response-evaluation.csv")
    need(all(not row["response"] and row["review_state"] == "NOT RECEIVED" and not row["reviewer"] and row["decision"] == "OPEN" for row in evaluation), "response evaluation must remain blank/open")
    transmission = rows(OUT / "transmission-register.csv")[0]
    need(transmission["authorization"] == "NOT AUTHORIZED" and transmission["state"] == "UNSENT" and not transmission["sent_at"] and not transmission["sender"] and not transmission["response_uri"], "transmission improperly advanced")
    need(transmission["attachment_sha256"] == sha(OUT / ZIP_NAME), "transmission ZIP hash mismatch")

    with zipfile.ZipFile(OUT / ZIP_NAME) as archive:
        names = archive.namelist()
        expected_names = ["request-message.txt", "assembly-definition.svg", "harness-requirement.csv", "provider-question-register.csv", "response-evaluation.csv", "PAYLOAD-MANIFEST.csv", "PACKAGE-CONTROL.json"]
        need(names == expected_names, f"ZIP membership/order mismatch: {names}")
        need(all(item.date_time == (2026, 8, 12, 0, 0, 0) for item in archive.infolist()), "ZIP timestamps are not deterministic")
        control = json.loads(archive.read("PACKAGE-CONTROL.json"))
        need(control == {"identifier":ID,"state":"UNSENT","purchase_order":False,"work_authority":False,"warning":WARNING}, "ZIP control state mismatch")
        payload_manifest = list(csv.DictReader(archive.read("PAYLOAD-MANIFEST.csv").decode().splitlines()))
        for row in payload_manifest:
            content = archive.read(row["path"])
            need(len(content) == int(row["bytes"]) and hashlib.sha256(content).hexdigest() == row["sha256"], f"ZIP internal manifest mismatch: {row['path']}")
    need((OUT / ZIP_NAME).read_bytes() == (REL / ZIP_NAME).read_bytes(), "engineering/release ZIP bytes differ")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == ID and status.get("parent_harness") == HID and status.get("manufacturer_build_route_defined") is True, "package identity/route state mismatch")
    for field in ("external_transmission_authorized","external_transmission_sent","provider_response_received","quote_received","provider_selected","purchase_authorized","purchase_order_issued","physical_article_exists","physical_test_executed","qualified_review_complete","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status.get(field) is False, f"fail-closed package field changed: {field}")

    bom = {row["item_id"]: row for row in rows(ROOT / "bom/bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom/hr-v0-bom-closure.csv")}
    need(len(bom) >= 108, "system BOM count below R262 minimum")
    for item_id in ("BOM-054", "BOM-055", "BOM-061"):
        need(closure[item_id]["closure_class"] == "exact_candidate_hold", f"closure class drift for {item_id}")
        need("R262" in bom[item_id]["selection_basis"], f"R262 BOM boundary missing for {item_id}")

    cfg = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    expected_cfg = {"identifier":CID,"round":"R262","system_bom_groups":108,"current_records":45,"supersession_records":38,"bom_integration_records":29,"gate_records":11,"open_holds":175,"acceptance_rows":216}
    for key, value in expected_cfg.items():
        need(cfg.get(key) == value, f"config {key}: expected {value!r}, got {cfg.get(key)!r}")
    need(any(row["record_id"] == "CFG-45" and row["identifier"] == ID for row in rows(CFG / "current-configuration-map.csv")), "CFG-45 missing")
    need(any(row["record_id"] == "SUP-38" and row["current_or_required_successor"] == CID for row in rows(CFG / "supersession-map.csv")), "SUP-38 missing")
    need(all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "OPEN" for row in rows(CFG / "acceptance-matrix.csv")), "configuration acceptance state advanced")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    for domain in ("electrical", "bill_of_materials", "assembly"):
        product = next((row for row in release["current_products"] if row.get("domain") == domain), {})
        need(product.get("configuration_reconciliation") in {CID, "HR-V0-CONFIG-REC-P0.27", "HR-V0-CONFIG-REC-P0.28", "HR-V0-CONFIG-REC-P0.29", "HR-V0-CONFIG-REC-P0.30", "HR-V0-CONFIG-REC-P0.31", "HR-V0-CONFIG-REC-P0.32", "HR-V0-CONFIG-REC-P0.33", "HR-V0-CONFIG-REC-P0.34", "HR-V0-CONFIG-REC-P0.35"} and product.get("u2d2_jc1_harness_rfq") == ID and ID in product.get("supporting_identifiers", []) and CID in product.get("supporting_identifiers", []), f"release metadata stale: {domain}")

    for left, right in ((OUT, REL), (CFG, CFGR)):
        left_files = sorted(path.name for path in left.iterdir() if path.is_file())
        right_files = sorted(path.name for path in right.iterdir() if path.is_file())
        need(left_files == right_files, f"mirror membership mismatch: {left.relative_to(ROOT)}")
        for name in left_files:
            need(sha(left / name) == sha(right / name), f"mirror digest mismatch: {name}")

    page = (REL / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "font:clamp(16px", "font-size:14px", "UNSENT", "assembly-definition.svg", "No splice"):
        need(token in page, f"web guide token missing: {token}")

    if errors:
        print("R262 U2D2-to-JC1 harness RFQ validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("R262 U2D2-to-JC1 harness RFQ validation: PASS")
    print("8 sources; 3 routes; 12 requirements; 18 UNSENT questions; 10 holds; 12 blank acceptances")
    print("Deterministic ZIP and mirror parity: PASS")
    print("No transmission, response, quote, selection, purchase, article, test, work or energization authority exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
