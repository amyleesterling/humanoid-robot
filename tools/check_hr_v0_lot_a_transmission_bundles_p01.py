#!/usr/bin/env python3
"""Fail-closed checks for R258 deterministic Lot A bundles."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_lot_a_transmission_bundles_p01 as gen  # noqa: E402


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
    routes = gen.inquiry.old.read_csv(gen.SOURCE / "inquiry-route-register.csv")[0]
    bundles = rows(gen.OUT / "bundle-register.csv")
    members = rows(gen.OUT / "bundle-member-register.csv")
    if len(bundles) != 5 or {row["route_id"] for row in bundles} != {row["route_id"] for row in routes}: errors.append("five-route bundle coverage failed")
    for route in routes:
        route_id = route["route_id"]
        expected, expected_members = gen.build_bundle(route)
        row = next(item for item in bundles if item["route_id"] == route_id)
        path = gen.OUT / row["archive_path"]
        if path.read_bytes() != expected or sha(path) != row["archive_sha256"] or str(path.stat().st_size) != row["archive_bytes"]: errors.append(f"archive not deterministic/current: {route_id}")
        with zipfile.ZipFile(io.BytesIO(expected)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or any(info.date_time != gen.FIXED_ZIP_TIME or info.CRC != zipfile.crc32(archive.read(info.filename)) for info in archive.infolist()): errors.append(f"archive metadata/CRC defect: {route_id}")
            control = json.loads(archive.read("00-CONTROL/bundle-control.json"))
            if control["route_id"] != route_id or control["send_authorization"] != "NOT AUTHORIZED" or control["sent_state"] != "NOT SENT" or control["procurement_authorized"] or control["work_authorized"]: errors.append(f"control promoted: {route_id}")
            text_payload = "\n".join(archive.read(name).decode("utf-8", errors="ignore") for name in names if name.endswith((".csv", ".json", ".md", ".txt")))
            other_routes = {item["route_id"] for item in routes} - {route_id}
            if any(other in text_payload for other in other_routes): errors.append(f"cross-route leakage: {route_id}")
            if route_id == "R257-RT-01" and any(f"R257-RQ-{index:02d}" in text_payload for index in range(9, 13)): errors.append("technical questions leaked to sales")
            if route_id == "R257-RT-02" and any(f"R257-RQ-{index:02d}" in text_payload for index in range(1, 9)): errors.append("sales questions leaked to technical support")
            metrology = route_id not in {"R257-RT-01", "R257-RT-02"}
            if metrology and (len([name for name in names if name.startswith("02-SCOPE/R257-AT-")]) != 14 or len(rows_from_bytes(archive.read("01-RESPONSE/characteristic-bid-response.csv"))) != 18 or len(rows_from_bytes(archive.read("01-RESPONSE/method-bid-response.csv"))) != 5): errors.append(f"metrology payload incomplete: {route_id}")
            if not metrology and any(name.startswith("02-SCOPE/") or "characteristic" in name or "method-bid" in name for name in names): errors.append(f"metrology content leaked to ROBOTIS: {route_id}")
        registered = [item for item in members if item["route_id"] == route_id]
        if len(registered) != len(expected_members) or any(item["state"] != "UNSENT / NOT AUTHORIZED" for item in registered): errors.append(f"member register mismatch: {route_id}")
    gates = rows(gen.OUT / "decision-gate.csv")
    events = rows(gen.OUT / "transmission-event-register.csv")
    acceptance = rows(gen.OUT / "acceptance-matrix.csv")
    if len(gates) != 11 or any(row["state"] != "OPEN" for row in gates) or not any("redistribution" in row["decision"].lower() for row in gates): errors.append("gates changed or vendor-CAD redistribution gate missing")
    if len(events) != 5 or any(row["state"] != "NOT SENT" or row["authorization_evidence_uri"] or row["transport"] or row["recipient"] or row["sender"] or row["sent_utc"] or row["receipt_evidence_uri"] for row in events): errors.append("transmission event populated")
    if len(acceptance) != 11 or any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" or row["approver"] for row in acceptance): errors.append("acceptance promoted")
    status = json.loads((gen.OUT / "package-status.json").read_text(encoding="utf-8"))
    false_keys = ("sender_identity_selected", "reply_address_selected", "provider_selected", "purchase_authorized", "work_authorized", "physical_articles_received", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "qualified_review_complete", "safety_credit")
    if status["identifier"] != gen.ID or status["transmissions_authorized"] or status["messages_sent"] or status["responses_received"] or any(status[key] for key in false_keys): errors.append("package status promoted")
    config = json.loads((gen.CFG / "package-status.json").read_text(encoding="utf-8"))
    if (config["identifier"], config["current_records"], config["supersession_records"], config["open_holds"], config["acceptance_rows"]) != (gen.CID, 41, 34, 136, 169): errors.append("configuration counts mismatch")
    for path in (gen.OUT / "index.html", gen.REL / "index.html", gen.CFG / "index.html", gen.CFGR / "index.html"):
        text = path.read_text(encoding="utf-8")
        for token in (gen.WARNING, "font:clamp(16px", "font-size:14px", "No archive is authorized or sent", "redistribution rights"):
            if token not in text: errors.append(f"{path} omits {token}")
    if errors:
        print("R258 Lot A transmission bundles: FAIL", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print("R258 Lot A transmission bundles: PASS")
    print("5 deterministic isolated archives; exact internal manifests; 0 sends/authorizations")
    print(gen.WARNING)
    return 0


def rows_from_bytes(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


if __name__ == "__main__":
    raise SystemExit(main())
