#!/usr/bin/env python3
"""Fail-closed checks for the HR-30 carrier circuit/placement package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "electrical" / "carriers-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    required = [
        OUT / "hr30-actuator-interface-carriers-p0.1.kicad_pro",
        OUT / "hr30-actuator-interface-carriers-p0.1.kicad_sch",
        OUT / "carrier-a" / "hr30-carrier-a-p0.1.kicad_pcb",
        OUT / "carrier-b" / "hr30-carrier-b-p0.1.kicad_pcb",
        OUT / "carrier-component-register.csv",
        OUT / "carrier-terminal-register.csv",
        OUT / "carrier-routing-register.csv",
        OUT / "carrier-configuration-register.csv",
        OUT / "primary-source-register.csv",
        OUT / "carrier-status.json",
        OUT / "README.md",
        OUT / "index.html",
        OUT / "file-manifest.csv",
    ]
    require(all(path.is_file() for path in required), "required carrier artifact missing")
    require(len(list(OUT.glob("*.kicad_sch"))) == 10, "native schematic hierarchy must contain root plus nine child sheets")

    components = rows(OUT / "carrier-component-register.csv")
    require(len(components) == 86, "component register must contain 86 placements")
    require(len({row["reference"] for row in components}) == 86, "component references must be unique")
    require(sum(row["board"] == "A" for row in components) == 49, "Carrier A component count drift")
    require(sum(row["board"] == "B" for row in components) == 37, "Carrier B component count drift")
    require(sum(row["manufacturer_part_number"] == "ISOW1432DFMR" for row in components) == 5, "five ISOW1432 channels required")
    require(sum(row["manufacturer_part_number"] == "SN74LVC1T45DCKR" for row in components) == 3, "three TTL translators required")
    require(sum(row["manufacturer_part_number"] == "SM712-02HTG" for row in components) == 5, "five RS-485 TVS candidates required")
    require(sum(row["manufacturer_part_number"] == "MPZ1005S331ETD25" for row in components) == 10, "two ferrites per isolated channel required")
    require(sum(row["fitted_p0_1"] == "NO / DNP" for row in components) == 8, "five termination jumpers and three TTL idle pull-ups must be DNP")
    require(all(row["warning"] == WARNING for row in components), "component warning drift")

    terminals = rows(OUT / "carrier-terminal-register.csv")
    require(len(terminals) == 297, "terminal register count drift")
    field_refs = {f"J{number}" for number in range(101, 106)} | {f"J20{number}" for number in range(1, 4)}
    for reference in field_refs:
        field = [row for row in terminals if row["reference"] == reference]
        require(field, f"missing field connector {reference}")
        require(not any("VDD" in row["net"] or row["net"] == "CTRL_5V" for row in field), f"{reference} must remain data-only")

    sources = rows(OUT / "primary-source-register.csv")
    require({row["source_id"] for row in sources} == {"TI-ISOW1432", "TI-ISOW-EVM", "TI-LVC1T45", "TI-TPD1E10B06", "TDK-MPZ1005", "LITTELFUSE-SM712", "JST-GH"}, "primary source set drift")
    require(all(row["url"].startswith("https://") for row in sources), "primary source URL missing")

    board_expectations = {"a": (49, 43, 140), "b": (37, 25, 89)}
    for board_id, (part_count, net_count, unconnected) in board_expectations.items():
        path = OUT / f"carrier-{board_id}" / f"hr30-carrier-{board_id}-p0.1.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        require(board.GetCopperLayerCount() == 6, f"Carrier {board_id.upper()} must remain six-layer")
        require(len([fp for fp in board.GetFootprints() if not fp.GetReference().startswith("MH")]) == part_count, f"Carrier {board_id.upper()} placement count drift")
        require(board.GetNetCount() - 1 == net_count, f"Carrier {board_id.upper()} net count drift")
        require(len(list(board.GetTracks())) == 0, f"Carrier {board_id.upper()} must not retain rejected tracks/vias")
        edge_points = []
        for drawing in board.GetDrawings():
            if drawing.GetLayer() == pcbnew.Edge_Cuts:
                edge_points.extend((drawing.GetStart(), drawing.GetEnd()))
        xs = [pcbnew.ToMM(p.x) for p in edge_points]; ys = [pcbnew.ToMM(p.y) for p in edge_points]
        require(round(max(xs) - min(xs), 3) == 82.0 and round(max(ys) - min(ys), 3) == 42.0, f"Carrier {board_id.upper()} outline drift")
        drc = (OUT / "validation" / f"hr30-carrier-{board_id}-p0.1-drc.rpt").read_text(encoding="utf-8")
        require("** Found 0 DRC violations **" in drc, f"Carrier {board_id.upper()} has non-connectivity DRC violations")
        require(f"** Found {unconnected} unconnected pads **" in drc, f"Carrier {board_id.upper()} unrouted count drift")
        require("[shorting_items]" not in drc and "[clearance]" not in drc and "[courtyards_overlap]" not in drc, f"Carrier {board_id.upper()} placement defect present")
        require((OUT / "output" / f"hr30-carrier-{board_id}-p0.1-front.svg").is_file(), f"Carrier {board_id.upper()} front SVG missing")
        require((OUT / "output" / f"hr30-carrier-{board_id}-p0.1-back.svg").is_file(), f"Carrier {board_id.upper()} back SVG missing")
    require(not list(OUT.rglob("*.gbr")) and not list(OUT.rglob("*.drl")), "unrouted package must not publish Gerber or drill files")

    erc = (OUT / "validation" / "hr30-actuator-interface-carriers-p0.1-erc.rpt").read_text(encoding="utf-8")
    require("** ERC messages: 0  Errors 0  Warnings 0" in erc, "carrier schematic ERC must be 0/0")
    status = json.loads((OUT / "carrier-status.json").read_text(encoding="utf-8"))
    for key in ("drc_acceptance", "fabrication_authority", "assembly_authority", "connection_authority", "motion_authority", "energization_authority"):
        require(status[key] is False, f"authority gate {key} must remain false")
    require("unrouted" in (OUT / "README.md").read_text(encoding="utf-8").lower(), "README must disclose unrouted state")
    require("What it is not:</strong> a routed PCB" in (OUT / "index.html").read_text(encoding="utf-8"), "web guide must disclose unrouted state")

    manifest = rows(OUT / "file-manifest.csv")
    manifest_by_path = {row["path"]: row for row in manifest}
    payload = [p for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"]
    require(len(manifest) == len(payload), "carrier manifest file count drift")
    for path in payload:
        rel = path.relative_to(OUT).as_posix(); require(rel in manifest_by_path, f"manifest missing {rel}")
        require(int(manifest_by_path[rel]["bytes"]) == path.stat().st_size and manifest_by_path[rel]["sha256"] == sha256(path), f"manifest mismatch {rel}")

    root_status = json.loads((PACKAGE / "package-status.json").read_text(encoding="utf-8"))
    require(root_status["actuator_interface_carrier_component_count"] == 86, "root package carrier count missing")
    require(root_status["actuator_interface_carrier_routing_complete"] is False, "root package must keep routing open")
    root_page = (PACKAGE / "index.html").read_text(encoding="utf-8")
    require(root_page.count("<!-- HR30-CARRIERS-P01-START -->") == 1 and root_page.count("<!-- HR30-CARRIERS-P01-END -->") == 1, "root web carrier section marker drift")
    holds = rows(PACKAGE / "open-holds.csv")
    h11 = [row for row in holds if row["hold_id"] == "HR30-P01-H11"]
    require(len(h11) == 1 and "Copper routing remains deliberately open" in h11[0]["unresolved_item"], "H11 carrier routing hold missing")
    require(all(not root_status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "whole-body authority boundary changed")
    print("PASS: 86 sourced carrier parts; native schematic ERC 0/0; two clean placement candidates; 229 unrouted connections and all authority held open")


if __name__ == "__main__":
    main()
