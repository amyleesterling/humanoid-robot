#!/usr/bin/env python3
"""Validate the R204 Raspberry Pi observation carrier and harness candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import pcbnew
except ImportError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"
PROJECT = "hr-v0-pi-observation-carrier-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
EXPECTED = {"17": "PI_3V3_CANDIDATE", "20": "COMPUTE_0V", "15": "OBS_SR1_PI", "16": "OBS_SRA1_PI", "18": "OBS_K1_PI", "22": "OBS_K2_PI"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    required = [
        f"{PROJECT}.kicad_pro", f"{PROJECT}.kicad_sch", "01_pi_observation_carrier.kicad_sch",
        f"{PROJECT}.kicad_pcb", "connector-schedule.csv", "bom.csv", "harness-interface.csv",
        "source-register.csv", "selection-holds.csv", "pcb-placement.csv", "SOURCE-MANIFEST.csv",
        f"validation/{PROJECT}-erc.rpt", f"validation/{PROJECT}-drc.rpt", "validation/validation-summary.json",
        "output/pi-observation-carrier.svg",
    ]
    for rel in required:
        need((ECAD / rel).is_file(), f"missing {rel}")
    need(not list((ECAD / "output").glob("*.pdf")), "PDF export must not exist")
    need(not any(path for pattern in ("*.gbr", "*.drl", "*.zip") for path in ECAD.rglob(pattern)), "supplier/CAM output must not exist")

    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    drc = (ECAD / f"validation/{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("0  Errors 0  Warnings" in erc, "ERC is not 0/0")
    need("Found 0 DRC violations" in drc, "DRC is not zero")
    summary = json.loads((ECAD / "validation/validation-summary.json").read_text(encoding="utf-8"))
    need(summary["routed_nets"] == 6 and summary["unused_header_positions"] == 34, "summary net/no-copper counts drifted")
    need(summary["holds_open"] == 10, "hold count drifted")
    need(not any(summary[key] for key in ("fabrication_authorized", "connection_authorized", "energization_authorized")), "authority weakened")

    schedule = rows(ECAD / "connector-schedule.csv")
    pi = [row for row in schedule if row["reference"] == "JPI1"]
    out = [row for row in schedule if row["reference"] == "JOBS1"]
    need(len(pi) == 40 and len(out) == 6, "connector schedule must contain 40 Pi plus 6 terminal positions")
    need({row["terminal"]: row["net"] for row in pi if row["net"] != "NO_NET"} == EXPECTED, "Pi mapping drifted")
    need(sum(row["net"] == "NO_NET" for row in pi) == 34, "exactly 34 Pi positions must be NO_NET")
    for number in ("2", "4", "27", "28"):
        row = next(item for item in pi if item["terminal"] == number)
        need(row["net"] == "NO_NET" and "NO COPPER" in row["function"], f"Pi pin {number} must have no copper")
    need({row["terminal"]: row["net"] for row in out} == {str(index): net for index, net in enumerate(("PI_3V3_CANDIDATE", "COMPUTE_0V", "OBS_SR1_PI", "OBS_SRA1_PI", "OBS_K1_PI", "OBS_K2_PI"), 1)}, "JOBS mapping drifted")

    bom = rows(ECAD / "bom.csv")
    need([(row["reference"], row["manufacturer_part"]) for row in bom] == [("JPI1", "ESQ-120-33-G-D"), ("JOBS1", "1751280")], "exact connector BOM drifted")
    harness = rows(ECAD / "harness-interface.csv")
    need(len(harness) == 6 and all(row["cut_length_mm"] == "SELECTION REQUIRED" for row in harness), "harness lengths must remain unresolved")
    need([row["stock_mpn"] for row in harness] == ["Belden 3051 RD005", "Belden 3051 BK005", "Belden 3051 BL005", "Belden 3051 OR005", "Belden 3051 VI005", "Belden 3051 WH005"], "wire order codes drifted")
    need(len(rows(ECAD / "selection-holds.csv")) == 10, "ten R204 holds required")
    sources = rows(ECAD / "source-register.csv")
    need(len(sources) == 8 and all(row["official_url"].startswith("https://") for row in sources), "source register incomplete")
    need(any("1.02 mm" in row["use_and_limit"] and "copper land" in row["use_and_limit"] for row in sources), "Samtec drill/land boundary missing")

    if pcbnew is None:
        raise RuntimeError("pcbnew is required; use KiCad 10 Python")
    board = pcbnew.LoadBoard(str(ECAD / f"{PROJECT}.kicad_pcb"))
    need(board.GetCopperLayerCount() == 2, "board must be two-layer")
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(set(footprints) == {"JPI1", "JOBS1", "MH1", "MH2", "MH3", "MH4"}, "footprint set drifted")
    jpi = footprints["JPI1"]
    need(len(list(jpi.Pads())) == 40, "JPI1 must contain 40 physical pads")
    actual = {pad.GetNumber(): pad.GetNetname() for pad in jpi.Pads() if pad.GetNetCode()}
    need(actual == EXPECTED, f"JPI1 board nets drifted: {actual}")
    need(sum(pad.GetNetCode() == 0 for pad in jpi.Pads()) == 34, "34 JPI1 pads must be no-net")
    for pad in jpi.Pads():
        need(abs(pcbnew.ToMM(pad.GetDrillSize().x) - 1.02) < 0.001, "Samtec drill must be 1.02 mm")
        need(abs(pcbnew.ToMM(pad.GetSize().x) - 1.70) < 0.001, "project-controlled Samtec land must be 1.70 mm")
    holes = [footprints[f"MH{i}"] for i in range(1, 5)]
    positions = {(round(pcbnew.ToMM(fp.GetPosition().x), 1), round(pcbnew.ToMM(fp.GetPosition().y), 1)) for fp in holes}
    need(positions == {(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)}, "mounting-hole pattern drifted")
    track_nets = {item.GetNetname() for item in board.GetTracks() if item.GetNetCode()}
    need(track_nets == set(EXPECTED.values()), "routed net set drifted")
    need(not ({"5V", "ID_SD", "ID_SC"} & track_nets), "forbidden 5 V/ID copper present")

    html_text = (ROOT / "release/hr-v0/pi-observation-carrier-p0.1/index.html").read_text(encoding="utf-8")
    doc_text = (ROOT / "docs/hr-v0-pi-observation-carrier-p0.1.md").read_text(encoding="utf-8")
    for text in (html_text, doc_text):
        need(WARNING in text, "full warning missing")
        need("not a hat" in text.lower() or "not** a hat" in text.lower(), "HAT naming boundary missing")
        need("zero functional-safety credit" in text.lower(), "zero safety-credit boundary missing")
    need("font:16px" in html_text and "font-size:14px" in html_text, "web minimum text sizes drifted")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", html_text), "web contains user-facing text below 12 px")

    manifest = rows(ECAD / "SOURCE-MANIFEST.csv")
    for row in manifest:
        path = ECAD / row["file"]
        need(path.is_file(), f"manifest target missing: {row['file']}")
        need(hashlib.sha256(path.read_bytes()).hexdigest().upper() == row["sha256"], f"manifest hash mismatch: {row['file']}")
    print("R204 Pi observation carrier: ERC 0/0, DRC 0, 6 routed nets, 34 no-copper Pi positions, 10 holds open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
