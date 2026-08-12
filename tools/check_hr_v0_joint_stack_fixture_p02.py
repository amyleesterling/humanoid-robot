#!/usr/bin/env python3
"""Fail-closed R253 rank-6 3-2-1 fixture checker."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_joint_stack_fixture_p01 as p01  # noqa: E402

OUT = ROOT / "test-fixtures/hr-v0/joint-stack-fixture-p0.2"
REL = ROOT / "release/hr-v0/joint-stack-fixture-p0.2"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.17"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.17"
ID = "HR-V0-JOINT-STACK-FIXTURE-P0.2"


def fail(errors: list[str]) -> int:
    print("R253 joint-stack fixture correction: FAIL", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    for directory in (OUT, REL, CFG, CFGR):
        if not directory.is_dir():
            errors.append(f"missing directory: {directory}")
        else:
            p01_check_manifest(directory, errors)
    if errors:
        return fail(errors)
    source = p01.read_csv(OUT / "source-binding.csv")[0]
    manufacturer = p01.read_csv(OUT / "manufacturer-evidence.csv")[0]
    contacts = p01.read_csv(OUT / "contact-zone-register.csv")[0]
    matrix_rows = p01.read_csv(OUT / "constraint-matrix.csv")[0]
    keepouts = p01.read_csv(OUT / "keepout-register.csv")[0]
    steps = p01.read_csv(OUT / "temporary-stack-instruction.csv")[0]
    selections = p01.read_csv(OUT / "selection-register.csv")[0]
    holds = p01.read_csv(OUT / "open-holds.csv")[0]
    acceptance = p01.read_csv(OUT / "acceptance-matrix.csv")[0]
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if len(source) != 6 or any(p01.sha(ROOT / row["path"]) != row["sha256"] for row in source):
        errors.append("six source bindings are absent or stale")
    if len(manufacturer) != 4 or not any("XM540-W270-R" in row["conflict_or_limit"] for row in manufacturer):
        errors.append("current four-row ROBOTIS evidence or T/R contradiction is missing")
    expected_ids = ["JFX2-A1", "JFX2-A2", "JFX2-A3", "JFX2-B1", "JFX2-B2", "JFX2-C1"]
    if [row["contact_id"] for row in contacts] != expected_ids:
        errors.append("3-2-1 contact identities/order changed")
    for row in contacts:
        if abs(float(row["nominal_s102_distance_mm"])) > 1e-7:
            errors.append(f"contact does not touch nominal S102: {row['contact_id']}")
        if float(row["nominal_xm540_distance_mm"]) <= 0 or float(row["nominal_h101_distance_mm"]) <= 0:
            errors.append(f"contact intersects a keepout part: {row['contact_id']}")
        if any(abs(float(row[key])) > 1e-10 for key in ("s102_intersection_volume_mm3", "xm540_intersection_volume_mm3", "h101_intersection_volume_mm3")):
            errors.append(f"contact has modeled solid penetration: {row['contact_id']}")
        if row["material_and_force"] != "SELECTION REQUIRED":
            errors.append(f"contact material/force inferred: {row['contact_id']}")
    a = np.array([[float(row[key]) for key in ("nx", "ny", "nz", "rx_cross_n_over_L", "ry_cross_n_over_L", "rz_cross_n_over_L")] for row in matrix_rows])
    rank = int(np.linalg.matrix_rank(a))
    proof = json.loads((OUT / "constraint-proof.json").read_text(encoding="utf-8"))
    if len(matrix_rows) != 6 or rank != 6 or proof.get("rank") != 6 or proof.get("r252_coplanar_scheme_rank") != 3:
        errors.append("rank-6 successor / rank-3 predecessor proof changed")
    supersession = p01.read_csv(OUT / "supersession-disposition.csv")[0]
    if len(supersession) != 1 or "PROHIBITED FOR FIXTURE FABRICATION" not in supersession[0]["disposition"]:
        errors.append("P0.1 prohibition/supersession is missing")
    if len(keepouts) != 7 or any(row["state"] != "NOT EXECUTED" for row in keepouts):
        errors.append("seven blank keepout rows changed")
    if len(steps) != 14 or any(row["execution_state"] != "NOT EXECUTED" or row["evidence_uri"] or row["signer"] for row in steps):
        errors.append("fourteen blank temporary steps changed")
    if len(selections) != 14 or any(row["state"] != "SELECTION REQUIRED" for row in selections):
        errors.append("fourteen selections changed")
    if len(holds) != 13 or any(row["state"] != "OPEN" for row in holds):
        errors.append("thirteen holds changed")
    if len(acceptance) != 12 or any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" for row in acceptance):
        errors.append("twelve blank acceptances changed")
    false_keys = ("physical_article_exists", "fixture_buildable", "fixture_fabrication_authorized", "temporary_assembly_authorized", "session_authorized", "qualified_review_complete", "procurement_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit")
    if status.get("identifier") != ID or any(status.get(key) is not False for key in false_keys) or status.get("operations_executed") != 0 or status.get("warning") != p01.WARNING:
        errors.append("fixture status was promoted")
    shape = cq.importers.importStep(str(OUT / "HR-V0_joint-stack-fixture_P0.2_review.step")).val()
    if len(shape.Solids()) != 13:
        errors.append(f"review STEP solid count changed: {len(shape.Solids())}")
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    if cfg_status.get("identifier") != "HR-V0-CONFIG-REC-P0.17" or cfg_status.get("current_records") != 36 or cfg_status.get("supersession_records") != 25 or cfg_status.get("open_holds") != 70 or cfg_status.get("acceptance_rows") != 103:
        errors.append("P0.17 configuration counts changed")
    cfg_current = p01.read_csv(CFG / "current-configuration-map.csv")[0]
    ids = [row["identifier"] for row in cfg_current]
    if ID not in ids or "HR-V0-JOINT-STACK-FIXTURE-P0.1" in ids:
        errors.append("configuration does not replace P0.1 with P0.2")
    for path, tokens in (
        (REL / "index.html", (p01.WARNING, "font:clamp(16px", "font-size:14px", "P0.1 SUPERSEDED", "P0.2 NOT BUILDABLE")),
        (CFGR / "index.html", (p01.WARNING, "font:clamp(16px", "font-size:14px", "P0.1 FIXTURE PROHIBITED", "CONFIGURATION NOT AUTHORIZED")),
    ):
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{path} omits {token}")
    if errors:
        return fail(errors)
    print("R253 joint-stack fixture correction: PASS")
    print(f"6 contacts; matrix rank {rank}; condition {np.linalg.cond(a):.6f}; P0.1 prohibited; P0.2 not buildable; nothing authorized")
    print(p01.WARNING)
    return 0


def p01_check_manifest(directory: Path, errors: list[str]) -> None:
    for row in p01.read_csv(directory / "file-manifest.csv")[0]:
        path = directory / row["path"]
        if not path.is_file() or str(path.stat().st_size) != row["bytes"] or p01.sha(path) != row["sha256"]:
            errors.append(f"manifest mismatch: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
