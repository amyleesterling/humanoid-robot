#!/usr/bin/env python3
"""Fail-closed checks for the R277 P0.13 J2 pad-pocket CAD candidate."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
P012 = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
P013 = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def imported(path: Path) -> cq.Shape:
    return cq.importers.importStep(str(path)).val()


def main() -> int:
    status = json.loads((P013 / "p013-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE", "identity drift")
    need(status["round"] == "R277" and status["parent"].endswith("P0.12-ACCESS-WELL-STOP-CANDIDATE"), "lineage drift")
    need(status["pad_pocket_quantity"] == 2 and status["metal_backup_unchanged"] is True, "pocket/backup drift")
    need(status["pad_structural_credit"] is False and status["selected"] is False, "selection or strength-credit drift")
    need(not any(status[k] for k in ("fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit")), "authority drift")

    p012 = imported(P012 / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step")
    p013 = imported(P013 / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step")
    expected_removed = 2.0 * (12.4 * 40.4 - (4.0 - math.pi) * 2.0**2) * 0.52
    need(math.isclose(p012.Volume() - p013.Volume(), expected_removed, abs_tol=1e-4), "exact pocket volume drift")
    for attr in ("xlen", "ylen", "zlen"):
        need(math.isclose(getattr(p012.BoundingBox(), attr), getattr(p013.BoundingBox(), attr), abs_tol=1e-5), f"C07 outer {attr} drift")

    installed = imported(P013 / "HR-V0_J2_C07_pad-pocket-installed-screen.step")
    need(len(installed.Solids()) == 3, "installed screen must contain one C07 plus two pads")
    need(math.isclose(installed.BoundingBox().ymax, p013.BoundingBox().ymax, abs_tol=1e-5), "pads escape the existing C07 gross envelope")
    need((P013 / "HR-V0_J2_C07_pad-pocket-installed-screen.glb").stat().st_size > 100_000, "interactive GLB missing")

    definition = rows(P013 / "j2-pad-pocket-definition.csv")
    need(len(definition) == 1 and definition[0]["rail_centers_x_mm"] == "-44.000;+44.000", "pocket definition drift")
    need("DEPENDENT FEATURE" in definition[0]["depth_rule"] and "no pad strength credit" in definition[0]["metal_backup"], "dependent-depth boundary missing")
    tolerance = rows(P013 / "j2-pad-pocket-tolerance-screen.csv")
    need(len(tolerance) == 3, "tolerance screen count drift")
    values = [float(row["protrusion_mm"]) for row in tolerance]
    need(values == [0.09, -0.01, 0.19], f"pad-only sensitivity drift: {values}")
    need(all(WARNING in row["warning"] for row in tolerance), "warning missing from tolerance screen")
    need(len(rows(P013 / "j2-pad-pocket-inspection.csv")) == 4, "inspection plan drift")
    need(len(rows(P013 / "open-holds.csv")) == 20 and len(rows(P013 / "acceptance-matrix.csv")) == 20, "hold/acceptance drift")
    need(all(row["state"] == "OPEN" for row in rows(P013 / "open-holds.csv")), "hold state drift")
    need("R277-CH-05" in {row["change_id"] for row in rows(P013 / "design-change-register.csv")}, "change record missing")
    print("PASS: R277 P0.13 has two exact pad pockets, dependent depth and unchanged metal backup; no work or safety authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
