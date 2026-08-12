#!/usr/bin/env python3
"""Fail-closed checks for the R273 P0.12 access-well stop package."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.12-access-well-stop"
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-access-well-fea-p0.1"
CAD_REL = ROOT / "release/hr-v0/arm-architecture-p0.12-access-well-stop"
FEA_REL = ROOT / "release/hr-v0/j2-stop-access-well-fea-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.37"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.37"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(value: bool, label: str) -> None:
    if not value:
        raise SystemExit(f"FAIL: {label}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((CAD / "p012-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-ARM-ARCH-P0.12-ACCESS-WELL-STOP-CANDIDATE" and status["round"] == "R273", "CAD identity")
    need(status["parent"] == "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE", "CAD parent")
    need(status["c07_m2p5_hole_depth_changed"] is False and status["c07_m2p5_access_wells_added"] is True, "A04 grip restoration")
    need(abs(status["c07_rear_access_well_diameter_mm"] - 5.2) < 1e-9 and abs(status["c07_original_a04_clamped_grip_restored_mm"] - 9.525) < 1e-9, "access-well controls")
    for key in ("selected", "fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(status[key] is False, f"CAD {key}")

    c07 = cq.importers.importStep(str(CAD / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    box = c07.BoundingBox()
    need(abs(box.xmin + 54.0) < 1e-6 and abs(box.xmax - 54.0) < 1e-6 and abs(box.ymin + 15.875) < 1e-5 and abs(box.ymax - 9.525) < 1e-6, "C07 envelope")
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            open_probe = cq.Solid.makeCylinder(2.59, 15.80, cq.Vector(x, -15.84, z), cq.Vector(0, 1, 0))
            seat_annulus_probe = cq.Solid.makeCylinder(2.25, 0.20, cq.Vector(x, 0.01, z), cq.Vector(0, 1, 0))
            need(c07.intersect(open_probe).Volume() < 1e-8, f"open access well {x},{z}")
            need(c07.intersect(seat_annulus_probe).Volume() > 1.0, f"head seat retained {x},{z}")

    clearance = json.loads((CAD / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    need(clearance["pair_count"] == 69 and clearance["minimum_guaranteed_clearance_mm"] >= 0.75, "continuous clearance")
    stop = json.loads((CAD / "j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    need(abs(stop["nominal_metal_contact_deg"] - 118.0) < 1e-6 and "access wells" in stop["architecture"], "stop/contact architecture")
    a04 = next(row for row in rows(CAD / "interface-schedule.csv") if row["interface"] == "A04")
    need("5.20" in a04["pattern"] and "9.525" in a04["pattern"] and "SELECTION REQUIRED" in a04["fasteners"], "A04 schedule")

    envelope = rows(CAD / "a04-fastener-envelope-screen.csv")[0]
    need(abs(float(envelope["radial_head_clearance_mm"]) - 0.350) < 1e-9, "head clearance")
    need(abs(float(envelope["minimum_inner_web_ligament_mm_nominal"]) - 1.400) < 1e-9, "web ligament")
    need(abs(float(envelope["screen_thread_beyond_nut_pitches"]) - 4.500) < 1e-9, "thread screen")
    need(float(envelope["nominal_shank_envelope_to_exact_xm540_mm"]) > 18.0 and "PHYSICAL PROOF OPEN" in envelope["result"], "XM540 envelope/boundary")
    sources = rows(CAD / "a04-hardware-source-register.csv")
    need(len(sources) == 4 and all("SELECTION REQUIRED" in row["selection_state"] or "REFERENCE VERIFIED" in row["selection_state"] for row in sources), "source records fail closed")
    need(sum("unavailable" in row["availability"] or "discontinued" in row["availability"] for row in sources) >= 2, "stale availability disclosed")
    demand = rows(CAD / "a04-joint-demand-screen.csv")[0]
    need(abs(float(demand["maximum_absolute_axial_reaction_n"]) - 392.085) < 0.001, "axial demand")
    need(abs(float(demand["maximum_in_plane_shear_reaction_n"]) - 112.275) < 0.001, "shear demand")
    need(abs(float(demand["maximum_combined_reaction_n"]) - 407.844) < 0.001 and demand["result"] == "DEMAND CALCULATED - NO CAPACITY OR PASS CLAIM", "combined demand/boundary")
    need(len(rows(CAD / "open-holds.csv")) == 15 and len(rows(CAD / "acceptance-matrix.csv")) == 15, "CAD evidence rows")

    analysis = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    need(analysis["identifier"] == "HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1" and analysis["round"] == "R273", "FEA identity")
    expected = {"C06": (17.914835713103184, 71.65934285241273), "C07": (25.671009726441117, 102.68403890576447)}
    for part, (global_max, four_x) in expected.items():
        record = analysis["parts"][part]
        need(abs(record["finest_global_maximum_mpa"] - global_max) < 1e-9, f"{part} global")
        need(abs(record["four_x_global_maximum_mpa"] - four_x) < 1e-9 and record["four_x_result"] == "PASS INTERIM REJECTION SCREEN", f"{part} screen")
    need(analysis["joined_fastener_model_complete"] is False and analysis["selected"] is False and analysis["energization_authorized"] is False and analysis["safety_credit"] is False, "FEA fail closed")
    need(len(rows(FEA / "mesh-convergence.csv")) == 6 and len(rows(FEA / "open-holds.csv")) == 15, "FEA rows")

    config = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(config["identifier"] == "HR-V0-CONFIG-REC-P0.37" and config["current_records"] == 56 and config["supersession_records"] == 51, "config identity/counts")
    need(config["open_holds"] == 306 and config["acceptance_rows"] == 360, "config evidence counts")
    need(config["p012_disposition"] == "PASSES INTERNAL LINEAR REJECTION SCREEN - UNSELECTED", "config disposition")
    for key in ("fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(config[key] is False, f"config {key}")

    page = (FEA_REL / "index.html").read_text(encoding="utf-8")
    for token in ("assemblable access concept", "25.671 MPa", "407.844 N", "font:clamp(16px", "font-size:14px", WARNING):
        need(token in page, f"page {token}")
    for directory in (CAD_REL, FEA, FEA_REL, CFG, CFG_REL):
        for record in rows(directory / "file-manifest.csv"):
            path = directory / record["relative_path"]
            need(path.is_file() and sha(path) == record["sha256"] and path.stat().st_size == int(record["bytes"]), f"manifest {path}")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R273 access-well J2 stop candidate:", "R274 A04 exact-candidate joint package:", "R275 J2 soft-contact pad boundary:", "R276 exact-contact J2 pad correction:")), "handoff")
    need("| R273 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "ledger")
    need("Two hundred seventy-six rounds are complete: R01-R276." in (ROOT / "README.md").read_text(encoding="utf-8"), "README count")
    print("R273 P0.12 access-well stop package checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
