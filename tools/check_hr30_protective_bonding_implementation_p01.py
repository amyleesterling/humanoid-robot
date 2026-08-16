#!/usr/bin/env python3
"""Fail-closed validation for the HR-30 protective-bonding candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "electrical" / "protective-bonding-implementation-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / OUT.name
GEN = ROOT / "tools" / "generate_hr30_protective_bonding_implementation_p01.py"
WARNING = "PRELIMINARY - UNBUILT BONDING IMPLEMENTATION CANDIDATE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"


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
    bindings = rows(OUT / "source-binding.csv")
    site = rows(OUT / "site-jurisdiction-basis.csv")
    hardware = rows(OUT / "bond-hardware-register.csv")
    sizing = rows(OUT / "conductor-sizing-basis.csv")
    zones = rows(OUT / "robot-bond-zone-register.csv")
    bypasses = rows(OUT / "joint-bypass-obligation.csv")
    traveler = rows(OUT / "installation-traveler.csv")
    tests = rows(OUT / "inspection-measurement-plan.csv")
    holds = rows(OUT / "open-holds.csv")
    status = json.loads((OUT / "physical-bond-status.json").read_text(encoding="utf-8"))

    need(len(sources) == 8 and len(bindings) == 5 and len(site) == 5, "source/site coverage drift")
    need(len(hardware) == 9 and len(sizing) == 10, "hardware/sizing coverage drift")
    need(len(zones) == 13 and len(bypasses) == 14, "whole-body bond coverage drift")
    need(len(traveler) == 16 and len(tests) == 12 and len(holds) == 10, "traveler/test/hold coverage drift")
    need(all(r["execution_state"] == "NOT EXECUTED" and r["warning"] == WARNING for group in [sources, bindings, site, hardware, sizing, zones, bypasses, traveler, tests, holds] for r in group), "execution/warning overclaim")
    need(all(r["installed"] == "NO" and r["measured"] == "NO" for r in zones), "bond installation overclaim")
    need(all(r["complete"] == "NO" and r["record"] == "NONE" for r in traveler), "installation traveler overclaim")
    need(all(r["result"] == "NOT EXECUTED" and r["measured_value"] == "NONE" for r in tests), "measurement overclaim")
    need(all(r["state"] == "OPEN" for r in holds), "hold falsely closed")
    need(all(r["bearing_or_joint_conductivity_credited"] == "NO" and r["worst_pose_tested"] == "NO" for r in bypasses), "joint bond credit/test overclaim")
    need(all(r["calculation_released"] == "NO" and r["current_value"] == "SELECTION REQUIRED" for r in sizing), "conductor sizing invented")
    need(all(r["procurement_released"] == "NO" for r in hardware), "hardware procurement overclaim")

    by_id = {r["hardware_id"]: r for r in hardware}
    need(by_id["PB-HW03"]["manufacturer"] == "Phoenix Contact" and "3044173" in by_id["PB-HW03"]["candidate"], "UT 10-PE selection drift")
    need(by_id["PB-HW04"]["manufacturer"] == "Alpha Wire" and "460619" in by_id["PB-HW04"]["candidate"] and "SELECTION REQUIRED" in by_id["PB-HW04"]["candidate"], "Alpha candidate/order-code boundary drift")
    need(by_id["PB-HW05"]["manufacturer"] == "Anderson Power" and "1340G1" in by_id["PB-HW05"]["candidate"], "SBS pre-mate candidate drift")
    need(by_id["PB-HW07"]["manufacturer"] == "SELECTION REQUIRED" and by_id["PB-HW08"]["manufacturer"] == "SELECTION REQUIRED", "moving jumper or BR1 hardware invented")
    need(any("discontinuation" in r["verified_scope"] for r in sources if r["source_id"] == "PB-S03"), "Hammond availability caveat missing")
    need(any("applicability" in r["verified_scope"] for r in sources if r["source_id"] in {"PB-S01", "PB-S02"}), "jurisdiction applicability caveat missing")
    need(all(r["sha256"] == sha(ROOT / r["path"]) and int(r["bytes"]) == (ROOT / r["path"]).stat().st_size for r in bindings), "source-binding drift")

    for key in ["moving_joint_jumper_selected", "conductor_sizing_released", "br1_hardware_selected", "procurement_authority", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"]:
        need(status[key] is False, f"fail-closed status violated: {key}")
    need(status["installed_bond_count"] == status["executed_measurement_count"] == status["qualified_signoff_count"] == 0, "physical evidence overclaim")
    need(status["candidate_panel_pe_terminal_selected"] and status["candidate_tether_pe_contact_selected"] and status["candidate_fixed_panel_conductor_family_selected"], "defensible candidate progress missing")

    need((OUT / "protective-bonding-source.py").read_bytes() == GEN.read_bytes(), "generator snapshot drift")
    manifest = rows(OUT / "file-manifest.csv")
    expected = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(sorted(r["path"] for r in manifest) == expected, "manifest membership drift")
    need(all(int(r["bytes"]) == (OUT / r["path"]).stat().st_size and r["sha256"] == sha(OUT / r["path"]) for r in manifest), "manifest hash/size drift")
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*") if p.is_file())
    need(source_files == release_files and all(sha(OUT / p) == sha(RELEASE / p) for p in source_files), "source/release parity drift")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    svg = (OUT / "protective-bonding-layout.svg").read_text(encoding="utf-8")
    need("font:17px" in page and "font-size:16px" in page and "min-width:1000px" in page, "web guide legibility/overflow drift")
    need("font-size:16px" in svg and "font-size:31px" in svg, "drawing legibility drift")
    need("The grounding topology now has an installable candidate kit" in page, "guide purpose drift")
    need("HR30-PROTECTIVE-BONDING-P01-START" in (WHOLE / "index.html").read_text(encoding="utf-8"), "root web integration missing")
    root_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(root_status["protective_bonding_hardware_record_count"] == 9 and root_status["protective_bonding_joint_bypass_count"] == 14, "root status integration missing")
    need(root_status["protective_bonding_approved"] is False and root_status["energization_authority"] is False, "root authority overclaim")
    print("PASS: HR-30 physical protective-bonding candidate has 9 hardware records, 13 bond zones, 14 joint bypasses, 0 installations, 0 measurements, and no work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
