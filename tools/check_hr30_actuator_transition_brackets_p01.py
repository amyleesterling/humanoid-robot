#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 25-axis transition-bracket package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
PHYSICAL = WB / "harness" / "physical-p0.1"
OUT = WB / "harness" / "actuator-transition-brackets-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_actuator_transition_brackets_p01.py"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release bracket package missing")
    placements, spacing = rows(OUT / "placement-register.csv"), rows(OUT / "spacing-screen.csv")
    transitions = rows(PHYSICAL / "actuator-power-transition-register.csv")
    parts, interfaces, holds, sources = rows(OUT / "part-register.csv"), rows(OUT / "interface-register.csv"), rows(OUT / "open-holds.csv"), rows(OUT / "source-register.csv")
    need(len(placements) == len(spacing) == len(transitions) == 25, "25-axis transition coverage required")
    need({r["axis_id"] for r in placements} == {r["axis_id"] for r in transitions}, "axis coverage drift")
    need(len({r["placement_id"] for r in placements}) == 25 and len({(r["candidate_x_mm"],r["candidate_y_mm"],r["candidate_z_mm"]) for r in placements}) == 25, "placement identity/coordinate collision")
    need(all(r["nominal_envelope_overlap"] == "NO" and float(r["nominal_aabb_clearance_mm"]) > 0 for r in spacing), "nominal cassette envelope overlap")
    need(len(parts) == 2 and len(interfaces) == 4 and len(holds) == 6 and len(sources) == 7, "controlled register count drift")
    need(any("NOT A MOLEX CUTOUT" in r["verified_state"] for r in interfaces), "connector proxy boundary missing")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["sha256"] == sha(ROOT / r["official_url_or_path"]) for r in sources if r["publisher"] == "Project Button"), "local source hash drift")
    required = ["ATB-BASE-P0.1.step","ATB-CLAMP-CAP-P0.1.step","ATB-STANDARD-ASSEMBLY-P0.1.step","ATB-STANDARD-ASSEMBLY-P0.1.glb","HR30_25_axis_transition_brackets_candidate.step","HR30_25_axis_transition_brackets_candidate.glb"]
    need(all((OUT / name).stat().st_size > 1000 for name in required), "CAD export missing or implausibly small")
    need((OUT / "actuator-transition-brackets-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    status = json.loads((OUT / "bracket-status.json").read_text(encoding="utf-8"))
    need(status["placement_count"] == 25 and status["installed_solid_count"] == 75 and status["bracket_candidate_dimensioned"] is True, "status coverage drift")
    for key in ["connector_fit_released","manufacturing_cutout_released","received_part_fit_verified","material_selected","clamp_validated","tolerance_aware_collision_validated","fabrication_released","procurement_authority","fabrication_authority","connection_authority","powered_test_authority","motion_authority","energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:14px" in page and "project-owned clearance proxy" in page.lower(), "guide content/legibility drift")
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["actuator_transition_bracket_placement_count"] == 25 and root_status["actuator_transition_bracket_manufacturing_cutout_released"] is False, "root status integration drift")
    need("HR30-TRANSITION-BRACKETS-P01-START" in (WB / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    print("PASS: 25 dimensioned transition-cassette placements and editable CAD are synchronized; connector fit, fabrication and all power/motion authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
