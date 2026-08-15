#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 axis commissioning station P0.1."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "electrical" / "axis-commissioning-station-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1"
PROJECT = "hr30-axis-commissioning-station-p0.1"


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((OUT / "commissioning-status.json").read_text(encoding="utf-8"))
    assert status["native_sheet_count"] == 5 and status["child_sheet_count"] == 4
    assert status["erc_errors"] == status["erc_warnings"] == 0
    assert status["axis_count"] == 25 and status["simultaneous_actuator_limit"] == 1
    assert status["candidate_first_power_voltage_v"] == 11.0
    assert status["candidate_first_power_current_limit_a"] == 0.25
    assert status["absolute_station_configuration_current_a"] == 2.0
    assert status["torque_or_motion_command_permitted"] is False
    assert status["whole_body_power_role"] == status["walking_power_role"] == "REJECT"
    for key in ("physical_validation_complete", "qualified_procedure_approved", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False
    assert len(list(OUT.glob("*.kicad_sch"))) == 5
    assert (OUT / f"{PROJECT}.kicad_pro").exists()
    assert "0  Errors 0  Warnings" in (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    matrix = rows("axis-commissioning-matrix.csv")
    assert len(matrix) == 25
    assert [int(row["proposed_global_id"]) for row in matrix] == list(range(1, 26))
    assert len({row["axis_id"] for row in matrix}) == 25
    assert all(row["initial_voltage_v"] == "11.0" and row["initial_current_limit_a"] == "0.25" for row in matrix)
    assert all(row["first_power_motion_command"] == "PROHIBITED" and row["execution_result"] == "NOT EXECUTED" for row in matrix)
    assert sum("X4P" in row["station_cable"] for row in matrix) == 19
    assert sum("X3P" in row["station_cable"] for row in matrix) == 6
    sources = rows("primary-source-register.csv")
    assert {r["source_id"] for r in sources} == {"KEYSIGHT", "U2D2", "PHB", "X4P", "X3P", "MOLEX", "LEAD", "LEAD-LIST", "XH540", "XM540", "XM430", "XC330"}
    assert all(r["official_url"].startswith("https://") and r["document_revision_or_date"] for r in sources)
    assert any(r["source_id"] == "MOLEX" and "638190901 Rev D" in r["document_revision_or_date"] for r in sources)
    assert any(r["source_id"] == "LEAD" and "18 AWG" in r["verified_scope"] and "tin-dipped" in r["verified_scope"] for r in sources)
    bom = rows("candidate-bom.csv")
    assert len(bom) == 10 and {r["order_code"] for r in bom} >= {"E36313A", "902-0132-000", "902-0145-001", "903-0244-000", "903-0249-000", "39-01-2020", "39-00-0038", "BU-0061-M-39-2", "BU-0061-M-39-0"}
    contacts = rows("connector-contact-map.csv")
    assert len(contacts) == 6 and contacts[2]["contact"] == "1" and contacts[2]["function"] == "GND" and contacts[3]["contact"] == "2" and contacts[3]["function"] == "VDD"
    settings = rows("controlled-settings.csv")
    assert any(r["setting"] == "actuator population" and r["value"] == "exactly one" for r in settings)
    assert any(r["setting"] == "Torque Enable" and r["value"] == "0 readback" for r in settings)
    procedure = rows("first-power-procedure.csv")
    assert len(procedure) == 11 and all(r["execution"] == "NOT EXECUTED" and "NO CONNECTION" in r["authority"] for r in procedure)
    holds = rows("open-holds.csv")
    assert len(holds) == 8 and all(r["state"] == "OPEN" for r in holds)
    step = cq.importers.importStep(str(OUT / "HR30_axis_commissioning_station_candidate.step")).val()
    assert step.isValid() and step.Volume() > 100000
    assert (OUT / "HR30_axis_commissioning_station_candidate.glb").stat().st_size > 5000
    assert (OUT / "HR30_axis_commissioning_tray_candidate.stl").stat().st_size > 1000
    assert (OUT / "HR30_axis_commissioning_cover_candidate.stl").stat().st_size > 1000
    web = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:clamp(16px" in web and "font-size:14px" in web
    assert "First power, one actuator at a time" in web and "does not authorize energization" in web
    drawing_refs = [html.unescape(path) for path in re.findall(r'data="output/([^"]+\.svg)"', web)]
    assert len(drawing_refs) == 4 and len(set(drawing_refs)) == 4
    assert all((OUT / "output" / path).is_file() for path in drawing_refs)
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    assert root_status["axis_commissioning_station_present"] is True
    assert root_status["axis_commissioning_axis_count"] == 25
    assert root_status["axis_commissioning_proposed_global_id_count"] == 25
    assert root_status["axis_commissioning_physically_validated"] is False
    assert root_status["axis_commissioning_energization_authority"] is False
    assert (WB / "index.html").read_text(encoding="utf-8").count('id="axis-commissioning"') == 1
    manifest = rows("file-manifest.csv")
    assert manifest
    for row in manifest:
        path = OUT / row["path"]
        assert path.exists() and path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"]
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    assert source_files == release_files
    assert all(sha(OUT / path) == sha(REL / path) for path in source_files)
    root_manifest = rows("../file-manifest.csv") if False else list(csv.DictReader((WB / "file-manifest.csv").open(encoding="utf-8")))
    indexed = {r["path"]: r for r in root_manifest}
    for path in ("README.md", "index.html", "package-status.json", "electrical/axis-commissioning-station-p0.1/commissioning-status.json"):
        assert path in indexed and sha(WB / path) == indexed[path]["sha256"]
    print("PASS: HR-30 has a native 5-sheet, 25-axis, one-actuator current-limited commissioning station candidate; first power remains unexecuted and unauthorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
