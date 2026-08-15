#!/usr/bin/env python3
"""Execute the single preregistered R293 PE-junction mesh-method candidate."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIOR_GENERATOR = ROOT / "tools/generate_hr_v0_j2_c07_conformal_successor_mesh_p01.py"
BASE_GENERATOR = ROOT / "tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1"
R291_PREREG = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1"
R291_MESH = ROOT / "mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1"
RELEASE = ROOT / "release/hr-v0/j2-c07-pe-topology-mesh-p0.1"
IDENT = "HR-V0-J2-C07-PE-TOPOLOGY-MESH-P0.1"
ROUND = "R293"
WARNING = (
    "PRELIMINARY - PREREGISTERED PE-JUNCTION MESH-METHOD EVIDENCE ONLY - NOT "
    "APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, "
    "POWERED TESTING, MOTION, OR ENERGIZATION"
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


def load_prior():
    spec = importlib.util.spec_from_file_location("r291_execution", PRIOR_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R291 execution generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    protocol_path = PREREG / "frozen-pe-topology-protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    prereg_status = json.loads((PREREG / "analysis-status.json").read_text(encoding="utf-8"))
    if protocol["candidate_id"] != "R293-C07-PE-TOPOLOGY-V01":
        raise RuntimeError("R293 candidate identity drift")
    if protocol["linear_mesh_method"]["optimizer_sequence"] != ["Netgen", "Relocate3D"]:
        raise RuntimeError("R293 optimizer sequence drift")
    if prereg_status["mesh_executed"] or not prereg_status["single_candidate_frozen"]:
        raise RuntimeError("R293 preregistration is not fail-closed")

    prior = load_prior()
    original_load_base = prior.load_base
    optimizer_calls: list[str] = []

    def load_base_with_sequence():
        base = original_load_base()
        original_optimize = base.gmsh.model.mesh.optimize

        def optimize_sequence(method: str = "", force: bool = False, niter: int = 1, dimTags=()):
            if method != "Netgen":
                raise RuntimeError(f"unexpected linear optimizer call: {method}")
            optimizer_calls.append("Netgen")
            original_optimize("Netgen", force, niter, dimTags)
            optimizer_calls.append("Relocate3D")
            original_optimize("Relocate3D", force, niter, dimTags)

        base.gmsh.model.mesh.optimize = optimize_sequence
        return base

    prior.load_base = load_base_with_sequence
    prior.OUT = OUT
    prior.RELEASE = RELEASE
    prior.IDENT = IDENT
    prior.ROUND = ROUND
    prior.WARNING = WARNING
    return_code = prior.main()
    if optimizer_calls != ["Netgen", "Relocate3D"]:
        raise RuntimeError(f"optimizer execution sequence drift: {optimizer_calls}")

    # Replace the inherited R291 metadata with the frozen R293 method identity.
    old_protocol = OUT / "frozen-successor-protocol.json"
    if old_protocol.exists():
        old_protocol.unlink()
    shutil.copy2(protocol_path, OUT / "frozen-pe-topology-protocol.json")
    status_path = OUT / "analysis-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "identifier": IDENT,
        "round": ROUND,
        "candidate_id": protocol["candidate_id"],
        "preregistration_sha256": sha(protocol_path),
        "r291_baseline_status_sha256": sha(R291_MESH / "analysis-status.json"),
        "linear_optimizer_sequence": ["Netgen", "Relocate3D"],
        "high_order_optimizer": "NONE",
        "thresholds_unchanged": True,
        "single_preregistered_execution_complete": True,
        "warning": WARNING,
    })
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    provenance_path = OUT / "execution-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update({
        "identifier": IDENT,
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": sha(Path(__file__).resolve()),
        "transitive_r291_generator_sha256": sha(PRIOR_GENERATOR),
        "transitive_r289_generator_sha256": sha(BASE_GENERATOR),
        "preregistration_path": protocol_path.relative_to(ROOT).as_posix(),
        "preregistration_sha256": sha(protocol_path),
        "linear_optimizer": "SEQUENCE",
        "linear_optimizer_sequence": ["Netgen", "Relocate3D"],
        "high_order_optimizer": "NONE",
        "thresholds_unchanged": True,
        "warning": WARNING,
    })
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    write_csv(OUT / "method-execution-register.csv", [{
        "candidate_id": protocol["candidate_id"],
        "stage_1": "Netgen",
        "stage_2": "Relocate3D",
        "stage": "LINEAR MESH BEFORE TET10 CONVERSION",
        "execution_count": 1,
        "thresholds_unchanged": True,
        "result_global_sicn_gate": status["global_sicn_gate"],
        "result_monitored_zone_gate": status["monitored_zone_minimum_gate"],
        "result_actual_quadrature_jacobian_gate": status["actual_quadrature_signed_jacobian_gate"],
        "result_r279_c02": status["r279_c02_complete"],
        "warning": WARNING,
    }])
    write_csv(OUT / "method-baseline-register.csv", [{
        "baseline_id": "R291-C07-CONFORMAL-SUCCESSOR-V01",
        "baseline_status_sha256": sha(R291_MESH / "analysis-status.json"),
        "linear_optimizer_sequence": "Netgen",
        "global_sicn_minimum": json.loads((R291_MESH / "analysis-status.json").read_text(encoding="utf-8"))["global_sicn_minimum"],
        "monitored_zone_minimum_gate": False,
        "actual_quadrature_signed_jacobian_gate": True,
        "r279_c02_complete": False,
        "retention": "IMMUTABLE FAILED METHOD BASELINE",
        "warning": WARNING,
    }])
    failed_baseline = OUT / "failed-baseline-register.csv"
    if failed_baseline.exists():
        failed_baseline.unlink()
    (OUT / "README.md").write_text(
        f"# {IDENT}\n\n**{WARNING}**\n\n"
        "R293 executes exactly one preregistered PE-junction method candidate. Exact CAD, target entities, mesh-size fields, and acceptance thresholds are byte-bound to the prior evidence. The only change is the linear optimizer sequence `Netgen` then `Relocate3D` before Tet10 conversion.\n\n"
        "The result is a bounded mesh-method execution. Even an R279-C02 pass does not execute structural fields, establish convergence or capacity, close H02, or grant any work authority.\n",
        encoding="utf-8",
    )
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "file-manifest.csv":
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
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
