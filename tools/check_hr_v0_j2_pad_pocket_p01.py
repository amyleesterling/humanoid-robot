#!/usr/bin/env python3
"""Fail-closed checks for R277 J2 pad-pocket integration P0.1."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "mechanical/stops/hr-v0-j2-pad-pocket-p0.1"
REL = ROOT / "release/hr-v0/j2-pad-pocket-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.41"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.41"
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
    need(len(records) == len(actual), f"manifest count mismatch: {directory}")
    mapped = {r["relative_path"]:r for r in records}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in mapped and mapped[rel]["sha256"] == sha(path), f"manifest hash mismatch: {directory}/{rel}")


def main() -> int:
    for directory in (PKG, REL, CFG, CFG_REL):
        need(directory.is_dir(), f"missing package {directory}")
        check_manifest(directory)
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-PAD-POCKET-P0.1" and status["round"] == "R277", "identity drift")
    need(status["cad_identifier"] == "HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE", "CAD binding drift")
    need(status["production_depth"].startswith("DEPENDENT") and status["metal_backup_preserved"] is True, "depth/backup boundary drift")
    need(status["pad_structural_credit"] is False and status["candidate_selected"] is False, "selection/credit drift")
    need(not any(status[k] for k in ("procurement_authorized","fabrication_authorized","assembly_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")), "work authority drift")
    need(len(rows(PKG / "candidate-definition.csv")) == 3, "candidate definition drift")
    sources = rows(PKG / "source-register.csv")
    need(len(sources) == 4 and any(r["manufacturer"] == "3M" and "September 2024" in r["revision_or_date"] for r in sources), "3M source/revision missing")
    need(any(r["manufacturer"] == "Rogers Corporation" and "1224-PDF" in r["revision_or_date"] for r in sources), "Rogers source/revision missing")
    stack = rows(PKG / "dependent-depth-stack.csv")
    need(len(stack) == 4 and "DO NOT MACHINE FROM 0.520" in stack[1]["result"], "dependent stack drift")
    need(len(rows(PKG / "failure-mode-register.csv")) == 5, "failure register drift")
    need(len(rows(PKG / "verification-matrix.csv")) == 8, "verification matrix drift")
    need(len(rows(PKG / "open-holds.csv")) == 10 and len(rows(PKG / "acceptance-matrix.csv")) == 10, "hold/acceptance drift")
    need(all(r["state"] == "OPEN" and r["execution"] == "NOT EXECUTED" for r in rows(PKG / "open-holds.csv")), "hold state drift")
    page = (REL / "index.html").read_text(encoding="utf-8")
    need(WARNING in page and "0.520 mm screen depth" in page and "zero structural credit" in page, "web boundary drift")
    need("font-size:16px" in page and "font:17px" in page and "model-viewer" in page and "overflow:auto" in page, "web legibility/interaction drift")
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg_status["identifier"] == "HR-V0-CONFIG-REC-P0.41" and cfg_status["j2_pad_pocket_review"] == status["identifier"], "config binding drift")
    need(cfg_status["j2_pad_selected"] is False and cfg_status["j2_retention_selected"] is False, "config selection drift")
    for row in rows(CFG / "source-hash-register.csv"):
        need(sha(ROOT / row["source_path"]) == row["sha256"], f"config source hash drift: {row['source_path']}")
    bmap = {r["item_id"]:r for r in rows(CFG / "bom-integration-map.csv")}
    need(bmap["BOM-110"]["bound_identifier"] == status["identifier"] and bmap["BOM-111"]["bound_identifier"] == status["identifier"], "config BOM binding drift")
    bom = {r["item_id"]:r for r in rows(ROOT / "bom/bom.csv")}
    need("40 x 12" in bom["BOM-110"]["quantity"] and "467MP" in bom["BOM-111"]["manufacturer_part_number"], "master BOM drift")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R277 J2 pad-pocket correction:", "R278 exact-normal J2 stop correction:", "R279 J2 convergence protocol:", "R280 J2 refinement execution feasibility:")), "handoff drift")
    need((ROOT / "docs/review-ledger.md").read_text(encoding="utf-8").count("| R277 |") == 1, "ledger missing or duplicated")
    need(any(text in (ROOT / "README.md").read_text(encoding="utf-8") for text in ("Two hundred seventy-seven rounds are complete", "Two hundred seventy-eight rounds are complete", "Two hundred seventy-nine rounds are complete", "Two hundred eighty rounds are complete")), "README count drift")
    print("PASS: R277 pad-pocket, retention and dependent-depth controls are synchronized and fail-closed; no work or safety authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
