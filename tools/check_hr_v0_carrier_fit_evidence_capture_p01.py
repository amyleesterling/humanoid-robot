"""Validate R265 blank carrier-fit evidence capture without granting authority."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import generate_hr_v0_carrier_fit_evidence_capture_p01 as gen


ROOT = Path(__file__).resolve().parents[1]


def need(condition: bool, message: str) -> None:
    if not condition: raise SystemExit(message)


def rows(path: Path):
    with path.open(newline="",encoding="utf-8-sig") as handle: return list(csv.DictReader(handle))


def check_manifest(directory: Path) -> None:
    entries=rows(directory/"file-manifest.csv")
    paths=sorted(p for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(len(entries)==len(paths),f"manifest count: {directory}")
    by={r["path"]:r for r in entries}
    for path in paths:
        rel=path.relative_to(directory).as_posix()
        need(rel in by,f"manifest missing {rel}")
        need(int(by[rel]["bytes"])==path.stat().st_size,f"manifest size {rel}")
        need(by[rel]["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest(),f"manifest hash {rel}")


def main() -> None:
    for directory in (gen.ENG,gen.REL,gen.CFG,gen.CFGR):
        need(directory.is_dir(),f"missing {directory}"); check_manifest(directory)
    status=json.loads((gen.ENG/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":gen.ID,"round":gen.ROUND,"measurement_rows":80,"article_rows":9,"instrument_rows":5,"photo_groups":12,"stop_conditions":12,"deviation_rows":12,"authorization_rows":3,"signoff_rows":6,"open_holds":10,"acceptance_rows":12}.items(): need(status.get(key)==value,f"status {key}")
    for key in ("network_submission","physical_session_authorized","physical_session_executed","download_executed","measurement_executed","photo_captured","qualified_review_complete","procurement_authorized","fabrication_authorized","marking_authorized","drilling_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status.get(key) is False,f"unsafe true {key}")
    need(status["all_measurements_blank"] is True and status["all_acceptance_executed"] is False,"blank state mismatch")
    for key,path in gen.SOURCES.items(): need(status["source_hashes"][key]==hashlib.sha256(path.read_bytes()).hexdigest(),f"source hash {key}")

    measurements=rows(gen.ENG/"measurement-plan.csv")
    need(len(measurements)==80,"measurement count")
    need([r["measurement_id"] for r in measurements]==[f"MEAS-{i:03d}" for i in range(1,81)],"measurement IDs")
    need(all(r["raw_value"]==r["instrument_id"]==r["evidence_uri"]==r["operator"]==r["reviewer"]=="" for r in measurements),"raw evidence prefilled")
    need(all(r["acceptance_limit"]=="SELECTION REQUIRED" and r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in measurements),"measurement acceptance claimed")
    need(len(rows(gen.ENG/"article-identity-register.csv"))==9 and all(r["review_state"]=="OPEN" for r in rows(gen.ENG/"article-identity-register.csv")),"articles")
    need(len(rows(gen.ENG/"instrument-register.csv"))==5 and all(r["state"]=="SELECTION REQUIRED" and not r["serial"] for r in rows(gen.ENG/"instrument-register.csv")),"instruments")
    need(len(rows(gen.ENG/"photo-shot-list.csv"))==12 and all(r["captured"]==r["reviewed"]=="NO" for r in rows(gen.ENG/"photo-shot-list.csv")),"photos")
    need(len(rows(gen.ENG/"stop-work-register.csv"))==12 and all(r["state"]=="ACTIVE" for r in rows(gen.ENG/"stop-work-register.csv")),"stops")
    need(len(rows(gen.ENG/"deviation-register.csv"))==12 and all(r["closed"]=="NO" for r in rows(gen.ENG/"deviation-register.csv")),"deviations")
    need(len(rows(gen.ENG/"session-authorization-template.csv"))==3 and all(r["state"]=="NOT AUTHORIZED" for r in rows(gen.ENG/"session-authorization-template.csv")),"authorization")
    need(len(rows(gen.ENG/"signoff-register.csv"))==6 and all(r["decision"]=="NOT SIGNED / NO ACCEPTANCE" for r in rows(gen.ENG/"signoff-register.csv")),"signoff")
    need(len(rows(gen.ENG/"open-holds.csv"))==10 and all(r["state"]=="OPEN" for r in rows(gen.ENG/"open-holds.csv")),"holds")
    need(len(rows(gen.ENG/"acceptance-matrix.csv"))==12 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in rows(gen.ENG/"acceptance-matrix.csv")),"acceptance")
    for path in gen.ENG.glob("*.csv"):
        if path.name!="file-manifest.csv": need(all(r.get("warning","")==gen.WARNING for r in rows(path)),f"warning {path.name}")

    svg=(gen.ENG/"disposable-mockups-letter.svg").read_text(encoding="utf-8")
    need("width='279.4mm'" in svg and "height='215.9mm'" in svg and "viewBox='0 0 279.4 215.9'" in svg,"letter geometry")
    need(svg.count("width='100' height='60' class='board'")==3,"board envelopes")
    need(svg.count("r='1.6'")==12,"source holes")
    need("x1='124' y1='115' x2='224' y2='115'" in svg and "x1='250' y1='102' x2='250' y2='202'" in svg,"100 mm bars")
    need("NOT A DRILL TEMPLATE" in svg and "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, MARKING, DRILLING," in svg and "ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION" in svg,"SVG boundary")
    page=(gen.REL/"index.html").read_text(encoding="utf-8")
    script=(gen.REL/"capture.js").read_text(encoding="utf-8")
    for token in ("font:clamp(16px","font-size:14px","Download raw JSON","Download raw CSV","local-only guide","transmits nothing","SELECTION REQUIRED",gen.WARNING,"<script src='capture.js'></script>"): need(token in page,f"page token {token}")
    for token in ("window.projectButtonCollect=collect",r"lines.join('\n')","acceptance_limits:'SELECTION REQUIRED'","result:'OPEN'"): need(token in script,f"script token {token}")
    need("<script>" not in page,"inline script present")
    need(not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(",page+script),"network API present")
    need("<form" not in page.lower() and "action=" not in page.lower(),"submission form present")
    need(all((gen.REL/href).exists() for href in re.findall(r"href='([^']+)'",page)),"broken local link")
    schema=json.loads((gen.ENG/"evidence-schema.json").read_text(encoding="utf-8"))
    need(schema=={"schema":"project-button-carrier-fit-raw-v1","package":gen.ID,"measurement_rows":80,"acceptance_limits":"SELECTION REQUIRED","network_submission":False,"authority_released":False,"warning":gen.WARNING},"schema")
    common={p.name for p in gen.ENG.iterdir() if p.is_file()}
    need(common-{"file-manifest.csv"} <= {p.name for p in gen.REL.iterdir() if p.is_file()},"release mirror membership")
    for name in common-{"file-manifest.csv"}: need((gen.ENG/name).read_bytes()==(gen.REL/name).read_bytes(),f"mirror mismatch {name}")

    cfg=json.loads((gen.CFG/"package-status.json").read_text(encoding="utf-8"))
    need((gen.CFG/"capture.js").read_bytes()==(gen.REL/"capture.js").read_bytes(),"config script mirror")
    for key,value in {"identifier":gen.CID,"round":gen.ROUND,"system_bom_groups":109,"current_records":46,"supersession_records":43,"bom_integration_records":30,"open_holds":210,"acceptance_rows":264,"carrier_fit_evidence_capture":gen.ID}.items(): need(cfg.get(key)==value,f"config {key}")
    need(all(cfg.get(k) is False for k in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")),"config authority")
    current={r["record_id"]:r for r in rows(gen.CFG/"current-configuration-map.csv")}
    need(len(current)==46 and current["CFG-46"]["identifier"]==gen.ID,"current map")
    supers=rows(gen.CFG/"supersession-map.csv")
    need(len(supers)==43 and supers[-1]["prior_identifier"]=="HR-V0-CONFIG-REC-P0.28" and supers[-1]["current_or_required_successor"]==gen.CID,"supersession")
    release=json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}:
            need(product.get("configuration_reconciliation") in {gen.CID,"HR-V0-CONFIG-REC-P0.30","HR-V0-CONFIG-REC-P0.31"} and product.get("carrier_fit_evidence_capture")==gen.ID,f"release metadata {product.get('domain')}")
            need(gen.ID in product.get("supporting_identifiers",[]) and gen.CID in product.get("supporting_identifiers",[]),"support identifiers")
    for path in (ROOT/"README.md",ROOT/"docs/handoff-current.md",ROOT/"docs/review-ledger.md"):
        text=path.read_text(encoding="utf-8"); need("R265" in text and gen.ID in text,f"narrative {path.name}")
    need("No Sol R12 blocker closes" in (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r265-status.md").read_text(encoding="utf-8"),"Sol overclaim")
    print("R265 carrier-fit evidence capture checks: PASS")
    print("80 blank measurements / 12 photos / 12 active stops / 0 authority")
    print(gen.WARNING)


if __name__ == "__main__": main()
