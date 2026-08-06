"""Validate the checked-in HR-V0 CAD release structure and vendor references."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
GENERATED = CAD / "generated"
VENDOR = ROOT / "cad" / "vendor" / "robotis"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    required_parts = ["MV0-001", "MV0-002", "MV0-003", "MV0-004"]
    with (GENERATED / "custom-parts.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if [row["part_number"] for row in rows] != required_parts:
        errors.append("custom-parts.csv does not contain the controlled four-part sequence")
    for row in rows:
        matches = list((GENERATED / "parts").glob(f'{row["part_number"]}_*'))
        suffixes = {path.suffix.lower() for path in matches}
        if suffixes != {".dxf", ".step", ".stl"}:
            errors.append(f'{row["part_number"]} missing DXF/STEP/STL set: {sorted(suffixes)}')
        if "QUOTE GEOMETRY ONLY" not in row["release_status"]:
            errors.append(f'{row["part_number"]} lost the preliminary release status')
    for svg in (GENERATED / "drawings").glob("*.svg"):
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            errors.append(f"invalid SVG {svg.name}: {exc}")
        text = svg.read_text(encoding="utf-8")
        if "PRELIMINARY—NOT RELEASED FOR FABRICATION" not in text:
            errors.append(f"{svg.name} lacks fabrication warning")
        if "font: 16px" not in text:
            errors.append(f"{svg.name} lacks 16 px drawing text baseline")
    manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))
    if "NOT RELEASED" not in manifest["warning"]:
        errors.append("generated manifest lost release warning")
    for name in ("HR-V0_preliminary_assembly.step", "HR-V0_preliminary_assembly.glb"):
        path = GENERATED / name
        if not path.exists() or path.stat().st_size < 10_000:
            errors.append(f"missing or implausibly small assembly export: {name}")
    with (VENDOR / "vendor-manifest.csv").open(newline="", encoding="utf-8") as handle:
        vendor_rows = list(csv.DictReader(handle))
    for row in vendor_rows:
        path = VENDOR / row["file"]
        if not path.exists():
            errors.append(f'missing vendor reference {row["file"]}')
        elif sha256(path) != row["sha256"].upper():
            errors.append(f'vendor hash mismatch {row["file"]}')
    checks = json.loads((GENERATED / "mechanical-checks.json").read_text(encoding="utf-8"))
    if checks["calculation_result"] != "GEOMETRY SCREEN PASSES; RELEASE REMAINS OPEN":
        errors.append("mechanical calculation status is not the controlled preliminary result")
    if not checks["not_credited_or_unresolved"]:
        errors.append("mechanical calculation omitted unresolved release inputs")
    if errors:
        print("HR-V0 CAD validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"HR-V0 CAD validation: PASS ({len(rows)} custom parts, {len(vendor_rows)} vendor references)")
    print("Status remains PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())

