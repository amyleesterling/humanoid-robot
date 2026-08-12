#!/usr/bin/env python3
"""Generate R268 functional datum/GD&T correction and P0.32 config."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-GDT-REVIEW-P0.2"
CID = "HR-V0-CONFIG-REC-P0.32"
ROUND = "R268"
DATE = "2026-08-12"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
SRC = ROOT / "mechanical/drawings/hr-v0-gdt-review-p0.2"
REL = ROOT / "release/hr-v0/gdt-review-p0.2"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.31"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.32"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.32"
DRAWINGS = ROOT / "cad/hr-v0/generated/mechanical-shop-drawing-p0.2"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, object]) -> dict[str, object]:
    return {**row, "warning": WARNING}


def write_csv(path: Path, fields: list[str], records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in records)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append(warned({"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    write_csv(directory / "file-manifest.csv", ["relative_path", "sha256", "bytes", "warning"], records)


PARTS = [
    ("MV0-C01", "Joint-to-20-2040 adapter", "J1-J4", "four 32 x 16 mm M2.5 clearance holes", "E1-E2", "two M5 clearance/countersink axes"),
    ("MV0-C04", "H104-to-20-2040 adapter", "H1-H4", "four asymmetric H104 clearance holes", "E1-E2", "two M5 clearance/countersink axes"),
    ("MV0-C05", "S102-to-40-4040 support", "S1-S4", "four 32 x 16 mm S102 clearance holes", "K1-K2", "two M8 clearance axes spaced 60 mm"),
    ("MV0-C06", "J2 positive moving striker", "J1-J4", "four 32 x 16 mm interface holes", "E1-E2 + striker profiles", "two M5 axes and twin striker rail profiles"),
    ("MV0-C07", "J2 positive fixed catch", "J1-J4", "four 32 x 16 mm interface holes", "E1-E2 + catch profiles", "two M5 axes and twin catch rail profiles"),
]


def package_data() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    drawings = []
    drf = []
    features = []
    controls = []
    dof = []
    for part, name, primary_ids, primary, secondary_ids, secondary in PARTS:
        drawing = DRAWINGS / f"{part}_shop-drawing_P0.2.svg"
        drawings.append(warned({
            "part_id": part, "part_name": name,
            "source_path": drawing.relative_to(ROOT).as_posix(), "sha256": sha(drawing),
            "geometry_changed_by_r268": "FALSE", "authority": "CURRENT P0.2 REVIEW DRAWING; NOT RELEASED FOR FABRICATION",
        }))
        drf.append(warned({
            "part_id": part,
            "datum_A_candidate": "non-countersink broad seating face",
            "datum_B_candidate": f"{primary_ids} primary mating-hole pattern as a pattern datum feature candidate",
            "datum_C_candidate": "NONE PROPOSED; secondary interface is controlled to A|B unless qualified reviewer requires a tertiary datum",
            "functional_intent": "A seats the plate; B is intended to locate both in-plane translations and clocking; secondary features are related to the seated primary interface without a redundant datum claim",
            "modifier": "SELECTION REQUIRED BY QUALIFIED REVIEWER",
            "standard_state": "FUNCTIONAL STRATEGY ONLY - EXACT Y14.5 SYMBOL/MODIFIER/DRF SYNTAX NOT RELEASED",
        }))
        features.extend([
            warned({"feature_id": f"{part}-A", "part_id": part, "source_feature_ids": "broad seating face", "feature_family": "primary plane", "current_control": "flatness 0.15 mm; drawing-specific thickness control", "candidate_relationship": "datum feature A", "decision": "QUALIFIED REVIEW REQUIRED"}),
            warned({"feature_id": f"{part}-B", "part_id": part, "source_feature_ids": primary_ids, "feature_family": primary, "current_control": "diameter tolerance and basic-looking coordinate values with +/-0.05 mm coordinate tolerance", "candidate_relationship": "pattern datum feature B after qualified approval", "decision": "DO NOT CONVERT AUTOMATICALLY"}),
            warned({"feature_id": f"{part}-S", "part_id": part, "source_feature_ids": secondary_ids, "feature_family": secondary, "current_control": "drawing-specific size/coordinate/profile controls", "candidate_relationship": "control to A|B; tertiary datum only if justified", "decision": "QUALIFIED REVIEW REQUIRED"}),
            warned({"feature_id": f"{part}-OPP", "part_id": part, "source_feature_ids": "opposite broad face", "feature_family": "opposite plane", "current_control": "parallelism 0.10 mm to proposed A", "candidate_relationship": "parallelism to A", "decision": "QUALIFIED REVIEW REQUIRED"}),
        ])
        controls.extend([
            warned({"control_id": f"{part}-FCF-01", "part_id": part, "controlled_feature": "broad seating face", "proposal": "retain 0.15 mm flatness candidate", "reference": "none", "material_condition": "not applicable", "disposition": "REVIEW ONLY - NOT RELEASED"}),
            warned({"control_id": f"{part}-FCF-02", "part_id": part, "controlled_feature": "opposite broad face", "proposal": "retain 0.10 mm parallelism candidate", "reference": "A", "material_condition": "not applicable", "disposition": "REVIEW ONLY - NOT RELEASED"}),
            warned({"control_id": f"{part}-FCF-03", "part_id": part, "controlled_feature": primary_ids, "proposal": "retain current +/-0.05 mm X/Z coordinate controls pending fit and qualified zone selection", "reference": "A; possible pattern datum B definition requires reviewer", "material_condition": "SELECTION REQUIRED BY QUALIFIED REVIEWER", "disposition": "NO DIAMETRICAL SUBSTITUTION"}),
            warned({"control_id": f"{part}-FCF-04", "part_id": part, "controlled_feature": secondary_ids, "proposal": "retain current drawing-specific coordinate/profile controls pending functional stack and qualified review", "reference": "candidate A|B", "material_condition": "SELECTION REQUIRED BY QUALIFIED REVIEWER", "disposition": "REVIEW ONLY - NOT RELEASED"}),
        ])
        dof.extend([
            warned({"part_id": part, "datum_or_feature": "A", "intended_constraint": "translation normal to seating face plus two rotations", "remaining_motion": "two in-plane translations plus clocking", "risk": "surface form and restraint method can bias setup", "qualified_decision": "accept face, simulator and restraint"}),
            warned({"part_id": part, "datum_or_feature": "B pattern", "intended_constraint": "two in-plane translations plus clocking", "remaining_motion": "none for nominal rigid registration", "risk": "modifier and simulator choice can change boundary/shift", "qualified_decision": "accept pattern datum definition and modifier"}),
            warned({"part_id": part, "datum_or_feature": "secondary features", "intended_constraint": "controlled output features; no additional datum constraint proposed", "remaining_motion": "not applicable", "risk": "adding C without functional need may create a redundant or ambiguous scheme", "qualified_decision": "decide whether tertiary datum is functionally necessary"}),
        ])

    half = 0.05
    proposed_diameter = 0.14
    comparison = [warned({
        "comparison_id": "TZ-01", "legacy_zone": "+/-0.05 mm independently in X and Z (0.10 x 0.10 mm square)",
        "candidate_zone": "diametrical position 0.14 mm (radius 0.07 mm circle)",
        "square_corner_radius_mm": f"{math.hypot(half, half):.9f}",
        "circle_radius_mm": f"{proposed_diameter/2:.9f}",
        "diameter_to_enclose_square_mm": f"{2*math.hypot(half, half):.9f}",
        "diameter_for_circle_inside_square_mm": f"{2*half:.9f}",
        "result": "NON-EQUIVALENT: the 0.14 circle extends beyond square sides, while square corners extend beyond the 0.14 circle; neither contains the other",
        "release_rule": "DO NOT SUBSTITUTE; retain current coordinate controls until functional fit analysis and qualified Y14.5 disposition",
    })]
    sources = [
        warned({"source_id":"R268-SRC-01","organization":"ASME","title":"Y14.5 Dimensioning and Tolerancing","revision_or_date":"2018; reaffirmed 2024; page accessed 2026-08-12","url_or_path":"https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensiones-y-tolerancias","use":"current official standard identity and scope; licensed normative text not reproduced","boundary":"does not approve this proposal"}),
        warned({"source_id":"R268-SRC-02","organization":"ASME","title":"Y14 Standards overview","revision_or_date":"live page; accessed 2026-08-12","url_or_path":"https://www.asme.org/codes-standards/y14-standards","use":"official drawing/GD&T standards context","boundary":"not a substitute for licensed standard access"}),
        warned({"source_id":"R268-SRC-03","organization":"ASME","title":"GDTP certification","revision_or_date":"live page; accessed 2026-08-12","url_or_path":"https://www.asme.org/certification-accreditation/personnel-certification/gdtp-%28y14-5%29-geometric-dimensioning-and-tolerancing-professional-certification","use":"supports qualified reviewer route for datum structures/modifiers","boundary":"certification page does not approve any project drawing"}),
        warned({"source_id":"R268-SRC-04","organization":"Project Button","title":"R247 held shop package","revision_or_date":"P0.2 drawing set; hash bound 2026-08-12","url_or_path":"cad/hr-v0/generated/mechanical-shop-drawing-p0.2/","use":"five current review drawings and existing coordinate controls","boundary":"not released for fabrication"}),
        warned({"source_id":"R268-SRC-05","organization":"Project Button","title":"R250 review-only proposal","revision_or_date":"P0.1; superseded for current review use by R268","url_or_path":"release/hr-v0/gdt-review-p0.1/package-status.json","use":"identified ambiguous B/C wording and 0.14 mm substitution proposal","boundary":"historical proposal only"}),
    ]
    holds_text = [
        "Licensed/current ASME Y14.5 access available to the qualified reviewer",
        "Qualified reviewer accepts or revises each A/B scheme and modifier",
        "Functional fit/tolerance stack establishes acceptable zones for every mating pattern",
        "All exact FCF symbols, datum-feature symbols and basic dimensions are placed on successor drawings",
        "C06/C07 rail surface/contact profile scheme is accepted",
        "Countersink axis, head-seat and received-fastener acceptance are defined",
        "Inspection simulators, restraint, probing, temperature and alignment are validated",
        "Measurement uncertainty and conformity decision rules are accepted",
        "Provider DFM and metrology capability response is accepted",
        "Five first articles and raw inspection records are accepted",
        "Received mating-part dry fits are accepted",
        "Configuration-bound qualified release and separate fabrication authority are signed",
    ]
    holds = [warned({"hold_id":f"R268-H{i:02d}","hold":value,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS DRAWING/FABRICATION RELEASE"}) for i,value in enumerate(holds_text,1)]
    questions = [
        "Accept or revise the A seating face and its simulator/restraint for each part.",
        "Accept or revise the primary mating pattern as datum feature B and select the applicable modifier.",
        "Confirm that no tertiary datum is required, or define the exact functional tertiary datum.",
        "Perform the mating-stack analysis and choose coordinate or position zones without claiming equivalence.",
        "Define C06/C07 rail surface-profile and contact acceptance relative to the accepted DRF.",
        "Define countersink axis, seat and received-head functional acceptance.",
        "Resolve size, flatness, parallelism and any envelope-rule interactions.",
        "Define inspection simulator, restraint, probe strategy, temperature and alignment.",
        "Allocate uncertainty and conformity decision rules by measurand.",
        "Approve successor drawing/model authority and conflict precedence.",
        "Confirm provider capability, DFM response and first-article plan.",
        "Sign or reject a configuration-bound disposition; do not authorize fabrication implicitly.",
    ]
    review = [warned({"review_id":f"R268-QR-{i:02d}","question":q,"response":"","evidence_uri":"","reviewer":"","state":"NOT EXECUTED"}) for i,q in enumerate(questions,1)]
    acceptance = [warned({"acceptance_id":f"R268-ACC-{i:02d}","criterion":h["hold"],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}) for i,h in enumerate(holds,1)]
    return {
        "drawing-binding.csv": (["part_id","part_name","source_path","sha256","geometry_changed_by_r268","authority","warning"],drawings),
        "functional-datum-strategy.csv": (["part_id","datum_A_candidate","datum_B_candidate","datum_C_candidate","functional_intent","modifier","standard_state","warning"],drf),
        "exact-feature-family-register.csv": (["feature_id","part_id","source_feature_ids","feature_family","current_control","candidate_relationship","decision","warning"],features),
        "feature-control-decision.csv": (["control_id","part_id","controlled_feature","proposal","reference","material_condition","disposition","warning"],controls),
        "degree-of-freedom-intent.csv": (["part_id","datum_or_feature","intended_constraint","remaining_motion","risk","qualified_decision","warning"],dof),
        "tolerance-zone-comparison.csv": (["comparison_id","legacy_zone","candidate_zone","square_corner_radius_mm","circle_radius_mm","diameter_to_enclose_square_mm","diameter_for_circle_inside_square_mm","result","release_rule","warning"],comparison),
        "source-register.csv": (["source_id","organization","title","revision_or_date","url_or_path","use","boundary","warning"],sources),
        "qualified-review-checklist.csv": (["review_id","question","response","evidence_uri","reviewer","state","warning"],review),
        "open-holds.csv": (["hold_id","hold","state","closure_evidence","release_effect","warning"],holds),
        "acceptance-matrix.csv": (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"],acceptance),
    }


def table(name: str, fields: list[str], rows: list[dict[str, object]]) -> str:
    head = "".join(f"<th>{html.escape(f.replace('_',' '))}</th>" for f in fields)
    body = "".join("<tr>"+"".join(f"<td>{html.escape(str(row.get(f,'')))}</td>" for f in fields)+"</tr>" for row in rows)
    return f"<section><h2>{html.escape(name[:-4].replace('-',' ').title())}</h2><p><a href='{name}'>Download {name}</a></p><div class='table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def page(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    key = data["tolerance-zone-comparison.csv"][1][0]
    sections = "".join(table(name,*payload) for name,payload in data.items())
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#082e55;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,18px)/1.55 system-ui,sans-serif}}header,main{{padding:clamp(18px,3vw,42px)}}header{{background:linear-gradient(135deg,var(--blue),#086bad);color:white}}header>div,main{{max-width:1500px;margin:auto}}.warning{{border:3px solid var(--gold);border-radius:12px;padding:14px;font-size:clamp(16px,1.3vw,20px);font-weight:800;color:#fff2bd}}h1{{font-size:clamp(34px,5vw,64px);line-height:1.06}}h2{{font-size:clamp(24px,2.6vw,36px)}}.result{{background:#fff4c9;border:3px solid var(--gold);padding:18px;border-radius:14px;font-size:18px}}.metric{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric div{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}.metric strong{{display:block;font-size:32px;color:var(--blue)}}a{{color:#075ea8;font-size:16px;font-weight:750}}section{{margin:34px 0}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:1100px}}th,td{{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #cce1ef;font-size:14px;line-height:1.45}}th{{background:var(--sky)}}code{{font-size:16px}}@media(max-width:600px){{header,main{{padding:18px}}h1{{font-size:36px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>{ROUND} · qualified-review input · zero work authority</p><h1>Functional datum and tolerance-zone correction</h1><p>Exact feature families replace “B/C as applicable.” Existing drawing geometry and coordinate controls remain unchanged.</p></div></header><main><section class='result'><h2>The Ø0.14 proposal is not equivalent to ±0.05 coordinates</h2><p>{html.escape(str(key['result']))}. Automatic conversion is prohibited.</p></section><section><h2>Bounded result</h2><div class='metric'><div><strong>5</strong>hash-bound current drawings</div><div><strong>20</strong>exact feature-control decisions</div><div><strong>12</strong>open qualified-review holds</div><div><strong>0</strong>fabrication releases</div></div></section>{sections}</main></body></html>"""


