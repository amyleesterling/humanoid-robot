#!/usr/bin/env python3
"""Fail-closed validation for HR-30 whole-body power route guides P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1" / "harness" / "power-route-guides-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
WARNING = "PRELIMINARY - WHOLE-BODY POWER ROUTE-GUIDE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    required = {
        "README.md", "status.json", "index.html", "power-route-guides.svg", "power-route-guides-source.py",
        "route-centerline-register.csv", "clamp-obligation-register.csv", "guard-envelope-register.csv",
        "open-holds.csv", "primary-source-register.csv", "HR-30_power_route_guides_candidate.step",
        "HR-30_power_route_guides_candidate.glb", "HR-30_whole_body_power_routes_candidate.glb", "file-manifest.csv",
    }
    need(required <= {p.name for p in OUT.iterdir() if p.is_file()}, "required route-guide artifacts missing")
    route_rows = rows("route-centerline-register.csv")
    need(len(route_rows) == 6, "six route rows required")
    need(len({r["source_corridor"] for r in route_rows}) == 6, "corridor IDs must be unique")
    for row in route_rows:
        radius = float(row["exact_guide_radius_mm"])
        max_od = float(row["candidate_max_od_mm"])
        chord = float(row["chord_length_mm"])
        centerline = float(row["candidate_centerline_length_mm"])
        need(abs(radius - 8.0 * max_od) < 1e-3, f"8xd radius mismatch: {row['source_corridor']}")
        need(chord > 2.0 * radius, f"route too short: {row['source_corridor']}")
        expected = chord - 2.0 * radius + 3.141592653589793 * radius
        need(abs(centerline - expected) < 0.002, f"centerline mismatch: {row['source_corridor']}")
        need(row["bend_screen"] == "PASS GEOMETRIC CENTERLINE RADIUS", "radius screen must pass")
        need(row["collision_state"].startswith("NOT EXECUTED"), "collision may not be claimed")
        need(row["warning"] == WARNING, "warning drift")
    need(len(rows("clamp-obligation-register.csv")) == 24, "24 clamp obligations required")
    need(len(rows("guard-envelope-register.csv")) == 6, "six guard envelopes required")
    need(len(rows("open-holds.csv")) >= 10, "open hold coverage missing")
    status = json.loads((OUT / "status.json").read_text(encoding="utf-8"))
    need(status["route_count"] == 6 and status["exact_circular_turn_count"] == 12, "status counts drift")
    for key in ["guard_solids_complete", "collision_sweeps_complete", "walking_clearance_complete", "physical_validation_complete", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"{key} must remain false")
    for artifact in ["HR-30_power_route_guides_candidate.step", "HR-30_power_route_guides_candidate.glb", "HR-30_whole_body_power_routes_candidate.glb"]:
        need((OUT / artifact).stat().st_size > 1000, f"empty CAD artifact: {artifact}")
    manifest = rows("file-manifest.csv")
    listed = {row["path"] for row in manifest}
    payload = {p.name for p in OUT.iterdir() if p.is_file() and p.name != "file-manifest.csv"}
    need(listed == payload, "manifest file set mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"manifest mismatch: {path.name}")
        need(row["warning"] == WARNING, f"manifest warning drift: {path.name}")
    source_files = {p.name: sha(p) for p in OUT.iterdir() if p.is_file()}
    release_files = {p.name: sha(p) for p in RELEASE.iterdir() if p.is_file()}
    need(source_files == release_files, "source/release package parity failed")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px/1.55" in page and "font-size:16px" in page and "font-size:14px" in page, "legibility CSS missing")
    need("HR-30_whole_body_power_routes_candidate.glb" in page and "camera-controls" in page, "interactive whole-body viewer missing")
    need(WARNING in page and "0</div><p>executed whole-body collision" in page, "preliminary boundary missing")
    for parent in [ROOT / "hr30" / "whole-body-p0.1" / "index.html", ROOT / "hr30" / "whole-body-p0.1" / "harness" / "index.html"]:
        text = parent.read_text(encoding="utf-8")
        need(text.count("HR30-POWER-ROUTE-GUIDES-P01-START") == 1, f"parent marker missing: {parent}")
        need("power-route-guides-p0.1/index.html" in text, f"parent link missing: {parent}")
    whole = ROOT / "hr30" / "whole-body-p0.1"
    release_whole = ROOT / "release" / "hr30" / "whole-body-p0.1"
    changed_parent = ["README.md", "index.html", "file-manifest.csv", "harness/README.md", "harness/index.html", "harness/file-manifest.csv"]
    for relative in changed_parent:
        need(sha(whole / relative) == sha(release_whole / relative), f"parent source/release drift: {relative}")
    whole_manifest = {r["path"]: r for r in csv.DictReader((whole / "file-manifest.csv").open(encoding="utf-8", newline=""))}
    for relative in ["README.md", "index.html", "harness/README.md", "harness/index.html", "harness/file-manifest.csv"]:
        need(relative in whole_manifest, f"whole-body manifest row missing: {relative}")
        need(whole_manifest[relative]["sha256"] == sha(whole / relative), f"whole-body manifest hash drift: {relative}")
    for path in OUT.iterdir():
        if path.is_file():
            relative = path.relative_to(whole).as_posix()
            need(relative in whole_manifest and whole_manifest[relative]["sha256"] == sha(path), f"whole-body package manifest drift: {relative}")
    print("PASS: 6 tangent whole-body power routes, 12 exact radius guides, 24 clamp obligations; all physical/work authority open")


if __name__ == "__main__":
    main()
