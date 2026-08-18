#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 distributed power harness successor."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1" / "harness" / "distributed-power-harness-successor-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
ROUTE_GUIDES = WHOLE / "harness" / "power-route-guides-p0.1" / "route-centerline-register.csv"
RELEASE_WHOLE = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - DISTRIBUTED ACTUATOR-POWER HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
MARKER = "HR30-DISTRIBUTED-POWER-HARNESS-P01"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, tol: float = 1e-7) -> None:
    if not math.isclose(a, b, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"not close: {a} != {b}")


def verify_manifest(path: Path) -> None:
    listed = rows(path / "file-manifest.csv")
    actual = sorted(p.name for p in path.iterdir() if p.is_file() and p.name != "file-manifest.csv")
    if sorted(r["file"] for r in listed) != actual:
        raise AssertionError(f"manifest file set mismatch: {path}")
    for row in listed:
        target = path / row["file"]
        if int(row["bytes"]) != target.stat().st_size or row["sha256"] != sha(target):
            raise AssertionError(f"manifest mismatch: {target}")
        if row["warning"] != WARNING:
            raise AssertionError(f"warning drift: {target}")


def verify_parent_manifest(manifest: Path, base: Path, expected: list[Path]) -> None:
    indexed = {row["path"]: row for row in rows(manifest)}
    for target in expected:
        relative = target.relative_to(base).as_posix()
        if relative not in indexed:
            raise AssertionError(f"parent manifest missing {relative}")
        row = indexed[relative]
        if int(row["bytes"]) != target.stat().st_size or row["sha256"] != sha(target):
            raise AssertionError(f"parent manifest mismatch: {target}")


