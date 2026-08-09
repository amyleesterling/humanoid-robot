"""Fail-closed validation for HR-V0-ACT-AC-CORD-P0.1."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "ac-input" / "hr-v0-actuator-ac-cord-p0.1"
WEB = ROOT / "release" / "hr-v0" / "actuator-ac-cord-p0.1" / "index.html"
RECEIVING = ROOT / "tests" / "forms" / "hr-v0-actuator-ac-cord-receiving-template-p0.1.csv"
SITE = ROOT / "tests" / "forms" / "hr-v0-actuator-ac-cord-site-fit-template-p0.1.csv"
BOM = ROOT / "bom" / "bom.csv"
CLOSURE = ROOT / "bom" / "hr-v0-bom-closure.csv"
GATES = ROOT / "requirements" / "hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release" / "hr-v0" / "release-candidate.json"
IDENTIFIER = "HR-V0-ACT-AC-CORD-P0.1"
EXPECTED = {"source-register.csv", "interface-control.csv", "selection-holds.csv", "package-status.json"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    if not OUT.is_dir() or {path.name for path in OUT.iterdir() if path.is_file()} != EXPECTED:
        errors.append("artifact membership changed")
    if not WEB.is_file() or not RECEIVING.is_file() or not SITE.is_file():
        errors.append("web or evidence form missing")
    if errors:
        print(f"{IDENTIFIER}: FAIL", file=sys.stderr)
        return 1

    sources = rows(OUT / "source-register.csv")
    controls = rows(OUT / "interface-control.csv")
    holds = rows(OUT / "selection-holds.csv")
    receiving = rows(RECEIVING)
    site = rows(SITE)
    bom = {row["item_id"]: row for row in rows(BOM)}
    closure = {row["item_id"]: row for row in rows(CLOSURE)}
    gates = {row["gate_id"]: row for row in rows(GATES)}
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))

    if len(sources) != 2 or [row["source_id"] for row in sources] != ["ACCORD-SRC-001", "ACCORD-SRC-002"]:
        errors.append("two-source register changed")
    meanwell = sources[0]
    eaton = sources[1]
    if meanwell["revision_or_date"] != "2026-04-03" or "IEC320-C14" not in meanwell["controlled_facts"] or "95 A" not in meanwell["controlled_facts"] or "-V connected to AC FG" not in meanwell["controlled_facts"]:
        errors.append("Mean Well identity/current/inrush/FG facts changed")
    if eaton["product"] != "P006-006" or "10 A" not in eaton["controlled_facts"] or "18 AWG" not in eaton["controlled_facts"] or "UL Listed" not in eaton["controlled_facts"] or "cUL Listed" not in eaton["controlled_facts"]:
        errors.append("Eaton catalog facts changed")
    if len(controls) != 18 or [row["control_id"] for row in controls] != [f"ACC-{index:03d}" for index in range(1, 19)]:
        errors.append("18-control identity changed")
    if any(row["state"] != "CATALOG CANDIDATE - APPLICATION HOLD" for row in controls):
        errors.append("interface control promoted")
    screen = next((row for row in controls if row["control_id"] == "ACC-015"), {})
    if "0.300" not in screen.get("candidate_value", "") or "not an ampacity" not in screen.get("release_boundary", ""):
        errors.append("nominal-current screen or boundary changed")
    if len(holds) != 12 or any(row["state"] != "OPEN" or row["named_owner"] != "SELECTION REQUIRED" or row["evidence_uri"] != "NOT EXECUTED" for row in holds):
        errors.append("twelve holds must remain open and unassigned")
    if len(receiving) != 16 or len(site) != 14:
        errors.append("receiving/site record counts changed")
    for record in receiving + site:
        if record["result"] != "NOT EXECUTED" or record["authorization"] != "NOT AUTHORIZED" or record["disposition"] != "NOT EXECUTED":
            errors.append(f"{record['record_id']}: evidence record promoted")

    item = bom.get("BOM-063", {})
    if item.get("manufacturer") != "Eaton Tripp Lite series" or item.get("manufacturer_part_number") != "P006-006; NEMA 5-15P to IEC C13; 10 A 125 VAC; 18 AWG; 6 ft; black" or item.get("quantity") != "1":
        errors.append("BOM-063 exact catalog identity changed")
    close = closure.get("BOM-063", {})
    if close.get("closure_class") != "exact_candidate_hold" or close.get("application_state") != "SELECTION REQUIRED" or close.get("allowed_action") != "HOLD":
        errors.append("BOM-063 closure must remain exact-candidate hold")
    if any(gates.get(gate_id, {}).get("status") != "partial" for gate_id in ("EG-001", "EG-003", "EG-016", "EG-019")):
        errors.append("site/BOM/PE/mains gates must remain partial")
    for token in ("docs/hr-v0-actuator-ac-cord-p0.1.md", "electrical/ac-input/hr-v0-actuator-ac-cord-p0.1/", "tools/check_hr_v0_actuator_ac_cord_p01.py"):
        if token not in gates["EG-001"]["evidence_location"]:
            errors.append(f"EG-001 evidence route omits {token}")
    electrical_product = next((item for item in candidate["current_products"] if item["domain"] == "electrical"), None)
    bom_product = next((item for item in candidate["current_products"] if item["domain"] == "bill_of_materials"), None)
    if not electrical_product or IDENTIFIER not in electrical_product["supporting_identifiers"] or not bom_product or IDENTIFIER not in bom_product["supporting_identifiers"]:
        errors.append("release candidate does not bind the held AC-cord product")

    expected_status = {
        "identifier": IDENTIFIER,
        "date": "2026-08-09",
        "build_location_basis": "Boston, Massachusetts, USA",
        "source_candidate": "MEAN WELL GST280A12-C6P",
        "cord_candidate": "Eaton Tripp Lite series P006-006",
        "interface_control_count": 18,
        "open_hold_count": 12,
        "receiving_record_count": 16,
        "site_fit_record_count": 14,
        "catalog_candidate_identified": True,
        "application_selected": False,
        "purchase_authorized": False,
        "received_evidence_present": False,
        "site_evidence_present": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION",
    }
    if status != expected_status:
        errors.append("package status changed")
    page = WEB.read_text(encoding="utf-8")
    for token in (IDENTIFIER, "P006-006", "95 A", "0.300", "Twelve open holds", "font:clamp(16px", "not approved for purchase, connection, or use"):
        if token not in page:
            errors.append(f"interactive guide omits {token}")
    if errors:
        print(f"{IDENTIFIER}: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"{IDENTIFIER}: PASS")
    print("P006-006 exact catalog candidate / 18 controls / 12 open holds / 30 unexecuted physical records")
    print("BOM-063 exact-candidate hold; EG-001/003/016/019 partial; no purchase, connection or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
