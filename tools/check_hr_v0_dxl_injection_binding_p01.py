"""Validate R152 DXL injection allocation binding without granting work authority."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "dxl-injection-binding-p0.1"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, "
    "ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)
SOURCE_MAP = {
    "electrical/kicad/project-button-v3/connector-schedule.csv": ROOT / "electrical/kicad/project-button-v3/connector-schedule.csv",
    "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv": ROOT / "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv",
    "electrical/kicad/project-button-v3/bom.csv": ROOT / "electrical/kicad/project-button-v3/bom.csv",
    "electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pcb": ROOT / "electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pcb",
    "release/hr-v0/dxl-star-manufacturing-p0.1/package-status.json": ROOT / "release/hr-v0/dxl-star-manufacturing-p0.1/package-status.json",
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

    required = {"README.md", "index.html", "package-status.json", "file-manifest.csv", "bom-allocation-binding.csv", "allocation-parity.csv", "residual-holds.csv"}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    need(required == actual, f"package membership mismatch: {sorted(required ^ actual)}")
    need(not any(path.suffix.lower() in {".zip", ".7z", ".rar"} for path in OUT.rglob("*")), "archive must not exist")

    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    need(status.get("identifier") == "HR-V0-DXL-INJECT-BIND-P0.1" and status.get("round") == "R152", "identity/round mismatch")
    need(status.get("legacy_item") == "BOM-035" and status.get("parent_item") == "BOM-051", "BOM binding identity mismatch")
    need(status.get("parent_board") == "DXL-STAR-P0.1" and status.get("system_reference") == "INJ1", "board/system identity mismatch")
    need(status.get("parent_quantity") == 1 and status.get("implemented_branches") == 3, "parent quantity/branch count mismatch")
    need(status.get("terminal_parity_rows") == 18 and status.get("terminal_parity_failures") == 0, "terminal parity count changed")
    need(status.get("residual_holds") == 12 and status.get("separate_bom035_purchase_required") is False, "residual/allocation state changed")
    need(status.get("parent_cam_review_only") is True, "parent CAM must remain review-only")
    for key in ("supplier_selected", "supplier_contacted", "files_uploaded", "quotation_requested", "purchase_authorized", "fabrication_authorized", "assembly_authorized", "physical_article_exists", "connection_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status.get(key) is False, f"{key} must remain false")
    need(status.get("warning") == WARNING, "status warning changed")
    need(set(status.get("source_hashes", {})) == set(SOURCE_MAP), "source hash membership mismatch")
    for key, path in SOURCE_MAP.items():
        need(status.get("source_hashes", {}).get(key) == sha256(path), f"source hash mismatch: {key}")

    electrical_bom = read_csv(ROOT / "electrical/kicad/project-button-v3/bom.csv")
    inj = [row for row in electrical_bom if row["reference"] == "INJ1"]
    need(len(inj) == 1 and inj[0]["quantity"] == "1" and "DXL-STAR-P0.1" in inj[0]["value"], "Electrical V3 must contain one DXL-star INJ1")
    system_terms = [row for row in read_csv(ROOT / "electrical/kicad/project-button-v3/connector-schedule.csv") if row["reference"] == "INJ1"]
    native_terms = read_csv(ROOT / "electrical/kicad/hr-v0-dxl-star/connector-schedule.csv")
    need(len(system_terms) == 18 and len(native_terms) == 18, "source terminal count mismatch")

    parity = read_csv(OUT / "allocation-parity.csv")
    need(len(parity) == 18 and all(row["parity"] == "PASS" for row in parity), "allocation parity must contain 18 passes")
    need(len({(row["system_reference"], row["system_terminal"]) for row in parity}) == 18, "system terminal parity membership duplicates")
    need(len({(row["native_reference"], row["native_terminal"]) for row in parity}) == 18, "native terminal parity membership duplicates")
    need(all(row["system_net"] == row["native_net"] for row in parity), "system/native net parity changed")
    jc2 = next((row for row in parity if row["native_reference"] == "JC1" and row["native_terminal"] == "2"), {})
    need(jc2.get("native_net") == "INTENTIONALLY_UNUSED_U2D2_VDD" and jc2.get("system_terminal") == "CTRL:2", "JC1.2 omission parity changed")

    binding = read_csv(OUT / "bom-allocation-binding.csv")
    need(len(binding) == 1 and binding[0]["legacy_item_id"] == "BOM-035" and binding[0]["parent_item_id"] == "BOM-051", "binding row mismatch")
    need(binding[0]["disposition"] == "INTEGRATED IN PARENT - NO SEPARATE PURCHASE" and binding[0]["parent_quantity"] == "1" and binding[0]["implemented_branch_count"] == "3", "binding disposition/count mismatch")
    holds = read_csv(OUT / "residual-holds.csv")
    need(len(holds) == 12 and len({row["hold_id"] for row in holds}) == 12, "expected 12 unique residual holds")
    need(all(row["status"] == "OPEN" and row["warning"] == WARNING for row in holds), "all residual holds must remain open")

    system_bom = {row["item_id"]: row for row in read_csv(ROOT / "bom/bom.csv")}
    bom035 = system_bom.get("BOM-035", {})
    bom051 = system_bom.get("BOM-051", {})
    need(bom035.get("baseline_status") == "integrated_candidate" and bom035.get("quantity") == "1", "BOM-035 is not integrated with parent-controlled quantity")
    need("Integrated in BOM-051" in bom035.get("manufacturer_part_number", "") and "no separate item" in bom035.get("manufacturer_part_number", "").lower(), "BOM-035 integration boundary missing")
    need(bom051.get("baseline_status") == "exact_candidate_hold" and "DXL-STAR-P0.2-CARRIER-CANDIDATE" in bom051.get("manufacturer_part_number", "") and "HR-V0-DXL-STAR-MFG-P0.2" in bom051.get("manufacturer_part_number", ""), "BOM-051 current parent hold changed")
    closure = {row["item_id"]: row for row in read_csv(ROOT / "bom/hr-v0-bom-closure.csv")}
    need(closure.get("BOM-035", {}).get("closure_class") == "integrated_no_separate_purchase", "BOM-035 closure class mismatch")
    need(closure.get("BOM-035", {}).get("allowed_action") == "INTEGRATED NO SEPARATE PURCHASE", "BOM-035 allowed action mismatch")

    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    electrical = next((row for row in release["current_products"] if row["domain"] == "electrical"), {})
    bom_product = next((row for row in release["current_products"] if row["domain"] == "bill_of_materials"), {})
    need("HR-V0-DXL-INJECT-BIND-P0.1" in electrical.get("supporting_identifiers", []), "electrical release identifiers omit binding")
    need("HR-V0-DXL-INJECT-BIND-P0.1" in bom_product.get("supporting_identifiers", []), "BOM release identifiers omit binding")
    gates = {row["gate_id"]: row for row in read_csv(ROOT / "requirements/hr-v0-energization-gates.csv")}
    for gate_id in ("EG-003", "EG-004", "EG-015"):
        need(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "code{font-size:14px", "One board replaces three placeholders", "configuration correction, not a hardware release", "Twelve residual holds remain open", "0</b>work authorizations"):
        need(token in page, f"guide token missing: {token}")
    need(page.count("DXL-BIND-HOLD-") == 12, "guide does not display all twelve holds")
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "no separate purchase" in readme and "does not release BOM-051" in readme, "README boundary missing")

    manifest = read_csv(OUT / "file-manifest.csv")
    expected_manifest = actual - {"file-manifest.csv"}
    need({row["path"] for row in manifest} == expected_manifest, "manifest membership mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(row["sha256"] == sha256(path) and int(row["bytes"]) == path.stat().st_size, f"manifest identity mismatch: {row['path']}")

    if failures:
        print("HR-V0-DXL-INJECT-BIND-P0.1 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0-DXL-INJECT-BIND-P0.1 PASS")
    print("  BOM-035 integrated in BOM-051: one INJ1 board / three isolated VDD branches / 18 terminal parity rows")
    print("  12 residual holds OPEN; no separate module purchase or external work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
