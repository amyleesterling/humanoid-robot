#!/usr/bin/env python3
"""Fail-closed checks for the R269 J2 stop-strength package."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_j2_stop_strength_p01 as gen


def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(message)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def check_manifest(directory: Path) -> None:
    listed = rows(directory / "file-manifest.csv")
    actual = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(len(listed) == len(actual), f"manifest count {directory}")
    index = {r["relative_path"]: r for r in listed}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in index, f"manifest member {rel}")
        need(index[rel]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), f"manifest hash {rel}")
        need(index[rel]["warning"] == gen.WARNING, f"manifest warning {rel}")


def main() -> None:
    for directory in (gen.SRC, gen.REL, gen.CFG, gen.CFGR):
        need(directory.exists(), f"missing {directory}"); check_manifest(directory)
    csvs = {"artifact-binding.csv","design-change-register.csv","j2-positive-stop-load-screen.csv","combined-factor-envelope.csv","clearance-verification.csv","source-register.csv","open-holds.csv","acceptance-matrix.csv"}
    base = csvs | {"README.md","package-status.json","file-manifest.csv"}
    need({p.name for p in gen.SRC.iterdir() if p.is_file()} == base, "source membership")
    need({p.name for p in gen.REL.iterdir() if p.is_file()} == base | {"index.html"}, "release membership")
    for name in base - {"file-manifest.csv"}: need((gen.SRC / name).read_bytes() == (gen.REL / name).read_bytes(), f"mirror {name}")
    bindings = rows(gen.REL / "artifact-binding.csv")
    need(len(bindings) == 12 and len({r["artifact_id"] for r in bindings}) == 12, "artifact bindings")
    for row in bindings:
        path = ROOT / row["source_path"]
        need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], f"artifact {row['artifact_id']}")
    changes = rows(gen.REL / "design-change-register.csv")
    need(any("6" in " ".join(r.values()) and "12" in " ".join(r.values()) for r in changes), "striker width change")
    need(any("8" in " ".join(r.values()) and "14" in " ".join(r.values()) for r in changes), "catch width change")
    load = rows(gen.REL / "j2-positive-stop-load-screen.csv")
    stall = next(r for r in load if r["case"] == "PUBLISHED_12V_MOMENTARY_STALL_ENDPOINT")
    need(math.isclose(float(stall["torque_input_nm"]), 10.6, abs_tol=1e-9), "stall torque")
    need(math.isclose(float(stall["single_rail_nominal_stress_mpa"]), 61.344, abs_tol=1e-9), "single rail stress")
    need(math.isclose(float(stall["static_yield_ratio_at_240_mpa"]), 3.912, abs_tol=1e-9), "static ratio")
    factors = rows(gen.REL / "combined-factor-envelope.csv")
    need(len(factors) == 7 and factors[-1]["case_id"] == "CF-40" and factors[-1]["screen_result"] == "FAIL SCREEN", "factor envelope fail")
    clear = rows(gen.REL / "clearance-verification.csv")
    need(len(clear) == 1 and clear[0]["discrete_pose_rows"] == "40001" and clear[0]["continuous_pair_rows"] == "69", "geometry counts")
    need(math.isclose(float(clear[0]["minimum_guaranteed_clearance_mm"]), .765783102, abs_tol=1e-9), "minimum clearance")
    need(len(rows(gen.REL / "open-holds.csv")) == 12, "holds")
    accept = rows(gen.REL / "acceptance-matrix.csv")
    need(len(accept) == 12 and all(r["execution_state"] == "NOT EXECUTED" and r["result"] == "OPEN" for r in accept), "acceptance")
    status = json.loads((gen.REL / "package-status.json").read_text(encoding="utf-8"))
    expected = {"identifier":gen.ID,"cad_candidate":gen.CAD_ID,"stop_candidate":gen.STOP_ID,"round":gen.ROUND,"artifact_bindings":12,"discrete_pose_rows":40001,"continuous_pair_rows":69,"single_rail_stall_nominal_stress_mpa":61.344,"static_yield_ratio_at_240_mpa":3.912,"four_x_factor_screen":"FAIL SCREEN","open_holds":12,"acceptance_rows":12}
    for key, value in expected.items(): need(status.get(key) == value, f"status {key}")
    for key in ("selected","physical_evidence_complete","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(status.get(key) is False, f"status false {key}")
    for path in gen.REL.glob("*.csv"):
        if path.name != "file-manifest.csv": need(all(r.get("warning") == gen.WARNING for r in rows(path)), f"warning {path.name}")
    page = (gen.REL / "index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px", "font-size:14px", "A real defect was found", "4× combined factor", gen.WARNING): need(token in page, f"page {token}")
    need("<form" not in page.lower() and "<button" not in page.lower() and not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(", page), "no form/network")
    cfg = json.loads((gen.CFG / "package-status.json").read_text(encoding="utf-8"))
    expected_cfg = {"identifier":gen.CID,"round":gen.ROUND,"current_records":50,"supersession_records":47,"open_holds":258,"acceptance_rows":312,"unaccepted_stop_strength_candidate":gen.CAD_ID,"j2_stop_strength_review":gen.ID,"current_mechanical_identifier":"HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"}
    for key, value in expected_cfg.items(): need(cfg.get(key) == value, f"config {key}")
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(cfg.get(key) is False, f"config false {key}")
    current = rows(gen.CFG / "current-configuration-map.csv")
    need(len(current) == 50 and current[-1]["identifier"] == gen.ID, "current map")
    supers = rows(gen.CFG / "supersession-map.csv")
    need(len(supers) == 47 and supers[-1]["current_or_required_successor"] == gen.CID, "supersession map")
    for row in rows(gen.CFG / "source-hash-register.csv"):
        path = ROOT / row["source_path"]
        if row["source_path"] in {"bom/bom.csv","release/hr-v0/release-candidate.json"}: need(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None, f"mutable hash {path}")
        else: need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], f"config hash {path}")
    release = json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}: need(product.get("configuration_reconciliation") in {gen.CID, "HR-V0-CONFIG-REC-P0.34", "HR-V0-CONFIG-REC-P0.35"}, f"release config {product.get('domain')}")
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            need(product.get("unaccepted_stop_strength_candidate") == gen.CAD_ID and product.get("j2_stop_strength_review") == gen.ID, f"release stop {product.get('domain')}")
            need(product.get("current_arm_architecture", "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE") != gen.CAD_ID, "P0.9 not current")
    need((ROOT / "docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R269 J2 hard-stop strength correction:", "R270 corrected J2 contact/load model:", "R271 C06 full-part FEA rejection screen:", "R272 mixed-side J2 stop candidate:", "R273 access-well J2 stop candidate:")), "handoff")
    need("| R269 |" in (ROOT / "docs/review-ledger.md").read_text(encoding="utf-8"), "ledger")
    need("All 18 Sol R12 blockers remain" in (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r269-status.md").read_text(encoding="utf-8"), "Sol boundary")
    print("R269 J2 stop-strength correction checks: PASS")
    print("12 artifacts / 40,001 poses / 69 continuous pairs / 61.344 MPa single-rail / 0 authority")
    print(gen.WARNING)


if __name__ == "__main__": main()
