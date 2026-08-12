#!/usr/bin/env python3
"""Generate R278 exact-normal linear screens for the P0.13 J2 stop.

This corrects the prior C06/C07 load-direction simplifications and screens two
distinct C07 paths: pad absent / metal perimeter contact, and a distributed
pad-pocket-floor transfer.  It remains small-displacement, fixed-hole linear
elasticity; it is not nonlinear contact, a joined-bolt model, impact, fatigue,
an allowable, or a release analysis.
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
import generate_hr_v0_j2_stop_sideweb_fea_p01 as prior


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-pad-pocket-fea-p0.1"
IDENT = "HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1"
CAD_IDENT = "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
MESH_LEVELS = (4.0, 3.0, 2.0)
PROJECT_THRESHOLD_MPA = 240.0
INTERIM_GEOMETRY_RESERVE_TARGET = 4.0
POCKET_FLOOR_Y = 8.525 - 0.520


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def fixed_hole_nodes(mesh: MeshTet) -> np.ndarray:
    """Idealized restraints only in the original 9.525 mm C07/C06 land."""
    return prior.fixed_hole_nodes(mesh)


def areas(mesh: MeshTet, facets: np.ndarray) -> float:
    return prior.facets_area(mesh, facets)


def boundaries(mesh: MeshTet, case_id: str) -> tuple[np.ndarray, np.ndarray, float]:
    boundary = mesh.boundary_facets()
    centers = mesh.p[:, mesh.facets[:, boundary]].mean(axis=1)
    fixed = fixed_hole_nodes(mesh)
    if case_id == "C06_EXACT_NORMAL_TOP":
        selected = boundary[(np.abs(centers[2] - 36.026374) < 1e-5) & (centers[0] > 35.0)]
    elif case_id == "C07_METAL_PERIMETER_EXACT_NORMAL":
        selected = boundary[(np.abs(centers[1] - 8.525) < 1e-5) & (centers[0] > 34.0)]
    elif case_id == "C07_POCKET_FLOOR_EXACT_NORMAL":
        selected = boundary[(np.abs(centers[1] - POCKET_FLOOR_Y) < 1e-5) & (centers[0] > 34.0)]
    else:
        raise ValueError(case_id)
    if len(fixed) < 80 or len(selected) < 8:
        raise RuntimeError(f"boundary selection failed {case_id}: fixed={len(fixed)} loaded_facets={len(selected)}")
    return fixed, selected, areas(mesh, selected)


def solve_case(mesh: MeshTet, basis: Basis, stiffness, fixed: np.ndarray, loaded: np.ndarray,
               load_area: float, force_vector: np.ndarray, lam: float, mu: float) -> dict[str, object]:
    traction = force_vector / load_area

    @LinearForm
    def load(v, _w):
        return traction[0] * v[0] + traction[1] * v[1] + traction[2] * v[2]

    load_vector = asm(load, FacetBasis(mesh, ElementVector(ElementTetP1()), facets=loaded))
    displacement = solve(*condense(stiffness, load_vector, D=basis.nodal_dofs[:, fixed].ravel()))
    von_mises, _stress = base.element_stress(mesh, displacement, lam, mu)
    centroids = mesh.p[:, mesh.t].mean(axis=1).T
    root = (centroids[:, 0] > 20.0) & (centroids[:, 2] > -22.0) & (centroids[:, 2] < 22.0)
    root_values = von_mises[root]
    reaction = stiffness @ displacement - load_vector
    reaction_vector = reaction.reshape((-1, 3))[fixed].sum(axis=0)
    applied_vector = load_vector.reshape((-1, 3)).sum(axis=0)
    imbalance = reaction_vector + applied_vector
    maximum_index = int(np.argmax(von_mises))
    return {
        "applied_fx_n": float(applied_vector[0]), "applied_fy_n": float(applied_vector[1]), "applied_fz_n": float(applied_vector[2]),
        "reaction_fx_n": float(reaction_vector[0]), "reaction_fy_n": float(reaction_vector[1]), "reaction_fz_n": float(reaction_vector[2]),
        "normalized_force_balance_error": float(np.linalg.norm(imbalance) / np.linalg.norm(applied_vector)),
        "maximum_displacement_mm": float(np.max(np.linalg.norm(displacement.reshape((-1, 3)), axis=1))),
        "strain_energy_n_mm": float(0.5 * displacement @ stiffness @ displacement),
        "global_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(von_mises)),
        "global_p99_element_von_mises_mpa": float(np.quantile(von_mises, 0.99)),
        "root_maximum_element_von_mises_mpa_mesh_sensitive": float(np.max(root_values)),
        "root_p99_element_von_mises_mpa": float(np.quantile(root_values, 0.99)),
        "global_maximum_centroid_x_mm": float(centroids[maximum_index, 0]),
        "global_maximum_centroid_y_mm": float(centroids[maximum_index, 1]),
        "global_maximum_centroid_z_mm": float(centroids[maximum_index, 2]),
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    static = list(csv.DictReader((CAD / "corrected-static-stop-screen.csv").open(newline="", encoding="utf-8-sig")))[-1]
    force_n = float(static["single_rail_normal_force_n"])
    contact = json.loads((CAD / "cad-contact-normal-evidence.json").read_text(encoding="utf-8"))
    normal_world = np.asarray(contact["selected_conservative_solution"]["normal_fixed_to_moving"], dtype=float)
    q = math.radians(float(contact["sample_angle_deg"]))
    force_c07 = -force_n * normal_world
    normal_c06 = np.asarray((
        normal_world[0],
        math.cos(q) * normal_world[1] + math.sin(q) * normal_world[2],
        -math.sin(q) * normal_world[1] + math.cos(q) * normal_world[2],
    ))
    force_c06 = force_n * normal_c06
    if abs(np.linalg.norm(normal_c06) - 1.0) > 1e-9 or abs(normal_c06[1]) > 1e-8 or abs(normal_c06[2] + 1.0) > 1e-8:
        raise RuntimeError(f"unexpected exact C06-local normal {normal_c06}")

    cases = (
        ("C06_EXACT_NORMAL_TOP", "C06", "MV0-C06_J2_positive_moving_striker_adapter.step", force_c06,
         "exact fixed-to-moving CAD normal transformed by R_x(-q); one positive C06 rail top; pad mechanics excluded"),
        ("C07_METAL_PERIMETER_EXACT_NORMAL", "C07", "MV0-C07_J2_positive_fixed_catch_adapter.step", force_c07,
         "opposite exact CAD normal on one positive C07 surrounding metal face; pad absent / metal-backup case"),
        ("C07_POCKET_FLOOR_EXACT_NORMAL", "C07", "MV0-C07_J2_positive_fixed_catch_adapter.step", force_c07,
         "opposite exact CAD normal distributed on one positive pocket floor; pad constitutive/contact behavior excluded"),
    )
    lam, mu = lame_parameters(base.E_MPA, base.POISSON)
    result_rows: list[dict[str, object]] = []
    source_rows: list[dict[str, object]] = []
    for case_id, part_id, filename, force_vector, boundary_note in cases:
        base.STEP = CAD / "parts" / filename
        source_rows.append({
            "case_id":case_id,"part_id":part_id,"step_path":base.STEP.relative_to(ROOT).as_posix(),
            "force_source":"cad-contact-normal-evidence.json + corrected-static-stop-screen.csv",
            "force_vector_xyz_n":";".join(f"{value:.9f}" for value in force_vector),
            "boundary":boundary_note,"warning":WARNING,
        })
        for mesh_size in MESH_LEVELS:
            points, tets, meta = base.build_mesh(mesh_size)
            mesh = MeshTet(points.T, tets.T)
            basis = Basis(mesh, ElementVector(ElementTetP1()))
            stiffness = asm(linear_elasticity(lam, mu), basis)
            fixed, loaded, load_area = boundaries(mesh, case_id)
            result = solve_case(mesh, basis, stiffness, fixed, loaded, load_area, force_vector, lam, mu)
            maximum = float(result["global_maximum_element_von_mises_mpa_mesh_sensitive"])
            reserve = PROJECT_THRESHOLD_MPA / maximum
            result_rows.append({
                "case_id":case_id,"part_id":part_id,"mesh_size_mm":mesh_size,"nodes":meta["nodes"],"tetrahedra":meta["tetrahedra"],
                "minimum_minSICN":meta["minimum_minSICN"],"loaded_boundary_facets":len(loaded),"loaded_area_mm2":load_area,
                "single_rail_resultant_n":force_n,**result,
                "ratio_to_project_240_mpa_mtr_threshold_not_allowable":reserve,
                "interim_geometry_reserve_target":INTERIM_GEOMETRY_RESERVE_TARGET,
                "interim_rejection_result":"PASS INTERNAL GEOMETRY SCREEN" if reserve >= INTERIM_GEOMETRY_RESERVE_TARGET else "FAIL INTERNAL GEOMETRY SCREEN",
                "model_boundary":boundary_note + "; fixed hole cylinders; linear isotropic small-displacement model; no bolt/frame/contact/dynamic/fatigue/tolerance credit",
                "warning":WARNING,
            })
    write_csv(OUT / "mesh-convergence.csv", result_rows)
    write_csv(OUT / "load-boundary-register.csv", source_rows)

    summaries: dict[str, object] = {}
    for case_id, *_rest in cases:
        case_rows = [row for row in result_rows if row["case_id"] == case_id]
        finest, previous = case_rows[-1], case_rows[-2]
        summaries[case_id] = {
            "finest_mesh_mm":finest["mesh_size_mm"],"finest_loaded_area_mm2":finest["loaded_area_mm2"],
            "finest_global_maximum_mpa":finest["global_maximum_element_von_mises_mpa_mesh_sensitive"],
            "finest_global_p99_mpa":finest["global_p99_element_von_mises_mpa"],
            "finest_root_maximum_mpa":finest["root_maximum_element_von_mises_mpa_mesh_sensitive"],
            "finest_maximum_displacement_mm":finest["maximum_displacement_mm"],
            "ratio_to_project_threshold":finest["ratio_to_project_240_mpa_mtr_threshold_not_allowable"],
            "interim_rejection_result":finest["interim_rejection_result"],
            "final_two_mesh_global_maximum_relative_change":abs(float(finest["global_maximum_element_von_mises_mpa_mesh_sensitive"])-float(previous["global_maximum_element_von_mises_mpa_mesh_sensitive"]))/float(finest["global_maximum_element_von_mises_mpa_mesh_sensitive"]),
        }
    status = {
        "identifier":IDENT,"round":"R278","date":"2026-08-12","cad_identifier":CAD_IDENT,
        "supersedes_for_current_linear_calculation":"HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1",
        "correction":"C06 force transformed from exact CAD contact normal into moving-part coordinates; C07 uses the equal-and-opposite exact world/fixed-part normal; P0.13 metal-perimeter and pocket-floor paths are separate",
        "single_rail_force_n":force_n,"normal_fixed_to_moving_world":normal_world.tolist(),"force_on_c06_local_n":force_c06.tolist(),"force_on_c07_fixed_n":force_c07.tolist(),
        "cases":summaries,
        "solver":{"gmsh":base.gmsh.__version__,"scikit_fem":base.skfem.__version__,"scipy":base.scipy.__version__,"element":"first-order tetrahedron","analysis":"small-displacement isotropic linear elasticity"},
        "material_model":{"youngs_modulus_mpa":base.E_MPA,"poisson_ratio_assumption":base.POISSON,"project_mtr_threshold_mpa":PROJECT_THRESHOLD_MPA,"threshold_is_allowable":False,"interim_geometry_reserve_target":INTERIM_GEOMETRY_RESERVE_TARGET},
        "convergence_acceptance":"NOT ESTABLISHED; mesh-sensitive extrema and idealized restraints/load distribution preclude qualified convergence",
        "joined_fastener_model_complete":False,"nonlinear_contact_model_complete":False,"dynamic_model_complete":False,
        "selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")
    assumptions = [
        "Exact P0.13 STEP B-Reps represent nominal geometry only; no manufacturing tolerance or as-built deviation is included",
        "One rail carries the complete 253.607 N endpoint-plus-gravity resultant; twin sharing receives no credit",
        "C06 load direction is the exact CAD fixed-to-moving normal transformed into C06 local coordinates",
        "C07 load direction is the equal-and-opposite exact CAD normal in fixed/world coordinates",
        "Metal-perimeter and pocket-floor transfers are separate bounding screens; real pad/contact load sharing is not inferred",
        "Hole cylinders are perfectly fixed; fastener preload, slip, bearing, prying, S102/extrusion compliance and separation are excluded",
        "6061-T651 elastic constants are assumptions and 240 MPa is a project MTR threshold, not a released allowable",
        "The 4.0 reserve target is an internal geometry-rejection rule, not a safety factor or impact model",
    ]
    write_csv(OUT / "assumption-register.csv", [{"assumption_id":f"R278-A{i:02d}","assumption":text,"accepted":False,"closure":"qualified analysis/physical evidence required","warning":WARNING} for i,text in enumerate(assumptions,1)])
    holds_text = [
        "Qualified reviewer accepts the exact-normal coordinate transforms and sign conventions against the P0.13 assembly",
        "Mesh refinement/local stress convergence is demonstrated at the pocket edges, rail roots and restrained holes",
        "Nonlinear one-rail and two-rail C06/C07 contact includes edge contact, pad compression, metal backup, friction, tolerance and first-contact mismatch",
        "A04 and frame/extrusion joined-load model includes exact received hardware, preload, slip, bearing, prying, separation and flexibility",
        "Received 6061-T651 lot, MTR, orientation, machining effects, surface condition and qualified allowables/factors are accepted",
        "Accepted inertia, approach/fault speed, motor-current/torque decay, force-stroke and event spectrum drive an energy-based transient analysis",
        "Deflection, overtravel, rebound, fatigue, damage and stopping-time/angle acceptance limits are allocated and verified",
        "Pad-absent, one-pad, bottom-out and pad-migration fault cases correlate to guarded physical force/strain/angle/current tests",
        "P0.13 DFM, dependent pocket depth, inspection, mass/COM and guard/cable envelopes are accepted",
        "Configuration-bound qualified release and separate fabrication, assembly and powered-work authorities are signed",
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id":f"R278-H{i:02d}","hold":text,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS P0.13 SELECTION/FABRICATION/MOTION","warning":WARNING} for i,text in enumerate(holds_text,1)])
    write_csv(OUT / "acceptance-matrix.csv", [{"acceptance_id":f"R278-ACC-{i:02d}","criterion":text,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,text in enumerate(holds_text,1)])
    print(json.dumps(summaries, indent=2))
    print(f"Generated {IDENT}; P0.13 remains unselected and no work authority is released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
