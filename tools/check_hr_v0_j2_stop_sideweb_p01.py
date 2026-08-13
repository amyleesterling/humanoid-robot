#!/usr/bin/env python3
"""Fail-closed checks for R272 mixed-side stop evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.11-side-web-stop"
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-sideweb-fea-p0.1"
CAD_REL = ROOT / "release/hr-v0/arm-architecture-p0.11-side-web-stop"
FEA_REL = ROOT / "release/hr-v0/j2-stop-sideweb-fea-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.36"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.36"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(value: bool, label: str) -> None:
    if not value: raise SystemExit(f"FAIL: {label}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cad = json.loads((CAD / "p011-status.json").read_text(encoding="utf-8"))
    need(cad["identifier"] == "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE" and cad["round"] == "R272", "CAD identity")
    need(cad["striker_top_z_changed_from_p010"] is True and abs(cad["striker_top_z_mm"] - 36.026374) < 1e-9, "retuned striker")
    need(cad["c07_m2p5_hole_depth_changed"] is True and cad["c07_m2p5_fastener_stack"] == "SELECTION REQUIRED", "C07 stack hold")
    for key in ("selected","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(cad[key] is False, f"CAD {key}")
    clearance = json.loads((CAD / "continuous-clearance-analysis.json").read_text(encoding="utf-8"))
    need(clearance["pair_count"] == 69 and clearance["minimum_guaranteed_clearance_mm"] >= 0.75, "continuous clearance")
    stop = json.loads((CAD / "j2-positive-stop-analysis.json").read_text(encoding="utf-8"))
    need(abs(stop["nominal_metal_contact_deg"] - 118.0) < 1e-6, "stop contact")
    interfaces = rows(CAD / "interface-schedule.csv")
    a04 = next(row for row in interfaces if row["interface"] == "A04")
    need("25.4 mm" in a04["pattern"] and "SELECTION REQUIRED" in a04["fasteners"], "A04 changed stack")

    status = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-STOP-SIDEWEB-FEA-P0.1" and status["round"] == "R272", "FEA identity")
    expected = {"C06": (17.914835713103184, 71.65934285241273), "C07": (7.845007096449407, 31.38002838579763)}
    for part, (global_max, four_x) in expected.items():
        record = status["parts"][part]
        need(abs(record["finest_global_maximum_mpa"] - global_max) < 1e-9, f"{part} global")
        need(abs(record["four_x_global_maximum_mpa"] - four_x) < 1e-9 and record["four_x_result"] == "PASS INTERIM REJECTION SCREEN", f"{part} screen")
    need(len(rows(FEA / "mesh-convergence.csv")) == 6 and len(rows(FEA / "open-holds.csv")) == 12, "FEA rows")
    need(status["selected"] is False and status["fabrication_authorized"] is False and status["energization_authorized"] is False and status["safety_credit"] is False, "FEA fail closed")

    cfg = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"] == "HR-V0-CONFIG-REC-P0.36" and cfg["current_records"] == 54 and cfg["supersession_records"] == 50, "config identity/counts")
    need(cfg["open_holds"] == 291 and cfg["acceptance_rows"] == 345, "config evidence counts")
    need(cfg["p011_disposition"] == "PASSES INTERNAL LINEAR REJECTION SCREEN - UNSELECTED", "config disposition")
    for key in ("fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(cfg[key] is False, f"config {key}")

    page = (FEA_REL / "index.html").read_text(encoding="utf-8")
    for token in ("A stronger stop candidate survives the internal screen", "17.915 MPa", "7.845 MPa", "font:clamp(16px", "font-size:14px", WARNING): need(token in page, f"page {token}")
    for directory in (CAD_REL, FEA, FEA_REL, CFG, CFG_REL):
        for record in rows(directory / "file-manifest.csv"):
            path = directory / record["relative_path"]
            need(path.is_file() and sha(path) == record["sha256"] and path.stat().st_size == int(record["bytes"]), f"manifest {path}")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R272 mixed-side J2 stop candidate:", "R273 access-well J2 stop candidate:", "R274 A04 exact-candidate joint package:", "R275 J2 soft-contact pad boundary:", "R276 exact-contact J2 pad correction:", "R277 J2 pad-pocket correction:", "R278 exact-normal J2 stop correction:", "R279 J2 convergence protocol:", "R280 J2 refinement execution feasibility:", "R281 J2 numerical backend:", "R282 J2 refinement erratum:", "R283 J2 execution architecture:")), "handoff")
    need("| R272 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "ledger")
    print("R272 mixed-side stop package checks: PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
