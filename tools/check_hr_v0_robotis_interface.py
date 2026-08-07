"""Fail-closed source and disposition checks for HR-V0 ROBOTIS interface evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "vendor-interfaces"
EXPECTED = {
    "XM540 actuator": ("XMHD-540.N101.I101.STP", "-16.75", "16.75", "-44.75", "13.75", "-24.5", "29.8"),
    "FR13-H101K": ("FR13-H101K.stp", "-26.5", "26.5", "-2.5", "32", "-16", "16"),
    "FR13-S101K": ("FR13-S101K.stp", "-24", "24", "-44.5", "13.5", "10.5", "23.5"),
    "FR13-S102K": ("FR13-S102K.stp", "-24", "24", "-16.5", "16.5", "38.5", "51.5"),
    "FR12-H104K": ("FR12-H104K.stp", "-20.5", "20.5", "-2.5", "28", "-11.25", "35.25"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    required = {"same-origin-bounds.csv", "XM540-H101-S102-same-origin.step", "XM540-frame-orientation.svg", "interface-orientation-summary.json"}
    if {p.name for p in OUT.iterdir() if p.is_file()} != required:
        errors.append("vendor-interface artifact set changed")
    with (OUT / "same-origin-bounds.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 5:
        errors.append("expected five exact-source records")
    for row in rows:
        expected = EXPECTED.get(row.get("component", ""))
        if not expected:
            errors.append(f"unexpected component {row.get('component')}"); continue
        filename, *bounds = expected
        source = ROOT / "cad" / "vendor" / "robotis" / filename
        if row.get("source") != f"cad/vendor/robotis/{filename}" or row.get("sha256") != digest(source):
            errors.append(f"source identity/hash mismatch for {row.get('component')}")
        actual = [row.get(key) for key in ("xmin_mm", "xmax_mm", "ymin_mm", "ymax_mm", "zmin_mm", "zmax_mm")]
        if actual != bounds:
            errors.append(f"same-origin bounds changed for {row.get('component')}: {actual}")
    s102 = next((row for row in rows if row.get("component") == "FR13-S102K"), {})
    if s102.get("release_disposition") != "P0.2_APPLICATION_WITHDRAWN":
        errors.append("S102 P0.2 application is not withdrawn")
    summary = json.loads((OUT / "interface-orientation-summary.json").read_text(encoding="utf-8"))
    if summary.get("revision") != "HR-V0-ROBOTIS-IF-P0.1" or any(value != "0" for value in summary.get("pairwise_intersection_volume_mm3", {}).values()):
        errors.append("orientation summary revision or same-origin intersection evidence changed")
    if "withdrawn" not in summary.get("engineering_disposition", ""):
        errors.append("summary lost withdrawal disposition")
    try:
        tree = ET.parse(OUT / "XM540-frame-orientation.svg")
        text = " ".join(node.text or "" for node in tree.iter() if node.tag.endswith("text"))
        for token in ("P0.2 arm geometry", "not the single coplanar plate", "NO BUILDABLE ARM GEOMETRY"):
            if token not in text:
                errors.append(f"orientation SVG omits {token}")
    except ET.ParseError as exc:
        errors.append(f"orientation SVG does not parse: {exc}")
    if errors:
        print("HR-V0 ROBOTIS interface validation: FAIL", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 ROBOTIS interface validation: PASS")
    print("5 exact manufacturer STEP sources; same-origin evidence controlled; P0.2 arm geometry withdrawn")
    print("PRELIMINARY - ORIENTATION EVIDENCE ONLY - NO BUILDABLE ARM GEOMETRY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
