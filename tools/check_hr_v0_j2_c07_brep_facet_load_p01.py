#!/usr/bin/env python3
"""Fail-closed checker for R286 exact C07 facet/B-Rep/load evidence."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import generate_hr_v0_j2_c07_brep_facet_load_p01 as gen


ROOT = Path(__file__).resolve().parents[1]
OUT = gen.OUT
RELEASE = gen.RELEASE


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def fail(message: str) -> None:
    raise SystemExit(f"R286 facet/B-Rep/load check failed: {message}")


def check_manifest(directory: Path) -> None:
    manifest = rows(directory / "file-manifest.csv")
    actual = sorted(path for path in directory.rglob("*") if path.is_file() and path.name != "file-manifest.csv")
    if len(manifest) != len(actual):
        fail(f"manifest count mismatch {directory}")
    expected = {row["relative_path"]: row for row in manifest}
    if len(expected) != len(manifest):
        fail(f"duplicate manifest paths {directory}")
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        row = expected.get(rel)
        if row is None or row["sha256"] != sha(path) or int(row["bytes"]) != path.stat().st_size:
            fail(f"manifest mismatch {directory}/{rel}")


def main() -> int:
    required = {
        "README.md", "analysis-status.json", "exact-input-register.csv", "execution-provenance.json",
        "face-fidelity-summary.csv", "facet-to-occ-register.csv", "fidelity-remesh-preregistration.json", "file-manifest.csv", "index.html",
        "load-boundary-preservation.csv", "open-holds.csv", "raw-facet-load-evidence.npz", "validation-register.csv",
    }
    if {path.name for path in OUT.iterdir() if path.is_file()} != required:
        fail("source package file set drift")
    if {path.name for path in RELEASE.iterdir() if path.is_file()} != required:
        fail("release package file set drift")
    check_manifest(OUT)
    check_manifest(RELEASE)
    for name in required:
        if sha(OUT / name) != sha(RELEASE / name):
            fail(f"source/release mismatch {name}")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    if status["identifier"] != gen.IDENT or status["warning"] != gen.WARNING:
        fail("status identity/warning drift")
    for key in (
        "next_level_area_drift_complete", "exact_zone_clipping_complete", "full_domain_curved_jacobian_positive",
        "structural_solution_executed", "r279_c02_complete", "r278_h02_closed", "capacity_credit", "selected",
        "safety_credit", "procurement_authorized", "fabrication_authorized", "assembly_authorized",
        "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized",
    ):
        if status[key] is not False:
            fail(f"authority/no-credit gate changed: {key}")

    inputs = rows(OUT / "exact-input-register.csv")
    expected_inputs = {
        gen.STEP.relative_to(ROOT).as_posix(), gen.RAW.relative_to(ROOT).as_posix(),
        (gen.R285 / "frozen-protocol.json").relative_to(ROOT).as_posix(),
        gen.LOAD_SOURCE.relative_to(ROOT).as_posix(), Path(gen.__file__).resolve().relative_to(ROOT).as_posix(),
    }
    if {row["path"] for row in inputs} != expected_inputs:
        fail("exact input set mismatch")
    for row in inputs:
        path = ROOT / row["path"]
        if row["sha256"] != sha(path) or int(row["bytes"]) != path.stat().st_size:
            fail(f"input hash mismatch {row['path']}")

    source_raw = np.load(gen.RAW)
    evidence = np.load(OUT / "raw-facet-load-evidence.npz")
    facet_nodes, facet_elements, facet_local = gen.boundary_facets(np.asarray(source_raw["tet10_connectivity"], dtype=np.int64))
    if not np.array_equal(facet_nodes, evidence["facet_node_tags"]):
        fail("facet-node reconstruction mismatch")
    if not np.array_equal(facet_elements, evidence["facet_source_element_index"]):
        fail("facet source-element reconstruction mismatch")
    if not np.array_equal(facet_local, evidence["facet_local_face"]):
        fail("facet local-face reconstruction mismatch")
    if len(facet_nodes) != 25368 or int(status["exterior_quadratic_facets"]) != len(facet_nodes):
        fail("exterior facet count drift")
    if np.any(evidence["facet_mapping_candidate_count"] != 1):
        fail("facet map is not one-to-one")
    if float(np.max(evidence["facet_node_max_deviation_mm"])) > gen.NODE_FACE_TOL_MM:
        fail("facet node deviation exceeds tolerance")
    observed_surface_pass = bool(float(np.max(evidence["facet_q8_deviation_mm"])) <= gen.SURFACE_DEVIATION_LIMIT_MM)
    if bool(status["surface_deviation_screen_pass"]) != observed_surface_pass:
        fail("Q8 surface-deviation disposition mismatch")

    face_rows = rows(OUT / "face-fidelity-summary.csv")
    if len(face_rows) != int(status["exact_occ_faces"]) or len(face_rows) != 152:
        fail("exact face-count drift")
    if sum(int(row["mapped_quadratic_facets"]) for row in face_rows) != len(facet_nodes):
        fail("face-summary facet population mismatch")
    failing_face_rows = [row for row in face_rows if float(row["maximum_q8_surface_deviation_mm"]) > gen.SURFACE_DEVIATION_LIMIT_MM]
    prereg = json.loads((OUT / "fidelity-remesh-preregistration.json").read_text(encoding="utf-8"))
    if prereg["step_sha256"] != sha(gen.STEP) or prereg["source_raw_sha256"] != sha(gen.RAW):
        fail("fidelity-remesh preregistration source drift")
    if int(prereg["failing_face_count"]) != len(failing_face_rows) or len(failing_face_rows) != 21:
        fail("fidelity-remesh failing-face count drift")
    if {row["face_signature_sha256"] for row in prereg["failing_faces"]} != {row["face_signature_sha256"] for row in failing_face_rows}:
        fail("fidelity-remesh exact face-signature set drift")
    if prereg["successor_distance_field"] != {
        "entities": "all 21 exact failing face signatures plus every exact owner-boundary curve",
        "size_min_mm": 0.35, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 2.5,
        "classification": "PRE-REGISTERED BOUNDED DIAGNOSTIC RETRY; NOT ACCEPTED PRODUCTION",
    }:
        fail("fidelity-remesh field prescription drift")
    total_exact = sum(float(row["exact_occ_area_mm2"]) for row in face_rows)
    total_mesh = float(np.sum(evidence["facet_area_mm2"]))
    total_relative = abs(total_mesh - total_exact) / total_exact
    if not np.isclose(total_relative, float(status["total_surface_area_relative_error"]), rtol=1e-12, atol=1e-15):
        fail("total surface area summary mismatch")

    load = rows(OUT / "load-boundary-preservation.csv")
    if len(load) != 1:
        fail("load boundary row count")
    load = load[0]
    mesh_area = float(np.sum(evidence["loaded_area_contribution_mm2"]))
    mesh_first = np.sum(evidence["loaded_first_moment_contribution_mm3"], axis=0)
    mesh_centroid = mesh_first / mesh_area
    exact_area, exact_centroid, diagonal = gen.exact_loaded_patch()
    if not np.isclose(mesh_area, float(load["mesh_curved_clipped_area_mm2"]), rtol=1e-12, atol=1e-10):
        fail("mesh loaded area mismatch")
    if not np.isclose(exact_area, float(load["exact_brep_loaded_area_mm2"]), rtol=1e-12, atol=1e-10):
        fail("exact loaded area mismatch")
    if not np.allclose(mesh_centroid, np.asarray(json.loads(load["mesh_centroid_mm_json"])), rtol=1e-12, atol=1e-10):
        fail("mesh loaded centroid mismatch")
    if not np.allclose(exact_centroid, np.asarray(json.loads(load["exact_centroid_mm_json"])), rtol=1e-12, atol=1e-10):
        fail("exact loaded centroid mismatch")
    area_error = abs(mesh_area - exact_area) / exact_area
    location_error = np.linalg.norm(mesh_centroid - exact_centroid) / np.linalg.norm(diagonal)
    exact_moment = np.cross(exact_centroid, gen.LOAD_FORCE_N)
    mesh_moment = np.cross(mesh_centroid, gen.LOAD_FORCE_N)
    moment_scale = max(np.linalg.norm(exact_moment), np.linalg.norm(gen.LOAD_FORCE_N) * np.linalg.norm(diagonal))
    moment_error = np.linalg.norm(mesh_moment - exact_moment) / moment_scale
    if not np.isclose(area_error, float(load["area_relative_error"]), rtol=1e-12, atol=1e-15):
        fail("area-error recomputation mismatch")
    if not np.isclose(location_error, float(load["centroid_error_normalized_by_exact_patch_bbox_diagonal"]), rtol=1e-12, atol=1e-15):
        fail("location-error recomputation mismatch")
    if not np.isclose(moment_error, float(load["normalized_moment_drift"]), rtol=1e-12, atol=1e-15):
        fail("moment-error recomputation mismatch")
    if area_error > gen.LOAD_AREA_REL_LIMIT or location_error > gen.LOAD_LOCATION_REL_LIMIT or moment_error > gen.LOAD_MOMENT_REL_LIMIT:
        fail("single-level load-geometry gate failed")
    if load["last_pair_area_drift_gate"] != "NOT EXECUTED - REQUIRES NEXT VALID REFINEMENT LEVEL":
        fail("last-pair hold language drift")

    for path in OUT.iterdir():
        if path.suffix in (".csv", ".json", ".md", ".html"):
            text = path.read_text(encoding="utf-8-sig")
            if gen.WARNING not in text:
                fail(f"warning absent from {path.name}")
    print(
        "PASS: R286 evidence synchronized; exact facet map and single-level load geometry pass, "
        "0.005 mm surface-deviation screen fails; next-level drift/exact zones/structural convergence/"
        "R279-C02/H02/capacity/all authority open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
