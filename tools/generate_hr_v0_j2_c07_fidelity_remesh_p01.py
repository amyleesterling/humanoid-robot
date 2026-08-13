#!/usr/bin/env python3
"""R287 preregistered C07 surface-fidelity remesh and exact evaluation."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import gmsh

import generate_hr_v0_j2_c07_brep_facet_load_p01 as evaluate
import generate_hr_v0_j2_c07_curved_mesh_repair_p01 as prior
import generate_hr_v0_j2_c07_target_feature_identity_p01 as feature
import generate_hr_v0_j2_c07_targeted_remesh_p01 as r285


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-fidelity-remesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-fidelity-remesh-p0.1"
EVAL = ROOT / "mechanical/analysis/hr-v0-j2-c07-fidelity-remesh-evaluation-p0.1"
EVAL_RELEASE = ROOT / "release/hr-v0/j2-c07-fidelity-remesh-evaluation-p0.1"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-brep-facet-load-p0.1/fidelity-remesh-preregistration.json"
BASELINE_LOAD = ROOT / "mechanical/analysis/hr-v0-j2-c07-brep-facet-load-p0.1/load-boundary-preservation.csv"
IDENT = "HR-V0-J2-C07-FIDELITY-REMESH-P0.1"
EVAL_IDENT = "HR-V0-J2-C07-FIDELITY-REMESH-EVALUATION-P0.1"
WARNING = (
    "PRELIMINARY - TARGETED B-REP FIDELITY REMESH EVIDENCE ONLY - NOT APPROVED "
    "FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)
VARIANT = prior.Variant("R287_FIDELITY_V01", 3.0, 0.50, 0.75, 1, "Netgen", "")
FIDELITY_FACE_SIZE_MM = 0.35
FIDELITY_DISTANCE_MM = 2.5
ORIGINAL_ENTITY_REGISTER = prior.base.entity_register
ORIGINAL_ADD_THRESHOLD = prior.base.add_threshold
FIDELITY_FACES: list[int] = []
FIDELITY_CURVES: list[int] = []
FIDELITY_ROWS: list[dict[str, object]] = []
ASYMMETRIC_ATTEMPT = {
    "attempt_id": "R287-ATTEMPT-01-AS-OBSERVED-ONLY",
    "target_face_count": 21,
    "target_curve_count": 82,
    "tet10_elements": 193604,
    "exterior_quadratic_facets": 43998,
    "raw_npz_sha256": "30c622fa91a6206dfcb786bf6120a1f78ac2e291fe33000198de8a4079460427",
    "maximum_q8_surface_deviation_mm": 0.01456089491278006,
    "remaining_failure_face_signature_sha256": "4cbf4bcf13e61ee9588f4222fdc93585013b190508b7356a26e029e1526e02ec",
    "result": "REJECTED - OBSERVED FAILURE SET WAS NOT X-MIRROR CLOSED",
    "credit": "DIAGNOSTIC ONLY; RAW BYTES NOT PROMOTED",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty controlled table {path}")
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def fidelity_entity_register(part: str):
    global FIDELITY_FACES, FIDELITY_CURVES, FIDELITY_ROWS
    entities, groups = r285.target_entity_register(part)
    if part != "C07":
        return entities, groups
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg["step_sha256"] != sha(prior.STEP) or int(prereg["failing_face_count"]) != 21:
        raise RuntimeError("R286 fidelity preregistration identity/count drift")
    observed = {row["face_signature_sha256"]: dict(row, selection_basis="R286_OBSERVED_OVER_LIMIT") for row in prereg["failing_faces"]}
    all_faces: dict[str, tuple[int, dict[str, object]]] = {}
    for _dim, tag in gmsh.model.getEntities(2):
        signature, detail = feature.face_signature(tag)
        all_faces[signature] = (tag, detail)
    expected = dict(observed)
    for signature, row in observed.items():
        bbox = json.loads(str(row["bbox_mm_json"]))
        mirror_bbox = [-bbox[3], bbox[1], bbox[2], -bbox[0], bbox[4], bbox[5]]
        matches = [
            (candidate_signature, detail)
            for candidate_signature, (_tag, detail) in all_faces.items()
            if detail["geometry_type"] == row["geometry_type"]
            and max(abs(float(a) - float(b)) for a, b in zip(detail["bbox_mm"], mirror_bbox)) < 1e-5
        ]
        if len(matches) != 1:
            raise RuntimeError(f"X-mirror face resolution drift for {signature}: {len(matches)}")
        mirror_signature, mirror_detail = matches[0]
        expected.setdefault(mirror_signature, {
            "face_signature_sha256": mirror_signature,
            "geometry_type": mirror_detail["geometry_type"],
            "bbox_mm_json": json.dumps(mirror_detail["bbox_mm"], separators=(",", ":")),
            "observed_maximum_q8_surface_deviation_mm": "X_MIRROR_CLOSURE",
            "observed_relative_area_error": "X_MIRROR_CLOSURE",
            "selection_basis": "X_MIRROR_CLOSURE",
        })
    if len(expected) != 22:
        raise RuntimeError(f"mirror-closed fidelity face count drift: {len(expected)}")
    resolved: dict[str, int] = {}
    rows: list[dict[str, object]] = []
    curve_tags: set[int] = set()
    for _dim, tag in gmsh.model.getEntities(2):
        signature, detail = feature.face_signature(tag)
        if signature not in expected:
            continue
        if signature in resolved:
            raise RuntimeError(f"duplicate fidelity face signature {signature}")
        resolved[signature] = tag
        boundary = sorted({curve for dim, curve in gmsh.model.getBoundary([(2, tag)], combined=False, oriented=False) if dim == 1})
        curve_tags.update(boundary)
        rows.append({
            "entity_role": "R286_SURFACE_DEVIATION_FAILURE_FACE",
            "dimension": 2,
            "resolved_occ_tag_diagnostic_only": tag,
            "geometric_signature_sha256": signature,
            "geometry_type": detail["geometry_type"],
            "bbox_mm_json": json.dumps(detail["bbox_mm"], separators=(",", ":")),
            "r286_maximum_q8_surface_deviation_mm": expected[signature]["observed_maximum_q8_surface_deviation_mm"],
            "selection_basis": expected[signature].get("selection_basis", "R286_OBSERVED_OVER_LIMIT"),
            "target_size_mm": FIDELITY_FACE_SIZE_MM,
            "warning": WARNING,
        })
    if set(resolved) != set(expected):
        raise RuntimeError(f"R286 fidelity face signature mismatch missing={set(expected)-set(resolved)}")
    for curve in sorted(curve_tags):
        signature, detail = feature.curve_signature(curve)
        rows.append({
            "entity_role": "OWNER_BOUNDARY_CURVE",
            "dimension": 1,
            "resolved_occ_tag_diagnostic_only": curve,
            "geometric_signature_sha256": signature,
            "geometry_type": detail["geometry_type"],
            "bbox_mm_json": json.dumps(detail["bbox_mm"], separators=(",", ":")),
            "r286_maximum_q8_surface_deviation_mm": "OWNER FACE CONTROL",
            "selection_basis": "OWNER_BOUNDARY_OF_MIRROR_CLOSED_FACE_SET",
            "target_size_mm": FIDELITY_FACE_SIZE_MM,
            "warning": WARNING,
        })
    FIDELITY_FACES = sorted(resolved.values())
    FIDELITY_CURVES = sorted(curve_tags)
    FIDELITY_ROWS = rows
    groups = dict(groups)
    groups["fidelity_faces"] = FIDELITY_FACES
    groups["fidelity_owner_boundary_curves"] = FIDELITY_CURVES
    return entities, groups


def fidelity_add_threshold(entities: list[int], dimension: int, size_min: float, size_max: float, dist_max: float) -> int:
    fields = [r285.targeted_add_threshold(entities, dimension, size_min, size_max, dist_max)]
    if dimension == 2 and set(r285.TARGET_GROUPS.get("backside_boss_cylinders", [])).issubset(set(entities)):
        fields.append(ORIGINAL_ADD_THRESHOLD(FIDELITY_FACES, 2, FIDELITY_FACE_SIZE_MM, size_max, FIDELITY_DISTANCE_MM))
        fields.append(ORIGINAL_ADD_THRESHOLD(FIDELITY_CURVES, 1, FIDELITY_FACE_SIZE_MM, size_max, FIDELITY_DISTANCE_MM))
    if len(fields) == 1:
        return fields[0]
    minimum = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", fields)
    return minimum


def normalize_run(run: Path) -> None:
    for path in run.glob("*.csv"):
        text = path.read_text(encoding="utf-8")
        text = text.replace(prior.IDENT, IDENT).replace(prior.WARNING, WARNING)
        path.write_text(text, encoding="utf-8")


def manifest(directory: Path) -> None:
    rows = [
        {"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name != "file-manifest.csv"
    ]
    write_csv(directory / "file-manifest.csv", rows)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    run = OUT / "run-a"
    run.mkdir()
    prior.OUT = run
    prior.base.entity_register = fidelity_entity_register
    prior.base.add_threshold = fidelity_add_threshold
    try:
        result, quadrature = prior.execute(VARIANT)
    finally:
        prior.base.entity_register = ORIGINAL_ENTITY_REGISTER
        prior.base.add_threshold = ORIGINAL_ADD_THRESHOLD
    normalize_run(run)
    raw_path = ROOT / str(result["raw_npz"])
    edge_path = ROOT / str(result["edge_map"])
    result.update({
        "identifier": IDENT,
        "round": "R287",
        "variant": VARIANT.name,
        "fidelity_face_count": len(FIDELITY_FACES),
        "fidelity_owner_boundary_curve_count": len(FIDELITY_CURVES),
        "fidelity_face_size_mm": FIDELITY_FACE_SIZE_MM,
        "fidelity_transition_distance_mm": FIDELITY_DISTANCE_MM,
        "raw_npz_sha256": sha(raw_path),
        "edge_map_sha256": sha(edge_path),
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "work_authority": False,
        "warning": WARNING,
    })
    for row in quadrature:
        row.update({"identifier": IDENT, "round": "R287", "warning": WARNING})
    write_csv(run / "variant-register.csv", [result])
    write_csv(run / "jacobian-screen-register.csv", quadrature)
    write_csv(run / "fidelity-target-entity-register.csv", FIDELITY_ROWS)
    inputs = [
        ("exact C07 STEP", prior.STEP),
        ("R286 fidelity preregistration", PREREG),
        ("R285 frozen protocol", r285.OUT / "frozen-protocol.json"),
        ("R287 generator", Path(__file__).resolve()),
    ]
    write_csv(OUT / "exact-input-register.csv", [
        {"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING}
        for role, path in inputs
    ])
    write_csv(OUT / "failed-attempt-register.csv", [{**ASYMMETRIC_ATTEMPT, "warning": WARNING}])
    mesh_pass = bool(result["mesh_repair_pass"])
    status = {
        "identifier": IDENT,
        "round": "R287",
        "variant": VARIANT.name,
        "fidelity_faces": len(FIDELITY_FACES),
        "fidelity_owner_boundary_curves": len(FIDELITY_CURVES),
        "mesh_identity_sicn_sampled_jacobian_pass": mesh_pass,
        "exact_facet_map_complete": False,
        "surface_deviation_screen_pass": False,
        "next_level_area_drift_complete": False,
        "exact_zone_clipping_complete": False,
        "structural_solution_executed": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n> **{WARNING}**\n\n"
        f"R287 applies the preregistered 0.35 mm field to the X-mirror-closed set of {len(FIDELITY_FACES)} exact "
        "faces (21 R286 failures plus one required mirror counterpart) and "
        f"their {len(FIDELITY_CURVES)} owner-boundary curves while retaining the R285 global, pocket, hole, boss "
        "and rail-transition controls. The exact R286 evaluator is run next; no mesh pass alone grants structural, "
        "capacity, safety or work-authority credit.\n",
        encoding="utf-8",
    )
    manifest(OUT)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)

    evaluate.OUT = EVAL
    evaluate.RELEASE = EVAL_RELEASE
    evaluate.RAW = raw_path
    evaluate.IDENT = EVAL_IDENT
    evaluate.ROUND = "R287"
    evaluate.RAW_LABEL = "R287 fidelity-remesh raw Tet10"
    evaluate.WARNING = WARNING
    evaluate.ADDITIONAL_INPUTS = [
        ("R287 remesh generator", Path(__file__).resolve()),
        ("R286 fidelity preregistration", PREREG),
        ("R287 mesh package manifest", OUT / "file-manifest.csv"),
    ]
    evaluate.main()

    baseline_load = read_rows(BASELINE_LOAD)[0]
    current_load_path = EVAL / "load-boundary-preservation.csv"
    current_load = read_rows(current_load_path)[0]
    baseline_area = float(baseline_load["mesh_curved_clipped_area_mm2"])
    current_area = float(current_load["mesh_curved_clipped_area_mm2"])
    last_pair_drift = abs(current_area - baseline_area) / max(abs(current_area), abs(baseline_area))
    last_pair_pass = last_pair_drift <= 0.001
    current_load.update({
        "previous_mesh_identifier": "R285-CONFIRMATORY-TARGETED-V06-P01",
        "previous_mesh_loaded_area_mm2": baseline_area,
        "last_pair_loaded_area_relative_drift": last_pair_drift,
        "last_pair_area_drift_limit": 0.001,
        "last_pair_area_drift_gate": "PASS" if last_pair_pass else "FAIL",
    })
    write_csv(current_load_path, [current_load])
    eval_status_path = EVAL / "analysis-status.json"
    eval_status = json.loads(eval_status_path.read_text(encoding="utf-8"))
    eval_status.update({
        "next_level_area_drift_complete": True,
        "next_level_area_drift_pass": last_pair_pass,
        "last_pair_loaded_area_relative_drift": last_pair_drift,
    })
    eval_status_path.write_text(json.dumps(eval_status, indent=2) + "\n", encoding="utf-8")
    validation_path = EVAL / "validation-register.csv"
    validation = read_rows(validation_path)
    for row in validation:
        if row["check_id"] == "R287-V07":
            row.update({
                "result": "PASS" if last_pair_pass else "FAIL",
                "evidence": f"R285 {baseline_area} mm2; R287 {current_area} mm2; relative drift {last_pair_drift}",
                "credit": "NEXT-LEVEL LOAD-AREA DRIFT" if last_pair_pass else "NONE",
            })
    write_csv(validation_path, validation)
    evaluate.file_manifest(EVAL)
    if EVAL_RELEASE.exists():
        shutil.rmtree(EVAL_RELEASE)
    EVAL_RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(EVAL, EVAL_RELEASE)
    print(json.dumps({"mesh": status, "evaluation": eval_status}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
