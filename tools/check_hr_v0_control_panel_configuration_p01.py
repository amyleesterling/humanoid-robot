#!/usr/bin/env python3
"""Validate the fail-closed HR-V0 control-panel current configuration overlay."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release/hr-v0/control-panel-configuration-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, "
    "CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    expected = {
        "configuration-binding.csv", "identity-reconciliation.csv", "wire-endpoint-parity.csv",
        "current-stationary-wire-schedule.csv", "current-installation-bom.csv", "current-backplate-layout.csv",
        "board-envelope-parity.csv", "closure-register.csv", "authority-boundary.csv", "package-status.json", "index.html",
    }
    need(OUT.is_dir(), "package directory missing")
    if OUT.is_dir():
        need({p.name for p in OUT.iterdir() if p.is_file()} == expected, "package file set changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-CP-CONFIG-P0.1" and status.get("round") == "R220", "identity changed")
    for key, value in {
        "configuration_bindings": 8, "identity_records": 5, "panel_endpoint_records": 66,
        "endpoint_mismatches": 0, "current_bom_records": 34, "layout_records": 26,
        "board_envelope_records": 2, "open_holds": 12,
    }.items():
        need(status.get(key) == value, f"status count changed: {key}")
    for key in (
        "historical_panel_geometry_released", "supplier_packet_released", "procurement_authorized",
        "fabrication_authorized", "assembly_authorized", "connection_authorized",
        "powered_test_authorized", "motion_authorized", "energization_authorized",
    ):
        need(status.get(key) is False, f"status falsely authorizes {key}")
    need(status.get("warning") == WARNING, "status warning changed")

    bindings = rows("configuration-binding.csv")
    need(len(bindings) == 8, "binding count changed")
    for row in bindings:
        path = ROOT / row["path"]
        need(path.is_file() and digest(path) == row["sha256"], f"bound source changed: {row['record_id']}")
        need(row["warning"] == WARNING, f"binding warning missing: {row['record_id']}")
    need({r["identifier"] for r in bindings} >= {
        "HR-V0-CP-P0.6", "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE",
        "PCB-P1.0-P1.15-DIRECT", "DXL-STAR-P0.2-CARRIER-CANDIDATE", "HR-V0-CONFIG-REC-P0.3",
    }, "current binding set incomplete")

    identities = rows("identity-reconciliation.csv")
    need(len(identities) == 5, "identity record count changed")
    by_id = {r["record_id"]: r for r in identities}
    need(by_id.get("CPC-ID-03", {}).get("current_identity") == "PCB-P1.0-P1.15-DIRECT", "watchdog current identity changed")
    need(by_id.get("CPC-ID-04", {}).get("current_identity") == "DXL-STAR-P0.2-CARRIER-CANDIDATE", "DXL-star current identity changed")
    need(by_id.get("CPC-ID-05", {}).get("disposition") == "SUPPORTING VIEW ONLY", "P1.17 scope widened")
    need(all(r["physical_acceptance"] == "NOT EXECUTED" and r["warning"] == WARNING for r in identities), "identity record implies physical acceptance")

    parity = rows("wire-endpoint-parity.csv")
    need(len(parity) == 66 and len({r["wire_number"] for r in parity}) == 66, "endpoint parity coverage changed")
    need(all(r["parity"] == "EXACT MATCH" and r["physical_evidence"] == "NOT EXECUTED" and r["warning"] == WARNING for r in parity), "endpoint parity mismatch or physical claim")

    schedule = rows("current-stationary-wire-schedule.csv")
    need(len(schedule) == 66 and len({r["wire_number"] for r in schedule}) == 66, "current schedule coverage changed")
    for row in schedule:
        for field in ("conductor_part_number", "gauge", "color", "length_mm", "termination_a", "termination_b"):
            need(row[field] == "SELECTION REQUIRED", f"{row['wire_number']} invents {field}")
        need(row["configuration_identity"] == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", f"{row['wire_number']} current identity changed")
        need(row["release_state"].startswith("NOT RELEASED") and row["warning"] == WARNING, f"{row['wire_number']} release boundary weakened")

    bom = rows("current-installation-bom.csv")
    need(len(bom) == 34 and {r["item_id"] for r in bom} == {f"PAN-{i:03d}" for i in range(1, 35)}, "panel BOM coverage changed")
    by_item = {r["item_id"]: r for r in bom}
    need(by_item.get("PAN-017", {}).get("manufacturer_part_number") == "PCB-P1.0 / Electrical V3-P1.15 direct-bound", "PAN-017 stale")
    need(by_item.get("PAN-018", {}).get("manufacturer_part_number") == "DXL-STAR-P0.2-CARRIER-CANDIDATE", "PAN-018 stale")
    need(all(("HOLD" in r["physical_release"] or "NO " in r["physical_release"]) and r["warning"] == WARNING for r in bom), "BOM contains released-looking record")

    layout = rows("current-backplate-layout.csv")
    need(len(layout) == 26, "layout record count changed")
    layout_by = {r["layout_id"]: r for r in layout}
    need("PCB-P1.0" in layout_by.get("BP-012", {}).get("mounting_basis", ""), "BP-012 stale")
    need("DXL-STAR-P0.2" in layout_by.get("BP-013", {}).get("mounting_basis", ""), "BP-013 stale")
    need(all(r["warning"] == WARNING and ("HOLD" in r["release_state"] or "CANDIDATE" in r["release_state"] or "SELECTION REQUIRED" in r["release_state"]) for r in layout), "layout release boundary weakened")

    envelopes = rows("board-envelope-parity.csv")
    need({(r["reference"], r["planning_width_mm"], r["planning_height_mm"]) for r in envelopes} == {("WDPCB1", "160.000", "100.000"), ("INJ1", "100.000", "60.000")}, "board envelopes changed")
    need(all(r["received_fit"] == "NOT EXECUTED" and r["mounting_hole_release"] == "FALSE" for r in envelopes), "envelope record implies fit or holes")

    holds = rows("closure-register.csv")
    need(len(holds) == 12 and {r["hold_id"] for r in holds} == {f"CPC-HOLD-{i:02d}" for i in range(1, 13)}, "hold coverage changed")
    need(all(r["current_state"] == "OPEN" and r["accepted"] == "FALSE" and r["warning"] == WARNING for r in holds), "hold falsely closed")

    authority = rows("authority-boundary.csv")
    need(len(authority) == 7 and sum(r["permitted_by_this_package"] == "TRUE" for r in authority) == 1, "authority scope changed")

    with (ROOT / "requirements/hr-v0-energization-gates.csv").open(newline="", encoding="utf-8") as handle:
        gates = {r["gate_id"]: r for r in csv.DictReader(handle)}
    for gate in ("EG-002", "EG-003", "EG-004", "EG-018", "EG-020"):
        need(gates.get(gate, {}).get("status") == "partial", f"{gate} promoted")
        need("requirements/hr-v0-gate-evidence-supplement-r220.csv" in gates.get(gate, {}).get("evidence_location", ""), f"{gate} missing R220")

    candidate = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next((item for item in candidate.get("current_products", []) if item.get("domain") == "electrical"), {})
    need(electrical.get("control_panel_configuration") == "HR-V0-CP-CONFIG-P0.1", "release candidate lacks current panel configuration")
    need(electrical.get("control_panel_geometry_basis") == "HR-V0-CP-P0.6", "panel geometry basis changed")
    need("HR-V0-CP-CONFIG-P0.1" in electrical.get("supporting_identifiers", []), "supporting identifier missing")
    need(electrical.get("control_panel_conductor_basis") == "HR-V0-PANEL-COND-P0.1", "R221 conductor basis missing")
    need("HR-V0-PANEL-COND-P0.1" in electrical.get("supporting_identifiers", []), "R221 supporting identifier missing")
    need(electrical.get("panel_topology_candidate") == "V3-P1.18-PANEL-TOPOLOGY-CANDIDATE", "R222 topology candidate missing")
    need(electrical.get("panel_point_to_point_candidate") == "HR-V0-PANEL-P2P-P0.1", "R222 point-to-point candidate missing")
    need(electrical.get("control_panel_node_placement_candidate") == "HR-V0-PANEL-NODE-PLACEMENT-P0.1", "R223 node-placement candidate missing")
    need(electrical.get("configuration_reconciliation") == "HR-V0-CONFIG-REC-P0.4", "R223 configuration reconciliation missing")
    need(electrical.get("ecad_web_review_surface") == "HR-V0-ECAD-WEB-REVIEW-P0.1", "R224 ECAD web-review surface missing")
    need(electrical.get("identifier") == "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE", "P1.15 current identity changed")
    need(electrical.get("release_state") == "p115_current_p118_unaccepted_k1k2_32_row_parity_proved_dc_application_protection_physical_tests_and_qualified_acceptance_open", "electrical release state changed")
    need(electrical.get("contactor_application_record") == "HR-V0-K1K2-APP-P0.3", "current contactor application record missing")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (WARNING, "HR-V0-CP-CONFIG-P0.1", "font:clamp(16px", "font-size:14px", "66 / 66", "PCB-P1.0", "DXL-STAR-P0.2", "12</b>physical closure holds"):
        need(token in page, f"interactive guide missing {token}")

    if failures:
        print("HR-V0 control-panel configuration P0.1: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("HR-V0 control-panel configuration P0.1: PASS")
    print("66/66 P1.15 panel endpoints; PCB-P1.0 and DXL-STAR-P0.2 current; 12 holds open")
    print("No supplier, fabrication, wiring, connection, powered-test, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
