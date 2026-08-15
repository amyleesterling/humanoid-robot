#!/usr/bin/env python3
"""Execute the single preregistered R291 successor of the failed R289 mesh."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import gmsh


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
R289 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-successor-mesh-p0.1"
IDENT = "HR-V0-J2-C07-CONFORMAL-SUCCESSOR-MESH-P0.1"
ROUND = "R291"
WARNING = "PRELIMINARY - PREREGISTERED CONFORMAL SUCCESSOR MESH EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
TARGET_VOLUMES = {"C07-PE-EAST-STRAIGHT", "C07-PE-NORTH-STRAIGHT", "C07-PE-SOUTH-STRAIGHT", "C07-PE-WEST-STRAIGHT"}
TOL = 2.0e-6


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows: raise RuntimeError(f"empty table: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def close_bbox(a: list[float], b: list[float]) -> bool:
    return all(abs(x-y) <= TOL for x,y in zip(a,b))


def load_base():
    spec = importlib.util.spec_from_file_location("r289_base", BASE_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load R289 generator")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def main() -> int:
    prereg_status = json.loads((PREREG / "analysis-status.json").read_text(encoding="utf-8"))
    protocol = json.loads((PREREG / "frozen-successor-protocol.json").read_text(encoding="utf-8"))
    if prereg_status["mesh_executed"] or not prereg_status["thresholds_unchanged"]:
        raise RuntimeError("R291 prereg status is not fail-closed")
    with (PREREG / "exact-face-target-register.csv").open(newline="", encoding="utf-8") as stream:
        face_targets = list(csv.DictReader(stream))
    if len(face_targets) != 6: raise RuntimeError("R291 prereg face target count drift")
    target_bboxes = [json.loads(row["bbox_mm_json"]) for row in face_targets]

    base = load_base()
    original_add_threshold = base.add_threshold
    resolution_rows: list[dict[str, object]] = []
    call_count = 0

    def successor_add_threshold(surfaces: list[int], size_min: float, dist_max: float) -> int:
        nonlocal call_count
        base_field = original_add_threshold(surfaces, size_min, dist_max)
        call_count += 1
        if call_count != 1: return base_field
        exact_volume_surfaces = set()
        resolved_names = set()
        for dim, physical in gmsh.model.getPhysicalGroups(3):
            name = gmsh.model.getPhysicalName(dim, physical)
            if name not in TARGET_VOLUMES: continue
            resolved_names.add(name)
            volume_tags = gmsh.model.getEntitiesForPhysicalGroup(dim, physical)
            for volume_tag in volume_tags:
                exact_volume_surfaces.update(tag for child_dim, tag in gmsh.model.getBoundary([(3, int(volume_tag))], combined=False, oriented=False) if child_dim == 2)
        if resolved_names != TARGET_VOLUMES or not exact_volume_surfaces:
            raise RuntimeError(f"preregistered exact volume target resolution drift: {sorted(resolved_names)}")
        volume_field = original_add_threshold(sorted(exact_volume_surfaces), 0.18, 0.75)

        exact_face_tags = []
        for target_index, target_bbox in enumerate(target_bboxes, 1):
            matches = []
            for _dim, tag in gmsh.model.getEntities(2):
                if gmsh.model.getType(2, tag) != "Cylinder": continue
                candidate = [float(value) for value in gmsh.model.getBoundingBox(2, tag)]
                if close_bbox(candidate, target_bbox): matches.append(tag)
            if len(matches) != 1: raise RuntimeError(f"preregistered exact face target {target_index} resolved {len(matches)} times")
            tag = matches[0]; exact_face_tags.append(tag)
            resolution_rows.append({
                "target_kind": "EXACT_CYLINDER_FACE", "preregistered_ordinal": target_index,
                "resolved_occ_tag_diagnostic_only": tag, "bbox_mm_json": json.dumps(target_bbox, separators=(",", ":")),
                "size_min_mm": 0.35, "dist_max_mm": 2.0, "resolution_gate": "PASS", "warning": WARNING,
            })
        if len(set(exact_face_tags)) != 6: raise RuntimeError("preregistered face targets are not unique")
        face_field = original_add_threshold(sorted(exact_face_tags), 0.35, 2.0)
        for name in sorted(resolved_names):
            resolution_rows.append({
                "target_kind": "EXACT_FAILED_POCKET_VOLUME", "preregistered_ordinal": name,
                "resolved_occ_tag_diagnostic_only": "PHYSICAL_VOLUME_PROVENANCE",
                "bbox_mm_json": "N/A", "size_min_mm": 0.18, "dist_max_mm": 0.75,
                "resolution_gate": "PASS", "warning": WARNING,
            })
        minimum = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(minimum, "FieldsList", [base_field, volume_field, face_field])
        return minimum

    base.OUT = OUT; base.RELEASE = RELEASE; base.IDENT = IDENT; base.ROUND = ROUND; base.WARNING = WARNING
    base.add_threshold = successor_add_threshold
    return_code = base.main()
    if call_count != 4 or len(resolution_rows) != 10:
        raise RuntimeError(f"successor field execution drift: calls={call_count} resolutions={len(resolution_rows)}")

    status_path = OUT / "analysis-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "candidate_id": "R291-C07-CONFORMAL-SUCCESSOR-V01", "preregistration_sha256": sha(PREREG / "frozen-successor-protocol.json"),
        "preregistered_exact_volume_targets": 4, "preregistered_exact_face_targets": 6,
        "r289_failed_baseline_status_sha256": sha(R289 / "analysis-status.json"),
        "thresholds_unchanged": True, "single_preregistered_execution_complete": True,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_csv(OUT / "successor-field-resolution.csv", resolution_rows)
    shutil.copy2(PREREG / "frozen-successor-protocol.json", OUT / "frozen-successor-protocol.json")
    write_csv(OUT / "failed-baseline-register.csv", [{
        "baseline_id": "R289", "status_sha256": sha(R289 / "analysis-status.json"),
        "global_sicn_gate": True, "monitored_zone_minimum_gate": False,
        "actual_quadrature_signed_jacobian_gate": False, "r279_c02_complete": False,
        "retention": "IMMUTABLE FAILED BASELINE", "warning": WARNING,
    }])
    provenance_path = OUT / "execution-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update({
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()), "transitive_r289_generator_sha256": sha(BASE_PATH),
        "preregistration_path": (PREREG / "frozen-successor-protocol.json").relative_to(ROOT).as_posix(),
        "preregistration_sha256": sha(PREREG / "frozen-successor-protocol.json"),
        "additional_exact_volume_field": protocol["additional_volume_field"],
        "additional_exact_face_field": protocol["additional_face_field"], "warning": WARNING,
    })
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\nR291 executes exactly one preregistered successor to the retained failed R289 mesh. It preserves every R289 setting, adds a 0.18 mm field to the four failed exact pocket-straight volumes, and adds a 0.35 mm field to six symmetry-closed exact cylinder faces. All R279 thresholds are unchanged.\n\nThe result is data-driven. Even a complete R279-C02 mesh-quality pass does not execute structural fields, close H02, establish capacity, or grant any work authority.\n",
        encoding="utf-8",
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv": manifest.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2)); return return_code


if __name__ == "__main__": raise SystemExit(main())
