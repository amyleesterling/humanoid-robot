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
    assert status["installed_item_count"] == len(rows) == 64
    assert status["empty_component_bays_replaced"] is True
    assert status["tether_first_configuration"] is True
    assert status["tether_development_interface_retained"] is True
    assert status["onboard_energy_candidate_geometry_present"] is True
    assert status["onboard_energy_installed"] is False
    assert status["exact_selections_closed"] is False
    assert status["energization_authority"] is False
    assert abs(sum(float(row["planning_mass_kg"]) for row in rows) - status["planning_installed_mass_kg"]) < 1e-5
    ids = {row["item_id"] for row in rows}
    required = {
        "EQ-T01-PI5", "EQ-T01-MOTION", "EQ-T01-WATCHDOG", "EQ-T01-BUS-CARRIER-A", "EQ-T01-BUS-CARRIER-B", "EQ-P01-TETHER-INLET",
        "EQ-P01-EIGHT-BRANCH-DISTRIBUTOR", "EQ-WPS-RS-LLEG", "EQ-WPS-RS-RLEG", "EQ-WPS-RS-LARM", "EQ-WPS-RS-RARM", "EQ-WPS-RS-WAIST", "EQ-WPS-TTL-LDIST", "EQ-WPS-TTL-RDIST", "EQ-WPS-TTL-HEAD", "EQ-P01-IMU", "EQ-H01-DISPLAY",
        "EQ-H01-CAMERA-L", "EQ-H01-CAMERA-R", "EQ-H01-MIC-ARRAY",
        "EQ-H01-SPEAKER-L", "EQ-H01-SPEAKER-R", "EQ-F01-SOLE", "EQ-F02-SOLE",
        "EQ-T01-BATTERY-PACK", "EQ-T01-BATTERY-CASSETTE", "EQ-T01-BATTERY-PROTECTION",
        "EQ-T01-TTL-REG-LDIST", "EQ-T01-TTL-REG-RDIST", "EQ-T01-TTL-REG-HEAD",
    }
    assert required <= ids
    assert "EQ-P01-DUAL-INTERRUPT" not in ids
    assert any(row["item_id"] == "EQ-P01-EIGHT-BRANCH-DISTRIBUTOR" and "nine Littelfuse 04980923ZXT" in row["candidate"] for row in rows)
    assert any(row["item_id"] == "EQ-P01-TETHER-INLET" and "SBS75GBLK" in row["candidate"] for row in rows)
    assert "EQ-P01-PDU" not in ids
    pdu_rows = [row for row in rows if row["item_id"].startswith("EQ-WPS-")]
    assert len(pdu_rows) == 8 and abs(sum(float(row["planning_mass_kg"]) for row in pdu_rows) - 0.360) < 1e-9
    assert all(sorted((round(float(row["bbox_x_mm"])), round(float(row["bbox_z_mm"])))) == [45, 124] for row in pdu_rows)
    assert all("ERC 0/0" in row["evidence_state"] and "PCB" in row["evidence_state"] for row in pdu_rows)
    ttl_reg_rows = [row for row in rows if row["item_id"].startswith("EQ-T01-TTL-REG-")]
    assert len(ttl_reg_rows) == 3 and all("S18V20F9" in row["candidate"] for row in ttl_reg_rows)
    assert not any(item.startswith("EQ-T01-U2D2-") for item in ids)
    assert sum(item.startswith("EQ-T01-BUS-CARRIER-") for item in ids) == 2
    assert sum("LOAD-" in item for item in ids) == 8
    assert sum(item.startswith("EQ-HN01_") for item in ids) == 12
    assert any("raspberrypi.com" in row["manufacturer_source_url"] for row in sources)
    assert not any("u2d2" in row["manufacturer_source_url"].lower() for row in sources)
    assert any("waveshare.com" in row["manufacturer_source_url"] for row in sources)
    assert any("grepow.com" in row["manufacturer_source_url"] for row in sources)
    assert len(battery) == 1 and battery[0]["model"] == "TAA12K4S30EC5" and battery[0]["selection_state"].startswith("REJECTED DIRECT SOURCE")
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
    assert "battery-energy-source-register.csv" in html and "rejected legacy geometry; tether-first is primary" in html
    print(f"PASS: HR-30 has {len(rows)} located equipment items including eight isolated one-bus walking-power boards, {status['planning_installed_mass_kg']:.3f} kg provisional installed mass, synchronized STEP/GLB/source-release evidence; no procurement, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
