#!/usr/bin/env python3
"""Development-only geometry sweep for an R272 J2-stop successor.

The output is written to the operating-system temporary directory.  This is
not release evidence and does not select a part or authorize physical work.
"""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path

import cadquery as cq
import numpy as np
from skfem import Basis, ElementTetP1, ElementVector, MeshTet, asm
from skfem.models.elasticity import lame_parameters, linear_elasticity

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_j2_stop_fea_p01 as fea


OUT = Path(tempfile.gettempdir()) / "project-button-r272-stop-sweep"
FORCE_N = 582.622


def boss_profile(stock_t: float, outer: float, thin_stock_t: float, step_blend_r: float) -> cq.Shape:
    """Symmetric contact-side webs; the actuator-side envelope is unchanged."""
    shapes: list[cq.Shape] = []
    extension = stock_t - arm.PLATE_T
    for sign in (-1.0, 1.0):
        points = [
            (sign * 22.0, -20.0),
            (sign * outer, -20.0),
            (sign * outer, arm.STOP_STRIKER_TOP_Z_MM),
            (sign * 35.0, arm.STOP_STRIKER_TOP_Z_MM),
            (sign * 35.0, 20.0),
            (sign * 22.0, 20.0),
        ]
        if sign < 0:
            points.reverse()
        full = arm._profile_plate(points, arm.PLATE_T, extension)
        if step_blend_r > 0.0:
            full = cq.Workplane(obj=full).faces("<Y").edges().fillet(step_blend_r).val()
        shapes.append(full)
    return cq.Compound.makeCompound(shapes)


def candidate(stock_t: float, outer: float, thin_stock_t: float, step_blend_r: float) -> tuple[cq.Shape, int]:
    prior_outer = arm.STOP_STRIKER_OUTER_X_MM
    arm.STOP_STRIKER_OUTER_X_MM = outer
    try:
        front = arm.j2_positive_striker_adapter(0.0)
    finally:
        arm.STOP_STRIKER_OUTER_X_MM = prior_outer
    fused = front
    for addition in boss_profile(stock_t, outer, thin_stock_t, step_blend_r).Solids():
        fused = fused.fuse(addition)
    solids = fused.Solids()
    if len(solids) != 1:
        raise RuntimeError(f"expected one fused solid, got {len(solids)}")
    solid = solids[0]
    return solid, 2


def solve_variant(name: str, stock_t: float, outer: float, thin_stock_t: float, step_blend_r: float) -> dict[str, object]:
    step = OUT / f"{name}.step"
    solid, blended_edges = candidate(stock_t, outer, thin_stock_t, step_blend_r)
    cq.exporters.export(solid, str(step))
    fea.STEP = step
    points, tets, meta = fea.build_mesh(2.5)
    mesh = MeshTet(points.T, tets.T)
    p = mesh.p
    boundary = mesh.boundary_facets()
    centers = p[:, mesh.facets[:, boundary]].mean(axis=1)
    positive = boundary[(np.abs(centers[2] - fea.TOP_Z) < 1e-5) & (centers[0] > 35.0)]
    negative = boundary[(np.abs(centers[2] - fea.TOP_Z) < 1e-5) & (centers[0] < -35.0)]
    fixed = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            radial = np.sqrt((p[0] - x) ** 2 + (p[2] - z) ** 2)
            fixed.extend(np.where((np.abs(radial - 1.35) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    for z in (-10.0, 10.0):
        radial = np.sqrt(p[0] ** 2 + (p[2] - z) ** 2)
        fixed.extend(np.where((np.abs(radial - 2.75) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    fixed = np.asarray(sorted(set(fixed)), dtype=np.int64)
    def area(facets):
        total = 0.0
        for triangle in mesh.facets[:, facets].T:
            a, b, c = p[:, triangle].T
            total += np.linalg.norm(np.cross(b-a,c-a))/2.0
        return total
    positive_area, negative_area = area(positive), area(negative)
    lam, mu = lame_parameters(fea.E_MPA, fea.POISSON)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    stiffness = asm(linear_elasticity(lam, mu), basis)
    result, displacement, von_mises = fea.solve_case(
        mesh,
        basis,
        stiffness,
        fixed,
        positive,
        negative,
        positive_area,
        negative_area,
        FORCE_N,
        "single_positive",
        lam,
        mu,
        root_min_x_mm=20.0,
        root_z_min_mm=-22.0,
        root_z_max_mm=22.0,
    )
    centroids = mesh.p[:, mesh.t].mean(axis=1).T
    max_index = int(np.argmax(von_mises))
    root_transition = (
        (centroids[:, 0] > 20.0)
        & (centroids[:, 0] < 38.0)
        & (centroids[:, 2] > -22.0)
        & (centroids[:, 2] < 22.0)
    )
    return {
        "variant": name,
        "stock_t_mm": stock_t,
        "outer_x_mm": outer,
        "rail_width_mm": outer - 35.0,
        "inner_web_total_thickness_mm": thin_stock_t,
        "step_blend_radius_mm": step_blend_r,
        "step_blended_edges": blended_edges,
        "nodes": meta["nodes"],
        "tetrahedra": meta["tetrahedra"],
        "load_area_mm2": positive_area,
        "root_transition_max_mpa": float(np.max(von_mises[root_transition])),
        "root_roi_max_mpa": result["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"],
        "global_max_mpa": result["global_maximum_element_von_mises_mpa_mesh_sensitive"],
        "global_max_centroid_mm": [float(value) for value in centroids[max_index]],
        "global_p99_mpa": float(np.quantile(von_mises, 0.99)),
        "maximum_displacement_mm": result["maximum_displacement_mm"],
        "four_x_root_transition_mpa": 4.0 * float(np.max(von_mises[root_transition])),
        "step": str(step),
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    variants = (
        ("v23-25p4-18w-contactside-r2", 25.4, 53.0, 9.525, 2.0),
    )
    rows = [solve_variant(*variant) for variant in variants]
    with (OUT / "results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "results.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
