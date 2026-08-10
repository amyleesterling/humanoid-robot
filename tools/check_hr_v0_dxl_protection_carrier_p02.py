#!/usr/bin/env python3
"""Native parity check for corrected DXL protection carrier P0.2."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.2"
REL = ROOT / "release" / "hr-v0" / "dxl-protection-carrier-p0.2"
PROJECT = "hr-v0-dxl-protection-carrier-p0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def close(a: float, b: float, tol: float = 0.00001) -> bool:
    return abs(a - b) <= tol


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def signature(pad: pcbnew.PAD) -> tuple[str, float, float, float, float, bool, bool, bool]:
    pos = pad.GetFPRelativePosition()
    size = pad.GetSize()
    layers = pad.GetLayerSet()
    return (
        pad.GetNumber(), mm(pos.x), mm(pos.y), mm(size.x), mm(size.y),
        layers.Contains(pcbnew.F_Cu), layers.Contains(pcbnew.F_Mask), layers.Contains(pcbnew.F_Paste),
    )


def main() -> int:
    failures: list[str] = []
    board = pcbnew.LoadBoard(str(OUT / f"{PROJECT}.kicad_pcb"))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    u1 = footprints.get("U1")
    if u1 is None:
        failures.append("U1 missing")
        pads = []
    else:
        if "TI4225183A_P02" not in str(u1.GetFPID().GetLibItemName()):
            failures.append(f"wrong U1 footprint: {u1.GetFPID()}")
        pads = list(u1.Pads())
    sigs = [signature(pad) for pad in pads]

    expected_copper = {
        ("2", -0.9, 0.225, 0.6, 0.25), ("3", -0.9, -0.225, 0.6, 0.25),
        ("8", 0.9, -0.225, 0.6, 0.25), ("9", 0.9, 0.225, 0.6, 0.25),
        ("5", -0.25, 0.0, 0.3, 2.4), ("6", 0.25, 0.0, 0.3, 2.4),
        ("1", -0.9, 0.7, 0.6, 0.3), ("1", -0.725, 0.875, 0.25, 0.65),
        ("4", -0.9, -0.7, 0.6, 0.3), ("4", -0.725, -0.875, 0.25, 0.65),
        ("7", 0.9, -0.7, 0.6, 0.3), ("7", 0.725, -0.875, 0.25, 0.65),
        ("10", 0.9, 0.7, 0.6, 0.3), ("10", 0.725, 0.875, 0.25, 0.65),
    }
    actual_copper = {(n, x, y, sx, sy) for n, x, y, sx, sy, cu, mask, paste in sigs if cu}
    if actual_copper != expected_copper:
        failures.append(f"copper geometry mismatch: {sorted(actual_copper ^ expected_copper)}")
    for n, x, y, sx, sy, cu, mask, paste in sigs:
        if cu and (not mask or paste):
            failures.append(f"copper pad {n}@{x},{y} must be F.Cu/F.Mask only")

    expected_paste = {
        ("", -0.9, 0.225, 0.6, 0.25), ("", -0.9, -0.225, 0.6, 0.25),
        ("", 0.9, -0.225, 0.6, 0.25), ("", 0.9, 0.225, 0.6, 0.25),
        ("", -0.25, 0.63, 0.28, 1.06), ("", -0.25, -0.63, 0.28, 1.06),
        ("", 0.25, 0.63, 0.28, 1.06), ("", 0.25, -0.63, 0.28, 1.06),
        ("", -0.9, 0.7, 0.6, 0.275), ("", -0.725, 0.875, 0.225, 0.63),
        ("", -0.9, -0.7, 0.6, 0.275), ("", -0.725, -0.875, 0.225, 0.63),
        ("", 0.9, -0.7, 0.6, 0.275), ("", 0.725, -0.875, 0.225, 0.63),
        ("", 0.9, 0.7, 0.6, 0.275), ("", 0.725, 0.875, 0.225, 0.63),
    }
    actual_paste = {(n, x, y, sx, sy) for n, x, y, sx, sy, cu, mask, paste in sigs if paste}
    if actual_paste != expected_paste:
        failures.append(f"paste geometry mismatch: {sorted(actual_paste ^ expected_paste)}")
    if any(cu or mask or not paste for n, x, y, sx, sy, cu, mask, paste in sigs if paste):
        failures.append("paste apertures must be paste-only")

    if len(pads) != 30 or len(actual_copper) != 14 or len(actual_paste) != 16:
        failures.append(f"expected 30 pad primitives (14 copper + 16 paste), got {len(pads)}")
    parity = rows(REL / "rpw-land-pattern-parity.csv")
    if len(parity) != 10 or sum("P0.1 FAIL" in row["disposition"] for row in parity) != 8:
        failures.append("parity register must preserve eight explicit P0.1 failures")
    holds = rows(REL / "residual-holds.csv")
    if len(holds) != 16 or sum(row["state"] == "PARTIAL" for row in holds) != 1 or sum(row["state"] == "OPEN" for row in holds) != 15:
        failures.append("hold register must contain one partial footprint hold and fifteen open holds")
    status = json.loads((REL / "package-status.json").read_text(encoding="utf-8"))
    for flag in ("fabrication_authorized", "assembly_authorized", "connection_authorized", "energization_authorized", "functional_safety_credit"):
        if status.get(flag) is not False:
            failures.append(f"{flag} must remain false")
    if status.get("p0_1_land_pattern_superseded") is not True or status.get("tests_executed") != 0:
        failures.append("status must supersede P0.1 and claim zero tests")
    for path in (REL / "README.md", REL / "index.html"):
        text = path.read_text(encoding="utf-8")
        if WARNING not in text or "P0.1" not in text or "P0.2" not in text:
            failures.append(f"{path.name} missing warning/supersession language")
    for path in OUT.rglob("*"):
        if path.is_file():
            copied = REL / "source" / path.relative_to(OUT)
            if not copied.is_file() or hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(copied.read_bytes()).digest():
                failures.append(f"controlled source copy mismatch: {path.relative_to(OUT).as_posix()}")
    manifest = {row["file"]: row["sha256"] for row in rows(REL / "file-manifest.csv")}
    current = {
        path.relative_to(REL).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper()
        for path in REL.rglob("*") if path.is_file() and path.name != "file-manifest.csv"
    }
    if manifest != current:
        failures.append("release file manifest stale")
    if failures:
        print("HR-V0 DXL protection carrier P0.2 check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 DXL protection carrier P0.2 OK: exact 14 copper + 16 paste primitives, 8 P0.1 defects superseded, 0 tests/authorizations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
