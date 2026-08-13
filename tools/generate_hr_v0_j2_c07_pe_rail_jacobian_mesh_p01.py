#!/usr/bin/env python3
"""Execute the single preregistered R302 rail-transition Jacobian successor."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import gmsh
import numpy as np

from hr_v0_mesh_raw_shards import LINEAR_KEYS, TET10_KEYS, load_shards, split_raw

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py"
BASE = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-prereg-p0.1"
BORE_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-prereg-p0.1"
R300 = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-rail-jacobian-mesh-p0.1"
IDENT = "HR-V0-J2-C07-PE-RAIL-JACOBIAN-MESH-P0.1"
ROUND = "R303"
WARNING = "PRELIMINARY - PREREGISTERED RAIL-TRANSITION JACOBIAN SUCCESSOR EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
TOL = 2e-6


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, data: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in data:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_prior():
    spec = importlib.util.spec_from_file_location("r298_for_r303", PRIOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R298 generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def close(a: list[float], b: list[float]) -> bool:
    return all(abs(x - y) <= TOL for x, y in zip(a, b))


def resolve_cylinders(bboxes: list[list[float]], role: str) -> tuple[list[int], list[dict[str, object]]]:
    resolved: list[int] = []
    rows: list[dict[str, object]] = []
    for ordinal, bbox in enumerate(bboxes, 1):
        matches = [
            tag
            for _dimension, tag in gmsh.model.getEntities(2)
            if gmsh.model.getType(2, tag) == "Cylinder"
            and close([float(value) for value in gmsh.model.getBoundingBox(2, tag)], bbox)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"{role} {ordinal} resolved {len(matches)}")
        resolved.append(matches[0])
        rows.append(
            {
                "role": role,
                "ordinal": ordinal,
                "resolved_occ_tag_diagnostic_only": matches[0],
                "bbox_mm_json": json.dumps(bbox, separators=(",", ":")),
                "size_min_mm": 0.25,
                "dist_max_mm": 1.5,
                "gate": "PASS",
                "warning": WARNING,
            }
        )
    if len(set(resolved)) != len(resolved):
        raise RuntimeError(f"{role} targets not unique")
    return resolved, rows


def main() -> int:
    finalize_existing = "--finalize-existing" in sys.argv[1:]
    protocol_path = PREREG / "frozen-rail-jacobian-protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    prereg_status = json.loads((PREREG / "analysis-status.json").read_text(encoding="utf-8"))
    if prereg_status["mesh_executed"] or protocol["candidate_id"] != "R302-C07-PE-RAIL-JACOBIAN-V01":
        raise RuntimeError("R302 prereg state")

    bore_target_path = BORE_PREREG / "exact-bore-wall-target-register.csv"
    rail_target_path = PREREG / "exact-rail-transition-target-register.csv"
    bore_bboxes = [json.loads(row["bbox_mm_json"]) for row in read_csv(bore_target_path)]
    rail_bboxes = [json.loads(row["bbox_mm_json"]) for row in read_csv(rail_target_path)]
    if len(bore_bboxes) != 4 or len(rail_bboxes) != 2:
        raise RuntimeError("R303 target count")

    lower_calls = 0
    bore_resolution: list[dict[str, object]] = []
    rail_resolution: list[dict[str, object]] = []

    def load_base_with_successor_fields():
        base = original_load()
        original_add = base.add_threshold

        def add_threshold(surfaces: list[int], size_min: float, dist_max: float) -> int:
            nonlocal lower_calls
            field = original_add(surfaces, size_min, dist_max)
            lower_calls += 1
            if lower_calls != 1:
                return field
            bore_faces, bore_rows = resolve_cylinders(bore_bboxes, "H1-H4 BORE WALL")
            rail_faces, rail_rows = resolve_cylinders(rail_bboxes, "X-MIRRORED RAIL TRANSITION")
            if set(bore_faces) & set(rail_faces):
                raise RuntimeError("bore and rail targets overlap")
            bore_resolution.extend(bore_rows)
            rail_resolution.extend(rail_rows)
            bore_field = original_add(sorted(bore_faces), 0.25, 1.5)
            rail_field = original_add(sorted(rail_faces), 0.25, 1.5)
            minimum = gmsh.model.mesh.field.add("Min")
            gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", [field, bore_field, rail_field])
            return minimum

        base.add_threshold = add_threshold
        return base

    if finalize_existing:
        required_existing = {
            "analysis-status.json",
            "actual-quadrature-jacobian-register.csv",
            "bore-wall-field-resolution.csv",
            "rail-transition-field-resolution.csv",
            "raw-conformal-zone-mesh.npz",
        }
        if not required_existing.issubset({path.name for path in OUT.iterdir()}):
            raise RuntimeError("incomplete R303 execution evidence; refusing finalize-only mode")
        bore_resolution = [dict(row) for row in read_csv(OUT / "bore-wall-field-resolution.csv")]
        rail_resolution = [dict(row) for row in read_csv(OUT / "rail-transition-field-resolution.csv")]
        executed_status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
        code = 0 if executed_status["actual_quadrature_signed_jacobian_gate"] else 1
    else:
        prior = load_prior()
        original_load = prior.load_base
        prior.load_base = load_base_with_successor_fields
        prior.OUT = OUT
        prior.RELEASE = RELEASE
        prior.IDENT = IDENT
        prior.ROUND = ROUND
        prior.WARNING = WARNING
        code = prior.main()
        if lower_calls != 6 or len(bore_resolution) != 4 or len(rail_resolution) != 2:
            raise RuntimeError(
                f"R303 field execution drift calls={lower_calls} bore={len(bore_resolution)} rail={len(rail_resolution)}"
            )

    old_protocol = OUT / "frozen-seam-free-mesh-protocol.json"
    if old_protocol.exists():
        old_protocol.unlink()
    shutil.copy2(protocol_path, OUT / "frozen-rail-jacobian-protocol.json")
    write_csv(OUT / "bore-wall-field-resolution.csv", bore_resolution)
    write_csv(OUT / "rail-transition-field-resolution.csv", rail_resolution)

    raw_candidates = [OUT / "raw-conformal-zone-mesh.npz", OUT / "raw-mesh.npz"]
    raw_paths = [path for path in raw_candidates if path.exists()]
    if len(raw_paths) != 1:
        raise RuntimeError(f"expected one monolithic raw evidence file, found {[path.name for path in raw_paths]}")
    raw_path = raw_paths[0]
    original_raw_sha = sha(raw_path)
    linear_path = OUT / "raw-linear-mesh.npz"
    tet10_path = OUT / "raw-tet10-mesh.npz"
    split_raw(raw_path, linear_path, tet10_path)
    with np.load(raw_path) as original:
        reconstructed = load_shards(OUT)
        expected_keys = LINEAR_KEYS + TET10_KEYS
        if tuple(original.files) != expected_keys or any(
            not np.array_equal(original[key], reconstructed[key]) for key in expected_keys
        ):
            raise RuntimeError("lossless shard verification failed")
    raw_path.unlink()

    status_path = OUT / "analysis-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    sampled_candidate = bool(
        status["global_sicn_gate"]
        and status["monitored_zone_minimum_gate"]
        and status["actual_quadrature_signed_jacobian_gate"]
    )
    status.update(
        {
            "identifier": IDENT,
            "round": ROUND,
            "candidate_id": protocol["candidate_id"],
            "preregistration_sha256": sha(protocol_path),
            "r300_current_status_sha256": sha(R300 / "analysis-status.json"),
            "inherited_bore_wall_face_targets": 4,
            "additional_rail_transition_face_targets": 2,
            "bore_wall_size_min_mm": 0.25,
            "rail_transition_size_min_mm": 0.25,
            "field_dist_max_mm": 1.5,
            "thresholds_unchanged": True,
            "single_preregistered_execution_complete": True,
            "sampled_mesh_quality_candidate_pass": sampled_candidate,
            "r279_c02_complete": False,
            "r279_c02_completion_hold": "Q4/Q6/Q8 are finite samples; full-reference-domain positive Jacobian and independent numerical acceptance remain open",
            "raw_evidence_layout": "LOSSLESS TWO-SHARD NPZ",
            "raw_evidence_original_sha256": original_raw_sha,
            "raw_linear_mesh_sha256": sha(linear_path),
            "raw_tet10_mesh_sha256": sha(tet10_path),
            "raw_shard_array_count": len(LINEAR_KEYS + TET10_KEYS),
            "warning": WARNING,
        }
    )
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    provenance_path = OUT / "execution-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update(
        {
            "identifier": IDENT,
            "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "generator_sha256": sha(Path(__file__).resolve()),
            "transitive_r298_generator_sha256": sha(PRIOR),
            "transitive_r289_generator_sha256": sha(BASE),
            "preregistration_path": protocol_path.relative_to(ROOT).as_posix(),
            "preregistration_sha256": sha(protocol_path),
            "bore_target_register_sha256": sha(bore_target_path),
            "rail_target_register_sha256": sha(rail_target_path),
            "r300_current_status_sha256": sha(R300 / "analysis-status.json"),
            "inherited_bore_wall_field": {"size_min_mm": 0.25, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 1.5},
            "additional_rail_transition_field": protocol["additional_face_field"],
            "raw_evidence_layout": "LOSSLESS TWO-SHARD NPZ",
            "raw_evidence_original_sha256": original_raw_sha,
            "raw_linear_mesh_sha256": sha(linear_path),
            "raw_tet10_mesh_sha256": sha(tet10_path),
            "raw_shard_helper_sha256": sha(ROOT / "tools/hr_v0_mesh_raw_shards.py"),
            "raw_shard_array_keys": list(LINEAR_KEYS + TET10_KEYS),
            "warning": WARNING,
        }
    )
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    status_text = "passes" if sampled_candidate else "does not pass"
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R303 executes exactly one R302-preregistered successor to R300. The only new field is the frozen "
        "0.25 mm / 1.5 mm field on the R301-localized rail-transition cylinder and its exact X mirror. "
        "The R300 H1-H4 bore-wall field, seam-free partition, Frontal+Netgen method, all prior fields, and "
        f"all thresholds remain unchanged. The resulting finite sampled mesh-quality candidate {status_text}.\n\n"
        "Even a sampled gate pass does not prove full-reference-domain curved-element positivity, close R279-C02 "
        "or H02, establish capacity, or grant any physical-work authority.\n",
        encoding="utf-8",
    )

    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
            manifest.append(
                {"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
            )
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
