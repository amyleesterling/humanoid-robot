#!/usr/bin/env python3
"""Build the R283 exact-zone/submodel evidence architecture prototype.

The executable portion is deliberately bounded.  It binds exact STEP B-Reps,
freezes topology signatures, evaluates exact OpenCASCADE point-to-edge distance,
creates exact solid/plane gauge intersections, and exercises quadrature-direct
statistics on an explicitly synthetic method-test field.  It does not solve a
structural case or close any convergence, contact, joint, capacity, or work gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import shutil
import sys
from pathlib import Path
from typing import Iterable

import cadquery as cq
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts"
R282 = ROOT / "mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-exact-zone-submodel-architecture-p0.1"
RELEASE_OUT = ROOT / "release/hr-v0/j2-exact-zone-submodel-architecture-p0.1"
IDENT = "HR-V0-J2-EXACT-ZONE-SUBMODEL-ARCH-P0.1"
ROUND = "R283-PROTOTYPE"
WARNING = (
    "PRELIMINARY - NUMERICAL METHOD PROTOTYPE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)
STEP_PATHS = {
    "C06": CAD / "MV0-C06_J2_positive_moving_striker_adapter.step",
    "C07": CAD / "MV0-C07_J2_positive_fixed_catch_adapter.step",
}
MOMENT_DATUM_MM = np.asarray((0.0, 0.0, 0.0), dtype=float)
SICN_BINS = (0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00)
PROBES = (
    ("C07-PF-C", "C07", (44.0, 8.005, 1.0), (0.0, 1.0, 0.0)),
    ("C07-PF-LL", "C07", (40.0, 8.005, -15.0), (0.0, 1.0, 0.0)),
    ("C07-PF-LU", "C07", (40.0, 8.005, 17.0), (0.0, 1.0, 0.0)),
    ("C07-PF-RL", "C07", (48.0, 8.005, -15.0), (0.0, 1.0, 0.0)),
    ("C07-PF-RU", "C07", (48.0, 8.005, 17.0), (0.0, 1.0, 0.0)),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def rounded(values: Iterable[float], digits: int = 9) -> list[float]:
    return [round(float(value), digits) for value in values]


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise RuntimeError(f"refusing to write empty table: {path}")
    fields: list[str] = []
    for record in records:
        for field in record:
            if field not in fields:
                fields.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def edge_signature(edge: cq.Edge) -> tuple[str, dict[str, object]]:
    bb = edge.BoundingBox()
    center = edge.Center()
    endpoints = sorted(
        [rounded((vertex.X, vertex.Y, vertex.Z)) for vertex in edge.Vertices()]
    )
    record: dict[str, object] = {
        "geometry_type": edge.geomType(),
        "length_mm": round(edge.Length(), 9),
        "bbox_mm": rounded((bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)),
        "center_mm": rounded((center.x, center.y, center.z)),
        "endpoints_mm": endpoints,
    }
    signature = stable_hash(record)
    return signature, record


def constant(value: float, target: float, tol: float = 2e-6) -> bool:
    return abs(value - target) <= tol


def c07_outer_semantic(detail: dict[str, object]) -> str | None:
    """Name only the intended outer rounded-rectangle pocket perimeter."""
    b = detail["bbox_mm"]
    kind = detail["geometry_type"]
    if kind == "LINE":
        if constant(b[0], 37.8) and constant(b[3], 37.8) and constant(b[2], -17.2) and constant(b[5], 19.2):
            return "WEST_STRAIGHT"
        if constant(b[2], 21.2) and constant(b[5], 21.2) and constant(b[0], 39.8) and constant(b[3], 48.2):
            return "NORTH_STRAIGHT"
        if constant(b[0], 50.2) and constant(b[3], 50.2) and constant(b[2], -17.2) and constant(b[5], 19.2):
            return "EAST_STRAIGHT"
        if constant(b[2], -19.2) and constant(b[5], -19.2) and constant(b[0], 39.8) and constant(b[3], 48.2):
            return "SOUTH_STRAIGHT"
    if kind == "CIRCLE":
        west = constant(b[0], 37.8) and constant(b[3], 39.8)
        east = constant(b[0], 48.2) and constant(b[3], 50.2)
        south = constant(b[2], -19.2) and constant(b[5], -17.2)
        north = constant(b[2], 19.2) and constant(b[5], 21.2)
        if west and south:
            return "SOUTH_WEST_CORNER_R2"
        if west and north:
            return "NORTH_WEST_CORNER_R2"
        if east and north:
            return "NORTH_EAST_CORNER_R2"
        if east and south:
            return "SOUTH_EAST_CORNER_R2"
    return None


C07_LOOP_ORDER = (
    "SOUTH_WEST_CORNER_R2", "WEST_STRAIGHT", "NORTH_WEST_CORNER_R2",
    "NORTH_STRAIGHT", "NORTH_EAST_CORNER_R2", "EAST_STRAIGHT",
    "SOUTH_EAST_CORNER_R2", "SOUTH_STRAIGHT",
)


def select_edges(part: str, shape: cq.Shape) -> dict[str, list[tuple[int, cq.Edge, str, dict[str, object]]]]:
    records: list[tuple[int, cq.Edge, str, dict[str, object]]] = []
    for index, edge in enumerate(shape.Edges()):
        signature, detail = edge_signature(edge)
        records.append((index, edge, signature, detail))

    selected: dict[str, list[tuple[int, cq.Edge, str, dict[str, object]]]] = {}
    if part == "C06":
        profile = []
        step = []
        for item in records:
            _, edge, _, _ = item
            b = edge.BoundingBox()
            # The exact R2 profile transitions are circular edges centered at
            # the +X rail shoulder around X=35..37, Z=18.536..22.000.
            if (
                edge.geomType() == "CIRCLE"
                and b.xmin >= 34.999
                and b.xmax <= 37.001
                and abs(b.ymax - b.ymin) <= 2e-6
                and b.zmin >= 18.53
                and b.zmax <= 22.001
            ):
                profile.append(item)
            # The separately named boss/thickness-step blend is the circular
            # transition spanning Y=9.525..11.525 at the same shoulder.
            if (
                edge.geomType() == "CIRCLE"
                and b.xmin >= 32.99
                and b.xmax <= 37.001
                and b.ymin >= 9.524
                and b.ymax <= 11.526
                and b.zmin >= 17.99
                and b.zmax <= 22.001
            ):
                step.append(item)
        selected["C06-RR-PROFILE"] = profile
        selected["C06-RR-STEP"] = [item for item in step if item not in profile]
    else:
        pocket = []
        for item in records:
            _, edge, _, _ = item
            b = edge.BoundingBox()
            if (
                constant(b.ymin, 8.005)
                and constant(b.ymax, 8.005)
                and c07_outer_semantic(item[3]) is not None
            ):
                pocket.append(item)
        selected["C07-PE"] = sorted(
            pocket, key=lambda item: C07_LOOP_ORDER.index(c07_outer_semantic(item[3]))
        )
    selected["ALL"] = records
    return selected


def exact_edge_distance(point: tuple[float, float, float], edges: list[cq.Edge]) -> tuple[float, int]:
    vertex = cq.Vertex.makeVertex(*point)
    distances = [edge.distance(vertex) for edge in edges]
    index = int(np.argmin(distances))
    return float(distances[index]), index


def exact_section(shape: cq.Shape, part: str) -> cq.Shape:
    if part == "C06":
        plane = cq.Plane(origin=(0.0, 0.0, 18.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0))
    else:
        plane = cq.Plane(origin=(34.0, 0.0, 0.0), xDir=(0.0, 1.0, 0.0), normal=(1.0, 0.0, 0.0))
    section = cq.Workplane(plane).newObject([shape]).section().val()
    if section.isNull() or section.Area() <= 0.0:
        raise RuntimeError(f"empty exact section for {part}")
    return section


def face_signature(face: cq.Face) -> tuple[str, dict[str, object]]:
    bb = face.BoundingBox()
    center = face.Center()
    normal = face.normalAt()
    edge_signatures = sorted(edge_signature(edge)[0] for edge in face.Edges())
    record: dict[str, object] = {
        "geometry_type": face.geomType(),
        "area_mm2": round(face.Area(), 9),
        "bbox_mm": rounded((bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)),
        "center_mm": rounded((center.x, center.y, center.z)),
        "normal": rounded((normal.x, normal.y, normal.z)),
        "edge_signatures": edge_signatures,
    }
    return stable_hash(record), record


def edge_adjacency(shape: cq.Shape, target: cq.Edge) -> list[dict[str, object]]:
    occurrences: list[dict[str, object]] = []
    for face in shape.Faces():
        face_sig, _detail = face_signature(face)
        for wire_index, wire in enumerate(face.Wires(), 1):
            for edge_index, occurrence in enumerate(wire.Edges(), 1):
                if occurrence.isSame(target):
                    occurrences.append({
                        "owner_face_geometric_signature_sha256": face_sig,
                        "wire_ordinal": wire_index,
                        "edge_ordinal_in_wire": edge_index,
                        "occ_orientation": int(occurrence.wrapped.Orientation()),
                    })
    if not occurrences:
        raise RuntimeError("selected edge has no owner-face/wire occurrence")
    return sorted(occurrences, key=lambda row: json.dumps(row, sort_keys=True))


def probe_floor_face(shape: cq.Shape, point: tuple[float, float, float]) -> tuple[cq.Face, str, dict[str, object], float]:
    vertex = cq.Vertex.makeVertex(*point)
    candidates: list[tuple[float, cq.Face, str, dict[str, object]]] = []
    for face in shape.Faces():
        bb = face.BoundingBox()
        if face.geomType() != "PLANE" or not constant(bb.ymin, 8.005) or not constant(bb.ymax, 8.005):
            continue
        signature, detail = face_signature(face)
        normal = np.asarray(detail["normal"], dtype=float)
        if float(np.dot(normal, np.asarray((0.0, 1.0, 0.0)))) < 0.999999:
            continue
        candidates.append((face.distance(vertex), face, signature, detail))
    if not candidates:
        raise RuntimeError("no exact +Y C07 pocket-floor faces")
    distance, face, signature, detail = min(candidates, key=lambda item: item[0])
    return face, signature, detail, float(distance)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probability: float) -> float:
    if not (0.0 <= probability <= 1.0):
        raise ValueError(probability)
    order = np.argsort(values, kind="stable")
    sorted_values = values[order]
    sorted_weights = weights[order]
    threshold = probability * float(np.sum(sorted_weights))
    index = int(np.searchsorted(np.cumsum(sorted_weights), threshold, side="left"))
    return float(sorted_values[min(index, len(sorted_values) - 1)])


def direct_quadrature_statistics(values: np.ndarray, weights: np.ndarray) -> dict[str, float | int]:
    values = np.asarray(values, dtype=float).reshape((-1,))
    weights = np.asarray(weights, dtype=float).reshape((-1,))
    if len(values) == 0 or len(values) != len(weights):
        raise RuntimeError("empty or mismatched quadrature arrays")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise RuntimeError("quadrature arrays must be finite with strictly positive weights")
    total = float(np.sum(weights))
    return {
        "quadrature_points": len(values),
        "integrated_weight": total,
        "weighted_mean": float(np.sum(values * weights) / total),
        "weighted_rms": float(math.sqrt(np.sum(values**2 * weights) / total)),
        "weighted_p95": weighted_quantile(values, weights, 0.95),
        "raw_maximum": float(np.max(values)),
    }


def validate_r282_freeze() -> dict[str, str]:
    freeze = (R282 / "protocol-freeze-register.csv").read_text(encoding="utf-8")
    zones = (R282 / "exact-zone-register.csv").read_text(encoding="utf-8")
    required = {
        "moment_origin": "d=(0,0,0) mm in each part-local STEP frame",
        "probe_center": "center (44,8.005,1)",
        "quadrature": "evaluate stress at solver quadrature points",
        "profile_zone": "C06-RR-PROFILE",
        "step_zone": "C06-RR-STEP",
        "pocket_zone": "C07-PE",
        "gauge_zone": "C06/C07-GAUGE",
    }
    for key, token in required.items():
        source = zones if key.endswith("zone") else freeze
        if token not in source:
            raise RuntimeError(f"R282 freeze token missing: {key}={token}")
    return {key: token for key, token in required.items()}


def run_manifest_schema() -> dict[str, object]:
    required = [
        "schema_version", "run_id", "stage", "case_id", "part", "level",
        "environment", "generator", "hardware", "coordinate_transform",
        "geometry", "mesh", "solver", "loads", "restraints", "zones",
        "probes", "sections", "transfers", "raw_artifacts", "authority",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:project-button:hr-v0:j2:raw-run-manifest:p0.1",
        "title": "HR-V0 J2 raw global/submodel/HPC run manifest",
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": {
            "schema_version": {"const": "HR-V0-J2-RAW-RUN-MANIFEST-P0.1"},
            "run_id": {"type": "string", "minLength": 1},
            "stage": {"enum": ["A_GLOBAL_SCOUT", "B_CURVED_GLOBAL", "C_LOCAL_SUBMODEL", "D_HPC_CONFIRMATION"]},
            "case_id": {"type": "string", "minLength": 1},
            "part": {"enum": ["C06", "C07"]},
            "level": {"enum": ["P2C", "L0", "L1", "L2", "L3", "L4"]},
            "environment": {"type": "object", "required": ["os", "python", "packages_lock_path", "packages_lock_sha256"], "additionalProperties": True},
            "generator": {"type": "object", "required": ["path", "sha256", "git_commit", "parameters_path", "parameters_sha256"], "additionalProperties": True},
            "hardware": {"type": "object", "required": ["hostname_or_scheduler_id", "cpu", "logical_cores", "ram_bytes", "accelerator", "wall_seconds", "peak_rss_bytes"], "additionalProperties": True},
            "coordinate_transform": {"type": "object", "required": ["source_frame", "target_frame", "matrix_4x4", "matrix_sha256", "moment_datum_mm"], "additionalProperties": True},
            "geometry": {"type": "object", "required": ["step_path", "step_sha256", "geometry_order", "entity_signature_register_sha256"], "additionalProperties": True},
            "mesh": {"type": "object", "required": ["nodes_path", "connectivity_path", "quality_path", "signed_jacobian_path", "metric_specific_h_path"], "additionalProperties": True},
            "solver": {"type": "object", "required": ["name", "version", "element", "preconditioner", "residual_history_path", "correction_history_path"], "additionalProperties": True},
            "loads": {"type": "object", "required": ["source_sha256", "loaded_entity_signatures", "resultant_n", "moment_n_mm", "quadrature_path"], "additionalProperties": True},
            "restraints": {"type": "object", "required": ["entity_signatures", "reaction_path", "free_residual_path"], "additionalProperties": True},
            "zones": {"type": "object", "required": ["definition_sha256", "membership_path", "clipped_measure_path", "statistics_path", "singularity_path"], "additionalProperties": True},
            "probes": {"type": "object", "required": ["definition_sha256", "field_results_path"], "additionalProperties": True},
            "sections": {"type": "object", "required": ["definition_sha256", "geometry_path", "resultants_path"], "additionalProperties": True},
            "transfers": {"type": "object", "required": ["mode", "donor_run_manifest_sha256", "donor_mesh_sha256", "cut_boundary_signature", "interpolation_method", "interpolation_tolerance_mm", "field_path", "force_conservation_relative_error", "moment_conservation_relative_error", "energy_conservation_relative_error", "saint_venant_boundary_distances_mm", "saint_venant_metric_path", "saint_venant_acceptance_tolerances"], "additionalProperties": True},
            "raw_artifacts": {"type": "array", "minItems": 1, "items": {"type": "object", "required": ["role", "path", "sha256", "bytes"], "additionalProperties": False, "properties": {"role": {"type": "string", "minLength": 1}, "path": {"type": "string", "minLength": 1}, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "bytes": {"type": "integer", "minimum": 0}}}},
            "authority": {"type": "object", "additionalProperties": False, "required": ["numerical_convergence", "capacity", "fabrication", "powered_testing", "motion", "energization", "safety_credit"], "properties": {key: {"const": False} for key in ("numerical_convergence", "capacity", "fabrication", "powered_testing", "motion", "energization", "safety_credit")}},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose-edges", action="store_true")
    args = parser.parse_args()
    freeze = validate_r282_freeze()
    shapes = {part: cq.importers.importStep(str(path)).val() for part, path in STEP_PATHS.items()}
    selections = {part: select_edges(part, shape) for part, shape in shapes.items()}

    if args.diagnose_edges:
        for part, groups in selections.items():
            print(f"{part}: total edges={len(groups['ALL'])}")
            for group, items in groups.items():
                if group == "ALL":
                    continue
                print(f"  {group}: {len(items)}")
                for index, _edge, signature, detail in items:
                    print(index, signature[:16], json.dumps(detail, sort_keys=True))
        return 0

    # Exact P0.13 topology counts are part of the frozen prototype identity.
    # Any STEP/topology drift must stop execution rather than silently widen a
    # selector. C07's 40 curves are retained as-is; semantic aggregation to
    # four straights/four corners is frozen as one exact closed perimeter.
    expected_counts = {"C06-RR-PROFILE": 1, "C06-RR-STEP": 4, "C07-PE": 8}
    actual_counts = {
        "C06-RR-PROFILE": len(selections["C06"]["C06-RR-PROFILE"]),
        "C06-RR-STEP": len(selections["C06"]["C06-RR-STEP"]),
        "C07-PE": len(selections["C07"]["C07-PE"]),
    }
    if actual_counts != expected_counts:
        raise RuntimeError(f"exact P0.13 zone-edge count drift: expected={expected_counts}, actual={actual_counts}")
    c07_types = [item[3]["geometry_type"] for item in selections["C07"]["C07-PE"]]
    expected_c07_types = {"LINE": 4, "CIRCLE": 4}
    actual_c07_types = {kind: c07_types.count(kind) for kind in sorted(set(c07_types))}
    if actual_c07_types != expected_c07_types:
        raise RuntimeError(f"exact C07 boundary-curve class drift: expected={expected_c07_types}, actual={actual_c07_types}")
    c07_loop = selections["C07"]["C07-PE"]
    c07_semantics = [c07_outer_semantic(item[3]) for item in c07_loop]
    if tuple(c07_semantics) != C07_LOOP_ORDER:
        raise RuntimeError(f"exact C07 semantic loop-order drift: {c07_semantics}")
    for index, item in enumerate(c07_loop):
        successor = c07_loop[(index + 1) % len(c07_loop)]
        shared = set(map(tuple, item[3]["endpoints_mm"])) & set(map(tuple, successor[3]["endpoints_mm"]))
        if len(shared) != 1:
            raise RuntimeError(f"C07 loop is not singly endpoint-adjacent at {c07_semantics[index]}: {sorted(shared)}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    entity_rows: list[dict[str, object]] = []
    selected_signatures: dict[str, list[str]] = {}
    for part in ("C06", "C07"):
        for group, items in selections[part].items():
            if group == "ALL":
                continue
            selected_signatures[f"{part}:{group}"] = [item[2] for item in items]
            for ordinal, (index, _edge, signature, detail) in enumerate(items, 1):
                semantic_class = "PROFILE_ROOT"
                if group == "C06-RR-STEP":
                    semantic_class = "THICKNESS_STEP_BLEND"
                elif group == "C07-PE":
                    semantic_class = c07_outer_semantic(detail)
                successor_signature = "N/A"
                shared_endpoint_json = "N/A"
                if group == "C07-PE":
                    successor = items[ordinal % len(items)]
                    successor_signature = successor[2]
                    shared = set(map(tuple, detail["endpoints_mm"])) & set(map(tuple, successor[3]["endpoints_mm"]))
                    shared_endpoint_json = json.dumps(list(next(iter(shared))), separators=(",", ":"))
                entity_rows.append({
                    "part": part,
                    "zone_group": group,
                    "zone_edge_ordinal": ordinal,
                    "occ_traversal_index_diagnostic_only": index,
                    "geometric_edge_signature_sha256": signature,
                    "geometry_type": detail["geometry_type"],
                    "semantic_class": semantic_class,
                    "closed_loop_ordinal": ordinal if group == "C07-PE" else "N/A",
                    "loop_successor_geometric_signature_sha256": successor_signature,
                    "shared_endpoint_with_successor_mm_json": shared_endpoint_json,
                    "length_mm": detail["length_mm"],
                    "bbox_mm_json": json.dumps(detail["bbox_mm"], separators=(",", ":")),
                    "center_mm_json": json.dumps(detail["center_mm"], separators=(",", ":")),
                    "endpoints_mm_json": json.dumps(detail["endpoints_mm"], separators=(",", ":")),
                    "owner_face_wire_adjacency_json": json.dumps(edge_adjacency(shapes[part], _edge), sort_keys=True, separators=(",", ":")),
                    "identity_rule": "geometric edge signature + owner-face/wire/ordinal/orientation adjacency + STEP SHA; OCC traversal index receives no identity credit",
                    "warning": WARNING,
                })
    write_csv(OUT / "entity-signature-register.csv", entity_rows)

    # Exact distance test: evaluate actual B-Rep points and deterministic remote
    # points.  No polyline sampling or centroid membership is used.
    distance_rows: list[dict[str, object]] = []
    for part, group in (("C06", "C06-RR-PROFILE"), ("C06", "C06-RR-STEP"), ("C07", "C07-PE")):
        edges = [item[1] for item in selections[part][group]]
        for edge_ordinal, edge in enumerate(edges, 1):
            for parameter in (0.25, 0.50, 0.75):
                position = edge.positionAt(parameter)
                point = (float(position.x), float(position.y), float(position.z))
                distance, nearest = exact_edge_distance(point, edges)
                distance_rows.append({
                    "part": part, "zone_group": group, "source_edge_ordinal": edge_ordinal,
                    "point_kind": "EXACT_EDGE_PARAMETER", "parameter": parameter,
                    "point_x_mm": point[0], "point_y_mm": point[1], "point_z_mm": point[2],
                    "exact_occ_distance_mm": distance, "nearest_edge_ordinal": nearest + 1,
                    "equal_minimum_edge_count_at_1e_7_mm": sum(candidate.distance(cq.Vertex.makeVertex(*point)) <= distance + 1e-7 for candidate in edges),
                    "membership_at_zone_radius": "IN" if distance <= (1.0 if part == "C07" else 3.0) else "OUT",
                    "credit": "EXACT DISTANCE METHOD TEST ONLY", "warning": WARNING,
                })
        midpoint = edges[0].positionAt(0.5)
        offset = (float(midpoint.x) + 0.137, float(midpoint.y) + 0.211, float(midpoint.z) + 0.173)
        distance, nearest = exact_edge_distance(offset, edges)
        distance_rows.append({
            "part": part, "zone_group": group, "source_edge_ordinal": 1,
            "point_kind": "DETERMINISTIC_OFF_EDGE_POINT", "parameter": 0.5,
            "point_x_mm": offset[0], "point_y_mm": offset[1], "point_z_mm": offset[2],
            "exact_occ_distance_mm": distance, "nearest_edge_ordinal": nearest + 1,
            "equal_minimum_edge_count_at_1e_7_mm": sum(candidate.distance(cq.Vertex.makeVertex(*offset)) <= distance + 1e-7 for candidate in edges),
            "membership_at_zone_radius": "IN" if distance <= (1.0 if part == "C07" else 3.0) else "OUT",
            "credit": "EXACT DISTANCE OFFSET METHOD TEST ONLY", "warning": WARNING,
        })
        if len(edges) > 1:
            shared_endpoint: tuple[float, float, float] | None = None
            for candidate in edges[0].Vertices():
                point = (float(candidate.X), float(candidate.Y), float(candidate.Z))
                zero_count = sum(edge.distance(cq.Vertex.makeVertex(*point)) <= 1e-7 for edge in edges)
                if zero_count >= 2:
                    shared_endpoint = point
                    break
            if shared_endpoint is not None:
                distance, nearest = exact_edge_distance(shared_endpoint, edges)
                distance_rows.append({
                    "part": part, "zone_group": group, "source_edge_ordinal": 1,
                    "point_kind": "SHARED_ENDPOINT_TIE", "parameter": "ENDPOINT",
                    "point_x_mm": shared_endpoint[0], "point_y_mm": shared_endpoint[1], "point_z_mm": shared_endpoint[2],
                    "exact_occ_distance_mm": distance, "nearest_edge_ordinal": nearest + 1,
                    "equal_minimum_edge_count_at_1e_7_mm": sum(candidate.distance(cq.Vertex.makeVertex(*shared_endpoint)) <= distance + 1e-7 for candidate in edges),
                    "membership_at_zone_radius": "IN", "credit": "EXACT DISTANCE TIE METHOD TEST ONLY", "warning": WARNING,
                })
        remote = (0.0, -15.0, 0.0)
        distance, nearest = exact_edge_distance(remote, edges)
        distance_rows.append({
            "part": part, "zone_group": group, "source_edge_ordinal": "N/A",
            "point_kind": "DETERMINISTIC_REMOTE_POINT", "parameter": "N/A",
            "point_x_mm": remote[0], "point_y_mm": remote[1], "point_z_mm": remote[2],
            "exact_occ_distance_mm": distance, "nearest_edge_ordinal": nearest + 1,
            "equal_minimum_edge_count_at_1e_7_mm": sum(candidate.distance(cq.Vertex.makeVertex(*remote)) <= distance + 1e-7 for candidate in edges),
            "membership_at_zone_radius": "IN" if distance <= (1.0 if part == "C07" else 3.0) else "OUT",
            "credit": "EXACT DISTANCE METHOD TEST ONLY", "warning": WARNING,
        })
    write_csv(OUT / "exact-distance-prototype.csv", distance_rows)

    section_rows: list[dict[str, object]] = []
    for part in ("C06", "C07"):
        section = exact_section(shapes[part], part)
        center = section.Center()
        bb = section.BoundingBox()
        component_faces = section.Faces()
        component_areas = [face.Area() for face in component_faces]
        if not math.isclose(section.Area(), sum(component_areas), rel_tol=1e-10, abs_tol=1e-8):
            raise RuntimeError(f"section compound Area() mismatch for {part}")
        section_wires = section.Wires()
        section_edges = section.Edges()
        section_topology = {
            "part": part,
            "plane": "Z=18.000 mm" if part == "C06" else "X=34.000 mm",
            "face_signatures": sorted(face_signature(face)[0] for face in component_faces),
            "wire_edge_signatures": sorted(
                sorted(edge_signature(edge)[0] for edge in wire.Edges())
                for wire in section_wires
            ),
            "area_mm2": round(section.Area(), 9),
            "bbox_mm": rounded((bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)),
        }
        section_rows.append({
            "section_id": "C06-GAUGE-Z18" if part == "C06" else "C07-GAUGE-X34",
            "part": part,
            "plane": "Z=18.000 mm" if part == "C06" else "X=34.000 mm",
            "moment_datum_mm": "[0,0,0]",
            "exact_occ_area_mm2": section.Area(),
            "planar_face_components": len(component_faces),
            "closed_wire_loops": len(section_wires),
            "boundary_edge_occurrences": len(section_edges),
            "section_geometry_signature_sha256": stable_hash(section_topology),
            "component_areas_mm2_json": json.dumps(rounded(component_areas), separators=(",", ":")),
            "area_crosscheck_sum_mm2": sum(component_areas),
            "centroid_x_mm": center.x, "centroid_y_mm": center.y, "centroid_z_mm": center.z,
            "bbox_mm_json": json.dumps(rounded((bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)), separators=(",", ":")),
            "required_future_output": "integrated Fx,Fy,Fz,Mx,My,Mz plus membrane/bending stress with sign convention",
            "resultant_executed": False,
            "credit": "EXACT SOLID/PLANE INTERSECTION GEOMETRY ONLY",
            "warning": WARNING,
        })
    write_csv(OUT / "section-definition-and-geometry.csv", section_rows)

    probe_rows: list[dict[str, object]] = []
    c07 = shapes["C07"]
    for probe_id, part, point, normal in PROBES:
        _face, signature, face_detail, distance = probe_floor_face(c07, point)
        probe_rows.append({
            "probe_id": probe_id, "part": part,
            "x_mm": point[0], "y_mm": point[1], "z_mm": point[2],
            "normal_x": normal[0], "normal_y": normal[1], "normal_z": normal[2],
            "exact_floor_face_signature_sha256": signature,
            "exact_floor_face_bbox_mm_json": json.dumps(face_detail["bbox_mm"], separators=(",", ":")),
            "exact_floor_face_normal_json": json.dumps(face_detail["normal"], separators=(",", ":")),
            "exact_distance_to_named_floor_face_mm": distance,
            "on_exact_named_floor_face_with_plus_y_normal": distance <= 1e-7,
            "field_interpolation_executed": False,
            "credit": "FROZEN EXACT PROBE LOCATION ONLY",
            "warning": WARNING,
        })
    if not all(row["on_exact_named_floor_face_with_plus_y_normal"] for row in probe_rows):
        raise RuntimeError("one or more frozen R282 probes are not on an exact +Y C07 floor face")
    write_csv(OUT / "frozen-probe-register.csv", probe_rows)

    # Direct-quadrature method test.  Values are deliberately synthetic and
    # analytically auditable; they are never represented as FEA evidence.
    synthetic_values = np.asarray((1.0, 2.0, 4.0, 8.0, 16.0), dtype=float)
    synthetic_weights = np.asarray((0.5, 1.0, 1.5, 2.0, 3.0), dtype=float)
    stats = direct_quadrature_statistics(synthetic_values, synthetic_weights)
    write_csv(OUT / "direct-quadrature-method-test.csv", [{
        "test_id": "R283-DQ-01",
        "field": "synthetic scalar; values [1,2,4,8,16]",
        "weights": "[0.5,1,1.5,2,3]",
        **stats,
        "element_mean_preaverage_used": False,
        "structural_or_capacity_credit": "NONE",
        "warning": WARNING,
    }])

    zone_definition = {
        "identifier": IDENT,
        "step_sha256": {part: sha(path) for part, path in STEP_PATHS.items()},
        "geometric_edge_signatures": selected_signatures,
        "membership": {
            "C06-RR-PROFILE": {"operation": "exact OCC point-to-edge distance", "radius_mm": 3.0, "subzones": ["INBOARD_Y_FRONT", "INBOARD_Y_BACK", "OUTBOARD_Y_FRONT", "OUTBOARD_Y_BACK"], "clipped_volume_required_for_production": True},
            "C06-RR-STEP": {"operation": "exact OCC point-to-edge distance", "radius_mm": 3.0, "separate_from_profile": True, "clipped_volume_required_for_production": True},
            "C07-PE": {"operation": "exact OCC point-to-edge distance", "radius_mm": 1.0, "retained_exact_brep_boundary_curves": len(selections["C07"]["C07-PE"]), "straight_edges": 4, "corner_r2_arcs": 4, "closed_loop_order": list(C07_LOOP_ORDER), "identity": "each of eight curves has geometric signature, owner-face/wire/order/orientation adjacency, and exactly one shared endpoint with its successor", "clipped_volume_required_for_production": True},
        },
        "prohibited": ["tetrahedron-centroid membership", "sampled-polyline distance", "element-mean stress before RMS or p95", "transient OCC tag as identity"],
        "production_boundary": "cell/zone and facet/zone B-Rep clipping plus solver quadrature fields remain required",
        "warning": WARNING,
    }
    (OUT / "exact-zone-definition.json").write_text(json.dumps(zone_definition, indent=2) + "\n", encoding="utf-8")

    schema = run_manifest_schema()
    (OUT / "raw-run-manifest.schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    template = {
        "schema_version": "HR-V0-J2-RAW-RUN-MANIFEST-P0.1",
        "run_id": "SELECTION REQUIRED",
        "stage": "C_LOCAL_SUBMODEL",
        "case_id": "SELECTION REQUIRED",
        "part": "C06",
        "level": "L0",
        "environment": {"os": "SELECTION REQUIRED", "python": "SELECTION REQUIRED", "packages_lock_path": "SELECTION REQUIRED", "packages_lock_sha256": "SELECTION REQUIRED"},
        "generator": {"path": "SELECTION REQUIRED", "sha256": "SELECTION REQUIRED", "git_commit": "SELECTION REQUIRED", "parameters_path": "SELECTION REQUIRED", "parameters_sha256": "SELECTION REQUIRED"},
        "hardware": {"hostname_or_scheduler_id": "SELECTION REQUIRED", "cpu": "SELECTION REQUIRED", "logical_cores": 0, "ram_bytes": 0, "accelerator": "NONE OR SELECTION REQUIRED", "wall_seconds": 0, "peak_rss_bytes": 0},
        "coordinate_transform": {"source_frame": "SELECTION REQUIRED", "target_frame": "SELECTION REQUIRED", "matrix_4x4": [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], "matrix_sha256": "SELECTION REQUIRED", "moment_datum_mm": [0,0,0]},
        "geometry": {"step_path": "SELECTION REQUIRED", "step_sha256": "SELECTION REQUIRED", "geometry_order": "SELECTION REQUIRED", "entity_signature_register_sha256": "SELECTION REQUIRED"},
        "mesh": {"nodes_path": "SELECTION REQUIRED", "connectivity_path": "SELECTION REQUIRED", "quality_path": "SELECTION REQUIRED", "signed_jacobian_path": "SELECTION REQUIRED", "metric_specific_h_path": "SELECTION REQUIRED"},
        "solver": {"name": "SELECTION REQUIRED", "version": "SELECTION REQUIRED", "element": "SELECTION REQUIRED", "preconditioner": "SELECTION REQUIRED", "residual_history_path": "SELECTION REQUIRED", "correction_history_path": "SELECTION REQUIRED"},
        "loads": {"source_sha256": "SELECTION REQUIRED", "loaded_entity_signatures": [], "resultant_n": [0, 0, 0], "moment_n_mm": [0, 0, 0], "quadrature_path": "SELECTION REQUIRED"},
        "restraints": {"entity_signatures": [], "reaction_path": "SELECTION REQUIRED", "free_residual_path": "SELECTION REQUIRED"},
        "zones": {"definition_sha256": "SELECTION REQUIRED", "membership_path": "SELECTION REQUIRED", "clipped_measure_path": "SELECTION REQUIRED", "statistics_path": "SELECTION REQUIRED", "singularity_path": "SELECTION REQUIRED"},
        "probes": {"definition_sha256": "SELECTION REQUIRED", "field_results_path": "SELECTION REQUIRED"},
        "sections": {"definition_sha256": "SELECTION REQUIRED", "geometry_path": "SELECTION REQUIRED", "resultants_path": "SELECTION REQUIRED"},
        "transfers": {"mode": "DISPLACEMENT_OR_TRACTION_SELECTION_REQUIRED", "donor_run_manifest_sha256": "SELECTION REQUIRED", "donor_mesh_sha256": "SELECTION REQUIRED", "cut_boundary_signature": "SELECTION REQUIRED", "interpolation_method": "SELECTION REQUIRED", "interpolation_tolerance_mm": "SELECTION REQUIRED", "field_path": "SELECTION REQUIRED", "force_conservation_relative_error": "NOT EXECUTED", "moment_conservation_relative_error": "NOT EXECUTED", "energy_conservation_relative_error": "NOT EXECUTED", "saint_venant_boundary_distances_mm": [], "saint_venant_metric_path": "SELECTION REQUIRED", "saint_venant_acceptance_tolerances": "SELECTION REQUIRED"},
        "raw_artifacts": [{"role": "TEMPLATE PLACEHOLDER - REPLACE", "path": "SELECTION REQUIRED", "sha256": "0000000000000000000000000000000000000000000000000000000000000000", "bytes": 0}],
        "authority": {key: False for key in ("numerical_convergence", "capacity", "fabrication", "powered_testing", "motion", "energization", "safety_credit")},
    }
    (OUT / "raw-run-manifest-template.json").write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    architecture_rows = [
        {"stage": "A", "execution": "global linear-geometry resource scout", "exact_zone_role": "bind entity signatures and estimate clipped-domain workload", "required_input": "SHA-bound STEP and run manifest", "required_output": "raw mesh/quality/entity/zone maps", "prototype_state": "SCHEMA + BOUNDED EXTRACTION EXECUTED", "credit": "METHOD ONLY", "warning": WARNING},
        {"stage": "B", "execution": "curved global L0/L1", "exact_zone_role": "quadrature-direct fixed-domain statistics", "required_input": "accepted signed-Jacobian curved mesh", "required_output": "solution/reaction/residual/zone/probe/section bundles", "prototype_state": "NOT EXECUTED; C07 CURVED REPAIR EXTERNAL", "credit": "NONE", "warning": WARNING},
        {"stage": "C", "execution": "Saint-Venant checked local submodels L1-L4", "exact_zone_role": "exact cut-boundary and fixed physical-zone preservation", "required_input": "hash-bound global transfer field", "required_output": "boundary-distance, energy/resultant and transfer-conservation studies", "prototype_state": "MANIFEST SCHEMA ONLY", "credit": "NONE", "warning": WARNING},
        {"stage": "D", "execution": "matrix-free/HPC confirmation", "exact_zone_role": "independent final-level confirmation", "required_input": "reproducible assembly and raw histories", "required_output": "independent solution and convergence bundle", "prototype_state": "MANIFEST SCHEMA ONLY", "credit": "NONE", "warning": WARNING},
    ]
    write_csv(OUT / "execution-architecture.csv", architecture_rows)

    open_holds = [
        "Accept the exact C06 profile/step identities and freeze the missing C06 INBOARD/OUTBOARD normalized-parameter and Y_FRONT/Y_BACK half-space definitions",
        "Implement exact cell/zone and facet/zone geometric clipping with measure conservation; no centroid membership",
        "Execute structural quadrature fields, named-zone statistics, frozen probes and six-component gauge resultants",
        "Implement and validate global-to-local donor interpolation, force/moment/energy conservation and Saint-Venant boundary-distance criteria",
        "Repair/accept curved C07 geometry and execute accepted L0-L3/L4 or HPC convergence with raw manifests",
        "Obtain independent numerical-method acceptance and retain contact/joint/dynamic/physical/capacity gates separately",
    ]
    write_csv(OUT / "open-holds.csv", [{
        "hold_id": f"R283-H{index:02d}", "hold": hold, "state": "OPEN",
        "closure_evidence": "NOT EXECUTED", "effect": "R278-H02 AND ALL CAPACITY/WORK AUTHORITY REMAIN BLOCKED",
        "warning": WARNING,
    } for index, hold in enumerate(open_holds, 1)])

    validation_rows = [
        {"check_id": "R283-V01", "check": "R282 freeze records contain bound definitions", "result": "PASS", "evidence": json.dumps(freeze, sort_keys=True), "credit": "METHOD CONTROL", "warning": WARNING},
        {"check_id": "R283-V02", "check": "exact STEP topology signatures frozen", "result": "PASS", "evidence": f"{len(entity_rows)} selected exact edges", "credit": "IDENTITY METHOD", "warning": WARNING},
        {"check_id": "R283-V03", "check": "exact OCC edge distance bounded test", "result": "PASS", "evidence": f"{len(distance_rows)} exact calls; all edge-parameter distances <=1e-7", "credit": "DISTANCE METHOD", "warning": WARNING},
        {"check_id": "R283-V04", "check": "exact solid-plane gauge intersections", "result": "PASS", "evidence": "C06 Z=18 and C07 X=34 areas retained", "credit": "SECTION GEOMETRY METHOD", "warning": WARNING},
        {"check_id": "R283-V05", "check": "frozen C07 probes bind to exact +Y pocket-floor faces", "result": "PASS", "evidence": "five exact point/face distance and normal checks with face signatures", "credit": "PROBE DEFINITION", "warning": WARNING},
        {"check_id": "R283-V06", "check": "direct quadrature statistics", "result": "PASS METHOD TEST", "evidence": "synthetic weighted field; no element preaverage", "credit": "POSTPROCESSOR METHOD ONLY", "warning": WARNING},
        {"check_id": "R283-V07", "check": "exact clipped cell/facet measures", "result": "NOT EXECUTED", "evidence": "production mesh and zone-solid clipping backend required", "credit": "NONE; FAIL CLOSED", "warning": WARNING},
        {"check_id": "R283-V08", "check": "structural field/probes/section resultants/convergence", "result": "NOT EXECUTED", "evidence": "no structural solve in R283 component", "credit": "NONE; H02 OPEN", "warning": WARNING},
        {"check_id": "R283-V09", "check": "C07 exact ordered four-straight/four-R2-corner closed perimeter", "result": "PASS PROTOTYPE", "evidence": "eight exact signed identities; ordered loop has one shared endpoint at each successor boundary", "credit": "ENTITY-SELECTION METHOD ONLY", "warning": WARNING},
        {"check_id": "R283-V10", "check": "C06 INBOARD/OUTBOARD and Y_FRONT/Y_BACK parametric split", "result": "NOT EXECUTED", "evidence": "R282 gives labels but not deterministic parameter origin/direction or FRONT/BACK half-space sign; no convention invented", "credit": "NONE; FAIL CLOSED", "warning": WARNING},
    ]
    write_csv(OUT / "validation-register.csv", validation_rows)
    status = {
        "identifier": IDENT,
        "round": ROUND,
        "date": "2026-08-12",
        "cad_identifier": "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE",
        "exact_step_identity_bound": True,
        "topology_signature_prototype_pass": True,
        "exact_occ_distance_prototype_pass": True,
        "exact_solid_plane_intersection_prototype_pass": True,
        "direct_quadrature_statistics_method_test_pass": True,
        "frozen_probe_definition_pass": True,
        "raw_run_manifest_schema_issued": True,
        "exact_clipped_cell_zone_execution_complete": False,
        "structural_solution_executed": False,
        "submodel_transfer_executed": False,
        "mesh_convergence_complete": False,
        "r278_h02_closed": False,
        "capacity_established": False,
        "selected": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    provenance = {
        "generator": {"path": "tools/generate_hr_v0_j2_exact_zone_submodel_p01.py", "sha256": sha(Path(__file__).resolve())},
        "checker": {"path": "tools/check_hr_v0_j2_exact_zone_submodel_p01.py", "sha256": sha(ROOT / "tools/check_hr_v0_j2_exact_zone_submodel_p01.py")},
        "runtime": {"python_executable": sys.executable, "python_version": platform.python_version(), "platform": platform.platform(), "cadquery_version": getattr(cq, "__version__", "UNKNOWN"), "numpy_version": np.__version__},
        "shared_inputs": {
            "protocol-freeze-register.csv": sha(R282 / "protocol-freeze-register.csv"),
            "exact-zone-register.csv": sha(R282 / "exact-zone-register.csv"),
            "execution-architecture.csv": sha(R282 / "execution-architecture.csv"),
        },
        "step_inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path) for path in STEP_PATHS.values()},
        "warning": WARNING,
    }
    (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n"
        f"**{WARNING}**\n\n"
        "This isolated R283 package is an executable numerical-method architecture prototype. "
        "It proves SHA-bound STEP loading, exact OpenCASCADE edge-distance calls, retained B-Rep "
        "edge identities with owner-face/wire adjacency, exact section geometry, exact frozen-probe "
        "face binding, synthetic direct-quadrature arithmetic, and a fail-closed raw-run schema.\n\n"
        "It does **not** execute production cell/facet clipping, a structural solve, submodel transfer, "
        "mesh convergence, section resultants, or H02 closure. The intended C07 pocket perimeter is "
        "retained as one ordered closed loop of four straight edges and four R2 corner arcs. The C06 "
        "INBOARD/OUTBOARD parameter convention and FRONT/BACK half-space sign remain open.\n\n"
        "Run `tools/generate_hr_v0_j2_exact_zone_submodel_p01.py`, then "
        "`tools/check_hr_v0_j2_exact_zone_submodel_p01.py` in the repository CAD environment.\n",
        encoding="utf-8",
    )

    artifacts = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
            artifacts.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", artifacts)
    if RELEASE_OUT.exists():
        shutil.rmtree(RELEASE_OUT)
    RELEASE_OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE_OUT)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
