"""Fail-closed consistency checks for HR-V0-MECH-P0.4."""

from __future__ import annotations

import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.4"
ARM_REVISION = "HR-V0-ARM-ARCH-P0.5"


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
    expected_parameters = {
        "MRD-006": ("500", "integrated_candidate"),
        "MRD-008": ("X=0; Y=81.025", "integrated_candidate"),
        "MRD-009": ("202.55", "integrated_candidate"),
        "MRD-010": ("129.05", "integrated_candidate"),
        "MRD-011": ("20-2040 vertical 100 mm upper and 50 mm forearm members with MV0-C01/C04 adapters", "integrated_candidate"),
        "MRD-012": ("6061-T651 candidate; 9.525 nominal", "candidate_material_hold"),
        "MRD-013": ("A00 through A07 exact candidate schedule", "exact_candidate_hold"),
        "MRD-014": ("48 x 80 x 9.525", "integrated_candidate"),
        "MRD-015": ("81.025", "integrated_candidate"),
        "MRD-021": ("15 to 120", "candidate_limit"),
    }
    for pid, expected in expected_parameters.items():
        row = next(r for r in data if r["parameter_id"] == pid)
        if (row["nominal_value"], row["status"]) != expected: errors.append(f"{pid} integrated candidate changed")
    for iid in ("MIC-004", "MIC-005", "MIC-006", "MIC-007", "MIC-008", "MIC-009"):
        row = next(r for r in interfaces if r["interface_id"] == iid)
        if row["current_status"] != "exact_candidate_hold" or "SELECTION REQUIRED" not in row["fastener_boundary"]: errors.append(f"{iid} lost exact-candidate/release hold")
    for item in ("6", "10", "14"):
        if next(r for r in components if r["item_no"] == item)["configuration_state"] != "exact_candidate_hold": errors.append(f"assembly item {item} lost exact-candidate hold")
    by_datum = {r["datum_id"]: r for r in datums}
    expected_datums = {
        "J1": ("-210", "81.025", "500"),
        "J2": ("-210", "283.575", "500"),
        "G1": ("-210", "412.625", "500"),
        "OMAX": ("-210", "441.025", "500"),
    }
    for datum, expected in expected_datums.items():
        row = by_datum.get(datum, {})
        if tuple(row.get(axis) for axis in ("x_mm", "y_mm", "z_mm")) != expected: errors.append(f"{datum} integrated datum changed")
    if by_datum.get("A0", {}).get("x_mm") != "0" or by_datum.get("C0", {}).get("x_mm") != "-210": errors.append("retained base datums changed")
    if any(r.get("mechanical_revision") != REVISION or r.get("record_id") != "NOT-EXECUTED" for r in inspection): errors.append("mechanical inspection template revision/state changed")
    if len(closure) != 1 or closure[0].get("record_id") != "NOT-EXECUTED" or closure[0].get("disposition") != "NOT EXECUTED": errors.append("interface closure template looks executed")
    summary = json.loads((OUT / "mechanical-release-summary.json").read_text(encoding="utf-8"))
    if summary.get("revision") != REVISION or summary.get("arm_revision") != ARM_REVISION or summary.get("release_state") != "integrated_exact_coordinate_candidate_not_released_for_fabrication_or_energization": errors.append("summary revision/state changed")
    if summary.get("integrated_interface_ids") != [f"A0{i}" for i in range(8)] or summary.get("arm_transform_count") != 8 or summary.get("arm_sample_count") != 40001 or summary.get("first_nominal_collision_j2_deg") != 122.0: errors.append("summary lacks integrated arm evidence")
    if "MV0-001" not in summary.get("superseded", []) or summary.get("counts", {}).get("vendor_interface_sources") != 5: errors.append("summary lacks supersession/vendor evidence")
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    mech = next((p for p in release["current_products"] if p["domain"] == "mechanical"), {})
    if mech.get("identifier") != REVISION or ARM_REVISION not in mech.get("supporting_identifiers", []) or mech.get("release_state") != "integrated_exact_coordinate_candidate_not_released_for_fabrication_or_energization": errors.append("release candidate does not enforce the current P0.4 hold")
    try:
        tree = ET.parse(OUT / "HR-V0_general-arrangement.svg")
        text = " ".join(node.text or "" for node in tree.iter() if node.tag.endswith("text"))
        for token in (REVISION, "ARM RELEASE HOLD", "A00-A07 SOURCE GEOMETRY CLOSED AS A CANDIDATE", "40,001 sampled J1/J2 poses", "NO PART OR ASSEMBLY IS RELEASED"):
            if token not in text: errors.append(f"general arrangement omits {token}")
    except ET.ParseError as exc: errors.append(f"general arrangement does not parse: {exc}")
    if errors:
        print("HR-V0 mechanical release validation: FAIL", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 mechanical release validation: PASS")
    print("Integrated A00-A07 candidate retained; 4 arm datums explicit; physical and qualified release gates remain open; 0 fabrication releases")
    print("PRELIMINARY - INTEGRATED CANDIDATE ONLY - NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__": raise SystemExit(main())
