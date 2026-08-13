#!/usr/bin/env python3
"""Freeze the R291 successor mesh targets before any mesh execution."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import gmsh


ROOT = Path(__file__).resolve().parents[1]
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
R289 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-zone-mesh-p0.1"
R290 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-mesh-failure-localization-p0.1"
BREP = R288 / "c07-exact-zone-fragmented.brep"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-conformal-successor-prereg-p0.1"
IDENT = "HR-V0-J2-C07-CONFORMAL-SUCCESSOR-PREREG-P0.1"
WARNING = "PRELIMINARY - SUCCESSOR MESH PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
TOL = 2.0e-6


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"empty table: {path}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def face_record(tag: int) -> dict[str, object]:
    bbox = [round(float(value), 9) for value in gmsh.model.getBoundingBox(2, tag)]
    record = {
        "geometry_type": gmsh.model.getType(2, tag), "bbox_mm": bbox,
        "area_mm2": round(float(gmsh.model.occ.getMass(2, tag)), 9),
        "center_mm": [round(float(value), 9) for value in gmsh.model.occ.getCenterOfMass(2, tag)],
    }
    record["geometric_signature_sha256"] = stable(record)
    return record


def mirror_bbox(bbox: list[float]) -> list[float]:
    return [-bbox[3], bbox[1], bbox[2], -bbox[0], bbox[4], bbox[5]]


def close_bbox(a: list[float], b: list[float]) -> bool:
    return all(abs(x - y) <= TOL for x, y in zip(a, b))


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    status290 = json.loads((R290 / "analysis-status.json").read_text(encoding="utf-8"))
    if status290["remesh_executed"] or status290["thresholds_unchanged"] is not True:
        raise RuntimeError("R290 fail-closed successor boundary drift")
    with (R290 / "curved-jacobian-failure-localization.csv").open(newline="", encoding="utf-8") as stream:
        observed = list(csv.DictReader(stream))
    observed_bboxes = []
    for row in observed:
        bbox = json.loads(row["nearest_exact_face_bbox_mm_json"])
        if not any(close_bbox(bbox, prior) for prior in observed_bboxes): observed_bboxes.append(bbox)
    if len(observed_bboxes) != 4:
        raise RuntimeError(f"R290 observed face-cluster count drift: {len(observed_bboxes)}")

    gmsh.initialize(["-nopopup"]); gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.add("R291_PREREG")
        gmsh.model.occ.importShapes(str(BREP)); gmsh.model.occ.synchronize()
        faces = [(tag, face_record(tag)) for dim, tag in gmsh.model.getEntities(2)]
        target_bboxes = list(observed_bboxes)
        for bbox in observed_bboxes:
            mirrored = mirror_bbox(bbox)
            if not any(close_bbox(mirrored, prior) for prior in target_bboxes): target_bboxes.append(mirrored)
        selected = []
        for bbox in target_bboxes:
            matches = [(tag, record) for tag, record in faces if record["geometry_type"] == "Cylinder" and close_bbox(record["bbox_mm"], bbox)]
            if len(matches) != 1: raise RuntimeError(f"exact target face did not resolve uniquely: bbox={bbox} matches={len(matches)}")
            selected.append(matches[0])
        if len(selected) != 6 or len({record["geometric_signature_sha256"] for _tag, record in selected}) != 6:
            raise RuntimeError("symmetry-closed cylinder target set must contain six unique faces")
        rows = []
        for tag, record in sorted(selected, key=lambda item: item[1]["bbox_mm"]):
            basis = "R290_OBSERVED_FAILURE_FACE" if any(close_bbox(record["bbox_mm"], bbox) for bbox in observed_bboxes) else "X_MIRROR_CLOSURE"
            rows.append({
                "target_role": "CURVED_JACOBIAN_LOCAL_REFINEMENT_FACE", "selection_basis": basis,
                "occ_tag_diagnostic_only": tag, "geometric_signature_sha256": record["geometric_signature_sha256"],
                "geometry_type": record["geometry_type"], "bbox_mm_json": json.dumps(record["bbox_mm"], separators=(",", ":")),
                "area_mm2": record["area_mm2"], "center_mm_json": json.dumps(record["center_mm"], separators=(",", ":")),
                "size_min_mm": 0.35, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 2.0,
                "identity_rule": "R288 B-Rep SHA + exact cylinder geometry/bbox/area/center signature; OCC tag diagnostic only",
                "warning": WARNING,
            })
        write_csv(OUT / "exact-face-target-register.csv", rows)
    finally:
        gmsh.finalize()

    volume_targets = ["C07-PE-EAST-STRAIGHT", "C07-PE-NORTH-STRAIGHT", "C07-PE-SOUTH-STRAIGHT", "C07-PE-WEST-STRAIGHT"]
    write_csv(OUT / "exact-volume-target-register.csv", [{
        "exact_zone_id": zone, "selection_basis": "R290_MONITORED_ZONE_MINIMUM_FAILURE",
        "size_min_mm": 0.18, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 0.75,
        "threshold": "R279 monitored-zone min SICN >=0.20 (UNCHANGED)", "warning": WARNING,
    } for zone in volume_targets])
    protocol = {
        "identifier": IDENT, "round": "R291-PREREG", "date": "2026-08-13",
        "r288_brep_sha256": sha(BREP), "r289_status_sha256": sha(R289 / "analysis-status.json"),
        "r290_status_sha256": sha(R290 / "analysis-status.json"),
        "exact_failed_volume_targets": volume_targets, "exact_failed_volume_target_count": 4,
        "symmetry_closed_exact_face_target_count": 6, "observed_face_count": 4, "mirror_closure_face_count": 2,
        "base_prescription": "R289 unchanged: global 3.0; PE/PF/rims 0.25; ligaments 0.40; Algorithm3D=1; Netgen linear optimization; no high-order optimizer",
        "additional_volume_field": {"size_min_mm": 0.18, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 0.75},
        "additional_face_field": {"size_min_mm": 0.35, "size_max_mm": 3.0, "dist_min_mm": 0.0, "dist_max_mm": 2.0},
        "acceptance_thresholds": {"global_min_sicn": 0.10, "global_fraction_below_0p20_max": 0.001, "each_monitored_zone_min_sicn": 0.20, "actual_gauss4_6_8_wrong_or_zero": 0, "actual_gauss4_6_8_normalized_floor_fail": 0},
        "stop_rule": "one execution only; pass only if all unchanged R279-C02 gates pass; otherwise retain failure and localize before another prescription",
        "mesh_executed": False, "r279_c02_complete": False, "r278_h02_closed": False,
        "capacity_credit": False, "safety_credit": False, "work_authority": False, "warning": WARNING,
    }
    (OUT / "frozen-successor-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR291 freezes one successor execution before meshing: four exact failed pocket-straight volumes receive a 0.18 mm local field and the four observed curved-failure cylinder faces are X-mirror-closed to six exact faces receiving a 0.35 mm field. All R279 acceptance thresholds remain unchanged. No mesh has been executed by this package.\n", encoding="utf-8")
    status = {"identifier": IDENT, "round": "R291-PREREG", "exact_volume_targets": 4, "exact_face_targets": 6, "x_mirror_closed": True, "thresholds_unchanged": True, "mesh_executed": False, "r279_c02_complete": False, "r278_h02_closed": False, "capacity_credit": False, "safety_credit": False, "work_authority": False, "warning": WARNING}
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(json.dumps({"generator_sha256": sha(Path(__file__).resolve()), "r288_brep_sha256": sha(BREP), "r289_status_sha256": sha(R289 / "analysis-status.json"), "r290_status_sha256": sha(R290 / "analysis-status.json"), "warning": WARNING}, indent=2) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv": manifest.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
