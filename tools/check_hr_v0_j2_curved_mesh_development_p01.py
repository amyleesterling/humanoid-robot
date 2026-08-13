#!/usr/bin/env python3
"""Fail-closed checker for the R284 C07 curved-mesh development package."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-curved-mesh-development-p0.1"
REL = ROOT / "release/hr-v0/j2-curved-mesh-development-p0.1"
FIXED = ROOT / "mechanical/analysis/hr-v0-j2-c07-fixed-corner-screen-p0.1"
CONSTRAINED = ROOT / "mechanical/analysis/hr-v0-j2-c07-constrained-high-order-p0.1"
LOCAL = ROOT / "mechanical/analysis/hr-v0-j2-c07-failure-localization-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.48"
CFGREL = ROOT / "release/hr-v0/configuration-reconciliation-p0.48"


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def manifest(directory: Path, name: str = "file-manifest.csv") -> None:
    records = rows(directory / name)
    actual = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != name)
    need(len(records) == len(actual), f"manifest count {directory}")
    mapped = {r["relative_path"]: r for r in records}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in mapped and mapped[rel]["sha256"] == sha(path), f"manifest hash {directory.name}/{rel}")
        need(int(mapped[rel]["bytes"]) == path.stat().st_size, f"manifest bytes {directory.name}/{rel}")


def parity(left: Path, right: Path) -> None:
    a = {p.relative_to(left).as_posix(): sha(p) for p in left.rglob("*") if p.is_file()}
    b = {p.relative_to(right).as_posix(): sha(p) for p in right.rglob("*") if p.is_file()}
    need(a == b, f"source/release parity {left.name}")


def main() -> int:
    for directory in (OUT, REL, CFG, CFGREL):
        need(directory.is_dir(), f"missing {directory}")
        manifest(directory)
    parity(OUT, REL)
    parity(CFG, CFGREL)
    parity(FIXED, ROOT / "release/hr-v0/j2-c07-fixed-corner-screen-p0.1")
    parity(CONSTRAINED, ROOT / "release/hr-v0/j2-c07-constrained-high-order-p0.1")
    parity(LOCAL, ROOT / "release/hr-v0/j2-c07-failure-localization-p0.1")

    variants = {r["screen_id"]: r for r in rows(FIXED / "variant-summary.csv")}
    need(set(variants) == {"R284-V03-REFINED", "R284-V06-FINE", "R284-V08-ULTRAFINE"}, "fixed variants")
    need(int(variants["R284-V03-REFINED"]["curved_wrong_or_zero_across_screens"]) == 37, "V03 result")
    need(int(variants["R284-V06-FINE"]["curved_wrong_or_zero_across_screens"]) == 0, "V06 result")
    need(int(variants["R284-V08-ULTRAFINE"]["curved_wrong_or_zero_across_screens"]) == 9, "V08 result")
    need(variants["R284-V06-FINE"]["bounded_sampled_jacobian_candidate_pass"] == "True", "V06 candidate")
    need(all(variants[x]["bounded_sampled_jacobian_candidate_pass"] == "False" for x in ("R284-V03-REFINED", "R284-V08-ULTRAFINE")), "failed variants")
    fixed_status = json.loads((FIXED / "analysis-status.json").read_text(encoding="utf-8"))
    need(fixed_status["passing_variants"] == ["R284-V06-FINE"] and not fixed_status["r279_c02_complete"], "fixed status")

    constrained = json.loads((CONSTRAINED / "analysis-status.json").read_text(encoding="utf-8"))
    need(constrained["bounded_constrained_high_order_method_pass"], "constrained method")
    need(not constrained["surface_deviation_from_brep_complete"] and not constrained["r279_c02_complete"], "constrained boundary")
    localized = rows(LOCAL / "variant-localization-summary.csv")
    loc = {r["screen_id"]: r for r in localized}
    need(int(loc["R284-V03-REFINED"]["unique_failed_elements"]) == 11, "V03 localization")
    need(int(loc["R284-V06-FINE"]["unique_failed_elements"]) == 0, "V06 localization")
    need(int(loc["R284-V08-ULTRAFINE"]["unique_failed_elements"]) == 1, "V08 localization")

    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-CURVED-MESH-DEVELOPMENT-P0.1" and status["round"] == "R284", "integration identity")
    need(status["bounded_c07_curved_mesh_method_candidate_found"] and status["failure_localization_complete"], "bounded advance")
    false_fields = (
        "targeted_successor_remesh_executed", "exact_facet_brep_fidelity_complete", "r279_c02_complete",
        "structural_solution_executed", "mesh_convergence_complete", "independent_numerical_acceptance_complete",
        "r278_h02_closed", "capacity_established", "selected", "safety_credit", "procurement_authorized",
        "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized",
        "motion_authorized", "energization_authorized",
    )
    need(not any(status[k] for k in false_fields), "integration authority boundary")
    need(len(rows(OUT / "finding-register.csv")) == 8, "findings")
    need(len(rows(OUT / "open-holds.csv")) == 10, "holds")
    need(len(rows(OUT / "acceptance-matrix.csv")) == 8, "acceptance")
    for row in rows(OUT / "exact-input-register.csv"):
        need(sha(ROOT / row["source_path"]) == row["sha256"], f"input hash {row['source_path']}")

    cfg = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"] == "HR-V0-CONFIG-REC-P0.48" and cfg["round"] == "R284", "config identity")
    need(cfg["current_records"] == 72 and cfg["open_holds"] == 400 and cfg["acceptance_rows"] == 451, "config counts")
    need(cfg["bounded_c07_curved_mesh_method_candidate_found"] and not cfg["r279_c02_complete"] and not cfg["r278_h02_closed"], "config gates")
    for row in rows(CFG / "source-hash-register.csv"):
        need(sha(ROOT / row["source_path"]) == row["sha256"], f"config source hash {row['source_path']}")
    page = (REL / "index.html").read_text(encoding="utf-8")
    need(all(token in page for token in ("One mesh passes a bounded screen", "not converged", "font-size:16px", "overflow:auto", "R279-C02")), "web guide")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R284 C07 curved-mesh development:", "R285 targeted C07 remesh:")), "handoff")
    need((ROOT / "docs/review-ledger.md").read_text(encoding="utf-8").count("| R284 |") == 1, "ledger")
    need(any(text in (ROOT / "README.md").read_text(encoding="utf-8") for text in ("Two hundred eighty-four rounds are complete", "Two hundred eighty-five rounds are complete")), "README count")
    print("PASS: R284 bounded C07 mesh-method candidates synchronized; R279-C02/H02/capacity/all work authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
