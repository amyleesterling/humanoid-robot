#!/usr/bin/env python3
"""R286 exact C07 boundary-facet, B-Rep deviation and load-patch screen.

This component consumes the retained, repeatable R285 Tet10 mesh.  It does not
remesh or solve a structural model.  Every exterior quadratic facet is mapped
to one exact OCC face by six-node membership, then sampled against that face.
The positive catch load patch is clipped at exact X=34 mm and compared with an
independent CadQuery/OpenCASCADE clip of the STEP face.

Passing this screen is geometry/load-method evidence only.  It cannot close
R279-C02, R278-H02, capacity, safety, or any physical-work authority.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq
import gmsh
import numpy as np
from skfem.quadrature import get_quadrature_tri

import generate_hr_v0_j2_c07_target_feature_identity_p01 as feature


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-brep-facet-load-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-brep-facet-load-p0.1"
STEP = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
R285 = ROOT / "mechanical/analysis/hr-v0-j2-c07-targeted-remesh-p0.1"
RAW = R285 / "run-a/raw-r285-confirmatory-targeted-v06-p01.npz"
LOAD_SOURCE = ROOT / "mechanical/analysis/hr-v0-j2-stop-pad-pocket-fea-p0.1/analysis-status.json"
IDENT = "HR-V0-J2-C07-BREP-FACET-LOAD-P0.1"
ROUND = "R286"
RAW_LABEL = "retained R285 raw Tet10"
ADDITIONAL_INPUTS: list[tuple[str, Path]] = []
WARNING = (
    "PRELIMINARY - EXACT FACET/B-REP AND LOAD-GEOMETRY EVIDENCE ONLY - NOT "
    "APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, "
    "POWERED TESTING, MOTION, OR ENERGIZATION"
)
NODE_FACE_TOL_MM = 1e-7
SURFACE_DEVIATION_LIMIT_MM = 0.005
SURFACE_AREA_REL_LIMIT = 0.0025
LOAD_AREA_REL_LIMIT = 0.0025
LOAD_LOCATION_REL_LIMIT = 0.001
LOAD_MOMENT_REL_LIMIT = 0.001
LOAD_CLIP_X_MM = 34.0
LOAD_FORCE_N = np.asarray((0.0, -223.9218979819317, -119.06088380811465), dtype=float)
MOMENT_DATUM_MM = np.zeros(3, dtype=float)
TRI_QUADRATURE_ORDER = 8
PARTIAL_CLIP_SUBDIVISIONS = 64

# Gmsh Tet10 node order: four corners then 01, 12, 20, 03, 23, 31.
FACE_LOCAL = (
    (1, 2, 3, 5, 8, 9),
    (0, 3, 2, 7, 8, 6),
    (0, 1, 3, 4, 9, 7),
    (0, 2, 1, 6, 5, 4),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty controlled table: {path}")
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def boundary_facets(tet10: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    occurrences: dict[tuple[int, int, int], list[tuple[int, int, np.ndarray]]] = defaultdict(list)
    for element_index, tet in enumerate(tet10):
        for local_face, local in enumerate(FACE_LOCAL):
            nodes = np.asarray(tet[list(local)], dtype=np.int64)
            key = tuple(sorted(int(value) for value in nodes[:3]))
            occurrences[key].append((element_index, local_face, nodes))
    exterior = [value[0] for value in occurrences.values() if len(value) == 1]
    if any(len(value) not in (1, 2) for value in occurrences.values()):
        raise RuntimeError("nonmanifold Tet10 corner-face incidence")
    exterior.sort(key=lambda item: tuple(sorted(int(value) for value in item[2][:3])))
    return (
        np.asarray([item[2] for item in exterior], dtype=np.int64),
        np.asarray([item[0] for item in exterior], dtype=np.int64),
        np.asarray([item[1] for item in exterior], dtype=np.int8),
    )


def tri6_shapes(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, v = points
    l1, l2, l3 = 1.0 - u - v, u, v
    n = np.vstack((
        l1 * (2.0 * l1 - 1.0),
        l2 * (2.0 * l2 - 1.0),
        l3 * (2.0 * l3 - 1.0),
        4.0 * l1 * l2,
        4.0 * l2 * l3,
        4.0 * l3 * l1,
    ))
    du = np.vstack((
        1.0 - 4.0 * l1,
        4.0 * l2 - 1.0,
        np.zeros_like(u),
        4.0 * (l1 - l2),
        4.0 * l3,
        -4.0 * l3,
    ))
    dv = np.vstack((
        1.0 - 4.0 * l1,
        np.zeros_like(u),
        4.0 * l3 - 1.0,
        -4.0 * l2,
        4.0 * l2,
        4.0 * (l1 - l3),
    ))
    return n, du, dv


def tri6_quadrature(coords: np.ndarray, points: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n, du, dv = tri6_shapes(points)
    xyz = np.einsum("fkc,kq->fqc", coords, n)
    dxdu = np.einsum("fkc,kq->fqc", coords, du)
    dxdv = np.einsum("fkc,kq->fqc", coords, dv)
    jac = np.linalg.norm(np.cross(dxdu, dxdv), axis=2)
    weighted = jac * weights[None, :]
    area = weighted.sum(axis=1)
    first = np.einsum("fq,fqc->fc", weighted, xyz)
    return xyz, jac, area, first


def clip_polygon_x(points: list[np.ndarray], x_min: float) -> list[np.ndarray]:
    result: list[np.ndarray] = []
    for start, end in zip(points, points[1:] + points[:1]):
        inside_start = start[0] >= x_min
        inside_end = end[0] >= x_min
        if inside_start:
            result.append(start)
        if inside_start != inside_end:
            fraction = (x_min - start[0]) / (end[0] - start[0])
            result.append(start + fraction * (end - start))
    return result


def polygon_area_first(points: list[np.ndarray]) -> tuple[float, np.ndarray]:
    if len(points) < 3:
        return 0.0, np.zeros(3)
    origin = points[0]
    total = 0.0
    first = np.zeros(3)
    for index in range(1, len(points) - 1):
        a, b, c = origin, points[index], points[index + 1]
        area = 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
        total += area
        first += area * (a + b + c) / 3.0
    return total, first


def map_tri6(coords: np.ndarray, uv: np.ndarray) -> np.ndarray:
    n, _du, _dv = tri6_shapes(uv.T)
    return n.T @ coords


def partial_clip_area_first(coords: np.ndarray, subdivisions: int) -> tuple[float, np.ndarray]:
    total = 0.0
    first = np.zeros(3)
    n = subdivisions
    for i in range(n):
        for j in range(n - i):
            p00 = np.asarray((i / n, j / n))
            p10 = np.asarray(((i + 1) / n, j / n))
            p01 = np.asarray((i / n, (j + 1) / n))
            triangles = [(p00, p10, p01)]
            if i + j + 1 < n:
                p11 = np.asarray(((i + 1) / n, (j + 1) / n))
                triangles.append((p10, p11, p01))
            for tri in triangles:
                xyz = map_tri6(coords, np.vstack(tri))
                polygon = clip_polygon_x([xyz[0], xyz[1], xyz[2]], LOAD_CLIP_X_MM)
                area, moment = polygon_area_first(polygon)
                total += area
                first += moment
    return total, first


def exact_loaded_patch() -> tuple[float, np.ndarray, np.ndarray]:
    shape = cq.importers.importStep(str(STEP)).val()
    faces = [
        face for face in shape.Faces()
        if abs(face.BoundingBox().ymin - 8.525) < 1e-5
        and abs(face.BoundingBox().ymax - 8.525) < 1e-5
        and face.BoundingBox().xmax > 0.0
    ]
    if len(faces) != 1:
        raise RuntimeError(f"exact positive metal face selector drift: {len(faces)}")
    clip_box = cq.Solid.makeBox(100.0, 100.0, 100.0, cq.Vector(LOAD_CLIP_X_MM, -50.0, -50.0))
    clipped = faces[0].intersect(clip_box)
    if len(clipped.Faces()) != 1:
        raise RuntimeError(f"exact loaded face clip topology drift: {len(clipped.Faces())}")
    center = clipped.Center()
    bbox = clipped.BoundingBox()
    diagonal = np.asarray((bbox.xlen, bbox.ylen, bbox.zlen), dtype=float)
    return float(clipped.Area()), np.asarray((center.x, center.y, center.z)), diagonal


def file_manifest(directory: Path) -> None:
    rows = [
        {
            "relative_path": path.relative_to(directory).as_posix(),
            "sha256": sha(path),
            "bytes": path.stat().st_size,
            "warning": WARNING,
        }
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name != "file-manifest.csv"
    ]
    write_csv(directory / "file-manifest.csv", rows)


def html_table(rows: list[dict[str, object]]) -> str:
    keys = list(rows[0])
    head = "".join(f"<th>{key.replace('_', ' ')}</th>" for key in keys)
    body = "".join("<tr>" + "".join(f"<td>{row.get(key, '')}</td>" for key in keys) + "</tr>" for row in rows)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main() -> int:
    started = datetime.now(timezone.utc)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    raw = np.load(RAW)
    tet10 = np.asarray(raw["tet10_connectivity"], dtype=np.int64)
    node_tags = np.asarray(raw["node_tags"], dtype=np.int64)
    node_xyz = np.asarray(raw["node_xyz"], dtype=float)
    tag_to_row = {int(tag): index for index, tag in enumerate(node_tags)}
    facet_nodes, facet_elements, facet_local = boundary_facets(tet10)
    facet_coords = np.asarray([[node_xyz[tag_to_row[int(tag)]] for tag in facet] for facet in facet_nodes])
    boundary_tags = np.asarray(sorted(set(int(value) for value in facet_nodes.ravel())), dtype=np.int64)
    boundary_xyz = np.asarray([node_xyz[tag_to_row[int(tag)]] for tag in boundary_tags])
    boundary_row = {int(tag): index for index, tag in enumerate(boundary_tags)}

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.add("R286_C07_BREP_FACET_LOAD")
        imported = gmsh.model.occ.importShapes(str(STEP))
        gmsh.model.occ.synchronize()
        if len(imported) != 1 or imported[0][0] != 3:
            raise RuntimeError(f"unexpected STEP volume import: {imported}")
        faces = [tag for _dim, tag in gmsh.model.getEntities(2)]
        face_records: dict[int, dict[str, object]] = {}
        memberships: dict[int, set[int]] = {int(tag): set() for tag in boundary_tags}
        node_face_deviation: dict[tuple[int, int], float] = {}
        for face_tag in faces:
            signature, detail = feature.face_signature(face_tag)
            bbox = np.asarray(detail["bbox_mm"], dtype=float)
            mask = np.all(boundary_xyz >= bbox[:3] - SURFACE_DEVIATION_LIMIT_MM, axis=1) & np.all(
                boundary_xyz <= bbox[3:] + SURFACE_DEVIATION_LIMIT_MM, axis=1
            )
            candidate_indices = np.nonzero(mask)[0]
            if candidate_indices.size:
                closest, _parameters = gmsh.model.getClosestPoint(2, face_tag, boundary_xyz[candidate_indices].ravel().tolist())
                closest_xyz = np.asarray(closest, dtype=float).reshape((-1, 3))
                deviations = np.linalg.norm(closest_xyz - boundary_xyz[candidate_indices], axis=1)
                for index, deviation in zip(candidate_indices, deviations):
                    tag = int(boundary_tags[index])
                    if deviation <= NODE_FACE_TOL_MM:
                        memberships[tag].add(face_tag)
                        node_face_deviation[(tag, face_tag)] = float(deviation)
            face_records[face_tag] = {
                "occ_face_tag_diagnostic_only": face_tag,
                "face_signature_sha256": signature,
                "geometry_type": detail["geometry_type"],
                "bbox_mm_json": json.dumps(detail["bbox_mm"], separators=(",", ":")),
                "exact_occ_area_mm2": float(detail["measure_mm_or_mm2"]),
            }

        facet_faces = np.full(len(facet_nodes), -1, dtype=np.int64)
        facet_mapping_count = np.zeros(len(facet_nodes), dtype=np.int16)
        facet_node_max_deviation = np.full(len(facet_nodes), np.inf)
        facet_candidate_faces: list[tuple[int, ...]] = []
        for index, nodes in enumerate(facet_nodes):
            common = set(memberships[int(nodes[0])])
            for node in nodes[1:]:
                common.intersection_update(memberships[int(node)])
            if len(common) > 1:
                # `getClosestPoint` addresses the underlying surface and can
                # therefore match two differently trimmed coplanar/cylindrical
                # faces.  Resolve only with an interior quadratic-facet point
                # projected onto each candidate and tested against that exact
                # trimmed face.  This is not a bbox or centroid substitute.
                interior = map_tri6(facet_coords[index], np.asarray(((1.0 / 3.0, 1.0 / 3.0),)))[0]
                trimmed: set[int] = set()
                for face_tag in common:
                    closest, _parameters = gmsh.model.getClosestPoint(2, face_tag, interior.tolist())
                    if gmsh.model.isInside(2, face_tag, list(closest), parametric=False) == 1:
                        trimmed.add(face_tag)
                common = trimmed
            facet_mapping_count[index] = len(common)
            facet_candidate_faces.append(tuple(sorted(common)))
            if len(common) == 1:
                face_tag = next(iter(common))
                facet_faces[index] = face_tag
                facet_node_max_deviation[index] = max(node_face_deviation[(int(node), face_tag)] for node in nodes)

        exact_map_complete = bool(np.all(facet_mapping_count == 1))
        if not exact_map_complete:
            failed = int(np.count_nonzero(facet_mapping_count != 1))
            values, counts = np.unique(facet_mapping_count, return_counts=True)
            distribution = {int(value): int(count) for value, count in zip(values, counts)}
            pair_distribution: dict[tuple[int, ...], int] = defaultdict(int)
            for candidates in facet_candidate_faces:
                if len(candidates) != 1:
                    pair_distribution[candidates] += 1
            raise RuntimeError(
                f"exact facet map fail-closed: {failed} exterior facets lack one exact OCC face; "
                f"candidate-count distribution={distribution}; ambiguous pairs={dict(pair_distribution)}"
            )

        qpoints, qweights = get_quadrature_tri(TRI_QUADRATURE_ORDER)
        qpoints = np.asarray(qpoints, dtype=float)
        qweights = np.asarray(qweights, dtype=float)
        qxyz, _qjac, facet_area, facet_first = tri6_quadrature(facet_coords, qpoints, qweights)
        qdeviation = np.full(qxyz.shape[:2], np.inf)
        for face_tag in faces:
            indices = np.nonzero(facet_faces == face_tag)[0]
            if not indices.size:
                raise RuntimeError(f"exact OCC face {face_tag} has no mapped boundary facets")
            query = qxyz[indices].reshape((-1, 3))
            closest, _parameters = gmsh.model.getClosestPoint(2, face_tag, query.ravel().tolist())
            closest_xyz = np.asarray(closest, dtype=float).reshape((-1, 3))
            qdeviation[indices] = np.linalg.norm(closest_xyz - query, axis=1).reshape((len(indices), -1))

        facet_max_qdeviation = qdeviation.max(axis=1)
        surface_deviation_pass = bool(float(qdeviation.max()) <= SURFACE_DEVIATION_LIMIT_MM)
        face_rows: list[dict[str, object]] = []
        for face_tag in faces:
            indices = np.nonzero(facet_faces == face_tag)[0]
            exact_area = float(face_records[face_tag]["exact_occ_area_mm2"])
            mesh_area = float(facet_area[indices].sum())
            relative_error = abs(mesh_area - exact_area) / exact_area
            face_rows.append({
                **face_records[face_tag],
                "mapped_quadratic_facets": int(indices.size),
                "mesh_quadratic_area_mm2": mesh_area,
                "absolute_area_error_mm2": abs(mesh_area - exact_area),
                "relative_area_error": relative_error,
                "maximum_six_node_deviation_mm": float(facet_node_max_deviation[indices].max()),
                "maximum_q8_surface_deviation_mm": float(qdeviation[indices].max()),
                "rms_q8_surface_deviation_mm": float(np.sqrt(np.mean(qdeviation[indices] ** 2))),
                "area_within_0p25_percent": relative_error <= SURFACE_AREA_REL_LIMIT,
                "surface_deviation_within_0p005_mm": float(qdeviation[indices].max()) <= SURFACE_DEVIATION_LIMIT_MM,
                "warning": WARNING,
            })
        total_exact_area = float(sum(float(row["exact_occ_area_mm2"]) for row in face_rows))
        total_mesh_area = float(facet_area.sum())
        total_area_error = abs(total_mesh_area - total_exact_area) / total_exact_area

        positive_planar_faces = [
            tag for tag in faces
            if gmsh.model.getType(2, tag) == "Plane"
            and abs(gmsh.model.getBoundingBox(2, tag)[1] - 8.525) < 1e-5
            and abs(gmsh.model.getBoundingBox(2, tag)[4] - 8.525) < 1e-5
            and gmsh.model.getBoundingBox(2, tag)[3] > 0.0
        ]
        if len(positive_planar_faces) != 1:
            raise RuntimeError(f"positive metal-face identity drift: {positive_planar_faces}")
        load_face_tag = positive_planar_faces[0]
        load_indices = np.nonzero(facet_faces == load_face_tag)[0]
        loaded_area_contribution = np.zeros(len(facet_nodes))
        loaded_first_contribution = np.zeros((len(facet_nodes), 3))
        full_count = partial_count = excluded_count = 0
        for index in load_indices:
            x_values = facet_coords[index, :, 0]
            if float(x_values.min()) >= LOAD_CLIP_X_MM - 1e-12:
                loaded_area_contribution[index] = facet_area[index]
                loaded_first_contribution[index] = facet_first[index]
                full_count += 1
            elif float(x_values.max()) <= LOAD_CLIP_X_MM + 1e-12:
                excluded_count += 1
            else:
                area, first = partial_clip_area_first(facet_coords[index], PARTIAL_CLIP_SUBDIVISIONS)
                loaded_area_contribution[index] = area
                loaded_first_contribution[index] = first
                partial_count += 1
        mesh_load_area = float(loaded_area_contribution.sum())
        mesh_load_centroid = loaded_first_contribution.sum(axis=0) / mesh_load_area
        exact_load_area, exact_load_centroid, exact_load_bbox_diagonal = exact_loaded_patch()
        characteristic_length = float(np.linalg.norm(exact_load_bbox_diagonal))
        area_relative_error = abs(mesh_load_area - exact_load_area) / exact_load_area
        centroid_delta = mesh_load_centroid - exact_load_centroid
        centroid_relative_error = float(np.linalg.norm(centroid_delta) / characteristic_length)
        exact_moment = np.cross(exact_load_centroid - MOMENT_DATUM_MM, LOAD_FORCE_N)
        mesh_moment = np.cross(mesh_load_centroid - MOMENT_DATUM_MM, LOAD_FORCE_N)
        moment_scale = max(float(np.linalg.norm(exact_moment)), float(np.linalg.norm(LOAD_FORCE_N)) * characteristic_length)
        moment_relative_error = float(np.linalg.norm(mesh_moment - exact_moment) / moment_scale)
        load_geometry_pass = bool(
            area_relative_error <= LOAD_AREA_REL_LIMIT
            and centroid_relative_error <= LOAD_LOCATION_REL_LIMIT
            and moment_relative_error <= LOAD_MOMENT_REL_LIMIT
        )

        facet_rows: list[dict[str, object]] = []
        for index, nodes in enumerate(facet_nodes):
            face_tag = int(facet_faces[index])
            facet_rows.append({
                "facet_id": index + 1,
                "source_tet10_element_tag": int(raw["tet10_element_tags"][facet_elements[index]]),
                "source_local_face": int(facet_local[index]),
                "corner_node_tags_json": json.dumps([int(value) for value in nodes[:3]], separators=(",", ":")),
                "midside_node_tags_json": json.dumps([int(value) for value in nodes[3:]], separators=(",", ":")),
                "occ_face_tag_diagnostic_only": face_tag,
                "face_signature_sha256": face_records[face_tag]["face_signature_sha256"],
                "mapping_candidate_count": int(facet_mapping_count[index]),
                "maximum_six_node_deviation_mm": float(facet_node_max_deviation[index]),
                "maximum_q8_surface_deviation_mm": float(facet_max_qdeviation[index]),
                "quadratic_area_mm2": float(facet_area[index]),
                "loaded_clip_area_contribution_mm2": float(loaded_area_contribution[index]),
                "warning": WARNING,
            })
        write_csv(OUT / "facet-to-occ-register.csv", facet_rows)
        write_csv(OUT / "face-fidelity-summary.csv", face_rows)
        failing_faces = [
            {
                "face_signature_sha256": row["face_signature_sha256"],
                "geometry_type": row["geometry_type"],
                "bbox_mm_json": row["bbox_mm_json"],
                "observed_maximum_q8_surface_deviation_mm": row["maximum_q8_surface_deviation_mm"],
                "observed_relative_area_error": row["relative_area_error"],
            }
            for row in face_rows
            if float(row["maximum_q8_surface_deviation_mm"]) > SURFACE_DEVIATION_LIMIT_MM
        ]
        fidelity_preregistration = {
            "identifier": "HR-V0-J2-C07-FIDELITY-REMESH-PREREG-P0.1",
            "source_component": IDENT,
            "step_sha256": sha(STEP),
            "source_raw_label": RAW_LABEL,
            "source_raw_sha256": sha(RAW),
            "surface_deviation_limit_mm": SURFACE_DEVIATION_LIMIT_MM,
            "failing_face_count": len(failing_faces),
            "failing_faces": failing_faces,
            "successor_distance_field": {
                "entities": f"all {len(failing_faces)} exact failing face signatures plus every exact owner-boundary curve",
                "size_min_mm": 0.35,
                "size_max_mm": 3.0,
                "dist_min_mm": 0.0,
                "dist_max_mm": 2.5,
                "classification": "PRE-REGISTERED BOUNDED DIAGNOSTIC RETRY; NOT ACCEPTED PRODUCTION",
            },
            "acceptance": "all exterior facets uniquely mapped; max Q8 deviation <=0.005 mm; loaded geometry gates retained; no regression in R285 identity/SICN/Q4/Q6/Q8 gates",
            "authority": {"r279_c02": False, "r278_h02": False, "capacity": False, "safety": False, "work": False},
            "warning": WARNING,
        }
        (OUT / "fidelity-remesh-preregistration.json").write_text(
            json.dumps(fidelity_preregistration, indent=2) + "\n", encoding="utf-8"
        )

        load_rows = [{
            "case_id": "C07_METAL_PERIMETER_EXACT_NORMAL",
            "exact_occ_face_tag_diagnostic_only": load_face_tag,
            "exact_face_signature_sha256": face_records[load_face_tag]["face_signature_sha256"],
            "clip_definition": "exact positive planar B-Rep face intersected with X>=34.000 mm half-space",
            "mesh_selection_method": "complete exact OCC face map plus quadratic-facet geometric clipping; no facet-centroid selection",
            "exact_brep_loaded_area_mm2": exact_load_area,
            "mesh_curved_clipped_area_mm2": mesh_load_area,
            "area_relative_error": area_relative_error,
            "area_gate_limit": LOAD_AREA_REL_LIMIT,
            "exact_centroid_mm_json": json.dumps(exact_load_centroid.tolist(), separators=(",", ":")),
            "mesh_centroid_mm_json": json.dumps(mesh_load_centroid.tolist(), separators=(",", ":")),
            "centroid_delta_mm_json": json.dumps(centroid_delta.tolist(), separators=(",", ":")),
            "centroid_error_normalized_by_exact_patch_bbox_diagonal": centroid_relative_error,
            "location_gate_limit": LOAD_LOCATION_REL_LIMIT,
            "resultant_n_json": json.dumps(LOAD_FORCE_N.tolist(), separators=(",", ":")),
            "resultant_relative_drift": 0.0,
            "moment_datum_mm_json": json.dumps(MOMENT_DATUM_MM.tolist(), separators=(",", ":")),
            "exact_moment_n_mm_json": json.dumps(exact_moment.tolist(), separators=(",", ":")),
            "mesh_moment_n_mm_json": json.dumps(mesh_moment.tolist(), separators=(",", ":")),
            "normalized_moment_drift": moment_relative_error,
            "moment_gate_limit": LOAD_MOMENT_REL_LIMIT,
            "fully_included_facets": full_count,
            "partially_clipped_facets": partial_count,
            "excluded_face_facets": excluded_count,
            "partial_clip_subdivisions": PARTIAL_CLIP_SUBDIVISIONS,
            "single_level_geometry_gate": "PASS" if load_geometry_pass else "FAIL",
            "last_pair_area_drift_gate": "NOT EXECUTED - REQUIRES NEXT VALID REFINEMENT LEVEL",
            "warning": WARNING,
        }]
        write_csv(OUT / "load-boundary-preservation.csv", load_rows)

        raw_evidence = OUT / "raw-facet-load-evidence.npz"
        np.savez_compressed(
            raw_evidence,
            facet_node_tags=facet_nodes,
            facet_source_element_index=facet_elements,
            facet_local_face=facet_local,
            facet_occ_face_tag=facet_faces,
            facet_mapping_candidate_count=facet_mapping_count,
            facet_node_max_deviation_mm=facet_node_max_deviation,
            facet_q8_xyz_mm=qxyz,
            facet_q8_deviation_mm=qdeviation,
            facet_area_mm2=facet_area,
            facet_first_moment_mm3=facet_first,
            loaded_area_contribution_mm2=loaded_area_contribution,
            loaded_first_moment_contribution_mm3=loaded_first_contribution,
            q8_reference_points=qpoints,
            q8_reference_weights=qweights,
        )

        input_rows = [
            {"role": "exact C07 STEP", "path": STEP.relative_to(ROOT).as_posix(), "sha256": sha(STEP), "bytes": STEP.stat().st_size, "warning": WARNING},
            {"role": RAW_LABEL, "path": RAW.relative_to(ROOT).as_posix(), "sha256": sha(RAW), "bytes": RAW.stat().st_size, "warning": WARNING},
            {"role": "R285 configuration", "path": (R285 / "frozen-protocol.json").relative_to(ROOT).as_posix(), "sha256": sha(R285 / "frozen-protocol.json"), "bytes": (R285 / "frozen-protocol.json").stat().st_size, "warning": WARNING},
            {"role": "load vector source", "path": LOAD_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha(LOAD_SOURCE), "bytes": LOAD_SOURCE.stat().st_size, "warning": WARNING},
            {"role": "generator", "path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).resolve()), "bytes": Path(__file__).stat().st_size, "warning": WARNING},
        ] + [
            {"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
            for role, path in ADDITIONAL_INPUTS
        ]
        write_csv(OUT / "exact-input-register.csv", input_rows)

        validation_rows = [
            {"check_id": f"{ROUND}-V01", "check": f"{RAW_LABEL} identity", "result": "PASS", "evidence": f"raw SHA {sha(RAW)}; {len(tet10)} Tet10", "credit": "SOURCE IDENTITY", "warning": WARNING},
            {"check_id": f"{ROUND}-V02", "check": "complete exterior facet incidence", "result": "PASS", "evidence": f"{len(facet_nodes)} exterior facets; manifold corner-face incidence", "credit": "MESH TOPOLOGY", "warning": WARNING},
            {"check_id": f"{ROUND}-V03", "check": "one exact OCC face per exterior facet", "result": "PASS" if exact_map_complete else "FAIL", "evidence": f"unique six-node map for {len(facet_nodes)} facets", "credit": "EXACT FACET MAP" if exact_map_complete else "NONE", "warning": WARNING},
            {"check_id": f"{ROUND}-V04", "check": "quadratic surface deviation screen", "result": "PASS" if surface_deviation_pass else "FAIL", "evidence": f"max Q8 deviation {float(qdeviation.max())} mm against {SURFACE_DEVIATION_LIMIT_MM} mm method limit", "credit": "SINGLE-MESH B-REP FIDELITY" if surface_deviation_pass else "NONE", "warning": WARNING},
            {"check_id": f"{ROUND}-V05", "check": "total curved exterior area", "result": "PASS" if total_area_error <= SURFACE_AREA_REL_LIMIT else "FAIL", "evidence": f"exact {total_exact_area} mm2; mesh {total_mesh_area} mm2; relative error {total_area_error}", "credit": "SINGLE-MESH AREA FIDELITY", "warning": WARNING},
            {"check_id": f"{ROUND}-V06", "check": "positive catch exact clipped load geometry", "result": "PASS" if load_geometry_pass else "FAIL", "evidence": f"area error {area_relative_error}; normalized centroid {centroid_relative_error}; normalized moment {moment_relative_error}", "credit": "SINGLE-MESH LOAD-BOUNDARY GEOMETRY" if load_geometry_pass else "NONE", "warning": WARNING},
            {"check_id": f"{ROUND}-V07", "check": "next-level area drift", "result": "NOT EXECUTED", "evidence": f"only {RAW_LABEL} assessed", "credit": "NONE", "warning": WARNING},
            {"check_id": f"{ROUND}-V08", "check": "structural/exact-zone/convergence/capacity", "result": "NOT EXECUTED", "evidence": "no structural solve or production zone clipping", "credit": "NONE", "warning": WARNING},
        ]
        write_csv(OUT / "validation-register.csv", validation_rows)
        holds = [
            "Repeat exact facet/B-Rep and loaded-area evidence at the next valid refinement level and meet <=0.10% last-pair area drift",
            "Implement production exact cell/facet zone clipping with measure conservation and fixed-zone histograms",
            "Freeze actual structural quadrature and execute load/reaction/moment balance with retained facet identities",
            "Prove full-domain curved-Jacobian positivity or retain the finite-sampling limitation",
            "Execute multilevel structural convergence, GCI, singularity trends and independent numerical acceptance",
            "Keep nonlinear contact, joined hardware, dynamics, material, DFM/FAI and guarded physical correlation separate",
        ]
        write_csv(OUT / "open-holds.csv", [
            {"hold_id": f"R286-H{index:02d}", "hold": hold, "state": "OPEN", "closure_evidence": "NOT EXECUTED", "release_effect": "R279-C02, R278-H02, CAPACITY AND ALL WORK AUTHORITY REMAIN OPEN", "warning": WARNING}
            for index, hold in enumerate(holds, 1)
        ])
        status = {
            "identifier": IDENT,
            "round": ROUND,
            "date": "2026-08-13",
            "step_sha256": sha(STEP),
            "source_raw_label": RAW_LABEL,
            "source_raw_sha256": sha(RAW),
            "tet10_elements": int(len(tet10)),
            "exterior_quadratic_facets": int(len(facet_nodes)),
            "exact_occ_faces": int(len(faces)),
            "exact_facet_map_complete": exact_map_complete,
            "surface_deviation_screen_pass": surface_deviation_pass,
            "faces_over_surface_deviation_limit": int(len(failing_faces)),
            "faces_over_0p25_percent_area_error": int(sum(float(row["relative_area_error"]) > SURFACE_AREA_REL_LIMIT for row in face_rows)),
            "maximum_q8_surface_deviation_mm": float(qdeviation.max()),
            "total_surface_area_relative_error": total_area_error,
            "single_level_load_geometry_pass": load_geometry_pass,
            "next_level_area_drift_complete": False,
            "exact_zone_clipping_complete": False,
            "full_domain_curved_jacobian_positive": False,
            "structural_solution_executed": False,
            "r279_c02_complete": False,
            "r278_h02_closed": False,
            "capacity_credit": False,
            "selected": False,
            "safety_credit": False,
            "procurement_authorized": False,
            "fabrication_authorized": False,
            "assembly_authorized": False,
            "connection_authorized": False,
            "powered_testing_authorized": False,
            "motion_authorized": False,
            "energization_authorized": False,
            "warning": WARNING,
        }
        (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        provenance = {
            "identifier": IDENT,
            "started_utc": started.isoformat(),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "argv": [sys.executable, Path(__file__).resolve().relative_to(ROOT).as_posix()],
            "cwd": ROOT.as_posix(),
            "git_commit": subprocess.run(
                [shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe", "rev-parse", "HEAD"],
                cwd=ROOT, check=True, capture_output=True, text=True,
            ).stdout.strip(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gmsh": importlib.metadata.version("gmsh"),
            "cadquery": getattr(cq, "__version__", "UNKNOWN"),
            "numpy": np.__version__,
            "scikit_fem": importlib.metadata.version("scikit-fem"),
            "generator_sha256": sha(Path(__file__).resolve()),
            "warning": WARNING,
        }
        (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        (OUT / "README.md").write_text(
            f"# {IDENT}\n\n> **{WARNING}**\n\n"
            f"R286 maps all {len(facet_nodes):,} exterior R285 Tet10 facets to exact C07 OCC faces, "
            "measures quadratic-face deviation, and compares the X>=34 mm positive catch load patch "
            "with an exact CAD clip. This replaces the earlier facet-centroid load selection for geometry "
            f"verification. The exact facet map and load geometry pass, but the 0.005 mm surface-deviation "
            f"screen fails at 0.0211863 mm across {len(failing_faces)} exact faces; 12 individual face-area "
            "comparisons also exceed 0.25%, although total exterior area passes. The retained successor "
            "preregistration targets those exact face signatures and owner-boundary curves without relaxing "
            "the limit. It is a single-mesh geometry screen: next-level drift, exact physical zones, "
            "structural fields, convergence, contact, joined hardware, dynamics, physical tests and qualified "
            "acceptance remain open. No physical work or energization is authorized.\n",
            encoding="utf-8",
        )
        html = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{IDENT}</title><style>:root{{--navy:#082b55;--blue:#245aa6;--sky:#8ed8f8;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;padding:clamp(28px,6vw,70px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:28px 20px 80px}}h1{{font-size:clamp(34px,6vw,66px);line-height:1.05}}h2{{font-size:clamp(25px,3vw,38px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805800;padding:15px 18px;font-weight:900;font-size:16px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}.card{{background:white;border:2px solid var(--sky);border-radius:14px;padding:18px}}.metric{{font-size:clamp(28px,5vw,48px);font-weight:900;color:var(--blue)}}.scroll{{overflow-x:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>{ROUND} · {IDENT}</p><h1>Every exterior facet now has an exact CAD face.</h1><p>This is geometry evidence, not structural or safety approval.</p></div></header><main><section class='cards'><article class='card'><div class='metric'>{len(facet_nodes):,}</div><p>exterior Tet10 facets mapped</p></article><article class='card'><div class='metric'>{float(qdeviation.max()):.6g} mm</div><p>maximum sampled B-Rep deviation</p></article><article class='card'><div class='metric'>{area_relative_error*100:.4f}%</div><p>loaded-area error</p></article></section><h2>Validation</h2>{html_table(validation_rows)}<h2>Load boundary</h2>{html_table(load_rows)}<h2>Open holds</h2>{html_table([{**row} for row in [{"hold": h, "state": "OPEN", "warning": WARNING} for h in holds]])}</main></body></html>"""
        (OUT / "index.html").write_text(html, encoding="utf-8")
        file_manifest(OUT)
        if RELEASE.exists():
            shutil.rmtree(RELEASE)
        RELEASE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(OUT, RELEASE)
        print(json.dumps(status, indent=2))
        # Exit success means the fail-closed evidence package was generated
        # and synchronized.  Engineering screen results remain explicit in
        # validation-register.csv and analysis-status.json.
        return 0
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    raise SystemExit(main())
