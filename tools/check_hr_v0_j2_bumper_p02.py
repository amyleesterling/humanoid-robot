#!/usr/bin/env python3
"""Fail-closed checks for R276 exact-contact pad boundary P0.2."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "mechanical/stops/hr-v0-j2-soft-contact-pad-p0.2"
REL = ROOT / "release/hr-v0/j2-soft-contact-pad-p0.2"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.40"
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
    mapped = {r["relative_path"]: r for r in records}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in mapped and mapped[rel]["sha256"] == sha(path), f"manifest hash mismatch: {directory}/{rel}")


def main() -> int:
    for directory in (PKG, REL, CFG, ROOT / "release/hr-v0/configuration-reconciliation-p0.40"):
        need(directory.is_dir(), f"missing package: {directory}")
        check_manifest(directory)
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == "HR-V0-J2-SOFT-CONTACT-PAD-P0.2" and status["round"] == "R276", "identity drift")
    need(status["candidate_selected"] is False and status["sole_structural_stop"] is False and status["safety_credit"] is False, "authority drift")
    need(not any(status[k] for k in ("procurement_authorized","assembly_authorized","powered_testing_authorized","motion_authorized","energization_authorized")), "work authority drift")
    need(math.isclose(float(status["exact_nominal_moment_arm_mm"]), 44.07204121151434, rel_tol=1e-9), "moment arm drift")
    need(math.isclose(float(status["endpoint_plus_gravity_force_n"]), 253.607, rel_tol=2e-6), "force drift")
    cases = {r["case_id"]: r for r in rows(PKG / "exact-contact-load-case-register.csv")}
    need(len(cases) == 7 and "superseded radius" not in " ".join(str(cases).lower()), "load cases incomplete or stale")
    need("253.607" in cases["PAD2-LC-003"]["result"], "exact force missing")
    need("1231" in cases["PAD2-LC-004"]["result"], "work ratio drift")
    need("74.9x" in cases["PAD2-LC-007"]["result"], "velocity ratio drift")
    caps = rows(PKG / "published-force-boundary.csv")
    need(len(caps) == 2 and all(float(r["demand_over_published_force"]) > 4.0 for r in caps), "published-force boundary drift")
    bindings = rows(PKG / "configuration-source-binding.csv")
    need(len(bindings) == 3 and all(sha(ROOT / r["source_path"]) == r["sha256"] for r in bindings), "source binding drift")
    need(len(rows(PKG / "verification-matrix.csv")) == 12, "test matrix drift")
    need(len(rows(PKG / "open-holds.csv")) == 12 and len(rows(PKG / "acceptance-matrix.csv")) == 12, "hold/acceptance drift")
    need(all(r["state"] == "OPEN" and r["execution"] == "NOT EXECUTED" for r in rows(PKG / "open-holds.csv")), "hold state drift")
    page = (PKG / "index.html").read_text(encoding="utf-8")
    need(WARNING in page and "44.072" in page and "253.6" in page and "pad cannot be the structural stop" in page, "web boundary drift")
    need("font-size:14px" in page and "font:16px" in page and "overflow:auto" in page, "web legibility drift")
    cfg_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    need(cfg_status["identifier"] == "HR-V0-CONFIG-REC-P0.40" and cfg_status["j2_soft_contact_review"] == status["identifier"], "config identity drift")
    need(any(r["item_id"] == "BOM-110" and r["bound_identifier"] == status["identifier"] for r in rows(CFG / "bom-integration-map.csv")), "BOM integration missing")
    bom = {r["item_id"]:r for r in rows(ROOT / "bom/bom.csv")}
    need("BOM-110" in bom and "2300327" in bom["BOM-110"]["manufacturer_part_number"], "master BOM missing pad candidate")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R276 exact-contact J2 pad correction:", "R277 J2 pad-pocket correction:", "R278 exact-normal J2 stop correction:", "R279 J2 convergence protocol:", "R280 J2 refinement execution feasibility:", "R281 J2 numerical backend:", "R282 J2 refinement erratum:", "R283 J2 execution architecture:", "R284 C07 curved-mesh development:", "R285 targeted C07 remesh:")), "handoff drift")
    need("| R276 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "ledger drift")
    need(any(text in (ROOT / "README.md").read_text(encoding="utf-8") for text in ("Two hundred seventy-six rounds are complete", "Two hundred seventy-seven rounds are complete", "Two hundred seventy-eight rounds are complete", "Two hundred seventy-nine rounds are complete", "Two hundred eighty rounds are complete", "Two hundred eighty-one rounds are complete", "Two hundred eighty-two rounds are complete", "Two hundred eighty-three rounds are complete", "Two hundred eighty-four rounds are complete", "Two hundred eighty-five rounds are complete")), "README count drift")
    print("PASS: R276 exact-contact pad boundary is synchronized and fail-closed; no work or safety authority released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
