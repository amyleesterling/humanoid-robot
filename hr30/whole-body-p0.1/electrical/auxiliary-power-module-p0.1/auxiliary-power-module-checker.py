#!/usr/bin/env python3
"""Fail-closed consistency checks for the HR-30 auxiliary-power module."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "auxiliary-power-module-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
WARNING = "PRELIMINARY - UNBUILT AUXILIARY-POWER MODULE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    return list(csv.DictReader((OUT / name).open(encoding="utf-8")))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    status = json.loads((OUT / "auxiliary-power-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR30-AUXILIARY-POWER-MODULE-P0.1", "identifier drift")
    need(status["converter_count"] == status["rail_count"] == 3, "three-rail count drift")
    need(status["candidate_converter_order_codes"] == ["REC30E-2405SZ", "TEN 40-1211E"], "converter order code drift")
    need(status["rec30e_converter_count"] == 2 and status["ten40e_converter_count"] == 1, "converter allocation drift")
    need(status["published_total_capacity_w"] == 100 and status["p0_1_peak_budget_total_w"] == 72, "power budget drift")
    need(status["hmi_peak_headroom_w"] == 10 and status["hmi_zero_peak_headroom_blocker"] is False, "HMI positive-margin correction missing")
    need(status["board_dimensions_mm"] == [150.0, 58.0, 1.6], "board dimensions drift")
    need(status["native_kicad_sheet_count"] == 4, "KiCad sheet count drift")
    need(status["erc_errors"] == status["erc_warnings"] == status["drc_violations"] == status["unconnected_items"] == 0, "native KiCad validation not clean")
    for key in ("protection_values_selected", "secondary_pe_bond_selected", "harness_selected", "thermal_validated", "physical_fit_validated", "procurement_authority", "fabrication_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "walking_authority", "energization_authority"):
        need(status[key] is False, f"unsafe authority/state drift: {key}")

    rails = rows("rail-allocation-register.csv"); need(len(rails) == 3, "rail register count")
    by_id = {row["rail_id"]: row for row in rails}; need(set(by_id) == {"AUX-COMPUTE", "AUX-HMI", "AUX-CONTROL"}, "rail identities")
    need(by_id["AUX-HMI"]["converter"] == "TEN 40-1211E" and by_id["AUX-HMI"]["capacity_margin_w"] == "10" and "POSITIVE COARSE HEADROOM" in by_id["AUX-HMI"]["state"], "HMI margin correction not controlled")
    need(all(row["secondary_return"] == "AUX_0V_STAR" for row in rails), "secondary star drift")
    components = rows("component-register.csv"); need(len(components) == 15, "component count")
    need(sum(row["manufacturer_part_number"] == "REC30E-2405SZ" for row in components) == 2, "REC30E converter count")
    need(sum(row["manufacturer_part_number"] == "TEN 40-1211E" for row in components) == 1, "TEN 40E converter count")
    need(sum(row["manufacturer_part_number"] == "SELECTION REQUIRED" for row in components) == 6, "protection placeholders must remain explicit")
    contacts = rows("connector-contact-map.csv"); need(len(contacts) == 15, "connector contact count")
    need({row["net"] for row in contacts if row["connector"].startswith("JO")} == {"COMPUTE_5V1", "HMI_5V0", "AUX_5V_SAFE", "AUX_0V_STAR"}, "output contact map drift")
    holds = rows("open-holds.csv"); need(len(holds) == 10 and all(row["state"] == "OPEN" for row in holds), "open holds drift")
    need(len(rows("inspection-test-register.csv")) == 8, "test register drift")
    sources = rows("primary-source-register.csv"); need(len(sources) == 5 and any(row["revision_or_date"] == "REV 1/2024" for row in sources) and any(row["revision_or_date"] == "Rev. August 7, 2024" for row in sources), "primary source revision missing")

    erc = (OUT / "validation" / "hr30-auxiliary-power-module-p0.1-erc.rpt").read_text(encoding="utf-8")
    drc = (OUT / "validation" / "hr30-auxiliary-power-module-p0.1-drc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "ERC report not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "DRC report not 0/0")
    need(len(list(OUT.glob("0?_*.kicad_sch"))) == 3 and (OUT / "hr30-auxiliary-power-module-p0.1.kicad_sch").is_file(), "native sheets missing")
    need((OUT / "board" / "hr30-auxiliary-power-module-p0.1.kicad_pcb").is_file(), "native board missing")
    need((OUT / "HR30_AUX.pretty" / "TEN40E.kicad_mod").is_file(), "TEN 40E native footprint missing")
    shape = cq.importers.importStep(str(OUT / "HR30_auxiliary_power_module_candidate.step")).val()
    need(shape.isValid() and shape.Volume() > 10000, "STEP assembly invalid")
    need((OUT / "HR30_auxiliary_power_module_candidate.glb").stat().st_size > 10000, "GLB missing/too small")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    need("The imaginary converter is gone." in page and "model-viewer" in page, "interactive guide drift")
    sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", page)]
    need(not sizes or min(sizes) >= 14, "web text below 14 px")
    need(WARNING in page and WARNING in (OUT / "README.md").read_text(encoding="utf-8"), "warning missing")
    architecture = OUT / "auxiliary-power-architecture.svg"
    svg_root = ET.parse(architecture).getroot()
    need(svg_root.attrib.get("viewBox") == "0 0 1500 820", "architecture SVG view box drift")
    svg_text = architecture.read_text(encoding="utf-8")
    need(all(svg_text.count(label) >= 1 for label in ("COMPUTE_5V1", "HMI_5V0", "AUX_5V_SAFE", "AUX_0V_STAR")), "architecture SVG omits a rail/star label")
    need("translate(0,190)" in svg_text and "translate(0,345)" in svg_text and "translate(0,500)" in svg_text, "architecture SVG lanes do not use the controlled stacked layout")
    svg_sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", svg_text)]
    need(svg_sizes and min(svg_sizes) >= 16, "architecture SVG text below 16 px")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8"); root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_page.count("<!-- HR30-AUXILIARY-POWER-P01-START -->") == 1 and root_page.count("<!-- HR30-AUXILIARY-POWER-P01-END -->") == 1, "root page integration marker drift")
    need(root_readme.count("<!-- HR30-AUXILIARY-POWER-P01-START -->") == 1 and "REC30E-2405SZ" in root_readme and "TEN 40-1211E" in root_readme, "root README integration drift")

    equipment = {row["item_id"]: row for row in csv.DictReader((WHOLE / "installed-equipment-register.csv").open(encoding="utf-8"))}
    aux = equipment["EQ-P01-AUX-CONVERTER"]
    need("2x RECOM REC30E-2405SZ + 1x TRACO POWER TEN 40-1211E" in aux["candidate"], "installed equipment converter mix drift")
    need([float(aux[key]) for key in ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm")] == [150.004, 16.004, 58.004], "installed envelope drift")
    need(abs(float(aux["planning_mass_kg"]) - 0.185) < 1e-9, "installed auxiliary mass drift")
    root_bom = {row["item_id"]: row for row in csv.DictReader((WHOLE / "whole-robot-candidate-bom.csv").open(encoding="utf-8"))}
    need("TEN 40-1211E" in root_bom["HR30-BOM-025"]["candidate"] and "REC30E-2405SZ" in root_bom["HR30-BOM-025"]["candidate"], "whole-robot BOM auxiliary conversion missing")

    manifest = rows("file-manifest.csv"); need(len(manifest) >= 25, "package manifest unexpectedly small")
    listed = {row["path"] for row in manifest}; actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    need(listed == actual, "manifest file set drift")
    for row in manifest:
        path = OUT / row["path"]; need(path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"], f"manifest mismatch {row['path']}")
    source_files = {path.relative_to(OUT).as_posix(): sha(path) for path in OUT.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL).as_posix(): sha(path) for path in REL.rglob("*") if path.is_file()}
    need(source_files == release_files, "source/release package parity failure")
    print(f"PASS: three-rail HR-30 auxiliary module; 2x REC30E-2405SZ + 1x TEN 40-1211E; HMI coarse headroom 10 W; ERC/DRC 0/0; {len(holds)} holds open; no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
