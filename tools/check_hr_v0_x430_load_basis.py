#!/usr/bin/env python3
"""Fail-closed checks for the P1.1 X430 moving-load basis."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "cad" / "hr-v0" / "generated" / "arm-load-basis-p1.1-x430"
DOC = ROOT / "docs" / "hr-v0-x430-load-basis-p1.1.md"
GUIDE = ROOT / "release" / "hr-v0" / "arm-load-basis-p1.1-x430" / "index.html"
REVISION = "HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(value: object, expected: float, tolerance: float = 1e-6) -> bool:
    return math.isclose(float(value), expected, abs_tol=tolerance)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    expected_files = {
        "component-mass-properties.csv",
        "gravity-envelope.csv",
        "inertia-energy-sensitivity.csv",
        "load-basis-summary.json",
        "open-input-register.csv",
        "package-status.json",
        "source-register.csv",
        "stop-load-sensitivity.csv",
    }
    actual_files = {path.name for path in PKG.iterdir() if path.is_file()}
    if actual_files != expected_files:
        errors.append(f"file set mismatch: missing={sorted(expected_files-actual_files)} extra={sorted(actual_files-expected_files)}")
    try:
        summary = json.loads((PKG / "load-basis-summary.json").read_text(encoding="utf-8"))
        status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
        components = rows("component-mass-properties.csv")
        gravity = rows("gravity-envelope.csv")
        energy = rows("inertia-energy-sensitivity.csv")
        stop = rows("stop-load-sensitivity.csv")
        open_inputs = rows("open-input-register.csv")
        sources = rows("source-register.csv")
    except Exception as exc:
        print(f"P1.1 load-basis parse failure: {exc}")
        return 1

    if summary.get("revision") != REVISION or status.get("revision") != REVISION:
        errors.append("revision mismatch")
    if "NOT APPROVED" not in summary.get("warning", "") or "ENERGIZATION" not in summary.get("warning", ""):
        errors.append("preliminary warning missing")
    counts = summary.get("counts", {})
    expected_counts = {"component_rows": 7, "gravity_rows": 401, "energy_rows": 20, "stop_rows": 16, "open_inputs": 10}
    if counts != expected_counts:
        errors.append(f"summary counts changed: {counts}")
    if [len(components), len(gravity), len(energy), len(stop), len(open_inputs), len(sources)] != [7, 401, 20, 16, 10, 4]:
        errors.append("CSV row counts changed")

    known = summary.get("known_subset", {})
    reference = summary.get("reference_allocation", {})
    if not close(known.get("mass_g", 0), 143.485169) or not close(known.get("nominal_ixx_about_j2_kg_m2", 0), 0.000650235102, 1e-12) or not close(known.get("geometry_support_ixx_kg_m2", 0), 0.000921987948, 1e-12):
        errors.append("known-subset mass/inertia changed")
    if not close(reference.get("mass_g", 0), 453.485169) or not close(reference.get("point_model_ixx_about_j2_kg_m2", 0), 0.006303990877, 1e-12) or not close(reference.get("support_plus_point_ixx_kg_m2", 0), 0.006575743723, 1e-12):
        errors.append("reference allocation mass/inertia changed")
    if "NOT UPPER BOUND" not in reference.get("status", ""):
        errors.append("reference model overclaims an upper bound")

    by_component = {row["component_id"]: row for row in components}
    if set(by_component) != {"P11-C02", "20-2040-050", "P11-DISTAL", "GRIP-ALLOC", "PAYLOAD-REQ", "FR12-H101", "MOVE-HARDWARE"}:
        errors.append("component identifiers changed")
    if by_component.get("FR12-H101", {}).get("mass_g") != "SELECTION REQUIRED" or "EXCLUDED" not in by_component.get("FR12-H101", {}).get("state", ""):
        errors.append("FR12-H101 uncertainty was hidden")
    if by_component.get("MOVE-HARDWARE", {}).get("mass_g") != "SELECTION REQUIRED" or "EXCLUDED" not in by_component.get("MOVE-HARDWARE", {}).get("state", ""):
        errors.append("moving-hardware uncertainty was hidden")
    if "NOT MASS/INERTIA EVIDENCE" not in by_component.get("GRIP-ALLOC", {}).get("state", ""):
        errors.append("gripper allocation is presented as evidence")

    if gravity[0]["j2_deg"] != "15.00" or gravity[-1]["j2_deg"] != "115.00":
        errors.append("gravity domain changed")
    gravity_summary = summary.get("gravity", {})
    if not close(gravity_summary.get("maximum_reference_absolute_nm", 0), 0.483257699) or not close(gravity_summary.get("angle_of_maximum_deg", 0), 15.0) or not close(gravity_summary.get("screen_2_25x_nm", 0), 1.087329823) or not close(gravity_summary.get("proof_3x_screen_nm", 0), 3.261989468):
        errors.append("gravity screen changed")
    if any("INCOMPLETE" not in row["status"] for row in gravity):
        errors.append("gravity rows overclaim completeness")

    if {row["case_id"] for row in energy} != {"KNOWN-NOMINAL", "KNOWN-SUPPORT-BOUND", "REFERENCE-POINT", "REFERENCE-SUPPORT"}:
        errors.append("energy case identifiers changed")
    if {row["speed_deg_s"] for row in energy} != {"5.000", "10.000", "20.000", "30.000", "180.000"}:
        errors.append("energy speed sensitivity changed")
    if any("SENSITIVITY ONLY" not in row["status"] for row in energy):
        errors.append("energy sensitivity overclaims a result")

    stop_summary = summary.get("stop", {})
    if not close(stop_summary.get("nominal_contact_deg", 0), 117.999977) or not close(stop_summary.get("nominal_contact_radius_mm", 0), 45.604835001) or stop_summary.get("contact_solution_count") != 4 or not close(stop_summary.get("proof_screen_one_rail_force_n", 0), 71.527272672):
        errors.append("stop geometry/force screen changed")
    by_stop = {row["case_id"]: row for row in stop}
    if not close(by_stop.get("3X-PROOF-SCREEN", {}).get("derived_average_force_n", 0), 71.527272672) or not close(by_stop.get("MOMENT-10NM", {}).get("derived_average_force_n", 0), 219.274995729):
        errors.append("stop moment sensitivity changed")
    if any("NOT PEAK" not in row["status"] for row in stop):
        errors.append("stop-force sensitivity overclaims peak/capacity")

    if any(row["state"] != "OPEN" for row in open_inputs) or {row["input_id"] for row in open_inputs} != {f"LOAD-OPEN-{index:02d}" for index in range(1, 11)}:
        errors.append("open-input register changed or closed without evidence")
    for row in sources:
        path = ROOT / row["path"]
        if not path.is_file() or sha256(path) != row["sha256"]:
            errors.append(f"source binding failed: {row['source_id']} {row['path']}")
    if summary.get("source_binding") != {"count": 4, "status": "SHA256_BOUND_TO_R95"}:
        errors.append("source-binding summary changed")

    flags = status.get("release_flags", {})
    expected_flags = {"p1_1_selected", "x430_selected", "mass_closed", "com_closed", "inertia_closed", "continuous_torque_closed", "stop_load_closed", "structural_release", "motion_authorized", "fabrication_authorized", "connection_authorized", "energization_authorized"}
    if set(flags) != expected_flags or any(flags.values()):
        errors.append("release flags are missing or non-false")
    for path in (DOC, GUIDE):
        if not path.is_file():
            errors.append(f"missing synchronized artifact {path.relative_to(ROOT)}")
        else:
            text = path.read_text(encoding="utf-8")
            if REVISION not in text or "NOT APPROVED" not in text:
                errors.append(f"revision/warning missing from {path.relative_to(ROOT)}")

    if errors:
        print("HR-V0 P1.1 X430 load-basis check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 P1.1 X430 load-basis check: PASS")
    print("143.485169 g known subset; 453.485169 g incomplete reference allocation")
    print("0.483257699 N m max incomplete gravity reference; 3.261989468 N m proof-screen input")
    print("45.604835001 mm nominal contact radius; 71.527272672 N one-rail static proof-screen equivalent")
    print("10 inputs remain OPEN; mass/COM/inertia/torque/stop/structure and all authorization flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
