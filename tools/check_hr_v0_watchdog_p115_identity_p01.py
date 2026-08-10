#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-WD-P115-ID-P0.1 / R195."""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def main() -> None:
    failures: list[str] = []
    def need(value: bool, message: str) -> None:
        if not value:
            failures.append(message)

    board_text = (ROOT / "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb").read_text(encoding="utf-8-sig")
    assembly = ROOT / "electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2"
    assembly_status = json.loads((assembly / "package-status.json").read_text(encoding="utf-8"))
    structural = json.loads((assembly / "p0.8-p1.0-geometry-topology-parity.json").read_text(encoding="utf-8"))
    assembly_parity = rows(assembly / "assembly-parity-p0.7-to-p1.0.csv")
    cam = json.loads((ROOT / "release/hr-v0/watchdog-pcb-cam-p0.2/package-status.json").read_text(encoding="utf-8"))
    e2 = json.loads((ROOT / "release/hr-v0/e2-hardware-p0.4/e2-hardware-summary.json").read_text(encoding="utf-8"))
    release = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    gates = rows(ROOT / "requirements/hr-v0-gate-evidence-supplement-r195.csv")
    doc = (ROOT / "docs/hr-v0-watchdog-p115-identity-correction-p0.1.md").read_text(encoding="utf-8")
    page = (ROOT / "release/hr-v0/watchdog-p115-identity-p0.1/index.html").read_text(encoding="utf-8")

    need('rev "PCB-P1.0 / Electrical V3-P1.15"' in board_text, "native PCB title is not direct P1.15")
    need(assembly_status.get("board") == "PCB-P1.0 / Electrical V3-P1.15", "assembly package identity changed")
    need(structural.get("geometry_topology_equal") is True and structural.get("copper_changed") is False and structural.get("placement_changed") is False and structural.get("nets_changed") is False, "structural parity is not fail-closed")
    need(len(assembly_parity) == 46 and all(row["overall_match"] == "TRUE" for row in assembly_parity), "assembly parity is not 46/46")
    need(cam.get("native_board_title_revision") == "PCB-P1.0 / Electrical V3-P1.15" and cam.get("direct_p115_binding") is True and cam.get("p115_parity_evidence") is None, "CAM still depends on the parity exception")
    need(cam.get("open_holds") == 18 and cam.get("cam_released") is False and cam.get("energization_authorized") is False, "CAM hold boundary changed")
    need(e2.get("configuration_binding") == "PCB-P1.0 / Electrical V3-P1.15" and e2.get("p115_direct_binding_verified_by_checker") is True, "E2 direct binding missing")
    need(e2.get("blocking_holds") == 12 and e2.get("run_authorized") is False and e2.get("energization_authorized") is False, "E2 fail-closed boundary changed")
    electrical = next((item for item in release["current_products"] if item.get("domain") == "electrical"), {})
    need(electrical.get("correction_identifier") == "HR-V0-WD-P115-ID-P0.1" and "PCB-P1.0-P1.15-DIRECT" in electrical.get("supporting_identifiers", []) and "HR-V0-E2-P115-PARITY-P0.1" not in electrical.get("supporting_identifiers", []), "release candidate current identity changed")
    need(any(item.get("identifier") == "HR-V0-E2-P115-PARITY-P0.1" for item in release["historical_or_out_of_scope_products"]), "historical parity evidence not retained")
    need({row["gate_id"] for row in gates} == {"EG-002", "EG-004"} and all(row["state"] == "REMAINS PARTIAL" for row in gates), "R195 gate disposition changed")
    combined = doc + page
    for token in ("HR-V0-WD-P115-ID-P0.1", "PCB-P1.0", "Electrical V3-P1.15", "46/46", "18", "EG-002", "EG-004", WARNING):
        need(token in combined, f"missing controlled token {token}")
    need("font:16px" in page and "font-size:14px" in page, "interactive guide text floors missing")
    need('data-view="before"' in page and 'data-view="after"' in page, "interactive comparison missing")
    need(not re.search(r"(?:font-size|font):\s*1[123]px", page), "undersized CSS text declaration found")

    if failures:
        raise SystemExit("HR-V0 watchdog P1.15 identity check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 watchdog P1.15 identity check passed: PCB-P1.0 direct binding, 46/46 assembly parity, 18 CAM holds and 12 E2 holds")
    print("EG-002 and EG-004 remain partial; no fabrication, connection, motion or energization authority exists")
    print(WARNING)

if __name__ == "__main__":
    main()
