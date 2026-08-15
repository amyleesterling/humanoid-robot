#!/usr/bin/env python3
"""Execute the single preregistered R306 constrained high-order-curving candidate."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import shutil
import time
from pathlib import Path

import gmsh
import numpy as np

from hr_v0_mesh_raw_shards import LINEAR_KEYS, load_shards

ROOT = Path(__file__).resolve().parents[1]
R300 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-prereg-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-constrained-curving-mesh-p0.1"
IDENT = "HR-V0-J2-C07-PE-CONSTRAINED-CURVING-MESH-P0.1"
WARNING = "PRELIMINARY - PREREGISTERED CONSTRAINED HIGH-ORDER CURVING EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
NORMALIZED_FLOOR = 1e-10


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalized_copy(source: Path, destination: Path) -> None:
    rows = read_csv(source)
    for row in rows:
        if "warning" in row:
            row["warning"] = WARNING
    write_csv(destination, rows)


def main() -> int:
    started = time.perf_counter()
    protocol_path = PREREG / "frozen-constrained-curving-protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol["mesh_executed"] or protocol["candidate_id"] != "R306-C07-R300-CONSTRAINED-HIGHORDER-V01":
        raise RuntimeError("R306 prereg state")
    if protocol["source_mesh_gzip_sha256"] != sha(R300 / "c07-conformal-zone-mesh.msh.gz"):
        raise RuntimeError("R300 mesh binding")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    working = OUT / "_working.msh"
    with gzip.open(R300 / "c07-conformal-zone-mesh.msh.gz", "rb") as source, working.open("wb") as target:
        shutil.copyfileobj(source, target, length=1024 * 1024)

    baseline = load_shards(R300)
    baseline_tet_tags = baseline["tet10_element_tags"]
    baseline_tet_conn = baseline["tet10_connectivity"]
    baseline_node_tags = baseline["node_tags"]
    baseline_node_xyz = baseline["node_xyz"]
    baseline_lookup = {int(tag): baseline_node_xyz[index] for index, tag in enumerate(baseline_node_tags)}
    corner_tags = np.unique(baseline_tet_conn[:, :4])
    corner_pre_xyz = np.vstack([baseline_lookup[int(tag)] for tag in corner_tags])

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.open(str(working))
        matrix_entities: list[int] = []
        for dimension, physical_tag in gmsh.model.getPhysicalGroups(3):
            if gmsh.model.getPhysicalName(dimension, physical_tag) == "C07-MATRIX":
                matrix_entities = [int(tag) for tag in gmsh.model.getEntitiesForPhysicalGroup(dimension, physical_tag)]
        if len(matrix_entities) != 1:
            raise RuntimeError("C07-MATRIX entity")

        gmsh.model.mesh.optimize("HighOrder", False, 1, [(3, matrix_entities[0])])
        post_tags_raw, post_coords_raw, _ = gmsh.model.mesh.getNodes()
        post_tags = np.asarray(post_tags_raw, dtype=np.int64)
        post_xyz = np.asarray(post_coords_raw, dtype=float).reshape((-1, 3))
        post_lookup = {int(tag): post_xyz[index] for index, tag in enumerate(post_tags)}
        if not all(int(tag) in post_lookup for tag in corner_tags):
            raise RuntimeError("optimizer changed corner node tags; frozen same-tag route rejected")
        pre_restore_xyz = np.vstack([post_lookup[int(tag)] for tag in corner_tags])
        pre_restore_distance = np.linalg.norm(pre_restore_xyz - corner_pre_xyz, axis=1)
        if float(np.max(pre_restore_distance)) > float(protocol["operation"]["corner_mapping_tolerance_mm"]):
            raise RuntimeError("optimizer corner movement exceeds preregistered mapping tolerance")
        for index, tag in enumerate(corner_tags):
            gmsh.model.mesh.setNode(int(tag), corner_pre_xyz[index].tolist(), [])

        restored_tags_raw, restored_coords_raw, _ = gmsh.model.mesh.getNodes()
        restored_tags = np.asarray(restored_tags_raw, dtype=np.int64)
        restored_xyz = np.asarray(restored_coords_raw, dtype=float).reshape((-1, 3))
        restored_lookup = {int(tag): restored_xyz[index] for index, tag in enumerate(restored_tags)}
        restored_corner_xyz = np.vstack([restored_lookup[int(tag)] for tag in corner_tags])
        post_restore_distance = np.linalg.norm(restored_corner_xyz - corner_pre_xyz, axis=1)
        post_restore_max = float(np.max(post_restore_distance))

        tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
        optimized_tags_raw, optimized_conn_raw = gmsh.model.mesh.getElementsByType(tet10)
        optimized_tags = np.asarray(optimized_tags_raw, dtype=np.int64)
        optimized_conn = np.asarray(optimized_conn_raw, dtype=np.int64).reshape((-1, 10))
        connectivity_gate = bool(
            np.array_equal(optimized_tags, baseline_tet_tags) and np.array_equal(optimized_conn, baseline_tet_conn)
        )
        corner_gate = bool(post_restore_max <= float(protocol["operation"]["corner_restore_tolerance_mm"]))

        jacobian_rows: list[dict[str, object]] = []
        q8_volume: dict[str, float] = {}
        jacobian_gate = True
        for order in (4, 6, 8):
            local, weights_raw = gmsh.model.mesh.getIntegrationPoints(tet10, f"Gauss{order}")
            weights = np.asarray(weights_raw, dtype=float)
            for dimension, physical_tag in sorted(gmsh.model.getPhysicalGroups(3)):
                zone_name = gmsh.model.getPhysicalName(dimension, physical_tag)
                for volume_tag in gmsh.model.getEntitiesForPhysicalGroup(dimension, physical_tag):
                    jacobian_raw, determinant_raw, _coordinates = gmsh.model.mesh.getJacobians(tet10, local, int(volume_tag))
                    determinant = np.asarray(determinant_raw, dtype=float)
                    matrices = np.asarray(jacobian_raw, dtype=float).reshape((-1, 3, 3))
                    normalized = determinant / np.maximum(
                        np.sqrt(np.sum(matrices * matrices, axis=(1, 2))) ** 3, np.finfo(float).tiny
                    )
                    wrong = int(np.count_nonzero(determinant <= 0.0))
                    normalized_fail = int(np.count_nonzero(normalized <= NORMALIZED_FLOOR))
                    passed = wrong == 0 and normalized_fail == 0
                    jacobian_gate = jacobian_gate and passed
                    jacobian_rows.append(
                        {
                            "quadrature_order": order,
                            "zone_id": zone_name,
                            "volume_tag_diagnostic_only": int(volume_tag),
                            "quadrature_samples": determinant.size,
                            "wrong_or_zero_count": wrong,
                            "normalized_floor_fail_count": normalized_fail,
                            "minimum_determinant": float(np.min(determinant)),
                            "minimum_normalized_determinant": float(np.min(normalized)),
                            "normalized_floor": NORMALIZED_FLOOR,
                            "actual_gmsh_tet10_quadrature_gate": "PASS" if passed else "FAIL",
                            "full_reference_domain_positivity": "UNVERIFIED",
                            "warning": WARNING,
                        }
                    )
                    if order == 8:
                        element_count = determinant.size // len(weights)
                        q8_volume[zone_name] = q8_volume.get(zone_name, 0.0) + float(
                            np.sum(determinant.reshape((element_count, len(weights))) * weights[None, :])
                        )
        write_csv(OUT / "actual-quadrature-jacobian-register.csv", jacobian_rows)

        exact_volume = {row["zone_id"]: float(row["exact_occ_volume_mm3"]) for row in read_csv(R300 / "zone-volume-integration.csv")}
        write_csv(
            OUT / "zone-volume-integration.csv",
            [
                {
                    "zone_id": zone,
                    "exact_occ_volume_mm3": exact_volume[zone],
                    "tet10_q8_integrated_volume_mm3": integrated,
                    "relative_error": abs(integrated - exact_volume[zone]) / exact_volume[zone],
                    "credit": "CURVED-MESH GEOMETRY CONSERVATION SCREEN ONLY",
                    "warning": WARNING,
                }
                for zone, integrated in sorted(q8_volume.items())
            ],
        )

        np.savez_compressed(
            OUT / "raw-linear-mesh.npz", **{key: baseline[key] for key in LINEAR_KEYS}
        )
        np.savez_compressed(
            OUT / "raw-tet10-mesh.npz",
            node_tags=restored_tags,
            node_xyz=restored_xyz,
            tet10_element_tags=optimized_tags,
            tet10_connectivity=optimized_conn,
        )
        np.savez_compressed(
            OUT / "corner-restoration-evidence.npz",
            corner_tags=corner_tags,
            corner_pre_xyz=corner_pre_xyz,
            corner_pre_restore_xyz=pre_restore_xyz,
            corner_restored_xyz=restored_corner_xyz,
            pre_restore_distance_mm=pre_restore_distance,
            post_restore_distance_mm=post_restore_distance,
        )

        output_mesh = OUT / "c07-constrained-curving.msh"
        output_gzip = OUT / "c07-constrained-curving.msh.gz"
        gmsh.write(str(output_mesh))
        mesh_uncompressed_sha = sha(output_mesh)
        mesh_uncompressed_bytes = output_mesh.stat().st_size
        with output_mesh.open("rb") as source, output_gzip.open("wb") as compressed_stream:
            with gzip.GzipFile(filename="", mode="wb", fileobj=compressed_stream, compresslevel=9, mtime=0) as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
        output_mesh.unlink()
    finally:
        gmsh.finalize()
    working.unlink()

    for name in ("sicn-histogram.csv", "zone-quality-summary.csv", "retained-pe-subzone-quality-inference.csv"):
        normalized_copy(R300 / name, OUT / name)
    sampled_gate = bool(connectivity_gate and corner_gate and jacobian_gate)
    status = {
        "identifier": IDENT,
        "round": "R306",
        "date": "2026-08-13",
        "candidate_id": protocol["candidate_id"],
        "preregistration_sha256": sha(protocol_path),
        "r300_status_sha256": sha(R300 / "analysis-status.json"),
        "tet10_tetrahedra": len(optimized_tags),
        "linear_corners": len(corner_tags),
        "optimizer": "HighOrder",
        "optimizer_force": False,
        "optimizer_iterations": 1,
        "optimizer_dim_tag": "C07-MATRIX",
        "maximum_pre_restore_corner_movement_mm": float(np.max(pre_restore_distance)),
        "maximum_post_restore_corner_error_mm": post_restore_max,
        "corner_restore_gate": corner_gate,
        "element_connectivity_gate": connectivity_gate,
        "global_and_zone_linear_quality_retained": True,
        "actual_quadrature_signed_jacobian_gate": jacobian_gate,
        "sampled_constrained_curving_candidate_pass": sampled_gate,
        "exact_facet_revalidation_executed": False,
        "exact_facet_revalidation_pass": False,
        "full_reference_domain_curved_jacobian_positive": False,
        "r279_c02_complete": False,
        "structural_solution_executed": False,
        "mesh_convergence_complete": False,
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
        "mesh_gzip_sha256": sha(output_gzip),
        "mesh_uncompressed_sha256": mesh_uncompressed_sha,
        "mesh_uncompressed_bytes": mesh_uncompressed_bytes,
        "raw_linear_mesh_sha256": sha(OUT / "raw-linear-mesh.npz"),
        "raw_tet10_mesh_sha256": sha(OUT / "raw-tet10-mesh.npz"),
        "corner_evidence_sha256": sha(OUT / "corner-restoration-evidence.npz"),
        "seconds": time.perf_counter() - started,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(
        json.dumps(
            {
                "identifier": IDENT,
                "generator_sha256": sha(Path(__file__).resolve()),
                "preregistration_sha256": sha(protocol_path),
                "r300_status_sha256": sha(R300 / "analysis-status.json"),
                "r300_mesh_gzip_sha256": sha(R300 / "c07-conformal-zone-mesh.msh.gz"),
                "r300_raw_linear_sha256": sha(R300 / "raw-linear-mesh.npz"),
                "r300_raw_tet10_sha256": sha(R300 / "raw-tet10-mesh.npz"),
                "gmsh_method": "HighOrder",
                "force": False,
                "niter": 1,
                "dim_tags": "C07-MATRIX volume only",
                "warning": WARNING,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R306 executes one preregistered constrained `HighOrder` operation on the retained R300 mesh without remeshing. "
        "Every Tet10 corner is restored to its pre-operation coordinate and optimized midsides are retained. This package "
        "reports finite Q4/Q6/Q8 evidence only; exact facet/B-Rep/load revalidation remains a separate mandatory gate.\n",
        encoding="utf-8",
    )
    write_csv(
        OUT / "open-holds.csv",
        [
            {"hold_id": f"R306-H{index:02d}", "hold": hold, "state": "OPEN", "warning": WARNING}
            for index, hold in enumerate(
                (
                    "Execute exact exterior-facet/B-Rep surface deviation, per-face area and load-geometry revalidation.",
                    "Prove full-reference-domain curved Jacobian positivity or retain the finite sampled boundary.",
                    "Obtain independent numerical acceptance before structural execution.",
                    "Execute structural fields, exact-zone metrics, sections, singularities and convergence only after disposition.",
                    "Close nonlinear contact, joined hardware, dynamics, material, DFM/FAI and physical correlation separately.",
                ),
                1,
            )
        ],
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv":
            manifest.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2))
    return 0 if sampled_gate else 2


if __name__ == "__main__":
    raise SystemExit(main())
