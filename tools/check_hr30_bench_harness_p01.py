#!/usr/bin/env python3
"""Fail-closed checks for HR-30 axis-commissioning bench harness P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
STATION = WB / "electrical" / "axis-commissioning-station-p0.1"
OUT = STATION / "bench-harness-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "axis-commissioning-station-p0.1" / "bench-harness-p0.1"


def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((OUT / "harness-status.json").read_text(encoding="utf-8"))
    assert status["assembly_count"] == 1 and status["conductor_count"] == 2 and status["physical_connector_contact_count"] == 4
    assert status["exact_mini_fit_tool_candidate_selected"] and status["exact_cut_and_strip_definition_present"]
    assert status["assembly_traveler_step_count"] == 10 and status["as_built_record_count"] == 13
    assert status["manufacturer_assembled_source_end_selected"] and status["source_end_termination_process_selected"]
    for key in ("received_lead_compatibility_validated", "physical_assembly_executed", "inspection_executed", "qualified_review_complete", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        assert status[key] is False
    assembly = rows("harness-assembly-register.csv")
    assert len(assembly) == 1 and assembly[0]["assembly_id"] == "BH-A01" and assembly[0]["conductor_count"] == "2"
    prep = rows("conductor-preparation-register.csv")
    assert {r["wire_id"] for r in prep} == {"BH-W01", "BH-W02"}
    assert {r["color"] for r in prep} == {"RED", "BLACK"}
    assert {r["manufacturer_part"] for r in prep} == {"Mueller BU-0061-M-39-2", "Mueller BU-0061-M-39-0"}
    assert all(r["catalog_nominal_length"] == "39 in / 990.6 mm; tolerance not published" and r["j1_strip_length_mm"] == "3.00-3.30" and r["j1_conductor_crimp_height_mm"] == "1.00-1.10" and r["minimum_pull_force_n"] == "88.0" for r in prep)
    assert all("tin-dipped segment" in r["open_end_preparation"] and "no field termination" in r["source_end_preparation"] for r in prep)
    contacts = rows("connector-contact-map.csv")
    assert len(contacts) == 4
    j1 = {r["contact"]: r for r in contacts if r["connector"] == "J1"}
    assert j1["1"]["function"] == "GND" and j1["1"]["wire_id"] == "BH-W02"
    assert j1["2"]["function"] == "VDD" and j1["2"]["wire_id"] == "BH-W01"
    tools = rows("tooling-register.csv")
    assert len(tools) == 5 and any(r["order_code"] == "63819-0901" and "39-00-0038" in r["application"] for r in tools)
    assert any(r["order_code"] == "11-03-0044" and "must not be reused" in r["application"] for r in tools)
    traveler = rows("assembly-traveler.csv")
    assert len(traveler) == 10 and [r["step"] for r in traveler] == [f"A{i:02d}" for i in range(1, 11)]
    assert all(r["state"] == "NOT EXECUTED" and r["stop_rule"] for r in traveler)
    records = rows("as-built-record.csv")
    assert len(records) == 13 and all(r["observed_value"] == "NOT RECORDED" and r["result"] == "OPEN" for r in records)
    assert {r["record_id"] for r in records} == {f"BH-R{i:02d}" for i in range(1, 14)}
    sources = rows("primary-source-register.csv")
    assert len(sources) == 7 and all(r["official_url"].startswith("https://") and r["document"] and r["document_date"] for r in sources)
    assert any(r["source_id"] == "MOLEX-TOOL" and r["document"] == "638190901 Rev D" and r["document_date"] == "2025-03-31" for r in sources)
    assert {r["source_id"] for r in sources} >= {"MUELLER-LEAD", "MUELLER-LIST"}
    holds = rows("open-holds.csv")
    assert len(holds) == 6 and all(r["state"] == "OPEN" and "NO CONNECTION" in r["authority"] for r in holds)
    svg = (OUT / "bench-harness.svg").read_text(encoding="utf-8")
    assert "font-size=\"18\"" in svg and "font-size=\"19\"" in svg and "J1 pin 2 to RED" in svg and "J1 pin 1 to BLACK" in svg
    web = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:clamp(16px" in web and "font-size:14px" in web and "overflow:auto" in web
    assert "Two wires. One keyed input. Zero guessed contacts." in web and "Still not permission to build or connect" in web
    manifest = rows("file-manifest.csv")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    assert {r["path"] for r in manifest} == set(source_files) - {"file-manifest.csv"}
    for row in manifest:
        p = OUT / row["path"]
        assert p.stat().st_size == int(row["bytes"]) and sha(p) == row["sha256"]
    assert source_files == release_files and all(sha(OUT / p) == sha(REL / p) for p in source_files)
    station_status = json.loads((STATION / "commissioning-status.json").read_text(encoding="utf-8"))
    assert station_status["bench_harness_design_present"] and station_status["bench_harness_exact_mini_fit_tool_selected"]
    assert station_status["bench_harness_manufacturer_assembled_source_end_selected"] and station_status["bench_harness_source_end_process_selected"]
    assert not station_status["bench_harness_received_lead_compatibility_validated"] and not station_status["bench_harness_physically_assembled"]
    root_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    assert root_status["axis_commissioning_bench_harness_present"] and root_status["axis_commissioning_bench_harness_contact_map_complete"]
    assert root_status["axis_commissioning_bench_harness_manufacturer_assembled_source_end_selected"]
    assert root_status["axis_commissioning_bench_harness_source_end_process_selected"]
    assert not root_status["axis_commissioning_bench_harness_received_lead_compatibility_validated"]
    assert not root_status["axis_commissioning_bench_harness_physically_validated"]
    assert (STATION / "index.html").read_text(encoding="utf-8").count("<!-- BENCH-HARNESS-P01 START -->") == 1
    assert (WB / "index.html").read_text(encoding="utf-8").count('id="bench-harness"') == 1
    with (WB / "file-manifest.csv").open(encoding="utf-8", newline="") as handle:
        root_manifest = {r["path"]: r for r in csv.DictReader(handle)}
    for path in ("README.md", "index.html", "package-status.json", "electrical/axis-commissioning-station-p0.1/bench-harness-p0.1/harness-status.json"):
        assert path in root_manifest and root_manifest[path]["sha256"] == sha(WB / path)
    print("PASS: HR-30 one-axis station has an exact two-wire Mini-Fit bench-harness traveler and as-built record; physical assembly, qualified approval, and all connection/power authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
