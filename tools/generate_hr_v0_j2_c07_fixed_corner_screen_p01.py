#!/usr/bin/env python3
"""Screen C07 curved Tet10 meshes with every linear corner held fixed.

This R284 development screen reuses the R283 audited transfer and Jacobian
checks but disables high-order optimization.  A passing row is only a bounded
meshing-method candidate; it does not satisfy R279-C02 or close H02.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import generate_hr_v0_j2_c07_curved_mesh_repair_p01 as prior


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
IDENT = "HR-V0-J2-C07-FIXED-CORNER-SCREEN-P0.1"
WARNING = (
    "PRELIMINARY - FIXED-CORNER CURVED-MESH DEVELOPMENT SCREEN ONLY - NOT "
    "APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, "
    "POWERED TESTING, MOTION, OR ENERGIZATION"
)
VARIANTS = {
    "R284-V03-REFINED": prior.Variant("R284_V03_REFINED_FIXED", 4.0, 0.70, 1.0, 1, "Netgen", ""),
    "R284-V06-FINE": prior.Variant("R284_V06_FINE_FIXED", 3.0, 0.50, 0.75, 1, "Netgen", ""),
    "R284-V08-ULTRAFINE": prior.Variant("R284_V08_ULTRAFINE_FIXED", 2.0, 0.35, 0.50, 1, "Netgen", ""),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for record in records:
        for field in record:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.iterdir() if p.is_file() and p.name != "file-manifest.csv"):
        records.append({"relative_path": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(directory / "file-manifest.csv", records)


def recursive_manifest() -> None:
    records = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "package-manifest.csv"):
        records.append({"relative_path": path.relative_to(OUT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "package-manifest.csv", records)


def git_head() -> str:
    head = (ROOT / ".git/HEAD").read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        reference = ROOT / ".git" / head[5:]
        return reference.read_text(encoding="utf-8").strip()
    return head


def git_worktree_state() -> dict[str, object]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=normal"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    lines = completed.stdout.splitlines()
    serialized = ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")
    return {
        "git_worktree_dirty": bool(lines),
        "git_status_porcelain": lines,
        "git_status_porcelain_sha256": hashlib.sha256(serialized).hexdigest(),
        "git_status_untracked_scope": "normal",
    }


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in VARIANTS:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} {'|'.join(VARIANTS)}")
    variant_id = sys.argv[1]
    run_started = datetime.now(timezone.utc)
    baseline = git_head()
    worktree_state = git_worktree_state()
    OUT.mkdir(parents=True, exist_ok=True)
    run_out = OUT / variant_id.lower()
    if run_out.exists():
        shutil.rmtree(run_out)
    run_out.mkdir(parents=True)
    prior.OUT = run_out
    result, quadrature = prior.execute(VARIANTS[variant_id])
    # The inherited executor writes raw tables before returning. Normalize the
    # component identity/warning in every textual raw artifact so the package
    # never mixes R283 and R284 authority language.
    for path in run_out.iterdir():
        if path.suffix.lower() == ".csv":
            text = path.read_text(encoding="utf-8")
            text = text.replace(prior.IDENT, IDENT).replace(prior.WARNING, WARNING)
            path.write_text(text, encoding="utf-8")
    result.update({
        "identifier": IDENT,
        "screen_id": variant_id,
        "high_order_optimizer": "NONE",
        "bounded_sampled_jacobian_candidate_pass": bool(result["mesh_repair_pass"]),
        "screen_scope": "bounded fixed-linear-corner and sampled-Jacobian development screen; not R279-C02, convergence, capacity or authority",
        "linear_corner_coordinate_statement": "linear corner coordinates preserved within 1e-9 mm; this does not claim zero midside movement or exact B-Rep surface deviation",
        "geometry_identity_evidence": "linear-corner coordinate/connectivity/orientation and OCC corner-membership checks only; curved midsides are retained and exact B-Rep facet deviation is not evaluated",
        "r283_h03_disposition": "PARTIAL/OPEN - corner-coordinate portion advanced; exact facet connectivity, B-Rep deviation, loaded-area/resultant/location/moment remain unexecuted",
        "warning": WARNING,
    })
    for row in quadrature:
        row.update({"identifier": IDENT, "screen_id": variant_id, "warning": WARNING})
    write_csv(run_out / "variant-register.csv", [result])
    write_csv(run_out / "jacobian-screen-register.csv", quadrature)
    status = {
        "identifier": IDENT,
        "round": "R284-DEVELOPMENT",
        "screen_id": variant_id,
        "step_sha256": result["step_sha256"],
        "linear_corner_positions_preserved_within_tolerance": result["corner_bijection_gate"] == "PASS",
        "corner_bijection_tolerance_mm": float(result["corner_bijection_tolerance_mm"]),
        "corner_bijection_max_distance_mm": float(result["corner_bijection_max_distance_mm"]),
        "linear_sicn_screen_pass": result["linear_sicn_gate"] == "PASS",
        "curved_jacobian_screen_pass": result["curved_jacobian_gate"] == "PASS",
        "bounded_fixed_corner_sampled_jacobian_candidate_pass": bool(result["bounded_sampled_jacobian_candidate_pass"]),
        "r279_c02_complete": False,
        "mesh_convergence_complete": False,
        "r278_h02_closed": False,
        "capacity_established": False,
        "selected": False,
        "safety_credit": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (run_out / "analysis-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    base_generator = ROOT / "tools/generate_hr_v0_j2_stop_refinement_execution_p01.py"
    write_csv(run_out / "input-register.csv", [
        {"source_path": prior.STEP.relative_to(ROOT).as_posix(), "sha256": sha(prior.STEP), "role": "exact C07 STEP", "warning": WARNING},
        {"source_path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha(Path(__file__).resolve()), "role": "R284 screen generator", "warning": WARNING},
        {"source_path": Path(prior.__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha(Path(prior.__file__).resolve()), "role": "audited R283 transfer/check implementation", "warning": WARNING},
        {"source_path": base_generator.relative_to(ROOT).as_posix(), "sha256": sha(base_generator), "role": "transitive OCC entity/local-field implementation", "warning": WARNING},
    ])
    runtime = {
        "identifier": IDENT,
        "screen_id": variant_id,
        "run_started_timestamp_utc": run_started.isoformat(),
        "run_completed_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command_argv": [
            sys.executable,
            Path(__file__).resolve().relative_to(ROOT).as_posix(),
            variant_id,
        ],
        "working_directory": str(ROOT),
        "baseline_commit": baseline,
        **worktree_state,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "gmsh_version": importlib.metadata.version("gmsh"),
        "numpy_version": importlib.metadata.version("numpy"),
        "scipy_version": importlib.metadata.version("scipy"),
        "scikit_fem_version": importlib.metadata.version("scikit-fem"),
        "return_code_recorded_after_execution": 0 if result["mesh_repair_pass"] else 2,
        "general_num_threads": 1,
        "mesh_random_factor": "GMSH DEFAULT; SEED CONTROL NOT EXPOSED IN THIS TOOL - REPEATABILITY HOLD OPEN",
        "algorithm3d": result["algorithm3d"],
        "linear_optimizer": result["linear_optimizer"],
        "high_order_optimizer": "NONE",
        "effective_size_fields": {"global_h_mm": result["global_h_mm"], "pocket_h_mm": result["pocket_h_mm"], "hole_h_mm": result["hole_h_mm"]},
        "warning": WARNING,
    }
    (run_out / "runtime-provenance.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")
    (run_out / "README.md").write_text(
        f"# {IDENT}\n\n> **{WARNING}**\n\n{variant_id} uses no high-order optimizer. Its result is a bounded method screen only; R279-C02, H02, capacity and every work authority remain open.\n",
        encoding="utf-8",
    )
    manifest(run_out)
    summaries = []
    for candidate in sorted(path for path in OUT.iterdir() if path.is_dir()):
        register = candidate / "variant-register.csv"
        if register.exists():
            with register.open(newline="", encoding="utf-8-sig") as stream:
                summaries.extend(csv.DictReader(stream))
    write_csv(OUT / "variant-summary.csv", summaries)
    (OUT / "analysis-status.json").write_text(json.dumps({
        "identifier": IDENT,
        "round": "R284-DEVELOPMENT",
        "variants_executed": len(summaries),
        "passing_variants": [row["screen_id"] for row in summaries if str(row["bounded_sampled_jacobian_candidate_pass"]).lower() == "true"],
        "r279_c02_complete": False,
        "mesh_convergence_complete": False,
        "r278_h02_closed": False,
        "capacity_established": False,
        "selected": False,
        "safety_credit": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }, indent=2) + "\n", encoding="utf-8")
    recursive_manifest()
    print(json.dumps(status, indent=2))
    return 0 if status["bounded_fixed_corner_sampled_jacobian_candidate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
