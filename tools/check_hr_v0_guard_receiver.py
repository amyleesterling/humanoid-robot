"""Fail-closed validation for the HR-V0 guard/receiver candidate."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import generate_hr_v0_guard_receiver as guard


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-receiver-p0.2"
FORM = ROOT / "tests" / "forms" / "hr-v0-guard-clearance-inspection-template.csv"


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "HR-V0_fixed-guard-interactive.html",
        "HR-V0_fixed-guard-receiver-candidate.glb",
        "HR-V0_fixed-guard-receiver-candidate.step",
        "HR-V0_fixed-guard-receiver-layout.svg",
        "guard-calculation-screen.csv",
        "guard-closure-holds.csv",
        "guard-frame-cut-schedule.csv",
        "guard-interface-controls.csv",
        "guard-panel-cut-schedule.csv",
        "guard-receiver-summary.json",
        "guard-source-register.csv",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    if actual != required:
        raise AssertionError(f"artifact membership mismatch: missing={required-actual}, extra={actual-required}")

    summary = json.loads((OUT / "guard-receiver-summary.json").read_text(encoding="utf-8"))
    if summary["revision"] != guard.REVISION or summary["arm_revision"] != guard.ARM_REVISION:
        raise AssertionError("guard/arm revision binding changed")
    if summary["internal_clear_mm"] != {"x": 400.0, "y": 900.0, "z": 950.0}:
        raise AssertionError("controlled internal guard space changed")
    if summary["frame_physical_pieces"] != 16 or summary["panel_physical_pieces"] != 8:
        raise AssertionError("frame/panel schedule count changed")
    if summary["open_holds"] != 12 or "ALL FABRICATION" not in summary["release_state"]:
        raise AssertionError("guard holds or fail-closed release state weakened")

    frame = read_rows("guard-frame-cut-schedule.csv")
    if len(frame) != 4 or sum(int(row["quantity"]) for row in frame) != 16:
        raise AssertionError("frame cut schedule is incomplete")
    if any("SELECTION REQUIRED" not in row["selection_state"] for row in frame):
        raise AssertionError("frame schedule falsely releases a material or connector")
    panels = read_rows("guard-panel-cut-schedule.csv")
    if len(panels) != 4 or sum(int(row["quantity"]) for row in panels) != 8:
        raise AssertionError("panel schedule is incomplete")
    if any("SELECTION REQUIRED" not in row["selection_state"] for row in panels):
        raise AssertionError("panel schedule falsely releases a material or retention method")
    holds = read_rows("guard-closure-holds.csv")
    if {row["hold_id"] for row in holds} != {f"GH-{index:03d}" for index in range(1, 13)}:
        raise AssertionError("guard closure register lost GH-001 through GH-012")
    if any(row["state"] not in {"OPEN", "SELECTION REQUIRED", "DESIGN REQUIRED"} for row in holds):
        raise AssertionError("guard closure register contains an executed-looking state")
    sources = read_rows("guard-source-register.csv")
    if len(sources) != 4 or sources[2]["verification"] != "NOT VERIFIED - SELECTION REQUIRED" or sources[3]["url"] != "SELECTION REQUIRED":
        raise AssertionError("unverified frame/panel primary-source boundary was weakened")

    with FORM.open(encoding="utf-8", newline="") as handle:
        form = list(csv.DictReader(handle))
    if {row["case_id"] for row in form} != {f"GC-{index:03d}" for index in range(1, 13)}:
        raise AssertionError("guard inspection form lost GC-001 through GC-012")
    expected_limits = {
        "GC-001": ("-20", "15"), "GC-002": ("-20", "115"),
        "GC-003": ("70", "15"), "GC-004": ("70", "115"),
        "GC-005": ("-20", "120"), "GC-006": ("70", "120"),
    }
    by_id = {row["case_id"]: row for row in form}
    for case_id, (j1, j2) in expected_limits.items():
        if (by_id[case_id]["j1_deg"], by_id[case_id]["j2_internal_deg"]) != (j1, j2):
            raise AssertionError(f"{case_id} lost the current P0.7 limit/certificate case")
    if any(row["record_id"] != "NOT-EXECUTED" or row["disposition"] != "NOT EXECUTED" for row in form):
        raise AssertionError("guard inspection form contains executed-looking evidence")

    svg = (OUT / "HR-V0_fixed-guard-receiver-layout.svg").read_text(encoding="utf-8")
    root = ET.fromstring(svg)
    if root.attrib.get("viewBox") != "0 0 1600 1080":
        raise AssertionError("guard layout viewBox changed")
    sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", svg)]
    if not sizes or min(sizes) < 18:
        raise AssertionError("guard layout text fell below 18 px")
    html = (OUT / "HR-V0_fixed-guard-interactive.html").read_text(encoding="utf-8")
    if "font:16px" not in html or "font-size:16px" not in html or guard.WARNING not in html:
        raise AssertionError("interactive guide legibility or warning changed")
    if "No cutting, drilling, purchase" not in html:
        raise AssertionError("interactive guide release warning weakened")

    step = (OUT / "HR-V0_fixed-guard-receiver-candidate.step").read_text(encoding="utf-8", errors="ignore")
    if "ISO-10303-21" not in step or len(step) < 10000:
        raise AssertionError("guard STEP export is missing or invalid")
    if (OUT / "HR-V0_fixed-guard-receiver-candidate.glb").stat().st_size < 5000:
        raise AssertionError("guard GLB export is unexpectedly small")

    print("HR-V0 guard/receiver check passed: 16 frame pieces, 8 panel candidates, 12 open holds, 12 unexecuted inspection cases")
    print(guard.WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
