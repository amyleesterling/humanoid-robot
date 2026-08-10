"""Validate the HR-V0 DYNAMIXEL star-injection KiCad candidate.

Run with KiCad 10 bundled Python. Passing results prove encoded source
consistency only, not cable suitability, fabrication release or energization.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import math
import re
import sys
from collections import Counter
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
EXPECTED_REFS = {"JC1", "JP1", "JP2", "JP3", "JA1", "JA2", "JA3"}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_generator():
    path = ROOT / "tools" / "generate_hr_v0_dxl_star.py"
    spec = importlib.util.spec_from_file_location("dxl_star_check_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load DXL star generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def pad(footprints, reference: str, number: str):
    matches = [item for item in footprints[reference].Pads() if item.GetNumber() == number]
    if len(matches) != 1:
        raise RuntimeError(f"expected one pad {reference}.{number}, found {len(matches)}")
    return matches[0]


def point(item) -> tuple[int, int, int]:
    position = item.GetPosition()
    return position.x, position.y, item.GetLayer()


def explicit_path_exists(board, start_pad, end_pad, net_name: str) -> bool:
    graph: dict[tuple[int, int, int], set[tuple[int, int, int]]] = {}

    def connect(a, b):
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)

    for item in board.Tracks():
        if item.GetNetname() != net_name or type(item).__name__ != "PCB_TRACK":
            continue
        layer = item.GetLayer()
        start = item.GetStart()
        end = item.GetEnd()
        connect((start.x, start.y, layer), (end.x, end.y, layer))
    starts = {(start_pad.GetPosition().x, start_pad.GetPosition().y, layer) for layer in (pcbnew.F_Cu, pcbnew.B_Cu)}
    goals = {(end_pad.GetPosition().x, end_pad.GetPosition().y, layer) for layer in (pcbnew.F_Cu, pcbnew.B_Cu)}
    pending = list(starts)
    seen = set(starts)
    while pending:
        node = pending.pop()
        if node in goals:
            return True
        for neighbor in graph.get(node, set()):
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return False


def board_outline_size(board) -> tuple[float, float]:
    edges = [item for item in board.GetDrawings() if item.GetLayer() == pcbnew.Edge_Cuts]
    xs: list[int] = []
    ys: list[int] = []
    for edge in edges:
        xs.extend((edge.GetStart().x, edge.GetEnd().x))
        ys.extend((edge.GetStart().y, edge.GetEnd().y))
    return pcbnew.ToMM(max(xs) - min(xs)), pcbnew.ToMM(max(ys) - min(ys))


def main() -> int:
    failures: list[str] = []
    gen = load_generator()
    model = gen.load_schematic_model()
    items = gen.components(model)
    require(gen.REV == "DXL-STAR-P0.1", "unexpected DXL star revision", failures)
    require({item.ref for item in items} == EXPECTED_REFS, "generator connector set changed", failures)
    require(sum(len(item.pins) for item in items) == 18, "expected 18 modeled terminals", failures)

    schedule = read_csv("connector-schedule.csv")
    expected_schedule = Counter(
        (item.ref, pin.number, pin.name, pin.net, item.status)
        for item in items for pin in item.pins
    )
    actual_schedule = Counter(
        (row["reference"], row["terminal"], row["pin_name"], row["net"], row["status"])
        for row in schedule
    )
    require(expected_schedule == actual_schedule, "connector schedule differs from generator", failures)

    netlist = (OUT / "validation" / "hr-v0-dxl-star.net").read_text(encoding="utf-8-sig")
    refs = set(re.findall(r'\(ref "([A-Z]+[0-9]+)"\)', netlist)) & EXPECTED_REFS
    require(refs == EXPECTED_REFS, "native netlist reference set differs from model", failures)
    require('(tool "Eeschema 10.0.5")' in netlist and '(rev "DXL-STAR-P0.1")' in netlist,
            "native netlist tool/revision identity missing", failures)
    erc = (OUT / "validation" / "hr-v0-dxl-star-erc.rpt").read_text(encoding="utf-8-sig")
    require("ERC messages: 0  Errors 0  Warnings 0" in erc, "native ERC is not 0/0", failures)

    board = pcbnew.LoadBoard(str(OUT / "hr-v0-dxl-star.kicad_pcb"))
    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    require(set(footprints) == EXPECTED_REFS | {"MH1", "MH2", "MH3", "MH4"},
            "board footprint membership changed", failures)
    expected_footprints = {
        "JC1": "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
        "JA1": "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
        "JA2": "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
        "JA3": "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
        "JP1": "JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
        "JP2": "JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
        "JP3": "JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
    }
    for ref, name in expected_footprints.items():
        require(footprints[ref].GetFPID().GetLibItemName() == name, f"{ref} footprint changed", failures)

    require(pad(footprints, "JC1", "1").GetNetname() == "ACT_0V_PE_BONDED" and
            pad(footprints, "JC1", "2").GetNetname() == "" and
            pad(footprints, "JC1", "3").GetNetname() == "DXL_TTL_DATA",
            "JC1 no-VDD pin allocation changed", failures)
    for index in (1, 2, 3):
        vdd = f"J{index}_VDD"
        require(pad(footprints, f"JP{index}", "1").GetNetname() == vdd and
                pad(footprints, f"JP{index}", "2").GetNetname() == "ACT_0V_PE_BONDED",
                f"JP{index} power polarity/net mapping changed", failures)
        require(pad(footprints, f"JA{index}", "1").GetNetname() == "ACT_0V_PE_BONDED" and
                pad(footprints, f"JA{index}", "2").GetNetname() == vdd and
                pad(footprints, f"JA{index}", "3").GetNetname() == "DXL_TTL_DATA",
                f"JA{index} actuator pin mapping changed", failures)
        require(explicit_path_exists(board, pad(footprints, f"JP{index}", "1"), pad(footprints, f"JA{index}", "2"), vdd),
                f"{vdd} lacks an explicit routed path", failures)
    for target in ("JA1", "JA2", "JA3"):
        require(explicit_path_exists(board, pad(footprints, "JC1", "3"), pad(footprints, target, "3"), "DXL_TTL_DATA"),
                f"DATA path to {target} is incomplete", failures)

    track_counts = Counter((item.GetNetname(), round(pcbnew.ToMM(item.GetWidth()), 4), board.GetLayerName(item.GetLayer())) for item in board.Tracks())
    require(len(list(board.Tracks())) == 17, "expected 17 routed segments", failures)
    require(track_counts[("DXL_TTL_DATA", 0.25, "B.Cu")] == 8, "DATA routing width/layer/count changed", failures)
    for index in (1, 2, 3):
        require(track_counts[(f"J{index}_VDD", 2.0, "F.Cu")] == 3,
                f"J{index}_VDD routing width/layer/count changed", failures)
    zones = list(board.Zones())
    require(len(zones) == 1 and zones[0].GetNetname() == "ACT_0V_PE_BONDED" and zones[0].GetLayer() == pcbnew.B_Cu,
            "common-return B.Cu zone changed", failures)
    width, height = board_outline_size(board)
    require(math.isclose(width, 100.0, abs_tol=0.01) and math.isclose(height, 60.0, abs_tol=0.01),
            f"board outline changed to {width:.2f} x {height:.2f} mm", failures)

    drc = (OUT / "validation" / "hr-v0-dxl-star-drc.rpt").read_text(encoding="utf-8-sig")
    require("Found 0 DRC violations" in drc and "Found 0 unconnected pads" in drc,
            "native DRC is not zero violations/zero unconnected pads", failures)
    log = (OUT / "validation" / "kicad-cli.log").read_text(encoding="utf-8-sig")
    require(log.count("exit=0") == 7 and "annotation errors" not in log.lower(),
            "one or more native export/render commands failed or reported annotation errors", failures)

    svg_files = sorted((OUT / "output").glob("*.svg"))
    require(len(svg_files) == 2 and all(WARNING.encode() in path.read_bytes() for path in svg_files),
            "two warned schematic SVG pages were not generated", failures)
    require((OUT / "output" / "hr-v0-dxl-star-top.png").stat().st_size > 10_000 and
            (OUT / "output" / "hr-v0-dxl-star-bottom.png").stat().st_size > 10_000,
            "PCB renders missing or unexpectedly small", failures)
    prohibited_suffixes = {".gbr", ".ger", ".drl", ".pos", ".zip"}
    require(not any(path.suffix.lower() in prohibited_suffixes for path in OUT.rglob("*") if path.is_file()),
            "source tree contains embedded fabrication/placement output", failures)

    manifest = {row["file"]: row["sha256"] for row in read_csv("SOURCE-MANIFEST.csv")}
    current = {
        path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in OUT.rglob("*") if path.is_file() and path.name != "SOURCE-MANIFEST.csv"
    }
    require(manifest == current, "source manifest differs from current file set", failures)

    if failures:
        print("HR-V0 DXL star-injection validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 DXL star-injection validation: PASS")
    print("7 connectors; 18 terminals; 17 routed segments; 1 return zone; native ERC/DRC 0/0")
    print("U2D2 pin 2 unrouted; three positive rails isolated; source tree contains no embedded CAM/archive")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
