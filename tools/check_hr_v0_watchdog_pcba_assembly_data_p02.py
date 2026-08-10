"""Validate HR-V0-WD-PCBA-DATA-P0.2 without granting work authority."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pcbnew

from hr_v0_watchdog_footprint_metadata import ASSEMBLY_IDENTITIES, BASE_IDENTITY_FIELDS, WARNING


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-pcba-assembly-data-p0.2"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcba-assembly-data-p0.2" / "index.html"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures = []
    board = pcbnew.LoadBoard(str(BOARD))
    if board.GetTitleBlock().GetRevision() != "PCB-P1.0 / Electrical V3-P1.15":
        failures.append("native board revision mismatch")
    footprints = {fp.GetReference():fp for fp in board.GetFootprints()}
    if set(ASSEMBLY_IDENTITIES) != {ref for ref in footprints if not ref.startswith("MH")}:
        failures.append("42-reference native identity membership mismatch")
    expected_common = {"AlternatePolicy":"NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION","AssemblyProcessState":"SELECTION REQUIRED","FabricationStatus":WARNING}
    for ref, (manufacturer, mpn, description, process) in ASSEMBLY_IDENTITIES.items():
        expected = {"Manufacturer":manufacturer,"ManufacturerPartNumber":mpn,"AssemblyDescription":description,"ProcessClass":process,**expected_common}
        fp = footprints[ref]
        for field in BASE_IDENTITY_FIELDS:
            if not fp.HasField(field) or fp.GetField(field).GetText() != expected[field] or fp.GetField(field).IsVisible():
                failures.append(f"{ref} native field mismatch: {field}")
    parity = json.loads((OUT / "p0.8-p1.0-geometry-topology-parity.json").read_text(encoding="utf-8"))
    if not parity.get("geometry_topology_equal") or parity.get("baseline_snapshot_sha256") != parity.get("current_snapshot_sha256"):
        failures.append("P0.8/P1.0 structural parity failed")
    assembly = rows("assembly-parity-p0.7-to-p1.0.csv")
    if len(assembly) != 46 or any(row["overall_match"] != "TRUE" for row in assembly):
        failures.append("P0.7/P1.0 assembly parity is not 46/46")
    placements, mechanical, bom, identities = rows("assembly-placement-reference.csv"), rows("mechanical-feature-register.csv"), rows("board-assembly-bom.csv"), rows("native-identity-field-register.csv")
    if len(placements) != 42 or len(mechanical) != 4 or len(bom) != 16 or sum(int(row["quantity_per_board"]) for row in bom) != 42:
        failures.append("assembly membership/BOM counts changed")
    if len(identities) != 294 or any(row["match"] != "TRUE" or row["hidden"] != "TRUE" for row in identities):
        failures.append("native identity register is not 294/294 exact hidden matches")
    if sum(row["process_class"] == "SMD_REFLOW" for row in placements) != 38 or sum(row["process_class"] == "MANUAL_THT_POST_REFLOW" for row in placements) != 4:
        failures.append("38 SMD / 4 THT split changed")
    if any(row["assembler_transform_state"] != "SELECTION REQUIRED - DO NOT IMPORT AS MACHINE XYRS" for row in placements):
        failures.append("machine XYRS prohibition missing")
    holds = rows("assembly-data-holds.csv")
    if len(holds) != 12 or any(row["status"] != "OPEN" for row in holds):
        failures.append("twelve assembly-data holds must remain open")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-WD-PCBA-DATA-P0.2" or status.get("board") != "PCB-P1.0 / Electrical V3-P1.15" or status.get("native_identity_fields") != 294:
        failures.append("package status identity/count mismatch")
    if status.get("p0.7_assembly_parity") is not True or status.get("p0.8_geometry_topology_parity") is not True:
        failures.append("package parity flags are not true")
    if status.get("cam_exists") is not True or status.get("cam_released") is not False:
        failures.append("current quarantined CAM state is not encoded")
    for key in ("supplier_normalized_xyrs_exists","provider_selected","provider_contacted","files_uploaded","fabrication_authorized","assembly_authorized","physical_article_exists","energization_authorized","safety_credit"):
        if status.get(key) is not False:
            failures.append(f"{key} must be false")
    page = WEB.read_text(encoding="utf-8")
    for token in (WARNING,"42/42","294","16","data-filter=\"SMD_REFLOW\"","font:16px","SELECTION REQUIRED"):
        if token not in page:
            failures.append(f"interactive guide missing {token}")
    if failures:
        print("HR-V0-WD-PCBA-DATA-P0.2 FAIL")
        for failure in failures:
            print(" -", failure)
        return 1
    print("HR-V0-WD-PCBA-DATA-P0.2 PASS")
    print("  42 populated references; 294 exact hidden native fields; 16 BOM lines")
    print("  P0.7/P1.0 assembly and P0.8/P1.0 geometry/topology parity PASS")
    print("  quarantined CAM exists; supplier XYRS/release, fabrication, assembly, energization and safety credit remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
