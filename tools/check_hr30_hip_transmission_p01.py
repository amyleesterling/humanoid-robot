"""Fail-closed checks for the HR-30 P0.1 compound hip-drive package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30/whole-body-p0.1/hip-transmission-p0.1"
REL = ROOT / "release/hr30/whole-body-p0.1/hip-transmission-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    status = json.loads((OUT / "hip-transmission-status.json").read_text(encoding="utf-8"))
    need(status["complete_humanoid_present"] and status["hip_axis_count"] == 4, "whole body/four hips")
    need(status["stage_count_per_axis"] == 2 and status["total_transmission_ratio"] == 4.0, "two-stage ratio")
    need(status["new_hip_pair_interference_count"] == 0, "new hip package collision")
    need(not any(status[k] for k in ("capacity_validated", "motion_sweep_validated", "thermal_validated", "fabrication_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority")), "authority boundary")
    reg = rows("hip-transmission-register.csv")
    need(len(reg) == 4 and {r["axis_id"] for r in reg} == {"L_HIP_PITCH","L_HIP_ROLL","R_HIP_PITCH","R_HIP_ROLL"}, "axis register")
    need(all(r["total_ratio"] == "4.000:1" and "GPA32" in r["pulley_set"] and "GBN225" in r["belt_set"] for r in reg), "catalog geometry binding")
    need(len(rows("hip-package-clearance-register.csv")) == 6, "six bilateral pair screens")
    need(len(rows("hip-transmission-mass-budget.csv")) >= 60, "physical part/mass spine")
    mass_impact = rows("whole-body-mass-impact.csv")
    need(len(mass_impact) == 4 and mass_impact[-1]["state"].startswith("EXCEEDS PROGRAM MAXIMUM"), "whole-body replacement mass impact")
    need(not status["program_mass_maximum_met"] and status["projected_active_tether_mass_kg"] > 10.0, "mass blocker disclosed")
    need(len(rows("open-holds.csv")) >= 7 and all(r["state"] == "OPEN" for r in rows("open-holds.csv")), "open engineering holds")
    for name in ("HR-30_hip4_whole_body_candidate.step", "HR-30_hip4_transmissions_only_candidate.step"):
        shape = cq.importers.importStep(str(OUT / name)).val()
        need(shape.Volume() > 1e6, f"nontrivial {name}")
    body_shape = cq.importers.importStep(str(OUT / "HR-30_hip4_whole_body_candidate.step")).val()
    bb = body_shape.BoundingBox()
    print(f"whole-body envelope mm: {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f}")
    need(755 <= bb.zlen <= 775 and bb.xlen > 300 and bb.ylen > 180, "recognizable full-scale whole humanoid envelope")
    urdf = ET.parse(OUT / "hr30_tether_hip4_candidate.urdf").getroot()
    transmissions = [t for t in urdf.findall("transmission") if "HIP4" in t.attrib.get("name", "")]
    need(len(transmissions) == 4 and all(t.find("actuator/mechanicalReduction").text == "4.0" for t in transmissions), "URDF reduction bindings")
    need((OUT / "hr30_tether_hip4_candidate.xml").stat().st_size > 10000, "MJCF present")
    manifest = rows("file-manifest.csv")
    need(all((OUT / r["path"]).is_file() and sha(OUT / r["path"]) == r["sha256"] and (OUT / r["path"]).stat().st_size == int(r["bytes"]) for r in manifest), "manifest")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(REL / p) for p in source_files), "source/release parity")
    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "Four real compound hip drives" in page, "human-legible guide")
    print(f"PASS: four installed 4:1 compound hip drives; {len(manifest)} artifacts; authority remains closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
