#!/usr/bin/env python3
"""Fail-closed checks for the P0.9 X430 integrated-arm comparison."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.9-x430"
DOC = ROOT / "docs" / "hr-v0-x430-integrated-arm-p0.9.md"
GUIDE = ROOT / "release" / "hr-v0" / "arm-architecture-p0.9-x430" / "index.html"
REVISION = "HR-V0-ARM-ARCH-P0.9-X430-INTEGRATED-CANDIDATE"


def rows(name: str) -> list[dict[str, str]]:
    with (PKG / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(value: object, expected: float, tolerance: float = 0.002) -> bool:
    return math.isclose(float(value), expected, abs_tol=tolerance)


def main() -> int:
    errors: list[str] = []
    summary = json.loads((PKG / "architecture-summary.json").read_text(encoding="utf-8"))
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    continuous = json.loads((PKG / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    collision = rows("full-arm-collision-sweep.csv")
    continuous_pairs = rows("continuous-clearance-summary.csv")
    continuous_cells = rows("continuous-clearance-cells.csv")
    stops = rows("hard-stop-sweep.csv")
    holds = rows("architecture-holds.csv")
    interfaces = rows("interface-schedule.csv")
    transforms = rows("transform-schedule.csv")
    fasteners = rows("fastener-stack-requirements.csv")
    tolerances = rows("tolerance-control-register.csv")
    load = rows("mass-load-screen.csv")

    if summary.get("revision") != REVISION or status.get("revision") != REVISION:
        errors.append("revision identity changed")
    if status.get("state") != "COMPARISON_CANDIDATE_NOT_SELECTED":
        errors.append("candidate selection state changed")
    flags = summary.get("release_flags", {})
    if len(flags) != 9 or any(value is not False for value in flags.values()):
        errors.append("one or more release flags are absent or not false")
    if summary.get("configuration_disposition") != "P0.9 integrated comparison only; P0.7 remains controlled and XM430 is not selected":
        errors.append("configuration disposition changed")

    geometry = summary.get("geometry_mm", {})
    for key, expected in {"j1_to_j2": 191.55, "j2_to_g1": 125.05, "object_center_from_j1": 345.0}.items():
        if not close(geometry.get(key, -1), expected):
            errors.append(f"geometry changed: {key}")
    mass = summary.get("mass_load", {})
    for key, expected in {
        "incomplete_known_mass_g": 577.091,
        "provisional_headroom_g": 172.909,
        "elbow_2_25_screen_nm": 1.104,
        "xm430_stall_endpoint_ratio_only": 3.713,
    }.items():
        if not close(mass.get(key, -1), expected):
            errors.append(f"mass/load screen changed: {key}")
    if not close(float(mass.get("incomplete_known_mass_g", 0)) + float(mass.get("provisional_headroom_g", 0)), 750.0):
        errors.append("mass and provisional headroom do not sum to 750 g")

    if len(collision) != 9464:
        errors.append("sampled full-arm pose count changed")
    if max(float(row["nonintentional_intersection_mm3"]) for row in collision if float(row["j2_deg"]) <= 115.0) > 1e-8:
        errors.append("positive nonintentional sampled volume exists through soft limit")
    if len(continuous_pairs) != 69 or len(continuous_cells) != 130:
        errors.append("continuous certificate pair/cell count changed")
    if continuous.get("joint_domain_deg") != {"j1": [-20.0, 70.0], "j2": [15.0, 115.0]}:
        errors.append("continuous joint domain changed")
    if not close(continuous.get("required_certified_clearance_mm", 0), 0.75, 1e-9):
        errors.append("required continuous clearance changed")
    if float(continuous.get("minimum_guaranteed_clearance_mm", 0)) < 0.75:
        errors.append("continuous certificate falls below 0.75 mm")
    if not close(continuous.get("minimum_guaranteed_clearance_mm", 0), 0.862928, 1e-6):
        errors.append("continuous minimum changed unexpectedly")
    if continuous.get("pair_count") != 69 or continuous.get("leaf_cell_count") != 130 or continuous.get("exact_brep_distance_calls") != 85:
        errors.append("continuous certificate accounting changed")
    if any(float(row["minimum_guaranteed_clearance_mm"]) < 0.75 for row in continuous_pairs):
        errors.append("a continuous pair certificate is below the required clearance")

    if len(stops) != 61 or not close(summary["positive_stop"]["nominal_first_metal_contact_deg"], 118.0, 0.001):
        errors.append("nominal positive-stop evidence changed")
    if len(holds) != 12 or sum(row["state"] == "OPEN" for row in holds) != 8 or sum(row["state"] == "PARTIAL" for row in holds) != 4:
        errors.append("hold register is not 8 OPEN / 4 PARTIAL")
    if {row["hold_id"] for row in holds if row["state"] == "PARTIAL"} != {"ELBH-002", "ELBH-007", "ELBH-008", "ELBH-009"}:
        errors.append("unexpected hold advanced to PARTIAL")
    if len(interfaces) != 5 or len(transforms) != 5 or len(fasteners) != 4 or len(tolerances) != 5 or len(load) != 1:
        errors.append("interface/transform/fastener/tolerance/load record count changed")
    if any(row["state"] != "OPEN" or row["candidate"] != "SELECTION REQUIRED" for row in fasteners):
        errors.append("a fastener stack is selected or not open")
    if any(row["state"] != "OPEN" for row in tolerances):
        errors.append("a tolerance control was advanced without evidence")

    required = (
        "HR-V0_arm_P0.9_X430_integrated_candidate.step",
        "HR-V0_arm_P0.9_X430_integrated_candidate.glb",
        "parts/P09-C01_X430_fixed-catch-adapter.step",
        "parts/P09-C02_X430_moving-striker-adapter.step",
        "P09-C01_fixed-catch-review-drawing.svg",
        "P09-C02_moving-striker-review-drawing.svg",
    )
    for name in required:
        if not (PKG / name).is_file():
            errors.append(f"missing generated artifact: {name}")
    if (PKG / required[0]).is_file() and not (PKG / required[0]).read_bytes().startswith(b"ISO-10303-21;"):
        errors.append("integrated STEP header invalid")
    if (PKG / required[1]).is_file() and not (PKG / required[1]).read_bytes().startswith(b"glTF"):
        errors.append("integrated GLB header invalid")

    guide = GUIDE.read_text(encoding="utf-8") if GUIDE.is_file() else ""
    doc = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for token in (
        REVISION, "577.091", "172.909", "0.862928", "9,464",
        "P0.7 remains controlled", "XM430 is not selected", "stall-endpoint ratio",
        "NOT APPROVED", "fastener", "tolerance",
    ):
        if token not in guide or token not in doc:
            errors.append(f"controlled explanatory token missing: {token}")
    for unsafe in ("approved for energization", "XM430 is selected", "ready for fabrication"):
        if unsafe.lower() in (guide + doc).lower():
            errors.append(f"unsafe release claim present: {unsafe}")
    for token in ("model-viewer", "font:17px", "font-size:16px", "font-size:13px"):
        if token not in guide:
            errors.append(f"interactive guide legibility/model token missing: {token}")

    if errors:
        print("HR-V0 P0.9 X430 integrated-arm check: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 P0.9 X430 integrated-arm check: PASS")
    print("9,464 sampled poses; 69 continuous pairs; 130 cells; minimum 0.862928 mm")
    print("8 OPEN / 4 PARTIAL holds; P0.7 remains controlled; XM430 is not selected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
