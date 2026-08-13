#!/usr/bin/env python3
"""Prototype an exact Gmsh Tet10 -> scikit-fem MeshTet2 geometry transfer.

This is numerical-method evidence only.  It does not establish convergence,
contact capacity, joint capacity, or authority for physical work.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import gmsh
import numpy as np
from skfem import MeshTet, MeshTet2

import generate_hr_v0_j2_stop_refinement_execution_p01 as base

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-curved-tet10-prototype-p0.1"
IDENT = "HR-V0-J2-CURVED-TET10-PROTOTYPE-P0.1"
WARNING = "PRELIMINARY - NUMERICAL METHOD PROTOTYPE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def execute(part: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    suffix = "positive_moving_striker" if part == "C06" else "positive_fixed_catch"
    step = CAD / f"MV0-{part}_J2_{suffix}_adapter.step"
    level = base.Level("CURVED_PROTOTYPE", 6.0, 1.8, 1.0, 1.4)
    gmsh.initialize(["-nopopup"])
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)
        gmsh.option.setNumber("Mesh.MeshSizeMin", min(level.rail_h, level.pocket_h, level.hole_h))
        gmsh.option.setNumber("Mesh.MeshSizeMax", level.global_h)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
        gmsh.option.setNumber("Mesh.Algorithm3D", 1 if part == "C07" else 10)
        gmsh.model.add(f"R282_{part}_CURVED")
        imported = gmsh.model.occ.importShapes(str(step)); gmsh.model.occ.synchronize()
        if len(imported) != 1 or imported[0][0] != 3:
            raise RuntimeError(f"expected one volume, got {imported}")
        entities, groups = base.entity_register(part)
        fields = [base.add_threshold(groups["holes"], 2, level.hole_h, level.global_h, 3.0)]
        if part == "C06":
            fields.append(base.add_threshold(groups["rail_root"], 1, level.rail_h, level.global_h, 4.0))
        else:
            fields.append(base.add_threshold(groups["pocket_edge"], 1, level.pocket_h, level.global_h, 2.5))
            fields.append(base.add_threshold(groups["pocket_floor"], 2, level.pocket_h, level.global_h, 1.5))
        minimum = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", fields)
        gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.model.mesh.generate(3)
        if part == "C07": gmsh.model.mesh.optimize("Netgen")
        gmsh.model.mesh.setOrder(2)
        tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
        element_tags, element_nodes = gmsh.model.mesh.getElementsByType(tet10)
        if len(element_tags) == 0: raise RuntimeError("no Tet10 elements")
        raw = np.asarray(element_nodes, dtype=np.int64).reshape((-1, 10))
        node_tags, coords, _ = gmsh.model.mesh.getNodes()
        xyz = np.asarray(coords).reshape((-1, 3))
        tag_xyz = {int(tag): xyz[i] for i, tag in enumerate(node_tags)}
        corner_tags = sorted(set(int(v) for v in raw[:, :4].ravel()))
        corner_index = {tag: i for i, tag in enumerate(corner_tags)}
        p = np.vstack([tag_xyz[tag] for tag in corner_tags]).T
        t = np.asarray([[corner_index[int(tag)] for tag in tet[:4]] for tet in raw], dtype=np.int64).T
        linear = MeshTet(p, t)
        curved = MeshTet2.from_mesh(linear)
        edge_nodes = np.asarray(gmsh.model.mesh.getElementEdgeNodes(tet10, primary=False), dtype=np.int64).reshape((-1, 6, 3))
        edge_map: dict[tuple[int, int], tuple[int, np.ndarray]] = {}
        consistency_max = 0.0
        for block in edge_nodes:
            for edge in block:
                # Gmsh returns each quadratic edge as [corner_a, corner_b,
                # midside].  The first prototype interpreted the triple as
                # [corner_a, midside, corner_b] and mapped zero edges; that
                # failed attempt is retained in failed-attempt-register.csv.
                key = tuple(sorted((int(edge[0]), int(edge[1]))))
                candidate = tag_xyz[int(edge[2])]
                if key in edge_map:
                    consistency_max = max(consistency_max, float(np.linalg.norm(edge_map[key][1]-candidate)))
                else:
                    edge_map[key] = (int(edge[2]), candidate)
        doflocs = curved.doflocs.copy()
        missing = 0
        max_shift = 0.0
        rows = []
        for edge_i, (a, b) in enumerate(curved.edges.T):
            key = tuple(sorted((corner_tags[int(a)], corner_tags[int(b)])))
            if key not in edge_map:
                missing += 1; continue
            dof = int(curved.dofs.edge_dofs[0, edge_i])
            midpoint = (doflocs[:, int(a)] + doflocs[:, int(b)]) / 2.0
            mid_tag, location = edge_map[key]
            shift = float(np.linalg.norm(location-midpoint)); max_shift = max(max_shift, shift)
            doflocs[:, dof] = location
            rows.append({"part":part,"edge_corner_tag_a":key[0],"edge_corner_tag_b":key[1],"gmsh_mid_node_tag":mid_tag,"scikit_geometry_dof":dof,"midpoint_shift_mm":shift,"warning":WARNING})
        curved = MeshTet2(doflocs, curved.t)
        # A positive curved Jacobian screen at the quadrature used by P2 assembly.
        mapping = curved.mapping()
        from skfem.quadrature import get_quadrature_tet
        X, _ = get_quadrature_tet(4)
        det = np.asarray(mapping.detDF(X))
        linear_det = np.asarray(linear.mapping().detDF(X))
        expected_sign = 1.0 if float(np.median(linear_det)) > 0 else -1.0
        linear_nonpositive = int(np.count_nonzero(linear_det*expected_sign <= 0.0))
        curved_nonpositive = int(np.count_nonzero(det*expected_sign <= 0.0))
        status = {
            "identifier": IDENT, "part": part, "step_sha256": sha(step),
            "tet10_elements": int(len(element_tags)), "corner_vertices": int(len(corner_tags)),
            "global_edges": int(curved.edges.shape[1]), "mapped_edge_dofs": int(len(rows)),
            "missing_edge_dofs": missing, "adjacent_mid_node_consistency_max_mm": consistency_max,
            "maximum_curved_midpoint_shift_mm": max_shift,
            "expected_jacobian_orientation_sign_from_linear_mesh": int(expected_sign),
            "linear_signed_jacobian_min": float(np.min(linear_det)), "linear_signed_jacobian_max": float(np.max(linear_det)),
            "curved_signed_jacobian_min": float(np.min(det)), "curved_signed_jacobian_max": float(np.max(det)),
            "linear_wrong_or_zero_jacobian_count": linear_nonpositive,
            "curved_wrong_or_zero_jacobian_count": curved_nonpositive,
            "curved_wrong_or_zero_jacobian_fraction": float(curved_nonpositive/det.size),
            "minimum_oriented_curved_jacobian": float(np.min(det*expected_sign)),
            "positive_curved_jacobian_screen": bool(linear_nonpositive == 0 and curved_nonpositive == 0 and missing == 0 and consistency_max <= 1e-12),
            "exact_surface_subface_route": "boundary facets remain bound by exact OCC entity corner-node membership; quadratic edge geometry is transferred from the same Tet10 mesh",
            "curved_geometry_execution_complete": False,
            "reason_not_complete": "prototype import only; no R279 L0-L3 curved solve or zone convergence was executed",
            "r278_h02_closed": False, "capacity_credit": False, "work_authority": False, "warning": WARNING,
        }
        return status, rows
    finally:
        gmsh.finalize()


def main() -> int:
    parser=argparse.ArgumentParser();parser.add_argument("--part",choices=("C06","C07"),required=True);args=parser.parse_args()
    if OUT.exists() and not (OUT/"failed-attempt-register.csv").exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    for stale in (OUT/"curved-import-register.csv",OUT/"edge-map-register.csv"):
        if stale.exists(): stale.unlink()
    if not (OUT/"failed-attempt-register.csv").exists():
        write_csv(OUT/"failed-attempt-register.csv", [{"attempt_id":"R282-CURVED-ATTEMPT-01","parts":"C06,C07","failure":"Gmsh quadratic edge triple incorrectly parsed as corner/midside/corner; zero global edges mapped","evidence":"partial prior curved-import-register: C06 0/18351 and C07 0/26209","correction":"parse each triple as corner_a/corner_b/midside and validate every global edge","credit":"NONE","warning":WARNING}])
    status, mappings = execute(args.part)
    write_csv(OUT/f"curved-import-{args.part.lower()}.csv", [status])
    write_csv(OUT/f"edge-map-{args.part.lower()}.csv", mappings)
    statuses=[]
    for part in ("c06","c07"):
        path=OUT/f"curved-import-{part}.csv"
        if path.exists():
            with path.open(newline="",encoding="utf-8-sig") as stream: statuses.extend(csv.DictReader(stream))
    complete=len(statuses)==2 and all(str(s["positive_curved_jacobian_screen"]).lower()=="true" for s in statuses)
    (OUT/"analysis-status.json").write_text(json.dumps({"identifier":IDENT,"parts":statuses,"both_import_screens_pass":complete,"curved_geometry_execution_complete":False,"r278_h02_closed":False,"warning":WARNING},indent=2)+"\n",encoding="utf-8")
    print(json.dumps(status,indent=2)); return 0 if status["positive_curved_jacobian_screen"] else 2


if __name__ == "__main__": raise SystemExit(main())
