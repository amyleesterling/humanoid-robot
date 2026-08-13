#!/usr/bin/env python3
"""R285 bounded C07 targeted-remesh and repeatability screen.

The screen starts from the R284 V06 no-high-order-optimizer size triplet and
adds exact OCC-local fields for four backside mounting-boss cylinders, their
topological rim curves, and the two outer top rail-transition cylinders and
boundary curves identified by the retained R284 localization evidence.

This is meshing-method evidence only.  It grants no R279-C02, H02, capacity,
safety, fabrication, powered-test, motion, or energization credit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import gmsh
import numpy as np
from skfem.quadrature import get_quadrature_tet

import generate_hr_v0_j2_c07_curved_mesh_repair_p01 as prior
import generate_hr_v0_j2_c07_failure_localization_p01 as localize
import generate_hr_v0_j2_c07_target_feature_identity_p01 as feature
import generate_hr_v0_j2_stop_refinement_execution_p01 as base


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-targeted-remesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-targeted-remesh-p0.1"
IDENT = "HR-V0-J2-C07-TARGETED-REMESH-P0.1"
WARNING = (
    "PRELIMINARY - TARGETED CURVED-MESH METHOD EVIDENCE ONLY - NOT APPROVED "
    "FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)
VARIANT_ID = "R285-CONFIRMATORY-TARGETED-V06-P01"
VARIANT = prior.Variant(VARIANT_ID, 3.0, 0.50, 0.75, 1, "Netgen", "")
RUN_IDS = ("run-a", "run-b-repeat", "run-c-repeat")
ORIGINAL_ENTITY_REGISTER = base.entity_register
ORIGINAL_ADD_THRESHOLD = base.add_threshold
TARGET_GROUPS: dict[str, list[int]] = {}
TARGET_ROWS: list[dict[str, object]] = []
FEATURE_SOURCE = ROOT / "mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near(value: float, target: float, tolerance: float = 2e-3) -> bool:
    return abs(value - target) <= tolerance


def signature(dim: int, tag: int) -> dict[str, object]:
    return {
        "dimension": dim,
        "tag": tag,
        "type": gmsh.model.getType(dim, tag),
        "bbox_mm": [round(float(x), 9) for x in gmsh.model.getBoundingBox(dim, tag)],
    }


def target_entity_register(part: str):
    global TARGET_GROUPS, TARGET_ROWS
    entities, groups = ORIGINAL_ENTITY_REGISTER(part)
    if part != "C07":
        return entities, groups
    prereg = json.loads((FEATURE_SOURCE / "factor-model-feature-preregistration.json").read_text(encoding="utf-8"))
    if prereg["step_sha256"] != sha(prior.STEP):
        raise RuntimeError("feature preregistration STEP identity mismatch")
    with (FEATURE_SOURCE / "exact-feature-identity-register.csv").open(newline="", encoding="utf-8-sig") as stream:
        frozen_rows = list(csv.DictReader(stream))
    selected_faces = feature.select_faces()
    resolved: dict[str, list[int]] = {}
    resolved_rows = []
    for face_group, faces in selected_faces.items():
        expected_faces = prereg["groups"][face_group]
        face_map = {}
        for face in faces:
            face_sig, _ = feature.face_signature(face)
            if face_sig not in expected_faces["geometric_signatures_sha256"] or face_sig in face_map:
                raise RuntimeError(f"unregistered or duplicate face signature {face_group} {face_sig}")
            face_map[face_sig] = face
        if set(face_map) != set(expected_faces["geometric_signatures_sha256"]):
            raise RuntimeError(f"face signature set mismatch {face_group}")
        curve_group = face_group.replace("_SURFACES", "_BOUNDARY_CURVES")
        expected_curves = prereg["groups"][curve_group]
        curve_map = {}
        for face_sig, face in face_map.items():
            boundary = {tag for dim, tag in gmsh.model.getBoundary([(2, face)], combined=False, oriented=False) if dim == 1}
            for curve in boundary:
                curve_sig, _ = feature.curve_signature(curve)
                key = (face_sig, curve_sig)
                matches = [row for row in frozen_rows if row["feature_group"] == curve_group and
                           row["owner_face_signature_sha256"] == face_sig and
                           row["geometric_signature_sha256"] == curve_sig]
                if len(matches) != 1:
                    raise RuntimeError(f"curve owner/signature mismatch {curve_group} {key}")
                curve_map[curve_sig] = curve
        if set(curve_map) != set(expected_curves["geometric_signatures_sha256"]):
            raise RuntimeError(f"curve signature set mismatch {curve_group}")
        resolved[face_group] = sorted(face_map.values())
        resolved[curve_group] = sorted(curve_map.values())
        for row in frozen_rows:
            if row["feature_group"] in (face_group, curve_group):
                tag = face_map[row["geometric_signature_sha256"]] if row["dimension"] == "2" else curve_map[row["geometric_signature_sha256"]]
                resolved_rows.append({
                    "feature_group": row["feature_group"], "stable_owner": row["stable_owner"],
                    "entity_role": row["entity_role"], "dimension": int(row["dimension"]),
                    "resolved_occ_tag": tag, "geometric_signature_sha256": row["geometric_signature_sha256"],
                    "owner_face_signature_sha256": row["owner_face_signature_sha256"],
                    "geometry_type": row["geometry_type"], "bbox_mm_json": row["bbox_mm_json"],
                    "identity_match": True,
                    "feature_preregistration_sha256": sha(FEATURE_SOURCE / "factor-model-feature-preregistration.json"),
                    "warning": WARNING,
                })
    boss_faces = resolved["BACKSIDE_BOSS_SURFACES"]
    boss_rims = resolved["BACKSIDE_BOSS_BOUNDARY_CURVES"]
    original_bores = resolved["ORIGINAL_BORE_SURFACES"]
    original_bore_rims = resolved["ORIGINAL_BORE_BOUNDARY_CURVES"]
    rail_faces = resolved["TOP_RAIL_TRANSITION_SURFACES"]
    rail_curves = resolved["TOP_RAIL_TRANSITION_BOUNDARY_CURVES"]
    actual_counts = tuple(map(len, (boss_faces, boss_rims, original_bores, original_bore_rims, rail_faces, rail_curves)))
    if actual_counts != (4, 20, 6, 18, 2, 8):
        raise RuntimeError(f"frozen target count mismatch {actual_counts}")
    groups = dict(groups)
    groups.update({
        "backside_boss_cylinders": sorted(boss_faces),
        "backside_boss_rim_curves": boss_rims,
        "original_bore_cylinders": sorted(original_bores),
        "original_bore_boundary_curves": original_bore_rims,
        "rail_transition_cylinders": sorted(rail_faces),
        "rail_transition_curves": rail_curves,
    })
    # The inherited executor applies its 0.75 mm face field through `holes`.
    groups["holes"] = sorted(set(original_bores + boss_faces))
    TARGET_GROUPS = groups
    TARGET_ROWS = resolved_rows
    return entities, groups


def targeted_add_threshold(entities: list[int], dimension: int, size_min: float, size_max: float, dist_max: float) -> int:
    fields = [ORIGINAL_ADD_THRESHOLD(entities, dimension, size_min, size_max, dist_max)]
    if dimension == 2 and set(TARGET_GROUPS.get("backside_boss_cylinders", [])).issubset(set(entities)):
        fields.append(ORIGINAL_ADD_THRESHOLD(TARGET_GROUPS["backside_boss_rim_curves"], 1, 0.75, size_max, 3.0))
        fields.append(ORIGINAL_ADD_THRESHOLD(TARGET_GROUPS["original_bore_boundary_curves"], 1, 0.75, size_max, 3.0))
    if dimension == 1 and set(entities) == set(TARGET_GROUPS.get("pocket_edge", [])):
        fields.append(ORIGINAL_ADD_THRESHOLD(TARGET_GROUPS["rail_transition_cylinders"], 2, 0.50, size_max, 2.5))
        fields.append(ORIGINAL_ADD_THRESHOLD(TARGET_GROUPS["rail_transition_curves"], 1, 0.50, size_max, 2.5))
    if len(fields) == 1:
        return fields[0]
    minimum = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", fields)
    return minimum


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise RuntimeError(f"empty records: {path}")
    fields = []
    for record in records:
        for field in record:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def normalize_run(run: Path) -> None:
    for path in run.glob("*.csv"):
        text = path.read_text(encoding="utf-8")
        text = text.replace(prior.IDENT, IDENT).replace(prior.WARNING, WARNING)
        path.write_text(text, encoding="utf-8")


def execute_run(run_id: str) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    started = datetime.now(timezone.utc)
    run = OUT / run_id
    if run.exists():
        shutil.rmtree(run)
    run.mkdir(parents=True)
    prior.OUT = run
    prior.base.entity_register = target_entity_register
    prior.base.add_threshold = targeted_add_threshold
    try:
        result, quadrature = prior.execute(VARIANT)
        rows = [dict(row) for row in TARGET_ROWS]
    finally:
        prior.base.entity_register = ORIGINAL_ENTITY_REGISTER
        prior.base.add_threshold = ORIGINAL_ADD_THRESHOLD
    normalize_run(run)
    # The inherited executor hashes its edge CSV before R285 normalizes the
    # component identity and warning text.  Recompute the declared hash from
    # the final retained bytes so internal provenance and the manifest agree.
    edge_path = ROOT / str(result["edge_map"])
    result["edge_map_sha256"] = sha(edge_path)
    result.update({
        "identifier": IDENT,
        "round": "R285",
        "run_id": run_id,
        "screen_scope": "bounded targeted-remesh and sampled-Jacobian method evidence only",
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "work_authority": False,
        "selected": False,
        "warning": WARNING,
    })
    for row in quadrature:
        row.update({"identifier": IDENT, "round": "R285", "run_id": run_id, "warning": WARNING})
    write_csv(run / "variant-register.csv", [result])
    write_csv(run / "jacobian-screen-register.csv", quadrature)
    write_csv(run / "exact-target-entity-register.csv", rows)
    (run / "analysis-status.json").write_text(json.dumps({
        "identifier": IDENT, "round": "R285", "variant_id": VARIANT_ID, "run_id": run_id,
        "mesh_repair_pass": bool(result["mesh_repair_pass"]), "selected": False,
        "r279_c02_complete": False, "r278_h02_closed": False, "safety_credit": False,
        "capacity_credit": False, "work_authority": False, "fabrication_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (run / "runtime-provenance.json").write_text(json.dumps({
        "identifier": IDENT, "variant_id": VARIANT_ID, "run_id": run_id,
        "started_utc": started.isoformat(), "completed_utc": datetime.now(timezone.utc).isoformat(),
        "command": [sys.executable, Path(__file__).resolve().relative_to(ROOT).as_posix(), "--single-run", run_id],
        "fresh_python_process": True, "python_executable": sys.executable,
        "python_version": platform.python_version(), "gmsh_version": importlib.metadata.version("gmsh"),
        "numpy_version": importlib.metadata.version("numpy"), "scipy_version": importlib.metadata.version("scipy"),
        "scikit_fem_version": importlib.metadata.version("scikit-fem"),
        "frozen_protocol_sha256": sha(OUT / "frozen-protocol.json"),
        "generator_sha256": sha(Path(__file__).resolve()), "step_sha256": sha(prior.STEP),
        "feature_identity_generator_sha256": sha(Path(feature.__file__).resolve()),
        "feature_identity_checker_sha256": sha(ROOT / "tools/check_hr_v0_j2_c07_target_feature_identity_p01.py"),
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    return result, quadrature, rows


def compare_raw(a: Path, b: Path) -> list[dict[str, object]]:
    za, zb = np.load(a), np.load(b)
    keys = sorted(set(za.files) | set(zb.files))
    records = []
    for key in keys:
        present = key in za.files and key in zb.files
        equal = bool(present and np.array_equal(za[key], zb[key]))
        max_delta = 0.0
        if present and za[key].shape == zb[key].shape and np.issubdtype(za[key].dtype, np.number):
            max_delta = float(np.max(np.abs(za[key].astype(float) - zb[key].astype(float)))) if za[key].size else 0.0
        records.append({"array": key, "present_both": present, "shape_a": str(za[key].shape) if key in za.files else "MISSING",
                        "shape_b": str(zb[key].shape) if key in zb.files else "MISSING", "exactly_equal": equal,
                        "maximum_absolute_delta": max_delta, "warning": WARNING})
    return records


def independently_screen(run_id: str, raw_path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    z = np.load(raw_path)
    linear, curved, _ = localize.reconstruct(z)
    qrows = []
    for order in (4, 6, 8):
        points, _ = get_quadrature_tet(order)
        ld = np.asarray(linear.mapping().detDF(points))
        cd = np.asarray(curved.mapping().detDF(points))
        oriented = cd * np.where(ld >= 0.0, 1.0, -1.0)
        df = np.asarray(curved.mapping().DF(points))
        frobenius = np.sqrt(np.sum(df * df, axis=(0, 1)))
        normalized = oriented / np.maximum(frobenius**3, np.finfo(float).tiny)
        qrows.append({
            "run_id": run_id, "quadrature_order": order, "points": int(oriented.size),
            "wrong_or_zero": int(np.count_nonzero(oriented <= 0.0)),
            "normalized_at_or_below_1e_10": int(np.count_nonzero(normalized <= 1e-10)),
            "minimum_oriented_determinant": float(np.min(oriented)),
            "minimum_normalized_determinant": float(np.min(normalized)),
            "method": "independent reconstruction from retained raw Tet10 connectivity/nodes using localization reconstruct route",
            "scope": "finite sampled-Jacobian evidence; not full-domain positivity or structural quadrature",
            "warning": WARNING,
        })
    sicn = np.asarray(z["linear_sicn"], dtype=float)
    edges = np.asarray([0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00])
    counts, _ = np.histogram(sicn, bins=edges)
    hrows = [{
        "run_id": run_id, "bin_lower_inclusive": float(edges[i]),
        "bin_upper": float(edges[i + 1]), "upper_bound_inclusive": i == len(counts) - 1,
        "count": int(counts[i]), "fraction": float(counts[i] / sicn.size),
        "population": int(sicn.size), "warning": WARNING,
    } for i in range(len(counts))]
    return qrows, hrows


def manifest(directory: Path) -> None:
    records = [{"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path),
                "bytes": path.stat().st_size, "warning": WARNING}
               for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(directory / "file-manifest.csv", records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-run", choices=RUN_IDS)
    args = parser.parse_args()
    if args.single_run:
        if not (OUT / "frozen-protocol.json").is_file():
            raise SystemExit("frozen protocol absent before confirmatory run")
        result, _, _ = execute_run(args.single_run)
        return 0 if result["mesh_repair_pass"] else 2
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    started = datetime.now(timezone.utc)
    frozen_protocol = {
        "identifier": IDENT, "round": "R285", "classification": "CONFIRMATORY METHOD SCREEN",
        "variant_id": VARIANT_ID, "fresh_process_runs": list(RUN_IDS), "step_sha256": sha(prior.STEP),
        "feature_identity_register_sha256": sha(FEATURE_SOURCE / "exact-feature-identity-register.csv"),
        "feature_preregistration_sha256": sha(FEATURE_SOURCE / "factor-model-feature-preregistration.json"),
        "feature_identity_generator_sha256": sha(Path(feature.__file__).resolve()),
        "feature_identity_checker_sha256": sha(ROOT / "tools/check_hr_v0_j2_c07_target_feature_identity_p01.py"),
        "general_num_threads": 1, "algorithm3d": 1, "linear_optimizer": "Netgen", "high_order_optimizer": "NONE",
        "exact_sizes_mm": {"global": 3.0, "pocket": 0.50, "original_hole_faces": 0.75,
                           "backside_boss_faces": 0.75, "backside_boss_rim_curves": 0.75,
                           "rail_transition_faces": 0.50, "rail_transition_curves": 0.50},
        "exact_transition_distances_mm": {"original_hole_and_boss_faces_and_rims": 3.0,
                                           "pocket_and_rail_faces_and_curves": 2.5,
                                           "pocket_floor": 1.5},
        "sampled_quadrature_orders": [4, 6, 8], "normalized_determinant_floor": 1e-10,
        "linear_sicn_minimum": 0.10, "maximum_fraction_linear_sicn_below_0p20": 0.001,
        "fixed_sicn_histogram_edges": [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00],
        "acceptance": "all three runs pass identity, global SICN and finite Q4/Q6/Q8 gates; all retained raw arrays and target signatures repeat exactly",
        "warning": WARNING,
    }
    (OUT / "frozen-protocol.json").write_text(json.dumps(frozen_protocol, indent=2) + "\n", encoding="utf-8")
    subprocesses = []
    for run_id in RUN_IDS:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--single-run", run_id], cwd=ROOT)
        subprocesses.append({"run_id": run_id, "return_code": completed.returncode})
    results = []
    targets = []
    raw_paths = []
    independent_qrows = []
    histogram_rows = []
    for run_id in RUN_IDS:
        with (OUT / run_id / "variant-register.csv").open(newline="", encoding="utf-8-sig") as stream:
            result = next(csv.DictReader(stream))
        results.append(result)
        with (OUT / run_id / "exact-target-entity-register.csv").open(newline="", encoding="utf-8-sig") as stream:
            targets.append(list(csv.DictReader(stream)))
        raw_path = ROOT / result["raw_npz"]
        raw_paths.append(raw_path)
        qrows, hrows = independently_screen(run_id, raw_path)
        independent_qrows.extend(qrows)
        histogram_rows.extend(hrows)
    repeat = []
    for compare_id, other in (("A_TO_B", raw_paths[1]), ("A_TO_C", raw_paths[2])):
        for row in compare_raw(raw_paths[0], other):
            row["comparison_id"] = compare_id
            repeat.append(row)
    repeat_pass = all(bool(row["exactly_equal"]) for row in repeat)
    target_repeat = targets[0] == targets[1] == targets[2]
    independent_pass = all(row["wrong_or_zero"] == 0 and row["normalized_at_or_below_1e_10"] == 0 for row in independent_qrows)
    write_csv(OUT / "repeatability-register.csv", repeat)
    write_csv(OUT / "variant-summary.csv", results)
    write_csv(OUT / "independent-jacobian-register.csv", independent_qrows)
    write_csv(OUT / "global-sicn-histogram.csv", histogram_rows)
    write_csv(OUT / "fresh-process-register.csv", [{**row, "warning": WARNING} for row in subprocesses])
    status = {
        "identifier": IDENT,
        "round": "R285",
        "baseline_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "step_sha256": sha(prior.STEP),
        "variant_id": VARIANT_ID,
        "runs_executed": 3,
        "all_fresh_process_return_codes_zero": all(row["return_code"] == 0 for row in subprocesses),
        "all_runs_pass": all(str(result["mesh_repair_pass"]).lower() == "true" for result in results),
        "independently_reconstructed_q4_q6_q8_pass": independent_pass,
        "raw_arrays_exactly_repeatable": repeat_pass,
        "target_entity_discovery_exactly_repeatable": target_repeat,
        "bounded_targeted_method_screen_pass": bool(all(row["return_code"] == 0 for row in subprocesses) and all(str(result["mesh_repair_pass"]).lower() == "true" for result in results) and independent_pass and repeat_pass and target_repeat),
        "jacobian_evidence_scope": "finite samples at solver-reference tetrahedral Q4/Q6/Q8 rules; not proof over the full curved element domain or future structural assembly quadrature",
        "surface_deviation_from_brep_complete": False,
        "exact_facet_map_complete": False,
        "exact_zone_clipped_histograms_complete": False,
        "full_domain_curved_jacobian_positivity_proven": False,
        "load_boundary_preservation_complete": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "selected": False,
        "safety_credit": False,
        "capacity_credit": False,
        "work_authority": False,
        "fabrication_authorized": False,
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
        "command": [sys.executable, Path(__file__).resolve().relative_to(ROOT).as_posix()],
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "gmsh_version": importlib.metadata.version("gmsh"),
        "numpy_version": importlib.metadata.version("numpy"),
        "scipy_version": importlib.metadata.version("scipy"),
        "scikit_fem_version": importlib.metadata.version("scikit-fem"),
        "general_num_threads": 1,
        "algorithm3d": 1,
        "linear_optimizer": "Netgen",
        "high_order_optimizer": "NONE",
        "variant_id": VARIANT_ID,
        "frozen_protocol_sha256": sha(OUT / "frozen-protocol.json"),
        "fresh_processes": subprocesses,
        "sizes_mm": {"global": 3.0, "pocket": 0.50, "original_holes_and_boss_faces_and_rims": 0.75, "rail_faces_and_curves": 0.50},
        "transition_distances_mm": {"boss_faces_and_rims": 3.0, "rail_faces_and_curves": 2.5},
        "generator_sha256": sha(Path(__file__).resolve()),
        "transitive_r283_generator_sha256": sha(Path(prior.__file__).resolve()),
        "transitive_occ_field_generator_sha256": sha(Path(base.__file__).resolve()),
        "localization_action_sha256": sha(ROOT / "mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1/actionable-meshing-correction.json"),
        "feature_identity_register_sha256": sha(FEATURE_SOURCE / "exact-feature-identity-register.csv"),
        "feature_preregistration_sha256": sha(FEATURE_SOURCE / "factor-model-feature-preregistration.json"),
        "feature_identity_generator_sha256": sha(Path(feature.__file__).resolve()),
        "feature_identity_checker_sha256": sha(ROOT / "tools/check_hr_v0_j2_c07_target_feature_identity_p01.py"),
        "step_sha256": sha(prior.STEP),
        "warning": WARNING,
    }
    (OUT / "execution-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n> **{WARNING}**\n\nR285 applies bounded exact-OCC targeted refinement to the R284 V06 no-high-order-optimizer route and repeats it twice in fresh Python processes. Q4/Q6/Q8 are finite sampled-Jacobian screens, not a proof over each curved element or a structural solve. Exact B-Rep surface deviation, exact facet mapping, exact-zone clipped histograms, full-domain curved-Jacobian positivity, load-boundary preservation, R279-C02, H02, selection, capacity, safety and every work authority remain open.\n",
        encoding="utf-8",
    )
    manifest(OUT)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    manifest(RELEASE)
    print(json.dumps(status, indent=2))
    return 0 if status["bounded_targeted_method_screen_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
