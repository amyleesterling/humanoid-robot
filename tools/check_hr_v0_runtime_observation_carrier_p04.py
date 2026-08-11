#!/usr/bin/env python3
"""Independently check the R210/P0.4 observation-carrier correction."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.4"
PROJECT = "hr-v0-runtime-observation-carrier-p0.4"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.4.md"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.4/index.html"
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
        if not condition:
            failures.append(message)

    need(len(list(ECAD.glob("*.kicad_sch"))) == 5, "expected root plus four native sheets")
    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    drc = (ECAD / f"validation/{PROJECT}-drc.rpt").read_text(encoding="utf-8-sig")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "ERC is not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc and "Found 0 Footprint errors" in drc, "DRC is not clean")

    connector, bom, sources = rows("connector-schedule.csv"), rows("bom.csv"), rows("source-register.csv")
    holds, loads, placements = rows("selection-holds.csv"), rows("load-budget.csv"), rows("pcb-placement.csv")
    need(len(connector) == 138 and len(bom) == 45 and len(placements) == 49, "schedule membership changed")
    need(len(holds) == 14, "fourteen evidence holds must remain open")
    need(all(row.get("warning") == WARNING for row in connector + bom + sources + holds + loads + placements), "controlled warning missing")
    need(any(row["source_id"] == "OBS4-SRC-022" and row["revision"] == "4214839/K" for row in sources), "TI land-pattern source binding missing")
    need(any(row["source_id"] == "OBS4-SRC-020" and "ERJ6ENF3902V" in row["document"] for row in sources), "39.0 kohm source binding missing")

    board = pcbnew.LoadBoard(str(ECAD / f"{PROJECT}.kicad_pcb"))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    nodes = {(row["reference"], row["terminal"]): row["net"] for row in connector}
    bom_values = {row["reference"]: row["value"] for row in bom}
    for index, name, jpin in CHANNELS:
        ref = f"UBUF{index}"
        fp = footprints[ref]
        need(fp.GetFPID().GetLibItemName() == "TI_DBV0005A_SOT23_5", f"{ref} footprint identity changed")
        pads = {pad.GetNumber(): pad for pad in fp.Pads()}
        need(len(pads) == 5, f"{ref} pad count changed")
        for number, pad in pads.items():
            need(close(mm(pad.GetSize().x), 1.10) and close(mm(pad.GetSize().y), .60), f"{ref}.{number} land is not 1.10 x 0.60 mm")
        need(close(abs(mm(pads["4"].GetPosition().x - pads["3"].GetPosition().x)), 2.60), f"{ref} row spacing is not 2.60 mm")
        need(close(abs(mm(pads["3"].GetPosition().y - pads["1"].GetPosition().y)), 1.90), f"{ref} three-pin row span is not 1.90 mm")
        need(nodes.get((ref, "1")) == "COMPUTE_0V" and nodes.get((ref, "3")) == "COMPUTE_0V", f"{ref} OE/GND is not hard-low")
        need(nodes.get((ref, "5")) == "PI_3V3_CANDIDATE", f"{ref} supply changed")
        need(nodes.get((ref, "2")) == f"OBS_{name}_BUF_IN" and nodes.get((ref, "4")) == f"OBS_{name}_BUF_OUT", f"{ref} signal mapping changed")
        need(nodes.get(("JLOGIC1", jpin)) == f"OBS_{name}_PI", f"JLOGIC1.{jpin} mapping changed")
        need("ERJ6ENF3902V" in bom_values.get(f"RGP{index}", "") and "39.0 kohm" in bom_values.get(f"RGP{index}", ""), f"RGP{index} exact candidate changed")

    # Confirm the corrected temperature-inclusive analytical screens.
    iso_short_ma = 3.6 / (1500 * .99 * .99) * 1000
    gpio_short_ua = 3.6 / (39000 * .99 * .99) * 1e6
    input_high = 2.6 * (47000 * .99 * .99) / ((47000 * .99 * .99) + (1500 * 1.01 * 1.01))
    cable_high = 2.9 * (330000 * .99 * .99) / ((330000 * .99 * .99) + (39000 * 1.01 * 1.01))
    need(close(iso_short_ma, 2.44873, .0001), "ISO short screen changed")
    need(close(gpio_short_ua, 94.1819, .001), "GPIO short screen changed")
    need(close(input_high, 2.5164, .001), "buffer-input HIGH screen changed")
    need(close(cable_high, 2.5824, .001), "cable-side HIGH screen changed")
    load = {row["load_id"]: row for row in loads}
    need(load.get("OBS4-LOAD-006", {}).get("result") == "6.183 mA", "steady load screen changed")

    tracks, zones = list(board.GetTracks()), list(board.Zones())
    need(len([t for t in tracks if type(t).__name__ == "PCB_TRACK"]) == 195 and len([t for t in tracks if type(t).__name__ == "PCB_VIA"]) == 76, "controlled routing counts changed")
    need({(z.GetNetname(), z.GetLayer()) for z in zones} == {("SAFETY_0V", pcbnew.In1_Cu), ("COMPUTE_0V", pcbnew.In1_Cu), ("PI_3V3_CANDIDATE", pcbnew.In2_Cu)}, "plane allocation changed")
    summary = json.loads((ECAD / "validation/pcb-summary.json").read_text(encoding="utf-8"))
    for key in ("fabrication_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(summary.get(key) is False, f"summary asserts {key}")

    production = {".gbr", ".ger", ".drl", ".xln", ".pos", ".ipc", ".odb", ".zip", ".pdf"}
    need(not [path for path in ECAD.rglob("*") if path.is_file() and path.suffix.lower() in production], "production-like or PDF output exists")
    doc, html = DOC.read_text(encoding="utf-8"), WEB.read_text(encoding="utf-8")
    for token in (WARNING, "4214839/K", "94.18 uA", "6.183 mA", "zero functional-safety credit"):
        need(token.lower() in (doc + html).lower(), f"documentation boundary missing: {token}")
    need("font-size:14px" in html and "font-size:13px" not in html and "font-size:12px" not in html, "web legibility floor changed")

    manifest = rows("SOURCE-MANIFEST.csv")
    for row in manifest:
        need(hashlib.sha256((ECAD / row["file"]).read_bytes()).hexdigest().upper() == row["sha256"], f"manifest mismatch: {row['file']}")

    if failures:
        print("HR-V0 runtime observation carrier P0.4 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 runtime observation carrier P0.4 check PASS")
    print("  TI 4214839/K land geometry; 39.0 kohm GPIO limiter; ERC/DRC 0; fourteen holds open")
    print("  zero procurement, fabrication, connection, test, motion, safety, or energization authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
