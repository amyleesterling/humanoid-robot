#!/usr/bin/env python3
"""Fail-closed checker for HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "cad" / "hr-v0" / "generated" / "elbow-architecture-p0.8"
GUIDE = ROOT / "release" / "hr-v0" / "elbow-architecture-p0.8" / "index.html"
DOC = ROOT / "docs" / "hr-v0-x430-elbow-architecture-p0.8.md"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"


def read_csv(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def close(actual: object, expected: float, tolerance: float = 0.001) -> bool:
    return math.isclose(float(actual), expected, abs_tol=tolerance)


def main() -> int:
    errors: list[str] = []
    summary = json.loads((PKG / "architecture-summary.json").read_text(encoding="utf-8"))
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    features = read_csv("interface-feature-evidence.csv")
    transforms = read_csv("transform-schedule.csv")
    interfaces = read_csv("interface-schedule.csv")
    collisions = read_csv("collision-sweep.csv")
    stops = read_csv("hard-stop-sweep.csv")
    comparison = read_csv("mass-load-comparison.csv")
    holds = read_csv("architecture-holds.csv")

    if summary.get("revision") != "HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE":
        errors.append("revision identity changed")
    flags = summary.get("release_flags", {})
    if len(flags) != 9 or any(value is not False for value in flags.values()):
        errors.append("one or more release flags are missing or not false")
    if status.get("state") != "COMPARISON_CANDIDATE_NOT_SELECTED":
        errors.append("candidate selection state changed")
    if status.get("open_hold_count") != 9 or status.get("partial_hold_count") != 3:
        errors.append("hold-state counts changed")
    if len(holds) != 12 or sum(row["state"] == "OPEN" for row in holds) != 9 or sum(row["state"] == "PARTIAL" for row in holds) != 3:
        errors.append("architecture hold register is not 9 OPEN / 3 PARTIAL")
    if {row["hold_id"] for row in holds if row["state"] == "PARTIAL"} != {"ELBH-002", "ELBH-007", "ELBH-008"}:
        errors.append("unexpected hold advanced to PARTIAL")

    geometry = summary.get("geometry_mm", {})
    for key, expected in {
        "j1_to_j2_axis": 191.55,
        "j2_to_g1_frame_origin": 125.05,
        "candidate_object_center_from_j1": 345.0,
        "fr12_s102_local_z_registration_shift": 21.0,
        "fr12_s102_fixed_face_offset": 40.5,
        "fr12_h101_moving_face_offset": 28.0,
    }.items():
        if not close(geometry.get(key, -999), expected):
            errors.append(f"geometry value changed: {key}")
    overlaps = summary.get("assembly_model_overlap_review_mm3", {})
    for key, expected in {
        "x430_with_fr12_s102": 200.75725,
        "x430_with_fr12_h101_straight_reference": 221.902962,
        "fr12_s102_with_fr12_h101_straight_reference": 0.0,
    }.items():
        if not close(overlaps.get(key, -999), expected, 0.001):
            errors.append(f"assembly overlap review value changed: {key}")

    stop = summary.get("stop", {})
    if not close(stop.get("nominal_first_contact_deg", -1), 118.0, 0.01):
        errors.append("nominal stop contact is not 118 degrees")
    if float(stop.get("maximum_nonintentional_intersection_through_soft_limit_mm3", -1)) != 0.0:
        errors.append("positive nonintentional volume exists through soft limit")
    if float(stop.get("maximum_nonintentional_intersection_through_stop_mm3", -1)) != 0.0:
        errors.append("positive nonintentional volume exists through stop target")
    if not close(stop.get("first_sampled_nonintentional_collision_deg", -1), 120.0):
        errors.append("first sampled nonintentional collision changed")

    mass = summary.get("mass_and_load", {})
    for key, expected in {
        "fixed_catch_cad_mass_g": 52.234,
        "moving_striker_cad_mass_g": 52.234,
        "incomplete_known_mass_g": 577.091,
        "provisional_headroom_to_750_g": 172.909,
        "elbow_2_25_screen_nm": 1.104,
        "xm430_12v_stall_endpoint_ratio_only": 3.713,
    }.items():
        if not close(mass.get(key, -999), expected, 0.002):
            errors.append(f"mass/load value changed: {key}")
    if not close(float(mass["incomplete_known_mass_g"]) + float(mass["provisional_headroom_to_750_g"]), 750.0, 0.002):
        errors.append("mass and headroom do not close to 750 g")

    if len(features) != 3 or len(transforms) != 3 or len(interfaces) != 3:
        errors.append("controlled feature/transform/interface counts changed")
    if len(collisions) != 221 or len(stops) != 61 or len(comparison) != 2:
        errors.append("controlled sweep/comparison counts changed")
    if max(float(row["nonintentional_intersection_mm3"]) for row in collisions if float(row["j2_deg"]) <= 118.0) > 1e-8:
        errors.append("collision CSV contains nonintentional volume through 118 degrees")

    for name, digest in summary.get("source_sha256", {}).items():
        path = (VENDOR / name) if name != "FR12-H104K.stp" else (ROOT / "cad" / "vendor" / "robotis" / name)
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"source identity mismatch: {name}")

    required_files = (
        "HR-V0_X430_elbow_P0.8_candidate.step",
        "HR-V0_X430_elbow_P0.8_candidate.glb",
        "parts/P08-C01_X430_fixed-catch-adapter.step",
        "parts/P08-C02_X430_moving-striker-adapter.step",
        "P08-C01_fixed-catch-review-drawing.svg",
        "P08-C02_moving-striker-review-drawing.svg",
    )
    for name in required_files:
        if not (PKG / name).is_file():
            errors.append(f"missing generated artifact: {name}")
    if (PKG / required_files[0]).is_file() and not (PKG / required_files[0]).read_bytes().startswith(b"ISO-10303-21;"):
        errors.append("integrated STEP header invalid")
    if (PKG / required_files[1]).is_file() and not (PKG / required_files[1]).read_bytes().startswith(b"glTF"):
        errors.append("integrated GLB header invalid")

    guide = GUIDE.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    for token in (
        "577.091",
        "172.909",
        "191.55",
        "125.05",
        "345.0",
        "stall-endpoint ratio only",
        "P0.7 remains",
        "XM430 is not selected",
    ):
        if token not in guide or token not in doc:
            errors.append(f"controlled explanatory token missing: {token}")
    for unsafe in ("approved for energization", "XM430 is selected", "ready for fabrication"):
        if unsafe.lower() in (guide + doc).lower():
            errors.append(f"unsafe release claim present: {unsafe}")
    for token in ("font:17px", "font-size:16px", "font-size:13px", "model-viewer"):
        if token not in guide:
            errors.append(f"interactive guide requirement missing: {token}")

    if errors:
        print("HR-V0 X430 elbow P0.8 check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 X430 elbow P0.8 check: PASS")
    print("3 exact feature records; 221 sampled poses; 118 deg nominal stop; 9 OPEN and 3 PARTIAL holds")
    print("P0.7 remains controlled; XM430 is not selected; all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
