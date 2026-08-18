#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 carrier-to-first-axis harness package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "harness" / "carrier-first-axis-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_carrier_first_axis_p01.py"
WARNING = "PRELIMINARY - UNBUILT CARRIER-TO-FIRST-AXIS HARNESS CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


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
    assemblies = rows(OUT / "carrier-first-axis-register.csv")
    contacts = rows(OUT / "contact-map.csv")
    routes = rows(OUT / "route-leg-register.csv")
    bom = rows(OUT / "candidate-bom.csv")
    tests = rows(OUT / "test-plan.csv")
    inspections = rows(OUT / "inspection-register.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "carrier-first-axis-status.json").read_text(encoding="utf-8"))
    need((len(sources), len(assemblies), len(contacts), len(routes), len(bom), len(tests), len(inspections), len(holds)) == (12, 8, 37, 13, 9, 14, 8, 10), "package coverage drift")
    all_rows = sources + assemblies + contacts + routes + bom + tests + inspections + holds
    need(all(row["execution_state"] == "NOT EXECUTED" and row["warning"] == WARNING for row in all_rows), "warning/execution overclaim")
    need(all(row["state"] == "OPEN" for row in holds), "hold falsely closed")
    need(all(row["result"] == "NOT EXECUTED" and row["recorded_result"] == "NONE" for row in tests), "test overclaim")
    need(all(row["result"] == "NOT EXECUTED" and row["serial_number"] == "UNASSIGNED" and row["evidence"] == "NONE" for row in inspections), "inspection overclaim")

    links = [row for row in rows(WHOLE / "harness/physical-p0.1/serial-data-link-register.csv") if row["ordinal"] == "1"]
    expected_buses = {row["bus_id"] for row in links}
    need(len(links) == len(expected_buses) == 8, "ordinal-one source topology drift")
    need({row["bus_id"] for row in assemblies} == expected_buses, "eight-bus assembly coverage drift")
    rs = [row for row in assemblies if row["protocol"].startswith("RS-485")]
    ttl = [row for row in assemblies if row["protocol"].startswith("TTL")]
    need(len(rs) == 5 and len(ttl) == 3, "5 RS / 3 TTL split required")
    need(all(row["carrier_housing_candidate"] == "GHR-03V-S" and row["destination_housing_candidate"] == "EHR-4" and row["field_reference_leg_count"] == "1" for row in rs), "RS connector/reference mapping drift")
    need(all(row["carrier_housing_candidate"] == "GHR-02V-S" and row["destination_housing_candidate"] == "EHR-3" and row["field_reference_leg_count"] == "0" and row["carrier_empty_reference_cavity_count"] == "1" for row in ttl), "TTL connector/reference mapping drift")
    need(all(row["data_conductor_candidate"].startswith("SELECTION REQUIRED") for row in assemblies), "unsupported conductor selected")

    carrier_terms = {(row["reference"], row["pad"]): row["net"] for row in rows(WHOLE / "electrical/carriers-p0.1/carrier-terminal-register.csv")}
    cavity = {(row["connector_id"], row["pin"]): row for row in rows(WHOLE / "harness/actuator-cable-kit-p0.1/connector-cavity-population.csv")}
    by_assembly: dict[str, list[dict[str, str]]] = {}
    for row in contacts:
        by_assembly.setdefault(row["assembly_id"], []).append(row)
    for item in assemblies:
        aid, bus, carrier, dest = item["assembly_id"], item["bus_id"], item["carrier_connector"], item["destination_connector"]
        mapped = by_assembly[aid]
        if bus.startswith("RS-"):
            need(len(mapped) == 5, f"RS contact count drift: {aid}")
            for pin in ("1", "2", "3"):
                row = next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == pin)
                need(carrier_terms[(carrier, pin)] == row["signal"], f"carrier terminal/net drift: {aid}.{pin}")
            need(next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == "1")["to_connector"] == f"RB0-REF-{bus}", f"RS star landing hidden: {aid}")
            need(next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == "2")["to_contact"] == "3", f"RS DP map drift: {aid}")
            need(next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == "3")["to_contact"] == "4", f"RS DN map drift: {aid}")
        else:
            need(len(mapped) == 4, f"TTL contact count drift: {aid}")
            empty = next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == "1")
            need(carrier_terms[(carrier, "1")] == "CTRL_GND" and empty["required_population"] == "EMPTY" and empty["to_connector"] == "NONE", f"TTL duplicate-reference risk: {aid}")
            data = next(row for row in mapped if row["from_connector"] == carrier and row["from_contact"] == "2")
            need(carrier_terms[(carrier, "2")] == data["signal"] and data["to_connector"] == dest and data["to_contact"] == "3", f"TTL data map drift: {aid}")
        need(cavity[(dest, "1")]["physical_role"] == "INDIVIDUAL BRANCH RETURN", f"destination return boundary drift: {aid}")
        need(cavity[(dest, "2")]["physical_role"] == "INDIVIDUAL PROTECTED BRANCH POSITIVE", f"destination VDD boundary drift: {aid}")
        for pin in (("3",) if bus.startswith("TTL-") else ("3", "4")):
            need(cavity[(dest, pin)]["physical_role"] == "SERIAL DATA", f"destination data boundary drift: {aid}.{pin}")

    need(len([row for row in routes if row["service"] == "ISOLATED FIELD REFERENCE"]) == 5, "five RS reference route legs required")
    need(len([row for row in routes if "DATA" in row["service"]]) == 8, "eight data route legs required")
    need(all(row["conductor_candidate"].startswith("SELECTION REQUIRED") and row["route_validation"] == "NOT EXECUTED" for row in routes), "route/conductor overclaim")
    need(any(row["order_code"] == "SSHL-002T-P0.2" and row["planning_quantity"] == "18" for row in bom), "GH contact quantity drift")
    need(any(row["order_code"] == "SEH-001T-P0.6" and row["planning_quantity"] == "13" for row in bom), "EH data-contact quantity drift")
    need(any(row["hold_id"] == "CFA-H02" and "0.25 mm2" in row["unresolved_item"] for row in holds), "RS direct-crimp mismatch hidden")
    need(any(row["hold_id"] == "CFA-H03" and "0.14 mm2" in row["unresolved_item"] for row in holds), "TTL direct-crimp mismatch hidden")

    local = [row for row in sources if row["publisher"] == "Project Button"]
    need(len(local) == 6 and all(row["sha256"] == sha(ROOT / row["official_url_or_path"]) for row in local), "local source hash drift")
    for key, value in {
        "assembly_count": 8, "rs485_assembly_count": 5, "ttl_assembly_count": 3,
        "contact_map_row_count": 37, "route_leg_count": 13,
        "rs_field_reference_leg_count": 5, "ttl_empty_reference_cavity_count": 3,
        "built_assembly_count": 0, "inspected_assembly_count": 0,
        "route_validated_assembly_count": 0, "electrically_tested_assembly_count": 0,
    }.items():
        need(status[key] == value, f"status count drift: {key}")
    for key in ["conductor_selected", "rb0_star_landing_selected", "shield_topology_selected", "crimp_process_selected", "assembly_selected", "procurement_authority", "fabrication_authority", "assembly_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")

    need((OUT / "carrier-first-axis-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    need(sorted(row["path"] for row in manifest) == expected_files, "manifest membership drift")
    need(all(int(row["bytes"]) == (OUT / row["path"]).stat().st_size and row["sha256"] == sha(OUT / row["path"]) for row in manifest), "manifest hash/size drift")
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*") if path.is_file())
    need(source_files == release_files and all(sha(OUT / path) == sha(RELEASE / path) for path in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "carrier-first-axis.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1500px" in page, "web legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:34px" in svg, "drawing legibility drift")
    need("Every carrier now reaches its first joint" in page and "This closes a definition gap" in page, "guide purpose/scope drift")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    need(root_page.count("HR30-CARRIER-FIRST-AXIS-P01-START") == root_page.count("HR30-CARRIER-FIRST-AXIS-P01-END") == 1, "root web integration missing")
    need(root_readme.count("HR30-CARRIER-FIRST-AXIS-P01-README-START") == root_readme.count("HR30-CARRIER-FIRST-AXIS-P01-README-END") == 1, "root README integration missing")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["carrier_first_axis_assembly_count"] == 8 and root_status["carrier_first_axis_contact_map_count"] == 37, "root status integration missing")
    need(root_status["carrier_first_axis_conductor_selected"] is False and root_status["energization_authority"] is False, "root authority drift")
    print("PASS: HR-30 maps all eight carrier-to-first-axis harnesses through 37 controlled contacts, five unique RS field-reference legs and three intentionally empty TTL reference cavities; conductor/crimp/routing/test/authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
