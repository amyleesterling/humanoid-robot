from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/dynamic-event-ain-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-dynamic-event-ain-p0.1"
FORM = ROOT / "tests/forms/hr-v0-dynamic-event-ain-receiving-template-p0.1.csv"
WEB = ROOT / "release/hr-v0/dynamic-event-ain-p0.1/index.html"
WARNING = "PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected = {"candidate-bom.csv", "channel-map.csv", "connector-map.csv", "loading-design-inputs.csv", "package-status.json", "selection-holds.csv", "source-register.csv", "timing-budget-inputs.csv"}
    need(errors, PKG.is_dir() and {p.name for p in PKG.iterdir()} == expected, "package membership changed")
    bom = rows(PKG / "candidate-bom.csv")
    evm = next((r for r in bom if r["item_id"] == "TE-009B"), {})
    need(errors, evm.get("manufacturer") == "Texas Instruments" and evm.get("part_number") == "AMC3330EVM" and evm.get("quantity") == "7", "seven-EVM candidate changed")
    need(errors, all(r["procurement_state"] == "NOT AUTHORIZED" for r in bom), "procurement authority introduced")
    channels = rows(PKG / "channel-map.csv")
    need(errors, len(channels) == 7, "expected seven channels")
    need(errors, [r["t7_pair"] for r in channels] == ["AIN0-AIN1", "AIN2-AIN3", "AIN4-AIN5", "AIN6-AIN7", "AIN8-AIN9", "AIN10-AIN11", "AIN12-AIN13"], "differential-pair allocation changed")
    need(errors, all("PROHIBITED" in r["connection_state"] for r in channels), "field connection released")
    connectors = rows(PKG / "connector-map.csv")
    need(errors, len(connectors) == 28, "expected four connector records per EVM")
    need(errors, all(any(r["terminal"] == t for r in connectors) for t in ("J2.1", "J2.2/J2.3", "J3.2/J3.1", "J1.1/J1.2")), "EVM terminal family incomplete")
    loads = rows(PKG / "loading-design-inputs.csv")
    need(errors, len(loads) == 6 and loads[-1]["value"] == "SELECTION REQUIRED", "loading inputs or hold changed")
    timing = rows(PKG / "timing-budget-inputs.csv")
    need(errors, len(timing) == 6 and next(r for r in timing if r["input_id"] == "ATI-003")["state"] == "DERIVED SCREEN ONLY", "scan-rate screen gained acceptance")
    holds = rows(PKG / "selection-holds.csv")
    need(errors, len(holds) == 15 and all(r["warning"] == WARNING for r in holds), "hold set changed")
    sources = rows(PKG / "source-register.csv")
    need(errors, len(sources) == 7 and {r["manufacturer"] for r in sources} == {"Texas Instruments", "LabJack"}, "primary source set changed")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(errors, status.get("identifier") == "HR-V0-DYN-EVENT-AIN-P0.1" and status.get("scan_address_count") == 8, "package status changed")
    for key in ("authorized_procurement_count", "authorized_connection_count", "authorized_powered_run_count", "executed_physical_run_count"):
        need(errors, status.get(key) == 0, f"{key} is not zero")
    refs = [
        (ROOT / "references/ti/amc3330-r177/amc3330-sbasa34b.pdf", 1580557, "1AC6B81FFB52DFDBDE49C86CA31F3A0BEAA7D52BFF60547834F34EC75A58B288"),
        (ROOT / "references/ti/amc3330-r177/amc3301-amc3302-amc3330-evm-sbau330c.pdf", 683693, "75F5FC38B39B2C60C2D5D363812AFEBFA66EE78C523358F63221A48DAF8552D1"),
    ]
    for path, size, digest in refs:
        need(errors, path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest().upper() == digest, f"controlled TI source changed: {path.name}")
    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(errors, len(sheets) == 6, "expected root plus five native sheets")
    erc = (ECAD / "validation/hr-v0-dynamic-event-ain-p0.1-erc.rpt").read_text(encoding="utf-8")
    need(errors, "0  Errors 0  Warnings" in erc, "native ERC is not 0/0")
    need(errors, len(list((ECAD / "output").glob("event-ain-*.svg"))) == 5, "expected five child SVG exports")
    schedule = rows(ECAD / "connector-schedule.csv")
    capture_functions = {r["function"] for r in schedule if r["reference"] == "DAQCFG1"}
    need(errors, capture_functions == {"AIN8-9", "AIN10-11", "AIN12-13", "FIO_STATE"}, "capture-sheet pair labels changed")
    received = rows(FORM)
    need(errors, len(received) == 4 and all(r["result"] == "NOT EXECUTED" for r in received), "receiving evidence invented")
    html = WEB.read_text(encoding="utf-8")
    for token in ("Lower loading. Same hard stop.", "font:16px", "font-size:16px", "not certified for high-voltage operation", "sequential", "SELECTION REQUIRED"):
        need(errors, token in html, f"web guide missing {token!r}")
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    product = next((item for item in release["current_products"] if item.get("identifier") == "HR-V0-DYN-EVENT-AIN-P0.1"), None)
    need(errors, product is not None, "release candidate lacks R177 event AIN product")
    if product:
        need(errors, "all_field_connections_prohibited" in product["release_state"] and "zero_safety_credit" in product["release_state"], "release state is not fail-closed")
    gates = {r["gate_id"]: r for r in rows(ROOT / "requirements/hr-v0-energization-gates.csv")}
    need(errors, gates["EG-025"]["status"] == "open" and "hr-v0-gate-evidence-supplement-r177.csv" in gates["EG-025"]["evidence_location"], "EG-025 state/evidence changed")
    need(errors, gates["EG-026"]["status"] == "partial" and "hr-v0-gate-evidence-supplement-r177.csv" in gates["EG-026"]["evidence_location"], "EG-026 state/evidence changed")
    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))
    print("HR-V0 dynamic-event AIN P0.1 check passed: 7 AMC3330EVM candidates, 7 T7 differential pairs, native ERC 0/0")
    print("15 holds open; zero procurement, connection, powered-run, physical-result, release or safety authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
