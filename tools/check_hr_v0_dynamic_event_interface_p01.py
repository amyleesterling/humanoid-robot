from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "test-equipment/hr-v0/dynamic-event-interface-p0.1"
ECAD = ROOT / "electrical/kicad/hr-v0-dynamic-event-interface-p0.1"
WEB = ROOT / "release/hr-v0/dynamic-event-interface-p0.1/index.html"
FORM = ROOT / "tests/forms/hr-v0-dynamic-event-interface-receiving-template-p0.1.csv"
WARNING = "PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected = {"candidate-bom.csv", "channel-map.csv", "evm-connector-map.csv", "field-tap-risk-register.csv", "package-status.json", "selection-holds.csv", "source-register.csv", "timing-budget-inputs.csv"}
    need(errors, PKG.is_dir(), "package directory missing")
    if PKG.is_dir():
        need(errors, {path.name for path in PKG.iterdir()} == expected, "package membership changed")

    bom = read_rows(PKG / "candidate-bom.csv")
    need(errors, len(bom) == 5, "expected five equipment/interface rows")
    evm = next((row for row in bom if row["item_id"] == "TE-009A"), {})
    need(errors, evm.get("manufacturer") == "Texas Instruments" and evm.get("part_number") == "ISO1212EVM" and evm.get("quantity") == "2", "exact two-EVM candidate changed")
    need(errors, all(row["procurement_state"] == "NOT AUTHORIZED" for row in bom), "procurement authority introduced")

    channels = read_rows(PKG / "channel-map.csv")
    need(errors, len(channels) == 8, "expected FIO0-FIO7 allocation")
    need(errors, [row["t7_terminal"] for row in channels] == [f"FIO{i}" for i in range(8)], "FIO allocation changed")
    need(errors, channels[0]["requirement"] == "DCH-001", "common trigger mapping changed")
    need(errors, {row["requirement"] for row in channels[1:]} == {"DCH-014", "DCH-X01", "DCH-X02", "DCH-008", "DCH-009", "DCH-010", "DCH-011"}, "event requirement coverage changed")
    need(errors, all("prohibited" in row["hold"].lower() for row in channels[1:]), "field tap became connectable")

    evm_map = read_rows(PKG / "evm-connector-map.csv")
    need(errors, len(evm_map) == 8, "expected eight EVM channel rows")
    need(errors, [row["field_terminal"] for row in evm_map[:4]] == ["J4-9", "J4-8", "J4-7", "J4-6"], "EVM A J4 fast pins changed")
    need(errors, [row["logic_terminal"] for row in evm_map[:4]] == ["J2-2", "J2-4", "J2-6", "J2-8"], "EVM A J2 output pins changed")
    need(errors, evm_map[-1]["configuration"] == "unused fast channel / DNP", "EVM B spare channel changed")

    risks = read_rows(PKG / "field-tap-risk-register.csv")
    need(errors, len(risks) == 7, "expected seven field-tap risks")
    need(errors, {row["project_net_candidate"] for row in risks} == {"SR1_S12", "SR1_START_RETURN", "ARM_AFTER_S2", "K1_A1", "K2_A1", "EDM_K1_OUT", "SRA1_START_RETURN"}, "project field-net set changed")

    holds = read_rows(PKG / "selection-holds.csv")
    need(errors, len(holds) == 15, "expected fifteen open holds")
    need(errors, all(row["warning"] == WARNING for row in holds), "hold warning changed")
    sources = read_rows(PKG / "source-register.csv")
    need(errors, len(sources) == 7, "expected seven primary sources")
    need(errors, {row["manufacturer"] for row in sources} == {"Texas Instruments", "LabJack"}, "source manufacturer set changed")
    need(errors, all(row["official_locator"].startswith("https://") for row in sources), "non-HTTPS source found")

    timing = read_rows(PKG / "timing-budget-inputs.csv")
    need(errors, len(timing) == 7, "expected seven timing inputs")
    need(errors, next(row for row in timing if row["input_id"] == "DTI-002")["state"] == "DERIVED SCREEN ONLY", "100 us screen gained acceptance")

    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(errors, status.get("identifier") == "HR-V0-DYN-EVENT-IF-P0.1", "package identifier changed")
    need(errors, status.get("field_event_count") == 7 and status.get("open_hold_count") == 15, "status counts changed")
    for key in ("authorized_procurement_count", "authorized_connection_count", "authorized_powered_run_count", "executed_physical_run_count"):
        need(errors, status.get(key) == 0, f"{key} is not zero")
    need(errors, status.get("safety_function_credit") == "ZERO" and status.get("release_effect") == "NONE", "safety/release boundary changed")

    source_pdf = ROOT / "references/ti/iso1212evm-r176/sllu254a.pdf"
    source_record = json.loads((ROOT / "references/ti/iso1212evm-r176/source-record.json").read_text(encoding="utf-8"))
    need(errors, source_pdf.stat().st_size == 648488, "TI guide byte count changed")
    need(errors, hashlib.sha256(source_pdf.read_bytes()).hexdigest().upper() == "8F7F03908AFF49C2BA7C6BEC378D121A1EDD75AE52E5FEE0F4490F256BB60BC5", "TI guide hash changed")
    need(errors, source_record.get("revision") == "SLLU254A" and source_record.get("sha256") == "8F7F03908AFF49C2BA7C6BEC378D121A1EDD75AE52E5FEE0F4490F256BB60BC5", "TI source record changed")

    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(errors, len(sheets) == 5, "expected root plus four native KiCad child sheets")
    erc = (ECAD / "validation/hr-v0-dynamic-event-interface-p0.1-erc.rpt").read_text(encoding="utf-8")
    need(errors, "0  Errors 0  Warnings" in erc, "native KiCad ERC is not 0/0")
    need(errors, len(list((ECAD / "output").glob("event-interface-*.svg"))) == 4, "expected four readable child SVG exports")
    connector = read_rows(ECAD / "connector-schedule.csv")
    need(errors, len(connector) == 51, "connector schedule row count changed")
    expected_db37 = {"DB37-27", "DB37-1", "DB37-6", "DB37-24", "DB37-5", "DB37-23", "DB37-4", "DB37-22", "DB37-3", "DB37-21"}
    need(errors, {row["terminal"] for row in connector if row["reference"] == "DAQ1"} == expected_db37, "DAQ1 DB37 set changed")

    receiving = read_rows(FORM)
    need(errors, len(receiving) == 4, "expected four receiving rows")
    need(errors, all(row["result"] == "NOT EXECUTED" and row["reviewer"] == "SELECTION REQUIRED" for row in receiving), "receiving evidence invented")
    for row in receiving:
        for field in ("serial_or_lot", "received_identity", "hardware_revision", "power_off_continuity", "evidence_hash"):
            need(errors, row[field] == "", f"{row['record_id']} has invented {field}")

    html = WEB.read_text(encoding="utf-8")
    for token in ("Seven events. One clock.", "font:16px", "font-size:16px", "2.25 mA", "connection prohibited", "ZERO SAFETY CREDIT", "event-interface-1.svg"):
        need(errors, token in html, f"web guide missing {token!r}")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    product = next((item for item in release["current_products"] if item.get("identifier") == "HR-V0-DYN-EVENT-IF-P0.1"), None)
    need(errors, product is not None, "release candidate lacks R176 event interface")
    if product:
        need(errors, "connection_prohibited" in product["release_state"] and "zero_safety_credit" in product["release_state"], "release state is not fail-closed")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 dynamic-event interface P0.1 check passed: 2 EVMs, 7 field events, FIO0-FIO7 common-word capture, native ERC 0/0")
    print("15 holds open; zero procurement, connection, powered-run, physical-result, release or safety authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
