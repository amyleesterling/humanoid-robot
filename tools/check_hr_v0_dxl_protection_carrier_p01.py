"""Fail-closed consistency checks for HR-V0-DXL-PROT-CARRIER-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier"
RELEASE = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.1"
PROJECT = "hr-v0-dxl-protection-carrier"
WARNING_TOKEN = "NOT APPROVED"


def need(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    failures: list[str] = []
    expected_source = {
        f"{PROJECT}.kicad_pro", f"{PROJECT}.kicad_sch", f"{PROJECT}.kicad_sym", f"{PROJECT}.kicad_pcb",
        "01_protection_core.kicad_sch", "02_threshold_dividers.kicad_sch", "03_bypass_and_transients.kicad_sch", "04_measurement_points.kicad_sch",
        "ProjectButton_RPW.pretty/TI_RPW0010A_HotRodQFN_2x2mm_P0.475mm_CANDIDATE.kicad_mod", "bom.csv", "terminal-schedule.csv", "sym-lib-table", "fp-lib-table",
    }
    for relative in expected_source:
        need((SOURCE / relative).is_file(), f"missing native source {relative}", failures)
        need((RELEASE / "source" / relative).is_file(), f"missing controlled source {relative}", failures)
    native_sheets = sorted(SOURCE.glob("*.kicad_sch"))
    need(len(native_sheets) == 5, f"native sheet count {len(native_sheets)} != 5", failures)
    for path in expected_source:
        if (SOURCE / path).is_file() and (RELEASE / "source" / path).is_file():
            need(sha(SOURCE / path) == sha(RELEASE / "source" / path), f"controlled source hash mismatch: {path}", failures)

    erc = (RELEASE / "validation" / f"{PROJECT}-erc.rpt").read_text(encoding="utf-8")
    drc = (RELEASE / "validation" / f"{PROJECT}-drc.rpt").read_text(encoding="utf-8")
    need("ERC messages: 0  Errors 0  Warnings 0" in erc, "ERC is not 0/0", failures)
    need("Found 0 DRC violations" in drc, "DRC violations remain", failures)
    need("Found 0 unconnected pads" in drc, "unconnected board pads remain", failures)

    bom = rows(SOURCE / "bom.csv")
    physical = [row for row in bom if int(row["quantity"]) > 0]
    need(len(physical) == 20, f"physical BOM placement count {len(physical)} != 20", failures)
    bom_by_ref = {row["reference"]: row for row in bom}
    exact = {
        "U1": "TPS259461LRPWR", "JIN1": "B2P-VH", "JOUT1": "B2P-VH",
        "RUVT1": "RC0603FR-07365KL", "RUVB1": "RC0603FR-0749K9L", "ROVT1": "RC0603FR-07470KL", "ROVB1": "RC0603FR-0744K2L",
        "CDV1": "C1608C0G1H222J080AA", "CINHF1": "C1608X7R1H104K080AA", "CINBULK1": "C1608X7R1V105K080AC",
        "COUTA1": "C1608X7R1V105K080AC", "COUTB1": "C1608X7R1V105K080AC", "DCLAMP1": "B330A-13-F",
    }
    for ref, mpn in exact.items():
        need(bom_by_ref.get(ref, {}).get("manufacturer_part_number") == mpn, f"{ref} exact MPN mismatch", failures)
    need(bom_by_ref.get("RILM1", {}).get("manufacturer_part_number") == "RC0603FR-071K65L / RC0603FR-073K32L", "RILM variant identities changed", failures)
    need(bom_by_ref.get("U1G", {}).get("quantity") == "0", "U1G must remain zero-quantity same-device cross-reference", failures)

    terminals = rows(SOURCE / "terminal-schedule.csv")
    terminal_map = {(row["reference"], row["terminal"]): row["net"] for row in terminals}
    expected_u1 = {"1": "UVLO_SET", "2": "OVLO_SET", "3": "SPLYGD_DIAG", "4": "FLT_DIAG", "5": "BRANCH_FUSED_IN", "6": "BRANCH_LIMITED_OUT", "7": "DVDT_SET", "8": "ACT_0V_PE_BONDED", "9": "ILM_SET", "10": "INTENTIONALLY_OPEN_ITIMER"}
    for terminal, net in expected_u1.items():
        ref = "U1G" if terminal == "8" else "U1"
        need(terminal_map.get((ref, terminal)) == net, f"schematic terminal mismatch {ref}.{terminal}", failures)
    need(terminal_map.get(("JIN1", "1")) == "BRANCH_FUSED_IN" and terminal_map.get(("JIN1", "2")) == "ACT_0V_PE_BONDED", "JIN1 polarity changed", failures)
    need(terminal_map.get(("JOUT1", "1")) == "BRANCH_LIMITED_OUT" and terminal_map.get(("JOUT1", "2")) == "ACT_0V_PE_BONDED", "JOUT1 polarity changed", failures)

    board = pcbnew.LoadBoard(str(SOURCE / f"{PROJECT}.kicad_pcb"))
    need(board.GetCopperLayerCount() == 4, "board is not four copper layers", failures)
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    need(len([ref for ref in footprints if not ref.startswith("MH")]) == 20, "board placement membership changed", failures)
    u1 = footprints.get("U1")
    need(u1 is not None, "U1 footprint missing", failures)
    if u1:
        pad_numbers = [pad.GetNumber() for pad in u1.Pads()]
        need(set(pad_numbers) == {str(i) for i in range(1, 11)}, "U1 unique pad numbers changed", failures)
        need(len(pad_numbers) == 14, "U1 compound land count changed", failures)
        pcb_map = {}
        for pad in u1.Pads():
            pcb_map.setdefault(pad.GetNumber(), pad.GetNetname())
        for terminal, net in expected_u1.items():
            expected = "" if terminal == "10" else net
            need(pcb_map.get(terminal) == expected, f"PCB U1.{terminal} net mismatch", failures)
    need(sum(isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks()) >= 18, "carrier via/fanout count unexpectedly low", failures)

    variants = rows(RELEASE / "assembly-variants.csv")
    need(sum(int(row["quantity"]) for row in variants) == 3, "assembly variant quantity is not three", failures)
    need({row["RILM1_mpn"] for row in variants} == {"RC0603FR-071K65L", "RC0603FR-073K32L"}, "assembly RILM variants changed", failures)
    sources = rows(RELEASE / "primary-source-register.csv")
    need(len(sources) == 7, "primary-source register count changed", failures)
    need(all(row["url"].startswith("https://") and row["revision"] for row in sources), "primary-source revision/URL missing", failures)
    holds = rows(RELEASE / "residual-holds.csv")
    need(len(holds) == 16 and all(row["state"] == "OPEN" for row in holds), "residual holds are not sixteen OPEN records", failures)
    tests = rows(RELEASE / "test-plan.csv")
    data = rows(RELEASE / "test-data-template.csv")
    need(len(tests) == 10 and all(row["execution_state"] == "NOT EXECUTED" and row["result"] == "" for row in tests), "test plan claims execution/results", failures)
    need(len(data) == 10 and all(row["result"] == "" and row["article_serial"] == "" for row in data), "test data template is not blank", failures)

    status = json.loads((RELEASE / "package-status.json").read_text(encoding="utf-8"))
    for key in ("robot_baseline_changed", "fabrication_authorized", "assembly_authorized", "connection_authorized", "energization_authorized", "functional_safety_credit"):
        need(status.get(key) is False, f"fail-closed status changed: {key}", failures)
    need(status.get("native_kicad_sheets") == 5 and status.get("tests_executed") == 0 and status.get("open_holds") == 16, "package-status counts changed", failures)

    outputs = RELEASE / "output"
    need(len(list(outputs.glob("*.svg"))) == 5, "schematic SVG count changed", failures)
    need((outputs / f"{PROJECT}-top.png").is_file() and (outputs / f"{PROJECT}-bottom.png").is_file(), "board review render missing", failures)
    need(len(list((RELEASE / "cam" / "gerbers").glob("*Cu.*"))) == 4, "four copper Gerbers not present", failures)
    page = (RELEASE / "index.html").read_text(encoding="utf-8")
    need("font:16px/1.55" in page and "font-size:14px" in page, "web guide legibility floor changed", failures)
    need(all(name in page for name in ("01_protection_core.svg", "02_threshold_dividers.svg", "03_bypass_and_transients.svg", "04_measurement_points.svg")), "web guide schematic links incomplete", failures)
    need(WARNING_TOKEN in page and WARNING_TOKEN in (RELEASE / "README.md").read_text(encoding="utf-8"), "preliminary warning missing", failures)

    manifest = rows(RELEASE / "file-manifest.csv")
    actual = {path.relative_to(RELEASE).as_posix(): sha(path) for path in RELEASE.rglob("*") if path.is_file() and path.name != "file-manifest.csv"}
    recorded = {row["file"]: row["sha256"] for row in manifest}
    need(recorded == actual, "release file manifest is incomplete or stale", failures)

    if failures:
        print("R156 carrier checks FAILED")
        for failure in failures: print(f"- {failure}")
        return 1
    print("R156 carrier checks passed: five native sheets, ERC/DRC 0/0, 20 physical placements, three variants, ten blank tests, sixteen open holds")
    print("PRELIMINARY - no fabrication, assembly, connection, motion, energization or functional-safety approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
