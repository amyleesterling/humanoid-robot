"""Validate the HR-V0 gripper source-control and integration package."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import generate_hr_v0_gripper_integration as package


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "gripper-integration-p0.2"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-3) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{actual} != {expected} within {tolerance}")


def main() -> int:
    required = {
        "HR-V0_gripper-reference-envelope.svg",
        "HR-V0_gripper-reference-viewer.html",
        "README.md",
        "gripper-geometry-summary.json",
        "gripper-integration-holds.csv",
        "gripper-kinematic-samples.csv",
        "gripper-mass-load-sensitivity.csv",
        "gripper-source-integrity.csv",
    }
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    if actual != required:
        raise AssertionError(f"artifact membership mismatch: missing={required-actual}, extra={actual-required}")

    sources = rows("gripper-source-integrity.csv")
    if len(sources) != len(package.EXPECTED_HASHES):
        raise AssertionError("source register count mismatch")
    for row in sources:
        name = row["file"]
        if row["upstream_commit"] != package.SOURCE_COMMIT:
            raise AssertionError(f"unfrozen source commit: {name}")
        if row["sha256"] != package.EXPECTED_HASHES[name]:
            raise AssertionError(f"recorded source hash mismatch: {name}")
        if package.sha256(package.VENDOR / name) != package.EXPECTED_HASHES[name]:
            raise AssertionError(f"vendor source changed: {name}")
        if "NO FABRICATION OR MASS CREDIT" not in row["project_use"]:
            raise AssertionError(f"source boundary missing: {name}")

    samples = rows("gripper-kinematic-samples.csv")
    if [row["configuration"] for row in samples] != [item[0] for item in package.CONFIGURATIONS]:
        raise AssertionError("kinematic configuration list mismatch")
    close(float(samples[0]["joint_displacement_q_mm"]), -11.0)
    close(float(samples[1]["joint_displacement_q_mm"]), 0.0)
    close(float(samples[2]["joint_displacement_q_mm"]), 20.0)
    close(float(samples[0]["closest_mesh_distance_mm"]), 0.059329, 0.0001)
    close(float(samples[1]["closest_mesh_distance_mm"]), 19.939267, 0.0001)
    close(float(samples[2]["closest_mesh_distance_mm"]), 59.106467, 0.0001)
    if any("NOT CERTIFIED JAW OPENING" not in row["interpretation"] for row in samples):
        raise AssertionError("mesh-distance interpretation was weakened")

    holds = rows("gripper-integration-holds.csv")
    if len(holds) != 7 or {row["hold_id"] for row in holds} != {f"GRH-{value:03d}" for value in range(1, 8)}:
        raise AssertionError("integration hold register incomplete")
    if any(row["status"] != "OPEN" for row in holds):
        raise AssertionError("an integration hold was closed without evidence")
    effects = " ".join(row["effect"].lower() for row in holds)
    for phrase in ("fabrication", "mass-002", "guarded motion", "grip-force", "assembly"):
        if phrase not in effects:
            raise AssertionError(f"missing fail-closed effect: {phrase}")

    sensitivity = rows("gripper-mass-load-sensitivity.csv")
    if len(sensitivity) != len(package.MASS_POINTS_G):
        raise AssertionError("mass sensitivity table incomplete")
    threshold = next(row for row in sensitivity if row["parameterized_unresolved_gripper_mass_g"] == "57.242")
    close(float(threshold["p0_7_total_if_only_this_unknown_remained_g"]), 750.0)
    if threshold["p0_7_750_g_screen"] != "WITHIN":
        raise AssertionError("P0.7 exact headroom row changed")
    after_threshold = next(row for row in sensitivity if row["parameterized_unresolved_gripper_mass_g"] == "75.000")
    if after_threshold["p0_7_750_g_screen"] != "OVER":
        raise AssertionError("P0.7 over-mass screen failed")
    if any("OTHER UNRESOLVED MOVING ITEMS" not in row["boundary"] for row in sensitivity):
        raise AssertionError("mass table could be misread as isolated gripper allowance")

    summary = json.loads((OUT / "gripper-geometry-summary.json").read_text(encoding="utf-8"))
    if summary["revision"] != package.REVISION or summary["upstream_commit"] != package.SOURCE_COMMIT:
        raise AssertionError("summary revision/source binding mismatch")
    if summary["mass_credit"] != "NONE - URDF inertial values and mesh volumes are not used as physical gripper mass":
        raise AssertionError("unsupported mass credit introduced")
    close(float(summary["controlled_p0_7_total_unresolved_headroom_g"]), 57.242)
    close(float(summary["r70_nonselected_total_unresolved_headroom_g"]), 115.225)
    if "OPEN" not in summary["integration_state"]:
        raise AssertionError("integration state was weakened")

    svg = (OUT / "HR-V0_gripper-reference-envelope.svg").read_text(encoding="utf-8")
    root = ET.fromstring(svg)
    if root.attrib.get("viewBox") != "0 0 1600 950":
        raise AssertionError("SVG viewBox changed")
    sizes = [int(value) for value in re.findall(r"font-size:\s*(\d+)px", svg)]
    if not sizes or min(sizes) < 16:
        raise AssertionError("SVG contains text below 16 px")
    if package.WARNING not in svg or "not certified jaw opening" not in svg.lower():
        raise AssertionError("SVG warning/boundary missing")

    html = (OUT / "HR-V0_gripper-reference-viewer.html").read_text(encoding="utf-8")
    for token in (package.WARNING, package.SOURCE_COMMIT, 'min="-11"', 'max="20"', "not Project Button manufacturing drawings"):
        if token not in html:
            raise AssertionError(f"interactive viewer missing {token!r}")
    css_sizes = [int(value) for value in re.findall(r"font-size:(\d+)px", html)]
    if not css_sizes or min(css_sizes) < 14:
        raise AssertionError("HTML interface text below 14 px")
    if re.search(r"font-size:(?:[0-9]|1[0-3])px", html):
        raise AssertionError("HTML contains undersized text")

    print("HR-V0 gripper integration check passed: exact source frozen, 3 reference poses, 7 holds open")
    print("PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
