from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-equipment" / "hr-v0" / "dynamic-instrumentation-p0.1"
WEB = ROOT / "release" / "hr-v0" / "dynamic-instrumentation-p0.1" / "index.html"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    expected = {
        "candidate-bom.csv",
        "channel-allocation.csv",
        "interface-register.csv",
        "package-status.json",
        "selection-holds.csv",
        "source-register.csv",
    }
    need(errors, OUT.is_dir(), "instrumentation package directory missing")
    if OUT.is_dir():
        need(errors, {path.name for path in OUT.iterdir()} == expected, "package membership changed")

    bom = rows("candidate-bom.csv")
    need(errors, len(bom) == 10, "expected ten instrumentation BOM rows")
    need(errors, {row["item_id"] for row in bom} == {f"TE-{index:03d}" for index in range(1, 11)}, "equipment identifiers changed")
    exact = [row for row in bom if row["selection_state"].startswith("EXACT PRODUCT CANDIDATE")]
    need(errors, len(exact) == 4, "expected four exact product candidates")
    need(errors, all(row["procurement_state"] == "NOT AUTHORIZED" for row in bom), "procurement authorization introduced")
    divider = next(row for row in bom if row["item_id"] == "TE-003")
    need(errors, divider["disposition"] == "REJECTED AS COMPLETE PRIMARY INTERFACE", "ground-referenced divider rejection lost")

    channels = rows("channel-allocation.csv")
    need(errors, len(channels) == 15, "expected fifteen R78 channel mappings")
    need(errors, {row["channel_id"] for row in channels} == {f"DCH-{index:03d}" for index in range(1, 16)}, "channel coverage changed")
    need(errors, next(row for row in channels if row["channel_id"] == "DCH-013")["primary_evidence_state"] == "DEFINED SUPPLEMENTAL", "DYNAMIXEL telemetry gained primary credit")

    interfaces = rows("interface-register.csv")
    need(errors, len(interfaces) == 8, "expected eight controlled interface boundaries")
    need(errors, all(row["direct_connection"].startswith("PROHIBITED") for row in interfaces), "an unresolved direct connection was allowed")
    event_input = next(row for row in interfaces if row["interface_id"] == "DIF-003")
    need(errors, "24 V is not a direct input" in event_input["manufacturer_fact"], "24 V T7 boundary lost")
    safety_boundary = next(row for row in interfaces if row["interface_id"] == "DIF-008")
    need(errors, "zero safety-function credit" in safety_boundary["manufacturer_fact"], "DAQ safety-credit prohibition lost")

    holds = rows("selection-holds.csv")
    need(errors, len(holds) == 15, "expected fifteen selection holds")
    need(errors, all(row["state"] == "OPEN" and row["release_effect"] == "NONE" for row in holds), "a selection hold closed or gained release effect")

    sources = rows("source-register.csv")
    need(errors, len(sources) == 8, "expected eight primary manufacturer sources")
    need(errors, all(row["accessed_on"] == "2026-08-10" for row in sources), "source access date changed")
    need(errors, all(row["locator"].startswith("https://") for row in sources), "non-HTTPS source locator found")
    need(errors, {row["manufacturer"] for row in sources} == {"LabJack", "LEM", "Teledyne Vision Solutions"}, "source manufacturer set changed")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(errors, status.get("identifier") == "HR-V0-DYN-INST-P0.1", "wrong package identifier")
    for field in ("executed_receiving_count", "executed_calibration_count", "executed_physical_run_count", "authorized_procurement_count", "authorized_connection_count", "authorized_powered_run_count"):
        need(errors, status.get(field) == 0, f"{field} is not zero")
    need(errors, status.get("release_effect") == "NONE", "package gained release effect")

    with (ROOT / "tests" / "forms" / "hr-v0-dynamic-instrumentation-receiving-template-p0.1.csv").open(encoding="utf-8", newline="") as handle:
        receiving = list(csv.DictReader(handle))
    need(errors, len(receiving) == 4, "expected four blank receiving rows")
    need(errors, all(row["status"] == "NOT EXECUTED" and row["reviewer"] == "SELECTION REQUIRED" for row in receiving), "receiving evidence was invented")
    for row in receiving:
        for field in ("serial_or_lot", "received_identity", "firmware_or_revision", "calibration_id", "calibration_due", "inspection_result", "evidence_hash"):
            need(errors, row[field] == "", f"{row['record_id']} contains invented {field}")

    gates_path = ROOT / "requirements" / "hr-v0-energization-gates.csv"
    with gates_path.open(encoding="utf-8", newline="") as handle:
        gates = {row["gate_id"]: row for row in csv.DictReader(handle)}
    need(errors, gates["EG-025"]["status"] == "open", "EG-025 must remain open")
    need(errors, gates["EG-026"]["status"] == "partial", "EG-026 must remain partial")
    for gate_id in ("EG-025", "EG-026"):
        need(errors, "dynamic-instrumentation-p0.1" in gates[gate_id]["evidence_location"], f"{gate_id} lacks instrumentation evidence path")

    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    product = next((item for item in release["current_products"] if item.get("identifier") == "HR-V0-DYN-INST-P0.1"), None)
    need(errors, product is not None, "release candidate lacks instrumentation product")
    if product:
        need(errors, product["release_state"].endswith("no_safety_credit"), "fail-closed release state changed")

    html = WEB.read_text(encoding="utf-8")
    for token in ("Measure before motion", "font:16px", "font-size:16px", "No direct 24 V connection", "15 hard holds", "NOT APPROVED"):
        need(errors, token in html, f"interactive guide missing {token!r}")
    need(errors, "font-size:" not in html.replace("font-size:clamp", "").replace("font-size:16px", ""), "unexpected fixed font size introduced")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 dynamic instrumentation P0.1 check passed: 10 equipment rows; 15 channels; 8 interfaces; 15 open holds")
    print("Four exact evaluation candidates; zero procurement, connection, physical-run or safety-function authority")
    print("PRELIMINARY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION")


if __name__ == "__main__":
    main()
