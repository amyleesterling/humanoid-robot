#!/usr/bin/env python3
"""Check the R201 four-channel runtime observation candidate."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ECAD = ROOT / "electrical/kicad/hr-v0-runtime-observation-interface-p0.1"
WEB = ROOT / "release/hr-v0/runtime-observation-interface-p0.1/index.html"
DOC = ROOT / "docs/hr-v0-runtime-observation-interface-p0.1.md"
PROJECT = "hr-v0-runtime-observation-interface-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (ECAD / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    sheets = sorted(ECAD.glob("*.kicad_sch"))
    need(len(sheets) == 5, "expected root plus four native KiCad sheets")
    need((ECAD / f"{PROJECT}.kicad_pro").is_file(), "KiCad project missing")
    need((ECAD / f"{PROJECT}.kicad_sym").is_file(), "KiCad symbol library missing")
    erc = (ECAD / f"validation/{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    need(bool(re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc)), "native KiCad ERC is not 0/0")
    need(len(list((ECAD / "output").glob("runtime-observation-*.svg"))) == 4, "expected four child SVG exports")

    connector = rows("connector-schedule.csv")
    bom = rows("bom.csv")
    nets = rows("net-schedule.csv")
    loads = rows("load-budget.csv")
    holds = rows("selection-holds.csv")
    sources = rows("source-register.csv")
    need(len(connector) == 102, "connector schedule row count changed")
    need(len(bom) == 31, "BOM row count changed")
    need(len(nets) == 33, "net schedule row count changed")
    need(len(loads) == 5, "load budget row count changed")
    need(len(holds) == 10, "ten open holds required")
    need(len(sources) == 7, "seven primary-source records required")
    need(all(row["warning"] == WARNING for row in connector + bom + nets + loads + holds + sources), "warning changed or missing")

    node_net = {(row["reference"], row["terminal"]): row["net"] for row in connector}
    for ref, ch1, ch2 in (("UOBS1", "SR1", "SRA1"), ("UOBS2", "K1", "K2")):
        need(node_net.get((ref, "1")) == "COMPUTE_0V" and node_net.get((ref, "8")) == "COMPUTE_0V", f"{ref} logic ground changed")
        need(node_net.get((ref, "12")) == "SAFETY_0V" and node_net.get((ref, "14")) == "SAFETY_0V", f"{ref} field ground changed")
        need(node_net.get((ref, "9")) == f"INTENTIONALLY_UNUSED_{ref}_9" and node_net.get((ref, "13")) == f"INTENTIONALLY_UNUSED_{ref}_13", f"{ref} SUB pin became connected")
        need(node_net.get((ref, "15")) == f"{ch1}_IN" and node_net.get((ref, "16")) == f"{ch1}_SENSE", f"{ref} channel 1 changed")
        need(node_net.get((ref, "11")) == f"{ch2}_IN" and node_net.get((ref, "10")) == f"{ch2}_SENSE", f"{ref} channel 2 changed")

    need({row["net"] for row in loads} == {"SR1_STATUS", "SRA1_STATUS", "K1_STATUS", "K2_STATUS", "PI_3V3"}, "load-budget net set changed")
    need(next(row for row in loads if row["net"] == "SR1_STATUS")["state"].startswith("OPEN"), "SR1 load was falsely closed")
    need(all("10.41 to 12.18 mA" in (row["current_basis"] + row["derived_result"]) or row["net"] in {"SR1_STATUS", "PI_3V3"} for row in loads), "channel load screen changed")
    need({row["reference"] for row in bom if row["reference"].startswith("RW")} == {"RW2", "RW3", "RW4"}, "shunt set changed; SR1 must not gain RW1")
    need({row["manufacturer"] for row in sources} == {"Pilz", "Texas Instruments", "Schneider Electric", "IDEC", "Raspberry Pi", "Phoenix Contact"}, "primary-source set changed")
    need({row["source_id"] for row in sources if row["manufacturer"] == "Phoenix Contact"} == {"OBS-SRC-006", "OBS-SRC-007"}, "Phoenix terminal candidates lost exact source records")

    netlist = (ECAD / f"validation/{PROJECT}.net").read_text(encoding="utf-8")
    need(len(re.findall(r"^\s*\(comp\s*$", netlist, re.MULTILINE)) == 33, "native component count changed")
    need(len(re.findall(r"^\s*\(net\s*$", netlist, re.MULTILINE)) == 33, "native net count changed")
    for token in ("SR1_STATUS", "SRA1_STATUS", "K1_STATUS", "K2_STATUS", "OBS_SR1_PI", "OBS_SRA1_PI", "OBS_K1_PI", "OBS_K2_PI"):
        need(token in netlist, f"native netlist missing {token}")

    html_text = WEB.read_text(encoding="utf-8")
    doc_text = DOC.read_text(encoding="utf-8")
    for token in ("font:16px/1.55", "font-size:14px", "10.41-12.18 mA", "Ten gates still open", "runtime-observation-4.svg"):
        need(token in html_text, f"web guide missing {token}")
    need("font-size:13px" not in html_text and "font-size:12px" not in html_text, "web guide contains undersized user-facing text")
    need("engineering/electrical" not in html_text, "web guide points at nonexistent presentation-tree SVGs")
    need("no more than 5.0 mA" in doc_text and "no system insulation or functional-safety credit" in doc_text, "documentation boundary changed")
    need("GPIO17" not in doc_text and "physical pin" not in doc_text.lower(), "runtime observation document inferred a Pi GPIO/header pin")
    need(WARNING in doc_text and WARNING in html_text, "preliminary warning missing")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("HR-V0 runtime observation interface P0.1 check passed: 5 native sheets, 33 components, 33 nets, ERC 0/0")
    print("4 diagnostic channels; 10 holds open; no GPIO, PCB, harness, connection, motion, safety or energization release")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
