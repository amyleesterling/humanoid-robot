#!/usr/bin/env python3
"""Freeze the R293 PE-junction linear-mesh method before execution."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R288 = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1"
R291_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
R291_MESH = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
R292 = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-disposition-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-prereg-p0.1"
IDENT = "HR-V0-J2-C07-PE-TOPOLOGY-PREREG-P0.1"
WARNING = (
    "PRELIMINARY - PE-JUNCTION MESH-METHOD PREREGISTRATION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, "
    "MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    boundary_path = R292 / "next-method-boundary.json"
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    prior_protocol_path = R291_PREREG / "frozen-successor-protocol.json"
    prior_protocol = json.loads(prior_protocol_path.read_text(encoding="utf-8"))
    prior_status_path = R291_MESH / "analysis-status.json"
    prior_status = json.loads(prior_status_path.read_text(encoding="utf-8"))
    brep_path = R288 / "c07-exact-zone-fragmented.brep"
    if boundary["next_mesh_executed"] or boundary["r279_c02_complete"]:
        raise RuntimeError("R292 next-method boundary is not fail-closed")
    if "Netgen followed by Relocate3D" not in boundary["required_next_preregistration"]:
        raise RuntimeError("R292 method boundary drift")
    if prior_status["actual_quadrature_signed_jacobian_gate"] is not True:
        raise RuntimeError("R291 retained Jacobian success is absent")
    if prior_status["monitored_zone_minimum_gate"] is not False:
        raise RuntimeError("R291 retained monitored-zone failure is absent")
    if sha(brep_path) != prior_protocol["r288_brep_sha256"]:
        raise RuntimeError("R288 B-Rep identity drift")
    face_register = R291_PREREG / "exact-face-target-register.csv"
    volume_register = R291_PREREG / "exact-volume-target-register.csv"
    with face_register.open(newline="", encoding="utf-8") as stream:
        faces = list(csv.DictReader(stream))
    with volume_register.open(newline="", encoding="utf-8") as stream:
        volumes = list(csv.DictReader(stream))
    if len(faces) != 6 or len(volumes) != 4:
        raise RuntimeError("R291 exact target register drift")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    protocol = {
        "identifier": IDENT,
        "round": "R293-PREREG",
        "date": "2026-08-13",
        "candidate_id": "R293-C07-PE-TOPOLOGY-V01",
        "r288_brep_sha256": sha(brep_path),
        "r291_protocol_sha256": sha(prior_protocol_path),
        "r291_status_sha256": sha(prior_status_path),
        "r292_method_boundary_sha256": sha(boundary_path),
        "exact_volume_target_register_sha256": sha(volume_register),
        "exact_face_target_register_sha256": sha(face_register),
        "exact_volume_target_count": 4,
        "exact_face_target_count": 6,
        "mesh_size_fields": {
            "base": "R289 unchanged: global 3.0 mm; PE/PF/rims 0.25 mm; ligaments 0.40 mm",
            "failed_exact_volume_field": prior_protocol["additional_volume_field"],
            "symmetry_closed_exact_face_field": prior_protocol["additional_face_field"],
        },
        "linear_mesh_method": {
            "algorithm3d": 1,
            "optimizer_sequence": ["Netgen", "Relocate3D"],
            "optimizer_stage": "after linear mesh generation and before Tet10 conversion",
            "general_num_threads": 1,
            "high_order_optimizer": "NONE",
        },
        "acceptance_thresholds": prior_protocol["acceptance_thresholds"],
        "thresholds_unchanged": True,
        "stop_rule": "execute this candidate exactly once; retain and disposition the result without tuning; no structural solve unless every R279-C02 constituent gate passes",
        "mesh_executed": False,
        "structural_solution_executed": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "work_authority": False,
        "warning": WARNING,
    }
    (OUT / "frozen-pe-topology-protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(OUT / "inherited-target-register.csv", [
        {
            "target_kind": "EXACT_FAILED_POCKET_VOLUME",
            "target_id": row["exact_zone_id"],
            "source_register": volume_register.relative_to(ROOT).as_posix(),
            "source_register_sha256": sha(volume_register),
            "size_min_mm": row["size_min_mm"],
            "dist_max_mm": row["dist_max_mm"],
            "warning": WARNING,
        }
        for row in volumes
    ] + [
        {
            "target_kind": "SYMMETRY_CLOSED_EXACT_CYLINDER_FACE",
            "target_id": row["geometric_signature_sha256"],
            "source_register": face_register.relative_to(ROOT).as_posix(),
            "source_register_sha256": sha(face_register),
            "size_min_mm": row["size_min_mm"],
            "dist_max_mm": row["dist_max_mm"],
            "warning": WARNING,
        }
        for row in faces
    ])
    status = {
        "identifier": IDENT,
        "round": "R293-PREREG",
        "candidate_id": protocol["candidate_id"],
        "exact_volume_targets": 4,
        "exact_face_targets": 6,
        "thresholds_unchanged": True,
        "optimizer_sequence": ["Netgen", "Relocate3D"],
        "single_candidate_frozen": True,
        "mesh_executed": False,
        "structural_solution_executed": False,
        "r279_c02_complete": False,
        "r278_h02_closed": False,
        "capacity_credit": False,
        "selected": False,
        "safety_credit": False,
        "work_authority": False,
        "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(json.dumps({
        "identifier": IDENT,
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()),
        "r288_brep_sha256": sha(brep_path),
        "r291_protocol_sha256": sha(prior_protocol_path),
        "r291_status_sha256": sha(prior_status_path),
        "r292_method_boundary_sha256": sha(boundary_path),
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R293 freezes one PE-junction mesh-method candidate before execution. It preserves the exact R288 CAD partition, all R291 size fields and targets, and every acceptance threshold. The only method change is a pre-Tet10 linear optimizer sequence of `Netgen` followed by `Relocate3D`.\n\n"
        "The one-run stop rule forbids result-dependent tuning. No mesh, structural solution, convergence study, capacity decision, or work authority is created here.\n",
        encoding="utf-8",
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv":
            manifest.append({
                "relative_path": path.name,
                "sha256": sha(path),
                "bytes": path.stat().st_size,
                "warning": WARNING,
            })
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
