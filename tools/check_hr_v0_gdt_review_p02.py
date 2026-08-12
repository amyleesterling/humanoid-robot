#!/usr/bin/env python3
"""Fail-closed checks for R268 datum/GD&T correction."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import generate_hr_v0_gdt_review_p02 as gen


def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(message)


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def check_manifest(directory: Path) -> None:
    listed=rows(directory/"file-manifest.csv")
    actual=sorted(p for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(len(listed)==len(actual),f"manifest count {directory}")
    index={r["relative_path"]:r for r in listed}
    for path in actual:
        rel=path.relative_to(directory).as_posix()
        need(rel in index,f"manifest member {rel}")
        need(index[rel]["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest(),f"manifest hash {rel}")
        need(index[rel]["warning"]==gen.WARNING,f"manifest warning {rel}")


def main() -> None:
    for directory in (gen.SRC,gen.REL,gen.CFG,gen.CFGR):
        need(directory.exists(),f"missing {directory}"); check_manifest(directory)
    csvs={"drawing-binding.csv","functional-datum-strategy.csv","exact-feature-family-register.csv","feature-control-decision.csv","degree-of-freedom-intent.csv","tolerance-zone-comparison.csv","source-register.csv","qualified-review-checklist.csv","open-holds.csv","acceptance-matrix.csv"}
    base=csvs|{"README.md","package-status.json","file-manifest.csv"}
    need({p.name for p in gen.SRC.iterdir() if p.is_file()}==base,"source membership")
    need({p.name for p in gen.REL.iterdir() if p.is_file()}==base|{"index.html"},"release membership")
    for name in base-{"file-manifest.csv"}: need((gen.SRC/name).read_bytes()==(gen.REL/name).read_bytes(),f"mirror {name}")
    bindings=rows(gen.REL/"drawing-binding.csv")
    need(len(bindings)==5 and all(r["geometry_changed_by_r268"]=="FALSE" for r in bindings),"drawing bindings")
    for row in bindings:
        path=ROOT/row["source_path"]
        need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==row["sha256"],f"drawing hash {row['part_id']}")
    datums=rows(gen.REL/"functional-datum-strategy.csv")
    need(len(datums)==5,"datum rows")
    need(all("pattern datum feature candidate" in r["datum_B_candidate"] and r["datum_C_candidate"].startswith("NONE PROPOSED") for r in datums),"exact datum strategy")
    need(all("B/C as applicable" not in " ".join(r.values()) for r in datums),"ambiguous datum language")
    features=rows(gen.REL/"exact-feature-family-register.csv")
    controls=rows(gen.REL/"feature-control-decision.csv")
    dof=rows(gen.REL/"degree-of-freedom-intent.csv")
    need(len(features)==20 and len(controls)==20 and len(dof)==15,"feature/control/DOF counts")
    need(all("B/C as applicable" not in " ".join(r.values()) for r in features+controls+dof),"ambiguous control language")
    need(sum(r["disposition"]=="NO DIAMETRICAL SUBSTITUTION" for r in controls)==5,"no substitution decisions")
    comparison=rows(gen.REL/"tolerance-zone-comparison.csv"); need(len(comparison)==1,"comparison")
    comp=comparison[0]
    need(math.isclose(float(comp["square_corner_radius_mm"]),math.hypot(.05,.05),rel_tol=0,abs_tol=5e-10),"corner radius")
    need(math.isclose(float(comp["diameter_to_enclose_square_mm"]),2*math.hypot(.05,.05),rel_tol=0,abs_tol=5e-10),"enclosing diameter")
    need(float(comp["circle_radius_mm"])==.07 and float(comp["diameter_for_circle_inside_square_mm"])==.1,"circle values")
    need("NON-EQUIVALENT" in comp["result"] and "DO NOT SUBSTITUTE" in comp["release_rule"],"comparison boundary")
    sources=rows(gen.REL/"source-register.csv")
    need(len(sources)==5 and sum(r["organization"]=="ASME" for r in sources)==3,"sources")
    need(any("reaffirmed 2024" in r["revision_or_date"] for r in sources),"ASME revision")
    review=rows(gen.REL/"qualified-review-checklist.csv")
    holds=rows(gen.REL/"open-holds.csv")
    acceptance=rows(gen.REL/"acceptance-matrix.csv")
    need(len(review)==12 and all(r["state"]=="NOT EXECUTED" and not r["response"] and not r["reviewer"] for r in review),"review blanks")
    need(len(holds)==12 and all(r["state"]=="OPEN" for r in holds),"holds")
    need(len(acceptance)==12 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in acceptance),"acceptance")
    for path in gen.REL.glob("*.csv"):
        if path.name!="file-manifest.csv": need(all(r.get("warning")==gen.WARNING for r in rows(path)),f"warning {path.name}")
    status=json.loads((gen.REL/"package-status.json").read_text(encoding="utf-8"))
    expected={"identifier":gen.ID,"round":gen.ROUND,"parts":5,"drawing_bindings":5,"feature_families":20,"feature_control_decisions":20,"dof_rows":15,"tolerance_zone_comparisons":1,"review_questions":12,"open_holds":12,"acceptance_rows":12,"supersedes_for_current_review_use":"HR-V0-GDT-REVIEW-P0.1"}
    for key,value in expected.items(): need(status.get(key)==value,f"status {key}")
    for key in ("drawing_geometry_changed","coordinate_controls_changed","formal_gdt_released","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(status.get(key) is False,f"status false {key}")
    page=(gen.REL/"index.html").read_text(encoding="utf-8")
    for token in ("font:clamp(16px","font-size:14px","not equivalent","Automatic conversion is prohibited",gen.WARNING): need(token in page,f"page {token}")
    need("<form" not in page.lower() and not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(",page),"no submission/network")
    cfg=json.loads((gen.CFG/"package-status.json").read_text(encoding="utf-8"))
    expected_cfg={"identifier":gen.CID,"round":gen.ROUND,"current_records":49,"supersession_records":46,"open_holds":246,"acceptance_rows":300,"gdt_review":gen.ID}
    for key,value in expected_cfg.items(): need(cfg.get(key)==value,f"config {key}")
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(cfg.get(key) is False,f"config false {key}")
    current=rows(gen.CFG/"current-configuration-map.csv"); need(len(current)==49 and current[-1]["identifier"]==gen.ID,"current map")
    supers=rows(gen.CFG/"supersession-map.csv"); need(len(supers)==46 and supers[-1]["current_or_required_successor"]==gen.CID,"supersession map")
    for row in rows(gen.CFG/"source-hash-register.csv"):
        path=ROOT/row["source_path"]
        if row["source_path"] in {"bom/bom.csv","release/hr-v0/release-candidate.json"}: need(re.fullmatch(r"[0-9a-f]{64}",row["sha256"]) is not None,f"mutable hash {path}")
        else: need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==row["sha256"],f"config hash {path}")
    release=json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}: need(product.get("configuration_reconciliation")==gen.CID,f"release config {product.get('domain')}")
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}: need(product.get("gdt_review")==gen.ID,f"release gdt {product.get('domain')}")
    need((ROOT/"docs/handoff-current.md").read_text(encoding="utf-8").startswith("R268 functional datum/GD&T correction:"),"handoff")
    need("| R268 |" in (ROOT/"docs/review-ledger.md").read_text(encoding="utf-8"),"ledger")
    need("All 18 Sol R12 blockers remain" in (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r268-status.md").read_text(encoding="utf-8"),"Sol boundary")
    print("R268 functional datum/GD&T correction checks: PASS")
    print("5 drawings / 20 feature decisions / non-equivalent zone correction / 0 authority")
    print(gen.WARNING)


if __name__=="__main__": main()
