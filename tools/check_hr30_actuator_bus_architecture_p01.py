"""Fail-closed checks for the HR-30 P0.1 mixed-protocol actuator buses."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def rows(name: str) -> list[dict]:
    with (SRC / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    topology = rows("actuator-bus-topology.csv")
    binding = rows("actuator-bus-axis-binding.csv")
    expected_counts = {"RS-LLEG": 6, "RS-RLEG": 6, "RS-LARM": 3, "RS-RARM": 3, "RS-WAIST": 1, "TTL-LDIST": 2, "TTL-RDIST": 2, "TTL-HEAD": 2}
    require(len(topology) == 8 and {r["bus_id"] for r in topology} == set(expected_counts), "exact eight-segment topology missing")
    require({r["bus_id"]: int(r["axis_count"]) for r in topology} == expected_counts, "segment population drift")
    require(len(binding) == 25 and len({r["axis_id"] for r in binding}) == 25, "each of 25 axes must be bound exactly once")
    require(all(r["protocol_compatibility"] == "MATCH" for r in binding), "actuator protocol mismatch")
    rs = [r for r in binding if r["protocol"] == "RS-485 HALF-DUPLEX"]
    ttl = [r for r in binding if r["protocol"] == "TTL HALF-DUPLEX"]
    require(len(rs) == 19 and len(ttl) == 6, "19 RS-485 / 6 TTL split missing")
    require(all(r["actuator_family"] in {"XH540", "XM540", "XM430"} and r["actuator_connector_contacts"] == "4" and "-R" in r["candidate_actuator"] for r in rs), "RS-485 family/variant/contact classification drift")
    require(all(r["actuator_family"] == "XC330" and r["actuator_connector_contacts"] == "3" for r in ttl), "XC330 TTL/contact classification drift")
    require(all(r["actuator_id"] == "SELECTION REQUIRED" and r["connector_pin_mapping"].startswith("SELECTION REQUIRED") for r in binding), "unreleased pins or IDs were inferred")
    require(all("data daisy" in r["branch_power_injection"] for r in binding), "data-only branch-power boundary missing")

    sources = rows("actuator-bus-source-register.csv")
    require(len(sources) == 4 and {r["actuator_family"] for r in sources} == {"XH540", "XM540", "XM430", "XC330"}, "official source family register incomplete")
    require(all(r["manufacturer"] == "ROBOTIS" and r["official_url"].startswith("https://emanual.robotis.com/") and r["accessed_date"] == "2026-08-14" for r in sources), "source authority/date drift")
    require(all("UNRESOLVED" in r["published_revision_or_date"] for r in sources), "unstated document revisions must remain unresolved")

    compute = rows("compute-sensor-network-budget.csv")
    bus_budget = [r for r in compute if r["function"] == "Actuator buses"]
    require(len(bus_budget) == 1 and bus_budget[0]["quantity"] == "8" and "RS-485" in bus_budget[0]["candidate"] and "TTL" in bus_budget[0]["candidate"], "mixed-protocol compute budget missing")
    bom = rows("whole-robot-candidate-bom.csv")
    bus_bom = [r for r in bom if r["item_id"] == "HR30-BOM-010"]
    require(len(bus_bom) == 1 and bus_bom[0]["quantity"] == "8" and "TTL" in bus_bom[0]["candidate"], "mixed-protocol bus BOM missing")

    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_actuator_bus_architecture_present"] and status["protocol_compatibility_screen_complete"], "bus architecture status missing")
    require((status["actuator_bus_segment_count"], status["actuator_bus_axis_binding_count"], status["rs485_actuator_axis_count"], status["ttl_actuator_axis_count"]) == (8, 25, 19, 6), "status bus counts drift")
    require(not any(status[k] for k in ("native_hr30_kicad_reconciled", "actuator_bus_interface_selected", "actuator_bus_connector_harness_validated", "procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "selection/KiCad/authority overclaim")
    holds = rows("open-holds.csv")
    require(any(r["hold_id"] == "HR30-P01-H11" and r["state"] == "OPEN" and "KiCad" in r["unresolved_item"] for r in holds), "electrical integration hold missing")
    doc = (SRC / "whole-body-electrical-integration.md").read_text(encoding="utf-8")
    require("nineteen selected `-R`" in doc and "six XC330" in doc and "not synchronized" in doc and "no connection" in doc.lower(), "electrical integration boundary incomplete")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require(page.count("HR30-ACTUATOR-BUS-P01-START") == 1 and 'id="actuator-buses"' in page and "19 RS-485 axes" in page and "6 TTL axes" in page, "web bus guide missing or duplicated")
    require(sha(SRC / "actuator-bus-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_actuator_bus_architecture_p01.py"), "bus generator snapshot drift")
    src_files = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*") if p.is_file()}
    rel_files = {p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file()}
    require(src_files == rel_files, "source/release file-set mismatch")
    require(all(sha(SRC / name) == sha(REL / name) for name in src_files), "source/release byte mismatch")
    manifest = rows("file-manifest.csv")
    require({r["path"] for r in manifest} == src_files - {"file-manifest.csv"}, "manifest set mismatch")
    require(all(r["warning"] == WARNING and r["sha256"] == sha(SRC / r["path"]) for r in manifest), "manifest hash/warning mismatch")
    print("PASS: all 25 HR-30 axes are bound exactly once to five RS-485 and three TTL segments; physical interfaces, HR-30-only KiCad, validation and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
