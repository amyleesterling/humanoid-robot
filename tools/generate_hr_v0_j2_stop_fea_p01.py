#!/usr/bin/env python3
"""Generate the R271 linear-elastic C06 full-part FEA screening package.

The model is intentionally narrow: exact P0.10 C06 geometry, bonded/fixed hole
surfaces, and distributed resultants on the flat rail-top faces.  It is useful
for rejecting weak geometry and exposing full-part load paths.  It is not a
nonlinear contact model, a bolt-joint model, an allowable, or a release.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path

import gmsh
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "project-button-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meshio
import numpy as np
import scipy
import skfem
from skfem import Basis, ElementTetP1, ElementVector, FacetBasis, LinearForm, MeshTet, asm, condense, solve
from skfem.models.elasticity import lame_parameters, linear_elasticity

ROOT = Path(__file__).resolve().parents[1]
STEP = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/parts/MV0-C06_J2_positive_moving_striker_adapter.step"
CONTACT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/cad-contact-normal-evidence.json"
STATIC = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop/corrected-static-stop-screen.csv"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-fea-p0.1"
ID = "HR-V0-J2-STOP-FEA-P0.1"
CAD_ID = "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE"
ROUND = "R271"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
matplotlib.rcParams["svg.hashsalt"] = "project-button-r271"

# Units: N, mm, MPa.  Kaiser values are typical, not minimum allowables.
E_MPA = 68_300.0
POISSON = 0.33  # explicit modeling assumption; configuration-bound value remains SELECTION REQUIRED
PROJECT_MTR_THRESHOLD_MPA = 240.0
TOP_Z = 37.380699
J2_ANGLE_DEG = 117.9999
MESH_LEVELS_MM = (4.0, 3.0, 2.0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonicalize_svg(path: Path) -> None:
    """Remove generator whitespace and retain stable SVG bytes."""
    text = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def build_mesh(size_mm: float) -> tuple[np.ndarray, np.ndarray, dict[str, float | int | str]]:
    gmsh.initialize(["-nopopup"])
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads1D", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads2D", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)
        gmsh.option.setNumber("Mesh.MeshSizeMin", size_mm)
        gmsh.option.setNumber("Mesh.MeshSizeMax", size_mm)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.RandomFactor", 1e-12)
        gmsh.model.add(f"C06_{size_mm:g}mm")
        imported = gmsh.model.occ.importShapes(str(STEP))
        gmsh.model.occ.synchronize()
        if len(imported) != 1 or imported[0][0] != 3:
            raise RuntimeError(f"expected one STEP volume, got {imported}")
        gmsh.model.mesh.generate(3)
        node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
        points = np.asarray(coordinates, dtype=float).reshape((-1, 3))
        tag_to_index = {int(tag): index for index, tag in enumerate(node_tags)}
        element_types, element_tags, element_nodes = gmsh.model.mesh.getElements(3)
        tetra_tags: np.ndarray | None = None
        tetra_nodes: np.ndarray | None = None
        for element_type, tags, nodes in zip(element_types, element_tags, element_nodes):
            name, dimension, order, count, _, _ = gmsh.model.mesh.getElementProperties(element_type)
            if dimension == 3 and order == 1 and count == 4 and "tetra" in name.lower():
                tetra_tags = np.asarray(tags, dtype=np.int64)
                raw = np.asarray(nodes, dtype=np.int64).reshape((-1, 4))
                tetra_nodes = np.vectorize(tag_to_index.__getitem__, otypes=[np.int64])(raw)
                break
        if tetra_tags is None or tetra_nodes is None:
            raise RuntimeError("first-order tetrahedral volume elements were not generated")
        quality = np.asarray(gmsh.model.mesh.getElementQualities(tetra_tags.tolist(), "minSICN"), dtype=float)
        metadata: dict[str, float | int | str] = {
            "mesh_size_mm": size_mm,
            "nodes": len(points),
            "tetrahedra": len(tetra_nodes),
            "minimum_minSICN": float(np.min(quality)),
            "mean_minSICN": float(np.mean(quality)),
            "gmsh_version": gmsh.__version__,
        }
        return points, tetra_nodes, metadata
    finally:
        gmsh.finalize()


def boundary_sets(mesh: MeshTet) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    p = mesh.p
    boundary = mesh.boundary_facets()
    facet_nodes = mesh.facets[:, boundary]
    centers = p[:, facet_nodes].mean(axis=1)
    positive = boundary[
        (np.abs(centers[2] - TOP_Z) < 1e-5)
        & (centers[0] > 35.0)
        & (centers[1] > -6.351)
        & (centers[1] < 9.526)
    ]
    negative = boundary[
        (np.abs(centers[2] - TOP_Z) < 1e-5)
        & (centers[0] < -35.0)
        & (centers[1] > -6.351)
        & (centers[1] < 9.526)
    ]

    fixed_nodes: list[int] = []
    for x in (-16.0, 16.0):
        for z in (-8.0, 8.0):
            radial = np.sqrt((p[0] - x) ** 2 + (p[2] - z) ** 2)
            fixed_nodes.extend(np.where((np.abs(radial - 1.35) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    for z in (-10.0, 10.0):
        radial = np.sqrt(p[0] ** 2 + (p[2] - z) ** 2)
        fixed_nodes.extend(np.where((np.abs(radial - 2.75) < 1e-4) & (p[1] >= -1e-5) & (p[1] <= 9.52501))[0])
    fixed = np.asarray(sorted(set(fixed_nodes)), dtype=np.int64)
    if len(fixed) < 80 or len(positive) < 8 or len(negative) < 8:
        raise RuntimeError(f"inadequate boundary discretization: fixed={len(fixed)}, positive={len(positive)}, negative={len(negative)}")

    def area(facets: np.ndarray) -> float:
        triangles = mesh.facets[:, facets]
        total = 0.0
        for triangle in triangles.T:
            a, b, c = p[:, triangle].T
            total += np.linalg.norm(np.cross(b - a, c - a)) / 2.0
        return float(total)

    return fixed, positive, negative, area(positive), area(negative)


def element_stress(mesh: MeshTet, displacement: np.ndarray, lam: float, mu: float) -> tuple[np.ndarray, np.ndarray]:
    tets = mesh.t.T
    xyz = mesh.p.T[tets]
    matrices = np.concatenate((np.ones((len(tets), 4, 1)), xyz), axis=2)
    inverse = np.linalg.inv(matrices)
    gradients = inverse[:, 1:, :].transpose(0, 2, 1)
    nodal_u = displacement.reshape((-1, 3))[tets]
    grad_u = np.einsum("eic,eij->ecj", nodal_u, gradients)
    strain = 0.5 * (grad_u + grad_u.transpose(0, 2, 1))
    traces = np.trace(strain, axis1=1, axis2=2)
    stress = 2.0 * mu * strain + lam * traces[:, None, None] * np.eye(3)[None, :, :]
    sx, sy, sz = stress[:, 0, 0], stress[:, 1, 1], stress[:, 2, 2]
    txy, tyz, tzx = stress[:, 0, 1], stress[:, 1, 2], stress[:, 2, 0]
    von_mises = np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3.0 * (txy**2 + tyz**2 + tzx**2))
    return von_mises, stress


def solve_case(
    mesh: MeshTet,
    basis: Basis,
    stiffness,
    fixed_nodes: np.ndarray,
    positive_facets: np.ndarray,
    negative_facets: np.ndarray,
    positive_area: float,
    negative_area: float,
    total_force_n: float,
    share: str,
    lam: float,
    mu: float,
) -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    # Fixed catch face normal is +Y in the assembled frame.  Transforming the
    # force direction into C06 local coordinates at the sampled J2 angle gives
    # (0, cos(q), -sin(q)).
    direction = np.asarray((0.0, math.cos(math.radians(J2_ANGLE_DEG)), -math.sin(math.radians(J2_ANGLE_DEG))))

    def facet_load(facets: np.ndarray, area: float, force_vector: np.ndarray) -> np.ndarray:
        traction = force_vector / area

        @LinearForm
        def load(v, _w):
            return traction[0] * v[0] + traction[1] * v[1] + traction[2] * v[2]

        return asm(load, FacetBasis(mesh, ElementVector(ElementTetP1()), facets=facets))

    if share == "single_positive":
        applied = direction * total_force_n
        load_vector = facet_load(positive_facets, positive_area, applied)
    elif share == "equal_twin":
        applied = direction * total_force_n
        load_vector = facet_load(positive_facets, positive_area, applied / 2.0) + facet_load(negative_facets, negative_area, applied / 2.0)
    else:
        raise ValueError(share)

    fixed_dofs = basis.nodal_dofs[:, fixed_nodes].ravel()
    displacement = solve(*condense(stiffness, load_vector, D=fixed_dofs))
    von_mises, _ = element_stress(mesh, displacement, lam, mu)
    centroids = mesh.p[:, mesh.t].mean(axis=1).T
    root = (centroids[:, 0] > 32.0) & (centroids[:, 2] > -12.0) & (centroids[:, 2] < 2.0)
    if not np.any(root):
        raise RuntimeError("positive rail-root ROI is empty")
    reaction = stiffness @ displacement - load_vector
    reaction_vector = reaction.reshape((-1, 3))[fixed_nodes].sum(axis=0)
    applied_vector = load_vector.reshape((-1, 3)).sum(axis=0)
    imbalance = reaction_vector + applied_vector
    nodal_magnitude = np.linalg.norm(displacement.reshape((-1, 3)), axis=1)
    root_values = von_mises[root]
    result: dict[str, object] = {
        "share_case": share,
        "total_normal_force_n": total_force_n,
        "applied_fx_n": applied_vector[0],
        "applied_fy_n": applied_vector[1],
        "applied_fz_n": applied_vector[2],
        "reaction_fx_n": reaction_vector[0],
        "reaction_fy_n": reaction_vector[1],
        "reaction_fz_n": reaction_vector[2],
        "normalized_force_balance_error": float(np.linalg.norm(imbalance) / np.linalg.norm(applied_vector)),
        "maximum_displacement_mm": float(np.max(nodal_magnitude)),
        "strain_energy_n_mm": float(0.5 * displacement @ stiffness @ displacement),
        "global_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(von_mises)),
        "global_p99_element_von_mises_mpa": float(np.quantile(von_mises, 0.99)),
        "positive_root_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(root_values)),
        "positive_root_p99_element_von_mises_mpa": float(np.quantile(root_values, 0.99)),
        "positive_root_p95_element_von_mises_mpa": float(np.quantile(root_values, 0.95)),
        "positive_root_elements": int(np.sum(root)),
    }
    return result, displacement, von_mises


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    endpoint = read_csv(STATIC)[-1]
    endpoint_force = float(endpoint["single_rail_normal_force_n"])
    raw_force = float(read_csv(STATIC)[0]["single_rail_normal_force_n"])
    contact = json.loads(CONTACT.read_text(encoding="utf-8"))
    lam, mu = lame_parameters(E_MPA, POISSON)

    convergence_rows: list[dict[str, object]] = []
    case_rows: list[dict[str, object]] = []
    finest_data: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None
    mesh_hash_rows: list[dict[str, object]] = []

    for mesh_size in MESH_LEVELS_MM:
        points, tets, mesh_meta = build_mesh(mesh_size)
        mesh = MeshTet(points.T, tets.T)
        fixed, positive, negative, positive_area, negative_area = boundary_sets(mesh)
        element = ElementVector(ElementTetP1())
        basis = Basis(mesh, element)
        stiffness = asm(linear_elasticity(lam, mu), basis)

        endpoint_result, endpoint_u, endpoint_vm = solve_case(
            mesh, basis, stiffness, fixed, positive, negative, positive_area, negative_area,
            endpoint_force, "single_positive", lam, mu,
        )
        endpoint_result.update(mesh_meta)
        endpoint_result.update({"case_id": "STATIC-PUBLISHED-ENDPOINT-SINGLE", "fixed_surface_nodes": len(fixed), "positive_flat_load_area_mm2": positive_area, "negative_flat_load_area_mm2": negative_area})
        convergence_rows.append({**endpoint_result, "warning": WARNING})

        if mesh_size == min(MESH_LEVELS_MM):
            for case_id, force, share in (
                ("STATIC-RAW800-SINGLE", raw_force, "single_positive"),
                ("STATIC-PUBLISHED-ENDPOINT-SINGLE", endpoint_force, "single_positive"),
                ("STATIC-PUBLISHED-ENDPOINT-EQUAL-TWIN", endpoint_force, "equal_twin"),
            ):
                result, displacement, von_mises = solve_case(
                    mesh, basis, stiffness, fixed, positive, negative, positive_area, negative_area,
                    force, share, lam, mu,
                )
                result.update(mesh_meta)
                result.update({"case_id": case_id, "yield_ratio_to_project_240_mpa_using_root_max": PROJECT_MTR_THRESHOLD_MPA / float(result["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"]), "status": "LINEAR SCREEN ONLY - CONTACT/JOINED LOAD PATH/ALLOWABLE/PHYSICAL PROOF OPEN", "warning": WARNING})
                case_rows.append(result)
                if case_id == "STATIC-PUBLISHED-ENDPOINT-SINGLE":
                    finest_data = (points, tets, displacement, von_mises)

        # Store a deterministic compressed node/connectivity capsule for audit;
        # full meshes are reproducible from the exact STEP and generator.
        capsule = OUT / f"c06-mesh-{mesh_size:g}mm.npz"
        np.savez_compressed(capsule, points_mm=points, tetrahedra=tets)
        mesh_hash_rows.append({**mesh_meta, "capsule": capsule.name, "sha256": sha(capsule), "bytes": capsule.stat().st_size, "warning": WARNING})

    if finest_data is None:
        raise RuntimeError("finest result was not captured")
    points, tets, displacement, von_mises = finest_data
    meshio.write(
        OUT / "c06-single-endpoint-finest.vtu",
        meshio.Mesh(points=points, cells=[("tetra", tets)], point_data={"displacement_mm": displacement.reshape((-1, 3))}, cell_data={"von_mises_mpa": [von_mises]}),
        binary=True,
    )

    for row in convergence_rows:
        row["four_x_linear_scaled_root_max_mpa_not_impact_model"] = 4.0 * float(row["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"])
        row["four_x_rejection_result"] = "FAIL INTERIM REJECTION SCREEN" if float(row["four_x_linear_scaled_root_max_mpa_not_impact_model"]) > PROJECT_MTR_THRESHOLD_MPA else "PASS INTERIM REJECTION SCREEN"
        row["model_boundary"] = "fixed hole surfaces; distributed flat rail-top resultant; local contact/bolt slip-preload/prying/nonlinearity excluded"
    write_csv(OUT / "mesh-convergence.csv", convergence_rows)
    write_csv(OUT / "finest-mesh-load-cases.csv", case_rows)
    write_csv(OUT / "mesh-artifact-register.csv", mesh_hash_rows)

    finest_root = float(convergence_rows[-1]["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"])
    previous_root = float(convergence_rows[-2]["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"])
    convergence_delta = abs(finest_root - previous_root) / finest_root
    mesh_convergence = {
        "identifier": ID,
        "round": ROUND,
        "cad_identifier": CAD_ID,
        "exact_step_sha256": sha(STEP),
        "contact_evidence_sha256": sha(CONTACT),
        "solver": {"gmsh": gmsh.__version__, "scikit_fem": skfem.__version__, "scipy": scipy.__version__, "element": "first-order tetrahedron", "analysis": "small-displacement isotropic linear elasticity"},
        "material_model": {"family": "6061-T651 candidate", "youngs_modulus_mpa": E_MPA, "poisson_ratio_assumption": POISSON, "project_mtr_threshold_mpa": PROJECT_MTR_THRESHOLD_MPA, "allowable_released": False},
        "boundary_condition": "all displacement components fixed on four M2.5 and two M5 cylindrical through-hole surfaces; no bolt contact, preload, clearance, slip, prying or frame compliance",
        "load_condition": "CAD-derived fixed-catch +Y normal transformed into C06 local frame; resultant distributed over one flat positive rail-top face; local edge contact stress receives no credit",
        "contact_sample": contact["selected_conservative_solution"],
        "mesh_levels_mm": list(MESH_LEVELS_MM),
        "final_two_mesh_root_maximum_relative_change": convergence_delta,
        "convergence_acceptance": "NOT ESTABLISHED; mesh-sensitive maxima and singular boundary/contact idealizations preclude qualified convergence",
        "disposition": "P0.10 beam screen is non-conservative for the modeled full-part load path; P0.10 remains unselected",
        "selected": False,
        "fabrication_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(mesh_convergence, indent=2) + "\n", encoding="utf-8")

    assumptions = [
        {"assumption_id": "FEA-A01", "assumption": "isotropic linear elastic 6061-T651 with E=68.3 GPa and nu=0.33", "evidence": "E from Kaiser 6061 sheet/plate Rev 05/06; nu is an explicit unverified model assumption", "closure": "received lot MTR and qualified material-model disposition", "warning": WARNING},
        {"assumption_id": "FEA-A02", "assumption": "all six cylindrical hole surfaces fully fixed", "evidence": "exact CAD hole surfaces; no assembled joint model", "closure": "bolt/frame/contact/preload/slip/prying model calibrated by physical joint test", "warning": WARNING},
        {"assumption_id": "FEA-A03", "assumption": "normal resultant distributed over flat rail-top face", "evidence": "preserves force and direction but regularizes edge contact", "closure": "nonlinear C06/C07 contact model with tolerances and measured contact marks", "warning": WARNING},
        {"assumption_id": "FEA-A04", "assumption": "quasistatic endpoint force; no kinetic, motor-work, rebound or fatigue", "evidence": "R270 corrected static case only", "closure": "accepted inertia/speed/current-decay/force-stroke and event spectrum", "warning": WARNING},
        {"assumption_id": "FEA-A05", "assumption": "240 MPa project MTR threshold used only as rejection comparator", "evidence": "no received MTR and no qualified allowable", "closure": "received MTR, orientation/process effects and qualified factor/allowable", "warning": WARNING},
    ]
    write_csv(OUT / "model-assumptions-and-closure.csv", assumptions)

    sources = [
        {"source_id": "R271-SRC-01", "organization": "Kaiser Aluminum", "document": "Sheet Coil & Plate Alloy 6061 Technical Data", "revision_or_date": "Rev. 05/06; accessed 2026-08-12", "url": "https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1015/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf", "use": "typical E=68.3 GPa and typical T6/T651 yield=276 MPa", "boundary": "typical values only; not received-lot minimums or allowables", "warning": WARNING},
        {"source_id": "R271-SRC-02", "organization": "Gmsh", "document": "Gmsh 4.15.2 reference manual", "revision_or_date": "4.15.2; accessed 2026-08-12", "url": "https://gmsh.info/doc/texinfo/", "use": "OpenCASCADE STEP import and 3D tetrahedral mesh generation", "boundary": "mesh generator, not structural validation", "warning": WARNING},
        {"source_id": "R271-SRC-03", "organization": "scikit-fem", "document": "Documentation and Example 11: 3D linear elasticity", "revision_or_date": "12.0.2; accessed 2026-08-12", "url": "https://scikit-fem.readthedocs.io/en/latest/index.html", "use": "sparse finite-element assembly and linear-elastic formulation", "boundary": "project boundary conditions/postprocessing remain project responsibility", "warning": WARNING},
    ]
    write_csv(OUT / "source-register.csv", sources)

    # Convergence plot.
    sizes = np.asarray([float(row["mesh_size_mm"]) for row in convergence_rows])
    root_max = np.asarray([float(row["positive_root_maximum_element_von_mises_mpa_mesh_sensitive"]) for row in convergence_rows])
    root_p99 = np.asarray([float(row["positive_root_p99_element_von_mises_mpa"]) for row in convergence_rows])
    plt.figure(figsize=(9, 5.5))
    plt.plot(sizes, root_max, "o-", linewidth=2.5, label="Root maximum (mesh-sensitive)")
    plt.plot(sizes, root_p99, "s-", linewidth=2.5, label="Root 99th percentile")
    plt.axhline(PROJECT_MTR_THRESHOLD_MPA, color="#9b1c31", linestyle="--", linewidth=2, label="240 MPa project MTR threshold")
    plt.gca().invert_xaxis()
    plt.xlabel("Nominal mesh size (mm)", fontsize=14)
    plt.ylabel("Element von Mises stress (MPa)", fontsize=14)
    plt.title("C06 single-rail endpoint: mesh sensitivity", fontsize=17)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    plt.xticks(fontsize=12); plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(OUT / "mesh-convergence.svg", metadata={"Date": "2026-08-12"})
    plt.savefig(OUT / "mesh-convergence.png", dpi=180)
    plt.close()
    canonicalize_svg(OUT / "mesh-convergence.svg")

    # Mid-thickness stress view.  This is a centroid map, not a smoothed stress contour.
    centroids = points[tets].mean(axis=1)
    slice_mask = np.abs(centroids[:, 1] - 1.5) < 0.75
    plt.figure(figsize=(10, 6.5))
    scatter = plt.scatter(centroids[slice_mask, 0], centroids[slice_mask, 2], c=von_mises[slice_mask], s=10, cmap="viridis", vmin=0, vmax=min(240.0, float(np.quantile(von_mises, 0.995))))
    colorbar = plt.colorbar(scatter)
    colorbar.set_label("Element von Mises stress (MPa)", fontsize=13)
    plt.xlabel("C06 local X (mm)", fontsize=14)
    plt.ylabel("C06 local Z (mm)", fontsize=14)
    plt.title("C06 single-rail endpoint — centroid stress slice (2 mm mesh)", fontsize=17)
    plt.grid(True, alpha=0.2)
    plt.xticks(fontsize=12); plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(OUT / "c06-stress-slice.svg", metadata={"Date": "2026-08-12"})
    plt.savefig(OUT / "c06-stress-slice.png", dpi=180)
    plt.close()
    canonicalize_svg(OUT / "c06-stress-slice.svg")

    holds = [
        "Qualified reviewer accepts modeling scope, boundary conditions and singularity treatment",
        "Nonlinear C06/C07 one-rail/twin-rail contact including tolerances is converged",
        "Bolt/frame/extrusion contact, preload, clearance, slip and prying are modeled and physically calibrated",
        "Material lot, orientation, machining effects and qualified allowables/factors are accepted",
        "Accepted inertia, speed, current-decay, bumper force-stroke and event-spectrum inputs drive dynamic analysis",
        "Deflection, overtravel, rebound, fatigue and damage acceptance limits are qualified",
        "Provider DFM, drawings, FAI and received geometry/material evidence are accepted",
        "Single-rail and twin-rail strain/force/angle proof tests correlate to the model",
        "Configuration-bound qualified release and separate work authority are signed",
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": f"R271-H{i:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED", "release_effect": "BLOCKS P0.10 SELECTION/FABRICATION/MOTION", "warning": WARNING} for i, hold in enumerate(holds, 1)])
    write_csv(OUT / "acceptance-matrix.csv", [{"acceptance_id": f"R271-ACC-{i:02d}", "criterion": hold, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING} for i, hold in enumerate(holds, 1)])
    print(f"Generated {ID}: finest root max {finest_root:.3f} MPa; P0.10 remains unselected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
