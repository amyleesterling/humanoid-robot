#!/usr/bin/env python3
"""Execute the single preregistered R307 CAD-resident curving candidate.

The hash-bound R300/R298/base generators are imported without modification.
This wrapper intercepts only the live-OCC setOrder(2) call, performs the one
frozen constrained HighOrder operation, restores every linear corner, and
then lets the original generator produce its normal quality evidence.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path

import gmsh
import numpy as np
from scipy.spatial import cKDTree

from hr_v0_mesh_raw_shards import LINEAR_KEYS, TET10_KEYS, load_shards, split_raw

ROOT = Path(__file__).resolve().parents[1]
R300_GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_seam_free_jacobian_mesh_p01.py"
R298_GEN = ROOT / "tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py"
BASE_GEN = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
R300 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1"
R306 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-prereg-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-cad-curving-mesh-p0.1"
IDENT = "HR-V0-J2-C07-PE-CAD-CURVING-MESH-P0.1"
ROUND = "R307"
WARNING = "PRELIMINARY - CAD-RESIDENT CONSTRAINED CURVING EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha(value: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode())
    digest.update(json.dumps(value.shape).encode())
    digest.update(np.ascontiguousarray(value).tobytes())
    return digest.hexdigest()


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_r300_generator():
    spec = importlib.util.spec_from_file_location("r300_for_r307", R300_GEN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R300 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    started = time.perf_counter()
    protocol_path = PREREG / "frozen-cad-curving-protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    prereg_status = json.loads((PREREG / "analysis-status.json").read_text(encoding="utf-8"))
    if prereg_status["execution_started"] or protocol["candidate_id"] != "R307-C07-CAD-RESIDENT-CONSTRAINED-HIGHORDER-V01":
        raise RuntimeError("R307 preregistration state")
    if protocol["transitive_generators"] != {
        "r300": sha(R300_GEN), "r298": sha(R298_GEN), "base": sha(BASE_GEN)
    }:
        raise RuntimeError("R307 transitive generator binding")
    baseline = load_shards(R300)
    evidence: dict[str, object] = {}

    r300 = load_r300_generator()
    original_load_prior = r300.load_prior

    def load_prior_with_live_occ_hook():
        prior = original_load_prior()
        original_load_base = prior.load_base

        def load_base_with_live_occ_hook():
            base = original_load_base()
            original_set_order = base.gmsh.model.mesh.setOrder

            def set_order_with_r307(order: int) -> None:
                if order != 2:
                    raise RuntimeError(f"unexpected setOrder({order})")

                tet4 = gmsh.model.mesh.getElementType("tetrahedron", 1)
                linear_etags_raw, linear_conn_raw = gmsh.model.mesh.getElementsByType(tet4)
                linear_etags = np.asarray(linear_etags_raw, dtype=np.int64)
                linear_conn = np.asarray(linear_conn_raw, dtype=np.int64).reshape((-1, 4))
                linear_sicn = np.asarray(gmsh.model.mesh.getElementQualities(linear_etags.tolist(), "minSICN"), dtype=float)
                linear_ntags_raw, linear_coords_raw, _ = gmsh.model.mesh.getNodes()
                linear_ntags = np.asarray(linear_ntags_raw, dtype=np.int64)
                linear_xyz = np.asarray(linear_coords_raw, dtype=float).reshape((-1, 3))

                tag_gate = bool(np.array_equal(linear_etags, baseline["linear_element_tags"]))
                conn_gate = bool(np.array_equal(linear_conn, baseline["linear_tet4_connectivity"]))
                sicn_gate = bool(np.array_equal(linear_sicn, baseline["linear_sicn"]))
                node_tag_gate = bool(np.array_equal(linear_ntags, baseline["linear_node_tags"]))
                coord_delta = float(np.max(np.abs(linear_xyz - baseline["linear_node_xyz"]))) if node_tag_gate else float("inf")
                if not (tag_gate and conn_gate and sicn_gate and node_tag_gate and coord_delta <= 1e-12):
                    raise RuntimeError(
                        f"R300 linear mesh did not reproduce: tags={tag_gate} conn={conn_gate} "
                        f"quality={sicn_gate} node_tags={node_tag_gate} coord_delta={coord_delta}"
                    )
                evidence.update({
                    "linear_element_tags_exact": tag_gate,
                    "linear_connectivity_exact": conn_gate,
                    "linear_sicn_exact": sicn_gate,
                    "linear_node_tags_exact": node_tag_gate,
                    "linear_coordinate_max_delta_mm": coord_delta,
                })
                (OUT / "_r307-attempt-state.json").write_text(json.dumps({
                    "candidate_id": protocol["candidate_id"], "phase": "R300_LINEAR_REPRODUCED",
                    "optimizer_started": False, "warning": WARNING,
                }, indent=2) + "\n", encoding="utf-8")

                original_set_order(order)
                tet10 = gmsh.model.mesh.getElementType("tetrahedron", 2)
                pre_etags_raw, pre_conn_raw = gmsh.model.mesh.getElementsByType(tet10)
                pre_etags = np.asarray(pre_etags_raw, dtype=np.int64)
                pre_conn = np.asarray(pre_conn_raw, dtype=np.int64).reshape((-1, 10))
                pre_ntags_raw, pre_coords_raw, _ = gmsh.model.mesh.getNodes()
                pre_ntags = np.asarray(pre_ntags_raw, dtype=np.int64)
                pre_xyz = np.asarray(pre_coords_raw, dtype=float).reshape((-1, 3))
                pre_lookup = {int(tag): pre_xyz[index] for index, tag in enumerate(pre_ntags)}
                old_lookup = {int(tag): linear_xyz[index] for index, tag in enumerate(linear_ntags)}
                old_corners = np.unique(linear_conn)
                new_corners = np.unique(pre_conn[:, :4])
                old_points = np.vstack([old_lookup[int(tag)] for tag in old_corners])
                new_points = np.vstack([pre_lookup[int(tag)] for tag in new_corners])
                distances, targets = cKDTree(new_points).query(old_points, k=1, workers=1)
                unique = len(set(int(value) for value in targets)) == len(new_corners)
                corner_map_gate = bool(len(old_corners) == len(new_corners) and unique and float(np.max(distances)) <= 0.1)
                if not corner_map_gate:
                    raise RuntimeError(f"R307 corner mapping failed: max={float(np.max(distances))} unique={unique}")
                mapped_tags = np.asarray([new_corners[int(index)] for index in targets], dtype=np.int64)

                matrix_entities: list[int] = []
                for dimension, physical_tag in gmsh.model.getPhysicalGroups(3):
                    if gmsh.model.getPhysicalName(dimension, physical_tag) == "C07-MATRIX":
                        matrix_entities = [int(tag) for tag in gmsh.model.getEntitiesForPhysicalGroup(dimension, physical_tag)]
                if len(matrix_entities) != 1:
                    raise RuntimeError(f"C07-MATRIX volume count {len(matrix_entities)}")
                (OUT / "_r307-attempt-state.json").write_text(json.dumps({
                    "candidate_id": protocol["candidate_id"], "phase": "HIGHORDER_RUNNING",
                    "optimizer_started": True, "optimizer_completed": False,
                    "optimizer": "HighOrder", "force": False, "niter": 1,
                    "dim_tags": [[3, matrix_entities[0]]], "warning": WARNING,
                }, indent=2) + "\n", encoding="utf-8")
                print("R307_PROGRESS HIGHORDER_START", flush=True)
                gmsh.model.mesh.optimize("HighOrder", False, 1, [(3, matrix_entities[0])])
                print("R307_PROGRESS HIGHORDER_COMPLETE", flush=True)

                post_ntags_raw, post_coords_raw, _ = gmsh.model.mesh.getNodes()
                post_ntags = np.asarray(post_ntags_raw, dtype=np.int64)
                post_xyz = np.asarray(post_coords_raw, dtype=float).reshape((-1, 3))
                post_lookup = {int(tag): post_xyz[index] for index, tag in enumerate(post_ntags)}
                if not all(int(tag) in post_lookup for tag in mapped_tags):
                    raise RuntimeError("optimizer changed mapped corner node tags")
                pre_restore_xyz = np.vstack([post_lookup[int(tag)] for tag in mapped_tags])
                pre_restore_distance = np.linalg.norm(pre_restore_xyz - old_points, axis=1)
                if float(np.max(pre_restore_distance)) > 0.1:
                    raise RuntimeError(f"optimizer corner movement exceeds 0.1 mm: {float(np.max(pre_restore_distance))}")
                for index, tag in enumerate(mapped_tags):
                    gmsh.model.mesh.setNode(int(tag), old_points[index].tolist(), [])

                restored_ntags_raw, restored_coords_raw, _ = gmsh.model.mesh.getNodes()
                restored_ntags = np.asarray(restored_ntags_raw, dtype=np.int64)
                restored_xyz = np.asarray(restored_coords_raw, dtype=float).reshape((-1, 3))
                restored_lookup = {int(tag): restored_xyz[index] for index, tag in enumerate(restored_ntags)}
                restored_corner_xyz = np.vstack([restored_lookup[int(tag)] for tag in mapped_tags])
                restore_distance = np.linalg.norm(restored_corner_xyz - old_points, axis=1)
                restore_max = float(np.max(restore_distance))
                if restore_max > 1e-12:
                    raise RuntimeError(f"corner restoration exceeds 1e-12 mm: {restore_max}")

                post_etags_raw, post_conn_raw = gmsh.model.mesh.getElementsByType(tet10)
                post_etags = np.asarray(post_etags_raw, dtype=np.int64)
                post_conn = np.asarray(post_conn_raw, dtype=np.int64).reshape((-1, 10))
                identity_gate = bool(np.array_equal(pre_etags, post_etags) and np.array_equal(pre_conn, post_conn))
                if not identity_gate:
                    raise RuntimeError("optimizer changed Tet10 element tags/connectivity")
                evidence.update({
                    "corner_bijection_gate": corner_map_gate,
                    "corner_bijection_max_mm": float(np.max(distances)),
                    "corner_count": len(old_corners),
                    "maximum_pre_restore_corner_movement_mm": float(np.max(pre_restore_distance)),
                    "maximum_post_restore_corner_error_mm": restore_max,
                    "element_connectivity_gate": identity_gate,
                    "pre_tet10_element_tags_sha256": array_sha(pre_etags),
                    "pre_tet10_connectivity_sha256": array_sha(pre_conn),
                    "post_tet10_element_tags_sha256": array_sha(post_etags),
                    "post_tet10_connectivity_sha256": array_sha(post_conn),
                    "matrix_volume_tag_diagnostic_only": matrix_entities[0],
                })
                np.savez_compressed(
                    OUT / "corner-restoration-evidence.npz",
                    old_corner_tags=old_corners, mapped_tet10_corner_tags=mapped_tags,
                    linear_corner_xyz=old_points, pre_restore_corner_xyz=pre_restore_xyz,
                    restored_corner_xyz=restored_corner_xyz,
                    initial_mapping_distance_mm=distances,
                    pre_restore_distance_mm=pre_restore_distance,
                    post_restore_distance_mm=restore_distance,
                )
                (OUT / "_r307-attempt-state.json").write_text(json.dumps({
                    "candidate_id": protocol["candidate_id"], "phase": "HIGHORDER_COMPLETE_CORNERS_RESTORED",
                    "optimizer_started": True, "optimizer_completed": True,
                    "maximum_post_restore_corner_error_mm": restore_max, "warning": WARNING,
                }, indent=2) + "\n", encoding="utf-8")

            base.gmsh.model.mesh.setOrder = set_order_with_r307
            return base

        prior.load_base = load_base_with_live_occ_hook
        return prior

    r300.load_prior = load_prior_with_live_occ_hook
    r300.OUT = OUT
    r300.RELEASE = RELEASE
    r300.IDENT = IDENT
    r300.ROUND = ROUND
    r300.WARNING = WARNING
    base_code = r300.main()

    raw_monolithic = OUT / "raw-conformal-zone-mesh.npz"
    split_raw(raw_monolithic, OUT / "raw-linear-mesh.npz", OUT / "raw-tet10-mesh.npz")
    raw_monolithic.unlink()
    result = load_shards(OUT)
    exact_linear = {key: bool(np.array_equal(result[key], baseline[key])) for key in LINEAR_KEYS}
    linear_exact = all(exact_linear.values())
    tet10_topology_exact = bool(
        np.array_equal(result["tet10_element_tags"], baseline["tet10_element_tags"])
        and np.array_equal(result["tet10_connectivity"], baseline["tet10_connectivity"])
    )
    if not linear_exact or not tet10_topology_exact:
        raise RuntimeError(f"post-run R300 identity failed: linear={exact_linear} tet10={tet10_topology_exact}")

    protocol_copy = OUT / "frozen-cad-curving-protocol.json"
    shutil.copy2(protocol_path, protocol_copy)
    old_protocol = OUT / "frozen-jacobian-successor-protocol.json"
    if old_protocol.exists():
        old_protocol.unlink()
    attempt_state = OUT / "_r307-attempt-state.json"
    if attempt_state.exists():
        attempt_state.unlink()

    status_path = OUT / "analysis-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    jac_rows = read_csv(OUT / "actual-quadrature-jacobian-register.csv")
    jac_gate = all(int(row["wrong_or_zero_count"]) == 0 and int(row["normalized_floor_fail_count"]) == 0 for row in jac_rows)
    sampled_gate = bool(
        linear_exact and tet10_topology_exact and evidence["corner_bijection_gate"]
        and evidence["maximum_post_restore_corner_error_mm"] <= 1e-12
        and evidence["element_connectivity_gate"] and status["global_sicn_gate"]
        and status["monitored_zone_minimum_gate"] and jac_gate
    )
    status.update({
        "identifier": IDENT, "round": ROUND, "candidate_id": protocol["candidate_id"],
        "preregistration_sha256": sha(protocol_path),
        "r300_status_sha256": sha(R300 / "analysis-status.json"),
        "r306_status_sha256": sha(R306 / "analysis-status.json"),
        "single_preregistered_execution_complete": True,
        "optimizer": "HighOrder", "optimizer_force": False, "optimizer_iterations": 1,
        "optimizer_dim_tag": "C07-MATRIX volume only",
        "r300_linear_arrays_exact": linear_exact,
        "r300_linear_array_comparison": exact_linear,
        "r300_linear_coordinate_max_delta_mm": evidence["linear_coordinate_max_delta_mm"],
        "r300_tet10_tags_and_connectivity_exact": tet10_topology_exact,
        "maximum_initial_corner_mapping_distance_mm": evidence["corner_bijection_max_mm"],
        "maximum_pre_restore_corner_movement_mm": evidence["maximum_pre_restore_corner_movement_mm"],
        "maximum_post_restore_corner_error_mm": evidence["maximum_post_restore_corner_error_mm"],
        "corner_bijection_gate": evidence["corner_bijection_gate"],
        "element_connectivity_gate": evidence["element_connectivity_gate"],
        "sampled_cad_curving_candidate_pass": sampled_gate,
        "exact_facet_revalidation_executed": False,
        "exact_facet_revalidation_pass": False,
        "full_reference_domain_curved_jacobian_positive": False,
        "r279_c02_complete": False,
        "structural_solution_executed": False, "mesh_convergence_complete": False,
        "r278_h02_closed": False, "capacity_credit": False, "selected": False,
        "safety_credit": False, "procurement_authorized": False,
        "fabrication_authorized": False, "assembly_authorized": False,
        "connection_authorized": False, "powered_testing_authorized": False,
        "motion_authorized": False, "energization_authorized": False,
        "raw_linear_mesh_sha256": sha(OUT / "raw-linear-mesh.npz"),
        "raw_tet10_mesh_sha256": sha(OUT / "raw-tet10-mesh.npz"),
        "corner_evidence_sha256": sha(OUT / "corner-restoration-evidence.npz"),
        "base_generator_exit_code": base_code,
        "seconds": time.perf_counter() - started, "warning": WARNING,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    provenance_path = OUT / "execution-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update({
        "identifier": IDENT,
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()),
        "transitive_r300_generator_sha256": sha(R300_GEN),
        "transitive_r298_generator_sha256": sha(R298_GEN),
        "transitive_base_generator_sha256": sha(BASE_GEN),
        "preregistration_path": protocol_path.relative_to(ROOT).as_posix(),
        "preregistration_sha256": sha(protocol_path),
        "r300_raw_linear_sha256": sha(R300 / "raw-linear-mesh.npz"),
        "r300_raw_tet10_sha256": sha(R300 / "raw-tet10-mesh.npz"),
        "optimizer": "HighOrder", "force": False, "niter": 1,
        "dim_tags": "C07-MATRIX volume only", "corners_restored": True,
        "warning": WARNING,
    })
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R307 executes the one frozen CAD-resident constrained `HighOrder` candidate while the exact R297 OCC model remains live. "
        "The regenerated R300 linear mesh must reproduce exactly, all mapped linear corners are restored, and only optimized "
        "midsides are retained. Q4/Q6/Q8 results are finite sampled evidence, not proof over the complete reference tetrahedron.\n\n"
        "Even a sampled pass does not close R279-C02. Exact exterior-facet/B-Rep/load revalidation, independent acceptance, "
        "structural fields, convergence, H02, capacity, physical validation and every work authority remain open.\n",
        encoding="utf-8",
    )
    write_csv(OUT / "r300-reproduction-register.csv", [{
        "linear_element_tags_exact": evidence["linear_element_tags_exact"],
        "linear_connectivity_exact": evidence["linear_connectivity_exact"],
        "linear_sicn_exact": evidence["linear_sicn_exact"],
        "linear_node_tags_exact": evidence["linear_node_tags_exact"],
        "linear_coordinate_max_delta_mm": evidence["linear_coordinate_max_delta_mm"],
        "element_zone_code_exact": exact_linear["element_zone_code"],
        "tet10_element_tags_and_connectivity_exact": tet10_topology_exact,
        "gate": "PASS" if linear_exact and tet10_topology_exact else "FAIL", "warning": WARNING,
    }])
    write_csv(OUT / "open-holds.csv", [
        {"hold_id": "R307-H01", "hold": "Execute exact exterior-facet/B-Rep deviation, per-face area and load area/location/moment revalidation.", "state": "OPEN", "warning": WARNING},
        {"hold_id": "R307-H02", "hold": "Prove full-reference-domain curved Jacobian positivity or retain the finite sampled boundary.", "state": "OPEN", "warning": WARNING},
        {"hold_id": "R307-H03", "hold": "Obtain independent numerical acceptance before structural execution.", "state": "OPEN", "warning": WARNING},
        {"hold_id": "R307-H04", "hold": "Execute structural fields, exact-zone metrics, sections, singularities and convergence only after disposition.", "state": "OPEN", "warning": WARNING},
        {"hold_id": "R307-H05", "hold": "Close nonlinear contact, joined hardware, dynamics, material, DFM/FAI and physical correlation separately.", "state": "OPEN", "warning": WARNING},
    ])

    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
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
