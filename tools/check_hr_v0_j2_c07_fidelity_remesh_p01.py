#!/usr/bin/env python3
"""Checker for the R287 C07 fidelity-remesh and exact evaluation packages."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import generate_hr_v0_j2_c07_brep_facet_load_p01 as eval_gen
import generate_hr_v0_j2_c07_fidelity_remesh_p01 as gen


ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def fail(message: str) -> None:
    raise SystemExit(f"R287 fidelity-remesh check failed: {message}")


def check_package(source: Path, release: Path) -> None:
    source_files = sorted(path.relative_to(source).as_posix() for path in source.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(release).as_posix() for path in release.rglob("*") if path.is_file())
    if source_files != release_files:
        fail(f"source/release file-set mismatch {source.name}")
    for rel in source_files:
        if sha(source / rel) != sha(release / rel):
            fail(f"source/release hash mismatch {source.name}/{rel}")
    manifest = rows(source / "file-manifest.csv")
    actual = [path for path in source.rglob("*") if path.is_file() and path.name != "file-manifest.csv"]
    if len(manifest) != len(actual):
        fail(f"manifest count mismatch {source.name}")
    mapped = {row["relative_path"]: row for row in manifest}
    for path in actual:
        rel = path.relative_to(source).as_posix()
        row = mapped.get(rel)
        if row is None or row["sha256"] != sha(path) or int(row["bytes"]) != path.stat().st_size:
            fail(f"manifest mismatch {source.name}/{rel}")


def main() -> int:
    check_package(gen.OUT, gen.RELEASE)
    check_package(gen.EVAL, gen.EVAL_RELEASE)
    mesh_status = json.loads((gen.OUT / "analysis-status.json").read_text(encoding="utf-8"))
    eval_status = json.loads((gen.EVAL / "analysis-status.json").read_text(encoding="utf-8"))
    if mesh_status["fidelity_faces"] != 22 or mesh_status["fidelity_owner_boundary_curves"] <= 0:
        fail("fidelity target count drift")
    target_rows = rows(gen.OUT / "run-a/fidelity-target-entity-register.csv")
    if sum(row["dimension"] == "2" for row in target_rows) != 22:
        fail("exact target face rows drift")
    prereg = json.loads(gen.PREREG.read_text(encoding="utf-8"))
    observed_signatures = {row["face_signature_sha256"] for row in prereg["failing_faces"]}
    target_face_rows = [row for row in target_rows if row["dimension"] == "2"]
    target_signatures = {row["geometric_signature_sha256"] for row in target_face_rows}
    if not observed_signatures.issubset(target_signatures) or len(target_signatures - observed_signatures) != 1:
        fail("R286-to-R287 mirror-closed face-signature set mismatch")
    if sum(row["selection_basis"] == "X_MIRROR_CLOSURE" for row in target_face_rows) != 1:
        fail("mirror-closure face disposition mismatch")
    attempts = rows(gen.OUT / "failed-attempt-register.csv")
    if len(attempts) != 1 or attempts[0]["result"] != "REJECTED - OBSERVED FAILURE SET WAS NOT X-MIRROR CLOSED":
        fail("asymmetric failed-attempt record drift")
    variant = rows(gen.OUT / "run-a/variant-register.csv")
    if len(variant) != 1:
        fail("variant row count")
    variant = variant[0]
    for key in ("corner_identity_gate", "linear_sicn_gate", "curved_jacobian_gate"):
        if variant[key] != "PASS":
            fail(f"R287 bounded mesh gate failed: {key}")
    raw_path = ROOT / variant["raw_npz"]
    if variant["raw_npz_sha256"] != sha(raw_path):
        fail("R287 raw hash mismatch")
    evidence = np.load(gen.EVAL / "raw-facet-load-evidence.npz")
    raw = np.load(raw_path)
    facets, elements, local = eval_gen.boundary_facets(np.asarray(raw["tet10_connectivity"], dtype=np.int64))
    if not np.array_equal(facets, evidence["facet_node_tags"]):
        fail("evaluation facet reconstruction mismatch")
    if not np.array_equal(elements, evidence["facet_source_element_index"]) or not np.array_equal(local, evidence["facet_local_face"]):
        fail("evaluation facet provenance mismatch")
    if np.any(evidence["facet_mapping_candidate_count"] != 1):
        fail("evaluation exact facet map incomplete")
    observed_surface_pass = bool(float(np.max(evidence["facet_q8_deviation_mm"])) <= eval_gen.SURFACE_DEVIATION_LIMIT_MM)
    if bool(eval_status["surface_deviation_screen_pass"]) != observed_surface_pass:
        fail("surface-deviation disposition mismatch")
    load = rows(gen.EVAL / "load-boundary-preservation.csv")[0]
    for key in ("area_relative_error", "centroid_error_normalized_by_exact_patch_bbox_diagonal", "normalized_moment_drift"):
        if float(load[key]) > float(load[{"area_relative_error":"area_gate_limit", "centroid_error_normalized_by_exact_patch_bbox_diagonal":"location_gate_limit", "normalized_moment_drift":"moment_gate_limit"}[key]]):
            fail(f"load geometry gate failed: {key}")
    baseline_area = float(rows(gen.BASELINE_LOAD)[0]["mesh_curved_clipped_area_mm2"])
    current_area = float(load["mesh_curved_clipped_area_mm2"])
    drift = abs(current_area - baseline_area) / max(abs(current_area), abs(baseline_area))
    if not np.isclose(drift, float(load["last_pair_loaded_area_relative_drift"]), rtol=1e-12, atol=1e-15):
        fail("last-pair loaded-area drift mismatch")
    if bool(eval_status["next_level_area_drift_pass"]) != bool(drift <= 0.001):
        fail("last-pair loaded-area disposition mismatch")
    for status in (mesh_status, eval_status):
        for key in (
            "exact_zone_clipping_complete", "structural_solution_executed", "r279_c02_complete", "r278_h02_closed",
            "capacity_credit", "selected", "safety_credit", "procurement_authorized", "fabrication_authorized",
            "powered_testing_authorized", "motion_authorized", "energization_authorized",
        ):
            if status[key] is not False:
                fail(f"authority/no-credit gate changed {status['identifier']}:{key}")
    print(
        f"PASS: R287 fidelity remesh evidence synchronized; surface_pass={observed_surface_pass}; "
        f"max_deviation_mm={float(np.max(evidence['facet_q8_deviation_mm']))}; "
        "exact zones/structural convergence/R279-C02/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
