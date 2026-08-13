#!/usr/bin/env python3
"""Fail-closed checks for R283 J2 execution-architecture integration."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mechanical/analysis/hr-v0-j2-execution-architecture-p0.1"
REL = ROOT / "release/hr-v0/j2-execution-architecture-p0.1"
EXACT = ROOT / "mechanical/analysis/hr-v0-j2-exact-zone-submodel-architecture-p0.1"
CURVED = ROOT / "mechanical/analysis/hr-v0-j2-c07-curved-mesh-repair-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.47"
CFGREL = ROOT / "release/hr-v0/configuration-reconciliation-p0.47"


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path) -> None:
    records = rows(directory / "file-manifest.csv")
    actual = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(len(records) == len(actual), f"manifest count {directory}")
    mapped = {record["relative_path"]: record for record in records}
    for path in actual:
        relative = path.relative_to(directory).as_posix()
        need(relative in mapped, f"manifest missing {relative}")
        need(mapped[relative]["sha256"] == sha(path), f"manifest hash {relative}")
        need(int(mapped[relative]["bytes"]) == path.stat().st_size, f"manifest bytes {relative}")


def main() -> int:
    for directory in (OUT, REL, EXACT, CURVED, CFG, CFGREL):
        need(directory.is_dir(), f"missing {directory}")
        check_manifest(directory)
    need({p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob("*") if p.is_file()} == {p.relative_to(REL).as_posix(): sha(p) for p in REL.rglob("*") if p.is_file()}, "source/release integration parity")
    exact = json.loads((EXACT / "analysis-status.json").read_text(encoding="utf-8"))
    curved = json.loads((CURVED / "analysis-status.json").read_text(encoding="utf-8"))
    need(exact["topology_signature_prototype_pass"] and exact["raw_run_manifest_schema_issued"], "exact architecture")
    need(not curved["bounded_mesh_method_route_found"] and not curved["r279_c02_complete"], "curved rejection")
    status = json.loads((OUT / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-EXECUTION-ARCHITECTURE-P0.1" and status["round"] == "R283", "identity")
    need(status["exact_zone_architecture_prototype_pass"] and status["c07_outer_loop_identity_pass"], "method evidence")
    false_gates = (
        "c06_subzone_semantics_complete", "c07_curved_mesh_route_promoted", "exact_clipped_zone_execution_complete",
        "structural_solution_executed", "submodel_transfer_executed", "mesh_convergence_complete",
        "independent_numerical_acceptance_complete", "r278_h02_closed", "nonlinear_contact_complete",
        "joined_joint_complete", "capacity_established", "selected", "procurement_authorized",
        "fabrication_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized",
        "motion_authorized", "energization_authorized", "safety_credit",
    )
    need(not any(status[key] for key in false_gates), "authority gate")
    findings = rows(OUT / "finding-register.csv")
    need(len(findings) == 6 and findings[4]["result"] == "REJECT" and "897/8999" in findings[4]["evidence"], "V04 disposition")
    need(len(rows(OUT / "open-holds.csv")) == 8 and len(rows(OUT / "acceptance-matrix.csv")) == 7, "holds/acceptance")
    for record in rows(OUT / "exact-input-register.csv"):
        need(sha(ROOT / record["source_path"]) == record["sha256"], f"input hash {record['source_path']}")
    cfg = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"] == "HR-V0-CONFIG-REC-P0.47" and cfg["round"] == "R283", "config identity")
    need(cfg["current_records"] == 68 and cfg["open_holds"] == 390 and cfg["acceptance_rows"] == 443, "config counts")
    need(cfg["j2_exact_zone_architecture_prototype_pass"] and not cfg["j2_c07_curved_mesh_route_promoted"] and not cfg["r278_h02_closed"], "config disposition")
    for record in rows(CFG / "source-hash-register.csv"):
        need(sha(ROOT / record["source_path"]) == record["sha256"], f"config source hash {record['source_path']}")
    page = (REL / "index.html").read_text(encoding="utf-8")
    need(all(token in page for token in ("The execution architecture advanced", "curved mesh did not", "H02 remains open", "font-size:16px", "overflow:auto")), "web guide")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R283 J2 execution architecture:", "R284 C07 curved-mesh development:")), "handoff")
    need((ROOT / "docs/review-ledger.md").read_text(encoding="utf-8").count("| R283 |") == 1, "review ledger")
    need(any(text in (ROOT / "README.md").read_text(encoding="utf-8") for text in ("Two hundred eighty-three rounds are complete", "Two hundred eighty-four rounds are complete")), "README count")
    print("PASS: R283 exact-zone execution architecture synchronized; V04 rejected, H02/capacity/all work authority open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
