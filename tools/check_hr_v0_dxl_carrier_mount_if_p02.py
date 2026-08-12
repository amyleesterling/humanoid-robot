"""Validate R264 carrier mounting datums without granting physical-work authority."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import generate_hr_v0_dxl_carrier_mount_if_p02 as gen


ROOT = Path(__file__).resolve().parents[1]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def file_manifest_ok(directory: Path) -> None:
    entries = rows(directory / "file-manifest.csv")
    expected = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(len(entries) == len(expected), f"manifest count mismatch: {directory}")
    by = {r["path"]: r for r in entries}
    for path in expected:
        rel = path.relative_to(directory).as_posix()
        need(rel in by, f"manifest missing {rel}")
        need(int(by[rel]["bytes"]) == path.stat().st_size, f"manifest size mismatch {rel}")
        need(by[rel]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), f"manifest hash mismatch {rel}")


def main() -> None:
    for directory in (gen.ENG, gen.REL, gen.CFG, gen.CFGR):
        need(directory.is_dir(), f"missing directory: {directory}")
        file_manifest_ok(directory)
    status = json.loads((gen.ENG / "package-status.json").read_text(encoding="utf-8"))
    expected_status = {"identifier":gen.ID,"round":gen.ROUND,"carrier_count":3,"mounting_hole_centers":12,"connector_anchors":6,"stack_screens":10,"clearance_screens":9,"open_holds":15,"metrology_rows":14,"acceptance_rows":18}
    for key,value in expected_status.items(): need(status.get(key) == value, f"status mismatch {key}")
    for key in ("all_acceptance_executed","panel_hole_diameter_selected","wire_exit_vectors_released","route_or_cut_lengths_released","physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","drilling_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status.get(key) is False, f"unsafe status true: {key}")
    for key,path in gen.SOURCES.items():
        need(status["source_hashes"][key] == hashlib.sha256(path.read_bytes()).hexdigest(), f"source hash mismatch: {key}")

    holes = rows(gen.ENG / "hole-coordinate-register.csv")
    need(len(holes) == 12, "hole row count")
    expected_holes = {
        ("LIM1","MH1"):(493,305),("LIM1","MH2"):(493,395),("LIM1","MH3"):(443,305),("LIM1","MH4"):(443,395),
        ("LIM2","MH1"):(493,415),("LIM2","MH2"):(493,505),("LIM2","MH3"):(443,415),("LIM2","MH4"):(443,505),
        ("LIM3","MH1"):(493,525),("LIM3","MH2"):(493,615),("LIM3","MH3"):(443,525),("LIM3","MH4"):(443,615),
    }
    for row in holes:
        need((float(row["panel_center_x_mm"]),float(row["panel_center_y_mm"])) == expected_holes[(row["carrier"],row["hole"])], f"hole coordinate mismatch {row}")
        need(row["panel_hole"] == "SELECTION REQUIRED" and "DO NOT" in row["state"], "hole released")
    anchors=rows(gen.ENG / "connector-anchor-register.csv")
    need(len(anchors)==6,"anchor row count")
    expected_anchors={("LIM1","JIN1"):(468,308),("LIM1","JOUT1"):(468,392),("LIM2","JIN1"):(468,418),("LIM2","JOUT1"):(468,502),("LIM3","JIN1"):(468,528),("LIM3","JOUT1"):(468,612)}
    for row in anchors:
        need((float(row["panel_anchor_x_mm"]),float(row["panel_anchor_y_mm"])) == expected_anchors[(row["carrier"],row["connector"])], f"anchor mismatch {row}")
        need(row["header_style"]=="B2P-VH TOP ENTRY" and row["wire_exit_direction"].startswith("NOT DEFINED"),"wire exit inferred")
    transforms=rows(gen.ENG/"transform-definition.csv")
    need(len(transforms)==1 and transforms[0]["equations"]=="x_panel = x0 + (60 - y_board); y_panel = y0 + x_board","transform mismatch")
    clear=rows(gen.ENG/"clearance-screen.csv")
    need(len(clear)==9,"clearance count")
    need(next(r for r in clear if r["screen_id"]=="CLR-01")["nominal_clearance_mm"]=="14.2","WD2 clearance")
    need(next(r for r in clear if r["screen_id"]=="CLR-06")["nominal_clearance_mm"]=="5.0","WD4 clearance")
    need(len(rows(gen.ENG/"depth-stack-screen.csv"))==10,"stack count")
    need(all(r["cut_length_mm"]=="SELECTION REQUIRED" for r in rows(gen.ENG/"route-anchor-screen.csv")),"cut length released")
    need(len(rows(gen.ENG/"open-holds.csv"))==15 and all(r["state"]=="OPEN" for r in rows(gen.ENG/"open-holds.csv")),"hold state")
    need(len(rows(gen.ENG/"no-drill-metrology-form.csv"))==14 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in rows(gen.ENG/"no-drill-metrology-form.csv")),"metrology claimed")
    need(len(rows(gen.ENG/"acceptance-matrix.csv"))==18 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in rows(gen.ENG/"acceptance-matrix.csv")),"acceptance claimed")
    need("NOT A DRILL TEMPLATE" in (gen.ENG/"panel-datum-screen.svg").read_text(encoding="utf-8"),"SVG warning absent")

    cfg=json.loads((gen.CFG/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":gen.CID,"round":gen.ROUND,"system_bom_groups":109,"current_records":45,"supersession_records":42,"bom_integration_records":30,"open_holds":200,"acceptance_rows":252,"dxl_carrier_mount":gen.ID}.items(): need(cfg.get(key)==value,f"config mismatch {key}")
    need(all(cfg.get(k) is False for k in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")),"configuration grants authority")
    current={r["record_id"]:r for r in rows(gen.CFG/"current-configuration-map.csv")}
    need(current["CFG-06"]["identifier"]==gen.ID,"CFG-06 stale")
    supers=rows(gen.CFG/"supersession-map.csv")
    need(len(supers)==42 and supers[-2]["record_id"]=="SUP-41" and supers[-1]["record_id"]=="SUP-42","supersession mismatch")
    bom={r["item_id"]:r for r in rows(gen.BOM)}
    need("NSE-1580-M3-6" in bom["BOM-091"]["manufacturer_part_number"] and "replacement" in bom["BOM-091"]["manufacturer_part_number"],"BOM-091 replacement missing")
    need("No procurement" in bom["BOM-091"]["selection_basis"],"BOM-091 authority leak")
    need(len(rows(gen.CLOSURE))==109,"closure count")
    release=json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","bill_of_materials","assembly"}:
            need(product.get("configuration_reconciliation") in {gen.CID,"HR-V0-CONFIG-REC-P0.29","HR-V0-CONFIG-REC-P0.30","HR-V0-CONFIG-REC-P0.31","HR-V0-CONFIG-REC-P0.32","HR-V0-CONFIG-REC-P0.33"} and product.get("dxl_carrier_mount")==gen.ID,"release metadata stale")
            need(gen.ID in product.get("supporting_identifiers",[]) and gen.CID in product.get("supporting_identifiers",[]),"release identifiers absent")
    for path in (ROOT/"README.md",ROOT/"docs/handoff-current.md",ROOT/"docs/review-ledger.md"):
        text=path.read_text(encoding="utf-8")
        need("R264" in text and gen.ID in text,"narrative stale")
    need("No Sol R12 blocker" in (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r264-status.md").read_text(encoding="utf-8"),"Sol closure overclaim")
    print("R264 carrier mounting-datum checks: PASS")
    print("12 hole centers / 6 connector anchors / 15 open holds / 18 blank acceptances")
    print(gen.WARNING)


if __name__ == "__main__": main()
