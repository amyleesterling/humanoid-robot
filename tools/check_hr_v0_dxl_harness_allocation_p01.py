"""Validate R153 DXL harness allocation without granting work authority."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-harness-allocation-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SOURCE_MAP = {
    "bom/bom.csv": ROOT / "bom" / "bom.csv",
    "bom/hr-v0-bom-closure.csv": ROOT / "bom" / "hr-v0-bom-closure.csv",
    "electrical/kicad/project-button-v3/connector-schedule.csv": ROOT / "electrical" / "kicad" / "project-button-v3" / "connector-schedule.csv",
    "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv": ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "connector-schedule.csv",
    "firmware/supervisor/actuator-config.json": ROOT / "firmware" / "supervisor" / "actuator-config.json",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    required = {
        "README.md", "index.html", "package-status.json", "file-manifest.csv",
        "primary-source-register.csv", "harness-allocation.csv", "connector-bom-parity.csv",
        "controller-cable-pinmap.csv", "manufacturer-questions.csv", "acceptance-matrix.csv",
        "residual-holds.csv", "receiving-template.csv", "current-qualification-template.csv",
    }
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(required == actual, f"package membership mismatch: {sorted(required ^ actual)}")
    need(not any(path.suffix.lower() in {".zip", ".7z", ".rar"} for path in OUT.rglob("*")), "archive must not exist")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-HARNESS-ALLOC-P0.1" and status.get("round") == "R153", "identity/round mismatch")
    counts = {
        "harness_allocations": 4, "integrated_factory_branch_cables": 3, "custom_controller_cables": 1,
        "loose_ehr3_housings": 2, "loose_seh_contacts": 4, "primary_sources": 6,
        "manufacturer_questions": 8, "acceptance_rows": 10, "residual_holds": 14,
        "duplicate_branch_housings_removed": 6, "duplicate_branch_contacts_removed": 18,
    }
    for key, value in counts.items():
        need(status.get(key) == value, f"{key} changed")
    need(status.get("bom086_separate_purchase_required") is False, "BOM-086 must remain integrated")
    need(status.get("controller_vdd_conductor_allowed") is False, "controller VDD conductor must remain prohibited")
    for key in (
        "connector_current_conflict_closed", "harness_fully_selected", "manufacturer_contacted",
        "manufacturer_response_received", "procurement_authorized", "fabrication_authorized",
        "assembly_authorized", "physical_article_exists", "connection_authorized",
        "powered_test_authorized", "motion_authorized", "energization_authorized", "safety_credit",
    ):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")
    need(set(status.get("source_hashes", {})) == set(SOURCE_MAP), "source hash membership mismatch")
    for key, path in SOURCE_MAP.items():
        need(status.get("source_hashes", {}).get(key) == sha256(path), f"source hash mismatch: {key}")

    bom = {row["item_id"]: row for row in read_csv(ROOT / "bom" / "bom.csv")}
    need(len(bom) == 86 and "BOM-086" in bom, "system BOM must contain 86 unique groups including BOM-086")
    need(bom["BOM-054"]["quantity"] == "2" and "controller cable" in bom["BOM-054"]["selection_basis"].lower(), "BOM-054 allocation mismatch")
    need(bom["BOM-055"]["quantity"] == "4" and "controller-cable" in bom["BOM-055"]["selection_basis"].lower(), "BOM-055 allocation mismatch")
    need(bom["BOM-061"]["quantity"] == "1" and "cavity 2 empty at both ends" in bom["BOM-061"]["manufacturer_part_number"], "BOM-061 controller-only allocation mismatch")
    need(bom["BOM-086"]["quantity"] == "3" and bom["BOM-086"]["baseline_status"] == "integrated_candidate", "BOM-086 integrated quantity/status mismatch")
    need("903-0249-000" in bom["BOM-086"]["manufacturer_part_number"] and "no separate purchase" in bom["BOM-086"]["selection_basis"].lower(), "BOM-086 source/purchase boundary missing")
    closure = {row["item_id"]: row for row in read_csv(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    need(closure.get("BOM-086", {}).get("closure_class") == "integrated_no_separate_purchase", "BOM-086 closure class mismatch")
    need(closure.get("BOM-086", {}).get("allowed_action") == "INTEGRATED NO SEPARATE PURCHASE", "BOM-086 allowed action mismatch")

    allocations = read_csv(OUT / "harness-allocation.csv")
    need(len(allocations) == 4 and {row["harness_id"] for row in allocations} == {"HAR-CTRL", "HAR-J1", "HAR-J2", "HAR-G1"}, "harness allocation membership mismatch")
    ctrl = next(row for row in allocations if row["harness_id"] == "HAR-CTRL")
    need(ctrl["conductor_count"] == "2" and ctrl["cavity_2"].startswith("EMPTY") and ctrl["separate_purchase"].startswith("YES"), "controller harness boundary mismatch")
    branches = [row for row in allocations if row["harness_id"] != "HAR-CTRL"]
    need(all(row["nominal_length_mm"] == "180" and row["conductor_count"] == "3" and row["separate_purchase"] == "NO" for row in branches), "integrated branch cable allocation mismatch")

    parity = read_csv(OUT / "connector-bom-parity.csv")
    need(len(parity) == 5 and all(row["result"] == "PASS" for row in parity), "connector BOM parity must contain five passes")
    pinmap = read_csv(OUT / "controller-cable-pinmap.csv")
    need(len(pinmap) == 6, "controller pin map count changed")
    cavity2 = [row for row in pinmap if row["cavity"] == "2"]
    need(len(cavity2) == 2 and all(row["population"] == "EMPTY" and row["destination"] == "NONE" for row in cavity2), "both controller cavity-2 positions must remain empty")
    need(any("NO_NET_NO_COPPER" in row["acceptance"] for row in cavity2), "JC1.2 no-copper boundary missing")

    system_terms = [row for row in read_csv(SOURCE_MAP["electrical/kicad/project-button-v3/connector-schedule.csv"]) if row["reference"] == "INJ1"]
    native_terms = read_csv(SOURCE_MAP["electrical/kicad/hr-v0-dxl-star/connector-schedule.csv"])
    ctrl2 = next((row for row in system_terms if row["terminal"] == "CTRL:2"), {})
    jc12 = next((row for row in native_terms if row["reference"] == "JC1" and row["terminal"] == "2"), {})
    need(ctrl2.get("net") == "INTENTIONALLY_UNUSED_U2D2_VDD" and jc12.get("net") == "INTENTIONALLY_UNUSED_U2D2_VDD", "system/native controller-VDD omission changed")

    sources = read_csv(OUT / "primary-source-register.csv")
    need(len(sources) == 6 and all(row["url"].startswith("https://") and "2026-08-09" in row["revision_or_access"] for row in sources), "primary source register incomplete")
    need(any("3 A AC/DC" in row["controlled_fact"] and "21 AWG" in row["not_proved"] for row in sources), "JST rating/21-AWG boundary missing")
    need(any("4.4 A" in row["controlled_fact"] for row in sources), "XM540 4.4 A endpoint missing")
    questions = read_csv(OUT / "manufacturer-questions.csv")
    need(len(questions) == 8 and all(row["status"] == "NOT SENT" and not row["response_evidence"] for row in questions), "manufacturer questions must remain unsent/unanswered")
    acceptance = read_csv(OUT / "acceptance-matrix.csv")
    need(len(acceptance) == 10 and all(row["result"] == "OPEN" and not row["approver"] and not row["approval_date"] for row in acceptance), "acceptance matrix must remain open and unsigned")
    holds = read_csv(OUT / "residual-holds.csv")
    need(len(holds) == 14 and len({row["hold_id"] for row in holds}) == 14 and all(row["status"] == "OPEN" for row in holds), "fourteen unique holds must remain open")

    receiving = read_csv(OUT / "receiving-template.csv")
    need(len(receiving) == 4 and all(row["result"] == "NOT EXECUTED" and not row["approver"] for row in receiving), "receiving rows must remain unexecuted")
    current = read_csv(OUT / "current-qualification-template.csv")
    need(len(current) == 7 and all(row["result"] == "NOT EXECUTED" and row["acceptance_basis"] == "SELECTION REQUIRED" and not row["raw_data_uri"] for row in current), "current qualification rows must remain unexecuted")
    need({row["current_limit_raw"] for row in current} == {"200", "300", "400", "600", "800"}, "guarded current candidates changed")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", "Three cables were already in the boxes", "Fourteen holds remain open", "0</b>work authorizations", "JST EH 3 A rating versus the XM540 4.4 A stall endpoint"):
        need(token in page, f"guide token missing: {token}")
    need(page.count("DXL-HAR-HOLD-") == 14, "guide does not display all fourteen holds")
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "BOM-086" in readme and "does not close the JST EH 3 A" in readme, "README boundary missing")

    manifest = read_csv(OUT / "file-manifest.csv")
    expected_manifest = actual - {"file-manifest.csv"}
    need({row["path"] for row in manifest} == expected_manifest, "manifest membership mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path) and int(row["bytes"]) == path.stat().st_size, f"manifest identity mismatch: {row['path']}")

    if failures:
        print("HR-V0-DXL-HARNESS-ALLOC-P0.1 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-HARNESS-ALLOC-P0.1 PASS")
    print("  3 integrated branch cables / 1 custom controller cable / 2 loose housings / 4 loose contacts")
    print("  14 holds OPEN; connector-current conflict remains open; no external work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
