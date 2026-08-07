"""Fail-closed consistency checks for HR-V0-MECH-P0.3."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.3"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle: return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    data = rows(CAD / "mechanical-release-data.csv")
    interfaces = rows(CAD / "mechanical-interface-control.csv")
    components = rows(CAD / "mechanical-assembly-components.csv")
    datums = rows(OUT / "assembly-datums.csv")
    inspection = rows(ROOT / "tests" / "forms" / "hr-v0-mechanical-release-inspection-template.csv")
    closure = rows(ROOT / "tests" / "forms" / "hr-v0-robotis-interface-closure-template.csv")
    if len(data) != 24 or [r["parameter_id"] for r in data] != [f"MRD-{i:03d}" for i in range(1, 25)]: errors.append("MRD set changed")
    if len(interfaces) != 12 or [r["interface_id"] for r in interfaces] != [f"MIC-{i:03d}" for i in range(1, 13)]: errors.append("MIC set changed")
    if len(components) != 20: errors.append("assembly component count changed")
    for pid in ("MRD-008", "MRD-009", "MRD-010", "MRD-014"):
        row = next(r for r in data if r["parameter_id"] == pid)
        if row["status"] != "superseded_invalid_geometry" or row["nominal_value"] != "SUPERSEDED": errors.append(f"{pid} is not superseded")
    for pid in ("MRD-006", "MRD-011", "MRD-012", "MRD-013", "MRD-015"):
        if next(r for r in data if r["parameter_id"] == pid)["status"] != "architecture_redesign_required": errors.append(f"{pid} lost redesign hold")
    for iid in ("MIC-004", "MIC-005", "MIC-006", "MIC-007", "MIC-008", "MIC-009"):
        if next(r for r in interfaces if r["interface_id"] == iid)["current_status"] != "architecture_redesign_required": errors.append(f"{iid} lost redesign hold")
    for item in ("6", "10", "14"):
        if next(r for r in components if r["item_no"] == item)["configuration_state"] != "withdrawn_invalid_geometry": errors.append(f"assembly item {item} is not withdrawn")
    by_datum = {r["datum_id"]: r for r in datums}
    for datum in ("J1", "J2", "G1", "OMAX"):
        if any(by_datum.get(datum, {}).get(axis) for axis in ("x_mm", "y_mm", "z_mm")) or "SELECTION REQUIRED" not in by_datum.get(datum, {}).get("status", ""): errors.append(f"{datum} still looks dimensioned")
    if by_datum.get("A0", {}).get("x_mm") != "0" or by_datum.get("C0", {}).get("x_mm") != "-210": errors.append("retained base datums changed")
    if any(r.get("mechanical_revision") != REVISION or r.get("record_id") != "NOT-EXECUTED" for r in inspection): errors.append("mechanical inspection template revision/state changed")
    if len(closure) != 1 or closure[0].get("record_id") != "NOT-EXECUTED" or closure[0].get("disposition") != "NOT EXECUTED": errors.append("interface closure template looks executed")
    summary = json.loads((OUT / "mechanical-release-summary.json").read_text(encoding="utf-8"))
    if summary.get("revision") != REVISION or summary.get("release_state") != "base_coordination_only_arm_architecture_withdrawn": errors.append("summary revision/state changed")
    if "MV0-001" not in summary.get("superseded", []) or summary.get("counts", {}).get("vendor_interface_sources") != 5: errors.append("summary lacks supersession/vendor evidence")
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    mech = next((p for p in release["current_products"] if p["domain"] == "mechanical"), {})
    if mech.get("identifier") != REVISION or "no_buildable_arm_geometry" not in mech.get("release_state", ""): errors.append("release candidate does not enforce P0.3 hold")
    try:
        tree = ET.parse(OUT / "HR-V0_general-arrangement.svg")
        text = " ".join(node.text or "" for node in tree.iter() if node.tag.endswith("text"))
        for token in (REVISION, "ARM ARCHITECTURE HOLD", "44 / 160 / 160 mm chain is superseded", "NO ARM PART MAY BE QUOTED"):
            if token not in text: errors.append(f"general arrangement omits {token}")
    except ET.ParseError as exc: errors.append(f"general arrangement does not parse: {exc}")
    if errors:
        print("HR-V0 mechanical release validation: FAIL", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 mechanical release validation: PASS")
    print("Base coordination retained; 4 arm datums blank; 3 custom arm parts withdrawn; 0 fabrication releases")
    print("PRELIMINARY - NO BUILDABLE ARM GEOMETRY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__": raise SystemExit(main())
