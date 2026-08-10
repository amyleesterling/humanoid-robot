"""Fail-closed checks for HR-V0-GRIP-ADAPT-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/pololu-gripper-adapter-p0.1"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def near(actual: float, expected: float, tolerance: float = 1e-4) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def main() -> int:
    adapter = cq.importers.importStep(str(OUT / "hr-v0-pololu-gripper-adapter-p0.1.step"))
    solids = adapter.solids().vals()
    assert len(solids) == 1
    box = adapter.val().BoundingBox()
    for actual, expected in zip((box.xlen, box.ylen, box.zlen), (40.0, 28.5, 40.0)):
        near(actual, expected)
    near(adapter.val().Volume(), 9366.558784, 1e-3)

    assembly = cq.importers.importStep(str(OUT / "hr-v0-pololu-gripper-adapter-assembly-p0.1.step"))
    assert len(assembly.solids().vals()) == 4
    assert (OUT / "hr-v0-pololu-gripper-adapter-assembly-p0.1.glb").stat().st_size > 10000

    feature = rows("feature-register.csv")
    assert [r["feature_id"] for r in feature] == [f"PAF-{i:03d}" for i in range(1, 5)]
    collision = rows("collision-register.csv")
    assert [r["minimum_nominal_separation_mm"] for r in collision] == ["0.300", "8.122", "11.161"]
    holds = rows("hold-register.csv")
    assert [r["hold_id"] for r in holds] == [f"PAH-{i:03d}" for i in range(1, 13)]
    assert all(r["state"] == "OPEN" for r in holds)
    analysis = {r["analysis_id"]: r for r in rows("analysis-register.csv")}
    assert "25.289709 g" in analysis["PAA-002"]["result"]
    assert "117.619291 g" in analysis["PAA-003"]["result"]
    assert "screen only" in analysis["PAA-005"]["boundary"]

    summary = json.loads((OUT / "package-summary.json").read_text(encoding="utf-8"))
    assert summary["identifier"] == "HR-V0-GRIP-ADAPT-P0.1"
    near(summary["adapter_mass_g"], 25.289709, 1e-6)
    near(summary["remaining_arithmetic_headroom_g"], 117.619291, 1e-6)
    assert summary["hold_count"] == 12 and summary["requirements_closed"] == 0
    for flag in ("procurement_release", "fabrication_release", "assembly_release", "motion_release", "energization_release"):
        assert summary[flag] is False

    drawing = (OUT / "hr-v0-pololu-gripper-adapter-drawing-p0.1.svg").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/gripper-adapter-p0.1/index.html").read_text(encoding="utf-8")
    for token in ("PRELIMINARY", "SELECTION REQUIRED", "not fabrication authority"):
        assert token in drawing
    for token in ("PRELIMINARY", "not a selected configuration", "font:16px", "font-size:14px", "model-viewer", "No ordering"):
        assert token in guide
    assert "@media(max-width:620px)" in guide
    print("HR-V0 Pololu adapter P0.1 check passed: exact STEP/assembly parsed; 12 release holds remain open")
    print("PRELIMINARY - NOT RELEASED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
