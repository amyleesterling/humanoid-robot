#!/usr/bin/env python3
"""Fail-closed retained-evidence checks for the R284 C07 mesh screen."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from skfem import MeshTet, MeshTet2
from skfem.quadrature import get_quadrature_tet


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
IDENT = "HR-V0-J2-C07-FIXED-CORNER-SCREEN-P0.1"
WARNING = "PRELIMINARY - FIXED-CORNER CURVED-MESH DEVELOPMENT SCREEN ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OLD_IDENT = "HR-V0-J2-C07-CURVED-MESH-REPAIR-P0.1"
OLD_WARNING = "PRELIMINARY - CURVED MESH METHOD EVIDENCE ONLY"
TET10_EDGES = ((0, 1, 4), (1, 2, 5), (2, 0, 6), (0, 3, 7), (2, 3, 8), (3, 1, 9))
EXPECTED_INPUTS = {
    "cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step": "exact C07 STEP",
    "tools/generate_hr_v0_j2_c07_fixed_corner_screen_p01.py": "R284 screen generator",
    "tools/generate_hr_v0_j2_c07_curved_mesh_repair_p01.py": "audited R283 transfer/check implementation",
    "tools/generate_hr_v0_j2_stop_refinement_execution_p01.py": "transitive OCC entity/local-field implementation",
}
EXPECTED = {
    "R284-V03-REFINED": {"wrong": 37, "passed": False, "return_code": 2, "sizes": (4.0, 0.70, 1.0)},
    "R284-V06-FINE": {"wrong": 0, "passed": True, "return_code": 0, "sizes": (3.0, 0.50, 0.75)},
    "R284-V08-ULTRAFINE": {"wrong": 9, "passed": False, "return_code": 2, "sizes": (2.0, 0.35, 0.50)},
}


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, *, atol: float = 1e-12, rtol: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol)


def check_manifest(directory: Path) -> None:
    records = rows(directory / "file-manifest.csv")
    actual = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    mapped = {record["relative_path"]: record for record in records}
    need(len(mapped) == len(records) == len(actual), f"manifest count/uniqueness {directory}")
    for path in actual:
        need(path.name in mapped, f"manifest missing {path.name}")
        need(mapped[path.name]["sha256"] == sha(path), f"manifest hash {path.name}")
        need(int(mapped[path.name]["bytes"]) == path.stat().st_size, f"manifest bytes {path.name}")
        need(mapped[path.name]["warning"] == WARNING, f"manifest warning {path.name}")


def check_package_manifest() -> None:
    records = rows(OUT / "package-manifest.csv")
    actual = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "package-manifest.csv")
    mapped = {record["relative_path"]: record for record in records}
    need(len(mapped) == len(records) == len(actual), "package manifest count/uniqueness")
    for path in actual:
        relative = path.relative_to(OUT).as_posix()
        need(relative in mapped, f"package manifest missing {relative}")
        need(mapped[relative]["sha256"] == sha(path), f"package manifest hash {relative}")
        need(int(mapped[relative]["bytes"]) == path.stat().st_size, f"package manifest bytes {relative}")
        need(mapped[relative]["warning"] == WARNING, f"package manifest warning {relative}")


def check_text_identity() -> None:
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        need(OLD_IDENT not in text and OLD_WARNING not in text, f"stale identity/warning {path}")
        if path.suffix.lower() == ".csv":
            for record in rows(path):
                if "warning" in record:
                    need(record["warning"] == WARNING, f"warning drift {path}")
                if record.get("identifier"):
                    need(record["identifier"] == IDENT, f"identifier drift {path}")
        elif path.suffix.lower() == ".json":
            record = json.loads(text)
            need(record.get("warning") == WARNING, f"JSON warning {path}")
            if "identifier" in record:
                need(record["identifier"] == IDENT, f"JSON identifier {path}")
        else:
            need(WARNING in text, f"README warning {path}")


def check_runtime(screen: str, summary: dict[str, str], run: Path) -> None:
    input_records = rows(run / "input-register.csv")
    actual_inputs = {record["source_path"]: record["role"] for record in input_records}
    need(len(input_records) == len(actual_inputs) == 4 and actual_inputs == EXPECTED_INPUTS, f"exact transitive inputs {screen}")
    for record in input_records:
        need(record["warning"] == WARNING, f"input warning {screen}")
        need(sha(ROOT / record["source_path"]) == record["sha256"], f"input hash {screen} {record['source_path']}")

    provenance = json.loads((run / "runtime-provenance.json").read_text(encoding="utf-8"))
    need(provenance["identifier"] == IDENT and provenance["screen_id"] == screen, f"runtime identity {screen}")
    started = datetime.fromisoformat(provenance["run_started_timestamp_utc"])
    completed = datetime.fromisoformat(provenance["run_completed_timestamp_utc"])
    need(started.tzinfo is not None and completed.tzinfo is not None and completed >= started, f"runtime timestamps {screen}")
    expected_argv = [provenance["python_executable"], "tools/generate_hr_v0_j2_c07_fixed_corner_screen_p01.py", screen]
    need(provenance["command_argv"] == expected_argv, f"runtime argv {screen}")
    need(Path(provenance["working_directory"]).resolve() == ROOT.resolve(), f"runtime cwd {screen}")
    need(len(provenance["baseline_commit"]) == 40 and all(c in "0123456789abcdef" for c in provenance["baseline_commit"]), f"baseline SHA {screen}")
    status_lines = provenance["git_status_porcelain"]
    serialized = ("\n".join(status_lines) + ("\n" if status_lines else "")).encode("utf-8")
    need(provenance["git_worktree_dirty"] is bool(status_lines), f"dirty state {screen}")
    need(provenance["git_status_porcelain_sha256"] == hashlib.sha256(serialized).hexdigest(), f"status hash {screen}")
    need(provenance["git_status_untracked_scope"] == "normal", f"status scope {screen}")
    need(provenance["python_version"] == platform.python_version(), f"Python version {screen}")
    need(provenance["platform"] == platform.platform() and provenance["processor"], f"platform {screen}")
    need(provenance["gmsh_version"] == importlib.metadata.version("gmsh"), f"Gmsh version {screen}")
    need(provenance["numpy_version"] == importlib.metadata.version("numpy"), f"NumPy version {screen}")
    need(provenance["scipy_version"] == importlib.metadata.version("scipy"), f"SciPy version {screen}")
    need(provenance["scikit_fem_version"] == importlib.metadata.version("scikit-fem"), f"scikit-fem version {screen}")
    expected = EXPECTED[screen]
    need(provenance["return_code_recorded_after_execution"] == expected["return_code"], f"return code {screen}")
    need(provenance["general_num_threads"] == 1 and provenance["high_order_optimizer"] == "NONE", f"deterministic options {screen}")
    need("REPEATABILITY HOLD OPEN" in provenance["mesh_random_factor"], f"seed disclosure {screen}")
    need(int(provenance["algorithm3d"]) == int(summary["algorithm3d"]) and provenance["linear_optimizer"] == summary["linear_optimizer"], f"algorithm {screen}")
    sizes = provenance["effective_size_fields"]
    expected_sizes = expected["sizes"]
    need(close(sizes["global_h_mm"], expected_sizes[0]) and close(sizes["pocket_h_mm"], expected_sizes[1]) and close(sizes["hole_h_mm"], expected_sizes[2]), f"size fields {screen}")


def check_run(screen: str, summary: dict[str, str]) -> None:
    run = OUT / screen.lower()
    need(run.is_dir(), f"run dir {screen}")
    check_manifest(run)
    check_runtime(screen, summary, run)

    raw_path = ROOT / summary["raw_npz"]
    need(raw_path.is_file() and sha(raw_path) == summary["raw_npz_sha256"], f"raw hash {screen}")
    raw = np.load(raw_path)
    required_arrays = {
        "linear_node_tags", "linear_node_xyz", "linear_element_tags", "linear_tet4_connectivity",
        "node_tags", "node_xyz", "tet10_element_tags", "tet10_connectivity", "linear_sicn",
        "pre_entity_nodes_holes", "pre_entity_nodes_pocket_edge", "pre_entity_nodes_pocket_floor", "pre_entity_nodes_metal_face",
        "post_entity_nodes_holes", "post_entity_nodes_pocket_edge", "post_entity_nodes_pocket_floor", "post_entity_nodes_metal_face",
    }
    need(required_arrays <= set(raw.files), f"raw arrays {screen}")
    linear_node_tags = np.asarray(raw["linear_node_tags"], dtype=np.int64)
    linear_node_xyz = np.asarray(raw["linear_node_xyz"], dtype=float)
    node_tags = np.asarray(raw["node_tags"], dtype=np.int64)
    node_xyz = np.asarray(raw["node_xyz"], dtype=float)
    linear_element_tags = np.asarray(raw["linear_element_tags"], dtype=np.int64)
    linear_tet4 = np.asarray(raw["linear_tet4_connectivity"], dtype=np.int64)
    tet10_element_tags = np.asarray(raw["tet10_element_tags"], dtype=np.int64)
    tet10 = np.asarray(raw["tet10_connectivity"], dtype=np.int64)
    sicn = np.asarray(raw["linear_sicn"], dtype=float)
    need(linear_node_xyz.shape == (len(linear_node_tags), 3) and len(set(map(int, linear_node_tags))) == len(linear_node_tags), f"linear nodes {screen}")
    need(node_xyz.shape == (len(node_tags), 3) and len(set(map(int, node_tags))) == len(node_tags), f"Tet10 nodes {screen}")
    need(linear_tet4.shape == (len(linear_element_tags), 4) and len(set(map(int, linear_element_tags))) == len(linear_element_tags), f"Tet4 arrays {screen}")
    need(tet10.shape == (int(summary["tet10_elements"]), 10) and len(tet10_element_tags) == len(tet10) and len(set(map(int, tet10_element_tags))) == len(tet10_element_tags), f"Tet10 arrays {screen}")
    need(sicn.shape == (len(linear_tet4),), f"SICN array {screen}")
    linear_xyz = {int(tag): linear_node_xyz[i] for i, tag in enumerate(linear_node_tags)}
    tet10_xyz = {int(tag): node_xyz[i] for i, tag in enumerate(node_tags)}

    corners = rows(run / f"corner-bijection-{summary['variant'].lower()}.csv")
    need(len(corners) == int(summary["vertices"]), f"corner rows {screen}")
    old_to_new = {int(record["old_linear_corner_tag"]): int(record["new_tet10_corner_tag"]) for record in corners}
    old_corner_set = set(map(int, np.unique(linear_tet4)))
    new_corner_set = set(map(int, np.unique(tet10[:, :4])))
    need(len(old_to_new) == len(corners) and set(old_to_new) == old_corner_set and set(old_to_new.values()) == new_corner_set, f"corner sets {screen}")
    distances = []
    for record in corners:
        old = int(record["old_linear_corner_tag"])
        new = int(record["new_tet10_corner_tag"])
        old_point = linear_xyz[old]
        new_point = tet10_xyz[new]
        distance = float(np.linalg.norm(old_point - new_point))
        distances.append(distance)
        need(np.allclose(old_point, [float(record["old_x_mm"]), float(record["old_y_mm"]), float(record["old_z_mm"])], rtol=0, atol=1e-12), f"old corner XYZ {screen}/{old}")
        need(np.allclose(new_point, [float(record["new_x_mm"]), float(record["new_y_mm"]), float(record["new_z_mm"])], rtol=0, atol=1e-12), f"new corner XYZ {screen}/{new}")
        need(close(record["distance_mm"], distance, atol=1e-15, rtol=1e-12) and record["within_tolerance"] == str(distance <= 1e-9), f"corner distance {screen}/{old}")
    need(close(max(distances), summary["corner_bijection_max_distance_mm"], atol=1e-15) and max(distances) <= float(summary["corner_bijection_tolerance_mm"]), f"corner summary {screen}")
    need(int(summary["corner_bijection_unique_targets"]) == len(new_corner_set) and summary["corner_bijection_gate"] == "PASS", f"corner gate {screen}")

    elements = rows(run / f"element-corner-identity-{summary['variant'].lower()}.csv")
    old_elements = {int(tag): linear_tet4[i] for i, tag in enumerate(linear_element_tags)}
    new_elements = {int(tag): tet10[i, :4] for i, tag in enumerate(tet10_element_tags)}
    element_rows = {int(record["element_tag"]): record for record in elements}
    need(set(element_rows) == set(old_elements) == set(new_elements), f"element tag sets {screen}")
    for tag, record in element_rows.items():
        old_nodes = old_elements[tag]
        new_nodes = new_elements[tag]
        mapped = np.asarray([old_to_new[int(node)] for node in old_nodes], dtype=np.int64)
        connectivity_ok = bool(np.array_equal(mapped, new_nodes))
        old_points = np.vstack([linear_xyz[int(node)] for node in old_nodes])
        new_points = np.vstack([tet10_xyz[int(node)] for node in new_nodes])
        old_det = float(np.linalg.det(np.stack((old_points[1] - old_points[0], old_points[2] - old_points[0], old_points[3] - old_points[0]), axis=1)))
        new_det = float(np.linalg.det(np.stack((new_points[1] - new_points[0], new_points[2] - new_points[0], new_points[3] - new_points[0]), axis=1)))
        orientation_ok = old_det * new_det > 0
        need(record["corner_connectivity_preserved"] == str(connectivity_ok) and record["orientation_preserved"] == str(orientation_ok), f"element flags {screen}/{tag}")
        need(close(record["linear_corner_det"], old_det) and close(record["tet10_corner_det"], new_det), f"element determinant {screen}/{tag}")
    need(summary["element_corner_connectivity_gate"] == "PASS" and summary["element_corner_orientation_gate"] == "PASS", f"element gates {screen}")

    membership = {record["entity_group"]: record for record in rows(run / f"occ-corner-membership-{summary['variant'].lower()}.csv")}
    need(set(membership) == {"holes", "pocket_edge", "pocket_floor", "metal_face"}, f"OCC groups {screen}")
    for group, record in membership.items():
        pre = set(map(int, raw[f"pre_entity_nodes_{group}"]))
        post = set(map(int, raw[f"post_entity_nodes_{group}"]))
        old_group_corners = pre & old_corner_set
        mapped_group = {old_to_new[tag] for tag in old_group_corners}
        membership_ok = mapped_group <= post
        need(int(record["old_corner_nodes"]) == len(old_group_corners) and int(record["mapped_new_corner_nodes"]) == len(mapped_group) and int(record["post_entity_nodes_total"]) == len(post), f"OCC counts {screen}/{group}")
        need(record["mapped_corner_membership_preserved"] == str(membership_ok) and membership_ok, f"OCC membership {screen}/{group}")
    need(summary["occ_corner_membership_gate"] == "PASS", f"OCC gate {screen}")

    raw_edge_midtags: dict[tuple[int, int], int] = {}
    shared_midtag_conflicts = 0
    for tet in tet10:
        for a, b, midpoint in TET10_EDGES:
            key = tuple(sorted((int(tet[a]), int(tet[b]))))
            tag = int(tet[midpoint])
            if key in raw_edge_midtags and raw_edge_midtags[key] != tag:
                shared_midtag_conflicts += 1
            else:
                raw_edge_midtags[key] = tag
    need(shared_midtag_conflicts == 0, f"shared midside tag conflicts {screen}")
    edge_records = rows(run / f"edge-map-{summary['variant'].lower()}.csv")
    edge_map = {tuple(sorted((int(record["edge_corner_tag_a"]), int(record["edge_corner_tag_b"])))): record for record in edge_records}
    need(len(edge_map) == len(edge_records) == len(raw_edge_midtags) == int(summary["global_edges"]), f"edge sets {screen}")
    need(set(edge_map) == set(raw_edge_midtags), f"raw edge coverage {screen}")
    need(len({record["gmsh_mid_node_tag"] for record in edge_records}) == len(edge_records), f"midside uniqueness {screen}")

    sorted_corners = sorted(new_corner_set)
    corner_index = {tag: i for i, tag in enumerate(sorted_corners)}
    p = np.vstack([tet10_xyz[tag] for tag in sorted_corners]).T
    t = np.asarray([[corner_index[int(tag)] for tag in tet[:4]] for tet in tet10], dtype=np.int64).T
    linear_mesh = MeshTet(p, t)
    curved_mesh = MeshTet2.from_mesh(linear_mesh)
    doflocs = curved_mesh.doflocs.copy()
    for edge_index, (a, b) in enumerate(curved_mesh.edges.T):
        key = tuple(sorted((sorted_corners[int(a)], sorted_corners[int(b)])))
        record = edge_map[key]
        midtag = int(record["gmsh_mid_node_tag"])
        need(midtag == raw_edge_midtags[key] and midtag in tet10_xyz, f"raw midside tag {screen}/{key}")
        point = tet10_xyz[midtag]
        recorded_point = np.asarray([float(record["transferred_x_mm"]), float(record["transferred_y_mm"]), float(record["transferred_z_mm"])])
        need(np.allclose(point, recorded_point, rtol=0, atol=1e-12), f"midside XYZ {screen}/{key}")
        dof = int(curved_mesh.dofs.edge_dofs[0, edge_index])
        need(int(record["scikit_geometry_dof"]) == dof, f"scikit edge DOF {screen}/{key}")
        midpoint_shift = float(np.linalg.norm(point - (doflocs[:, int(a)] + doflocs[:, int(b)]) / 2.0))
        need(close(record["midpoint_shift_mm"], midpoint_shift), f"midpoint shift {screen}/{key}")
        doflocs[:, dof] = point
    curved_mesh = MeshTet2(doflocs, curved_mesh.t)
    need(int(summary["mapped_edges"]) == len(edge_records) and int(summary["missing_edges"]) == 0, f"edge summary {screen}")
    need(close(summary["adjacent_midnode_consistency_max_mm"], 0.0, atol=1e-15), f"edge consistency summary {screen}")

    minimum_sicn = float(np.min(sicn))
    fraction_low = float(np.mean(sicn < 0.20))
    linear_gate = minimum_sicn >= 0.10 and fraction_low <= 0.001
    need(close(summary["minimum_linear_sicn"], minimum_sicn, atol=1e-15) and close(summary["fraction_linear_sicn_below_0p20"], fraction_low, atol=1e-15), f"SICN summary {screen}")
    need(summary["linear_sicn_gate"] == ("PASS" if linear_gate else "FAIL"), f"SICN gate {screen}")

    jacobian_rows = {int(record["quadrature_order"]): record for record in rows(run / "jacobian-screen-register.csv")}
    need(set(jacobian_rows) == {4, 6, 8}, f"quadrature orders {screen}")
    wrong_total = 0
    normalized_fail_total = 0
    points_total = 0
    minimum_oriented = float("inf")
    minimum_normalized = float("inf")
    all_jacobian_pass = True
    for order, record in jacobian_rows.items():
        X, _ = get_quadrature_tet(order)
        linear_det = np.asarray(linear_mesh.mapping().detDF(X))
        curved_det = np.asarray(curved_mesh.mapping().detDF(X))
        oriented = curved_det * np.where(linear_det >= 0.0, 1.0, -1.0)
        curved_df = np.asarray(curved_mesh.mapping().DF(X))
        frobenius = np.sqrt(np.sum(curved_df * curved_df, axis=(0, 1)))
        normalized = oriented / np.maximum(frobenius**3, np.finfo(float).tiny)
        linear_floor = float(record["linear_abs_det_floor"])
        normalized_gate = float(record["normalized_determinant_gate"])
        linear_small = int(np.count_nonzero(np.abs(linear_det) <= linear_floor))
        wrong = int(np.count_nonzero(oriented <= 0.0))
        normalized_fail = int(np.count_nonzero(normalized <= normalized_gate))
        passed = linear_small == 0 and wrong == 0 and normalized_fail == 0
        need(int(record["quadrature_points"]) == curved_det.size, f"quadrature points {screen}/q{order}")
        need(int(record["linear_abs_det_below_floor"]) == linear_small and int(record["curved_wrong_or_zero"]) == wrong and int(record["normalized_determinant_fail_count"]) == normalized_fail, f"Jacobian counts {screen}/q{order}")
        need(close(record["curved_wrong_or_zero_fraction"], wrong / curved_det.size, atol=1e-15), f"Jacobian fraction {screen}/q{order}")
        need(close(record["minimum_oriented_curved_jacobian"], float(np.min(oriented))) and close(record["maximum_oriented_curved_jacobian"], float(np.max(oriented))), f"Jacobian extrema {screen}/q{order}")
        need(close(record["minimum_normalized_determinant"], float(np.min(normalized))) and record["gate"] == ("PASS" if passed else "FAIL"), f"normalized determinant {screen}/q{order}")
        wrong_total += wrong
        normalized_fail_total += normalized_fail
        points_total += curved_det.size
        minimum_oriented = min(minimum_oriented, float(np.min(oriented)))
        minimum_normalized = min(minimum_normalized, float(np.min(normalized)))
        all_jacobian_pass = all_jacobian_pass and passed
    need(wrong_total == int(summary["curved_wrong_or_zero_across_screens"]) and normalized_fail_total == int(summary["normalized_determinant_fail_across_screens"]) and points_total == int(summary["curved_quadrature_points_across_screens"]), f"Jacobian totals {screen}")
    need(close(summary["minimum_oriented_curved_jacobian_across_screens"], minimum_oriented) and close(summary["minimum_normalized_determinant_across_screens"], minimum_normalized), f"Jacobian summary extrema {screen}")
    need(summary["curved_jacobian_gate"] == ("PASS" if all_jacobian_pass else "FAIL"), f"Jacobian gate {screen}")

    expected_pass = bool(linear_gate and all_jacobian_pass)
    need(expected_pass is EXPECTED[screen]["passed"], f"expected disposition {screen}")
    need(summary["bounded_sampled_jacobian_candidate_pass"] == str(expected_pass) and summary["mesh_repair_pass"] == str(expected_pass), f"candidate flags {screen}")
    need(summary["high_order_optimizer"] == "NONE", f"optimizer terminology {screen}")
    need(summary["geometry_identity_evidence"].startswith("linear-corner coordinate/connectivity/orientation"), f"geometry wording {screen}")
    need(summary["r283_h03_disposition"].startswith("PARTIAL/OPEN"), f"H03 boundary {screen}")
    run_status = json.loads((run / "analysis-status.json").read_text(encoding="utf-8"))
    need(run_status["bounded_fixed_corner_sampled_jacobian_candidate_pass"] is expected_pass, f"run status candidate {screen}")
    raw.close()


def main() -> int:
    check_text_identity()
    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == IDENT, "identity")
    need(status["variants_executed"] == 3 and status["passing_variants"] == ["R284-V06-FINE"], "variant disposition")
    for key in ("r279_c02_complete", "mesh_convergence_complete", "r278_h02_closed", "capacity_established", "selected", "safety_credit", "fabrication_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized"):
        need(status[key] is False, f"authority {key}")
    summary_rows = rows(OUT / "variant-summary.csv")
    summary = {record["screen_id"]: record for record in summary_rows}
    need(len(summary_rows) == len(summary) == 3 and set(summary) == set(EXPECTED), "screens")
    for screen, record in summary.items():
        check_run(screen, record)
        need(int(record["curved_wrong_or_zero_across_screens"]) == EXPECTED[screen]["wrong"], f"expected wrong count {screen}")
    check_package_manifest()
    print("PASS: independently reconstructed R284 raw Tet10 transfer/Jacobians; V06 sole bounded candidate; convergence/H02/capacity/authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
