#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 inter-axis data-adapter package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "interaxis-data-adapter-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_interaxis_data_adapter_p01.py"
WARNING = "PRELIMINARY - UNBUILT INTER-AXIS DATA ADAPTER CANDIDATE - NOT APPROVED FOR PROCUREMENT, MODIFICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    sources = rows(OUT / "primary-source-register.csv")
    adapters = rows(OUT / "interaxis-adapter-register.csv")
    bom = rows(OUT / "adapter-bom.csv")
    traveler = rows(OUT / "adapter-build-traveler.csv")
    inspections = rows(OUT / "adapter-inspection-register.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "interaxis-data-adapter-status.json").read_text(encoding="utf-8"))
    need((len(sources), len(adapters), len(bom), len(traveler), len(inspections), len(holds)) == (10, 17, 4, 14, 17, 10), "package coverage drift")
    all_rows = sources + adapters + bom + traveler + inspections + holds
    need(all(row["execution_state"] == "NOT EXECUTED" and row["warning"] == WARNING for row in all_rows), "execution/warning overclaim")
    need(all(row["state"] == "OPEN" for row in holds), "hold falsely closed")
    need(all(row["result"] == "NOT EXECUTED" and row["recorded_value"] == "NONE" for row in traveler), "traveler overclaim")
    need(all(row["result"] == "NOT EXECUTED" and row["serial_number"] == "UNASSIGNED" and row["evidence"] == "NONE" for row in inspections), "inspection overclaim")

    links = rows(WHOLE / "harness/physical-p0.1/serial-data-link-register.csv")
    expected = {row["link_id"] for row in links if row["from_endpoint"].startswith("J-OUT-")}
    need(len(expected) == 17 and {row["link_id"] for row in adapters} == expected, "17 inter-axis link coverage drift")
    rs485 = [row for row in adapters if row["protocol"].startswith("RS-485")]
    ttl = [row for row in adapters if row["protocol"].startswith("TTL")]
    need(len(rs485) == 14 and len(ttl) == 3, "14 RS-485 / 3 TTL split required")
    need(all(row["robotis_sku"] == "903-0245-000" and row["nominal_cable_length_mm"] == "240" and row["destination_data_cavities"] == "3,4" for row in rs485), "X4P candidate mapping drift")
    need(all(row["robotis_sku"] == "903-0249-000" and row["nominal_cable_length_mm"] == "180" and row["destination_data_cavities"] == "3" for row in ttl), "X3P candidate mapping drift")
    need(all(row["source_cavity_1"] == row["source_cavity_2"] == "EMPTY" for row in adapters), "upstream power cavity not empty")
    need(all(row["destination_cavity_1"] == "INSERT DEDICATED BRANCH RETURN CONTACT" and row["destination_cavity_2"] == "INSERT DEDICATED BRANCH VDD CONTACT" for row in adapters), "destination branch-power merge missing")
    need(all("REMOVE COMPLETE CONDUCTORS AND FOUR TERMINALS" in row["factory_power_conductors_removed"] for row in adapters), "hidden/cut factory power conductor risk")
    need(all(float(row["nominal_length_minus_axis_spacing_mm"]) > 0 for row in adapters), "nominal cable shorter than axis spacing")

    cavity_rows = rows(WHOLE / "harness/actuator-cable-kit-p0.1/connector-cavity-population.csv")
    indexed = {(row["connector_id"], row["pin"]): row for row in cavity_rows}
    for adapter in adapters:
        for pin in ("1", "2"):
            need(indexed[(adapter["source_connector"], pin)]["required_population"] == "EMPTY", f"source cavity population drift: {adapter['adapter_id']} pin {pin}")
            need(indexed[(adapter["destination_connector"], pin)]["required_population"] == "POPULATED", f"destination power cavity drift: {adapter['adapter_id']} pin {pin}")
        for pin in adapter["destination_data_cavities"].split(","):
            need(indexed[(adapter["destination_connector"], pin)]["required_population"] == "POPULATED", f"destination data cavity drift: {adapter['adapter_id']} pin {pin}")

    local = [row for row in sources if row["publisher"] == "Project Button"]
    need(len(local) == 5 and all(row["sha256"] == sha(ROOT / row["official_url_or_path"]) for row in local), "local source hash drift")
    need(any(row["order_code"] == "903-0245-000" and row["assigned_quantity"] == "14" for row in bom), "X4P BOM quantity missing")
    need(any(row["order_code"] == "903-0249-000" and row["assigned_quantity"] == "3" for row in bom), "X3P BOM quantity missing")
    need(any(row["hold_id"] == "IAD-H09" and "eight carrier-to-first-actuator" in row["unresolved_item"] for row in holds), "carrier-lead boundary hidden")

    need(status["interaxis_adapter_count"] == 17 and status["rs485_x4p_adapter_count"] == 14 and status["ttl_x3p_adapter_count"] == 3, "status count drift")
    need(status["factory_power_conductor_removal_count"] == 34 and status["extracted_factory_terminal_count"] == 68, "removal count drift")
    need(status["destination_branch_power_contact_insertion_count"] == status["upstream_required_empty_power_cavity_count"] == 34, "cavity/contact count drift")
    need(status["carrier_to_first_axis_harness_count_open"] == 8 and status["carrier_to_first_axis_harness_count_in_scope"] == 0, "carrier-lead scope drift")
    for key in ["unmodified_powered_daisy_cable_approved", "extraction_process_selected", "destination_power_contact_process_selected", "adapter_selected", "procurement_authority", "modification_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["built_adapter_count"] == status["inspected_adapter_count"] == status["route_validated_adapter_count"] == status["communication_tested_adapter_count"] == 0, "physical evidence overclaim")

    need((OUT / "interaxis-data-adapter-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(sorted(row["path"] for row in manifest) == expected_files, "manifest membership drift")
    need(all(int(row["bytes"]) == (OUT / row["path"]).stat().st_size and row["sha256"] == sha(OUT / row["path"]) for row in manifest), "manifest hash/size drift")
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    need(source_files == release_files and all(sha(OUT / path) == sha(RELEASE / path) for path in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "interaxis-data-adapter.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1400px" in page, "web legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:34px" in svg, "drawing legibility drift")
    need("Seventeen inter-axis links" in page and "eight controller-to-first-actuator harnesses" in page, "guide purpose/scope drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_page.count("HR30-INTERAXIS-DATA-ADAPTER-P01-START") == root_page.count("HR30-INTERAXIS-DATA-ADAPTER-P01-END") == 1, "root web integration missing")
    need(root_readme.count("HR30-INTERAXIS-DATA-ADAPTER-P01-README-START") == root_readme.count("HR30-INTERAXIS-DATA-ADAPTER-P01-README-END") == 1, "root README integration missing")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["interaxis_data_adapter_count"] == 17 and root_status["interaxis_factory_power_conductor_removal_count"] == 34, "root status integration missing")
    need(root_status["interaxis_data_adapter_selected"] is False and root_status["energization_authority"] is False, "root authority drift")
    print("PASS: HR-30 defines all 17 inter-axis X4P/X3P adaptation candidates with upstream power cavities empty and destination branch-power merge explicit; zero physical work or powered authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
