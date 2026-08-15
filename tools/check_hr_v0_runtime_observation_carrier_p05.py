#!/usr/bin/env python3
"""Independently check R211/P0.5 open-drain observation carrier."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.5"
PROJECT = "hr-v0-runtime-observation-carrier-p0.5"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.5.md"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.5/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
CHANNELS = ((1, "SR1", "3"), (2, "SRA1", "4"), (3, "K1", "5"), (4, "K2", "6"))


def rows(name: str) -> list[dict[str, str]]:
    with (ECAD / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def close(actual: float, expected: float, tolerance: float = .001) -> bool:
    return math.isclose(actual, expected, abs_tol=tolerance)


def main() -> int:
    failures: list[str] = []
    def need(condition: bool, message: str) -> None:
        if not condition: failures.append(message)

    need(len(list(ECAD.glob("*.kicad_sch"))) == 5, "expected root plus four native sheets")
    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    drc = (ECAD / f"validation/{PROJECT}-drc.rpt").read_text(encoding="utf-8-sig")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "ERC is not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc and "Found 0 Footprint errors" in drc, "DRC is not clean")

    connector, bom, sources = rows("connector-schedule.csv"), rows("bom.csv"), rows("source-register.csv")
    holds, loads, placements = rows("selection-holds.csv"), rows("load-budget.csv"), rows("pcb-placement.csv")
    need(len(connector) == 146 and len(bom) == 49 and len(placements) == 53, "controlled schedule membership changed")
    need(len(holds) == 14, "fourteen evidence holds must remain open")
    need(all(row.get("warning") == WARNING for row in connector + bom + sources + holds + loads + placements), "controlled warning missing")
    for source_id in ("OBS5-SRC-016", "OBS5-SRC-017", "OBS5-SRC-020", "OBS5-SRC-022", "OBS5-SRC-023", "OBS5-SRC-024", "OBS5-SRC-025"):
        need(any(row["source_id"] == source_id for row in sources), f"source binding missing: {source_id}")

    nodes = {(row["reference"], row["terminal"]): row["net"] for row in connector}; values = {row["reference"]: row["value"] for row in bom}
    board = pcbnew.LoadBoard(str(ECAD / f"{PROJECT}.kicad_pcb")); footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for index, name, jpin in CHANNELS:
        ref = f"UBUF{index}"; fp = footprints[ref]; pads = {pad.GetNumber(): pad for pad in fp.Pads()}
        need(fp.GetFPID().GetLibItemName() == "TI_DBV0005A_SOT23_5", f"{ref} footprint identity changed")
        need("SN74LVC1G07DBVR" in values.get(ref, "") and "SN74LVC1G125" not in values.get(ref, ""), f"{ref} exact open-drain candidate changed")
        need(len(pads) == 5 and all(close(mm(p.GetSize().x), 1.10) and close(mm(p.GetSize().y), .60) for p in pads.values()), f"{ref} land geometry changed")
        need(close(abs(mm(pads["4"].GetPosition().x - pads["3"].GetPosition().x)), 2.60), f"{ref} DBV row spacing changed")
        need(nodes.get((ref, "1")) == f"INTENTIONALLY_UNUSED_{ref}_1" and pads["1"].GetNetname() == f"INTENTIONALLY_UNUSED_{ref}_1", f"{ref}.1 is not NC")
        need(nodes.get((ref, "2")) == f"OBS_{name}_BUF_IN" and nodes.get((ref, "3")) == "COMPUTE_0V" and nodes.get((ref, "4")) == f"OBS_{name}_BUF_OUT" and nodes.get((ref, "5")) == "PI_3V3_CANDIDATE", f"{ref} pin map changed")
        need(nodes.get(("JLOGIC1", jpin)) == f"OBS_{name}_PI", f"JLOGIC1.{jpin} mapping changed")
        need(nodes.get((f"RPU{index}", "1")) == f"OBS_{name}_BUF_OUT" and nodes.get((f"RPU{index}", "2")) == "PI_3V3_CANDIDATE", f"RPU{index} mapping changed")
        need("ERJ6ENF1002V" in values.get(f"RPU{index}", "") and "10.0 kohm" in values.get(f"RPU{index}", ""), f"RPU{index} exact pull-up changed")
        need(nodes.get((f"RGP{index}", "1")) == f"OBS_{name}_BUF_OUT" and nodes.get((f"RGP{index}", "2")) == f"OBS_{name}_PI", f"RGP{index} series mapping changed")
        need(nodes.get((f"RPO{index}", "1")) == f"OBS_{name}_PI" and nodes.get((f"RPO{index}", "2")) == "COMPUTE_0V", f"RPO{index} fail-low mapping changed")

    rmin = lambda nominal: nominal * .99 * .99; rmax = lambda nominal: nominal * 1.01 * 1.01
    high = 3.0 * rmin(330000) / (rmax(10000) + rmax(39000) + rmin(330000))
    low = .4 * rmin(330000) / (rmax(39000) + rmin(330000))
    pullup_short_ma = 3.6 / rmin(10000) * 1000
    need(close(high, 2.5984266, .0001), "open-drain HIGH screen changed")
    need(close(low, .3561872, .0001), "open-drain LOW screen changed")
    need(close(pullup_short_ma, .3673095, .0001), "pull-up short screen changed")
    load = {row["load_id"]: row for row in loads}; need(load.get("OBS5-LOAD-006", {}).get("result") == "7.612 mA", "steady-load screen changed")

    tracks, zones = list(board.GetTracks()), list(board.Zones())
    need(len([x for x in tracks if type(x).__name__ == "PCB_TRACK"]) == 207 and len([x for x in tracks if type(x).__name__ == "PCB_VIA"]) == 84, "controlled routing counts changed")
    need({(z.GetNetname(), z.GetLayer()) for z in zones} == {("SAFETY_0V", pcbnew.In1_Cu), ("COMPUTE_0V", pcbnew.In1_Cu), ("PI_3V3_CANDIDATE", pcbnew.In2_Cu)}, "plane allocation changed")
    summary = json.loads((ECAD / "validation/pcb-summary.json").read_text(encoding="utf-8"))
    for key in ("fabrication_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(summary.get(key) is False, f"summary asserts {key}")

    production = {".gbr", ".ger", ".drl", ".xln", ".pos", ".ipc", ".odb", ".zip", ".pdf"}
    need(not [path for path in ECAD.rglob("*") if path.is_file() and path.suffix.lower() in production], "production-like or PDF output exists")
    doc, web = DOC.read_text(encoding="utf-8"), WEB.read_text(encoding="utf-8")
    combined = (doc + web).lower()
    for token in (WARNING, "SN74LVC1G07DBVR", "2.598 V", "0.356 V", "7.612 mA", "zero functional-safety credit"):
        need(token.lower() in combined, f"documentation boundary missing: {token}")
    need("font-size:14px" in web and "font-size:13px" not in web and "font-size:12px" not in web, "web legibility floor changed")
    need("oe sequencing" in combined and "rp1" in combined and "standby" in combined, "power-state disposition missing")

    manifest = rows("SOURCE-MANIFEST.csv")
    for row in manifest:
        need(hashlib.sha256((ECAD / row["file"]).read_bytes()).hexdigest().upper() == row["sha256"], f"manifest mismatch: {row['file']}")
    if failures:
        print("HR-V0 runtime observation carrier P0.5 check FAILED")
        for failure in failures: print("-", failure)
        return 1
    print("HR-V0 runtime observation carrier P0.5 check PASS")
    print("  G07 open drain; 10k pull-up; 39k fault limiter; ERC/DRC 0; fourteen holds open")
    print("  zero procurement, fabrication, connection, test, motion, safety, or energization authority")
    print(WARNING); return 0


if __name__ == "__main__":
    raise SystemExit(main())
