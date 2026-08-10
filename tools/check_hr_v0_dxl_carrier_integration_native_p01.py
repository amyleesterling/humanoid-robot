"""KiCad-native parity checks for the R161 DXL-star net-name-only candidate."""

from __future__ import annotations

import math
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star" / "hr-v0-dxl-star.kicad_pcb"
CAND = ROOT / "electrical" / "kicad" / "hr-v0-dxl-star-p0.2-carrier-candidate" / "hr-v0-dxl-star-p0.2-carrier-candidate.kicad_pcb"
CARRIER = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "hr-v0-dxl-protection-carrier-p0.3.kicad_pcb"


def mapped(net: str) -> str:
    return {
        "J1_VDD": "J1_LIMITED_VDD",
        "J2_VDD": "J2_LIMITED_VDD",
        "J3_VDD": "J3_LIMITED_VDD",
    }.get(net, net)


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def footprint_signature(board, map_nets: bool) -> list[tuple]:
    result = []
    for fp in board.GetFootprints():
        pos = fp.GetPosition()
        pads = []
        for pad in fp.Pads():
            p, size, drill = pad.GetPosition(), pad.GetSize(), pad.GetDrillSize()
            net = mapped(pad.GetNetname()) if map_nets else pad.GetNetname()
            pads.append((pad.GetNumber(), mm(p.x), mm(p.y), mm(size.x), mm(size.y), mm(drill.x), mm(drill.y), net))
        result.append((fp.GetReference(), fp.GetFPID().GetLibItemName(), mm(pos.x), mm(pos.y), round(fp.GetOrientationDegrees(), 6), tuple(sorted(pads))))
    return sorted(result)


def track_signature(board, map_nets: bool) -> list[tuple]:
    result = []
    for item in board.GetTracks():
        start, end = item.GetStart(), item.GetEnd()
        net = mapped(item.GetNetname()) if map_nets else item.GetNetname()
        result.append((type(item).__name__, net, item.GetLayer(), mm(start.x), mm(start.y), mm(end.x), mm(end.y), mm(item.GetWidth())))
    return sorted(result)


def zone_signature(board, map_nets: bool) -> list[tuple]:
    result = []
    for zone in board.Zones():
        box = zone.GetBoundingBox()
        net = mapped(zone.GetNetname()) if map_nets else zone.GetNetname()
        result.append((net, zone.GetLayer(), mm(box.GetX()), mm(box.GetY()), mm(box.GetWidth()), mm(box.GetHeight()), mm(zone.GetLocalClearance()), mm(zone.GetMinThickness())))
    return sorted(result)


def outline_size(board) -> tuple[float, float]:
    edges = [item for item in board.GetDrawings() if item.GetLayer() == pcbnew.Edge_Cuts]
    xs, ys = [], []
    for item in edges:
        xs.extend((item.GetStart().x, item.GetEnd().x))
        ys.extend((item.GetStart().y, item.GetEnd().y))
    return mm(max(xs) - min(xs)), mm(max(ys) - min(ys))


def main() -> int:
    failures: list[str] = []
    base = pcbnew.LoadBoard(str(BASE))
    cand = pcbnew.LoadBoard(str(CAND))
    carrier = pcbnew.LoadBoard(str(CARRIER))

    if footprint_signature(base, True) != footprint_signature(cand, False):
        failures.append("baseline/candidate footprint and pad geometry differ beyond the explicit net map")
    if track_signature(base, True) != track_signature(cand, False):
        failures.append("baseline/candidate copper track geometry differs beyond the explicit net map")
    if zone_signature(base, True) != zone_signature(cand, False):
        failures.append("baseline/candidate zone geometry differs beyond the explicit net map")
    if outline_size(base) != (100.0, 60.0) or outline_size(cand) != (100.0, 60.0):
        failures.append("DXL-star outline must remain 100 x 60 mm")
    expected_refs = {"JC1", "JP1", "JP2", "JP3", "JA1", "JA2", "JA3", "MH1", "MH2", "MH3", "MH4"}
    if {fp.GetReference() for fp in cand.GetFootprints()} != expected_refs:
        failures.append("candidate DXL-star footprint membership changed")
    nets = {pad.GetNetname() for fp in cand.GetFootprints() for pad in fp.Pads() if pad.GetNetname()}
    for old in ("J1_VDD", "J2_VDD", "J3_VDD"):
        if old in nets:
            failures.append(f"ambiguous legacy PCB net remains: {old}")
    for new in ("J1_LIMITED_VDD", "J2_LIMITED_VDD", "J3_LIMITED_VDD"):
        if new not in nets:
            failures.append(f"post-carrier PCB net missing: {new}")

    carrier_refs = {fp.GetReference(): fp for fp in carrier.GetFootprints()}
    if outline_size(carrier) != (100.0, 60.0):
        failures.append("P0.3 carrier outline must remain 100 x 60 mm")
    expected_holes = {"MH1": (5.0, 5.0), "MH2": (95.0, 5.0), "MH3": (5.0, 55.0), "MH4": (95.0, 55.0)}
    for ref, expected in expected_holes.items():
        fp = carrier_refs.get(ref)
        if fp is None:
            failures.append(f"P0.3 carrier missing {ref}")
            continue
        pos = fp.GetPosition()
        actual = (mm(pos.x), mm(pos.y))
        if not (math.isclose(actual[0], expected[0], abs_tol=0.001) and math.isclose(actual[1], expected[1], abs_tol=0.001)):
            failures.append(f"P0.3 {ref} coordinate changed: {actual}")

    erc = CAND.parent / "validation" / "hr-v0-dxl-star-p0.2-carrier-candidate-erc.rpt"
    drc = CAND.parent / "validation" / "hr-v0-dxl-star-p0.2-carrier-candidate-drc.rpt"
    if "ERC messages: 0  Errors 0  Warnings 0" not in erc.read_text(encoding="utf-8-sig"):
        failures.append("candidate native ERC is not 0/0")
    drc_text = drc.read_text(encoding="utf-8-sig")
    if "Found 0 DRC violations" not in drc_text or "Found 0 unconnected pads" not in drc_text:
        failures.append("candidate native DRC is not zero/zero")

    if failures:
        print("HR-V0 DXL carrier integration native parity FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("HR-V0 DXL carrier integration native parity PASS")
    print("  P0.2 star is copper/geometry-identical to P0.1 after explicit pre/post-limiter net mapping")
    print("  P0.3 carrier 100 x 60 mm and four mounting datums confirmed; no fabrication or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
