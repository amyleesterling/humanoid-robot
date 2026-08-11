#!/usr/bin/env python3
"""Independently check the R209 buffered observation-carrier candidate.

Passing proves encoded source consistency and zero native ERC/DRC findings only.
It grants no procurement, fabrication, connection, test, motion, safety, or
energization authority.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.3"
LEGACY = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
PROJECT = "hr-v0-runtime-observation-carrier-p0.3"
DOC = ROOT / "docs/hr-v0-runtime-observation-carrier-p0.3.md"
WEB = ROOT / "release/hr-v0/runtime-observation-carrier-p0.3/index.html"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
CHANNELS = ((1, "SR1", "UOBS1", "4", "3"), (2, "SRA1", "UOBS1", "5", "4"), (3, "K1", "UOBS2", "4", "5"), (4, "K2", "UOBS2", "5", "6"))


def rows(name: str) -> list[dict[str, str]]:
    with (ECAD / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def main() -> int:
    failures: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    need(len(list(ECAD.glob("*.kicad_sch"))) == 5, "expected root plus four native sheets")
    for suffix in ("kicad_pro", "kicad_sym", "kicad_pcb"):
        need((ECAD / f"{PROJECT}.{suffix}").is_file(), f"native {suffix} source missing")
    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8-sig")
    drc = (ECAD / f"validation/{PROJECT}-drc.rpt").read_text(encoding="utf-8-sig")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "native ERC is not 0/0")
    need("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc, "native DRC is not clean")

    connector, holds, sources = rows("connector-schedule.csv"), rows("selection-holds.csv"), rows("source-register.csv")
    placements, bom, loads = rows("pcb-placement.csv"), rows("bom.csv"), rows("load-budget.csv")
    need(len(connector) == 138, "connector schedule row count changed")
    need(len(holds) == 14 and all("open" not in row.get("state", "").lower() for row in holds), "fourteen evidence holds must remain unresolved")
    need(len(sources) == 21, "source register must contain 21 controlled records")
    need(len(placements) == 49 and len(bom) == 45, "expected 45 mounted parts plus four holes")
    need(all(row.get("warning") == WARNING for row in connector + holds + sources + placements + bom + loads), "schedule warning changed or is missing")
    need(any("SCES223T Rev T" in row["revision"] and "sn74lvc1g125.pdf" in row["official_url"] for row in sources), "TI buffer source binding missing")

    board = pcbnew.LoadBoard(str(ECAD / f"{PROJECT}.kicad_pcb"))
    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    need(len(footprints) == 49, "board footprint count changed")
    nodes = {(row["reference"], row["terminal"]): row["net"] for row in connector}
    for ref in {row["reference"] for row in placements} - {f"MH{i}" for i in range(1, 5)}:
        actual = {pad.GetNumber(): pad.GetNetname() for pad in footprints[ref].Pads()}
        expected = {terminal: net for (node_ref, terminal), net in nodes.items() if node_ref == ref}
        need(actual == expected, f"pad/net parity changed at {ref}")

    expected_mpn = {
        "RSO": "Panasonic ERJ6ENF1501V", "RPD": "Panasonic ERJ6ENF4702V",
        "RGP": "Panasonic ERJ6ENF3652V", "RPO": "Panasonic ERJ6ENF3303V",
    }
    bom_values = {row["reference"]: row["value"] for row in bom}
    for index, name, uref, upin, jpin in CHANNELS:
        ubuf = f"UBUF{index}"
        need(bom_values.get(ubuf) == "Texas Instruments SN74LVC1G125DBVR", f"{ubuf} exact identity changed")
        need(nodes.get((ubuf, "1")) == "COMPUTE_0V" and nodes.get((ubuf, "3")) == "COMPUTE_0V", f"{ubuf} enable/ground is not hard-low")
        need(nodes.get((ubuf, "5")) == "PI_3V3_CANDIDATE", f"{ubuf} supply changed")
        need(nodes.get((uref, upin)) == f"OBS_{name}_RAW", f"{name} ISO raw output changed")
        need(nodes.get((f"RSO{index}", "1")) == f"OBS_{name}_RAW" and nodes.get((f"RSO{index}", "2")) == f"OBS_{name}_BUF_IN", f"{name} ISO-side limiter topology changed")
        need(nodes.get((ubuf, "2")) == f"OBS_{name}_BUF_IN" and nodes.get((ubuf, "4")) == f"OBS_{name}_BUF_OUT", f"{name} buffer topology changed")
        need(nodes.get((f"RGP{index}", "1")) == f"OBS_{name}_BUF_OUT" and nodes.get((f"RGP{index}", "2")) == f"OBS_{name}_PI", f"{name} GPIO-side limiter topology changed")
        need(nodes.get(("JLOGIC1", jpin)) == f"OBS_{name}_PI", f"{name} JLOGIC mapping changed")
        for prefix, mpn in expected_mpn.items():
            need(mpn in bom_values.get(f"{prefix}{index}", ""), f"{prefix}{index} exact candidate changed")

    for pin, net in (("1", "PI_3V3_CANDIDATE"), ("2", "COMPUTE_0V"), ("3", "OBS_SR1_PI"), ("4", "OBS_SRA1_PI"), ("5", "OBS_K1_PI"), ("6", "OBS_K2_PI")):
        need(nodes.get(("JLOGIC1", pin)) == net, f"JLOGIC1.{pin} mapping changed")
    for pin, net in (("1", "SR1_STATUS"), ("2", "SRA1_STATUS"), ("3", "K1_STATUS"), ("4", "K2_STATUS"), ("5", "SAFETY_0V"), ("6", "INTENTIONALLY_UNUSED_JFIELD1_6")):
        need(nodes.get(("JFIELD1", pin)) == net, f"JFIELD1.{pin} mapping changed")

    tracks, zones = list(board.GetTracks()), list(board.Zones())
    segments = [item for item in tracks if type(item).__name__ == "PCB_TRACK"]
    vias = [item for item in tracks if type(item).__name__ == "PCB_VIA"]
    need(len(segments) == 195 and len(vias) == 76 and len(zones) == 3, "controlled copper counts changed")
    need({(z.GetNetname(), z.GetLayer()) for z in zones} == {("SAFETY_0V", pcbnew.In1_Cu), ("COMPUTE_0V", pcbnew.In1_Cu), ("PI_3V3_CANDIDATE", pcbnew.In2_Cu)}, "plane allocation changed")
    need(board.GetCopperLayerCount() == 4, "board is no longer four-layer")
    edges = [item for item in board.GetDrawings() if item.GetLayer() == pcbnew.Edge_Cuts]
    xs = [mm(point) for item in edges for point in (item.GetStart().x, item.GetEnd().x)]
    ys = [mm(point) for item in edges for point in (item.GetStart().y, item.GetEnd().y)]
    need(math.isclose(max(xs)-min(xs), 120.0, abs_tol=.001) and math.isclose(max(ys)-min(ys), 90.0, abs_tol=.001), "120 x 90 mm outline changed")

    summary = json.loads((ECAD / "validation/pcb-summary.json").read_text(encoding="utf-8"))
    need(summary.get("footprints") == 49 and summary.get("mounted_components") == 45, "PCB summary membership changed")
    for key in ("fabrication_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(summary.get(key) is False, f"PCB summary improperly asserts {key}")

    load = {row["load_id"]: row for row in loads}
    need(load.get("OBS3-LOAD-006", {}).get("result") == "6.180 mA", "3V3 load screen changed")
    need(math.isclose(3.6/(1500*.99)*1000, 2.424242, abs_tol=.00001), "ISO short calculation changed")
    need(math.isclose(3.6/(36500*.99)*1e6, 99.6265, abs_tol=.001), "GPIO short calculation changed")

    netlist = (ECAD / f"validation/{PROJECT}.net").read_text(encoding="utf-8-sig")
    need("SN74LVC125ADR" not in netlist, "superseded quad-buffer candidate remains")
    forbidden = {".gbr", ".ger", ".drl", ".xln", ".pos", ".ipc", ".odb", ".zip", ".pdf"}
    need(not [path for path in ECAD.rglob("*") if path.is_file() and path.suffix.lower() in forbidden], "production-like or PDF output exists")
    for svg in ECAD.glob("output/*.svg"):
        need(svg.read_text(encoding="utf-8").lstrip().startswith("<?xml"), f"invalid SVG export: {svg.name}")

    doc, html = DOC.read_text(encoding="utf-8"), WEB.read_text(encoding="utf-8")
    for token in (WARNING, "zero functional-safety credit", "6.180 mA", "Pi 5/RP1"):
        need(token.lower() in (doc + html).lower(), f"documentation boundary missing: {token}")
    need("font-size:14px" in html and "font-size:13px" not in html and "font-size:12px" not in html, "web legibility floor changed")

    manifest = rows("SOURCE-MANIFEST.csv")
    manifest_map = {row["file"]: row["sha256"] for row in manifest}
    for rel, digest in manifest_map.items():
        need(hashlib.sha256((ECAD / rel).read_bytes()).hexdigest().upper() == digest, f"manifest hash mismatch: {rel}")

    if failures:
        print("HR-V0 runtime observation carrier P0.3 check FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 runtime observation carrier P0.3 check PASS")
    print("  5 sheets; 49 footprints; 195 segments; 76 vias; ERC/DRC 0; 14 holds open")
    print("  zero procurement, fabrication, connection, test, motion, safety, or energization authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
