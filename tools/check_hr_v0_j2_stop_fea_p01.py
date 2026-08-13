#!/usr/bin/env python3
"""Fail-closed checks for R271 C06 linear FEA evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mechanical/analysis/hr-v0-j2-stop-fea-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-fea-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.35"
REQ = ROOT / "tools/requirements-structural-analysis.txt"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(value: bool, label: str) -> None:
    if not value: raise SystemExit(f"FAIL: {label}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    status = json.loads((SRC / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-STOP-FEA-P0.1" and status["round"] == "R271", "identity")
    need(status["solver"] == {"gmsh":"4.15.2","scikit_fem":"12.0.2","scipy":"1.18.0","element":"first-order tetrahedron","analysis":"small-displacement isotropic linear elasticity"}, "solver binding")
    requirements = REQ.read_text(encoding="utf-8").splitlines()
    need("gmsh==4.15.2" in requirements and "meshio==5.3.5" in requirements and "scikit-fem==12.0.2" in requirements, "pinned structural-analysis dependencies")
    need(status["mesh_levels_mm"] == [4.0,3.0,2.0], "mesh levels")
    need(status["convergence_acceptance"].startswith("NOT ESTABLISHED"), "convergence boundary")
    need(status["selected"] is False and status["fabrication_authorized"] is False and status["energization_authorized"] is False and status["safety_credit"] is False, "fail closed")
    convergence = rows(SRC / "mesh-convergence.csv")
    need(len(convergence) == 3, "convergence rows")
    need([float(row["mesh_size_mm"]) for row in convergence] == [4.0,3.0,2.0], "convergence order")
    finest = convergence[-1]
    need(int(finest["nodes"]) == 9229 and int(finest["tetrahedra"]) == 39187, "finest mesh")
    need(abs(float(finest["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"]) - 122.20542897666164) < 1e-8, "root max")
    need(abs(float(finest["global_maximum_element_von_mises_mpa_mesh_sensitive"]) - 180.57336889973817) < 1e-8, "global max")
    need(abs(float(finest["maximum_displacement_mm"]) - 0.415553702136105) < 1e-10, "displacement")
    need(float(finest["normalized_force_balance_error"]) < 1e-10, "force balance")
    need(finest["four_x_rejection_result"] == "FAIL INTERIM REJECTION SCREEN", "screen disposition")
    cases = rows(SRC / "finest-mesh-load-cases.csv")
    need(len(cases) == 3, "load cases")
    single = next(row for row in cases if row["case_id"] == "STATIC-PUBLISHED-ENDPOINT-SINGLE")
    twin = next(row for row in cases if row["case_id"] == "STATIC-PUBLISHED-ENDPOINT-EQUAL-TWIN")
    need(float(single["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"]) > 1.95 * float(twin["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"]), "single rail governs")
    need(len(rows(SRC / "open-holds.csv")) == 9 and len(rows(SRC / "acceptance-matrix.csv")) == 9, "open evidence")
    for record in rows(SRC / "mesh-artifact-register.csv"):
        capsule = SRC / record["capsule"]
        need(capsule.is_file() and sha(capsule) == record["sha256"] and capsule.stat().st_size == int(record["bytes"]), "mesh capsule")
        with np.load(capsule) as data:
            need(data["points_mm"].shape[1] == 3 and data["tetrahedra"].shape[1] == 4, "capsule arrays")
    need((SRC / "c06-single-endpoint-finest.vtu").stat().st_size > 1_000_000, "VTU")
    for image in ("mesh-convergence.svg","mesh-convergence.png","c06-stress-slice.svg","c06-stress-slice.png"):
        need((SRC / image).stat().st_size > 10_000, f"plot {image}")
    page = (REL / "index.html").read_text(encoding="utf-8")
    for token in ("P0.10 fails the strengthened stop screen", "122.205", "180.573", "font:clamp(16px", "font-size:14px", WARNING): need(token in page, f"page {token}")
    config = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(config["identifier"] == "HR-V0-CONFIG-REC-P0.35" and config["current_records"] == 52 and config["supersession_records"] == 49, "config ids")
    need(config["open_holds"] == 279 and config["acceptance_rows"] == 333, "config counts")
    need(config["current_mechanical_identifier"] == "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE", "P0.8 current")
    need(config["p010_fea_disposition"] == "FAILS INTERIM FULL-PART SCREEN - UNSELECTED", "P0.10 disposition")
    for key in ("fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(config[key] is False, f"config {key}")
    for directory in (SRC, REL, CFG, ROOT / "release/hr-v0/configuration-reconciliation-p0.35"):
        for record in rows(directory / "file-manifest.csv"):
            path = directory / record["relative_path"]
            need(path.is_file() and sha(path) == record["sha256"] and path.stat().st_size == int(record["bytes"]), f"manifest {path}")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R271 C06 full-part FEA rejection screen:", "R272 mixed-side J2 stop candidate:", "R273 access-well J2 stop candidate:", "R274 A04 exact-candidate joint package:", "R275 J2 soft-contact pad boundary:", "R276 exact-contact J2 pad correction:", "R277 J2 pad-pocket correction:", "R278 exact-normal J2 stop correction:", "R279 J2 convergence protocol:", "R280 J2 refinement execution feasibility:", "R281 J2 numerical backend:", "R282 J2 refinement erratum:", "R283 J2 execution architecture:")), "handoff")
    need("| R271 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "ledger")
    print("R271 C06 FEA package checks: PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
