#!/usr/bin/env python3
"""Development-only C06/C07 root-web refinement sweep for R272."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import cadquery as cq
import numpy as np
from skfem import Basis, ElementTetP1, ElementVector, MeshTet, asm
from skfem.models.elasticity import lame_parameters, linear_elasticity

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_j2_stop_fea_p01 as base
import generate_hr_v0_j2_stop_sideweb_fea_p01 as screen


OUT = Path(tempfile.gettempdir()) / "project-button-r272-mixedside-refinement"
EXTENSION = 25.4 - arm.PLATE_T


def plate(points: list[tuple[float, float]], y0: float, thickness: float, face: str) -> cq.Shape:
    shape = arm._profile_plate(points, y0, thickness)
    return cq.Workplane(obj=shape).faces(face).edges().fillet(2.0).val()


def symmetric(points_positive: list[tuple[float, float]], y0: float, thickness: float, face: str) -> list[cq.Shape]:
    result = []
    for sign in (1.0, -1.0):
        points = [(sign * x, z) for x, z in points_positive]
        if sign < 0:
            points.reverse()
        result.append(plate(points, y0, thickness, face))
    return result


def c06(root_inner: float) -> cq.Shape:
    prior = (arm.STOP_STRIKER_INNER_X_MM, arm.STOP_STRIKER_OUTER_X_MM)
    arm.STOP_STRIKER_INNER_X_MM, arm.STOP_STRIKER_OUTER_X_MM = 35.0, 53.0
    try:
        solid = arm.j2_positive_striker_adapter(0.0, screen.STRIKER_TOP_Z)
    finally:
        arm.STOP_STRIKER_INNER_X_MM, arm.STOP_STRIKER_OUTER_X_MM = prior
    points = [(root_inner, -20.0), (53.0, -20.0), (53.0, screen.STRIKER_TOP_Z), (35.0, screen.STRIKER_TOP_Z), (35.0, 20.0), (root_inner, 20.0)]
    for addition in symmetric(points, arm.PLATE_T, EXTENSION, "<Y"):
        solid = solid.fuse(addition)
    return solid


def c07(root_inner: float) -> cq.Shape:
    prior = (arm.STOP_CATCH_INNER_X_MM, arm.STOP_CATCH_OUTER_X_MM)
    arm.STOP_CATCH_INNER_X_MM, arm.STOP_CATCH_OUTER_X_MM = 34.0, 54.0
    try:
        solid = arm.j2_positive_catch_adapter(0.0)
    finally:
        arm.STOP_CATCH_INNER_X_MM, arm.STOP_CATCH_OUTER_X_MM = prior
    rear = [(root_inner, -20.0), (54.0, -20.0), (54.0, 22.0), (34.0, 22.0), (34.0, 17.0), (root_inner, 17.0)]
    for addition in symmetric(rear, -EXTENSION, EXTENSION, ">Y"):
        solid = solid.fuse(addition)
    if root_inner < 17.35:
        for x in (-16.0, 16.0):
            for z in (-8.0, 8.0):
                solid = solid.cut(cq.Solid.makeCylinder(1.35, 25.4, cq.Vector(x, -EXTENSION, z), cq.Vector(0, 1, 0)))
    return solid


def solve_part(part_id: str, root_inner: float) -> dict[str, object]:
    shape = c06(root_inner) if part_id == "C06" else c07(root_inner)
    step = OUT / f"{part_id.lower()}-root-{root_inner:g}.step"
    cq.exporters.export(shape, str(step))
    base.STEP = step
    base.TOP_Z = screen.STRIKER_TOP_Z
    points, tets, metadata = base.build_mesh(2.5)
    mesh = MeshTet(points.T, tets.T)
    basis = Basis(mesh, ElementVector(ElementTetP1()))
    lam, mu = lame_parameters(base.E_MPA, base.POISSON)
    stiffness = asm(linear_elasticity(lam, mu), basis)
    if part_id == "C06":
        fixed, pos, neg, area_pos, area_neg = screen.c06_boundary(mesh)
        result, _u, vm = base.solve_case(mesh, basis, stiffness, fixed, pos, neg, area_pos, area_neg, screen.FORCE_N, "single_positive", lam, mu, root_min_x_mm=16.0, root_z_min_mm=-22.0, root_z_max_mm=22.0)
    else:
        fixed, pos, _neg, area_pos, _area_neg = screen.c07_boundary(mesh)
        if root_inner < 17.35:
            p = mesh.p
            full_fixed: list[int] = []
            for x in (-16.0, 16.0):
                for z in (-8.0, 8.0):
                    radial = np.sqrt((p[0] - x) ** 2 + (p[2] - z) ** 2)
                    full_fixed.extend(np.where((np.abs(radial - 1.35) < 1e-4) & (p[1] >= -EXTENSION - 1e-5) & (p[1] <= 9.52501))[0])
            for z in (-10.0, 10.0):
                radial = np.sqrt(p[0] ** 2 + (p[2] - z) ** 2)
                full_fixed.extend(np.where((np.abs(radial - 2.75) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
            fixed = np.asarray(sorted(set(full_fixed)), dtype=np.int64)
        result, vm = screen.solve_c07(mesh, basis, stiffness, fixed, pos, area_pos, lam, mu)
    centroids = mesh.p[:, mesh.t].mean(axis=1).T
    index = int(np.argmax(vm))
    return {
        "part_id": part_id,
        "root_inner_x_mm": root_inner,
        "nodes": metadata["nodes"],
        "tetrahedra": metadata["tetrahedra"],
        "global_max_mpa": result["global_maximum_element_von_mises_mpa_mesh_sensitive"],
        "global_max_centroid_mm": [float(value) for value in centroids[index]],
        "global_p99_mpa": result["global_p99_element_von_mises_mpa"],
        "maximum_displacement_mm": result["maximum_displacement_mm"],
        "four_x_global_max_mpa": 4.0 * float(result["global_maximum_element_von_mises_mpa_mesh_sensitive"]),
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    rows = [solve_part("C06", 20.0), solve_part("C07", 14.0), solve_part("C07", 12.0), solve_part("C07", 10.0)]
    (OUT / "results.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
