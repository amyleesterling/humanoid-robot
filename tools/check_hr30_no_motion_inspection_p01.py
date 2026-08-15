#!/usr/bin/env python3
"""Fail-closed checks for HR-30 guarded no-motion inspection P0.1."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
STATION = WB / "electrical" / "axis-commissioning-station-p0.1"
OUT = STATION / "no-motion-inspection-p0.1"
REL_STATION = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1"
EXPECTED_MODELS = {"XH540-W270-R", "XM540-W270-R", "XM430-W350-R", "XC330-T288-T"}


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_no_device_write_api(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    forbidden = re.compile(r"(?i)(write[124]bytetxrx|syncwrite|bulkwrite|regwrite|reboot|factoryreset|broadcastping|clearMultiTurn|goal(position|velocity|current|pwm)|torque_enable.*=\s*1)")
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute): names.append(node.attr)
        elif isinstance(node, ast.Name): names.append(node.id)
    hits = sorted(name for name in names if forbidden.search(name))
    assert not hits, f"forbidden DYNAMIXEL device-write API identifiers: {hits}"
    assert "BROADCAST_ID" not in text and "SyncWrite" not in text and "BulkWrite" not in text
    assert "0 <= a.device_id <= 252" in text and "--execute-read-only" in text
    assert set(re.findall(r"packet\.(read[12]ByteTxRx)", text)) == {"read1ByteTxRx", "read2ByteTxRx"}
    assert "packet.ping" in text and "scan" not in {n.lower() for n in names}


def main() -> int:
    status = json.loads((OUT / "inspection-status.json").read_text(encoding="utf-8"))
    assert status["model_count"] == 4 and status["physical_form_factor_count"] == 3
    assert status["sha_bound_vendor_geometry"] and status["guarded_fixture_cad_present"] and status["read_only_inspector_present"]
    assert status["device_write_api_present"] is False and status["broadcast_or_scan_path_present"] is False
    assert status["offline_simulation_passed"] is True
    for key in ("received_fit_validated", "fixture_retention_validated", "software_environment_approved", "hardware_inspection_executed", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False
    fixtures = rows(OUT / "actuator-fixture-register.csv")
    assert len(fixtures) == 4 and {r["model"] for r in fixtures} == EXPECTED_MODELS
    assert {r["form_factor"] for r in fixtures} == {"540", "X430", "XC330"}
    assert all(r["horn_or_body_link_installed"] == "NO" and r["output_guard_present"].startswith("YES") for r in fixtures)
    assert all(r["restraint_state"].startswith("UNVALIDATED") and r["official_source"].startswith("https://docs.robotis.com/") for r in fixtures)
    dimensions = rows(OUT / "fixture-dimension-register.csv")
    assert len(dimensions) == 4
    assert all(float(r["body_xy_clearance_per_side_mm"]) == 2.5 and float(r["output_guard_clearance_above_vendor_bbox_mm"]) == 10.0 for r in dimensions)
    assert all(float(r["cover_wall_mm"]) >= 3 and float(r["bench_hole_diameter_mm"]) == 5.5 for r in dimensions)
    parts = rows(OUT / "fixture-part-register.csv")
    assert len(parts) == 16 and all("REQUIRED" in r["validation"] for r in parts)
    fields = rows(OUT / "inspection-field-register.csv")
    assert len(fields) == 9 and {int(r["address"]) for r in fields} == {0, 6, 7, 8, 13, 64, 70, 144, 146}
    assert all(r["access_used"] == "READ ONLY" for r in fields)
    sources = rows(OUT / "primary-source-register.csv")
    assert len(sources) == 7 and all(r["official_url"].startswith("https://") and r["revision_or_date"] for r in sources)
    check_no_device_write_api(OUT / "hr30_read_only_inspector.py")
    assert "PASS: offline fake transport" in (OUT / "offline-test.log").read_text(encoding="utf-8")
    for fixture in fixtures:
        stem = fixture["model"].lower().replace("-", "_")
        for suffix in ("restraint_base.step", "output_guard.step", "restraint_base.stl", "output_guard.stl", "guarded_fixture.step"):
            p = OUT / f"{stem}_{suffix}"
            assert p.exists() and p.stat().st_size > 1000
        assembly = cq.importers.importStep(str(OUT / f"{stem}_guarded_fixture.step")).val()
        assert assembly.isValid() and assembly.Volume() > 10000
    lineup = cq.importers.importStep(str(OUT / "HR30_four_model_guarded_fixture_lineup.step")).val()
    assert lineup.isValid() and lineup.Volume() > 100000
    assert (OUT / "HR30_four_model_guarded_fixture_lineup.glb").stat().st_size > 5000
    web = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:clamp(16px" in web and "font-size:14px" in web
    assert "Guard the output. Read one ID. Send no motion." in web
    assert "does not authorize energization" not in web.lower() or "not permission to connect" in web.lower()
    assert "overflow:auto" in web and "model-viewer" in web
    station_status = json.loads((STATION / "commissioning-status.json").read_text(encoding="utf-8"))
    assert station_status["no_motion_fixture_design_present"] and station_status["read_only_inspector_present"]
    assert station_status["read_only_inspector_device_write_api_present"] is False and station_status["read_only_inspector_offline_test_passed"] is True
    assert station_status["mechanical_restraint_physically_validated"] is False and station_status["host_software_environment_approved"] is False
    holds = rows(STATION / "open-holds.csv")
    h = {r["hold_id"]:r for r in holds}
    assert h["CS-H06"]["state"] == h["CS-H07"]["state"] == "OPEN"
    assert "received-fit" in h["CS-H06"]["unresolved_evidence"] and "exact DYNAMIXEL SDK version" in h["CS-H07"]["unresolved_evidence"]
    assert (STATION / "index.html").read_text(encoding="utf-8").count("<!-- NO-MOTION-P01 START -->") == 1
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    assert root_status["axis_commissioning_guarded_model_count"] == 4
    assert root_status["axis_commissioning_device_write_api_present"] is False
    assert root_status["axis_commissioning_fixture_physically_validated"] is False and root_status["axis_commissioning_energization_authority"] is False
    assert (WB / "index.html").read_text(encoding="utf-8").count('id="no-motion-inspection"') == 1
    manifest = rows(OUT / "file-manifest.csv")
    assert manifest
    for row in manifest:
        p = OUT / row["path"]
        assert p.exists() and p.stat().st_size == int(row["bytes"]) and sha(p) == row["sha256"]
    station_manifest = {r["path"]:r for r in rows(STATION / "file-manifest.csv")}
    for p in OUT.rglob("*"):
        if p.is_file():
            rel = p.relative_to(STATION).as_posix()
            assert rel in station_manifest and sha(p) == station_manifest[rel]["sha256"]
    src = sorted(p.relative_to(STATION).as_posix() for p in STATION.rglob("*") if p.is_file())
    rel = sorted(p.relative_to(REL_STATION).as_posix() for p in REL_STATION.rglob("*") if p.is_file())
    assert src == rel and all(sha(STATION / p) == sha(REL_STATION / p) for p in src)
    root_manifest = {r["path"]:r for r in rows(WB / "file-manifest.csv")}
    for path in ("README.md", "index.html", "package-status.json", "electrical/axis-commissioning-station-p0.1/no-motion-inspection-p0.1/inspection-status.json"):
        assert path in root_manifest and sha(WB / path) == root_manifest[path]["sha256"]
    print("PASS: four exact-envelope guarded actuator candidates and a single-ID read-only inspector exist; physical approval and all power/motion authority remain open")
    return 0


if __name__ == "__main__": raise SystemExit(main())
