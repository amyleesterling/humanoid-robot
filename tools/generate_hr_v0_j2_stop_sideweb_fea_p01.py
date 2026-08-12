#!/usr/bin/env python3
"""Generate R272 linear-elastic C06/C07 screening for exact P0.11 CAD.

This fixed-hole/distributed-load model is a geometry rejection screen.  It is
not nonlinear contact, a validated bolt joint, a qualified allowable, or work
authority.
"""
from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import numpy as np
from skfem import Basis, ElementTetP1, ElementVector, FacetBasis, LinearForm, MeshTet, asm, condense, solve
from skfem.models.elasticity import lame_parameters, linear_elasticity

import generate_hr_v0_j2_stop_fea_p01 as base


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.11-side-web-stop"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-sideweb-fea-p0.1"
ID = "HR-V0-J2-STOP-SIDEWEB-FEA-P0.1"
CAD_ID = "HR-V0-ARM-ARCH-P0.11-SIDE-WEB-STOP-CANDIDATE"
STATIC = CAD / "corrected-static-stop-screen.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
MESH_LEVELS = (4.0, 3.0, 2.0)
FORCE_N = 0.0
STRIKER_TOP_Z = 36.026374


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fixed_hole_nodes(mesh: MeshTet) -> np.ndarray:
    p = mesh.p
    nodes: list[int] = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            radial = np.sqrt((p[0] - x) ** 2 + (p[2] - z) ** 2)
            nodes.extend(np.where((np.abs(radial - 1.35) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    for z in (-10.0, 10.0):
        radial = np.sqrt(p[0] ** 2 + (p[2] - z) ** 2)
        nodes.extend(np.where((np.abs(radial - 2.75) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    return np.asarray(sorted(set(nodes)), dtype=np.int64)


def facets_area(mesh: MeshTet, facets: np.ndarray) -> float:
    total = 0.0
    for triangle in mesh.facets[:, facets].T:
        a, b, c = mesh.p[:, triangle].T
        total += np.linalg.norm(np.cross(b - a, c - a)) / 2.0
    return float(total)


def c07_boundary(mesh: MeshTet) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    boundary = mesh.boundary_facets()
    centers = mesh.p[:, mesh.facets[:, boundary]].mean(axis=1)
    positive = boundary[(np.abs(centers[1] - 8.525) < 1e-5) & (centers[0] > 34.0)]
    negative = boundary[(np.abs(centers[1] - 8.525) < 1e-5) & (centers[0] < -34.0)]
    p = mesh.p
    nodes: list[int] = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            radial = np.sqrt((p[0] - x) ** 2 + (p[2] - z) ** 2)
            nodes.extend(np.where((np.abs(radial - 1.35) < 1e-4) & (p[1] >= -15.87501) & (p[1] <= 9.52501))[0])
    for z in (-10.0, 10.0):
        radial = np.sqrt(p[0] ** 2 + (p[2] - z) ** 2)
        nodes.extend(np.where((np.abs(radial - 2.75) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    fixed = np.asarray(sorted(set(nodes)), dtype=np.int64)
    if len(fixed) < 80 or len(positive) < 8 or len(negative) < 8:
        raise RuntimeError(f"C07 boundary selection failed: fixed={len(fixed)} positive={len(positive)} negative={len(negative)}")
    return fixed, positive, negative, facets_area(mesh, positive), facets_area(mesh, negative)


def c06_boundary(mesh: MeshTet) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    boundary = mesh.boundary_facets()
    centers = mesh.p[:, mesh.facets[:, boundary]].mean(axis=1)
    positive = boundary[(np.abs(centers[2] - STRIKER_TOP_Z) < 1e-5) & (centers[0] > 35.0)]
    negative = boundary[(np.abs(centers[2] - STRIKER_TOP_Z) < 1e-5) & (centers[0] < -35.0)]
    fixed = fixed_hole_nodes(mesh)
    if len(fixed) < 80 or len(positive) < 8 or len(negative) < 8:
        raise RuntimeError(f"C06 boundary selection failed: fixed={len(fixed)} positive={len(positive)} negative={len(negative)}")
    return fixed, positive, negative, facets_area(mesh, positive), facets_area(mesh, negative)


def solve_c07(
    mesh: MeshTet,
    basis: Basis,
    stiffness,
    fixed: np.ndarray,
    positive: np.ndarray,
    area: float,
    lam: float,
    mu: float,
) -> tuple[dict[str, object], np.ndarray]:
    traction = np.asarray((0.0, -FORCE_N / area, 0.0))

    @LinearForm
    def load(v, _w):
        return traction[1] * v[1]

    load_vector = asm(load, FacetBasis(mesh, ElementVector(ElementTetP1()), facets=positive))
    displacement = solve(*condense(stiffness, load_vector, D=basis.nodal_dofs[:, fixed].ravel()))
    von_mises, _ = base.element_stress(mesh, displacement, lam, mu)
    centroids = mesh.p[:, mesh.t].mean(axis=1).T
    root = (centroids[:, 0] > 20.0) & (centroids[:, 2] > -22.0) & (centroids[:, 2] < 22.0)
    reaction = stiffness @ displacement - load_vector
    imbalance = reaction.reshape((-1, 3))[fixed].sum(axis=0) + load_vector.reshape((-1, 3)).sum(axis=0)
    root_values = von_mises[root]
    result = {
        "maximum_displacement_mm": float(np.max(np.linalg.norm(displacement.reshape((-1, 3)), axis=1))),
        "global_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(von_mises)),
        "global_p99_element_von_mises_mpa": float(np.quantile(von_mises, 0.99)),
        "positive_root_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(root_values)),
        "positive_root_p99_element_von_mises_mpa": float(np.quantile(root_values, 0.99)),
        "normalized_force_balance_error": float(np.linalg.norm(imbalance) / FORCE_N),
    }
    return result, von_mises


def main() -> int:
    global FORCE_N
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    with STATIC.open(newline="", encoding="utf-8-sig") as stream:
        static_rows = list(csv.DictReader(stream))
    FORCE_N = float(static_rows[-1]["single_rail_normal_force_n"])
    lam, mu = lame_parameters(base.E_MPA, base.POISSON)
    base.TOP_Z = STRIKER_TOP_Z
    rows: list[dict[str, object]] = []

    for part_id, filename in (
        ("C06", "MV0-C06_J2_positive_moving_striker_adapter.step"),
        ("C07", "MV0-C07_J2_positive_fixed_catch_adapter.step"),
    ):
        base.STEP = CAD / "parts" / filename
        for mesh_size in MESH_LEVELS:
            points, tets, meta = base.build_mesh(mesh_size)
            mesh = MeshTet(points.T, tets.T)
            element = ElementVector(ElementTetP1())
            basis = Basis(mesh, element)
            stiffness = asm(linear_elasticity(lam, mu), basis)
            if part_id == "C06":
                fixed, positive, negative, positive_area, negative_area = c06_boundary(mesh)
                result, _u, _vm = base.solve_case(
                    mesh, basis, stiffness, fixed, positive, negative,
                    positive_area, negative_area, FORCE_N, "single_positive",
                    lam, mu, root_min_x_mm=20.0, root_z_min_mm=-22.0, root_z_max_mm=22.0,
                )
            else:
                fixed, positive, negative, positive_area, negative_area = c07_boundary(mesh)
                result, _vm = solve_c07(mesh, basis, stiffness, fixed, positive, positive_area, lam, mu)
            centroids = mesh.p[:, mesh.t].mean(axis=1).T
            max_index = int(np.argmax(_vm))
            result["global_maximum_centroid_x_mm"] = float(centroids[max_index, 0])
            result["global_maximum_centroid_y_mm"] = float(centroids[max_index, 1])
            result["global_maximum_centroid_z_mm"] = float(centroids[max_index, 2])
            root_max = float(result["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"])
            global_max = float(result["global_maximum_element_von_mises_mpa_mesh_sensitive"])
            rows.append(
                {
                    "part_id": part_id,
                    "mesh_size_mm": mesh_size,
                    "nodes": meta["nodes"],
                    "tetrahedra": meta["tetrahedra"],
                    "minimum_minSICN": meta["minimum_minSICN"],
                    "single_rail_load_area_mm2": positive_area,
                    "single_rail_resultant_n": FORCE_N,
                    **result,
                    "four_x_linear_scaled_global_max_mpa_not_impact_model": 4.0 * global_max,
                    "four_x_rejection_result": "PASS INTERIM REJECTION SCREEN" if 4.0 * global_max <= base.PROJECT_MTR_THRESHOLD_MPA else "FAIL INTERIM REJECTION SCREEN",
                    "model_boundary": "fixed hole surfaces; distributed nominal contact-face resultant; nonlinear contact/bolt/frame/dynamics excluded",
                    "warning": WARNING,
                }
            )
    write_csv(OUT / "mesh-convergence.csv", rows)

    status_parts: dict[str, object] = {}
    for part_id in ("C06", "C07"):
        part_rows = [row for row in rows if row["part_id"] == part_id]
        finest = part_rows[-1]
        previous = part_rows[-2]
        status_parts[part_id] = {
            "finest_root_maximum_mpa": finest["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"],
            "finest_global_maximum_mpa": finest["global_maximum_element_von_mises_mpa_mesh_sensitive"],
            "finest_maximum_displacement_mm": finest["maximum_displacement_mm"],
            "four_x_global_maximum_mpa": finest["four_x_linear_scaled_global_max_mpa_not_impact_model"],
            "four_x_result": finest["four_x_rejection_result"],
            "final_two_mesh_global_maximum_relative_change": abs(float(finest["global_maximum_element_von_mises_mpa_mesh_sensitive"]) - float(previous["global_maximum_element_von_mises_mpa_mesh_sensitive"])) / float(finest["global_maximum_element_von_mises_mpa_mesh_sensitive"]),
        }
    status = {
        "identifier": ID,
        "round": "R272",
        "cad_identifier": CAD_ID,
        "parts": status_parts,
        "solver": {"gmsh": base.gmsh.__version__, "scikit_fem": base.skfem.__version__, "scipy": base.scipy.__version__, "element": "first-order tetrahedron", "analysis": "small-displacement isotropic linear elasticity"},
        "material_model": {"youngs_modulus_mpa": base.E_MPA, "poisson_ratio_assumption": base.POISSON, "project_mtr_threshold_mpa": base.PROJECT_MTR_THRESHOLD_MPA, "allowable_released": False},
        "convergence_acceptance": "NOT ESTABLISHED; mesh-sensitive extrema and idealized restraints/contact preclude qualified convergence",
        "selected": False,
        "fabrication_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    holds = [
        "Qualified reviewer accepts P0.11 CAD, contact-normal extraction, 118 degree retuned striker datum and analysis scope",
        "C07 M2.5 length, grip, head/nut/washer stack, torque, locking, reuse and tool access are selected and accepted",
        "C06 and C07 bolt/frame/extrusion contact, preload, clearance, slip, bearing and prying are modeled and physically calibrated",
        "Nonlinear C06/C07 one-rail and twin-rail contact including tolerance, edge contact and first-contact mismatch is converged",
        "Received 6061-T651 material identity, MTR, orientation, machining effects and qualified allowables/factors are accepted",
        "Accepted inertia, approach/overspeed, motor-current decay, bumper force-stroke and event spectrum drive dynamic analysis",
        "Deflection, stopping travel, overtravel, rebound, fatigue and damage acceptance limits are qualified",
        "Guard, receiver and cable envelopes are regenerated for the 108 mm contact envelope and accepted",
        "Provider DFM, conventional drawings, datum/GD&T scheme and first-article plan are accepted",
        "Received C06/C07 geometry, material, fastener stacks, mass and unpowered fit/contact marks pass inspection",
        "Single-rail and twin-rail strain/force/angle proof and stopping tests correlate to accepted models",
        "Configuration-bound qualified release and separate work authority are signed",
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": f"R272-H{i:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED", "release_effect": "BLOCKS P0.11 SELECTION/FABRICATION/MOTION", "warning": WARNING} for i, hold in enumerate(holds, 1)])
    write_csv(OUT / "acceptance-matrix.csv", [{"acceptance_id": f"R272-ACC-{i:02d}", "criterion": hold, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING} for i, hold in enumerate(holds, 1)])
    print(json.dumps(status_parts, indent=2))
    print(f"Generated {ID}; P0.11 remains unselected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
