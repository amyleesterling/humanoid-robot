#!/usr/bin/env python3
"""Fail-closed checks for R257 Lot A inquiry P0.3."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "procurement/hr-v0/lot-a-inquiry-p0.3"
REL = ROOT / "release/hr-v0/lot-a-inquiry-p0.3"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.21"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.21"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    for directory in (OUT, REL, CFG, CFGR):
        for row in rows(directory / "file-manifest.csv"):
            path = directory / row["path"]
            if not path.is_file() or str(path.stat().st_size) != row["bytes"] or sha(path) != row["sha256"]:
                errors.append(f"manifest mismatch: {path}")
    routes = rows(OUT / "inquiry-route-register.csv")
    tx = rows(OUT / "transmittal-register.csv")
    questions = rows(OUT / "metrology-question-register.csv")
    method_bids = rows(OUT / "method-bid-schedule.csv")
    char_bids = rows(OUT / "characteristic-bid-schedule.csv")
    attachments = rows(OUT / "attachment-manifest.csv")
    responses = rows(OUT / "response-template-register.csv")
    gates = rows(OUT / "decision-gate.csv")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    if len(routes) != 5 or any("NOT" not in row["selection_state"] for row in routes): errors.append("five held routes changed")
    if len(tx) != 5 or any(row["send_authorization"] != "NOT AUTHORIZED" or row["sent_state"] != "NOT SENT" or row["sender_identity"] != "SELECTION REQUIRED" or row["reply_address"] != "SELECTION REQUIRED" for row in tx): errors.append("transmission state promoted")
    if len(questions) != 99 or len({(row["method_id"], row["category"], row["question"]) for row in questions}) != 33 or any(row["state"] != "UNSENT / NOT RECEIVED" for row in questions): errors.append("expected 33 unique / 99 provider-attributed questions")
    if len(method_bids) != 15 or any(row["bid_state"] != "NOT RECEIVED" for row in method_bids): errors.append("method bids changed")
    if len(char_bids) != 54 or {row["characteristic_id"] for row in char_bids} != {f"R256-MZ-{index:03d}" for index in range(1, 19)} or any(row["bid_state"] != "NOT RECEIVED" or row["quoted_price"] or row["lead_time"] or row["technical_disposition"] != "NOT EXECUTED" for row in char_bids): errors.append("characteristic bids incomplete or populated")
    required = {"feature-register.csv", "measurand-definition.csv", "transform-register.csv", "execution-result-template.csv", "XMHD-540.N101.I101.STP", "FR13-H101K.stp", "FR13-S102K.stp"}
    if len(attachments) != 14 or not required.issubset({Path(row["path"]).name for row in attachments}) or any(sha(ROOT / row["path"]) != row["sha256"] for row in attachments): errors.append("attachment hashes/scope incomplete")
    if len(responses) != 8 or sorted(int(row["response_rows"]) for row in responses) != [4, 8, 18, 18, 18, 33, 33, 33] or any(row["response_state"] != "BLANK / NOT RECEIVED" or sha(OUT / row["path"]) != row["sha256"] for row in responses): errors.append("isolated response templates incorrect")
    if len(gates) != 16 or len(acceptance) != 16 or any(row["state"] != "OPEN" for row in gates) or any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" or row["approver"] for row in acceptance): errors.append("gates or acceptances promoted")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    false_keys = ("provider_selected", "purchase_authorized", "order_placed", "shipment_authorized", "work_authorized", "physical_articles_received", "qualified_review_complete", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit")
    if status["identifier"] != "HR-V0-LOT-A-INQUIRY-P0.3" or status["messages_sent"] != 0 or status["responses_received"] != 0 or status["transmissions_authorized"] != 0 or any(status[key] for key in false_keys): errors.append("package status promoted")
    config = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    if (config["identifier"], config["current_records"], config["supersession_records"], config["open_holds"], config["acceptance_rows"]) != ("HR-V0-CONFIG-REC-P0.21", 40, 33, 125, 158): errors.append("configuration counts mismatch")
    for path in (OUT / "index.html", REL / "index.html", CFG / "index.html", CFGR / "index.html"):
        text = path.read_text(encoding="utf-8")
        for token in (WARNING, "font:clamp(16px", "font-size:14px", "79</div>source features", "18</div>characteristics per provider", "Nothing sent"):
            if token not in text: errors.append(f"{path} omits {token}")
    if errors:
        print("R257 Lot A inquiry P0.3: FAIL", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print("R257 Lot A inquiry P0.3: PASS")
    print("5 routes; 79 source features; 18 characteristics/provider; 0 sends/responses/authorizations")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
