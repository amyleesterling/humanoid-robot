#!/usr/bin/env python3
"""Localize every residual R303 curved-Jacobian failure without remeshing."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import shutil
from pathlib import Path

import gmsh
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R303 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1"
R297 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1"
BREP = R297 / "c07-pe-seam-free-analysis-partition.brep"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-failure-localization-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-rail-jacobian-failure-localization-p0.1"
IDENT = "HR-V0-J2-C07-PE-RAIL-JACOBIAN-FAILURE-LOCALIZATION-P0.1"
WARNING = "PRELIMINARY - RAIL-JACOBIAN SUCCESSOR FAILURE LOCALIZATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()


def write_csv(path: Path, data: list[dict[str, object]]) -> None:
    if not data:
        raise RuntimeError(f"empty evidence {path}")
    fields: list[str] = []
    for row in data:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def face_record(tag: int) -> dict[str, object]:
    record = {
        "geometry_type": gmsh.model.getType(2, tag),
        "bbox_mm": [round(float(value), 9) for value in gmsh.model.getBoundingBox(2, tag)],
        "area_mm2": round(float(gmsh.model.occ.getMass(2, tag)), 9),
        "center_mm": [round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(2, tag)],
    }
    record["signature_sha256"] = stable(record)
    return record


def nearest(point: np.ndarray, faces: list[int]) -> dict[str, object]:
    best: tuple[float, int, np.ndarray] | None = None
    for tag in faces:
        closest, _parameters = gmsh.model.getClosestPoint(2, tag, point.tolist())
        xyz = np.asarray(closest[:3])
        distance = float(np.linalg.norm(xyz - point))
        if best is None or distance < best[0]:
            best = (distance, tag, xyz)
    assert best is not None
    distance, tag, xyz = best
    record = face_record(tag)
    return {
        "nearest_exact_face_tag_diagnostic_only": tag,
        "nearest_exact_face_signature_sha256": record["signature_sha256"],
        "nearest_exact_face_type": record["geometry_type"],
        "nearest_exact_face_bbox_mm_json": json.dumps(record["bbox_mm"], separators=(",", ":")),
        "nearest_exact_face_area_mm2": record["area_mm2"],
        "nearest_exact_face_center_mm_json": json.dumps(record["center_mm"], separators=(",", ":")),
        "nearest_exact_face_distance_mm": distance,
        "nearest_exact_point_mm_json": json.dumps([float(value) for value in xyz], separators=(",", ":")),
    }


def main() -> int:
    status = json.loads((R303 / "analysis-status.json").read_text(encoding="utf-8"))
    if (
        not status["global_sicn_gate"]
        or not status["monitored_zone_minimum_gate"]
        or status["actual_quadrature_signed_jacobian_gate"]
        or status["sampled_mesh_quality_candidate_pass"]
    ):
        raise RuntimeError("R303 failure boundary drift")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    working = OUT / "_working.msh"
    digest = hashlib.sha256()
    with gzip.open(R303 / "c07-conformal-zone-mesh.msh.gz", "rb") as source, working.open("wb") as target:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            target.write(block)
            digest.update(block)
    if digest.hexdigest() != status["mesh_uncompressed_sha256"]:
        raise RuntimeError("mesh identity")

    failures: list[dict[str, object]] = []
    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.open(str(working))
        tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
        matrix: int | None = None
        for dimension, physical_tag in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(dimension, physical_tag) == "C07-MATRIX":
                matrix = int(gmsh.model.getEntitiesForPhysicalGroup(dimension, physical_tag)[0])
        if matrix is None:
            raise RuntimeError("matrix entity")
        element_tags: np.ndarray | None = None
        types, blocks, _nodes = gmsh.model.mesh.getElements(3, matrix)
        for element_type, block in zip(types, blocks):
            if int(element_type) == int(tet10):
                element_tags = np.asarray(block, dtype=np.int64)
        if element_tags is None:
            raise RuntimeError("matrix Tet10")
        for order in (4, 6, 8):
            local, _weights = gmsh.model.mesh.getIntegrationPoints(tet10, f"Gauss{order}")
            points = np.asarray(local).reshape((-1, 3))
            jacobian_raw, determinant_raw, coordinate_raw = gmsh.model.mesh.getJacobians(tet10, local, matrix)
            determinant = np.asarray(determinant_raw).reshape((len(element_tags), len(points)))
            jacobian = np.asarray(jacobian_raw).reshape((len(element_tags), len(points), 3, 3))
            coordinates = np.asarray(coordinate_raw).reshape((len(element_tags), len(points), 3))
            normalized = determinant / np.maximum(
                np.sqrt(np.sum(jacobian * jacobian, axis=(2, 3))) ** 3, np.finfo(float).tiny
            )
            for element_index, point_index in np.argwhere((determinant <= 0) | (normalized <= 1e-10)):
                point = coordinates[element_index, point_index]
                failures.append(
                    {
                        "quadrature_order": order,
                        "element_tag": int(element_tags[element_index]),
                        "quadrature_point_index": int(point_index),
                        "physical_x_mm": float(point[0]),
                        "physical_y_mm": float(point[1]),
                        "physical_z_mm": float(point[2]),
                        "determinant": float(determinant[element_index, point_index]),
                        "normalized_determinant": float(normalized[element_index, point_index]),
                        "warning": WARNING,
                    }
                )
        gmsh.clear()
        gmsh.model.add("R304_EXACT_FACE")
        gmsh.model.occ.importShapes(str(BREP))
        gmsh.model.occ.synchronize()
        faces = [tag for _dimension, tag in gmsh.model.getEntities(2)]
        for row in failures:
            row.update(
                nearest(
                    np.asarray([row["physical_x_mm"], row["physical_y_mm"], row["physical_z_mm"]]), faces
                )
            )
    finally:
        gmsh.finalize()
    working.unlink()

    write_csv(OUT / "curved-jacobian-failure-localization.csv", failures)
    elements = {row["element_tag"] for row in failures}
    face_signatures = {row["nearest_exact_face_signature_sha256"] for row in failures}
    face_summary: list[dict[str, object]] = []
    for signature in sorted(face_signatures):
        subset = [row for row in failures if row["nearest_exact_face_signature_sha256"] == signature]
        first = subset[0]
        face_summary.append(
            {
                "nearest_exact_face_signature_sha256": signature,
                "nearest_exact_face_type": first["nearest_exact_face_type"],
                "nearest_exact_face_bbox_mm_json": first["nearest_exact_face_bbox_mm_json"],
                "failed_order_qp_pairs": len(subset),
                "unique_failed_elements": len({row["element_tag"] for row in subset}),
                "minimum_normalized_determinant": min(float(row["normalized_determinant"]) for row in subset),
                "warning": WARNING,
            }
        )
    write_csv(OUT / "exact-face-failure-summary.csv", face_summary)

    result_status = {
        "identifier": IDENT,
        "round": "R304",
        "date": "2026-08-13",
        "r303_status_sha256": sha(R303 / "analysis-status.json"),
        "r303_raw_linear_sha256": sha(R303 / "raw-linear-mesh.npz"),
        "r303_raw_tet10_sha256": sha(R303 / "raw-tet10-mesh.npz"),
        "failed_order_qp_pairs": len(failures),
        "unique_failed_elements": len(elements),
        "nearest_exact_face_clusters": len(face_signatures),
        "global_quality_gate_retained": True,
        "monitored_zone_gate_retained": True,
        "remesh_executed": False,
        "structural_solution_executed": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "work_authority": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(result_status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(
        json.dumps(
            {
                "identifier": IDENT,
                "generator_sha256": sha(Path(__file__).resolve()),
                "r303_status_sha256": sha(R303 / "analysis-status.json"),
                "r303_mesh_gzip_sha256": sha(R303 / "c07-conformal-zone-mesh.msh.gz"),
                "r303_raw_linear_sha256": sha(R303 / "raw-linear-mesh.npz"),
                "r303_raw_tet10_sha256": sha(R303 / "raw-tet10-mesh.npz"),
                "r297_brep_sha256": sha(BREP),
                "warning": WARNING,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        f"R304 localizes all {len(failures)} residual R303 failed quadrature points across "
        f"{len(elements)} element(s) and {len(face_signatures)} exact B-Rep face cluster(s). "
        "R303 retains the global and monitored-zone linear quality gates. No remesh or structural work is executed.\n",
        encoding="utf-8",
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv":
            manifest.append(
                {"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
            )
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(result_status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
