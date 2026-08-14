"""Fail-closed checks for HR-30 whole-body physical-harness P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "harness" / "physical-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / "physical-p0.1"
WARNING = "PRELIMINARY - PHYSICAL HARNESS ARCHITECTURE ONLY"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def main() -> int:
    status = json.loads((OUT / "physical-harness-status.json").read_text(encoding="utf-8"))
    axes = rows("axis-harness-binding.csv")
    routes = rows("route-segment-register.csv")
    points = rows("route-point-register.csv")
    loops = rows("service-loop-register.csv")
    power = rows("actuator-power-drop-register.csv")
    links = rows("bus-physical-link-register.csv")
    connectors = rows("connector-instance-register.csv")
    contacts = rows("connector-contact-map.csv")
    cores = rows("cable-core-register.csv")
    equipment = rows("equipment-interface-register.csv")
    logical = rows("logical-terminal-binding.csv")
    assemblies = rows("harness-assembly-register.csv")
    terminations = rows("bus-termination-register.csv")
    shields = rows("shield-bond-register.csv")
    retain = rows("retention-strain-relief-register.csv")
    derating = rows("current-derating-register.csv")
    inspections = rows("inspection-test-register.csv")
    unresolved = rows("unresolved-harness-selections.csv")
    source = rows("source-register.csv")

    require(len(axes) == len(loops) == len(power) == len(links) == len(connectors) == len(retain) == len(derating) == 25, "25-axis register spine incomplete")
    require(len(routes) == 62 and len(points) == 124, "route geometry count drift")
    require(Counter(r["segment_kind"] for r in routes) == {"MOVING JOINT LOOP": 50, "FIXED BODY CORRIDOR": 12}, "fixed/moving route split drift")
    require(len(assemblies) == 14 and len(terminations) == len(shields) == 8, "assembly/bus completeness drift")
    with (WB / "electrical/kicad/hr30-whole-body-electrical-p0.1/connector-schedule.csv").open(encoding="utf-8-sig", newline="") as handle:
        ecad_terminals = list(csv.DictReader(handle))
    require(len(equipment) == 54 and len(logical) == len(ecad_terminals), "equipment or logical-terminal binding incomplete")
    require(len(contacts) == len(cores) == 94, "actuator contact/core mapping drift")
    require(len(inspections) >= 10 and len(unresolved) >= 10, "inspection/open-selection registers incomplete")

    axis_ids = {r["axis_id"] for r in axes}
    require(len(axis_ids) == 25, "axis IDs not unique")
    route_ids = {r["segment_id"] for r in routes}
    point_ids = {r["point_id"] for r in points}
    require(len(route_ids) == len(routes) and len(point_ids) == len(points), "route/point IDs not unique")
    for r in routes:
        require(r["from_point"] in point_ids and r["to_point"] in point_ids, f"route point missing for {r['segment_id']}")
        require(float(r["planning_length_mm"]) > 0, f"nonpositive route length {r['segment_id']}")
    for a in axes:
        require(a["power_loop"] in route_ids and a["data_loop"] in route_ids, f"axis loops missing {a['axis_id']}")
        require(a["power_trunk"] in route_ids and a["data_trunk"] in route_ids, f"axis trunk missing {a['axis_id']}")

    bus_axis: dict[str, list[str]] = defaultdict(list)
    for a in axes: bus_axis[a["bus_id"]].append(a["axis_id"])
    require(sorted(len(v) for v in bus_axis.values()) == [1, 2, 2, 2, 3, 3, 6, 6], "eight-bus axis allocation drift")
    require(abs(sum(float(r["candidate_12v_stall_endpoint_a"]) for r in power) - 76.08) < 1e-8, "stall endpoint arithmetic drift")
    require(all("ONE DISTINCT PROTECTION / TELEMETRY BOUNDARY PER ACTUATOR" in r["protection_topology"] for r in power), "25 individual protection boundaries missing")
    require({r["branch_net"] for r in power} == {axis + "_VDD" for axis in axis_ids}, "individual actuator VDD net binding drift")
    require(all("STANDARD DYNAMIXEL CABLE VDD" in r["vdd_isolation_rule"] for r in links), "VDD backfeed boundary missing")

    by_connector = Counter(r["connector_id"] for r in contacts)
    for c in connectors:
        require(by_connector[c["connector_id"]] == int(c["contact_count"]), f"contact count mismatch {c['connector_id']}")
    require({r["core_id"] for r in cores} == {r["wire_core"] for r in contacts}, "contact/core references mismatch")
    require(all(r["physical_connector"] == "SELECTION REQUIRED" for r in equipment), "equipment connector closure overclaimed")
    require(all(r["physical_binding_state"].startswith("LOGICAL TERMINAL RETAINED") for r in logical), "logical terminal lost or overclaimed")

    false_gates = ["standard_dynamixel_cable_direct_use_approved", "assembled_cables_selected", "conductor_sizing_released", "protection_released", "connector_set_released", "harness_validated", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]
    require(all(status[k] is False for k in false_gates), "authority/selection gate overclaimed")
    require(status["total_route_segments"] == 62 and status["logical_terminals"] == len(ecad_terminals), "status count drift")

    for s in source:
        p = ROOT / s["source"]
        require(p.is_file() and sha(p) == s["sha256"], f"source hash mismatch {s['source']}")

    manifest = rows("file-manifest.csv")
    listed = {r["path"] for r in manifest}
    actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
    require(listed == actual, "package manifest file set mismatch")
    for row in manifest:
        p = OUT / row["path"]
        require(p.stat().st_size == int(row["bytes"]) and sha(p) == row["sha256"], f"manifest mismatch {row['path']}")

    src_files = {p.relative_to(OUT).as_posix(): p for p in OUT.rglob("*") if p.is_file()}
    rel_files = {p.relative_to(RELEASE).as_posix(): p for p in RELEASE.rglob("*") if p.is_file()}
    require(src_files.keys() == rel_files.keys(), "release mirror file set mismatch")
    require(all(sha(p) == sha(rel_files[n]) for n, p in src_files.items()), "release mirror byte mismatch")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "whole-body-physical-harness.svg").read_text(encoding="utf-8")
    require("font-size:14px" in page and "font:16px/1.5" in page, "web guide legibility floor missing")
    require(not re.search(r"font-size\s*:\s*(?:[0-9]|1[01])px", page), "web guide contains text below 12 px")
    require(svg.count('class="joint"') == 25 and svg.count('class="route ') == 62, "SVG route/joint completeness drift")
    require(not list(OUT.rglob("*.pdf")), "physical harness package must remain web/register native")

    whole_readme = (WB / "README.md").read_text(encoding="utf-8")
    whole_page = (WB / "index.html").read_text(encoding="utf-8")
    whole_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    require("## Physical whole-body harness P0.1" in whole_readme, "whole-body README integration missing")
    require('href="harness/physical-p0.1/index.html"' in whole_page, "whole-body web guide link missing")
    require(whole_status.get("physical_harness_package_present") is True, "whole-body status integration missing")
    require(whole_status.get("physical_harness_selected") is False and whole_status.get("physical_harness_validated") is False, "whole-body harness status overclaimed")

    print(f"PASS: HR-30 physical harness: 25 separate actuator feeds, 8 data buses, 62 routes, 94 contacts/cores, 54 equipment, {len(logical)} logical terminals; all release/authority gates false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
