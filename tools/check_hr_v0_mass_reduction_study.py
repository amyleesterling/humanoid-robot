"""Validate the HR-V0 mass-reduction feasibility-study package."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import generate_hr_v0_arm_architecture as base
import generate_hr_v0_mass_reduction_study as study


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "mass-reduction-p0.1"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-3) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{actual} != {expected} within {tolerance}")


def main() -> int:
    required = {
        "HR-V0_mass-reduced-moving-adapters-candidate.glb",
        "HR-V0_mass-reduced-moving-adapters-candidate.step",
        "HR-V0_mass-reduction-study.svg",
        "candidate-decision-register.csv",
        "candidate-mass-comparison.csv",
        "exact-subset-proof.csv",
        "interface-preservation.csv",
        "ligament-and-load-screen.csv",
        "mass-reduction-summary.json",
        "stop-contact-compatibility.csv",
        "parts/MV0-C01R_same-interface-relief-candidate.step",
        "parts/MV0-C04R_same-interface-relief-candidate.step",
        "parts/MV0-C06R_same-interface-relief-candidate.step",
        "parts/MV0-C07R_same-interface-relief-candidate.step",
    }
    actual = {path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file()}
    if actual != required:
        raise AssertionError(f"artifact membership mismatch: missing={required-actual}, extra={actual-required}")

    summary = json.loads((OUT / "mass-reduction-summary.json").read_text(encoding="utf-8"))
    if summary["revision"] != study.REVISION or summary["parent_revision"] != base.REVISION:
        raise AssertionError("revision binding mismatch")
    if "NOT RELEASED" not in summary["warning"]:
        raise AssertionError("preliminary warning missing")
    close(float(summary["parent_four_adapter_mass_g"]), 231.110, 0.002)
    close(float(summary["candidate_four_adapter_mass_g"]), 173.127, 0.002)
    close(float(summary["four_adapter_reduction_g"]), 57.983, 0.002)
    close(float(summary["candidate_known_moving_subtotal_g"]), 634.775, 0.002)
    close(float(summary["candidate_headroom_g"]), 115.225, 0.002)
    if "BLOCKED" not in summary["status"]:
        raise AssertionError("mass-blocker status was weakened")

    comparison = rows("candidate-mass-comparison.csv")
    if len(comparison) != 4 or {row["candidate_part"] for row in comparison} != {"MV0-C01R", "MV0-C04R", "MV0-C06R", "MV0-C07R"}:
        raise AssertionError("four-part comparison is incomplete")
    if sum(float(row["reduction_g"]) for row in comparison) < 57.97:
        raise AssertionError("mass reduction fell below recorded candidate")
    if any("RECEIVED MASS" not in row["status"] for row in comparison):
        raise AssertionError("CAD mass estimate boundary missing")

    subset = rows("exact-subset-proof.csv")
    if len(subset) != 4:
        raise AssertionError("subset proof is incomplete")
    if any(float(row["candidate_outside_parent_volume_mm3"]) > study.SUBSET_TOLERANCE_MM3 for row in subset):
        raise AssertionError("candidate adds volume outside its parent")
    if any(row["result"] != "PASS EXACT BREP SUBSET" for row in subset):
        raise AssertionError("subset proof did not pass")

    contacts = rows("stop-contact-compatibility.csv")
    if len(contacts) != 2 or any(row["result"] != "PASS" for row in contacts):
        raise AssertionError("stop-contact compatibility did not pass")
    parent_angle = float(contacts[0]["parent_value"].split()[0])
    candidate_angle = float(contacts[0]["candidate_value"].split()[0])
    close(parent_angle, candidate_angle, 1e-5)
    close(candidate_angle, 117.999985, 2e-5)

    strength = rows("ligament-and-load-screen.csv")
    if len(strength) != 7 or any("PASS" not in row["result"] for row in strength):
        raise AssertionError("ligament/load study screen is incomplete or failed")
    if any("open" not in row["boundary"].lower() for row in strength):
        raise AssertionError("load-screen limitations are incomplete")

    interfaces = rows("interface-preservation.csv")
    if len(interfaces) != 4 or any(row["result"] != "UNCHANGED BY SUBTRACTIVE CONSTRUCTION" for row in interfaces):
        raise AssertionError("interface preservation register is incomplete")
    decisions = rows("candidate-decision-register.csv")
    if len(decisions) != 1 or decisions[0]["decision"] != "HOLD FOR INDEPENDENT REVIEW":
        raise AssertionError("candidate selection boundary was weakened")
    prohibited = decisions[0]["prohibited_use"].lower()
    if not all(word in prohibited for word in ("fabrication", "motion", "energization")):
        raise AssertionError("prohibited-use list is incomplete")

    svg = (OUT / "HR-V0_mass-reduction-study.svg").read_text(encoding="utf-8")
    root = ET.fromstring(svg)
    if root.attrib.get("viewBox") != "0 0 1600 1000":
        raise AssertionError("study drawing viewBox changed")
    sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", svg)]
    if not sizes or min(sizes) < 16:
        raise AssertionError("study drawing contains text below 16 px")
    if study.WARNING not in svg or "remains a blocker" not in svg.lower():
        raise AssertionError("study drawing warning/blocker text missing")
    for element in root.findall("{http://www.w3.org/2000/svg}text"):
        x = float(element.attrib.get("x", "0"))
        y = float(element.attrib.get("y", "0"))
        content = "".join(element.itertext())
        class_name = element.attrib.get("class", "")
        font_px = 34 if class_name == "title" else 23 if class_name == "head" else 20 if class_name == "warn" else 18
        approximate_right = x + len(content) * font_px * 0.58
        if x < 0 or y < font_px or y > 1000 or approximate_right > 1590:
            raise AssertionError(f"study text may clip: {content!r} at ({x}, {y})")

    for step_path in OUT.rglob("*.step"):
        text = step_path.read_text(encoding="utf-8", errors="ignore")
        if "ISO-10303-21" not in text or len(text) < 1000:
            raise AssertionError(f"invalid STEP export: {step_path}")
    if (OUT / "HR-V0_mass-reduced-moving-adapters-candidate.glb").stat().st_size < 1000:
        raise AssertionError("GLB export is unexpectedly small")

    print(
        "HR-V0 mass-reduction study check passed: 4 exact-subset candidates, "
        "57.983 g CAD reduction, 115.225 g provisional unresolved headroom; MASS-002 remains blocked"
    )
    print("PRELIMINARY—NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
