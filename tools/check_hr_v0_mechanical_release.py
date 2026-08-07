"""Fail-closed consistency checks for HR-V0-MECH-P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
OUT = CAD / "generated" / "assembly"
REVISION = "HR-V0-MECH-P0.2"
WARNING = "PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def canonical_text_sha256(path: Path) -> str:
    """Hash controlled text independent of Git's LF/CRLF checkout policy."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    data_path = CAD / "mechanical-release-data.csv"
    interface_path = CAD / "mechanical-interface-control.csv"
    component_path = CAD / "mechanical-assembly-components.csv"
    extrusion_path = ROOT / "bom" / "hr-v0-extrusion-cut-schedule.csv"
    inspection_path = ROOT / "tests" / "forms" / "hr-v0-mechanical-release-inspection-template.csv"
    svg_path = OUT / "HR-V0_general-arrangement.svg"
    datums_path = OUT / "assembly-datums.csv"
    summary_path = OUT / "mechanical-release-summary.json"
    required = [data_path, interface_path, component_path, extrusion_path, inspection_path, svg_path, datums_path, summary_path]
    for path in required:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    data = rows(data_path)
    interfaces = rows(interface_path)
    components = rows(component_path)
    extrusions = rows(extrusion_path)
    inspection = rows(inspection_path)
    datums = rows(datums_path)
    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    if len(data) != 24 or [row["parameter_id"] for row in data] != [f"MRD-{index:03d}" for index in range(1, 25)]:
        errors.append("mechanical release data must contain ordered MRD-001 through MRD-024")
    actual_parameter_counts = Counter(row["status"] for row in data)
    # Use an explicit total plus mandatory categories; this also catches new
    # statuses that would otherwise silently weaken the release boundary.
    mandatory_counts = {
        "candidate_component": 1,
        "candidate_dimension": 10,
        "candidate_limit": 2,
        "controlled_requirement": 1,
        "derived_candidate": 1,
        "selection_required": 5,
        "study_only": 4,
    }
    if actual_parameter_counts != mandatory_counts:
        errors.append(f"parameter status counts changed: {dict(actual_parameter_counts)}")
    if len(interfaces) != 12 or [row["interface_id"] for row in interfaces] != [f"MIC-{index:03d}" for index in range(1, 13)]:
        errors.append("interface register must contain ordered MIC-001 through MIC-012")
    expected_interface_counts = {
        "design_required": 2,
        "physical_fit_required": 5,
        "received_verification_required": 1,
        "selection_required": 4,
    }
    if Counter(row["current_status"] for row in interfaces) != expected_interface_counts:
        errors.append("interface status counts changed")
    if len(components) != 19 or [row["item_no"] for row in components] != [str(index) for index in range(1, 20)]:
        errors.append("assembly component schedule must contain item numbers 1 through 19")
    for row in components:
        if row["source_id"] not in bom:
            errors.append(f"assembly item {row['item_no']} references unknown {row['source_id']}")
        if not row["assembly_disposition"]:
            errors.append(f"assembly item {row['item_no']} lacks a disposition")
    if len(extrusions) != 3 or sum(int(row["quantity"]) for row in extrusions) != 5:
        errors.append("extrusion schedule must resolve five cuts in three rows")
    total_length = sum(int(row["quantity"]) * float(row["finished_length_mm"]) for row in extrusions)
    if total_length != 2140.0:
        errors.append(f"extrusion cut total expected 2140 mm, found {total_length}")
    if any(row["parent_bom_id"] != "BOM-024" or row["release_state"] != "candidate_cut_length" for row in extrusions):
        errors.append("extrusion schedule lost BOM-024/candidate-cut controls")

    expected_inspection_ids = {
        "MRD-001", "MRD-002", "MRD-003", "MRD-005", "MRD-006", "MRD-007", "MRD-008", "MRD-009", "MRD-010",
        "MIC-001", "MIC-003", "MIC-004", "MIC-005", "MIC-006", "MIC-007", "MIC-008", "MIC-009", "MIC-010", "MIC-011", "MIC-012",
    }
    if {row["parameter_or_interface_id"] for row in inspection} != expected_inspection_ids:
        errors.append("mechanical inspection template seed IDs changed")
    for row in inspection:
        if row["record_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" or row["mechanical_revision"] != REVISION:
            errors.append(f"inspection row {row['parameter_or_interface_id']} looks executed or has wrong revision")

    expected_datums = {
        "A0": ("0", "0", "0"),
        "C0": ("-210", "0", "0"),
        "J1": ("-166", "0", "500"),
        "J2": ("-6", "0", "500"),
        "G1": ("154", "0", "500"),
        "OMAX": ("194", "0", "500"),
    }
    if {row["datum_id"]: (row["x_mm"], row["y_mm"], row["z_mm"]) for row in datums} != expected_datums:
        errors.append("generated datum chain changed")
    if float(expected_datums["J2"][0]) - float(expected_datums["J1"][0]) != 160.0:
        errors.append("J1-J2 spacing is not 160 mm")
    if float(expected_datums["G1"][0]) - float(expected_datums["J2"][0]) != 160.0:
        errors.append("J2-G1 spacing is not 160 mm")
    if float(expected_datums["OMAX"][0]) - float(expected_datums["J1"][0]) != 360.0:
        errors.append("J1-OMAX reach is not 360 mm")

    try:
        tree = ET.parse(svg_path)
    except ET.ParseError as exc:
        errors.append(f"general-arrangement SVG does not parse: {exc}")
    else:
        all_text = " ".join(element.text or "" for element in tree.iter() if element.tag.endswith("text"))
        for token in (REVISION, WARNING, "J1 AXIS HEIGHT 500", "REACH ≤ 360", "NO STRUCTURAL CUTTING ORDER"):
            if token not in all_text:
                errors.append(f"general-arrangement SVG lacks {token!r}")
        style_text = " ".join(element.text or "" for element in tree.iter() if element.tag.endswith("style"))
        sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", style_text)]
        if not sizes or min(sizes) < 14:
            errors.append(f"general-arrangement text below 14 px or uncheckable: {sizes}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("revision") != REVISION or summary.get("warning") != WARNING:
        errors.append("mechanical summary revision/warning changed")
    expected_counts = {"controlled_parameters": 24, "interfaces": 12, "assembly_components": 19, "extrusion_cut_rows": 3, "datums": 6}
    if summary.get("counts") != expected_counts:
        errors.append(f"mechanical summary counts changed: {summary.get('counts')}")
    for path in (data_path, interface_path, component_path, extrusion_path):
        key = path.relative_to(ROOT).as_posix()
        if summary.get("source_hashes", {}).get(key) != canonical_text_sha256(path):
            errors.append(f"mechanical summary hash stale for {key}")

    manifest = json.loads((CAD / "generated" / "manifest.json").read_text(encoding="utf-8"))
    controlled = manifest["controlled_parameters"]
    if controlled.get("link_centers_mm") != 160.0 or controlled.get("adapter_mm") != [90.0, 110.0, 6.35] or controlled.get("anchor_mm") != [100.0, 80.0, 6.35]:
        errors.append("P0.2 data contract disagrees with R0.1 native CAD manifest")
    guard = controlled.get("guard_space_reservation_mm", {})
    if [guard.get("internal_width"), guard.get("internal_depth"), guard.get("internal_height")] != [900.0, 400.0, 950.0]:
        errors.append("P0.2 guard reservation disagrees with R0.1 manifest")

    gate_text = (ROOT / "requirements" / "hr-v0-energization-gates.csv").read_text(encoding="utf-8")
    for evidence in (
        "cad/hr-v0/mechanical-release-data.csv",
        "cad/hr-v0/mechanical-interface-control.csv",
        "cad/hr-v0/generated/assembly/",
        "bom/hr-v0-extrusion-cut-schedule.csv",
        "docs/hr-v0-mechanical-release-p0.2.md",
    ):
        if evidence not in gate_text:
            errors.append(f"energization gates do not cite {evidence}")
    requirement_rows = {row["id"]: row for row in rows(ROOT / "requirements" / "requirements.csv")}
    if requirement_rows.get("MECH-002", {}).get("verification_id") != "AUDIT-MECH-001":
        errors.append("MECH-002 / AUDIT-MECH-001 traceability missing")
    procedures = {row["verification_id"]: row for row in rows(ROOT / "tests" / "procedures" / "procedure-registry.csv")}
    if procedures.get("AUDIT-MECH-001", {}).get("linked_requirement_ids") != "MECH-002":
        errors.append("AUDIT-MECH-001 procedure missing")
    release = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    mechanical = next((item for item in release["current_products"] if item["domain"] == "mechanical"), {})
    if mechanical.get("identifier") != REVISION:
        errors.append("release candidate does not identify HR-V0-MECH-P0.2")

    if errors:
        print("HR-V0 mechanical release validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 mechanical release validation: PASS")
    print("24 controlled parameters; 12 interfaces; 19 assembly groups; 5 extrusion cuts; 6 datums")
    print("0 fabrication or assembly releases; physical fit, fasteners, stops, guard, mass and bench anchoring remain open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
