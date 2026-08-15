#!/usr/bin/env python3
"""Fail-closed R252 fixture candidate checker."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures/hr-v0/joint-stack-fixture-p0.1"
REL = ROOT / "release/hr-v0/joint-stack-fixture-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.16"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.16"
ID = "HR-V0-JOINT-STACK-FIXTURE-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path, errors: list[str]) -> None:
    for row in rows(directory / "file-manifest.csv"):
        path = directory / row["path"]
        if not path.is_file() or str(path.stat().st_size) != row["bytes"] or sha(path) != row["sha256"]:
            errors.append(f"manifest mismatch: {path}")


def main() -> int:
    errors: list[str] = []
    for directory in (OUT, REL, CFG, CFGR):
        if not directory.is_dir():
            errors.append(f"missing directory: {directory}")
        else:
            check_manifest(directory, errors)
    if errors:
        return fail(errors)
    source = rows(OUT / "source-binding.csv")
    contacts = rows(OUT / "contact-zone-register.csv")
    keepouts = rows(OUT / "keepout-register.csv")
    steps = rows(OUT / "temporary-stack-instruction.csv")
    selections = rows(OUT / "selection-register.csv")
    holds = rows(OUT / "open-holds.csv")
    acceptance = rows(OUT / "acceptance-matrix.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    if len(source) != 5 or any(sha(ROOT / row["path"]) != row["sha256"] for row in source):
        errors.append("five source bindings are absent or stale")
    if len(contacts) != 6 or [r["contact_id"] for r in contacts] != [f"JFX-CP-{i:02d}" for i in range(1, 7)]:
        errors.append("six contact candidates changed")
    for row in contacts:
        if abs(float(row["nominal_s102_distance_mm"])) > 1e-7 or float(row["nominal_xm540_distance_mm"]) < 6.75 - 1e-7:
            errors.append(f"contact screen failed: {row['contact_id']}")
        if "SELECTION REQUIRED" not in row["material"] or row["maximum_contact_force"] != "SELECTION REQUIRED":
            errors.append(f"contact selection was inferred: {row['contact_id']}")
    if len(keepouts) != 6 or any(row["state"] != "NOT EXECUTED" for row in keepouts):
        errors.append("six blank keepout rows changed")
    if len(steps) != 12 or any(row["execution_state"] != "NOT EXECUTED" or row["evidence_uri"] or row["signer"] for row in steps):
        errors.append("twelve blank temporary-stack steps changed")
    if len(selections) != 12 or any(row["state"] != "SELECTION REQUIRED" for row in selections):
        errors.append("twelve fixture selections changed")
    if len(holds) != 12 or any(row["state"] != "OPEN" for row in holds):
        errors.append("twelve fixture holds changed")
    if len(acceptance) != 10 or any(row["execution_state"] != "NOT EXECUTED" or row["result"] != "OPEN" for row in acceptance):
        errors.append("ten fixture acceptance rows changed")
    false_keys = ("physical_article_exists", "fixture_buildable", "fixture_fabrication_authorized", "temporary_assembly_authorized", "session_authorized", "qualified_review_complete", "procurement_authorized", "assembly_authorized", "connection_authorized", "powered_testing_authorized", "motion_authorized", "energization_authorized", "safety_credit")
    if status.get("identifier") != ID or any(status.get(key) is not False for key in false_keys) or status.get("operations_executed") != 0 or status.get("warning") != WARNING:
        errors.append("fixture package status was promoted")
    shape = cq.importers.importStep(str(OUT / "HR-V0_joint-stack-fixture_P0.1_review.step")).val()
    if len(shape.Solids()) != 13:
        errors.append(f"review STEP solid count changed: {len(shape.Solids())}")
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    if cfg_status.get("identifier") != "HR-V0-CONFIG-REC-P0.16" or cfg_status.get("current_records") != 36 or cfg_status.get("open_holds") != 70 or cfg_status.get("acceptance_rows") != 103:
        errors.append("P0.16 configuration counts changed")
    for path in (REL / "index.html", CFGR / "index.html"):
        text = path.read_text(encoding="utf-8")
        for token in (WARNING, "font:clamp(16px", "font-size:14px", "NOT BUILDABLE", "NOT AUTHORIZED"):
            if token not in text:
                errors.append(f"{path} omits {token}")
    if errors:
        return fail(errors)
    print("R252 joint-stack fixture candidate: PASS")
    print("3 vendor STEP sources; 13 review solids; 6 contacts; 6 keepouts; 12 steps; 12 selections; nothing authorized")
    print(WARNING)
    return 0


def fail(errors: list[str]) -> int:
    print("R252 joint-stack fixture candidate: FAIL", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
