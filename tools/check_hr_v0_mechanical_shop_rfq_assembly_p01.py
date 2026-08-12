#!/usr/bin/env python3
"""Validate R247 successor shop drawings, RFQ payload, assembly definition, and P0.11 reconciliation."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "cad/hr-v0/generated/mechanical-shop-drawing-p0.2"
REL = ROOT / "release/hr-v0/mechanical-shop-rfq-assembly-p0.1"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.11"
CFG_REL = ROOT / "release/hr-v0/configuration-reconciliation-p0.11"
BINDING = ROOT / "bom/hr-v0-mechanical-custom-part-binding-p0.3.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
ARCH = "HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE"
PARTS = {"MV0-C01","MV0-C04","MV0-C05","MV0-C06","MV0-C07"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle: return list(csv.DictReader(handle))


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_fingerprint(text: str) -> str:
    tags = re.findall(r"<(?:line|circle|polyline|rect)\b[^>]*class=\"(?:profile|hole|csk|center|dim|ext|recess)\"[^>]*/?>", text)
    return hashlib.sha256("\n".join(re.sub(r"\s+", " ", tag.strip()) for tag in tags).encode("utf-8")).hexdigest()


def check_manifest(directory: Path, fail) -> None:
    manifest = rows(directory / "file-manifest.csv")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
    fail({r["path"] for r in manifest} != actual, f"manifest membership: {directory}")
    for row in manifest:
        path = directory / row["path"]
        fail(not path.is_file() or path.stat().st_size != int(row["bytes"]) or digest(path) != row["sha256"], f"manifest hash: {path}")


def main() -> int:
    errors: list[str] = []
    fail = lambda condition, message: errors.append(message) if condition else None
    csv_names = {"source-binding.csv","title-block-register.csv","rfq-payload-manifest.csv","administrative-correction-register.csv","datum-gdt-disposition.csv","rfq-cover-sheet.csv","provider-capability-questionnaire.csv","unpowered-assembly-sequence.csv","joint-verification-matrix.csv","tooling-consumables.csv","nonconformance-workflow.csv","open-holds.csv","acceptance-matrix.csv"}
    drawings = {f"{part}_shop-drawing_P0.2.svg" for part in PARTS}
    source_expected = csv_names | drawings | {"README.md","package-status.json","file-manifest.csv"}
    release_expected = source_expected | {"index.html"}
    fail(not SRC.is_dir() or {p.name for p in SRC.iterdir() if p.is_file()} != source_expected, "source membership")
    fail(not REL.is_dir() or {p.name for p in REL.iterdir() if p.is_file()} != release_expected, "release membership")
    check_manifest(SRC, fail); check_manifest(REL, fail)
    for name in source_expected - {"file-manifest.csv"}:
        fail((SRC/name).read_bytes() != (REL/name).read_bytes(), f"source/release mismatch: {name}")

    status = json.loads((REL/"package-status.json").read_text(encoding="utf-8"))
    expected = {"identifier":"HR-V0-MECH-SHOP-RFQ-ASSY-P0.1","drawing_identifier":"HR-V0-MECH-SHOP-DWG-P0.2","round":"R247","architecture":ARCH,"binding":"HR-V0-MECH-BOM-BIND-P0.3","status":"REVIEW/RFQ PREPARATION ONLY","part_count":5,"successor_drawing_count":5,"payload_artifact_count":15,"geometry_changes":0,"administrative_corrections":5,"provider_questions":14,"unpowered_assembly_steps":21,"joint_verification_rows":9,"tooling_rows":12,"open_holds":12,"acceptance_rows":10,"warning":WARNING}
    for key,value in expected.items(): fail(status.get(key) != value, f"status {key}")
    for key in ("formal_gdt_released","provider_contacted","physical_article_exists","qualified_review_complete","quotation_authorized","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        fail(status.get(key) is not False, f"{key} must be false")

    bindings = {r["part_id"]:r for r in rows(BINDING)}
    source_rows = {r["part_id"]:r for r in rows(REL/"source-binding.csv")}
    fail(set(bindings) != PARTS or set(source_rows) != PARTS, "five-part binding set")
    for part in PARTS:
        binding, record = bindings[part], source_rows[part]
        prior = ROOT / record["prior_drawing_path"]
        successor = ROOT / record["successor_drawing_path"]
        fail(record["architecture_id"] != ARCH or record["binding_id"] != binding["binding_id"], f"architecture/binding: {part}")
        for field,path_field in (("prior_drawing_sha256","prior_drawing_path"),("successor_drawing_sha256","successor_drawing_path"),("step_sha256","step_path"),("dxf_sha256","dxf_path")):
            path = ROOT / record[path_field]
            fail(not path.is_file() or digest(path) != record[field], f"hash binding {part} {field}")
        fail(record["step_sha256"] != binding["step_sha256"] or record["dxf_sha256"] != binding["dxf_sha256"], f"P0.3 STEP/DXF identity: {part}")
        prior_fp = geometry_fingerprint(prior.read_text(encoding="utf-8")); successor_text = successor.read_text(encoding="utf-8"); successor_fp = geometry_fingerprint(successor_text)
        fail(prior_fp != successor_fp or successor_fp != record["geometry_fingerprint"] or record["geometry_changed"] != "FALSE", f"geometry parity: {part}")
        for token in (WARNING,"HR-V0-MECH-SHOP-DWG-P0.2",ARCH,f"HRV0-{part}-SD-P0.2","P0.2 · INTEGRATED HELD CANDIDATE","FORMAL DATUM / GD&amp;T","SELECTION REQUIRED","FABRICATION AUTHORITY","FALSE","GEOMETRY CHANGE","NONE FROM P0.1"):
            fail(token not in successor_text, f"drawing token {part}: {token}")
        fail('data-shop-field="source-binding">HR-V0-MECH-BOM-BIND-P0.3</text>' not in successor_text, f"split source-binding field: {part}")
        fail(f'data-shop-field="architecture">{ARCH}</text>' not in successor_text, f"split architecture field: {part}")
        fail("PHYSICAL / QUALIFIED EVIDENCE" not in successor_text or "NOT EXECUTED" not in successor_text, f"physical evidence state: {part}")
        fail("HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE" in successor_text, f"stale architecture: {part}")
        fail(
            "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"
            in successor_text,
            f"stale warning: {part}",
        )
        fail("STATUS: NONSELECTED CANDIDATE" in successor_text, f"stale status: {part}")
        fail(re.search(r"font-size:(?:[0-9]|1[0-3])(?:\.\d+)?px", successor_text) is not None, f"sub-14px text: {part}")

    titles = rows(REL/"title-block-register.csv")
    fail(len(titles)!=5 or {r["part_id"] for r in titles}!=PARTS, "title rows")
    fail(any(r["formal_gdt_state"]!="SELECTION REQUIRED" or r["fabrication_authorized"]!="FALSE" or r["warning"]!=WARNING for r in titles), "title states")
    payload = rows(REL/"rfq-payload-manifest.csv")
    fail(len(payload)!=15 or {r["artifact_class"] for r in payload}!={"SHOP DRAWING","FINISHED DXF","STEP"}, "15-artifact payload")
    fail(any(r["transmission_authorized"]!="FALSE" or r["provider_response"]!="NOT SENT / NO RESPONSE" for r in payload), "payload transmission boundary")
    for row in payload:
        path=ROOT/row["path"]
        fail(not path.is_file() or digest(path)!=row["sha256"], f"payload hash: {row['payload_id']}")
    admin=rows(REL/"administrative-correction-register.csv")
    fail(len(admin)!=5 or sum(r["geometry_effect"]=="NONE" for r in admin)!=5, "administrative corrections")
    fail(admin[-1]["closure_state"]!="OPEN - QUALIFIED REVIEW REQUIRED", "GD&T must stay open")
    gdt=rows(REL/"datum-gdt-disposition.csv")
    fail(len(gdt)!=5 or any(r["formal_datum_reference_frame"]!="SELECTION REQUIRED" or r["feature_control_frames"]!="SELECTION REQUIRED" or r["qualified_disposition"]!="NOT EXECUTED" for r in gdt), "formal GD&T boundary")
    fail(len(rows(REL/"rfq-cover-sheet.csv"))!=5, "RFQ cover count")
    questions=rows(REL/"provider-capability-questionnaire.csv")
    fail(len(questions)!=14 or any(r["response"]!="NOT SENT / NO RESPONSE" or r["transmission_authorized"]!="FALSE" for r in questions), "14 questions unsent")
    sequence=rows(REL/"unpowered-assembly-sequence.csv")
    fail(len(sequence)!=21 or any(r["execution_state"]!="NOT EXECUTED" or r["assembly_authorized"]!="FALSE" for r in sequence), "21 steps unexecuted")
    fail(not {r["interface_or_phase"] for r in sequence}.issuperset({"A00","A01","A02","A03","A04","A05","A06","A07","STOP"}), "assembly interface coverage")
    joints=rows(REL/"joint-verification-matrix.csv")
    fail(len(joints)!=9 or {r["interface"] for r in joints}!={"A00","A01","A02","A03","A04","A05","A06","A07","HS-J2-POS"}, "nine joint rows")
    fail(any(r["verification_state"]!="NOT EXECUTED" or r["motion_credit"]!="NONE" for r in joints), "joint evidence boundary")
    fail(len(rows(REL/"tooling-consumables.csv"))!=12 or any(r["selection_state"]!="SELECTION REQUIRED" or r["use_authorized"]!="FALSE" for r in rows(REL/"tooling-consumables.csv")), "tool selections")
    fail(len(rows(REL/"nonconformance-workflow.csv"))!=8, "NCR workflow")
    fail(len(rows(REL/"open-holds.csv"))!=12 or any(r["state"]!="OPEN" for r in rows(REL/"open-holds.csv")), "12 holds open")
    fail(len(rows(REL/"acceptance-matrix.csv"))!=10 or any(r["execution_state"]!="NOT EXECUTED" or r["result"]!="OPEN" for r in rows(REL/"acceptance-matrix.csv")), "10 acceptances open")
    page=(REL/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","REVIEW/RFQ PREPARATION ONLY","Successor shop drawings","provider-capability-questionnaire"):
        fail(token not in page, f"web token: {token}")

    cfg_common={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    fail({p.name for p in CFG.iterdir() if p.is_file()}!=cfg_common, "config membership")
    fail({p.name for p in CFG_REL.iterdir() if p.is_file()}!=cfg_common|{"index.html"}, "config release membership")
    check_manifest(CFG,fail); check_manifest(CFG_REL,fail)
    cfg=json.loads((CFG_REL/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.11","round":"R247","system_bom_groups":98,"current_records":31,"supersession_records":18,"bom_integration_records":18,"gate_records":11,"open_holds":45,"acceptance_rows":65,"mechanical_shop_rfq_assembly":"HR-V0-MECH-SHOP-RFQ-ASSY-P0.1"}.items(): fail(cfg.get(key)!=value,f"config {key}")
    fail(cfg.get("current_mechanical_identifier")!=ARCH or cfg.get("current_custom_part_binding")!="HR-V0-MECH-BOM-BIND-P0.3", "current mechanical config")
    current=rows(CFG_REL/"current-configuration-map.csv")
    fail(len(current)!=31 or current[-1]["identifier"]!="HR-V0-MECH-SHOP-RFQ-ASSY-P0.1", "31 config records")
    hashes=rows(CFG_REL/"source-hash-register.csv")
    fail(len(hashes)!=31, "31 config hashes")
    for row in hashes:
        path=ROOT/row["source_path"]
        fail(not path.is_file() or digest(path)!=row["sha256"], f"config hash: {row['source_path']}")
    fail(len(rows(ROOT/"bom/bom.csv"))!=98, "98 BOM groups unchanged")

    if errors:
        print("HR-V0 R247 mechanical shop/RFQ/assembly package: FAIL")
        for error in errors: print("-",error)
        return 1
    print("HR-V0 R247 mechanical shop/RFQ/assembly package: PASS")
    print("5 successor drawings; 0 geometry changes; 15 payload artifacts; 21 unpowered steps; 12 holds; 10 open acceptances")
    print("Formal GD&T, provider contact, physical work, qualified review, motion and energization remain unauthorized")
    return 0


if __name__=="__main__": raise SystemExit(main())
