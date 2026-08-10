#!/usr/bin/env python3
"""Check the R203 Pi-header allocation without accessing hardware."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "electrical/interfaces/hr-v0-runtime-observation-pi-pinmap-p0.1"
DOC = ROOT / "docs/hr-v0-runtime-observation-pi-pinmap-p0.1.md"
WEB = ROOT / "release/hr-v0/runtime-observation-pi-pinmap-p0.1/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (PACKAGE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    pins = rows("pin-allocation.csv")
    conflicts = rows("conflict-audit.csv")
    harness = rows("harness-interface.csv")
    holds = rows("selection-holds.csv")
    sources = rows("source-register.csv")
    summary = json.loads((PACKAGE / "pinmap-summary.json").read_text(encoding="utf-8"))
    host = json.loads((ROOT / "software/host/hr-v0-host-deploy-p0.1/host-deploy-config.json").read_text(encoding="utf-8"))
    compute = json.loads((ROOT / "firmware/supervisor/compute-interface-config.json").read_text(encoding="utf-8"))
    carrier = rows_from_path(ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/connector-schedule.csv")
    doc = DOC.read_text(encoding="utf-8")
    web = WEB.read_text(encoding="utf-8")

    need(len(pins) == 8, "expected six carrier rows plus heartbeat and return")
    need(len(conflicts) == 8 and len(harness) == 6 and len(holds) == 8 and len(sources) == 4, "package row counts changed")
    need(all(row.get("warning") == WARNING for row in pins + conflicts + harness + holds + sources), "schedule warning changed")

    expected = {
        ("JLOGIC1", "1"): ("17", "N/A", "PI_3V3_CANDIDATE"),
        ("JLOGIC1", "2"): ("20", "N/A", "COMPUTE_0V"),
        ("JLOGIC1", "3"): ("15", "22", "OBS_SR1_PI"),
        ("JLOGIC1", "4"): ("16", "23", "OBS_SRA1_PI"),
        ("JLOGIC1", "5"): ("18", "24", "OBS_K1_PI"),
        ("JLOGIC1", "6"): ("22", "25", "OBS_K2_PI"),
        ("JWH1", "1"): ("11", "17", "PI_HEARTBEAT"),
        ("JWH1", "2"): ("6", "N/A", "COMPUTE_0V"),
    }
    actual = {(r["source_reference"], r["source_terminal"]): (r["physical_header_pin"], r["bcm_rp1_gpio"], r["source_net"]) for r in pins}
    need(actual == expected, "Pi pin allocation changed")
    need(len({r["bcm_rp1_gpio"] for r in pins if r["bcm_rp1_gpio"] != "N/A"}) == 5, "GPIO allocation contains a duplicate")
    need(all(r["logical_polarity"] == "active-high" for r in pins if r["source_reference"] == "JLOGIC1" and r["source_terminal"] in {"3", "4", "5", "6"}), "observation polarity changed")

    carrier_map = {(r["reference"], r["terminal"]): r["net"] for r in carrier}
    for key, (_, _, net) in expected.items():
        if key[0] == "JLOGIC1":
            need(carrier_map.get(key) == net, f"carrier parity changed at {key[0]}.{key[1]}")

    gpio = host["gpio"]
    need(gpio["heartbeat_line"] == 17, "host heartbeat line differs from pin map")
    expected_inputs = {"sr1_status": 22, "sra1_status": 23, "k1_status": 24, "k2_status": 25}
    need({name: item["line"] for name, item in gpio["inputs"].items()} == expected_inputs, "host input lines differ from pin map")
    need(all(item["active_high"] is True for item in gpio["inputs"].values()), "host input polarity differs from pin map")
    need(gpio["chip_path"] == "SELECTION REQUIRED", "target gpiochip path was inferred")
    heartbeat = compute["heartbeat"]
    need((heartbeat["gpio"], heartbeat["physical_header_pin"], heartbeat["return_physical_header_pin"]) == (17, 11, 6), "compute-interface heartbeat binding changed")

    need(summary["identifier"] == "HR-V0-RUNTIME-OBS-PINMAP-P0.1", "summary identifier changed")
    need(summary["mating_connector"] == "SELECTION REQUIRED" and summary["harness"] == "SELECTION REQUIRED", "physical harness was falsely released")
    need(summary["functional_safety_credit"] == "NONE" and summary["connection_authorized"] is False and summary["energization_authorized"] is False, "summary claims prohibited authority")
    need(any("enable_jtag_gpio=1" in row["known_alternate_or_conflict"] for row in conflicts), "JTAG conflict missing")
    need(any("gpiochip" in row["resource"] for row in conflicts), "target gpiochip hold missing")
    need(all(row["state"] == "OPEN" for row in holds), "a local physical-evidence hold was improperly closed")

    combined = doc + web
    for token in (WARNING, "GPIO22", "GPIO23", "GPIO24", "GPIO25", "physical pin 11", "eight local holds remain open", "zero functional-safety credit", "SELECTION REQUIRED"):
        need(token.lower() in combined.lower(), f"documentation boundary missing: {token}")
    need("font:16px/1.55" in web and "font-size:14px" in web, "web guide legibility floor changed")
    need("font-size:13px" not in web and "font-size:12px" not in web, "web guide contains undersized user-facing text")

    if failures:
        print("HR-V0 runtime observation Pi pin map P0.1 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 runtime observation Pi pin map P0.1 check PASS")
    print("  GPIO22/23/24/25 -> header 15/16/18/22; heartbeat GPIO17/header 11 preserved")
    print("  8 local holds open; gpiochip path, harness, target readback and HIL unresolved")
    print(WARNING)
    return 0


def rows_from_path(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    raise SystemExit(main())
