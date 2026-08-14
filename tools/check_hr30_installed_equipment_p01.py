"""Fail-closed checks for the HR-30 P0.1 installed-equipment layout."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((OUT / "installed-equipment-status.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((OUT / "installed-equipment-register.csv").open(encoding="utf-8")))
    sources = list(csv.DictReader((OUT / "installed-equipment-source-register.csv").open(encoding="utf-8")))
    battery = list(csv.DictReader((OUT / "battery-energy-source-register.csv").open(encoding="utf-8")))
    assert status["installed_item_count"] == len(rows) == 57
    assert status["empty_component_bays_replaced"] is True
    assert status["tether_first_configuration"] is False
    assert status["tether_development_interface_retained"] is True
    assert status["onboard_energy_candidate_geometry_present"] is True
    assert status["onboard_energy_installed"] is False
    assert status["exact_selections_closed"] is False
    assert status["energization_authority"] is False
    assert abs(sum(float(row["planning_mass_kg"]) for row in rows) - status["planning_installed_mass_kg"]) < 1e-5
    ids = {row["item_id"] for row in rows}
    required = {
        "EQ-T01-PI5", "EQ-T01-MOTION", "EQ-T01-WATCHDOG", "EQ-P01-TETHER-INLET",
        "EQ-P01-DUAL-INTERRUPT", "EQ-P01-PDU", "EQ-P01-IMU", "EQ-H01-DISPLAY",
        "EQ-H01-CAMERA-L", "EQ-H01-CAMERA-R", "EQ-H01-MIC-ARRAY",
        "EQ-H01-SPEAKER-L", "EQ-H01-SPEAKER-R", "EQ-F01-SOLE", "EQ-F02-SOLE",
        "EQ-T01-BATTERY-PACK", "EQ-T01-BATTERY-CASSETTE", "EQ-T01-BATTERY-PROTECTION",
    }
    assert required <= ids
    assert sum(item.startswith("EQ-T01-U2D2-") for item in ids) == 5
    assert sum("LOAD-" in item for item in ids) == 8
    assert sum(item.startswith("EQ-HN01_") for item in ids) == 12
    assert any("raspberrypi.com" in row["manufacturer_source_url"] for row in sources)
    assert any("robotis.us" in row["manufacturer_source_url"] for row in sources)
    assert any("waveshare.com" in row["manufacturer_source_url"] for row in sources)
    assert any("grepow.com" in row["manufacturer_source_url"] for row in sources)
    assert len(battery) == 1 and battery[0]["model"] == "TAA12K4S30EC5"
    assert battery[0]["published_dimensions_mm"] == "193 x 72 x 37"
    assert abs(float(battery[0]["published_mass_kg"]) - 1.057) < 1e-9
    assert abs(float(battery[0]["whole_robot_short_peak_current_screen_a"]) - 727 / 14.8) < 0.001
    assert "NO INTEGRATED BMS/PCM CLAIM" in battery[0]["protection_boundary"]
    assert status["minimum_z_mm"] >= -0.01 and status["maximum_z_mm"] <= 762.01
    step = cq.importers.importStep(str(OUT / "HR-30_installed_equipment_candidate.step")).val()
    assert step.isValid() and step.Volume() > 0
    for name in ("installed-equipment-register.csv", "installed-equipment-source-register.csv", "battery-energy-source-register.csv",
                 "installed-equipment-status.json", "installed-equipment-source.py",
                 "HR-30_installed_equipment_candidate.step", "HR-30_installed_equipment_candidate.glb",
                 "HR-30_integrated_whole_robot_candidate.step"):
        assert (REL / name).exists() and sha(OUT / name) == sha(REL / name)
    html = (OUT / "index.html").read_text(encoding="utf-8")
    assert html.count('id="equipment-layout"') == 1
    assert "Installed equipment—not empty bays" in html
    assert "HR-30_integrated_whole_robot_candidate.step" in html
    assert "battery-energy-source-register.csv" in html and "rear-torso battery cassette" in html
    print(f"PASS: HR-30 has {len(rows)} located equipment/harness/contact items, {status['planning_installed_mass_kg']:.3f} kg provisional installed mass, synchronized STEP/GLB/source-release evidence; no procurement, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