def main() -> None:
    required = {
        "README.md", "status.json", "index.html", "distributed-power-harness.svg", "distributed-power-harness-source.py",
        "primary-source-register.csv", "cable-family-register.csv", "axis-core-allocation.csv", "corridor-architecture.csv",
        "distribution-node-register.csv", "actuator-breakout-register.csv", "connector-contact-register.csv", "open-holds.csv", "file-manifest.csv",
    }
    if {p.name for p in OUT.iterdir() if p.is_file()} != required:
        raise AssertionError("source package file set drift")
    verify_manifest(OUT)
    verify_manifest(RELEASE)
    source_files = sorted(p.name for p in OUT.iterdir() if p.is_file())
    release_files = sorted(p.name for p in RELEASE.iterdir() if p.is_file())
    if source_files != release_files:
        raise AssertionError("source/release file sets differ")
    for name in source_files:
        if sha(OUT / name) != sha(RELEASE / name):
            raise AssertionError(f"source/release hash mismatch: {name}")

    status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
    if status["axis_count"] != 25 or status["distribution_node_count"] != 6 or status["corridor_count"] != 6:
        raise AssertionError("controlled counts drift")
    if status["old_individual_cable_corridor_failures"] != 5 or status["successor_diameter_screens_pass"] != 6 or status["successor_bend_screens_pass"] != 6:
        raise AssertionError("screen totals drift")
    if status["route_guide_geometry_integrated"] is not True:
        raise AssertionError("route-guide geometry is not integrated")
    for gate in ["protection_components_selected", "breakout_ecad_complete", "route_sweeps_complete", "thermal_validated", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        if status[gate] is not False:
            raise AssertionError(f"unsafe gate true: {gate}")

    cables = {r["part_number"]: r for r in rows(OUT / "cable-family-register.csv")}
    if set(cables) != {"861802", "861804", "861812"}:
        raise AssertionError("cable family drift")
    close(float(cables["861802"]["cable_od_max_mm"]), 5.5880)
    close(float(cables["861804"]["cable_od_max_mm"]), 6.2992)
    close(float(cables["861812"]["cable_od_max_mm"]), 9.3472)
    close(float(cables["861802"]["nominal_dcr_20c_ohm_per_km"]), 6.9 / 1000.0 * 3280.8398950131)
    close(float(cables["861812"]["planning_min_radius_using_max_od_mm"]), 9.3472 * 8.0)

    corridors = rows(OUT / "corridor-architecture.csv")
    if sum(r["old_bundle_geometric_result"] == "FAIL" for r in corridors) != 5:
        raise AssertionError("old bundle failure count drift")
    if any(r["diameter_screen"] != "PASS GEOMETRIC AREA" for r in corridors):
        raise AssertionError("successor diameter screen regression")
    if sum(r["bend_screen"] == "PASS ROUTE-GUIDE GEOMETRY" for r in corridors) != 6:
        raise AssertionError("bend screen count drift")
    guide_rows = {r["source_corridor"]: r for r in rows(ROUTE_GUIDES)}
    if set(guide_rows) != {r["corridor"] for r in corridors}:
        raise AssertionError("route-guide/corridor identity drift")
    for row in corridors:
        close(float(row["trunk_area_fill_ratio"]), (float(row["trunk_max_od_mm"]) / float(row["corridor_diameter_mm"])) ** 2, 2e-6)
        guide = guide_rows[row["corridor"]]
        if row["route_guide_id"] != guide["route_id"] or row["integrated_route_geometry"] != guide["turn_geometry"]:
            raise AssertionError(f"route-guide binding drift: {row['corridor']}")
        close(float(row["integrated_route_guide_radius_mm"]), float(guide["exact_guide_radius_mm"]))
        if float(row["integrated_route_guide_radius_mm"]) < float(row["candidate_required_bend_radius_mm"]):
            raise AssertionError(f"route-guide bend regression: {row['corridor']}")
        if int(row["protected_core_count"]) + int(row["spare_cores"]) != int(row["trunk_core_count"]):
            raise AssertionError(f"core accounting error: {row['corridor']}")

    axes = rows(OUT / "axis-core-allocation.csv")
    breakouts = rows(OUT / "actuator-breakout-register.csv")
    if len(axes) != 25 or len(breakouts) != 25 or len({r["axis_id"] for r in axes}) != 25:
        raise AssertionError("axis allocation count/uniqueness failure")
    for row in axes:
        cap = float(row["candidate_current_cap_a"])
        if cap > 2.499010 + 1e-9:
            raise AssertionError(f"cap drift: {row['axis_id']}")
        r20 = float(row["nominal_cable_only_loop_r20_ohm"])
        r80 = float(row["nominal_cable_only_loop_r80_ohm"])
        close(r80, r20 * (1 + 0.00393 * 60), 2e-6)
        close(float(row["cap_drop_80c_v"]), cap * r80, 2e-6)
        close(float(row["cap_loss_80c_w"]), cap * cap * r80, 2e-6)
        if "core/cavity" not in row["core_pair"] or "=RETURN" not in row["core_pair"] or "=VDD" not in row["core_pair"]:
            raise AssertionError(f"non-explicit core assignment: {row['axis_id']}")

    nodes = rows(OUT / "distribution-node-register.csv")
    if sorted(int(r["channel_count"]) for r in nodes) != [1, 2, 5, 5, 6, 6] or sum(int(r["channel_count"]) for r in nodes) != 25:
        raise AssertionError("distribution node channel count drift")
    contacts = rows(OUT / "connector-contact-register.csv")
    if not {"430300038", "430310021", "430251200", "430201200"}.issubset({r["part_number"] for r in contacts}):
        raise AssertionError("exact connector candidate missing")
    if len(rows(OUT / "open-holds.csv")) != 12:
        raise AssertionError("open hold count drift")

    parent_files = [
        WHOLE / "README.md", WHOLE / "index.html", WHOLE / "harness" / "README.md",
        WHOLE / "harness" / "index.html", WHOLE / "harness" / "file-manifest.csv",
        *sorted(p for p in OUT.iterdir() if p.is_file()),
    ]
    verify_parent_manifest(WHOLE / "file-manifest.csv", WHOLE, parent_files)
    verify_parent_manifest(
        WHOLE / "harness" / "file-manifest.csv",
        WHOLE / "harness",
        [WHOLE / "harness" / "README.md", WHOLE / "harness" / "index.html"],
    )
    for relative in [Path("README.md"), Path("index.html"), Path("file-manifest.csv"), Path("harness/README.md"), Path("harness/index.html"), Path("harness/file-manifest.csv")]:
        if sha(WHOLE / relative) != sha(RELEASE_WHOLE / relative):
            raise AssertionError(f"parent source/release mismatch: {relative}")
    for parent in [WHOLE / "README.md", WHOLE / "index.html", WHOLE / "harness" / "README.md", WHOLE / "harness" / "index.html"]:
        text = parent.read_text(encoding="utf-8")
        if text.count(f"<!-- {MARKER}-START -->") != 1 or text.count(f"<!-- {MARKER}-END -->") != 1:
            raise AssertionError(f"parent guide marker missing or duplicated: {parent}")
        if "distributed-power-harness-successor-p0.1/index.html" not in text:
            raise AssertionError(f"parent guide link missing: {parent}")

    for path in list(OUT.glob("*.csv")) + [OUT / "index.html", OUT / "README.md", OUT / "distributed-power-harness.svg"]:
        text = path.read_text(encoding="utf-8")
        if path.name != "file-manifest.csv" and WARNING not in text:
            raise AssertionError(f"warning absent: {path}")
        forbidden = ["APPROVED FOR ENERGIZATION", "ENERGIZATION AUTHORITY GRANTED", "FABRICATION RELEASED"]
        if any(token in text for token in forbidden):
            raise AssertionError(f"unsafe wording: {path}")
    html_text = (OUT / "index.html").read_text(encoding="utf-8")
    if "font-size:11px" in html_text or "font-size:10px" in html_text or "font-size:9px" in html_text:
        raise AssertionError("interface text below 12px")
    print("PASS: 25 explicit protected core pairs; six distributed nodes; all diameter and route-guide bend screens pass; guarding, collision, thermal and all power authorities remain open")


if __name__ == "__main__":
    main()