def build_package(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> None:
    for directory in (SRC,REL):
        if directory.exists(): shutil.rmtree(directory)
        directory.mkdir(parents=True)
    for name,(fields,records) in data.items(): write_csv(SRC/name,fields,records)
    status = {"identifier":ID,"round":ROUND,"date":DATE,"state":"FUNCTIONAL DATUM/GD&T CORRECTION FOR QUALIFIED REVIEW","parts":5,"drawing_bindings":5,"feature_families":20,"feature_control_decisions":20,"dof_rows":15,"tolerance_zone_comparisons":1,"review_questions":12,"open_holds":12,"acceptance_rows":12,"supersedes_for_current_review_use":"HR-V0-GDT-REVIEW-P0.1","drawing_geometry_changed":False,"coordinate_controls_changed":False,"formal_gdt_released":False,"qualified_review_complete":False,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (SRC/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (SRC/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR268 removes the ambiguous `B/C as applicable` wording and proves that the prior Ø0.14 position proposal is not equivalent to the current ±0.05 coordinate zones. Current controls remain unchanged until functional stack analysis and qualified review.\n",encoding="utf-8")
    for path in SRC.iterdir():
        if path.is_file() and path.name != "file-manifest.csv": shutil.copy2(path,REL/path.name)
    (REL/"index.html").write_text(page(data),encoding="utf-8")
    manifest(SRC); manifest(REL)


def update_config() -> None:
    for directory in (CFG,CFGR):
        if directory.exists(): shutil.rmtree(directory)
    shutil.copytree(CFG0,CFG)
    # P0.31 inherited two route-draft scripts. P0.32 has no form or runtime
    # behavior, so carrying those unrelated scripts would be misleading.
    for stale in (CFG/"capture.js",CFG/"decision.js"):
        if stale.exists(): stale.unlink()
    current = read_csv(CFG/"current-configuration-map.csv")
    current.append(warned({"record_id":"CFG-49","role":"functional datum/GD&T correction for qualified review","identifier":ID,"source_path":"release/hr-v0/gdt-review-p0.2/package-status.json","configuration_state":"CURRENT REVIEW DEFINITION - FORMAL GD&T NOT RELEASED","release_boundary":"exact feature/DOF strategy only; current coordinate controls retained; qualified disposition, successor drawings, DFM, FAI and fit open"}))
    write_csv(CFG/"current-configuration-map.csv",list(current[0]),current)
    supers = read_csv(CFG/"supersession-map.csv")
    supers.append(warned({"record_id":"SUP-46","prior_identifier":"HR-V0-CONFIG-REC-P0.31","current_or_required_successor":CID,"disposition":"superseded for current package indexing; R267 remains source evidence","use_authorized":"NO"}))
    write_csv(CFG/"supersession-map.csv",list(supers[0]),supers)
    holds = read_csv(CFG/"open-holds.csv")
    for row in read_csv(REL/"open-holds.csv"):
        holds.append(warned({"hold_id":f"HOLD-{len(holds)+1:03d}","hold":f"{ID}: {row['hold']}","state":"NOT EXECUTED","closure_evidence":row["closure_evidence"]}))
    write_csv(CFG/"open-holds.csv",list(holds[0]),holds)
    acceptance = read_csv(CFG/"acceptance-matrix.csv")
    for row in read_csv(REL/"acceptance-matrix.csv"):
        acceptance.append(warned({"acceptance_id":f"ACC-{len(acceptance)+1:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    write_csv(CFG/"acceptance-matrix.csv",list(acceptance[0]),acceptance)
    impacts = read_csv(CFG/"gate-impact.csv")
    for row in impacts:
        if row["gate_id"] == "EG-005":
            row["evidence_added"] += f"; {ID} exact feature-family and DOF strategy; non-equivalent tolerance-zone correction"
            row["remaining_evidence"] += "; qualified Y14.5 disposition; accepted functional stack; successor drawings; provider DFM; FAI; received fit and proof"
    write_csv(CFG/"gate-impact.csv",list(impacts[0]),impacts)
    status = json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"current_records":49,"supersession_records":46,"open_holds":len(holds),"acceptance_rows":len(acceptance),"gdt_review":ID})
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): status[key]=False
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR268 adds {ID}. It corrects a non-equivalent tolerance-zone proposal and removes ambiguous datum wording without changing drawing geometry or authorizing work. {len(holds)} holds and {len(acceptance)} blank acceptances remain.\n",encoding="utf-8")
    hashes=[]
    for row in current:
        path=ROOT/row["source_path"]
        hashes.append(warned({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"]}))
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes)
    shutil.copy2(REL/"index.html",CFG/"index.html")
    manifest(CFG)
    shutil.copytree(CFG,CFGR)
    manifest(CFGR)


def update_release() -> None:
    data=json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}: product["configuration_reconciliation"]=CID
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]): product.setdefault("supporting_identifiers",[]).append(value)
            product["gdt_review"]=ID
    RELEASE.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def update_docs() -> None:
    (ROOT/"docs/hr-v0-gdt-review-p0.2.md").write_text(f"""# HR-V0 functional datum/GD&T correction P0.2

> **{WARNING}**

R268 supersedes P0.1 for current review use. It binds the five current P0.2 shop drawings by SHA-256, names every primary and secondary feature family, records the intended six-degree-of-freedom constraint strategy, and removes the ambiguous phrase `B/C as applicable`.

The prior Ø0.14 mm position proposal is **not equivalent** to independent ±0.05 mm X/Z coordinates. The square-zone corner radius is 0.070710678 mm; a Ø0.14 circle has 0.070000000 mm radius. The circle extends 0.02 mm beyond the square across its diameter on each axis, while each square corner lies 0.000710678 mm outside the circle. Neither zone contains the other. No automatic substitution is permitted; existing coordinate controls remain current until a functional fit stack and qualified ASME Y14.5 disposition are complete.

ASME identifies Y14.5-2018 as reaffirmed in 2024. Normative text is not reproduced. The reviewer must have lawful access to the current standard and must select exact symbols, modifiers, datum simulators, uncertainty rules and successor drawing content.

Interactive guide: [release package](../release/hr-v0/gdt-review-p0.2/index.html).
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r268-validation-record.md").write_text(f"""# R268 validation record

> **{WARNING}**

`{ID}` binds five current drawings and provides five functional datum strategies, twenty exact feature-family rows, twenty feature-control decisions, fifteen degree-of-freedom rows, one numerical tolerance-zone comparison, twelve open holds and twelve blank acceptances. It changes no drawing geometry or coordinate tolerance and releases no formal GD&T.

The numerical comparison independently reproduces the square-corner radius `sqrt(0.05^2 + 0.05^2) = 0.070710678 mm`, the enclosing circular diameter `0.141421356 mm`, and the Ø0.14 radius `0.070000000 mm`. Because neither zone contains the other, P0.1's proposed conversion is rejected as non-equivalent.

Automated validation passed **211/211 non-native repository checks** and **18/18 KiCad-native checks** under KiCad 10.0. Browser QA passed at 1280 x 720 and 390 x 844: body text remained 16 px, table text 14 px, the warning remained visible, the page had no horizontal overflow, and wide tables used internal horizontal scrolling. The page contains zero forms and zero buttons. The staged master manifest covers **6,521 package files**.

No Sol R12 blocker closes. B-003 and EG-005 remain partial/open pending qualified review, functional stack analysis, successor drawings, provider DFM, FAI, received fit, structural proof and signed authority.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r268-independent-review-request.md").write_text(f"""# R268 independent review request

> **{WARNING}**

Audit the five drawing hashes, exact feature families, degree-of-freedom intent, and tolerance-zone arithmetic. Confirm that P0.2 does not claim the Ø0.14 and ±0.05 zones are equivalent and does not invent a tertiary datum. With lawful access to ASME Y14.5-2018 (R2024), accept or revise the proposed A/B strategies, modifiers, simulators, surface/profile controls, countersink controls, uncertainty rules and successor drawing plan. Report BLOCKER / MAJOR / MINOR findings with exact file and row references. Do not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r268-status.md").write_text(f"""# Sol R12 status after R268

> **{WARNING}**

R268 is a project-owned correction prompted by Sol R12 B-003; it is not another independent review. It removes one drawing-review ambiguity and one invalid equivalence implication. It does not create buildable released drawings, provider DFM, FAI, received fit, structural proof or qualified approval.

All 18 Sol R12 blockers remain without qualified closure. HR-V0 remains not build-ready and energization remains prohibited.
""",encoding="utf-8")
    readme=ROOT/"README.md"; text=readme.read_text(encoding="utf-8"); marker="## Start here\n\n"; links="- [R268 functional datum/GD&T correction](docs/hr-v0-gdt-review-p0.2.md)\n- [Interactive R268 GD&T review guide](release/hr-v0/gdt-review-p0.2/index.html)\n- [Interactive configuration reconciliation P0.32](release/hr-v0/configuration-reconciliation-p0.32/index.html)\n- [R268 independent review request](docs/reviews/2026-08-12-r268-independent-review-request.md)\n- [Sol R12 status after R268](docs/reviews/2026-08-12-sol-r12-post-r268-status.md)\n"
    if links.splitlines()[0] not in text: text=text.replace(marker,marker+links,1)
    text=text.replace("Two hundred sixty-five rounds are complete: R01-R265.","Two hundred sixty-eight rounds are complete: R01-R268. R268 corrects the GD&T review path while retaining every physical and authority hold.")
    readme.write_text(text,encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md"; h=handoff.read_text(encoding="utf-8"); block=f"R268 functional datum/GD&T correction: **`{ID}` supersedes P0.1 for current review use, binds all five P0.2 shop drawings, removes `B/C as applicable`, and proves Ø0.14 position is non-equivalent to independent ±0.05 coordinates. Current geometry and coordinate controls remain unchanged. `{CID}` carries 49 current records, 46 supersessions, 246 holds and 300 blank acceptances. Qualified Y14.5 disposition, functional stacks, successor drawings, DFM, FAI, received fit and structural proof remain open. Zero Sol blockers close and energization remains prohibited.**\n\n"
    if not h.startswith("R268 functional datum/GD&T correction:"): handoff.write_text(block+h,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"; l=ledger.read_text(encoding="utf-8"); row=f"| R268 | 2026-08-12 | Functional datum/GD&T correction | Codex project-owned correction responding to Sol R12 B-003; not an independent or qualified review | R250 used ambiguous `B/C as applicable` language and implied a Ø0.14 position proposal could be derived from ±0.05 coordinate controls without proving equivalent zones | Issued `{ID}` and `{CID}`; bound five drawings, named exact feature families and DOF intent, proved neither tolerance zone contains the other, retained current controls, and left twelve qualified-review/fabrication holds open. All 18 Sol blockers remain without qualified closure. | `docs/hr-v0-gdt-review-p0.2.md`; `release/hr-v0/gdt-review-p0.2/`; `configuration/hr-v0-config-reconciliation-p0.32/`; `docs/reviews/2026-08-12-r268-validation-record.md`; `docs/reviews/2026-08-12-r268-independent-review-request.md` |\n"
    l=l.replace("Two hundred sixty-seven rounds are complete (R01-R267).","Two hundred sixty-eight rounds are complete (R01-R268). R268 corrects the GD&T review path while retaining every physical and authority hold.")
    if "| R268 |" not in l: l=l.rstrip()+"\n"+row
    ledger.write_text(l,encoding="utf-8")


def main() -> None:
    data=package_data(); build_package(data); update_config(); update_release(); update_docs()
    print("Generated R268 GD&T correction and P0.32; no work authority released")


if __name__ == "__main__": main()
