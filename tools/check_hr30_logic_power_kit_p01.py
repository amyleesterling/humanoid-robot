#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 logic-only power kit P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical/logic-power-kit-p0.1"
RELEASE = ROOT / "release/hr30/whole-body-p0.1/electrical/logic-power-kit-p0.1"
GEN = ROOT / "tools/generate_hr30_logic_power_kit_p01.py"
WARNING = "PRELIMINARY - UNBUILT LOGIC-ONLY POWER FIXTURE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check_manifest() -> None:
    manifest = rows(OUT / "file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    need(listed == actual, "manifest file-set mismatch")
    for row in manifest:
        path = OUT / row["path"]
        need(path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"], f"manifest mismatch {row['path']}")
        need(row["warning"] == WARNING, f"warning drift {row['path']}")
    source = {path.relative_to(OUT).as_posix(): sha(path) for path in OUT.rglob("*") if path.is_file()}
    release = {path.relative_to(RELEASE).as_posix(): sha(path) for path in RELEASE.rglob("*") if path.is_file()}
    need(source == release, "source/release parity failed")


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source or release package missing")
    need((OUT / "logic-power-kit-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    check_manifest()
    sources = rows(OUT / "primary-source-register.csv")
    need(len(sources) == 5 and {row["source_id"] for row in sources} == {f"LP-S0{i}" for i in range(1, 6)}, "primary-source set drift")
    need(any(row["manufacturer"] == "SIGLENT" and "EN03A" in row["revision_or_date"] for row in sources), "SIGLENT datasheet revision missing")
    equipment = rows(OUT / "equipment-register.csv")
    expected = {"SPD3303X", "VHR-2N", "SVH-21T-P1.1", "3051 RD005", "3051 BK005", "5934-2", "5934-0"}
    need(expected <= {row["manufacturer_part_number"] for row in equipment}, "exact candidate parts missing")
    need(all(row["procurement_released"] == "NO" for row in equipment), "procurement must remain unreleased")
    contacts = rows(OUT / "connector-contact-map.csv")
    need(len(contacts) == 2, "contact map must contain exactly two conductors")
    by_destination = {row["destination_contact"]: row for row in contacts}
    need(by_destination["J1.2"]["net"] == "AUX_5V_SAFE" and by_destination["J1.2"]["source_terminal"] == "CH1 +", "positive contact drift")
    need(by_destination["J1.1"]["net"] == "CTRL_GND" and by_destination["J1.1"]["source_terminal"] == "CH1 -", "return contact drift")
    need(all(row["continuity_result"] == row["short_to_other_contact_result"] == "NOT EXECUTED" for row in contacts), "contact map claims execution")
    configuration = {row["configuration_id"]: row for row in rows(OUT / "supply-configuration-register.csv")}
    need(configuration["LP-CFG04"]["candidate_value"] == "5.000 V" and "CANDIDATE ONLY" in configuration["LP-CFG04"]["release_state"], "nominal voltage boundary drift")
    need(all(configuration[key]["candidate_value"] == "SELECTION REQUIRED" for key in ("LP-CFG05", "LP-CFG06", "LP-CFG07")), "released limits were invented")
    need("NO INTENTIONAL BOND" in configuration["LP-CFG08"]["candidate_value"] and "OPEN" in configuration["LP-CFG08"]["release_state"], "reference disposition overclaimed")
    gates, holds, measurements = rows(OUT / "setup-gate-register.csv"), rows(OUT / "open-holds.csv"), rows(OUT / "measurement-register.csv")
    need(len(gates) == 9 and all(row["result"] == "NOT EXECUTED" for row in gates), "gate state drift")
    need(len(holds) == 8 and all(row["state"] == "OPEN" for row in holds), "hold state drift")
    need(len(measurements) == 10 and all(row["measured_value"] == "NONE" for row in measurements), "measurement state drift")
    status = json.loads((OUT / "logic-power-status.json").read_text(encoding="utf-8"))
    need(status["exact_supply_candidate_selected"] is True and status["exact_conductor_and_source_plug_candidates_selected"] is True, "candidate status drift")
    for key in ("supply_received", "cable_built", "output_voltage_setpoint_released", "current_limit_released", "ocp_threshold_released", "dc_reference_disposition_approved", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        need(status[key] is False, f"fail-closed status drift {key}")
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    need("font:17px" in guide and "font-size:16px" in guide, "guide legibility floor missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", guide), "guide includes text below 12 px")
    need("still no permission to plug it in" in guide and "logic-power-boundary.svg" in guide, "guide outcome or diagram missing")
    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(whole_status["logic_power_kit_package_present"] is True and whole_status["logic_power_connection_authority"] is False, "whole-body status integration drift")
    need("electrical/logic-power-kit-p0.1/index.html" in (WHOLE / "README.md").read_text(encoding="utf-8"), "README integration missing")
    need('id="logic-power-kit"' in (WHOLE / "index.html").read_text(encoding="utf-8"), "web integration missing")
    print("PASS: HR-30 logic-only supply/cable candidate, records, guides and fail-closed authority verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
