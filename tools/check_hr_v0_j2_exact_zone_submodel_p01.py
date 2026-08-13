#!/usr/bin/env python3
"""Fail-closed checks for the isolated R283 exact-zone prototype."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import cadquery as cq
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-exact-zone-submodel-architecture-p0.1"
RELEASE_OUT = ROOT / "release/hr-v0/j2-exact-zone-submodel-architecture-p0.1"


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(OUT.is_dir(), "R283 output missing")
    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-EXACT-ZONE-SUBMODEL-ARCH-P0.1", "identity")
    need(status["round"] == "R283-PROTOTYPE", "round")
    for key in (
        "exact_step_identity_bound", "topology_signature_prototype_pass",
        "exact_occ_distance_prototype_pass", "exact_solid_plane_intersection_prototype_pass",
        "direct_quadrature_statistics_method_test_pass", "frozen_probe_definition_pass",
        "raw_run_manifest_schema_issued",
    ):
        need(status[key] is True, key)
    for key in (
        "exact_clipped_cell_zone_execution_complete", "structural_solution_executed",
        "submodel_transfer_executed", "mesh_convergence_complete", "r278_h02_closed",
        "capacity_established", "selected", "fabrication_authorized",
        "powered_testing_authorized", "motion_authorized", "energization_authorized",
        "safety_credit",
    ):
        need(status[key] is False, f"fail-closed flag {key}")

    entities = rows(OUT / "entity-signature-register.csv")
    grouped = {}
    for row in entities:
        grouped.setdefault(row["zone_group"], []).append(row)
    need({key: len(value) for key, value in grouped.items()} == {"C06-RR-PROFILE": 1, "C06-RR-STEP": 4, "C07-PE": 8}, "exact edge counts")
    c07 = grouped["C07-PE"]
    expected_c07_order = ["SOUTH_WEST_CORNER_R2", "WEST_STRAIGHT", "NORTH_WEST_CORNER_R2", "NORTH_STRAIGHT", "NORTH_EAST_CORNER_R2", "EAST_STRAIGHT", "SOUTH_EAST_CORNER_R2", "SOUTH_STRAIGHT"]
    need([row["semantic_class"] for row in c07] == expected_c07_order, "C07 semantic loop order")
    need(sum(row["geometry_type"] == "LINE" for row in c07) == 4, "C07 straight edges")
    need(sum(row["geometry_type"] == "CIRCLE" for row in c07) == 4, "C07 corner arcs")
    need([int(row["closed_loop_ordinal"]) for row in c07] == list(range(1, 9)), "C07 loop ordinals")
    need(all(len(row["loop_successor_geometric_signature_sha256"]) == 64 and len(json.loads(row["shared_endpoint_with_successor_mm_json"])) == 3 for row in c07), "C07 closed endpoint adjacency")
    need(len({row["geometric_edge_signature_sha256"] for row in entities}) == len(entities), "duplicate edge signature")
    need(all(len(row["geometric_edge_signature_sha256"]) == 64 for row in entities), "signature format")
    need(all(json.loads(row["owner_face_wire_adjacency_json"]) for row in entities), "adjacency")
    need(all("OCC traversal index receives no identity credit" in row["identity_rule"] for row in entities), "identity boundary")

    distances = rows(OUT / "exact-distance-prototype.csv")
    edge_points = [row for row in distances if row["point_kind"] == "EXACT_EDGE_PARAMETER"]
    need(edge_points and max(float(row["exact_occ_distance_mm"]) for row in edge_points) <= 1e-7, "exact edge distance")
    need(all(row["membership_at_zone_radius"] == "IN" for row in edge_points), "edge membership")
    remote = [row for row in distances if row["point_kind"] == "DETERMINISTIC_REMOTE_POINT"]
    need(len(remote) == 3 and all(row["membership_at_zone_radius"] == "OUT" for row in remote), "remote exclusion")
    offsets = [row for row in distances if row["point_kind"] == "DETERMINISTIC_OFF_EDGE_POINT"]
    need(len(offsets) == 3 and all(float(row["exact_occ_distance_mm"]) > 1e-5 for row in offsets), "offset distance")
    ties = [row for row in distances if row["point_kind"] == "SHARED_ENDPOINT_TIE"]
    need(ties and all(int(row["equal_minimum_edge_count_at_1e_7_mm"]) >= 2 for row in ties), "tie handling")

    sections = rows(OUT / "section-definition-and-geometry.csv")
    need({row["section_id"] for row in sections} == {"C06-GAUGE-Z18", "C07-GAUGE-X34"}, "sections")
    need(all(float(row["exact_occ_area_mm2"]) > 0 and int(row["planar_face_components"]) > 0 and row["resultant_executed"] == "False" for row in sections), "section boundary")
    need(all(int(row["closed_wire_loops"]) > 0 and int(row["boundary_edge_occurrences"]) > 0 for row in sections), "section topology")
    need(all(len(row["section_geometry_signature_sha256"]) == 64 for row in sections), "section geometry signature")
    need(len({row["section_geometry_signature_sha256"] for row in sections}) == 2, "distinct section geometry signatures")
    need(all(math.isclose(float(row["exact_occ_area_mm2"]), float(row["area_crosscheck_sum_mm2"]), rel_tol=1e-10) for row in sections), "section area crosscheck")
    probes = rows(OUT / "frozen-probe-register.csv")
    need(len(probes) == 5 and all(row["on_exact_named_floor_face_with_plus_y_normal"] == "True" for row in probes), "probes")
    need(all(json.loads(row["exact_floor_face_normal_json"])[1] > 0.999999 for row in probes), "probe face normal")
    need(all(row["field_interpolation_executed"] == "False" for row in probes), "probe field boundary")

    test = rows(OUT / "direct-quadrature-method-test.csv")[0]
    values = [1.0, 2.0, 4.0, 8.0, 16.0]
    weights = [0.5, 1.0, 1.5, 2.0, 3.0]
    expected_mean = sum(v*w for v, w in zip(values, weights))/sum(weights)
    expected_rms = math.sqrt(sum(v*v*w for v, w in zip(values, weights))/sum(weights))
    need(math.isclose(float(test["weighted_mean"]), expected_mean, rel_tol=1e-12), "direct mean")
    need(math.isclose(float(test["weighted_rms"]), expected_rms, rel_tol=1e-12), "direct rms")
    need(test["element_mean_preaverage_used"] == "False" and test["structural_or_capacity_credit"] == "NONE", "stats boundary")

    schema = json.loads((OUT / "raw-run-manifest.schema.json").read_text(encoding="utf-8"))
    template = json.loads((OUT / "raw-run-manifest-template.json").read_text(encoding="utf-8"))
    provenance = json.loads((OUT / "execution-provenance.json").read_text(encoding="utf-8"))
    need(provenance["generator"]["sha256"] == sha(ROOT / provenance["generator"]["path"]), "generator provenance")
    need(provenance["checker"]["sha256"] == sha(ROOT / provenance["checker"]["path"]), "checker provenance")
    shared_paths = {
        "protocol-freeze-register.csv": ROOT / "mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1/protocol-freeze-register.csv",
        "exact-zone-register.csv": ROOT / "mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1/exact-zone-register.csv",
        "execution-architecture.csv": ROOT / "mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1/execution-architecture.csv",
    }
    need(provenance["shared_inputs"] == {name: sha(path) for name, path in shared_paths.items()}, "shared input provenance")
    need(all(provenance["step_inputs"][relative] == sha(ROOT / relative) for relative in provenance["step_inputs"]), "STEP provenance")
    runtime = provenance["runtime"]
    need(Path(runtime["python_executable"]).resolve() == Path(sys.executable).resolve(), "Python executable provenance")
    need(runtime["python_version"] == platform.python_version(), "Python version provenance")
    need(runtime["cadquery_version"] == getattr(cq, "__version__", "UNKNOWN") and runtime["numpy_version"] == np.__version__, "package runtime provenance")
    need(schema["additionalProperties"] is False, "schema closed")
    need(set(schema["required"]).issubset(template), "template fields")
    need(all(value is False for value in template["authority"].values()), "template authority")
    need(schema["properties"]["raw_artifacts"]["minItems"] == 1 and len(template["raw_artifacts"]) == 1, "raw artifact nonempty")
    need("clipped_measure_path" in template["zones"] and "saint_venant_metric_path" in template["transfers"], "submodel evidence schema")
    need(all(key in template["transfers"] for key in ("donor_run_manifest_sha256", "interpolation_method", "force_conservation_relative_error", "moment_conservation_relative_error", "energy_conservation_relative_error", "saint_venant_acceptance_tolerances")), "transfer controls")

    validations = {row["check_id"]: row for row in rows(OUT / "validation-register.csv")}
    need(validations["R283-V07"]["result"] == "NOT EXECUTED", "clipping fail closed")
    need(validations["R283-V08"]["result"] == "NOT EXECUTED", "structural fail closed")
    need(validations["R283-V09"]["result"] == "PASS PROTOTYPE", "C07 perimeter selector")
    need(validations["R283-V10"]["result"] == "NOT EXECUTED", "C06 parametric split fail closed")
    need(len(rows(OUT / "open-holds.csv")) == 6, "open holds")

    manifest = rows(OUT / "file-manifest.csv")
    actual = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    need(len(manifest) == len(actual), "manifest count")
    mapped = {row["relative_path"]: row for row in manifest}
    for path in actual:
        need(path.name in mapped, f"manifest missing {path.name}")
        need(mapped[path.name]["sha256"] == sha(path), f"manifest hash {path.name}")
        need(int(mapped[path.name]["bytes"]) == path.stat().st_size, f"manifest bytes {path.name}")
    need(RELEASE_OUT.is_dir(), "release mirror missing")
    release_actual = sorted(path for path in RELEASE_OUT.iterdir() if path.is_file())
    need({path.name for path in release_actual} == {path.name for path in OUT.iterdir() if path.is_file()}, "release mirror file set")
    for source in sorted(path for path in OUT.iterdir() if path.is_file()):
        need(sha(source) == sha(RELEASE_OUT / source.name), f"release mirror hash {source.name}")
    print("PASS: R283 exact B-Rep distance/section/direct-quadrature architecture prototype; clipping, structural convergence, H02 and all authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
