#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 tether power-core P0.1 package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "electrical" / "tether-power-core-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "electrical" / "tether-power-core-p0.1"
PROJECT = "hr30-tether-power-core-p0.1"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((OUT / "power-core-status.json").read_text(encoding="utf-8"))
    assert status["native_sheet_count"] == 7 and status["child_sheet_count"] == 6
    assert status["erc_errors"] == status["erc_warnings"] == 0
    assert status["external_contactor_count"] == 2 and status["on_robot_contactor_count"] == 0
    assert status["robot_pdu_feed_count"] == 5 and status["fuse_holder_count"] == 6
    assert status["fuse_values_selected"] is False and status["final_conductors_selected"] is False
    assert all(status[key] is False for key in ("functional_safety_approved", "fabrication_authority", "connection_authority", "powered_test_authority", "motion_authority", "energization_authority"))

    sheets = list(OUT.glob("*.kicad_sch"))
    assert len(sheets) == 7 and (OUT / f"{PROJECT}.kicad_pro").exists()
    erc = (OUT / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    assert "0  Errors 0  Warnings" in erc
    netlist = (OUT / "validation" / f"{PROJECT}.net").read_text(encoding="utf-8")
    for ref in ("PS1", "PS2", "SR1", "K1", "K2", "XT1A", "XT1B", "FM0", "FB1", "FB2", "FB3", "FB4", "FB5"):
        assert f'(ref "{ref}")' in netlist or f"(ref {ref})" in netlist

    sources = rows("primary-source-register.csv")
    assert {r["source_id"] for r in sources} == {"RSP", "SD", "PNOZ", "GV12", "SBS", "MIDI", "HAMMOND", "PHOENIX"}
    assert all(r["official_url"].startswith("https://") and r["document_revision_or_date"] for r in sources)
    branches = rows("five-pdu-feed-register.csv")
    assert [r["board_instance"] for r in branches] == ["PDU-LLEG", "PDU-RLEG", "PDU-ARMS", "PDU-DISTAL", "PDU-CORE"]
    assert abs(sum(float(r["published_actuator_stall_endpoint_sum_a"]) for r in branches) - 76.08) < 1e-9
    assert all(r["fuse_order_code"] == r["fuse_value_a"] == "SELECTION REQUIRED" for r in branches)
    assert all(r["holder_order_code"] == "04980923ZXT" and r["terminal_nominal_current_a"] == "32" for r in branches)
    contacts = rows("connector-contact-map.csv")
    assert len(contacts) == 3 and [r["project_cavity"] for r in contacts] == ["P1", "G center", "P2"]
    assert "1340G1" in contacts[1]["contact_candidate"] and all(r["physical_validation"] == "NOT EXECUTED" for r in contacts)
    holds = rows("open-holds.csv")
    assert len(holds) == 10 and all(r["state"] == "OPEN" and "NO PROCUREMENT" in r["authority"] for r in holds)

    panel = cq.importers.importStep(str(OUT / "HR30_external_tether_panel_candidate.step")).val()
    robot = cq.importers.importStep(str(OUT / "HR30_robot_five_branch_distributor_candidate.step")).val()
    assert panel.isValid() and panel.Volume() > 1e6
    assert robot.isValid() and robot.Volume() > 1e4
    assert (OUT / "HR30_external_tether_panel_candidate.glb").stat().st_size > 10000
    assert (OUT / "HR30_robot_five_branch_distributor_candidate.glb").stat().st_size > 10000

    equipment = list(csv.DictReader((WB / "installed-equipment-register.csv").open(encoding="utf-8")))
    ids = {r["item_id"] for r in equipment}
    assert "EQ-P01-DUAL-INTERRUPT" not in ids
    assert {"EQ-P01-TETHER-INLET", "EQ-P01-FIVE-BRANCH-DISTRIBUTOR"} <= ids
    assert sum(i.startswith("EQ-PDU-") for i in ids) == 5
    package = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    assert package["external_contactor_count"] == 2 and package["on_robot_contactor_count"] == 0
    assert package["robot_pdu_feed_count"] == 5 and package["tether_power_core_energization_authority"] is False

    web = (OUT / "index.html").read_text(encoding="utf-8")
    assert "font:clamp(16px" in web and "small{font-size:14px}" in web
    assert "Fuse values are intentionally absent" in web and "The contactors are outside the robot" in web
    assert "HR30_external_tether_panel_candidate.glb" in web and web.count("<details>") == 6
    main_web = (WB / "index.html").read_text(encoding="utf-8")
    assert main_web.count('id="tether-power-core"') == 1 and "No fuse values released" in main_web

    manifest = rows("file-manifest.csv")
    assert manifest
    for row in manifest:
        path = OUT / row["path"]
        assert path.exists() and path.stat().st_size == int(row["bytes"]) and sha(path) == row["sha256"]
    source_files = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    release_files = sorted(p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file())
    assert source_files == release_files
    assert all(sha(OUT / name) == sha(REL / name) for name in source_files)
    print("PASS: HR-30 tether power core has 7 native KiCad sheets at ERC 0/0, external dual interruption, one touch-safe tether and five protected PDU feeds; all fuse values, conductors, safety approval and work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
