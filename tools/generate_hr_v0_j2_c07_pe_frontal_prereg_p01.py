#!/usr/bin/env python3
"""Freeze the R295 Frontal tetrahedralization candidate before execution."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R288_BREP = ROOT / "mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1/c07-exact-zone-fragmented.brep"
R291_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
R293_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1/frozen-pe-topology-protocol.json"
R294_BOUNDARY = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-disposition-p0.1/next-method-boundary.json"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-frontal-prereg-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-frontal-prereg-p0.1"
IDENT = "HR-V0-J2-C07-PE-FRONTAL-PREREG-P0.1"
WARNING = (
    "PRELIMINARY - FRONTAL TETRAHEDRALIZATION PREREGISTRATION ONLY - NOT APPROVED "
    "FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED "
    "TESTING, MOTION, OR ENERGIZATION"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    boundary = json.loads(R294_BOUNDARY.read_text(encoding="utf-8"))
    inherited = json.loads(R293_PREREG.read_text(encoding="utf-8"))
    if boundary["next_mesh_executed"] or boundary["next_candidate_id"] != "R295-C07-PE-FRONTAL-V01":
        raise RuntimeError("R294 Frontal boundary drift")
    if "Algorithm3D=4 (Frontal)" not in boundary["required_next_preregistration"]:
        raise RuntimeError("R294 algorithm boundary drift")
    face_register = R291_PREREG / "exact-face-target-register.csv"
    volume_register = R291_PREREG / "exact-volume-target-register.csv"
    with face_register.open(newline="", encoding="utf-8") as stream:
        faces = list(csv.DictReader(stream))
    with volume_register.open(newline="", encoding="utf-8") as stream:
        volumes = list(csv.DictReader(stream))
    if len(faces) != 6 or len(volumes) != 4:
        raise RuntimeError("inherited exact target count drift")
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    protocol = {
        "identifier": IDENT, "round": "R295-PREREG", "date": "2026-08-13",
        "candidate_id": "R295-C07-PE-FRONTAL-V01",
        "r288_brep_sha256": sha(R288_BREP),
        "r293_protocol_sha256": sha(R293_PREREG),
        "r294_method_boundary_sha256": sha(R294_BOUNDARY),
        "exact_volume_target_register_sha256": sha(volume_register),
        "exact_face_target_register_sha256": sha(face_register),
        "exact_volume_target_count": 4, "exact_face_target_count": 6,
        "mesh_size_fields": inherited["mesh_size_fields"],
        "linear_mesh_method": {
            "algorithm3d": 4, "algorithm_name": "Frontal",
            "optimizer_sequence": ["Netgen"],
            "optimizer_stage": "after linear mesh generation and before Tet10 conversion",
            "general_num_threads": 1, "relocate3d": False, "high_order_optimizer": "NONE",
        },
        "acceptance_thresholds": inherited["acceptance_thresholds"],
        "thresholds_unchanged": True,
        "stop_rule": "execute this candidate exactly once; retain and disposition without tuning; do not start a structural solve unless every R279-C02 constituent gate passes",
        "mesh_executed": False, "structural_solution_executed": False,
        "r279_c02_complete": False, "r278_h02_closed": False,
        "capacity_credit": False, "selected": False, "safety_credit": False,
        "work_authority": False, "warning": WARNING,
    }
    (OUT / "frozen-frontal-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    write_csv(OUT / "inherited-target-register.csv", [{
        "target_kind": "EXACT_FAILED_POCKET_VOLUME", "target_id": row["exact_zone_id"],
        "source_sha256": sha(volume_register), "size_min_mm": row["size_min_mm"],
        "dist_max_mm": row["dist_max_mm"], "warning": WARNING,
    } for row in volumes] + [{
        "target_kind": "SYMMETRY_CLOSED_EXACT_CYLINDER_FACE", "target_id": row["geometric_signature_sha256"],
        "source_sha256": sha(face_register), "size_min_mm": row["size_min_mm"],
        "dist_max_mm": row["dist_max_mm"], "warning": WARNING,
    } for row in faces])
    status = {
        "identifier": IDENT, "round": "R295-PREREG", "candidate_id": protocol["candidate_id"],
        "algorithm3d": 4, "algorithm_name": "Frontal", "optimizer_sequence": ["Netgen"],
        "thresholds_unchanged": True, "single_candidate_frozen": True,
        "mesh_executed": False, "structural_solution_executed": False,
        "r279_c02_complete": False, "r278_h02_closed": False,
        "capacity_credit": False, "selected": False, "safety_credit": False,
        "work_authority": False, "warning": WARNING,
    }
    (OUT / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "execution-provenance.json").write_text(json.dumps({
        "identifier": IDENT, "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()), "r288_brep_sha256": sha(R288_BREP),
        "r293_protocol_sha256": sha(R293_PREREG), "r294_method_boundary_sha256": sha(R294_BOUNDARY),
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\nR295 freezes one genuinely different linear tetrahedralization before execution: Gmsh Frontal `Algorithm3D=4`, then Netgen optimization, then Tet10 conversion. Exact CAD, targets, mesh-size fields, thresholds, and single-thread execution remain unchanged. Relocate3D and high-order optimization are prohibited.\n",
        encoding="utf-8",
    )
    manifest=[]
    for path in sorted(OUT.iterdir()):
        if path.name != "file-manifest.csv": manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT / "file-manifest.csv", manifest)
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(OUT, RELEASE)
    print(json.dumps(status, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
