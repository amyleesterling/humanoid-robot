#!/usr/bin/env python3
"""Fail-closed repository checks for the R270 J2 stop correction."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop"
REL = ROOT / "release/hr-v0/j2-stop-bossed-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.34"
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
    status = json.loads((CAD / "p010-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE", "CAD id")
    need(status["load_model_identifier"] == "HR-V0-J2-STOP-LOAD-MODEL-P0.2", "load model id")
    need(abs(float(status["cad_effective_normal_moment_arm_mm"]) - 19.115315) < 1e-6, "effective arm")
    need(status["contact_face_and_hole_axes_changed"] is False, "interfaces preserved")
    need(status["striker_rail_width_mm"] == 16.0 and status["catch_rail_width_mm"] == 18.0, "rail widths")
    need(status["selected"] is False and status["energization_authorized"] is False and status["safety_credit"] is False, "fail closed")
    need(not (CAD / "j2-positive-stop-load-screen.csv").exists(), "superseded radius load file removed")
    need(not (CAD / "combined-factor-envelope.csv").exists(), "misleading combined factor removed")

    c06 = cq.importers.importStep(str(CAD / "parts/MV0-C06_J2_positive_moving_striker_adapter.step")).val()
    c07 = cq.importers.importStep(str(CAD / "parts/MV0-C07_J2_positive_fixed_catch_adapter.step")).val()
    b06, b07 = c06.BoundingBox(), c07.BoundingBox()
    need(abs(b06.xmin + 51.0) < 1e-6 and abs(b06.xmax - 51.0) < 1e-6, "C06 width")
    need(abs(b07.xmin + 52.0) < 1e-6 and abs(b07.xmax - 52.0) < 1e-6, "C07 width")
    need(abs(b06.ymin + 6.35) < 1e-6 and abs(b06.ymax - 9.525) < 1e-6, "C06 stock envelope")
    need(abs(b07.ymin + 6.35) < 1e-6 and abs(b07.ymax - 9.525) < 1e-6, "C07 stock envelope")
    central_back_probe = cq.Solid.makeBox(4.0, 6.0, 4.0, cq.Vector(-2.0, -6.1, -2.0))
    rail_back_probe = cq.Solid.makeBox(2.0, 6.0, 4.0, cq.Vector(40.0, -6.1, 0.0))
    need(c06.intersect(central_back_probe).Volume() < 1e-9, "central mounting land not thickened")
    need(c06.intersect(rail_back_probe).Volume() > 40.0, "integral rail boss exists")

    contact = json.loads((CAD / "cad-contact-normal-evidence.json").read_text(encoding="utf-8"))
    chosen = contact["selected_conservative_solution"]
    need(contact["governing_relation"] == "T_x = F_n * abs((r cross n)_x)", "axis-specific relation")
    need(float(contact["face_gap_mm"]) < 0.00004, "near-contact kernel sample")
    need(all(abs(float(a) - float(b)) < 1e-9 for a, b in zip(chosen["normal_fixed_to_moving"], [0.0, 1.0, 0.0])), "contact normal")

    static = rows(CAD / "corrected-static-stop-screen.csv")
    need(len(static) == 2, "static cases")
    endpoint = static[-1]
    need(abs(float(endpoint["reaction_torque_nm"]) - 11.137) < 1e-6, "stall plus gravity")
    need(abs(float(endpoint["single_rail_normal_force_n"]) - 582.622) < 0.001, "single rail force")
    need(abs(float(endpoint["nominal_beam_stress_mpa"]) - 50.864) < 0.001, "nominal screen")
    factors = rows(CAD / "static-geometry-factor-screen.csv")
    need(len(factors) == 4 and factors[-1]["result"] == "PASS INTERIM REJECTION SCREEN", "4x rejection screen")
    need("not an impact factor" in factors[-1]["interpretation"], "factor boundary")
    need(len(rows(CAD / "impact-energy-sensitivity.csv")) == 10, "impact sensitivity rows")
    bumper = rows(CAD / "bumper-test-candidate.csv")[0]
    need(bumper["manufacturer_product_number"] == "2300327" and bumper["structural_stop_credit"] == "NONE", "bumper boundary")
    need(len(rows(CAD / "open-holds.csv")) == 12 and len(rows(CAD / "acceptance-matrix.csv")) == 12, "open evidence")

    rel_status = json.loads((REL / "package-status.json").read_text(encoding="utf-8"))
    need(rel_status["r269_load_model_disposition"].startswith("SUPERSEDED"), "R269 disposition")
    need(rel_status["all_18_sol_blockers_qualified_closed"] is False, "Sol blocker truth")
    page = (REL / "index.html").read_text(encoding="utf-8")
    need("R269’s 61.344 MPa result is superseded" in page, "web correction")
    need("font:clamp(16px" in page and "font-size:14px" in page, "legible CSS floors")
    need(WARNING in page, "page warning")

    config = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(config["identifier"] == "HR-V0-CONFIG-REC-P0.34" and config["current_records"] == 51, "config")
    need(config["open_holds"] == 270 and config["acceptance_rows"] == 324, "config counts")
    need(config["current_mechanical_identifier"] == "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "P0.8 remains current")
    for key in ("fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit"):
        need(config[key] is False, f"config {key}")

    for directory in (ROOT / "mechanical/analysis/hr-v0-j2-stop-bossed-p0.1", REL, CFG, ROOT / "release/hr-v0/configuration-reconciliation-p0.34"):
        manifest = rows(directory / "file-manifest.csv")
        for row in manifest:
            path = directory / row["relative_path"]
            need(path.is_file() and sha(path) == row["sha256"] and path.stat().st_size == int(row["bytes"]), f"manifest {path}")
    need("| R270 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "review ledger")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R270 corrected J2 contact/load model:", "R271 C06 full-part FEA rejection screen:", "R272 mixed-side J2 stop candidate:", "R273 access-well J2 stop candidate:", "R274 A04 exact-candidate joint package:", "R275 J2 soft-contact pad boundary:", "R276 exact-contact J2 pad correction:", "R277 J2 pad-pocket correction:", "R278 exact-normal J2 stop correction:")), "handoff")
    print("R270 corrected J2 stop package checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
