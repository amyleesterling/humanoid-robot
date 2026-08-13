#!/usr/bin/env python3
"""Fail-closed checks for R278 exact-normal P0.13 stop analysis."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEA = ROOT / "mechanical/analysis/hr-v0-j2-stop-pad-pocket-fea-p0.1"
REL = ROOT / "release/hr-v0/j2-stop-pad-pocket-fea-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.42"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.42"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path) -> None:
    records = rows(directory / "file-manifest.csv")
    actual = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(len(records) == len(actual), f"manifest count mismatch {directory}")
    mapped = {r["relative_path"]:r for r in records}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in mapped and mapped[rel]["sha256"] == sha(path) and int(mapped[rel]["bytes"]) == path.stat().st_size, f"manifest drift {directory}/{rel}")


def close(value: float, target: float, tolerance: float = 1e-9) -> bool:
    return math.isclose(value, target, rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    for directory in (FEA, REL, CFG, CFG_REL):
        need(directory.is_dir(), f"missing package {directory}")
        check_manifest(directory)
    status = json.loads((FEA / "analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1" and status["round"] == "R278", "identity drift")
    need(status["cad_identifier"] == "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE", "CAD binding drift")
    need(status["supersedes_for_current_linear_calculation"] == "HR-V0-J2-STOP-ACCESS-WELL-FEA-P0.1", "supersession drift")
    n = status["normal_fixed_to_moving_world"]
    c06, c07 = status["force_on_c06_local_n"], status["force_on_c07_fixed_n"]
    need(close(sum(x*x for x in n), 1.0) and abs(c06[1]) < 1e-8 and close(c06[2], -253.607, 1e-8), "C06 exact transform drift")
    need(close(c07[1], -223.9218979819317, 1e-8) and close(c07[2], -119.06088380811465, 1e-8), "C07 exact force drift")
    need(close(math.sqrt(sum(x*x for x in c07)), 253.607, 1e-8), "C07 resultant drift")
    expected = {
        "C06_EXACT_NORMAL_TOP":(8.33644586447293, 327.6, 28.78924710862666),
        "C07_METAL_PERIMETER_EXACT_NORMAL":(26.609788752477737, 340.43555389060856, 9.01923732775416),
        "C07_POCKET_FLOOR_EXACT_NORMAL":(26.586571264479083, 496.27370849898483, 9.02711363614801),
    }
    for case_id,(stress,area,reserve) in expected.items():
        record=status["cases"][case_id]
        need(close(record["finest_global_maximum_mpa"],stress) and close(record["finest_loaded_area_mm2"],area), f"{case_id} result drift")
        need(close(record["ratio_to_project_threshold"],reserve) and record["interim_rejection_result"] == "PASS INTERNAL GEOMETRY SCREEN", f"{case_id} disposition drift")
        need(record["final_two_mesh_global_maximum_relative_change"] < 0.08, f"{case_id} mesh sensitivity drift")
    mesh = rows(FEA / "mesh-convergence.csv")
    need(len(mesh) == 9 and {r["case_id"] for r in mesh} == set(expected), "mesh register drift")
    need(all(float(r["normalized_force_balance_error"]) < 1e-9 for r in mesh), "force balance drift")
    need(len(rows(FEA / "load-boundary-register.csv")) == 3 and len(rows(FEA / "assumption-register.csv")) == 8, "boundary/assumption register drift")
    need(len(rows(FEA / "open-holds.csv")) == 10 and len(rows(FEA / "acceptance-matrix.csv")) == 10, "hold/acceptance drift")
    need(status["material_model"]["threshold_is_allowable"] is False and status["convergence_acceptance"].startswith("NOT ESTABLISHED"), "allowable/convergence boundary drift")
    need(not any(status[k] for k in ("joined_fastener_model_complete","nonlinear_contact_model_complete","dynamic_model_complete","selected","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")), "analysis authority drift")
    page = (REL / "index.html").read_text(encoding="utf-8")
    for token in (WARNING,"26.610 MPa","26.587 MPa","supersedes the earlier load-direction calculation","font:17px","font-size:16px","model-viewer","overflow:auto","class='diagram-scroll'","min-width:900px"):
        need(token in page, f"web token missing: {token}")
    cfg = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"] == "HR-V0-CONFIG-REC-P0.42" and cfg["round"] == "R278", "config identity drift")
    need(cfg["system_bom_groups"] == len(rows(ROOT / "bom/bom.csv")) == 111, "BOM count drift")
    need(cfg["current_records"] == 61 and cfg["supersession_records"] == 56 and cfg["open_holds"] == 362 and cfg["acceptance_rows"] == 416, "config count drift")
    need(cfg["p013_fea_review"] == status["identifier"] and cfg["prior_p012_fea_current_use_authorized"] is False, "config analysis binding drift")
    need(not any(cfg[k] for k in ("fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")), "config authority drift")
    for record in rows(CFG / "source-hash-register.csv"):
        need(sha(ROOT / record["source_path"]) == record["sha256"], f"config source hash drift {record['source_path']}")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R278 exact-normal J2 stop correction:", "R279 J2 convergence protocol:", "R280 J2 refinement execution feasibility:", "R281 J2 numerical backend:", "R282 J2 refinement erratum:", "R283 J2 execution architecture:")), "handoff drift")
    need((ROOT / "docs/review-ledger.md").read_text(encoding="utf-8").count("| R278 |") == 1, "ledger drift")
    need(any(text in (ROOT / "README.md").read_text(encoding="utf-8") for text in ("Two hundred seventy-eight rounds are complete", "Two hundred seventy-nine rounds are complete", "Two hundred eighty rounds are complete", "Two hundred eighty-one rounds are complete", "Two hundred eighty-two rounds are complete", "Two hundred eighty-three rounds are complete")), "README count drift")
    print("PASS: R278 exact-normal P0.13 linear screens are synchronized and fail-closed; no work or safety authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
