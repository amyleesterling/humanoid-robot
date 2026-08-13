#!/usr/bin/env python3
"""Prototype the fail-closed R279 local-refinement/P2 execution protocol.

This is scratch numerical evidence for the *idealized* R278 fixed-hole model.
It cannot select P0.13, establish an allowable, validate a joint/contact model,
or authorize any physical work.  Exact OpenCASCADE entities are discovered
from the SHA-bound P0.13 STEP B-Reps and drive Gmsh local-size fields.  The
structural solve uses a quadratic displacement field on the corner-node
tetrahedral geometry because scikit-fem does not import Gmsh's curved
high-order geometry directly; that limitation is recorded in every output.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import math
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import gmsh
import numpy as np
from scipy.spatial import cKDTree
from skfem import Basis, ElementTetP1, ElementTetP2, ElementVector, FacetBasis, LinearForm, MeshTet, asm, condense, solve
from skfem.models.elasticity import lame_parameters, linear_elasticity


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-stop-refinement-execution-p0.1"
IDENT = "HR-V0-J2-STOP-REFINEMENT-EXECUTION-P0.1"
WARNING = "PRELIMINARY - SCRATCH NUMERICAL EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
E_MPA = 68_300.0
POISSON = 0.33
POCKET_FLOOR_Y = 8.525 - 0.520
FORCE_N = 253.607


@dataclass(frozen=True)
class Level:
    name: str
    global_h: float
    rail_h: float
    pocket_h: float
    hole_h: float


LEVELS = {
    "P2C": Level("P2C", 4.0, 1.00, 0.52, 0.80),
    "L0": Level("L0", 2.0, 0.50, 0.26, 0.40),
    "L1": Level("L1", 1.4, 0.35, 0.18, 0.28),
    "L2": Level("L2", 1.0, 0.25, 0.13, 0.20),
    "L3": Level("L3", 0.7, 0.18, 0.09, 0.14),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        fieldnames: list[str] = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rss_mb() -> float:
    """Return Windows working-set memory without adding a dependency."""
    class PMC(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
        ]
    counters = PMC()
    counters.cb = ctypes.sizeof(counters)
    try:
        ctypes.windll.psapi.GetProcessMemoryInfo(  # type: ignore[attr-defined]
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
        )
        return counters.WorkingSetSize / 1024.0**2
    except Exception:
        return float("nan")


def bbox(dim: int, tag: int) -> tuple[float, ...]:
    return tuple(float(value) for value in gmsh.model.getBoundingBox(dim, tag))


def near(value: float, target: float, tol: float = 2e-3) -> bool:
    return abs(value - target) <= tol


def entity_register(part: str) -> tuple[list[dict[str, object]], dict[str, list[int]]]:
    """Select exact CAD entities; fail rather than silently use a box substitute."""
    rows: list[dict[str, object]] = []
    groups: dict[str, list[int]] = {"load": [], "holes": [], "rail_root": [], "pocket_edge": [], "pocket_floor": [], "metal_face": []}
    for dim in (1, 2):
        for _, tag in gmsh.model.getEntities(dim):
            b = bbox(dim, tag)
            kind = gmsh.model.getType(dim, tag)
            rows.append({"part": part, "dimension": dim, "tag": tag, "type": kind,
                         "xmin": b[0], "ymin": b[1], "zmin": b[2], "xmax": b[3], "ymax": b[4], "zmax": b[5]})
            if dim == 2:
                # Exact cylindrical surfaces of the six original mounting holes.
                if kind == "Cylinder" and b[1] >= -2e-3 and b[4] <= 9.527:
                    cx, cz = (b[0] + b[3]) / 2.0, (b[2] + b[5]) / 2.0
                    candidates = [(-16, -8, 1.35), (-16, 8, 1.35), (16, -8, 1.35), (16, 8, 1.35), (0, -10, 2.75), (0, 10, 2.75)]
                    if any(abs(cx-x) < 2e-3 and abs(cz-z) < 2e-3 and abs((b[3]-b[0])/2-r) < 2e-3 for x,z,r in candidates):
                        groups["holes"].append(tag)
                if part == "C06" and near(b[2], 36.026374) and near(b[5], 36.026374) and b[0] >= 34.998:
                    groups["load"].append(tag)
                if part == "C07" and near(b[1], POCKET_FLOOR_Y) and near(b[4], POCKET_FLOOR_Y) and b[0] >= 37.79 and b[3] <= 50.21:
                    groups["pocket_floor"].append(tag)
                # The planar metal-backup entity may span both rails; retain
                # the exact face tag here and clip its mesh facets to +X in
                # solve_case rather than pretending it is two CAD entities.
                if part == "C07" and near(b[1], 8.525) and near(b[4], 8.525) and b[3] > 34.0:
                    groups["metal_face"].append(tag)
            elif dim == 1 and part == "C06":
                # Actual modeled R2 rail/shoulder transition around (+35,+20) in X-Z.
                if b[0] >= 34.99 and b[3] <= 37.01 and b[2] >= 19.99 and b[5] <= 22.01:
                    groups["rail_root"].append(tag)

    if part == "C07":
        # Pocket-edge curves are the exact boundary of the identified floor face.
        for face in groups["pocket_floor"]:
            groups["pocket_edge"].extend(tag for dim, tag in gmsh.model.getBoundary([(2, face)], combined=False, oriented=False) if dim == 1)
        groups["pocket_edge"] = sorted(set(groups["pocket_edge"]))
    required = ("load", "holes", "rail_root") if part == "C06" else ("holes", "pocket_floor", "pocket_edge", "metal_face")
    missing = [name for name in required if not groups[name]]
    if missing or len(groups["holes"]) != 6:
        raise RuntimeError(f"{part} exact B-Rep entity discovery failed: missing={missing}, holes={groups['holes']}")
    return rows, groups


def add_threshold(entities: list[int], dimension: int, size_min: float, size_max: float, dist_max: float) -> int:
    distance = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(distance, "CurvesList" if dimension == 1 else "FacesList", entities)
    gmsh.model.mesh.field.setNumber(distance, "Sampling", 120)
    threshold = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(threshold, "InField", distance)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMin", size_min)
    gmsh.model.mesh.field.setNumber(threshold, "SizeMax", size_max)
    gmsh.model.mesh.field.setNumber(threshold, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(threshold, "DistMax", dist_max)
    return threshold


def curve_samples(tags: list[int], spacing: float = 0.04) -> np.ndarray:
    samples: list[np.ndarray] = []
    for tag in tags:
        lo, hi = gmsh.model.getParametrizationBounds(1, tag)
        length = gmsh.model.occ.getMass(1, tag)
        count = max(12, int(math.ceil(length / spacing)) + 1)
        params = np.linspace(float(lo[0]), float(hi[0]), count)
        values = np.asarray(gmsh.model.getValue(1, tag, params.tolist()), dtype=float).reshape((-1, 3))
        samples.append(values)
    return np.vstack(samples)


def build_mesh(part: str, level: Level) -> tuple[MeshTet, dict[str, object], dict[str, set[int]], np.ndarray, list[dict[str, object]]]:
    step = CAD / "parts" / f"MV0-{part}_J2_{'positive_moving_striker' if part == 'C06' else 'positive_fixed_catch'}_adapter.step"
    t0 = time.perf_counter()
    gmsh.initialize(["-nopopup"])
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads1D", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads2D", 1)
        gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)
        gmsh.option.setNumber("Mesh.MeshSizeMin", min(level.rail_h, level.pocket_h, level.hole_h))
        gmsh.option.setNumber("Mesh.MeshSizeMax", level.global_h)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.RandomFactor", 1e-12)
        gmsh.model.add(f"R279_{part}_{level.name}")
        imported = gmsh.model.occ.importShapes(str(step))
        gmsh.model.occ.synchronize()
        if len(imported) != 1 or imported[0][0] != 3:
            raise RuntimeError(f"expected one STEP volume, got {imported}")
        entities, groups = entity_register(part)
        fields = [add_threshold(groups["holes"], 2, level.hole_h, level.global_h, 3.0)]
        if part == "C06":
            fields.append(add_threshold(groups["rail_root"], 1, level.rail_h, level.global_h, 4.0))
        else:
            fields.append(add_threshold(groups["pocket_edge"], 1, level.pocket_h, level.global_h, 2.5))
            fields.append(add_threshold(groups["pocket_floor"], 2, level.pocket_h, level.global_h, 1.5))
        minimum = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", fields)
        gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.model.mesh.generate(3)

        # Bind exact CAD surface entity node sets before extraction.
        surface_nodes: dict[str, set[int]] = {}
        for name in ("load", "holes", "pocket_floor", "metal_face"):
            tags: set[int] = set()
            for entity in groups[name]:
                node_tags, _, _ = gmsh.model.mesh.getNodes(2, entity, includeBoundary=True)
                tags.update(int(tag) for tag in node_tags)
            surface_nodes[name] = tags
        samples = curve_samples(groups["rail_root"] if part == "C06" else groups["pocket_edge"])

        node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
        all_points = np.asarray(coordinates, dtype=float).reshape((-1, 3))
        tag_xyz = {int(tag): all_points[index] for index, tag in enumerate(node_tags)}
        element_types, element_tags, element_nodes = gmsh.model.mesh.getElements(3)
        raw = tags = None
        for etype, etags, enodes in zip(element_types, element_tags, element_nodes):
            name, dim, order, count, _, _ = gmsh.model.mesh.getElementProperties(etype)
            if dim == 3 and order == 1 and count == 4 and "tetra" in name.lower():
                tags = np.asarray(etags, dtype=np.int64)
                raw = np.asarray(enodes, dtype=np.int64).reshape((-1, 4))
                break
        if raw is None or tags is None:
            raise RuntimeError("first-order tetrahedra not generated")
        corner_tags = sorted(set(int(value) for value in raw.ravel()))
        tag_to_index = {tag: index for index, tag in enumerate(corner_tags)}
        points = np.vstack([tag_xyz[tag] for tag in corner_tags])
        tets = np.asarray([[tag_to_index[int(tag)] for tag in tet] for tet in raw], dtype=np.int64)
        quality = np.asarray(gmsh.model.mesh.getElementQualities(tags.tolist(), "minSICN"), dtype=float)
        local_surface_indices = {name: {tag_to_index[tag] for tag in values if tag in tag_to_index} for name, values in surface_nodes.items()}
        mesh = MeshTet(points.T, tets.T)
        p2_dofs_if_solved = Basis(mesh, ElementVector(ElementTetP2())).N
        meta = {
            "identifier": IDENT, "part": part, "level": level.name, "step_sha256": sha256(step),
            "global_h_mm": level.global_h, "rail_h_mm": level.rail_h, "pocket_h_mm": level.pocket_h, "hole_h_mm": level.hole_h,
            "vertices": len(points), "tetrahedra": len(tets), "min_sicn": float(np.min(quality)),
            "p2_dofs_if_solved": p2_dofs_if_solved,
            "fraction_sicn_below_0p20": float(np.mean(quality < 0.20)), "mesh_seconds": time.perf_counter()-t0,
            "rss_after_mesh_mb": rss_mb(), "exact_entity_groups": groups,
            "geometry_order": 1,
            "high_order_geometry_limitation": "scikit-fem P2 displacement on straight-sided tetrahedra; Gmsh curved high-order nodes are not imported",
            "warning": WARNING,
        }
        return mesh, meta, local_surface_indices, samples, entities
    finally:
        gmsh.finalize()


def tagged_facets(mesh: MeshTet, node_indices: set[int]) -> np.ndarray:
    boundary = mesh.boundary_facets()
    selected = [facet for facet in boundary if all(int(node) in node_indices for node in mesh.facets[:, facet])]
    return np.asarray(selected, dtype=np.int64)


def area(mesh: MeshTet, facets: np.ndarray) -> float:
    total = 0.0
    for tri in mesh.facets[:, facets].T:
        a, b, c = mesh.p[:, tri].T
        total += np.linalg.norm(np.cross(b-a, c-a)) / 2.0
    return float(total)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    v, w = values[order], weights[order]
    return float(v[np.searchsorted(np.cumsum(w), q*np.sum(w), side="left")])


def solve_case(part: str, case: str, mesh: MeshTet, exact_nodes: dict[str, set[int]], feature_samples: np.ndarray, solution_order: int) -> tuple[dict[str, object], list[dict[str, object]]]:
    t0 = time.perf_counter()
    fixed_facets = tagged_facets(mesh, exact_nodes["holes"])
    if part == "C06":
        loaded_facets = tagged_facets(mesh, exact_nodes["load"])
        force = np.asarray([0.0, 2.186583449470536e-9, -FORCE_N])
    elif case == "C07_POCKET_FLOOR_EXACT_NORMAL":
        loaded_facets = tagged_facets(mesh, exact_nodes["pocket_floor"])
        force = np.asarray([0.0, -223.9218979819317, -119.06088380811465])
    else:
        loaded_facets = tagged_facets(mesh, exact_nodes["metal_face"])
        centers = mesh.p[:, mesh.facets[:, loaded_facets]].mean(axis=1)
        loaded_facets = loaded_facets[centers[0] > 34.0]
        force = np.asarray([0.0, -223.9218979819317, -119.06088380811465])
    if len(fixed_facets) < 12 or len(loaded_facets) < 4:
        raise RuntimeError(f"facet binding failed: {part}/{case}: fixed={len(fixed_facets)} load={len(loaded_facets)}")
    load_area = area(mesh, loaded_facets)
    traction = force/load_area
    scalar_element = ElementTetP2() if solution_order == 2 else ElementTetP1()
    vector_element = ElementVector(scalar_element)
    basis = Basis(mesh, vector_element)
    lam, mu = lame_parameters(E_MPA, POISSON)
    stiffness = asm(linear_elasticity(lam, mu), basis)

    @LinearForm
    def load(v, _w):
        return traction[0]*v[0] + traction[1]*v[1] + traction[2]*v[2]

    load_vector = asm(load, FacetBasis(mesh, vector_element, facets=loaded_facets))
    fixed_dofs = basis.get_dofs(facets=fixed_facets).all()
    displacement = solve(*condense(stiffness, load_vector, D=fixed_dofs))
    reaction = stiffness@displacement-load_vector
    applied = load_vector.reshape((-1, 3)).sum(axis=0)
    reacted = reaction.reshape((-1, 3)).sum(axis=0)
    field = basis.interpolate(displacement)
    grad = field.grad
    strain = 0.5*(grad+np.swapaxes(grad, 0, 1))
    trace = strain[0,0]+strain[1,1]+strain[2,2]
    stress = 2*mu*strain
    for i in range(3):
        stress[i,i] += lam*trace
    sx,sy,sz = stress[0,0],stress[1,1],stress[2,2]
    txy,tyz,tzx = stress[0,1],stress[1,2],stress[2,0]
    vm = np.sqrt(0.5*((sx-sy)**2+(sy-sz)**2+(sz-sx)**2)+3*(txy**2+tyz**2+tzx**2))
    weights = basis.dx
    elem_volume = weights.sum(axis=1)
    elem_mean = (vm*weights).sum(axis=1)/elem_volume
    centroids = mesh.p[:,mesh.t].mean(axis=1).T
    tree = cKDTree(feature_samples)
    feature_distance = tree.query(centroids, workers=1)[0]
    feature_zone = feature_distance <= (3.0 if part == "C06" else 1.0)
    # Fixed physical nonsingular hole ligament: 1..3 mm outside each bore, Y=1..8.525.
    ligament = np.zeros(len(centroids), dtype=bool)
    for x,z,r in [(-16,-8,1.35),(-16,8,1.35),(16,-8,1.35),(16,8,1.35),(0,-10,2.75),(0,10,2.75)]:
        radial = np.hypot(centroids[:,0]-x, centroids[:,2]-z)
        ligament |= (radial >= r+1.0)&(radial <= r+3.0)&(centroids[:,1]>=1.0)&(centroids[:,1]<=8.525)

    def zone_metrics(name: str, mask: np.ndarray) -> dict[str, object]:
        if not np.any(mask):
            raise RuntimeError(f"empty zone {name}")
        vals, vols = elem_mean[mask], elem_volume[mask]
        return {"case_id":case,"zone":name,"elements":int(np.sum(mask)),"volume_mm3":float(np.sum(vols)),
                "volume_weighted_mean_vm_mpa":float(np.average(vals,weights=vols)),
                "volume_weighted_rms_vm_mpa":float(np.sqrt(np.average(vals**2,weights=vols))),
                "volume_weighted_p95_vm_mpa":weighted_quantile(vals,vols,0.95),
                "raw_element_max_vm_mpa_not_for_capacity":float(np.max(vals)),"warning":WARNING}
    zones = [zone_metrics("C06_RR_PROFILE" if part=="C06" else "C07_POCKET_EDGE",feature_zone), zone_metrics("HOLE_LIGAMENTS_AGGREGATE",ligament)]
    energy = float(0.5*displacement@stiffness@displacement)
    result = {"identifier":IDENT,"part":part,"case_id":case,"solution_order":solution_order,"solution_dofs":basis.N,
              "fixed_facets":len(fixed_facets),"loaded_facets":len(loaded_facets),"loaded_area_mm2":load_area,
              "applied_fx_n":float(applied[0]),"applied_fy_n":float(applied[1]),"applied_fz_n":float(applied[2]),
              "reaction_fx_n":float(reacted[0]),"reaction_fy_n":float(reacted[1]),"reaction_fz_n":float(reacted[2]),
              "normalized_force_balance_error":float(np.linalg.norm(applied+reacted)/np.linalg.norm(applied)),
              "strain_energy_n_mm":energy,"maximum_solution_dof_displacement_mm":float(np.max(np.linalg.norm(displacement.reshape((-1,3)),axis=1))),
              "global_raw_quadrature_max_vm_mpa_not_for_capacity":float(np.max(vm)),"solve_seconds":time.perf_counter()-t0,
              "rss_after_solve_mb":rss_mb(),"convergence_accepted":False,"selection_or_release_effect":"NONE", "warning":WARNING}
    return result,zones


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--levels",default="L0",help="comma-separated subset of P2C,L0,L1,L2,L3; P2C is a coarse cross-check only")
    parser.add_argument("--parts",default="C06,C07",help="comma-separated C06,C07")
    parser.add_argument("--keep",action="store_true",help="retain existing scratch output and append")
    parser.add_argument("--mesh-only",action="store_true",help="stop after exact tagging/local mesh generation; no structural solve")
    parser.add_argument("--solution-order",type=int,choices=(1,2),default=2,help="P1 primary resource screen or P2 cross-check")
    args=parser.parse_args()
    selected_levels=[LEVELS[name] for name in args.levels.split(",")]
    parts=[] if args.parts.upper()=="NONE" else args.parts.split(",")
    if not args.keep and OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    def prior_rows(name: str) -> list[dict[str, object]]:
        path=OUT/name
        if not args.keep or not path.exists(): return []
        with path.open(newline="",encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))
    mesh_rows=prior_rows("mesh-register.csv"); result_rows=prior_rows("case-results.csv")
    zone_rows=prior_rows("zone-results.csv"); entity_rows=prior_rows("brep-entity-register.csv")
    for row in mesh_rows:
        # A mesh is usable by several polynomial orders; an early prototype
        # incorrectly called this `solution_order=2`.  Remove that ambiguity.
        row.pop("solution_order",None)
        row.pop("rss_after_mesh_mb",None)
        row["memory_capture"]="UNAVAILABLE IN-PROCESS; SEE ATTEMPT REGISTER FOR EXTERNAL OBSERVATIONS"
    for row in result_rows:
        if "maximum_p2_dof_displacement_mm" in row:
            row["maximum_solution_dof_displacement_mm"]=row.pop("maximum_p2_dof_displacement_mm")
        row.pop("rss_after_solve_mb",None)
        row["memory_capture"]="UNAVAILABLE IN-PROCESS; SEE ATTEMPT REGISTER FOR EXTERNAL OBSERVATIONS"
    attempt_rows=[
        {"attempt_id":"R279-ATTEMPT-01","part":"C06","level":"L0","solution_order":2,
         "mesh_vertices":40399,"mesh_tetrahedra":197167,"p2_dofs":884739,
         "elapsed_at_interrupt_s_lower_bound":180,"observed_working_set_mb":"6255..7000 (external Get-Process observation)",
         "result":"INTERRUPTED CLEANLY - DIRECT SPARSE P2 RESOURCE LIMIT; NO STRUCTURAL RESULT","convergence_or_release_credit":"NONE","warning":WARNING},
        {"attempt_id":"R279-ATTEMPT-02","part":"C06","level":"P2C","solution_order":2,
         "mesh_vertices":8027,"mesh_tetrahedra":33102,"p2_dofs":162702,
         "elapsed_at_interrupt_s_lower_bound":225,"observed_working_set_mb":"5048 and climbing (external Get-Process observation)",
         "result":"INTERRUPTED CLEANLY - COARSE DIRECT SPARSE P2 RESOURCE LIMIT; NO STRUCTURAL RESULT","convergence_or_release_credit":"NONE","warning":WARNING},
    ]
    write_csv(OUT/"attempt-register.csv",attempt_rows)
    for part in parts:
        for level in selected_levels:
            mesh,meta,exact_nodes,samples,entities=build_mesh(part,level)
            mesh_rows=[row for row in mesh_rows if not (row.get("part")==part and row.get("level")==level.name)]
            entity_rows=[row for row in entity_rows if row.get("part")!=part]
            mesh_rows.append(meta); entity_rows.extend(entities)
            # Persist mesh/resource evidence before any potentially expensive P2 solve.
            write_csv(OUT/"mesh-register.csv",mesh_rows)
            write_csv(OUT/"brep-entity-register.csv",entity_rows)
            if args.mesh_only:
                continue
            cases=["C06_EXACT_NORMAL_TOP"] if part=="C06" else ["C07_METAL_PERIMETER_EXACT_NORMAL","C07_POCKET_FLOOR_EXACT_NORMAL"]
            for case in cases:
                result,zones=solve_case(part,case,mesh,exact_nodes,samples,args.solution_order)
                result.update({"level":level.name,"vertices":meta["vertices"],"tetrahedra":meta["tetrahedra"]})
                for row in zones: row.update({"part":part,"level":level.name})
                result_rows.append(result); zone_rows.extend(zones)
            write_csv(OUT/"mesh-register.csv",mesh_rows); write_csv(OUT/"case-results.csv",result_rows)
            write_csv(OUT/"zone-results.csv",zone_rows); write_csv(OUT/"brep-entity-register.csv",entity_rows)
    mesh_executions=sorted({f"{row.get('part')}:{row.get('level')}" for row in mesh_rows})
    case_executions=sorted({f"{row.get('part')}:{row.get('level')}:P{row.get('solution_order')}:{row.get('case_id')}" for row in result_rows})
    quality_rejections=[f"{row.get('part')}:{row.get('level')}:minSICN={row.get('min_sicn')}" for row in mesh_rows if float(row.get('min_sicn',1.0))<0.10 or float(row.get('fraction_sicn_below_0p20',0.0))>0.001]
    # Rewrite all append-preserved tables so provenance normalization is not
    # deferred merely because the latest invocation was mesh-only.
    write_csv(OUT/"mesh-register.csv",mesh_rows); write_csv(OUT/"case-results.csv",result_rows)
    write_csv(OUT/"zone-results.csv",zone_rows); write_csv(OUT/"brep-entity-register.csv",entity_rows)
    status={"identifier":IDENT,"round":"R279-PROTOTYPE","cad_identifier":"HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE",
            "mesh_executions":mesh_executions,"case_executions":case_executions,"solver":"scikit-fem displacement / straight-sided tetrahedra; actual order is per case row",
            "mesh_quality_rejections":quality_rejections,
            "mesh_convergence_complete":False,"r278_h02_closed":False,"nonlinear_contact_complete":False,"joined_joint_complete":False,
            "selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,
            "mesh_only_on_latest_invocation":args.mesh_only,"latest_requested_solution_order":args.solution_order,
            "direct_p2_attempts_interrupted_for_resources":2,"known_limitations":["single execution is not convergence","straight-sided corner geometry in scikit-fem","ideal fixed-hole restraints","no nonlinear contact, joined hardware, dynamics, fatigue, tolerance or physical correlation"],"warning":WARNING}
    (OUT/"execution-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"meshes":mesh_rows,"cases":result_rows},indent=2,default=str))
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
