"""Check the R138 critical-IC native KiCad metadata correction."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pcbnew

from hr_v0_watchdog_footprint_metadata import FOOTPRINT_METADATA, WARNING


ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OUT = ROOT / "electrical" / "manufacturing" / "hr-v0-watchdog-footprint-metadata-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-footprint-metadata-p0.1" / "index.html"


def main() -> int:
    failures = []
    board = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if board.GetTitleBlock().GetRevision() != "PCB-P0.8 / Electrical V3-P1.14":
        failures.append("native board revision is not PCB-P0.8 / Electrical V3-P1.14")
    for ref, expected in FOOTPRINT_METADATA.items():
        if ref not in fps:
            failures.append(f"missing footprint {ref}")
            continue
        for field, value in expected.items():
            if not fps[ref].HasField(field):
                failures.append(f"{ref} missing {field}")
            elif fps[ref].GetField(field).GetText() != value:
                failures.append(f"{ref} {field} mismatch")
            elif fps[ref].GetField(field).IsVisible():
                failures.append(f"{ref} {field} must be hidden")
    parity = json.loads((OUT / "geometry-topology-parity.json").read_text(encoding="utf-8"))
    if not parity.get("geometry_topology_equal") or parity.get("baseline_snapshot_sha256") != parity.get("current_snapshot_sha256"):
        failures.append("P0.7/P0.8 native geometry/topology parity failed")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if status.get("identifier") != "HR-V0-WD-IC-META-P0.1" or status.get("critical_references") != 4 or status.get("native_fields") != 36:
        failures.append("package status identity/count mismatch")
    for key in ("copper_changed", "placement_changed", "nets_changed", "assembly_process_selected", "fabrication_authorized", "energization_authorized", "safety_credit"):
        if status.get(key) is not False:
            failures.append(f"{key} must be false")
    with (OUT / "footprint-metadata-register.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 36 or any(row["match"] != "TRUE" or row["field_visible"] != "FALSE" for row in rows):
        failures.append("native-field register does not contain 36 hidden exact matches")
    with (OUT / "source-register.csv").open(newline="", encoding="utf-8") as handle:
        sources = list(csv.DictReader(handle))
    if len(sources) != 3 or any(not row["official_url"].startswith("https://") for row in sources):
        failures.append("primary-source register mismatch")
    page = WEB.read_text(encoding="utf-8")
    for token in (WARNING, "SELECTION REQUIRED", "geometry/topology digest equal: TRUE", "font:16px"):
        if token not in page:
            failures.append(f"interactive guide missing {token}")
    if failures:
        print("HR-V0-WD-IC-META-P0.1 FAIL")
        for failure in failures:
            print(" -", failure)
        return 1
    print("HR-V0-WD-IC-META-P0.1 PASS")
    print("  4 critical references; 36 exact hidden native fields")
    print("  P0.7/P0.8 footprint/pad/net/copper/outline/zone fingerprint identical")
    print("  assembly process, fabrication, energization and safety credit remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
